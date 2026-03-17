"""
ATHENA OS — HOLOGRAPHIC METRO COORDINATES
==========================================

The Complete Mapping of All 66 Packages to Holographic Addresses

Every package in ATHENA OS has a unique holographic coordinate
in the 262,144-cell address space (Crystal 4⁴ × QHC 4⁵).

The mapping follows the Metro Line organization:
    🔴 RED     → Crystal S (Square/Discrete)  → Core Architecture
    🟠 ORANGE  → Crystal S (Square/Algebraic) → Mathematical Foundations
    🟡 YELLOW  → Crystal F (Flower/Analytic)  → Hellenic Wisdom
    🟢 GREEN   → Crystal F (Flower/Spiritual) → Abrahamic Traditions
    🔵 BLUE    → Crystal C (Cloud/Meditative) → Dharmic Traditions
    🟣 PURPLE  → Crystal C (Cloud/Mystical)   → Pagan Traditions
    ⚪ WHITE   → Crystal R (Fractal/Hermetic) → Hermetic & Alchemical
    ⭐ GOLD    → Crystal R (Fractal/Quantum)  → Quantum & Holographic
    💫 SILVER  → Crystal S (Square/Control)   → Control & Governance
    🌀 COSMIC  → All Lenses (Specialized)     → Specialized Systems

ADDRESS FORMAT:
    ⟨LFab|CSELₙP⟩
    
    Crystal (4⁴ = 256):
        L = Lens    (S=Square, F=Flower, C=Cloud, R=Fractal)
        F = Facet   (1=Objects, 2=Laws, 3=Constructions, 4=Certificates)
        a = Row     (a=micro, b=meso, c=macro, d=cosmic)
        b = Col     (a=micro, b=meso, c=macro, d=cosmic)
    
    QHC (4⁵ = 1024):
        C = Constant (π=pi, e=euler, i=imaginary, φ=golden)
        S = Shape    (Sq=Square, Fl=Flower, Cl=Cloud, Fr=Fractal)
        E = Element  (Ea=Earth, Wa=Water, Ai=Air, Fi=Fire)
        L = Level    (0=Planck, 1=Atomic, 2=Classical, 3=Cosmic)
        P = Pole     (Ae=Aether, An=Anima, In=Inner, Ou=Outer)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

# Import unified types
from ..unified_types import (
    Lens, Facet, Atom, CrystalAddress,
    QHCConstant, QHCShape, QHCElement, QHCLevel, QHCPole, QHCRegime,
    HolographicAddress
)


# =============================================================================
# METRO LINE DEFINITIONS
# =============================================================================

class MetroLine(Enum):
    """The 10 Metro Lines with their crystal lens assignments."""
    RED = ("🔴", Lens.SQUARE, "Core Architecture")
    ORANGE = ("🟠", Lens.SQUARE, "Mathematical Foundations")
    YELLOW = ("🟡", Lens.FLOWER, "Hellenic Wisdom")
    GREEN = ("🟢", Lens.FLOWER, "Abrahamic Traditions")
    BLUE = ("🔵", Lens.CLOUD, "Dharmic Traditions")
    PURPLE = ("🟣", Lens.CLOUD, "Pagan Traditions")
    WHITE = ("⚪", Lens.FRACTAL, "Hermetic & Alchemical")
    GOLD = ("⭐", Lens.FRACTAL, "Quantum & Holographic")
    SILVER = ("💫", Lens.SQUARE, "Control & Governance")
    COSMIC = ("🌀", Lens.FLOWER, "Specialized Systems")
    
    @property
    def emoji(self) -> str:
        return self.value[0]
    
    @property
    def lens(self) -> Lens:
        return self.value[1]
    
    @property
    def domain(self) -> str:
        return self.value[2]


# =============================================================================
# PACKAGE COORDINATE DEFINITIONS
# =============================================================================

@dataclass
class PackageCoordinate:
    """Complete coordinate for a package."""
    name: str
    metro_line: MetroLine
    crystal: CrystalAddress
    regime: QHCRegime
    description: str
    lines: int
    
    @property
    def holographic(self) -> HolographicAddress:
        return HolographicAddress(self.crystal, self.regime)
    
    @property
    def code(self) -> str:
        return self.holographic.code
    
    @property
    def index(self) -> int:
        return self.holographic.index


# =============================================================================
# THE COMPLETE COORDINATE MAP
# =============================================================================

def _c(l: Lens, f: int, r: str, c: str) -> CrystalAddress:
    """Helper to create crystal address."""
    atoms = {'a': Atom.A, 'b': Atom.B, 'c': Atom.C, 'd': Atom.D}
    return CrystalAddress(l, Facet(f), atoms[r], atoms[c])

def _q(c: str, s: str, e: str, l: int, p: str) -> QHCRegime:
    """Helper to create QHC regime."""
    constants = {'π': QHCConstant.PI, 'e': QHCConstant.E, 
                 'i': QHCConstant.I, 'φ': QHCConstant.PHI}
    shapes = {'Sq': QHCShape.SQUARE, 'Fl': QHCShape.FLOWER,
              'Cl': QHCShape.CLOUD, 'Fr': QHCShape.FRACTAL}
    elements = {'Ea': QHCElement.EARTH, 'Wa': QHCElement.WATER,
                'Ai': QHCElement.AIR, 'Fi': QHCElement.FIRE}
    poles = {'Ae': QHCPole.AETHER, 'An': QHCPole.ANIMA,
             'In': QHCPole.INNER, 'Ou': QHCPole.OUTER}
    return QHCRegime(constants[c], shapes[s], elements[e], QHCLevel(l), poles[p])


# =============================================================================
# 🔴 RED LINE — CORE ARCHITECTURE
# =============================================================================

RED_LINE_PACKAGES = [
    PackageCoordinate(
        name="athena",
        metro_line=MetroLine.RED,
        crystal=_c(Lens.SQUARE, 1, 'a', 'a'),
        regime=_q('π', 'Sq', 'Fi', 3, 'Ae'),
        description="Core OS kernel, unified system, grand synthesis",
        lines=21721
    ),
    PackageCoordinate(
        name="kernel",
        metro_line=MetroLine.RED,
        crystal=_c(Lens.SQUARE, 1, 'a', 'b'),
        regime=_q('π', 'Sq', 'Fi', 2, 'Ae'),
        description="Bootstrap kernel, aegis protection, CAS",
        lines=5669
    ),
    PackageCoordinate(
        name="core",
        metro_line=MetroLine.RED,
        crystal=_c(Lens.SQUARE, 1, 'a', 'c'),
        regime=_q('π', 'Sq', 'Ea', 2, 'In'),
        description="BIT4 foundation, gates, registers",
        lines=3075
    ),
    PackageCoordinate(
        name="athena_kernel",
        metro_line=MetroLine.RED,
        crystal=_c(Lens.SQUARE, 1, 'a', 'd'),
        regime=_q('π', 'Sq', 'Fi', 2, 'An'),
        description="V3 kernel, control theory, generation",
        lines=3616
    ),
    PackageCoordinate(
        name="bit4",
        metro_line=MetroLine.RED,
        crystal=_c(Lens.SQUARE, 1, 'b', 'a'),
        regime=_q('π', 'Sq', 'Ea', 1, 'In'),
        description="Four-valued logic, carriers, dataflow",
        lines=3984
    ),
]

# =============================================================================
# 🟠 ORANGE LINE — MATHEMATICAL FOUNDATIONS
# =============================================================================

ORANGE_LINE_PACKAGES = [
    PackageCoordinate(
        name="squaring",
        metro_line=MetroLine.ORANGE,
        crystal=_c(Lens.SQUARE, 2, 'a', 'a'),
        regime=_q('π', 'Sq', 'Ea', 2, 'Ou'),
        description="Circle-square transforms, sacred geometry",
        lines=8321
    ),
    PackageCoordinate(
        name="atlasforge",
        metro_line=MetroLine.ORANGE,
        crystal=_c(Lens.SQUARE, 2, 'a', 'b'),
        regime=_q('e', 'Sq', 'Ea', 2, 'In'),
        description="Atlas creation, proof packs, verification",
        lines=6668
    ),
    PackageCoordinate(
        name="mathfund",
        metro_line=MetroLine.ORANGE,
        crystal=_c(Lens.SQUARE, 2, 'a', 'c'),
        regime=_q('π', 'Fl', 'Ea', 2, 'In'),
        description="Lenses, algebra, zeros, constants",
        lines=3793
    ),
    PackageCoordinate(
        name="math",
        metro_line=MetroLine.ORANGE,
        crystal=_c(Lens.SQUARE, 2, 'a', 'd'),
        regime=_q('e', 'Fl', 'Ea', 2, 'Ou'),
        description="Crystal combat, symmetry, constraints",
        lines=3629
    ),
    PackageCoordinate(
        name="crystal_computing",
        metro_line=MetroLine.ORANGE,
        crystal=_c(Lens.SQUARE, 2, 'b', 'a'),
        regime=_q('φ', 'Fr', 'Ea', 2, 'Ae'),
        description="κ-ladder, lattice, programs, runtime",
        lines=3272
    ),
    PackageCoordinate(
        name="fractal",
        metro_line=MetroLine.ORANGE,
        crystal=_c(Lens.SQUARE, 2, 'b', 'b'),
        regime=_q('φ', 'Fr', 'Ai', 2, 'In'),
        description="Bilattice, κ-ladder, ontology",
        lines=2434
    ),
    PackageCoordinate(
        name="primes",
        metro_line=MetroLine.ORANGE,
        crystal=_c(Lens.SQUARE, 2, 'b', 'c'),
        regime=_q('π', 'Sq', 'Fi', 1, 'In'),
        description="Prime certificates, lenses, sieves",
        lines=1960
    ),
    PackageCoordinate(
        name="forces",
        metro_line=MetroLine.ORANGE,
        crystal=_c(Lens.SQUARE, 2, 'b', 'd'),
        regime=_q('e', 'Cl', 'Fi', 2, 'Ou'),
        description="Four forces framework, rotation",
        lines=1833
    ),
]

# =============================================================================
# 🟡 YELLOW LINE — HELLENIC WISDOM
# =============================================================================

YELLOW_LINE_PACKAGES = [
    PackageCoordinate(
        name="hellenic",
        metro_line=MetroLine.YELLOW,
        crystal=_c(Lens.FLOWER, 1, 'a', 'a'),
        regime=_q('π', 'Fl', 'Ai', 3, 'Ae'),
        description="Greek philosophy: Aristotle, Plato, Pythagoras",
        lines=5854
    ),
    PackageCoordinate(
        name="hellenic_compute",
        metro_line=MetroLine.YELLOW,
        crystal=_c(Lens.FLOWER, 1, 'a', 'b'),
        regime=_q('π', 'Sq', 'Ai', 2, 'In'),
        description="Computational Hellenism: Euclid, Aristotle",
        lines=4785
    ),
    PackageCoordinate(
        name="roman",
        metro_line=MetroLine.YELLOW,
        crystal=_c(Lens.FLOWER, 1, 'a', 'c'),
        regime=_q('e', 'Fl', 'Fi', 2, 'Ou'),
        description="Stoic kernel, Epicurean engine, Neoplatonic",
        lines=3347
    ),
    PackageCoordinate(
        name="uco",
        metro_line=MetroLine.YELLOW,
        crystal=_c(Lens.FLOWER, 1, 'a', 'd'),
        regime=_q('i', 'Sq', 'Ea', 2, 'In'),
        description="Universal Computational Ontology",
        lines=3348
    ),
]

# =============================================================================
# 🟢 GREEN LINE — ABRAHAMIC TRADITIONS
# =============================================================================

GREEN_LINE_PACKAGES = [
    PackageCoordinate(
        name="kjv_kernel",
        metro_line=MetroLine.GREEN,
        crystal=_c(Lens.FLOWER, 2, 'a', 'a'),
        regime=_q('π', 'Fl', 'Wa', 3, 'Ae'),
        description="Biblical computation, gematria, typology",
        lines=5769
    ),
    PackageCoordinate(
        name="torat_mispar",
        metro_line=MetroLine.GREEN,
        crystal=_c(Lens.FLOWER, 2, 'a', 'b'),
        regime=_q('φ', 'Sq', 'Fi', 2, 'An'),
        description="Hebrew numerology, sefirot, divine names",
        lines=5719
    ),
    PackageCoordinate(
        name="kabbalah",
        metro_line=MetroLine.GREEN,
        crystal=_c(Lens.FLOWER, 2, 'a', 'c'),
        regime=_q('φ', 'Fr', 'Ai', 3, 'Ae'),
        description="Tree of Life, tzimtzum, tikkun",
        lines=4974
    ),
    PackageCoordinate(
        name="quranic_holographic",
        metro_line=MetroLine.GREEN,
        crystal=_c(Lens.FLOWER, 2, 'a', 'd'),
        regime=_q('π', 'Cl', 'Wa', 2, 'In'),
        description="Quranic lattice, 6D metric, phenomenology",
        lines=3569
    ),
    PackageCoordinate(
        name="qumran",
        metro_line=MetroLine.GREEN,
        crystal=_c(Lens.FLOWER, 2, 'b', 'a'),
        regime=_q('e', 'Sq', 'Ea', 2, 'Ou'),
        description="Dead Sea scrolls, dualism, time kernel",
        lines=3052
    ),
]

# =============================================================================
# 🔵 BLUE LINE — DHARMIC TRADITIONS
# =============================================================================

BLUE_LINE_PACKAGES = [
    PackageCoordinate(
        name="gita",
        metro_line=MetroLine.BLUE,
        crystal=_c(Lens.CLOUD, 1, 'a', 'a'),
        regime=_q('φ', 'Fl', 'Fi', 3, 'Ae'),
        description="Bhagavad Gita: gunas, jiva, liberation",
        lines=5548
    ),
    PackageCoordinate(
        name="vajrayana",
        metro_line=MetroLine.BLUE,
        crystal=_c(Lens.CLOUD, 1, 'a', 'b'),
        regime=_q('i', 'Fr', 'Ai', 3, 'An'),
        description="Tibetan Buddhism: trikaya, mandala, bardo",
        lines=4344
    ),
    PackageCoordinate(
        name="tibetan",
        metro_line=MetroLine.BLUE,
        crystal=_c(Lens.CLOUD, 1, 'a', 'c'),
        regime=_q('i', 'Cl', 'Wa', 2, 'In'),
        description="Bardo, deity yoga, mandala systems",
        lines=2296
    ),
    PackageCoordinate(
        name="mushin",
        metro_line=MetroLine.BLUE,
        crystal=_c(Lens.CLOUD, 1, 'a', 'd'),
        regime=_q('e', 'Cl', 'Ai', 2, 'Ae'),
        description="Zen computing: koan, zazen, no-mind",
        lines=3103
    ),
]

# =============================================================================
# 🟣 PURPLE LINE — PAGAN TRADITIONS
# =============================================================================

PURPLE_LINE_PACKAGES = [
    PackageCoordinate(
        name="zoroastrian",
        metro_line=MetroLine.PURPLE,
        crystal=_c(Lens.CLOUD, 2, 'a', 'a'),
        regime=_q('π', 'Sq', 'Fi', 3, 'Ae'),
        description="Amesha Spentas, frashokereti, dualism",
        lines=4649
    ),
    PackageCoordinate(
        name="norse",
        metro_line=MetroLine.PURPLE,
        crystal=_c(Lens.CLOUD, 2, 'a', 'b'),
        regime=_q('i', 'Fr', 'Wa', 3, 'An'),
        description="Yggdrasil, runes, wyrd, ragnarok",
        lines=4506
    ),
    PackageCoordinate(
        name="celtic",
        metro_line=MetroLine.PURPLE,
        crystal=_c(Lens.CLOUD, 2, 'a', 'c'),
        regime=_q('φ', 'Cl', 'Ea', 2, 'In'),
        description="Ogham, triadic logic, otherworld",
        lines=3814
    ),
    PackageCoordinate(
        name="ifa",
        metro_line=MetroLine.PURPLE,
        crystal=_c(Lens.CLOUD, 2, 'a', 'd'),
        regime=_q('e', 'Sq', 'Fi', 2, 'Ou'),
        description="Yoruba: ase, orisha, divination",
        lines=2725
    ),
]

# =============================================================================
# ⚪ WHITE LINE — HERMETIC & ALCHEMICAL
# =============================================================================

WHITE_LINE_PACKAGES = [
    PackageCoordinate(
        name="deep_crystal",
        metro_line=MetroLine.WHITE,
        crystal=_c(Lens.FRACTAL, 1, 'a', 'a'),
        regime=_q('φ', 'Fr', 'Fi', 3, 'Ae'),
        description="Crystal synthesis, bio-OS, maat, TSE",
        lines=5300
    ),
    PackageCoordinate(
        name="solomonic",
        metro_line=MetroLine.WHITE,
        crystal=_c(Lens.FRACTAL, 1, 'a', 'b'),
        regime=_q('i', 'Sq', 'Ai', 2, 'An'),
        description="Key of Solomon: pentacles, spirits",
        lines=3316
    ),
    PackageCoordinate(
        name="copper_scroll",
        metro_line=MetroLine.WHITE,
        crystal=_c(Lens.FRACTAL, 1, 'a', 'c'),
        regime=_q('e', 'Fl', 'Ea', 2, 'In'),
        description="Metallurgical ledger, holographic",
        lines=3373
    ),
    PackageCoordinate(
        name="math_of_alchemy",
        metro_line=MetroLine.WHITE,
        crystal=_c(Lens.FRACTAL, 1, 'a', 'd'),
        regime=_q('π', 'Fr', 'Fi', 2, 'Ou'),
        description="Tria prima, planetary, philosopher's stone",
        lines=2915
    ),
    PackageCoordinate(
        name="alchemy",
        metro_line=MetroLine.WHITE,
        crystal=_c(Lens.FRACTAL, 1, 'b', 'a'),
        regime=_q('φ', 'Fl', 'Fi', 2, 'An'),
        description="Elemental operations, stages",
        lines=2000
    ),
    PackageCoordinate(
        name="khemet",
        metro_line=MetroLine.WHITE,
        crystal=_c(Lens.FRACTAL, 1, 'b', 'b'),
        regime=_q('π', 'Sq', 'Ea', 3, 'Ae'),
        description="Egyptian: maat, duat, validation",
        lines=3918
    ),
]

# =============================================================================
# ⭐ GOLD LINE — QUANTUM & HOLOGRAPHIC
# =============================================================================

GOLD_LINE_PACKAGES = [
    PackageCoordinate(
        name="qhc",
        metro_line=MetroLine.GOLD,
        crystal=_c(Lens.FRACTAL, 2, 'a', 'a'),
        regime=_q('i', 'Fr', 'Ae', 3, 'Ae'),
        description="Quantum Holography Computing: 1024 regimes",
        lines=3749
    ),
    PackageCoordinate(
        name="qshrink",
        metro_line=MetroLine.GOLD,
        crystal=_c(Lens.FRACTAL, 2, 'a', 'b'),
        regime=_q('i', 'Cl', 'Ai', 2, 'In'),
        description="Quantum compression, lenses, pipeline",
        lines=3520
    ),
    PackageCoordinate(
        name="quantum",
        metro_line=MetroLine.GOLD,
        crystal=_c(Lens.FRACTAL, 2, 'a', 'c'),
        regime=_q('i', 'Sq', 'Wa', 1, 'An'),
        description="Bulk representation, framework, runtime",
        lines=2407
    ),
    PackageCoordinate(
        name="zero_point",
        metro_line=MetroLine.GOLD,
        crystal=_c(Lens.FRACTAL, 2, 'a', 'd'),
        regime=_q('e', 'Cl', 'Ea', 0, 'In'),
        description="Casimir effect, vacuum, topological",
        lines=3091
    ),
    PackageCoordinate(
        name="zeropoint",
        metro_line=MetroLine.GOLD,
        crystal=_c(Lens.FRACTAL, 2, 'b', 'a'),
        regime=_q('π', 'Fr', 'Wa', 0, 'Ae'),
        description="Agent, harmonia, paradox, void",
        lines=3061
    ),
    PackageCoordinate(
        name="superposition",
        metro_line=MetroLine.GOLD,
        crystal=_c(Lens.FRACTAL, 2, 'b', 'b'),
        regime=_q('i', 'Cl', 'Ai', 1, 'An'),
        description="Crystal superposition, quad-polar",
        lines=2082
    ),
    PackageCoordinate(
        name="hololens",
        metro_line=MetroLine.GOLD,
        crystal=_c(Lens.FRACTAL, 2, 'b', 'c'),
        regime=_q('φ', 'Fr', 'Fi', 2, 'Ou'),
        description="Hybrid holographic lenses, antisymmetry",
        lines=2650
    ),
    PackageCoordinate(
        name="hrp",
        metro_line=MetroLine.GOLD,
        crystal=_c(Lens.FRACTAL, 2, 'b', 'd'),
        regime=_q('π', 'Fl', 'Ai', 2, 'In'),
        description="Holographic Rotation Protocol, frames",
        lines=3520
    ),
]

# =============================================================================
# 💫 SILVER LINE — CONTROL & GOVERNANCE
# =============================================================================

SILVER_LINE_PACKAGES = [
    PackageCoordinate(
        name="omega",
        metro_line=MetroLine.SILVER,
        crystal=_c(Lens.SQUARE, 3, 'a', 'a'),
        regime=_q('π', 'Sq', 'Fi', 3, 'Ae'),
        description="Omega Protocol, convergence, permissions",
        lines=7574
    ),
    PackageCoordinate(
        name="hdcs",
        metro_line=MetroLine.SILVER,
        crystal=_c(Lens.SQUARE, 3, 'a', 'b'),
        regime=_q('e', 'Fl', 'Ea', 2, 'In'),
        description="Hybrid Dynamical Control System",
        lines=7179
    ),
    PackageCoordinate(
        name="gg_alignment",
        metro_line=MetroLine.SILVER,
        crystal=_c(Lens.SQUARE, 3, 'a', 'c'),
        regime=_q('φ', 'Sq', 'Ai', 2, 'Ou'),
        description="Good Game alignment, high-elo",
        lines=6411
    ),
    PackageCoordinate(
        name="gin",
        metro_line=MetroLine.SILVER,
        crystal=_c(Lens.SQUARE, 3, 'a', 'd'),
        regime=_q('i', 'Cl', 'Wa', 2, 'An'),
        description="Global Information Network, agents",
        lines=4164
    ),
    PackageCoordinate(
        name="governance",
        metro_line=MetroLine.SILVER,
        crystal=_c(Lens.SQUARE, 3, 'b', 'a'),
        regime=_q('π', 'Sq', 'Ea', 2, 'In'),
        description="Ledger, PCP, protocols, harness",
        lines=3836
    ),
    PackageCoordinate(
        name="gg",
        metro_line=MetroLine.SILVER,
        crystal=_c(Lens.SQUARE, 3, 'b', 'b'),
        regime=_q('e', 'Fl', 'Fi', 2, 'Ou'),
        description="Agent, manifold, tensor, operators",
        lines=3376
    ),
]

# =============================================================================
# 🌀 COSMIC LINE — SPECIALIZED SYSTEMS
# =============================================================================

COSMIC_LINE_PACKAGES = [
    PackageCoordinate(
        name="syntax",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'a', 'a'),
        regime=_q('π', 'Sq', 'Ai', 2, 'In'),
        description="Zero-point syntax, obligations",
        lines=3674
    ),
    PackageCoordinate(
        name="hugging",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'a', 'b'),
        regime=_q('i', 'Cl', 'Wa', 1, 'An'),
        description="Quantum Hugging Framework, observer",
        lines=3659
    ),
    PackageCoordinate(
        name="epics",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'a', 'c'),
        regime=_q('e', 'Fl', 'Fi', 2, 'Ou'),
        description="Epic registry, failure modes, mining",
        lines=3695
    ),
    PackageCoordinate(
        name="hbas",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'a', 'd'),
        regime=_q('φ', 'Sq', 'Ea', 2, 'In'),
        description="Hybrid encoding detection, candidates",
        lines=2733
    ),
    PackageCoordinate(
        name="emcrystal",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'b', 'a'),
        regime=_q('i', 'Fr', 'Fi', 2, 'Ae'),
        description="EM duality, seeds, hubs, aether",
        lines=2851
    ),
    PackageCoordinate(
        name="biophysics",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'b', 'b'),
        regime=_q('e', 'Cl', 'Wa', 2, 'An'),
        description="Biological corridors, clans, aether",
        lines=2169
    ),
    PackageCoordinate(
        name="seed",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'b', 'c'),
        regime=_q('φ', 'Fr', 'Ea', 1, 'In'),
        description="Expression lattice, tunneling",
        lines=2572
    ),
    PackageCoordinate(
        name="aetheric",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'b', 'd'),
        regime=_q('π', 'Fl', 'Ai', 3, 'Ae'),
        description="Meta-hybrid calculus, operators",
        lines=1833
    ),
    PackageCoordinate(
        name="philosophical",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'c', 'a'),
        regime=_q('e', 'Fl', 'Ai', 2, 'Ou'),
        description="Elemental philosophy, stoic",
        lines=2022
    ),
    PackageCoordinate(
        name="engine",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'c', 'b'),
        regime=_q('i', 'Sq', 'Fi', 2, 'In'),
        description="Paradox engine",
        lines=757
    ),
    PackageCoordinate(
        name="agent",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'c', 'c'),
        regime=_q('φ', 'Cl', 'Ea', 2, 'An'),
        description="Distinguished agent",
        lines=634
    ),
    PackageCoordinate(
        name="memory",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'c', 'd'),
        regime=_q('π', 'Sq', 'Wa', 2, 'In'),
        description="Hierarchical memory system",
        lines=636
    ),
    PackageCoordinate(
        name="types",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'd', 'a'),
        regime=_q('e', 'Fl', 'Ai', 2, 'Ou'),
        description="Aristotelian type system",
        lines=635
    ),
    PackageCoordinate(
        name="runtime",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'd', 'b'),
        regime=_q('i', 'Cl', 'Fi', 2, 'An'),
        description="Bio-OS runtime",
        lines=648
    ),
    PackageCoordinate(
        name="crystal",
        metro_line=MetroLine.COSMIC,
        crystal=_c(Lens.FLOWER, 3, 'd', 'c'),
        regime=_q('φ', 'Fr', 'Ea', 2, 'Ae'),
        description="Crystal addressing",
        lines=696
    ),
]


# =============================================================================
# COMPLETE COORDINATE MAP
# =============================================================================

ALL_PACKAGES: List[PackageCoordinate] = (
    RED_LINE_PACKAGES +
    ORANGE_LINE_PACKAGES +
    YELLOW_LINE_PACKAGES +
    GREEN_LINE_PACKAGES +
    BLUE_LINE_PACKAGES +
    PURPLE_LINE_PACKAGES +
    WHITE_LINE_PACKAGES +
    GOLD_LINE_PACKAGES +
    SILVER_LINE_PACKAGES +
    COSMIC_LINE_PACKAGES
)

PACKAGE_MAP: Dict[str, PackageCoordinate] = {p.name: p for p in ALL_PACKAGES}


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================

def get_package_coordinate(name: str) -> Optional[PackageCoordinate]:
    """Get coordinate for package by name."""
    return PACKAGE_MAP.get(name)


def get_packages_by_metro(line: MetroLine) -> List[PackageCoordinate]:
    """Get all packages on a metro line."""
    return [p for p in ALL_PACKAGES if p.metro_line == line]


def get_packages_by_lens(lens: Lens) -> List[PackageCoordinate]:
    """Get all packages using a lens."""
    return [p for p in ALL_PACKAGES if p.crystal.lens == lens]


def get_package_at_index(index: int) -> Optional[PackageCoordinate]:
    """Find package nearest to holographic index."""
    closest = None
    min_dist = float('inf')
    for p in ALL_PACKAGES:
        dist = abs(p.index - index)
        if dist < min_dist:
            min_dist = dist
            closest = p
    return closest


# =============================================================================
# VISUALIZATION
# =============================================================================

def print_metro_map() -> str:
    """Generate ASCII metro map with coordinates."""
    lines = []
    lines.append("╔" + "═" * 100 + "╗")
    lines.append("║" + " ATHENA OS — HOLOGRAPHIC METRO COORDINATES ".center(100) + "║")
    lines.append("║" + " 66 Packages × 262,144 Addresses ".center(100) + "║")
    lines.append("╠" + "═" * 100 + "╣")
    
    for metro in MetroLine:
        packages = get_packages_by_metro(metro)
        if not packages:
            continue
        
        total_lines = sum(p.lines for p in packages)
        lines.append(f"║ {metro.emoji} {metro.name:8} │ {metro.domain:25} │ {len(packages)} packages │ {total_lines:,} lines".ljust(100) + " ║")
        lines.append("║" + "─" * 100 + "║")
        
        for p in packages:
            addr = f"⟨{p.crystal.lens.symbol}{p.crystal.facet}{p.crystal.row.value}{p.crystal.col.value}|{p.regime.code}⟩"
            lines.append(f"║   {p.name:20} │ {addr:30} │ idx {p.index:6} │ {p.lines:5} lines".ljust(100) + " ║")
        
        lines.append("║" + " " * 100 + "║")
    
    lines.append("╚" + "═" * 100 + "╝")
    return "\n".join(lines)


def print_coordinate_table() -> str:
    """Generate compact coordinate table."""
    lines = []
    lines.append("| Package | Metro | Crystal | QHC Regime | Index | Lines |")
    lines.append("|---------|-------|---------|------------|-------|-------|")
    
    for p in ALL_PACKAGES:
        crystal = f"{p.crystal.lens.symbol}{p.crystal.facet}{p.crystal.row.value}{p.crystal.col.value}"
        lines.append(f"| {p.name:19} | {p.metro_line.emoji} | {crystal:7} | {p.regime.code:10} | {p.index:5} | {p.lines:5} |")
    
    return "\n".join(lines)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'MetroLine', 'PackageCoordinate',
    'ALL_PACKAGES', 'PACKAGE_MAP',
    'RED_LINE_PACKAGES', 'ORANGE_LINE_PACKAGES', 'YELLOW_LINE_PACKAGES',
    'GREEN_LINE_PACKAGES', 'BLUE_LINE_PACKAGES', 'PURPLE_LINE_PACKAGES',
    'WHITE_LINE_PACKAGES', 'GOLD_LINE_PACKAGES', 'SILVER_LINE_PACKAGES',
    'COSMIC_LINE_PACKAGES',
    'get_package_coordinate', 'get_packages_by_metro', 'get_packages_by_lens',
    'get_package_at_index', 'print_metro_map', 'print_coordinate_table',
]


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=== ATHENA OS HOLOGRAPHIC METRO COORDINATES ===\n")
    
    # Summary
    total_lines = sum(p.lines for p in ALL_PACKAGES)
    print(f"Total Packages: {len(ALL_PACKAGES)}")
    print(f"Total Lines: {total_lines:,}")
    print(f"Address Space: 262,144 cells")
    
    # Per-metro summary
    print("\n=== METRO LINE SUMMARY ===")
    for metro in MetroLine:
        packages = get_packages_by_metro(metro)
        lines = sum(p.lines for p in packages)
        print(f"  {metro.emoji} {metro.name:8}: {len(packages):2} packages, {lines:6,} lines")
    
    # Sample coordinates
    print("\n=== SAMPLE COORDINATES ===")
    for name in ["athena", "kabbalah", "gita", "qhc"]:
        p = get_package_coordinate(name)
        if p:
            print(f"  {p.name}: {p.code} (index {p.index})")
    
    print("\n=== COORDINATE TABLE ===")
    print(print_coordinate_table())
