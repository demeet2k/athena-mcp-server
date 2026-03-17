from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .derive_four_agent_57_cycle_orchestration import (
    ACTIVE_QUEUE_PATH,
    ACTIVE_RUN_PATH,
    BUILD_QUEUE_PATH,
    LOOP_STATE_PATH,
    MASTER_REGISTRY_PATH,
    NEXT_SELF_PROMPT_PATH,
    PACKET_ATLAS_PATH,
    PHASE_SEQUENCE,
    QUEST_BOARD_PATH,
    RECEIPT_INDEX_PATH,
    RUNTIME_VERIFICATION_PATH,
    TEMPLE_BOARD_PATH,
    TEMPLE_STATE_PATH,
    WORKSPACE_ROOT,
    docs_gate_payload,
    load_json,
    read_text,
    utc_now,
    write_json,
)


EXPECTED_HALL_IDS = {
    "FA57-Q-FIRE-RESEARCH",
    "FA57-Q-WATER-PLANNER",
    "FA57-Q-AIR-WORKER",
    "FA57-Q-EARTH-PRUNER",
}

EXPECTED_TEMPLE_IDS = {
    "T57-PRIME-ARBITRATION",
    "T57-FIRE-SYNTHESIS-GATE",
    "T57-WATER-QUEST-BINDING",
    "T57-AIR-EXECUTION-LIFT",
    "T57-EARTH-PRUNE-RETURN",
}


def absolute_from_relative(path_str: str) -> Path:
    return WORKSPACE_ROOT / path_str


def heading_ids(text: str, prefix: str) -> list[str]:
    return re.findall(rf"^### ({re.escape(prefix)}[A-Z0-9-]+)", text, re.M)


def marker_block(text: str) -> str:
    match = re.search(r"<!-- FOUR_AGENT_57_CYCLE:START -->(.*?)<!-- FOUR_AGENT_57_CYCLE:END -->", text, re.S)
    return match.group(1) if match else text


def contract_violations(receipt_index_payload: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    for entry in receipt_index_payload.get("entries", []):
        if entry.get("status") != "COMPLETE":
            continue
        artifact_paths = [absolute_from_relative(path) for path in entry.get("required_artifacts", {}).values()]
        receipt_exists = absolute_from_relative(entry["receipt_path"]).exists()
        if not receipt_exists or not all(path.exists() for path in artifact_paths):
            violations.append(entry["loop_id"])
    return violations


def main() -> int:
    docs_gate = docs_gate_payload()
    loop_state_payload = load_json(LOOP_STATE_PATH, {})
    registry_payload = load_json(MASTER_REGISTRY_PATH, {})
    packet_atlas_payload = load_json(PACKET_ATLAS_PATH, {})
    receipt_index_payload = load_json(RECEIPT_INDEX_PATH, {})

    hall_text = read_text(QUEST_BOARD_PATH)
    temple_text = read_text(TEMPLE_BOARD_PATH)
    active_run_text = read_text(ACTIVE_RUN_PATH)
    build_queue_text = read_text(BUILD_QUEUE_PATH)
    active_queue_text = read_text(ACTIVE_QUEUE_PATH)
    next_self_prompt_text = read_text(NEXT_SELF_PROMPT_PATH)
    temple_state_text = read_text(TEMPLE_STATE_PATH)
    current_surface_text = "\n".join(
        [
            marker_block(hall_text),
            marker_block(temple_text),
            marker_block(active_run_text),
            marker_block(build_queue_text),
            marker_block(active_queue_text),
            marker_block(next_self_prompt_text),
            marker_block(temple_state_text),
        ]
    )
    qs64_25_scan_text = current_surface_text.replace("do not invent `QS64-25`", "").replace("do not invent QS64-25", "")

    hall_ids = heading_ids(hall_text, "FA57-Q-")
    temple_ids = heading_ids(temple_text, "T57-")
    per_master_summary = packet_atlas_payload.get("per_master_summary", [])
    packet_counts_ok = all(
        summary.get("depth_counts") == {"1": 4, "2": 16, "3": 64, "4": 256, "5": 1024, "6": 4096}
        and summary.get("active_depth6_count") == 1024
        and summary.get("dormant_depth6_count") == 3072
        for summary in per_master_summary
    )
    live_spine = loop_state_payload.get("live_spine", {})
    completion_violations = contract_violations(receipt_index_payload)

    checks = {
        "docs_gate_blocked": docs_gate["status"] == "BLOCKED",
        "hall_macro_rows_4": len(hall_ids) == 4 and set(hall_ids) == EXPECTED_HALL_IDS,
        "temple_mirror_rows_5": len(temple_ids) == 5 and set(temple_ids) == EXPECTED_TEMPLE_IDS,
        "packet_atlas_depth_counts_ok": packet_counts_ok,
        "packet_atlas_total_entries_ok": packet_atlas_payload.get("packet_entries_total") == 21840,
        "current_sequence_is_five_phase": loop_state_payload.get("current_sequence") == [item["owner"] for item in PHASE_SEQUENCE],
        "loop_state_has_required_fields": all(
            key in loop_state_payload
            for key in [
                "current_cycle",
                "current_phase",
                "current_cycle_owner",
                "live_spine",
                "support_contract",
                "current_restart_seed",
            ]
        ),
        "live_spine_preserved": (
            live_spine.get("active_coordination_membrane") == "Q41 / TQ06"
            and live_spine.get("q42_carried_witness") == "QS64-20 Connectivity-Diagnose-Fractal"
            and live_spine.get("q42_operational_current") == "QS64-21 Connectivity-Refine-Square"
            and live_spine.get("q42_next_hall_seed") == "QS64-22 Connectivity-Refine-Flower"
            and live_spine.get("deeper_receiver") == "TQ04: Bind The Helical Schema Pack To A Runner Contract"
            and live_spine.get("reserve_frontier") == "Q46"
            and live_spine.get("blocked_external_front") == "Q02"
            and live_spine.get("separate_runtime_seed") == "Q50 -> Wave7/Helix.Runtime.Fire.Diagnose"
        ),
        "no_qs64_25_in_current_surfaces": "QS64-25" not in qs64_25_scan_text,
        "no_completed_loops_missing_bundle": not completion_violations,
        "docs_gate_honesty_visible": "BLOCKED" in current_surface_text,
        "q50_visible": "Q50 -> Wave7/Helix.Runtime.Fire.Diagnose" in current_surface_text,
        "q42_visible": "QS64-20 Connectivity-Diagnose-Fractal" in current_surface_text
        and "QS64-21 Connectivity-Refine-Square" in current_surface_text
        and "QS64-22 Connectivity-Refine-Flower" in current_surface_text,
        "registry_rows_5": len(registry_payload.get("rows", [])) == 5,
    }

    truth = "OK" if all(checks.values()) else "NEAR"
    payload = {
        "generated_at": utc_now(),
        "truth": truth,
        "checks": checks,
        "hall_visible_rows": hall_ids,
        "temple_visible_rows": temple_ids,
        "current_cycle": loop_state_payload.get("current_cycle"),
        "current_phase": loop_state_payload.get("current_phase"),
        "current_cycle_owner": loop_state_payload.get("current_cycle_owner"),
        "completion_contract_violations": completion_violations,
    }
    write_json(RUNTIME_VERIFICATION_PATH, payload)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
