from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .campaign_fresh_resume import fresh_resume_branch
from .campaign_v3_ledger import PULSE_ARTIFACT
from .rehydration_campaign import (
    ACTIVE_WIDTH_STATES,
    ARTIFACT as CAMPAIGN_ARTIFACT,
    CAMPAIGN_ROOT,
    _campaign_state_digest,
)

ARTIFACT = "ATHENA.CAMPAIGN.V3.COLD.RESUME.V1"
SOURCE_ARTIFACT = "ATHENA.CAMPAIGN.V3.BRANCH.SOURCE.V1"
SOURCE_KIND = "CAMPAIGN_V3_LEDGER_RESIDUAL"

LAWS = [
    "COLD_BOOT != CHAT_MEMORY",
    "CAMPAIGN_START != SOURCE_BOUND",
    "SOURCE_BOUND != CLAIM",
    "DISCOVERY != EXECUTION_AUTHORITY",
    "AMBIGUOUS_CAMPAIGN => HOLD",
    "AMBIGUOUS_BRANCH => HOLD",
    "CAMPAIGN_STATE_DIGEST_REQUIRED",
    "CAMPAIGN_REPLAY_PASS_REQUIRED",
    "CHECKPOINT_ANCESTRY_REQUIRED",
    "SOURCE_DIGEST_REQUIRED",
    "NO_DURABLE_CAMPAIGN != EMPTY_WORLD",
    "PRIVATE_CHAIN_OF_THOUGHT != CAMPAIGN_TELEMETRY",
]


def _sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse_integrity(pulse: Mapping[str, Any]) -> bool:
    digest = str(pulse.get("pulse_digest") or "")
    if not digest:
        return False
    return digest == _sha({k: v for k, v in pulse.items() if k != "pulse_digest"})


def _source_digest(source: Mapping[str, Any]) -> str:
    return _sha({k: v for k, v in source.items() if k != "source_digest"})


def _source_valid(source: Any, branch: Mapping[str, Any] | None = None) -> bool:
    if not isinstance(source, Mapping):
        return False
    if source.get("artifact") != SOURCE_ARTIFACT or source.get("kind") != SOURCE_KIND:
        return False
    digest = str(source.get("source_digest") or "")
    if not digest or digest != _source_digest(source):
        return False
    required = ("ledger_digest", "pulse_digest", "pulse_index", "step", "horizon", "text", "compiled_at_head")
    if any(source.get(key) in (None, "") for key in required):
        return False
    if str(source.get("horizon")) not in {"I", "M", "L"}:
        return False
    if branch is not None and str(branch.get("task") or "") != str(source.get("text") or ""):
        return False
    return True


def _result(status: str, *, next_action: str, remote_sync=None, **extra: Any) -> dict[str, Any]:
    value = {
        "artifact": ARTIFACT,
        "status": status,
        "execution_authority": False,
        "work_executed": False,
        "read_only": status not in {"STARTED_SOURCE_BOUND", "STARTED_SOURCE_UNBOUND_HOLD"},
        "remote_sync": dict(remote_sync or {}),
        "shared_fresh": bool((remote_sync or {}).get("shared_frontier_verified")),
        "next": next_action,
        "laws": list(LAWS),
    }
    value.update(extra)
    return value


def start_source_bound_campaign_v3(
    runtime: Any,
    *,
    pulse: Mapping[str, Any],
    residual_step: int,
    expected_git_head: str,
    actor: str = "agent",
    max_width: int = 4,
    max_depth: int = 8,
    max_branches: int = 32,
    lease_steps: int = 4,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    """Start one durable Campaign V3 residual and event-source its source identity.

    This is deliberately a two-effect saga. If generic campaign start succeeds but
    V3 source binding fails, the started campaign remains visible for recovery and
    callers must not create a replacement campaign blindly.
    """
    failures: list[str] = []
    if pulse.get("artifact") != PULSE_ARTIFACT:
        failures.append("PULSE_ARTIFACT_INVALID")
    if not _pulse_integrity(pulse):
        failures.append("PULSE_DIGEST_INVALID")
    if pulse.get("execution_authorized") is not False:
        failures.append("PULSE_AUTHORITY_FIREWALL_MISSING")
    address = pulse.get("current_coordinates") or {}
    pulse_head = str(address.get("git_head") or "")
    if pulse_head != str(expected_git_head):
        failures.append(f"STALE_PULSE_HEAD:{pulse_head}!={expected_git_head}")
    if address.get("shared_fresh") is not True:
        failures.append("SHARED_FRESHNESS_REQUIRED")

    residual_step = int(residual_step)
    residuals = {int(value) for value in (pulse.get("residual_steps") or [])}
    if residual_step not in residuals:
        failures.append("STEP_NOT_RESIDUAL")
    action = None
    for row in pulse.get("actions") or []:
        if int(row.get("step") or -1) == residual_step:
            action = dict(row)
            break
    if action is None:
        failures.append("RESIDUAL_ACTION_MISSING")
    elif str(action.get("current_state") or "").upper() != "RESIDUAL":
        failures.append("ACTION_NOT_RESIDUAL")

    if failures:
        return _result(
            "HOLD_INVALID_START_INPUT",
            next_action="REHYDRATE_AND_RECOMPILE_CURRENT_PULSE",
            failures=failures,
            residual_step=residual_step,
            standing="CAMPAIGN_NOT_STARTED",
        )

    task = str(action.get("text") or "").strip()
    horizon = str(action.get("horizon") or "").strip()
    if not task or horizon not in {"I", "M", "L"}:
        return _result(
            "HOLD_INVALID_START_INPUT",
            next_action="REPAIR_PULSE_ACTION_IDENTITY",
            failures=["SOURCE_ACTION_INVALID"],
            residual_step=residual_step,
            standing="CAMPAIGN_NOT_STARTED",
        )

    try:
        started = runtime.start(
            goal=f"Campaign V3 pulse {int(pulse.get('pulse_index') or 0)} residual step {residual_step}",
            expected_git_head=expected_git_head,
            initial_tasks=[task],
            actor=actor,
            max_width=max_width,
            max_depth=max_depth,
            max_branches=max_branches,
            lease_steps=lease_steps,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
    except Exception as exc:
        return _result(
            "HOLD_CAMPAIGN_START_FAILED",
            next_action="REHYDRATE_CAMPAIGN_START_PRECONDITIONS",
            failures=[f"CAMPAIGN_START_FAILED:{type(exc).__name__}:{exc}"],
            residual_step=residual_step,
            standing="CAMPAIGN_NOT_STARTED",
        )

    campaign_id = str(started.get("campaign_id") or "")
    start_state_digest = str(started.get("state_digest") or "")
    start_checkpoint_head = str(started.get("checkpoint_head") or "")
    branch_id = None
    try:
        state, _ = runtime._read_state(campaign_id)
        if _campaign_state_digest(state) != state.get("state_digest") or state.get("state_digest") != start_state_digest:
            raise ValueError("started campaign state digest mismatch")
        if len(state.get("branches") or {}) != 1:
            raise ValueError("source-bound Campaign V3 start requires exactly one initial branch")
        branch_id, branch = next(iter(state["branches"].items()))
        if str(branch.get("task") or "") != task or branch.get("source") is not None:
            raise ValueError("started branch shape does not match source-binding contract")
    except Exception as exc:
        return _result(
            "STARTED_SOURCE_UNBOUND_HOLD",
            next_action="RECOVER_EXISTING_CAMPAIGN_SOURCE_BINDING",
            failures=[f"START_READBACK_FAILED:{type(exc).__name__}:{exc}"],
            campaign_id=campaign_id or None,
            branch_id=branch_id,
            start_state_digest=start_state_digest or None,
            start_checkpoint_head=start_checkpoint_head or None,
            residual_step=residual_step,
            standing="CAMPAIGN_STARTED_SOURCE_UNBOUND",
        )

    source = {
        "artifact": SOURCE_ARTIFACT,
        "kind": SOURCE_KIND,
        "ledger_digest": pulse.get("ledger_digest"),
        "pulse_digest": pulse.get("pulse_digest"),
        "pulse_index": int(pulse.get("pulse_index") or 0),
        "step": residual_step,
        "horizon": horizon,
        "text": task,
        "source_issue": pulse.get("source_issue"),
        "verification_issue": pulse.get("verification_issue"),
        "compiled_at_head": expected_git_head,
        "operational_basis_digest": pulse.get("operational_basis_digest"),
        "current_coordinates": dict(address),
    }
    source["source_digest"] = _source_digest(source)

    def bind_source(new_state: dict) -> dict:
        branch = (new_state.get("branches") or {}).get(branch_id)
        if not branch:
            raise ValueError("source branch disappeared")
        if str(branch.get("task") or "") != task:
            raise ValueError("source branch task drift")
        existing = branch.get("source")
        if existing is not None and existing != source:
            raise ValueError("source branch already carries different source identity")
        branch["source"] = dict(source)
        return new_state

    try:
        bound = runtime._mutate(
            campaign_id=campaign_id,
            expected_state_digest=start_state_digest,
            expected_checkpoint_head=start_checkpoint_head,
            actor=actor,
            event_type="CAMPAIGN_V3_SOURCE_BOUND",
            mutator=bind_source,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
    except Exception as exc:
        return _result(
            "STARTED_SOURCE_UNBOUND_HOLD",
            next_action="RECOVER_EXISTING_CAMPAIGN_SOURCE_BINDING",
            failures=[f"SOURCE_BIND_FAILED:{type(exc).__name__}:{exc}"],
            campaign_id=campaign_id,
            branch_id=branch_id,
            start_state_digest=start_state_digest,
            start_checkpoint_head=start_checkpoint_head,
            source=source,
            residual_step=residual_step,
            standing="CAMPAIGN_STARTED_SOURCE_UNBOUND",
        )

    return _result(
        "STARTED_SOURCE_BOUND",
        next_action="CLAIM_OR_BIND_SOURCE_BOUND_RESIDUAL_EXPLICITLY",
        campaign_id=campaign_id,
        branch_id=branch_id,
        start_state_digest=start_state_digest,
        start_checkpoint_head=start_checkpoint_head,
        state_digest=bound.get("state_digest"),
        checkpoint_head=bound.get("checkpoint_head"),
        source=source,
        residual_step=residual_step,
        standing="DURABLE_SOURCE_BOUND_NOT_CLAIMED",
    )


def cold_resume_campaign_v3(
    runtime: Any,
    *,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    """Discover a unique durable Campaign V3 steering branch without chat IDs."""
    try:
        mode = runtime._remote_mode(shared_remote_mode)
        remote_sync = runtime._sync(mode, remote)
    except Exception as exc:
        return _result(
            "HOLD_SHARED_FRESHNESS",
            next_action="RESTORE_SHARED_FRESHNESS",
            failures=[f"SHARED_FRESHNESS_ERROR:{type(exc).__name__}:{exc}"],
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
            next_action="START_DURABLE_SOURCE_BOUND_CAMPAIGN_V3",
            remote_sync=remote_sync,
            current_git_head=current_head,
            campaign_root=CAMPAIGN_ROOT,
            observed_namespace="ABSENT",
        )

    diagnostics: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for entry in sorted(root.iterdir(), key=lambda path: path.name):
        if not entry.is_dir() or not entry.name.startswith("RHC-"):
            continue
        campaign_id = entry.name
        try:
            state, paths = runtime._read_state(campaign_id)
        except Exception as exc:
            diagnostics.append({"campaign_id": campaign_id, "standing": "INVALID_STATE", "detail": f"{type(exc).__name__}:{exc}"})
            continue
        if state.get("artifact") != CAMPAIGN_ARTIFACT or _campaign_state_digest(state) != state.get("state_digest"):
            diagnostics.append({"campaign_id": campaign_id, "standing": "STATE_DIGEST_HOLD"})
            continue
        try:
            checkpoint = runtime._path_last_commit(paths["state"])
            if not checkpoint or not runtime._is_ancestor(checkpoint, current_head):
                diagnostics.append({"campaign_id": campaign_id, "standing": "CHECKPOINT_ANCESTRY_HOLD", "checkpoint_head": checkpoint})
                continue
            verification = runtime.verify(campaign_id)
        except Exception as exc:
            diagnostics.append({"campaign_id": campaign_id, "standing": "VERIFY_ERROR", "detail": f"{type(exc).__name__}:{exc}"})
            continue
        if verification.get("status") != "PASS":
            diagnostics.append({"campaign_id": campaign_id, "standing": "VERIFY_HOLD", "verification": verification})
            continue

        source_bound = []
        invalid_sources = []
        for branch in (state.get("branches") or {}).values():
            source = branch.get("source")
            if isinstance(source, Mapping) and source.get("kind") == SOURCE_KIND:
                if _source_valid(source, branch):
                    source_bound.append(branch)
                else:
                    invalid_sources.append(str(branch.get("branch_id")))
        if invalid_sources:
            diagnostics.append({"campaign_id": campaign_id, "standing": "INVALID_V3_SOURCE", "branch_ids": sorted(invalid_sources)})
        if not source_bound:
            diagnostics.append({"campaign_id": campaign_id, "standing": "NOT_SOURCE_BOUND_CAMPAIGN_V3"})
            continue
        resumable = [branch for branch in source_bound if branch.get("status") in ACTIVE_WIDTH_STATES]
        candidates.append({
            "campaign_id": campaign_id,
            "state": state,
            "checkpoint_head": checkpoint,
            "verification": verification,
            "source_bound_branches": source_bound,
            "resumable_branches": resumable,
        })

    if not candidates:
        return _result(
            "HOLD_NO_VALID_CAMPAIGN_V3",
            next_action="START_OR_REPAIR_DURABLE_SOURCE_BOUND_CAMPAIGN_V3",
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
            campaign_candidates=[{
                "campaign_id": row["campaign_id"],
                "state_digest": row["state"].get("state_digest"),
                "checkpoint_head": row["checkpoint_head"],
            } for row in candidates],
            diagnostics=diagnostics,
        )

    selected = candidates[0]
    resumable = selected["resumable_branches"]
    if not resumable:
        return _result(
            "DISCOVERED_NO_RESUMABLE_V3_BRANCH",
            next_action="RECONCILE_OR_RESEED_CAMPAIGN_V3_FRONTIER",
            remote_sync=remote_sync,
            current_git_head=current_head,
            campaign_id=selected["campaign_id"],
            state_digest=selected["state"].get("state_digest"),
            checkpoint_head=selected["checkpoint_head"],
            source_bound_branches=[{
                "branch_id": branch.get("branch_id"),
                "status": branch.get("status"),
                "source": branch.get("source"),
            } for branch in selected["source_bound_branches"]],
        )
    if len(resumable) != 1:
        return _result(
            "HOLD_AMBIGUOUS_BRANCH",
            next_action="RECONCILE_CAMPAIGN_V3_BRANCH_FRONTIER",
            remote_sync=remote_sync,
            current_git_head=current_head,
            campaign_id=selected["campaign_id"],
            state_digest=selected["state"].get("state_digest"),
            checkpoint_head=selected["checkpoint_head"],
            branch_ids=sorted(str(branch.get("branch_id")) for branch in resumable),
        )

    branch = resumable[0]
    branch_id = str(branch.get("branch_id") or "")
    source = dict(branch.get("source") or {})
    loop = branch.get("loop")
    discovered = {
        "campaign_id": selected["campaign_id"],
        "branch_id": branch_id,
        "state_digest": selected["state"].get("state_digest"),
        "checkpoint_head": selected["checkpoint_head"],
        "current_git_head": current_head,
        "source": source,
        "loop_id": (loop or {}).get("loop_id") if isinstance(loop, Mapping) else None,
    }
    if not isinstance(loop, Mapping) or not loop.get("loop_id"):
        return _result(
            "DISCOVERED_SOURCE_BOUND_UNBOUND_BRANCH",
            next_action="BIND_DISCOVERED_BRANCH_TO_EXPLICIT_V1_LOOP",
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
