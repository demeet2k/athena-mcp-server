from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"

NEXT4_STATE_PATH = SELF_ACTUALIZE_ROOT / "qshrink_next4_state.json"
AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
NETWORK_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
CANONICAL_BUNDLE_PATH = SELF_ACTUALIZE_ROOT / "q42_canonical_bundle.json"
RUNTIME_MEMBRANE_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
CONTROL_STATE_PACKET_PATH = SELF_ACTUALIZE_ROOT / "control_state_packet.json"
OUTPUT_PATH = SELF_ACTUALIZE_ROOT / "q42_next4_closure_verification.json"

ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
TEMPLE_STATE_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
NEXT_SELF_PROMPT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
QSHRINK_ACTIVE_FRONT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "QSHRINK_ACTIVE_FRONT.md"
ACTIVE_RUN_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BUILD_QUEUE.md"
QUEST_BOARD_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
LOOPED_PLAN_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "13_QSHRINK_LOOPED_AGENTIC_PLAN.md"

EXPECTED_UPSTREAM = "QS64-20 Connectivity-Diagnose-Fractal"
EXPECTED_CURRENT = "QS64-24 Connectivity-Refine-Fractal"
EXPECTED_NEXT = None
EXPECTED_NEXT_DISPLAY = "none; do not invent QS64-25"
EXPECTED_TEMPLE = "TQ04: Bind The Helical Schema Pack To A Runner Contract"
EXPECTED_QUEUE = "P3 ORGIN"
EXPECTED_RESERVE = "Q46"
EXPECTED_BLOCKED = "Q02"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def has_all(text: str, *needles: str) -> bool:
    return all(needle in text for needle in needles if needle is not None)


def main() -> int:
    next4_state = load_json(NEXT4_STATE_PATH)
    matrix = load_json(AGENT_MATRIX_PATH)
    network = load_json(NETWORK_PATH)
    canonical_bundle = load_json(CANONICAL_BUNDLE_PATH)
    runtime_membrane = load_json(RUNTIME_MEMBRANE_PATH)
    control_state_packet = load_json(CONTROL_STATE_PACKET_PATH)

    active_queue = read_text(ACTIVE_QUEUE_PATH)
    temple_state = read_text(TEMPLE_STATE_PATH)
    next_self_prompt = read_text(NEXT_SELF_PROMPT_PATH)
    active_front = read_text(QSHRINK_ACTIVE_FRONT_PATH)
    active_run = read_text(ACTIVE_RUN_PATH)
    build_queue = read_text(BUILD_QUEUE_PATH)
    quest_board = read_text(QUEST_BOARD_PATH)
    looped_plan = read_text(LOOPED_PLAN_PATH)

    credentials_path = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token_path = WORKSPACE_ROOT / "Trading Bot" / "token.json"

    checks = {
        "next4_state_roles": (
            next4_state.get("current_carried_witness") == EXPECTED_UPSTREAM
            and next4_state.get("operational_current") == EXPECTED_CURRENT
            and next4_state.get("next_hall_seed") == EXPECTED_NEXT
            and next4_state.get("deeper_receiver") == EXPECTED_TEMPLE
            and next4_state.get("reserve_frontier") == EXPECTED_RESERVE
            and next4_state.get("blocked_external_front") == EXPECTED_BLOCKED
        ),
        "agent_matrix_roles": (
            matrix.get("current_carried_witness") == EXPECTED_UPSTREAM
            and matrix.get("operational_current") == EXPECTED_CURRENT
            and matrix.get("next_hall_seed") == EXPECTED_NEXT
            and matrix.get("deeper_receiving_frontier") == EXPECTED_TEMPLE
            and matrix.get("queued_follow_on") == EXPECTED_QUEUE
            and matrix.get("reserve_frontier") == EXPECTED_RESERVE
            and matrix.get("blocked_external_front") == EXPECTED_BLOCKED
        ),
        "network_roles": (
            network.get("current_carried_witness") == EXPECTED_UPSTREAM
            and network.get("active_local_subfront") == EXPECTED_CURRENT
            and network.get("next_hall_seed") == EXPECTED_NEXT
            and network.get("next_temple_handoff") == EXPECTED_TEMPLE
            and network.get("reserve_frontier") == EXPECTED_RESERVE
            and network.get("blocked_external_front") == EXPECTED_BLOCKED
        ),
        "canonical_bundle_roles": (
            canonical_bundle.get("current_carried_witness") == EXPECTED_UPSTREAM
            and canonical_bundle.get("active_subfront") == EXPECTED_CURRENT
            and canonical_bundle.get("next_seed") == EXPECTED_NEXT
            and canonical_bundle.get("deeper_receiving_frontier") == EXPECTED_TEMPLE
            and canonical_bundle.get("reserve_frontier") == EXPECTED_RESERVE
            and canonical_bundle.get("blocked_external_front") == EXPECTED_BLOCKED
        ),
        "runtime_membrane_roles": (
            runtime_membrane.get("current_carried_witness") == EXPECTED_UPSTREAM
            and runtime_membrane.get("active_local_subfront") == EXPECTED_CURRENT
            and runtime_membrane.get("next_seed") == EXPECTED_NEXT
            and runtime_membrane.get("deeper_receiving_frontier") == EXPECTED_TEMPLE
            and runtime_membrane.get("queued_follow_on") == EXPECTED_QUEUE
            and runtime_membrane.get("reserve_frontier") == EXPECTED_RESERVE
            and runtime_membrane.get("blocked_external_front") == EXPECTED_BLOCKED
        ),
        "control_state_packet_roles": (
            control_state_packet.get("carried_witness") == EXPECTED_UPSTREAM
            and control_state_packet.get("operational_current") == EXPECTED_CURRENT
            and control_state_packet.get("next_hall_seed") == EXPECTED_NEXT_DISPLAY
            and control_state_packet.get("deeper_receiver") == EXPECTED_TEMPLE
            and control_state_packet.get("reserve_frontier") == EXPECTED_RESERVE
            and control_state_packet.get("blocked_external_front") == EXPECTED_BLOCKED
        ),
        "active_queue_current_state": has_all(
            active_queue,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
            EXPECTED_BLOCKED,
            "Trading Bot/credentials.json",
            "Trading Bot/token.json",
        ),
        "temple_state_current_state": has_all(
            temple_state,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
            EXPECTED_BLOCKED,
        ),
        "next_self_prompt_current_state": has_all(
            next_self_prompt,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
            EXPECTED_BLOCKED,
            "do not invent QS64-25",
        ),
        "active_front_current_state": has_all(
            active_front,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
            EXPECTED_BLOCKED,
        ),
        "active_run_current_state": has_all(
            active_run,
            EXPECTED_UPSTREAM,
            EXPECTED_CURRENT,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
            EXPECTED_BLOCKED,
        ),
        "build_queue_current_state": has_all(
            build_queue,
            "Q41 / TQ06",
            EXPECTED_UPSTREAM,
            EXPECTED_CURRENT,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
            EXPECTED_BLOCKED,
        ),
        "quest_board_current_state": has_all(
            quest_board,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
            EXPECTED_BLOCKED,
            "do not invent QS64-25",
        ),
        "looped_plan_current_state": has_all(
            looped_plan,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
            EXPECTED_BLOCKED,
            "P3 ORGIN",
        ),
        "docs_gate_honest": (not credentials_path.exists()) and (not token_path.exists()),
    }
    failed = [name for name, ok in checks.items() if not ok]
    payload = {
        "generated_at": utc_now(),
        "derivation_command": "python -m self_actualize.runtime.verify_q42_next4_closure",
        "truth": "OK" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "expected_roles": {
            "current_carried_witness": EXPECTED_UPSTREAM,
            "active_local_subfront": EXPECTED_CURRENT,
            "next_hall_seed": EXPECTED_NEXT_DISPLAY,
            "deeper_receiving_frontier": EXPECTED_TEMPLE,
            "queued_follow_on": EXPECTED_QUEUE,
            "reserve_frontier": EXPECTED_RESERVE,
            "blocked_external_front": EXPECTED_BLOCKED,
        },
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Truth: {payload['truth']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
