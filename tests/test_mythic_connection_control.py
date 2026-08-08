import unittest

from athena_mcp.mythic_connection_control import (
    CONTROL_STANDING,
    UNKNOWN_INVALID_OPERATOR,
    UNKNOWN_MISSING_OPERATOR,
    UNKNOWN_NOT_CLOSED,
    UNKNOWN_PATH_DISCONTINUITY,
    UNKNOWN_UNTYPED_LOSS,
    EdgeOperator,
    FeatureTransform,
    SyntheticConnectionRuntime,
    TransportState,
)


class MythicConnectionControlTests(unittest.TestCase):
    def test_operator_schema_has_no_expected_class_or_oracle_field(self):
        self.assertNotIn("expected_class", EdgeOperator.__dataclass_fields__)
        self.assertNotIn("expected", EdgeOperator.__dataclass_fields__)

    def test_identity_loop_executes_return_operator_and_has_zero_residue(self):
        runtime = SyntheticConnectionRuntime(
            ["x"],
            [EdgeOperator("ID", "A", "A", {"x": FeatureTransform("IDENTITY")}, frozenset())],
        )
        result = runtime.evaluate_closed_loop(TransportState("A", {"x": 2}), ["ID"])
        self.assertEqual("DEFINED", result["status"])
        self.assertTrue(result["projection_back_executed"])
        self.assertEqual("ID", result["projection_back_operator"])
        self.assertEqual(["ID"], result["executed_edge_ids"])
        self.assertFalse(result["closed_loop_residue_nonzero"])
        self.assertEqual(0, result["closed_loop_residue"]["value_mismatch_count"])
        self.assertEqual(0, result["closed_loop_residue"]["irreversible_loss_count"])

    def test_declared_reversible_roundtrip_closes_to_zero(self):
        operators = [
            EdgeOperator(
                "FWD", "A", "B", {"x": FeatureTransform("ADD", 1)}, frozenset(),
                inverse_edge_id="BACK", provenance=("SYNTHETIC:FWD",),
            ),
            EdgeOperator(
                "BACK", "B", "A", {"x": FeatureTransform("ADD", -1)}, frozenset(),
                inverse_edge_id="FWD", provenance=("SYNTHETIC:BACK",),
            ),
        ]
        result = SyntheticConnectionRuntime(["x"], operators).evaluate_closed_loop(
            TransportState("A", {"x": 5}), ["FWD", "BACK"]
        )
        self.assertEqual({"x": 5}, result["final_values"])
        self.assertFalse(result["closed_loop_residue_nonzero"])
        self.assertEqual(["BACK", "FWD"], result["declared_inverse_pairs_observed"][0])
        self.assertEqual(["FWD", "BACK"], result["executed_edge_ids"])
        self.assertEqual("BACK", result["projection_back_operator"])

    def test_verified_typed_loss_survives_value_restoring_return(self):
        operators = [
            EdgeOperator("LOSS_FWD", "A", "B", {"x": FeatureTransform("ADD", 1)}, frozenset({"x"})),
            EdgeOperator("LOSS_BACK", "B", "A", {"x": FeatureTransform("ADD", -1)}, frozenset()),
        ]
        result = SyntheticConnectionRuntime(["x"], operators).evaluate_closed_loop(
            TransportState("A", {"x": 5}), ["LOSS_FWD", "LOSS_BACK"]
        )
        self.assertEqual({"x": 5}, result["final_values"])
        self.assertTrue(result["closed_loop_residue_nonzero"])
        self.assertEqual(0, result["closed_loop_residue"]["value_mismatch_count"])
        self.assertEqual(["x"], result["closed_loop_residue"]["irreversible_loss_features"])
        self.assertEqual(1, result["closed_loop_residue"]["irreversible_loss_count"])

    def test_untyped_loss_returns_unknown_even_when_values_restore(self):
        operators = [
            EdgeOperator(
                "UNTYPED_FWD", "A", "B", {"x": FeatureTransform("ADD", 1)},
                typed_loss=None, loss_standing="UNTYPED_PROSE_ONLY",
            ),
            EdgeOperator("UNTYPED_BACK", "B", "A", {"x": FeatureTransform("ADD", -1)}, frozenset()),
        ]
        result = SyntheticConnectionRuntime(["x"], operators).evaluate_closed_loop(
            TransportState("A", {"x": 5}), ["UNTYPED_FWD", "UNTYPED_BACK"]
        )
        self.assertEqual("UNKNOWN", result["status"])
        self.assertEqual(UNKNOWN_UNTYPED_LOSS, result["standing"])
        self.assertIsNone(result["closed_loop_residue"])
        self.assertFalse(result["projection_back_executed"])

    def test_missing_operator_returns_unknown(self):
        result = SyntheticConnectionRuntime(["x"], []).evaluate_closed_loop(
            TransportState("A", {"x": 1}), ["MISSING"]
        )
        self.assertEqual(UNKNOWN_MISSING_OPERATOR, result["standing"])
        self.assertIsNone(result["closed_loop_residue"])

    def test_open_path_without_return_operator_is_unknown(self):
        runtime = SyntheticConnectionRuntime(
            ["x"],
            [EdgeOperator("FWD", "A", "B", {"x": FeatureTransform("IDENTITY")}, frozenset())],
        )
        result = runtime.evaluate_closed_loop(TransportState("A", {"x": 1}), ["FWD"])
        self.assertEqual(UNKNOWN_NOT_CLOSED, result["standing"])
        self.assertEqual("B", result["final_coordinate"])
        self.assertFalse(result["projection_back_executed"])

    def test_path_discontinuity_is_unknown(self):
        runtime = SyntheticConnectionRuntime(
            ["x"],
            [
                EdgeOperator("AB", "A", "B", {}, frozenset()),
                EdgeOperator("CA", "C", "A", {}, frozenset()),
            ],
        )
        result = runtime.evaluate_closed_loop(TransportState("A", {"x": 1}), ["AB", "CA"])
        self.assertEqual(UNKNOWN_PATH_DISCONTINUITY, result["standing"])
        self.assertEqual(["AB"], result["executed_edge_ids"])

    def test_invalid_declared_inverse_is_unknown_not_proof(self):
        runtime = SyntheticConnectionRuntime(
            ["x"],
            [
                EdgeOperator("F", "A", "B", {}, frozenset(), inverse_edge_id="G"),
                EdgeOperator("G", "B", "C", {}, frozenset(), inverse_edge_id="F"),
            ],
        )
        result = runtime.evaluate_closed_loop(TransportState("A", {"x": 1}), ["F", "G"])
        self.assertEqual(UNKNOWN_INVALID_OPERATOR, result["standing"])
        self.assertTrue(any("INVERSE_COORDINATE_MISMATCH" in x for x in result["errors"]))

    def test_typed_loss_feature_outside_basis_is_invalid(self):
        runtime = SyntheticConnectionRuntime(
            ["x"],
            [EdgeOperator("ID", "A", "A", {}, frozenset({"y"}))],
        )
        result = runtime.evaluate_closed_loop(TransportState("A", {"x": 1}), ["ID"])
        self.assertEqual(UNKNOWN_INVALID_OPERATOR, result["standing"])
        self.assertTrue(any("LOSS_FEATURE_OUTSIDE_BASIS" in x for x in result["errors"]))

    def test_unsupported_transform_is_invalid(self):
        runtime = SyntheticConnectionRuntime(
            ["x"],
            [EdgeOperator("POW", "A", "A", {"x": FeatureTransform("POW", 2)}, frozenset())],
        )
        result = runtime.evaluate_closed_loop(TransportState("A", {"x": 1}), ["POW"])
        self.assertEqual(UNKNOWN_INVALID_OPERATOR, result["standing"])
        self.assertTrue(any("UNSUPPORTED_TRANSFORM" in x for x in result["errors"]))

    def test_noncommuting_operator_order_changes_residue_without_oracle(self):
        operators = [
            EdgeOperator("ADD1", "C", "C", {"x": FeatureTransform("ADD", 1)}, frozenset()),
            EdgeOperator("DOUBLE", "C", "C", {"x": FeatureTransform("MUL", 2)}, frozenset()),
        ]
        runtime = SyntheticConnectionRuntime(["x"], operators)
        add_then_double = runtime.evaluate_closed_loop(TransportState("C", {"x": 1}), ["ADD1", "DOUBLE"])
        double_then_add = runtime.evaluate_closed_loop(TransportState("C", {"x": 1}), ["DOUBLE", "ADD1"])
        self.assertEqual(4, add_then_double["final_values"]["x"])
        self.assertEqual(3, double_then_add["final_values"]["x"])
        self.assertNotEqual(add_then_double["closed_loop_residue"], double_then_add["closed_loop_residue"])
        self.assertFalse(add_then_double["expected_class_used"])
        self.assertFalse(double_then_add["expected_class_used"])

    def test_initial_state_must_equal_declared_ambient_basis(self):
        runtime = SyntheticConnectionRuntime(
            ["x"], [EdgeOperator("ID", "A", "A", {}, frozenset())]
        )
        result = runtime.evaluate_closed_loop(TransportState("A", {"x": 1, "y": 2}), ["ID"])
        self.assertEqual(UNKNOWN_INVALID_OPERATOR, result["standing"])
        self.assertEqual("INITIAL_STATE_FEATURE_BASIS_MISMATCH", result["reason"])

    def test_defined_result_is_explicitly_synthetic_not_source_evidence(self):
        runtime = SyntheticConnectionRuntime(
            ["x"], [EdgeOperator("ID", "A", "A", {}, frozenset())]
        )
        result = runtime.evaluate_closed_loop(TransportState("A", {"x": 1}), ["ID"])
        self.assertEqual(CONTROL_STANDING, result["control_standing"])
        self.assertEqual("NONE_SYNTHETIC_CONTROL", result["source_evidence"])
        self.assertIn("SYNTHETIC_CONTROL != HISTORICAL_SOURCE_WITNESS", result["laws"])


if __name__ == "__main__":
    unittest.main()
