from __future__ import annotations

import copy
import json
import unittest

import athena_mcp
from athena_mcp.capability_basis import (
    ARTIFACT,
    CONTROL_CAPABILITY_DESCRIPTORS,
    DESCRIPTOR_ARTIFACT,
    derive_operational_basis,
)


class CapabilityBasisTests(unittest.TestCase):
    def current_control_names(self) -> set[str]:
        # Package initialization composes the current prompt/frontier/rehydration/
        # successor/handoff/bootstrap surface into this existing dispatcher set.
        return set(athena_mcp.PROMPT_RUNTIME_TOOL_NAMES)

    def test_current_registered_control_surface_is_fully_classified(self):
        basis = derive_operational_basis(
            self.current_control_names(),
            runtime_identity="test-head-a",
        )
        self.assertEqual(basis["artifact"], ARTIFACT)
        self.assertEqual(basis["status"], "PASS")
        self.assertEqual(basis["unclassified"], [])
        self.assertEqual(
            basis["registered_negotiated_count"],
            basis["classified_count"],
        )
        self.assertIn("BOOTSTRAP_REFRESH", basis["capability_classes"])
        self.assertIn("PROMPT", basis["capability_classes"])
        self.assertIn("FRONTIER_READ_SELECT", basis["capability_classes"])
        self.assertIn("REHYDRATION_LOOP", basis["capability_classes"])
        self.assertIn("SUCCESSOR", basis["capability_classes"])
        self.assertIn("HANDOFF", basis["capability_classes"])
        self.assertIn("VERIFY_REPLAY_INDEX", basis["capability_classes"])

    def test_basis_digest_is_order_and_runtime_clock_independent(self):
        names = sorted(self.current_control_names())
        a = derive_operational_basis(names, runtime_identity="head-a")
        b = derive_operational_basis(reversed(names), runtime_identity="head-b")
        self.assertEqual(a["basis_digest"], b["basis_digest"])
        self.assertNotEqual(a["runtime_identity"], b["runtime_identity"])

    def test_unrelated_nonnegotiated_tool_does_not_change_basis(self):
        names = self.current_control_names()
        base = derive_operational_basis(names)
        with_unrelated = derive_operational_basis(names | {"athena_bionano_compile"})
        self.assertEqual(base["basis_digest"], with_unrelated["basis_digest"])
        self.assertEqual(base["descriptors"], with_unrelated["descriptors"])

    def test_feature_only_claim_name_is_unclassified_until_same_lineage_descriptor(self):
        names = self.current_control_names() | {"athena_frontier_claim"}
        basis = derive_operational_basis(names, runtime_identity="feature-head")
        self.assertEqual(basis["status"], "HOLD_UNCLASSIFIED_CAPABILITY")
        self.assertEqual(basis["unclassified"], ["athena_frontier_claim"])
        exposed = {row["operation"] for row in basis["descriptors"]}
        self.assertNotIn("athena_frontier_claim", exposed)

    def test_dormant_descriptor_does_not_create_exposure_or_change_digest(self):
        names = self.current_control_names()
        base = derive_operational_basis(names)
        mapping = copy.deepcopy(CONTROL_CAPABILITY_DESCRIPTORS)
        prototype = copy.deepcopy(mapping["athena_rehydration_successor_preview"])
        prototype["operation"] = "athena_rehydration_epoch_rollover"
        prototype["capability_class"] = "EPOCH_ROLLOVER"
        mapping[prototype["operation"]] = prototype
        augmented = derive_operational_basis(names, descriptor_map=mapping)
        self.assertEqual(base["basis_digest"], augmented["basis_digest"])
        self.assertIn("athena_rehydration_epoch_rollover", augmented["dormant_descriptors"])
        self.assertNotIn("EPOCH_ROLLOVER", augmented["capability_classes"])

    def test_descriptor_effects_preserve_read_write_boundary(self):
        basis = derive_operational_basis(self.current_control_names())
        rows = {row["operation"]: row for row in basis["descriptors"]}
        self.assertEqual(rows["athena_agent_bootstrap"]["effect"], "READ_ONLY_SHARED_SYNC")
        self.assertEqual(rows["athena_frontier_select"]["effect"], "READ_ONLY")
        self.assertEqual(rows["athena_prompt_propose"]["effect"], "GIT_WRITE_BOUNDED")
        self.assertEqual(rows["athena_rehydration_advance"]["effect"], "GIT_WRITE_BOUNDED")
        self.assertNotEqual(
            rows["athena_prompt_promote"]["authority_class"],
            rows["athena_prompt_hydrate"]["authority_class"],
        )

    def test_descriptor_shape_and_secret_boundary(self):
        required = {
            "artifact",
            "operation",
            "capability_class",
            "component",
            "effect",
            "authority_class",
            "freshness_dependencies",
            "preconditions",
            "replayability",
            "rollback_or_compensation",
        }
        serialized = json.dumps(CONTROL_CAPABILITY_DESCRIPTORS, sort_keys=True).lower()
        for descriptor in CONTROL_CAPABILITY_DESCRIPTORS.values():
            self.assertEqual(descriptor["artifact"], DESCRIPTOR_ARTIFACT)
            self.assertTrue(required.issubset(descriptor))
            self.assertIsInstance(descriptor["freshness_dependencies"], list)
            self.assertIsInstance(descriptor["preconditions"], list)
        for forbidden in ("token", "authorization_header", "chain_of_thought", "private_reasoning"):
            self.assertNotIn(f'"{forbidden}"', serialized)

    def test_operation_add_remove_changes_content_identity(self):
        names = self.current_control_names()
        full = derive_operational_basis(names)
        removed = derive_operational_basis(names - {"athena_agent_refresh"})
        self.assertNotEqual(full["basis_digest"], removed["basis_digest"])
        self.assertNotIn(
            "athena_agent_refresh",
            {row["operation"] for row in removed["descriptors"]},
        )

    def test_issue_or_feature_prose_cannot_enter_derivation(self):
        names = self.current_control_names()
        basis = derive_operational_basis(names, runtime_identity="canonical-master")
        # The derivation accepts only the registered runtime names and descriptor
        # map; there is no issue/PR assertion input that can manufacture exposure.
        self.assertNotIn("athena_frontier_claim", basis["capability_classes"].get("CLAIM_EXECUTION", []))
        self.assertEqual(basis["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
