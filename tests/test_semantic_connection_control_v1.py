from __future__ import annotations

import unittest

from athena_mcp.semantic_connection_control_v1 import (
    DEFINED,
    NONZERO_RESIDUE,
    UNKNOWN,
    UNKNOWN_RESIDUE,
    ZERO_RESIDUE,
    EdgeOperator,
    FieldOperation,
    SemanticState,
    compose_closed_route,
    declared_round_trip,
    raw_behavior_with_expected_label,
)


class SemanticConnectionControlV1Tests(unittest.TestCase):
    def test_identity_loop_is_exact_zero_even_with_audit_bookkeeping(self):
        initial = SemanticState("S", {"x": 1, "role": "seed"}, provenance=("SEED",))
        operators = {
            "id": EdgeOperator("id", "S", "S", provenance=("AUDIT::IDENTITY",)),
        }

        result = compose_closed_route(initial, ["id"], operators)

        self.assertEqual(result.standing, DEFINED)
        self.assertEqual(result.classification, ZERO_RESIDUE)
        self.assertEqual(result.residue, {})
        self.assertTrue(result.residue_zero)
        self.assertNotEqual(result.final_state.provenance, initial.provenance)
        self.assertTrue(result.audit["provenance_excluded_from_residue"])

    def test_declared_reversible_round_trip_is_exact_zero(self):
        initial = SemanticState("A", {"x": 7, "role": "signal"})
        operators = {
            "forward": EdgeOperator(
                "forward",
                "A",
                "B",
                operations=(FieldOperation("x", "ADD", 5),),
                inverse_edge_id="reverse",
            ),
            "reverse": EdgeOperator(
                "reverse",
                "B",
                "A",
                operations=(FieldOperation("x", "ADD", -5),),
                inverse_edge_id="forward",
            ),
        }

        result = declared_round_trip(initial, "forward", operators)

        self.assertEqual(result.standing, DEFINED)
        self.assertEqual(result.classification, ZERO_RESIDUE)
        self.assertEqual(result.residue, {})
        self.assertEqual(result.final_state.values, initial.values)
        self.assertEqual(result.executed_edges, ("forward", "reverse"))

    def test_typed_irreversible_loss_survives_return_and_is_nonzero(self):
        initial = SemanticState("A", {"signal": "alpha", "x": 2})
        operators = {
            "loss": EdgeOperator(
                "loss",
                "A",
                "B",
                operations=(FieldOperation("signal", "DELETE"),),
                inverse_edge_id="restore",
                typed_loss=frozenset({"signal"}),
            ),
            "restore": EdgeOperator(
                "restore",
                "B",
                "A",
                operations=(FieldOperation("signal", "SET", "alpha"),),
                inverse_edge_id="loss",
            ),
        }

        result = declared_round_trip(initial, "loss", operators)

        self.assertEqual(result.standing, DEFINED)
        self.assertEqual(result.classification, NONZERO_RESIDUE)
        self.assertFalse(result.residue_zero)
        self.assertEqual(result.final_state.values, initial.values)
        self.assertIn("__irreversible_loss__", result.residue)
        self.assertEqual(result.residue["__irreversible_loss__"]["after"], ["signal"])

    def test_open_path_without_return_operator_is_unknown(self):
        initial = SemanticState("A", {"x": 1})
        operators = {
            "forward": EdgeOperator("forward", "A", "B", operations=(FieldOperation("x", "ADD", 1),)),
        }

        result = compose_closed_route(initial, ["forward"], operators)

        self.assertEqual(result.standing, UNKNOWN)
        self.assertEqual(result.classification, UNKNOWN_RESIDUE)
        self.assertIsNone(result.residue_zero)
        self.assertTrue(result.reason.startswith("OPEN_PATH_NO_RETURN"))

    def test_missing_declared_inverse_is_unknown_not_guessed(self):
        initial = SemanticState("A", {"x": 1})
        operators = {
            "forward": EdgeOperator("forward", "A", "B", operations=(FieldOperation("x", "ADD", 1),)),
        }

        result = declared_round_trip(initial, "forward", operators)

        self.assertEqual(result.standing, UNKNOWN)
        self.assertEqual(result.classification, UNKNOWN_RESIDUE)
        self.assertEqual(result.reason, "MISSING_DECLARED_INVERSE:forward")

    def test_untyped_edge_is_unknown(self):
        initial = SemanticState("A", {"x": 1})
        operators = {
            "legacy": EdgeOperator("legacy", "A", "A", typed=False),
        }

        result = compose_closed_route(initial, ["legacy"], operators)

        self.assertEqual(result.standing, UNKNOWN)
        self.assertEqual(result.reason, "UNTYPED_EDGE:legacy")
        self.assertIsNone(result.residue)

    def test_delete_without_typed_loss_is_unknown(self):
        initial = SemanticState("A", {"signal": "alpha"})
        operators = {
            "bad": EdgeOperator(
                "bad",
                "A",
                "A",
                operations=(FieldOperation("signal", "DELETE"),),
            ),
        }

        result = compose_closed_route(initial, ["bad"], operators)

        self.assertEqual(result.standing, UNKNOWN)
        self.assertTrue(result.reason.startswith("UNTYPED_DELETE:bad:signal"))

    def test_expected_class_mutation_cannot_change_raw_transport_behavior(self):
        initial = SemanticState("S", {"x": 1})
        operators = {"id": EdgeOperator("id", "S", "S")}

        first = raw_behavior_with_expected_label(
            initial,
            ["id"],
            operators,
            expected_class="ZERO_HOLONOMY_CONTROL",
        )
        mutated = raw_behavior_with_expected_label(
            initial,
            ["id"],
            operators,
            expected_class="DELIBERATELY_WRONG",
        )

        self.assertEqual(first.to_dict(), mutated.to_dict())
        self.assertEqual(first.classification, ZERO_RESIDUE)

    def test_oracle_metadata_is_rejected_before_raw_execution(self):
        initial = SemanticState("S", {"x": 1})
        operators = {
            "contaminated": EdgeOperator(
                "contaminated",
                "S",
                "S",
                metadata={"expected_class": "ZERO_RESIDUE"},
            ),
        }

        result = compose_closed_route(initial, ["contaminated"], operators)

        self.assertEqual(result.standing, UNKNOWN)
        self.assertEqual(result.reason, "ORACLE_METADATA_FORBIDDEN:contaminated")

    def test_order_effect_arises_from_declared_noncommuting_operators(self):
        initial = SemanticState("S", {"x": 1})
        operators = {
            "add": EdgeOperator("add", "S", "S", operations=(FieldOperation("x", "ADD", 1),)),
            "scale": EdgeOperator("scale", "S", "S", operations=(FieldOperation("x", "SCALE", 2),)),
        }

        add_then_scale = compose_closed_route(initial, ["add", "scale"], operators)
        scale_then_add = compose_closed_route(initial, ["scale", "add"], operators)

        self.assertEqual(add_then_scale.standing, DEFINED)
        self.assertEqual(scale_then_add.standing, DEFINED)
        self.assertEqual(add_then_scale.final_state.values["x"], 4)
        self.assertEqual(scale_then_add.final_state.values["x"], 3)
        self.assertEqual(add_then_scale.classification, NONZERO_RESIDUE)
        self.assertEqual(scale_then_add.classification, NONZERO_RESIDUE)
        self.assertNotEqual(add_then_scale.residue, scale_then_add.residue)

    def test_same_route_replay_is_deterministic(self):
        initial = SemanticState("S", {"x": 3}, provenance=("SEED",))
        operators = {
            "up": EdgeOperator("up", "S", "S", operations=(FieldOperation("x", "ADD", 2),), provenance=("P",)),
            "down": EdgeOperator("down", "S", "S", operations=(FieldOperation("x", "ADD", -2),), provenance=("Q",)),
        }

        first = compose_closed_route(initial, ["up", "down"], operators)
        replay = compose_closed_route(initial, ["up", "down"], operators)

        self.assertEqual(first.to_dict(), replay.to_dict())
        self.assertEqual(first.classification, ZERO_RESIDUE)


if __name__ == "__main__":
    unittest.main()
