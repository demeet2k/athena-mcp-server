from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.next_quest_pipeline import RollingQuestPipelineRuntime
from athena_mcp.next_quest_pipeline_bridge import NextPipelineFocusBridge
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime


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


def _brain(base: Path):
    root = base / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")
    _write(root, "prompts/PROMPT.manifest.json", {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core"]},
        "modules": {"core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}},
    })
    _write(root, "prompts/state/ACTIVE.json", {"artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1", "status": "ACTIVE", "profile": "MAXDEV", "enabled_modules": ["core"], "active_scoped_overlays": [], "revision": 1})
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed")
    git = GitBackend(root)
    prompt = PromptRuntime(git)
    loop = RehydrationLoopRuntime(git, prompt)
    pipeline = RollingQuestPipelineRuntime(git, prompt)
    prompt._rehydration_loop_runtime_v1 = loop
    prompt._next_pipeline_runtime_v1 = pipeline
    return root, git, prompt, loop, pipeline


def _completion():
    return {
        "status": "SUCCEEDED",
        "observed": True,
        "terminal": False,
        "summary": "Q1 implementation complete",
        "progress_delta": 1.0,
        "passes": [
            {"kind": "reconstruct", "summary": "reconstructed"},
            {"kind": "execute", "summary": "executed"},
            {"kind": "verify", "summary": "verified"},
        ],
        "tests": [{"name": "unit", "status": "PASS"}],
        "evidence_refs": ["git://feature.txt"],
        "residuals": [{"task": "Quest four", "source_ref": "residual:q4"}],
    }


class NextPipelineFocusBridgeTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root, self.git, self.prompt, self.loop, self.pipeline = _brain(Path(self.td.name))
        self.loop_start = self.loop.start(
            goal="Long campaign", task="Quest one", expected_git_head=self.git.head(),
            depth_mode="standard", shared_remote_mode="DISABLED", use_frontier=False,
        )
        self.pipeline_start = self.pipeline.start(
            goal="Long campaign", quests=["Quest one", "Quest two", "Quest three"], expected_git_head=self.git.head()
        )
        self.bridge = NextPipelineFocusBridge(self.prompt)

    def test_composite_advance_keeps_q2_focus_and_uses_q4_as_reseed(self):
        _write(self.root, "feature.txt", "implemented\n")
        _run(self.root, "add", ".")
        _run(self.root, "commit", "-m", "implement Q1")
        focus = self.pipeline_start["window"]["focus"]
        result = self.bridge.advance_focus({
            "pipeline_id": self.pipeline_start["pipeline_id"],
            "pipeline_state_digest": self.pipeline_start["state_digest"],
            "pipeline_checkpoint_head": self.pipeline_start["checkpoint_head"],
            "loop_id": self.loop_start["loop_id"],
            "loop_state_digest": self.loop_start["state_digest"],
            "loop_prompt_digest": self.loop_start["prompt_digest"],
            "loop_checkpoint_head": self.loop_start["checkpoint_head"],
            "completed_quest_id": focus["quest_id"],
            "completion": _completion(),
            "shared_remote_mode": "DISABLED",
        })
        self.assertEqual(result["new_focus"]["task"], "Quest two")
        self.assertEqual(result["reseed_baton"]["selected"]["task"], "Quest four")
        self.assertEqual([q["task"] for q in result["pipeline"]["window"]["execution_order"]], ["Quest two", "Quest three", "Quest four"])
        resumed = self.loop.resume(self.loop_start["loop_id"], shared_remote_mode="DISABLED")
        self.assertEqual(resumed["task"], "Quest two")
        self.assertIn("feature.txt", result["material_work_paths"])

    def test_bookkeeping_only_change_is_not_substantive_progress(self):
        focus = self.pipeline_start["window"]["focus"]
        with self.assertRaisesRegex(ValueError, "substantive work"):
            self.bridge.advance_focus({
                "pipeline_id": self.pipeline_start["pipeline_id"],
                "pipeline_state_digest": self.pipeline_start["state_digest"],
                "pipeline_checkpoint_head": self.pipeline_start["checkpoint_head"],
                "loop_id": self.loop_start["loop_id"],
                "loop_state_digest": self.loop_start["state_digest"],
                "loop_prompt_digest": self.loop_start["prompt_digest"],
                "loop_checkpoint_head": self.loop_start["checkpoint_head"],
                "completed_quest_id": focus["quest_id"],
                "completion": _completion(),
                "shared_remote_mode": "DISABLED",
            })

    def test_loop_focus_must_equal_pipeline_focus(self):
        state_path = self.root / "prompts" / "rehydration" / self.loop_start["loop_id"] / "state.json"
        state = json.loads(state_path.read_text())
        # The bridge checks semantic focus equality before any mutation. We change
        # the frozen test packet in-memory by directly exercising that mismatch via
        # a distinct pipeline task rather than trying to mint a valid state digest.
        pipeline_state, _ = self.pipeline._read_state(self.pipeline_start["pipeline_id"])
        pipeline_state["queue"][0]["task"] = "Different focus"
        pipeline_state["queue"][0]["task_key"] = "different focus"
        pipeline_state["state_digest"] = __import__("athena_mcp.next_quest_pipeline", fromlist=["_state_digest"])._state_digest(pipeline_state)
        pipeline_file = self.root / "prompts" / "next_quest_pipelines" / self.pipeline_start["pipeline_id"] / "state.json"
        pipeline_file.write_text(json.dumps(pipeline_state), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "disagree"):
            self.bridge.advance_focus({
                "pipeline_id": self.pipeline_start["pipeline_id"],
                "pipeline_state_digest": pipeline_state["state_digest"],
                "pipeline_checkpoint_head": self.pipeline_start["checkpoint_head"],
                "loop_id": self.loop_start["loop_id"],
                "loop_state_digest": self.loop_start["state_digest"],
                "loop_prompt_digest": self.loop_start["prompt_digest"],
                "loop_checkpoint_head": self.loop_start["checkpoint_head"],
                "completed_quest_id": pipeline_state["queue"][0]["quest_id"],
                "completion": _completion(),
                "shared_remote_mode": "DISABLED",
            })


if __name__ == "__main__":
    unittest.main()
