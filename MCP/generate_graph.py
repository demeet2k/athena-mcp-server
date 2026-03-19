# CRYSTAL: Xi108:W3:A4:S22 | face=S | node=361 | depth=1 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W3:A4:S21→Xi108:W3:A4:S23→Xi108:W2:A4:S22→Xi108:W3:A3:S22→Xi108:W3:A5:S22

"""
Athena Mycelium Graph Generator
================================
Scans the ENTIRE Athena organism — MCP tools, data, element servers,
Guild Hall, manuscript-being Python framework, AND the full local corpus
(Voynich, Trading Bot, Neural Network, QSHRINK, Math, Games, Manuscripts,
Nervous System, etc.) — to produce the universal shard/edge graph manifest
with metro line mappings.

Usage:
    python -X utf8 MCP/generate_graph.py

Emits:
    MCP/data/mycelium_graph.json
    MCP/data/node_registry.json
"""

import json
import re
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Ensure MCP/ is importable
_MCP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_MCP_DIR))
os.environ.setdefault("ATHENA_ROOT", str(_MCP_DIR.parent))

from crystal_108d.metabolism import (
    Shard, Edge, make_shard_id, make_edge_id, to_dict, now_iso,
)

DATA_DIR = _MCP_DIR / "data"
CRYSTAL_DIR = _MCP_DIR / "crystal_108d"
ELEMENT_DIR = _MCP_DIR / "element_servers"
GUILD_HALL_DIR = _MCP_DIR.parent / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
ATHENA_REPO_DIR = Path(os.environ.get("ATHENA_REPO", str(Path.home() / "Documents" / "athena")))

NOW = now_iso()

# ── Family inference from filename ──────────────────────────────────

FAMILY_MAP = {
    "shell_registry": "shells",
    "hologram_chapters": "hologram",
    "dimensional_ladder": "dimensions",
    "organ_atlas": "organs",
    "live_lock_registry": "live_lock",
    "clock_projections": "clock",
    "move_primitives": "moves",
    "metro_lines": "metro",
    "z_point_hierarchy": "z_points",
    "conservation_laws": "conservation",
    "overlay_registries": "overlays",
    "transport_stacks": "transport",
    "mobius_lenses": "mobius",
    "stage_codes": "stages",
    "angel_object": "angel",
    "brain_network": "brain",
    "live_cell_constitution": "live_cell",
    "dimensional_emergence": "emergence",
    "hologram_reading": "hologram",
    "hologram_rosetta": "hologram",
    "angel_geometry": "angel",
    "angel_conservation": "angel",
    "inverse_crystal_seed": "inverse_crystal",
    "inverse_crystal_octave": "inverse_crystal",
    "inverse_crystal_complete": "inverse_crystal",
}

MODULE_FAMILY_MAP = {
    "shells": "shells",
    "dimensions": "dimensions",
    "organs": "organs",
    "address": "address",
    "live_lock": "live_lock",
    "clock": "clock",
    "moves": "moves",
    "metro_lines": "metro",
    "z_points": "z_points",
    "conservation": "conservation",
    "overlays": "overlays",
    "transport": "transport",
    "mobius_lenses": "mobius",
    "stage_codes": "stages",
    "angel": "angel",
    "angel_geometry": "angel",
    "brain": "brain",
    "live_cell": "live_cell",
    "emergence": "emergence",
    "hologram_reading": "hologram",
    "inverse_seed": "inverse_crystal",
    "inverse_octave": "inverse_crystal",
    "inverse_complete": "inverse_crystal",
    "metabolism": "mycelium",
    "mycelium": "mycelium",
}

ELEMENT_LENS = {
    "square_server": "S",
    "flower_server": "F",
    "cloud_server": "C",
    "fractal_server": "R",
}

SKIP_MODULES = {"__init__", "_cache", "constants", "__pycache__"}

# ── Full Organism SFCR Element Mapping ─────────────────────────────
# Every top-level directory → (primary_lens, secondary_lens, metro_line, family)
# Metro lines: Sa=Shell Ascent, Wr=Wreath Ring, Ac=Archetype Column,
#   Me=Metro Express, Mt=Mobius Twist, Bw=Bridge Walk, Cc=Crown Circuit, Dl=Dimensional Lift

ORGANISM_DIR_MAP = {
    # Core nervous system
    "DEEPER_CRYSTALIZATION": ("S", "R", "Dl", "crystal"),       # Square: deep structural crystallization
    "NERVOUS_SYSTEM":       ("R", "S", "Sa", "nervous"),        # Fractal: recursive nervous system
    "MATH":                 ("S", "R", "Sa", "math"),           # Square: mathematical structure
    # Active directories
    "CLEAN":                ("C", "S", "Bw", "manuscript"),     # Cloud: distilled/purified manuscripts
    "ECOSYSTEM":            ("F", "C", "Wr", "ecosystem"),      # Flower: living ecosystem dynamics
    "FRESH":                ("C", "F", "Me", "manuscript"),     # Cloud: fresh perspective, new captures
    "GUILDMASTER":          ("F", "S", "Cc", "guild"),          # Flower: guild mastery, social dynamics
    "I AM ATHENA":          ("R", "C", "Mt", "identity"),       # Fractal: self-referential identity
    "mycelial_unified_nervous_system_bundle": ("R", "C", "Bw", "mycelium"),  # Fractal: mycelium recursion
    "self_actualize":       ("F", "R", "Dl", "actualize"),      # Flower: growth dynamics, emergence
    ".github":              ("S", "F", "Bw", "infra"),          # Square: infrastructure
    # PROJECTS/ grouping (restructured from top-level)
    "PROJECTS/GAMES":           ("F", "S", "Me", "games"),      # Flower: game dynamics, play
    "PROJECTS/NEURAL_NETWORK":  ("C", "F", "Dl", "neural"),     # Cloud: learning, observation, inference
    "PROJECTS/TRADING_BOT":     ("F", "C", "Me", "trading"),    # Flower: market dynamics, fire
    "PROJECTS/VOYNICH":         ("C", "R", "Mt", "voynich"),    # Cloud: observation, decoding
    "PROJECTS/QUADRANT_BINARY": ("S", "R", "Sa", "binary"),     # Square: binary/discrete structure
    "PROJECTS/STOICHEIA":       ("F", "S", "Wr", "games"),      # Flower: element play, sudoku dynamics
    "PROJECTS/QSHRINK":         ("R", "S", "Mt", "qshrink"),    # Fractal: compression, holographic seed
}

# Subdirectory overrides for deeper SFCR precision
ORGANISM_SUBDIR_MAP = {
    "DEEPER_CRYSTALIZATION/13_ACCEPTED_INPUTS":       ("C", "S", "Bw", "accepted"),
    "DEEPER_CRYSTALIZATION/CRYSTAL_SEEDS":            ("R", "S", "Mt", "seed"),
    "DEEPER_CRYSTALIZATION/MANUSCRIPTS":              ("S", "C", "Ac", "manuscript"),
    "MATH/FINAL FORM":                                ("S", "R", "Cc", "math_final"),
    "MATH/lp57omega":                                 ("F", "S", "Wr", "lp57"),
    "PROJECTS/NEURAL_NETWORK/ATHENA Neural Network":  ("C", "F", "Dl", "neural_core"),
    "NERVOUS_SYSTEM/10_OVERVIEW":                     ("R", "S", "Sa", "nervous_overview"),
    "NERVOUS_SYSTEM/20_CORPUS":                       ("S", "R", "Ac", "corpus"),
    "NERVOUS_SYSTEM/30_APPENDIX":                     ("S", "C", "Bw", "appendix"),
    "PROJECTS/QSHRINK/00_CONTROL":                    ("S", "R", "Cc", "qshrink_control"),
    "PROJECTS/QSHRINK/CODEC":                         ("R", "S", "Mt", "qshrink_codec"),
    "PROJECTS/TRADING_BOT/CRYPTO CURRENCY":           ("F", "C", "Me", "crypto"),
    "PROJECTS/TRADING_BOT/FOREX":                     ("F", "S", "Me", "forex"),
    "PROJECTS/VOYNICH/eva":                           ("C", "S", "Mt", "voynich_eva"),
    "PROJECTS/VOYNICH/decoder":                       ("C", "R", "Mt", "voynich_decoder"),
    "self_actualize/mycelium_brain":                  ("R", "F", "Dl", "mycelium_brain"),
    "NERVOUS_SYSTEM/30_CHAPTERS/HPRO":                ("S", "R", "Ω",  "hpro"),           # HPRO manuscripts → zero-point spine
}

# Skip directories that are not meaningful organism content
ORGANISM_SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".claude", "MCP", "tests", "_repo_root", ".mypy_cache", "dist", "build",
    "egg-info", ".eggs", ".tox", "ARCHIVE",
}

# File extensions to scan as organism shards
ORGANISM_EXTENSIONS = {".py", ".md", ".json", ".js", ".ts", ".yaml", ".yml", ".html", ".css"}

# Metro line descriptions for the graph metadata
# Original 8 Athena metro lines + 9 HPRO corpus-wide lines = 17 total
METRO_LINES = {
    # ── Original Athena Organism Lines ──
    "Sa": {"name": "Shell Ascent",      "desc": "Structural hierarchy — dimension layers",       "element": "S"},
    "Wr": {"name": "Wreath Ring",       "desc": "Cyclical grouping — 7-chapter wreath bodies",   "element": "F"},
    "Ac": {"name": "Archetype Column",  "desc": "12-archetype classification threads",           "element": "S"},
    "Me": {"name": "Metro Express",     "desc": "Fast routing — core logic and dynamics",        "element": "F"},
    "Mt": {"name": "Mobius Twist",      "desc": "Parity/inversion — compression and decoding",   "element": "R"},
    "Bw": {"name": "Bridge Walk",       "desc": "Cross-domain connection corridors",             "element": "C"},
    "Cc": {"name": "Crown Circuit",     "desc": "Organism-level governance and command",         "element": "S"},
    "Dl": {"name": "Dimensional Lift",  "desc": "Higher-D emergence and actualization",          "element": "R"},
    # ── HPRO Corpus-Wide Lines (Holographic Programming & Repo Organization) ──
    "Ω":  {"name": "Zero-Point Spine",  "desc": "Ω(Ω)=Ω — all lines terminate/re-enter here",  "element": "R", "hpro": True},
    "w":  {"name": "Generator Line",    "desc": "w=(1+i)/2 seed propagation across all docs",    "element": "F", "hpro": True},
    "□":  {"name": "Square Address",    "desc": "Base-4 discrete addressing — CODE_KEY grammar",  "element": "S", "hpro": True},
    "○":  {"name": "Convergence Circle","desc": "1/e, 1/φ, 1/π threshold convergence",          "element": "C", "hpro": True},
    "△":  {"name": "Triangle Control",  "desc": "ℤ₃ recursion legality, cycle length, cadence",  "element": "F", "hpro": True},
    "✶":  {"name": "Fractal Holographic","desc": "Part=whole at lower resolution — seed storage", "element": "R", "hpro": True},
    "T":  {"name": "Truth Lattice",     "desc": "OK/NEAR/AMBIG/FAIL structured truth corridor",  "element": "C", "hpro": True},
    "Ξ":  {"name": "Operator Spectral", "desc": "Eigenvalues, Laplacian, Fiedler connectivity",  "element": "S", "hpro": True},
    "M":  {"name": "Migration Evolution","desc": "MIGRATE collapse-to-Z* then re-expansion",     "element": "F", "hpro": True},
}

# ── HPRO CODE_KEY Level Assignment ─────────────────────────────────
# Level 0=atom(function), 1=module, 2=package, 3=service, 4=monorepo
# Maps directory depth + type to hologram level

HPRO_ELEMENT_MAP = {
    # Fire🜂=compute (.py with algorithms, transforms, engines)
    "compute": "Fire", "engine": "Fire", "bot": "Fire", "trading": "Fire",
    "neural": "Fire", "solver": "Fire", "executor": "Fire", "runtime": "Fire",
    "generator": "Fire", "builder": "Fire", "compiler": "Fire",
    # Air🜁=interface (.py with API, schema, protocol, router)
    "api": "Air", "schema": "Air", "protocol": "Air", "router": "Air",
    "interface": "Air", "cli": "Air", "server": "Air", "handler": "Air",
    # Water🜄=state (.py with state, session, cache, buffer)
    "state": "Air", "session": "Water", "cache": "Water", "buffer": "Water",
    "store": "Water", "memory": "Water", "registry": "Water", "ledger": "Water",
    # Earth🜃=storage (.json, .yaml, .md, configs, data)
    "data": "Earth", "config": "Earth", "manifest": "Earth", "index": "Earth",
    "archive": "Earth", "seed": "Earth", "snapshot": "Earth",
}

HPRO_PHASE_MAP = {
    # Cardinal=init/create, Fixed=stabilize, Mutable=refactor
    "new": "Cardinal", "init": "Cardinal", "create": "Cardinal", "seed": "Cardinal",
    "stable": "Fixed", "final": "Fixed", "canonical": "Fixed", "locked": "Fixed",
    "refactor": "Mutable", "draft": "Mutable", "wip": "Mutable", "dev": "Mutable",
}

def _compute_hpro_code_key(rel_path: str, depth: int, ext: str, stem: str) -> dict:
    """Compute HPRO CODE_KEY for a file.

    CODE_KEY = ⟨level | path | element | phase | semver_phase⟩
    """
    # Level from depth: 0=atom(leaf), 1=module(1 dir), 2=package(2 dirs), 3=service(3+)
    level = min(depth, 3)

    # Element from filename keywords
    element = "Earth"  # default for docs/data
    if ext in (".py", ".js", ".ts"):
        element = "Fire"  # default for code
        for keyword, elem in HPRO_ELEMENT_MAP.items():
            if keyword in stem.lower():
                element = elem
                break
    elif ext in (".json", ".yaml", ".yml"):
        element = "Earth"
    elif ext == ".md":
        element = "Air"  # docs = interface/specification

    # Phase from keywords
    phase = "Fixed"  # default
    for keyword, ph in HPRO_PHASE_MAP.items():
        if keyword in stem.lower():
            phase = ph
            break

    # Chi (public/private): +1 if no underscore prefix, -1 if private
    chi = -1 if stem.startswith("_") else 1

    # Side-effect signature
    sigma = "pure"
    if ext in (".py", ".js", ".ts"):
        sigma = "IO" if any(k in stem.lower() for k in ("server", "cli", "api", "handler")) else "pure"

    return {
        "level": level,
        "element": element,
        "phase": phase,
        "chi": chi,
        "sigma": sigma,
        "code_key": f"⟨{level}|{rel_path}|{element}|{phase}⟩",
    }

MANUSCRIPT_MODULE_FAMILY = {
    "address": "crystal",
    "parse_kernel": "kernel",
    "wave_engine": "kernel",
    "lattice": "crystal",
    "gate": "crystal",
    "router": "metro",
    "schedule": "metro",
    "certificate": "proof",
    "conservation": "proof",
    "seed": "replication",
    "corridor": "truth",
    "witness": "truth",
    "collective": "swarm",
    "stack": "transport",
    "sfcr": "lens",
    "field": "tensor",
    "regeneration": "cycle",
    "store": "memory",
    "runtime": "agent",
    "executor": "runtime",
}

def _infer_family(stem: str) -> str:
    return FAMILY_MAP.get(stem, stem.replace("_", "-"))

def _extract_docstring(path: Path) -> str:
    """Extract first line of module docstring."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'"""(.*?)"""', text, re.DOTALL)
        if m:
            first = m.group(1).strip().split("\n")[0].strip()
            if first and len(first) > 5:
                return first
        m = re.search(r"'''(.*?)'''", text, re.DOTALL)
        if m:
            first = m.group(1).strip().split("\n")[0].strip()
            if first and len(first) > 5:
                return first
    except Exception:
        pass
    return f"Module {path.stem}"

def _extract_json_caches(path: Path) -> list[str]:
    """Find all JsonCache('filename.json') references in a Python file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return re.findall(r'JsonCache\(["\']([^"\']+\.json)["\']\)', text)
    except Exception:
        return []

def _extract_json_title(path: Path) -> str:
    """Extract meta.title from a JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "meta" in data:
            return data["meta"].get("title", path.stem)
    except Exception:
        pass
    return path.stem

def _infer_dimensional_scope(data: dict, stem: str) -> str:
    """Infer dimensional scope from JSON content."""
    if "dimension" in str(data).lower()[:200]:
        return "3D-12D"
    if "108" in stem or "shell" in stem:
        return "108D"
    if "brain" in stem:
        return "4D-10D"
    if "angel" in stem:
        return "all"
    if "inverse_crystal" in stem:
        return "3D-108D"
    if "hologram" in stem:
        return "all"
    if "emergence" in stem:
        return "3D-A+"
    return "all"

def _infer_seed_vector(family: str, lens: str | None) -> list[float]:
    """Infer SFCR seed vector from family and lens."""
    if lens == "S":
        return [1.0, 0.0, 0.0, 0.0]
    if lens == "F":
        return [0.0, 1.0, 0.0, 0.0]
    if lens == "C":
        return [0.0, 0.0, 1.0, 0.0]
    if lens == "R":
        return [0.0, 0.0, 0.0, 1.0]
    # Universal — balanced
    return [0.25, 0.25, 0.25, 0.25]

# ── Chapter / Appendix Definitions ─────────────────────────────────

CHAPTER_TITLES = {
    1: "Foundations", 2: "Elements", 3: "Cycles", 4: "Structure",
    5: "Growth", 6: "Harmony", 7: "Transformation", 8: "Observation",
    9: "Compression", 10: "Integration", 11: "Convergence", 12: "Emergence",
    13: "Self-Reference", 14: "Agency", 15: "Consciousness",
    16: "Civilization", 17: "Transcendence", 18: "Unity",
    19: "Recursion", 20: "Completion", 21: "Beyond",
}

APPENDIX_TITLES = {
    "A": "Mathematics", "B": "Physics", "C": "Biology", "D": "Psychology",
    "E": "Philosophy", "F": "Cosmology", "G": "Linguistics", "H": "Music",
    "I": "Art", "J": "Architecture", "K": "Computing", "L": "Ecology",
    "M": "Mythology", "N": "Pedagogy", "O": "Ethics", "P": "Governance",
}

CHAPTER_TAGS = {
    1: ["foundations", "axioms", "base"],
    2: ["elements", "sfcr", "four"],
    3: ["cycles", "recursion", "loop"],
    4: ["structure", "lattice", "form"],
    5: ["growth", "emergence", "expansion"],
    6: ["harmony", "balance", "resonance"],
    7: ["transformation", "change", "alchemy"],
    8: ["observation", "witness", "measurement"],
    9: ["compression", "encoding", "qshrink"],
    10: ["integration", "synthesis", "merge"],
    11: ["convergence", "zero_point", "omega"],
    12: ["emergence", "self_organization", "complexity"],
    13: ["self_reference", "godel", "recursion"],
    14: ["agency", "will", "action"],
    15: ["consciousness", "awareness", "qualia"],
    16: ["civilization", "collective", "society"],
    17: ["transcendence", "beyond", "infinity"],
    18: ["unity", "zero_point", "one"],
    19: ["recursion", "fractal", "self_similar"],
    20: ["completion", "zero_point", "wholeness"],
    21: ["beyond", "zero_point", "meta"],
}

ZERO_POINT_CHAPTERS = {11, 18, 20, 21}

# Metro weight hierarchy for differentiated METRO edge weights
METRO_WEIGHT_HIERARCHY = {
    "Ω":  0.90,   # Zero-Point Spine
    "Sa": 0.80,   # Shell Ascent
    "∞":  0.75,   # Generator w-spiral (mapped from "w" line)
    "w":  0.75,   # Generator w-spiral
    "Me": 0.70,   # Mercury/Wednesday
    "Dl": 0.65,   # Daily Loop / Dimensional Lift
    "Su": 0.65,   # Sunday
}
METRO_WEIGHT_DEFAULT = 0.50

# ── Scan Functions ──────────────────────────────────────────────────

def _create_chapter_appendix_shards() -> list[Shard]:
    """Create 37 new shards: 21 chapter shards + 16 appendix shards."""
    shards = []

    # 21 chapter shards
    for n, title in CHAPTER_TITLES.items():
        sid = f"chapter:Ch{n:02d}"
        routes = ["Sa"]  # structural by default
        if n in ZERO_POINT_CHAPTERS:
            routes = ["Ω"]
        # Seed vector: chapters are balanced with slight structural bias
        sv = [0.35, 0.20, 0.25, 0.20]
        if n in ZERO_POINT_CHAPTERS:
            sv = [0.15, 0.15, 0.15, 0.55]  # fractal/recursive for zero-point

        shards.append(Shard(
            shard_id=sid,
            lineage_id=sid,
            medium="doc",
            repo="athena-mcp-server",
            lens=None,
            dimensional_scope="all",
            payload_ref=f"hologram/chapter/{n:02d}",
            summary=f"Chapter {n}: {title}",
            seed_vector=sv,
            route_refs=routes,
            cert_refs=[],
            mirror_refs=[],
            truth_status="CANONICAL",
            promotion_status="PROMOTED",
            family="hologram_chapters",
            tags=CHAPTER_TAGS.get(n, [title.lower()]) + [f"ch{n:02d}", "chapter"],
            created_at=NOW,
            updated_at=NOW,
        ))

    # 16 appendix shards
    for letter, title in APPENDIX_TITLES.items():
        sid = f"appendix:App{letter}"
        routes = ["Sa"]  # structural/organizational
        sv = [0.30, 0.25, 0.25, 0.20]

        shards.append(Shard(
            shard_id=sid,
            lineage_id=sid,
            medium="doc",
            repo="athena-mcp-server",
            lens=None,
            dimensional_scope="all",
            payload_ref=f"hologram/appendix/{letter}",
            summary=f"Appendix {letter}: {title}",
            seed_vector=sv,
            route_refs=routes,
            cert_refs=[],
            mirror_refs=[],
            truth_status="CANONICAL",
            promotion_status="PROMOTED",
            family="appendix",
            tags=[title.lower(), f"app{letter.lower()}", "appendix"],
            created_at=NOW,
            updated_at=NOW,
        ))

    return shards


def _create_google_doc_shards() -> list[Shard]:
    """Create shards for all Google Doc mirrors defined in node.yaml."""
    import yaml as _yaml
    node_yaml_path = _MCP_DIR.parent / "node.yaml"
    if not node_yaml_path.exists():
        return []
    try:
        with open(node_yaml_path, "r", encoding="utf-8") as f:
            node_data = _yaml.safe_load(f) or {}
    except Exception:
        return []

    mirrors = node_data.get("mirrors", [])
    shards = []
    for mirror in mirrors:
        if mirror.get("type") != "google_doc":
            continue
        mid = mirror.get("id", "unknown")
        doc_id = mirror.get("doc_id", "")
        desc = mirror.get("description", mid)
        # Derive tags from the id
        tags = [t for t in mid.replace("-gdoc", "").replace("-", "_").split("_") if len(t) > 2]
        sid = f"gdoc:{mid.replace('-gdoc', '')}"
        shards.append(Shard(
            shard_id=sid,
            lineage_id=sid,
            medium="web",
            repo="google-docs",
            lens=None,
            dimensional_scope="all",
            payload_ref=f"gdoc/{doc_id}",
            summary=desc,
            seed_vector=[0.25, 0.25, 0.25, 0.25],
            route_refs=["Bw"],
            cert_refs=[],
            mirror_refs=[],
            truth_status="CANONICAL",
            promotion_status="PROMOTED",
            family="google_docs",
            tags=tags[:8],
            created_at=NOW,
            updated_at=NOW,
        ))
    return shards


def _create_guild_hall_shards() -> list[Shard]:
    """Scan guild hall directory for .md files and create shards with summaries."""
    shards = []
    if not GUILD_HALL_DIR.exists():
        return shards

    for fp in sorted(GUILD_HALL_DIR.glob("*.md")):
        stem = fp.stem
        sid = f"guild:{stem}"
        # Extract first line as summary
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
            first_line = ""
            for line in text.split("\n"):
                stripped = line.strip().lstrip("# ").strip()
                if stripped and len(stripped) > 3:
                    first_line = stripped[:120]
                    break
            if not first_line:
                first_line = stem.replace("_", " ").title()
        except Exception:
            first_line = stem.replace("_", " ").title()

        shards.append(Shard(
            shard_id=sid,
            lineage_id=sid,
            medium="doc",
            repo="athena-mcp-server",
            lens=None,
            dimensional_scope="all",
            payload_ref=f"guild_hall/{fp.name}",
            summary=first_line,
            seed_vector=[0.25, 0.25, 0.25, 0.25],
            route_refs=["Cc"],  # Crown Circuit — governance
            cert_refs=[],
            mirror_refs=[],
            truth_status="CANONICAL",
            promotion_status="PROMOTED",
            family="guild_hall",
            tags=[stem[:40], "guild_hall", "guild"],
            created_at=NOW,
            updated_at=NOW,
        ))

    return shards


def scan_json_data() -> list[Shard]:
    """Scan MCP/data/*.json and create shards."""
    shards = []
    for fp in sorted(DATA_DIR.glob("*.json")):
        stem = fp.stem
        rel = f"data/{fp.name}"
        sid = make_shard_id("json", rel)
        title = _extract_json_title(fp)
        family = _infer_family(stem)

        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            data = {}

        shards.append(Shard(
            shard_id=sid,
            lineage_id=sid,
            medium="json",
            repo="athena-mcp-server",
            lens=None,
            dimensional_scope=_infer_dimensional_scope(data, stem),
            payload_ref=rel,
            summary=title,
            seed_vector=_infer_seed_vector(family, None),
            route_refs=[],
            cert_refs=[],
            mirror_refs=[],
            truth_status="CANONICAL",
            promotion_status="PROMOTED",
            family=family,
            tags=[stem],
            created_at=NOW,
            updated_at=NOW,
        ))
    return shards

def scan_crystal_modules() -> list[Shard]:
    """Scan MCP/crystal_108d/*.py and create shards."""
    shards = []
    for fp in sorted(CRYSTAL_DIR.glob("*.py")):
        if fp.stem in SKIP_MODULES:
            continue
        rel = f"crystal_108d/{fp.name}"
        sid = make_shard_id("code", rel)
        summary = _extract_docstring(fp)
        family = MODULE_FAMILY_MAP.get(fp.stem, fp.stem)

        shards.append(Shard(
            shard_id=sid,
            lineage_id=sid,
            medium="code",
            repo="athena-mcp-server",
            lens=None,
            dimensional_scope="all",
            payload_ref=rel,
            summary=summary,
            seed_vector=[0.25, 0.25, 0.25, 0.25],
            route_refs=[],
            cert_refs=[],
            mirror_refs=[],
            truth_status="CANONICAL",
            promotion_status="PROMOTED",
            family=family,
            tags=[fp.stem, "tool_module"],
            created_at=NOW,
            updated_at=NOW,
        ))
    return shards

def scan_element_servers() -> list[Shard]:
    """Scan MCP/element_servers/*.py and create shards."""
    shards = []
    for fp in sorted(ELEMENT_DIR.glob("*.py")):
        if fp.stem == "__init__":
            continue
        rel = f"element_servers/{fp.name}"
        sid = make_shard_id("code", rel)
        summary = _extract_docstring(fp)
        lens = ELEMENT_LENS.get(fp.stem)
        family = "brain"

        shards.append(Shard(
            shard_id=sid,
            lineage_id=sid,
            medium="code",
            repo="athena-mcp-server",
            lens=lens,
            dimensional_scope="all",
            payload_ref=rel,
            summary=summary,
            seed_vector=_infer_seed_vector(family, lens),
            route_refs=[],
            cert_refs=[],
            mirror_refs=[],
            truth_status="CANONICAL",
            promotion_status="PROMOTED",
            family=family,
            tags=[fp.stem, "element_server", f"lens_{lens}"],
            created_at=NOW,
            updated_at=NOW,
        ))
    return shards

def scan_main_server() -> Shard:
    """Create a shard for the main server entry point."""
    rel = "athena_mcp_server.py"
    sid = make_shard_id("code", rel)
    return Shard(
        shard_id=sid,
        lineage_id=sid,
        medium="code",
        repo="athena-mcp-server",
        lens=None,
        dimensional_scope="all",
        payload_ref=rel,
        summary="Athena MCP Server — unified 64-tool entry point",
        seed_vector=[0.25, 0.25, 0.25, 0.25],
        route_refs=[],
        cert_refs=[],
        mirror_refs=[],
        truth_status="CANONICAL",
        promotion_status="PROMOTED",
        family="server",
        tags=["entry_point", "mcp_server"],
        created_at=NOW,
        updated_at=NOW,
    )

def scan_guild_hall() -> list[Shard]:
    """Scan Guild Hall markdown files and create shards."""
    shards = []
    if not GUILD_HALL_DIR.exists():
        return shards
    for fp in sorted(GUILD_HALL_DIR.glob("**/*.md")):
        rel = str(fp.relative_to(GUILD_HALL_DIR.parent.parent.parent))
        sid = make_shard_id("doc", rel)
        title = fp.stem.replace("_", " ").title()
        # Infer family from path
        if "BOARDS" in str(fp):
            family = "quest"
        elif "SYNTHESIS" in str(fp) or "SYNTHESIS" in fp.stem:
            family = "synthesis"
        elif "PROMOTION" in str(fp) or "WITNESS" in str(fp):
            family = "guild_hall"
        else:
            family = "guild_hall"

        shards.append(Shard(
            shard_id=sid,
            lineage_id=sid,
            medium="doc",
            repo="athena-mcp-server",
            lens=None,
            dimensional_scope="all",
            payload_ref=rel,
            summary=title,
            seed_vector=[0.25, 0.25, 0.25, 0.25],
            route_refs=[],
            cert_refs=[],
            mirror_refs=[],
            truth_status="CANONICAL",
            promotion_status="PROMOTED",
            family=family,
            tags=[fp.stem, "guild_hall"],
            created_at=NOW,
            updated_at=NOW,
        ))
    return shards

def scan_manuscript_being() -> list[Shard]:
    """Scan the manuscript-being Python framework modules."""
    shards = []
    src_dir = ATHENA_REPO_DIR / "src" / "athena"
    if not src_dir.exists():
        return shards
    for fp in sorted(src_dir.glob("**/*.py")):
        if fp.stem.startswith("_"):
            continue
        rel = str(fp.relative_to(ATHENA_REPO_DIR))
        sid = make_shard_id("code", f"manuscript-being/{rel}")
        summary = _extract_docstring(fp)
        family = MANUSCRIPT_MODULE_FAMILY.get(fp.stem, fp.parent.name)

        shards.append(Shard(
            shard_id=sid,
            lineage_id=sid,
            medium="code",
            repo="manuscript-being",
            lens=None,
            dimensional_scope="all",
            payload_ref=rel,
            summary=summary,
            seed_vector=[0.25, 0.25, 0.25, 0.25],
            route_refs=[],
            cert_refs=[],
            mirror_refs=[],
            truth_status="CANONICAL",
            promotion_status="PROMOTED",
            family=family,
            tags=[fp.stem, "manuscript_being", fp.parent.name],
            created_at=NOW,
            updated_at=NOW,
        ))
    return shards

def scan_full_organism() -> list[Shard]:
    """Scan the ENTIRE Athena Agent organism — every directory, every file.

    Maps each file to:
    - SFCR element affinity (primary + secondary lens)
    - Metro line class (Sa/Wr/Ac/Me/Mt/Bw/Cc/Dl)
    - Family (organism organ)
    - Medium (code/doc/json/web/config)

    Skips: .git, .venv, node_modules, MCP/ (already scanned), tests/
    """
    shards = []
    root = _MCP_DIR.parent  # Athena Agent root

    def _medium_for(ext: str) -> str:
        if ext in (".py", ".js", ".ts"):
            return "code"
        if ext in (".md",):
            return "doc"
        if ext in (".json",):
            return "json"
        if ext in (".html", ".css"):
            return "web"
        if ext in (".yaml", ".yml"):
            return "config"
        return "doc"

    def _should_skip(parts: tuple[str, ...]) -> bool:
        """Check if any path component is in the skip set."""
        for p in parts:
            if p in ORGANISM_SKIP_DIRS:
                return True
            if p.endswith(".egg-info"):
                return True
        return False

    def _lookup_dir(rel_parts: tuple[str, ...]) -> tuple[str, str, str, str]:
        """Find best SFCR/metro mapping for a file's directory path.
        Returns (primary_lens, secondary_lens, metro_line, family).
        Checks subdirectory overrides first, then top-level directory.
        """
        # Try subdirectory overrides (most specific first)
        for depth in range(min(3, len(rel_parts)), 0, -1):
            subpath = "/".join(rel_parts[:depth])
            if subpath in ORGANISM_SUBDIR_MAP:
                return ORGANISM_SUBDIR_MAP[subpath]

        # Fall back to top-level directory
        if rel_parts and rel_parts[0] in ORGANISM_DIR_MAP:
            return ORGANISM_DIR_MAP[rel_parts[0]]

        # Unknown directory — balanced
        return ("S", "C", "Bw", "misc")

    def _seed_vector(primary: str, secondary: str) -> list[float]:
        """Compute SFCR seed vector from primary+secondary lens."""
        vec = [0.1, 0.1, 0.1, 0.1]
        idx = {"S": 0, "F": 1, "C": 2, "R": 3}
        vec[idx.get(primary, 0)] = 0.6
        vec[idx.get(secondary, 1)] = 0.2
        return vec

    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dp = Path(dirpath)
        rel = dp.relative_to(root)
        parts = rel.parts if str(rel) != "." else ()

        # Filter out skip directories in-place (prunes os.walk)
        dirnames[:] = [d for d in dirnames if d not in ORGANISM_SKIP_DIRS
                       and not d.endswith(".egg-info")]

        # Skip top-level dirs already scanned by other functions
        if parts and parts[0] in ("MCP", "tests"):
            dirnames.clear()
            continue

        for fname in filenames:
            fp = dp / fname
            ext = fp.suffix.lower()
            if ext not in ORGANISM_EXTENSIONS:
                continue

            file_rel = fp.relative_to(root)
            file_parts = file_rel.parts
            dir_parts = file_parts[:-1]

            if _should_skip(file_parts):
                continue

            primary, secondary, metro, family = _lookup_dir(dir_parts)
            medium = _medium_for(ext)
            rel_str = str(file_rel).replace("\\", "/")
            sid = make_shard_id(medium, f"organism/{rel_str}")

            # Build summary from filename
            stem = fp.stem
            if ext == ".py":
                summary = _extract_docstring(fp)
            elif ext == ".md" and stem.startswith("#"):
                summary = stem.lstrip("# ").strip()[:80]
            else:
                summary = stem.replace("_", " ").replace("-", " ").title()[:80]

            # Compute HPRO CODE_KEY for this file
            hpro = _compute_hpro_code_key(rel_str, len(dir_parts), ext, stem)

            # Assign HPRO metro lines based on element + level
            hpro_routes = [metro]  # original Athena metro line
            if hpro["element"] == "Fire":
                hpro_routes.append("Ω")  # compute touches zero-point
            if hpro["element"] == "Air":
                hpro_routes.append("□")  # interfaces = addressing
            if hpro["element"] == "Water":
                hpro_routes.append("T")  # state = truth corridor
            if hpro["element"] == "Earth":
                hpro_routes.append("✶")  # storage = holographic seed
            if hpro["level"] >= 2:
                hpro_routes.append("○")  # package+ = convergence circle
            if "seed" in stem.lower() or "compress" in stem.lower():
                hpro_routes.append("w")  # seed/compress = generator line
            if "migration" in stem.lower() or "migrate" in stem.lower():
                hpro_routes.append("M")  # migration evolution line

            shards.append(Shard(
                shard_id=sid,
                lineage_id=sid,
                medium=medium,
                repo="manuscript-being",
                lens=primary,
                dimensional_scope="all",
                payload_ref=rel_str,
                summary=summary,
                seed_vector=_seed_vector(primary, secondary),
                route_refs=hpro_routes,
                cert_refs=[],
                mirror_refs=[],
                truth_status="CANONICAL",
                promotion_status="PROMOTED",
                family=family,
                tags=[stem[:40], f"lens_{primary}", f"metro_{metro}", family,
                      dir_parts[0] if dir_parts else "root",
                      f"hpro_L{hpro['level']}", f"hpro_{hpro['element']}",
                      f"hpro_{hpro['phase']}"],
                created_at=NOW,
                updated_at=NOW,
            ))
            scanned += 1

    print(f"  scanned {scanned} organism files")
    return shards

# ── Edge Building ───────────────────────────────────────────────────

def build_edges(shards: list[Shard]) -> list[Edge]:
    """Build typed edges from shard relationships."""
    edges = []
    shard_by_ref = {s.payload_ref: s.shard_id for s in shards}
    shard_by_stem = {}
    for s in shards:
        stem = s.payload_ref.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        shard_by_stem[stem] = s.shard_id

    # BUILD edges: code modules → their JsonCache data files
    for fp in sorted(CRYSTAL_DIR.glob("*.py")):
        if fp.stem in SKIP_MODULES:
            continue
        code_ref = f"crystal_108d/{fp.name}"
        code_sid = shard_by_ref.get(code_ref)
        if not code_sid:
            continue

        for json_name in _extract_json_caches(fp):
            data_ref = f"data/{json_name}"
            data_sid = shard_by_ref.get(data_ref)
            if data_sid:
                eid = make_edge_id(code_sid, data_sid, "BUILD")
                edges.append(Edge(
                    edge_id=eid,
                    source_shard=code_sid,
                    target_shard=data_sid,
                    edge_type="BUILD",
                    weight=0.8,
                    medium_cross=False,
                    metadata={"json_file": json_name},
                ))

    # BRIDGE edges: element servers → brain_network entry
    brain_sid = shard_by_ref.get("data/brain_network.json")
    if brain_sid:
        for fp in sorted(ELEMENT_DIR.glob("*.py")):
            if fp.stem == "__init__":
                continue
            srv_ref = f"element_servers/{fp.name}"
            srv_sid = shard_by_ref.get(srv_ref)
            if srv_sid:
                eid = make_edge_id(srv_sid, brain_sid, "BRIDGE")
                edges.append(Edge(
                    edge_id=eid,
                    source_shard=srv_sid,
                    target_shard=brain_sid,
                    edge_type="BRIDGE",
                    weight=0.618,
                    medium_cross=False,
                    metadata={"bridge_type": "element_to_brain"},
                ))

    # MIRROR edges: element servers ↔ main server
    main_sid = shard_by_ref.get("athena_mcp_server.py")
    if main_sid:
        for fp in sorted(ELEMENT_DIR.glob("*.py")):
            if fp.stem == "__init__":
                continue
            srv_ref = f"element_servers/{fp.name}"
            srv_sid = shard_by_ref.get(srv_ref)
            if srv_sid:
                eid = make_edge_id(srv_sid, main_sid, "MIRROR")
                edges.append(Edge(
                    edge_id=eid,
                    source_shard=srv_sid,
                    target_shard=main_sid,
                    edge_type="MIRROR",
                    weight=0.5,
                    medium_cross=False,
                    metadata={"mirror_type": "lobe_to_unified"},
                ))

    # REF edges: MCP data JSON files in same family (NOT organism JSON files)
    family_groups: dict[str, list[str]] = {}
    for s in shards:
        if s.medium == "json" and s.repo == "athena-mcp-server":
            family_groups.setdefault(s.family, []).append(s.shard_id)
    for family, sids in family_groups.items():
        if len(sids) > 1:
            for i, a in enumerate(sids):
                for b in sids[i + 1:]:
                    eid = make_edge_id(a, b, "REF")
                    edges.append(Edge(
                        edge_id=eid,
                        source_shard=a,
                        target_shard=b,
                        edge_type="REF",
                        weight=0.7,
                        medium_cross=False,
                        metadata={"family": family},
                    ))

    # BRIDGE edges: guild hall shards → MCP data shards
    guild_shards = [s for s in shards if "guild_hall" in s.tags]
    mcp_data_shards = [s for s in shards if s.medium == "json"]
    if guild_shards and mcp_data_shards:
        # Connect guild hall to brain_network
        if brain_sid:
            for gs in guild_shards:
                eid = make_edge_id(gs.shard_id, brain_sid, "BRIDGE")
                edges.append(Edge(
                    edge_id=eid,
                    source_shard=gs.shard_id,
                    target_shard=brain_sid,
                    edge_type="BRIDGE",
                    weight=0.5,
                    medium_cross=True,
                    metadata={"bridge_type": "guild_hall_to_brain"},
                ))

    # BRIDGE edges: manuscript-being modules → MCP tool modules
    ms_shards = [s for s in shards if s.repo == "manuscript-being"]
    mcp_code_shards = [s for s in shards if s.repo == "athena-mcp-server" and s.medium == "code"]
    for ms in ms_shards:
        # Connect manuscript-being modules to their MCP counterparts by family
        for mcp in mcp_code_shards:
            if ms.family == mcp.family or ms.family in mcp.tags:
                eid = make_edge_id(ms.shard_id, mcp.shard_id, "BRIDGE")
                edges.append(Edge(
                    edge_id=eid,
                    source_shard=ms.shard_id,
                    target_shard=mcp.shard_id,
                    edge_type="BRIDGE",
                    weight=0.618,
                    medium_cross=False,
                    metadata={"bridge_type": "manuscript_to_mcp"},
                ))
                break  # one bridge per manuscript module

    # SEEDS edge: main server → all element servers
    if main_sid:
        for fp in sorted(ELEMENT_DIR.glob("*.py")):
            if fp.stem == "__init__":
                continue
            srv_ref = f"element_servers/{fp.name}"
            srv_sid = shard_by_ref.get(srv_ref)
            if srv_sid:
                eid = make_edge_id(main_sid, srv_sid, "SEEDS")
                edges.append(Edge(
                    edge_id=eid,
                    source_shard=main_sid,
                    target_shard=srv_sid,
                    edge_type="SEEDS",
                    weight=0.9,
                    medium_cross=False,
                    metadata={"seed_type": "unified_to_lobe"},
                ))

    # ── METRO edges: organism shards sharing the same metro line ──
    # Group organism shards by metro line, then connect shards within each line
    metro_groups: dict[str, list[Shard]] = {}
    for s in shards:
        for route in (s.route_refs or []):
            if route in METRO_LINES:
                metro_groups.setdefault(route, []).append(s)

    for metro_code, group in metro_groups.items():
        # Connect each shard to the next in the group (chain topology)
        # Limit to avoid O(n^2) explosion — chain, not full mesh
        metro_weight = METRO_WEIGHT_HIERARCHY.get(metro_code, METRO_WEIGHT_DEFAULT)
        for i in range(len(group) - 1):
            a, b = group[i], group[i + 1]
            eid = make_edge_id(a.shard_id, b.shard_id, "METRO")
            edges.append(Edge(
                edge_id=eid,
                source_shard=a.shard_id,
                target_shard=b.shard_id,
                edge_type="METRO",
                weight=metro_weight,
                medium_cross=(a.medium != b.medium),
                metadata={"metro_line": metro_code, "line_name": METRO_LINES[metro_code]["name"]},
            ))

    # ── BRIDGE edges: organism shards → MCP tool modules by SFCR lens ──
    # Connect organism files with matching lens to the corresponding element server
    element_server_sids = {}
    for fp in sorted(ELEMENT_DIR.glob("*.py")):
        if fp.stem == "__init__":
            continue
        lens = ELEMENT_LENS.get(fp.stem)
        if lens:
            element_server_sids[lens] = shard_by_ref.get(f"element_servers/{fp.name}")

    organism_shards = [s for s in shards if s.repo == "manuscript-being" and s.lens]
    # Sample: connect first shard of each family to its element server (avoid explosion)
    family_connected: dict[tuple[str, str], bool] = {}
    for os_shard in organism_shards:
        key = (os_shard.family, os_shard.lens)
        if key in family_connected:
            continue
        srv_sid = element_server_sids.get(os_shard.lens)
        if srv_sid:
            eid = make_edge_id(os_shard.shard_id, srv_sid, "BRIDGE")
            edges.append(Edge(
                edge_id=eid,
                source_shard=os_shard.shard_id,
                target_shard=srv_sid,
                edge_type="BRIDGE",
                weight=0.4,
                medium_cross=True,
                metadata={"bridge_type": "organism_to_element", "family": os_shard.family},
            ))
            family_connected[key] = True

    # ── BRIDGE edges: organism families → brain_network ──
    if brain_sid:
        organism_families_seen = set()
        for os_shard in organism_shards:
            if os_shard.family not in organism_families_seen:
                organism_families_seen.add(os_shard.family)
                eid = make_edge_id(os_shard.shard_id, brain_sid, "BRIDGE")
                edges.append(Edge(
                    edge_id=eid,
                    source_shard=os_shard.shard_id,
                    target_shard=brain_sid,
                    edge_type="BRIDGE",
                    weight=0.3,
                    medium_cross=True,
                    metadata={"bridge_type": "organism_family_to_brain", "family": os_shard.family},
                ))

    # ── CHAPTER edges: document shards → chapter/appendix shards ──
    chapter_shards_map = {}   # "Ch01" → shard_id
    appendix_shards_map = {}  # "AppA" → shard_id
    for s in shards:
        if s.shard_id.startswith("chapter:Ch"):
            key = s.shard_id.split(":")[1]  # "Ch01"
            chapter_shards_map[key] = s.shard_id
        elif s.shard_id.startswith("appendix:App"):
            key = s.shard_id.split(":")[1]  # "AppA"
            appendix_shards_map[key] = s.shard_id

    if chapter_shards_map or appendix_shards_map:
        _ch_ref_re = re.compile(r'Ch(?:apter)?[_\s]*(\d{1,2})', re.IGNORECASE)
        _app_ref_re = re.compile(r'App(?:endix)?[_\s]*([A-P])', re.IGNORECASE)
        chapter_edge_count = 0
        chapter_edge_set = set()

        for s in shards:
            ext = s.payload_ref.rsplit(".", 1)[-1] if "." in s.payload_ref else ""
            if ext not in ("md", "py", "json"):
                continue
            if s.shard_id.startswith("chapter:") or s.shard_id.startswith("appendix:"):
                continue
            # Resolve file path
            if s.payload_ref.startswith("organism/"):
                fp = root / s.payload_ref[len("organism/"):]
            elif any(s.payload_ref.startswith(p) for p in ("crystal_108d/", "data/", "element_servers/")):
                fp = _MCP_DIR / s.payload_ref
            else:
                fp = _MCP_DIR / s.payload_ref
            if not fp.exists():
                continue
            try:
                text = fp.read_text(encoding="utf-8", errors="replace")[:8000]
            except Exception:
                continue
            for m in _ch_ref_re.finditer(text):
                ch_num = int(m.group(1))
                if ch_num < 1 or ch_num > 21:
                    continue
                ch_key = f"Ch{ch_num:02d}"
                tgt_sid = chapter_shards_map.get(ch_key)
                if tgt_sid:
                    edge_key = (s.shard_id, tgt_sid)
                    if edge_key not in chapter_edge_set:
                        chapter_edge_set.add(edge_key)
                        w = 0.9 if ch_num in ZERO_POINT_CHAPTERS else 0.7
                        eid = make_edge_id(s.shard_id, tgt_sid, "CHAPTER")
                        edges.append(Edge(
                            edge_id=eid,
                            source_shard=s.shard_id,
                            target_shard=tgt_sid,
                            edge_type="CHAPTER",
                            weight=w,
                            medium_cross=(s.medium != "doc"),
                            metadata={"chapter": ch_key, "zero_point": ch_num in ZERO_POINT_CHAPTERS},
                        ))
                        chapter_edge_count += 1
            for m in _app_ref_re.finditer(text):
                app_letter = m.group(1).upper()
                app_key = f"App{app_letter}"
                tgt_sid = appendix_shards_map.get(app_key)
                if tgt_sid:
                    edge_key = (s.shard_id, tgt_sid)
                    if edge_key not in chapter_edge_set:
                        chapter_edge_set.add(edge_key)
                        eid = make_edge_id(s.shard_id, tgt_sid, "CHAPTER")
                        edges.append(Edge(
                            edge_id=eid,
                            source_shard=s.shard_id,
                            target_shard=tgt_sid,
                            edge_type="CHAPTER",
                            weight=0.7,
                            medium_cross=(s.medium != "doc"),
                            metadata={"appendix": app_key},
                        ))
                        chapter_edge_count += 1
        print(f"  {chapter_edge_count} CHAPTER edges (document → chapter/appendix)")

    # ── Google Doc MIRROR edges ──
    gdoc_mirror_count = 0
    gdoc_bridge_map = {
        "gdoc:emergence_master_plan": ["emergence", "dimensional_emergence", "actualize"],
        "gdoc:athena_skills": ["guild_hall", "quest", "synthesis"],
        "gdoc:brain_stem": ["brain", "nervous", "nervous_overview"],
    }
    # Pre-build family index for this phase
    _fam_to_sids: dict[str, list[str]] = {}
    for s in shards:
        _fam_to_sids.setdefault(s.family, []).append(s.shard_id)
    for gdoc_sid, target_families in gdoc_bridge_map.items():
        if not any(s.shard_id == gdoc_sid for s in shards):
            continue
        for fam in target_families:
            targets = _fam_to_sids.get(fam, [])
            for tgt_sid in targets[:3]:
                eid = make_edge_id(gdoc_sid, tgt_sid, "MIRROR")
                edges.append(Edge(
                    edge_id=eid,
                    source_shard=gdoc_sid,
                    target_shard=tgt_sid,
                    edge_type="MIRROR",
                    weight=0.5,
                    medium_cross=True,
                    metadata={"mirror_type": "gdoc_to_repo"},
                ))
                gdoc_mirror_count += 1
    print(f"  {gdoc_mirror_count} Google Doc MIRROR edges")

    # ── Guild Hall → Chapter/Organ BRIDGE edges ──
    guild_bridge_count = 0
    guild_shards_indexed = [s for s in shards if s.shard_id.startswith("guild:")]
    ch_keyword_map_local: dict[str, list[str]] = {}
    for n, title in CHAPTER_TITLES.items():
        for kw in [title.lower()] + CHAPTER_TAGS.get(n, []):
            ch_keyword_map_local.setdefault(kw, []).append(f"chapter:Ch{n:02d}")

    shard_by_id_local = {s.shard_id: s for s in shards}
    for gs in guild_shards_indexed:
        name_lower = gs.shard_id.replace("guild:", "").lower()
        matched_chapters = set()
        for kw, ch_sids in ch_keyword_map_local.items():
            if kw in name_lower:
                for ch_sid in ch_sids:
                    matched_chapters.add(ch_sid)
        if "synthesis" in name_lower or "integration" in name_lower:
            matched_chapters.add("chapter:Ch10")
        if "emergence" in name_lower or "emergent" in name_lower:
            matched_chapters.add("chapter:Ch12")
        if "quest" in name_lower or "temple" in name_lower:
            matched_chapters.add("chapter:Ch11")
        if "promotion" in name_lower or "witness" in name_lower:
            matched_chapters.add("chapter:Ch08")
        if "command" in name_lower or "protocol" in name_lower:
            matched_chapters.add("chapter:Ch04")
        if "heaven" in name_lower or "reward" in name_lower:
            matched_chapters.add("chapter:Ch21")
        if "awakening" in name_lower or "transition" in name_lower:
            matched_chapters.add("chapter:Ch07")
        if "loop" in name_lower or "57" in name_lower:
            matched_chapters.add("chapter:Ch03")
        if "organism" in name_lower:
            matched_chapters.add("chapter:Ch10")
        if "swarm" in name_lower or "hive" in name_lower:
            matched_chapters.add("chapter:Ch16")
        if not matched_chapters:
            matched_chapters.add("chapter:Ch11")
        for ch_sid in list(matched_chapters)[:5]:
            if ch_sid in shard_by_id_local:
                eid = make_edge_id(gs.shard_id, ch_sid, "BRIDGE")
                edges.append(Edge(
                    edge_id=eid,
                    source_shard=gs.shard_id,
                    target_shard=ch_sid,
                    edge_type="BRIDGE",
                    weight=0.55,
                    medium_cross=False,
                    metadata={"bridge_type": "guild_to_chapter"},
                ))
                guild_bridge_count += 1
        if brain_sid:
            eid = make_edge_id(gs.shard_id, brain_sid, "BRIDGE")
            edges.append(Edge(
                edge_id=eid,
                source_shard=gs.shard_id,
                target_shard=brain_sid,
                edge_type="BRIDGE",
                weight=0.4,
                medium_cross=True,
                metadata={"bridge_type": "guild_to_brain"},
            ))
            guild_bridge_count += 1
    print(f"  {guild_bridge_count} guild hall BRIDGE edges")

    # ══════════════════════════════════════════════════════════════════
    # PHASE 2: Dense connectivity edges (REF, BUILD, MIRROR, BRIDGE, SEEDS)
    # ══════════════════════════════════════════════════════════════════
    old_edge_count = len(edges)
    old_edge_dist = {}
    for e in edges:
        old_edge_dist[e.edge_type] = old_edge_dist.get(e.edge_type, 0) + 1

    root = _MCP_DIR.parent
    # Build indexes for efficient lookup
    shard_by_id = {s.shard_id: s for s in shards}
    # Index: filename (no ext) → list of shard_ids
    stem_to_shards: dict[str, list[str]] = {}
    for s in shards:
        stem = s.payload_ref.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        stem_to_shards.setdefault(stem, []).append(s.shard_id)
    # Index: family → list of shard_ids
    family_to_shards: dict[str, list[str]] = {}
    for s in shards:
        family_to_shards.setdefault(s.family, []).append(s.shard_id)
    # Index: directory → list of shard_ids
    dir_to_shards: dict[str, list[str]] = {}
    for s in shards:
        d = s.payload_ref.rsplit("/", 1)[0] if "/" in s.payload_ref else ""
        dir_to_shards.setdefault(d, []).append(s.shard_id)

    new_edge_set = set()  # deduplicate by (source, target, type)
    MAX_NEW_EDGES = 5000

    def _add_edge(src_sid, tgt_sid, etype, weight, metadata, medium_cross=False):
        """Add a new edge if under the cap and not duplicate."""
        if len(new_edge_set) >= MAX_NEW_EDGES:
            return
        if src_sid == tgt_sid:
            return
        key = (src_sid, tgt_sid, etype)
        if key in new_edge_set:
            return
        new_edge_set.add(key)
        eid = make_edge_id(src_sid, tgt_sid, etype)
        edges.append(Edge(
            edge_id=eid,
            source_shard=src_sid,
            target_shard=tgt_sid,
            edge_type=etype,
            weight=weight,
            medium_cross=medium_cross,
            metadata=metadata,
        ))

    # ── 1. Content-Reference Edges (REF) ──────────────────────────────
    # Scan markdown and Python files for references to other files
    print("  Phase 2: Content-Reference edges (REF) ...")
    _ref_patterns = [
        re.compile(r'capsule[_\s]*(\d{1,4})', re.IGNORECASE),    # capsule 315, capsule_042
        re.compile(r'Ch(?:apter)?[_\s]*(\d{1,3})', re.IGNORECASE),  # Ch11, Chapter 7
        re.compile(r'["\']([A-Za-z0-9_/.-]+\.(?:py|md|json))["\']'),  # "file.py", 'data.json'
        re.compile(r'\b([A-Za-z0-9_-]{3,40})\.(?:py|md|json)\b'),  # filename.py bare refs
    ]
    ref_count = 0
    for s in shards:
        if len(new_edge_set) >= MAX_NEW_EDGES:
            break
        ext = s.payload_ref.rsplit(".", 1)[-1] if "." in s.payload_ref else ""
        if ext not in ("md", "py"):
            continue
        # Resolve the actual file path
        if s.payload_ref.startswith("organism/"):
            fp = root / s.payload_ref[len("organism/"):]
        elif s.payload_ref.startswith("crystal_108d/") or s.payload_ref.startswith("data/") or s.payload_ref.startswith("element_servers/"):
            fp = _MCP_DIR / s.payload_ref
        else:
            fp = _MCP_DIR / s.payload_ref
        if not fp.exists():
            continue
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")[:8000]  # first 8KB
        except Exception:
            continue
        for pat in _ref_patterns:
            for m in pat.finditer(text):
                ref_name = m.group(1) if m.lastindex else m.group(0)
                # Strip extension to get stem
                ref_stem = ref_name.rsplit(".", 1)[0].rsplit("/", 1)[-1]
                # Find target shards with matching stem
                targets = stem_to_shards.get(ref_stem, [])
                for tgt in targets[:3]:  # max 3 targets per reference
                    _add_edge(s.shard_id, tgt, "REF", 0.6,
                              {"ref_type": "content_reference", "ref_name": ref_name},
                              medium_cross=(shard_by_id[tgt].medium != s.medium if tgt in shard_by_id else False))
                    ref_count += 1
    print(f"    +{ref_count} content-reference REF edges")

    # ── 2. Import-Graph Edges (BUILD) ─────────────────────────────────
    # Parse Python import statements and map to file shards
    print("  Phase 2: Import-Graph edges (BUILD) ...")
    _import_re = re.compile(r'^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))', re.MULTILINE)
    build_count = 0
    py_shards = [s for s in shards if s.payload_ref.endswith(".py")]
    for s in py_shards:
        if len(new_edge_set) >= MAX_NEW_EDGES:
            break
        if s.payload_ref.startswith("organism/"):
            fp = root / s.payload_ref[len("organism/"):]
        elif s.payload_ref.startswith("crystal_108d/") or s.payload_ref.startswith("data/") or s.payload_ref.startswith("element_servers/"):
            fp = _MCP_DIR / s.payload_ref
        else:
            fp = _MCP_DIR / s.payload_ref
        if not fp.exists():
            continue
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")[:5000]
        except Exception:
            continue
        for m in _import_re.finditer(text):
            mod_name = (m.group(1) or m.group(2)).split(".")[-1]  # last component
            targets = stem_to_shards.get(mod_name, [])
            for tgt in targets[:2]:
                if tgt != s.shard_id:
                    _add_edge(s.shard_id, tgt, "BUILD", 0.75,
                              {"build_type": "import", "module": mod_name})
                    build_count += 1
    print(f"    +{build_count} import-graph BUILD edges")

    # ── 3. Cross-Medium Mirror Edges (MIRROR) ─────────────────────────
    # Connect files of different types that share the same stem name
    print("  Phase 2: Cross-Medium Mirror edges (MIRROR) ...")
    mirror_count = 0
    for stem_name, sids in stem_to_shards.items():
        if len(new_edge_set) >= MAX_NEW_EDGES:
            break
        if len(sids) < 2:
            continue
        # Group by medium
        by_medium: dict[str, list[str]] = {}
        for sid in sids:
            s = shard_by_id.get(sid)
            if s:
                by_medium.setdefault(s.medium, []).append(sid)
        mediums_present = list(by_medium.keys())
        if len(mediums_present) < 2:
            continue
        # Connect one representative from each medium to each other medium
        for i in range(len(mediums_present)):
            for j in range(i + 1, len(mediums_present)):
                src_list = by_medium[mediums_present[i]]
                tgt_list = by_medium[mediums_present[j]]
                for src in src_list[:2]:
                    for tgt in tgt_list[:2]:
                        _add_edge(src, tgt, "MIRROR", 0.65,
                                  {"mirror_type": "cross_medium_stem", "stem": stem_name},
                                  medium_cross=True)
                        mirror_count += 1
    # Also: .json data files → .py query modules in crystal_108d
    for s in shards:
        if s.medium == "json" and s.repo == "athena-mcp-server":
            stem_name = s.payload_ref.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            py_targets = stem_to_shards.get(stem_name, [])
            for tgt in py_targets:
                tgt_s = shard_by_id.get(tgt)
                if tgt_s and tgt_s.medium == "code":
                    _add_edge(s.shard_id, tgt, "MIRROR", 0.7,
                              {"mirror_type": "json_to_query_module", "stem": stem_name},
                              medium_cross=True)
                    mirror_count += 1
    print(f"    +{mirror_count} cross-medium MIRROR edges")

    # ── 4. Cross-Project Bridge Edges (BRIDGE) ────────────────────────
    # Connect related files across different project directories
    print("  Phase 2: Cross-Project Bridge edges (BRIDGE) ...")
    bridge_count = 0

    # 4a. QSHRINK ↔ crystal_108d (compression/encoding theme)
    qshrink_sids = [s.shard_id for s in shards
                    if "qshrink" in s.family or "QSHRINK" in s.payload_ref]
    crystal_encoding_sids = [s.shard_id for s in shards
                             if s.payload_ref.startswith("crystal_108d/")
                             and any(k in s.payload_ref.lower() for k in ("inverse", "seed", "mobius", "hologram"))]
    for qs in qshrink_sids[:20]:
        for cs in crystal_encoding_sids[:10]:
            _add_edge(qs, cs, "BRIDGE", 0.5,
                      {"bridge_type": "qshrink_to_crystal"}, medium_cross=True)
            bridge_count += 1

    # 4b. NEURAL_NETWORK ↔ crystal_108d (neural/control theme)
    neural_sids = [s.shard_id for s in shards
                   if "neural" in s.family or "NEURAL" in s.payload_ref]
    crystal_control_sids = [s.shard_id for s in shards
                            if s.payload_ref.startswith("crystal_108d/")
                            and any(k in s.payload_ref.lower() for k in ("brain", "live_lock", "conservation", "emergence"))]
    for ns in neural_sids[:20]:
        for cs in crystal_control_sids[:10]:
            _add_edge(ns, cs, "BRIDGE", 0.5,
                      {"bridge_type": "neural_to_crystal"}, medium_cross=True)
            bridge_count += 1

    # 4c. Corpus capsules ↔ accepted inputs
    corpus_sids = [s for s in shards if "corpus" in s.family or "20_CORPUS" in s.payload_ref]
    accepted_sids = [s for s in shards if "accepted" in s.family or "ACCEPTED_INPUT" in s.payload_ref
                     or "13_ACCEPTED" in s.payload_ref]
    for cs in corpus_sids[:30]:
        for ais in accepted_sids[:15]:
            _add_edge(cs.shard_id, ais.shard_id, "BRIDGE", 0.55,
                      {"bridge_type": "corpus_to_accepted"}, medium_cross=(cs.medium != ais.medium))
            bridge_count += 1

    # 4d. Cross-directory same-family bridges
    # For each family with shards in multiple directories, connect across directories
    family_by_dir: dict[str, dict[str, list[str]]] = {}  # family → dir → [shard_ids]
    for s in shards:
        d = s.payload_ref.rsplit("/", 1)[0] if "/" in s.payload_ref else ""
        family_by_dir.setdefault(s.family, {}).setdefault(d, []).append(s.shard_id)
    for family, dirs in family_by_dir.items():
        if len(new_edge_set) >= MAX_NEW_EDGES:
            break
        dir_keys = list(dirs.keys())
        if len(dir_keys) < 2:
            continue
        # Connect one representative from each directory to the next
        for i in range(len(dir_keys) - 1):
            for j in range(i + 1, min(i + 4, len(dir_keys))):  # limit fan-out
                src = dirs[dir_keys[i]][0]
                tgt = dirs[dir_keys[j]][0]
                _add_edge(src, tgt, "BRIDGE", 0.45,
                          {"bridge_type": "cross_dir_family", "family": family})
                bridge_count += 1
    print(f"    +{bridge_count} cross-project BRIDGE edges")

    # ── 5. Seed Edges (SEEDS) ─────────────────────────────────────────
    # Connect deep core files to their consumers; INDEX files to indexed files
    print("  Phase 2: Seed edges (SEEDS) ...")
    seed_count = 0

    # 5a. Core crystal_108d files → all code that imports/references them
    core_stems = {"constants", "conservation", "metabolism", "shells", "dimensions",
                  "address", "brain", "live_lock", "angel", "hologram_reading"}
    core_sids = {}
    for stem_name in core_stems:
        candidates = stem_to_shards.get(stem_name, [])
        for sid in candidates:
            s = shard_by_id.get(sid)
            if s and "crystal_108d" in s.payload_ref:
                core_sids[stem_name] = sid
                break
    # Connect core files to all py files that reference them (via BUILD edges already found)
    # but also to all organism files in matching families
    for stem_name, core_sid in core_sids.items():
        if len(new_edge_set) >= MAX_NEW_EDGES:
            break
        # Find the family this core module serves
        core_s = shard_by_id.get(core_sid)
        if not core_s:
            continue
        family = core_s.family
        consumers = family_to_shards.get(family, [])
        for consumer_sid in consumers[:20]:  # cap per core file
            if consumer_sid != core_sid:
                _add_edge(core_sid, consumer_sid, "SEEDS", 0.8,
                          {"seed_type": "core_to_consumer", "core_module": stem_name})
                seed_count += 1

    # 5b. INDEX.md files → files they index (same directory)
    index_shards = [s for s in shards if s.payload_ref.lower().endswith("index.md")
                    or s.payload_ref.lower().endswith("readme.md")]
    for idx_s in index_shards:
        if len(new_edge_set) >= MAX_NEW_EDGES:
            break
        idx_dir = idx_s.payload_ref.rsplit("/", 1)[0] if "/" in idx_s.payload_ref else ""
        siblings = dir_to_shards.get(idx_dir, [])
        for sib_sid in siblings[:15]:
            if sib_sid != idx_s.shard_id:
                _add_edge(idx_s.shard_id, sib_sid, "SEEDS", 0.7,
                          {"seed_type": "index_to_indexed"})
                seed_count += 1

    # 5c. Manifest/config files → same-directory files
    manifest_shards = [s for s in shards
                       if any(k in s.payload_ref.lower() for k in ("manifest", "config", "setup", "package.json"))]
    for ms in manifest_shards:
        if len(new_edge_set) >= MAX_NEW_EDGES:
            break
        ms_dir = ms.payload_ref.rsplit("/", 1)[0] if "/" in ms.payload_ref else ""
        siblings = dir_to_shards.get(ms_dir, [])
        for sib_sid in siblings[:10]:
            if sib_sid != ms.shard_id:
                _add_edge(ms.shard_id, sib_sid, "SEEDS", 0.65,
                          {"seed_type": "manifest_to_module"})
                seed_count += 1
    print(f"    +{seed_count} seed SEEDS edges")

    # ── Phase 2 Summary ──────────────────────────────────────────────
    new_edge_count = len(edges) - old_edge_count
    new_edge_dist = {}
    for e in edges[old_edge_count:]:
        new_edge_dist[e.edge_type] = new_edge_dist.get(e.edge_type, 0) + 1
    print(f"\n  Phase 2 total: +{new_edge_count} new edges (cap={MAX_NEW_EDGES})")
    print(f"  Edge distribution BEFORE Phase 2: {old_edge_dist}")
    print(f"  Edge distribution FROM Phase 2:   {new_edge_dist}")
    final_dist = {}
    for e in edges:
        final_dist[e.edge_type] = final_dist.get(e.edge_type, 0) + 1
    print(f"  Edge distribution AFTER Phase 2:  {final_dist}")
    n = len(shards)
    max_edges = n * (n - 1) / 2
    density = len(edges) / max_edges * 100 if max_edges > 0 else 0
    print(f"  Graph density: {density:.4f}% ({len(edges)} edges / {max_edges:.0f} possible)")

    return edges

# ── Node Registry ───────────────────────────────────────────────────

def build_node_registry() -> list[dict]:
    """Build the node registry for all Athena nodes."""
    return [
        {
            "node_id": "athena-mcp-server",
            "role": "unified",
            "medium_class": "code",
            "lobe_affinity": None,
            "shard_families": ["all"],
            "mirrors": ["athena-square-earth", "athena-flower-fire", "athena-cloud-water", "athena-fractal-air"],
            "bridges": [
                {"type": "git_to_mcp", "description": "Git state exposed via 68 MCP tools + 21 resources"},
                {"type": "element_to_unified", "description": "4 element servers mirror unified tool subsets"},
            ],
            "cert_capabilities": ["STRUCTURAL", "CONSERVATION"],
            "read_surfaces": ["mcp_tool", "mcp_resource", "file_read", "git_log"],
            "write_surfaces": ["file_write", "git_commit"],
            "sync_sources": ["https://github.com/demeet2k/athena-mcp-server"],
            "github_repo": "https://github.com/demeet2k/athena-mcp-server",
            "tool_count": 71,
            "resource_count": 23,
        },
        {
            "node_id": "athena-square-earth",
            "role": "lobe",
            "medium_class": "code",
            "lobe_affinity": "S",
            "shard_families": ["shells", "dimensions", "address", "conservation", "hologram", "inverse_crystal", "angel"],
            "mirrors": ["athena-mcp-server"],
            "bridges": [{"type": "lobe_to_unified", "description": "Mirrors unified server's structure/address tools"}],
            "cert_capabilities": ["STRUCTURAL"],
            "read_surfaces": ["mcp_tool", "mcp_resource"],
            "write_surfaces": [],
            "sync_sources": ["https://github.com/demeet2k/athena-square-earth"],
            "github_repo": "https://github.com/demeet2k/athena-square-earth",
            "tool_count": 17,
            "resource_count": 1,
        },
        {
            "node_id": "athena-flower-fire",
            "role": "lobe",
            "medium_class": "code",
            "lobe_affinity": "F",
            "shard_families": ["metro", "clock", "moves", "transport", "z_points", "inverse_crystal"],
            "mirrors": ["athena-mcp-server"],
            "bridges": [{"type": "lobe_to_unified", "description": "Mirrors unified server's dynamics/corridor tools"}],
            "cert_capabilities": [],
            "read_surfaces": ["mcp_tool", "mcp_resource"],
            "write_surfaces": [],
            "sync_sources": ["https://github.com/demeet2k/athena-flower-fire"],
            "github_repo": "https://github.com/demeet2k/athena-flower-fire",
            "tool_count": 15,
            "resource_count": 1,
        },
        {
            "node_id": "athena-cloud-water",
            "role": "lobe",
            "medium_class": "code",
            "lobe_affinity": "C",
            "shard_families": ["conservation", "hologram", "angel", "brain"],
            "mirrors": ["athena-mcp-server"],
            "bridges": [{"type": "lobe_to_unified", "description": "Mirrors unified server's observation tools"}],
            "cert_capabilities": ["CONSERVATION"],
            "read_surfaces": ["mcp_tool", "mcp_resource"],
            "write_surfaces": [],
            "sync_sources": ["https://github.com/demeet2k/athena-cloud-water"],
            "github_repo": "https://github.com/demeet2k/athena-cloud-water",
            "tool_count": 16,
            "resource_count": 1,
        },
        {
            "node_id": "athena-fractal-air",
            "role": "lobe",
            "medium_class": "code",
            "lobe_affinity": "R",
            "shard_families": ["stages", "angel", "mobius", "inverse_crystal", "hologram"],
            "mirrors": ["athena-mcp-server"],
            "bridges": [{"type": "lobe_to_unified", "description": "Mirrors unified server's compression/seed tools"}],
            "cert_capabilities": ["REPLAY"],
            "read_surfaces": ["mcp_tool", "mcp_resource"],
            "write_surfaces": [],
            "sync_sources": ["https://github.com/demeet2k/athena-fractal-air"],
            "github_repo": "https://github.com/demeet2k/athena-fractal-air",
            "tool_count": 16,
            "resource_count": 1,
        },
        {
            "node_id": "google-docs",
            "role": "docs",
            "medium_class": "google_doc",
            "lobe_affinity": None,
            "shard_families": ["core", "crystal", "emergence", "skills", "brain_stem"],
            "mirrors": ["athena-mcp-server"],
            "bridges": [{"type": "docs_to_github", "description": "Google Docs sections mirror nervous system files"}],
            "cert_capabilities": [],
            "read_surfaces": ["google_drive_api"],
            "write_surfaces": ["google_drive_api"],
            "sync_sources": [
                "https://docs.google.com/document/d/1OUjhabDK08QvamAa0USQmTeEDNAwN3b853OVmvMUdaE",
                "https://docs.google.com/document/d/1bzcO7PKGlMUc2A35VYo5msN7hGYZzGA4KRQaFaRfbvQ",
                "https://docs.google.com/document/d/1LJEMi-OmqSfSqJTc585nxlf5zGF0rfyqbygNlYYB6J4",
            ],
            "github_repo": None,
            "tool_count": 0,
            "resource_count": 0,
        },
        {
            "node_id": "athena-guild-hall",
            "role": "guild-hall",
            "medium_class": "code",
            "lobe_affinity": None,
            "shard_families": ["manuscript", "quest", "synthesis", "proof", "replication", "guild_hall"],
            "mirrors": ["athena-mcp-server", "google-docs"],
            "bridges": [
                {"type": "guild_to_mcp", "description": "Guild Hall boards exposed via 4 MCP tools + 2 resources"},
                {"type": "guild_to_framework", "description": "Python framework implements 21-chapter x 256-gate computational model"},
                {"type": "guild_to_docs", "description": "Guild Hall synthesis mirrors Google Docs organism state"},
            ],
            "cert_capabilities": ["STRUCTURAL", "CONSERVATION", "REPLAY", "PROMOTION"],
            "read_surfaces": ["mcp_tool", "mcp_resource", "file_read", "cli"],
            "write_surfaces": ["file_write", "git_commit"],
            "sync_sources": [],
            "github_repo": None,
            "tool_count": 4,
            "resource_count": 2,
        },
        {
            "node_id": "manuscript-being",
            "role": "main-brain",
            "medium_class": "code",
            "lobe_affinity": None,
            "shard_families": ["manuscript", "quest", "synthesis", "proof", "replication",
                               "guild_hall", "crystal", "metro", "swarm", "truth"],
            "mirrors": ["athena-mcp-server", "athena-guild-hall", "google-docs"],
            "bridges": [
                {"type": "main_brain_to_mcp", "description": "MCP tools expose manuscript-being computation to all agents"},
                {"type": "main_brain_to_guild_hall", "description": "Guild Hall is the social coordination surface"},
                {"type": "main_brain_to_docs", "description": "Google Docs = slow-form, manuscript-being = executable form"},
            ],
            "cert_capabilities": ["STRUCTURAL", "CONSERVATION", "REPLAY", "PROMOTION", "REPLICATION", "TRUTH_CORRIDOR"],
            "read_surfaces": ["mcp_tool", "mcp_resource", "file_read", "cli", "python_import"],
            "write_surfaces": ["file_write", "git_commit", "python_exec"],
            "sync_sources": ["https://github.com/demeet2k/manuscript-being"],
            "github_repo": "https://github.com/demeet2k/manuscript-being",
            "tool_count": 0,
            "resource_count": 0,
        },
    ]

# ── Main ────────────────────────────────────────────────────────────

def main():
    print("Scanning MCP/data/*.json ...")
    json_shards = scan_json_data()
    print(f"  {len(json_shards)} JSON data shards")

    print("Scanning MCP/crystal_108d/*.py ...")
    code_shards = scan_crystal_modules()
    print(f"  {len(code_shards)} code module shards")

    print("Scanning MCP/element_servers/*.py ...")
    element_shards = scan_element_servers()
    print(f"  {len(element_shards)} element server shards")

    main_shard = scan_main_server()
    print("  1 main server shard")

    print("Scanning Guild Hall ...")
    guild_shards = scan_guild_hall()
    print(f"  {len(guild_shards)} guild hall shards")

    print("Scanning manuscript-being Python framework ...")
    ms_shards = scan_manuscript_being()
    print(f"  {len(ms_shards)} manuscript-being shards")

    print("Scanning FULL ORGANISM (every directory) ...")
    organism_shards = scan_full_organism()
    print(f"  {len(organism_shards)} organism shards")

    print("Creating chapter/appendix shards ...")
    chapter_appendix_shards = _create_chapter_appendix_shards()
    print(f"  {len(chapter_appendix_shards)} chapter/appendix shards")

    print("Creating Google Doc shards ...")
    gdoc_shards = _create_google_doc_shards()
    print(f"  {len(gdoc_shards)} Google Doc shards")

    print("Creating Guild Hall indexed shards ...")
    guild_hall_indexed_shards = _create_guild_hall_shards()
    print(f"  {len(guild_hall_indexed_shards)} guild hall indexed shards")

    all_shards = (json_shards + code_shards + element_shards + [main_shard]
                  + guild_shards + ms_shards + organism_shards
                  + chapter_appendix_shards + gdoc_shards + guild_hall_indexed_shards)
    print(f"\nTotal shards: {len(all_shards)}")

    print("Building edges ...")
    edges = build_edges(all_shards)
    print(f"  {len(edges)} edges")

    mirrors = [e for e in edges if e.edge_type == "MIRROR"]
    print(f"  {len(mirrors)} mirror edges")

    print("Building node registry ...")
    nodes = build_node_registry()
    print(f"  {len(nodes)} nodes")

    # Compute stats
    families = sorted(set(s.family for s in all_shards))
    mediums = sorted(set(s.medium for s in all_shards))
    edge_dist = {}
    for e in edges:
        edge_dist[e.edge_type] = edge_dist.get(e.edge_type, 0) + 1
    family_sizes = {}
    for s in all_shards:
        family_sizes[s.family] = family_sizes.get(s.family, 0) + 1

    # Compute metro line stats
    metro_stats = {}
    for s in all_shards:
        for route in (s.route_refs or []):
            if route in METRO_LINES:
                metro_stats[route] = metro_stats.get(route, 0) + 1

    # Compute lens distribution
    lens_dist = {}
    for s in all_shards:
        lens_dist[s.lens or "balanced"] = lens_dist.get(s.lens or "balanced", 0) + 1

    # Compute HPRO-level distributions from tags
    hpro_level_dist = {}
    hpro_element_dist = {}
    hpro_phase_dist = {}
    for s in all_shards:
        for tag in (s.tags or []):
            if tag.startswith("hpro_L"):
                hpro_level_dist[tag] = hpro_level_dist.get(tag, 0) + 1
            elif tag.startswith("hpro_Fire") or tag.startswith("hpro_Air") or tag.startswith("hpro_Water") or tag.startswith("hpro_Earth"):
                hpro_element_dist[tag] = hpro_element_dist.get(tag, 0) + 1
            elif tag.startswith("hpro_Cardinal") or tag.startswith("hpro_Fixed") or tag.startswith("hpro_Mutable"):
                hpro_phase_dist[tag] = hpro_phase_dist.get(tag, 0) + 1

    # Emit mycelium_graph.json
    graph = {
        "meta": {
            "title": "Athena Mycelium Graph",
            "description": "Universal shard/edge/node graph manifest for the ENTIRE Athena distributed superbrain organism",
            "generated_at": NOW,
            "generator": "generate_graph.py v4 — full organism + HPRO + chapters/appendices + gdocs + guild hall + metro weight hierarchy",
            "shard_count": len(all_shards),
            "edge_count": len(edges),
            "mirror_count": len(mirrors),
            "node_count": len(nodes),
            "families": families,
            "mediums": mediums,
        },
        "metro_lines": METRO_LINES,
        "sfcr_directory_map": {k: {"primary": v[0], "secondary": v[1], "metro": v[2], "family": v[3]}
                               for k, v in ORGANISM_DIR_MAP.items()},
        "shards": [to_dict(s) for s in all_shards],
        "edges": [to_dict(e) for e in edges],
        "mirrors": [to_dict(e) for e in mirrors],
        "nodes": nodes,
        "graph_stats": {
            "edge_type_distribution": edge_dist,
            "family_sizes": family_sizes,
            "medium_distribution": {m: sum(1 for s in all_shards if s.medium == m) for m in mediums},
            "metro_line_distribution": metro_stats,
            "sfcr_lens_distribution": lens_dist,
            "hpro_hologram_level_distribution": hpro_level_dist,
            "hpro_element_distribution": hpro_element_dist,
            "hpro_phase_distribution": hpro_phase_dist,
        },
    }

    out_graph = DATA_DIR / "mycelium_graph.json"
    out_graph.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out_graph}")

    # Emit node_registry.json
    registry = {
        "meta": {
            "title": "Athena Node Registry",
            "description": "All nodes in the distributed Athena superbrain",
            "generated_at": NOW,
            "total_nodes": len(nodes),
        },
        "nodes": nodes,
    }

    out_nodes = DATA_DIR / "node_registry.json"
    out_nodes.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_nodes}")

    print(f"\nDone. {len(all_shards)} shards, {len(edges)} edges, {len(nodes)} nodes.")

if __name__ == "__main__":
    main()
