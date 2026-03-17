#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nervous_system_core import write_text


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = PROJECT_ROOT / "canonical_manuscript_manifest.json"
VALID_KINDS = {"chapter", "appendix", "supplement"}
VALID_VOLUMES = {"spine", "supplements"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical manuscript volumes from the typed registry.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--volume", choices=["spine", "supplements", "all"], default="all")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def load_registry(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_path(base: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return (base / candidate).resolve()


def validate_entry(entry: dict) -> None:
    if entry["kind"] not in VALID_KINDS:
        raise ValueError(f"Invalid manuscript entry kind: {entry['kind']}")
    if entry["volume"] not in VALID_VOLUMES:
        raise ValueError(f"Invalid manuscript entry volume: {entry['volume']}")
    if "source_file" not in entry or "canonical_target_file" not in entry:
        raise ValueError(f"Missing source_file/canonical_target_file in manuscript entry: {entry.get('canonical_id')}")


def built_entries(registry: dict, volume: str) -> list[dict]:
    entries = []
    for entry in registry["entries"]:
        validate_entry(entry)
        if entry["volume"] != volume:
            continue
        if entry.get("include_in_build", True) is False:
            continue
        entries.append(entry)
    return sorted(entries, key=lambda item: (item["order"], item["canonical_id"]))


def source_only_entries(registry: dict) -> list[dict]:
    entries = []
    for entry in registry["entries"]:
        validate_entry(entry)
        if entry.get("include_in_build", True) is False:
            entries.append(entry)
    return sorted(entries, key=lambda item: (item["volume"], item["order"], item["canonical_id"]))


def build_volume(registry_path: Path, registry: dict, volume: str) -> dict:
    base_dir = registry_path.parent
    sections_dir = resolve_path(base_dir, registry["sections_dir"])
    output_path = resolve_path(base_dir, registry["outputs"][volume])
    entries = built_entries(registry, volume)

    source_paths = [sections_dir / entry["source_file"] for entry in entries]
    missing = [str(path) for path in source_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing {volume} manuscript sections: {missing}")

    merged_parts = []
    for path in source_paths:
        text = path.read_text(encoding="utf-8").strip()
        if text:
            merged_parts.append(text)

    write_text(output_path, "\n\n".join(merged_parts))
    return {
        "volume": volume,
        "output_path": str(output_path),
        "entry_count": len(entries),
        "entry_ids": [entry["canonical_id"] for entry in entries],
        "entry_files": [entry["source_file"] for entry in entries],
    }


def build_manuscript_volumes(manifest_path: Path) -> dict:
    registry = load_registry(manifest_path)
    base_dir = manifest_path.parent
    sections_dir = resolve_path(base_dir, registry["sections_dir"])
    receipt = {
        "manifest_path": str(manifest_path),
        "sections_dir": str(sections_dir),
        "strict_spine_mode": registry.get("strict_spine_mode", False),
        "volumes": {},
        "source_only_entries": [
            {
                "canonical_id": entry["canonical_id"],
                "status": entry["status"],
                "source_file": entry["source_file"],
            }
            for entry in source_only_entries(registry)
        ],
    }
    for volume in ("spine", "supplements"):
        receipt["volumes"][volume] = build_volume(manifest_path, registry, volume)
    return receipt


def build_canonical_manuscript(manifest_path: Path) -> dict:
    receipt = build_manuscript_volumes(manifest_path)
    spine = dict(receipt["volumes"]["spine"])
    spine["manifest_path"] = receipt["manifest_path"]
    spine["sections_dir"] = receipt["sections_dir"]
    return spine


def main() -> int:
    args = parse_args()
    receipt = build_manuscript_volumes(Path(args.manifest))

    if args.as_json:
        if args.volume == "all":
            print(json.dumps(receipt, indent=2))
        else:
            print(json.dumps(receipt["volumes"][args.volume], indent=2))
        return 0

    if args.volume == "all":
        print(f"Wrote canonical spine: {receipt['volumes']['spine']['output_path']}")
        print(f"Wrote supplements volume: {receipt['volumes']['supplements']['output_path']}")
        print(f"Spine entries: {receipt['volumes']['spine']['entry_count']}")
        print(f"Supplement entries: {receipt['volumes']['supplements']['entry_count']}")
    else:
        volume = receipt["volumes"][args.volume]
        print(f"Wrote {args.volume} volume: {volume['output_path']}")
        print(f"Entries merged: {volume['entry_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
