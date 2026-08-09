import copy
import json
import math
import unittest
from pathlib import Path

from athena_mcp.mythic_connection_packet import (
    HISTORICAL_MAPPING_STATUS,
    MANDATORY_FIREWALLS,
    PACKET_ARTIFACT,
    PACKET_LOSS_STANDING,
    PACKET_STANDING,
    PACKET_VERSION,
    SOURCE_EVIDENCE,
    compile_connection_packet,
    validate_connection_packet,
)
from athena_mcp.semantic_connection_control_v1 import SemanticState


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


def deletion_backed_packet():
    packet = valid_packet()
    packet["feature_basis"] = ["x", "memo"]
    packet["operators"][0]["transforms"]["memo"] = {"op": "DELETE"}
    packet["operators"][0]["typed_loss"] = ["memo"]
    packet["operators"][1]["transforms"]["memo"] = {
        "op": "SET",
        "operand": "restored",
    }
    return packet


class MythicConnectionPacketSemanticFusionTests(unittest.TestCase):
    def assert_hold_code(self, packet, code):
        result = validate_connection_packet(packet)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual(code, result["errors"][0]["code"])
        self.assertIsNone(result["packet_semantic_digest"])
        self.assertIsNone(result["operator_registry_digest"])
        self.assertEqual(SOURCE_EVIDENCE, result["source_evidence"])

    def test_valid_reversible_packet_passes_and_digests_are_stable(self):
        first = validate_connection_packet(valid_packet())
        second = validate_connection_packet(valid_packet())
        self.assertEqual("VALID", first["status"])
        self.assertEqual(
            first["packet_semantic_digest"], second["packet_semantic_digest"]
        )
        self.assertEqual(
            first["operator_registry_digest"], second["operator_registry_digest"]
        )
        self.assertEqual(64, len(first["packet_semantic_digest"]))
        self.assertEqual(64, len(first["operator_registry_digest"]))
        self.assertEqual(SOURCE_EVIDENCE, first["source_evidence"])
        self.assertEqual(
            "EXTERNAL_BINDING_REQUIRED", first["implementation_witness"]
        )

    def test_recursive_oracle_fields_are_rejected(self):
        for key in (
            "expected_class",
            "expected",
            "answer_key",
            "oracle",
            "benchmark_label",
        ):
            packet = valid_packet()
            packet["operators"][0]["transforms"]["x"]["metadata"] = {
                key: "FORBIDDEN"
            }
            self.assert_hold_code(packet, "RESERVED_ORACLE_FIELD")

    def test_historical_mapping_must_remain_empty_hold(self):
        packet = valid_packet()
        packet["historical_mapping"]["edges"] = [
            {"source": "historical", "target": "synthetic"}
        ]
        self.assert_hold_code(packet, "HISTORICAL_MAPPING_MUST_BE_EMPTY")

        packet = valid_packet()
        packet["historical_mapping"]["status"] = "SOURCE_VERIFIED"
        self.assert_hold_code(packet, "HISTORICAL_MAPPING_STATUS_INVALID")

    def test_phantom_typed_loss_declaration_is_rejected(self):
        packet = valid_packet()
        packet["operators"][0]["typed_loss"] = ["x"]
        self.assert_hold_code(packet, "UNEXECUTED_TYPED_LOSS_DECLARATION")

    def test_delete_without_matching_typed_loss_is_rejected(self):
        packet = valid_packet()
        packet["operators"][0]["transforms"]["x"] = {"op": "DELETE"}
        packet["operators"][0]["typed_loss"] = []
        self.assert_hold_code(packet, "UNTYPED_DELETE_DECLARATION")

    def test_delete_with_matching_typed_loss_is_valid(self):
        result = validate_connection_packet(deletion_backed_packet())
        self.assertEqual("VALID", result["status"])
        by_id = {
            row["edge_id"]: row
            for row in result["canonical_semantics"]["operators"]
        }
        self.assertEqual(["memo"], by_id["FWD"]["typed_loss"])
        self.assertEqual("DELETE", by_id["FWD"]["transforms"]["memo"]["op"])
        self.assertEqual([], by_id["BACK"]["typed_loss"])

    def test_delete_operand_is_forbidden(self):
        packet = deletion_backed_packet()
        packet["operators"][0]["transforms"]["memo"]["operand"] = "fake"
        self.assert_hold_code(packet, "DELETE_OPERAND_FORBIDDEN")

    def test_scale_is_numeric_and_nonfinite_is_rejected(self):
        packet = valid_packet()
        packet["operators"][0]["transforms"]["x"] = {
            "op": "SCALE",
            "operand": 2,
        }
        packet["operators"][1]["transforms"]["x"] = {
            "op": "SCALE",
            "operand": 0.5,
        }
        self.assertEqual("VALID", validate_connection_packet(packet)["status"])

        for value in (math.nan, math.inf, -math.inf):
            packet = valid_packet()
            packet["operators"][0]["transforms"]["x"] = {
                "op": "SCALE",
                "operand": value,
            }
            self.assert_hold_code(packet, "NONFINITE_JSON_NUMBER")

    def test_legacy_mul_is_not_silently_reinterpreted(self):
        packet = valid_packet()
        packet["operators"][0]["transforms"]["x"] = {
            "op": "MUL",
            "operand": 2,
        }
        self.assert_hold_code(packet, "UNSUPPORTED_TRANSFORM")

    def test_operator_order_is_declaration_digest_invariant(self):
        a = valid_packet()
        b = valid_packet()
        b["operators"].reverse()
        ra = validate_connection_packet(a)
        rb = validate_connection_packet(b)
        self.assertEqual(ra["packet_semantic_digest"], rb["packet_semantic_digest"])
        self.assertEqual(ra["operator_registry_digest"], rb["operator_registry_digest"])

    def test_packet_firewall_change_does_not_change_registry_digest(self):
        a = valid_packet()
        b = valid_packet()
        b["firewalls"].append("CUSTOM_AUDIT_FIREWALL")
        ra = validate_connection_packet(a)
        rb = validate_connection_packet(b)
        self.assertNotEqual(ra["packet_semantic_digest"], rb["packet_semantic_digest"])
        self.assertEqual(ra["operator_registry_digest"], rb["operator_registry_digest"])

    def test_operator_semantic_change_changes_both_digests(self):
        a = valid_packet()
        b = valid_packet()
        b["operators"][0]["transforms"]["x"]["operand"] = 2
        ra = validate_connection_packet(a)
        rb = validate_connection_packet(b)
        self.assertNotEqual(ra["packet_semantic_digest"], rb["packet_semantic_digest"])
        self.assertNotEqual(ra["operator_registry_digest"], rb["operator_registry_digest"])

    def test_caller_digest_mismatch_is_rejected(self):
        packet = valid_packet()
        packet["packet_semantic_digest"] = "0" * 64
        self.assert_hold_code(packet, "PACKET_SEMANTIC_DIGEST_MISMATCH")

        packet = valid_packet()
        packet["operator_registry_digest"] = "0" * 64
        self.assert_hold_code(packet, "OPERATOR_REGISTRY_DIGEST_MISMATCH")

    def test_invalid_inverse_metadata_is_rejected(self):
        packet = valid_packet()
        packet["operators"][1]["inverse_edge_id"] = None
        self.assert_hold_code(packet, "INVERSE_NOT_MUTUAL")

        packet = valid_packet()
        packet["operators"][1]["source_coordinate"] = "C"
        self.assert_hold_code(packet, "INVERSE_COORDINATE_MISMATCH")

    def test_reversible_runtime_roundtrip_is_zero(self):
        receipt, compiled = compile_connection_packet(valid_packet())
        self.assertEqual("VALID", receipt["status"])
        self.assertTrue(receipt["runtime_translation"]["deletion_backed_typed_loss"])
        self.assertTrue(receipt["runtime_translation"]["phantom_loss_rejected"])
        result = compiled.evaluate_closed_loop(
            SemanticState("A", {"x": 5}, feature_basis=("x",)),
            ["FWD", "BACK"],
        )
        self.assertEqual("DEFINED", result["standing"])
        self.assertEqual("ZERO_RESIDUE", result["classification"])
        self.assertTrue(result["residue_zero"])
        self.assertEqual({}, result["residue"])

    def test_deletion_backed_loss_remains_nonzero_after_visible_restore(self):
        receipt, compiled = compile_connection_packet(deletion_backed_packet())
        self.assertEqual("VALID", receipt["status"])
        result = compiled.evaluate_closed_loop(
            SemanticState(
                "A",
                {"x": 5, "memo": "restored"},
                feature_basis=("x", "memo"),
            ),
            ["FWD", "BACK"],
        )
        self.assertEqual("DEFINED", result["standing"])
        self.assertEqual("NONZERO_RESIDUE", result["classification"])
        self.assertFalse(result["residue_zero"])
        self.assertIn("__irreversible_loss__", result["residue"])
        self.assertEqual("restored", result["final_state"]["values"]["memo"])

    def test_provenance_is_audit_only_not_semantic_residue(self):
        packet = valid_packet()
        packet["operators"][0]["provenance"] = ["TRACE:ONE", "TRACE:TWO"]
        receipt, compiled = compile_connection_packet(packet)
        self.assertEqual("VALID", receipt["status"])
        result = compiled.evaluate_closed_loop(
            SemanticState("A", {"x": 9}, feature_basis=("x",)),
            ["FWD", "BACK"],
        )
        self.assertEqual("ZERO_RESIDUE", result["classification"])
        self.assertTrue(result["audit"]["provenance_excluded_from_residue"])
        self.assertGreater(len(result["final_state"]["provenance"]), 0)

    def test_initial_basis_mismatch_is_unknown(self):
        receipt, compiled = compile_connection_packet(valid_packet())
        self.assertEqual("VALID", receipt["status"])
        result = compiled.evaluate_closed_loop(
            SemanticState(
                "A",
                {"x": 1, "y": 2},
                feature_basis=("x", "y"),
            ),
            ["FWD", "BACK"],
        )
        self.assertEqual("UNKNOWN", result["standing"])
        self.assertEqual("INITIAL_STATE_FEATURE_BASIS_MISMATCH", result["reason"])
        self.assertIsNone(result["residue"])

    def test_schema_freezes_identity_transform_vocabulary_and_empty_history(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "schemas"
            / "mck_connection_operator_packet_v1.schema.json"
        )
        schema = json.loads(path.read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(PACKET_ARTIFACT, props["artifact"]["const"])
        self.assertEqual(PACKET_VERSION, props["version"]["const"])
        self.assertEqual(PACKET_STANDING, props["standing"]["const"])
        op_enum = (
            props["operators"]["items"]["properties"]["transforms"]
            ["additionalProperties"]["properties"]["op"]["enum"]
        )
        self.assertEqual({"IDENTITY", "SET", "ADD", "SCALE", "DELETE"}, set(op_enum))
        hist = props["historical_mapping"]["properties"]
        self.assertEqual(HISTORICAL_MAPPING_STATUS, hist["status"]["const"])
        self.assertEqual(0, hist["edges"]["maxItems"])


if __name__ == "__main__":
    unittest.main()
