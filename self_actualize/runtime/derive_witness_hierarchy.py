from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
GUILD_HALL_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
INDEX_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "00_INDEX.md"

CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "archive_atlas.json"
BOARD_STATUS_PATH = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "07_FULL_PROJECT_INTEGRATION_256"
    / "06_REALTIME_BOARD"
    / "00_STATUS"
    / "00_BOARD_STATUS.md"
)
BOARD_WITNESS_FALLBACK_PATHS = [
    GUILD_HALL_ROOT / "07_CANONICAL_WITNESS_HIERARCHY.md",
    SELF_ACTUALIZE_ROOT / "witness_hierarchy.json",
    WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "00_INDEX.md",
]
PROMOTED_STATE_HEADER_PATH = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "_build"
    / "nervous_system"
    / "manifests"
    / "STATE_HEADER.md"
)
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "witness_hierarchy.json"
REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "registry" / "witness_hierarchy.json"
OUTPUT_MARKDOWN_PATH = GUILD_HALL_ROOT / "07_CANONICAL_WITNESS_HIERARCHY.md"
OUTPUT_RECEIPT_PATH = (
    SELF_ACTUALIZE_ROOT
    / "mycelium_brain"
    / "receipts"
    / "2026-03-09_witness_hierarchy_derivation.md"
)
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_witness_hierarchy"

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def should_skip(path: Path) -> bool:
    lowered = {part.lower() for part in path.parts}
    return any(part.lower() in lowered for part in IGNORE_DIRS)


def existing_physical_witness() -> int | None:
    if INDEX_PATH.exists():
        text = INDEX_PATH.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"Physical witness`: `(\d+)`", text)
        if match:
            return int(match.group(1))
    candidates = [OUTPUT_JSON_PATH, REGISTRY_JSON_PATH]
    for path in candidates:
        if not path.exists():
            continue
        payload = load_json(path)
        value = payload.get("witnesses", {}).get("physical", {}).get("value")
        if value is not None:
            return int(value)
    return None


def count_physical_witness() -> tuple[int, str, str]:
    script = (
        "param([string]$root)\n"
        "(Get-ChildItem -Path $root -Recurse -File -Force -ErrorAction SilentlyContinue |\n"
        "Where-Object { $_.FullName -notmatch '\\.git(\\\\|$)|\\.venv(\\\\|$)|__pycache__(\\\\|$)|\\.mypy_cache(\\\\|$)|\\.pytest_cache(\\\\|$)|\\.ruff_cache(\\\\|$)|\\.idea(\\\\|$)|\\.vscode(\\\\|$)' } |\n"
        "Measure-Object).Count\n"
    )
    temp_path = Path(tempfile.gettempdir()) / "athena_witness_hierarchy_count.ps1"
    temp_path.write_text(script, encoding="utf-8")
    try:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(temp_path),
                str(WORKSPACE_ROOT),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass

    if completed.returncode == 0:
        try:
            return (
                int(completed.stdout.strip()),
                utc_now(),
                "powershell file-backed recursive file sweep excluding runtime ignore directories",
            )
        except ValueError:
            pass

    fallback = existing_physical_witness()
    if fallback is not None:
        return (
            fallback,
            utc_now(),
            "reused existing physical witness after powershell count failure",
        )

    raise RuntimeError("Could not derive physical witness from PowerShell count or fallback.")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def extract_int(pattern: str, text: str, source_name: str) -> int:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Could not derive {source_name} from pattern: {pattern}")
    return int(match.group(1))


def load_board_witness() -> tuple[int, Path, str]:
    pattern = r"(?:Workspace files observed|Board witness \(workspace scan\)|Board witness): `(\d+)`"
    candidates = [BOARD_STATUS_PATH, *BOARD_WITNESS_FALLBACK_PATHS]
    for path in candidates:
        if not path.exists():
            continue
        if path.suffix.lower() == ".json":
            payload = load_json(path)
            board_value = payload.get("witnesses", {}).get("board", {}).get("value")
            if board_value is not None:
                return int(board_value), path, "fallback from existing witness_hierarchy.json"
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(pattern, text)
        if match:
            provenance = (
                "parsed from canonical fallback witness surface"
                if path != BOARD_STATUS_PATH
                else "parsed from board status markdown"
            )
            return int(match.group(1)), path, provenance
    raise FileNotFoundError(
        f"Could not derive board witness from {BOARD_STATUS_PATH} or fallback surfaces."
    )


def derive_witness_hierarchy() -> dict:
    corpus_atlas = load_json(CORPUS_ATLAS_PATH)
    archive_atlas = load_json(ARCHIVE_ATLAS_PATH)
    promoted_state_text = PROMOTED_STATE_HEADER_PATH.read_text(encoding="utf-8")
    board, board_source_path, board_provenance = load_board_witness()

    generated_at = utc_now()
    physical, physical_timestamp, physical_provenance = count_physical_witness()
    indexed = len(corpus_atlas.get("records", []))
    archive = len(archive_atlas.get("records", []))
    archive_count = int(archive_atlas.get("archive_count", 0))
    promoted = extract_int(r"live_atlas_records: (\d+)", promoted_state_text, "promoted witness")

    return {
        "generated_at": generated_at,
        "workspace_root": str(WORKSPACE_ROOT),
        "derivation_version": "2026-03-09.q18.runtime",
        "derivation_command": DERIVATION_COMMAND,
        "ignore_dirs": sorted(IGNORE_DIRS),
        "witnesses": {
            "physical": {
                "label": "Physical witness",
                "value": physical,
                "meaning": "full workspace body on disk using runtime ignore rules",
                "source": str(WORKSPACE_ROOT),
                "source_timestamp": physical_timestamp,
                "provenance": physical_provenance,
            },
            "indexed": {
                "label": "Indexed witness",
                "value": indexed,
                "meaning": "live searchable records in corpus_atlas.json",
                "source": str(CORPUS_ATLAS_PATH),
                "source_timestamp": file_timestamp(CORPUS_ATLAS_PATH),
                "provenance": "len(corpus_atlas.records)",
            },
            "board": {
                "label": "Board witness",
                "value": board,
                "meaning": "workspace slice visible to the realtime board",
                "source": str(board_source_path),
                "source_timestamp": file_timestamp(board_source_path),
                "provenance": board_provenance,
            },
            "archive": {
                "label": "Archive witness",
                "value": archive,
                "meaning": "archive-backed records indexed but not yet promoted into live roots",
                "source": str(ARCHIVE_ATLAS_PATH),
                "source_timestamp": file_timestamp(ARCHIVE_ATLAS_PATH),
                "provenance": f"len(archive_atlas.records) across {archive_count} archives",
                "archive_count": archive_count,
            },
            "promoted": {
                "label": "Promoted witness",
                "value": promoted,
                "meaning": "promoted bronze nervous-system slice declared by the active bronze state header",
                "source": str(PROMOTED_STATE_HEADER_PATH),
                "source_timestamp": file_timestamp(PROMOTED_STATE_HEADER_PATH),
                "provenance": "parsed from live_atlas_records in bronze state header",
            },
        },
    }


def render_markdown(payload: dict) -> str:
    witnesses = payload["witnesses"]
    physical = witnesses["physical"]
    indexed = witnesses["indexed"]
    board = witnesses["board"]
    archive = witnesses["archive"]
    promoted = witnesses["promoted"]

    def section(name: str, block: dict) -> str:
        return (
            f"### {name}\n\n"
            f"- surface:\n"
            f"  `{block['source']}`\n"
            f"- current value:\n"
            f"  `{block['value']}`\n"
            f"- meaning:\n"
            f"  {block['meaning']}\n"
            f"- source timestamp:\n"
            f"  `{block['source_timestamp']}`\n"
            f"- provenance:\n"
            f"  {block['provenance']}\n"
        )

    return f"""# Canonical Witness Hierarchy

Date: `{payload['generated_at'][:10]}`
Generated: `{payload['generated_at']}`
Verdict: `OK`

This document defines the authoritative precedence of count-bearing witness surfaces inside Athena.

The problem is not that multiple counts exist.
The problem is that they are too often read as if they were measuring the same thing.

They are not.

## Why This Is Needed

Athena currently emits several real count signals:

- full filesystem body size
- board-visible workspace size
- indexed atlas record count
- archive-backed record count
- promoted nervous-system slice count

These counts are all valid inside their own scope.
They become harmful when treated as interchangeable.

## Canonical Precedence

Read witness surfaces in this order:

1. `Physical Witness`
2. `Indexed Witness`
3. `Board Witness`
4. `Archive Witness`
5. `Promoted Witness`

## Current Witness Values

{section("1. Physical Witness", physical)}
{section("2. Indexed Witness", indexed)}
{section("3. Board Witness", board)}
{section("4. Archive Witness", archive)}
{section("5. Promoted Witness", promoted)}

## Derivation Law

This hierarchy is machine-derived, not hand-propagated.

- command:
  `{payload['derivation_command']}`
- derivation version:
  `{payload['derivation_version']}`
- workspace root:
  `{payload['workspace_root']}`
- ignore dirs:
  `{", ".join(payload['ignore_dirs'])}`

## Interpretation Law

The correct reading is:

- `Physical witness: {physical['value']}` does not mean Athena has that many searchable source records
- `Indexed witness: {indexed['value']}` does not mean the whole disk only contains that many files
- `Board witness: {board['value']}` does not mean the board sees the full organism
- `Archive witness: {archive['value']}` does not mean archive mass is already live
- `Promoted witness: {promoted['value']}` does not mean the promoted slice is the whole corpus

Each count is true at a different layer.

## Promotion Law

When a summary surface must cite one number, it must also cite its witness class.

Approved examples:

- `Physical witness: {physical['value']}`
- `Indexed witness: {indexed['value']}`
- `Board witness: {board['value']}`
- `Archive witness: {archive['value']}`
- `Promoted witness: {promoted['value']}`

Unapproved examples:

- `Athena has {indexed['value']} files`
- `The corpus is {promoted['value']}`
- `The workspace is {board['value']}`

## Operational Consequences

1. whole-organism syntheses should cite at least `Physical` and `Indexed` witness together
2. runtime and board coordination documents should default to `Board` witness and then cite `Indexed` when needed
3. archive-promotion planning should cite `Archive` witness explicitly
4. nervous-system self-descriptions should stop inflating promoted slices into whole-corpus claims
5. family and manuscript promotion passes should cite `Promoted` witness only when describing what has already been metabolized

## Deep Meaning

The organism does not have one size.
It has one body expressed through multiple witness layers.

Those layers are not noise.
They are the depth structure of Athena's self-observation.
"""


def render_receipt(payload: dict) -> str:
    witnesses = payload["witnesses"]
    archive_count = witnesses["archive"].get("archive_count", 0)
    return f"""# Witness Hierarchy Derivation Receipt

- Generated: `{payload['generated_at']}`
- Quest: `Q18 Machine-Derive The Witness Hierarchy`
- Verdict: `OK`
- Command: `{payload['derivation_command']}`
- Derivation version: `{payload['derivation_version']}`

## Measured Values

- `Physical witness`: `{witnesses['physical']['value']}`
- `Indexed witness`: `{witnesses['indexed']['value']}`
- `Board witness`: `{witnesses['board']['value']}`
- `Archive witness`: `{witnesses['archive']['value']}`
- `Promoted witness`: `{witnesses['promoted']['value']}`

## Source Provenance

- physical witness:
  `{witnesses['physical']['provenance']}`
- indexed witness:
  `{witnesses['indexed']['provenance']}` from `{witnesses['indexed']['source']}` at `{witnesses['indexed']['source_timestamp']}`
- board witness:
  `{witnesses['board']['provenance']}` from `{witnesses['board']['source']}` at `{witnesses['board']['source_timestamp']}`
- archive witness:
  `{witnesses['archive']['provenance']}` from `{witnesses['archive']['source']}` at `{witnesses['archive']['source_timestamp']}`
- promoted witness:
  `{witnesses['promoted']['provenance']}` from `{witnesses['promoted']['source']}` at `{witnesses['promoted']['source_timestamp']}`

## Derivation Notes

- archive count observed alongside archive witness: `{archive_count}`
- board witness is intentionally smaller than indexed witness because the board is a control-plane-visible slice, not the whole searchable corpus
- promoted witness is intentionally smaller than indexed witness because it measures the currently metabolized nervous-system slice, not the whole organism
"""


def main() -> int:
    payload = derive_witness_hierarchy()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    REGISTRY_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    OUTPUT_RECEIPT_PATH.write_text(render_receipt(payload), encoding="utf-8")
    print(f"Wrote witness hierarchy json: {OUTPUT_JSON_PATH}")
    print(f"Wrote witness hierarchy registry mirror: {REGISTRY_JSON_PATH}")
    print(f"Wrote witness hierarchy markdown: {OUTPUT_MARKDOWN_PATH}")
    print(f"Wrote witness hierarchy receipt: {OUTPUT_RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
