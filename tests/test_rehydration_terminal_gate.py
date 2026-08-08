from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
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
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _runtime(base: Path) -> tuple[RehydrationLoopRuntime, Path]:
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
        "modules": {
            "core": {
                "path": "prompts/ORCHESTRATION_CORE.md",
                "order": 0,
                "mandatory": True,
            }
        },
    })
    _write(root, "prompts/state/ACTIVE.json", {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "MAXDEV",
        "enabled_modules": ["core"],
        "active_scoped_overlays": [],
        "revision": 1,
    })
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed brain")
    git = GitBackend(root)
    return RehydrationLoopRuntime(git, PromptRuntime(git)), root


def _passes() -> list[dict]:
    return [
        {"kind": kind, "summary": f"{kind} completed", "evidence_refs": []}
        for kind in ("reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize")
    ]


def _terminal_evidence() -> dict:
    return {
        "goal_satisfied": True,
        "remaining_material_work": False,
        "reason": "all declared work is complete",
        "evidence_refs": ["git://feature", "test://unit"],
    }


def _completion(**updates) -> dict:
    value = {
        "status": "SUCCEEDED",
        "observed": True,
        "terminal": True,
        "hard_hold": False,
        "summary": "finished the bounded implementation",
        "progress_delta": 1.0,
        "passes": _passes(),
        "tests": [{"name": "unit", "status": "PASS", "evidence_ref": "test://unit"}],
        "evidence_refs": ["git://feature"],
        "residuals": [],
        "next_task": None,
        "handoff_to": None,
        "terminal_evidence": _terminal_evidence(),
    }
    value.update(updates)
    return value


class TerminalClosureGateTests(unittest.TestCase):
    def _start(self, *, stop_conditions=None):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        runtime, root = _runtime(Path(td.name))
        started = runtime.start(
            goal="Complete the full feature without premature termination",
            task="Implement the current slice",
            expected_git_head=runtime.git.head(),
            use_frontier=False,
            fetch=False,
            shared_remote_mode="DISABLED",
            depth_mode="deep",
            stop_conditions=stop_conditions or [],
        )
        _write(root, "feature.txt", "material implementation\n")
        _run(root, "add", "feature.txt")
        _run(root, "commit", "-m", "material implementation")
        return runtime, root, started

    @staticmethod
    def _advance(runtime, started, completion):
        return runtime.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=started["checkpoint_head"],
            expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"],
            completion=completion,
            shared_remote_mode="DISABLED",
        )

    def test_known_residual_rejects_terminal_and_auto_steers_successor(self):
        runtime, _, started = self._start()
        out = self._advance(runtime, started, _completion(
            residuals=["Implement the remaining hardening slice"],
        ))
        self.assertEqual(out["status"], "ACTIVE")
        self.assertFalse(out["terminal"])
        self.assertFalse(out["terminal_request_accepted"])
        self.assertEqual(out["terminal_gate"]["status"], "REJECTED_CONTINUE")
        self.assertIn("KNOWN_RESIDUAL_WORK_REMAINS", out["terminal_gate"]["reasons"])
        self.assertEqual(out["successor_baton"]["status"], "SELECTED")
        self.assertEqual(out["successor_baton"]["selected"]["task"], "Implement the remaining hardening slice")

        state, _ = runtime._read_state(started["loop_id"])
        self.assertEqual(state["status"], "ACTIVE")
        self.assertFalse(state["last_completion"]["terminal"])
        self.assertEqual(state["last_completion"]["terminal_gate"]["status"], "REJECTED_CONTINUE")
        self.assertEqual(state["task"], "Implement the remaining hardening slice")

    def test_declared_next_task_rejects_terminal(self):
        runtime, _, started = self._start()
        out = self._advance(runtime, started, _completion(next_task="Run the integration witness"))
        self.assertEqual(out["status"], "ACTIVE")
        self.assertIn("NEXT_TASK_DECLARED", out["terminal_gate"]["reasons"])
        self.assertEqual(out["successor_baton"]["status"], "SELECTED")

    def test_nonpass_test_rejects_terminal(self):
        runtime, _, started = self._start()
        out = self._advance(runtime, started, _completion(
            tests=[{"name": "integration", "status": "HOLD", "evidence_ref": "hold://dependency"}],
        ))
        self.assertEqual(out["status"], "ACTIVE")
        self.assertTrue(any(reason.startswith("NONPASS_TERMINAL_TESTS:") for reason in out["terminal_gate"]["reasons"]))
        self.assertNotEqual(out["successor_baton"]["status"], "TERMINAL")

    def test_missing_terminal_evidence_rejects_terminal(self):
        runtime, _, started = self._start()
        out = self._advance(runtime, started, _completion(terminal_evidence=None))
        self.assertEqual(out["status"], "ACTIVE")
        self.assertIn("TERMINAL_EVIDENCE_MISSING", out["terminal_gate"]["reasons"])
        self.assertNotEqual(out["successor_baton"]["status"], "TERMINAL")

    def test_unwitnessed_stop_condition_rejects_terminal(self):
        condition = "integration artifact is independently verified"
        runtime, _, started = self._start(stop_conditions=[condition])
        out = self._advance(runtime, started, _completion())
        self.assertEqual(out["status"], "ACTIVE")
        self.assertTrue(any(reason.startswith("STOP_CONDITIONS_UNWITNESSED:") for reason in out["terminal_gate"]["reasons"]))

    def test_valid_stop_witness_accepts_terminal_and_suppresses_successor(self):
        condition = "integration artifact is independently verified"
        runtime, _, started = self._start(stop_conditions=[condition])
        out = self._advance(runtime, started, _completion(
            stop_results=[{
                "condition": condition,
                "status": "PASS",
                "evidence_ref": "test://independent-integration",
            }],
        ))
        self.assertEqual(out["status"], "COMPLETE")
        self.assertTrue(out["terminal"])
        self.assertTrue(out["terminal_request_accepted"])
        self.assertEqual(out["terminal_gate"]["status"], "ACCEPTED")
        self.assertEqual(out["successor_baton"]["status"], "TERMINAL")
        self.assertEqual(out["successor_baton"]["candidates"], [])


if __name__ == "__main__":
    unittest.main()
