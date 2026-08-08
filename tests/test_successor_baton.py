from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.frontier_runtime import DEFAULT_SOURCE_REF
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOL_NAMES, PromptRuntime
from athena_mcp.rehydration_loop import RehydrationLoopRuntime
from athena_mcp.successor_baton import SUCCESSOR_BATON_TOOL_NAMES, SuccessorBatonRuntime


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


class _MutableFrontier:
    def __init__(self):
        self.digest = "frontier-v1"
        self.source_head = "sched-head-v1"

    def select(self, **kwargs):
        return {
            "status": "SELECTED",
            "source_head": self.source_head,
            "frontier_digest": self.digest,
            "selected": {"run_id": "run.alpha", "node_id": "build"},
            "pareto_front": [{"run_id": "run.alpha", "node_id": "build"}],
            "frontier": {
                "frontier_digest": self.digest,
                "source_head": self.source_head,
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


def _brain(base: Path):
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
        "default_profile": "BUILD",
        "profiles": {"BUILD": ["core"]},
        "modules": {
            "core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True}
        },
    }
    active = {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "BUILD",
        "enabled_modules": ["core"],
        "active_scoped_overlays": [],
        "revision": 1,
    }
    _write(root, "prompts/PROMPT.manifest.json", manifest)
    _write(root, "prompts/state/ACTIVE.json", active)
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE V1\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed brain")

    git = GitBackend(root)
    prompt = PromptRuntime(git)
    frontier = _MutableFrontier()
    loop = RehydrationLoopRuntime(git, prompt, frontier, _Remote())
    baton = SuccessorBatonRuntime(git, prompt, loop)
    return root, frontier, loop, baton


def _passes():
    return [
        {"kind": kind, "summary": f"{kind} complete", "evidence_refs": []}
        for kind in ("reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize")
    ]


def _completion(**updates):
    value = {
        "status": "SUCCEEDED",
        "observed": True,
        "terminal": False,
        "hard_hold": False,
        "summary": "completed one verified bounded transition",
        "progress_delta": 1.0,
        "passes": _passes(),
        "tests": [{"name": "unit", "status": "PASS", "evidence_ref": "test://unit"}],
        "evidence_refs": ["git://feature.txt"],
        "residuals": ["next bounded residual"],
        "next_task": "Continue from the verified delta",
        "handoff_to": "successor",
    }
    value.update(updates)
    return value


class SuccessorBatonTests(unittest.TestCase):
    def _fixture(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return _brain(Path(td.name))

    def _start(self, loop):
        return loop.start(
            goal="Build a durable feature across successor agents",
            task="Implement one bounded feature slice",
            expected_git_head=loop.git.head(),
            actor="builder",
            profile="BUILD",
            source_ref=DEFAULT_SOURCE_REF,
            fetch=False,
            use_frontier=True,
            shared_remote_mode="DISABLED",
            max_steps=8,
            depth_mode="deep",
        )

    def _advance(self, root, loop, started, rel="feature.txt", text="feature v1\n"):
        _write(root, rel, text)
        _run(root, "add", ".")
        _run(root, "commit", "-m", f"work {rel}")
        return loop.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=started["checkpoint_head"],
            expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"],
            completion=_completion(),
            actor="builder",
            shared_remote_mode="DISABLED",
        )

    def test_delta_baton_is_deterministic_read_only_and_compressed(self):
        root, _, loop, baton = self._fixture()
        started = self._start(loop)
        self._advance(root, loop, started)
        head_before = loop.git.head()

        first = baton.derive(started["loop_id"])
        second = baton.derive(started["loop_id"])
        self.assertEqual(first["status"], "BATON_READY", first)
        self.assertEqual(first["baton_digest"], second["baton_digest"])
        self.assertEqual(loop.git.head(), head_before, "deriving a baton must not create Git progress")
        self.assertEqual(first["baton"]["hydration"]["mode"], "DELTA_ONLY")
        self.assertIn("project_work", first["baton"]["affected_cone"]["components"])

        consumed = baton.consume(
            loop_id=started["loop_id"],
            expected_baton_digest=first["baton_digest"],
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(consumed["status"], "SUCCESSOR_READY", consumed)
        self.assertEqual(consumed["hydration_mode"], "DELTA_ONLY")
        self.assertLess(consumed["compression"]["ratio"], 1.0, consumed["compression"])
        self.assertGreater(consumed["compression"]["saved_chars"], 0)

    def test_prompt_mutation_expands_only_prompt_cone(self):
        root, _, loop, baton = self._fixture()
        started = self._start(loop)
        self._advance(root, loop, started, "prompts/ORCHESTRATION_CORE.md", "CORE V2\n")
        derived = baton.derive(started["loop_id"])
        self.assertEqual(derived["status"], "BATON_READY")
        self.assertEqual(derived["baton"]["hydration"]["mode"], "PROMPT_CONE")
        self.assertTrue(derived["baton"]["coordinate_delta"]["prompt_stack_changed"])
        self.assertFalse(derived["baton"]["coordinate_delta"]["frontier_changed"])

        consumed = baton.consume(
            loop_id=started["loop_id"],
            expected_baton_digest=derived["baton_digest"],
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(consumed["status"], "SUCCESSOR_READY", consumed)
        self.assertIn("prompt_cone", consumed)
        self.assertNotIn("frontier_cone", consumed)

    def test_frontier_mutation_expands_only_frontier_cone(self):
        root, frontier, loop, baton = self._fixture()
        started = self._start(loop)
        frontier.digest = "frontier-v2"
        frontier.source_head = "sched-head-v2"
        self._advance(root, loop, started)
        derived = baton.derive(started["loop_id"])
        self.assertEqual(derived["baton"]["hydration"]["mode"], "FRONTIER_CONE")
        self.assertFalse(derived["baton"]["coordinate_delta"]["prompt_stack_changed"])
        self.assertTrue(derived["baton"]["coordinate_delta"]["frontier_changed"])

        consumed = baton.consume(
            loop_id=started["loop_id"],
            expected_baton_digest=derived["baton_digest"],
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(consumed["status"], "SUCCESSOR_READY", consumed)
        self.assertIn("frontier_cone", consumed)
        self.assertNotIn("prompt_cone", consumed)

    def test_head_motion_invalidates_consumption_without_rewriting_baton_identity(self):
        root, _, loop, baton = self._fixture()
        started = self._start(loop)
        self._advance(root, loop, started)
        before = baton.derive(started["loop_id"])
        self.assertEqual(before["status"], "BATON_READY")

        _write(root, "late.txt", "new sibling work\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "late work")
        after = baton.derive(started["loop_id"])
        self.assertEqual(after["status"], "HEAD_MOVED_REHYDRATE_REQUIRED")
        self.assertEqual(after["baton_digest"], before["baton_digest"], "freshness must not rewrite transition identity")
        self.assertFalse(after["observation"]["exact_loop_tip"])

        consumed = baton.consume(
            loop_id=started["loop_id"],
            expected_baton_digest=before["baton_digest"],
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(consumed["status"], "HEAD_MOVED_REHYDRATE_REQUIRED")
        self.assertIn("fallback", consumed)

    def test_wrong_baton_digest_fails_closed(self):
        root, _, loop, baton = self._fixture()
        started = self._start(loop)
        self._advance(root, loop, started)
        result = baton.consume(
            loop_id=started["loop_id"],
            expected_baton_digest="0" * 64,
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "STALE_BATON_HOLD")
        self.assertFalse(result["durable_return"])

    def test_no_transition_requires_full_resume(self):
        _, _, loop, baton = self._fixture()
        started = self._start(loop)
        result = baton.derive(started["loop_id"])
        self.assertEqual(result["status"], "NO_TRANSITION_FULL_REHYDRATE_REQUIRED")
        self.assertNotIn("baton_digest", result)

    def test_tool_surface_is_registered_through_prompt_runtime(self):
        self.assertEqual(SUCCESSOR_BATON_TOOL_NAMES, {"athena_successor_baton", "athena_successor_resume"})
        self.assertTrue(SUCCESSOR_BATON_TOOL_NAMES.issubset(PROMPT_RUNTIME_TOOL_NAMES))


if __name__ == "__main__":
    unittest.main()
