#!/usr/bin/env python3
"""Launch Athena through a real MCP stdio host and emit a P07 witness.

This is deliberately a transport-level probe.  It does not import or call the
federation consumer directly: every observation crosses the MCP initialize,
tools/list, resources/list, tools/call, and resources/read boundaries.
"""

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

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "MCP" / "athena_mcp_server.py"
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


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


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
    """Remove the SDK's optional single-result envelope."""
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
    raise RuntimeError(f"MCP tool result did not contain a JSON object: {result!r}")


def _resource_payload(result: Any) -> dict[str, Any]:
    for content in getattr(result, "contents", []):
        text = getattr(content, "text", None)
        if not text:
            continue
        decoded = json.loads(text)
        if isinstance(decoded, dict):
            return decoded
    raise RuntimeError(f"MCP resource did not contain a JSON object: {result!r}")


async def _observe() -> dict[str, Any]:
    child_env = dict(os.environ)
    child_env["ATHENA_ROOT"] = str(ROOT)
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER)],
        env=child_env,
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            tool_catalog = await session.list_tools()
            resource_catalog = await session.list_resources()

            tool_names = sorted(tool.name for tool in tool_catalog.tools)
            resource_uris = sorted(
                str(resource.uri) for resource in resource_catalog.resources
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
                    "athena_federation_cutover_receipt", arguments={}
                )
            )
            cutover_resource = _resource_payload(
                await session.read_resource("athena://federation-v2/cutover")
            )

    return {
        "initialize": _jsonable(initialized),
        "catalog": {
            "tools_count": len(tool_names),
            "resources_count": len(resource_uris),
            "required_tools": sorted(EXPECTED_TOOLS),
            "required_resources": sorted(EXPECTED_RESOURCES),
            "required_tools_present": EXPECTED_TOOLS.issubset(tool_names),
            "required_resources_present": EXPECTED_RESOURCES.issubset(
                resource_uris
            ),
        },
        "answers": {
            "status": status,
            "v2_identity": v2_identity,
            "v2_route": v2_route,
            "v1_fallback": v1_fallback,
            "cutover_tool": cutover_tool,
            "cutover_resource": cutover_resource,
        },
    }


def _build_receipt(observation: dict[str, Any]) -> dict[str, Any]:
    answers = observation["answers"]
    route = answers["v2_route"]
    v1 = answers["v1_fallback"]
    status = answers["status"]
    cutover_tool = answers["cutover_tool"]
    cutover_resource = answers["cutover_resource"]

    checks = {
        "mcp_initialize": bool(observation["initialize"]),
        "required_tools_present": observation["catalog"][
            "required_tools_present"
        ],
        "required_resources_present": observation["catalog"][
            "required_resources_present"
        ],
        "frozen_graph_exact": status.get("graph_digest")
        == EXPECTED_GRAPH_DIGEST,
        "v2_identity_answered": (
            answers["v2_identity"].get("verdict") == "FOUND"
            and answers["v2_identity"].get("answered_by")
            == "athena-federation-v2"
            and answers["v2_identity"].get("fallback_used") is False
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
            v1.get("verdict") == "FOUND_LEGACY"
            and v1.get("answered_by") == "athena-108d-v1"
            and v1.get("fallback_used") is True
        ),
        "tool_resource_receipts_equal": cutover_tool == cutover_resource,
        "promotion_boundary": (
            status.get("promotion_ready") is False
            and cutover_tool.get("promotion_claimed") is False
        ),
    }

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if now.endswith("+00:00"):
        now = f"{now[:-6]}Z"
    repository = os.environ.get(
        "GITHUB_REPOSITORY", "demeet2k/athena-mcp-server"
    )
    run_id = os.environ.get("GITHUB_RUN_ID")
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_url = (
        f"{server_url}/{repository}/actions/runs/{run_id}" if run_id else None
    )
    body = {
        "schema": "athena.mcp-host-witness/v2",
        "phase": "P07",
        "seed": (
            "KC144.MYC.SKELETON.P07::"
            "HOSTED-RUNTIME-DEPLOYMENT-AND-CONTROL-PLANE-ADMISSION"
        ),
        "verdict": (
            "PASS_LIVE_EPHEMERAL_MCP_HOST"
            if all(checks.values())
            else "HOLD"
        ),
        "observed_at": now,
        "repository": repository,
        "witnessed_commit": os.environ.get("GITHUB_SHA"),
        "deployment": {
            "class": "github-actions-ephemeral-stdio",
            "transport": "stdio",
            "server_entrypoint": "MCP/athena_mcp_server.py",
            "client_probe": "scripts/p07_mcp_host_witness.py",
            "workflow": os.environ.get("GITHUB_WORKFLOW"),
            "job": os.environ.get("GITHUB_JOB"),
            "run_id": run_id,
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "run_url": run_url,
            "persistent_endpoint": False,
        },
        "checks": checks,
        "catalog": observation["catalog"],
        "answer_provenance": {
            "v2_identity": {
                "identifier": V2_IDENTIFIER,
                "verdict": answers["v2_identity"].get("verdict"),
                "answered_by": answers["v2_identity"].get("answered_by"),
                "fallback_used": answers["v2_identity"].get("fallback_used"),
                "resource": answers["v2_identity"].get("resource", {}).get(
                    "rid"
                ),
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
                "verdict": v1.get("verdict"),
                "answered_by": v1.get("answered_by"),
                "fallback_used": v1.get("fallback_used"),
            },
        },
        "frozen_source": {
            "control_repository": status.get("control_repository"),
            "control_commit": status.get("control_commit"),
            "release_candidate": status.get("release_candidate"),
            "selected_contract_lineage": status.get(
                "selected_contract_lineage"
            ),
            "graph_digest": status.get("graph_digest"),
            "cold_replay": status.get("cold_replay"),
        },
        "rollback": cutover_tool.get("rollback"),
        "promotion_claimed": False,
        "merge_claimed": False,
        "persistent_deployment_claimed": False,
        "next_gate": (
            "Admit this exact hosted witness in the Athena control plane; "
            "persistent endpoint promotion remains a separate gate."
        ),
    }
    return {
        "receipt_id": f"mcp-host:sha256:{sha256(_canonical_bytes(body)).hexdigest()}",
        **body,
    }


async def _main(output: Path, timeout: int) -> int:
    async with asyncio.timeout(timeout):
        observation = await _observe()
    receipt = _build_receipt(observation)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["verdict"].startswith("PASS_") else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("p07-mcp-host-witness.json"),
    )
    parser.add_argument("--timeout", type=int, default=120)
    arguments = parser.parse_args()
    return asyncio.run(_main(arguments.output, arguments.timeout))


if __name__ == "__main__":
    raise SystemExit(main())
