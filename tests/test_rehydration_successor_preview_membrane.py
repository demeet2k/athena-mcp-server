from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime
from athena_mcp.rehydration_successor import SUCCESSOR_TOOLS


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


def _seed_shared_brain(base: Path) -> tuple[Path, Path]:
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


def _start(runtime: RehydrationLoopRuntime) -> dict:
    return runtime.start(
        goal="Keep developing until witnessed closure rather than premature finish",
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


def _advance_from_cold_agent(origin: Path, base: Path, started: dict) -> dict:
    agent_b = base / "agent-b"
    _clone(origin, agent_b, "agent-b")
    runtime_b = _runtime(agent_b)
    resumed = runtime_b.resume(started["loop_id"])
    if resumed["status"] != "RESUMED":
        raise AssertionError(resumed)
    _write(agent_b, "feature.txt", "material step one\n")
    _run(agent_b, "add", "feature.txt")
    _run(agent_b, "commit", "-m", "agent-b material step one")
    work_head = _run(agent_b, "rev-parse", "HEAD").stdout.strip()
    _run(agent_b, "push", "origin", "main")
    return runtime_b.advance(
        loop_id=started["loop_id"],
        expected_checkpoint_head=resumed["checkpoint_head"],
        expected_state_digest=resumed["state_digest"],
        expected_prompt_digest=resumed["prompt_digest"],
        completion={
            "status": "SUCCEEDED",
            "observed": True,
            "terminal": False,
            "hard_hold": False,
            "summary": "cold agent-b completed the first material step",
            "progress_delta": 1.0,
            "passes": _passes(),
            "tests": [{"name": "step-one", "status": "PASS", "evidence_ref": f"git://{work_head}"}],
            "evidence_refs": [f"git://{work_head}"],
            "residuals": ["Implement the second material step"],
            "next_task": "Implement the second material step",
            "handoff_to": "observer",
        },
        actor="agent-b",
        shared_remote_mode="REQUIRED",
    )


def _terminal_completion(*, residuals=None) -> dict:
    return {
        "status": "SUCCEEDED",
        "observed": True,
        "terminal": True,
        "hard_hold": False,
        "summary": "request closure from preview",
        "progress_delta": 1.0,
        "passes": _passes(),
        "tests": [{"name": "integration", "status": "PASS", "evidence_ref": "test://integration"}],
        "evidence_refs": ["git://artifact", "test://integration"],
        "residuals": list(residuals or []),
        "next_task": None,
        "terminal_evidence": {
            "goal_satisfied": True,
            "remaining_material_work": False,
            "reason": "all declared work appears complete",
            "evidence_refs": ["git://artifact", "test://integration"],
        },
    }


class SuccessorPreviewMembraneTests(unittest.TestCase):
    def test_stale_preview_syncs_first_then_rejects_old_state_digest(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        agent_a, origin = _seed_shared_brain(base)
        runtime_a = _runtime(agent_a)
        started = _start(runtime_a)

        observer = base / "observer"
        _clone(origin, observer, "observer")
        runtime_observer = _runtime(observer)
        old_head = _run(observer, "rev-parse", "HEAD").stdout.strip()
        old_digest = started["state_digest"]

        advanced = _advance_from_cold_agent(origin, base, started)
        self.assertEqual(advanced["status"], "ACTIVE")
        self.assertEqual(advanced["step_index"], 1)
        self.assertNotEqual(advanced["checkpoint_head"], old_head)
        self.assertEqual(_run(observer, "rev-parse", "HEAD").stdout.strip(), old_head)

        stale = runtime_observer.call_tool("athena_rehydration_successor_preview", {
            "loop_id": started["loop_id"],
            "expected_state_digest": old_digest,
            "completion": {"status": "SUCCEEDED", "residuals": ["old local residual"]},
        })
        self.assertEqual(stale["status"], "STALE_SUCCESSOR_PREVIEW")
        self.assertTrue(stale["shared_frontier_verified"])
        self.assertEqual(stale["remote_sync"]["status"], "FAST_FORWARDED")
        self.assertTrue(stale["requires_rehydrate"])
        self.assertEqual(stale["detail"]["current_step_index"], 1)
        self.assertEqual(stale["detail"]["current_state_digest"], advanced["state_digest"])
        self.assertEqual(_run(observer, "rev-parse", "HEAD").stdout.strip(), advanced["checkpoint_head"])

    def test_invalid_terminal_preview_routes_residual_instead_of_returning_terminal(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        agent_a, _ = _seed_shared_brain(base)
        runtime = _runtime(agent_a)
        started = _start(runtime)

        preview = runtime.call_tool("athena_rehydration_successor_preview", {
            "loop_id": started["loop_id"],
            "expected_state_digest": started["state_digest"],
            "completion": _terminal_completion(residuals=["Implement the remaining hardening slice"]),
        })
        self.assertEqual(preview["status"], "SELECTED")
        self.assertTrue(preview["shared_frontier_verified"])
        self.assertEqual(preview["preview_verification"], "SHARED_CURRENT")
        self.assertFalse(preview["terminal_request_accepted"])
        self.assertEqual(preview["terminal_gate"]["status"], "REJECTED_CONTINUE")
        self.assertIn("KNOWN_RESIDUAL_WORK_REMAINS", preview["terminal_gate"]["reasons"])
        self.assertEqual(preview["selected"]["task"], "Implement the remaining hardening slice")
        self.assertIn("TERMINAL_REQUEST != TERMINAL_VERDICT", preview["laws"])

    def test_valid_witnessed_terminal_preview_can_return_terminal(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        agent_a, _ = _seed_shared_brain(base)
        runtime = _runtime(agent_a)
        started = _start(runtime)

        preview = runtime.call_tool("athena_rehydration_successor_preview", {
            "loop_id": started["loop_id"],
            "expected_state_digest": started["state_digest"],
            "completion": _terminal_completion(residuals=[]),
        })
        self.assertEqual(preview["status"], "TERMINAL")
        self.assertTrue(preview["terminal_request_accepted"])
        self.assertEqual(preview["terminal_gate"]["status"], "ACCEPTED")
        self.assertEqual(preview["candidates"], [])
        self.assertTrue(preview["shared_frontier_verified"])

    def test_required_remote_loss_holds_preview_but_disabled_mode_is_explicitly_local(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        agent_a, _ = _seed_shared_brain(base)
        runtime = _runtime(agent_a)
        started = _start(runtime)
        _run(agent_a, "remote", "remove", "origin")

        held = runtime.call_tool("athena_rehydration_successor_preview", {
            "loop_id": started["loop_id"],
            "expected_state_digest": started["state_digest"],
            "completion": {"status": "SUCCEEDED", "residuals": ["Continue locally"]},
        })
        self.assertEqual(held["status"], "REHYDRATION_SUCCESSOR_PREVIEW_SHARED_FRONTIER_HOLD")
        self.assertFalse(held["shared_frontier_verified"])
        self.assertTrue(held["requires_rehydrate"])

        local = runtime.call_tool("athena_rehydration_successor_preview", {
            "loop_id": started["loop_id"],
            "expected_state_digest": started["state_digest"],
            "completion": {"status": "SUCCEEDED", "residuals": ["Continue locally"]},
            "shared_remote_mode": "DISABLED",
        })
        self.assertEqual(local["status"], "SELECTED")
        self.assertFalse(local["shared_frontier_verified"])
        self.assertEqual(local["preview_verification"], "LOCAL_ONLY_UNVERIFIED")
        self.assertEqual(local["selected"]["task"], "Continue locally")

    def test_preview_tool_schema_exposes_shared_freshness_controls(self):
        tool = next(row for row in SUCCESSOR_TOOLS if row["name"] == "athena_rehydration_successor_preview")
        props = tool["inputSchema"]["properties"]
        self.assertIn("shared_remote_mode", props)
        self.assertIn("remote", props)
        self.assertIn("terminal", props["completion"]["description"])
        self.assertIn("Fresh-sync shared Git", tool["description"])


if __name__ == "__main__":
    unittest.main()
