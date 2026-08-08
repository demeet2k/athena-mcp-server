from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime
from athena_mcp.rehydration_terminal import evaluate_terminal_request


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


def _runtime(base: Path) -> tuple[RehydrationLoopRuntime, dict]:
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
    _run(root, "commit", "-m", "seed")
    git = GitBackend(root)
    runtime = RehydrationLoopRuntime(git, PromptRuntime(git))
    started = runtime.start(
        goal="Finish only after observed deep closure",
        task="Current slice",
        expected_git_head=git.head(),
        use_frontier=False,
        fetch=False,
        shared_remote_mode="DISABLED",
        depth_mode="deep",
    )
    return runtime, started


def _passes() -> list[dict]:
    return [
        {"kind": kind, "summary": f"{kind} observed", "evidence_refs": []}
        for kind in ("reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize")
    ]


def _completion(**updates) -> dict:
    value = {
        "status": "SUCCEEDED",
        "observed": True,
        "terminal": True,
        "hard_hold": False,
        "summary": "closure candidate",
        "passes": _passes(),
        "tests": [{"name": "unit", "status": "PASS", "evidence_ref": "test://unit"}],
        "residuals": [],
        "next_task": None,
        "terminal_evidence": {
            "goal_satisfied": True,
            "remaining_material_work": False,
            "reason": "all work is complete",
            "evidence_refs": ["git://artifact", "test://unit"],
        },
    }
    value.update(updates)
    return value


class TerminalGateObservationTests(unittest.TestCase):
    def test_unobserved_completion_cannot_close_even_outside_advance(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        runtime, started = _runtime(Path(td.name))
        gate = evaluate_terminal_request(runtime, started["loop_id"], _completion(observed=False))
        self.assertEqual(gate["status"], "REJECTED_CONTINUE")
        self.assertIn("TERMINAL_COMPLETION_NOT_OBSERVED", gate["reasons"])

    def test_missing_required_deep_pass_cannot_close(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        runtime, started = _runtime(Path(td.name))
        partial = [row for row in _passes() if row["kind"] != "attack"]
        gate = evaluate_terminal_request(runtime, started["loop_id"], _completion(passes=partial))
        self.assertEqual(gate["status"], "REJECTED_CONTINUE")
        self.assertTrue(any(reason == "TERMINAL_REQUIRED_PASSES_MISSING:attack" for reason in gate["reasons"]))
        self.assertIn("attack", gate["required_passes"])
        self.assertNotIn("attack", gate["observed_passes"])

    def test_fully_observed_required_passes_can_clear_this_layer(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        runtime, started = _runtime(Path(td.name))
        gate = evaluate_terminal_request(runtime, started["loop_id"], _completion())
        self.assertEqual(gate["status"], "ACCEPTED", gate)
        self.assertEqual(sorted(gate["required_passes"]), sorted(gate["observed_passes"]))


if __name__ == "__main__":
    unittest.main()
