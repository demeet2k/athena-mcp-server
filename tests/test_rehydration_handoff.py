from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.frontier_runtime import DEFAULT_SOURCE_REF
from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOL_NAMES, PromptRuntime
from athena_mcp.rehydration_handoff import (
    REHYDRATION_HANDOFF_TOOL_NAMES,
    RehydrationHandoffRuntime,
)
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
    handoff = RehydrationHandoffRuntime(git, prompt, loop)
    return root, frontier, loop, handoff


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


class RehydrationHandoffTests(unittest.TestCase):
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

    def _advance(self, root, loop, started, rel="feature.txt", text="feature v1\n", completion=None):
        _write(root, rel, text)
        _run(root, "add", ".")
        _run(root, "commit", "-m", f"work {rel}")
        return loop.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=started["checkpoint_head"],
            expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"],
            completion=completion or _completion(),
            actor="builder",
            shared_remote_mode="DISABLED",
        )

    def test_delta_handoff_is_deterministic_read_only_and_compressed(self):
        root, _, loop, handoff = self._fixture()
        started = self._start(loop)
        self._advance(root, loop, started)
        head_before = loop.git.head()

        first = handoff.derive(started["loop_id"])
        second = handoff.derive(started["loop_id"])
        self.assertEqual(first["artifact"], "ATHENA.REHYDRATION.HANDOFF.DELTA.V1")
        self.assertEqual(first["status"], "HANDOFF_READY", first)
        self.assertEqual(first["handoff_digest"], second["handoff_digest"])
        self.assertEqual(loop.git.head(), head_before, "deriving a handoff must not create Git progress")
        self.assertEqual(first["handoff"]["hydration"]["mode"], "DELTA_ONLY")

        consumed = handoff.consume(
            loop_id=started["loop_id"],
            expected_handoff_digest=first["handoff_digest"],
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(consumed["status"], "HANDOFF_RESUME_READY", consumed)
        self.assertEqual(consumed["hydration_mode"], "DELTA_ONLY")
        self.assertIn("handoff_prompt", consumed)
        self.assertNotIn("successor_prompt", consumed)
        self.assertIn("handoff_delta_prompt_chars", consumed["compression"])
        self.assertNotIn("successor_delta_prompt_chars", consumed["compression"])
        self.assertLess(consumed["compression"]["ratio"], 1.0, consumed["compression"])
        self.assertGreater(consumed["compression"]["saved_chars"], 0)

    def test_prompt_mutation_expands_only_prompt_cone(self):
        root, _, loop, handoff = self._fixture()
        started = self._start(loop)
        self._advance(root, loop, started, "prompts/ORCHESTRATION_CORE.md", "CORE V2\n")
        derived = handoff.derive(started["loop_id"])
        self.assertEqual(derived["handoff"]["hydration"]["mode"], "PROMPT_CONE")
        self.assertTrue(derived["handoff"]["coordinate_delta"]["prompt_stack_changed"])
        self.assertFalse(derived["handoff"]["coordinate_delta"]["frontier_changed"])
        consumed = handoff.consume(
            loop_id=started["loop_id"],
            expected_handoff_digest=derived["handoff_digest"],
            shared_remote_mode="DISABLED",
        )
        self.assertIn("prompt_cone", consumed)
        self.assertNotIn("frontier_cone", consumed)

    def test_frontier_mutation_expands_only_frontier_cone(self):
        root, frontier, loop, handoff = self._fixture()
        started = self._start(loop)
        frontier.digest = "frontier-v2"
        frontier.source_head = "sched-head-v2"
        self._advance(root, loop, started)
        derived = handoff.derive(started["loop_id"])
        self.assertEqual(derived["handoff"]["hydration"]["mode"], "FRONTIER_CONE")
        self.assertFalse(derived["handoff"]["coordinate_delta"]["prompt_stack_changed"])
        self.assertTrue(derived["handoff"]["coordinate_delta"]["frontier_changed"])
        consumed = handoff.consume(
            loop_id=started["loop_id"],
            expected_handoff_digest=derived["handoff_digest"],
            shared_remote_mode="DISABLED",
        )
        self.assertIn("frontier_cone", consumed)
        self.assertNotIn("prompt_cone", consumed)

    def test_head_motion_invalidates_consumption_without_rewriting_handoff_identity(self):
        root, _, loop, handoff = self._fixture()
        started = self._start(loop)
        self._advance(root, loop, started)
        before = handoff.derive(started["loop_id"])
        _write(root, "late.txt", "new sibling work\n")
        _run(root, "add", ".")
        _run(root, "commit", "-m", "late work")
        after = handoff.derive(started["loop_id"])
        self.assertEqual(after["status"], "HEAD_MOVED_REHYDRATE_REQUIRED")
        self.assertEqual(after["handoff_digest"], before["handoff_digest"])
        self.assertFalse(after["observation"]["exact_loop_tip"])
        consumed = handoff.consume(
            loop_id=started["loop_id"],
            expected_handoff_digest=before["handoff_digest"],
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(consumed["status"], "HEAD_MOVED_REHYDRATE_REQUIRED")
        self.assertIn("fallback", consumed)

    def test_routing_successor_is_transported_not_reinterpreted(self):
        root, _, loop, handoff = self._fixture()
        started = self._start(loop)
        routing = {
            "artifact": "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1",
            "status": "SELECTED",
            "selected": {"task": "Build the highest-value next slice"},
            "baton_digest": "a" * 64,
            "laws": ["ROUTING_SCORE != AUTHORITY"],
        }
        completion = _completion(successor_baton=routing, next_task="Build the highest-value next slice")
        self._advance(root, loop, started, completion=completion)
        derived = handoff.derive(started["loop_id"])
        self.assertEqual(derived["routing_successor"], routing)
        self.assertEqual(
            derived["routing_successor_bound_by"],
            derived["handoff"]["transition"]["receipt_digest"],
        )
        self.assertIn("WHAT_NEXT != WHAT_TO_REHYDRATE", derived["laws"])
        self.assertEqual(derived["handoff"]["transition"]["next_task"], routing["selected"]["task"])

    def test_wrong_handoff_digest_fails_closed(self):
        root, _, loop, handoff = self._fixture()
        started = self._start(loop)
        self._advance(root, loop, started)
        result = handoff.consume(
            loop_id=started["loop_id"],
            expected_handoff_digest="0" * 64,
            shared_remote_mode="DISABLED",
        )
        self.assertEqual(result["status"], "STALE_HANDOFF_HOLD")
        self.assertFalse(result["durable_return"])

    def test_no_transition_requires_full_resume(self):
        _, _, loop, handoff = self._fixture()
        started = self._start(loop)
        result = handoff.derive(started["loop_id"])
        self.assertEqual(result["status"], "NO_TRANSITION_FULL_REHYDRATE_REQUIRED")
        self.assertIsNone(result["handoff_digest"])

    def test_public_surface_uses_handoff_names_not_ambiguous_successor_aliases(self):
        self.assertEqual(
            REHYDRATION_HANDOFF_TOOL_NAMES,
            {"athena_rehydration_handoff_delta", "athena_rehydration_handoff_resume"},
        )
        self.assertTrue(REHYDRATION_HANDOFF_TOOL_NAMES.issubset(PROMPT_RUNTIME_TOOL_NAMES))
        self.assertNotIn("athena_successor_baton", PROMPT_RUNTIME_TOOL_NAMES)
        self.assertNotIn("athena_successor_resume", PROMPT_RUNTIME_TOOL_NAMES)


if __name__ == "__main__":
    unittest.main()
