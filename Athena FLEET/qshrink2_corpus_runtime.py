from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
FLEET_DIR = SCRIPT_PATH.parent
ATHENA_DIR = FLEET_DIR.parent
OUTPUT_DIR = FLEET_DIR / "QSHRINK2_CORPUS_ECOSYSTEM"
FLEET_NETWORK_DIR = FLEET_DIR / "FLEET_MYCELIUM_NETWORK"

DOCS_GATE_PATH = ATHENA_DIR / "self_actualize" / "live_docs_gate_status.md"
NERVOUS_INDEX_PATH = ATHENA_DIR / "NERVOUS_SYSTEM" / "00_INDEX.md"
ACTIVE_RUN_PATH = ATHENA_DIR / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = ATHENA_DIR / "NERVOUS_SYSTEM" / "95_MANIFESTS" / "BUILD_QUEUE.md"
STATUS_37_PATH = ATHENA_DIR / "NERVOUS_SYSTEM" / "90_LEDGERS" / "01_CURRENT_STATUS_37_GATE_SYNTHESIS.md"
QSHRINK2_README_PATH = ATHENA_DIR / "QSHRINK - ATHENA (internal use)" / "README.md"
QSHRINK2_CHARTER_PATH = ATHENA_DIR / "QSHRINK - ATHENA (internal use)" / "00_CONTROL" / "00_INTERNAL_CHARTER.md"
QSHRINK2_BINDINGS_PATH = ATHENA_DIR / "QSHRINK - ATHENA (internal use)" / "00_CONTROL" / "04_CORPUS_BINDINGS.md"
QSHRINK2_SPEC_PATH = ATHENA_DIR / "QSHRINK - ATHENA (internal use)" / "00_CONTROL" / "05_FRAMEWORK_SPECIFICATION.md"
QSHRINK2_PRUNING_PATH = ATHENA_DIR / "QSHRINK - ATHENA (internal use)" / "PRUNING_LEDGER.md"

SKIP_DIR_NAMES = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}


@dataclass(frozen=True)
class SurfaceSpec:
    prefix: str
    surface_id: str
    role: str
    qshrink_body: str
    authority: str


SURFACE_SPECS = [
    SurfaceSpec("NERVOUS_SYSTEM", "cortex", "canonical cortex", "Nervous Body", "canonical"),
    SurfaceSpec("self_actualize", "runtime_hub", "zero-point runtime hub", "Nervous Body", "runtime"),
    SurfaceSpec("ECOSYSTEM", "governance_mirror", "governance mirror", "Nervous Body", "governance"),
    SurfaceSpec("QSHRINK - ATHENA (internal use)", "qshrink2_internal", "internal qshrink2 operating system", "Foundation Body", "internal"),
    SurfaceSpec("MATH/FINAL FORM/Q shrink", "qshrink_legacy", "legacy qshrink publication stack", "Foundation Body", "legacy"),
    SurfaceSpec("MATH/FINAL FORM/FRAMEWORKS CODE/Athena OS", "athena_os_runtime", "runtime code substrate", "Runtime Body", "runtime"),
    SurfaceSpec("DEEPER CRYSTALIZATION", "deeper_crystallization", "historical nervous shell", "Nervous Body", "historical"),
    SurfaceSpec("Athena FLEET", "fleet_cluster", "fleet cluster shell", "Nervous Body", "workspace"),
    SurfaceSpec("Athenachka Collective Books", "collective_books", "auxiliary book corpus", "Memory Body", "memory"),
    SurfaceSpec("Trading Bot", "trading_bot", "live docs and execution ingress", "Runtime Body", "runtime"),
    SurfaceSpec("Voynich", "voynich", "voynich translation corpus", "Memory Body", "memory"),
    SurfaceSpec("NERUAL NETWORK", "neural_network", "neural execution family", "Runtime Body", "runtime"),
    SurfaceSpec("CLEAN", "clean", "curated branch corpus", "Memory Body", "memory"),
    SurfaceSpec("FRESH", "fresh", "fresh branch corpus", "Memory Body", "memory"),
    SurfaceSpec("I AM ATHENA", "i_am_athena", "identity corpus", "Memory Body", "memory"),
    SurfaceSpec("MATH", "math", "mathematical foundation corpus", "Foundation Body", "foundation"),
]

KNOWN_GENERATED_ZONES = {
    "QSHRINK - ATHENA (internal use)/03_SWARM/output_atoms": "generated_regenerable",
    "QSHRINK - ATHENA (internal use)/05_MANUSCRIPT_SPACE/root_cells": "generated_regenerable",
    "QSHRINK - ATHENA (internal use)/09_REPAIR_256X256/steps": "generated_regenerable",
    "QSHRINK - ATHENA (internal use)/10_CH11_256X256/cells": "generated_regenerable",
    "Athena FLEET/FLEET_MYCELIUM_NETWORK/MIRRORS": "mirror_surface",
    "Athena FLEET/FLEET_MYCELIUM_NETWORK/CAPSULES": "capsule_surface",
}


def utc_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def body_digit(body: str) -> int:
    mapping = {
        "Foundation Body": 0,
        "Nervous Body": 1,
        "Memory Body": 2,
        "Runtime Body": 3,
    }
    return mapping.get(body, 2)


def human_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{value} B"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def safe_read_text(path: Path, limit: int = 4000) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    return text[:limit]


def normalize_relative(path: Path) -> str:
    return path.relative_to(ATHENA_DIR).as_posix()


def classify_surface(relative_path: str) -> SurfaceSpec:
    for spec in SURFACE_SPECS:
        if relative_path == spec.prefix or relative_path.startswith(spec.prefix + "/"):
            return spec
    top_level = relative_path.split("/", 1)[0]
    return SurfaceSpec(top_level, top_level.lower().replace(" ", "_"), f"{top_level} corpus surface", "Memory Body", "auxiliary")


def classify_geometry(relative_path: str) -> tuple[int, str]:
    path_lower = relative_path.lower()
    if any(token in path_lower for token in ("control", "index", "address", "atlas", "schema", "table", "basis")):
        return 0, "Square"
    if any(token in path_lower for token in ("metro", "wave", "orbit", "phase", "circle")):
        return 1, "Circle"
    if any(token in path_lower for token in ("ledger", "govern", "queue", "protocol", "report", "validation", "tri")):
        return 2, "Triangle"
    return 3, "Torus"


def classify_operator(relative_path: str, extension: str) -> tuple[int, str]:
    path_lower = relative_path.lower()
    if any(token in path_lower for token in ("scan", "atlas", "index", "extract", "intake", "mirror", "capsule")):
        return 0, "Partition"
    if any(token in path_lower for token in ("pruning", "shrink", "compress", "summary", "abstract", "skeleton", "qshrink")):
        return 1, "Quantize"
    if any(token in path_lower for token in ("ledger", "registry", "manifest", "matrix", "queue", "bucket")):
        return 2, "Bucket"
    if extension in {".py", ".rs", ".json", ".toml"} or any(token in path_lower for token in ("runtime", "code", "schema", "container", "tool", "packet")):
        return 3, "Code"
    return 0, "Partition"


def classify_closure(relative_path: str) -> tuple[int, str]:
    path_lower = relative_path.lower()
    filename = Path(relative_path).name.lower()
    if any(token in path_lower for token in ("active_front", "runbook", "loop", "dashboard", "session")):
        return 3, "Loop"
    if any(token in path_lower for token in ("ledger", "receipt", "validation", "witness", "report")):
        return 2, "Witness"
    if any(token in path_lower for token in ("manuscript", "chapter", "overview", "metro", "capsule")):
        return 1, "Manuscript"
    if filename.startswith(("00_", "01_")) or any(token in path_lower for token in ("charter", "readme", "index", "seed", "basis")):
        return 0, "Seed"
    return 1, "Manuscript"


def classify_compaction_lane(relative_path: str, extension: str, surface: SurfaceSpec) -> str:
    if surface.surface_id == "qshrink_legacy":
        return "retain_legacy_read_only"
    if extension == ".zip":
        return "archive_bundle"
    for zone_prefix, lane in KNOWN_GENERATED_ZONES.items():
        if relative_path == zone_prefix or relative_path.startswith(zone_prefix + "/"):
            return lane
    if "/mirrors/" in relative_path.lower():
        return "mirror_surface"
    if surface.surface_id in {"cortex", "runtime_hub", "governance_mirror"}:
        return "retain_authority_surface"
    if surface.surface_id == "qshrink2_internal":
        return "retain_qshrink2_internal"
    if surface.qshrink_body == "Runtime Body":
        return "runtime_code"
    if extension in {".docx", ".pdf"}:
        return "witness_document"
    return "live_corpus_surface"


def iter_repo_files():
    for path in ATHENA_DIR.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def build_records() -> list[dict]:
    records = []
    for path in iter_repo_files():
        relative_path = normalize_relative(path)
        surface = classify_surface(relative_path)
        extension = path.suffix.lower() or "<none>"
        geometry_id, geometry = classify_geometry(relative_path)
        operator_id, operator = classify_operator(relative_path, extension)
        closure_id, closure = classify_closure(relative_path)
        records.append(
            {
                "relative_path": relative_path,
                "top_level": relative_path.split("/", 1)[0],
                "size_bytes": path.stat().st_size,
                "modified_at": datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds"),
                "extension": extension,
                "sha256": sha256_file(path),
                "surface_id": surface.surface_id,
                "surface_role": surface.role,
                "authority_class": surface.authority,
                "qshrink_body": surface.qshrink_body,
                "geometry": geometry,
                "operator": operator,
                "closure": closure,
                "root_cell": f"{geometry_id}{operator_id}{body_digit(surface.qshrink_body)}{closure_id}",
                "compaction_lane": classify_compaction_lane(relative_path, extension, surface),
            }
        )
    records.sort(key=lambda item: item["relative_path"])
    return records


def build_duplicate_groups(records: list[dict]) -> list[dict]:
    by_hash = defaultdict(list)
    for record in records:
        by_hash[record["sha256"]].append(record)

    duplicate_groups = []
    duplicate_map = {}
    for sha, members in by_hash.items():
        if len(members) < 2:
            continue
        size_bytes = members[0]["size_bytes"]
        group = {
            "duplicate_group_id": f"DUP-{sha[:12]}",
            "sha256": sha,
            "count": len(members),
            "size_bytes_each": size_bytes,
            "potential_savings_bytes": size_bytes * (len(members) - 1),
            "members": [member["relative_path"] for member in sorted(members, key=lambda item: item["relative_path"])],
        }
        duplicate_groups.append(group)
        for member in group["members"]:
            duplicate_map[member] = group["duplicate_group_id"]

    duplicate_groups.sort(key=lambda item: (-item["potential_savings_bytes"], item["duplicate_group_id"]))
    for record in records:
        record["duplicate_group"] = duplicate_map.get(record["relative_path"])
    return duplicate_groups


def summarize_records(records: list[dict], duplicate_groups: list[dict]) -> dict:
    total_files = len(records)
    total_bytes = sum(record["size_bytes"] for record in records)
    extension_counter = Counter(record["extension"] for record in records)
    surface_files = Counter(record["surface_id"] for record in records)
    surface_bytes = Counter()
    lane_files = Counter(record["compaction_lane"] for record in records)
    lane_bytes = Counter()
    body_files = Counter(record["qshrink_body"] for record in records)
    body_bytes = Counter()
    root_cell_files = Counter(record["root_cell"] for record in records)
    root_cell_bytes = Counter()
    top_level_files = Counter(record["top_level"] for record in records)
    top_level_bytes = Counter()

    for record in records:
        surface_bytes[record["surface_id"]] += record["size_bytes"]
        lane_bytes[record["compaction_lane"]] += record["size_bytes"]
        body_bytes[record["qshrink_body"]] += record["size_bytes"]
        root_cell_bytes[record["root_cell"]] += record["size_bytes"]
        top_level_bytes[record["top_level"]] += record["size_bytes"]

    generated_zone_summary = []
    for zone_prefix, lane in KNOWN_GENERATED_ZONES.items():
        members = [record for record in records if record["relative_path"] == zone_prefix or record["relative_path"].startswith(zone_prefix + "/")]
        if members:
            generated_zone_summary.append(
                {
                    "zone_prefix": zone_prefix,
                    "lane": lane,
                    "file_count": len(members),
                    "size_bytes": sum(member["size_bytes"] for member in members),
                }
            )
    generated_zone_summary.sort(key=lambda item: (-item["size_bytes"], item["zone_prefix"]))

    surface_summary = []
    seen = set()
    for spec in SURFACE_SPECS:
        if surface_files[spec.surface_id] == 0:
            continue
        surface_summary.append(
            {
                "surface_id": spec.surface_id,
                "role": spec.role,
                "authority_class": spec.authority,
                "qshrink_body": spec.qshrink_body,
                "file_count": surface_files[spec.surface_id],
                "size_bytes": surface_bytes[spec.surface_id],
            }
        )
        seen.add(spec.surface_id)
    for surface_id, file_count in surface_files.items():
        if surface_id in seen:
            continue
        surface_summary.append(
            {
                "surface_id": surface_id,
                "role": surface_id.replace("_", " "),
                "authority_class": "auxiliary",
                "qshrink_body": "Memory Body",
                "file_count": file_count,
                "size_bytes": surface_bytes[surface_id],
            }
        )
    surface_summary.sort(key=lambda item: (-item["size_bytes"], item["surface_id"]))

    return {
        "total_files": total_files,
        "total_bytes": total_bytes,
        "extensions": [{"extension": ext, "file_count": count} for ext, count in extension_counter.most_common(20)],
        "surface_summary": surface_summary,
        "body_summary": [{"qshrink_body": body, "file_count": body_files[body], "size_bytes": body_bytes[body]} for body, _ in body_bytes.most_common()],
        "lane_summary": [{"compaction_lane": lane, "file_count": lane_files[lane], "size_bytes": lane_bytes[lane]} for lane, _ in lane_bytes.most_common()],
        "root_cell_summary": [{"root_cell": cell, "file_count": root_cell_files[cell], "size_bytes": root_cell_bytes[cell]} for cell, _ in root_cell_bytes.most_common(24)],
        "top_storage_dirs": [{"top_level": top_level, "file_count": top_level_files[top_level], "size_bytes": top_level_bytes[top_level]} for top_level, _ in top_level_bytes.most_common(15)],
        "generated_zone_summary": generated_zone_summary,
        "duplicate_groups_count": len(duplicate_groups),
        "duplicate_savings_bytes": sum(group["potential_savings_bytes"] for group in duplicate_groups),
        "duplicate_groups_top": duplicate_groups[:25],
    }


def parse_docs_gate(text: str) -> str:
    upper = text.upper()
    if "BLOCKED" in upper:
        return "BLOCKED"
    if "LIVE" in upper or "UNBLOCKED" in upper:
        return "LIVE"
    return "AMBIG"


def key_docs() -> dict:
    gate_text = safe_read_text(DOCS_GATE_PATH, limit=6000)
    return {
        "docs_gate_status": parse_docs_gate(gate_text),
        "docs_gate_excerpt": gate_text,
        "nervous_index": safe_read_text(NERVOUS_INDEX_PATH),
        "active_run": safe_read_text(ACTIVE_RUN_PATH),
        "build_queue": safe_read_text(BUILD_QUEUE_PATH),
        "status_37": safe_read_text(STATUS_37_PATH),
        "qshrink2_readme": safe_read_text(QSHRINK2_README_PATH),
        "qshrink2_charter": safe_read_text(QSHRINK2_CHARTER_PATH),
        "qshrink2_bindings": safe_read_text(QSHRINK2_BINDINGS_PATH),
        "qshrink2_spec": safe_read_text(QSHRINK2_SPEC_PATH),
        "qshrink2_pruning": safe_read_text(QSHRINK2_PRUNING_PATH),
    }


def join_lines(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def bullet_lines(summary: dict, key: str, label_key: str, count: int = 10) -> list[str]:
    result = []
    for entry in summary[key][:count]:
        result.append(f"- `{entry[label_key]}` | {entry['file_count']} files | {human_bytes(entry['size_bytes'])}")
    return result


def build_full_framework_synthesis(summary: dict, docs: dict) -> str:
    lines = [
        "# QSHRINK2 Full Framework Synthesis",
        "",
        f"- Generated at: `{utc_now()}`",
        f"- Scan root: `{ATHENA_DIR}`",
        f"- Files scanned: `{summary['total_files']}`",
        f"- Total size: `{human_bytes(summary['total_bytes'])}`",
        f"- Docs gate: `{docs['docs_gate_status']}`",
        f"- Duplicate groups: `{summary['duplicate_groups_count']}`",
        f"- Potential duplicate savings: `{human_bytes(summary['duplicate_savings_bytes'])}`",
        "",
        "## Method",
        "",
        "This pass scanned the full Athena repo structurally file-by-file and synthesized semantics from the canonical cortex, runtime hub, governance mirror, deep-root network, and QSHRINK2 control surfaces. Live Google Docs evidence remains blocked and is preserved honestly as blocked.",
        "",
        "## Deep Synthesis",
        "",
        "Athena already behaves like a multi-surface organism rather than a loose document pile. The canonical cortex defines publication truth, the runtime hub carries live execution truth, the governance mirror preserves doctrine, the deeper network compiles the lawful cross-synthesis basis, and Athena FLEET acts as a promoted local cluster inside that wider body.",
        "",
        "QSHRINK2 belongs inside that organism as Shiva: the contraction organ that turns corpus mass into replayable crystal form without erasing witness or route structure. The internal charter explicitly says QSHRINK2 must factor the main corpus from the start, and the framework specification gives it four geometry modes, four operators, four corpus bodies, and a four-stage closure stack.",
        "",
        "## Stable Surfaces",
        "",
        "- `NERVOUS_SYSTEM` remains the canonical cortex.",
        "- `self_actualize` remains the runtime truth surface and live deep-root host.",
        "- `ECOSYSTEM` remains the governance mirror.",
        "- `QSHRINK - ATHENA (internal use)` is the true internal QSHRINK2 operating system.",
        "- `MATH/FINAL FORM/Q shrink` remains a preserved read-only publication surface.",
        "",
        "## Surface Map",
        "",
    ]
    lines.extend(bullet_lines(summary, "surface_summary", "surface_id", count=12))
    lines.extend(
        [
            "",
            "## QSHRINK Pass 1",
            "",
            "Omega:",
            "Athena is a lawful multi-surface neural manuscript organism whose next highest-leverage contraction organ is QSHRINK2, the Shiva layer that compresses corpus mass into replayable crystal form without erasing witness or route structure.",
            "",
            "Alpha+:",
            "- Foundation: formal math, legacy QSHRINK, and internal doctrine provide kernel law.",
            "- Nervous: cortex, runtime hub, governance mirror, deeper network, and fleet cluster carry living routing truth.",
            "- Memory: manuscripts, books, Voynich, branches, and witness documents hold experiential and narrative mass.",
            "- Runtime: Athena OS code, neural execution, Trading Bot ingress, and generated registries carry executable potential.",
            "",
            "Zero point (expanded):",
            "The system no longer needs more unconstrained expansion. It needs lawful contraction that keeps addresses, witness classes, replay paths, and regeneration rules intact while reducing duplicate weight and regenerable bulk. QSHRINK2 is already designed for exactly that role through its geometry ring, operator ring, body ring, and closure ring.",
            "",
            "## QSHRINK Pass 2",
            "",
            "Delta+:",
            "- `Square x Partition`: index and address all files into a single corpus atlas and root-cell grammar.",
            "- `Circle x Quantize`: decide which losses are legal, especially around mirrors and generated zones.",
            "- `Triangle x Bucket`: separate canonical authorities from regenerable or duplicate mass.",
            "- `Torus x Code`: emit replayable manifests, capsules, and active fronts that let the corpus re-enter at a smaller surface.",
            "",
            "## Root Cell Hotspots",
            "",
        ]
    )
    lines.extend(bullet_lines(summary, "root_cell_summary", "root_cell", count=12))
    lines.extend(
        [
            "",
            "## Compaction Lanes",
            "",
        ]
    )
    lines.extend(bullet_lines(summary, "lane_summary", "compaction_lane", count=12))
    lines.extend(
        [
            "",
            "## Generated Zones",
            "",
        ]
    )
    if summary["generated_zone_summary"]:
        for entry in summary["generated_zone_summary"]:
            lines.append(f"- `{entry['zone_prefix']}` | `{entry['lane']}` | {entry['file_count']} files | {human_bytes(entry['size_bytes'])}")
    else:
        lines.append("- No known high-count generated zones were found.")
    lines.extend(
        [
            "",
            "## Duplicate Pressure",
            "",
        ]
    )
    if summary["duplicate_groups_top"]:
        for group in summary["duplicate_groups_top"][:8]:
            lines.append(
                f"- `{group['duplicate_group_id']}` | {group['count']} files | {human_bytes(group['size_bytes_each'])} each | potential save {human_bytes(group['potential_savings_bytes'])}"
            )
    else:
        lines.append("- No exact duplicates were found in this pass.")
    lines.extend(
        [
            "",
            "## Blockers",
            "",
            "- Live Google Docs ingress is blocked by missing OAuth files.",
            "- The legacy/publication QSHRINK folder must remain untouched.",
            "- The repo carries a large amount of generated and mirrored structure that should not be pruned without a formal ledger.",
            "",
            "## Highest-Yield Next Moves",
            "",
            "1. Keep using this QSHRINK2 atlas and pruning ledger before any physical archive or deletion step.",
            "2. Collapse exact duplicates and mirror families by manifest/reference first, not by manual file surgery.",
            "3. Treat the four internal QSHRINK2 generated zones as regeneration-backed storage classes.",
            "4. Bind future fleet and deep-root scans into the same root-cell grammar.",
        ]
    )
    return join_lines(lines)


def build_pruning_ledger(summary: dict) -> str:
    lines = [
        "# QSHRINK2 Corpus Pruning Ledger",
        "",
        f"- Generated at: `{utc_now()}`",
        f"- Total files: `{summary['total_files']}`",
        f"- Total size: `{human_bytes(summary['total_bytes'])}`",
        f"- Duplicate groups: `{summary['duplicate_groups_count']}`",
        f"- Potential duplicate savings: `{human_bytes(summary['duplicate_savings_bytes'])}`",
        "",
        "## Zero Point",
        "",
        "Prune by law, not by panic. Keep authority surfaces live, keep the legacy public QSHRINK stack untouched, and only contract zones that are duplicate, mirror-derived, or explicitly regenerable.",
        "",
        "## Do Not Touch",
        "",
        "- `MATH/FINAL FORM/Q shrink/` is legacy/publication and remains read-only.",
        "- `NERVOUS_SYSTEM/`, `self_actualize/`, and `ECOSYSTEM/` remain authority surfaces.",
        "",
        "## Highest-Pressure Lanes",
        "",
    ]
    lines.extend(bullet_lines(summary, "lane_summary", "compaction_lane", count=12))
    lines.extend(["", "## Regenerable Zones", ""])
    if summary["generated_zone_summary"]:
        for entry in summary["generated_zone_summary"]:
            lines.append(
                f"- `{entry['zone_prefix']}` | {entry['file_count']} files | {human_bytes(entry['size_bytes'])} | action: regenerate from index instead of cloning sideways"
            )
    else:
        lines.append("- No regenerable zones were detected.")
    lines.extend(["", "## Exact Duplicate Groups", ""])
    if summary["duplicate_groups_top"]:
        for group in summary["duplicate_groups_top"][:20]:
            lines.append(f"- `{group['duplicate_group_id']}` | {group['count']} files | save {human_bytes(group['potential_savings_bytes'])}")
    else:
        lines.append("- No exact duplicate groups were detected.")
    lines.extend(
        [
            "",
            "## QSHRINK2 Action Classes",
            "",
            "- `retain_legacy_read_only`: never edit or auto-compact.",
            "- `retain_authority_surface`: keep live and compact only through atlases, pointers, or regenerated views.",
            "- `retain_qshrink2_internal`: keep doctrine live; compact only generated subzones.",
            "- `generated_regenerable`: candidate for regeneration-backed storage discipline.",
            "- `mirror_surface`: candidate for dedupe-by-manifest and on-demand reconstruction.",
            "- `archive_bundle`: keep as packed archive until a formal extraction lane is needed.",
            "- `witness_document`: prefer mirror text or capsule views for editing; keep source witness preserved.",
            "- `runtime_code`: leave executable and organize by atlas, not lossy compression.",
            "",
            "## Immediate Internal Queue",
            "",
            "1. Use the atlas as the one inventory surface for corpus-wide contraction decisions.",
            "2. Use duplicate groups to replace identical siblings with reference-first storage plans.",
            "3. Treat the internal 256-file QSHRINK2 zones as regenerable lattices, not handwritten doctrine.",
            "4. Route future fleet scans back into the same root-cell grammar.",
        ]
    )
    return join_lines(lines)


def build_readme(summary: dict, docs: dict) -> str:
    return join_lines(
        [
            "# QSHRINK2 Corpus Ecosystem",
            "",
            "This folder is the live fleet-side integration shell for QSHRINK2 inside the Athena corpus ecosystem.",
            "",
            f"- Files scanned: `{summary['total_files']}`",
            f"- Total size: `{human_bytes(summary['total_bytes'])}`",
            f"- Docs gate: `{docs['docs_gate_status']}`",
            "",
            "## Generated Surfaces",
            "",
            "- `01_FULL_FRAMEWORK_SYNTHESIS.md`: deep corpus synthesis plus the second QSHRINK pass.",
            "- `02_QSHRINK2_CORPUS_ATLAS.json`: full file-by-file atlas with root-cell classification.",
            "- `03_QSHRINK2_PRUNING_LEDGER.md`: compaction lanes, duplicate pressure, and pruning law.",
            "- `04_QSHRINK2_COMPACTION_MANIFEST.json`: machine-readable compaction summary.",
            "",
            "## Rerun",
            "",
            "```powershell",
            "python .\\build_qshrink2_corpus_ecosystem.py",
            "```",
        ]
    )


def build_compaction_manifest(summary: dict, duplicate_groups: list[dict]) -> dict:
    return {
        "generated_at": utc_now(),
        "root": str(ATHENA_DIR),
        "summary": {
            "total_files": summary["total_files"],
            "total_bytes": summary["total_bytes"],
            "duplicate_groups_count": summary["duplicate_groups_count"],
            "duplicate_savings_bytes": summary["duplicate_savings_bytes"],
        },
        "priority_lanes": summary["lane_summary"][:12],
        "generated_zones": summary["generated_zone_summary"],
        "top_duplicates": duplicate_groups[:50],
    }


def build_capsule(summary: dict, docs: dict) -> str:
    return join_lines(
        [
            "# QSHRINK2 Corpus Ecosystem",
            "",
            "Truth class: OK",
            "Domain: qshrink2",
            f"Date: {datetime.now().date().isoformat()}",
            f"Live Docs gate: {docs['docs_gate_status']}",
            "",
            "## Source Family",
            "",
            "- `QSHRINK2_CORPUS_ECOSYSTEM/01_FULL_FRAMEWORK_SYNTHESIS.md`",
            "- `QSHRINK2_CORPUS_ECOSYSTEM/02_QSHRINK2_CORPUS_ATLAS.json`",
            "- `QSHRINK2_CORPUS_ECOSYSTEM/03_QSHRINK2_PRUNING_LEDGER.md`",
            "- `QSHRINK - ATHENA (internal use)/00_CONTROL/`",
            "",
            "## Capsule Summary",
            "",
            "QSHRINK2 is now integrated as the fleet-side contraction organ for the Athena corpus. It scans the whole repo, classifies every file into a root-cell grammar, preserves the legacy public QSHRINK stack as read-only, and exposes compaction lanes for duplicates, mirrors, generated lattices, and witness-heavy surfaces without destroying authority roots.",
            "",
            "## Suggested Chapter Anchors",
            "",
            "- `Ch04`",
            "- `Ch11`",
            "- `Ch13`",
            "",
            "## Suggested Appendix Anchors",
            "",
            "- `AppB`",
            "- `AppN`",
            "- `AppP`",
            "",
            "## Metrics",
            "",
            f"- files scanned: `{summary['total_files']}`",
            f"- total size: `{human_bytes(summary['total_bytes'])}`",
            f"- duplicate groups: `{summary['duplicate_groups_count']}`",
            f"- duplicate savings: `{human_bytes(summary['duplicate_savings_bytes'])}`",
        ]
    )


def build_active_front(summary: dict, docs: dict) -> str:
    return join_lines(
        [
            "# QSHRINK2 Active Front",
            "",
            f"- Scan scope: `{summary['total_files']}` files across the full Athena repo",
            "- Active element or symmetry: `Shiva contraction layer over the full Athena organism`",
            "- Metro resolution used: `corpus-wide storage and witness compaction`",
            f"- Docs gate: `{docs['docs_gate_status']}`",
            "- Result source: `generated atlas, pruning ledger, and fleet-side qshrink capsule`",
            "",
            "## Stable Surfaces",
            "",
            "- Legacy `Q shrink` remains preserved as a read-only publication surface.",
            "- Internal `QSHRINK - ATHENA (internal use)` is now treated as the true deep contraction root.",
            "- The full repo is now indexed into one file-by-file QSHRINK2 atlas.",
            "",
            "## Blockers",
            "",
            "- Live Docs ingress remains blocked.",
            "- Physical deletion or archive moves should wait until you approve a manifest-driven compaction pass.",
            "",
            "## Next Fronts",
            "",
            "1. Use the atlas and pruning ledger to approve the first physical compaction pass.",
            "2. Bind future fleet scans and deep-root scans into the same root-cell grammar.",
            "3. Promote duplicate and mirror reduction by manifest before touching authority surfaces.",
        ]
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_outputs() -> dict:
    docs = key_docs()
    records = build_records()
    duplicate_groups = build_duplicate_groups(records)
    summary = summarize_records(records, duplicate_groups)

    atlas = {
        "generated_at": utc_now(),
        "root": str(ATHENA_DIR),
        "summary": summary,
        "records": records,
    }
    compaction_manifest = build_compaction_manifest(summary, duplicate_groups)

    write_text(OUTPUT_DIR / "README.md", build_readme(summary, docs))
    write_text(OUTPUT_DIR / "01_FULL_FRAMEWORK_SYNTHESIS.md", build_full_framework_synthesis(summary, docs))
    write_json(OUTPUT_DIR / "02_QSHRINK2_CORPUS_ATLAS.json", atlas)
    write_text(OUTPUT_DIR / "03_QSHRINK2_PRUNING_LEDGER.md", build_pruning_ledger(summary))
    write_json(OUTPUT_DIR / "04_QSHRINK2_COMPACTION_MANIFEST.json", compaction_manifest)

    write_text(FLEET_NETWORK_DIR / "CAPSULES" / "REPO" / "QS01_qshrink2_corpus_ecosystem.md", build_capsule(summary, docs))
    write_text(FLEET_NETWORK_DIR / "15_QSHRINK2_ACTIVE_FRONT.md", build_active_front(summary, docs))

    return {
        "summary": summary,
        "docs": {"docs_gate_status": docs["docs_gate_status"]},
        "output_dir": str(OUTPUT_DIR),
        "capsule_path": str(FLEET_NETWORK_DIR / "CAPSULES" / "REPO" / "QS01_qshrink2_corpus_ecosystem.md"),
    }
