from __future__ import annotations

from typing import Any, Mapping

from .rehydration_campaign import _baton_valid

ARTIFACT = "ATHENA.CAMPAIGN.FRESH.RESUME.V1"

TERMINAL_LOOP_STATES = {"COMPLETE", "HOLD_MAX_STEPS", "HOLD_NO_PROGRESS", "ABORTED"}

LAWS = [
    "FRESH_RESUME != EXECUTION_AUTHORITY",
    "BOUND_LOOP != FRESH_LOOP",
    "LOCAL_INTEGRITY_PASS != SHARED_FRONTIER_FRESHNESS",
    "LOOP_DRIFT => SYNC_BRANCH_REQUIRED",
    "HANDOFF_AVAILABLE != CLAIM",
    "TERMINAL_LOOP != CAMPAIGN_SUCCESS",
    "REMOTE_SYNC != TARGET_EXECUTION_AUTHORITY",
    "READBACK != MUTATION",
]


def _base_result(
    *,
    status: str,
    campaign_id: str,
    branch_id: str,
    next_action: str,
    detail: str | None = None,
    remote_sync: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "artifact": ARTIFACT,
        "status": status,
        "campaign_id": campaign_id,
        "branch_id": branch_id,
        "read_only": True,
        "execution_authority": False,
        "shared_fresh": bool((remote_sync or {}).get("shared_frontier_verified")),
        "remote_sync": dict(remote_sync or {}),
        "next": next_action,
        "laws": list(LAWS),
    }
    if detail:
        result["detail"] = detail
    return result


def _hold(
    *,
    status: str,
    campaign_id: str,
    branch_id: str,
    next_action: str,
    detail: str | None = None,
    remote_sync: Mapping[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    result = _base_result(
        status=status,
        campaign_id=campaign_id,
        branch_id=branch_id,
        next_action=next_action,
        detail=detail,
        remote_sync=remote_sync,
    )
    result.update(extra)
    return result


def fresh_resume_branch(
    runtime: Any,
    *,
    campaign_id: str,
    branch_id: str,
    expected_state_digest: str,
    expected_checkpoint_head: str,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    """Compose campaign + bound-loop readback into a shared-fresh resume receipt.

    This function does not claim, bind, sync, advance, reconcile, or execute work.
    It only observes the supplied campaign checkpoint, refreshes shared Git state,
    verifies that the campaign did not move during that refresh, replays the bound
    V1 loop integrity chain, and reports the next lawful routing action.
    """

    try:
        before_state, before_paths = runtime._read_state(campaign_id)
    except Exception as exc:
        return _hold(
            status="HOLD_CAMPAIGN_READ",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REPAIR_CAMPAIGN_READBACK",
            detail=f"{type(exc).__name__}:{exc}",
        )

    try:
        runtime._assert_state(before_state, expected_state_digest)
    except Exception as exc:
        return _hold(
            status="HOLD_CAMPAIGN_STATE",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REHYDRATE_CAMPAIGN_STATE",
            detail=f"{type(exc).__name__}:{exc}",
        )

    before_checkpoint = runtime._path_last_commit(before_paths["state"])
    if before_checkpoint != expected_checkpoint_head:
        return _hold(
            status="HOLD_CAMPAIGN_CHECKPOINT",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REHYDRATE_CAMPAIGN_CHECKPOINT",
            detail=f"expected={expected_checkpoint_head};current={before_checkpoint}",
            campaign_checkpoint_head=before_checkpoint,
        )

    try:
        mode = runtime._remote_mode(shared_remote_mode)
        remote_sync = runtime._sync(mode, remote)
    except Exception as exc:
        return _hold(
            status="HOLD_SHARED_FRESHNESS",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="RESTORE_SHARED_FRESHNESS",
            detail=f"{type(exc).__name__}:{exc}",
        )

    if not remote_sync.get("shared_frontier_verified"):
        return _hold(
            status="HOLD_SHARED_FRESHNESS",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="RESTORE_SHARED_FRESHNESS",
            detail="shared frontier was not independently verified",
            remote_sync=remote_sync,
        )

    try:
        after_state, after_paths = runtime._read_state(campaign_id)
        after_checkpoint = runtime._path_last_commit(after_paths["state"])
    except Exception as exc:
        return _hold(
            status="HOLD_CAMPAIGN_READ_AFTER_SYNC",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REHYDRATE_CAMPAIGN_STATE",
            detail=f"{type(exc).__name__}:{exc}",
            remote_sync=remote_sync,
        )

    if (
        after_state.get("state_digest") != expected_state_digest
        or after_checkpoint != expected_checkpoint_head
    ):
        return _hold(
            status="HOLD_CAMPAIGN_STATE_MOVED",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REHYDRATE_MOVED_CAMPAIGN",
            remote_sync=remote_sync,
            expected_state_digest=expected_state_digest,
            current_state_digest=after_state.get("state_digest"),
            expected_checkpoint_head=expected_checkpoint_head,
            current_checkpoint_head=after_checkpoint,
        )

    current_head = runtime.git.head()
    if not after_checkpoint or not runtime._is_ancestor(after_checkpoint, current_head):
        return _hold(
            status="HOLD_CAMPAIGN_ANCESTRY",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REHYDRATE_OR_REBASE_CAMPAIGN",
            remote_sync=remote_sync,
            campaign_checkpoint_head=after_checkpoint,
            current_git_head=current_head,
        )

    branch = (after_state.get("branches") or {}).get(branch_id)
    if not branch:
        return _hold(
            status="HOLD_BRANCH_MISSING",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REHYDRATE_CAMPAIGN_FRONTIER",
            remote_sync=remote_sync,
            campaign_checkpoint_head=after_checkpoint,
            current_git_head=current_head,
        )

    bound = branch.get("loop")
    if not isinstance(bound, dict) or not bound.get("loop_id"):
        return _hold(
            status="HOLD_NO_BOUND_LOOP",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="BIND_V1_LOOP_BEFORE_RESUME",
            remote_sync=remote_sync,
            campaign_checkpoint_head=after_checkpoint,
            current_git_head=current_head,
            branch_status=branch.get("status"),
        )

    loop_id = str(bound["loop_id"])
    try:
        loop_resume = runtime.loop_runtime.resume(loop_id, include_prompt=False)
    except Exception as exc:
        return _hold(
            status="HOLD_LOOP_READ",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REPAIR_LOOP_READBACK",
            detail=f"{type(exc).__name__}:{exc}",
            remote_sync=remote_sync,
            loop_id=loop_id,
        )

    if loop_resume.get("status") != "RESUMED":
        return _hold(
            status="HOLD_LOOP_INTEGRITY",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REPAIR_LOOP_STATE_OR_PROMPT",
            remote_sync=remote_sync,
            loop_id=loop_id,
            loop_resume=loop_resume,
        )

    try:
        loop_verify = runtime.loop_runtime.verify(loop_id)
    except Exception as exc:
        return _hold(
            status="HOLD_LOOP_VERIFY",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REPAIR_LOOP_REPLAY",
            detail=f"{type(exc).__name__}:{exc}",
            remote_sync=remote_sync,
            loop_id=loop_id,
        )

    if loop_verify.get("status") != "PASS":
        return _hold(
            status="HOLD_LOOP_VERIFY",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REPAIR_LOOP_REPLAY",
            remote_sync=remote_sync,
            loop_id=loop_id,
            loop_verify=loop_verify,
        )

    try:
        loop_state, loop_paths = runtime.loop_runtime._read_state(loop_id)
        loop_checkpoint = runtime.loop_runtime._path_last_commit(loop_paths["state"])
    except Exception as exc:
        return _hold(
            status="HOLD_LOOP_READ_AFTER_VERIFY",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REHYDRATE_LOOP_STATE",
            detail=f"{type(exc).__name__}:{exc}",
            remote_sync=remote_sync,
            loop_id=loop_id,
        )

    if not loop_checkpoint or not runtime._is_ancestor(loop_checkpoint, current_head):
        return _hold(
            status="HOLD_LOOP_ANCESTRY",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REHYDRATE_OR_REBASE_BOUND_LOOP",
            remote_sync=remote_sync,
            loop_id=loop_id,
            loop_checkpoint_head=loop_checkpoint,
            current_git_head=current_head,
        )

    observed_loop = {
        "loop_id": loop_id,
        "state_digest": loop_state.get("state_digest"),
        "chain_digest": loop_state.get("chain_digest"),
        "checkpoint_head": loop_checkpoint,
        "step_index": loop_state.get("step_index"),
        "status": loop_state.get("status"),
    }
    drift_fields = [
        key
        for key in (
            "loop_id",
            "state_digest",
            "chain_digest",
            "checkpoint_head",
            "step_index",
            "status",
        )
        if bound.get(key) != observed_loop.get(key)
    ]
    if drift_fields:
        return _hold(
            status="SYNC_BRANCH_REQUIRED",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="CALL_CAMPAIGN_SYNC_BRANCH_THEN_RETRY",
            remote_sync=remote_sync,
            campaign_checkpoint_head=after_checkpoint,
            current_git_head=current_head,
            branch_status=branch.get("status"),
            bound_loop=dict(bound),
            observed_loop=observed_loop,
            drift_fields=drift_fields,
            loop_verify=loop_verify,
        )

    completion = loop_state.get("last_completion") or {}
    baton = completion.get("successor_baton")
    loop_status = str(loop_state.get("status") or "")

    if loop_status == "ACTIVE":
        status = "ALIGNED_ACTIVE"
        next_action = "CONTINUE_BOUND_LOOP"
    elif loop_status == "COMPLETE" and _baton_valid(baton):
        status = "HANDOFF_AVAILABLE"
        next_action = "ROUTE_SUCCESSOR_BATON"
    elif loop_status == "COMPLETE":
        status = "ALIGNED_COMPLETE_NO_HANDOFF"
        next_action = "RECONCILE_OR_SUPPLY_SUCCESSOR"
    elif loop_status in TERMINAL_LOOP_STATES:
        status = "ALIGNED_TERMINAL_HOLD"
        next_action = "RECONCILE_TERMINAL_LOOP"
    else:
        return _hold(
            status="HOLD_LOOP_STATUS",
            campaign_id=campaign_id,
            branch_id=branch_id,
            next_action="REHYDRATE_LOOP_STATUS",
            remote_sync=remote_sync,
            loop_id=loop_id,
            loop_status=loop_status,
        )

    result = _base_result(
        status=status,
        campaign_id=campaign_id,
        branch_id=branch_id,
        next_action=next_action,
        remote_sync=remote_sync,
    )
    result.update(
        {
            "campaign": {
                "state_digest": expected_state_digest,
                "checkpoint_head": after_checkpoint,
                "current_git_head": current_head,
                "branch_status": branch.get("status"),
            },
            "loop": observed_loop,
            "loop_verify": loop_verify,
            "successor_baton": baton if _baton_valid(baton) else None,
        }
    )
    return result
