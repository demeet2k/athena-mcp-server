"""
ATHENA OS - IFÁ KERNEL: ỌPẸ́-256 COMPUTATIONAL ONTOLOGY
========================================================
The 8-Bit Binary State Machine from West African Cosmology

ỌPẸ́-256: THE HIGH-RESOLUTION BINARY EXTENSION

Core Axiom: Reality is a 256-State Machine
    |Ψ(t)⟩ = Σₖ cₖ(t)|Odù_k⟩, k ∈ {1, 2, ..., 256}

MODULES:

    hypercube.py   - Q₈ Boolean Hypercube (256 Odù states)
    orisha.py      - Orisha Operator Algebra
    divination.py  - Measurement Protocol + Ebó
    ase.py         - Àṣẹ Information Flux

MATHEMATICAL STRUCTURE:

    STATE SPACE (Q₈):
        - 256 vertices (Odù)
        - 1024 edges (transitions)
        - 16 × 16 tensor decomposition
        - Bipartite (even/odd parity)

    OPERATOR ALGEBRA (ORISHA):
        - Tier 1: Creation operators (Obàtálá, Èṣù, Ọrúnmìlà)
        - Tier 2: Dynamical operators (Ògún, Ṣàngó, Yemọja, Ọ̀ṣun, Ọya)
        - Tier 3: Specialized operators

    MEASUREMENT (DIVINATION):
        - Ọ̀pẹ̀lẹ̀ casting: 8-bit measurement
        - State collapse: |Ψ⟩ → |Odù_k⟩

    ERROR CORRECTION (EBÓ):
        - Rírú: Amplification
        - Ẹ̀tùtù: Attenuation
        - Ìdájọ́: Phase correction

    INFORMATION DYNAMICS (ÀṢẸ):
        - Conserved flux
        - Character tensor (Ìwà)
        - Destiny alignment (Orí)

COMPLEMENTARY RADIX SYSTEMS:
    | System     | Base  | Domain         |
    |------------|-------|----------------|
    | I Ching    | 2⁶=64 | Low-res binary |
    | Ifá        | 2⁸=256| High-res binary|
    | Sumerian   | 60    | Coordinates    |
    | Maya       | 20    | Calendar       |
    | Vedic      | ∞     | Consciousness  |

VERSION: 1.0.0
CODENAME: "Àṣẹ"
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
import numpy as np

__version__ = "1.0.0"
__codename__ = "Àṣẹ"
__author__ = "ATHENA OS"

# =============================================================================
# HYPERCUBE MODULE
# =============================================================================

from .hypercube import (
    # Enums
    PrincipalOdu,
    MEJI_PATTERNS,
    PATTERN_TO_MEJI,
    
    # Core classes
    Odu,
    Q8Hypercube,
    OduSuperposition,
    IwaTensor,
)

# =============================================================================
# ORISHA MODULE
# =============================================================================

from .orisha import (
    # Enums
    OrishaTier,
    OrishaType,
    
    # Core classes
    Orisha,
    OrishaGenerator,
    OrishaFactory,
    OrishaAlgebra,
)

# =============================================================================
# DIVINATION MODULE
# =============================================================================

from .divination import (
    # Enums
    CastingMethod,
    CastingResult,
    EboType,
    EboStatus,
    
    # Data classes
    DivinationQuery,
    CastResult,
    DivinationReading,
    EboPrescription,
    
    # Engines
    CastingEngine,
    EboEngine,
    DivinationSystem,
)

# =============================================================================
# ÀṢẸ MODULE
# =============================================================================

from .ase import (
    # Enums
    AseType,
    
    # Data classes
    AseQuantum,
    Ori,
    
    # Systems
    AseField,
    IwaEvolution,
    AseSystem,
)


# =============================================================================
# INTEGRATED IFÁ SYSTEM
# =============================================================================

class IfaKernel:
    """
    Complete IFÁ Computational Kernel.
    
    Integrates:
    - Q₈ Hypercube (state space)
    - Orisha Algebra (operators)
    - Divination System (measurement)
    - Àṣẹ System (information dynamics)
    """
    
    def __init__(self, seed: Optional[int] = None):
        # State space
        self.q8 = Q8Hypercube()
        
        # Operator algebra
        self.algebra = OrishaAlgebra(self.q8)
        
        # Divination
        self.divination = DivinationSystem(self.q8, seed)
        
        # Àṣẹ dynamics
        self.ase = AseSystem(self.q8)
        
        # Current system state (default: uniform superposition)
        self._state = OduSuperposition.uniform()
    
    @property
    def state(self) -> OduSuperposition:
        """Get current system state."""
        return self._state
    
    @state.setter
    def state(self, value: OduSuperposition) -> None:
        """Set system state."""
        self._state = value
    
    def get_odu(self, index: int) -> Odu:
        """Get Odù by index."""
        return self.q8.get_odu(index)
    
    def get_meji(self, principal: PrincipalOdu) -> Odu:
        """Get a principal Meji."""
        return self.q8.get_meji(principal)
    
    def apply_orisha(self, orisha_type: OrishaType) -> None:
        """Apply Orisha operator to system state."""
        orisha = self.algebra.get_orisha(orisha_type)
        self._state = orisha.apply_superposition(self._state)
    
    def divine(self, question: str, querent: str = "Client") -> DivinationReading:
        """
        Perform divination on current state.
        
        Collapses superposition and returns reading.
        """
        reading = self.divination.divine_with_state(question, self._state)
        
        # Collapse state to measured Odù
        measured = reading.primary_odu.odu_index
        self._state = OduSuperposition.from_odu(self.q8.get_odu(measured))
        
        return reading
    
    def perform_ebo(self, reading: DivinationReading) -> None:
        """Perform ebó to correct state."""
        self._state = self.divination.perform_ebo(reading, self._state)
    
    def create_agent(self, name: str, seed: Optional[int] = None) -> Ori:
        """Create a new agent with destiny."""
        return self.ase.create_agent(name, seed)
    
    def evolve_agent(self, name: str, orisha_type: OrishaType) -> Dict[str, Any]:
        """Apply Orisha action to agent's Ìwà."""
        orisha = self.algebra.get_orisha(orisha_type)
        return self.ase.apply_action_to_agent(name, orisha.matrix)
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete kernel status."""
        return {
            "version": __version__,
            "codename": __codename__,
            "hypercube": self.q8.statistics(),
            "algebra": self.algebra.get_statistics(),
            "divination": self.divination.get_statistics(),
            "ase": self.ase.system_status(),
            "current_state": {
                "entropy": self._state.entropy(),
                "dominant_odu": self._state.dominant_odu(),
                "top_3": self._state.top_k(3)
            }
        }
    
    def reset(self) -> None:
        """Reset to uniform superposition."""
        self._state = OduSuperposition.uniform()


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_ifa_kernel(seed: Optional[int] = None) -> IfaKernel:
    """Create a complete IFÁ kernel."""
    return IfaKernel(seed)


def create_hypercube() -> Q8Hypercube:
    """Create a Q₈ hypercube."""
    return Q8Hypercube()


def create_orisha_algebra(hypercube: Q8Hypercube) -> OrishaAlgebra:
    """Create Orisha algebra."""
    return OrishaAlgebra(hypercube)


def create_divination_system(hypercube: Q8Hypercube, 
                              seed: Optional[int] = None) -> DivinationSystem:
    """Create divination system."""
    return DivinationSystem(hypercube, seed)


def create_ase_system(hypercube: Q8Hypercube) -> AseSystem:
    """Create Àṣẹ system."""
    return AseSystem(hypercube)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_ifa() -> Dict[str, Any]:
    """Validate all IFÁ modules."""
    from .hypercube import validate_hypercube
    from .orisha import validate_orisha
    from .divination import validate_divination
    from .ase import validate_ase
    
    results = {}
    
    try:
        results["hypercube"] = validate_hypercube()
    except Exception as e:
        results["hypercube"] = f"FAILED: {e}"
    
    try:
        results["orisha"] = validate_orisha()
    except Exception as e:
        results["orisha"] = f"FAILED: {e}"
    
    try:
        results["divination"] = validate_divination()
    except Exception as e:
        results["divination"] = f"FAILED: {e}"
    
    try:
        results["ase"] = validate_ase()
    except Exception as e:
        results["ase"] = f"FAILED: {e}"
    
    # Test integration
    try:
        kernel = IfaKernel(seed=42)
        
        # Test basic operations
        assert kernel.q8.statistics()["vertices"] == 256
        
        # Test divination
        reading = kernel.divine("Test question?")
        assert reading.primary_odu is not None
        
        # Test Orisha application
        kernel.reset()
        kernel.apply_orisha(OrishaType.ESU)
        
        # Test agent creation
        ori = kernel.create_agent("test", seed=42)
        assert ori is not None
        
        # Test agent evolution
        result = kernel.evolve_agent("test", OrishaType.OGUN)
        assert "current_coherence" in result
        
        # Test status
        status = kernel.get_status()
        assert "hypercube" in status
        
        results["integration"] = True
    except Exception as e:
        results["integration"] = f"FAILED: {e}"
    
    passed = sum(1 for v in results.values() if v is True)
    total = len(results)
    results["summary"] = f"{passed}/{total} modules validated"
    
    return results


def get_info() -> Dict[str, Any]:
    """Get module information."""
    return {
        "name": "IFÁ Kernel - Ọpẹ́-256",
        "version": __version__,
        "codename": __codename__,
        "modules": [
            "hypercube (Q₈)",
            "orisha (operators)",
            "divination (measurement)",
            "ase (information flux)"
        ],
        "state_space": "256 = 2⁸",
        "description": "8-bit binary state machine from West African cosmology"
    }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("IFÁ KERNEL - ỌPẸ́-256")
    print("=" * 60)
    
    info = get_info()
    print(f"\nVersion: {info['version']}")
    print(f"Codename: {info['codename']}")
    print(f"State Space: {info['state_space']}")
    
    print("\n--- Validating All Modules ---")
    results = validate_ifa()
    
    for module, status in results.items():
        if module != "summary":
            symbol = "✓" if status is True else "✗"
            print(f"  {symbol} {module}")
    
    print(f"\n{results['summary']}")
    
    print("\n--- Quick Demo ---")
    kernel = create_ifa_kernel(seed=42)
    
    # Show hypercube stats
    stats = kernel.q8.statistics()
    print(f"\nQ₈ Hypercube:")
    print(f"  Vertices: {stats['vertices']}")
    print(f"  Edges: {stats['edges']}")
    print(f"  Diameter: {stats['diameter']}")
    
    # Perform divination
    print("\n--- Divination Demo ---")
    reading = kernel.divine("What is my path?", "Seeker")
    print(f"Odù: {reading.primary_odu.odu.name}")
    print(f"Pattern: {reading.primary_odu.binary}")
    print(f"Fortune: {'Ire' if reading.primary_odu.is_ire else 'Ibi'}")
    
    # Create agent
    print("\n--- Agent Demo ---")
    ori = kernel.create_agent("Traveler", seed=123)
    print(f"Destiny Odù: {ori.name}")
    
    # Evolve
    result = kernel.evolve_agent("Traveler", OrishaType.OGUN)
    print(f"After Ògún: Coherence = {result['current_coherence']:.4f}")
