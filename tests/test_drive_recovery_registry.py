import unittest

from athena_mcp.drive_recovery_protocol import RECOVERY_RESOURCE, RECOVERY_TOOL_NAMES
from athena_mcp.drive_recovery_registry import (
    SOURCE_ATHENA_HEAD,
    SOURCE_MCP_HEAD,
    get_organ,
    list_organs,
    residual_frontier,
)
from athena_mcp.drive_recovery_surface import DriveRecoverySurface


class DriveRecoveryRegistryTests(unittest.TestCase):
    def test_qhug_is_partial_not_missing(self):
        row = get_organ("qhug.ultimate")["organ"]
        self.assertEqual(row["status"], "PARTIAL_CURRENT")
        self.assertTrue(any("qhug_pareto_kernel.py" in ref for ref in row["current_runtime_refs"]))
        self.assertEqual(row["source"]["revision_id"], "25")

    def test_cross_zoom_knows_current_pomdp_overlap(self):
        row = get_organ("cross_zoom.belief_control")["organ"]
        self.assertEqual(row["status"], "PARTIAL_CURRENT")
        self.assertTrue(any("pomdp_solve" in ref for ref in row["current_runtime_refs"]))
        self.assertIn("Blackwell dominance certificate", row["residuals"])

    def test_filter_and_semantic_search(self):
        out = list_organs(status="RESIDUAL_HIGH_VALUE")
        ids = {row["organ_id"] for row in out["organs"]}
        self.assertIn("navlearn.future_state_cartography", ids)
        self.assertIn("set_relation.theory_kernel", ids)
        q = list_organs(query="Blackwell")
        self.assertEqual([row["organ_id"] for row in q["organs"]], ["cross_zoom.belief_control"])

    def test_frontier_prioritizes_residual_work_without_theory_by_default(self):
        out = residual_frontier(limit=3)
        self.assertEqual(out["frontier"][0]["organ_id"], "navlearn.future_state_cartography")
        self.assertEqual(out["frontier"][1]["organ_id"], "output.atomization_fitness")
        self.assertNotIn("rh16.process_memory_recovery", {row["organ_id"] for row in out["frontier"]})

    def test_resource_and_tools_are_read_only_index_surface(self):
        self.assertEqual(
            RECOVERY_TOOL_NAMES,
            {"athena_recovery_organs", "athena_recovery_organ", "athena_recovery_frontier"},
        )
        surface = DriveRecoverySurface()
        handled, out = surface.call_tool("athena_recovery_frontier", {"limit": 2})
        self.assertTrue(handled)
        self.assertEqual(out["count"], 2)
        resource = surface.read_resource(RECOVERY_RESOURCE["uri"])
        self.assertEqual(resource["version"], "DRIVE.ORGAN-RECOVERY.1")
        self.assertIn("read-only", resource["boundary"])

    def test_source_heads_are_explicit_provenance_not_freshness_claim(self):
        self.assertEqual(SOURCE_ATHENA_HEAD, "24f260134d978d5314ee729e8f1dd59df0226a59")
        self.assertEqual(SOURCE_MCP_HEAD, "1c526bb16575192040d634c1dad244cc9cb35132")


if __name__ == "__main__":
    unittest.main()
