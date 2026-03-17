"""
ATHENA OS - Four Elements Archetype System
==========================================
The elemental foundation: Fire, Air, Water, Earth
with 90° rotation tunneling between adjacent poles.

This implements the core "rotation engine" that allows:
- Domain transitions without information loss
- Shadow pole awareness (conjugate pairs)
- Constraint/gradient balance across archetypes
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Set, Any
from abc import ABC, abstractmethod
import math


# =============================================================================
# THE FOUR ELEMENTS
# =============================================================================

class Element(IntEnum):
    """
    The Four Elemental Archetypes.
    
    Arranged in a square with 90° rotation between adjacent elements:
    
           FIRE
          /    \
       AIR      WATER
          \    /
           EARTH
    
    - Fire ↔ Air (adjacent, 90°)
    - Air ↔ Water (adjacent, 90°)
    - Water ↔ Earth (adjacent, 90°)
    - Earth ↔ Fire (adjacent, 90°)
    - Fire ↔ Water (opposite, 180° - NO direct transition)
    - Air ↔ Earth (opposite, 180° - NO direct transition)
    """
    FIRE = 0    # Initiation, impulse, ignition
    AIR = 1     # Structure, relation, mapping
    WATER = 2   # Adaptation, flow, shaping
    EARTH = 3   # Constraint, embodiment, verification
    
    @property
    def core_function(self) -> str:
        """Core functional description."""
        return {
            Element.FIRE: "Initiation / impulse / ignition",
            Element.AIR: "Structure through relation / mapping / routing",
            Element.WATER: "Adaptation / flow / shaping",
            Element.EARTH: "Constraint / embodiment / verification"
        }[self]
    
    @property
    def pattern_signature(self) -> str:
        """What this element generates/does."""
        return {
            Element.FIRE: "generates energy, pushes phase forward, creates gradient",
            Element.AIR: "builds links, creates models, moves information sideways",
            Element.WATER: "minimizes resistance, smooths discontinuities, converges by flow",
            Element.EARTH: "enforces bounds, locks invariants, turns plan into artifact"
        }[self]
    
    @property
    def system_role(self) -> str:
        """Role in system terms."""
        return {
            Element.FIRE: "drive, will, activation, 'do the first rep'",
            Element.AIR: "language, abstraction, strategy, navigation",
            Element.WATER: "optimization dynamics, gradients, learning, 'become what system needs'",
            Element.EARTH: "proof, tests, production constraints, compression integrity"
        }[self]
    
    @property
    def shadow_mode(self) -> str:
        """Failure/shadow mode when overused."""
        return {
            Element.FIRE: "reckless forcing, premature collapse, overheat",
            Element.AIR: "over-analysis, detachment, endless branching without landing",
            Element.WATER: "drift, dissolving boundaries, avoiding commitment",
            Element.EARTH: "rigidity, over-constraint, stagnation"
        }[self]
    
    @property
    def opposite(self) -> 'Element':
        """Return the opposite element (180° away)."""
        return Element((self.value + 2) % 4)
    
    @property
    def clockwise(self) -> 'Element':
        """Return next element clockwise (90° rotation)."""
        return Element((self.value + 1) % 4)
    
    @property
    def counterclockwise(self) -> 'Element':
        """Return next element counter-clockwise (-90° rotation)."""
        return Element((self.value - 1) % 4)
    
    def can_rotate_to(self, other: 'Element') -> bool:
        """Check if direct rotation is allowed (adjacent only)."""
        return other in (self.clockwise, self.counterclockwise)
    
    def rotation_distance(self, other: 'Element') -> int:
        """Return minimum rotation steps to reach other element."""
        diff = (other.value - self.value) % 4
        return min(diff, 4 - diff)


# =============================================================================
# ELEMENTAL STATE
# =============================================================================

@dataclass
class ElementalState:
    """
    A state vector over the four elements.
    
    Represents the "balance" or "emphasis" across all four archetypes.
    Total weight should sum to 1.0 (normalized) or represent intensity.
    """
    fire: float = 0.25
    air: float = 0.25
    water: float = 0.25
    earth: float = 0.25
    
    def __post_init__(self):
        """Normalize if needed."""
        self._normalize()
    
    def _normalize(self) -> None:
        """Normalize weights to sum to 1."""
        total = self.fire + self.air + self.water + self.earth
        if total > 0:
            self.fire /= total
            self.air /= total
            self.water /= total
            self.earth /= total
    
    def get(self, element: Element) -> float:
        """Get weight for specific element."""
        return [self.fire, self.air, self.water, self.earth][element.value]
    
    def set(self, element: Element, value: float) -> None:
        """Set weight for specific element."""
        if element == Element.FIRE:
            self.fire = value
        elif element == Element.AIR:
            self.air = value
        elif element == Element.WATER:
            self.water = value
        else:
            self.earth = value
        self._normalize()
    
    @property
    def dominant(self) -> Element:
        """Return the dominant element."""
        weights = [self.fire, self.air, self.water, self.earth]
        return Element(weights.index(max(weights)))
    
    @property
    def recessive(self) -> Element:
        """Return the weakest element."""
        weights = [self.fire, self.air, self.water, self.earth]
        return Element(weights.index(min(weights)))
    
    @property
    def balance_score(self) -> float:
        """
        Measure how balanced the state is (0 = one dominant, 1 = perfect balance).
        Uses entropy normalized by max entropy (log(4)).
        """
        weights = [self.fire, self.air, self.water, self.earth]
        entropy = 0.0
        for w in weights:
            if w > 0:
                entropy -= w * math.log(w)
        max_entropy = math.log(4)
        return entropy / max_entropy
    
    @property
    def axis_tension(self) -> Tuple[float, float]:
        """
        Return tension on each axis:
        - Fire-Water axis (opposite pair 1)
        - Air-Earth axis (opposite pair 2)
        
        Positive = first element dominant, Negative = second dominant.
        """
        fire_water = self.fire - self.water
        air_earth = self.air - self.earth
        return (fire_water, air_earth)
    
    def rotate_emphasis(self, direction: int = 1) -> 'ElementalState':
        """
        Rotate emphasis by 90° (1=clockwise, -1=counter-clockwise).
        This shifts which element is dominant.
        """
        weights = [self.fire, self.air, self.water, self.earth]
        if direction > 0:
            # Clockwise: [F,A,W,E] -> [E,F,A,W]
            new_weights = [weights[3], weights[0], weights[1], weights[2]]
        else:
            # Counter-clockwise: [F,A,W,E] -> [A,W,E,F]
            new_weights = [weights[1], weights[2], weights[3], weights[0]]
        return ElementalState(*new_weights)
    
    def blend(self, other: 'ElementalState', ratio: float = 0.5) -> 'ElementalState':
        """Blend two elemental states."""
        return ElementalState(
            fire=self.fire * (1-ratio) + other.fire * ratio,
            air=self.air * (1-ratio) + other.air * ratio,
            water=self.water * (1-ratio) + other.water * ratio,
            earth=self.earth * (1-ratio) + other.earth * ratio
        )
    
    def amplify(self, element: Element, factor: float = 2.0) -> 'ElementalState':
        """Amplify a specific element."""
        weights = [self.fire, self.air, self.water, self.earth]
        weights[element.value] *= factor
        return ElementalState(*weights)
    
    def dampen(self, element: Element, factor: float = 0.5) -> 'ElementalState':
        """Dampen a specific element."""
        return self.amplify(element, factor)
    
    def to_vector(self) -> Tuple[float, float, float, float]:
        """Return as tuple."""
        return (self.fire, self.air, self.water, self.earth)
    
    def __str__(self) -> str:
        return f"[??{self.fire:.2f} ??{self.air:.2f} ??{self.water:.2f} ??{self.earth:.2f}]"


# =============================================================================
# ROTATION ENGINE
# =============================================================================

class RotationEngine:
    """
    The 90° rotation engine for transitioning between elemental domains.
    
    Key rule: You can only rotate to ADJACENT elements.
    - Fire ↔ Air ↔ Water ↔ Earth ↔ Fire
    - Fire and Water are OPPOSITES (no direct transition)
    - Air and Earth are OPPOSITES (no direct transition)
    
    When stuck, don't push harder in same pole - ROTATE into adjacent archetype.
    """
    
    # Adjacency matrix (True = can rotate directly)
    ADJACENT = {
        (Element.FIRE, Element.AIR): True,
        (Element.AIR, Element.FIRE): True,
        (Element.AIR, Element.WATER): True,
        (Element.WATER, Element.AIR): True,
        (Element.WATER, Element.EARTH): True,
        (Element.EARTH, Element.WATER): True,
        (Element.EARTH, Element.FIRE): True,
        (Element.FIRE, Element.EARTH): True,
        # Opposites - no direct rotation
        (Element.FIRE, Element.WATER): False,
        (Element.WATER, Element.FIRE): False,
        (Element.AIR, Element.EARTH): False,
        (Element.EARTH, Element.AIR): False,
    }
    
    # Same element is trivial rotation
    for e in Element:
        ADJACENT[(e, e)] = True
    
    @classmethod
    def can_rotate(cls, source: Element, target: Element) -> bool:
        """Check if direct rotation is allowed."""
        return cls.ADJACENT.get((source, target), False)
    
    @classmethod
    def rotation_path(cls, source: Element, target: Element) -> List[Element]:
        """
        Find the shortest rotation path between two elements.
        
        For adjacent: [source, target]
        For opposite: [source, intermediate, target] (two 90° rotations)
        """
        if source == target:
            return [source]
        
        if cls.can_rotate(source, target):
            return [source, target]
        
        # Opposite - need intermediate step
        # Choose clockwise intermediate
        intermediate = source.clockwise
        return [source, intermediate, target]
    
    @classmethod
    def rotate_state(cls, state: ElementalState, 
                     from_elem: Element, to_elem: Element) -> ElementalState:
        """
        Rotate an elemental state from one element toward another.
        Transfers weight from source to target.
        """
        if not cls.can_rotate(from_elem, to_elem):
            # Need intermediate rotation
            path = cls.rotation_path(from_elem, to_elem)
            result = state
            for i in range(len(path) - 1):
                result = cls.rotate_state(result, path[i], path[i+1])
            return result
        
        # Direct rotation - transfer some weight
        current_weight = state.get(from_elem)
        transfer = current_weight * 0.5  # Transfer half
        
        new_state = ElementalState(*state.to_vector())
        new_state.set(from_elem, current_weight - transfer)
        new_state.set(to_elem, state.get(to_elem) + transfer)
        
        return new_state


# =============================================================================
# SHADOW POLES (Conjugate Pairs)
# =============================================================================

@dataclass
class ShadowPoles:
    """
    When you focus on one pole, its shadow poles become active.
    
    Based on quantum conjugacy:
    - What is SHARP in one lens becomes SPREAD in the conjugate
    - What is SIMPLE in one becomes COMPLEX in the other
    
    Uncertainty relation: ΔA · ΔB ≥ ℏ/2
    """
    primary: Element
    
    @property
    def shadow(self) -> Element:
        """The opposite element is the primary shadow."""
        return self.primary.opposite
    
    @property
    def conjugate_pair(self) -> Tuple[Element, Element]:
        """Return the conjugate pair (primary and shadow)."""
        return (self.primary, self.shadow)
    
    @property
    def orthogonal_pair(self) -> Tuple[Element, Element]:
        """Return the orthogonal pair (the other axis)."""
        if self.primary in (Element.FIRE, Element.WATER):
            return (Element.AIR, Element.EARTH)
        else:
            return (Element.FIRE, Element.WATER)
    
    def compression_cost(self, sharpness: float) -> float:
        """
        Calculate the "spread" in the shadow pole given sharpness in primary.
        Based on uncertainty principle.
        """
        # Sharper in primary = more spread in shadow
        # Using simple inverse relationship
        if sharpness <= 0:
            return float('inf')
        return 1.0 / sharpness
    
    def describe(self) -> str:
        """Describe the shadow relationship."""
        descriptions = {
            Element.FIRE: "When FIRE is dominant (action/impulse), WATER (adaptation) is suppressed. Shadow: drift toward premature commitment.",
            Element.AIR: "When AIR is dominant (abstraction/mapping), EARTH (embodiment) is suppressed. Shadow: endless analysis without grounding.",
            Element.WATER: "When WATER is dominant (flow/optimization), FIRE (will/drive) is suppressed. Shadow: dissolution of boundaries.",
            Element.EARTH: "When EARTH is dominant (constraint/proof), AIR (flexibility/navigation) is suppressed. Shadow: rigidity and stagnation."
        }
        return descriptions[self.primary]


# =============================================================================
# WAVE-PARTICLE DUALITY MAPPING
# =============================================================================

class WaveParticleLens:
    """
    Maps the Four Elements to Quantum Wave-Particle Duality.
    
    The 4-pole square for quantum phenomena:
    1. PARTICLE (event/localized outcome) ~ EARTH
    2. WAVE (amplitude/phase interference) ~ WATER  
    3. SPECTRUM (frequency/momentum composition) ~ AIR
    4. MEASUREMENT (discrete draws from |ψ|²) ~ FIRE
    
    The 90° rotation is the Fourier/basis change transform.
    """
    
    QUANTUM_MAPPING = {
        Element.FIRE: "Measurement/Projection",    # Discrete collapse
        Element.AIR: "Spectrum/Momentum",          # Frequency composition
        Element.WATER: "Wave/Amplitude",           # Phase interference
        Element.EARTH: "Particle/Position"         # Localized event
    }
    
    @classmethod
    def to_quantum(cls, element: Element) -> str:
        """Map element to quantum concept."""
        return cls.QUANTUM_MAPPING[element]
    
    @classmethod
    def fourier_pair(cls, element: Element) -> Element:
        """
        Get the Fourier conjugate element.
        Position ↔ Momentum (Earth ↔ Air)
        Time/Event ↔ Frequency/Wave (Fire ↔ Water)
        """
        return element.opposite
    
    @classmethod
    def uncertainty_bound(cls, delta_primary: float) -> float:
        """
        Given uncertainty in primary variable, compute minimum
        uncertainty in conjugate (Heisenberg-style bound).
        """
        hbar_over_2 = 0.5  # Normalized units
        if delta_primary <= 0:
            return float('inf')
        return hbar_over_2 / delta_primary


# =============================================================================
# ELEMENTAL PROCESSOR
# =============================================================================

class ElementalProcessor:
    """
    Process states through elemental transformations.
    
    Each element has associated operations:
    - FIRE: Activate, push, initiate
    - AIR: Map, connect, analyze
    - WATER: Optimize, flow, adapt
    - EARTH: Constrain, verify, ground
    """
    
    @staticmethod
    def fire_process(data: Any, intensity: float = 1.0) -> Tuple[Any, bool]:
        """
        FIRE: Initiation process.
        Returns (result, success_flag).
        """
        # Fire activates/transforms
        if data is None:
            return (None, False)
        # Simulate activation
        return (data, True)
    
    @staticmethod
    def air_process(data: Any, depth: int = 1) -> Tuple[Any, Dict]:
        """
        AIR: Analysis/mapping process.
        Returns (result, analysis_metadata).
        """
        metadata = {
            "type": type(data).__name__,
            "depth": depth,
            "branches": []
        }
        return (data, metadata)
    
    @staticmethod
    def water_process(data: Any, target: Any, 
                      learning_rate: float = 0.1) -> Tuple[Any, float]:
        """
        WATER: Optimization/adaptation process.
        Returns (adapted_result, residual_error).
        """
        # Simple gradient-style adaptation
        if isinstance(data, (int, float)) and isinstance(target, (int, float)):
            error = target - data
            adapted = data + learning_rate * error
            return (adapted, abs(error))
        return (data, 0.0)
    
    @staticmethod
    def earth_process(data: Any, constraints: List[Callable]) -> Tuple[Any, bool]:
        """
        EARTH: Constraint/verification process.
        Returns (data, all_constraints_satisfied).
        """
        if not constraints:
            return (data, True)
        
        all_satisfied = all(c(data) for c in constraints)
        return (data, all_satisfied)
    
    @classmethod
    def process_by_element(cls, element: Element, data: Any, **kwargs) -> Tuple[Any, Any]:
        """Dispatch to appropriate processor."""
        processors = {
            Element.FIRE: cls.fire_process,
            Element.AIR: cls.air_process,
            Element.WATER: cls.water_process,
            Element.EARTH: cls.earth_process
        }
        return processors[element](data, **kwargs)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_elemental_geometry() -> bool:
    """Validate elemental relationships."""
    # Four elements
    assert len(Element) == 4
    
    # Opposite pairs
    assert Element.FIRE.opposite == Element.WATER
    assert Element.WATER.opposite == Element.FIRE
    assert Element.AIR.opposite == Element.EARTH
    assert Element.EARTH.opposite == Element.AIR
    
    # Adjacency (90° rotation)
    assert Element.FIRE.clockwise == Element.AIR
    assert Element.AIR.clockwise == Element.WATER
    assert Element.WATER.clockwise == Element.EARTH
    assert Element.EARTH.clockwise == Element.FIRE
    
    # Cannot rotate directly between opposites
    assert not RotationEngine.can_rotate(Element.FIRE, Element.WATER)
    assert not RotationEngine.can_rotate(Element.AIR, Element.EARTH)
    
    # Can rotate between adjacent
    assert RotationEngine.can_rotate(Element.FIRE, Element.AIR)
    assert RotationEngine.can_rotate(Element.AIR, Element.WATER)
    
    # Rotation path for opposites has 3 elements (2 steps)
    path = RotationEngine.rotation_path(Element.FIRE, Element.WATER)
    assert len(path) == 3
    
    return True


if __name__ == "__main__":
    print("Validating elemental geometry...")
    assert validate_elemental_geometry()
    print("✓ Four Elements validated")
    
    # Demo
    print("\n=== Four Elements ===")
    for e in Element:
        print(f"\n{e.name}:")
        print(f"  Function: {e.core_function}")
        print(f"  Pattern: {e.pattern_signature}")
        print(f"  Shadow: {e.shadow_mode}")
        print(f"  Opposite: {e.opposite.name}")
    
    print("\n=== Elemental State ===")
    state = ElementalState(fire=0.5, air=0.2, water=0.2, earth=0.1)
    print(f"State: {state}")
    print(f"Dominant: {state.dominant.name}")
    print(f"Balance score: {state.balance_score:.3f}")
    print(f"Axis tension: {state.axis_tension}")
    
    print("\n=== Rotation Demo ===")
    print(f"Fire → Water path: {[e.name for e in RotationEngine.rotation_path(Element.FIRE, Element.WATER)]}")
    
    rotated = RotationEngine.rotate_state(state, Element.FIRE, Element.AIR)
    print(f"After rotating Fire→Air: {rotated}")
    
    print("\n=== Shadow Poles ===")
    shadow = ShadowPoles(Element.FIRE)
    print(shadow.describe())
    
    print("\n=== Quantum Mapping ===")
    for e in Element:
        print(f"{e.name} → {WaveParticleLens.to_quantum(e)}")
