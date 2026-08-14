import json
import tempfile
import unittest

from athena_mcp.composition_integrity import composition_certificate
from athena_mcp.nexus4d import VERSION
from athena_mcp.nexus4d_protocol import NEXUS4D_RESOURCE_URIS, NEXUS4D_TOOL_NAMES
from athena_mcp.server import Server
from athena_mcp.surface_contract import REQUIRED_RESOURCES, REQUIRED_TOOLS


class Nexus4dIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db")
        self.server = Server(self.tmp.name)
        self.seq = 0

    def tearDown(self):
        self.server.store.close()
        self.tmp.close()

    def rpc(self, method, params=None):
        self.seq += 1
        message = {"jsonrpc": "2.0", "id": self.seq, "method": method}
        if params is not None:
            message["params"] = params
        return self.server.handle(message)

    def tool(self, name, arguments):
        response = self.rpc("tools/call", {"name": name, "arguments": arguments})
        result = response["result"]
        self.assertFalse(result.get("isError"), response)
        return result["structuredContent"]

    def test_nexus4d_is_a_resident_required_surface(self):
        tools = {item["name"] for item in self.rpc("tools/list")["result"]["tools"]}
        resources = {item["uri"] for item in self.rpc("resources/list")["result"]["resources"]}
        self.assertTrue(NEXUS4D_TOOL_NAMES <= tools)
        self.assertTrue(NEXUS4D_RESOURCE_URIS <= resources)
        self.assertEqual(REQUIRED_TOOLS["nexus4d"], NEXUS4D_TOOL_NAMES)
        self.assertEqual(REQUIRED_RESOURCES["nexus4d"], NEXUS4D_RESOURCE_URIS)
        resource = json.loads(self.rpc("resources/read", {"uri": "athena://nexus4d"})["result"]["contents"][0]["text"])
        self.assertEqual(resource["version"], VERSION)
        self.assertFalse(resource["authority"]["execution"])
        manifest = json.loads(self.rpc("resources/read", {"uri": "athena://manifest"})["result"]["contents"][0]["text"])
        self.assertEqual(manifest["nexus4d"]["version"], VERSION)
        self.assertIn("NEXUS4D_BIDIRECTIONAL_OBLIGATION_PRESSURE_KERNEL", manifest["extensions"])
        audit = self.tool("athena_surface_audit", {})
        self.assertEqual(audit["status"], "PASS", audit)
        self.assertEqual(audit["groups"]["nexus4d"]["status"], "PASS", audit)
        cert = composition_certificate(self.server, run_probes=True)
        self.assertEqual(cert["status"], "PASS", cert)
        self.assertIn("nexus4d", cert["development_organs"]["required"])
        benchmark = self.tool("athena_benchmark", {})
        self.assertEqual(benchmark["nexus4d_version"], VERSION)
        self.assertEqual(benchmark["nexus4d_machines"], 0)

    def test_mcp_lifecycle_reaches_terminal_only_after_observed_consumption(self):
        spec = {
            "name": "integration lifecycle",
            "initial_state": {"x": 0},
            "goals": [
                {
                    "id": "G",
                    "predicate": {"kind": "state_equals", "path": "x", "value": 1},
                    "evidence_threshold": {"local": 1.0},
                    "consumer": "runtime",
                    "require_outcome": True,
                }
            ],
            "nodes": [
                {
                    "id": "N",
                    "goals": ["G"],
                    "readset": ["x"],
                    "writeset": ["x"],
                    "evidence_threshold": {"local": 1.0},
                    "consumer": "runtime",
                    "require_outcome": True,
                }
            ],
        }
        compiled = self.tool("athena_nexus_compile", {"machine_id": "MCP-NEXUS", "spec": spec})
        self.assertEqual(compiled["status"], "COMPILED")
        packet = compiled["plan"]["batch"][0]["nexus_packet"]
        advanced = self.tool(
            "athena_nexus_advance",
            {
                "machine_id": "MCP-NEXUS",
                "expected_revision": 0,
                "events": [
                    {
                        "type": "CLAIMED",
                        "payload": {
                            "node_id": "N",
                            "claim_id": "CL",
                            "readset_digest": packet["readset_digest"],
                            "writeset": packet["writeset"],
                            "lease_until_revision": 20,
                        },
                    },
                    {
                        "type": "CANDIDATE_PRODUCED",
                        "payload": {
                            "node_id": "N",
                            "claim_id": "CL",
                            "candidate_id": "C",
                            "readset_digest": packet["readset_digest"],
                            "state_delta": {"x": 1},
                        },
                    },
                    {
                        "type": "EVIDENCE_RECORDED",
                        "payload": {"node_id": "N", "candidate_id": "C", "profile": {"local": 1.0}, "refs": ["TEST:MCP"]},
                    },
                    {
                        "type": "VERIFIED",
                        "payload": {"node_id": "N", "candidate_id": "C", "passed": True, "verifier_ref": "VERIFIER:MCP"},
                    },
                    {
                        "type": "COMMITTED",
                        "payload": {"node_id": "N", "candidate_id": "C", "authority_ref": "AUTH:MCP"},
                    },
                ],
            },
        )
        self.assertFalse(advanced["terminal"]["terminal"])
        consumed = self.tool(
            "athena_nexus_advance",
            {
                "machine_id": "MCP-NEXUS",
                "expected_revision": advanced["revision"],
                "events": [{"type": "CONSUMED", "payload": {"node_id": "N", "consumer": "runtime", "receipt_ref": "CONSUMER:MCP"}}],
            },
        )
        self.assertFalse(consumed["terminal"]["terminal"])
        observed = self.tool(
            "athena_nexus_advance",
            {
                "machine_id": "MCP-NEXUS",
                "expected_revision": consumed["revision"],
                "events": [{"type": "OUTCOME_OBSERVED", "payload": {"node_id": "N", "observation_ref": "OBS:MCP"}}],
            },
        )
        self.assertTrue(observed["terminal"]["terminal"])
        terminal = self.tool("athena_nexus_terminal", {"machine_id": "MCP-NEXUS"})
        self.assertEqual(terminal["status"], "TERMINAL")
        replay = self.tool("athena_nexus_replay", {"machine_id": "MCP-NEXUS"})
        self.assertEqual(replay["status"], "REPLAY_MATCH", replay)
        benchmark = self.tool("athena_benchmark", {})
        self.assertEqual(benchmark["nexus4d_terminal_machines"], 1)


if __name__ == "__main__":
    unittest.main()
