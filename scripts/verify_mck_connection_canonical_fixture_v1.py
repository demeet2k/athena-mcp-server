from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from athena_mcp.mck_evaluation_receipt_v1 import (
    build_evaluation_receipt,
    replay_stored_evaluation_receipt,
    validate_evaluation_receipt,
)
from athena_mcp.mythic_connection_packet import validate_connection_packet
from athena_mcp.semantic_connection_control_v1 import SemanticState

ARTIFACT = "ATHENA.MCK.CONNECTION.CANONICAL_FIXTURE.V1.VERIFIER"
VERSION = "MCK.CONNECTION.CANONICAL_FIXTURE.V1.VERIFIER"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _state_from_registry(spec: dict[str, Any]) -> SemanticState:
    return SemanticState(
        spec["coordinate"],
        spec["values"],
        feature_basis=tuple(spec["feature_basis"]),
        provenance=tuple(spec.get("provenance", [])),
        irreversible_loss=frozenset(spec.get("irreversible_loss", [])),
        standing=spec["standing"],
    )


def _control_vector(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "initial_state_digest": receipt["initial_state_digest"],
        "ordered_path_digest": receipt["ordered_path_digest"],
        "evaluation_input_digest": receipt["evaluation_input_digest"],
        "raw_result_digest": receipt["raw_result_digest"],
        "semantic_result_digest": receipt["semantic_result_digest"],
        "receipt_digest": receipt["receipt_digest"],
        "receipt_id": receipt["receipt_id"],
        "classification": receipt["raw_result"]["classification"],
        "residue_zero": receipt["raw_result"]["residue_zero"],
    }


def _expected_control_vector(registry: dict[str, Any], control: dict[str, Any]) -> dict[str, Any]:
    return {
        "initial_state_digest": registry["initial_state_digest"],
        "ordered_path_digest": control["ordered_path_digest"],
        "evaluation_input_digest": control["evaluation_input_digest"],
        "raw_result_digest": control["raw_result_digest"],
        "semantic_result_digest": control["semantic_result_digest"],
        "receipt_digest": control["receipt_digest"],
        "receipt_id": control["receipt_id"],
        "classification": control["expected_classification"],
        "residue_zero": control["expected_residue_zero"],
    }


def _mutation_probe(packet: dict[str, Any], state: SemanticState, pinned_receipt: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(packet)
    by_id = {row["edge_id"]: row for row in mutated["operators"]}
    by_id["FWD"]["transforms"]["x"]["operand"] = 2
    mutated.pop("packet_semantic_digest", None)
    mutated.pop("operator_registry_digest", None)
    changed = build_evaluation_receipt(mutated, state, ["FWD", "BACK"])
    return {
        "status": changed.get("status"),
        "packet_digest_changed": changed.get("packet_semantic_digest") != pinned_receipt.get("packet_semantic_digest"),
        "operator_digest_changed": changed.get("operator_registry_digest") != pinned_receipt.get("operator_registry_digest"),
        "receipt_digest_changed": changed.get("receipt_digest") != pinned_receipt.get("receipt_digest"),
    }


def verify(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[1]
    registry = _load_json(root / "registry" / "mck_connection_canonical_fixture_v1.json")
    packet = _load_json(root / registry["packet_path"])
    pinned_receipt = _load_json(root / registry["canonical_receipt_path"])
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}

    packet_validation = validate_connection_packet(packet)
    checks["packet_valid"] = packet_validation.get("status") == "VALID"
    checks["packet_digest_pinned"] = packet_validation.get("packet_semantic_digest") == registry["packet_semantic_digest"] == packet.get("packet_semantic_digest")
    checks["operator_digest_pinned"] = packet_validation.get("operator_registry_digest") == registry["operator_registry_digest"] == packet.get("operator_registry_digest")

    state = _state_from_registry(registry["initial_state"])
    generated: dict[str, dict[str, Any]] = {}
    for name in ("reversible_zero", "irreversible_loss"):
        control = registry["controls"][name]
        receipt = build_evaluation_receipt(packet, state, control["edge_path"])
        generated[name] = receipt
        checks[f"{name}_recorded"] = receipt.get("status") == "RECORDED"
        checks[f"{name}_identity_pinned"] = _control_vector(receipt) == _expected_control_vector(registry, control)

    zero = generated["reversible_zero"]
    checks["zero_control_zero"] = zero.get("raw_result", {}).get("classification") == "ZERO_RESIDUE" and zero.get("raw_result", {}).get("residue") == {} and zero.get("raw_result", {}).get("residue_zero") is True

    loss = generated["irreversible_loss"]
    expected_loss = registry["controls"]["irreversible_loss"]["expected_irreversible_loss"]
    checks["loss_control_nonzero"] = loss.get("raw_result", {}).get("classification") == "NONZERO_RESIDUE" and loss.get("raw_result", {}).get("residue_zero") is False and loss.get("raw_result", {}).get("residue", {}).get("__irreversible_loss__", {}).get("after") == expected_loss

    checks["stored_receipt_exact"] = pinned_receipt == loss
    stored_validation = validate_evaluation_receipt(pinned_receipt)
    checks["stored_receipt_valid"] = stored_validation.get("status") == "VALID"
    replay = replay_stored_evaluation_receipt(pinned_receipt, packet)
    checks["stored_receipt_replays"] = replay.get("status") == "MATCH"

    mutation = _mutation_probe(packet, state, zero)
    checks["declaration_mutation_detected"] = all((mutation["status"] == "RECORDED", mutation["packet_digest_changed"], mutation["operator_digest_changed"], mutation["receipt_digest_changed"]))

    tampered = copy.deepcopy(pinned_receipt)
    tampered["initial_state_digest"] = "0" * 64
    checks["state_digest_tamper_detected"] = validate_evaluation_receipt(tampered).get("status") == "HOLD"
    tampered = copy.deepcopy(pinned_receipt)
    tampered["ordered_path_digest"] = "0" * 64
    checks["path_digest_tamper_detected"] = validate_evaluation_receipt(tampered).get("status") == "HOLD"
    tampered = copy.deepcopy(pinned_receipt)
    tampered["raw_result"]["classification"] = "FORGED"
    checks["receipt_tamper_detected"] = validate_evaluation_receipt(tampered).get("status") == "HOLD"

    attestation = registry["external_attestation"]
    checks["external_attestation_unbound"] = attestation.get("standing") == "NOT_SELF_BOUND" and all(attestation.get(key) is None for key in ("repository", "git_head", "workflow", "run_id", "run_number", "conclusion", "attestation_ref"))

    details.update({
        "packet_semantic_digest": packet_validation.get("packet_semantic_digest"),
        "operator_registry_digest": packet_validation.get("operator_registry_digest"),
        "initial_state_digest": registry["initial_state_digest"],
        "zero_ordered_path_digest": registry["controls"]["reversible_zero"]["ordered_path_digest"],
        "loss_ordered_path_digest": registry["controls"]["irreversible_loss"]["ordered_path_digest"],
        "zero_receipt_id": zero.get("receipt_id"),
        "loss_receipt_id": loss.get("receipt_id"),
        "stored_validation": stored_validation,
        "replay": replay,
        "mutation_probe": mutation,
    })

    failed = sorted(name for name, passed in checks.items() if not passed)
    return {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed": failed,
        "details": details,
        "standing": "SYNTHETIC_CANONICAL_FIXTURE_VERIFICATION_ONLY",
        "external_repository_witness": "NOT_SELF_BOUND",
        "historical_mapping": "HOLD",
        "promotion": "HOLD",
    }


def main() -> int:
    result = verify()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
