import unittest

from athena_mcp.drive_recovery_protocol import RECOVERY_RESOURCE, RECOVERY_TOOL_NAMES
from athena_mcp.drive_recovery_registry_v2 import (
    VERSION,
    get_organ,
    holoaddress_for,
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

    def test_wave2_holoaddress_preserves_revision_without_fabricating_digest(self):
        out = holoaddress_for("recovery.holoaddress_dereference")
        h = out["holoaddress"]
        self.assertEqual(h["VersionPin"], {"status": "PINNED", "revision_id": "41"})
        self.assertEqual(h["LookupKey"]["drive_file_id"], "11RM1vUiZbnBVSzlYl6BJPBRyx7-WA-DY4A_YOXugx2I")
        self.assertEqual(h["DigestLocator"]["status"], "UNCOMPUTED")
        self.assertIsNone(h["DigestLocator"]["digest"])
        self.assertIn("HoloAddress", h["CompressionSeed"]["semantic_signature"])
        self.assertTrue(any("fresh Athena and MCP Git heads" in step for step in h["ReentryInstructions"]))
        self.assertIn("not source bytes", out["law"])

    def test_unpinned_source_stays_explicitly_unpinned(self):
        out = holoaddress_for("kc144.command_hub")["holoaddress"]
        self.assertEqual(out["VersionPin"]["status"], "UNPINNED")
        self.assertIsNone(out["VersionPin"]["revision_id"])
        self.assertEqual(out["DigestLocator"]["status"], "UNCOMPUTED")

    def test_temporal_formalism_is_scoped_residual_not_false_novelty(self):
        row = get_organ("formal.temporal_manifestation_return")["organ"]
        self.assertEqual(row["source"]["revision_id"], "22")
        self.assertEqual(row["status"], "RESIDUAL_HIGH_VALUE_SCOPED_ISSUE")
        self.assertTrue(any("SID != OID != MID != VID" in ref for ref in row["current_runtime_refs"]))
        self.assertTrue(any("timebundle.py" in ref for ref in row["current_runtime_refs"]))
        self.assertIn("bitemporal recorded_time versus valid_time", row["residuals"])
        self.assertIn("#62", " ".join(row["current_runtime_refs"]))

    def test_filter_and_semantic_search_crosses_both_waves(self):
        q = list_organs(query="Blackwell")
        self.assertEqual([row["organ_id"] for row in q["organs"]], ["cross_zoom.belief_control"])
        q2 = list_organs(query="request_collapse")
        self.assertEqual([row["organ_id"] for row in q2["organs"]], ["continuity.request_collapse"])
        q3 = list_organs(query="ManifestationOrigin")
        self.assertEqual([row["organ_id"] for row in q3["organs"]], ["formal.temporal_manifestation_return"])

    def test_frontier_prioritizes_unresolved_residuals_not_implemented_holoaddress(self):
        out = residual_frontier(limit=4)
        ids = [row["organ_id"] for row in out["frontier"]]
        self.assertEqual(ids[0], "formal.temporal_manifestation_return")
        self.assertIn("navlearn.future_state_cartography", ids)
        self.assertIn("output.atomization_fitness", ids)
        self.assertNotIn("recovery.holoaddress_dereference", ids)
        self.assertNotIn("rh16.process_memory_recovery", ids)

    def test_resource_and_tools_are_read_only_recovery_surface(self):
        self.assertEqual(
            RECOVERY_TOOL_NAMES,
            {"athena_recovery_organs", "athena_recovery_organ", "athena_recovery_holoaddress", "athena_recovery_frontier"},
        )
        surface = DriveRecoverySurface()
        handled, out = surface.call_tool("athena_recovery_holoaddress", {"organ_id": "recovery.holoaddress_dereference"})
        self.assertTrue(handled)
        self.assertEqual(out["version"], VERSION)
        resource = surface.read_resource(RECOVERY_RESOURCE["uri"])
        self.assertEqual(resource["version"], "DRIVE.ORGAN-RECOVERY.2")
        self.assertIn("read-only", resource["boundary"])
        self.assertEqual(resource["formal_residual_issue"], "demeet2k/athena-mcp-server#62")

    def test_source_heads_are_provenance_coordinates_not_freshness_claims(self):
        surface = DriveRecoverySurface()
        state = surface.read_resource(RECOVERY_RESOURCE["uri"])
        self.assertEqual(state["source_heads"]["wave2_athena"], "b67492c589e7cb9f5d31611b23343ad02896baa2")
        self.assertEqual(state["source_heads"]["wave2_mcp"], "649ad6c6976da101ba8602c70a239ef5b5dbf388")


if __name__ == "__main__":
    unittest.main()
