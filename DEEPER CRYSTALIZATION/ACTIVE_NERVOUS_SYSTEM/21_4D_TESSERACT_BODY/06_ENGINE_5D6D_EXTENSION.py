#!/usr/bin/env python3
"""
Mycelium Metro v5/v6 Extension — 5D/6D Coordinate Engine

Extends tesseract_metro_v4.py with:
- 5D family/council coordinates
- 6D civilization/succession coordinates
- Emergent chapter routing (E01-E09)
- Reverse appendix mapping (Z→K)
- Möbius bridge traversal (Q↔O)
- Holographic seed compression/expansion
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# --- 5D Constants ---

FAMILY_KEYWORDS = {
    "manuscript-architecture": ("manuscript", "chapter", "appendix", "metro", "routing", "address", "crystal"),
    "mathematical-kernel": ("math", "equation", "proof", "theorem", "lattice", "algebra", "geometry"),
    "voynich-analysis": ("voynich", "vml", "folio", "glyph", "decode", "botanical", "pharmaceutical"),
    "consciousness-framework": ("consciousness", "awareness", "observation", "meta", "self", "awakening"),
    "game-theory": ("game", "strategy", "player", "move", "equilibrium", "payoff", "sudoku"),
    "agent-protocol": ("agent", "swarm", "loop", "protocol", "worker", "synthesizer", "planner"),
    "elemental-system": ("element", "fire", "water", "earth", "air", "alchemy", "transmutation"),
    "void-and-collapse": ("void", "zero", "collapse", "seed", "compression", "nothing", "emptiness"),
    "higher-dimensional": ("dimension", "tesseract", "hypercube", "4d", "5d", "6d", "holographic"),
}

COUNCIL_MAP = {
    "manuscript-architecture": "Architect",
    "mathematical-kernel": "Mathematician",
    "voynich-analysis": "Decoder",
    "consciousness-framework": "Observer",
    "game-theory": "Strategist",
    "agent-protocol": "Operator",
    "elemental-system": "Alchemist",
    "void-and-collapse": "Mystic",
    "higher-dimensional": "Geometer",
}

# --- 6D Constants ---

CIVILIZATION_PHASES = {
    "SEED": {"fraction": "0/16", "description": "pre-existence, potential, void"},
    "SPROUT": {"fraction": "2/16", "description": "first emergence, initial structure"},
    "GROWTH": {"fraction": "6/16", "description": "expansion, differentiation, branching"},
    "HARVEST": {"fraction": "10/16", "description": "maturation, fruit-bearing, peak form"},
    "CLOSURE": {"fraction": "14/16", "description": "completion, integration, review"},
    "LIFT": {"fraction": "1/8", "description": "transcendence, dimensional fold, succession"},
}

SUCCESSION_ORDER = ["SEED", "SPROUT", "GROWTH", "HARVEST", "CLOSURE", "LIFT"]

# --- Emergent Chapter Mapping ---

ARC_TO_EMERGENT = {
    0: "E01",  # Ch01-Ch03 → E01 (The Seed)
    1: "E02",  # Ch04-Ch06 → E02 (The Mirror)
    2: "E03",  # Ch07-Ch09 → E03 (The Bridge)
    3: "E04",  # Ch10-Ch12 → E04 (The Lattice)
    4: "E05",  # Ch13-Ch15 → E05 (The Spiral)
    5: "E06",  # Ch16-Ch18 → E06 (The Prism)
    6: "E07",  # Ch19-Ch21 → E07 (The Wave)
}

EMERGENT_CHAPTERS = {
    "E01": {"title": "The Seed", "sources": ["Ch01", "Ch02", "Ch03"], "arc": 0},
    "E02": {"title": "The Mirror", "sources": ["Ch04", "Ch05", "Ch06"], "arc": 1},
    "E03": {"title": "The Bridge", "sources": ["Ch07", "Ch08", "Ch09"], "arc": 2},
    "E04": {"title": "The Lattice", "sources": ["Ch10", "Ch11", "Ch12"], "arc": 3},
    "E05": {"title": "The Spiral", "sources": ["Ch13", "Ch14", "Ch15"], "arc": 4},
    "E06": {"title": "The Prism", "sources": ["Ch16", "Ch17", "Ch18"], "arc": 5},
    "E07": {"title": "The Wave", "sources": ["Ch19", "Ch20", "Ch21"], "arc": 6},
    "E08": {"title": "The Axis", "sources": ["Rail_Su", "Rail_Me", "Rail_Sa"], "arc": -1},
    "E09": {"title": "The Zero", "sources": ["All"], "arc": -2},
}

# --- Reverse Appendix Mapping ---

REVERSE_APPENDIX_MAP = {
    "AppZ": "AppA", "AppY": "AppB", "AppX": "AppC", "AppW": "AppD",
    "AppV": "AppE", "AppU": "AppF", "AppT": "AppG", "AppS_rev": "AppH",
    "AppR_rev": "AppI", "AppQ_rev": "AppJ", "AppP_em": "AppK", "AppO_em": "AppL",
    "AppN_em": "AppM", "AppM_em": "AppN", "AppL_em": "AppO", "AppK_em": "AppP",
}

FORWARD_APPENDIX_MAP = {v: k for k, v in REVERSE_APPENDIX_MAP.items()}

# --- Möbius Bridge ---

MOBIUS_Q_GATES = {
    0: "Q.S1", 1: "Q.S2", 2: "Q.F1", 3: "Q.F2",
    4: "Q.C1", 5: "Q.C2", 6: "Q.R1",
    "rails": "Q.R2", "all": "Q.⊙",
}

MOBIUS_O_GATES = {
    "E01": "O.S1", "E02": "O.S2", "E03": "O.F1", "E04": "O.F2",
    "E05": "O.C1", "E06": "O.C2", "E07": "O.R1",
    "E08": "O.R2", "E09": "O.⊙",
}

MOBIUS_MODES = ("FIX", "CAR", "MUT")


@dataclass
class Coordinate5D:
    """5D coordinate: 4D tesseract + family/council axis."""
    chapter: str           # ChXX or E{NN}
    lens: str              # S, F, C, R
    facet: str             # 1, 2, 3, 4
    atom: str              # a, b, c, d
    family: str            # family name
    council: str           # council role

    @property
    def address(self) -> str:
        return f"{self.chapter}.{self.lens}{self.facet}.{self.atom}[{self.council}]"


@dataclass
class Coordinate6D:
    """6D coordinate: 5D + civilization/succession axis."""
    coord_5d: Coordinate5D
    phase: str             # SEED, SPROUT, GROWTH, HARVEST, CLOSURE, LIFT
    succession: int        # cycle number (0 = first crystal)

    @property
    def address(self) -> str:
        return f"{self.coord_5d.address}@{self.phase}/{self.succession}"


@dataclass
class EmergentRoutePlan:
    """Route plan for 5D emergent chapters."""
    emergent_chapter: str
    source_arc: int
    q_gate: str
    legacy_sources: list[str]
    hubs_5d: list[str]
    mobius_mode: str
    header_5d: str


@dataclass
class HolographicSeed:
    """The 6D holographic seed — compressed representation of entire corpus."""
    z0: str = "Z*"           # zero-point
    ae0: str = "Æ*"          # aether-point
    spin: str = "SP+"        # current spin direction
    mobius: str = "FIX"      # current Möbius mode
    symmetry_node: str = "Σ11"  # current symmetry position (Cosmos by default)
    element: str = "ALL"     # current elemental focus
    phase: str = "SEED"      # civilization phase


def score_family(text: str) -> str:
    """Score text against family keywords to determine 5D family coordinate."""
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for family, keywords in FAMILY_KEYWORDS.items():
        scores[family] = sum(text_lower.count(kw) for kw in keywords)
    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "manuscript-architecture"


def derive_council(family: str) -> str:
    """Map family to council role."""
    return COUNCIL_MAP.get(family, "Architect")


def derive_civilization_phase(omega: int, total: int = 21) -> str:
    """Compute civilization phase from orbit position."""
    fraction = omega / total
    if fraction < 0.1:
        return "SEED"
    elif fraction < 0.25:
        return "SPROUT"
    elif fraction < 0.45:
        return "GROWTH"
    elif fraction < 0.65:
        return "HARVEST"
    elif fraction < 0.85:
        return "CLOSURE"
    else:
        return "LIFT"


def legacy_to_emergent(chapter_code: str) -> str:
    """Map a legacy chapter to its emergent chapter via arc collapse."""
    chapter_num = int(chapter_code.replace("Ch", ""))
    arc = (chapter_num - 1) // 3
    return ARC_TO_EMERGENT.get(arc, "E09")


def emergent_to_legacy(emergent_code: str) -> list[str]:
    """Map an emergent chapter back to its legacy sources."""
    info = EMERGENT_CHAPTERS.get(emergent_code)
    if not info:
        return []
    return info["sources"]


def q_gate_for_arc(arc: int) -> str:
    """Get the Q-bridge gate for a given arc."""
    return MOBIUS_Q_GATES.get(arc, "Q.⊙")


def o_gate_for_emergent(emergent_code: str) -> str:
    """Get the O-bridge gate for a given emergent chapter."""
    return MOBIUS_O_GATES.get(emergent_code, "O.⊙")


def reverse_appendix(legacy_code: str) -> Optional[str]:
    """Get the reverse appendix mirror of a legacy appendix."""
    return FORWARD_APPENDIX_MAP.get(legacy_code)


def forward_appendix(reverse_code: str) -> Optional[str]:
    """Get the legacy appendix mirror of a reverse appendix."""
    return REVERSE_APPENDIX_MAP.get(reverse_code)


def build_5d_header(
    chapter_code: str,
    arc: int,
    rot: int,
    lane: str,
    family: str,
    council: str,
    omega: int,
) -> str:
    """Build the extended 5D tesseract header."""
    return (
        f"**[⊙Z_i↔Z* | ○Arc {arc} | ○Rot {rot} | △Lane {lane} | "
        f"⧈View 5D | ☆{council} | ω={omega}]**"
    )


def build_6d_header(
    chapter_code: str,
    arc: int,
    rot: int,
    lane: str,
    family: str,
    council: str,
    phase: str,
    omega: int,
) -> str:
    """Build the full 6D tesseract header."""
    return (
        f"**[⊙Z_i↔Z* | ○Arc {arc} | ○Rot {rot} | △Lane {lane} | "
        f"⧈View 6D | ☆{council} | ⏣{phase} | ω={omega}]**"
    )


def build_emergent_route(
    legacy_chapter_code: str,
    arc: int,
    family: str,
    mobius_mode: str = "CAR",
) -> EmergentRoutePlan:
    """Build a route from legacy chapter through Q-bridge to emergent chapter."""
    emergent = legacy_to_emergent(legacy_chapter_code)
    q_gate = q_gate_for_arc(arc)
    sources = emergent_to_legacy(emergent)
    council = derive_council(family)

    # 5D hub set: mandatory + arc hub + Q-bridge + emergent target
    hubs_5d = ["AppA", "AppI", "AppM", q_gate, emergent]

    header = build_5d_header(
        emergent, arc, arc % 3, "5D",
        family, council, int(emergent[1:]) + 100,
    )

    return EmergentRoutePlan(
        emergent_chapter=emergent,
        source_arc=arc,
        q_gate=q_gate,
        legacy_sources=sources,
        hubs_5d=hubs_5d,
        mobius_mode=mobius_mode,
        header_5d=header,
    )


def compress_to_seed(chapters: list[str]) -> HolographicSeed:
    """Compress a set of chapters to their holographic seed representation."""
    return HolographicSeed(
        z0="Z*",
        ae0="Æ*",
        spin="SP+" if len(chapters) % 2 == 1 else "SP-",
        mobius="FIX" if len(chapters) <= 3 else "CAR" if len(chapters) <= 9 else "MUT",
        symmetry_node=f"Σ{min(len(chapters), 15):02d}",
        element="ALL" if len(chapters) > 7 else ["FIRE", "WATER", "EARTH", "AIR"][len(chapters) % 4],
        phase=derive_civilization_phase(len(chapters) - 1, max(len(chapters), 1)),
    )


def expand_from_seed(seed: HolographicSeed, target_dimension: int = 4) -> dict:
    """Expand a holographic seed back toward a target dimension."""
    result = {
        "seed": seed,
        "target_dimension": target_dimension,
        "expansion_path": [],
    }

    if target_dimension >= 6:
        result["expansion_path"].append(f"6D: {seed.phase} phase, {seed.spin} spin")
    if target_dimension >= 5:
        result["expansion_path"].append(f"5D: Möbius {seed.mobius}, Symmetry {seed.symmetry_node}")
    if target_dimension >= 4:
        result["expansion_path"].append(f"4D: Element {seed.element}, Z0={seed.z0}")
    if target_dimension >= 3:
        result["expansion_path"].append("3D: Expand to legacy chapters via rail projection")

    return result


# --- Powers of 4 Ladder ---

def crystal_size(m: int, d: int) -> int:
    """Compute H_{m,d} = 4^{m*d}"""
    return 4 ** (m * d)


def dimensional_atoms(dimension: int) -> int:
    """Compute the number of atoms at a given dimensional level."""
    return {
        3: 21 * 64,    # 1,344 (legacy)
        4: 21 * 256,   # 5,376 (tesseract)
        5: 10 * 256,   # 2,560 (emergent)
        6: 1 * 1024,   # 1,024 (holographic)
    }.get(dimension, 0)


def compression_ratio(from_dim: int, to_dim: int) -> float:
    """Compute the compression ratio between dimensions."""
    from_atoms = dimensional_atoms(from_dim)
    to_atoms = dimensional_atoms(to_dim)
    if to_atoms == 0:
        return float('inf')
    return from_atoms / to_atoms


# --- Full Orbit Functions ---

def full_mobius_circuit() -> list[str]:
    """Return the complete Möbius circuit: A→P→Q→Z→K→O→A"""
    legacy = [f"App{chr(65+i)}" for i in range(16)]  # A through P
    bridge_in = ["AppQ"]
    reverse = [
        "AppZ", "AppY", "AppX", "AppW",
        "AppV", "AppU", "AppT", "AppS_rev",
        "AppR_rev", "AppQ_rev", "AppP_em", "AppO_em",
        "AppN_em", "AppM_em", "AppL_em", "AppK_em",
    ]
    bridge_out = ["AppO"]
    return legacy + bridge_in + reverse + bridge_out


if __name__ == "__main__":
    # Demo: compute coordinates for Ch11 (the center chapter)
    family = "manuscript-architecture"
    council = derive_council(family)
    phase = derive_civilization_phase(10, 21)

    print("=== 5D Coordinate Demo ===")
    coord5 = Coordinate5D("Ch11", "S", "1", "a", family, council)
    print(f"5D Address: {coord5.address}")
    print(f"5D Header: {build_5d_header('Ch11', 3, 0, 'Me', family, council, 10)}")

    print("\n=== 6D Coordinate Demo ===")
    coord6 = Coordinate6D(coord5, phase, 0)
    print(f"6D Address: {coord6.address}")
    print(f"6D Header: {build_6d_header('Ch11', 3, 0, 'Me', family, council, phase, 10)}")

    print("\n=== Emergent Route Demo ===")
    route = build_emergent_route("Ch11", 3, family)
    print(f"Emergent: {route.emergent_chapter}")
    print(f"Q-Gate: {route.q_gate}")
    print(f"Header: {route.header_5d}")

    print("\n=== Holographic Seed Demo ===")
    seed = compress_to_seed([f"Ch{i:02d}" for i in range(1, 22)])
    print(f"Seed: spin={seed.spin}, möbius={seed.mobius}, symmetry={seed.symmetry_node}")
    expanded = expand_from_seed(seed, 4)
    for step in expanded["expansion_path"]:
        print(f"  {step}")

    print("\n=== Crystal Mathematics ===")
    for d in range(3, 7):
        print(f"  {d}D atoms: {dimensional_atoms(d):,}")
    print(f"  3D→6D compression: {compression_ratio(3, 6):.1f}:1")
    print(f"  Möbius circuit length: {len(full_mobius_circuit())} stations")
