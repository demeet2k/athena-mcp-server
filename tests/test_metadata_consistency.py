import tempfile
import tomllib
import unittest
from pathlib import Path

import athena_mcp
from athena_mcp.protocol import SERVER_INFO
from athena_mcp.server import Server


class MetadataConsistencyTests(unittest.TestCase):
    def test_package_server_and_entrypoint_versions_match_current_release(self):
        root = Path(__file__).resolve().parents[1]
        project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
        self.assertEqual(project["version"], "3.1.0")
        self.assertEqual(athena_mcp.__version__, "3.1.0")
        self.assertEqual(project["version"], athena_mcp.__version__)
        self.assertEqual(project["version"], SERVER_INFO["version"])
        self.assertEqual(project["name"], SERVER_INFO["name"])
        self.assertEqual(
            project["scripts"]["athena-mcp"],
            "athena_mcp.deployment_hub:main",
        )
        self.assertEqual(
            project["scripts"]["athena-mcp-http"],
            "athena_mcp.http_host:main",
        )
        description = project["description"].lower()
        for phrase in (
            "adaptive probabilistic",
            "causal sensitivity",
            "finite belief-state",
            "digest-pinned oci",
            "secure json-rpc http",
        ):
            self.assertIn(phrase, description)

    def test_v5_v11_and_claim_namespaces_are_exposed_without_collision(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            srv = Server(f.name)
            init = srv.handle(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2025-11-25"},
                }
            )["result"]
            self.assertEqual(init["serverInfo"]["version"], "3.1.0")
            self.assertEqual(init["serverInfo"], SERVER_INFO)
            tools = srv.handle(
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
            )["result"]["tools"]
            names = [item["name"] for item in tools]
            self.assertEqual(len(names), len(set(names)))
            for name in (
                "athena_bayes_predict",
                "athena_experiment_design",
                "athena_ood_score",
                "athena_causal_identify",
                "athena_dual_control_plan",
                "athena_belief_register",
                "athena_gaussian_belief_register",
                "athena_gp_register",
                "athena_gp_hyperfit",
                "athena_latent_project_admg",
                "athena_bapomdp_solve",
                "athena_discovery_claim_register",
                "athena_claim_register",
            ):
                self.assertIn(name, names)
            by_name = {item["name"]: item for item in tools}
            self.assertEqual(
                by_name["athena_claim_register"]["inputSchema"]["required"],
                ["claim_id", "source_ref"],
            )
            self.assertNotEqual(
                by_name["athena_claim_register"]["inputSchema"],
                by_name["athena_discovery_claim_register"]["inputSchema"],
            )
            uris = {
                item["uri"]
                for item in srv.handle(
                    {"jsonrpc": "2.0", "id": 3, "method": "resources/list"}
                )["result"]["resources"]
            }
            for uri in (
                "athena://collective/v4",
                "athena://collective/v5",
                "athena://collective/v6",
                "athena://collective/v7",
                "athena://collective/v8",
                "athena://collective/v9",
                "athena://collective/v10",
                "athena://collective/v11",
                "athena://authority",
            ):
                self.assertIn(uri, uris)
            srv.store.close()


if __name__ == "__main__":
    unittest.main()
