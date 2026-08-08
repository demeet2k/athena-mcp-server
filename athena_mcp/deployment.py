from __future__ import annotations

"""Deployment contracts for ATHENA's packaged runtime.

This module describes and validates deployment intent.  It never contacts a
cluster, moves traffic, mutates a tag, or treats a release/image as empirical
or Y1 authority.  Execution belongs to an external deployment controller and
must return an independently observed receipt.
"""

import hashlib
import json
import math
import re
from typing import Any, Mapping

DEPLOYMENT_VERSION = "ATHENA.DEPLOYMENT.1"
ACTIVATION_PLAN_VERSION = "ATHENA.ACTIVATION.PLAN.1"
CANARY_ASSESSMENT_VERSION = "ATHENA.CANARY.ASSESSMENT.1"
DEFAULT_IMAGE_REPOSITORY = "ghcr.io/demeet2k/athena-mcp-server"
HTTP_ADAPTER_VERSION = "ATHENA.JSONRPC.HTTP.ADAPTER.1"

_DIGEST_IMAGE = re.compile(
    r"^(?P<repository>[a-z0-9]+(?:[._/-][a-z0-9]+)*)@sha256:(?P<digest>[0-9a-f]{64})$"
)
_TAGGED_IMAGE = re.compile(
    r"^(?P<repository>[a-z0-9]+(?:[._/-][a-z0-9]+)*):(?P<tag>[A-Za-z0-9_][A-Za-z0-9_.-]{0,127})$"
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def validate_image_ref(image_ref: str, *, require_digest: bool = True) -> dict[str, Any]:
    """Validate an OCI reference without resolving or pulling it."""

    ref = str(image_ref or "").strip()
    digest_match = _DIGEST_IMAGE.fullmatch(ref)
    tag_match = _TAGGED_IMAGE.fullmatch(ref)
    if digest_match:
        return {
            "version": DEPLOYMENT_VERSION,
            "status": "PASS",
            "image_ref": ref,
            "repository": digest_match.group("repository"),
            "digest": "sha256:" + digest_match.group("digest"),
            "immutable": True,
            "boundary": "Syntax validation does not prove the registry object exists or was deployed.",
        }
    if tag_match and not require_digest:
        return {
            "version": DEPLOYMENT_VERSION,
            "status": "PASS_WITH_MUTABLE_TAG",
            "image_ref": ref,
            "repository": tag_match.group("repository"),
            "tag": tag_match.group("tag"),
            "digest": None,
            "immutable": False,
            "boundary": "Mutable tags are admissible only for local development and never for production activation.",
        }
    expected = "repository@sha256:" + "0" * 64
    raise ValueError(
        f"image_ref must be digest-pinned ({expected})"
        if require_digest
        else "image_ref must be an OCI digest or tag reference"
    )


def manifest() -> dict[str, Any]:
    value: dict[str, Any] = {
        "version": DEPLOYMENT_VERSION,
        "state": "ACTIVATION_CAPABLE_DEPLOYMENT_NOT_IMPLIED",
        "image_repository": DEFAULT_IMAGE_REPOSITORY,
        "runtime": {
            "entrypoint": "athena-mcp-http",
            "adapter": HTTP_ADAPTER_VERSION,
            "transport_boundary": (
                "The network surface is a bounded JSON-RPC-over-HTTP adapter. "
                "It does not claim MCP Streamable HTTP or SSE semantics."
            ),
            "endpoints": {
                "rpc": {"method": "POST", "path": "/mcp", "authentication": "Bearer"},
                "liveness": {"method": "GET", "path": "/livez"},
                "readiness": {"method": "GET", "path": "/readyz"},
                "health": {"method": "GET", "path": "/healthz"},
                "metrics": {"method": "GET", "path": "/metrics"},
            },
        },
        "persistence": {
            "engine": "SQLite WAL",
            "mount": "/var/lib/athena",
            "database": "/var/lib/athena/athena.db",
            "mode": "SINGLE_WRITER",
            "active_active_supported": False,
            "backup_required_before_cutover": True,
            "law": (
                "A single SQLite database must not be mounted read-write by multiple active pods. "
                "Horizontal active-active service requires a separately implemented transactional backend."
            ),
        },
        "security": {
            "non_root": True,
            "read_only_root_filesystem": True,
            "drop_all_capabilities": True,
            "no_new_privileges": True,
            "rpc_token_required_off_loopback": True,
            "token_query_parameters_forbidden": True,
            "request_body_limit": True,
            "secrets_embedded_in_image": False,
        },
        "supply_chain": {
            "production_image_must_be_digest_pinned": True,
            "release_assets": [
                "container-attestation.json",
                "application-sbom.spdx.json",
                "deployment-manifest.yaml",
                "SHA256SUMS",
            ],
            "tag_is_not_digest": True,
            "digest_is_not_deployment_receipt": True,
        },
        "rollout": {
            "strategy": "ISOLATED_CANARY_THEN_SINGLE_WRITER_CUTOVER",
            "canary_database": "isolated fresh or snapshot-cloned database",
            "production_traffic_to_canary": "forbidden until write isolation is established",
            "cutover": "one active writer at a time",
            "rollback": "restore previous digest and pre-cutover state snapshot",
        },
        "authority_boundary": (
            "A valid deployment plan, OCI digest, health response, or canary score is not proof of "
            "production activation, semantic correctness, empirical truth, or Y1 authority."
        ),
    }
    value["manifest_digest"] = _digest(value)
    return value


def validate_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Validate an activation bundle as intent, not execution."""

    data = dict(bundle or {})
    defects: list[dict[str, str]] = []
    if data.get("schema") != "ATHENA.DEPLOYMENT.BUNDLE.1":
        defects.append({"field": "schema", "reason": "must equal ATHENA.DEPLOYMENT.BUNDLE.1"})
    image_ref = data.get("image_ref")
    image = None
    try:
        image = validate_image_ref(str(image_ref or ""), require_digest=True)
    except ValueError as exc:
        defects.append({"field": "image_ref", "reason": str(exc)})
    if data.get("transport") != HTTP_ADAPTER_VERSION:
        defects.append({"field": "transport", "reason": f"must equal {HTTP_ADAPTER_VERSION}"})
    if data.get("state_mode") != "SINGLE_WRITER":
        defects.append({"field": "state_mode", "reason": "must equal SINGLE_WRITER"})
    if not str(data.get("token_secret_ref") or "").strip():
        defects.append({"field": "token_secret_ref", "reason": "external secret reference is required"})
    if data.get("allow_insecure_http") is not False:
        defects.append({"field": "allow_insecure_http", "reason": "must be false"})
    if data.get("database_backup_witness") in {None, "", False}:
        defects.append(
            {"field": "database_backup_witness", "reason": "pre-cutover backup witness is required"}
        )
    result: dict[str, Any] = {
        "version": DEPLOYMENT_VERSION,
        "status": "PASS" if not defects else "FAIL",
        "valid": not defects,
        "defects": defects,
        "image": image,
        "bundle_digest": _digest(data),
        "boundary": "PASS validates the supplied bundle contract only; no infrastructure action was performed.",
    }
    return result


def activation_plan(
    image_ref: str,
    *,
    replicas: int = 1,
    canary_percent: int = 10,
    state_snapshot_ref: str,
    token_secret_ref: str,
    actor: str = "agent",
) -> dict[str, Any]:
    image = validate_image_ref(image_ref, require_digest=True)
    replicas = int(replicas)
    canary_percent = int(canary_percent)
    if replicas != 1:
        raise ValueError("SQLite production activation requires replicas=1")
    if not 1 <= canary_percent <= 50:
        raise ValueError("canary_percent must be between 1 and 50")
    if not str(state_snapshot_ref or "").strip():
        raise ValueError("state_snapshot_ref is required")
    if not str(token_secret_ref or "").strip():
        raise ValueError("token_secret_ref is required")
    plan: dict[str, Any] = {
        "version": ACTIVATION_PLAN_VERSION,
        "actor": str(actor),
        "status": "PLAN_ONLY",
        "image": image,
        "replicas": 1,
        "canary_percent": canary_percent,
        "state_snapshot_ref": str(state_snapshot_ref),
        "token_secret_ref": str(token_secret_ref),
        "stages": [
            {
                "ordinal": 1,
                "name": "PREFLIGHT",
                "requires": [
                    "exact image digest pull",
                    "release attestation and checksum verification",
                    "database backup witness",
                    "secret reference resolution",
                ],
            },
            {
                "ordinal": 2,
                "name": "ISOLATED_CANARY",
                "requires": [
                    "isolated database or snapshot clone",
                    "no production writes",
                    "live/readiness/RPC probes",
                    "receipt replay and schema verification",
                ],
            },
            {
                "ordinal": 3,
                "name": "CUTOVER_HOLD",
                "requires": [
                    "canary assessment PROMOTE",
                    "human or policy authorization",
                    "confirmed single-writer quiescence",
                ],
            },
            {
                "ordinal": 4,
                "name": "SINGLE_WRITER_CUTOVER",
                "requires": [
                    "stop previous writer",
                    "mount production state once",
                    "start exact digest",
                    "readyz PASS",
                ],
            },
            {
                "ordinal": 5,
                "name": "POST_ACTIVATION_VERIFY",
                "requires": [
                    "RPC initialize",
                    "schema PASS",
                    "state replay PASS",
                    "error and latency observation",
                    "activation receipt",
                ],
            },
        ],
        "rollback": {
            "triggers": [
                "readiness failure",
                "schema failure",
                "replay divergence",
                "error-rate threshold breach",
                "latency threshold breach",
                "unexpected restart",
            ],
            "action": "stop candidate, restore previous digest, restore or remount witnessed pre-cutover snapshot",
            "automatic_data_rewrite": False,
        },
        "boundary": "This object is an ordered activation contract; it neither authorizes nor performs deployment.",
    }
    plan["plan_digest"] = _digest(plan)
    return plan


def assess_canary(
    baseline: Mapping[str, Any],
    canary: Mapping[str, Any],
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare observed canary metrics without inventing absent values."""

    before = dict(baseline or {})
    after = dict(canary or {})
    limits = {
        "max_error_rate_delta": 0.01,
        "max_p95_ratio": 1.25,
        "max_restart_delta": 1,
        **dict(thresholds or {}),
    }
    required_numeric = ("error_rate", "p95_ms", "restart_count")
    missing = [
        f"baseline.{key}" for key in required_numeric if key not in before
    ] + [f"canary.{key}" for key in required_numeric if key not in after]
    required_boolean = ("ready", "schema_up_to_date", "replay_match")
    missing.extend(f"canary.{key}" for key in required_boolean if key not in after)
    if missing:
        return {
            "version": CANARY_ASSESSMENT_VERSION,
            "decision": "HOLD",
            "status": "INSUFFICIENT_OBSERVATION",
            "missing": sorted(missing),
            "boundary": "Missing metrics remain UNKNOWN and are never treated as zero or PASS.",
        }

    baseline_error = _finite_number(before["error_rate"], "baseline.error_rate")
    canary_error = _finite_number(after["error_rate"], "canary.error_rate")
    baseline_p95 = _finite_number(before["p95_ms"], "baseline.p95_ms")
    canary_p95 = _finite_number(after["p95_ms"], "canary.p95_ms")
    baseline_restarts = _finite_number(before["restart_count"], "baseline.restart_count")
    canary_restarts = _finite_number(after["restart_count"], "canary.restart_count")
    if baseline_p95 <= 0:
        raise ValueError("baseline.p95_ms must be greater than zero")

    observations = {
        "error_rate_delta": canary_error - baseline_error,
        "p95_ratio": canary_p95 / baseline_p95,
        "restart_delta": canary_restarts - baseline_restarts,
        "ready": after["ready"] is True,
        "schema_up_to_date": after["schema_up_to_date"] is True,
        "replay_match": after["replay_match"] is True,
    }
    gates = {
        "readiness": observations["ready"],
        "schema": observations["schema_up_to_date"],
        "replay": observations["replay_match"],
        "error_rate": observations["error_rate_delta"]
        <= _finite_number(limits["max_error_rate_delta"], "max_error_rate_delta"),
        "latency": observations["p95_ratio"]
        <= _finite_number(limits["max_p95_ratio"], "max_p95_ratio"),
        "restarts": observations["restart_delta"]
        <= _finite_number(limits["max_restart_delta"], "max_restart_delta"),
    }
    failed = sorted(name for name, passed in gates.items() if not passed)
    result: dict[str, Any] = {
        "version": CANARY_ASSESSMENT_VERSION,
        "decision": "PROMOTE" if not failed else "ROLLBACK",
        "status": "PASS" if not failed else "FAIL",
        "gates": {name: "PASS" if passed else "FAIL" for name, passed in gates.items()},
        "failed_gates": failed,
        "observations": observations,
        "thresholds": limits,
        "boundary": (
            "PROMOTE means the supplied observed metrics satisfy this bounded policy. "
            "It is not deployment authority and does not prove absence of unmeasured defects."
        ),
    }
    result["assessment_digest"] = _digest(result)
    return result


def benchmark() -> dict[str, Any]:
    return {
        "deployment_version": DEPLOYMENT_VERSION,
        "http_adapter_version": HTTP_ADAPTER_VERSION,
        "production_digest_required": True,
        "single_writer_state": True,
        "active_active_supported": False,
        "activation_is_external": True,
    }
