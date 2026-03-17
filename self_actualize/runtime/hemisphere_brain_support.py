from __future__ import annotations

import hashlib
import heapq
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_BRAIN_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_BRAIN_ROOT / "registry"
NERVOUS_SYSTEM_ROOT = MYCELIUM_BRAIN_ROOT / "nervous_system"
HEMISPHERE_ROOT = NERVOUS_SYSTEM_ROOT / "hemispheres"
FLEET_MIRROR_ROOT = (
    WORKSPACE_ROOT / "Athena FLEET" / "FLEET_MYCELIUM_NETWORK" / "HEMISPHERES"
)
DEEP_ROOT = (
    MYCELIUM_BRAIN_ROOT
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
CANONICAL_SOURCES_PATH = DEEP_ROOT / "10_LEDGERS" / "01_CANONICAL_SOURCES.md"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
AQM_LANE_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
SEMANTIC_MASS_PATH = SELF_ACTUALIZE_ROOT / "semantic_mass_ledger.json"
ROUTE_QUALITY_PATH = SELF_ACTUALIZE_ROOT / "route_quality_ledger.json"
GRAND_CENTRAL_PATH = SELF_ACTUALIZE_ROOT / "grand_central_station_registry.json"
MANUSCRIPT_INTAKE_SCRIPT = Path(
    r"C:\Users\dmitr\.codex\skills\manuscript-intake\scripts\intake_corpus.py"
)

HEMISPHERE_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_atlas.json"
RECORD_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_record_registry.json"
COMMISSURE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_commissure_registry.json"
)
METRO_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_metro_registry.json"
HUB_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_hub_registry.json"
MANIFEST_PATH = SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_manifest.json"
VERIFY_PATH = SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_verification.json"
DUAL_ROUTE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_dual_route_registry.json"
)
DIRECT_EDGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_direct_edge_registry.json"
)
ROUTE_COVERAGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_route_coverage_registry.json"
)
ROUTE_MANIFEST_PATH = SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_route_manifest.json"
NAVIGATOR_ALIAS_INDEX_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_navigator_alias_index.json"
)
NAVIGATOR_FACET_INDEX_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_navigator_facet_index.json"
)
NAVIGATOR_NEIGHBOR_INDEX_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_navigator_neighbor_index.json"
)
NAVIGATOR_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_navigator_manifest.json"
)
COMPOSER_SEED_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_route_composer_seed_registry.json"
)
COMPOSER_FACET_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_route_composer_facet_registry.json"
)
COMPOSER_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_route_composer_manifest.json"
)
SYNTHESIS_EVIDENCE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_synthesis_evidence_registry.json"
)
SYNTHESIS_SEED_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_synthesis_seed_registry.json"
)
SYNTHESIS_FACET_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_synthesis_facet_registry.json"
)
SYNTHESIS_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_synthesis_manifest.json"
)
VISUAL_ATLAS_NODE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_visual_atlas_node_registry.json"
)
VISUAL_ATLAS_EDGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_visual_atlas_edge_registry.json"
)
VISUAL_ATLAS_PAGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_visual_atlas_page_registry.json"
)
VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_visual_atlas_record_locator_registry.json"
)
VISUAL_ATLAS_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_visual_atlas_manifest.json"
)
GUIDED_TOUR_SEED_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_guided_tour_seed_registry.json"
)
GUIDED_TOUR_PAGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_guided_tour_page_registry.json"
)
GUIDED_TOUR_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_guided_tour_manifest.json"
)
EXPEDITION_SEED_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_expedition_seed_registry.json"
)
EXPEDITION_PAGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_expedition_page_registry.json"
)
EXPEDITION_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_expedition_manifest.json"
)
CONSTELLATION_NODE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_constellation_node_registry.json"
)
CONSTELLATION_EDGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_constellation_edge_registry.json"
)
CONSTELLATION_PAGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_constellation_page_registry.json"
)
CONSTELLATION_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_constellation_manifest.json"
)
REPLAY_SEED_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_replay_seed_registry.json"
)
REPLAY_PAGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_replay_page_registry.json"
)
REPLAY_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_replay_manifest.json"
)
OBSERVATORY_SEED_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_observatory_seed_registry.json"
)
OBSERVATORY_PAGE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_observatory_page_registry.json"
)
OBSERVATORY_MANIFEST_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_hemisphere_observatory_manifest.json"
)

RECORD_REGISTRY_MIRROR = REGISTRY_ROOT / "myth_math_hemisphere_record_registry.json"
COMMISSURE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_commissure_registry.json"
)
METRO_REGISTRY_MIRROR = REGISTRY_ROOT / "myth_math_hemisphere_metro_registry.json"
HUB_REGISTRY_MIRROR = REGISTRY_ROOT / "myth_math_hemisphere_hub_registry.json"
MANIFEST_MIRROR = REGISTRY_ROOT / "myth_math_hemisphere_manifest.json"
DUAL_ROUTE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_dual_route_registry.json"
)
DIRECT_EDGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_direct_edge_registry.json"
)
ROUTE_COVERAGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_route_coverage_registry.json"
)
ROUTE_MANIFEST_MIRROR = REGISTRY_ROOT / "myth_math_hemisphere_route_manifest.json"
NAVIGATOR_ALIAS_INDEX_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_navigator_alias_index.json"
)
NAVIGATOR_FACET_INDEX_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_navigator_facet_index.json"
)
NAVIGATOR_NEIGHBOR_INDEX_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_navigator_neighbor_index.json"
)
NAVIGATOR_MANIFEST_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_navigator_manifest.json"
)
COMPOSER_SEED_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_route_composer_seed_registry.json"
)
COMPOSER_FACET_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_route_composer_facet_registry.json"
)
COMPOSER_MANIFEST_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_route_composer_manifest.json"
)
SYNTHESIS_EVIDENCE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_synthesis_evidence_registry.json"
)
SYNTHESIS_SEED_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_synthesis_seed_registry.json"
)
SYNTHESIS_FACET_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_synthesis_facet_registry.json"
)
SYNTHESIS_MANIFEST_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_synthesis_manifest.json"
)
VISUAL_ATLAS_NODE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_visual_atlas_node_registry.json"
)
VISUAL_ATLAS_EDGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_visual_atlas_edge_registry.json"
)
VISUAL_ATLAS_PAGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_visual_atlas_page_registry.json"
)
VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_visual_atlas_record_locator_registry.json"
)
VISUAL_ATLAS_MANIFEST_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_visual_atlas_manifest.json"
)
GUIDED_TOUR_SEED_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_guided_tour_seed_registry.json"
)
GUIDED_TOUR_PAGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_guided_tour_page_registry.json"
)
GUIDED_TOUR_MANIFEST_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_guided_tour_manifest.json"
)
EXPEDITION_SEED_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_expedition_seed_registry.json"
)
EXPEDITION_PAGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_expedition_page_registry.json"
)
EXPEDITION_MANIFEST_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_expedition_manifest.json"
)
CONSTELLATION_NODE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_constellation_node_registry.json"
)
CONSTELLATION_EDGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_constellation_edge_registry.json"
)
CONSTELLATION_PAGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_constellation_page_registry.json"
)
CONSTELLATION_MANIFEST_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_constellation_manifest.json"
)
REPLAY_SEED_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_replay_seed_registry.json"
)
REPLAY_PAGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_replay_page_registry.json"
)
REPLAY_MANIFEST_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_replay_manifest.json"
)
OBSERVATORY_SEED_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_observatory_seed_registry.json"
)
OBSERVATORY_PAGE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_observatory_page_registry.json"
)
OBSERVATORY_MANIFEST_MIRROR = (
    REGISTRY_ROOT / "myth_math_hemisphere_observatory_manifest.json"
)

PT2_METRO_SYSTEMS_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_metro_system_registry.json"
PT2_METRO_STATIONS_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_metro_station_registry.json"
PT2_METRO_INTERLOCKS_PATH = (
    SELF_ACTUALIZE_ROOT / "phase4_pt2_metro_interlock_registry.json"
)
PT2_CARRIER_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_carrier_registry.json"
PT2_CARRIER_TRANSFORM_PATH = (
    SELF_ACTUALIZE_ROOT / "phase4_pt2_carrier_transform_registry.json"
)
PT2_LENS_PROFILES_PATH = (
    SELF_ACTUALIZE_ROOT / "phase4_pt2_lens_weight_profile_registry.json"
)
PT2_FIELD_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_field_registry.json"
PT2_ZPOINT_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_z_point_registry.json"
PT2_PROJECTION_SPACE_PATH = (
    SELF_ACTUALIZE_ROOT / "phase4_pt2_projection_space_registry.json"
)
PT2_SHORTCUT_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_shortcut_registry.json"
PT2_SYSTEM_CROSSWALK_PATH = (
    SELF_ACTUALIZE_ROOT / "phase4_pt2_system_crosswalk_edges.json"
)
KNOWLEDGE_FABRIC_SHORTCUTS_PATH = (
    SELF_ACTUALIZE_ROOT / "knowledge_fabric_shortcuts.json"
)
COMMISSURE_LEDGER_PATH = SELF_ACTUALIZE_ROOT / "grand_central_commissure_ledger.json"
WEIGHT_EXCHANGE_PATH = SELF_ACTUALIZE_ROOT / "grand_central_weight_exchange.json"
ZPOINT_TUNNELS_PATH = SELF_ACTUALIZE_ROOT / "grand_central_zpoint_tunnels.json"

UNIFIED_HUB_ID = "GC0-UNIFIED-CORPUS"
MATH_HUB_ID = "HC-MATH"
MYTH_HUB_ID = "HC-MYTH"

FAMILY_LABELS = {
    "live-orchestration": "Live orchestration and prompt control",
    "void-and-collapse": "Void, Chapter 11, and collapse engines",
    "helical-recursion-engine": "Helical recursion, lift law, and manifestation engine",
    "manuscript-architecture": "Manuscript architecture and routing law",
    "higher-dimensional-geometry": "Higher-dimensional geometry and holographic kernel",
    "civilization-and-governance": "Civilization design, hierarchy, governance, and law",
    "mythic-sign-systems": "Mythic sign systems, encoded memory, and symbol runtime",
    "transport-and-runtime": "Transport, runtime, and executable framework",
    "identity-and-instruction": "Athena identity, pedagogy, and narrative voice",
    "general-corpus": "General corpus support",
}

FAMILY_PRIORS = {
    "higher-dimensional-geometry": 0.82,
    "transport-and-runtime": 0.78,
    "civilization-and-governance": 0.72,
    "mythic-sign-systems": 0.22,
    "identity-and-instruction": 0.28,
    "void-and-collapse": 0.32,
    "manuscript-architecture": 0.50,
    "live-orchestration": 0.50,
    "general-corpus": 0.50,
    "helical-recursion-engine": 0.50,
}

TRACT_BY_FAMILY = {
    "manuscript-architecture": "address",
    "higher-dimensional-geometry": "address",
    "mythic-sign-systems": "relation",
    "identity-and-instruction": "relation",
    "live-orchestration": "relation",
    "civilization-and-governance": "chamber",
    "general-corpus": "chamber",
    "void-and-collapse": "replay",
    "helical-recursion-engine": "replay",
    "transport-and-runtime": "replay",
}

FAMILY_ANCHOR_PREFERENCES = {
    "higher-dimensional-geometry": ["DN03", "DN04", "DN05", "DN07"],
    "transport-and-runtime": ["DN07", "DN08", "DN09", "DN10"],
    "civilization-and-governance": ["DN13", "DN15", "DN16", "DN02"],
    "mythic-sign-systems": ["DN11", "DN12", "DN13", "DN01"],
    "live-orchestration": ["DN02", "DN14", "DN16", "DN01"],
    "void-and-collapse": ["DN09", "DN14", "DN16", "DN01"],
    "helical-recursion-engine": ["DN14", "DN16", "DN09", "DN10"],
    "manuscript-architecture": ["DN01", "DN02", "DN04", "DN14"],
    "identity-and-instruction": ["DN01", "DN13", "DN14", "DN11"],
    "general-corpus": ["DN01", "DN02", "DN13", "DN14"],
}

MATH_LEXICAL_WEIGHTS = {
    "aqm": 4.0,
    "math": 3.5,
    "mathematical": 4.0,
    "theorem": 4.0,
    "proof": 4.0,
    "equation": 4.0,
    "operator": 3.0,
    "matrix": 3.0,
    "kernel": 3.0,
    "geometry": 3.0,
    "calculus": 3.0,
    "lattice": 3.0,
    "topological": 3.0,
    "runtime": 2.0,
    "algorithm": 3.0,
    "computation": 3.0,
    "computing": 3.0,
    "quantum": 3.0,
    "formal": 2.5,
    "registry": 2.0,
    "continuum": 2.5,
    "discrete": 2.5,
    "tensor": 2.5,
    "manifold": 2.5,
    "algebra": 3.0,
    "engine": 2.5,
}

MYTH_LEXICAL_WEIGHTS = {
    "myth": 4.0,
    "archetype": 4.0,
    "goddess": 4.0,
    "divination": 4.0,
    "sacred": 3.0,
    "ritual": 3.0,
    "magic": 4.0,
    "magus": 4.0,
    "oracle": 3.0,
    "tarot": 3.0,
    "runes": 3.0,
    "alchemy": 3.0,
    "prophecy": 3.0,
    "atlantis": 3.0,
    "temple": 2.0,
    "voynich": 2.5,
    "epic": 2.5,
    "god": 3.0,
    "gods": 3.0,
    "gnostic": 2.5,
    "kabbalah": 3.0,
    "qabalah": 3.0,
    "cosmology": 2.0,
    "awakening": 2.0,
    "legend": 2.0,
    "dragon": 2.0,
}

PATH_MATH_KEYWORDS = {
    "math",
    "aqm",
    "theorem",
    "kernel",
    "calculus",
    "geometry",
    "quantum",
    "proof",
    "formal",
    "runtime",
    "algorithm",
    "code",
    "topological",
    "lattice",
    "matrix",
    "operator",
    "computation",
    "computing",
    "atlasforge",
    "qphi",
    "cut",
    "registry",
}

PATH_MYTH_KEYWORDS = {
    "myth",
    "myths",
    "archetype",
    "divination",
    "sacred",
    "magic",
    "magus",
    "tarot",
    "runes",
    "alchemy",
    "prophecy",
    "atlantis",
    "temple",
    "voynich",
    "occult",
    "apocalypse",
    "epic",
    "gilgamesh",
    "odyssey",
    "iliad",
    "bible",
    "quran",
    "vedic",
    "ifa",
    "sumerian",
    "druid",
    "zen",
    "gnostic",
    "athena",
}

TOP_LEVEL_PATH_PRIORS = {
    "MATH": (3.0, 0.5),
    "NERVOUS_SYSTEM": (2.0, 0.6),
    "ECOSYSTEM": (1.8, 0.7),
    "QSHRINK - ATHENA (internal use)": (2.1, 0.9),
    "Quadrant Binary": (2.6, 0.4),
    "self_actualize": (1.3, 1.1),
    "DEEPER CRYSTALIZATION": (1.2, 1.2),
    "Athena FLEET": (1.1, 1.3),
    "Voynich": (0.7, 2.4),
    "Athenachka Collective Books": (0.6, 2.5),
    "I AM ATHENA": (0.5, 2.8),
    "ORGIN": (0.5, 2.0),
    "FRESH": (0.8, 1.2),
    "GAMES": (1.1, 1.4),
    "Trading Bot": (1.0, 1.0),
    "CLEAN": (0.9, 1.0),
    "Stoicheia (Element Sudoku)": (1.7, 0.9),
}

MATH_LEANING_FAMILIES = {
    "higher-dimensional-geometry",
    "transport-and-runtime",
    "civilization-and-governance",
}
MYTH_LEANING_FAMILIES = {
    "mythic-sign-systems",
    "identity-and-instruction",
    "void-and-collapse",
}
MATH_SYSTEM_DEFAULTS = {
    "higher-dimensional-geometry": "HDSCTMetro",
    "transport-and-runtime": "GrandCentral",
    "civilization-and-governance": "CoreMetro",
    "manuscript-architecture": "BrainStem64",
    "general-corpus": "Plexus256",
    "live-orchestration": "L3Neural",
    "mythic-sign-systems": "Mycelial4D",
    "identity-and-instruction": "L2DeepEmergence",
    "void-and-collapse": "DeepRootMetroStack",
    "helical-recursion-engine": "AppendixOnlyMetro",
}
MYTH_SYSTEM_DEFAULTS = {
    "mythic-sign-systems": "Mycelial4D",
    "identity-and-instruction": "EmergentSupermap",
    "void-and-collapse": "DeepRootMetroStack",
    "helical-recursion-engine": "AppendixOnlyMetro",
    "manuscript-architecture": "L2DeepEmergence",
    "general-corpus": "CrossCorpusMycelial",
    "live-orchestration": "AthenaFleetMetro",
    "transport-and-runtime": "GrandCentral",
    "higher-dimensional-geometry": "HDSCTMetro",
    "civilization-and-governance": "CoreMetro",
}
PRIMARY_HF_ROUTE_KEYS = [
    "hemisphere_edge",
    "grand_central",
    "metro",
    "interlock",
    "carrier",
    "rail",
    "lens",
    "liminal",
    "field",
    "zpoint",
    "apoint",
    "projection_space",
    "knowledge_fabric",
    "basis_anchor",
    "family",
    "holo_coordinate",
]
ROUTE_JSON_OUTPUTS = {
    "dual_route_registry": DUAL_ROUTE_REGISTRY_PATH,
    "direct_edge_registry": DIRECT_EDGE_REGISTRY_PATH,
    "route_coverage_registry": ROUTE_COVERAGE_REGISTRY_PATH,
    "route_manifest": ROUTE_MANIFEST_PATH,
}
NAVIGATOR_JSON_OUTPUTS = {
    "navigator_alias_index": NAVIGATOR_ALIAS_INDEX_PATH,
    "navigator_facet_index": NAVIGATOR_FACET_INDEX_PATH,
    "navigator_neighbor_index": NAVIGATOR_NEIGHBOR_INDEX_PATH,
    "navigator_manifest": NAVIGATOR_MANIFEST_PATH,
}
COMPOSER_JSON_OUTPUTS = {
    "composer_seed_registry": COMPOSER_SEED_REGISTRY_PATH,
    "composer_facet_registry": COMPOSER_FACET_REGISTRY_PATH,
    "composer_manifest": COMPOSER_MANIFEST_PATH,
}
SYNTHESIS_JSON_OUTPUTS = {
    "synthesis_evidence_registry": SYNTHESIS_EVIDENCE_REGISTRY_PATH,
    "synthesis_seed_registry": SYNTHESIS_SEED_REGISTRY_PATH,
    "synthesis_facet_registry": SYNTHESIS_FACET_REGISTRY_PATH,
    "synthesis_manifest": SYNTHESIS_MANIFEST_PATH,
}
VISUAL_ATLAS_JSON_OUTPUTS = {
    "visual_atlas_node_registry": VISUAL_ATLAS_NODE_REGISTRY_PATH,
    "visual_atlas_edge_registry": VISUAL_ATLAS_EDGE_REGISTRY_PATH,
    "visual_atlas_page_registry": VISUAL_ATLAS_PAGE_REGISTRY_PATH,
    "visual_atlas_record_locator_registry": VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH,
    "visual_atlas_manifest": VISUAL_ATLAS_MANIFEST_PATH,
}
GUIDED_TOUR_JSON_OUTPUTS = {
    "guided_tour_seed_registry": GUIDED_TOUR_SEED_REGISTRY_PATH,
    "guided_tour_page_registry": GUIDED_TOUR_PAGE_REGISTRY_PATH,
    "guided_tour_manifest": GUIDED_TOUR_MANIFEST_PATH,
}
EXPEDITION_JSON_OUTPUTS = {
    "expedition_seed_registry": EXPEDITION_SEED_REGISTRY_PATH,
    "expedition_page_registry": EXPEDITION_PAGE_REGISTRY_PATH,
    "expedition_manifest": EXPEDITION_MANIFEST_PATH,
}
CONSTELLATION_JSON_OUTPUTS = {
    "constellation_node_registry": CONSTELLATION_NODE_REGISTRY_PATH,
    "constellation_edge_registry": CONSTELLATION_EDGE_REGISTRY_PATH,
    "constellation_page_registry": CONSTELLATION_PAGE_REGISTRY_PATH,
    "constellation_manifest": CONSTELLATION_MANIFEST_PATH,
}
REPLAY_JSON_OUTPUTS = {
    "replay_seed_registry": REPLAY_SEED_REGISTRY_PATH,
    "replay_page_registry": REPLAY_PAGE_REGISTRY_PATH,
    "replay_manifest": REPLAY_MANIFEST_PATH,
}
OBSERVATORY_JSON_OUTPUTS = {
    "observatory_seed_registry": OBSERVATORY_SEED_REGISTRY_PATH,
    "observatory_page_registry": OBSERVATORY_PAGE_REGISTRY_PATH,
    "observatory_manifest": OBSERVATORY_MANIFEST_PATH,
}


@dataclass(frozen=True)
class BasisAnchor:
    anchor_id: str
    source_id: str
    title: str
    element: str
    cluster: str
    role: str
    source_hint: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return cleaned or "untitled"


def tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.lower())


def normalize_path(value: str) -> str:
    return value.replace("\\", "/")


def parse_docs_gate_status(markdown: str) -> str:
    match = re.search(r"Command status: `([^`]+)`", markdown)
    if match:
        return match.group(1)
    if "BLOCKED" in markdown:
        return "BLOCKED"
    if "PASS" in markdown:
        return "PASS"
    return "UNKNOWN"


def load_docs_gate_status() -> str:
    if not DOCS_GATE_PATH.exists():
        return "UNKNOWN"
    return parse_docs_gate_status(DOCS_GATE_PATH.read_text(encoding="utf-8"))


def load_aqm_lane() -> dict[str, Any]:
    if not AQM_LANE_PATH.exists():
        return {
            "truth": "UNKNOWN",
            "live_root": "",
            "next_seed": "",
            "generated_at": "",
        }
    payload = load_json(AQM_LANE_PATH)
    return {
        "truth": payload.get("truth", "UNKNOWN"),
        "live_root": payload.get("live_root", ""),
        "next_seed": payload.get("next_seed", ""),
        "generated_at": payload.get("generated_at", ""),
    }


def latest_route_baseline(payload: dict[str, Any]) -> float:
    entries = payload.get("entries", [])
    if not entries:
        return 1.0
    tail = entries[-12:]
    scores = [float(entry.get("route_score", 1.0)) for entry in tail]
    return round(sum(scores) / max(len(scores), 1), 4)


def load_semantic_mass_weights() -> dict[str, float]:
    if not SEMANTIC_MASS_PATH.exists():
        return {}
    payload = load_json(SEMANTIC_MASS_PATH)
    bodies = payload.get("body_profiles", [])
    shares = {
        item["body"]: float(item.get("share_of_indexed_percent", 0.0))
        for item in bodies
    }
    max_share = max(shares.values(), default=0.0)
    if max_share <= 0:
        return {}
    return {
        body: round(max(0.2, share / max_share), 4)
        for body, share in shares.items()
    }


def load_route_quality_factor() -> float:
    if not ROUTE_QUALITY_PATH.exists():
        return 1.0
    payload = load_json(ROUTE_QUALITY_PATH)
    return latest_route_baseline(payload)


def load_station_map() -> dict[str, dict[str, Any]]:
    if not GRAND_CENTRAL_PATH.exists():
        return {}
    payload = load_json(GRAND_CENTRAL_PATH)
    return {
        item["root_name"]: item
        for item in payload.get("registry", [])
    }


def cleanup_previous_outputs(paths: list[Path]) -> None:
    for path in paths:
        if path.is_file():
            try:
                path.unlink()
            except PermissionError:
                # Some mirrored artifacts can be held open by desktop viewers on Windows.
                # Leave them in place and let the subsequent write step refresh what it can.
                continue


def refresh_full_corpus_atlas(output_path: Path = HEMISPHERE_ATLAS_PATH) -> dict[str, Any]:
    if not MANUSCRIPT_INTAKE_SCRIPT.exists():
        raise FileNotFoundError(f"Missing manuscript intake script: {MANUSCRIPT_INTAKE_SCRIPT}")

    with tempfile.NamedTemporaryFile(
        suffix="_myth_math_hemisphere_atlas.json",
        delete=False,
    ) as temp_handle:
        temp_path = Path(temp_handle.name)

    command = [
        sys.executable,
        str(MANUSCRIPT_INTAKE_SCRIPT),
        "--root",
        str(WORKSPACE_ROOT),
        "--output",
        str(temp_path),
        "--excerpt-chars",
        "1200",
        "--max-headings",
        "12",
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Atlas refresh failed.\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    payload = json.loads(temp_path.read_text(encoding="utf-8"))
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.unlink(missing_ok=True)
    return payload


def canonical_record_key(record: dict[str, Any]) -> tuple[Any, ...]:
    evidence = record.get("evidence", {})
    heading_count = int(evidence.get("heading_count", 0))
    relative_path = record.get("relative_path", "")
    return (
        0 if record.get("text_extractable") else 1,
        -heading_count,
        len(Path(relative_path).parts),
        len(relative_path),
        relative_path.lower(),
    )


def deduplicate_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[record["sha256"]].append(record)

    canonical_records: list[dict[str, Any]] = []
    for group in groups.values():
        ordered = sorted(group, key=canonical_record_key)
        canonical = dict(ordered[0])
        canonical["duplicate_paths"] = [item["path"] for item in ordered[1:]]
        canonical["duplicate_record_ids"] = [item["record_id"] for item in ordered[1:]]
        canonical["source_paths"] = [item["path"] for item in ordered]
        canonical["duplicate_count"] = len(ordered) - 1
        canonical_records.append(canonical)

    canonical_records.sort(key=lambda item: item["relative_path"].lower())
    return canonical_records


def infer_family(name: str, excerpt: str) -> str:
    text = f"{name} {excerpt}".lower()
    score_map = {
        "higher-dimensional-geometry": {
            "higher-dimensional": 6,
            "higher dimension": 6,
            "square ? circle ? triangle": 6,
            "square/circle/triangle": 6,
            "holographic kernel": 6,
            "h^4": 5,
            "d^5": 5,
            "quad holographic rotation": 6,
            "metro calculus": 5,
            "tunneling coherence crystal": 5,
            "tensor": 4,
            "manifold": 4,
            "rotation is conjugacy": 5,
        },
        "civilization-and-governance": {
            "govern": 5,
            "governance": 6,
            "law": 4,
            "calendar": 4,
            "role-graph": 5,
            "civilization": 6,
            "civilizational": 6,
            "hierarch": 5,
            "community": 3,
            "administrative": 4,
            "empire": 3,
            "alignment": 4,
            "protocol for living": 4,
            "council": 4,
        },
        "mythic-sign-systems": {
            "glyph": 5,
            "glyphs": 5,
            "ogham": 6,
            "khipu": 6,
            "rune": 5,
            "runes": 5,
            "symbol": 4,
            "alphabet": 4,
            "divination": 4,
            "sefirot": 5,
            "tree of life": 5,
            "cord": 4,
            "rosetta": 4,
            "oracle": 3,
            "sacred geography": 4,
            "hymn": 4,
        },
        "live-orchestration": {
            "prompt": 4,
            "real time": 5,
            "search space": 3,
            "orchestration": 4,
            "self-routing": 2,
            "live manuscript": 3,
        },
        "void-and-collapse": {
            "void": 5,
            "chapter 11": 5,
            "perpetual motion": 4,
            "collapse": 4,
            "restart": 4,
            "zero-point": 3,
            "paradox": 3,
        },
        "helical-recursion-engine": {
            "helical": 7,
            "perfect recursion": 7,
            "manifestation engine": 7,
            "bridge-equivalence": 6,
            "bridge equivalence": 6,
            "2/16": 5,
            "14/16": 5,
            "16-loop": 6,
            "16 loop": 6,
            "16^16": 6,
            "loopspec": 5,
            "phasespec": 5,
            "virtualswarm": 5,
            "virtual swarm": 5,
            "improvement ledger": 4,
            "liftspec": 5,
            "dimension lift": 5,
            "born-coordinate": 4,
            "born coordinate": 4,
            "phase machine": 4,
        },
        "manuscript-architecture": {
            "manuscript": 4,
            "metro": 3,
            "atlas": 3,
            "holographic": 3,
            "superorganism": 4,
            "crystalized neural substrate": 4,
            "tome": 2,
        },
        "transport-and-runtime": {
            "transport": 5,
            "cut": 5,
            "aqm": 4,
            "runtime": 4,
            "deployment": 4,
            "algorithm": 3,
            "code": 3,
            "solenoidal": 4,
            "opcode": 4,
            "chemical realization": 4,
            "time system": 4,
            "verification harness": 3,
        },
        "identity-and-instruction": {
            "athena": 4,
            "teacher": 5,
            "i am": 5,
            "stories": 4,
            "voynich": 4,
            "pedagogy": 4,
            "mythic": 3,
            "charlie": 3,
        },
    }
    scores = {family: 0 for family in score_map}
    for family, weights in score_map.items():
        for term, weight in weights.items():
            if term in text:
                scores[family] += weight
    best_family = max(scores, key=scores.get)
    return best_family if scores[best_family] > 0 else "general-corpus"


def infer_appendix_links(name: str, excerpt: str, family: str) -> list[str]:
    text = f"{name} {excerpt}".lower()
    links: list[str] = []
    base = {
        "live-orchestration": ["AppA", "AppL", "AppP"],
        "void-and-collapse": ["AppF", "AppI", "AppL"],
        "helical-recursion-engine": ["AppF", "AppG", "AppI", "AppM"],
        "manuscript-architecture": ["AppA", "AppC", "AppI", "AppM"],
        "higher-dimensional-geometry": ["AppE", "AppF", "AppG", "AppM"],
        "civilization-and-governance": ["AppA", "AppD", "AppG", "AppP"],
        "mythic-sign-systems": ["AppA", "AppB", "AppC", "AppM"],
        "transport-and-runtime": ["AppF", "AppG", "AppM", "AppN"],
        "identity-and-instruction": ["AppG", "AppP"],
    }
    links.extend(base.get(family, []))
    if "conflict" in text or "quarantine" in text:
        links.append("AppK")
    if "time" in text or "orbit" in text:
        links.append("AppE")
    if "sign" in text or "glyph" in text or "khipu" in text or "ogham" in text:
        links.append("AppA")
        links.append("AppB")
    if "govern" in text or "hierarch" in text or "civiliz" in text:
        links.append("AppG")
        links.append("AppP")
    ordered: list[str] = []
    seen: set[str] = set()
    for item in links:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered[:4]


def keyword_count(text: str, weights: dict[str, float]) -> float:
    normalized = text.lower()
    score = 0.0
    for term, weight in weights.items():
        if term in normalized:
            score += weight
    return score


def smooth_ratio(math_score: float, myth_score: float) -> float:
    safe_math = max(math_score, 0.0) + 1.0
    safe_myth = max(myth_score, 0.0) + 1.0
    return round(safe_math / (safe_math + safe_myth), 4)


def path_prior(record: dict[str, Any], station_map: dict[str, dict[str, Any]]) -> float:
    relative_path = normalize_path(record.get("relative_path", "")).lower()
    top_level = record.get("top_level") or "<unknown>"
    math_score = 1.0
    myth_score = 1.0

    path_tokens = set(tokens(relative_path))
    math_score += sum(1.0 for token in path_tokens if token in PATH_MATH_KEYWORDS)
    myth_score += sum(1.0 for token in path_tokens if token in PATH_MYTH_KEYWORDS)

    top_level_bonus = TOP_LEVEL_PATH_PRIORS.get(top_level)
    if top_level_bonus:
        math_score += top_level_bonus[0]
        myth_score += top_level_bonus[1]

    station = station_map.get(top_level)
    if station:
        hemisphere = station.get("hemisphere", "")
        if hemisphere == "left":
            math_score += 1.4
            myth_score += 0.4
        elif hemisphere == "right":
            myth_score += 1.4
            math_score += 0.4
        else:
            math_score += 0.7
            myth_score += 0.7

    return smooth_ratio(math_score, myth_score)


def family_prior(family: str) -> float:
    return FAMILY_PRIORS.get(family, 0.5)


def title_heading_lexical_score(record: dict[str, Any]) -> float:
    headings = record.get("heading_candidates") or []
    title = Path(record.get("relative_path", "")).stem
    text = " ".join([title, *headings])
    return smooth_ratio(
        keyword_count(text, MATH_LEXICAL_WEIGHTS),
        keyword_count(text, MYTH_LEXICAL_WEIGHTS),
    )


def excerpt_lexical_score(record: dict[str, Any]) -> float:
    return smooth_ratio(
        keyword_count(record.get("excerpt", ""), MATH_LEXICAL_WEIGHTS),
        keyword_count(record.get("excerpt", ""), MYTH_LEXICAL_WEIGHTS),
    )


def structural_density_score(record: dict[str, Any]) -> float:
    if not record.get("text_extractable"):
        return 0.5

    text = " ".join(
        [
            Path(record.get("relative_path", "")).stem,
            *list(record.get("heading_candidates") or []),
            record.get("excerpt", ""),
        ]
    )
    if not text:
        return 0.5

    length = max(len(text), 1)
    digits = sum(ch.isdigit() for ch in text)
    symbols = sum(ch in "=<>[](){}^_*/+-|" for ch in text)
    uppercase_lines = sum(
        1
        for heading in record.get("heading_candidates") or []
        if heading and heading.upper() == heading
    )
    equation_hits = sum(
        1
        for term in ("theorem", "lemma", "definition", "matrix", "equation", "operator")
        if term in text.lower()
    )
    narrative_hits = sum(
        1
        for term in ("myth", "goddess", "ritual", "prophecy", "dream", "oracle")
        if term in text.lower()
    )

    math_signal = min(
        1.0,
        (digits / length) * 9.0
        + (symbols / length) * 18.0
        + uppercase_lines * 0.08
        + equation_hits * 0.08,
    )
    myth_signal = min(1.0, narrative_hits * 0.08)
    return round(max(0.0, min(1.0, 0.5 + (math_signal - myth_signal) / 2.0)), 4)


def weighted_math_score(component_scores: dict[str, float]) -> float:
    score = (
        component_scores["path_prior"] * 0.30
        + component_scores["family_prior"] * 0.25
        + component_scores["title_heading"] * 0.20
        + component_scores["excerpt"] * 0.20
        + component_scores["structural_density"] * 0.05
    )
    return round(max(0.0, min(1.0, score)), 4)


def compute_component_scores(
    record: dict[str, Any],
    family: str,
    station_map: dict[str, dict[str, Any]],
) -> dict[str, float]:
    return {
        "path_prior": path_prior(record, station_map),
        "family_prior": family_prior(family),
        "title_heading": title_heading_lexical_score(record),
        "excerpt": excerpt_lexical_score(record),
        "structural_density": structural_density_score(record),
    }


def compute_confidence(record: dict[str, Any], math_weight: float) -> float:
    extractable_factor = 1.0 if record.get("text_extractable") else 0.35
    separation = abs(math_weight - 0.5) * 2.0
    confidence = 0.35 + 0.35 * extractable_factor + 0.30 * separation
    if not record.get("text_extractable"):
        confidence = min(confidence, 0.65)
    return round(max(0.0, min(0.98, confidence)), 4)


def parse_canonical_sources() -> list[BasisAnchor]:
    if not CANONICAL_SOURCES_PATH.exists():
        return []
    anchors: list[BasisAnchor] = []
    pattern = re.compile(
        r"^- `(?P<code>\d+)` (?P<title>.+?) \[(?P<element>.+?)\]: "
        r"(?P<role>.+?)\. Cluster: (?P<cluster>.+?)\. Source hint: `(?P<hint>.+?)`\.$"
    )
    for line in CANONICAL_SOURCES_PATH.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        code = match.group("code")
        anchors.append(
            BasisAnchor(
                anchor_id=f"DN{code.zfill(2)}",
                source_id=code.zfill(2),
                title=match.group("title"),
                element=match.group("element"),
                cluster=match.group("cluster"),
                role=match.group("role"),
                source_hint=match.group("hint"),
            )
        )
    return anchors


def anchor_score(record: dict[str, Any], anchor: BasisAnchor) -> float:
    title = Path(record.get("relative_path", "")).stem
    headings = " ".join(record.get("heading_candidates") or [])
    excerpt = record.get("excerpt", "")
    blob_tokens = Counter(tokens(f"{title} {headings} {excerpt}"))

    title_tokens = set(tokens(anchor.title))
    hint_tokens = set(tokens(anchor.source_hint))
    cluster_tokens = set(tokens(anchor.cluster))
    role_tokens = set(tokens(anchor.role))

    score = 0.0
    score += sum(blob_tokens[token] for token in title_tokens) * 2.5
    score += sum(blob_tokens[token] for token in hint_tokens) * 2.0
    score += sum(blob_tokens[token] for token in cluster_tokens) * 1.2
    score += sum(blob_tokens[token] for token in role_tokens) * 1.0

    relative_path = normalize_path(record.get("relative_path", "")).lower()
    if anchor.source_hint.lower().replace("\\", "/").split("/")[-1].split(".")[0] in relative_path:
        score += 3.0
    if anchor.title.lower() in excerpt.lower():
        score += 3.0
    return score


def fallback_anchor_ids(family: str, primary_hemisphere: str) -> list[str]:
    preferred = FAMILY_ANCHOR_PREFERENCES.get(family)
    if preferred:
        return preferred[:3]
    if primary_hemisphere == "MATH":
        return ["DN03", "DN05", "DN07"]
    return ["DN01", "DN11", "DN12"]


def assign_basis_anchor_ids(
    record: dict[str, Any],
    anchors: list[BasisAnchor],
    family: str,
    primary_hemisphere: str,
) -> list[str]:
    scores = sorted(
        ((anchor_score(record, anchor), anchor.anchor_id) for anchor in anchors),
        key=lambda item: (-item[0], item[1]),
    )
    chosen = [anchor_id for score, anchor_id in scores if score > 0][:3]
    if not chosen:
        chosen = fallback_anchor_ids(family, primary_hemisphere)
    return chosen


def family_bucket_digit(family: str) -> int:
    if family in {"higher-dimensional-geometry", "manuscript-architecture"}:
        return 0
    if family in {"mythic-sign-systems", "identity-and-instruction", "live-orchestration"}:
        return 1
    if family in {"civilization-and-governance", "general-corpus"}:
        return 2
    return 3


def tract_digit(tract: str) -> int:
    return {
        "address": 0,
        "relation": 1,
        "chamber": 2,
        "replay": 3,
    }.get(tract, 0)


def holo_tail(record_id: str) -> str:
    digest = hashlib.sha256(record_id.encode("utf-8")).hexdigest()
    number = int(digest[:8], 16)
    digits: list[str] = []
    for _ in range(8):
        digits.append(str(number % 4))
        number //= 4
    return "".join(reversed(digits))


def build_holo_address(
    primary_hemisphere: str,
    tract: str,
    family: str,
    anchor_ids: list[str],
    record_id: str,
) -> str:
    hemisphere_digit = 0 if primary_hemisphere == "MATH" else 3
    anchor_digit = 0
    if anchor_ids:
        anchor_digit = (int(anchor_ids[0][-2:]) - 1) % 4
    prefix = (
        f"{hemisphere_digit}"
        f"{tract_digit(tract)}"
        f"{family_bucket_digit(family)}"
        f"{anchor_digit}"
    )
    return f"H4::{prefix}::{holo_tail(record_id)}"


def resolve_tract(
    family: str,
    record: dict[str, Any],
    station_map: dict[str, dict[str, Any]],
) -> str:
    tract = TRACT_BY_FAMILY.get(family)
    if tract:
        return tract
    station = station_map.get(record.get("top_level") or "")
    if station:
        return station.get("tract", "address")
    return "address"


def metro_line_ids(
    primary_hemisphere: str,
    bridge_class: str,
    family: str,
    tract: str,
    anchor_ids: list[str],
    record_id: str,
) -> list[str]:
    level_one = (
        "L1-COMMISSURE"
        if bridge_class == "commissure_bridge"
        else f"L1-{primary_hemisphere}"
    )
    lines = [
        level_one,
        f"L2-FAMILY-{slugify(family)}",
        f"L2-ANCHOR-{anchor_ids[0] if anchor_ids else 'DN00'}",
        f"L3-TRACT-{tract.upper()}",
        f"L3-CORRIDOR-{slugify(family)}-{anchor_ids[0] if anchor_ids else 'DN00'}",
        f"L4-SUPERMESH-{record_id}",
    ]
    return lines


def trace_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:24]


def record_title(record: dict[str, Any]) -> str:
    headings = record.get("heading_candidates") or []
    if headings:
        return headings[0]
    return Path(record.get("relative_path", "")).stem


def record_summary_line(record: dict[str, Any]) -> str:
    return (
        f"`{record['record_id']}` | `{record['primary_hemisphere']}` | "
        f"`{record['math_weight']:.3f}` | `{record['family']}` | "
        f"`{record['relative_path']}`"
    )


def mirror_paths() -> list[Path]:
    return [
        FLEET_MIRROR_ROOT / "README.md",
        FLEET_MIRROR_ROOT / "01_math_crystal.md",
        FLEET_MIRROR_ROOT / "02_myth_crystal.md",
        FLEET_MIRROR_ROOT / "03_unified_corpus_hub.md",
        FLEET_MIRROR_ROOT / "04_metro_level_1.md",
        FLEET_MIRROR_ROOT / "05_metro_level_2.md",
        FLEET_MIRROR_ROOT / "06_metro_level_3.md",
        FLEET_MIRROR_ROOT / "07_metro_level_4.md",
        FLEET_MIRROR_ROOT / "08_build_receipt.md",
        FLEET_MIRROR_ROOT / "09_route_index.md",
        FLEET_MIRROR_ROOT / "10_math_direct_route_atlas.md",
        FLEET_MIRROR_ROOT / "11_myth_direct_route_atlas.md",
        FLEET_MIRROR_ROOT / "12_dual_hemisphere_crosswalk_map.md",
        FLEET_MIRROR_ROOT / "13_route_coverage_receipt.md",
        FLEET_MIRROR_ROOT / "14_navigator_index.md",
        FLEET_MIRROR_ROOT / "15_query_cookbook.md",
        FLEET_MIRROR_ROOT / "16_math_facet_hotspots.md",
        FLEET_MIRROR_ROOT / "17_myth_facet_hotspots.md",
        FLEET_MIRROR_ROOT / "18_cross_hemisphere_entrypoint_atlas.md",
        FLEET_MIRROR_ROOT / "19_route_composer_index.md",
        FLEET_MIRROR_ROOT / "20_route_composer_cookbook.md",
        FLEET_MIRROR_ROOT / "21_math_route_starters.md",
        FLEET_MIRROR_ROOT / "22_myth_route_starters.md",
        FLEET_MIRROR_ROOT / "23_commissure_route_starters.md",
        FLEET_MIRROR_ROOT / "24_facet_route_starters.md",
        FLEET_MIRROR_ROOT / "25_synthesis_index.md",
        FLEET_MIRROR_ROOT / "26_synthesis_cookbook.md",
        FLEET_MIRROR_ROOT / "27_math_starter_syntheses.md",
        FLEET_MIRROR_ROOT / "28_myth_starter_syntheses.md",
        FLEET_MIRROR_ROOT / "29_commissure_starter_syntheses.md",
        FLEET_MIRROR_ROOT / "30_facet_synthesis_atlas.md",
        FLEET_MIRROR_ROOT / "31_visual_atlas_index.md",
        FLEET_MIRROR_ROOT / "32_corpus_overview_map.md",
        FLEET_MIRROR_ROOT / "33_math_route_topology_atlas.md",
        FLEET_MIRROR_ROOT / "34_myth_route_topology_atlas.md",
        FLEET_MIRROR_ROOT / "35_anchor_crosswalk_atlas.md",
        FLEET_MIRROR_ROOT / "36_target_system_atlas.md",
        FLEET_MIRROR_ROOT / "37_record_locator_index.md",
        FLEET_MIRROR_ROOT / "38_atlas_coverage_receipt.md",
        FLEET_MIRROR_ROOT / "39_guided_tour_index.md",
        FLEET_MIRROR_ROOT / "40_guided_tour_cookbook.md",
        FLEET_MIRROR_ROOT / "41_main_atlas_page_starters.md",
        FLEET_MIRROR_ROOT / "42_family_guided_starters.md",
        FLEET_MIRROR_ROOT / "43_anchor_guided_starters.md",
        FLEET_MIRROR_ROOT / "44_target_system_guided_starters.md",
        FLEET_MIRROR_ROOT / "45_expedition_index.md",
        FLEET_MIRROR_ROOT / "46_expedition_cookbook.md",
        FLEET_MIRROR_ROOT / "47_main_atlas_expeditions.md",
        FLEET_MIRROR_ROOT / "48_family_expedition_starters.md",
        FLEET_MIRROR_ROOT / "49_anchor_expedition_starters.md",
        FLEET_MIRROR_ROOT / "50_target_system_expedition_starters.md",
        FLEET_MIRROR_ROOT / "51_constellation_index.md",
        FLEET_MIRROR_ROOT / "52_constellation_cookbook.md",
        FLEET_MIRROR_ROOT / "53_family_constellations.md",
        FLEET_MIRROR_ROOT / "54_anchor_constellations.md",
        FLEET_MIRROR_ROOT / "55_target_system_constellations.md",
        FLEET_MIRROR_ROOT / "56_constellation_coverage_receipt.md",
        FLEET_MIRROR_ROOT / "57_replay_index.md",
        FLEET_MIRROR_ROOT / "58_replay_cookbook.md",
        FLEET_MIRROR_ROOT / "59_math_replay_starters.md",
        FLEET_MIRROR_ROOT / "60_myth_replay_starters.md",
        FLEET_MIRROR_ROOT / "61_bridge_replay_starters.md",
        FLEET_MIRROR_ROOT / "62_replay_coverage_receipt.md",
        FLEET_MIRROR_ROOT / "63_observatory_index.md",
        FLEET_MIRROR_ROOT / "64_observatory_cookbook.md",
        FLEET_MIRROR_ROOT / "65_main_page_briefings.md",
        FLEET_MIRROR_ROOT / "66_family_briefings.md",
        FLEET_MIRROR_ROOT / "67_anchor_briefings.md",
        FLEET_MIRROR_ROOT / "68_observatory_coverage_receipt.md",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_record_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_commissure_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_metro_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_hub_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_dual_route_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_direct_edge_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_route_coverage_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_route_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_navigator_alias_index.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_navigator_facet_index.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_navigator_neighbor_index.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_navigator_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_route_composer_seed_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_route_composer_facet_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_route_composer_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_synthesis_evidence_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_synthesis_seed_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_synthesis_facet_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_synthesis_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_visual_atlas_node_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_visual_atlas_edge_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_visual_atlas_page_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_visual_atlas_record_locator_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_visual_atlas_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_guided_tour_seed_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_guided_tour_page_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_guided_tour_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_expedition_seed_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_expedition_page_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_expedition_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_constellation_node_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_constellation_edge_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_constellation_page_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_constellation_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_replay_seed_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_replay_page_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_replay_manifest.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_observatory_seed_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_observatory_page_registry.json",
        FLEET_MIRROR_ROOT / "myth_math_hemisphere_observatory_manifest.json",
    ]
