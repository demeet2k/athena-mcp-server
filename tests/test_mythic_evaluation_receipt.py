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
)
from athena_mcp.mythic_evaluation_receipt import (
    HOLD_STANDING,
    RECEIPT_ARTIFACT,
    RECEIPT_STANDING,
    RECEIPT_VERSION,
    REPLAY_STANDING,
    create_evaluation_receipt,
    replay_evaluation_receipt,
)


FIREWALLS = [
    "EXPECTED_CLASS != CONNECTION_DEFINITION",
    "SYNTHETIC_CONTROL_PACKET != HISTORICAL_SOURCE_EVIDENCE",
    "PACKET_DIGEST != INTERPRETER_IMPLEMENTATION_WITNESS",
]


def packet():
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


def state(x=5):
    return {
        "coordinate": "A",
        "values": {"x": x},
        "irreversible_loss": [],
        "provenance": ["SYNTHETIC:INITIAL"],
    }


class MythicEvaluationReceiptTests(unittest.TestCase):
    def test_same_inputs_produce_byte_stable_execution_identity(self):
        a = create_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        b = create_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        self.assertEqual("EVALUATED", a["status"])
        self.assertEqual(a, b)
        self.assertEqual(64, len(a["evaluation_receipt_digest"]))
        self.assertEqual(RECEIPT_STANDING, a["standing"])
        self.assertFalse(a["raw_result"]["closed_loop_residue_nonzero"])

    def test_initial_state_change_splits_state_and_receipt_digest(self):
        a = create_evaluation_receipt(packet(), state(5), ["FWD", "BACK"])
        b = create_evaluation_receipt(packet(), state(6), ["FWD", "BACK"])
        self.assertNotEqual(a["initial_state_digest"], b["initial_state_digest"])
        self.assertNotEqual(a["evaluation_receipt_digest"], b["evaluation_receipt_digest"])

    def test_ordered_path_change_splits_path_and_receipt_digest(self):
        a = create_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        b = create_evaluation_receipt(packet(), state(), ["FWD", "BACK", "FWD", "BACK"])
        self.assertEqual("DEFINED", a["raw_result"]["status"])
        self.assertEqual("DEFINED", b["raw_result"]["status"])
        self.assertNotEqual(a["ordered_path_digest"], b["ordered_path_digest"])
        self.assertNotEqual(a["result_semantic_digest"], b["result_semantic_digest"])
        self.assertNotEqual(a["evaluation_receipt_digest"], b["evaluation_receipt_digest"])

    def test_packet_operator_order_is_semantically_invariant(self):
        a_packet = packet()
        b_packet = packet()
        b_packet["operators"].reverse()
        a = create_evaluation_receipt(a_packet, state(), ["FWD", "BACK"])
        b = create_evaluation_receipt(b_packet, state(), ["FWD", "BACK"])
        self.assertEqual(a["packet_semantic_digest"], b["packet_semantic_digest"])
        self.assertEqual(a["operator_registry_digest"], b["operator_registry_digest"])
        self.assertEqual(a["evaluation_receipt_digest"], b["evaluation_receipt_digest"])

    def test_input_mutation_after_execution_cannot_change_stored_receipt(self):
        source_packet = packet()
        source_state = state()
        source_path = ["FWD", "BACK"]
        receipt = create_evaluation_receipt(source_packet, source_state, source_path)
        frozen = copy.deepcopy(receipt)

        source_packet["operators"][0]["transforms"]["x"]["operand"] = 999
        source_state["values"]["x"] = 999
        source_state["provenance"].append("MUTATED")
        source_path.append("FWD")

        self.assertEqual(frozen, receipt)
        self.assertEqual(5, receipt["initial_state"]["values"]["x"])
        self.assertEqual(["FWD", "BACK"], receipt["ordered_path"])

    def test_valid_packet_can_receipt_raw_unknown_without_inventing_residue(self):
        a = create_evaluation_receipt(packet(), state(), ["MISSING"])
        b = create_evaluation_receipt(packet(), state(), ["MISSING"])
        self.assertEqual("EVALUATED", a["status"])
        self.assertEqual("UNKNOWN", a["raw_result"]["status"])
        self.assertIsNone(a["raw_result"]["closed_loop_residue"])
        self.assertEqual(a["evaluation_receipt_digest"], b["evaluation_receipt_digest"])

    def test_invalid_packet_holds_without_execution_identity(self):
        bad = packet()
        bad["historical_mapping"]["edges"] = [{"source": "history", "target": "synthetic"}]
        result = create_evaluation_receipt(bad, state(), ["FWD", "BACK"])
        self.assertEqual("HOLD", result["status"])
        self.assertEqual(HOLD_STANDING, result["standing"])
        self.assertIsNone(result["evaluation_receipt_digest"])
        self.assertEqual("INVALID_CONNECTION_PACKET", result["errors"][0]["code"])

    def test_nonfinite_state_holds_before_runtime_execution(self):
        for value in (math.nan, math.inf, -math.inf):
            bad_state = state(value)
            result = create_evaluation_receipt(packet(), bad_state, ["FWD", "BACK"])
            self.assertEqual("HOLD", result["status"])
            self.assertEqual("NONFINITE_JSON_NUMBER", result["errors"][0]["code"])

    def test_caller_cannot_self_mint_ci_authority_or_source_verification(self):
        for claims in (
            {"ci_status": "success"},
            {"authority": "CANONICAL"},
            {"source_verified": True},
            {"implementation_verified": True, "ci_run_id": 123},
        ):
            result = create_evaluation_receipt(
                packet(), state(), ["FWD", "BACK"], caller_claims=claims
            )
            self.assertEqual("HOLD", result["status"])
            self.assertEqual("UNTRUSTED_IMPLEMENTATION_CLAIM", result["errors"][0]["code"])
            self.assertIsNone(result["evaluation_receipt_digest"])

    def test_implementation_binding_is_explicitly_empty_external_requirement(self):
        receipt = create_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        binding = receipt["implementation_binding"]
        self.assertEqual("EXTERNAL_BINDING_REQUIRED", binding["standing"])
        for key in ("repository", "git_head", "ci_workflow", "ci_run_id", "ci_run_number", "ci_conclusion"):
            self.assertIsNone(binding[key])
        self.assertEqual("NONE_SYNTHETIC_CONTROL", receipt["source_evidence"])
        self.assertFalse(receipt["expected_class_used"])

    def test_exact_replay_matches_all_execution_digests_and_raw_result(self):
        receipt = create_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        replay = replay_evaluation_receipt(packet(), receipt)
        self.assertEqual("REPLAY_MATCH", replay["status"])
        self.assertEqual(REPLAY_STANDING, replay["standing"])
        self.assertTrue(all(replay["checks"].values()))
        self.assertEqual(receipt["evaluation_receipt_digest"], replay["evaluation_receipt_digest"])
        self.assertEqual("NONE_SYNTHETIC_CONTROL", replay["source_evidence"])
        self.assertEqual("NONE", replay["authority_delta"])

    def test_changed_packet_cannot_replay_old_receipt(self):
        receipt = create_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        changed = packet()
        changed["firewalls"].append("SYNTHETIC:CHANGED_WRAPPER")
        replay = replay_evaluation_receipt(changed, receipt)
        self.assertEqual("HOLD", replay["status"])
        self.assertEqual("REPLAY_PACKET_SEMANTIC_DIGEST_MISMATCH", replay["errors"][0]["code"])

    def test_tampered_receipt_fails_self_digest_before_replay(self):
        receipt = create_evaluation_receipt(packet(), state(), ["FWD", "BACK"])
        receipt["raw_result"]["source_evidence"] = "FORGED_SOURCE"
        replay = replay_evaluation_receipt(packet(), receipt)
        self.assertEqual("HOLD", replay["status"])
        self.assertEqual("EVALUATION_RECEIPT_SELF_DIGEST_MISMATCH", replay["errors"][0]["code"])

    def test_receipt_schema_freezes_non_witness_standing_and_null_binding(self):
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "mck_connection_evaluation_receipt_v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(RECEIPT_ARTIFACT, props["artifact"]["const"])
        self.assertEqual(RECEIPT_VERSION, props["version"]["const"])
        self.assertEqual(RECEIPT_STANDING, props["standing"]["const"])
        binding = props["implementation_binding"]["properties"]
        self.assertEqual("EXTERNAL_BINDING_REQUIRED", binding["standing"]["const"])
        self.assertEqual("null", binding["git_head"]["type"])
        self.assertEqual("null", binding["ci_run_id"]["type"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
