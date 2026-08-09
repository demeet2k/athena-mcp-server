from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from athena_mcp.mck_evaluation_receipt_v1 import (
    build_evaluation_receipt,
    replay_stored_evaluation_receipt,
    validate_evaluation_receipt,
)
from athena_mcp.mythic_connection_packet import (
    HISTORICAL_MAPPING_STATUS,
    MANDATORY_FIREWALLS,
    PACKET_ARTIFACT,
    PACKET_LOSS_STANDING,
    PACKET_STANDING,
    PACKET_VERSION,
)
from athena_mcp.semantic_connection_control_v1 import SemanticState


def packet():
    return {
        "artifact": PACKET_ARTIFACT,
        "version": PACKET_VERSION,
        "standing": PACKET_STANDING,
        "feature_basis": ["x", "y"],
        "operators": [
            {
                "edge_id": "FWD",
                "source_coordinate": "A",
                "target_coordinate": "B",
                "transforms": {
                    "x": {"op": "ADD", "operand": 1},
                    "y": {"op": "ADD", "operand": 2},
                },
                "typed_loss": [],
                "loss_standing": PACKET_LOSS_STANDING,
                "inverse_edge_id": "BACK",
                "provenance": ["SYNTHETIC:FWD"],
                "standing": PACKET_STANDING,
            },
            {
                "edge_id": "BACK",
                "source_coordinate": "B",
                "target_coordinate": "A",
                "transforms": {
                    "x": {"op": "ADD", "operand": -1},
                    "y": {"op": "ADD", "operand": -2},
                },
                "typed_loss": [],
                "loss_standing": PACKET_LOSS_STANDING,
                "inverse_edge_id": "FWD",
                "provenance": ["SYNTHETIC:BACK"],
                "standing": PACKET_STANDING,
            },
        ],
        "historical_mapping": {
            "status": HISTORICAL_MAPPING_STATUS,
            "edges": [],
        },
        "firewalls": sorted(MANDATORY_FIREWALLS),
    }


def state(x=5, y=9, *, basis=("x", "y"), provenance=("SEED",)):
    values = {"x": x, "y": y}
    return SemanticState(
        "A",
        values,
        feature_basis=basis,
        provenance=provenance,
    )


class MckEvaluationReceiptStatePathTests(unittest.TestCase):
    def test_required_execution_coordinates_are_independent_64_hex_digests(self):
        receipt = build_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        self.assertEqual("RECORDED", receipt["status"])
        for key in (
            "initial_state_digest",
            "ordered_path_digest",
            "semantic_result_digest",
            "receipt_digest",
        ):
            self.assertRegex(receipt[key], r"^[0-9a-f]{64}$", key)
        self.assertEqual("VALID", validate_evaluation_receipt(receipt)["status"])

    def test_state_change_moves_state_and_receipt_without_moving_path(self):
        first = build_evaluation_receipt(packet(), state(x=5), ["FWD", "BACK"])
        second = build_evaluation_receipt(packet(), state(x=6), ["FWD", "BACK"])
        self.assertNotEqual(first["initial_state_digest"], second["initial_state_digest"])
        self.assertEqual(first["ordered_path_digest"], second["ordered_path_digest"])
        self.assertNotEqual(first["semantic_result_digest"], second["semantic_result_digest"])
        self.assertNotEqual(first["receipt_digest"], second["receipt_digest"])

    def test_longer_equivalent_loop_moves_path_not_semantic_result(self):
        short = build_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        long = build_evaluation_receipt(
            packet(),
            state(),
            ["FWD", "BACK", "FWD", "BACK"],
        )
        self.assertEqual(short["initial_state_digest"], long["initial_state_digest"])
        self.assertNotEqual(short["ordered_path_digest"], long["ordered_path_digest"])
        self.assertEqual(short["semantic_result_digest"], long["semantic_result_digest"])
        self.assertNotEqual(short["raw_result_digest"], long["raw_result_digest"])
        self.assertNotEqual(short["receipt_digest"], long["receipt_digest"])

    def test_provenance_only_change_moves_state_audit_not_semantic_result(self):
        first = build_evaluation_receipt(
            packet(),
            state(provenance=("TRACE:A",)),
            ["FWD", "BACK"],
        )
        second = build_evaluation_receipt(
            packet(),
            state(provenance=("TRACE:B",)),
            ["FWD", "BACK"],
        )
        self.assertNotEqual(first["initial_state_digest"], second["initial_state_digest"])
        self.assertEqual(first["ordered_path_digest"], second["ordered_path_digest"])
        self.assertEqual(first["semantic_result_digest"], second["semantic_result_digest"])
        self.assertNotEqual(first["receipt_digest"], second["receipt_digest"])

    def test_equivalent_feature_basis_permutation_is_canonicalized_before_execution(self):
        canonical = build_evaluation_receipt(
            packet(),
            state(basis=("x", "y")),
            ["FWD", "BACK"],
        )
        permuted = build_evaluation_receipt(
            packet(),
            state(basis=("y", "x")),
            ["FWD", "BACK"],
        )
        self.assertEqual("RECORDED", canonical["status"])
        self.assertEqual(canonical, permuted)
        self.assertEqual(["x", "y"], permuted["initial_state"]["feature_basis"])

    def test_receipt_can_replay_from_its_own_frozen_state_and_path(self):
        stored = build_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        replay = replay_stored_evaluation_receipt(stored, packet())
        self.assertEqual("MATCH", replay["status"])
        self.assertEqual("EXACT_REPLAY_MATCH", replay["reason"])
        self.assertEqual(stored["receipt_id"], replay["stored_receipt_id"])
        self.assertEqual(stored["receipt_id"], replay["replay_receipt_id"])
        self.assertEqual([], replay["mismatches"])

    def test_state_digest_tamper_is_detected_independently(self):
        forged = build_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        forged["initial_state_digest"] = "0" * 64
        result = validate_evaluation_receipt(forged)
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(any("INITIAL_STATE_DIGEST_MISMATCH" in error for error in result["errors"]))

    def test_path_digest_tamper_is_detected_independently(self):
        forged = build_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        forged["ordered_path_digest"] = "0" * 64
        result = validate_evaluation_receipt(forged)
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(any("ORDERED_PATH_DIGEST_MISMATCH" in error for error in result["errors"]))

    def test_original_state_and_path_mutation_after_build_cannot_change_receipt(self):
        source_path = ["FWD", "BACK"]
        source_state = state()
        receipt = build_evaluation_receipt(packet(), source_state, source_path)
        frozen = copy.deepcopy(receipt)
        source_path.append("FWD")
        source_state.values["x"] = 999
        self.assertEqual(frozen, receipt)

    def test_schema_requires_state_and_path_digests(self):
        schema_path = (
            Path(__file__).resolve().parents[1]
            / "schemas"
            / "mck_evaluation_receipt_v1.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertIn("initial_state_digest", schema["required"])
        self.assertIn("ordered_path_digest", schema["required"])
        self.assertEqual(
            "^[0-9a-f]{64}$",
            schema["properties"]["initial_state_digest"]["pattern"],
        )
        self.assertEqual(
            "^[0-9a-f]{64}$",
            schema["properties"]["ordered_path_digest"]["pattern"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
