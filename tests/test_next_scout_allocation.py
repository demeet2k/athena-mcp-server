from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime
from athena_mcp.next_scout_allocation import NextScoutAllocationRuntime, VERSION, _work_key
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


class ScoutAllocationTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root = Path(td.name) / "brain"
        self.root.mkdir()
        _run(self.root, "init")
        _run(self.root, "config", "user.name", "test")
        _run(self.root, "config", "user.email", "test@example.invalid")
        _write(self.root, "prompts/PROMPT.manifest.json", {
            "artifact": "ATHENA.PROMPT.RUNTIME.V1", "authority_ceiling": "below external authority",
            "active_state": "prompts/state/ACTIVE.json", "policy": "policies/PROMPT_RUNTIME.md",
            "default_profile": "MAXDEV", "profiles": {"MAXDEV": ["core"]},
            "modules": {"core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}},
        })
        _write(self.root, "prompts/state/ACTIVE.json", {"artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1", "status": "ACTIVE", "profile": "MAXDEV", "enabled_modules": ["core"], "active_scoped_overlays": [], "revision": 1})
        _write(self.root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
        _write(self.root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
        _run(self.root, "add", ".")
        _run(self.root, "commit", "-m", "seed")
        self.git = GitBackend(self.root)
        self.prompt = PromptRuntime(self.git)
        self.pipeline = RollingQuestPipelineRuntime(self.git, self.prompt)
        self.breadth = NextQuestBreadthRuntime(self.pipeline)
        self.board = _Board()
        self.runtime = NextScoutAllocationRuntime(self.pipeline, self.breadth, self.board)
        self.start = self.pipeline.start(goal="g", quests=["Q1", "Q2", "Q3"], expected_git_head=self.git.head())
        self.planned = self.breadth.plan(
            pipeline_id=self.start["pipeline_id"],
            expected_pipeline_state_digest=self.start["state_digest"],
            expected_git_head=self.git.head(),
        )

    def alloc(self, **kwargs):
        return self.runtime.allocate(
            pipeline_id=self.start["pipeline_id"],
            expected_pipeline_state_digest=self.start["state_digest"],
            shared_remote_mode="DISABLED",
            **kwargs,
        )

    def test_version_and_read_only_capacity(self):
        before = self.git.head()
        out = self.alloc(max_scouts=4, reserve_slots=1)
        self.assertEqual(VERSION, "ATHENA.NEXT.SCOUT.ALLOCATION.4")
        self.assertEqual(out["usable_capacity"], 3)
        self.assertEqual(len(out["selected_plan_ids"] or []), 3)
        self.assertEqual(self.git.head(), before)
        self.assertEqual(out["claim_effect"], "NONE")

    def test_reserve_capacity_is_not_allocated(self):
        out = self.alloc(max_scouts=2, reserve_slots=1)
        self.assertEqual(out["usable_capacity"], 1)
        self.assertEqual(len(out["selected_plan_ids"] or []), 1)

    def test_active_claim_consumes_capacity_and_is_excluded(self):
        active_plan = self.planned["plans"][0]
        self.board.active.append({
            "agent_id": "scout-a", "status": "ACTIVE",
            "work_key": _work_key(self.start["pipeline_id"], active_plan["plan_id"]),
        })
        out = self.alloc(max_scouts=4, reserve_slots=1)
        self.assertIn(active_plan["plan_id"], out["active_plan_ids"])
        self.assertEqual(out["available_new_slots"], 2)
        self.assertNotIn(active_plan["plan_id"], out["selected_plan_ids"] or [])

    def test_observed_plan_is_excluded(self):
        plan = self.planned["plans"][0]
        self.breadth.record(
            pipeline_id=self.start["pipeline_id"], plan_id=plan["plan_id"],
            expected_pipeline_state_digest=self.start["state_digest"], expected_git_head=self.git.head(),
            result={"observed": True, "status": "OBSERVED", "summary": "done"},
        )
        out = self.alloc(max_scouts=4, reserve_slots=1)
        reasons = {row["plan_id"]: row["reason"] for row in out["excluded"]}
        self.assertEqual(reasons[plan["plan_id"]], "ALREADY_OBSERVED")

    def test_allocator_covers_both_staged_quests_when_capacity_allows(self):
        out = self.alloc(max_scouts=4, reserve_slots=1)
        quest_ids = {row["quest"]["quest_id"] for row in out["selected"]}
        self.assertEqual(len(quest_ids), 2)

    def test_stale_pipeline_digest_fails(self):
        with self.assertRaisesRegex(ValueError, "STALE_PIPELINE_STATE"):
            self.runtime.allocate(
                pipeline_id=self.start["pipeline_id"], expected_pipeline_state_digest="0" * 64,
                shared_remote_mode="DISABLED",
            )


if __name__ == "__main__":
    unittest.main()
