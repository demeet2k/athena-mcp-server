"""
ATHENA OS - EPICS: THE CRASH LOGS
==================================
Epic Narratives as Encoded System Manuals

CONCEPTUAL REFRAMING:
    Epics are not literature but DESIGNED ARTIFACTS serving:
    - DATA ARCHIVE: High-resolution recordings of extreme states
    - SIMULATION LOG: Step-by-step execution traces
    - PROTOCOL LIBRARY: Procedures, constraints, warnings

EACH EPIC IS A MODULE IN THE EPIC OS LIBRARY:
    Pre-run simulations and crash logs encoding how human systems
    behave at the edge of their capacities.

MODULES:

1. EPIC REGISTRY
   - Catalog of all major epics across cultures
   - System designations and objectives
   - Failure modes and patches

2. STATE EXTRACTION
   - State variables (political, social, moral, psychological, cosmic)
   - State vectors and state spaces
   - Qualitative-to-quantitative mapping

3. FAILURE MODES
   - Crash signatures (rage overflow, legitimacy loss, daemon leak, etc.)
   - Error injection points and propagation patterns
   - Severity classification

4. PROTOCOLS
   - Gilgamesh Protocol (Termination/Persistence)
   - Iliad Protocol (Rage Management)
   - Odyssey Protocol (Navigation/Identity)
   - Mahabharata Protocol (System Reset)
   - Beowulf Protocol (Daemon Hunting)

5. MINING
   - 9-pass extraction protocol
   - Cross-epic pattern recognition
   - Epic-learned prior library

OUTPUT:
    A library of "don't do this" and "if you must do this, here's
    the least damaging way" - baked into decision-making before
    running those scenarios in the real world.
"""

from __future__ import annotations

# =============================================================================
# EPIC REGISTRY
# =============================================================================

from .epic_registry import (
    # Enums
    SystemDomain,
    FailureCategory,
    PatchType,
    
    # Epic Entry
    EpicEntry,
    
    # Registry
    EpicRegistry,
    EPIC_REGISTRY,
    
    validate_epic_registry,
)

# =============================================================================
# STATE EXTRACTION
# =============================================================================

from .state_extraction import (
    # Enums
    StateDimension,
    StateScale,
    
    # State Variable
    StateVariable,
    COMMON_VARIABLES,
    
    # State Vector
    StateVector,
    
    # State Space
    StateSpace,
    
    # Extractor
    StateExtractor,
    
    validate_state_extraction,
)

# =============================================================================
# FAILURE MODES
# =============================================================================

from .failure_modes import (
    # Enums
    CrashSeverity,
    PropagationPattern,
    
    # Injection Point
    InjectionPoint,
    
    # Crash Signature
    CrashSignature,
    
    # Library
    FailureModeLibrary,
    
    # Analyzer
    FailureAnalyzer,
    
    # Canonical signatures
    create_rage_overflow_signature,
    create_legitimacy_loss_signature,
    create_daemon_leak_signature,
    create_identity_corruption_signature,
    create_doomed_reset_signature,
    
    validate_failure_modes,
)

# =============================================================================
# PROTOCOLS
# =============================================================================

from .protocols import (
    # Enums
    ProtocolStatus,
    ProtocolPhase,
    
    # Invariant
    Invariant,
    
    # Step
    ProtocolStep,
    
    # Protocol
    Protocol,
    
    # Library
    ProtocolLibrary,
    PROTOCOL_LIBRARY,
    
    # Protocol creators
    create_gilgamesh_protocol,
    create_iliad_protocol,
    create_odyssey_protocol,
    create_mahabharata_protocol,
    create_beowulf_protocol,
    
    validate_protocols,
)

# =============================================================================
# MINING
# =============================================================================

from .mining import (
    # Enums
    MiningPass,
    
    # Narrative structures
    NarrativeSegment,
    NarrativeToken,
    
    # Results
    MiningResult,
    FullMiningResult,
    
    # Miner
    EpicMiner,
    
    validate_mining,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_epics() -> bool:
    """Validate complete epics module."""
    assert validate_epic_registry()
    assert validate_state_extraction()
    assert validate_failure_modes()
    assert validate_protocols()
    assert validate_mining()
    return True


# =============================================================================
# EPIC COMPUTER
# =============================================================================

class EpicComputer:
    """
    The Epic Computer: Complete crash log analysis system.
    
    Mines epics for computational frameworks and provides:
    - Failure mode detection
    - Protocol recommendations
    - Cross-epic pattern recognition
    """
    
    def __init__(self):
        # Core components
        self.registry = EPIC_REGISTRY
        self.protocol_library = PROTOCOL_LIBRARY
        self.failure_library = FailureModeLibrary()
        self.miner = EpicMiner()
        
        # State
        self._mined_epics: Dict[str, FullMiningResult] = {}
    
    def mine_epic(self, name: str) -> Optional[FullMiningResult]:
        """Mine a specific epic by name."""
        epic = self.registry.get(name)
        if not epic:
            return None
        
        result = self.miner.mine(epic)
        self._mined_epics[name] = result
        return result
    
    def mine_all(self) -> Dict[str, FullMiningResult]:
        """Mine all epics in the registry."""
        return self.miner.mine_all()
    
    def detect_failure_pattern(self, 
                               state_variables: List[str]) -> List[CrashSignature]:
        """
        Detect potential failure patterns from current state.
        
        Uses crash signatures as intrusion detection rules.
        """
        return self.failure_library.detect_pattern(state_variables)
    
    def get_protocol_for_failure(self, 
                                 failure: FailureCategory) -> List[Protocol]:
        """Get protocols that address a specific failure mode."""
        return self.protocol_library.get_for_failure(failure)
    
    def build_prior_library(self) -> Dict:
        """
        Build the Epic-Learned Prior library.
        
        A library of warnings and mitigation strategies.
        """
        analyzer = FailureAnalyzer()
        return analyzer.build_prior_library()
    
    def get_cross_epic_patterns(self) -> Dict:
        """Get patterns appearing across multiple epics."""
        return self.miner.get_cross_epic_patterns()
    
    def get_epic_by_domain(self, domain: SystemDomain) -> List[EpicEntry]:
        """Get epics for a specific system domain."""
        return self.registry.get_by_domain(domain)
    
    def execute_protocol(self, protocol_name: str) -> Dict:
        """Execute a named protocol."""
        return self.protocol_library.execute_protocol(protocol_name)
    
    def get_system_status(self) -> Dict:
        """Get status of the Epic Computer."""
        return {
            "epics_registered": len(self.registry),
            "protocols_available": len(self.protocol_library),
            "failure_signatures": len(self.failure_library._signatures),
            "epics_mined": len(self._mined_epics)
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Epic Registry
    "SystemDomain", "FailureCategory", "PatchType",
    "EpicEntry", "EpicRegistry", "EPIC_REGISTRY",
    
    # State Extraction
    "StateDimension", "StateScale",
    "StateVariable", "COMMON_VARIABLES",
    "StateVector", "StateSpace", "StateExtractor",
    
    # Failure Modes
    "CrashSeverity", "PropagationPattern",
    "InjectionPoint", "CrashSignature",
    "FailureModeLibrary", "FailureAnalyzer",
    
    # Protocols
    "ProtocolStatus", "ProtocolPhase",
    "Invariant", "ProtocolStep", "Protocol",
    "ProtocolLibrary", "PROTOCOL_LIBRARY",
    
    # Mining
    "MiningPass", "NarrativeSegment", "NarrativeToken",
    "MiningResult", "FullMiningResult", "EpicMiner",
    
    # Integration
    "EpicComputer",
    
    # Validation
    "validate_epics",
]

__version__ = "1.0.0"
__module_name__ = "epics"


# Type hints
from typing import Dict, List, Optional


if __name__ == "__main__":
    print("=" * 70)
    print("ATHENA OS - EPICS: THE CRASH LOGS")
    print("Epic Narratives as Encoded System Manuals")
    print("=" * 70)
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_epics():
        print("✓ All components validated")
    
    # Demo
    print("\n--- Epic Computer Demo ---")
    
    computer = EpicComputer()
    
    # Status
    print(f"\nSystem Status:")
    status = computer.get_system_status()
    print(f"  Epics Registered: {status['epics_registered']}")
    print(f"  Protocols Available: {status['protocols_available']}")
    print(f"  Failure Signatures: {status['failure_signatures']}")
    
    # Mine an epic
    print(f"\nMining Iliad...")
    result = computer.mine_epic("Iliad")
    if result:
        print(f"  Protocol: {result.protocol.name}")
        print(f"  Completeness: {result.completeness:.0%}")
    
    # Detect failure pattern
    print(f"\nDetecting failure patterns for ['menis', 'kleos']:")
    patterns = computer.detect_failure_pattern(["menis", "kleos"])
    for p in patterns[:3]:
        print(f"  - {p.name}: {p.failure_category.value}")
    
    # Get protocols for rage
    print(f"\nProtocols for RAGE_OVERFLOW:")
    protos = computer.get_protocol_for_failure(FailureCategory.RAGE_OVERFLOW)
    for p in protos:
        print(f"  - {p.name}")
    
    # Prior library
    print(f"\nBuilding Epic-Learned Prior Library...")
    prior = computer.build_prior_library()
    print(f"  Error patterns: {len(prior['error_patterns'])}")
    print(f"  Partial fixes: {len(prior['partial_fixes'])}")
    print(f"  Invariants: {len(prior['invariants'])}")
    
    print("\n" + "=" * 70)
