from __future__ import annotations

import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from MCP.http_security import MCPHTTPBoundary, deployment_health
from scripts.host_attestation import health_url, validate_host_attestation


async def _receive():
    return {"type": "http.request", "body": b"", "more_body": False}


TOKEN = "t" * 32
COMMIT = "a" * 40


class HTTPBoundaryTests(unittest.TestCase):
    def run_request(self, headers=()):
        called = []
        messages = []

        async def downstream(scope, receive, send):
            called.append(scope)
            await send(
                {"type": "http.response.start", "status": 204, "headers": []}
            )
            await send({"type": "http.response.body", "body": b""})

        async def send(message):
            messages.append(message)

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/mcp",
            "headers": [
                (
                    key.lower().encode("latin-1"),
                    value.encode("latin-1"),
                )
                for key, value in headers
            ],
        }
        asyncio.run(MCPHTTPBoundary(downstream)(scope, _receive, send))
        return called, messages

    def test_missing_deployment_token_fails_closed(self):
        with patch.dict(os.environ, {"ATHENA_DEPLOYED_COMMIT": COMMIT}, clear=True):
            called, messages = self.run_request()
            status, health = deployment_health()
        self.assertEqual(called, [])
        self.assertEqual(messages[0]["status"], 503)
        self.assertEqual(status, 503)
        self.assertFalse(health["commit_attested"])
        self.assertFalse(health["promotion_ready"])

    def test_missing_deployed_commit_fails_closed(self):
        with patch.dict(
            os.environ,
            {"ATHENA_MCP_BEARER_TOKEN": TOKEN},
            clear=True,
        ):
            called, messages = self.run_request(
                (("Authorization", f"Bearer {TOKEN}"),)
            )
            status, health = deployment_health()
        self.assertEqual(called, [])
        self.assertEqual(messages[0]["status"], 503)
        self.assertEqual(status, 503)
        self.assertIsNone(health["deployed_commit"])

    def test_invalid_deployed_commit_fails_closed(self):
        environment = {
            "ATHENA_MCP_BEARER_TOKEN": TOKEN,
            "ATHENA_DEPLOYED_COMMIT": "not-a-commit",
        }
        with patch.dict(os.environ, environment, clear=True):
            called, messages = self.run_request(
                (("Authorization", f"Bearer {TOKEN}"),)
            )
        self.assertEqual(called, [])
        self.assertEqual(messages[0]["status"], 503)

    def test_invalid_bearer_is_rejected(self):
        environment = {
            "ATHENA_MCP_BEARER_TOKEN": TOKEN,
            "ATHENA_DEPLOYED_COMMIT": COMMIT,
        }
        with patch.dict(os.environ, environment, clear=True):
            called, messages = self.run_request(
                (("Authorization", "Bearer wrong"),)
            )
        self.assertEqual(called, [])
        self.assertEqual(messages[0]["status"], 401)

    def test_unapproved_browser_origin_is_rejected(self):
        environment = {
            "ATHENA_MCP_BEARER_TOKEN": TOKEN,
            "ATHENA_DEPLOYED_COMMIT": COMMIT,
            "ATHENA_MCP_ALLOWED_ORIGINS": "https://athena.example",
        }
        with patch.dict(os.environ, environment, clear=True):
            called, messages = self.run_request(
                (
                    ("Authorization", f"Bearer {TOKEN}"),
                    ("Origin", "https://wrong.example"),
                )
            )
        self.assertEqual(called, [])
        self.assertEqual(messages[0]["status"], 403)
        body = json.loads(messages[1]["body"])
        self.assertEqual(body["error"], "origin_not_allowed")

    def test_authorized_nonbrowser_client_reaches_mcp(self):
        environment = {
            "ATHENA_MCP_BEARER_TOKEN": TOKEN,
            "ATHENA_DEPLOYED_COMMIT": COMMIT,
        }
        with patch.dict(os.environ, environment, clear=True):
            called, messages = self.run_request(
                (("Authorization", f"Bearer {TOKEN}"),)
            )
            status, health = deployment_health()
        self.assertEqual(len(called), 1)
        self.assertEqual(messages[0]["status"], 204)
        self.assertEqual(status, 200)
        self.assertEqual(health["status"], "ready")
        self.assertEqual(health["deployed_commit"], COMMIT)
        self.assertTrue(health["commit_attested"])

    def test_build_locked_commit_file_overrides_runtime_commit(self):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as handle:
            handle.write(COMMIT + "\n")
            handle.flush()
            environment = {
                "ATHENA_MCP_BEARER_TOKEN": TOKEN,
                "ATHENA_DEPLOYED_COMMIT": "b" * 40,
                "ATHENA_DEPLOYED_COMMIT_FILE": handle.name,
            }
            with patch.dict(os.environ, environment, clear=True):
                status, health = deployment_health()
        self.assertEqual(status, 200)
        self.assertEqual(health["deployed_commit"], COMMIT)
        self.assertEqual(health["commit_source"], "build-locked-file")

    def test_health_url_is_derived_from_exact_mcp_endpoint(self):
        self.assertEqual(
            health_url("https://athena.example/mcp"),
            "https://athena.example/healthz",
        )
        with self.assertRaises(ValueError):
            health_url("http://athena.example/mcp")

    def test_host_attestation_requires_exact_commit_match(self):
        health = {
            "status": "ready",
            "endpoint": "/mcp",
            "deployed_commit": COMMIT,
            "commit_attested": True,
            "promotion_ready": False,
        }
        self.assertIs(validate_host_attestation(health, COMMIT), health)
        with self.assertRaises(RuntimeError):
            validate_host_attestation(health, "b" * 40)


if __name__ == "__main__":
    unittest.main()
