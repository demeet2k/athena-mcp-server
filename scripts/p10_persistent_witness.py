#!/usr/bin/env python3
"""Probe an authorized persistent Athena HTTPS endpoint without leaking secrets."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

try:
    from scripts.p10_contract import (
        IMAGE_DIGEST,
        IMAGE_REFERENCE,
        P09_HEAD,
        PUBLICATION_RECEIPT,
        SOURCE_COMMIT,
        TOKEN_ENV,
        WITNESS_OUTCOME,
        canonical_bytes,
        content_addressed_receipt,
        content_digest,
        health_url,
        load_contract,
        secret_free,
        validate_contract,
        validate_endpoint,
        validate_token_from_environment,
    )
except ModuleNotFoundError:
    from p10_contract import (
        IMAGE_DIGEST,
        IMAGE_REFERENCE,
        P09_HEAD,
        PUBLICATION_RECEIPT,
        SOURCE_COMMIT,
        TOKEN_ENV,
        WITNESS_OUTCOME,
        canonical_bytes,
        content_addressed_receipt,
        content_digest,
        health_url,
        load_contract,
        secret_free,
        validate_contract,
        validate_endpoint,
        validate_token_from_environment,
    )


V2_IDENTIFIER = (
    "amc://github/compression/repo-q-shrink@0.1.0?lens=11#codec"
)
V1_IDENTIFIER = "athena://crystal-108d"
EXPECTED_GRAPH_DIGEST = (
    "sha256:82a3f9e2369394f39080b795476342688b95e35dcfcda3fe6a8be0212618d8d1"
)
EXPECTED_TOOL_COUNT = 174
EXPECTED_TOOL_INVENTORY_DIGEST = (
    "sha256:230b41262dd77cc7e73f1acb3afcbc8de67bb52e680f35abfebb3465620fc34c"
)
EXPECTED_RESOURCE_COUNT = 27
EXPECTED_RESOURCE_INVENTORY_DIGEST = (
    "sha256:6e74961966019708425aa26ed6bddb0c665cfffacb1ef7e44494f8861deb9eea"
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
MINIMUM_PERSISTENT_SAMPLES = 3
DEFAULT_INTERVAL_SECONDS = 5.0


def utc_now() -> str:
    value = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return value.replace("+00:00", "Z")


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
        raise RuntimeError("MCP tool returned an error")
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
            decoded = json.loads(text)
            if isinstance(decoded, dict):
                return decoded
    raise RuntimeError("MCP resource did not contain a JSON object")


def inventory_digest(names: list[str]) -> str:
    return f"sha256:{sha256(canonical_bytes(names)).hexdigest()}"


def _strict_httpx_factory(
    *,
    headers: dict[str, str] | None = None,
    timeout: httpx.Timeout | None = None,
    auth: httpx.Auth | None = None,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers=headers,
        timeout=timeout,
        auth=auth,
        follow_redirects=False,
    )


def _require_direct_response(
    response: httpx.Response,
    expected_url: str,
    expected_status: int,
    label: str,
) -> None:
    if response.history or response.is_redirect or "location" in response.headers:
        raise RuntimeError(f"{label} unexpectedly redirected")
    if str(response.url) != expected_url:
        raise RuntimeError(f"{label} changed the exact endpoint")
    if response.url.scheme != "https":
        raise RuntimeError(f"{label} downgraded from HTTPS")
    if response.status_code != expected_status:
        raise RuntimeError(f"{label} returned an unexpected status")


async def observe_http_boundary(
    endpoint: str,
    token: str,
    *,
    timeout: float = 20.0,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    """Verify health and both negative authentication cases without redirects."""
    endpoint = validate_endpoint(endpoint)
    derived_health_url = health_url(endpoint)
    invalid_token = "athena-p10-invalid-token-never-authorized"
    if invalid_token == token:
        invalid_token = "athena-p10-second-invalid-token-never-authorized"
    request_body = {
        "jsonrpc": "2.0",
        "id": "p10-negative-auth-check",
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "athena-p10-witness", "version": "1"},
        },
    }
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(
        follow_redirects=False,
        verify=True,
        timeout=timeout,
        transport=transport,
    ) as client:
        health_response = await client.get(
            derived_health_url,
            headers={"Accept": "application/json"},
        )
        _require_direct_response(
            health_response, derived_health_url, 200, "health endpoint"
        )
        health = health_response.json()
        if not isinstance(health, dict):
            raise RuntimeError("health endpoint did not return a JSON object")

        unauthenticated = await client.post(
            endpoint,
            headers=headers,
            json=request_body,
        )
        _require_direct_response(
            unauthenticated, endpoint, 401, "unauthenticated MCP request"
        )

        invalid = await client.post(
            endpoint,
            headers={
                **headers,
                "Authorization": f"Bearer {invalid_token}",
            },
            json=request_body,
        )
        _require_direct_response(invalid, endpoint, 401, "invalid-token MCP request")

    health_checks = {
        "status_ready": health.get("status") == "ready",
        "transport_streamable_http": health.get("transport") == "streamable-http",
        "endpoint_exact": health.get("endpoint") == "/mcp",
        "authentication_bearer": health.get("authentication") == "bearer",
        "source_commit_exact": health.get("deployed_commit") == SOURCE_COMMIT,
        "build_locked_commit_attested": (
            health.get("commit_attested") is True
            and health.get("commit_source") == "build-locked-file"
        ),
        "promotion_ready_false": health.get("promotion_ready") is False,
        "unauthenticated_rejected": unauthenticated.status_code == 401,
        "invalid_token_rejected": invalid.status_code == 401,
        "redirects_absent": True,
        "https_not_downgraded": True,
    }
    failed = sorted(name for name, passed in health_checks.items() if not passed)
    if failed:
        raise RuntimeError("HTTP boundary failed: " + ", ".join(failed))
    return {
        "health": health,
        "checks": health_checks,
        "real_network_contact": transport is None,
    }


async def observe_mcp(endpoint: str, token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    async with streamablehttp_client(
        endpoint,
        headers=headers,
        timeout=30,
        sse_read_timeout=120,
        httpx_client_factory=_strict_httpx_factory,
    ) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            tools_result = await session.list_tools()
            resources_result = await session.list_resources()
            tool_names = sorted(tool.name for tool in tools_result.tools)
            resource_uris = sorted(
                str(resource.uri) for resource in resources_result.resources
            )
            status = _tool_payload(
                await session.call_tool("athena_federation_status", arguments={})
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
                await session.read_resource("athena://federation-v2/cutover")
            )
    return {
        "initialized": bool(_jsonable(initialized)),
        "catalog": {
            "tool_count": len(tool_names),
            "tool_inventory_digest": inventory_digest(tool_names),
            "tool_names": tool_names,
            "resource_count": len(resource_uris),
            "resource_inventory_digest": inventory_digest(resource_uris),
            "resource_uris": resource_uris,
        },
        "status": status,
        "identity": identity,
        "route": route,
        "fallback": fallback,
        "cutover_tool": cutover_tool,
        "cutover_resource": cutover_resource,
    }


def validate_mcp_observation(observation: dict[str, Any]) -> dict[str, bool]:
    catalog = observation["catalog"]
    status = observation["status"]
    identity = observation["identity"]
    route = observation["route"]
    fallback = observation["fallback"]
    cutover_tool = observation["cutover_tool"]
    checks = {
        "streamable_http_initialized": observation["initialized"] is True,
        "actual_tool_count_exact": catalog["tool_count"] == EXPECTED_TOOL_COUNT,
        "actual_tool_inventory_exact": (
            catalog["tool_inventory_digest"]
            == EXPECTED_TOOL_INVENTORY_DIGEST
        ),
        "required_tools_present": EXPECTED_TOOLS.issubset(
            catalog["tool_names"]
        ),
        "actual_resource_count_exact": (
            catalog["resource_count"] == EXPECTED_RESOURCE_COUNT
        ),
        "actual_resource_inventory_exact": (
            catalog["resource_inventory_digest"]
            == EXPECTED_RESOURCE_INVENTORY_DIGEST
        ),
        "required_resources_present": EXPECTED_RESOURCES.issubset(
            catalog["resource_uris"]
        ),
        "frozen_graph_exact": status.get("graph_digest")
        == EXPECTED_GRAPH_DIGEST,
        "v2_identity_exact": (
            identity.get("verdict") == "FOUND"
            and identity.get("answered_by") == "athena-federation-v2"
            and identity.get("fallback_used") is False
            and identity.get("resource", {}).get("rid")
            == "athena.repo.q-shrink"
        ),
        "v2_route_exact": (
            route.get("verdict") == "FOUND"
            and route.get("answered_by") == "athena-federation-v2"
            and route.get("fallback_used") is False
            and route.get("hops")
            == ["edge.q-shrink-to-control", "edge.control-to-runtime"]
        ),
        "reciprocal_return_exact": route.get("return_plan")
        == ["edge.runtime-to-control", "edge.control-to-q-shrink"],
        "explicit_athena_108d_v1_fallback": (
            fallback.get("verdict") == "FOUND_LEGACY"
            and fallback.get("answered_by") == "athena-108d-v1"
            and fallback.get("fallback_used") is True
        ),
        "cutover_tool_resource_equal": (
            cutover_tool == observation["cutover_resource"]
        ),
        "promotion_ready_false": (
            status.get("promotion_ready") is False
            and cutover_tool.get("promotion_claimed") is False
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError("MCP observation failed: " + ", ".join(failed))
    return checks


def summarize_mcp(observation: dict[str, Any]) -> dict[str, Any]:
    identity = observation["identity"]
    route = observation["route"]
    fallback = observation["fallback"]
    return {
        "catalog": observation["catalog"],
        "answer_provenance": {
            "v2_identity": {
                "identifier": V2_IDENTIFIER,
                "verdict": identity.get("verdict"),
                "answered_by": identity.get("answered_by"),
                "fallback_used": identity.get("fallback_used"),
                "resource": identity.get("resource", {}).get("rid"),
            },
            "v2_route": {
                "source": route.get("source"),
                "target": route.get("target"),
                "hops": route.get("hops"),
                "return_plan": route.get("return_plan"),
                "answered_by": route.get("answered_by"),
                "fallback_used": route.get("fallback_used"),
            },
            "v1_fallback": {
                "identifier": V1_IDENTIFIER,
                "verdict": fallback.get("verdict"),
                "answered_by": fallback.get("answered_by"),
                "fallback_used": fallback.get("fallback_used"),
            },
        },
    }


async def sample_endpoint(
    contract: dict[str, Any],
    token: str,
    *,
    timeout: float,
) -> dict[str, Any]:
    endpoint = contract["network"]["external_mcp_endpoint"]
    http_observation = await observe_http_boundary(
        endpoint, token, timeout=timeout
    )
    mcp_observation = await observe_mcp(endpoint, token)
    mcp_checks = validate_mcp_observation(mcp_observation)
    return {
        "observed_at": utc_now(),
        "real_network_contact": http_observation["real_network_contact"],
        "http_checks": http_observation["checks"],
        "health": http_observation["health"],
        "mcp_checks": mcp_checks,
        **summarize_mcp(mcp_observation),
    }


def build_witness_receipt(
    contract: dict[str, Any],
    samples: list[dict[str, Any]],
    *,
    witness_class: str,
) -> dict[str, Any]:
    if not samples:
        raise ValueError("at least one witness sample is required")
    persistent = witness_class == "persistent-https"
    if persistent:
        if len(samples) < MINIMUM_PERSISTENT_SAMPLES:
            raise ValueError(
                f"persistent witness requires {MINIMUM_PERSISTENT_SAMPLES} samples"
            )
        if not all(sample.get("real_network_contact") is True for sample in samples):
            raise ValueError("persistent verdict requires real network contact")
    elif witness_class != "local-ephemeral-simulation":
        raise ValueError("unknown witness class")

    for sample in samples:
        if not all(sample["http_checks"].values()):
            raise ValueError("witness contains a failed HTTP check")
        if not all(sample["mcp_checks"].values()):
            raise ValueError("witness contains a failed MCP check")
        health = sample["health"]
        if (
            health.get("deployed_commit") != SOURCE_COMMIT
            or health.get("commit_source") != "build-locked-file"
            or health.get("promotion_ready") is not False
        ):
            raise ValueError("witness sample lacks exact build-locked health")

    first = samples[0]
    evidence_projection = {
        "contract_digest": content_digest(contract),
        "endpoint": contract["network"]["external_mcp_endpoint"],
        "source_commit": SOURCE_COMMIT,
        "image_reference": IMAGE_REFERENCE,
        "catalog": first["catalog"],
        "answer_provenance": first["answer_provenance"],
        "http_checks": first["http_checks"],
        "mcp_checks": first["mcp_checks"],
        "sample_count": len(samples),
        "witness_class": witness_class,
    }
    verdict = (
        WITNESS_OUTCOME
        if persistent
        else "PASS_LOCAL_SIMULATION_NOT_PERSISTENT"
    )
    run_id = os.environ.get("GITHUB_RUN_ID")
    repository = os.environ.get(
        "GITHUB_REPOSITORY", "demeet2k/athena-mcp-server"
    )
    body = {
        "schema": "athena.p10-persistent-https-witness/v1",
        "phase": "P10",
        "seed": (
            "KC144.MYC.SKELETON.P10::"
            "AUTHORIZED-HTTPS-ENDPOINT-AND-PERSISTENT-WITNESS"
        ),
        "verdict": verdict,
        "witness_class": witness_class,
        "evidence_digest": content_digest(evidence_projection),
        "observation_window": {
            "first_observed_at": samples[0]["observed_at"],
            "last_observed_at": samples[-1]["observed_at"],
            "sample_count": len(samples),
            "samples": samples,
        },
        "selected_image": {
            "reference": IMAGE_REFERENCE,
            "digest": IMAGE_DIGEST,
            "source_commit": SOURCE_COMMIT,
            "runtime_p09_head": P09_HEAD,
            "publication_receipt": PUBLICATION_RECEIPT,
        },
        "target": {
            **contract["target"],
            "endpoint": contract["network"]["external_mcp_endpoint"],
            "contract_digest": content_digest(contract),
        },
        "authentication": {
            "class": "bearer",
            "environment": TOKEN_ENV,
            "token_present": True,
            "token_recorded": False,
            "secret_store_ref": contract["authentication"][
                "secret_store_ref"
            ],
            "unauthenticated_rejected": True,
            "invalid_token_rejected": True,
        },
        "authority": {
            "persistent_https_witness": persistent,
            "deployment_claimed": persistent,
            "admission_claimed": False,
            "promotion_ready": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_promotion_required": True,
        },
        "workflow": {
            "repository": repository if run_id else None,
            "run_id": run_id,
            "run_url": (
                f"https://github.com/{repository}/actions/runs/{run_id}"
                if run_id
                else None
            ),
        },
        "rollback": contract["rollback"],
        "next_gate": (
            "Admit this exact persistent witness in the Athena control plane; "
            "IC10 remains a separate promotion decision."
            if persistent
            else "Local simulation is not persistent evidence and cannot be admitted."
        ),
    }
    return content_addressed_receipt("p10-persistent-witness", body)


async def probe_persistent_endpoint(
    contract: dict[str, Any],
    token: str,
    *,
    sample_count: int,
    interval_seconds: float,
    timeout: float,
) -> dict[str, Any]:
    if sample_count < MINIMUM_PERSISTENT_SAMPLES:
        raise ValueError(
            f"persistent witness requires {MINIMUM_PERSISTENT_SAMPLES} samples"
        )
    if interval_seconds < 0:
        raise ValueError("sample interval cannot be negative")
    samples = []
    for index in range(sample_count):
        samples.append(
            await sample_endpoint(contract, token, timeout=timeout)
        )
        if index + 1 < sample_count:
            await asyncio.sleep(interval_seconds)
    return build_witness_receipt(
        contract, samples, witness_class="persistent-https"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--samples", type=int, default=MINIMUM_PERSISTENT_SAMPLES
    )
    parser.add_argument(
        "--interval", type=float, default=DEFAULT_INTERVAL_SECONDS
    )
    parser.add_argument("--timeout", type=float, default=20.0)
    arguments = parser.parse_args()

    token = validate_token_from_environment(
        os.environ.get(TOKEN_ENV), argv=sys.argv[1:]
    )
    contract = load_contract(arguments.contract)
    validate_contract(
        contract,
        require_authorized_target=True,
        token=token,
        argv=sys.argv[1:],
    )
    validate_endpoint(contract["network"]["external_mcp_endpoint"])
    receipt = asyncio.run(
        probe_persistent_endpoint(
            contract,
            token,
            sample_count=arguments.samples,
            interval_seconds=arguments.interval,
            timeout=arguments.timeout,
        )
    )
    if receipt["verdict"] != WITNESS_OUTCOME:
        raise RuntimeError("persistent probe did not produce the legal P10 verdict")
    if not secret_free(receipt, token):
        raise RuntimeError("persistent witness receipt contains bearer secret material")
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
