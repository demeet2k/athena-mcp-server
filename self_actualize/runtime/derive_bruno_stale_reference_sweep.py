from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = MYCELIUM_ROOT / "nervous_system"
FAMILIES_ROOT = NERVOUS_SYSTEM_ROOT / "families"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "bruno_stale_reference_sweep.json"
LEDGER_PATH = (
    MYCELIUM_ROOT
    / "nervous_system"
    / "ledgers"
    / "LEDGER_2026-03-13_q40_bruno_stale_reference_sweep.md"
)
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_bruno_stale_reference_sweep"
DERIVATION_VERSION = "2026-03-13.bruno-stale-reference-sweep.v1"

META_SURFACES = [
    MYCELIUM_ROOT / "nervous_system" / "04_deeper_emergent_metro_supermap.md",
    MYCELIUM_ROOT / "nervous_system" / "20_deeper_enhancement_real_time_agent.md",
]
FIXED_SCAN_PATHS = [
    *META_SURFACES,
    FAMILIES_ROOT / "FAMILY_bruno_archetype_compression.md",
    FAMILIES_ROOT / "FAMILY_bruno_primary_sources.md",
    FAMILIES_ROOT / "FAMILY_bruno_route_map.md",
    FAMILIES_ROOT / "BRUNO_B12_OPERATOR_TABLE.md",
    FAMILIES_ROOT / "BRUNO_ADDRESS_C_LEAF_PROMOTION.md",
    NERVOUS_SYSTEM_ROOT / "ganglia" / "GANGLION_bruno.md",
    NERVOUS_SYSTEM_ROOT / "ledgers" / "WITNESS_bruno_family.md",
    NERVOUS_SYSTEM_ROOT / "manifests" / "BRUNO_ACTIVE_FRONT.md",
    NERVOUS_SYSTEM_ROOT / "receipts" / "2026-03-09_bruno_family_activation.md",
    RECEIPTS_ROOT / "2026-03-10_q08_bruno_b12_operator_table.md",
    RECEIPTS_ROOT / "2026-03-10_q36_bruno_address_c_leaf_promotion.md",
]
RECONCILIATION_PATHS = {
    FAMILIES_ROOT / "BRUNO_B12_OPERATOR_TABLE.md",
    RECEIPTS_ROOT / "2026-03-10_q08_bruno_b12_operator_table.md",
}
TOKEN_MAP = {
    "132_bruno_working.md": "135_bruno_working.md",
    "51_athena_the_archetype.md": "54_athena_the_archetype.md",
    "179_the_magus.md": "182_the_magus.md",
    "132/51/179": "135/54/182",
}
AUTHORITY_BASIS = (
    "self_actualize/mycelium_brain/nervous_system/families/BRUNO_B12_OPERATOR_TABLE.md"
)
CORRECTION_NOTE_MARKER = "## Q40 Correction Note (2026-03-13)"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(WORKSPACE_ROOT).as_posix()


def docs_gate_status() -> str:
    credentials = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token = WORKSPACE_ROOT / "Trading Bot" / "token.json"
    return "READY" if credentials.exists() and token.exists() else "BLOCKED"


def classify_reference(path: Path) -> str:
    if path in RECONCILIATION_PATHS:
        return "reconciliation_evidence"
    if "receipts" in {part.lower() for part in path.parts}:
        return "historical_receipt"
    return "stale_live"


def action_for_classification(reference_class: str) -> str:
    return {
        "stale_live": "replace_live_ref",
        "historical_receipt": "add_correction_note",
        "reconciliation_evidence": "preserve_mapping",
    }[reference_class]


def note_for(path: Path, old_ref: str, live_ref: str, reference_class: str) -> str:
    if reference_class == "stale_live":
        return f"Live organism-routing prose must point to `{live_ref}` instead of `{old_ref}`."
    if reference_class == "historical_receipt":
        return (
            f"Historical receipt keeps chronology but must carry the `{CORRECTION_NOTE_MARKER}` erratum "
            f"mapping `{old_ref}` to `{live_ref}`."
        )
    return (
        f"Preserve `{old_ref}` because this surface documents the authoritative old-to-live reconciliation "
        f"into `{live_ref}`."
    )


def line_excerpt(line: str) -> str:
    collapsed = " ".join(line.strip().split())
    return collapsed[:220]


def scan_path(path: Path) -> list[dict[str, Any]]:
    text = read_text(path)
    records: list[dict[str, Any]] = []
    reference_class = classify_reference(path)
    seen_tokens: set[str] = set()
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        for old_ref, live_ref in TOKEN_MAP.items():
            if old_ref not in raw_line:
                continue
            if old_ref in seen_tokens:
                continue
            seen_tokens.add(old_ref)
            records.append(
                {
                    "source_path": relative(path),
                    "old_ref": old_ref,
                    "live_ref": live_ref,
                    "reference_class": reference_class,
                    "action": action_for_classification(reference_class),
                    "authority_basis": AUTHORITY_BASIS,
                    "notes": note_for(path, old_ref, live_ref, reference_class),
                    "line_number": line_number,
                    "excerpt": line_excerpt(raw_line),
                }
            )
    return records


def render_ledger(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Q40 Bruno Stale Reference Sweep",
        "",
        "Date: `2026-03-13`",
        f"Truth candidate: `{summary['truth_candidate']}`",
        f"Docs gate: `{summary['docs_gate_status']}`",
        "",
        "## Purpose",
        "",
        "Sweep retired Bruno capsule ids out of live routing surfaces while preserving the old-to-live mapping only where reconciliation evidence still needs it.",
        "",
        "## Replacement Map",
        "",
        "- `132_bruno_working.md -> 135_bruno_working.md`",
        "- `51_athena_the_archetype.md -> 54_athena_the_archetype.md`",
        "- `179_the_magus.md -> 182_the_magus.md`",
        "- `132/51/179 -> 135/54/182`",
        "",
        "## Summary",
        "",
        f"- scanned_paths: `{summary['scanned_path_count']}`",
        f"- recorded_occurrences: `{summary['record_count']}`",
        f"- stale_live: `{summary['counts_by_class'].get('stale_live', 0)}`",
        f"- historical_receipt: `{summary['counts_by_class'].get('historical_receipt', 0)}`",
        f"- reconciliation_evidence: `{summary['counts_by_class'].get('reconciliation_evidence', 0)}`",
        "",
        "## Clean Live Meta Surfaces",
        "",
    ]
    if payload["clean_live_surfaces"]:
        for item in payload["clean_live_surfaces"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- `none`")
    lines.extend(
        [
            "",
            "## Detected References",
            "",
            "| Source | Old | Live | Class | Action |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for record in payload["records"]:
        lines.append(
            f"| `{record['source_path']}` | `{record['old_ref']}` | `{record['live_ref']}` | `{record['reference_class']}` | `{record['action']}` |"
        )
    return "\n".join(lines)


def derive_payload() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    clean_live_surfaces: list[str] = []
    for path in FIXED_SCAN_PATHS:
        path_records = scan_path(path)
        records.extend(path_records)
        if path in META_SURFACES and not path_records:
            clean_live_surfaces.append(relative(path))
    counts_by_class: dict[str, int] = {}
    for record in records:
        counts_by_class[record["reference_class"]] = counts_by_class.get(record["reference_class"], 0) + 1
    truth_candidate = "OK" if counts_by_class.get("stale_live", 0) == 0 else "NEAR"
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "records": records,
        "clean_live_surfaces": clean_live_surfaces,
        "summary": {
            "docs_gate_status": docs_gate_status(),
            "scanned_path_count": len(FIXED_SCAN_PATHS),
            "record_count": len(records),
            "counts_by_class": counts_by_class,
            "truth_candidate": truth_candidate,
            "scan_paths": [relative(path) for path in FIXED_SCAN_PATHS],
        },
    }


def main() -> int:
    payload = derive_payload()
    write_json(OUTPUT_JSON_PATH, payload)
    write_text(LEDGER_PATH, render_ledger(payload))
    print(f"Wrote Bruno stale reference sweep json: {OUTPUT_JSON_PATH}")
    print(f"Wrote Bruno stale reference sweep ledger: {LEDGER_PATH}")
    print(f"Truth candidate: {payload['summary']['truth_candidate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
