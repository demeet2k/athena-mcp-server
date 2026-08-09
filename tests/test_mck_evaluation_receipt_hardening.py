from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

import athena_mcp.mck_evaluation_receipt_v1 as receipt_mod
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
        "feature_basis": ["x"],
        "operators": [
            {
                "edge_id": "FWD", "source_coordinate": "A", "target_coordinate": "B",
                "transforms": {"x": {"op": "ADD", "operand": 1}}, "typed_loss": [],
                "loss_standing": PACKET_LOSS_STANDING, "inverse_edge_id": "BACK",
                "provenance": ["SYNTHETIC:FWD"], "standing": PACKET_STANDING,
            },
            {
                "edge_id": "BACK", "source_coordinate": "B", "target_coordinate": "A",
                "transforms": {"x": {"op": "ADD", "operand": -1}}, "typed_loss": [],
                "loss_standing": PACKET_LOSS_STANDING, "inverse_edge_id": "FWD",
                "provenance": ["SYNTHETIC:BACK"], "standing": PACKET_STANDING,
            },
        ],
        "historical_mapping": {"status": HISTORICAL_MAPPING_STATUS, "edges": []},
        "firewalls": sorted(MANDATORY_FIREWALLS),
    }


def state():
    return SemanticState("A", {"x": 5}, feature_basis=("x",), provenance=("SEED",))


def reseal_outer_coordinates(forged):
    normalized_initial = receipt_mod._normalize_audit_state(forged["initial_state"])
    normalized_path = receipt_mod._normalize_path(forged["edge_path"])
    forged["initial_state_digest"] = receipt_mod._domain_digest(
        receipt_mod.STATE_DIGEST_DOMAIN,
        normalized_initial,
    )
    forged["ordered_path_digest"] = receipt_mod._domain_digest(
        receipt_mod.PATH_DIGEST_DOMAIN,
        normalized_path,
    )
    input_payload = receipt_mod._evaluation_input_payload(
        packet_semantic_digest=forged["packet_semantic_digest"],
        operator_registry_digest=forged["operator_registry_digest"],
        initial_state=normalized_initial,
        edge_path=normalized_path,
    )
    forged["evaluation_input_digest"] = receipt_mod._domain_digest(
        receipt_mod.INPUT_DIGEST_DOMAIN,
        input_payload,
    )
    forged["receipt_digest"] = receipt_mod._domain_digest(
        receipt_mod.RECEIPT_DIGEST_DOMAIN,
        receipt_mod._receipt_identity_payload(forged),
    )
    forged["receipt_id"] = f"MCK-EVAL-{forged['receipt_digest'][:24]}"
    return forged


class MckEvaluationReceiptHardeningTests(unittest.TestCase):
    def good_receipt(self):
        value = receipt_mod.build_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        self.assertEqual("RECORDED", value["status"])
        return value

    def test_future_packet_compiler_revision_drift_holds(self):
        with patch.object(receipt_mod, "PACKET_COMPILER_REVISION", "FUTURE.COMPILER"):
            value = receipt_mod.build_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        self.assertEqual("HOLD", value["status"])
        self.assertEqual("PACKET_COMPILER_REVISION_DRIFT", value["reason"])
        self.assertIsNone(value["receipt_id"])

    def test_scalar_stored_initial_state_holds_before_replay(self):
        forged = self.good_receipt()
        forged["initial_state"] = "NOT_AN_OBJECT"
        result = receipt_mod.validate_evaluation_receipt(forged)
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(any("RECEIPT_INITIAL_STATE_SCHEMA_DRIFT" in x for x in result["errors"]))

    def test_mapping_path_is_not_accepted_as_sequence(self):
        forged = self.good_receipt()
        forged["edge_path"] = {"not": "a list"}
        result = receipt_mod.validate_evaluation_receipt(forged)
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(any("edge_path must be a sequence" in x for x in result["errors"]))

    def test_duplicate_stored_basis_holds(self):
        forged = self.good_receipt()
        forged["initial_state"]["feature_basis"] = ["x", "x"]
        result = receipt_mod.validate_evaluation_receipt(forged)
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(any("DUPLICATE_RECEIPT_INITIAL_FEATURE_BASIS" in x for x in result["errors"]))

    def test_state_raw_result_binding_cannot_be_split(self):
        forged = self.good_receipt()
        forged["initial_state"]["values"]["x"] = 6
        reseal_outer_coordinates(forged)
        result = receipt_mod.validate_evaluation_receipt(forged)
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(any("RECEIPT_INITIAL_STATE_RAW_RESULT_MISMATCH" in x for x in result["errors"]))

    def test_path_raw_result_binding_cannot_be_split(self):
        forged = self.good_receipt()
        forged["edge_path"] = ["FWD", "BACK", "FWD", "BACK"]
        reseal_outer_coordinates(forged)
        result = receipt_mod.validate_evaluation_receipt(forged)
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(any("RECEIPT_PATH_RAW_RESULT_MISMATCH" in x for x in result["errors"]))

    def test_extra_trust_field_rejected_before_digest_semantics(self):
        forged = self.good_receipt()
        forged["source_verified"] = True
        result = receipt_mod.validate_evaluation_receipt(forged)
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(any("RECEIPT_SHAPE_MISMATCH" in x for x in result["errors"]))


if __name__ == "__main__":
    unittest.main()
