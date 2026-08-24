from __future__ import annotations

import copy
import json
from pathlib import Path
import threading
import unittest

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime
from athena_mcp.synapse_ingress_correlation import (
    attach_ingress_correlation,
    ingress_source_preflight,
    record_ingress_correlation,
)
from athena_mcp.synapse_liminal_adapter import _digest
from athena_mcp.synapse_liminal_extension import SynapseLiminalRuntime

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "athena_core_synapse_packet_envelope_v1.json"


class FakeClock:
    def __init__(self, value=1000.0):
        self.value = float(value)

    def __call__(self):
        return self.value


class DummyServer:
    git = None


class SynapseIngressPreflightTests(unittest.TestCase):
    def vector(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))["envelope"]

    def runtime(self):
        server = DummyServer()
        mesh = LiminalBeaconMeshRuntime(server, clock=FakeClock())
        server._liminal_beacon_mesh_runtime_v1 = mesh
        mesh.touch("bridge-agent", work_refs=["OID-144"])
        return server, mesh, SynapseLiminalRuntime(server)

    def ingest(self, runtime, envelope):
        return runtime.call_tool(
            "athena_synapse_liminal_ingest",
            {"agent_id": "bridge-agent", "envelope": copy.deepcopy(envelope)},
        )

    def test_exact_source_replay_reuses_packet_before_monotone_sender_sequence_advances(self):
        server, mesh, runtime = self.runtime()
        source = self.vector()
        first = self.ingest(runtime, source)
        before_count = mesh.state()["packet_count"]
        second = self.ingest(runtime, source)
        self.assertEqual(before_count, mesh.state()["packet_count"])
        self.assertEqual(first["emitted"]["packet"]["packet_id"], second["emitted"]["packet"]["packet_id"])
        self.assertEqual("ALREADY_EMITTED", second["emitted"]["status"])
        self.assertTrue(second["emitted"]["idempotent"])
        self.assertEqual("EXACT_SOURCE_CORRELATION", second["preflight"]["status"])
        self.assertEqual("EXACT_CORRELATION_REPLAY", second["source_correlation"]["status"])
        self.assertEqual("EXISTING_EPHEMERAL_COORDINATION_SIGNAL_REUSED_PROCESS_LOCAL", second["standing"])

    def test_concurrent_exact_ingress_serializes_preflight_emit_record_to_one_packet(self):
        server, mesh, runtime = self.runtime()
        source = self.vector()
        original_emit = mesh.emit
        first_emit_entered = threading.Event()
        release_first_emit = threading.Event()
        delay_guard = threading.Lock()
        delay_used = {"value": False}

        def delayed_emit(**kwargs):
            with delay_guard:
                should_delay = not delay_used["value"]
                if should_delay:
                    delay_used["value"] = True
            if should_delay:
                first_emit_entered.set()
                self.assertTrue(release_first_emit.wait(timeout=2.0))
            return original_emit(**kwargs)

        mesh.emit = delayed_emit
        results = []
        failures = []

        def run_ingest():
            try:
                results.append(self.ingest(runtime, source))
            except BaseException as exc:  # preserve worker assertion/timeout details
                failures.append(exc)

        first = threading.Thread(target=run_ingest, daemon=True)
        second = threading.Thread(target=run_ingest, daemon=True)
        first.start()
        self.assertTrue(first_emit_entered.wait(timeout=2.0))
        second.start()

        # The second call must block on the mesh transaction lock before it can
        # preflight or emit. No packet exists until the deliberately delayed
        # first native emit is released.
        second.join(timeout=0.05)
        self.assertTrue(second.is_alive())
        self.assertEqual(0, mesh.state()["packet_count"])

        release_first_emit.set()
        first.join(timeout=2.0)
        second.join(timeout=2.0)
        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual([], failures)
        self.assertEqual(2, len(results))
        self.assertEqual(1, mesh.state()["packet_count"])

        packet_ids = {row["emitted"]["packet"]["packet_id"] for row in results}
        self.assertEqual(1, len(packet_ids))
        statuses = sorted(row["emitted"]["status"] for row in results)
        self.assertEqual(["ALREADY_EMITTED", "EMITTED"], statuses)
        preflights = sorted(row["preflight"]["status"] for row in results)
        self.assertEqual(["EXACT_SOURCE_CORRELATION", "UNOBSERVED_SOURCE_OCCURRENCE"], preflights)
        self.assertEqual(1, sum(row["source_correlation"]["status"] == "EXACT_CORRELATION_REPLAY" for row in results))
        self.assertEqual(1, sum(row["source_correlation"]["status"] == "CORRELATED_PROCESS_LOCAL" for row in results))

    def test_same_source_event_changed_body_holds_before_local_emit(self):
        server, mesh, runtime = self.runtime()
        source = self.vector()
        first = self.ingest(runtime, source)
        packet_id = first["emitted"]["packet"]["packet_id"]
        before_count = mesh.state()["packet_count"]

        changed = copy.deepcopy(source)
        changed["clock"]["bridge_observed_at"] = "2099-01-01T00:00:00Z"
        self.assertEqual(source["event_id"], changed["event_id"])
        self.assertNotEqual(_digest(source), _digest(changed))
        preflight = ingress_source_preflight(server, changed, agent_id="bridge-agent")
        self.assertEqual("SOURCE_EVENT_BODY_COLLISION_HOLD", preflight["status"])
        self.assertEqual([packet_id], [row["local_packet_id"] for row in preflight["conflicts"]])

        with self.assertRaisesRegex(ValueError, "SOURCE_EVENT_BODY_COLLISION_HOLD"):
            self.ingest(runtime, changed)
        self.assertEqual(before_count, mesh.state()["packet_count"])

    def test_historical_ambiguous_packet_correlation_is_fail_closed_without_selected_source(self):
        server, mesh, runtime = self.runtime()
        source = self.vector()
        first = self.ingest(runtime, source)
        emitted = first["emitted"]
        packet_id = emitted["packet"]["packet_id"]

        changed = copy.deepcopy(source)
        changed["clock"]["bridge_observed_at"] = "2099-01-01T00:00:00Z"
        observation = record_ingress_correlation(
            server,
            changed,
            emitted,
            agent_id="bridge-agent",
            observed_at="2099-01-01T00:00:01Z",
        )
        self.assertEqual("AMBIGUOUS_CORRELATION_HOLD", observation["status"])
        self.assertEqual(2, observation["correlation_count"])
        self.assertIsNone(observation["correlation_id"])
        self.assertIsNone(observation["source_event_id"])
        self.assertIsNone(observation["record_digest"])

        attached = attach_ingress_correlation(
            server,
            packet_id=packet_id,
            source_revision="test-revision",
            export_result={"status": "TEST", "envelope": source},
        )
        self.assertEqual("AMBIGUOUS_CORRELATION_HOLD", attached["source_correlation"]["status"])
        self.assertIsNone(attached["correlation_envelope"])
        self.assertEqual(source, attached["envelope"])


if __name__ == "__main__":
    unittest.main()
