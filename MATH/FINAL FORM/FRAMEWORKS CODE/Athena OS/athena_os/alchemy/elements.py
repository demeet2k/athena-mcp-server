"""
ATHENA OS - ALCHEMY MODULE: ELEMENTS
====================================
The Four Elements and Quality Framework

THE ELEMENTAL TETRAD:
    Fire  (F) - Hot + Dry
    Air   (A) - Hot + Wet
    Water (W) - Cold + Wet
    Earth (E) - Cold + Dry

THE QUALITY AXES:
    Temperature: Hot (1) ↔ Cold (0)
    Moisture:    Wet (1) ↔ Dry (0)

BIT4 ENCODING:
    (b₁, b₂) where b₁ = Hot/Cold, b₂ = Wet/Dry
    
    Fire  = (1, 0)
    Air   = (1, 1)  
    Water = (0, 1)
    Earth = (0, 0)

THE ELEMENTAL SIMPLEX:
    Δ³ = { (c_F, c_A, c_W, c_E) | cᵢ ≥ 0, Σcᵢ = 1 }
    
    The 3-simplex in 4D space where all valid elemental
    compositions live.

MATHEMATICAL FRAMEWORK:
    State vector: Ψ = (c_F, c_A, c_W, c_E)
    Qualities: H(Ψ) = c_F + c_A (heat), M(Ψ) = c_A + c_W (moisture)
    Balance: Ψ* = (1/4, 1/4, 1/4, 1/4)

SOURCES:
    - THE_MATH_OF_ALCHEMY.docx
    - Greek elemental theory
    - Hippocratic humoral system
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np


# =============================================================================
# ENUMS
# =============================================================================

class Element(Enum):
    """The four classical elements."""
    
    FIRE = "fire"
    AIR = "air"
    WATER = "water"
    EARTH = "earth"


class Quality(Enum):
    """The two quality axes."""
    
    HOT = "hot"
    COLD = "cold"
    WET = "wet"
    DRY = "dry"


class Humor(Enum):
    """The four humors (medical correspondences)."""
    
    YELLOW_BILE = "yellow_bile"   # Fire - Choleric
    BLOOD = "blood"                # Air - Sanguine
    PHLEGM = "phlegm"              # Water - Phlegmatic
    BLACK_BILE = "black_bile"     # Earth - Melancholic


# =============================================================================
# ELEMENT PROPERTIES
# =============================================================================

@dataclass
class ElementProperties:
    """
    Properties of a single element.
    """
    
    element: Element
    symbol: str
    
    # Quality encoding (b₁, b₂)
    is_hot: bool
    is_wet: bool
    
    # Associated humor
    humor: Humor
    
    # Platonic solid correspondence
    platonic_solid: str
    
    # Planetary ruler
    planet: str
    
    @property
    def bit_encoding(self) -> Tuple[int, int]:
        """Get BIT4 encoding."""
        return (1 if self.is_hot else 0, 1 if self.is_wet else 0)
    
    @property
    def temperature(self) -> float:
        """Temperature as float (1=hot, 0=cold)."""
        return 1.0 if self.is_hot else 0.0
    
    @property
    def moisture(self) -> float:
        """Moisture as float (1=wet, 0=dry)."""
        return 1.0 if self.is_wet else 0.0
    
    def is_opposite(self, other: ElementProperties) -> bool:
        """Check if elements are opposites (no shared qualities)."""
        return self.is_hot != other.is_hot and self.is_wet != other.is_wet
    
    def is_adjacent(self, other: ElementProperties) -> bool:
        """Check if elements are adjacent (one shared quality)."""
        shared = (self.is_hot == other.is_hot) + (self.is_wet == other.is_wet)
        return shared == 1


# Standard element definitions
FIRE = ElementProperties(
    element=Element.FIRE,
    symbol="??",
    is_hot=True, is_wet=False,
    humor=Humor.YELLOW_BILE,
    platonic_solid="Tetrahedron",
    planet="Mars"
)

AIR = ElementProperties(
    element=Element.AIR,
    symbol="??",
    is_hot=True, is_wet=True,
    humor=Humor.BLOOD,
    platonic_solid="Octahedron",
    planet="Jupiter"
)

WATER = ElementProperties(
    element=Element.WATER,
    symbol="??",
    is_hot=False, is_wet=True,
    humor=Humor.PHLEGM,
    platonic_solid="Icosahedron",
    planet="Moon"
)

EARTH = ElementProperties(
    element=Element.EARTH,
    symbol="??",
    is_hot=False, is_wet=False,
    humor=Humor.BLACK_BILE,
    platonic_solid="Cube",
    planet="Saturn"
)

# Element registry
ELEMENTS: Dict[Element, ElementProperties] = {
    Element.FIRE: FIRE,
    Element.AIR: AIR,
    Element.WATER: WATER,
    Element.EARTH: EARTH
}


# =============================================================================
# ELEMENTAL STATE
# =============================================================================

@dataclass
class ElementalState:
    """
    Complete elemental state vector.
    
    Ψ = (c_F, c_A, c_W, c_E) on the 3-simplex.
    """
    
    fire: float = 0.25
    air: float = 0.25
    water: float = 0.25
    earth: float = 0.25
    
    def __post_init__(self):
        self._normalize()
    
    def _normalize(self) -> None:
        """Ensure state is on the simplex (sums to 1, all non-negative)."""
        total = self.fire + self.air + self.water + self.earth
        if total > 0:
            self.fire = max(0, self.fire) / total
            self.air = max(0, self.air) / total
            self.water = max(0, self.water) / total
            self.earth = max(0, self.earth) / total
    
    @property
    def vector(self) -> np.ndarray:
        """Get as numpy array."""
        return np.array([self.fire, self.air, self.water, self.earth])
    
    @classmethod
    def from_vector(cls, v: np.ndarray) -> ElementalState:
        """Create from numpy array."""
        return cls(fire=v[0], air=v[1], water=v[2], earth=v[3])
    
    @classmethod
    def balanced(cls) -> ElementalState:
        """Create perfectly balanced state."""
        return cls(0.25, 0.25, 0.25, 0.25)
    
    @classmethod
    def pure(cls, element: Element) -> ElementalState:
        """Create pure elemental state."""
        if element == Element.FIRE:
            return cls(1.0, 0.0, 0.0, 0.0)
        elif element == Element.AIR:
            return cls(0.0, 1.0, 0.0, 0.0)
        elif element == Element.WATER:
            return cls(0.0, 0.0, 1.0, 0.0)
        else:
            return cls(0.0, 0.0, 0.0, 1.0)
    
    @property
    def heat(self) -> float:
        """Total heat H(Ψ) = c_F + c_A."""
        return self.fire + self.air
    
    @property
    def cold(self) -> float:
        """Total cold = c_W + c_E."""
        return self.water + self.earth
    
    @property
    def moisture(self) -> float:
        """Total moisture M(Ψ) = c_A + c_W."""
        return self.air + self.water
    
    @property
    def dryness(self) -> float:
        """Total dryness = c_F + c_E."""
        return self.fire + self.earth
    
    @property
    def dominant_element(self) -> Element:
        """Get the dominant element."""
        v = self.vector
        idx = np.argmax(v)
        return [Element.FIRE, Element.AIR, Element.WATER, Element.EARTH][idx]
    
    @property
    def dominant_humor(self) -> Humor:
        """Get the dominant humor."""
        elem = self.dominant_element
        return ELEMENTS[elem].humor
    
    def distance_from_balance(self) -> float:
        """Euclidean distance from perfect balance."""
        balanced = np.array([0.25, 0.25, 0.25, 0.25])
        return float(np.linalg.norm(self.vector - balanced))
    
    def is_balanced(self, threshold: float = 0.01) -> bool:
        """Check if state is approximately balanced."""
        return self.distance_from_balance() < threshold
    
    def entropy(self) -> float:
        """Compute Shannon entropy of the state."""
        v = self.vector
        v = v[v > 0]  # Filter zeros
        return float(-np.sum(v * np.log2(v)))
    
    def get_imbalance_vector(self) -> np.ndarray:
        """Get vector showing deviation from balance."""
        return self.vector - 0.25
    
    def __str__(self) -> str:
        return (f"ElementalState(F={self.fire:.3f}, A={self.air:.3f}, "
                f"W={self.water:.3f}, E={self.earth:.3f})")


# =============================================================================
# QUALITY STATE
# =============================================================================

@dataclass
class QualityState:
    """
    State in terms of qualities (Heat, Moisture).
    
    H ∈ [0, 1] - Total heat
    M ∈ [0, 1] - Total moisture
    """
    
    heat: float = 0.5
    moisture: float = 0.5
    
    def __post_init__(self):
        self.heat = np.clip(self.heat, 0, 1)
        self.moisture = np.clip(self.moisture, 0, 1)
    
    @classmethod
    def from_elemental(cls, state: ElementalState) -> QualityState:
        """Convert from elemental state."""
        return cls(heat=state.heat, moisture=state.moisture)
    
    def to_elemental(self) -> ElementalState:
        """
        Convert to elemental state.
        
        Given H and M, solve for unique simplex point.
        """
        # Fire = Hot ∩ Dry
        # Air = Hot ∩ Wet
        # Water = Cold ∩ Wet
        # Earth = Cold ∩ Dry
        
        # H = F + A, M = A + W
        # Also: F + A + W + E = 1
        
        # With 2 equations and 4 unknowns, we need constraints
        # Use minimum entropy principle (most uniform given constraints)
        
        H, M = self.heat, self.moisture
        
        # One valid decomposition:
        air = min(H, M)  # Hot ∩ Wet
        fire = H - air
        water = M - air
        earth = 1 - H - M + air
        
        # Normalize if needed
        return ElementalState(fire=fire, air=air, water=water, earth=earth)
    
    @property
    def is_balanced(self) -> bool:
        """Check if qualities are balanced (0.5, 0.5)."""
        return abs(self.heat - 0.5) < 0.01 and abs(self.moisture - 0.5) < 0.01
    
    def distance_from_balance(self) -> float:
        """Distance from (0.5, 0.5)."""
        return np.sqrt((self.heat - 0.5)**2 + (self.moisture - 0.5)**2)


# =============================================================================
# ELEMENTAL SIMPLEX
# =============================================================================

class ElementalSimplex:
    """
    The 3-simplex Δ³ in which all valid elemental compositions live.
    
    Δ³ = { (c_F, c_A, c_W, c_E) | cᵢ ≥ 0, Σcᵢ = 1 }
    """
    
    @staticmethod
    def is_valid(state: ElementalState) -> bool:
        """Check if state is on the simplex."""
        v = state.vector
        return np.all(v >= -1e-10) and abs(np.sum(v) - 1.0) < 1e-6
    
    @staticmethod
    def project_to_simplex(v: np.ndarray) -> np.ndarray:
        """Project a vector onto the simplex."""
        # Ensure non-negative
        v = np.maximum(v, 0)
        # Normalize
        total = np.sum(v)
        if total > 0:
            v = v / total
        else:
            v = np.ones(4) / 4
        return v
    
    @staticmethod
    def vertices() -> List[np.ndarray]:
        """Get the 4 vertices of the simplex (pure elements)."""
        return [
            np.array([1, 0, 0, 0]),  # Fire
            np.array([0, 1, 0, 0]),  # Air
            np.array([0, 0, 1, 0]),  # Water
            np.array([0, 0, 0, 1]),  # Earth
        ]
    
    @staticmethod
    def centroid() -> np.ndarray:
        """Get the centroid (balanced state)."""
        return np.array([0.25, 0.25, 0.25, 0.25])
    
    @staticmethod
    def edges() -> List[Tuple[int, int]]:
        """Get edges of the simplex (adjacent element pairs)."""
        # Adjacent elements share one quality
        return [
            (0, 1),  # Fire-Air (both Hot)
            (1, 2),  # Air-Water (both Wet)
            (2, 3),  # Water-Earth (both Cold)
            (3, 0),  # Earth-Fire (both Dry)
        ]
    
    @staticmethod
    def diagonals() -> List[Tuple[int, int]]:
        """Get diagonals (opposite element pairs)."""
        return [
            (0, 2),  # Fire-Water
            (1, 3),  # Air-Earth
        ]
    
    @staticmethod
    def random_point() -> ElementalState:
        """Generate a random point on the simplex."""
        # Use Dirichlet distribution with all alphas = 1
        v = np.random.dirichlet([1, 1, 1, 1])
        return ElementalState.from_vector(v)
    
    @staticmethod
    def interpolate(state1: ElementalState, state2: ElementalState,
                    t: float) -> ElementalState:
        """Interpolate between two states."""
        v = (1 - t) * state1.vector + t * state2.vector
        return ElementalState.from_vector(v)


# =============================================================================
# ELEMENTAL TRANSFORMATIONS
# =============================================================================

class ElementalTransform:
    """
    Basic elemental transformations.
    """
    
    @staticmethod
    def heat(state: ElementalState, amount: float) -> ElementalState:
        """Apply heat (shift toward Fire/Air)."""
        v = state.vector.copy()
        # Transfer from Cold to Hot
        shift = min(amount, v[2] + v[3])  # Limited by cold elements
        
        # Water → Air, Earth → Fire
        transfer_from_water = min(shift * 0.5, v[2])
        transfer_from_earth = min(shift * 0.5, v[3])
        
        v[2] -= transfer_from_water
        v[1] += transfer_from_water
        v[3] -= transfer_from_earth
        v[0] += transfer_from_earth
        
        return ElementalState.from_vector(v)
    
    @staticmethod
    def cool(state: ElementalState, amount: float) -> ElementalState:
        """Apply cold (shift toward Water/Earth)."""
        v = state.vector.copy()
        shift = min(amount, v[0] + v[1])
        
        # Fire → Earth, Air → Water
        transfer_from_fire = min(shift * 0.5, v[0])
        transfer_from_air = min(shift * 0.5, v[1])
        
        v[0] -= transfer_from_fire
        v[3] += transfer_from_fire
        v[1] -= transfer_from_air
        v[2] += transfer_from_air
        
        return ElementalState.from_vector(v)
    
    @staticmethod
    def moisten(state: ElementalState, amount: float) -> ElementalState:
        """Apply moisture (shift toward Air/Water)."""
        v = state.vector.copy()
        shift = min(amount, v[0] + v[3])
        
        # Fire → Air, Earth → Water
        transfer_from_fire = min(shift * 0.5, v[0])
        transfer_from_earth = min(shift * 0.5, v[3])
        
        v[0] -= transfer_from_fire
        v[1] += transfer_from_fire
        v[3] -= transfer_from_earth
        v[2] += transfer_from_earth
        
        return ElementalState.from_vector(v)
    
    @staticmethod
    def dry(state: ElementalState, amount: float) -> ElementalState:
        """Apply dryness (shift toward Fire/Earth)."""
        v = state.vector.copy()
        shift = min(amount, v[1] + v[2])
        
        # Air → Fire, Water → Earth
        transfer_from_air = min(shift * 0.5, v[1])
        transfer_from_water = min(shift * 0.5, v[2])
        
        v[1] -= transfer_from_air
        v[0] += transfer_from_air
        v[2] -= transfer_from_water
        v[3] += transfer_from_water
        
        return ElementalState.from_vector(v)
    
    @staticmethod
    def balance(state: ElementalState, strength: float) -> ElementalState:
        """Move toward balanced state."""
        centroid = np.array([0.25, 0.25, 0.25, 0.25])
        v = (1 - strength) * state.vector + strength * centroid
        return ElementalState.from_vector(v)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_elements() -> bool:
    """Validate elements module."""
    
    # Test ElementProperties
    assert FIRE.is_hot and not FIRE.is_wet
    assert AIR.is_hot and AIR.is_wet
    assert WATER.is_wet and not WATER.is_hot
    assert EARTH.is_opposite(AIR)
    assert FIRE.is_adjacent(AIR)
    
    # Test ElementalState
    state = ElementalState.balanced()
    assert state.is_balanced()
    assert abs(state.heat - 0.5) < 0.01
    assert abs(state.moisture - 0.5) < 0.01
    
    pure_fire = ElementalState.pure(Element.FIRE)
    assert pure_fire.fire == 1.0
    assert pure_fire.heat == 1.0
    
    # Test simplex
    assert ElementalSimplex.is_valid(state)
    
    random_state = ElementalSimplex.random_point()
    assert ElementalSimplex.is_valid(random_state)
    
    # Test interpolation
    s1 = ElementalState.pure(Element.FIRE)
    s2 = ElementalState.pure(Element.WATER)
    mid = ElementalSimplex.interpolate(s1, s2, 0.5)
    assert abs(mid.fire - 0.5) < 0.01
    assert abs(mid.water - 0.5) < 0.01
    
    # Test transformations
    heated = ElementalTransform.heat(state, 0.1)
    assert heated.heat > state.heat
    
    cooled = ElementalTransform.cool(state, 0.1)
    assert cooled.heat < state.heat
    
    return True


if __name__ == "__main__":
    print("Validating Elements Module...")
    assert validate_elements()
    print("✓ Elements Module validated")
    
    # Demo
    print("\n--- Elemental Framework Demo ---")
    
    print("\nElement Properties:")
    for elem in Element:
        props = ELEMENTS[elem]
        print(f"  {props.symbol} {elem.value}: "
              f"{'Hot' if props.is_hot else 'Cold'}+"
              f"{'Wet' if props.is_wet else 'Dry'} "
              f"= {props.humor.value}")
    
    print("\nElemental States:")
    balanced = ElementalState.balanced()
    print(f"  Balanced: {balanced}")
    print(f"    Heat: {balanced.heat:.2f}, Moisture: {balanced.moisture:.2f}")
    
    print("\n  Pure states:")
    for elem in Element:
        pure = ElementalState.pure(elem)
        print(f"    {elem.value}: {pure}")
    
    print("\nTransformations on balanced state:")
    state = ElementalState.balanced()
    
    heated = ElementalTransform.heat(state, 0.2)
    print(f"  After heating: Heat={heated.heat:.2f}")
    
    moistened = ElementalTransform.moisten(state, 0.2)
    print(f"  After moistening: Moisture={moistened.moisture:.2f}")
