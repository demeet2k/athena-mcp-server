from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .git_backend import GitBackend
from .prompt_runtime import PromptRuntime
from .rehydration_loop import RehydrationLoopRuntime

ARTIFACT = "ATHENA.SUCCESSOR.BATON.V1"
_PROMPT_META = re.compile(r"<!-- ATHENA_REHYDRATION_PROMPT_V1\n(.*?)\n-->", re.DOTALL)
_REMOTE_MODES = {"REQUIRED", "BEST_EFFORT", "DISABLED"}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    raw = value if isinstance(value, bytes) else (value.encode("utf-8") if isinstance(value, str) else _canonical(value))
    return hashlib.sha256(raw).hexdigest()


def _cone_for_path(path: str) -> str:
    if path.startswith("prompts/") or path == "policies/PROMPT_RUNTIME.md":
        return "prompt_policy"
    if path.startswith("athena_mcp/"):
        return "runtime_implementation"
    if path.startswith("tests/"):
        return "verification"
    if path.startswith("spec/"):
        return "specification"
    if path.startswith("skills/"):
        return "skill"
    if path.startswith(("developments/", "jspace/", "kc144/", "ledger/", "math/", "navigation/")):
        return "knowledge_geometry"
    return "project_work"


class SuccessorBatonRuntime:
    """Deterministic delta projection over the durable rehydration receipt chain.

    A baton is derived, not committed. This is deliberate: creating a baton must
    never become a Git commit that the parent loop can mistake for substantive work.
    """

    def __init__(
        self,
        git: GitBackend,
        prompt_runtime: PromptRuntime | None = None,
        rehydration_runtime: RehydrationLoopRuntime | None = None,
    ):
        self.git = git
        self.prompt_runtime = prompt_runtime or PromptRuntime(git)
        self.loop = rehydration_runtime or RehydrationLoopRuntime(git, self.prompt_runtime)

    @staticmethod
    def _remote_mode(value: str | None) -> str:
        mode = str(value or "REQUIRED").upper()
        if mode not in _REMOTE_MODES:
            raise ValueError("shared_remote_mode must be REQUIRED, BEST_EFFORT, or DISABLED")
        return mode

    @staticmethod
    def _prompt_metadata(path: Path) -> dict:
        match = _PROMPT_META.search(path.read_text(encoding="utf-8"))
        if not match:
            raise ValueError(f"rehydration prompt metadata missing: {path.name}")
        value = json.loads(match.group(1))
        if not isinstance(value, dict):
            raise ValueError("rehydration prompt metadata must be an object")
        return value

    def derive(self, loop_id: str) -> dict:
        verification = self.loop.verify(loop_id)
        state, paths = self.loop._read_state(loop_id)
        step = int(state.get("step_index") or 0)
        checkpoint_head = self.loop._path_last_commit(paths["state"])
        current_git_head = self.git.head()
        if verification.get("status") != "PASS":
            return {
                "status": "INTEGRITY_HOLD",
                "loop_id": loop_id,
                "verification": verification,
                "checkpoint_head": checkpoint_head,
                "current_git_head": current_git_head,
            }
        if step <= 0:
            return {
                "status": "NO_TRANSITION_FULL_REHYDRATE_REQUIRED",
                "loop_id": loop_id,
                "step_index": step,
                "verification": verification,
                "checkpoint_head": checkpoint_head,
                "current_git_head": current_git_head,
            }

        receipt_path = f"{paths['receipts']}/{step:04d}.json"
        receipt = self.loop._read_json(receipt_path)
        previous_prompt = self.loop._loop_prompt_path(
            paths, f"{paths['prompts']}/{step - 1:04d}.md", f"{step - 1:04d}.md"
        )
        current_prompt = self.loop._loop_prompt_path(paths, receipt["prompt_path"], f"{step:04d}.md")
        previous_meta = self._prompt_metadata(previous_prompt)
        current_meta = self._prompt_metadata(current_prompt)

        previous_prompt_stack = previous_meta.get("prompt_stack_digest")
        previous_frontier = previous_meta.get("frontier_digest")
        current_prompt_stack = receipt.get("prompt_stack_digest")
        current_frontier = receipt.get("frontier_digest")
        coverage = {
            "loop_chain_verified": True,
            "previous_prompt_stack_digest": "prompt_stack_digest" in previous_meta,
            "previous_frontier_digest": "frontier_digest" in previous_meta,
            "current_prompt_stack_digest": "prompt_stack_digest" in receipt,
            "current_frontier_digest": "frontier_digest" in receipt,
            "frontier_source_head_pair": False,
            "scheduler_contract_pair": False,
            "remote_witness_pair": False,
        }
        delta_covered = all(
            coverage[key]
            for key in (
                "previous_prompt_stack_digest",
                "previous_frontier_digest",
                "current_prompt_stack_digest",
                "current_frontier_digest",
            )
        )
        exact_tip = bool(checkpoint_head and checkpoint_head == current_git_head)
        prompt_changed = previous_prompt_stack != current_prompt_stack
        frontier_changed = previous_frontier != current_frontier

        path_cones: dict[str, list[str]] = {}
        for raw in receipt.get("material_work_paths") or []:
            path = str(raw)
            path_cones.setdefault(_cone_for_path(path), []).append(path)
        for key in path_cones:
            path_cones[key] = sorted(set(path_cones[key]))
        if prompt_changed:
            path_cones.setdefault("prompt_policy", [])
        if frontier_changed:
            path_cones.setdefault("frontier", [])
        completion = receipt.get("completion") or {}
        if completion.get("evidence_refs"):
            path_cones.setdefault("evidence", [])
        if completion.get("residuals"):
            path_cones.setdefault("residual", [])

        if not delta_covered:
            hydration_mode = "FULL_REHYDRATE_REQUIRED"
            required = ["full_rehydration"]
        elif not exact_tip:
            hydration_mode = "HEAD_MOVED_REHYDRATE_REQUIRED"
            required = ["shared_git", "loop_checkpoint", "full_rehydration"]
        elif prompt_changed and frontier_changed:
            hydration_mode = "PROMPT_AND_FRONTIER_CONE"
            required = ["receipt_chain", "work_delta", "prompt_policy", "frontier"]
        elif prompt_changed:
            hydration_mode = "PROMPT_CONE"
            required = ["receipt_chain", "work_delta", "prompt_policy"]
        elif frontier_changed:
            hydration_mode = "FRONTIER_CONE"
            required = ["receipt_chain", "work_delta", "frontier"]
        else:
            hydration_mode = "DELTA_ONLY"
            required = ["receipt_chain", "work_delta"]

        core = {
            "artifact": ARTIFACT,
            "loop_id": loop_id,
            "step_index": step,
            "predecessor": {
                "checkpoint_head": receipt.get("expected_checkpoint_head"),
                "state_digest": receipt.get("previous_state_digest"),
                "prompt_digest": receipt.get("previous_prompt_digest"),
                "chain_digest": receipt.get("previous_chain_digest"),
                "prompt_stack_digest": previous_prompt_stack,
                "frontier_digest": previous_frontier,
            },
            "successor": {
                "checkpoint_head": checkpoint_head,
                "work_head": receipt.get("work_head"),
                "state_digest": receipt.get("state_digest"),
                "prompt_digest": receipt.get("prompt_digest"),
                "chain_digest": receipt.get("chain_digest"),
                "prompt_stack_digest": current_prompt_stack,
                "frontier_digest": current_frontier,
            },
            "transition": {
                "receipt_path": receipt_path,
                "receipt_digest": receipt.get("receipt_digest"),
                "changed_paths": receipt.get("changed_paths") or [],
                "material_work_paths": receipt.get("material_work_paths") or [],
                "completion_status": completion.get("status"),
                "completion_summary": completion.get("summary"),
                "tests": completion.get("tests") or [],
                "evidence_refs": completion.get("evidence_refs") or [],
                "residuals": completion.get("residuals") or [],
                "next_task": completion.get("next_task") or state.get("task"),
                "handoff_to": completion.get("handoff_to"),
                "next_status": receipt.get("next_status"),
            },
            "coordinate_delta": {
                "git_work_changed": receipt.get("expected_checkpoint_head") != receipt.get("work_head"),
                "prompt_stack_changed": prompt_changed,
                "frontier_changed": frontier_changed,
                "state_changed": receipt.get("previous_state_digest") != receipt.get("state_digest"),
                "prompt_changed": receipt.get("previous_prompt_digest") != receipt.get("prompt_digest"),
                "chain_changed": receipt.get("previous_chain_digest") != receipt.get("chain_digest"),
            },
            "affected_cone": {"components": sorted(path_cones), "paths": path_cones},
            "hydration": {
                "mode": hydration_mode,
                "required": required,
                "content_delta_covered": delta_covered,
                "exact_loop_tip": exact_tip,
                "frontier_interpretation_refresh_required_before_scheduler_action": bool(
                    (state.get("source") or {}).get("use_frontier", True)
                ),
            },
            "coverage": coverage,
            "goal": state.get("goal"),
            "task": state.get("task"),
            "laws": [
                "BATON != HIGHER_AUTHORITY",
                "BATON_DIGEST != WORLD_TRUTH",
                "DERIVED_BATON != NEW_GIT_PROGRESS",
                "MISSING_COORDINATE_COVERAGE => FULL_REHYDRATE",
                "HEAD_CHANGE => REHYDRATE",
                "FRONTIER_INTERPRETATION_WITNESS_MISSING => REFRESH_BEFORE_SCHEDULER_ACTION",
            ],
        }
        digest = _sha(core)
        baton = {**core, "baton_digest": digest}
        ready = hydration_mode not in {"FULL_REHYDRATE_REQUIRED", "HEAD_MOVED_REHYDRATE_REQUIRED"}
        return {
            "status": "BATON_READY" if ready else hydration_mode,
            "baton": baton,
            "baton_digest": digest,
            "verification": verification,
            "observation": {
                "current_git_head": current_git_head,
                "checkpoint_head": checkpoint_head,
                "exact_loop_tip": exact_tip,
                "current_prompt_metadata_matches_receipt": current_meta.get("prompt_stack_digest") == current_prompt_stack
                and current_meta.get("frontier_digest") == current_frontier,
            },
        }

    @staticmethod
    def _delta_prompt(baton: dict) -> str:
        transition = baton["transition"]
        return f"""# ATHENA Successor Delta Baton — {baton['loop_id']} / step {baton['step_index']}

Baton: `{baton['baton_digest']}`
Checkpoint: `{baton['successor']['checkpoint_head']}`

## Goal
{baton.get('goal')}

## Next bounded task
{transition.get('next_task') or baton.get('task')}

## Verified predecessor delta
{transition.get('completion_summary')}

Material paths: {json.dumps(transition.get('material_work_paths') or [], sort_keys=True)}
Evidence: {json.dumps(transition.get('evidence_refs') or [], sort_keys=True)}
Residuals: {json.dumps(transition.get('residuals') or [], sort_keys=True)}

## Coordinate delta
{json.dumps(baton['coordinate_delta'], indent=2, sort_keys=True)}

## Affected cone
{json.dumps(baton['affected_cone'], indent=2, sort_keys=True)}

Hydrate only the required cone. If Git head, baton digest, prompt-stack digest, or frontier digest no longer matches, stop and rehydrate.

`BATON != AUTHORITY`; current platform/repository/user authority remains controlling.
"""

    def consume(
        self,
        *,
        loop_id: str,
        expected_baton_digest: str,
        shared_remote_mode: str = "REQUIRED",
        include_full_prompt_on_change: bool = True,
        include_frontier_on_change: bool = True,
    ) -> dict:
        mode = self._remote_mode(shared_remote_mode)
        before = self.derive(loop_id)
        if before.get("baton_digest") != expected_baton_digest:
            return {
                "status": "STALE_BATON_HOLD",
                "expected_baton_digest": expected_baton_digest,
                "current_baton_digest": before.get("baton_digest"),
                "detail": before,
                "durable_return": False,
            }
        state, _ = self.loop._read_state(loop_id)
        remote = (state.get("source") or {}).get("remote") or "origin"
        remote_sync = {"status": "DISABLED", "shared_frontier_verified": False}
        if mode != "DISABLED":
            remote_sync = self.loop.remote_sync.sync(remote)
            if mode == "REQUIRED" and not remote_sync.get("shared_frontier_verified"):
                return {
                    "status": "SHARED_FRONTIER_HOLD",
                    "baton_digest": expected_baton_digest,
                    "remote_sync": remote_sync,
                    "durable_return": False,
                }

        after = self.derive(loop_id)
        if after.get("baton_digest") != expected_baton_digest:
            return {
                "status": "STALE_BATON_AFTER_SYNC_HOLD",
                "expected_baton_digest": expected_baton_digest,
                "current_baton_digest": after.get("baton_digest"),
                "detail": after,
                "remote_sync": remote_sync,
                "durable_return": False,
            }
        if after.get("status") != "BATON_READY":
            return {
                "status": after.get("status"),
                "baton_digest": expected_baton_digest,
                "fallback": self.loop.resume(loop_id, include_prompt=True),
                "remote_sync": remote_sync,
                "durable_return": False,
            }

        baton = after["baton"]
        state, paths = self.loop._read_state(loop_id)
        context = self.loop._context(
            task=str(baton["transition"].get("next_task") or state.get("task") or ""),
            profile=state.get("profile"),
            source_ref=(state.get("source") or {}).get("source_ref"),
            remote=remote,
            fetch=bool((state.get("source") or {}).get("fetch", True)),
            use_frontier=bool((state.get("source") or {}).get("use_frontier", True)),
        )
        live_prompt = (context.get("prompt") or {}).get("prompt_stack_digest")
        live_frontier = (context.get("frontier") or {}).get("frontier_digest")
        persisted_prompt = baton["successor"].get("prompt_stack_digest")
        persisted_frontier = baton["successor"].get("frontier_digest")
        drift = {"prompt_stack": live_prompt != persisted_prompt, "frontier": live_frontier != persisted_frontier}
        if any(drift.values()):
            return {
                "status": "LIVE_COORDINATE_DRIFT_HOLD",
                "baton_digest": expected_baton_digest,
                "live_drift": drift,
                "persisted": {"prompt_stack_digest": persisted_prompt, "frontier_digest": persisted_frontier},
                "live": {"prompt_stack_digest": live_prompt, "frontier_digest": live_frontier},
                "remote_sync": remote_sync,
                "durable_return": False,
            }

        delta_prompt = self._delta_prompt(baton)
        full_prompt = self.loop._loop_prompt_path(paths, state["current_prompt_path"]).read_text(encoding="utf-8")
        result = {
            "status": "SUCCESSOR_READY",
            "loop_id": loop_id,
            "step_index": baton["step_index"],
            "baton_digest": expected_baton_digest,
            "checkpoint_head": baton["successor"].get("checkpoint_head"),
            "hydration_mode": baton["hydration"]["mode"],
            "required_hydration": baton["hydration"]["required"],
            "affected_cone": baton["affected_cone"],
            "successor_prompt": delta_prompt,
            "compression": {
                "full_rehydration_prompt_chars": len(full_prompt),
                "successor_delta_prompt_chars": len(delta_prompt),
                "saved_chars": max(0, len(full_prompt) - len(delta_prompt)),
                "ratio": (len(delta_prompt) / len(full_prompt)) if full_prompt else 1.0,
            },
            "remote_sync": remote_sync,
            "live_coordinates": {"prompt_stack_digest": live_prompt, "frontier_digest": live_frontier},
            "durable_return": bool(remote_sync.get("shared_frontier_verified")) if mode != "DISABLED" else False,
            "laws": baton["laws"],
        }
        if include_full_prompt_on_change and baton["coordinate_delta"]["prompt_stack_changed"]:
            result["prompt_cone"] = self.prompt_runtime.compile(
                task=str(baton["transition"].get("next_task") or state.get("task") or ""),
                profile=state.get("profile"),
                include_text=True,
            )
        if include_frontier_on_change and baton["coordinate_delta"]["frontier_changed"]:
            result["frontier_cone"] = context.get("frontier")
        return result

    def call_tool(self, name: str, arguments: dict):
        if name == "athena_successor_baton":
            return self.derive(arguments["loop_id"])
        if name == "athena_successor_resume":
            return self.consume(
                loop_id=arguments["loop_id"],
                expected_baton_digest=arguments["expected_baton_digest"],
                shared_remote_mode=arguments.get("shared_remote_mode", "REQUIRED"),
                include_full_prompt_on_change=arguments.get("include_full_prompt_on_change", True),
                include_frontier_on_change=arguments.get("include_frontier_on_change", True),
            )
        raise KeyError(name)


SUCCESSOR_BATON_TOOLS = [
    {
        "name": "athena_successor_baton",
        "description": "Derive a deterministic content-addressed successor baton from the latest verified rehydration transition. The baton creates no Git progress.",
        "inputSchema": {
            "type": "object",
            "required": ["loop_id"],
            "properties": {"loop_id": {"type": "string"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_successor_resume",
        "description": "Verify and consume an exact successor baton, refresh shared state, reject drift, and hydrate only the affected dependency cone; fall back to full rehydration when delta coverage is insufficient.",
        "inputSchema": {
            "type": "object",
            "required": ["loop_id", "expected_baton_digest"],
            "properties": {
                "loop_id": {"type": "string"},
                "expected_baton_digest": {"type": "string"},
                "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
                "include_full_prompt_on_change": {"type": "boolean"},
                "include_frontier_on_change": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
]
SUCCESSOR_BATON_TOOL_NAMES = {tool["name"] for tool in SUCCESSOR_BATON_TOOLS}
