from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime, PREP_KINDS, VERSION
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_loop import _sha


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _runtime(base: Path):
    root = base / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")
    manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core"]},
        "modules": {"core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}},
    }
    active = {"artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1", "status": "ACTIVE", "profile": "MAXDEV", "enabled_modules": ["core"], "active_scoped_overlays": [], "revision": 1}
    _write(root, "prompts/PROMPT.manifest.json", json.dumps(manifest))
    _write(root, "prompts/state/ACTIVE.json", json.dumps(active))
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed")
    git = GitBackend(root)
    prompt = PromptRuntime(git)
    pipeline = RollingQuestPipelineRuntime(git, prompt)
    breadth = NextQuestBreadthRuntime(pipeline)
    return pipeline, breadth, root


def _baton(task="Quest four"):
    selected = {"candidate_id": "SC-4", "task": task, "routing_score": 1.0, "metrics": {}, "source": "EXPLICIT_CANDIDATE"}
    value = {"artifact": "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1", "status": "SELECTED", "selected": selected, "ties": [], "candidates": [selected]}
    value["baton_digest"] = _sha(value)
    return value


class NextQuestPipelineBreadthTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.pipeline, self.breadth, self.root = _runtime(Path(td.name))
        self.started = self.pipeline.start(
            goal="Long campaign",
            quests=["Quest one", "Quest two", "Quest three"],
            expected_git_head=self.pipeline.git.head(),
        )

    def test_plan_targets_only_q2_q3(self):
        planned = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=self.started["checkpoint_head"],
            kinds=["DEPENDENCY_MAP", "TEST_DESIGN"],
        )
        self.assertEqual(planned["status"], "PLANNED")
        self.assertEqual(planned["plan_count"], 4)
        self.assertEqual({p["quest"]["task"] for p in planned["plans"]}, {"Quest two", "Quest three"})
        self.assertNotIn("Quest one", {p["quest"]["task"] for p in planned["plans"]})
        self.assertTrue(all(p["authority"] == "PREPARATION_ONLY" for p in planned["plans"]))

    def test_record_is_context_only_and_cannot_complete_staged_quest(self):
        planned = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=self.started["checkpoint_head"],
            kinds=["RISK_SCAN"],
        )
        plan = next(p for p in planned["plans"] if p["quest"]["task"] == "Quest two")
        recorded = self.breadth.record(
            pipeline_id=self.started["pipeline_id"],
            plan_id=plan["plan_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=planned["checkpoint_head"],
            result={"observed": True, "status": "OBSERVED", "summary": "found two risks", "findings": ["risk-a", "risk-b"], "evidence_refs": ["git://risk-note"]},
        )
        packet = recorded["result"]
        self.assertFalse(packet["quest_completion"])
        self.assertFalse(packet["focus_mutation"])
        self.assertFalse(packet["promotion_authority"])
        state = self.pipeline.state(self.started["pipeline_id"])
        self.assertEqual(state["window"]["focus"]["task"], "Quest one")

    def test_prep_survives_rotation_and_becomes_focus_context(self):
        planned = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=self.started["checkpoint_head"],
            kinds=["DEPENDENCY_MAP"],
        )
        q2_plan = next(p for p in planned["plans"] if p["quest"]["task"] == "Quest two")
        recorded = self.breadth.record(
            pipeline_id=self.started["pipeline_id"],
            plan_id=q2_plan["plan_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=planned["checkpoint_head"],
            result={"observed": True, "status": "OBSERVED", "summary": "dependency map prepared", "findings": ["needs schema X"]},
        )
        current = self.pipeline.state(self.started["pipeline_id"])
        rotated = self.pipeline.rotate(
            pipeline_id=self.started["pipeline_id"],
            expected_state_digest=current["state_digest"],
            expected_checkpoint_head=current["checkpoint_head"],
            completed_quest_id=current["window"]["focus"]["quest_id"],
            completion={"observed": True, "status": "SUCCEEDED", "summary": "q1 done", "evidence_refs": ["git://q1"]},
            successor_baton=_baton(),
        )
        self.assertEqual(rotated["window"]["focus"]["task"], "Quest two")
        context = self.breadth.context(pipeline_id=self.started["pipeline_id"])
        self.assertEqual(context["status"], "AVAILABLE")
        self.assertTrue(context["is_current_focus"])
        self.assertEqual(context["observations"][0]["summary"], "dependency map prepared")

    def test_stale_pipeline_state_blocks_prep_record(self):
        planned = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=self.started["checkpoint_head"],
            kinds=["TEST_DESIGN"],
        )
        plan = planned["plans"][0]
        state = self.pipeline.state(self.started["pipeline_id"])
        rotated = self.pipeline.rotate(
            pipeline_id=self.started["pipeline_id"],
            expected_state_digest=state["state_digest"],
            expected_checkpoint_head=state["checkpoint_head"],
            completed_quest_id=state["window"]["focus"]["quest_id"],
            completion={"observed": True, "status": "SUCCEEDED", "summary": "done"},
            successor_baton=_baton(),
        )
        with self.assertRaisesRegex(Exception, "STALE_PIPELINE_STATE"):
            self.breadth.record(
                pipeline_id=self.started["pipeline_id"],
                plan_id=plan["plan_id"],
                expected_pipeline_state_digest=self.started["state_digest"],
                expected_git_head=rotated["checkpoint_head"],
                result={"observed": True, "status": "OBSERVED", "summary": "late result"},
            )

    def test_verify_preserves_authority_boundary(self):
        planned = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=self.started["checkpoint_head"],
            kinds=["SOURCE_REVIEW"],
        )
        plan = planned["plans"][0]
        self.breadth.record(
            pipeline_id=self.started["pipeline_id"],
            plan_id=plan["plan_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=planned["checkpoint_head"],
            result={"observed": True, "status": "OBSERVED", "summary": "sources mapped"},
        )
        verified = self.breadth.verify(self.started["pipeline_id"])
        self.assertEqual(verified["status"], "PASS", verified)
        self.assertEqual(verified["authority"], "NONE")

    def test_all_prep_kinds_are_bounded(self):
        self.assertEqual(set(PREP_KINDS), {"DEPENDENCY_MAP", "RETRIEVAL_PLAN", "TEST_DESIGN", "RISK_SCAN", "SOURCE_REVIEW", "INTERFACE_MAP"})
        self.assertEqual(VERSION, "ATHENA.NEXT.QUEST.PIPELINE.BREADTH.2")


if __name__ == "__main__":
    unittest.main()
