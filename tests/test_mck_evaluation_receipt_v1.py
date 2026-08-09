from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from athena_mcp.mck_evaluation_receipt_v1 import (
    ARTIFACT,
    AUTHORITY_DELTA,
    CI_QUALIFICATION,
    EMPTY_IMPLEMENTATION_BINDING,
    EVIDENCE_STANDING,
    HISTORICAL_MAPPING,
    INDEPENDENT_WITNESS,
    RECEIPT_STANDING,
    REPLAY_ARTIFACT,
    SEMANTIC_RESULT_PROJECTION_BASIS,
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
        "historical_mapping": {"status": HISTORICAL_MAPPING_STATUS, "edges": []},
        "firewalls": sorted(MANDATORY_FIREWALLS),
    }


def deletion_packet():
    packet = reversible_packet()
    packet["feature_basis"] = ["x", "memo"]
    packet["operators"][0]["transforms"]["memo"] = {"op": "DELETE"}
    packet["operators"][0]["typed_loss"] = ["memo"]
    packet["operators"][1]["transforms"]["memo"] = {"op": "SET", "operand": "restored"}
    return packet


def initial_state(x=5, *, provenance=("SEED",)):
    return SemanticState("A", {"x": x}, feature_basis=("x",), provenance=provenance)


def deletion_state(*, provenance=("SEED",)):
    return SemanticState(
        "A",
        {"x": 5, "memo": "restored"},
        feature_basis=("x", "memo"),
        provenance=provenance,
    )


class MckEvaluationReceiptV1Tests(unittest.TestCase):
    def test_same_input_produces_identical_receipt(self):
        first = build_evaluation_receipt(reversible_packet(), initial_state(), ["FWD", "BACK"])
        second = build_evaluation_receipt(reversible_packet(), initial_state(), ["FWD", "BACK"])
        self.assertEqual(first, second)
        self.assertEqual("RECORDED", first["status"])
        self.assertEqual(ARTIFACT, first["artifact"])
        self.assertEqual(VERSION, first["version"])
        self.assertEqual(RECEIPT_STANDING, first["receipt_standing"])
        self.assertEqual(EVIDENCE_STANDING, first["evidence_standing"])
        self.assertEqual(SOURCE_EVIDENCE, first["source_evidence"])
        self.assertEqual(HISTORICAL_MAPPING, first["historical_mapping"])
        self.assertEqual(INDEPENDENT_WITNESS, first["independent_witness"])
        self.assertEqual(AUTHORITY_DELTA, first["authority_delta"])
        self.assertEqual(CI_QUALIFICATION, first["ci_qualification"])
        self.assertEqual(EMPTY_IMPLEMENTATION_BINDING, first["implementation_binding"])
        self.assertEqual(SEMANTIC_RESULT_PROJECTION_BASIS, first["semantic_result_projection_basis"])
        for field in (
            "packet_semantic_digest",
            "operator_registry_digest",
            "evaluation_input_digest",
            "raw_result_digest",
            "semantic_result_digest",
            "receipt_digest",
        ):
            self.assertEqual(64, len(first[field]))

    def test_recorded_receipt_validates(self):
        receipt = build_evaluation_receipt(reversible_packet(), initial_state(), ["FWD", "BACK"])
        validation = validate_evaluation_receipt(receipt)
        self.assertEqual("VALID", validation["status"])
        self.assertEqual(receipt["receipt_id"], validation["receipt_id"])

    def test_provenance_only_change_splits_audit_but_not_semantic_identity(self):
        a = build_evaluation_receipt(
            reversible_packet(), initial_state(provenance=("TRACE:A",)), ["FWD", "BACK"]
        )
        b = build_evaluation_receipt(
            reversible_packet(), initial_state(provenance=("TRACE:B",)), ["FWD", "BACK"]
        )
        self.assertNotEqual(a["evaluation_input_digest"], b["evaluation_input_digest"])
        self.assertNotEqual(a["raw_result_digest"], b["raw_result_digest"])
        self.assertEqual(a["semantic_result"], b["semantic_result"])
        self.assertEqual(a["semantic_result_digest"], b["semantic_result_digest"])
        self.assertNotEqual(a["receipt_digest"], b["receipt_digest"])

    def test_longer_same_semantic_loop_splits_path_audit_not_semantics(self):
        short = build_evaluation_receipt(reversible_packet(), initial_state(), ["FWD", "BACK"])
        long = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", "BACK", "FWD", "BACK"]
        )
        self.assertEqual("ZERO_RESIDUE", short["raw_result"]["classification"])
        self.assertEqual("ZERO_RESIDUE", long["raw_result"]["classification"])
        self.assertNotEqual(short["evaluation_input_digest"], long["evaluation_input_digest"])
        self.assertNotEqual(short["raw_result_digest"], long["raw_result_digest"])
        self.assertEqual(short["semantic_result_digest"], long["semantic_result_digest"])
        self.assertNotEqual(short["receipt_digest"], long["receipt_digest"])

    def test_deletion_backed_loss_is_semantic_and_replay_bound(self):
        receipt = build_evaluation_receipt(deletion_packet(), deletion_state(), ["FWD", "BACK"])
        self.assertEqual("RECORDED", receipt["status"])
        self.assertEqual("NONZERO_RESIDUE", receipt["raw_result"]["classification"])
        self.assertIn("__irreversible_loss__", receipt["raw_result"]["residue"])
        self.assertEqual("NONZERO_RESIDUE", receipt["semantic_result"]["classification"])
        replay = replay_evaluation_receipt(
            receipt, deletion_packet(), deletion_state(), ["FWD", "BACK"]
        )
        self.assertEqual("MATCH", replay["status"])

    def test_operator_declaration_order_is_full_receipt_invariant(self):
        a = reversible_packet()
        b = reversible_packet()
        b["operators"].reverse()
        first = build_evaluation_receipt(a, initial_state(), ["FWD", "BACK"])
        second = build_evaluation_receipt(b, initial_state(), ["FWD", "BACK"])
        self.assertEqual(first, second)

    def test_packet_wrapper_change_splits_packet_not_runtime_semantics(self):
        a = reversible_packet()
        b = reversible_packet()
        b["firewalls"].append("CUSTOM_AUDIT_FIREWALL")
        first = build_evaluation_receipt(a, initial_state(), ["FWD", "BACK"])
        second = build_evaluation_receipt(b, initial_state(), ["FWD", "BACK"])
        self.assertNotEqual(first["packet_semantic_digest"], second["packet_semantic_digest"])
        self.assertEqual(first["operator_registry_digest"], second["operator_registry_digest"])
        self.assertEqual(first["raw_result_digest"], second["raw_result_digest"])
        self.assertEqual(first["semantic_result_digest"], second["semantic_result_digest"])
        self.assertNotEqual(first["receipt_digest"], second["receipt_digest"])

    def test_semantic_state_change_splits_semantic_identity(self):
        a = build_evaluation_receipt(reversible_packet(), initial_state(5), ["FWD", "BACK"])
        b = build_evaluation_receipt(reversible_packet(), initial_state(6), ["FWD", "BACK"])
        self.assertNotEqual(a["evaluation_input_digest"], b["evaluation_input_digest"])
        self.assertNotEqual(a["semantic_result_digest"], b["semantic_result_digest"])
        self.assertNotEqual(a["receipt_digest"], b["receipt_digest"])

    def test_operator_semantic_change_splits_declaration_and_result(self):
        a = reversible_packet()
        b = reversible_packet()
        b["operators"][0]["transforms"]["x"]["operand"] = 2
        first = build_evaluation_receipt(a, initial_state(), ["FWD", "BACK"])
        second = build_evaluation_receipt(b, initial_state(), ["FWD", "BACK"])
        self.assertNotEqual(first["operator_registry_digest"], second["operator_registry_digest"])
        self.assertNotEqual(first["semantic_result_digest"], second["semantic_result_digest"])
        self.assertNotEqual(first["receipt_digest"], second["receipt_digest"])

    def test_invalid_packet_hold_has_no_execution_identity(self):
        packet = reversible_packet()
        packet["expected_class"] = "ZERO_RESIDUE"
        receipt = build_evaluation_receipt(packet, initial_state(), ["FWD", "BACK"])
        self.assertEqual("HOLD", receipt["status"])
        self.assertEqual("PACKET_VALIDATION_HOLD", receipt["reason"])
        self.assertIsNone(receipt["receipt_id"])
        self.assertIsNone(receipt["execution_identity"])

    def test_unknown_execution_is_recorded_without_invented_residue(self):
        receipt = build_evaluation_receipt(reversible_packet(), initial_state(), ["MISSING_EDGE"])
        self.assertEqual("RECORDED", receipt["status"])
        self.assertEqual("UNKNOWN", receipt["raw_result"]["standing"])
        self.assertEqual("UNKNOWN_RESIDUE", receipt["raw_result"]["classification"])
        self.assertIsNone(receipt["raw_result"]["residue"])
        self.assertIsNone(receipt["semantic_result"]["residue"])

    def test_empty_path_holds_before_execution_identity(self):
        receipt = build_evaluation_receipt(reversible_packet(), initial_state(), [])
        self.assertEqual("HOLD", receipt["status"])
        self.assertTrue(receipt["reason"].startswith("INVALID_EVALUATION_INPUT"))
        self.assertIsNone(receipt["receipt_id"])

    def test_initial_non_synthetic_standing_holds(self):
        state = SemanticState("A", {"x": 5}, feature_basis=("x",), standing="PRIMARY_EVIDENCE")
        receipt = build_evaluation_receipt(reversible_packet(), state, ["FWD", "BACK"])
        self.assertEqual("HOLD", receipt["status"])
        self.assertEqual("INITIAL_STATE_STANDING_MUST_BE_SYNTHETIC_CONTROL", receipt["reason"])

    def test_reserved_caller_trust_claims_cannot_self_mint_standing(self):
        claims = [
            {"ci_status": "PASS"},
            {"nested": {"authority": "ROOT"}},
            {"nested": [{"source_verified": True}]},
            {"nested": [{"independent_witness": True}]},
            {"nested": [{"oracle": "PASS"}]},
            {"promotion": "QUALIFIED"},
        ]
        for caller_claims in claims:
            with self.subTest(caller_claims=caller_claims):
                receipt = build_evaluation_receipt(
                    reversible_packet(), initial_state(), ["FWD", "BACK"], caller_claims=caller_claims
                )
                self.assertEqual("HOLD", receipt["status"])
                self.assertTrue(receipt["reason"].startswith("CALLER_TRUST_CLAIM_FORBIDDEN"))
                self.assertFalse(receipt["independent_witness"])

    def test_even_benign_caller_context_is_not_admitted_v1(self):
        receipt = build_evaluation_receipt(
            reversible_packet(), initial_state(), ["FWD", "BACK"], caller_claims={"note": "hello"}
        )
        self.assertEqual("HOLD", receipt["status"])
        self.assertEqual("CALLER_CONTEXT_NOT_ADMITTED_V1", receipt["reason"])

    def test_source_objects_are_copied_before_persistence(self):
        packet = reversible_packet()
        values = {"x": 5}
        state = SemanticState("A", values, feature_basis=("x",), provenance=("SEED",))
        receipt = build_evaluation_receipt(packet, state, ["FWD", "BACK"])
        frozen = copy.deepcopy(receipt)
        packet["operators"][0]["transforms"]["x"]["operand"] = 999
        values["x"] = 999
        self.assertEqual(frozen, receipt)
        self.assertEqual(5, receipt["initial_state"]["values"]["x"])

    def test_raw_result_tamper_invalidates_receipt(self):
        receipt = build_evaluation_receipt(reversible_packet(), initial_state(), ["FWD", "BACK"])
        tampered = copy.deepcopy(receipt)
        tampered["raw_result"]["classification"] = "FORGED"
        validation = validate_evaluation_receipt(tampered)
        self.assertEqual("HOLD", validation["status"])
        self.assertTrue(any("RAW_RESULT_DIGEST_MISMATCH" in x for x in validation["errors"]))

    def test_semantic_projection_tamper_invalidates_receipt(self):
        receipt = build_evaluation_receipt(reversible_packet(), initial_state(), ["FWD", "BACK"])
        tampered = copy.deepcopy(receipt)
        tampered["semantic_result"]["classification"] = "FORGED"
        validation = validate_evaluation_receipt(tampered)
        self.assertEqual("HOLD", validation["status"])
        self.assertTrue(any("SEMANTIC_RESULT_PROJECTION_MISMATCH" in x for x in validation["errors"]))

    def test_trust_and_implementation_binding_tamper_invalidates(self):
        receipt = build_evaluation_receipt(reversible_packet(), initial_state(), ["FWD", "BACK"])
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
        tampered = copy.deepcopy(receipt)
        tampered["implementation_binding"]["git_head"] = "a" * 40
        self.assertEqual("HOLD", validate_evaluation_receipt(tampered)["status"])

    def test_unknown_top_level_field_is_rejected_even_with_self_digest_unchanged(self):
        receipt = build_evaluation_receipt(reversible_packet(), initial_state(), ["FWD", "BACK"])
        tampered = copy.deepcopy(receipt)
        tampered["authority"] = "CANONICAL"
        self.assertEqual(receipt["receipt_digest"], tampered["receipt_digest"])
        validation = validate_evaluation_receipt(tampered)
        self.assertEqual("HOLD", validation["status"])
        self.assertTrue(any("RECEIPT_SHAPE_MISMATCH" in x for x in validation["errors"]))

    def test_receipt_id_and_digest_tamper_detected(self):
        receipt = build_evaluation_receipt(reversible_packet(), initial_state(), ["FWD", "BACK"])
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

    def test_changed_packet_replay_mismatches(self):
        packet = reversible_packet()
        receipt = build_evaluation_receipt(packet, initial_state(), ["FWD", "BACK"])
        changed = reversible_packet()
        changed["operators"][0]["transforms"]["x"]["operand"] = 2
        replay = replay_evaluation_receipt(receipt, changed, initial_state(), ["FWD", "BACK"])
        self.assertEqual("MISMATCH", replay["status"])
        self.assertIn("packet_semantic_digest", replay["mismatches"])
        self.assertIn("semantic_result_digest", replay["mismatches"])

    def test_changed_initial_state_replay_mismatches(self):
        packet = reversible_packet()
        receipt = build_evaluation_receipt(packet, initial_state(5), ["FWD", "BACK"])
        replay = replay_evaluation_receipt(receipt, packet, initial_state(6), ["FWD", "BACK"])
        self.assertEqual("MISMATCH", replay["status"])
        self.assertIn("evaluation_input_digest", replay["mismatches"])
        self.assertIn("semantic_result_digest", replay["mismatches"])

    def test_changed_provenance_replay_mismatches_audit_not_semantic(self):
        packet = reversible_packet()
        receipt = build_evaluation_receipt(
            packet, initial_state(provenance=("A",)), ["FWD", "BACK"]
        )
        replay = replay_evaluation_receipt(
            receipt, packet, initial_state(provenance=("B",)), ["FWD", "BACK"]
        )
        self.assertEqual("MISMATCH", replay["status"])
        self.assertIn("evaluation_input_digest", replay["mismatches"])
        self.assertIn("raw_result_digest", replay["mismatches"])
        self.assertNotIn("semantic_result_digest", replay["mismatches"])

    def test_changed_path_replay_mismatches(self):
        packet = reversible_packet()
        receipt = build_evaluation_receipt(packet, initial_state(), ["FWD", "BACK"])
        replay = replay_evaluation_receipt(
            receipt, packet, initial_state(), ["FWD", "BACK", "FWD", "BACK"]
        )
        self.assertEqual("MISMATCH", replay["status"])
        self.assertIn("evaluation_input_digest", replay["mismatches"])
        self.assertIn("raw_result_digest", replay["mismatches"])
        self.assertNotIn("semantic_result_digest", replay["mismatches"])

    def test_invalid_stored_receipt_replay_holds(self):
        packet = reversible_packet()
        receipt = build_evaluation_receipt(packet, initial_state(), ["FWD", "BACK"])
        receipt["raw_result_digest"] = "0" * 64
        replay = replay_evaluation_receipt(receipt, packet, initial_state(), ["FWD", "BACK"])
        self.assertEqual("HOLD", replay["status"])
        self.assertEqual("STORED_RECEIPT_INVALID", replay["reason"])

    def test_schema_freezes_non_promotional_semantic_audit_contract(self):
        path = Path(__file__).resolve().parents[1] / "schemas" / "mck_evaluation_receipt_v1.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(ARTIFACT, props["artifact"]["const"])
        self.assertEqual(VERSION, props["version"]["const"])
        self.assertEqual(RECEIPT_STANDING, props["receipt_standing"]["const"])
        self.assertEqual(EVIDENCE_STANDING, props["evidence_standing"]["const"])
        self.assertEqual(SOURCE_EVIDENCE, props["source_evidence"]["const"])
        self.assertEqual(HISTORICAL_MAPPING_STATUS, props["historical_mapping"]["properties"]["status"]["const"])
        self.assertFalse(props["independent_witness"]["const"])
        self.assertEqual(CI_QUALIFICATION, props["ci_qualification"]["const"])
        self.assertEqual(SEMANTIC_RESULT_PROJECTION_BASIS, props["semantic_result_projection_basis"]["const"])
        binding = props["implementation_binding"]["properties"]
        self.assertEqual("EXTERNAL_BINDING_REQUIRED", binding["standing"]["const"])
        self.assertEqual("null", binding["git_head"]["type"])


if __name__ == "__main__":
    unittest.main()
