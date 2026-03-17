"""
ATHENA OS - ALCHEMICAL STATE SPACE
==================================
The Mathematical Foundation of Alchemy

From THE_MATH_OF_ALCHEMY.docx:

ALCHEMY AS DYNAMICAL SYSTEM:
    A = (S, O, D)
    S = State space (matter-psyche-process)
    O = Operator family (transformations)
    D = Dynamical law (evolution)

THE ELEMENTAL STATE SPACE V_elem:
    V = R^4 or C^4 with basis {e_F, e_A, e_W, e_E}
    Ψ = c_F·e_F + c_A·e_A + c_W·e_W + c_E·e_E
    
    Elements are orthogonal: ⟨e_i, e_j⟩ = δ_ij

THE QUALITY SPACE Q:
    Q = R^2 with axes (Heat, Moisture)
    H > 0 = hot, H < 0 = cold
    M > 0 = moist, M < 0 = dry
    
    Element-to-Quality mapping Φ:
    Fire → (+1, -1)   hot & dry
    Air  → (+1, +1)   hot & moist
    Water→ (-1, +1)   cold & moist
    Earth→ (-1, -1)   cold & dry

QUALITY MATRIX:
    Q = [[+1, +1, -1, -1],
         [-1, +1, +1, -1]]
    [H, M]^T = Q · [c_F, c_A, c_W, c_E]^T
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum, auto
import math
import cmath
import numpy as np


# =============================================================================
# ELEMENTS
# =============================================================================

class Element(Enum):
    """The Four Elements as basis directions."""
    FIRE = 0    # Hot & Dry
    AIR = 1     # Hot & Moist
    WATER = 2   # Cold & Moist
    EARTH = 3   # Cold & Dry
    
    @property
    def quality_coords(self) -> Tuple[float, float]:
        """Get (Heat, Moisture) coordinates."""
        coords = {
            Element.FIRE: (+1.0, -1.0),
            Element.AIR: (+1.0, +1.0),
            Element.WATER: (-1.0, +1.0),
            Element.EARTH: (-1.0, -1.0)
        }
        return coords[self]
    
    @property
    def opposite(self) -> 'Element':
        """Get opposite element."""
        opposites = {
            Element.FIRE: Element.WATER,
            Element.WATER: Element.FIRE,
            Element.AIR: Element.EARTH,
            Element.EARTH: Element.AIR
        }
        return opposites[self]


# =============================================================================
# ELEMENTAL STATE VECTOR
# =============================================================================

@dataclass
class ElementalState:
    """
    An elemental state vector Ψ ∈ V_elem.
    
    Ψ = c_F·e_F + c_A·e_A + c_W·e_W + c_E·e_E
    
    Coefficients can be real or complex.
    """
    
    fire: complex = 0.0 + 0j
    air: complex = 0.0 + 0j
    water: complex = 0.0 + 0j
    earth: complex = 0.0 + 0j
    
    def __post_init__(self):
        # Ensure complex type
        self.fire = complex(self.fire)
        self.air = complex(self.air)
        self.water = complex(self.water)
        self.earth = complex(self.earth)
    
    @classmethod
    def from_element(cls, element: Element, magnitude: float = 1.0) -> 'ElementalState':
        """Create pure elemental state."""
        state = cls()
        if element == Element.FIRE:
            state.fire = magnitude
        elif element == Element.AIR:
            state.air = magnitude
        elif element == Element.WATER:
            state.water = magnitude
        else:
            state.earth = magnitude
        return state
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'ElementalState':
        """Create from numpy array."""
        return cls(
            fire=complex(arr[0]),
            air=complex(arr[1]),
            water=complex(arr[2]),
            earth=complex(arr[3])
        )
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.fire, self.air, self.water, self.earth], dtype=complex)
    
    @property
    def coefficients(self) -> Tuple[complex, complex, complex, complex]:
        """Get coefficient tuple."""
        return (self.fire, self.air, self.water, self.earth)
    
    @property
    def norm(self) -> float:
        """Euclidean norm ||Ψ||."""
        return math.sqrt(sum(abs(c)**2 for c in self.coefficients))
    
    @property
    def is_real(self) -> bool:
        """Check if all coefficients are real."""
        return all(c.imag == 0 for c in self.coefficients)
    
    def normalize(self) -> 'ElementalState':
        """Return normalized state."""
        n = self.norm
        if n == 0:
            return ElementalState()
        return ElementalState(
            self.fire / n,
            self.air / n,
            self.water / n,
            self.earth / n
        )
    
    def get_distribution(self) -> Dict[Element, float]:
        """
        Get normalized probability-like distribution.
        
        p_i = |c_i| / Σ|c_j|
        """
        magnitudes = [abs(c) for c in self.coefficients]
        total = sum(magnitudes)
        if total == 0:
            return {e: 0.25 for e in Element}
        
        return {
            Element.FIRE: magnitudes[0] / total,
            Element.AIR: magnitudes[1] / total,
            Element.WATER: magnitudes[2] / total,
            Element.EARTH: magnitudes[3] / total
        }
    
    def entropy(self) -> float:
        """
        Shannon entropy of elemental distribution.
        
        S(p) = -Σ p_i ln(p_i)
        """
        dist = self.get_distribution()
        s = 0.0
        for p in dist.values():
            if p > 0:
                s -= p * math.log(p)
        return s
    
    def inner_product(self, other: 'ElementalState') -> complex:
        """Compute inner product ⟨Ψ|Φ⟩."""
        return sum(
            c1.conjugate() * c2 
            for c1, c2 in zip(self.coefficients, other.coefficients)
        )
    
    def __add__(self, other: 'ElementalState') -> 'ElementalState':
        return ElementalState(
            self.fire + other.fire,
            self.air + other.air,
            self.water + other.water,
            self.earth + other.earth
        )
    
    def __mul__(self, scalar: complex) -> 'ElementalState':
        return ElementalState(
            self.fire * scalar,
            self.air * scalar,
            self.water * scalar,
            self.earth * scalar
        )
    
    def __rmul__(self, scalar: complex) -> 'ElementalState':
        return self.__mul__(scalar)


# =============================================================================
# QUALITY SPACE
# =============================================================================

@dataclass
class QualityState:
    """
    A state in quality space Q = R^2.
    
    Axes:
    - H (Heat): positive = hot, negative = cold
    - M (Moisture): positive = moist, negative = dry
    """
    
    heat: float = 0.0
    moisture: float = 0.0
    
    @classmethod
    def from_element(cls, element: Element) -> 'QualityState':
        """Get quality state for pure element."""
        h, m = element.quality_coords
        return cls(h, m)
    
    @property
    def is_hot(self) -> bool:
        return self.heat > 0
    
    @property
    def is_cold(self) -> bool:
        return self.heat < 0
    
    @property
    def is_moist(self) -> bool:
        return self.moisture > 0
    
    @property
    def is_dry(self) -> bool:
        return self.moisture < 0
    
    @property
    def magnitude(self) -> float:
        """Distance from origin."""
        return math.sqrt(self.heat**2 + self.moisture**2)
    
    @property
    def quadrant(self) -> Element:
        """Get corresponding element from quadrant."""
        if self.heat >= 0 and self.moisture < 0:
            return Element.FIRE
        elif self.heat >= 0 and self.moisture >= 0:
            return Element.AIR
        elif self.heat < 0 and self.moisture >= 0:
            return Element.WATER
        else:
            return Element.EARTH
    
    def distance_to(self, other: 'QualityState') -> float:
        """Euclidean distance to another quality state."""
        return math.sqrt(
            (self.heat - other.heat)**2 +
            (self.moisture - other.moisture)**2
        )


# =============================================================================
# QUALITY MAPPING
# =============================================================================

class QualityMapping:
    """
    The linear map Φ: V_elem → Q.
    
    Quality Matrix:
    Q = [[+1, +1, -1, -1],
         [-1, +1, +1, -1]]
    """
    
    # Quality matrix
    Q_MATRIX = np.array([
        [+1, +1, -1, -1],  # Heat row
        [-1, +1, +1, -1]   # Moisture row
    ], dtype=float)
    
    @classmethod
    def map(cls, state: ElementalState) -> QualityState:
        """
        Map elemental state to quality coordinates.
        
        [H, M]^T = Q · c
        """
        c = np.array([
            abs(state.fire),
            abs(state.air),
            abs(state.water),
            abs(state.earth)
        ])
        
        result = cls.Q_MATRIX @ c
        return QualityState(heat=result[0], moisture=result[1])
    
    @classmethod
    def project_dynamics(cls, dPsi: np.ndarray) -> Tuple[float, float]:
        """
        Project elemental dynamics to quality space.
        
        d/dt[H, M]^T = Q · dΨ/dt
        """
        result = cls.Q_MATRIX @ np.abs(dPsi)
        return (result[0], result[1])


# =============================================================================
# THE ARISTOTELIAN SQUARE
# =============================================================================

class AristotelianSquare:
    """
    The Aristotelian Square of Elements in quality space.
    
    Fire ←→ Air
      ↕       ↕
    Earth ←→ Water
    
    Vertices at (±1, ±1) in (H, M) coordinates.
    """
    
    VERTICES = {
        Element.FIRE: (+1.0, -1.0),
        Element.AIR: (+1.0, +1.0),
        Element.WATER: (-1.0, +1.0),
        Element.EARTH: (-1.0, -1.0)
    }
    
    # Adjacent pairs (share one quality)
    ADJACENCIES = [
        (Element.FIRE, Element.AIR),     # Both hot
        (Element.AIR, Element.WATER),    # Both moist
        (Element.WATER, Element.EARTH),  # Both cold
        (Element.EARTH, Element.FIRE)    # Both dry
    ]
    
    # Opposite pairs (share no quality)
    OPPOSITIONS = [
        (Element.FIRE, Element.WATER),
        (Element.AIR, Element.EARTH)
    ]
    
    @classmethod
    def are_adjacent(cls, e1: Element, e2: Element) -> bool:
        """Check if elements are adjacent (share one quality)."""
        return (e1, e2) in cls.ADJACENCIES or (e2, e1) in cls.ADJACENCIES
    
    @classmethod
    def are_opposite(cls, e1: Element, e2: Element) -> bool:
        """Check if elements are opposite."""
        return (e1, e2) in cls.OPPOSITIONS or (e2, e1) in cls.OPPOSITIONS
    
    @classmethod
    def shared_quality(cls, e1: Element, e2: Element) -> Optional[str]:
        """Get shared quality if adjacent."""
        h1, m1 = e1.quality_coords
        h2, m2 = e2.quality_coords
        
        if h1 == h2:
            return "hot" if h1 > 0 else "cold"
        if m1 == m2:
            return "moist" if m1 > 0 else "dry"
        return None
    
    @classmethod
    def transformation_path(cls, start: Element, end: Element) -> List[Element]:
        """
        Get transformation path between elements.
        
        Adjacent elements: direct path
        Opposite elements: two-step path via shared quality
        """
        if start == end:
            return [start]
        
        if cls.are_adjacent(start, end):
            return [start, end]
        
        # Opposite: find intermediate via adjacency
        for e in Element:
            if e != start and e != end:
                if cls.are_adjacent(start, e) and cls.are_adjacent(e, end):
                    return [start, e, end]
        
        return []


# =============================================================================
# COMPLETE STATE SPACE
# =============================================================================

@dataclass
class AlchemicalState:
    """
    Complete alchemical state s ∈ S.
    
    s = (Ψ, (H, M), Θ, A)
    - Ψ: elemental composition
    - (H, M): thermodynamic-humoral qualities
    - Θ: planetary configuration (7 phases)
    - A: archetypal sector (zodiacal)
    """
    
    elemental: ElementalState = field(default_factory=ElementalState)
    quality: QualityState = field(default_factory=QualityState)
    planetary_phases: Dict[str, float] = field(default_factory=dict)
    archetype: int = 0  # Zodiacal sector (0-11)
    
    def __post_init__(self):
        # Initialize planetary phases if empty
        if not self.planetary_phases:
            self.planetary_phases = {
                "sun": 0.0, "moon": 0.0, "mercury": 0.0, "venus": 0.0,
                "mars": 0.0, "jupiter": 0.0, "saturn": 0.0
            }
        
        # Compute quality from elemental if not set
        if self.quality.heat == 0 and self.quality.moisture == 0:
            self.quality = QualityMapping.map(self.elemental)
    
    def update_quality(self) -> None:
        """Update quality state from elemental composition."""
        self.quality = QualityMapping.map(self.elemental)
    
    @property
    def dominant_element(self) -> Element:
        """Get dominant element."""
        dist = self.elemental.get_distribution()
        return max(dist.keys(), key=lambda e: dist[e])
    
    @property
    def zodiac_sign(self) -> str:
        """Get zodiacal sign name."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        return signs[self.archetype % 12]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_alchemical_state_space() -> bool:
    """Validate the alchemical state space module."""
    
    # Test Element
    assert Element.FIRE.opposite == Element.WATER
    assert Element.AIR.quality_coords == (+1.0, +1.0)
    
    # Test ElementalState
    fire_state = ElementalState.from_element(Element.FIRE, 1.0)
    assert fire_state.fire == 1.0
    assert fire_state.norm == 1.0
    
    # Test mixed state
    mixed = ElementalState(0.5, 0.5, 0.5, 0.5)
    assert abs(mixed.norm - 1.0) < 0.01
    
    dist = mixed.get_distribution()
    assert all(abs(v - 0.25) < 0.01 for v in dist.values())
    
    # Test entropy (max for uniform distribution = ln(4))
    assert abs(mixed.entropy() - math.log(4)) < 0.01
    
    # Test QualityMapping
    q = QualityMapping.map(fire_state)
    assert q.heat == 1.0
    assert q.moisture == -1.0
    assert q.is_hot
    assert q.is_dry
    
    # Test Aristotelian Square
    assert AristotelianSquare.are_adjacent(Element.FIRE, Element.AIR)
    assert AristotelianSquare.are_opposite(Element.FIRE, Element.WATER)
    assert AristotelianSquare.shared_quality(Element.FIRE, Element.AIR) == "hot"
    
    path = AristotelianSquare.transformation_path(Element.FIRE, Element.WATER)
    assert len(path) == 3  # Opposite needs intermediate
    
    # Test AlchemicalState
    state = AlchemicalState(elemental=mixed)
    assert state.dominant_element in Element
    assert state.zodiac_sign == "Aries"
    
    # Test inner product
    state1 = ElementalState.from_element(Element.FIRE)
    state2 = ElementalState.from_element(Element.WATER)
    assert state1.inner_product(state2) == 0  # Orthogonal
    assert state1.inner_product(state1) == 1  # Self = 1
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - ALCHEMICAL STATE SPACE")
    print("The Mathematical Foundation of Alchemy")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_alchemical_state_space()
    print("✓ Module validated")
    
    # Demo
    print("\n--- ELEMENTAL STATE DEMO ---")
    mixed = ElementalState(fire=0.6, air=0.3, water=0.1, earth=0.0)
    print(f"State: Fire={mixed.fire:.2f}, Air={mixed.air:.2f}, " +
          f"Water={mixed.water:.2f}, Earth={mixed.earth:.2f}")
    
    dist = mixed.get_distribution()
    print(f"Distribution: {', '.join(f'{e.name}={v:.2%}' for e, v in dist.items())}")
    print(f"Entropy: {mixed.entropy():.3f} (max = {math.log(4):.3f})")
    
    q = QualityMapping.map(mixed)
    print(f"Quality: Heat={q.heat:.2f}, Moisture={q.moisture:.2f}")
    print(f"  Hot: {q.is_hot}, Cold: {q.is_cold}, Moist: {q.is_moist}, Dry: {q.is_dry}")
    
    print("\n--- ARISTOTELIAN SQUARE ---")
    for e in Element:
        h, m = e.quality_coords
        print(f"  {e.name}: ({'+' if h > 0 else ''}{h:.0f}, {'+' if m > 0 else ''}{m:.0f})")
