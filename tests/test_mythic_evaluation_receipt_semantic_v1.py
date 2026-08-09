import copy
import json
import math
import unittest
from pathlib import Path

from athena_mcp.mythic_connection_packet import (
    COMPILER_REVISION,
    HISTORICAL_MAPPING_STATUS,
    MANDATORY_FIREWALLS,
    PACKET_ARTIFACT,
    PACKET_LOSS_STANDING,
    PACKET_STANDING,
    PACKET_VERSION,
    SOURCE_EVIDENCE,
)
from athena_mcp.mythic_evaluation_receipt_semantic_v1 import (
    RECEIPT_ARTIFACT,
    RECEIPT_DIGEST_DOMAIN,
    RECEIPT_REVISION,
    RECEIPT_STANDING,
    RECEIPT_VERSION,
    REPLAY_STANDING,
    SEMANTIC_RESULT_PROJECTION_BASIS,
    _domain_digest,
    create_evaluation_receipt,
    replay_evaluation_receipt,
)
from athena_mcp.semantic_connection_control_v1 import (
    ARTIFACT as SEMANTIC_CONTROL_ARTIFACT,
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


def initial_state(x=5, provenance=None):
    return {
        "coordinate": "A",
        "values": {"x": x},
        "irreversible_loss": [],
        "provenance": list(provenance or ["SYNTHETIC:INITIAL"]),
    }


def deletion_state(provenance=None):
    return {
        "coordinate": "A",
        "values": {"x": 5, "memo": "restored"},
        "irreversible_loss": [],
        "provenance": list(provenance or ["SYNTHETIC:INITIAL"]),
    }


def recompute_self_digest(receipt):
    payload = {
        key: copy.deepcopy(value)
        for key, value in receipt.items()
        if key != "evaluation_receipt_digest"
    }
    return _domain_digest(RECEIPT_DIGEST_DOMAIN, payload)


class MythicEvaluationReceiptSemanticV1Tests(unittest.TestCase):
    def test_reversible_receipt_is_stable_and_zero_semantic_residue(self):
        first = create_evaluation_receipt(
            valid_packet(), initial_state(), ["FWD", "BACK"]
        )
        second = create_evaluation_receipt(
            valid_packet(), initial_state(), ["FWD", "BACK"]
        )
        self.assertEqual("EVALUATED", first["status"])
        self.assertEqual(first, second)
        self.assertEqual(RECEIPT_STANDING, first["standing"])
        self.assertEqual(COMPILER_REVISION, first["packet_compiler_revision"])
        self.assertEqual(SEMANTIC_CONTROL_ARTIFACT, first["semantic_control_artifact"])
        self.assertEqual("DEFINED", first["raw_result"]["standing"])
        self.assertEqual("ZERO_RESIDUE", first["raw_result"]["classification"])
        self.assertTrue(first["raw_result"]["residue_zero"])
        self.assertEqual({}, first["raw_result"]["residue"])
        self.assertEqual("ZERO_RESIDUE", first["semantic_result"]["classification"])
        self.assertNotIn("provenance", first["semantic_result"]["initial_state"])
        self.assertNotIn("audit", first["semantic_result"])
        self.assertNotIn("executed_edges", first["semantic_result"])
        self.assertEqual(64, len(first["evaluation_receipt_digest"]))

    def test_deletion_backed_irreversible_loss_is_receipted_and_replays(self):
        receipt = create_evaluation_receipt(
            deletion_backed_packet(),
            deletion_state(),
            ["FWD", "BACK"],
        )
        self.assertEqual("EVALUATED", receipt["status"])
        raw = receipt["raw_result"]
        self.assertEqual("DEFINED", raw["standing"])
        self.assertEqual("NONZERO_RESIDUE", raw["classification"])
        self.assertFalse(raw["residue_zero"])
        self.assertIn("__irreversible_loss__", raw["residue"])
        self.assertEqual("restored", raw["final_state"]["values"]["memo"])
        self.assertIn("memo", raw["final_state"]["irreversible_loss"])

        semantic = receipt["semantic_result"]
        self.assertEqual("NONZERO_RESIDUE", semantic["classification"])
        self.assertIn("memo", semantic["final_state"]["irreversible_loss"])
        replay = replay_evaluation_receipt(deletion_backed_packet(), receipt)
        self.assertEqual("REPLAY_MATCH", replay["status"])
        self.assertEqual(REPLAY_STANDING, replay["standing"])
        self.assertTrue(all(replay["checks"].values()))

    def test_provenance_only_change_splits_audit_not_semantic_result(self):
        first = create_evaluation_receipt(
            valid_packet(), initial_state(provenance=["TRACE:A"]), ["FWD", "BACK"]
        )
        second = create_evaluation_receipt(
            valid_packet(), initial_state(provenance=["TRACE:B"]), ["FWD", "BACK"]
        )
        self.assertNotEqual(first["initial_state_digest"], second["initial_state_digest"])
        self.assertNotEqual(first["raw_result_digest"], second["raw_result_digest"])
        self.assertEqual(first["semantic_result_digest"], second["semantic_result_digest"])
        self.assertEqual(first["semantic_result"], second["semantic_result"])
        self.assertNotEqual(
            first["evaluation_receipt_digest"], second["evaluation_receipt_digest"]
        )

    def test_longer_same_semantic_loop_splits_path_and_audit_but_not_semantic_result(self):
        short = create_evaluation_receipt(
            valid_packet(), initial_state(), ["FWD", "BACK"]
        )
        long = create_evaluation_receipt(
            valid_packet(),
            initial_state(),
            ["FWD", "BACK", "FWD", "BACK"],
        )
        self.assertEqual("ZERO_RESIDUE", short["raw_result"]["classification"])
        self.assertEqual("ZERO_RESIDUE", long["raw_result"]["classification"])
        self.assertNotEqual(short["ordered_path_digest"], long["ordered_path_digest"])
        self.assertNotEqual(short["raw_result_digest"], long["raw_result_digest"])
        self.assertEqual(short["semantic_result_digest"], long["semantic_result_digest"])
        self.assertEqual(short["semantic_result"], long["semantic_result"])
        self.assertNotEqual(
            short["evaluation_receipt_digest"], long["evaluation_receipt_digest"]
        )

    def test_semantic_state_change_splits_state_and_semantic_result(self):
        first = create_evaluation_receipt(
            valid_packet(), initial_state(5), ["FWD", "BACK"]
        )
        second = create_evaluation_receipt(
            valid_packet(), initial_state(6), ["FWD", "BACK"]
        )
        self.assertNotEqual(first["initial_state_digest"], second["initial_state_digest"])
        self.assertNotEqual(first["semantic_result_digest"], second["semantic_result_digest"])
        self.assertNotEqual(
            first["evaluation_receipt_digest"], second["evaluation_receipt_digest"]
        )

    def test_operator_declaration_order_is_full_receipt_invariant(self):
        a = valid_packet()
        b = valid_packet()
        b["operators"].reverse()
        first = create_evaluation_receipt(a, initial_state(), ["FWD", "BACK"])
        second = create_evaluation_receipt(b, initial_state(), ["FWD", "BACK"])
        self.assertEqual(first, second)

    def test_packet_wrapper_change_splits_packet_and_receipt_not_runtime_semantics(self):
        a = valid_packet()
        b = valid_packet()
        b["firewalls"].append("CUSTOM_AUDIT_FIREWALL")
        first = create_evaluation_receipt(a, initial_state(), ["FWD", "BACK"])
        second = create_evaluation_receipt(b, initial_state(), ["FWD", "BACK"])
        self.assertNotEqual(first["packet_semantic_digest"], second["packet_semantic_digest"])
        self.assertEqual(first["operator_registry_digest"], second["operator_registry_digest"])
        self.assertEqual(first["semantic_result_digest"], second["semantic_result_digest"])
        self.assertEqual(first["raw_result_digest"], second["raw_result_digest"])
        self.assertNotEqual(
            first["evaluation_receipt_digest"], second["evaluation_receipt_digest"]
        )

    def test_source_inputs_are_copied_before_receipt_persistence(self):
        packet = valid_packet()
        state = initial_state()
        path = ["FWD", "BACK"]
        receipt = create_evaluation_receipt(packet, state, path)
        frozen = copy.deepcopy(receipt)

        packet["operators"][0]["transforms"]["x"]["operand"] = 999
        state["values"]["x"] = 999
        state["provenance"].append("MUTATED")
        path.append("FWD")

        self.assertEqual(frozen, receipt)
        self.assertEqual(5, receipt["initial_state"]["values"]["x"])
        self.assertEqual(["FWD", "BACK"], receipt["ordered_path"])

    def test_valid_packet_can_receipt_raw_unknown_without_inventing_zero(self):
        first = create_evaluation_receipt(
            valid_packet(), initial_state(), ["MISSING"]
        )
        second = create_evaluation_receipt(
            valid_packet(), initial_state(), ["MISSING"]
        )
        self.assertEqual("EVALUATED", first["status"])
        self.assertEqual("UNKNOWN", first["raw_result"]["standing"])
        self.assertEqual("UNKNOWN_RESIDUE", first["raw_result"]["classification"])
        self.assertIsNone(first["raw_result"]["residue"])
        self.assertIsNone(first["raw_result"]["residue_zero"])
        self.assertEqual(first["semantic_result_digest"], second["semantic_result_digest"])
        self.assertEqual(
            first["evaluation_receipt_digest"], second["evaluation_receipt_digest"]
        )

    def test_invalid_packet_holds_without_execution_identity(self):
        packet = valid_packet()
        packet["historical_mapping"]["edges"] = [
            {"source": "history", "target": "synthetic"}
        ]
        result = create_evaluation_receipt(
            packet, initial_state(), ["FWD", "BACK"]
        )
        self.assertEqual("HOLD", result["status"])
        self.assertIsNone(result["evaluation_receipt_digest"])
        self.assertEqual("INVALID_CONNECTION_PACKET", result["errors"][0]["code"])

    def test_nonfinite_initial_state_holds_before_execution(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                result = create_evaluation_receipt(
                    valid_packet(), initial_state(value), ["FWD", "BACK"]
                )
                self.assertEqual("HOLD", result["status"])
                self.assertEqual("NONFINITE_JSON_NUMBER", result["errors"][0]["code"])

        nested = initial_state()
        nested["values"]["x"] = {"nested": [1, math.nan]}
        result = create_evaluation_receipt(
            valid_packet(), nested, ["FWD", "BACK"]
        )
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("NONFINITE_JSON_NUMBER", result["errors"][0]["code"])

    def test_caller_cannot_self_mint_implementation_source_or_authority(self):
        for claims in (
            {"ci_status": "success"},
            {"authority": "CANONICAL"},
            {"source_verified": True},
            {"implementation_verified": True, "ci_run_id": 123},
            {"git_head": "a" * 40},
            {"repository": "demeet2k/athena-mcp-server"},
        ):
            with self.subTest(claims=claims):
                result = create_evaluation_receipt(
                    valid_packet(),
                    initial_state(),
                    ["FWD", "BACK"],
                    caller_claims=claims,
                )
                self.assertEqual("HOLD", result["status"])
                self.assertEqual(
                    "UNTRUSTED_IMPLEMENTATION_CLAIM",
                    result["errors"][0]["code"],
                )
                self.assertIsNone(result["evaluation_receipt_digest"])

    def test_initial_state_cannot_override_derived_basis_or_standing(self):
        for key, value in (
            ("feature_basis", ["x"]),
            ("standing", "PRIMARY_EVIDENCE"),
        ):
            with self.subTest(key=key):
                state = initial_state()
                state[key] = value
                result = create_evaluation_receipt(
                    valid_packet(), state, ["FWD", "BACK"]
                )
                self.assertEqual("HOLD", result["status"])
                self.assertEqual("UNKNOWN_INITIAL_STATE_FIELD", result["errors"][0]["code"])

    def test_initial_irreversible_loss_must_be_unique_and_in_basis(self):
        state = initial_state()
        state["irreversible_loss"] = ["missing"]
        result = create_evaluation_receipt(
            valid_packet(), state, ["FWD", "BACK"]
        )
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("INITIAL_LOSS_FEATURE_OUTSIDE_BASIS", result["errors"][0]["code"])

        state = initial_state()
        state["irreversible_loss"] = ["x", "x"]
        result = create_evaluation_receipt(
            valid_packet(), state, ["FWD", "BACK"]
        )
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(result["errors"][0]["code"].startswith("DUPLICATE_"))

    def test_empty_path_holds(self):
        result = create_evaluation_receipt(valid_packet(), initial_state(), [])
        self.assertEqual("HOLD", result["status"])
        self.assertEqual("EMPTY_ORDERED_PATH", result["errors"][0]["code"])

    def test_exact_replay_matches_state_path_semantic_and_audit_identity(self):
        receipt = create_evaluation_receipt(
            valid_packet(), initial_state(), ["FWD", "BACK"]
        )
        replay = replay_evaluation_receipt(valid_packet(), receipt)
        self.assertEqual("REPLAY_MATCH", replay["status"])
        self.assertEqual(REPLAY_STANDING, replay["standing"])
        self.assertTrue(all(replay["checks"].values()))
        self.assertEqual(
            receipt["evaluation_receipt_digest"],
            replay["evaluation_receipt_digest"],
        )
        self.assertEqual(SOURCE_EVIDENCE, replay["source_evidence"])
        self.assertEqual("NONE", replay["authority_delta"])

    def test_changed_packet_cannot_replay_old_receipt(self):
        receipt = create_evaluation_receipt(
            valid_packet(), initial_state(), ["FWD", "BACK"]
        )
        changed = valid_packet()
        changed["firewalls"].append("CUSTOM_AUDIT_FIREWALL")
        replay = replay_evaluation_receipt(changed, receipt)
        self.assertEqual("HOLD", replay["status"])
        self.assertEqual(
            "REPLAY_PACKET_SEMANTIC_DIGEST_MISMATCH",
            replay["errors"][0]["code"],
        )

    def test_tampered_receipt_fails_self_digest(self):
        receipt = create_evaluation_receipt(
            valid_packet(), initial_state(), ["FWD", "BACK"]
        )
        receipt["raw_result"]["classification"] = "FORGED"
        replay = replay_evaluation_receipt(valid_packet(), receipt)
        self.assertEqual("HOLD", replay["status"])
        self.assertEqual(
            "EVALUATION_RECEIPT_SELF_DIGEST_MISMATCH",
            replay["errors"][0]["code"],
        )

    def test_recomputed_digest_cannot_smuggle_external_implementation_binding(self):
        receipt = create_evaluation_receipt(
            valid_packet(), initial_state(), ["FWD", "BACK"]
        )
        receipt["implementation_binding"]["git_head"] = "a" * 40
        receipt["implementation_binding"]["ci_conclusion"] = "success"
        receipt["evaluation_receipt_digest"] = recompute_self_digest(receipt)
        replay = replay_evaluation_receipt(valid_packet(), receipt)
        self.assertEqual("HOLD", replay["status"])
        self.assertEqual(
            "RECEIPT_IMPLEMENTATION_BINDING_INVALID",
            replay["errors"][0]["code"],
        )

    def test_receipt_schema_freezes_non_witness_and_semantic_audit_split(self):
        schema_path = (
            Path(__file__).resolve().parents[1]
            / "schemas"
            / "mck_connection_evaluation_receipt_v1.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(RECEIPT_ARTIFACT, props["artifact"]["const"])
        self.assertEqual(RECEIPT_VERSION, props["version"]["const"])
        self.assertEqual(RECEIPT_REVISION, props["revision"]["const"])
        self.assertEqual(RECEIPT_STANDING, props["standing"]["const"])
        self.assertEqual(SEMANTIC_CONTROL_ARTIFACT, props["semantic_control_artifact"]["const"])
        self.assertEqual(
            SEMANTIC_RESULT_PROJECTION_BASIS,
            props["semantic_result_projection_basis"]["const"],
        )
        binding = props["implementation_binding"]["properties"]
        self.assertEqual("EXTERNAL_BINDING_REQUIRED", binding["standing"]["const"])
        self.assertEqual("null", binding["git_head"]["type"])
        self.assertEqual("null", binding["ci_run_id"]["type"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
