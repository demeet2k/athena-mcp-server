from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .derive_bruno_stale_reference_sweep import (
    AUTHORITY_BASIS,
    CORRECTION_NOTE_MARKER,
    LEDGER_PATH,
    META_SURFACES,
    OUTPUT_JSON_PATH as REGISTRY_PATH,
    TOKEN_MAP,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "bruno_stale_reference_verification.json"
QUEST_BOARD_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
CHANGE_FEED_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "04_CHANGE_FEED_BOARD.md"
ACTIVE_QUEUE_PATH = MYCELIUM_ROOT / "nervous_system" / "06_active_queue.md"
ENHANCEMENT_FRONT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "DEEPER_ENHANCEMENT_ACTIVE_FRONT.md"
BRUNO_ACTIVE_FRONT_PATH = MYCELIUM_ROOT / "nervous_system" / "manifests" / "BRUNO_ACTIVE_FRONT.md"
BRUNO_RECEIPT_PATH = MYCELIUM_ROOT / "nervous_system" / "receipts" / "2026-03-09_bruno_family_activation.md"
Q08_RECEIPT_PATH = MYCELIUM_ROOT / "receipts" / "2026-03-10_q08_bruno_b12_operator_table.md"
B12_TABLE_PATH = MYCELIUM_ROOT / "nervous_system" / "families" / "BRUNO_B12_OPERATOR_TABLE.md"
QUEST_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "adventurer_quest_registry.json"
AGENT_STATE_PATH = SELF_ACTUALIZE_ROOT / "adventurer_agent_state.json"
LOOP_STATE_PATH = SELF_ACTUALIZE_ROOT / "adventurer_loop_state.json"
DERIVATION_COMMAND = "python -m self_actualize.runtime.verify_bruno_stale_reference_sweep"
DERIVATION_VERSION = "2026-03-13.bruno-stale-reference-sweep.verify.v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def docs_gate_status() -> str:
    credentials = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token = WORKSPACE_ROOT / "Trading Bot" / "token.json"
    return "READY" if credentials.exists() and token.exists() else "BLOCKED"


def run_check(label: str, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return {"label": label, "status": "OK", "details": fn()}
    except Exception as exc:  # noqa: BLE001
        return {"label": label, "status": "FAIL", "details": str(exc)}


def scan_occurrences() -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    registry = load_json(REGISTRY_PATH)
    for source_path in registry["summary"]["scan_paths"]:
        path = WORKSPACE_ROOT / source_path
        text = read_text(path)
        for old_ref in TOKEN_MAP:
            if old_ref in text:
                matches.append((source_path, old_ref))
    return matches


def verify_registry_coverage() -> dict[str, Any]:
    registry = load_json(REGISTRY_PATH)
    actual_pairs = scan_occurrences()
    registry_pairs = [(record["source_path"], record["old_ref"]) for record in registry["records"]]
    ensure(sorted(actual_pairs) == sorted(registry_pairs), "registry coverage does not match current fixed-scan occurrences")
    return {
        "record_count": len(registry["records"]),
        "scan_occurrence_count": len(actual_pairs),
    }


def verify_live_meta_surfaces_clean() -> dict[str, Any]:
    failures: list[str] = []
    for path in META_SURFACES:
        text = read_text(path)
        hits = [old_ref for old_ref in TOKEN_MAP if old_ref in text]
        if hits:
            failures.append(f"{path.relative_to(WORKSPACE_ROOT).as_posix()} -> {hits}")
    ensure(not failures, f"stale live Bruno refs remain: {failures}")
    return {"clean_surfaces": [path.relative_to(WORKSPACE_ROOT).as_posix() for path in META_SURFACES]}


def verify_reconciliation_surfaces_preserved() -> dict[str, Any]:
    b12_text = read_text(B12_TABLE_PATH)
    q08_text = read_text(Q08_RECEIPT_PATH)
    ensure("132_bruno_working.md" in b12_text and "135_bruno_working.md" in b12_text, "B12 table lost the working reconciliation map")
    ensure("51_athena_the_archetype.md" in b12_text and "54_athena_the_archetype.md" in b12_text, "B12 table lost the Athena reconciliation map")
    ensure("179_the_magus.md" in b12_text and "182_the_magus.md" in b12_text, "B12 table lost the Magus reconciliation map")
    ensure("132/51/179" in q08_text and "135/54/182" in q08_text, "Q08 receipt lost the compact reconciliation evidence")
    ensure(AUTHORITY_BASIS.replace("self_actualize/mycelium_brain/", "") in str(B12_TABLE_PATH).replace("\\", "/"), "authority basis drifted")
    return {
        "b12_table": B12_TABLE_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
        "q08_receipt": Q08_RECEIPT_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
    }


def verify_historical_receipt_correction() -> dict[str, Any]:
    text = read_text(BRUNO_RECEIPT_PATH)
    ensure(CORRECTION_NOTE_MARKER in text, "historical Bruno activation receipt is missing the Q40 correction note")
    ensure("132_bruno_working.md -> 135_bruno_working.md" in text, "historical receipt correction note missing working mapping")
    ensure("51_athena_the_archetype.md -> 54_athena_the_archetype.md" in text, "historical receipt correction note missing Athena mapping")
    ensure("179_the_magus.md -> 182_the_magus.md" in text, "historical receipt correction note missing Magus mapping")
    return {"receipt_path": BRUNO_RECEIPT_PATH.relative_to(WORKSPACE_ROOT).as_posix()}


def verify_control_plane_sync() -> dict[str, Any]:
    quest_board = read_text(QUEST_BOARD_PATH)
    change_feed = read_text(CHANGE_FEED_PATH)
    active_queue = read_text(ACTIVE_QUEUE_PATH)
    enhancement_front = read_text(ENHANCEMENT_FRONT_PATH)
    bruno_front = read_text(BRUNO_ACTIVE_FRONT_PATH)
    registry = load_json(QUEST_REGISTRY_PATH)
    agent_state = load_json(AGENT_STATE_PATH)
    loop_state = load_json(LOOP_STATE_PATH)

    ensure("### Quest Q40: Sweep Stale Bruno References Beyond The Canonical Family Core `[PROMOTED 2026-03-13]`" in quest_board, "Hall quest board does not show Q40 as promoted")
    ensure("`Q42`" in quest_board, "Hall quest board is missing the Q42 restart seed")
    ensure("Q40 is now promoted" in change_feed, "change feed missing Q40 promotion entry")
    ensure("### FRONT-Q40-BRUNO-STALE-REFERENCE-SWEEP" in active_queue, "active queue missing promoted Q40 entry")
    ensure("`Q42: Activate The First QSHRINK Agent Sweep`" in enhancement_front, "deeper enhancement active front did not advance to Q42")
    ensure("`Q42 Activate The First QSHRINK Agent Sweep`" in bruno_front or "`Q42: Activate The First QSHRINK Agent Sweep`" in bruno_front, "Bruno active front did not hand off to Q42")
    ensure(registry["next_frontier"] == "Q42", f"adventurer registry next frontier drifted: {registry['next_frontier']}")
    ensure(loop_state["next_frontier"] == "Q42", f"loop state next frontier drifted: {loop_state['next_frontier']}")
    ensure(agent_state["agents"][0]["active_claim"] == "Q42", f"primary floating agent did not claim Q42: {agent_state['agents'][0]['active_claim']}")
    return {
        "next_frontier": registry["next_frontier"],
        "primary_active_claim": agent_state["agents"][0]["active_claim"],
    }


def verify_docs_gate_honesty() -> dict[str, Any]:
    registry = load_json(REGISTRY_PATH)
    status = docs_gate_status()
    ensure(registry["summary"]["docs_gate_status"] == status, "registry docs gate status drifted")
    if status == "BLOCKED":
        credentials = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
        token = WORKSPACE_ROOT / "Trading Bot" / "token.json"
        ensure(not (credentials.exists() and token.exists()), "docs gate says blocked but OAuth files exist")
    return {"docs_gate_status": status}


def verify_payload() -> dict[str, Any]:
    checks = [
        run_check("registry_coverage", verify_registry_coverage),
        run_check("live_meta_surfaces_clean", verify_live_meta_surfaces_clean),
        run_check("reconciliation_surfaces_preserved", verify_reconciliation_surfaces_preserved),
        run_check("historical_receipt_correction", verify_historical_receipt_correction),
        run_check("control_plane_sync", verify_control_plane_sync),
        run_check("docs_gate_honesty", verify_docs_gate_honesty),
        run_check("ledger_exists", lambda: {"ledger_path": LEDGER_PATH.relative_to(WORKSPACE_ROOT).as_posix(), "exists": LEDGER_PATH.exists()} if LEDGER_PATH.exists() else (_ for _ in ()).throw(AssertionError("Q40 ledger missing"))),
    ]
    failed = [check for check in checks if check["status"] != "OK"]
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": [check["label"] for check in failed],
    }


def main() -> int:
    payload = verify_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote Bruno stale reference verification json: {OUTPUT_JSON_PATH}")
    print(f"Truth: {payload['truth']}")
    for check in payload["checks"]:
        print(f"- {check['label']}: {check['status']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
