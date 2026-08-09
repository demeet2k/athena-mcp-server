from __future__ import annotations

import unittest

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime
from athena_mcp.liminal_beacon_mesh_protocol import LIMINAL_BEACON_TOOL_NAMES
from athena_mcp import protocol


class FakeClock:
    def __init__(self, value=1000.0):
        self.value = float(value)

    def __call__(self):
        return self.value

    def advance(self, seconds):
        self.value += float(seconds)


class DummyServer:
    git = None


class LiminalBeaconMeshTests(unittest.TestCase):
    def runtime(self):
        clock = FakeClock()
        return LiminalBeaconMeshRuntime(DummyServer(), clock=clock), clock

    def test_protocol_surface_is_registered(self):
        names = {tool["name"] for tool in protocol.TOOLS}
        self.assertTrue(LIMINAL_BEACON_TOOL_NAMES <= names)

    def test_unknown_sender_encounter_by_object_topology(self):
        mesh, _ = self.runtime()
        mesh.touch("alpha", object_refs=["oid:shared"], focus="build A")
        mesh.touch("beta", object_refs=["oid:shared"], focus="review B")
        emitted = mesh.emit("alpha", "DISCOVERY", "shared object changed", object_refs=["oid:shared"], scout_quota=0 if False else None)
        packet_id = emitted["packet"]["packet_id"]

        view = mesh.rendezvous("beta", scout_quota=0)
        self.assertEqual([packet_id], [row["packet_id"] for row in view["packets"]])
        self.assertEqual("alpha", view["neighbors"][0]["agent_id"])
        self.assertEqual("PACKETS_PRESENTED_NOT_CONSUMED", view["receipt_standing"])

        again = mesh.rendezvous("beta", cursor=view["next_cursor"], scout_quota=0)
        self.assertEqual([], again["packets"])

    def test_active_old_signal_is_encountered_after_receiver_moves_into_neighborhood(self):
        mesh, _ = self.runtime()
        mesh.touch("alpha", object_refs=["oid:shared"])
        mesh.touch("beta", object_refs=["oid:other"])
        packet = mesh.emit("alpha", "DELTA", "still-live delta", object_refs=["oid:shared"])["packet"]

        first = mesh.rendezvous("beta", scout_quota=0)
        self.assertEqual([], first["packets"])
        old_cursor = first["next_cursor"]

        mesh.touch("beta", object_refs=["oid:shared"])
        second = mesh.rendezvous("beta", cursor=old_cursor, scout_quota=0)
        self.assertEqual(packet["packet_id"], second["packets"][0]["packet_id"])
        self.assertLessEqual(packet["event_seq"], old_cursor)

    def test_receipt_ladder_cannot_fake_consumption_or_skip_stages(self):
        mesh, _ = self.runtime()
        mesh.touch("alpha", work_refs=["w:1"])
        mesh.touch("beta", work_refs=["w:1"])
        packet_id = mesh.emit("alpha", "DELTA", "delta", work_refs=["w:1"])["packet"]["packet_id"]
        mesh.rendezvous("beta", scout_quota=0)

        with self.assertRaisesRegex(ValueError, "RECEIPT_STAGE_SKIP_HOLD"):
            mesh.receipt("beta", packet_id, "DECISION_CHANGED")

        consumed = mesh.receipt("beta", packet_id, "CONSUMED", consumer_ref="event:beta:1")
        self.assertEqual("CONSUMED", consumed["receipt"]["stage"])
        mesh.receipt("beta", packet_id, "INCORPORATED", disposition="PARTIAL")
        changed = mesh.receipt("beta", packet_id, "DECISION_CHANGED")
        self.assertEqual("DECISION_CHANGED", changed["receipt"]["stage"])

    def test_correction_reverse_routes_to_prior_consumer_after_topology_changes(self):
        mesh, _ = self.runtime()
        mesh.touch("alpha", object_refs=["oid:old"])
        mesh.touch("beta", object_refs=["oid:old"])
        original = mesh.emit("alpha", "DISCOVERY", "claim v1", object_refs=["oid:old"])["packet"]["packet_id"]
        mesh.rendezvous("beta", scout_quota=0)
        mesh.receipt("beta", original, "CONSUMED", consumer_ref="beta:descendant")

        mesh.touch("beta", object_refs=["oid:new"])
        correction = mesh.emit(
            "alpha",
            "CORRECTION",
            "claim v1 was wrong",
            object_refs=["oid:old"],
            correction_of=original,
            urgency=1.0,
        )["packet"]["packet_id"]
        view = mesh.rendezvous("beta", scout_quota=0)
        self.assertEqual(correction, view["packets"][0]["packet_id"])
        self.assertTrue(view["packets"][0]["reverse_route"])
        self.assertEqual(0, view["packets"][0]["route_overlap"])

    def test_expiry_removes_packet_without_erasing_receipt_law(self):
        mesh, clock = self.runtime()
        mesh.touch("alpha", semantic_tags=["x"])
        packet = mesh.emit("alpha", "DELTA", "short lived", semantic_tags=["x"], ttl_seconds=5)["packet"]
        self.assertEqual(1, mesh.state()["packet_count"])
        clock.advance(6)
        state = mesh.state()
        self.assertEqual(0, state["packet_count"])
        self.assertEqual(1, state["metrics"]["expired_packets"])
        self.assertIn("GIT_HISTORY_DOES_NOT_EVAPORATE_WITH_PHEROMONE_DECAY", state["laws"])
        self.assertTrue(packet["packet_id"].startswith("LBM."))

    def test_packet_identity_is_deterministic_for_same_sender_epoch_sequence_and_content(self):
        left, _ = self.runtime()
        right, _ = self.runtime()
        for mesh in (left, right):
            mesh.touch("alpha", instance_id="i1", session_epoch="e1", work_refs=["w:1"])
        a = left.emit("alpha", "RESULT", "done", work_refs=["w:1"], payload_ref="ref:1")["packet"]["packet_id"]
        b = right.emit("alpha", "RESULT", "done", work_refs=["w:1"], payload_ref="ref:1")["packet"]["packet_id"]
        self.assertEqual(a, b)

    def test_auto_metadata_share_does_not_copy_full_tool_result(self):
        mesh, _ = self.runtime()
        before = mesh.auto_before_tool("athena_example", {"agent_id": "alpha", "oid": "OID-1"})
        self.assertIsNotNone(before)
        after = mesh.auto_after_tool(
            "athena_example",
            {"agent_id": "alpha", "oid": "OID-1"},
            {"status": "OK", "event": "E1", "secret_payload": "DO_NOT_BROADCAST"},
        )
        self.assertIsNotNone(after)
        packet = after["emitted"]
        self.assertIn("status:OK", packet["summary"])
        self.assertNotIn("DO_NOT_BROADCAST", packet["summary"])
        self.assertEqual("RUNTIME_METADATA_ONLY", packet["evidence_ceiling"])


if __name__ == "__main__":
    unittest.main()
