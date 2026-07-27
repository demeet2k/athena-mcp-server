"""Fail-closed security boundary for Athena's remote MCP transport."""
from __future__ import annotations

import hmac
import json
import os
from typing import Any, Awaitable, Callable

ASGIApp = Callable[[dict[str, Any], Callable[..., Awaitable[Any]], Callable[..., Awaitable[Any]]], Awaitable[None]]
TOKEN_ENV = "ATHENA_MCP_BEARER_TOKEN"
ORIGINS_ENV = "ATHENA_MCP_ALLOWED_ORIGINS"


def deployment_health() -> tuple[int, dict[str, Any]]:
    token_present = bool(os.environ.get(TOKEN_ENV))
    body = {
        "status": "ready" if token_present else "blocked",
        "transport": "streamable-http",
        "endpoint": "/mcp",
        "authentication": "bearer",
        "promotion_ready": False,
    }
    if not token_present:
        body["defect"] = f"missing {TOKEN_ENV}"
    return (200 if token_present else 503), body


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


async def _json_response(send: Callable[..., Awaitable[Any]], status: int, body: dict[str, Any]) -> None:
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
    """Require bearer authentication and reject unapproved browser origins."""

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

        headers = _headers(scope)
        expected = os.environ.get(TOKEN_ENV)
        if not expected:
            await _json_response(
                send,
                503,
                {"error": "deployment_not_configured", "missing": TOKEN_ENV},
            )
            return

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
