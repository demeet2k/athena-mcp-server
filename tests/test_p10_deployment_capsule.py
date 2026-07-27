from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

from scripts.p10_contract import (
    IMAGE,
    SOURCE_COMMIT,
    target_digest,
    validate_endpoint,
    validate_target,
    validate_token,
)


ROOT = Path(__file__).resolve().parents[1]


def authorized_target() -> dict:
    return {
        "schema": "athena.persistent-host-target/v1",
        "state": "AUTHORIZED",
        "target_id": "athena-p10-primary",
        "endpoint": "https://athena.example.test/mcp",
        "image": IMAGE,
        "source_commit": SOURCE_COMMIT,
        "authorization": {
            "ref": "github-environment:p10-persistent-host",
            "actor": "authorized-operator",
            "authorized_at": "2026-07-27T05:00:00Z",
        },
        "persistence": {
            "class": "self-hosted-service",
            "restart_policy": "unless-stopped",
            "ephemeral": False,
        },
        "tls": {
            "required": True,
            "minimum_version": "1.2",
        },
        "secret": {
            "environment": "ATHENA_MCP_BEARER_TOKEN",
            "provider_ref": (
                "github-environment:p10-persistent-host/"
                "ATHENA_P10_BEARER_TOKEN"
            ),
            "minimum_length": 32,
            "record_value": False,
        },
        "authority": {
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "ic10_required": True,
        },
    }


class TargetContractTests(unittest.TestCase):
    def test_authorized_target_is_deterministic(self) -> None:
        target = authorized_target()
        self.assertEqual(validate_target(target), target)
        self.assertRegex(target_digest(target), r"^sha256:[0-9a-f]{64}$")

    def test_target_rejects_moving_image_tag(self) -> None:
        target = authorized_target()
        target["image"] = "ghcr.io/demeet2k/athena-mcp-server:latest"
        with self.assertRaises(ValueError):
            validate_target(target)

    def test_target_rejects_ephemeral_or_promotional_state(self) -> None:
        for mutation in ("ephemeral", "promotion"):
            target = authorized_target()
            if mutation == "ephemeral":
                target["persistence"]["ephemeral"] = True
            else:
                target["authority"]["promotion_claimed"] = True
            with self.assertRaises(ValueError):
                validate_target(target)

    def test_endpoint_and_secret_fail_closed(self) -> None:
        self.assertEqual(
            validate_endpoint("https://athena.example.test/mcp/"),
            "https://athena.example.test/mcp",
        )
        for endpoint in (
            "http://athena.example.test/mcp",
            "https://athena.example.test/other",
            "https://user:pass@athena.example.test/mcp",
            "https://athena.example.test/mcp?token=forbidden",
        ):
            with self.assertRaises(ValueError):
                validate_endpoint(endpoint)
        with self.assertRaises(ValueError):
            validate_token("short")
        self.assertEqual(validate_token("x" * 32), "x" * 32)


class CapsuleTests(unittest.TestCase):
    def test_readiness_receipt_preserves_null_external_state(self) -> None:
        receipt = json.loads(
            (ROOT / ".athena/receipts/p10-host-readiness.json").read_text()
        )
        self.assertEqual(
            receipt["verdict"],
            "PASS_DEPLOYMENT_CAPSULE_TARGET_PENDING",
        )
        self.assertIsNone(receipt["deployment"]["authorized_target"])
        self.assertIsNone(receipt["deployment"]["https_endpoint"])
        self.assertFalse(receipt["authority"]["promotion_claimed"])

    def test_compose_is_exact_digest_non_root_and_loopback_only(self) -> None:
        compose = (ROOT / "deploy/p10/compose.yaml").read_text()
        self.assertIn(IMAGE, compose)
        self.assertIn('user: "10001:10001"', compose)
        self.assertIn("read_only: true", compose)
        self.assertIn("no-new-privileges:true", compose)
        self.assertIn('"127.0.0.1:', compose)
        self.assertNotIn(":latest", compose)
        self.assertNotRegex(
            compose,
            r"ATHENA_MCP_BEARER_TOKEN:\s*[A-Za-z0-9]{32}",
        )

    def test_caddy_and_workflow_preserve_boundaries(self) -> None:
        caddy = (ROOT / "deploy/p10/Caddyfile").read_text()
        workflow = (
            ROOT / ".github/workflows/p10-host-readiness.yml"
        ).read_text()
        self.assertIn("reverse_proxy 127.0.0.1:", caddy)
        self.assertIn("environment: p10-persistent-host", workflow)
        self.assertIn("secrets.ATHENA_P10_BEARER_TOKEN", workflow)
        self.assertNotIn("ATHENA_P10_BEARER_TOKEN=", workflow)
        uses = re.findall(r"^\s*uses:\s*([^#\s]+)", workflow, re.MULTILINE)
        self.assertTrue(uses)
        for action in uses:
            self.assertRegex(action, r"@[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
