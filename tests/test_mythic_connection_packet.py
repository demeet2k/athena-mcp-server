import copy
import json
import math
import unittest
from pathlib import Path

from athena_mcp.mythic_connection_packet import (
    HISTORICAL_MAPPING_STATUS,
    PACKET_ARTIFACT,
    PACKET_LOSS_STANDING,
    PACKET_STANDING,
    PACKET_VERSION,
    SOURCE_EVIDENCE,
    compile_connection_packet,
    validate_connection_packet,
)
from athena_mcp.mythic_connection_control import CONTROL_STANDING, TransportState


FIREWALLS = [
    "EXPECTED_CLASS != CONNECTION_DEFINITION",
    "SYNTHETIC_CONTROL_PACKET != HISTORICAL_SOURCE_EVIDENCE",
    "PACKET_DIGEST != INTERPRETER_IMPLEMENTATION_WITNESS",
]


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
        "historical_mapping": {"status": HISTORICAL_MAPPING_STATUS, "edges": []},
        "firewalls": list(FIREWALLS),
    }


class MythicConnectionPacketTests(unittest.TestCase):
    def assert_hold_code(self, packet, code):
        result = validate_connection_packet(packet)
        self.assertEqual("HOLD", result["status"])
        self.assertEqual(code, result["errors"][0]["code"])
        self.assertIsNone(result["packet_semantic_digest"])
        self.assertEqual(SOURCE_EVIDENCE, result["source_evidence"])

    def test_valid_synthetic_packet_passes_and_digest_is_stable(self):
        first = validate_connection_packet(valid_packet())
        second = validate_connection_packet(valid_packet())
        self.assertEqual("VALID", first["status"])
        self.assertEqual(first["packet_semantic_digest"], second["packet_semantic_digest"])
        self.assertEqual(64, len(first["packet_semantic_digest"]))
        self.assertEqual(SOURCE_EVIDENCE, first["source_evidence"])
        self.assertEqual("EXTERNAL_BINDING_REQUIRED", first["implementation_witness"])

    def test_recursive_expected_class_injection_is_rejected(self):
        packet = valid_packet()
        packet["operators"][0]["transforms"]["x"]["metadata"] = {"expected_class": "NONZERO"}
        self.assert_hold_code(packet, "RESERVED_ORACLE_FIELD")

    def test_recursive_oracle_injection_is_rejected_before_shape_validation(self):
        packet = valid_packet()
        packet["operators"][0]["oracle"] = {"deep": True}
        self.assert_hold_code(packet, "RESERVED_ORACLE_FIELD")

    def test_recursive_answer_key_injection_is_rejected(self):
        packet = valid_packet()
        packet["historical_mapping"]["answer_key"] = 1
        self.assert_hold_code(packet, "RESERVED_ORACLE_FIELD")

    def test_unknown_top_level_field_is_rejected(self):
        packet = valid_packet()
        packet["notes"] = "not part of the semantic packet contract"
        self.assert_hold_code(packet, "UNKNOWN_PACKET_FIELD")

    def test_lowercase_transform_op_is_rejected_to_match_schema(self):
        packet = valid_packet()
        packet["operators"][0]["transforms"]["x"]["op"] = "add"
        self.assert_hold_code(packet, "UNSUPPORTED_TRANSFORM")

    def test_nonempty_historical_mapping_is_rejected(self):
        packet = valid_packet()
        packet["historical_mapping"]["edges"] = [{"source": "Yijing", "target": "synthetic"}]
        self.assert_hold_code(packet, "HISTORICAL_MAPPING_MUST_BE_EMPTY")

    def test_wrong_historical_mapping_status_is_rejected(self):
        packet = valid_packet()
        packet["historical_mapping"]["status"] = "SOURCE_VERIFIED"
        self.assert_hold_code(packet, "HISTORICAL_MAPPING_STATUS_INVALID")

    def test_duplicate_feature_id_is_rejected(self):
        packet = valid_packet()
        packet["feature_basis"] = ["x", "x"]
        self.assert_hold_code(packet, "DUPLICATE_FEATURE_ID")

    def test_duplicate_edge_id_is_rejected(self):
        packet = valid_packet()
        packet["operators"][1]["edge_id"] = "FWD"
        self.assert_hold_code(packet, "DUPLICATE_EDGE_ID")

    def test_transform_feature_outside_basis_is_rejected(self):
        packet = valid_packet()
        packet["operators"][0]["transforms"] = {"y": {"op": "ADD", "operand": 1}}
        self.assert_hold_code(packet, "TRANSFORM_FEATURE_OUTSIDE_BASIS")

    def test_loss_feature_outside_basis_is_rejected(self):
        packet = valid_packet()
        packet["operators"][0]["typed_loss"] = ["y"]
        self.assert_hold_code(packet, "LOSS_FEATURE_OUTSIDE_BASIS")

    def test_nonfinite_transform_operand_is_rejected(self):
        for value in (math.nan, math.inf, -math.inf):
            packet = valid_packet()
            packet["operators"][0]["transforms"]["x"]["operand"] = value
            self.assert_hold_code(packet, "NONFINITE_JSON_NUMBER")

    def test_untyped_or_unknown_loss_cannot_masquerade_as_typed(self):
        packet = valid_packet()
        packet["operators"][0]["loss_standing"] = "UNTYPED_PROSE_ONLY"
        self.assert_hold_code(packet, "INVALID_LOSS_STANDING")

        packet = valid_packet()
        packet["operators"][0]["typed_loss"] = None
        self.assert_hold_code(packet, "TYPED_LOSS")

    def test_invalid_inverse_metadata_is_rejected(self):
        packet = valid_packet()
        packet["operators"][1]["inverse_edge_id"] = None
        self.assert_hold_code(packet, "INVERSE_NOT_MUTUAL")

        packet = valid_packet()
        packet["operators"][1]["source_coordinate"] = "C"
        self.assert_hold_code(packet, "INVERSE_COORDINATE_MISMATCH")

    def test_caller_digest_mismatch_is_rejected(self):
        packet = valid_packet()
        packet["packet_semantic_digest"] = "0" * 64
        self.assert_hold_code(packet, "PACKET_SEMANTIC_DIGEST_MISMATCH")

    def test_operator_order_does_not_change_semantic_digest(self):
        a = valid_packet()
        b = valid_packet()
        b["operators"].reverse()
        self.assertEqual(
            validate_connection_packet(a)["packet_semantic_digest"],
            validate_connection_packet(b)["packet_semantic_digest"],
        )

    def test_feature_and_firewall_order_do_not_change_semantic_digest(self):
        a = valid_packet()
        a["feature_basis"] = ["x", "y"]
        for op in a["operators"]:
            op["transforms"]["y"] = {"op": "IDENTITY"}
        b = copy.deepcopy(a)
        b["feature_basis"].reverse()
        b["firewalls"].reverse()
        self.assertEqual(
            validate_connection_packet(a)["packet_semantic_digest"],
            validate_connection_packet(b)["packet_semantic_digest"],
        )

    def test_semantic_operator_change_changes_digest(self):
        a = valid_packet()
        b = valid_packet()
        b["operators"][0]["transforms"]["x"]["operand"] = 2
        self.assertNotEqual(
            validate_connection_packet(a)["packet_semantic_digest"],
            validate_connection_packet(b)["packet_semantic_digest"],
        )

    def test_provenance_order_is_semantic_and_changes_digest(self):
        a = valid_packet()
        a["operators"][0]["provenance"] = ["SYNTHETIC:ONE", "SYNTHETIC:TWO"]
        b = copy.deepcopy(a)
        b["operators"][0]["provenance"].reverse()
        self.assertNotEqual(
            validate_connection_packet(a)["packet_semantic_digest"],
            validate_connection_packet(b)["packet_semantic_digest"],
        )

    def test_translation_preserves_synthetic_source_boundary(self):
        receipt, runtime = compile_connection_packet(valid_packet())
        self.assertEqual("VALID", receipt["status"])
        self.assertIsNotNone(runtime)
        self.assertEqual(CONTROL_STANDING, receipt["runtime_translation"]["control_standing"])
        self.assertEqual(SOURCE_EVIDENCE, receipt["runtime_translation"]["source_evidence"])
        self.assertFalse(receipt["runtime_translation"]["historical_mapping_applied"])
        self.assertFalse(receipt["runtime_translation"]["public_mcp_registration"])
        for edge in runtime.operators.values():
            self.assertEqual(CONTROL_STANDING, edge.standing)

    def test_compiled_runtime_replays_reversible_roundtrip_without_oracle(self):
        receipt, runtime = compile_connection_packet(valid_packet())
        self.assertEqual("VALID", receipt["status"])
        result = runtime.evaluate_closed_loop(TransportState("A", {"x": 5}), ["FWD", "BACK"])
        self.assertEqual("DEFINED", result["status"])
        self.assertFalse(result["closed_loop_residue_nonzero"])
        self.assertFalse(result["expected_class_used"])
        self.assertEqual("NONE_SYNTHETIC_CONTROL", result["source_evidence"])

    def test_schema_freezes_core_identity_and_empty_historical_mapping(self):
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "mck_connection_operator_packet_v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(PACKET_ARTIFACT, props["artifact"]["const"])
        self.assertEqual(PACKET_VERSION, props["version"]["const"])
        self.assertEqual(PACKET_STANDING, props["standing"]["const"])
        self.assertEqual(HISTORICAL_MAPPING_STATUS, props["historical_mapping"]["properties"]["status"]["const"])
        self.assertEqual(0, props["historical_mapping"]["properties"]["edges"]["maxItems"])


if __name__ == "__main__":
    unittest.main()
