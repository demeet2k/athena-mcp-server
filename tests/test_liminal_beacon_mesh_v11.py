from __future__ import annotations

import json
import unittest

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime


class FakeClock:
    def __init__(self, value=5000.0):
        self.value = float(value)

    def __call__(self):
        return self.value


class DummyServer:
    git = None


class LiminalBeaconMeshV11Tests(unittest.TestCase):
    def runtime(self):
        return LiminalBeaconMeshRuntime(DummyServer(), clock=FakeClock())

    def test_typed_semantic_correction_reverse_routes_after_topology_divergence(self):
        mesh = self.runtime()
        mesh.touch("alpha", object_refs=["oid:old"])
        mesh.touch("beta", object_refs=["oid:old"])
        original = mesh.emit(
            "alpha", "DISCOVERY", "D1", object_refs=["oid:old"]
        )["packet"]["packet_id"]
        mesh.rendezvous("beta", scout_quota=0)
        mesh.receipt("beta", original, "CONSUMED", consumer_ref="beta:D1")
        mesh.touch("beta", object_refs=["oid:new"])

        after = mesh.auto_after_tool(
            "athena_fix",
            {"agent_id": "alpha", "oid": "old"},
            {
                "status": "STALE",
                "event": "C1",
                "secret_payload": "NEVER_BROADCAST_THIS",
                "_liminal_publish": {
                    "message_class": "CORRECTION",
                    "summary": "D1 requires correction",
                    "payload_ref": "event:C1",
                    "changed_refs": ["event:C1"],
                    "correction_of": original,
                },
            },
        )
        packet = after["emitted"]
        self.assertEqual("CORRECTION", packet["message_class"])
        self.assertEqual(original, packet["correction_of"])
        self.assertEqual("RUNTIME_METADATA_ONLY", packet["evidence_ceiling"])
        self.assertNotIn("NEVER_BROADCAST_THIS", str(packet))

        view = mesh.rendezvous("beta", scout_quota=0)
        correction = next(row for row in view["packets"] if row["packet_id"] == packet["packet_id"])
        self.assertTrue(correction["reverse_route"])
        self.assertEqual(0, correction["route_overlap"])

    def test_plain_result_fields_never_infer_correction_lineage(self):
        mesh = self.runtime()
        mesh.touch("alpha", object_refs=["oid:old"])
        original = mesh.emit("alpha", "DISCOVERY", "D1", object_refs=["oid:old"])["packet"]["packet_id"]
        result = mesh.auto_after_tool(
            "athena_fix",
            {"agent_id": "alpha", "oid": "old"},
            {"status": "STALE", "correction_of": original, "event": "C1"},
        )
        packet = result["emitted"]
        self.assertEqual("BLOCKER", packet["message_class"])
        self.assertFalse(packet.get("correction_of"))
        self.assertIn("AUTO_METADATA_BEACON", result["law"])

    def test_malformed_envelope_fails_share_closed_without_generic_downgrade(self):
        mesh = self.runtime()
        mesh.touch("alpha", object_refs=["oid:old"])
        before = mesh.state()["packet_count"]
        result = mesh.auto_after_tool(
            "athena_fix",
            {"agent_id": "alpha", "oid": "old"},
            {
                "status": "OK",
                "_liminal_publish": {
                    "message_class": "RESULT",
                    "summary": "done",
                    "unexpected": "must reject",
                },
            },
        )
        self.assertIsNone(result["emitted"])
        self.assertIn("SEMANTIC_ENVELOPE_HOLD", result["semantic_error"])
        self.assertEqual(before, mesh.state()["packet_count"])

    def test_caller_cannot_escalate_semantic_evidence_ceiling(self):
        mesh = self.runtime()
        mesh.touch("alpha")
        result = mesh.auto_after_tool(
            "athena_fix",
            {"agent_id": "alpha"},
            {
                "status": "OK",
                "_liminal_publish": {
                    "message_class": "RESULT",
                    "summary": "done",
                    "evidence_ceiling": "VERIFIED_TRUTH",
                },
            },
        )
        self.assertIsNone(result["emitted"])
        self.assertIn("unknown semantic envelope keys", result["semantic_error"])

    def test_valid_semantic_result_has_fixed_metadata_evidence_ceiling(self):
        mesh = self.runtime()
        mesh.touch("alpha")
        result = mesh.auto_after_tool(
            "athena_fix",
            {"agent_id": "alpha"},
            {
                "status": "OK",
                "_liminal_publish": {
                    "message_class": "RESULT",
                    "summary": "bounded result",
                },
            },
        )
        self.assertEqual("RUNTIME_METADATA_ONLY", result["emitted"]["evidence_ceiling"])

    def test_critical_reserve_admits_one_overloaded_blocker(self):
        mesh = self.runtime()
        mesh.touch("alpha", object_refs=["oid:shared"])
        mesh.touch("beta", object_refs=["oid:shared"])
        blocker = mesh.emit(
            "alpha",
            "BLOCKER",
            "critical but low route score",
            object_refs=["oid:shared"],
            urgency=0.0,
            novelty=0.0,
        )["packet"]["packet_id"]
        view = mesh.rendezvous(
            "beta", threshold=0.95, scout_quota=0, critical_quota=1
        )
        self.assertEqual([blocker], [row["packet_id"] for row in view["packets"]])
        self.assertTrue(view["packets"][0]["critical_reserve"])
        self.assertEqual([blocker], view["critical_reserve_packet_ids"])
        self.assertEqual(1, view["critical_reserve_used"])
        self.assertEqual(1, view["critical_quota"])

    def test_critical_label_flood_cannot_exceed_reserve_quota(self):
        mesh = self.runtime()
        mesh.touch("alpha", object_refs=["oid:shared"])
        mesh.touch("beta", object_refs=["oid:shared"])
        packet_ids = []
        for index in range(3):
            packet_ids.append(
                mesh.emit(
                    "alpha",
                    "BLOCKER",
                    f"blocker {index}",
                    object_refs=["oid:shared"],
                    urgency=0.0,
                    novelty=0.0,
                )["packet"]["packet_id"]
            )
        view = mesh.rendezvous(
            "beta", threshold=0.95, scout_quota=0, critical_quota=1, limit=8
        )
        reserved = [row for row in view["packets"] if row.get("critical_reserve")]
        self.assertEqual(1, len(reserved))
        self.assertLessEqual(len(view["packets"]), 1)
        self.assertEqual(2, len(view["backpressure_filtered"]))
        self.assertTrue(set(view["backpressure_filtered"]) <= set(packet_ids))

    def test_ordinary_and_direct_packets_remain_backpressured(self):
        mesh = self.runtime()
        mesh.touch("alpha", object_refs=["oid:shared"])
        mesh.touch("beta", object_refs=["oid:shared"])
        ordinary = mesh.emit(
            "alpha",
            "RESULT",
            "ordinary",
            object_refs=["oid:shared"],
            urgency=0.0,
            novelty=0.0,
        )["packet"]["packet_id"]
        direct = mesh.emit(
            "alpha",
            "RESULT",
            "direct ordinary",
            object_refs=["oid:shared"],
            recipients=["beta"],
            urgency=0.0,
            novelty=0.0,
        )["packet"]["packet_id"]
        view = mesh.rendezvous(
            "beta", threshold=0.95, scout_quota=0, critical_quota=1, limit=8
        )
        self.assertEqual([], view["packets"])
        self.assertEqual({ordinary, direct}, set(view["backpressure_filtered"]))

    def test_critical_reserve_cannot_break_hard_context_budget(self):
        mesh = self.runtime()
        mesh.touch("alpha", object_refs=["oid:shared"])
        mesh.touch("beta", object_refs=["oid:shared"])
        blocker = mesh.emit(
            "alpha",
            "BLOCKER",
            "X" * 1200,
            object_refs=["oid:shared"],
            urgency=0.0,
            novelty=0.0,
        )["packet"]["packet_id"]
        view = mesh.rendezvous(
            "beta",
            threshold=0.95,
            scout_quota=0,
            critical_quota=1,
            context_budget=256,
        )
        self.assertLessEqual(view["context_used"], view["context_budget"])
        self.assertLessEqual(view["packet_context_used"], view["context_budget"])
        rendered_packet_bytes = sum(
            len(json.dumps(row, ensure_ascii=False, sort_keys=True))
            for row in view["packets"]
        )
        self.assertEqual(rendered_packet_bytes, view["packet_context_used"])
        if blocker not in [row["packet_id"] for row in view["packets"]]:
            self.assertIn(blocker, view["context_budget_filtered"])
        self.assertIn("CONTEXT_BUDGET != SOFT_TARGET", view["attention_law"])


if __name__ == "__main__":
    unittest.main()
