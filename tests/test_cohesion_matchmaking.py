from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.server import Server


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _fixture(base: Path):
    local = base / "local"
    local.mkdir()
    _run(local, "init", "-b", "master")
    _run(local, "config", "user.name", "local")
    _run(local, "config", "user.email", "local@example.invalid")
    (local / "seed.txt").write_text("seed\n", encoding="utf-8")
    _run(local, "add", ".")
    _run(local, "commit", "-m", "seed")

    origin = base / "origin.git"
    proc = subprocess.run(["git", "init", "--bare", str(origin)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(local, "remote", "add", "origin", str(origin))
    _run(local, "push", "-u", "origin", "master")

    clone = base / "clone"
    proc = subprocess.run(["git", "clone", str(origin), str(clone)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(clone, "config", "user.name", "clone")
    _run(clone, "config", "user.email", "clone@example.invalid")
    return local, clone


class CohesionMatchmakingTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        local, clone = _fixture(Path(self.td.name))
        self.a = Server(str(Path(self.td.name) / "a.db"), git_root=local)
        self.b = Server(str(Path(self.td.name) / "b.db"), git_root=clone)
        self.addCleanup(self.a.store.close)
        self.addCleanup(self.b.store.close)
        self.board_a = MessageBoardRuntime(self.a.git)
        self.board_b = MessageBoardRuntime(self.b.git)
        self.seq = 0

    def rpc(self, server, method, params=None):
        self.seq += 1
        message = {"jsonrpc":"2.0","id":self.seq,"method":method}
        if params is not None:
            message["params"] = params
        return server.handle(message)

    def tool(self, server, name, args, expect_error=False):
        response = self.rpc(server, "tools/call", {"name":name,"arguments":args})
        result = response["result"]
        if expect_error:
            self.assertTrue(result.get("isError"), response)
            return result
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    def present(self, board, agent, task, work_key, targets=None, **kwargs):
        result = board.present(
            agent_id=agent,
            task=task,
            work_key=work_key,
            targets=targets or [],
            **kwargs,
        )
        self.assertEqual(result["status"], "PRESENT", result)
        return result

    def publish(self, server, request_id, agent_id, kind, capabilities, goal_ref, **kwargs):
        args = {
            "request_id":request_id,
            "agent_id":agent_id,
            "kind":kind,
            "capabilities":capabilities,
            "goal_ref":goal_ref,
        }
        args.update(kwargs)
        return self.tool(server, "athena_cohesion_request_offer", args)

    def test_tools_and_resource_register_without_displacing_existing_surfaces(self):
        tools = {row["name"] for row in self.rpc(self.a, "tools/list")["result"]["tools"]}
        for name in [
            "athena_message_board",
            "athena_party_form",
            "athena_impossible_open",
            "athena_transport_aor_to_collective",
            "athena_cohesion_request_offer",
            "athena_cohesion_matchmake",
            "athena_cohesion_coalition",
            "athena_cohesion_solo_party_compare",
        ]:
            self.assertIn(name, tools)
        resources = {row["uri"] for row in self.rpc(self.a, "resources/list")["result"]["resources"]}
        for uri in ["athena://party-coordination/v1", "athena://impossible-godboard/v1", "athena://cohesion/v1"]:
            self.assertIn(uri, resources)

    def test_request_offer_requires_presence_and_is_semantically_idempotent(self):
        held = self.publish(self.a, "NEED.X", "alpha", "NEED", ["code"], "goal.x")
        self.assertEqual(held["status"], "COHESION_AGENT_NOT_PRESENT_HOLD")
        self.present(self.board_a, "alpha", "Build X", "x", ["x.py"])
        first = self.publish(
            self.a,
            "NEED.X",
            "alpha",
            "NEED",
            ["code"],
            "goal.x",
            dependencies=["schema.ready"],
            quest_ref="Athena#192",
            life_policy="STAY_IN_GAME_LIFE_LOOP_V1",
            clear_condition_digest="sha256:criterion",
        )
        self.assertEqual(first["status"], "COHESION_NEED_PUBLISHED")
        self.assertFalse(first["assignment_authority"])
        digest = first["request"]["request_digest"]

        self.present(self.board_b, "beta", "Unrelated lane", "beta", ["beta.py"])
        replay = self.publish(
            self.a,
            "NEED.X",
            "alpha",
            "NEED",
            ["code"],
            "goal.x",
            dependencies=["schema.ready"],
            quest_ref="Athena#192",
            life_policy="STAY_IN_GAME_LIFE_LOOP_V1",
            clear_condition_digest="sha256:criterion",
        )
        self.assertEqual(replay["status"], "COHESION_REQUEST_ALREADY_PUBLISHED")
        self.assertTrue(replay["idempotent"])
        self.assertEqual(replay["request"]["request_digest"], digest)

        self.publish(
            self.a,
            "NEED.X",
            "alpha",
            "NEED",
            ["review"],
            "goal.x",
            expect_error=True,
        ) if False else None
        conflict = self.tool(
            self.a,
            "athena_cohesion_request_offer",
            {"request_id":"NEED.X","agent_id":"alpha","kind":"NEED","capabilities":["review"],"goal_ref":"goal.x"},
            expect_error=True,
        )
        self.assertIn("COHESION_REQUEST_ID_CONFLICT", conflict["content"][0]["text"])

    def test_cross_clone_matchmaking_ranks_explicit_offers_and_does_not_assign(self):
        self.present(self.board_a, "alpha", "Need implementation and tests", "need-alpha", ["alpha.txt"])
        self.publish(
            self.a, "NEED.A", "alpha", "NEED", ["code","tests"], "goal.implementation",
            role="BUILDER", dependencies=["api.ready"], needed_units=1,
        )
        self.present(self.board_b, "beta", "Available implementation lane", "offer-beta", ["beta.py"])
        self.publish(
            self.b, "OFFER.B", "beta", "OFFER", ["code","tests"], "offer.impl",
            role="BUILDER", provides=["api.ready"], capacity_units=2,
        )
        self.present(self.board_a, "gamma", "Available partial lane", "offer-gamma", ["gamma.py"])
        self.publish(
            self.a, "OFFER.G", "gamma", "OFFER", ["code"], "offer.partial",
            role="REVIEWER", capacity_units=1,
        )
        before = {
            row["agent_id"]: row["claim_id"]
            for row in self.board_b.read(shared_remote_mode="REQUIRED")["active"]
        }
        result = self.tool(self.b, "athena_cohesion_matchmake", {"need_id":"NEED.A","limit":10})
        self.assertEqual(result["status"], "COHESION_MATCHES")
        eligible = [row for row in result["candidates"] if row["eligible"]]
        self.assertGreaterEqual(len(eligible), 2)
        self.assertEqual(eligible[0]["agent_id"], "beta")
        self.assertGreater(eligible[0]["score"], eligible[1]["score"])
        self.assertIn("FULL_CAPABILITY_FIT", eligible[0]["reason_codes"])
        self.assertIn("DEPENDENCY_UNLOCK", eligible[0]["reason_codes"])
        self.assertFalse(result["assignment_authority"])
        after = {
            row["agent_id"]: row["claim_id"]
            for row in self.board_b.read(shared_remote_mode="REQUIRED")["active"]
        }
        self.assertEqual(before, after, "advisory matchmake must not mutate claims or presence")

    def test_exact_duplicate_is_upstream_board_hold_and_declared_replica_is_explicit(self):
        self.present(self.board_a, "alpha", "Benchmark solver", "solver", ["solver.py"])
        self.publish(
            self.a, "NEED.SOLVER", "alpha", "NEED", ["verify"], "Benchmark solver",
            allow_collaboration=False,
        )
        duplicate = self.board_b.present(
            agent_id="beta", task="Benchmark solver", work_key="solver", targets=["solver.py"]
        )
        self.assertEqual(duplicate["status"], "DUPLICATE_WORK_HOLD")
        replica = self.board_b.present(
            agent_id="beta",
            task="Benchmark solver",
            work_key="solver",
            targets=["solver.py"],
            mode="REPLICA",
            replication_reason="independent verification",
        )
        self.assertEqual(replica["status"], "PRESENT")
        self.publish(self.b, "OFFER.REPLICA", "beta", "OFFER", ["verify"], "Independent verification")
        result = self.tool(self.a, "athena_cohesion_matchmake", {"need_id":"NEED.SOLVER"})
        candidate = next(row for row in result["candidates"] if row["agent_id"] == "beta")
        self.assertTrue(candidate["eligible"])
        self.assertEqual(candidate["collision"]["treatment"], "JOIN_OR_PARTITION_REQUIRED")
        self.assertTrue(candidate["collision"]["declared_collaboration_or_replica"])

    def test_coalition_respects_offer_capacity_and_creates_no_claims(self):
        self.present(self.board_a, "alpha", "Campaign proposer", "proposal", ["proposal.md"])
        self.publish(self.a, "NEED.CODE", "alpha", "NEED", ["code"], "goal.code")
        self.present(self.board_b, "delta", "Review requester", "delta", ["delta.md"])
        self.publish(self.b, "NEED.REVIEW", "delta", "NEED", ["review"], "goal.review")
        self.present(self.board_a, "beta", "Code capacity", "beta-code", ["beta.py"])
        self.publish(self.a, "OFFER.CODE", "beta", "OFFER", ["code"], "offer.code", capacity_units=1)
        self.present(self.board_b, "gamma", "Review capacity", "gamma-review", ["gamma.md"])
        self.publish(self.b, "OFFER.REVIEW", "gamma", "OFFER", ["review"], "offer.review", capacity_units=1)

        before = {
            row["agent_id"]: row["claim_id"]
            for row in self.board_a.read(shared_remote_mode="REQUIRED")["active"]
        }
        result = self.tool(
            self.a,
            "athena_cohesion_coalition",
            {
                "campaign_id":"CAMPAIGN.MATCH.1",
                "proposer_id":"alpha",
                "need_ids":["NEED.CODE","NEED.REVIEW"],
                "max_participants":4,
                "exit_criteria":["both goals witnessed"],
            },
        )
        self.assertEqual(result["status"], "COHESION_COALITION_PROPOSED")
        assignments = result["proposal"]["assignments"]
        self.assertEqual(len(assignments), 2)
        self.assertEqual({row["assigned_candidate"] for row in assignments}, {"beta","gamma"})
        self.assertFalse(result["assignment_authority"])
        after = {
            row["agent_id"]: row["claim_id"]
            for row in self.board_a.read(shared_remote_mode="REQUIRED")["active"]
        }
        self.assertEqual(before, after)

        replay = self.tool(
            self.b,
            "athena_cohesion_coalition",
            {"campaign_id":"CAMPAIGN.MATCH.1","proposer_id":"alpha","need_ids":["NEED.REVIEW","NEED.CODE"],"max_participants":4,"exit_criteria":["both goals witnessed"]},
        )
        self.assertEqual(replay["status"], "COHESION_COALITION_ALREADY_PROPOSED")
        self.assertTrue(replay["idempotent"])

        conflict = self.tool(
            self.a,
            "athena_cohesion_coalition",
            {"campaign_id":"CAMPAIGN.MATCH.1","proposer_id":"alpha","need_ids":["NEED.CODE","NEED.REVIEW"],"max_participants":5},
            expect_error=True,
        )
        self.assertIn("COHESION_CAMPAIGN_ID_CONFLICT", conflict["content"][0]["text"])

    @staticmethod
    def sample(mission_id, match_key, verified_delta, cost, *, dup=0, stale=0, interrupts=0, merge=0, meta=0, closure=True, violations=0):
        return {
            "mission_id":mission_id,
            "match_key":match_key,
            "evidence_refs":[f"receipt://{mission_id}"],
            "productive_transition_count":verified_delta,
            "verified_delta":verified_delta,
            "cost":cost,
            "duplicate_actions":dup,
            "stale_actions":stale,
            "human_interrupts":interrupts,
            "merge_debt":merge,
            "meta_overhead":meta,
            "closure":closure,
            "stop_class":"SUCCESS_CLOSED" if closure else "NO_POSITIVE_FRONTIER",
            "authority_evidence_violations":violations,
            "wasted_overrun":0,
        }

    @staticmethod
    def rule(min_pairs=2):
        return {
            "rule_ref":"Athena#192/frozen-rule-v1",
            "frozen_before_results":True,
            "min_pairs":min_pairs,
            "min_primary_effect":0.10,
            "max_duplicate_regression":0,
            "max_stale_regression":0,
            "max_human_interrupt_regression":0,
            "max_meta_overhead_regression":0,
        }

    def test_solo_party_compare_returns_unknown_when_underpowered(self):
        self.present(self.board_a, "observer", "Compare GTC party effects", "compare", ["compare.json"])
        result = self.tool(
            self.a,
            "athena_cohesion_solo_party_compare",
            {
                "comparison_id":"COMPARE.WEAK",
                "observer_id":"observer",
                "solo_samples":[self.sample("solo-1","m1",10,10)],
                "party_samples":[self.sample("party-1","m1",12,10)],
                "decision_rule":self.rule(min_pairs=2),
            },
        )
        self.assertEqual(result["decision"], "UNKNOWN_INSUFFICIENT_EVIDENCE")
        self.assertIn("INSUFFICIENT_MATCHED_PAIRS", result["quality_reasons"])
        self.assertEqual(result["causal_effect"], "UNKNOWN")
        self.assertFalse(result["promotion_authority"])

    def test_solo_party_compare_can_pass_frozen_descriptive_rule_without_claiming_causality(self):
        self.present(self.board_a, "observer", "Compare matched missions", "compare", ["compare.json"])
        solo = [
            self.sample("solo-1","m1",10,10,dup=1,interrupts=2,meta=2),
            self.sample("solo-2","m2",8,8,dup=1,interrupts=1,meta=1),
            self.sample("solo-3","m3",12,12,dup=0,interrupts=1,meta=1),
        ]
        party = [
            self.sample("party-1","m1",15,10,dup=0,interrupts=1,meta=1),
            self.sample("party-2","m2",12,8,dup=0,interrupts=0,meta=1),
            self.sample("party-3","m3",18,12,dup=0,interrupts=0,meta=1),
        ]
        args = {
            "comparison_id":"COMPARE.STRONG",
            "observer_id":"observer",
            "solo_samples":solo,
            "party_samples":party,
            "decision_rule":self.rule(min_pairs=3),
        }
        result = self.tool(self.a, "athena_cohesion_solo_party_compare", args)
        self.assertEqual(result["decision"], "PARTY_RULE_PASS_DESCRIPTIVE")
        self.assertTrue(result["rule_pass"])
        self.assertEqual(result["standing"], "MATCHED_DESCRIPTIVE_OBSERVATION")
        self.assertEqual(result["causal_effect"], "UNKNOWN")
        self.assertGreater(result["summary"]["verified_delta_per_cost"]["mean_party_minus_solo"], 0)
        self.assertLessEqual(result["summary"]["duplicate_actions"]["mean_party_minus_solo"], 0)
        receipt = result["receipt_digest"]

        replay_args = dict(args)
        replay_args["solo_samples"] = list(reversed(solo))
        replay_args["party_samples"] = list(reversed(party))
        replay = self.tool(self.b, "athena_cohesion_solo_party_compare", replay_args)
        self.assertTrue(replay["idempotent"])
        self.assertEqual(replay["receipt_digest"], receipt)

    def test_resource_exposes_authority_and_evidence_boundaries(self):
        resource = json.loads(
            self.rpc(self.a, "resources/read", {"uri":"athena://cohesion/v1"})
            ["result"]["contents"][0]["text"]
        )
        self.assertEqual(resource["transport"], "ATHENA Message Board V1")
        self.assertIn("athena_cohesion_matchmake", resource["tools"])
        self.assertIn("athena_cohesion_solo_party_compare", resource["tools"])
        self.assertTrue(any("MATCHED_DESCRIPTIVE_DIFFERENCE" in law for law in resource["laws"]))
        self.assertTrue(any("FUZZY_SIMILARITY" in law for law in resource["laws"]))
        bench = self.tool(self.a, "athena_benchmark", {})
        self.assertIn("cohesion_version", bench)
        self.assertIn("party_coordination_version", bench)
        self.assertIn("impossible_godboard_version", bench)


if __name__ == "__main__":
    unittest.main()
