"""
ATHENA OS — META PACKAGE REGISTRY
=================================

The complete registry of all 66 packages organized by tradition/tier.

This module provides:
1. Package metadata (name, description, lines, files)
2. Cross-package dependencies
3. Type mapping to unified core
4. Metro line assignments
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum, auto


# =============================================================================
# METRO LINES — THE 10 ORGANIZATIONAL TIERS
# =============================================================================

class MetroLine(Enum):
    """The 10 Metro Lines organizing ATHENA OS packages."""
    
    RED = "Core Architecture"
    ORANGE = "Mathematical Foundations"
    YELLOW = "Hellenic Wisdom"
    GREEN = "Abrahamic Traditions"
    BLUE = "Dharmic Traditions"
    PURPLE = "Pagan Traditions"
    WHITE = "Hermetic & Alchemical"
    GOLD = "Quantum & Holographic"
    SILVER = "Control & Governance"
    COSMIC = "Specialized Systems"


# =============================================================================
# TRADITION — SPIRITUAL/PHILOSOPHICAL SOURCE
# =============================================================================

class Tradition(Enum):
    """Source tradition for each package."""
    
    CORE = "Core System"
    GREEK = "Hellenic"
    ROMAN = "Roman"
    HEBREW = "Hebrew/Jewish"
    CHRISTIAN = "Christian"
    ISLAMIC = "Islamic"
    HINDU = "Hindu"
    BUDDHIST = "Buddhist"
    ZEN = "Zen Buddhism"
    NORSE = "Norse/Germanic"
    CELTIC = "Celtic"
    EGYPTIAN = "Egyptian"
    YORUBA = "Yoruba/Ifa"
    ZOROASTRIAN = "Zoroastrian"
    HERMETIC = "Hermetic/Alchemical"
    MATHEMATICAL = "Pure Mathematics"
    QUANTUM = "Quantum Physics"
    CONTROL = "Control Theory"


# =============================================================================
# PACKAGE METADATA
# =============================================================================

@dataclass
class PackageInfo:
    """Metadata for a single package."""
    
    name: str
    description: str
    metro_line: MetroLine
    tradition: Tradition
    lines: int
    files: int
    dependencies: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    unified_types_used: List[str] = field(default_factory=list)


# =============================================================================
# THE COMPLETE PACKAGE REGISTRY
# =============================================================================

PACKAGE_REGISTRY: Dict[str, PackageInfo] = {
    # =========================================================================
    # TIER I — RED LINE: CORE ARCHITECTURE (36,000+ lines)
    # =========================================================================
    
    "athena": PackageInfo(
        name="athena",
        description="Core OS kernel, unified system, grand synthesis",
        metro_line=MetroLine.RED,
        tradition=Tradition.CORE,
        lines=21721,
        files=32,
        dependencies=["core", "kernel", "bit4"],
        exports=["ATHENA_OS", "ATHENABootSequence", "HardwareSubstrate", "ComputationalKernel"],
        unified_types_used=["B4", "Element", "TypedTruth", "Certificate", "Ledger"]
    ),
    
    "kernel": PackageInfo(
        name="kernel",
        description="Bootstrap kernel, aegis protection, CAS, thermal control",
        metro_line=MetroLine.RED,
        tradition=Tradition.CORE,
        lines=5669,
        files=9,
        dependencies=["core", "bit4"],
        exports=["Aegis", "CAS", "ThermalController", "InstructionSet"],
        unified_types_used=["B4", "Certificate", "Corridor"]
    ),
    
    "core": PackageInfo(
        name="core",
        description="BIT4 foundation, gates, registers, integration",
        metro_line=MetroLine.RED,
        tradition=Tradition.CORE,
        lines=3075,
        files=6,
        dependencies=["bit4"],
        exports=["RegisterFile", "GateMatrix", "ProcessingDAG"],
        unified_types_used=["B4", "Klein4Op", "TypedTruth"]
    ),
    
    "athena_kernel": PackageInfo(
        name="athena_kernel",
        description="V3 kernel, control theory, generation operators",
        metro_line=MetroLine.RED,
        tradition=Tradition.CORE,
        lines=3616,
        files=6,
        dependencies=["athena", "kernel"],
        exports=["V3Kernel", "ControlTheory", "Generation"],
        unified_types_used=["B4", "Operator", "Ledger"]
    ),
    
    "bit4": PackageInfo(
        name="bit4",
        description="Four-valued logic, carriers, dataflow, gates",
        metro_line=MetroLine.RED,
        tradition=Tradition.CORE,
        lines=3984,
        files=8,
        dependencies=[],
        exports=["B4", "TwoRail", "B4Vector", "B4Word", "CollapsePolicy"],
        unified_types_used=["B4", "Klein4Op"]
    ),
    
    # =========================================================================
    # TIER II — ORANGE LINE: MATHEMATICAL FOUNDATIONS (29,000+ lines)
    # =========================================================================
    
    "squaring": PackageInfo(
        name="squaring",
        description="Circle-square transforms, cosmology, sacred geometry",
        metro_line=MetroLine.ORANGE,
        tradition=Tradition.MATHEMATICAL,
        lines=8321,
        files=13,
        dependencies=["mathfund", "core"],
        exports=["CircleSystem", "SquareSystem", "Vitruvian", "Mandala"],
        unified_types_used=["Lens", "Element", "CrystalAddress"]
    ),
    
    "atlasforge": PackageInfo(
        name="atlasforge",
        description="Atlas creation, proof packs, verification, recipes",
        metro_line=MetroLine.ORANGE,
        tradition=Tradition.MATHEMATICAL,
        lines=6668,
        files=11,
        dependencies=["core", "mathfund"],
        exports=["Atlas", "ProofPack", "Recipe", "VerifierKernel"],
        unified_types_used=["Certificate", "TypedTruth", "ZResult"]
    ),
    
    "mathfund": PackageInfo(
        name="mathfund",
        description="Lenses, algebra, zeros, constants, operations",
        metro_line=MetroLine.ORANGE,
        tradition=Tradition.MATHEMATICAL,
        lines=3793,
        files=7,
        dependencies=["core"],
        exports=["Lens", "ZeroCalculus", "Constants", "Compiler"],
        unified_types_used=["Lens", "ZResult", "Constants"]
    ),
    
    "math": PackageInfo(
        name="math",
        description="Crystal combat, symmetry, constraints, zeros",
        metro_line=MetroLine.ORANGE,
        tradition=Tradition.MATHEMATICAL,
        lines=3629,
        files=6,
        dependencies=["mathfund"],
        exports=["CrystalCombat", "Symmetry", "Constraint"],
        unified_types_used=["Lens", "Element", "TypedTruth"]
    ),
    
    "crystal_computing": PackageInfo(
        name="crystal_computing",
        description="κ-ladder, lattice, programs, runtime",
        metro_line=MetroLine.ORANGE,
        tradition=Tradition.MATHEMATICAL,
        lines=3272,
        files=7,
        dependencies=["core", "mathfund"],
        exports=["KappaField", "CrystalCell", "MetaCrystal", "CrystalRuntime"],
        unified_types_used=["CrystalAddress", "B4", "Operator"]
    ),
    
    "fractal": PackageInfo(
        name="fractal",
        description="Bilattice, κ-ladder, ontology, omega",
        metro_line=MetroLine.ORANGE,
        tradition=Tradition.MATHEMATICAL,
        lines=2434,
        files=5,
        dependencies=["mathfund", "crystal_computing"],
        exports=["Bilattice", "KappaLadder", "Ontology"],
        unified_types_used=["Lens", "ZResult"]
    ),
    
    "primes": PackageInfo(
        name="primes",
        description="Prime certificates, lenses, sieves",
        metro_line=MetroLine.ORANGE,
        tradition=Tradition.MATHEMATICAL,
        lines=1960,
        files=3,
        dependencies=["mathfund"],
        exports=["PrimeCertificate", "Sieve", "PrimeLens"],
        unified_types_used=["Certificate", "Lens", "ZResult"]
    ),
    
    "forces": PackageInfo(
        name="forces",
        description="Four forces framework, rotation, implementations",
        metro_line=MetroLine.ORANGE,
        tradition=Tradition.MATHEMATICAL,
        lines=1833,
        files=4,
        dependencies=["core"],
        exports=["ForceFramework", "Rotation", "Certificate"],
        unified_types_used=["Element", "Certificate", "Operator"]
    ),
    
    # =========================================================================
    # TIER III — YELLOW LINE: HELLENIC WISDOM (19,000+ lines)
    # =========================================================================
    
    "hellenic": PackageInfo(
        name="hellenic",
        description="Greek philosophy: Aristotelian, Platonic, Pythagorean, Stoic",
        metro_line=MetroLine.YELLOW,
        tradition=Tradition.GREEK,
        lines=5854,
        files=9,
        dependencies=["core"],
        exports=["Aristotelian", "Platonic", "Pythagorean", "Stoic", "Hippocratic"],
        unified_types_used=["Cause", "Category", "Element", "Humor"]
    ),
    
    "hellenic_compute": PackageInfo(
        name="hellenic_compute",
        description="Computational Hellenism: Euclid, Pythagoras, Plato, Aristotle",
        metro_line=MetroLine.YELLOW,
        tradition=Tradition.GREEK,
        lines=4785,
        files=8,
        dependencies=["hellenic", "core"],
        exports=["EuclidCompute", "PythagorasCompute", "AristotleCompute"],
        unified_types_used=["Cause", "Category", "Operator"]
    ),
    
    "roman": PackageInfo(
        name="roman",
        description="Stoic kernel, Epicurean engine, Neoplatonic stack, Skeptical debugger",
        metro_line=MetroLine.YELLOW,
        tradition=Tradition.ROMAN,
        lines=3347,
        files=5,
        dependencies=["hellenic"],
        exports=["StoicKernel", "EpicureanEngine", "NeoplatonicStack"],
        unified_types_used=["Element", "Cause", "TypedTruth"]
    ),
    
    "uco": PackageInfo(
        name="uco",
        description="Universal Computational Ontology, sexagesimal, logic kernel",
        metro_line=MetroLine.YELLOW,
        tradition=Tradition.GREEK,
        lines=3348,
        files=5,
        dependencies=["hellenic", "core"],
        exports=["LogicKernel", "Sexagesimal", "Substrate"],
        unified_types_used=["Category", "B4", "Operator"]
    ),
    
    # =========================================================================
    # TIER IV — GREEN LINE: ABRAHAMIC TRADITIONS (26,000+ lines)
    # =========================================================================
    
    "kjv_kernel": PackageInfo(
        name="kjv_kernel",
        description="Biblical computation, gematria, Strong's, typology, prophecy",
        metro_line=MetroLine.GREEN,
        tradition=Tradition.CHRISTIAN,
        lines=5769,
        files=11,
        dependencies=["core", "kabbalah"],
        exports=["GematriaEngine", "StrongsIndex", "Typology", "ProphecyEngine"],
        unified_types_used=["Certificate", "TypedTruth", "Ledger"]
    ),
    
    "torat_mispar": PackageInfo(
        name="torat_mispar",
        description="Hebrew numerology, sefirot, tzimtzum, tikkun, divine names",
        metro_line=MetroLine.GREEN,
        tradition=Tradition.HEBREW,
        lines=5719,
        files=11,
        dependencies=["kabbalah"],
        exports=["Gematria", "Sefirot", "Tzimtzum", "Tikkun", "DivineNames"],
        unified_types_used=["Element", "Certificate", "Ledger"]
    ),
    
    "kabbalah": PackageInfo(
        name="kabbalah",
        description="Tree of Life, tzimtzum, tikkun, gematria, topology",
        metro_line=MetroLine.GREEN,
        tradition=Tradition.HEBREW,
        lines=4974,
        files=7,
        dependencies=["core"],
        exports=["TreeOfLife", "Sefirah", "Tzimtzum", "SoulStack"],
        unified_types_used=["Element", "TypedTruth", "Certificate"]
    ),
    
    "quranic_holographic": PackageInfo(
        name="quranic_holographic",
        description="Quranic lattice, 6D metric, phenomenology, ritual",
        metro_line=MetroLine.GREEN,
        tradition=Tradition.ISLAMIC,
        lines=3569,
        files=6,
        dependencies=["core"],
        exports=["QuranicLattice", "IslamicMetric", "SalahProtocol"],
        unified_types_used=["HolographicAddress", "Certificate"]
    ),
    
    "qumran": PackageInfo(
        name="qumran",
        description="Dead Sea scrolls, dualism, time kernel, role graph",
        metro_line=MetroLine.GREEN,
        tradition=Tradition.HEBREW,
        lines=3052,
        files=5,
        dependencies=["kabbalah"],
        exports=["Dualism", "TimeKernel", "RoleGraph"],
        unified_types_used=["B4", "Element", "Ledger"]
    ),
    
    # =========================================================================
    # TIER V — BLUE LINE: DHARMIC TRADITIONS (18,000+ lines)
    # =========================================================================
    
    "gita": PackageInfo(
        name="gita",
        description="Bhagavad Gita: gunas, jiva, liberation, visvarupa",
        metro_line=MetroLine.BLUE,
        tradition=Tradition.HINDU,
        lines=5548,
        files=9,
        dependencies=["core"],
        exports=["Gunas", "Jiva", "Liberation", "Visvarupa", "Katapayadi"],
        unified_types_used=["Element", "TypedTruth", "Certificate"]
    ),
    
    "vajrayana": PackageInfo(
        name="vajrayana",
        description="Tibetan Buddhism: trikaya, mandala, bardo, yoga",
        metro_line=MetroLine.BLUE,
        tradition=Tradition.BUDDHIST,
        lines=4344,
        files=6,
        dependencies=["core"],
        exports=["Trikaya", "Mandala", "Bardo", "DeityYoga"],
        unified_types_used=["Element", "TypedTruth"]
    ),
    
    "tibetan": PackageInfo(
        name="tibetan",
        description="Bardo, deity yoga, mandala systems",
        metro_line=MetroLine.BLUE,
        tradition=Tradition.BUDDHIST,
        lines=2296,
        files=4,
        dependencies=["vajrayana"],
        exports=["BardoStates", "DeityYogaProtocol", "MandalaSystem"],
        unified_types_used=["TypedTruth", "Operator"]
    ),
    
    "mushin": PackageInfo(
        name="mushin",
        description="Zen computing: koan, zazen, network, no-mind",
        metro_line=MetroLine.BLUE,
        tradition=Tradition.ZEN,
        lines=3103,
        files=5,
        dependencies=["core"],
        exports=["MushinCore", "Koan", "Zazen", "MuNetwork"],
        unified_types_used=["B4", "TypedTruth", "ZResult"]
    ),
    
    # =========================================================================
    # TIER VI — PURPLE LINE: PAGAN TRADITIONS (17,000+ lines)
    # =========================================================================
    
    "zoroastrian": PackageInfo(
        name="zoroastrian",
        description="Amesha Spentas, frashokereti, chronology, rituals",
        metro_line=MetroLine.PURPLE,
        tradition=Tradition.ZOROASTRIAN,
        lines=4649,
        files=7,
        dependencies=["core"],
        exports=["AmeshaSpenta", "Frashokereti", "BinaryField", "SoulStack"],
        unified_types_used=["B4", "Element", "Certificate"]
    ),
    
    "norse": PackageInfo(
        name="norse",
        description="Yggdrasil, runes, wyrd, ragnarok, seidr",
        metro_line=MetroLine.PURPLE,
        tradition=Tradition.NORSE,
        lines=4506,
        files=7,
        dependencies=["core"],
        exports=["Yggdrasil", "Runes", "Wyrd", "Ragnarok", "Seidr"],
        unified_types_used=["Element", "TypedTruth", "Ledger"]
    ),
    
    "celtic": PackageInfo(
        name="celtic",
        description="Ogham, triadic logic, otherworld, temporal protocols",
        metro_line=MetroLine.PURPLE,
        tradition=Tradition.CELTIC,
        lines=3814,
        files=6,
        dependencies=["core"],
        exports=["Ogham", "Triadic", "Otherworld", "TemporalProtocol"],
        unified_types_used=["Element", "TypedTruth"]
    ),
    
    "ifa": PackageInfo(
        name="ifa",
        description="Yoruba: ase, orisha, divination, hypercube",
        metro_line=MetroLine.PURPLE,
        tradition=Tradition.YORUBA,
        lines=2725,
        files=5,
        dependencies=["core"],
        exports=["Ase", "Orisha", "Divination", "IfaHypercube"],
        unified_types_used=["B4", "Element", "Certificate"]
    ),
    
    # =========================================================================
    # TIER VII — WHITE LINE: HERMETIC & ALCHEMICAL (22,000+ lines)
    # =========================================================================
    
    "deep_crystal": PackageInfo(
        name="deep_crystal",
        description="Crystal synthesis, bio-OS, maat, duat, TSE",
        metro_line=MetroLine.WHITE,
        tradition=Tradition.HERMETIC,
        lines=5300,
        files=8,
        dependencies=["crystal_computing", "core"],
        exports=["DeepSynthesis", "BioOS", "Maat", "Duat", "TSE"],
        unified_types_used=["CrystalAddress", "Element", "Operator"]
    ),
    
    "solomonic": PackageInfo(
        name="solomonic",
        description="Key of Solomon: pentacles, spirits, spells, geometry",
        metro_line=MetroLine.WHITE,
        tradition=Tradition.HERMETIC,
        lines=3316,
        files=5,
        dependencies=["kabbalah", "core"],
        exports=["Pentacle", "Spirit", "Spell", "SolomonicGeometry"],
        unified_types_used=["Element", "Certificate", "TypedTruth"]
    ),
    
    "copper_scroll": PackageInfo(
        name="copper_scroll",
        description="Metallurgical ledger, holographic, geodetics, cipher",
        metro_line=MetroLine.WHITE,
        tradition=Tradition.HERMETIC,
        lines=3373,
        files=6,
        dependencies=["core"],
        exports=["MetallurgicalLedger", "CopperCipher", "Geodetics"],
        unified_types_used=["Ledger", "Certificate", "HolographicAddress"]
    ),
    
    "math_of_alchemy": PackageInfo(
        name="math_of_alchemy",
        description="Tria prima, planetary, zodiac, philosopher's stone",
        metro_line=MetroLine.WHITE,
        tradition=Tradition.HERMETIC,
        lines=2915,
        files=6,
        dependencies=["alchemy", "core"],
        exports=["TriaPrima", "PlanetaryOps", "Zodiac", "Stone"],
        unified_types_used=["Element", "Operator", "TypedTruth"]
    ),
    
    "alchemy": PackageInfo(
        name="alchemy",
        description="Elemental operations, stages, transformations",
        metro_line=MetroLine.WHITE,
        tradition=Tradition.HERMETIC,
        lines=2000,
        files=3,
        dependencies=["core"],
        exports=["ElementalOps", "Stages", "AlchemicalTransform"],
        unified_types_used=["Element", "Operator"]
    ),
    
    "khemet": PackageInfo(
        name="khemet",
        description="Egyptian: dynamics, substrate, recovery, validation",
        metro_line=MetroLine.WHITE,
        tradition=Tradition.EGYPTIAN,
        lines=3918,
        files=6,
        dependencies=["core"],
        exports=["KhemetDynamics", "KhemetSubstrate", "MaatValidation"],
        unified_types_used=["Element", "TypedTruth", "Ledger"]
    ),
    
    # =========================================================================
    # TIER VIII — GOLD LINE: QUANTUM & HOLOGRAPHIC (26,000+ lines)
    # =========================================================================
    
    "qhc": PackageInfo(
        name="qhc",
        description="Quantum Holography Computing: 1024 regimes, tiles, blocktree",
        metro_line=MetroLine.GOLD,
        tradition=Tradition.QUANTUM,
        lines=3749,
        files=7,
        dependencies=["core", "quantum"],
        exports=["QHCRuntime", "HilbertSpace", "Blocktree", "Tiles", "ModeWord"],
        unified_types_used=["QHCRegime", "HolographicAddress", "B4"]
    ),
    
    "qshrink": PackageInfo(
        name="qshrink",
        description="Quantum compression, lenses, pipeline, container",
        metro_line=MetroLine.GOLD,
        tradition=Tradition.QUANTUM,
        lines=3520,
        files=5,
        dependencies=["quantum", "core"],
        exports=["QShrinkCore", "CompressionLens", "Pipeline"],
        unified_types_used=["Lens", "ZResult", "Certificate"]
    ),
    
    "quantum": PackageInfo(
        name="quantum",
        description="Bulk representation, framework, runtime",
        metro_line=MetroLine.GOLD,
        tradition=Tradition.QUANTUM,
        lines=2407,
        files=4,
        dependencies=["core"],
        exports=["QuantumBulk", "QuantumFramework", "QuantumRuntime"],
        unified_types_used=["B4", "Operator", "Certificate"]
    ),
    
    "zero_point": PackageInfo(
        name="zero_point",
        description="Casimir effect, vacuum, topological, superconducting",
        metro_line=MetroLine.GOLD,
        tradition=Tradition.QUANTUM,
        lines=3091,
        files=5,
        dependencies=["quantum", "core"],
        exports=["CasimirEffect", "VacuumFluctuation", "TopologicalZero"],
        unified_types_used=["ZResult", "TypedTruth"]
    ),
    
    "zeropoint": PackageInfo(
        name="zeropoint",
        description="Agent, harmonia, paradox, void dynamics",
        metro_line=MetroLine.GOLD,
        tradition=Tradition.QUANTUM,
        lines=3061,
        files=6,
        dependencies=["zero_point", "core"],
        exports=["ZeroAgent", "Harmonia", "Paradox", "VoidDynamics"],
        unified_types_used=["ZResult", "B4", "Operator"]
    ),
    
    "superposition": PackageInfo(
        name="superposition",
        description="Crystal superposition, quad-polar, shadow states",
        metro_line=MetroLine.GOLD,
        tradition=Tradition.QUANTUM,
        lines=2082,
        files=4,
        dependencies=["quantum", "core"],
        exports=["SuperpositionCrystal", "QuadPolar", "ShadowState"],
        unified_types_used=["B4", "CrystalAddress"]
    ),
    
    "hololens": PackageInfo(
        name="hololens",
        description="Hybrid holographic lenses, antisymmetry, verification",
        metro_line=MetroLine.GOLD,
        tradition=Tradition.QUANTUM,
        lines=2650,
        files=5,
        dependencies=["quantum", "core"],
        exports=["HoloLens", "Antisymmetry", "HoloVerification"],
        unified_types_used=["Lens", "HolographicAddress", "Certificate"]
    ),
    
    "hrp": PackageInfo(
        name="hrp",
        description="Holographic Rotation Protocol, frames, texture, objects",
        metro_line=MetroLine.GOLD,
        tradition=Tradition.QUANTUM,
        lines=3520,
        files=6,
        dependencies=["hololens", "core"],
        exports=["RotationProtocol", "HRPFrame", "HRPTexture"],
        unified_types_used=["HolographicAddress", "Operator"]
    ),
    
    # =========================================================================
    # TIER IX — SILVER LINE: CONTROL & GOVERNANCE (31,000+ lines)
    # =========================================================================
    
    "omega": PackageInfo(
        name="omega",
        description="Omega Protocol, convergence, frashokereti, permissions",
        metro_line=MetroLine.SILVER,
        tradition=Tradition.CONTROL,
        lines=7574,
        files=11,
        dependencies=["core", "governance"],
        exports=["OmegaProtocol", "Convergence", "PermissionEscalation"],
        unified_types_used=["TypedTruth", "Certificate", "Ledger"]
    ),
    
    "hdcs": PackageInfo(
        name="hdcs",
        description="Hybrid Dynamical Control System, controllers, stability",
        metro_line=MetroLine.SILVER,
        tradition=Tradition.CONTROL,
        lines=7179,
        files=12,
        dependencies=["core"],
        exports=["HDCSController", "Stability", "Actuators", "Sensors"],
        unified_types_used=["TypedTruth", "Certificate", "Operator"]
    ),
    
    "gg_alignment": PackageInfo(
        name="gg_alignment",
        description="Good Game alignment, high-elo, protocols, topology",
        metro_line=MetroLine.SILVER,
        tradition=Tradition.CONTROL,
        lines=6411,
        files=8,
        dependencies=["gg", "core"],
        exports=["GGAlignment", "HighElo", "AlignmentTopology"],
        unified_types_used=["TypedTruth", "Certificate"]
    ),
    
    "gin": PackageInfo(
        name="gin",
        description="Global Information Network, agents, deadlock, moral geometry",
        metro_line=MetroLine.SILVER,
        tradition=Tradition.CONTROL,
        lines=4164,
        files=7,
        dependencies=["core"],
        exports=["GINAgent", "DeadlockResolver", "MoralGeometry"],
        unified_types_used=["TypedTruth", "Ledger"]
    ),
    
    "governance": PackageInfo(
        name="governance",
        description="Ledger, PCP, protocols, harness, defects",
        metro_line=MetroLine.SILVER,
        tradition=Tradition.CONTROL,
        lines=3836,
        files=6,
        dependencies=["core"],
        exports=["GovernanceLedger", "PCP", "Harness"],
        unified_types_used=["Ledger", "Certificate", "TypedTruth"]
    ),
    
    "gg": PackageInfo(
        name="gg",
        description="Agent, manifold, tensor, operators",
        metro_line=MetroLine.SILVER,
        tradition=Tradition.CONTROL,
        lines=3376,
        files=5,
        dependencies=["core"],
        exports=["GGAgent", "Manifold", "Tensor"],
        unified_types_used=["Operator", "TypedTruth"]
    ),
    
    # =========================================================================
    # TIER X — COSMIC LINE: SPECIALIZED SYSTEMS (38,000+ lines)
    # =========================================================================
    
    "syntax": PackageInfo(
        name="syntax",
        description="Zero-point syntax, obligations, coordinates, representation",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.CORE,
        lines=3674,
        files=6,
        dependencies=["core"],
        exports=["ZeroPointSyntax", "Obligations", "Coordinates"],
        unified_types_used=["ZResult", "TypedTruth"]
    ),
    
    "hugging": PackageInfo(
        name="hugging",
        description="Quantum Hugging Framework, observer, instruments",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.QUANTUM,
        lines=3659,
        files=7,
        dependencies=["quantum", "core"],
        exports=["HuggingFramework", "Observer", "Instruments"],
        unified_types_used=["B4", "Operator"]
    ),
    
    "epics": PackageInfo(
        name="epics",
        description="Epic registry, failure modes, mining, protocols",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.CORE,
        lines=3695,
        files=6,
        dependencies=["core"],
        exports=["EpicRegistry", "FailureModes", "Mining"],
        unified_types_used=["TypedTruth", "Certificate", "Ledger"]
    ),
    
    "hbas": PackageInfo(
        name="hbas",
        description="Hybrid encoding detection, candidates, encoders",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.CORE,
        lines=2733,
        files=4,
        dependencies=["core"],
        exports=["EncodingDetection", "Candidates", "Encoders"],
        unified_types_used=["TypedTruth", "ZResult"]
    ),
    
    "emcrystal": PackageInfo(
        name="emcrystal",
        description="EM duality, seeds, hubs, aether, atlas",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.QUANTUM,
        lines=2851,
        files=6,
        dependencies=["crystal_computing", "core"],
        exports=["EMDuality", "Seeds", "Hubs", "EMAtlas"],
        unified_types_used=["Element", "CrystalAddress"]
    ),
    
    "biophysics": PackageInfo(
        name="biophysics",
        description="Biological corridors, clans, aether, metro",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.CORE,
        lines=2169,
        files=5,
        dependencies=["core"],
        exports=["BioCorridors", "Clans", "BioAether"],
        unified_types_used=["Corridor", "Element", "Humor"]
    ),
    
    "seed": PackageInfo(
        name="seed",
        description="Expression lattice, tunneling, verification",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.MATHEMATICAL,
        lines=2572,
        files=5,
        dependencies=["core"],
        exports=["ExpressionLattice", "Tunneling", "SeedVerification"],
        unified_types_used=["CrystalAddress", "Certificate"]
    ),
    
    "aetheric": PackageInfo(
        name="aetheric",
        description="Meta-hybrid calculus, operators, core",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.HERMETIC,
        lines=1833,
        files=3,
        dependencies=["core"],
        exports=["AethericCore", "MetaOperators"],
        unified_types_used=["Element", "Operator"]
    ),
    
    "philosophical": PackageInfo(
        name="philosophical",
        description="Elemental philosophy, stoic, alchemical",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.GREEK,
        lines=2022,
        files=4,
        dependencies=["hellenic", "alchemy"],
        exports=["ElementalPhilosophy", "StoicPhilosophy"],
        unified_types_used=["Element", "Cause", "Category"]
    ),
    
    "engine": PackageInfo(
        name="engine",
        description="Paradox engine",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.CORE,
        lines=757,
        files=2,
        dependencies=["core"],
        exports=["ParadoxEngine"],
        unified_types_used=["B4", "TypedTruth"]
    ),
    
    "agent": PackageInfo(
        name="agent",
        description="Distinguished agent",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.CORE,
        lines=634,
        files=2,
        dependencies=["core"],
        exports=["DistinguishedAgent"],
        unified_types_used=["TypedTruth", "Certificate"]
    ),
    
    "memory": PackageInfo(
        name="memory",
        description="Hierarchical memory system",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.CORE,
        lines=636,
        files=2,
        dependencies=["core"],
        exports=["MemoryHierarchy", "MemoryManager"],
        unified_types_used=["B4"]
    ),
    
    "types": PackageInfo(
        name="types",
        description="Aristotelian type system",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.GREEK,
        lines=635,
        files=2,
        dependencies=["hellenic"],
        exports=["AristotelianTypes", "TypeRegistry"],
        unified_types_used=["Category", "Cause"]
    ),
    
    "runtime": PackageInfo(
        name="runtime",
        description="Bio-OS runtime",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.CORE,
        lines=648,
        files=2,
        dependencies=["core"],
        exports=["BioRuntime"],
        unified_types_used=["Humor", "Element"]
    ),
    
    "crystal": PackageInfo(
        name="crystal",
        description="Crystal addressing",
        metro_line=MetroLine.COSMIC,
        tradition=Tradition.MATHEMATICAL,
        lines=696,
        files=1,
        dependencies=["core"],
        exports=["CrystalAddressing"],
        unified_types_used=["CrystalAddress"]
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_packages_by_metro_line(line: MetroLine) -> List[PackageInfo]:
    """Get all packages on a metro line."""
    return [p for p in PACKAGE_REGISTRY.values() if p.metro_line == line]


def get_packages_by_tradition(tradition: Tradition) -> List[PackageInfo]:
    """Get all packages from a tradition."""
    return [p for p in PACKAGE_REGISTRY.values() if p.tradition == tradition]


def get_dependency_graph() -> Dict[str, Set[str]]:
    """Build complete dependency graph."""
    graph = {}
    for name, info in PACKAGE_REGISTRY.items():
        graph[name] = set(info.dependencies)
    return graph


def get_total_lines() -> int:
    """Get total lines across all packages."""
    return sum(p.lines for p in PACKAGE_REGISTRY.values())


def get_total_files() -> int:
    """Get total files across all packages."""
    return sum(p.files for p in PACKAGE_REGISTRY.values())


def get_metro_statistics() -> Dict[MetroLine, Dict[str, int]]:
    """Get statistics per metro line."""
    stats = {}
    for line in MetroLine:
        packages = get_packages_by_metro_line(line)
        stats[line] = {
            "packages": len(packages),
            "lines": sum(p.lines for p in packages),
            "files": sum(p.files for p in packages),
        }
    return stats


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    print("=== ATHENA OS META PACKAGE REGISTRY ===\n")
    
    print(f"Total Packages: {len(PACKAGE_REGISTRY)}")
    print(f"Total Lines: {get_total_lines():,}")
    print(f"Total Files: {get_total_files()}")
    
    print("\n=== METRO LINE STATISTICS ===")
    for line, stats in get_metro_statistics().items():
        print(f"  {line.value}: {stats['packages']} packages, {stats['lines']:,} lines, {stats['files']} files")
    
    print("\n=== TRADITION DISTRIBUTION ===")
    for tradition in Tradition:
        packages = get_packages_by_tradition(tradition)
        if packages:
            lines = sum(p.lines for p in packages)
            print(f"  {tradition.value}: {len(packages)} packages, {lines:,} lines")
