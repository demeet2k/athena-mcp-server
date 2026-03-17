"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ATLAS FORGE - Operator Simplex                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

The operator simplex (3-simplex / tetrahedron) that organizes the
coefficient space for hybrid generators.

The coefficient vector α = (α_D, α_Ω, α_Σ, α_Ψ) lives on:
    Δ₃ = { α : α_• ≥ 0, Σα_• = 1 }

This provides a complete taxonomy:
- Vertices: Pure poles (D, Ω, Σ, Ψ)
- Edges: Dyadic interfaces (6 edges)
- Faces: Three-pole couplings (4 faces)
- Interior: Full four-pole hybrids
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Any, Dict, Generator, Iterator, List, Optional,
    Sequence, Tuple, Type, Union
)
import math
import numpy as np
from numpy.typing import NDArray

from atlasforge.core.enums import Pole, DyadicEdge, Element
from atlasforge.core.base import AtlasObject


@dataclass(frozen=True)
class PoleCoefficients:
    """
    Coefficient vector on the operator simplex.
    
    Represents a point α = (α_D, α_Ω, α_Σ, α_Ψ) with:
    - α_• ≥ 0
    - Σα_• = 1 (when normalized)
    """
    
    alpha_d: float
    alpha_omega: float
    alpha_sigma: float
    alpha_psi: float
    
    def __post_init__(self):
        # Allow negative for intermediate computations, but warn
        pass
    
    @classmethod
    def pure(cls, pole: Pole) -> 'PoleCoefficients':
        """Create a pure pole (vertex of simplex)."""
        coeffs = {Pole.D: 0, Pole.OMEGA: 0, Pole.SIGMA: 0, Pole.PSI: 0}
        coeffs[pole] = 1.0
        return cls(coeffs[Pole.D], coeffs[Pole.OMEGA], coeffs[Pole.SIGMA], coeffs[Pole.PSI])
    
    @classmethod
    def uniform(cls) -> 'PoleCoefficients':
        """Create uniform mixture (centroid of simplex)."""
        return cls(0.25, 0.25, 0.25, 0.25)
    
    @classmethod
    def from_array(cls, arr: Sequence[float]) -> 'PoleCoefficients':
        """Create from array [α_D, α_Ω, α_Σ, α_Ψ]."""
        if len(arr) != 4:
            raise ValueError("Expected 4 coefficients")
        return cls(arr[0], arr[1], arr[2], arr[3])
    
    @classmethod
    def dyadic(cls, pole1: Pole, pole2: Pole, theta: float = 0.5) -> 'PoleCoefficients':
        """
        Create a dyadic mixture on an edge.
        
        Args:
            pole1, pole2: The two poles forming the edge
            theta: Mixture parameter in [0, 1] (0 = pure pole1, 1 = pure pole2)
        """
        coeffs = {Pole.D: 0, Pole.OMEGA: 0, Pole.SIGMA: 0, Pole.PSI: 0}
        coeffs[pole1] = 1.0 - theta
        coeffs[pole2] = theta
        return cls(coeffs[Pole.D], coeffs[Pole.OMEGA], coeffs[Pole.SIGMA], coeffs[Pole.PSI])
    
    @property
    def as_tuple(self) -> Tuple[float, float, float, float]:
        return (self.alpha_d, self.alpha_omega, self.alpha_sigma, self.alpha_psi)
    
    @property
    def as_array(self) -> NDArray[np.float64]:
        return np.array([self.alpha_d, self.alpha_omega, self.alpha_sigma, self.alpha_psi])
    
    @property
    def total(self) -> float:
        """Sum of coefficients."""
        return self.alpha_d + self.alpha_omega + self.alpha_sigma + self.alpha_psi
    
    @property
    def is_normalized(self) -> bool:
        """Check if coefficients sum to 1."""
        return abs(self.total - 1.0) < 1e-10
    
    @property
    def is_valid(self) -> bool:
        """Check if all coefficients are non-negative."""
        return all(c >= -1e-10 for c in self.as_tuple)
    
    @property
    def on_simplex(self) -> bool:
        """Check if point lies on the simplex."""
        return self.is_valid and self.is_normalized
    
    def normalize(self) -> 'PoleCoefficients':
        """Normalize to lie on simplex (sum = 1)."""
        total = self.total
        if total == 0:
            return PoleCoefficients.uniform()
        return PoleCoefficients(
            self.alpha_d / total,
            self.alpha_omega / total,
            self.alpha_sigma / total,
            self.alpha_psi / total
        )
    
    def project_to_simplex(self) -> 'PoleCoefficients':
        """Project onto simplex (handles negative values)."""
        # Clip negative values to zero, then normalize
        clipped = [max(0, c) for c in self.as_tuple]
        total = sum(clipped)
        if total == 0:
            return PoleCoefficients.uniform()
        return PoleCoefficients(*(c / total for c in clipped))
    
    @property
    def dominant_pole(self) -> Pole:
        """Return the pole with highest coefficient."""
        poles = [Pole.D, Pole.OMEGA, Pole.SIGMA, Pole.PSI]
        coeffs = self.as_tuple
        return poles[np.argmax(coeffs)]
    
    @property
    def active_poles(self) -> List[Pole]:
        """Return poles with non-zero coefficient."""
        poles = [Pole.D, Pole.OMEGA, Pole.SIGMA, Pole.PSI]
        return [p for p, c in zip(poles, self.as_tuple) if c > 1e-10]
    
    @property
    def order(self) -> int:
        """
        Order of the simplex face:
        - 0: Vertex (single pole)
        - 1: Edge (two poles)
        - 2: Face (three poles)
        - 3: Interior (four poles)
        """
        return len(self.active_poles) - 1
    
    def get(self, pole: Pole) -> float:
        """Get coefficient for a specific pole."""
        mapping = {
            Pole.D: self.alpha_d,
            Pole.OMEGA: self.alpha_omega,
            Pole.SIGMA: self.alpha_sigma,
            Pole.PSI: self.alpha_psi
        }
        return mapping[pole]
    
    def with_pole(self, pole: Pole, value: float) -> 'PoleCoefficients':
        """Return new coefficients with one pole changed."""
        coeffs = list(self.as_tuple)
        idx = [Pole.D, Pole.OMEGA, Pole.SIGMA, Pole.PSI].index(pole)
        coeffs[idx] = value
        return PoleCoefficients(*coeffs)
    
    # Arithmetic operations
    
    def __add__(self, other: 'PoleCoefficients') -> 'PoleCoefficients':
        return PoleCoefficients(
            self.alpha_d + other.alpha_d,
            self.alpha_omega + other.alpha_omega,
            self.alpha_sigma + other.alpha_sigma,
            self.alpha_psi + other.alpha_psi
        )
    
    def __sub__(self, other: 'PoleCoefficients') -> 'PoleCoefficients':
        return PoleCoefficients(
            self.alpha_d - other.alpha_d,
            self.alpha_omega - other.alpha_omega,
            self.alpha_sigma - other.alpha_sigma,
            self.alpha_psi - other.alpha_psi
        )
    
    def __mul__(self, scalar: float) -> 'PoleCoefficients':
        return PoleCoefficients(
            self.alpha_d * scalar,
            self.alpha_omega * scalar,
            self.alpha_sigma * scalar,
            self.alpha_psi * scalar
        )
    
    def __rmul__(self, scalar: float) -> 'PoleCoefficients':
        return self * scalar
    
    def __truediv__(self, scalar: float) -> 'PoleCoefficients':
        return self * (1.0 / scalar)
    
    def dot(self, other: 'PoleCoefficients') -> float:
        """Inner product of coefficient vectors."""
        return sum(a * b for a, b in zip(self.as_tuple, other.as_tuple))
    
    def distance(self, other: 'PoleCoefficients') -> float:
        """Euclidean distance between coefficient points."""
        diff = self - other
        return math.sqrt(diff.dot(diff))
    
    # Interpolation
    
    def lerp(self, other: 'PoleCoefficients', t: float) -> 'PoleCoefficients':
        """Linear interpolation: self + t*(other - self)."""
        return self + t * (other - self)
    
    def midpoint(self, other: 'PoleCoefficients') -> 'PoleCoefficients':
        """Midpoint between two coefficient points."""
        return self.lerp(other, 0.5)
    
    # Barycentric coordinates
    
    @property
    def barycentric(self) -> Tuple[float, float, float, float]:
        """Barycentric coordinates (same as coefficients when normalized)."""
        if not self.is_normalized:
            return self.normalize().as_tuple
        return self.as_tuple


@dataclass
class DyadicInterface:
    """
    A dyadic interface (edge of the tetrahedron) between two poles.
    
    Each dyad is a one-parameter family:
        G_{AB}(θ) = (1-θ)A + θB,  θ ∈ [0,1]
    
    with swap symmetry θ ↦ (1-θ) and midpoint at θ=0.5.
    """
    
    edge: DyadicEdge
    
    @property
    def poles(self) -> Tuple[Pole, Pole]:
        """The two poles forming this edge."""
        return self.edge.poles
    
    @property
    def is_principal_axis(self) -> bool:
        """Whether this is a principal axis (D-Ω or Σ-Ψ)."""
        return self.edge.is_principal_axis
    
    @property
    def governs(self) -> str:
        """What interplay this dyad governs."""
        return self.edge.governs
    
    def coefficients(self, theta: float) -> PoleCoefficients:
        """
        Get simplex coordinates for parameter θ ∈ [0,1].
        
        θ=0: Pure first pole
        θ=1: Pure second pole
        θ=0.5: Midpoint (equal mixture)
        """
        pole1, pole2 = self.poles
        return PoleCoefficients.dyadic(pole1, pole2, theta)
    
    def midpoint(self) -> PoleCoefficients:
        """The midpoint of this edge (θ=0.5)."""
        return self.coefficients(0.5)
    
    def sample(self, n: int = 10) -> List[PoleCoefficients]:
        """Sample n points along this edge."""
        return [self.coefficients(i / (n - 1)) for i in range(n)]
    
    def contains(self, coeffs: PoleCoefficients) -> bool:
        """Check if coefficients lie on this edge."""
        pole1, pole2 = self.poles
        poles = [Pole.D, Pole.OMEGA, Pole.SIGMA, Pole.PSI]
        
        # Check that only these two poles have non-zero weight
        for p, c in zip(poles, coeffs.as_tuple):
            if p not in (pole1, pole2) and c > 1e-10:
                return False
        return True
    
    def parameter(self, coeffs: PoleCoefficients) -> Optional[float]:
        """
        Get the θ parameter for coefficients on this edge.
        
        Returns None if coefficients are not on this edge.
        """
        if not self.contains(coeffs):
            return None
        
        pole1, pole2 = self.poles
        c1 = coeffs.get(pole1)
        c2 = coeffs.get(pole2)
        
        if c1 + c2 == 0:
            return 0.5
        return c2 / (c1 + c2)


@dataclass
class SimplexFace:
    """
    A face (2-simplex) of the tetrahedron.
    
    Each face involves three poles, with the fourth being zero.
    """
    
    poles: Tuple[Pole, Pole, Pole]
    
    @classmethod
    def excluding(cls, excluded_pole: Pole) -> 'SimplexFace':
        """Create face by excluding one pole."""
        all_poles = [Pole.D, Pole.OMEGA, Pole.SIGMA, Pole.PSI]
        face_poles = tuple(p for p in all_poles if p != excluded_pole)
        return cls(face_poles)
    
    @property
    def excluded_pole(self) -> Pole:
        """The pole not on this face."""
        all_poles = {Pole.D, Pole.OMEGA, Pole.SIGMA, Pole.PSI}
        return list(all_poles - set(self.poles))[0]
    
    def contains(self, coeffs: PoleCoefficients) -> bool:
        """Check if coefficients lie on this face."""
        return coeffs.get(self.excluded_pole) < 1e-10
    
    def centroid(self) -> PoleCoefficients:
        """Centroid of this face."""
        result = {Pole.D: 0, Pole.OMEGA: 0, Pole.SIGMA: 0, Pole.PSI: 0}
        for p in self.poles:
            result[p] = 1/3
        return PoleCoefficients(result[Pole.D], result[Pole.OMEGA], 
                               result[Pole.SIGMA], result[Pole.PSI])
    
    def edges(self) -> List[DyadicInterface]:
        """Get the three edges of this face."""
        p1, p2, p3 = self.poles
        edges = []
        for pair in [(p1, p2), (p2, p3), (p1, p3)]:
            for edge in DyadicEdge:
                if set(edge.poles) == set(pair):
                    edges.append(DyadicInterface(edge))
                    break
        return edges


@dataclass
class OperatorSimplex:
    """
    The full operator simplex (3-simplex / tetrahedron).
    
    Provides navigation and analysis tools for the coefficient space.
    """
    
    @staticmethod
    def vertices() -> List[PoleCoefficients]:
        """Get all vertices (pure poles)."""
        return [PoleCoefficients.pure(p) for p in Pole]
    
    @staticmethod
    def edges() -> List[DyadicInterface]:
        """Get all 6 edges (dyadic interfaces)."""
        return [DyadicInterface(e) for e in DyadicEdge]
    
    @staticmethod
    def faces() -> List[SimplexFace]:
        """Get all 4 faces."""
        return [SimplexFace.excluding(p) for p in Pole]
    
    @staticmethod
    def centroid() -> PoleCoefficients:
        """Get the centroid of the simplex."""
        return PoleCoefficients.uniform()
    
    @staticmethod
    def random_point(rng: Optional[np.random.Generator] = None) -> PoleCoefficients:
        """Generate a random point uniformly on the simplex."""
        if rng is None:
            rng = np.random.default_rng()
        
        # Sample from Dirichlet(1,1,1,1)
        samples = rng.exponential(1.0, size=4)
        normalized = samples / samples.sum()
        return PoleCoefficients.from_array(normalized)
    
    @staticmethod
    def principal_axes() -> Tuple[DyadicInterface, DyadicInterface]:
        """
        Get the two principal axes:
        - Horizontal: D-Ω (dissipation-coherence)
        - Vertical: Σ-Ψ (noise-law)
        """
        return (
            DyadicInterface(DyadicEdge.D_OMEGA),
            DyadicInterface(DyadicEdge.SIGMA_PSI)
        )
    
    @staticmethod
    def diagonal_pairs() -> List[Tuple[DyadicInterface, DyadicInterface]]:
        """
        Get the two diagonal matchings (90° basis rotations).
        
        These give alternative decompositions of the tetrad.
        """
        # Diagonal pair 1: D-Σ and Ω-Ψ
        pair1 = (DyadicInterface(DyadicEdge.D_SIGMA), 
                 DyadicInterface(DyadicEdge.OMEGA_PSI))
        
        # Diagonal pair 2: D-Ψ and Ω-Σ
        pair2 = (DyadicInterface(DyadicEdge.D_PSI),
                 DyadicInterface(DyadicEdge.OMEGA_SIGMA))
        
        return [pair1, pair2]
    
    @staticmethod
    def project_to_edge(coeffs: PoleCoefficients, edge: DyadicInterface) -> PoleCoefficients:
        """Project coefficients onto an edge."""
        pole1, pole2 = edge.poles
        c1 = coeffs.get(pole1)
        c2 = coeffs.get(pole2)
        total = c1 + c2
        
        if total == 0:
            return edge.midpoint()
        
        theta = c2 / total
        return edge.coefficients(theta)
    
    @staticmethod
    def project_to_face(coeffs: PoleCoefficients, face: SimplexFace) -> PoleCoefficients:
        """Project coefficients onto a face."""
        result = {Pole.D: coeffs.alpha_d, Pole.OMEGA: coeffs.alpha_omega,
                 Pole.SIGMA: coeffs.alpha_sigma, Pole.PSI: coeffs.alpha_psi}
        
        # Zero out excluded pole
        result[face.excluded_pole] = 0
        
        # Normalize
        total = sum(result.values())
        if total == 0:
            return face.centroid()
        
        for p in result:
            result[p] /= total
        
        return PoleCoefficients(result[Pole.D], result[Pole.OMEGA],
                               result[Pole.SIGMA], result[Pole.PSI])
    
    @staticmethod
    def find_nearest_feature(coeffs: PoleCoefficients) -> Dict[str, Any]:
        """
        Find the nearest simplex feature (vertex, edge, face, or interior).
        
        Returns dict with 'type', 'feature', and 'distance'.
        """
        best = {'type': 'interior', 'feature': None, 'distance': float('inf')}
        
        # Check vertices
        for pole in Pole:
            vertex = PoleCoefficients.pure(pole)
            dist = coeffs.distance(vertex)
            if dist < best['distance']:
                best = {'type': 'vertex', 'feature': pole, 'distance': dist}
        
        # Check edges
        for edge in DyadicEdge:
            interface = DyadicInterface(edge)
            projected = OperatorSimplex.project_to_edge(coeffs, interface)
            dist = coeffs.distance(projected)
            if dist < best['distance']:
                best = {'type': 'edge', 'feature': edge, 'distance': dist}
        
        # Check faces
        for pole in Pole:
            face = SimplexFace.excluding(pole)
            projected = OperatorSimplex.project_to_face(coeffs, face)
            dist = coeffs.distance(projected)
            if dist < best['distance']:
                best = {'type': 'face', 'feature': face, 'distance': dist}
        
        return best
    
    @staticmethod
    def interpolate_path(
        start: PoleCoefficients,
        end: PoleCoefficients,
        n_steps: int = 10,
        geodesic: bool = False
    ) -> List[PoleCoefficients]:
        """
        Interpolate path between two simplex points.
        
        Args:
            start, end: Simplex points
            n_steps: Number of steps
            geodesic: If True, use geodesic (not yet implemented)
        
        Returns:
            List of intermediate points
        """
        path = []
        for i in range(n_steps):
            t = i / (n_steps - 1) if n_steps > 1 else 0
            point = start.lerp(end, t)
            if point.is_valid:
                path.append(point)
            else:
                path.append(point.project_to_simplex())
        return path
    
    @staticmethod
    def grid(resolution: int = 5) -> List[PoleCoefficients]:
        """
        Generate a grid of points on the simplex.
        
        Uses barycentric coordinates with given resolution.
        """
        points = []
        
        for i in range(resolution + 1):
            for j in range(resolution + 1 - i):
                for k in range(resolution + 1 - i - j):
                    l = resolution - i - j - k
                    point = PoleCoefficients(
                        i / resolution,
                        j / resolution,
                        k / resolution,
                        l / resolution
                    )
                    points.append(point)
        
        return points
    
    @staticmethod
    def analyze_mixture(coeffs: PoleCoefficients) -> Dict[str, Any]:
        """
        Analyze a coefficient mixture.
        
        Returns dict with analysis results:
        - dominant: Most active pole
        - order: Simplex order (0=vertex, 1=edge, 2=face, 3=interior)
        - balance: How balanced the mixture is (0=pure, 1=uniform)
        - active_poles: List of active poles
        - nearest_feature: Nearest simplex feature
        """
        active = coeffs.active_poles
        order = len(active) - 1
        
        # Compute balance (entropy-based)
        arr = np.array([max(c, 1e-10) for c in coeffs.as_tuple])
        arr = arr / arr.sum()
        entropy = -np.sum(arr * np.log(arr))
        max_entropy = np.log(4)  # Uniform distribution
        balance = entropy / max_entropy
        
        return {
            'dominant': coeffs.dominant_pole,
            'order': order,
            'balance': balance,
            'active_poles': active,
            'nearest_feature': OperatorSimplex.find_nearest_feature(coeffs),
            'is_pure': order == 0,
            'is_dyadic': order == 1,
            'is_triadic': order == 2,
            'is_full': order == 3,
        }
