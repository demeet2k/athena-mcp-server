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


def _start_shared_loop(runtime: RehydrationLoopRuntime) -> dict:
    return runtime.start(
        goal="Develop the feature across multiple cold agents",
        task="Implement the first bounded slice",
        expected_git_head=runtime.git.head(),
        actor="agent-a",
        use_frontier=False,
        fetch=False,
        shared_remote_mode="REQUIRED",
        max_steps=16,
        max_no_progress=3,
        depth_mode="deep",
    )


def _advance_from_cold_agent(origin: Path, base: Path, started: dict, actor: str = "agent-b") -> tuple[Path, dict]:
    agent = base / actor
    _clone(origin, agent, actor)
    runtime = _runtime(agent)
    resumed = runtime.resume(started["loop_id"])
    if resumed["status"] != "RESUMED":
        raise AssertionError(resumed)
    _write(agent, "feature.txt", f"feature from cold {actor}\n")
    _run(agent, "add", "feature.txt")
    _run(agent, "commit", "-m", f"{actor} implements first slice")
    work_head = _run(agent, "rev-parse", "HEAD").stdout.strip()
    _run(agent, "push", "origin", "main")
    advanced = runtime.advance(
        loop_id=started["loop_id"],
        expected_checkpoint_head=resumed["checkpoint_head"],
        expected_state_digest=resumed["state_digest"],
        expected_prompt_digest=resumed["prompt_digest"],
        completion={
            "status": "SUCCEEDED",
            "observed": True,
            "terminal": False,
            "hard_hold": False,
            "summary": f"cold {actor} implemented and verified the first slice",
            "progress_delta": 1.0,
            "passes": _passes(),
            "tests": [{"name": "cold-agent-work", "status": "PASS", "evidence_ref": f"git://{work_head}"}],
            "evidence_refs": [f"git://{work_head}"],
            "residuals": ["second bounded slice remains"],
            "next_task": "Harden the feature from the shared successor checkpoint",
            "handoff_to": "agent-a",
        },
        actor=actor,
        shared_remote_mode="REQUIRED",
    )
    return agent, advanced


class RehydrationLoopRemoteResumeTests(unittest.TestCase):
    def test_stale_existing_agent_auto_syncs_before_resume(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        agent_a, origin = _seed_prompt_brain(base)
        runtime_a = _runtime(agent_a)

        started = _start_shared_loop(runtime_a)
        self.assertEqual(started["status"], "STARTED")
        self.assertTrue(started["durable_return"])
        start_checkpoint = started["checkpoint_head"]

        _, advanced = _advance_from_cold_agent(origin, base, started)
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

    def test_stale_verify_and_index_auto_sync_before_reading(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        agent_a, origin = _seed_prompt_brain(base)
        runtime_a = _runtime(agent_a)
        started = _start_shared_loop(runtime_a)
        start_checkpoint = started["checkpoint_head"]

        # Clone an index observer while shared state is still at step 0. Both A
        # and the observer must remain stale while B later publishes step 1.
        observer = base / "observer"
        _clone(origin, observer, "observer")
        runtime_observer = _runtime(observer)
        self.assertEqual(_run(observer, "rev-parse", "HEAD").stdout.strip(), start_checkpoint)

        _, advanced = _advance_from_cold_agent(origin, base, started)
        successor_checkpoint = advanced["checkpoint_head"]
        self.assertNotEqual(successor_checkpoint, start_checkpoint)
        self.assertEqual(_run(agent_a, "rev-parse", "HEAD").stdout.strip(), start_checkpoint)
        self.assertEqual(_run(observer, "rev-parse", "HEAD").stdout.strip(), start_checkpoint)

        # Pre-RHL-002 this could PASS the internally valid but obsolete step-0
        # chain. The shared-fresh verifier must FF first and prove step 1 instead.
        verified = runtime_a.verify(started["loop_id"])
        self.assertEqual(verified["status"], "PASS")
        self.assertTrue(verified["shared_frontier_verified"])
        self.assertEqual(verified["remote_sync"]["status"], "FAST_FORWARDED")
        self.assertEqual(verified["step_count"], 1)
        self.assertEqual(verified["checkpoint_head"], successor_checkpoint)
        self.assertEqual(_run(agent_a, "rev-parse", "HEAD").stdout.strip(), successor_checkpoint)

        # Pre-RHL-003 the observer could inventory the old step-0 tip. Index must
        # independently refresh and return the current shared checkpoint/step.
        indexed = runtime_observer.index()
        self.assertEqual(indexed["status"], "OK")
        self.assertTrue(indexed["shared_frontier_verified"])
        self.assertEqual(indexed["remote_sync"]["status"], "FAST_FORWARDED")
        loop = next(row for row in indexed["loops"] if row["loop_id"] == started["loop_id"])
        self.assertEqual(loop["step_index"], 1)
        self.assertEqual(loop["checkpoint_head"], successor_checkpoint)
        self.assertEqual(_run(observer, "rev-parse", "HEAD").stdout.strip(), successor_checkpoint)

    def test_rehydration_reads_hold_when_shared_remote_cannot_be_verified(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        agent_a, _ = _seed_prompt_brain(base)
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

        # Remove the configured remote after the durable start. All read-side
        # surfaces that claim shared-current state must fail closed.
        _run(agent_a, "remote", "remove", "origin")
        cases = (
            ("athena_rehydration_resume", {"loop_id": started["loop_id"], "include_prompt": False}, "REHYDRATION_RESUME_SHARED_FRONTIER_HOLD"),
            ("athena_rehydration_verify", {"loop_id": started["loop_id"]}, "REHYDRATION_VERIFY_SHARED_FRONTIER_HOLD"),
            ("athena_rehydration_index", {}, "REHYDRATION_INDEX_SHARED_FRONTIER_HOLD"),
        )
        for tool, args, expected in cases:
            value = runtime.call_tool(tool, args)
            self.assertEqual(value["status"], expected, value)
            self.assertFalse(value["durable_return"])


if __name__ == "__main__":
    unittest.main()
