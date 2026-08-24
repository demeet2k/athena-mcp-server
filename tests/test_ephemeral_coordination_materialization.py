from __future__ import annotations

import tempfile
import unittest

from athena_mcp.ephemeral_coordination import EphemeralCoordinationRuntime
from athena_mcp.store import Store


class EphemeralCoordinationMaterializationTests(unittest.TestCase):
    def _runtime(self, **kwargs):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        store = Store(f"{td.name}/athena.db")
        self.addCleanup(store.close)
        now = [1000.0]
        runtime = EphemeralCoordinationRuntime(store, clock=lambda: now[0], **kwargs)
        return runtime, now

    def _present(self, runtime, aid="a"):
        runtime.present({
            "aid": aid,
            "epoch": "e1",
            "ttl_ms": 10000,
            "capabilities": ["coordination"],
            "need_offer_summary": {},
            "lamport": 1,
            "causal_parents": [],
            "source_digest": f"source:{aid}",
        })

    def _post_args(self, *, ref="sha256:logical", payload=None, include_payload=True):
        args = {
            "sender_aid": "a",
            "recipient_selector": {"aids": ["b"]},
            "delivery_class": "NUDGE",
            "salience": 0.5,
            "ttl_ms": 10000,
            "packet_digest_or_ref": ref,
            "lamport": 2,
            "causal_parents": [],
        }
        if include_payload:
            args["inline_payload"] = payload
        return args

    def test_inline_payload_survives_post_poll_with_digest_binding(self):
        runtime, _ = self._runtime()
        self._present(runtime)
        payload = {"z": [1, True, None, {"a": "µ"}], "a": {"k": "v"}}
        posted = runtime.post(self._post_args(payload=payload))
        self.assertTrue(posted["payload_materialized"])
        self.assertTrue(posted["inline_payload_digest"].startswith("sha256:"))
        item = runtime.poll({"aid": "b"})["packets"][0]
        self.assertEqual(item["inline_payload"], payload)
        self.assertEqual(item["inline_payload_digest"], posted["inline_payload_digest"])
        self.assertTrue(item["payload_materialized"])

    def test_inline_payload_digest_is_canonical_across_key_order(self):
        runtime, now = self._runtime()
        self._present(runtime)
        first = runtime.post(self._post_args(ref="same", payload={"b": 2, "a": 1}))
        now[0] += 11
        self._present(runtime)
        second = runtime.post(self._post_args(ref="same", payload={"a": 1, "b": 2}))
        self.assertEqual(first["inline_payload_digest"], second["inline_payload_digest"])

    def test_same_active_reference_with_different_payload_fails_closed(self):
        runtime, _ = self._runtime()
        self._present(runtime)
        runtime.post(self._post_args(ref="same", payload={"a": 1}))
        with self.assertRaisesRegex(ValueError, "ACTIVE_REFERENCE_PAYLOAD_CONTRADICTION"):
            runtime.post(self._post_args(ref="same", payload={"a": 2}))

    def test_same_active_reference_with_same_payload_still_coalesces(self):
        runtime, _ = self._runtime()
        self._present(runtime)
        first = runtime.post(self._post_args(ref="same", payload={"a": 1}))
        second = runtime.post(self._post_args(ref="same", payload={"a": 1}))
        self.assertTrue(second["coalesced"])
        self.assertEqual(first["packet_id"], second["packet_id"])

    def test_reference_only_legacy_post_remains_supported(self):
        runtime, _ = self._runtime()
        self._present(runtime)
        posted = runtime.post(self._post_args(ref="legacy", include_payload=False))
        self.assertFalse(posted["payload_materialized"])
        item = runtime.poll({"aid": "b"})["packets"][0]
        self.assertIsNone(item["inline_payload"])
        self.assertIsNone(item["inline_payload_digest"])
        self.assertFalse(item["payload_materialized"])

    def test_inline_payload_size_bound_fails_closed(self):
        runtime, _ = self._runtime(max_inline_payload_bytes=32)
        self._present(runtime)
        with self.assertRaisesRegex(ValueError, "INLINE_PAYLOAD_TOO_LARGE"):
            runtime.post(self._post_args(payload={"x": "y" * 100}))

    def test_nonfinite_inline_payload_fails_closed(self):
        runtime, _ = self._runtime()
        self._present(runtime)
        with self.assertRaisesRegex(ValueError, "non-finite JSON number"):
            runtime.post(self._post_args(payload={"x": float("nan")}))

    def test_nonstring_inline_payload_key_fails_closed(self):
        runtime, _ = self._runtime()
        self._present(runtime)
        with self.assertRaisesRegex(ValueError, "JSON object keys must be strings"):
            runtime.post(self._post_args(payload={1: "x"}))

    def test_existing_v0_packet_table_is_migrated_in_place(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(f"{td}/athena.db")
            self.addCleanup(store.close)
            store.db.execute("DROP TABLE IF EXISTS ephemeral_packets")
            store.db.execute(
                "CREATE TABLE ephemeral_packets("
                "packet_id TEXT PRIMARY KEY,sender_aid TEXT NOT NULL,delivery_class TEXT NOT NULL,"
                "salience REAL NOT NULL,ttl_ms INTEGER NOT NULL,packet_digest_or_ref TEXT NOT NULL,"
                "lamport INTEGER NOT NULL,causal_parents_json TEXT NOT NULL,coalesce_key TEXT NOT NULL,"
                "created_at REAL NOT NULL,expires_at REAL NOT NULL)"
            )
            store.db.commit()
            runtime = EphemeralCoordinationRuntime(store, clock=lambda: 1000.0)
            columns = {row["name"] for row in store.db.execute("PRAGMA table_info(ephemeral_packets)")}
            self.assertTrue({"inline_payload_json", "inline_payload_digest"}.issubset(columns))
            self._present(runtime)
            self.assertTrue(runtime.post(self._post_args(payload={"migrated": True}))["payload_materialized"])

    def test_benchmark_exposes_materialized_packet_count(self):
        runtime, _ = self._runtime()
        self._present(runtime)
        runtime.post(self._post_args(ref="one", payload={"x": 1}))
        runtime.post(self._post_args(ref="two", payload={"y": 2}))
        self.assertEqual(runtime.benchmark()["ephemeral_materialized_packets_live"], 2)


if __name__ == "__main__":
    unittest.main()
