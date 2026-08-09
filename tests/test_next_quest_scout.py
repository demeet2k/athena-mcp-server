from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_breadth import NextQuestBreadthRuntime
from athena_mcp.next_quest_scout import NextQuestScoutRuntime, VERSION, _target_path, _work_key
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


class _Remote:
    def __init__(self):
        self.publish_ok = True
        self.published = []

    def publish(self, head, remote="origin"):
        self.published.append((head, remote))
        return {"status": "PUBLISHED_SHARED" if self.publish_ok else "PUBLISH_HOLD", "shared_frontier_verified": self.publish_ok, "published_head": head}


class _Board:
    def __init__(self):
        self.active = {}
        self.remote_sync = _Remote()
        self.release_calls = []

    def present(self, *, agent_id, task, work_key=None, targets=None, details=None, mode="PRIMARY", replication_reason=None, lease_seconds=1800, remote="origin"):
        for row in self.active.values():
            if row.get("work_key") == work_key and row.get("agent_id") != agent_id:
                return {"status": "DUPLICATE_WORK_HOLD", "conflicts": [row]}
        existing = self.active.get(agent_id)
        if existing:
            return {"status": "ALREADY_PRESENT" if existing.get("work_key") == work_key else "AGENT_ALREADY_PRESENT_HOLD", "presence": existing}
        row = {"agent_id": agent_id, "claim_id": f"claim-{agent_id}", "status": "ACTIVE", "mode": mode, "task": task, "work_key": work_key, "targets": list(targets or []), "details": details}
        self.active[agent_id] = row
        return {"status": "PRESENT", "presence": row, "durable_return": True}

    def read(self, *, agent_id=None, limit=50, include_stale=False, remote="origin", shared_remote_mode="REQUIRED"):
        return {"status": "OK", "active": list(self.active.values()), "shared_frontier_verified": True}

    def release(self, *, agent_id, release_status="DONE", outcome=None, handoff_to=None, remote="origin"):
        self.release_calls.append((agent_id, release_status, outcome))
        row = self.active.pop(agent_id, None)
        return {"status": "RELEASED" if row else "NOT_PRESENT", "presence": row}


def _brain(base: Path):
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
    scout = NextQuestScoutRuntime(pipeline, breadth, board)
    start = pipeline.start(goal="g", quests=["Q1", "Q2", "Q3"], expected_git_head=git.head())
    planned = breadth.plan(
        pipeline_id=start["pipeline_id"], expected_pipeline_state_digest=start["state_digest"], expected_git_head=git.head(),
        kinds=["DEPENDENCY_MAP", "TEST_DESIGN"],
    )
    return root, git, pipeline, breadth, board, scout, start, planned


class NextQuestScoutTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root, self.git, self.pipeline, self.breadth, self.board, self.scout, self.start, self.planned = _brain(Path(self.td.name))
        self.plan = self.planned["plans"][0]

    def test_claim_is_exact_prep_plan_not_parent_quest(self):
        result = self.scout.claim(
            pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"], agent_id="scout-a"
        )
        self.assertEqual(result["status"], "SCOUT_CLAIMED")
        self.assertEqual(result["work_key"], _work_key(self.start["pipeline_id"], self.plan["plan_id"]))
        self.assertEqual(result["allowed_target"], _target_path(self.start["pipeline_id"], self.plan["plan_id"]))
        self.assertEqual(result["authority"], "PREPARATION_ONLY")
        self.assertNotEqual(result["work_key"], self.plan["quest"]["task"])

    def test_duplicate_scout_for_same_plan_holds(self):
        first = self.scout.claim(pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"], agent_id="scout-a")
        second = self.scout.claim(pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"], agent_id="scout-b")
        self.assertEqual(first["status"], "SCOUT_CLAIMED")
        self.assertEqual(second["status"], "SCOUT_CLAIM_HOLD")

    def test_return_requires_active_exact_claim(self):
        result = self.scout.return_result(
            pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"],
            expected_git_head=self.git.head(), agent_id="scout-a", result={"summary": "mapped deps"}
        )
        self.assertEqual(result["status"], "SCOUT_CLAIM_REQUIRED_HOLD")

    def test_successful_return_publishes_before_release_and_never_completes_quest(self):
        self.scout.claim(pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"], agent_id="scout-a")
        current = self.git.head()
        result = self.scout.return_result(
            pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"],
            expected_git_head=current, agent_id="scout-a", result={"summary": "mapped deps", "findings": ["dep-a"], "evidence_refs": ["git://dep-a"]}
        )
        self.assertEqual(result["status"], "SCOUT_RETURNED")
        self.assertTrue(self.board.remote_sync.published)
        self.assertTrue(self.board.release_calls)
        self.assertFalse(result["quest_completion"])
        self.assertFalse(result["focus_mutation"])
        self.assertFalse(result["promotion_authority"])
        ctx = self.breadth.context(pipeline_id=self.start["pipeline_id"], quest_id=self.plan["quest"]["quest_id"])
        self.assertEqual(ctx["status"], "AVAILABLE")
        self.assertEqual(ctx["observations"][0]["summary"], "mapped deps")
        state = self.pipeline.state(self.start["pipeline_id"])
        self.assertEqual(state["window"]["focus"]["task"], "Q1")

    def test_publish_failure_preserves_claim_for_recovery(self):
        self.scout.claim(pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"], agent_id="scout-a")
        self.board.remote_sync.publish_ok = False
        result = self.scout.return_result(
            pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"],
            expected_git_head=self.git.head(), agent_id="scout-a", result={"summary": "mapped deps"}
        )
        self.assertEqual(result["status"], "SCOUT_RESULT_LOCAL_PUBLISH_HOLD")
        self.assertTrue(result["claim_preserved"])
        self.assertIn("scout-a", self.board.active)
        self.assertEqual(self.board.release_calls, [])

    def test_late_return_after_rotation_fails_state_binding(self):
        self.scout.claim(pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"], agent_id="scout-a")
        state, paths = self.pipeline._read_state(self.start["pipeline_id"])
        state["state_digest"] = "0" * 64
        (self.root / paths["state"]).write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaisesRegex(Exception, "STALE|TAMPERED"):
            self.scout.return_result(
                pipeline_id=self.start["pipeline_id"], plan_id=self.plan["plan_id"], expected_pipeline_state_digest=self.start["state_digest"],
                expected_git_head=self.git.head(), agent_id="scout-a", result={"summary": "late"}
            )

    def test_version(self):
        self.assertEqual(VERSION, "ATHENA.NEXT.SCOUT.EXECUTION.3")


if __name__ == "__main__":
    unittest.main()
