import unittest

from athena_mcp.command_hub import KC144CommandHub
from athena_mcp.runtime_truth import ORGAN_CAPABILITY_REQUIREMENTS


LIVE_ORGANS = {
    "ORGAN.EQ1",
    "ORGAN.SX1",
    "ORGAN.RAG1",
    "ORGAN.HUG_ABI1",
    "ORGAN.GAP1",
}


class CommandHubTests(unittest.TestCase):
    def setUp(self):
        live_development_tools = [
            tool
            for requirement in ORGAN_CAPABILITY_REQUIREMENTS
            if requirement["id"] in LIVE_ORGANS
            for tool in requirement["required_tools"]
        ]
        live_development_resources = [
            uri
            for requirement in ORGAN_CAPABILITY_REQUIREMENTS
            if requirement["id"] in LIVE_ORGANS
            for uri in requirement["required_resources"]
        ]
        hub_tools = [
            f"athena_kc144_hub_{name}"
            for name in (
                "status",
                "manifest",
                "seat",
                "inventory",
                "graph",
                "route",
                "datasets",
                "communication",
                "readiness",
                "validate",
            )
        ]
        self.hub = KC144CommandHub(
            tool_names=lambda: ["alpha", "beta", *live_development_tools, *hub_tools],
            runtime_probe=lambda: {"state": "TEST"},
            resource_uris=[*live_development_resources, "athena://kc144/hub"],
        )

    def test_inventory_seats_every_dynamic_tool_and_resource(self):
        tool_inventory = self.hub.inventory(kind="TOOL", limit=5000)
        names = {item["payload"]["name"] for item in tool_inventory["items"]}
        self.assertIn("alpha", names)
        self.assertIn("athena_retrieval_compile", names)
        self.assertIn("athena_hug_register", names)
        self.assertIn("athena_gap_compile", names)
        self.assertIn("athena_kc144_hub_validate", names)
        self.assertTrue(all(44 <= item["gid"] <= 80 for item in tool_inventory["items"]))

        resource_inventory = self.hub.inventory(kind="RESOURCE", limit=5000)
        uris = {item["payload"]["uri"] for item in resource_inventory["items"]}
        self.assertIn("athena://equivalence", uris)
        self.assertIn("athena://hug", uris)
        self.assertIn("athena://gap", uris)

    def test_seat_fibres_and_datasets(self):
        seat = self.hub.seat(39)
        self.assertEqual(seat["gid"], 39)
        self.assertTrue(any(item["id"] == "ORGAN.TOPOLOGICAL_COMMAND_HUB" for item in seat["fibres"]))
        datasets = self.hub.datasets()
        self.assertGreaterEqual(datasets["count"], 19)
        self.assertTrue(all("locator" in item for item in datasets["items"]))

    def test_runtime_overlay_marks_live_prefix_and_open_frontier_exactly(self):
        status = self.hub.status()
        overlay = status["runtime_organ_overlay"]["organs"]
        self.assertEqual(overlay["ORGAN.EQ1"]["state"], "LIVE_UNIFIED")
        self.assertEqual(overlay["ORGAN.SX1"]["state"], "LIVE_UNIFIED")
        self.assertEqual(overlay["ORGAN.RAG1"]["state"], "LIVE_UNIFIED")
        self.assertEqual(overlay["ORGAN.HUG_ABI1"]["state"], "LIVE_UNIFIED_FAIL_CLOSED")
        self.assertEqual(overlay["ORGAN.GAP1"]["state"], "LIVE_UNIFIED")
        self.assertTrue(all(overlay[organ]["surface_pass"] for organ in LIVE_ORGANS))
        for organ in ("ORGAN.FIELD1", "ORGAN.SURFACE1", "ORGAN.COMPOSITION1", "ORGAN.PROMOTION1"):
            self.assertFalse(overlay[organ]["surface_pass"])
            self.assertGreater(len(overlay[organ]["missing_tools"]), 0)
            self.assertGreater(len(overlay[organ]["missing_resources"]), 0)

    def test_readiness_never_self_promotes(self):
        readiness = self.hub.readiness()
        self.assertFalse(readiness["athena_ready"])
        self.assertEqual(readiness["promotion"], "HOLD")
        self.assertTrue(LIVE_ORGANS.issubset(set(readiness["progress_delta"]["newly_live_since_structural_snapshot"])))
        self.assertIn("ORGAN.FIELD1", readiness["progress_delta"]["not_live"])
        self.assertGreater(len(readiness["blockers"]), 0)

    def test_validation_requires_hub_surface_and_live_development_prefix(self):
        result = self.hub.validate()
        self.assertEqual(result["overall_status"], "PASS")
        self.assertEqual(result["runtime_checks"][2]["observed"], 10)
        self.assertTrue(result["runtime_checks"][3]["pass"])
        self.assertTrue(result["runtime_checks"][4]["pass"])

    def test_manifest_dynamic_digest(self):
        first = self.hub.manifest()
        second = self.hub.manifest()
        self.assertEqual(first["runtime_manifest_digest"], second["runtime_manifest_digest"])
        self.assertEqual(len(first["seats"]), 144)
        self.assertEqual(first["active_parent_runtime_sha"], "10f1dc39ffc6066ea00f880ef522050394fd5e3a")


if __name__ == "__main__":
    unittest.main()
