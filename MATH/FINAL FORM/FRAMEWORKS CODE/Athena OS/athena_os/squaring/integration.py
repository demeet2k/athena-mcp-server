"""
ATHENA OS - SQUARING THE CIRCLE: INTEGRATION
=============================================
Circle-Square Integration - The Pythagorean Completion

THE INTEGRATION FORMULA:
    36 + 64 = 100
    6² + 8² = 10²
    
    This is the Pythagorean theorem:
    - 36: Circle's faces (6²)
    - 64: Square's permutations (8²) 
    - 100: Complete system (10² = Decad squared)

FIRST-LEVEL INTEGRATION (12 + 4 = 16):
    - 12 archetypes (peripheral positions)
    - 4 elements (axial positions)
    - 16 total (complete mandala)

DEEP INTEGRATION (36 + 64 = 100):
    - 36 faces (circle level 4)
    - 64 permutations (square level 3)
    - 100 total (Pythagorean completion)

ORTHOGONALITY:
    Circle and Square are perpendicular:
    - Circle: temporal, sequential, cyclic
    - Square: structural, simultaneous, combinatorial
    
    They meet at right angles, hence Pythagorean relation.

THE COMPLETE STATE SPACE:
    Any complete state requires BOTH coordinates:
    - Where in the cycle? (circle position)
    - What configuration? (square position)
    
    100 = 36 × 64 product space, or 100 = 36 + 64 union

SOURCES:
    - SQUARING_THE_CIRCLE.docx Chapters 14, 22
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Iterator
from enum import Enum
import numpy as np
import math

from .circle_system import (
    CircleSystem, CircularPosition, Face, Archetype as CircleArchetype,
    Mode, Element as CircleElement, FACES, ARCHETYPE_ORDER
)
from .square_system import (
    SquareSystem, ElementalArchetype, ElementalPermutation,
    Element as SquareElement, ARCHETYPES_16, PERMUTATIONS_64
)


# =============================================================================
# PYTHAGOREAN CONSTANTS
# =============================================================================

# The fundamental Pythagorean triple
CIRCLE_NUMBER = 6       # √36
SQUARE_NUMBER = 8       # √64
COMPLETION_NUMBER = 10  # √100

# The squared values
CIRCLE_SQUARED = 36     # Faces
SQUARE_SQUARED = 64     # Permutations
COMPLETION_SQUARED = 100  # Total

# First-level integration
ARCHETYPES = 12
ELEMENTS = 4
MANDALA = 16


# =============================================================================
# INTEGRATION LEVEL
# =============================================================================

class IntegrationLevel(Enum):
    """Levels of circle-square integration."""
    
    FIRST = "first"     # 12 + 4 = 16
    DEEP = "deep"       # 36 + 64 = 100
    COMPLETE = "complete"  # Full product space


# =============================================================================
# INTEGRATED POSITION
# =============================================================================

@dataclass
class IntegratedPosition:
    """
    A position in the integrated circle-square space.
    
    Combines circular (temporal) and square (structural) coordinates.
    """
    
    # Circle coordinate (which face, 0-35)
    face_index: int
    
    # Square coordinate (which permutation, 0-63)
    permutation_index: int
    
    def __post_init__(self):
        self.face_index = self.face_index % 36
        self.permutation_index = self.permutation_index % 64
    
    @property
    def face(self) -> Face:
        """Get the circular face."""
        return FACES[self.face_index]
    
    @property
    def permutation(self) -> ElementalPermutation:
        """Get the square permutation."""
        return PERMUTATIONS_64[self.permutation_index]
    
    @property
    def degree(self) -> float:
        """Get center degree of face."""
        return self.face.center_degree
    
    @property
    def circular_position(self) -> CircularPosition:
        """Get as CircularPosition."""
        return CircularPosition(self.degree)
    
    @property
    def linear_index(self) -> int:
        """Get linear index in product space (0 to 36×64-1)."""
        return self.face_index * 64 + self.permutation_index
    
    @property
    def union_index(self) -> int:
        """
        Get index in union space (0-99).
        
        Maps to 100-element union:
        - 0-35: face indices
        - 36-99: permutation indices (offset)
        """
        # This is a projection, not 1-1 with product
        if self.face_index < 36:
            return self.face_index  # Circle contribution
        return 36 + (self.permutation_index % 64)  # Square contribution
    
    @property
    def circle_archetype(self) -> CircleArchetype:
        """Get zodiacal archetype."""
        return self.face.archetype
    
    @property
    def square_archetype(self) -> ElementalArchetype:
        """Get elemental archetype from permutation."""
        return self.permutation.archetype
    
    def distance_to(self, other: IntegratedPosition) -> float:
        """
        Compute distance in integrated space.
        
        Uses Pythagorean combination of circle and square distances.
        """
        # Circle distance (normalized to [0, 1])
        face_diff = min(
            abs(self.face_index - other.face_index),
            36 - abs(self.face_index - other.face_index)
        ) / 18  # Max distance is 18
        
        # Square distance (normalized to [0, 1])
        perm_diff = abs(self.permutation_index - other.permutation_index) / 64
        
        # Pythagorean combination
        return math.sqrt(face_diff**2 + perm_diff**2)
    
    def resonance_with(self, other: IntegratedPosition) -> float:
        """
        Compute resonance/harmony between two positions.
        
        Based on shared elements and aspects.
        """
        # Element matching
        circle_elem = self.face.element
        other_circle_elem = other.face.element
        
        perm_root = self.permutation.root
        other_perm_root = other.permutation.root
        
        # Count matches
        matches = 0
        if circle_elem == other_circle_elem:
            matches += 1
        if perm_root == other_perm_root:
            matches += 1
        if self.face.mode == other.face.mode:
            matches += 1
        
        # Aspect bonus
        aspect = self.circular_position.aspect_to(other.circular_position)
        aspect_bonus = {
            "trine": 0.3,
            "sextile": 0.2,
            "conjunction": 0.1,
            "opposition": -0.1,
            "square": -0.2
        }.get(aspect, 0)
        
        return (matches / 3) + aspect_bonus
    
    def __repr__(self) -> str:
        return f"IntegratedPosition(face={self.face_index}, perm={self.permutation_index})"


# =============================================================================
# PYTHAGOREAN TRIANGLE
# =============================================================================

@dataclass
class PythagoreanTriangle:
    """
    The 6-8-10 Pythagorean triangle representing circle-square integration.
    
    - Leg a (6): Circle's contribution
    - Leg b (8): Square's contribution  
    - Hypotenuse c (10): Integrated completion
    """
    
    a: int = CIRCLE_NUMBER
    b: int = SQUARE_NUMBER
    c: int = COMPLETION_NUMBER
    
    def __post_init__(self):
        # Verify Pythagorean property
        assert self.a**2 + self.b**2 == self.c**2, \
            f"Not a valid Pythagorean triple: {self.a}² + {self.b}² ≠ {self.c}²"
    
    @property
    def a_squared(self) -> int:
        """Circle's squared contribution."""
        return self.a ** 2
    
    @property
    def b_squared(self) -> int:
        """Square's squared contribution."""
        return self.b ** 2
    
    @property
    def c_squared(self) -> int:
        """Completion squared."""
        return self.c ** 2
    
    @property
    def area(self) -> float:
        """Triangle area."""
        return (self.a * self.b) / 2
    
    @property
    def perimeter(self) -> int:
        """Triangle perimeter."""
        return self.a + self.b + self.c
    
    @property
    def ratio_a_b(self) -> Tuple[int, int]:
        """Ratio of legs (reduced)."""
        from math import gcd
        g = gcd(self.a, self.b)
        return (self.a // g, self.b // g)
    
    @property
    def is_primitive(self) -> bool:
        """Check if this is a primitive triple (GCD = 1)."""
        from math import gcd
        return gcd(gcd(self.a, self.b), self.c) == 1
    
    def scale(self, factor: int) -> PythagoreanTriangle:
        """Scale the triangle by a factor."""
        return PythagoreanTriangle(
            self.a * factor,
            self.b * factor,
            self.c * factor
        )
    
    @property
    def angle_alpha(self) -> float:
        """Angle at vertex A (opposite to side a) in radians."""
        return math.asin(self.a / self.c)
    
    @property
    def angle_beta(self) -> float:
        """Angle at vertex B (opposite to side b) in radians."""
        return math.asin(self.b / self.c)
    
    def describe(self) -> str:
        """Get description of the triangle."""
        return (
            f"Pythagorean Triangle ({self.a}-{self.b}-{self.c}):\n"
            f"  {self.a}² + {self.b}² = {self.c}²\n"
            f"  {self.a_squared} + {self.b_squared} = {self.c_squared}\n"
            f"  Circle + Square = Completion\n"
            f"  Primitive: {self.is_primitive}\n"
            f"  Ratio: {self.ratio_a_b[0]}:{self.ratio_a_b[1]} = 3:4"
        )


# The fundamental integration triangle
INTEGRATION_TRIANGLE = PythagoreanTriangle()


# =============================================================================
# INTEGRATION SPACE
# =============================================================================

class IntegrationSpace:
    """
    The complete circle-square integration space.
    
    Product space: 36 × 64 = 2304 positions
    Union space: 36 + 64 = 100 components
    """
    
    # Space sizes
    PRODUCT_SIZE = 36 * 64  # 2304
    UNION_SIZE = 100        # 36 + 64
    
    def __init__(self):
        self.circle = CircleSystem()
        self.square = SquareSystem()
        self.triangle = INTEGRATION_TRIANGLE
    
    def get_position(self, face_index: int, 
                    perm_index: int) -> IntegratedPosition:
        """Get integrated position."""
        return IntegratedPosition(face_index, perm_index)
    
    def from_linear_index(self, index: int) -> IntegratedPosition:
        """Get position from linear product index."""
        face = index // 64
        perm = index % 64
        return IntegratedPosition(face, perm)
    
    def from_union_index(self, index: int) -> Tuple[str, int]:
        """
        Interpret union index (0-99).
        
        Returns (type, local_index) where type is 'circle' or 'square'.
        """
        if index < 36:
            return ('circle', index)
        else:
            return ('square', index - 36)
    
    def iterate_product(self) -> Iterator[IntegratedPosition]:
        """Iterate through all 2304 product positions."""
        for face in range(36):
            for perm in range(64):
                yield IntegratedPosition(face, perm)
    
    def iterate_union(self) -> Iterator[Tuple[str, int, Any]]:
        """
        Iterate through the 100 union components.
        
        Yields (type, index, object).
        """
        for i, face in enumerate(FACES):
            yield ('circle', i, face)
        for i, perm in enumerate(PERMUTATIONS_64):
            yield ('square', i, perm)
    
    def sample_product(self, n: int = 10) -> List[IntegratedPosition]:
        """Sample n random positions from product space."""
        indices = np.random.choice(self.PRODUCT_SIZE, size=n, replace=False)
        return [self.from_linear_index(int(i)) for i in indices]
    
    def find_resonant_positions(self, 
                                target: IntegratedPosition,
                                threshold: float = 0.5) -> List[IntegratedPosition]:
        """Find positions resonant with target."""
        resonant = []
        for pos in self.iterate_product():
            if pos != target and pos.resonance_with(target) >= threshold:
                resonant.append(pos)
        return resonant
    
    def pythagorean_decomposition(self, value: int) -> Optional[Tuple[int, int]]:
        """
        Decompose value into circle + square components if possible.
        
        Finds (a², b²) such that a² + b² = value.
        """
        for a in range(1, int(math.sqrt(value)) + 1):
            a_sq = a * a
            b_sq = value - a_sq
            b = int(math.sqrt(b_sq))
            if b * b == b_sq:
                return (a_sq, b_sq)
        return None
    
    def harmonic_ratio(self) -> Tuple[int, int]:
        """
        Get the harmonic ratio of circle to square.
        
        36:64 = 9:16, but 6:8 = 3:4 (perfect fourth).
        """
        return (3, 4)  # The musical fourth
    
    def summary(self) -> Dict[str, Any]:
        """Get integration summary."""
        return {
            "pythagorean_triple": (6, 8, 10),
            "circle_contribution": 36,
            "square_contribution": 64,
            "union_total": 100,
            "product_total": 2304,
            "harmonic_ratio": "3:4 (perfect fourth)",
            "triangle": {
                "a": self.triangle.a,
                "b": self.triangle.b,
                "c": self.triangle.c,
                "a²": self.triangle.a_squared,
                "b²": self.triangle.b_squared,
                "c²": self.triangle.c_squared
            }
        }


# =============================================================================
# NUPTIAL NUMBER
# =============================================================================

class NuptialNumber:
    """
    Plato's Nuptial Number from Republic Book VIII.
    
    N = 12,960,000 = 360² × 100
    
    Encodes the circle-square integration:
    - 360²: The circle squared (degrees squared)
    - 100: The completion number (36 + 64)
    """
    
    N = 12960000
    
    # Factorization
    CIRCLE_FACTOR = 360
    COMPLETION_FACTOR = 100
    
    @classmethod
    def verify(cls) -> bool:
        """Verify the nuptial number formula."""
        return cls.N == cls.CIRCLE_FACTOR ** 2 * cls.COMPLETION_FACTOR
    
    @classmethod
    def factorizations(cls) -> Dict[str, Any]:
        """Get various factorizations."""
        return {
            "standard": f"{cls.CIRCLE_FACTOR}² × {cls.COMPLETION_FACTOR}",
            "expanded": f"{cls.CIRCLE_FACTOR}² × (36 + 64)",
            "pythagorean": f"{cls.CIRCLE_FACTOR}² × (6² + 8²)",
            "decad": f"{cls.CIRCLE_FACTOR}² × 10²",
            "prime": cls.prime_factorization()
        }
    
    @classmethod
    def prime_factorization(cls) -> Dict[int, int]:
        """Get prime factorization of N."""
        n = cls.N
        factors = {}
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors[d] = factors.get(d, 0) + 1
                n //= d
            d += 1
        if n > 1:
            factors[n] = factors.get(n, 0) + 1
        return factors
    
    @classmethod
    def cosmological_meaning(cls) -> str:
        """Get cosmological interpretation."""
        return (
            "The Nuptial Number governs the proper timing for conception "
            "of guardian-class citizens. It represents:\n"
            "  - 360² = Complete cycle squared (the Great Year)\n"
            "  - 100 = Circle + Square integration\n"
            "  - Total = Perfect temporal window for generation"
        )


# =============================================================================
# VALIDATION
# =============================================================================

def validate_integration() -> bool:
    """Validate integration module."""
    
    # Verify Pythagorean identity
    assert CIRCLE_NUMBER**2 + SQUARE_NUMBER**2 == COMPLETION_NUMBER**2
    assert CIRCLE_SQUARED + SQUARE_SQUARED == COMPLETION_SQUARED
    assert 36 + 64 == 100
    
    # Verify first-level integration
    assert ARCHETYPES + ELEMENTS == MANDALA
    assert 12 + 4 == 16
    
    # Test Pythagorean triangle
    tri = INTEGRATION_TRIANGLE
    assert tri.a_squared == 36
    assert tri.b_squared == 64
    assert tri.c_squared == 100
    assert tri.ratio_a_b == (3, 4)
    
    # Test integrated position
    pos = IntegratedPosition(0, 0)
    assert pos.face_index == 0
    assert pos.permutation_index == 0
    assert pos.linear_index == 0
    
    pos2 = IntegratedPosition(1, 10)
    assert pos2.linear_index == 1 * 64 + 10
    
    # Test distance
    dist = pos.distance_to(pos2)
    assert dist >= 0
    
    # Test integration space
    space = IntegrationSpace()
    assert space.PRODUCT_SIZE == 36 * 64
    assert space.UNION_SIZE == 100
    
    # Test decomposition
    decomp = space.pythagorean_decomposition(100)
    assert decomp == (36, 64) or decomp == (64, 36)
    
    # Test nuptial number
    assert NuptialNumber.verify()
    assert NuptialNumber.N == 360 * 360 * 100
    
    return True


if __name__ == "__main__":
    print("Validating Integration Module...")
    assert validate_integration()
    print("✓ Integration Module validated")
    
    # Demo
    print("\n--- Circle-Square Integration Demo ---")
    
    print("\nThe Pythagorean Integration:")
    print(INTEGRATION_TRIANGLE.describe())
    
    print("\nIntegration Levels:")
    print(f"  First Level: 12 + 4 = {ARCHETYPES + ELEMENTS} (mandala)")
    print(f"  Deep Level: 36 + 64 = {CIRCLE_SQUARED + SQUARE_SQUARED} (completion)")
    
    space = IntegrationSpace()
    summary = space.summary()
    
    print(f"\nProduct Space: {summary['product_total']} positions")
    print(f"Union Space: {summary['union_total']} components")
    print(f"Harmonic Ratio: {summary['harmonic_ratio']}")
    
    print("\nSample Integrated Position:")
    pos = space.get_position(5, 23)
    print(f"  Face: {pos.face_index} ({pos.face.archetype.name})")
    print(f"  Permutation: {pos.permutation_index} ({pos.permutation.name})")
    print(f"  Degree: {pos.degree}°")
    print(f"  Linear Index: {pos.linear_index}")
    
    print("\nNuptial Number:")
    print(f"  N = {NuptialNumber.N:,}")
    print(f"  = {NuptialNumber.factorizations()['standard']}")
    print(f"  = {NuptialNumber.factorizations()['pythagorean']}")
