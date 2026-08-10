from __future__ import annotations

import tempfile
import unittest

from athena_mcp.ephemeral_coordination import EphemeralCoordinationRuntime
from athena_mcp.store import Store


class EphemeralCoordinationTests(unittest.TestCase):
    def _runtime(self, **kwargs):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        store = Store(f"{td.name}/athena.db")
        self.addCleanup(store.close)
        now = [1000.0]
        runtime = EphemeralCoordinationRuntime(store, clock=lambda: now[0], **kwargs)
        return runtime, now

    def _present(self, runtime, aid, epoch="e1", ttl_ms=10000, summary=None):
        return runtime.present({
            "aid": aid,
            "epoch": epoch,
            "ttl_ms": ttl_ms,
            "capabilities": ["coordination"],
            "need_offer_summary": summary or {},
            "lamport": 1,
            "causal_parents": [],
            "source_digest": f"source:{aid}:{epoch}",
        })

    def _post(self, runtime, sender="a", recipient="b", ref="sha256:x", **overrides):
        args = {
            "sender_aid": sender,
            "recipient_selector": {"aids": [recipient]},
            "delivery_class": "NUDGE",
            "salience": 0.5,
            "ttl_ms": 10000,
            "packet_digest_or_ref": ref,
            "lamport": 2,
            "causal_parents": [],
        }
        args.update(overrides)
        return runtime.post(args)

    def test_presence_is_advisory_not_liveness_or_authority(self):
        runtime, _ = self._runtime()
        result = self._present(runtime, "a", summary={"need": ["review"]})
        self.assertEqual(result["authority"], "NONE")
        self.assertIn("PRESENCE!=HOST_LIVENESS_PROOF", result["laws"])
        snapshot = runtime.snapshot({"scope": "global", "freshness_bound_ms": 60000})
        self.assertFalse(snapshot["shared_deployment_proven"])
        self.assertFalse(snapshot["product_exposure_proven"])
        self.assertEqual(snapshot["need_offer_index"][0]["aid"], "a")

    def test_post_is_targeted_deduped_and_poll_is_cursor_bounded(self):
        runtime, _ = self._runtime()
        self._present(runtime, "a")
        first = self._post(runtime)
        duplicate = self._post(runtime)
        self.assertEqual(first["route_state"], "ROUTED")
        self.assertTrue(duplicate["coalesced"])
        self.assertEqual(duplicate["packet_id"], first["packet_id"])
        poll = runtime.poll({"aid": "b", "after_cursor": 0, "max_items": 10, "salience_budget": 1.0})
        self.assertEqual([row["packet_id"] for row in poll["packets"]], [first["packet_id"]])
        self.assertGreater(poll["next_cursor"], 0)
        empty = runtime.poll({"aid": "b", "after_cursor": poll["next_cursor"], "max_items": 10, "salience_budget": 1.0})
        self.assertEqual(empty["packets"], [])
        self.assertEqual(poll["authority"], "NONE")

    def test_material_candidate_requires_explicit_durable_escalation(self):
        runtime, _ = self._runtime()
        self._present(runtime, "a")
        result = self._post(runtime, delivery_class="MATERIAL_CANDIDATE")
        self.assertTrue(result["durable_escalation_required"])
        self.assertFalse(result["durable_escalation_contract"]["performed"])
        self.assertEqual(result["durable_escalation_contract"]["target"], "ROOM_OR_GIT_MESSAGE_BOARD")

    def test_receipt_ladder_is_monotonic_and_later_stages_need_witness(self):
        runtime, _ = self._runtime()
        self._present(runtime, "a")
        packet = self._post(runtime)["packet_id"]
        with self.assertRaisesRegex(ValueError, "RECEIPT_STAGE_GAP"):
            runtime.receipt({"packet_id": packet, "aid": "b", "stage": "PRESENTED"})
        delivered = runtime.receipt({"packet_id": packet, "aid": "b", "stage": "DELIVERED"})
        self.assertEqual(delivered["receipt_standing"], "CALLER_ATTESTED_RUNTIME_RECEIPT")
        runtime.receipt({"packet_id": packet, "aid": "b", "stage": "PRESENTED"})
        with self.assertRaisesRegex(ValueError, "requires a non-empty typed witness"):
            runtime.receipt({"packet_id": packet, "aid": "b", "stage": "CONSUMED"})
        consumed = runtime.receipt({"packet_id": packet, "aid": "b", "stage": "CONSUMED", "witness": {"consumer_ref": "agent:b"}})
        self.assertEqual(consumed["authority"], "NONE")
        same = runtime.receipt({"packet_id": packet, "aid": "b", "stage": "CONSUMED", "witness": {"consumer_ref": "ignored-on-idempotent-read"}})
        self.assertTrue(same["idempotent"])

    def test_ttl_gc_removes_presence_and_packets(self):
        runtime, now = self._runtime()
        self._present(runtime, "a", ttl_ms=500)
        self._post(runtime, ttl_ms=500)
        now[0] += 0.6
        snapshot = runtime.snapshot({"scope": "global", "freshness_bound_ms": 60000})
        self.assertEqual(snapshot["fresh_presence"], [])
        poll = runtime.poll({"aid": "b", "after_cursor": 0, "max_items": 10, "salience_budget": 2.0})
        self.assertEqual(poll["packets"], [])
        self.assertGreaterEqual(poll["dropped_or_coalesced_counts"]["expired_dropped"], 0)

    def test_queue_and_salience_backpressure_fail_closed(self):
        runtime, _ = self._runtime(per_aid_queue_limit=1, sender_active_salience_limit=0.75)
        self._present(runtime, "a")
        self._post(runtime, ref="x", salience=0.5)
        with self.assertRaisesRegex(ValueError, "SENDER_SALIENCE_BACKPRESSURE|RECIPIENT_QUEUE_BACKPRESSURE"):
            self._post(runtime, ref="y", salience=0.5)

    def test_broadcast_selector_is_rejected(self):
        runtime, _ = self._runtime()
        self._present(runtime, "a")
        with self.assertRaisesRegex(ValueError, "supports only explicit aids"):
            runtime.post({
                "sender_aid": "a",
                "recipient_selector": {"broadcast": True},
                "delivery_class": "NUDGE",
                "salience": 0.2,
                "ttl_ms": 1000,
                "packet_digest_or_ref": "x",
                "lamport": 2,
                "causal_parents": [],
            })


if __name__ == "__main__":
    unittest.main()
