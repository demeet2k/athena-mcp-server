import json
import tempfile
import unittest

from athena_mcp.deployment_hub import DeploymentHubServer


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
        readiness = self.server.call_tool("athena_kc144_hub_readiness", {})
        self.assertIn("ORGAN.DEPLOYMENT1", readiness["progress_delta"]["live_organs"])

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
