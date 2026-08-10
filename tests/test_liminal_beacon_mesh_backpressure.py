from __future__ import annotations

import unittest

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class DummyServer:
    git = None


class LiminalBeaconBackpressureTests(unittest.TestCase):
    def test_topological_match_does_not_bypass_attention_threshold(self):
        mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        mesh.touch("alpha", object_refs=["oid:shared"])
        mesh.touch("beta", object_refs=["oid:shared"])
        packet_id = mesh.emit(
            "alpha",
            "DELTA",
            "low-salience topology delta",
            object_refs=["oid:shared"],
            urgency=0.0,
            novelty=0.0,
        )["packet"]["packet_id"]

        blocked = mesh.rendezvous("beta", threshold=0.95, scout_quota=0)
        self.assertEqual([], blocked["packets"])
        self.assertEqual([packet_id], blocked["backpressure_filtered"])
        self.assertIn("TOPOLOGICAL_MATCH != ATTENTION_BYPASS", blocked["attention_law"])

        # A filtered capsule must not retain a fake PRESENTED receipt. Lowering
        # the receiver threshold should make the same still-live packet eligible.
        admitted = mesh.rendezvous("beta", threshold=0.0, scout_quota=0)
        self.assertEqual(packet_id, admitted["packets"][0]["packet_id"])
        self.assertEqual("PACKETS_PRESENTED_NOT_CONSUMED", admitted["receipt_standing"])

    def test_explicit_recipient_is_priority_not_spam_bypass(self):
        mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        mesh.touch("alpha", object_refs=["oid:a"])
        mesh.touch("beta", object_refs=["oid:b"])
        packet_id = mesh.emit(
            "alpha",
            "DELTA",
            "direct but low-salience",
            recipients=["beta"],
            urgency=0.0,
            novelty=0.0,
        )["packet"]["packet_id"]

        blocked = mesh.rendezvous("beta", threshold=0.95, scout_quota=0)
        self.assertEqual([], blocked["packets"])
        self.assertEqual([packet_id], blocked["backpressure_filtered"])
        self.assertIn("DIRECT_RECIPIENT != ATTENTION_BYPASS", blocked["attention_law"])

        admitted = mesh.rendezvous("beta", threshold=0.0, scout_quota=0)
        self.assertEqual(packet_id, admitted["packets"][0]["packet_id"])
        self.assertTrue(admitted["packets"][0]["direct_route"])
        self.assertFalse(admitted["packets"][0]["reverse_route"])

    def test_neighbor_presence_metadata_is_inside_context_budget(self):
        mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        for index in range(8):
            mesh.touch(
                f"agent-{index}",
                object_refs=["oid:shared"],
                focus="x" * 512,
                capabilities=[f"cap-{n}" for n in range(20)],
                needs=[f"need-{n}" for n in range(20)],
                offers=[f"offer-{n}" for n in range(20)],
            )
        mesh.touch("receiver", object_refs=["oid:shared"])

        view = mesh.rendezvous("receiver", context_budget=256, scout_quota=0)
        self.assertLessEqual(view["context_used"], 256)
        self.assertEqual(
            view["context_used"],
            view["packet_context_used"] + view["neighbor_context_used"],
        )
        self.assertIn("PRESENCE_METADATA_COUNTS_AGAINST_CONTEXT_BUDGET", view["attention_law"])


if __name__ == "__main__":
    unittest.main()
