#!/usr/bin/env python3
"""Repeated live witness window for the canonical P10 deployment capsule."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

from scripts.p10_contract import (
    canonical_bytes,
    target_digest,
    validate_target,
    validate_token,
)
from scripts.p10_persistent_witness import (
    EXPECTED_RESOURCE_COUNT,
    EXPECTED_RESOURCE_INVENTORY_DIGEST,
    EXPECTED_TOOL_COUNT,
    EXPECTED_TOOL_INVENTORY_DIGEST,
)
from scripts.p10_provider_evidence import (
    load_provider_evidence,
    validate_provider_evidence,
)


MINIMUM_SAMPLES = 3
MINIMUM_INTERVAL_SECONDS = 20.0
MINIMUM_SPAN_SECONDS = 40.0
REQUIRED_SAMPLE_CHECKS = {
    "mcp_initialize",
    "real_network_contact",
    "host_commit_attested",
    "required_tools_present",
    "actual_tool_count_exact",
    "actual_tool_inventory_exact",
    "required_resources_present",
    "actual_resource_count_exact",
    "actual_resource_inventory_exact",
    "unauthenticated_rejected",
    "invalid_token_rejected",
    "redirects_absent",
    "https_not_downgraded",
    "frozen_graph_exact",
    "v2_identity_answered",
    "v2_route_answered",
    "reciprocal_return_answered",
    "explicit_v1_fallback_answered",
    "tool_resource_receipts_equal",
    "promotion_boundary",
}
LEGAL_PERSISTENT_VERDICT = "PASS_PERSISTENT_HTTPS_WITNESS"


def _timestamp() -> str:
    value = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return value[:-6] + "Z" if value.endswith("+00:00") else value


def _parse_timestamp(value: Any, path: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path} must be an ISO-8601 timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ValueError(f"{path} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError(f"{path} must include a timezone")
    return parsed


def _validated_samples(
    samples: list[dict[str, Any]],
    target: dict[str, Any],
    interval_seconds: float,
) -> tuple[list[dict[str, Any]], float]:
    normalized: list[dict[str, Any]] = []
    observed_times: list[datetime] = []
    expected_target = {
        "target_id": target["target_id"],
        "target_digest": target_digest(target),
        "endpoint": target["endpoint"],
        "persistence_class": target["persistence"]["class"],
        "authorization_ref": target["authorization"]["ref"],
    }
    for index, sample in enumerate(samples, start=1):
        if sample.get("verdict") != "PASS_LIVE_PERSISTENT_ENDPOINT_NOT_PROMOTED":
            raise ValueError(f"sample {index} is not a passing persistent witness")
        checks = sample.get("checks")
        if not isinstance(checks, dict):
            raise ValueError(f"sample {index} has no check map")
        missing = REQUIRED_SAMPLE_CHECKS - set(checks)
        failed = sorted(key for key in REQUIRED_SAMPLE_CHECKS if checks.get(key) is not True)
        if missing or failed:
            raise ValueError(
                f"sample {index} failed required checks: "
                + ", ".join(sorted(missing) + failed)
            )
        if sample.get("target") != expected_target:
            raise ValueError(f"sample {index} targets a different contract")
        deployment = sample.get("deployment")
        if not isinstance(deployment, dict):
            raise ValueError(f"sample {index} has no deployment attestation")
        if deployment.get("image") != target.get("image"):
            raise ValueError(f"sample {index} uses a different image")
        if deployment.get("source_commit") != target.get("source_commit"):
            raise ValueError(f"sample {index} uses a different source commit")
        if (
            deployment.get("image_selection_attestation")
            != "authorized-target-contract"
            or deployment.get("source_commit_attestation")
            != "host-health-build-locked-file"
            or deployment.get("transport") != "streamable-http"
            or deployment.get("authentication")
            != "bearer-present-value-not-recorded"
            or deployment.get("persistent_endpoint") is not True
        ):
            raise ValueError(
                f"sample {index} lacks exact deployment attestation"
            )
        if (
            sample.get("secret_recorded") is not False
            or sample.get("persistent_deployment_claimed") is not True
            or sample.get("promotion_ready") is not False
            or sample.get("promotion_claimed") is not False
            or sample.get("merge_claimed") is not False
        ):
            raise ValueError(f"sample {index} crosses the promotion boundary")
        catalog = sample.get("catalog")
        if not isinstance(catalog, dict) or (
            catalog.get("tools_count") != EXPECTED_TOOL_COUNT
            or catalog.get("tool_inventory_digest")
            != EXPECTED_TOOL_INVENTORY_DIGEST
            or catalog.get("resources_count") != EXPECTED_RESOURCE_COUNT
            or catalog.get("resource_inventory_digest")
            != EXPECTED_RESOURCE_INVENTORY_DIGEST
            or catalog.get("required_tools_present") is not True
            or catalog.get("required_resources_present") is not True
        ):
            raise ValueError(f"sample {index} has a non-exact catalog")
        provenance = sample.get("answer_provenance")
        route = provenance.get("v2_route", {}) if isinstance(provenance, dict) else {}
        fallback = (
            provenance.get("v1_fallback", {})
            if isinstance(provenance, dict)
            else {}
        )
        if (
            route.get("hops")
            != ["edge.q-shrink-to-control", "edge.control-to-runtime"]
            or route.get("return_plan")
            != ["edge.runtime-to-control", "edge.control-to-q-shrink"]
            or fallback.get("answered_by") != "athena-108d-v1"
            or fallback.get("fallback_used") is not True
        ):
            raise ValueError(
                f"sample {index} lacks exact route and fallback provenance"
            )
        observed_times.append(
            _parse_timestamp(sample.get("observed_at"), f"sample {index}")
        )
        normalized.append({
            "observed_at": sample.get("observed_at"),
            "checks": checks,
            "catalog": sample.get("catalog"),
            "answer_provenance": sample.get("answer_provenance"),
            "workflow_run": sample.get("workflow_run"),
        })
    for index in range(1, len(observed_times)):
        elapsed = (
            observed_times[index] - observed_times[index - 1]
        ).total_seconds()
        if elapsed < interval_seconds:
            raise ValueError(
                f"sample {index + 1} was observed before the required interval"
            )
    observed_span = (
        observed_times[-1] - observed_times[0]
    ).total_seconds()
    if observed_span < MINIMUM_SPAN_SECONDS:
        raise ValueError(
            f"observed sample span must be at least {MINIMUM_SPAN_SECONDS:g} seconds"
        )
    return normalized, observed_span


def build_window_receipt(
    target: dict[str, Any],
    provider_evidence: dict[str, Any],
    samples: list[dict[str, Any]],
    interval_seconds: float,
) -> dict[str, Any]:
    target = validate_target(target)
    provider_evidence = validate_provider_evidence(
        provider_evidence,
        target,
    )
    if len(samples) < MINIMUM_SAMPLES:
        raise ValueError(f"at least {MINIMUM_SAMPLES} samples are required")
    if interval_seconds < MINIMUM_INTERVAL_SECONDS:
        raise ValueError(
            f"sample interval must be at least {MINIMUM_INTERVAL_SECONDS:g} seconds"
        )
    observations, observed_span = _validated_samples(
        samples,
        target,
        interval_seconds,
    )
    authorization_time = _parse_timestamp(
        target["authorization"]["authorized_at"],
        "target authorization",
    )
    deployment_time = _parse_timestamp(
        provider_evidence["deployment_observed_at"],
        "provider deployment observation",
    )
    first_observation_time = _parse_timestamp(
        samples[0]["observed_at"],
        "first sample",
    )
    if authorization_time > deployment_time:
        raise ValueError("deployment observation cannot precede authorization")
    if deployment_time > first_observation_time:
        raise ValueError("live witness cannot precede deployment observation")
    first = samples[0]
    body = {
        "schema": "athena.persistent-mcp-witness/v2",
        "phase": "P10",
        "seed": (
            "KC144.MYC.SKELETON.P10::"
            "AUTHORIZED-HTTPS-ENDPOINT-AND-PERSISTENT-WITNESS"
        ),
        "verdict": LEGAL_PERSISTENT_VERDICT,
        "observed_at": _timestamp(),
        "target": first["target"],
        "provider_evidence": provider_evidence,
        "deployment": first["deployment"],
        "authentication": {
            "class": "bearer",
            "token_present": True,
            "token_recorded": False,
            "secret_store_ref": provider_evidence["secret_store_ref"],
        },
        "observation_window": {
            "sample_count": len(observations),
            "interval_seconds": interval_seconds,
            "minimum_elapsed_seconds": observed_span,
            "samples": observations,
        },
        "secret_recorded": False,
        "persistent_deployment_claimed": True,
        "promotion_ready": False,
        "promotion_claimed": False,
        "merge_claimed": False,
        "authority": {
            "persistent_endpoint_witnessed": True,
            "runtime_can_promote": False,
            "ic10_required": True,
        },
        "rollback": {
            "class": "immutable-digest-selection",
            "action": (
                "Stop routing to this endpoint and reselect the exact P09 digest "
                "or explicit athena-108d-v1 fallback without rewriting history."
            ),
        },
        "next_gate": (
            "Admit this exact repeated witness in the Athena control plane; "
            "IC10 remains required for any promotion decision."
        ),
        "successor_seed": (
            "KC144.MYC.SKELETON.P11::"
            "PERSISTENT-WITNESS-ADMISSION-AND-IC10-READINESS"
        ),
    }
    return {
        "receipt_id": (
            "persistent-window:sha256:"
            + sha256(canonical_bytes(body)).hexdigest()
        ),
        **body,
    }


async def observe_window(
    target: dict[str, Any],
    provider_evidence: dict[str, Any],
    token: str,
    samples: int,
    interval_seconds: float,
    per_sample_timeout: int,
) -> dict[str, Any]:
    from scripts.p10_persistent_witness import _build_receipt, _observe

    if samples < MINIMUM_SAMPLES:
        raise ValueError(f"at least {MINIMUM_SAMPLES} samples are required")
    if interval_seconds < MINIMUM_INTERVAL_SECONDS:
        raise ValueError(
            f"sample interval must be at least {MINIMUM_INTERVAL_SECONDS:g} seconds"
        )
    receipts: list[dict[str, Any]] = []
    for index in range(samples):
        async with asyncio.timeout(per_sample_timeout):
            observation = await _observe(target, token)
        receipt = _build_receipt(target, observation)
        if not receipt["verdict"].startswith("PASS_"):
            raise RuntimeError(f"persistent sample {index + 1} failed closed")
        receipts.append(receipt)
        if index + 1 < samples:
            await asyncio.sleep(interval_seconds)
    return build_window_receipt(
        target, provider_evidence, receipts, interval_seconds
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--provider-evidence", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("p10-persistent-witness.json"))
    parser.add_argument("--samples", type=int, default=MINIMUM_SAMPLES)
    parser.add_argument("--interval", type=float, default=MINIMUM_INTERVAL_SECONDS)
    parser.add_argument("--per-sample-timeout", type=int, default=180)
    arguments = parser.parse_args()

    target = validate_target(
        json.loads(arguments.target.read_text(encoding="utf-8"))
    )
    evidence = load_provider_evidence(arguments.provider_evidence, target)
    token = validate_token(os.environ.get("ATHENA_MCP_BEARER_TOKEN"))
    receipt = asyncio.run(
        observe_window(
            target,
            evidence,
            token,
            arguments.samples,
            arguments.interval,
            arguments.per_sample_timeout,
        )
    )
    content = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    arguments.output.write_text(content, encoding="utf-8")
    print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
