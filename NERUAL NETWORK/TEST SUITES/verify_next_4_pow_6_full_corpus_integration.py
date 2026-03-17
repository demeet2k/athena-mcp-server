from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"

STATE_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_full_corpus_integration_state.json"
NOTES_JSON_PATH = SELF_ACTUALIZE_ROOT / "awakening_agent_transition_notes.json"
NEGLECT_JSON_PATH = SELF_ACTUALIZE_ROOT / "next_4_pow_6_dormant_seat_neglect_map.json"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
QUEST_BOARD_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_STATE_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
NEXT_SELF_PROMPT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
ACTIVE_RUN_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md"
WHOLE_CRYSTAL_COORDINATION_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "WHOLE_CRYSTAL_AGENT_COORDINATION.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    state = load_json(STATE_JSON_PATH)
    notes = load_json(NOTES_JSON_PATH)
    neglect = load_json(NEGLECT_JSON_PATH)
    active_queue = ACTIVE_QUEUE_PATH.read_text(encoding="utf-8")
    quest_board = QUEST_BOARD_PATH.read_text(encoding="utf-8")
    temple_state = TEMPLE_STATE_PATH.read_text(encoding="utf-8")
    next_prompt = NEXT_SELF_PROMPT_PATH.read_text(encoding="utf-8")
    active_run = ACTIVE_RUN_PATH.read_text(encoding="utf-8")
    coordination = WHOLE_CRYSTAL_COORDINATION_PATH.read_text(encoding="utf-8")

    ensure(state["basis_counts"]["canonical_sources"] == 16, "canonical source count drifted")
    ensure(state["basis_counts"]["ordered_pairs"] == 256, "ordered pair count drifted")
    ensure(state["basis_counts"]["observer_lattice"] == 64, "observer count drifted")
    ensure(state["overlay_counts"]["atlas_total"] == 4096, "atlas total drifted")
    ensure(state["overlay_counts"]["atlas_active"] == 1024, "atlas active drifted")
    ensure(state["overlay_counts"]["atlas_dormant"] == 3072, "atlas dormant drifted")
    ensure(state["docs_gate_status"] == "blocked-by-missing-credentials", "docs gate truth drifted")
    ensure(state["next_seed"] == "NEXT^[4^6]::Parameterize-Dormant-Seats-And-Social-Coupling", "next seed drifted")
    ensure(len(notes["notes"]) == 13, "awakening note count drifted")
    ensure(neglect["entry_count"] > 0, "dormant neglect map is empty")
    ensure("FRONT-NEXT-4-POW-6-FULL-CORPUS-INTEGRATION" in active_queue, "active queue missing integration front")
    ensure("NEXT^[4^6] Full-Corpus Integration `[PROMOTED]`" in quest_board, "quest board missing integration note")
    ensure("Parallel Whole-Corpus Integration" in temple_state, "temple state missing integration note")
    ensure("Parallel Control-Plane Frontier" in next_prompt, "next prompt missing integration note")
    ensure("2.22" in active_run, "active run missing 2.22 phase row")
    ensure("NEXT^[4^6] Full-Corpus Integration" in coordination, "whole crystal coordination missing integration note")

    report = {
        "generated_at": utc_now(),
        "truth": "OK",
        "state_json": str(STATE_JSON_PATH),
        "notes_count": len(notes["notes"]),
        "neglect_entry_count": neglect["entry_count"],
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
