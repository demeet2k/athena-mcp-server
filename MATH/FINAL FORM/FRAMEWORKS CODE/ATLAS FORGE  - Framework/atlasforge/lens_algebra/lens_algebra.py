"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        LENS ALGEBRA MODULE                                   ║
║                                                                              ║
║  Vesica Piscis, Lens Chains, and Flower of Life                              ║
║                                                                              ║
║  Vesica Piscis:                                                              ║
║    Intersection of two equal circles with centers on each other's boundary   ║
║    Height/Width ratio = √3                                                   ║
║    Fundamental lens from which sacred geometry is constructed                ║
║                                                                              ║
║  Lens Chain:                                                                 ║
║    Sequence of overlapping circles forming connected vesicas                 ║
║    Each intersection creates a lens region                                   ║
║                                                                              ║
║  Flower of Life:                                                             ║
║    Circle packing on A₂ (triangular) lattice                                 ║
║    Standing-wave pattern on the plane                                        ║
║    7 circles: 1 center + 6 surrounding                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# SACRED CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SacredConstants:
    """
    Constants from sacred geometry.
    """
    SQRT_3: float = np.sqrt(3)                  # Height/width of vesica
    PHI: float = (1 + np.sqrt(5)) / 2           # Golden ratio φ
    SILVER: float = 1 + np.sqrt(2)              # Silver ratio δ_S
    BRONZE: float = (3 + np.sqrt(13)) / 2       # Bronze ratio
    
    # Common angles
    PI_6: float = np.pi / 6    # 30°
    PI_4: float = np.pi / 4    # 45°
    PI_3: float = np.pi / 3    # 60°
    PI_2: float = np.pi / 2    # 90°
    
    # A₂ lattice basis angle
    A2_ANGLE: float = np.pi / 3  # 60° between basis vectors


# ═══════════════════════════════════════════════════════════════════════════════
# VESICA PISCIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Circle:
    """A circle in the plane."""
    center: Tuple[float, float]
    radius: float = 1.0
    
    def point_at_angle(self, theta: float) -> Tuple[float, float]:
        """Point on circle at angle θ from center."""
        return (
            self.center[0] + self.radius * np.cos(theta),
            self.center[1] + self.radius * np.sin(theta)
        )
    
    def contains(self, point: Tuple[float, float], tol: float = 1e-10) -> bool:
        """Check if point is inside or on circle."""
        dx = point[0] - self.center[0]
        dy = point[1] - self.center[1]
        return dx**2 + dy**2 <= self.radius**2 + tol
    
    def intersects(self, other: 'Circle') -> bool:
        """Check if circles intersect."""
        dx = other.center[0] - self.center[0]
        dy = other.center[1] - self.center[1]
        dist = np.sqrt(dx**2 + dy**2)
        return abs(self.radius - other.radius) < dist < self.radius + other.radius
    
    def intersection_points(self, other: 'Circle') -> List[Tuple[float, float]]:
        """Find intersection points with another circle."""
        dx = other.center[0] - self.center[0]
        dy = other.center[1] - self.center[1]
        d = np.sqrt(dx**2 + dy**2)
        
        if d > self.radius + other.radius or d < abs(self.radius - other.radius):
            return []  # No intersection
        
        if d < 1e-10:
            return []  # Concentric circles
        
        # Distance from self.center to chord
        a = (self.radius**2 - other.radius**2 + d**2) / (2 * d)
        
        # Height of chord from line joining centers
        h_sq = self.radius**2 - a**2
        if h_sq < 0:
            return []
        h = np.sqrt(h_sq)
        
        # Midpoint of chord
        mx = self.center[0] + a * dx / d
        my = self.center[1] + a * dy / d
        
        # Two intersection points
        p1 = (mx + h * (-dy) / d, my + h * dx / d)
        p2 = (mx - h * (-dy) / d, my - h * dx / d)
        
        return [p1, p2]


@dataclass
class VesicaPiscis:
    """
    Vesica Piscis: intersection of two equal circles.
    
    When two circles of radius r have centers on each other's boundary
    (distance = r), their intersection forms a lens (vesica piscis).
    
    Properties:
    - Height (major axis) = r√3
    - Width (minor axis) = r
    - Height/Width = √3
    - Area = (π/3 - √3/2)r² ≈ 0.181r²
    """
    circle1: Circle
    circle2: Circle
    
    @classmethod
    def standard(cls, radius: float = 1.0) -> 'VesicaPiscis':
        """
        Create standard vesica with:
        - Circle 1 centered at origin
        - Circle 2 centered at (r, 0)
        """
        c1 = Circle((0.0, 0.0), radius)
        c2 = Circle((radius, 0.0), radius)
        return cls(c1, c2)
    
    @property
    def radius(self) -> float:
        """Common radius of both circles."""
        return self.circle1.radius
    
    @property
    def width(self) -> float:
        """Width (minor axis) of vesica = r."""
        return self.radius
    
    @property
    def height(self) -> float:
        """Height (major axis) of vesica = r√3."""
        return self.radius * np.sqrt(3)
    
    @property
    def aspect_ratio(self) -> float:
        """Height/Width = √3 ≈ 1.732."""
        return np.sqrt(3)
    
    @property
    def area(self) -> float:
        """Area of vesica = (2π/3 - √3/2)r²."""
        r = self.radius
        return (2 * np.pi / 3 - np.sqrt(3) / 2) * r**2
    
    @property
    def intersection_points(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """The two intersection points of the circles."""
        points = self.circle1.intersection_points(self.circle2)
        if len(points) >= 2:
            return (points[0], points[1])
        return ((0, 0), (0, 0))
    
    @property
    def center(self) -> Tuple[float, float]:
        """Center of the vesica (midpoint of line joining circle centers)."""
        return (
            (self.circle1.center[0] + self.circle2.center[0]) / 2,
            (self.circle1.center[1] + self.circle2.center[1]) / 2
        )
    
    def contains(self, point: Tuple[float, float]) -> bool:
        """Check if point is inside the vesica."""
        return self.circle1.contains(point) and self.circle2.contains(point)


# ═══════════════════════════════════════════════════════════════════════════════
# LENS CHAIN
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LensChain:
    """
    A chain of overlapping circles forming connected vesicas.
    
    Each consecutive pair of circles creates a vesica piscis.
    """
    circles: List[Circle]
    
    @classmethod
    def linear(cls, n: int, radius: float = 1.0, 
               overlap_fraction: float = 0.5) -> 'LensChain':
        """
        Create a linear chain of n circles.
        
        overlap_fraction = 0.5 means circles overlap by r/2 (standard vesica).
        overlap_fraction = 1.0 means centers coincide.
        """
        circles = []
        spacing = radius * (2 - overlap_fraction)
        
        for i in range(n):
            center = (i * spacing, 0.0)
            circles.append(Circle(center, radius))
        
        return cls(circles)
    
    @classmethod
    def circular(cls, n: int, radius: float = 1.0) -> 'LensChain':
        """
        Create a circular arrangement of n circles around a central point.
        
        For n=6, this is the seed of the Flower of Life.
        """
        circles = []
        # Central circle
        circles.append(Circle((0.0, 0.0), radius))
        
        # Surrounding circles
        for i in range(n):
            angle = 2 * np.pi * i / n
            center = (radius * np.cos(angle), radius * np.sin(angle))
            circles.append(Circle(center, radius))
        
        return cls(circles)
    
    @property
    def n_circles(self) -> int:
        """Number of circles in chain."""
        return len(self.circles)
    
    def get_vesica(self, i: int, j: int) -> Optional[VesicaPiscis]:
        """Get vesica formed by circles i and j if they intersect."""
        if not self.circles[i].intersects(self.circles[j]):
            return None
        return VesicaPiscis(self.circles[i], self.circles[j])
    
    def all_vesicas(self) -> List[VesicaPiscis]:
        """Get all vesicas in the chain."""
        vesicas = []
        for i in range(self.n_circles):
            for j in range(i + 1, self.n_circles):
                v = self.get_vesica(i, j)
                if v is not None:
                    vesicas.append(v)
        return vesicas
    
    def intersection_graph(self) -> NDArray:
        """
        Adjacency matrix where entry (i,j) = 1 if circles i,j intersect.
        """
        n = self.n_circles
        adj = np.zeros((n, n), dtype=int)
        for i in range(n):
            for j in range(i + 1, n):
                if self.circles[i].intersects(self.circles[j]):
                    adj[i, j] = 1
                    adj[j, i] = 1
        return adj


# ═══════════════════════════════════════════════════════════════════════════════
# FLOWER OF LIFE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FlowerOfLife:
    """
    Flower of Life: circle packing on the A₂ (triangular) lattice.
    
    The basic Flower of Life consists of 7 circles:
    - 1 central circle
    - 6 surrounding circles at 60° intervals
    
    Extended versions add concentric shells of 12, 18, 24, ... circles.
    """
    radius: float = 1.0
    shells: int = 1  # Number of concentric shells (1 = basic 7 circles)
    
    @property
    def n_circles(self) -> int:
        """Total number of circles."""
        # Shell k has 6k circles, plus 1 for center
        return 1 + sum(6 * k for k in range(1, self.shells + 1))
    
    def circle_centers(self) -> List[Tuple[float, float]]:
        """Get all circle centers on A₂ lattice."""
        centers = [(0.0, 0.0)]  # Central circle
        
        for shell in range(1, self.shells + 1):
            # Each shell has 6 * shell circles arranged hexagonally
            # Start at angle 0 and go around
            for i in range(6):
                base_angle = i * np.pi / 3
                
                # Points along edge of hexagon at this shell
                for j in range(shell):
                    # Interpolate along hexagon edge
                    angle1 = base_angle
                    angle2 = base_angle + np.pi / 3
                    
                    # Center positions
                    t = j / shell
                    x = self.radius * shell * ((1-t) * np.cos(angle1) + t * np.cos(angle2))
                    y = self.radius * shell * ((1-t) * np.sin(angle1) + t * np.sin(angle2))
                    
                    centers.append((x, y))
        
        return centers
    
    def get_circles(self) -> List[Circle]:
        """Get all circles in the Flower of Life."""
        return [Circle(c, self.radius) for c in self.circle_centers()]
    
    def as_lens_chain(self) -> LensChain:
        """Convert to lens chain."""
        return LensChain(self.get_circles())
    
    def count_vesicas(self) -> int:
        """Count total number of vesica intersections."""
        chain = self.as_lens_chain()
        return len(chain.all_vesicas())
    
    @staticmethod
    def a2_lattice_basis() -> Tuple[NDArray, NDArray]:
        """
        Basis vectors for A₂ (triangular) lattice.
        
        e₁ = (1, 0)
        e₂ = (1/2, √3/2)
        """
        e1 = np.array([1.0, 0.0])
        e2 = np.array([0.5, np.sqrt(3) / 2])
        return e1, e2
    
    @staticmethod
    def a2_lattice_point(n: int, m: int, scale: float = 1.0) -> Tuple[float, float]:
        """Get lattice point n·e₁ + m·e₂."""
        e1, e2 = FlowerOfLife.a2_lattice_basis()
        point = scale * (n * e1 + m * e2)
        return (point[0], point[1])


# ═══════════════════════════════════════════════════════════════════════════════
# NEXUS RADII
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NexusRadius:
    """
    Nexus radius: a radius at which multiple polygonal shells intersect.
    
    These special radii are governed by Pell-like recurrences and
    quadratic irrationals.
    """
    value: float
    description: str
    polygon_orders: List[int]  # Polygon orders that meet at this radius
    
    @classmethod
    def unit_circle_nexuses(cls) -> List['NexusRadius']:
        """Standard nexus radii on the unit circle."""
        return [
            cls(1.0, "Unit radius", [3, 4, 6]),
            cls(np.sqrt(2), "√2: diagonal of unit square", [4, 8]),
            cls(np.sqrt(3), "√3: height of equilateral triangle", [3, 6]),
            cls((1 + np.sqrt(5)) / 2, "φ: golden ratio (pentagon)", [5, 10]),
            cls(2.0, "Double unit", [3, 4, 6]),
            cls(1 + np.sqrt(2), "Silver ratio", [8]),
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# STANDING WAVE INTERPRETATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CirclePackingWave:
    """
    Interpretation of circle packing as standing wave pattern.
    
    The Flower of Life can be seen as a 2D standing wave with
    6-fold symmetry (k=6 angular mode).
    """
    packing: FlowerOfLife
    
    def wave_at_point(self, x: float, y: float) -> float:
        """
        Approximate wave amplitude at point (x,y).
        
        Uses superposition of modes from circle centers.
        """
        total = 0.0
        r = self.packing.radius
        
        for cx, cy in self.packing.circle_centers():
            # Distance from circle center
            d = np.sqrt((x - cx)**2 + (y - cy)**2)
            # Wave contribution (Bessel-like decay)
            if d < r:
                total += np.cos(np.pi * d / r)
        
        return total
    
    def sample_wave(self, nx: int = 100, ny: int = 100,
                    extent: float = 5.0) -> NDArray:
        """Sample wave on a grid."""
        x = np.linspace(-extent, extent, nx)
        y = np.linspace(-extent, extent, ny)
        
        wave = np.zeros((ny, nx))
        for i, yi in enumerate(y):
            for j, xj in enumerate(x):
                wave[i, j] = self.wave_at_point(xj, yi)
        
        return wave


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LensPoleBridge:
    """
    Bridge between Lens Algebra and four-pole framework.
    """
    
    @staticmethod
    def integration() -> str:
        return """
        LENS ALGEBRA ↔ FRAMEWORK
        
        Vesica Piscis:
          - Two circles on ✿ Flower chart (continuous)
          - Intersection region = □ Square chart (bounded)
          - Height/Width = √3 (A₂ lattice constant)
        
        Lens Chain:
          - Sequence of overlapping circles
          - Intersection graph → discrete structure
          - Wave ↔ Particle duality manifest
        
        Flower of Life:
          - A₂ (triangular) lattice packing
          - 6-fold symmetry (k=6 mode)
          - Standing wave on plane
          - 7 circles = 1 + 6 (center + shell)
        
        Sacred Constants:
          √3 : Equilateral triangle, vesica aspect
          φ  : Golden ratio, pentagon
          δ_S: Silver ratio, octagon
          
        Chart Mapping:
          Circles → ✿ Flower (continuous phase)
          Intersections → □ Square (discrete points)
          Overlap regions → ☁ Cloud (bounded uncertainty)
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def sacred_constants() -> SacredConstants:
    """Get sacred geometry constants."""
    return SacredConstants()


def circle(center: Tuple[float, float], radius: float = 1.0) -> Circle:
    """Create circle."""
    return Circle(center, radius)


def vesica_piscis(radius: float = 1.0) -> VesicaPiscis:
    """Create standard vesica piscis."""
    return VesicaPiscis.standard(radius)


def lens_chain_linear(n: int, radius: float = 1.0) -> LensChain:
    """Create linear lens chain."""
    return LensChain.linear(n, radius)


def lens_chain_circular(n: int, radius: float = 1.0) -> LensChain:
    """Create circular lens chain."""
    return LensChain.circular(n, radius)


def flower_of_life(radius: float = 1.0, shells: int = 1) -> FlowerOfLife:
    """Create Flower of Life."""
    return FlowerOfLife(radius, shells)


def nexus_radii() -> List[NexusRadius]:
    """Get standard nexus radii."""
    return NexusRadius.unit_circle_nexuses()


def circle_packing_wave(packing: FlowerOfLife) -> CirclePackingWave:
    """Create standing wave interpretation."""
    return CirclePackingWave(packing)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Constants
    'SacredConstants',
    
    # Circle
    'Circle',
    
    # Vesica
    'VesicaPiscis',
    
    # Chains
    'LensChain',
    
    # Flower of Life
    'FlowerOfLife',
    
    # Nexus
    'NexusRadius',
    
    # Wave
    'CirclePackingWave',
    
    # Bridge
    'LensPoleBridge',
    
    # Functions
    'sacred_constants',
    'circle',
    'vesica_piscis',
    'lens_chain_linear',
    'lens_chain_circular',
    'flower_of_life',
    'nexus_radii',
    'circle_packing_wave',
]
