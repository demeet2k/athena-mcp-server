from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
FULL_INTEGRATION_ROOT = (
    WORKSPACE_ROOT
    / "DEEPER CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "07_FULL_PROJECT_INTEGRATION_256"
)
BOARD_ROOT = FULL_INTEGRATION_ROOT / "06_REALTIME_BOARD"
STATE_ROOT = BOARD_ROOT / "_state"
AGENT_ROOT = BOARD_ROOT / "01_AGENT_INBOXES"
THREAD_ROOT = BOARD_ROOT / "02_ACTIVE_THREADS"
CLAIM_ROOT = BOARD_ROOT / "03_CLAIMS" / "claims"
STATUS_ROOT = BOARD_ROOT / "00_STATUS"
CHANGE_ROOT = BOARD_ROOT / "04_CHANGE_FEED"
SYNTHESIS_ROOT = BOARD_ROOT / "05_SYNTHESIS"
PROTOCOL_ROOT = BOARD_ROOT / "06_PROTOCOLS"
TENSOR_ROOT = BOARD_ROOT / "07_TENSOR"
SWARM_ROOT = BOARD_ROOT / "08_SWARM_RUNTIME"
GANGLIA_ROOT = SWARM_ROOT / "ganglia"
RAILS_ROOT = SWARM_ROOT / "rails"
NEURON_ROOT = SWARM_ROOT / "neurons"
POD_ROOT = SWARM_ROOT / "pods"
WAVE_ROOT = SWARM_ROOT / "waves"
MANIFEST_ROOT = SWARM_ROOT / "manifests"
CORTEX_ROOT = SWARM_ROOT / "cortex"
KERNEL_ROOT = SWARM_ROOT / "kernel"
ELEMENTAL_ROOT = SWARM_ROOT / "elementals"
ARCHETYPE_ROOT = SWARM_ROOT / "archetypes"
PANTHEON_ROOT = SWARM_ROOT / "pantheon"
CLUSTER_ROOT = SWARM_ROOT / "clusters"
COUNCIL_ROOT = SWARM_ROOT / "councils"
HYPERGRAPH_ROOT = SWARM_ROOT / "hypergraph"

LIVE_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = WORKSPACE_ROOT / "self_actualize" / "archive_atlas.json"
ARCHIVE_MANIFEST_PATH = WORKSPACE_ROOT / "self_actualize" / "archive_manifest.json"
LEGACY_RUNTIME_ROOT = FULL_INTEGRATION_ROOT.parent / "06_RUNTIME"
LEGACY_TENSOR_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "01_tensor_manifest.json"
LEGACY_SWARM_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "02_swarm_manifest.json"
LEGACY_HYPERGRAPH_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "03_hypergraph_manifest.json"
LEGACY_NODE_TENSOR_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "04_node_tensor_manifest.json"
LEGACY_NERVE_EDGE_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "05_nerve_edge_manifest.json"
LEGACY_CIVILIZATION_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "07_civilization_manifest.json"
LEGACY_FRONTIER_MANIFEST_PATH = LEGACY_RUNTIME_ROOT / "09_frontier_manifest.json"
QUEUE_PATH = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "nervous_system"
    / "06_active_queue.md"
)
LEGACY_CLAIMS_PATH = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "registry"
    / "01_tandem_frontier_claims.md"
)
DOCS_GATE_RECEIPT_PATH = WORKSPACE_ROOT / "self_actualize" / "live_docs_gate_status.md"
TRADING_BOT_ROOT = WORKSPACE_ROOT / "Trading Bot"

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
SKIP_FOR_DUPES = {"readme.md", "index.md", "__init__.py", "requirements.txt"}
DOC_EXTS = {".docx", ".md", ".txt", ".pdf"}
OPEN_STATUSES = {"queued", "active", "blocked"}
REGION_ORDER = [
    "DEEPER CRYSTALIZATION",
    "self_actualize",
    "MATH",
    "Voynich",
    "Trading Bot",
    "ECOSYSTEM",
    "NERUAL NETWORK",
    "NERVOUS_SYSTEM",
    "FRESH",
    "Athenachka Collective Books",
]

REGION_PROFILES: dict[str, dict[str, Any]] = {
    "DEEPER CRYSTALIZATION": {
        "role": "deep integration compiler, chapter lattice, and active nervous-system scaffold",
        "edges": [
            "binds directly into self_actualize as the runtime writeback surface",
            "acts as the integration mirror for Voynich, MATH, and archive promotion",
        ],
        "risk": "rich synthesis without a live coordination loop becomes descriptive instead of operative",
    },
    "self_actualize": {
        "role": "thin-waist runtime, atlas contracts, and orchestration control plane",
        "edges": [
            "converts corpus state into typed packets and replay-safe decisions",
            "is the most natural place to host a shared board runtime",
        ],
        "risk": "runtime discipline stays narrower than the surrounding manuscript theory body",
    },
    "MATH": {
        "role": "formal reservoir, theorem inventory, and archive-heavy engine room",
        "edges": [
            "feeds archive-backed framework code into the atlas through ZIP promotion",
            "should compile downstream into code and chapter surfaces instead of remaining shelfware",
        ],
        "risk": "archive opacity hides the strongest implementation assets from everyday routing",
    },
    "Voynich": {
        "role": "densest live manuscript execution surface and proof that the corpus can self-compile",
        "edges": [
            "shares queue, manifests, and final-draft mechanics with the nervous-system layer",
            "provides the highest-volume live markdown body for testing routes and synthesis",
        ],
        "risk": "parallel folio work can duplicate effort if claims and thread ownership stay informal",
    },
    "Trading Bot": {
        "role": "external memory bridge and Google Docs access point",
        "edges": [
            "connects live Docs memory to the local atlas once OAuth is unlocked",
            "should become the external evidence relay for manuscript drafting fronts",
        ],
        "risk": "missing OAuth keeps the workspace bi-lobed and forces local-only recall",
    },
    "ECOSYSTEM": {
        "role": "governance, skill ecology, and operator protocol layer",
        "edges": [
            "names the skills, routing rules, and future frontier surfaces",
            "supplies the policy side of swarm behavior and reuse",
        ],
        "risk": "without a live board, governance knowledge stays advisory instead of executable",
    },
    "NERUAL NETWORK": {
        "role": "adaptive benchmark lab and experimental learning surface",
        "edges": [
            "can validate whether routing quality improves with better coordination",
            "should score evidence density, replay quality, and handoff quality, not only model output",
        ],
        "risk": "experimentation can drift away from manuscript and runtime truth if not fed back",
    },
    "FRESH": {
        "role": "intake and markdown mirror lane for docx-heavy sources",
        "edges": [
            "reduces dependence on one-off extraction passes",
            "bridges raw manuscripts into searchable working memory",
        ],
        "risk": "if mirrors lag behind docx drift, the board will coordinate against stale text",
    },
    "Athenachka Collective Books": {
        "role": "publication and outward-facing manuscript bundle surface",
        "edges": [
            "is the final packaging lane for material promoted out of the nervous system",
            "shows what is ready to leave the internal coordination layer",
        ],
        "risk": "published surfaces can detach from operating truth if promotion lacks receipts",
    },
}

RAIL_DESCRIPTIONS = {
    "Me": {
        "name": "Mercury",
        "role": "map logic, canon, normalization, and formal bridge law",
    },
    "Sa": {
        "name": "Salt",
        "role": "manuscript mass, durable memory, precursor foldback, and stable placement",
    },
    "Su": {
        "name": "Sulfur",
        "role": "pressure, execution, gateway forcing, and runtime action",
    },
}

FAMILY_TENSOR_DEFAULTS: dict[str, dict[str, str]] = {
    "Voynich": {
        "rail": "Sa",
        "face": "Water",
        "scale": "B12",
        "hub": "AppL",
        "regime": "stratified",
        "best_front": "folio-to-family metro contraction",
        "ganglion": "ganglia/GANGLION_voynich.md",
        "lineage": "W-A-E",
        "truth": "NEAR",
    },
    "MATH": {
        "rail": "Me",
        "face": "Air",
        "scale": "B12",
        "hub": "AppB",
        "regime": "classical",
        "best_front": "archive-backed framework surfacing",
        "ganglion": "ganglia/GANGLION_math.md",
        "lineage": "A-E-F",
        "truth": "AMBIG",
    },
    "Trading Bot": {
        "rail": "Su",
        "face": "Fire",
        "scale": "S8",
        "hub": "AppI",
        "regime": "restart-token",
        "best_front": "live Docs gate unlock and query manifests",
        "ganglion": "ganglia/GANGLION_trading_bot.md",
        "lineage": "F-A-W",
        "truth": "FAIL",
    },
    "DEEPER CRYSTALIZATION": {
        "rail": "Sa",
        "face": "Aether",
        "scale": "S8",
        "hub": "AppE",
        "regime": "stratified",
        "best_front": "precursor nervous-system foldback",
        "ganglion": "ganglia/GANGLION_deeper_crystalization.md",
        "lineage": "E-W-A",
        "truth": "NEAR",
    },
    "self_actualize": {
        "rail": "Su",
        "face": "Aether",
        "scale": "S8",
        "hub": "AppM",
        "regime": "classical",
        "best_front": "runtime and ledger control plane",
        "ganglion": "ganglia/GANGLION_self_actualize.md",
        "lineage": "F-A-E",
        "truth": "OK",
    },
    "ECOSYSTEM": {
        "rail": "Me",
        "face": "Air",
        "scale": "S8",
        "hub": "AppC",
        "regime": "classical",
        "best_front": "framework normalization and transport law",
        "ganglion": "ganglia/GANGLION_ecosystem.md",
        "lineage": "A-E-W",
        "truth": "OK",
    },
    "NERUAL NETWORK": {
        "rail": "Su",
        "face": "Fire",
        "scale": "G4",
        "hub": "AppF",
        "regime": "restart-token",
        "best_front": "executable bridge study",
        "ganglion": "ganglia/GANGLION_nerual_network.md",
        "lineage": "F-A-F",
        "truth": "AMBIG",
    },
    "Athenachka Collective Books": {
        "rail": "Sa",
        "face": "Earth",
        "scale": "G4",
        "hub": "AppA",
        "regime": "restart-token",
        "best_front": "family intake and placement",
        "ganglion": "ganglia/GANGLION_athenachka_collective_books.md",
        "lineage": "E-W-E",
        "truth": "NEAR",
    },
    "FRESH": {
        "rail": "Me",
        "face": "Void",
        "scale": "G4",
        "hub": "AppN",
        "regime": "restart-token",
        "best_front": "intake triage and placement",
        "ganglion": "ganglia/GANGLION_fresh.md",
        "lineage": "E-A-W",
        "truth": "AMBIG",
    },
    "NERVOUS_SYSTEM": {
        "rail": "Sa",
        "face": "Aether",
        "scale": "S8",
        "hub": "AppG",
        "regime": "stratified",
        "best_front": "system-level memory and routing foldback",
        "ganglion": "ganglia/GANGLION_nervous_system.md",
        "lineage": "W-A-F",
        "truth": "NEAR",
    },
    "I AM ATHENA": {
        "rail": "Sa",
        "face": "Water",
        "scale": "G4",
        "hub": "AppA",
        "regime": "restart-token",
        "best_front": "identity family intake and placement",
        "ganglion": "ganglia/GANGLION_i_am_athena.md",
        "lineage": "W-F-A",
        "truth": "NEAR",
    },
}

TRANSFER_HUBS = [
    ("Voynich", "self_actualize", "AppL", "folio routing into runtime control"),
    ("MATH", "ECOSYSTEM", "AppB", "framework law moving toward skill and governance form"),
    ("Trading Bot", "self_actualize", "AppI", "live Docs evidence entering the runtime waist"),
    ("DEEPER CRYSTALIZATION", "self_actualize", "AppE", "precursor nervous-system foldback into the current control plane"),
    ("NERUAL NETWORK", "self_actualize", "AppF", "benchmark and executable bridge exchange"),
]

KNOWN_FAMILIES = set(FAMILY_TENSOR_DEFAULTS) | set(REGION_ORDER) | {
    "QSHRINK - ATHENA (internal use)",
    "I AM ATHENA",
}

ELEMENT_ORDER = ["Earth", "Water", "Fire", "Air"]
ELEMENT_SYMBOLS = {
    "E": "Earth",
    "W": "Water",
    "F": "Fire",
    "A": "Air",
}
MICRO_MODE_DESCRIPTIONS = {
    "Earth": "anchor, file, verify, preserve",
    "Water": "connect, bind, contextualize, restore",
    "Fire": "build, mutate, generate, intensify",
    "Air": "map, name, abstract, compress",
}
TRUTH_ORDER = ["OK", "NEAR", "AMBIG", "FAIL"]
CRYSTAL_CELL_ROLES = {
    ("Earth", "Earth"): "Pillar of corpus integrity, manifests, stable storage",
    ("Earth", "Water"): "Root binder of folders to memory surfaces",
    ("Earth", "Fire"): "Builder of durable artifact shells",
    ("Earth", "Air"): "Cartographer of concrete file terrain",
    ("Water", "Earth"): "Keeper of source lineage and replay continuity",
    ("Water", "Water"): "Pillar of manuscript memory and thematic persistence",
    ("Water", "Fire"): "Transmuter of raw notes into linked narrative motion",
    ("Water", "Air"): "Interpreter of meaning across folders and forms",
    ("Fire", "Earth"): "Implementer that turns plans into folders, files, scripts, and queues",
    ("Fire", "Water"): "Catalyst that turns memory into active synthesis",
    ("Fire", "Fire"): "Pillar of execution, generation, and commit pressure",
    ("Fire", "Air"): "Strategist that turns maps into build moves",
    ("Air", "Earth"): "Mapper that lands abstractions in file coordinates",
    ("Air", "Water"): "Storyweaver of lines, stations, and hubs",
    ("Air", "Fire"): "Signal spear for prioritization and high-yield compression",
    ("Air", "Air"): "Pillar of architecture, taxonomy, and metro reasoning",
}
LEGACY_MANIFEST_DEFAULTS = {
    "tensor": {"axes": [], "chapters": [], "families": [], "truth_default": "AMBIG", "live_docs_blocked": True},
    "swarm": {"layers": [], "relay_interfaces": [], "family_agents": [], "chapter_agents": [], "council_agents": []},
    "hypergraph": {"sources": {}, "edges": []},
    "node_tensor": {"nodes": [], "deep_pass": 0},
    "nerve_edges": {"edges": [], "deep_pass": 0},
    "civilization": {"tiers": [], "signs": [], "family_councils": [], "rail_councils": [], "live_docs_blocked": True},
    "frontiers": {"frontiers": []},
}
CONCEPTUAL_TO_LIVE_FAMILIES = {
    "civilization-and-governance": ["ECOSYSTEM", "Athenachka Collective Books", "DEEPER CRYSTALIZATION"],
    "general-corpus": ["DEEPER CRYSTALIZATION", "MATH", "Voynich", "self_actualize"],
    "higher-dimensional-geometry": ["MATH", "DEEPER CRYSTALIZATION"],
    "identity-and-instruction": ["Athenachka Collective Books", "I AM ATHENA", "self_actualize"],
    "live-orchestration": ["self_actualize", "Trading Bot", "NERVOUS_SYSTEM"],
    "manuscript-architecture": ["DEEPER CRYSTALIZATION", "Voynich", "self_actualize", "NERVOUS_SYSTEM"],
    "mythic-sign-systems": ["ECOSYSTEM", "Voynich", "Athenachka Collective Books", "I AM ATHENA"],
    "transport-and-runtime": ["MATH", "self_actualize", "Trading Bot", "NERUAL NETWORK"],
    "void-and-collapse": ["Trading Bot", "DEEPER CRYSTALIZATION", "MATH"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    pieces: list[str] = []
    for ch in lowered:
        if ch.isalnum():
            pieces.append(ch)
        else:
            pieces.append("_")
    slug = "".join(pieces)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "untitled"


def normalized_basename(path_text: str) -> str:
    name = Path(path_text).name.lower()
    stem = Path(name).stem
    if stem.endswith(" copy"):
        stem = stem[:-5]
    if stem.endswith("_copy"):
        stem = stem[:-5]
    if stem.endswith("-copy"):
        stem = stem[:-5]
    while stem.endswith(")"):
        left = stem.rfind("(")
        if left == -1:
            break
        inner = stem[left + 1 : -1]
        if inner.isdigit():
            stem = stem[:left].rstrip()
        else:
            break
    return f"{stem}{Path(name).suffix}"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_legacy_manifests() -> dict[str, Any]:
    return {
        "tensor": read_json(LEGACY_TENSOR_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["tensor"]),
        "swarm": read_json(LEGACY_SWARM_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["swarm"]),
        "hypergraph": read_json(LEGACY_HYPERGRAPH_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["hypergraph"]),
        "node_tensor": read_json(LEGACY_NODE_TENSOR_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["node_tensor"]),
        "nerve_edges": read_json(LEGACY_NERVE_EDGE_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["nerve_edges"]),
        "civilization": read_json(LEGACY_CIVILIZATION_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["civilization"]),
        "frontiers": read_json(LEGACY_FRONTIER_MANIFEST_PATH, LEGACY_MANIFEST_DEFAULTS["frontiers"]),
    }


def format_ts(epoch_ns: int | None) -> str:
    if epoch_ns is None:
        return "unknown"
    return datetime.fromtimestamp(epoch_ns / 1_000_000_000, tz=timezone.utc).isoformat()


def should_skip_parts(parts: tuple[str, ...]) -> bool:
    board_parts = BOARD_ROOT.relative_to(WORKSPACE_ROOT).parts
    if parts[: len(board_parts)] == board_parts:
        return True
    return any(part in IGNORE_DIRS for part in parts)


def top_level_sort_key(name: str) -> tuple[int, str]:
    if name in REGION_ORDER:
        return (REGION_ORDER.index(name), name.lower())
    return (len(REGION_ORDER), name.lower())


def lineage_to_elements(lineage: str) -> list[str]:
    elements: list[str] = []
    for token in lineage.replace(" ", "").split("-"):
        if not token:
            continue
        element = ELEMENT_SYMBOLS.get(token[0].upper())
        if element:
            elements.append(element)
    return elements


def archetype_for_lineage(lineage: str) -> tuple[str, str]:
    elements = lineage_to_elements(lineage)
    if not elements:
        return ("Air", "Air")
    if len(elements) == 1:
        return (elements[0], elements[0])
    return (elements[0], elements[1])


def archetype_role(primary: str, secondary: str) -> str:
    return CRYSTAL_CELL_ROLES.get((primary, secondary), "Unclassified crystal cell")


def micro_mode_for_thread(thread: dict[str, Any]) -> str:
    packet = thread.get("packet", "")
    status = thread.get("status", "")
    if packet == "ganglion" or thread.get("kind") == "region":
        return "Earth"
    if packet in {"pod", "worker", "wave"} or status in {"active", "queued", "blocked", "hot"}:
        return "Fire"
    if packet in {"note", "thread", "synthesis"} or thread.get("note_count", 0) > 0:
        return "Water"
    return "Air"


def cluster_id(primary: str, secondary: str, micro_mode: str) -> str:
    return f"CLUSTER-{slugify(primary)}-{slugify(secondary)}-{slugify(micro_mode)}"


def neuron_leaf_id(primary: str, secondary: str, micro_mode: str, truth: str) -> str:
    return f"LEAF-{slugify(primary)}-{slugify(secondary)}-{slugify(micro_mode)}-{slugify(truth)}"


def live_family_bridges(conceptual_family: str) -> list[str]:
    return CONCEPTUAL_TO_LIVE_FAMILIES.get(conceptual_family, [])


def file_record(rel_path: str, size: int, mtime_ns: int) -> dict[str, Any]:
    path_obj = Path(rel_path)
    top_level = path_obj.parts[0] if path_obj.parts else rel_path
    return {
        "relative_path": rel_path,
        "top_level": top_level,
        "extension": path_obj.suffix.lower() or "[noext]",
        "size": size,
        "mtime_ns": mtime_ns,
        "mtime_iso": format_ts(mtime_ns),
    }


def scan_workspace() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    extension_counts: Counter[str] = Counter()
    top_level_counts: Counter[str] = Counter()
    now_ns = time.time_ns()
    modified_last_hour = 0
    modified_last_day = 0

    for current_root, dirs, filenames in os.walk(WORKSPACE_ROOT):
        current_path = Path(current_root)
        rel_parts = ()
        if current_path != WORKSPACE_ROOT:
            rel_parts = current_path.relative_to(WORKSPACE_ROOT).parts
        if should_skip_parts(rel_parts):
            dirs[:] = []
            continue

        filtered_dirs: list[str] = []
        for dirname in dirs:
            candidate_parts = rel_parts + (dirname,)
            if should_skip_parts(candidate_parts):
                continue
            filtered_dirs.append(dirname)
        dirs[:] = filtered_dirs

        for filename in filenames:
            candidate_parts = rel_parts + (filename,)
            if should_skip_parts(candidate_parts):
                continue
            path = current_path / filename
            try:
                stat = path.stat()
            except OSError:
                continue
            rel_path = path.relative_to(WORKSPACE_ROOT).as_posix()
            record = file_record(rel_path=rel_path, size=stat.st_size, mtime_ns=stat.st_mtime_ns)
            files.append(record)
            extension_counts[record["extension"]] += 1
            top_level_counts[record["top_level"]] += 1
            age_ns = now_ns - stat.st_mtime_ns
            if age_ns <= 3_600_000_000_000:
                modified_last_hour += 1
            if age_ns <= 86_400_000_000_000:
                modified_last_day += 1

    files.sort(key=lambda item: item["relative_path"])
    recent_files = sorted(files, key=lambda item: item["mtime_ns"], reverse=True)[:80]

    digest = hashlib.sha256()
    for item in files:
        digest.update(item["relative_path"].encode("utf-8"))
        digest.update(str(item["size"]).encode("utf-8"))
        digest.update(str(item["mtime_ns"]).encode("utf-8"))

    duplicate_map: dict[str, list[str]] = defaultdict(list)
    for item in files:
        ext = item["extension"]
        if ext not in DOC_EXTS:
            continue
        base = normalized_basename(item["relative_path"])
        if base in SKIP_FOR_DUPES:
            continue
        duplicate_map[base].append(item["relative_path"])

    duplicate_families: list[dict[str, Any]] = []
    for name, paths in duplicate_map.items():
        if len(paths) < 2:
            continue
        unique_top_levels = sorted({Path(path).parts[0] for path in paths}, key=top_level_sort_key)
        duplicate_families.append(
            {
                "name": name,
                "count": len(paths),
                "top_levels": unique_top_levels,
                "paths": sorted(paths)[:8],
            }
        )
    duplicate_families.sort(key=lambda item: (-item["count"], item["name"]))

    return {
        "generated_at": utc_now(),
        "fingerprint": digest.hexdigest(),
        "file_count": len(files),
        "files": files,
        "recent_files": recent_files,
        "by_extension": dict(sorted(extension_counts.items(), key=lambda item: (-item[1], item[0]))),
        "by_top_level": dict(sorted(top_level_counts.items(), key=lambda item: (-item[1], top_level_sort_key(item[0])))),
        "modified_last_hour": modified_last_hour,
        "modified_last_day": modified_last_day,
        "duplicate_families": duplicate_families[:20],
    }


def compute_diff(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    previous_files = {}
    if previous:
        previous_files = {item["relative_path"]: item for item in previous.get("files", [])}
    current_files = {item["relative_path"]: item for item in current.get("files", [])}

    changes: list[dict[str, Any]] = []
    added = 0
    modified = 0
    removed = 0

    all_paths = set(previous_files) | set(current_files)
    for path in sorted(all_paths):
        before = previous_files.get(path)
        after = current_files.get(path)
        if before is None and after is not None:
            added += 1
            changes.append(
                {
                    "kind": "added",
                    "relative_path": path,
                    "top_level": after["top_level"],
                    "mtime_ns": after["mtime_ns"],
                    "mtime_iso": after["mtime_iso"],
                }
            )
            continue
        if before is not None and after is None:
            removed += 1
            changes.append(
                {
                    "kind": "removed",
                    "relative_path": path,
                    "top_level": before["top_level"],
                    "mtime_ns": before["mtime_ns"],
                    "mtime_iso": before["mtime_iso"],
                }
            )
            continue
        if before is None or after is None:
            continue
        if before["mtime_ns"] != after["mtime_ns"] or before["size"] != after["size"]:
            modified += 1
            changes.append(
                {
                    "kind": "modified",
                    "relative_path": path,
                    "top_level": after["top_level"],
                    "mtime_ns": after["mtime_ns"],
                    "mtime_iso": after["mtime_iso"],
                }
            )

    changes.sort(key=lambda item: item["mtime_ns"], reverse=True)
    return {
        "added": added,
        "modified": modified,
        "removed": removed,
        "total": added + modified + removed,
        "changes": changes[:160],
    }


def docs_gate_status() -> dict[str, Any]:
    credentials = TRADING_BOT_ROOT / "credentials.json"
    token = TRADING_BOT_ROOT / "token.json"
    status = "BLOCKED"
    detail = "OAuth credentials are missing."
    if credentials.exists() and token.exists():
        status = "READY"
        detail = "credentials.json and token.json are both present."
    elif credentials.exists():
        status = "PARTIAL"
        detail = "credentials.json exists but token.json is still missing."

    receipt_excerpt = ""
    if DOCS_GATE_RECEIPT_PATH.exists():
        text = DOCS_GATE_RECEIPT_PATH.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("Error:"):
                receipt_excerpt = stripped
                break
            if stripped.startswith("Command status:"):
                receipt_excerpt = stripped
    return {
        "status": status,
        "detail": detail,
        "receipt_excerpt": receipt_excerpt,
    }


def read_atlas_metrics() -> dict[str, Any]:
    live = read_json(LIVE_ATLAS_PATH, {})
    archive = read_json(ARCHIVE_ATLAS_PATH, {})
    manifest = read_json(ARCHIVE_MANIFEST_PATH, {})
    return {
        "live_record_count": live.get("record_count", 0),
        "archive_record_count": archive.get("record_count", 0),
        "archive_count": manifest.get("archive_count", archive.get("archive_count", 0)),
        "live_summary": live.get("summary", {}),
        "archive_summary": archive.get("summary", {}),
    }


def parse_queue() -> dict[str, list[str]]:
    queue: dict[str, list[str]] = defaultdict(list)
    current = "general"
    if not QUEUE_PATH.exists():
        return {}
    for raw_line in QUEUE_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        if line[:2] == "- ":
            queue[current].append(line[2:].strip())
            continue
        if len(line) > 3 and line[0].isdigit() and line[1:3] == ". ":
            queue[current].append(line[3:].strip())
    return dict(queue)


def parse_legacy_claims() -> list[dict[str, Any]]:
    if not LEGACY_CLAIMS_PATH.exists():
        return []
    claims: list[dict[str, Any]] = []
    for line in LEGACY_CLAIMS_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "Claim ID" in stripped or "---" in stripped:
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) < 7:
            continue
        owner = parts[3]
        status = parts[4].lower()
        paths: list[str] = []
        for field in (parts[5], parts[6]):
            field_clean = field.replace("`", "")
            for piece in field_clean.split(","):
                candidate = piece.strip()
                if "/" in candidate or "\\" in candidate or candidate.endswith(".md"):
                    paths.append(candidate)
        if owner.lower() in OPEN_STATUSES or owner.lower() in {"done", "completed", "superseded"}:
            owner = "legacy-unassigned"
        claims.append(
            {
                "claim_id": parts[0],
                "frontier": parts[1],
                "level": parts[2],
                "owner": owner,
                "status": status,
                "output_target": parts[5],
                "receipt": parts[6],
                "source": "legacy",
                "updated_at": None,
                "paths": paths,
                "note": "Imported from the legacy tandem frontier claims table.",
            }
        )
    return claims


def note_card_markdown(note: dict[str, Any]) -> str:
    path_lines = "\n".join(f"- `{path}`" for path in note.get("paths", [])) or "- none"
    return (
        f"# Note {note['note_id']}\n\n"
        f"- Agent: `{note['agent']}`\n"
        f"- Front: `{note['front']}`\n"
        f"- Status: `{note['status']}`\n"
        f"- Created: `{note['created_at']}`\n"
        f"- Updated: `{note['updated_at']}`\n\n"
        "## Related Paths\n"
        f"{path_lines}\n\n"
        "## Message\n"
        f"{note['message']}\n"
    )


def claim_card_markdown(claim: dict[str, Any]) -> str:
    path_lines = "\n".join(f"- `{path}`" for path in claim.get("paths", [])) or "- none"
    return (
        f"# Claim {claim['claim_id']}\n\n"
        f"- Frontier: `{claim['frontier']}`\n"
        f"- Level: `{claim['level']}`\n"
        f"- Owner: `{claim['owner']}`\n"
        f"- Status: `{claim['status']}`\n"
        f"- Output Target: `{claim['output_target']}`\n"
        f"- Receipt: `{claim['receipt']}`\n"
        f"- Source: `{claim['source']}`\n"
        f"- Created: `{claim['created_at']}`\n"
        f"- Updated: `{claim['updated_at']}`\n\n"
        "## Related Paths\n"
        f"{path_lines}\n\n"
        "## Note\n"
        f"{claim['note']}\n"
    )


def load_notes() -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    if not AGENT_ROOT.exists():
        return notes
    for path in sorted(AGENT_ROOT.glob("*/*/*.json")):
        if path.parent.name != "notes":
            continue
        note = read_json(path, None)
        if not note:
            continue
        note["json_path"] = path
        note["md_path"] = path.with_suffix(".md")
        notes.append(note)
    notes.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    return notes


def load_board_claims() -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    if not CLAIM_ROOT.exists():
        return claims
    for path in sorted(CLAIM_ROOT.glob("*.json")):
        claim = read_json(path, None)
        if not claim:
            continue
        claim["json_path"] = path
        claim["md_path"] = path.with_suffix(".md")
        claims.append(claim)
    claims.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    return claims


def build_claim_index(board_claims: list[dict[str, Any]], legacy_claims: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for claim in legacy_claims:
        merged[claim["claim_id"]] = claim
    for claim in board_claims:
        merged[claim["claim_id"]] = claim
    return merged


def make_object_id(prefix: str, owner: str, front: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha1(f"{prefix}|{owner}|{front}|{time.time_ns()}".encode("utf-8")).hexdigest()[:6]
    return f"{prefix}-{stamp}-{digest}"


def create_note(agent: str, front: str, status: str, message: str, paths: list[str]) -> dict[str, Any]:
    note_id = make_object_id("NOTE", agent, front)
    payload = {
        "note_id": note_id,
        "agent": agent,
        "front": front,
        "front_slug": slugify(front),
        "status": status.lower(),
        "message": message.strip(),
        "paths": paths,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    agent_dir = AGENT_ROOT / slugify(agent) / "notes"
    json_path = agent_dir / f"{note_id}.json"
    md_path = agent_dir / f"{note_id}.md"
    write_json(json_path, payload)
    write_text(md_path, note_card_markdown(payload))
    payload["json_path"] = json_path
    payload["md_path"] = md_path
    return payload


def save_claim(payload: dict[str, Any]) -> dict[str, Any]:
    CLAIM_ROOT.mkdir(parents=True, exist_ok=True)
    json_path = CLAIM_ROOT / f"{payload['claim_id']}.json"
    md_path = CLAIM_ROOT / f"{payload['claim_id']}.md"
    write_json(json_path, payload)
    write_text(md_path, claim_card_markdown(payload))
    payload["json_path"] = json_path
    payload["md_path"] = md_path
    return payload


def create_or_update_claim(
    agent: str,
    front: str,
    level: str,
    output_target: str,
    receipt: str,
    status: str,
    message: str,
    paths: list[str],
    claim_id: str | None = None,
) -> dict[str, Any]:
    existing: dict[str, Any] | None = None
    if claim_id:
        candidate = CLAIM_ROOT / f"{claim_id}.json"
        if candidate.exists():
            existing = read_json(candidate, None)
    if existing is None:
        claim_id = claim_id or make_object_id("CLM", agent, front)
        payload = {
            "claim_id": claim_id,
            "frontier": front,
            "front_slug": slugify(front),
            "level": level,
            "owner": agent,
            "status": status.lower(),
            "output_target": output_target,
            "receipt": receipt,
            "source": "board",
            "paths": paths,
            "note": message.strip(),
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        return save_claim(payload)

    existing["frontier"] = front or existing.get("frontier", "")
    existing["front_slug"] = slugify(existing["frontier"])
    existing["level"] = level or existing.get("level", "")
    existing["owner"] = agent or existing.get("owner", "")
    existing["status"] = status.lower() or existing.get("status", "")
    existing["output_target"] = output_target or existing.get("output_target", "")
    existing["receipt"] = receipt or existing.get("receipt", "")
    existing["paths"] = paths or existing.get("paths", [])
    existing["note"] = message.strip() or existing.get("note", "")
    existing["updated_at"] = utc_now()
    return save_claim(existing)


def infer_family(front: str, paths: list[str]) -> str:
    counter: Counter[str] = Counter()
    for path in paths:
        normalized = path.replace("\\", "/")
        top = normalized.split("/", 1)[0]
        if top in KNOWN_FAMILIES:
            counter[top] += 1
    if counter:
        return counter.most_common(1)[0][0]

    lowered = front.lower()
    family_matches = [
        "Voynich",
        "MATH",
        "Trading Bot",
        "DEEPER CRYSTALIZATION",
        "self_actualize",
        "ECOSYSTEM",
        "NERUAL NETWORK",
        "NERVOUS_SYSTEM",
        "FRESH",
        "Athenachka Collective Books",
        "I AM ATHENA",
    ]
    for family in family_matches:
        if family.lower() in lowered:
            return family

    heuristics = [
        ("docs", "Trading Bot"),
        ("oauth", "Trading Bot"),
        ("google", "Trading Bot"),
        ("archive", "MATH"),
        ("framework", "MATH"),
        ("math", "MATH"),
        ("folio", "Voynich"),
        ("voynich", "Voynich"),
        ("chapter", "DEEPER CRYSTALIZATION"),
        ("board", "self_actualize"),
        ("runtime", "self_actualize"),
        ("atlas", "self_actualize"),
        ("route", "self_actualize"),
        ("skill", "ECOSYSTEM"),
    ]
    for token, family in heuristics:
        if token in lowered:
            return family
    return "self_actualize"


def truth_for_status(status: str) -> str:
    mapping = {
        "done": "OK",
        "active": "NEAR",
        "blocked": "FAIL",
        "queued": "AMBIG",
        "hot": "NEAR",
        "monitor": "AMBIG",
    }
    return mapping.get(status, "AMBIG")


def regime_for_status(default_regime: str, status: str, docs_gate: dict[str, Any]) -> str:
    if status in {"blocked", "queued"}:
        return "restart-token"
    if docs_gate["status"] != "READY" and status in {"active", "hot"}:
        return "stratified" if default_regime == "classical" else default_regime
    return default_regime


def packet_for_thread(thread: dict[str, Any]) -> str:
    if thread["kind"] == "region":
        return "ganglion"
    if thread["kind"] == "front":
        return "pod"
    if thread["note_count"] > 0 and thread["claim_count"] == 0:
        return "note"
    return "thread"


def orbit_for_index(index: int) -> str:
    return f"O{index + 1:02d}"


def arc_for_thread(front: str, family: str, status: str) -> str:
    lowered = front.lower()
    if "docs" in lowered or family == "Trading Bot":
        return "Arc0"
    if family in {"MATH", "ECOSYSTEM", "FRESH"}:
        return "Arc1"
    if family in {"Voynich", "DEEPER CRYSTALIZATION", "Athenachka Collective Books"}:
        return "Arc2"
    if status == "done":
        return "Arc3"
    return "Arc1"


def preferred_face(profile: dict[str, str], status: str) -> str:
    if status == "blocked":
        return "Void"
    if status == "done":
        return "Aether"
    return profile["primary_face"]


def build_family_tensor(snapshot: dict[str, Any], docs_gate: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for family, weight in snapshot["by_top_level"].items():
        base = FAMILY_TENSOR_DEFAULTS.get(
            family,
            {
                "rail": "Me",
                "face": "Air",
                "scale": "G4",
                "hub": "AppA",
                "regime": "classical",
                "best_front": "family placement and routing",
                "ganglion": f"ganglia/GANGLION_{slugify(family)}.md",
                "lineage": "A-E-W",
                "truth": "AMBIG",
            },
        )
        record = {
            "family": family,
            "weight": weight,
            "primary_rail": base["rail"],
            "primary_face": base["face"],
            "preferred_scale": base["scale"],
            "primary_hub": base["hub"],
            "preferred_regime": base["regime"],
            "best_front": base["best_front"],
            "primary_ganglion": base["ganglion"],
            "lineage": base["lineage"],
            "truth": base["truth"],
        }
        if family == "Trading Bot" and docs_gate["status"] != "READY":
            record["truth"] = "FAIL"
            record["preferred_regime"] = "restart-token"
        records.append(record)

    records.sort(key=lambda item: (-item["weight"], top_level_sort_key(item["family"])))
    return records


def annotate_threads(
    threads: list[dict[str, Any]],
    family_tensor: list[dict[str, Any]],
    docs_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    profile_map = {item["family"]: item for item in family_tensor}
    for index, thread in enumerate(threads):
        family = infer_family(
            front=thread["front"],
            paths=[*thread.get("claim_paths", []), *thread.get("note_paths", [])],
        )
        profile = profile_map.get(family) or profile_map.get("self_actualize")
        packet = packet_for_thread(thread)
        truth = truth_for_status(thread["status"])
        regime = regime_for_status(profile["preferred_regime"], thread["status"], docs_gate)
        orbit = orbit_for_index(index)
        arc = arc_for_thread(thread["front"], family, thread["status"])
        face = preferred_face(profile, thread["status"])
        primary_element, secondary_element = archetype_for_lineage(profile["lineage"])
        thread["family"] = family
        thread["rail"] = profile["primary_rail"]
        thread["face"] = face
        thread["scale"] = profile["preferred_scale"]
        thread["hub"] = profile["primary_hub"]
        thread["regime"] = regime
        thread["truth"] = truth
        thread["packet"] = packet
        thread["lineage"] = profile["lineage"]
        thread["orbit"] = orbit
        thread["arc"] = arc
        thread["contraction_target"] = f"cortex/{thread['front_slug']}.md"
        thread["primary_element"] = primary_element
        thread["secondary_element"] = secondary_element
        thread["archetype_cell"] = f"{primary_element}-{secondary_element}"
        thread["archetype_role"] = archetype_role(primary_element, secondary_element)
        thread["micro_mode"] = micro_mode_for_thread(thread)
        thread["cluster_id"] = cluster_id(primary_element, secondary_element, thread["micro_mode"])
        thread["cluster_role"] = (
            f"{thread['archetype_role']} operating in {thread['micro_mode']} mode "
            f"({MICRO_MODE_DESCRIPTIONS[thread['micro_mode']]})"
        )
        thread["neuron_leaf"] = neuron_leaf_id(primary_element, secondary_element, thread["micro_mode"], truth)
        thread["nscoord"] = (
            f"({profile['lineage']}, {profile['preferred_scale']}, {face}, {orbit}, {arc}, "
            f"{profile['primary_rail']}, {profile['primary_hub']}, {family}, {regime}, {packet}, {truth})"
        )
        thread["neuron_addr"] = (
            f"<{family}, {slugify(thread['front'])}, {orbit}, C, 3, a, {profile['lineage'].replace('-', '')}, "
            f"{arc}, {profile['primary_rail']}, {profile['primary_hub']}, {truth}, {regime}>"
        )
    return threads


def build_pods(threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pods: list[dict[str, Any]] = []
    for idx, thread in enumerate(threads):
        if thread["kind"] != "front":
            continue
        pods.append(
            {
                "pod_id": f"POD-{idx + 1:02d}-{thread['front_slug']}",
                "frontier": thread["front"],
                "agents": sorted({*(note["agent"] for note in thread["notes"]), *(claim.get("owner", "") for claim in thread["claims"] if claim.get("owner"))}),
                "family": thread["family"],
                "rail": thread["rail"],
                "packet_family": thread["packet"],
                "contraction_target": thread["contraction_target"],
                "status": thread["status"],
                "truth": thread["truth"],
                "hub": thread["hub"],
                "regime": thread["regime"],
                "nscoord": thread["nscoord"],
                "archetype_cell": thread["archetype_cell"],
                "archetype_role": thread["archetype_role"],
                "micro_mode": thread["micro_mode"],
                "cluster_id": thread["cluster_id"],
                "cluster_role": thread["cluster_role"],
                "neuron_leaf": thread["neuron_leaf"],
            }
        )
    return pods


def build_neurons(pods: list[dict[str, Any]], family_tensor: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tensor_map = {item["family"]: item for item in family_tensor}
    neurons: list[dict[str, Any]] = []
    for idx, (src, dst, hub, purpose) in enumerate(TRANSFER_HUBS, start=1):
        src_profile = tensor_map.get(src)
        dst_profile = tensor_map.get(dst)
        if not src_profile or not dst_profile:
            continue
        active_src = [pod["pod_id"] for pod in pods if pod["family"] == src]
        active_dst = [pod["pod_id"] for pod in pods if pod["family"] == dst]
        truth = "OK" if active_src and active_dst else "AMBIG"
        src_primary, _src_secondary = archetype_for_lineage(src_profile["lineage"])
        dst_primary, _dst_secondary = archetype_for_lineage(dst_profile["lineage"])
        bridge_cell = f"{src_primary}-{dst_primary}"
        bridge_micro_mode = "Air"
        neurons.append(
            {
                "node_id": f"NEURON-{idx:02d}-{slugify(src)}-to-{slugify(dst)}",
                "src_family": src,
                "dst_family": dst,
                "operator": purpose,
                "witness_set": active_src + active_dst,
                "replay_path": f"{src_profile['primary_hub']} -> {hub} -> {dst_profile['primary_hub']}",
                "truth_class": truth,
                "hub": hub,
                "archetype_cell": bridge_cell,
                "archetype_role": archetype_role(src_primary, dst_primary),
                "micro_mode": bridge_micro_mode,
                "cluster_id": cluster_id(src_primary, dst_primary, bridge_micro_mode),
                "neuron_leaf": neuron_leaf_id(src_primary, dst_primary, bridge_micro_mode, truth),
            }
        )
    return neurons


def build_waves(pods: list[dict[str, Any]], docs_gate: dict[str, Any], diff: dict[str, Any]) -> list[dict[str, Any]]:
    active_pods = [pod for pod in pods if pod["status"] in {"active", "queued", "blocked"}]
    if not active_pods:
        active_pods = pods[:4]
    stop_condition = "gate unlock or one reusable artifact lands"
    if diff["total"] == 0:
        stop_condition = "new workspace mutation or new claim lands"
    wave = {
        "wave_id": f"WAVE-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "goal": "continue the higher-dimensional swarm from the strongest admissible frontier",
        "active_pods": [pod["pod_id"] for pod in active_pods[:8]],
        "shared_kernel": "board_status + family_tensor + current_claims",
        "writeback_set": [
            "00_STATUS/00_BOARD_STATUS.md",
            "03_CLAIMS/00_ACTIVE_CLAIMS.md",
            "08_SWARM_RUNTIME/manifests/ACTIVE_RUN.md",
        ],
        "stop_condition": stop_condition,
        "restart_seed": "Start at the beginning again. Check the live Docs gate, preserve the blocker exactly if blocked, then choose the smallest stronger front.",
        "gate_status": docs_gate["status"],
    }
    return [wave]


def build_kernel_state(
    threads: list[dict[str, Any]],
    pods: list[dict[str, Any]],
    waves: list[dict[str, Any]],
    active_run: dict[str, Any],
    docs_gate: dict[str, Any],
    legacy: dict[str, Any],
) -> dict[str, Any]:
    return {
        "kernel_id": "KERNEL-Z0",
        "docs_gate_status": docs_gate["status"],
        "relay_interfaces": legacy["swarm"].get("relay_interfaces", []),
        "tier_count": len(legacy["civilization"].get("tiers", [])),
        "sign_count": len(legacy["civilization"].get("signs", [])),
        "hypergraph_edges": len(legacy["hypergraph"].get("edges", [])),
        "node_tensor_nodes": len(legacy["node_tensor"].get("nodes", [])),
        "nerve_edges": len(legacy["nerve_edges"].get("edges", [])),
        "frontier_gap_count": len(legacy["frontiers"].get("frontiers", [])),
        "current_front": active_run["chosen_front"],
        "pivot_front": active_run["pivot_front"],
        "thread_count": len(threads),
        "pod_count": len(pods),
        "wave_ids": [wave["wave_id"] for wave in waves],
    }


def build_elemental_field(
    threads: list[dict[str, Any]],
    pods: list[dict[str, Any]],
    bridge_neurons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pillar_roles = {
        "Earth": "structure, files, manifests, integrity",
        "Water": "memory, continuity, manuscript flow",
        "Fire": "execution, transformation, construction",
        "Air": "abstraction, mapping, routing",
    }
    records = {
        element: {
            "element": element,
            "role": pillar_roles[element],
            "thread_ids": [],
            "pod_ids": [],
            "neuron_ids": [],
        }
        for element in ELEMENT_ORDER
    }
    for thread in threads:
        records[thread["primary_element"]]["thread_ids"].append(thread["front"])
    for pod in pods:
        primary = pod["archetype_cell"].split("-")[0]
        records[primary]["pod_ids"].append(pod["pod_id"])
    for neuron in bridge_neurons:
        primary = neuron["archetype_cell"].split("-")[0]
        records[primary]["neuron_ids"].append(neuron["node_id"])

    result = []
    for element in ELEMENT_ORDER:
        record = records[element]
        record["thread_count"] = len(record["thread_ids"])
        record["pod_count"] = len(record["pod_ids"])
        record["neuron_count"] = len(record["neuron_ids"])
        result.append(record)
    return result


def build_archetype_lattice(threads: list[dict[str, Any]], pods: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    record_map: dict[str, dict[str, Any]] = {}
    for primary in ELEMENT_ORDER:
        for secondary in ELEMENT_ORDER:
            cell = f"{primary}-{secondary}"
            record = {
                "cell": cell,
                "primary": primary,
                "secondary": secondary,
                "role": archetype_role(primary, secondary),
                "thread_ids": [],
                "pod_ids": [],
                "micro_modes": Counter(),
                "truths": Counter(),
            }
            records.append(record)
            record_map[cell] = record

    for thread in threads:
        record = record_map[thread["archetype_cell"]]
        record["thread_ids"].append(thread["front"])
        record["micro_modes"][thread["micro_mode"]] += 1
        record["truths"][thread["truth"]] += 1
    for pod in pods:
        record_map[pod["archetype_cell"]]["pod_ids"].append(pod["pod_id"])

    for record in records:
        record["thread_count"] = len(record["thread_ids"])
        record["pod_count"] = len(record["pod_ids"])

    records.sort(key=lambda item: (-item["thread_count"], -item["pod_count"], item["cell"]))
    return records


def build_pantheon_overlay(archetypes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pantheon = [item for item in archetypes if item["primary"] != item["secondary"]]
    pantheon.sort(key=lambda item: (-item["thread_count"], -item["pod_count"], item["cell"]))
    return pantheon


def build_cluster_field(
    threads: list[dict[str, Any]],
    pods: list[dict[str, Any]],
    bridge_neurons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    record_map: dict[str, dict[str, Any]] = {}
    for primary in ELEMENT_ORDER:
        for secondary in ELEMENT_ORDER:
            role = archetype_role(primary, secondary)
            for micro_mode in ELEMENT_ORDER:
                cid = cluster_id(primary, secondary, micro_mode)
                record = {
                    "cluster_id": cid,
                    "cell": f"{primary}-{secondary}",
                    "micro_mode": micro_mode,
                    "role": f"{role} in {micro_mode} mode ({MICRO_MODE_DESCRIPTIONS[micro_mode]})",
                    "thread_ids": [],
                    "pod_ids": [],
                    "neuron_ids": [],
                    "truths": Counter(),
                }
                records.append(record)
                record_map[cid] = record

    for thread in threads:
        record = record_map[thread["cluster_id"]]
        record["thread_ids"].append(thread["front"])
        record["truths"][thread["truth"]] += 1
    for pod in pods:
        record_map[pod["cluster_id"]]["pod_ids"].append(pod["pod_id"])
    for neuron in bridge_neurons:
        record_map[neuron["cluster_id"]]["neuron_ids"].append(neuron["node_id"])
        record_map[neuron["cluster_id"]]["truths"][neuron["truth_class"]] += 1

    for record in records:
        record["occupancy"] = len(record["thread_ids"]) + len(record["pod_ids"]) + len(record["neuron_ids"])

    records.sort(key=lambda item: (-item["occupancy"], item["cluster_id"]))
    return records


def build_neuron_lattice(threads: list[dict[str, Any]], bridge_neurons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    record_map: dict[str, dict[str, Any]] = {}
    for primary in ELEMENT_ORDER:
        for secondary in ELEMENT_ORDER:
            for micro_mode in ELEMENT_ORDER:
                cluster = cluster_id(primary, secondary, micro_mode)
                for truth in TRUTH_ORDER:
                    leaf = neuron_leaf_id(primary, secondary, micro_mode, truth)
                    record = {
                        "leaf_id": leaf,
                        "cluster_id": cluster,
                        "cell": f"{primary}-{secondary}",
                        "micro_mode": micro_mode,
                        "truth": truth,
                        "thread_ids": [],
                        "neuron_ids": [],
                    }
                    records.append(record)
                    record_map[leaf] = record

    for thread in threads:
        record_map[thread["neuron_leaf"]]["thread_ids"].append(thread["front"])
    for neuron in bridge_neurons:
        record_map[neuron["neuron_leaf"]]["neuron_ids"].append(neuron["node_id"])

    for record in records:
        record["occupancy"] = len(record["thread_ids"]) + len(record["neuron_ids"])

    records.sort(key=lambda item: (-item["occupancy"], item["leaf_id"]))
    return records


def build_council_mesh(legacy: dict[str, Any], threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chapter_map = {item["code"]: item for item in legacy["swarm"].get("chapter_agents", [])}
    tensor_chapter_map = {item["code"]: item for item in legacy["tensor"].get("chapters", [])}
    family_map = {item["family"]: item for item in legacy["swarm"].get("family_agents", [])}
    frontier_map = {item["chapter"]: item for item in legacy["frontiers"].get("frontiers", [])}
    sign_map = {item["id"]: item for item in legacy["civilization"].get("signs", [])}
    councils: list[dict[str, Any]] = []
    for council in legacy["swarm"].get("council_agents", []):
        if council.get("scope") == "rail":
            live_threads = [thread for thread in threads if thread["rail"] == council["rail"]]
            chapter_targets = [
                chapter["code"] for chapter in legacy["tensor"].get("chapters", []) if chapter.get("rail") == council["rail"]
            ]
            sign_ids = sorted(
                {
                    sign_id
                    for chapter in chapter_targets
                    for sign_id in tensor_chapter_map.get(chapter, {}).get("governance_signs", [])
                }
            )
            label = f"{council['rail']} rail council"
            frontier_hits = [frontier_map[chapter] for chapter in chapter_targets if chapter in frontier_map]
        else:
            family_agent = family_map.get(council["family"], {})
            bridge_families = live_family_bridges(council["family"])
            live_threads = [thread for thread in threads if thread["family"] in bridge_families]
            chapter_targets = family_agent.get("chapter_targets", [])
            sign_ids = sorted(
                {
                    sign_id
                    for chapter in chapter_targets
                    for sign_id in chapter_map.get(chapter, {}).get("governance_signs", [])
                }
            )
            label = family_agent.get("label", council["family"])
            frontier_hits = [frontier_map[chapter] for chapter in chapter_targets if chapter in frontier_map]
        councils.append(
            {
                "id": council["id"],
                "scope": council["scope"],
                "label": label,
                "family": council.get("family"),
                "rail": council.get("rail"),
                "chapter_targets": chapter_targets,
                "sign_ids": sign_ids,
                "sign_labels": [sign_map[sign_id]["label"] for sign_id in sign_ids if sign_id in sign_map],
                "live_threads": live_threads,
                "frontier_hits": frontier_hits,
            }
        )
    councils.sort(key=lambda item: (item["scope"] != "rail", -len(item["live_threads"]), item["id"]))
    return councils


def build_hypergraph_projection(
    legacy: dict[str, Any],
    threads: list[dict[str, Any]],
    bridge_neurons: list[dict[str, Any]],
    councils: list[dict[str, Any]],
) -> dict[str, Any]:
    edges = legacy["hypergraph"].get("edges", [])
    edge_kinds = Counter(edge.get("kind", "unknown") for edge in edges)
    family_degrees = Counter(edge["dst"] for edge in edges if edge.get("kind") == "source_to_family")
    chapter_degrees = Counter(edge["dst"] for edge in edges if edge.get("kind") == "source_to_chapter")
    hub_degrees = Counter(edge["dst"] for edge in edges if edge.get("kind") == "chapter_to_hub")
    return {
        "source_count": len(legacy["hypergraph"].get("sources", {})),
        "edge_count": len(edges),
        "edge_kinds": edge_kinds,
        "top_families": family_degrees.most_common(8),
        "top_chapters": chapter_degrees.most_common(8),
        "top_hubs": hub_degrees.most_common(8),
        "live_thread_count": len(threads),
        "live_bridge_count": len(bridge_neurons),
        "council_count": len(councils),
        "frontiers": legacy["frontiers"].get("frontiers", []),
    }


def build_active_run_manifest(threads: list[dict[str, Any]], queue: dict[str, list[str]], docs_gate: dict[str, Any], diff: dict[str, Any]) -> dict[str, Any]:
    prioritized = sorted(
        threads,
        key=lambda item: (
            item["status"] not in {"blocked", "active", "queued", "hot"},
            item["family"] != "Trading Bot",
            item["family"] != "MATH",
            -item["claim_count"],
            -item["change_count"],
        ),
    )
    chosen = prioritized[0] if prioritized else None
    pivot = next(
        (
            thread
            for thread in prioritized
            if thread["family"] != "Trading Bot" and thread["status"] in {"active", "queued", "hot", "monitor"}
        ),
        chosen,
    )
    return {
        "gate_status": docs_gate["status"],
        "chosen_front": chosen["front"] if chosen else "none",
        "chosen_family": chosen["family"] if chosen else "none",
        "chosen_nscoord": chosen["nscoord"] if chosen else "none",
        "pivot_front": pivot["front"] if pivot else "none",
        "pivot_family": pivot["family"] if pivot else "none",
        "pivot_nscoord": pivot["nscoord"] if pivot else "none",
        "artifact_delta": f"+{diff['added']} ~{diff['modified']} -{diff['removed']}",
        "verification_summary": [
            "confirm board artifacts exist",
            "confirm claims and threads agree on ownership",
            "confirm next seed points at the next stronger front",
        ],
        "frontier_update": queue.get("P0", [])[:2] + queue.get("P1", [])[:2],
    }


def build_next_seed(active_run: dict[str, Any], docs_gate: dict[str, Any]) -> str:
    front = active_run["chosen_front"]
    family = active_run["chosen_family"]
    gate_line = "1. Check the live Docs gate."
    if docs_gate["status"] != "READY":
        gate_line += (
            " It is still blocked, so preserve the blocker exactly and pivot immediately to "
            f"`{active_run['pivot_front']}` in family `{active_run['pivot_family']}`."
        )
    return (
        "You are continuing the Athena higher-dimensional swarm runtime.\n\n"
        "Start at the beginning again.\n\n"
        f"{gate_line}\n"
        "2. Read the family tensor, current wave, active claims, and thread coordinates.\n"
        f"3. Preserve the gate state, then work the strongest admissible local front: `{front}` in family `{family}`.\n"
        "4. Land one stronger reusable surface: pod, neuron, ganglion, rail update, ledger, or manifest.\n"
        "5. Verify truth class, contraction target, and ownership.\n"
        "6. Emit the next restart seed instead of stopping.\n"
    )


def render_board_readme() -> str:
    return (
        "# Realtime Swarm Board\n\n"
        "This is the live coordination surface for the full-project integration layer.\n"
        "It is also a projection of the higher-dimensional swarm runtime, not only a flat message board.\n\n"
        "## Folder Map\n\n"
        "- `00_STATUS/` holds the current workspace snapshot and orchestrator view.\n"
        "- `01_AGENT_INBOXES/` holds per-agent note folders and generated inboxes.\n"
        "- `02_ACTIVE_THREADS/` holds one folder per active front or hot region.\n"
        "- `03_CLAIMS/` holds human-readable claim cards and the merged claims summary.\n"
        "- `04_CHANGE_FEED/` holds recent file-change observations and event history.\n"
        "- `05_SYNTHESIS/` holds whole-project and cross-region synthesis documents.\n"
        "- `06_PROTOCOLS/` explains how the board should be used.\n"
        "- `07_TENSOR/` holds family tensor, thread coordinates, archetype, pantheon, cluster, and neuron-lattice projections.\n"
        "- `08_SWARM_RUNTIME/` holds kernel, elementals, ganglia, rails, archetypes, councils, pods, neurons, hypergraph, waves, manifests, and cortex summaries.\n\n"
        "## Canonical Rule\n\n"
        "New work should claim a frontier here before it expands. The goal is one shared place "
        "where agents can see what is active, what changed, how it is located in the swarm tensor, "
        "and what should not be duplicated.\n"
    )


def render_protocol_doc() -> str:
    return (
        "# How To Use The Realtime Swarm Board\n\n"
        "## Primary Commands\n\n"
        "```powershell\n"
        "python -m self_actualize.runtime.swarm_board build\n"
        "python -m self_actualize.runtime.swarm_board watch --interval 15\n"
        "python -m self_actualize.runtime.swarm_board note --agent codex --front \"archive promotion\" --message \"Investigating archive-backed framework landing zone\"\n"
        "python -m self_actualize.runtime.swarm_board claim --agent codex --front \"archive promotion\" --level framework --output-target \"MATH extracted tree\" --receipt \"receipt pending\" --status active --message \"Claiming archive promotion front\"\n"
        "```\n\n"
        "## Operating Rule\n\n"
        "1. Refresh the board or run the watcher.\n"
        "2. Read `03_CLAIMS/00_ACTIVE_CLAIMS.md`, `07_TENSOR/01_FAMILY_TENSOR_FIELD.md`, `07_TENSOR/05_ARCHETYPE_GRID.md`, and `08_SWARM_RUNTIME/manifests/ACTIVE_RUN.md`.\n"
        "3. Claim the smallest frontier that creates the biggest shared reuse gain.\n"
        "4. Leave at least one note or claim card before going deep.\n"
        "5. Make sure every serious front has a family owner, rail, packet class, truth class, contraction target, archetype cell, cluster, and truth leaf.\n"
        "6. Land a receipt or change the claim status when the artifact is done.\n"
        "7. Update the next self prompt so the loop restarts from the beginning.\n\n"
        "## No-Duplication Rule\n\n"
        "If a frontier is already `active`, take a validation or receipt role unless the owner has explicitly handed it off.\n"
    )


def render_status_doc(
    snapshot: dict[str, Any],
    diff: dict[str, Any],
    atlas_metrics: dict[str, Any],
    docs_gate: dict[str, Any],
    queue: dict[str, list[str]],
    all_claims: dict[str, dict[str, Any]],
    notes: list[dict[str, Any]],
    events: list[dict[str, Any]],
    pods: list[dict[str, Any]],
    neurons: list[dict[str, Any]],
    waves: list[dict[str, Any]],
    active_run: dict[str, Any],
    kernel_state: dict[str, Any],
    councils: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
    neuron_lattice: list[dict[str, Any]],
    hypergraph: dict[str, Any],
) -> str:
    active_claims = [claim for claim in all_claims.values() if claim.get("status") in OPEN_STATUSES]
    recent_events = events[-5:]
    hot_regions = list(snapshot["by_top_level"].items())[:8]
    queue_lines = []
    for bucket in ("P0", "P1", "P2"):
        for item in queue.get(bucket, [])[:4]:
            queue_lines.append(f"- `{bucket}` {item}")
    if not queue_lines:
        queue_lines.append("- queue unavailable")

    event_lines = []
    for event in reversed(recent_events):
        summary = event.get("summary", {})
        event_lines.append(
            f"- `{event.get('detected_at', 'unknown')}` "
            f"+{summary.get('added', 0)} ~{summary.get('modified', 0)} -{summary.get('removed', 0)}"
        )
    if not event_lines:
        event_lines.append("- no prior board events")

    region_lines = []
    for name, count in hot_regions:
        region_lines.append(f"- `{name}`: `{count}` visible files")

    return (
        "# Board Status\n\n"
        f"- Generated: `{snapshot['generated_at']}`\n"
        f"- Workspace files observed: `{snapshot['file_count']}`\n"
        f"- Live atlas records: `{atlas_metrics['live_record_count']}`\n"
        f"- Archive-backed records: `{atlas_metrics['archive_record_count']}` across `{atlas_metrics['archive_count']}` archives\n"
        f"- Change batch: `+{diff['added']} ~{diff['modified']} -{diff['removed']}`\n"
        f"- Notes on board: `{len(notes)}`\n"
        f"- Open claims: `{len(active_claims)}`\n"
        f"- Pods: `{len(pods)}`\n"
        f"- Bridge neurons: `{len(neurons)}`\n"
        f"- Waves: `{len(waves)}`\n"
        f"- Councils: `{len(councils)}`\n"
        f"- Occupied clusters: `{sum(1 for item in clusters if item['occupancy'])}` of `{len(clusters)}`\n"
        f"- Occupied truth leaves: `{sum(1 for item in neuron_lattice if item['occupancy'])}` of `{len(neuron_lattice)}`\n"
        f"- Legacy hypergraph edges: `{hypergraph['edge_count']}`\n"
        f"- Live Docs gate: `{docs_gate['status']}`\n"
        f"- Docs detail: {docs_gate['detail']}\n\n"
        "## Global Read\n\n"
        "The workspace is already a multi-body organism and the board now treats it as a higher-dimensional swarm: "
        "kernel, elementals, archetypes, pantheon, clusters, truth leaves, ganglia, councils, pods, neurons, waves, and manifests now all project into one live board. "
        "The older machine-readable swarm is folded in rather than ignored: the board is carrying the legacy hypergraph, council mesh, frontier gaps, and civilization tiers forward into the current control plane. "
        "Voynich remains the densest live manuscript engine, MATH remains the deepest formal reservoir, DEEPER CRYSTALIZATION remains the integration compiler, "
        "self_actualize remains the runtime waist, Trading Bot remains the blocked external-memory bridge, and ECOSYSTEM remains the governance shell. "
        "The highest leverage move is therefore coordination that prevents those bodies from rediscovering each other every run while still preserving the real blocked gate.\n\n"
        "## Active Run\n\n"
        f"- Chosen front: `{active_run['chosen_front']}`\n"
        f"- Chosen family: `{active_run['chosen_family']}`\n"
        f"- Pivot front: `{active_run['pivot_front']}`\n"
        f"- Chosen NSCoord: `{active_run['chosen_nscoord']}`\n\n"
        "## Kernel Read\n"
        f"- Kernel: `{kernel_state['kernel_id']}`\n"
        f"- Relay interfaces: `{len(kernel_state['relay_interfaces'])}`\n"
        f"- Frontier gaps preserved: `{kernel_state['frontier_gap_count']}`\n\n"
        "## Hot Regions\n"
        + "\n".join(region_lines)
        + "\n\n## Queue Pressure\n"
        + "\n".join(queue_lines)
        + "\n\n## Recent Board Events\n"
        + "\n".join(event_lines)
        + "\n"
    )


def render_change_feed(diff: dict[str, Any], events: list[dict[str, Any]]) -> str:
    change_lines = []
    for change in diff.get("changes", [])[:60]:
        change_lines.append(
            f"- `{change['kind']}` `{change['relative_path']}` at `{change['mtime_iso']}`"
        )
    if not change_lines:
        change_lines.append("- no workspace changes detected since the previous snapshot")

    event_lines = []
    for event in reversed(events[-12:]):
        summary = event.get("summary", {})
        event_lines.append(
            f"- `{event.get('detected_at', 'unknown')}` "
            f"+{summary.get('added', 0)} ~{summary.get('modified', 0)} -{summary.get('removed', 0)}"
        )
    if not event_lines:
        event_lines.append("- no event history yet")

    return (
        "# Change Feed\n\n"
        "## Current Batch\n"
        + "\n".join(change_lines)
        + "\n\n## Event History\n"
        + "\n".join(event_lines)
        + "\n"
    )


def render_claim_summary(all_claims: dict[str, dict[str, Any]]) -> str:
    claims = sorted(
        all_claims.values(),
        key=lambda item: (
            item.get("status") not in OPEN_STATUSES,
            item.get("updated_at") or "",
            item["claim_id"],
        ),
        reverse=True,
    )
    rows = [
        "| Claim ID | Frontier | Level | Owner | Status | Output Target | Source |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for claim in claims:
        rows.append(
            "| "
            + " | ".join(
                [
                    claim["claim_id"],
                    claim["frontier"],
                    claim.get("level", ""),
                    claim.get("owner", ""),
                    claim.get("status", ""),
                    claim.get("output_target", ""),
                    claim.get("source", ""),
                ]
            )
            + " |"
        )
    return "# Active Claims\n\n" + "\n".join(rows) + "\n"


def render_agent_index(notes: list[dict[str, Any]], all_claims: dict[str, dict[str, Any]]) -> str:
    agent_counts: Counter[str] = Counter(note["agent"] for note in notes)
    claim_counts: Counter[str] = Counter(
        claim["owner"] for claim in all_claims.values() if claim.get("status") in OPEN_STATUSES
    )
    agents = sorted(set(agent_counts) | set(claim_counts))
    lines = ["# Agent Inboxes", ""]
    for agent in agents:
        agent_slug = slugify(agent)
        lines.append(
            f"- `{agent}`: `{agent_counts[agent]}` notes, `{claim_counts[agent]}` open claims, "
            f"`01_AGENT_INBOXES/{agent_slug}/INBOX.md`"
        )
    if len(lines) == 2:
        lines.append("- no agent notes or claims yet")
    lines.append("")
    return "\n".join(lines)


def render_agent_inbox(agent: str, notes: list[dict[str, Any]], claims: list[dict[str, Any]]) -> str:
    note_lines = [
        f"- `{note['updated_at']}` `{note['front']}` -> `{note['status']}` "
        f"(`{note['md_path'].relative_to(BOARD_ROOT).as_posix()}`)"
        for note in notes[:20]
    ]
    if not note_lines:
        note_lines.append("- no notes yet")
    claim_lines = [
        f"- `{claim.get('status', '')}` `{claim['frontier']}` -> `{claim.get('output_target', '')}`"
        for claim in claims[:20]
    ]
    if not claim_lines:
        claim_lines.append("- no claims yet")
    return (
        f"# Inbox `{agent}`\n\n"
        "## Claims\n"
        + "\n".join(claim_lines)
        + "\n\n## Notes\n"
        + "\n".join(note_lines)
        + "\n"
    )


def render_thread_index(threads: list[dict[str, Any]]) -> str:
    lines = ["# Active Threads", ""]
    for thread in threads:
        lines.append(
            f"- `{thread['front']}`: `{thread['status']}`, `{thread['note_count']}` notes, "
            f"`{thread['claim_count']}` claims, `{thread['change_count']}` tracked changes"
        )
    if len(lines) == 2:
        lines.append("- no active threads yet")
    lines.append("")
    return "\n".join(lines)


def render_thread_doc(thread: dict[str, Any]) -> str:
    claim_lines = [
        f"- `{claim['claim_id']}` `{claim.get('status', '')}` by `{claim.get('owner', '')}` -> `{claim.get('output_target', '')}`"
        for claim in thread["claims"][:20]
    ]
    if not claim_lines:
        claim_lines.append("- no claims attached")

    note_lines = [
        f"- `{note['updated_at']}` `{note['agent']}` -> `{note['status']}` "
        f"(`{note['md_path'].relative_to(BOARD_ROOT).as_posix()}`)"
        for note in thread["notes"][:20]
    ]
    if not note_lines:
        note_lines.append("- no notes attached")

    change_lines = [
        f"- `{change['kind']}` `{change['relative_path']}` at `{change['mtime_iso']}`"
        for change in thread["changes"][:25]
    ]
    if not change_lines:
        change_lines.append("- no current file changes tied to this thread")

    return (
        f"# Thread `{thread['front']}`\n\n"
        f"- Thread status: `{thread['status']}`\n"
        f"- Notes: `{thread['note_count']}`\n"
        f"- Claims: `{thread['claim_count']}`\n"
        f"- Tracked changes: `{thread['change_count']}`\n"
        f"- Family: `{thread.get('family', 'unknown')}`\n"
        f"- ArchetypeCell: `{thread.get('archetype_cell', 'unknown')}`\n"
        f"- ArchetypeRole: {thread.get('archetype_role', 'unknown')}\n"
        f"- MicroMode: `{thread.get('micro_mode', 'unknown')}`\n"
        f"- ClusterID: `{thread.get('cluster_id', 'unknown')}`\n"
        f"- NeuronLeaf: `{thread.get('neuron_leaf', 'unknown')}`\n"
        f"- Rail: `{thread.get('rail', 'unknown')}`\n"
        f"- Face: `{thread.get('face', 'unknown')}`\n"
        f"- Scale: `{thread.get('scale', 'unknown')}`\n"
        f"- Hub: `{thread.get('hub', 'unknown')}`\n"
        f"- Regime: `{thread.get('regime', 'unknown')}`\n"
        f"- Packet: `{thread.get('packet', 'unknown')}`\n"
        f"- Truth: `{thread.get('truth', 'unknown')}`\n"
        f"- NSCoord: `{thread.get('nscoord', 'unknown')}`\n"
        f"- NeuronAddr: `{thread.get('neuron_addr', 'unknown')}`\n"
        f"- ContractionTarget: `{thread.get('contraction_target', 'unknown')}`\n\n"
        "## Claims\n"
        + "\n".join(claim_lines)
        + "\n\n## Notes\n"
        + "\n".join(note_lines)
        + "\n\n## Related Changes\n"
        + "\n".join(change_lines)
        + "\n"
    )


def render_global_synthesis(
    snapshot: dict[str, Any],
    atlas_metrics: dict[str, Any],
    docs_gate: dict[str, Any],
    queue: dict[str, list[str]],
) -> str:
    region_lines = []
    sorted_regions = sorted(
        snapshot["by_top_level"].items(),
        key=lambda item: (-item[1], top_level_sort_key(item[0])),
    )
    for name, count in sorted_regions[:10]:
        profile = REGION_PROFILES.get(name)
        if profile:
            region_lines.append(
                f"- `{name}` `{count}` files: {profile['role']}. Pressure point: {profile['risk']}"
            )
        else:
            region_lines.append(f"- `{name}` `{count}` files: visible region without a custom profile yet.")

    queue_pressure = queue.get("P0", [])[:3] + queue.get("P1", [])[:3]
    queue_lines = [f"- {item}" for item in queue_pressure] or ["- queue unavailable"]

    return (
        "# Global Orchestration Synthesis\n\n"
        "The project is not a single manuscript and not a single codebase. It is a compound organism with four main bodies:\n\n"
        "1. live manuscript execution (`Voynich`, `DEEPER CRYSTALIZATION`, `FRESH`)\n"
        "2. formal and archive depth (`MATH` plus ZIP-backed frameworks)\n"
        "3. runtime and retrieval (`self_actualize`, `Trading Bot`, `NERUAL NETWORK`)\n"
        "4. governance and publication (`ECOSYSTEM`, `Athenachka Collective Books`)\n\n"
        "The live atlas now sees "
        f"`{atlas_metrics['live_record_count']}` local records, while the archive atlas exposes "
        f"`{atlas_metrics['archive_record_count']}` additional hidden records. That means the active problem is no longer lack of material. "
        "The active problem is collision management, promotion discipline, and keeping the local and archive bodies in one shared route space.\n\n"
        "The strongest cross-synthesis is this: the repo already knows how to think in queues, claims, receipts, chapters, metro lines, and swarms. "
        "What it lacked was a live board where those abstractions could become the everyday operating surface for many agents at once.\n\n"
        "The current hard external gate remains "
        f"`{docs_gate['status']}`. Until Google Docs is unlocked, the board should treat local markdown and archive-backed evidence as the primary memory body, "
        "and it should record exact blocked queries instead of pretending the live side is available.\n\n"
        "## Region Read\n"
        + "\n".join(region_lines)
        + "\n\n## Current Pressure Fronts\n"
        + "\n".join(queue_lines)
        + "\n"
    )


def render_region_matrix(snapshot: dict[str, Any]) -> str:
    lines = ["# Cross-Region Matrix", ""]
    for name in sorted(snapshot["by_top_level"], key=top_level_sort_key):
        profile = REGION_PROFILES.get(name)
        count = snapshot["by_top_level"][name]
        lines.append(f"## {name}")
        lines.append(f"- Visible files: `{count}`")
        if not profile:
            lines.append("- Role: emergent region")
            lines.append("- Primary edges: not profiled yet")
            lines.append("- Failure mode: unknown")
            lines.append("")
            continue
        lines.append(f"- Role: {profile['role']}")
        for edge in profile["edges"]:
            lines.append(f"- Edge: {edge}")
        lines.append(f"- Failure mode: {profile['risk']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_tensor_overview() -> str:
    return (
        "# Higher-Dimensional Tensor Overview\n\n"
        "The board is a projection surface for the swarm tensor.\n\n"
        "## Coordinate Bundle\n\n"
        "`NSCoord = (Addr4, Scale, Face6, Orbit, Arc, Rail, Hub, Family, Regime, Packet, Truth)`\n\n"
        "## Swarm Tensor\n\n"
        "`SwarmTensor = (Kernel, Elementals, Archetypes, Pantheon, Clusters, Neurons, Families, Waves, Ledgers, Cortex)`\n\n"
        "## Canonical Rule\n\n"
        "No serious front is fully located until it has a family owner, rail, hub, regime, packet class, truth class, and contraction target.\n"
    )


def render_swarm_tensor_stack(
    kernel_state: dict[str, Any],
    elemental_field: list[dict[str, Any]],
    archetypes: list[dict[str, Any]],
    pantheon: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
    neuron_lattice: list[dict[str, Any]],
    councils: list[dict[str, Any]],
) -> str:
    return (
        "# Swarm Tensor Stack\n\n"
        "This board pass explicitly projects the deeper swarm stack into live files.\n\n"
        f"- Kernel: `1` shared zero point (`{kernel_state['kernel_id']}`)\n"
        f"- Elementals: `{len(elemental_field)}` pillars\n"
        f"- Archetypes: `{len(archetypes)}` crystal cells\n"
        f"- Pantheon: `{len(pantheon)}` off-diagonal cells\n"
        f"- Clusters: `{len(clusters)}` task fields\n"
        f"- Neuron leaves: `{len(neuron_lattice)}` truth-addressable microcells\n"
        f"- Councils: `{len(councils)}` family and rail councils\n"
        f"- Legacy hypergraph edges preserved: `{kernel_state['hypergraph_edges']}`\n"
    )


def render_family_tensor_doc(family_tensor: list[dict[str, Any]]) -> str:
    rows = [
        "| Family | Weight | PrimaryRail | PrimaryFace | PreferredScale | PrimaryHub | PreferredRegime | BestFront | PrimaryGanglion | Lineage | Truth |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in family_tensor:
        rows.append(
            "| "
            + " | ".join(
                [
                    f"`{item['family']}`",
                    f"`{item['weight']}`",
                    f"`{item['primary_rail']}`",
                    f"`{item['primary_face']}`",
                    f"`{item['preferred_scale']}`",
                    f"`{item['primary_hub']}`",
                    f"`{item['preferred_regime']}`",
                    item["best_front"],
                    f"`{item['primary_ganglion']}`",
                    f"`{item['lineage']}`",
                    f"`{item['truth']}`",
                ]
            )
            + " |"
        )
    return "# Family Tensor Field\n\n" + "\n".join(rows) + "\n"


def render_thread_coordinates_doc(threads: list[dict[str, Any]]) -> str:
    lines = ["# Thread Coordinates", ""]
    for thread in threads:
        lines.append(f"## {thread['front']}")
        lines.append(f"- Family: `{thread['family']}`")
        lines.append(f"- ArchetypeCell: `{thread['archetype_cell']}`")
        lines.append(f"- ArchetypeRole: {thread['archetype_role']}")
        lines.append(f"- MicroMode: `{thread['micro_mode']}`")
        lines.append(f"- ClusterID: `{thread['cluster_id']}`")
        lines.append(f"- NeuronLeaf: `{thread['neuron_leaf']}`")
        lines.append(f"- Rail: `{thread['rail']}`")
        lines.append(f"- Face: `{thread['face']}`")
        lines.append(f"- Scale: `{thread['scale']}`")
        lines.append(f"- Hub: `{thread['hub']}`")
        lines.append(f"- Regime: `{thread['regime']}`")
        lines.append(f"- Packet: `{thread['packet']}`")
        lines.append(f"- Truth: `{thread['truth']}`")
        lines.append(f"- NSCoord: `{thread['nscoord']}`")
        lines.append(f"- NeuronAddr: `{thread['neuron_addr']}`")
        lines.append(f"- ContractionTarget: `{thread['contraction_target']}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_transfer_hubs_doc(neurons: list[dict[str, Any]]) -> str:
    lines = ["# Transfer Hubs", ""]
    for neuron in neurons:
        lines.append(f"## {neuron['src_family']} -> {neuron['dst_family']}")
        lines.append(f"- Hub: `{neuron['hub']}`")
        lines.append(f"- Operator: {neuron['operator']}")
        lines.append(f"- Truth: `{neuron['truth_class']}`")
        lines.append(f"- ReplayPath: `{neuron['replay_path']}`")
        if neuron["witness_set"]:
            lines.append("- WitnessSet: " + ", ".join(f"`{item}`" for item in neuron["witness_set"]))
        else:
            lines.append("- WitnessSet: none")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_kernel_doc(kernel_state: dict[str, Any]) -> str:
    lines = [
        "# Kernel Zero Point",
        "",
        "The live board now contracts through a kernel surface instead of only through status pages.",
        "",
        f"- KernelID: `{kernel_state['kernel_id']}`",
        f"- DocsGate: `{kernel_state['docs_gate_status']}`",
        f"- CurrentFront: `{kernel_state['current_front']}`",
        f"- PivotFront: `{kernel_state['pivot_front']}`",
        f"- Threads: `{kernel_state['thread_count']}`",
        f"- Pods: `{kernel_state['pod_count']}`",
        f"- Waves: `{', '.join(kernel_state['wave_ids']) if kernel_state['wave_ids'] else 'none'}`",
        f"- LegacyHypergraphEdges: `{kernel_state['hypergraph_edges']}`",
        f"- LegacyNodeTensorNodes: `{kernel_state['node_tensor_nodes']}`",
        f"- LegacyNerveEdges: `{kernel_state['nerve_edges']}`",
        f"- CivilizationTiers: `{kernel_state['tier_count']}`",
        f"- GovernanceSigns: `{kernel_state['sign_count']}`",
        f"- FrontierGaps: `{kernel_state['frontier_gap_count']}`",
        "",
        "## Relay Interfaces",
    ]
    for relay in kernel_state["relay_interfaces"]:
        lines.append(f"- `{relay['id']}` `{relay['status']}` {relay['notes']}")
    if not kernel_state["relay_interfaces"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_elemental_index(elemental_field: list[dict[str, Any]]) -> str:
    lines = [
        "# Elemental Field",
        "",
        "| Element | Role | Threads | Pods | BridgeNeurons |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for item in elemental_field:
        lines.append(
            f"| `{item['element']}` | {item['role']} | `{item['thread_count']}` | `{item['pod_count']}` | `{item['neuron_count']}` |"
        )
    return "\n".join(lines) + "\n"


def render_elemental_doc(item: dict[str, Any]) -> str:
    lines = [
        f"# {item['element']}",
        "",
        f"- Role: {item['role']}",
        f"- ThreadCount: `{item['thread_count']}`",
        f"- PodCount: `{item['pod_count']}`",
        f"- BridgeNeuronCount: `{item['neuron_count']}`",
        "",
        "## Live Threads",
    ]
    lines.extend(f"- `{front}`" for front in item["thread_ids"][:20])
    if not item["thread_ids"]:
        lines.append("- none")
    lines.extend(["", "## Live Pods"])
    lines.extend(f"- `{pod_id}`" for pod_id in item["pod_ids"][:20])
    if not item["pod_ids"]:
        lines.append("- none")
    lines.extend(["", "## Bridge Neurons"])
    lines.extend(f"- `{node_id}`" for node_id in item["neuron_ids"][:20])
    if not item["neuron_ids"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_archetype_grid_doc(archetypes: list[dict[str, Any]]) -> str:
    lines = [
        "# Archetype Grid",
        "",
        "The 16-cell crystal is the native higher-dimensional swarm basis: four diagonal pillars plus twelve off-diagonal archetype cells.",
        "",
        "| Cell | Role | Threads | Pods | MicroModes | Truths |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for item in archetypes:
        micro_modes = ", ".join(f"{mode}:{count}" for mode, count in sorted(item["micro_modes"].items())) or "none"
        truths = ", ".join(f"{truth}:{count}" for truth, count in sorted(item["truths"].items())) or "none"
        lines.append(
            f"| `{item['cell']}` | {item['role']} | `{item['thread_count']}` | `{item['pod_count']}` | `{micro_modes}` | `{truths}` |"
        )
    return "\n".join(lines) + "\n"


def render_archetype_doc(item: dict[str, Any]) -> str:
    micro_modes = ", ".join(f"{mode}:{count}" for mode, count in sorted(item["micro_modes"].items())) or "none"
    truths = ", ".join(f"{truth}:{count}" for truth, count in sorted(item["truths"].items())) or "none"
    lines = [
        f"# Archetype {item['cell']}",
        "",
        f"- Role: {item['role']}",
        f"- ThreadCount: `{item['thread_count']}`",
        f"- PodCount: `{item['pod_count']}`",
        f"- MicroModes: `{micro_modes}`",
        f"- Truths: `{truths}`",
        "",
        "## Live Threads",
    ]
    lines.extend(f"- `{front}`" for front in item["thread_ids"][:20])
    if not item["thread_ids"]:
        lines.append("- none")
    lines.extend(["", "## Live Pods"])
    lines.extend(f"- `{pod_id}`" for pod_id in item["pod_ids"][:20])
    if not item["pod_ids"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_pantheon_doc(pantheon: list[dict[str, Any]]) -> str:
    lines = [
        "# Pantheon Overlay",
        "",
        "The twelve off-diagonal cells are the archetype pantheon. They are where mixed swarm behaviors specialize without collapsing back to the four pillars.",
        "",
    ]
    for item in pantheon:
        lines.append(f"## {item['cell']}")
        lines.append(f"- Role: {item['role']}")
        lines.append(f"- Threads: `{item['thread_count']}`")
        lines.append(f"- Pods: `{item['pod_count']}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_cluster_field_doc(clusters: list[dict[str, Any]]) -> str:
    lines = [
        "# Cluster Field",
        "",
        "The 64-node layer is the 16-cell crystal split again by the four elemental micro-modes.",
        "",
        f"- Total clusters: `{len(clusters)}`",
        f"- Occupied clusters: `{sum(1 for item in clusters if item['occupancy'])}`",
        "",
        "## Most active clusters",
    ]
    active_clusters = [item for item in clusters if item["occupancy"]][:24]
    for item in active_clusters:
        truths = ", ".join(f"{truth}:{count}" for truth, count in sorted(item["truths"].items())) or "none"
        lines.append(
            f"- `{item['cluster_id']}` -> `{item['cell']}` / `{item['micro_mode']}` / occupancy=`{item['occupancy']}` / truths=`{truths}`"
        )
    if not active_clusters:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_neuron_lattice_doc(neuron_lattice: list[dict[str, Any]]) -> str:
    lines = [
        "# Neuron Lattice",
        "",
        "The 256-leaf layer is the 64-node cluster field split again by corridor truth. This is the full 4^4 closure used here: archetype cell x micro-mode x truth class.",
        "",
        f"- Total leaves: `{len(neuron_lattice)}`",
        f"- Occupied leaves: `{sum(1 for item in neuron_lattice if item['occupancy'])}`",
        "",
        "## Active leaves",
    ]
    active_leaves = [item for item in neuron_lattice if item["occupancy"]][:40]
    for item in active_leaves:
        lines.append(
            f"- `{item['leaf_id']}` -> cell=`{item['cell']}` mode=`{item['micro_mode']}` truth=`{item['truth']}` "
            f"threads=`{len(item['thread_ids'])}` bridge_neurons=`{len(item['neuron_ids'])}`"
        )
    if not active_leaves:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_council_index(councils: list[dict[str, Any]]) -> str:
    lines = ["# Council Mesh", ""]
    for council in councils:
        target = council["rail"] or council["family"] or council["id"]
        lines.append(
            f"- `{council['id']}` scope=`{council['scope']}` target=`{target}` live_threads=`{len(council['live_threads'])}` frontier_gaps=`{len(council['frontier_hits'])}`"
        )
    if len(lines) == 2:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_council_doc(council: dict[str, Any]) -> str:
    sign_labels = ", ".join(council["sign_labels"]) or "none"
    lines = [
        f"# {council['id']}",
        "",
        f"- Scope: `{council['scope']}`",
        f"- Label: {council['label']}",
        f"- Family: `{council['family'] or 'n/a'}`",
        f"- Rail: `{council['rail'] or 'n/a'}`",
        f"- ChapterTargets: `{', '.join(council['chapter_targets']) or 'none'}`",
        f"- Signs: `{sign_labels}`",
        "",
        "## Live Threads",
    ]
    lines.extend(f"- `{thread['status']}` `{thread['front']}` ({thread['family']})" for thread in council["live_threads"][:20])
    if not council["live_threads"]:
        lines.append("- none")
    lines.extend(["", "## Frontier Gaps"])
    for frontier in council["frontier_hits"]:
        lines.append(f"- `{frontier['chapter']}` {frontier['title']}")
    if not council["frontier_hits"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_hypergraph_overview(hypergraph: dict[str, Any]) -> str:
    lines = [
        "# Hypergraph Overview",
        "",
        f"- LegacySources: `{hypergraph['source_count']}`",
        f"- LegacyEdges: `{hypergraph['edge_count']}`",
        f"- LiveThreads: `{hypergraph['live_thread_count']}`",
        f"- LiveBridgeNeurons: `{hypergraph['live_bridge_count']}`",
        f"- Councils: `{hypergraph['council_count']}`",
        f"- FrontierGaps: `{len(hypergraph['frontiers'])}`",
        "",
        "## Top Source Families",
    ]
    for family, count in hypergraph["top_families"]:
        lines.append(f"- `{family}` <- `{count}` source bindings")
    if not hypergraph["top_families"]:
        lines.append("- none")
    lines.extend(["", "## Top Chapters"])
    for chapter, count in hypergraph["top_chapters"]:
        lines.append(f"- `{chapter}` <- `{count}` source bindings")
    if not hypergraph["top_chapters"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_edge_kind_breakdown(hypergraph: dict[str, Any]) -> str:
    lines = ["# Hypergraph Edge Breakdown", ""]
    for kind, count in sorted(hypergraph["edge_kinds"].items()):
        lines.append(f"- `{kind}`: `{count}`")
    if len(lines) == 2:
        lines.append("- none")
    lines.extend(["", "## Top Hubs"])
    for hub, count in hypergraph["top_hubs"]:
        lines.append(f"- `{hub}` <- `{count}` chapter bindings")
    if not hypergraph["top_hubs"]:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_frontier_gaps_doc(frontiers: list[dict[str, Any]]) -> str:
    lines = [
        "# Frontier Gaps",
        "",
        "These are the structurally visible chapters that the older swarm runtime still marked as under-supported. They are preserved here so the live board can route into genuine gaps instead of redoing saturated work.",
        "",
    ]
    for frontier in frontiers:
        lines.append(f"## {frontier['chapter']} - {frontier['title']}")
        for record in frontier.get("support_records", [])[:10]:
            lines.append(
                f"- `{record['name']}` from `{record['source_layer']}` score=`{record['score']}`"
            )
        if not frontier.get("support_records"):
            lines.append("- no supporting records listed")
        lines.append("")
    if len(lines) == 4:
        lines.append("- none")
    return "\n".join(lines).strip() + "\n"


def render_swarm_runtime_overview(
    pods: list[dict[str, Any]],
    neurons: list[dict[str, Any]],
    waves: list[dict[str, Any]],
    councils: list[dict[str, Any]],
    hypergraph: dict[str, Any],
) -> str:
    return (
        "# Swarm Runtime Overview\n\n"
        "This runtime treats the workspace as a federated swarm.\n\n"
        f"- Pods: `{len(pods)}`\n"
        f"- Bridge neurons: `{len(neurons)}`\n"
        f"- Active waves: `{len(waves)}`\n\n"
        f"- Councils: `{len(councils)}`\n"
        f"- Hypergraph edges in legacy runtime: `{hypergraph['edge_count']}`\n\n"
        "Every promoted front should leave a pod, a truth class, a contraction target, and a restart seed.\n"
    )


def render_ganglion_doc(item: dict[str, Any], threads: list[dict[str, Any]]) -> str:
    family_threads = [thread for thread in threads if thread["family"] == item["family"]]
    lines = [
        f"# Ganglion `{item['family']}`",
        "",
        f"- Weight: `{item['weight']}`",
        f"- PrimaryRail: `{item['primary_rail']}`",
        f"- PrimaryFace: `{item['primary_face']}`",
        f"- PreferredScale: `{item['preferred_scale']}`",
        f"- PrimaryHub: `{item['primary_hub']}`",
        f"- PreferredRegime: `{item['preferred_regime']}`",
        f"- BestFront: {item['best_front']}",
        "",
        "## Local Threads",
    ]
    if family_threads:
        lines.extend(
            f"- `{thread['status']}` `{thread['front']}` -> `{thread['packet']}` / `{thread['truth']}`"
            for thread in family_threads[:15]
        )
    else:
        lines.append("- no active localized threads")
    lines.append("")
    return "\n".join(lines)


def render_rail_doc(rail_code: str, family_tensor: list[dict[str, Any]], threads: list[dict[str, Any]]) -> str:
    meta = RAIL_DESCRIPTIONS[rail_code]
    families = [item for item in family_tensor if item["primary_rail"] == rail_code]
    owned_threads = [thread for thread in threads if thread["rail"] == rail_code]
    lines = [
        f"# {rail_code} Rail",
        "",
        f"- Name: `{meta['name']}`",
        f"- Role: {meta['role']}",
        "",
        "## Families",
    ]
    lines.extend(f"- `{item['family']}` -> `{item['best_front']}`" for item in families)
    if not families:
        lines.append("- none")
    lines.extend(["", "## Active Threads"])
    lines.extend(f"- `{thread['status']}` `{thread['front']}` ({thread['family']})" for thread in owned_threads[:20])
    if not owned_threads:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_pod_doc(pod: dict[str, Any]) -> str:
    agents = ", ".join(f"`{agent}`" for agent in pod["agents"] if agent) or "none"
    return (
        f"# {pod['pod_id']}\n\n"
        f"- Frontier: `{pod['frontier']}`\n"
        f"- Family: `{pod['family']}`\n"
        f"- ArchetypeCell: `{pod['archetype_cell']}`\n"
        f"- ArchetypeRole: {pod['archetype_role']}\n"
        f"- MicroMode: `{pod['micro_mode']}`\n"
        f"- ClusterID: `{pod['cluster_id']}`\n"
        f"- NeuronLeaf: `{pod['neuron_leaf']}`\n"
        f"- Rail: `{pod['rail']}`\n"
        f"- Status: `{pod['status']}`\n"
        f"- Truth: `{pod['truth']}`\n"
        f"- Hub: `{pod['hub']}`\n"
        f"- Regime: `{pod['regime']}`\n"
        f"- Agents: {agents}\n"
        f"- ContractionTarget: `{pod['contraction_target']}`\n"
        f"- NSCoord: `{pod['nscoord']}`\n"
    )


def render_neuron_doc(neuron: dict[str, Any]) -> str:
    witnesses = ", ".join(f"`{item}`" for item in neuron["witness_set"]) or "none"
    return (
        f"# {neuron['node_id']}\n\n"
        f"- SrcFamily: `{neuron['src_family']}`\n"
        f"- DstFamily: `{neuron['dst_family']}`\n"
        f"- ArchetypeCell: `{neuron['archetype_cell']}`\n"
        f"- ArchetypeRole: {neuron['archetype_role']}\n"
        f"- MicroMode: `{neuron['micro_mode']}`\n"
        f"- ClusterID: `{neuron['cluster_id']}`\n"
        f"- NeuronLeaf: `{neuron['neuron_leaf']}`\n"
        f"- Hub: `{neuron['hub']}`\n"
        f"- Truth: `{neuron['truth_class']}`\n"
        f"- Operator: {neuron['operator']}\n"
        f"- ReplayPath: `{neuron['replay_path']}`\n"
        f"- WitnessSet: {witnesses}\n"
    )


def render_wave_doc(wave: dict[str, Any]) -> str:
    pods = ", ".join(f"`{item}`" for item in wave["active_pods"]) or "none"
    writebacks = "\n".join(f"- `{item}`" for item in wave["writeback_set"])
    return (
        f"# {wave['wave_id']}\n\n"
        f"- Goal: {wave['goal']}\n"
        f"- GateStatus: `{wave['gate_status']}`\n"
        f"- ActivePods: {pods}\n"
        f"- SharedKernel: `{wave['shared_kernel']}`\n"
        f"- StopCondition: {wave['stop_condition']}\n"
        f"- RestartSeed: {wave['restart_seed']}\n\n"
        "## Writeback Set\n"
        f"{writebacks}\n"
    )


def render_active_run_doc(active_run: dict[str, Any]) -> str:
    frontier_lines = "\n".join(f"- {item}" for item in active_run["frontier_update"]) or "- none"
    verify_lines = "\n".join(f"- {item}" for item in active_run["verification_summary"])
    return (
        "# Active Run\n\n"
        f"- GateStatus: `{active_run['gate_status']}`\n"
        f"- ChosenFront: `{active_run['chosen_front']}`\n"
        f"- ChosenFamily: `{active_run['chosen_family']}`\n"
        f"- ChosenNSCoord: `{active_run['chosen_nscoord']}`\n"
        f"- PivotFront: `{active_run['pivot_front']}`\n"
        f"- PivotFamily: `{active_run['pivot_family']}`\n"
        f"- PivotNSCoord: `{active_run['pivot_nscoord']}`\n"
        f"- ArtifactDelta: `{active_run['artifact_delta']}`\n\n"
        "## VerificationSummary\n"
        f"{verify_lines}\n\n"
        "## FrontierUpdate\n"
        f"{frontier_lines}\n"
    )


def render_next_prompt_doc(next_seed: str) -> str:
    return "# Next Self Prompt\n\n## Prompt\n\n```text\n" + next_seed.rstrip() + "\n```\n"


def render_cortex_doc(threads: list[dict[str, Any]], pods: list[dict[str, Any]]) -> str:
    lines = [
        "# Cortex Contraction",
        "",
        "The cortex is the contraction surface for the current swarm pass.",
        "",
        f"- Thread count: `{len(threads)}`",
        f"- Pod count: `{len(pods)}`",
        "",
        "## Strongest reusable fronts",
    ]
    for thread in threads[:10]:
        lines.append(
            f"- `{thread['front']}` -> `{thread['family']}` / `{thread['rail']}` / `{thread['truth']}` / `{thread['contraction_target']}`"
        )
    if len(lines) == 7:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def build_threads(
    notes: list[dict[str, Any]],
    all_claims: dict[str, dict[str, Any]],
    diff: dict[str, Any],
    snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    thread_map: dict[str, dict[str, Any]] = {}

    def ensure_thread(front: str, kind: str) -> dict[str, Any]:
        slug = slugify(front)
        if slug not in thread_map:
            thread_map[slug] = {
                "front": front,
                "front_slug": slug,
                "kind": kind,
                "notes": [],
                "claims": [],
                "changes": [],
                "note_count": 0,
                "claim_count": 0,
                "change_count": 0,
                "status": "monitor",
                "note_paths": [],
                "claim_paths": [],
            }
        return thread_map[slug]

    for note in notes:
        thread = ensure_thread(note["front"], "front")
        thread["notes"].append(note)
        thread["note_paths"].extend(note.get("paths", []))

    for claim in all_claims.values():
        front = claim.get("frontier") or claim.get("front") or claim["claim_id"]
        thread = ensure_thread(front, "front")
        thread["claims"].append(claim)
        thread["claim_paths"].extend(claim.get("paths", []))

    recent_regions = [name for name, _count in list(snapshot["by_top_level"].items())[:10]]
    for region in recent_regions:
        ensure_thread(region, "region")

    for change in diff.get("changes", []):
        region_thread = ensure_thread(change["top_level"], "region")
        region_thread["changes"].append(change)
        for claim in all_claims.values():
            for path in claim.get("paths", []):
                normalized = path.replace("\\", "/")
                if change["relative_path"].startswith(normalized):
                    front = claim.get("frontier") or claim["claim_id"]
                    front_thread = ensure_thread(front, "front")
                    front_thread["changes"].append(change)
                    break

    threads: list[dict[str, Any]] = []
    for thread in thread_map.values():
        thread["notes"].sort(key=lambda item: item.get("updated_at", ""), reverse=True)
        thread["claims"].sort(key=lambda item: item.get("updated_at") or "", reverse=True)
        dedup_changes = {}
        for change in thread["changes"]:
            dedup_changes[(change["kind"], change["relative_path"])] = change
        thread["changes"] = sorted(dedup_changes.values(), key=lambda item: item["mtime_ns"], reverse=True)
        thread["note_count"] = len(thread["notes"])
        thread["claim_count"] = len(thread["claims"])
        thread["change_count"] = len(thread["changes"])
        open_statuses = {claim.get("status") for claim in thread["claims"]}
        if "active" in open_statuses:
            thread["status"] = "active"
        elif "blocked" in open_statuses:
            thread["status"] = "blocked"
        elif "queued" in open_statuses:
            thread["status"] = "queued"
        elif thread["change_count"]:
            thread["status"] = "hot"
        else:
            thread["status"] = "monitor"
        threads.append(thread)

    threads.sort(
        key=lambda item: (
            item["status"] not in {"active", "blocked", "queued", "hot"},
            -item["claim_count"],
            -item["note_count"],
            -item["change_count"],
            item["front_slug"],
        )
    )
    return threads[:40]


def load_event_log() -> list[dict[str, Any]]:
    return read_json(STATE_ROOT / "event_log.json", [])


def update_event_log(snapshot: dict[str, Any], diff: dict[str, Any]) -> list[dict[str, Any]]:
    events = load_event_log()
    event = {
        "detected_at": utc_now(),
        "fingerprint": snapshot["fingerprint"],
        "summary": {
            "added": diff["added"],
            "modified": diff["modified"],
            "removed": diff["removed"],
        },
        "changes": diff.get("changes", [])[:40],
    }
    if not events or events[-1].get("fingerprint") != snapshot["fingerprint"]:
        events.append(event)
    events = events[-200:]
    write_json(STATE_ROOT / "event_log.json", events)
    return events


def refresh_board(snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    if snapshot is None:
        snapshot = scan_workspace()
    previous_snapshot = read_json(STATE_ROOT / "last_snapshot.json", None)
    diff = compute_diff(previous_snapshot, snapshot)

    atlas_metrics = read_atlas_metrics()
    docs_gate = docs_gate_status()
    legacy = load_legacy_manifests()
    queue = parse_queue()
    legacy_claims = parse_legacy_claims()
    board_claims = load_board_claims()
    notes = load_notes()
    all_claims = build_claim_index(board_claims=board_claims, legacy_claims=legacy_claims)
    events = update_event_log(snapshot=snapshot, diff=diff)
    threads = build_threads(notes=notes, all_claims=all_claims, diff=diff, snapshot=snapshot)
    family_tensor = build_family_tensor(snapshot=snapshot, docs_gate=docs_gate)
    threads = annotate_threads(threads=threads, family_tensor=family_tensor, docs_gate=docs_gate)
    pods = build_pods(threads)
    neurons = build_neurons(pods=pods, family_tensor=family_tensor)
    waves = build_waves(pods=pods, docs_gate=docs_gate, diff=diff)
    active_run = build_active_run_manifest(threads=threads, queue=queue, docs_gate=docs_gate, diff=diff)
    kernel_state = build_kernel_state(
        threads=threads,
        pods=pods,
        waves=waves,
        active_run=active_run,
        docs_gate=docs_gate,
        legacy=legacy,
    )
    elemental_field = build_elemental_field(threads=threads, pods=pods, bridge_neurons=neurons)
    archetypes = build_archetype_lattice(threads=threads, pods=pods)
    pantheon = build_pantheon_overlay(archetypes=archetypes)
    clusters = build_cluster_field(threads=threads, pods=pods, bridge_neurons=neurons)
    neuron_lattice = build_neuron_lattice(threads=threads, bridge_neurons=neurons)
    councils = build_council_mesh(legacy=legacy, threads=threads)
    hypergraph = build_hypergraph_projection(
        legacy=legacy,
        threads=threads,
        bridge_neurons=neurons,
        councils=councils,
    )
    next_seed = build_next_seed(active_run=active_run, docs_gate=docs_gate)

    write_text(BOARD_ROOT / "README.md", render_board_readme())
    write_text(PROTOCOL_ROOT / "00_HOW_TO_USE_THIS_BOARD.md", render_protocol_doc())
    write_text(
        STATUS_ROOT / "00_BOARD_STATUS.md",
        render_status_doc(
            snapshot=snapshot,
            diff=diff,
            atlas_metrics=atlas_metrics,
            docs_gate=docs_gate,
            queue=queue,
            all_claims=all_claims,
            notes=notes,
            events=events,
            pods=pods,
            neurons=neurons,
            waves=waves,
            active_run=active_run,
            kernel_state=kernel_state,
            councils=councils,
            clusters=clusters,
            neuron_lattice=neuron_lattice,
            hypergraph=hypergraph,
        ),
    )
    write_json(STATUS_ROOT / "01_SYSTEM_SNAPSHOT.json", snapshot)
    write_text(CHANGE_ROOT / "00_RECENT_CHANGES.md", render_change_feed(diff=diff, events=events))
    write_json(CHANGE_ROOT / "01_CURRENT_BATCH.json", diff)
    write_text(SYNTHESIS_ROOT / "00_GLOBAL_ORCHESTRATION_SYNTHESIS.md", render_global_synthesis(snapshot, atlas_metrics, docs_gate, queue))
    write_text(SYNTHESIS_ROOT / "01_CROSS_REGION_MATRIX.md", render_region_matrix(snapshot))
    write_text(TENSOR_ROOT / "00_TENSOR_OVERVIEW.md", render_tensor_overview())
    write_text(TENSOR_ROOT / "01_FAMILY_TENSOR_FIELD.md", render_family_tensor_doc(family_tensor))
    write_text(TENSOR_ROOT / "02_THREAD_COORDINATES.md", render_thread_coordinates_doc(threads))
    write_text(TENSOR_ROOT / "03_TRANSFER_HUBS.md", render_transfer_hubs_doc(neurons))
    write_text(
        TENSOR_ROOT / "04_SWARM_TENSOR_STACK.md",
        render_swarm_tensor_stack(kernel_state, elemental_field, archetypes, pantheon, clusters, neuron_lattice, councils),
    )
    write_text(TENSOR_ROOT / "05_ARCHETYPE_GRID.md", render_archetype_grid_doc(archetypes))
    write_text(TENSOR_ROOT / "06_PANTHEON_OVERLAY.md", render_pantheon_doc(pantheon))
    write_text(TENSOR_ROOT / "07_CLUSTER_FIELD.md", render_cluster_field_doc(clusters))
    write_text(TENSOR_ROOT / "08_NEURON_LATTICE.md", render_neuron_lattice_doc(neuron_lattice))
    write_text(BOARD_ROOT / "03_CLAIMS" / "00_ACTIVE_CLAIMS.md", render_claim_summary(all_claims))
    write_text(AGENT_ROOT / "INDEX.md", render_agent_index(notes, all_claims))
    write_text(THREAD_ROOT / "INDEX.md", render_thread_index(threads))
    write_text(SWARM_ROOT / "00_SWARM_RUNTIME_OVERVIEW.md", render_swarm_runtime_overview(pods, neurons, waves, councils, hypergraph))
    write_text(KERNEL_ROOT / "00_KERNEL_ZERO_POINT.md", render_kernel_doc(kernel_state))
    write_text(ELEMENTAL_ROOT / "00_ELEMENTAL_FIELD.md", render_elemental_index(elemental_field))
    for element in elemental_field:
        write_text(ELEMENTAL_ROOT / f"{element['element'].upper()}.md", render_elemental_doc(element))
    write_text(ARCHETYPE_ROOT / "00_ARCHETYPE_GRID.md", render_archetype_grid_doc(archetypes))
    for item in archetypes:
        write_text(ARCHETYPE_ROOT / f"ARCHETYPE_{slugify(item['cell'])}.md", render_archetype_doc(item))
    write_text(PANTHEON_ROOT / "00_PANTHEON_OVERLAY.md", render_pantheon_doc(pantheon))
    write_text(CLUSTER_ROOT / "00_CLUSTER_FIELD.md", render_cluster_field_doc(clusters))
    write_text(COUNCIL_ROOT / "INDEX.md", render_council_index(councils))
    for council in councils:
        write_text(COUNCIL_ROOT / f"{slugify(council['id'])}.md", render_council_doc(council))
    write_text(HYPERGRAPH_ROOT / "00_HYPERGRAPH_OVERVIEW.md", render_hypergraph_overview(hypergraph))
    write_text(HYPERGRAPH_ROOT / "01_EDGE_KIND_BREAKDOWN.md", render_edge_kind_breakdown(hypergraph))
    write_text(HYPERGRAPH_ROOT / "02_FRONTIER_GAPS.md", render_frontier_gaps_doc(hypergraph["frontiers"]))
    write_text(MANIFEST_ROOT / "ACTIVE_RUN.md", render_active_run_doc(active_run))
    write_text(MANIFEST_ROOT / "NEXT_SELF_PROMPT.md", render_next_prompt_doc(next_seed))
    write_json(
        MANIFEST_ROOT / "LOOP_STATE.json",
        {
            "generated_at": utc_now(),
            "gate_status": docs_gate["status"],
            "active_run": active_run,
            "next_seed": next_seed,
            "wave_ids": [wave["wave_id"] for wave in waves],
        },
    )
    write_text(CORTEX_ROOT / "00_CORTEX_CONTRACTION.md", render_cortex_doc(threads, pods))

    notes_by_agent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    claims_by_owner: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for note in notes:
        notes_by_agent[note["agent"]].append(note)
    for claim in all_claims.values():
        claims_by_owner[claim.get("owner", "unassigned")].append(claim)

    for agent, agent_notes in notes_by_agent.items():
        agent_slug = slugify(agent)
        inbox_path = AGENT_ROOT / agent_slug / "INBOX.md"
        write_text(inbox_path, render_agent_inbox(agent, agent_notes, claims_by_owner.get(agent, [])))

    for thread in threads:
        thread_dir = THREAD_ROOT / thread["front_slug"]
        write_text(thread_dir / "THREAD.md", render_thread_doc(thread))

    for item in family_tensor:
        write_text(GANGLIA_ROOT / f"GANGLION_{slugify(item['family'])}.md", render_ganglion_doc(item, threads))

    for rail_code in sorted(RAIL_DESCRIPTIONS):
        write_text(RAILS_ROOT / f"{rail_code}_RAIL.md", render_rail_doc(rail_code, family_tensor, threads))

    for pod in pods:
        write_text(POD_ROOT / f"{pod['pod_id']}.md", render_pod_doc(pod))

    for neuron in neurons:
        write_text(NEURON_ROOT / f"{neuron['node_id']}.md", render_neuron_doc(neuron))

    for wave in waves:
        write_text(WAVE_ROOT / f"{wave['wave_id']}.md", render_wave_doc(wave))
        write_json(WAVE_ROOT / f"{wave['wave_id']}.json", wave)

    write_json(STATE_ROOT / "last_snapshot.json", snapshot)
    return {
        "snapshot": snapshot,
        "diff": diff,
        "events": events,
        "thread_count": len(threads),
        "note_count": len(notes),
        "claim_count": len(all_claims),
        "pod_count": len(pods),
        "neuron_count": len(neurons),
        "wave_count": len(waves),
        "council_count": len(councils),
        "cluster_count": len(clusters),
        "neuron_leaf_count": len(neuron_lattice),
        "hypergraph_edge_count": hypergraph["edge_count"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Realtime swarm board for the Athena workspace.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="Refresh the board once from the current workspace state.")

    watch = subparsers.add_parser("watch", help="Poll the workspace and refresh the board when changes land.")
    watch.add_argument("--interval", type=float, default=15.0, help="Seconds between scans.")
    watch.add_argument("--max-cycles", type=int, default=0, help="Optional cap for test runs.")

    note = subparsers.add_parser("note", help="Create an agent note and refresh the board.")
    note.add_argument("--agent", required=True, help="Agent name for the note.")
    note.add_argument("--front", required=True, help="Front or thread this note belongs to.")
    note.add_argument("--status", default="active", help="Note status, for example active or done.")
    note.add_argument("--message", required=True, help="The note body.")
    note.add_argument("--path", action="append", default=[], help="Optional related workspace path.")

    claim = subparsers.add_parser("claim", help="Create or update a frontier claim.")
    claim.add_argument("--claim-id", help="Existing claim id to update.")
    claim.add_argument("--agent", required=True, help="Agent taking or updating the claim.")
    claim.add_argument("--front", required=True, help="Frontier label.")
    claim.add_argument("--level", required=True, help="Scope such as file, folder, framework, or ecosystem.")
    claim.add_argument("--output-target", required=True, help="Intended output path or surface.")
    claim.add_argument("--receipt", required=True, help="Receipt target or status marker.")
    claim.add_argument("--status", default="active", help="Claim status.")
    claim.add_argument("--message", required=True, help="Claim note or handoff detail.")
    claim.add_argument("--path", action="append", default=[], help="Optional related workspace path.")

    return parser.parse_args()


def command_build() -> int:
    result = refresh_board()
    diff = result["diff"]
    print(
        "Board refreshed at "
        f"{result['snapshot']['generated_at']} "
        f"(+{diff['added']} ~{diff['modified']} -{diff['removed']}, "
        f"{result['claim_count']} claims, {result['note_count']} notes)."
    )
    print(f"Board root: {BOARD_ROOT}")
    return 0


def command_watch(interval: float, max_cycles: int) -> int:
    cycles = 0
    last_fingerprint = None
    while True:
        snapshot = scan_workspace()
        fingerprint = snapshot["fingerprint"]
        if fingerprint != last_fingerprint:
            result = refresh_board(snapshot=snapshot)
            diff = result["diff"]
            print(
                "Observed change batch "
                f"+{diff['added']} ~{diff['modified']} -{diff['removed']} "
                f"at {result['snapshot']['generated_at']}"
            )
            last_fingerprint = fingerprint
        cycles += 1
        if max_cycles and cycles >= max_cycles:
            break
        time.sleep(interval)
    return 0


def command_note(agent: str, front: str, status: str, message: str, paths: list[str]) -> int:
    note = create_note(agent=agent, front=front, status=status, message=message, paths=paths)
    refresh_board()
    print(f"Created note {note['note_id']} at {note['md_path']}")
    return 0


def command_claim(
    claim_id: str | None,
    agent: str,
    front: str,
    level: str,
    output_target: str,
    receipt: str,
    status: str,
    message: str,
    paths: list[str],
) -> int:
    claim = create_or_update_claim(
        agent=agent,
        front=front,
        level=level,
        output_target=output_target,
        receipt=receipt,
        status=status,
        message=message,
        paths=paths,
        claim_id=claim_id,
    )
    refresh_board()
    print(f"Wrote claim {claim['claim_id']} at {claim['md_path']}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "build":
        return command_build()
    if args.command == "watch":
        return command_watch(interval=args.interval, max_cycles=args.max_cycles)
    if args.command == "note":
        return command_note(
            agent=args.agent,
            front=args.front,
            status=args.status,
            message=args.message,
            paths=args.path,
        )
    if args.command == "claim":
        return command_claim(
            claim_id=args.claim_id,
            agent=args.agent,
            front=args.front,
            level=args.level,
            output_target=args.output_target,
            receipt=args.receipt,
            status=args.status,
            message=args.message,
            paths=args.path,
        )
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
