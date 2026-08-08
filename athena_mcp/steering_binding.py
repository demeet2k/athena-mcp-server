from __future__ import annotations

import hashlib
import inspect
import json
from typing import Any, Callable, Mapping

ARTIFACT = "ATHENA.STEERING.CAMPAIGN.LOOP.BINDING.V1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _git_head(runtime: Any) -> str:
    git = getattr(runtime, "git", None)
    if git is None or not hasattr(git, "head"):
        raise ValueError("runtime does not expose git.head()")
    return str(git.head())


def _result_digest(result: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = result.get(key)
        if value:
            return str(value)
    return None


def _call_compatible(
    fn: Callable[..., Any],
    semantic_values: Mapping[str, Any],
    aliases: Mapping[str, tuple[str, ...]],
    required: tuple[str, ...],
) -> Any:
    """Call an internal runtime method through a narrow semantic adapter.

    The historical campaign library is intentionally requalified as a pure
    library before public dispatch. This adapter tolerates harmless parameter
    spelling changes while failing closed if a required semantic slot cannot be
    bound to the current method signature.
    """

    signature = inspect.signature(fn)
    parameters = signature.parameters
    has_var_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values())
    call_kwargs: dict[str, Any] = {}
    missing: list[str] = []

    for semantic, value in semantic_values.items():
        names = aliases.get(semantic, (semantic,))
        chosen = next((name for name in names if name in parameters), None)
        if chosen is not None:
            call_kwargs[chosen] = value
        elif has_var_kwargs:
            call_kwargs[names[0]] = value
        elif semantic in required:
            missing.append(semantic)

    if missing:
        raise TypeError(
            f"runtime method {getattr(fn, '__name__', repr(fn))} cannot bind required semantics: {','.join(missing)}"
        )
    return fn(**call_kwargs)


def _find_candidate(compilation: Mapping[str, Any], candidate_id: str) -> Mapping[str, Any] | None:
    for candidate in compilation.get("candidates") or []:
        if str(candidate.get("candidate_id") or "") == str(candidate_id):
            return candidate
    return None


def _operation_surface(execution_surface: Mapping[str, Any] | None) -> set[str]:
    surface = execution_surface or {}
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
    return names


def bind_campaign_branch_to_loop(
    *,
    campaign_runtime: Any,
    loop_runtime: Any,
    campaign_id: str,
    branch_id: str,
    expected_campaign_digest: str,
    expected_git_head: str,
    compilation: Mapping[str, Any],
    candidate_id: str,
    actor: str = "agent",
    execution_surface: Mapping[str, Any] | None = None,
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
    """Lease one campaign branch and bind it to an explicit rehydration loop.

    This function coordinates durable state only. It does not execute the task,
    obtain a scheduler/provider claim, or treat the campaign lease as execution
    authority. Material work occurs in a later explicit rehydration-loop cycle.
    """

    failures: list[str] = []
    holds: list[dict[str, Any]] = []
    if compilation.get("status") != "RESIDUAL_CANDIDATES":
        failures.append("COMPILATION_NOT_RESIDUAL_CANDIDATES")
    candidate = _find_candidate(compilation, candidate_id)
    if candidate is None:
        failures.append("CANDIDATE_NOT_FOUND")
    elif candidate.get("standing") != "CAMPAIGN_CANDIDATE_NOT_EXECUTION_AUTHORITY":
        failures.append("CANDIDATE_STANDING_INVALID")

    compilation_address = compilation.get("current_address") or {}
    compilation_head = str(compilation_address.get("git_head") or compilation_address.get("H") or "")
    if compilation_head and compilation_head != str(expected_git_head):
        failures.append(f"STALE_COMPILATION_HEAD:{compilation_head}!={expected_git_head}")

    required_operation = str((candidate or {}).get("required_operation") or "").strip() or None
    exposed = _operation_surface(execution_surface)
    if required_operation and required_operation not in exposed:
        holds.append(
            {
                "kind": "UNEXPOSED_REQUIRED_OPERATION",
                "required_operation": required_operation,
                "reason": "Required operation is not exposed in the fresh binding-time execution surface.",
            }
        )

    try:
        pre_lease_head = _git_head(campaign_runtime)
    except Exception as exc:
        failures.append(f"GIT_HEAD_UNAVAILABLE:{type(exc).__name__}")
        pre_lease_head = None

    if pre_lease_head and pre_lease_head != str(expected_git_head):
        failures.append(f"STALE_PRE_LEASE_HEAD:{pre_lease_head}!={expected_git_head}")

    if failures:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_INVALID_BINDING_INPUT",
            "failures": failures,
            "holds": holds,
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "candidate_id": candidate_id,
            "pre_lease_head": pre_lease_head,
            "standing": "BINDING_NOT_STARTED",
            "laws": [
                "CAMPAIGN_BRANCH_LEASE != SCHEDULER_CLAIM",
                "CAMPAIGN_BINDING != WORK_EXECUTION",
                "STALE_BINDING_INPUT => NO_MUTATION",
            ],
        }
    if holds:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD",
            "failures": [],
            "holds": holds,
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "candidate_id": candidate_id,
            "pre_lease_head": pre_lease_head,
            "standing": "UNEXPOSED_OPERATION_NOT_BOUND",
            "laws": [
                "UNEXPOSED_REQUIRED_OPERATION => HOLD",
                "CAMPAIGN_BRANCH_LEASE != SCHEDULER_CLAIM",
                "CAMPAIGN_BINDING != WORK_EXECUTION",
            ],
        }

    claim_aliases = {
        "campaign_id": ("campaign_id",),
        "branch_id": ("branch_id",),
        "actor": ("actor",),
        "expected_campaign_digest": ("expected_campaign_digest", "expected_digest", "expected_state_digest"),
    }
    bind_aliases = {
        "campaign_id": ("campaign_id",),
        "branch_id": ("branch_id",),
        "actor": ("actor",),
        "expected_campaign_digest": ("expected_campaign_digest", "expected_digest", "expected_state_digest"),
        "loop_id": ("loop_id",),
        "loop_state_digest": ("loop_state_digest", "expected_loop_state_digest", "expected_loop_digest"),
        "loop_checkpoint_head": ("loop_checkpoint_head", "checkpoint_head", "expected_loop_checkpoint_head"),
    }

    try:
        claim_result = _call_compatible(
            campaign_runtime.claim_branch,
            {
                "campaign_id": campaign_id,
                "branch_id": branch_id,
                "actor": actor,
                "expected_campaign_digest": expected_campaign_digest,
            },
            claim_aliases,
            required=("campaign_id", "branch_id", "actor", "expected_campaign_digest"),
        )
    except Exception as exc:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_CAMPAIGN_LEASE_FAILED",
            "failures": [f"CAMPAIGN_LEASE_FAILED:{type(exc).__name__}:{exc}"],
            "holds": [],
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "candidate_id": candidate_id,
            "pre_lease_head": pre_lease_head,
            "standing": "LEASE_NOT_ACQUIRED",
            "laws": ["CAMPAIGN_BRANCH_LEASE != SCHEDULER_CLAIM"],
        }

    post_lease_head = _git_head(campaign_runtime)
    claim_campaign_digest = _result_digest(
        claim_result,
        "campaign_digest",
        "state_digest",
        "digest",
    )
    if not claim_campaign_digest:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_CAMPAIGN_LEASE_RECEIPT",
            "failures": ["CAMPAIGN_DIGEST_MISSING_AFTER_LEASE"],
            "holds": [],
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "candidate_id": candidate_id,
            "pre_lease_head": pre_lease_head,
            "post_lease_head": post_lease_head,
            "standing": "LEASE_RECEIPT_INCOMPLETE",
        }
    if post_lease_head == pre_lease_head:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_CAMPAIGN_LEASE_RECEIPT",
            "failures": ["CAMPAIGN_LEASE_DID_NOT_ADVANCE_GIT_HEAD"],
            "holds": [],
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "candidate_id": candidate_id,
            "pre_lease_head": pre_lease_head,
            "post_lease_head": post_lease_head,
            "standing": "LEASE_RECEIPT_INCOMPLETE",
        }

    # The campaign lease commit is causal state. The loop MUST start from this
    # post-lease head rather than the stale pre-lease compilation address.
    loop_start_kwargs = {
        "goal": str((candidate or {}).get("task") or "").strip(),
        "task": str((candidate or {}).get("task") or "").strip(),
        "expected_git_head": post_lease_head,
        "actor": actor,
        "profile": loop_profile,
        "source_ref": source_ref,
        "remote": remote,
        "fetch": fetch,
        "use_frontier": use_frontier,
        "shared_remote_mode": shared_remote_mode,
        "max_steps": max_steps,
        "max_no_progress": max_no_progress,
        "max_prompt_chars": max_prompt_chars,
        "depth_mode": depth_mode,
        "required_passes": required_passes,
        "stop_conditions": list(stop_conditions or []),
    }
    try:
        loop_result = loop_runtime.start(**loop_start_kwargs)
    except Exception as exc:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_LOOP_START_FAILED",
            "failures": [f"LOOP_START_FAILED:{type(exc).__name__}:{exc}"],
            "holds": [
                {
                    "kind": "CAMPAIGN_BRANCH_LEASE_HELD_WITHOUT_LOOP",
                    "reason": "Campaign lease succeeded but loop start failed; caller must release/recover the branch through campaign semantics before retry.",
                }
            ],
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "candidate_id": candidate_id,
            "pre_lease_head": pre_lease_head,
            "post_lease_head": post_lease_head,
            "loop_start_expected_head": post_lease_head,
            "standing": "LEASED_NOT_BOUND",
            "laws": [
                "POST_LEASE_HEAD != PRE_LEASE_HEAD",
                "CAMPAIGN_BRANCH_LEASE != WORK_EXECUTION",
                "FAILED_LOOP_START_REQUIRES_EXPLICIT_RECOVERY",
            ],
        }

    loop_id = _result_digest(loop_result, "loop_id")
    loop_state_digest = _result_digest(loop_result, "state_digest", "loop_state_digest")
    loop_checkpoint_head = _result_digest(loop_result, "checkpoint_head", "git_head")
    if not loop_id or not loop_state_digest:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_LOOP_START_RECEIPT",
            "failures": ["LOOP_ID_OR_STATE_DIGEST_MISSING"],
            "holds": [],
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "candidate_id": candidate_id,
            "post_lease_head": post_lease_head,
            "loop_result": dict(loop_result),
            "standing": "LEASED_LOOP_RECEIPT_INCOMPLETE",
        }

    post_loop_start_head = _git_head(loop_runtime)
    if loop_checkpoint_head and loop_checkpoint_head != post_loop_start_head:
        # Checkpoint head names the durable loop commit; if a wrapper returns a
        # different semantic head, force a HOLD rather than guessing ancestry.
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_LOOP_START_RECEIPT",
            "failures": [f"LOOP_CHECKPOINT_HEAD_MISMATCH:{loop_checkpoint_head}!={post_loop_start_head}"],
            "holds": [],
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "candidate_id": candidate_id,
            "post_lease_head": post_lease_head,
            "post_loop_start_head": post_loop_start_head,
            "standing": "LEASED_LOOP_RECEIPT_INCOMPLETE",
        }

    try:
        bind_result = _call_compatible(
            campaign_runtime.bind_loop,
            {
                "campaign_id": campaign_id,
                "branch_id": branch_id,
                "actor": actor,
                "expected_campaign_digest": claim_campaign_digest,
                "loop_id": loop_id,
                "loop_state_digest": loop_state_digest,
                "loop_checkpoint_head": post_loop_start_head,
            },
            bind_aliases,
            required=(
                "campaign_id",
                "branch_id",
                "actor",
                "expected_campaign_digest",
                "loop_id",
                "loop_state_digest",
            ),
        )
    except Exception as exc:
        return {
            "artifact": ARTIFACT,
            "status": "HOLD_CAMPAIGN_BIND_FAILED",
            "failures": [f"CAMPAIGN_BIND_FAILED:{type(exc).__name__}:{exc}"],
            "holds": [
                {
                    "kind": "LOOP_STARTED_BUT_CAMPAIGN_UNBOUND",
                    "loop_id": loop_id,
                    "loop_state_digest": loop_state_digest,
                    "reason": "Explicit loop exists but campaign bind failed; recover by fresh campaign resume and bind/reconcile rather than starting a duplicate loop.",
                }
            ],
            "campaign_id": campaign_id,
            "branch_id": branch_id,
            "candidate_id": candidate_id,
            "loop_id": loop_id,
            "loop_state_digest": loop_state_digest,
            "pre_lease_head": pre_lease_head,
            "post_lease_head": post_lease_head,
            "post_loop_start_head": post_loop_start_head,
            "standing": "LOOP_EXISTS_CAMPAIGN_UNBOUND",
            "laws": ["DUPLICATE_LOOP_ON_BIND_FAILURE = FORBIDDEN"],
        }

    post_bind_head = _git_head(campaign_runtime)
    bind_campaign_digest = _result_digest(bind_result, "campaign_digest", "state_digest", "digest")
    return {
        "artifact": ARTIFACT,
        "status": "BOUND",
        "failures": [],
        "holds": [],
        "campaign_id": campaign_id,
        "branch_id": branch_id,
        "candidate_id": candidate_id,
        "candidate_task": str((candidate or {}).get("task") or "").strip(),
        "campaign_digest_after_lease": claim_campaign_digest,
        "campaign_digest_after_bind": bind_campaign_digest,
        "loop_id": loop_id,
        "loop_state_digest": loop_state_digest,
        "pre_lease_head": pre_lease_head,
        "post_lease_head": post_lease_head,
        "loop_start_expected_head": post_lease_head,
        "post_loop_start_head": post_loop_start_head,
        "post_bind_head": post_bind_head,
        "git_transition_digest": _sha(
            {
                "pre_lease_head": pre_lease_head,
                "post_lease_head": post_lease_head,
                "post_loop_start_head": post_loop_start_head,
                "post_bind_head": post_bind_head,
            }
        ),
        "execution_authority_granted": False,
        "work_executed": False,
        "standing": "BOUND_LOOP_NOT_WORK_EXECUTED",
        "next": "RESUME_EXPLICIT_LOOP_AND_EXECUTE_ONE_LAWFUL_CYCLE",
        "laws": [
            "CAMPAIGN_BRANCH_LEASE != SCHEDULER_CLAIM",
            "CAMPAIGN_BINDING != WORK_EXECUTION",
            "POST_LEASE_HEAD != PRE_LEASE_HEAD",
            "LOOP_START_USES_POST_LEASE_HEAD",
            "BOUND_LOOP != OBSERVED_SUCCESS",
            "MATERIAL_WORK_REQUIRES_LATER_EXPLICIT_LOOP_CYCLE",
        ],
    }
