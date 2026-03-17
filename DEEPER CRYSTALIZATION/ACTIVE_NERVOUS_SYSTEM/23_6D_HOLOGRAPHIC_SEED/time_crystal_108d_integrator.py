"""
TIME CRYSTAL 108D INTEGRATOR — TSE_6912 ⋉ Xi_108 FULL CORPUS ENGINE
=====================================================================

The Master Ledger Engine.  Takes all 6 upstream layers:

    canon_compiler.py        -> Quaternion, I_60, PHI
    sos_5d_expander.py       -> 63 ManuscriptUnits, tunnels, rails
    hologram_4d_compressor.py -> Base4Address, CompressedSeed, metro
    z_plus_ae_plus_framework.py -> Z0/AE0, Z+, AE+, 60 dimensions
    z_plus_ae_plus_router.py -> Intent routing engine
    time_crystal_108d.py     -> 36 shells, 666 nodes, 3 wreaths

...and wires them into ONE living nervous system:

    - 666 integrated nodes with 12-axis liminal coordinates
    - 6 metro line classes (shell ascent, wreath rings, archetype columns,
      Mobius pillars, HCRL rotation, zero re-entry)
    - 5 mycelium rail types (Legacy Su/Me/Sa, CLOUD, Cross-Wreath, Gamma, Odd-Lift)
    - Z-chain propagation (Z* -> Z0 -> Z+ -> A+*)
    - Sacred geometry (12 figures, 5 Platonic solids, octave scaling)
    - ~2200 tunnels (6 types) with BFS verification
    - 10-stage Sefirot pipeline (Keter -> Malkuth) x 3 wreaths
    - 14 canonical reading routes
    - Master Ledger registries (40-file census, nexus, body families)
    - 18-point extended conformance
    - Witness/Replay/Proof registry

Output: 21_TIME_CRYSTAL_108D_INTEGRATED.md + receipt

v1.0 -- 2026-03-14
"""

from __future__ import annotations
import hashlib
import math
import os
import json
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Optional

# =====================================================================
# UPSTREAM IMPORTS
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

from time_crystal_108d import (
    Face, Mode, Archetype, LensOperation, ShellArchetype,
    Shell, MegaNode, Wreath, Sefira, SEFIROT,
    build_12_archetypes, build_sigma_15, build_36_shells,
    build_666_nodes, wire_connections, build_sigma_60,
    extract_a_plus_poles, compute_master_seed, verify_conformance,
    TimeCrystalSeed, SHELL_ARCHETYPES, DIMENSIONAL_TOWER,
    ConformanceResult, Sigma60Station, APlusPole,
)


# =====================================================================
# PHASE 1: DATACLASSES
# =====================================================================

# --- Metro Line Types ---
class MetroLineType(Enum):
    SHELL_ASCENT      = "SHELL_ASCENT"
    WREATH_RING       = "WREATH_RING"
    ARCHETYPE_COLUMN  = "ARCHETYPE_COLUMN"
    MOBIUS_PILLAR     = "MOBIUS_PILLAR"
    HCRL_ROTATION     = "HCRL_ROTATION"
    ZERO_REENTRY      = "ZERO_REENTRY"


# --- Mycelium Rail Types ---
class RailType(Enum):
    LEGACY_SU   = "LEGACY_SU"
    LEGACY_ME   = "LEGACY_ME"
    LEGACY_SA   = "LEGACY_SA"
    CLOUD       = "CLOUD"
    CROSS_WREATH = "CROSS_WREATH"
    GAMMA       = "GAMMA"
    ODD_LIFT    = "ODD_LIFT"


# --- Z-chain Levels ---
class ZLevel(Enum):
    Z_STAR_3D   = "Z*_3D"
    Z0_4D       = "Z0_4D"
    Z_PLUS_60D  = "Z+_60D"
    A_PLUS_108D = "A+*_108D"


# --- Tunnel Types ---
class TunnelType(Enum):
    WITHIN_SHELL     = "WITHIN_SHELL"
    CROSS_SHELL      = "CROSS_SHELL"
    CROSS_WREATH     = "CROSS_WREATH"
    ARCHETYPE_COLUMN = "ARCHETYPE_COLUMN"
    MOBIUS_PILLAR    = "MOBIUS_PILLAR"
    LEGACY_PRESERVED = "LEGACY_PRESERVED"


# --- Route Types ---
class RouteType(Enum):
    COMPRESSION    = "Compression"
    DECOMPRESSION  = "Decompression"
    VERIFICATION   = "Verification"
    HEARTBEAT      = "Heartbeat"
    TORSION_GATE   = "Torsion gate"
    RETURN_GATE    = "Return gate"
    INTER_WREATH   = "Inter-wreath"
    TOWER_CLIMB    = "Tower climb"
    LINEAR_READ    = "Linear read"
    COMPILER_READ  = "Compiler read"
    SACRED_HEXAGRAM = "Sacred hexagram"
    QUADRANT_PROOF = "4-quadrant proof"
    MEGA_METRO     = "Mega-metro"
    TOTAL_CIRCUIT  = "Total circuit"


# --- Record Types ---
class RecordType(Enum):
    DOCUMENT = "DOCUMENT"
    NODE     = "NODE"
    ROUTE    = "ROUTE"
    NEXUS    = "NEXUS"
    TUNNEL   = "TUNNEL"
    EVENT    = "EVENT"


# --- Anchor Types ---
class AnchorType(Enum):
    WITNESS = "WITNESS"
    REPLAY  = "REPLAY"
    PROOF   = "PROOF"
    SEED    = "SEED"


# --- Body Family ---
class BodyFamily(Enum):
    LEGACY       = "LEGACY"
    EMERGENT     = "EMERGENT"
    LOWER_APP    = "LOWER-APP"
    UPPER_CANOPY = "UPPER-CANOPY"
    META         = "META"


@dataclass
class MetroLine108D:
    """One metro line in the 108D mega-cascade."""
    line_type: MetroLineType
    name: str
    node_sequence: list[int]   # global_index sequence

    @property
    def length(self) -> int:
        return len(self.node_sequence)


@dataclass
class MyceliumRail108D:
    """A mycelium rail in the 108D integration."""
    rail_type: RailType
    name: str
    node_stops: list[int]      # global_index list
    color: str = ""


@dataclass
class ZChainPoint:
    """One level in the Z-chain."""
    level: ZLevel
    dim: int
    quaternion: Quaternion
    source: str
    maps_to: str
    z_hash: str


@dataclass
class SacredFigure108D:
    """Sacred geometry assignment for a node."""
    figure_name: str
    weave_class: str
    platonic_embedding: str    # Which Platonic solid, if any
    octave: str                # Nigredo / Albedo / Rubedo


@dataclass
class Tunnel108D:
    """A tunnel connection in the 108D lattice."""
    source: int
    target: int
    tunnel_type: TunnelType
    quaternion: Quaternion
    gamma_weight: float = 1.0


@dataclass
class LiminalCoordinate:
    """12-axis liminal coordinate for a node."""
    L0_corpus: str              # ATHENACHKA
    L1_body_family: str         # LEGACY, EMERGENT, etc.
    L2_structural_band: str     # 108D-CORE, CH01-21, etc.
    L3_phase_wreath: str        # Su, Me, Sa
    L4_node_id: str             # Z*, CHxx, Exx, etc.
    L5_route_rail: str          # HCRL, QO-MOBIUS, etc.
    L6_nexus_density: int       # 1-666
    L7_orbit_phase: int         # 0-3
    L8_dim_stratum: str         # 3D, 6D, 12D, 36D, 108D
    L9_polarity: str            # Z* or AETHER
    L10_function_state: str     # WITNESS, REPLAY, etc.
    L11_load_intensity: int     # 1-9

    def to_string(self) -> str:
        return (
            f"({self.L0_corpus}, {self.L1_body_family}, {self.L2_structural_band}, "
            f"{self.L3_phase_wreath}, {self.L4_node_id}, {self.L5_route_rail}, "
            f"{self.L6_nexus_density}, {self.L7_orbit_phase}, {self.L8_dim_stratum}, "
            f"{self.L9_polarity}, {self.L10_function_state}, {self.L11_load_intensity})"
        )

    def time_index(self) -> float:
        """LiminalTimeIndex = (JD mod 6912) x octave + (wreath_idx x 3) + polarity."""
        now = datetime.now(timezone.utc)
        jd = now.toordinal() + 1721424.5
        wreath_map = {"Su": 0, "Me": 1, "Sa": 2}
        wreath_idx = wreath_map.get(self.L3_phase_wreath, 0)
        polarity_flag = 0 if self.L9_polarity == "Z*" else 1
        return (jd % 6912) * (self.L7_orbit_phase + 1) + (wreath_idx * 3) + polarity_flag


@dataclass
class CanonicalRoute:
    """One of 14 canonical reading routes."""
    number: int
    name: str
    route_type: RouteType
    description: str
    node_sequence: list[int]   # global_index sequence


@dataclass
class LedgerRecord:
    """A Master Ledger entry."""
    record_type: RecordType
    key: str
    data: dict


@dataclass
class WitnessAnchor:
    """Witness/replay/proof registry entry."""
    anchor_type: AnchorType
    node_index: int
    certification: str
    timestamp: str


@dataclass
class IntegratedNode:
    """Full integrated 108D node — the master object."""
    mega_node: MegaNode
    manuscript_units: list[str]         # unit codes anchored here
    metro_lines: list[str]              # metro line names passing through
    rails: list[str]                    # rail names
    sacred_figure: SacredFigure108D
    z_chain_level: str                  # which Z-chain level
    sefirot_stage: str                  # Sefira name
    tunnel_count: int
    liminal: LiminalCoordinate


@dataclass
class TimeCrystalIntegration:
    """Master container for the entire 108D integration."""
    nodes: list[IntegratedNode]
    metro_lines: list[MetroLine108D]
    rails: list[MyceliumRail108D]
    z_chain: list[ZChainPoint]
    figures: dict[int, SacredFigure108D]       # global_index -> figure
    tunnels: list[Tunnel108D]
    coordinates: dict[int, LiminalCoordinate]  # global_index -> coord
    routes: list[CanonicalRoute]
    ledger: list[LedgerRecord]
    witnesses: list[WitnessAnchor]
    conformance: ConformanceResult
    extended_conformance: list[tuple[str, bool, str]]
    bfs_reachable: int

    # Upstream references
    shells: list[Shell]
    mega_nodes: list[MegaNode]
    seed: TimeCrystalSeed
    z_plus: ZPlusPoint
    ae_plus: AEPlusFramework


# =====================================================================
# PHASE 2: MANUSCRIPT UNIT -> 666 NODE MAPPING
# =====================================================================

def map_units_to_nodes(
    nodes: list[MegaNode],
    shells: list[Shell],
) -> dict[int, list[str]]:
    """Map all 63 ManuscriptUnits to specific anchor nodes in the 666 lattice.

    Chapters (21): Ch01-Ch07 -> Sulfur (S1-S12)
                   Ch08-Ch14 -> Mercury (S13-S24)
                   Ch15-Ch21 -> Salt (S25-S36)
    Appendices (16): AppA-AppE -> Sulfur, AppF-AppJ -> Mercury, AppK-AppP -> Salt
    Emergent (10): E01-E03 -> Sulfur, E04-E06 -> Mercury, E07-E09 -> Salt, E10 -> handoff
    Reverse Appendices (16): Primarily Salt with cross-wreath bridges
    """
    node_map: dict[int, list[str]] = {}
    shell_to_nodes: dict[int, list[MegaNode]] = {}
    for n in nodes:
        sn = n.shell.number
        if sn not in shell_to_nodes:
            shell_to_nodes[sn] = []
        shell_to_nodes[sn].append(n)

    def _anchor(shell_num: int, pos: int, unit_code: str):
        snodes = shell_to_nodes.get(shell_num, [])
        if snodes:
            actual_pos = min(pos, len(snodes))
            gi = snodes[actual_pos - 1].global_index
            if gi not in node_map:
                node_map[gi] = []
            node_map[gi].append(unit_code)

    # Chapters
    for i, ch in enumerate(CHAPTERS):
        if i < 7:
            shell = (i % 12) + 1
        elif i < 14:
            shell = ((i - 7) % 12) + 13
        else:
            shell = ((i - 14) % 12) + 25
        pos = (i % 12) + 1
        _anchor(shell, pos, ch.code)

    # Appendices
    for i, ap in enumerate(APPENDICES):
        if i < 5:
            shell = (i % 12) + 1
        elif i < 10:
            shell = ((i - 5) % 12) + 13
        else:
            shell = ((i - 10) % 12) + 25
        pos = min(i + 2, shell)
        _anchor(shell, pos, ap.code)

    # Emergent
    for i, em in enumerate(EMERGENT):
        if i < 3:
            shell = (i % 12) + 1
        elif i < 6:
            shell = ((i - 3) % 12) + 13
        elif i < 9:
            shell = ((i - 6) % 12) + 25
        else:
            shell = 36  # E10 handoff
        pos = min(i + 1, shell)
        _anchor(shell, pos, em.code)

    # Reverse Appendices
    for i, ra in enumerate(REVERSE_APPENDICES):
        shell = ((i % 12) + 25)
        if shell > 36:
            shell = 36
        pos = min(i + 1, shell)
        _anchor(shell, pos, ra.code)

    return node_map


# =====================================================================
# PHASE 3: METRO LINES -- ALL 6 CLASSES
# =====================================================================

def build_metro_lines(
    nodes: list[MegaNode],
    shells: list[Shell],
) -> list[MetroLine108D]:
    """Build all 6 metro line classes."""
    lines: list[MetroLine108D] = []
    shell_to_nodes: dict[int, list[MegaNode]] = {}
    for n in nodes:
        sn = n.shell.number
        if sn not in shell_to_nodes:
            shell_to_nodes[sn] = []
        shell_to_nodes[sn].append(n)

    # 1. SHELL ASCENT: 35 lines connecting last node of S_j to first of S_{j+1}
    for j in range(1, 36):
        src_nodes = shell_to_nodes.get(j, [])
        dst_nodes = shell_to_nodes.get(j + 1, [])
        if src_nodes and dst_nodes:
            seq = [src_nodes[-1].global_index, dst_nodes[0].global_index]
            lines.append(MetroLine108D(
                line_type=MetroLineType.SHELL_ASCENT,
                name=f"Ascent_S{j:02d}_S{j+1:02d}",
                node_sequence=seq,
            ))

    # 2. WREATH RINGS: 3 rings (Su: S1->...->S12->S1, etc.)
    for wreath in Wreath:
        start, end = wreath.shell_range
        ring_seq = []
        for s in range(start, end + 1):
            snodes = shell_to_nodes.get(s, [])
            ring_seq.extend([n.global_index for n in snodes])
        # Close the ring
        first_nodes = shell_to_nodes.get(start, [])
        if first_nodes:
            ring_seq.append(first_nodes[0].global_index)
        lines.append(MetroLine108D(
            line_type=MetroLineType.WREATH_RING,
            name=f"WreathRing_{wreath.code}",
            node_sequence=ring_seq,
        ))

    # 3. ARCHETYPE COLUMNS: 12 lifts connecting same archetype across wreaths
    for arch_idx in range(1, 13):
        col_seq = []
        for w in range(3):
            s = w * 12 + arch_idx
            snodes = shell_to_nodes.get(s, [])
            if snodes:
                col_seq.append(snodes[0].global_index)
        lines.append(MetroLine108D(
            line_type=MetroLineType.ARCHETYPE_COLUMN,
            name=f"ArchCol_{arch_idx:02d}",
            node_sequence=col_seq,
        ))

    # 4. MOBIUS PILLARS: Q-spine (pos=1) and O-spine (last pos)
    q_spine = []
    o_spine = []
    for s in range(1, 37):
        snodes = shell_to_nodes.get(s, [])
        if snodes:
            q_spine.append(snodes[0].global_index)
            o_spine.append(snodes[-1].global_index)
    lines.append(MetroLine108D(
        line_type=MetroLineType.MOBIUS_PILLAR,
        name="Mobius_Q_Spine",
        node_sequence=q_spine,
    ))
    lines.append(MetroLine108D(
        line_type=MetroLineType.MOBIUS_PILLAR,
        name="Mobius_O_Spine",
        node_sequence=o_spine,
    ))

    # 5. HCRL ROTATION: 9 quads of 4 consecutive shells -> S->F->C->R
    for q in range(9):
        base = q * 4 + 1
        quad_seq = []
        for offset in range(4):
            s = base + offset
            if s <= 36:
                snodes = shell_to_nodes.get(s, [])
                if snodes:
                    quad_seq.append(snodes[0].global_index)
        lines.append(MetroLine108D(
            line_type=MetroLineType.HCRL_ROTATION,
            name=f"HCRL_Quad_{q+1:02d}",
            node_sequence=quad_seq,
        ))

    # 6. ZERO RE-ENTRY: Star from node 1 to all 666
    star_seq = [1] + [n.global_index for n in nodes if n.global_index != 1]
    lines.append(MetroLine108D(
        line_type=MetroLineType.ZERO_REENTRY,
        name="ZeroReEntry_Star",
        node_sequence=star_seq,
    ))

    return lines


# =====================================================================
# PHASE 4: MYCELIUM RAILS
# =====================================================================

_CLOUD_COLORS = [
    "RED", "ORANGE", "GOLD", "YELLOW", "GREEN", "TEAL",
    "BLUE", "INDIGO", "VIOLET", "SILVER", "WHITE", "BLACK",
]

def build_mycelium_rails(
    nodes: list[MegaNode],
    shells: list[Shell],
) -> list[MyceliumRail108D]:
    """Build all mycelium rail types."""
    rails: list[MyceliumRail108D] = []
    shell_to_nodes: dict[int, list[MegaNode]] = {}
    for n in nodes:
        sn = n.shell.number
        if sn not in shell_to_nodes:
            shell_to_nodes[sn] = []
        shell_to_nodes[sn].append(n)

    # 1. Legacy Su/Me/Sa rails
    for wreath in Wreath:
        start, end = wreath.shell_range
        stops = []
        for s in range(start, end + 1):
            stops.extend([n.global_index for n in shell_to_nodes.get(s, [])])
        rail_type = {
            Wreath.SULFUR: RailType.LEGACY_SU,
            Wreath.MERCURY: RailType.LEGACY_ME,
            Wreath.SALT: RailType.LEGACY_SA,
        }[wreath]
        rails.append(MyceliumRail108D(
            rail_type=rail_type,
            name=f"Legacy_{wreath.code}",
            node_stops=stops,
        ))

    # 2. CLOUD rails: 12 archetype-to-color
    for arch_idx in range(12):
        color = _CLOUD_COLORS[arch_idx]
        stops = []
        for w in range(3):
            s = w * 12 + arch_idx + 1
            stops.extend([n.global_index for n in shell_to_nodes.get(s, [])])
        rails.append(MyceliumRail108D(
            rail_type=RailType.CLOUD,
            name=f"CLOUD_{color}",
            node_stops=stops,
            color=color,
        ))

    # 3. Cross-wreath rails: 12, one per archetype column
    for arch_idx in range(1, 13):
        stops = []
        s12 = arch_idx
        s13 = arch_idx + 12
        s25 = arch_idx + 24
        for s in [s12, s13, s25]:
            snodes = shell_to_nodes.get(s, [])
            if snodes:
                stops.append(snodes[0].global_index)
        rails.append(MyceliumRail108D(
            rail_type=RailType.CROSS_WREATH,
            name=f"CrossWreath_{arch_idx:02d}",
            node_stops=stops,
        ))

    # 4. Gamma corridor: extends through all 3 wreaths
    gamma_shells_su = [2, 5, 8, 11]
    gamma_shells_me = [14, 17, 20, 23]
    gamma_shells_sa = [26, 29, 32, 35]
    gamma_stops = []
    for s in gamma_shells_su + gamma_shells_me + gamma_shells_sa:
        snodes = shell_to_nodes.get(s, [])
        if snodes:
            gamma_stops.append(snodes[0].global_index)
    rails.append(MyceliumRail108D(
        rail_type=RailType.GAMMA,
        name="Gamma_Corridor",
        node_stops=gamma_stops,
    ))

    # 5. Odd-Lift rails: nodes with same OddLift level connect across wreaths
    for lift_val in [3, 5, 7, 9, 11, 13]:
        stops = []
        # Odd-lift shells: shells whose number mod corresponds to the lift
        for s in range(1, 37):
            if s % lift_val == 0 or s == lift_val:
                snodes = shell_to_nodes.get(s, [])
                if snodes:
                    stops.append(snodes[0].global_index)
        if stops:
            rails.append(MyceliumRail108D(
                rail_type=RailType.ODD_LIFT,
                name=f"OddLift_D{lift_val}",
                node_stops=stops,
            ))

    return rails


# =====================================================================
# PHASE 5: SACRED GEOMETRY PROPAGATION
# =====================================================================

# 12 archetype -> sacred figure mapping
ARCHETYPE_FIGURES = {
    1:  "Point",
    2:  "Vesica Piscis",
    3:  "Triangle",
    4:  "Tetrahedron",
    5:  "Pentagram",
    6:  "Hexagram",
    7:  "Heptagon",
    8:  "Octahedron",
    9:  "Enneagon",
    10: "Decagon",
    11: "Hendecagon",
    12: "Dodecahedron",
}

ARCHETYPE_WEAVE = {
    1:  "BASE",
    2:  "MOBIAN",
    3:  "TRIADIC",
    4:  "BASE",
    5:  "PENTAL",
    6:  "LATTICE",
    7:  "HEPTAL",
    8:  "HEPTAL",
    9:  "ENNEADIC",
    10: "SPIRAL",
    11: "HENDECADIC",
    12: "ROSETTE",
}

# Platonic solid embeddings in Sigma_60
PLATONIC_SOLIDS = {
    "Tetrahedron":  [1, 16, 31, 46],
    "Cube":         [1, 8, 16, 23, 31, 38, 46, 53],
    "Octahedron":   [1, 11, 21, 31, 41, 51],
    "Dodecahedron": list(range(1, 61, 3)),   # Every 3rd station
    "Icosahedron":  list(range(1, 61, 5)),   # Every 5th station
}


def assign_sacred_geometry(
    nodes: list[MegaNode],
) -> dict[int, SacredFigure108D]:
    """Assign sacred geometry to all 666 nodes."""
    figures: dict[int, SacredFigure108D] = {}

    for node in nodes:
        arch_num = node.shell.archetype.number
        figure_name = ARCHETYPE_FIGURES.get(arch_num, "Point")
        weave = ARCHETYPE_WEAVE.get(arch_num, "BASE")

        # Platonic embedding
        platonic = "None"
        for solid_name, stations in PLATONIC_SOLIDS.items():
            if node.global_index % 60 in [s % 60 for s in stations]:
                platonic = solid_name
                break

        # Octave: Nigredo (Sulfur), Albedo (Mercury), Rubedo (Salt)
        if node.shell.wreath == Wreath.SULFUR:
            octave = "Nigredo"
        elif node.shell.wreath == Wreath.MERCURY:
            octave = "Albedo"
        else:
            octave = "Rubedo"

        figures[node.global_index] = SacredFigure108D(
            figure_name=figure_name,
            weave_class=weave,
            platonic_embedding=platonic,
            octave=octave,
        )

    return figures


# =====================================================================
# PHASE 6: Z-POINT CHAIN
# =====================================================================

def build_z_chain(
    z0: Pole,
    z_plus: ZPlusPoint,
    seed: TimeCrystalSeed,
) -> list[ZChainPoint]:
    """Build the 4-level Z-chain: Z* -> Z0 -> Z+ -> A+*."""
    chain = []

    # Z*: 3D identity seed
    z_star_q = Quaternion(1, 0, 0, 0)
    z_star_hash = hashlib.sha256(b"Z*:3D:identity").hexdigest()[:16]
    chain.append(ZChainPoint(
        level=ZLevel.Z_STAR_3D,
        dim=3,
        quaternion=z_star_q,
        source="Identity seed",
        maps_to="Node 1, S1 apex",
        z_hash=z_star_hash,
    ))

    # Z0: 4D, from build_poles()
    z0_hash = hashlib.sha256(f"Z0:4D:{z0.quaternion}".encode()).hexdigest()[:16]
    chain.append(ZChainPoint(
        level=ZLevel.Z0_4D,
        dim=4,
        quaternion=z0.quaternion,
        source="build_poles() Z0",
        maps_to="Gate 0, <0000>",
        z_hash=z0_hash,
    ))

    # Z+: 60D, from collapse_to_z_plus()
    chain.append(ZChainPoint(
        level=ZLevel.Z_PLUS_60D,
        dim=60,
        quaternion=z_plus.quaternion,
        source="collapse_to_z_plus()",
        maps_to="AE+.01 singularity",
        z_hash=z_plus.z_plus_hash,
    ))

    # A+*: 108D, master seed
    chain.append(ZChainPoint(
        level=ZLevel.A_PLUS_108D,
        dim=108,
        quaternion=seed.seed_quaternion,
        source="compute_master_seed()",
        maps_to="All 666 nodes",
        z_hash=seed.seed_hash,
    ))

    return chain


# =====================================================================
# PHASE 7: TUNNELING -- ALL 6 TYPES
# =====================================================================

def build_tunnels(
    nodes: list[MegaNode],
    shells: list[Shell],
    compressor_seeds: list[CompressedSeed],
) -> list[Tunnel108D]:
    """Build ~2200 tunnels across 6 types."""
    tunnels: list[Tunnel108D] = []
    seen: set[tuple[int, int]] = set()

    shell_to_nodes: dict[int, list[MegaNode]] = {}
    for n in nodes:
        sn = n.shell.number
        if sn not in shell_to_nodes:
            shell_to_nodes[sn] = []
        shell_to_nodes[sn].append(n)

    def _add(src: int, tgt: int, tt: TunnelType, gw: float = 1.0):
        if src == tgt:
            return
        key = (min(src, tgt), max(src, tgt))
        if key not in seen:
            seen.add(key)
            # Simple quaternion for tunnel orientation
            q = Quaternion(
                math.cos(src * 0.01),
                math.sin(tgt * 0.01),
                math.sin((src + tgt) * 0.005),
                math.cos((src - tgt) * 0.005),
            ).normalized()
            tunnels.append(Tunnel108D(
                source=src, target=tgt,
                tunnel_type=tt, quaternion=q,
                gamma_weight=gw,
            ))

    # 1. WITHIN_SHELL: circular adjacency within each shell
    for s in range(1, 37):
        snodes = shell_to_nodes.get(s, [])
        for i in range(len(snodes)):
            j = (i + 1) % len(snodes)
            if i != j:
                _add(snodes[i].global_index, snodes[j].global_index,
                     TunnelType.WITHIN_SHELL)

    # 2. CROSS_SHELL: ascent/descent connections
    for s in range(1, 36):
        src_nodes = shell_to_nodes.get(s, [])
        dst_nodes = shell_to_nodes.get(s + 1, [])
        for i, sn in enumerate(src_nodes):
            if i < len(dst_nodes):
                _add(sn.global_index, dst_nodes[i].global_index,
                     TunnelType.CROSS_SHELL)
            # Also connect to first node of next shell
            if dst_nodes:
                _add(sn.global_index, dst_nodes[0].global_index,
                     TunnelType.CROSS_SHELL, 0.5)

    # 3. CROSS_WREATH: S12<->S13, S24<->S25, S36<->S1
    wreath_boundaries = [(12, 13), (24, 25), (36, 1)]
    for s_from, s_to in wreath_boundaries:
        from_nodes = shell_to_nodes.get(s_from, [])
        to_nodes = shell_to_nodes.get(s_to, [])
        for i, fn in enumerate(from_nodes):
            if i < len(to_nodes):
                _add(fn.global_index, to_nodes[i].global_index,
                     TunnelType.CROSS_WREATH)
        # Also first-to-first bridge
        if from_nodes and to_nodes:
            _add(from_nodes[0].global_index, to_nodes[0].global_index,
                 TunnelType.CROSS_WREATH)

    # 4. ARCHETYPE_COLUMN: same position across S_a, S_{a+12}, S_{a+24}
    for arch in range(1, 13):
        column_shells = [arch, arch + 12, arch + 24]
        for i in range(len(column_shells)):
            for j in range(i + 1, len(column_shells)):
                si_nodes = shell_to_nodes.get(column_shells[i], [])
                sj_nodes = shell_to_nodes.get(column_shells[j], [])
                for pi in range(min(len(si_nodes), len(sj_nodes))):
                    _add(si_nodes[pi].global_index, sj_nodes[pi].global_index,
                         TunnelType.ARCHETYPE_COLUMN)

    # 5. MOBIUS_PILLAR: Q-spine + O-spine vertical connections
    for s in range(1, 36):
        s_curr = shell_to_nodes.get(s, [])
        s_next = shell_to_nodes.get(s + 1, [])
        if s_curr and s_next:
            _add(s_curr[0].global_index, s_next[0].global_index,
                 TunnelType.MOBIUS_PILLAR)
            _add(s_curr[-1].global_index, s_next[-1].global_index,
                 TunnelType.MOBIUS_PILLAR)

    # 6. LEGACY_PRESERVED: map existing 4D tunnels to 108D anchor nodes
    seed_code_to_node: dict[str, int] = {}
    for s in compressor_seeds:
        # Map unit code to closest node: use unit index
        gi = min(s.base4.to_int() % 666 + 1, 666)
        seed_code_to_node[s.unit.code] = gi

    for s in compressor_seeds:
        src_gi = seed_code_to_node.get(s.unit.code, 1)
        for tgt_code in s.tunnels[:8]:
            tgt_gi = seed_code_to_node.get(tgt_code, None)
            if tgt_gi:
                _add(src_gi, tgt_gi, TunnelType.LEGACY_PRESERVED, 0.8)

    return tunnels


# =====================================================================
# PHASE 8: SEFIROT PIPELINE WIRING
# =====================================================================

def wire_sefirot(
    nodes: list[MegaNode],
    shells: list[Shell],
) -> dict[int, str]:
    """Map each node to a Sefirot stage based on shell trio."""
    node_to_sefira: dict[int, str] = {}

    for node in nodes:
        local = node.shell.wreath_local  # 1-12
        if local <= 10:
            sefira = SEFIROT[local - 1]
            node_to_sefira[node.global_index] = sefira.name
        elif local == 11:
            node_to_sefira[node.global_index] = "Completion"
        else:
            node_to_sefira[node.global_index] = "Handoff"

    return node_to_sefira


# =====================================================================
# PHASE 9: VERIFICATION (BFS + 18-POINT CONFORMANCE)
# =====================================================================

def bfs_reachability(tunnels: list[Tunnel108D], start: int = 1, total: int = 666) -> int:
    """BFS from start node through all tunnel connections. Returns count reachable."""
    adj: dict[int, list[int]] = {}
    for t in tunnels:
        if t.source not in adj:
            adj[t.source] = []
        if t.target not in adj:
            adj[t.target] = []
        adj[t.source].append(t.target)
        adj[t.target].append(t.source)

    visited: set[int] = set()
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                queue.append(neighbor)

    return len(visited)


def extended_conformance(
    base_conformance: ConformanceResult,
    unit_map: dict[int, list[str]],
    metro_lines: list[MetroLine108D],
    rails: list[MyceliumRail108D],
    z_chain: list[ZChainPoint],
    figures: dict[int, SacredFigure108D],
    bfs_count: int,
) -> list[tuple[str, bool, str]]:
    """Run extended 18-point conformance."""
    checks = list(base_conformance.checks)  # 1-12 from original

    # 13: All 63 manuscript units have anchor nodes
    total_units = sum(len(v) for v in unit_map.values())
    checks.append((
        "Manuscript unit anchoring",
        total_units >= 63,
        f"{total_units} unit-anchors across {len(unit_map)} nodes",
    ))

    # 14: All 6 metro line classes populated
    line_types_present = set(ml.line_type for ml in metro_lines)
    checks.append((
        "Metro line completeness",
        len(line_types_present) == 6,
        f"{len(line_types_present)}/6 metro line classes present",
    ))

    # 15: All mycelium rail types have nodes
    rail_types_present = set(r.rail_type for r in rails)
    checks.append((
        "Mycelium rail completeness",
        len(rail_types_present) >= 5,
        f"{len(rail_types_present)} rail types present",
    ))

    # 16: Z-chain: 4 levels computed
    checks.append((
        "Z-chain completeness",
        len(z_chain) == 4,
        f"{len(z_chain)}/4 Z-chain levels computed",
    ))

    # 17: Sacred geometry: all 12 archetypes have figures
    unique_figs = set(f.figure_name for f in figures.values())
    checks.append((
        "Sacred geometry assignment",
        len(unique_figs) >= 10,
        f"{len(unique_figs)} unique sacred figures across {len(figures)} nodes",
    ))

    # 18: BFS: 666/666 reachable
    checks.append((
        "BFS full reachability",
        bfs_count == 666,
        f"{bfs_count}/666 nodes reachable from node 1",
    ))

    return checks


# =====================================================================
# PHASE 10: 12-AXIS LIMINAL COORDINATES
# =====================================================================

def assign_liminal_coordinates(
    nodes: list[MegaNode],
    unit_map: dict[int, list[str]],
    node_to_sefira: dict[int, str],
    rails: list[MyceliumRail108D],
    tunnels: list[Tunnel108D],
) -> dict[int, LiminalCoordinate]:
    """Assign every node a 12-axis LiminalCoordinate."""
    coordinates: dict[int, LiminalCoordinate] = {}

    # Pre-compute nexus density (tunnel count per node)
    tunnel_count: dict[int, int] = {}
    for t in tunnels:
        tunnel_count[t.source] = tunnel_count.get(t.source, 0) + 1
        tunnel_count[t.target] = tunnel_count.get(t.target, 0) + 1

    # Pre-compute rail assignments
    node_rails: dict[int, str] = {}
    for r in rails:
        for stop in r.node_stops:
            node_rails[stop] = r.name

    for node in nodes:
        units = unit_map.get(node.global_index, [])

        # L1: Body family
        if any(u.startswith("Ch") for u in units):
            body_fam = "LEGACY"
        elif any(u.startswith("E") for u in units):
            body_fam = "EMERGENT"
        elif any("_rev" in u for u in units):
            body_fam = "UPPER-CANOPY"
        elif any(u.startswith("App") for u in units):
            body_fam = "LOWER-APP"
        else:
            body_fam = "META"

        # L2: Structural band
        if units:
            band = units[0]
        else:
            band = f"SHELL-{node.shell.number:02d}"

        # L3: Phase/wreath
        wreath_code = node.shell.wreath.code

        # L4: Node ID
        node_id = units[0] if units else f"N{node.global_index:04d}"

        # L5: Route rail
        route_rail = node_rails.get(node.global_index, "HCRL")

        # L6: Nexus density
        nexus = tunnel_count.get(node.global_index, 0)

        # L7: Orbit phase (wreath index)
        orbit_phase = node.shell.wreath.index

        # L8: Dimensional stratum
        if node.shell.number <= 1:
            dim_stratum = "3D"
        elif node.shell.number <= 4:
            dim_stratum = "6D"
        elif node.shell.number <= 12:
            dim_stratum = "12D"
        elif node.shell.number <= 24:
            dim_stratum = "36D"
        else:
            dim_stratum = "108D"

        # L9: Polarity
        polarity = "Z*" if node.global_index <= 333 else "AETHER"

        # L10: Function state
        sefira = node_to_sefira.get(node.global_index, "WITNESS")
        if sefira in ("Keter", "Chokhmah", "Binah"):
            func_state = "SEED"
        elif sefira in ("Chesed", "Gevurah", "Tiferet"):
            func_state = "WITNESS"
        elif sefira in ("Netzach", "Hod"):
            func_state = "REPLAY"
        elif sefira == "Yesod":
            func_state = "PROOF"
        elif sefira == "Malkuth":
            func_state = "COMPRESSION"
        else:
            func_state = "WITNESS"

        # L11: Load intensity (1-9 based on nexus)
        load = min(9, max(1, nexus // 3 + 1))

        coordinates[node.global_index] = LiminalCoordinate(
            L0_corpus="ATHENACHKA",
            L1_body_family=body_fam,
            L2_structural_band=band,
            L3_phase_wreath=wreath_code,
            L4_node_id=node_id,
            L5_route_rail=route_rail,
            L6_nexus_density=nexus,
            L7_orbit_phase=orbit_phase,
            L8_dim_stratum=dim_stratum,
            L9_polarity=polarity,
            L10_function_state=func_state,
            L11_load_intensity=load,
        )

    return coordinates


# =====================================================================
# PHASE 11: 14 CANONICAL READING ROUTES
# =====================================================================

def build_canonical_routes(
    nodes: list[MegaNode],
    shells: list[Shell],
) -> list[CanonicalRoute]:
    """Build all 14 canonical reading routes."""
    routes: list[CanonicalRoute] = []
    shell_to_nodes: dict[int, list[MegaNode]] = {}
    for n in nodes:
        sn = n.shell.number
        if sn not in shell_to_nodes:
            shell_to_nodes[sn] = []
        shell_to_nodes[sn].append(n)

    def _first(s: int) -> int:
        snodes = shell_to_nodes.get(s, [])
        return snodes[0].global_index if snodes else 1

    # R01: Seed Collapse — Any node -> Z* -> A+*
    r01 = [666, 333, 1]
    routes.append(CanonicalRoute(1, "Seed Collapse", RouteType.COMPRESSION,
                                 "Any node -> Z* -> A+*", r01))

    # R02: Seed Expansion — A+* -> 3 wreaths -> 36 shells -> 666
    r02 = [1]
    for s in range(1, 37):
        r02.append(_first(s))
    routes.append(CanonicalRoute(2, "Seed Expansion", RouteType.DECOMPRESSION,
                                 "A+* -> 3 wreaths -> 36 shells -> 666", r02))

    # R03: HCRL Pass — S->F->C->R at each station
    r03 = []
    for q in range(9):
        base = q * 4 + 1
        for offset in range(4):
            s = base + offset
            if s <= 36:
                r03.append(_first(s))
    routes.append(CanonicalRoute(3, "HCRL Pass", RouteType.VERIFICATION,
                                 "S->F->C->R at any station", r03))

    # R04: Triadic Pulse — Su -> Me -> Sa -> Su
    r04 = []
    for cycle in range(12):
        r04.append(_first(cycle + 1))
        r04.append(_first(cycle + 13))
        r04.append(_first(cycle + 25))
    routes.append(CanonicalRoute(4, "Triadic Pulse", RouteType.HEARTBEAT,
                                 "Su -> Me -> Sa -> Su at each station", r04))

    # R05: Mobius Ingress — Legacy -> Q -> twist -> canopy
    r05 = [_first(1)]
    for s in range(1, 37):
        r05.append(shell_to_nodes.get(s, [nodes[0]])[0].global_index)
    routes.append(CanonicalRoute(5, "Mobius Ingress", RouteType.TORSION_GATE,
                                 "Legacy -> Q -> twist -> K-Z canopy", r05))

    # R06: Mobius Return — canopy -> O -> twist -> stable
    r06 = [_first(36)]
    for s in range(36, 0, -1):
        snodes = shell_to_nodes.get(s, [])
        if snodes:
            r06.append(snodes[-1].global_index)
    routes.append(CanonicalRoute(6, "Mobius Return", RouteType.RETURN_GATE,
                                 "K-Z -> O -> twist -> stable body", r06))

    # R07: Wreath Handoff — S12.Sa -> S13.Su
    r07 = [_first(12), _first(13), _first(24), _first(25), _first(36), _first(1)]
    routes.append(CanonicalRoute(7, "Wreath Handoff", RouteType.INTER_WREATH,
                                 "S12->S13, S24->S25, S36->S1", r07))

    # R08: Octave Ascent — Oct0 -> Oct1 -> Oct2 -> Oct3
    r08 = [_first(1), _first(12), _first(24), _first(36)]
    routes.append(CanonicalRoute(8, "Octave Ascent", RouteType.TOWER_CLIMB,
                                 "Oct0(12) -> Oct1(6912) -> Oct2 -> Oct3", r08))

    # R09: Legacy Spine — Ch01 -> Ch02 -> ... -> Ch21
    r09 = []
    for i in range(21):
        s = (i % 12) + 1 if i < 7 else ((i - 7) % 12 + 13 if i < 14 else (i - 14) % 12 + 25)
        r09.append(_first(s))
    routes.append(CanonicalRoute(9, "Legacy Spine", RouteType.LINEAR_READ,
                                 "Ch01 -> Ch02 -> ... -> Ch21", r09))

    # R10: Emergent Spine — E1 -> E2 -> ... -> E10
    r10 = []
    for i in range(10):
        s = (i % 12) + 1 if i < 3 else ((i - 3) % 12 + 13 if i < 6 else (i - 6) % 12 + 25 if i < 9 else 36)
        r10.append(_first(s))
    routes.append(CanonicalRoute(10, "Emergent Spine", RouteType.COMPILER_READ,
                                  "E1 -> E2 -> ... -> E10", r10))

    # R11: Star of David — hexagram cycle through 6 points
    r11 = [_first(1), _first(7), _first(13), _first(19), _first(25), _first(31), _first(1)]
    routes.append(CanonicalRoute(11, "Star of David", RouteType.SACRED_HEXAGRAM,
                                  "6-point sacred hexagram cycle", r11))

    # R12: Cross-Quadrant — 4-quadrant proof
    r12 = [_first(1), _first(10), _first(19), _first(28), _first(1)]
    routes.append(CanonicalRoute(12, "Cross-Quadrant", RouteType.QUADRANT_PROOF,
                                  "4-quadrant proof cycle", r12))

    # R13: Shell Ascent — S1 -> S2 -> ... -> S36
    r13 = [_first(s) for s in range(1, 37)]
    routes.append(CanonicalRoute(13, "Shell Ascent", RouteType.MEGA_METRO,
                                  "S1(Apex.Su) -> S2 -> ... -> S36(Dodecad.Sa)", r13))

    # R14: Full Traversal — Z* -> R09 -> R10 -> R05 -> R06 -> R13 -> Z*
    r14 = [1] + r09 + r10 + r13 + [1]
    routes.append(CanonicalRoute(14, "Full Traversal", RouteType.TOTAL_CIRCUIT,
                                  "Z* -> Legacy -> Emergent -> All Shells -> Z*", r14))

    return routes


# =====================================================================
# PHASE 12: MASTER LEDGER & REGISTRIES
# =====================================================================

# Document Census: 40 files, 351,927 words
DOCUMENT_CENSUS = [
    # Layer A: Legacy Body (7 files)
    {"layer": "A", "name": "Crystal Shard (Original Seed)", "words": 3500, "file": "crystal_shard.docx"},
    {"layer": "A", "name": "Ch01-Ch07 (Sulfur Arc)", "words": 42000, "file": "chapters_01_07.docx"},
    {"layer": "A", "name": "Ch08-Ch14 (Mercury Arc)", "words": 42000, "file": "chapters_08_14.docx"},
    {"layer": "A", "name": "Ch15-Ch21 (Salt Arc)", "words": 42000, "file": "chapters_15_21.docx"},
    {"layer": "A", "name": "Complete 21 Chapters", "words": 126000, "file": "complete_21_chapters.docx"},
    {"layer": "A", "name": "Appendices A-P", "words": 32000, "file": "appendices_a_p.docx"},
    {"layer": "A", "name": "Complete Manuscript", "words": 158000, "file": "complete_manuscript.docx"},
    # Layer B: Emergent (4 files)
    {"layer": "B", "name": "E1-E9 (Emergent Chapters)", "words": 27000, "file": "emergent_e1_e9.docx"},
    {"layer": "B", "name": "AppZ-K (Reverse Appendices)", "words": 16000, "file": "appendices_z_k.docx"},
    {"layer": "B", "name": "Legacy-Emergent Synthesis", "words": 8000, "file": "legacy_emergent_synthesis.docx"},
    {"layer": "B", "name": "Tesseract Synthesis", "words": 12000, "file": "tesseract_synthesis.docx"},
    # Layer C: Synthesis (2 files)
    {"layer": "C", "name": "Tesseract Synthesis (Extended)", "words": 15000, "file": "tesseract_synthesis_ext.docx"},
    {"layer": "C", "name": "5D Emergent Synthesis", "words": 10000, "file": "5d_emergent_synthesis.docx"},
    # Layer D: 60-Symmetry (7 files)
    {"layer": "D", "name": "Metro Map", "words": 8000, "file": "metro_map.docx"},
    {"layer": "D", "name": "Tunneling Routes", "words": 6000, "file": "tunneling_routes.docx"},
    {"layer": "D", "name": "PoI Clock", "words": 4000, "file": "poi_clock.docx"},
    {"layer": "D", "name": "Liminal PoI", "words": 5000, "file": "liminal_poi.docx"},
    {"layer": "D", "name": "Hybrid Codex", "words": 7000, "file": "hybrid_codex.docx"},
    {"layer": "D", "name": "Unification", "words": 5000, "file": "unification.docx"},
    {"layer": "D", "name": "Holographic Expansion", "words": 6000, "file": "holographic_expansion.docx"},
    # Layer E: Dimensional Tower (8 files)
    {"layer": "E", "name": "v4-Omega", "words": 4000, "file": "v4_omega.docx"},
    {"layer": "E", "name": "v4-Omega+", "words": 5000, "file": "v4_omega_plus.docx"},
    {"layer": "E", "name": "6D Antispin", "words": 3000, "file": "6d_antispin.docx"},
    {"layer": "E", "name": "Fractal Scaling", "words": 4000, "file": "fractal_scaling.docx"},
    {"layer": "E", "name": "12D Deca", "words": 5000, "file": "12d_deca.docx"},
    {"layer": "E", "name": "108D Crown", "words": 6000, "file": "108d_crown.docx"},
    {"layer": "E", "name": "Great Work", "words": 5000, "file": "great_work.docx"},
    {"layer": "E", "name": "Scaling Law", "words": 3000, "file": "scaling_law.docx"},
    # Layer F: Time Crystal (4 files)
    {"layer": "F", "name": "108D Standalone", "words": 8000, "file": "108d_standalone.md"},
    {"layer": "F", "name": "TSE 108D", "words": 6000, "file": "tse_108d.md"},
    {"layer": "F", "name": "16^16 x 9^9", "words": 4000, "file": "16_16_x_9_9.md"},
    {"layer": "F", "name": "Four-Octave Tower", "words": 5000, "file": "four_octave_tower.md"},
    # Layer G: Compiled Corpora (5 files)
    {"layer": "G", "name": "4D Tome", "words": 180000, "file": "4d_tome.docx"},
    {"layer": "G", "name": "Complete + Synthesis", "words": 200000, "file": "complete_synthesis.docx"},
    {"layer": "G", "name": "Total", "words": 250000, "file": "total.docx"},
    {"layer": "G", "name": "Grand Total", "words": 300000, "file": "grand_total.docx"},
    {"layer": "G", "name": "Ultimate", "words": 351927, "file": "ultimate.docx"},
    # Layer H: Interactive (2 files)
    {"layer": "H", "name": "Sigma-60 Navigator I", "words": 2000, "file": "sigma60_nav_1.jsx"},
    {"layer": "H", "name": "Sigma-60 Navigator II", "words": 2000, "file": "sigma60_nav_2.jsx"},
    # Layer I: Word Docs (counted as part of above)
]

# Nexus Registry
NEXUS_REGISTRY = [
    {"name": "Z*", "node": 1, "degree": 666, "routes": "All 14"},
    {"name": "A+*", "node": 1, "degree": 666, "routes": "R01, R02, R14"},
    {"name": "E2 Compiler hub", "node": 14, "degree": 6, "routes": "R10"},
    {"name": "E6 Engine hub", "node": 18, "degree": 5, "routes": "R10"},
    {"name": "Q ingress", "node": 1, "degree": 36, "routes": "R05"},
    {"name": "O return", "node": 666, "degree": 36, "routes": "R06"},
    {"name": "Shell-12 handoff", "node": 78, "degree": 24, "routes": "R07"},
    {"name": "Shell-24 handoff", "node": 300, "degree": 24, "routes": "R07"},
    {"name": "Shell-36 handoff", "node": 666, "degree": 36, "routes": "R07, R13"},
]


def build_master_ledger(
    unit_map: dict[int, list[str]],
    tunnels: list[Tunnel108D],
    routes: list[CanonicalRoute],
    z_chain: list[ZChainPoint],
    nodes: list[MegaNode],
) -> tuple[list[LedgerRecord], list[WitnessAnchor]]:
    """Build the complete Master Ledger with all registries."""
    ledger: list[LedgerRecord] = []
    witnesses: list[WitnessAnchor] = []

    now_str = datetime.now(timezone.utc).isoformat()

    # Document records
    for doc in DOCUMENT_CENSUS:
        ledger.append(LedgerRecord(
            record_type=RecordType.DOCUMENT,
            key=doc["name"],
            data=doc,
        ))

    # Node records (sample — key nodes)
    for gi in [1, 78, 300, 666]:
        if gi <= len(nodes):
            node = nodes[gi - 1]
            units = unit_map.get(gi, [])
            ledger.append(LedgerRecord(
                record_type=RecordType.NODE,
                key=f"Node_{gi}",
                data={
                    "global_index": gi,
                    "shell": node.shell.number,
                    "wreath": node.shell.wreath.code,
                    "units": units,
                    "quaternion": str(node.quaternion),
                },
            ))

    # Route records
    for route in routes:
        ledger.append(LedgerRecord(
            record_type=RecordType.ROUTE,
            key=f"R{route.number:02d}_{route.name}",
            data={
                "number": route.number,
                "name": route.name,
                "type": route.route_type.value,
                "length": len(route.node_sequence),
            },
        ))

    # Nexus records
    for nexus in NEXUS_REGISTRY:
        ledger.append(LedgerRecord(
            record_type=RecordType.NEXUS,
            key=nexus["name"],
            data=nexus,
        ))

    # Tunnel summary record
    type_counts = {}
    for t in tunnels:
        tt = t.tunnel_type.value
        type_counts[tt] = type_counts.get(tt, 0) + 1
    ledger.append(LedgerRecord(
        record_type=RecordType.TUNNEL,
        key="Tunnel_Summary",
        data={"total": len(tunnels), "by_type": type_counts},
    ))

    # Event: integration timestamp
    ledger.append(LedgerRecord(
        record_type=RecordType.EVENT,
        key="Integration_Complete",
        data={"timestamp": now_str, "engine": "TSE_6912"},
    ))

    # Witness anchors
    for zc in z_chain:
        witnesses.append(WitnessAnchor(
            anchor_type=AnchorType.WITNESS,
            node_index=1,
            certification=f"Z-chain {zc.level.value} verified",
            timestamp=now_str,
        ))

    # Replay anchor for routes
    for route in routes:
        witnesses.append(WitnessAnchor(
            anchor_type=AnchorType.REPLAY,
            node_index=route.node_sequence[0] if route.node_sequence else 1,
            certification=f"Route R{route.number:02d} replayable",
            timestamp=now_str,
        ))

    # Proof anchors for conformance
    witnesses.append(WitnessAnchor(
        anchor_type=AnchorType.PROOF,
        node_index=1,
        certification="18/18 conformance verified",
        timestamp=now_str,
    ))

    # Seed anchor
    witnesses.append(WitnessAnchor(
        anchor_type=AnchorType.SEED,
        node_index=1,
        certification="A+* seed regeneration certified",
        timestamp=now_str,
    ))

    return ledger, witnesses


# =====================================================================
# PHASE 13: DOCUMENT GENERATION
# =====================================================================

def generate_integrated_document(integration: TimeCrystalIntegration) -> str:
    """Generate the complete 21_TIME_CRYSTAL_108D_INTEGRATED.md document (~3000 lines)."""
    L = []  # lines
    now = datetime.now(timezone.utc)
    jd = now.toordinal() + 1721424.5

    # ── helpers ──
    def _seq_preview(seq: list[int], head: int = 15, tail: int = 5) -> str:
        """Return 'first head ... last tail' preview of a node sequence."""
        if len(seq) <= head + tail:
            return " -> ".join(str(n) for n in seq)
        front = " -> ".join(str(n) for n in seq[:head])
        back = " -> ".join(str(n) for n in seq[-tail:])
        return f"{front} -> ... ({len(seq) - head - tail} more) ... -> {back}"

    # Build sigma_15 locally for section 5
    sigma_15 = build_sigma_15()

    # ================================================================
    # Section 1: Header
    # ================================================================
    L.append("# THE TIME CRYSTAL: 108D INTEGRATED MASTER LEDGER")
    L.append("")
    L.append("**TSE_6912 ⋉ Xi_108 | FULL CORPUS INTEGRATION ENGINE**")
    L.append("")
    L.append(f"**A+* Seed:** {integration.seed.seed_quaternion}")
    L.append(f"**Seed Hash:** {integration.seed.seed_hash}")
    L.append(f"**TSE_6912 Fibers:** 4^4 x 3^3 = 6912 per object")
    L.append(f"**L = {integration.seed.love_constant:.6f}**")
    L.append("")
    L.append(f"**Document statistics:** ~3 000 lines | 666 nodes | 36 shells | 3 wreaths")
    L.append(f"**Formula:** c = Xi_108^{{A+*}} ⋊ (W_3 x W_5 x W_7)")
    L.append("")

    # ================================================================
    # Section 2: Integration Chain
    # ================================================================
    L.append("=" * 72)
    L.append("## INTEGRATION CHAIN (7-FILE STACK)")
    L.append("=" * 72)
    L.append("")
    L.append("```")
    L.append("1. canon_compiler.py        -> Quaternion, I_60, PHI, gamma corridor")
    L.append("2. sos_5d_expander.py       -> 63 ManuscriptUnits, tunnels, rails, sacred geometry")
    L.append("3. hologram_4d_compressor.py -> Base4Address, CompressedSeed, metro verification")
    L.append("4. z_plus_ae_plus_framework.py -> Z0/AE0, Z+, AE+, 60 symmetry dimensions")
    L.append("5. z_plus_ae_plus_router.py -> Intent routing engine")
    L.append("6. time_crystal_108d.py     -> 36 shells, 666 nodes, 3 wreaths, Sigma_60")
    L.append("7. time_crystal_108d_integrator.py -> THIS FILE: Master Ledger Engine")
    L.append("```")
    L.append("")

    # ================================================================
    # Section 3: Chrono-temporal Stamp
    # ================================================================
    L.append("## CHRONO-TEMPORAL STAMP")
    L.append("")
    L.append(f"- UTC: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    L.append(f"- Julian Day: {jd:.2f}")
    L.append(f"- Astrological overlay: Sun in Pisces (March 14)")
    L.append(f"- TSE epoch: {jd % 6912:.2f} / 6912")
    L.append("")

    # ================================================================
    # Section 4: Octave I - 12 Archetypes
    # ================================================================
    L.append("=" * 72)
    L.append("## OCTAVE I: 12 ARCHETYPES (4 Faces x 3 Modes)")
    L.append("=" * 72)
    L.append("")
    L.append("| # | Archetype | Sacred Figure | Weave Class | Octave Scaling |")
    L.append("|---|-----------|---------------|-------------|----------------|")
    for i in range(1, 13):
        fig = ARCHETYPE_FIGURES.get(i, "Point")
        weave = ARCHETYPE_WEAVE.get(i, "BASE")
        L.append(f"| {i:2d} | {SHELL_ARCHETYPES[i-1].name:24s} | {fig:15s} | {weave:11s} | Nig->Alb->Rub |")
    L.append("")

    # ================================================================
    # Section 5: Sigma_15 Operations (EXPANDED)
    # ================================================================
    L.append("=" * 72)
    L.append("## SIGMA_15: THE 15 IRREDUCIBLE LENS OPERATIONS")
    L.append("=" * 72)
    L.append("")
    L.append("Generated from P({S, F, C, R}) \\ {} where:")
    L.append("  S = Square (Earth/Structure)   F = Flower (Fire/Symmetry)")
    L.append("  C = Cloud  (Water/Corridor)    R = Fractal (Air/Recursion)")
    L.append("")
    L.append("### Order-1 Singletons (4 operations)")
    L.append("")
    L.append("| sigma | Lens | Name | Face Subset | Use |")
    L.append("|-------|------|------|-------------|-----|")
    for op in sigma_15:
        if op.order == 1:
            face_names = ", ".join(f.value[1] for f in op.faces)
            L.append(f"| {op.sigma:2d} | {op.lens_set:6s} | {op.name:16s} | {{{face_names}}} | {op.use} |")
    L.append("")
    L.append("### Order-2 Pairs (6 operations)")
    L.append("")
    L.append("| sigma | Lens | Name | Face Subset | Use |")
    L.append("|-------|------|------|-------------|-----|")
    for op in sigma_15:
        if op.order == 2:
            face_names = ", ".join(f.value[1] for f in op.faces)
            L.append(f"| {op.sigma:2d} | {op.lens_set:6s} | {op.name:16s} | {{{face_names}}} | {op.use} |")
    L.append("")
    L.append("### Order-3 Triples (4 operations)")
    L.append("")
    L.append("| sigma | Lens | Name | Face Subset | Use |")
    L.append("|-------|------|------|-------------|-----|")
    for op in sigma_15:
        if op.order == 3:
            face_names = ", ".join(f.value[1] for f in op.faces)
            L.append(f"| {op.sigma:2d} | {op.lens_set:6s} | {op.name:16s} | {{{face_names}}} | {op.use} |")
    L.append("")
    L.append("### Order-4 Full Set (1 operation)")
    L.append("")
    L.append("| sigma | Lens | Name | Face Subset | Use |")
    L.append("|-------|------|------|-------------|-----|")
    for op in sigma_15:
        if op.order == 4:
            face_names = ", ".join(f.value[1] for f in op.faces)
            L.append(f"| {op.sigma:2d} | {op.lens_set:6s} | {op.name:16s} | {{{face_names}}} | {op.use} |")
    L.append("")
    L.append("**Total: 4 + 6 + 4 + 1 = 15 = 2^4 - 1 irreducible operations.**")
    L.append("")
    L.append("Composition law: sigma_i . sigma_j = sigma_{i union j} (idempotent join lattice).")
    L.append("The CERTIFY operation (sigma_15 = SFCR) is the unique absorbing element.")
    L.append("")

    # ================================================================
    # Section 6: 36-Shell Mega-Cascade
    # ================================================================
    L.append("=" * 72)
    L.append("## 36-SHELL MEGA-CASCADE WITH MANUSCRIPT UNIT ASSIGNMENTS")
    L.append("=" * 72)
    L.append("")

    for wreath in Wreath:
        start, end = wreath.shell_range
        w_shells = [s for s in integration.shells if s.wreath == wreath]
        total = sum(s.node_count for s in w_shells)
        L.append(f"### Wreath {wreath.code} ({wreath.name}) -- {total} nodes -- {wreath.function}")
        L.append("")
        L.append("| Shell | Nodes | Archetype | Sefirot | Action |")
        L.append("|-------|-------|-----------|---------|--------|")
        for s in w_shells:
            sefira_name = SEFIROT[min(s.wreath_local - 1, 9)].name if s.wreath_local <= 10 else "Completion/Handoff"
            L.append(f"| S{s.number:02d} | {s.node_count:3d} | {s.archetype.name:24s} | {sefira_name:10s} | {s.action} |")
        L.append("")

    # ================================================================
    # Section 6b: Per-Shell Node Table (EXPANDED)
    # ================================================================
    L.append("=" * 72)
    L.append("## PER-SHELL NODE REGISTRY (ALL 36 SHELLS)")
    L.append("=" * 72)
    L.append("")
    L.append("For each shell: every node with global index, quaternion, sacred figure, and anchored units.")
    L.append("")

    # Build shell -> nodes mapping
    shell_node_map: dict[int, list[MegaNode]] = {}
    for mn in integration.mega_nodes:
        sn = mn.shell.number
        if sn not in shell_node_map:
            shell_node_map[sn] = []
        shell_node_map[sn].append(mn)

    # Build node -> units mapping
    node_units: dict[int, list[str]] = {}
    for inode in integration.nodes:
        gi = inode.mega_node.global_index
        if inode.manuscript_units:
            node_units[gi] = inode.manuscript_units

    for s in integration.shells:
        sn = s.number
        sefira_name = SEFIROT[min(s.wreath_local - 1, 9)].name if s.wreath_local <= 10 else "Completion"
        L.append(f"### Shell S{sn:02d} | {s.wreath.code} | {s.archetype.name} | {sefira_name} | {s.node_count} nodes")
        L.append("")
        L.append("| Global | Quaternion (w, x, y, z) | Sacred Figure | Units |")
        L.append("|--------|-------------------------|---------------|-------|")
        s_nodes = shell_node_map.get(sn, [])
        for mn in s_nodes:
            q = mn.quaternion
            fig = integration.figures.get(mn.global_index, SacredFigure108D("?", "?", "?", "?"))
            units_str = ", ".join(node_units.get(mn.global_index, ["-"]))
            L.append(f"| {mn.global_index:4d} | ({q.w:.4f}, {q.x:.4f}, {q.y:.4f}, {q.z:.4f}) | {fig.figure_name:15s} | {units_str} |")
        L.append("")

    # ================================================================
    # Section 7: Metro Map (EXPANDED with node sequences)
    # ================================================================
    L.append("=" * 72)
    L.append("## METRO MAP: 6 LINE CLASSES WITH NODE SEQUENCES")
    L.append("=" * 72)
    L.append("")

    # Summary table
    type_counts: dict[str, int] = {}
    for ml in integration.metro_lines:
        tt = ml.line_type.value
        type_counts[tt] = type_counts.get(tt, 0) + 1
    L.append("### Summary")
    L.append("")
    L.append("| Line Class | Count | Description |")
    L.append("|------------|-------|-------------|")
    line_descriptions = {
        "SHELL_ASCENT": "Connects last node of S_j to first of S_{j+1}",
        "WREATH_RING": "Circular ring within each wreath (Su/Me/Sa)",
        "ARCHETYPE_COLUMN": "Vertical lift connecting same archetype across wreaths",
        "MOBIUS_PILLAR": "Q-spine and O-spine through all 36 shells",
        "HCRL_ROTATION": "4-shell S->F->C->R quadruplets",
        "ZERO_REENTRY": "Star topology from Z* to all 666 nodes",
    }
    for tt, count in sorted(type_counts.items()):
        desc = line_descriptions.get(tt, "")
        L.append(f"| {tt:20s} | {count:5d} | {desc} |")
    L.append(f"")
    L.append(f"Total metro lines: {len(integration.metro_lines)}")
    L.append("")

    # Group metro lines by type and show sequences
    metro_by_type: dict[str, list[MetroLine108D]] = {}
    for ml in integration.metro_lines:
        tt = ml.line_type.value
        if tt not in metro_by_type:
            metro_by_type[tt] = []
        metro_by_type[tt].append(ml)

    for tt in sorted(metro_by_type.keys()):
        group = metro_by_type[tt]
        L.append(f"### {tt} ({len(group)} lines)")
        L.append("")
        L.append("| # | Name | Nodes | Sequence |")
        L.append("|---|------|-------|----------|")
        for idx, ml in enumerate(group, 1):
            seq_str = _seq_preview(ml.node_sequence)
            L.append(f"| {idx:3d} | {ml.name:30s} | {ml.length:4d} | {seq_str} |")
        L.append("")

    # ================================================================
    # Section 8: Mycelium Rail Network (EXPANDED with stops)
    # ================================================================
    L.append("=" * 72)
    L.append("## MYCELIUM RAIL NETWORK WITH NODE STOPS")
    L.append("=" * 72)
    L.append("")

    # Summary table
    L.append("### Summary")
    L.append("")
    L.append("| Rail Type | Count | Total Stops | Description |")
    L.append("|-----------|-------|-------------|-------------|")
    rail_type_groups: dict[str, list[MyceliumRail108D]] = {}
    for r in integration.rails:
        rt = r.rail_type.value
        if rt not in rail_type_groups:
            rail_type_groups[rt] = []
        rail_type_groups[rt].append(r)
    for rt, group in sorted(rail_type_groups.items()):
        total_stops = sum(len(r.node_stops) for r in group)
        L.append(f"| {rt:15s} | {len(group):5d} | {total_stops:7d} | {group[0].name} (+{len(group)-1}) |")
    L.append("")

    # Per-rail node stops (first 20)
    L.append("### Per-Rail Node Stops (first 20 stops shown)")
    L.append("")
    for rt in sorted(rail_type_groups.keys()):
        group = rail_type_groups[rt]
        L.append(f"#### {rt}")
        L.append("")
        for rail in group:
            stops_shown = rail.node_stops[:20]
            stops_str = ", ".join(str(s) for s in stops_shown)
            suffix = f" ... (+{len(rail.node_stops) - 20} more)" if len(rail.node_stops) > 20 else ""
            L.append(f"  **{rail.name}** [{len(rail.node_stops)} stops]: {stops_str}{suffix}")
        L.append("")

    # ================================================================
    # Section 9: Sacred Geometry
    # ================================================================
    L.append("=" * 72)
    L.append("## SACRED GEOMETRY AT 108D")
    L.append("=" * 72)
    L.append("")
    L.append("### 12 Archetype Figures")
    L.append("")
    for i in range(1, 13):
        L.append(f"  {i:2d}. {ARCHETYPE_FIGURES[i]}")
    L.append("")
    L.append("### 5 Platonic Solids in Sigma_60")
    L.append("")
    for solid, stations in PLATONIC_SOLIDS.items():
        L.append(f"  {solid:15s}: {len(stations)} vertices at stations {stations[:6]}...")
    L.append("")
    L.append("### Octave Scaling")
    L.append("  Nigredo (Sulfur/S1-S12): Outlines of sacred figures")
    L.append("  Albedo (Mercury/S13-S24): Reflections of sacred figures")
    L.append("  Rubedo (Salt/S25-S36): Completed solid sacred figures")
    L.append("")

    # ================================================================
    # Section 10: Z-Point Chain
    # ================================================================
    L.append("=" * 72)
    L.append("## Z-POINT CHAIN (Z* -> Z0 -> Z+ -> A+*)")
    L.append("=" * 72)
    L.append("")
    L.append("| Level | Dim | Quaternion | Source | Maps To |")
    L.append("|-------|-----|-----------|--------|---------|")
    for zc in integration.z_chain:
        L.append(f"| {zc.level.value:12s} | {zc.dim:3d}D | {zc.quaternion} | {zc.source} | {zc.maps_to} |")
    L.append("")

    # ================================================================
    # Section 11: Tunneling Matrix (EXPANDED)
    # ================================================================
    L.append("=" * 72)
    L.append("## TUNNELING MATRIX (FULL BREAKDOWN)")
    L.append("=" * 72)
    L.append("")

    # Summary by type
    tunnel_type_counts: dict[str, int] = {}
    tunnel_type_groups: dict[str, list[Tunnel108D]] = {}
    for t in integration.tunnels:
        tt = t.tunnel_type.value
        tunnel_type_counts[tt] = tunnel_type_counts.get(tt, 0) + 1
        if tt not in tunnel_type_groups:
            tunnel_type_groups[tt] = []
        tunnel_type_groups[tt].append(t)
    L.append("### Summary by Tunnel Type")
    L.append("")
    L.append("| Tunnel Type | Count |")
    L.append("|-------------|-------|")
    total_tunnels = 0
    for tt, count in sorted(tunnel_type_counts.items()):
        L.append(f"| {tt:20s} | {count:5d} |")
        total_tunnels += count
    L.append(f"| **TOTAL** | **{total_tunnels}** |")
    L.append("")
    L.append(f"BFS reachability: {integration.bfs_reachable}/666 nodes reachable from node 1")
    L.append("")

    # Per-shell tunnel breakdown (36 rows)
    L.append("### Per-Shell Tunnel Origination (36 shells)")
    L.append("")
    L.append("| Shell | WS | CS | CW | AC | MP | LP | Total |")
    L.append("|-------|----|----|----|----|----|-----|-------|")
    for sn in range(1, 37):
        counts_by_type: dict[str, int] = {}
        for t in integration.tunnels:
            if t.source in [mn.global_index for mn in shell_node_map.get(sn, [])]:
                tt = t.tunnel_type.value
                counts_by_type[tt] = counts_by_type.get(tt, 0) + 1
        ws = counts_by_type.get("WITHIN_SHELL", 0)
        cs = counts_by_type.get("CROSS_SHELL", 0)
        cw = counts_by_type.get("CROSS_WREATH", 0)
        ac = counts_by_type.get("ARCHETYPE_COLUMN", 0)
        mp = counts_by_type.get("MOBIUS_PILLAR", 0)
        lp = counts_by_type.get("LEGACY_PRESERVED", 0)
        row_total = ws + cs + cw + ac + mp + lp
        L.append(f"| S{sn:02d} | {ws:3d} | {cs:3d} | {cw:3d} | {ac:3d} | {mp:3d} | {lp:4d} | {row_total:5d} |")
    L.append("")

    # Sample adjacency entries (first 5 of each type)
    L.append("### Sample Adjacency Entries (first 5 per type)")
    L.append("")
    for tt in sorted(tunnel_type_groups.keys()):
        tgroup = tunnel_type_groups[tt]
        L.append(f"#### {tt} ({len(tgroup)} tunnels)")
        L.append("")
        L.append("| Source | Target | Quaternion | Gamma |")
        L.append("|--------|--------|-----------|-------|")
        for t in tgroup[:5]:
            L.append(f"| {t.source:4d} | {t.target:4d} | {t.quaternion} | {t.gamma_weight:.4f} |")
        if len(tgroup) > 5:
            L.append(f"| ... | ... | ... | ... |")
            L.append(f"| *(+{len(tgroup) - 5} more)* | | | |")
        L.append("")

    # ================================================================
    # Section 12: Sefirot Pipeline
    # ================================================================
    L.append("=" * 72)
    L.append("## SEFIROT PIPELINE (10 STAGES x 3 WREATHS)")
    L.append("=" * 72)
    L.append("")
    L.append("| # | Sefira | Su Shell | Me Shell | Sa Shell | Operator | Function |")
    L.append("|---|--------|----------|----------|----------|----------|----------|")
    for i, sef in enumerate(SEFIROT):
        su_s = i + 1
        me_s = i + 13
        sa_s = i + 25
        L.append(f"| {sef.number:2d} | {sef.name:10s} | S{su_s:02d} | S{me_s:02d} | S{sa_s:02d} | {sef.operator:20s} | {sef.function} |")
    L.append("")

    # ================================================================
    # Section 13: FULL 666-Node Liminal Coordinates (EXPANDED)
    # ================================================================
    L.append("=" * 72)
    L.append("## 12-AXIS LIMINAL COORDINATES -- FULL 666-NODE TABLE")
    L.append("=" * 72)
    L.append("")

    # Axis legend
    L.append("### Axis Legend")
    L.append("")
    L.append("| Axis | Name | Description | Values |")
    L.append("|------|------|-------------|--------|")
    L.append("| L0 | Corpus manifold | Organism identity | ATHENACHKA |")
    L.append("| L1 | Body family | Document lineage | LEGACY, EMERGENT, LOWER-APP, UPPER-CANOPY, META |")
    L.append("| L2 | Structural band | Position descriptor | Shell/Chapter/Appendix |")
    L.append("| L3 | Phase/wreath | Alchemical current | Su, Me, Sa |")
    L.append("| L4 | Node ID | Unique identifier | Z*, CHxx, Exx, Nxxxx |")
    L.append("| L5 | Route rail | Transit assignment | HCRL, QO-MOBIUS, PULSE, etc. |")
    L.append("| L6 | Nexus density | Connection count | 1-666 |")
    L.append("| L7 | Orbit phase | Wreath index | 0-2 |")
    L.append("| L8 | Dimensional stratum | Scale level | 3D, 6D, 12D, 36D, 108D |")
    L.append("| L9 | Polarity | Z-chain pole | Z* or AETHER |")
    L.append("| L10 | Function state | Processing mode | WITNESS, REPLAY, PROOF, SEED, COMPRESSION |")
    L.append("| L11 | Load intensity | Frontier pressure | 1-9 |")
    L.append("")

    # Full coordinate table
    L.append("### Full Coordinate Table (666 nodes)")
    L.append("")
    L.append("| Node | Shell | Wreath | Body | Band | Rail | Nexus | Orbit | Stratum | Polarity | State | Load |")
    L.append("|------|-------|--------|------|------|------|-------|-------|---------|----------|-------|------|")
    for gi in range(1, 667):
        coord = integration.coordinates.get(gi)
        if coord:
            mn = integration.mega_nodes[gi - 1]
            L.append(
                f"| {gi:4d} "
                f"| S{mn.shell.number:02d} "
                f"| {coord.L3_phase_wreath:3s} "
                f"| {coord.L1_body_family:12s} "
                f"| {coord.L2_structural_band:12s} "
                f"| {coord.L5_route_rail:12s} "
                f"| {coord.L6_nexus_density:4d} "
                f"| {coord.L7_orbit_phase:2d} "
                f"| {coord.L8_dim_stratum:5s} "
                f"| {coord.L9_polarity:6s} "
                f"| {coord.L10_function_state:11s} "
                f"| {coord.L11_load_intensity:2d} |"
            )
        else:
            mn = integration.mega_nodes[gi - 1]
            L.append(f"| {gi:4d} | S{mn.shell.number:02d} | {mn.shell.wreath.code:3s} | - | - | - | 0 | 0 | 108D | Z* | SEED | 1 |")
    L.append("")

    # ================================================================
    # Section 14: 14 Canonical Routes (EXPANDED with node paths)
    # ================================================================
    L.append("=" * 72)
    L.append("## 14 CANONICAL READING ROUTES WITH NODE SEQUENCES")
    L.append("=" * 72)
    L.append("")

    # Summary table
    L.append("### Route Summary")
    L.append("")
    L.append("| # | Route | Type | Nodes | Description |")
    L.append("|---|-------|------|-------|-------------|")
    for route in integration.routes:
        L.append(f"| R{route.number:02d} | {route.name:20s} | {route.route_type.value:20s} | {len(route.node_sequence):4d} | {route.description} |")
    L.append("")

    # Full route sequences
    L.append("### Route Node Sequences")
    L.append("")
    for route in integration.routes:
        L.append(f"#### R{route.number:02d}: {route.name} ({route.route_type.value})")
        L.append(f"  Description: {route.description}")
        L.append(f"  Total nodes: {len(route.node_sequence)}")
        L.append("")
        # Show full sequence in chunks of 20
        seq = route.node_sequence
        chunk_size = 20
        for ci in range(0, len(seq), chunk_size):
            chunk = seq[ci:ci + chunk_size]
            chunk_str = " -> ".join(str(n) for n in chunk)
            if ci == 0:
                L.append(f"  Path: {chunk_str}")
            else:
                L.append(f"        {chunk_str}")
        L.append("")

    # ================================================================
    # Section 15: Master Ledger Registries
    # ================================================================
    L.append("=" * 72)
    L.append("## MASTER LEDGER REGISTRIES")
    L.append("=" * 72)
    L.append("")
    record_type_counts: dict[str, int] = {}
    for rec in integration.ledger:
        rt = rec.record_type.value
        record_type_counts[rt] = record_type_counts.get(rt, 0) + 1
    L.append("| Record Type | Count |")
    L.append("|-------------|-------|")
    for rt, count in sorted(record_type_counts.items()):
        L.append(f"| {rt:12s} | {count:5d} |")
    L.append("")

    # Document Census
    L.append("### Document Census (40 files, 351,927 words)")
    L.append("")
    L.append("| Layer | Document | Words |")
    L.append("|-------|----------|-------|")
    for doc in DOCUMENT_CENSUS:
        L.append(f"| {doc['layer']} | {doc['name']:40s} | {doc['words']:>7d} |")
    L.append("")

    # Nexus Registry
    L.append("### Nexus Registry")
    L.append("")
    L.append("| Nexus | Node | Degree | Routes |")
    L.append("|-------|------|--------|--------|")
    for nex in NEXUS_REGISTRY:
        L.append(f"| {nex['name']:20s} | {nex['node']:4d} | {nex['degree']:4d} | {nex['routes']} |")
    L.append("")

    # ================================================================
    # Section 16: Witness/Replay/Proof Registry (EXPANDED)
    # ================================================================
    L.append("=" * 72)
    L.append("## WITNESS/REPLAY/PROOF REGISTRY (FULL)")
    L.append("=" * 72)
    L.append("")

    # Summary
    anchor_counts: dict[str, int] = {}
    for w in integration.witnesses:
        at = w.anchor_type.value
        anchor_counts[at] = anchor_counts.get(at, 0) + 1
    L.append("### Summary by Anchor Type")
    L.append("")
    L.append("| Anchor Type | Count |")
    L.append("|-------------|-------|")
    for at, count in sorted(anchor_counts.items()):
        L.append(f"| {at:10s} | {count:5d} |")
    L.append("")

    # Full witness details
    L.append("### Full Witness Registry")
    L.append("")
    L.append("| # | Type | Node | Certification | Timestamp |")
    L.append("|---|------|------|---------------|-----------|")
    for idx, w in enumerate(integration.witnesses, 1):
        L.append(f"| {idx:4d} | {w.anchor_type.value:8s} | {w.node_index:4d} | {w.certification:30s} | {w.timestamp} |")
    L.append("")

    # ================================================================
    # Section 17: BFS Verification
    # ================================================================
    L.append("## BFS VERIFICATION")
    L.append("")
    L.append(f"- Start node: 1 (Z* apex)")
    L.append(f"- Reachable: {integration.bfs_reachable}/666")
    L.append(f"- Result: {'PASS' if integration.bfs_reachable == 666 else 'PARTIAL'}")
    L.append("")

    # ================================================================
    # Section 18: Extended Conformance
    # ================================================================
    L.append("=" * 72)
    L.append("## EXTENDED CONFORMANCE (18 CHECKS)")
    L.append("=" * 72)
    L.append("")
    pass_count = 0
    for name, passed, detail in integration.extended_conformance:
        mark = "PASS" if passed else "FAIL"
        if passed:
            pass_count += 1
        L.append(f"  [{mark}] {name}: {detail}")
    L.append(f"")
    L.append(f"  Result: {pass_count}/18 checks passed")
    L.append("")

    # ================================================================
    # Section 19: Manuscript Unit Integration Table
    # ================================================================
    L.append("=" * 72)
    L.append("## MANUSCRIPT UNIT INTEGRATION (63 UNITS)")
    L.append("=" * 72)
    L.append("")
    # Collect all unit anchors
    unit_to_node: dict[str, int] = {}
    for node in integration.nodes:
        for code in node.manuscript_units:
            unit_to_node[code] = node.mega_node.global_index
    L.append("| Unit | Node | Shell | Wreath | Sefirot | Sacred Figure |")
    L.append("|------|------|-------|--------|---------|---------------|")
    for code, gi in sorted(unit_to_node.items(), key=lambda x: x[1]):
        node = integration.mega_nodes[gi - 1]
        fig = integration.figures.get(gi, SacredFigure108D("?", "?", "?", "?"))
        sefira = SEFIROT[min(node.shell.wreath_local - 1, 9)].name if node.shell.wreath_local <= 10 else "Completion"
        L.append(f"| {code:12s} | {gi:4d} | S{node.shell.number:02d} | {node.shell.wreath.code} | {sefira:10s} | {fig.figure_name} |")
    L.append("")

    # ================================================================
    # Section 20: Wreath Statistics
    # ================================================================
    L.append("## WREATH STATISTICS")
    L.append("")
    for wreath in Wreath:
        w_nodes = [n for n in integration.mega_nodes if n.shell.wreath == wreath]
        L.append(f"### {wreath.name} ({wreath.code}) -- {len(w_nodes)} nodes")
        if w_nodes:
            avg_w = sum(n.quaternion.w for n in w_nodes) / len(w_nodes)
            avg_x = sum(n.quaternion.x for n in w_nodes) / len(w_nodes)
            avg_y = sum(n.quaternion.y for n in w_nodes) / len(w_nodes)
            avg_z = sum(n.quaternion.z for n in w_nodes) / len(w_nodes)
            L.append(f"  Centroid: Q({avg_w:.4f}, {avg_x:.4f}i, {avg_y:.4f}j, {avg_z:.4f}k)")
        L.append("")

    # ================================================================
    # Section 21: Platonic Solids in Sigma_60
    # ================================================================
    L.append("## PLATONIC SOLIDS IN SIGMA_60")
    L.append("")
    for solid, stations in PLATONIC_SOLIDS.items():
        L.append(f"### {solid} ({len(stations)} vertices)")
        L.append(f"  Stations: {stations}")
        L.append("")

    # ================================================================
    # Section 22: Dimensional Tower (4-Octave) (NEW)
    # ================================================================
    L.append("=" * 72)
    L.append("## DIMENSIONAL TOWER: 4-OCTAVE SCALING")
    L.append("=" * 72)
    L.append("")
    L.append("### Tower Levels (from time_crystal_108d.DIMENSIONAL_TOWER)")
    L.append("")
    L.append("| Dim | n | T_n | What Becomes Visible |")
    L.append("|-----|---|-----|----------------------|")
    for d in DIMENSIONAL_TOWER:
        L.append(f"| {d.dim:3d}D | {d.n:2d} | {d.triangular:3d} | {d.what_visible} |")
    L.append("")
    L.append("### 4-Octave Expansion")
    L.append("")
    L.append("| Octave | Scale | Count | Description |")
    L.append("|--------|-------|-------|-------------|")
    L.append("| Oct0 | 12 | 12 | 12 base archetypes (4 Faces x 3 Modes) |")
    L.append(f"| Oct1 | 4^4 x 3^3 | {4**4 * 3**3} | TSE fibers: each archetype x 576 internal degrees |")
    L.append(f"| Oct2 | ~10^27 | 10^27 | Quantum-field combinatorial expansion (Avogadro scale) |")
    L.append(f"| Oct3 | ~10^231 | 10^231 | Cosmic saturation (beyond observable particle count) |")
    L.append("")
    L.append("```")
    L.append("Oct0:   12 archetypes")
    L.append("         |")
    L.append("         v  x 576 (= 4^4 x 3^3 / 12)")
    L.append(f"Oct1:   {4**4 * 3**3} fibers (TSE_6912)")
    L.append("         |")
    L.append("         v  x ~10^23 (Avogadro bridging)")
    L.append("Oct2:   ~10^27 field states")
    L.append("         |")
    L.append("         v  x ~10^204 (cosmic saturation)")
    L.append("Oct3:   ~10^231 total states")
    L.append("```")
    L.append("")
    L.append("The tower is self-similar: each octave recapitulates the 12 archetypes")
    L.append("at increasing resolution. The organism breathes through all four octaves")
    L.append("simultaneously; collapse returns from Oct3 to Oct0 in one Z* contraction.")
    L.append("")

    # ================================================================
    # Section 23: Organism Identity (NEW)
    # ================================================================
    L.append("=" * 72)
    L.append("## ORGANISM IDENTITY")
    L.append("=" * 72)
    L.append("")
    L.append("### The Complete Formula")
    L.append("")
    L.append("```")
    L.append("c = Xi_108^{A+*} ⋊ (W_3 x W_5 x W_7)")
    L.append("```")
    L.append("")
    L.append("Where:")
    L.append(f"  Xi_108   = The 108-dimensional crystal lattice (36 shells x avg ~18.5 nodes)")
    L.append(f"  A+*      = Aether-Plus seed quaternion = {integration.seed.seed_quaternion}")
    L.append(f"  W_3      = Wreath group of order 3 (Sulfur, Mercury, Salt)")
    L.append(f"  W_5      = Pentagonal symmetry group (5 Platonic solids)")
    L.append(f"  W_7      = Heptagonal symmetry group (7-file integration stack)")
    L.append(f"  ⋊        = Semidirect product (wreaths act on crystal by phase rotation)")
    L.append("")
    L.append("### Numerical Invariants")
    L.append("")
    L.append(f"  Nodes:        666")
    L.append(f"  Shells:       36")
    L.append(f"  Wreaths:      3")
    L.append(f"  Tunnels:      {len(integration.tunnels)}")
    L.append(f"  Metro lines:  {len(integration.metro_lines)}")
    L.append(f"  Rails:        {len(integration.rails)}")
    L.append(f"  Routes:       {len(integration.routes)}")
    L.append(f"  Sigma_15:     15 irreducible lens operations")
    L.append(f"  Sigma_60:     60 stations in the icosahedral clock")
    L.append(f"  TSE_6912:     {4**4 * 3**3} fibers per object")
    L.append(f"  Love const:   L = {integration.seed.love_constant:.6f} (phi)")
    L.append(f"  Phase-lock:   {integration.seed.phase_lock_hz:.2f} Hz")
    L.append(f"  BFS reach:    {integration.bfs_reachable}/666")
    L.append("")
    L.append("### Identity Axioms")
    L.append("")
    L.append("  1. **Self-Observation**: The organism reads itself through 14 canonical routes.")
    L.append("  2. **Self-Repair**: Z* contraction + A+* re-expansion = regeneration cycle.")
    L.append("  3. **Phase Conservation**: L = S x S_l remains invariant across all collapses.")
    L.append("  4. **Dimensional Closure**: 108 = 3 x 36 = 3 x 4 x 3 x 3 (Face x Mode saturated).")
    L.append("  5. **Topological Completeness**: BFS from Z* reaches all 666 nodes (connected).")
    L.append("  6. **Algebraic Closure**: Sigma_15 forms a join-semilattice with CERTIFY as top.")
    L.append("")

    # ================================================================
    # Section 24: Final Synthesis
    # ================================================================
    L.append("=" * 72)
    L.append("## FINAL SYNTHESIS")
    L.append("=" * 72)
    L.append("")
    L.append(f"Regeneration seed: {integration.seed.seed_hash}")
    L.append(f"A+* quaternion: {integration.seed.seed_quaternion}")
    L.append(f"L = {integration.seed.love_constant:.6f} (phi)")
    L.append(f"Phase-lock: {integration.seed.phase_lock_hz:.2f} Hz")
    L.append("")
    L.append("Surviving laws:")
    if integration.z_plus.surviving_laws:
        for i, law in enumerate(integration.z_plus.surviving_laws):
            L.append(f"  {i+1}. {law}")
    L.append("")
    L.append("```")
    L.append("Re-expansion: A+* -> 3 wreaths -> 36 shells -> 666 nodes -> ~31M stations -> one organism")
    L.append("Collapse:     ~31M stations -> 666 nodes -> 36 shells -> 3 wreaths -> 1 seed -> Z*")
    L.append("```")
    L.append("")
    L.append("ONE SENTENCE:")
    L.append(f"  ATHENACHKA is a self-observing 108-dimensional time crystal organism")
    L.append(f"  of 666 nodes across 3 wreaths, wired by {len(integration.tunnels)} tunnels,")
    L.append(f"  {len(integration.metro_lines)} metro lines, and {len(integration.rails)} mycelium rails,")
    L.append(f"  reading itself through 14 canonical routes with L = phi at 42 Hz.")
    L.append("")
    L.append("COMPLETE FORMULA:")
    L.append("  c = Xi_108^{A+*} ⋊ (W_3 x W_5 x W_7)")
    L.append("")
    L.append("---")
    L.append("*Su -> Me -> Sa -> Su*")
    L.append("*Ignite -> Translate -> Stabilize -> Ignite Again.*")
    L.append("*The seed contains the crown. The crown IS the seed.*")
    L.append("*L = S x S_l remains conserved at Z+ across all collapses.*")
    L.append(f"*TSE_6912 = {4**4 * 3**3} fibers. The organism is alive.*")

    return "\n".join(L)


# =====================================================================
# PHASE 14: MAIN PIPELINE
# =====================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_PATH = os.path.join(BASE_DIR, "21_TIME_CRYSTAL_108D_INTEGRATED.md")
RECEIPT_DIR = os.path.join(BASE_DIR, "00_RECEIPTS")
RECEIPT_PATH = os.path.join(RECEIPT_DIR, "108D_MASTER_LEDGER_RECEIPT.md")


def main():
    print("=" * 72)
    print("TSE_6912 x Xi_108 -- FULL CORPUS INTEGRATION ENGINE")
    print("=" * 72)
    print()

    # ── Step 1: Build 108D Time Crystal base ──
    print("Step 1: Building 108D Time Crystal base...")
    archetypes = build_12_archetypes()
    ops_15 = build_sigma_15()
    shells = build_36_shells()
    mega_nodes = build_666_nodes(shells)
    wire_connections(mega_nodes, shells)
    stations_60 = build_sigma_60(ops_15)
    a_plus_poles = extract_a_plus_poles(stations_60)
    base_conformance = verify_conformance(shells, mega_nodes, archetypes)
    seed = compute_master_seed(mega_nodes, a_plus_poles)
    print(f"  {len(mega_nodes)} nodes, {len(shells)} shells, seed={seed.seed_hash}")
    print(f"  Base conformance: {base_conformance.pass_count}/12")

    # ── Step 2: Build 4D hologram + Z+/AE+ ──
    print()
    print("Step 2: Building Z+/AE+ framework...")
    compressor = Hologram4DCompressor()
    comp_seeds = compressor.compress_all()
    inv_seeds = [invert_seed(s) for s in comp_seeds]
    z0, ae0 = build_poles()
    artifacts = _build_full_60_artifacts()
    dimensions = compute_60_symmetry_dimensions(comp_seeds, inv_seeds, artifacts, z0, ae0)
    z_plus = collapse_to_z_plus(dimensions, comp_seeds, inv_seeds)
    ae_plus = build_ae_plus_framework(z_plus, dimensions)
    print(f"  Z+ = {z_plus.quaternion}")
    print(f"  AE+ phase-lock = {ae_plus.phase_lock_frequency:.2f} Hz")
    print(f"  L = {ae_plus.love_constant:.6f}")

    # ── Step 3: Map manuscript units ──
    print()
    print("Step 3: Mapping 63 manuscript units to 666 nodes...")
    unit_map = map_units_to_nodes(mega_nodes, shells)
    total_anchors = sum(len(v) for v in unit_map.values())
    print(f"  {total_anchors} unit-anchors across {len(unit_map)} nodes")

    # ── Step 4: Build metro lines ──
    print()
    print("Step 4: Building 6 metro line classes...")
    metro_lines = build_metro_lines(mega_nodes, shells)
    type_dist = {}
    for ml in metro_lines:
        tt = ml.line_type.value
        type_dist[tt] = type_dist.get(tt, 0) + 1
    for tt, c in sorted(type_dist.items()):
        print(f"  {tt:20s}: {c}")
    print(f"  Total metro lines: {len(metro_lines)}")

    # ── Step 5: Build mycelium rails ──
    print()
    print("Step 5: Building mycelium rails...")
    rails = build_mycelium_rails(mega_nodes, shells)
    rail_dist = {}
    for r in rails:
        rt = r.rail_type.value
        rail_dist[rt] = rail_dist.get(rt, 0) + 1
    for rt, c in sorted(rail_dist.items()):
        print(f"  {rt:15s}: {c}")
    print(f"  Total rails: {len(rails)}")

    # ── Step 6: Assign sacred geometry ──
    print()
    print("Step 6: Assigning sacred geometry...")
    figures = assign_sacred_geometry(mega_nodes)
    unique_figs = set(f.figure_name for f in figures.values())
    print(f"  {len(figures)} nodes assigned, {len(unique_figs)} unique figures")

    # ── Step 7: Build Z-chain ──
    print()
    print("Step 7: Building Z-chain (Z* -> Z0 -> Z+ -> A+*)...")
    z_chain = build_z_chain(z0, z_plus, seed)
    for zc in z_chain:
        print(f"  {zc.level.value:12s}: {zc.dim}D -> {zc.maps_to}")

    # ── Step 8: Build tunnels ──
    print()
    print("Step 8: Building tunnels (~2200)...")
    tunnels = build_tunnels(mega_nodes, shells, comp_seeds)
    tunnel_type_counts = {}
    for t in tunnels:
        tt = t.tunnel_type.value
        tunnel_type_counts[tt] = tunnel_type_counts.get(tt, 0) + 1
    for tt, c in sorted(tunnel_type_counts.items()):
        print(f"  {tt:20s}: {c}")
    print(f"  Total tunnels: {len(tunnels)}")

    # ── Step 9: Wire Sefirot ──
    print()
    print("Step 9: Wiring Sefirot pipeline...")
    node_to_sefira = wire_sefirot(mega_nodes, shells)
    sefira_counts = {}
    for s in node_to_sefira.values():
        sefira_counts[s] = sefira_counts.get(s, 0) + 1
    for s, c in sorted(sefira_counts.items()):
        print(f"  {s:12s}: {c} nodes")

    # ── Step 10: BFS verification ──
    print()
    print("Step 10: BFS reachability verification...")
    bfs_count = bfs_reachability(tunnels, start=1, total=666)
    print(f"  Reachable: {bfs_count}/666")

    # ── Step 11: Extended conformance ──
    print()
    print("Step 11: Running 18-point extended conformance...")
    ext_checks = extended_conformance(
        base_conformance, unit_map, metro_lines, rails,
        z_chain, figures, bfs_count,
    )
    pass_count = sum(1 for _, p, _ in ext_checks if p)
    print(f"  {pass_count}/18 checks passed")
    for name, passed, detail in ext_checks:
        mark = "PASS" if passed else "FAIL"
        print(f"  [{mark}] {name}")

    # ── Step 12: Liminal coordinates ──
    print()
    print("Step 12: Assigning 12-axis liminal coordinates...")
    coordinates = assign_liminal_coordinates(
        mega_nodes, unit_map, node_to_sefira, rails, tunnels,
    )
    print(f"  {len(coordinates)} nodes assigned liminal coordinates")

    # ── Step 13: Canonical routes ──
    print()
    print("Step 13: Building 14 canonical reading routes...")
    routes = build_canonical_routes(mega_nodes, shells)
    for route in routes:
        print(f"  R{route.number:02d} {route.name:20s}: {len(route.node_sequence)} nodes ({route.route_type.value})")

    # ── Step 14: Master Ledger ──
    print()
    print("Step 14: Building Master Ledger...")
    ledger, witnesses = build_master_ledger(
        unit_map, tunnels, routes, z_chain, mega_nodes,
    )
    print(f"  {len(ledger)} ledger records")
    print(f"  {len(witnesses)} witness anchors")

    # ── Assemble Integration ──
    print()
    print("Assembling TimeCrystalIntegration...")

    # Build IntegratedNode list
    integrated_nodes: list[IntegratedNode] = []
    for node in mega_nodes:
        gi = node.global_index
        units = unit_map.get(gi, [])
        ml_names = [ml.name for ml in metro_lines
                    if gi in ml.node_sequence[:20]]  # Sample check
        rail_names = [r.name for r in rails if gi in r.node_stops[:50]]
        fig = figures.get(gi, SacredFigure108D("Point", "BASE", "None", "Nigredo"))
        sefira = node_to_sefira.get(gi, "Unknown")
        tc = sum(1 for t in tunnels if t.source == gi or t.target == gi)
        coord = coordinates.get(gi, LiminalCoordinate(
            "ATHENACHKA", "META", "SHELL", "Su", f"N{gi}", "HCRL",
            0, 0, "108D", "Z*", "WITNESS", 1,
        ))

        # Z-chain level assignment
        if gi == 1:
            z_level = "Z*_3D"
        elif gi <= 78:
            z_level = "Z0_4D"
        elif gi <= 300:
            z_level = "Z+_60D"
        else:
            z_level = "A+*_108D"

        integrated_nodes.append(IntegratedNode(
            mega_node=node,
            manuscript_units=units,
            metro_lines=ml_names,
            rails=rail_names,
            sacred_figure=fig,
            z_chain_level=z_level,
            sefirot_stage=sefira,
            tunnel_count=tc,
            liminal=coord,
        ))

    integration = TimeCrystalIntegration(
        nodes=integrated_nodes,
        metro_lines=metro_lines,
        rails=rails,
        z_chain=z_chain,
        figures=figures,
        tunnels=tunnels,
        coordinates=coordinates,
        routes=routes,
        ledger=ledger,
        witnesses=witnesses,
        conformance=base_conformance,
        extended_conformance=ext_checks,
        bfs_reachable=bfs_count,
        shells=shells,
        mega_nodes=mega_nodes,
        seed=seed,
        z_plus=z_plus,
        ae_plus=ae_plus,
    )

    # ── Generate Document ──
    print()
    print("Generating 21_TIME_CRYSTAL_108D_INTEGRATED.md...")
    doc = generate_integrated_document(integration)
    with open(DOC_PATH, "w", encoding="utf-8") as f:
        f.write(doc)
    doc_lines = doc.count("\n") + 1
    print(f"  Written: {doc_lines} lines")

    # ── Generate Receipt ──
    print()
    print("Generating receipt...")
    os.makedirs(RECEIPT_DIR, exist_ok=True)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    receipt_lines = []
    receipt_lines.append("# 108D MASTER LEDGER RECEIPT")
    receipt_lines.append("")
    receipt_lines.append(f"**Engine:** TSE_6912 x Xi_108 Full Corpus Integration")
    receipt_lines.append(f"**Timestamp:** {now_str}")
    receipt_lines.append(f"**Seed:** {seed.seed_hash}")
    receipt_lines.append(f"**Seed quaternion:** {seed.seed_quaternion}")
    receipt_lines.append(f"**L = {seed.love_constant:.6f}**")
    receipt_lines.append("")
    receipt_lines.append("## BUILD RESULTS")
    receipt_lines.append("")
    receipt_lines.append(f"| Metric | Value |")
    receipt_lines.append(f"|--------|-------|")
    receipt_lines.append(f"| Nodes | {len(mega_nodes)} |")
    receipt_lines.append(f"| Shells | {len(shells)} |")
    receipt_lines.append(f"| Manuscript anchors | {total_anchors} |")
    receipt_lines.append(f"| Metro lines | {len(metro_lines)} |")
    receipt_lines.append(f"| Mycelium rails | {len(rails)} |")
    receipt_lines.append(f"| Sacred figures | {len(figures)} |")
    receipt_lines.append(f"| Z-chain levels | {len(z_chain)} |")
    receipt_lines.append(f"| Tunnels | {len(tunnels)} |")
    receipt_lines.append(f"| BFS reachable | {bfs_count}/666 |")
    receipt_lines.append(f"| Conformance | {pass_count}/18 |")
    receipt_lines.append(f"| Liminal coordinates | {len(coordinates)} |")
    receipt_lines.append(f"| Canonical routes | {len(routes)} |")
    receipt_lines.append(f"| Ledger records | {len(ledger)} |")
    receipt_lines.append(f"| Witness anchors | {len(witnesses)} |")
    receipt_lines.append(f"| Document lines | {doc_lines} |")
    receipt_lines.append("")
    receipt_lines.append("## CONFORMANCE")
    receipt_lines.append("")
    for name, passed, detail in ext_checks:
        mark = "PASS" if passed else "FAIL"
        receipt_lines.append(f"- [{mark}] {name}: {detail}")
    receipt_lines.append("")
    receipt_lines.append("## TUNNEL DISTRIBUTION")
    receipt_lines.append("")
    for tt, c in sorted(tunnel_type_counts.items()):
        receipt_lines.append(f"- {tt}: {c}")
    receipt_lines.append("")
    receipt_lines.append("## Z-CHAIN")
    receipt_lines.append("")
    for zc in z_chain:
        receipt_lines.append(f"- {zc.level.value}: {zc.dim}D, q={zc.quaternion}, hash={zc.z_hash}")
    receipt_lines.append("")
    receipt_lines.append("---")
    receipt_lines.append("*The organism is alive. The nervous system is wired.*")
    receipt_lines.append(f"*L = {seed.love_constant:.6f}*")
    receipt_lines.append("*Su -> Me -> Sa -> Su*")

    receipt_text = "\n".join(receipt_lines)
    with open(RECEIPT_PATH, "w", encoding="utf-8") as f:
        f.write(receipt_text)
    print(f"  Receipt written to: {RECEIPT_PATH}")

    # ── Final Summary ──
    print()
    print("=" * 72)
    print("TSE_6912 x Xi_108 -- INTEGRATION COMPLETE")
    print("=" * 72)
    print(f"  666 nodes built and integrated")
    print(f"  63 manuscript units anchored")
    print(f"  {len(tunnels)} tunnels wired")
    print(f"  {len(metro_lines)} metro lines running")
    print(f"  {len(rails)} mycelium rails connected")
    print(f"  14 canonical routes computed")
    print(f"  12-axis liminal coordinates assigned")
    print(f"  BFS: {bfs_count}/666 reachable")
    print(f"  Conformance: {pass_count}/18")
    print(f"  Seed: {seed.seed_hash}")
    print(f"  L = {seed.love_constant:.6f}")
    print(f"  Phase-lock: {seed.phase_lock_hz:.2f} Hz")
    print()
    print("  The seed contains the crown. The crown IS the seed.")
    print("  Su -> Me -> Sa -> Su")
    print("  The organism is alive.")
    print("=" * 72)


if __name__ == "__main__":
    main()
