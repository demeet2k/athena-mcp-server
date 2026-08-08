from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.frontier_runtime import DEFAULT_SOURCE_REF
from athena_mcp.git_backend import GitBackend, GitStaleHead
from athena_mcp.prompt_runtime import PromptRuntime
from athena_mcp.rehydration_loop import (
    REHYDRATION_TOOL_NAMES,
    RehydrationLoopRuntime,
)


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
            "status": "SELECTED",
            "source_head": "source-head-1",
            "frontier_digest": "frontier-digest-1",
            "selected": {"run_id": "run.alpha", "node_id": "build"},
            "pareto_front": [{"run_id": "run.alpha", "node_id": "build"}],
            "frontier": {
                "residuals": [{"kind": "DECLARED_NEXT_FRONTIER", "value": "verify"}],
                "source_coverage": {"event_reduced_runs": 1},
            },
        }


class _Remote:
    def sync(self, remote="origin"):
        return {"status": "UP_TO_DATE", "remote": remote, "shared_frontier_verified": True}

    def publish(self, expected_git_head, remote="origin"):
        return {
            "status": "PUBLISHED_SHARED",
            "remote": remote,
            "published_head": expected_git_head,
            "shared_frontier_verified": True,
        }


class _RemoteHold:
    def sync(self, remote="origin"):
        return {"status": "DIVERGED_HOLD", "remote": remote, "shared_frontier_verified": False}

    def publish(self, expected_git_head, remote="origin"):
        return {"status": "PUBLISH_HOLD", "remote": remote, "shared_frontier_verified": False}


def _brain(base: Path, remote=None) -> tuple[RehydrationLoopRuntime, Path]:
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
        "profiles": {"MAXDEV": ["core"], "BUILD": ["core"]},
        "modules": {
            "core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}
        },
    }
    active = {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "MAXDEV",
        "enabled_modules": ["core"],
        "active_scoped_overlays": [],
        "revision": 1,
    }
    _write(root, "prompts/PROMPT.manifest.json", manifest)
    _write(root, "prompts/state/ACTIVE.json", active)
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed brain")
    git = GitBackend(root)
    prompt = PromptRuntime(git)
    runtime = RehydrationLoopRuntime(git, prompt, _Frontier(), remote or _Remote())
    return runtime, root


def _passes():
    return [
        {"kind": kind, "summary": f"{kind} completed", "evidence_refs": []}
        for kind in ("reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize")
    ]


def _completion(**updates):
    value = {
        "status": "SUCCEEDED",
        "observed": True,
        "terminal": False,
        "hard_hold": False,
        "summary": "implemented and verified one bounded change",
        "progress_delta": 1.0,
        "passes": _passes(),
        "tests": [{"name": "unit", "status": "PASS", "evidence_ref": "test://unit"}],
        "evidence_refs": ["git://feature.txt"],
        "residuals": ["next hardening step"],
        "next_task": "Harden the feature",
        "handoff_to": None,
    }
    value.update(updates)
    return value


class RehydrationLoopTests(unittest.TestCase):
    def _runtime(self, remote=None):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _brain(Path(td.name), remote)

    def _start(self, runtime):
        return runtime.start(
            goal="Build and verify a durable Git feature",
            task="Implement one bounded feature slice",
            expected_git_head=runtime.git.head(),
            actor="builder",
            profile="BUILD",
            source_ref=DEFAULT_SOURCE_REF,
            fetch=False,
            use_frontier=True,
            shared_remote_mode="DISABLED",
            max_steps=8,
            max_no_progress=2,
            depth_mode="deep",
        )

    def test_start_work_advance_resume_and_verify(self):
        runtime, root = self._runtime()
        started = self._start(runtime)
        self.assertEqual(started["status"], "STARTED")
        self.assertIn("CYCLE != BACKGROUND_EXECUTION", started["compiled_self_prompt"])

        _write(root, "feature.txt", "feature v1\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "implement feature v1")

        advanced = runtime.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=started["checkpoint_head"],
            expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"],
            completion=_completion(),
            actor="builder",
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(advanced["status"], "ACTIVE")
        self.assertEqual(advanced["step_index"], 1)
        self.assertIn("feature.txt", advanced["material_work_paths"])

        resumed = runtime.resume(started["loop_id"])
        self.assertEqual(resumed["status"], "RESUMED")
        self.assertEqual(resumed["step_index"], 1)
        self.assertIn("Harden the feature", resumed["compiled_self_prompt"])

        verified = runtime.verify(started["loop_id"])
        self.assertEqual(verified["status"], "PASS", verified)
        self.assertEqual(verified["step_count"], 1)

    def test_completion_must_be_observed_and_include_deep_passes(self):
        runtime, root = self._runtime()
        started = self._start(runtime)
        _write(root, "feature.txt", "v1\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "feature")

        with self.assertRaisesRegex(ValueError, "observed=true"):
            runtime.advance(
                loop_id=started["loop_id"],
                expected_checkpoint_head=started["checkpoint_head"],
                expected_state_digest=started["state_digest"],
                expected_prompt_digest=started["prompt_digest"],
                completion=_completion(observed=False),
                shared_remote_mode="DISABLED",
            )

        with self.assertRaisesRegex(ValueError, "missing required deliberation passes"):
            runtime.advance(
                loop_id=started["loop_id"],
                expected_checkpoint_head=started["checkpoint_head"],
                expected_state_digest=started["state_digest"],
                expected_prompt_digest=started["prompt_digest"],
                completion=_completion(passes=[{"kind": "execute", "summary": "only executed"}]),
                shared_remote_mode="DISABLED",
            )

    def test_advance_requires_a_descendant_work_commit(self):
        runtime, _ = self._runtime()
        started = self._start(runtime)
        with self.assertRaisesRegex(ValueError, "substantive Git commit"):
            runtime.advance(
                loop_id=started["loop_id"],
                expected_checkpoint_head=started["checkpoint_head"],
                expected_state_digest=started["state_digest"],
                expected_prompt_digest=started["prompt_digest"],
                completion=_completion(),
                shared_remote_mode="DISABLED",
            )

    def test_repeated_no_progress_holds_instead_of_recursing_forever(self):
        runtime, _ = self._runtime()
        started = self._start(runtime)
        no_progress = {
            "status": "NO_PROGRESS",
            "observed": True,
            "terminal": False,
            "summary": "external dependency remained unavailable",
            "progress_delta": 0.0,
            "passes": [],
            "tests": [],
            "evidence_refs": ["hold://external"],
            "residuals": ["external dependency"],
            "next_task": "Attempt the next lawful alternative",
        }
        first = runtime.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=started["checkpoint_head"],
            expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"],
            completion=no_progress,
            allow_no_git_change=True,
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(first["status"], "ACTIVE")
        self.assertEqual(first["no_progress_count"], 1)
        second = runtime.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=first["checkpoint_head"],
            expected_state_digest=first["state_digest"],
            expected_prompt_digest=first["prompt_digest"],
            completion={**no_progress, "summary": "second observed no-progress cycle"},
            allow_no_git_change=True,
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(second["status"], "HOLD_NO_PROGRESS")
        self.assertTrue(second["terminal"])
        self.assertEqual(runtime.verify(started["loop_id"])["status"], "PASS")

    def test_stale_checkpoint_and_tampered_prompt_fail_closed(self):
        runtime, root = self._runtime()
        started = self._start(runtime)
        prompt = root / started["prompt_path"]
        prompt.write_text(prompt.read_text() + "tamper\n", encoding="utf-8")
        with self.assertRaisesRegex(Exception, "TAMPERED_REHYDRATION_PROMPT"):
            runtime.advance(
                loop_id=started["loop_id"],
                expected_checkpoint_head=started["checkpoint_head"],
                expected_state_digest=started["state_digest"],
                expected_prompt_digest=started["prompt_digest"],
                completion=_completion(),
                allow_no_git_change=True,
                shared_remote_mode="DISABLED",
            )
        _run(root, "reset", "--hard", "HEAD")

        with self.assertRaises(GitStaleHead):
            runtime.advance(
                loop_id=started["loop_id"],
                expected_checkpoint_head="0" * 40,
                expected_state_digest=started["state_digest"],
                expected_prompt_digest=started["prompt_digest"],
                completion=_completion(),
                allow_no_git_change=True,
                shared_remote_mode="DISABLED",
            )

    def test_required_remote_failure_returns_typed_hold_through_tool(self):
        runtime, _ = self._runtime(_RemoteHold())
        value = runtime.call_tool("athena_rehydration_start", {
            "goal": "Build feature",
            "expected_git_head": runtime.git.head(),
            "shared_remote_mode": "REQUIRED",
            "use_frontier": False,
        })
        self.assertEqual(value["status"], "SHARED_FRONTIER_HOLD")
        self.assertFalse(value["durable_return"])

    def test_terminal_completion_and_index(self):
        runtime, root = self._runtime()
        started = self._start(runtime)
        _write(root, "feature.txt", "done\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "complete feature")
        final = runtime.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=started["checkpoint_head"],
            expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"],
            completion=_completion(terminal=True, next_task=None),
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(final["status"], "COMPLETE")
        with self.assertRaisesRegex(ValueError, "terminal"):
            runtime.advance(
                loop_id=started["loop_id"],
                expected_checkpoint_head=final["checkpoint_head"],
                expected_state_digest=final["state_digest"],
                expected_prompt_digest=final["prompt_digest"],
                completion=_completion(),
                allow_no_git_change=True,
                shared_remote_mode="DISABLED",
            )
        index = runtime.index()
        self.assertEqual(index["count"], 1)
        self.assertEqual(index["loops"][0]["status"], "COMPLETE")

    def test_tool_surface_contains_full_loop_membrane(self):
        self.assertEqual(REHYDRATION_TOOL_NAMES, {
            "athena_rehydration_start",
            "athena_rehydration_advance",
            "athena_rehydration_resume",
            "athena_rehydration_verify",
            "athena_rehydration_index",
        })


if __name__ == "__main__":
    unittest.main()
