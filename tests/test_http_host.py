from __future__ import annotations

import asyncio
import json
import os
import unittest
from unittest.mock import patch

from MCP.http_security import MCPHTTPBoundary, deployment_health


async def _receive():
    return {"type": "http.request", "body": b"", "more_body": False}


class HTTPBoundaryTests(unittest.TestCase):
    def run_request(self, headers=()):
        called = []
        messages = []

        async def downstream(scope, receive, send):
            called.append(scope)
            await send({"type": "http.response.start", "status": 204, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        async def send(message):
            messages.append(message)

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/mcp",
            "headers": [
                (key.lower().encode("latin-1"), value.encode("latin-1"))
                for key, value in headers
            ],
        }
        asyncio.run(MCPHTTPBoundary(downstream)(scope, _receive, send))
        return called, messages

    def test_missing_deployment_token_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            called, messages = self.run_request()
            status, health = deployment_health()
        self.assertEqual(called, [])
        self.assertEqual(messages[0]["status"], 503)
        self.assertEqual(status, 503)
        self.assertEqual(health["promotion_ready"], False)

    def test_invalid_bearer_is_rejected(self):
        with patch.dict(os.environ, {"ATHENA_MCP_BEARER_TOKEN": "correct"}, clear=True):
            called, messages = self.run_request((("Authorization", "Bearer wrong"),))
        self.assertEqual(called, [])
        self.assertEqual(messages[0]["status"], 401)

    def test_unapproved_browser_origin_is_rejected(self):
        environment = {
            "ATHENA_MCP_BEARER_TOKEN": "correct",
            "ATHENA_MCP_ALLOWED_ORIGINS": "https://athena.example",
        }
        with patch.dict(os.environ, environment, clear=True):
            called, messages = self.run_request(
                (
                    ("Authorization", "Bearer correct"),
                    ("Origin", "https://wrong.example"),
                )
            )
        self.assertEqual(called, [])
        self.assertEqual(messages[0]["status"], 403)
        body = json.loads(messages[1]["body"])
        self.assertEqual(body["error"], "origin_not_allowed")

    def test_authorized_nonbrowser_client_reaches_mcp(self):
        with patch.dict(os.environ, {"ATHENA_MCP_BEARER_TOKEN": "correct"}, clear=True):
            called, messages = self.run_request((("Authorization", "Bearer correct"),))
            status, health = deployment_health()
        self.assertEqual(len(called), 1)
        self.assertEqual(messages[0]["status"], 204)
        self.assertEqual(status, 200)
        self.assertEqual(health["status"], "ready")


if __name__ == "__main__":
    unittest.main()
