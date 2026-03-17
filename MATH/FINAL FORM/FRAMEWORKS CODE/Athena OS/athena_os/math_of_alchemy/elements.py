"""
ATHENA OS - THE MATH OF ALCHEMY
================================
Module I: Elements (יסודות) - The Elemental State Space

THE FOUR ELEMENTS AS BASIS VECTORS:
    Fire (??) - e_F - Hot & Dry - Will, Drive, Action
    Air (??) - e_A - Hot & Moist - Intellect, Pattern, Diffusion
    Water (??) - e_W - Cold & Moist - Emotion, Memory, Cohesion
    Earth (??) - e_E - Cold & Dry - Form, Structure, Stability

THE QUALITY SPACE:
    Q = ℝ² with axes:
    - Heat (H): H > 0 = hot, H < 0 = cold
    - Moisture (M): M > 0 = moist, M < 0 = dry

    Element-to-Quality Mapping:
    Φ: V_elem → Q_qual
    
    Fire  → (+1, -1)  Hot & Dry
    Air   → (+1, +1)  Hot & Moist
    Water → (-1, +1)  Cold & Moist
    Earth → (-1, -1)  Cold & Dry

THE ELEMENTAL SIMPLEX:
    Normalized compositions form a 3-simplex: Δ³
    p = (p_F, p_A, p_W, p_E) where Σp_i = 1

SOURCES:
    THE MATH OF ALCHEMY
    Aristotelian Physics
    Classical Alchemical Tradition
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum, auto


# =============================================================================
# ELEMENT TYPES
# =============================================================================

class Element(Enum):
    """The Four Classical Elements."""
    
    FIRE = ("??", "Fire", "Ignis", (+1, -1), "Hot & Dry")
    AIR = ("??", "Air", "Aer", (+1, +1), "Hot & Moist")
    WATER = ("??", "Water", "Aqua", (-1, +1), "Cold & Moist")
    EARTH = ("??", "Earth", "Terra", (-1, -1), "Cold & Dry")
    
    def __init__(self, symbol: str, name: str, latin: str,
                 quality_coords: Tuple[int, int], qualities: str):
        self.symbol = symbol
        self._name = name
        self.latin = latin
        self.quality_coords = quality_coords  # (Heat, Moisture)
        self.qualities = qualities
    
    @property
    def heat(self) -> int:
        """Heat coordinate: +1 hot, -1 cold."""
        return self.quality_coords[0]
    
    @property
    def moisture(self) -> int:
        """Moisture coordinate: +1 moist, -1 dry."""
        return self.quality_coords[1]
    
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
    def opposite(self) -> 'Element':
        """Get the opposing element."""
        opposites = {
            Element.FIRE: Element.WATER,
            Element.WATER: Element.FIRE,
            Element.AIR: Element.EARTH,
            Element.EARTH: Element.AIR,
        }
        return opposites[self]


class Quality(Enum):
    """The Four Qualities."""
    
    HOT = ("Heat", +1, 0)
    COLD = ("Cold", -1, 0)
    MOIST = ("Moisture", 0, +1)
    DRY = ("Dryness", 0, -1)
    
    def __init__(self, name: str, h_component: int, m_component: int):
        self._name = name
        self.h_component = h_component
        self.m_component = m_component


# =============================================================================
# ELEMENTAL STATE VECTOR
# =============================================================================

@dataclass
class ElementalState:
    """
    A state in the 4-dimensional elemental space.
    
    Ψ = c_F·e_F + c_A·e_A + c_W·e_W + c_E·e_E
    
    where c_i ∈ ℝ or ℂ
    """
    
    fire: complex = 0.0
    air: complex = 0.0
    water: complex = 0.0
    earth: complex = 0.0
    
    def __post_init__(self):
        """Convert to complex if real."""
        self.fire = complex(self.fire)
        self.air = complex(self.air)
        self.water = complex(self.water)
        self.earth = complex(self.earth)
    
    @property
    def vector(self) -> np.ndarray:
        """Get as numpy array [F, A, W, E]."""
        return np.array([self.fire, self.air, self.water, self.earth], dtype=complex)
    
    @classmethod
    def from_vector(cls, v: np.ndarray) -> 'ElementalState':
        """Create from numpy array."""
        return cls(fire=v[0], air=v[1], water=v[2], earth=v[3])
    
    @classmethod
    def pure(cls, element: Element, intensity: float = 1.0) -> 'ElementalState':
        """Create a pure elemental state."""
        state = cls()
        if element == Element.FIRE:
            state.fire = intensity
        elif element == Element.AIR:
            state.air = intensity
        elif element == Element.WATER:
            state.water = intensity
        elif element == Element.EARTH:
            state.earth = intensity
        return state
    
    @property
    def magnitude(self) -> float:
        """Total magnitude of the state."""
        return float(np.abs(self.fire) + np.abs(self.air) + 
                    np.abs(self.water) + np.abs(self.earth))
    
    @property
    def norm(self) -> float:
        """L2 norm of the state."""
        return float(np.linalg.norm(self.vector))
    
    @property
    def normalized(self) -> 'ElementalState':
        """Get normalized composition (simplex point)."""
        mag = self.magnitude
        if mag == 0:
            return ElementalState(0.25, 0.25, 0.25, 0.25)
        return ElementalState(
            fire=np.abs(self.fire) / mag,
            air=np.abs(self.air) / mag,
            water=np.abs(self.water) / mag,
            earth=np.abs(self.earth) / mag
        )
    
    @property
    def probabilities(self) -> Tuple[float, float, float, float]:
        """Get elemental probabilities (simplex coordinates)."""
        n = self.normalized
        return (float(n.fire.real), float(n.air.real), 
                float(n.water.real), float(n.earth.real))
    
    def __add__(self, other: 'ElementalState') -> 'ElementalState':
        return ElementalState(
            fire=self.fire + other.fire,
            air=self.air + other.air,
            water=self.water + other.water,
            earth=self.earth + other.earth
        )
    
    def __mul__(self, scalar: complex) -> 'ElementalState':
        return ElementalState(
            fire=self.fire * scalar,
            air=self.air * scalar,
            water=self.water * scalar,
            earth=self.earth * scalar
        )
    
    def __rmul__(self, scalar: complex) -> 'ElementalState':
        return self * scalar


# =============================================================================
# QUALITY SPACE
# =============================================================================

@dataclass
class QualityState:
    """
    A state in the 2-dimensional quality space.
    
    (H, M) ∈ ℝ²
    H > 0: hot, H < 0: cold
    M > 0: moist, M < 0: dry
    """
    
    heat: float = 0.0
    moisture: float = 0.0
    
    @property
    def vector(self) -> np.ndarray:
        """Get as numpy array [H, M]."""
        return np.array([self.heat, self.moisture])
    
    @classmethod
    def from_vector(cls, v: np.ndarray) -> 'QualityState':
        """Create from numpy array."""
        return cls(heat=v[0], moisture=v[1])
    
    @property
    def quadrant(self) -> Element:
        """Determine which elemental quadrant this falls into."""
        if self.heat >= 0 and self.moisture < 0:
            return Element.FIRE
        elif self.heat >= 0 and self.moisture >= 0:
            return Element.AIR
        elif self.heat < 0 and self.moisture >= 0:
            return Element.WATER
        else:
            return Element.EARTH
    
    @property
    def dominant_quality(self) -> Quality:
        """Get the dominant quality."""
        abs_h = abs(self.heat)
        abs_m = abs(self.moisture)
        
        if abs_h > abs_m:
            return Quality.HOT if self.heat > 0 else Quality.COLD
        else:
            return Quality.MOIST if self.moisture > 0 else Quality.DRY
    
    def distance_to(self, other: 'QualityState') -> float:
        """Euclidean distance to another quality state."""
        return float(np.linalg.norm(self.vector - other.vector))


# =============================================================================
# QUALITY MAPPING
# =============================================================================

class QualityMapping:
    """
    The linear mapping from elemental space to quality space.
    
    Φ: V_elem → Q_qual
    
    (H_Ψ, M_Ψ) = Q · c
    
    where Q = [+1, +1, -1, -1]
              [-1, +1, +1, -1]
    """
    
    # The quality mapping matrix
    Q_MATRIX = np.array([
        [+1, +1, -1, -1],  # Heat row
        [-1, +1, +1, -1],  # Moisture row
    ], dtype=float)
    
    @classmethod
    def map_to_quality(cls, state: ElementalState) -> QualityState:
        """Map an elemental state to quality space."""
        c = np.array([
            state.fire.real, state.air.real,
            state.water.real, state.earth.real
        ])
        hm = cls.Q_MATRIX @ c
        return QualityState(heat=hm[0], moisture=hm[1])
    
    @classmethod
    def element_quality(cls, element: Element) -> QualityState:
        """Get the quality coordinates for a pure element."""
        h, m = element.quality_coords
        return QualityState(heat=float(h), moisture=float(m))


# =============================================================================
# ELEMENTAL SIMPLEX
# =============================================================================

@dataclass
class ElementalSimplex:
    """
    The 3-simplex of normalized elemental compositions.
    
    Δ³ = {(p_F, p_A, p_W, p_E) | p_i ≥ 0, Σp_i = 1}
    
    Vertices are pure elements.
    Interior points are mixtures.
    """
    
    @staticmethod
    def vertices() -> Dict[Element, np.ndarray]:
        """Get the four vertices (pure elements)."""
        return {
            Element.FIRE: np.array([1, 0, 0, 0]),
            Element.AIR: np.array([0, 1, 0, 0]),
            Element.WATER: np.array([0, 0, 1, 0]),
            Element.EARTH: np.array([0, 0, 0, 1]),
        }
    
    @staticmethod
    def centroid() -> np.ndarray:
        """Get the centroid (balanced mixture)."""
        return np.array([0.25, 0.25, 0.25, 0.25])
    
    @staticmethod
    def entropy(p: np.ndarray) -> float:
        """
        Shannon entropy of elemental distribution.
        
        S(p) = -Σ p_i ln(p_i)
        """
        p = np.clip(p, 1e-10, 1.0)  # Avoid log(0)
        return float(-np.sum(p * np.log(p)))
    
    @staticmethod
    def is_valid(p: np.ndarray, tol: float = 1e-6) -> bool:
        """Check if point is on the simplex."""
        return (
            np.all(p >= -tol) and
            abs(np.sum(p) - 1.0) < tol
        )
    
    @staticmethod
    def project(v: np.ndarray) -> np.ndarray:
        """Project a vector onto the simplex."""
        # Normalize to non-negative
        v = np.maximum(v, 0)
        total = np.sum(v)
        if total == 0:
            return ElementalSimplex.centroid()
        return v / total
    
    @staticmethod
    def barycentric_coords(p: np.ndarray) -> Dict[Element, float]:
        """Get barycentric coordinates as element dict."""
        return {
            Element.FIRE: float(p[0]),
            Element.AIR: float(p[1]),
            Element.WATER: float(p[2]),
            Element.EARTH: float(p[3]),
        }


# =============================================================================
# ELEMENTAL SYSTEM
# =============================================================================

@dataclass
class ElementalSystem:
    """
    The complete elemental state space system.
    """
    
    state: ElementalState = field(default_factory=ElementalState)
    
    @property
    def quality_state(self) -> QualityState:
        """Get the quality space projection."""
        return QualityMapping.map_to_quality(self.state)
    
    @property
    def simplex_point(self) -> np.ndarray:
        """Get the normalized simplex coordinates."""
        n = self.state.normalized
        return np.array([n.fire.real, n.air.real, n.water.real, n.earth.real])
    
    @property
    def entropy(self) -> float:
        """Entropy of the elemental distribution."""
        return ElementalSimplex.entropy(self.simplex_point)
    
    @property
    def dominant_element(self) -> Element:
        """Get the dominant element."""
        p = self.simplex_point
        idx = np.argmax(p)
        return [Element.FIRE, Element.AIR, Element.WATER, Element.EARTH][idx]
    
    def apply_matrix(self, M: np.ndarray) -> 'ElementalSystem':
        """Apply a 4x4 transformation matrix."""
        new_vec = M @ self.state.vector
        return ElementalSystem(state=ElementalState.from_vector(new_vec))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        q = self.quality_state
        p = self.simplex_point
        return {
            "state": {
                "fire": complex(self.state.fire),
                "air": complex(self.state.air),
                "water": complex(self.state.water),
                "earth": complex(self.state.earth),
            },
            "quality": {
                "heat": q.heat,
                "moisture": q.moisture,
                "quadrant": q.quadrant.name,
            },
            "simplex": {
                "fire": float(p[0]),
                "air": float(p[1]),
                "water": float(p[2]),
                "earth": float(p[3]),
            },
            "entropy": self.entropy,
            "dominant": self.dominant_element.name,
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_elements() -> bool:
    """Validate the Elements module."""
    
    # Test Element enum
    assert Element.FIRE.heat == 1
    assert Element.FIRE.moisture == -1
    assert Element.WATER.is_cold
    assert Element.AIR.is_moist
    assert Element.FIRE.opposite == Element.WATER
    
    # Test ElementalState
    state = ElementalState(fire=1, air=0.5, water=0.3, earth=0.2)
    assert state.magnitude == 2.0
    
    # Test pure state
    pure_fire = ElementalState.pure(Element.FIRE, 2.0)
    assert pure_fire.fire == 2.0
    assert pure_fire.air == 0.0
    
    # Test normalized
    n = state.normalized
    probs = n.probabilities
    assert abs(sum(probs) - 1.0) < 1e-6
    
    # Test QualityState
    q = QualityState(heat=0.5, moisture=-0.3)
    assert q.quadrant == Element.FIRE
    
    # Test QualityMapping
    fire_q = QualityMapping.element_quality(Element.FIRE)
    assert fire_q.heat == 1.0
    assert fire_q.moisture == -1.0
    
    mapped = QualityMapping.map_to_quality(pure_fire)
    assert mapped.heat == 2.0
    assert mapped.moisture == -2.0
    
    # Test ElementalSimplex
    assert ElementalSimplex.is_valid(np.array([0.25, 0.25, 0.25, 0.25]))
    assert not ElementalSimplex.is_valid(np.array([0.5, 0.5, 0.5, 0.5]))
    
    # Test entropy
    uniform = np.array([0.25, 0.25, 0.25, 0.25])
    max_entropy = ElementalSimplex.entropy(uniform)
    pure = np.array([1, 0, 0, 0])
    min_entropy = ElementalSimplex.entropy(pure)
    assert max_entropy > min_entropy
    
    # Test ElementalSystem
    system = ElementalSystem(state=state)
    assert system.dominant_element == Element.FIRE
    summary = system.get_summary()
    assert "entropy" in summary
    
    return True


if __name__ == "__main__":
    print("Validating Elements Module...")
    assert validate_elements()
    print("✓ Elements module validated")
    
    # Demo
    print("\n--- Elements Demo ---")
    
    print("\nThe Four Elements:")
    for elem in Element:
        print(f"  {elem.symbol} {elem._name} ({elem.latin}): {elem.qualities}")
    
    print("\nQuality Mapping Matrix:")
    print(f"  Q = {QualityMapping.Q_MATRIX.tolist()}")
    
    # Example state
    state = ElementalState(fire=0.6, air=0.3, water=0.05, earth=0.05)
    system = ElementalSystem(state=state)
    
    print("\nExample State:")
    print(f"  Fire={state.fire.real:.2f}, Air={state.air.real:.2f}, "
          f"Water={state.water.real:.2f}, Earth={state.earth.real:.2f}")
    
    q = system.quality_state
    print(f"\nQuality Projection:")
    print(f"  Heat={q.heat:.2f}, Moisture={q.moisture:.2f}")
    print(f"  Quadrant: {q.quadrant.name}")
    
    print(f"\nEntropy: {system.entropy:.4f}")
    print(f"Dominant Element: {system.dominant_element.name}")
