from __future__ import annotations

import math
import unittest

from athena_mcp.semantic_connection_control_v1 import (
    UNKNOWN,
    EdgeOperator,
    FieldOperation,
    SemanticState,
    compose_closed_route,
    digest,
)


class SemanticConnectionControlHardeningTests(unittest.TestCase):
    def test_duplicate_explicit_feature_basis_rejects_before_normalization(self):
        with self.assertRaisesRegex(ValueError, "feature_basis contains duplicates"):
            SemanticState(
                "A",
                {"x": 1},
                feature_basis=("x", "x"),
            )

    def test_empty_explicit_feature_name_rejects(self):
        with self.assertRaisesRegex(ValueError, "feature_basis contains empty feature"):
            SemanticState(
                "A",
                {"x": 1},
                feature_basis=("x", ""),
            )

    def test_non_string_state_key_rejects(self):
        with self.assertRaisesRegex(ValueError, "values keys must be non-empty strings"):
            SemanticState("A", {1: "x"})

    def test_nonfinite_state_values_reject_strict_json(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    SemanticState("A", {"x": value})

    def test_nested_nonfinite_state_value_rejects_strict_json(self):
        with self.assertRaises(ValueError):
            SemanticState("A", {"x": {"nested": [1, math.nan]}})

    def test_digest_rejects_nonfinite_json(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    digest({"x": value})

    def test_add_and_scale_reject_bool_operands(self):
        for op in ("ADD", "SCALE"):
            with self.subTest(op=op):
                with self.assertRaisesRegex(
                    ValueError,
                    f"{op} requires a finite non-bool numeric value",
                ):
                    FieldOperation("x", op, True)

    def test_add_and_scale_reject_nonfinite_operands(self):
        for op in ("ADD", "SCALE"):
            for value in (math.nan, math.inf, -math.inf):
                with self.subTest(op=op, value=value):
                    with self.assertRaisesRegex(
                        ValueError,
                        f"{op} requires a finite non-bool numeric value",
                    ):
                        FieldOperation("x", op, value)

    def test_set_rejects_nonfinite_json(self):
        with self.assertRaises(ValueError):
            FieldOperation("x", "SET", {"nested": math.nan})

    def test_identity_and_delete_reject_operands(self):
        for op in ("IDENTITY", "DELETE"):
            with self.subTest(op=op):
                with self.assertRaisesRegex(ValueError, f"{op} does not accept a value"):
                    FieldOperation("x", op, 0)

    def test_nested_expected_class_metadata_is_rejected_before_execution(self):
        initial = SemanticState("S", {"x": 1})
        edge = EdgeOperator(
            "contaminated",
            "S",
            "S",
            metadata={"nested": {"expected_class": "ZERO_RESIDUE"}},
        )
        result = compose_closed_route(initial, ["contaminated"], {"contaminated": edge})
        self.assertEqual(UNKNOWN, result.standing)
        self.assertEqual("ORACLE_METADATA_FORBIDDEN:contaminated", result.reason)
        self.assertEqual((), result.executed_edges)

    def test_nested_oracle_and_benchmark_label_metadata_are_rejected(self):
        contaminants = [
            {"nested": [{"oracle": "ALLOW"}]},
            {"nested": [{"benchmark_label": "PASS"}]},
            {"nested": [{"expected": "ZERO"}]},
        ]
        for metadata in contaminants:
            with self.subTest(metadata=metadata):
                initial = SemanticState("S", {"x": 1})
                edge = EdgeOperator("e", "S", "S", metadata=metadata)
                result = compose_closed_route(initial, ["e"], {"e": edge})
                self.assertEqual(UNKNOWN, result.standing)
                self.assertEqual("ORACLE_METADATA_FORBIDDEN:e", result.reason)
                self.assertEqual((), result.executed_edges)

    def test_clean_nested_metadata_is_allowed_and_audit_only(self):
        initial = SemanticState("S", {"x": 1})
        edge = EdgeOperator(
            "e",
            "S",
            "S",
            metadata={"nested": [{"source_ref": "fixture:1"}]},
            provenance=("AUDIT::EDGE",),
        )
        result = compose_closed_route(initial, ["e"], {"e": edge})
        self.assertTrue(result.residue_zero)
        self.assertEqual({}, result.residue)
        self.assertTrue(result.audit["provenance_excluded_from_residue"])

    def test_nonfinite_numeric_result_fails_closed(self):
        initial = SemanticState("S", {"x": 1e308})
        edge = EdgeOperator(
            "overflow",
            "S",
            "S",
            operations=(FieldOperation("x", "SCALE", 1e308),),
        )
        result = compose_closed_route(initial, ["overflow"], {"overflow": edge})
        self.assertEqual(UNKNOWN, result.standing)
        self.assertEqual(
            "NONFINITE_NUMERIC_RESULT:x:overflow",
            result.reason,
        )
        self.assertEqual((), result.executed_edges)
        self.assertIsNone(result.residue)

    def test_bool_current_value_is_not_numeric_transport_state(self):
        initial = SemanticState("S", {"x": True})
        edge = EdgeOperator(
            "add",
            "S",
            "S",
            operations=(FieldOperation("x", "ADD", 1),),
        )
        result = compose_closed_route(initial, ["add"], {"add": edge})
        self.assertEqual(UNKNOWN, result.standing)
        self.assertEqual("NON_NUMERIC_FIELD:x:add", result.reason)
        self.assertEqual((), result.executed_edges)


if __name__ == "__main__":
    unittest.main()
