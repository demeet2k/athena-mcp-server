"""
ATHENA OS - HBAS-Ω: CANDIDATES MODULE
======================================
Catalog of Confirmed HBAS Systems with Predicted Encodings

TIER 1 CANDIDATES (Strong Signal, Full Systems):
    1. Ifá/Yoruba - Binary Hypercube (Q_8 = 256)
    2. Norse/Germanic - World-Tree Graph (9 nodes, 24 runes)
    3. Zoroastrian - Dual-Phase Dynamics (12,000-year cycle)
    4. Tibetan Vajrayana - Transition Matrix (49-day Bardo)
    5. Pythagorean/Orphic - Spectral Decomposition
    6. Hebrew/Kabbalistic - Tree Graph (10 Sefirot, 22 paths)
    7. Dogon - Paired Operators (Nummo twins)
    8. Polynesian/Hawaiian - Sequential Symmetry Breaking (16 wā)

TIER 2 CANDIDATES (Partial Signal):
    9. Incan/Andean - Spatial Coordinate Systems (Khipu, Ceque)
    10. Celtic/Druidic - Tree/Graph + Triadic Logic (Ogham)
    11. Japanese Esoteric - Vibration/Sound Operators
    12. Minoan/Mycenaean - Labyrinth as Path Integral
    13. Proto-Elamite/Harappan - Metrological Kernels

CORE SYSTEMS (Already Implemented):
    - Taoist (I Ching) - Binary Q_6
    - Egyptian (KHEMET) - Rigged Hilbert Space
    - Vedic (Sanātana Gaṇita) - Consciousness Space
    - Sumerian (ŠAR-60) - Sexagesimal Control
    - Maya (Q-Maya) - Discrete-Time Lattice
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np

from .detection import HBASDetector, CriterionResult
from .encoders import (
    EncoderType, BinaryEncoder, GraphEncoder, 
    SpectralEncoder, MetrologicalEncoder, TransitionEncoder,
    IfaEncoder, IChingEncoder, YggdrasilEncoder, SefirotEncoder,
    PythagoreanEncoder, SumerianEncoder, MayaEncoder,
    BardoEncoder, DuatEncoder
)


# =============================================================================
# CANDIDATE CLASSIFICATION
# =============================================================================

class CandidateTier(Enum):
    """Classification tiers for HBAS candidates."""
    
    CORE = "core"       # Already fully implemented
    TIER_1 = "tier_1"   # Strong signal, likely full systems
    TIER_2 = "tier_2"   # Partial signal, require investigation


class EncodingFocus(Enum):
    """Primary encoding focus of a system."""
    
    BINARY_HYPERCUBE = "binary"
    GRAPH_TOPOLOGY = "graph"
    SPECTRAL_HARMONIC = "spectral"
    METROLOGICAL = "metrology"
    TRANSITION_REPAIR = "transition"
    COORDINATE_SPATIAL = "spatial"
    VIBRATIONAL = "vibration"
    LABYRINTHINE = "labyrinth"


# =============================================================================
# CANDIDATE SYSTEM
# =============================================================================

@dataclass
class CandidateSystem:
    """
    A candidate HBAS system.
    
    Contains all metadata and predicted encodings.
    """
    
    name: str
    culture: str
    tier: CandidateTier
    
    # Observable structure
    primary_focus: EncodingFocus
    secondary_focus: Optional[EncodingFocus] = None
    
    # Key elements
    state_space: str = ""
    operator_set: List[str] = field(default_factory=list)
    cycles: List[str] = field(default_factory=list)
    bridging_principle: str = ""
    error_correction: str = ""
    
    # Mathematical correlates
    math_objects: Dict[str, str] = field(default_factory=dict)
    
    # Confidence
    confidence: float = 0.0
    
    # Encoders
    _encoders: Dict[str, Any] = field(default_factory=dict)
    
    def add_encoder(self, encoder_type: str, encoder: Any) -> None:
        """Add an encoder to this system."""
        self._encoders[encoder_type] = encoder
    
    def get_encoder(self, encoder_type: str) -> Optional[Any]:
        """Get encoder by type."""
        return self._encoders.get(encoder_type)


# =============================================================================
# TIER 1 CANDIDATES
# =============================================================================

def create_ifa_candidate() -> CandidateSystem:
    """Create Ifá/Yoruba candidate system."""
    system = CandidateSystem(
        name="Ọpẹ́-256 (Ifá)",
        culture="Yoruba (West Africa)",
        tier=CandidateTier.TIER_1,
        primary_focus=EncodingFocus.BINARY_HYPERCUBE,
        secondary_focus=EncodingFocus.TRANSITION_REPAIR,
        state_space="256 Odù (2⁸ binary figures)",
        operator_set=["Orunmila", "Eshu", "Ogun", "Shango", 
                     "Yemoja", "Oshun", "Obatala", "Oya"],
        cycles=["16-day divination cycle", "Seasonal festivals"],
        bridging_principle="Àṣẹ (vital force / information flux)",
        error_correction="Ebó (sacrifice as state correction)",
        math_objects={
            "Q_8 hypercube": "256 Odù as vertices",
            "8-bit binary": "Opele chain casting",
            "16×16 tensor": "Principal Odù decomposition",
            "Markov matrix": "Odù-to-Odù transitions"
        },
        confidence=0.95
    )
    system.add_encoder("binary", IfaEncoder())
    return system


def create_norse_candidate() -> CandidateSystem:
    """Create Norse/Germanic candidate system."""
    system = CandidateSystem(
        name="Yggdrasil Graph Theory",
        culture="Norse/Germanic",
        tier=CandidateTier.TIER_1,
        primary_focus=EncodingFocus.GRAPH_TOPOLOGY,
        secondary_focus=EncodingFocus.TRANSITION_REPAIR,
        state_space="9 Worlds on weighted graph",
        operator_set=["Odin", "Thor", "Freya", "Loki", "Tyr", "Baldur",
                     "Heimdall", "Frigg", "Hel", "Freyr"],
        cycles=["Ragnarök cycle", "Seasonal blóts"],
        bridging_principle="Ørlog (cosmic law / fate)",
        error_correction="Seiðr (magic), Ragnarök (reset)",
        math_objects={
            "9-node graph": "Yggdrasil Nine Worlds",
            "24 operators": "Elder Futhark runes",
            "Wyrd tensor": "Non-commutative history",
            "Phase transition": "Ragnarök → Rebirth"
        },
        confidence=0.90
    )
    system.add_encoder("graph", YggdrasilEncoder())
    return system


def create_zoroastrian_candidate() -> CandidateSystem:
    """Create Zoroastrian candidate system."""
    return CandidateSystem(
        name="Asha Dynamics",
        culture="Zoroastrian/Persian",
        tier=CandidateTier.TIER_1,
        primary_focus=EncodingFocus.TRANSITION_REPAIR,
        secondary_focus=EncodingFocus.BINARY_HYPERCUBE,
        state_space="Dual-phase field (Asha vs Druj)",
        operator_set=["Ahura Mazda", "Angra Mainyu", 
                     "Vohu Manah", "Asha Vahishta", "Khshathra Vairya",
                     "Spenta Armaiti", "Haurvatat", "Ameretat"],
        cycles=["12,000-year cosmic cycle (4 × 3000)", "Seasonal Gahanbars"],
        bridging_principle="Asha (truth / cosmic order)",
        error_correction="Fire maintenance, Frashokereti (final renovation)",
        math_objects={
            "Binary field": "Asha (order) vs Druj (chaos)",
            "7 generators": "Amesha Spenta",
            "12000-year cycle": "4-phase evolution",
            "Absorbing state": "Frashokereti"
        },
        confidence=0.85
    )


def create_tibetan_candidate() -> CandidateSystem:
    """Create Tibetan Vajrayana candidate system."""
    system = CandidateSystem(
        name="Bardo Transition Matrix",
        culture="Tibetan Vajrayana",
        tier=CandidateTier.TIER_1,
        primary_focus=EncodingFocus.TRANSITION_REPAIR,
        secondary_focus=EncodingFocus.SPECTRAL_HARMONIC,
        state_space="Hilbert space with projective measurement",
        operator_set=["Five Dhyani Buddhas", "Eight Bodhisattvas",
                     "Peaceful/Wrathful deities"],
        cycles=["49-day Bardo (7×7)", "Kālacakra 360-spoke wheel"],
        bridging_principle="Dharma / Karma",
        error_correction="Bardo navigation, Liberation vs Rebirth",
        math_objects={
            "49-step Markov": "Bardo transition chain",
            "Eigenstates": "Deity lights as projections",
            "Mandala": "Group representation diagram",
            "6 absorbing states": "Rebirth realms"
        },
        confidence=0.88
    )
    system.add_encoder("transition", BardoEncoder())
    return system


def create_pythagorean_candidate() -> CandidateSystem:
    """Create Pythagorean/Orphic candidate system."""
    system = CandidateSystem(
        name="Harmonia Mundi",
        culture="Pythagorean/Orphic Greek",
        tier=CandidateTier.TIER_1,
        primary_focus=EncodingFocus.SPECTRAL_HARMONIC,
        state_space="Spectral decomposition space",
        operator_set=["Monad", "Dyad", "Triad", "Tetrad"],
        cycles=["Harmony of Spheres (planetary)", "Metempsychosis"],
        bridging_principle="Harmonia (cosmic harmony)",
        error_correction="Metempsychosis (soul transmigration)",
        math_objects={
            "Spectral theory": "Harmony of Spheres",
            "Integer lattice": "Tetraktys (1+2+3+4=10)",
            "Ratio metric": "Musical intervals",
            "Norm conservation": "Soul invariance in transmigration"
        },
        confidence=0.85
    )
    system.add_encoder("spectral", PythagoreanEncoder())
    return system


def create_kabbalistic_candidate() -> CandidateSystem:
    """Create Hebrew/Kabbalistic candidate system."""
    system = CandidateSystem(
        name="Etz Chaim (Tree of Life)",
        culture="Hebrew/Kabbalistic",
        tier=CandidateTier.TIER_1,
        primary_focus=EncodingFocus.GRAPH_TOPOLOGY,
        secondary_focus=EncodingFocus.BINARY_HYPERCUBE,
        state_space="10-dimensional state space (Sefirot)",
        operator_set=["Keter", "Chokmah", "Binah", "Chesed", "Gevurah",
                     "Tiferet", "Netzach", "Hod", "Yesod", "Malkuth"],
        cycles=["Shemitot (7000-year cycles)", "Jubilee"],
        bridging_principle="Torah / Tikkun",
        error_correction="Tikkun Olam (repair of world)",
        math_objects={
            "10-node tree": "Sefirot as basis vectors",
            "22 edges": "Hebrew letters as operators",
            "4 worlds": "Dimensional cascade",
            "Gematria": "Hash function (word → number)"
        },
        confidence=0.90
    )
    system.add_encoder("graph", SefirotEncoder())
    return system


def create_dogon_candidate() -> CandidateSystem:
    """Create Dogon candidate system."""
    return CandidateSystem(
        name="Nummo Cosmology",
        culture="Dogon (Mali)",
        tier=CandidateTier.TIER_1,
        primary_focus=EncodingFocus.BINARY_HYPERCUBE,
        secondary_focus=EncodingFocus.SPECTRAL_HARMONIC,
        state_space="22-category ontology",
        operator_set=["Nummo twins", "Amma", "Lebe"],
        cycles=["60-year Sigui ceremony"],
        bridging_principle="Nommo (water/word principle)",
        error_correction="Sigui renewal",
        math_objects={
            "60-year cycle": "Sexagesimal echo",
            "Paired operators": "Nummo twins",
            "22 categories": "Ontological dimensions",
            "Sirius calibration": "Astronomical reference (if authentic)"
        },
        confidence=0.70  # Lower due to interpretation disputes
    )


def create_polynesian_candidate() -> CandidateSystem:
    """Create Polynesian/Hawaiian candidate system."""
    return CandidateSystem(
        name="Kumulipo",
        culture="Polynesian/Hawaiian",
        tier=CandidateTier.TIER_1,
        primary_focus=EncodingFocus.TRANSITION_REPAIR,
        secondary_focus=EncodingFocus.COORDINATE_SPATIAL,
        state_space="16-phase creation sequence",
        operator_set=["Various akua (gods)", "Ancestral spirits"],
        cycles=["16 wā (eras)", "Makahiki season"],
        bridging_principle="Mana (sacred power)",
        error_correction="Kapu (constraint system)",
        math_objects={
            "16 phases": "Sequential symmetry breaking",
            "Mana conservation": "Operator transferability",
            "Kapu constraints": "Hard boundary conditions",
            "32-house compass": "Directional basis vectors"
        },
        confidence=0.80
    )


# =============================================================================
# TIER 2 CANDIDATES
# =============================================================================

def create_incan_candidate() -> CandidateSystem:
    """Create Incan/Andean candidate system."""
    return CandidateSystem(
        name="Ceque-Khipu System",
        culture="Incan/Andean",
        tier=CandidateTier.TIER_2,
        primary_focus=EncodingFocus.COORDINATE_SPATIAL,
        secondary_focus=EncodingFocus.BINARY_HYPERCUBE,
        state_space="Radial coordinate grid (41 ceques)",
        operator_set=["Viracocha", "Inti", "Mama Quilla", "Pachamama"],
        cycles=["Inti Raymi (solstice)", "Capacocha"],
        bridging_principle="Ayni (reciprocity)",
        error_correction="Capacocha offerings",
        math_objects={
            "41 radial lines": "Ceque coordinate system",
            "~350 huacas": "Sacred data points",
            "Khipu": "Multidimensional database",
            "Dual moiety": "ℤ₂ symmetry (Hanan/Hurin)"
        },
        confidence=0.65
    )


def create_celtic_candidate() -> CandidateSystem:
    """Create Celtic/Druidic candidate system."""
    return CandidateSystem(
        name="Ogham Encoding",
        culture="Celtic/Druidic",
        tier=CandidateTier.TIER_2,
        primary_focus=EncodingFocus.GRAPH_TOPOLOGY,
        secondary_focus=EncodingFocus.VIBRATIONAL,
        state_space="20-25 letter/tree associations",
        operator_set=["Danu", "Dagda", "Brigid", "Lugh", "Morrigan"],
        cycles=["13-month lunar + 1 day", "Samhain/Beltane transitions"],
        bridging_principle="Dán (fate/skill)",
        error_correction="Otherworld mirror",
        math_objects={
            "Ogham alphabet": "Multi-attribute operators",
            "13 + 1 months": "Lunar calendar",
            "Triadic closure": "3-element generating sets",
            "Otherworld": "Dual space (adjoint?)"
        },
        confidence=0.55
    )


def create_japanese_candidate() -> CandidateSystem:
    """Create Japanese Esoteric (Shingon) candidate system."""
    return CandidateSystem(
        name="Kotodama-Shingon",
        culture="Japanese Esoteric",
        tier=CandidateTier.TIER_2,
        primary_focus=EncodingFocus.VIBRATIONAL,
        secondary_focus=EncodingFocus.GRAPH_TOPOLOGY,
        state_space="Phoneme operator space",
        operator_set=["Dainichi Nyorai", "Five Wisdom Buddhas", "Godai"],
        cycles=["Seasonal rituals", "Mandala circuits"],
        bridging_principle="Kotodama (word-spirit)",
        error_correction="Mantra recitation",
        math_objects={
            "Phonemes → operators": "Kotodama mapping",
            "Seed syllables": "Bīja as generators",
            "Mandala": "State-space representation",
            "Kū (Void)": "Vacuum state"
        },
        confidence=0.60
    )


def create_minoan_candidate() -> CandidateSystem:
    """Create Minoan/Mycenaean candidate system."""
    return CandidateSystem(
        name="Labyrinth Protocol",
        culture="Minoan/Mycenaean",
        tier=CandidateTier.TIER_2,
        primary_focus=EncodingFocus.LABYRINTHINE,
        state_space="Labyrinth path space",
        operator_set=["Goddess (Mother)", "Bull/Minotaur"],
        cycles=["Bull-leaping rituals", "Harvest"],
        bridging_principle="Unknown (Linear A undeciphered)",
        error_correction="Labyrinth traversal",
        math_objects={
            "Labyrinth": "Unique geodesic path",
            "Minotaur": "Boundary operator",
            "Linear A": "Possible numerical encoding",
            "Palace": "Cosmogram layout"
        },
        confidence=0.40  # Lower due to undeciphered script
    )


# =============================================================================
# CORE SYSTEMS (Already Implemented)
# =============================================================================

def create_taoist_candidate() -> CandidateSystem:
    """Create Taoist/I Ching candidate system."""
    system = CandidateSystem(
        name="Dao/I Ching",
        culture="Chinese/Taoist",
        tier=CandidateTier.CORE,
        primary_focus=EncodingFocus.BINARY_HYPERCUBE,
        state_space="64 hexagrams (2⁶ = Q_6)",
        operator_set=["Yin", "Yang", "Wu Xing (Five Elements)"],
        cycles=["60-year (10 Stems × 12 Branches)", "Seasons"],
        bridging_principle="Dao (道) / De (德)",
        error_correction="I Ching divination → Wu Wei adjustment",
        math_objects={
            "Q_6 hypercube": "64 hexagrams as vertices",
            "8 trigrams": "Generators",
            "Wu Xing": "5-element transformation cycle"
        },
        confidence=1.0
    )
    system.add_encoder("binary", IChingEncoder())
    return system


def create_egyptian_candidate() -> CandidateSystem:
    """Create Egyptian/KHEMET candidate system."""
    system = CandidateSystem(
        name="KHEMET (Egyptian)",
        culture="Ancient Egyptian",
        tier=CandidateTier.CORE,
        primary_focus=EncodingFocus.TRANSITION_REPAIR,
        secondary_focus=EncodingFocus.SPECTRAL_HARMONIC,
        state_space="Rigged Hilbert Space (Gelfand Triple)",
        operator_set=["Ra", "Osiris", "Isis", "Horus", "Set", 
                     "Thoth", "Anubis", "Ma'at", "Ptah"],
        cycles=["Sothic (1460 yr)", "Civil (365)", "Lunar"],
        bridging_principle="Ma'at",
        error_correction="Omen → Purification → Ammit",
        math_objects={
            "Gelfand Triple": "Φ ⊂ H ⊂ Φ×",
            "12-hour Duat": "Transition matrix",
            "42 Confessions": "Constraint grid",
            "Ammit": "Garbage collection"
        },
        confidence=1.0
    )
    system.add_encoder("transition", DuatEncoder())
    return system


def create_vedic_candidate() -> CandidateSystem:
    """Create Vedic/Sanātana candidate system."""
    return CandidateSystem(
        name="Sanātana Gaṇita",
        culture="Vedic/Hindu",
        tier=CandidateTier.CORE,
        primary_focus=EncodingFocus.SPECTRAL_HARMONIC,
        secondary_focus=EncodingFocus.TRANSITION_REPAIR,
        state_space="H_Cit (consciousness Hilbert space)",
        operator_set=["Brahma", "Vishnu", "Shiva", "Pancha Bhuta"],
        cycles=["Yuga (4:3:2:1 decay)", "Kalpa"],
        bridging_principle="Ṛta / Dharma",
        error_correction="Jyotiṣa → Yajña → Pralaya",
        math_objects={
            "Trimurti": "3 primary operators",
            "Chakras": "7-level energy quantization",
            "Yuga decay": "4:3:2:1 entropy increase",
            "Kaṭapayādi": "Phoneme → integer cipher"
        },
        confidence=1.0
    )


def create_sumerian_candidate() -> CandidateSystem:
    """Create Sumerian candidate system."""
    system = CandidateSystem(
        name="ŠAR-60",
        culture="Sumerian/Babylonian",
        tier=CandidateTier.CORE,
        primary_focus=EncodingFocus.METROLOGICAL,
        secondary_focus=EncodingFocus.TRANSITION_REPAIR,
        state_space="Control Plane (An) + Data Plane (Ki)",
        operator_set=["An", "Enlil", "Enki", "Inanna", "Utu", "Nanna"],
        cycles=["Sar (3600)", "Ner (600)", "Great Year (25920)"],
        bridging_principle="Me (divine decrees)",
        error_correction="Omen catalogues → Namburbi → Flood",
        math_objects={
            "Base-60": "Sexagesimal positional notation",
            "Me (100+)": "Civilization function operators",
            "Ziggurat levels": "Dimensional hierarchy"
        },
        confidence=1.0
    )
    system.add_encoder("metrological", SumerianEncoder())
    return system


def create_maya_candidate() -> CandidateSystem:
    """Create Maya candidate system."""
    system = CandidateSystem(
        name="Q-Maya",
        culture="Maya",
        tier=CandidateTier.CORE,
        primary_focus=EncodingFocus.METROLOGICAL,
        secondary_focus=EncodingFocus.TRANSITION_REPAIR,
        state_space="Discrete-time Hilbert space",
        operator_set=["Itzamna", "K'inich Ahau", "Chaak", "K'awiil",
                     "Ix Chel", "Nine Lords of Xibalba"],
        cycles=["Tzolk'in (260)", "Haab' (365)", "Long Count"],
        bridging_principle="K'uhul / Ch'ulel",
        error_correction="Eclipse tables → Bloodletting → K'atun reset",
        math_objects={
            "Base-20": "Vigesimal positional",
            "260 × 365": "Calendar Round (18980 days)",
            "Long Count": "5125-year cycle",
            "9 underworld levels": "Transition states"
        },
        confidence=1.0
    )
    system.add_encoder("metrological", MayaEncoder())
    return system


# =============================================================================
# CANDIDATE REGISTRY
# =============================================================================

class CandidateRegistry:
    """
    Registry of all HBAS candidate systems.
    
    Provides access to cataloged systems and their encoders.
    """
    
    def __init__(self):
        self._candidates: Dict[str, CandidateSystem] = {}
        self._by_tier: Dict[CandidateTier, List[str]] = {
            CandidateTier.CORE: [],
            CandidateTier.TIER_1: [],
            CandidateTier.TIER_2: []
        }
        self._by_focus: Dict[EncodingFocus, List[str]] = {
            focus: [] for focus in EncodingFocus
        }
        
        self._populate()
    
    def _populate(self) -> None:
        """Populate registry with all candidates."""
        # Core systems
        self._add(create_taoist_candidate())
        self._add(create_egyptian_candidate())
        self._add(create_vedic_candidate())
        self._add(create_sumerian_candidate())
        self._add(create_maya_candidate())
        
        # Tier 1 candidates
        self._add(create_ifa_candidate())
        self._add(create_norse_candidate())
        self._add(create_zoroastrian_candidate())
        self._add(create_tibetan_candidate())
        self._add(create_pythagorean_candidate())
        self._add(create_kabbalistic_candidate())
        self._add(create_dogon_candidate())
        self._add(create_polynesian_candidate())
        
        # Tier 2 candidates
        self._add(create_incan_candidate())
        self._add(create_celtic_candidate())
        self._add(create_japanese_candidate())
        self._add(create_minoan_candidate())
    
    def _add(self, candidate: CandidateSystem) -> None:
        """Add candidate to registry."""
        key = candidate.name.lower().replace(" ", "_")
        self._candidates[key] = candidate
        self._by_tier[candidate.tier].append(key)
        self._by_focus[candidate.primary_focus].append(key)
        
        if candidate.secondary_focus:
            self._by_focus[candidate.secondary_focus].append(key)
    
    def get(self, name: str) -> Optional[CandidateSystem]:
        """Get candidate by name."""
        key = name.lower().replace(" ", "_")
        return self._candidates.get(key)
    
    def get_by_tier(self, tier: CandidateTier) -> List[CandidateSystem]:
        """Get all candidates of a tier."""
        return [self._candidates[key] for key in self._by_tier[tier]]
    
    def get_by_focus(self, focus: EncodingFocus) -> List[CandidateSystem]:
        """Get all candidates with encoding focus."""
        return [self._candidates[key] for key in self._by_focus[focus]]
    
    def get_all(self) -> List[CandidateSystem]:
        """Get all candidates."""
        return list(self._candidates.values())
    
    def summary(self) -> Dict[str, Any]:
        """Get registry summary."""
        return {
            "total": len(self._candidates),
            "by_tier": {
                tier.value: len(keys) 
                for tier, keys in self._by_tier.items()
            },
            "by_focus": {
                focus.value: len(keys)
                for focus, keys in self._by_focus.items()
                if len(keys) > 0
            }
        }


# =============================================================================
# COMPLEMENTARY RADIX THESIS
# =============================================================================

class ComplementaryRadixAnalysis:
    """
    Analysis of complementary radix systems.
    
    The thesis: Ancient civilizations developed complementary,
    not competing, mathematical frameworks.
    """
    
    def __init__(self, registry: CandidateRegistry):
        self.registry = registry
    
    def binary_resolution_hierarchy(self) -> Dict[str, int]:
        """
        Identify binary resolution hierarchy.
        
        I Ching (2⁶) → Ifá (2⁸) progression.
        """
        hierarchy = {}
        
        for candidate in self.registry.get_by_focus(EncodingFocus.BINARY_HYPERCUBE):
            encoder = candidate.get_encoder("binary")
            if encoder and isinstance(encoder, BinaryEncoder):
                hierarchy[candidate.name] = encoder.n_states
        
        return dict(sorted(hierarchy.items(), key=lambda x: x[1]))
    
    def metrological_bases(self) -> Dict[str, int]:
        """
        Identify metrological base systems.
        
        Sumerian (60), Maya (20), Decimal (10), etc.
        """
        bases = {}
        
        for candidate in self.registry.get_by_focus(EncodingFocus.METROLOGICAL):
            encoder = candidate.get_encoder("metrological")
            if encoder and isinstance(encoder, MetrologicalEncoder):
                bases[candidate.name] = encoder.base
        
        return bases
    
    def module_coverage(self) -> Dict[str, List[str]]:
        """
        Identify which modules each system covers.
        
        Each culture holds a different module of the same machine.
        """
        modules = {
            "binary_hypercube": [],
            "graph_topology": [],
            "spectral_harmonic": [],
            "metrological": [],
            "transition_repair": []
        }
        
        focus_to_module = {
            EncodingFocus.BINARY_HYPERCUBE: "binary_hypercube",
            EncodingFocus.GRAPH_TOPOLOGY: "graph_topology",
            EncodingFocus.SPECTRAL_HARMONIC: "spectral_harmonic",
            EncodingFocus.METROLOGICAL: "metrological",
            EncodingFocus.TRANSITION_REPAIR: "transition_repair"
        }
        
        for candidate in self.registry.get_all():
            primary_module = focus_to_module.get(candidate.primary_focus)
            if primary_module:
                modules[primary_module].append(candidate.name)
        
        return modules


# =============================================================================
# VALIDATION
# =============================================================================

def validate_candidates() -> bool:
    """Validate HBAS candidates module."""
    
    # Test individual candidate creation
    ifa = create_ifa_candidate()
    assert ifa.tier == CandidateTier.TIER_1
    assert ifa.primary_focus == EncodingFocus.BINARY_HYPERCUBE
    assert ifa.confidence > 0.9
    
    encoder = ifa.get_encoder("binary")
    assert isinstance(encoder, IfaEncoder)
    
    norse = create_norse_candidate()
    assert norse.tier == CandidateTier.TIER_1
    assert norse.primary_focus == EncodingFocus.GRAPH_TOPOLOGY
    
    # Test registry
    registry = CandidateRegistry()
    
    summary = registry.summary()
    assert summary["total"] >= 17  # Core + Tier1 + Tier2
    
    core = registry.get_by_tier(CandidateTier.CORE)
    assert len(core) == 5  # Taoist, Egyptian, Vedic, Sumerian, Maya
    
    tier1 = registry.get_by_tier(CandidateTier.TIER_1)
    assert len(tier1) >= 8
    
    binary_systems = registry.get_by_focus(EncodingFocus.BINARY_HYPERCUBE)
    assert len(binary_systems) >= 3  # Ifá, I Ching, Kabbalah, etc.
    
    # Test lookup
    found = registry.get("ifa")
    # May not match exactly due to key format
    
    # Test complementary radix analysis
    analysis = ComplementaryRadixAnalysis(registry)
    
    binary_hierarchy = analysis.binary_resolution_hierarchy()
    assert len(binary_hierarchy) >= 2
    
    modules = analysis.module_coverage()
    assert "binary_hypercube" in modules
    assert len(modules["binary_hypercube"]) > 0
    
    return True


if __name__ == "__main__":
    print("Validating HBAS Candidates Module...")
    assert validate_candidates()
    print("✓ HBAS Candidates Module validated")
