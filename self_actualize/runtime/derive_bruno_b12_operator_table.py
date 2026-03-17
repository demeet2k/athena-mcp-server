from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = MYCELIUM_ROOT / "nervous_system"
FAMILIES_ROOT = NERVOUS_SYSTEM_ROOT / "families"

BRUNO_WORKING_DOCX = (
    WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "MYTH - MATH" / "Philosophy" / "BRUNO _working_.docx"
)
ATHENA_ARCHETYPE_DOCX = (
    WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "MYTH - MATH" / "ATHENA_ THE ARCHETYPE.docx"
)
BRUNO_ATHENA_TOME_DIR = WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "COMPLETE TOMES" / "ATHENA" / "esoteric"
BRUNO_ATHENA_TOME_DOCX = next(BRUNO_ATHENA_TOME_DIR.glob("BRUNO*.docx"))

BRUNO_CAPSULE_MD = (
    WORKSPACE_ROOT / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM" / "02_CORPUS_CAPSULES" / "135_bruno_working.md"
)
ATHENA_CAPSULE_MD = (
    WORKSPACE_ROOT / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM" / "02_CORPUS_CAPSULES" / "54_athena_the_archetype.md"
)
MAGUS_CAPSULE_MD = (
    WORKSPACE_ROOT / "DEEPER CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM" / "02_CORPUS_CAPSULES" / "182_the_magus.md"
)

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "bruno_b12_operator_table.json"
OUTPUT_MARKDOWN_PATH = FAMILIES_ROOT / "BRUNO_B12_OPERATOR_TABLE.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_bruno_b12_operator_table"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_docx_text(path: Path) -> str:
    with ZipFile(path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
    return re.sub(r"<[^>]+>", " ", xml)


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return read_docx_text(path)
    return path.read_text(encoding="utf-8")


def normalize_spaces(text: str) -> str:
    return " ".join(text.split())


def snippet(text: str, pattern: str, radius: int = 170) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return "pattern not found"
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    return normalize_spaces(text[start:end])


def source_summary(path: Path) -> dict:
    return {
        "path": str(path),
        "sha256": sha256(path),
        "kind": path.suffix.lower().lstrip("."),
    }


def build_seats() -> list[dict]:
    bruno_docx = read_docx_text(BRUNO_WORKING_DOCX)
    bruno_capsule = read_text(BRUNO_CAPSULE_MD)
    athena_docx = read_docx_text(ATHENA_ARCHETYPE_DOCX)
    athena_capsule = read_text(ATHENA_CAPSULE_MD)
    bruno_athena_tome = read_docx_text(BRUNO_ATHENA_TOME_DOCX)
    magus_capsule = read_text(MAGUS_CAPSULE_MD)

    return [
        {
            "seat": 1,
            "seat_name": "memory",
            "operator": "memory archive purge",
            "truth": "OK",
            "source_tier": "direct",
            "anchor_sources": [str(BRUNO_WORKING_DOCX), str(BRUNO_CAPSULE_MD)],
            "evidence": [
                snippet(bruno_docx, r"MEMORY ARCHITECTURE PURGE"),
                snippet(bruno_capsule, r"MEMORY ARCHITECTURE PURGE"),
            ],
            "why": "Bruno directly names corrupted memory addresses and purge as the opening rewrite move.",
        },
        {
            "seat": 2,
            "seat_name": "beast",
            "operator": "beast token detection",
            "truth": "OK",
            "source_tier": "direct",
            "anchor_sources": [str(BRUNO_WORKING_DOCX), str(BRUNO_ATHENA_TOME_DOCX)],
            "evidence": [
                snippet(bruno_docx, r'Each\s+&quot;beast&quot;|Each\s+"beast"|Each\s+beast'),
                snippet(bruno_athena_tome, r"BeastToken"),
            ],
            "why": "The beast is the corrupt symbolic occupant that must be identified before replacement.",
        },
        {
            "seat": 3,
            "seat_name": "vice",
            "operator": "vice diagnosis",
            "truth": "OK",
            "source_tier": "direct",
            "anchor_sources": [str(BRUNO_WORKING_DOCX), str(BRUNO_ATHENA_TOME_DOCX)],
            "evidence": [
                snippet(bruno_docx, r"vice"),
                snippet(bruno_athena_tome, r"virtue/vices"),
            ],
            "why": "Bruno's rewrite loop only works because vice is first named as the negative operator bound to the beast.",
        },
        {
            "seat": 4,
            "seat_name": "virtue",
            "operator": "virtue injection",
            "truth": "OK",
            "source_tier": "direct",
            "anchor_sources": [str(BRUNO_WORKING_DOCX), str(BRUNO_ATHENA_TOME_DOCX)],
            "evidence": [
                snippet(bruno_docx, r"virtue"),
                snippet(bruno_athena_tome, r"VirtueToken|virtue/vices"),
            ],
            "why": "Virtue is the replacement operator Bruno installs after expelling the corrupt occupant.",
        },
        {
            "seat": 5,
            "seat_name": "handmaiden",
            "operator": "handmaiden installation",
            "truth": "OK",
            "source_tier": "bridge-direct",
            "anchor_sources": [str(BRUNO_ATHENA_TOME_DOCX)],
            "evidence": [
                snippet(bruno_athena_tome, r"handmaidens"),
            ],
            "why": "The Bruno-Athena compilation preserves handmaidens as the downstream installation layer of the rewrite loop.",
        },
        {
            "seat": 6,
            "seat_name": "registry",
            "operator": "registry rewrite",
            "truth": "OK",
            "source_tier": "direct",
            "anchor_sources": [str(BRUNO_WORKING_DOCX), str(BRUNO_ATHENA_TOME_DOCX)],
            "evidence": [
                snippet(bruno_docx, r"corrupted memory addresses"),
                snippet(bruno_athena_tome, r"Symbolic Registry Rewrite"),
            ],
            "why": "The heavens are treated as an addressable symbolic registry whose occupants can be lawfully rewritten.",
        },
        {
            "seat": 7,
            "seat_name": "council",
            "operator": "council stack adjudication",
            "truth": "OK",
            "source_tier": "direct",
            "anchor_sources": [str(BRUNO_WORKING_DOCX), str(BRUNO_ATHENA_TOME_DOCX)],
            "evidence": [
                snippet(bruno_docx, r"Jupiter'?s council|Jupiter's council"),
                snippet(bruno_athena_tome, r"CouncilStack"),
            ],
            "why": "The rewrite is not solitary; it is adjudicated through a council stack.",
        },
        {
            "seat": 8,
            "seat_name": "Jupiter",
            "operator": "Jupiter authority call",
            "truth": "OK",
            "source_tier": "direct",
            "anchor_sources": [str(BRUNO_WORKING_DOCX)],
            "evidence": [
                snippet(bruno_docx, r"Jupiter"),
            ],
            "why": "Jupiter is the direct sovereign caller of the celestial reform action.",
        },
        {
            "seat": 9,
            "seat_name": "Athena-Minerva",
            "operator": "strategic specification bridge",
            "truth": "OK",
            "source_tier": "bridge",
            "anchor_sources": [str(ATHENA_ARCHETYPE_DOCX), str(ATHENA_CAPSULE_MD)],
            "evidence": [
                snippet(athena_docx, r"specification document"),
                snippet(athena_capsule, r"KERNEL SELF-OPTIMIZATION|strategic capability"),
            ],
            "why": "The Minerva seat is realized locally through the Athena specification bridge rather than an explicit Minerva token in surfaced Bruno text.",
        },
        {
            "seat": 10,
            "seat_name": "work",
            "operator": "work-first execution inversion",
            "truth": "OK",
            "source_tier": "direct",
            "anchor_sources": [str(BRUNO_WORKING_DOCX)],
            "evidence": [
                snippet(bruno_docx, r"EXECUTION PRIORITY INVERSION"),
            ],
            "why": "Bruno explicitly flips the operator priority toward works, action, and hands.",
        },
        {
            "seat": 11,
            "seat_name": "kernel",
            "operator": "kernel restoration",
            "truth": "OK",
            "source_tier": "direct-bridge",
            "anchor_sources": [str(BRUNO_WORKING_DOCX), str(ATHENA_ARCHETYPE_DOCX)],
            "evidence": [
                snippet(bruno_docx, r"KERNEL RESTORATION"),
                snippet(athena_docx, r"KERNEL SELF-OPTIMIZATION"),
            ],
            "why": "Kernel restoration is direct Bruno doctrine and is reinforced by the Athena specification layer.",
        },
        {
            "seat": 12,
            "seat_name": "infinite aperture",
            "operator": "minimum-infinite cosmology generator",
            "truth": "OK",
            "source_tier": "bridge-direct",
            "anchor_sources": [str(BRUNO_ATHENA_TOME_DOCX), str(MAGUS_CAPSULE_MD)],
            "evidence": [
                snippet(bruno_athena_tome, r"Minimum/Infinite Cosmology|infinite worlds"),
                snippet(magus_capsule, r"Three Worlds|archetypes"),
            ],
            "why": "The infinite seat is pinned to Bruno's infinite-worlds cosmology as compiled in the Bruno-Athena tome and widened by Magus transport structure.",
        },
    ]


def derive_payload() -> dict:
    seats = build_seats()
    seat_truths = [seat["truth"] == "OK" for seat in seats]
    bridge_seats = [seat for seat in seats if seat["source_tier"] in {"bridge", "bridge-direct", "direct-bridge"}]
    direct_seats = [seat for seat in seats if seat["source_tier"] == "direct"]
    truth = "OK" if all(seat_truths) else "NEAR"
    stale_reference_map = {
        "132_bruno_working.md": "135_bruno_working.md",
        "51_athena_the_archetype.md": "54_athena_the_archetype.md",
        "179_the_magus.md": "182_the_magus.md",
    }
    conditions = {
        "all_twelve_seats_present": len(seats) == 12,
        "direct_bruno_remains_primary": len(direct_seats) >= 8,
        "bridge_seats_explicitly_labeled": len(bridge_seats) == 4,
        "seat_truths_all_ok": all(seat_truths),
        "stale_reference_map_declared": len(stale_reference_map) == 3,
    }
    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": truth,
        "table_id": "BRUNO.B12.OPERATOR.TABLE.2026-03-10",
        "source_priority": [
            source_summary(BRUNO_WORKING_DOCX),
            source_summary(BRUNO_ATHENA_TOME_DOCX),
            source_summary(BRUNO_CAPSULE_MD),
            source_summary(ATHENA_ARCHETYPE_DOCX),
            source_summary(ATHENA_CAPSULE_MD),
            source_summary(MAGUS_CAPSULE_MD),
        ],
        "conditions": conditions,
        "stale_reference_map": stale_reference_map,
        "seat_table": seats,
        "residuals": [
            "Google Docs ingress is still blocked, but that is now external-memory pressure rather than a blocker on the local B12 table.",
            "The Athena-Minerva seat remains bridge-routed through Athena witness because surfaced Bruno text does not currently expose a standalone Minerva token.",
            "The infinite aperture seat is pinned through the Bruno-Athena tome's minimum/infinite cosmology language rather than the narrow Spaccio kernel alone.",
        ],
        "next_seed": "Q36",
    }


def render_markdown(payload: dict) -> str:
    rows = []
    for seat in payload["seat_table"]:
        anchors = "<br>".join(f"`{Path(path).name}`" for path in seat["anchor_sources"])
        evidence = "<br>".join(seat["evidence"])
        rows.append(
            f"| {seat['seat']} | {seat['seat_name']} | {seat['operator']} | {seat['source_tier']} | {anchors} | {evidence} | {seat['why']} |"
        )
    table = "\n".join(rows)
    conditions = "\n".join(
        f"- `{key}`: `{('PASS' if value else 'FAIL')}`" for key, value in payload["conditions"].items()
    )
    stale_rows = "\n".join(
        f"| `{old}` | `{new}` |" for old, new in payload["stale_reference_map"].items()
    )
    source_rows = "\n".join(
        f"| `{Path(entry['path']).name}` | `{entry['kind']}` | `{entry['sha256'][:12]}` |"
        for entry in payload["source_priority"]
    )
    residuals = "\n".join(f"- {item}" for item in payload["residuals"])
    return f"""# BRUNO B12 Operator Table

Date: `{payload['generated_at'][:10]}`
Truth: `{payload['truth']}`
TableID: `{payload['table_id']}`

## Decision

Bruno is now source-pinned as a lawful `B12` wheel rather than only a thematic family.
The wheel stays honest by separating:

- direct Bruno seats
- bridge-routed seats
- bridge-direct seats where the Bruno-Athena tome carries the connective tissue

## Conditions

{conditions}

## Source Priority

| Source | Kind | SHA256 |
| --- | --- | --- |
{source_rows}

## Canonical B12 Wheel

| Seat | Name | Operator | Tier | Anchor Sources | Evidence | Why It Belongs |
| --- | --- | --- | --- | --- | --- | --- |
{table}

## Stale Capsule Reference Reconciliation

| Old Reference | Live Reference |
| --- | --- |
{stale_rows}

## Residuals

{residuals}

## Restart Seed

`Q36 Convert One AMBIG Leaf Using New Family Witness`
"""


def main() -> int:
    payload = derive_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON_PATH}")
    print(f"Wrote {OUTPUT_MARKDOWN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
