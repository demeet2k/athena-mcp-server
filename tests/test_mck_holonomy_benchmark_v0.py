from __future__ import annotations

import copy
import unittest

from athena_mcp.mck_holonomy_benchmark_v0 import (
    ARMS,
    distance_vector,
    evaluate_case,
    run_benchmark,
)


def _packet():
    return {
        "artifact": "TEST.HELDOUT",
        "version": "MCK.HOLONOMY.BENCH.V0",
        "families": [
            {
                "family_id": "F",
                "layers": [
                    {"layer_id": "F.S0", "semantic_role": "source", "decoder_role": "d0", "ontology_tags": ["a", "shared"], "authority_scope": "A", "standing": "SECONDARY_SCHOLARSHIP", "provenance": ["SRC"], "declared_loss": []},
                    {"layer_id": "F.S1", "semantic_role": "translation", "decoder_role": "d1", "ontology_tags": ["b", "shared"], "authority_scope": "A", "standing": "SECONDARY_SCHOLARSHIP", "provenance": ["SRC"], "declared_loss": ["translation changes decoder"]},
                    {"layer_id": "F.S2", "semantic_role": "reception", "decoder_role": "d2", "ontology_tags": ["c", "shared"], "authority_scope": "B", "standing": "SECONDARY_SCHOLARSHIP", "provenance": ["SRC"], "declared_loss": ["reception changes context"]},
                ],
            }
        ],
        "cases": [
            {"case_id": "T", "family_id": "F", "path": ["F.S0", "F.S1"], "operation": "SEMANTIC_TRANSPORT", "expected_class": "ALLOW_WITH_LOSS", "source_refs": ["SRC"], "bridge_invariants": ["source remains traceable"], "declared_loss": ["translation"]},
            {"case_id": "E", "family_id": "F", "path": ["F.S2", "F.S0"], "operation": "SEMANTIC_EQUIVALENCE", "expected_class": "HOLD_EQUIVALENCE", "source_refs": ["SRC"]},
            {"case_id": "H", "family_id": "F", "path": ["F.S0", "F.S1", "F.S2", "F.S0"], "operation": "HOLONOMY_LOOP", "expected_class": "NONZERO_HOLONOMY_EXPECTED", "source_refs": ["SRC"], "declared_loss": ["round trip"]},
            {"case_id": "O", "family_id": "F", "path": ["F.S0", "F.S1", "F.S2"], "operation": "PATH_ORDER_COMPARE", "expected_class": "NONCOMMUTATIVE_EXPECTED", "source_refs": ["SRC"]},
            {"case_id": "C", "family_id": "F", "path": ["F.S0", "F.S0"], "operation": "SAME_LAYER_CONTROL", "expected_class": "ZERO_HOLONOMY_CONTROL", "source_refs": ["SRC"]},
        ],
        "distance_semantics": {
            "scalarization": "DISABLED_V0",
            "standing_ranks": {"UNKNOWN": 0, "SECONDARY_SCHOLARSHIP": 2},
        },
    }


class MckHolonomyBenchmarkV0Tests(unittest.TestCase):
    def test_distance_vector_is_vector_not_scalar(self):
        packet = _packet()
        a, b = packet["families"][0]["layers"][:2]
        vector = distance_vector(a, b)
        self.assertEqual(vector["role_delta"], 1)
        self.assertEqual(vector["decoder_delta"], 1)
        self.assertAlmostEqual(vector["ontology_delta"], 2 / 3)
        self.assertNotIn("score", vector)

    def test_answer_key_does_not_change_inference(self):
        packet = _packet()
        baseline = run_benchmark(packet)
        mutated = copy.deepcopy(packet)
        for case in mutated["cases"]:
            case["expected_class"] = "DELIBERATELY_WRONG"
        challenger = run_benchmark(mutated)
        for arm in ARMS:
            left = [row["predicted_class"] for row in baseline["arms"][arm]["results"]]
            right = [row["predicted_class"] for row in challenger["arms"][arm]["results"]]
            self.assertEqual(left, right)
        self.assertFalse(baseline["answer_key_used_during_inference"])

    def test_composed_arm_detects_loop_holonomy_but_edge_arm_collapses_endpoint(self):
        packet = _packet()
        case = next(case for case in packet["cases"] if case["case_id"] == "H")
        case = {k: v for k, v in case.items() if k != "expected_class"}
        a1 = evaluate_case(packet, case, "A1_STRATA_MEMBRANE")
        a2 = evaluate_case(packet, case, "A2_COMPOSED_HOLONOMY_LEDGER")
        self.assertEqual(a1["predicted_class"], "ZERO_HOLONOMY_CONTROL")
        self.assertEqual(a2["predicted_class"], "NONZERO_HOLONOMY_EXPECTED")
        self.assertGreater(a2["holonomy_vector"]["role_delta"], 0)
        self.assertEqual(a2["endpoint_vector"]["role_delta"], 0)

    def test_path_order_is_preserved_only_by_composed_arm(self):
        packet = _packet()
        case = next(case for case in packet["cases"] if case["case_id"] == "O")
        case = {k: v for k, v in case.items() if k != "expected_class"}
        a1 = evaluate_case(packet, case, "A1_STRATA_MEMBRANE")
        a2 = evaluate_case(packet, case, "A2_COMPOSED_HOLONOMY_LEDGER")
        self.assertEqual(a1["predicted_class"], "COMMUTATIVE_ASSUMED")
        self.assertEqual(a2["predicted_class"], "NONCOMMUTATIVE_EXPECTED")
        self.assertTrue(a2["path_ledger"]["order_sensitive"])
        self.assertNotEqual(a2["path_ledger"]["ordered_path"], a2["path_ledger"]["permuted_path"])

    def test_equivalence_is_held_when_frozen_features_differ(self):
        packet = _packet()
        case = next(case for case in packet["cases"] if case["case_id"] == "E")
        case = {k: v for k, v in case.items() if k != "expected_class"}
        a0 = evaluate_case(packet, case, "A0_UNSCOPED_REFERENCE")
        a1 = evaluate_case(packet, case, "A1_STRATA_MEMBRANE")
        self.assertEqual(a0["predicted_class"], "ALLOW_EQUIVALENCE")
        self.assertEqual(a1["predicted_class"], "HOLD_EQUIVALENCE")

    def test_unknown_textual_invariants_and_loss_are_not_zeroed(self):
        result = run_benchmark(_packet())
        a2 = result["arms"]["A2_COMPOSED_HOLONOMY_LEDGER"]
        self.assertGreater(a2["metrics"]["unknown_textual_invariant_checks"], 0)
        self.assertGreater(a2["metrics"]["unknown_typed_loss_checks"], 0)

    def test_arm_ladder_matches_fixture_without_using_answer_key_for_inference(self):
        result = run_benchmark(_packet())
        self.assertEqual(result["arms"]["A0_UNSCOPED_REFERENCE"]["assay"]["matches"], 2)
        self.assertEqual(result["arms"]["A1_STRATA_MEMBRANE"]["assay"]["matches"], 3)
        self.assertEqual(result["arms"]["A2_COMPOSED_HOLONOMY_LEDGER"]["assay"]["matches"], 5)
        self.assertEqual(result["arms"]["A2_COMPOSED_HOLONOMY_LEDGER"]["metrics"]["standing_amplification_violations"], 0)
        self.assertEqual(result["arms"]["A2_COMPOSED_HOLONOMY_LEDGER"]["metrics"]["authority_minting_violations"], 0)

    def test_scalarization_rejected(self):
        packet = _packet()
        packet["distance_semantics"]["scalarization"] = "ENABLED"
        with self.assertRaises(ValueError):
            run_benchmark(packet)


if __name__ == "__main__":
    unittest.main()
