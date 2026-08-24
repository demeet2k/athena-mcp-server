from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime
from athena_mcp.synapse_ingress_correlation import (
    AUTHORITY_CLASS,
    CORRELATION_PROFILE,
    TRUTH_CEILING,
    attach_ingress_correlation,
    ingress_correlation_snapshot,
    record_ingress_correlation,
)
from athena_mcp.synapse_liminal_adapter import (
    LIMINAL_RESOURCE,
    PACKET_PROFILE,
    RECEIPT_PROFILE,
    _bridge_id,
    _digest,
    _packet_bridge_id,
    _validate_envelope,
)
from athena_mcp.synapse_liminal_extension import SynapseLiminalRuntime

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "athena_core_synapse_packet_envelope_v1.json"
REV = "d4d169707f54b133905471b36811a02bb212e92a"


class FakeClock:
    def __init__(self, value=1000.0):
        self.value = float(value)

    def __call__(self):
        return self.value


class DummyServer:
    git = None


class SynapseIngressCorrelationTests(unittest.TestCase):
    def vector(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def runtime(self):
        server = DummyServer()
        mesh = LiminalBeaconMeshRuntime(server, clock=FakeClock())
        server._liminal_beacon_mesh_runtime_v1 = mesh
        return server, mesh, SynapseLiminalRuntime(server)

    def ingest(self, server, mesh, runtime, envelope=None, agent_id="bridge-agent"):
        mesh.touch(agent_id, work_refs=["OID-144"])
        result = runtime.call_tool(
            "athena_synapse_liminal_ingest",
            {"agent_id": agent_id, "envelope": copy.deepcopy(envelope or self.vector()["envelope"])},
        )
        return result

    def test_ingest_records_unique_process_local_source_mapping(self):
        server, mesh, runtime = self.runtime()
        result = self.ingest(server, mesh, runtime)
        correlation = result["source_correlation"]
        packet_id = result["emitted"]["packet"]["packet_id"]
        self.assertEqual("CORRELATED_PROCESS_LOCAL", correlation["status"])
        self.assertEqual(self.vector()["envelope"]["event_id"], correlation["source_event_id"])
        self.assertEqual(packet_id, correlation["packet_id"])
        self.assertEqual(1, correlation["correlation_count"])
        self.assertFalse(correlation["durable"])
        snapshot = ingress_correlation_snapshot(server, packet_id)
        self.assertEqual(correlation["correlation_id"], snapshot["correlation_id"])

    def test_exact_reingest_is_idempotent_and_reuses_first_observation(self):
        server, mesh, runtime = self.runtime()
        first = self.ingest(server, mesh, runtime)
        second = self.ingest(server, mesh, runtime)
        self.assertEqual(first["emitted"]["packet"]["packet_id"], second["emitted"]["packet"]["packet_id"])
        self.assertEqual("EXACT_CORRELATION_REPLAY", second["source_correlation"]["status"])
        self.assertEqual(first["source_correlation"]["correlation_id"], second["source_correlation"]["correlation_id"])
        self.assertEqual(first["source_correlation"]["record_digest"], second["source_correlation"]["record_digest"])
        self.assertEqual(1, second["source_correlation"]["correlation_count"])

    def test_packet_export_attaches_sibling_correlation_without_mutating_canonical_profile(self):
        server, mesh, runtime = self.runtime()
        ingested = self.ingest(server, mesh, runtime)
        packet_id = ingested["emitted"]["packet"]["packet_id"]
        exported = runtime.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet_id, "source_revision": REV},
        )
        native = exported["envelope"]
        sibling = exported["correlation_envelope"]
        self.assertEqual(PACKET_PROFILE, native["projection"]["profile"])
        self.assertEqual(CORRELATION_PROFILE, sibling["projection"]["profile"])
        self.assertNotEqual(native["event_id"], sibling["event_id"])
        self.assertEqual(AUTHORITY_CLASS, sibling["semantics"]["authority_class"])
        self.assertEqual(TRUTH_CEILING, sibling["semantics"]["truth_ceiling"])
        _validate_envelope(native)
        _validate_envelope(sibling)

    def test_correlation_envelope_closes_source_to_local_packet_causal_edge(self):
        server, mesh, runtime = self.runtime()
        source = self.vector()["envelope"]
        ingested = self.ingest(server, mesh, runtime, source)
        packet_id = ingested["emitted"]["packet"]["packet_id"]
        exported = runtime.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet_id, "source_revision": REV},
        )
        sibling = exported["correlation_envelope"]
        self.assertIn(source["event_id"], sibling["causality"]["parent_ids"])
        self.assertIn(_packet_bridge_id(packet_id, REV), sibling["causality"]["parent_ids"])
        self.assertEqual(source["event_id"], sibling["causality"]["reply_to"])
        self.assertEqual(source["subject"], sibling["subject"])

    def test_original_core_return_routes_propagate_only_on_sibling_not_native_export(self):
        server, mesh, runtime = self.runtime()
        source = self.vector()["envelope"]
        ingested = self.ingest(server, mesh, runtime, source)
        packet_id = ingested["emitted"]["packet"]["packet_id"]
        exported = runtime.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet_id, "source_revision": REV},
        )
        native_routes = exported["envelope"]["routing"]["return_routes"]
        sibling_routes = exported["correlation_envelope"]["routing"]["return_routes"]
        self.assertEqual([LIMINAL_RESOURCE], native_routes)
        for route in source["routing"]["return_routes"]:
            self.assertNotIn(route, native_routes)
            self.assertIn(route, sibling_routes)
        self.assertIn(LIMINAL_RESOURCE, sibling_routes)

    def test_sibling_replay_is_exact_even_when_native_export_observation_time_moves(self):
        server, mesh, runtime = self.runtime()
        ingested = self.ingest(server, mesh, runtime)
        packet_id = ingested["emitted"]["packet"]["packet_id"]
        first = runtime.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet_id, "source_revision": REV},
        )
        second = runtime.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet_id, "source_revision": REV},
        )
        self.assertEqual(first["correlation_envelope"]["event_id"], second["correlation_envelope"]["event_id"])
        self.assertEqual(_digest(first["correlation_envelope"]), _digest(second["correlation_envelope"]))
        self.assertEqual(
            first["correlation_envelope"]["clock"]["bridge_observed_at"],
            second["correlation_envelope"]["clock"]["bridge_observed_at"],
        )

    def test_restart_without_ledger_reports_unobserved_instead_of_reconstructing_from_packet_hash(self):
        server = DummyServer()
        snapshot = ingress_correlation_snapshot(server, "LBM.fake")
        self.assertEqual("UNOBSERVED_PROCESS_LOCAL_CORRELATION", snapshot["status"])
        self.assertEqual(0, snapshot["correlation_count"])
        self.assertIsNone(snapshot["source_event_id"])
        self.assertFalse(snapshot["durable"])

    def test_same_bridge_id_changed_source_body_is_ambiguity_hold_not_overwrite(self):
        server, mesh, runtime = self.runtime()
        source = self.vector()["envelope"]
        first = self.ingest(server, mesh, runtime, source)
        packet = first["emitted"]
        packet_id = packet["packet"]["packet_id"]

        reobserved = copy.deepcopy(source)
        reobserved["clock"]["bridge_observed_at"] = "2099-01-01T00:00:00Z"
        self.assertEqual(source["event_id"], reobserved["event_id"])
        self.assertNotEqual(_digest(source), _digest(reobserved))
        second = record_ingress_correlation(
            server,
            reobserved,
            packet,
            agent_id="bridge-agent",
            observed_at="2099-01-01T00:00:01Z",
        )
        self.assertEqual("AMBIGUOUS_CORRELATION_HOLD", second["status"])
        self.assertEqual(2, second["correlation_count"])
        attached = attach_ingress_correlation(
            server,
            packet_id=packet_id,
            source_revision=REV,
            export_result={"envelope": source, "status": "TEST"},
        )
        self.assertEqual("AMBIGUOUS_CORRELATION_HOLD", attached["source_correlation"]["status"])
        self.assertIsNone(attached["correlation_envelope"])
        self.assertEqual(source, attached["envelope"])

    def test_source_revision_rebinds_correlation_event_not_record_identity(self):
        server, mesh, runtime = self.runtime()
        ingested = self.ingest(server, mesh, runtime)
        packet_id = ingested["emitted"]["packet"]["packet_id"]
        a = runtime.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet_id, "source_revision": REV},
        )["correlation_envelope"]
        b = runtime.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet_id, "source_revision": "other-revision"},
        )["correlation_envelope"]
        self.assertNotEqual(a["event_id"], b["event_id"])
        self.assertEqual(a["payload"]["body"], b["payload"]["body"])
        self.assertEqual(a["frontier"]["native_digest"], b["frontier"]["native_digest"])

    def test_receipt_export_keeps_native_receipt_envelope_and_adds_same_correlation_sibling(self):
        server, mesh, runtime = self.runtime()
        source = self.vector()["envelope"]
        ingested = self.ingest(server, mesh, runtime, source)
        packet_id = ingested["emitted"]["packet"]["packet_id"]

        mesh.touch("observer", work_refs=["OID-144"])
        rendezvous = mesh.rendezvous("observer", scout_quota=1)
        self.assertIn(packet_id, [row["packet_id"] for row in rendezvous["packets"]])
        before = dict(mesh._receipts[("observer", packet_id)])
        exported = runtime.call_tool(
            "athena_synapse_liminal_export_receipt",
            {"agent_id": "observer", "packet_id": packet_id, "source_revision": REV},
        )
        after = dict(mesh._receipts[("observer", packet_id)])
        self.assertEqual(before, after)
        self.assertEqual(RECEIPT_PROFILE, exported["envelope"]["projection"]["profile"])
        self.assertEqual("PRESENTED", exported["envelope"]["receipt"]["stage"])
        self.assertEqual(CORRELATION_PROFILE, exported["correlation_envelope"]["projection"]["profile"])
        self.assertIn(source["event_id"], exported["correlation_envelope"]["causality"]["parent_ids"])
        self.assertNotIn(source["event_id"], exported["envelope"]["causality"]["parent_ids"])

    def test_attaching_correlation_never_changes_canonical_envelope_digest(self):
        server, mesh, runtime = self.runtime()
        source = self.vector()["envelope"]
        ingested = self.ingest(server, mesh, runtime, source)
        packet_id = ingested["emitted"]["packet"]["packet_id"]
        native = copy.deepcopy(source)
        before = _digest(native)
        attached = attach_ingress_correlation(
            server,
            packet_id=packet_id,
            source_revision=REV,
            export_result={"status": "TEST", "envelope": native},
        )
        self.assertEqual(before, _digest(attached["envelope"]))
        self.assertEqual(source, attached["envelope"])
        self.assertNotEqual(attached["envelope"]["event_id"], attached["correlation_envelope"]["event_id"])

    def test_correlation_event_id_uses_shared_bridge_identity_law(self):
        server, mesh, runtime = self.runtime()
        ingested = self.ingest(server, mesh, runtime)
        packet_id = ingested["emitted"]["packet"]["packet_id"]
        envelope = runtime.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet_id, "source_revision": REV},
        )["correlation_envelope"]
        self.assertEqual(
            _bridge_id(envelope["origin"], CORRELATION_PROFILE),
            envelope["event_id"],
        )


if __name__ == "__main__":
    unittest.main()
