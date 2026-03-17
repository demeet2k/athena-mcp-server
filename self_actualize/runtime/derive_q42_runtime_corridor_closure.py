from __future__ import annotations

from pathlib import Path
from typing import Any

from self_actualize.runtime.qshrink_refine_common import (
    BLOCKED_EXTERNAL_FRONT,
    CURRENT_CARRIED_WITNESS,
    NEXT_HALL_SEED,
    NEXT_TEMPLE_HANDOFF,
    OPERATIONAL_CURRENT,
    RESERVE_FRONTIER,
    SELF_ACTUALIZE_ROOT,
    WORKSPACE_ROOT,
    docs_gate_payload,
    load_json,
    utc_now,
    write_json,
)


MANIFESTS_ROOT = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "nervous_system"
    / "manifests"
)
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
OUTPUT_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_CORRIDOR_MEMBRANE.md"
QSHRINK_RUNTIME_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"
Q42_ORGIN_PACKET_WITNESS_PATH = SELF_ACTUALIZE_ROOT / "q42_orgin_seed_packet_witness.json"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_q42_runtime_corridor_closure"
QUEUED_FOLLOW_ON = "P3 ORGIN"
AUTHORITATIVE_RECEIPT = (
    "self_actualize/mycelium_brain/receipts/2026-03-13_q42_refine_bundle_closure.md"
)
NEXT_HALL_SEED_DISPLAY = "none; do not invent QS64-25"


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")


def build_payload() -> dict[str, Any]:
    runtime_verification = load_json(QSHRINK_RUNTIME_VERIFICATION_PATH, {"truth": "NEAR"})
    packet_witness = load_json(Q42_ORGIN_PACKET_WITNESS_PATH, {"truth_state": "NEAR"})
    docs_gate = docs_gate_payload()
    truth_state = "OK" if runtime_verification.get("truth") == "OK" else "NEAR"
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth_state": truth_state,
        "corridor_id": "Q42-M3-RUNTIME-RAIL",
        "source_body_id": "A16",
        "target_runtime_surface": "MATH\\FINAL FORM\\FRAMEWORKS CODE\\Athena OS\\athena_os\\qshrink\\",
        "writeback_surface": "self_actualize/mycelium_brain/nervous_system/manifests/QSHRINK_ACTIVE_FRONT.md",
        "current_carried_witness": CURRENT_CARRIED_WITNESS,
        "current_owner_facing_subfront": OPERATIONAL_CURRENT,
        "active_local_subfront": OPERATIONAL_CURRENT,
        "next_seed": NEXT_HALL_SEED,
        "next_seed_display": NEXT_HALL_SEED_DISPLAY,
        "deeper_receiving_frontier": NEXT_TEMPLE_HANDOFF,
        "queued_follow_on": QUEUED_FOLLOW_ON,
        "reserve_frontier": RESERVE_FRONTIER,
        "blocked_external_front": BLOCKED_EXTERNAL_FRONT,
        "selected_pressure": "P2 Athena OS runtime",
        "docs_gate": docs_gate,
        "authoritative_current_receipt": AUTHORITATIVE_RECEIPT,
        "witness_basis": [
            relative_string(QSHRINK_RUNTIME_VERIFICATION_PATH),
            relative_string(OUTPUT_MD_PATH),
            "self_actualize/mycelium_brain/nervous_system/manifests/QSHRINK_ACTIVE_FRONT.md",
            relative_string(Q42_ORGIN_PACKET_WITNESS_PATH),
        ],
        "note": (
            f"Athena OS runtime remains P2, carries `{CURRENT_CARRIED_WITNESS}` as carried witness, "
            f"keeps `{OPERATIONAL_CURRENT}` as the closed Hall-local NEXT^4 terminal, keeps "
            f"`{NEXT_TEMPLE_HANDOFF}` as the immediate deeper receiver, keeps `{QUEUED_FOLLOW_ON}` "
            f"queue-visible, keeps `{RESERVE_FRONTIER}` reserve-only, and keeps `{BLOCKED_EXTERNAL_FRONT}` "
            "as blocked external truth."
        ),
        "packet_witness_truth": packet_witness.get("truth_state", "NEAR"),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    basis_lines = "\n".join(f"- `{item}`" for item in payload["witness_basis"])
    return "\n".join(
        [
            "# ATHENA OS QSHRINK CORRIDOR MEMBRANE",
            "",
            "Date: `2026-03-13`",
            f"Truth: `{payload['truth_state']}`",
            "",
            "## Corridor",
            "",
            f"- corridor id: `{payload['corridor_id']}`",
            f"- source body id: `{payload['source_body_id']}`",
            f"- target runtime surface: `{payload['target_runtime_surface']}`",
            f"- writeback surface: `{payload['writeback_surface']}`",
            f"- current carried witness: `{payload['current_carried_witness']}`",
            f"- active local subfront: `{payload['active_local_subfront']}`",
            f"- next Hall seed: `{payload['next_seed_display']}`",
            f"- immediate deeper receiver: `{payload['deeper_receiving_frontier']}`",
            f"- queued follow-on: `{payload['queued_follow_on']}`",
            f"- reserve frontier: `{payload['reserve_frontier']}`",
            f"- blocked external front: `{payload['blocked_external_front']}`",
            f"- authoritative receipt: `{payload['authoritative_current_receipt']}`",
            "",
            "## Witness basis",
            "",
            basis_lines,
            "",
            "## Note",
            "",
            payload["note"],
            "",
        ]
    ) + "\n"


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON_PATH, payload)
    OUTPUT_MD_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON_PATH}")
    print(f"Wrote {OUTPUT_MD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
