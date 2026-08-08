from __future__ import annotations

import unittest

from athena_mcp.party_matchmaking import rank_party_matches


def state(
    party_id,
    *,
    goals,
    members,
    capacity=4,
    status="OPEN",
    shared=True,
):
    return {
        "party": {
            "party_id": party_id,
            "status": status,
            "capacity": capacity,
            "goals": goals,
        },
        "members": members,
        "board": {"shared_frontier_verified": shared},
    }


class PartyMatchmakingTests(unittest.TestCase):
    def test_ranks_complementary_gap_and_capability(self):
        parties = [
            state(
                "P.A",
                goals=[
                    {"goal_id": "analysis", "required_capabilities": ["analysis"]},
                    {"goal_id": "code", "required_capabilities": ["code"]},
                ],
                members=[
                    {
                        "agent_id": "alpha",
                        "goal_refs": ["analysis"],
                        "capabilities": ["analysis"],
                    }
                ],
            ),
            state(
                "P.B",
                goals=[
                    {"goal_id": "docs", "required_capabilities": ["writing"]},
                    {"goal_id": "review", "required_capabilities": ["review"]},
                ],
                members=[
                    {
                        "agent_id": "gamma",
                        "goal_refs": ["docs"],
                        "capabilities": ["writing"],
                    }
                ],
            ),
        ]
        result = rank_party_matches(
            agent_id="beta",
            party_states=parties,
            capabilities=["code"],
            desired_goal_refs=["code"],
        )
        row = result["recommendations"][0]
        self.assertEqual(row["party_id"], "P.A")
        self.assertEqual(row["suggested_goal_refs"], ["code"])
        self.assertFalse(row["next"]["auto_join"])
        self.assertTrue(row["next"]["requires_explicit_task_relation"])
        self.assertFalse(result["execution_authority"])
        self.assertFalse(result["xp_authority"])
        self.assertFalse(result["auto_join"])

    def test_filters_closed_full_existing_member_and_unverified_frontier(self):
        goals = [
            {"goal_id": "a", "required_capabilities": []},
            {"goal_id": "b", "required_capabilities": []},
        ]
        parties = [
            state("P.CLOSED", goals=goals, members=[], status="CLOSED"),
            state(
                "P.FULL",
                goals=goals,
                members=[{"agent_id": "a"}, {"agent_id": "b"}],
                capacity=2,
            ),
            state("P.MEMBER", goals=goals, members=[{"agent_id": "beta"}]),
            state("P.STALE", goals=goals, members=[], shared=False),
        ]
        result = rank_party_matches(agent_id="beta", party_states=parties)
        self.assertEqual(result["status"], "NO_MATCH")
        reasons = {row["party_id"]: row["reason"] for row in result["rejected"]}
        self.assertEqual(reasons["P.CLOSED"], "PARTY_NOT_OPEN")
        self.assertEqual(reasons["P.FULL"], "PARTY_FULL")
        self.assertEqual(reasons["P.MEMBER"], "ALREADY_MEMBER")
        self.assertEqual(reasons["P.STALE"], "SHARED_FRONTIER_HOLD")

    def test_missing_capability_declaration_is_unknown_not_zero(self):
        party = state(
            "P.UNKNOWN",
            goals=[
                {"goal_id": "analysis", "required_capabilities": ["analysis"]},
                {"goal_id": "code", "required_capabilities": ["code"]},
            ],
            members=[
                {
                    "agent_id": "alpha",
                    "goal_refs": ["analysis"],
                    "capabilities": ["analysis"],
                }
            ],
        )
        result = rank_party_matches(agent_id="beta", party_states=[party])
        row = result["recommendations"][0]
        self.assertEqual(row["dimension_standing"]["capability_fit"], "UNKNOWN")
        self.assertEqual(row["dimension_standing"]["capability_novelty"], "UNKNOWN")
        self.assertIsNone(row["dimensions"]["capability_fit"])
        self.assertIn("code", row["suggested_goal_refs"])

    def test_deterministic_under_party_input_reordering(self):
        goals = [
            {"goal_id": "a", "required_capabilities": []},
            {"goal_id": "b", "required_capabilities": []},
        ]
        a = state("P.A", goals=goals, members=[{"agent_id": "x", "goal_refs": ["a"]}])
        b = state("P.B", goals=goals, members=[{"agent_id": "y", "goal_refs": ["a"]}])
        first = rank_party_matches(agent_id="beta", party_states=[b, a])
        second = rank_party_matches(agent_id="beta", party_states=[a, b])
        self.assertEqual(first["result_digest"], second["result_digest"])
        self.assertEqual(
            [row["party_id"] for row in first["recommendations"]],
            ["P.A", "P.B"],
        )

    def test_unverified_snapshot_requires_explicit_opt_out_and_remains_non_authoritative(self):
        goals = [
            {"goal_id": "a", "required_capabilities": []},
            {"goal_id": "b", "required_capabilities": []},
        ]
        party = state("P.STALE", goals=goals, members=[], shared=False)
        held = rank_party_matches(agent_id="beta", party_states=[party])
        self.assertEqual(held["status"], "NO_MATCH")

        inspected = rank_party_matches(
            agent_id="beta",
            party_states=[party],
            require_shared_frontier=False,
        )
        self.assertEqual(inspected["status"], "OK")
        row = inspected["recommendations"][0]
        self.assertFalse(row["shared_frontier_verified"])
        self.assertFalse(row["execution_authority"])
        self.assertFalse(row["xp_authority"])
        self.assertFalse(row["next"]["auto_join"])


if __name__ == "__main__":
    unittest.main()
