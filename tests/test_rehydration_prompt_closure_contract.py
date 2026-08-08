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
    _run(root, "commit", "-m", "seed prompt brain")
    git = GitBackend(root)
    return RehydrationLoopRuntime(git, PromptRuntime(git)), root


def _passes() -> list[dict]:
    return [
        {"kind": kind, "summary": f"{kind} observed", "evidence_refs": []}
        for kind in ("reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize")
    ]


class RehydrationPromptClosureContractTests(unittest.TestCase):
    def _start(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        runtime, root = _runtime(Path(td.name))
        stop_condition = "all integration acceptance tests pass on the shared-current head"
        started = runtime.start(
            goal="Finish the whole mission without premature stopping",
            task="Implement the current bounded slice",
            expected_git_head=runtime.git.head(),
            actor="agent-a",
            use_frontier=False,
            fetch=False,
            shared_remote_mode="DISABLED",
            max_steps=16,
            max_no_progress=3,
            max_prompt_chars=8000,
            depth_mode="deep",
            stop_conditions=[stop_condition],
        )
        return runtime, root, started, stop_condition

    def assertClosureContract(self, prompt: str, stop_condition: str) -> None:
        self.assertIn("ATHENA.REHYDRATION.PROMPT.CLOSURE.CONTRACT.V1", prompt)
        self.assertIn("BOUNDED_CYCLE_COMPLETE != MISSION_COMPLETE", prompt)
        self.assertIn("HUMAN_NEXT != ORDINARY_CONTINUATION_CONTROL", prompt)
        self.assertIn("terminal=true", prompt)
        self.assertIn("witnessed closure request", prompt)
        self.assertIn('"terminal_evidence": null', prompt)
        self.assertIn('"stop_results": []', prompt)
        self.assertIn('"remaining_material_work": false', prompt)
        self.assertIn("AUTO-route the successor baton", prompt)
        self.assertIn("runtime demotes it to continuation and self-steers the successor", prompt)
        self.assertIn(stop_condition, prompt)
        self.assertNotIn("before requesting the next one", prompt)

    def test_first_prompt_teaches_mission_closure_and_fits_minimum_budget(self):
        _, _, started, stop_condition = self._start()
        prompt = started["compiled_self_prompt"]
        self.assertClosureContract(prompt, stop_condition)
        self.assertLessEqual(len(prompt), 8000)

    def test_successor_prompt_retains_contract_after_real_material_advance(self):
        runtime, root, started, stop_condition = self._start()
        _write(root, "feature.txt", "material bounded slice\n")
        _run(root, "add", "feature.txt")
        _run(root, "commit", "-m", "material bounded slice")

        advanced = runtime.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=started["checkpoint_head"],
            expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"],
            completion={
                "status": "SUCCEEDED",
                "observed": True,
                "terminal": False,
                "hard_hold": False,
                "summary": "implemented and verified the bounded slice",
                "progress_delta": 1.0,
                "passes": _passes(),
                "tests": [{"name": "slice", "status": "PASS", "evidence_ref": "test://slice"}],
                "evidence_refs": ["git://feature.txt"],
                "residuals": ["run the remaining integration hardening"],
                "next_task": "Run the remaining integration hardening",
                "handoff_to": "agent-b",
            },
            actor="agent-a",
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(advanced["status"], "ACTIVE")
        self.assertClosureContract(advanced["compiled_self_prompt"], stop_condition)
        self.assertIn("run the remaining integration hardening", advanced["compiled_self_prompt"])
        self.assertLessEqual(len(advanced["compiled_self_prompt"]), 8000)

    def test_prompt_explicitly_separates_cycle_receipt_from_terminal_evidence(self):
        _, _, started, _ = self._start()
        prompt = started["compiled_self_prompt"]
        self.assertIn("Complete the current bounded cycle and return one observed receipt", prompt)
        self.assertIn("whole mission, not merely this cycle", prompt)
        self.assertIn("Keep `terminal=false` whenever any material residual", prompt)
        self.assertIn("Do not erase residuals merely to make closure pass", prompt)


if __name__ == "__main__":
    unittest.main()
