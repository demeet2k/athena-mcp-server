"""Fail-closed security boundary for Athena's remote MCP transport."""
from __future__ import annotations

import hmac
import json
import os
from typing import Any, Awaitable, Callable

ASGIApp = Callable[
    [dict[str, Any], Callable[..., Awaitable[Any]], Callable[..., Awaitable[Any]]],
    Awaitable[None],
]
TOKEN_ENV = "ATHENA_MCP_BEARER_TOKEN"
ORIGINS_ENV = "ATHENA_MCP_ALLOWED_ORIGINS"
COMMIT_ENV = "ATHENA_DEPLOYED_COMMIT"
MINIMUM_TOKEN_LENGTH = 32


def _exact_commit(value: str | None) -> bool:
    return bool(
        value
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value)
    )


def _configuration_defects() -> list[str]:
    defects: list[str] = []
    token = os.environ.get(TOKEN_ENV)
    commit = os.environ.get(COMMIT_ENV)
    if not token:
        defects.append(f"missing {TOKEN_ENV}")
    elif len(token) < MINIMUM_TOKEN_LENGTH:
        defects.append(f"{TOKEN_ENV} must contain at least {MINIMUM_TOKEN_LENGTH} characters")
    if not commit:
        defects.append(f"missing {COMMIT_ENV}")
    elif not _exact_commit(commit):
        defects.append(f"{COMMIT_ENV} must be an exact lowercase 40-hex commit")
    return defects


def deployment_health() -> tuple[int, dict[str, Any]]:
    defects = _configuration_defects()
    commit = os.environ.get(COMMIT_ENV)
    ready = not defects
    body: dict[str, Any] = {
        "status": "ready" if ready else "blocked",
        "transport": "streamable-http",
        "endpoint": "/mcp",
        "authentication": "bearer",
        "deployed_commit": commit if _exact_commit(commit) else None,
        "commit_attested": ready and _exact_commit(commit),
        "promotion_ready": False,
    }
    if defects:
        body["defects"] = defects
    return (200 if ready else 503), body


def _headers(scope: dict[str, Any]) -> dict[str, str]:
    return {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in scope.get("headers", [])
    }


def _allowed_origins() -> frozenset[str]:
    return frozenset(
        item.strip()
        for item in os.environ.get(ORIGINS_ENV, "").split(",")
        if item.strip()
    )


async def _json_response(
    send: Callable[..., Awaitable[Any]],
    status: int,
    body: dict[str, Any],
) -> None:
    content = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(content)).encode("ascii")),
                (b"cache-control", b"no-store"),
            ],
        }
    )
    await send({"type": "http.response.body", "body": content})


class MCPHTTPBoundary:
    """Require a valid deployment lock, bearer authentication, and safe origin."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Awaitable[Any]],
        send: Callable[..., Awaitable[Any]],
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        defects = _configuration_defects()
        if defects:
            await _json_response(
                send,
                503,
                {"error": "deployment_not_configured", "defects": defects},
            )
            return

        headers = _headers(scope)
        expected = os.environ[TOKEN_ENV]
        observed = headers.get("authorization", "")
        expected_header = f"Bearer {expected}"
        if not hmac.compare_digest(observed, expected_header):
            await _json_response(send, 401, {"error": "unauthorized"})
            return

        origin = headers.get("origin")
        allowed = _allowed_origins()
        if origin is not None and origin not in allowed:
            await _json_response(
                send,
                403,
                {"error": "origin_not_allowed", "origin": origin},
            )
            return

        await self.app(scope, receive, send)
