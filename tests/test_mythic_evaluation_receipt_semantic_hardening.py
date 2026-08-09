import copy
import unittest
from unittest.mock import patch

import athena_mcp.mythic_evaluation_receipt_semantic_v1 as receipt_mod
from athena_mcp.mythic_connection_packet import (
    HISTORICAL_MAPPING_STATUS,
    MANDATORY_FIREWALLS,
    PACKET_ARTIFACT,
    PACKET_LOSS_STANDING,
    PACKET_STANDING,
    PACKET_VERSION,
)


FIREWALLS = sorted(MANDATORY_FIREWALLS)


def valid_packet():
    return {
        "artifact": PACKET_ARTIFACT,
        "version": PACKET_VERSION,
        "standing": PACKET_STANDING,
        "feature_basis": ["x"],
        "operators": [
            {
                "edge_id": "FWD",
                "source_coordinate": "A",
                "target_coordinate": "B",
                "transforms": {"x": {"op": "ADD", "operand": 1}},
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
                "transforms": {"x": {"op": "ADD", "operand": -1}},
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
        "firewalls": list(FIREWALLS),
    }


def initial_state():
    return {
        "coordinate": "A",
        "values": {"x": 5},
        "irreversible_loss": [],
        "provenance": ["SYNTHETIC:INITIAL"],
    }


def redigest(value):
    payload = {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != "evaluation_receipt_digest"
    }
    value["evaluation_receipt_digest"] = receipt_mod._domain_digest(
        receipt_mod.RECEIPT_DIGEST_DOMAIN,
        payload,
    )
    return value


class MythicEvaluationReceiptSemanticHardeningTests(unittest.TestCase):
    def good_receipt(self):
        result = receipt_mod.create_evaluation_receipt(
            valid_packet(), initial_state(), ["FWD", "BACK"]
        )
        self.assertEqual("EVALUATED", result["status"])
        return result

    def test_future_packet_compiler_revision_drift_holds_not_raises(self):
        with patch.object(receipt_mod, "COMPILER_REVISION", "FUTURE.COMPILER.REVISION"):
            result = receipt_mod.create_evaluation_receipt(
                valid_packet(), initial_state(), ["FWD", "BACK"]
            )
        self.assertEqual("HOLD", result["status"])
        self.assertEqual(
            "PACKET_COMPILER_REVISION_DRIFT",
            result["errors"][0]["code"],
        )
        self.assertIsNone(result["evaluation_receipt_digest"])

    def test_redigested_scalar_initial_state_holds_before_dereference(self):
        forged = self.good_receipt()
        forged["initial_state"] = "NOT_AN_OBJECT"
        redigest(forged)
        result = receipt_mod.replay_evaluation_receipt(valid_packet(), forged)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("RECEIPT_INITIAL_STATE_NOT_OBJECT", result["errors"][0]["code"])

    def test_redigested_malformed_path_holds_before_reexecution(self):
        forged = self.good_receipt()
        forged["ordered_path"] = {"not": "a list"}
        redigest(forged)
        result = receipt_mod.replay_evaluation_receipt(valid_packet(), forged)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("INVALID_ORDERED_PATH", result["errors"][0]["code"])

    def test_redigested_state_change_cannot_reuse_old_state_digest(self):
        forged = self.good_receipt()
        forged["initial_state"]["values"]["x"] = 6
        redigest(forged)
        result = receipt_mod.replay_evaluation_receipt(valid_packet(), forged)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual(
            "RECEIPT_INITIAL_STATE_DIGEST_MISMATCH",
            result["errors"][0]["code"],
        )

    def test_redigested_path_change_cannot_reuse_old_path_digest(self):
        forged = self.good_receipt()
        forged["ordered_path"] = ["FWD", "BACK", "FWD", "BACK"]
        redigest(forged)
        result = receipt_mod.replay_evaluation_receipt(valid_packet(), forged)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual(
            "RECEIPT_ORDERED_PATH_DIGEST_MISMATCH",
            result["errors"][0]["code"],
        )

    def test_redigested_duplicate_stored_basis_holds(self):
        forged = self.good_receipt()
        forged["initial_state"]["feature_basis"] = ["x", "x"]
        redigest(forged)
        result = receipt_mod.replay_evaluation_receipt(valid_packet(), forged)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual(
            "DUPLICATE_RECEIPT_INITIAL_FEATURE_BASIS",
            result["errors"][0]["code"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
