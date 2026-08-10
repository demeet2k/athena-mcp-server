from __future__ import annotations

import unittest

from athena_mcp.liminal_beacon_mesh import LiminalBeaconMeshRuntime


class Clock:
    def __call__(self):
        return 1000.0


class DummyServer:
    git = None


class LiminalBeaconScopeTests(unittest.TestCase):
    def test_guild_packet_requires_shared_party_route(self):
        mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        # Presence and packet visibility are distinct fibres. Scope Alpha's
        # presence to GUILD too so this fixture tests both packet and presence
        # filtering rather than accidentally asserting that a COLONY-visible
        # presence must disappear because one packet is guild-scoped.
        mesh.touch(
            "alpha",
            object_refs=["oid:shared"],
            party_refs=["guild:A"],
            visibility="GUILD",
        )
        mesh.touch("beta", object_refs=["oid:shared"], party_refs=["guild:B"])
        mesh.touch("gamma", object_refs=["oid:shared"], party_refs=["guild:A"])
        packet_id = mesh.emit(
            "alpha",
            "DELTA",
            "guild scoped delta",
            object_refs=["oid:shared"],
            party_refs=["guild:A"],
            visibility="GUILD",
        )["packet"]["packet_id"]

        denied = mesh.rendezvous("beta", threshold=0.0, scout_quota=0)
        self.assertEqual([], denied["packets"])
        self.assertEqual([packet_id], denied["scope_filtered"])
        self.assertNotIn("alpha", {row["agent_id"] for row in denied["neighbors"]})

        allowed = mesh.rendezvous("gamma", threshold=0.0, scout_quota=0)
        self.assertEqual(packet_id, allowed["packets"][0]["packet_id"])
        self.assertIn("alpha", {row["agent_id"] for row in allowed["neighbors"]})

    def test_colony_presence_remains_visible_when_one_packet_is_guild_scoped(self):
        mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        mesh.touch("alpha", object_refs=["oid:shared"], party_refs=["guild:A"])
        mesh.touch("beta", object_refs=["oid:shared"], party_refs=["guild:B"])
        packet_id = mesh.emit(
            "alpha",
            "DELTA",
            "guild packet from colony-visible sender",
            object_refs=["oid:shared"],
            party_refs=["guild:A"],
            visibility="GUILD",
        )["packet"]["packet_id"]

        view = mesh.rendezvous("beta", threshold=0.0, scout_quota=0)
        self.assertEqual([], view["packets"])
        self.assertEqual([packet_id], view["scope_filtered"])
        self.assertIn("alpha", {row["agent_id"] for row in view["neighbors"]})

    def test_local_packet_requires_explicit_recipient(self):
        mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        mesh.touch("alpha", object_refs=["oid:shared"], visibility="LOCAL")
        mesh.touch("beta", object_refs=["oid:shared"])
        private_id = mesh.emit(
            "alpha",
            "DELTA",
            "local unaddressed",
            object_refs=["oid:shared"],
            visibility="LOCAL",
        )["packet"]["packet_id"]
        denied = mesh.rendezvous("beta", threshold=0.0, scout_quota=0)
        self.assertEqual([], denied["packets"])
        self.assertEqual([private_id], denied["scope_filtered"])

        direct_id = mesh.emit(
            "alpha",
            "DELTA",
            "local addressed",
            recipients=["beta"],
            visibility="LOCAL",
        )["packet"]["packet_id"]
        allowed = mesh.rendezvous("beta", threshold=0.0, scout_quota=0)
        self.assertEqual(direct_id, allowed["packets"][0]["packet_id"])
        self.assertTrue(allowed["packets"][0]["direct_route"])

    def test_scope_is_transport_not_authority(self):
        mesh = LiminalBeaconMeshRuntime(DummyServer(), clock=Clock())
        mesh.touch("alpha")
        view = mesh.rendezvous("alpha", scout_quota=0)
        self.assertIn("VISIBILITY != AUTHORITY", view["scope_law"])


if __name__ == "__main__":
    unittest.main()
