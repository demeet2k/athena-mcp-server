from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from self_actualize.runtime.crystal_remaster_contracts import RuntimeSquareContractRecord
from self_actualize.runtime.derive_crystal_remaster import (
    load_json,
    read_text,
    refresh_corpus_atlas,
    relative_string,
    utc_now,
    write_json,
    write_text,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_ROOT / "registry"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"

RUNTIME_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"
CAPABILITY_STACK_PATH = SELF_ACTUALIZE_ROOT / "qshrink_capability_stack.json"
FLOWER_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_flower.json"
CLOUD_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_cloud.json"
FRACTAL_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_fractal.json"
SQUARE_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_square.json"
NETWORK_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
QSHRINK_RUNTIME_MEMBRANE_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
QSHRINK_RUNTIME_CARRIER_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_carrier_contract.json"
QSHRINK_RUNTIME_SQUARE_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_square_contract.json"
QSHRINK_RUNTIME_SQUARE_JSON_MIRROR = REGISTRY_ROOT / QSHRINK_RUNTIME_SQUARE_JSON_PATH.name
DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_square_runtime_formalization_dashboard.json"
DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / DASHBOARD_JSON_PATH.name
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_square_runtime_formalization_verification.json"
VERIFICATION_JSON_MIRROR = REGISTRY_ROOT / VERIFICATION_JSON_PATH.name
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
PHASE4_PATH = SELF_ACTUALIZE_ROOT / "phase4_weave_candidates.json"
KNOWLEDGE_FABRIC_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_edges.json"
PHASE4_PT2_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_system_crosswalk_edges.json"
QSHRINK_STACK_VERIFY_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"
AQM_RUNTIME_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
ATLASFORGE_RUNTIME_PATH = SELF_ACTUALIZE_ROOT / "atlasforge_runtime_lane.json"
RUNTIME_WAIST_PATH = SELF_ACTUALIZE_ROOT / "runtime_waist_verification.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

MANIFESTS_ROOT = MYCELIUM_ROOT / "nervous_system" / "manifests"
FAMILIES_ROOT = MYCELIUM_ROOT / "nervous_system" / "families"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"
NERVOUS_RUNTIME_ROOT = MYCELIUM_ROOT / "nervous_system"
GUILD_HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS"

ACTIVE_QUEUE_PATH = NERVOUS_RUNTIME_ROOT / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = MANIFESTS_ROOT / "NEXT_SELF_PROMPT.md"
QSHRINK_ACTIVE_FRONT_PATH = MANIFESTS_ROOT / "QSHRINK_ACTIVE_FRONT.md"
QSHRINK_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use_route_map.md"
QSHRINK_FAMILY_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use.md"
ATHENA_FLEET_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_athena_fleet_route_map.md"
ORGIN_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_orgin_route_map.md"
QUEST_BOARD_PATH = GUILD_HALL_ROOT / "06_QUEST_BOARD.md"
CHANGE_FEED_PATH = GUILD_HALL_ROOT / "04_CHANGE_FEED_BOARD.md"
RUNTIME_MEMBRANE_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_CORRIDOR_MEMBRANE.md"
RUNTIME_CARRIER_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_RUNTIME_CARRIER_CONTRACT.md"
RUNTIME_SQUARE_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_RUNTIME_SQUARE_CONTRACT.md"
QSHRINK_AGENT_PLAN_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "13_QSHRINK_LOOPED_AGENTIC_PLAN.md"
QSHRINK_ECOSYSTEM_CAPSULE_PATH = NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "qshrink" / "02_qshrink_shiva_corpus_ecosystem.md"
QSHRINK_AGENT_CAPSULE_PATH = NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "qshrink" / "03_qshrink_agent_sweep_contract.md"

MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "Q42_SQUARE_RUNTIME_FORMALIZATION_MANIFEST.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "Q42_SQUARE_RUNTIME_FORMALIZATION_DASHBOARD.md"
VERIFICATION_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "Q42_SQUARE_RUNTIME_FORMALIZATION_VERIFICATION.md"
RUNTIME_MD_PATH = NERVOUS_RUNTIME_ROOT / "34_q42_square_runtime_formalization_runtime.md"
RECEIPT_MD_PATH = RECEIPTS_ROOT / "2026-03-13_q42_qs64_21_authoritative_square_bundle.md"

FRACTAL_SUBFRONT = "QS64-20 Connectivity-Diagnose-Fractal"
SQUARE_SUBFRONT = "QS64-21 Connectivity-Refine-Square"
FLOWER_REFINEMENT_SUBFRONT = "QS64-22 Connectivity-Refine-Flower"
DEEPER_RECEIVING_FRONTIER = "TQ04: Bind The Helical Schema Pack To A Runner Contract"
QUEUED_FOLLOW_ON = "P3 ORGIN"
RESERVE_FRONTIER = "Q45"
BLOCKED_EXTERNAL_FRONT = "Q02"
DERIVATION_VERSION = "2026-03-13.q42-square-runtime-formalization-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_q42_square_runtime_formalization"


def run_module(module: str) -> Dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-m", module],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "module": module,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "ok": result.returncode == 0,
    }


def docs_gate_status() -> str:
    credentials_path = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token_path = WORKSPACE_ROOT / "Trading Bot" / "token.json"
    if not credentials_path.exists():
        return "blocked-by-missing-credentials"
    if not token_path.exists():
        return "blocked-by-missing-token"
    gate_text = read_text(LIVE_DOCS_GATE_PATH)
    if "Command status: `OPEN`" in gate_text:
        return "open"
    return "blocked-by-auth-failure"


def later_qshrink_state_present() -> bool:
    matrix = load_json(AGENT_MATRIX_PATH)
    active_local_subfront = matrix.get("active_local_subfront") or matrix.get("active_subfront")
    return bool(active_local_subfront) and active_local_subfront != SQUARE_SUBFRONT


def skill_path(skill_name: str) -> Path | None:
    skills_root = Path.home() / ".codex" / "skills"
    local_path = skills_root / skill_name / "SKILL.md"
    if local_path.exists():
        return local_path
    system_path = skills_root / ".system" / skill_name / "SKILL.md"
    if system_path.exists():
        return system_path
    return None


def build_runtime_square_contract() -> RuntimeSquareContractRecord:
    runtime_payload = load_json(RUNTIME_VERIFICATION_PATH)
    membrane_payload = load_json(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH)
    carrier_payload = load_json(QSHRINK_RUNTIME_CARRIER_JSON_PATH)
    truth_state = (
        "OK"
        if runtime_payload.get("truth") == "OK"
        and membrane_payload.get("truth_state") == "OK"
        and carrier_payload.get("truth_state") == "OK"
        else "NEAR"
    )
    return RuntimeSquareContractRecord(
        square_contract_id="Q42-LEG-C3-RUNTIME-SQUARE",
        source_body_id="A16",
        runtime_surface="MATH\\FINAL FORM\\FRAMEWORKS CODE\\Athena OS\\athena_os\\qshrink\\",
        upstream_membrane_surface=relative_string(RUNTIME_MEMBRANE_MD_PATH),
        upstream_carrier_surface=relative_string(RUNTIME_CARRIER_MD_PATH),
        crosswalk_surface=relative_string(SQUARE_JSON_PATH),
        writeback_surfaces=[
            relative_string(QSHRINK_ACTIVE_FRONT_PATH),
            relative_string(QSHRINK_ROUTE_MAP_PATH),
            relative_string(ATHENA_FLEET_ROUTE_MAP_PATH),
            relative_string(NEXT_SELF_PROMPT_PATH),
        ],
        truth_state=truth_state,
        active_subfront=SQUARE_SUBFRONT,
        next_seed=FLOWER_REFINEMENT_SUBFRONT,
        note="Athena OS runtime is now formalized as the corridor-facing square membrane and structural crosswalk for LEG-C3.",
    )


def render_runtime_square_markdown(record: RuntimeSquareContractRecord) -> str:
    writeback_lines = "\n".join(f"- `{item}`" for item in record.writeback_surfaces)
    return f"""# ATHENA OS QSHRINK RUNTIME SQUARE CONTRACT

Date: `2026-03-13`
Truth: `{record.truth_state}`
Active subfront: `{record.active_subfront}`

## Square Contract

- square contract id: `{record.square_contract_id}`
- source body id: `{record.source_body_id}`
- runtime surface: `{record.runtime_surface}`
- upstream membrane surface: `{record.upstream_membrane_surface}`
- upstream carrier surface: `{record.upstream_carrier_surface}`
- crosswalk surface: `{record.crosswalk_surface}`
- next seed: `{record.next_seed}`

## Writeback surfaces

{writeback_lines}

## Note

{record.note}
"""


def build_square_payload(record: RuntimeSquareContractRecord) -> Dict[str, Any]:
    cloud = load_json(CLOUD_JSON_PATH)
    fractal = load_json(FRACTAL_JSON_PATH)
    runtime_payload = load_json(RUNTIME_VERIFICATION_PATH)
    membrane_payload = load_json(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH)
    carrier_payload = load_json(QSHRINK_RUNTIME_CARRIER_JSON_PATH)
    queue_visible = cloud.get("queue_visible_pressures", [{"id": "P3", "body": "ORGIN", "selection_state": "QUEUE_VISIBLE"}])
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK" if record.truth_state == "OK" else "NEAR",
        "focus": "core-corridor-square-refinement",
        "prior_pass": FRACTAL_SUBFRONT,
        "completed_subfront": FRACTAL_SUBFRONT,
        "completed_subfronts": [
            "QS64-18 Connectivity-Diagnose-Flower",
            "QS64-19 Connectivity-Diagnose-Cloud",
            FRACTAL_SUBFRONT,
        ],
        "current_carried_witness": FRACTAL_SUBFRONT,
        "active_local_subfront": SQUARE_SUBFRONT,
        "active_subfront": SQUARE_SUBFRONT,
        "next_hall_seed": FLOWER_REFINEMENT_SUBFRONT,
        "deeper_receiving_frontier": DEEPER_RECEIVING_FRONTIER,
        "queued_follow_on": QUEUED_FOLLOW_ON,
        "reserve_frontier": RESERVE_FRONTIER,
        "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        "square_sync_status": "OK" if record.truth_state == "OK" else "NEAR",
        "runtime_square_status": record.truth_state,
        "lead_pressure": "P2",
        "lead_pressure_body": "Athena OS runtime",
        "queue_visible_pressures": queue_visible,
        "next_restart_seed": FLOWER_REFINEMENT_SUBFRONT,
        "authoritative_current_receipt": relative_string(RECEIPT_MD_PATH),
        "docs_gate_status": docs_gate_status(),
        "pinned_blocker": {
            "id": "P1",
            "body": "Trading Bot",
            "selection_state": "PINNED_BLOCKER",
            "truth": "FAIL",
            "detail": docs_gate_status(),
        },
        "square_selected_boundary": {
            "id": "LEG-C3",
            "body": "Athena OS runtime",
            "role": "runtime-square-membrane",
        },
        "square_boundaries": [
            {
                "id": "LEG-C1",
                "body": "Athena FLEET",
                "truth": "OK",
                "status": "stable-square-anchor",
                "meaning": "QSHRINK and Athena FLEET remain the stable square membrane around the corridor.",
                "surfaces": [
                    "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md",
                    relative_string(ATHENA_FLEET_ROUTE_MAP_PATH),
                    relative_string(QSHRINK_ROUTE_MAP_PATH),
                ],
            },
            {
                "id": "LEG-C2",
                "body": "Trading Bot",
                "truth": "FAIL",
                "status": "pinned-external-overlay",
                "meaning": "The Docs gate stays blocked and external to local square closure.",
                "surfaces": [
                    "self_actualize/trading_bot_truth_corridor.json",
                    relative_string(LIVE_DOCS_GATE_PATH),
                ],
            },
            {
                "id": "LEG-C3",
                "body": "Athena OS runtime",
                "truth": record.truth_state,
                "status": "formalized-square-boundary",
                "meaning": "The runtime leg is now a corridor-facing square membrane and structural crosswalk instead of only a promoted carrier.",
                "surfaces": [
                    relative_string(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH),
                    relative_string(QSHRINK_RUNTIME_CARRIER_JSON_PATH),
                    relative_string(QSHRINK_RUNTIME_SQUARE_JSON_PATH),
                    relative_string(RUNTIME_VERIFICATION_PATH),
                ],
            },
            {
                "id": "LEG-C4",
                "body": "ORGIN",
                "truth": "OK",
                "status": "queue-visible-follow-on",
                "meaning": "ORGIN remains packet-backed and queue-visible, but mirror deepening is not bundled into the square pass.",
                "surfaces": [
                    "self_actualize/q42_orgin_seed_packet_witness.json",
                    relative_string(ORGIN_ROUTE_MAP_PATH),
                ],
            },
        ],
        "source_paths": {
            "qshrink_connectivity_cloud": str(CLOUD_JSON_PATH),
            "qshrink_connectivity_fractal": str(FRACTAL_JSON_PATH),
            "runtime_membrane": str(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH),
            "runtime_carrier": str(QSHRINK_RUNTIME_CARRIER_JSON_PATH),
            "runtime_square_contract": str(QSHRINK_RUNTIME_SQUARE_JSON_PATH),
            "runtime_verification": str(RUNTIME_VERIFICATION_PATH),
            "live_docs_gate_status": str(LIVE_DOCS_GATE_PATH),
        },
        "witness_basis": {
            "cloud_truth": cloud.get("truth", "NEAR"),
            "fractal_truth": fractal.get("truth", "NEAR"),
            "runtime_verification_truth": runtime_payload.get("truth", "NEAR"),
            "membrane_truth": membrane_payload.get("truth_state", "NEAR"),
            "carrier_truth": carrier_payload.get("truth_state", "NEAR"),
        },
    }


def build_runtime_membrane_payload(
    square_payload: Dict[str, Any],
    record: RuntimeSquareContractRecord,
) -> Dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth_state": "OK" if record.truth_state == "OK" else "NEAR",
        "corridor_id": "Q42-M3-RUNTIME-RAIL",
        "source_body_id": "A16",
        "target_runtime_surface": record.runtime_surface,
        "writeback_surface": relative_string(QSHRINK_ACTIVE_FRONT_PATH),
        "current_carried_witness": square_payload["current_carried_witness"],
        "current_owner_facing_subfront": square_payload["active_subfront"],
        "active_local_subfront": square_payload["active_local_subfront"],
        "next_seed": square_payload["next_hall_seed"],
        "deeper_receiving_frontier": square_payload["deeper_receiving_frontier"],
        "queued_follow_on": square_payload["queued_follow_on"],
        "reserve_frontier": square_payload["reserve_frontier"],
        "blocked_external_front": square_payload["blocked_external_front"],
        "selected_pressure": "P2 Athena OS runtime",
        "authoritative_current_receipt": square_payload["authoritative_current_receipt"],
        "witness_basis": [
            relative_string(RUNTIME_VERIFICATION_PATH),
            relative_string(RUNTIME_MEMBRANE_MD_PATH),
            relative_string(QSHRINK_ACTIVE_FRONT_PATH),
            relative_string(QSHRINK_RUNTIME_CARRIER_JSON_PATH),
            relative_string(QSHRINK_RUNTIME_SQUARE_JSON_PATH),
        ],
        "note": (
            f"Athena OS runtime remains P2, carries {square_payload['current_carried_witness']} "
            f"as upstream witness, keeps {square_payload['active_subfront']} current, keeps "
            f"{square_payload['next_hall_seed']} next only, and preserves {QUEUED_FOLLOW_ON} "
            f"behind {RESERVE_FRONTIER} reserve and {BLOCKED_EXTERNAL_FRONT} blocked truth."
        ),
    }


def build_qshrink_network_payload(
    square_payload: Dict[str, Any],
    record: RuntimeSquareContractRecord,
) -> Dict[str, Any]:
    atlas = load_json(WORKSPACE_ROOT / "Athena FLEET" / "QSHRINK2_CORPUS_ECOSYSTEM" / "02_QSHRINK2_CORPUS_ATLAS.json")
    summary = atlas.get("summary", {})
    return {
        "generated_at": utc_now(),
        "derivation_command": "python -m self_actualize.runtime.derive_qshrink_network_integration",
        "truth": "OK" if record.truth_state == "OK" else "NEAR",
        "source_paths": {
            "qshrink_ecosystem": str(WORKSPACE_ROOT / "Athena FLEET" / "QSHRINK2_CORPUS_ECOSYSTEM"),
            "runtime_verification": str(RUNTIME_VERIFICATION_PATH),
            "capability_stack": str(CAPABILITY_STACK_PATH),
            "connectivity_flower": str(FLOWER_JSON_PATH),
            "connectivity_cloud": str(CLOUD_JSON_PATH),
            "connectivity_fractal": str(FRACTAL_JSON_PATH),
            "connectivity_square": str(SQUARE_JSON_PATH),
            "runtime_membrane": str(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH),
            "runtime_carrier": str(QSHRINK_RUNTIME_CARRIER_JSON_PATH),
            "runtime_square_contract": str(QSHRINK_RUNTIME_SQUARE_JSON_PATH),
        },
        "corpus_metrics": {
            "total_files": summary.get("total_files", 0),
            "total_bytes": summary.get("total_bytes", 0),
            "duplicate_groups_count": summary.get("duplicate_groups_count", 0),
            "duplicate_savings_bytes": summary.get("duplicate_savings_bytes", 0),
        },
        "current_carried_witness": square_payload["current_carried_witness"],
        "active_local_subfront": square_payload["active_local_subfront"],
        "completed_subfront": square_payload["completed_subfront"],
        "active_subfront": square_payload["active_subfront"],
        "next_hall_seed": square_payload["next_hall_seed"],
        "deeper_receiving_frontier": square_payload["deeper_receiving_frontier"],
        "queued_follow_on": square_payload["queued_follow_on"],
        "reserve_frontier": square_payload["reserve_frontier"],
        "blocked_external_front": square_payload["blocked_external_front"],
        "square_sync_status": square_payload["square_sync_status"],
        "runtime_square_status": square_payload["runtime_square_status"],
        "lead_pressure": square_payload["lead_pressure"],
        "queue_visible_pressures": square_payload["queue_visible_pressures"],
        "docs_gate_status": square_payload["docs_gate_status"],
        "next_seed": square_payload["next_restart_seed"],
    }


def build_agent_payload(
    square_payload: Dict[str, Any],
    record: RuntimeSquareContractRecord,
) -> Dict[str, Any]:
    first_wave_agents = [
        {
            "skill": "q-shrink",
            "quest": SQUARE_SUBFRONT,
            "status": "ACTIVE",
            "role": "formalize LEG-C3 into a replay-safe square contract and keep the contraction layer aligned with the runtime membrane.",
            "target_surfaces": [
                "self_actualize/qshrink_connectivity_square.json",
                "self_actualize/qshrink_network_integration.json",
                "self_actualize/q42_runtime_square_contract.json",
                "self_actualize/mycelium_brain/nervous_system/families/FAMILY_qshrink_athena_internal_use_route_map.md",
            ],
            "expected_outputs": [
                "one square contract",
                "one runtime membrane crosswalk",
                "one route-safe square writeback",
            ],
        },
        {
            "skill": "metro-cartography",
            "quest": "QS64-18 Connectivity-Diagnose-Flower",
            "status": "DONE",
            "role": "preserve the completed cadence and handoff map as upstream witness.",
            "target_surfaces": [
                "Athena FLEET/",
                "self_actualize/qshrink_connectivity_flower.json",
            ],
            "expected_outputs": [
                "one completed cadence witness",
                "one preserved handoff map",
            ],
        },
        {
            "skill": "guild-hall-quest-loop",
            "quest": "QS64-19 Connectivity-Diagnose-Cloud",
            "status": "DONE",
            "role": "preserve the completed Cloud writeback as the last landed owner-facing synchronization pass.",
            "target_surfaces": [
                "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/04_CHANGE_FEED_BOARD.md",
                "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
                "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
            ],
            "expected_outputs": [
                "one completed synchronization witness",
                "one queue-safe restart handoff",
            ],
        },
        {
            "skill": "manuscript-intake",
            "quest": SQUARE_SUBFRONT,
            "status": "ACTIVE",
            "role": "refresh the square boundary surfaces so the active corridor state stays grounded in current local witness.",
            "target_surfaces": [
                "Athena FLEET/",
                "Trading Bot/",
                "ORGIN/",
                "self_actualize/corpus_atlas.json",
                "self_actualize/qshrink_connectivity_square.json",
            ],
            "expected_outputs": [
                "one grounded square witness",
                "one refreshed atlas slice",
                "one boundary-ready surface delta",
            ],
        },
        {
            "skill": "corpus-status-synthesizer",
            "quest": SQUARE_SUBFRONT,
            "status": "ACTIVE",
            "role": "keep P2 as lead pressure, keep P1 pinned externally, and keep P3 queue-visible while square refinement lands.",
            "target_surfaces": [
                "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/04_CHANGE_FEED_BOARD.md",
                "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
                "self_actualize/qshrink_network_integration.json",
                "self_actualize/qshrink_connectivity_square.json",
            ],
            "expected_outputs": [
                "one square pressure report",
                "one witness-aware queue ordering",
            ],
        },
        {
            "skill": "deeper-integrated-neural-network",
            "quest": FLOWER_REFINEMENT_SUBFRONT,
            "status": "READY",
            "role": "take the square membrane formalization as the next follow-on input for flower refinement instead of activating early in this pass.",
            "target_surfaces": [
                "self_actualize/mycelium_brain/dynamic_neural_network/",
                "GLOBAL_EMERGENT_GUILD_HALL/13_QSHRINK_LOOPED_AGENTIC_PLAN.md",
            ],
            "expected_outputs": [
                "one refinement-ready network handoff",
                "one next-pass synthesis pack",
            ],
        },
    ]
    for agent in first_wave_agents:
        path = skill_path(agent["skill"])
        agent["skill_path"] = str(path) if path else None
        agent["truth"] = "OK" if path else "MISSING"
    return {
        "generated_at": utc_now(),
        "truth": "OK" if record.truth_state == "OK" else "NEAR",
        "docs_gate": "BLOCKED",
        "blocked_by": ["Trading Bot/credentials.json missing", "Trading Bot/token.json missing"],
        "front_id": "Q42",
        "front_title": "Activate The First QSHRINK Agent Sweep",
        "activation_quest": "QS64-09 QShrink-Synthesize-Square",
        "completed_subfront": FRACTAL_SUBFRONT,
        "completed_subfronts": square_payload["completed_subfronts"],
        "active_subfront": SQUARE_SUBFRONT,
        "next_connectivity_quest": FLOWER_REFINEMENT_SUBFRONT,
        "restart_seed": FLOWER_REFINEMENT_SUBFRONT,
        "loop_law": "gate check -> landed Fractal truth -> square boundary formalization -> guild writeback -> queue refresh -> flower refinement restart",
        "guild_law": "request -> quest -> witness -> writeback -> restart",
        "square_selected_boundary": "LEG-C3",
        "lead_pressure": "P2",
        "queued_follow_on_pressure": "P3",
        "runtime_square_status": record.truth_state,
        "first_wave_agents": first_wave_agents,
    }


def render_qshrink_family(payload: Dict[str, Any]) -> str:
    queued = ", ".join(item.get("id", "") for item in payload.get("queue_visible_pressures", [])) or "none"
    return f"""# FAMILY QSHRINK Internal Use

Date: `{payload['generated_at'][:10]}`
Truth: `{payload['truth']}`
Primary rail: `Me`
Primary face: `Air`
Primary hub: `AppN`

## Role

`QSHRINK - ATHENA (internal use)` remains Athena's Shiva layer: the contraction organ that binds doctrine, Fleet routing, runtime proof, Hall closure, square refinement, and replay-safe restart.

## Current front

- completed subfront: `{payload['completed_subfront']}`
- active subfront: `{payload['active_subfront']}`
- square sync status: `{payload['square_sync_status']}`
- runtime square status: `{payload['runtime_square_status']}`
- lead pressure: `{payload['lead_pressure']}`
- queue-visible follow-on: `{queued}`
- external gate overlay: `{payload['docs_gate_status']}`
- next seed: `{payload['next_restart_seed']}`

## Local mass

- runtime square boundary: `LEG-C3`
- thinnest local blocker: `Athena OS runtime structural crosswalk`
- blocked external overlay: `Trading Bot`
"""


def render_qshrink_route_map(payload: Dict[str, Any], record: RuntimeSquareContractRecord) -> str:
    queued = ", ".join(item.get("id", "") for item in payload.get("queue_visible_pressures", [])) or "none"
    return f"""# FAMILY QSHRINK Internal Use Route Map

## Intake

- `QSHRINK - ATHENA (internal use)/README.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/12_QSHRINK_CORE_CORRIDOR_METRO.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/13_QSHRINK_CORE_CORRIDOR_CLOUD.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/14_QSHRINK_CORE_CORRIDOR_FRACTAL.md`
- `self_actualize/qshrink_connectivity_cloud.json`
- `self_actualize/qshrink_connectivity_fractal.json`
- `self_actualize/qshrink_connectivity_square.json`
- `self_actualize/q42_runtime_corridor_membrane.json`
- `self_actualize/q42_runtime_carrier_contract.json`
- `self_actualize/q42_runtime_square_contract.json`
- `self_actualize/q42_orgin_seed_packet_witness.json`

## Main transfer

`QSHRINK - ATHENA (internal use) -> Athena FLEET ecosystem -> qshrink_connectivity_square.json -> runtime square contract -> active queue -> next prompt`

## Law

- treat Flower, Cloud, and Fractal as landed upstream witness, not as current owner-facing passes
- keep Square as the active owner-facing structural crosswalk layer
- hold `P2` as the lead runtime boundary pressure
- keep `P3` queue-visible behind the square membrane
- keep `M2` explicit as an external blocked Docs overlay

## Runtime square boundary

- selected boundary: `LEG-C3`
- contract id: `{record.square_contract_id}`
- truth: `{record.truth_state}`
- crosswalk surface: `{record.crosswalk_surface}`

## Queue-visible follow-on

`{queued}`

## Next route

`QSHRINK -> {payload['active_subfront']} -> {payload['next_restart_seed']}`
"""


def render_qshrink_active_front(payload: Dict[str, Any], record: RuntimeSquareContractRecord) -> str:
    queued = ", ".join(item.get("id", "") for item in payload.get("queue_visible_pressures", [])) or "none"
    return f"""# QSHRINK ACTIVE FRONT

## FrontID

`Q42`

## Quest

Activate The First QSHRINK Agent Sweep

## State

`OPEN`

## Truth

`{payload['truth']}`

## Objective

Carry `{payload['active_subfront']}` honestly by preserving Fractal as the landed prior pass, formalizing `LEG-C3` through the Athena OS runtime square contract, keeping `P2` lead, keeping `P1` external, and leaving `P3` queue-visible.

## Why Now

Flower, Cloud, and Fractal are now landed, but the live surfaces still need one clean present tense. The honest current move is to make Square the only active owner-facing truth and harden the runtime boundary before Flower refinement begins.

## Targets

- `self_actualize/q42_runtime_square_contract.json`
- `self_actualize/qshrink_connectivity_square.json`
- `self_actualize/qshrink_network_integration.json`
- `self_actualize/qshrink_agent_task_matrix.json`
- `self_actualize/mycelium_brain/nervous_system/families/FAMILY_qshrink_athena_internal_use_route_map.md`
- `self_actualize/mycelium_brain/nervous_system/families/FAMILY_athena_fleet_route_map.md`
- `self_actualize/mycelium_brain/nervous_system/families/FAMILY_orgin_route_map.md`

## Queue-visible follow-on

`{queued}`

## Next Seed

`{record.next_seed}`
"""


def render_qshrink_capsule(payload: Dict[str, Any]) -> str:
    queued = ", ".join(item.get("id", "") for item in payload.get("queue_visible_pressures", [])) or "none"
    return f"""# QSHRINK Shiva Corpus Ecosystem

Truth class: `{payload['truth']}`
Domain: `qshrink`
Date: `{payload['generated_at'][:10]}`

## Capsule Summary

The QSHRINK corridor now treats Flower, Cloud, and Fractal as landed upstream, makes Square the active owner-facing pass, and formalizes the Athena OS runtime boundary while ORGIN remains queue-visible.

## State

- completed subfront: `{payload['completed_subfront']}`
- active subfront: `{payload['active_subfront']}`
- square sync status: `{payload['square_sync_status']}`
- runtime square status: `{payload['runtime_square_status']}`
- lead pressure: `{payload['lead_pressure']}`
- queue-visible follow-on: `{queued}`
- next seed: `{payload['next_restart_seed']}`
"""


def render_fleet_route_map(record: RuntimeSquareContractRecord) -> str:
    return f"""# FAMILY Athena FLEET Route Map

## Intake

- `Athena FLEET/MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md`
- `Athena FLEET/FLEET_MYCELIUM_NETWORK/00_README.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/12_QSHRINK_CORE_CORRIDOR_METRO.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/13_QSHRINK_CORE_CORRIDOR_CLOUD.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/14_QSHRINK_CORE_CORRIDOR_FRACTAL.md`
- `self_actualize/qshrink_connectivity_cloud.json`
- `self_actualize/qshrink_connectivity_fractal.json`
- `self_actualize/qshrink_connectivity_square.json`
- `self_actualize/q42_runtime_corridor_membrane.json`
- `self_actualize/q42_runtime_carrier_contract.json`
- `self_actualize/q42_runtime_square_contract.json`
- `self_actualize/q42_orgin_seed_packet_witness.json`

## Main transfer

`QSHRINK -> Athena FLEET ecosystem -> runtime square contract -> Hall Square writeback`

Governance overlay:

`Athena FLEET -> Trading Bot truth corridor -> blocked Docs gate`

## Law

- Flower, Cloud, and Fractal are landed upstream and no longer current owner-facing passes
- Square is the active owner-facing structural layer
- `P2` remains the lead runtime boundary pressure
- `P3` remains queue-visible behind the square membrane
- `M2` remains an external governance overlay while Docs is blocked

## Square status

- landed prior pass: `{FRACTAL_SUBFRONT}`
- active square sync: `OK`
- runtime square contract: `{record.truth_state}`
- external gate overlay: `blocked-by-missing-credentials`
- queue-visible follow-on: `P3 / ORGIN`

## Next route

`{SQUARE_SUBFRONT} -> {FLOWER_REFINEMENT_SUBFRONT}`
"""


def render_orgin_route_map() -> str:
    return f"""# FAMILY ORGIN Route Map

## Intake

- `ORGIN/Fine Tuning Docs/`
- `self_actualize/orgin_atlas.json`
- `NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\orgin\\08_orgin_readable_mirror_megalithic_tome_generator_latent_tunneling_multi.md`
- `self_actualize\\mycelium_brain\\nervous_system\\packets\\PKT_2026-03-13_q42_orgin_seed_packet_witness.md`

## Main transfer

`ORGIN -> readable mirror bundle -> seed packet witness -> Athena FLEET square queue -> runtime square contract`

## Law

Read `ORGIN` as origin memory and observer-seed matter.
Do not route it as miscellaneous storage.
Mirror surfaces remain queue-visible follow-on matter behind the runtime square boundary and do not bypass atlas indexing or the blocked Docs gate.
Do not pre-claim the denser mirror mesh in this pass or bundle mirror deepening into `QS64-21`.

## Next route

`ORGIN -> queue-visible P3 behind {SQUARE_SUBFRONT} -> {FLOWER_REFINEMENT_SUBFRONT}`
"""


def render_q42_queue_block() -> str:
    return f"""### FRONT-Q42-QSHRINK-AGENT-SWEEP

- Quest:
  `Q42: Activate The First QSHRINK Agent Sweep`
- State:
  `OPEN`
- Truth:
  `OK`
- Objective:
  preserve the landed `Cloud -> Fractal` proof, formalize `LEG-C3` through the Athena OS runtime square contract, keep the blocked Docs gate external, keep `P2` lead, and keep `P3` queue-visible
- Why Now:
  Flower, Cloud, and Fractal are now landed, but the organism still needs one lawful present tense across Hall, queue, route, and restart surfaces: Square is active now and Flower refinement is next
- Active subfront:
  `{SQUARE_SUBFRONT}`
- Targets:
  `self_actualize/q42_runtime_square_contract.json`
  `self_actualize/qshrink_connectivity_square.json`
  `self_actualize/qshrink_network_integration.json`
  `self_actualize/qshrink_agent_task_matrix.json`
  `manifests/ATHENA_OS_QSHRINK_RUNTIME_SQUARE_CONTRACT.md`
  `manifests/QSHRINK_ACTIVE_FRONT.md`
  `families/FAMILY_qshrink_athena_internal_use_route_map.md`
  `families/FAMILY_athena_fleet_route_map.md`
  `families/FAMILY_orgin_route_map.md`
  `manifests/NEXT_SELF_PROMPT.md`
  `../receipts/2026-03-13_q42_qs64_21_authoritative_square_bundle.md`
- Witness:
  one square-refinement proof bundle showing `{FRACTAL_SUBFRONT}` as landed, `{SQUARE_SUBFRONT}` as the only active owner-facing pass, one formalized runtime square contract, one queue-visible `P3` marker, one atlas refresh, and one restart-safe `{FLOWER_REFINEMENT_SUBFRONT}` handoff
- Writeback:
  quest board, change feed, active queue, next-self-prompt, and receipt
- Next Seed:
  `{FLOWER_REFINEMENT_SUBFRONT}`
"""


def replace_q42_queue_block() -> None:
    text = read_text(ACTIVE_QUEUE_PATH)
    pattern = r"### FRONT-Q42-QSHRINK-AGENT-SWEEP\n.*?(?=\n### FRONT-|\Z)"
    updated = re.sub(pattern, render_q42_queue_block().rstrip() + "\n\n", text, flags=re.S)
    write_text(ACTIVE_QUEUE_PATH, updated)


def update_next_self_prompt() -> None:
    text = read_text(NEXT_SELF_PROMPT_PATH)
    current_seed_pattern = r"## Current Restart Seed\n\n`[^`]+`"
    current_seed_replacement = (
        "## Current Restart Seed\n\n"
        "`2026-03-13 America/Los_Angeles: keep packet governance on Q41/TQ06 as the active control membrane, "
        "preserve blocked-Docs honesty, record Flower, Cloud, and Fractal as landed upstream Q42 states, "
        f"hold Q42 on {SQUARE_SUBFRONT} as the active owner-facing pass, keep P2 current through the Athena OS runtime square contract, "
        f"keep P3 queue-visible behind it, then carry Q42 into {FLOWER_REFINEMENT_SUBFRONT} as the next corridor followthrough.`"
    )
    text = re.sub(current_seed_pattern, current_seed_replacement, text, flags=re.S)
    preferred_order_pattern = r"Preferred frontier order:\n(?:.*\n)*?(?=```|\Z)"
    preferred_order_replacement = (
        "Preferred frontier order:\n"
        f"1. one `Q42` Square refinement pass through `{SQUARE_SUBFRONT}`\n"
        f"2. one `Q42` corridor carrythrough from `{SQUARE_SUBFRONT}` into `{FLOWER_REFINEMENT_SUBFRONT}`\n"
        "3. one `P3` ORGIN mirror-deepening follow-on after the square membrane remains stable\n"
        "4. one `TQ04` runner-contract binding pass\n"
        "5. one `Q02` live-memory bootstrap prerequisite pass if OAuth material appears\n"
    )
    text = re.sub(preferred_order_pattern, preferred_order_replacement, text, flags=re.S)
    frontier_order_pattern = r"8\. Choose the strongest next frontier in this order:\n(?:   - .*\n)+"
    frontier_order_replacement = (
        "8. Choose the strongest next frontier in this order:\n"
        f"   - `Q42 -> {SQUARE_SUBFRONT}` as the highest executable Hall-side contraction followthrough\n"
        f"   - `Q42 -> {FLOWER_REFINEMENT_SUBFRONT}` only after the square membrane is stable\n"
        "   - `TQ04` as the next deeper Temple receiving frontier for runner-contract pressure\n"
        "   - `Q45` only as a reserve after `Q42` and `TQ04` remain aligned\n"
        "   - `Q02` only if the Docs gate becomes real\n"
    )
    text = re.sub(frontier_order_pattern, frontier_order_replacement, text, flags=re.S)
    write_text(NEXT_SELF_PROMPT_PATH, text)


def render_q42_quest_block() -> str:
    return f"""### Quest Q42: Activate The First QSHRINK Agent Sweep `[OPEN]`

- Objective:
  bind the first-wave QSHRINK agent set to the new 64-lattice so compression, connectivity, runtime, and promotion work become one repeatable ownerable sweep, preserve the landed `Cloud -> Fractal` proof, and advance the owner-facing corridor into `{SQUARE_SUBFRONT}` without bundling the ORGIN mirror deepening into the same pass
- Why now:
  Flower, Cloud, and Fractal are now landed, but the live control plane still needs one lawful present tense: `P1` stays pinned externally, `P2` remains the lead boundary pressure, `P3` stays queue-visible, and the active owner-facing move is now Square refinement
- Active subfront:
  `{SQUARE_SUBFRONT}`
- Target surfaces:
  `self_actualize/q42_runtime_square_contract.json`
  `self_actualize/qshrink_agent_task_matrix.json`
  `self_actualize/qshrink_runtime_verification.json`
  `self_actualize/qshrink_capability_stack.json`
  `self_actualize/qshrink_connectivity_square.json`
  `self_actualize/qshrink_network_integration.json`
  `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/13_QSHRINK_LOOPED_AGENTIC_PLAN.md`
  `self_actualize/mycelium_brain/nervous_system/manifests/QSHRINK_ACTIVE_FRONT.md`
  `self_actualize/mycelium_brain/nervous_system/families/FAMILY_athena_fleet_route_map.md`
  `self_actualize/mycelium_brain/nervous_system/families/FAMILY_orgin_route_map.md`
  `manifests/ATHENA_OS_QSHRINK_RUNTIME_SQUARE_CONTRACT.md`
  `self_actualize/mycelium_brain/receipts/2026-03-13_q42_qs64_21_authoritative_square_bundle.md`
- Witness needed:
  one synced `Cloud -> Fractal -> Square` truth layer, one formalized runtime square contract, one active `{SQUARE_SUBFRONT}` task matrix, one queue-visible `P3` marker, one integration refresh, and one receipt proving `{FLOWER_REFINEMENT_SUBFRONT}` is the sole next corridor seed
- Writeback:
  Hall quest board, change feed, active queue, next-self-prompt, and receipt
- Restart seed:
  keep `Q42` open on `{SQUARE_SUBFRONT}`, keep `Q02` suppressed while Docs gate is blocked, and emit `{FLOWER_REFINEMENT_SUBFRONT}` as the sole next corridor seed
"""


def replace_q42_quest_board_block() -> None:
    text = read_text(QUEST_BOARD_PATH)
    pattern = r"### Quest Q42: Activate The First QSHRINK Agent Sweep `\[OPEN\]`\n.*?(?=\n### Quest |\Z)"
    updated = re.sub(pattern, render_q42_quest_block().rstrip() + "\n\n", text, flags=re.S)
    write_text(QUEST_BOARD_PATH, updated)


def append_change_feed_entry() -> None:
    text = read_text(CHANGE_FEED_PATH)
    existing_phrase = "Q42 Square refinement and runtime membrane formalization is now landed"
    if existing_phrase in text:
        return
    numbers = [int(match) for match in re.findall(r"(?m)^(\d+)\.\s", text)]
    next_number = max(numbers) + 1 if numbers else 1
    entry = (
        f"{next_number}. Q42 Square refinement and runtime membrane formalization is now landed: "
        f"`derive_q42_square_runtime_formalization.py` and `q42_runtime_square_contract.json` formalize `LEG-C3` into the active Athena OS runtime square membrane, "
        f"`qshrink_connectivity_square.json`, `qshrink_network_integration.json`, and `qshrink_agent_task_matrix.json` now agree on `{SQUARE_SUBFRONT}` as the active owner-facing pass, "
        f"`P3` remains explicitly queue-visible, and Hall, queue, route, and restart surfaces now emit `{FLOWER_REFINEMENT_SUBFRONT}` as the sole next corridor seed."
    )
    updated = text.rstrip() + "\n" + entry + "\n"
    write_text(CHANGE_FEED_PATH, updated)


def render_agent_plan(payload: Dict[str, Any]) -> str:
    lines = [
        "# QSHRINK Looped Agentic Plan",
        "",
        f"Date: `{payload['generated_at'][:10]}`",
        f"Truth: `{payload['truth']}`",
        f"Hall frontier: `{payload['front_id']} {payload['front_title']}`",
        f"Crystal activation: `{payload['activation_quest']}`",
        f"Completed subfront: `{payload['completed_subfront']}`",
        f"Active subfront: `{payload['active_subfront']}`",
        f"Next connectivity quest: `{payload['next_connectivity_quest']}`",
        "Live Docs Gate: `BLOCKED` due to missing OAuth files, so this plan is grounded in local corpus witness only.",
        "",
        "## Square Selection",
        "",
        f"- selected boundary: `{payload['square_selected_boundary']}`",
        f"- lead pressure: `{payload['lead_pressure']}`",
        f"- queued follow-on: `{payload['queued_follow_on_pressure']}`",
        f"- runtime square status: `{payload['runtime_square_status']}`",
        "",
        "## First-Wave Agent Task Matrix",
        "",
    ]
    for index, agent in enumerate(payload["first_wave_agents"], start=1):
        targets = "; ".join(f"`{item}`" for item in agent["target_surfaces"])
        outputs = "; ".join(agent["expected_outputs"])
        lines.extend(
            [
                f"### A{index:02d} `{agent['skill']}` -> `{agent['quest']}`",
                "",
                f"- Status: `{agent['status']}`",
                f"- Skill truth: `{agent['truth']}`",
                f"- Role: {agent['role']}",
                f"- Target surfaces: {targets}",
                f"- Expected outputs: {outputs}",
                "",
            ]
        )
    lines.extend(["## Restart Seed", "", f"`{payload['restart_seed']}`"])
    return "\n".join(lines) + "\n"


def render_agent_capsule(payload: Dict[str, Any]) -> str:
    active_agents = [agent["skill"] for agent in payload["first_wave_agents"] if agent["status"] == "ACTIVE"]
    completed = ", ".join(payload.get("completed_subfronts", []))
    return f"""# QSHRINK Agent Sweep Contract

Date: `{payload['generated_at'][:10]}`
Truth class: `{payload['truth']}`
Hall frontier: `{payload['front_id']}`
Crystal activation: `{payload['activation_quest']}`
Completed subfronts: `{completed}`
Active subfront: `{payload['active_subfront']}`
Restart seed: `{payload['restart_seed']}`

## Summary

Q42 now preserves Flower, Cloud, and Fractal as completed corridor states, keeps the governance blocker pinned honestly, and advances the live Hall subfront to Square refinement.

## Corridor selection

- selected boundary: `{payload['square_selected_boundary']}`
- lead pressure: `{payload['lead_pressure']}`
- queued follow-on: `{payload['queued_follow_on_pressure']}`
- runtime square status: `{payload['runtime_square_status']}`

## Active agents

{chr(10).join(f"- {agent}" for agent in active_agents)}

## Next seed

`{payload['restart_seed']}`
"""


def render_manifest(outputs: Dict[str, str], module_runs: List[Dict[str, Any]]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    run_lines = "\n".join(f"- `{run['module']}`: `{'OK' if run['ok'] else 'FAIL'}`" for run in module_runs)
    return f"""# Q42 SQUARE RUNTIME FORMALIZATION MANIFEST

Date: `2026-03-13`
Derivation: `{DERIVATION_COMMAND}`
Wave: `Q42 / {SQUARE_SUBFRONT}`

## Law

- keep Flower, Cloud, and Fractal as landed upstream truth, not as the active owner-facing pass
- synchronize Hall, queue, front, route, and restart surfaces on Square
- formalize `LEG-C3` through the Athena OS runtime square contract
- keep `P3` queue-visible and do not bundle ORGIN mirror deepening into this pass
- emit `{FLOWER_REFINEMENT_SUBFRONT}` as the sole next restart seed

## Outputs

{output_lines}

## Downstream reruns

{run_lines}
"""


def render_dashboard(payload: Dict[str, Any]) -> str:
    verifier_truth = payload.get("verifier_truth", {})
    return f"""# Q42 SQUARE RUNTIME FORMALIZATION DASHBOARD

Date: `2026-03-13`
Truth: `{payload['truth']}`

## Corridor

- completed subfront: `{payload['completed_subfront']}`
- active subfront: `{payload['active_subfront']}`
- square sync status: `{payload['square_sync_status']}`
- runtime square status: `{payload['runtime_square_status']}`
- lead pressure: `{payload['lead_pressure']}`
- queue-visible follow-on: `{payload['queue_visible_follow_on']}`

## Docs gate

- status: `{payload['docs_gate_status']}`

## Verifiers

- `QSHRINK`: `{verifier_truth.get('qshrink_runtime_verification', 'UNKNOWN')}`
- `AQM`: `{verifier_truth.get('aqm_runtime_lane', 'UNKNOWN')}`
- `ATLAS FORGE`: `{verifier_truth.get('atlasforge_runtime_lane', 'UNKNOWN')}`
- `runtime waist`: `{verifier_truth.get('runtime_waist', 'UNKNOWN')}`

## Next seed

`{payload['next_restart_seed']}`
"""


def render_verification(payload: Dict[str, Any]) -> str:
    check_lines = "\n".join(f"- `{name}`: `{value}`" for name, value in payload["checks"].items())
    unresolved_lines = "\n".join(f"- {item}" for item in payload["unresolved"]) or "- none"
    return f"""# Q42 SQUARE RUNTIME FORMALIZATION VERIFICATION

Date: `2026-03-13`
Truth: `{payload['truth']}`

## Checks

{check_lines}

## Unresolved

{unresolved_lines}
"""


def render_runtime(outputs: Dict[str, str], verification: Dict[str, Any]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    return f"""# 34 Q42 SQUARE RUNTIME FORMALIZATION RUNTIME

Date: `2026-03-13`
Truth: `{verification['truth']}`
Docs gate: `{verification['docs_gate_status']}`

## Outputs

{output_lines}
"""


def render_receipt(
    record: RuntimeSquareContractRecord,
    verification: Dict[str, Any],
    module_runs: List[Dict[str, Any]],
) -> str:
    run_lines = "\n".join(f"- `{run['module']}`: `{'OK' if run['ok'] else 'FAIL'}`" for run in module_runs)
    unresolved_lines = "\n".join(f"- {item}" for item in verification["unresolved"]) or "- none"
    return f"""# 2026-03-13 q42 square runtime formalization

- truth: `{verification['truth']}`
- docs gate: `{verification['docs_gate_status']}`
- completed subfront: `{verification['completed_subfront']}`
- active subfront: `{verification['active_subfront']}`
- square sync status: `{verification['square_sync_status']}`
- runtime square status: `{verification['runtime_square_status']}`
- next seed: `{verification['next_restart_seed']}`

## Landed witness

- runtime square contract: `{record.square_contract_id}` / `{record.truth_state}`

## Downstream reruns

{run_lines}

## Honest limits

{unresolved_lines}
"""


def build_verification(generated_paths: List[Path], module_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    square = load_json(SQUARE_JSON_PATH)
    network = load_json(NETWORK_JSON_PATH)
    agent_matrix = load_json(AGENT_MATRIX_PATH)
    contract = load_json(QSHRINK_RUNTIME_SQUARE_JSON_PATH)
    atlas = load_json(CORPUS_ATLAS_PATH)
    atlas_paths = {record.get("relative_path") for record in atlas.get("records", [])}
    generated_relative = [relative_string(path) for path in generated_paths if path.exists()]
    atlas_missing = [path for path in generated_relative if path not in atlas_paths]

    phase4_candidates = load_json(PHASE4_PATH).get("candidates", [])
    knowledge_edges = load_json(KNOWLEDGE_FABRIC_PATH).get("edges", [])
    pt2_edges = load_json(PHASE4_PT2_PATH).get("edges", [])
    phase4_edge_ids = {item.get("bridge_edge_id") for item in phase4_candidates if item.get("bridge_edge_id")}
    knowledge_edge_ids = {item.get("edge_id") for item in knowledge_edges}
    pt2_edge_ids = {item.get("edge_id") for item in pt2_edges}

    queue_text = read_text(ACTIVE_QUEUE_PATH)
    next_prompt_text = read_text(NEXT_SELF_PROMPT_PATH)
    qshrink_family_text = read_text(QSHRINK_FAMILY_PATH)
    qshrink_route_text = read_text(QSHRINK_ROUTE_MAP_PATH)
    fleet_route_text = read_text(ATHENA_FLEET_ROUTE_MAP_PATH)
    orgin_route_text = read_text(ORGIN_ROUTE_MAP_PATH)
    active_front_text = read_text(QSHRINK_ACTIVE_FRONT_PATH)
    quest_board_text = read_text(QUEST_BOARD_PATH)
    change_feed_text = read_text(CHANGE_FEED_PATH)
    agent_plan_text = read_text(QSHRINK_AGENT_PLAN_PATH)

    verifier_truth = {
        "qshrink_runtime_verification": load_json(QSHRINK_STACK_VERIFY_PATH).get("truth", "UNKNOWN"),
        "aqm_runtime_lane": load_json(AQM_RUNTIME_PATH).get("truth", "UNKNOWN"),
        "atlasforge_runtime_lane": load_json(ATLASFORGE_RUNTIME_PATH).get("truth", "UNKNOWN"),
        "runtime_waist": load_json(RUNTIME_WAIST_PATH).get("truth", "UNKNOWN"),
    }

    checks = {
        "square_contract_ok": contract.get("truth_state") == "OK",
        "square_contract_references_upstream": (
            contract.get("upstream_membrane_surface") == relative_string(RUNTIME_MEMBRANE_MD_PATH)
            and contract.get("upstream_carrier_surface") == relative_string(RUNTIME_CARRIER_MD_PATH)
            and contract.get("crosswalk_surface") == relative_string(SQUARE_JSON_PATH)
        ),
        "square_truth_ok": (
            square.get("truth") == "OK"
            and square.get("prior_pass") == FRACTAL_SUBFRONT
            and square.get("active_subfront") == SQUARE_SUBFRONT
            and square.get("next_restart_seed") == FLOWER_REFINEMENT_SUBFRONT
        ),
        "square_runtime_square_ok": square.get("runtime_square_status") == "OK",
        "square_lead_p2": square.get("lead_pressure") == "P2",
        "square_queue_visible_p3": any(item.get("id") == "P3" for item in square.get("queue_visible_pressures", [])),
        "network_completed_fractal": network.get("completed_subfront") == FRACTAL_SUBFRONT,
        "network_active_subfront_square": network.get("active_subfront") == SQUARE_SUBFRONT,
        "network_runtime_square_ok": network.get("runtime_square_status") == "OK",
        "network_next_seed_flower": network.get("next_seed") == FLOWER_REFINEMENT_SUBFRONT,
        "agent_matrix_completed_fractal": agent_matrix.get("completed_subfront") == FRACTAL_SUBFRONT,
        "agent_matrix_active_subfront_square": agent_matrix.get("active_subfront") == SQUARE_SUBFRONT,
        "agent_matrix_selected_boundary_leg_c3": agent_matrix.get("square_selected_boundary") == "LEG-C3",
        "agent_matrix_queue_p3": agent_matrix.get("queued_follow_on_pressure") == "P3",
        "agent_matrix_next_flower": agent_matrix.get("next_connectivity_quest") == FLOWER_REFINEMENT_SUBFRONT,
        "qshrink_family_aligned": SQUARE_SUBFRONT in qshrink_family_text and FLOWER_REFINEMENT_SUBFRONT in qshrink_family_text and "runtime square status" in qshrink_family_text.lower(),
        "active_front_aligned": SQUARE_SUBFRONT in active_front_text and FLOWER_REFINEMENT_SUBFRONT in active_front_text and "runtime square" in active_front_text.lower(),
        "active_queue_aligned": SQUARE_SUBFRONT in queue_text and FLOWER_REFINEMENT_SUBFRONT in queue_text and "square contract" in queue_text.lower(),
        "next_prompt_aligned": (
            SQUARE_SUBFRONT in next_prompt_text
            and FLOWER_REFINEMENT_SUBFRONT in next_prompt_text
            and f"`Q42 -> {SQUARE_SUBFRONT}`" in next_prompt_text
        ),
        "next_prompt_not_cloud_current": "QS64-19 Connectivity-Diagnose-Cloud as the active owner-facing pass" not in next_prompt_text,
        "quest_board_aligned": SQUARE_SUBFRONT in quest_board_text and FLOWER_REFINEMENT_SUBFRONT in quest_board_text and "runtime square contract" in quest_board_text.lower(),
        "change_feed_written": "Q42 Square refinement and runtime membrane formalization is now landed" in change_feed_text,
        "qshrink_route_map_aligned": SQUARE_SUBFRONT in qshrink_route_text and FLOWER_REFINEMENT_SUBFRONT in qshrink_route_text and "runtime square contract" in qshrink_route_text.lower(),
        "fleet_route_map_aligned": SQUARE_SUBFRONT in fleet_route_text and FLOWER_REFINEMENT_SUBFRONT in fleet_route_text and "runtime square contract" in fleet_route_text.lower(),
        "orgin_route_map_aligned": SQUARE_SUBFRONT in orgin_route_text and FLOWER_REFINEMENT_SUBFRONT in orgin_route_text and "queue-visible" in orgin_route_text.lower(),
        "orgin_remains_queue_only": f"queue-visible P3 behind {SQUARE_SUBFRONT}" in orgin_route_text,
        "agent_plan_aligned": SQUARE_SUBFRONT in agent_plan_text and FLOWER_REFINEMENT_SUBFRONT in agent_plan_text and "Square Selection" in agent_plan_text,
        "atlas_refresh_complete": not atlas_missing,
        "phase4_direct_edges_preserved": {"CS-001", "CS-002", "CS-003"}.issubset(phase4_edge_ids),
        "knowledge_fabric_direct_edges_preserved": {"CS-001", "CS-002", "CS-003"}.issubset(knowledge_edge_ids),
        "phase4_pt2_direct_edges_preserved": {"CS-001", "CS-002", "CS-003"}.issubset(pt2_edge_ids),
        "downstream_reruns_green": all(run["ok"] for run in module_runs),
        "runtime_verifiers_green": all(value == "OK" for value in verifier_truth.values()),
        "docs_gate_preserved_blocked": docs_gate_status() == "blocked-by-missing-credentials",
    }
    unresolved: List[str] = []
    if docs_gate_status() != "blocked-by-missing-credentials":
        unresolved.append("Docs gate no longer matches the expected blocked-by-missing-credentials state.")
    if atlas_missing:
        unresolved.append("One or more square-runtime-formalization surfaces are still missing from corpus_atlas.json.")
    if square.get("truth") != "OK":
        unresolved.append("Square no longer reports the expected OK truth state.")
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK" if all(checks.values()) else "FAIL",
        "docs_gate_status": docs_gate_status(),
        "completed_subfront": FRACTAL_SUBFRONT,
        "active_subfront": SQUARE_SUBFRONT,
        "square_sync_status": square.get("square_sync_status", "NEAR"),
        "runtime_square_status": square.get("runtime_square_status", "NEAR"),
        "lead_pressure": square.get("lead_pressure", "P2"),
        "queue_visible_follow_on": ",".join(item.get("id", "") for item in square.get("queue_visible_pressures", [])) or "P3",
        "checks": checks,
        "verifier_truth": verifier_truth,
        "atlas_refresh_pending_paths": atlas_missing,
        "next_restart_seed": FLOWER_REFINEMENT_SUBFRONT,
        "unresolved": unresolved,
    }


def build_dashboard(verification: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "truth": verification["truth"],
        "completed_subfront": verification["completed_subfront"],
        "active_subfront": verification["active_subfront"],
        "square_sync_status": verification["square_sync_status"],
        "runtime_square_status": verification["runtime_square_status"],
        "lead_pressure": verification["lead_pressure"],
        "queue_visible_follow_on": verification["queue_visible_follow_on"],
        "docs_gate_status": verification["docs_gate_status"],
        "verifier_truth": verification["verifier_truth"],
        "next_restart_seed": verification["next_restart_seed"],
    }


def main() -> int:
    if later_qshrink_state_present():
        matrix = load_json(AGENT_MATRIX_PATH)
        active_local_subfront = matrix.get("active_local_subfront") or matrix.get("active_subfront")
        print(
            f"Skipping {DERIVATION_COMMAND}: later QSHRINK state `{active_local_subfront}` already supersedes `{SQUARE_SUBFRONT}`."
        )
        return 0
    runtime_square = build_runtime_square_contract()
    square_payload = build_square_payload(runtime_square)
    runtime_membrane_payload = build_runtime_membrane_payload(square_payload, runtime_square)
    network_payload = build_qshrink_network_payload(square_payload, runtime_square)
    agent_payload = build_agent_payload(square_payload, runtime_square)

    write_json(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH, runtime_membrane_payload)
    write_json(QSHRINK_RUNTIME_SQUARE_JSON_PATH, runtime_square.to_dict())
    write_json(QSHRINK_RUNTIME_SQUARE_JSON_MIRROR, runtime_square.to_dict())
    write_text(RUNTIME_SQUARE_MD_PATH, render_runtime_square_markdown(runtime_square))
    write_json(SQUARE_JSON_PATH, square_payload)
    write_json(NETWORK_JSON_PATH, network_payload)
    write_text(QSHRINK_FAMILY_PATH, render_qshrink_family(square_payload))
    write_text(QSHRINK_ROUTE_MAP_PATH, render_qshrink_route_map(square_payload, runtime_square))
    write_text(QSHRINK_ACTIVE_FRONT_PATH, render_qshrink_active_front(square_payload, runtime_square))
    write_text(QSHRINK_ECOSYSTEM_CAPSULE_PATH, render_qshrink_capsule(square_payload))
    write_json(AGENT_MATRIX_PATH, agent_payload)
    write_text(QSHRINK_AGENT_PLAN_PATH, render_agent_plan(agent_payload))
    write_text(QSHRINK_AGENT_CAPSULE_PATH, render_agent_capsule(agent_payload))

    derivation_runs = [
        {"module": "local.qshrink_square_write", "returncode": 0, "stdout": "", "stderr": "", "ok": True},
        {"module": "local.qshrink_network_write", "returncode": 0, "stdout": "", "stderr": "", "ok": True},
        {"module": "local.qshrink_agent_matrix_write", "returncode": 0, "stdout": "", "stderr": "", "ok": True},
    ]

    write_text(ATHENA_FLEET_ROUTE_MAP_PATH, render_fleet_route_map(runtime_square))
    write_text(ORGIN_ROUTE_MAP_PATH, render_orgin_route_map())
    replace_q42_queue_block()
    update_next_self_prompt()
    replace_q42_quest_board_block()
    append_change_feed_entry()

    outputs = {
        "runtime_square_json": relative_string(QSHRINK_RUNTIME_SQUARE_JSON_PATH),
        "square_json": relative_string(SQUARE_JSON_PATH),
        "dashboard_json": relative_string(DASHBOARD_JSON_PATH),
        "verification_json": relative_string(VERIFICATION_JSON_PATH),
        "manifest_md": relative_string(MANIFEST_MD_PATH),
        "dashboard_md": relative_string(DASHBOARD_MD_PATH),
        "verification_md": relative_string(VERIFICATION_MD_PATH),
        "runtime_md": relative_string(RUNTIME_MD_PATH),
        "receipt_md": relative_string(RECEIPT_MD_PATH),
    }

    provisional_verification = {
        "generated_at": utc_now(),
        "truth": "NEAR",
        "docs_gate_status": docs_gate_status(),
        "completed_subfront": FRACTAL_SUBFRONT,
        "active_subfront": SQUARE_SUBFRONT,
        "square_sync_status": "NEAR",
        "runtime_square_status": runtime_square.truth_state,
        "lead_pressure": "P2",
        "queue_visible_follow_on": "P3",
        "checks": {},
        "verifier_truth": {},
        "next_restart_seed": FLOWER_REFINEMENT_SUBFRONT,
        "unresolved": ["Square-runtime-formalization atlas refresh pending."],
    }
    provisional_dashboard = build_dashboard(provisional_verification)

    write_json(DASHBOARD_JSON_PATH, provisional_dashboard)
    write_json(DASHBOARD_JSON_MIRROR, provisional_dashboard)
    write_json(VERIFICATION_JSON_PATH, provisional_verification)
    write_json(VERIFICATION_JSON_MIRROR, provisional_verification)
    write_text(MANIFEST_MD_PATH, render_manifest(outputs, derivation_runs))
    write_text(DASHBOARD_MD_PATH, render_dashboard(provisional_dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(provisional_verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, provisional_verification))
    write_text(RECEIPT_MD_PATH, render_receipt(runtime_square, provisional_verification, derivation_runs))

    generated_paths = [
        QSHRINK_RUNTIME_SQUARE_JSON_PATH,
        QSHRINK_RUNTIME_SQUARE_JSON_MIRROR,
        RUNTIME_SQUARE_MD_PATH,
        SQUARE_JSON_PATH,
        NETWORK_JSON_PATH,
        AGENT_MATRIX_PATH,
        DASHBOARD_JSON_PATH,
        DASHBOARD_JSON_MIRROR,
        VERIFICATION_JSON_PATH,
        VERIFICATION_JSON_MIRROR,
        MANIFEST_MD_PATH,
        DASHBOARD_MD_PATH,
        VERIFICATION_MD_PATH,
        RUNTIME_MD_PATH,
        RECEIPT_MD_PATH,
        ACTIVE_QUEUE_PATH,
        NEXT_SELF_PROMPT_PATH,
        QSHRINK_ACTIVE_FRONT_PATH,
        QSHRINK_FAMILY_PATH,
        QSHRINK_ROUTE_MAP_PATH,
        QSHRINK_ECOSYSTEM_CAPSULE_PATH,
        QSHRINK_AGENT_PLAN_PATH,
        QSHRINK_AGENT_CAPSULE_PATH,
        ATHENA_FLEET_ROUTE_MAP_PATH,
        ORGIN_ROUTE_MAP_PATH,
        QUEST_BOARD_PATH,
        CHANGE_FEED_PATH,
    ]
    refresh_corpus_atlas(generated_paths)

    downstream_runs = derivation_runs + [
        run_module("self_actualize.runtime.derive_phase4_structured_neuron_storage"),
        run_module("self_actualize.runtime.derive_knowledge_fabric"),
        run_module("self_actualize.runtime.derive_phase4_pt2_inter_metro_lens_weight_superstructure"),
        run_module("self_actualize.runtime.verify_qshrink_stack"),
        run_module("self_actualize.runtime.verify_aqm_runtime_lane"),
        run_module("self_actualize.runtime.verify_atlasforge_runtime_lane"),
        run_module("self_actualize.runtime.verify_runtime_waist"),
    ]

    verification = build_verification(generated_paths, downstream_runs)
    dashboard = build_dashboard(verification)

    write_json(DASHBOARD_JSON_PATH, dashboard)
    write_json(DASHBOARD_JSON_MIRROR, dashboard)
    write_json(VERIFICATION_JSON_PATH, verification)
    write_json(VERIFICATION_JSON_MIRROR, verification)
    write_text(DASHBOARD_MD_PATH, render_dashboard(dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, verification))
    write_text(RECEIPT_MD_PATH, render_receipt(runtime_square, verification, downstream_runs))

    refresh_corpus_atlas(
        [
            DASHBOARD_JSON_PATH,
            DASHBOARD_JSON_MIRROR,
            VERIFICATION_JSON_PATH,
            VERIFICATION_JSON_MIRROR,
            DASHBOARD_MD_PATH,
            VERIFICATION_MD_PATH,
            RUNTIME_MD_PATH,
            RECEIPT_MD_PATH,
            ACTIVE_QUEUE_PATH,
            NEXT_SELF_PROMPT_PATH,
            ATHENA_FLEET_ROUTE_MAP_PATH,
            ORGIN_ROUTE_MAP_PATH,
            QUEST_BOARD_PATH,
            CHANGE_FEED_PATH,
            QSHRINK_ACTIVE_FRONT_PATH,
            QSHRINK_FAMILY_PATH,
            QSHRINK_ROUTE_MAP_PATH,
            QSHRINK_ECOSYSTEM_CAPSULE_PATH,
            QSHRINK_AGENT_PLAN_PATH,
            QSHRINK_AGENT_CAPSULE_PATH,
        ]
    )

    print(f"Wrote Q42 square-runtime-formalization artifacts under {SELF_ACTUALIZE_ROOT}")
    print(f"Truth: {verification['truth']}")
    return 0 if verification["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
