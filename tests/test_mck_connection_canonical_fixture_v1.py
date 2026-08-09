from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

from athena_mcp.mck_evaluation_receipt_v1 import (
    build_evaluation_receipt,
    replay_evaluation_receipt,
    validate_evaluation_receipt,
)
from athena_mcp.mythic_connection_packet import validate_connection_packet
from athena_mcp.semantic_connection_control_v1 import SemanticState


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "fixtures" / "mck_connection_packet_v1_canonical.json"
RECEIPT_PATH = ROOT / "fixtures" / "mck_connection_replay_receipt_v1_canonical.json"
REGISTRY_PATH = ROOT / "registry" / "mck_connection_canonical_fixture_v1.json"
SCRIPT_PATH = ROOT / "scripts" / "verify_mck_connection_canonical_fixture_v1.py"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_verifier_module():
    spec = importlib.util.spec_from_file_location("mck_fixture_verifier", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load canonical fixture verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _state(registry):
    spec = registry["initial_state"]
    return SemanticState(
        spec["coordinate"],
        spec["values"],
        feature_basis=tuple(spec["feature_basis"]),
        provenance=tuple(spec["provenance"]),
        standing=spec["standing"],
    )


class MckConnectionCanonicalFixtureV1Tests(unittest.TestCase):
    def setUp(self):
        self.packet = _load(PACKET_PATH)
        self.receipt = _load(RECEIPT_PATH)
        self.registry = _load(REGISTRY_PATH)
        self.state = _state(self.registry)

    def test_verifier_passes_all_frozen_checks(self):
        result = _load_verifier_module().verify(ROOT)
        self.assertEqual("PASS", result["status"], result)
        self.assertEqual([], result["failed"])
        self.assertTrue(result["checks"])
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual("NOT_SELF_BOUND", result["external_repository_witness"])
        self.assertEqual("HOLD", result["historical_mapping"])
        self.assertEqual("HOLD", result["promotion"])

    def test_packet_literal_validates_to_exact_pins(self):
        validation = validate_connection_packet(self.packet)
        self.assertEqual("VALID", validation["status"])
        self.assertEqual(
            self.registry["packet_semantic_digest"],
            validation["packet_semantic_digest"],
        )
        self.assertEqual(
            self.registry["operator_registry_digest"],
            validation["operator_registry_digest"],
        )
        self.assertEqual(
            self.packet["packet_semantic_digest"],
            validation["packet_semantic_digest"],
        )
        self.assertEqual(
            self.packet["operator_registry_digest"],
            validation["operator_registry_digest"],
        )

    def test_reversible_zero_control_matches_literal_vector(self):
        control = self.registry["controls"]["reversible_zero"]
        receipt = build_evaluation_receipt(
            self.packet, self.state, control["edge_path"]
        )
        self.assertEqual("RECORDED", receipt["status"])
        self.assertEqual("ZERO_RESIDUE", receipt["raw_result"]["classification"])
        self.assertEqual({}, receipt["raw_result"]["residue"])
        self.assertTrue(receipt["raw_result"]["residue_zero"])
        for key in (
            "evaluation_input_digest",
            "raw_result_digest",
            "semantic_result_digest",
            "receipt_digest",
            "receipt_id",
        ):
            self.assertEqual(control[key], receipt[key], key)

    def test_irreversible_control_exactly_recreates_stored_receipt(self):
        control = self.registry["controls"]["irreversible_loss"]
        generated = build_evaluation_receipt(
            self.packet, self.state, control["edge_path"]
        )
        self.assertEqual(self.receipt, generated)
        self.assertEqual("NONZERO_RESIDUE", generated["raw_result"]["classification"])
        self.assertFalse(generated["raw_result"]["residue_zero"])
        self.assertEqual(
            control["expected_irreversible_loss"],
            generated["raw_result"]["residue"]["__irreversible_loss__"]["after"],
        )
        self.assertEqual("VALID", validate_evaluation_receipt(self.receipt)["status"])
        replay = replay_evaluation_receipt(
            self.receipt,
            self.packet,
            self.state,
            control["edge_path"],
        )
        self.assertEqual("MATCH", replay["status"])
        self.assertEqual([], replay["mismatches"])

    def test_operator_mutation_breaks_all_relevant_pins(self):
        mutated = copy.deepcopy(self.packet)
        by_id = {row["edge_id"]: row for row in mutated["operators"]}
        by_id["FWD"]["transforms"]["x"]["operand"] = 2
        mutated.pop("packet_semantic_digest", None)
        mutated.pop("operator_registry_digest", None)

        validation = validate_connection_packet(mutated)
        self.assertEqual("VALID", validation["status"])
        self.assertNotEqual(
            self.registry["packet_semantic_digest"],
            validation["packet_semantic_digest"],
        )
        self.assertNotEqual(
            self.registry["operator_registry_digest"],
            validation["operator_registry_digest"],
        )

        changed = build_evaluation_receipt(
            mutated,
            self.state,
            self.registry["controls"]["reversible_zero"]["edge_path"],
        )
        self.assertEqual("RECORDED", changed["status"])
        pinned = self.registry["controls"]["reversible_zero"]
        self.assertNotEqual(pinned["receipt_digest"], changed["receipt_digest"])
        self.assertNotEqual(pinned["receipt_id"], changed["receipt_id"])

    def test_stored_receipt_tamper_is_rejected(self):
        tampered = copy.deepcopy(self.receipt)
        tampered["raw_result"]["classification"] = "ZERO_RESIDUE"
        result = validate_evaluation_receipt(tampered)
        self.assertEqual("HOLD", result["status"])
        self.assertTrue(
            any("RAW_RESULT_DIGEST_MISMATCH" in error for error in result["errors"])
        )

    def test_external_attestation_cannot_be_self_minted_by_fixture(self):
        attestation = self.registry["external_attestation"]
        self.assertEqual("NOT_SELF_BOUND", attestation["standing"])
        for key in (
            "repository",
            "git_head",
            "workflow",
            "run_id",
            "run_number",
            "conclusion",
            "attestation_ref",
        ):
            self.assertIsNone(attestation[key])
        self.assertEqual("NONE_SYNTHETIC_CONTROL", self.receipt["source_evidence"])
        self.assertFalse(self.receipt["independent_witness"])
        self.assertEqual("NOT_INFERRED_BY_RECEIPT", self.receipt["ci_qualification"])
        binding = self.receipt["implementation_binding"]
        self.assertEqual("EXTERNAL_BINDING_REQUIRED", binding["standing"])
        self.assertTrue(
            all(
                binding[key] is None
                for key in (
                    "repository",
                    "git_head",
                    "ci_workflow",
                    "ci_run_id",
                    "ci_run_number",
                    "ci_conclusion",
                )
            )
        )

    def test_fixture_paths_and_control_names_are_frozen(self):
        self.assertEqual(
            "fixtures/mck_connection_packet_v1_canonical.json",
            self.registry["packet_path"],
        )
        self.assertEqual(
            "fixtures/mck_connection_replay_receipt_v1_canonical.json",
            self.registry["canonical_receipt_path"],
        )
        self.assertEqual(
            {"reversible_zero", "irreversible_loss"},
            set(self.registry["controls"]),
        )
        self.assertEqual(
            "irreversible_loss", self.registry["canonical_receipt_control"]
        )


if __name__ == "__main__":
    unittest.main()
