from __future__ import annotations

import json
from pathlib import Path

from .derive_ap6d_full_corpus_integration import (
    DEEP_MD_PATH,
    HALL_NOTES_MD_PATH,
    NOTES_JSON_PATH,
    RECEIPT_JSON_PATH,
    RUNTIME_MD_PATH,
    TEMPLE_DECREE_MD_PATH,
    VERIFY_JSON_PATH,
    WAVE_JSON_PATH,
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    wave = load(WAVE_JSON_PATH)
    notes = load(NOTES_JSON_PATH)
    receipt = load(RECEIPT_JSON_PATH)
    note_class_counts = notes.get("class_counts") or notes.get("note_index", {}).get("class_counts") or wave.get("awakening_note_index", {}).get("class_counts")
    ensure(wave["docs_gate_status"] == "BLOCKED", "wave docs gate drifted")
    ensure(wave["frontier_seed"] == ["Q42", "Q46", "TQ04", "TQ06"], "feeder order drifted")
    ensure(note_class_counts == {"ap6d_lane": 5, "awakening_stage": 7, "archetype": 4}, "note counts drifted")
    ensure(len(notes["notes"]) == 16, "note total drifted")
    ensure(len(receipt["receipts"]) == 4, "receipt count drifted")
    for path in [HALL_NOTES_MD_PATH, TEMPLE_DECREE_MD_PATH, DEEP_MD_PATH, RUNTIME_MD_PATH]:
        ensure(path.exists(), f"missing surface: {path}")
    payload = {
        "generated_at": load(VERIFY_JSON_PATH)["generated_at"],
        "truth": "OK",
        "checks": {
            "docs_gate_status": wave["docs_gate_status"],
            "frontier_seed": wave["frontier_seed"],
            "note_count": len(notes["notes"]),
            "note_class_counts": note_class_counts,
            "receipt_count": len(receipt["receipts"]),
            "surfaces_checked": 4,
        },
    }
    VERIFY_JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote verification: {VERIFY_JSON_PATH}")
    print("Truth: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
