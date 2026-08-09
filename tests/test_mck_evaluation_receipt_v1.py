from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from athena_mcp.mck_evaluation_receipt_v1 import (
    ARTIFACT,
    CI_QUALIFICATION,
    EVIDENCE_STANDING,
    HISTORICAL_MAPPING,
    INDEPENDENT_WITNESS,
    RECEIPT_STANDING,
    REPLAY_ARTIFACT,
    SOURCE_EVIDENCE,
    VERSION,
    build_evaluation_receipt,
    replay_evaluation_receipt,
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


def reversible_packet():
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
        "firewalls": sorted(MANDATORY_FIREWALLS),
    }


def initial_state(x=5, *, provenance=("SEED",)):
    return SemanticState(
        "A",
        {"x": x},
        feature_basis=("x",),
        provenance=provenance,
    )


class MckEvaluationReceiptV1Tests(unittest.TestCase):
    def test_same_input_produces_identical_receipt(self):
        first = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", "BACK"]
        )
        second = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", "BACK"]
        )
        self.assertEqual(first, second)
        self.assertEqual("RECORDED", first["status"])
        self.assertEqual(ARTIFACT, first["artifact"])
        self.assertEqual(VERSION, first["version"])
        self.assertEqual(RECEIPT_STANDING, first["receipt_standing"])
        self.assertEqual(EVIDENCE_STANDING, first["evidence_standing"])
        self.assertEqual(SOURCE_EVIDENCE, first["source_evidence"])
        self.assertEqual(HISTORICAL_MAPPING, first["historical_mapping"])
        self.assertEqual(INDEPENDENT_WITNESS, first["independent_witness"])
        self.assertEqual(CI_QUALIFICATION, first["ci_qualification"])
        self.assertEqual(64, len(first["evaluation_input_digest"]))
        self.assertEqual(64, len(first["raw_result_digest"]))
        self.assertEqual(64, len(first["receipt_digest"]))
        self.assertTrue(first["receipt_id"].startswith("MCK-EVAL-"))

    def test_recorded_receipt_validates(self):
        receipt = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", "BACK"]
        )
        validation = validate_evaluation_receipt(receipt)
        self.assertEqual("VALID", validation["status"])
        self.assertEqual(receipt["receipt_id"], validation["receipt_id"])
        self.assertEqual(receipt["receipt_digest"], validation["receipt_digest"])

    def test_packet_operator_order_reordering_is_identity_invariant(self):
        packet_a = reversible_packet()
        packet_b = reversible_packet()
        packet_b["operators"].reverse()
        a = build_evaluation_receipt(packet_a, initial_state(), ["FWD", "BACK"])
        b = build_evaluation_receipt(packet_b, initial_state(), ["FWD", "BACK"])
        self.assertEqual(a["packet_semantic_digest"], b["packet_semantic_digest"])
        self.assertEqual(a["operator_registry_digest"], b["operator_registry_digest"])
        self.assertEqual(a["evaluation_input_digest"], b["evaluation_input_digest"])
        self.assertEqual(a["raw_result_digest"], b["raw_result_digest"])
        self.assertEqual(a["receipt_digest"], b["receipt_digest"])
        self.assertEqual(a["receipt_id"], b["receipt_id"])

    def test_initial_value_change_splits_input_result_and_receipt_identity(self):
        a = build_evaluation_receipt(
            reversible_packet(), initial_state(5), ["FWD", "BACK"]
        )
        b = build_evaluation_receipt(
            reversible_packet(), initial_state(6), ["FWD", "BACK"]
        )
        self.assertNotEqual(a["evaluation_input_digest"], b["evaluation_input_digest"])
        self.assertNotEqual(a["raw_result_digest"], b["raw_result_digest"])
        self.assertNotEqual(a["receipt_digest"], b["receipt_digest"])

    def test_initial_provenance_is_bound_as_full_initial_state(self):
        a = build_evaluation_receipt(
            reversible_packet(), initial_state(provenance=("SEED-A",)), ["FWD", "BACK"]
        )
        b = build_evaluation_receipt(
            reversible_packet(), initial_state(provenance=("SEED-B",)), ["FWD", "BACK"]
        )
        self.assertNotEqual(a["evaluation_input_digest"], b["evaluation_input_digest"])
        self.assertNotEqual(a["raw_result_digest"], b["raw_result_digest"])
        self.assertNotEqual(a["receipt_digest"], b["receipt_digest"])

    def test_ordered_path_change_splits_identity(self):
        normal = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", "BACK"]
        )
        reversed_path = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["BACK", "FWD"]
        )
        self.assertEqual("RECORDED", reversed_path["status"])
        self.assertNotEqual(
            normal["evaluation_input_digest"], reversed_path["evaluation_input_digest"]
        )
        self.assertNotEqual(normal["raw_result_digest"], reversed_path["raw_result_digest"])
        self.assertEqual("UNKNOWN", reversed_path["raw_result"]["standing"])
        self.assertIsNone(reversed_path["raw_result"]["residue"])

    def test_packet_semantic_change_splits_declaration_and_receipt_identity(self):
        packet_a = reversible_packet()
        packet_b = reversible_packet()
        packet_b["operators"][0]["transforms"]["x"]["operand"] = 2
        a = build_evaluation_receipt(packet_a, initial_state(), ["FWD", "BACK"])
        b = build_evaluation_receipt(packet_b, initial_state(), ["FWD", "BACK"])
        self.assertNotEqual(a["packet_semantic_digest"], b["packet_semantic_digest"])
        self.assertNotEqual(a["operator_registry_digest"], b["operator_registry_digest"])
        self.assertNotEqual(a["evaluation_input_digest"], b["evaluation_input_digest"])
        self.assertNotEqual(a["receipt_digest"], b["receipt_digest"])

    def test_invalid_packet_hold_has_no_execution_identity(self):
        packet = reversible_packet()
        packet["expected_class"] = "ZERO_RESIDUE"
        receipt = build_evaluation_receipt(packet, initial_state(), ["FWD", "BACK"])
        self.assertEqual("HOLD", receipt["status"])
        self.assertEqual("PACKET_VALIDATION_HOLD", receipt["reason"])
        self.assertIsNone(receipt["receipt_id"])
        self.assertIsNone(receipt["execution_identity"])
        self.assertEqual(SOURCE_EVIDENCE, receipt["source_evidence"])

    def test_unknown_execution_is_recorded_without_invented_residue(self):
        receipt = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["MISSING_EDGE"]
        )
        self.assertEqual("RECORDED", receipt["status"])
        self.assertEqual("UNKNOWN", receipt["raw_result"]["standing"])
        self.assertEqual("UNKNOWN_RESIDUE", receipt["raw_result"]["classification"])
        self.assertIsNone(receipt["raw_result"]["residue"])
        self.assertIsNone(receipt["raw_result"]["residue_zero"])

    def test_empty_identity_route_is_recorded_exactly(self):
        receipt = build_evaluation_receipt(reversible_packet(), initial_state(), [])
        self.assertEqual("RECORDED", receipt["status"])
        self.assertEqual("DEFINED", receipt["raw_result"]["standing"])
        self.assertEqual("ZERO_RESIDUE", receipt["raw_result"]["classification"])
        self.assertEqual({}, receipt["raw_result"]["residue"])
        self.assertEqual([], receipt["edge_path"])

    def test_invalid_path_input_holds_before_execution_identity(self):
        receipt = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", ""]
        )
        self.assertEqual("HOLD", receipt["status"])
        self.assertTrue(receipt["reason"].startswith("INVALID_EVALUATION_INPUT"))
        self.assertIsNone(receipt["receipt_id"])

    def test_reserved_caller_trust_claims_cannot_self_mint_standing(self):
        claims = [
            {"ci_status": "PASS"},
            {"nested": {"authority": "ROOT"}},
            {"nested": [{"source_verified": True}]},
            {"nested": [{"independent_witness": True}]},
            {"nested": [{"oracle": "PASS"}]},
            {"nested": [{"benchmark_label": "WIN"}]},
            {"promotion": "QUALIFIED"},
        ]
        for caller_claims in claims:
            with self.subTest(caller_claims=caller_claims):
                receipt = build_evaluation_receipt(
                    reversible_packet(),
                    initial_state(),
                    ["FWD", "BACK"],
                    caller_claims=caller_claims,
                )
                self.assertEqual("HOLD", receipt["status"])
                self.assertTrue(receipt["reason"].startswith("CALLER_TRUST_CLAIM_FORBIDDEN"))
                self.assertIsNone(receipt["receipt_id"])
                self.assertEqual(SOURCE_EVIDENCE, receipt["source_evidence"])
                self.assertFalse(receipt["independent_witness"])

    def test_even_benign_caller_context_is_not_admitted_in_v1_identity(self):
        receipt = build_evaluation_receipt(
            reversible_packet(),
            initial_state(),
            ["FWD", "BACK"],
            caller_claims={"note": "hello"},
        )
        self.assertEqual("HOLD", receipt["status"])
        self.assertEqual("CALLER_CONTEXT_NOT_ADMITTED_V1", receipt["reason"])
        self.assertIsNone(receipt["receipt_id"])

    def test_mutating_source_objects_after_recording_cannot_change_receipt(self):
        packet = reversible_packet()
        values = {"x": 5}
        state = SemanticState("A", values, feature_basis=("x",), provenance=("SEED",))
        receipt = build_evaluation_receipt(packet, state, ["FWD", "BACK"])
        frozen = copy.deepcopy(receipt)

        packet["operators"][0]["transforms"]["x"]["operand"] = 999
        values["x"] = 999

        self.assertEqual(frozen, receipt)
        self.assertEqual(5, receipt["initial_state"]["values"]["x"])
        self.assertEqual("VALID", validate_evaluation_receipt(receipt)["status"])

    def test_raw_result_tamper_invalidates_receipt(self):
        receipt = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", "BACK"]
        )
        tampered = copy.deepcopy(receipt)
        tampered["raw_result"]["classification"] = "NONZERO_RESIDUE"
        validation = validate_evaluation_receipt(tampered)
        self.assertEqual("HOLD", validation["status"])
        self.assertTrue(any("RAW_RESULT_DIGEST_MISMATCH" in x for x in validation["errors"]))

    def test_standing_tamper_invalidates_receipt(self):
        receipt = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", "BACK"]
        )
        mutations = {
            "source_evidence": "SOURCE_VERIFIED",
            "evidence_standing": "INDEPENDENT_SOURCE_VALIDATION",
            "independent_witness": True,
            "authority_delta": "ROOT",
            "ci_qualification": "QUALIFIED",
        }
        for key, value in mutations.items():
            with self.subTest(key=key):
                tampered = copy.deepcopy(receipt)
                tampered[key] = value
                self.assertEqual("HOLD", validate_evaluation_receipt(tampered)["status"])

    def test_receipt_id_and_digest_tamper_are_detected(self):
        receipt = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", "BACK"]
        )
        tampered = copy.deepcopy(receipt)
        tampered["receipt_id"] = "MCK-EVAL-" + "0" * 24
        self.assertEqual("HOLD", validate_evaluation_receipt(tampered)["status"])

        tampered = copy.deepcopy(receipt)
        tampered["receipt_digest"] = "0" * 64
        self.assertEqual("HOLD", validate_evaluation_receipt(tampered)["status"])

    def test_exact_replay_matches(self):
        packet = reversible_packet()
        state = initial_state()
        path = ["FWD", "BACK"]
        receipt = build_evaluation_receipt(packet, state, path)
        replay = replay_evaluation_receipt(receipt, packet, state, path)
        self.assertEqual(REPLAY_ARTIFACT, replay["artifact"])
        self.assertEqual("MATCH", replay["status"])
        self.assertEqual([], replay["mismatches"])
        self.assertEqual(receipt["receipt_id"], replay["replay_receipt_id"])
        self.assertFalse(replay["independent_witness"])

    def test_changed_packet_replay_mismatches(self):
        packet = reversible_packet()
        receipt = build_evaluation_receipt(packet, initial_state(), ["FWD", "BACK"])
        changed = reversible_packet()
        changed["operators"][0]["transforms"]["x"]["operand"] = 2
        replay = replay_evaluation_receipt(
            receipt, changed, initial_state(), ["FWD", "BACK"]
        )
        self.assertEqual("MISMATCH", replay["status"])
        self.assertIn("packet_semantic_digest", replay["mismatches"])
        self.assertIn("operator_registry_digest", replay["mismatches"])
        self.assertIn("evaluation_input_digest", replay["mismatches"])

    def test_changed_initial_state_replay_mismatches(self):
        packet = reversible_packet()
        receipt = build_evaluation_receipt(packet, initial_state(5), ["FWD", "BACK"])
        replay = replay_evaluation_receipt(
            receipt, packet, initial_state(6), ["FWD", "BACK"]
        )
        self.assertEqual("MISMATCH", replay["status"])
        self.assertIn("evaluation_input_digest", replay["mismatches"])
        self.assertIn("raw_result_digest", replay["mismatches"])

    def test_changed_path_replay_mismatches(self):
        packet = reversible_packet()
        receipt = build_evaluation_receipt(packet, initial_state(), ["FWD", "BACK"])
        replay = replay_evaluation_receipt(
            receipt, packet, initial_state(), ["BACK", "FWD"]
        )
        self.assertEqual("MISMATCH", replay["status"])
        self.assertIn("evaluation_input_digest", replay["mismatches"])
        self.assertIn("raw_result_digest", replay["mismatches"])

    def test_invalid_stored_receipt_replay_holds(self):
        packet = reversible_packet()
        receipt = build_evaluation_receipt(packet, initial_state(), ["FWD", "BACK"])
        receipt["raw_result_digest"] = "0" * 64
        replay = replay_evaluation_receipt(
            receipt, packet, initial_state(), ["FWD", "BACK"]
        )
        self.assertEqual("HOLD", replay["status"])
        self.assertEqual("STORED_RECEIPT_INVALID", replay["reason"])

    def test_schema_freezes_non_promotional_evidence_boundary(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "schemas"
            / "mck_evaluation_receipt_v1.schema.json"
        )
        schema = json.loads(path.read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(ARTIFACT, props["artifact"]["const"])
        self.assertEqual(VERSION, props["version"]["const"])
        self.assertEqual(RECEIPT_STANDING, props["receipt_standing"]["const"])
        self.assertEqual(EVIDENCE_STANDING, props["evidence_standing"]["const"])
        self.assertEqual(SOURCE_EVIDENCE, props["source_evidence"]["const"])
        self.assertEqual(HISTORICAL_MAPPING, props["historical_mapping"]["const"])
        self.assertFalse(props["independent_witness"]["const"])
        self.assertEqual(CI_QUALIFICATION, props["ci_qualification"]["const"])


if __name__ == "__main__":
    unittest.main()
