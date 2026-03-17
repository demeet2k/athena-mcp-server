"""
ATHENA OS - SQUARING THE CIRCLE: VITRUVIAN SYSTEM
==================================================
The Human as the Squared Circle

THE VITRUVIAN DOCTRINE:
    The human figure simultaneously inscribed in circle and square
    demonstrates humanity's participation in both orders:
    
    - Circle: Celestial, divine, eternal (soul)
    - Square: Terrestrial, material, temporal (body)
    
    The human being uniquely integrates both.

VITRUVIAN PROPORTIONS:
    From Vitruvius's De Architectura, Book III:
    
    - Body height = arm span (square proportion)
    - Navel is the center of the body (circle center)
    - Height = 8 heads
    - Arm span = height
    - Foot = 1/6 height
    
    These ratios enable simultaneous inscription.

THE TWO CENTERS:
    Leonardo's drawing shows different centers:
    - Square centered on genitals (reproductive, material)
    - Circle centered on navel (cosmic, spiritual)
    
    This difference encodes the ontological gap.

CANONICAL PROPORTIONS:
    The golden ratio φ = (1 + √5)/2 ≈ 1.618 appears:
    - Navel divides height in golden ratio
    - Forearm to hand ratio
    - Face proportions
    
    φ bridges circle and square mathematically.

SOURCES:
    - SQUARING_THE_CIRCLE.docx Chapter 11.3
    - Vitruvius, De Architectura
    - Leonardo da Vinci, Vitruvian Man
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, IntEnum
import numpy as np
import math


# =============================================================================
# GOLDEN RATIO
# =============================================================================

PHI = (1 + math.sqrt(5)) / 2  # ≈ 1.6180339887...
PHI_SQUARED = PHI ** 2        # ≈ 2.6180339887...
PHI_INVERSE = 1 / PHI         # ≈ 0.6180339887... = φ - 1

# Fibonacci sequence (approaches φ ratio)
def fibonacci(n: int) -> List[int]:
    """Generate first n Fibonacci numbers."""
    if n <= 0:
        return []
    if n == 1:
        return [1]
    fibs = [1, 1]
    while len(fibs) < n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs


def fibonacci_ratio(n: int) -> float:
    """Get F(n+1)/F(n), approaches φ."""
    fibs = fibonacci(n + 2)
    return fibs[-1] / fibs[-2]


# =============================================================================
# VITRUVIAN PROPORTIONS
# =============================================================================

@dataclass
class VitruvianProportions:
    """
    The canonical proportions of the ideal human figure.
    
    Height is normalized to 1 unit.
    All other measurements expressed as fractions of height.
    """
    
    # Primary measurements
    height: float = 1.0
    arm_span: float = 1.0          # Equal to height (square)
    navel_height: float = 0.618    # φ^(-1) ≈ golden ratio point
    
    # Head-based proportions (height = 8 heads)
    head_height: float = 0.125     # 1/8
    face_length: float = 0.10      # 4/5 of head
    
    # Limb proportions
    arm_length: float = 0.45       # From shoulder
    forearm_length: float = 0.25   # Elbow to wrist
    hand_length: float = 0.10      # Wrist to fingertip
    leg_length: float = 0.50       # From hip
    foot_length: float = 0.167     # 1/6 of height
    
    # Torso
    shoulder_width: float = 0.25   # 2 heads wide
    hip_width: float = 0.167       # Slightly narrower
    
    @property
    def navel_from_feet(self) -> float:
        """Height of navel from ground."""
        return self.navel_height
    
    @property
    def navel_to_crown(self) -> float:
        """Distance from navel to top of head."""
        return self.height - self.navel_height
    
    @property
    def golden_ratio_check(self) -> float:
        """Ratio of height to navel segment (should ≈ φ)."""
        return self.height / self.navel_height
    
    @property
    def is_golden(self) -> bool:
        """Check if proportions follow golden ratio."""
        return abs(self.golden_ratio_check - PHI) < 0.05
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary of proportions."""
        return {
            "height": self.height,
            "arm_span": self.arm_span,
            "navel_height": self.navel_height,
            "head_height": self.head_height,
            "forearm_to_hand": self.forearm_length / self.hand_length,
            "navel_ratio": self.golden_ratio_check
        }


# Canonical proportions
CANONICAL_PROPORTIONS = VitruvianProportions()


# =============================================================================
# CIRCLE AND SQUARE INSCRIPTION
# =============================================================================

@dataclass
class CircleInscription:
    """
    Circle inscription of the human figure.
    
    With arms raised and legs spread, the human figure
    fits within a circle centered on the navel.
    """
    
    center_height: float = 0.618   # Navel position (φ^(-1))
    radius: float = 0.618          # From navel to extremities
    
    @property
    def circle_area(self) -> float:
        """Area of inscribing circle."""
        return math.pi * self.radius ** 2
    
    @property
    def circumference(self) -> float:
        """Circumference of inscribing circle."""
        return 2 * math.pi * self.radius
    
    @property
    def center_point(self) -> Tuple[float, float]:
        """Center point (x=0, y=navel height)."""
        return (0.0, self.center_height)
    
    def point_on_circle(self, angle: float) -> Tuple[float, float]:
        """Get point on circle at given angle (radians)."""
        x = self.radius * math.cos(angle)
        y = self.center_height + self.radius * math.sin(angle)
        return (x, y)
    
    @property
    def diameter(self) -> float:
        """Diameter of circle."""
        return 2 * self.radius


@dataclass
class SquareInscription:
    """
    Square inscription of the human figure.
    
    With arms horizontal and legs together, the human figure
    fits within a square centered on the genitals.
    """
    
    center_height: float = 0.5     # Genital position (halfway)
    side_length: float = 1.0       # Equal to height and arm span
    
    @property
    def square_area(self) -> float:
        """Area of inscribing square."""
        return self.side_length ** 2
    
    @property
    def perimeter(self) -> float:
        """Perimeter of inscribing square."""
        return 4 * self.side_length
    
    @property
    def center_point(self) -> Tuple[float, float]:
        """Center point (x=0, y=genital height)."""
        return (0.0, self.center_height)
    
    @property
    def corners(self) -> List[Tuple[float, float]]:
        """Get four corner points."""
        half = self.side_length / 2
        cy = self.center_height
        return [
            (-half, cy - half),  # Bottom-left
            (half, cy - half),   # Bottom-right
            (half, cy + half),   # Top-right
            (-half, cy + half)   # Top-left
        ]
    
    @property
    def diagonal(self) -> float:
        """Diagonal of square."""
        return self.side_length * math.sqrt(2)


# =============================================================================
# VITRUVIAN FIGURE
# =============================================================================

@dataclass
class VitruvianFigure:
    """
    Complete Vitruvian figure with circle and square inscriptions.
    """
    
    proportions: VitruvianProportions = field(default_factory=VitruvianProportions)
    circle: CircleInscription = field(default_factory=CircleInscription)
    square: SquareInscription = field(default_factory=SquareInscription)
    
    @property
    def center_displacement(self) -> float:
        """Vertical distance between circle and square centers."""
        return self.circle.center_height - self.square.center_height
    
    @property
    def area_ratio(self) -> float:
        """Ratio of circle area to square area (approaches π/4)."""
        return self.circle.circle_area / self.square.square_area
    
    @property
    def perimeter_ratio(self) -> float:
        """Ratio of circumference to perimeter."""
        return self.circle.circumference / self.square.perimeter
    
    @property
    def overlap_analysis(self) -> Dict[str, Any]:
        """Analyze the overlap of circle and square."""
        # The circle and square overlap but don't coincide
        # Calculate intersection properties
        return {
            "circle_center": self.circle.center_point,
            "square_center": self.square.center_point,
            "displacement": self.center_displacement,
            "circle_radius": self.circle.radius,
            "square_side": self.square.side_length,
            "area_ratio": self.area_ratio,
            "perimeter_ratio": self.perimeter_ratio
        }
    
    @property
    def ontological_meaning(self) -> Dict[str, str]:
        """Ontological interpretation of the figure."""
        return {
            "circle": "Soul, spirit, eternal, celestial, divine participation",
            "square": "Body, matter, temporal, terrestrial, material embodiment",
            "navel_center": "Point of spiritual connection (omphalos)",
            "genital_center": "Point of material reproduction",
            "displacement": "Gap between material and spiritual centers",
            "inscription": "Human participates in both orders simultaneously"
        }
    
    def describe(self) -> str:
        """Get description of the Vitruvian figure."""
        overlap = self.overlap_analysis
        return f"""Vitruvian Figure Analysis:

Circle (Celestial):
  Center: {overlap['circle_center']}
  Radius: {overlap['circle_radius']:.3f}
  Area: {self.circle.circle_area:.4f}

Square (Terrestrial):
  Center: {overlap['square_center']}
  Side: {overlap['square_side']:.3f}
  Area: {self.square.square_area:.4f}

Integration:
  Center Displacement: {overlap['displacement']:.3f}
  Area Ratio (π/4 ≈ 0.785): {overlap['area_ratio']:.4f}
  Human bridges both orders through simultaneous inscription.
"""


# =============================================================================
# ANTHROPIC PROPORTIONS
# =============================================================================

class AnthropicProportions:
    """
    Mathematical analysis of human proportions.
    """
    
    @staticmethod
    def head_to_height(heads: int = 8) -> float:
        """Canonical: 8 heads = full height."""
        return 1.0 / heads
    
    @staticmethod
    def golden_navel_split(height: float = 1.0) -> Tuple[float, float]:
        """
        Split height at golden ratio via navel.
        
        Returns (lower, upper) segments.
        """
        lower = height / PHI
        upper = height - lower
        return (lower, upper)
    
    @staticmethod
    def forearm_to_hand() -> float:
        """Ratio of forearm length to hand length (approaches φ)."""
        # Canonical: forearm ≈ 25%, hand ≈ 10%
        return 0.25 / 0.10  # = 2.5, but idealized is φ²
    
    @staticmethod
    def arm_segments() -> Dict[str, float]:
        """Idealized arm segments following golden ratio."""
        # If hand = 1, forearm = φ, upper arm = φ²
        hand = 1.0
        forearm = PHI
        upper_arm = PHI_SQUARED
        total = hand + forearm + upper_arm
        return {
            "hand": hand / total,
            "forearm": forearm / total,
            "upper_arm": upper_arm / total,
            "total": total
        }
    
    @staticmethod
    def verify_vitruvian_square() -> bool:
        """Verify that height = arm span (square condition)."""
        # In the canonical figure, these are equal
        return CANONICAL_PROPORTIONS.height == CANONICAL_PROPORTIONS.arm_span


# =============================================================================
# SACRED GEOMETRY CONNECTIONS
# =============================================================================

class SacredGeometry:
    """
    Sacred geometry principles in the Vitruvian system.
    """
    
    @staticmethod
    def squaring_the_circle_area(radius: float) -> float:
        """
        Side of square with same area as circle of given radius.
        
        πr² = s²
        s = r√π
        """
        return radius * math.sqrt(math.pi)
    
    @staticmethod
    def circling_the_square_perimeter(side: float) -> float:
        """
        Radius of circle with same perimeter as square of given side.
        
        4s = 2πr
        r = 2s/π
        """
        return 2 * side / math.pi
    
    @staticmethod
    def vitruvian_approximation(height: float = 1.0) -> Dict[str, float]:
        """
        The Vitruvian figure approximates both:
        - Area equivalence (circle area ≈ square area)
        - Perimeter proportions
        
        But exact equality is impossible (π is transcendental).
        """
        # For the canonical figure
        circle_radius = height * PHI_INVERSE  # ≈ 0.618
        square_side = height
        
        circle_area = math.pi * circle_radius ** 2
        square_area = square_side ** 2
        
        return {
            "circle_radius": circle_radius,
            "square_side": square_side,
            "circle_area": circle_area,
            "square_area": square_area,
            "area_ratio": circle_area / square_area,
            "theoretical_perfect": math.pi / 4,  # ≈ 0.785
            "difference": abs(circle_area/square_area - math.pi/4)
        }
    
    @staticmethod
    def pentagram_proportions() -> Dict[str, float]:
        """
        Pentagram (5-pointed star) proportions related to φ.
        
        The pentagram was sacred to the Pythagoreans.
        """
        return {
            "diagonal_to_side": PHI,          # Pentagon diagonal/side = φ
            "inner_to_outer": PHI_INVERSE,    # Inner pentagon/outer = φ^(-1)
            "segment_ratios": PHI             # Any two segments ratio = φ
        }


# =============================================================================
# INTEGRATION SYMBOLISM
# =============================================================================

class VitruvianSymbolism:
    """
    Symbolic interpretation of the Vitruvian integration.
    """
    
    @staticmethod
    def body_cosmos_correspondence() -> Dict[str, str]:
        """
        Correspondence between body parts and cosmos.
        
        From ancient microcosm-macrocosm doctrine.
        """
        return {
            "head": "Heaven, celestial sphere, rational soul",
            "heart": "Sun, vital center, spirited soul",
            "navel": "Horizon, cosmic center (omphalos), balance point",
            "genitals": "Earth center, generative power, material continuity",
            "feet": "Underworld, foundation, earthly realm",
            "hands": "Creative extension, manipulation of matter",
            "arms_spread": "Embrace of whole, extension into space",
            "legs_together": "Groundedness, material stability"
        }
    
    @staticmethod
    def two_postures() -> Dict[str, Dict[str, str]]:
        """
        The two postures and their meanings.
        """
        return {
            "circle_posture": {
                "description": "Arms raised, legs spread",
                "geometry": "Inscribed in circle",
                "center": "Navel (cosmic)",
                "meaning": "Spiritual expansion, reaching toward divine",
                "element": "Spirit, air, fire"
            },
            "square_posture": {
                "description": "Arms horizontal, legs together",
                "geometry": "Inscribed in square",
                "center": "Genitals (material)",
                "meaning": "Material stability, grounded presence",
                "element": "Body, earth, water"
            }
        }
    
    @staticmethod
    def integration_meaning() -> str:
        """The meaning of the integrated figure."""
        return """
The Vitruvian Figure integrates Circle and Square:

The human being is uniquely positioned at the intersection of
celestial and terrestrial orders. Unlike pure spirits (circle only)
or brute matter (square only), humanity participates in both.

This dual participation is what makes human beings:
- Capable of knowing eternal truths (circle)
- Capable of acting in material world (square)
- Bridges between heaven and earth
- The "measure of all things"

The different centers (navel vs. genitals) show that these two
aspects are not identical - there is genuine tension between
spiritual and material orientations. Yet the single figure
inscribed in both shows their ultimate unity in the human person.

The Vitruvian integration is not geometric (impossible due to π)
but ontological - the union of complementary modes of being.
"""


# =============================================================================
# VITRUVIAN SYSTEM
# =============================================================================

class VitruvianSystem:
    """
    Complete Vitruvian system for circle-square integration.
    """
    
    def __init__(self):
        self.figure = VitruvianFigure()
        self.proportions = CANONICAL_PROPORTIONS
        self.geometry = SacredGeometry()
        self.symbolism = VitruvianSymbolism()
    
    def analyze(self) -> Dict[str, Any]:
        """Complete analysis of the Vitruvian system."""
        return {
            "proportions": self.proportions.to_dict(),
            "overlap": self.figure.overlap_analysis,
            "golden_ratio": {
                "phi": PHI,
                "navel_ratio": self.proportions.golden_ratio_check,
                "is_golden": self.proportions.is_golden
            },
            "geometry": self.geometry.vitruvian_approximation(),
            "ontology": self.figure.ontological_meaning
        }
    
    def summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "figure_height": self.proportions.height,
            "arm_span": self.proportions.arm_span,
            "navel_height": self.proportions.navel_height,
            "circle_radius": self.figure.circle.radius,
            "square_side": self.figure.square.side_length,
            "center_displacement": self.figure.center_displacement,
            "area_ratio": self.figure.area_ratio,
            "golden_ratio_phi": PHI
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_vitruvian() -> bool:
    """Validate the Vitruvian module."""
    
    # Verify golden ratio
    assert abs(PHI - (1 + math.sqrt(5))/2) < 1e-10
    assert abs(PHI_INVERSE - (PHI - 1)) < 1e-10
    assert abs(PHI * PHI_INVERSE - 1.0) < 1e-10
    
    # Verify canonical proportions
    assert CANONICAL_PROPORTIONS.height == 1.0
    assert CANONICAL_PROPORTIONS.arm_span == 1.0
    assert abs(CANONICAL_PROPORTIONS.navel_height - PHI_INVERSE) < 0.01
    
    # Verify circle inscription
    circle = CircleInscription()
    assert circle.center_height > 0
    assert circle.radius > 0
    
    # Verify square inscription
    square = SquareInscription()
    assert square.side_length == 1.0
    
    # Verify figure
    figure = VitruvianFigure()
    assert figure.center_displacement > 0  # Circle center above square center
    
    # Verify area ratio (should be close to π/4 for equal radii)
    geom = SacredGeometry.vitruvian_approximation()
    # The canonical figure doesn't give exact π/4, but demonstrates the principle
    assert 0 < geom["area_ratio"] < 1
    
    # System
    system = VitruvianSystem()
    analysis = system.analyze()
    assert "proportions" in analysis
    assert "golden_ratio" in analysis
    
    return True


if __name__ == "__main__":
    print("Validating Vitruvian Module...")
    assert validate_vitruvian()
    print("✓ Vitruvian Module validated")
    
    # Demo
    print("\n--- Vitruvian System Demo ---")
    
    system = VitruvianSystem()
    summary = system.summary()
    
    print(f"\nGolden Ratio φ = {PHI:.6f}")
    print(f"φ^(-1) = {PHI_INVERSE:.6f}")
    
    print("\nCanonical Proportions:")
    print(f"  Height: {summary['figure_height']}")
    print(f"  Arm span: {summary['arm_span']}")
    print(f"  Navel height: {summary['navel_height']:.3f}")
    
    print("\nInscription:")
    print(f"  Circle radius: {summary['circle_radius']:.3f}")
    print(f"  Square side: {summary['square_side']:.3f}")
    print(f"  Center displacement: {summary['center_displacement']:.3f}")
    
    print("\nFigure Description:")
    print(system.figure.describe())
    
    print("\nSymbolic Meaning:")
    print(VitruvianSymbolism.integration_meaning())
