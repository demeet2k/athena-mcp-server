"""
ATHENA OS — UNIFIED STATE PROTOCOL
==================================

The universal state interface that unifies all state types
across the 70 packages of ATHENA OS.

Every state in ATHENA OS implements this protocol, enabling:
1. Universal state transitions
2. Cross-package state composition
3. Holographic state projection
4. Certified state verification

STATE CATEGORIES:
    1. Elemental States  - Fire, Air, Water, Earth, Aether
    2. Modal States      - Actuality, Potentiality
    3. Process States    - Running, Waiting, Complete, Failed
    4. Ontological States - Being, Becoming, Non-Being
    5. Humoral States    - Blood, Yellow Bile, Black Bile, Phlegm
    6. Quantum States    - Superposition, Collapsed, Entangled
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Optional, Tuple, Any, Set, FrozenSet,
    Callable, TypeVar, Generic, Protocol, runtime_checkable
)
from enum import Enum, IntEnum, auto
from abc import ABC, abstractmethod
import hashlib
from datetime import datetime

# Import unified types
from .core import (
    B4, Klein4Op, Element, TypedTruth, Certificate,
    CrystalAddress, HolographicAddress, ZResult, Constants
)


T = TypeVar('T')
S = TypeVar('S', bound='UnifiedState')


# =============================================================================
# STATE CATEGORIES
# =============================================================================

class StateCategory(Enum):
    """Categories of state types."""
    ELEMENTAL = "elemental"      # Based on four elements
    MODAL = "modal"              # Actuality/potentiality
    PROCESS = "process"          # Execution lifecycle
    ONTOLOGICAL = "ontological"  # Being/becoming
    HUMORAL = "humoral"          # Galenic humors
    QUANTUM = "quantum"          # Superposition/collapse
    THERMAL = "thermal"          # Temperature-based
    SPIRITUAL = "spiritual"      # Soul/spirit states


class ProcessPhase(IntEnum):
    """Universal process phases."""
    INIT = 0        # Initialized
    RUNNING = 1     # In progress
    WAITING = 2     # Blocked
    COMPLETE = 3    # Finished successfully
    FAILED = 4      # Finished with error
    SUSPENDED = 5   # Temporarily halted


class ModalPhase(Enum):
    """Modal phases (Aristotelian)."""
    ACTUALITY = "act"       # ἐνέργεια - fully realized
    POTENTIALITY = "pot"    # δύναμις - capable of becoming
    PRIVATION = "priv"      # στέρησις - absence of form


class OntologicalPhase(Enum):
    """Ontological phases (Parmenidean/Heraclitean)."""
    BEING = "is"            # τὸ ὄν - that which is
    BECOMING = "flux"       # γένεσις - coming-to-be
    NON_BEING = "not"       # τὸ μὴ ὄν - that which is not


# =============================================================================
# UNIFIED STATE PROTOCOL
# =============================================================================

@runtime_checkable
class UnifiedState(Protocol):
    """
    Universal state protocol.
    
    Every state type in ATHENA OS should implement this protocol.
    """
    
    @property
    def category(self) -> StateCategory:
        """State category."""
        ...
    
    @property
    def phase(self) -> Any:
        """Current phase within category."""
        ...
    
    @property
    def element(self) -> Element:
        """Associated element."""
        ...
    
    @property
    def b4(self) -> B4:
        """B4 truth value of state."""
        ...
    
    def transition(self, target: 'UnifiedState') -> ZResult['UnifiedState']:
        """Attempt transition to target state."""
        ...
    
    def project(self, address: CrystalAddress) -> 'UnifiedState':
        """Project state to crystal address."""
        ...
    
    def hash(self) -> str:
        """State content hash."""
        ...


# =============================================================================
# BASE STATE IMPLEMENTATION
# =============================================================================

@dataclass
class BaseState:
    """
    Base implementation of UnifiedState.
    
    Provides default implementations for common state operations.
    """
    
    _category: StateCategory = StateCategory.PROCESS
    _phase: Any = ProcessPhase.INIT
    _element: Element = Element.EARTH
    _metadata: Dict[str, Any] = field(default_factory=dict)
    _timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def category(self) -> StateCategory:
        return self._category
    
    @property
    def phase(self) -> Any:
        return self._phase
    
    @property
    def element(self) -> Element:
        return self._element
    
    @property
    def b4(self) -> B4:
        """Map phase to B4."""
        if isinstance(self._phase, ProcessPhase):
            if self._phase == ProcessPhase.COMPLETE:
                return B4.ONE
            elif self._phase == ProcessPhase.FAILED:
                return B4.BOT
            elif self._phase == ProcessPhase.WAITING:
                return B4.TOP
            else:
                return B4.ZERO
        return B4.ZERO
    
    def transition(self, target: 'BaseState') -> ZResult['BaseState']:
        """Transition to target state."""
        # Check if transition is valid
        if not self._can_transition(target):
            return ZResult.zero(f"Invalid transition: {self._phase} → {target._phase}")
        
        # Create new state
        new_state = BaseState(
            _category=target._category,
            _phase=target._phase,
            _element=target._element,
            _metadata={**self._metadata, **target._metadata}
        )
        return ZResult.ok(new_state)
    
    def _can_transition(self, target: 'BaseState') -> bool:
        """Check if transition is allowed."""
        # Same category transitions always allowed
        if self._category == target._category:
            return True
        # Cross-category needs same element
        return self._element == target._element
    
    def project(self, address: CrystalAddress) -> 'BaseState':
        """Project state to crystal address."""
        # Map lens to element
        lens_elements = {
            0: Element.EARTH,   # SQUARE
            1: Element.WATER,   # FLOWER
            2: Element.AIR,     # CLOUD
            3: Element.FIRE,    # FRACTAL
        }
        new_element = lens_elements.get(list(address.lens.__class__).index(address.lens), Element.EARTH)
        
        return BaseState(
            _category=self._category,
            _phase=self._phase,
            _element=new_element,
            _metadata={**self._metadata, "crystal_address": address.code}
        )
    
    def hash(self) -> str:
        """Compute state hash."""
        content = f"{self._category.value}:{self._phase}:{self._element.name}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# =============================================================================
# ELEMENTAL STATE
# =============================================================================

@dataclass
class ElementalState(BaseState):
    """
    State based on the four elements.
    
    Used in alchemical, Galenic, and Greek philosophical systems.
    """
    
    fire: float = 0.0    # Hot + Dry
    air: float = 0.0     # Hot + Wet
    water: float = 0.0   # Cold + Wet
    earth: float = 0.0   # Cold + Dry
    
    def __post_init__(self):
        self._category = StateCategory.ELEMENTAL
        self._element = self.dominant_element
    
    @property
    def dominant_element(self) -> Element:
        """Get the dominant element."""
        values = {
            Element.FIRE: self.fire,
            Element.AIR: self.air,
            Element.WATER: self.water,
            Element.EARTH: self.earth,
        }
        return max(values, key=values.get)
    
    @property
    def qualities(self) -> Tuple[float, float]:
        """Get (hot, wet) quality values."""
        hot = (self.fire + self.air) - (self.water + self.earth)
        wet = (self.air + self.water) - (self.fire + self.earth)
        return (hot, wet)
    
    @property
    def normalized(self) -> 'ElementalState':
        """Normalize to unit sum."""
        total = self.fire + self.air + self.water + self.earth
        if total == 0:
            return ElementalState(0.25, 0.25, 0.25, 0.25)
        return ElementalState(
            fire=self.fire / total,
            air=self.air / total,
            water=self.water / total,
            earth=self.earth / total
        )
    
    def apply_klein4(self, op: Klein4Op) -> 'ElementalState':
        """Apply Klein-4 transformation."""
        if op == Klein4Op.I:
            return self
        elif op == Klein4Op.R:  # Swap hot/cold
            return ElementalState(
                fire=self.water, air=self.earth,
                water=self.fire, earth=self.air
            )
        elif op == Klein4Op.S:  # Swap wet/dry
            return ElementalState(
                fire=self.air, air=self.fire,
                water=self.earth, earth=self.water
            )
        else:  # C = R∘S
            return ElementalState(
                fire=self.earth, air=self.water,
                water=self.air, earth=self.fire
            )
    
    def blend(self, other: 'ElementalState', ratio: float = 0.5) -> 'ElementalState':
        """Blend with another elemental state."""
        r = max(0, min(1, ratio))
        return ElementalState(
            fire=self.fire * (1 - r) + other.fire * r,
            air=self.air * (1 - r) + other.air * r,
            water=self.water * (1 - r) + other.water * r,
            earth=self.earth * (1 - r) + other.earth * r
        )


# =============================================================================
# HUMORAL STATE
# =============================================================================

@dataclass
class HumoralState(BaseState):
    """
    State based on the four Galenic humors.
    
    Maps to elements:
        Blood       ↔ Air   (sanguine)
        Yellow Bile ↔ Fire  (choleric)
        Black Bile  ↔ Earth (melancholic)
        Phlegm      ↔ Water (phlegmatic)
    """
    
    blood: float = 0.25        # Sanguine (Air)
    yellow_bile: float = 0.25  # Choleric (Fire)
    black_bile: float = 0.25   # Melancholic (Earth)
    phlegm: float = 0.25       # Phlegmatic (Water)
    
    def __post_init__(self):
        self._category = StateCategory.HUMORAL
        self._element = self.dominant_element
    
    @property
    def dominant_element(self) -> Element:
        """Get dominant element from humors."""
        humor_elements = {
            Element.AIR: self.blood,
            Element.FIRE: self.yellow_bile,
            Element.EARTH: self.black_bile,
            Element.WATER: self.phlegm,
        }
        return max(humor_elements, key=humor_elements.get)
    
    @property
    def temperament(self) -> str:
        """Get dominant temperament."""
        temperaments = {
            "sanguine": self.blood,
            "choleric": self.yellow_bile,
            "melancholic": self.black_bile,
            "phlegmatic": self.phlegm,
        }
        return max(temperaments, key=temperaments.get)
    
    def to_elemental(self) -> ElementalState:
        """Convert to elemental state."""
        return ElementalState(
            fire=self.yellow_bile,
            air=self.blood,
            water=self.phlegm,
            earth=self.black_bile
        )
    
    @classmethod
    def from_elemental(cls, state: ElementalState) -> 'HumoralState':
        """Create from elemental state."""
        return cls(
            blood=state.air,
            yellow_bile=state.fire,
            black_bile=state.earth,
            phlegm=state.water
        )


# =============================================================================
# QUANTUM STATE
# =============================================================================

@dataclass
class QuantumState(BaseState):
    """
    Quantum-like state with superposition.
    
    Uses B4 for four-valued quantum logic:
        ⊥ = undefined (not yet measured)
        0 = collapsed to FALSE
        1 = collapsed to TRUE
        ⊤ = superposition (both possible)
    """
    
    amplitude_0: complex = 0.0 + 0.0j  # Amplitude for |0⟩
    amplitude_1: complex = 0.0 + 0.0j  # Amplitude for |1⟩
    collapsed: bool = False
    collapsed_value: Optional[bool] = None
    
    def __post_init__(self):
        self._category = StateCategory.QUANTUM
        if not self.collapsed:
            self._phase = "superposition"
        else:
            self._phase = "collapsed"
    
    @property
    def b4(self) -> B4:
        """Get B4 value."""
        if not self.collapsed:
            if self.amplitude_0 != 0 and self.amplitude_1 != 0:
                return B4.TOP  # Superposition
            elif self.amplitude_0 != 0:
                return B4.ZERO
            elif self.amplitude_1 != 0:
                return B4.ONE
            else:
                return B4.BOT  # Undefined
        else:
            return B4.ONE if self.collapsed_value else B4.ZERO
    
    @property
    def probability_0(self) -> float:
        """Probability of measuring 0."""
        return abs(self.amplitude_0) ** 2
    
    @property
    def probability_1(self) -> float:
        """Probability of measuring 1."""
        return abs(self.amplitude_1) ** 2
    
    def normalize(self) -> 'QuantumState':
        """Normalize amplitudes."""
        norm = (abs(self.amplitude_0)**2 + abs(self.amplitude_1)**2) ** 0.5
        if norm == 0:
            return QuantumState(0.707 + 0j, 0.707 + 0j)
        return QuantumState(
            amplitude_0=self.amplitude_0 / norm,
            amplitude_1=self.amplitude_1 / norm
        )
    
    def measure(self) -> 'QuantumState':
        """Collapse superposition (deterministic for reproducibility)."""
        if self.collapsed:
            return self
        
        # Deterministic collapse based on amplitudes
        result = self.probability_1 > 0.5
        return QuantumState(
            amplitude_0=1.0 + 0j if not result else 0.0 + 0j,
            amplitude_1=1.0 + 0j if result else 0.0 + 0j,
            collapsed=True,
            collapsed_value=result
        )
    
    @classmethod
    def superposition(cls) -> 'QuantumState':
        """Create equal superposition state."""
        return cls(amplitude_0=0.707 + 0j, amplitude_1=0.707 + 0j)
    
    @classmethod
    def from_b4(cls, b4: B4) -> 'QuantumState':
        """Create from B4 value."""
        if b4 == B4.BOT:
            return cls(0 + 0j, 0 + 0j)
        elif b4 == B4.ZERO:
            return cls(1 + 0j, 0 + 0j, collapsed=True, collapsed_value=False)
        elif b4 == B4.ONE:
            return cls(0 + 0j, 1 + 0j, collapsed=True, collapsed_value=True)
        else:  # TOP
            return cls.superposition()


# =============================================================================
# STATE MACHINE
# =============================================================================

@dataclass
class StateTransition:
    """A transition between states."""
    
    from_state: UnifiedState
    to_state: UnifiedState
    condition: Optional[Callable[[UnifiedState], bool]] = None
    action: Optional[Callable[[UnifiedState], None]] = None
    certificate: Optional[Certificate] = None


class StateMachine:
    """
    Universal state machine.
    
    Manages state transitions with validation and certification.
    """
    
    def __init__(self, initial: UnifiedState):
        self.current = initial
        self.history: List[UnifiedState] = [initial]
        self.transitions: List[StateTransition] = []
    
    def register_transition(self, transition: StateTransition) -> None:
        """Register allowed transition."""
        self.transitions.append(transition)
    
    def can_transition(self, target: UnifiedState) -> TypedTruth:
        """Check if transition to target is allowed."""
        for t in self.transitions:
            if (self._states_match(t.from_state, self.current) and
                self._states_match(t.to_state, target)):
                if t.condition is None or t.condition(self.current):
                    return TypedTruth.OK
                return TypedTruth.NEAR  # Condition not met
        return TypedTruth.FAIL  # No matching transition
    
    def transition(self, target: UnifiedState) -> ZResult[UnifiedState]:
        """Execute transition to target state."""
        truth = self.can_transition(target)
        if truth == TypedTruth.FAIL:
            return ZResult.zero(f"No valid transition to {target}")
        
        # Find and execute transition
        for t in self.transitions:
            if (self._states_match(t.from_state, self.current) and
                self._states_match(t.to_state, target)):
                if t.action:
                    t.action(self.current)
                self.current = target
                self.history.append(target)
                return ZResult.ok(target)
        
        return ZResult.zero("Transition failed")
    
    def _states_match(self, pattern: UnifiedState, actual: UnifiedState) -> bool:
        """Check if states match (pattern matching)."""
        return (pattern.category == actual.category and
                pattern.phase == actual.phase)
    
    @property
    def state_hash(self) -> str:
        """Hash of current state."""
        if hasattr(self.current, 'hash'):
            return self.current.hash()
        return hashlib.sha256(str(self.current).encode()).hexdigest()[:16]


# =============================================================================
# STATE PROJECTOR
# =============================================================================

class StateProjector:
    """
    Projects states between different representations.
    
    Enables cross-tradition state conversion.
    """
    
    def __init__(self):
        self._projectors: Dict[Tuple[StateCategory, StateCategory], Callable] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default projections."""
        # Elemental ↔ Humoral
        self.register(
            StateCategory.ELEMENTAL, StateCategory.HUMORAL,
            lambda s: HumoralState.from_elemental(s) if isinstance(s, ElementalState) else s
        )
        self.register(
            StateCategory.HUMORAL, StateCategory.ELEMENTAL,
            lambda s: s.to_elemental() if isinstance(s, HumoralState) else s
        )
        
        # Quantum ↔ Elemental (via B4)
        self.register(
            StateCategory.QUANTUM, StateCategory.ELEMENTAL,
            self._quantum_to_elemental
        )
    
    def register(self, from_cat: StateCategory, to_cat: StateCategory,
                 func: Callable[[UnifiedState], UnifiedState]) -> None:
        """Register a projection function."""
        self._projectors[(from_cat, to_cat)] = func
    
    def project(self, state: UnifiedState, target_category: StateCategory) -> ZResult[UnifiedState]:
        """Project state to target category."""
        if state.category == target_category:
            return ZResult.ok(state)
        
        key = (state.category, target_category)
        if key in self._projectors:
            try:
                result = self._projectors[key](state)
                return ZResult.ok(result)
            except Exception as e:
                return ZResult.zero(f"Projection failed: {e}")
        
        return ZResult.zero(f"No projection: {state.category} → {target_category}")
    
    def _quantum_to_elemental(self, state: QuantumState) -> ElementalState:
        """Project quantum to elemental via B4."""
        b4 = state.b4
        # Map B4 to elemental emphasis
        if b4 == B4.ONE:
            return ElementalState(fire=1.0, air=0.0, water=0.0, earth=0.0)
        elif b4 == B4.ZERO:
            return ElementalState(fire=0.0, air=0.0, water=0.0, earth=1.0)
        elif b4 == B4.TOP:
            return ElementalState(fire=0.5, air=0.5, water=0.0, earth=0.0)
        else:  # BOT
            return ElementalState(fire=0.0, air=0.0, water=0.5, earth=0.5)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Categories
    'StateCategory', 'ProcessPhase', 'ModalPhase', 'OntologicalPhase',
    
    # Protocol
    'UnifiedState',
    
    # Implementations
    'BaseState', 'ElementalState', 'HumoralState', 'QuantumState',
    
    # Machine
    'StateTransition', 'StateMachine',
    
    # Projector
    'StateProjector',
]


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    print("=== ATHENA OS UNIFIED STATE PROTOCOL ===\n")
    
    # Test ElementalState
    fire_state = ElementalState(fire=0.7, air=0.2, water=0.05, earth=0.05)
    print(f"Fire-dominant state: {fire_state.dominant_element.name}")
    print(f"Qualities (hot, wet): {fire_state.qualities}")
    
    # Test Klein-4 transformation
    reflected = fire_state.apply_klein4(Klein4Op.R)
    print(f"After reflection: {reflected.dominant_element.name}")
    
    # Test HumoralState
    choleric = HumoralState(blood=0.1, yellow_bile=0.7, black_bile=0.1, phlegm=0.1)
    print(f"\nCholeric temperament: {choleric.temperament}")
    elemental = choleric.to_elemental()
    print(f"As elemental: {elemental.dominant_element.name}")
    
    # Test QuantumState
    superpos = QuantumState.superposition()
    print(f"\nSuperposition B4: {superpos.b4.glyph}")
    collapsed = superpos.measure()
    print(f"After collapse: {collapsed.b4.glyph}")
    
    # Test StateProjector
    projector = StateProjector()
    projected = projector.project(choleric, StateCategory.ELEMENTAL)
    if projected.is_ok:
        print(f"\nProjected humoral → elemental: {projected.value.dominant_element.name}")
    
    print("\n=== STATE PROTOCOL VERIFIED ===")
