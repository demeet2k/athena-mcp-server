from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime
from athena_mcp.next_quest_pipeline_breadth_hardening import install_next_pipeline_breadth_idempotency_hardening
from athena_mcp.prompt_runtime import PromptRuntime


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_runtime(base: Path):
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
    install_next_pipeline_breadth_idempotency_hardening()
    return pipeline, breadth, root


class BreadthIdempotencyTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.pipeline, self.breadth, self.root = _make_runtime(Path(td.name))
        self.started = self.pipeline.start(
            goal="Long campaign",
            quests=["Quest one", "Quest two", "Quest three"],
            expected_git_head=self.pipeline.git.head(),
        )

    def test_exact_repeat_reuses_without_git_mutation(self):
        first = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=self.started["checkpoint_head"],
            kinds=["DEPENDENCY_MAP", "TEST_DESIGN"],
        )
        head = self.pipeline.git.head()
        second = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=head,
            kinds=["DEPENDENCY_MAP", "TEST_DESIGN"],
        )
        self.assertEqual(second["status"], "REUSED")
        self.assertFalse(second["git_mutation"])
        self.assertEqual(self.pipeline.git.head(), head)
        self.assertEqual([p["plan_id"] for p in first["plans"]], [p["plan_id"] for p in second["plans"]])
        self.assertEqual([p["packet_digest"] for p in first["plans"]], [p["packet_digest"] for p in second["plans"]])

    def test_reuse_requires_current_git_head(self):
        first = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=self.started["checkpoint_head"],
            kinds=["RISK_SCAN"],
        )
        with self.assertRaisesRegex(ValueError, "STALE_GIT_HEAD_FOR_BREADTH_REUSE"):
            self.breadth.plan(
                pipeline_id=self.started["pipeline_id"],
                expected_pipeline_state_digest=self.started["state_digest"],
                expected_git_head=self.started["checkpoint_head"],
                kinds=["RISK_SCAN"],
            )
        self.assertEqual(self.pipeline.git.head(), first["checkpoint_head"])

    def test_observed_annotation_does_not_change_planned_identity(self):
        first = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=self.started["checkpoint_head"],
            kinds=["SOURCE_REVIEW"],
        )
        plan = first["plans"][0]
        recorded = self.breadth.record(
            pipeline_id=self.started["pipeline_id"],
            plan_id=plan["plan_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=first["checkpoint_head"],
            result={"observed": True, "status": "OBSERVED", "summary": "source review done"},
        )
        reused = self.breadth.plan(
            pipeline_id=self.started["pipeline_id"],
            expected_pipeline_state_digest=self.started["state_digest"],
            expected_git_head=recorded["checkpoint_head"],
            kinds=["SOURCE_REVIEW"],
        )
        self.assertEqual(reused["status"], "REUSED")
        row = next(p for p in reused["plans"] if p["plan_id"] == plan["plan_id"])
        self.assertEqual(row["packet_digest"], plan["packet_digest"])
        self.assertEqual(row["status"], "OBSERVED")
        self.assertEqual(row["result_digest"], recorded["result"]["packet_digest"])


if __name__ == "__main__":
    unittest.main()
