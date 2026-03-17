"""
ATHENA OS - HELLENIC COMPUTATION FRAMEWORK
==========================================
Part VII: The Control Kernel (Stoicism)

THE DICHOTOMY OF CONTROL:
    The fundamental partition of reality:
    - τὰ ἐφ᾽ ἡμῖν (eph' hēmin): Things in our control
    - τὰ οὐκ ἐφ᾽ ἡμῖν (ouk eph' hēmin): Things not in our control
    
    Only the former are proper subjects of concern.

THE PROHAIRESIS (Kernel Space):
    The faculty of choice (προαίρεσις).
    The inviolable core that processes impressions and generates assent.
    This is the "kernel" that cannot be harmed by external events.

THE PNEUMATIC FIELD:
    The Stoic cosmos is a plenum of pneuma (breath/spirit).
    Pneuma has varying degrees of tension (τόνος):
    - Hexis: Cohesion (stones, objects)
    - Physis: Growth (plants)
    - Psyche: Soul (animals)
    - Logikon: Rational soul (humans)

THE TRANQUILITY METRIC:
    ἀταραξία (ataraxia): Undisturbedness
    Goal: Minimize disturbance from external events.

SOURCES:
    - THE_HELLENIC_COMPUTATION_FRAMEWORK.docx Part VII
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Callable, Any
from enum import Enum, auto
import numpy as np
from abc import ABC, abstractmethod

from .foundation import StateVector, Klein4Op


# =============================================================================
# THE DICHOTOMY OF CONTROL
# =============================================================================

class ControlDomain(Enum):
    """
    The Stoic dichotomy of control.
    
    Maps to 2-bit state space:
    - First bit: Internal(1) / External(0)
    - Second bit: Preferred(1) / Dispreferred(0)
    """
    
    INTERNAL_PREFERRED = ("internal preferred", True, True)
    INTERNAL_DISPREFERRED = ("internal dispreferred", True, False)
    EXTERNAL_PREFERRED = ("external preferred", False, True)
    EXTERNAL_DISPREFERRED = ("external dispreferred", False, False)
    
    def __init__(self, name: str, is_internal: bool, is_preferred: bool):
        self._name = name
        self.is_internal = is_internal
        self.is_preferred = is_preferred
    
    def to_state(self) -> StateVector:
        """Convert to 2-bit state."""
        return StateVector(
            1 if self.is_internal else 0,
            1 if self.is_preferred else 0
        )
    
    @classmethod
    def from_state(cls, state: StateVector) -> ControlDomain:
        """Create from state vector."""
        is_internal = state.b1 == 1
        is_preferred = state.b2 == 1
        
        if is_internal and is_preferred:
            return cls.INTERNAL_PREFERRED
        elif is_internal and not is_preferred:
            return cls.INTERNAL_DISPREFERRED
        elif not is_internal and is_preferred:
            return cls.EXTERNAL_PREFERRED
        else:
            return cls.EXTERNAL_DISPREFERRED
    
    def in_our_control(self) -> bool:
        """Is this in our control? (eph' hēmin)"""
        return self.is_internal


@dataclass
class Impression:
    """
    A Stoic impression (φαντασία).
    
    The raw sensory/cognitive input that requires processing.
    """
    
    content: str
    source: str = "external"
    intensity: float = 0.5  # 0-1
    domain: ControlDomain = ControlDomain.EXTERNAL_PREFERRED
    
    # The judgment attached (if any)
    judgment: Optional[str] = None
    value_judgment: float = 0.0  # -1 (bad) to +1 (good)
    
    def is_assented(self) -> bool:
        """Has assent been given to this impression?"""
        return self.judgment is not None
    
    def is_in_control(self) -> bool:
        """Is this impression about something in our control?"""
        return self.domain.in_our_control()


# =============================================================================
# THE PROHAIRESIS (KERNEL SPACE)
# =============================================================================

class AssentState(Enum):
    """States of assent to an impression."""
    
    WITHHELD = 0     # ἐποχή - suspension
    ASSENT = 1       # συγκατάθεσις - assent
    DISSENT = 2      # Not formal Stoic term, but useful


@dataclass
class Prohairesis:
    """
    The faculty of choice (προαίρεσις).
    
    The inviolable kernel that:
    1. Receives impressions
    2. Makes judgments
    3. Generates assent or withholding
    4. Produces impulses to action
    """
    
    # Core state
    tranquility: float = 1.0  # ἀταραξία level (0-1)
    logos_strength: float = 1.0  # Rational faculty strength
    
    # Processing state
    impressions_queue: List[Impression] = field(default_factory=list)
    judgments: Dict[str, AssentState] = field(default_factory=dict)
    
    # Values
    preferred_indifferents: Set[str] = field(default_factory=set)
    dispreferred_indifferents: Set[str] = field(default_factory=set)
    
    def receive_impression(self, impression: Impression) -> None:
        """Receive an impression for processing."""
        self.impressions_queue.append(impression)
    
    def process_impression(self, impression: Impression) -> AssentState:
        """
        Process an impression through rational judgment.
        
        The Stoic discipline: examine if the impression is 
        about something in our control.
        """
        # Check if in control
        if not impression.is_in_control():
            # External: withhold strong value judgment
            # "It is not things that disturb us, but our judgments about things"
            if abs(impression.value_judgment) > 0.5:
                # High value judgment on external → disturbance
                self._disturb(impression.intensity * abs(impression.value_judgment))
            
            # Classify as indifferent
            return AssentState.WITHHELD
        
        # Internal: evaluate and respond
        if impression.value_judgment > 0:
            return AssentState.ASSENT
        elif impression.value_judgment < 0:
            return AssentState.DISSENT
        else:
            return AssentState.WITHHELD
    
    def _disturb(self, amount: float) -> None:
        """Reduce tranquility due to improper judgment."""
        self.tranquility = max(0.0, self.tranquility - amount * 0.1)
    
    def restore_tranquility(self, amount: float = 0.1) -> None:
        """Restore tranquility through philosophical practice."""
        self.tranquility = min(1.0, self.tranquility + amount)
    
    def is_invulnerable(self) -> bool:
        """
        Check if prohairesis is in invulnerable state.
        
        "No one can harm you without your consent."
        """
        return self.tranquility > 0.8 and self.logos_strength > 0.8
    
    def apply_discipline(self, discipline: str) -> None:
        """
        Apply one of the three Stoic disciplines.
        
        - Desire: Wanting only what is in our control
        - Action: Acting appropriately in social roles
        - Assent: Careful judgment of impressions
        """
        if discipline == "desire":
            # Reduce attachment to externals
            self.preferred_indifferents.clear()
            self.restore_tranquility(0.2)
        elif discipline == "action":
            # Strengthen virtue
            self.logos_strength = min(1.0, self.logos_strength + 0.1)
        elif discipline == "assent":
            # Clear impressions with wisdom
            self.impressions_queue.clear()
            self.restore_tranquility(0.1)


# =============================================================================
# THE PNEUMATIC FIELD
# =============================================================================

class PneumaTension(Enum):
    """
    Degrees of pneumatic tension (τόνος).
    
    Higher tension = greater organization/soul.
    """
    
    HEXIS = ("hexis", 1, "cohesion")        # Stones, objects
    PHYSIS = ("physis", 2, "growth")         # Plants
    PSYCHE = ("psyche", 3, "soul")           # Animals
    LOGIKON = ("logikon", 4, "rational soul")  # Humans
    
    def __init__(self, name: str, level: int, description: str):
        self._name = name
        self.level = level
        self.description = description
    
    def __lt__(self, other: PneumaTension) -> bool:
        return self.level < other.level


@dataclass
class PneumaField:
    """
    The Stoic pneuma (πνεῦμα) - the cosmic breath/spirit.
    
    The universe is a continuous plenum of pneuma at varying tensions.
    """
    
    tension: PneumaTension = PneumaTension.HEXIS
    intensity: float = 0.5  # 0-1
    
    # Components of pneuma
    fire_ratio: float = 0.5  # Artistic fire component
    air_ratio: float = 0.5   # Air component
    
    @property
    def total(self) -> float:
        """Total pneuma intensity."""
        return self.fire_ratio + self.air_ratio
    
    def tonos(self) -> float:
        """
        Calculate tension (τόνος).
        
        τόνος = level × intensity × fire_ratio
        """
        return self.tension.level * self.intensity * self.fire_ratio
    
    def can_support(self, required_tension: PneumaTension) -> bool:
        """Check if field can support given tension level."""
        return self.tension.level >= required_tension.level
    
    def elevate(self) -> bool:
        """Attempt to elevate tension level."""
        tensions = list(PneumaTension)
        current_idx = tensions.index(self.tension)
        
        if current_idx < len(tensions) - 1:
            self.tension = tensions[current_idx + 1]
            return True
        return False
    
    def harmonize(self, other: PneumaField) -> float:
        """
        Calculate sympathetic resonance with another field.
        
        The Stoics believed all things are connected through pneuma.
        """
        tension_diff = abs(self.tension.level - other.tension.level)
        intensity_match = 1 - abs(self.intensity - other.intensity)
        
        return intensity_match / (1 + tension_diff)


# =============================================================================
# THE PASSIONS AND VIRTUES
# =============================================================================

class Passion(Enum):
    """
    The four Stoic passions (πάθη) - to be eliminated.
    
    These are irrational movements of the soul based on false judgments.
    """
    
    DESIRE = ("desire", "ἐπιθυμία", "present good", True, True)
    FEAR = ("fear", "φόβος", "future evil", False, True)
    PLEASURE = ("pleasure", "ἡδονή", "present good", True, False)
    DISTRESS = ("distress", "λύπη", "present evil", False, False)
    
    def __init__(self, name: str, greek: str, object_type: str,
                 is_positive: bool, is_future: bool):
        self._name = name
        self.greek = greek
        self.object_type = object_type
        self.is_positive = is_positive
        self.is_future = is_future
    
    def to_state(self) -> StateVector:
        """Map to 2-bit state."""
        return StateVector(
            1 if self.is_positive else 0,
            1 if self.is_future else 0
        )


class Eupathos(Enum):
    """
    The three good emotions (εὐπάθειαι) - rational alternatives to passions.
    
    These are appropriate responses of the sage.
    """
    
    JOY = ("joy", "χαρά", "replaces pleasure")
    CAUTION = ("caution", "εὐλάβεια", "replaces fear")
    WISH = ("wish", "βούλησις", "replaces desire")
    # Note: There is no rational alternative to distress
    
    def __init__(self, name: str, greek: str, replaces: str):
        self._name = name
        self.greek = greek
        self.replaces = replaces


class Virtue(Enum):
    """
    The four cardinal Stoic virtues.
    
    These are forms of knowledge about good and evil.
    """
    
    WISDOM = ("wisdom", "σοφία", "knowledge of good and evil")
    COURAGE = ("courage", "ἀνδρεία", "knowledge of what to endure")
    JUSTICE = ("justice", "δικαιοσύνη", "knowledge of what to distribute")
    TEMPERANCE = ("temperance", "σωφροσύνη", "knowledge of what to choose")
    
    def __init__(self, name: str, greek: str, definition: str):
        self._name = name
        self.greek = greek
        self.definition = definition
    
    def to_state(self) -> StateVector:
        """Map to 2-bit state."""
        mapping = {
            Virtue.WISDOM: StateVector(0, 0),
            Virtue.COURAGE: StateVector(0, 1),
            Virtue.JUSTICE: StateVector(1, 0),
            Virtue.TEMPERANCE: StateVector(1, 1),
        }
        return mapping[self]


# =============================================================================
# THE STOIC KERNEL
# =============================================================================

class StoicKernel:
    """
    The complete Stoic control kernel.
    
    Processes impressions and maintains rational self-governance.
    """
    
    def __init__(self):
        self.prohairesis = Prohairesis()
        self.pneuma = PneumaField(tension=PneumaTension.LOGIKON)
        
        # Virtue development
        self.virtues: Dict[Virtue, float] = {v: 0.5 for v in Virtue}
        
        # Passion suppression
        self.passions: Dict[Passion, float] = {p: 0.0 for p in Passion}
        
        # Event log
        self.event_log: List[Tuple[str, float]] = []
    
    def receive_event(self, event: str, 
                     domain: ControlDomain,
                     intensity: float = 0.5) -> AssentState:
        """
        Process an external event.
        
        The Stoic algorithm:
        1. Receive as impression
        2. Classify (in control / not in control)
        3. Make judgment
        4. Generate response
        """
        # Create impression
        impression = Impression(
            content=event,
            source="external",
            intensity=intensity,
            domain=domain
        )
        
        # Log event
        self.event_log.append((event, self.prohairesis.tranquility))
        
        # Process through prohairesis
        self.prohairesis.receive_impression(impression)
        result = self.prohairesis.process_impression(impression)
        
        return result
    
    def develop_virtue(self, virtue: Virtue, amount: float = 0.1) -> None:
        """Develop a virtue through practice."""
        self.virtues[virtue] = min(1.0, self.virtues[virtue] + amount)
        
        # Virtue development also strengthens logos
        self.prohairesis.logos_strength = min(
            1.0, 
            self.prohairesis.logos_strength + amount * 0.5
        )
    
    def suppress_passion(self, passion: Passion) -> None:
        """Apply rational analysis to suppress a passion."""
        if self.passions[passion] > 0:
            # Wisdom is the key virtue for all passion suppression
            wisdom = self.virtues[Virtue.WISDOM]
            suppression = wisdom * 0.2
            self.passions[passion] = max(0.0, self.passions[passion] - suppression)
    
    def trigger_passion(self, passion: Passion, intensity: float) -> None:
        """Record a passion being triggered."""
        self.passions[passion] = min(1.0, self.passions[passion] + intensity)
        
        # Passions disturb tranquility
        self.prohairesis._disturb(intensity)
    
    def ataraxia_level(self) -> float:
        """
        Calculate overall tranquility level.
        
        ἀταραξία = tranquility - Σ(passions) + Σ(virtues)/4
        """
        passion_sum = sum(self.passions.values())
        virtue_sum = sum(self.virtues.values())
        
        base = self.prohairesis.tranquility
        penalty = passion_sum * 0.2
        bonus = (virtue_sum / 4) * 0.1
        
        return max(0.0, min(1.0, base - penalty + bonus))
    
    def is_sage(self) -> bool:
        """
        Check if the kernel has achieved sage status.
        
        A sage has:
        - All virtues at maximum
        - All passions at zero
        - Perfect tranquility
        """
        all_virtues = all(v >= 0.95 for v in self.virtues.values())
        no_passions = all(p <= 0.05 for p in self.passions.values())
        tranquil = self.ataraxia_level() >= 0.95
        
        return all_virtues and no_passions and tranquil
    
    def apply_memento_mori(self) -> None:
        """
        Apply the memento mori meditation.
        
        Remembering death resets perspective and reduces attachments.
        """
        # Reset all preferences for externals
        self.prohairesis.preferred_indifferents.clear()
        self.prohairesis.dispreferred_indifferents.clear()
        
        # Boost wisdom
        self.develop_virtue(Virtue.WISDOM, 0.2)
        
        # Reduce all passions
        for passion in Passion:
            self.passions[passion] *= 0.5
        
        # Restore significant tranquility
        self.prohairesis.restore_tranquility(0.3)
    
    def status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "tranquility": self.prohairesis.tranquility,
            "ataraxia": self.ataraxia_level(),
            "logos_strength": self.prohairesis.logos_strength,
            "virtues": {v.value[0]: self.virtues[v] for v in Virtue},
            "passions": {p.value[0]: self.passions[p] for p in Passion},
            "is_sage": self.is_sage(),
            "pneuma_tension": self.pneuma.tension.value[0],
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_stoicism() -> bool:
    """Validate Stoic control kernel module."""
    
    # Test ControlDomain
    internal = ControlDomain.INTERNAL_PREFERRED
    assert internal.in_our_control()
    assert internal.to_state() == StateVector(1, 1)
    
    external = ControlDomain.EXTERNAL_DISPREFERRED
    assert not external.in_our_control()
    assert external.to_state() == StateVector(0, 0)
    
    # Test Impression
    imp = Impression(
        content="Someone insulted me",
        domain=ControlDomain.EXTERNAL_DISPREFERRED,
        value_judgment=-0.8
    )
    assert not imp.is_in_control()
    
    # Test Prohairesis
    proh = Prohairesis()
    assert proh.tranquility == 1.0
    
    result = proh.process_impression(imp)
    assert result == AssentState.WITHHELD
    assert proh.tranquility < 1.0  # Should be disturbed
    
    proh.restore_tranquility(0.5)
    assert proh.tranquility > 0.9
    
    # Test PneumaField
    pneuma = PneumaField(tension=PneumaTension.LOGIKON)
    assert pneuma.can_support(PneumaTension.PSYCHE)
    assert pneuma.tonos() > 0
    
    # Test Virtue mapping
    assert Virtue.WISDOM.to_state() == StateVector(0, 0)
    assert Virtue.TEMPERANCE.to_state() == StateVector(1, 1)
    
    # Test StoicKernel
    kernel = StoicKernel()
    
    # Process negative external event
    result = kernel.receive_event(
        "Lost money", 
        ControlDomain.EXTERNAL_DISPREFERRED,
        intensity=0.7
    )
    assert kernel.prohairesis.tranquility < 1.0
    
    # Apply memento mori
    kernel.apply_memento_mori()
    assert kernel.virtues[Virtue.WISDOM] > 0.5
    
    # Develop all virtues
    for virtue in Virtue:
        for _ in range(20):
            kernel.develop_virtue(virtue, 0.05)
    
    status = kernel.status()
    assert status["ataraxia"] > 0.5
    
    return True


if __name__ == "__main__":
    print("Validating Stoic Control Kernel Module...")
    assert validate_stoicism()
    print("✓ Stoic module validated")
    
    # Demo
    print("\n--- Stoic Control Kernel Demo ---")
    
    print("\n1. Dichotomy of Control:")
    for domain in ControlDomain:
        in_ctrl = "YES" if domain.in_our_control() else "NO"
        print(f"   {domain.value[0]}: In our control = {in_ctrl}")
    
    print("\n2. Virtue-State Mapping:")
    for virtue in Virtue:
        state = virtue.to_state()
        print(f"   {virtue.value[0]}: {state} - {virtue.definition}")
    
    print("\n3. Stoic Kernel Simulation:")
    kernel = StoicKernel()
    print(f"   Initial ataraxia: {kernel.ataraxia_level():.2f}")
    
    # Simulate adversity
    events = [
        ("Loss of wealth", ControlDomain.EXTERNAL_DISPREFERRED, 0.8),
        ("Insult from enemy", ControlDomain.EXTERNAL_DISPREFERRED, 0.6),
        ("Chose virtue over pleasure", ControlDomain.INTERNAL_PREFERRED, 0.5),
        ("Sickness of body", ControlDomain.EXTERNAL_DISPREFERRED, 0.7),
    ]
    
    for event, domain, intensity in events:
        result = kernel.receive_event(event, domain, intensity)
        print(f"\n   Event: {event}")
        print(f"   Domain: {domain.value[0]}")
        print(f"   Assent: {result.name}")
        print(f"   Ataraxia: {kernel.ataraxia_level():.2f}")
    
    print("\n   Applying memento mori meditation...")
    kernel.apply_memento_mori()
    print(f"   Ataraxia after meditation: {kernel.ataraxia_level():.2f}")
    
    print("\n4. Final Status:")
    status = kernel.status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v:.2f}")
        else:
            print(f"   {key}: {value}")
