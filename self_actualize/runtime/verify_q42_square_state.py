from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"

AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
REFINE_SQUARE_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_refine_square.json"
SQUARE_PAYLOAD_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_square.json"
RUNTIME_MEMBRANE_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
OUTPUT_PATH = SELF_ACTUALIZE_ROOT / "q42_square_state_verification.json"
AUTHORITATIVE_RECEIPT_PATH = MYCELIUM_ROOT / "receipts" / "2026-03-13_q42_qs64_21_authoritative_square_bundle.md"

ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
TEMPLE_STATE_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
NEXT_SELF_PROMPT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
QSHRINK_ACTIVE_FRONT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "QSHRINK_ACTIVE_FRONT.md"
ACTIVE_RUN_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md"
QUEST_BOARD_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"

EXPECTED_CURRENT = "QS64-21 Connectivity-Refine-Square"
EXPECTED_UPSTREAM = "QS64-20 Connectivity-Diagnose-Fractal"
EXPECTED_NEXT = "QS64-22 Connectivity-Refine-Flower"
EXPECTED_TEMPLE = "TQ04: Bind The Helical Schema Pack To A Runner Contract"
EXPECTED_QUEUE = "P3 ORGIN"
EXPECTED_RESERVE = "Q45"
EXPECTED_BLOCKED = "Q02"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def has_all(text: str, *needles: str) -> bool:
    return all(needle in text for needle in needles)


def build_checks() -> dict[str, bool]:
    matrix = load_json(AGENT_MATRIX_PATH)
    refine_square = load_json(REFINE_SQUARE_PATH)
    square_payload = load_json(SQUARE_PAYLOAD_PATH)
    runtime_membrane = load_json(RUNTIME_MEMBRANE_PATH)
    active_queue = read_text(ACTIVE_QUEUE_PATH)
    temple_state = read_text(TEMPLE_STATE_PATH)
    next_self_prompt = read_text(NEXT_SELF_PROMPT_PATH)
    active_front = read_text(QSHRINK_ACTIVE_FRONT_PATH)
    active_run = read_text(ACTIVE_RUN_PATH)
    quest_board = read_text(QUEST_BOARD_PATH)

    credentials_path = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token_path = WORKSPACE_ROOT / "Trading Bot" / "token.json"

    return {
        "agent_matrix_roles": (
            matrix.get("current_carried_witness") == EXPECTED_UPSTREAM
            and matrix.get("active_local_subfront") == EXPECTED_CURRENT
            and matrix.get("next_hall_seed") == EXPECTED_NEXT
            and matrix.get("deeper_receiving_frontier") == EXPECTED_TEMPLE
            and matrix.get("queued_follow_on") == EXPECTED_QUEUE
            and matrix.get("reserve_frontier") == EXPECTED_RESERVE
            and matrix.get("blocked_external_front") == EXPECTED_BLOCKED
        ),
        "refine_square_roles": (
            refine_square.get("current_carried_witness") == EXPECTED_UPSTREAM
            and refine_square.get("active_local_subfront") == EXPECTED_CURRENT
            and refine_square.get("next_hall_seed") == EXPECTED_NEXT
            and refine_square.get("deeper_receiving_frontier") == EXPECTED_TEMPLE
            and refine_square.get("queued_follow_on") == EXPECTED_QUEUE
            and refine_square.get("reserve_frontier") == EXPECTED_RESERVE
            and refine_square.get("blocked_external_front") == EXPECTED_BLOCKED
        ),
        "square_payload_roles": (
            square_payload.get("current_carried_witness") == EXPECTED_UPSTREAM
            and square_payload.get("active_local_subfront") == EXPECTED_CURRENT
            and square_payload.get("next_hall_seed") == EXPECTED_NEXT
            and square_payload.get("deeper_receiving_frontier") == EXPECTED_TEMPLE
            and square_payload.get("queued_follow_on") == EXPECTED_QUEUE
            and square_payload.get("reserve_frontier") == EXPECTED_RESERVE
            and square_payload.get("blocked_external_front") == EXPECTED_BLOCKED
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
        "active_queue_square_state": has_all(
            active_queue,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_NEXT,
            EXPECTED_TEMPLE,
            EXPECTED_QUEUE,
            EXPECTED_RESERVE,
            "Trading Bot/credentials.json",
            "Trading Bot/token.json",
        ),
        "temple_state_square_state": has_all(
            temple_state,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_NEXT,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
        ),
        "next_self_prompt_square_state": has_all(
            next_self_prompt,
            EXPECTED_CURRENT,
            EXPECTED_NEXT,
            EXPECTED_TEMPLE,
            EXPECTED_QUEUE,
        ),
        "active_front_square_state": has_all(
            active_front,
            EXPECTED_CURRENT,
            EXPECTED_NEXT,
            EXPECTED_TEMPLE,
            EXPECTED_QUEUE,
        ),
        "active_run_square_state": has_all(
            active_run,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_NEXT,
            EXPECTED_TEMPLE,
            EXPECTED_RESERVE,
            EXPECTED_QUEUE,
        ),
        "quest_board_square_state": has_all(
            quest_board,
            EXPECTED_CURRENT,
            EXPECTED_UPSTREAM,
            EXPECTED_NEXT,
            EXPECTED_TEMPLE,
            EXPECTED_QUEUE,
            str(AUTHORITATIVE_RECEIPT_PATH),
        ),
        "authoritative_receipt_exists": AUTHORITATIVE_RECEIPT_PATH.exists(),
        "docs_gate_honest": (not credentials_path.exists()) and (not token_path.exists()),
    }


def main() -> int:
    checks = build_checks()
    failed = [name for name, ok in checks.items() if not ok]
    payload = {
        "generated_at": utc_now(),
        "derivation_command": "python -m self_actualize.runtime.verify_q42_square_state",
        "truth": "OK" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "expected_roles": {
            "current_carried_witness": EXPECTED_UPSTREAM,
            "active_local_subfront": EXPECTED_CURRENT,
            "next_hall_seed": EXPECTED_NEXT,
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
