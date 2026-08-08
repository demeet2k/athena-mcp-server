from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOL_NAMES, PromptRuntime
from athena_mcp.rehydration_epoch import ARTIFACT, TOOL_NAME
from athena_mcp.rehydration_loop import REHYDRATION_TOOL_NAMES, RehydrationLoopRuntime


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


def _seed_shared_brain(base: Path) -> tuple[Path, Path, RehydrationLoopRuntime]:
    root = base / "agent-a"
    root.mkdir()
    _run(root, "init", "-b", "main")
    _run(root, "config", "user.name", "agent-a")
    _run(root, "config", "user.email", "agent-a@example.invalid")
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
    _run(root, "commit", "-m", "seed shared prompt brain")

    origin = base / "brain.git"
    p = subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(root, "remote", "add", "origin", str(origin))
    _run(root, "push", "-u", "origin", "main")
    git = GitBackend(root)
    return root, origin, RehydrationLoopRuntime(git, PromptRuntime(git))


def _clone(origin: Path, target: Path, actor: str) -> RehydrationLoopRuntime:
    p = subprocess.run(["git", "clone", str(origin), str(target)], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    _run(target, "config", "user.name", actor)
    _run(target, "config", "user.email", f"{actor}@example.invalid")
    git = GitBackend(target)
    return RehydrationLoopRuntime(git, PromptRuntime(git))


def _passes() -> list[dict]:
    return [
        {"kind": kind, "summary": f"{kind} observed", "evidence_refs": []}
        for kind in ("reconstruct", "retrieve", "generate", "attack", "execute", "verify", "synthesize")
    ]


def _start_epoch(runtime: RehydrationLoopRuntime, *, max_steps: int = 1, max_prompt_chars: int = 8000) -> dict:
    return runtime.start(
        goal="Continue the whole mission across bounded epochs without resetting safety budgets",
        task="Implement epoch zero material work",
        expected_git_head=runtime.git.head(),
        actor="agent-a",
        use_frontier=False,
        fetch=False,
        shared_remote_mode="REQUIRED",
        max_steps=max_steps,
        max_no_progress=3,
        max_prompt_chars=max_prompt_chars,
        depth_mode="deep",
        stop_conditions=["all mission integration tests pass on the shared-current descendant"],
    )


def _material_and_hold(
    runtime: RehydrationLoopRuntime,
    root: Path,
    loop: dict,
    *,
    filename: str,
    residual: str,
    actor: str = "agent-a",
) -> dict:
    _write(root, filename, f"material work for {filename}\n")
    _run(root, "add", filename)
    _run(root, "commit", "-m", f"material {filename}")
    _run(root, "push", "origin", "main")
    return runtime.advance(
        loop_id=loop["loop_id"],
        expected_checkpoint_head=loop["checkpoint_head"],
        expected_state_digest=loop["state_digest"],
        expected_prompt_digest=loop["prompt_digest"],
        completion={
            "status": "SUCCEEDED",
            "observed": True,
            "terminal": False,
            "hard_hold": False,
            "summary": f"completed bounded work {filename}",
            "progress_delta": 1.0,
            "passes": _passes(),
            "tests": [{"name": filename, "status": "PASS", "evidence_ref": f"test://{filename}"}],
            "evidence_refs": [f"git://{filename}"],
            "residuals": [residual],
            "next_task": None,
            "handoff_to": None,
        },
        actor=actor,
        shared_remote_mode="REQUIRED",
    )


def _roll(runtime: RehydrationLoopRuntime, hold: dict, **extra) -> dict:
    baton = hold["successor_baton"]
    return runtime.call_tool(TOOL_NAME, {
        "parent_loop_id": hold["loop_id"],
        "expected_checkpoint_head": hold["checkpoint_head"],
        "expected_state_digest": hold["state_digest"],
        "expected_successor_baton_digest": baton["baton_digest"],
        "actor": "epoch-controller",
        "shared_remote_mode": "REQUIRED",
        **extra,
    })


class RehydrationEpochRolloverTests(unittest.TestCase):
    def test_tool_is_registered_on_canonical_prompt_surface(self):
        self.assertIn(TOOL_NAME, REHYDRATION_TOOL_NAMES)
        self.assertIn(TOOL_NAME, PROMPT_RUNTIME_TOOL_NAMES)

    def test_max_step_hold_rolls_to_published_child_without_mutating_parent(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        root, origin, runtime = _seed_shared_brain(base)
        started = _start_epoch(runtime)
        parent_state_path = started["state_path"]
        parent_state_blob_before = _run(root, "rev-parse", f"{started['checkpoint_head']}:{parent_state_path}").stdout.strip()

        held = _material_and_hold(
            runtime,
            root,
            started,
            filename="epoch0.txt",
            residual="Implement epoch one material work",
        )
        self.assertEqual(held["status"], "HOLD_MAX_STEPS")
        self.assertEqual(held["successor_baton"]["status"], "SELECTED")
        self.assertIn(ARTIFACT, held["compiled_self_prompt"])
        self.assertIn(TOOL_NAME, held["compiled_self_prompt"])
        self.assertIn("HOLD_MAX_STEPS != MISSION_COMPLETE", held["compiled_self_prompt"])
        self.assertLessEqual(len(held["compiled_self_prompt"]), 8000)

        rolled = _roll(runtime, held, max_epochs=3, max_total_steps=3)
        self.assertEqual(rolled["status"], "EPOCH_STARTED", rolled)
        self.assertTrue(rolled["durable_return"])
        self.assertEqual(rolled["epoch_index"], 1)
        self.assertEqual(rolled["cumulative_steps_before"], 1)
        self.assertEqual(rolled["child_max_steps"], 1)
        self.assertEqual(rolled["max_epochs"], 3)
        self.assertEqual(rolled["max_total_steps"], 3)
        self.assertEqual(rolled["successor_task"], "Implement epoch one material work")
        self.assertNotEqual(rolled["child_loop_id"], held["loop_id"])

        shared_head = _run(root, "rev-parse", "origin/main").stdout.strip()
        self.assertEqual(shared_head, rolled["published_head"])
        parent_state_blob_after = _run(root, "rev-parse", f"{shared_head}:{parent_state_path}").stdout.strip()
        self.assertEqual(parent_state_blob_before, parent_state_blob_after)

        lineage = json.loads((root / rolled["lineage_path"]).read_text(encoding="utf-8"))
        self.assertEqual(lineage["artifact"], ARTIFACT)
        self.assertEqual(lineage["root_loop_id"], held["loop_id"])
        self.assertEqual(lineage["parent_loop_id"], held["loop_id"])
        self.assertEqual(lineage["child_loop_id"], rolled["child_loop_id"])
        self.assertEqual(lineage["epoch_index"], 1)
        self.assertEqual(lineage["cumulative_steps_before"], 1)

        cold_root = base / "cold-observer"
        cold = _clone(origin, cold_root, "cold-observer")
        resumed = cold.resume(rolled["child_loop_id"])
        self.assertEqual(resumed["status"], "RESUMED")
        self.assertTrue(resumed["shared_frontier_verified"])
        self.assertEqual(resumed["epoch"]["epoch_index"], 1)
        self.assertEqual(resumed["epoch"]["root_loop_id"], held["loop_id"])
        indexed = cold.index()
        row = next(x for x in indexed["loops"] if x["loop_id"] == rolled["child_loop_id"])
        self.assertEqual(row["epoch"]["cumulative_steps_before"], 1)

    def test_cumulative_budget_is_monotone_across_two_rollovers(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        root, _, runtime = _seed_shared_brain(base)
        started = _start_epoch(runtime)
        held0 = _material_and_hold(runtime, root, started, filename="e0.txt", residual="epoch one task")
        epoch1 = _roll(runtime, held0, max_epochs=3, max_total_steps=3)
        self.assertEqual(epoch1["status"], "EPOCH_STARTED")

        child1 = runtime.resume(epoch1["child_loop_id"])
        held1 = _material_and_hold(runtime, root, child1, filename="e1.txt", residual="epoch two task")
        self.assertEqual(held1["status"], "HOLD_MAX_STEPS")
        epoch2 = _roll(runtime, held1)
        self.assertEqual(epoch2["status"], "EPOCH_STARTED", epoch2)
        self.assertEqual(epoch2["epoch_index"], 2)
        self.assertEqual(epoch2["cumulative_steps_before"], 2)
        self.assertEqual(epoch2["max_epochs"], 3)
        self.assertEqual(epoch2["max_total_steps"], 3)
        self.assertEqual(epoch2["child_max_steps"], 1)

        child2 = runtime.resume(epoch2["child_loop_id"])
        held2 = _material_and_hold(runtime, root, child2, filename="e2.txt", residual="would require forbidden epoch three")
        exhausted = _roll(runtime, held2)
        self.assertEqual(exhausted["status"], "EPOCH_COUNT_EXHAUSTED_HOLD")
        self.assertIsNone(exhausted["child_loop_id"])
        self.assertFalse(exhausted["durable_return"])

    def test_frozen_budget_cannot_be_increased_on_later_rollover(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        root, _, runtime = _seed_shared_brain(base)
        started = _start_epoch(runtime)
        held0 = _material_and_hold(runtime, root, started, filename="root.txt", residual="child task")
        epoch1 = _roll(runtime, held0, max_epochs=4, max_total_steps=2)
        child = runtime.resume(epoch1["child_loop_id"])
        held1 = _material_and_hold(runtime, root, child, filename="child.txt", residual="more work")

        mismatch = _roll(runtime, held1, max_epochs=5, max_total_steps=3)
        self.assertEqual(mismatch["status"], "EPOCH_BUDGET_MISMATCH_HOLD")
        self.assertIsNone(mismatch["child_loop_id"])

        exhausted = _roll(runtime, held1)
        self.assertEqual(exhausted["status"], "EPOCH_TOTAL_STEP_BUDGET_EXHAUSTED_HOLD")
        self.assertIsNone(exhausted["child_loop_id"])

    def test_non_max_step_parent_and_missing_baton_fail_closed(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        root, _, runtime = _seed_shared_brain(base)
        started = _start_epoch(runtime, max_steps=2)
        fake = runtime.call_tool(TOOL_NAME, {
            "parent_loop_id": started["loop_id"],
            "expected_checkpoint_head": started["checkpoint_head"],
            "expected_state_digest": started["state_digest"],
            "expected_successor_baton_digest": "0" * 64,
            "shared_remote_mode": "REQUIRED",
        })
        self.assertEqual(fake["status"], "EPOCH_PARENT_NOT_MAX_STEPS_HOLD")

        # Reach the max step hold without self-steering, proving rollover will not
        # fabricate a successor task simply because the epoch budget ended.
        _write(root, "work1.txt", "first\n")
        _run(root, "add", "work1.txt")
        _run(root, "commit", "-m", "first")
        _run(root, "push", "origin", "main")
        step1 = runtime.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=started["checkpoint_head"],
            expected_state_digest=started["state_digest"],
            expected_prompt_digest=started["prompt_digest"],
            completion={
                "status": "SUCCEEDED", "observed": True, "terminal": False, "summary": "first",
                "passes": _passes(), "tests": [{"name": "first", "status": "PASS"}],
                "evidence_refs": ["git://work1"], "residuals": [], "next_task": "explicit second task",
            },
            shared_remote_mode="REQUIRED",
        )
        _write(root, "work2.txt", "second\n")
        _run(root, "add", "work2.txt")
        _run(root, "commit", "-m", "second")
        _run(root, "push", "origin", "main")
        step2 = runtime.advance(
            loop_id=started["loop_id"],
            expected_checkpoint_head=step1["checkpoint_head"],
            expected_state_digest=step1["state_digest"],
            expected_prompt_digest=step1["prompt_digest"],
            completion={
                "status": "SUCCEEDED", "observed": True, "terminal": False, "summary": "second",
                "passes": _passes(), "tests": [{"name": "second", "status": "PASS"}],
                "evidence_refs": ["git://work2"], "residuals": [], "next_task": "explicit third task",
            },
            shared_remote_mode="REQUIRED",
        )
        self.assertEqual(step2["status"], "HOLD_MAX_STEPS")
        self.assertIsNone(step2.get("successor_baton"))
        missing = runtime.call_tool(TOOL_NAME, {
            "parent_loop_id": step2["loop_id"],
            "expected_checkpoint_head": step2["checkpoint_head"],
            "expected_state_digest": step2["state_digest"],
            "expected_successor_baton_digest": "0" * 64,
            "shared_remote_mode": "REQUIRED",
        })
        self.assertEqual(missing["status"], "EPOCH_SUCCESSOR_MISSING_HOLD")


if __name__ == "__main__":
    unittest.main()
