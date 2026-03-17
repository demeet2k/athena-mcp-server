#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from canonical_manuscript_builder import DEFAULT_MANIFEST, build_manuscript_volumes, load_registry, resolve_path
from nervous_system_core import utc_now, write_json, write_text


PROJECT_ROOT = Path(__file__).resolve().parent
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
README_PATH = ACTIVE_ROOT / "README.md"
FULL_STACK_MANIFEST_PATH = ACTIVE_ROOT / "06_RUNTIME" / "12_full_stack_manifest.json"
AUDIT_RECEIPT_PATH = ACTIVE_ROOT / "06_RUNTIME" / "15_canonical_spine_audit.json"
LIVE_DOCS_GATE_PATH = ACTIVE_ROOT / "00_RECEIPTS" / "00_live_docs_gate_status.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the strict spine/supplements manuscript split.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--build-first", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def replace_or_append_section(text: str, heading: str, body_lines: list[str]) -> str:
    block = "\n".join([heading, "", *body_lines]).rstrip()
    pattern = re.compile(rf"\n{re.escape(heading)}\n(?:.*?)(?=\n## |\Z)", re.S)
    if heading in text:
        return pattern.sub("\n" + block + "\n", text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block + "\n"


def built_entries(registry: dict, volume: str) -> list[dict]:
    entries = [
        entry for entry in registry["entries"]
        if entry["volume"] == volume and entry.get("include_in_build", True) is not False
    ]
    return sorted(entries, key=lambda item: (item["order"], item["canonical_id"]))


def first_heading(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            return line.strip()
    return ""


def legacy_source_filenames(registry: dict) -> list[str]:
    return [
        Path(entry["source_file"]).name
        for entry in registry["entries"]
        if entry["status"] == "legacy-source"
    ]


def update_readme(receipt: dict) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    body = [
        "- Mode: `Strict Spine`",
        f"- Spine volume: `{Path(receipt['spine_output_path']).name}`",
        f"- Supplements volume: `{Path(receipt['supplements_output_path']).name}`",
        f"- Spine entries: `{receipt['spine_entry_count']}`",
        f"- Supplement entries: `{receipt['supplement_entry_count']}`",
        f"- Canonical chapter ids: `{', '.join(receipt['spine_chapter_ids'])}`",
        f"- Appendix ids: `{', '.join(receipt['appendix_ids'])}`",
        f"- Audit passed: `{receipt['audit']['passed']}`",
        f"- Live Google Docs: `{'BLOCKED' if receipt['live_docs_blocked'] else 'PASS'}`",
    ]
    updated = replace_or_append_section(text, "## Canonical Spine State", body)
    write_text(README_PATH, updated)


def update_full_stack_manifest(receipt: dict) -> None:
    manifest = json.loads(FULL_STACK_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest.setdefault("layers", {})
    manifest["layers"]["canonical_spine_registry"] = {
        "manifest": "canonical_manuscript_manifest.json",
        "strict_spine_mode": True,
        "spine_output_path": receipt["spine_output_path"],
        "supplements_output_path": receipt["supplements_output_path"],
        "spine_entry_count": receipt["spine_entry_count"],
        "supplement_entry_count": receipt["supplement_entry_count"],
        "spine_chapter_ids": receipt["spine_chapter_ids"],
        "appendix_ids": receipt["appendix_ids"],
        "supplements_moved_from_spine": receipt["supplements_moved_from_spine"],
        "audit_receipt": "06_RUNTIME/15_canonical_spine_audit.json",
        "audit_passed": receipt["audit"]["passed"],
        "live_docs_blocked": receipt["live_docs_blocked"],
    }
    write_json(FULL_STACK_MANIFEST_PATH, manifest)


def audit_manuscript(manifest_path: Path, build_first: bool) -> dict:
    volume_receipt = build_manuscript_volumes(manifest_path) if build_first else None
    registry = load_registry(manifest_path)
    base_dir = manifest_path.parent

    spine_output_path = resolve_path(base_dir, registry["outputs"]["spine"])
    supplements_output_path = resolve_path(base_dir, registry["outputs"]["supplements"])
    spine_text = spine_output_path.read_text(encoding="utf-8") if spine_output_path.exists() else ""
    supplements_text = supplements_output_path.read_text(encoding="utf-8") if supplements_output_path.exists() else ""

    spine_entries = built_entries(registry, "spine")
    supplement_entries = built_entries(registry, "supplements")
    legacy_filenames = legacy_source_filenames(registry)

    handoff_excluded = all("_handoff" not in entry["source_file"] for entry in spine_entries + supplement_entries)
    alternates_excluded = all("alternates" not in entry["source_file"] for entry in spine_entries + supplement_entries)

    legacy_filenames_absent = all(name not in spine_text for name in legacy_filenames)

    chapter_entries = [entry for entry in spine_entries if entry["kind"] == "chapter"]
    appendix_entries = [entry for entry in spine_entries if entry["kind"] == "appendix"]
    sections_dir = resolve_path(base_dir, registry["sections_dir"])
    chapter_heading_counts = {}
    for entry in chapter_entries:
        heading = first_heading(sections_dir / entry["source_file"])
        if heading:
            chapter_heading_counts[entry["canonical_id"]] = spine_text.count(heading)
    chapter_heading_uniqueness = all(count == 1 for count in chapter_heading_counts.values())

    max_chapter_order = max((entry["order"] for entry in chapter_entries), default=0)
    appendix_slots_valid = all(entry["order"] > max_chapter_order for entry in appendix_entries)

    live_docs_error = "Error: Missing OAuth client file: credentials.json"
    if LIVE_DOCS_GATE_PATH.exists():
        gate_text = LIVE_DOCS_GATE_PATH.read_text(encoding="utf-8")
        for line in gate_text.splitlines():
            if "Missing OAuth client file" in line:
                live_docs_error = line.strip()
                break

    receipt = {
        "generated_at": utc_now(),
        "registry_path": str(manifest_path),
        "strict_spine_mode": True,
        "live_docs_blocked": True,
        "live_docs_error": live_docs_error,
        "spine_output_path": str(spine_output_path),
        "supplements_output_path": str(supplements_output_path),
        "spine_entry_count": len(spine_entries),
        "supplement_entry_count": len(supplement_entries),
        "spine_chapter_ids": [entry["canonical_id"] for entry in chapter_entries],
        "appendix_ids": [entry["canonical_id"] for entry in appendix_entries],
        "supplements_moved_from_spine": [entry["canonical_id"] for entry in supplement_entries],
        "source_only_entries": [
            entry["canonical_id"] for entry in registry["entries"] if entry.get("include_in_build", True) is False
        ],
        "audit": {
            "handoff_excluded": handoff_excluded,
            "alternates_excluded": alternates_excluded,
            "legacy_filenames_absent_from_spine": legacy_filenames_absent,
            "chapter_heading_uniqueness": chapter_heading_uniqueness,
            "appendix_slots_valid": appendix_slots_valid,
            "passed": all(
                (
                    handoff_excluded,
                    alternates_excluded,
                    legacy_filenames_absent,
                    chapter_heading_uniqueness,
                    appendix_slots_valid,
                )
            ),
        },
    }
    if volume_receipt:
        receipt["build_receipt"] = volume_receipt
    return receipt


def main() -> int:
    args = parse_args()
    receipt = audit_manuscript(Path(args.manifest), build_first=args.build_first)
    write_json(AUDIT_RECEIPT_PATH, receipt)
    update_readme(receipt)
    update_full_stack_manifest(receipt)

    if args.as_json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"Wrote spine audit receipt: {AUDIT_RECEIPT_PATH}")
        print(f"Strict spine mode: {receipt['strict_spine_mode']}")
        print(f"Audit passed: {receipt['audit']['passed']}")
        print(f"Spine entries: {receipt['spine_entry_count']}")
        print(f"Supplement entries: {receipt['supplement_entry_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
