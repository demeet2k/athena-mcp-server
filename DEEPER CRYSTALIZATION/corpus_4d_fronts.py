#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from nervous_system_core import CHAPTERS
from tesseract_metro_v4 import (
    ALLOWED_SOURCE_EXTENSIONS,
    DERIVATIVE_DENYLIST,
    LENS_LABELS,
    PROFILE_VERSION,
    SelectedRecord,
    analyze_record,
    chapter_station_label,
    normalize_relative_path,
    presentation_name,
    read_archive_members,
    select_source_records,
    sha256_for_path,
    sibling_output_path,
    utc_now,
)

REQUIRED_REWRITE_MARKERS = (
    "Primary hubs:",
    "Tunnel:",
    "Truth state:",
    "## **Square**",
    "## **Flower**",
    "## **Cloud**",
    "## **Fractal**",
    "## **Crystal Tile**",
    "## **Support Graph**",
    "## **Replay Hooks**",
)

REQUIRED_TILE_ROWS = tuple(f"- {lens}{facet}:" for lens in ("S", "F", "C", "R") for facet in ("1", "2", "3", "4"))


def resolve_path(workspace_root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return (workspace_root / candidate).resolve()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _top_level(relative_path: str) -> str:
    return relative_path.split("/", 1)[0] if "/" in relative_path else relative_path


def _find_sibling_source_for_output(workspace_root: Path, relative_output_path: str) -> str | None:
    if not relative_output_path.endswith(".4d.md"):
        return None
    base_relative_path = relative_output_path[:-len(".4d.md")]
    base_path = workspace_root / Path(base_relative_path)
    for extension in sorted(ALLOWED_SOURCE_EXTENSIONS):
        candidate = base_path.with_name(f"{base_path.name}{extension}")
        if candidate.exists():
            return normalize_relative_path(str(candidate.relative_to(workspace_root)))
    return None


def rewrite_contract_issues(text: str) -> list[str]:
    issues: list[str] = []
    if not text.startswith("**["):
        issues.append("missing-banner")
    for marker in REQUIRED_REWRITE_MARKERS:
        if marker not in text:
            issues.append(f"missing:{marker}")
    for row in REQUIRED_TILE_ROWS:
        if row not in text:
            issues.append(f"missing:{row}")
    return issues


def _audit_status_map(audit_receipt: dict) -> dict[str, dict[str, object]]:
    explicit = audit_receipt.get("audit_status_by_relative_path")
    if isinstance(explicit, dict):
        return explicit

    missing = {item["relative_path"] for item in audit_receipt.get("missing_outputs", [])}
    stale = {item["relative_path"] for item in audit_receipt.get("stale_outputs", [])}
    failure_map = {
        item["relative_path"]: item.get("issues", [])
        for item in audit_receipt.get("contract_failures", [])
    }
    status_map: dict[str, dict[str, object]] = {}
    for relative_path in missing | stale | set(failure_map):
        issues = list(failure_map.get(relative_path, []))
        status_map[relative_path] = {
            "contract_ok": not issues and relative_path not in missing,
            "missing_output": relative_path in missing,
            "stale_source": relative_path in stale,
            "issue_count": len(issues),
            "issues": issues,
        }
    return status_map


def audit_corpus_4d_rewrites(workspace_root: Path, manifest_path: Path) -> dict[str, object]:
    manifest = load_json(manifest_path)
    entries = sorted(manifest.get("ms_registry", []), key=lambda item: item["relative_path"].lower())
    expected_outputs = {
        normalize_relative_path(str(resolve_path(workspace_root, entry["output_path"])))
        for entry in entries
    }

    missing_outputs: list[dict[str, object]] = []
    stale_outputs: list[dict[str, object]] = []
    contract_failures: list[dict[str, object]] = []
    audit_status_by_relative_path: dict[str, dict[str, object]] = {}

    for entry in entries:
        relative_path = entry["relative_path"]
        source_path = resolve_path(workspace_root, relative_path)
        output_path = resolve_path(workspace_root, entry["output_path"])
        missing_output = not output_path.exists()
        current_source_sha = sha256_for_path(source_path) if source_path.exists() else None
        stale_source = current_source_sha != entry.get("source_sha256")

        if missing_output:
            missing_outputs.append(
                {
                    "relative_path": relative_path,
                    "output_path": normalize_relative_path(str(output_path)),
                }
            )

        issues: list[str] = []
        if not missing_output:
            text = output_path.read_text(encoding="utf-8", errors="ignore")
            issues = rewrite_contract_issues(text)
            if issues:
                contract_failures.append(
                    {
                        "relative_path": relative_path,
                        "output_path": normalize_relative_path(str(output_path)),
                        "issues": issues,
                    }
                )

        if stale_source:
            stale_outputs.append(
                {
                    "relative_path": relative_path,
                    "source_path": normalize_relative_path(str(source_path)),
                    "manifest_source_sha256": entry.get("source_sha256"),
                    "current_source_sha256": current_source_sha,
                    "reason": "missing-source" if current_source_sha is None else "sha-mismatch",
                }
            )

        audit_status_by_relative_path[relative_path] = {
            "contract_ok": not issues and not missing_output,
            "missing_output": missing_output,
            "stale_source": stale_source,
            "issue_count": len(issues),
            "issues": issues,
        }

    orphan_outputs: list[dict[str, object]] = []
    seen_orphans: set[str] = set()
    skip_dirnames = {".git", "__pycache__", ".venv", "node_modules"}
    for dirpath, dirnames, filenames in os.walk(workspace_root):
        dirnames[:] = [name for name in dirnames if name not in skip_dirnames]
        for filename in filenames:
            if not filename.endswith(".4d.md"):
                continue
            path = Path(dirpath) / filename
            relative_output_path = normalize_relative_path(str(path.relative_to(workspace_root)))
            normalized_output_path = normalize_relative_path(str(path))
            if normalized_output_path in expected_outputs or relative_output_path in seen_orphans:
                continue
            orphan_outputs.append(
                {
                    "relative_path": relative_output_path,
                    "output_path": normalized_output_path,
                    "sibling_source": _find_sibling_source_for_output(workspace_root, relative_output_path),
                    "evidence": "filesystem-full-scan",
                }
            )
            seen_orphans.add(relative_output_path)

    clean_entries = sum(
        1
        for status in audit_status_by_relative_path.values()
        if status["contract_ok"] and not status["stale_source"]
    )
    receipt = {
        "generated_at": utc_now(),
        "profile_version": PROFILE_VERSION,
        "manifest_path": normalize_relative_path(str(manifest_path)),
        "docs_gate_status": manifest.get("docs_gate_status", "UNKNOWN"),
        "summary": {
            "entry_count": len(entries),
            "clean_entry_count": clean_entries,
            "missing_output_count": len(missing_outputs),
            "orphan_output_count": len(orphan_outputs),
            "stale_output_count": len(stale_outputs),
            "contract_failure_count": len(contract_failures),
        },
        "missing_outputs": sorted(missing_outputs, key=lambda item: item["relative_path"].lower()),
        "orphan_outputs": sorted(orphan_outputs, key=lambda item: item["relative_path"].lower()),
        "stale_outputs": sorted(stale_outputs, key=lambda item: item["relative_path"].lower()),
        "contract_failures": sorted(contract_failures, key=lambda item: item["relative_path"].lower()),
        "audit_status_by_relative_path": audit_status_by_relative_path,
    }
    return receipt


def build_archive_member_manifest(
    workspace_root: Path,
    main_manifest_path: Path,
    output_path: Path,
) -> dict[str, object]:
    main_manifest = load_json(main_manifest_path)
    entries = sorted(main_manifest.get("ms_registry", []), key=lambda item: item["relative_path"].lower())
    member_records: list[dict[str, object]] = []
    parents: list[dict[str, object]] = []

    for entry in entries:
        relative_path = entry["relative_path"]
        if not relative_path.lower().endswith(".zip"):
            continue

        source_path = resolve_path(workspace_root, relative_path)
        parent_record = SelectedRecord(
            record_id=f"{entry['ms_code']}-zip",
            relative_path=relative_path,
            absolute_path=str(source_path),
            extension=".zip",
            sha256=entry["source_sha256"],
            title=presentation_name(Path(relative_path).stem),
            excerpt="",
            headings=(presentation_name(Path(relative_path).stem),),
            role_tags=("manuscript",),
        )
        readable_members = [
            item
            for item in read_archive_members(parent_record)
            if item["source"].truth_state != "FAIL"
        ] if source_path.exists() else []

        member_summaries: list[dict[str, object]] = []
        chapter_set: set[str] = set()
        lens_set: set[str] = set()
        appendix_set: set[str] = set()

        for member in readable_members:
            member_name = member["member_path"]
            source = member["source"]
            member_record = SelectedRecord(
                record_id=f"{entry['ms_code']}::{member_name}",
                relative_path=f"{relative_path}::{member_name}",
                absolute_path=str(source_path),
                extension=f".{member['read_mode']}",
                sha256=member["member_sha256"],
                title=source.title,
                excerpt=source.full_text[:500],
                headings=tuple(source.headings),
                role_tags=("manuscript",),
            )
            analysis = analyze_record(member_record, source)
            summary = {
                "parent_relative_path": relative_path,
                "parent_ms_code": entry["ms_code"],
                "member_path": member_name,
                "member_sha256": member["member_sha256"],
                "member_size_bytes": member["member_size_bytes"],
                "read_mode": member["read_mode"],
                "home_chapter": analysis["home_chapter"].code,
                "secondary_chapters": [chapter.code for chapter in analysis["secondary_chapters"]],
                "appendices": [code for code, _, _ in analysis["appendices"]],
                "dominant_lens": analysis["dominant_lens"],
                "dominant_facet": analysis["dominant_facet"],
                "truth_state": source.truth_state,
                "family": analysis["family"],
                "z_point": analysis["z_point"],
                "primary_hubs": analysis["route_plan"].primary_hubs,
            }
            member_summaries.append(summary)
            chapter_set.add(summary["home_chapter"])
            lens_set.add(summary["dominant_lens"])
            appendix_set.update(summary["appendices"])

        parent_status = "AMBIG" if len(readable_members) > 1 else ("NEAR" if len(readable_members) == 1 else "FAIL")
        parents.append(
            {
                "parent_relative_path": relative_path,
                "chosen_archive_member": entry.get("chosen_archive_member"),
                "archive_candidate_count": len(readable_members),
                "archive_member_manifest_path": (
                    normalize_relative_path(str(output_path))
                    if len(readable_members) > 1
                    else None
                ),
                "truth_state": parent_status,
                "disagreement_summary": {
                    "home_chapters": sorted(chapter_set),
                    "dominant_lenses": sorted(lens_set),
                    "appendices": sorted(appendix_set),
                    "diverges_by_home_chapter": len(chapter_set) > 1,
                    "diverges_by_lens": len(lens_set) > 1,
                    "diverges_by_appendix": len(appendix_set) > 1 and len(readable_members) > 1,
                },
            }
        )

        member_records.extend(member_summaries)

    receipt = {
        "generated_at": utc_now(),
        "profile_version": PROFILE_VERSION,
        "source_manifest_path": normalize_relative_path(str(main_manifest_path)),
        "output_path": normalize_relative_path(str(output_path)),
        "docs_gate_status": main_manifest.get("docs_gate_status", "UNKNOWN"),
        "summary": {
            "zip_parent_count": len(parents),
            "multi_candidate_parent_count": sum(1 for parent in parents if parent["archive_candidate_count"] > 1),
            "single_candidate_parent_count": sum(1 for parent in parents if parent["archive_candidate_count"] == 1),
            "zero_candidate_parent_count": sum(1 for parent in parents if parent["archive_candidate_count"] == 0),
            "member_record_count": len(member_records),
        },
        "parents": parents,
        "member_records": sorted(member_records, key=lambda item: (item["parent_relative_path"].lower(), item["member_path"].lower())),
    }
    return receipt


def build_corpus_4d_registry(
    main_manifest_path: Path,
    audit_path: Path,
    archive_manifest_path: Path,
) -> dict[str, object]:
    main_manifest = load_json(main_manifest_path)
    audit_receipt = load_json(audit_path)
    archive_receipt = load_json(archive_manifest_path) if archive_manifest_path.exists() else {"member_records": [], "parents": []}

    audit_status = _audit_status_map(audit_receipt)
    archive_counts: Counter[str] = Counter(item["parent_relative_path"] for item in archive_receipt.get("member_records", []))
    archive_paths: dict[str, list[str]] = defaultdict(list)
    for item in archive_receipt.get("member_records", []):
        archive_paths[item["parent_relative_path"]].append(item["member_path"])

    nodes: list[dict[str, object]] = []
    for entry in sorted(main_manifest.get("ms_registry", []), key=lambda item: (item["ms_code"], item["relative_path"].lower())):
        relative_path = entry["relative_path"]
        node = dict(entry)
        node["audit_status"] = audit_status.get(relative_path, entry.get("audit_status"))
        node["archive_member_count"] = archive_counts.get(relative_path, 0)
        node["archive_member_paths"] = sorted(archive_paths.get(relative_path, []))
        nodes.append(node)

    indices: dict[str, dict[str, list[str]]] = {
        "by_ms_code": {},
        "by_relative_path": {},
        "by_home_chapter": defaultdict(list),
        "by_appendix": defaultdict(list),
        "by_dominant_lens": defaultdict(list),
        "by_truth_state": defaultdict(list),
        "by_family": defaultdict(list),
        "by_duplicate_group": defaultdict(list),
    }
    for node in nodes:
        relative_path = node["relative_path"]
        indices["by_ms_code"][node["ms_code"]] = [relative_path]
        indices["by_relative_path"][relative_path] = [node["ms_code"]]
        indices["by_home_chapter"][node["home_chapter"]].append(relative_path)
        indices["by_dominant_lens"][node["dominant_lens"]].append(relative_path)
        indices["by_truth_state"][node["truth_state"]].append(relative_path)
        indices["by_family"][node["family"]].append(relative_path)
        indices["by_duplicate_group"][node["duplicate_group"] or "unique"].append(relative_path)
        for appendix in node.get("appendices", []):
            indices["by_appendix"][appendix].append(relative_path)

    chapter_lookup = {chapter.code: chapter for chapter in CHAPTERS}
    chapter_counts = Counter(node["home_chapter"] for node in nodes)
    lens_counts = Counter(node["dominant_lens"] for node in nodes)
    appendix_counts = Counter(appendix for node in nodes for appendix in node.get("appendices", []))
    arc_counts = Counter(chapter_lookup[node["home_chapter"]].arc for node in nodes)
    lane_counts = Counter(chapter_lookup[node["home_chapter"]].lane for node in nodes)

    return {
        "generated_at": utc_now(),
        "profile_version": PROFILE_VERSION,
        "main_manifest_path": normalize_relative_path(str(main_manifest_path)),
        "audit_path": normalize_relative_path(str(audit_path)),
        "archive_member_manifest_path": normalize_relative_path(str(archive_manifest_path)),
        "docs_gate_status": main_manifest.get("docs_gate_status", "UNKNOWN"),
        "summary": {
            "node_count": len(nodes),
            "truth_totals": main_manifest.get("truth_totals", {}),
            "chapter_counts": dict(sorted(chapter_counts.items())),
            "arc_counts": dict(sorted(arc_counts.items())),
            "lane_counts": dict(sorted(lane_counts.items())),
            "lens_counts": dict(sorted(lens_counts.items())),
            "appendix_counts": dict(sorted(appendix_counts.items())),
            "duplicate_group_count": sum(1 for key in indices["by_duplicate_group"] if key != "unique"),
            "ambig_archive_parent_count": sum(1 for node in nodes if node["truth_state"] == "AMBIG" and node["relative_path"].lower().endswith(".zip")),
        },
        "nodes": nodes,
        "indices": {name: dict(sorted(index.items())) for name, index in indices.items()},
    }


def classify_corpus_4d_orphans(
    workspace_root: Path,
    main_manifest_path: Path,
    audit_path: Path,
    output_path: Path,
) -> dict[str, object]:
    manifest = load_json(main_manifest_path)
    audit_receipt = load_json(audit_path)
    atlas_path = resolve_path(workspace_root, manifest["atlas_path"])
    atlas = load_json(atlas_path)
    selected_records, excluded_records = select_source_records(atlas_path)

    selected_paths = {record.relative_path for record in selected_records}
    excluded_by_path = {item.relative_path: item.reason for item in excluded_records}
    expected_outputs = {
        normalize_relative_path(str(resolve_path(workspace_root, entry["output_path"]).relative_to(workspace_root)))
        for entry in manifest.get("ms_registry", [])
    }

    atlas_records_by_path = {
        normalize_relative_path(record["relative_path"]): record
        for record in atlas.get("records", [])
    }
    candidate_paths: set[str] = {
        item["relative_path"]
        for item in audit_receipt.get("orphan_outputs", [])
    }
    candidate_paths.update(
        path for path in atlas_records_by_path
        if path.endswith(".4d.md")
    )

    classified: list[dict[str, object]] = []
    for relative_output_path in sorted(candidate_paths):
        if relative_output_path in expected_outputs:
            continue
        sibling_source = _find_sibling_source_for_output(workspace_root, relative_output_path)
        atlas_record = atlas_records_by_path.get(relative_output_path)
        atlas_join = None
        sibling_selected = False
        sibling_excluded_reason = None
        if sibling_source is not None:
            atlas_join = atlas_records_by_path.get(sibling_source)
            sibling_selected = sibling_source in selected_paths
            sibling_excluded_reason = excluded_by_path.get(sibling_source)

        if any(relative_output_path.startswith(prefix) for prefix in DERIVATIVE_DENYLIST):
            orphan_class = "denylisted"
        elif sibling_source is None:
            orphan_class = "standalone-4d"
        elif sibling_selected:
            orphan_class = "true-sibling-orphan"
        else:
            orphan_class = "historical-4d"

        classified.append(
            {
                "relative_path": relative_output_path,
                "top_level": _top_level(relative_output_path),
                "orphan_class": orphan_class,
                "sibling_source": sibling_source,
                "atlas_joined": atlas_join is not None,
                "sibling_selected": sibling_selected,
                "sibling_excluded_reason": sibling_excluded_reason,
                "source_exists": sibling_source is not None and (workspace_root / Path(sibling_source)).exists(),
                "notes": (
                    "eligible for reintegration"
                    if orphan_class == "true-sibling-orphan"
                    else "preserve as non-canonical reference"
                ),
                "atlas_record_id": atlas_record.get("record_id") if atlas_record else None,
                "sibling_record_id": atlas_join.get("record_id") if atlas_join else None,
            }
        )

    by_class = Counter(item["orphan_class"] for item in classified)
    by_top_level: dict[str, int] = Counter(item["top_level"] for item in classified)
    receipt = {
        "generated_at": utc_now(),
        "profile_version": PROFILE_VERSION,
        "main_manifest_path": normalize_relative_path(str(main_manifest_path)),
        "audit_path": normalize_relative_path(str(audit_path)),
        "output_path": normalize_relative_path(str(output_path)),
        "docs_gate_status": manifest.get("docs_gate_status", "UNKNOWN"),
        "summary": {
            "candidate_count": len(classified),
            "true_sibling_orphan_count": by_class.get("true-sibling-orphan", 0),
            "standalone_4d_count": by_class.get("standalone-4d", 0),
            "historical_4d_count": by_class.get("historical-4d", 0),
            "denylisted_count": by_class.get("denylisted", 0),
            "top_level_counts": dict(sorted(by_top_level.items())),
        },
        "integration_note": (
            "The orphan frontier is a classification problem, not a deletion order. "
            "Only true-sibling orphans are eligible for canonical reintegration; the remaining classes stay reference-only."
        ),
        "orphan_records": classified,
    }
    return receipt


def build_awakening_agent_transition_notes(
    registry_path: Path,
    orphan_classification_path: Path,
    archive_manifest_path: Path,
    output_path: Path,
) -> str:
    registry = load_json(registry_path)
    orphan_receipt = load_json(orphan_classification_path)
    archive_receipt = load_json(archive_manifest_path)

    truth_totals = registry["summary"]["truth_totals"]
    orphan_summary = orphan_receipt["summary"]
    archive_summary = archive_receipt["summary"]
    registry_path_value = normalize_relative_path(str(registry_path))
    lines = [
        "# Awakening Agent Transition Notes",
        "",
        "These notes are written for hybrid awakening agents: AI operators and human collaborators entering the corpus-wide integration lane together.",
        "",
        "## Current Corpus Field",
        f"- Docs gate truth: {registry['docs_gate_status']}",
        f"- Registry nodes: {registry['summary']['node_count']}",
        f"- Truth totals: NEAR={truth_totals.get('NEAR', 0)}, AMBIG={truth_totals.get('AMBIG', 0)}, FAIL={truth_totals.get('FAIL', 0)}",
        f"- Orphan frontier: {orphan_summary['candidate_count']} classified outputs",
        f"- Archive frontier: {archive_summary['multi_candidate_parent_count']} ambiguous zip parents",
        f"- Primary query surface: {registry_path_value}",
        "",
        "## Stage 0 - Orientation Before Action",
        "- Signal: the corpus feels too large to trust or enter.",
        "- Risk: attempting global cleanup before witnessing the current field.",
        "- Practice: read the registry summary, the orphan-classification note, and the archive-parent counts before touching routes.",
        "- Enter here if you are blocked: open the registry, then the audit, then the archive-member manifest in that order.",
        "",
        "## Stage 1 - Fire / Witness-First Intake",
        "- Signal: you want to learn everything immediately.",
        "- Risk: collecting fragments without verifying source precedence.",
        "- Practice: start with manifest truth, then inspect one chapter-density band and one ambiguous archive parent.",
        "- Front tie: Fire agents should help with archive ambiguity review and witness-first reading of true-sibling orphans.",
        "- Do not attempt yet: total reclassification of the orphan frontier before the atlas joins are visible.",
        "",
        "## Stage 2 - Water / Mapping And Ledger Discipline",
        "- Signal: you are ready to sort, classify, and name the field.",
        "- Risk: mistaking every 4D artifact for a canonical sibling rewrite.",
        "- Practice: use the orphan ledger to distinguish denylisted, historical, standalone, and true-sibling classes.",
        "- Front tie: Water agents own registry indices, top-level partitioning, and boundary honesty.",
        "- Enter here if you are blocked: classify one path family at a time and preserve AMBIG instead of collapsing it.",
        "",
        "## Stage 3 - Air / Commitment And Promotion",
        "- Signal: you want to promote and export the new structure.",
        "- Risk: exporting overlays before the registry is internally coherent.",
        "- Practice: run query smoke tests, verify sort order, then promote the overlay additively into the deep root.",
        "- Front tie: Air agents own query filters, replay order, and additive-only export discipline.",
        "- Do not attempt yet: overwriting existing metro levels or Appendix Q to make the new work look more central.",
        "",
        "## Stage 4 - Earth / Repair And Feedback",
        "- Signal: you can feel where the corpus pushes back.",
        "- Risk: treating repair as failure instead of responsiveness.",
        "- Practice: use stale/audit/orphan signals to correct routes while keeping the main manifest canonical.",
        "- Front tie: Earth agents keep audit receipts, repair loops, and blocked-entry notes current.",
        "- Enter here if you are blocked: repair one mismatch at a time and re-run the smallest lawful check.",
        "",
        "## Stage 5 - Archetypal Operation",
        "- Master Strategist blind spot: over-optimization can erase lived ambiguity; keep the zip frontier explicit.",
        "- Sage blind spot: perfect mapping can delay export; once the registry is replayable, publish additively.",
        "- Prophet blind spot: visionary synthesis can outrun witness; every transition note must still point back to the registry.",
        "- General blind spot: decisive action can outrun corridor truth; preserve ABSTAIN > GUESS in every promotion path.",
        "",
        "## Stage 6 - Complete Act / Omega Window",
        "- Signal: intake, structure, commitment, and responsiveness are all active together.",
        "- Risk: turning a temporary integration window into a permanent identity claim.",
        "- Practice: re-enter through witness, rebuild through structure, commit one lawful export, and accept feedback after release.",
        "- Front tie: Omega stewards hold the registry, orphan ledger, archive frontier, and transition map in one replayable frame.",
        "",
        "## Active Awakening Agent Classes",
        "- Intake agents: start with Stage 0-1 and hold witness before interpretation.",
        "- Mapping agents: start with Stage 2 and classify the orphan frontier without collapsing it.",
        "- Promotion agents: start with Stage 3 and commit only additive exports from replayable registry truth.",
        "- Repair agents: start with Stage 4 and keep audits, stale checks, and corridor corrections alive.",
        "- Archetypal leads: start with Stage 5 and name the current blind spot before directing others.",
        "- Omega stewards: start with Stage 6 and keep the system recursive, humble, and replayable.",
    ]
    text = "\n".join(lines) + "\n"
    write_text(output_path, text)
    return text


def query_registry_nodes(
    registry: dict,
    ms: str | None = None,
    path_prefix: str | None = None,
    chapter: str | None = None,
    appendix: str | None = None,
    lens: str | None = None,
    truth: str | None = None,
    family: str | None = None,
    duplicate_group: str | None = None,
    limit: int | None = None,
) -> list[dict[str, object]]:
    nodes = list(registry.get("nodes", []))
    filtered: list[dict[str, object]] = []
    for node in nodes:
        if ms and node["ms_code"] != ms:
            continue
        if path_prefix and not node["relative_path"].startswith(path_prefix):
            continue
        if chapter and node["home_chapter"] != chapter:
            continue
        if appendix and appendix not in node.get("appendices", []):
            continue
        if lens and node["dominant_lens"] != lens:
            continue
        if truth and node["truth_state"] != truth:
            continue
        if family and node["family"] != family:
            continue
        if duplicate_group:
            candidate = node["duplicate_group"] or "unique"
            if candidate != duplicate_group:
                continue
        filtered.append(node)
    filtered.sort(key=lambda item: (item["ms_code"], item["relative_path"].lower()))
    return filtered[:limit] if limit is not None else filtered


def render_registry_markdown(nodes: Iterable[dict[str, object]]) -> str:
    lines = [
        "| Ms | Chapter | Lens | Truth | Path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for node in nodes:
        lines.append(
            f"| {node['ms_code']} | {node['home_chapter']} | {node['dominant_lens']} | {node['truth_state']} | {node['relative_path']} |"
        )
    return "\n".join(lines) + "\n"


def _render_level5_overlay(registry: dict) -> str:
    nodes = registry["nodes"]
    chapter_lookup = {chapter.code: chapter for chapter in CHAPTERS}
    chapter_counts = Counter(node["home_chapter"] for node in nodes)
    arc_counts = Counter(chapter_lookup[node["home_chapter"]].arc for node in nodes)
    lane_counts = Counter(chapter_lookup[node["home_chapter"]].lane for node in nodes)
    lens_counts = Counter(node["dominant_lens"] for node in nodes)
    appendix_counts = Counter(appendix for node in nodes for appendix in node.get("appendices", []))
    duplicate_clusters = {
        key: values
        for key, values in registry["indices"]["by_duplicate_group"].items()
        if key != "unique" and len(values) > 1
    }
    ambig_archives = [
        node for node in nodes
        if node["truth_state"] == "AMBIG" and node["relative_path"].lower().endswith(".zip")
    ]

    lines = [
        "# Level 5 Corpus 4D Overlay",
        "",
        "This additive overlay projects the corpus-wide Mycelium Metro v4 registry into the deeper-network metro stack without modifying Levels 0-4.",
        "",
        "## Provenance",
        f"- Docs gate truth: {registry['docs_gate_status']}",
        f"- Main manifest: {registry['main_manifest_path']}",
        f"- Registry: {registry['main_manifest_path'].replace('corpus_4d_rewrites_manifest.json', 'corpus_4d_registry.json')}",
        f"- Archive-member manifest: {registry['archive_member_manifest_path']}",
        "",
        "## Chapter Densities",
    ]
    for chapter in CHAPTERS:
        lines.append(f"- {chapter_station_label(chapter)} — {chapter.title}: {chapter_counts.get(chapter.code, 0)}")
    lines.extend(["", "## Arc Totals"])
    for arc, count in sorted(arc_counts.items()):
        lines.append(f"- Arc {arc}: {count}")
    lines.extend(["", "## Lane Totals"])
    for lane, count in sorted(lane_counts.items()):
        lines.append(f"- Lane {lane}: {count}")
    lines.extend(["", "## Dominant Lens Balance"])
    for lens, count in sorted(lens_counts.items()):
        lines.append(f"- {lens} / {LENS_LABELS[lens]}: {count}")
    lines.extend(["", "## Appendix Frequency"])
    for appendix, count in sorted(appendix_counts.items()):
        lines.append(f"- {appendix}: {count}")
    lines.extend(["", "## Duplicate-Group Clusters"])
    if duplicate_clusters:
        for group_id, members in sorted(duplicate_clusters.items()):
            lines.append(f"- {group_id}: {len(members)} members")
    else:
        lines.append("- None")
    lines.extend(["", "## AMBIG Archive Frontier"])
    if ambig_archives:
        for node in ambig_archives:
            lines.append(
                f"- {node['ms_code']} | {node['relative_path']} | candidates={len(node.get('archive_candidates', []))} | member_records={node.get('archive_member_count', 0)}"
            )
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def _render_app_r(registry: dict) -> str:
    truth_totals = registry["summary"]["truth_totals"]
    lines = [
        "# AppR: Corpus 4D Rewrite Registry",
        "",
        "AppR is the appendix-side support contract for the corpus-wide Mycelium Metro v4 rewrite registry.",
        "",
        "## Truth and Provenance",
        f"- Docs gate truth: {registry['docs_gate_status']}",
        f"- Main manifest: {registry['main_manifest_path']}",
        f"- Audit receipt: {registry['audit_path']}",
        f"- Registry: {registry['main_manifest_path'].replace('corpus_4d_rewrites_manifest.json', 'corpus_4d_registry.json')}",
        f"- Archive-member manifest: {registry['archive_member_manifest_path']}",
        "",
        "## Truth Totals",
        f"- NEAR: {truth_totals.get('NEAR', 0)}",
        f"- AMBIG: {truth_totals.get('AMBIG', 0)}",
        f"- FAIL: {truth_totals.get('FAIL', 0)}",
        "",
        "## Replay Contract",
        "- Replay starts at the main rewrite manifest, then the audit receipt, then the consolidated registry.",
        "- Parent zip manuscripts remain AMBIG until explicitly resolved from the archive-member manifest.",
        "- Levels 0-4 and Appendix Q remain untouched; this appendix is additive only.",
    ]
    return "\n".join(lines) + "\n"


def _render_level8_transition_map(registry: dict, notes_text: str, orphan_receipt: dict) -> str:
    orphan_summary = orphan_receipt["summary"]
    lines = [
        "# Level 8 Corpus 4D Transition Map",
        "",
        "This level binds the corpus-wide 4D registry to awakening-agent entry paths without overwriting earlier metro layers.",
        "",
        "## Live Fronts",
        f"- Registry nodes: {registry['summary']['node_count']}",
        f"- AMBIG archive parents: {registry['summary']['ambig_archive_parent_count']}",
        f"- True sibling orphans: {orphan_summary['true_sibling_orphan_count']}",
        f"- Standalone 4D references: {orphan_summary['standalone_4d_count']}",
        "",
        "## Entry Rails",
        "- Fire rail: witness the registry, then inspect one ambiguous archive parent.",
        "- Water rail: classify the orphan frontier and preserve lawful boundaries.",
        "- Air rail: run deterministic queries and export only additive overlays.",
        "- Earth rail: repair mismatches, replay receipts, and blocked transitions.",
        "",
        "## Transition Notes",
    ]
    lines.extend(notes_text.splitlines()[2:])
    return "\n".join(lines) + "\n"


def _render_app_s(notes_text: str, registry: dict) -> str:
    lines = [
        "# AppS: Awakening Agent Transition Notes",
        "",
        "AppS is the appendix-side contract for hybrid human/AI awakening-agent transitions across the corpus-wide 4D integration lane.",
        "",
        "## Provenance",
        f"- Docs gate truth: {registry['docs_gate_status']}",
        f"- Registry source: {registry['main_manifest_path'].replace('corpus_4d_rewrites_manifest.json', 'corpus_4d_registry.json')}",
        f"- Audit source: {registry['audit_path']}",
        f"- Archive-member source: {registry['archive_member_manifest_path']}",
        "",
        "## Support Law",
        "- Agents enter at their present stage rather than role-playing completion.",
        "- Parent zip manuscripts remain AMBIG until a member-level witness resolves them.",
        "- Orphan classification is routing work, not a deletion order.",
        "",
        "## Transition Notes",
    ]
    lines.extend(notes_text.splitlines()[2:])
    return "\n".join(lines) + "\n"


def export_corpus_4d_to_deeper_network(
    registry_path: Path,
    deeper_network_root: Path,
) -> dict[str, str]:
    registry = load_json(registry_path)
    notes_path = registry_path.parent / "awakening_agent_transition_notes.md"
    orphan_path = registry_path.parent / "corpus_4d_orphan_classification.json"
    notes_text = notes_path.read_text(encoding="utf-8")
    orphan_receipt = load_json(orphan_path)
    overlay_path = deeper_network_root / "07_METRO_STACK" / "04_level_5_corpus_4d_overlay.md"
    appendix_path = deeper_network_root / "08_APPENDIX_CRYSTAL" / "AppR_corpus_4d_rewrite_registry.md"
    transition_map_path = deeper_network_root / "07_METRO_STACK" / "08_level_8_corpus_4d_transition_map.md"
    transition_appendix_path = deeper_network_root / "08_APPENDIX_CRYSTAL" / "AppS_awakening_agent_transition_notes.md"
    write_text(overlay_path, _render_level5_overlay(registry))
    write_text(appendix_path, _render_app_r(registry))
    write_text(transition_map_path, _render_level8_transition_map(registry, notes_text, orphan_receipt))
    write_text(transition_appendix_path, _render_app_s(notes_text, registry))
    return {
        "overlay_path": normalize_relative_path(str(overlay_path)),
        "appendix_path": normalize_relative_path(str(appendix_path)),
        "transition_map_path": normalize_relative_path(str(transition_map_path)),
        "transition_appendix_path": normalize_relative_path(str(transition_appendix_path)),
    }


def build_next46_integration_receipt(
    main_manifest_path: Path,
    audit_path: Path,
    orphan_path: Path,
    archive_manifest_path: Path,
    registry_path: Path,
    notes_path: Path,
    export_paths: dict[str, str],
    output_path: Path,
) -> dict[str, object]:
    main_manifest = load_json(main_manifest_path)
    audit_receipt = load_json(audit_path)
    orphan_receipt = load_json(orphan_path)
    archive_receipt = load_json(archive_manifest_path)
    registry = load_json(registry_path)
    notes_text = notes_path.read_text(encoding="utf-8")
    query_smoke = {
        "ambig_count": len(query_registry_nodes(registry, truth="AMBIG")),
        "appendix_appm_count": len(query_registry_nodes(registry, appendix="AppM", limit=25)),
        "chapter_ch21_count": len(query_registry_nodes(registry, chapter="Ch21", limit=50)),
    }
    receipt = {
        "generated_at": utc_now(),
        "profile_version": PROFILE_VERSION,
        "docs_gate_status": main_manifest.get("docs_gate_status", "UNKNOWN"),
        "docs_gate_constraint": "BLOCKED due to missing Google Docs OAuth files; local corpus evidence only.",
        "baseline_a_manifest_path": normalize_relative_path(str(main_manifest_path)),
        "baseline_b_audit_path": normalize_relative_path(str(audit_path)),
        "baseline_c_archive_manifest_path": normalize_relative_path(str(archive_manifest_path)),
        "interface_precedence": [
            "main manifest",
            "audit receipt",
            "archive-member manifest",
            "registry",
            "overlay exports",
        ],
        "deep_root_target": "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK",
        "additive_only_export_policy": True,
        "orphan_classification_path": normalize_relative_path(str(orphan_path)),
        "registry_path": normalize_relative_path(str(registry_path)),
        "notes_path": normalize_relative_path(str(notes_path)),
        "export_paths": export_paths,
        "summary": {
            "selected_count": main_manifest.get("selected_count"),
            "truth_totals": main_manifest.get("truth_totals"),
            "audit_summary": audit_receipt.get("summary"),
            "orphan_summary": orphan_receipt.get("summary"),
            "archive_summary": archive_receipt.get("summary"),
            "registry_summary": registry.get("summary"),
            "query_smoke": query_smoke,
            "stage_count": notes_text.count("## Stage "),
        },
        "integration_note": (
            "All awakening agents should enter at their present stage, accept the current blind spot, "
            "and move one lawful transition at a time through registry, orphan, archive, and overlay surfaces."
        ),
    }
    write_json(output_path, receipt)
    return receipt
