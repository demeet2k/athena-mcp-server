import unittest

from athena_mcp.command_hub import KC144CommandHub
from athena_mcp.runtime_truth import (
    INTEGRATION_BASE_SHA,
    ORGAN_CAPABILITY_REQUIREMENTS,
    TRANSPORT_CAPABILITY_REQUIREMENTS,
)


class CommandHubTests(unittest.TestCase):
    def setUp(self):
        all_requirements = (
            list(ORGAN_CAPABILITY_REQUIREMENTS)
            + list(TRANSPORT_CAPABILITY_REQUIREMENTS)
        )
        required_tools = sorted(
            {
                tool
                for requirement in all_requirements
                for tool in requirement["required_tools"]
            }
        )
        required_resources = sorted(
            {
                uri
                for requirement in all_requirements
                for uri in requirement["required_resources"]
            }
        )
        gate_matrix = {
            symbol: {
                "status": "PASS",
                "evidence": {"test": True},
                "boundary": f"measured {symbol}",
            }
            for symbol in "CIEPRVOMSX"
        }
        self.hub = KC144CommandHub(
            tool_names=lambda: required_tools,
            runtime_probe=lambda: {
                "state": "TEST",
                "system_upgrade": {
                    "status": "READY_LOCAL",
                    "athena_ready_local": True,
                    "gate_matrix": gate_matrix,
                    "snapshot_digest": "snapshot:test",
                },
            },
            resource_uris=required_resources,
        )

    def test_inventory_seats_every_dynamic_tool_and_resource(self):
        tool_inventory = self.hub.inventory(kind="TOOL", limit=5000)
        names = {
            item["payload"]["name"]
            for item in tool_inventory["items"]
        }
        self.assertIn("athena_retrieval_compile", names)
        self.assertIn("athena_hug_register", names)
        self.assertIn("athena_gap_compile", names)
        self.assertIn("athena_system_upgrade_plan", names)
        self.assertIn("athena_kc144_hub_validate", names)
        self.assertTrue(
            all(44 <= item["gid"] <= 80 for item in tool_inventory["items"])
        )

        resource_inventory = self.hub.inventory(
            kind="RESOURCE", limit=5000
        )
        uris = {
            item["payload"]["uri"]
            for item in resource_inventory["items"]
        }
        self.assertIn("athena://equivalence", uris)
        self.assertIn("athena://hug", uris)
        self.assertIn("athena://gap", uris)
        self.assertIn("athena://system/upgrade", uris)
        self.assertIn("athena://system/release", uris)

    def test_seat_fibres_and_datasets(self):
        seat = self.hub.seat(39)
        self.assertEqual(seat["gid"], 39)
        self.assertTrue(
            any(
                item["id"] == "ORGAN.TOPOLOGICAL_COMMAND_HUB"
                for item in seat["fibres"]
            )
        )
        datasets = self.hub.datasets()
        self.assertGreaterEqual(datasets["count"], 19)
        self.assertTrue(
            all("locator" in item for item in datasets["items"])
        )

    def test_runtime_overlay_marks_complete_organism_live(self):
        status = self.hub.status()
        overlay = status["runtime_organ_overlay"]["organs"]
        self.assertTrue(status["runtime_organ_overlay"]["all_required_live"])
        self.assertEqual(overlay["ORGAN.EQ1"]["state"], "LIVE_UNIFIED")
        self.assertEqual(
            overlay["ORGAN.HUG_ABI1"]["state"],
            "LIVE_UNIFIED_FAIL_CLOSED",
        )
        self.assertEqual(
            overlay["ORGAN.SYSTEM_UPGRADE1"]["state"],
            "LIVE_UNIFIED_WITNESS_GATED",
        )
        self.assertEqual(
            overlay["ORGAN.PROMOTION1"]["state"],
            "LIVE_UNIFIED_FAIL_CLOSED",
        )
        self.assertTrue(
            all(value["surface_pass"] for value in overlay.values())
        )

    def test_measured_readiness_is_local_not_external_promotion(self):
        readiness = self.hub.readiness()
        self.assertTrue(readiness["athena_ready_local"])
        self.assertEqual(readiness["verdict"], "PASS_LOCAL")
        self.assertEqual(
            readiness["promotion"],
            "EXTERNAL_EXACT_HEAD_ATTESTATION_REQUIRED",
        )
        self.assertEqual(readiness["blockers"], [])
        self.assertEqual(
            readiness["gate_states"],
            {key: "PASS" for key in "CIEPRVOMSX"},
        )

    def test_validation_requires_complete_organs_and_transports(self):
        result = self.hub.validate()
        self.assertEqual(result["overall_status"], "PASS", result)
        self.assertEqual(result["runtime_checks"][2]["observed"], 10)
        self.assertTrue(result["runtime_checks"][3]["pass"])
        self.assertTrue(result["runtime_checks"][4]["pass"])
        self.assertTrue(result["runtime_checks"][5]["pass"])

    def test_manifest_dynamic_digest(self):
        first = self.hub.manifest()
        second = self.hub.manifest()
        self.assertEqual(
            first["runtime_manifest_digest"],
            second["runtime_manifest_digest"],
        )
        self.assertEqual(len(first["seats"]), 144)
        self.assertEqual(
            first["integration_base_sha"],
            INTEGRATION_BASE_SHA,
        )


if __name__ == "__main__":
    unittest.main()
