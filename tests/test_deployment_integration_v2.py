import tempfile
import unittest

from athena_mcp.protocol import SERVER_INFO
from athena_mcp.server import Server


class DeploymentCurrentRuntimeIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.temp.name)
        foundation = self.server.aor_development.integrity.state_foundation
        receipt = foundation.schema.migrate(
            "test-deployment-v2",
            foundation.CRITICAL_REQUIRED_TABLES,
            foundation.CRITICAL_REQUIRED_COLUMNS,
        )
        self.assertIn(receipt["status"], {"APPLIED", "UP_TO_DATE"})

    def tearDown(self):
        self.server.store.close()
        self.temp.close()

    def test_tools_resources_prompt_initialize_and_manifest_are_composed(self):
        init = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2025-11-25"},
            }
        )["result"]
        self.assertEqual(init["serverInfo"], SERVER_INFO)

        tools = {
            item["name"]
            for item in self.server.handle(
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
            )["result"]["tools"]
        }
        required_tools = {
            "athena_deployment_manifest",
            "athena_deployment_validate",
            "athena_deployment_activation_plan",
            "athena_deployment_assess_canary",
            "athena_deployment_verify_receipt",
        }
        self.assertTrue(required_tools <= tools)

        call = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "athena_deployment_manifest", "arguments": {}},
            }
        )["result"]
        self.assertFalse(call["isError"], call)
        self.assertEqual(call["structuredContent"]["version"], "ATHENA.DEPLOYMENT.2")

        resources = {
            item["uri"]
            for item in self.server.handle(
                {"jsonrpc": "2.0", "id": 4, "method": "resources/list"}
            )["result"]["resources"]
        }
        self.assertTrue(
            {
                "athena://deployment",
                "athena://deployment/security",
                "athena://deployment/rollout",
                "athena://deployment/evidence",
            }
            <= resources
        )
        resource = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "resources/read",
                "params": {"uri": "athena://deployment/evidence"},
            }
        )["result"]["contents"][0]["text"]
        self.assertIn("RECEIPT_BINDING_PASS", resource)

        prompt = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "prompts/get",
                "params": {
                    "name": "athena_deployment_activation",
                    "arguments": {"objective": "activate exact current-master image"},
                },
            }
        )["result"]["messages"][0]["content"]["text"]
        self.assertIn("PLAN_ONLY != EXECUTION", prompt)
        self.assertIn(">=30 samples", prompt)

        manifest = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "resources/read",
                "params": {"uri": "athena://manifest"},
            }
        )["result"]["contents"][0]["text"]
        self.assertIn("DEPLOYMENT2_SOURCE_BOUND_CAS_ACTIVATION", manifest)

        benchmark = self.server.call_tool("athena_benchmark", {})
        self.assertEqual(benchmark["deployment_version"], "ATHENA.DEPLOYMENT.2")


if __name__ == "__main__":
    unittest.main()
