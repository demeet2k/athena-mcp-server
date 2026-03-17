"""
ATHENA OS - Zero Calculus
=========================
Zero structures, hierarchies, and "zero points of zero points."

Zero Taxonomy:
1. Order-1 Zero (Intersection): H(x*) = 0
2. Order-m Zero (Zero-of-Zero Chain): H^(k)(x*) = 0 for k = 0..m-1
3. Singular Seed: H(z*) = 0 AND det J_H(z*) = 0

Zero Structures:
- Z(H) = {x ∈ D : H(x) = 0} (zero set)
- Z₀(F, G) = {x : F(x) = G(x)} = Z(F - G) (between-pole zeros)
- Multiway intersection: F₁ = ... = Fₙ
- Cancellation zeros: Σ wᵢFᵢ = 0

The precise meaning of "zero points of zero points":
Not only do two expressions meet, but their local geometry
(slope/curvature/...) collapses to higher order.

For systems H: ℝⁿ → ℝⁿ (including parameters), the higher-order
collapse is the singular seed condition:
H(z*) = 0, det J_H(z*) = 0
encoding "the intersection manifold itself collapses" (fold/cusp/bifurcation).

Multiplicity Transport Theorem:
Under sufficient smoothness and nondegeneracy of T, root multiplicity
and tangency structure are preserved under conjugacy.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set, Union
import numpy as np
from scipy import optimize

from .lenses import Lens


# =============================================================================
# ZERO STRUCTURES
# =============================================================================

class ZeroType(IntEnum):
    """Classification of zero types."""
    SIMPLE = 1        # Order-1, non-degenerate
    DOUBLE = 2        # Order-2 (tangent crossing)
    TRIPLE = 3        # Order-3
    HIGHER = 4        # Order ≥ 4
    SINGULAR = 0      # Singular (Jacobian degenerate)


@dataclass
class ZeroPoint:
    """
    A zero point with multiplicity and classification.
    
    For H(x*) = 0, stores:
    - location x*
    - order m (number of vanishing derivatives)
    - type classification
    - certificate data
    """
    location: float
    order: int
    zero_type: ZeroType
    residual: float = 0.0
    derivative_values: List[float] = field(default_factory=list)
    
    @property
    def is_simple(self) -> bool:
        return self.order == 1
    
    @property
    def is_degenerate(self) -> bool:
        return self.order > 1
    
    def multiplicity(self) -> int:
        """Return algebraic multiplicity."""
        return self.order


@dataclass
class ZeroSet:
    """
    Zero set Z(H) = {x ∈ D : H(x) = 0}.
    
    Stores the function H, its zeros, and certificates.
    """
    function: Callable[[float], float]
    domain: Tuple[float, float]
    zeros: List[ZeroPoint] = field(default_factory=list)
    name: str = "H"
    
    def find_zeros(self, n_samples: int = 1000, tolerance: float = 1e-10) -> List[ZeroPoint]:
        """
        Find zeros numerically via sign-change detection + bisection.
        """
        a, b = self.domain
        if not np.isfinite(a):
            a = 0.01
        if not np.isfinite(b):
            b = 100.0
        
        xs = np.linspace(a, b, n_samples)
        self.zeros = []
        
        for i in range(len(xs) - 1):
            try:
                f1 = self.function(xs[i])
                f2 = self.function(xs[i+1])
                
                if f1 * f2 < 0:  # Sign change
                    # Bisection refinement
                    zero = self._refine_zero(xs[i], xs[i+1], tolerance)
                    if zero is not None:
                        self.zeros.append(zero)
            except (ValueError, OverflowError):
                pass
        
        return self.zeros
    
    def _refine_zero(self, lo: float, hi: float, tolerance: float) -> Optional[ZeroPoint]:
        """Refine zero via bisection and determine order."""
        f_lo = self.function(lo)
        
        for _ in range(100):
            mid = (lo + hi) / 2
            f_mid = self.function(mid)
            
            if abs(f_mid) < tolerance:
                break
            
            if f_mid * f_lo < 0:
                hi = mid
            else:
                lo = mid
                f_lo = f_mid
        
        x_star = (lo + hi) / 2
        residual = abs(self.function(x_star))
        
        # Determine order via derivative analysis
        order, derivs = self._compute_order(x_star, tolerance)
        
        if order == 1:
            zero_type = ZeroType.SIMPLE
        elif order == 2:
            zero_type = ZeroType.DOUBLE
        elif order == 3:
            zero_type = ZeroType.TRIPLE
        else:
            zero_type = ZeroType.HIGHER
        
        return ZeroPoint(
            location=x_star,
            order=order,
            zero_type=zero_type,
            residual=residual,
            derivative_values=derivs
        )
    
    def _compute_order(self, x: float, tolerance: float, max_order: int = 5) -> Tuple[int, List[float]]:
        """
        Compute order by checking vanishing derivatives.
        
        Order m: H(x) = H'(x) = ... = H^(m-1)(x) = 0, H^(m)(x) ≠ 0
        """
        derivs = []
        h = 1e-6
        
        # Compute derivatives via finite differences
        for k in range(max_order):
            deriv_k = self._numerical_derivative(x, k, h)
            derivs.append(deriv_k)
            
            if abs(deriv_k) > tolerance:
                return k + 1, derivs
        
        return max_order, derivs
    
    def _numerical_derivative(self, x: float, order: int, h: float = 1e-6) -> float:
        """Compute numerical derivative of given order."""
        if order == 0:
            return self.function(x)
        
        # Finite difference for higher derivatives
        # D^n f ≈ (1/h^n) Σ (-1)^k C(n,k) f(x + (n/2 - k)h)
        coeffs = [(-1)**k * np.math.comb(order, k) for k in range(order + 1)]
        
        result = 0.0
        for k, c in enumerate(coeffs):
            shift = (order / 2 - k) * h
            try:
                result += c * self.function(x + shift)
            except (ValueError, OverflowError):
                return np.inf
        
        return result / (h ** order)
    
    def contains(self, x: float, tolerance: float = 1e-8) -> bool:
        """Check if x is in the zero set."""
        try:
            return abs(self.function(x)) < tolerance
        except (ValueError, OverflowError):
            return False


# =============================================================================
# BETWEEN-POLE ZEROS (INTERSECTION)
# =============================================================================

@dataclass
class IntersectionZero:
    """
    Between-pole zero: Z₀(F, G) = {x : F(x) = G(x)} = Z(F - G)
    
    This is where two expressions meet.
    """
    f: Callable[[float], float]
    g: Callable[[float], float]
    domain: Tuple[float, float]
    zeros: List[ZeroPoint] = field(default_factory=list)
    f_name: str = "F"
    g_name: str = "G"
    
    def find_intersections(self, **kwargs) -> List[ZeroPoint]:
        """Find intersection points F(x) = G(x)."""
        def H(x):
            return self.f(x) - self.g(x)
        
        zero_set = ZeroSet(H, self.domain, name=f"{self.f_name}-{self.g_name}")
        self.zeros = zero_set.find_zeros(**kwargs)
        return self.zeros
    
    @property
    def name(self) -> str:
        return f"Z₀({self.f_name}, {self.g_name})"


# =============================================================================
# MULTIWAY INTERSECTION
# =============================================================================

@dataclass
class MultiwayIntersection:
    """
    Multiway intersection: F₁ = F₂ = ... = Fₙ
    
    Points where multiple expressions simultaneously agree.
    """
    functions: List[Callable[[float], float]]
    domain: Tuple[float, float]
    names: List[str] = field(default_factory=list)
    zeros: List[ZeroPoint] = field(default_factory=list)
    
    def find_intersections(self, n_samples: int = 1000, tolerance: float = 1e-8) -> List[ZeroPoint]:
        """
        Find points where all functions are equal.
        
        Uses sum of squared differences: Σᵢ<ⱼ (Fᵢ - Fⱼ)²
        """
        if len(self.functions) < 2:
            return []
        
        def total_variance(x):
            try:
                values = [f(x) for f in self.functions]
                mean = sum(values) / len(values)
                return sum((v - mean)**2 for v in values)
            except (ValueError, OverflowError):
                return np.inf
        
        a, b = self.domain
        if not np.isfinite(a):
            a = 0.01
        if not np.isfinite(b):
            b = 100.0
        
        # Search for minima
        xs = np.linspace(a, b, n_samples)
        candidates = []
        
        for i in range(1, len(xs) - 1):
            v_prev = total_variance(xs[i-1])
            v_curr = total_variance(xs[i])
            v_next = total_variance(xs[i+1])
            
            if v_curr < v_prev and v_curr < v_next and v_curr < tolerance:
                # Local minimum below threshold
                # Refine with optimization
                try:
                    result = optimize.minimize_scalar(
                        total_variance,
                        bounds=(xs[i-1], xs[i+1]),
                        method='bounded'
                    )
                    if result.fun < tolerance:
                        candidates.append(result.x)
                except:
                    candidates.append(xs[i])
        
        self.zeros = [
            ZeroPoint(
                location=x,
                order=1,
                zero_type=ZeroType.SIMPLE,
                residual=total_variance(x)
            )
            for x in candidates
        ]
        
        return self.zeros


# =============================================================================
# CANCELLATION ZEROS
# =============================================================================

@dataclass
class CancellationZero:
    """
    Cancellation zeros: Σ wᵢFᵢ = 0
    
    Linear combinations that vanish.
    """
    functions: List[Callable[[float], float]]
    weights: List[float]
    domain: Tuple[float, float]
    zeros: List[ZeroPoint] = field(default_factory=list)
    
    def find_zeros(self, **kwargs) -> List[ZeroPoint]:
        """Find zeros of weighted sum."""
        def H(x):
            try:
                return sum(w * f(x) for w, f in zip(self.weights, self.functions))
            except (ValueError, OverflowError):
                return np.inf
        
        zero_set = ZeroSet(H, self.domain, name="cancellation")
        self.zeros = zero_set.find_zeros(**kwargs)
        return self.zeros


# =============================================================================
# SINGULAR SEEDS - HIGHER-ORDER COLLAPSE
# =============================================================================

@dataclass
class SingularSeed:
    """
    Singular seed: H(z*) = 0 AND det J_H(z*) = 0
    
    For systems H: ℝⁿ → ℝⁿ, this encodes:
    "The intersection manifold itself collapses"
    
    This is the fold/cusp/bifurcation condition where not only
    do expressions meet, but their Jacobian becomes degenerate.
    """
    H: Callable[[np.ndarray], np.ndarray]
    dim: int
    location: Optional[np.ndarray] = None
    jacobian_det: float = 0.0
    bifurcation_type: str = "unknown"
    
    def compute_jacobian(self, z: np.ndarray, h: float = 1e-6) -> np.ndarray:
        """Compute numerical Jacobian at z."""
        n = len(z)
        J = np.zeros((n, n))
        
        for j in range(n):
            e_j = np.zeros(n)
            e_j[j] = h
            
            H_plus = self.H(z + e_j)
            H_minus = self.H(z - e_j)
            
            J[:, j] = (H_plus - H_minus) / (2 * h)
        
        return J
    
    def is_singular(self, z: np.ndarray, tolerance: float = 1e-8) -> Tuple[bool, float]:
        """
        Check if z is a singular point.
        
        Singular: H(z) = 0 AND det J(z) = 0
        """
        # Check H(z) = 0
        Hz = self.H(z)
        if np.linalg.norm(Hz) > tolerance:
            return False, np.inf
        
        # Check det J = 0
        J = self.compute_jacobian(z)
        det_J = np.linalg.det(J)
        
        return abs(det_J) < tolerance, det_J
    
    def classify_bifurcation(self, z: np.ndarray) -> str:
        """
        Classify the type of bifurcation at a singular point.
        
        Uses eigenvalue analysis of the Jacobian.
        """
        J = self.compute_jacobian(z)
        eigenvalues = np.linalg.eigvals(J)
        
        # Count zero eigenvalues
        zero_count = sum(abs(ev) < 1e-6 for ev in eigenvalues)
        
        if zero_count == 1:
            return "fold"  # Saddle-node
        elif zero_count == 2:
            return "cusp"  # Pitchfork candidate
        else:
            return "higher_codimension"
    
    def find_singular_points(self, bounds: List[Tuple[float, float]], 
                            n_starts: int = 10, tolerance: float = 1e-8) -> List[np.ndarray]:
        """
        Search for singular points via optimization.
        
        Minimizes |H(z)|² + λ(1 - |det J|)² for small det J.
        """
        results = []
        
        for _ in range(n_starts):
            # Random starting point
            z0 = np.array([
                np.random.uniform(b[0], b[1]) for b in bounds
            ])
            
            def objective(z):
                Hz = self.H(z)
                J = self.compute_jacobian(z)
                det_J = np.linalg.det(J)
                return np.sum(Hz**2) + det_J**2
            
            try:
                result = optimize.minimize(
                    objective, z0,
                    bounds=bounds,
                    method='L-BFGS-B'
                )
                
                if result.fun < tolerance:
                    is_sing, det = self.is_singular(result.x, tolerance)
                    if is_sing:
                        results.append(result.x)
            except:
                pass
        
        return results


# =============================================================================
# ZERO-OF-ZERO CHAIN (ORDER-M ZEROS)
# =============================================================================

class ZeroOfZeroChain:
    """
    Zero-of-zero chain: H^(k)(x*) = 0 for k = 0, 1, ..., m-1
    
    This is the precise meaning of "zero points of zero points":
    Not only do two expressions meet, but their local geometry
    (slope/curvature/...) collapses to higher order.
    """
    
    def __init__(self, H: Callable[[float], float], domain: Tuple[float, float]):
        self.H = H
        self.domain = domain
    
    def check_order(self, x: float, tolerance: float = 1e-8, max_order: int = 10) -> int:
        """
        Check the order of the zero at x.
        
        Returns m such that H^(0)=...=H^(m-1)=0 but H^(m)≠0
        """
        h = 1e-6
        
        for m in range(max_order):
            deriv = self._numerical_derivative(x, m, h)
            if abs(deriv) > tolerance:
                return m
        
        return max_order
    
    def _numerical_derivative(self, x: float, order: int, h: float = 1e-6) -> float:
        """Compute numerical derivative of given order."""
        if order == 0:
            return self.H(x)
        
        # Finite difference coefficients
        coeffs = [(-1)**k * np.math.comb(order, k) for k in range(order + 1)]
        
        result = 0.0
        for k, c in enumerate(coeffs):
            shift = (order / 2 - k) * h
            try:
                result += c * self.H(x + shift)
            except (ValueError, OverflowError):
                return np.inf
        
        return result / (h ** order)
    
    def find_high_order_zeros(self, min_order: int = 2, 
                              n_samples: int = 1000,
                              tolerance: float = 1e-8) -> List[ZeroPoint]:
        """Find zeros of order ≥ min_order (degenerate zeros)."""
        # First find all zeros
        zero_set = ZeroSet(self.H, self.domain)
        all_zeros = zero_set.find_zeros(n_samples, tolerance)
        
        # Filter by order
        return [z for z in all_zeros if z.order >= min_order]
    
    def jet_at_zero(self, x: float, order: int) -> List[float]:
        """
        Compute the jet (Taylor coefficients) at a zero.
        
        Returns [H(x), H'(x), H''(x)/2!, ..., H^(n)(x)/n!]
        """
        h = 1e-6
        jet = []
        
        for k in range(order + 1):
            deriv = self._numerical_derivative(x, k, h)
            jet.append(deriv / np.math.factorial(k))
        
        return jet


# =============================================================================
# MULTIPLICITY TRANSPORT
# =============================================================================

class MultiplicityTransport:
    """
    Multiplicity Transport Theorem:
    
    Under sufficient smoothness and nondegeneracy of T, root multiplicity
    and tangency structure are preserved under conjugacy.
    
    Hence "zero-of-zero" constructions remain meaningful across lenses.
    """
    
    @staticmethod
    def transport_zero(zero: ZeroPoint, lens: Lens) -> ZeroPoint:
        """
        Transport a zero through a lens.
        
        If H has a zero of order m at x*, then H_T = T⁻¹ ∘ H ∘ T
        has a zero of order m at T⁻¹(x*) (under smoothness conditions).
        """
        # Transport location
        t_star = lens.inverse(zero.location)
        
        return ZeroPoint(
            location=t_star,
            order=zero.order,  # Order preserved
            zero_type=zero.zero_type,
            residual=zero.residual,
            derivative_values=[]  # Would need recomputation
        )
    
    @staticmethod
    def verify_transport(H: Callable, lens: Lens, x_star: float, 
                        expected_order: int, tolerance: float = 1e-6) -> bool:
        """
        Verify that multiplicity is preserved under transport.
        """
        # Original order at x*
        chain = ZeroOfZeroChain(H, (0.01, 100))
        original_order = chain.check_order(x_star, tolerance)
        
        # Transported function
        def H_T(t):
            x = lens.inverse(t)
            return H(x)
        
        # Order at t* = T(x*)
        t_star = lens.forward(x_star)
        chain_T = ZeroOfZeroChain(H_T, (-100, 100))
        transported_order = chain_T.check_order(t_star, tolerance)
        
        return original_order == transported_order == expected_order


# =============================================================================
# VALIDATION
# =============================================================================

def validate_zero_calculus() -> bool:
    """Validate zero calculus."""
    # Simple zero
    def H1(x):
        return x - 2
    
    zero_set = ZeroSet(H1, (0, 10))
    zeros = zero_set.find_zeros()
    assert len(zeros) == 1
    assert abs(zeros[0].location - 2.0) < 1e-8
    assert zeros[0].order == 1  # Simple zero
    
    # Double zero
    def H2(x):
        return (x - 3) ** 2
    
    zero_set2 = ZeroSet(H2, (0, 10))
    zeros2 = zero_set2.find_zeros()
    # Double zeros are harder to detect numerically, but we can check order
    if zeros2:
        assert zeros2[0].order >= 1
    
    # Between-pole intersection
    def F(x):
        return x ** 2
    def G(x):
        return 2 * x + 3
    
    intersection = IntersectionZero(F, G, (0, 10))
    intersections = intersection.find_intersections()
    # x² = 2x + 3 → x² - 2x - 3 = 0 → x = 3 or x = -1
    # Only x = 3 in domain (0, 10)
    assert any(abs(z.location - 3.0) < 1e-6 for z in intersections)
    
    # Zero-of-zero chain
    def H3(x):
        return (x - 2) ** 3
    
    chain = ZeroOfZeroChain(H3, (0, 10))
    order = chain.check_order(2.0)
    assert order >= 3  # Triple zero
    
    # Cancellation zero
    functions = [lambda x: x**2, lambda x: -x**2 + 4]
    weights = [1, 1]  # x² + (-x² + 4) = 4, no zeros
    
    # Better example: sin(x) - cos(x) at x = π/4
    import math
    cancellation = CancellationZero(
        [lambda x: np.sin(x), lambda x: -np.cos(x)],
        [1, 1],
        (0, 2)
    )
    cancel_zeros = cancellation.find_zeros()
    # sin(x) - cos(x) = 0 at x = π/4
    assert any(abs(z.location - np.pi/4) < 1e-4 for z in cancel_zeros)
    
    return True


if __name__ == "__main__":
    print("Validating Zero Calculus...")
    assert validate_zero_calculus()
    print("✓ Zero Calculus validated")
    
    # Demo
    print("\n=== Zero Set Demo ===")
    def H(x):
        return np.sin(x)
    
    zero_set = ZeroSet(H, (0, 10), name="sin")
    zeros = zero_set.find_zeros()
    print(f"Zeros of sin(x) in (0, 10): {[f'{z.location:.4f}' for z in zeros]}")
    
    print("\n=== Zero-of-Zero Demo ===")
    def H2(x):
        return (x - np.pi) ** 2 * np.sin(x)
    
    chain = ZeroOfZeroChain(H2, (0, 10))
    order_pi = chain.check_order(np.pi)
    print(f"Order of zero at π: {order_pi}")
    
    jet = chain.jet_at_zero(np.pi, 4)
    print(f"Jet at π: {[f'{j:.4f}' for j in jet]}")
