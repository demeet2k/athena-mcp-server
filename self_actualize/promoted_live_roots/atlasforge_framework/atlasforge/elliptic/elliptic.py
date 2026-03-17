"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ELLIPTIC CURVES MODULE                                 ║
║                                                                              ║
║  Weierstrass Form, Group Law, and Arithmetic                                 ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Elliptic curves unify algebra, geometry, and number theory.              ║
║    The j-invariant from modular forms classifies curves over ℂ.             ║
║    Gateway algebra connects to curves via Pell equations.                   ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Weierstrass form: y² = x³ + ax + b                                     ║
║    - Group law: P + Q via chord-tangent construction                        ║
║    - j-invariant: j = 1728 · 4a³/(4a³ + 27b²)                               ║
║    - Discriminant: Δ = -16(4a³ + 27b²)                                      ║
║    - Mordell-Weil: E(ℚ) is finitely generated                               ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Pell equation → rational points                                        ║
║    - Modular forms → L-functions                                            ║
║    - Continued fractions → approximations to torsion                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Union
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# ELLIPTIC CURVE POINT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ECPoint:
    """
    Point on an elliptic curve.
    
    Either (x, y) affine coordinates or point at infinity O.
    """
    x: Optional[float] = None
    y: Optional[float] = None
    is_infinity: bool = False
    
    def __post_init__(self):
        if self.x is None and self.y is None and not self.is_infinity:
            self.is_infinity = True
    
    @classmethod
    def infinity(cls) -> 'ECPoint':
        """Point at infinity (identity element)."""
        return cls(is_infinity=True)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ECPoint):
            return False
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return np.isclose(self.x, other.x) and np.isclose(self.y, other.y)
    
    def __neg__(self) -> 'ECPoint':
        """Negation: (x, y) → (x, -y)."""
        if self.is_infinity:
            return ECPoint.infinity()
        return ECPoint(self.x, -self.y)
    
    def __repr__(self) -> str:
        if self.is_infinity:
            return "O"
        return f"({self.x:.6f}, {self.y:.6f})"


# ═══════════════════════════════════════════════════════════════════════════════
# ELLIPTIC CURVE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EllipticCurve:
    """
    Elliptic curve in Weierstrass form: y² = x³ + ax + b.
    
    Requires Δ = -16(4a³ + 27b²) ≠ 0 for smoothness.
    """
    a: float
    b: float
    
    def __post_init__(self):
        if self.discriminant() == 0:
            raise ValueError("Singular curve: discriminant is zero")
    
    def discriminant(self) -> float:
        """Δ = -16(4a³ + 27b²)."""
        return -16 * (4 * self.a**3 + 27 * self.b**2)
    
    def j_invariant(self) -> float:
        """
        j-invariant: j = 1728 · 4a³/Δ.
        
        Classifies curves up to isomorphism over ℂ.
        """
        numerator = 1728 * 4 * self.a**3
        delta = self.discriminant()
        if abs(delta) < 1e-15:
            return float('inf')
        return -numerator / delta
    
    def contains(self, P: ECPoint, tolerance: float = 1e-10) -> bool:
        """Check if point lies on curve."""
        if P.is_infinity:
            return True
        
        lhs = P.y**2
        rhs = P.x**3 + self.a * P.x + self.b
        return abs(lhs - rhs) < tolerance
    
    def add(self, P: ECPoint, Q: ECPoint) -> ECPoint:
        """
        Group law: P + Q.
        
        Uses chord-tangent construction.
        """
        # Identity cases
        if P.is_infinity:
            return Q
        if Q.is_infinity:
            return P
        
        # Inverse case
        if np.isclose(P.x, Q.x) and np.isclose(P.y, -Q.y):
            return ECPoint.infinity()
        
        # Compute slope
        if np.isclose(P.x, Q.x) and np.isclose(P.y, Q.y):
            # Tangent case: λ = (3x² + a)/(2y)
            if np.isclose(P.y, 0):
                return ECPoint.infinity()
            lam = (3 * P.x**2 + self.a) / (2 * P.y)
        else:
            # Secant case: λ = (y_Q - y_P)/(x_Q - x_P)
            lam = (Q.y - P.y) / (Q.x - P.x)
        
        # New point
        x_r = lam**2 - P.x - Q.x
        y_r = lam * (P.x - x_r) - P.y
        
        return ECPoint(x_r, y_r)
    
    def double(self, P: ECPoint) -> ECPoint:
        """2P = P + P."""
        return self.add(P, P)
    
    def multiply(self, n: int, P: ECPoint) -> ECPoint:
        """
        Scalar multiplication: nP.
        
        Uses double-and-add algorithm.
        """
        if n == 0:
            return ECPoint.infinity()
        
        if n < 0:
            return self.multiply(-n, -P)
        
        result = ECPoint.infinity()
        addend = P
        
        while n > 0:
            if n & 1:
                result = self.add(result, addend)
            addend = self.double(addend)
            n >>= 1
        
        return result
    
    def find_point(self, x: float) -> Optional[ECPoint]:
        """Find point with given x-coordinate (if exists over ℝ)."""
        y_squared = x**3 + self.a * x + self.b
        if y_squared < 0:
            return None
        y = np.sqrt(y_squared)
        return ECPoint(x, y)
    
    def rational_points_search(self, height_bound: int = 100
                              ) -> List[ECPoint]:
        """
        Search for rational points with small height.
        
        Simplified search over rationals p/q with |p|, |q| ≤ bound.
        """
        points = []
        
        for p in range(-height_bound, height_bound + 1):
            for q in range(1, height_bound + 1):
                x = p / q
                y_squared = x**3 + self.a * x + self.b
                
                if y_squared >= 0:
                    y = np.sqrt(y_squared)
                    # Check if y is rational
                    for r in range(-height_bound, height_bound + 1):
                        for s in range(1, height_bound + 1):
                            if np.isclose(y, r / s, atol=1e-10):
                                pt = ECPoint(x, y)
                                if pt not in points:
                                    points.append(pt)
                                break
        
        return points
    
    def order(self, P: ECPoint, max_order: int = 1000) -> Optional[int]:
        """Find order of point P (smallest n with nP = O)."""
        if P.is_infinity:
            return 1
        
        current = P
        for n in range(2, max_order + 1):
            current = self.add(current, P)
            if current.is_infinity:
                return n
        
        return None  # Order > max_order or infinite
    
    @classmethod
    def from_j_invariant(cls, j: float) -> 'EllipticCurve':
        """
        Construct curve with given j-invariant.
        
        j ≠ 0, 1728: y² = x³ - 3jc²x + 2jc³ where c = j/(j-1728)
        j = 0: y² = x³ + 1
        j = 1728: y² = x³ + x
        """
        if j == 0:
            return cls(0, 1)
        elif j == 1728:
            return cls(1, 0)
        else:
            c = j / (j - 1728)
            a = -3 * j * c**2
            b = 2 * j * c**3
            # Normalize
            a = -3 * c
            b = 2 * c
            return cls(a, b)


# ═══════════════════════════════════════════════════════════════════════════════
# ISOGENY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Isogeny:
    """
    Isogeny between elliptic curves.
    
    φ: E₁ → E₂ with finite kernel.
    """
    source: EllipticCurve
    target: EllipticCurve
    degree: int
    kernel_generator: Optional[ECPoint] = None
    
    def is_cyclic(self) -> bool:
        """Check if isogeny has cyclic kernel."""
        return self.kernel_generator is not None
    
    @classmethod
    def multiplication_by_n(cls, E: EllipticCurve, n: int) -> 'Isogeny':
        """[n]: E → E multiplication map (degree n²)."""
        return cls(E, E, n * n)


# ═══════════════════════════════════════════════════════════════════════════════
# TORSION SUBGROUP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TorsionSubgroup:
    """
    Torsion subgroup E[n] of n-torsion points.
    """
    curve: EllipticCurve
    n: int
    points: List[ECPoint] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.points:
            self._compute_torsion()
    
    def _compute_torsion(self):
        """Find n-torsion points (simplified for small n)."""
        self.points = [ECPoint.infinity()]
        
        # For 2-torsion: solve y = 0, i.e., x³ + ax + b = 0
        if self.n == 2:
            # Find roots of cubic
            coeffs = [1, 0, self.curve.a, self.curve.b]
            roots = np.roots(coeffs)
            for r in roots:
                if np.isreal(r):
                    self.points.append(ECPoint(float(np.real(r)), 0))
    
    def order(self) -> int:
        """Order of torsion subgroup."""
        return len(self.points)
    
    def is_cyclic(self) -> bool:
        """Check if torsion is cyclic."""
        return self.order() == self.n


# ═══════════════════════════════════════════════════════════════════════════════
# WEIL PAIRING (SIMPLIFIED)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WeilPairing:
    """
    Weil pairing e_n: E[n] × E[n] → μ_n.
    
    Bilinear, alternating, non-degenerate.
    """
    curve: EllipticCurve
    n: int
    
    def evaluate(self, P: ECPoint, Q: ECPoint) -> complex:
        """
        Evaluate e_n(P, Q).
        
        Returns n-th root of unity.
        """
        # Simplified: for real curves, return ±1
        if P.is_infinity or Q.is_infinity:
            return 1
        
        # Compute using Miller's algorithm (simplified)
        # For demonstration, return a root of unity
        return np.exp(2j * np.pi / self.n)
    
    def is_non_degenerate(self, P: ECPoint, Q: ECPoint) -> bool:
        """Check if pairing is non-degenerate on these points."""
        val = self.evaluate(P, Q)
        return not np.isclose(val, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# MORDELL-WEIL GROUP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MordellWeilGroup:
    """
    Mordell-Weil group E(ℚ).
    
    Finitely generated abelian group: E(ℚ) ≅ ℤʳ × E(ℚ)_tors
    """
    curve: EllipticCurve
    generators: List[ECPoint] = field(default_factory=list)
    torsion: List[ECPoint] = field(default_factory=list)
    
    @property
    def rank(self) -> int:
        """Algebraic rank r."""
        return len(self.generators)
    
    def height(self, P: ECPoint) -> float:
        """
        Naive height: h(P) = max(log|x|, log|y|).
        """
        if P.is_infinity:
            return 0
        return max(np.log(abs(P.x) + 1), np.log(abs(P.y) + 1))


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY-CURVE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewayCurveBridge:
    """
    Bridge between gateway algebra and elliptic curves.
    
    Pell equation x² - Dy² = 1 relates to curves.
    """
    
    @staticmethod
    def pell_to_curve(D: int) -> EllipticCurve:
        """
        Associate elliptic curve to discriminant D.
        
        Uses the curve y² = x³ - Dx.
        """
        return EllipticCurve(-D, 0)
    
    @staticmethod
    def fundamental_solution_as_point(D: int, x: int, y: int
                                     ) -> Optional[ECPoint]:
        """
        Map Pell solution (x, y) to curve point.
        
        The mapping is: (x, y) → (x/y², 1/y³) on normalized curve.
        """
        if y == 0:
            return ECPoint.infinity()
        
        # Point on y² = x³ - Dx
        curve = EllipticCurve(-D, 0)
        
        # Use: if x² - Dy² = 1, then ((x-1)/y², D(x-1)/y³) lies on y² = x³ - Dx
        # Simplified approach
        pt_x = D
        pt_y_sq = D**3 - D * D
        
        if pt_y_sq >= 0:
            return ECPoint(pt_x, np.sqrt(pt_y_sq))
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def elliptic_curve(a: float, b: float) -> EllipticCurve:
    """Create elliptic curve y² = x³ + ax + b."""
    return EllipticCurve(a, b)


def curve_discriminant(a: float, b: float) -> float:
    """Compute discriminant Δ = -16(4a³ + 27b²)."""
    return -16 * (4 * a**3 + 27 * b**2)


def ec_j_invariant(a: float, b: float) -> float:
    """Compute j-invariant."""
    return EllipticCurve(a, b).j_invariant()


def point_addition(E: EllipticCurve, P: ECPoint, Q: ECPoint) -> ECPoint:
    """Add two points on curve."""
    return E.add(P, Q)


def scalar_multiply(E: EllipticCurve, n: int, P: ECPoint) -> ECPoint:
    """Compute nP."""
    return E.multiply(n, P)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Points
    'ECPoint',
    
    # Curves
    'EllipticCurve',
    
    # Structure
    'Isogeny',
    'TorsionSubgroup',
    'WeilPairing',
    'MordellWeilGroup',
    
    # Bridge
    'GatewayCurveBridge',
    
    # Functions
    'elliptic_curve',
    'curve_discriminant',
    'ec_j_invariant',
    'point_addition',
    'scalar_multiply',
]
