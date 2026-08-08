import json
import tempfile
import unittest

from athena_mcp.hub_server import HubServer


class HubServerTests(unittest.TestCase):
    def test_hub_is_composed_entry_surface(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as handle:
            server = HubServer(handle.name)
            try:
                tools = server.handle(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list",
                    }
                )["result"]["tools"]
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
                    "athena_system_upgrade_manifest",
                    "athena_system_upgrade_plan",
                    "athena_system_upgrade_state",
                    "athena_system_upgrade_observe",
                    "athena_system_upgrade_refresh",
                    "athena_system_upgrade_replay",
                    "athena_system_release_certificate",
                    "athena_system_release_replay",
                ):
                    self.assertIn(name, names)
                self.assertIn("athena_promotion_evaluate", names)

                resources = server.handle(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "resources/list",
                    }
                )["result"]["resources"]
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
                    "athena://system/upgrade",
                    "athena://system/upgrade/frontier",
                    "athena://system/release",
                ):
                    self.assertIn(uri, uris)
                self.assertIn("athena://promotion", uris)

                reply = server.handle(
                    {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "athena_kc144_hub_validate",
                            "arguments": {},
                        },
                    }
                )
                payload = json.loads(
                    reply["result"]["content"][0]["text"]
                )
                self.assertEqual(payload["overall_status"], "PASS", payload)
                self.assertEqual(
                    payload["authoritative_registry_pack"]["status"],
                    "PASS",
                )
                overlay = payload["runtime_organ_overlay"]
                self.assertEqual(
                    overlay["ORGAN.EQ1"]["state"], "LIVE_UNIFIED"
                )
                self.assertEqual(
                    overlay["ORGAN.HUG_ABI1"]["state"],
                    "LIVE_UNIFIED_FAIL_CLOSED",
                )
                self.assertEqual(
                    overlay["ORGAN.FIELD1"]["state"],
                    "LIVE_UNIFIED",
                )
                self.assertEqual(
                    overlay["ORGAN.PROMOTION1"]["state"],
                    "LIVE_UNIFIED_FAIL_CLOSED",
                )
                self.assertEqual(
                    overlay["ORGAN.SYSTEM_UPGRADE1"]["state"],
                    "LIVE_UNIFIED_WITNESS_GATED",
                )
                self.assertTrue(
                    all(value["surface_pass"] for value in overlay.values())
                )

                inventory_reply = server.handle(
                    {
                        "jsonrpc": "2.0",
                        "id": 4,
                        "method": "tools/call",
                        "params": {
                            "name": "athena_kc144_hub_inventory",
                            "arguments": {
                                "kind": "RESOURCE",
                                "limit": 5000,
                            },
                        },
                    }
                )
                inventory = json.loads(
                    inventory_reply["result"]["content"][0]["text"]
                )
                discovered = {
                    item["payload"]["uri"]
                    for item in inventory["items"]
                }
                for uri in (
                    "athena://equivalence",
                    "athena://extraction",
                    "athena://retrieval",
                    "athena://hug",
                    "athena://gap",
                    "athena://field",
                    "athena://kc144/registry/status",
                    "athena://system/upgrade",
                    "athena://system/release",
                ):
                    self.assertIn(uri, discovered)

                field = server.handle(
                    {
                        "jsonrpc": "2.0",
                        "id": 5,
                        "method": "tools/call",
                        "params": {
                            "name": "athena_field_compile",
                            "arguments": {
                                "seed_ref": "seed://hub-test",
                                "module_outputs": {},
                                "persist": False,
                            },
                        },
                    }
                )["result"]
                self.assertFalse(field.get("isError"), field)
                self.assertEqual(
                    field["structuredContent"]["version"], "FIELD.1"
                )

                verification = server.handle(
                    {
                        "jsonrpc": "2.0",
                        "id": 6,
                        "method": "tools/call",
                        "params": {
                            "name": "athena_kc144_registry_verify",
                            "arguments": {"deep": True},
                        },
                    }
                )["result"]
                self.assertFalse(
                    verification.get("isError"), verification
                )
                self.assertEqual(
                    verification["structuredContent"]["status"], "PASS"
                )

                frontier = server.handle(
                    {
                        "jsonrpc": "2.0",
                        "id": 7,
                        "method": "tools/call",
                        "params": {
                            "name": "athena_kc144_completion_frontier",
                            "arguments": {},
                        },
                    }
                )["result"]
                self.assertFalse(frontier.get("isError"), frontier)
                self.assertEqual(
                    frontier["structuredContent"]["frontier"][0][
                        "task_id"
                    ],
                    "TASK.000",
                )

                migration = server.handle(
                    {
                        "jsonrpc": "2.0",
                        "id": 8,
                        "method": "tools/call",
                        "params": {
                            "name": "athena_schema_migrate",
                            "arguments": {},
                        },
                    }
                )["result"]["structuredContent"]
                self.assertIn(
                    migration["status"], {"APPLIED", "UP_TO_DATE"}
                )
                plan = server.handle(
                    {
                        "jsonrpc": "2.0",
                        "id": 9,
                        "method": "tools/call",
                        "params": {
                            "name": "athena_system_upgrade_plan",
                            "arguments": {
                                "objective": "hub integration test"
                            },
                        },
                    }
                )["result"]
                self.assertFalse(plan.get("isError"), plan)
                self.assertTrue(
                    plan["structuredContent"]["athena_ready_local"],
                    plan,
                )
                self.assertTrue(
                    plan["structuredContent"]["run_id"].startswith(
                        "UPGRUN."
                    )
                )
            finally:
                server.store.close()


if __name__ == "__main__":
    unittest.main()
