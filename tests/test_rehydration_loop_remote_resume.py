from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime


def _run(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if check and p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p


def _write(root: Path, rel: str, value) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed_prompt_brain(base: Path) -> tuple[Path, Path]:
    agent_a = base / "agent-a"
    agent_a.mkdir()
    _run(agent_a, "init", "-b", "main")
    _run(agent_a, "config", "user.name", "agent-a")
    _run(agent_a, "config", "user.email", "agent-a@example.invalid")
    _write(agent_a, "prompts/PROMPT.manifest.json", {
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
    _write(agent_a, "prompts/state/ACTIVE.json", {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "MAXDEV",
        "enabled_modules": ["core"],
        "active_scoped_overlays": [],
        "revision": 1,
    })
    _write(agent_a, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(agent_a, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(agent_a, "add", ".")
    _run(agent_a, "commit", "-m", "seed shared prompt brain")

    origin = base / "brain.git"
    p = subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(agent_a, "remote", "add", "origin", str(origin))
    _run(agent_a, "push", "-u", "origin", "main")
    return agent_a, origin


def _clone(origin: Path, target: Path, actor: str) -> None:
    p = subprocess.run(["git", "clone", str(origin), str(target)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(target, "config", "user.name", actor)
    _run(target, "config", "user.email", f"{actor}@example.invalid")


def _runtime(root: Path) -> RehydrationLoopRuntime:
    git = GitBackend(root)
    return RehydrationLoopRuntime(git, PromptRuntime(git))


def _passes() -> list[dict]:
    return [
        {"kind": kind, "summary": f"{kind} completed", "evidence_refs": []}
        for kind in ("reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize")
    ]


class RehydrationLoopRemoteResumeTests(unittest.TestCase):
    def test_stale_existing_agent_auto_syncs_before_resume(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        agent_a, origin = _seed_prompt_brain(base)
        runtime_a = _runtime(agent_a)

        started = runtime_a.start(
            goal="Develop the feature across multiple cold agents",
            task="Implement the first bounded slice",
            expected_git_head=runtime_a.git.head(),
            actor="agent-a",
            use_frontier=False,
            fetch=False,
            shared_remote_mode="REQUIRED",
            max_steps=16,
            max_no_progress=3,
            depth_mode="deep",
        )
        self.assertEqual(started["status"], "STARTED")
        self.assertTrue(started["durable_return"])
        start_checkpoint = started["checkpoint_head"]

        # Agent B is a genuinely cold checkout created only after A has published
        # the loop. Its first operation is resume, not a copied in-memory packet.
        agent_b = base / "agent-b"
        _clone(origin, agent_b, "agent-b")
        runtime_b = _runtime(agent_b)
        resumed_b = runtime_b.resume(started["loop_id"])
        self.assertEqual(resumed_b["status"], "RESUMED")
        self.assertTrue(resumed_b["shared_frontier_verified"])
        self.assertEqual(resumed_b["checkpoint_head"], start_checkpoint)
        self.assertEqual(resumed_b["step_index"], 0)

        # B performs material work and shares that work commit before asking the
        # loop to advance. The advance commit then publishes the new checkpoint.
        _write(agent_b, "feature.txt", "feature from cold agent B\n")
        _run(agent_b, "add", "feature.txt")
        _run(agent_b, "commit", "-m", "agent B implements first slice")
        work_head = _run(agent_b, "rev-parse", "HEAD").stdout.strip()
        _run(agent_b, "push", "origin", "main")

        advanced = runtime_b.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=resumed_b["checkpoint_head"],
            expected_state_digest=resumed_b["state_digest"],
            expected_prompt_digest=resumed_b["prompt_digest"],
            completion={
                "status": "SUCCEEDED",
                "observed": True,
                "terminal": False,
                "hard_hold": False,
                "summary": "cold agent B implemented and verified the first slice",
                "progress_delta": 1.0,
                "passes": _passes(),
                "tests": [{"name": "cold-agent-work", "status": "PASS", "evidence_ref": f"git://{work_head}"}],
                "evidence_refs": [f"git://{work_head}"],
                "residuals": ["second bounded slice remains"],
                "next_task": "Harden the feature from the shared successor checkpoint",
                "handoff_to": "agent-a",
            },
            actor="agent-b",
            shared_remote_mode="REQUIRED",
        )
        self.assertEqual(advanced["status"], "ACTIVE")
        self.assertTrue(advanced["durable_return"])
        self.assertEqual(advanced["step_index"], 1)
        successor_checkpoint = advanced["checkpoint_head"]
        self.assertNotEqual(successor_checkpoint, start_checkpoint)

        # A has deliberately not fetched since starting the loop. Pre-fix resume
        # would have read A's old step-0 state and returned RESUMED. The RHL-001
        # antibody must fetch+fast-forward first and only then read the handoff.
        self.assertEqual(_run(agent_a, "rev-parse", "HEAD").stdout.strip(), start_checkpoint)
        resumed_a = runtime_a.resume(started["loop_id"])
        self.assertEqual(resumed_a["status"], "RESUMED")
        self.assertTrue(resumed_a["shared_frontier_verified"])
        self.assertEqual(resumed_a["remote_sync"]["status"], "FAST_FORWARDED")
        self.assertEqual(resumed_a["step_index"], 1)
        self.assertEqual(resumed_a["checkpoint_head"], successor_checkpoint)
        self.assertEqual(resumed_a["current_git_head"], successor_checkpoint)
        self.assertIn("Harden the feature from the shared successor checkpoint", resumed_a["compiled_self_prompt"])
        self.assertEqual(runtime_a.verify(started["loop_id"])["status"], "PASS")

    def test_resume_holds_when_shared_remote_cannot_be_verified(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        agent_a, origin = _seed_prompt_brain(base)
        runtime = _runtime(agent_a)
        started = runtime.start(
            goal="Persist one resumable loop",
            task="Start",
            expected_git_head=runtime.git.head(),
            actor="agent-a",
            use_frontier=False,
            fetch=False,
            shared_remote_mode="REQUIRED",
        )
        self.assertTrue(started["durable_return"])

        # Remove the configured remote after the durable start. Direct resume must
        # no longer silently trust the local checkpoint as shared-current state.
        _run(agent_a, "remote", "remove", "origin")
        value = runtime.call_tool("athena_rehydration_resume", {
            "loop_id": started["loop_id"],
            "include_prompt": False,
        })
        self.assertEqual(value["status"], "REHYDRATION_RESUME_SHARED_FRONTIER_HOLD")
        self.assertFalse(value["durable_return"])


if __name__ == "__main__":
    unittest.main()
