#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tesseract_metro_v4 import (
    PROFILE_VERSION,
    assign_ms_codes,
    current_sha256,
    build_duplicate_groups,
    build_rewrite_artifact,
    docs_gate_status,
    manifest_entry,
    normalize_relative_path,
    read_source,
    render_rewrite_markdown,
    select_source_records,
    sibling_output_path,
    truth_totals,
    utc_now,
    analyze_record,
)


DEFAULT_WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
DEFAULT_ATLAS = Path("self_actualize/corpus_atlas.json")
DEFAULT_MANIFEST = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_rewrites_manifest.json")
DEFAULT_ARCHIVE_MEMBER_MANIFEST = Path("DEEPER CRYSTALIZATION/_build/corpus_4d_archive_members_manifest.json")
DEFAULT_GATE = Path("self_actualize/live_docs_gate_status.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build sibling Mycelium Metro v4 rewrites for the corpus atlas.")
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--atlas", default=str(DEFAULT_ATLAS))
    parser.add_argument("--manifest-out", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--path-prefix")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def resolve_path(workspace_root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return (workspace_root / candidate).resolve()


def load_previous_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def previous_entry_map(previous_manifest: dict) -> dict[str, dict]:
    entries = previous_manifest.get("ms_registry") or []
    return {
        entry["relative_path"]: entry
        for entry in entries
        if isinstance(entry, dict) and "relative_path" in entry
    }


def is_unchanged(previous_entry: dict | None, output_path: Path, record_sha: str, docs_status: str) -> bool:
    if not previous_entry:
        return False
    return (
        previous_entry.get("source_sha256") == record_sha
        and previous_entry.get("profile_version") == PROFILE_VERSION
        and previous_entry.get("docs_gate_status") == docs_status
        and output_path.exists()
    )


def build_manifest(
    workspace_root: Path,
    atlas_path: Path,
    manifest_path: Path,
    docs_status: str,
    selected_count: int,
    written_count: int,
    skipped_count: int,
    excluded_records: list[object],
    duplicate_groups: list[dict[str, object]],
    registry_entries: list[dict[str, object]],
    path_prefix: str | None,
    limit: int | None,
) -> dict[str, object]:
    return {
        "generated_at": utc_now(),
        "profile_version": PROFILE_VERSION,
        "workspace_root": str(workspace_root),
        "atlas_path": normalize_relative_path(str(atlas_path)),
        "manifest_path": normalize_relative_path(str(manifest_path)),
        "docs_gate_status": docs_status,
        "selected_count": selected_count,
        "written_count": written_count,
        "skipped_unchanged_count": skipped_count,
        "path_prefix": path_prefix,
        "limit": limit,
        "excluded_paths": [{"relative_path": item.relative_path, "reason": item.reason} for item in excluded_records],
        "duplicate_groups": duplicate_groups,
        "truth_totals": truth_totals(registry_entries),
        "ms_registry": registry_entries,
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    workspace_root = Path(args.workspace_root).resolve()
    atlas_path = resolve_path(workspace_root, args.atlas)
    manifest_path = resolve_path(workspace_root, args.manifest_out)
    archive_member_manifest_path = resolve_path(workspace_root, str(DEFAULT_ARCHIVE_MEMBER_MANIFEST))
    gate_path = resolve_path(workspace_root, str(DEFAULT_GATE))

    docs_status = docs_gate_status(gate_path)
    selected_records, excluded_records = select_source_records(atlas_path, args.path_prefix, args.limit)
    ms_codes = assign_ms_codes(selected_records)
    live_sha_map = {record.relative_path: current_sha256(record) for record in selected_records}
    duplicate_group_map, duplicate_groups = build_duplicate_groups(selected_records, live_sha_map)
    previous_manifest = load_previous_manifest(manifest_path)
    previous_entries = previous_entry_map(previous_manifest)

    source_cache: dict[str, object] = {}
    analysis_cache: dict[str, dict[str, object]] = {}
    registry_entries: list[dict[str, object]] = []
    written_count = 0
    skipped_count = 0

    for record in selected_records:
        output_path = sibling_output_path(record)
        previous_entry = previous_entries.get(record.relative_path)
        live_sha = live_sha_map[record.relative_path]
        if not args.force and is_unchanged(previous_entry, output_path, live_sha, docs_status):
            registry_entries.append(previous_entry)
            skipped_count += 1
            continue

        source = source_cache.get(live_sha)
        if source is None:
            source = read_source(record)
            source_cache[live_sha] = source

        analysis = analysis_cache.get(live_sha)
        if analysis is None:
            analysis = analyze_record(record, source)
            analysis_cache[live_sha] = analysis

        artifact = build_rewrite_artifact(
            ms_codes[record.relative_path],
            record,
            docs_status,
            duplicate_group_map.get(record.relative_path),
            source,
            analysis,
        )
        markdown = render_rewrite_markdown(artifact, manifest_path, archive_member_manifest_path)
        if not args.dry_run:
            output_path.write_text(markdown, encoding="utf-8")
        registry_entries.append(manifest_entry(artifact, output_path, archive_member_manifest_path))
        written_count += 1

    registry_entries.sort(key=lambda item: item["relative_path"].lower())
    manifest = build_manifest(
        workspace_root=workspace_root,
        atlas_path=atlas_path,
        manifest_path=manifest_path,
        docs_status=docs_status,
        selected_count=len(selected_records),
        written_count=written_count,
        skipped_count=skipped_count,
        excluded_records=excluded_records,
        duplicate_groups=duplicate_groups,
        registry_entries=registry_entries,
        path_prefix=args.path_prefix,
        limit=args.limit,
    )
    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    args = parse_args()
    manifest = run(args)
    print(f"Docs gate: {manifest['docs_gate_status']}")
    print(f"Selected manuscripts: {manifest['selected_count']}")
    print(f"Writes: {manifest['written_count']}")
    print(f"Skipped unchanged: {manifest['skipped_unchanged_count']}")
    print(f"Manifest: {manifest['manifest_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
