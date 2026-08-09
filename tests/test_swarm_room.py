from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.swarm_room import (
    JOB_FAMILIES,
    compile_pulse,
    compile_shadow,
    contract,
    select_quest,
    target_horizon_counts,
)


def run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def clone(remote: Path, destination: Path) -> None:
    proc = subprocess.run(["git", "clone", str(remote), str(destination)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    run(destination, "config", "user.name", "swarm-room-test")
    run(destination, "config", "user.email", "swarm-room-test@example.invalid")


def fixture(base: Path):
    remote = base / "origin.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    seed = base / "seed"
    seed.mkdir()
    run(seed, "init", "-b", "master")
    run(seed, "config", "user.name", "seed")
    run(seed, "config", "user.email", "seed@example.invalid")
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    run(seed, "add", ".")
    run(seed, "commit", "-m", "seed")
    run(seed, "remote", "add", "origin", str(remote))
    run(seed, "push", "-u", "origin", "master")
    subprocess.run(["git", "--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/master"], check=True, capture_output=True)
    local_a, local_b = base / "local-a", base / "local-b"
    clone(remote, local_a)
    clone(remote, local_b)
    return remote, local_a, local_b


def resources(**overrides):
    value = {
        "tool_calls": 100,
        "tokens": 100000,
        "wall_seconds": 3600,
        "write_ops": 20,
        "api_calls": 100,
        "shared_sinks": [],
    }
    value.update(overrides)
    return value


def reserve(**overrides):
    value = {
        "tool_calls": 10,
        "tokens": 10000,
        "wall_seconds": 300,
        "write_ops": 2,
        "api_calls": 10,
        "shared_sinks": [],
    }
    value.update(overrides)
    return value


def quest(identifier: str, horizon: str, *, family="GIT_ENGINEERING", target=None, work_key=None, capability="code", score=3, resource=None):
    queue = {"W0": "Q1", "W1": "Q2", "W2": "Q3"}[horizon]
    return {
        "quest_id": identifier,
        "title": f"execute coherent quest {identifier}",
        "horizon": horizon,
        "queue_slot": queue,
        "job_family": family,
        "work_key": work_key or f"WK:{identifier}",
        "targets": [target or f"src/{identifier}.py"],
        "required_capabilities": [capability],
        "source_refs": [f"git://source/{identifier}"],
        "acceptance": [f"test:{identifier}", f"readback:{identifier}"],
        "dependency_refs": [],
        "satisfied_dependency_refs": [],
        "allowed_mutations": [f"branch:{identifier}"],
        "forbidden_claims": ["merge", "promotion", "production authority"],
        "resource_upper_bound": resource or {
            "tool_calls": 5,
            "tokens": 5000,
            "wall_seconds": 300,
            "write_ops": 1,
            "api_calls": 5,
            "shared_sinks": [],
        },
        "integration_owner": "root",
        "scores": {
            "dependency_unlock": score,
            "downstream_reach": score,
            "verified_gain": score,
            "information_gain": score,
            "evidence_gain": score,
            "urgency": score,
            "reversibility": score,
            "risk": 1,
            "estimated_cost": 1,
        },
        "admitted": True,
    }


class AllocationTests(unittest.TestCase):
    def test_exact_default_seats_for_population_growth(self):
        expected = {
            1: {"W0": 1, "W1": 0, "W2": 0},
            2: {"W0": 1, "W1": 1, "W2": 0},
            3: {"W0": 1, "W1": 1, "W2": 1},
            4: {"W0": 2, "W1": 1, "W2": 1},
            10: {"W0": 5, "W1": 3, "W2": 2},
        }
        for population, counts in expected.items():
            self.assertEqual(target_horizon_counts(population, {"W0", "W1", "W2"}), counts)

    def test_empty_horizon_gets_no_fake_seat(self):
        self.assertEqual(target_horizon_counts(10, {"W2"}), {"W0": 0, "W1": 0, "W2": 10})

    def test_pressure_variant_changes_ten_worker_mix(self):
        self.assertEqual(
            target_horizon_counts(10, {"W0", "W1", "W2"}, {"W0": 200, "W1": 200, "W2": 600}),
            {"W0": 3, "W1": 2, "W2": 5},
        )

    def test_population_percentages_sum_to_10000_basis_points(self):
        snapshot = {
            "status": "OK",
            "git_head": "head",
            "active": [
                {"agent_id": f"external-{index}", "details": None}
                for index in range(7)
            ],
        }
        pulse = compile_pulse(snapshot, [])
        self.assertEqual(sum(row["basis_points"] for row in pulse["actual_job_population"].values()), 10000)
        self.assertEqual(sum(row["basis_points"] for row in pulse["actual_horizon_population"].values()), 10000)
        self.assertEqual(pulse["observed_room_workers"], 0)
        self.assertEqual(pulse["external_unclassified_workers"], 7)

    def test_no_ready_quest_means_no_assignment(self):
        invalid = quest("bad", "W0")
        invalid["acceptance"] = []
        result = select_quest(
            active_rows=[], quests=[invalid], capabilities=["code"],
            room_budget=resources(), protected_reserve=reserve(),
        )
        self.assertEqual(result["status"], "NO_READY_QUESTS")
        self.assertIsNone(result["selected"])
        self.assertIn("EMPTY_ACCEPTANCE", result["held"][0]["reasons"])

    def test_unknown_or_extreme_cost_holds_instead_of_becoming_zero(self):
        unknown = quest("unknown", "W0")
        del unknown["resource_upper_bound"]["api_calls"]
        extreme = quest("extreme", "W0", resource={
            "tool_calls": 2**53 - 1,
            "tokens": 5000,
            "wall_seconds": 300,
            "write_ops": 1,
            "api_calls": 5,
            "shared_sinks": [],
        })
        result = select_quest(
            active_rows=[], quests=[unknown, extreme], capabilities=["code"],
            room_budget=resources(), protected_reserve=reserve(),
        )
        self.assertEqual(result["status"], "NO_READY_QUESTS")
        reasons = {row["quest_id"]: row["reasons"] for row in result["held"]}
        self.assertIn("QUEST_RESOURCE_api_calls_UNBOUND", reasons["unknown"])
        self.assertIn("RESOURCE_HOLD_tool_calls", reasons["extreme"])

    def test_self_score_is_ignored(self):
        low = quest("a", "W0", score=1)
        low["self_score"] = 999999
        high = quest("b", "W0", score=5)
        result = select_quest(
            active_rows=[], quests=[low, high], capabilities=["code"],
            room_budget=resources(), protected_reserve=reserve(),
        )
        self.assertEqual(result["selected"]["quest_id"], "b")

    def test_shadow_is_counterfactual_and_has_no_winner_or_authority(self):
        snapshot = {"git_head": "head", "active": [{"agent_id": f"a{index}"} for index in range(10)]}
        result = compile_shadow(snapshot, [quest("w0", "W0"), quest("w1", "W1"), quest("w2", "W2")], [
            {"variant_id": "delivery", "horizon_weights": {"W0": 600, "W1": 250, "W2": 150}},
            {"variant_id": "meta", "horizon_weights": {"W0": 200, "W1": 200, "W2": 600}},
        ])
        self.assertEqual(result["status"], "COUNTERFACTUAL_ONLY")
        self.assertIsNone(result["winner"])
        self.assertFalse(result["mutation_performed"])
        self.assertFalse(result["promotion_authority"])


class SwarmRoomIntegrationTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        _, local_a, local_b = fixture(Path(self._td.name))
        self.local_a, self.local_b = local_a, local_b
        self.board_a = MessageBoardRuntime(GitBackend(local_a))
        self.board_b = MessageBoardRuntime(GitBackend(local_b))
        self.prompt_digest = "sha256:" + "a" * 64
        self.contract_digest = contract()["room_contract_digest"]
        self._bind_prompt(self.board_a)
        self._bind_prompt(self.board_b)

    def _bind_prompt(self, board):
        board._compile_room_prompt = lambda task: {
            "status": "COMPILED",
            "profile": "MAXDEV",
            "prompt_stack_digest": self.prompt_digest,
            "git_head": board.git.head(),
            "selected_modules": ["core", "git_organism", "self_engineering"],
            "selected_overlays": [],
        }

    def enter(self, board, agent_id, quests, **kwargs):
        return board.room_enter(
            agent_id=agent_id,
            expected_git_head=kwargs.pop("expected_git_head", board.git.head()),
            prompt_stack_digest=kwargs.pop("prompt_stack_digest", self.prompt_digest),
            room_contract_digest=kwargs.pop("room_contract_digest", self.contract_digest),
            capabilities=kwargs.pop("capabilities", ["code"]),
            quests=quests,
            room_budget=kwargs.pop("room_budget", resources()),
            protected_reserve=kwargs.pop("protected_reserve", reserve()),
            **kwargs,
        )

    def test_enter_is_one_commit_with_presence_and_typed_event(self):
        before = self.board_a.git.head()
        result = self.enter(self.board_a, "agent-a", [quest("q1", "W0")])
        self.assertEqual(result["status"], "ROOM_ENTERED", result)
        after = self.board_a.git.head()
        self.assertEqual(run(self.local_a, "rev-list", "--count", f"{before}..{after}"), "1")
        paths = run(self.local_a, "diff-tree", "--no-commit-id", "--name-only", "-r", after).splitlines()
        self.assertEqual(len(paths), 2)
        self.assertTrue(any(path.endswith("agents/agent-a.json") for path in paths))
        event = json.loads(next((self.local_a / path).read_text(encoding="utf-8") for path in paths if "/events/" in path))
        self.assertEqual(event["kind"], "ROOM_ENTER")
        self.assertEqual(result["presence"]["claim_base_head"], before)
        self.assertTrue(result["durable_return"])

    def test_no_ready_quest_creates_no_commit_or_presence(self):
        bad = quest("bad", "W0")
        bad["admitted"] = False
        before = self.board_a.git.head()
        result = self.enter(self.board_a, "agent-a", [bad])
        self.assertEqual(result["status"], "NO_READY_QUESTS")
        self.assertEqual(self.board_a.git.head(), before)
        self.assertFalse((self.local_a / "runtime/message_board/v1/agents/agent-a.json").exists())

    def test_stale_head_and_prompt_digest_fail_closed_without_mutation(self):
        before = self.board_a.git.head()
        stale = self.enter(self.board_a, "agent-a", [quest("q1", "W0")], expected_git_head="0" * 40)
        self.assertEqual(stale["status"], "STALE_ROOM_HEAD_HOLD")
        wrong_prompt = self.enter(self.board_a, "agent-a", [quest("q1", "W0")], prompt_stack_digest="sha256:" + "b" * 64)
        self.assertEqual(wrong_prompt["status"], "PROMPT_STACK_MISMATCH_HOLD")
        self.assertEqual(self.board_a.git.head(), before)

    def test_contract_mismatch_fails_closed(self):
        result = self.enter(self.board_a, "agent-a", [quest("q1", "W0")], room_contract_digest="sha256:" + "0" * 64)
        self.assertEqual(result["status"], "ROOM_CONTRACT_MISMATCH_HOLD")

    def test_two_clone_race_detects_duplicate_target(self):
        first = self.enter(self.board_a, "agent-a", [quest("q1", "W0", target="src/shared.py", work_key="WK:SHARED")])
        self.assertEqual(first["status"], "ROOM_ENTERED")
        refreshed = self.board_b.read(shared_remote_mode="REQUIRED")
        self.assertTrue(refreshed["shared_frontier_verified"])
        second = self.enter(self.board_b, "agent-b", [quest("q2", "W1", target="SRC/shared.py/", work_key="WK:SHARED")])
        self.assertEqual(second["status"], "DUPLICATE_WORK_HOLD", second)
        self.assertFalse((self.local_b / "runtime/message_board/v1/agents/agent-b.json").exists())

    def test_done_requires_exact_acceptance_and_evidence_then_returns_in_one_commit(self):
        entered = self.enter(self.board_a, "agent-a", [quest("q1", "W0")])
        claim = entered["presence"]["claim_id"]
        before_return = self.board_a.git.head()
        hold = self.board_a.room_return(
            agent_id="agent-a", expected_claim_id=claim, expected_git_head=before_return,
            prompt_stack_digest=self.prompt_digest, room_contract_digest=self.contract_digest,
            result_status="DONE", summary="implemented and tested", acceptance_results={"test:q1": "PASS", "readback:q1": "PASS"}, evidence_refs=[],
        )
        self.assertEqual(hold["status"], "RESULT_EVIDENCE_HOLD")
        self.assertEqual(self.board_a.git.head(), before_return)
        result = self.board_a.room_return(
            agent_id="agent-a", expected_claim_id=claim, expected_git_head=before_return,
            prompt_stack_digest=self.prompt_digest, room_contract_digest=self.contract_digest,
            result_status="DONE", summary="implemented and tested", acceptance_results={"test:q1": "PASS", "readback:q1": "PASS"}, evidence_refs=["git://commit/abc", "test://suite/pass"],
        )
        self.assertEqual(result["status"], "ROOM_RETURNED", result)
        self.assertTrue(result["signed_out"])
        self.assertTrue(result["verified_return"])
        after = self.board_a.git.head()
        self.assertEqual(run(self.local_a, "rev-list", "--count", f"{before_return}..{after}"), "1")
        paths = run(self.local_a, "diff-tree", "--no-commit-id", "--name-only", "-r", after).splitlines()
        self.assertEqual(len(paths), 2)
        event = json.loads(next((self.local_a / path).read_text(encoding="utf-8") for path in paths if "/events/" in path))
        self.assertEqual(event["kind"], "ROOM_RETURN")

    def test_failure_can_sign_out_without_positive_evidence(self):
        entered = self.enter(self.board_a, "agent-a", [quest("q1", "W0")])
        before = self.board_a.git.head()
        result = self.board_a.room_return(
            agent_id="agent-a", expected_claim_id=entered["presence"]["claim_id"], expected_git_head=before,
            prompt_stack_digest=self.prompt_digest, room_contract_digest=self.contract_digest,
            result_status="FAILED", summary="API wall prevented the readback", failure_detail="provider denied the required endpoint",
        )
        self.assertEqual(result["status"], "ROOM_RETURNED")
        self.assertFalse(result["verified_return"])
        self.assertEqual(result["outcome"]["result_status"], "FAILED")
        self.assertTrue(result["signed_out"])

    def test_one_worker_is_not_reported_as_three_concurrent_waves(self):
        self.enter(self.board_a, "agent-a", [quest("q1", "W0"), quest("q2", "W1"), quest("q3", "W2")])
        pulse = self.board_a.room_pulse(quests=[quest("q1b", "W0"), quest("q2b", "W1"), quest("q3b", "W2")], shared_remote_mode="REQUIRED")
        self.assertEqual(pulse["observed_active_workers"], 1)
        self.assertEqual(sum(wave["workers"] for wave in pulse["waves"]), 1)
        self.assertEqual(pulse["observed_concurrency"], "UNKNOWN_UNLESS_SEPARATELY_ATTESTED")

    def test_ten_real_entries_converge_to_five_three_two_without_preemption(self):
        entered_claims = []
        for index in range(10):
            choices = [
                quest(f"agent-{index}-w0", "W0"),
                quest(f"agent-{index}-w1", "W1", family="NAVIGATION_ALGORITHMS"),
                quest(f"agent-{index}-w2", "W2", family="META_OBSERVATION"),
            ]
            result = self.enter(self.board_a, f"agent-{index}", choices)
            self.assertEqual(result["status"], "ROOM_ENTERED", result)
            entered_claims.append(result["presence"]["claim_id"])
        pulse = self.board_a.room_pulse(quests=[], shared_remote_mode="REQUIRED")
        counts = {wave["horizon"]: wave["workers"] for wave in pulse["waves"]}
        self.assertEqual(counts, {"W0": 5, "W1": 3, "W2": 2})
        active_claims = {row["claim_id"] for row in self.board_a.snapshot()["active"]}
        self.assertEqual(active_claims, set(entered_claims))

    def test_budget_and_horizon_policy_drift_hold_new_entry(self):
        first = self.enter(self.board_a, "agent-a", [quest("q1", "W0")])
        self.assertEqual(first["status"], "ROOM_ENTERED")
        changed_budget = resources(tokens=99999)
        budget_hold = self.enter(self.board_a, "agent-b", [quest("q2", "W1")], room_budget=changed_budget)
        self.assertEqual(budget_hold["status"], "NO_READY_QUESTS")
        self.assertIn("ROOM_BUDGET_POLICY_DRIFT_HOLD", budget_hold["held"][0]["reasons"])
        policy_hold = self.enter(
            self.board_a,
            "agent-c",
            [quest("q3", "W2")],
            horizon_weights={"W0": 200, "W1": 200, "W2": 600},
        )
        self.assertEqual(policy_hold["status"], "NO_READY_QUESTS")
        self.assertIn("HORIZON_POLICY_DRIFT_HOLD", policy_hold["held"][0]["reasons"])

    def test_peer_cannot_return_another_agents_claim_by_claim_mismatch(self):
        entered = self.enter(self.board_a, "agent-a", [quest("q1", "W0")])
        before = self.board_a.git.head()
        result = self.board_a.room_return(
            agent_id="agent-a", expected_claim_id="MBC-" + "0" * 32, expected_git_head=before,
            prompt_stack_digest=self.prompt_digest, room_contract_digest=self.contract_digest,
            result_status="FAILED", summary="attempted peer release", failure_detail="wrong owner",
        )
        self.assertEqual(result["status"], "ROOM_CLAIM_OWNERSHIP_HOLD")
        self.assertEqual(self.board_a.git.head(), before)
        self.assertEqual(entered["presence"]["agent_id"], "agent-a")

    def test_legacy_release_is_not_a_verified_room_return(self):
        entered = self.enter(self.board_a, "agent-a", [quest("q1", "W0")])
        released = self.board_a.release(agent_id="agent-a", release_status="DONE", outcome="caller prose only")
        self.assertEqual(released["status"], "RELEASED")
        events = self.board_a._events()
        self.assertFalse(any(event["kind"] == "ROOM_RETURN" for event in events))
        self.assertTrue(any(event["kind"] == "RELEASE" for event in events))
        self.assertTrue(entered["durable_return"])

    def test_expired_presence_is_excluded_from_room_census(self):
        now = datetime.now(timezone.utc)
        stale = {
            "artifact": "ATHENA.MESSAGE.BOARD.PRESENCE.V1",
            "agent_id": "stale-agent",
            "claim_id": "MBC-stale",
            "status": "ACTIVE",
            "expires_at": (now - timedelta(seconds=1)).isoformat(),
            "details": None,
        }
        self.board_a._presence_rows = lambda: [stale]
        snapshot = self.board_a.snapshot()
        pulse = compile_pulse(snapshot, [])
        self.assertEqual(pulse["observed_active_workers"], 0)

    def test_all_job_families_are_real_admissible_categories(self):
        self.assertEqual(len(JOB_FAMILIES), 9)
        for family in JOB_FAMILIES:
            candidate = quest(family.lower(), "W0", family=family)
            selected = select_quest(active_rows=[], quests=[candidate], capabilities=["code"], room_budget=resources(), protected_reserve=reserve())
            self.assertEqual(selected["status"], "QUEST_SELECTED", family)

    def test_real_prompt_runtime_is_compiled_and_bound_at_entry(self):
        prompt_root = self.local_a / "prompts"
        (prompt_root / "state").mkdir(parents=True)
        (prompt_root / "modules").mkdir(parents=True)
        (self.local_a / "policies").mkdir(parents=True)
        manifest = {
            "artifact": "ATHENA.PROMPT.RUNTIME.V1",
            "default_profile": "MAXDEV",
            "active_state": "prompts/state/ACTIVE.json",
            "policy": "policies/PROMPT_RUNTIME.md",
            "profiles": {"MAXDEV": ["core"]},
            "modules": {
                "core": {
                    "path": "prompts/modules/CORE.md",
                    "order": 10,
                    "mandatory": True,
                    "selectors": [],
                    "depends_on": [],
                }
            },
            "authority_ceiling": "NO_HIGHER_AUTHORITY",
        }
        active = {
            "status": "ACTIVE",
            "revision": 1,
            "profile": "MAXDEV",
            "enabled_modules": ["core"],
            "active_scoped_overlays": [],
        }
        (prompt_root / "PROMPT.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (prompt_root / "state/ACTIVE.json").write_text(json.dumps(active), encoding="utf-8")
        (prompt_root / "modules/CORE.md").write_text("Enter, claim coherent work, return evidence, and sign out.\n", encoding="utf-8")
        (self.local_a / "policies/PROMPT_RUNTIME.md").write_text("Source and authority remain distinct.\n", encoding="utf-8")
        run(self.local_a, "add", "prompts", "policies/PROMPT_RUNTIME.md")
        run(self.local_a, "commit", "-m", "install prompt fixture")
        run(self.local_a, "push", "origin", "master")
        board = MessageBoardRuntime(GitBackend(self.local_a))
        compiled = PromptRuntime(board.git).compile(task="execute coherent quest q1", profile="MAXDEV", include_text=False)
        result = board.room_enter(
            agent_id="agent-real-prompt",
            expected_git_head=board.git.head(),
            prompt_stack_digest=compiled["prompt_stack_digest"],
            room_contract_digest=self.contract_digest,
            capabilities=["code"],
            quests=[quest("q1", "W0")],
            room_budget=resources(),
            protected_reserve=reserve(),
        )
        self.assertEqual(result["status"], "ROOM_ENTERED", result)
        self.assertEqual(result["room_profile"]["prompt_stack_digest"], compiled["prompt_stack_digest"])
        self.assertEqual(result["room_profile"]["selected_modules"], ["core"])


if __name__ == "__main__":
    unittest.main()
