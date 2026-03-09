from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
import zipfile


EXCLUDED_PARTS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "node_modules",
}


@dataclass
class LiveFile:
    relative_path: str
    normalized_path: str
    basename: str


@dataclass
class ArchiveEntry:
    archive_relative_path: str
    archive_normalized_path: str
    entry_path: str
    normalized_entry_path: str
    basename: str


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip("/").lower()


def should_skip(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    lowered = {part.lower() for part in parts}
    return any(part in lowered for part in EXCLUDED_PARTS)


def iter_live_files(root: Path) -> list[LiveFile]:
    files: list[LiveFile] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path, root):
            continue
        relative_path = str(path.relative_to(root))
        normalized = normalize_path(relative_path)
        files.append(
            LiveFile(
                relative_path=relative_path,
                normalized_path=normalized,
                basename=Path(relative_path).name.lower(),
            )
        )
    return files


def iter_archive_entries(root: Path) -> tuple[list[ArchiveEntry], list[str]]:
    entries: list[ArchiveEntry] = []
    warnings: list[str] = []
    for archive_path in root.rglob("*.zip"):
        if should_skip(archive_path, root):
            continue
        archive_relative_path = str(archive_path.relative_to(root))
        archive_normalized_path = normalize_path(archive_relative_path)
        try:
            with zipfile.ZipFile(archive_path) as zf:
                for name in zf.namelist():
                    if name.endswith("/"):
                        continue
                    normalized_entry_path = normalize_path(name)
                    basename = Path(name).name.lower()
                    entries.append(
                        ArchiveEntry(
                            archive_relative_path=archive_relative_path,
                            archive_normalized_path=archive_normalized_path,
                            entry_path=name,
                            normalized_entry_path=normalized_entry_path,
                            basename=basename,
                        )
                    )
        except zipfile.BadZipFile:
            warnings.append(f"Bad zip archive skipped: {archive_relative_path}")
    return entries, warnings


def longest_common_suffix_segments(left: str, right: str) -> int:
    left_parts = left.split("/")
    right_parts = right.split("/")
    count = 0
    for left_part, right_part in zip(reversed(left_parts), reversed(right_parts)):
        if left_part != right_part:
            break
        count += 1
    return count


def wrapper_prefix(full_path: str, suffix_path: str) -> str:
    if full_path == suffix_path:
        return ""
    if not full_path.endswith(suffix_path):
        return ""
    return full_path[: -len(suffix_path)].strip("/")


def trim_list(items: list[str], limit: int = 5) -> list[str]:
    return items[:limit]


def build_indexes(
    live_files: list[LiveFile],
    archive_entries: list[ArchiveEntry],
) -> dict[str, Any]:
    live_exact: dict[str, list[LiveFile]] = defaultdict(list)
    live_basename: dict[str, list[LiveFile]] = defaultdict(list)
    for item in live_files:
        live_exact[item.normalized_path].append(item)
        live_basename[item.basename].append(item)

    archive_exact: dict[str, list[ArchiveEntry]] = defaultdict(list)
    archive_basename: dict[str, list[ArchiveEntry]] = defaultdict(list)
    for item in archive_entries:
        archive_exact[item.normalized_entry_path].append(item)
        archive_basename[item.basename].append(item)

    return {
        "live_exact": live_exact,
        "live_basename": live_basename,
        "archive_exact": archive_exact,
        "archive_basename": archive_basename,
    }


def match_scan_record(
    rel_path: str,
    live_files: list[LiveFile],
    archive_entries: list[ArchiveEntry],
    indexes: dict[str, Any],
) -> dict[str, Any]:
    normalized_rel_path = normalize_path(rel_path)
    basename = Path(rel_path).name.lower()
    rel_path_segments = len([part for part in normalized_rel_path.split("/") if part])

    live_exact_matches = indexes["live_exact"].get(normalized_rel_path, [])
    archive_exact_matches = indexes["archive_exact"].get(normalized_rel_path, [])

    live_suffix_matches = [
        item
        for item in live_files
        if item.normalized_path != normalized_rel_path and item.normalized_path.endswith(normalized_rel_path)
    ]
    archive_suffix_matches = [
        item
        for item in archive_entries
        if item.normalized_entry_path != normalized_rel_path
        and item.normalized_entry_path.endswith(normalized_rel_path)
    ]

    live_basename_matches = indexes["live_basename"].get(basename, [])
    archive_basename_matches = indexes["archive_basename"].get(basename, [])

    best_status = "unresolved"
    if live_exact_matches:
        best_status = "live_exact"
    elif live_suffix_matches:
        best_status = "live_suffix"
    elif archive_exact_matches:
        best_status = "archive_exact"
    elif archive_suffix_matches:
        best_status = "archive_suffix"
    elif live_basename_matches or archive_basename_matches:
        best_status = "basename_only"

    live_root_hints = Counter()
    for item in live_suffix_matches:
        prefix = wrapper_prefix(item.normalized_path, normalized_rel_path)
        live_root_hints[prefix or "."] += 1

    archive_hints = Counter()
    for item in archive_exact_matches:
        archive_hints[f"{item.archive_relative_path}::(root)"] += 1
    for item in archive_suffix_matches:
        prefix = wrapper_prefix(item.normalized_entry_path, normalized_rel_path)
        archive_hints[f"{item.archive_relative_path}::{prefix or '(root)'}"] += 1

    nearest_live = sorted(
        live_basename_matches,
        key=lambda item: (
            -longest_common_suffix_segments(item.normalized_path, normalized_rel_path),
            len(item.normalized_path),
        ),
    )
    nearest_archives = sorted(
        archive_basename_matches,
        key=lambda item: (
            -longest_common_suffix_segments(item.normalized_entry_path, normalized_rel_path),
            len(item.normalized_entry_path),
        ),
    )

    return {
        "rel_path": rel_path,
        "normalized_rel_path": normalized_rel_path,
        "basename": basename,
        "path_depth": rel_path_segments,
        "best_status": best_status,
        "live_exact_paths": [item.relative_path for item in live_exact_matches],
        "live_suffix_paths": trim_list([item.relative_path for item in live_suffix_matches], limit=6),
        "archive_exact_paths": trim_list(
            [f"{item.archive_relative_path}::{item.entry_path}" for item in archive_exact_matches],
            limit=6,
        ),
        "archive_suffix_paths": trim_list(
            [f"{item.archive_relative_path}::{item.entry_path}" for item in archive_suffix_matches],
            limit=6,
        ),
        "live_basename_paths": trim_list([item.relative_path for item in nearest_live], limit=6),
        "archive_basename_paths": trim_list(
            [f"{item.archive_relative_path}::{item.entry_path}" for item in nearest_archives],
            limit=6,
        ),
        "live_root_hints": live_root_hints.most_common(3),
        "archive_hints": archive_hints.most_common(3),
    }


def project_overview(project: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(record["best_status"] for record in records)
    live_roots = Counter()
    archive_roots = Counter()
    for record in records:
        primary_live_root = record["live_root_hints"][:1]
        primary_archive_root = record["archive_hints"][:1]
        for root, hits in primary_live_root:
            live_roots[root] += hits
        for root, hits in primary_archive_root:
            archive_roots[root] += hits

    strong_hits = (
        status_counts["live_exact"]
        + status_counts["live_suffix"]
        + status_counts["archive_exact"]
        + status_counts["archive_suffix"]
    )
    total = len(records)
    unresolved = status_counts["unresolved"]
    basename_only = status_counts["basename_only"]
    live_backed = status_counts["live_exact"] + status_counts["live_suffix"]
    archive_backed = status_counts["archive_exact"] + status_counts["archive_suffix"]

    diagnosis = "mixed_state"
    if strong_hits == total and archive_backed == total:
        diagnosis = "archive_backed_complete"
    elif strong_hits == total and live_backed == total:
        diagnosis = "live_backed_complete"
    elif unresolved == total:
        diagnosis = "unresolved"
    elif unresolved > 0:
        diagnosis = "partial_recovery"
    elif basename_only > 0:
        diagnosis = "basename_only_recovery"

    return {
        "project": project,
        "record_count": total,
        "status_counts": dict(status_counts),
        "coverage": {
            "strong_match_count": strong_hits,
            "strong_match_ratio": round((strong_hits / total) if total else 0.0, 4),
            "live_backed_count": live_backed,
            "archive_backed_count": archive_backed,
            "basename_only_count": basename_only,
            "unresolved_count": unresolved,
        },
        "diagnosis": diagnosis,
        "likely_live_roots": [
            {"root": root, "hits": hits}
            for root, hits in live_roots.most_common(5)
        ],
        "likely_archives": [
            {"root": root, "hits": hits}
            for root, hits in archive_roots.most_common(5)
        ],
        "sample_strong_matches": [
            {
                "rel_path": record["rel_path"],
                "best_status": record["best_status"],
                "example": (
                    record["live_exact_paths"]
                    or record["live_suffix_paths"]
                    or record["archive_exact_paths"]
                    or record["archive_suffix_paths"]
                )[:1]
            }
            for record in records
            if record["best_status"] in {"live_exact", "live_suffix", "archive_exact", "archive_suffix"}
        ][:5],
        "sample_basename_only": [
            {
                "rel_path": record["rel_path"],
                "live_basename_paths": record["live_basename_paths"][:2],
                "archive_basename_paths": record["archive_basename_paths"][:2],
            }
            for record in records
            if record["best_status"] == "basename_only"
        ][:5],
        "sample_unresolved": [
            record["rel_path"]
            for record in records
            if record["best_status"] == "unresolved"
        ][:8],
    }


def build_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Scan Reconciliation Report",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Scope",
        "",
        f"- Workspace root: `{payload['workspace_root']}`",
        f"- Scan source: `{payload['scan_source']}`",
        f"- Scan records: `{summary['scan_record_count']}`",
        f"- Live files scanned: `{summary['live_file_count']}`",
        f"- ZIP archives scanned: `{summary['zip_archive_count']}`",
        f"- ZIP entries scanned: `{summary['zip_entry_count']}`",
        "",
        "## Global Status",
        "",
    ]

    for status, count in sorted(summary["best_status_counts"].items()):
        lines.append(f"- `{status}`: `{count}`")

    if summary["warnings"]:
        lines.extend(["", "## Warnings", ""])
        for warning in summary["warnings"]:
            lines.append(f"- {warning}")

    lines.extend(["", "## Project Analysis", ""])
    for project in payload["projects"]:
        coverage = project["coverage"]
        lines.extend(
            [
                f"### {project['project']}",
                "",
                f"- Diagnosis: `{project['diagnosis']}`",
                f"- Records: `{project['record_count']}`",
                f"- Strong matches: `{coverage['strong_match_count']}` ({coverage['strong_match_ratio']:.2%})",
                f"- Live-backed: `{coverage['live_backed_count']}`",
                f"- Archive-backed: `{coverage['archive_backed_count']}`",
                f"- Basename-only: `{coverage['basename_only_count']}`",
                f"- Unresolved: `{coverage['unresolved_count']}`",
            ]
        )

        if project["likely_live_roots"]:
            lines.append("- Likely live roots:")
            for item in project["likely_live_roots"]:
                lines.append(f"  - `{item['root']}` ({item['hits']} hits)")

        if project["likely_archives"]:
            lines.append("- Likely archives:")
            for item in project["likely_archives"]:
                lines.append(f"  - `{item['root']}` ({item['hits']} hits)")

        if project["sample_strong_matches"]:
            lines.append("- Strong match samples:")
            for item in project["sample_strong_matches"]:
                example = item["example"][0] if item["example"] else "n/a"
                lines.append(f"  - `{item['rel_path']}` -> `{item['best_status']}` via `{example}`")

        if project["sample_basename_only"]:
            lines.append("- Basename-only samples:")
            for item in project["sample_basename_only"]:
                evidence = item["live_basename_paths"] or item["archive_basename_paths"] or ["n/a"]
                lines.append(f"  - `{item['rel_path']}` -> `{evidence[0]}`")

        if project["sample_unresolved"]:
            lines.append("- Unresolved samples:")
            for item in project["sample_unresolved"]:
                lines.append(f"  - `{item}`")

        lines.append("")

    return "\n".join(lines).strip() + "\n"


def reconcile(
    workspace_root: Path,
    scan_source: Path,
    output_json: Path,
    output_report: Path,
) -> dict[str, Any]:
    raw_scan = json.loads(scan_source.read_text(encoding="utf-8"))
    if not isinstance(raw_scan, list):
        raise ValueError("Unified scan payload must be a list of records.")

    live_files = iter_live_files(workspace_root)
    archive_entries, warnings = iter_archive_entries(workspace_root)
    indexes = build_indexes(live_files, archive_entries)

    records_by_project: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in raw_scan:
        project = str(item.get("project", "UNKNOWN"))
        rel_path = str(item.get("rel_path", "")).strip()
        if not rel_path:
            continue
        record = match_scan_record(rel_path, live_files, archive_entries, indexes)
        record["project"] = project
        records_by_project[project].append(record)

    project_payloads = [
        {
            **project_overview(project, records),
            "records": records,
        }
        for project, records in sorted(records_by_project.items())
    ]

    global_status_counts = Counter()
    for project in project_payloads:
        global_status_counts.update(project["status_counts"])

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace_root": str(workspace_root),
        "scan_source": str(scan_source),
        "summary": {
            "scan_record_count": sum(len(project["records"]) for project in project_payloads),
            "project_count": len(project_payloads),
            "live_file_count": len(live_files),
            "zip_archive_count": len({item.archive_relative_path for item in archive_entries}),
            "zip_entry_count": len(archive_entries),
            "best_status_counts": dict(global_status_counts),
            "warnings": warnings,
        },
        "projects": project_payloads,
    }

    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_report.write_text(build_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    workspace_root = Path(__file__).resolve().parents[2]
    default_scan_source = workspace_root / "MATH" / "FINAL FORM" / "FRAMEWORKS CODE" / "Unified SCAN JSON.json"
    default_output_json = workspace_root / "self_actualize" / "scan_reconciliation.json"
    default_output_report = workspace_root / "self_actualize" / "scan_reconciliation_report.md"

    parser = argparse.ArgumentParser(
        description="Reconcile Unified SCAN JSON records against the live Athena Agent workspace.",
    )
    parser.add_argument(
        "--workspace-root",
        default=str(workspace_root),
        help="Workspace root to scan for live files and archives.",
    )
    parser.add_argument(
        "--scan-source",
        default=str(default_scan_source),
        help="Path to Unified SCAN JSON.json.",
    )
    parser.add_argument(
        "--output-json",
        default=str(default_output_json),
        help="Path to write the machine-readable reconciliation payload.",
    )
    parser.add_argument(
        "--output-report",
        default=str(default_output_report),
        help="Path to write the markdown reconciliation report.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace_root = Path(args.workspace_root).resolve()
    scan_source = Path(args.scan_source).resolve()
    output_json = Path(args.output_json).resolve()
    output_report = Path(args.output_report).resolve()

    if not scan_source.exists():
        raise FileNotFoundError(f"Scan source not found: {scan_source}")

    reconcile(
        workspace_root=workspace_root,
        scan_source=scan_source,
        output_json=output_json,
        output_report=output_report,
    )


if __name__ == "__main__":
    main()
