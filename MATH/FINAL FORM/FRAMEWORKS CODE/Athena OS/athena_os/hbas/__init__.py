"""
ATHENA OS - HBAS-Ω: UNIFIED ENCODING DETECTION PROTOCOL
========================================================
Comparative Analysis Framework for Ancient Computational Systems

The HBAS-Ω protocol provides a systematic method for detecting and
analyzing computational structures encoded in ancient knowledge systems.

DETECTION METHODOLOGY:

TIER 0 - BASELINE REQUIREMENTS (Hard Filter):
    B0: Bronze Age temporal overlap or continuity
    B1: Specialist class with multi-generational transmission
    B2: Monumental architecture with geometric intentionality
    B3: Persistent notation system
    
    Fail any → NOT an HBAS candidate

TIER 1 - CORE HOLOGRAPHIC CRITERIA:
    H1: State Space Container (infinite potentiality)
    H2: Operator Alphabet (3-7 generators)
    H3: Non-Commutative Operations
    H4: Multi-Cycle Time Lattice
    H5: Bridging Principle (Physics = Ethics = Law)
    H6: Error Correction Protocols
    H7: Holographic Projection (Multi-Medium Mirroring)
    H8: Writing System as Mathematical Encoding

TIER 2 - STRUCTURAL/MATHEMATICAL DEPTH:
    M1: Lie Algebraic Structure
    M2: Eigenmode Thinking
    M3: Topological Protection Concepts
    M4: Vacuum/Ground State
    M5: Scale Invariance

ENCODER TYPES:
    1. Binary/Hypercube - Ifá (256), I Ching (64)
    2. Graph/World-Tree - Yggdrasil, Kabbalah
    3. Spectral/Harmonic - Pythagorean intervals
    4. Metrological - Sumerian base-60, Maya base-20
    5. Transition/Repair - Egyptian Duat, Tibetan Bardo

THE COMPLEMENTARY RADIX THESIS:
    Ancient civilizations developed COMPLEMENTARY, not competing,
    mathematical frameworks. Each culture holds a different MODULE
    of the same universal computational machine.

CONFIRMED SYSTEMS (Core + Tier 1):
    - Taoist/I Ching: Binary Q_6 (64 states)
    - Egyptian/KHEMET: Rigged Hilbert Space + QECC
    - Vedic: Consciousness Hilbert Space
    - Sumerian/ŠAR-60: Sexagesimal Control
    - Maya/Q-Maya: Discrete-Time Calendar Lattice
    - Ifá/Yoruba: Binary Q_8 (256 states)
    - Norse/Yggdrasil: 9-World Graph
    - Kabbalistic: 10-Sefirot Tree
    - Pythagorean: Spectral Harmonics
    - Tibetan: Bardo Transition Matrix
    - Zoroastrian: Dual-Phase Dynamics
"""

from __future__ import annotations

# =============================================================================
# DETECTION MODULE
# =============================================================================

from .detection import (
    # Tiers
    DetectionTier,
    CriterionResult,
    
    # Tier 0 Criteria
    BaselineCriterion,
    B0_TemporalOverlap,
    B1_SpecialistClass,
    B2_MonumentalArchitecture,
    B3_NotationSystem,
    
    # Tier 1 Criteria
    HolographicCriterion,
    H1_StateSpaceContainer,
    H2_OperatorAlphabet,
    H3_NonCommutativeOps,
    H4_MultiCycleTimeLattice,
    H5_BridgingPrinciple,
    H6_ErrorCorrection,
    H7_HolographicProjection,
    H8_MathematicalWriting,
    
    # Detector
    HBASDetector,
    
    validate_detection,
)

# =============================================================================
# ENCODERS MODULE
# =============================================================================

from .encoders import (
    # Types
    EncoderType,
    
    # Binary Encoders
    BinaryEncoder,
    IfaEncoder,
    IChingEncoder,
    
    # Graph Encoders
    GraphEncoder,
    YggdrasilEncoder,
    SefirotEncoder,
    
    # Spectral Encoders
    SpectralEncoder,
    PythagoreanEncoder,
    
    # Metrological Encoders
    MetrologicalEncoder,
    SumerianEncoder,
    MayaEncoder,
    
    # Transition Encoders
    TransitionEncoder,
    BardoEncoder,
    DuatEncoder,
    
    # Factory
    EncoderFactory,
    
    validate_encoders,
)

# =============================================================================
# CANDIDATES MODULE
# =============================================================================

from .candidates import (
    # Classification
    CandidateTier,
    EncodingFocus,
    
    # Candidate System
    CandidateSystem,
    
    # Candidate Creators
    create_ifa_candidate,
    create_norse_candidate,
    create_zoroastrian_candidate,
    create_tibetan_candidate,
    create_pythagorean_candidate,
    create_kabbalistic_candidate,
    create_dogon_candidate,
    create_polynesian_candidate,
    create_incan_candidate,
    create_celtic_candidate,
    create_japanese_candidate,
    create_minoan_candidate,
    create_taoist_candidate,
    create_egyptian_candidate,
    create_vedic_candidate,
    create_sumerian_candidate,
    create_maya_candidate,
    
    # Registry
    CandidateRegistry,
    
    # Analysis
    ComplementaryRadixAnalysis,
    
    validate_candidates,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_hbas() -> bool:
    """Validate complete HBAS-Ω module."""
    assert validate_detection()
    assert validate_encoders()
    assert validate_candidates()
    return True


# =============================================================================
# CONVENIENCE CLASSES
# =============================================================================

class HBASFramework:
    """
    The Complete HBAS-Ω Framework.
    
    Integrates detection, encoding, and candidate analysis
    for unified study of ancient computational systems.
    """
    
    def __init__(self):
        # Components
        self.detector = HBASDetector()
        self.registry = CandidateRegistry()
        self.radix_analysis = ComplementaryRadixAnalysis(self.registry)
    
    def detect_system(self, evidence: dict) -> dict:
        """
        Detect if evidence indicates an HBAS system.
        
        Returns full evaluation with tier classification.
        """
        return self.detector.full_evaluation(evidence)
    
    def get_candidate(self, name: str):
        """Get candidate system by name."""
        return self.registry.get(name)
    
    def get_by_encoding(self, focus: EncodingFocus):
        """Get all candidates with encoding focus."""
        return self.registry.get_by_focus(focus)
    
    def get_binary_hierarchy(self) -> dict:
        """Get binary resolution hierarchy (64 → 256)."""
        return self.radix_analysis.binary_resolution_hierarchy()
    
    def get_module_coverage(self) -> dict:
        """Get which modules each culture encodes."""
        return self.radix_analysis.module_coverage()
    
    def summary(self) -> dict:
        """Get framework summary."""
        return {
            "registry": self.registry.summary(),
            "binary_systems": self.get_binary_hierarchy(),
            "module_coverage": self.get_module_coverage()
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Detection
    "DetectionTier", "CriterionResult",
    "BaselineCriterion",
    "B0_TemporalOverlap", "B1_SpecialistClass",
    "B2_MonumentalArchitecture", "B3_NotationSystem",
    "HolographicCriterion",
    "H1_StateSpaceContainer", "H2_OperatorAlphabet",
    "H3_NonCommutativeOps", "H4_MultiCycleTimeLattice",
    "H5_BridgingPrinciple", "H6_ErrorCorrection",
    "H7_HolographicProjection", "H8_MathematicalWriting",
    "HBASDetector",
    
    # Encoders
    "EncoderType",
    "BinaryEncoder", "IfaEncoder", "IChingEncoder",
    "GraphEncoder", "YggdrasilEncoder", "SefirotEncoder",
    "SpectralEncoder", "PythagoreanEncoder",
    "MetrologicalEncoder", "SumerianEncoder", "MayaEncoder",
    "TransitionEncoder", "BardoEncoder", "DuatEncoder",
    "EncoderFactory",
    
    # Candidates
    "CandidateTier", "EncodingFocus", "CandidateSystem",
    "CandidateRegistry", "ComplementaryRadixAnalysis",
    
    # Framework
    "HBASFramework",
    
    # Validation
    "validate_hbas",
]

__version__ = "1.0.0"
__module_name__ = "hbas"


if __name__ == "__main__":
    print("=" * 70)
    print("ATHENA OS - HBAS-Ω: UNIFIED ENCODING DETECTION PROTOCOL")
    print("Comparative Analysis of Ancient Computational Systems")
    print("=" * 70)
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_hbas():
        print("✓ All components validated")
    
    # Demo
    print("\n--- Framework Demo ---")
    
    framework = HBASFramework()
    
    print("\nRegistry Summary:")
    summary = framework.summary()
    print(f"  Total systems: {summary['registry']['total']}")
    print(f"  By tier: {summary['registry']['by_tier']}")
    
    print("\nBinary Resolution Hierarchy:")
    for name, states in summary['binary_systems'].items():
        print(f"  {name}: {states} states (2^{int(np.log2(states))})")
    
    print("\nModule Coverage:")
    for module, systems in summary['module_coverage'].items():
        if systems:
            print(f"  {module}:")
            for sys in systems[:3]:
                print(f"    - {sys}")
    
    print("\n--- Detection Demo ---")
    
    # Test Egyptian-style evidence
    evidence = {
        "earliest_date": -3000,
        "priest_class": True,
        "training_lineages": True,
        "monuments": True,
        "geometric_intentionality": True,
        "writing_system": True,
        "container_name": "Nun",
        "infinite_potential": True,
        "generative": True,
        "operators": ["Ra", "Osiris", "Isis", "Horus", "Set"],
        "bridging_term": "Ma'at",
        "unified_domains": ["cosmic", "justice", "truth"],
        "anomaly_detection": True,
        "correction_ritual": True
    }
    
    result = framework.detect_system(evidence)
    print(f"Detection result: {result['classification']}")
    print(f"Tier 0 pass: {result['tier0_pass']}")
    print(f"Tier 1 score: {result['tier1_score']:.2f}")
    
    print("\n" + "=" * 70)


# Import numpy for demo
import numpy as np
