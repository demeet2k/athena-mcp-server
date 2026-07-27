#!/usr/bin/env python3
"""Probe a deployed Athena MCP host and emit a non-promotional P07 witness."""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

try:
    from scripts.host_attestation import exact_git_commit, fetch_host_attestation
except ModuleNotFoundError:
    from host_attestation import exact_git_commit, fetch_host_attestation


def _dump(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


async def probe(endpoint: str, token: str, expected_commit: str) -> dict[str, Any]:
    host_attestation = fetch_host_attestation(endpoint, expected_commit)
    headers = {"Authorization": f"Bearer {token}"}
    async with streamablehttp_client(endpoint, headers=headers) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            status = await session.call_tool("athena_federation_status", {})
            exact = await session.call_tool(
                "resolve_athena_identity",
                {"identifier": "athena.repo.q-shrink"},
            )
            fallback = await session.call_tool(
                "resolve_athena_identity",
                {"identifier": "athena://crystal-108d"},
            )
            cutover = await session.call_tool(
                "athena_federation_cutover_receipt",
                {},
            )
            resources = await session.list_resources()

    return {
        "schema": "athena.mcp-host-deployment-witness/v1",
        "phase": "P07",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "deployed_commit": host_attestation["deployed_commit"],
        "transport": "streamable-http",
        "authentication": "bearer-token-present-not-recorded",
        "probes": {
            "host_attestation": host_attestation,
            "status": _dump(status),
            "exact_v2_identity": _dump(exact),
            "explicit_v1_fallback": _dump(fallback),
            "cutover": _dump(cutover),
            "resources": _dump(resources),
        },
        "promotion_claimed": False,
        "verdict": "WITNESSED_NOT_PROMOTED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("endpoint", help="HTTPS MCP endpoint ending in /mcp")
    parser.add_argument("expected_commit", help="exact 40-hex commit expected on host")
    parser.add_argument("--token-env", default="ATHENA_MCP_BEARER_TOKEN")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    token = os.environ.get(args.token_env)
    if not token:
        raise SystemExit(
            f"missing bearer token environment variable: {args.token_env}"
        )
    if not args.endpoint.startswith("https://") or not args.endpoint.rstrip(
        "/"
    ).endswith("/mcp"):
        raise SystemExit("endpoint must be HTTPS and end in /mcp")
    if not exact_git_commit(args.expected_commit):
        raise SystemExit("expected_commit must be an exact lowercase 40-hex commit")

    receipt = asyncio.run(probe(args.endpoint, token, args.expected_commit))
    content = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
