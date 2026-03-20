# CRYSTAL: Xi108:W1:A7:S17 | face=S | node=588 | depth=2 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W1:A7:S16→Xi108:W1:A7:S18→Xi108:W2:A7:S17→Xi108:W1:A6:S17→Xi108:W1:A8:S17

"""
Crystal coordinate assignment engine for the Athena mycelium graph.

Maps every shard in mycelium_graph.json to a CrystalCoordinate inside
the Sigma_60 x 4 x 3 = 720 station system.

Coordinate schema:
    shell(1-36), wreath(1-3), archetype(1-12), face(S/F/C/R),
    node_id(1-666), depth(0-3), phase(Fixed/Cardinal/Mutable),
    metro_stops(list)
"""

import dataclasses
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from ._cache import JsonCache, DATA_DIR
from .constants import (
    ARCHETYPE_NAMES,
    TOTAL_SHELLS,
    TOTAL_NODES,
    TOTAL_WREATHS,
    SUPERPHASE_NAMES,
)

# ---------------------------------------------------------------------------
# Lazy caches
# ---------------------------------------------------------------------------

_graph = JsonCache("mycelium_graph.json")
_shells_reg = JsonCache("shell_registry.json")
_coord_cache: dict | None = None          # populated on first assign_all call

# ---------------------------------------------------------------------------
# CrystalCoordinate dataclass
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True, slots=True)
class CrystalCoordinate:
    """Immutable crystal address for one mycelium shard."""

    shell: int          # 1-36
    wreath: int         # 1-3  (1=Sulfur, 2=Mercury, 3=Salt)
    archetype: int      # 1-12
    face: str           # S / F / C / R
    node_id: int        # 1-666
    depth: int          # 0-3  (0=deepest/seed, 3=surface)
    phase: str          # Fixed / Cardinal / Mutable
    metro_stops: tuple  # metro line codes (frozen for hashability)

    def to_dict(self) -> dict:
        return {
            "shell": self.shell,
            "wreath": self.wreath,
            "archetype": self.archetype,
            "face": self.face,
            "node_id": self.node_id,
            "depth": self.depth,
            "phase": self.phase,
            "metro_stops": list(self.metro_stops),
        }

    def address(self) -> str:
        """Xi108 canonical address string."""
        sp = ("Su", "Me", "Sa")[self.wreath - 1]
        return (
            f"Xi108:W{self.wreath}:A{self.archetype}:S{self.shell}"
            f":u{self.node_id}:{sp}:{self.face}:d{self.depth}"
        )

# ---------------------------------------------------------------------------
# Deterministic hash helper
# ---------------------------------------------------------------------------

def _stable_hash(s: str) -> int:
    """Return a deterministic positive integer from a string."""
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)

# ---------------------------------------------------------------------------
# Shell assignment (1-36)  based on family / directory depth
# ---------------------------------------------------------------------------

# Family keywords mapped to shell bands.  Each band spans 6 shells.
_SHELL_BAND_FAMILIES: dict[int, tuple[str, ...]] = {
    # Band 0 → shells 1-6: deep core framework
    0: (
        "crystal", "conservation", "shells", "kernel", "inverse_crystal",
        "inverse-crystal-complete-v1", "address", "z_points", "seed",
    ),
    # Band 1 → shells 7-12: nervous system, chapters, appendices
    1: (
        "nervous", "nervous_overview", "hologram", "hologram-reading-v1",
        "hologram-rosetta-v1", "dimensions", "stages", "angel",
        "angel-object-v1", "live_lock", "clock", "moves", "transport",
    ),
    # Band 2 → shells 13-18: corpus capsules, synthesis, overlays
    2: (
        "synthesis", "overlays", "organs", "mobius", "mobius-lenses-v1",
        "metro", "lens", "dls_lenses", "dls-6x6-lenses", "live_cell",
        "emergence", "cycle", "math", "math_final", "proof", "truth",
    ),
    # Band 3 → shells 19-24: projects, neural, swarm, E8
    3: (
        "qshrink_control", "neural_core", "e8_lattice", "e8-lattice",
        "meta_observer", "meta-observer-swarm", "swarm", "brain",
        "mycelium_brain", "evolution", "evolution-compiler",
        "calculus_4d", "calculus-4d", "crown_12d", "crown-12d",
        "athenachka", "athenachka-720", "program_rosetta", "program-rosetta",
        "tensor", "voynich_eva",
    ),
    # Band 4 → shells 25-30: active/accepted content, frontiers
    4: (
        "accepted", "actualize", "quest", "agency", "agency-gateway",
        "guild_hall", "hpro", "replication", "ecosystem",
        "crypto", "runtime",
    ),
    # Band 5 → shells 31-36: infrastructure, misc, archive
    5: (
        "infra", "misc", "server", "agent", "athena", "memory",
        "config", "mycelium", "mycelium-graph", "node-registry",
    ),
}

# Pre-compute reverse lookup: family_keyword → band index
_FAMILY_TO_BAND: dict[str, int] = {}
for _band, _families in _SHELL_BAND_FAMILIES.items():
    for _fam in _families:
        _FAMILY_TO_BAND[_fam] = _band

def _assign_shell(shard: dict) -> int:
    """Determine shell 1-36 from shard family and payload path."""
    family = shard.get("family", "misc")
    band = _FAMILY_TO_BAND.get(family, 5)  # default to infra band

    # Distribute within band (6 shells per band) using stable hash
    band_start = band * 6 + 1                    # 1, 7, 13, 19, 25, 31
    offset = _stable_hash(shard["shard_id"]) % 6
    return band_start + offset

# ---------------------------------------------------------------------------
# Wreath assignment (1-3)  based on content modality
# ---------------------------------------------------------------------------

# Medium → wreath mapping
_MEDIUM_WREATH: dict[str, int] = {
    "json": 1,    # Sulfur: structural / definitional
    "config": 1,
    "code": 2,    # Mercury: dynamic / procedural
    "web": 2,
    "doc": 3,     # Salt: narrative / descriptive
}

# Family keywords that override the medium-based wreath
_SULFUR_FAMILIES = frozenset({
    "conservation", "shells", "z_points", "live_lock", "overlays",
    "stages", "transport", "kernel", "crystal", "address",
    "node-registry", "inverse_crystal", "inverse-crystal-complete-v1",
})
_MERCURY_FAMILIES = frozenset({
    "brain", "neural_core", "qshrink_control", "runtime", "server",
    "agent", "evolution", "evolution-compiler", "calculus_4d", "calculus-4d",
    "moves", "metro", "clock", "live_cell", "emergence",
})
_SALT_FAMILIES = frozenset({
    "hologram", "hologram-reading-v1", "hologram-rosetta-v1",
    "angel", "angel-object-v1", "synthesis", "quest",
    "accepted", "ecosystem", "voynich_eva", "memory",
})

def _assign_wreath(shard: dict) -> int:
    """Determine wreath 1-3 (Sulfur/Mercury/Salt)."""
    family = shard.get("family", "")
    if family in _SULFUR_FAMILIES:
        return 1
    if family in _MERCURY_FAMILIES:
        return 2
    if family in _SALT_FAMILIES:
        return 3
    # Fall back to medium
    medium = shard.get("medium", "doc")
    return _MEDIUM_WREATH.get(medium, 3)

# ---------------------------------------------------------------------------
# Archetype assignment (1-12)  keyword match against family/summary
# ---------------------------------------------------------------------------

# Enriched archetype keywords from ATHENA B lattice registry + Google Docs spec.
# Each archetype has element (Fire/Earth/Air/Water) and modality (Cardinal/Fixed/Mutable).
_ARCHETYPE_KEYWORDS: dict[int, tuple[str, ...]] = {
    1:  ("seed", "kernel", "core", "apex", "origin", "ignition", "spark", "boot", "start", "init"),
    2:  ("mobius", "twist", "parity", "inversion", "mirror", "accumulate", "store", "root", "memory", "preserve"),
    3:  ("modal", "trefoil", "mode", "triad", "bifurcation", "branch", "fork", "split", "route", "decide"),
    4:  ("enclosure", "vessel", "boundary", "contain", "seal", "shield", "chamber", "protect", "sanctuary"),
    5:  ("amplify", "observer", "meta", "swarm", "watch", "pentad", "intensify", "scale", "force", "power"),
    6:  ("hinge", "bridge", "dyad", "pair", "discriminat", "filter", "refine", "sort", "discern", "separate"),
    7:  ("calibrat", "arc", "evolution", "path", "transform", "tune", "align", "witness", "measure", "correct"),
    8:  ("dissolv", "octad", "reverse", "counter", "inverse", "release", "melt", "surrender", "soften", "unlayer"),
    9:  ("expand", "emergent", "ennead", "emergence", "grow", "bloom", "radiate", "unfold", "outreach", "extend"),
    10: ("crown", "cascade", "crystalliz", "govern", "command", "commit", "seal", "optimiz", "allocat", "durable"),
    11: ("disrupt", "orbit", "rupture", "helm", "wheel", "break", "migrat", "dislodge", "threshold", "liberat"),
    12: ("complet", "dodecad", "total", "full", "closure", "publish", "handoff", "return", "re-entry", "finish"),
}
# Element affinity per archetype (from ATHENA B: Fire/Earth/Air/Water cycles)
_ARCHETYPE_ELEMENT: dict[int, str] = {
    1: "R", 2: "S", 3: "C", 4: "F",   # Fire, Earth, Air, Water
    5: "R", 6: "S", 7: "C", 8: "F",
    9: "R", 10: "S", 11: "C", 12: "F",
}

def _assign_archetype(shard: dict) -> int:
    """Determine archetype 1-12 from family + summary keywords."""
    text = (shard.get("family", "") + " " + shard.get("summary", "")).lower()
    best_arch = 1
    best_score = 0
    for arch, keywords in _ARCHETYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_arch = arch
    if best_score == 0:
        # No keyword hit — distribute by hash
        best_arch = (_stable_hash(shard["shard_id"]) % 12) + 1
    return best_arch

# ---------------------------------------------------------------------------
# Face assignment (S/F/C/R)
# ---------------------------------------------------------------------------

_FACE_INDEX = ("S", "F", "C", "R")

# Family-to-face affinity from the SFCR directory map + Google Docs spec.
# Gold/Square=structure, Scarlet/Flower=narrative, Flame/Cloud=exploration, Violet/Fractal=recursion.
_FAMILY_FACE: dict[str, str] = {
    # S (Square/Earth) — structural, definitional, data
    "crystal": "S", "conservation": "S", "shells": "S", "address": "S",
    "z_points": "S", "kernel": "S", "stages": "S", "overlays": "S",
    "live_lock": "S", "transport": "S", "config": "S", "infra": "S",
    "node-registry": "S",
    # F (Flower/Water) — narrative, holographic, living, synthesis
    "hologram": "F", "angel": "F", "synthesis": "F", "quest": "F",
    "hologram-reading-v1": "F", "hologram-rosetta-v1": "F",
    "angel-object-v1": "F", "accepted": "F", "ecosystem": "F",
    "voynich_eva": "F", "memory": "F", "live_cell": "F",
    "actualize": "F",
    # C (Cloud/Air) — observational, liminal, meta, bridge
    "meta_observer": "C", "meta-observer-swarm": "C", "swarm": "C",
    "mobius": "C", "mobius-lenses-v1": "C", "lens": "C",
    "dls_lenses": "C", "dls-6x6-lenses": "C", "emergence": "C",
    "brain": "C", "mycelium_brain": "C", "metro": "C", "clock": "C",
    # R (Fractal/Fire) — recursive, neural, evolutionary, compression
    "neural_core": "R", "qshrink_control": "R", "e8_lattice": "R",
    "e8-lattice": "R", "evolution": "R", "evolution-compiler": "R",
    "calculus_4d": "R", "calculus-4d": "R", "crown_12d": "R",
    "crown-12d": "R", "athenachka": "R", "athenachka-720": "R",
    "program_rosetta": "R", "program-rosetta": "R", "tensor": "R",
    "inverse_crystal": "R", "inverse-crystal-complete-v1": "R",
    "runtime": "R", "server": "R", "agent": "R",
}

# Medium-to-face fallback (when no family match)
_MEDIUM_FACE: dict[str, str] = {
    "json": "S",    # data = structure
    "config": "S",
    "code": "R",    # code = recursive/procedural
    "web": "C",     # web = exploratory
    "doc": "F",     # documents = narrative
}

def _assign_face(shard: dict) -> str:
    """Assign SFCR face using multi-level fallback for balanced distribution.

    Priority: explicit lens > family affinity > archetype element > medium > hash.
    This replaces the old flat-hash fallback that produced S=64%, C=0.7%.
    """
    # 1. Explicit lens — ONLY trust non-S (S is 64% biased from historical embedder)
    lens = shard.get("lens")
    if lens in ("F", "C", "R"):
        return lens

    # 3. Family-to-face affinity table
    family = shard.get("family", "")
    if family in _FAMILY_FACE:
        return _FAMILY_FACE[family]

    # 4. Archetype element affinity (from ATHENA B element cycle)
    # Use the archetype we'd assign to derive face
    text = (family + " " + shard.get("summary", "")).lower()
    for arch, keywords in _ARCHETYPE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return _ARCHETYPE_ELEMENT.get(arch, "S")

    # 5. Medium-based fallback (balanced: doc splits between F and C)
    medium = shard.get("medium", "doc")
    if medium == "doc":
        # Split doc shards: use hash to distribute between F (60%) and C (40%)
        # This addresses the C under-representation (was 0.7%, target ~25%)
        h = _stable_hash(shard["shard_id"]) % 10
        if h < 4:
            return "C"  # 40% of docs → Cloud (observation, exploration)
        return "F"       # 60% of docs → Flower (narrative, living)
    if medium in _MEDIUM_FACE:
        return _MEDIUM_FACE[medium]

    # 6. Final: balanced hash (mod 4, not biased toward S)
    return _FACE_INDEX[_stable_hash(shard["shard_id"]) % 4]

# ---------------------------------------------------------------------------
# Depth, phase, metro stops
# ---------------------------------------------------------------------------

_PHASE_CYCLE = ("Fixed", "Cardinal", "Mutable")

def _assign_depth(shard: dict) -> int:
    """Depth 0-3.  Deeper = more core/structural."""
    family = shard.get("family", "")
    if family in _SULFUR_FAMILIES or family in _SHELL_BAND_FAMILIES.get(0, ()):
        return 0
    medium = shard.get("medium", "")
    if medium == "json":
        return 1
    if medium == "code":
        return 2
    return 3

def _assign_phase(shell: int) -> str:
    """Phase follows the 3-wreath cycle: shells 1-12 Fixed, 13-24 Cardinal, 25-36 Mutable."""
    return _PHASE_CYCLE[(shell - 1) // 12]

def _assign_metro_stops(shard: dict) -> tuple:
    """Derive metro-line memberships from shard tags and family."""
    stops: list[str] = []
    tags_str = " ".join(shard.get("tags", []))
    family = shard.get("family", "")
    summary = (shard.get("summary", "") + " " + family + " " + tags_str).lower()

    # Heuristic metro membership
    if any(kw in summary for kw in ("shell", "dimension", "layer")):
        stops.append("Sa")   # Shell Ascent
    if any(kw in summary for kw in ("wreath", "chapter", "cycle")):
        stops.append("Wr")   # Wreath Ring
    if any(kw in summary for kw in ("archetype", "column")):
        stops.append("Ac")   # Archetype Column
    if any(kw in summary for kw in ("metro", "route", "express")):
        stops.append("Me")   # Metro Express
    if any(kw in summary for kw in ("mobius", "twist", "parity", "compress")):
        stops.append("Mt")   # Mobius Twist
    if any(kw in summary for kw in ("bridge", "cross", "connect")):
        stops.append("Bw")   # Bridge Walk
    if any(kw in summary for kw in ("crown", "govern", "command")):
        stops.append("Cc")   # Crown Circuit
    if any(kw in summary for kw in ("emergence", "lift", "higher")):
        stops.append("Dl")   # Dimensional Lift
    if any(kw in summary for kw in ("omega", "zero", "spine")):
        stops.append("\u03a9")  # Zero-Point Spine
    if any(kw in summary for kw in ("seed", "generator", "propagat")):
        stops.append("w")    # Generator Line
    if any(kw in summary for kw in ("address", "grammar", "code_key")):
        stops.append("\u25a1")  # Square Address
    if any(kw in summary for kw in ("converge", "threshold")):
        stops.append("\u25cb")  # Convergence Circle
    if any(kw in summary for kw in ("recursion", "triangle", "cadence")):
        stops.append("\u25b3")  # Triangle Control
    if any(kw in summary for kw in ("fractal", "holographic", "hologram")):
        stops.append("\u2736")  # Fractal Holographic
    if any(kw in summary for kw in ("truth", "ok", "fail", "lattice")):
        stops.append("T")    # Truth Lattice

    return tuple(stops) if stops else ("Sa",)

# ---------------------------------------------------------------------------
# Node ID assignment (1-666, deterministic)
# ---------------------------------------------------------------------------

def _assign_node_id(shard_id: str, shell: int) -> int:
    """Assign a node_id within 1-666 based on shell capacity.

    Each shell s contains s triangular nodes (T_s - T_{s-1}).
    We hash into the shell's local capacity then offset by cumulative.
    """
    # shell s has exactly s nodes; cumulative up to s-1 = s*(s-1)/2
    local_capacity = shell
    cumulative_before = shell * (shell - 1) // 2
    local_offset = _stable_hash(shard_id) % local_capacity
    return cumulative_before + local_offset + 1   # 1-indexed

# ---------------------------------------------------------------------------
# Master assignment function
# ---------------------------------------------------------------------------

def assign_coordinate(shard: dict) -> CrystalCoordinate:
    """Compute the crystal coordinate for a single shard."""
    shell = _assign_shell(shard)
    wreath = _assign_wreath(shard)
    archetype = _assign_archetype(shard)
    face = _assign_face(shard)
    node_id = _assign_node_id(shard["shard_id"], shell)
    depth = _assign_depth(shard)
    phase = _assign_phase(shell)
    metro_stops = _assign_metro_stops(shard)
    return CrystalCoordinate(
        shell=shell,
        wreath=wreath,
        archetype=archetype,
        face=face,
        node_id=node_id,
        depth=depth,
        phase=phase,
        metro_stops=metro_stops,
    )

def assign_all_coordinates(
    graph_path: str | Path | None = None,
) -> dict[str, dict]:
    """Assign a CrystalCoordinate to every shard in the mycelium graph.

    Parameters
    ----------
    graph_path : str or Path, optional
        Override for mycelium_graph.json location.
        Defaults to DATA_DIR / "mycelium_graph.json".

    Returns
    -------
    dict mapping shard payload_ref → coordinate dict
    """
    global _coord_cache
    if _coord_cache is not None:
        return _coord_cache

    if graph_path is not None:
        with open(graph_path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = _graph.load()

    shards = data.get("shards", [])
    result: dict[str, dict] = {}
    for shard in shards:
        coord = assign_coordinate(shard)
        key = shard.get("payload_ref", shard["shard_id"])
        result[key] = coord.to_dict()

    _coord_cache = result
    return result

# ---------------------------------------------------------------------------
# File generation
# ---------------------------------------------------------------------------

def _build_shell_topology(coords: dict[str, dict]) -> list[dict]:
    """Per-shell summary with shard count and dominant face."""
    shells: dict[int, list[dict]] = defaultdict(list)
    for coord in coords.values():
        shells[coord["shell"]].append(coord)

    topo: list[dict] = []
    for s in range(1, TOTAL_SHELLS + 1):
        items = shells.get(s, [])
        face_counts: dict[str, int] = defaultdict(int)
        for c in items:
            face_counts[c["face"]] += 1
        dominant = max(face_counts, key=face_counts.get) if face_counts else "S"
        topo.append({
            "shell": s,
            "shard_count": len(items),
            "dominant_face": dominant,
            "face_distribution": dict(face_counts),
        })
    return topo

def _build_wreath_bodies(coords: dict[str, dict]) -> list[dict]:
    """Per-wreath summary."""
    wreaths: dict[int, list[dict]] = defaultdict(list)
    for coord in coords.values():
        wreaths[coord["wreath"]].append(coord)

    names = {1: "Sulfur", 2: "Mercury", 3: "Salt"}
    bodies: list[dict] = []
    for w in range(1, TOTAL_WREATHS + 1):
        items = wreaths.get(w, [])
        bodies.append({
            "wreath": w,
            "name": names[w],
            "shard_count": len(items),
            "shells_used": sorted({c["shell"] for c in items}),
        })
    return bodies

def _build_metro_intersections(coords: dict[str, dict]) -> dict[str, int]:
    """Count shards per metro line."""
    counts: dict[str, int] = defaultdict(int)
    for coord in coords.values():
        for stop in coord["metro_stops"]:
            counts[stop] += 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))

def generate_coordinate_file(
    graph_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """Generate crystal_coordinates.json with full mappings + metadata.

    Parameters
    ----------
    graph_path : path, optional
        Override input graph location.
    output_path : path, optional
        Override output file location.
        Defaults to DATA_DIR / "crystal_coordinates.json".

    Returns
    -------
    Path to the written file.
    """
    coords = assign_all_coordinates(graph_path)
    out = Path(output_path) if output_path else DATA_DIR / "crystal_coordinates.json"

    payload = {
        "meta": {
            "title": "Crystal Coordinate Assignments",
            "description": "Every mycelium shard mapped to a 108D crystal coordinate",
            "coordinate_schema": (
                "shell(1-36), wreath(1-3), archetype(1-12), face(S/F/C/R), "
                "node_id(1-666), depth(0-3), phase(Fixed/Cardinal/Mutable), "
                "metro_stops(list)"
            ),
            "station_system": "Sigma_60 x 4 x 3 = 720",
            "total_shards": len(coords),
            "total_shells": TOTAL_SHELLS,
            "total_nodes": TOTAL_NODES,
            "total_wreaths": TOTAL_WREATHS,
        },
        "shell_topology": _build_shell_topology(coords),
        "wreath_bodies": _build_wreath_bodies(coords),
        "metro_intersections": _build_metro_intersections(coords),
        "coordinates": coords,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out

# ---------------------------------------------------------------------------
# MCP tool function
# ---------------------------------------------------------------------------

def query_coordinates(component: str = "all") -> str:
    """
    Query crystal coordinate assignments for mycelium shards.

    Modes:
    - "all"             overview stats (shards per shell, per wreath, etc.)
    - "shard:path"      coordinate of a specific shard (by payload_ref)
    - "shell:N"         all shards in shell N  (1-36)
    - "wreath:N"        all shards in wreath N (1-3)
    - "archetype:N"     all shards with archetype N (1-12)
    - "neighbors:NID"   adjacent nodes (same shell +/-1, same wreath, same archetype)
    - "route:A->B"      shortest path between two node IDs
    - "stats"           distribution statistics
    """
    coords = assign_all_coordinates()

    # ---- "all" / overview ----
    if component == "all":
        return _overview(coords)

    # ---- "stats" ----
    if component == "stats":
        return _stats(coords)

    # ---- "shard:path" ----
    if component.startswith("shard:"):
        path = component[6:]
        return _query_shard_coord(coords, path)

    # ---- "shell:N" ----
    if component.startswith("shell:"):
        try:
            n = int(component[6:])
        except ValueError:
            return f"Invalid shell number: {component[6:]}"
        return _query_shell(coords, n)

    # ---- "wreath:N" ----
    if component.startswith("wreath:"):
        try:
            n = int(component[7:])
        except ValueError:
            return f"Invalid wreath number: {component[7:]}"
        return _query_wreath(coords, n)

    # ---- "archetype:N" ----
    if component.startswith("archetype:"):
        try:
            n = int(component[10:])
        except ValueError:
            return f"Invalid archetype number: {component[10:]}"
        return _query_archetype(coords, n)

    # ---- "neighbors:NID" ----
    if component.startswith("neighbors:"):
        try:
            nid = int(component[10:])
        except ValueError:
            return f"Invalid node_id: {component[10:]}"
        return _query_neighbors(coords, nid)

    # ---- "route:A->B" ----
    if component.startswith("route:"):
        route_spec = component[6:]
        sep = "\u2192" if "\u2192" in route_spec else "->"
        parts = route_spec.split(sep)
        if len(parts) != 2:
            return "Route format: route:A->B  (two node IDs separated by -> or \u2192)"
        try:
            a, b = int(parts[0].strip()), int(parts[1].strip())
        except ValueError:
            return "Route endpoints must be integer node IDs."
        return _route(coords, a, b)

    return (
        f"Unknown component '{component}'.\n"
        "Use: all | stats | shard:<path> | shell:<N> | wreath:<N> | "
        "archetype:<N> | neighbors:<node_id> | route:A->B"
    )

# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def _overview(coords: dict[str, dict]) -> str:
    shell_counts: dict[int, int] = defaultdict(int)
    wreath_counts: dict[int, int] = defaultdict(int)
    face_counts: dict[str, int] = defaultdict(int)
    phase_counts: dict[str, int] = defaultdict(int)

    for c in coords.values():
        shell_counts[c["shell"]] += 1
        wreath_counts[c["wreath"]] += 1
        face_counts[c["face"]] += 1
        phase_counts[c["phase"]] += 1

    wreath_names = {1: "Sulfur", 2: "Mercury", 3: "Salt"}
    lines = [
        "## Crystal Coordinate Overview\n",
        f"**Total shards assigned**: {len(coords)}",
        f"**Station system**: \u03a3\u2086\u2080 \u00d7 4 \u00d7 3 = 720\n",
        "### Shards per wreath",
    ]
    for w in sorted(wreath_counts):
        lines.append(f"- Wreath {w} ({wreath_names[w]}): {wreath_counts[w]}")

    lines.append("\n### Shards per face")
    for f in ("S", "F", "C", "R"):
        lines.append(f"- {f}: {face_counts.get(f, 0)}")

    lines.append("\n### Shards per phase")
    for p in ("Fixed", "Cardinal", "Mutable"):
        lines.append(f"- {p}: {phase_counts.get(p, 0)}")

    lines.append("\n### Shell distribution (top 10)")
    for s, cnt in sorted(shell_counts.items(), key=lambda kv: -kv[1])[:10]:
        lines.append(f"- Shell {s:>2}: {cnt}")

    return "\n".join(lines) + "\n"

def _stats(coords: dict[str, dict]) -> str:
    shell_counts: dict[int, int] = defaultdict(int)
    arch_counts: dict[int, int] = defaultdict(int)
    depth_counts: dict[int, int] = defaultdict(int)
    metro_counts: dict[str, int] = defaultdict(int)

    for c in coords.values():
        shell_counts[c["shell"]] += 1
        arch_counts[c["archetype"]] += 1
        depth_counts[c["depth"]] += 1
        for stop in c["metro_stops"]:
            metro_counts[stop] += 1

    lines = [
        "## Crystal Coordinate Statistics\n",
        f"**Total**: {len(coords)} shards\n",
        "### Archetype distribution",
    ]
    for a in range(1, 13):
        name = ARCHETYPE_NAMES[a - 1]
        lines.append(f"- {a:>2}. {name}: {arch_counts.get(a, 0)}")

    lines.append("\n### Depth distribution")
    for d in range(4):
        label = ("seed/core", "structural", "procedural", "surface")[d]
        lines.append(f"- Depth {d} ({label}): {depth_counts.get(d, 0)}")

    lines.append("\n### Metro line membership")
    for stop, cnt in sorted(metro_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"- {stop}: {cnt}")

    lines.append("\n### Shell utilisation")
    counts = [shell_counts.get(s, 0) for s in range(1, 37)]
    if counts:
        lines.append(f"- Min: {min(counts)}  Max: {max(counts)}  "
                      f"Mean: {sum(counts)/len(counts):.1f}")

    return "\n".join(lines) + "\n"

def _query_shard_coord(coords: dict[str, dict], path: str) -> str:
    # Try exact match first, then substring
    if path in coords:
        c = coords[path]
        return _format_coord(path, c)

    matches = [(k, v) for k, v in coords.items() if path in k]
    if not matches:
        return f"No shard found matching '{path}'."
    if len(matches) > 20:
        lines = [f"Found {len(matches)} matches for '{path}'. Showing first 20:\n"]
        matches = matches[:20]
    else:
        lines = [f"Found {len(matches)} match(es) for '{path}':\n"]
    for k, v in matches:
        lines.append(_format_coord(k, v))
    return "\n".join(lines)

def _format_coord(path: str, c: dict) -> str:
    sp = ("Sulfur", "Mercury", "Salt")[c["wreath"] - 1]
    arch_name = ARCHETYPE_NAMES[c["archetype"] - 1] if 1 <= c["archetype"] <= 12 else "?"
    return (
        f"**{path}**\n"
        f"  Shell {c['shell']} | Wreath {c['wreath']} ({sp}) | "
        f"Archetype {c['archetype']} ({arch_name})\n"
        f"  Face {c['face']} | Node {c['node_id']} | "
        f"Depth {c['depth']} | Phase {c['phase']}\n"
        f"  Metro: {', '.join(c['metro_stops']) if c['metro_stops'] else 'none'}\n"
    )

def _query_shell(coords: dict[str, dict], n: int) -> str:
    if n < 1 or n > TOTAL_SHELLS:
        return f"Shell must be 1-{TOTAL_SHELLS}. Got {n}."
    matches = [(k, v) for k, v in coords.items() if v["shell"] == n]
    lines = [f"## Shell {n} — {len(matches)} shards\n"]
    for k, v in matches[:50]:
        lines.append(f"- `{k}` (face={v['face']}, arch={v['archetype']}, "
                      f"node={v['node_id']}, depth={v['depth']})")
    if len(matches) > 50:
        lines.append(f"\n... and {len(matches) - 50} more.")
    return "\n".join(lines) + "\n"

def _query_wreath(coords: dict[str, dict], n: int) -> str:
    if n < 1 or n > TOTAL_WREATHS:
        return f"Wreath must be 1-{TOTAL_WREATHS}. Got {n}."
    names = {1: "Sulfur", 2: "Mercury", 3: "Salt"}
    matches = [(k, v) for k, v in coords.items() if v["wreath"] == n]
    lines = [f"## Wreath {n} ({names[n]}) — {len(matches)} shards\n"]
    # Group by shell
    by_shell: dict[int, int] = defaultdict(int)
    for _, v in matches:
        by_shell[v["shell"]] += 1
    for s in sorted(by_shell):
        lines.append(f"- Shell {s:>2}: {by_shell[s]} shards")
    return "\n".join(lines) + "\n"

def _query_archetype(coords: dict[str, dict], n: int) -> str:
    if n < 1 or n > 12:
        return f"Archetype must be 1-12. Got {n}."
    name = ARCHETYPE_NAMES[n - 1]
    matches = [(k, v) for k, v in coords.items() if v["archetype"] == n]
    lines = [f"## Archetype {n} — {name} — {len(matches)} shards\n"]
    for k, v in matches[:50]:
        lines.append(f"- `{k}` (shell={v['shell']}, face={v['face']}, "
                      f"wreath={v['wreath']}, depth={v['depth']})")
    if len(matches) > 50:
        lines.append(f"\n... and {len(matches) - 50} more.")
    return "\n".join(lines) + "\n"

def _query_neighbors(coords: dict[str, dict], nid: int) -> str:
    """Find shards adjacent to a node: same shell +/-1, same wreath, same archetype."""
    # Find the reference shard
    ref = None
    ref_key = None
    for k, v in coords.items():
        if v["node_id"] == nid:
            ref = v
            ref_key = k
            break
    if ref is None:
        return f"No shard with node_id={nid} found."

    neighbors: list[tuple[str, dict]] = []
    for k, v in coords.items():
        if k == ref_key:
            continue
        # Adjacent shell
        if abs(v["shell"] - ref["shell"]) <= 1 and v["wreath"] == ref["wreath"]:
            neighbors.append((k, v))
        # Same archetype, any shell
        elif v["archetype"] == ref["archetype"] and v["shell"] == ref["shell"]:
            neighbors.append((k, v))

    lines = [
        f"## Neighbors of node {nid} (shell={ref['shell']}, "
        f"wreath={ref['wreath']}, arch={ref['archetype']})\n",
        f"**Reference**: `{ref_key}`",
        f"**Neighbors found**: {len(neighbors)}\n",
    ]
    for k, v in neighbors[:30]:
        lines.append(f"- `{k}` (shell={v['shell']}, node={v['node_id']}, "
                      f"face={v['face']}, arch={v['archetype']})")
    if len(neighbors) > 30:
        lines.append(f"\n... and {len(neighbors) - 30} more.")
    return "\n".join(lines) + "\n"

def _route(coords: dict[str, dict], a: int, b: int) -> str:
    """Compute a shortest path between two node IDs via shell adjacency.

    Uses BFS over the implicit shell graph where nodes in shell s connect
    to nodes in shell s-1 and s+1 sharing the same wreath or archetype.
    """
    # Build node_id → (shell, wreath, archetype, key) index
    index: dict[int, list[tuple[int, int, int, str]]] = defaultdict(list)
    for k, v in coords.items():
        index[v["node_id"]].append((v["shell"], v["wreath"], v["archetype"], k))

    if a not in index:
        return f"Node {a} not found."
    if b not in index:
        return f"Node {b} not found."

    if a == b:
        return f"Source and target are the same node ({a})."

    # BFS over node IDs, expanding by shell adjacency
    from collections import deque

    # Pre-compute shell → set of node_ids
    shell_nodes: dict[int, set[int]] = defaultdict(set)
    node_shell: dict[int, int] = {}
    node_wreath: dict[int, int] = {}
    for nid, entries in index.items():
        for sh, wr, ar, _ in entries:
            shell_nodes[sh].add(nid)
            node_shell[nid] = sh
            node_wreath[nid] = wr

    visited: set[int] = {a}
    queue: deque[tuple[int, list[int]]] = deque([(a, [a])])

    while queue:
        current, path = queue.popleft()
        if len(path) > 20:
            break  # cap search depth
        c_shell = node_shell.get(current, 0)
        c_wreath = node_wreath.get(current, 0)

        # Expand to adjacent shells
        for adj_shell in (c_shell - 1, c_shell, c_shell + 1):
            if adj_shell < 1 or adj_shell > TOTAL_SHELLS:
                continue
            for neighbor in shell_nodes.get(adj_shell, set()):
                if neighbor in visited:
                    continue
                new_path = path + [neighbor]
                if neighbor == b:
                    steps = [
                        f"  {i+1}. node {n} (shell {node_shell.get(n, '?')})"
                        for i, n in enumerate(new_path)
                    ]
                    return (
                        f"## Route: node {a} \u2192 node {b}\n\n"
                        f"**Hops**: {len(new_path) - 1}\n\n"
                        + "\n".join(steps) + "\n"
                    )
                visited.add(neighbor)
                queue.append((neighbor, new_path))

    return (
        f"No route found between node {a} and node {b} within 20 hops.\n"
        "The nodes may be in disconnected shell regions."
    )
