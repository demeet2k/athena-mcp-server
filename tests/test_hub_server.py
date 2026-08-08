import json
import tempfile
import unittest

from athena_mcp.hub_server import HubServer


class HubServerTests(unittest.TestCase):
    def test_hub_is_composed_entry_surface(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as handle:
            server = HubServer(handle.name)
            tools = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
            names = {item["name"] for item in tools}
            self.assertIn("athena_kc144_hub_status", names)
            self.assertIn("athena_collective_plan", names)
            self.assertIn("athena_orchestrate", names)
            self.assertIn("athena_claim_register", names)
            self.assertIn("athena_equivalence_snapshot", names)
            self.assertIn("athena_extraction_plan", names)
            self.assertIn("athena_retrieval_compile", names)
            self.assertIn("athena_hug_register", names)
            self.assertIn("athena_gap_compile", names)
            self.assertNotIn("athena_field_compile", names)
            self.assertNotIn("athena_promotion_evaluate", names)

            resources = server.handle({"jsonrpc": "2.0", "id": 2, "method": "resources/list"})["result"]["resources"]
            uris = {item["uri"] for item in resources}
            for uri in (
                "athena://kc144/hub",
                "athena://equivalence",
                "athena://extraction",
                "athena://retrieval",
                "athena://hug",
                "athena://gap",
            ):
                self.assertIn(uri, uris)
            self.assertNotIn("athena://field", uris)
            self.assertNotIn("athena://promotion", uris)

            reply = server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "athena_kc144_hub_validate", "arguments": {}}})
            payload = json.loads(reply["result"]["content"][0]["text"])
            self.assertEqual(payload["overall_status"], "PASS")
            overlay = payload["runtime_organ_overlay"]
            self.assertEqual(overlay["ORGAN.EQ1"]["state"], "LIVE_UNIFIED")
            self.assertEqual(overlay["ORGAN.SX1"]["state"], "LIVE_UNIFIED")
            self.assertEqual(overlay["ORGAN.RAG1"]["state"], "LIVE_UNIFIED")
            self.assertEqual(overlay["ORGAN.HUG_ABI1"]["state"], "LIVE_UNIFIED_FAIL_CLOSED")
            self.assertEqual(overlay["ORGAN.GAP1"]["state"], "LIVE_UNIFIED")
            self.assertFalse(overlay["ORGAN.FIELD1"]["surface_pass"])
            self.assertFalse(overlay["ORGAN.PROMOTION1"]["surface_pass"])

            inventory_reply = server.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "athena_kc144_hub_inventory", "arguments": {"kind": "RESOURCE", "limit": 5000}}})
            inventory = json.loads(inventory_reply["result"]["content"][0]["text"])
            discovered = {item["payload"]["uri"] for item in inventory["items"]}
            for uri in (
                "athena://equivalence",
                "athena://extraction",
                "athena://retrieval",
                "athena://hug",
                "athena://gap",
            ):
                self.assertIn(uri, discovered)
            server.store.close()


if __name__ == "__main__":
    unittest.main()
