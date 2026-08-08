from __future__ import annotations

from typing import Any, Mapping, MutableSet

from .common import KernelError, parse_time, require_exact_keys, require_nonempty_string, require_positive_int, require_safe_id

CLAIM_KEYS = {
    "schema_version",
    "run_id",
    "node_id",
    "worker_role",
    "attempt",
    "policy_commit",
    "claimed_at",
    "lease_expires_at",
    "input_snapshot_digest",
    "production_authority",
}


class ClaimAlreadyExists(KernelError):
    """The fixed provider path already exists; this worker lost the claim race."""


def claim_path(run_id: str, node_id: str) -> str:
    safe_run = require_safe_id(run_id, "claim.run_id")
    safe_node = require_safe_id(node_id, "claim.node_id")
    return f"runtime/runs/{safe_run}/claims/{safe_node}.json"


def make_claim(
    *,
    run_id: str,
    node_id: str,
    worker_role: str,
    attempt: int,
    policy_commit: str,
    claimed_at: str,
    lease_expires_at: str,
    input_snapshot_digest: str,
    production_authority: str = "HOLD",
) -> dict[str, Any]:
    claim = {
        "schema_version": "CLAIM_V1",
        "run_id": run_id,
        "node_id": node_id,
        "worker_role": worker_role,
        "attempt": attempt,
        "policy_commit": policy_commit,
        "claimed_at": claimed_at,
        "lease_expires_at": lease_expires_at,
        "input_snapshot_digest": input_snapshot_digest,
        "production_authority": production_authority,
    }
    validate_claim(claim)
    return claim


def validate_claim(claim: Mapping[str, Any]) -> dict[str, Any]:
    require_exact_keys(claim, CLAIM_KEYS, "claim")
    if claim["schema_version"] != "CLAIM_V1":
        raise KernelError("claim.schema_version: expected CLAIM_V1")
    require_safe_id(claim["run_id"], "claim.run_id")
    require_safe_id(claim["node_id"], "claim.node_id")
    require_safe_id(claim["worker_role"], "claim.worker_role")
    require_positive_int(claim["attempt"], "claim.attempt")
    require_nonempty_string(claim["policy_commit"], "claim.policy_commit")
    claimed = parse_time(claim["claimed_at"], "claim.claimed_at")
    expires = parse_time(claim["lease_expires_at"], "claim.lease_expires_at")
    if expires <= claimed:
        raise KernelError("claim.lease_expires_at: must follow claimed_at")
    digest = require_nonempty_string(claim["input_snapshot_digest"], "claim.input_snapshot_digest")
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise KernelError("claim.input_snapshot_digest: expected lowercase SHA-256")
    if claim["production_authority"] not in {"HOLD", "AUTHORIZED"}:
        raise KernelError("claim.production_authority: unsupported value")
    return dict(claim)


def acquire_claim(existing_paths: MutableSet[str], claim: Mapping[str, Any]) -> dict[str, Any]:
    """Model the provider create-if-absent boundary used by the GitHub file write.

    In scheduled operation, the caller performs one create-file request at the returned
    fixed path.  A provider 'already exists' response is a lost race, not a retryable
    success.  This dependency-free model makes the boundary deterministic in tests.
    """

    validated = validate_claim(claim)
    path = claim_path(validated["run_id"], validated["node_id"])
    if path in existing_paths:
        raise ClaimAlreadyExists(f"claim path already exists: {path}")
    existing_paths.add(path)
    return {
        "effect": "CLAIM_ACQUIRED",
        "path": path,
        "claim": validated,
        "provider_operation": "CREATE_FILE_IF_ABSENT",
    }
