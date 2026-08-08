from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from .rehydration_loop import (
    REHYDRATION_TOOLS,
    REHYDRATION_TOOL_NAMES,
    RehydrationLoopRuntime,
    _sha,
    _state_digest,
    _utcnow,
)

ARTIFACT = "ATHENA.REHYDRATION.EPOCH.V1"
TOOL_NAME = "athena_rehydration_epoch_rollover"


def _bounded(value: Any, name: str, lo: int, hi: int) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if not lo <= result <= hi:
        raise ValueError(f"{name} must be between {lo} and {hi}")
    return result


def _lineage_path(loop_id: str) -> str:
    return f"prompts/rehydration/{loop_id}/epoch.json"


def _digest_without(value: dict, key: str) -> str:
    return _sha({k: v for k, v in value.items() if k != key})


def _read_epoch(runtime: RehydrationLoopRuntime, loop_id: str) -> dict | None:
    path = runtime._safe_rel(_lineage_path(loop_id))
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid epoch lineage for {loop_id}: {exc}") from exc
    if value.get("artifact") != ARTIFACT or value.get("child_loop_id") != loop_id:
        raise ValueError(f"invalid epoch lineage identity for {loop_id}")
    if value.get("lineage_digest") != _digest_without(value, "lineage_digest"):
        raise ValueError(f"tampered epoch lineage for {loop_id}")
    return value


def _children_for_parent(runtime: RehydrationLoopRuntime, parent_loop_id: str) -> list[dict]:
    base = runtime._safe_rel("prompts/rehydration")
    if not base.is_dir():
        return []
    children: list[dict] = []
    for path in sorted(base.glob("*/epoch.json")):
        child_loop_id = path.parent.name
        lineage = _read_epoch(runtime, child_loop_id)
        if lineage and lineage.get("parent_loop_id") == parent_loop_id:
            children.append(lineage)
    return children


def _baton_digest(baton: dict) -> str:
    return _sha({k: v for k, v in baton.items() if k != "baton_digest"})


def _hold(status: str, *, parent_loop_id: str, detail: dict | None = None, remote_sync: dict | None = None) -> dict:
    return {
        "artifact": ARTIFACT,
        "status": status,
        "parent_loop_id": parent_loop_id,
        "child_loop_id": None,
        "durable_return": False,
        "remote_sync": remote_sync,
        "detail": dict(detail or {}),
        "laws": [
            "HOLD_MAX_STEPS != MISSION_COMPLETE",
            "EPOCH_ROLLOVER != BUDGET_RESET",
            "OLD_EPOCH_IMMUTABLE",
            "ONE_PARENT_EPOCH -> AT_MOST_ONE_SHARED_CHILD",
            "AMBIGUOUS_SUCCESSOR => HOLD",
            "UNVERIFIED_SHARED_FRONTIER => HOLD",
        ],
    }


def _existing_child_result(
    runtime: RehydrationLoopRuntime,
    lineage: dict,
    *,
    remote_sync: dict,
    mode: str,
) -> dict:
    child_loop_id = lineage["child_loop_id"]
    child_state, child_paths = runtime._read_state(child_loop_id)
    child_checkpoint = runtime._path_last_commit(child_paths["state"])
    prompt_text = child_paths["prompt"].read_text(encoding="utf-8")
    durable = bool(remote_sync.get("shared_frontier_verified")) if mode != "DISABLED" else False
    return {
        "artifact": ARTIFACT,
        "status": "EPOCH_ALREADY_ROLLED",
        "root_loop_id": lineage["root_loop_id"],
        "parent_loop_id": lineage["parent_loop_id"],
        "child_loop_id": child_loop_id,
        "epoch_index": lineage["epoch_index"],
        "cumulative_steps_before": lineage["cumulative_steps_before"],
        "child_max_steps": lineage["child_max_steps"],
        "max_epochs": lineage["max_epochs"],
        "max_total_steps": lineage["max_total_steps"],
        "successor_task": lineage["successor_task"],
        "successor_baton_digest": lineage["parent_successor_baton_digest"],
        "lineage_path": _lineage_path(child_loop_id),
        "lineage_digest": lineage["lineage_digest"],
        "child_checkpoint_head": child_checkpoint,
        "published_head": runtime.git.head(),
        "child_state_digest": child_state["state_digest"],
        "child_prompt_digest": child_state["current_prompt_digest"],
        "compiled_self_prompt": prompt_text,
        "remote_sync": remote_sync,
        "remote_publish": None,
        "durable_return": durable,
        "terminal": False,
        "reused_existing_child": True,
        "laws": list(lineage.get("laws") or []) + ["IDEMPOTENT_PARENT_ROLLOVER_REUSES_EXISTING_CHILD"],
    }


def rollover(
    runtime: RehydrationLoopRuntime,
    *,
    parent_loop_id: str,
    expected_checkpoint_head: str,
    expected_state_digest: str,
    expected_successor_baton_digest: str,
    actor: str = "agent",
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
    max_epochs: int | None = None,
    max_total_steps: int | None = None,
) -> dict:
    """Create or reuse one bounded descendant epoch from a verified max-step parent."""

    mode = runtime._remote_mode(shared_remote_mode)
    if mode == "DISABLED":
        remote_sync = {"status": "DISABLED", "remote": remote, "shared_frontier_verified": False}
    else:
        remote_sync = runtime.remote_sync.sync(remote)
        if not remote_sync.get("shared_frontier_verified"):
            return _hold(
                "EPOCH_SHARED_FRONTIER_HOLD",
                parent_loop_id=parent_loop_id,
                remote_sync=remote_sync,
                detail={"law": "EPOCH_ROLLOVER_REQUIRES_SHARED_CURRENT_PARENT"},
            )

    parent_state, parent_paths = runtime._read_state(parent_loop_id)
    if _state_digest(parent_state) != parent_state.get("state_digest"):
        return _hold("EPOCH_PARENT_INTEGRITY_HOLD", parent_loop_id=parent_loop_id, remote_sync=remote_sync)
    if parent_state.get("state_digest") != expected_state_digest:
        return _hold(
            "STALE_EPOCH_PARENT_STATE",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"expected_state_digest": expected_state_digest, "current_state_digest": parent_state.get("state_digest")},
        )
    parent_checkpoint = runtime._path_last_commit(parent_paths["state"])
    if parent_checkpoint != expected_checkpoint_head:
        return _hold(
            "STALE_EPOCH_PARENT_CHECKPOINT",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"expected_checkpoint_head": expected_checkpoint_head, "current_checkpoint_head": parent_checkpoint},
        )
    if parent_state.get("status") != "HOLD_MAX_STEPS":
        return _hold(
            "EPOCH_PARENT_NOT_MAX_STEPS_HOLD",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"parent_status": parent_state.get("status")},
        )

    verified = runtime.verify(parent_loop_id, shared_remote_mode="DISABLED")
    if verified.get("status") != "PASS":
        return _hold(
            "EPOCH_PARENT_VERIFY_HOLD",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"verify": verified},
        )

    completion = parent_state.get("last_completion") or {}
    baton = completion.get("successor_baton")
    if not isinstance(baton, dict):
        return _hold("EPOCH_SUCCESSOR_MISSING_HOLD", parent_loop_id=parent_loop_id, remote_sync=remote_sync)
    actual_baton_digest = _baton_digest(baton)
    if baton.get("baton_digest") != actual_baton_digest:
        return _hold("EPOCH_SUCCESSOR_TAMPER_HOLD", parent_loop_id=parent_loop_id, remote_sync=remote_sync)
    if actual_baton_digest != expected_successor_baton_digest:
        return _hold(
            "STALE_EPOCH_SUCCESSOR_BATON",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"expected_baton_digest": expected_successor_baton_digest, "current_baton_digest": actual_baton_digest},
        )
    if baton.get("status") != "SELECTED" or not isinstance(baton.get("selected"), dict):
        return _hold(
            "EPOCH_SUCCESSOR_SELECTION_HOLD",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"baton_status": baton.get("status"), "ties": baton.get("ties") or []},
        )
    successor_task = str((baton.get("selected") or {}).get("task") or "").strip()
    if not successor_task:
        return _hold("EPOCH_SUCCESSOR_EMPTY_HOLD", parent_loop_id=parent_loop_id, remote_sync=remote_sync)

    # Sequential or stale-agent retries must not fork a completed parent. A clean
    # stale checkout will have fast-forwarded above; it now sees the sibling child
    # sidecar and reuses that exact descendant.
    existing_children = _children_for_parent(runtime, parent_loop_id)
    if len(existing_children) > 1:
        return _hold(
            "EPOCH_PARENT_FORK_HOLD",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"children": [x["child_loop_id"] for x in existing_children]},
        )
    if len(existing_children) == 1:
        existing = existing_children[0]
        if (
            existing.get("parent_state_digest") != parent_state.get("state_digest")
            or existing.get("parent_checkpoint_head") != parent_checkpoint
            or existing.get("parent_successor_baton_digest") != actual_baton_digest
            or existing.get("successor_task") != successor_task
        ):
            return _hold(
                "EPOCH_EXISTING_CHILD_MISMATCH_HOLD",
                parent_loop_id=parent_loop_id,
                remote_sync=remote_sync,
                detail={"child_loop_id": existing.get("child_loop_id")},
            )
        if max_epochs is not None and int(max_epochs) != int(existing["max_epochs"]):
            return _hold(
                "EPOCH_BUDGET_MISMATCH_HOLD",
                parent_loop_id=parent_loop_id,
                remote_sync=remote_sync,
                detail={"field": "max_epochs", "frozen": existing["max_epochs"], "requested": int(max_epochs)},
            )
        if max_total_steps is not None and int(max_total_steps) != int(existing["max_total_steps"]):
            return _hold(
                "EPOCH_BUDGET_MISMATCH_HOLD",
                parent_loop_id=parent_loop_id,
                remote_sync=remote_sync,
                detail={"field": "max_total_steps", "frozen": existing["max_total_steps"], "requested": int(max_total_steps)},
            )
        return _existing_child_result(runtime, existing, remote_sync=remote_sync, mode=mode)

    parent_epoch = _read_epoch(runtime, parent_loop_id)
    parent_steps = int(parent_state.get("step_index") or 0)
    parent_max_steps = int((parent_state.get("budget") or {}).get("max_steps") or 0)
    if parent_steps < parent_max_steps:
        return _hold(
            "EPOCH_PARENT_STEP_ACCOUNTING_HOLD",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"step_index": parent_steps, "max_steps": parent_max_steps},
        )

    if parent_epoch is None:
        root_loop_id = parent_loop_id
        parent_epoch_index = 0
        cumulative_before_parent = 0
        frozen_max_epochs = _bounded(max_epochs if max_epochs is not None else 8, "max_epochs", 2, 16)
        default_total = min(4096, max(parent_max_steps, parent_max_steps * frozen_max_epochs))
        frozen_max_total_steps = _bounded(
            max_total_steps if max_total_steps is not None else default_total,
            "max_total_steps",
            1,
            4096,
        )
        budget_origin = "INITIAL_ROLLOVER"
    else:
        root_loop_id = parent_epoch["root_loop_id"]
        parent_epoch_index = int(parent_epoch["epoch_index"])
        cumulative_before_parent = int(parent_epoch["cumulative_steps_before"])
        frozen_max_epochs = int(parent_epoch["max_epochs"])
        frozen_max_total_steps = int(parent_epoch["max_total_steps"])
        budget_origin = "INHERITED"
        if max_epochs is not None and int(max_epochs) != frozen_max_epochs:
            return _hold(
                "EPOCH_BUDGET_MISMATCH_HOLD",
                parent_loop_id=parent_loop_id,
                remote_sync=remote_sync,
                detail={"field": "max_epochs", "frozen": frozen_max_epochs, "requested": int(max_epochs)},
            )
        if max_total_steps is not None and int(max_total_steps) != frozen_max_total_steps:
            return _hold(
                "EPOCH_BUDGET_MISMATCH_HOLD",
                parent_loop_id=parent_loop_id,
                remote_sync=remote_sync,
                detail={"field": "max_total_steps", "frozen": frozen_max_total_steps, "requested": int(max_total_steps)},
            )

    cumulative_steps_before_child = cumulative_before_parent + parent_steps
    child_epoch_index = parent_epoch_index + 1
    if child_epoch_index >= frozen_max_epochs:
        return _hold(
            "EPOCH_COUNT_EXHAUSTED_HOLD",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"next_epoch_index": child_epoch_index, "max_epochs": frozen_max_epochs},
        )
    remaining_total_steps = frozen_max_total_steps - cumulative_steps_before_child
    if remaining_total_steps <= 0:
        return _hold(
            "EPOCH_TOTAL_STEP_BUDGET_EXHAUSTED_HOLD",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"cumulative_steps": cumulative_steps_before_child, "max_total_steps": frozen_max_total_steps},
        )
    child_max_steps = min(parent_max_steps, remaining_total_steps)
    if child_max_steps <= 0:
        return _hold("EPOCH_CHILD_BUDGET_ZERO_HOLD", parent_loop_id=parent_loop_id, remote_sync=remote_sync)

    current_head = runtime.git.head()
    if not runtime._is_ancestor(parent_checkpoint, current_head):
        return _hold(
            "EPOCH_PARENT_FORK_HOLD",
            parent_loop_id=parent_loop_id,
            remote_sync=remote_sync,
            detail={"parent_checkpoint": parent_checkpoint, "current_head": current_head},
        )

    child_start = runtime.start(
        goal=parent_state["goal"],
        task=successor_task,
        expected_git_head=current_head,
        actor=actor,
        profile=parent_state.get("profile"),
        source_ref=(parent_state.get("source") or {}).get("source_ref"),
        remote=remote,
        fetch=bool((parent_state.get("source") or {}).get("fetch", True)),
        use_frontier=bool((parent_state.get("source") or {}).get("use_frontier", True)),
        shared_remote_mode="DISABLED",
        max_steps=child_max_steps,
        max_no_progress=int((parent_state.get("budget") or {}).get("max_no_progress") or 3),
        max_prompt_chars=int((parent_state.get("budget") or {}).get("max_prompt_chars") or 32000),
        depth_mode=(parent_state.get("depth_policy") or {}).get("mode") or "deep",
        required_passes=list((parent_state.get("depth_policy") or {}).get("required_passes") or []),
        stop_conditions=list(parent_state.get("stop_conditions") or []),
    )
    child_loop_id = child_start["loop_id"]
    lineage = {
        "artifact": ARTIFACT,
        "root_loop_id": root_loop_id,
        "parent_loop_id": parent_loop_id,
        "child_loop_id": child_loop_id,
        "parent_epoch_index": parent_epoch_index,
        "epoch_index": child_epoch_index,
        "cumulative_steps_before": cumulative_steps_before_child,
        "parent_steps_consumed": parent_steps,
        "child_max_steps": child_max_steps,
        "remaining_total_steps_at_start": remaining_total_steps,
        "max_epochs": frozen_max_epochs,
        "max_total_steps": frozen_max_total_steps,
        "budget_origin": budget_origin,
        "parent_state_digest": parent_state["state_digest"],
        "parent_chain_digest": parent_state["chain_digest"],
        "parent_checkpoint_head": parent_checkpoint,
        "parent_successor_baton_digest": actual_baton_digest,
        "successor_task": successor_task,
        "created_from_shared_head": current_head,
        "child_start_checkpoint_head": child_start["checkpoint_head"],
        "child_start_state_digest": child_start["state_digest"],
        "child_start_prompt_digest": child_start["prompt_digest"],
        "created_at": _utcnow(),
        "laws": [
            "HOLD_MAX_STEPS != MISSION_COMPLETE",
            "EPOCH_ROLLOVER != BUDGET_RESET",
            "OLD_EPOCH_IMMUTABLE",
            "ONE_PARENT_EPOCH -> AT_MOST_ONE_SHARED_CHILD",
            "CUMULATIVE_STEP_BUDGET_MONOTONE",
            "EPOCH_COUNT_BUDGET_MONOTONE",
            "SUCCESSOR_BATON_BINDS_CHILD_TASK",
        ],
    }
    lineage["lineage_digest"] = _digest_without(lineage, "lineage_digest")
    lineage_path = _lineage_path(child_loop_id)
    lineage_commit = runtime.prompt_runtime._commit_files(
        child_start["checkpoint_head"],
        {lineage_path: json.dumps(lineage, indent=2, sort_keys=True, ensure_ascii=False) + "\n"},
        actor,
        f"record rehydration epoch lineage {child_loop_id}",
    )
    publish = runtime._publish_after_write(mode, remote, lineage_commit["head"])
    durable = bool(publish.get("shared_frontier_verified")) if mode != "DISABLED" else False
    status = "EPOCH_STARTED" if mode == "DISABLED" or durable else "EPOCH_PUBLISH_HOLD"
    return {
        "artifact": ARTIFACT,
        "status": status,
        "root_loop_id": root_loop_id,
        "parent_loop_id": parent_loop_id,
        "child_loop_id": child_loop_id,
        "epoch_index": child_epoch_index,
        "cumulative_steps_before": cumulative_steps_before_child,
        "child_max_steps": child_max_steps,
        "max_epochs": frozen_max_epochs,
        "max_total_steps": frozen_max_total_steps,
        "successor_task": successor_task,
        "successor_baton_digest": actual_baton_digest,
        "lineage_path": lineage_path,
        "lineage_digest": lineage["lineage_digest"],
        "child_checkpoint_head": child_start["checkpoint_head"],
        "published_head": lineage_commit["head"],
        "child_state_digest": child_start["state_digest"],
        "child_prompt_digest": child_start["prompt_digest"],
        "compiled_self_prompt": child_start["compiled_self_prompt"],
        "remote_sync": remote_sync,
        "remote_publish": publish,
        "durable_return": durable,
        "terminal": False,
        "reused_existing_child": False,
        "laws": lineage["laws"],
    }


EPOCH_TOOL = {
    "name": TOOL_NAME,
    "description": (
        "Roll a verified HOLD_MAX_STEPS rehydration loop into one unique bounded descendant epoch without resetting cumulative "
        "mission budgets. Requires an exact selected successor baton; the old epoch remains immutable and stale retries reuse "
        "the existing child rather than forking the mission."
    ),
    "inputSchema": {
        "type": "object",
        "required": [
            "parent_loop_id",
            "expected_checkpoint_head",
            "expected_state_digest",
            "expected_successor_baton_digest",
        ],
        "properties": {
            "parent_loop_id": {"type": "string"},
            "expected_checkpoint_head": {"type": "string"},
            "expected_state_digest": {"type": "string"},
            "expected_successor_baton_digest": {"type": "string"},
            "actor": {"type": "string"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
            "remote": {"type": "string"},
            "max_epochs": {"type": "integer", "minimum": 2, "maximum": 16},
            "max_total_steps": {"type": "integer", "minimum": 1, "maximum": 4096},
        },
        "additionalProperties": False,
    },
}


def install_epoch_rollover(runtime_cls=RehydrationLoopRuntime, tool_list=None) -> None:
    if getattr(runtime_cls, "_athena_epoch_rollover_v1_registered", False):
        return

    tools = REHYDRATION_TOOLS if tool_list is None else tool_list
    if TOOL_NAME not in REHYDRATION_TOOL_NAMES:
        tools.append(deepcopy(EPOCH_TOOL))
        REHYDRATION_TOOL_NAMES.add(TOOL_NAME)

    original_call = runtime_cls.call_tool
    original_render = runtime_cls._render_prompt
    original_resume = runtime_cls.resume
    original_index = runtime_cls.index

    def call_tool_with_epoch(self, name, a):
        if name == TOOL_NAME:
            try:
                return rollover(
                    self,
                    parent_loop_id=a["parent_loop_id"],
                    expected_checkpoint_head=a["expected_checkpoint_head"],
                    expected_state_digest=a["expected_state_digest"],
                    expected_successor_baton_digest=a["expected_successor_baton_digest"],
                    actor=a.get("actor", "agent"),
                    shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"),
                    remote=a.get("remote", "origin"),
                    max_epochs=a.get("max_epochs"),
                    max_total_steps=a.get("max_total_steps"),
                )
            except Exception as exc:
                return {
                    "artifact": ARTIFACT,
                    "status": "EPOCH_ERROR_HOLD",
                    "parent_loop_id": a.get("parent_loop_id"),
                    "durable_return": False,
                    "error": str(exc),
                }
        return original_call(self, name, a)

    def render_prompt_with_epoch(self, state, context, previous_completion):
        prompt = original_render(self, state, context, previous_completion)
        if state.get("status") != "HOLD_MAX_STEPS" or ARTIFACT in prompt:
            return prompt
        completion = state.get("last_completion") or {}
        baton = completion.get("successor_baton") or {}
        selected = baton.get("selected") or {}
        section = f"""\n## Bounded epoch boundary\n\n`{ARTIFACT}`\n\n- `HOLD_MAX_STEPS != MISSION_COMPLETE`. This loop reached its bounded epoch cap; do not erase the cap and do not ask the human to press NEXT solely for ordinary continuation.\n- If `successor_baton.status == SELECTED`, call `{TOOL_NAME}` with this loop's exact checkpoint/state/baton identities. The runtime creates or reuses one unique bounded descendant epoch with frozen cumulative budgets.\n- Ambiguous/missing successor, shared-frontier failure, epoch-count exhaustion, total-step exhaustion, or detected parent fork remains a true HOLD.\n- Never reset cumulative steps or epoch count to manufacture more budget.\n\nSelected successor task: {json.dumps(selected.get('task'), ensure_ascii=False)}\nSuccessor baton digest: {json.dumps(baton.get('baton_digest'), ensure_ascii=False)}\n"""
        prompt = prompt + section
        max_chars = int((state.get("budget") or {}).get("max_prompt_chars") or 32000)
        if len(prompt) > max_chars:
            raise ValueError(f"compiled self-prompt exceeds max_prompt_chars={max_chars} after epoch-boundary augmentation")
        return prompt

    def resume_with_epoch(self, *args, **kwargs):
        result = original_resume(self, *args, **kwargs)
        loop_id = kwargs.get("loop_id") if "loop_id" in kwargs else args[0] if args else None
        if loop_id:
            result["epoch"] = _read_epoch(self, loop_id)
        return result

    def index_with_epoch(self, *args, **kwargs):
        result = original_index(self, *args, **kwargs)
        for row in result.get("loops") or []:
            loop_id = row.get("loop_id")
            row["epoch"] = _read_epoch(self, loop_id) if loop_id else None
        return result

    runtime_cls.call_tool = call_tool_with_epoch
    runtime_cls._render_prompt = render_prompt_with_epoch
    runtime_cls.resume = resume_with_epoch
    runtime_cls.index = index_with_epoch
    runtime_cls._athena_epoch_rollover_v1_registered = True
