from __future__ import annotations

import unittest

from athena_mcp import protocol
from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime
from athena_mcp.liminal_synapse_return import install_liminal_synapse_return
from athena_mcp.server import Server
from athena_mcp.synapse_liminal_adapter import (
    LIMINAL_RESOURCE,
    PACKET_PROFILE,
    RECEIPT_PROFILE,
    SYNAPSE_SCHEMA,
    liminal_capsule_to_synapse,
)
from athena_mcp.synapse_liminal_extension import SynapseLiminalRuntime
from athena_mcp.synapse_liminal_protocol import SYNAPSE_LIMINAL_TOOL_NAMES
from athena_mcp.synapse_observer import TOOL_NAME as SYNAPSE_OBSERVER_TOOL
from athena_mcp.synapse_observer_extension import _synapse_abi_status


class _BridgeFake:
    def __init__(self):
        self._packets = {"LBM.packet": {"message_class": "RESULT"}}

    def _now(self):
        return 1000.0

    def manifest(self):
        return {"status": "OK"}

    def bridge(self, packet_id, bridge_kind="AUTO", remote="origin", allow_collaboration=False, role=None):
        return {
            "status": "BRIDGED",
            "bridge_kind": "MESSAGE_BOARD" if bridge_kind == "AUTO" else bridge_kind,
            "packet_id": packet_id,
            "bridge_result": {
                "status": "POSTED",
                "message_event": {"event_id": "MBE-composition"},
                "git": {"head": "abc123"},
            },
        }

    def receipt(self, agent_id, packet_id, stage, **kwargs):
        return {"status": "RECEIPT_ADVANCED", "receipt": {"stage": stage}}

    def state(self, agent_id=None, include_packets=False, limit=50):
        return {"status": "OK"}


class _ServerStub:
    git = None


class SynapseComposition379380Tests(unittest.TestCase):
    def test_install_surface_contains_both_sibling_organs(self):
        names = {tool["name"] for tool in protocol.TOOLS}
        self.assertTrue(SYNAPSE_LIMINAL_TOOL_NAMES <= names)
        self.assertIn(SYNAPSE_OBSERVER_TOOL, names)
        self.assertTrue(getattr(LiminalBeaconMeshRuntime, "_athena_liminal_synapse_return_v1_registered", False))
        self.assertTrue(getattr(LiminalBeaconMeshRuntime, "_athena_liminal_gc_v1_registered", False))
        self.assertTrue(getattr(Server, "_athena_synapse_liminal_v1_registered", False))
        self.assertTrue(getattr(Server, "_athena_synapse_observer_v1_registered", False))
        self.assertTrue(getattr(Server, "_athena_synapse_observer_resource_v1_registered", False))

    def test_observer_detects_real_companion_abi_without_mock(self):
        status = _synapse_abi_status()
        self.assertTrue(status["adapter_installed"])
        self.assertTrue(status["schema_match"])
        self.assertEqual(status["observed_schema"], SYNAPSE_SCHEMA)
        self.assertEqual(status["packet_profile"], PACKET_PROFILE)
        self.assertEqual(status["receipt_profile"], RECEIPT_PROFILE)
        self.assertEqual(status["standing"], "COMPANION_SCHEMA_MATCH")

    def test_bridge_receipt_token_and_synapse_return_route_are_distinct_types(self):
        class Runtime(_BridgeFake):
            pass

        install_liminal_synapse_return(Runtime)
        local = Runtime().bridge("LBM.packet", "MESSAGE_BOARD")
        bridge_token = local["bridge_receipt_token"]

        capsule = {
            "packet_id": "LBM.packet",
            "event_seq": 1,
            "sender_id": "alpha",
            "instance_id": "i1",
            "session_epoch": "e1",
            "sender_seq": 1,
            "lamport": 1,
            "message_class": "RESULT",
            "summary": "done",
            "payload_ref": None,
            "goal_ref": None,
            "evidence_ceiling": "RUNTIME_METADATA_ONLY",
            "urgency": 0.5,
            "novelty": 0.5,
            "created_at": 1000.0,
            "expires_at": 1900.0,
            "visibility": "COLONY",
            "recipients": [],
            "changed_refs": [],
            "affected_refs": [],
            "correction_of": None,
            "retraction_of": None,
            "reply_to": None,
            "parent_ids": [],
            "semantic_digest": "digest",
        }
        envelope = liminal_capsule_to_synapse(
            capsule,
            source_revision="composition-head",
            bridge_observed_at="2026-08-24T15:30:00Z",
        )
        route_token = envelope["projection"]["return_token"]

        self.assertTrue(bridge_token.startswith("LSR."))
        self.assertEqual(route_token, LIMINAL_RESOURCE)
        self.assertNotEqual(bridge_token, route_token)
        self.assertEqual(envelope["routing"]["return_routes"], [LIMINAL_RESOURCE])

    def test_real_liminal_export_ingest_and_receipt_export_compose(self):
        server = _ServerStub()
        runtime = LiminalBeaconMeshRuntime(server)
        server._liminal_beacon_mesh_runtime_v1 = runtime
        runtime.touch("alpha", object_refs=["oid:shared"], focus="source")
        runtime.touch("beta", object_refs=["oid:shared"], focus="sink")

        native = runtime.emit(
            "alpha",
            "RESULT",
            "composition result",
            object_refs=["oid:shared"],
            evidence_ceiling="RUNTIME_METADATA_ONLY",
        )["packet"]
        packet_id = native["packet_id"]
        synapse = SynapseLiminalRuntime(server)

        exported = synapse.call_tool(
            "athena_synapse_liminal_export_packet",
            {"packet_id": packet_id, "source_revision": "composition-head"},
        )
        envelope = exported["envelope"]
        self.assertEqual(exported["status"], "SYNAPSE_PACKET_EXPORTED")
        self.assertEqual(envelope["schema"], SYNAPSE_SCHEMA)
        self.assertEqual(envelope["origin"]["native_event_id"], packet_id)
        self.assertEqual(envelope["projection"]["return_token"], LIMINAL_RESOURCE)

        ingested = synapse.call_tool(
            "athena_synapse_liminal_ingest",
            {"agent_id": "beta", "envelope": envelope},
        )
        self.assertEqual(ingested["status"], "SYNAPSE_INGESTED_TO_LIMINAL")
        self.assertNotEqual(ingested["emitted"]["packet"]["packet_id"], packet_id)
        self.assertIn("INGEST != SOURCE_EVENT_IDENTITY", ingested["laws"])

        presented = runtime.rendezvous("beta", scout_quota=0)
        self.assertIn(packet_id, [row["packet_id"] for row in presented["packets"]])
        runtime.receipt("beta", packet_id, "CONSUMED", consumer_ref="beta:composition")

        receipt_export = synapse.call_tool(
            "athena_synapse_liminal_export_receipt",
            {
                "agent_id": "beta",
                "packet_id": packet_id,
                "source_revision": "composition-head",
            },
        )
        receipt_envelope = receipt_export["envelope"]
        self.assertEqual(receipt_export["status"], "SYNAPSE_RECEIPT_EXPORTED")
        self.assertEqual(receipt_envelope["event_type"], "RECEIPT")
        self.assertEqual(receipt_envelope["receipt"]["stage"], "CONSUMED")
        self.assertEqual(receipt_envelope["payload"]["body"]["consumer_ref"], "beta:composition")


if __name__ == "__main__":
    unittest.main()
