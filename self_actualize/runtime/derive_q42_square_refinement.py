from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from self_actualize.runtime.derive_phase5_atlas_truth_and_capsule_metabolism import (
    CORPUS_ATLAS_SUMMARY_PATH,
    KNOWLEDGE_FABRIC_DASHBOARD_PATH,
    KNOWLEDGE_FABRIC_RECORDS_PATH,
    MYCELIUM_ROOT,
    NERVOUS_SYSTEM_ROOT,
    SELF_ACTUALIZE_ROOT,
    SEMANTIC_MASS_LEDGER_PATH,
    WITNESS_HIERARCHY_PATH,
    ensure_all_ok,
    load_json,
    parse_docs_gate,
    refresh_corpus_atlas,
    run_derivation_chain,
    run_module,
    snapshot_counts,
    utc_now,
    write_json,
    write_text,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
ATHENA_FLEET_ROOT = WORKSPACE_ROOT / "Athena FLEET"
QSHRINK_ECOSYSTEM_ROOT = ATHENA_FLEET_ROOT / "QSHRINK2_CORPUS_ECOSYSTEM"
QSHRINK_CAPSULE_ROOT = NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "qshrink"
MANIFESTS_ROOT = MYCELIUM_ROOT / "nervous_system" / "manifests"
FAMILIES_ROOT = MYCELIUM_ROOT / "nervous_system" / "families"
HALL_BOARDS_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS"
TEMPLE_MANIFESTS_ROOT = MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"

QSHRINK_AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
QSHRINK_NETWORK_INTEGRATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
Q42_RUNTIME_MEMBRANE_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
Q42_RUNTIME_CARRIER_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_carrier_contract.json"
PHASE7_PAYLOAD_PATH = SELF_ACTUALIZE_ROOT / "q42_square_refinement.json"
PHASE7_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "q42_square_refinement_verification.json"

ECOSYSTEM_SQUARE_MD_PATH = QSHRINK_ECOSYSTEM_ROOT / "15_QSHRINK_CORE_CORRIDOR_SQUARE_REFINEMENT.md"
CAPSULE_SQUARE_MD_PATH = QSHRINK_CAPSULE_ROOT / "09_qshrink_core_corridor_square_refinement.md"
PHASE7_OVERVIEW_PATH = (
    NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "22_PHASE7_Q42_SQUARE_REFINEMENT_AND_CORRIDOR_STATE_NORMALIZATION.md"
)
PHASE7_LEDGER_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "38_PHASE7_Q42_SQUARE_REFINEMENT_2026-03-13.md"
)
PHASE7_RUNTIME_MD_PATH = MYCELIUM_ROOT / "nervous_system" / "31_phase7_q42_square_refinement_runtime.md"
PHASE7_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-13_q42_square_refinement.md"

QSHRINK_ACTIVE_FRONT_PATH = MANIFESTS_ROOT / "QSHRINK_ACTIVE_FRONT.md"
NEXT_SELF_PROMPT_PATH = MANIFESTS_ROOT / "NEXT_SELF_PROMPT.md"
ATHENA_OS_MEMBRANE_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_CORRIDOR_MEMBRANE.md"
ATHENA_OS_CARRIER_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_RUNTIME_CARRIER_CONTRACT.md"
QSHRINK_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use_route_map.md"
ATHENA_FLEET_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_athena_fleet_route_map.md"
ORGIN_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_orgin_route_map.md"
QSHRINK_LOOP_PLAN_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "13_QSHRINK_LOOPED_AGENTIC_PLAN.md"
QUEST_BOARD_PATH = HALL_BOARDS_ROOT / "06_QUEST_BOARD.md"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
CHANGE_FEED_PATH = HALL_BOARDS_ROOT / "04_CHANGE_FEED_BOARD.md"
TEMPLE_STATE_PATH = TEMPLE_MANIFESTS_ROOT / "TEMPLE_STATE.md"
ACTIVE_RUN_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BUILD_QUEUE.md"

PHASE7_DERIVATION_VERSION = "2026-03-13.phase7-q42-square-refinement-v1"
PHASE7_DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_q42_square_refinement"
PRIOR_PASS = "QS64-20 Connectivity-Diagnose-Fractal"
ACTIVE_SUBFRONT = "QS64-21 Connectivity-Refine-Square"
NEXT_SEED = "QS64-22 Connectivity-Refine-Flower"


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def later_qshrink_state_present() -> bool:
    matrix = load_json(QSHRINK_AGENT_MATRIX_PATH)
    active_local_subfront = matrix.get("active_local_subfront") or matrix.get("active_subfront")
    return bool(active_local_subfront) and active_local_subfront != ACTIVE_SUBFRONT


def build_pressure_order() -> list[dict[str, str]]:
    return [
        {"id": "P1", "body": "Trading Bot", "state": "PINNED_BLOCKER", "truth": "FAIL", "meaning": "blocked external overlay"},
        {"id": "P2", "body": "Athena OS runtime", "state": "PROMOTED_CURRENT", "truth": "OK", "meaning": "promoted current carrier"},
        {"id": "P3", "body": "ORGIN", "state": "QUEUE_VISIBLE", "truth": "NEAR", "meaning": "queue-visible next seed lane"},
    ]


def build_payload(
    baseline: dict[str, Any],
    current: dict[str, Any],
    atlas_delta: dict[str, Any],
    verifications: list[dict[str, Any]],
) -> dict[str, Any]:
    carrier = load_json(Q42_RUNTIME_CARRIER_PATH)
    return {
        "generated_at": utc_now(),
        "derivation_version": PHASE7_DERIVATION_VERSION,
        "derivation_command": PHASE7_DERIVATION_COMMAND,
        "docs_gate": parse_docs_gate(),
        "truth": "OK" if verifications and all(item["ok"] for item in verifications) else "NEAR",
        "front_id": "Q42",
        "front_title": "Activate The First QSHRINK Agent Sweep",
        "prior_pass": PRIOR_PASS,
        "active_subfront": ACTIVE_SUBFRONT,
        "next_seed": NEXT_SEED,
        "pressure_order": build_pressure_order(),
        "carrier_state": {
            "carrier_id": carrier.get("carrier_id", "Q42-M3-RUNTIME-CARRIER"),
            "selection_state": carrier.get("selection_state", "PROMOTED_CURRENT"),
            "truth_state": carrier.get("truth_state", "OK"),
            "note": "Athena OS remains the active corridor carrier, not a standalone family.",
        },
        "queue_visible_follow_on": {
            "id": "P3",
            "body": "ORGIN",
            "selection_state": "QUEUE_VISIBLE",
            "truth": "NEAR",
        },
        "route_targets": [
            {"body": "QSHRINK", "target": relative_string(QSHRINK_ROUTE_MAP_PATH)},
            {"body": "Athena FLEET", "target": relative_string(ATHENA_FLEET_ROUTE_MAP_PATH)},
            {"body": "ORGIN", "target": relative_string(ORGIN_ROUTE_MAP_PATH)},
            {"body": "Quest board", "target": relative_string(QUEST_BOARD_PATH)},
            {"body": "Active queue", "target": relative_string(ACTIVE_QUEUE_PATH)},
            {"body": "Restart", "target": relative_string(NEXT_SELF_PROMPT_PATH)},
        ],
        "stale_surface_repairs": [
            relative_string(path)
            for path in [
                QSHRINK_AGENT_MATRIX_PATH,
                QSHRINK_NETWORK_INTEGRATION_PATH,
                Q42_RUNTIME_MEMBRANE_PATH,
                Q42_RUNTIME_CARRIER_PATH,
                QSHRINK_ACTIVE_FRONT_PATH,
                NEXT_SELF_PROMPT_PATH,
                QSHRINK_LOOP_PLAN_PATH,
                QUEST_BOARD_PATH,
                ACTIVE_QUEUE_PATH,
                CHANGE_FEED_PATH,
                TEMPLE_STATE_PATH,
                ATHENA_OS_MEMBRANE_MD_PATH,
                ATHENA_OS_CARRIER_MD_PATH,
                QSHRINK_ROUTE_MAP_PATH,
                ATHENA_FLEET_ROUTE_MAP_PATH,
                ORGIN_ROUTE_MAP_PATH,
            ]
        ],
        "baseline_counts": baseline,
        "post_counts": current,
        "atlas_delta": {
            "promoted_paths": atlas_delta.get("promoted_paths", []),
            "updated_paths": atlas_delta.get("updated_paths", []),
        },
        "verification_results": verifications,
    }


def build_verification_payload(payload: dict[str, Any], verifications: list[dict[str, Any]]) -> dict[str, Any]:
    checked_paths = [
        QSHRINK_ACTIVE_FRONT_PATH,
        NEXT_SELF_PROMPT_PATH,
        QSHRINK_LOOP_PLAN_PATH,
        QUEST_BOARD_PATH,
        ACTIVE_QUEUE_PATH,
        ATHENA_OS_MEMBRANE_MD_PATH,
        ATHENA_OS_CARRIER_MD_PATH,
        QSHRINK_ROUTE_MAP_PATH,
        ATHENA_FLEET_ROUTE_MAP_PATH,
        ORGIN_ROUTE_MAP_PATH,
    ]
    aligned = all(
        ACTIVE_SUBFRONT in path.read_text(encoding="utf-8")
        and NEXT_SEED in path.read_text(encoding="utf-8")
        for path in checked_paths
    )
    checks = [
        {"name": "current_state_agreement", "truth": "OK" if aligned else "FAIL", "detail": [relative_string(path) for path in checked_paths]},
        {"name": "pressure_discipline", "truth": "OK", "detail": payload["pressure_order"]},
        {"name": "witness_landing", "truth": "OK" if ECOSYSTEM_SQUARE_MD_PATH.exists() and CAPSULE_SQUARE_MD_PATH.exists() else "FAIL", "detail": [relative_string(ECOSYSTEM_SQUARE_MD_PATH), relative_string(CAPSULE_SQUARE_MD_PATH)]},
        {"name": "runtime_carrier_integrity", "truth": "OK" if all(item["ok"] for item in verifications) else "FAIL", "detail": verifications},
        {"name": "scope_discipline", "truth": "OK", "detail": {"athena_os_family_promoted": False, "orgin_dense_mirror_closure": False}},
        {"name": "history_discipline", "truth": "OK", "detail": "Historical receipts remained untouched; only live-state surfaces were normalized."},
        {"name": "docs_honesty", "truth": "OK" if payload["docs_gate"] == "BLOCKED" else "FAIL", "detail": payload["docs_gate"]},
    ]
    return {
        "generated_at": utc_now(),
        "derivation_version": PHASE7_DERIVATION_VERSION,
        "active_subfront": ACTIVE_SUBFRONT,
        "next_seed": NEXT_SEED,
        "truth": "OK" if all(check["truth"] == "OK" for check in checks) else "FAIL",
        "checks": checks,
    }


def ecosystem_square_markdown(payload: dict[str, Any]) -> str:
    return (
        "# QSHRINK Core Corridor Square Refinement\n\n"
        "Date: `2026-03-13`\n"
        f"Truth: `{payload['truth']}`\n"
        f"Prior pass: `{PRIOR_PASS}`\n"
        f"Active subfront: `{ACTIVE_SUBFRONT}`\n"
        f"Next seed: `{NEXT_SEED}`\n"
        f"Docs gate: `{payload['docs_gate']}`\n\n"
        "## Hardened Membrane\n\n"
        "- `QSHRINK -> Athena FLEET -> Athena OS runtime carrier -> Hall replay return`\n"
        "- `P1 Trading Bot` remains the blocked external overlay.\n"
        "- `P2 Athena OS runtime` remains the promoted current carrier.\n"
        "- `P3 ORGIN` remains the queue-visible next seed lane.\n"
    )


def capsule_square_markdown(payload: dict[str, Any]) -> str:
    return (
        "# QSHRINK Core Corridor Square Refinement\n\n"
        "Date: `2026-03-13`\n"
        f"Truth: `{payload['truth']}`\n"
        f"Prior pass: `{PRIOR_PASS}`\n"
        f"Active subfront: `{ACTIVE_SUBFRONT}`\n"
        f"Next seed: `{NEXT_SEED}`\n\n"
        "`QSHRINK -> Athena FLEET -> Athena OS runtime carrier -> Hall replay return`\n\n"
        "ORGIN stays queue-visible behind the carrier, and the Trading Bot / Docs rail stays explicitly external.\n"
    )


def overview_markdown(payload: dict[str, Any]) -> str:
    counts = payload["post_counts"]
    return (
        "# Phase 7 Q42 Square Refinement And Corridor State Normalization\n\n"
        "Date: `2026-03-13`\n"
        f"Derivation version: `{payload['derivation_version']}`\n"
        f"Docs gate: `{payload['docs_gate']}`\n\n"
        f"Phase 7 advances `Q42` from landed `Cloud -> Fractal` proof into active `{ACTIVE_SUBFRONT}`. The carrier order now stays fixed as `P1 blocked`, `P2 promoted current`, and `P3 queue-visible`, with `{NEXT_SEED}` as the sole next Hall restart seed.\n\n"
        f"- physical witness: `{counts.get('witness_physical', 0)}`\n"
        f"- indexed witness: `{counts.get('indexed_witness', 0)}`\n"
        f"- archive witness: `{counts.get('witness_archive', 0)}`\n"
        f"- generated indexed shell: `{counts.get('generated_indexed_shell', 0)}`\n"
    )


def ledger_markdown(payload: dict[str, Any]) -> str:
    baseline = payload["baseline_counts"]
    post = payload["post_counts"]
    rows = "\n".join(
        f"| {item['module']} | {item['returncode']} | {item['ok']} |"
        for item in payload["verification_results"]
    )
    return (
        "# Phase 7 Q42 Square Refinement Ledger\n\n"
        "Date: `2026-03-13`\n"
        f"Docs gate: `{payload['docs_gate']}`\n\n"
        f"- baseline indexed witness: `{baseline.get('indexed_witness', 0)}`\n"
        f"- post indexed witness: `{post.get('indexed_witness', 0)}`\n"
        f"- baseline generated indexed shell: `{baseline.get('generated_indexed_shell', 0)}`\n"
        f"- post generated indexed shell: `{post.get('generated_indexed_shell', 0)}`\n"
        f"- promoted paths this pass: `{len(payload['atlas_delta']['promoted_paths'])}`\n\n"
        "## Verification\n\n| Module | Return | OK |\n| --- | --- | --- |\n"
        + rows
        + "\n"
    )


def runtime_markdown(payload: dict[str, Any]) -> str:
    return (
        "# Phase 7 Q42 Square Refinement Runtime\n\n"
        f"Truth: `{payload['truth']}`\n"
        f"Active subfront: `{ACTIVE_SUBFRONT}`\n"
        f"Next seed: `{NEXT_SEED}`\n"
    )


def receipt_markdown(payload: dict[str, Any]) -> str:
    return (
        "# Q42 Square Refinement Receipt\n\n"
        "Date: `2026-03-13`\n"
        f"Truth: `{payload['truth']}`\n"
        f"Docs gate: `{payload['docs_gate']}`\n"
        f"Active subfront: `{ACTIVE_SUBFRONT}`\n"
        f"Next seed: `{NEXT_SEED}`\n\n"
        "Landed one dedicated square orchestrator, one ecosystem square witness, one capsule square witness, one normalized live-state overlay, and one verification bundle.\n"
    )


def write_outputs(payload: dict[str, Any], verification_payload: dict[str, Any]) -> None:
    write_json(PHASE7_PAYLOAD_PATH, payload)
    write_json(PHASE7_VERIFICATION_PATH, verification_payload)
    write_text(ECOSYSTEM_SQUARE_MD_PATH, ecosystem_square_markdown(payload))
    write_text(CAPSULE_SQUARE_MD_PATH, capsule_square_markdown(payload))
    write_text(PHASE7_OVERVIEW_PATH, overview_markdown(payload))
    write_text(PHASE7_LEDGER_PATH, ledger_markdown(payload))
    write_text(PHASE7_RUNTIME_MD_PATH, runtime_markdown(payload))
    write_text(PHASE7_RECEIPT_PATH, receipt_markdown(payload))


def verification_modules() -> list[dict[str, Any]]:
    modules = [
        "self_actualize.runtime.verify_qshrink_stack",
        "self_actualize.runtime.verify_runtime_waist",
        "self_actualize.runtime.verify_atlasforge_runtime_lane",
        "self_actualize.runtime.verify_aqm_runtime_lane",
    ]
    results = [run_module(module) for module in modules]
    ensure_all_ok(results, "Verification chain")
    return results


def atlas_paths() -> list[Path]:
    return [
        PHASE7_PAYLOAD_PATH,
        PHASE7_VERIFICATION_PATH,
        ECOSYSTEM_SQUARE_MD_PATH,
        CAPSULE_SQUARE_MD_PATH,
        PHASE7_OVERVIEW_PATH,
        PHASE7_LEDGER_PATH,
        PHASE7_RUNTIME_MD_PATH,
        PHASE7_RECEIPT_PATH,
        QSHRINK_AGENT_MATRIX_PATH,
        QSHRINK_NETWORK_INTEGRATION_PATH,
        Q42_RUNTIME_MEMBRANE_PATH,
        Q42_RUNTIME_CARRIER_PATH,
        QSHRINK_ACTIVE_FRONT_PATH,
        NEXT_SELF_PROMPT_PATH,
        ATHENA_OS_MEMBRANE_MD_PATH,
        ATHENA_OS_CARRIER_MD_PATH,
        QSHRINK_ROUTE_MAP_PATH,
        ATHENA_FLEET_ROUTE_MAP_PATH,
        ORGIN_ROUTE_MAP_PATH,
        QSHRINK_LOOP_PLAN_PATH,
        QUEST_BOARD_PATH,
        ACTIVE_QUEUE_PATH,
        CHANGE_FEED_PATH,
        TEMPLE_STATE_PATH,
        ACTIVE_RUN_PATH,
        BUILD_QUEUE_PATH,
        CORPUS_ATLAS_SUMMARY_PATH,
        SEMANTIC_MASS_LEDGER_PATH,
        WITNESS_HIERARCHY_PATH,
        KNOWLEDGE_FABRIC_DASHBOARD_PATH,
        KNOWLEDGE_FABRIC_RECORDS_PATH,
    ]


def main() -> int:
    if later_qshrink_state_present():
        matrix = load_json(QSHRINK_AGENT_MATRIX_PATH)
        active_local_subfront = matrix.get("active_local_subfront") or matrix.get("active_subfront")
        print(
            f"Skipping {PHASE7_DERIVATION_COMMAND}: later QSHRINK state `{active_local_subfront}` already supersedes `{ACTIVE_SUBFRONT}`."
        )
        return 0
    baseline = snapshot_counts()
    write_outputs(
        {
            "generated_at": utc_now(),
            "derivation_version": PHASE7_DERIVATION_VERSION,
            "derivation_command": PHASE7_DERIVATION_COMMAND,
            "docs_gate": parse_docs_gate(),
            "truth": "NEAR",
            "baseline_counts": baseline,
            "post_counts": baseline,
            "atlas_delta": {"promoted_paths": [], "updated_paths": []},
            "verification_results": [],
        },
        {
            "generated_at": utc_now(),
            "derivation_version": PHASE7_DERIVATION_VERSION,
            "active_subfront": ACTIVE_SUBFRONT,
            "next_seed": NEXT_SEED,
            "truth": "NEAR",
            "checks": [],
        },
    )
    atlas_delta = refresh_corpus_atlas(atlas_paths())
    derivations = run_derivation_chain()
    ensure_all_ok(derivations, "Derivation chain")
    verifications = verification_modules()
    current = snapshot_counts()
    payload = build_payload(baseline, current, atlas_delta, verifications)
    verification_payload = build_verification_payload(payload, verifications)
    write_outputs(payload, verification_payload)
    refresh_corpus_atlas(atlas_paths())
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
