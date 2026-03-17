"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      HYPERBOLIC GEOMETRY MODULE                              ║
║                                                                              ║
║  Poincaré Models, Geodesics, and Isometries                                  ║
║                                                                              ║
║  Core Principle:                                                             ║
║    The gateway algebra lives naturally in hyperbolic geometry.               ║
║    The boost parameter T ∈ (-1,1) is a Cayley coordinate on the             ║
║    Poincaré disk, and gateway matrices are hyperbolic isometries.           ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Poincaré disk model: 𝔻 = {z ∈ ℂ : |z| < 1}                             ║
║    - Poincaré half-plane: ℍ = {z ∈ ℂ : Im(z) > 0}                           ║
║    - Metric: ds² = 4|dz|²/(1-|z|²)² on disk                                 ║
║    - Geodesics: Circular arcs perpendicular to boundary                     ║
║    - Isometries: PSL(2,ℝ) action via Möbius transformations                 ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Gateway T ↔ Poincaré disk coordinate                                   ║
║    - Rapidity α = artanh(T) ↔ hyperbolic distance                           ║
║    - Boost composition ↔ hyperbolic translation                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Callable, Union
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLEX NUMBER UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def mobius_transform(z: complex, a: complex, b: complex, 
                    c: complex, d: complex) -> complex:
    """
    Apply Möbius transformation: w = (az + b)/(cz + d)
    """
    denom = c * z + d
    if abs(denom) < 1e-15:
        return complex(float('inf'), 0)
    return (a * z + b) / denom


def cross_ratio(z1: complex, z2: complex, z3: complex, z4: complex) -> complex:
    """
    Cross-ratio (z1, z2; z3, z4) = (z1-z3)(z2-z4) / (z1-z4)(z2-z3)
    
    Invariant under Möbius transformations.
    """
    return ((z1 - z3) * (z2 - z4)) / ((z1 - z4) * (z2 - z3))


# ═══════════════════════════════════════════════════════════════════════════════
# POINCARÉ DISK MODEL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PoincareDisk:
    """
    The Poincaré disk model of hyperbolic geometry.
    
    𝔻 = {z ∈ ℂ : |z| < 1}
    
    Metric: ds² = 4|dz|²/(1 - |z|²)²
    Curvature: K = -1
    
    This is the natural home of the gateway parameter T.
    """
    
    @staticmethod
    def is_interior(z: complex, tol: float = 1e-10) -> bool:
        """Check if point is in the open disk."""
        return abs(z) < 1 - tol
    
    @staticmethod
    def distance(z1: complex, z2: complex) -> float:
        """
        Hyperbolic distance between two points.
        
        d(z1, z2) = 2 artanh(|z1 - z2| / |1 - z̄1·z2|)
        """
        if abs(z1) >= 1 or abs(z2) >= 1:
            return float('inf')
        
        diff = z1 - z2
        denom = 1 - np.conj(z1) * z2
        
        ratio = abs(diff / denom)
        ratio = min(ratio, 1 - 1e-15)  # Numerical safety
        
        return 2 * np.arctanh(ratio)
    
    @staticmethod
    def metric_tensor(z: complex) -> float:
        """
        Conformal factor λ(z) where ds² = λ²|dz|².
        
        λ(z) = 2/(1 - |z|²)
        """
        r_sq = abs(z) ** 2
        if r_sq >= 1:
            return float('inf')
        return 2 / (1 - r_sq)
    
    @staticmethod
    def area_element(z: complex) -> float:
        """
        Hyperbolic area element: dA = λ²(z) dx dy
        """
        lam = PoincareDisk.metric_tensor(z)
        return lam ** 2
    
    @staticmethod
    def geodesic_midpoint(z1: complex, z2: complex) -> complex:
        """
        Midpoint of geodesic segment from z1 to z2.
        """
        # Use Möbius transformation to move z1 to origin
        # midpoint, then transform back
        
        if abs(z1) < 1e-15:
            # z1 is at origin
            d = PoincareDisk.distance(0, z2)
            t = np.tanh(d / 4)  # Half the hyperbolic distance
            return t * z2 / abs(z2) if abs(z2) > 1e-15 else 0
        
        # Move z1 to origin
        def to_origin(z):
            return (z - z1) / (1 - np.conj(z1) * z)
        
        def from_origin(w):
            return (w + z1) / (1 + np.conj(z1) * w)
        
        w2 = to_origin(z2)
        d = PoincareDisk.distance(0, w2)
        t = np.tanh(d / 4)
        w_mid = t * w2 / abs(w2) if abs(w2) > 1e-15 else 0
        
        return from_origin(w_mid)
    
    @staticmethod
    def to_half_plane(z: complex) -> complex:
        """
        Map from Poincaré disk to upper half-plane.
        
        Cayley transform: w = i(1 + z)/(1 - z)
        """
        if abs(z - 1) < 1e-15:
            return complex(float('inf'), 0)
        return 1j * (1 + z) / (1 - z)
    
    @staticmethod
    def from_half_plane(w: complex) -> complex:
        """
        Map from upper half-plane to Poincaré disk.
        
        Inverse Cayley: z = (w - i)/(w + i)
        """
        return (w - 1j) / (w + 1j)


# ═══════════════════════════════════════════════════════════════════════════════
# POINCARÉ HALF-PLANE MODEL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PoincareHalfPlane:
    """
    The upper half-plane model of hyperbolic geometry.
    
    ℍ = {z ∈ ℂ : Im(z) > 0}
    
    Metric: ds² = |dz|²/y² where y = Im(z)
    
    Natural for SL(2,ℝ) action: z ↦ (az + b)/(cz + d)
    """
    
    @staticmethod
    def is_interior(z: complex, tol: float = 1e-10) -> bool:
        """Check if point is in the upper half-plane."""
        return z.imag > tol
    
    @staticmethod
    def distance(z1: complex, z2: complex) -> float:
        """
        Hyperbolic distance in the half-plane.
        
        d(z1, z2) = arcosh(1 + |z1 - z2|²/(2·Im(z1)·Im(z2)))
        """
        if z1.imag <= 0 or z2.imag <= 0:
            return float('inf')
        
        diff_sq = abs(z1 - z2) ** 2
        prod = 2 * z1.imag * z2.imag
        
        arg = 1 + diff_sq / prod
        return np.arccosh(arg)
    
    @staticmethod
    def metric_tensor(z: complex) -> float:
        """
        Conformal factor: λ(z) = 1/Im(z)
        """
        if z.imag <= 0:
            return float('inf')
        return 1 / z.imag
    
    @staticmethod
    def geodesic_type(z1: complex, z2: complex) -> str:
        """
        Determine geodesic type between two points.
        
        Returns 'vertical' if Re(z1) = Re(z2), else 'semicircle'.
        """
        if abs(z1.real - z2.real) < 1e-10:
            return 'vertical'
        return 'semicircle'
    
    @staticmethod
    def geodesic_center_radius(z1: complex, z2: complex
                              ) -> Optional[Tuple[float, float]]:
        """
        For semicircle geodesic, return (center_x, radius).
        
        Returns None if geodesic is vertical.
        """
        if abs(z1.real - z2.real) < 1e-10:
            return None
        
        # Semicircle centered on real axis
        # |z - c|² = r² with Im(z) = 0 on boundary
        x1, y1 = z1.real, z1.imag
        x2, y2 = z2.real, z2.imag
        
        # Center: (x1² + y1² - x2² - y2²)/(2(x1 - x2))
        c = (x1**2 + y1**2 - x2**2 - y2**2) / (2 * (x1 - x2))
        r = np.sqrt((x1 - c)**2 + y1**2)
        
        return (c, r)


# ═══════════════════════════════════════════════════════════════════════════════
# HYPERBOLIC ISOMETRIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HyperbolicIsometry:
    """
    Isometry of the hyperbolic plane.
    
    Represented as PSL(2,ℝ) matrix acting on the half-plane,
    or equivalently as PSU(1,1) on the disk.
    """
    a: complex
    b: complex
    c: complex
    d: complex
    
    def __post_init__(self):
        # Normalize to det = 1
        det = self.a * self.d - self.b * self.c
        if abs(det) < 1e-15:
            raise ValueError("Singular matrix")
        sqrt_det = np.sqrt(det)
        self.a /= sqrt_det
        self.b /= sqrt_det
        self.c /= sqrt_det
        self.d /= sqrt_det
    
    def apply_half_plane(self, z: complex) -> complex:
        """Apply to point in half-plane."""
        return mobius_transform(z, self.a, self.b, self.c, self.d)
    
    def apply_disk(self, z: complex) -> complex:
        """Apply to point in disk via conjugation."""
        # Convert to half-plane, apply, convert back
        w = PoincareDisk.to_half_plane(z)
        w_image = self.apply_half_plane(w)
        return PoincareDisk.from_half_plane(w_image)
    
    def compose(self, other: 'HyperbolicIsometry') -> 'HyperbolicIsometry':
        """Compose two isometries: (self ∘ other)."""
        # Matrix multiplication
        new_a = self.a * other.a + self.b * other.c
        new_b = self.a * other.b + self.b * other.d
        new_c = self.c * other.a + self.d * other.c
        new_d = self.c * other.b + self.d * other.d
        return HyperbolicIsometry(new_a, new_b, new_c, new_d)
    
    def inverse(self) -> 'HyperbolicIsometry':
        """Inverse isometry."""
        return HyperbolicIsometry(self.d, -self.b, -self.c, self.a)
    
    @property
    def trace(self) -> complex:
        """Trace of the matrix."""
        return self.a + self.d
    
    @property
    def isometry_type(self) -> str:
        """
        Classify isometry by trace.
        
        |tr| < 2: elliptic (rotation)
        |tr| = 2: parabolic (limit rotation)
        |tr| > 2: hyperbolic (translation)
        """
        tr = abs(self.trace)
        if tr < 2 - 1e-10:
            return 'elliptic'
        elif tr < 2 + 1e-10:
            return 'parabolic'
        else:
            return 'hyperbolic'
    
    @property
    def translation_length(self) -> float:
        """
        For hyperbolic isometry, the translation distance.
        
        ℓ = 2 arcosh(|tr|/2)
        """
        tr = abs(self.trace)
        if tr <= 2:
            return 0.0
        return 2 * np.arccosh(tr / 2)
    
    @classmethod
    def translation(cls, distance: float, direction: float = 0
                   ) -> 'HyperbolicIsometry':
        """
        Hyperbolic translation along axis.
        
        direction: angle of translation axis
        """
        t = distance / 2
        a = np.cosh(t) + 1j * np.sinh(t) * np.sin(direction)
        b = np.sinh(t) * np.cos(direction)
        c = np.sinh(t) * np.cos(direction)
        d = np.cosh(t) - 1j * np.sinh(t) * np.sin(direction)
        return cls(a, b, c, d)
    
    @classmethod
    def rotation(cls, angle: float, center: complex = 1j
                ) -> 'HyperbolicIsometry':
        """
        Elliptic rotation about a point.
        
        center: point in half-plane
        """
        # Conjugate: move center to i, rotate, move back
        # For center = i: simply [[cos(θ/2), sin(θ/2)], [-sin(θ/2), cos(θ/2)]]
        t = angle / 2
        return cls(np.cos(t), np.sin(t), -np.sin(t), np.cos(t))
    
    @classmethod
    def identity(cls) -> 'HyperbolicIsometry':
        """Identity isometry."""
        return cls(1, 0, 0, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# HYPERBOLIC GEODESIC
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HyperbolicGeodesic:
    """
    A geodesic in the hyperbolic plane.
    
    Can be represented in either disk or half-plane model.
    """
    # Two points determining the geodesic
    z1: complex
    z2: complex
    model: str = 'disk'  # 'disk' or 'halfplane'
    
    def point_at_parameter(self, t: float) -> complex:
        """
        Point on geodesic at parameter t ∈ [0, 1].
        
        t=0 gives z1, t=1 gives z2.
        """
        if self.model == 'disk':
            return self._disk_geodesic_point(t)
        else:
            return self._halfplane_geodesic_point(t)
    
    def _disk_geodesic_point(self, t: float) -> complex:
        """Point on geodesic in disk model."""
        # Move z1 to origin, parameterize, move back
        def to_origin(z):
            return (z - self.z1) / (1 - np.conj(self.z1) * z)
        
        def from_origin(w):
            return (w + self.z1) / (1 + np.conj(self.z1) * w)
        
        w2 = to_origin(self.z2)
        
        # In disk centered at origin, geodesic through origin is diameter
        d = PoincareDisk.distance(0, w2)
        s = np.tanh(t * d / 2)
        w = s * w2 / abs(w2) if abs(w2) > 1e-15 else 0
        
        return from_origin(w)
    
    def _halfplane_geodesic_point(self, t: float) -> complex:
        """Point on geodesic in half-plane model."""
        if abs(self.z1.real - self.z2.real) < 1e-10:
            # Vertical geodesic
            y1, y2 = self.z1.imag, self.z2.imag
            y = y1 * (y2 / y1) ** t
            return complex(self.z1.real, y)
        else:
            # Semicircle
            result = PoincareHalfPlane.geodesic_center_radius(self.z1, self.z2)
            if result is None:
                return self.z1
            c, r = result
            
            # Parameterize angle
            theta1 = np.arctan2(self.z1.imag, self.z1.real - c)
            theta2 = np.arctan2(self.z2.imag, self.z2.real - c)
            theta = (1 - t) * theta1 + t * theta2
            
            return complex(c + r * np.cos(theta), r * np.sin(theta))
    
    def length(self) -> float:
        """Hyperbolic length of the geodesic segment."""
        if self.model == 'disk':
            return PoincareDisk.distance(self.z1, self.z2)
        else:
            return PoincareHalfPlane.distance(self.z1, self.z2)
    
    def sample_points(self, n: int = 50) -> List[complex]:
        """Sample n points along the geodesic."""
        return [self.point_at_parameter(t) for t in np.linspace(0, 1, n)]


# ═══════════════════════════════════════════════════════════════════════════════
# HYPERBOLIC POLYGON
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HyperbolicPolygon:
    """
    A polygon with geodesic edges in the hyperbolic plane.
    """
    vertices: List[complex]
    model: str = 'disk'
    
    @property
    def n_sides(self) -> int:
        return len(self.vertices)
    
    def edges(self) -> List[HyperbolicGeodesic]:
        """List of geodesic edges."""
        edges = []
        n = len(self.vertices)
        for i in range(n):
            edges.append(HyperbolicGeodesic(
                self.vertices[i], 
                self.vertices[(i + 1) % n],
                self.model
            ))
        return edges
    
    def perimeter(self) -> float:
        """Total hyperbolic perimeter."""
        return sum(edge.length() for edge in self.edges())
    
    def interior_angle_sum(self) -> float:
        """
        Sum of interior angles.
        
        For hyperbolic polygon: sum < (n-2)π
        Defect = (n-2)π - sum = Area (Gauss-Bonnet)
        """
        # Compute angles at each vertex
        angles = []
        n = len(self.vertices)
        
        for i in range(n):
            prev_v = self.vertices[(i - 1) % n]
            curr_v = self.vertices[i]
            next_v = self.vertices[(i + 1) % n]
            
            # Angle at curr_v
            # In disk model, use tangent vectors
            if self.model == 'disk':
                # Direction to prev
                d1 = prev_v - curr_v
                # Direction to next
                d2 = next_v - curr_v
                
                # Correct for hyperbolic metric
                lam = PoincareDisk.metric_tensor(curr_v)
                
                # Angle between directions (Euclidean approximation at point)
                angle = abs(np.angle(d2) - np.angle(d1))
                if angle > np.pi:
                    angle = 2 * np.pi - angle
                angles.append(angle)
        
        return sum(angles)
    
    def area(self) -> float:
        """
        Hyperbolic area via Gauss-Bonnet.
        
        Area = (n-2)π - (sum of interior angles)
        """
        n = self.n_sides
        angle_sum = self.interior_angle_sum()
        return (n - 2) * np.pi - angle_sum
    
    @classmethod
    def regular(cls, n_sides: int, center: complex = 0, 
               circumradius: float = 0.5, model: str = 'disk') -> 'HyperbolicPolygon':
        """
        Regular hyperbolic polygon.
        
        Note: For large n or large radius, angles become very small.
        """
        vertices = []
        for i in range(n_sides):
            theta = 2 * np.pi * i / n_sides
            z = center + circumradius * np.exp(1j * theta)
            vertices.append(z)
        return cls(vertices, model)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNDAMENTAL DOMAIN
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FundamentalDomain:
    """
    Fundamental domain for a Fuchsian group.
    
    The modular group PSL(2,ℤ) has famous fundamental domain.
    """
    
    @staticmethod
    def modular_group_domain() -> List[complex]:
        """
        Vertices of fundamental domain for PSL(2,ℤ) in half-plane.
        
        Bounded by |z| = 1 and Re(z) = ±1/2
        Vertices: -1/2 + i√3/2, 1/2 + i√3/2, i∞
        """
        omega = -0.5 + 1j * np.sqrt(3) / 2
        omega_bar = 0.5 + 1j * np.sqrt(3) / 2
        return [omega, omega_bar]  # Third vertex at infinity
    
    @staticmethod
    def is_in_modular_domain(z: complex) -> bool:
        """
        Check if z is in the standard fundamental domain.
        
        |z| ≥ 1 and |Re(z)| ≤ 1/2
        """
        return abs(z) >= 1 - 1e-10 and abs(z.real) <= 0.5 + 1e-10
    
    @staticmethod
    def reduce_to_modular_domain(z: complex, max_iter: int = 100
                                ) -> Tuple[complex, List[Tuple[str, int]]]:
        """
        Reduce z to the fundamental domain.
        
        Returns (reduced_z, list of operations).
        Operations are ('T', n) for translation z -> z + n
        and ('S', 1) for inversion z -> -1/z
        """
        operations = []
        
        for _ in range(max_iter):
            # Translation: move Re(z) to [-1/2, 1/2]
            n = round(z.real)
            if n != 0:
                z = z - n
                operations.append(('T', -n))
            
            # Inversion if |z| < 1
            if abs(z) < 1 - 1e-10:
                z = -1 / z
                operations.append(('S', 1))
            else:
                break
        
        return z, operations


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY-HYPERBOLIC BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewayHyperbolicBridge:
    """
    Bridge between gateway algebra and hyperbolic geometry.
    
    The gateway parameter T ∈ (-1, 1) lives on the real diameter
    of the Poincaré disk.
    """
    
    @staticmethod
    def gateway_to_disk(T: float) -> complex:
        """Map gateway scalar to disk point."""
        if abs(T) >= 1:
            raise ValueError(f"T must be in (-1, 1), got {T}")
        return complex(T, 0)
    
    @staticmethod
    def disk_to_gateway(z: complex) -> float:
        """
        Map disk point to gateway scalar.
        
        Projects to real axis.
        """
        return z.real
    
    @staticmethod
    def rapidity_to_distance(alpha: float) -> float:
        """
        Map rapidity to hyperbolic distance.
        
        The rapidity α = artanh(T) is exactly the hyperbolic
        distance from origin to T on the disk.
        """
        return 2 * abs(alpha)
    
    @staticmethod
    def boost_to_isometry(T: float) -> HyperbolicIsometry:
        """
        Convert gateway boost B(T) to hyperbolic isometry.
        """
        alpha = np.arctanh(T)
        return HyperbolicIsometry.translation(2 * alpha, 0)
    
    @staticmethod
    def pell_to_isometry(u: int, v: int, A: int) -> HyperbolicIsometry:
        """
        Convert Pell solution (u, v) with u² - Av² = 1 to isometry.
        
        This is an integer point in PSL(2,ℤ).
        """
        sqrt_A = np.sqrt(A)
        return HyperbolicIsometry(
            complex(u, 0), complex(v * sqrt_A, 0),
            complex(v * sqrt_A, 0), complex(u, 0)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def hyperbolic_distance_disk(z1: complex, z2: complex) -> float:
    """Distance in Poincaré disk."""
    return PoincareDisk.distance(z1, z2)


def hyperbolic_distance_halfplane(z1: complex, z2: complex) -> float:
    """Distance in upper half-plane."""
    return PoincareHalfPlane.distance(z1, z2)


def disk_to_halfplane(z: complex) -> complex:
    """Cayley transform: disk → half-plane."""
    return PoincareDisk.to_half_plane(z)


def halfplane_to_disk(w: complex) -> complex:
    """Inverse Cayley: half-plane → disk."""
    return PoincareDisk.from_half_plane(w)


def hyperbolic_midpoint(z1: complex, z2: complex) -> complex:
    """Midpoint in disk model."""
    return PoincareDisk.geodesic_midpoint(z1, z2)


def classify_isometry(M: HyperbolicIsometry) -> str:
    """Classify isometry type."""
    return M.isometry_type


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Models
    'PoincareDisk',
    'PoincareHalfPlane',
    
    # Isometries
    'HyperbolicIsometry',
    
    # Geometric objects
    'HyperbolicGeodesic',
    'HyperbolicPolygon',
    'FundamentalDomain',
    
    # Bridge
    'GatewayHyperbolicBridge',
    
    # Utilities
    'mobius_transform',
    'cross_ratio',
    
    # Functions
    'hyperbolic_distance_disk',
    'hyperbolic_distance_halfplane',
    'disk_to_halfplane',
    'halfplane_to_disk',
    'hyperbolic_midpoint',
    'classify_isometry',
]
