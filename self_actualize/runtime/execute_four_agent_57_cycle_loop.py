from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .derive_four_agent_57_cycle_orchestration import (
    ARTIFACTS_ROOT,
    CHARTER_PATH,
    LOOP_STATE_PATH,
    MASTER_REGISTRY_PATH,
    PACKET_ATLAS_PATH,
    PHASE_SEQUENCE,
    RECEIPT_INDEX_PATH,
    VERIFICATION_PATH,
    SUPPORT_CONTRACT,
    artifact_completion_map,
    build_verification,
    current_spine_fields,
    cycle_artifact_bundle,
    cycle_artifact_paths,
    generate_packet_atlas,
    hall_quest_id,
    live_state,
    load_json,
    loop_state as seed_loop_state,
    master_registry,
    path_exists,
    phase_metadata,
    read_text,
    relative_string,
    temple_mirror_id,
    update_control_surfaces,
    utc_now,
    write_json,
)


def seed_if_missing() -> None:
    required_paths = [LOOP_STATE_PATH, MASTER_REGISTRY_PATH, PACKET_ATLAS_PATH, RECEIPT_INDEX_PATH, CHARTER_PATH]
    if all(path_exists(path) for path in required_paths):
        return
    from .derive_four_agent_57_cycle_orchestration import main as seed_overlay

    seed_overlay()


def contract_path(loop_id: str) -> Path:
    return ARTIFACTS_ROOT / loop_id / f"{loop_id.lower()}_contract.json"


def current_hall_quest_id(owner: str) -> str | None:
    if owner == "FA57-PRIME":
        return None
    return hall_quest_id(owner)


def required_artifact_contract(loop_state_payload: dict[str, Any]) -> dict[str, Any]:
    loop_id = loop_state_payload["current_cycle"]
    completion = artifact_completion_map(loop_id)
    missing = [name for name, exists in completion.items() if not exists]
    payload = {
        "generated_at": utc_now(),
        "truth": "OK" if not missing else "NEAR",
        "loop_id": loop_id,
        "current_phase": loop_state_payload["current_phase"],
        "current_owner": loop_state_payload["current_cycle_owner"],
        "phase_sequence": [item["phase"] for item in PHASE_SEQUENCE],
        "support_contract": SUPPORT_CONTRACT,
        "required_artifacts": cycle_artifact_bundle(loop_id),
        "artifact_completion": completion,
        "missing_artifacts": missing,
        "promotion_ready": not missing,
        "live_spine": loop_state_payload["live_spine"],
    }
    write_json(contract_path(loop_id), payload)
    return payload


def update_current_entry(
    receipt_index_payload: dict[str, Any],
    loop_state_payload: dict[str, Any],
    contract_payload: dict[str, Any],
) -> dict[str, Any]:
    loop_id = loop_state_payload["current_cycle"]
    entry = next(item for item in receipt_index_payload["entries"] if item["loop_id"] == loop_id)
    receipt_absolute = LOOP_STATE_PATH.parents[1] / entry["receipt_path"]
    entry["current_phase"] = loop_state_payload["current_phase"]
    entry["required_artifacts"] = contract_payload["required_artifacts"]
    entry["completed_artifacts"] = contract_payload["artifact_completion"]
    entry["completion_contract_met"] = contract_payload["promotion_ready"] and receipt_absolute.exists()
    entry["actual_receipt_exists"] = receipt_absolute.exists()
    return entry


def current_phase_index(phase_id: str) -> int:
    for index, item in enumerate(PHASE_SEQUENCE):
        if item["phase"] == phase_id:
            return index
    return 0


def refresh_registry_and_atlas(loop_state_payload: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    spine = current_spine_fields(live_state())
    loop_state_payload["live_spine"] = spine
    rows = master_registry(spine, current_owner=loop_state_payload["current_cycle_owner"])
    atlas = generate_packet_atlas(spine, rows, loop_id=loop_state_payload["current_cycle"])
    write_json(MASTER_REGISTRY_PATH, {"generated_at": utc_now(), "truth": "OK", "rows": rows})
    write_json(PACKET_ATLAS_PATH, atlas)
    return rows, atlas


def mark_pending(loop_state_payload: dict[str, Any], entry: dict[str, Any], contract_payload: dict[str, Any]) -> str:
    missing = contract_payload["missing_artifacts"]
    loop_state_payload["current_cycle_status"] = "ACTIVE_PENDING_ARTIFACTS"
    loop_state_payload["current_cycle_contract"] = relative_string(contract_path(loop_state_payload["current_cycle"]))
    loop_state_payload["current_cycle_artifacts"] = contract_payload["required_artifacts"]
    loop_state_payload["current_cycle_missing_artifacts"] = missing
    loop_state_payload["current_restart_seed"] = (
        f"{loop_state_payload['current_cycle']} blocked at {loop_state_payload['current_phase']} "
        f"until {', '.join(missing)} land"
    )
    entry["status"] = "ACTIVE_PENDING_ARTIFACTS"
    entry["completion_contract_met"] = False
    return "pending_artifacts"


def advance_phase(loop_state_payload: dict[str, Any], receipt_index_payload: dict[str, Any], entry: dict[str, Any]) -> str:
    index = current_phase_index(loop_state_payload["current_phase"])
    if index < len(PHASE_SEQUENCE) - 1:
        next_phase = PHASE_SEQUENCE[index + 1]
        loop_state_payload["current_phase"] = next_phase["phase"]
        loop_state_payload["current_phase_index"] = index + 1
        loop_state_payload["current_cycle_owner"] = next_phase["owner"]
        loop_state_payload["current_hall_quest_id"] = current_hall_quest_id(next_phase["owner"])
        loop_state_payload["current_temple_mirror_id"] = temple_mirror_id(next_phase["owner"])
        loop_state_payload["current_cycle_status"] = "ACTIVE"
        loop_state_payload["current_cycle_missing_artifacts"] = []
        loop_state_payload["current_restart_seed"] = (
            f"{loop_state_payload['current_cycle']} -> {next_phase['owner']} -> {phase_metadata(next_phase['phase'])['label']}"
        )
        entry["status"] = "ACTIVE"
        entry["current_phase"] = next_phase["phase"]
        return "advanced_phase"
    return "final_phase"


def complete_or_hold_final(
    loop_state_payload: dict[str, Any],
    receipt_index_payload: dict[str, Any],
    entry: dict[str, Any],
) -> str:
    receipt_absolute = LOOP_STATE_PATH.parents[1] / entry["receipt_path"]
    if not receipt_absolute.exists():
        loop_state_payload["current_cycle_status"] = "ACTIVE_PENDING_RECEIPT"
        loop_state_payload["current_restart_seed"] = (
            f"{loop_state_payload['current_cycle']} waiting for receipt {entry['receipt_path']}"
        )
        entry["status"] = "ACTIVE_PENDING_RECEIPT"
        entry["actual_receipt_exists"] = False
        entry["completion_contract_met"] = False
        return "pending_receipt"

    entry["status"] = "COMPLETE"
    entry["actual_receipt_exists"] = True
    entry["completion_contract_met"] = True
    entry["completed_at"] = utc_now()
    current_number = entry["cycle_number"]
    next_entry = next((item for item in receipt_index_payload["entries"] if item["cycle_number"] == current_number + 1), None)
    if next_entry is None:
        loop_state_payload["current_cycle_status"] = "COMPLETE"
        loop_state_payload["current_restart_seed"] = "FA57 complete -> reopen highest-yield unblocked next wave"
        return "complete_program"

    next_phase = PHASE_SEQUENCE[0]
    next_entry["status"] = "ACTIVE"
    next_entry["current_phase"] = next_phase["phase"]
    loop_state_payload["current_cycle"] = next_entry["loop_id"]
    loop_state_payload["current_phase"] = next_phase["phase"]
    loop_state_payload["current_phase_index"] = 0
    loop_state_payload["current_cycle_owner"] = next_phase["owner"]
    loop_state_payload["current_hall_quest_id"] = current_hall_quest_id(next_phase["owner"])
    loop_state_payload["current_temple_mirror_id"] = temple_mirror_id(next_phase["owner"])
    loop_state_payload["current_cycle_status"] = "ACTIVE"
    loop_state_payload["current_restart_seed"] = (
        f"{next_entry['loop_id']} -> {next_phase['owner']} -> {phase_metadata(next_phase['phase'])['label']}"
    )
    loop_state_payload["current_cycle_artifacts"] = cycle_artifact_bundle(next_entry["loop_id"])
    loop_state_payload["current_cycle_contract"] = relative_string(contract_path(next_entry["loop_id"]))
    return "advanced_cycle"


def write_runtime_state(
    loop_state_payload: dict[str, Any],
    receipt_index_payload: dict[str, Any],
    registry_rows: list[dict[str, Any]],
    packet_atlas: dict[str, Any],
) -> None:
    write_json(LOOP_STATE_PATH, loop_state_payload)
    write_json(RECEIPT_INDEX_PATH, receipt_index_payload)
    update_control_surfaces(loop_state_payload["live_spine"], loop_state_payload)
    verification_payload = build_verification(
        loop_state_payload["live_spine"],
        registry_rows,
        packet_atlas,
        receipt_index_payload,
        loop_state_payload,
    )
    write_json(VERIFICATION_PATH, verification_payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Advance or refresh the four-agent 57-cycle loop state.")
    parser.add_argument("--status-only", action="store_true", help="Refresh the current loop contract without promoting phase or cycle.")
    args = parser.parse_args()

    seed_if_missing()

    loop_state_payload = load_json(LOOP_STATE_PATH, {})
    receipt_index_payload = load_json(RECEIPT_INDEX_PATH, {})
    contract_payload = required_artifact_contract(loop_state_payload)
    loop_state_payload["current_cycle_contract"] = relative_string(contract_path(loop_state_payload["current_cycle"]))
    loop_state_payload["current_cycle_artifacts"] = contract_payload["required_artifacts"]

    entry = update_current_entry(receipt_index_payload, loop_state_payload, contract_payload)

    result = "status_refreshed"
    if not args.status_only:
        if contract_payload["missing_artifacts"]:
            result = mark_pending(loop_state_payload, entry, contract_payload)
        else:
            phase_result = advance_phase(loop_state_payload, receipt_index_payload, entry)
            if phase_result == "final_phase":
                result = complete_or_hold_final(loop_state_payload, receipt_index_payload, entry)
            else:
                result = phase_result

    registry_rows, packet_atlas = refresh_registry_and_atlas(loop_state_payload)
    write_runtime_state(loop_state_payload, receipt_index_payload, registry_rows, packet_atlas)

    print(f"Loop: {loop_state_payload['current_cycle']}")
    print(f"Phase: {loop_state_payload['current_phase']}")
    print(f"Owner: {loop_state_payload['current_cycle_owner']}")
    print(f"Result: {result}")
    if contract_payload["missing_artifacts"]:
        print("Missing artifacts:")
        for name in contract_payload["missing_artifacts"]:
            print(f"- {name}: {contract_payload['required_artifacts'][name]}")
    else:
        print("All seven support artifacts exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
