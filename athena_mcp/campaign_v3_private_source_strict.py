from __future__ import annotations

from typing import Any, Mapping

from .campaign_v3_private_source import (
    bind_private_source_branch_to_loop,
    cold_resume_private_campaign_v3,
    compile_private_source_identity,
    start_private_source_bound_campaign_v3,
    validate_private_source_identity,
)

ARTIFACT = "ATHENA.CAMPAIGN.V3.PRIVATE.SOURCE.STRICT.V1"
OPAQUE_PREFIX = "opaque:"

LAWS = [
    "REAL_PRIVATE_SOURCE_CONSUMER => STRICT_ENTRYPOINT_ONLY",
    "PRIVATE_LOCATOR_DIGEST != PRIVATE_LOCATOR_TEXT",
    "FREE_FORM_PRIVATE_REF => HOLD",
    "STRICT_OPAQUE_REF = opaque:<sha256>",
    "PRIVATE_PAYLOAD != DURABLE_SOURCE_IDENTITY",
    "PAYLOAD_DIGEST_MATCH != EXECUTION_AUTHORITY",
    "OPAQUE_LOOP_BOUND != WORK_EXECUTED",
    "CAMPAIGN_SUCCESS = HOLD",
]


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def opaque_private_ref(private_locator_digest: str) -> str:
    digest = str(private_locator_digest or "").strip()
    if not _is_sha256(digest):
        raise ValueError("private_locator_digest must be exactly 64 lowercase hex characters")
    return OPAQUE_PREFIX + digest


def is_strict_private_ref(value: Any) -> bool:
    ref = str(value or "")
    return ref.startswith(OPAQUE_PREFIX) and _is_sha256(ref[len(OPAQUE_PREFIX) :])


def _result(status: str, *, next_action: str, **extra: Any) -> dict[str, Any]:
    value = {
        "artifact": ARTIFACT,
        "status": status,
        "execution_authority": False,
        "work_executed": False,
        "private_payload_disclosed": False,
        "next": next_action,
        "laws": list(LAWS),
    }
    value.update(extra)
    return value


def _validate_strict_source(source: Mapping[str, Any]) -> list[str]:
    errors = list(validate_private_source_identity(source))
    if not is_strict_private_ref(source.get("private_ref")):
        errors.append("STRICT_OPAQUE_PRIVATE_REF_REQUIRED")
    return errors


def compile_strict_private_source_identity(
    pulse: Mapping[str, Any],
    residual_step: int,
    *,
    private_locator_digest: str,
    expected_git_head: str,
) -> dict[str, Any]:
    try:
        private_ref = opaque_private_ref(private_locator_digest)
    except ValueError:
        return _result(
            "HOLD_INVALID_PRIVATE_LOCATOR_DIGEST",
            next_action="SUPPLY_SHA256_PRIVATE_LOCATOR_DIGEST",
        )
    compiled = compile_private_source_identity(
        pulse,
        residual_step,
        private_ref=private_ref,
        expected_git_head=expected_git_head,
    )
    if compiled.get("status") != "PRIVATE_SOURCE_IDENTITY_COMPILED":
        return compiled
    source = compiled.get("source") or {}
    errors = _validate_strict_source(source)
    if errors:
        return _result(
            "HOLD_STRICT_PRIVATE_SOURCE_INVALID",
            next_action="RECOMPILE_STRICT_PRIVATE_SOURCE",
            failures=errors,
        )
    return {
        **compiled,
        "artifact": ARTIFACT,
        "status": "STRICT_PRIVATE_SOURCE_IDENTITY_COMPILED",
        "strict_entrypoint": True,
        "laws": list(LAWS),
    }


def start_strict_private_source_bound_campaign_v3(
    runtime: Any,
    *,
    pulse: Mapping[str, Any],
    residual_step: int,
    private_locator_digest: str,
    expected_git_head: str,
    actor: str = "agent",
    max_width: int = 4,
    max_depth: int = 8,
    max_branches: int = 32,
    lease_steps: int = 4,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    compiled = compile_strict_private_source_identity(
        pulse,
        residual_step,
        private_locator_digest=private_locator_digest,
        expected_git_head=expected_git_head,
    )
    if compiled.get("status") != "STRICT_PRIVATE_SOURCE_IDENTITY_COMPILED":
        return compiled
    result = start_private_source_bound_campaign_v3(
        runtime,
        pulse=pulse,
        residual_step=residual_step,
        private_ref=compiled["source"]["private_ref"],
        expected_git_head=expected_git_head,
        actor=actor,
        max_width=max_width,
        max_depth=max_depth,
        max_branches=max_branches,
        lease_steps=lease_steps,
        shared_remote_mode=shared_remote_mode,
        remote=remote,
    )
    source = result.get("source") or {}
    if result.get("status") == "STARTED_PRIVATE_SOURCE_BOUND":
        errors = _validate_strict_source(source)
        if errors:
            return _result(
                "HOLD_STRICT_PRIVATE_SOURCE_INVALID_AFTER_START",
                next_action="RECONCILE_STRICT_PRIVATE_SOURCE_CAMPAIGN",
                failures=errors,
                campaign_id=result.get("campaign_id"),
                branch_id=result.get("branch_id"),
            )
    return {
        **result,
        "artifact": ARTIFACT,
        "strict_entrypoint": True,
        "laws": list(LAWS),
    }


def cold_resume_strict_private_campaign_v3(
    runtime: Any,
    *,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    resumed = cold_resume_private_campaign_v3(
        runtime,
        shared_remote_mode=shared_remote_mode,
        remote=remote,
    )
    if resumed.get("status") != "PRIVATE_CAMPAIGN_RESUMED":
        return resumed
    source = resumed.get("source") or {}
    errors = _validate_strict_source(source)
    if errors:
        return _result(
            "HOLD_NON_STRICT_PRIVATE_SOURCE_CAMPAIGN",
            next_action="RECONCILE_TO_STRICT_DIGEST_ONLY_PRIVATE_SOURCE",
            failures=errors,
            campaign_id=resumed.get("campaign_id"),
            branch_id=resumed.get("branch_id"),
        )
    return {
        **resumed,
        "artifact": ARTIFACT,
        "strict_entrypoint": True,
        "laws": list(LAWS),
    }


def bind_strict_private_source_branch_to_loop(
    campaign_runtime: Any,
    loop_runtime: Any,
    *,
    campaign_id: str,
    branch_id: str,
    expected_state_digest: str,
    expected_checkpoint_head: str,
    private_payload: str,
    agent: str = "agent",
    actor: str = "agent",
    loop_max_steps: int = 3,
    shared_remote_mode: str = "REQUIRED",
    remote: str = "origin",
) -> dict[str, Any]:
    try:
        state, _ = campaign_runtime._read_state(campaign_id)
        branch = (state.get("branches") or {}).get(branch_id) or {}
        source = branch.get("source") or {}
    except Exception as exc:
        return _result(
            "HOLD_STRICT_PRIVATE_CAMPAIGN_READ_FAILED",
            next_action="REHYDRATE_STRICT_PRIVATE_CAMPAIGN",
            failures=[f"CAMPAIGN_READ_FAILED:{type(exc).__name__}:{exc}"],
        )
    errors = _validate_strict_source(source)
    if errors:
        return _result(
            "HOLD_NON_STRICT_PRIVATE_SOURCE_CAMPAIGN",
            next_action="RECONCILE_TO_STRICT_DIGEST_ONLY_PRIVATE_SOURCE",
            failures=errors,
            campaign_id=campaign_id,
            branch_id=branch_id,
        )
    result = bind_private_source_branch_to_loop(
        campaign_runtime,
        loop_runtime,
        campaign_id=campaign_id,
        branch_id=branch_id,
        expected_state_digest=expected_state_digest,
        expected_checkpoint_head=expected_checkpoint_head,
        private_payload=private_payload,
        agent=agent,
        actor=actor,
        loop_max_steps=loop_max_steps,
        shared_remote_mode=shared_remote_mode,
        remote=remote,
    )
    return {
        **result,
        "artifact": ARTIFACT,
        "strict_entrypoint": True,
        "laws": list(LAWS),
    }
