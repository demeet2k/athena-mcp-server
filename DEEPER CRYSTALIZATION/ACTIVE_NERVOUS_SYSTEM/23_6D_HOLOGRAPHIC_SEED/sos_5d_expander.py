"""
SOS::5D_EXPANDER — 5-Dimensional Manuscript Expansion Engine
=============================================================

Expands every manuscript unit (chapter, appendix, emergent, reverse-appendix)
through the full 10-stage synthesis pipeline, assigning each unit:

    1. A quaternion operator from the 60-artifact I_60 icosahedral group
    2. Tunneling adjacencies (Ch-Ch, Ch-App, App-App, Legacy-Em, Em-Rev, Mobius)
    3. Mycelium rail assignments (3 Legacy + 12 CLOUD + Gamma corridor)
    4. A sacred geometry figure
    5. A 5D expansion coordinate (chapter, lens, stage, rail, geometry)

The engine implements the complete 10-stage synthesis cascade:
    Stage 0: Legacy Neutral Baseline
    Stage 1: Single-Lens Witnesses
    Stage 2: Pairwise Symmetries
    Stage 3: Triadic Symmetries
    Stage 4: Four-Way Total Synthesis
    Stage 5: Zero-Point Collapse
    Stage 6: 5D Meta-Observation
    Stage 7: Manifestation / Compiler Pass
    Stage 8: Omega Anchoring
    Stage 9: Emergent Re-Expansion

v1.0 — 2026-03-13
"""

from __future__ import annotations
import hashlib
import math
import json
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from canon_compiler import (
    Quaternion, PHI, INV_PHI,
    ArtifactClass, SymmetryArtifact, SIGMA_ANCHOR, BLOOM_PHI, MOB_ZSTAR_GATE,
    artifact_station, station_artifact, tunnel_transition, verify_circuit_closure,
    LensView, Quadrant, USE_OPERATIONS, LENS_BITMASK, TUNNEL_FAMILY,
)


# =====================================================================
# SECTION 1: MANUSCRIPT ARCHITECTURE
# =====================================================================

class UnitKind(Enum):
    CHAPTER = "Ch"
    APPENDIX = "App"
    EMERGENT = "E"
    METRO_NUCLEUS = "E10"
    REVERSE_APPENDIX = "Rev"


@dataclass
class ManuscriptUnit:
    """A single addressable unit in the manuscript lattice."""
    code: str           # e.g. "Ch01", "AppA", "E03", "AppZ_rev"
    title: str
    kind: UnitKind
    index: int          # ordinal within kind (0-based)
    binary_addr: str    # base-2 address from chapter numbering


# --- 21 Chapters ---
CHAPTERS: list[ManuscriptUnit] = [
    ManuscriptUnit("Ch01", "Kernel and Entry Law", UnitKind.CHAPTER, 0, "0000"),
    ManuscriptUnit("Ch02", "Address Algebra and Crystal Coordinates", UnitKind.CHAPTER, 1, "0001"),
    ManuscriptUnit("Ch03", "Truth Corridors and Witness Discipline", UnitKind.CHAPTER, 2, "0002"),
    ManuscriptUnit("Ch04", "Zero-Point Stabilization", UnitKind.CHAPTER, 3, "0003"),
    ManuscriptUnit("Ch05", "Paradox Regimes and Quarantine Calculus", UnitKind.CHAPTER, 4, "0010"),
    ManuscriptUnit("Ch06", "Documents as Theories", UnitKind.CHAPTER, 5, "0011"),
    ManuscriptUnit("Ch07", "Tunnels as Morphisms", UnitKind.CHAPTER, 6, "0012"),
    ManuscriptUnit("Ch08", "Synchronization Calculus", UnitKind.CHAPTER, 7, "0013"),
    ManuscriptUnit("Ch09", "Retrieval and Metro Routing", UnitKind.CHAPTER, 8, "0020"),
    ManuscriptUnit("Ch10", "Multi-Lens Solution Construction", UnitKind.CHAPTER, 9, "0021"),
    ManuscriptUnit("Ch11", "Void Book and Restart Token Tunneling", UnitKind.CHAPTER, 10, "0022"),
    ManuscriptUnit("Ch12", "Legality Certificates and Closure", UnitKind.CHAPTER, 11, "0023"),
    ManuscriptUnit("Ch13", "Memory Regeneration and Persistence", UnitKind.CHAPTER, 12, "0030"),
    ManuscriptUnit("Ch14", "Migration Versioning and Pulse Retro-Weaving", UnitKind.CHAPTER, 13, "0031"),
    ManuscriptUnit("Ch15", "Cut Architecture", UnitKind.CHAPTER, 14, "0032"),
    ManuscriptUnit("Ch16", "Verification Harnesses and Replay Kernels", UnitKind.CHAPTER, 15, "0033"),
    ManuscriptUnit("Ch17", "Deployment and Bounded Agency", UnitKind.CHAPTER, 16, "0100"),
    ManuscriptUnit("Ch18", "Macro Invariants and Universal Math Stack", UnitKind.CHAPTER, 17, "0101"),
    ManuscriptUnit("Ch19", "Convergence Fixed Points and Controlled Non-Convergence", UnitKind.CHAPTER, 18, "0102"),
    ManuscriptUnit("Ch20", "Collective Authoring and Three-Agent Synchrony", UnitKind.CHAPTER, 19, "0103"),
    ManuscriptUnit("Ch21", "Self-Replication Open Problems and the Next Crystal", UnitKind.CHAPTER, 20, "0110"),
]

# --- 16 Appendices ---
APPENDICES: list[ManuscriptUnit] = [
    ManuscriptUnit("AppA", "Addressing Symbols Parsing Grammar", UnitKind.APPENDIX, 0, "1000"),
    ManuscriptUnit("AppB", "Canon Laws Equivalence Budgets Normal Forms", UnitKind.APPENDIX, 1, "1001"),
    ManuscriptUnit("AppC", "Square Kernel Pack", UnitKind.APPENDIX, 2, "1010"),
    ManuscriptUnit("AppD", "Registry Profiles Version IDs", UnitKind.APPENDIX, 3, "1011"),
    ManuscriptUnit("AppE", "Circle Gear and Mixed-Radix Clock", UnitKind.APPENDIX, 4, "1100"),
    ManuscriptUnit("AppF", "Transport Rotation as Conjugacy Dual Legality", UnitKind.APPENDIX, 5, "1101"),
    ManuscriptUnit("AppG", "Triangle Control and Tria Prima", UnitKind.APPENDIX, 6, "1110"),
    ManuscriptUnit("AppH", "Coupling and Topology", UnitKind.APPENDIX, 7, "1111"),
    ManuscriptUnit("AppI", "Corridors and Truth Lattice", UnitKind.APPENDIX, 8, "10000"),
    ManuscriptUnit("AppJ", "Residual Ledgers and Near Machinery", UnitKind.APPENDIX, 9, "10001"),
    ManuscriptUnit("AppK", "Conflict Quarantine Revocation", UnitKind.APPENDIX, 10, "10010"),
    ManuscriptUnit("AppL", "Evidence Plans and Ambig Promotion", UnitKind.APPENDIX, 11, "10011"),
    ManuscriptUnit("AppM", "Replay Kernel and Verifier Capsules", UnitKind.APPENDIX, 12, "10100"),
    ManuscriptUnit("AppN", "Container Formats and Virtual Mount", UnitKind.APPENDIX, 13, "10101"),
    ManuscriptUnit("AppO", "Publication Import/Export Bundles", UnitKind.APPENDIX, 14, "10110"),
    ManuscriptUnit("AppP", "Deployment Profiles and Monitoring", UnitKind.APPENDIX, 15, "10111"),
]

# --- 9 Emergent Chapters + E10 Metro Nucleus ---
EMERGENT: list[ManuscriptUnit] = [
    ManuscriptUnit("E01", "Seed", UnitKind.EMERGENT, 0, "11000"),
    ManuscriptUnit("E02", "Mirror", UnitKind.EMERGENT, 1, "11001"),
    ManuscriptUnit("E03", "Bridge", UnitKind.EMERGENT, 2, "11010"),
    ManuscriptUnit("E04", "Lattice", UnitKind.EMERGENT, 3, "11011"),
    ManuscriptUnit("E05", "Spiral", UnitKind.EMERGENT, 4, "11100"),
    ManuscriptUnit("E06", "Prism", UnitKind.EMERGENT, 5, "11101"),
    ManuscriptUnit("E07", "Wave", UnitKind.EMERGENT, 6, "11110"),
    ManuscriptUnit("E08", "Axis", UnitKind.EMERGENT, 7, "11111"),
    ManuscriptUnit("E09", "Zero", UnitKind.EMERGENT, 8, "100000"),
    ManuscriptUnit("E10", "Metro Nucleus", UnitKind.METRO_NUCLEUS, 9, "100001"),
]

# --- 16 Reverse Appendices ---
REVERSE_APPENDICES: list[ManuscriptUnit] = [
    ManuscriptUnit("AppZ_rev", "Origin Mirror", UnitKind.REVERSE_APPENDIX, 0, "110000"),
    ManuscriptUnit("AppY_rev", "Inverse Grammar", UnitKind.REVERSE_APPENDIX, 1, "110001"),
    ManuscriptUnit("AppX_rev", "Reflection Law", UnitKind.REVERSE_APPENDIX, 2, "110010"),
    ManuscriptUnit("AppW_rev", "Shadow Registry", UnitKind.REVERSE_APPENDIX, 3, "110011"),
    ManuscriptUnit("AppV_rev", "Counter-Clock", UnitKind.REVERSE_APPENDIX, 4, "110100"),
    ManuscriptUnit("AppU_rev", "Dual Transport", UnitKind.REVERSE_APPENDIX, 5, "110101"),
    ManuscriptUnit("AppT_rev", "Inverse Triangle", UnitKind.REVERSE_APPENDIX, 6, "110110"),
    ManuscriptUnit("AppS_rev", "Decoupling Boundary", UnitKind.REVERSE_APPENDIX, 7, "110111"),
    ManuscriptUnit("AppR_rev", "Anti-Corridor", UnitKind.REVERSE_APPENDIX, 8, "111000"),
    ManuscriptUnit("AppQ_rev", "Residual Return", UnitKind.REVERSE_APPENDIX, 9, "111001"),
    ManuscriptUnit("AppP_rev", "Conflict Reabsorption", UnitKind.REVERSE_APPENDIX, 10, "111010"),
    ManuscriptUnit("AppO_rev", "Counter-Evidence", UnitKind.REVERSE_APPENDIX, 11, "111011"),
    ManuscriptUnit("AppN_rev", "Replay Inverse", UnitKind.REVERSE_APPENDIX, 12, "111100"),
    ManuscriptUnit("AppM_rev", "Virtual Unmount", UnitKind.REVERSE_APPENDIX, 13, "111101"),
    ManuscriptUnit("AppL_rev", "Import Reversal", UnitKind.REVERSE_APPENDIX, 14, "111110"),
    ManuscriptUnit("AppK_rev", "Boundary Inverse", UnitKind.REVERSE_APPENDIX, 15, "111111"),
]

ALL_UNITS: list[ManuscriptUnit] = CHAPTERS + APPENDICES + EMERGENT + REVERSE_APPENDICES


# =====================================================================
# SECTION 2: 60-ARTIFACT ROUTING SYSTEM
# =====================================================================

def _build_full_60_artifacts() -> list[SymmetryArtifact]:
    """Build the complete 60-element icosahedral rotation group I_60.

    Class I:   1 Singularity (identity, 0 rotation)
    Class II:  24 Pentad Flowers (72 degree rotations, order 5)
    Class III: 20 Triadic Hinges (120 degree rotations, order 3)
    Class IV:  15 Mobius Dipoles (180 degree inversions, order 2)
    """
    artifacts: list[SymmetryArtifact] = []

    # --- Class I: 1 Singularity ---
    artifacts.append(SymmetryArtifact(
        number=1, name="Sigma-Anchor (Identity)",
        artifact_class=ArtifactClass.SINGULARITY,
        quaternion=Quaternion(1, 0, 0, 0),
        liminal_addr="<0000>", sigma60_state="Z*", v2x_dim="A+00.Z",
    ))

    # --- Class II: 24 Pentad Flowers (72 degree, order 5) ---
    # 6 axes of 5-fold symmetry, 4 non-trivial rotations each = 24
    pentad_axes = [
        (1, PHI, 0),
        (1, -PHI, 0),
        (0, 1, PHI),
        (0, 1, -PHI),
        (PHI, 0, 1),
        (PHI, 0, -1),
    ]
    pentad_names = [
        "Bloom-Alpha", "Bloom-Beta", "Bloom-Gamma",
        "Bloom-Delta", "Bloom-Epsilon", "Bloom-Zeta",
    ]
    n = 2
    for ax_idx, axis in enumerate(pentad_axes):
        for k in range(1, 5):  # 72, 144, 216, 288 degrees
            angle = k * 72.0
            q = Quaternion.from_axis_angle(axis, angle)
            quad_label, sigma = artifact_station(n)
            artifacts.append(SymmetryArtifact(
                number=n,
                name=f"{pentad_names[ax_idx]}-{k}",
                artifact_class=ArtifactClass.PENTAD,
                quaternion=q.normalized(),
                liminal_addr=f"<{n:04d}>",
                sigma60_state=f"{quad_label}.{sigma:02d}",
                v2x_dim=f"A+{(sigma % 15):02d}.{'SFCR'[n % 4]}",
            ))
            n += 1

    # --- Class III: 20 Triadic Hinges (120 degree, order 3) ---
    # 10 axes of 3-fold symmetry, 2 non-trivial rotations each = 20
    triad_axes = [
        (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
        (-1, 1, 1), (0, INV_PHI, PHI), (0, INV_PHI, -PHI),
        (INV_PHI, PHI, 0), (INV_PHI, -PHI, 0), (PHI, 0, INV_PHI),
    ]
    triad_names = [
        "Hinge-NE", "Hinge-NW", "Hinge-SE", "Hinge-SW", "Hinge-ZN",
        "Hinge-GP", "Hinge-GN", "Hinge-HP", "Hinge-HN", "Hinge-KP",
    ]
    for ax_idx, axis in enumerate(triad_axes):
        for k in range(1, 3):  # 120, 240 degrees
            angle = k * 120.0
            q = Quaternion.from_axis_angle(axis, angle)
            quad_label, sigma = artifact_station(n)
            artifacts.append(SymmetryArtifact(
                number=n,
                name=f"{triad_names[ax_idx]}-{k}",
                artifact_class=ArtifactClass.TRIAD,
                quaternion=q.normalized(),
                liminal_addr=f"<{n:04d}>",
                sigma60_state=f"{quad_label}.{sigma:02d}",
                v2x_dim=f"A+{(sigma % 15):02d}.{'SFCR'[n % 4]}",
            ))
            n += 1

    # --- Class IV: 15 Mobius Dipoles (180 degree, order 2) ---
    # 15 axes of 2-fold symmetry, 1 non-trivial rotation each = 15
    mobius_axes = [
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1),
        (0, 1, 1), (0, 1, -1),
        (PHI, 1, 0), (PHI, -1, 0), (0, PHI, 1), (0, PHI, -1),
        (1, 0, PHI), (1, 0, -PHI),
    ]
    mobius_names = [
        "Mob-X", "Mob-Y", "Mob-Z",
        "Mob-XY+", "Mob-XY-", "Mob-XZ+", "Mob-XZ-",
        "Mob-YZ+", "Mob-YZ-",
        "Mob-GP+", "Mob-GP-", "Mob-GQ+", "Mob-GQ-",
        "Mob-GR+", "Mob-GR-",
    ]
    for ax_idx, axis in enumerate(mobius_axes):
        q = Quaternion.from_axis_angle(axis, 180.0)
        quad_label, sigma = artifact_station(n)
        artifacts.append(SymmetryArtifact(
            number=n,
            name=f"{mobius_names[ax_idx]}",
            artifact_class=ArtifactClass.MOBIUS,
            quaternion=q.normalized(),
            liminal_addr=f"<{n:04d}>",
            sigma60_state=f"{quad_label}.{sigma:02d}",
            v2x_dim=f"A+{(sigma % 15):02d}.{'SFCR'[n % 4]}",
        ))
        n += 1

    return artifacts


ARTIFACTS_60 = _build_full_60_artifacts()
ARTIFACT_BY_NUMBER = {a.number: a for a in ARTIFACTS_60}


def assign_artifact(unit: ManuscriptUnit) -> SymmetryArtifact:
    """Assign a quaternion artifact to a manuscript unit via hash routing.

    The binary address of the unit is hashed and mapped modulo 60 into
    the artifact table. This gives each unit a deterministic rotational
    operator from the icosahedral group.
    """
    h = int(hashlib.sha256(unit.code.encode()).hexdigest(), 16)
    artifact_idx = (h % 60)
    return ARTIFACTS_60[artifact_idx]


# =====================================================================
# SECTION 3: ELEMENTAL LENS TRANSFORMS
# =====================================================================

class Element(Enum):
    FIRE = auto()    # ignition, emergence, differentiation
    WATER = auto()   # memory, coherence, resonance
    EARTH = auto()   # structure, embodiment, stability
    AIR = auto()     # abstraction, topology, communication


@dataclass
class LensTransform:
    """An elemental observation lens applied to a manuscript unit."""
    element: Element
    qualities: tuple[str, str, str]
    quadrant: str          # V4 quadrant label
    sigma_mask: int        # which sigma bits this lens activates
    color: str             # associated CLOUD rail color

    def witness(self, unit: ManuscriptUnit) -> str:
        """Generate the witness signature for a unit under this lens."""
        raw = f"{self.element.name}:{unit.code}:{unit.title}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]


LENS_FIRE = LensTransform(
    Element.FIRE, ("ignition", "emergence", "differentiation"),
    "A", 0b1000, "RED",
)
LENS_WATER = LensTransform(
    Element.WATER, ("memory", "coherence", "resonance"),
    "B", 0b0100, "BLUE",
)
LENS_EARTH = LensTransform(
    Element.EARTH, ("structure", "embodiment", "stability"),
    "C", 0b0010, "GREEN",
)
LENS_AIR = LensTransform(
    Element.AIR, ("abstraction", "topology", "communication"),
    "D", 0b0001, "SILVER",
)

ALL_LENSES = [LENS_FIRE, LENS_WATER, LENS_EARTH, LENS_AIR]
LENS_PAIRS = [
    (LENS_FIRE, LENS_WATER), (LENS_FIRE, LENS_EARTH), (LENS_FIRE, LENS_AIR),
    (LENS_WATER, LENS_EARTH), (LENS_WATER, LENS_AIR), (LENS_EARTH, LENS_AIR),
]
LENS_TRIADS = [
    (LENS_FIRE, LENS_WATER, LENS_EARTH),
    (LENS_FIRE, LENS_WATER, LENS_AIR),
    (LENS_FIRE, LENS_EARTH, LENS_AIR),
    (LENS_WATER, LENS_EARTH, LENS_AIR),
]


# =====================================================================
# SECTION 4: SACRED GEOMETRY MAPPING
# =====================================================================

CHAPTER_GEOMETRY: dict[str, str] = {
    "Ch01": "Square",      "Ch02": "Circle",      "Ch03": "Triangle",
    "Ch04": "Torus",       "Ch05": "Pentagon",     "Ch06": "Hexagon",
    "Ch07": "Heptagon",    "Ch08": "Octagon",      "Ch09": "Enneagon",
    "Ch10": "Decagon",     "Ch11": "Vesica-Piscis", "Ch12": "Dodecahedron",
    "Ch13": "Icosahedron", "Ch14": "Tetrahedron",  "Ch15": "Cube",
    "Ch16": "Octahedron",  "Ch17": "Flower-of-Life", "Ch18": "Metatrons-Cube",
    "Ch19": "Sri-Yantra",  "Ch20": "Seed-of-Life", "Ch21": "Merkaba",
}

APPENDIX_ROLE: dict[str, str] = {
    "AppA": "glossary",   "AppB": "proof",       "AppC": "routing",
    "AppD": "law",        "AppE": "runtime",      "AppF": "return",
    "AppG": "glossary",   "AppH": "proof",        "AppI": "routing",
    "AppJ": "law",        "AppK": "runtime",      "AppL": "return",
    "AppM": "glossary",   "AppN": "proof",        "AppO": "routing",
    "AppP": "law",
}

EMERGENT_PHASE: dict[str, str] = {
    "E01": "Seed",   "E02": "Mirror",  "E03": "Bridge",
    "E04": "Lattice", "E05": "Spiral", "E06": "Prism",
    "E07": "Wave",   "E08": "Axis",    "E09": "Zero",
    "E10": "Nucleus",
}

def sacred_figure(unit: ManuscriptUnit) -> str:
    """Return the sacred geometry figure for a manuscript unit."""
    if unit.kind == UnitKind.CHAPTER:
        return CHAPTER_GEOMETRY.get(unit.code, "Circle")
    if unit.kind == UnitKind.APPENDIX:
        role = APPENDIX_ROLE.get(unit.code, "routing")
        role_to_fig = {
            "glossary": "Hexagram", "proof": "Pentacle",
            "routing": "Labyrinth", "law": "Scales",
            "runtime": "Ouroboros", "return": "Ankh",
        }
        return role_to_fig.get(role, "Hexagram")
    if unit.kind in (UnitKind.EMERGENT, UnitKind.METRO_NUCLEUS):
        phase = EMERGENT_PHASE.get(unit.code, "Seed")
        phase_to_fig = {
            "Seed": "Point", "Mirror": "Line", "Bridge": "Arc",
            "Lattice": "Grid", "Spiral": "Golden-Spiral",
            "Prism": "Tetrahedron", "Wave": "Sine", "Axis": "Cross",
            "Zero": "Void-Circle", "Nucleus": "Torus-Knot",
        }
        return phase_to_fig.get(phase, "Point")
    if unit.kind == UnitKind.REVERSE_APPENDIX:
        return "Inverted-" + sacred_figure(ManuscriptUnit(
            code=unit.code.replace("_rev", "").replace("AppZ", "AppA")
            .replace("AppY", "AppB").replace("AppX", "AppC")
            .replace("AppW", "AppD").replace("AppV", "AppE")
            .replace("AppU", "AppF").replace("AppT", "AppG")
            .replace("AppS", "AppH").replace("AppR", "AppI")
            .replace("AppQ", "AppJ").replace("AppP", "AppK")
            .replace("AppO", "AppL").replace("AppN", "AppM")
            .replace("AppM", "AppN").replace("AppL", "AppO")
            .replace("AppK", "AppP"),
            title="", kind=UnitKind.APPENDIX, index=unit.index,
            binary_addr=unit.binary_addr,
        ))
    return "Unknown"


# =====================================================================
# SECTION 5: TUNNELING PATHS
# =====================================================================

@dataclass
class Tunnel:
    """A directed connection between two manuscript units."""
    source: str          # unit code
    target: str          # unit code
    tunnel_type: str     # "Ch-Ch", "Ch-App", "App-App", etc.
    quaternion: Quaternion  # transition operator
    gamma_weight: float  # corridor weighting (0-1)


def _ch_ch_tunnels() -> list[Tunnel]:
    """Chapter-to-chapter tunnels: each chapter connects to its binary neighbor."""
    tunnels = []
    for i, src in enumerate(CHAPTERS):
        # Sequential tunnel
        if i + 1 < len(CHAPTERS):
            tgt = CHAPTERS[i + 1]
            q_src = assign_artifact(src).quaternion
            q_tgt = assign_artifact(tgt).quaternion
            t_q = tunnel_transition(q_src, q_tgt)
            tunnels.append(Tunnel(src.code, tgt.code, "Ch-Ch", t_q, 1.0))
        # Modular tunnel: connect Ch_i to Ch_{(i+7) mod 21}
        j = (i + 7) % len(CHAPTERS)
        if j != i and j != i + 1:
            tgt = CHAPTERS[j]
            q_src = assign_artifact(src).quaternion
            q_tgt = assign_artifact(tgt).quaternion
            t_q = tunnel_transition(q_src, q_tgt)
            tunnels.append(Tunnel(src.code, tgt.code, "Ch-Ch", t_q, 0.618))
    return tunnels


def _ch_app_tunnels() -> list[Tunnel]:
    """Chapter-to-appendix tunnels: map chapter index mod 16 to appendix."""
    tunnels = []
    for ch in CHAPTERS:
        app_idx = ch.index % len(APPENDICES)
        app = APPENDICES[app_idx]
        q_ch = assign_artifact(ch).quaternion
        q_app = assign_artifact(app).quaternion
        t_q = tunnel_transition(q_ch, q_app)
        tunnels.append(Tunnel(ch.code, app.code, "Ch-App", t_q, 0.8))
    return tunnels


def _app_app_tunnels() -> list[Tunnel]:
    """Appendix-to-appendix: sequential ring plus cross-links."""
    tunnels = []
    for i, src in enumerate(APPENDICES):
        # Ring connection
        tgt = APPENDICES[(i + 1) % len(APPENDICES)]
        q_s = assign_artifact(src).quaternion
        q_t = assign_artifact(tgt).quaternion
        tunnels.append(Tunnel(src.code, tgt.code, "App-App",
                              tunnel_transition(q_s, q_t), 0.9))
        # Cross-link: mirror pair (i <-> 15-i)
        mirror_idx = 15 - i
        if mirror_idx != i and mirror_idx != (i + 1) % 16:
            tgt_m = APPENDICES[mirror_idx]
            q_m = assign_artifact(tgt_m).quaternion
            tunnels.append(Tunnel(src.code, tgt_m.code, "App-App",
                                  tunnel_transition(q_s, q_m), 0.5))
    return tunnels


def _legacy_emergent_tunnels() -> list[Tunnel]:
    """Legacy (chapters/appendices) to Emergent tunnels."""
    tunnels = []
    # Each emergent chapter pulls from a specific chapter range
    for em in EMERGENT:
        # E01 pulls from Ch01-Ch03, E02 from Ch04-Ch06, etc.
        start_ch = em.index * 2
        for offset in range(min(3, len(CHAPTERS) - start_ch)):
            ch = CHAPTERS[start_ch + offset]
            q_ch = assign_artifact(ch).quaternion
            q_em = assign_artifact(em).quaternion
            tunnels.append(Tunnel(ch.code, em.code, "Legacy-Em",
                                  tunnel_transition(q_ch, q_em), 0.7))
    return tunnels


def _emergent_reverse_tunnels() -> list[Tunnel]:
    """Emergent to reverse-appendix tunnels."""
    tunnels = []
    for em in EMERGENT:
        # Each emergent connects to 1-2 reverse appendices
        rev_idx = em.index % len(REVERSE_APPENDICES)
        rev = REVERSE_APPENDICES[rev_idx]
        q_em = assign_artifact(em).quaternion
        q_rev = assign_artifact(rev).quaternion
        tunnels.append(Tunnel(em.code, rev.code, "Em-Rev",
                              tunnel_transition(q_em, q_rev), 0.6))
        # Second connection offset by 8
        rev2_idx = (em.index + 8) % len(REVERSE_APPENDICES)
        rev2 = REVERSE_APPENDICES[rev2_idx]
        q_rev2 = assign_artifact(rev2).quaternion
        tunnels.append(Tunnel(em.code, rev2.code, "Em-Rev",
                              tunnel_transition(q_em, q_rev2), 0.4))
    return tunnels


def _mobius_bridge_tunnels() -> list[Tunnel]:
    """Mobius bridge tunnels: Q ingress (forward), O return (backward).

    These use Mobius dipoles (180 degree inversions) to connect
    the forward manuscript flow to reverse re-entry paths.
    """
    tunnels = []
    mobius_artifacts = [a for a in ARTIFACTS_60 if a.artifact_class == ArtifactClass.MOBIUS]

    # Q ingress: Ch -> Reverse via Mobius inversion
    for i, ch in enumerate(CHAPTERS[:15]):
        rev = REVERSE_APPENDICES[i]
        mob = mobius_artifacts[i % len(mobius_artifacts)]
        tunnels.append(Tunnel(ch.code, rev.code, "Mobius-Q-Ingress",
                              mob.quaternion, 0.382))

    # O return: Reverse -> Chapter via conjugate Mobius
    for i, rev in enumerate(REVERSE_APPENDICES[:15]):
        ch = CHAPTERS[i]
        mob = mobius_artifacts[i % len(mobius_artifacts)]
        tunnels.append(Tunnel(rev.code, ch.code, "Mobius-O-Return",
                              mob.quaternion.conjugate(), 0.382))
    return tunnels


def build_all_tunnels() -> list[Tunnel]:
    """Build the complete tunneling matrix."""
    return (
        _ch_ch_tunnels() +
        _ch_app_tunnels() +
        _app_app_tunnels() +
        _legacy_emergent_tunnels() +
        _emergent_reverse_tunnels() +
        _mobius_bridge_tunnels()
    )


# =====================================================================
# SECTION 6: MYCELIUM NETWORK
# =====================================================================

@dataclass
class MyceliumRail:
    """A named transport rail in the mycelium network."""
    name: str
    rail_type: str   # "Legacy" or "CLOUD"
    color: str
    sigma_path: list[int]  # sigma stations this rail visits


LEGACY_RAILS = [
    MyceliumRail("Su", "Legacy", "GOLD", [0, 3, 6, 9, 12]),
    MyceliumRail("Me", "Legacy", "SILVER", [1, 4, 7, 10, 13]),
    MyceliumRail("Sa", "Legacy", "CHARCOAL", [2, 5, 8, 11, 14]),
]

CLOUD_RAILS = [
    MyceliumRail("RED", "CLOUD", "RED", [0, 5, 10]),
    MyceliumRail("BLUE", "CLOUD", "BLUE", [1, 6, 11]),
    MyceliumRail("GREEN", "CLOUD", "GREEN", [2, 7, 12]),
    MyceliumRail("GREY", "CLOUD", "GREY", [3, 8, 13]),
    MyceliumRail("VIOLET", "CLOUD", "VIOLET", [4, 9, 14]),
    MyceliumRail("SILVER", "CLOUD", "SILVER", [0, 7, 14]),
    MyceliumRail("GOLD", "CLOUD", "GOLD", [1, 8, 0]),
    MyceliumRail("WHITE", "CLOUD", "WHITE", [2, 9, 1]),
    MyceliumRail("CHARCOAL", "CLOUD", "CHARCOAL", [3, 10, 2]),
    MyceliumRail("BLACK", "CLOUD", "BLACK", [4, 11, 3]),
    MyceliumRail("AIR", "CLOUD", "AIR", [5, 12, 4]),
    MyceliumRail("TEAL", "CLOUD", "TEAL", [6, 13, 5]),
]

ALL_RAILS = LEGACY_RAILS + CLOUD_RAILS

# Gamma corridor: the privileged cycle through sigma space
GAMMA_CORRIDOR = [2, 11, 5, 14, 8, 2]  # sigma=2 -> 11 -> 5 -> 14 -> 8 -> 2


def assign_rails(unit: ManuscriptUnit) -> list[str]:
    """Determine which mycelium rails serve a given manuscript unit.

    Each unit rides at least one legacy rail and one CLOUD rail,
    determined by its index and hash.
    """
    h = int(hashlib.sha256(unit.code.encode()).hexdigest(), 16)
    legacy_idx = unit.index % len(LEGACY_RAILS)
    cloud_idx = h % len(CLOUD_RAILS)
    rails = [LEGACY_RAILS[legacy_idx].name, CLOUD_RAILS[cloud_idx].name]

    # Units on the gamma corridor get the GAMMA tag
    artifact = assign_artifact(unit)
    _, sigma = artifact_station(artifact.number)
    if sigma in GAMMA_CORRIDOR:
        rails.append("GAMMA")
    return rails


# =====================================================================
# SECTION 7: SYNTHESIS ENGINE (10-Stage Pipeline)
# =====================================================================

@dataclass
class SynthesisStage:
    """Result of one synthesis stage."""
    stage_number: int
    stage_name: str
    witness_hash: str
    lens_config: str
    payload: dict


@dataclass
class ExpansionDocument:
    """The complete 5D expansion of a single manuscript unit."""
    unit: ManuscriptUnit
    artifact: SymmetryArtifact
    sacred_figure: str
    rails: list[str]
    tunnels: list[str]      # codes of adjacent units
    stages: list[SynthesisStage]
    coordinate_5d: tuple[int, int, int, int, int]

    def summary(self) -> str:
        lines = [
            f"=== 5D Expansion: {self.unit.code} — {self.unit.title} ===",
            f"  Kind:          {self.unit.kind.value}",
            f"  Artifact:      #{self.artifact.number} {self.artifact.name} ({self.artifact.artifact_class.value})",
            f"  Quaternion:    {self.artifact.quaternion}",
            f"  Sacred Figure: {self.sacred_figure}",
            f"  Rails:         {', '.join(self.rails)}",
            f"  Tunnels to:    {', '.join(self.tunnels[:6])}{'...' if len(self.tunnels) > 6 else ''}",
            f"  5D Coord:      {self.coordinate_5d}",
            f"  Stages:        {len(self.stages)} completed",
        ]
        return "\n".join(lines)


def _hash_witness(*parts: str) -> str:
    """Compute a witness hash from concatenated parts."""
    raw = ":".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _stage_0_baseline(unit: ManuscriptUnit, content_hash: str) -> SynthesisStage:
    """Stage 0: Legacy Neutral Baseline. Captures the unit before any lens is applied."""
    witness = _hash_witness("S0", unit.code, content_hash)
    return SynthesisStage(
        stage_number=0, stage_name="Legacy Neutral Baseline",
        witness_hash=witness, lens_config="NONE",
        payload={"unit": unit.code, "content_hash": content_hash,
                 "mode": "neutral", "truth_class": "OK"},
    )


def _stage_1_single_lens(unit: ManuscriptUnit, content_hash: str) -> SynthesisStage:
    """Stage 1: Single-Lens Witnesses. Apply each of FIRE, WATER, EARTH, AIR independently."""
    witnesses = {}
    for lens in ALL_LENSES:
        w = lens.witness(unit)
        witnesses[lens.element.name] = w
    combined = _hash_witness("S1", *witnesses.values())
    return SynthesisStage(
        stage_number=1, stage_name="Single-Lens Witnesses",
        witness_hash=combined, lens_config="F|W|E|A",
        payload={"witnesses": witnesses, "count": 4},
    )


def _stage_2_pairwise(unit: ManuscriptUnit, content_hash: str) -> SynthesisStage:
    """Stage 2: Pairwise Symmetries. Combine lenses in all 6 pairs."""
    pairs = {}
    for la, lb in LENS_PAIRS:
        key = f"{la.element.name}+{lb.element.name}"
        wa = la.witness(unit)
        wb = lb.witness(unit)
        pairs[key] = _hash_witness(wa, wb)
    combined = _hash_witness("S2", *pairs.values())
    return SynthesisStage(
        stage_number=2, stage_name="Pairwise Symmetries",
        witness_hash=combined, lens_config="FW|FE|FA|WE|WA|EA",
        payload={"pairs": pairs, "count": 6},
    )


def _stage_3_triadic(unit: ManuscriptUnit, content_hash: str) -> SynthesisStage:
    """Stage 3: Triadic Symmetries. Combine lenses in all 4 triads."""
    triads = {}
    for la, lb, lc in LENS_TRIADS:
        key = f"{la.element.name}+{lb.element.name}+{lc.element.name}"
        wa, wb, wc = la.witness(unit), lb.witness(unit), lc.witness(unit)
        triads[key] = _hash_witness(wa, wb, wc)
    combined = _hash_witness("S3", *triads.values())
    return SynthesisStage(
        stage_number=3, stage_name="Triadic Symmetries",
        witness_hash=combined, lens_config="FWE|FWA|FEA|WEA",
        payload={"triads": triads, "count": 4},
    )


def _stage_4_total(unit: ManuscriptUnit, content_hash: str) -> SynthesisStage:
    """Stage 4: Four-Way Total Synthesis. All four lenses simultaneously."""
    all_w = [lens.witness(unit) for lens in ALL_LENSES]
    total_hash = _hash_witness("S4", *all_w)
    sigma_mask = 0
    for lens in ALL_LENSES:
        sigma_mask |= lens.sigma_mask
    return SynthesisStage(
        stage_number=4, stage_name="Four-Way Total Synthesis",
        witness_hash=total_hash, lens_config="FWEA",
        payload={"sigma_mask": sigma_mask, "combined_witness": total_hash},
    )


def _stage_5_zero_point(unit: ManuscriptUnit, content_hash: str,
                         prev_hash: str) -> SynthesisStage:
    """Stage 5: Zero-Point Collapse. All lenses collapse to the identity quaternion."""
    identity = Quaternion(1, 0, 0, 0)
    artifact = assign_artifact(unit)
    collapse_q = tunnel_transition(artifact.quaternion, identity)
    collapse_hash = _hash_witness("S5", prev_hash, repr(collapse_q))
    deviation = abs(collapse_q.w - 1.0) + abs(collapse_q.x) + abs(collapse_q.y) + abs(collapse_q.z)
    return SynthesisStage(
        stage_number=5, stage_name="Zero-Point Collapse",
        witness_hash=collapse_hash, lens_config="Z*",
        payload={"collapse_quaternion": repr(collapse_q),
                 "deviation": round(deviation, 6), "stable": deviation < 2.0},
    )


def _stage_6_meta_observation(unit: ManuscriptUnit, content_hash: str,
                               prev_stages: list[SynthesisStage]) -> SynthesisStage:
    """Stage 6: 5D Meta-Observation. Observes the synthesis process itself."""
    stage_hashes = [s.witness_hash for s in prev_stages]
    meta_hash = _hash_witness("S6", *stage_hashes)
    coherence = sum(1 for s in prev_stages if s.payload.get("stable", True)) / max(len(prev_stages), 1)
    return SynthesisStage(
        stage_number=6, stage_name="5D Meta-Observation",
        witness_hash=meta_hash, lens_config="META",
        payload={"observed_stages": len(prev_stages),
                 "coherence_ratio": round(coherence, 4),
                 "meta_dimension": 5},
    )


def _stage_7_manifestation(unit: ManuscriptUnit, content_hash: str,
                            meta_hash: str) -> SynthesisStage:
    """Stage 7: Manifestation/Compiler Pass.

    Eight-step compiler chain:
    desire gradient -> optimal question -> Z* tunnel -> 60-gear hub ->
    beat synchrony -> downbeat anchor -> certificate -> replay kernel
    """
    artifact = assign_artifact(unit)
    desire_gradient = _hash_witness("S7.desire", unit.code, content_hash)
    optimal_question = _hash_witness("S7.question", desire_gradient, meta_hash)
    z_star_tunnel = _hash_witness("S7.zstar", optimal_question, "Z*")
    gear_hub = f"artifact_{artifact.number}_{artifact.artifact_class.value}"
    beat_sync = int(desire_gradient, 16) % 60
    downbeat = beat_sync % 21
    certificate = _hash_witness("S7.cert", z_star_tunnel, gear_hub, str(beat_sync))
    replay_kernel = _hash_witness("S7.replay", certificate, unit.binary_addr)

    return SynthesisStage(
        stage_number=7, stage_name="Manifestation/Compiler Pass",
        witness_hash=replay_kernel, lens_config="COMPILER",
        payload={
            "desire_gradient": desire_gradient,
            "optimal_question": optimal_question,
            "z_star_tunnel": z_star_tunnel,
            "gear_hub_60": gear_hub,
            "beat_synchrony": beat_sync,
            "downbeat_anchor": downbeat,
            "certificate": certificate,
            "replay_kernel": replay_kernel,
        },
    )


def _stage_8_omega_anchoring(unit: ManuscriptUnit, content_hash: str,
                              replay_kernel: str) -> SynthesisStage:
    """Stage 8: Omega Anchoring.

    Holographic memory, retrieval verification, backward re-entry path.
    """
    holographic_mem = _hash_witness("S8.holo", unit.code, content_hash, replay_kernel)
    retrieval_key = _hash_witness("S8.retrieve", holographic_mem, unit.binary_addr)

    # Backward re-entry: reverse the binary address for mirror addressing
    reverse_addr = unit.binary_addr[::-1]
    backward_entry = _hash_witness("S8.backward", retrieval_key, reverse_addr)

    return SynthesisStage(
        stage_number=8, stage_name="Omega Anchoring",
        witness_hash=backward_entry, lens_config="OMEGA",
        payload={
            "holographic_memory": holographic_mem,
            "retrieval_key": retrieval_key,
            "backward_re_entry": backward_entry,
            "reverse_addr": reverse_addr,
        },
    )


def _stage_9_re_expansion(unit: ManuscriptUnit, content_hash: str,
                           omega_hash: str) -> SynthesisStage:
    """Stage 9: Emergent Re-Expansion.

    E1-E9 phase mapping, E10 nucleus, Z->K path, Q/O circuit, Q->K bridge-band.
    """
    # Map unit to emergent phase
    em_idx = unit.index % len(EMERGENT)
    em_phase = EMERGENT[em_idx]
    e1_e9_hash = _hash_witness("S9.E1-E9", em_phase.code, omega_hash)

    # E10 Metro Nucleus contribution
    e10_hash = _hash_witness("S9.E10", "E10", e1_e9_hash)

    # Z -> K path (Zero to Kernel re-entry)
    z_to_k = _hash_witness("S9.ZK", e10_hash, "Ch01")

    # Q ingress and O return circuit
    q_ingress = _hash_witness("S9.Q", unit.code, z_to_k)
    o_return = _hash_witness("S9.O", q_ingress, unit.code)

    # Q -> K bridge-band
    q_to_k_bridge = _hash_witness("S9.QK", q_ingress, o_return, "bridge-band")

    return SynthesisStage(
        stage_number=9, stage_name="Emergent Re-Expansion",
        witness_hash=q_to_k_bridge, lens_config="EMERGENT",
        payload={
            "e1_e9_phase": em_phase.code,
            "e1_e9_hash": e1_e9_hash,
            "e10_nucleus": e10_hash,
            "z_to_k_path": z_to_k,
            "q_ingress": q_ingress,
            "o_return": o_return,
            "q_to_k_bridge": q_to_k_bridge,
        },
    )


def run_synthesis_pipeline(unit: ManuscriptUnit,
                           content_hash: str) -> list[SynthesisStage]:
    """Execute the full 10-stage synthesis pipeline for a single manuscript unit."""
    stages: list[SynthesisStage] = []

    s0 = _stage_0_baseline(unit, content_hash)
    stages.append(s0)

    s1 = _stage_1_single_lens(unit, content_hash)
    stages.append(s1)

    s2 = _stage_2_pairwise(unit, content_hash)
    stages.append(s2)

    s3 = _stage_3_triadic(unit, content_hash)
    stages.append(s3)

    s4 = _stage_4_total(unit, content_hash)
    stages.append(s4)

    s5 = _stage_5_zero_point(unit, content_hash, s4.witness_hash)
    stages.append(s5)

    s6 = _stage_6_meta_observation(unit, content_hash, stages)
    stages.append(s6)

    s7 = _stage_7_manifestation(unit, content_hash, s6.witness_hash)
    stages.append(s7)

    s8 = _stage_8_omega_anchoring(unit, content_hash, s7.payload["replay_kernel"])
    stages.append(s8)

    s9 = _stage_9_re_expansion(unit, content_hash, s8.witness_hash)
    stages.append(s9)

    return stages


# =====================================================================
# SECTION 8: EXPANSION FUNCTIONS
# =====================================================================

def _compute_5d_coordinate(unit: ManuscriptUnit, artifact: SymmetryArtifact,
                           stages: list[SynthesisStage],
                           rails: list[str]) -> tuple[int, int, int, int, int]:
    """Compute the 5-dimensional coordinate for a manuscript unit.

    Dimensions:
        d0: chapter/unit index (structural position)
        d1: lens configuration (bitmask of active lenses)
        d2: synthesis stage depth (highest completed stage)
        d3: rail index (primary mycelium rail)
        d4: geometry index (sacred figure hash mod 21)
    """
    d0 = unit.index
    d1 = sum(lens.sigma_mask for lens in ALL_LENSES)  # full mask at completion
    d2 = len(stages) - 1  # highest stage index
    rail_hash = int(hashlib.sha256(rails[0].encode()).hexdigest(), 16)
    d3 = rail_hash % 15
    geo = sacred_figure(unit)
    d4 = int(hashlib.sha256(geo.encode()).hexdigest(), 16) % 21
    return (d0, d1, d2, d3, d4)


def expand_manuscript_5d(chapter_code: str, title: str,
                         content_hash: str) -> ExpansionDocument:
    """Run the full 5D expansion for a single manuscript unit.

    Args:
        chapter_code: Unit code (e.g. "Ch01", "AppA", "E03")
        title: Human-readable title
        content_hash: SHA-256 hash of the unit's content

    Returns:
        A complete ExpansionDocument with all synthesis stages,
        artifact assignment, tunneling adjacencies, rail assignments,
        and sacred geometry mapping.
    """
    # Find the unit in the registry
    unit = None
    for u in ALL_UNITS:
        if u.code == chapter_code:
            unit = u
            break
    if unit is None:
        # Create an ad-hoc unit for codes not in the predefined registry
        kind = UnitKind.CHAPTER
        if chapter_code.startswith("App") and chapter_code.endswith("_rev"):
            kind = UnitKind.REVERSE_APPENDIX
        elif chapter_code.startswith("App"):
            kind = UnitKind.APPENDIX
        elif chapter_code.startswith("E"):
            kind = UnitKind.EMERGENT
        idx = int(hashlib.sha256(chapter_code.encode()).hexdigest(), 16) % 21
        unit = ManuscriptUnit(chapter_code, title, kind, idx,
                              bin(idx)[2:].zfill(4))

    # Assign artifact
    artifact = assign_artifact(unit)

    # Compute sacred figure
    geo = sacred_figure(unit)

    # Assign rails
    rails = assign_rails(unit)

    # Build tunneling adjacencies
    all_tunnels = build_all_tunnels()
    adjacent_codes = []
    for t in all_tunnels:
        if t.source == unit.code and t.target not in adjacent_codes:
            adjacent_codes.append(t.target)
        elif t.target == unit.code and t.source not in adjacent_codes:
            adjacent_codes.append(t.source)

    # Run synthesis
    stages = run_synthesis_pipeline(unit, content_hash)

    # Compute 5D coordinate
    coord = _compute_5d_coordinate(unit, artifact, stages, rails)

    return ExpansionDocument(
        unit=unit,
        artifact=artifact,
        sacred_figure=geo,
        rails=rails,
        tunnels=adjacent_codes,
        stages=stages,
        coordinate_5d=coord,
    )


# =====================================================================
# SECTION 9: MASTER MANIFEST GENERATOR
# =====================================================================

@dataclass
class MasterManifest:
    """The complete 5D manifest for the entire manuscript."""
    expansions: list[ExpansionDocument]
    tunneling_matrix: dict[str, list[str]]
    mycelium_network: dict[str, list[str]]
    sacred_geometry_map: dict[str, str]
    gamma_corridor: list[int]
    artifact_distribution: dict[str, int]
    total_units: int
    total_tunnels: int
    total_stages: int

    def summary(self) -> str:
        lines = [
            "=" * 72,
            "   5D MANUSCRIPT EXPANSION — MASTER MANIFEST",
            "=" * 72,
            f"  Total units:     {self.total_units}",
            f"  Total tunnels:   {self.total_tunnels}",
            f"  Total stages:    {self.total_stages}",
            f"  Gamma corridor:  {' -> '.join(f'sigma={s}' for s in self.gamma_corridor)}",
            "",
            "  ARTIFACT DISTRIBUTION:",
        ]
        for cls, count in sorted(self.artifact_distribution.items()):
            lines.append(f"    {cls}: {count} units")
        lines.append("")
        lines.append("  SACRED GEOMETRY MAP (first 10):")
        for code, fig in list(self.sacred_geometry_map.items())[:10]:
            lines.append(f"    {code:12s} -> {fig}")
        lines.append("")
        lines.append("  MYCELIUM NETWORK (rail -> unit count):")
        for rail, units in sorted(self.mycelium_network.items(), key=lambda x: -len(x[1])):
            lines.append(f"    {rail:12s} -> {len(units)} units")
        lines.append("")
        lines.append("  NINE-PART STRUCTURE:")
        part_names = [
            "I.   Kernel Foundation (Ch01-Ch04)",
            "II.  Paradox and Theory (Ch05-Ch08)",
            "III. Retrieval and Construction (Ch09-Ch12)",
            "IV.  Memory and Migration (Ch13-Ch16)",
            "V.   Deployment and Invariants (Ch17-Ch18)",
            "VI.  Convergence and Authoring (Ch19-Ch20)",
            "VII. Self-Replication (Ch21)",
            "VIII.Appendix Ring (AppA-AppP)",
            "IX.  Emergent Layer (E01-E10 + Reverse Ring)",
        ]
        for p in part_names:
            lines.append(f"    {p}")
        lines.append("=" * 72)
        return "\n".join(lines)


def generate_master_5d_manifest() -> MasterManifest:
    """Generate the complete 5D manifest for all manuscript units.

    Processes all 21 chapters, 16 appendices, 10 emergent chapters,
    and 16 reverse appendices through the full synthesis pipeline.
    """
    expansions: list[ExpansionDocument] = []
    tunneling_matrix: dict[str, list[str]] = {}
    mycelium_network: dict[str, list[str]] = {}
    sacred_map: dict[str, str] = {}
    artifact_dist: dict[str, int] = {
        "SINGULARITY": 0, "PENTAD": 0, "TRIAD": 0, "MOBIUS": 0,
    }

    # Initialize mycelium network buckets
    for rail in ALL_RAILS:
        mycelium_network[rail.name] = []

    # Process all units
    for unit in ALL_UNITS:
        content_hash = hashlib.sha256(
            f"{unit.code}:{unit.title}:v1.0".encode()
        ).hexdigest()[:32]

        doc = expand_manuscript_5d(unit.code, unit.title, content_hash)
        expansions.append(doc)

        # Record tunneling adjacency
        tunneling_matrix[unit.code] = doc.tunnels

        # Record sacred geometry
        sacred_map[unit.code] = doc.sacred_figure

        # Record artifact class distribution
        cls_name = doc.artifact.artifact_class.name
        artifact_dist[cls_name] = artifact_dist.get(cls_name, 0) + 1

        # Record mycelium assignments
        for rail_name in doc.rails:
            if rail_name in mycelium_network:
                mycelium_network[rail_name].append(unit.code)
            elif rail_name == "GAMMA":
                if "GAMMA" not in mycelium_network:
                    mycelium_network["GAMMA"] = []
                mycelium_network["GAMMA"].append(unit.code)

    all_tunnels = build_all_tunnels()
    total_stages = sum(len(doc.stages) for doc in expansions)

    return MasterManifest(
        expansions=expansions,
        tunneling_matrix=tunneling_matrix,
        mycelium_network=mycelium_network,
        sacred_geometry_map=sacred_map,
        gamma_corridor=GAMMA_CORRIDOR,
        artifact_distribution=artifact_dist,
        total_units=len(ALL_UNITS),
        total_tunnels=len(all_tunnels),
        total_stages=total_stages,
    )


# =====================================================================
# SECTION 10: MAIN EXECUTION
# =====================================================================

if __name__ == "__main__":
    print("SOS::5D_EXPANDER — Running full manuscript expansion...\n")

    # Generate master manifest
    manifest = generate_master_5d_manifest()

    # Print manifest summary
    print(manifest.summary())

    # Print detailed expansion for first chapter and first appendix
    print("\n" + "=" * 72)
    print("   SAMPLE EXPANSIONS")
    print("=" * 72)

    for code in ["Ch01", "Ch11", "Ch21", "AppA", "AppH", "E01", "E10", "AppZ_rev"]:
        for doc in manifest.expansions:
            if doc.unit.code == code:
                print(f"\n{doc.summary()}")
                print(f"  Stage 7 (Manifestation):")
                s7 = doc.stages[7]
                print(f"    Certificate:    {s7.payload['certificate']}")
                print(f"    Replay Kernel:  {s7.payload['replay_kernel']}")
                print(f"    Beat Synchrony: {s7.payload['beat_synchrony']}")
                print(f"  Stage 9 (Re-Expansion):")
                s9 = doc.stages[9]
                print(f"    E1-E9 Phase:    {s9.payload['e1_e9_phase']}")
                print(f"    Q->K Bridge:    {s9.payload['q_to_k_bridge']}")
                break

    # Verify a circuit closure through the gamma corridor
    print("\n" + "=" * 72)
    print("   GAMMA CORRIDOR CIRCUIT VERIFICATION")
    print("=" * 72)
    gamma_quaternions = []
    for i in range(len(GAMMA_CORRIDOR) - 1):
        s_from = GAMMA_CORRIDOR[i]
        s_to = GAMMA_CORRIDOR[i + 1]
        a_from = station_artifact("A", s_from)
        a_to = station_artifact("A", s_to)
        q_from = ARTIFACT_BY_NUMBER.get(a_from, ARTIFACTS_60[0]).quaternion
        q_to = ARTIFACT_BY_NUMBER.get(a_to, ARTIFACTS_60[0]).quaternion
        gamma_quaternions.append(tunnel_transition(q_from, q_to))

    is_closed, product = verify_circuit_closure(gamma_quaternions)
    print(f"  Gamma corridor: {' -> '.join(f'sigma={s}' for s in GAMMA_CORRIDOR)}")
    print(f"  Circuit closed: {is_closed}")
    print(f"  Product:        {product}")

    # Print tunnel counts by type
    print("\n" + "=" * 72)
    print("   TUNNELING STATISTICS")
    print("=" * 72)
    all_t = build_all_tunnels()
    type_counts: dict[str, int] = {}
    for t in all_t:
        type_counts[t.tunnel_type] = type_counts.get(t.tunnel_type, 0) + 1
    for ttype, count in sorted(type_counts.items()):
        print(f"  {ttype:25s} : {count:4d} tunnels")
    print(f"  {'TOTAL':25s} : {len(all_t):4d} tunnels")

    # Print artifact class summary
    print("\n" + "=" * 72)
    print("   I_60 ARTIFACT ATLAS SUMMARY")
    print("=" * 72)
    class_counts: dict[str, int] = {}
    for a in ARTIFACTS_60:
        cls = a.artifact_class.name
        class_counts[cls] = class_counts.get(cls, 0) + 1
    for cls, count in class_counts.items():
        angle = {"SINGULARITY": "0", "PENTAD": "72", "TRIAD": "120", "MOBIUS": "180"}[cls]
        print(f"  Class {a.artifact_class.value:4s} ({cls:12s}): {count:3d} artifacts @ {angle} degrees")

    print(f"\n  Total artifacts: {len(ARTIFACTS_60)}")
    print(f"  Total units expanded: {manifest.total_units}")
    print(f"  Total synthesis stages: {manifest.total_stages}")
    print("\nSOS::5D_EXPANDER — Expansion complete.")
