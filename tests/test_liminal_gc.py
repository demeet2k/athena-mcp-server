from __future__ import annotations

import unittest

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime


class FakeClock:
    def __init__(self, value=1000.0):
        self.value = float(value)

    def __call__(self):
        return self.value

    def advance(self, seconds):
        self.value += float(seconds)


class DummyServer:
    git = None


class LiminalGarbageCollectionTests(unittest.TestCase):
    def runtime(self):
        clock = FakeClock()
        return LiminalBeaconMeshRuntime(DummyServer(), clock=clock), clock

    def test_expired_packet_receipt_detail_compacts_but_reverse_consumer_survives(self):
        mesh, clock = self.runtime()
        mesh.touch("alpha", object_refs=["oid:old"], lease_seconds=60)
        mesh.touch("beta", object_refs=["oid:old"], lease_seconds=60)
        original = mesh.emit(
            "alpha", "DISCOVERY", "claim v1", object_refs=["oid:old"], ttl_seconds=5
        )["packet"]["packet_id"]
        mesh.rendezvous("beta", scout_quota=0)
        mesh.receipt("beta", original, "CONSUMED", consumer_ref="beta:descendant")

        mesh.touch("beta", object_refs=["oid:new"], lease_seconds=60)
        self.assertIn(("beta", original), mesh._receipts)
        self.assertIn("beta", mesh._reverse_consumers[original])

        clock.advance(6)
        state = mesh.state()
        self.assertEqual(state["packet_count"], 0)
        self.assertEqual(state["receipt_count"], 0)
        self.assertNotIn(("beta", original), mesh._receipts)
        self.assertIn("beta", mesh._reverse_consumers[original])
        self.assertGreaterEqual(state["garbage_collection"]["receipt_details_compacted"], 1)

        correction = mesh.emit(
            "alpha",
            "CORRECTION",
            "claim v1 was wrong",
            object_refs=["oid:old"],
            correction_of=original,
            ttl_seconds=30,
            urgency=1.0,
        )["packet"]["packet_id"]
        view = mesh.rendezvous("beta", scout_quota=0)
        self.assertEqual(view["packets"][0]["packet_id"], correction)
        self.assertTrue(view["packets"][0]["reverse_route"])
        self.assertEqual(view["packets"][0]["route_overlap"], 0)

    def test_expired_bridge_receipt_is_compacted_with_packet(self):
        mesh, clock = self.runtime()
        mesh.touch("alpha", semantic_tags=["x"], lease_seconds=60)
        packet_id = mesh.emit(
            "alpha", "RESULT", "done", semantic_tags=["x"], ttl_seconds=5
        )["packet"]["packet_id"]
        mesh._synapse_return_ledger_v1 = {
            (packet_id, "MESSAGE_BOARD", "origin", "", False): {
                "packet_id": packet_id,
                "bridge_receipt_id": "LSR.test",
                "status": "BRIDGED",
            }
        }
        clock.advance(6)
        state = mesh.state()
        self.assertEqual(mesh._synapse_return_ledger_v1, {})
        self.assertGreaterEqual(state["garbage_collection"]["bridge_receipts_compacted"], 1)

    def test_inactive_sender_epoch_sequence_compacts_only_after_live_packet_is_gone(self):
        mesh, clock = self.runtime()
        presence = mesh.touch("alpha", instance_id="proc-1", lease_seconds=5)["presence"]
        epoch_key = ("alpha", presence["session_epoch"])
        mesh.emit("alpha", "RESULT", "short", semantic_tags=["x"], ttl_seconds=5)
        self.assertIn(epoch_key, mesh._sender_seq)

        clock.advance(6)
        mesh.state()
        self.assertNotIn(epoch_key, mesh._sender_seq)

    def test_live_packet_state_is_not_collected(self):
        mesh, clock = self.runtime()
        mesh.touch("alpha", semantic_tags=["x"], lease_seconds=60)
        mesh.touch("beta", semantic_tags=["x"], lease_seconds=60)
        packet_id = mesh.emit(
            "alpha", "RESULT", "still live", semantic_tags=["x"], ttl_seconds=30
        )["packet"]["packet_id"]
        mesh.rendezvous("beta", scout_quota=0)
        mesh.receipt("beta", packet_id, "CONSUMED")
        clock.advance(6)
        state = mesh.state()
        self.assertEqual(state["packet_count"], 1)
        self.assertIn(("beta", packet_id), mesh._receipts)

    def test_manifest_declares_preservation_boundary(self):
        mesh, _ = self.runtime()
        gc = mesh.manifest()["garbage_collection"]
        self.assertIn("reverse_consumer_index", gc["preserves"])
        self.assertIn("durable_git_history", gc["preserves"])
        self.assertIn("PROCESS_LOCAL_GC != DURABLE_HISTORY_DELETION", gc["laws"])


if __name__ == "__main__":
    unittest.main()
