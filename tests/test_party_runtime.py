import os
import tempfile
import unittest

from athena_mcp.party_protocol import PARTY_RESOURCE, PARTY_TOOL_NAMES
from athena_mcp.party_runtime import OUTPUT_HEADS, communication_metrics, party_bonus_rate
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


class PartyNativeSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "athena.db")
        self.server = Server(self.db)
        self.surface = self.server.aor_development.party
        self.party = self.surface.runtime

    def tearDown(self):
        self.server.store.db.close()
        self.tmp.cleanup()

    def _formed_party(self, suffix=""):
        formed = self.party.form(
            "alpha",
            [
                {"id": f"goal-a{suffix}", "required_capabilities": ["research"]},
                {"id": f"goal-b{suffix}", "required_capabilities": ["build"]},
            ],
            [f"party-main{suffix}"],
            capabilities=["research", "verify"],
            name=f"Big 3 test party{suffix}",
        )
        self.assertEqual(formed["rules"]["presence_xp"], 0)
        joined = self.party.join(formed["party_id"], "beta", capabilities=["build", "verify"])
        self.assertEqual(joined["presence_xp"], 0)
        return formed["party_id"], f"party-main{suffix}", f"goal-a{suffix}", f"goal-b{suffix}"

    def _planning_braid(self, party_id, channel):
        self.party.message(
            party_id,
            "alpha",
            channel,
            "beta",
            "OFFER",
            "I will take the research goal and publish evidence.",
        )
        self.party.message(
            party_id,
            "beta",
            channel,
            "alpha",
            "HANDOFF",
            "I will take the build goal; send evidence here for joint verification.",
        )

    def _cycle_braid(self, party_id, channel, cycle_id):
        self.party.message(
            party_id,
            "alpha",
            channel,
            "beta",
            "RESULT",
            "Research result is ready for the current party cycle.",
            refs=[cycle_id],
        )
        self.party.message(
            party_id,
            "beta",
            channel,
            "alpha",
            "VERIFY",
            "Build result is ready and I verified the handoff for this cycle.",
            refs=[cycle_id],
        )

    def _outcomes(self, goal_a, goal_b, suffix=""):
        return [
            {"outcome_ref": f"outcome-a{suffix}", "agent": "alpha", "goal_id": goal_a, "witness_ref": f"witness-a{suffix}", "status": "VERIFIED"},
            {"outcome_ref": f"outcome-b{suffix}", "agent": "beta", "goal_id": goal_b, "witness_ref": f"witness-b{suffix}", "status": "VERIFIED"},
        ]

    def test_big3_3x5x7x9_and_capped_cycle_scoped_credit(self):
        party_id, channel, goal_a, goal_b = self._formed_party()
        self._planning_braid(party_id, channel)
        plan = self.party.steer(party_id, actor="alpha")
        self.assertEqual(plan["candidate_count"], 15)
        self.assertEqual(
            plan["suite"]["shape"],
            {"families": 3, "variants_per_family": 5, "stages": 7, "output_heads": 9},
        )
        self.assertEqual(tuple(plan["heads"]), OUTPUT_HEADS)
        self.assertEqual(plan["heads"]["xp_multiplier"]["value"], 1.0)
        self.assertEqual(plan["pareto"]["model_count"], 16)

        self._cycle_braid(party_id, channel, plan["cycle_id"])
        credited = self.surface._cycle_credit(
            party_id,
            plan["cycle_id"],
            self._outcomes(goal_a, goal_b),
            [
                {"agent": "alpha", "source_xp_ref": "quest-xp-alpha", "base_xp": 100, "witness_ref": "quest-xp-witness-alpha"},
                {"agent": "beta", "source_xp_ref": "quest-xp-beta", "base_xp": 100, "witness_ref": "quest-xp-witness-beta"},
            ],
            actor="verifier",
        )
        self.assertEqual(credited["status"], "BONUS_CREDITED")
        self.assertEqual(credited["credit"]["communication_scope"], "CURRENT_CYCLE_REFS_ONLY")
        self.assertGreater(credited["credit"]["bonus_rate"], 0.0)
        self.assertLessEqual(credited["credit"]["bonus_rate"], 0.05)
        self.assertEqual(len(credited["awards"]), 2)
        self.assertTrue(all(0 < row["bonus_xp"] <= 5 for row in credited["awards"]))

    def test_historical_braid_does_not_unlock_new_cycle(self):
        party_id, channel, goal_a, goal_b = self._formed_party()
        self._planning_braid(party_id, channel)
        plan = self.party.steer(party_id)
        locked = self.surface._cycle_credit(
            party_id,
            plan["cycle_id"],
            self._outcomes(goal_a, goal_b),
            [{"agent": "alpha", "source_xp_ref": "quest-a", "base_xp": 100, "witness_ref": "quest-wa"}],
        )
        self.assertEqual(locked["status"], "BONUS_LOCKED")
        self.assertEqual(locked["credit"]["bonus_rate"], 0.0)
        self.assertFalse(locked["credit"]["gates"]["communication"])
        self.assertEqual(locked["awards"], [])

    def test_outcomes_and_upstream_xp_receipts_are_single_use(self):
        party_id, channel, goal_a, goal_b = self._formed_party()
        self._planning_braid(party_id, channel)
        plan = self.party.steer(party_id)
        self._cycle_braid(party_id, channel, plan["cycle_id"])
        outcomes = self._outcomes(goal_a, goal_b)
        self.surface._cycle_credit(
            party_id,
            plan["cycle_id"],
            outcomes,
            [
                {"agent": "alpha", "source_xp_ref": "global-xp-alpha", "base_xp": 100, "witness_ref": "xpa"},
                {"agent": "beta", "source_xp_ref": "global-xp-beta", "base_xp": 100, "witness_ref": "xpb"},
            ],
        )
        with self.assertRaises(ValueError):
            self.surface._cycle_credit(
                party_id,
                plan["cycle_id"],
                outcomes,
                [
                    {"agent": "alpha", "source_xp_ref": "fresh-alpha", "base_xp": 100, "witness_ref": "fresh-a"},
                    {"agent": "beta", "source_xp_ref": "fresh-beta", "base_xp": 100, "witness_ref": "fresh-b"},
                ],
            )

        party2, channel2, goal_a2, goal_b2 = self._formed_party("-2")
        self._planning_braid(party2, channel2)
        plan2 = self.party.steer(party2)
        self._cycle_braid(party2, channel2, plan2["cycle_id"])
        with self.assertRaises(ValueError):
            self.surface._cycle_credit(
                party2,
                plan2["cycle_id"],
                self._outcomes(goal_a2, goal_b2, "-2"),
                [
                    {"agent": "alpha", "source_xp_ref": "global-xp-alpha", "base_xp": 100, "witness_ref": "other-a"},
                    {"agent": "beta", "source_xp_ref": "global-xp-beta", "base_xp": 100, "witness_ref": "other-b"},
                ],
            )

    def test_base_server_exports_party_tools_and_resource(self):
        response = self.server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertTrue(PARTY_TOOL_NAMES <= names)
        resources = self.server.handle({"jsonrpc": "2.0", "id": 2, "method": "resources/list"})
        uris = {row["uri"] for row in resources["result"]["resources"]}
        self.assertIn(PARTY_RESOURCE["uri"], uris)

    def test_mcp_form_join_and_state_use_canonical_server(self):
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
        state = joined["result"]["structuredContent"]
        self.assertEqual(len(state["members"]), 2)
        read = self.server.handle(
            {"jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": {"uri": PARTY_RESOURCE["uri"]}}
        )
        self.assertIn("result", read)
        text = read["result"]["contents"][0]["text"]
        self.assertIn("CURRENT_CYCLE_REFS_ONLY", text)
        self.assertIn("maximum_party_bonus_rate", text)


if __name__ == "__main__":
    unittest.main()
