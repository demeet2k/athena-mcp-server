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


class LiminalIdentityExpiryTests(unittest.TestCase):
    def runtime(self):
        clock = FakeClock()
        return LiminalBeaconMeshRuntime(DummyServer(), clock=clock), clock

    def test_active_same_instance_keeps_epoch_and_advances_heartbeat(self):
        mesh, _ = self.runtime()
        first = mesh.touch("alpha", instance_id="proc-1", lease_seconds=5)["presence"]
        second = mesh.touch("alpha", instance_id="proc-1", lease_seconds=5)["presence"]

        self.assertEqual(first["session_epoch"], second["session_epoch"])
        self.assertEqual(second["heartbeat_seq"], 2)
        self.assertEqual(second["instance_id"], "proc-1")

    def test_lease_gap_rotates_epoch_even_when_agent_and_instance_names_repeat(self):
        mesh, clock = self.runtime()
        first = mesh.touch("alpha", instance_id="proc-1", lease_seconds=5)["presence"]
        clock.advance(6)
        second_result = mesh.touch("alpha", instance_id="proc-1", lease_seconds=5)
        second = second_result["presence"]

        self.assertNotEqual(first["session_epoch"], second["session_epoch"])
        self.assertEqual(second["heartbeat_seq"], 1)
        self.assertEqual(second["instance_id"], "proc-1")
        self.assertEqual(
            second_result["epoch_law"],
            "RESTART_REBIND_OR_LEASE_GAP_REQUIRES_NEW_SENDER_EPOCH_NAMESPACE",
        )

    def test_expired_explicit_instance_is_not_inherited_when_next_instance_is_unwitnessed(self):
        mesh, clock = self.runtime()
        first = mesh.touch("alpha", instance_id="proc-1", lease_seconds=5)["presence"]
        clock.advance(6)
        second_result = mesh.touch("alpha", lease_seconds=5)
        second = second_result["presence"]

        self.assertNotEqual(first["session_epoch"], second["session_epoch"])
        self.assertEqual(second["instance_id"], "UNWITNESSED")
        self.assertEqual(second_result["identity_standing"], "PROCESS_INSTANCE_UNKNOWN")

    def test_active_explicit_rebind_rotates_epoch_without_waiting_for_expiry(self):
        mesh, _ = self.runtime()
        first = mesh.touch("alpha", instance_id="proc-1", lease_seconds=30)["presence"]
        second = mesh.touch("alpha", instance_id="proc-2", lease_seconds=30)["presence"]

        self.assertNotEqual(first["session_epoch"], second["session_epoch"])
        self.assertEqual(second["heartbeat_seq"], 1)
        self.assertEqual(second["instance_id"], "proc-2")


if __name__ == "__main__":
    unittest.main()
