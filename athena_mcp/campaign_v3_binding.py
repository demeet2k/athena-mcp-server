from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .campaign_v3_ledger import PULSE_ARTIFACT

ARTIFACT = "ATHENA.CAMPAIGN.V3.LOOP.BINDING.V1"


def _sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _git_head(runtime: Any) -> str:
    git = getattr(runtime, "git", None)
    if git is None or not hasattr(git, "head"):
        raise ValueError("runtime does not expose git.head()")
    return str(git.head())


def _pulse_integrity(pulse: Mapping[str, Any]) -> bool:
    digest = str(pulse.get("pulse_digest") or "")
    if not digest:
        return False
    basis = {k: v for k, v in pulse.items() if k != "pulse_digest"}
    return digest == _sha(basis)


def _exposed_operations(surface: Mapping[str, Any] | None) -> set[str]:
    surface = surface or {}
    names: set[str] = set()
    for key in (
        "exposed_operations",
        "frontier_tools",
        "prompt_tools",
        "rehydration_tools",
        "agent_tools",
        "campaign_tools",
    ):
        for value in surface.get(key) or []:
            if value:
                names.add(str(value))
    if surface.get("claim_tool_exposed"):
        names.add("athena_frontier_claim")
    basis = surface.get("operational_basis") or {}
    for row in basis.get("descriptors") or []:
        if not isinstance(row, Mapping) or row.get("current_exposure") is False:
            continue
        operation = row.get("operation")
        if operation:
            names.add(str(operation))
    return names


def _residual_action(pulse: Mapping[str, Any], step: int) -> Mapping[str, Any] | None:
    for row in pulse.get("actions") or []:
        if int(row.get("step") or -1) == int(step):
            return row
    return None


def _base_result(
    *,
    status: str,
    campaign_id: str,
    branch_id: str,
    residual_step: int,
    standing: str,
    failures: list[str] | None = None,
    holds: list[dict[str, Any]] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "artifact": ARTIFACT,
        "status": status,
        "campaign_id": campaign_id,
        "branch_id": branch_id,
        "residual_step": int(residual_step),
        "standing": standing,
        "failures": list(failures or []),
        "holds": list(holds or []),
        "execution_authority_granted": False,
        "work_executed": False,
        **extra,
    }


def bind_current_pulse_branch_to_loop(
    *,
    campaign_runtime: Any,
    loop_runtime: Any,
    pulse: Mapping[str, Any],
    residual_step: int,
    campaign_id: str,
    branch_id: str,
    expected_campaign_state_digest: str,
    expected_campaign_checkpoint_head: str,
    expected_git_head: str,
    agent: str,
    actor: str = "agent",
    execution_surface: Mapping[str, Any] | None = None,
    required_operation: str | None = None,
    loop_profile: str | None = None,
    source_ref: str = "athena-runtime-v3-candidate",
    remote: str = "origin",
    shared_remote_mode: str = "REQUIRED",
    fetch: bool = True,
    use_frontier: bool = True,
    max_steps: int = 64,
    max_no_progress: int = 3,
    max_prompt_chars: int = 32000,
    depth_mode: str = "deep",
    required_passes: list[str] | None = None,
    stop_conditions: list[str] | None = None,
) -> dict[str, Any]:
    """Lease one Campaign V3 residual branch and bind it to one explicit loop.

    This transaction persists coordination only. It does not execute the residual,
    create scheduler/provider authority, or convert ledger/basis state into READY.
    Material work occurs only through a later explicit RehydrationLoop advance.
    """

    failures: list[str] = []
    holds: list[dict[str, Any]] = []

    if pulse.get("artifact") != PULSE_ARTIFACT:
        failures.append("PULSE_ARTIFACT_INVALID")
    if not _pulse_integrity(pulse):
        failures.append("PULSE_DIGEST_INVALID")
    if pulse.get("execution_authorized") is not False:
        failures.append("PULSE_AUTHORITY_FIREWALL_MISSING")
    current_address = pulse.get("current_coordinates") or {}
    pulse_head = str(current_address.get("git_head") or "")
    if pulse_head != str(expected_git_head):
        failures.append(f"STALE_PULSE_HEAD:{pulse_head}!={expected_git_head}")

    action = _residual_action(pulse, int(residual_step))
    residual_set = {int(x) for x in (pulse.get("residual_steps") or [])}
    if int(residual_step) not in residual_set:
        failures.append("STEP_NOT_RESIDUAL")
    if action is None:
        failures.append("RESIDUAL_ACTION_MISSING")
    elif str(action.get("current_state") or "").upper() != "RESIDUAL":
        failures.append("ACTION_NOT_RESIDUAL")

    required_operation = str(required_operation or "").strip() or None
    if required_operation and required_operation not in _exposed_operations(execution_surface):
        holds.append(
            {
                "kind": "UNEXPOSED_REQUIRED_OPERATION",
                "required_operation": required_operation,
                "reason": "Binding-time operation exposure does not contain the required operation.",
            }
        )

    try:
        pre_lease_head = _git_head(campaign_runtime)
    except Exception as exc:
        pre_lease_head = None
        failures.append(f"GIT_HEAD_UNAVAILABLE:{type(exc).__name__}")
    if pre_lease_head and pre_lease_head != str(expected_git_head):
        failures.append(f"STALE_PRE_LEASE_HEAD:{pre_lease_head}!={expected_git_head}")

    if failures:
        return _base_result(
            status="HOLD_INVALID_BINDING_INPUT",
            campaign_id=campaign_id,
            branch_id=branch_id,
            residual_step=residual_step,
            standing="BINDING_NOT_STARTED",
            failures=failures,
            holds=holds,
            pre_lease_head=pre_lease_head,
        )
    if holds:
        return _base_result(
            status="HOLD",
            campaign_id=campaign_id,
            branch_id=branch_id,
            residual_step=residual_step,
            standing="UNEXPOSED_OPERATION_NOT_BOUND",
            holds=holds,
            pre_lease_head=pre_lease_head,
        )

    try:
        lease = campaign_runtime.claim(
            campaign_id=campaign_id,
            expected_state_digest=expected_campaign_state_digest,
            expected_checkpoint_head=expected_campaign_checkpoint_head,
            branch_id=branch_id,
            agent=agent,
            actor=actor,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
    except Exception as exc:
        return _base_result(
            status="HOLD_CAMPAIGN_LEASE_FAILED",
            campaign_id=campaign_id,
            branch_id=branch_id,
            residual_step=residual_step,
            standing="LEASE_NOT_ACQUIRED",
            failures=[f"CAMPAIGN_LEASE_FAILED:{type(exc).__name__}:{exc}"],
            pre_lease_head=pre_lease_head,
        )

    lease_state_digest = str(lease.get("state_digest") or "")
    post_lease_head = str(lease.get("checkpoint_head") or "")
    observed_post_lease_head = _git_head(campaign_runtime)
    if (
        not lease_state_digest
        or not post_lease_head
        or post_lease_head == str(pre_lease_head)
        or observed_post_lease_head != post_lease_head
    ):
        return _base_result(
            status="HOLD_CAMPAIGN_LEASE_RECEIPT",
            campaign_id=campaign_id,
            branch_id=branch_id,
            residual_step=residual_step,
            standing="LEASE_RECEIPT_INCOMPLETE",
            failures=["CAMPAIGN_LEASE_RECEIPT_INVALID_OR_HEAD_NOT_ADVANCED"],
            pre_lease_head=pre_lease_head,
            post_lease_head=post_lease_head or observed_post_lease_head,
        )

    task = str((action or {}).get("text") or "").strip()
    try:
        loop = loop_runtime.start(
            goal=task,
            task=task,
            expected_git_head=post_lease_head,
            actor=actor,
            profile=loop_profile,
            source_ref=source_ref,
            remote=remote,
            fetch=fetch,
            use_frontier=use_frontier,
            shared_remote_mode=shared_remote_mode,
            max_steps=max_steps,
            max_no_progress=max_no_progress,
            max_prompt_chars=max_prompt_chars,
            depth_mode=depth_mode,
            required_passes=required_passes,
            stop_conditions=list(stop_conditions or []),
        )
    except Exception as exc:
        recovery = {
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "agent": agent,
            "expected_state_digest": lease_state_digest,
            "expected_checkpoint_head": post_lease_head,
        }
        return _base_result(
            status="HOLD_LOOP_START_FAILED",
            campaign_id=campaign_id,
            branch_id=branch_id,
            residual_step=residual_step,
            standing="LEASED_NOT_BOUND",
            failures=[f"LOOP_START_FAILED:{type(exc).__name__}:{exc}"],
            holds=[{
                "kind": "LEASED_NOT_BOUND",
                "reason": "Campaign lease exists but loop start failed; release/recover the exact leased branch before retry.",
                "recovery": recovery,
            }],
            pre_lease_head=pre_lease_head,
            post_lease_head=post_lease_head,
            loop_start_expected_head=post_lease_head,
        )

    loop_id = str(loop.get("loop_id") or "")
    loop_state_digest = str(loop.get("state_digest") or "")
    loop_checkpoint_head = str(loop.get("checkpoint_head") or "")
    observed_loop_head = _git_head(loop_runtime)
    if (
        loop.get("status") != "STARTED"
        or not loop_id
        or not loop_state_digest
        or not loop_checkpoint_head
        or loop_checkpoint_head != observed_loop_head
    ):
        return _base_result(
            status="HOLD_LOOP_START_RECEIPT",
            campaign_id=campaign_id,
            branch_id=branch_id,
            residual_step=residual_step,
            standing="LEASED_LOOP_RECEIPT_INCOMPLETE",
            failures=["LOOP_START_RECEIPT_INVALID"],
            holds=[{
                "kind": "LEASED_LOOP_RECEIPT_INCOMPLETE",
                "reason": "Do not start a second loop until the first loop/checkpoint is reconciled.",
            }],
            loop_id=loop_id or None,
            post_lease_head=post_lease_head,
            post_loop_start_head=observed_loop_head,
        )

    try:
        bound = campaign_runtime.bind_loop(
            campaign_id=campaign_id,
            expected_state_digest=lease_state_digest,
            expected_checkpoint_head=post_lease_head,
            branch_id=branch_id,
            loop_id=loop_id,
            loop_state_digest=loop_state_digest,
            actor=actor,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
    except Exception as exc:
        return _base_result(
            status="HOLD_CAMPAIGN_BIND_FAILED",
            campaign_id=campaign_id,
            branch_id=branch_id,
            residual_step=residual_step,
            standing="LOOP_EXISTS_CAMPAIGN_UNBOUND",
            failures=[f"CAMPAIGN_BIND_FAILED:{type(exc).__name__}:{exc}"],
            holds=[{
                "kind": "LOOP_EXISTS_CAMPAIGN_UNBOUND",
                "reason": "The explicit loop already exists. Resume/rebind that loop; duplicate loop start is forbidden.",
                "loop_id": loop_id,
                "loop_state_digest": loop_state_digest,
                "loop_checkpoint_head": loop_checkpoint_head,
            }],
            loop_id=loop_id,
            pre_lease_head=pre_lease_head,
            post_lease_head=post_lease_head,
            post_loop_start_head=loop_checkpoint_head,
        )

    post_bind_head = str(bound.get("checkpoint_head") or "")
    observed_post_bind_head = _git_head(campaign_runtime)
    if not post_bind_head or post_bind_head != observed_post_bind_head or post_bind_head == loop_checkpoint_head:
        return _base_result(
            status="HOLD_BIND_RECEIPT",
            campaign_id=campaign_id,
            branch_id=branch_id,
            residual_step=residual_step,
            standing="BOUND_RECEIPT_INCOMPLETE",
            failures=["BIND_RECEIPT_INVALID_OR_HEAD_NOT_ADVANCED"],
            loop_id=loop_id,
            post_lease_head=post_lease_head,
            post_loop_start_head=loop_checkpoint_head,
            post_bind_head=post_bind_head or observed_post_bind_head,
        )

    return {
        **_base_result(
            status="BOUND",
            campaign_id=campaign_id,
            branch_id=branch_id,
            residual_step=residual_step,
            standing="BOUND_LOOP_NOT_WORK_EXECUTED",
        ),
        "task": task,
        "loop_id": loop_id,
        "loop_state_digest": loop_state_digest,
        "campaign_state_digest": str(bound.get("state_digest") or ""),
        "pre_lease_head": pre_lease_head,
        "post_lease_head": post_lease_head,
        "post_loop_start_head": loop_checkpoint_head,
        "post_bind_head": post_bind_head,
        "next": "RESUME_EXPLICIT_LOOP_AND_EXECUTE_ONE_LAWFUL_CYCLE",
        "laws": [
            "PULSE_DIGEST_VERIFIED_BEFORE_LEASE",
            "CAMPAIGN_BRANCH_LEASE != SCHEDULER_CLAIM",
            "CAMPAIGN_BINDING != WORK_EXECUTION",
            "POST_LEASE_HEAD != PRE_LEASE_HEAD",
            "BOUND_LOOP != OBSERVED_SUCCESS",
            "DUPLICATE_LOOP_ON_BIND_FAILURE = FORBIDDEN",
        ],
    }
