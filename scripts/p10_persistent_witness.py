#!/usr/bin/env python3
"""Validate and witness an authorized persistent Athena HTTPS MCP endpoint.

The bearer token is read only from an environment variable and is never added
to the receipt. Provider evidence is allowlisted so a credential cannot be
smuggled into a committed witness.
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


SOURCE_COMMIT = "52d0e2abf282aee5f8bf233521989bc2c8969989"
RUNTIME_P09_HEAD = "9731b24c5963b75821b381b4562aa51baa55196c"
SELECTED_IMAGE_DIGEST = (
    "sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2"
)
SELECTED_IMAGE = (
    "ghcr.io/demeet2k/athena-mcp-server@" + SELECTED_IMAGE_DIGEST
)
PUBLICATION_RECEIPT = (
    "oci-publication:sha256:"
    "65caf0c574b3981e8c499ff075dda5ffc1512517e413fcdb0bf424fe49432a0d"
)
V2_IDENTIFIER = (
    "amc://github/compression/repo-q-shrink@0.1.0?lens=11#codec"
)
V1_IDENTIFIER = "athena://crystal-108d"
EXPECTED_GRAPH_DIGEST = (
    "sha256:82a3f9e2369394f39080b795476342688b95e35dcfcda3fe6a8be0212618d8d1"
)
EXPECTED_TOOLS = {
    "athena_federation_status",
    "resolve_athena_identity",
    "route_athena_federation",
    "athena_federation_cutover_receipt",
}
EXPECTED_RESOURCES = {
    "athena://federation-v2",
    "athena://federation-v2/lock",
    "athena://federation-v2/cutover",
}
PROVIDER_EVIDENCE_SCHEMA = "athena.provider-deployment-evidence/v1"
ALLOWED_PROVIDER_FIELDS = {
    "schema",
    "provider_id",
    "provider_account_scope",
    "deployment_id",
    "deployed_image",
    "image_digest",
    "source_commit",
    "runtime_p09_head",
    "endpoint",
    "persistent_service",
    "deployment_observed_at",
    "secret_store_ref",
    "secret_material_recorded",
    "evidence_url",
}
MINIMUM_SAMPLES = 3
MINIMUM_INTERVAL_SECONDS = 20.0
MINIMUM_TOKEN_LENGTH = 32


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _timestamp() -> str:
    value = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return value[:-6] + "Z" if value.endswith("+00:00") else value


def _exact_commit(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(
        character in "0123456789abcdef" for character in value
    )


def validate_endpoint(endpoint: str) -> str:
    parts = urlsplit(endpoint)
    if parts.scheme != "https" or not parts.netloc:
        raise ValueError("endpoint must be an absolute HTTPS URL")
    if parts.username or parts.password:
        raise ValueError("endpoint must not contain user information")
    if parts.query or parts.fragment:
        raise ValueError("endpoint must not contain a query or fragment")
    if parts.path.rstrip("/") != "/mcp":
        raise ValueError("endpoint path must end exactly in /mcp")
    return endpoint.rstrip("/")


def _required_text(evidence: dict[str, Any], key: str) -> str:
    value = evidence.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"provider evidence requires non-empty {key}")
    return value.strip()


def _validate_timestamp(value: str) -> str:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        raise ValueError("deployment_observed_at must include a timezone")
    return value


def validate_provider_evidence(
    evidence: dict[str, Any], endpoint: str
) -> dict[str, Any]:
    if not isinstance(evidence, dict):
        raise ValueError("provider evidence must be a JSON object")
    unknown = set(evidence) - ALLOWED_PROVIDER_FIELDS
    if unknown:
        raise ValueError(
            "provider evidence contains forbidden or unknown fields: "
            + ", ".join(sorted(unknown))
        )
    if evidence.get("schema") != PROVIDER_EVIDENCE_SCHEMA:
        raise ValueError("provider evidence schema is not admitted")

    normalized_endpoint = validate_endpoint(endpoint)
    evidence_endpoint = validate_endpoint(_required_text(evidence, "endpoint"))
    if evidence_endpoint != normalized_endpoint:
        raise ValueError("provider evidence endpoint does not match probe endpoint")

    if _required_text(evidence, "deployed_image") != SELECTED_IMAGE:
        raise ValueError("provider evidence does not select the exact admitted image")
    if _required_text(evidence, "image_digest") != SELECTED_IMAGE_DIGEST:
        raise ValueError("provider evidence image digest is not the admitted digest")
    if _required_text(evidence, "source_commit") != SOURCE_COMMIT:
        raise ValueError("provider evidence source commit is not the frozen P08 source")
    if _required_text(evidence, "runtime_p09_head") != RUNTIME_P09_HEAD:
        raise ValueError("provider evidence does not descend from the P09 runtime head")
    if evidence.get("persistent_service") is not True:
        raise ValueError("provider evidence must identify a persistent service")
    if evidence.get("secret_material_recorded") is not False:
        raise ValueError("provider evidence must not record secret material")

    evidence_url = validate_endpoint_url(
        _required_text(evidence, "evidence_url"), "evidence_url"
    )
    observed_at = _validate_timestamp(
        _required_text(evidence, "deployment_observed_at")
    )

    return {
        "schema": PROVIDER_EVIDENCE_SCHEMA,
        "provider_id": _required_text(evidence, "provider_id"),
        "provider_account_scope": _required_text(
            evidence, "provider_account_scope"
        ),
        "deployment_id": _required_text(evidence, "deployment_id"),
        "deployed_image": SELECTED_IMAGE,
        "image_digest": SELECTED_IMAGE_DIGEST,
        "source_commit": SOURCE_COMMIT,
        "runtime_p09_head": RUNTIME_P09_HEAD,
        "endpoint": normalized_endpoint,
        "persistent_service": True,
        "deployment_observed_at": observed_at,
        "secret_store_ref": _required_text(evidence, "secret_store_ref"),
        "secret_material_recorded": False,
        "evidence_url": evidence_url,
    }


def validate_endpoint_url(value: str, field: str) -> str:
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.netloc:
        raise ValueError(f"{field} must be an absolute HTTPS URL")
    if parts.username or parts.password:
        raise ValueError(f"{field} must not contain user information")
    return value


def load_provider_evidence(path: Path, endpoint: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return validate_provider_evidence(value, endpoint)


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _unwrap(value: Any) -> Any:
    if isinstance(value, dict) and set(value) == {"result"}:
        return value["result"]
    return value


def _tool_payload(result: Any) -> dict[str, Any]:
    if getattr(result, "isError", False) or getattr(result, "is_error", False):
        raise RuntimeError(f"MCP tool returned an error: {_jsonable(result)!r}")
    structured = getattr(result, "structuredContent", None)
    if structured is None:
        structured = getattr(result, "structured_content", None)
    structured = _unwrap(_jsonable(structured))
    if isinstance(structured, dict):
        return structured
    for block in getattr(result, "content", []):
        text = getattr(block, "text", None)
        if not text:
            continue
        try:
            decoded = _unwrap(json.loads(text))
        except json.JSONDecodeError:
            continue
        if isinstance(decoded, dict):
            return decoded
    raise RuntimeError("MCP tool result did not contain a JSON object")


def _resource_payload(result: Any) -> dict[str, Any]:
    for content in getattr(result, "contents", []):
        text = getattr(content, "text", None)
        if text:
            value = json.loads(text)
            if isinstance(value, dict):
                return value
    raise RuntimeError("MCP resource did not contain a JSON object")


async def sample_endpoint(
    endpoint: str, token: str, expected_commit: str
) -> dict[str, Any]:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    from scripts.host_attestation import fetch_host_attestation

    host_attestation = fetch_host_attestation(endpoint, expected_commit)
    headers = {"Authorization": f"Bearer {token}"}
    async with streamablehttp_client(endpoint, headers=headers) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            resources = await session.list_resources()
            status = _tool_payload(
                await session.call_tool(
                    "athena_federation_status", arguments={}
                )
            )
            identity = _tool_payload(
                await session.call_tool(
                    "resolve_athena_identity",
                    arguments={"identifier": V2_IDENTIFIER},
                )
            )
            route = _tool_payload(
                await session.call_tool(
                    "route_athena_federation",
                    arguments={
                        "source": "athena.repo.q-shrink",
                        "target": "athena.runtime.route-compiler",
                        "require_return": True,
                        "allow_v1_fallback": True,
                    },
                )
            )
            fallback = _tool_payload(
                await session.call_tool(
                    "resolve_athena_identity",
                    arguments={"identifier": V1_IDENTIFIER},
                )
            )
            cutover_tool = _tool_payload(
                await session.call_tool(
                    "athena_federation_cutover_receipt", arguments={}
                )
            )
            cutover_resource = _resource_payload(
                await session.read_resource(
                    "athena://federation-v2/cutover"
                )
            )

    tool_names = {tool.name for tool in tools.tools}
    resource_uris = {str(resource.uri) for resource in resources.resources}
    checks = {
        "mcp_initialize": bool(initialized),
        "host_ready": host_attestation.get("status") == "ready",
        "source_commit_exact": (
            host_attestation.get("deployed_commit") == expected_commit
            and host_attestation.get("commit_attested") is True
            and host_attestation.get("commit_source") == "build-locked-file"
        ),
        "required_tools_present": EXPECTED_TOOLS.issubset(tool_names),
        "required_resources_present": EXPECTED_RESOURCES.issubset(resource_uris),
        "frozen_graph_exact": status.get("graph_digest")
        == EXPECTED_GRAPH_DIGEST,
        "v2_identity_answered": (
            identity.get("verdict") == "FOUND"
            and identity.get("answered_by") == "athena-federation-v2"
            and identity.get("fallback_used") is False
        ),
        "v2_route_answered": (
            route.get("verdict") == "FOUND"
            and route.get("answered_by") == "athena-federation-v2"
            and route.get("hops")
            == ["edge.q-shrink-to-control", "edge.control-to-runtime"]
        ),
        "reciprocal_return_answered": route.get("return_plan")
        == ["edge.runtime-to-control", "edge.control-to-q-shrink"],
        "v1_fallback_answered": (
            fallback.get("verdict") == "FOUND_LEGACY"
            and fallback.get("answered_by") == "athena-108d-v1"
            and fallback.get("fallback_used") is True
        ),
        "tool_resource_receipts_equal": cutover_tool == cutover_resource,
        "promotion_boundary": (
            status.get("promotion_ready") is False
            and cutover_tool.get("promotion_claimed") is False
            and host_attestation.get("promotion_ready") is False
        ),
    }
    if not all(checks.values()):
        failed = sorted(key for key, passed in checks.items() if not passed)
        raise RuntimeError("persistent endpoint sample failed: " + ", ".join(failed))
    return {
        "observed_at": _timestamp(),
        "checks": checks,
        "health": host_attestation,
        "answer_provenance": {
            "v2_identity": {
                "identifier": V2_IDENTIFIER,
                "answered_by": identity.get("answered_by"),
                "verdict": identity.get("verdict"),
                "fallback_used": identity.get("fallback_used"),
            },
            "v2_route": {
                "source": route.get("source"),
                "target": route.get("target"),
                "hops": route.get("hops"),
                "return_plan": route.get("return_plan"),
                "answered_by": route.get("answered_by"),
            },
            "v1_fallback": {
                "identifier": V1_IDENTIFIER,
                "answered_by": fallback.get("answered_by"),
                "verdict": fallback.get("verdict"),
                "fallback_used": fallback.get("fallback_used"),
            },
        },
    }


def build_witness_receipt(
    endpoint: str,
    provider_evidence: dict[str, Any],
    samples: list[dict[str, Any]],
    interval_seconds: float,
) -> dict[str, Any]:
    if len(samples) < MINIMUM_SAMPLES:
        raise ValueError(f"at least {MINIMUM_SAMPLES} samples are required")
    if interval_seconds < MINIMUM_INTERVAL_SECONDS:
        raise ValueError(
            f"sample interval must be at least {MINIMUM_INTERVAL_SECONDS:g} seconds"
        )
    body = {
        "schema": "athena.persistent-mcp-witness/v1",
        "phase": "P10",
        "seed": (
            "KC144.MYC.SKELETON.P10::"
            "AUTHORIZED-HTTPS-ENDPOINT-AND-PERSISTENT-WITNESS"
        ),
        "verdict": "PASS_PERSISTENT_ENDPOINT_WITNESSED_NOT_PROMOTED",
        "observed_at": _timestamp(),
        "endpoint": validate_endpoint(endpoint),
        "selected_image": {
            "reference": SELECTED_IMAGE,
            "digest": SELECTED_IMAGE_DIGEST,
            "source_commit": SOURCE_COMMIT,
            "runtime_p09_head": RUNTIME_P09_HEAD,
            "publication_receipt": PUBLICATION_RECEIPT,
        },
        "provider_evidence": provider_evidence,
        "authentication": {
            "class": "bearer",
            "token_present": True,
            "token_recorded": False,
            "secret_store_ref": provider_evidence["secret_store_ref"],
        },
        "observation_window": {
            "sample_count": len(samples),
            "interval_seconds": interval_seconds,
            "minimum_elapsed_seconds": interval_seconds * (len(samples) - 1),
            "samples": samples,
        },
        "authority": {
            "persistent_endpoint_witnessed": True,
            "promotion_ready": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_promotion_required": True,
        },
        "rollback": {
            "class": "immutable-digest-selection",
            "action": (
                "Stop routing to this endpoint and reselect the P09 digest or "
                "explicit athena-108d-v1 fallback without rewriting history."
            ),
        },
        "next_gate": (
            "Admit this witness in the control plane; IC10 promotion remains "
            "a separate conjunctive decision."
        ),
        "successor_seed": (
            "KC144.MYC.SKELETON.P11::"
            "PERSISTENT-WITNESS-ADMISSION-AND-IC10-READINESS"
        ),
    }
    return {
        "receipt_id": (
            "persistent-mcp:sha256:" + sha256(_canonical_bytes(body)).hexdigest()
        ),
        **body,
    }


async def probe_persistent_endpoint(
    endpoint: str,
    token: str,
    provider_evidence: dict[str, Any],
    samples: int,
    interval_seconds: float,
) -> dict[str, Any]:
    if len(token) < MINIMUM_TOKEN_LENGTH:
        raise ValueError(
            f"bearer token must contain at least {MINIMUM_TOKEN_LENGTH} characters"
        )
    if samples < MINIMUM_SAMPLES:
        raise ValueError(f"at least {MINIMUM_SAMPLES} samples are required")
    if interval_seconds < MINIMUM_INTERVAL_SECONDS:
        raise ValueError(
            f"sample interval must be at least {MINIMUM_INTERVAL_SECONDS:g} seconds"
        )
    observations: list[dict[str, Any]] = []
    for index in range(samples):
        observations.append(
            await sample_endpoint(endpoint, token, SOURCE_COMMIT)
        )
        if index + 1 < samples:
            await asyncio.sleep(interval_seconds)
    return build_witness_receipt(
        endpoint, provider_evidence, observations, interval_seconds
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("endpoint", help="authorized HTTPS endpoint ending in /mcp")
    parser.add_argument(
        "--provider-evidence", required=True, type=Path
    )
    parser.add_argument("--token-env", default="ATHENA_MCP_BEARER_TOKEN")
    parser.add_argument("--samples", type=int, default=MINIMUM_SAMPLES)
    parser.add_argument(
        "--interval", type=float, default=MINIMUM_INTERVAL_SECONDS
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-evidence-only", action="store_true")
    args = parser.parse_args()

    endpoint = validate_endpoint(args.endpoint)
    provider_evidence = load_provider_evidence(
        args.provider_evidence, endpoint
    )
    if args.validate_evidence_only:
        result: dict[str, Any] = {
            "schema": "athena.p10-activation-input-check/v1",
            "verdict": "VALID_AUTHORIZED_INPUTS_NOT_PROBED",
            "provider_evidence": provider_evidence,
            "promotion_claimed": False,
        }
    else:
        token = os.environ.get(args.token_env)
        if token is None:
            raise SystemExit(
                f"missing bearer token environment variable: {args.token_env}"
            )
        result = asyncio.run(
            probe_persistent_endpoint(
                endpoint,
                token,
                provider_evidence,
                args.samples,
                args.interval,
            )
        )

    content = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
