from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime
from athena_mcp.next_scout_economy import NextScoutEconomyRuntime, RESOURCE_PROFILE, VERSION
from athena_mcp.prompt_runtime import PromptRuntime


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, value) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value), encoding="utf-8")


class _Board:
    def __init__(self):
        self.active = []

    def read(self, **kwargs):
        return {"status": "OK", "active": list(self.active), "shared_frontier_verified": True}


def _brain(base: Path, kinds=None):
    root = base / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")
    _write(root, "prompts/PROMPT.manifest.json", {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1", "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json", "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV", "profiles": {"MAXDEV": ["core"]},
        "modules": {"core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}},
    })
    _write(root, "prompts/state/ACTIVE.json", {"artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1", "status": "ACTIVE", "profile": "MAXDEV", "enabled_modules": ["core"], "active_scoped_overlays": [], "revision": 1})
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed")
    git = GitBackend(root)
    prompt = PromptRuntime(git)
    pipeline = RollingQuestPipelineRuntime(git, prompt)
    breadth = NextQuestBreadthRuntime(pipeline)
    board = _Board()
    economy = NextScoutEconomyRuntime(pipeline, breadth, board)
    start = pipeline.start(goal="g", quests=["Q1", "Q2", "Q3"], expected_git_head=git.head())
    planned = breadth.plan(
        pipeline_id=start["pipeline_id"], expected_pipeline_state_digest=start["state_digest"],
        expected_git_head=git.head(), kinds=kinds or ["DEPENDENCY_MAP", "RISK_SCAN", "SOURCE_REVIEW"],
    )
    return root, git, pipeline, breadth, board, economy, start, planned


class NextScoutEconomyTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root, self.git, self.pipeline, self.breadth, self.board, self.economy, self.start, self.planned = _brain(Path(self.td.name))

    def _allocate(self, **updates):
        args = dict(
            pipeline_id=self.start["pipeline_id"], expected_pipeline_state_digest=self.start["state_digest"],
            shared_remote_mode="DISABLED",
        )
        args.update(updates)
        return self.economy.economy(**args)

    def test_resource_profiles_are_explicit_planning_estimates(self):
        result = self._allocate()
        self.assertEqual(result["artifact"], VERSION)
        self.assertEqual(result["cost_standing"], "PLANNING_ESTIMATES_NOT_OBSERVED_CONSUMPTION")
        self.assertEqual(result["resource_profiles"], RESOURCE_PROFILE)
        self.assertEqual(result["authority"], "ROUTING_ONLY")
        self.assertEqual(result["claim_effect"], "NONE")

    def test_reserve_vector_can_make_only_low_cost_risk_scan_feasible(self):
        result = self._allocate(
            max_scouts=1, reserve_slots=0,
            token_budget=7000, reserve_tokens=4000,
            minute_budget=20, reserve_minutes=5,
            tool_call_budget=5, reserve_tool_calls=1,
            coordination_budget=4, reserve_coordination=1,
            git_risk_budget=3, reserve_git_risk=1,
        )
        self.assertEqual(result["status"], "SELECTED")
        self.assertEqual(len(result["selected_plan_ids"]), 1)
        selected = result["selected"][0]
        self.assertEqual(selected["kind"], "RISK_SCAN")
        self.assertEqual(selected["quest"]["task"], "Q2")
        self.assertLessEqual(result["selected_profile"]["tokens"], result["available_after_active"]["tokens"])

    def test_active_scout_consumes_slot_and_resource_budget_first(self):
        dep = next(p for p in self.planned["plans"] if p["kind"] == "DEPENDENCY_MAP" and p["quest"]["task"] == "Q2")
        self.board.active = [{"agent_id": "scout-a", "work_key": f"next-prep:{self.start['pipeline_id']}:{dep['plan_id']}"}]
        result = self._allocate(max_scouts=2, reserve_slots=0, token_budget=7000, reserve_tokens=0)
        self.assertEqual(result["active_plan_ids"], [dep["plan_id"]])
        self.assertEqual(result["active_profile"]["tokens"], RESOURCE_PROFILE["DEPENDENCY_MAP"]["tokens"])
        self.assertEqual(result["new_slots"], 1)
        self.assertLessEqual(result["selected_profile"]["tokens"], 7000 - RESOURCE_PROFILE["DEPENDENCY_MAP"]["tokens"])

    def test_unknown_active_scout_cost_fails_closed(self):
        self.board.active = [{"agent_id": "scout-z", "work_key": f"next-prep:{self.start['pipeline_id']}:missing-plan"}]
        result = self._allocate()
        self.assertEqual(result["status"], "UNKNOWN_ACTIVE_SCOUT_COST_HOLD")
        self.assertEqual(result["unknown_active_plan_ids"], ["missing-plan"])

    def test_budget_can_legitimately_select_no_new_work(self):
        result = self._allocate(
            max_scouts=1, reserve_slots=0,
            token_budget=1000, reserve_tokens=0,
            minute_budget=5, reserve_minutes=0,
            tool_call_budget=1, reserve_tool_calls=0,
            coordination_budget=1, reserve_coordination=0,
            git_risk_budget=1, reserve_git_risk=0,
        )
        self.assertEqual(result["selected_plan_ids"], [])
        self.assertEqual(result["selected_profile"]["tokens"], 0)

    def test_economy_is_read_only_and_deterministic(self):
        before = self.git.head()
        a = self._allocate()
        middle = self.git.head()
        b = self._allocate()
        after = self.git.head()
        self.assertEqual((before, middle, after), (before, before, before))
        self.assertEqual(a["allocation_digest"], b["allocation_digest"])
        self.assertEqual(a["selected_plan_ids"], b["selected_plan_ids"])

    def test_version(self):
        self.assertEqual(VERSION, "ATHENA.NEXT.SCOUT.ECONOMY.5")


if __name__ == "__main__":
    unittest.main()
