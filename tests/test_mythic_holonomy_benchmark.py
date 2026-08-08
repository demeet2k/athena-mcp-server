import unittest

from athena_mcp.mythic_holonomy_benchmark import (
    CASES,
    LAYERS,
    SCALARIZATION,
    SOURCE_PACKET_BLOB_SHA,
    SOURCE_PACKET_COMMIT,
    SOURCE_PACKET_PATH,
    run_benchmark,
)


class MythicHolonomyHeldoutBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_benchmark()

    def test_frozen_projection_identity_and_shape(self):
        self.assertEqual(SOURCE_PACKET_BLOB_SHA, "1dabde8f450f237d28cf230ff2bb5d9e8d729c8e")
        self.assertEqual(SOURCE_PACKET_COMMIT, "c1858bcbc6587296c2b8a7e29642bfef695fdb2a")
        self.assertEqual(SOURCE_PACKET_PATH, "registry/mythic_holonomy_heldout_v0.json")
        self.assertEqual(SCALARIZATION, "DISABLED_V0")
        self.assertEqual(len(LAYERS), 10)
        self.assertEqual(len(CASES), 15)

    def test_three_arms_show_incremental_composition_gain(self):
        arms = self.result["arms"]
        a0 = arms["A0_UNSCOPED_REFERENCE"]
        a1 = arms["A1_STRATA_MEMBRANE"]
        a2 = arms["A2_COMPOSED_HOLONOMY_LEDGER"]
        self.assertEqual((a0["passed"], a1["passed"], a2["passed"]), (10, 12, 15))
        self.assertEqual((a0["false_equivalence_claims"], a1["false_equivalence_claims"], a2["false_equivalence_claims"]), (2, 0, 0))
        self.assertEqual((a1["nonzero_holonomy_loops_detected"], a2["nonzero_holonomy_loops_detected"]), (0, 2))
        self.assertEqual((a1["path_order_sensitive_cases"], a2["path_order_sensitive_cases"]), (0, 1))

    def test_a2_retains_lawful_transport_without_minting(self):
        a2 = self.result["arms"]["A2_COMPOSED_HOLONOMY_LEDGER"]
        self.assertEqual(a2["lawful_bridges_retained"], 7)
        self.assertEqual(a2["false_holds_on_lawful_transport"], 0)
        self.assertEqual(a2["standing_amplification_violations"], 0)
        self.assertEqual(a2["authority_minting_violations"], 0)
        self.assertEqual(a2["provenance_complete_cases"], 15)
        self.assertEqual(a2["loss_ledger_complete_cases"], 15)
        by_id = {x["case_id"]: x for x in a2["outcomes"]}
        self.assertEqual(by_id["HOL-H02-03"]["actual_class"], "HOLD_EQUIVALENCE")
        self.assertEqual(by_id["HOL-H03-03"]["actual_class"], "HOLD_EQUIVALENCE")
        self.assertTrue(by_id["HOL-H03-04"]["path_order_sensitive"])
        self.assertEqual(by_id["HOL-H03-04"]["canonical_status"], "COMPOSED_PATH_ALLOWED")
        self.assertEqual(by_id["HOL-H03-04"]["permuted_status"], "HOLD_NO_FROZEN_BRIDGE")

    def test_nonzero_loops_and_zero_controls_remain_separated(self):
        vectors = self.result["arms"]["A2_COMPOSED_HOLONOMY_LEDGER"]["holonomy_vectors"]
        for case_id in ("HOL-H01-04", "HOL-H02-04"):
            self.assertEqual(vectors[case_id]["role_delta"], 1)
            self.assertEqual(vectors[case_id]["decoder_delta"], 1)
            self.assertGreater(vectors[case_id]["ontology_delta"], 0)
            self.assertEqual(vectors[case_id]["standing_delta"], 0)
            self.assertEqual(vectors[case_id]["provenance_delta"], 0)
            self.assertEqual(vectors[case_id]["invariant_violations"], 0)
            self.assertEqual(vectors[case_id]["unaccounted_loss"], 0)
        self.assertEqual(vectors["HOL-H01-04"]["authority_delta"], 0)
        self.assertEqual(vectors["HOL-H02-04"]["authority_delta"], 1)
        for case_id in ("HOL-H01-05", "HOL-H02-05", "HOL-H03-05"):
            self.assertTrue(all(value == 0 for value in vectors[case_id].values()))

    def test_benchmark_pass_does_not_promote_mck_v2(self):
        self.assertTrue(self.result["benchmark_acceptance_passed"])
        self.assertEqual(self.result["practitioner_review"], "HOLD_EXTERNAL_REVIEW")
        self.assertFalse(self.result["mck_v2_promotion"])
        for law in (
            "SOURCE_DERIVED_FEATURE_ENCODING != OBJECTIVE_SEMANTIC_GROUND_TRUTH",
            "SELF_GENERATED_SCORE != INDEPENDENT_WITNESS",
            "BENCHMARK_GAIN != MCK_V2_PROMOTION",
        ):
            self.assertIn(law, self.result["laws"])


if __name__ == "__main__":
    unittest.main()
