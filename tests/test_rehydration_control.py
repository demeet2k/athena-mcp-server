from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_control import CONTROL_TOOL_NAMES, RehydrationControlRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def _write(root: Path, rel: str, value) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        p.write_text(value, encoding="utf-8")
    else:
        p.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class _Frontier:
    def select(self, **kwargs):
        return {
            "status": "SELECTED", "source_head": "source-head", "frontier_digest": "frontier-digest",
            "selected": {"run_id": "run.alpha", "node_id": "frontier-build"}, "pareto_front": [],
            "frontier": {"residuals": [{"summary": "frontier residual"}], "source_coverage": {}},
        }


class _Remote:
    def sync(self, remote="origin"):
        return {"status": "UP_TO_DATE", "shared_frontier_verified": True, "remote": remote}

    def publish(self, expected_git_head, remote="origin"):
        return {"status": "PUBLISHED_SHARED", "shared_frontier_verified": True, "remote": remote, "published_head": expected_git_head}


class _Board:
    def __init__(self):
        self.row = None
        self.release_calls = []

    @staticmethod
    def _lease_state(row):
        return "ACTIVE" if row and row.get("status") == "ACTIVE" else "RELEASED"

    def present(self, *, agent_id, task, work_key, targets, details, mode, lease_seconds, remote):
        if self.row and self.row.get("status") == "ACTIVE" and self.row.get("work_key") == work_key and self.row.get("agent_id") != agent_id:
            return {"status": "DUPLICATE_WORK_HOLD", "presence": self.row}
        self.row = {"agent_id": agent_id, "claim_id": "MBC-test", "status": "ACTIVE", "mode": "PRIMARY", "task": task, "work_key": work_key, "targets": targets}
        return {"status": "PRESENT", "presence": dict(self.row), "durable_return": True}

    def read(self, *, agent_id=None, include_stale=False, remote="origin", shared_remote_mode="REQUIRED"):
        active = [dict(self.row)] if self.row and self.row.get("status") == "ACTIVE" else []
        self_row = dict(self.row) if self.row and self.row.get("agent_id") == agent_id else None
        return {"status": "OK", "active": active, "self": self_row, "unread_messages": [], "shared_frontier_verified": True}

    def release(self, *, agent_id, release_status, outcome, handoff_to, remote):
        self.release_calls.append((agent_id, release_status, handoff_to))
        if self.row and self.row.get("agent_id") == agent_id:
            self.row = {**self.row, "status": "RELEASED", "handoff_to": handoff_to}
        return {"status": "RELEASED", "handoff": handoff_to, "durable_return": True}


def _runtime(base: Path):
    root = base / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")
    _write(root, "prompts/PROMPT.manifest.json", {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1", "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json", "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "BUILD", "profiles": {"BUILD": ["core"]},
        "modules": {"core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}},
    })
    _write(root, "prompts/state/ACTIVE.json", {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1", "status": "ACTIVE", "profile": "BUILD",
        "enabled_modules": ["core"], "active_scoped_overlays": [], "revision": 1,
    })
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed")
    git = GitBackend(root)
    prompt = PromptRuntime(git)
    base_runtime = RehydrationLoopRuntime(git, prompt, _Frontier(), _Remote())
    board = _Board()
    return RehydrationControlRuntime(base_runtime, board), base_runtime, board, root


def _passes():
    return [{"kind": k, "summary": f"{k} done", "evidence_refs": []} for k in (
        "reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize"
    )]


def _completion(**extra):
    value = {
        "status": "SUCCEEDED", "observed": True, "terminal": False, "hard_hold": False,
        "summary": "bounded change complete", "progress_delta": 1.0, "passes": _passes(),
        "tests": [{"name": "unit", "status": "PASS", "evidence_ref": "test://unit"}],
        "evidence_refs": ["git://feature.txt"], "residuals": ["Implement the next residual"],
        "next_task": None, "handoff_to": None,
    }
    value.update(extra)
    return value


class RehydrationControlTests(unittest.TestCase):
    def _case(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _runtime(Path(td.name))

    def _start(self, base):
        return base.start(
            goal="Develop the framework", task="Implement one slice", expected_git_head=base.git.head(),
            actor="agent_a", profile="BUILD", fetch=False, use_frontier=True,
            shared_remote_mode="DISABLED", depth_mode="deep", max_steps=8,
        )

    def test_claim_uses_message_board_as_only_claim_authority(self):
        control, base, board, _ = self._case()
        started = self._start(base)
        claimed = control.claim(loop_id=started["loop_id"], agent_id="agent_a")
        self.assertEqual(claimed["status"], "PRESENT")
        self.assertEqual(board.row["work_key"], f"rehydration:{started['loop_id']}")
        self.assertIn("MESSAGE_BOARD_IS_SOLE_CLAIM_AUTHORITY", claimed["laws"])

    def test_advance_without_claim_holds(self):
        control, base, _, _ = self._case()
        started = self._start(base)
        result = control.advance_claimed(
            loop_id=started["loop_id"], agent_id="agent_a",
            expected_checkpoint_head=started["checkpoint_head"], expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"], completion=_completion(),
            shared_remote_mode="DISABLED", allow_no_git_change=True,
        )
        self.assertEqual(result["status"], "REHYDRATION_CLAIM_REQUIRED_HOLD")

    def test_claimed_advance_delegates_successor_and_adds_cycle_gate(self):
        control, base, _, root = self._case()
        started = self._start(base)
        control.claim(loop_id=started["loop_id"], agent_id="agent_a")
        _write(root, "feature.txt", "feature\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "feature work")
        result = control.advance_claimed(
            loop_id=started["loop_id"], agent_id="agent_a",
            expected_checkpoint_head=started["checkpoint_head"], expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"], completion=_completion(), shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "ACTIVE")
        self.assertEqual(result["cycle_gate"]["state"], "VERIFIED_CYCLE")
        self.assertFalse(result["cycle_gate"]["promotion_qualified"])
        state = base._read_state(started["loop_id"])[0]
        last = state["last_completion"]
        self.assertEqual(last["_rehydration_control"]["claim_id"], "MBC-test")
        self.assertEqual(last["_rehydration_control"]["cycle_gate"]["state"], "VERIFIED_CYCLE")
        self.assertEqual(last["successor_baton"]["artifact"], "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1")
        self.assertEqual(last["next_task"], "Implement the next residual")
        self.assertIn("Implement the next residual", result["compiled_self_prompt"])
        self.assertEqual(base.verify(started["loop_id"], shared_remote_mode="DISABLED")["status"], "PASS")

    def test_explicit_next_task_preserves_existing_successor_compatibility(self):
        control, base, _, root = self._case()
        started = self._start(base)
        control.claim(loop_id=started["loop_id"], agent_id="agent_a")
        _write(root, "feature.txt", "feature\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "feature")
        result = control.advance_claimed(
            loop_id=started["loop_id"], agent_id="agent_a",
            expected_checkpoint_head=started["checkpoint_head"], expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"], completion=_completion(next_task="Run adversarial verification"),
            shared_remote_mode="DISABLED",
        )
        state = base._read_state(started["loop_id"])[0]
        self.assertEqual(state["last_completion"]["next_task"], "Run adversarial verification")
        self.assertNotIn("successor_baton", state["last_completion"])
        self.assertIn("Run adversarial verification", result["compiled_self_prompt"])

    def test_control_only_changes_never_count_as_substantive_work(self):
        control, base, _, _ = self._case()
        started = self._start(base)
        control.claim(loop_id=started["loop_id"], agent_id="agent_a")
        with self.assertRaisesRegex(ValueError, "substantive work"):
            control.advance_claimed(
                loop_id=started["loop_id"], agent_id="agent_a",
                expected_checkpoint_head=started["checkpoint_head"], expected_state_digest=started["state_digest"],
                expected_prompt_digest=started["prompt_digest"], completion=_completion(), shared_remote_mode="DISABLED",
            )

    def test_claim_handoff_is_coordination_only(self):
        control, base, board, _ = self._case()
        started = self._start(base)
        control.claim(loop_id=started["loop_id"], agent_id="agent_a")
        result = control.claim_handoff(loop_id=started["loop_id"], agent_id="agent_a", handoff_to="agent_b")
        self.assertEqual(result["status"], "RELEASED")
        self.assertEqual(board.release_calls[-1], ("agent_a", "HANDOFF", "agent_b"))
        self.assertIn("CLAIM_HANDOFF != REHYDRATION_HANDOFF_DELTA", result["laws"])

    def test_controlled_resume_exposes_owner_without_replacing_handoff_delta(self):
        control, base, _, _ = self._case()
        started = self._start(base)
        control.claim(loop_id=started["loop_id"], agent_id="agent_a")
        resumed = control.resume_controlled(loop_id=started["loop_id"], agent_id="agent_a", shared_remote_mode="DISABLED")
        self.assertEqual(resumed["status"], "RESUMED")
        self.assertEqual(resumed["coordination"]["active_owners"][0]["agent_id"], "agent_a")
        self.assertIn("athena_rehydration_handoff_delta/resume", resumed["next"])

    def test_control_tool_surface_does_not_duplicate_successor_or_handoff_delta_names(self):
        self.assertEqual(CONTROL_TOOL_NAMES, {
            "athena_rehydration_claim",
            "athena_rehydration_advance_claimed",
            "athena_rehydration_claim_handoff",
            "athena_rehydration_resume_controlled",
        })
        self.assertNotIn("athena_rehydration_successor_preview", CONTROL_TOOL_NAMES)
        self.assertNotIn("athena_rehydration_handoff_delta", CONTROL_TOOL_NAMES)
        self.assertNotIn("athena_rehydration_handoff_resume", CONTROL_TOOL_NAMES)


if __name__ == "__main__":
    unittest.main()
