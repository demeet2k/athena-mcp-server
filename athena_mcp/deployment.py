from __future__ import annotations

"""Pure deployment contracts for the canonical ATHENA runtime.

DEPLOYMENT.2 validates immutable activation intent, compiles compare-and-swap
cutover plans, evaluates externally observed canaries, and verifies activation
receipts.  It never contacts a registry or cluster, mutates traffic, or upgrades
an image/plan/health response into execution, truth, or canonical authority.
"""

import hashlib
import json
import math
import re
from typing import Any, Mapping

DEPLOYMENT_VERSION = "ATHENA.DEPLOYMENT.2"
ACTIVATION_PLAN_VERSION = "ATHENA.ACTIVATION.PLAN.2"
CANARY_ASSESSMENT_VERSION = "ATHENA.CANARY.ASSESSMENT.2"
ACTIVATION_RECEIPT_VERSION = "ATHENA.ACTIVATION.RECEIPT.1"
HTTP_ADAPTER_VERSION = "ATHENA.JSONRPC.HTTP.ADAPTER.2"
DEFAULT_IMAGE_REPOSITORY = "ghcr.io/demeet2k/athena-mcp-server"

_DIGEST_IMAGE = re.compile(
    r"^(?P<repository>[a-z0-9]+(?:[._/-][a-z0-9]+)*)@sha256:(?P<digest>[0-9a-f]{64})$"
)
_TAGGED_IMAGE = re.compile(
    r"^(?P<repository>[a-z0-9]+(?:[._/-][a-z0-9]+)*):(?P<tag>[A-Za-z0-9_][A-Za-z0-9_.-]{0,127})$"
)
_SHA256 = re.compile(r"^(?:sha256:)?(?P<digest>[0-9a-f]{64})$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric and non-boolean")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _nonempty(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required")
    return text


def _sha256_ref(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    match = _SHA256.fullmatch(text)
    if not match:
        raise ValueError(f"{field} must be a sha256 digest")
    return "sha256:" + match.group("digest")


def _git_sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    if not _GIT_SHA.fullmatch(text):
        raise ValueError(f"{field} must be a full 40-character Git SHA")
    return text


def validate_image_ref(image_ref: str, *, require_digest: bool = True) -> dict[str, Any]:
    """Validate OCI reference syntax without resolving or pulling it."""

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
            "boundary": "Syntax validation does not prove registry existence, provenance, or activation.",
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
            "boundary": "Mutable tags are local-development coordinates, never production activation identities.",
        }
    raise ValueError("image_ref must be digest-pinned as repository@sha256:<64 lowercase hex>")


def manifest() -> dict[str, Any]:
    value: dict[str, Any] = {
        "version": DEPLOYMENT_VERSION,
        "state": "ACTIVATION_CAPABLE_DEPLOYMENT_NOT_IMPLIED",
        "image_repository": DEFAULT_IMAGE_REPOSITORY,
        "runtime": {
            "canonical_server_root": "athena_mcp.server.Server",
            "http_entrypoint": "athena_mcp.http_host:main",
            "adapter": HTTP_ADAPTER_VERSION,
            "transport_boundary": (
                "Bounded one-request/one-response JSON-RPC over HTTP. It does not claim MCP "
                "Streamable HTTP, SSE, resumable sessions, or transport semantics it does not implement."
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
            "replicas": 1,
            "active_active_supported": False,
            "backup_required_before_cutover": True,
            "law": (
                "Exactly one process may own a writable SQLite state volume. Active-active service "
                "requires a separately implemented transactional backend and migration proof."
            ),
        },
        "security": {
            "non_root": True,
            "read_only_root_filesystem": True,
            "drop_all_capabilities": True,
            "no_new_privileges": True,
            "rpc_token_required_off_loopback": True,
            "minimum_token_bytes": 24,
            "token_query_parameters_forbidden": True,
            "bounded_request_body": True,
            "external_tls_termination_required": True,
            "secrets_embedded_in_image": False,
        },
        "supply_chain": {
            "production_image_must_be_digest_pinned": True,
            "source_head_must_equal_image_attestation_head": True,
            "required_references": [
                "release_attestation_ref",
                "sbom_ref",
                "state_snapshot_ref",
                "state_snapshot_digest",
            ],
            "tag_is_not_digest": True,
            "digest_is_not_provenance": True,
            "provenance_is_not_activation_receipt": True,
        },
        "rollout": {
            "strategy": "ISOLATED_CANARY_THEN_CAS_SINGLE_WRITER_CUTOVER",
            "canary_database": "isolated fresh or snapshot-cloned database",
            "production_writes_to_canary": "forbidden before cutover",
            "minimum_observation_window_seconds": 60,
            "minimum_sample_count": 30,
            "cutover": "compare-and-swap from the observed current image and witnessed state snapshot",
            "rollback": "restore previous exact digest and pre-cutover snapshot",
        },
        "receipt": {
            "schema": ACTIVATION_RECEIPT_VERSION,
            "must_bind": [
                "plan_digest",
                "image_ref",
                "source_head",
                "state_snapshot_ref",
                "state_snapshot_digest",
                "cutover_authority_ref",
                "observations",
            ],
        },
        "authority_boundary": (
            "A valid plan, OCI digest, attestation, health response, canary decision, or receipt shape "
            "is not by itself proof of production activation, semantic correctness, empirical truth, or Y1 authority."
        ),
    }
    value["manifest_digest"] = _digest(value)
    return value


def validate_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Validate activation intent while preserving infrastructure as external."""

    data = dict(bundle or {})
    defects: list[dict[str, str]] = []

    def capture(field: str, fn) -> Any:
        try:
            return fn()
        except ValueError as exc:
            defects.append({"field": field, "reason": str(exc)})
            return None

    if data.get("schema") != "ATHENA.DEPLOYMENT.BUNDLE.2":
        defects.append({"field": "schema", "reason": "must equal ATHENA.DEPLOYMENT.BUNDLE.2"})
    image = capture("image_ref", lambda: validate_image_ref(data.get("image_ref"), require_digest=True))
    current_image = None
    if data.get("expected_current_image_ref") not in {None, ""}:
        current_image = capture(
            "expected_current_image_ref",
            lambda: validate_image_ref(data.get("expected_current_image_ref"), require_digest=True),
        )
    source_head = capture("source_head", lambda: _git_sha(data.get("source_head"), "source_head"))
    image_source_head = capture(
        "image_source_head", lambda: _git_sha(data.get("image_source_head"), "image_source_head")
    )
    if source_head and image_source_head and source_head != image_source_head:
        defects.append({"field": "image_source_head", "reason": "must equal source_head"})
    snapshot_digest = capture(
        "state_snapshot_digest",
        lambda: _sha256_ref(data.get("state_snapshot_digest"), "state_snapshot_digest"),
    )
    for field in (
        "state_snapshot_ref",
        "token_secret_ref",
        "release_attestation_ref",
        "sbom_ref",
        "database_backup_witness",
    ):
        capture(field, lambda field=field: _nonempty(data.get(field), field))
    if data.get("transport") != HTTP_ADAPTER_VERSION:
        defects.append({"field": "transport", "reason": f"must equal {HTTP_ADAPTER_VERSION}"})
    if data.get("state_mode") != "SINGLE_WRITER":
        defects.append({"field": "state_mode", "reason": "must equal SINGLE_WRITER"})
    if data.get("replicas") != 1:
        defects.append({"field": "replicas", "reason": "SQLite activation requires replicas=1"})
    if data.get("allow_insecure_http") is not False:
        defects.append({"field": "allow_insecure_http", "reason": "must be false"})

    result: dict[str, Any] = {
        "version": DEPLOYMENT_VERSION,
        "status": "PASS" if not defects else "FAIL",
        "valid": not defects,
        "defects": defects,
        "image": image,
        "expected_current_image": current_image,
        "source_head": source_head,
        "image_source_head": image_source_head,
        "state_snapshot_digest": snapshot_digest,
        "bundle_digest": _digest(data),
        "boundary": "PASS validates supplied intent only; no registry, cluster, traffic, secret, or state mutation occurred.",
    }
    return result


def activation_plan(
    image_ref: str,
    *,
    source_head: str,
    state_snapshot_ref: str,
    state_snapshot_digest: str,
    token_secret_ref: str,
    release_attestation_ref: str,
    sbom_ref: str,
    expected_current_image_ref: str | None = None,
    replicas: int = 1,
    canary_percent: int = 10,
    actor: str = "agent",
) -> dict[str, Any]:
    image = validate_image_ref(image_ref, require_digest=True)
    source = _git_sha(source_head, "source_head")
    snapshot_ref = _nonempty(state_snapshot_ref, "state_snapshot_ref")
    snapshot_digest = _sha256_ref(state_snapshot_digest, "state_snapshot_digest")
    token_ref = _nonempty(token_secret_ref, "token_secret_ref")
    attestation_ref = _nonempty(release_attestation_ref, "release_attestation_ref")
    sbom = _nonempty(sbom_ref, "sbom_ref")
    current = (
        validate_image_ref(expected_current_image_ref, require_digest=True)
        if expected_current_image_ref
        else None
    )
    if isinstance(replicas, bool) or int(replicas) != 1:
        raise ValueError("SQLite production activation requires replicas=1")
    if isinstance(canary_percent, bool) or not 1 <= int(canary_percent) <= 50:
        raise ValueError("canary_percent must be between 1 and 50")

    plan: dict[str, Any] = {
        "version": ACTIVATION_PLAN_VERSION,
        "status": "PLAN_ONLY",
        "actor": str(actor),
        "image": image,
        "source_head": source,
        "expected_current_image": current,
        "replicas": 1,
        "canary_percent": int(canary_percent),
        "state_snapshot_ref": snapshot_ref,
        "state_snapshot_digest": snapshot_digest,
        "token_secret_ref": token_ref,
        "release_attestation_ref": attestation_ref,
        "sbom_ref": sbom,
        "compare_and_swap": {
            "expected_current_image_ref": current["image_ref"] if current else None,
            "expected_state_snapshot_ref": snapshot_ref,
            "expected_state_snapshot_digest": snapshot_digest,
            "failure": "HOLD_STALE_ACTIVATION_BASE",
        },
        "stages": [
            {
                "ordinal": 1,
                "name": "PREFLIGHT",
                "requires": [
                    "exact image digest pull",
                    "attestation source_head equals requested source_head",
                    "SBOM and release checksum verification",
                    "state snapshot digest verification",
                    "external secret resolution",
                ],
            },
            {
                "ordinal": 2,
                "name": "ISOLATED_CANARY",
                "requires": [
                    "isolated fresh or snapshot-cloned database",
                    "zero production writes",
                    "live/readiness/RPC probes",
                    "schema and deterministic replay verification",
                    "minimum observation window and sample count",
                ],
            },
            {
                "ordinal": 3,
                "name": "CUTOVER_HOLD",
                "requires": [
                    "canary assessment PROMOTE",
                    "explicit cutover authority reference",
                    "CAS current-image match",
                    "single-writer quiescence",
                ],
            },
            {
                "ordinal": 4,
                "name": "SINGLE_WRITER_CUTOVER",
                "requires": [
                    "stop previous writer",
                    "mount production state exactly once",
                    "start requested exact image digest",
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
                    "error/latency/restart observations",
                    "activation receipt bound to this plan digest",
                ],
            },
        ],
        "rollback": {
            "triggers": [
                "CAS base mismatch",
                "readiness failure",
                "schema failure",
                "replay divergence",
                "error-rate threshold breach",
                "latency threshold breach",
                "unexpected restart",
                "receipt mismatch",
            ],
            "action": "stop candidate, restore previous exact digest, restore or remount witnessed pre-cutover snapshot",
            "automatic_data_rewrite": False,
        },
        "boundary": "This is an ordered external-execution contract; it neither authorizes nor performs deployment.",
    }
    plan["plan_digest"] = _digest(plan)
    return plan


def assess_canary(
    baseline: Mapping[str, Any],
    canary: Mapping[str, Any],
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate external canary observations; absent or thin evidence HOLDs."""

    before = dict(baseline or {})
    after = dict(canary or {})
    limits = {
        "max_error_rate_delta": 0.01,
        "max_p95_ratio": 1.25,
        "max_restart_delta": 0,
        "min_sample_count": 30,
        "min_observation_window_seconds": 60,
        **dict(thresholds or {}),
    }
    required_numeric = ("error_rate", "p95_ms", "restart_count")
    required_boolean = ("ready", "schema_up_to_date", "replay_match")
    missing = [f"baseline.{key}" for key in required_numeric if key not in before]
    missing += [f"canary.{key}" for key in required_numeric if key not in after]
    missing += [f"canary.{key}" for key in required_boolean if key not in after]
    missing += [
        f"canary.{key}"
        for key in ("sample_count", "observation_window_seconds")
        if key not in after
    ]
    if missing:
        return {
            "version": CANARY_ASSESSMENT_VERSION,
            "decision": "HOLD",
            "status": "INSUFFICIENT_OBSERVATION",
            "missing": sorted(missing),
            "boundary": "Missing measurements remain UNKNOWN and are never converted to zero or PASS.",
        }

    baseline_error = _finite_number(before["error_rate"], "baseline.error_rate")
    canary_error = _finite_number(after["error_rate"], "canary.error_rate")
    baseline_p95 = _finite_number(before["p95_ms"], "baseline.p95_ms")
    canary_p95 = _finite_number(after["p95_ms"], "canary.p95_ms")
    baseline_restarts = _finite_number(before["restart_count"], "baseline.restart_count")
    canary_restarts = _finite_number(after["restart_count"], "canary.restart_count")
    sample_count = _positive_int(after["sample_count"], "canary.sample_count")
    observation_window = _positive_int(
        after["observation_window_seconds"], "canary.observation_window_seconds"
    )
    if baseline_p95 <= 0:
        raise ValueError("baseline.p95_ms must be greater than zero")

    observations = {
        "error_rate_delta": canary_error - baseline_error,
        "p95_ratio": canary_p95 / baseline_p95,
        "restart_delta": canary_restarts - baseline_restarts,
        "ready": after["ready"] is True,
        "schema_up_to_date": after["schema_up_to_date"] is True,
        "replay_match": after["replay_match"] is True,
        "sample_count": sample_count,
        "observation_window_seconds": observation_window,
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
        "sample_count": sample_count >= _positive_int(limits["min_sample_count"], "min_sample_count"),
        "observation_window": observation_window
        >= _positive_int(limits["min_observation_window_seconds"], "min_observation_window_seconds"),
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
            "PROMOTE means only that supplied observations satisfy this bounded policy. It is not cutover "
            "authority and cannot establish absence of unmeasured defects."
        ),
    }
    result["assessment_digest"] = _digest(result)
    return result


def verify_activation_receipt(
    receipt: Mapping[str, Any],
    *,
    expected_plan_digest: str,
    expected_image_ref: str,
    expected_source_head: str,
    expected_state_snapshot_ref: str,
    expected_state_snapshot_digest: str,
) -> dict[str, Any]:
    """Verify a supplied receipt's bindings without independently observing infrastructure."""

    data = dict(receipt or {})
    defects: list[dict[str, str]] = []
    expected_image = validate_image_ref(expected_image_ref, require_digest=True)["image_ref"]
    expected_plan = _sha256_ref(expected_plan_digest, "expected_plan_digest")
    expected_source = _git_sha(expected_source_head, "expected_source_head")
    expected_snapshot_ref = _nonempty(expected_state_snapshot_ref, "expected_state_snapshot_ref")
    expected_snapshot_digest = _sha256_ref(
        expected_state_snapshot_digest, "expected_state_snapshot_digest"
    )

    checks = {
        "schema": data.get("schema") == ACTIVATION_RECEIPT_VERSION,
        "status": data.get("status") == "ACTIVATED",
        "plan_digest": data.get("plan_digest") == expected_plan,
        "image_ref": data.get("image_ref") == expected_image,
        "source_head": data.get("source_head") == expected_source,
        "state_snapshot_ref": data.get("state_snapshot_ref") == expected_snapshot_ref,
        "state_snapshot_digest": data.get("state_snapshot_digest") == expected_snapshot_digest,
        "cutover_authority_ref": bool(str(data.get("cutover_authority_ref") or "").strip()),
        "executor_receipt_ref": bool(str(data.get("executor_receipt_ref") or "").strip()),
        "observed_at": bool(str(data.get("observed_at") or "").strip()),
        "observations": isinstance(data.get("observations"), dict) and bool(data.get("observations")),
    }
    for name, passed in checks.items():
        if not passed:
            defects.append({"field": name, "reason": "missing or mismatched receipt binding"})
    result = {
        "version": ACTIVATION_RECEIPT_VERSION,
        "status": "PASS" if not defects else "FAIL",
        "verified": not defects,
        "checks": {name: "PASS" if passed else "FAIL" for name, passed in checks.items()},
        "defects": defects,
        "receipt_digest": _digest(data),
        "boundary": (
            "PASS verifies supplied receipt structure and exact bindings only. The verifier does not independently "
            "query the cluster, registry, traffic plane, secret store, or state volume."
        ),
    }
    return result


def benchmark() -> dict[str, Any]:
    return {
        "deployment_version": DEPLOYMENT_VERSION,
        "http_adapter_version": HTTP_ADAPTER_VERSION,
        "production_digest_required": True,
        "source_head_binding_required": True,
        "single_writer_state": True,
        "active_active_supported": False,
        "minimum_canary_samples": 30,
        "minimum_canary_window_seconds": 60,
        "activation_receipt_replay": True,
        "activation_is_external": True,
    }
