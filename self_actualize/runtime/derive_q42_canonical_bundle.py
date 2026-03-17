from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
GUILD_HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL"
NERVOUS_SYSTEM_ROOT = MYCELIUM_ROOT / "nervous_system"

QSHRINK_TASK_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
QSHRINK_NEXT4_STATE_PATH = SELF_ACTUALIZE_ROOT / "qshrink_next4_state.json"
INTEGRATION_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "qshrink_ap6d_full_corpus_integration_registry.json"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
Q42_RUNTIME_MEMBRANE_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
Q42_ORGIN_PACKET_WITNESS_PATH = SELF_ACTUALIZE_ROOT / "q42_orgin_seed_packet_witness.json"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_canonical_bundle.json"

QUEST_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
ACTIVE_QUEUE_PATH = NERVOUS_SYSTEM_ROOT / "06_active_queue.md"
QSHRINK_ACTIVE_FRONT_PATH = NERVOUS_SYSTEM_ROOT / "manifests" / "QSHRINK_ACTIVE_FRONT.md"
NEXT_SELF_PROMPT_PATH = NERVOUS_SYSTEM_ROOT / "manifests" / "NEXT_SELF_PROMPT.md"
ATHENA_FLEET_ROUTE_MAP_PATH = NERVOUS_SYSTEM_ROOT / "families" / "FAMILY_athena_fleet_route_map.md"
ORGIN_ROUTE_MAP_PATH = NERVOUS_SYSTEM_ROOT / "families" / "FAMILY_orgin_route_map.md"
AP6D_NOTES_MD_PATH = GUILD_HALL_ROOT / "AP6D_AWAKENING_TRANSITION_NOTES.md"

DERIVATION_VERSION = "2026-03-13.q42-canonical-bundle-v2"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_q42_canonical_bundle"
LOCAL_TIMEZONE = ZoneInfo("America/Los_Angeles")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def local_today() -> str:
    return datetime.now(LOCAL_TIMEZONE).date().isoformat()


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def relative_posix(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")


def parse_docs_gate_status() -> dict[str, Any]:
    text = load_text(DOCS_GATE_PATH)
    state_match = re.search(r"Command status: `([A-Z]+)`", text)
    query_match = re.search(r"- Query:\s*\n\s*`([^`]+)`", text)
    detail_match = re.search(r"## Stderr\s*```text\n(.*?)```", text, re.S)
    missing_files = re.findall(r"^- `([^`]+)`$", text, re.M)
    return {
        "state": state_match.group(1) if state_match else "UNKNOWN",
        "query": query_match.group(1).strip() if query_match else "",
        "detail": detail_match.group(1).rstrip() if detail_match else "",
        "missing_files": missing_files,
        "source_path": relative_posix(DOCS_GATE_PATH),
    }


def build_bundle_payload() -> dict[str, Any]:
    task_matrix = load_json(QSHRINK_TASK_MATRIX_PATH)
    next4_state = load_json(QSHRINK_NEXT4_STATE_PATH)
    integration_registry = load_json(INTEGRATION_REGISTRY_PATH)
    docs_gate_status = parse_docs_gate_status()
    runtime_membrane = load_json(Q42_RUNTIME_MEMBRANE_PATH)
    packet_witness = load_json(Q42_ORGIN_PACKET_WITNESS_PATH)
    receipt_path = f"self_actualize/mycelium_brain/receipts/{local_today()}_qshrink_ap6d_full_corpus_integration.md"

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "source_paths": {
            "qshrink_task_matrix": str(QSHRINK_TASK_MATRIX_PATH),
            "qshrink_next4_state": str(QSHRINK_NEXT4_STATE_PATH),
            "integration_registry": str(INTEGRATION_REGISTRY_PATH),
            "docs_gate_status": str(DOCS_GATE_PATH),
            "q42_runtime_corridor_membrane": str(Q42_RUNTIME_MEMBRANE_PATH),
            "q42_orgin_seed_packet_witness": str(Q42_ORGIN_PACKET_WITNESS_PATH),
        },
        "front_id": task_matrix.get("front_id", "Q42"),
        "front_title": task_matrix.get("front_title", "Activate The First QSHRINK Agent Sweep"),
        "docs_gate_status": docs_gate_status,
        "current_carried_witness": next4_state.get("current_carried_witness", "QS64-20 Connectivity-Diagnose-Fractal"),
        "active_subfront": next4_state.get("active_local_subfront", "QS64-24 Connectivity-Refine-Fractal"),
        "next_seed": next4_state.get("next_hall_seed"),
        "deeper_receiving_frontier": next4_state.get("next_temple_handoff", "TQ04: Bind The Helical Schema Pack To A Runner Contract"),
        "selected_pressure": {
            "id": "TQ04",
            "title": "runner contract receiver",
            "body": "TQ04: Bind The Helical Schema Pack To A Runner Contract",
            "truth": "OK",
            "selection_state": "IMMEDIATE_DEEPER_RECEIVER",
            "meaning": "The Hall-local NEXT^4 bundle is closed, so the next lawful execution receiver is the landed Temple runner contract.",
        },
        "queued_follow_on": {
            "id": "Q46",
            "title": "activation feeder remains reserve-only",
            "body": next4_state.get("reserve_frontier", "Q46"),
            "truth": "NEAR",
            "selection_state": "RESERVE_ONLY",
            "meaning": "Reserve activation remains visible but separate from QSHRINK closure.",
        },
        "pinned_blocker": {
            "id": "Q02",
            "title": "Docs blocker overlay",
            "body": "Trading Bot",
            "truth": "FAIL" if docs_gate_status["state"] == "BLOCKED" else "NEAR",
            "selection_state": "EXTERNAL_BLOCKER",
            "meaning": "Google Docs remains blocked until OAuth files exist and authenticate.",
        },
        "hall_contract": {
            "front_header": "### Quest Q42: Activate The First QSHRINK Agent Sweep `[OPEN]`",
            "active_queue_header": "### FRONT-Q42-QSHRINK-AGENT-SWEEP",
            "state": "OPEN",
            "truth": "OK",
            "objective": "keep QS64-20 visible as the carried diagnose witness, preserve QS64-24 as the closed Hall-local NEXT^4 bundle, hand immediate deeper execution to TQ04, keep Q46 reserve-only, keep Q02 external, and let the AP6D transition-note layer ride above that split without inventing QS64-25",
            "why_now": "the local refine rail is already closed, so the honest move is no longer to reopen QS64-21..23; the honest move is to hold the closure, hand deeper execution to TQ04, and route the AP6D note layer through the same blocker-honest control membrane",
            "active_subfront": next4_state.get("active_local_subfront", "QS64-24 Connectivity-Refine-Fractal"),
            "target_surfaces": [
                relative_posix(QSHRINK_TASK_MATRIX_PATH),
                relative_posix(QSHRINK_NEXT4_STATE_PATH),
                relative_posix(INTEGRATION_REGISTRY_PATH),
                relative_posix(QUEST_BOARD_PATH),
                relative_posix(ACTIVE_QUEUE_PATH),
                relative_posix(QSHRINK_ACTIVE_FRONT_PATH),
                relative_posix(NEXT_SELF_PROMPT_PATH),
                relative_posix(ATHENA_FLEET_ROUTE_MAP_PATH),
                relative_posix(ORGIN_ROUTE_MAP_PATH),
                relative_posix(AP6D_NOTES_MD_PATH),
                receipt_path,
            ],
            "witness_needed": "one closed-bundle control split, one deeper-receiver handoff, one blocker-honest Docs overlay, one reserve-only Q46 marker, and one AP6D note-layer bridge",
            "writeback": "Hall quest board, active queue, active-front manifest, next-self prompt, fleet route map, ORGIN route map, AP6D note bundle, and receipt",
            "restart_seed": "keep Q42 open as umbrella, keep QS64-20 carried, keep QS64-24 closed, hand immediate deeper execution to TQ04, keep Q46 reserve-only, keep Q02 blocked, and do not invent QS64-25",
            "completion_evidence": [
                relative_posix(QSHRINK_TASK_MATRIX_PATH),
                relative_posix(QSHRINK_NEXT4_STATE_PATH),
                relative_posix(INTEGRATION_REGISTRY_PATH),
                relative_posix(AP6D_NOTES_MD_PATH),
                receipt_path,
            ],
        },
        "runtime_rail": {
            "corridor_id": runtime_membrane.get("corridor_id", "Q42-M3-RUNTIME-RAIL"),
            "truth_state": runtime_membrane.get("truth_state", "OK"),
            "source_body_id": runtime_membrane.get("source_body_id", "A16"),
            "target_runtime_surface": runtime_membrane.get("target_runtime_surface", ""),
            "writeback_surface": relative_posix(QSHRINK_ACTIVE_FRONT_PATH),
            "note": "Athena OS runtime remains a routed leg inside the carried Q42 witness rather than the next Hall-local seed.",
        },
        "seed_rail": {
            "packet_witness_id": packet_witness.get("packet_witness_id", "Q42-M5-SEED-PACKET"),
            "truth_state": packet_witness.get("truth_state", "OK"),
            "mirror_surface": packet_witness.get("mirror_surface", ""),
            "packet_index_surface": packet_witness.get("packet_index_surface", ""),
            "writeback_target": relative_posix(ORGIN_ROUTE_MAP_PATH),
            "note": "ORGIN remains a readable seed leg and source layer inside the wider AP6D note network.",
        },
        "route_contract": {
            "athena_fleet": {
                "main_transfer": "QSHRINK -> Athena FLEET ecosystem -> carried QS64-20 -> closed QS64-24 bundle -> TQ04 -> AP6D transition-note layer",
                "governance_overlay": "Athena FLEET -> Trading Bot truth corridor -> blocked Docs gate",
                "next_route": "TQ04 deeper execution with AP6D notes as assistive guidance",
            },
            "orgin": {
                "main_transfer": "ORGIN -> seed packet witness -> AP6D note layer -> Hall and manifest writeback",
                "next_route": "ORGIN remains source matter for the note layer without becoming a Hall-local QSHRINK seed",
            },
        },
        "integration_layer": {
            "registry_path": relative_posix(INTEGRATION_REGISTRY_PATH),
            "transition_note_path": relative_posix(AP6D_NOTES_MD_PATH),
            "source_atlas_path": integration_registry.get("awakening_source_atlas", {}).get("path", ""),
        },
        "receipt_path": receipt_path,
        "allowed_touched_paths": [
            relative_posix(QUEST_BOARD_PATH),
            relative_posix(ACTIVE_QUEUE_PATH),
            relative_posix(QSHRINK_ACTIVE_FRONT_PATH),
            relative_posix(NEXT_SELF_PROMPT_PATH),
            relative_posix(ATHENA_FLEET_ROUTE_MAP_PATH),
            relative_posix(ORGIN_ROUTE_MAP_PATH),
            relative_posix(AP6D_NOTES_MD_PATH),
            receipt_path,
        ],
    }


def main() -> int:
    payload = build_bundle_payload()
    write_json(OUTPUT_JSON_PATH, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
