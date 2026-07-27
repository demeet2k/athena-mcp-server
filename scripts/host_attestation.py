"""Exact host-commit attestation helpers for the P07 live probe."""
from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen


def exact_git_commit(value: str) -> bool:
    return len(value) == 40 and all(
        character in "0123456789abcdef" for character in value
    )


def health_url(endpoint: str) -> str:
    parts = urlsplit(endpoint)
    if parts.scheme != "https" or parts.query or parts.fragment:
        raise ValueError("endpoint must be a query-free HTTPS URL")
    if parts.path.rstrip("/") != "/mcp":
        raise ValueError("endpoint path must end exactly in /mcp")
    return urlunsplit((parts.scheme, parts.netloc, "/healthz", "", ""))


def validate_host_attestation(
    health: dict[str, Any],
    expected_commit: str,
) -> dict[str, Any]:
    if not exact_git_commit(expected_commit):
        raise ValueError("expected commit must be exact lowercase 40-hex")
    if health.get("status") != "ready":
        raise RuntimeError("host health is not ready")
    if health.get("endpoint") != "/mcp":
        raise RuntimeError("host attests the wrong MCP path")
    if health.get("deployed_commit") != expected_commit:
        raise RuntimeError("host commit does not match the expected deployment commit")
    if health.get("commit_attested") is not True:
        raise RuntimeError("host did not attest its commit")
    if health.get("promotion_ready") is not False:
        raise RuntimeError("host crossed the non-promotional P07 boundary")
    return health


def fetch_host_attestation(
    endpoint: str,
    expected_commit: str,
    *,
    timeout: float = 10.0,
) -> dict[str, Any]:
    request = Request(
        health_url(endpoint),
        headers={"Accept": "application/json"},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        health = json.load(response)
    if not isinstance(health, dict):
        raise RuntimeError("host health response must be a JSON object")
    return validate_host_attestation(health, expected_commit)
