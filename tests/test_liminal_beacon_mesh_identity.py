from __future__ import annotations

import unittest

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime


class Clock:
    def __call__(self):
        return 1000.0


class DummyServer:
    git = None


class LiminalBeaconIdentityTests(unittest.TestCase):
    def test_implicit_epoch_rotates_across_runtime_restart(self):
        left = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        right = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())

        lp = left.touch("alpha")["presence"]
        rp = right.touch("alpha")["presence"]
        self.assertEqual("UNWITNESSED", lp["instance_id"])
        self.assertEqual("UNWITNESSED", rp["instance_id"])
        self.assertNotEqual(lp["session_epoch"], rp["session_epoch"])

        left_id = left.emit("alpha", "RESULT", "same result")["packet"]["packet_id"]
        right_id = right.emit("alpha", "RESULT", "same result")["packet"]["packet_id"]
        self.assertNotEqual(left_id, right_id)
        self.assertEqual("UNKNOWN", left.state()["independent_process_count"])

    def test_exposed_instance_rebind_rotates_implicit_epoch(self):
        mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        first = mesh.touch("alpha", instance_id="worker-A")["presence"]
        second = mesh.touch("alpha", instance_id="worker-B")["presence"]
        self.assertNotEqual(first["session_epoch"], second["session_epoch"])
        self.assertEqual(1, second["heartbeat_seq"])

    def test_explicit_epoch_remains_deterministic_for_replay_fixture(self):
        left = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        right = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        for mesh in (left, right):
            mesh.touch("alpha", instance_id="i1", session_epoch="fixture-e1", work_refs=["w:1"])
        self.assertEqual(
            left.emit("alpha", "RESULT", "done", work_refs=["w:1"])["packet"]["packet_id"],
            right.emit("alpha", "RESULT", "done", work_refs=["w:1"])["packet"]["packet_id"],
        )


if __name__ == "__main__":
    unittest.main()
