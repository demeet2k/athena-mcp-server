from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"

CONTRACT_JSON_PATH = SELF_ACTUALIZE_ROOT / "helical_runner_contract.json"
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "helical_runner_contract_verification.json"
MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "TQ04_HELICAL_RUNNER_CONTRACT.md"

DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_helical_runner_contract"
DERIVATION_VERSION = "2026-03-13.tq04.helical-runner-contract-verifier.v2"

EXPECTED_METRICS = [
    "coverage",
    "coherence",
    "contradiction_pressure",
    "born_coordinate_discovery_rate",
    "operator_closure",
    "proof_density",
    "replayability",
    "retrieval_quality",
    "schema_completeness",
    "novelty_gain",
    "pruning_efficiency",
    "compression_ratio",
    "cross_domain_transfer",
    "meta_process_quality",
    "self_growth_gain",
    "unresolved_frontier_clarity",
]

REQUIRED_SPARSE_FIELDS = [
    "dominant_loop",
    "current_phase",
    "role_tensor_slice",
    "score_basis",
    "witness_basis",
    "expected_output_artifact",
    "contraction_target",
]

CONTROL_SURFACES = {
    "temple_board": MYCELIUM_ROOT / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md",
    "temple_state": MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md",
    "active_queue": MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md",
    "active_run": NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md",
    "next_self_prompt": MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md",
    "hall_board": MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md",
    "qshrink_active_front": MYCELIUM_ROOT / "nervous_system" / "manifests" / "QSHRINK_ACTIVE_FRONT.md",
    "loop_progress": MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "16_LOOP_PROGRESS.md",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def load_contract() -> dict:
    return json.loads(CONTRACT_JSON_PATH.read_text(encoding="utf-8"))


def build_checks(contract: dict) -> dict[str, bool]:
    metric_names = [item.get("metric") for item in contract.get("metric_tensor_audit", [])]
    sparse = contract.get("sparse_activation_example", {})
    docs_gate = contract.get("docs_gate", {})
    control_text = {name: read_text(path) for name, path in CONTROL_SURFACES.items()}
    active_run_lower = control_text["active_run"].lower()
    hall_board_lower = control_text["hall_board"].lower()
    qshrink_lower = control_text["qshrink_active_front"].lower()
    next_prompt_lower = control_text["next_self_prompt"].lower()

    return {
        "contract_exists": CONTRACT_JSON_PATH.exists(),
        "manifest_exists": MANIFEST_MD_PATH.exists(),
        "schema_refs_exist": all(
            (WORKSPACE_ROOT / item["path"].replace("\\", "/")).exists()
            for item in contract.get("schema_refs", [])
        ),
        "schema_ref_count_five": len(contract.get("schema_refs", [])) == 5,
        "witness_surfaces_present": all(
            (WORKSPACE_ROOT / path.replace("\\", "/")).exists()
            for path in contract.get("witness_surfaces", [])
        ),
        "docs_gate_blocked": docs_gate.get("status") == "BLOCKED",
        "docs_gate_missing_files_complete": set(docs_gate.get("missing_files", []))
        == {"Trading Bot/credentials.json", "Trading Bot/token.json"},
        "hall_front_q42": contract.get("hall_feeder_front") == "Q42",
        "hall_subfront_qs64_20": contract.get("hall_active_subfront") == "QS64-20 Connectivity-Diagnose-Fractal",
        "restart_seed_qs64_21": contract.get("restart_seed") == "Q42 -> QS64-21 Connectivity-Refine-Square",
        "temple_front_tq04": contract.get("temple_front") == "TQ04",
        "cadence_membrane_q41_tq06": contract.get("cadence_membrane", {}).get("hall_front") == "Q41"
        and contract.get("cadence_membrane", {}).get("temple_front") == "TQ06",
        "q39_receiving_pressure": contract.get("receiving_pressure", {}).get("id") == "Q39 contradiction packet 05",
        "sparse_activation_required_fields": all(field in sparse for field in REQUIRED_SPARSE_FIELDS),
        "phase_machine_walk_complete": len(sparse.get("phase_machine_walk", [])) == 13,
        "metric_tensor_complete": len(metric_names) == 16,
        "metric_tensor_exact_match": metric_names == EXPECTED_METRICS,
        "lift_gate_cap_ok": contract.get("lift_quality_gate", {}).get("max_ratio") == 0.125,
        "lift_gate_ratio_ok": contract.get("lift_quality_gate", {}).get("actual_ratio", 1.0) <= 0.125,
        "lift_gate_verdict_ok": contract.get("lift_quality_gate", {}).get("verdict") == "OK",
        "temple_board_promoted": "[PROMOTED 2026-03-13]" in control_text["temple_board"]
        and "helical_runner_contract.json" in control_text["temple_board"],
        "temple_state_landed_witness": "Landed contract feeder: `TQ04: Bind The Helical Schema Pack To A Runner Contract [PROMOTED 2026-03-13]`" in control_text["temple_state"]
        and "Current Hall-side shadow feeder: `Q42 -> carried QS64-20 Connectivity-Diagnose-Fractal`" in control_text["temple_state"]
        and "Current ownerable Hall uptake: `AP6D-H-WATER-Diagnose`" in control_text["temple_state"],
        "active_queue_promoted": "`PROMOTED 2026-03-13`" in control_text["active_queue"]
        and "helical_runner_contract.json" in control_text["active_queue"],
        "active_run_mentions_contract": "helical runner contract" in active_run_lower
        and "qs64-20 connectivity-diagnose-fractal" in active_run_lower
        and "ap6d-h-water-diagnose" in active_run_lower
        and "ap6d-h-water-refine" in active_run_lower,
        "next_prompt_released_square": "tq04" in next_prompt_lower
        and "operational_current = ap6d-h-water-diagnose" in next_prompt_lower
        and "next_hall_seed = ap6d-h-water-refine" in next_prompt_lower
        and "historical_local_proof = qs64-24 connectivity-refine-fractal [closed hall-local bundle]" in next_prompt_lower,
        "hall_board_q42_current": "qs64-20 connectivity-diagnose-fractal" in hall_board_lower
        and "qs64-24 connectivity-refine-fractal" in hall_board_lower
        and "ap6d-h-water-diagnose" in hall_board_lower
        and "ap6d-h-water-refine" in hall_board_lower
        and "tq04: bind the helical schema pack to a runner contract" in hall_board_lower,
        "qshrink_active_front_aligned": "qs64-20 connectivity-diagnose-fractal" in qshrink_lower
        and "qs64-24 connectivity-refine-fractal [closed hall-local bundle]" in qshrink_lower
        and "ap6d-h-water-diagnose" in qshrink_lower
        and "ap6d-h-water-refine" in qshrink_lower
        and "q50 -> wave7/helix.runtime.fire.diagnose" in qshrink_lower,
        "loop_progress_advanced": "Visible Helix Position: `8/16`" in control_text["loop_progress"]
        and "`7/16` Active Contract Binding `[COMPLETE]`" in control_text["loop_progress"],
    }


def build_payload() -> dict:
    contract = load_contract()
    checks = build_checks(contract)
    failed = [name for name, ok in checks.items() if not ok]
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "derivation_version": DERIVATION_VERSION,
        "truth": "OK" if not failed else "FAIL",
        "contract_path": relative_string(CONTRACT_JSON_PATH),
        "manifest_path": relative_string(MANIFEST_MD_PATH),
        "checks": checks,
        "failed_checks": failed,
        "next_seed": contract.get("restart_seed", "Q42 -> QS64-21 Connectivity-Refine-Square"),
    }


def main() -> int:
    payload = build_payload()
    VERIFICATION_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {VERIFICATION_JSON_PATH}")
    print(f"Truth: {payload['truth']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
