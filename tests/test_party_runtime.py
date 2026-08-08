import os
import tempfile
import unittest

from athena_mcp.party_protocol import PARTY_TOOL_NAMES
from athena_mcp.party_runtime import OUTPUT_HEADS, PartyRuntime, communication_metrics, party_bonus_rate
from athena_mcp.party_server import PartyServer
from athena_mcp.server import Server


class PartyPureTests(unittest.TestCase):
    def test_communication_requires_real_cross_agent_coordination(self):
        members = ["alpha", "beta"]
        one_way = [{"author": "alpha", "target": "beta", "kind": "OFFER"}]
        self.assertFalse(communication_metrics(members, one_way)["proper"])
        braided = one_way + [{"author": "beta", "target": "alpha", "kind": "HANDOFF"}]
        out = communication_metrics(members, braided)
        self.assertTrue(out["proper"])
        self.assertGreater(out["quality"], 0.8)

    def test_presence_never_unlocks_bonus(self):
        out = party_bonus_rate(
            ["alpha", "beta"],
            2,
            [],
            [
                {"outcome_ref": "o1", "agent": "alpha", "goal_id": "g1", "witness_ref": "w1", "status": "OBSERVED"},
                {"outcome_ref": "o2", "agent": "beta", "goal_id": "g2", "witness_ref": "w2", "status": "VERIFIED"},
            ],
        )
        self.assertFalse(out["active"])
        self.assertEqual(out["bonus_rate"], 0.0)
        self.assertEqual(out["xp_multiplier"], 1.0)


class PartyRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "athena.db")
        self.server = Server(self.db)
        self.party = PartyRuntime(self.server)

    def tearDown(self):
        self.server.store.db.close()
        self.tmp.cleanup()

    def _formed_party(self):
        formed = self.party.form(
            "alpha",
            [
                {"id": "goal-a", "required_capabilities": ["research"]},
                {"id": "goal-b", "required_capabilities": ["build"]},
            ],
            ["party-main"],
            capabilities=["research", "verify"],
            name="Big 3 test party",
        )
        self.assertEqual(formed["rules"]["presence_xp"], 0)
        joined = self.party.join(formed["party_id"], "beta", capabilities=["build", "verify"])
        self.assertEqual(joined["presence_xp"], 0)
        return formed["party_id"]

    def _braid(self, party_id):
        self.party.message(
            party_id,
            "alpha",
            "party-main",
            "beta",
            "OFFER",
            "I will take goal-a and publish evidence.",
        )
        self.party.message(
            party_id,
            "beta",
            "party-main",
            "alpha",
            "HANDOFF",
            "I will take goal-b; send goal-a evidence here for joint verification.",
        )

    def test_big3_3x5x7x9_and_capped_credit(self):
        party_id = self._formed_party()
        self._braid(party_id)
        plan = self.party.steer(party_id, actor="alpha")
        self.assertEqual(plan["candidate_count"], 15)
        self.assertEqual(
            plan["suite"]["shape"],
            {"families": 3, "variants_per_family": 5, "stages": 7, "output_heads": 9},
        )
        self.assertEqual(tuple(plan["heads"]), OUTPUT_HEADS)
        self.assertEqual(plan["heads"]["xp_multiplier"]["value"], 1.0)
        self.assertEqual(plan["pareto"]["model_count"], 16)

        credited = self.party.credit(
            party_id,
            plan["cycle_id"],
            [
                {"outcome_ref": "outcome-a", "agent": "alpha", "goal_id": "goal-a", "witness_ref": "witness-a", "status": "VERIFIED"},
                {"outcome_ref": "outcome-b", "agent": "beta", "goal_id": "goal-b", "witness_ref": "witness-b", "status": "VERIFIED"},
            ],
            [
                {"agent": "alpha", "source_xp_ref": "quest-xp-alpha", "base_xp": 100, "witness_ref": "quest-xp-witness-alpha"},
                {"agent": "beta", "source_xp_ref": "quest-xp-beta", "base_xp": 100, "witness_ref": "quest-xp-witness-beta"},
            ],
            actor="verifier",
        )
        self.assertEqual(credited["status"], "BONUS_CREDITED")
        self.assertGreater(credited["credit"]["bonus_rate"], 0.0)
        self.assertLessEqual(credited["credit"]["bonus_rate"], 0.05)
        self.assertEqual(len(credited["awards"]), 2)
        self.assertTrue(all(0 < row["bonus_xp"] <= 5 for row in credited["awards"]))

        with self.assertRaises(ValueError):
            self.party.credit(
                party_id,
                plan["cycle_id"],
                [
                    {"outcome_ref": "outcome-a2", "agent": "alpha", "goal_id": "goal-a", "witness_ref": "witness-a2", "status": "VERIFIED"},
                    {"outcome_ref": "outcome-b2", "agent": "beta", "goal_id": "goal-b", "witness_ref": "witness-b2", "status": "VERIFIED"},
                ],
                [{"agent": "alpha", "source_xp_ref": "quest-xp-alpha", "base_xp": 100, "witness_ref": "quest-xp-witness-alpha"}],
            )

    def test_bonus_locks_without_communication(self):
        party_id = self._formed_party()
        plan = self.party.steer(party_id)
        locked = self.party.credit(
            party_id,
            plan["cycle_id"],
            [
                {"outcome_ref": "outcome-a", "agent": "alpha", "goal_id": "goal-a", "witness_ref": "witness-a", "status": "VERIFIED"},
                {"outcome_ref": "outcome-b", "agent": "beta", "goal_id": "goal-b", "witness_ref": "witness-b", "status": "VERIFIED"},
            ],
            [{"agent": "alpha", "source_xp_ref": "quest-a", "base_xp": 100, "witness_ref": "quest-wa"}],
        )
        self.assertEqual(locked["status"], "BONUS_LOCKED")
        self.assertEqual(locked["credit"]["bonus_rate"], 0.0)
        self.assertEqual(locked["awards"], [])


class PartyServerSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "athena.db")
        self.server = PartyServer(self.db)

    def tearDown(self):
        self.server.store.db.close()
        self.tmp.cleanup()

    def test_default_surface_lists_party_tools(self):
        response = self.server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertTrue(PARTY_TOOL_NAMES <= names)

    def test_mcp_form_and_join(self):
        formed = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "athena_party_form",
                    "arguments": {"leader": "alpha", "goals": ["g1", "g2"], "channels": ["party-main"]},
                },
            }
        )
        self.assertFalse(formed["result"]["isError"])
        party_id = formed["result"]["structuredContent"]["party_id"]
        joined = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "athena_party_join", "arguments": {"party_id": party_id, "agent": "beta"}},
            }
        )
        self.assertFalse(joined["result"]["isError"])
        self.assertEqual(len(joined["result"]["structuredContent"]["members"]), 2)


if __name__ == "__main__":
    unittest.main()
