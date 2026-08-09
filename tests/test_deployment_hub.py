import json
import tempfile
import unittest

from athena_mcp import runtime_truth
from athena_mcp.command_hub import KC144CommandHub
from athena_mcp.deployment_hub import DeploymentHubServer
from athena_mcp.protocol import PROMPTS, TOOLS


class DeploymentHubTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = DeploymentHubServer(self.temp.name)
        foundation = self.server.aor_development.integrity.state_foundation
        receipt = foundation.schema.migrate(
            "test-deployment-hub",
            foundation.CRITICAL_REQUIRED_TABLES,
            foundation.CRITICAL_REQUIRED_COLUMNS,
        )
        self.assertIn(receipt["status"], {"APPLIED", "UP_TO_DATE"})

    def tearDown(self):
        self.server.store.close()
        self.temp.close()

    def test_initialize_tools_resources_and_runtime_truth(self):
        init = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2025-11-25"},
            }
        )["result"]
        self.assertEqual(init["serverInfo"]["version"], "3.1.0")
        self.assertEqual(
            init["serverInfo"]["httpAdapter"],
            "ATHENA.JSONRPC.HTTP.ADAPTER.1",
        )
        names = {
            item["name"]
            for item in self.server.handle(
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
            )["result"]["tools"]
        }
        for name in (
            "athena_deployment_manifest",
            "athena_deployment_validate",
            "athena_deployment_activation_plan",
            "athena_deployment_assess_canary",
        ):
            self.assertIn(name, names)
        uris = {
            item["uri"]
            for item in self.server.handle(
                {"jsonrpc": "2.0", "id": 3, "method": "resources/list"}
            )["result"]["resources"]
        }
        self.assertIn("athena://deployment", uris)
        tool_result = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 31,
                "method": "tools/call",
                "params": {
                    "name": "athena_deployment_manifest",
                    "arguments": {},
                },
            }
        )["result"]
        self.assertFalse(tool_result["isError"], tool_result)
        self.assertEqual(
            tool_result["structuredContent"]["version"],
            "ATHENA.DEPLOYMENT.1",
        )
        readiness = self.server.call_tool("athena_kc144_hub_readiness", {})
        self.assertIn(
            "ORGAN.DEPLOYMENT1", readiness["progress_delta"]["live_organs"]
        )

    def test_deployment_composition_is_instance_scoped_and_fail_closed(self):
        self.assertNotIn(
            "athena_deployment_manifest", {item["name"] for item in TOOLS}
        )
        self.assertNotIn(
            "athena_deployment_activation", {item["name"] for item in PROMPTS}
        )

        base_requirements = [
            item
            for item in runtime_truth.ORGAN_CAPABILITY_REQUIREMENTS
            if item["id"] != "ORGAN.DEPLOYMENT1"
        ] + list(runtime_truth.TRANSPORT_CAPABILITY_REQUIREMENTS)
        base_tools = sorted(
            {
                name
                for requirement in base_requirements
                for name in requirement["required_tools"]
            }
        )
        base_resources = sorted(
            {
                uri
                for requirement in base_requirements
                for uri in requirement.get("required_resources", ())
            }
        )
        base_hub = KC144CommandHub(
            tool_names=lambda: base_tools,
            runtime_probe=lambda: {"state": "TEST"},
            resource_uris=base_resources,
        )
        base_overlay = base_hub.status()["runtime_organ_overlay"]
        self.assertTrue(base_overlay["all_required_live"], base_overlay)
        self.assertNotIn("ORGAN.DEPLOYMENT1", base_overlay["organs"])

        partial = runtime_truth.overlay_summary(
            ["athena_deployment_manifest"], []
        )
        self.assertIn("ORGAN.DEPLOYMENT1", partial["not_live"])
        deployment = partial["organs"]["ORGAN.DEPLOYMENT1"]
        self.assertEqual(
            deployment["state"], "DEPLOYMENT_CONTRACT_NOT_SURFACED"
        )
        self.assertIn("athena://deployment", deployment["missing_resources"])

    def test_manifest_and_prompt_are_composed(self):
        manifest = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "resources/read",
                "params": {"uri": "athena://manifest"},
            }
        )["result"]["contents"][0]["text"]
        value = json.loads(manifest)
        self.assertIn("DEPLOYMENT1_DIGEST_PINNED_ACTIVATION", value["layers"])
        self.assertEqual(value["deployment"]["version"], "ATHENA.DEPLOYMENT.1")
        prompt = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "prompts/get",
                "params": {
                    "name": "athena_deployment_activation",
                    "arguments": {"objective": "activate exact image"},
                },
            }
        )["result"]["messages"][0]["content"]["text"]
        self.assertIn("PLAN_ONLY != infrastructure mutation", prompt)
        self.assertIn("exact OCI digest", prompt)


if __name__ == "__main__":
    unittest.main()
