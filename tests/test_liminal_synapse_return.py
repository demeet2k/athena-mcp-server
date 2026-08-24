from __future__ import annotations

import unittest

from athena_mcp.liminal_synapse_return import ARTIFACT, install_liminal_synapse_return


class FakeRuntime:
    def __init__(self):
        self._packets = {
            "LBM.packet": {"message_class": "RESULT"},
            "LBM.need": {"message_class": "NEED"},
        }
        self.bridge_calls = []
        self.receipt_calls = []
        self.clock = 1000.0

    def _now(self):
        return self.clock

    def manifest(self):
        return {"status": "OK"}

    def bridge(self, packet_id, bridge_kind="AUTO", remote="origin", allow_collaboration=False, role=None):
        self.bridge_calls.append((packet_id, bridge_kind, remote, allow_collaboration, role))
        return {
            "status": "BRIDGED",
            "bridge_kind": bridge_kind,
            "packet_id": packet_id,
            "bridge_result": {
                "status": "POSTED" if bridge_kind == "MESSAGE_BOARD" else "MATCHED",
                "message_event": {"event_id": "MBE-1"} if bridge_kind == "MESSAGE_BOARD" else None,
                "request_id": "REQ-1" if bridge_kind == "COHESION" else None,
                "git": {"head": "abc123"},
            },
        }

    def receipt(
        self,
        agent_id,
        packet_id,
        stage,
        *,
        disposition=None,
        consumer_ref=None,
        residual=None,
        propagation_refs=None,
        outcome_ref=None,
    ):
        row = {
            "agent_id": agent_id,
            "packet_id": packet_id,
            "stage": stage,
            "propagation_refs": list(propagation_refs or []),
        }
        self.receipt_calls.append(row)
        return {"status": "RECEIPT_ADVANCED", "receipt": row}

    def state(self, agent_id=None, include_packets=False, limit=50):
        return {"status": "OK", "packet_count": len(self._packets)}


class LiminalSynapseReturnTests(unittest.TestCase):
    def runtime(self):
        class Runtime(FakeRuntime):
            pass

        install_liminal_synapse_return(Runtime)
        return Runtime()

    def test_manifest_exposes_additive_non_authoritative_return_contract(self):
        runtime = self.runtime()
        manifest = runtime.manifest()
        self.assertEqual(manifest["synapse_return"]["artifact"], ARTIFACT)
        self.assertFalse(manifest["synapse_return"]["cross_restart_deduplication"])
        self.assertIn(
            "BRIDGE_RETURN != DELIVERY != CONSUMPTION != INCORPORATION != OUTCOME_IMPROVEMENT",
            manifest["synapse_return"]["laws"],
        )

    def test_same_live_packet_destination_bridges_once_and_returns_same_token(self):
        runtime = self.runtime()
        first = runtime.bridge("LBM.packet", "MESSAGE_BOARD")
        second = runtime.bridge("LBM.packet", "MESSAGE_BOARD")

        self.assertEqual(first["status"], "BRIDGED")
        self.assertEqual(second["status"], "ALREADY_BRIDGED")
        self.assertEqual(len(runtime.bridge_calls), 1)
        self.assertEqual(first["return_token"], second["bridge_receipt"]["bridge_receipt_id"])
        self.assertIn("message-board:MBE-1", first["durable_refs"])
        self.assertIn("git:abc123", first["durable_refs"])

    def test_auto_kind_is_resolved_before_idempotency_keying(self):
        runtime = self.runtime()
        first = runtime.bridge("LBM.need", "AUTO")
        second = runtime.bridge("LBM.need", "COHESION")

        self.assertEqual(first["bridge_kind"], "COHESION")
        self.assertEqual(second["status"], "ALREADY_BRIDGED")
        self.assertEqual(len(runtime.bridge_calls), 1)
        self.assertIn("cohesion:REQ-1", first["durable_refs"])

    def test_distinct_destinations_are_not_collapsed(self):
        runtime = self.runtime()
        runtime.bridge("LBM.packet", "MESSAGE_BOARD", remote="origin")
        runtime.bridge("LBM.packet", "MESSAGE_BOARD", remote="backup")
        self.assertEqual(len(runtime.bridge_calls), 2)

    def test_propagated_without_any_witness_holds(self):
        runtime = self.runtime()
        with self.assertRaisesRegex(ValueError, "PROPAGATION_EVIDENCE_HOLD"):
            runtime.receipt("beta", "LBM.packet", "PROPAGATED")
        self.assertEqual(runtime.receipt_calls, [])

    def test_explicit_propagation_ref_allows_propagated(self):
        runtime = self.runtime()
        result = runtime.receipt(
            "beta",
            "LBM.packet",
            "PROPAGATED",
            propagation_refs=["event:E-22"],
        )
        self.assertEqual(result["receipt"]["propagation_refs"], ["event:E-22"])
        self.assertEqual(result["synapse_return_refs"], ["event:E-22"])

    def test_successful_bridge_return_can_supply_propagation_witness(self):
        runtime = self.runtime()
        bridged = runtime.bridge("LBM.packet", "MESSAGE_BOARD")
        result = runtime.receipt("beta", "LBM.packet", "PROPAGATED")

        refs = result["receipt"]["propagation_refs"]
        self.assertEqual(refs, [f"synapse-return:{bridged['return_token']}"])

    def test_state_exposes_addressable_bridge_receipts(self):
        runtime = self.runtime()
        bridge = runtime.bridge("LBM.packet", "MESSAGE_BOARD")
        state = runtime.state()

        self.assertEqual(state["synapse_return"]["bridge_receipt_count"], 1)
        self.assertEqual(
            state["synapse_return"]["bridge_receipts"][0]["bridge_receipt_id"],
            bridge["return_token"],
        )
        self.assertFalse(state["synapse_return"]["cross_restart_deduplication"])

    def test_install_is_idempotent(self):
        class Runtime(FakeRuntime):
            pass

        install_liminal_synapse_return(Runtime)
        wrapped_bridge = Runtime.bridge
        install_liminal_synapse_return(Runtime)
        self.assertIs(Runtime.bridge, wrapped_bridge)


if __name__ == "__main__":
    unittest.main()
