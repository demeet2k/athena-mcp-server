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
            for name in (
                "athena_kc144_hub_status",
                "athena_collective_plan",
                "athena_orchestrate",
                "athena_claim_register",
                "athena_equivalence_snapshot",
                "athena_extraction_plan",
                "athena_retrieval_compile",
                "athena_hug_register",
                "athena_gap_compile",
                "athena_field_compile",
                "athena_kc144_registry_status",
                "athena_kc144_registry_catalog",
                "athena_kc144_registry_query",
                "athena_kc144_registry_cross_search",
                "athena_kc144_registry_source_bundle",
                "athena_kc144_registry_cell_bundle",
                "athena_kc144_completion_frontier",
                "athena_kc144_registry_verify",
            ):
                self.assertIn(name, names)
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
                "athena://field",
                "athena://kc144/registry/status",
                "athena://kc144/registry/catalog",
                "athena://kc144/registry/manifest",
                "athena://kc144/registry/verification",
                "athena://kc144/completion/frontier",
            ):
                self.assertIn(uri, uris)
            self.assertNotIn("athena://promotion", uris)

            reply = server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "athena_kc144_hub_validate", "arguments": {}}})
            payload = json.loads(reply["result"]["content"][0]["text"])
            self.assertEqual(payload["overall_status"], "PASS")
            self.assertEqual(payload["authoritative_registry_pack"]["status"], "PASS")
            overlay = payload["runtime_organ_overlay"]
            self.assertEqual(overlay["ORGAN.EQ1"]["state"], "LIVE_UNIFIED")
            self.assertEqual(overlay["ORGAN.SX1"]["state"], "LIVE_UNIFIED")
            self.assertEqual(overlay["ORGAN.RAG1"]["state"], "LIVE_UNIFIED")
            self.assertEqual(overlay["ORGAN.HUG_ABI1"]["state"], "LIVE_UNIFIED_FAIL_CLOSED")
            self.assertEqual(overlay["ORGAN.GAP1"]["state"], "LIVE_UNIFIED")
            self.assertEqual(overlay["ORGAN.FIELD1"]["state"], "LIVE_UNIFIED")
            self.assertTrue(overlay["ORGAN.FIELD1"]["surface_pass"])
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
                "athena://field",
                "athena://kc144/registry/status",
            ):
                self.assertIn(uri, discovered)

            field = server.handle({
                "jsonrpc": "2.0", "id": 5, "method": "tools/call",
                "params": {"name": "athena_field_compile", "arguments": {"seed_ref": "seed://hub-test", "module_outputs": {}, "persist": False}},
            })["result"]
            self.assertFalse(field.get("isError"), field)
            self.assertEqual(field["structuredContent"]["version"], "FIELD.1")

            verification = server.handle({
                "jsonrpc": "2.0", "id": 6, "method": "tools/call",
                "params": {"name": "athena_kc144_registry_verify", "arguments": {"deep": True}},
            })["result"]
            self.assertFalse(verification.get("isError"), verification)
            self.assertEqual(verification["structuredContent"]["status"], "PASS")

            query = server.handle({
                "jsonrpc": "2.0", "id": 7, "method": "tools/call",
                "params": {"name": "athena_kc144_registry_query", "arguments": {"registry": "math", "query": "prime", "limit": 3}},
            })["result"]
            self.assertFalse(query.get("isError"), query)
            self.assertLessEqual(query["structuredContent"]["returned"], 3)

            cross = server.handle({
                "jsonrpc": "2.0", "id": 8, "method": "tools/call",
                "params": {"name": "athena_kc144_registry_cross_search", "arguments": {"query": "prime", "registries": ["math", "graphs"], "limit": 4}},
            })["result"]
            self.assertFalse(cross.get("isError"), cross)
            self.assertLessEqual(cross["structuredContent"]["returned"], 4)

            frontier = server.handle({
                "jsonrpc": "2.0", "id": 9, "method": "tools/call",
                "params": {"name": "athena_kc144_completion_frontier", "arguments": {}},
            })["result"]
            self.assertFalse(frontier.get("isError"), frontier)
            self.assertEqual(frontier["structuredContent"]["frontier"][0]["task_id"], "TASK.000")
            server.store.close()


if __name__ == "__main__":
    unittest.main()
