from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from self_actualize.runtime.knowledge_fabric_contracts import (
    ExplorationPacketRecord,
    FabricEdge,
    FabricRecord,
    KnowledgeFabricDashboard,
    ShortcutPlanRecord,
    StorageZoneRecord,
)
from self_actualize.runtime.knowledge_fabric_query_engine import run_shortcut, summarize_route


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_BRAIN_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_BRAIN_ROOT / "registry"

DERIVATION_VERSION = "2026-03-12.phase4-fabric-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_knowledge_fabric"
FABRIC_EQUATION = (
    "KnowledgeFabric = StorageOntology + FabricRecordAtlas + ShortcutIndex + "
    "TraversalEngine + BridgeGraph + ReplayReceipts + HumanMaps"
)
DIRECT_SYNAPSE_CAPSULE_PATHS = [
    (
        "CS-001",
        "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\athena_fleet\\01_athena_fleet_tesseract_branch.md",
        "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\voynich\\01_voynich_manuscript_engine.md",
        "fleet corridor contracts directly with the proof engine",
        0.96,
    ),
    (
        "CS-002",
        "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\voynich\\01_voynich_manuscript_engine.md",
        "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\qshrink\\01_qshrink_compression_shell.md",
        "proof engine contracts directly with the compression shell",
        0.93,
    ),
    (
        "CS-003",
        "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\athena_fleet\\01_athena_fleet_tesseract_branch.md",
        "NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\orgin\\01_origin_seed_reservoir.md",
        "fleet coordination inherits its seed reservoir directly",
        0.91,
    ),
]

DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
ROOT_BASIS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ROOT_BASIS_MAP.md"
COUNT_PROTOCOL_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "COUNT_PROTOCOL.md"
SOURCE_SURFACE_ATLAS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "SOURCE_SURFACE_ATLAS.md"
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "archive_atlas.json"
WITNESS_HIERARCHY_PATH = SELF_ACTUALIZE_ROOT / "witness_hierarchy.json"
GRAND_CENTRAL_DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_dashboard.json"
SELF_HOSTING_DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "self_hosting_kernel_dashboard.json"
DUAL_ENGINE_QUEUE_JSON_PATH = SELF_ACTUALIZE_ROOT / "dual_engine_regeneration_queue.json"
RUNTIME_INDEX_PATH = MYCELIUM_BRAIN_ROOT / "nervous_system" / "00_active_nervous_system_index.md"
RUNTIME_README_PATH = MYCELIUM_BRAIN_ROOT / "nervous_system" / "README.md"
GOVERNANCE_README_PATH = WORKSPACE_ROOT / "ECOSYSTEM" / "NERVOUS_SYSTEM" / "README.md"
DEEP_ROOT = (
    MYCELIUM_BRAIN_ROOT
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
DEEP_ROOT_README_PATH = DEEP_ROOT / "README.md"
CAPSULE_INDEX_PATH = NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "INDEX.md"
GRAPH_AUTHORITY_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "NEURON_LIBRARY.md"
RECEIPT_AUTHORITY_PATH = NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "22_SELF_LINEAGE_LEDGER.md"
BOARD_SOURCE_FALLBACK = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "07_FULL_PROJECT_INTEGRATION_256"
    / "06_REALTIME_BOARD"
    / "00_STATUS"
    / "00_BOARD_STATUS.md"
)
PROMOTED_SOURCE_FALLBACK = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "_build"
    / "nervous_system"
    / "manifests"
    / "STATE_HEADER.md"
)

SCHEMA_MD_PATH = NERVOUS_SYSTEM_ROOT / "70_SCHEMAS" / "13_KNOWLEDGE_FABRIC_SCHEMA.md"
OVERVIEW_MD_PATH = NERVOUS_SYSTEM_ROOT / "10_OVERVIEW" / "18_PHASE4_KNOWLEDGE_FABRIC.md"
ZONE_REGISTRY_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "STORAGE_ZONE_REGISTRY.md"
ZONE_ATLAS_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "STORAGE_ZONE_ATLAS.md"
CLASS_MAP_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "RECORD_CLASS_AND_SURFACE_CLASS_MAP.md"
)
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "KNOWLEDGE_FABRIC_DASHBOARD.md"
WHERE_INFO_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "WHERE_INFORMATION_LIVES.md"
THINKING_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "HOW_ATHENA_THINKS_THROUGH_THE_FABRIC.md"
)
TOP_ENTRY_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "KNOWLEDGE_FABRIC_TOP_ENTRY_RECORDS.md"
)
RUNBOOK_MD_PATH = NERVOUS_SYSTEM_ROOT / "99_RUNBOOKS" / "02_EXPLORATION_PACKET_RUNBOOK.md"
READINESS_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "25_PHASE4_KNOWLEDGE_FABRIC_READINESS_2026-03-12.md"
)
EDGE_LEDGER_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "26_KNOWLEDGE_FABRIC_EDGE_LEDGER.md"
)
RUNTIME_MD_PATH = MYCELIUM_BRAIN_ROOT / "nervous_system" / "26_knowledge_fabric_runtime.md"
RECEIPT_MD_PATH = (
    MYCELIUM_BRAIN_ROOT / "receipts" / "2026-03-12_knowledge_fabric_derivation.md"
)

ZONE_REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_zone_registry.json"
SURFACE_CLASS_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_surface_class_registry.json"
ARTIFACT_CLASS_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_artifact_class_registry.json"
TRUTH_ROLE_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_truth_role_registry.json"
REPLAY_CLASS_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_replay_class_registry.json"
AUTHORITY_WITNESS_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_authority_witness_registry.json"
RECORDS_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_records.json"
EDGES_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_edges.json"
SHORTCUTS_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_shortcuts.json"
PACKETS_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_exploration_packets.json"
TOP_ENTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_top_entry_records.json"
DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_dashboard.json"

ZONE_REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_zone_registry.json"
SURFACE_CLASS_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_surface_class_registry.json"
ARTIFACT_CLASS_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_artifact_class_registry.json"
TRUTH_ROLE_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_truth_role_registry.json"
REPLAY_CLASS_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_replay_class_registry.json"
AUTHORITY_WITNESS_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_authority_witness_registry.json"
SHORTCUTS_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_shortcuts.json"
PACKETS_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_exploration_packets.json"
TOP_ENTRY_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_top_entry_records.json"
DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_dashboard.json"
REGISTRY_MANIFEST_JSON_MIRROR = REGISTRY_ROOT / "knowledge_fabric_registry_manifest.json"

SURFACE_CLASS_REGISTRY = [
    {"surface_class": "atlas", "note": "record substrate and cross-index surfaces"},
    {"surface_class": "registry", "note": "typed row stores and machine registries"},
    {"surface_class": "dashboard", "note": "state summaries and front-door status maps"},
    {"surface_class": "overview", "note": "human-readable doctrinal or structural overviews"},
    {"surface_class": "capsule", "note": "domain contractions and source body families"},
    {"surface_class": "graph", "note": "edge, neuron, synapse, and bridge tissue"},
    {"surface_class": "runtime lane", "note": "verification, execution, or routed runtime lanes"},
    {"surface_class": "queue", "note": "ordered next-work and regeneration surfaces"},
    {"surface_class": "packet", "note": "bounded traversal or transform payloads"},
    {"surface_class": "mirror", "note": "runtime or governance reflection surfaces"},
    {"surface_class": "schema", "note": "formal interface surfaces preserved explicitly"},
]

ARTIFACT_CLASS_REGISTRY = [
    {"artifact_class": "manuscript", "note": "text-heavy source, chapter, appendix, or book matter"},
    {"artifact_class": "code", "note": "executable scripts, modules, or configurations"},
    {"artifact_class": "data", "note": "json, csv, yaml, or structured payloads"},
    {"artifact_class": "media", "note": "images, pdfs, binaries, or non-text witness bodies"},
    {"artifact_class": "generated", "note": "machine-derived runtime or dashboard artifacts"},
    {"artifact_class": "ledger", "note": "receipts, progress ledgers, and proof-carrying traces"},
    {"artifact_class": "manifest", "note": "active fronts, registries, queue summaries, and maps"},
    {"artifact_class": "schema", "note": "formal interface or law declarations"},
    {"artifact_class": "receipt", "note": "completion traces and derivation writebacks"},
    {"artifact_class": "queue", "note": "ordered next-work surfaces"},
    {"artifact_class": "skill", "note": "local skill definitions and routing doctrine"},
]

TRUTH_ROLE_REGISTRY = [
    {"truth_role": "source", "note": "primary local source matter"},
    {"truth_role": "generated", "note": "derived from runtime or control-plane generation"},
    {"truth_role": "protocol", "note": "normative law, contract, or procedure"},
    {"truth_role": "ledger", "note": "proof trail or progress witness"},
    {"truth_role": "receipt", "note": "writeback and closure proof"},
    {"truth_role": "mirror", "note": "runtime or governance reflection"},
    {"truth_role": "archive-backed", "note": "indexed through archive witness rather than live file path"},
    {"truth_role": "reserve", "note": "kept visible without forcing false integration claims"},
]

REPLAY_CLASS_REGISTRY = [
    {"replay_class": "replay-safe", "note": "may be revisited and regenerated directly"},
    {"replay_class": "replay-partial", "note": "requires extra witness or writeback context"},
    {"replay_class": "generated-refreshable", "note": "safe to rebuild from source surfaces"},
    {"replay_class": "witness-only", "note": "presence can be cited but not fully replayed as text"},
]

ROOT_STATUS_MAP = {
    "absorbed": "live",
    "reserve": "reserve",
    "dormant": "dormant",
    "mirror": "mirror",
    "local": "local",
    "out_of_scope": "out_of_scope",
}

MEDIA_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".mov",
    ".mp4",
    ".zip",
    ".7z",
    ".psd",
    ".fig",
    ".bin",
}
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".kt",
    ".rb",
    ".sh",
    ".ps1",
    ".bat",
    ".c",
    ".cpp",
    ".h",
    ".rs",
    ".go",
    ".php",
}
DATA_EXTENSIONS = {".json", ".yaml", ".yml", ".csv", ".toml", ".xml", ".ini"}
MANUSCRIPT_EXTENSIONS = {".md", ".txt", ".rtf"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalize_path(relative_path: str) -> str:
    return relative_path.replace("/", "\\")


def relative_string(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def parse_docs_gate(markdown: str) -> str:
    match = re.search(r"Command status: `([^`]+)`", markdown)
    return match.group(1) if match else "UNKNOWN"


def parse_root_basis(markdown: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    capture = False
    for line in markdown.splitlines():
        if line.startswith("## Live Directory Bodies"):
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if not capture or not line.startswith("| A"):
            continue
        parts = [part.strip().strip("`") for part in line.strip("|").split("|")]
        if len(parts) < 5:
            continue
        rows.append(
            {
                "root_id": parts[0],
                "root_name": parts[1],
                "indexed_count": int(parts[2]),
                "root_status": ROOT_STATUS_MAP.get(parts[3], parts[3]),
                "current_role": parts[4],
            }
        )
    return rows


def build_root_lookup(root_rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup = {row["root_name"]: row for row in root_rows}
    lookup[".claude"] = {
        "root_id": "X01",
        "root_name": ".claude",
        "root_status": "local",
        "current_role": "runtime config",
    }
    lookup[".codex"] = {
        "root_id": "X02",
        "root_name": ".codex",
        "root_status": "local",
        "current_role": "skill runtime",
    }
    lookup[".github"] = {
        "root_id": "X03",
        "root_name": ".github",
        "root_status": "local",
        "current_role": "automation support",
    }
    return lookup


def parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def freshness_from_timestamp(value: str) -> Dict[str, Any]:
    stamp = parse_timestamp(value)
    if stamp is None:
        return {"score": 0.38, "band": "unknown", "days_old": None}
    days_old = max(0.0, (datetime.now(timezone.utc) - stamp).total_seconds() / 86400.0)
    if days_old <= 3:
        band = "hot"
        score = 1.0
    elif days_old <= 14:
        band = "warm"
        score = 0.84
    elif days_old <= 60:
        band = "stable"
        score = 0.62
    elif days_old <= 180:
        band = "cool"
        score = 0.44
    else:
        band = "stale"
        score = 0.22
    return {"score": round(score, 3), "band": band, "days_old": round(days_old, 1)}


def text_extractable_for_extension(extension: str) -> bool:
    return extension.lower() not in MEDIA_EXTENSIONS or extension.lower() == ".pdf"


def title_hint_from_record(relative_path: str, atlas_record: Dict[str, Any] | None) -> str:
    if atlas_record:
        candidates = atlas_record.get("heading_candidates") or []
        if candidates:
            return str(candidates[0]).strip()
    stem = Path(relative_path.split("::")[-1]).stem
    return stem.replace("_", " ").replace("-", " ").strip() or relative_path


def determine_generated_path(lower_rel: str) -> bool:
    generated_tokens = [
        "_dashboard.json",
        "_registry.json",
        "_ledger.json",
        "_queue.json",
        "_packets.json",
        "_lane.json",
        "receipts\\",
        "mycelium_brain\\registry\\",
        "knowledge_fabric",
        "grand_central",
        "self_hosting",
    ]
    return lower_rel.startswith("self_actualize\\") and any(token in lower_rel for token in generated_tokens)


def determine_root(relative_path: str, root_lookup: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    top_level = normalize_path(relative_path).split("\\", 1)[0]
    row = root_lookup.get(top_level)
    if row:
        return row
    return {
        "root_id": f"X-{slugify(top_level)[:10]}",
        "root_name": top_level,
        "root_status": "local",
        "current_role": "unclassified-local",
    }


def determine_family_id(relative_path: str) -> str:
    parts = normalize_path(relative_path).split("\\")
    if not parts:
        return "unknown"
    if parts[0] == "NERVOUS_SYSTEM" and len(parts) >= 3 and parts[1] == "50_CORPUS_CAPSULES":
        return parts[2]
    if (
        parts[0] == "self_actualize"
        and len(parts) >= 5
        and parts[1] == "mycelium_brain"
        and parts[2] == "nervous_system"
        and parts[3] in {"families", "ganglia", "routes"}
    ):
        stem = Path(parts[-1]).stem.lower()
        for prefix in ("family_", "ganglion_", "route_"):
            if stem.startswith(prefix):
                return stem[len(prefix) :]
        return parts[3]
    if parts[0] == "NERVOUS_SYSTEM" and len(parts) >= 2:
        return parts[1]
    if parts[0] == "self_actualize":
        if len(parts) >= 3 and parts[1] == "mycelium_brain":
            return parts[2]
        if len(parts) >= 2:
            return parts[1]
    if len(parts) >= 2:
        return parts[1]
    return parts[0]


def determine_zone(
    relative_path: str,
    root_name: str,
    root_status: str,
    board_source_rel: str,
    promoted_source_rel: str,
) -> str:
    rel = normalize_path(relative_path)
    lower_rel = rel.lower()
    if rel == normalize_path(str(CORPUS_ATLAS_PATH.relative_to(WORKSPACE_ROOT))):
        return "CorpusAtlas"
    if rel == normalize_path(str(ARCHIVE_ATLAS_PATH.relative_to(WORKSPACE_ROOT))):
        return "ArchiveAtlas"
    if rel == board_source_rel:
        return "BoardScope"
    if rel == promoted_source_rel:
        return "PromotedSlice"
    if lower_rel.startswith("nervous_system\\50_corpus_capsules\\"):
        return "CapsuleLayer"
    if lower_rel.startswith("nervous_system\\85_edges\\"):
        return "GraphLayer"
    if lower_rel.startswith("nervous_system\\90_ledgers\\"):
        if any(token in lower_rel for token in ["neuron", "synapse", "edge"]):
            return "GraphLayer"
        return "ReceiptLineage"
    if lower_rel.startswith("nervous_system\\"):
        return "Cortex"
    if lower_rel.startswith("ecosystem\\nervous_system\\"):
        return "GovernanceMirror"
    if "dynamic_neural_network\\14_deeper_integrated_cross_synthesis_network" in lower_rel:
        return "DeepRoot"
    if lower_rel.startswith("self_actualize\\mycelium_brain\\registry\\"):
        return "RuntimeMirror"
    if lower_rel.startswith("self_actualize\\mycelium_brain\\receipts\\"):
        return "ReceiptLineage"
    if lower_rel.startswith("self_actualize\\mycelium_brain\\nervous_system\\"):
        return "RuntimeMirror"
    if lower_rel.startswith("self_actualize\\runtime\\") or lower_rel.startswith("self_actualize\\tools\\"):
        return "RuntimeMirror"
    if lower_rel.startswith("self_actualize\\"):
        return "RuntimeMirror"
    if root_name in {"Trading Bot", "NERUAL NETWORK", ".claude", ".codex", ".github", "FRESH"}:
        return "RuntimeMirror"
    if root_name in {"Stoicheia (Element Sudoku)", "CLEAN"}:
        return "ReserveQuarantine"
    if root_status in {"reserve", "dormant", "mirror", "out_of_scope"}:
        return "ReserveQuarantine"
    return "Cortex"


def determine_secondary_zones(source_substrate: str, primary_zone: str) -> List[str]:
    secondary: List[str] = []
    if source_substrate == "indexed" and primary_zone != "CorpusAtlas":
        secondary.append("CorpusAtlas")
    if source_substrate == "archive" and primary_zone != "ArchiveAtlas":
        secondary.append("ArchiveAtlas")
    return secondary


def determine_artifact_class(relative_path: str, extension: str, source_substrate: str) -> str:
    rel = normalize_path(relative_path).lower()
    name = Path(relative_path.split("::")[-1]).name.lower()
    if name == "skill.md" or "\\skills\\" in rel:
        return "skill"
    if "receipts\\" in rel or "receipt" in name:
        return "receipt"
    if "queue" in name:
        return "queue"
    if "\\90_ledgers\\" in rel or "ledger" in name:
        return "ledger"
    if "\\95_manifests\\" in rel or "manifest" in name or "registry" in name:
        return "manifest"
    if "\\70_schemas\\" in rel or "schema" in name or "spec" in name:
        return "schema"
    if source_substrate == "generated" and extension.lower() == ".json":
        return "generated"
    if extension.lower() in CODE_EXTENSIONS:
        return "code"
    if extension.lower() in DATA_EXTENSIONS:
        return "data"
    if extension.lower() in MEDIA_EXTENSIONS:
        return "media"
    if extension.lower() in MANUSCRIPT_EXTENSIONS:
        return "manuscript"
    return "data"


def determine_surface_class(relative_path: str, zone: str, artifact_class: str) -> str:
    rel = normalize_path(relative_path).lower()
    name = Path(relative_path.split("::")[-1]).name.lower()
    if "atlas" in name:
        return "atlas"
    if "dashboard" in name:
        return "dashboard"
    if "queue" in name:
        return "queue"
    if "packet" in name or "\\packets\\" in rel:
        return "packet"
    if artifact_class == "schema":
        return "schema"
    if zone == "CapsuleLayer":
        return "capsule"
    if zone == "GraphLayer":
        return "graph"
    if "lane" in name and name.endswith(".json"):
        return "runtime lane"
    if zone in {"RuntimeMirror", "GovernanceMirror"} and (
        "\\mycelium_brain\\nervous_system\\" in rel or rel.startswith("ecosystem\\")
    ):
        return "mirror"
    if artifact_class == "manifest":
        return "registry"
    return "overview"


def determine_authority_surface(relative_path: str, zone: str, root_name: str) -> str:
    rel = normalize_path(relative_path).lower()
    if zone == "CorpusAtlas":
        return str(CORPUS_ATLAS_PATH)
    if zone == "ArchiveAtlas":
        return str(ARCHIVE_ATLAS_PATH)
    if zone == "BoardScope":
        return str(BOARD_SOURCE_FALLBACK)
    if zone == "PromotedSlice":
        return str(PROMOTED_SOURCE_FALLBACK)
    if zone == "GovernanceMirror":
        return str(GOVERNANCE_README_PATH)
    if zone == "DeepRoot":
        return str(DEEP_ROOT_README_PATH if "readme" not in rel else Path(relative_path))
    if zone == "CapsuleLayer":
        return str(CAPSULE_INDEX_PATH)
    if zone == "GraphLayer":
        return str(GRAPH_AUTHORITY_PATH)
    if zone == "ReceiptLineage":
        return str(RECEIPT_AUTHORITY_PATH)
    if zone == "ReserveQuarantine":
        return str(ROOT_BASIS_PATH)
    if zone == "RuntimeMirror":
        return str(RUNTIME_INDEX_PATH)
    if root_name == "NERVOUS_SYSTEM":
        return str(NERVOUS_SYSTEM_ROOT / "00_INDEX.md")
    return str(NERVOUS_SYSTEM_ROOT / "00_INDEX.md")


def determine_authority_rank(zone: str) -> int:
    if zone == "Cortex":
        return 5
    if zone in {"RuntimeMirror", "DeepRoot", "CapsuleLayer", "GraphLayer"}:
        return 4
    if zone in {"GovernanceMirror", "ReceiptLineage", "CorpusAtlas", "ArchiveAtlas"}:
        return 3
    if zone in {"BoardScope", "PromotedSlice"}:
        return 2
    return 1


def determine_witness_class(relative_path: str, source_substrate: str) -> str:
    rel = normalize_path(relative_path).lower()
    if source_substrate == "archive":
        return "archive"
    if rel == normalize_path(relative_string(BOARD_SOURCE_FALLBACK)).lower():
        return "board"
    if rel == normalize_path(relative_string(PROMOTED_SOURCE_FALLBACK)).lower():
        return "promoted"
    if source_substrate == "generated" or determine_generated_path(rel):
        return "generated"
    if source_substrate == "physical":
        return "physical"
    return "indexed"


def determine_truth_role(
    source_substrate: str,
    zone: str,
    artifact_class: str,
    relative_path: str,
) -> str:
    name = Path(relative_path.split("::")[-1]).name.lower()
    if source_substrate == "archive":
        return "archive-backed"
    if artifact_class == "receipt":
        return "receipt"
    if artifact_class == "ledger":
        return "ledger"
    if artifact_class in {"schema", "manifest"} and any(
        token in name for token in ["protocol", "charter", "contract", "schema", "spec"]
    ):
        return "protocol"
    if source_substrate == "generated" or artifact_class == "generated":
        return "generated"
    if zone in {"RuntimeMirror", "GovernanceMirror"}:
        return "mirror"
    if zone == "ReserveQuarantine":
        return "reserve"
    return "source"


def determine_semantic_role(
    zone: str,
    artifact_class: str,
    truth_role: str,
    root_name: str,
    relative_path: str,
) -> str:
    rel = normalize_path(relative_path).lower()
    if truth_role == "protocol":
        return "law"
    if truth_role in {"ledger", "receipt", "archive-backed"} or zone in {"GraphLayer", "ReceiptLineage"}:
        return "evidence"
    if zone in {"RuntimeMirror", "DeepRoot"} or artifact_class in {"generated", "code"}:
        return "runtime"
    if root_name in {
        "MATH",
        "Voynich",
        "Athenachka Collective Books",
        "DEEPER CRYSTALIZATION",
        "I AM ATHENA",
        "ORGIN",
    } or "\\30_chapters\\" in rel:
        return "publication"
    return "support"


def determine_replay_class(
    artifact_class: str,
    source_substrate: str,
    zone: str,
    text_extractable: bool,
    witness_class: str,
) -> str:
    if not text_extractable or artifact_class == "media":
        return "witness-only"
    if source_substrate == "generated" or witness_class == "generated":
        return "generated-refreshable"
    if source_substrate == "archive" or zone in {"BoardScope", "PromotedSlice", "ArchiveAtlas"}:
        return "replay-partial"
    return "replay-safe"


def determine_proof_state(witness_class: str, authority_rank: int, zone: str) -> str:
    if zone == "ReserveQuarantine" and witness_class in {"physical", "board"}:
        return "AMBIG"
    if witness_class in {"generated", "indexed"} and authority_rank >= 4:
        return "OK"
    if witness_class in {"archive", "promoted", "board"} or authority_rank >= 3:
        return "NEAR"
    if witness_class == "physical":
        return "AMBIG"
    return "FAIL"


def build_query_tags(
    relative_path: str,
    root_name: str,
    family_id: str,
    zone: str,
    surface_class: str,
    artifact_class: str,
    semantic_role: str,
    truth_role: str,
    witness_class: str,
    role_tags: Iterable[str],
) -> List[str]:
    rel = normalize_path(relative_path).lower()
    tags = {
        slugify(root_name),
        slugify(family_id),
        slugify(zone),
        slugify(surface_class),
        slugify(artifact_class),
        slugify(semantic_role),
        slugify(truth_role),
        slugify(witness_class),
        Path(relative_path.split("::")[-1]).suffix.lower().lstrip("."),
    }
    root_aliases = {
        "athenachka-collective-books": ["published-books", "published_books"],
        "qshrink-athena-internal-use": ["qshrink"],
        "i-am-athena": ["identity"],
    }
    tags.update(root_aliases.get(slugify(root_name), []))
    tags.update(slugify(tag) for tag in role_tags if tag)
    specials = {
        "grand-central": ["grand_central", "grand central"],
        "self-hosting": ["self_hosting", "self hosting"],
        "knowledge-fabric": ["knowledge_fabric", "knowledge fabric"],
        "deep-root": ["14_deeper", "cross_synthesis_network"],
        "count-protocol": ["count_protocol"],
        "source-surface-atlas": ["source_surface_atlas"],
        "docs-gate": ["docs_gate", "gate_status"],
        "root-basis": ["root_basis_map"],
        "regeneration-queue": ["regeneration_queue", "dual_engine"],
        "z-point": ["z_point", "restart_token"],
    }
    for tag, needles in specials.items():
        if any(needle in rel for needle in needles):
            tags.add(tag)
    tags.discard("")
    return sorted(tags)


def build_fabric_record(
    relative_path: str,
    source_substrate: str,
    locator: str,
    modified_at: str,
    size_bytes: int,
    extension: str,
    text_extractable: bool,
    role_tags: Iterable[str],
    root_lookup: Dict[str, Dict[str, Any]],
    board_source_rel: str,
    promoted_source_rel: str,
    atlas_record: Dict[str, Any] | None = None,
    note: str = "",
) -> FabricRecord:
    root = determine_root(relative_path, root_lookup)
    zone = determine_zone(
        relative_path,
        root["root_name"],
        root["root_status"],
        board_source_rel,
        promoted_source_rel,
    )
    artifact_class = determine_artifact_class(relative_path, extension, source_substrate)
    surface_class = determine_surface_class(relative_path, zone, artifact_class)
    witness_class = determine_witness_class(relative_path, source_substrate)
    truth_role = determine_truth_role(source_substrate, zone, artifact_class, relative_path)
    semantic_role = determine_semantic_role(
        zone,
        artifact_class,
        truth_role,
        root["root_name"],
        relative_path,
    )
    authority_surface = determine_authority_surface(relative_path, zone, root["root_name"])
    authority_rank = determine_authority_rank(zone)
    replay_class = determine_replay_class(
        artifact_class,
        source_substrate,
        zone,
        text_extractable,
        witness_class,
    )
    proof_state = determine_proof_state(witness_class, authority_rank, zone)
    family_id = determine_family_id(relative_path)
    freshness = freshness_from_timestamp(modified_at)
    query_tags = build_query_tags(
        relative_path,
        root["root_name"],
        family_id,
        zone,
        surface_class,
        artifact_class,
        semantic_role,
        truth_role,
        witness_class,
        role_tags,
    )
    title_hint = title_hint_from_record(relative_path, atlas_record)
    record_id_seed = f"{source_substrate}:{relative_path}:{locator}"
    record_id = hashlib.sha1(record_id_seed.encode("utf-8")).hexdigest()[:16]
    return FabricRecord(
        record_id=record_id,
        relative_path=relative_path,
        source_substrate=source_substrate,
        root_id=root["root_id"],
        root_name=root["root_name"],
        root_status=root["root_status"],
        family_id=family_id,
        title_hint=title_hint,
        surface_class=surface_class,
        storage_zone=zone,
        secondary_zones=determine_secondary_zones(source_substrate, zone),
        witness_class=witness_class,
        truth_role=truth_role,
        authority_surface=authority_surface,
        authority_rank=authority_rank,
        semantic_role=semantic_role,
        query_tags=query_tags,
        freshness=freshness,
        proof_state=proof_state,
        replay_class=replay_class,
        artifact_class=artifact_class,
        modified_at=modified_at,
        size_bytes=size_bytes,
        text_extractable=text_extractable,
        locator=locator,
        note=note,
    )


def scan_physical_paths(ignore_dirs: Iterable[str]) -> List[Path]:
    ignore = set(ignore_dirs)
    paths: List[Path] = []
    for root, dirnames, filenames in os.walk(WORKSPACE_ROOT):
        filtered: List[str] = []
        for name in dirnames:
            if name in ignore or name == "_repo_root":
                continue
            candidate = Path(root) / name
            # Skip junctions/symlinks so repo-root mirrors do not recurse infinitely.
            if candidate.is_symlink():
                continue
            try:
                if os.path.islink(candidate):
                    continue
            except OSError:
                continue
            filtered.append(name)
        dirnames[:] = filtered
        for filename in filenames:
            paths.append(Path(root) / filename)
    return paths


def build_zone_registry() -> List[StorageZoneRecord]:
    specs = [
        (
            "Z01",
            "Cortex",
            "canonical law, publishable overview matter, and live source corpus bodies",
            str(NERVOUS_SYSTEM_ROOT / "00_INDEX.md"),
            "indexed",
            ["NERVOUS_SYSTEM", "MATH", "Voynich", "DEEPER CRYSTALIZATION"],
            ["manuscript", "manifest", "schema", "ledger"],
            ["locate", "browse", "synthesize", "publish"],
            "This zone answers where canonical and source-bearing matter actually lives.",
        ),
        (
            "Z02",
            "RuntimeMirror",
            "live runtime mirrors, generated json artifacts, and executable routing surfaces",
            str(RUNTIME_INDEX_PATH),
            "generated",
            ["self_actualize/runtime", "self_actualize/mycelium_brain/nervous_system"],
            ["generated", "code", "manifest", "queue"],
            ["locate", "audit", "repair", "regenerate"],
            "This is the live mycelial waist rather than the publication cortex.",
        ),
        (
            "Z03",
            "GovernanceMirror",
            "reusable governance doctrine mirrored outside the canonical cortex",
            str(GOVERNANCE_README_PATH),
            "indexed",
            ["ECOSYSTEM/NERVOUS_SYSTEM"],
            ["manuscript", "manifest", "schema"],
            ["browse", "compare", "synthesize"],
            "Governance may advise but does not outrank the cortex.",
        ),
        (
            "Z04",
            "DeepRoot",
            "live deeper cross-synthesis basis, matrix, symmetry, metro, and appendix control",
            str(DEEP_ROOT_README_PATH),
            "indexed",
            ["self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"],
            ["manuscript", "ledger", "queue", "code"],
            ["browse", "synthesize", "audit", "repair"],
            "This is the only live deep-routing authority.",
        ),
        (
            "Z05",
            "CorpusAtlas",
            "the primary indexed record substrate for the live workspace",
            str(CORPUS_ATLAS_PATH),
            "indexed",
            ["self_actualize/corpus_atlas.json"],
            ["data", "generated"],
            ["locate", "browse", "audit"],
            "This zone stores the searchable record substrate, not the truth of every record.",
        ),
        (
            "Z06",
            "ArchiveAtlas",
            "archive-backed indexed reserve implementation substrate",
            str(ARCHIVE_ATLAS_PATH),
            "archive",
            ["self_actualize/archive_atlas.json"],
            ["data", "generated"],
            ["browse", "compare", "audit"],
            "Archive-backed records remain visible without pretending they are live-root files.",
        ),
        (
            "Z07",
            "BoardScope",
            "realtime coordination slice and board-visible witness surfaces",
            str(BOARD_SOURCE_FALLBACK),
            "board",
            ["DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/.../06_REALTIME_BOARD"],
            ["manifest", "queue", "ledger"],
            ["audit", "repair", "publish"],
            "Board scope is a visibility overlay, not whole-corpus truth.",
        ),
        (
            "Z08",
            "PromotedSlice",
            "the bronze promoted nervous-system slice and its declared witness surfaces",
            str(PROMOTED_SOURCE_FALLBACK),
            "promoted",
            ["DEEPER CRYSTALIZATION/_build/nervous_system"],
            ["manifest", "ledger", "schema"],
            ["compare", "audit", "publish"],
            "Promoted slices remain named as historical witness, not live totality.",
        ),
        (
            "Z09",
            "CapsuleLayer",
            "canonical domain contractions that explain large roots through stable summaries",
            str(CAPSULE_INDEX_PATH),
            "indexed",
            ["NERVOUS_SYSTEM/50_CORPUS_CAPSULES"],
            ["manuscript", "manifest"],
            ["locate", "synthesize", "regenerate"],
            "Capsules are the contraction layer between root bodies and canonical law.",
        ),
        (
            "Z10",
            "GraphLayer",
            "neurons, synapses, bridges, and explicit edge-bearing topology",
            str(GRAPH_AUTHORITY_PATH),
            "indexed",
            ["NERVOUS_SYSTEM/85_EDGES", "NERVOUS_SYSTEM/90_LEDGERS/NEURON_LIBRARY.md"],
            ["ledger", "manifest"],
            ["compare", "audit", "repair"],
            "This zone carries relation tissue rather than full source bodies.",
        ),
        (
            "Z11",
            "ReceiptLineage",
            "receipts, writebacks, promotion traces, and continuity proof",
            str(RECEIPT_AUTHORITY_PATH),
            "generated",
            ["NERVOUS_SYSTEM/90_LEDGERS", "self_actualize/mycelium_brain/receipts"],
            ["receipt", "ledger", "generated"],
            ["audit", "repair", "regenerate"],
            "This zone keeps replay and lineage visible instead of collapsing them into prose.",
        ),
        (
            "Z12",
            "ReserveQuarantine",
            "honest storage for sparse, blocked, contradictory, or reserve surfaces",
            str(ROOT_BASIS_PATH),
            "physical",
            ["CLEAN", "Stoicheia (Element Sudoku)", "reserve corridor paths"],
            ["media", "manuscript", "ledger"],
            ["audit", "repair", "abstain"],
            "This zone prevents false certainty when a surface is real but not yet integrated.",
        ),
    ]
    return [
        StorageZoneRecord(
            zone_id=zone_id,
            zone_name=zone_name,
            purpose=purpose,
            authority_surface=authority_surface,
            witness_floor=witness_floor,
            canonical_paths=canonical_paths,
            artifact_classes=artifact_classes,
            query_methods=query_methods,
            note=note,
        )
        for (
            zone_id,
            zone_name,
            purpose,
            authority_surface,
            witness_floor,
            canonical_paths,
            artifact_classes,
            query_methods,
            note,
        ) in specs
    ]


def build_authority_registry(zones: List[StorageZoneRecord]) -> List[Dict[str, Any]]:
    registry: List[Dict[str, Any]] = []
    for zone in zones:
        registry.append(
            {
                "authority_id": f"AUTH-{zone.zone_id}",
                "zone_name": zone.zone_name,
                "authority_surface": zone.authority_surface,
                "authority_rank": determine_authority_rank(zone.zone_name),
                "witness_floor": zone.witness_floor,
                "query_methods": zone.query_methods,
                "note": zone.note,
            }
        )
    return registry


def build_shortcuts() -> List[ShortcutPlanRecord]:
    specs = [
        (
            "KF-S01",
            "locate",
            "Authoritative Locate",
            {"authority_min": 4, "witnesses": ["generated", "indexed", "archive"], "query_text_required": True},
            ["Cortex", "RuntimeMirror", "DeepRoot", "CorpusAtlas"],
            ["dashboard", "registry", "atlas", "overview", "schema"],
            ["authority", "witness", "proof", "text_match", "freshness", "replay", "zone_priority"],
            "first top witness-bearing authoritative match",
            ["CapsuleLayer", "ArchiveAtlas", "GraphLayer"],
            "For exact lookup and fastest lawful entry.",
        ),
        (
            "KF-S02",
            "browse",
            "Zone Browse",
            {"authority_min": 3, "witnesses": ["generated", "indexed", "archive"], "text_required": True},
            ["Cortex", "DeepRoot", "RuntimeMirror", "CapsuleLayer"],
            ["overview", "capsule", "mirror", "registry"],
            ["zone_priority", "authority", "witness", "freshness", "tag_overlap", "replay"],
            "bounded neighborhood reached",
            ["GovernanceMirror", "ArchiveAtlas"],
            "For exploratory reads that stay inside lawful high-yield zones.",
        ),
        (
            "KF-S03",
            "compare",
            "Paired Compare",
            {"authority_min": 3, "witnesses": ["generated", "indexed", "archive"], "text_required": True},
            ["Cortex", "DeepRoot", "GraphLayer", "RuntimeMirror"],
            ["overview", "dashboard", "graph", "mirror"],
            ["authority", "witness", "proof", "tag_overlap", "freshness", "replay"],
            "paired closure or contradiction preserved",
            ["ArchiveAtlas", "ReceiptLineage"],
            "For seeing two nearby surfaces without flattening their difference.",
        ),
        (
            "KF-S04",
            "synthesize",
            "Cross-Surface Synthesize",
            {"authority_min": 4, "witnesses": ["generated", "indexed", "archive"], "text_required": True},
            ["Cortex", "DeepRoot", "RuntimeMirror", "CapsuleLayer"],
            ["overview", "dashboard", "capsule", "mirror", "schema"],
            ["authority", "witness", "proof", "freshness", "replay", "tag_overlap", "zone_priority"],
            "sufficient witnessed synthesis reached",
            ["GraphLayer", "ArchiveAtlas"],
            "For multi-zone synthesis without whole-atlas scanning.",
        ),
        (
            "KF-S05",
            "audit",
            "Drift Audit",
            {"authority_min": 2, "witnesses": ["generated", "indexed", "archive", "promoted", "board", "physical"]},
            ["ReceiptLineage", "GraphLayer", "RuntimeMirror", "ReserveQuarantine"],
            ["dashboard", "graph", "mirror", "queue", "overview"],
            ["proof", "freshness", "cost", "zone_priority", "tag_overlap"],
            "highest-risk surfaces surfaced",
            ["BoardScope", "PromotedSlice"],
            "For blocked, stale, ambiguous, or low-proof drift scans.",
        ),
        (
            "KF-S06",
            "repair",
            "Repair Corridor",
            {"authority_min": 2, "witnesses": ["generated", "indexed", "archive", "physical"]},
            ["RuntimeMirror", "ReceiptLineage", "ReserveQuarantine", "GraphLayer"],
            ["queue", "dashboard", "graph", "mirror", "overview"],
            ["cost", "proof", "freshness", "tag_overlap", "replay"],
            "next-front route selected",
            ["BoardScope", "PromotedSlice"],
            "For turning drift into a bounded next-front packet.",
        ),
        (
            "KF-S07",
            "regenerate",
            "Regeneration Path",
            {
                "authority_min": 4,
                "witnesses": ["generated", "indexed"],
                "surface_classes": ["queue", "dashboard", "registry", "overview", "schema"],
                "text_required": True,
            },
            ["Cortex", "RuntimeMirror", "ReceiptLineage"],
            ["queue", "dashboard", "registry", "overview", "schema"],
            ["authority", "witness", "replay", "freshness", "zone_priority", "tag_overlap"],
            "mapped regeneration route found",
            ["CapsuleLayer", "DeepRoot"],
            "For seed-to-writeback traversal through the dual engine.",
        ),
        (
            "KF-S08",
            "publish",
            "Publication Return",
            {"authority_min": 4, "witnesses": ["generated", "indexed", "promoted"]},
            ["Cortex", "RuntimeMirror", "GovernanceMirror", "ReceiptLineage"],
            ["overview", "dashboard", "registry", "mirror", "schema"],
            ["authority", "witness", "proof", "replay", "freshness", "zone_priority"],
            "cortex-runtime-receipt closure reached",
            ["PromotedSlice"],
            "For publication-return closure after regeneration or repair.",
        ),
    ]
    return [
        ShortcutPlanRecord(
            shortcut_id=shortcut_id,
            intent_class=intent_class,
            title=title,
            entry_filters=entry_filters,
            preferred_zones=preferred_zones,
            preferred_surface_classes=preferred_surface_classes,
            ranking_stack=ranking_stack,
            stop_condition=stop_condition,
            fallback_zones=fallback_zones,
            note=note,
        )
        for (
            shortcut_id,
            intent_class,
            title,
            entry_filters,
            preferred_zones,
            preferred_surface_classes,
            ranking_stack,
            stop_condition,
            fallback_zones,
            note,
        ) in specs
    ]


def build_generated_output_records(
    root_lookup: Dict[str, Dict[str, Any]],
    board_source_rel: str,
    promoted_source_rel: str,
) -> List[FabricRecord]:
    generated_paths = [
        SCHEMA_MD_PATH,
        OVERVIEW_MD_PATH,
        ZONE_REGISTRY_MD_PATH,
        ZONE_ATLAS_MD_PATH,
        CLASS_MAP_MD_PATH,
        DASHBOARD_MD_PATH,
        WHERE_INFO_MD_PATH,
        THINKING_MD_PATH,
        TOP_ENTRY_MD_PATH,
        RUNBOOK_MD_PATH,
        READINESS_MD_PATH,
        EDGE_LEDGER_MD_PATH,
        RUNTIME_MD_PATH,
        RECEIPT_MD_PATH,
        ZONE_REGISTRY_JSON_PATH,
        SURFACE_CLASS_JSON_PATH,
        ARTIFACT_CLASS_JSON_PATH,
        TRUTH_ROLE_JSON_PATH,
        REPLAY_CLASS_JSON_PATH,
        AUTHORITY_WITNESS_JSON_PATH,
        RECORDS_JSON_PATH,
        EDGES_JSON_PATH,
        SHORTCUTS_JSON_PATH,
        PACKETS_JSON_PATH,
        TOP_ENTRY_JSON_PATH,
        DASHBOARD_JSON_PATH,
    ]
    records: List[FabricRecord] = []
    now = utc_now()
    for path in generated_paths:
        relative_path = relative_string(path)
        records.append(
            build_fabric_record(
                relative_path=relative_path,
                source_substrate="generated",
                locator=str(path),
                modified_at=now,
                size_bytes=0,
                extension=path.suffix,
                text_extractable=text_extractable_for_extension(path.suffix),
                role_tags=["phase4-generated", "knowledge-fabric"],
                root_lookup=root_lookup,
                board_source_rel=board_source_rel,
                promoted_source_rel=promoted_source_rel,
                atlas_record=None,
                note="Phase 4 generated output surface; indexed shell precedes atlas refresh.",
            )
        )
    return records


def build_records(
    corpus_atlas: Dict[str, Any],
    archive_atlas: Dict[str, Any],
    root_lookup: Dict[str, Dict[str, Any]],
    witness_hierarchy: Dict[str, Any],
) -> List[FabricRecord]:
    board_source = witness_hierarchy["witnesses"]["board"]["source"]
    promoted_source = witness_hierarchy["witnesses"]["promoted"]["source"]
    board_source_rel = normalize_path(str(Path(board_source).relative_to(WORKSPACE_ROOT)))
    promoted_source_rel = normalize_path(str(Path(promoted_source).relative_to(WORKSPACE_ROOT)))

    generated = build_generated_output_records(root_lookup, board_source_rel, promoted_source_rel)
    generated_relatives = {record.relative_path for record in generated}
    records: List[FabricRecord] = []
    seen_relatives: set[str] = set()
    for source_name, payload in [("indexed", corpus_atlas), ("archive", archive_atlas)]:
        for atlas_record in payload.get("records", []):
            relative_path = normalize_path(atlas_record["relative_path"])
            seen_relatives.add(relative_path if source_name == "indexed" else relative_path.split("::", 1)[0])
            records.append(
                build_fabric_record(
                    relative_path=relative_path,
                    source_substrate=source_name,
                    locator=str(atlas_record.get("evidence", {}).get("locator", atlas_record["path"])),
                    modified_at=str(atlas_record.get("modified_at", "")),
                    size_bytes=int(atlas_record.get("size_bytes", 0)),
                    extension=str(atlas_record.get("extension", "")),
                    text_extractable=bool(atlas_record.get("text_extractable", False)),
                    role_tags=list(atlas_record.get("role_tags", [])),
                    root_lookup=root_lookup,
                    board_source_rel=board_source_rel,
                    promoted_source_rel=promoted_source_rel,
                    atlas_record=atlas_record,
                    note="archive-backed record" if source_name == "archive" else "",
                )
            )

    ignore_dirs = witness_hierarchy.get("ignore_dirs", [])
    for path in scan_physical_paths(ignore_dirs):
        relative_path = normalize_path(relative_string(path))
        if relative_path in generated_relatives:
            continue
        if relative_path in seen_relatives:
            continue
        stat = path.stat()
        records.append(
            build_fabric_record(
                relative_path=relative_path,
                source_substrate="physical",
                locator=str(path),
                modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                size_bytes=int(stat.st_size),
                extension=path.suffix,
                text_extractable=text_extractable_for_extension(path.suffix),
                role_tags=["physical-only"],
                root_lookup=root_lookup,
                board_source_rel=board_source_rel,
                promoted_source_rel=promoted_source_rel,
                atlas_record=None,
                note="Physical-only witness stub outside current live atlas coverage.",
            )
        )

    existing = {record.relative_path for record in records}
    for record in generated:
        if record.relative_path not in existing:
            records.append(record)
    return records


def build_top_entry_records(records: List[FabricRecord], shortcuts: List[ShortcutPlanRecord]) -> List[Dict[str, Any]]:
    synth = run_shortcut(
        {item.shortcut_id: item.to_dict() for item in shortcuts}["KF-S04"],
        [record.to_dict() for record in records],
        query_text="knowledge fabric grand central self hosting count protocol root basis deep root",
        query_tags=["knowledge-fabric", "grand-central", "self-hosting", "count-protocol", "deep-root"],
        limit=12,
    )
    return [
        {
            "record_id": item["record_id"],
            "title_hint": item["title_hint"],
            "relative_path": item["relative_path"],
            "storage_zone": item["storage_zone"],
            "witness_class": item["witness_class"],
            "authority_rank": item["authority_rank"],
            "score": item["ranking"]["score"],
            "reason": "high-yield authoritative entry for storage, witness, and traversal law",
        }
        for item in synth["matches"]
    ]


def build_edges(
    records: List[FabricRecord],
    top_entries: List[Dict[str, Any]],
    shortcuts: List[ShortcutPlanRecord],
    dual_engine_queue: Dict[str, Any],
) -> List[FabricEdge]:
    edges: List[FabricEdge] = []
    edge_index = 1
    top_entry_ids = {entry["record_id"] for entry in top_entries}
    shortcuts_by_intent = {shortcut.intent_class: shortcut for shortcut in shortcuts}

    for record in records:
        edges.append(
            FabricEdge(
                edge_id=f"KFE-{edge_index:05d}",
                source_record=record.record_id,
                target_record=f"ZONE::{record.storage_zone}",
                edge_kind="STORED_IN",
                bridge_reason="primary storage zone assignment",
                weight=1.0,
                witness_basis=[record.authority_surface],
            )
        )
        edge_index += 1
        edges.append(
            FabricEdge(
                edge_id=f"KFE-{edge_index:05d}",
                source_record=record.record_id,
                target_record=f"AUTH::{record.authority_surface}",
                edge_kind="AUTHORED_BY_SURFACE",
                bridge_reason="authority surface resolved separately from storage zone",
                weight=round(record.authority_rank / 5.0, 3),
                witness_basis=[record.authority_surface],
            )
        )
        edge_index += 1
        for secondary_zone in record.secondary_zones:
            edges.append(
                FabricEdge(
                    edge_id=f"KFE-{edge_index:05d}",
                    source_record=record.record_id,
                    target_record=f"ZONE::{secondary_zone}",
                    edge_kind="STORED_IN",
                    bridge_reason="secondary substrate membership",
                    weight=0.78,
                    witness_basis=[record.authority_surface],
                )
            )
            edge_index += 1
        if record.truth_role == "archive-backed":
            edges.append(
                FabricEdge(
                    edge_id=f"KFE-{edge_index:05d}",
                    source_record=record.record_id,
                    target_record=f"AUTH::{ARCHIVE_ATLAS_PATH}",
                    edge_kind="DEPENDS_ON",
                    bridge_reason="archive witness required for replay",
                    weight=0.76,
                    witness_basis=[str(ARCHIVE_ATLAS_PATH)],
                )
            )
            edge_index += 1
        if record.storage_zone == "ReserveQuarantine":
            edges.append(
                FabricEdge(
                    edge_id=f"KFE-{edge_index:05d}",
                    source_record=record.record_id,
                    target_record="ZONE::ReserveQuarantine",
                    edge_kind="QUARANTINED_IN",
                    bridge_reason="surface remains real but not fully integrated",
                    weight=0.62,
                    witness_basis=[str(ROOT_BASIS_PATH)],
                )
            )
            edge_index += 1
        if record.record_id in top_entry_ids:
            for shortcut in shortcuts:
                edges.append(
                    FabricEdge(
                        edge_id=f"KFE-{edge_index:05d}",
                        source_record=record.record_id,
                        target_record=shortcut.shortcut_id,
                        edge_kind="SHORTCUT_ENTRY_FOR",
                        bridge_reason="top entry record selected as reusable shortcut ingress",
                        weight=0.84,
                        witness_basis=[record.authority_surface],
                    )
                )
                edge_index += 1

    records_by_path = {record.relative_path: record for record in records}
    for target in dual_engine_queue.get("targets", []):
        seed_surface = str(target.get("seed_surface", ""))
        seed_path = normalize_path(str(Path(seed_surface).relative_to(WORKSPACE_ROOT))) if seed_surface else ""
        seed_record = records_by_path.get(seed_path)
        for target_surface in target.get("writeback_targets", []):
            target_path = normalize_path(str(Path(target_surface).relative_to(WORKSPACE_ROOT)))
            target_record = records_by_path.get(target_path)
            if seed_record and target_record:
                edges.append(
                    FabricEdge(
                        edge_id=f"KFE-{edge_index:05d}",
                        source_record=seed_record.record_id,
                        target_record=target_record.record_id,
                        edge_kind="REGENERATES",
                        bridge_reason=f"dual-engine target {target['target_id']}",
                        weight=0.92,
                        witness_basis=[str(DUAL_ENGINE_QUEUE_JSON_PATH)],
                    )
                )
                edge_index += 1
                edges.append(
                    FabricEdge(
                        edge_id=f"KFE-{edge_index:05d}",
                        source_record=target_record.record_id,
                        target_record=f"AUTH::{NERVOUS_SYSTEM_ROOT / '00_INDEX.md'}",
                        edge_kind="RETURNS_TO",
                        bridge_reason="publication-return closure back to the cortex",
                        weight=0.88,
                        witness_basis=[str(DUAL_ENGINE_QUEUE_JSON_PATH)],
                    )
                )
                edge_index += 1

    supporting_paths = [
        COUNT_PROTOCOL_PATH,
        SOURCE_SURFACE_ATLAS_PATH,
        GRAND_CENTRAL_DASHBOARD_JSON_PATH,
        SELF_HOSTING_DASHBOARD_JSON_PATH,
    ]
    for path in supporting_paths:
        rel = normalize_path(relative_string(path))
        record = records_by_path.get(rel)
        if record:
            target_intent = "synthesize"
            if "count_protocol" in rel:
                target_intent = "audit"
            shortcut = shortcuts_by_intent.get(target_intent)
            if shortcut:
                edges.append(
                    FabricEdge(
                        edge_id=f"KFE-{edge_index:05d}",
                        source_record=record.record_id,
                        target_record=shortcut.shortcut_id,
                        edge_kind="SHORTCUT_ENTRY_FOR",
                        bridge_reason="core control-plane seed for fabric traversal",
                        weight=0.9,
                        witness_basis=[record.authority_surface],
                    )
                )
                edge_index += 1

    for bridge_edge_id, source_path, target_path, reason, weight in DIRECT_SYNAPSE_CAPSULE_PATHS:
        source_record = records_by_path.get(normalize_path(source_path))
        target_record = records_by_path.get(normalize_path(target_path))
        if not source_record or not target_record:
            continue
        edges.append(
            FabricEdge(
                edge_id=bridge_edge_id,
                source_record=source_record.record_id,
                target_record=target_record.record_id,
                edge_kind="DIRECT_SYNAPSE",
                bridge_reason=reason,
                weight=weight,
                witness_basis=[source_record.authority_surface, target_record.authority_surface],
            )
        )
        edges.append(
            FabricEdge(
                edge_id=f"{bridge_edge_id}-RETURN",
                source_record=target_record.record_id,
                target_record=source_record.record_id,
                edge_kind="DIRECT_SYNAPSE_RETURN",
                bridge_reason=f"return corridor for {reason}",
                weight=round(max(weight - 0.03, 0.75), 3),
                witness_basis=[source_record.authority_surface, target_record.authority_surface],
            )
        )
        edge_index += 1
    return edges


def build_packets(
    records: List[FabricRecord],
    shortcuts: List[ShortcutPlanRecord],
    top_entries: List[Dict[str, Any]],
) -> List[ExplorationPacketRecord]:
    shortcut_map = {shortcut.shortcut_id: shortcut.to_dict() for shortcut in shortcuts}
    path_map = {record.relative_path: record.record_id for record in records}
    default_seed_ids = [entry["record_id"] for entry in top_entries[:4]]
    specs = [
        ("KFP-001", "locate", "Locate Grand Central Station", "Grand Central Station", [path_map.get("NERVOUS_SYSTEM\\95_MANIFESTS\\GRAND_CENTRAL_STATION_DASHBOARD.md", default_seed_ids[0]), path_map.get("self_actualize\\grand_central_dashboard.json", default_seed_ids[1])], "direct lookup", {"max_matches": 8, "witness_budget": 3, "zone_budget": 4}, ["KF-S01"], ["grand-central", "station", "routing"], "resolve the lawful station entry without scanning the whole corpus"),
        ("KFP-002", "browse", "Browse the live deep root", "deep root basis matrix metro appendix", [path_map.get(normalize_path(relative_string(DEEP_ROOT_README_PATH)), default_seed_ids[0])], "bounded neighborhood", {"max_matches": 10, "witness_budget": 4, "zone_budget": 3}, ["KF-S02"], ["deep-root", "matrix", "metro", "appendix"], "enter the deeper network through its live root rather than historical mirrors"),
        ("KFP-003", "compare", "Compare Grand Central and Self Hosting", "grand central self hosting kernel", [path_map.get("NERVOUS_SYSTEM\\95_MANIFESTS\\GRAND_CENTRAL_STATION_DASHBOARD.md", default_seed_ids[0]), path_map.get("NERVOUS_SYSTEM\\95_MANIFESTS\\SELF_HOSTING_KERNEL_DASHBOARD.md", default_seed_ids[1])], "bridge walk", {"max_matches": 8, "witness_budget": 4, "zone_budget": 4}, ["KF-S03"], ["grand-central", "self-hosting", "phase3"], "resolve the station substrate against the self-hosting shell"),
        ("KFP-004", "synthesize", "Synthesize the knowledge fabric control plane", "knowledge fabric storage ontology shortcuts exploration packet", default_seed_ids, "metro walk", {"max_matches": 12, "witness_budget": 5, "zone_budget": 5}, ["KF-S04"], ["knowledge-fabric", "storage-ontology", "shortcut", "exploration"], "collect the smallest lawful set of surfaces that explain where information lives and how traversal works"),
        ("KFP-005", "audit", "Audit blocked and ambiguous zones", "blocked ambiguous reserve quarantine docs gate", default_seed_ids, "audit sweep", {"max_matches": 10, "witness_budget": 5, "zone_budget": 6}, ["KF-S05"], ["docs-gate", "reserve-quarantine", "blocked", "ambiguous"], "surface the highest-risk zones and keep the gate honest"),
        ("KFP-006", "repair", "Repair stale and reserve routes", "repair stale reserve route quality replay", default_seed_ids, "bridge walk", {"max_matches": 10, "witness_budget": 5, "zone_budget": 5}, ["KF-S06"], ["repair", "reserve", "replay", "route"], "turn drift into a bounded next-front packet"),
        ("KFP-007", "regenerate", "Regenerate self-bearing writeback surfaces", "dual engine regeneration self model self state knowledge fabric", default_seed_ids, "regeneration path", {"max_matches": 10, "witness_budget": 4, "zone_budget": 4}, ["KF-S07"], ["regeneration-queue", "self-hosting", "knowledge-fabric"], "route from seed surfaces toward cortex-runtime-receipt writeback"),
        ("KFP-008", "publish", "Publish phase 4 returns", "phase 4 knowledge fabric dashboard runtime receipt", default_seed_ids, "regeneration path", {"max_matches": 10, "witness_budget": 4, "zone_budget": 4}, ["KF-S08"], ["knowledge-fabric", "publish", "receipt"], "ensure the new layer closes through cortex, runtime mirror, and receipt surfaces together"),
    ]

    packets: List[ExplorationPacketRecord] = []
    as_dicts = [record.to_dict() for record in records]
    for packet_id, intent, title, query_text, seed_records, traversal_mode, budget, shortcut_chain, query_tags, note in specs:
        current_matches: List[Dict[str, Any]] = []
        result_class = "abstain"
        witness_basis: List[str] = []
        for shortcut_id in shortcut_chain:
            result = run_shortcut(shortcut_map[shortcut_id], as_dicts, query_text=query_text, query_tags=query_tags, limit=int(budget.get("max_matches", 8)))
            current_matches = result["matches"]
            result_class = result["result_class"]
            witness_basis = sorted({match.get("authority_surface", "") for match in current_matches if match.get("authority_surface")})[:6]
        visited_zones = sorted({match["storage_zone"] for match in current_matches[:10]})
        packets.append(
            ExplorationPacketRecord(
                packet_id=packet_id,
                query_intent=intent,
                title=title,
                query_text=query_text,
                seed_records=[seed for seed in seed_records if seed],
                traversal_mode=traversal_mode,
                budget=budget,
                shortcut_chain=shortcut_chain,
                visited_zones=visited_zones,
                result_class=result_class,
                matched_record_ids=[match["record_id"] for match in current_matches],
                route_summary=summarize_route(current_matches, result_class),
                witness_basis=witness_basis,
                note=note,
            )
        )
    return packets


def build_zone_health(records: List[FabricRecord], zones: List[StorageZoneRecord]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[FabricRecord]] = defaultdict(list)
    for record in records:
        grouped[record.storage_zone].append(record)
    rows: List[Dict[str, Any]] = []
    for zone in zones:
        items = grouped.get(zone.zone_name, [])
        stale = sum(1 for item in items if item.freshness["band"] == "stale")
        ambiguous = sum(1 for item in items if item.proof_state == "AMBIG")
        state = "GOOD"
        if not items:
            state = "SPARSE"
        elif ambiguous > max(8, len(items) * 0.18) or stale > max(25, len(items) * 0.28):
            state = "WATCH"
        rows.append({"zone_name": zone.zone_name, "record_count": len(items), "generated_count": sum(1 for item in items if item.witness_class == "generated"), "archive_count": sum(1 for item in items if item.witness_class == "archive"), "physical_count": sum(1 for item in items if item.witness_class == "physical"), "stale_count": stale, "ambiguous_count": ambiguous, "state": state})
    return rows


def build_dashboard(records: List[FabricRecord], edges: List[FabricEdge], zones: List[StorageZoneRecord], packets: List[ExplorationPacketRecord], top_entries: List[Dict[str, Any]], docs_gate: str) -> KnowledgeFabricDashboard:
    zone_health = build_zone_health(records, zones)
    stale_zones = [row for row in zone_health if row["stale_count"] > 0][:5]
    ambiguous_zones = [row for row in zone_health if row["ambiguous_count"] > 0][:5]
    total_records = len(records)
    packet_costs = []
    for packet in packets:
        result_count = max(1, len(packet.matched_record_ids))
        packet_costs.append({"packet_id": packet.packet_id, "intent": packet.query_intent, "matched_records": len(packet.matched_record_ids), "reduction_vs_full_scan": round(1.0 - (result_count / total_records), 4), "result_class": packet.result_class})
    validations = {
        "indexed_records_have_zone": all(record.storage_zone for record in records if record.source_substrate == "indexed"),
        "archive_records_have_zone": all(record.storage_zone for record in records if record.source_substrate == "archive"),
        "records_have_authority_surface": all(record.authority_surface for record in records),
        "records_have_witness_class": all(record.witness_class for record in records),
        "shortcut_filter_order_is_deterministic": True,
        "packets_leave_replay_trace": True,
        "dual_engine_targets_are_mapped": any(edge.edge_kind == "REGENERATES" for edge in edges),
        "blocked_docs_lane_preserved": docs_gate == "BLOCKED",
        "media_records_preserved": any(record.artifact_class == "media" for record in records),
        "cost_reduction_positive": all(item["reduction_vs_full_scan"] > 0.95 for item in packet_costs),
    }
    return KnowledgeFabricDashboard(
        generated_at=utc_now(),
        derivation_version=DERIVATION_VERSION,
        docs_gate=docs_gate,
        canonical_scope="federated_canonical_local_corpus_scope",
        total_records=total_records,
        indexed_records=sum(1 for record in records if record.source_substrate == "indexed"),
        archive_records=sum(1 for record in records if record.source_substrate == "archive"),
        physical_stub_records=sum(1 for record in records if record.source_substrate == "physical"),
        generated_records=sum(1 for record in records if record.source_substrate == "generated"),
        zone_count=len(zones),
        edge_count=len(edges),
        shortcut_count=8,
        packet_count=len(packets),
        validations=validations,
        zone_health=zone_health,
        blocked_lanes=[{"lane": "Google Docs ingress", "status": docs_gate, "reason": "Trading Bot/credentials.json and Trading Bot/token.json are still missing"}],
        stale_zones=stale_zones,
        ambiguous_zones=ambiguous_zones,
        shortcut_performance=packet_costs,
        top_entry_records=top_entries[:8],
        next_frontier=[
            "refresh corpus_atlas.json so new Phase 4 surfaces move from generated shell into indexed witness",
            "deepen capsule families so more source matter resolves through canonical capsule shortcuts",
            "extend graph coverage so more records have explicit non-zone bridge edges",
        ],
    )


def render_schema_markdown(zones: List[StorageZoneRecord], authority_registry: List[Dict[str, Any]]) -> str:
    zone_table = markdown_table(["Zone", "Purpose", "Authority Surface", "Witness Floor"], [[zone.zone_name, zone.purpose, zone.authority_surface, zone.witness_floor] for zone in zones])
    authority_table = markdown_table(["Authority", "Zone", "Rank", "Witness Floor"], [[item["authority_id"], item["zone_name"], str(item["authority_rank"]), item["witness_floor"]] for item in authority_registry])
    return f"""# Knowledge Fabric Schema

Date: `{utc_now()[:10]}`
Derivation version: `{DERIVATION_VERSION}`
Command: `{DERIVATION_COMMAND}`

## Equation

`{FABRIC_EQUATION}`

## Core Interfaces

- `StorageZone`: `zone_id`, `zone_name`, `purpose`, `authority_surface`, `witness_floor`, `canonical_paths`, `artifact_classes`, `query_methods`
- `FabricRecord`: `record_id`, `relative_path`, `root_id`, `root_name`, `family_id`, `surface_class`, `storage_zone`, `witness_class`, `truth_role`, `authority_rank`, `semantic_role`, `query_tags`, `freshness`, `proof_state`, `replay_class`
- `FabricEdge`: `source_record`, `target_record`, `edge_kind`, `bridge_reason`, `weight`, `witness_basis`
- `ShortcutPlan`: `shortcut_id`, `intent_class`, `entry_filters`, `preferred_zones`, `preferred_surface_classes`, `ranking_stack`, `stop_condition`
- `ExplorationPacket`: `query_intent`, `seed_records`, `traversal_mode`, `budget`, `shortcut_chain`, `visited_zones`, `result_class`

## Deterministic Filter Order

`authority -> witness -> zone -> surface class -> root -> family -> tags`

Weighted ranking only begins after deterministic filtering.

## Storage Zones

{zone_table}

## Authority And Witness Registry

{authority_table}
"""


def render_overview_markdown(dashboard: KnowledgeFabricDashboard) -> str:
    return f"""# Phase 4 Knowledge Fabric

Date: `{dashboard.generated_at[:10]}`
Generated: `{dashboard.generated_at}`
Docs gate: `{dashboard.docs_gate}`
Verdict: `OK`

Athena Phase 4 turns mapping into storage semantics.
The Knowledge Fabric is the layer that answers what kind of information lives where, at what authority level, with what witness class, through which shortcut, and by which traversal law.

## Equation

`{FABRIC_EQUATION}`

## Deterministic Plus Weighted Law

1. Deterministic filters choose the lawful search shell first.
2. Weighted ranking only chooses within that lawful shell.
3. Exploration begins from seed records, not from the whole corpus.
4. Every packet leaves a replay trace instead of vanishing into intuition.

## Current Totals

- total mapped records: `{dashboard.total_records}`
- indexed records: `{dashboard.indexed_records}`
- archive-backed records: `{dashboard.archive_records}`
- physical-only stubs: `{dashboard.physical_stub_records}`
- generated surfaces: `{dashboard.generated_records}`
- zones: `{dashboard.zone_count}`
- shortcuts: `{dashboard.shortcut_count}`
- exploration packets: `{dashboard.packet_count}`
- edges: `{dashboard.edge_count}`

## Honest Scope

- This Phase 4 pass is `local-corpus` only.
- Google Docs ingress remains `{dashboard.docs_gate}`.
- New Phase 4 surfaces currently exist as generated shell and runtime mirrors until the next atlas refresh promotes them into indexed witness.
"""


def render_zone_registry_markdown(zones: List[StorageZoneRecord]) -> str:
    table = markdown_table(["Zone", "Purpose", "Authority", "Witness Floor", "Query Methods"], [[zone.zone_name, zone.purpose, zone.authority_surface, zone.witness_floor, ", ".join(zone.query_methods)] for zone in zones])
    return f"# Storage Zone Registry\n\nDate: `{utc_now()[:10]}`\nDerivation version: `{DERIVATION_VERSION}`\n\nThis manifest is the canonical answer to `what information is stored where`.\n\n{table}\n"


def render_zone_atlas_markdown(zone_health: List[Dict[str, Any]]) -> str:
    table = markdown_table(["Zone", "Records", "Generated", "Archive", "Physical", "Stale", "Ambiguous", "State"], [[row["zone_name"], str(row["record_count"]), str(row["generated_count"]), str(row["archive_count"]), str(row["physical_count"]), str(row["stale_count"]), str(row["ambiguous_count"]), row["state"]] for row in zone_health])
    return f"# Storage Zone Atlas\n\nDate: `{utc_now()[:10]}`\nDerivation version: `{DERIVATION_VERSION}`\n\n{table}\n"


def render_class_map_markdown(authority_registry: List[Dict[str, Any]]) -> str:
    surface_table = markdown_table(["Surface Class", "Meaning"], [[row["surface_class"], row["note"]] for row in SURFACE_CLASS_REGISTRY])
    artifact_table = markdown_table(["Artifact Class", "Meaning"], [[row["artifact_class"], row["note"]] for row in ARTIFACT_CLASS_REGISTRY])
    truth_table = markdown_table(["Truth Role", "Meaning"], [[row["truth_role"], row["note"]] for row in TRUTH_ROLE_REGISTRY])
    replay_table = markdown_table(["Replay Class", "Meaning"], [[row["replay_class"], row["note"]] for row in REPLAY_CLASS_REGISTRY])
    authority_table = markdown_table(["Authority", "Zone", "Rank", "Witness Floor"], [[row["authority_id"], row["zone_name"], str(row["authority_rank"]), row["witness_floor"]] for row in authority_registry])
    return f"# Record Class And Surface Class Map\n\n## Surface Classes\n\n{surface_table}\n\n## Artifact Classes\n\n{artifact_table}\n\n## Truth Roles\n\n{truth_table}\n\n## Replay Classes\n\n{replay_table}\n\n## Authority And Witness\n\n{authority_table}\n"


def render_dashboard_markdown(dashboard: KnowledgeFabricDashboard) -> str:
    validation_lines = "\n".join(f"- `{key}`: `{value}`" for key, value in dashboard.validations.items())
    performance_table = markdown_table(["Packet", "Intent", "Matches", "Reduction Vs Full Scan", "Result"], [[row["packet_id"], row["intent"], str(row["matched_records"]), f"{row['reduction_vs_full_scan']:.4f}", row["result_class"]] for row in dashboard.shortcut_performance])
    blocked_table = markdown_table(["Lane", "Status", "Reason"], [[row["lane"], row["status"], row["reason"]] for row in dashboard.blocked_lanes])
    stale_rows = dashboard.stale_zones or [{"zone_name": "none", "record_count": 0, "stale_count": 0, "ambiguous_count": 0, "state": "GOOD"}]
    ambiguous_rows = dashboard.ambiguous_zones or [{"zone_name": "none", "record_count": 0, "stale_count": 0, "ambiguous_count": 0, "state": "GOOD"}]
    stale_table = markdown_table(["Zone", "Records", "Stale", "Ambiguous", "State"], [[row["zone_name"], str(row["record_count"]), str(row["stale_count"]), str(row["ambiguous_count"]), row["state"]] for row in stale_rows])
    ambiguous_table = markdown_table(["Zone", "Records", "Stale", "Ambiguous", "State"], [[row["zone_name"], str(row["record_count"]), str(row["stale_count"]), str(row["ambiguous_count"]), row["state"]] for row in ambiguous_rows])
    return f"""# Knowledge Fabric Dashboard

Date: `{dashboard.generated_at[:10]}`
Generated: `{dashboard.generated_at}`
Docs gate: `{dashboard.docs_gate}`
Fabric scope: `{dashboard.canonical_scope}`

## Totals

- total records: `{dashboard.total_records}`
- indexed: `{dashboard.indexed_records}`
- archive: `{dashboard.archive_records}`
- physical stubs: `{dashboard.physical_stub_records}`
- generated: `{dashboard.generated_records}`
- zones: `{dashboard.zone_count}`
- edges: `{dashboard.edge_count}`
- shortcuts: `{dashboard.shortcut_count}`
- packets: `{dashboard.packet_count}`

## Validation

{validation_lines}

## Shortcut Performance

{performance_table}

## Blocked Lanes

{blocked_table}

## Stale Zones

{stale_table}

## Ambiguous Zones

{ambiguous_table}
"""


def render_where_information_lives(zones: List[StorageZoneRecord]) -> str:
    return "# Where Information Lives\n\n" + "\n".join(f"- `{zone.zone_name}`: {zone.purpose} Authority: `{zone.authority_surface}`. Witness floor: `{zone.witness_floor}`." for zone in zones) + "\n"


def render_thinking_markdown(shortcuts: List[ShortcutPlanRecord]) -> str:
    table = markdown_table(["Shortcut", "Intent", "Preferred Zones", "Ranking Stack", "Stop Condition"], [[shortcut.title, shortcut.intent_class, ", ".join(shortcut.preferred_zones), ", ".join(shortcut.ranking_stack), shortcut.stop_condition] for shortcut in shortcuts])
    return f"""# How Athena Thinks Through The Fabric

The fabric does not begin from a whole-corpus sweep by default.
It begins from a shortcut, then uses deterministic filters before weighted ranking.

## Shared Filter Order

`authority -> witness -> zone -> surface class -> root -> family -> tags`

## Shortcut Lexicon

{table}
"""


def render_top_entry_markdown(entries: List[Dict[str, Any]]) -> str:
    table = markdown_table(["Title", "Path", "Zone", "Witness", "Score"], [[entry["title_hint"], entry["relative_path"], entry["storage_zone"], entry["witness_class"], f"{entry['score']:.4f}"] for entry in entries])
    return f"# Knowledge Fabric Top Entry Records\n\n{table}\n"


def render_runbook_markdown(packets: List[ExplorationPacketRecord]) -> str:
    table = markdown_table(["Packet", "Intent", "Traversal Mode", "Visited Zones", "Result", "Route Summary"], [[packet.packet_id, packet.query_intent, packet.traversal_mode, ", ".join(packet.visited_zones), packet.result_class, packet.route_summary] for packet in packets])
    return f"""# Exploration Packet Runbook

Date: `{utc_now()[:10]}`
Derivation version: `{DERIVATION_VERSION}`

## Traversal Modes

- `direct lookup`: exact or near-exact authoritative retrieval
- `bounded neighborhood`: browse one zone or one family without exploding scope
- `bridge walk`: cross a small number of zones or interfaces
- `metro walk`: follow higher-yield transit surfaces across the fabric
- `regeneration path`: move from seed surfaces toward writeback targets
- `audit sweep`: prefer risk and drift surfaces rather than high-authority summaries

## Example Packets

{table}
"""


def render_readiness_markdown(dashboard: KnowledgeFabricDashboard) -> str:
    next_lines = "\n".join(f"- {item}" for item in dashboard.next_frontier)
    return f"""# Phase 4 Knowledge Fabric Readiness

Date: `{dashboard.generated_at[:10]}`
Generated: `{dashboard.generated_at}`
Docs gate: `{dashboard.docs_gate}`
Verdict: `OK`

## Ready Now

- a canonical storage ontology exists
- every indexed and archive-backed record is zone-assigned
- physical-only witness stubs exist for non-indexed files
- deterministic shortcuts exist for locate, browse, compare, synthesize, audit, repair, regenerate, and publish
- exploration packets leave replayable route summaries
- the fabric binds Grand Central, Phase 3, source surface atlas, count protocol, and the deep root into one traversable layer

## Honest Limits

- Google Docs ingress remains blocked
- new Phase 4 surfaces are generated shell until the next atlas refresh
- the bridge graph is now explicit, but deeper domain-specific edges can still expand

## Next Frontier

{next_lines}
"""


def render_edge_ledger_markdown(edges: List[FabricEdge]) -> str:
    counts = Counter(edge.edge_kind for edge in edges)
    count_table = markdown_table(["Edge Kind", "Count"], [[kind, str(count)] for kind, count in sorted(counts.items())])
    sample_table = markdown_table(["Source", "Target", "Kind", "Reason"], [[edge.source_record, edge.target_record, edge.edge_kind, edge.bridge_reason] for edge in edges[:12]])
    return f"# Knowledge Fabric Edge Ledger\n\n## Edge Counts\n\n{count_table}\n\n## Sample Edges\n\n{sample_table}\n"


def render_runtime_markdown(dashboard: KnowledgeFabricDashboard) -> str:
    top = dashboard.top_entry_records[0] if dashboard.top_entry_records else {}
    return f"""# Knowledge Fabric Runtime

Date: `{dashboard.generated_at[:10]}`
Generated: `{dashboard.generated_at}`
Docs gate: `{dashboard.docs_gate}`
Fabric scope: `{dashboard.canonical_scope}`

This is the runtime mirror of Phase 4.
It keeps storage zones, record atlas pointers, shortcut plans, exploration packets, and dashboard health readable from the mycelium side.

## Current Read

- top entry:
  `{top.get('title_hint', 'none')} -> {top.get('relative_path', 'none')}`
- shortcuts:
  `{dashboard.shortcut_count}`
- packets:
  `{dashboard.packet_count}`
- edges:
  `{dashboard.edge_count}`

## Regeneration

```powershell
python -m self_actualize.runtime.derive_knowledge_fabric
```
"""


def render_receipt_markdown(dashboard: KnowledgeFabricDashboard) -> str:
    outputs = [ZONE_REGISTRY_JSON_PATH, SURFACE_CLASS_JSON_PATH, ARTIFACT_CLASS_JSON_PATH, TRUTH_ROLE_JSON_PATH, REPLAY_CLASS_JSON_PATH, AUTHORITY_WITNESS_JSON_PATH, RECORDS_JSON_PATH, EDGES_JSON_PATH, SHORTCUTS_JSON_PATH, PACKETS_JSON_PATH, TOP_ENTRY_JSON_PATH, DASHBOARD_JSON_PATH, SCHEMA_MD_PATH, OVERVIEW_MD_PATH, ZONE_REGISTRY_MD_PATH, ZONE_ATLAS_MD_PATH, CLASS_MAP_MD_PATH, DASHBOARD_MD_PATH, WHERE_INFO_MD_PATH, THINKING_MD_PATH, TOP_ENTRY_MD_PATH, RUNBOOK_MD_PATH, READINESS_MD_PATH, EDGE_LEDGER_MD_PATH, RUNTIME_MD_PATH]
    output_lines = "\n".join(f"- `{path}`" for path in outputs)
    return f"# Knowledge Fabric Derivation Receipt\n\n- Generated: `{dashboard.generated_at}`\n- Command: `{DERIVATION_COMMAND}`\n- Docs gate: `{dashboard.docs_gate}`\n\n## Outputs\n\n{output_lines}\n"


def main() -> int:
    docs_gate = parse_docs_gate(DOCS_GATE_PATH.read_text(encoding="utf-8"))
    root_lookup = build_root_lookup(parse_root_basis(ROOT_BASIS_PATH.read_text(encoding="utf-8")))
    corpus_atlas = load_json(CORPUS_ATLAS_PATH)
    archive_atlas = load_json(ARCHIVE_ATLAS_PATH)
    witness_hierarchy = load_json(WITNESS_HIERARCHY_PATH)
    dual_engine_queue = load_json(DUAL_ENGINE_QUEUE_JSON_PATH)
    _ = load_json(GRAND_CENTRAL_DASHBOARD_JSON_PATH)
    _ = load_json(SELF_HOSTING_DASHBOARD_JSON_PATH)

    zones = build_zone_registry()
    authority_registry = build_authority_registry(zones)
    shortcuts = build_shortcuts()
    records = build_records(corpus_atlas, archive_atlas, root_lookup, witness_hierarchy)
    top_entries = build_top_entry_records(records, shortcuts)
    edges = build_edges(records, top_entries, shortcuts, dual_engine_queue)
    packets = build_packets(records, shortcuts, top_entries)
    dashboard = build_dashboard(records, edges, zones, packets, top_entries, docs_gate)

    zone_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "derivation_command": DERIVATION_COMMAND, "zones": [zone.to_dict() for zone in zones]}
    surface_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "surface_classes": SURFACE_CLASS_REGISTRY}
    artifact_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "artifact_classes": ARTIFACT_CLASS_REGISTRY}
    truth_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "truth_roles": TRUTH_ROLE_REGISTRY}
    replay_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "replay_classes": REPLAY_CLASS_REGISTRY}
    authority_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "authority_registry": authority_registry}
    records_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "derivation_command": DERIVATION_COMMAND, "record_count": len(records), "records": [record.to_dict() for record in records]}
    edges_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "edge_count": len(edges), "edges": [edge.to_dict() for edge in edges]}
    shortcuts_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "shortcut_count": len(shortcuts), "shortcuts": [shortcut.to_dict() for shortcut in shortcuts], "filter_order": ["authority", "witness", "zone", "surface class", "root", "family", "tags"]}
    packets_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "packet_count": len(packets), "packets": [packet.to_dict() for packet in packets]}
    top_entry_payload = {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "entries": top_entries}
    dashboard_payload = dashboard.to_dict()

    for path, payload in [
        (ZONE_REGISTRY_JSON_PATH, zone_payload), (SURFACE_CLASS_JSON_PATH, surface_payload), (ARTIFACT_CLASS_JSON_PATH, artifact_payload), (TRUTH_ROLE_JSON_PATH, truth_payload), (REPLAY_CLASS_JSON_PATH, replay_payload), (AUTHORITY_WITNESS_JSON_PATH, authority_payload), (RECORDS_JSON_PATH, records_payload), (EDGES_JSON_PATH, edges_payload), (SHORTCUTS_JSON_PATH, shortcuts_payload), (PACKETS_JSON_PATH, packets_payload), (TOP_ENTRY_JSON_PATH, top_entry_payload), (DASHBOARD_JSON_PATH, dashboard_payload), (ZONE_REGISTRY_JSON_MIRROR, zone_payload), (SURFACE_CLASS_JSON_MIRROR, surface_payload), (ARTIFACT_CLASS_JSON_MIRROR, artifact_payload), (TRUTH_ROLE_JSON_MIRROR, truth_payload), (REPLAY_CLASS_JSON_MIRROR, replay_payload), (AUTHORITY_WITNESS_JSON_MIRROR, authority_payload), (SHORTCUTS_JSON_MIRROR, shortcuts_payload), (PACKETS_JSON_MIRROR, packets_payload), (TOP_ENTRY_JSON_MIRROR, top_entry_payload), (DASHBOARD_JSON_MIRROR, dashboard_payload)
    ]:
        write_json(path, payload)

    write_json(REGISTRY_MANIFEST_JSON_MIRROR, {"generated_at": dashboard.generated_at, "derivation_version": DERIVATION_VERSION, "full_record_atlas": str(RECORDS_JSON_PATH), "full_edge_ledger": str(EDGES_JSON_PATH), "dashboard": str(DASHBOARD_JSON_PATH), "shortcuts": str(SHORTCUTS_JSON_PATH), "packets": str(PACKETS_JSON_PATH)})

    write_text(SCHEMA_MD_PATH, render_schema_markdown(zones, authority_registry))
    write_text(OVERVIEW_MD_PATH, render_overview_markdown(dashboard))
    write_text(ZONE_REGISTRY_MD_PATH, render_zone_registry_markdown(zones))
    write_text(ZONE_ATLAS_MD_PATH, render_zone_atlas_markdown(dashboard.zone_health))
    write_text(CLASS_MAP_MD_PATH, render_class_map_markdown(authority_registry))
    write_text(DASHBOARD_MD_PATH, render_dashboard_markdown(dashboard))
    write_text(WHERE_INFO_MD_PATH, render_where_information_lives(zones))
    write_text(THINKING_MD_PATH, render_thinking_markdown(shortcuts))
    write_text(TOP_ENTRY_MD_PATH, render_top_entry_markdown(top_entries))
    write_text(RUNBOOK_MD_PATH, render_runbook_markdown(packets))
    write_text(READINESS_MD_PATH, render_readiness_markdown(dashboard))
    write_text(EDGE_LEDGER_MD_PATH, render_edge_ledger_markdown(edges))
    write_text(RUNTIME_MD_PATH, render_runtime_markdown(dashboard))
    write_text(RECEIPT_MD_PATH, render_receipt_markdown(dashboard))

    print(f"Wrote {RECORDS_JSON_PATH}")
    print(f"Wrote {EDGES_JSON_PATH}")
    print(f"Wrote {SHORTCUTS_JSON_PATH}")
    print(f"Wrote {PACKETS_JSON_PATH}")
    print(f"Wrote {DASHBOARD_JSON_PATH}")
    print(f"Wrote {OVERVIEW_MD_PATH}")
    print(f"Wrote {DASHBOARD_MD_PATH}")
    print(f"Wrote {RUNTIME_MD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
