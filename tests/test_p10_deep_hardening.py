from __future__ import annotations

import asyncio
from copy import deepcopy
import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

import httpx

from scripts.p10_contract import SOURCE_COMMIT
from scripts.p10_persistent_witness import (
    EXPECTED_GRAPH_DIGEST,
    EXPECTED_RESOURCE_COUNT,
    EXPECTED_RESOURCE_INVENTORY_DIGEST,
    EXPECTED_TOOL_COUNT,
    EXPECTED_TOOL_INVENTORY_DIGEST,
    _build_receipt,
    inventory_digest,
    observe_http_boundary,
)
from tests.test_p10_deployment_capsule import authorized_target


ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://athena.authorized.example.com/mcp"
TOKEN = "p10-test-token-0123456789abcdef"


def health() -> dict:
    return {
        "status": "ready",
        "transport": "streamable-http",
        "endpoint": "/mcp",
        "authentication": "bearer",
        "deployed_commit": SOURCE_COMMIT,
        "commit_attested": True,
        "commit_source": "build-locked-file",
        "promotion_ready": False,
    }


class HTTPBoundaryTests(unittest.TestCase):
    def test_direct_health_and_negative_authentication_pass(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/healthz":
                return httpx.Response(200, json=health())
            return httpx.Response(401, json={"error": "unauthorized"})

        observation = asyncio.run(
            observe_http_boundary(
                ENDPOINT,
                TOKEN,
                transport=httpx.MockTransport(handler),
            )
        )
        self.assertTrue(all(observation["checks"].values()))
        self.assertFalse(observation["real_network_contact"])

    def test_redirect_or_wrong_negative_auth_status_fails_closed(self) -> None:
        def redirect(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                307,
                headers={"Location": "https://other.example.com/healthz"},
            )

        with self.assertRaises(RuntimeError):
            asyncio.run(
                observe_http_boundary(
                    ENDPOINT,
                    TOKEN,
                    transport=httpx.MockTransport(redirect),
                )
            )

        def accepts_invalid(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/healthz":
                return httpx.Response(200, json=health())
            return httpx.Response(200, json={"accepted": True})

        with self.assertRaises(RuntimeError):
            asyncio.run(
                observe_http_boundary(
                    ENDPOINT,
                    TOKEN,
                    transport=httpx.MockTransport(accepts_invalid),
                )
            )


class ExactInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        server_path = ROOT / "MCP/athena_mcp_server.py"
        momentum_path = ROOT / "MCP/data/momentum_field.json"
        original_momentum = momentum_path.read_bytes()
        spec = importlib.util.spec_from_file_location(
            "athena_mcp_server_p10_deep_inventory",
            server_path,
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            with mock.patch.dict(
                os.environ,
                {"ATHENA_ROOT": str(ROOT)},
                clear=False,
            ):
                spec.loader.exec_module(module)
        finally:
            momentum_path.write_bytes(original_momentum)
        cls.tool_names = sorted(module.mcp._tool_manager._tools)
        cls.resource_uris = sorted(
            str(uri) for uri in module.mcp._resource_manager._resources
        )

    def exact_observation(self) -> dict:
        cutover = {"promotion_claimed": False}
        boundary_checks = {
            "status_ready": True,
            "transport_streamable_http": True,
            "endpoint_exact": True,
            "authentication_bearer": True,
            "source_commit_exact": True,
            "build_locked_commit_attested": True,
            "promotion_ready_false": True,
            "unauthenticated_rejected": True,
            "invalid_token_rejected": True,
            "redirects_absent": True,
            "https_not_downgraded": True,
        }
        return {
            "initialized": True,
            "catalog": {
                "tools_count": len(self.tool_names),
                "tool_inventory_digest": inventory_digest(self.tool_names),
                "tool_names": self.tool_names,
                "resources_count": len(self.resource_uris),
                "resource_inventory_digest": inventory_digest(
                    self.resource_uris
                ),
                "resource_uris": self.resource_uris,
                "required_tools_present": True,
                "required_resources_present": True,
            },
            "host": health(),
            "http_boundary": {
                "health": health(),
                "checks": boundary_checks,
                "real_network_contact": True,
            },
            "status": {
                "graph_digest": EXPECTED_GRAPH_DIGEST,
                "promotion_ready": False,
            },
            "v2_identity": {
                "verdict": "FOUND",
                "answered_by": "athena-federation-v2",
                "fallback_used": False,
            },
            "v2_route": {
                "verdict": "FOUND",
                "hops": [
                    "edge.q-shrink-to-control",
                    "edge.control-to-runtime",
                ],
                "return_plan": [
                    "edge.runtime-to-control",
                    "edge.control-to-q-shrink",
                ],
            },
            "v1_fallback": {
                "verdict": "FOUND_LEGACY",
                "answered_by": "athena-108d-v1",
                "fallback_used": True,
            },
            "cutover_tool": cutover,
            "cutover_resource": deepcopy(cutover),
        }

    def test_actual_p09_inventory_is_exact(self) -> None:
        self.assertEqual(len(self.tool_names), EXPECTED_TOOL_COUNT)
        self.assertEqual(
            inventory_digest(self.tool_names),
            EXPECTED_TOOL_INVENTORY_DIGEST,
        )
        self.assertEqual(len(self.resource_uris), EXPECTED_RESOURCE_COUNT)
        self.assertEqual(
            inventory_digest(self.resource_uris),
            EXPECTED_RESOURCE_INVENTORY_DIGEST,
        )
        receipt = _build_receipt(
            authorized_target(),
            self.exact_observation(),
        )
        self.assertEqual(
            receipt["verdict"],
            "PASS_LIVE_PERSISTENT_ENDPOINT_NOT_PROMOTED",
        )

    def test_inventory_drift_blocks_sample(self) -> None:
        observation = self.exact_observation()
        observation["catalog"]["tools_count"] -= 1
        observation["catalog"]["tool_names"] = self.tool_names[:-1]
        observation["catalog"]["tool_inventory_digest"] = inventory_digest(
            observation["catalog"]["tool_names"]
        )
        receipt = _build_receipt(authorized_target(), observation)
        self.assertEqual(receipt["verdict"], "HOLD")
        self.assertFalse(receipt["checks"]["actual_tool_count_exact"])
        self.assertFalse(receipt["persistent_deployment_claimed"])
        self.assertFalse(receipt["deployment"]["persistent_endpoint"])


class WorkflowBoundaryTests(unittest.TestCase):
    def test_live_job_is_preflight_ordered_and_uses_one_secret_name(self) -> None:
        workflow = (
            ROOT / ".github/workflows/p10-host-readiness.yml"
        ).read_text(encoding="utf-8")
        readiness = workflow.split("  activation-preflight:", 1)[0]
        self.assertIn("github.event.pull_request.head.sha", readiness)
        self.assertIn('git merge-base "$P09_HEAD" HEAD', readiness)
        self.assertIn("possible secret material found in P10 diff", readiness)
        self.assertIn('"httpx==0.28.1"', readiness)
        self.assertIn('"mcp[cli]==1.28.1"', readiness)
        live = workflow.split("  persistent-witness:", 1)[1]
        self.assertIn("needs: activation-preflight", live)
        self.assertIn("secrets.ATHENA_MCP_BEARER_TOKEN", live)
        self.assertNotIn("ATHENA_P10_BEARER_TOKEN", workflow)
        self.assertIn("PASS_PERSISTENT_HTTPS_WITNESS", live)

    def test_receipt_only_synchronization_cannot_retrigger_p10(self) -> None:
        workflow = (
            ROOT / ".github/workflows/p10-host-readiness.yml"
        ).read_text(encoding="utf-8")
        pull_request = workflow.split("  workflow_dispatch:", 1)[0]
        self.assertIn("types: [opened]", pull_request)
        self.assertNotIn("synchronize", pull_request)
        self.assertIn("paths:", pull_request)
        self.assertNotIn(".athena/receipts", pull_request)
        self.assertNotIn(".athena/status", pull_request)

    def test_token_environment_cannot_be_selected_on_command_line(self) -> None:
        for path in (
            ROOT / "scripts/p10_persistent_witness.py",
            ROOT / "scripts/p10_persistent_observation_window.py",
        ):
            self.assertNotIn(
                "--token-env",
                path.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
