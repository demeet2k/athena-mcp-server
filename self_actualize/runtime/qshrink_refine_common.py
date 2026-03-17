from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
GUILD_HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL"
FAMILIES_ROOT = MYCELIUM_ROOT / "nervous_system" / "families"
MANIFESTS_ROOT = MYCELIUM_ROOT / "nervous_system" / "manifests"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"
TEMPLE_ROOT = MYCELIUM_ROOT / "ATHENA TEMPLE"
CAPSULE_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "50_CORPUS_CAPSULES" / "qshrink"
QSHRINK_ECOSYSTEM_ROOT = WORKSPACE_ROOT / "Athena FLEET" / "QSHRINK2_CORPUS_ECOSYSTEM"
DEEP_NETWORK_ROOT = (
    MYCELIUM_ROOT / "dynamic_neural_network" / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)

ATLAS_PATH = QSHRINK_ECOSYSTEM_ROOT / "02_QSHRINK2_CORPUS_ATLAS.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
QSHRINK_CONNECTIVITY_SQUARE_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_square.json"
QSHRINK_CONNECTIVITY_FLOWER_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_flower.json"
QSHRINK_CONNECTIVITY_CLOUD_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_cloud.json"
QSHRINK_CONNECTIVITY_FRACTAL_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_fractal.json"
QSHRINK_REFINEMENT_SQUARE_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_refine_square.json"
QSHRINK_REFINEMENT_FLOWER_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_refine_flower.json"
QSHRINK_REFINEMENT_CLOUD_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_refine_cloud.json"
QSHRINK_REFINEMENT_FRACTAL_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_refine_fractal.json"
QSHRINK_NEXT4_STATE_PATH = SELF_ACTUALIZE_ROOT / "qshrink_next4_state.json"
QSHRINK_NETWORK_INTEGRATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
QSHRINK_AGENT_TASK_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
QSHRINK_RUNTIME_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"
QSHRINK_CAPABILITY_STACK_PATH = SELF_ACTUALIZE_ROOT / "qshrink_capability_stack.json"
FULL_CORPUS_AWAKENING_SOURCE_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "full_corpus_awakening_source_atlas.json"
QSHRINK_AP6D_FULL_CORPUS_INTEGRATION_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "qshrink_ap6d_full_corpus_integration_registry.json"
)
AP6D_AWAKENING_TRANSITION_NOTES_JSON_PATH = SELF_ACTUALIZE_ROOT / "ap6d_awakening_transition_notes.json"
AP6D_AWAKENING_TRANSITION_NOTES_MD_PATH = (
    GUILD_HALL_ROOT / "AP6D_AWAKENING_TRANSITION_NOTES.md"
)

QUEST_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
CHANGE_FEED_PATH = GUILD_HALL_ROOT / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
REQUESTS_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "05_REQUESTS_AND_OFFERS_BOARD.md"
QSHRINK_LOOPED_PLAN_PATH = GUILD_HALL_ROOT / "13_QSHRINK_LOOPED_AGENTIC_PLAN.md"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = MANIFESTS_ROOT / "NEXT_SELF_PROMPT.md"
QSHRINK_ACTIVE_FRONT_PATH = MANIFESTS_ROOT / "QSHRINK_ACTIVE_FRONT.md"
QSHRINK_FAMILY_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use.md"
QSHRINK_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use_route_map.md"
ATHENA_FLEET_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_athena_fleet_route_map.md"
ORGIN_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_orgin_route_map.md"
TEMPLE_STATE_PATH = TEMPLE_ROOT / "MANIFESTS" / "TEMPLE_STATE.md"
TEMPLE_QUEST_BOARD_PATH = TEMPLE_ROOT / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"

FRONT_ID = "Q42"
FRONT_TITLE = "Activate The First QSHRINK Agent Sweep"
CURRENT_CARRIED_WITNESS = "QS64-20 Connectivity-Diagnose-Fractal"
NEXT_TEMPLE_HANDOFF = "TQ04: Bind The Helical Schema Pack To A Runner Contract"
RESERVE_FRONTIER = "Q46"
BLOCKED_EXTERNAL_FRONT = "Q02"
DUAL_TRACK_MODE = "dual_track"
PASS_IDS = {
    "square": "QS64-21 Connectivity-Refine-Square",
    "flower": "QS64-22 Connectivity-Refine-Flower",
    "cloud": "QS64-23 Connectivity-Refine-Cloud",
    "fractal": "QS64-24 Connectivity-Refine-Fractal",
}
NEXT4_CARRIED_WITNESS = CURRENT_CARRIED_WITNESS
HISTORICAL_LOCAL_PROOF = PASS_IDS["fractal"]
OPERATIONAL_CURRENT = PASS_IDS["fractal"]
NEXT_HALL_SEED = None
COMPILED_BUNDLE_MEMBERS = [
    PASS_IDS["square"],
    PASS_IDS["flower"],
    PASS_IDS["cloud"],
    PASS_IDS["fractal"],
]
COMPILED_BUNDLE_TERMINAL = PASS_IDS["fractal"]
COMPILED_BUNDLE_CLOSED = True
NEXT4_AUTHORITY_RECEIPTS = [
    "2026-03-13_qs64_21_connectivity_refine_square.md",
    "2026-03-13_qs64_22_connectivity_refine_flower.md",
    "2026-03-13_qs64_23_connectivity_refine_cloud.md",
    "2026-03-13_qs64_24_connectivity_refine_fractal.md",
]
PASS_ECOSYSTEM_FILES = {
    "square": "15_QSHRINK_CONNECTIVITY_REFINE_SQUARE.md",
    "flower": "16_QSHRINK_CONNECTIVITY_REFINE_FLOWER.md",
    "cloud": "17_QSHRINK_CONNECTIVITY_REFINE_CLOUD.md",
    "fractal": "18_QSHRINK_CONNECTIVITY_REFINE_FRACTAL.md",
}
PASS_CAPSULE_FILES = {
    "square": "08_qshrink_connectivity_refine_square.md",
    "flower": "09_qshrink_connectivity_refine_flower.md",
    "cloud": "10_qshrink_connectivity_refine_cloud.md",
    "fractal": "11_qshrink_connectivity_refine_fractal.md",
}
PASS_RECEIPT_FILES = {
    "square": "2026-03-13_qs64_21_connectivity_refine_square.md",
    "flower": "2026-03-13_qs64_22_connectivity_refine_flower.md",
    "cloud": "2026-03-13_qs64_23_connectivity_refine_cloud.md",
    "fractal": "2026-03-13_qs64_24_connectivity_refine_fractal.md",
}
AUTHORITATIVE_SQUARE_RECEIPT_FILE = PASS_RECEIPT_FILES["square"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def docs_gate_payload() -> dict[str, Any]:
    text = read_text(LIVE_DOCS_GATE_PATH)
    status = "BLOCKED" if "BLOCKED" in text else "UNKNOWN"
    detail = "blocked-by-missing-credentials" if "credentials.json" in text else "status-unknown"
    missing_files = []
    if "Trading Bot/credentials.json" in text:
        missing_files.append("Trading Bot/credentials.json")
    if "Trading Bot/token.json" in text:
        missing_files.append("Trading Bot/token.json")
    return {
        "status": status,
        "truth": "FAIL" if status == "BLOCKED" else "NEAR",
        "detail": detail,
        "confirmed_by": relative_string(LIVE_DOCS_GATE_PATH),
        "missing_files": missing_files,
        "surface_excerpt": "\n".join(text.splitlines()[:12]),
    }


def default_next4_state() -> dict[str, Any]:
    docs_gate = docs_gate_payload()
    return {
        "front_id": FRONT_ID,
        "mode": DUAL_TRACK_MODE,
        "docs_gate_status": docs_gate["status"],
        "docs_gate_truth": docs_gate["truth"],
        "docs_gate_confirmed_by": docs_gate["confirmed_by"],
        "carried_witness": NEXT4_CARRIED_WITNESS,
        "current_carried_witness": NEXT4_CARRIED_WITNESS,
        "historical_local_proof": HISTORICAL_LOCAL_PROOF,
        "operational_current": OPERATIONAL_CURRENT,
        "active_local_subfront": PASS_IDS["fractal"],
        "next_hall_seed": NEXT_HALL_SEED,
        "next_hall_seed_display": "none; do not invent QS64-25",
        "compiled_bundle": {
            "members": COMPILED_BUNDLE_MEMBERS,
            "terminal": COMPILED_BUNDLE_TERMINAL,
            "closed": COMPILED_BUNDLE_CLOSED,
        },
        "deeper_receiver": NEXT_TEMPLE_HANDOFF,
        "next_temple_handoff": NEXT_TEMPLE_HANDOFF,
        "reserve_frontier": RESERVE_FRONTIER,
        "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        "hall_local_bundle_closed": True,
        "carrier_state": "QS64-20 Diagnose = CARRIED_CURRENT",
        "queue_visible_follow_on": "TQ04 runner handoff / Q46 reserve-only",
        "pressure_order": {
            "current": [
                "QS64-20 carried diagnose witness",
                CURRENT_CARRIED_WITNESS,
            ],
            "queue_visible": [
                "TQ04 immediate deeper receiver and Q46 reserve-only frontier",
                NEXT_TEMPLE_HANDOFF,
                RESERVE_FRONTIER,
            ],
            "blocked_external": [
                "P1 Trading Bot docs-gated governance lane",
                BLOCKED_EXTERNAL_FRONT,
            ],
        },
    }


def load_next4_state() -> dict[str, Any]:
    payload = load_json(QSHRINK_NEXT4_STATE_PATH, default_next4_state())
    default_payload = default_next4_state()
    payload.setdefault("front_id", default_payload["front_id"])
    payload.setdefault("mode", default_payload["mode"])
    payload.setdefault("docs_gate_status", default_payload["docs_gate_status"])
    payload.setdefault("docs_gate_truth", default_payload["docs_gate_truth"])
    payload.setdefault("docs_gate_confirmed_by", default_payload["docs_gate_confirmed_by"])
    payload.setdefault("carried_witness", default_payload["carried_witness"])
    payload.setdefault("current_carried_witness", default_payload["current_carried_witness"])
    payload.setdefault("historical_local_proof", default_payload["historical_local_proof"])
    payload.setdefault("operational_current", default_payload["operational_current"])
    payload.setdefault("active_local_subfront", default_payload["active_local_subfront"])
    payload.setdefault("next_hall_seed", default_payload["next_hall_seed"])
    payload.setdefault("next_hall_seed_display", default_payload["next_hall_seed_display"])
    compiled_bundle = payload.setdefault("compiled_bundle", {})
    default_bundle = default_payload["compiled_bundle"]
    compiled_bundle.setdefault("members", default_bundle["members"])
    compiled_bundle.setdefault("terminal", default_bundle["terminal"])
    compiled_bundle.setdefault("closed", default_bundle["closed"])
    payload.setdefault("deeper_receiver", default_payload["deeper_receiver"])
    payload.setdefault("next_temple_handoff", default_payload["next_temple_handoff"])
    payload.setdefault("reserve_frontier", default_payload["reserve_frontier"])
    payload.setdefault("blocked_external_front", default_payload["blocked_external_front"])
    payload.setdefault("hall_local_bundle_closed", default_payload["hall_local_bundle_closed"])
    payload.setdefault("carrier_state", default_payload["carrier_state"])
    payload.setdefault("queue_visible_follow_on", default_payload["queue_visible_follow_on"])
    pressure_order = payload.setdefault("pressure_order", {})
    default_pressure_order = default_payload["pressure_order"]
    pressure_order.setdefault("current", default_pressure_order["current"])
    pressure_order.setdefault("queue_visible", default_pressure_order["queue_visible"])
    pressure_order.setdefault("blocked_external", default_pressure_order["blocked_external"])
    return payload


def atlas_metrics() -> dict[str, Any]:
    atlas = load_json(
        ATLAS_PATH,
        {"summary": {"total_files": 0, "total_bytes": 0, "duplicate_groups_count": 0, "duplicate_savings_bytes": 0}},
    )
    return atlas.get("summary", {})


def ecosystem_output_path(pass_name: str) -> Path:
    return QSHRINK_ECOSYSTEM_ROOT / PASS_ECOSYSTEM_FILES[pass_name]


def capsule_output_path(pass_name: str) -> Path:
    return CAPSULE_ROOT / PASS_CAPSULE_FILES[pass_name]


def receipt_output_path(pass_name: str) -> Path:
    return RECEIPTS_ROOT / PASS_RECEIPT_FILES[pass_name]


def refinement_output_path(pass_name: str) -> Path:
    mapping = {
        "square": QSHRINK_REFINEMENT_SQUARE_PATH,
        "flower": QSHRINK_REFINEMENT_FLOWER_PATH,
        "cloud": QSHRINK_REFINEMENT_CLOUD_PATH,
        "fractal": QSHRINK_REFINEMENT_FRACTAL_PATH,
    }
    return mapping[pass_name]


def route_targets() -> list[dict[str, str]]:
    return [
        {"body": "QSHRINK", "target": relative_string(QSHRINK_ROUTE_MAP_PATH)},
        {"body": "Athena FLEET", "target": relative_string(ATHENA_FLEET_ROUTE_MAP_PATH)},
        {"body": "ORGIN", "target": relative_string(ORGIN_ROUTE_MAP_PATH)},
        {"body": "Quest board", "target": relative_string(QUEST_BOARD_PATH)},
        {"body": "Active queue", "target": relative_string(ACTIVE_QUEUE_PATH)},
        {"body": "QSHRINK active front", "target": relative_string(QSHRINK_ACTIVE_FRONT_PATH)},
        {"body": "Next self prompt", "target": relative_string(NEXT_SELF_PROMPT_PATH)},
        {"body": "Temple state", "target": relative_string(TEMPLE_STATE_PATH)},
    ]


def render_qshrink_ecosystem_readme() -> str:
    metrics = atlas_metrics()
    total_files = metrics.get("total_files", 0)
    total_bytes = metrics.get("total_bytes", 0)
    total_gb = total_bytes / (1024**3) if total_bytes else 0.0
    return "\n".join(
        [
            "# QSHRINK2 Corpus Ecosystem",
            "",
            "This folder is the live fleet-side integration shell for QSHRINK2 inside the Athena corpus ecosystem.",
            "",
            f"- Files scanned: `{total_files}`",
            f"- Total size: `{total_gb:.2f} GB`",
            "- Docs gate: `BLOCKED`",
            "",
            "## Generated Surfaces",
            "",
            "- `01_FULL_FRAMEWORK_SYNTHESIS.md`: deep corpus synthesis plus the second QSHRINK pass.",
            "- `02_QSHRINK2_CORPUS_ATLAS.json`: full file-by-file atlas with root-cell classification.",
            "- `03_QSHRINK2_PRUNING_LEDGER.md`: compaction lanes, duplicate pressure, and pruning law.",
            "- `04_QSHRINK2_COMPACTION_MANIFEST.json`: machine-readable compaction summary.",
            "- `05_QSHRINK_DEBUG_LEDGER.md`: runtime fixes, verification state, and open risks.",
            "- `06_QSHRINK_MAXIMUM_CAPACITY_USE_CASE_ATLAS.md`: mapped use cases across runtime, doctrine, and fleet surfaces.",
            "- `07_QSHRINK_TOOLKIT_HANDBOOK.md`: toolkit map for geometry, operators, swarm, metro, repair, and Chapter 11.",
            "- `08_QSHRINK_SKILL_ROUTING_MATRIX.md`: first-wave through third-wave skill bindings and handoff contracts.",
            "- `09_QSHRINK_HOLOGRAPHIC_ARTIFACT_SCHEMA.json`: machine-readable artifact contract for future QSHRINK outputs.",
            "- `10_QSHRINK_COMPACTION_CONTRACT.json`: machine-readable compaction law for retain, regenerate, dedupe, archive, and promote-live.",
            "- `11_QSHRINK_CORE_CORRIDOR_CONTRACT.md`: square-law core corridor contract across QSHRINK, Athena FLEET, Trading Bot, Athena OS runtime, and the secondary ORGIN seed leg.",
            "- `12_QSHRINK_CORE_CORRIDOR_METRO.md`: flower-law cadence and handoff metro across QSHRINK, Athena FLEET, Trading Bot, Athena OS runtime, Hall, and the secondary ORGIN seed leg.",
            "- `13_QSHRINK_CORE_CORRIDOR_CLOUD.md`: cloud-law ranking witness that inherits local Flower closure, ranks corridor pressure honestly, and keeps Docs blocking explicit.",
            "- `14_QSHRINK_CORE_CORRIDOR_FRACTAL.md`: fractal-law recursive carrythrough that preserves the blocked Docs gate, carries runtime and ORGIN as distinct recursive crossings, and hands the deeper pressure to `TQ04`.",
            "- `15_QSHRINK_CONNECTIVITY_REFINE_SQUARE.md`: structural precedence membrane that separates Hall-local seed, Temple handoff, reserve frontier, and blocked external front.",
            "- `16_QSHRINK_CONNECTIVITY_REFINE_FLOWER.md`: cadence-law witness that fixes the four NEXT^4 rails across local refinement, Temple handoff, reserve growth, and blocker overlay.",
            "- `17_QSHRINK_CONNECTIVITY_REFINE_CLOUD.md`: ranked-pressure witness that keeps the Docs blocker pinned, promotes the runner handoff gap, and preserves ORGIN mirror deepening as queue-visible.",
            "- `18_QSHRINK_CONNECTIVITY_REFINE_FRACTAL.md`: recursive theorem witness that closes the Hall-local refine bundle on `QS64-24` and hands immediate deeper execution to `TQ04` without inventing `QS64-25`.",
            "",
            "## Rerun",
            "",
            "```powershell",
            "python .\\build_qshrink2_corpus_ecosystem.py",
            "```",
        ]
    ) + "\n"
