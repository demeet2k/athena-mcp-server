#!/usr/bin/env python3
"""Replay Athena across an authorized persistent HTTPS MCP endpoint."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

try:
    from scripts.p10_contract import (
        SOURCE_COMMIT,
        canonical_bytes,
        health_url,
        target_digest,
        validate_target,
        validate_token,
    )
except ModuleNotFoundError:
    from p10_contract import (
        SOURCE_COMMIT,
        canonical_bytes,
        health_url,
        target_digest,
        validate_target,
        validate_token,
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
EXPECTED_TOOL_COUNT = 174
EXPECTED_TOOL_INVENTORY_DIGEST = (
    "sha256:230b41262dd77cc7e73f1acb3afcbc8de67bb52e680f35abfebb3465620fc34c"
)
EXPECTED_RESOURCE_COUNT = 27
EXPECTED_RESOURCE_INVENTORY_DIGEST = (
    "sha256:6e74961966019708425aa26ed6bddb0c665cfffacb1ef7e44494f8861deb9eea"
)


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
    """Verify direct health plus unauthenticated and invalid-token rejection."""
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
            health_response,
            derived_health_url,
            200,
            "health endpoint",
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
            unauthenticated,
            endpoint,
            401,
            "unauthenticated MCP request",
        )

        invalid = await client.post(
            endpoint,
            headers={
                **headers,
                "Authorization": f"Bearer {invalid_token}",
            },
            json=request_body,
        )
        _require_direct_response(
            invalid,
            endpoint,
            401,
            "invalid-token MCP request",
        )

    checks = {
        "status_ready": health.get("status") == "ready",
        "transport_streamable_http": (
            health.get("transport") == "streamable-http"
        ),
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
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError("HTTP boundary failed: " + ", ".join(failed))
    return {
        "health": health,
        "checks": checks,
        "real_network_contact": transport is None,
    }


async def _observe(target: dict[str, Any], token: str) -> dict[str, Any]:
    endpoint = target["endpoint"]
    boundary = await observe_http_boundary(endpoint, token, timeout=20)
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
            tools = await session.list_tools()
            resources = await session.list_resources()
            tool_names = sorted(tool.name for tool in tools.tools)
            resource_uris = sorted(
                str(resource.uri) for resource in resources.resources
            )
            status = _tool_payload(
                await session.call_tool("athena_federation_status", arguments={})
            )
            v2_identity = _tool_payload(
                await session.call_tool(
                    "resolve_athena_identity",
                    arguments={"identifier": V2_IDENTIFIER},
                )
            )
            v2_route = _tool_payload(
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
            v1_fallback = _tool_payload(
                await session.call_tool(
                    "resolve_athena_identity",
                    arguments={"identifier": V1_IDENTIFIER},
                )
            )
            cutover_tool = _tool_payload(
                await session.call_tool(
                    "athena_federation_cutover_receipt",
                    arguments={},
                )
            )
            cutover_resource = _resource_payload(
                await session.read_resource("athena://federation-v2/cutover")
            )

    return {
        "initialized": bool(_jsonable(initialized)),
        "catalog": {
            "tools_count": len(tool_names),
            "tool_inventory_digest": inventory_digest(tool_names),
            "tool_names": tool_names,
            "resources_count": len(resource_uris),
            "resource_inventory_digest": inventory_digest(resource_uris),
            "resource_uris": resource_uris,
            "required_tools_present": EXPECTED_TOOLS.issubset(
                set(tool_names)
            ),
            "required_resources_present": EXPECTED_RESOURCES.issubset(
                set(resource_uris)
            ),
        },
        "host": boundary["health"],
        "http_boundary": boundary,
        "status": status,
        "v2_identity": v2_identity,
        "v2_route": v2_route,
        "v1_fallback": v1_fallback,
        "cutover_tool": cutover_tool,
        "cutover_resource": cutover_resource,
    }


def _build_receipt(
    target: dict[str, Any],
    observation: dict[str, Any],
) -> dict[str, Any]:
    route = observation["v2_route"]
    v1 = observation["v1_fallback"]
    status = observation["status"]
    checks = {
        "mcp_initialize": observation["initialized"],
        "real_network_contact": (
            observation["http_boundary"]["real_network_contact"] is True
        ),
        "host_commit_attested": (
            observation["host"]["deployed_commit"] == target["source_commit"]
            and observation["host"]["commit_attested"] is True
            and observation["host"]["commit_source"] == "build-locked-file"
        ),
        "required_tools_present": observation["catalog"][
            "required_tools_present"
        ],
        "actual_tool_count_exact": (
            observation["catalog"]["tools_count"] == EXPECTED_TOOL_COUNT
        ),
        "actual_tool_inventory_exact": (
            observation["catalog"]["tool_inventory_digest"]
            == EXPECTED_TOOL_INVENTORY_DIGEST
        ),
        "required_resources_present": observation["catalog"][
            "required_resources_present"
        ],
        "actual_resource_count_exact": (
            observation["catalog"]["resources_count"]
            == EXPECTED_RESOURCE_COUNT
        ),
        "actual_resource_inventory_exact": (
            observation["catalog"]["resource_inventory_digest"]
            == EXPECTED_RESOURCE_INVENTORY_DIGEST
        ),
        "unauthenticated_rejected": observation["http_boundary"]["checks"][
            "unauthenticated_rejected"
        ],
        "invalid_token_rejected": observation["http_boundary"]["checks"][
            "invalid_token_rejected"
        ],
        "redirects_absent": observation["http_boundary"]["checks"][
            "redirects_absent"
        ],
        "https_not_downgraded": observation["http_boundary"]["checks"][
            "https_not_downgraded"
        ],
        "frozen_graph_exact": (
            status.get("graph_digest") == EXPECTED_GRAPH_DIGEST
        ),
        "v2_identity_answered": (
            observation["v2_identity"].get("verdict") == "FOUND"
            and observation["v2_identity"].get("answered_by")
            == "athena-federation-v2"
            and observation["v2_identity"].get("fallback_used") is False
        ),
        "v2_route_answered": (
            route.get("verdict") == "FOUND"
            and route.get("hops")
            == ["edge.q-shrink-to-control", "edge.control-to-runtime"]
        ),
        "reciprocal_return_answered": (
            route.get("return_plan")
            == ["edge.runtime-to-control", "edge.control-to-q-shrink"]
        ),
        "explicit_v1_fallback_answered": (
            v1.get("verdict") == "FOUND_LEGACY"
            and v1.get("answered_by") == "athena-108d-v1"
            and v1.get("fallback_used") is True
        ),
        "tool_resource_receipts_equal": (
            observation["cutover_tool"] == observation["cutover_resource"]
        ),
        "promotion_boundary": (
            observation["host"].get("promotion_ready") is False
            and status.get("promotion_ready") is False
            and observation["cutover_tool"].get("promotion_claimed") is False
        ),
    }
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if now.endswith("+00:00"):
        now = now[:-6] + "Z"
    run_id = os.environ.get("GITHUB_RUN_ID")
    repository = os.environ.get(
        "GITHUB_REPOSITORY",
        "demeet2k/athena-mcp-server",
    )
    run_url = (
        f"https://github.com/{repository}/actions/runs/{run_id}"
        if run_id
        else None
    )
    passed = all(checks.values())
    body = {
        "schema": "athena.persistent-mcp-witness/v1",
        "phase": "P10",
        "seed": (
            "KC144.MYC.SKELETON.P10::"
            "AUTHORIZED-HTTPS-ENDPOINT-AND-PERSISTENT-WITNESS"
        ),
        "verdict": (
            "PASS_LIVE_PERSISTENT_ENDPOINT_NOT_PROMOTED"
            if passed
            else "HOLD"
        ),
        "observed_at": now,
        "target": {
            "target_id": target["target_id"],
            "target_digest": target_digest(target),
            "endpoint": target["endpoint"],
            "persistence_class": target["persistence"]["class"],
            "authorization_ref": target["authorization"]["ref"],
        },
        "deployment": {
            "image": target["image"],
            "image_selection_attestation": "authorized-target-contract",
            "source_commit": target["source_commit"],
            "source_commit_attestation": "host-health-build-locked-file",
            "transport": "streamable-http",
            "authentication": "bearer-present-value-not-recorded",
            "persistent_endpoint": passed,
        },
        "checks": checks,
        "catalog": observation["catalog"],
        "answer_provenance": {
            "v2_identity": observation["v2_identity"],
            "v2_route": observation["v2_route"],
            "v1_fallback": observation["v1_fallback"],
        },
        "workflow_run": run_url,
        "secret_recorded": False,
        "persistent_deployment_claimed": passed,
        "promotion_ready": False,
        "promotion_claimed": False,
        "merge_claimed": False,
        "next_gate": (
            "Admit this exact persistent witness in the Athena control plane; "
            "IC10 remains required for any promotion decision."
        ),
        "successor_seed": (
            "KC144.MYC.SKELETON.P11::"
            "PERSISTENT-WITNESS-ADMISSION-AND-IC10-READINESS"
        ),
    }
    return {
        "receipt_id": (
            "persistent-mcp:sha256:"
            + sha256(canonical_bytes(body)).hexdigest()
        ),
        **body,
    }


async def _main(
    target_path: Path,
    output_path: Path,
    timeout: int,
) -> int:
    target = validate_target(json.loads(target_path.read_text(encoding="utf-8")))
    token = validate_token(os.environ.get("ATHENA_MCP_BEARER_TOKEN"))
    async with asyncio.timeout(timeout):
        observation = await _observe(target, token)
    receipt = _build_receipt(target, observation)
    output_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["verdict"].startswith("PASS_") else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--output", type=Path, default=Path("p10-witness.json"))
    parser.add_argument("--timeout", type=int, default=180)
    arguments = parser.parse_args()
    return asyncio.run(
        _main(
            arguments.target,
            arguments.output,
            arguments.timeout,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
