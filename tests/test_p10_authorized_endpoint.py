from __future__ import annotations

import asyncio
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import unittest
from unittest import mock

import httpx
import yaml

from scripts.p10_contract import (
    AUTHORIZED_STATE,
    IMAGE_REFERENCE,
    PREPARED_OUTCOME,
    SOURCE_COMMIT,
    TOKEN_ENV,
    ContractError,
    load_contract,
    materialize_authorized_contract,
    secret_free,
    validate_contract,
    validate_endpoint,
    validate_token_from_environment,
)
from scripts.p10_persistent_witness import (
    EXPECTED_GRAPH_DIGEST,
    EXPECTED_RESOURCE_COUNT,
    EXPECTED_RESOURCE_INVENTORY_DIGEST,
    EXPECTED_TOOL_COUNT,
    EXPECTED_TOOL_INVENTORY_DIGEST,
    build_witness_receipt,
    inventory_digest,
    observe_http_boundary,
    validate_mcp_observation,
)
from scripts.p10_preflight import authorized_receipt, prepared_receipt


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "deploy/p10/host-contract.json"
TOKEN = "p10-test-token-that-is-long-enough-and-never-recorded"
ENDPOINT = "https://athena.authorized.example.net/mcp"


def prepared_contract() -> dict:
    return load_contract(CONTRACT_PATH)


def authorized_contract() -> dict:
    return materialize_authorized_contract(
        prepared_contract(),
        endpoint=ENDPOINT,
        provider_id="existing-authorized-provider",
        provider_account_scope="existing-authorized-account-scope",
        deployment_id="athena-p10-primary",
        persistence_class="managed-container-service",
        authorization_ref="change-control:athena-p10",
        authorized_by="authorized-operator",
        authorized_at="2026-07-27T06:00:00Z",
        secret_store_ref=(
            "github-environment:p10-persistent-host/"
            "ATHENA_MCP_BEARER_TOKEN"
        ),
    )


def fake_sample(*, real_network_contact: bool) -> dict:
    checks = {
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
    mcp_checks = {
        "streamable_http_initialized": True,
        "actual_tool_count_exact": True,
        "actual_tool_inventory_exact": True,
        "required_tools_present": True,
        "actual_resource_count_exact": True,
        "actual_resource_inventory_exact": True,
        "required_resources_present": True,
        "frozen_graph_exact": True,
        "v2_identity_exact": True,
        "v2_route_exact": True,
        "reciprocal_return_exact": True,
        "explicit_athena_108d_v1_fallback": True,
        "cutover_tool_resource_equal": True,
        "promotion_ready_false": True,
    }
    return {
        "observed_at": "2026-07-27T06:00:00Z",
        "real_network_contact": real_network_contact,
        "http_checks": checks,
        "health": {
            "status": "ready",
            "transport": "streamable-http",
            "endpoint": "/mcp",
            "authentication": "bearer",
            "deployed_commit": SOURCE_COMMIT,
            "commit_attested": True,
            "commit_source": "build-locked-file",
            "promotion_ready": False,
        },
        "mcp_checks": mcp_checks,
        "catalog": {
            "tool_count": EXPECTED_TOOL_COUNT,
            "tool_inventory_digest": EXPECTED_TOOL_INVENTORY_DIGEST,
            "tool_names": sorted(
                [
                    "athena_federation_cutover_receipt",
                    "athena_federation_status",
                    "resolve_athena_identity",
                    "route_athena_federation",
                ]
            ),
            "resource_count": EXPECTED_RESOURCE_COUNT,
            "resource_inventory_digest": EXPECTED_RESOURCE_INVENTORY_DIGEST,
            "resource_uris": sorted(
                [
                    "athena://federation-v2",
                    "athena://federation-v2/cutover",
                    "athena://federation-v2/lock",
                ]
            ),
        },
        "answer_provenance": {
            "v2_identity": {
                "identifier": (
                    "amc://github/compression/repo-q-shrink@0.1.0"
                    "?lens=11#codec"
                ),
                "verdict": "FOUND",
                "answered_by": "athena-federation-v2",
                "fallback_used": False,
                "resource": "athena.repo.q-shrink",
            },
            "v2_route": {
                "source": "athena.repo.q-shrink",
                "target": "athena.runtime.route-compiler",
                "hops": [
                    "edge.q-shrink-to-control",
                    "edge.control-to-runtime",
                ],
                "return_plan": [
                    "edge.runtime-to-control",
                    "edge.control-to-q-shrink",
                ],
                "answered_by": "athena-federation-v2",
                "fallback_used": False,
            },
            "v1_fallback": {
                "identifier": "athena://crystal-108d",
                "verdict": "FOUND_LEGACY",
                "answered_by": "athena-108d-v1",
                "fallback_used": True,
            },
        },
    }


class PreparedContractTests(unittest.TestCase):
    def test_prepared_contract_is_exact_and_null_authority(self) -> None:
        contract = prepared_contract()
        self.assertIs(
            validate_contract(contract, require_authorized_target=False),
            contract,
        )
        self.assertEqual(contract["outcome"], PREPARED_OUTCOME)
        self.assertIsNone(contract["network"]["external_mcp_endpoint"])
        self.assertIsNone(contract["authentication"]["secret_store_ref"])
        self.assertFalse(contract["authority"]["deployment_claimed"])

    def test_mutable_or_wrong_image_is_rejected(self) -> None:
        for reference in (
            "ghcr.io/demeet2k/athena-mcp-server:latest",
            IMAGE_REFERENCE.replace("31458783", "41458783"),
        ):
            contract = prepared_contract()
            contract["image"]["reference"] = reference
            with self.assertRaises(ContractError):
                validate_contract(contract, require_authorized_target=False)

    def test_wrong_digest_or_source_commit_is_rejected(self) -> None:
        contract = prepared_contract()
        contract["image"]["digest"] = "sha256:" + "0" * 64
        with self.assertRaises(ContractError):
            validate_contract(contract, require_authorized_target=False)
        contract = prepared_contract()
        contract["source_commit"] = "0" * 40
        with self.assertRaises(ContractError):
            validate_contract(contract, require_authorized_target=False)

    def test_promotion_ready_true_is_rejected(self) -> None:
        contract = prepared_contract()
        contract["authority"]["promotion_ready"] = True
        with self.assertRaises(ContractError):
            validate_contract(contract, require_authorized_target=False)

    def test_deployment_claim_without_successful_witness_is_rejected(self) -> None:
        contract = prepared_contract()
        contract["authority"]["deployment_claimed"] = True
        with self.assertRaises(ContractError):
            validate_contract(contract, require_authorized_target=False)

    def test_prepared_receipt_is_content_addressed_and_null_authority(self) -> None:
        first = prepared_receipt(prepared_contract())
        second = prepared_receipt(prepared_contract())
        self.assertEqual(first, second)
        self.assertEqual(first["verdict"], PREPARED_OUTCOME)
        self.assertIsNone(first["endpoint"])
        self.assertIsNone(first["persistent_witness"])


class AuthorizedPreflightTests(unittest.TestCase):
    def test_authorized_target_and_environment_token_pass(self) -> None:
        contract = authorized_contract()
        self.assertEqual(contract["deployment_state"], AUTHORIZED_STATE)
        self.assertIs(
            validate_contract(
                contract,
                require_authorized_target=True,
                token=TOKEN,
                argv=("validate", "--mode", "authorized"),
            ),
            contract,
        )

    def test_missing_or_short_environment_token_is_rejected(self) -> None:
        for token in (None, "short"):
            with self.assertRaises(ContractError):
                validate_contract(
                    authorized_contract(),
                    require_authorized_target=True,
                    token=token,
                )

    def test_token_or_authorization_argument_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_token_from_environment(TOKEN, argv=("--token", TOKEN))
        with self.assertRaises(ContractError):
            validate_token_from_environment(
                TOKEN, argv=("Authorization: Bearer redacted",)
            )

    def test_non_https_wrong_path_and_local_endpoints_are_rejected(self) -> None:
        for endpoint in (
            "http://athena.company.net/mcp",
            "https://athena.company.net/not-mcp",
            "https://localhost/mcp",
            "https://127.0.0.1/mcp",
            "https://runner.local/mcp",
        ):
            with self.assertRaises(ContractError):
                validate_endpoint(endpoint)

    def test_ephemeral_target_is_rejected(self) -> None:
        contract = authorized_contract()
        contract["target"]["ephemeral"] = True
        with self.assertRaises(ContractError):
            validate_contract(
                contract,
                require_authorized_target=True,
                token=TOKEN,
            )

    def test_authorized_preflight_receipt_never_serializes_token(self) -> None:
        receipt = authorized_receipt(authorized_contract(), TOKEN)
        self.assertTrue(secret_free(receipt, TOKEN))
        self.assertNotIn(TOKEN, json.dumps(receipt))
        self.assertFalse(receipt["deployment_claimed"])
        self.assertFalse(receipt["promotion_ready"])


class HTTPProbeTests(unittest.TestCase):
    def test_health_and_negative_authentication_checks_pass(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/healthz":
                return httpx.Response(
                    200,
                    json={
                        "status": "ready",
                        "transport": "streamable-http",
                        "endpoint": "/mcp",
                        "authentication": "bearer",
                        "deployed_commit": SOURCE_COMMIT,
                        "commit_attested": True,
                        "commit_source": "build-locked-file",
                        "promotion_ready": False,
                    },
                )
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

    def test_redirect_is_rejected_without_following(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                307,
                headers={"Location": "https://other.example.net/healthz"},
            )

        with self.assertRaises(RuntimeError):
            asyncio.run(
                observe_http_boundary(
                    ENDPOINT,
                    TOKEN,
                    transport=httpx.MockTransport(handler),
                )
            )

    def test_wrong_build_locked_commit_is_rejected(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/healthz":
                return httpx.Response(
                    200,
                    json={
                        "status": "ready",
                        "transport": "streamable-http",
                        "endpoint": "/mcp",
                        "authentication": "bearer",
                        "deployed_commit": "0" * 40,
                        "commit_attested": True,
                        "commit_source": "build-locked-file",
                        "promotion_ready": False,
                    },
                )
            return httpx.Response(401)

        with self.assertRaises(RuntimeError):
            asyncio.run(
                observe_http_boundary(
                    ENDPOINT,
                    TOKEN,
                    transport=httpx.MockTransport(handler),
                )
            )


class InventoryAndReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        server_path = ROOT / "MCP/athena_mcp_server.py"
        momentum_path = ROOT / "MCP/data/momentum_field.json"
        original_momentum = momentum_path.read_bytes()
        spec = importlib.util.spec_from_file_location(
            "athena_mcp_server_p10_inventory", server_path
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            with mock.patch.dict(
                os.environ, {"ATHENA_ROOT": str(ROOT)}, clear=False
            ):
                spec.loader.exec_module(module)
        finally:
            momentum_path.write_bytes(original_momentum)
        cls.tool_names = sorted(module.mcp._tool_manager._tools)
        cls.resource_uris = sorted(
            str(uri) for uri in module.mcp._resource_manager._resources
        )

    def exact_mcp_observation(self) -> dict:
        cutover = {"promotion_claimed": False}
        return {
            "initialized": True,
            "catalog": {
                "tool_count": len(self.tool_names),
                "tool_inventory_digest": inventory_digest(self.tool_names),
                "tool_names": self.tool_names,
                "resource_count": len(self.resource_uris),
                "resource_inventory_digest": inventory_digest(
                    self.resource_uris
                ),
                "resource_uris": self.resource_uris,
            },
            "status": {
                "graph_digest": EXPECTED_GRAPH_DIGEST,
                "promotion_ready": False,
            },
            "identity": {
                "verdict": "FOUND",
                "answered_by": "athena-federation-v2",
                "fallback_used": False,
                "resource": {"rid": "athena.repo.q-shrink"},
            },
            "route": {
                "verdict": "FOUND",
                "answered_by": "athena-federation-v2",
                "fallback_used": False,
                "hops": [
                    "edge.q-shrink-to-control",
                    "edge.control-to-runtime",
                ],
                "return_plan": [
                    "edge.runtime-to-control",
                    "edge.control-to-q-shrink",
                ],
            },
            "fallback": {
                "verdict": "FOUND_LEGACY",
                "answered_by": "athena-108d-v1",
                "fallback_used": True,
            },
            "cutover_tool": cutover,
            "cutover_resource": deepcopy(cutover),
        }

    def test_actual_p09_tool_and_resource_inventory_is_exact(self) -> None:
        observation = self.exact_mcp_observation()
        checks = validate_mcp_observation(observation)
        self.assertTrue(all(checks.values()))
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

    def test_tampered_inventory_is_rejected(self) -> None:
        observation = self.exact_mcp_observation()
        observation["catalog"]["tool_names"] = self.tool_names[:-1]
        observation["catalog"]["tool_count"] -= 1
        observation["catalog"]["tool_inventory_digest"] = inventory_digest(
            observation["catalog"]["tool_names"]
        )
        with self.assertRaises(RuntimeError):
            validate_mcp_observation(observation)

    def test_successful_local_simulation_is_never_persistent(self) -> None:
        sample = fake_sample(real_network_contact=False)
        receipt = build_witness_receipt(
            authorized_contract(),
            [sample],
            witness_class="local-ephemeral-simulation",
        )
        self.assertEqual(
            receipt["verdict"], "PASS_LOCAL_SIMULATION_NOT_PERSISTENT"
        )
        self.assertFalse(receipt["authority"]["persistent_https_witness"])
        self.assertFalse(receipt["authority"]["deployment_claimed"])

    def test_persistent_verdict_rejects_mock_or_ephemeral_samples(self) -> None:
        samples = [
            fake_sample(real_network_contact=False),
            fake_sample(real_network_contact=False),
            fake_sample(real_network_contact=False),
        ]
        with self.assertRaises(ValueError):
            build_witness_receipt(
                authorized_contract(),
                samples,
                witness_class="persistent-https",
            )

    def test_receipt_serialization_is_deterministic_and_secret_free(self) -> None:
        sample = fake_sample(real_network_contact=False)
        first = build_witness_receipt(
            authorized_contract(),
            [sample],
            witness_class="local-ephemeral-simulation",
        )
        second = build_witness_receipt(
            authorized_contract(),
            [deepcopy(sample)],
            witness_class="local-ephemeral-simulation",
        )
        self.assertEqual(first, second)
        self.assertTrue(secret_free(first, TOKEN))


class RepositorySurfaceTests(unittest.TestCase):
    def test_committed_status_and_receipt_use_only_legal_prepared_outcome(
        self,
    ) -> None:
        status = json.loads(
            (ROOT / ".athena/status.json").read_text(encoding="utf-8")
        )
        receipt = json.loads(
            (
                ROOT
                / ".athena/receipts/p10-authorized-endpoint-readiness.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(status["state"], PREPARED_OUTCOME)
        self.assertEqual(receipt["verdict"], PREPARED_OUTCOME)
        self.assertIsNone(status["deployment"]["external_https_endpoint"])
        self.assertIsNone(status["deployment"]["persistent_live_witness"])
        self.assertFalse(status["authority"]["deployment_claimed"])
        self.assertFalse(status["authority"]["promotion_ready"])

    def test_workflow_uses_pinned_actions_and_protected_secret(self) -> None:
        path = ROOT / ".github/workflows/p10-persistent-witness.yml"
        text = path.read_text(encoding="utf-8")
        self.assertIsInstance(yaml.safe_load(text), dict)
        uses = re.findall(r"^\s*uses:\s*([^@\s]+)@([^\s#]+)", text, re.MULTILINE)
        self.assertGreaterEqual(len(uses), 5)
        for action, reference in uses:
            self.assertRegex(
                reference,
                r"^[0-9a-f]{40}$",
                f"{action} is not pinned to a commit SHA",
            )
        self.assertIn("environment: p10-persistent-host", text)
        self.assertIn(
            "secrets.ATHENA_MCP_BEARER_TOKEN",
            text,
        )

    def test_receipt_only_commits_cannot_trigger_pull_request_workflow(
        self,
    ) -> None:
        text = (
            ROOT / ".github/workflows/p10-persistent-witness.yml"
        ).read_text(encoding="utf-8")
        pull_request_trigger = text.split("workflow_dispatch:", 1)[0]
        self.assertIn("paths:", pull_request_trigger)
        self.assertNotIn(".athena/receipts", pull_request_trigger)
        self.assertNotIn(".athena/status", pull_request_trigger)

    def test_compose_selects_exact_digest_and_non_root_uid(self) -> None:
        compose = yaml.safe_load(
            (ROOT / "deploy/p10/compose.yaml").read_text(encoding="utf-8")
        )
        service = compose["services"]["athena-mcp"]
        self.assertEqual(service["image"], IMAGE_REFERENCE)
        self.assertEqual(service["user"], "10001:10001")
        self.assertEqual(service["restart"], "unless-stopped")
        self.assertTrue(service["read_only"])


if __name__ == "__main__":
    unittest.main()
