from __future__ import annotations

import json
from typing import Any

from .campaign_fresh_resume import fresh_resume_branch
from .rehydration_campaign import (
    ACTIVE_WIDTH_STATES,
    ARTIFACT as CAMPAIGN_ARTIFACT,
    CAMPAIGN_ROOT,
    _campaign_state_digest,
)

ARTIFACT = "ATHENA.STEERING.CAMPAIGN.COLD.BOOT.V1"
STEERING_SOURCE_KIND = "STEERING_LEDGER_RESIDUAL"

LAWS = [
    "COLD_BOOT != CHAT_MEMORY",
    "DISCOVERY != CLAIM",
    "AMBIGUOUS_CAMPAIGN => HOLD",
    "AMBIGUOUS_BRANCH => HOLD",
    "CAMPAIGN_STATE_DIGEST_REQUIRED",
    "CAMPAIGN_REPLAY_PASS_REQUIRED",
    "CHECKPOINT_ANCESTRY_REQUIRED",
    "NO_DURABLE_CAMPAIGN != EMPTY_WORLD",
    "COLD_RESUME != EXECUTION_AUTHORITY",
]


def _result(status: str, *, next_action: str, remote_sync=None, **extra: Any) -> dict[str, Any]:
    out = {
        "artifact": ARTIFACT,
        "status": status,
        "read_only": True,
        "execution_authority": False,
        "remote_sync": dict(remote_sync or {}),
        "shared_fresh": bool((remote_sync or {}).get("shared_frontier_verified")),
        "next": next_action,
        "laws": list(LAWS),
    }
    out.update(extra)
    return out


def cold_resume_steering_campaign(
    runtime: Any,
    *,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    """Discover and cold-resume Campaign V3 from durable Git/runtime state only.

    No campaign ID, branch ID, state digest, checkpoint, or loop ID is supplied by
    chat. The function discovers those coordinates from the persisted campaign
    namespace, fails closed on ambiguity, and delegates a unique bound branch to
    the fresh-resume verifier.
    """

    try:
        mode = runtime._remote_mode(shared_remote_mode)
        remote_sync = runtime._sync(mode, remote)
    except Exception as exc:
        return _result(
            "HOLD_SHARED_FRESHNESS",
            next_action="RESTORE_SHARED_FRESHNESS",
            detail=f"{type(exc).__name__}:{exc}",
        )

    if not remote_sync.get("shared_frontier_verified"):
        return _result(
            "HOLD_SHARED_FRESHNESS",
            next_action="RESTORE_SHARED_FRESHNESS",
            remote_sync=remote_sync,
        )

    current_head = runtime.git.head()
    root = runtime._safe_rel(CAMPAIGN_ROOT)
    if not root.is_dir():
        return _result(
            "HOLD_NO_CAMPAIGN",
            next_action="START_DURABLE_CAMPAIGN_BEFORE_COLD_RESUME",
            remote_sync=remote_sync,
            current_git_head=current_head,
            campaign_root=CAMPAIGN_ROOT,
            observed_namespace="ABSENT",
        )

    diagnostics: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for entry in sorted(root.iterdir(), key=lambda p: p.name):
        if not entry.is_dir() or not entry.name.startswith("RHC-"):
            continue
        campaign_id = entry.name
        try:
            state, paths = runtime._read_state(campaign_id)
        except Exception as exc:
            diagnostics.append(
                {"campaign_id": campaign_id, "standing": "INVALID_STATE", "detail": f"{type(exc).__name__}:{exc}"}
            )
            continue

        if state.get("artifact") != CAMPAIGN_ARTIFACT:
            diagnostics.append({"campaign_id": campaign_id, "standing": "WRONG_ARTIFACT"})
            continue
        if _campaign_state_digest(state) != state.get("state_digest"):
            diagnostics.append({"campaign_id": campaign_id, "standing": "STATE_DIGEST_HOLD"})
            continue

        checkpoint = runtime._path_last_commit(paths["state"])
        if not checkpoint or not runtime._is_ancestor(checkpoint, current_head):
            diagnostics.append(
                {
                    "campaign_id": campaign_id,
                    "standing": "CHECKPOINT_ANCESTRY_HOLD",
                    "checkpoint_head": checkpoint,
                }
            )
            continue

        try:
            verification = runtime.verify(campaign_id)
        except Exception as exc:
            diagnostics.append(
                {"campaign_id": campaign_id, "standing": "VERIFY_ERROR", "detail": f"{type(exc).__name__}:{exc}"}
            )
            continue
        if verification.get("status") != "PASS":
            diagnostics.append(
                {
                    "campaign_id": campaign_id,
                    "standing": "VERIFY_HOLD",
                    "verification": verification,
                }
            )
            continue

        steering = []
        for branch in (state.get("branches") or {}).values():
            source = branch.get("source") or {}
            if isinstance(source, dict) and source.get("kind") == STEERING_SOURCE_KIND:
                steering.append(branch)
        if not steering:
            diagnostics.append({"campaign_id": campaign_id, "standing": "NOT_STEERING_CAMPAIGN"})
            continue

        active = [branch for branch in steering if branch.get("status") in ACTIVE_WIDTH_STATES]
        candidates.append(
            {
                "campaign_id": campaign_id,
                "state": state,
                "checkpoint_head": checkpoint,
                "verification": verification,
                "steering_branches": steering,
                "active_steering_branches": active,
            }
        )

    if not candidates:
        return _result(
            "HOLD_NO_VALID_STEERING_CAMPAIGN",
            next_action="START_OR_REPAIR_DURABLE_STEERING_CAMPAIGN",
            remote_sync=remote_sync,
            current_git_head=current_head,
            diagnostics=diagnostics,
        )

    if len(candidates) != 1:
        return _result(
            "HOLD_AMBIGUOUS_CAMPAIGN",
            next_action="RECONCILE_CAMPAIGN_IDENTITY_BEFORE_RESUME",
            remote_sync=remote_sync,
            current_git_head=current_head,
            campaign_candidates=[
                {
                    "campaign_id": row["campaign_id"],
                    "state_digest": row["state"].get("state_digest"),
                    "checkpoint_head": row["checkpoint_head"],
                }
                for row in candidates
            ],
            diagnostics=diagnostics,
        )

    selected = candidates[0]
    active = selected["active_steering_branches"]
    if not active:
        return _result(
            "DISCOVERED_NO_ACTIVE_STEERING_BRANCH",
            next_action="RECONCILE_OR_RESEED_STEERING_FRONTIER",
            remote_sync=remote_sync,
            current_git_head=current_head,
            campaign_id=selected["campaign_id"],
            state_digest=selected["state"].get("state_digest"),
            checkpoint_head=selected["checkpoint_head"],
            steering_branches=[
                {"branch_id": branch.get("branch_id"), "status": branch.get("status")}
                for branch in selected["steering_branches"]
            ],
        )

    if len(active) != 1:
        return _result(
            "HOLD_AMBIGUOUS_BRANCH",
            next_action="RECONCILE_STEERING_BRANCH_FRONTIER",
            remote_sync=remote_sync,
            current_git_head=current_head,
            campaign_id=selected["campaign_id"],
            state_digest=selected["state"].get("state_digest"),
            checkpoint_head=selected["checkpoint_head"],
            active_branch_ids=sorted(str(branch.get("branch_id")) for branch in active),
        )

    branch = active[0]
    branch_id = str(branch.get("branch_id") or "")
    loop = branch.get("loop")
    discovered = {
        "campaign_id": selected["campaign_id"],
        "branch_id": branch_id,
        "state_digest": selected["state"].get("state_digest"),
        "checkpoint_head": selected["checkpoint_head"],
        "loop_id": (loop or {}).get("loop_id") if isinstance(loop, dict) else None,
        "current_git_head": current_head,
        "source": branch.get("source"),
    }

    if not isinstance(loop, dict) or not loop.get("loop_id"):
        return _result(
            "DISCOVERED_UNBOUND_BRANCH",
            next_action="BIND_DISCOVERED_BRANCH_TO_V1_LOOP",
            remote_sync=remote_sync,
            discovered=discovered,
            diagnostics=diagnostics,
        )

    fresh = fresh_resume_branch(
        runtime,
        campaign_id=selected["campaign_id"],
        branch_id=branch_id,
        expected_state_digest=str(selected["state"].get("state_digest") or ""),
        expected_checkpoint_head=selected["checkpoint_head"],
        shared_remote_mode=shared_remote_mode,
        remote=remote,
    )
    return _result(
        "COLD_RESUME_COMPLETE" if fresh.get("status") in {"ALIGNED_ACTIVE", "HANDOFF_AVAILABLE"} else "COLD_RESUME_ROUTED",
        next_action=str(fresh.get("next") or "HONOR_FRESH_RESUME_STATUS"),
        remote_sync=remote_sync,
        discovered=discovered,
        fresh_resume=fresh,
        diagnostics=diagnostics,
    )
