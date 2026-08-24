from __future__ import annotations

import unittest

from athena_mcp.liminal_synapse_return import (
    ARTIFACT,
    BRIDGE_RECEIPT_REF_PREFIX,
    install_liminal_synapse_return,
)


class FakeRuntime:
    def __init__(self):
        self._packets = {
            "LBM.packet": {"message_class": "RESULT"},
            "LBM.need": {"message_class": "NEED"},
            "LBM.other": {"message_class": "RESULT"},
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
        self.assertEqual(
            manifest["synapse_return"]["synapse_projection_return_token_semantics"],
            "DISTINCT_RETURN_ROUTE_RESOURCE",
        )
        self.assertIn(
            "BRIDGE_RECEIPT_TOKEN != SYNAPSE_PROJECTION_RETURN_TOKEN",
            manifest["synapse_return"]["laws"],
        )
        self.assertIn(
            "BRIDGE_RETURN != DELIVERY != CONSUMPTION != INCORPORATION != PROPAGATION != OUTCOME_IMPROVEMENT",
            manifest["synapse_return"]["laws"],
        )

    def test_same_live_packet_destination_bridges_once_and_returns_same_receipt_token(self):
        runtime = self.runtime()
        first = runtime.bridge("LBM.packet", "MESSAGE_BOARD")
        second = runtime.bridge("LBM.packet", "MESSAGE_BOARD")

        self.assertEqual(first["status"], "BRIDGED")
        self.assertEqual(second["status"], "ALREADY_BRIDGED")
        self.assertEqual(len(runtime.bridge_calls), 1)
        self.assertEqual(first["bridge_receipt_token"], second["bridge_receipt_token"])
        self.assertNotIn("return_token", first)
        self.assertNotIn("return_token", second)
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

    def test_propagated_without_explicit_witness_holds_even_after_bridge(self):
        runtime = self.runtime()
        runtime.bridge("LBM.packet", "MESSAGE_BOARD")
        with self.assertRaisesRegex(ValueError, "PROPAGATION_EVIDENCE_HOLD"):
            runtime.receipt("beta", "LBM.packet", "PROPAGATED")
        self.assertEqual(runtime.receipt_calls, [])

    def test_explicit_external_propagation_ref_allows_propagated(self):
        runtime = self.runtime()
        result = runtime.receipt(
            "beta",
            "LBM.packet",
            "PROPAGATED",
            propagation_refs=["event:E-22"],
        )
        self.assertEqual(result["receipt"]["propagation_refs"], ["event:E-22"])
        self.assertEqual(result["propagation_witness_refs"], ["event:E-22"])

    def test_real_bridge_receipt_can_be_explicit_propagation_ref(self):
        runtime = self.runtime()
        bridged = runtime.bridge("LBM.packet", "MESSAGE_BOARD")
        ref = f"{BRIDGE_RECEIPT_REF_PREFIX}{bridged['bridge_receipt_token']}"
        result = runtime.receipt(
            "beta",
            "LBM.packet",
            "PROPAGATED",
            propagation_refs=[ref],
        )
        self.assertEqual(result["receipt"]["propagation_refs"], [ref])

    def test_fabricated_bridge_receipt_ref_holds(self):
        runtime = self.runtime()
        with self.assertRaisesRegex(ValueError, "PROPAGATION_BRIDGE_RECEIPT_HOLD"):
            runtime.receipt(
                "beta",
                "LBM.packet",
                "PROPAGATED",
                propagation_refs=[f"{BRIDGE_RECEIPT_REF_PREFIX}LSR.fabricated"],
            )
        self.assertEqual(runtime.receipt_calls, [])

    def test_bridge_receipt_token_from_other_packet_cannot_witness_this_packet(self):
        runtime = self.runtime()
        other = runtime.bridge("LBM.other", "MESSAGE_BOARD")
        with self.assertRaisesRegex(ValueError, "PROPAGATION_BRIDGE_RECEIPT_HOLD"):
            runtime.receipt(
                "beta",
                "LBM.packet",
                "PROPAGATED",
                propagation_refs=[f"{BRIDGE_RECEIPT_REF_PREFIX}{other['bridge_receipt_token']}"],
            )

    def test_synapse_style_return_route_is_not_mistaken_for_bridge_receipt(self):
        runtime = self.runtime()
        result = runtime.receipt(
            "beta",
            "LBM.packet",
            "PROPAGATED",
            propagation_refs=["athena://liminal/beacon-mesh"],
        )
        self.assertEqual(
            result["propagation_witness_refs"],
            ["athena://liminal/beacon-mesh"],
        )

    def test_state_exposes_addressable_bridge_receipts(self):
        runtime = self.runtime()
        bridge = runtime.bridge("LBM.packet", "MESSAGE_BOARD")
        state = runtime.state()

        self.assertEqual(state["synapse_return"]["bridge_receipt_count"], 1)
        self.assertEqual(
            state["synapse_return"]["bridge_receipts"][0]["bridge_receipt_id"],
            bridge["bridge_receipt_token"],
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
