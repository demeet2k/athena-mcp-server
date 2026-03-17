"""
ATHENA OS - EPICS: FAILURE MODES
=================================
Crash Signatures and Error Pattern Analysis

ERROR AND CRASH PATTERN EXTRACTION:
    Diagnose WHAT BREAKS, HOW, and WHY.

CRASH SIGNATURE COMPONENTS:
    1. Error Injection Points - where the fault was introduced
    2. Propagation Path - how the error spread through system
    3. Failure Mode - the specific type of crash
    4. Crash Signature - unique identifier for this failure pattern
    5. Available Patches - what repairs were attempted

FAILURE CATEGORIES:
    - Rage Overflow: Emotional saturation hijacks reward function
    - Legitimacy Loss: Authority collapse and succession failure
    - Daemon Leak: Uncontrolled threat escaping containment
    - Migration Failure: Failed transfer of civilization/identity
    - Identity Corruption: Self-loss through forgetting or transformation
    - Resource Contention: Zero-sum collapse and total war
    - Dharma Violation: Constraint breach triggering cosmic reset
    - Overconfidence: Pride bug and alert-fatigue
    - Doomed Reset: Scheduled catastrophe (Ragnarök pattern)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np

from .epic_registry import EpicEntry, FailureCategory, PatchType, EPIC_REGISTRY


# =============================================================================
# CRASH SEVERITY
# =============================================================================

class CrashSeverity(Enum):
    """Severity levels of system crashes."""
    
    MINOR = "minor"           # Recoverable without intervention
    MODERATE = "moderate"     # Requires local patch
    SEVERE = "severe"         # System degradation
    CRITICAL = "critical"     # Near-total failure
    CATASTROPHIC = "catastrophic"  # Complete system reset required


class PropagationPattern(Enum):
    """Patterns of error propagation."""
    
    LOCAL = "local"           # Contained to single node
    LINEAR = "linear"         # Spreads along chain
    EXPONENTIAL = "exponential"  # Viral spreading
    CASCADE = "cascade"       # Triggers secondary failures
    RECURSIVE = "recursive"   # Self-amplifying


# =============================================================================
# ERROR INJECTION
# =============================================================================

@dataclass
class InjectionPoint:
    """
    Point where error was injected into the system.
    
    The specific action, event, or decision that introduced the fault.
    """
    
    description: str
    agent: str
    action_type: str  # decision, event, external, divine
    state_variable_affected: str
    magnitude: float = 1.0
    
    # Temporal location
    narrative_location: str = ""
    
    def get_vector(self, dimension: int) -> np.ndarray:
        """Get injection as a perturbation vector."""
        vec = np.zeros(dimension)
        # Simplified - in full implementation would map to state index
        vec[0] = self.magnitude
        return vec


# =============================================================================
# CRASH SIGNATURE
# =============================================================================

@dataclass
class CrashSignature:
    """
    Unique identifier for a failure pattern.
    
    Contains the full diagnostic of what went wrong.
    """
    
    # Identity
    name: str
    epic_source: str
    
    # Classification
    failure_category: FailureCategory
    severity: CrashSeverity
    
    # Injection
    injection_points: List[InjectionPoint] = field(default_factory=list)
    
    # Propagation
    propagation_pattern: PropagationPattern = PropagationPattern.LOCAL
    propagation_path: List[str] = field(default_factory=list)
    
    # State at crash
    state_variables_at_threshold: List[str] = field(default_factory=list)
    
    # Consequences
    consequences: List[str] = field(default_factory=list)
    
    # Recovery
    recovery_possible: bool = True
    patches_attempted: List[PatchType] = field(default_factory=list)
    patch_success: bool = False
    
    def get_hash(self) -> str:
        """Get unique hash for this crash signature."""
        import hashlib
        content = f"{self.name}:{self.failure_category.value}:{self.severity.value}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def matches(self, other: 'CrashSignature', threshold: float = 0.7) -> bool:
        """Check if this signature matches another (for pattern detection)."""
        score = 0.0
        
        # Same failure category
        if self.failure_category == other.failure_category:
            score += 0.4
        
        # Same severity
        if self.severity == other.severity:
            score += 0.2
        
        # Similar propagation
        if self.propagation_pattern == other.propagation_pattern:
            score += 0.2
        
        # Overlapping state variables
        overlap = set(self.state_variables_at_threshold) & set(other.state_variables_at_threshold)
        if self.state_variables_at_threshold:
            score += 0.2 * len(overlap) / len(self.state_variables_at_threshold)
        
        return score >= threshold


# =============================================================================
# FAILURE MODE DEFINITIONS
# =============================================================================

def create_rage_overflow_signature() -> CrashSignature:
    """Create the RAGE OVERFLOW crash signature (Iliad pattern)."""
    return CrashSignature(
        name="RAGE_OVERFLOW",
        epic_source="Iliad",
        failure_category=FailureCategory.RAGE_OVERFLOW,
        severity=CrashSeverity.CATASTROPHIC,
        injection_points=[
            InjectionPoint(
                description="Agamemnon takes Achilles' prize",
                agent="Agamemnon",
                action_type="decision",
                state_variable_affected="time",
                magnitude=1.0,
                narrative_location="Book I"
            )
        ],
        propagation_pattern=PropagationPattern.CASCADE,
        propagation_path=[
            "time_violation",
            "menis_activation",
            "withdrawal_from_battle",
            "greek_losses",
            "patroclus_death",
            "rage_overflow"
        ],
        state_variables_at_threshold=["menis", "grief", "kleos"],
        consequences=[
            "Patroclus killed",
            "Hector killed",
            "Achilles' fate sealed",
            "Troy's fall accelerated"
        ],
        recovery_possible=True,
        patches_attempted=[PatchType.MORTALITY_HANDSHAKE],
        patch_success=True
    )


def create_legitimacy_loss_signature() -> CrashSignature:
    """Create the LEGITIMACY LOSS crash signature (Mahabharata pattern)."""
    return CrashSignature(
        name="LEGITIMACY_COLLAPSE",
        epic_source="Mahabharata",
        failure_category=FailureCategory.LEGITIMACY_LOSS,
        severity=CrashSeverity.CATASTROPHIC,
        injection_points=[
            InjectionPoint(
                description="Dice game - stochastic chaos injection",
                agent="Shakuni",
                action_type="event",
                state_variable_affected="dharma",
                magnitude=1.0,
                narrative_location="Sabha Parva"
            ),
            InjectionPoint(
                description="Draupadi's humiliation",
                agent="Duryodhana",
                action_type="decision",
                state_variable_affected="dharma",
                magnitude=1.0,
                narrative_location="Sabha Parva"
            )
        ],
        propagation_pattern=PropagationPattern.CASCADE,
        propagation_path=[
            "dharma_violation",
            "vow_of_vengeance",
            "thirteen_year_exile",
            "failed_negotiation",
            "kurukshetra_war"
        ],
        state_variables_at_threshold=["dharma", "legitimacy", "war_state"],
        consequences=[
            "18-day war",
            "Millions dead",
            "Kuru dynasty destroyed",
            "Kali Yuga initiated"
        ],
        recovery_possible=True,
        patches_attempted=[PatchType.HARD_RESET],
        patch_success=True  # System reset successful
    )


def create_daemon_leak_signature() -> CrashSignature:
    """Create the DAEMON LEAK crash signature (Beowulf pattern)."""
    return CrashSignature(
        name="DAEMON_LEAK",
        epic_source="Beowulf",
        failure_category=FailureCategory.DAEMON_LEAK,
        severity=CrashSeverity.SEVERE,
        injection_points=[
            InjectionPoint(
                description="Grendel attacks Heorot - uncompiled chaos hates order",
                agent="Grendel",
                action_type="external",
                state_variable_affected="threat_level",
                magnitude=1.0,
                narrative_location="Opening"
            )
        ],
        propagation_pattern=PropagationPattern.RECURSIVE,
        propagation_path=[
            "grendel_attacks",
            "grendel_defeated",
            "grendel_mother_attacks",
            "grendel_mother_defeated",
            "dragon_awakens",
            "hero_death"
        ],
        state_variables_at_threshold=["threat_level", "heroic_reputation"],
        consequences=[
            "Heorot cleansed but temporarily",
            "Recursive daemon spawning",
            "Hero ultimately sacrificed"
        ],
        recovery_possible=True,
        patches_attempted=[PatchType.DAEMON_BINDING],
        patch_success=True  # Each daemon bound, but at cost
    )


def create_identity_corruption_signature() -> CrashSignature:
    """Create the IDENTITY CORRUPTION crash signature (Odyssey pattern)."""
    return CrashSignature(
        name="IDENTITY_ERASURE",
        epic_source="Odyssey",
        failure_category=FailureCategory.IDENTITY_CORRUPTION,
        severity=CrashSeverity.MODERATE,
        injection_points=[
            InjectionPoint(
                description="Lotus Eaters - biochemical forgetting attack",
                agent="Environment",
                action_type="external",
                state_variable_affected="identity_vector",
                magnitude=0.5,
                narrative_location="Book IX"
            ),
            InjectionPoint(
                description="Circe - topological transformation",
                agent="Circe",
                action_type="divine",
                state_variable_affected="identity_vector",
                magnitude=0.7,
                narrative_location="Book X"
            )
        ],
        propagation_pattern=PropagationPattern.LINEAR,
        propagation_path=[
            "destination_address_threatened",
            "form_transformation_attempted",
            "identity_lock_procedures_activated",
            "origin_reclaimed"
        ],
        state_variables_at_threshold=["nostos", "identity_vector"],
        consequences=[
            "Crew temporarily lost",
            "Decades of delay",
            "But identity preserved"
        ],
        recovery_possible=True,
        patches_attempted=[PatchType.POLYMORPHIC_ROUTING],
        patch_success=True
    )


def create_doomed_reset_signature() -> CrashSignature:
    """Create the DOOMED RESET crash signature (Ragnarök pattern)."""
    return CrashSignature(
        name="SCHEDULED_APOCALYPSE",
        epic_source="Norse Eddas",
        failure_category=FailureCategory.DOOMED_RESET,
        severity=CrashSeverity.CATASTROPHIC,
        injection_points=[
            InjectionPoint(
                description="System designed with scheduled termination",
                agent="Cosmic_Design",
                action_type="divine",
                state_variable_affected="doom_proximity",
                magnitude=1.0,
                narrative_location="Creation"
            )
        ],
        propagation_pattern=PropagationPattern.CASCADE,
        propagation_path=[
            "fimbulwinter",
            "binding_breaks",
            "giants_march",
            "gods_fall",
            "world_burns",
            "world_reborn"
        ],
        state_variables_at_threshold=["doom_proximity", "curse_chain"],
        consequences=[
            "All gods die",
            "World destroyed",
            "New world emerges"
        ],
        recovery_possible=False,  # By design
        patches_attempted=[],
        patch_success=False  # No patch - this is the design
    )


# =============================================================================
# FAILURE MODE LIBRARY
# =============================================================================

class FailureModeLibrary:
    """
    Library of all known failure modes extracted from epics.
    
    Functions as an INTRUSION DETECTION SYSTEM (IDS) rule set.
    """
    
    def __init__(self):
        self._signatures: Dict[str, CrashSignature] = {}
        self._by_category: Dict[FailureCategory, List[CrashSignature]] = {}
        
        # Load canonical signatures
        self._load_canonical_signatures()
    
    def _load_canonical_signatures(self) -> None:
        """Load canonical crash signatures from epics."""
        
        signatures = [
            create_rage_overflow_signature(),
            create_legitimacy_loss_signature(),
            create_daemon_leak_signature(),
            create_identity_corruption_signature(),
            create_doomed_reset_signature(),
        ]
        
        for sig in signatures:
            self.register(sig)
    
    def register(self, signature: CrashSignature) -> None:
        """Register a crash signature."""
        self._signatures[signature.name] = signature
        
        cat = signature.failure_category
        if cat not in self._by_category:
            self._by_category[cat] = []
        self._by_category[cat].append(signature)
    
    def get(self, name: str) -> Optional[CrashSignature]:
        """Get a crash signature by name."""
        return self._signatures.get(name)
    
    def get_by_category(self, category: FailureCategory) -> List[CrashSignature]:
        """Get all signatures of a category."""
        return self._by_category.get(category, [])
    
    def detect_pattern(self, state_variables: List[str], 
                      threshold: float = 0.5) -> List[CrashSignature]:
        """
        Detect matching crash patterns from current state.
        
        Returns signatures that match the current danger state.
        """
        matches = []
        
        for sig in self._signatures.values():
            overlap = set(state_variables) & set(sig.state_variables_at_threshold)
            if sig.state_variables_at_threshold:
                score = len(overlap) / len(sig.state_variables_at_threshold)
                if score >= threshold:
                    matches.append(sig)
        
        return matches
    
    def get_patches_for_failure(self, 
                               category: FailureCategory) -> List[PatchType]:
        """Get all patches that have been attempted for a failure category."""
        patches = set()
        for sig in self.get_by_category(category):
            patches.update(sig.patches_attempted)
        return list(patches)
    
    def get_statistics(self) -> Dict:
        """Get statistics on the failure mode library."""
        return {
            "total_signatures": len(self._signatures),
            "by_category": {
                cat.value: len(sigs) 
                for cat, sigs in self._by_category.items()
            },
            "recoverable": sum(
                1 for s in self._signatures.values() if s.recovery_possible
            ),
            "unrecoverable": sum(
                1 for s in self._signatures.values() if not s.recovery_possible
            )
        }


# =============================================================================
# FAILURE ANALYZER
# =============================================================================

class FailureAnalyzer:
    """
    Analyzes epic narratives for failure patterns.
    
    Extracts crash signatures and builds the failure mode library.
    """
    
    def __init__(self):
        self.library = FailureModeLibrary()
    
    def analyze_epic(self, epic: EpicEntry) -> List[CrashSignature]:
        """
        Analyze an epic for failure patterns.
        
        Returns extracted crash signatures.
        """
        signatures = []
        
        for failure_mode in epic.failure_modes:
            sig = CrashSignature(
                name=f"{epic.name.upper().replace(' ', '_')}_{failure_mode.value.upper()}",
                epic_source=epic.name,
                failure_category=failure_mode,
                severity=self._estimate_severity(epic, failure_mode),
                state_variables_at_threshold=epic.state_variables,
                patches_attempted=epic.patches,
                patch_success=len(epic.patches) > 0
            )
            signatures.append(sig)
            self.library.register(sig)
        
        return signatures
    
    def _estimate_severity(self, epic: EpicEntry, 
                          failure: FailureCategory) -> CrashSeverity:
        """Estimate crash severity based on epic and failure type."""
        
        # Cosmic domain = catastrophic
        if epic.domain.value == "cosmic":
            return CrashSeverity.CATASTROPHIC
        
        # Doomed reset = catastrophic
        if failure == FailureCategory.DOOMED_RESET:
            return CrashSeverity.CATASTROPHIC
        
        # Rage overflow or dharma violation = severe to catastrophic
        if failure in [FailureCategory.RAGE_OVERFLOW, 
                      FailureCategory.DHARMA_VIOLATION]:
            return CrashSeverity.SEVERE
        
        # Identity corruption = moderate
        if failure == FailureCategory.IDENTITY_CORRUPTION:
            return CrashSeverity.MODERATE
        
        return CrashSeverity.MODERATE
    
    def cross_reference(self, sig1: CrashSignature, 
                       sig2: CrashSignature) -> Dict:
        """Cross-reference two crash signatures for pattern similarity."""
        return {
            "signature1": sig1.name,
            "signature2": sig2.name,
            "matches": sig1.matches(sig2),
            "shared_category": sig1.failure_category == sig2.failure_category,
            "shared_severity": sig1.severity == sig2.severity,
            "shared_propagation": sig1.propagation_pattern == sig2.propagation_pattern
        }
    
    def build_prior_library(self) -> Dict:
        """
        Build an Epic-Learned Prior library.
        
        A library of "don't do this" and "if you must, here's the least damaging way".
        """
        prior = {
            "error_patterns": {},
            "partial_fixes": {},
            "invariants": []
        }
        
        for sig in self.library._signatures.values():
            # Error patterns
            cat = sig.failure_category.value
            if cat not in prior["error_patterns"]:
                prior["error_patterns"][cat] = []
            prior["error_patterns"][cat].append({
                "name": sig.name,
                "source": sig.epic_source,
                "propagation": sig.propagation_pattern.value,
                "consequences": sig.consequences
            })
            
            # Partial fixes
            if sig.patches_attempted:
                for patch in sig.patches_attempted:
                    if patch.value not in prior["partial_fixes"]:
                        prior["partial_fixes"][patch.value] = []
                    prior["partial_fixes"][patch.value].append({
                        "for_failure": cat,
                        "success": sig.patch_success,
                        "source": sig.epic_source
                    })
        
        # Invariants (extracted from successful patches)
        prior["invariants"] = [
            "Mortality awareness enables de-escalation (Priam-Achilles handshake)",
            "Identity preservation requires active maintenance against forgetting",
            "Daemon containment requires recursive defense (defeating one spawns another)",
            "Soft persistence (monuments/stories) outlasts hard persistence (biological)",
            "System reset may be necessary when constraints are violated beyond repair"
        ]
        
        return prior


# =============================================================================
# VALIDATION
# =============================================================================

def validate_failure_modes() -> bool:
    """Validate failure modes module."""
    
    # Test InjectionPoint
    injection = InjectionPoint(
        description="Test injection",
        agent="TestAgent",
        action_type="decision",
        state_variable_affected="test_var",
        magnitude=0.5
    )
    
    vec = injection.get_vector(5)
    assert len(vec) == 5
    
    # Test CrashSignature
    sig = create_rage_overflow_signature()
    
    assert sig.failure_category == FailureCategory.RAGE_OVERFLOW
    assert sig.severity == CrashSeverity.CATASTROPHIC
    assert len(sig.injection_points) > 0
    
    hash_val = sig.get_hash()
    assert len(hash_val) == 8
    
    # Test matching
    sig2 = create_rage_overflow_signature()
    assert sig.matches(sig2)
    
    sig3 = create_daemon_leak_signature()
    assert not sig.matches(sig3, threshold=0.9)
    
    # Test FailureModeLibrary
    library = FailureModeLibrary()
    
    assert len(library._signatures) >= 5
    
    rage_sigs = library.get_by_category(FailureCategory.RAGE_OVERFLOW)
    assert len(rage_sigs) >= 1
    
    patches = library.get_patches_for_failure(FailureCategory.RAGE_OVERFLOW)
    assert PatchType.MORTALITY_HANDSHAKE in patches
    
    stats = library.get_statistics()
    assert stats["total_signatures"] >= 5
    
    # Test pattern detection
    matches = library.detect_pattern(["menis", "kleos"], threshold=0.3)
    assert len(matches) > 0
    
    # Test FailureAnalyzer
    analyzer = FailureAnalyzer()
    
    gilgamesh = EPIC_REGISTRY.get("Epic of Gilgamesh")
    assert gilgamesh is not None
    
    sigs = analyzer.analyze_epic(gilgamesh)
    assert len(sigs) > 0
    
    prior = analyzer.build_prior_library()
    assert "error_patterns" in prior
    assert "partial_fixes" in prior
    assert "invariants" in prior
    
    return True


if __name__ == "__main__":
    print("Validating Failure Modes Module...")
    assert validate_failure_modes()
    print("✓ Failure Modes Module validated")
