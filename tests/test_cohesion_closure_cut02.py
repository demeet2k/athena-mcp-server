from __future__ import annotations

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
    subprocess.run(
        ["git", "--git-dir", str(origin), "symbolic-ref", "HEAD", "refs/heads/master"],
        check=True,
        capture_output=True,
    )

    clone = base / "clone"
    proc = subprocess.run(["git", "clone", str(origin), str(clone)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(clone, "config", "user.name", "clone")
    _run(clone, "config", "user.email", "clone@example.invalid")
    return local, clone


class CohesionClosureCut02Tests(unittest.TestCase):
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
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return server.handle(message)

    def tool(self, server, name, args, expect_error=False):
        response = self.rpc(server, "tools/call", {"name": name, "arguments": args})
        result = response["result"]
        if expect_error:
            self.assertTrue(result.get("isError"), response)
            return result
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    def present(self, board, agent, task, work_key, targets=None):
        result = board.present(
            agent_id=agent,
            task=task,
            work_key=work_key,
            targets=targets or [],
        )
        self.assertEqual(result["status"], "PRESENT", result)
        return result

    def handoff(self):
        self.present(self.board_a, "alpha", "route guidance", "WK:ALPHA", ["a.txt"])
        self.present(self.board_b, "beta", "consume guidance", "WK:BETA", ["b.txt"])
        posted = self.board_a.post(
            agent_id="alpha",
            message="please inspect artifact://x",
            message_kind="HANDOFF",
            recipients=["beta"],
        )
        self.assertEqual(posted["status"], "POSTED")
        return posted["message_event"]

    def test_cut02_tools_and_resource_are_composed_with_existing_guards(self):
        names = {row["name"] for row in self.rpc(self.a, "tools/list")["result"]["tools"]}
        for name in [
            "athena_cohesion_consume",
            "athena_cohesion_dependency_cone",
            "athena_cohesion_outcome_credit",
            "athena_cohesion_pulse",
            "athena_cohesion_duplicate_guard",
            "athena_cohesion_solo_party_compare",
        ]:
            self.assertIn(name, names)
        resource = self.rpc(
            self.a,
            "resources/read",
            {"uri": "athena://cohesion/v1"},
        )["result"]["contents"][0]["text"]
        self.assertIn("COHESION.EVIDENCE.GUARD.1", resource)
        self.assertIn("COHESION.DEPENDENCY.CONE.1", resource)
        self.assertIn("ATHENA.COHESION.CLOSURE.CUT02.1", resource)

    def test_route_and_ack_do_not_establish_consumption(self):
        route = self.handoff()
        ack = self.board_b.ack(agent_id="beta", message_id=route["event_id"])
        self.assertEqual(ack["status"], "ACKED")
        pulse = self.tool(
            self.b,
            "athena_cohesion_pulse",
            {"observer_id": "beta"},
        )
        self.assertFalse(pulse["execution_authority"])
        self.assertTrue(any(
            row["route_ref"] == route["event_id"]
            for row in pulse["unconsumed_routes"]
        ))
        self.assertEqual(pulse["ranked_interventions"][0]["intervention"], "CONSUME_REVIEW")

    def test_explicit_rejection_is_consumed_without_truth_or_compliance(self):
        route = self.handoff()
        consumed = self.tool(
            self.b,
            "athena_cohesion_consume",
            {
                "consumption_id": "consume.reject.1",
                "recipient_id": "beta",
                "route_ref": route["event_id"],
                "expected_route_digest": None,
                "decision": "REJECTED",
                "behavior_change": False,
                "reason": "evidence conflicts with current plan",
                "evidence_refs": ["evidence://beta/reject"],
            },
        )
        self.assertEqual(consumed["status"], "COHESION_CONSUMPTION_RECORDED")
        self.assertTrue(consumed["consumption_established"])
        self.assertFalse(consumed["accepted"])
        self.assertFalse(consumed["behavior_changed"])
        self.assertFalse(consumed["truth_authority"])
        self.assertFalse(consumed["compliance_authority"])

        pulse = self.tool(self.a, "athena_cohesion_pulse", {"observer_id": "alpha"})
        self.assertFalse(any(
            row["route_ref"] == route["event_id"] and row["recipient_id"] == "beta"
            for row in pulse["unconsumed_routes"]
        ))

    def test_accept_changed_requires_behavior_change_reference(self):
        route = self.handoff()
        error = self.tool(
            self.b,
            "athena_cohesion_consume",
            {
                "consumption_id": "consume.invalid.1",
                "recipient_id": "beta",
                "route_ref": route["event_id"],
                "decision": "ACCEPTED_CHANGED",
                "behavior_change": True,
            },
            expect_error=True,
        )
        self.assertIn("behavior_change_ref", error["content"][0]["text"])

    def test_outcome_credit_separates_execution_coordination_truth_and_causality(self):
        route = self.handoff()
        consumed = self.tool(
            self.b,
            "athena_cohesion_consume",
            {
                "consumption_id": "consume.changed.1",
                "recipient_id": "beta",
                "route_ref": route["event_id"],
                "decision": "ACCEPTED_CHANGED",
                "behavior_change": True,
                "behavior_change_ref": "event://beta/changed-plan",
                "evidence_refs": ["evidence://consume/1"],
            },
        )
        consumption_ref = consumed["event"]["event_id"]
        credit = self.tool(
            self.a,
            "athena_cohesion_outcome_credit",
            {
                "credit_id": "credit.1",
                "observer_id": "alpha",
                "outcomes": [{
                    "outcome_id": "outcome.1",
                    "execution_ref": "exec://1",
                    "observation_ref": "obs://1",
                    "verification_ref": "verify://1",
                    "evidence_refs": ["evidence://outcome/1"],
                    "consumption_refs": [consumption_ref],
                }],
            },
        )
        self.assertEqual(credit["decision"], "DESCRIPTIVE_ATTRIBUTION_READY")
        row = credit["rows"][0]
        self.assertEqual(row["coordination_contribution"], "OBSERVED_CONSUMPTION_ASSOCIATION")
        self.assertEqual(row["causal_effect"], "UNKNOWN")
        self.assertIsNone(credit["scalar_credit"])
        self.assertFalse(credit["truth_authority"])
        self.assertFalse(credit["promotion_authority"])

    def test_outcome_credit_duplicate_evidence_and_missing_observation_fail_closed(self):
        self.present(self.board_a, "observer", "credit outcomes", "WK:OBS", ["obs.json"])
        result = self.tool(
            self.a,
            "athena_cohesion_outcome_credit",
            {
                "credit_id": "credit.duplicate",
                "observer_id": "observer",
                "outcomes": [
                    {"outcome_id": "o1", "execution_ref": "exec://1", "evidence_refs": ["same://evidence"]},
                    {"outcome_id": "o2", "execution_ref": "exec://2", "evidence_refs": ["same://evidence"]},
                ],
            },
        )
        self.assertEqual(result["decision"], "UNKNOWN_INSUFFICIENT_EVIDENCE")
        self.assertIn("DUPLICATE_EVIDENCE_ATTRIBUTION", result["quality_reasons"])
        self.assertIn("UNOBSERVED_OUTCOME_EFFECT", result["quality_reasons"])
        self.assertEqual(result["causal_effect"], "UNKNOWN")

    def test_dependency_cone_targets_only_exact_changed_lane(self):
        self.present(self.board_a, "alpha", "owns x", "WK:X", ["src/x.py"])
        self.present(self.board_b, "beta", "owns y", "WK:Y", ["src/y.py"])
        result = self.tool(
            self.a,
            "athena_cohesion_dependency_cone",
            {
                "change": {"kind": "TARGET", "targets": ["src/x.py"]},
            },
        )
        affected = {
            row["agent_id"]
            for row in (result["directly_affected"] + result["transitively_affected"])
        }
        self.assertEqual(affected, {"alpha"})
        self.assertIn("beta", {row["agent_id"] for row in result["unaffected_observed_lanes"]})
        self.assertFalse(result["execution_authority"])

    @staticmethod
    def sample(mission_id, match_key, delta):
        return {
            "mission_id": mission_id,
            "match_key": match_key,
            "evidence_refs": [f"receipt://{mission_id}"],
            "productive_transition_count": delta,
            "verified_delta": delta,
            "cost": 10,
            "duplicate_actions": 0,
            "stale_actions": 0,
            "human_interrupts": 0,
            "merge_debt": 0,
            "meta_overhead": 0,
            "closure": True,
            "authority_evidence_violations": 0,
            "wasted_overrun": 0,
        }

    def test_pulse_evidence_hold_outranks_favorable_descriptive_signal(self):
        self.present(self.board_a, "observer", "compare", "WK:COMPARE", ["compare.json"])
        compared = self.tool(
            self.a,
            "athena_cohesion_solo_party_compare",
            {
                "comparison_id": "compare.underpowered",
                "observer_id": "observer",
                "solo_samples": [self.sample("solo-1", "m1", 10)],
                "party_samples": [self.sample("party-1", "m1", 20)],
                "decision_rule": {
                    "rule_ref": "cut02/frozen",
                    "frozen_before_results": True,
                    "min_pairs": 2,
                    "min_primary_effect": 0.1,
                    "max_duplicate_regression": 0,
                    "max_stale_regression": 0,
                    "max_human_interrupt_regression": 0,
                    "max_meta_overhead_regression": 0,
                },
            },
        )
        self.assertEqual(compared["decision"], "UNKNOWN_INSUFFICIENT_EVIDENCE")
        pulse = self.tool(
            self.a,
            "athena_cohesion_pulse",
            {"observer_id": "observer", "comparison_id": "compare.underpowered"},
        )
        self.assertEqual(pulse["ranked_interventions"][0]["intervention"], "EVIDENCE_REQUIRED")
        self.assertFalse(pulse["stop_established"])
        self.assertFalse(pulse["execution_authority"])
        self.assertFalse(pulse["scheduler_authority"])


if __name__ == "__main__":
    unittest.main()
