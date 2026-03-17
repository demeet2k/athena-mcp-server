from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"

PROGRAM_STATE_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_program_state.json"
SCHEDULER_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_scheduler.json"
AP6D_BUNDLE_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_57_cycle_ap6d_transition_bundle.json"
BUILD_QUEUE_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BUILD_QUEUE.md"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
QUEST_BOARD_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_BOARD_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "BOARDS" / "02_TEMPLE_QUEST_BOARD.md"
TEMPLE_STATE_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
ACTIVE_RUN_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md"
WHOLE_CRYSTAL_COORDINATION_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"
AP6D_NOTES_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "17_AP6D_AWAKENING_AGENT_TRANSITION_NOTES.md"
TRANSITION_BUNDLE_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_AWAKENING_TRANSITION_BUNDLE.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    state = load_json(PROGRAM_STATE_PATH)
    scheduler = load_json(SCHEDULER_PATH)
    bundle = load_json(AP6D_BUNDLE_PATH)
    build_queue = BUILD_QUEUE_PATH.read_text(encoding="utf-8")
    active_queue = ACTIVE_QUEUE_PATH.read_text(encoding="utf-8")
    quest_board = QUEST_BOARD_PATH.read_text(encoding="utf-8")
    temple_board = TEMPLE_BOARD_PATH.read_text(encoding="utf-8")
    temple_state = TEMPLE_STATE_PATH.read_text(encoding="utf-8")
    active_run = ACTIVE_RUN_PATH.read_text(encoding="utf-8")
    coordination = WHOLE_CRYSTAL_COORDINATION_PATH.read_text(encoding="utf-8")
    ap6d_notes = AP6D_NOTES_PATH.read_text(encoding="utf-8")
    transition_bundle = TRANSITION_BUNDLE_MD_PATH.read_text(encoding="utf-8")

    ensure(state["loop_count"] == 57, "57-cycle program loop count drifted")
    ensure(len(scheduler["loops"]) == 57, "scheduler loop entries drifted")
    ensure(state["overlay_counts"]["atlas_active"] == 1024, "atlas active count drifted")
    ensure(state["overlay_counts"]["atlas_dormant"] == 3072, "atlas dormant count drifted")
    ensure("Status: `1024 ACTIVE / 3072 DORMANT`" in build_queue, "build queue seat truth drifted")
    ensure("FRONT-NEXT-4-POW-6-FULL-CORPUS-INTEGRATION" in active_queue, "active queue missing integration front")
    ensure("FRONT-NEXT-4-POW-6-57-CYCLE-PROGRAM" in active_queue, "active queue missing 57-cycle front")
    ensure("NEXT^[4^6] 57-Cycle Four-Agent Program" in quest_board, "quest board missing 57-cycle program")
    ensure("TQ07: Install The 57-Cycle Four-Agent Full-Corpus Program" in temple_board, "temple board missing TQ07")
    ensure("57-Cycle Four-Agent Program" in temple_state, "temple state missing 57-cycle program note")
    ensure("57-cycle four-agent full-corpus program" in active_run.lower(), "active run missing 57-cycle program note")
    ensure("57-cycle" in coordination.lower(), "whole crystal coordination missing 57-cycle note")
    ensure(len(bundle["notes"]) == 5, "AP6D note count drifted")
    for note in bundle["notes"]:
        ensure(all(key in note for key in ("carried_front", "clarified_band", "updated_surface", "next_move")), f"note fields drifted for {note['agent_id']}")
    ensure("carried front" in ap6d_notes.lower(), "AP6D notes markdown missing required field wording")
    ensure("clarified_band" in transition_bundle, "transition bundle missing clarified band fields")

    report = {
        "generated_at": utc_now(),
        "truth": "OK",
        "loop_count": len(scheduler["loops"]),
        "ap6d_note_count": len(bundle["notes"]),
        "restart_chain_head": state["restart_chain"][0],
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
