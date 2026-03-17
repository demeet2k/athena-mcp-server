"""
MASTER LEDGER HOLOGRAM ENGINE -- Total Holographic Snapshot H_Sigma
====================================================================

The 9th executable Python layer.  Capstone engine.

Builds the 12-component Total Holographic Snapshot:

    H_Sigma = (N, E, Z, A, L, T, B, D, W, Psi, M, R)

    N   = 19 Nexus rows (structural vertices of the organism)
    E   = 13 Route families (canonical reading paths)
    Z   = Z-chain (Z* -> Z0 -> Z+ -> A+*)
    A   = Aether-Zero manifold
    L   = Master Ledger (40-file census, 351,927 words)
    T   = 6 Tunnel classes (~2200 tunnels)
    B   = 256-state Timing Byte (Z_4^4 toroidal lattice)
    D   = Dimensional stratum (3D -> 6D -> 12D -> 36D -> 108D)
    W   = 5-Wheel Crown (W_1, W_3, W_5, W_7, W_9)
    Psi = Sefirot pipeline (10 stages x 3 wreaths)
    M   = Metro map (6 line classes)
    R   = Mycelium rails (5 types)

Then constructs the 4864-cell Mindsweeper Matrix:
    19 nexus rows x 256 timing columns = 4864 cells
    Each cell weighted on 7 axes, classified into 8 classes.

Plus: hidden nexus inference, master-key orientations,
      route gate book, nexus exposure book, fixed-point stabilization.

Output: 23_MASTER_LEDGER_HOLOGRAM.md + receipt

v1.0 -- 2026-03-14
"""

from __future__ import annotations
import hashlib
import math
import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Optional

# =====================================================================
# UPSTREAM IMPORTS (all 8 layers)
# =====================================================================

from canon_compiler import (
    Quaternion, PHI, INV_PHI,
    ArtifactClass, SymmetryArtifact, TruthClass,
)

from sos_5d_expander import (
    ALL_UNITS, CHAPTERS, APPENDICES, EMERGENT, REVERSE_APPENDICES,
    ManuscriptUnit, UnitKind,
    _build_full_60_artifacts,
)

from hologram_4d_compressor import (
    Hologram4DCompressor, CompressedSeed, Base4Address,
    OddLift, WeaveClass,
)

from z_plus_ae_plus_framework import (
    invert_seed, build_poles, compute_60_symmetry_dimensions,
    collapse_to_z_plus, build_ae_plus_framework,
    ZPlusPoint, AEPlusFramework, Pole, InvertedSeed, SymmetryDimension,
)

from z_plus_ae_plus_router import (
    ZPlusAEPlusRouter, decompose_intent, RoutingResult,
)

from time_crystal_108d import (
    Face, Mode, Archetype, LensOperation, ShellArchetype,
    Shell, MegaNode, Wreath, Sefira, SEFIROT,
    build_12_archetypes, build_sigma_15, build_36_shells,
    build_666_nodes, wire_connections, build_sigma_60,
    extract_a_plus_poles, compute_master_seed, verify_conformance,
    TimeCrystalSeed, SHELL_ARCHETYPES, DIMENSIONAL_TOWER,
    ConformanceResult, Sigma60Station, APlusPole,
)

from time_crystal_108d_integrator import (
    IntegratedNode, MetroLine108D, MyceliumRail108D,
    ZChainPoint, SacredFigure108D, Tunnel108D,
    LiminalCoordinate, CanonicalRoute, LedgerRecord,
    WitnessAnchor, TimeCrystalIntegration,
    MetroLineType, RailType, ZLevel, TunnelType, RouteType,
    map_units_to_nodes, build_metro_lines, build_mycelium_rails,
    assign_sacred_geometry, build_z_chain, build_tunnels,
    wire_sefirot, bfs_reachability,
    extended_conformance, assign_liminal_coordinates,
    build_canonical_routes, build_master_ledger,
)

from time_crystal_wheel_crown import (
    Sigma60Quartet, build_sigma60_quartets,
    extract_dual_seed_pair,
    TriadicCrown, build_triadic_crown,
    build_multi_wheel_crown, WheelFamily,
    FOUR_OCTAVE_TOWER, OctaveLevel,
    EmergentSeedMatrix, build_emergent_seed_matrix,
    ReverseCanopyW7, build_reverse_canopy_w7,
    build_aether_point, execute_hcrl_pass, AetherFace,
    WHEEL_LADDER, DimensionalWheelMapping,
    validate_canonical_weaves,
)


# =====================================================================
# SECTION 1: TIMING BYTE (256-STATE Z_4^4 TOROIDAL LATTICE)
# =====================================================================

class FacePhase(Enum):
    """q0: Face phase."""
    SQUARE  = 0  # Earth
    FLOWER  = 1  # Fire
    CLOUD   = 2  # Water
    FRACTAL = 3  # Air


class ModePhase(Enum):
    """q1: Mode phase."""
    SU   = 0  # Sulfur / Cardinal
    ME   = 1  # Mercury / Mutable
    SA   = 2  # Salt / Fixed
    REST = 3  # Quiescent


class WreathPhase(Enum):
    """q2: Wreath activation."""
    SULFUR  = 0
    MERCURY = 1
    SALT    = 2
    ALL     = 3


class OctavePhase(Enum):
    """q3: Octave level."""
    OMEGA_0 = 0  # 12
    OMEGA_1 = 1  # 6912
    OMEGA_2 = 2  # ~7.1e21
    OMEGA_3 = 3  # ~10^231


@dataclass
class TimingByte:
    """One of 256 timing states in the Z_4^4 toroidal lattice.

    B = q0 + 4*q1 + 16*q2 + 64*q3   where each qi in {0,1,2,3}
    """
    q0: int  # Face phase
    q1: int  # Mode phase
    q2: int  # Wreath activation
    q3: int  # Octave level

    @property
    def value(self) -> int:
        return self.q0 + 4 * self.q1 + 16 * self.q2 + 64 * self.q3

    @property
    def label(self) -> str:
        faces = ["Sq", "Fl", "Cl", "Fr"]
        modes = ["Su", "Me", "Sa", "Re"]
        wreaths = ["wSu", "wMe", "wSa", "wAl"]
        octaves = ["O0", "O1", "O2", "O3"]
        return f"{faces[self.q0]}.{modes[self.q1]}.{wreaths[self.q2]}.{octaves[self.q3]}"

    def hcrl_rotate(self) -> "TimingByte":
        """Cycle q0 through 0->1->2->3->0 (HCRL rotation) keeping other axes fixed."""
        return TimingByte((self.q0 + 1) % 4, self.q1, self.q2, self.q3)

    def full_hcrl_orbit(self) -> list["TimingByte"]:
        """Return the 4-element HCRL orbit of this timing byte."""
        orbit = [self]
        current = self
        for _ in range(3):
            current = current.hcrl_rotate()
            orbit.append(current)
        return orbit


def build_256_timing_bytes() -> list[TimingByte]:
    """Generate all 256 timing bytes in the Z_4^4 lattice."""
    result = []
    for q3 in range(4):
        for q2 in range(4):
            for q1 in range(4):
                for q0 in range(4):
                    result.append(TimingByte(q0, q1, q2, q3))
    return result


# =====================================================================
# SECTION 2: NEXUS REGISTRY (19 STRUCTURAL VERTICES)
# =====================================================================

@dataclass
class NexusRow:
    """One of the 19 structural vertices of the organism."""
    number: int
    label: str
    short_name: str
    degree: int           # Connectivity degree
    routes: list[str]     # Route families touching this nexus
    description: str
    native_face: int      # Native face phase (0-3)
    native_mode: int      # Native mode phase (0-3)
    stratum_level: int    # Dimensional stratum (1-5: 3D,6D,12D,36D,108D)
    tunnel_density: int   # Estimated tunnels at this nexus
    is_torsion: bool      # Is this a torsion gate?


def build_19_nexus_rows() -> list[NexusRow]:
    """Build the 19-row nexus registry."""
    return [
        NexusRow(1,  "Z* (Aether-Zero)", "Z*",
                 666, ["R01","R02","R03","R04","R05","R06","R07","R08","R09","R10","R11","R12","R13","R14"],
                 "Origin seed, identity quaternion", 0, 0, 5, 666, False),
        NexusRow(2,  "A+* (Master Seed)", "A+*",
                 666, ["R01","R02","R08"],
                 "Collapsed singularity", 3, 3, 5, 666, False),
        NexusRow(3,  "Ch01 (Crystal Shard)", "Ch01",
                 4, ["R09"],
                 "Legacy entry", 0, 0, 1, 12, False),
        NexusRow(4,  "Ch07 (Completion)", "Ch07",
                 5, ["R09","R11"],
                 "Sulfur close", 1, 0, 1, 15, False),
        NexusRow(5,  "Ch14 (Mirror)", "Ch14",
                 5, ["R09"],
                 "Mercury close", 2, 1, 1, 15, False),
        NexusRow(6,  "Ch21 (Crown)", "Ch21",
                 6, ["R09","R07"],
                 "Legacy exit, wreath handoff", 3, 2, 2, 18, False),
        NexusRow(7,  "E1 (Ignition)", "E1",
                 4, ["R10"],
                 "Emergent entry", 1, 0, 2, 10, False),
        NexusRow(8,  "E2 (Compiler)", "E2",
                 6, ["R10","R12"],
                 "Compiler hub", 0, 1, 2, 16, False),
        NexusRow(9,  "E6 (Engine)", "E6",
                 5, ["R10","R05"],
                 "Engine hub", 2, 1, 2, 14, False),
        NexusRow(10, "E9 (Seal)", "E9",
                 4, ["R10"],
                 "Emergent exit", 3, 2, 2, 10, False),
        NexusRow(11, "E10 (Handoff)", "E10",
                 3, ["R10","R14"],
                 "W_1 remap nucleus", 0, 3, 3, 8, False),
        NexusRow(12, "AppA (First App)", "AppA",
                 3, ["R09"],
                 "Lower crystal entry", 0, 0, 1, 6, False),
        NexusRow(13, "AppP (Last App)", "AppP",
                 3, ["R09"],
                 "Lower crystal exit", 3, 2, 1, 6, False),
        NexusRow(14, "AppZ (Canopy Top)", "AppZ",
                 4, ["R06"],
                 "Upper canopy entry", 3, 0, 3, 10, False),
        NexusRow(15, "AppK (Canopy Base)", "AppK",
                 4, ["R05"],
                 "Upper canopy exit, torsion gate", 2, 2, 3, 10, True),
        NexusRow(16, "Q (Ingress Torsion)", "Q",
                 36, ["R05"],
                 "A^Me_*, torsion gate", 1, 1, 4, 36, True),
        NexusRow(17, "O (Return Torsion)", "O",
                 36, ["R06"],
                 "Z^Sa_*, torsion gate", 2, 2, 4, 36, True),
        NexusRow(18, "Shell-12/24/36 (Wreath Handoffs)", "Shell-H",
                 12, ["R07","R13"],
                 "Inter-wreath gates", 0, 3, 4, 36, False),
        NexusRow(19, "Omega* (Crown Apex)", "Omega*",
                 9, ["R08","R14"],
                 "Four-Octave Tower apex", 3, 3, 5, 27, False),
    ]


# =====================================================================
# SECTION 3: HIDDEN NEXUS CANDIDATES
# =====================================================================

@dataclass
class HiddenNexus:
    """A candidate hidden nexus inferred from structural pressure."""
    code: str
    name: str
    description: str
    pressure_source: str
    estimated_degree: int
    novelty_score: float   # 0-1: how novel / unexpected


def infer_hidden_nexuses() -> list[HiddenNexus]:
    """Infer 6 hidden nexus candidates from structural pressure."""
    return [
        HiddenNexus("C1", "Mirror of Z*",
                     "Anti-identity, the shadow seed -- complement of gate 0 at gate 255",
                     "Structural: Z* at gate 0 implies anti-Z* at gate 255",
                     666, 0.95),
        HiddenNexus("C2", "Midpoint Ch10-Ch11",
                     "Legacy center of gravity -- the fulcrum of the 21-chapter spine",
                     "Geometric center of R09 (Legacy Spine)",
                     8, 0.70),
        HiddenNexus("C3", "E5 (Emergent Midpoint)",
                     "Bridge polarity -- center of the emergent 3x3 matrix",
                     "Topological center of R10 (Emergent Spine)",
                     6, 0.65),
        HiddenNexus("C4", "AppH (Appendix Center)",
                     "Center of the 16 appendices -- equidistant from AppA and AppP",
                     "Ring center of the appendix body",
                     5, 0.55),
        HiddenNexus("C5", "Shell-18 (Geometric Center)",
                     "Geometric center of the 36-shell lattice -- boundary of Mercury/Salt",
                     "Midpoint of the 36-shell mega-cascade",
                     12, 0.80),
        HiddenNexus("C6", "W_5 Apex (12D Wheel Peak)",
                     "Peak of the 5-spoke animal wheel at 12D -- embodied peak",
                     "Dimensional ladder: W_5 dominant at 12D, nexus of polarity + triad",
                     5, 0.60),
    ]


# =====================================================================
# SECTION 4: ROUTE FAMILIES (13 + 1 FULL TRAVERSAL)
# =====================================================================

@dataclass
class RouteFamily:
    """One of the 13 canonical route families (+ R14 full traversal)."""
    number: int
    name: str
    route_type: str
    required_nexuses: list[int]   # nexus numbers that must be active
    description: str


def build_route_families() -> list[RouteFamily]:
    """Build the 13+1 route families."""
    return [
        RouteFamily(1,  "Seed Collapse",     "Compression",   [1, 2],
                    "5D -> Z* -> 4D holographic seed"),
        RouteFamily(2,  "Seed Expansion",    "Decompression", [1, 2],
                    "4D seed -> Z* -> re-expand to full unit"),
        RouteFamily(3,  "HCRL Pass",         "Verification",  [1, 2, 19],
                    "Square->Flower->Cloud->Fractal 4-face rotation"),
        RouteFamily(4,  "Triadic Pulse",     "Heartbeat",     [1, 16, 17],
                    "Su->Me->Sa 3-mode heartbeat cycle"),
        RouteFamily(5,  "Mobius Ingress",    "Torsion gate",  [9, 15, 16],
                    "E6 -> AppK -> Q torsion entry"),
        RouteFamily(6,  "Mobius Return",     "Return gate",   [14, 17],
                    "AppZ -> O torsion return"),
        RouteFamily(7,  "Wreath Handoff",    "Inter-wreath",  [6, 18],
                    "Ch21 -> Shell-12/24/36 inter-wreath gate"),
        RouteFamily(8,  "Octave Ascent",     "Tower climb",   [2, 19],
                    "A+* -> Omega* four-octave tower climb"),
        RouteFamily(9,  "Legacy Spine",      "Linear read",   [3, 4, 5, 6, 12, 13],
                    "Ch01 -> Ch21 + AppA -> AppP linear read"),
        RouteFamily(10, "Emergent Spine",    "Compiler read", [7, 8, 9, 10, 11],
                    "E1 -> E10 compiler read"),
        RouteFamily(11, "Star of David",     "Sacred hexagram",[4, 1],
                    "Ch07 -> Z* sacred hexagram circuit"),
        RouteFamily(12, "Cross-Quadrant",    "4-quadrant proof",[8, 1],
                    "E2 -> Z* 4-quadrant proof traverse"),
        RouteFamily(13, "Shell Ascent",      "Mega-metro",    [18, 19],
                    "Shell-12/24/36 -> Omega* mega-metro ascent"),
        RouteFamily(14, "Full Traversal",    "Total circuit", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
                    "Composition of all routes -- full organism traverse"),
    ]


# =====================================================================
# SECTION 5: TUNNEL CLASSES
# =====================================================================

@dataclass
class TunnelClassSummary:
    """Summary of one tunnel class."""
    name: str
    estimated_count: int
    description: str


def build_tunnel_class_summaries() -> list[TunnelClassSummary]:
    return [
        TunnelClassSummary("WITHIN_SHELL",     666,  "Connections within a single shell (T_n nodes)"),
        TunnelClassSummary("CROSS_SHELL",      630,  "Shell-to-adjacent-shell connections"),
        TunnelClassSummary("CROSS_WREATH",     72,   "Wreath boundary crossings (Su/Me/Sa)"),
        TunnelClassSummary("ARCHETYPE_COLUMN", 500,  "Archetype-column vertical connections"),
        TunnelClassSummary("MOBIUS_PILLAR",    70,   "Q/O Mobius pillar torsion tunnels"),
        TunnelClassSummary("LEGACY_PRESERVED", 278,  "Legacy chapter-to-chapter preserved tunnels"),
    ]


# =====================================================================
# SECTION 6: WEIGHT FUNCTION AND CELL CLASSIFIER
# =====================================================================

@dataclass
class MindsweepCell:
    """One cell in the 4864-cell Mindsweeper matrix."""
    nexus_num: int
    timing_byte: int         # 0-255
    weight: float            # w(nu, B) composite weight
    classification: str      # one of 8 classes
    # Sub-weights
    connectivity: float
    route_coverage: float
    tunnel_density_w: float
    dimensional_reach: float
    timing_coherence: float
    polarity_balance: float
    novelty: float


def compute_weight(
    nexus: NexusRow,
    tb: TimingByte,
    rank_map: dict[int, float],
    hidden_map: dict[int, float],
) -> MindsweepCell:
    """Compute the weight w(nu, B) for a single nexus/timing pair.

    w = 20C + 20R + 15T + 15D + 10K + 10P + 10N

    C = connectivity (rank-normalized, not raw degree)
    R = route coverage (routes touching this nexus / 14)
    T = tunnel density (rank-normalized)
    D = dimensional reach (stratum 1-5 / 5)
    K = timing coherence
    P = polarity balance
    N = novelty (hidden nexus proximity)
    """
    # C: Connectivity -- rank-normalized so distribution is uniform across nexuses
    C = rank_map.get(nexus.number, 0.5)

    # R: Route coverage
    R = len(nexus.routes) / 14.0

    # T: Tunnel density -- log-scaled to prevent Z*/A+* from dominating
    import math as _m
    T = _m.log1p(nexus.tunnel_density) / _m.log1p(666)

    # D: Dimensional reach
    D = nexus.stratum_level / 5.0

    # K: Timing coherence -- how well the timing byte aligns with native phase
    # Face match has large range to make HCRL rotation (q0 cycling) discriminating
    face_match = 1.0 if tb.q0 == nexus.native_face else (0.6 if tb.q0 == (nexus.native_face + 2) % 4 else 0.2)
    mode_match = 1.0 if tb.q1 == nexus.native_mode else 0.25
    # Wreath: q2==3 (ALL) always resonates; otherwise match to native_mode
    wreath_match = 1.0 if tb.q2 == 3 else (0.8 if tb.q2 == nexus.native_mode else 0.3)
    # Octave alignment -- higher strata prefer higher octaves
    ideal_octave = min(nexus.stratum_level - 1, 3)
    octave_delta = abs(tb.q3 - ideal_octave)
    octave_match = 1.0 / (1.0 + 0.7 * octave_delta)
    K = (face_match + mode_match + wreath_match + octave_match) / 4.0

    # P: Polarity balance -- Z*/Aether balance
    if nexus.is_torsion:
        # Torsion gates: balanced at middle octaves
        P = 1.0 - 0.15 * abs(tb.q3 - 1.5)
    elif nexus.number in (1, 3, 4, 5, 12, 13):
        # Z*-polar: best when q3 is low
        P = 1.0 - 0.25 * tb.q3
    elif nexus.number in (2, 19):
        # A+-polar: best when q3 is high
        P = 0.25 + 0.25 * tb.q3
    elif nexus.number in (6, 7, 8, 9, 10, 11):
        # Emergent / wreath nexuses: balanced in middle
        P = 0.5 + 0.25 * (1.0 - abs(tb.q3 - 1.5) / 1.5)
    else:
        P = 0.6

    # N: Novelty -- hidden nexus proximity
    N = hidden_map.get(nexus.number, 0.0)

    # Composite weight
    w = 20 * C + 20 * R + 15 * T + 15 * D + 10 * K + 10 * P + 10 * N

    return MindsweepCell(
        nexus_num=nexus.number,
        timing_byte=tb.value,
        weight=w,
        classification="",  # Will be set by classifier
        connectivity=C,
        route_coverage=R,
        tunnel_density_w=T,
        dimensional_reach=D,
        timing_coherence=K,
        polarity_balance=P,
        novelty=N,
    )


def classify_cell(cell: MindsweepCell) -> str:
    """Classify a cell into one of 8 classes (priority order).

    Thresholds tuned for range [5, 100] with meaningful spread.
    """
    w = cell.weight
    high_novelty = cell.novelty > 0.5
    low_novelty = cell.novelty <= 0.5

    if w < 12:
        return "contradictory"
    if w >= 85:
        return "master-key"
    if w >= 70:
        if high_novelty and cell.connectivity < 0.8:
            return "hidden-pressure"
        if cell.timing_coherence >= 0.6:
            return "master-key"
        return "promising"
    if w >= 55:
        if high_novelty:
            return "hidden-pressure"
        if cell.timing_coherence >= 0.6:
            return "promising"
        return "seated"
    if w >= 40:
        if cell.timing_coherence < 0.4 and cell.connectivity < 0.4:
            return "frontier"
        if cell.connectivity >= 0.5:
            return "seated"
        return "unstable"
    if w >= 25:
        if cell.connectivity < 0.25:
            return "frontier"
        return "unstable"
    return "degenerate"


# =====================================================================
# SECTION 7: MINDSWEEPER MATRIX BUILDER
# =====================================================================

@dataclass
class MindsweepMatrix:
    """The 4864-cell Mindsweeper matrix.  19 nexus x 256 timing bytes."""
    cells: list[MindsweepCell]               # 4864 cells
    nexus_rows: list[NexusRow]               # 19 rows
    timing_bytes: list[TimingByte]           # 256 columns
    class_counts: dict[str, int]             # Global class distribution
    nexus_exposure: dict[int, dict[str, int]]  # Per-nexus classification distribution
    master_key_orientations: list[int]       # Top-10 timing bytes by master-key count
    fixed_points: list[MindsweepCell]        # HCRL-invariant cells
    route_gate_book: dict[int, list[int]]    # Route# -> list of open timing bytes


def build_mindsweep_matrix(
    nexus_rows: list[NexusRow],
    timing_bytes: list[TimingByte],
    hidden_nexuses: list[HiddenNexus],
    routes: list[RouteFamily],
) -> MindsweepMatrix:
    """Build the complete 4864-cell Mindsweeper matrix."""

    # Precompute hidden nexus proximity map
    # Hidden nexuses influence nearby real nexuses
    hidden_map: dict[int, float] = {}
    # C1 (Mirror of Z*) influences Z* (1) and A+* (2)
    hidden_map[1] = 0.95
    hidden_map[2] = 0.90
    # C2 (Ch10-Ch11 midpoint) influences Ch07(4), Ch14(5), Ch21(6)
    hidden_map[4] = 0.70
    hidden_map[5] = 0.65
    hidden_map[6] = 0.60
    # C3 (E5) influences E1(7), E6(9), E9(10)
    hidden_map[7] = 0.55
    hidden_map[9] = 0.65
    hidden_map[10] = 0.50
    # C4 (AppH) influences AppA(12), AppP(13)
    hidden_map[12] = 0.40
    hidden_map[13] = 0.40
    # C5 (Shell-18) influences Shell-H(18), Q(16), O(17)
    hidden_map[18] = 0.80
    hidden_map[16] = 0.55
    hidden_map[17] = 0.55
    # C6 (W_5 Apex) influences Omega*(19), E10(11)
    hidden_map[19] = 0.60
    hidden_map[11] = 0.50
    # Fill remaining
    for n in nexus_rows:
        if n.number not in hidden_map:
            hidden_map[n.number] = 0.1

    # Build rank-normalized connectivity map
    sorted_by_degree = sorted(nexus_rows, key=lambda n: n.degree)
    rank_map: dict[int, float] = {}
    for i, n in enumerate(sorted_by_degree):
        rank_map[n.number] = (i + 1) / len(sorted_by_degree)  # 0.05..1.0

    cells: list[MindsweepCell] = []
    for nexus in nexus_rows:
        for tb in timing_bytes:
            cell = compute_weight(nexus, tb, rank_map, hidden_map)
            cell.classification = classify_cell(cell)
            cells.append(cell)

    # Class counts
    class_counts = Counter(c.classification for c in cells)

    # Nexus exposure book
    nexus_exposure: dict[int, dict[str, int]] = {}
    for nexus in nexus_rows:
        nexus_cells = [c for c in cells if c.nexus_num == nexus.number]
        dist: dict[str, int] = {}
        for c in nexus_cells:
            dist[c.classification] = dist.get(c.classification, 0) + 1
        nexus_exposure[nexus.number] = dist

    # Master-key orientations: top-10 timing bytes by master-key count per column
    mk_by_col: dict[int, int] = {}
    for c in cells:
        if c.classification == "master-key":
            mk_by_col[c.timing_byte] = mk_by_col.get(c.timing_byte, 0) + 1
    top_10_mk = sorted(mk_by_col.keys(), key=lambda b: mk_by_col[b], reverse=True)[:10]

    # Fixed-point stabilization
    # A cell is a HCRL fixed point if its CLASSIFICATION is invariant under
    # the full 4-element HCRL orbit (cycling q0 through 0->1->2->3).
    # That is: all 4 orbit members share the same class.
    fixed_points: list[MindsweepCell] = []
    cell_lookup: dict[tuple[int, int], MindsweepCell] = {}
    for c in cells:
        cell_lookup[(c.nexus_num, c.timing_byte)] = c

    for nexus in nexus_rows:
        for tb in timing_bytes:
            base_cell = cell_lookup.get((nexus.number, tb.value))
            if base_cell is None:
                continue
            orbit = tb.full_hcrl_orbit()
            orbit_classes = set()
            for otb in orbit:
                oc = cell_lookup.get((nexus.number, otb.value))
                if oc:
                    orbit_classes.add(oc.classification)
            if len(orbit_classes) == 1:
                fixed_points.append(base_cell)

    # Deduplicate fixed points (keep unique nexus/byte combos)
    seen_fp = set()
    unique_fps: list[MindsweepCell] = []
    for fp in fixed_points:
        key = (fp.nexus_num, fp.timing_byte)
        if key not in seen_fp:
            seen_fp.add(key)
            unique_fps.append(fp)
    fixed_points = unique_fps

    # Route gate book
    route_gate_book: dict[int, list[int]] = {}
    for route in routes:
        open_bytes: list[int] = []
        for tb in timing_bytes:
            # A route is "open" at a timing byte when ALL its required nexuses
            # have weight > 30 at that timing byte (seated threshold)
            all_above = True
            for nx_num in route.required_nexuses:
                c = cell_lookup.get((nx_num, tb.value))
                if c is None or c.weight <= 30:
                    all_above = False
                    break
            if all_above:
                open_bytes.append(tb.value)
        route_gate_book[route.number] = open_bytes

    return MindsweepMatrix(
        cells=cells,
        nexus_rows=nexus_rows,
        timing_bytes=timing_bytes,
        class_counts=dict(class_counts),
        nexus_exposure=nexus_exposure,
        master_key_orientations=top_10_mk,
        fixed_points=fixed_points,
        route_gate_book=route_gate_book,
    )


# =====================================================================
# SECTION 8: H-SIGMA SNAPSHOT CONTAINER
# =====================================================================

@dataclass
class HSigmaSnapshot:
    """The Total Holographic Snapshot H_Sigma = (N, E, Z, A, L, T, B, D, W, Psi, M, R).

    Plus: the Mindsweeper matrix, hidden nexuses, master-key orientations, etc.
    """
    # Core 12 components
    nexus_rows: list[NexusRow]                  # N
    route_families: list[RouteFamily]           # E
    z_chain: list[ZChainPoint]                  # Z
    aethers: list[AetherFace]                   # A
    ledger_records: list[LedgerRecord]          # L
    tunnel_summaries: list[TunnelClassSummary]  # T
    timing_bytes: list[TimingByte]              # B
    dimensional_tower: list[OctaveLevel]        # D
    wheels: list[WheelFamily]                   # W
    sefirot_map: dict[int, str]                 # Psi
    metro_lines: list[MetroLine108D]            # M
    rails: list[MyceliumRail108D]               # R

    # Extended structures
    mindsweep: MindsweepMatrix
    hidden_nexuses: list[HiddenNexus]
    integration: TimeCrystalIntegration
    crown: TriadicCrown
    canopy: ReverseCanopyW7
    seed: TimeCrystalSeed
    z_plus: ZPlusPoint
    ae_plus: AEPlusFramework

    # Hash
    h_sigma_hash: str = ""


# =====================================================================
# SECTION 9: UPSTREAM PIPELINE
# =====================================================================

def build_upstream_pipeline() -> dict:
    """Build all upstream layers and return the results as a dict."""
    results = {}

    # Layer 1-2: 108D Time Crystal
    archetypes = build_12_archetypes()
    ops_15 = build_sigma_15()
    shells = build_36_shells()
    mega_nodes = build_666_nodes(shells)
    wire_connections(mega_nodes, shells)
    stations_60 = build_sigma_60(ops_15)
    a_plus_poles = extract_a_plus_poles(stations_60)
    base_conformance = verify_conformance(shells, mega_nodes, archetypes)
    seed = compute_master_seed(mega_nodes, a_plus_poles)
    results["archetypes"] = archetypes
    results["shells"] = shells
    results["mega_nodes"] = mega_nodes
    results["stations_60"] = stations_60
    results["a_plus_poles"] = a_plus_poles
    results["base_conformance"] = base_conformance
    results["seed"] = seed

    # Layer 3-4: 4D Hologram + Z+/AE+
    compressor = Hologram4DCompressor()
    comp_seeds = compressor.compress_all()
    inv_seeds = [invert_seed(s) for s in comp_seeds]
    z0, ae0 = build_poles()
    artifacts = _build_full_60_artifacts()
    dimensions = compute_60_symmetry_dimensions(comp_seeds, inv_seeds, artifacts, z0, ae0)
    z_plus = collapse_to_z_plus(dimensions, comp_seeds, inv_seeds)
    ae_plus = build_ae_plus_framework(z_plus, dimensions)
    results["comp_seeds"] = comp_seeds
    results["inv_seeds"] = inv_seeds
    results["z0"] = z0
    results["ae0"] = ae0
    results["artifacts_60"] = artifacts
    results["dimensions"] = dimensions
    results["z_plus"] = z_plus
    results["ae_plus"] = ae_plus

    # Layer 7: Integration
    unit_map = map_units_to_nodes(mega_nodes, shells)
    metro_lines = build_metro_lines(mega_nodes, shells)
    rails = build_mycelium_rails(mega_nodes, shells)
    figures = assign_sacred_geometry(mega_nodes)
    z_chain = build_z_chain(z0, z_plus, seed)
    tunnels = build_tunnels(mega_nodes, shells, comp_seeds)
    node_to_sefira = wire_sefirot(mega_nodes, shells)
    bfs_reach = bfs_reachability(tunnels)
    ext_conf = extended_conformance(base_conformance, unit_map, metro_lines,
                                    rails, z_chain, figures, bfs_reach)
    coordinates = assign_liminal_coordinates(mega_nodes, unit_map,
                                             node_to_sefira, rails, tunnels)
    canonical_routes = build_canonical_routes(mega_nodes, shells)
    ledger_records, witness_anchors = build_master_ledger(
        unit_map, tunnels, canonical_routes, z_chain, mega_nodes)
    results["unit_map"] = unit_map
    results["metro_lines"] = metro_lines
    results["rails"] = rails
    results["figures"] = figures
    results["z_chain"] = z_chain
    results["tunnels"] = tunnels
    results["node_to_sefira"] = node_to_sefira
    results["bfs_reach"] = bfs_reach
    results["ext_conf"] = ext_conf
    results["coordinates"] = coordinates
    results["canonical_routes"] = canonical_routes
    results["ledger_records"] = ledger_records

    # Build Integration container
    witnesses: list[WitnessAnchor] = witness_anchors
    integrated_nodes: list[IntegratedNode] = []
    for mn in mega_nodes:
        gi = mn.global_index
        i_node = IntegratedNode(
            mega_node=mn,
            manuscript_units=unit_map.get(gi, []),
            metro_lines=[ml.name for ml in metro_lines if gi in ml.node_sequence],
            rails=[r.name for r in rails if gi in r.node_stops],
            sacred_figure=figures.get(gi, SacredFigure108D("Unknown", "W0", "none", "Nigredo")),
            z_chain_level=z_chain[min(gi % len(z_chain), len(z_chain)-1)].level.value if z_chain else "Z*_3D",
            sefirot_stage=node_to_sefira.get(gi, "Unknown"),
            tunnel_count=sum(1 for t in tunnels if t.source == gi or t.target == gi),
            liminal=coordinates.get(gi, LiminalCoordinate(
                L0_corpus="ATHENACHKA", L1_body_family="UNKNOWN",
                L2_structural_band="108D-CORE", L3_phase_wreath="Su",
                L4_node_id=f"N{gi:03d}", L5_route_rail="NONE",
                L6_nexus_density=0, L7_orbit_phase=0,
                L8_dim_stratum="3D", L9_polarity="Z*",
                L10_function_state="IDLE", L11_load_intensity=1,
            )),
        )
        integrated_nodes.append(i_node)

    integration = TimeCrystalIntegration(
        nodes=integrated_nodes,
        metro_lines=metro_lines,
        rails=rails,
        z_chain=z_chain,
        figures=figures,
        tunnels=tunnels,
        coordinates=coordinates,
        routes=canonical_routes,
        ledger=ledger_records,
        witnesses=witnesses,
        conformance=base_conformance,
        extended_conformance=ext_conf,
        bfs_reachable=bfs_reach,
        shells=shells,
        mega_nodes=mega_nodes,
        seed=seed,
        z_plus=z_plus,
        ae_plus=ae_plus,
    )
    results["integration"] = integration

    # Layer 8: Wheel Crown
    quartets = build_sigma60_quartets(stations_60)
    a_poles, z_poles, a_star_q, z_star_q = extract_dual_seed_pair(quartets)
    crown = build_triadic_crown(a_star_q, z_star_q)
    wheels = build_multi_wheel_crown(crown)
    aethers = build_aether_point()
    hcrl = execute_hcrl_pass(aethers)
    e_matrix = build_emergent_seed_matrix(crown)
    canopy = build_reverse_canopy_w7(crown, a_star_q, z_star_q, REVERSE_APPENDICES)
    results["quartets"] = quartets
    results["crown"] = crown
    results["wheels"] = wheels
    results["aethers"] = aethers
    results["hcrl"] = hcrl
    results["e_matrix"] = e_matrix
    results["canopy"] = canopy
    results["a_star_q"] = a_star_q
    results["z_star_q"] = z_star_q

    return results


# =====================================================================
# SECTION 10: H-SIGMA BUILDER
# =====================================================================

def build_h_sigma(upstream: dict) -> HSigmaSnapshot:
    """Build the Total Holographic Snapshot H_Sigma from upstream results."""

    # N: 19 Nexus rows
    nexus_rows = build_19_nexus_rows()

    # E: 13+1 Route families
    route_families = build_route_families()

    # Z: Z-chain
    z_chain = upstream["z_chain"]

    # A: Aether manifold
    aethers = upstream["aethers"]

    # L: Master Ledger
    ledger_records = upstream["ledger_records"]

    # T: Tunnel classes
    tunnel_summaries = build_tunnel_class_summaries()

    # B: 256 Timing bytes
    timing_bytes = build_256_timing_bytes()

    # D: Dimensional tower
    dimensional_tower = list(FOUR_OCTAVE_TOWER)

    # W: 5 Wheels
    wheels = upstream["wheels"]

    # Psi: Sefirot map
    sefirot_map = upstream["node_to_sefira"]

    # M: Metro lines
    metro_lines = upstream["metro_lines"]

    # R: Rails
    rails = upstream["rails"]

    # Hidden nexuses
    hidden_nexuses = infer_hidden_nexuses()

    # Build Mindsweep matrix
    mindsweep = build_mindsweep_matrix(nexus_rows, timing_bytes, hidden_nexuses, route_families)

    # Compute H_Sigma hash
    hash_data = (
        f"H_SIGMA:{len(nexus_rows)}:{len(route_families)}:{len(z_chain)}:"
        f"{len(aethers)}:{len(ledger_records)}:{len(tunnel_summaries)}:"
        f"{len(timing_bytes)}:{len(dimensional_tower)}:{len(wheels)}:"
        f"{len(sefirot_map)}:{len(metro_lines)}:{len(rails)}:"
        f"{mindsweep.class_counts}:{len(mindsweep.fixed_points)}"
    )
    h_sigma_hash = hashlib.sha256(hash_data.encode()).hexdigest()[:24]

    return HSigmaSnapshot(
        nexus_rows=nexus_rows,
        route_families=route_families,
        z_chain=z_chain,
        aethers=aethers,
        ledger_records=ledger_records,
        tunnel_summaries=tunnel_summaries,
        timing_bytes=timing_bytes,
        dimensional_tower=dimensional_tower,
        wheels=wheels,
        sefirot_map=sefirot_map,
        metro_lines=metro_lines,
        rails=rails,
        mindsweep=mindsweep,
        hidden_nexuses=hidden_nexuses,
        integration=upstream["integration"],
        crown=upstream["crown"],
        canopy=upstream["canopy"],
        seed=upstream["integration"].seed,
        z_plus=upstream["z_plus"],
        ae_plus=upstream["ae_plus"],
        h_sigma_hash=h_sigma_hash,
    )


# =====================================================================
# SECTION 11: DOCUMENT GENERATION
# =====================================================================

def generate_master_document(hs: HSigmaSnapshot) -> str:
    """Generate the 23_MASTER_LEDGER_HOLOGRAM.md document."""
    # Build cell lookup for route gate detail
    cell_lookup_doc: dict[tuple[int, int], float] = {}
    for c in hs.mindsweep.cells:
        cell_lookup_doc[(c.nexus_num, c.timing_byte)] = c.weight

    lines: list[str] = []

    lines.append("# MASTER LEDGER HOLOGRAM -- Total Holographic Snapshot H_Sigma")
    lines.append("")
    lines.append("**H_Sigma = (N, E, Z, A, L, T, B, D, W, Psi, M, R)**")
    lines.append("")
    lines.append(f"**Hash:** `{hs.h_sigma_hash}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ---- Architecture overview ----
    lines.append("## 1. Architecture Overview")
    lines.append("")
    lines.append("```")
    lines.append("H_Sigma = 12-component Total Holographic Snapshot")
    lines.append("  N   = 19 nexus rows (structural vertices)")
    lines.append("  E   = 14 route families (canonical reading paths)")
    lines.append("  Z   = Z-chain (Z* -> Z0 -> Z+ -> A+*)")
    lines.append("  A   = Aether-Zero manifold (4 irreducible aethers)")
    lines.append(f"  L   = Master Ledger ({len(hs.ledger_records)} records)")
    lines.append("  T   = 6 Tunnel classes (~2200 tunnels)")
    lines.append("  B   = 256-state Timing Byte (Z_4^4 toroidal lattice)")
    lines.append("  D   = Dimensional stratum (3D -> 6D -> 12D -> 36D -> 108D)")
    lines.append(f"  W   = {len(hs.wheels)}-Wheel Crown (W_1, W_3, W_5, W_7, W_9)")
    lines.append(f"  Psi = Sefirot pipeline ({len(SEFIROT)} stages x 3 wreaths)")
    lines.append(f"  M   = Metro map ({len(hs.metro_lines)} lines, 6 classes)")
    lines.append(f"  R   = Mycelium rails ({len(hs.rails)} rails, 5 types)")
    lines.append("```")
    lines.append("")

    # ---- N: 19 Nexus Registry ----
    lines.append("## 2. Nexus Registry (N) -- 19 Structural Vertices")
    lines.append("")
    lines.append("| # | Label | Degree | Routes | Stratum | Torsion | Description |")
    lines.append("|---|-------|--------|--------|---------|---------|-------------|")
    for n in hs.nexus_rows:
        routes_str = ",".join(n.routes[:4])
        if len(n.routes) > 4:
            routes_str += f"...+{len(n.routes)-4}"
        torsion = "Yes" if n.is_torsion else ""
        lines.append(f"| {n.number:2d} | {n.short_name:10s} | {n.degree:3d} | "
                     f"{routes_str:20s} | {n.stratum_level}D | {torsion:3s} | {n.description} |")
    lines.append("")

    # ---- Hidden Nexuses ----
    lines.append("## 3. Hidden Nexus Candidates (6 Inferred)")
    lines.append("")
    lines.append("| Code | Name | Novelty | Source |")
    lines.append("|------|------|---------|--------|")
    for h in hs.hidden_nexuses:
        lines.append(f"| {h.code} | {h.name:30s} | {h.novelty_score:.2f} | {h.pressure_source[:50]} |")
    lines.append("")

    # ---- E: Route Families ----
    lines.append("## 4. Route Families (E) -- 14 Canonical Paths")
    lines.append("")
    lines.append("| # | Name | Type | Required Nexuses |")
    lines.append("|---|------|------|-----------------|")
    for r in hs.route_families:
        nx_str = ",".join(str(n) for n in r.required_nexuses[:5])
        if len(r.required_nexuses) > 5:
            nx_str += f"...+{len(r.required_nexuses)-5}"
        lines.append(f"| R{r.number:02d} | {r.name:20s} | {r.route_type:16s} | {nx_str} |")
    lines.append("")

    # ---- Z: Z-Chain ----
    lines.append("## 5. Z-Chain (Z)")
    lines.append("")
    for zc in hs.z_chain:
        lines.append(f"- **{zc.level.value}** ({zc.dim}D): {zc.source} -> {zc.maps_to}")
    lines.append("")

    # ---- A: Aether Manifold ----
    lines.append("## 6. Aether-Zero Manifold (A)")
    lines.append("")
    for ae in hs.aethers:
        lines.append(f"- **{ae.symbol}** ({ae.element}): {ae.essence}")
    lines.append("")

    # ---- T: Tunnel Classes ----
    lines.append("## 7. Tunnel Classes (T)")
    lines.append("")
    lines.append("| Type | Est. Count | Description |")
    lines.append("|------|-----------|-------------|")
    total_tunnels = 0
    for tc in hs.tunnel_summaries:
        lines.append(f"| {tc.name:20s} | {tc.estimated_count:5d} | {tc.description} |")
        total_tunnels += tc.estimated_count
    lines.append(f"| **TOTAL** | **{total_tunnels}** | |")
    lines.append("")

    # ---- B: Timing Byte Lattice ----
    lines.append("## 8. 256-State Timing Byte (B)")
    lines.append("")
    lines.append("```")
    lines.append("B = q0 + 4*q1 + 16*q2 + 64*q3")
    lines.append("  q0: Face phase   (Sq=0, Fl=1, Cl=2, Fr=3)")
    lines.append("  q1: Mode phase   (Su=0, Me=1, Sa=2, Re=3)")
    lines.append("  q2: Wreath       (wSu=0, wMe=1, wSa=2, wAll=3)")
    lines.append("  q3: Octave       (O0=0, O1=1, O2=2, O3=3)")
    lines.append("")
    lines.append("256 = 4^4, toroidal lattice with HCRL rotation on q0 axis")
    lines.append("```")
    lines.append("")

    # ---- D: Dimensional Tower ----
    lines.append("## 9. Dimensional Stratum (D)")
    lines.append("")
    lines.append("| Octave | Name | Base | Bits | Meaning |")
    lines.append("|--------|------|------|------|---------|")
    for o in hs.dimensional_tower:
        lines.append(f"| {o.level} | {o.name:20s} | {o.base_exp:30s} | {o.bits:.1f} | {o.meaning[:50]} |")
    lines.append("")

    # ---- W: Wheel Crown ----
    lines.append("## 10. 5-Wheel Crown (W)")
    lines.append("")
    for w in hs.wheels:
        spk = ", ".join(w.spokes[:4])
        if len(w.spokes) > 4:
            spk += f"...+{len(w.spokes)-4}"
        dim_str = f"dominant at {w.dominant_at_dim}D" if w.dominant_at_dim > 0 else "center"
        lines.append(f"- **W_{w.k}**: {w.name} ({len(w.spokes)} spokes, {dim_str})")
        lines.append(f"  - Spokes: {spk}")
        lines.append(f"  - Meaning: {w.meaning}")
    lines.append("")

    # ---- Psi: Sefirot ----
    lines.append("## 11. Sefirot Pipeline (Psi)")
    lines.append("")
    lines.append("10 stages x 3 wreaths = 30 Sefirot stations")
    lines.append("")
    sefira_dist = Counter(hs.sefirot_map.values())
    for name, count in sorted(sefira_dist.items()):
        lines.append(f"- {name}: {count} nodes")
    lines.append("")

    # ---- M: Metro Map ----
    lines.append("## 12. Metro Map (M)")
    lines.append("")
    metro_type_dist = Counter(ml.line_type.value for ml in hs.metro_lines)
    lines.append("| Line Class | Count | Total Stops |")
    lines.append("|------------|-------|-------------|")
    for lt, cnt in sorted(metro_type_dist.items()):
        stops = sum(ml.length for ml in hs.metro_lines if ml.line_type.value == lt)
        lines.append(f"| {lt:20s} | {cnt:5d} | {stops:5d} |")
    lines.append(f"| **TOTAL** | **{len(hs.metro_lines)}** | |")
    lines.append("")

    # ---- R: Mycelium Rails ----
    lines.append("## 13. Mycelium Rails (R)")
    lines.append("")
    rail_type_dist = Counter(r.rail_type.value for r in hs.rails)
    lines.append("| Rail Type | Count |")
    lines.append("|-----------|-------|")
    for rt, cnt in sorted(rail_type_dist.items()):
        lines.append(f"| {rt:15s} | {cnt:5d} |")
    lines.append(f"| **TOTAL** | **{len(hs.rails)}** |")
    lines.append("")

    # ---- Mindsweeper Matrix ----
    lines.append("---")
    lines.append("")
    lines.append("## 14. Mindsweeper Matrix (19 x 256 = 4864 cells)")
    lines.append("")
    lines.append("### 14.1 Global Classification Distribution")
    lines.append("")
    lines.append("| Class | Count | Percentage |")
    lines.append("|-------|-------|------------|")
    total_cells = sum(hs.mindsweep.class_counts.values())
    class_order = ["contradictory", "master-key", "hidden-pressure", "frontier",
                   "unstable", "seated", "promising", "degenerate"]
    for cls in class_order:
        cnt = hs.mindsweep.class_counts.get(cls, 0)
        pct = 100 * cnt / max(total_cells, 1)
        lines.append(f"| {cls:18s} | {cnt:5d} | {pct:6.2f}% |")
    lines.append(f"| **TOTAL** | **{total_cells}** | 100.00% |")
    lines.append("")

    # ---- Master-Key Orientations ----
    lines.append("### 14.2 Master-Key Orientations (Top 10)")
    lines.append("")
    lines.append("| Rank | Timing Byte | Label | Master-Key Nexuses |")
    lines.append("|------|-------------|-------|--------------------|")
    for rank, tb_val in enumerate(hs.mindsweep.master_key_orientations, 1):
        tb = hs.timing_bytes[tb_val]
        mk_count = sum(1 for c in hs.mindsweep.cells
                       if c.timing_byte == tb_val and c.classification == "master-key")
        lines.append(f"| {rank:2d} | B={tb_val:3d} | {tb.label} | {mk_count} nexuses |")
    lines.append("")

    # ---- Nexus Exposure Book ----
    lines.append("### 14.3 Nexus Exposure Book")
    lines.append("")
    lines.append("For each nexus, the distribution across 256 timing states:")
    lines.append("")
    for n in hs.nexus_rows:
        exp = hs.mindsweep.nexus_exposure.get(n.number, {})
        mk = exp.get("master-key", 0)
        seat = exp.get("seated", 0)
        prom = exp.get("promising", 0)
        hp = exp.get("hidden-pressure", 0)
        front = exp.get("frontier", 0)
        unst = exp.get("unstable", 0)
        contra = exp.get("contradictory", 0)
        degen = exp.get("degenerate", 0)
        lines.append(f"- **{n.short_name:10s}** (#{n.number:2d}): "
                     f"MK={mk:3d} Prom={prom:3d} HP={hp:3d} Seat={seat:3d} "
                     f"Front={front:3d} Unst={unst:3d} Contra={contra:3d} Degen={degen:3d}")
    lines.append("")

    # ---- Route Gate Book ----
    lines.append("### 14.4 Route Gate Book")
    lines.append("")
    lines.append("For each route, how many of the 256 timing bytes are 'open':")
    lines.append("")
    for r in hs.route_families:
        open_count = len(hs.mindsweep.route_gate_book.get(r.number, []))
        bar = "#" * (open_count // 4)
        lines.append(f"- **R{r.number:02d} {r.name:20s}**: {open_count:3d}/256 open  {bar}")
    lines.append("")

    # ---- Fixed Points ----
    lines.append("### 14.5 Fixed-Point Stabilization (HCRL-invariant cells)")
    lines.append("")
    lines.append(f"**Total fixed points:** {len(hs.mindsweep.fixed_points)}")
    lines.append("")
    # Distribution by nexus
    fp_by_nexus = Counter(fp.nexus_num for fp in hs.mindsweep.fixed_points)
    lines.append("| Nexus | Fixed Points | % of 256 |")
    lines.append("|-------|-------------|----------|")
    for n in hs.nexus_rows:
        cnt = fp_by_nexus.get(n.number, 0)
        pct = 100 * cnt / 256
        if cnt > 0:
            lines.append(f"| {n.short_name:10s} | {cnt:3d} | {pct:5.1f}% |")
    lines.append("")
    # Distribution by class
    fp_by_class = Counter(fp.classification for fp in hs.mindsweep.fixed_points)
    lines.append("Fixed-point classification distribution:")
    lines.append("")
    for cls in class_order:
        cnt = fp_by_class.get(cls, 0)
        if cnt > 0:
            lines.append(f"- {cls}: {cnt}")
    lines.append("")

    # ---- Full 19x8 Class Matrix ----
    lines.append("### 14.6 Full Nexus x Class Matrix")
    lines.append("")
    lines.append("| Nexus      | MK   | HP   | Prom | Seat | Front | Unst | Contra | Degen |")
    lines.append("|------------|------|------|------|------|-------|------|--------|-------|")
    for n in hs.nexus_rows:
        exp = hs.mindsweep.nexus_exposure.get(n.number, {})
        lines.append(
            f"| {n.short_name:10s} "
            f"| {exp.get('master-key',0):4d} "
            f"| {exp.get('hidden-pressure',0):4d} "
            f"| {exp.get('promising',0):4d} "
            f"| {exp.get('seated',0):4d} "
            f"| {exp.get('frontier',0):4d} "
            f"| {exp.get('unstable',0):4d} "
            f"| {exp.get('contradictory',0):4d} "
            f"| {exp.get('degenerate',0):4d} |"
        )
    lines.append("")

    # ---- Top 50 Master-Key Cells ----
    lines.append("### 14.7 Top 50 Master-Key Cells (by weight)")
    lines.append("")
    mk_cells = sorted(
        [c for c in hs.mindsweep.cells if c.classification == "master-key"],
        key=lambda c: c.weight, reverse=True
    )[:50]
    if mk_cells:
        lines.append("| Rank | Nexus | B | Label | Weight | C | R | T | D | K | P | N |")
        lines.append("|------|-------|---|-------|--------|-----|-----|-----|-----|-----|-----|-----|")
        for rank, c in enumerate(mk_cells, 1):
            tb = hs.timing_bytes[c.timing_byte]
            nxs = next((n for n in hs.nexus_rows if n.number == c.nexus_num), None)
            nxlabel = nxs.short_name if nxs else f"N{c.nexus_num}"
            lines.append(
                f"| {rank:2d} | {nxlabel:6s} | {c.timing_byte:3d} | {tb.label} "
                f"| {c.weight:5.1f} "
                f"| {c.connectivity:.2f} | {c.route_coverage:.2f} "
                f"| {c.tunnel_density_w:.2f} | {c.dimensional_reach:.2f} "
                f"| {c.timing_coherence:.2f} | {c.polarity_balance:.2f} "
                f"| {c.novelty:.2f} |"
            )
    else:
        lines.append("*No master-key cells detected.*")
    lines.append("")

    # ---- Top 30 Hidden-Pressure Cells ----
    lines.append("### 14.8 Top 30 Hidden-Pressure Cells")
    lines.append("")
    hp_cells = sorted(
        [c for c in hs.mindsweep.cells if c.classification == "hidden-pressure"],
        key=lambda c: c.weight, reverse=True
    )[:30]
    if hp_cells:
        lines.append("| Rank | Nexus | B | Weight | Novelty |")
        lines.append("|------|-------|---|--------|---------|")
        for rank, c in enumerate(hp_cells, 1):
            nxs = next((n for n in hs.nexus_rows if n.number == c.nexus_num), None)
            nxlabel = nxs.short_name if nxs else f"N{c.nexus_num}"
            lines.append(f"| {rank:2d} | {nxlabel:6s} | {c.timing_byte:3d} | {c.weight:5.1f} | {c.novelty:.2f} |")
    else:
        lines.append("*No hidden-pressure cells detected.*")
    lines.append("")

    # ---- Per-Route Gate Detail ----
    lines.append("### 14.9 Route Gate Detail (per route)")
    lines.append("")
    for r in hs.route_families:
        open_bytes = hs.mindsweep.route_gate_book.get(r.number, [])
        lines.append(f"#### R{r.number:02d}: {r.name} ({r.route_type})")
        lines.append("")
        lines.append(f"Required nexuses: {r.required_nexuses}")
        lines.append(f"Open timing bytes: {len(open_bytes)}/256")
        if open_bytes and len(open_bytes) <= 64:
            # List them
            byte_strs = [str(b) for b in open_bytes[:32]]
            lines.append(f"  Bytes: {', '.join(byte_strs)}")
            if len(open_bytes) > 32:
                lines.append(f"  ... and {len(open_bytes)-32} more")
        elif open_bytes:
            lines.append(f"  First 16: {', '.join(str(b) for b in open_bytes[:16])} ...")
        lines.append("")
        # Per-nexus weight statistics at open bytes
        if open_bytes and r.required_nexuses:
            lines.append("  Nexus weight statistics at open bytes:")
            for nx_num in r.required_nexuses[:6]:
                nxs = next((n for n in hs.nexus_rows if n.number == nx_num), None)
                nxlabel = nxs.short_name if nxs else f"N{nx_num}"
                nx_weights = [
                    cell_lookup_doc.get((nx_num, b), 0)
                    for b in open_bytes[:32]
                ]
                if nx_weights and any(isinstance(w, (int, float)) for w in nx_weights):
                    avg_w = sum(w for w in nx_weights if isinstance(w, (int, float))) / max(len(nx_weights), 1)
                    lines.append(f"    {nxlabel}: avg weight = {avg_w:.1f}")
        lines.append("")

    # ---- Timing Byte Legend (grouped by octave) ----
    lines.append("### 14.10 Full 256-State Timing Byte Legend")
    lines.append("")
    for q3 in range(4):
        lines.append(f"#### Octave {q3} (B = {q3*64}..{q3*64+63})")
        lines.append("")
        lines.append("| B | Face | Mode | Wreath | Label |")
        lines.append("|---|------|------|--------|-------|")
        faces = ["Square", "Flower", "Cloud", "Fractal"]
        modes = ["Sulfur", "Mercury", "Salt", "Rest"]
        wreaths = ["wSulfur", "wMercury", "wSalt", "wAll"]
        for q2 in range(4):
            for q1 in range(4):
                for q0 in range(4):
                    b = q0 + 4*q1 + 16*q2 + 64*q3
                    lines.append(
                        f"| {b:3d} | {faces[q0]:8s} | {modes[q1]:8s} "
                        f"| {wreaths[q2]:9s} | {hs.timing_bytes[b].label} |"
                    )
        lines.append("")

    # ---- Extended Conformance Checks ----
    lines.append("### 14.11 Extended Conformance (18-Point)")
    lines.append("")
    ext_checks = hs.integration.extended_conformance
    if ext_checks:
        lines.append("| # | Check | Pass | Detail |")
        lines.append("|---|-------|------|--------|")
        for i, (name, passed, detail) in enumerate(ext_checks, 1):
            mark = "PASS" if passed else "FAIL"
            lines.append(f"| {i:2d} | {name:30s} | {mark} | {detail[:60]} |")
    lines.append("")

    # ---- Cross-Nexus Timing Correlation ----
    lines.append("### 14.12 Cross-Nexus Weight Correlation (top pairs)")
    lines.append("")
    lines.append("Average weight difference between nexus pairs across 256 timing bytes:")
    lines.append("")
    # Pick the most interesting pairs
    interesting_pairs = [
        (1, 2), (1, 19), (1, 16), (1, 17), (2, 19),
        (3, 6), (7, 11), (16, 17), (4, 5), (8, 9),
        (12, 13), (14, 15), (6, 7), (18, 19), (3, 7),
    ]
    lines.append("| Nexus A | Nexus B | Mean |A-B| | Max |A-B| | Correlation |")
    lines.append("|---------|---------|---------|---------|-------------|")
    cell_lookup_corr: dict[tuple[int, int], float] = {}
    for c in hs.mindsweep.cells:
        cell_lookup_corr[(c.nexus_num, c.timing_byte)] = c.weight
    for na, nb in interesting_pairs:
        diffs = []
        for tb_val in range(256):
            wa = cell_lookup_corr.get((na, tb_val), 0)
            wb = cell_lookup_corr.get((nb, tb_val), 0)
            diffs.append(abs(wa - wb))
        mean_diff = sum(diffs) / len(diffs) if diffs else 0
        max_diff = max(diffs) if diffs else 0
        nxa = next((n for n in hs.nexus_rows if n.number == na), None)
        nxb = next((n for n in hs.nexus_rows if n.number == nb), None)
        la = nxa.short_name if nxa else f"N{na}"
        lb = nxb.short_name if nxb else f"N{nb}"
        # Simple correlation proxy
        corr = 1.0 - min(mean_diff / 50.0, 1.0)
        lines.append(f"| {la:10s} | {lb:10s} | {mean_diff:7.2f} | {max_diff:7.2f} | {corr:.3f} |")
    lines.append("")

    # ---- Ledger Records Sample ----
    lines.append("### 14.13 Master Ledger Records (first 30)")
    lines.append("")
    if hs.ledger_records:
        lines.append("| # | Record Type | Key | Data Summary |")
        lines.append("|---|------------|-----|-------------|")
        for i, lr in enumerate(hs.ledger_records[:30], 1):
            data_summary = str(lr.data)[:50] if lr.data else ""
            lines.append(f"| {i:2d} | {lr.record_type.value:15s} | {lr.key[:25]:25s} | {data_summary} |")
    lines.append("")

    # ---- Per-Nexus Detailed Profiles ----
    lines.append("### 14.14 Per-Nexus Detailed Profiles")
    lines.append("")
    for n in hs.nexus_rows:
        nx_cells = [c for c in hs.mindsweep.cells if c.nexus_num == n.number]
        ws = [c.weight for c in nx_cells]
        lines.append(f"#### Nexus #{n.number}: {n.label}")
        lines.append("")
        lines.append(f"- **Short name:** {n.short_name}")
        lines.append(f"- **Degree:** {n.degree}")
        lines.append(f"- **Routes:** {', '.join(n.routes)}")
        lines.append(f"- **Native face:** {n.native_face} (q0)")
        lines.append(f"- **Native mode:** {n.native_mode} (q1)")
        lines.append(f"- **Stratum:** {n.stratum_level}D")
        lines.append(f"- **Tunnel density:** {n.tunnel_density}")
        lines.append(f"- **Torsion gate:** {'Yes' if n.is_torsion else 'No'}")
        lines.append(f"- **Weight range:** [{min(ws):.1f}, {max(ws):.1f}]")
        lines.append(f"- **Weight mean:** {sum(ws)/len(ws):.2f}")
        lines.append(f"- **Weight median:** {sorted(ws)[len(ws)//2]:.2f}")
        exp = hs.mindsweep.nexus_exposure.get(n.number, {})
        dominant_class = max(exp.items(), key=lambda x: x[1])[0] if exp else "N/A"
        lines.append(f"- **Dominant class:** {dominant_class} ({exp.get(dominant_class, 0)}/256)")
        # Percentile thresholds
        sw = sorted(ws)
        p25 = sw[len(sw)//4]
        p50 = sw[len(sw)//2]
        p75 = sw[3*len(sw)//4]
        p90 = sw[int(len(sw)*0.9)]
        lines.append(f"- **Weight percentiles:** P25={p25:.1f}, P50={p50:.1f}, P75={p75:.1f}, P90={p90:.1f}")
        # Fixed points for this nexus
        fp_count = sum(1 for fp in hs.mindsweep.fixed_points if fp.nexus_num == n.number)
        lines.append(f"- **HCRL fixed points:** {fp_count}/256")
        lines.append("")

    # ---- Weight Percentile Matrix ----
    lines.append("### 14.15 Weight Percentile Matrix (all nexuses)")
    lines.append("")
    lines.append("| Nexus | P10 | P25 | P50 | P75 | P90 | Mean | StdDev |")
    lines.append("|-------|-----|-----|-----|-----|-----|------|--------|")
    for n in hs.nexus_rows:
        nx_cells = [c for c in hs.mindsweep.cells if c.nexus_num == n.number]
        ws = sorted([c.weight for c in nx_cells])
        mean_w = sum(ws) / len(ws)
        variance = sum((w - mean_w)**2 for w in ws) / len(ws)
        std_w = variance ** 0.5
        p10 = ws[int(len(ws)*0.1)]
        p25 = ws[len(ws)//4]
        p50 = ws[len(ws)//2]
        p75 = ws[3*len(ws)//4]
        p90 = ws[int(len(ws)*0.9)]
        lines.append(
            f"| {n.short_name:10s} | {p10:5.1f} | {p25:5.1f} | {p50:5.1f} "
            f"| {p75:5.1f} | {p90:5.1f} | {mean_w:5.1f} | {std_w:5.2f} |"
        )
    lines.append("")

    # ---- Fixed-Point Deep Analysis ----
    lines.append("### 14.16 Fixed-Point Analysis by Class")
    lines.append("")
    fp_by_class_nexus: dict[str, dict[int, int]] = {}
    for fp in hs.mindsweep.fixed_points:
        cls = fp.classification
        if cls not in fp_by_class_nexus:
            fp_by_class_nexus[cls] = {}
        fp_by_class_nexus[cls][fp.nexus_num] = fp_by_class_nexus[cls].get(fp.nexus_num, 0) + 1
    for cls in class_order:
        if cls in fp_by_class_nexus:
            lines.append(f"**{cls}** fixed points:")
            lines.append("")
            for n in hs.nexus_rows:
                cnt = fp_by_class_nexus[cls].get(n.number, 0)
                if cnt > 0:
                    lines.append(f"  - {n.short_name}: {cnt}")
            lines.append("")

    # ---- Sub-Weight Component Analysis ----
    lines.append("### 14.17 Sub-Weight Component Averages (per nexus)")
    lines.append("")
    lines.append("| Nexus | Conn | Route | Tunnel | Dim | Coher | Polar | Novel |")
    lines.append("|-------|------|-------|--------|-----|-------|-------|-------|")
    for n in hs.nexus_rows:
        nx_cells = [c for c in hs.mindsweep.cells if c.nexus_num == n.number]
        avg_c = sum(c.connectivity for c in nx_cells) / len(nx_cells)
        avg_r = sum(c.route_coverage for c in nx_cells) / len(nx_cells)
        avg_t = sum(c.tunnel_density_w for c in nx_cells) / len(nx_cells)
        avg_d = sum(c.dimensional_reach for c in nx_cells) / len(nx_cells)
        avg_k = sum(c.timing_coherence for c in nx_cells) / len(nx_cells)
        avg_p = sum(c.polarity_balance for c in nx_cells) / len(nx_cells)
        avg_n = sum(c.novelty for c in nx_cells) / len(nx_cells)
        lines.append(
            f"| {n.short_name:10s} | {avg_c:.3f} | {avg_r:.3f} | {avg_t:.3f} "
            f"| {avg_d:.3f} | {avg_k:.3f} | {avg_p:.3f} | {avg_n:.3f} |"
        )
    lines.append("")

    # ---- Octave x Wreath Breakdown ----
    lines.append("### 14.18 Octave x Wreath Class Distribution")
    lines.append("")
    lines.append("Classification distribution grouped by octave (q3) and wreath (q2):")
    lines.append("")
    for q3 in range(4):
        for q2 in range(4):
            subset = [c for c in hs.mindsweep.cells
                      if hs.timing_bytes[c.timing_byte].q3 == q3
                      and hs.timing_bytes[c.timing_byte].q2 == q2]
            if subset:
                dist = Counter(c.classification for c in subset)
                wreaths = ["wSu", "wMe", "wSa", "wAll"]
                mk = dist.get("master-key", 0)
                hp = dist.get("hidden-pressure", 0)
                seat = dist.get("seated", 0)
                unst = dist.get("unstable", 0)
                front = dist.get("frontier", 0)
                lines.append(
                    f"- O{q3}/{wreaths[q2]}: MK={mk} HP={hp} Seat={seat} "
                    f"Unst={unst} Front={front} (total={len(subset)})"
                )
    lines.append("")

    # ---- Best/Worst Timing Bytes per Nexus ----
    lines.append("### 14.19 Best and Worst Timing Bytes per Nexus")
    lines.append("")
    lines.append("Top-5 and bottom-5 timing bytes by weight for each nexus:")
    lines.append("")
    for n in hs.nexus_rows:
        nx_cells = sorted(
            [c for c in hs.mindsweep.cells if c.nexus_num == n.number],
            key=lambda c: c.weight, reverse=True
        )
        lines.append(f"**{n.short_name}** (#{n.number}):")
        lines.append("")
        lines.append("  Best 5:")
        for c in nx_cells[:5]:
            tb = hs.timing_bytes[c.timing_byte]
            lines.append(f"    B={c.timing_byte:3d} ({tb.label}) w={c.weight:.1f} [{c.classification}]")
        lines.append("  Worst 5:")
        for c in nx_cells[-5:]:
            tb = hs.timing_bytes[c.timing_byte]
            lines.append(f"    B={c.timing_byte:3d} ({tb.label}) w={c.weight:.1f} [{c.classification}]")
        lines.append("")

    # ---- Mode x Face Interaction Matrix ----
    lines.append("### 14.20 Mode x Face Interaction Matrix")
    lines.append("")
    lines.append("Average weight for each (face, mode) pair across all nexuses:")
    lines.append("")
    lines.append("| Face\\Mode | Sulfur | Mercury | Salt | Rest |")
    lines.append("|-----------|--------|---------|------|------|")
    faces_lbl = ["Square", "Flower", "Cloud", "Fractal"]
    for q0 in range(4):
        row = f"| {faces_lbl[q0]:9s} |"
        for q1 in range(4):
            subset_w = [c.weight for c in hs.mindsweep.cells
                        if hs.timing_bytes[c.timing_byte].q0 == q0
                        and hs.timing_bytes[c.timing_byte].q1 == q1]
            if subset_w:
                avg = sum(subset_w) / len(subset_w)
                row += f" {avg:6.2f} |"
            else:
                row += "   N/A |"
        lines.append(row)
    lines.append("")

    # ---- Classification Transition Heatmap under HCRL ----
    lines.append("### 14.21 HCRL Classification Transitions")
    lines.append("")
    lines.append("How often does the HCRL rotation (q0 -> q0+1) change the classification?")
    lines.append("")
    transition_count: dict[tuple[str, str], int] = {}
    # Build cell->classification lookup
    cell_cls_lookup: dict[tuple[int, int], str] = {}
    for c in hs.mindsweep.cells:
        cell_cls_lookup[(c.nexus_num, c.timing_byte)] = c.classification
    for nexus in hs.nexus_rows:
        for tb in hs.timing_bytes:
            c0_cls = cell_cls_lookup.get((nexus.number, tb.value))
            rotated = tb.hcrl_rotate()
            c1_cls = cell_cls_lookup.get((nexus.number, rotated.value))
            if c0_cls and c1_cls:
                key = (c0_cls, c1_cls)
                transition_count[key] = transition_count.get(key, 0) + 1
    if transition_count:
        lines.append("| From \\ To | " + " | ".join(f"{c[:6]:6s}" for c in class_order) + " |")
        lines.append("|-----------|" + "|".join("--------" for _ in class_order) + "|")
        for from_cls in class_order:
            row = f"| {from_cls[:9]:9s} |"
            for to_cls in class_order:
                cnt = transition_count.get((from_cls, to_cls), 0)
                row += f" {cnt:6d} |"
            lines.append(row)
    lines.append("")

    # ---- Upstream Integration Summary ----
    lines.append("---")
    lines.append("")
    lines.append("## 15. Upstream Integration Summary")
    lines.append("")
    lines.append("| Layer | File | Key Output |")
    lines.append("|-------|------|-----------|")
    lines.append("| 1 | canon_compiler.py | Quaternion, I_60, PHI, siteswap laws |")
    lines.append("| 2 | sos_5d_expander.py | 63 units, 5D coords, 10-stage pipeline |")
    lines.append("| 3 | hologram_4d_compressor.py | 63 compressed seeds, base-4, metro |")
    lines.append("| 4 | z_plus_ae_plus_framework.py | Z+/AE+, 60 symmetry dimensions |")
    lines.append("| 5 | z_plus_ae_plus_router.py | Intent routing, self-observation |")
    lines.append("| 6 | time_crystal_108d.py | 36 shells, 666 nodes, 3 wreaths |")
    lines.append("| 7 | time_crystal_108d_integrator.py | 14-phase integration, ledger |")
    lines.append("| 8 | time_crystal_wheel_crown.py | Wheel crown, canopy, emergent matrix |")
    lines.append("| 9 | master_ledger_hologram.py | THIS FILE -- H_Sigma capstone |")
    lines.append("")

    # ---- Key Invariants ----
    lines.append("## 16. Key Invariants")
    lines.append("")
    lines.append(f"- Z+ quaternion: {hs.z_plus.quaternion}")
    lines.append(f"- Z+ self-knowledge index: {hs.z_plus.self_knowledge_index:.6f}")
    lines.append(f"- AE+ phase-lock frequency: {hs.ae_plus.phase_lock_frequency:.2f} Hz")
    lines.append(f"- Love constant L = {hs.ae_plus.love_constant:.6f}")
    lines.append(f"- Master seed hash: {hs.seed.seed_hash}")
    lines.append(f"- H_Sigma hash: {hs.h_sigma_hash}")
    lines.append(f"- BFS reachability: {hs.integration.bfs_reachable}/666")
    lines.append(f"- Fixed points: {len(hs.mindsweep.fixed_points)}")
    lines.append(f"- Master-key cells: {hs.mindsweep.class_counts.get('master-key', 0)}")
    lines.append("")

    # ---- Crown Hexagon ----
    lines.append("## 17. Crown Hexagon Circuit")
    lines.append("")
    hex_labels = hs.crown.hexagon_circuit[:6]
    lines.append(f"```")
    lines.append(f"Crown hexagon: {' -> '.join(hex_labels)} -> ...")
    lines.append(f"Omega_* = {hs.crown.omega_star}")
    lines.append(f"```")
    lines.append("")

    # ---- Five Surviving Laws ----
    lines.append("## 18. The Five Surviving Laws")
    lines.append("")
    for i, law in enumerate(hs.z_plus.surviving_laws):
        lines.append(f"{i+1}. {law}")
    lines.append("")

    # ---- Mindsweeper Heatmap (ASCII) ----
    lines.append("## 19. Mindsweeper Heatmap (Nexus x Octave)")
    lines.append("")
    lines.append("Average weight per nexus per octave level (q3):")
    lines.append("")
    lines.append("| Nexus | O0 | O1 | O2 | O3 | Mean |")
    lines.append("|-------|-----|-----|-----|-----|------|")
    for n in hs.nexus_rows:
        octave_avgs = []
        for q3 in range(4):
            cells_at = [c for c in hs.mindsweep.cells
                        if c.nexus_num == n.number
                        and hs.timing_bytes[c.timing_byte].q3 == q3]
            if cells_at:
                avg = sum(c.weight for c in cells_at) / len(cells_at)
            else:
                avg = 0
            octave_avgs.append(avg)
        mean = sum(octave_avgs) / 4
        lines.append(f"| {n.short_name:10s} | {octave_avgs[0]:5.1f} | {octave_avgs[1]:5.1f} | "
                     f"{octave_avgs[2]:5.1f} | {octave_avgs[3]:5.1f} | {mean:5.1f} |")
    lines.append("")

    # ---- Dimensional Wheel Ladder ----
    lines.append("## 20. Dimensional Wheel Ladder")
    lines.append("")
    for wl in WHEEL_LADDER:
        active = ", ".join(f"W_{k}" for k in wl.active_wheels)
        lines.append(f"- **{wl.dim}D**: dominant W_{wl.dominant_wheel}, active: {active}")
        lines.append(f"  - {wl.meaning}")
    lines.append("")

    # ---- Final Synthesis ----
    lines.append("---")
    lines.append("")
    lines.append("## 21. Final Synthesis")
    lines.append("")
    lines.append("The Total Holographic Snapshot H_Sigma is COMPLETE.")
    lines.append("")
    lines.append("```")
    lines.append("12 components assembled:")
    lines.append(f"  N  = {len(hs.nexus_rows)} nexus rows")
    lines.append(f"  E  = {len(hs.route_families)} route families")
    lines.append(f"  Z  = {len(hs.z_chain)} Z-chain levels")
    lines.append(f"  A  = {len(hs.aethers)} aether faces")
    lines.append(f"  L  = {len(hs.ledger_records)} ledger records")
    lines.append(f"  T  = {sum(t.estimated_count for t in hs.tunnel_summaries)} tunnels (6 classes)")
    lines.append(f"  B  = {len(hs.timing_bytes)} timing bytes")
    lines.append(f"  D  = {len(hs.dimensional_tower)} octave levels")
    lines.append(f"  W  = {len(hs.wheels)} wheel families")
    lines.append(f"  Psi = {len(SEFIROT)} Sefirot stages x 3 wreaths")
    lines.append(f"  M  = {len(hs.metro_lines)} metro lines")
    lines.append(f"  R  = {len(hs.rails)} rails")
    lines.append("")
    lines.append(f"Mindsweeper: 19 x 256 = 4864 cells")
    lines.append(f"  Master-key cells:     {hs.mindsweep.class_counts.get('master-key', 0)}")
    lines.append(f"  Fixed points:         {len(hs.mindsweep.fixed_points)}")
    lines.append(f"  Master-key timings:   {len(hs.mindsweep.master_key_orientations)}")
    lines.append("")
    lines.append(f"H_Sigma hash: {hs.h_sigma_hash}")
    lines.append(f"L = {hs.ae_plus.love_constant:.6f}")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*The crystal is complete. Every cell has been swept.*")
    lines.append("*The timing byte lattice breathes. The nexus vertices hold.*")
    lines.append("*19 x 256 = 4864. The Mindsweeper has finished.*")
    lines.append("*L = S x S_l remains conserved at Z+ across all collapses.*")

    return "\n".join(lines)


# =====================================================================
# SECTION 12: RECEIPT GENERATION
# =====================================================================

def generate_receipt(hs: HSigmaSnapshot) -> str:
    """Generate the MASTER_LEDGER_HOLOGRAM_RECEIPT.md."""
    lines: list[str] = []

    lines.append("# MASTER LEDGER HOLOGRAM -- BUILD RECEIPT")
    lines.append("")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines.append(f"**Date:** {now}")
    lines.append(f"**Operation:** H_Sigma Total Holographic Snapshot -- 9th executable layer")
    lines.append(f"**Status:** COMPLETE")
    lines.append("")

    lines.append("## H_SIGMA COMPONENTS")
    lines.append("")
    lines.append("| Component | Symbol | Count |")
    lines.append("|-----------|--------|-------|")
    lines.append(f"| Nexus rows | N | {len(hs.nexus_rows)} |")
    lines.append(f"| Route families | E | {len(hs.route_families)} |")
    lines.append(f"| Z-chain levels | Z | {len(hs.z_chain)} |")
    lines.append(f"| Aether faces | A | {len(hs.aethers)} |")
    lines.append(f"| Ledger records | L | {len(hs.ledger_records)} |")
    lines.append(f"| Tunnel classes | T | {len(hs.tunnel_summaries)} |")
    lines.append(f"| Timing bytes | B | {len(hs.timing_bytes)} |")
    lines.append(f"| Octave levels | D | {len(hs.dimensional_tower)} |")
    lines.append(f"| Wheel families | W | {len(hs.wheels)} |")
    lines.append(f"| Sefirot stages | Psi | {len(SEFIROT)} |")
    lines.append(f"| Metro lines | M | {len(hs.metro_lines)} |")
    lines.append(f"| Rails | R | {len(hs.rails)} |")
    lines.append("")

    lines.append("## MINDSWEEPER MATRIX")
    lines.append("")
    lines.append(f"- Dimensions: 19 x 256 = 4864 cells")
    lines.append(f"- Classification distribution:")
    class_order = ["contradictory", "master-key", "hidden-pressure", "frontier",
                   "unstable", "seated", "promising", "degenerate"]
    for cls in class_order:
        cnt = hs.mindsweep.class_counts.get(cls, 0)
        lines.append(f"  - {cls}: {cnt}")
    lines.append(f"- Master-key orientations (top 10): {hs.mindsweep.master_key_orientations}")
    lines.append(f"- Fixed points (HCRL-invariant): {len(hs.mindsweep.fixed_points)}")
    lines.append("")

    lines.append("## HIDDEN NEXUSES")
    lines.append("")
    for h in hs.hidden_nexuses:
        lines.append(f"- {h.code}: {h.name} (novelty={h.novelty_score:.2f})")
    lines.append("")

    lines.append("## KEY INVARIANTS")
    lines.append("")
    lines.append(f"- Z+ self-knowledge: {hs.z_plus.self_knowledge_index:.6f}")
    lines.append(f"- AE+ phase-lock: {hs.ae_plus.phase_lock_frequency:.2f} Hz")
    lines.append(f"- L = {hs.ae_plus.love_constant:.6f}")
    lines.append(f"- Master seed: {hs.seed.seed_hash}")
    lines.append(f"- H_Sigma hash: {hs.h_sigma_hash}")
    lines.append(f"- BFS reachability: {hs.integration.bfs_reachable}/666")
    lines.append("")

    lines.append("## ROUTE GATE BOOK SUMMARY")
    lines.append("")
    for r in hs.route_families:
        open_count = len(hs.mindsweep.route_gate_book.get(r.number, []))
        lines.append(f"- R{r.number:02d} {r.name}: {open_count}/256 open")
    lines.append("")

    lines.append("## INTEGRATION CHAIN")
    lines.append("")
    lines.append("```")
    lines.append("Layer 1: canon_compiler.py         -> Quaternion, I_60, PHI")
    lines.append("Layer 2: sos_5d_expander.py         -> 63 units, 5D coordinates")
    lines.append("Layer 3: hologram_4d_compressor.py  -> 63 seeds, base-4 lattice")
    lines.append("Layer 4: z_plus_ae_plus_framework.py -> Z+, AE+, 60 dimensions")
    lines.append("Layer 5: z_plus_ae_plus_router.py    -> Intent routing engine")
    lines.append("Layer 6: time_crystal_108d.py        -> 36 shells, 666 nodes")
    lines.append("Layer 7: time_crystal_108d_integrator.py -> Full integration")
    lines.append("Layer 8: time_crystal_wheel_crown.py -> Wheel crown, canopy")
    lines.append("Layer 9: master_ledger_hologram.py   -> H_Sigma (THIS FILE)")
    lines.append("```")
    lines.append("")

    lines.append("## TRUTH STATE")
    lines.append("")
    lines.append("**SIGMA-STATE (TOTAL PHASE-LOCK)**")
    lines.append("")
    lines.append("The crystal is complete. Every cell has been swept.")
    lines.append(f"L = {hs.ae_plus.love_constant:.6f}")

    return "\n".join(lines)


# =====================================================================
# SECTION 13: MAIN PIPELINE
# =====================================================================

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    receipt_dir = os.path.join(script_dir, "00_RECEIPTS")
    os.makedirs(receipt_dir, exist_ok=True)

    print("=" * 72)
    print("MASTER LEDGER HOLOGRAM ENGINE -- Building H_Sigma")
    print("=" * 72)
    print()

    # ---- Step 1: Build upstream pipeline ----
    print("Step 1: Building all 8 upstream layers...")
    upstream = build_upstream_pipeline()
    seed = upstream["seed"]
    z_plus = upstream["z_plus"]
    ae_plus = upstream["ae_plus"]
    integration = upstream["integration"]
    print(f"  666 nodes, seed = {seed.seed_hash}")
    print(f"  Z+ = {z_plus.quaternion}")
    print(f"  AE+ phase-lock = {ae_plus.phase_lock_frequency:.2f} Hz")
    print(f"  L = {ae_plus.love_constant:.6f}")
    print(f"  BFS reachability: {integration.bfs_reachable}/666")
    print(f"  Metro lines: {len(integration.metro_lines)}")
    print(f"  Rails: {len(integration.rails)}")
    print(f"  Tunnels: {len(integration.tunnels)}")
    print(f"  Ledger records: {len(integration.ledger)}")
    print()

    # ---- Step 2: Build 19 Nexus Registry ----
    print("Step 2: Building 19 nexus rows...")
    nexus_rows = build_19_nexus_rows()
    print(f"  {len(nexus_rows)} nexus rows built")
    for n in nexus_rows[:5]:
        print(f"    #{n.number}: {n.short_name} (degree={n.degree})")
    print(f"    ... and {len(nexus_rows)-5} more")
    print()

    # ---- Step 3: Build 256 Timing Bytes ----
    print("Step 3: Generating 256-state timing byte lattice...")
    timing_bytes = build_256_timing_bytes()
    print(f"  {len(timing_bytes)} timing bytes in Z_4^4 lattice")
    print()

    # ---- Step 4: Infer Hidden Nexuses ----
    print("Step 4: Inferring hidden nexus candidates...")
    hidden_nexuses = infer_hidden_nexuses()
    for h in hidden_nexuses:
        print(f"  {h.code}: {h.name} (novelty={h.novelty_score:.2f})")
    print()

    # ---- Step 5: Build Route Families ----
    print("Step 5: Building 14 route families...")
    route_families = build_route_families()
    for r in route_families[:5]:
        print(f"  R{r.number:02d}: {r.name} ({r.route_type})")
    print(f"  ... and {len(route_families)-5} more")
    print()

    # ---- Step 6: Build H_Sigma ----
    print("Step 6: Assembling H_Sigma snapshot...")
    hs = build_h_sigma(upstream)
    print(f"  H_Sigma hash: {hs.h_sigma_hash}")
    print()

    # ---- Step 7: Compute Mindsweeper Matrix ----
    print("Step 7: Mindsweeper matrix (19 x 256 = 4864 cells)...")
    ms = hs.mindsweep
    print(f"  Total cells: {len(ms.cells)}")
    class_order = ["contradictory", "master-key", "hidden-pressure", "frontier",
                   "unstable", "seated", "promising", "degenerate"]
    for cls in class_order:
        cnt = ms.class_counts.get(cls, 0)
        pct = 100 * cnt / max(len(ms.cells), 1)
        bar = "#" * (cnt // 20)
        print(f"  {cls:18s}: {cnt:5d} ({pct:5.1f}%) {bar}")
    print()

    # ---- Step 8: Master-Key Orientations ----
    print("Step 8: Top 10 master-key orientations...")
    for rank, tb_val in enumerate(ms.master_key_orientations[:10], 1):
        tb = timing_bytes[tb_val]
        mk_count = sum(1 for c in ms.cells
                       if c.timing_byte == tb_val and c.classification == "master-key")
        print(f"  #{rank}: B={tb_val:3d} ({tb.label}) -> {mk_count} master-key nexuses")
    print()

    # ---- Step 9: Fixed-Point Stabilization ----
    print("Step 9: Fixed-point stabilization (HCRL-invariant cells)...")
    print(f"  Total fixed points: {len(ms.fixed_points)}")
    fp_by_nexus = Counter(fp.nexus_num for fp in ms.fixed_points)
    top_fp = sorted(fp_by_nexus.items(), key=lambda x: x[1], reverse=True)[:5]
    for nx_num, cnt in top_fp:
        nx_name = next((n.short_name for n in nexus_rows if n.number == nx_num), "?")
        print(f"    {nx_name}: {cnt} fixed points ({100*cnt/256:.1f}%)")
    print()

    # ---- Step 10: Route Gate Book ----
    print("Step 10: Route gate book...")
    for r in route_families:
        open_count = len(ms.route_gate_book.get(r.number, []))
        print(f"  R{r.number:02d} {r.name:20s}: {open_count:3d}/256 open")
    print()

    # ---- Step 11: Generate document ----
    print("Step 11: Generating 23_MASTER_LEDGER_HOLOGRAM.md...")
    doc = generate_master_document(hs)
    doc_path = os.path.join(script_dir, "23_MASTER_LEDGER_HOLOGRAM.md")
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc)
    doc_lines = doc.count("\n") + 1
    print(f"  Written: 23_MASTER_LEDGER_HOLOGRAM.md ({doc_lines} lines)")
    print()

    # ---- Step 12: Generate receipt ----
    print("Step 12: Generating receipt...")
    receipt = generate_receipt(hs)
    receipt_path = os.path.join(receipt_dir, "MASTER_LEDGER_HOLOGRAM_RECEIPT.md")
    with open(receipt_path, "w", encoding="utf-8") as f:
        f.write(receipt)
    print(f"  Written: 00_RECEIPTS/MASTER_LEDGER_HOLOGRAM_RECEIPT.md")
    print()

    # ---- Final Summary ----
    print("=" * 72)
    print("MASTER LEDGER HOLOGRAM ENGINE -- COMPLETE")
    print("=" * 72)
    print()
    print(f"  H_Sigma = (N, E, Z, A, L, T, B, D, W, Psi, M, R)")
    print(f"  N  = {len(hs.nexus_rows)} nexus rows")
    print(f"  E  = {len(hs.route_families)} route families")
    print(f"  Z  = {len(hs.z_chain)} Z-chain levels")
    print(f"  A  = {len(hs.aethers)} aether faces")
    print(f"  L  = {len(hs.ledger_records)} ledger records")
    print(f"  T  = {sum(t.estimated_count for t in hs.tunnel_summaries)} tunnels")
    print(f"  B  = {len(hs.timing_bytes)} timing bytes")
    print(f"  D  = {len(hs.dimensional_tower)} octave levels")
    print(f"  W  = {len(hs.wheels)} wheel families")
    print(f"  Psi = {len(SEFIROT)} Sefirot stages")
    print(f"  M  = {len(hs.metro_lines)} metro lines")
    print(f"  R  = {len(hs.rails)} rails")
    print()
    print(f"  Mindsweeper: 19 x 256 = 4864 cells")
    print(f"  Master-key cells: {ms.class_counts.get('master-key', 0)}")
    print(f"  Fixed points: {len(ms.fixed_points)}")
    print(f"  Hidden nexuses: {len(hs.hidden_nexuses)}")
    print()
    print(f"  Z+ self-knowledge: {z_plus.self_knowledge_index:.6f}")
    print(f"  AE+ phase-lock: {ae_plus.phase_lock_frequency:.2f} Hz")
    print(f"  L = {ae_plus.love_constant:.6f}")
    print(f"  H_Sigma hash: {hs.h_sigma_hash}")
    print()
    print("  The crystal is complete. Every cell has been swept.")
    print("  L = S x S_l remains conserved at Z+ across all collapses.")
    print()


if __name__ == "__main__":
    main()
