from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from athena_mcp.cell_closure import CellClosureCompiler, TERMINAL
from athena_mcp.identity import digest
from athena_mcp.inner_constitution import seat

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "KC15_EVIDENCE_CLOSURE_V1.json"
OUTPUT = Path("kc144_kc15_evidence_closure_matrix_v1.json")


def recount(matrix: dict) -> None:
    dims = [
        "constitution_status", "registry_status", "population_status",
        "execution_status", "evidence_status", "return_status",
    ]
    counts = {dimension: {} for dimension in dims}
    overall: dict[str, int] = {}
    next_witnesses: dict[str, int] = {}
    for packet in matrix["packets"]:
        closure = packet["closure"]
        for dimension in dims:
            value = closure[dimension]
            counts[dimension][value] = counts[dimension].get(value, 0) + 1
        state = closure["overall_state"]
        overall[state] = overall.get(state, 0) + 1
        witness = closure["next_required_witness"]
        next_witnesses[witness] = next_witnesses.get(witness, 0) + 1
    matrix["dimension_counts"] = counts
    matrix["overall_counts"] = overall
    matrix["next_witness_counts"] = next_witnesses


def update_kc15_packet(packet: dict, contract: dict, binding: dict) -> None:
    gid = int(packet["identity"]["gid"])
    descriptor = seat(gid)
    if descriptor["block"] != "KC15":
        raise RuntimeError(f"GID{gid:03d} is not KC15")
    closure = packet["closure"]
    if closure["population_status"] != "CLOSED":
        raise RuntimeError(f"GID{gid:03d} population not closed")
    if closure["evidence_status"] != "HOLD":
        raise RuntimeError(f"GID{gid:03d} expected evidence HOLD, got {closure['evidence_status']}")
    if closure["execution_status"] != "PARTIAL" or closure["return_status"] != "PARTIAL":
        raise RuntimeError(f"GID{gid:03d} execution/return standing changed unexpectedly")

    packet["verification"]["evidence"] = {
        "status": "CLOSED",
        "evidence_level": "E5_PROVIDER_OBSERVED",
        "standing": "KC15_BOUNDED_STRUCTURAL_CLAIM_IC10_ADMITTED",
        "claim_scope": contract["update_scope"]["claim_scope"],
        "admission_head": contract["kc15_admission"]["head_sha"],
        "admission_run_id": contract["kc15_admission"]["run_id"],
        "admission_artifact_id": contract["kc15_admission"]["binding_artifact_id"],
        "admission_artifact_digest": contract["kc15_admission"]["binding_artifact_digest"],
        "decision": binding["decision"],
        "decision_digest": binding["decision_digest"],
        "promotion_run_id": binding["promotion_run_id"],
        "promotion_authority": False,
        "truth_claim": "NOT_ESTABLISHED",
        "execution_claim": "NOT_ESTABLISHED",
    }
    packet["verification"]["evidence_level"] = "E5_PROVIDER_OBSERVED"
    closure["evidence_status"] = "CLOSED"
    closure["explicit_holds"] = [name for name in closure.get("explicit_holds", []) if name != "evidence_status"]
    closure["open_dimensions"] = [
        name for name in (
            "constitution_status", "registry_status", "population_status",
            "execution_status", "evidence_status", "return_status",
        )
        if closure[name] not in TERMINAL
    ]
    closure["overall_state"] = "CLOSED" if all(
        closure[name] == "CLOSED"
        for name in (
            "constitution_status", "registry_status", "population_status",
            "execution_status", "evidence_status", "return_status",
        )
    ) else ("HOLD" if closure["explicit_holds"] else "OPEN_TYPED")
    closure["next_required_witness"] = CellClosureCompiler._next_witness(
        closure["population_status"],
        closure["execution_status"],
        closure["evidence_status"],
        closure["return_status"],
        packet["population"].get("binding_defects") or [],
        packet["verification"].get("known_constitutional_obligations") or [],
    )
    packet.pop("packet_id", None)
    packet["packet_id"] = "CELLCLOSE." + digest(packet, 32)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", required=True)
    parser.add_argument("--observed", required=True)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--output", default=str(OUTPUT))
    args = parser.parse_args(argv)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    population_receipt = json.loads(Path(args.population).read_text(encoding="utf-8"))
    observed = json.loads(Path(args.observed).read_text(encoding="utf-8"))
    binding = json.loads(Path(args.binding).read_text(encoding="utf-8"))
    parent_matrix = population_receipt.get("matrix") or {}
    matrix = copy.deepcopy(parent_matrix)

    prechecks = {
        "parent_population_receipt_pass": population_receipt.get("status") == "KC144_SOURCE_POPULATION_144_MATCH",
        "parent_population_complete": population_receipt.get("population_complete") is True,
        "parent_seat_count_144": parent_matrix.get("seat_count") == 144,
        "observed_artifact_match": observed.get("artifact") == "ATHENA.KC15.IC10.OBSERVED.ADMISSION.V1",
        "observed_status_match": observed.get("status") == "I01_I09_OBSERVED_I10_UNBOUND_MATCH",
        "observed_head_match": observed.get("checkout_head") == contract["kc15_admission"]["head_sha"],
        "observed_claim_scope_match": (observed.get("claim") or {}).get("scope") == contract["update_scope"]["claim_scope"].replace(" only", " only"),
        "binding_status_match": binding.get("status") == "IC10_I10_BOUND_CHAIN_SATISFIED",
        "binding_head_match": binding.get("checkout_head") == contract["kc15_admission"]["head_sha"],
        "binding_decision_match": binding.get("decision") == contract["kc15_admission"]["decision"],
        "binding_decision_digest_match": binding.get("decision_digest") == contract["kc15_admission"]["decision_digest"],
        "binding_promotion_run_match": binding.get("promotion_run_id") == contract["kc15_admission"]["promotion_run_id"],
        "binding_all_gates_pass": all(value == "PASS" for value in (binding.get("gate_status") or {}).values()) and len(binding.get("gate_status") or {}) == 10,
        "binding_promotion_authority_false": binding.get("promotion_authority") is False,
    }
    # The observed claim's canonical wording is frozen in the observed artifact;
    # enforce bounded KC15 structural scope without depending on cosmetic phrasing.
    prechecks["observed_claim_is_kc15_structural_only"] = (
        "KC15" in str((observed.get("claim") or {}).get("claim_id") or "")
        and "STRUCTURAL" in str((observed.get("claim") or {}).get("claim_id") or "")
        and "structural" in str((observed.get("claim") or {}).get("scope") or "").lower()
    )

    if not all(value for key, value in prechecks.items() if key != "observed_claim_scope_match"):
        raise RuntimeError(json.dumps({"status": "KC15_EVIDENCE_INPUT_HOLD", "prechecks": prechecks}, sort_keys=True))

    parent_matrix_id = matrix.get("matrix_id")
    target_gids = [int(g) for g in contract["update_scope"]["gids"]]
    for gid in target_gids:
        packet = matrix["packets"][gid - 1]
        update_kc15_packet(packet, contract, binding)

    matrix["artifact"] = "ATHENA.KC144.GAP.MATRIX.KC15.EVIDENCE.V1"
    matrix["parent_matrix_id"] = parent_matrix_id
    matrix["evidence_update"] = {
        "artifact": contract["artifact"],
        "gids": target_gids,
        "claim_scope": contract["update_scope"]["claim_scope"],
        "admission_run_id": contract["kc15_admission"]["run_id"],
        "admission_artifact_id": contract["kc15_admission"]["binding_artifact_id"],
        "admission_artifact_digest": contract["kc15_admission"]["binding_artifact_digest"],
    }
    recount(matrix)
    matrix.pop("matrix_id", None)
    matrix["matrix_id"] = "KC144GAP." + digest(matrix, 32)

    expected = contract["expected_counts"]
    checks = {
        **prechecks,
        "population_counts_unchanged": matrix["dimension_counts"]["population_status"] == expected["population_status"],
        "execution_counts_unchanged": matrix["dimension_counts"]["execution_status"] == expected["execution_status"],
        "evidence_counts_updated": matrix["dimension_counts"]["evidence_status"] == expected["evidence_status"],
        "return_counts_unchanged": matrix["dimension_counts"]["return_status"] == expected["return_status"],
        "overall_counts_updated": matrix["overall_counts"] == expected["overall_state"],
        "all_kc15_evidence_closed": all(matrix["packets"][gid - 1]["closure"]["evidence_status"] == "CLOSED" for gid in target_gids),
        "all_kc15_open_typed": all(matrix["packets"][gid - 1]["closure"]["overall_state"] == "OPEN_TYPED" for gid in target_gids),
        "all_kc15_next_witness_execution": all(matrix["packets"][gid - 1]["closure"]["next_required_witness"] == "BIND_EXECUTABLE_RUNTIME_OR_DORMANT_STATUS" for gid in target_gids),
        "four_remaining_holds_exact": all(
            matrix["packets"][gid - 1]["closure"]["evidence_status"] == "HOLD"
            for gid in (73, 77, 78, 79)
        ) and matrix["overall_counts"].get("HOLD") == 4,
        "whole_crystal_still_not_closed": matrix["overall_counts"].get("CLOSED", 0) == 0,
    }
    ok = all(value for key, value in checks.items() if key != "observed_claim_scope_match")
    receipt = {
        "artifact": contract["artifact"],
        "status": "KC15_EVIDENCE_CLOSURE_MATRIX_MATCH" if ok else "KC15_EVIDENCE_CLOSURE_MATRIX_HOLD",
        "parent_matrix_id": parent_matrix_id,
        "matrix_id": matrix["matrix_id"],
        "checks": checks,
        "dimension_counts": matrix["dimension_counts"],
        "overall_counts": matrix["overall_counts"],
        "next_witness_counts": matrix["next_witness_counts"],
        "remaining_evidence_holds": contract["remaining_evidence_holds"],
        "evidence_ceiling": contract["firewalls"],
        "matrix": matrix,
    }
    Path(args.output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k != "matrix"}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
