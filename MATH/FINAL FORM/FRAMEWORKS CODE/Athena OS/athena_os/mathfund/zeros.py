"""
ATHENA OS - Zero Hierarchy and Hardening
========================================
Constants are forged as ZERO OBJECTS (solutions to constraint systems).

The central hierarchy:
1. Zero Point: H(x*) = 0
2. Zero-of-Zero (hardening): H^(k)(x*) = 0 for k = 0, ..., m-1
3. Zero of Intersection (singular seed): H(z*) = 0 AND det J_H(z*) = 0

This yields HYBRID CONSTANTS that encode simultaneous properties
of log, e, φ, sin, cos, power/radical by enforcing each property
in its natural lens and transporting constraints across lenses.

Zero Sets Transport Cleanly:
Under bijective lenses, lattice zeros in t-space become
structured families in x-space via T⁻¹.
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
import numpy as np
import math

from .lenses import (
    Lens, Domain, LensRegistry,
    create_ln_lens, create_phi_log_lens,
    PHI, E, PI, TAU, LN_PHI
)


# =============================================================================
# ZERO TYPES
# =============================================================================

class ZeroType(Enum):
    """Classification of zeros."""
    SIMPLE = auto()          # H(x*) = 0, H'(x*) ≠ 0
    MULTIPLE = auto()        # H(x*) = 0, H'(x*) = 0 (multiplicity > 1)
    HARDENED = auto()        # H^(k)(x*) = 0 for k = 0, ..., m-1
    INTERSECTION = auto()    # Multiple constraints: H_i(x*) = 0
    SINGULAR = auto()        # Intersection + det J = 0
    CANCELLATION = auto()    # Sum of terms cancels: Σ w_i F_i = 0
    CYCLE = auto()           # f^n(x*) = x* (periodic point)


# =============================================================================
# ZERO POINT
# =============================================================================

@dataclass
class ZeroPoint:
    """
    A zero point: a solution to H(x) = 0.
    
    The fundamental constant-forging object.
    """
    
    # The value
    value: float
    
    # The defining constraint
    constraint_name: str
    constraint_fn: Callable[[float], float]
    
    # Zero type
    zero_type: ZeroType = ZeroType.SIMPLE
    
    # Multiplicity (order of vanishing)
    multiplicity: int = 1
    
    # Verification tolerance
    tolerance: float = 1e-12
    
    # Certificate (proof of validity)
    certificate: Optional[str] = None
    
    def verify(self) -> bool:
        """Verify that this is indeed a zero."""
        residual = abs(self.constraint_fn(self.value))
        return residual < self.tolerance
    
    def residual(self) -> float:
        """Compute the residual |H(x*)|."""
        return abs(self.constraint_fn(self.value))
    
    @classmethod
    def find(cls, constraint: Callable[[float], float],
            initial: float, name: str = "H",
            tol: float = 1e-12, max_iter: int = 100) -> Optional['ZeroPoint']:
        """
        Find a zero using Newton's method.
        """
        x = initial
        h = 1e-8
        
        for _ in range(max_iter):
            fx = constraint(x)
            if abs(fx) < tol:
                return cls(
                    value=x,
                    constraint_name=name,
                    constraint_fn=constraint,
                    tolerance=tol
                )
            
            # Numerical derivative
            fpx = (constraint(x + h) - constraint(x - h)) / (2 * h)
            if abs(fpx) < 1e-15:
                break
            
            x = x - fx / fpx
        
        return None


# =============================================================================
# ZERO HIERARCHY
# =============================================================================

@dataclass
class ZeroHierarchy:
    """
    The hierarchy of zero structures.
    
    Level 0: H(x*) = 0 (simple zero)
    Level 1: H(x*) = H'(x*) = 0 (double zero)
    Level m: H^(k)(x*) = 0 for k = 0, ..., m-1 (m-fold zero)
    """
    
    # The defining function
    H: Callable[[float], float]
    
    # Numerical step for derivatives
    h: float = 1e-8
    
    def derivative(self, x: float, order: int = 1) -> float:
        """Compute numerical derivative of order k."""
        if order == 0:
            return self.H(x)
        elif order == 1:
            return (self.H(x + self.h) - self.H(x - self.h)) / (2 * self.h)
        else:
            # Higher order: recursive central difference
            def Hprev(t):
                return (self.H(t + self.h) - self.H(t - self.h)) / (2 * self.h)
            
            sub = ZeroHierarchy(Hprev, self.h)
            return sub.derivative(x, order - 1)
    
    def check_hardening(self, x: float, max_order: int = 5) -> int:
        """
        Check hardening level: how many derivatives vanish?
        
        Returns m such that H^(k)(x) ≈ 0 for k = 0, ..., m-1
        """
        tol = 1e-8
        
        for k in range(max_order + 1):
            deriv = self.derivative(x, k)
            if abs(deriv) > tol:
                return k
        
        return max_order + 1
    
    def find_hardened_zero(self, initial: float, 
                          target_level: int = 2) -> Optional[ZeroPoint]:
        """
        Find a zero with specified hardening level.
        
        This requires solving a system of equations:
        H(x) = 0, H'(x) = 0, ..., H^(m-1)(x) = 0
        
        For level 2, we seek x where both H and H' vanish.
        """
        # For hardened zeros, we need to find where derivatives also vanish
        # This is typically done by solving a coupled system
        
        # Simple approach: find where H(x) = 0 and check hardening
        x = initial
        h = 1e-8
        tol = 1e-10
        
        for _ in range(100):
            fx = self.H(x)
            if abs(fx) < tol:
                level = self.check_hardening(x)
                if level >= target_level:
                    return ZeroPoint(
                        value=x,
                        constraint_name="H_hardened",
                        constraint_fn=self.H,
                        zero_type=ZeroType.HARDENED,
                        multiplicity=level
                    )
            
            # Newton step
            fpx = self.derivative(x, 1)
            if abs(fpx) < 1e-15:
                break
            x = x - fx / fpx
        
        return None


# =============================================================================
# INTERSECTION ZEROS
# =============================================================================

@dataclass
class IntersectionZero:
    """
    A zero of intersection: where multiple constraints meet.
    
    Z_0(F, G) = {x : F(x) = G(x)} = Z(F - G)
    
    For systems H(z) = 0 (vector equation), additionally
    det J_H(z*) = 0 makes it a SINGULAR SEED.
    """
    
    # The constraints
    constraints: List[Callable[[float], float]]
    constraint_names: List[str]
    
    # The intersection point
    value: float = 0.0
    
    # Is it singular? (det J = 0)
    is_singular: bool = False
    
    # Jacobian determinant (if computed)
    jacobian_det: float = 0.0
    
    def combined_constraint(self, x: float) -> float:
        """
        Combine constraints: sum of squares.
        
        H_combined(x) = Σ H_i(x)²
        """
        return sum(h(x)**2 for h in self.constraints)
    
    def find_intersection(self, initial: float, 
                         tol: float = 1e-10) -> bool:
        """
        Find intersection point using optimization.
        """
        x = initial
        h = 1e-8
        
        for _ in range(100):
            # Combined constraint
            fx = self.combined_constraint(x)
            if fx < tol:
                self.value = x
                return True
            
            # Gradient of sum of squares
            grad = 0.0
            for constraint in self.constraints:
                hx = constraint(x)
                # Numerical derivative
                hp = (constraint(x + h) - constraint(x - h)) / (2 * h)
                grad += 2 * hx * hp
            
            if abs(grad) < 1e-15:
                break
            
            x = x - 0.1 * fx / abs(grad)  # Damped step
        
        return False
    
    def verify(self, tol: float = 1e-8) -> bool:
        """Verify all constraints are satisfied."""
        return all(abs(h(self.value)) < tol for h in self.constraints)


# =============================================================================
# ZERO SETS
# =============================================================================

@dataclass
class ZeroSet:
    """
    A zero set: Z(H) = {x ∈ D : H(x) = 0}.
    
    Zero sets transport cleanly under bijective lenses.
    """
    
    # The defining function
    H: Callable[[float], float]
    name: str
    
    # Known zeros
    zeros: List[ZeroPoint] = field(default_factory=list)
    
    # The lens (if transported)
    lens: Optional[Lens] = None
    
    def add_zero(self, x: float, verify: bool = True) -> bool:
        """Add a zero to the set."""
        if verify and abs(self.H(x)) > 1e-10:
            return False
        
        zero = ZeroPoint(
            value=x,
            constraint_name=self.name,
            constraint_fn=self.H
        )
        self.zeros.append(zero)
        return True
    
    def find_zeros_in_interval(self, a: float, b: float, 
                               n_samples: int = 100) -> int:
        """
        Search for zeros in [a, b] by sign changes.
        """
        found = 0
        xs = np.linspace(a, b, n_samples)
        
        for i in range(len(xs) - 1):
            try:
                fa = self.H(xs[i])
                fb = self.H(xs[i + 1])
                
                if fa * fb < 0:  # Sign change
                    # Bisection to refine
                    lo, hi = xs[i], xs[i + 1]
                    for _ in range(50):
                        mid = (lo + hi) / 2
                        fm = self.H(mid)
                        if abs(fm) < 1e-12:
                            break
                        if fa * fm < 0:
                            hi = mid
                        else:
                            lo, fa = mid, fm
                    
                    if self.add_zero(mid):
                        found += 1
            except (ValueError, OverflowError):
                continue
        
        return found
    
    def transport(self, lens: Lens) -> 'ZeroSet':
        """
        Transport zero set through a lens.
        
        Z_T = {T⁻¹(t) : t ∈ Z}
        
        If Z is a lattice in t-space, Z_T is a structured
        family in x-space.
        """
        def H_transported(x: float) -> float:
            t = lens(x)
            return self.H(t)
        
        transported_set = ZeroSet(
            H=H_transported,
            name=f"{self.name}_T({lens.name})",
            lens=lens
        )
        
        # Transport known zeros
        for zero in self.zeros:
            try:
                x = lens.inv(zero.value)
                transported_set.add_zero(x)
            except (ValueError, OverflowError):
                continue
        
        return transported_set


# =============================================================================
# LATTICE ZEROS
# =============================================================================

@dataclass
class LatticeZero:
    """
    Zeros forming a lattice structure.
    
    In the transported coordinate t = T(x), zeros often form
    regular lattices: t ∈ πℤ, t ∈ (π/2) + πℤ, etc.
    
    The LATTICE PREIMAGE PRINCIPLE:
    Cross symmetries in t-space become infinite constant families
    in x-space via T⁻¹.
    """
    
    # Lattice parameters
    origin: float = 0.0
    step: float = PI
    
    # Lattice type
    lattice_type: str = "axis"  # "axis", "diagonal", "half-diagonal"
    
    # Range of indices
    index_range: Tuple[int, int] = (-10, 10)
    
    # Generating lens
    lens: Optional[Lens] = None
    
    def lattice_points(self) -> List[float]:
        """Generate lattice points in t-space."""
        n_min, n_max = self.index_range
        return [self.origin + n * self.step for n in range(n_min, n_max + 1)]
    
    def preimage_points(self, lens: Lens) -> List[float]:
        """
        Compute preimages T⁻¹(lattice) in x-space.
        
        This gives the constant family.
        """
        result = []
        for t in self.lattice_points():
            try:
                x = lens.inv(t)
                if x > 0:  # Usually working in positive reals
                    result.append(x)
            except (ValueError, OverflowError):
                continue
        return result
    
    @classmethod
    def axis_lattice(cls, step: float = PI) -> 'LatticeZero':
        """Create an axis lattice (t = 0, ±step, ±2·step, ...)."""
        return cls(origin=0.0, step=step, lattice_type="axis")
    
    @classmethod
    def diagonal_lattice(cls, step: float = PI) -> 'LatticeZero':
        """Create a diagonal lattice (t = step/2, 3·step/2, ...)."""
        return cls(origin=step/2, step=step, lattice_type="diagonal")
    
    @classmethod
    def phi_lattice(cls) -> 'LatticeZero':
        """
        Create the φ-lattice: s = 0, ±1, ±2, ... in log_φ coordinate.
        
        Preimages are φ^n for integer n.
        """
        return cls(
            origin=0.0,
            step=1.0,  # Unit step in log_φ
            lattice_type="phi_lattice"
        )


# =============================================================================
# CROSS-SYMMETRY ZEROS
# =============================================================================

@dataclass
class CrossSymmetryZero:
    """
    Cross-symmetry zeros: where two functions equal.
    
    Z_0(F, G) = {x : F(x) = G(x)} = Z(F - G)
    
    Examples:
    - sin(x) = cos(x) at x = π/4 + nπ
    - x = ln(x) at x ≈ ... (no real solution for x > 0)
    - e^x = x^e has solutions
    """
    
    F: Callable[[float], float]
    G: Callable[[float], float]
    F_name: str = "F"
    G_name: str = "G"
    
    zeros: List[ZeroPoint] = field(default_factory=list)
    
    def difference(self, x: float) -> float:
        """The difference function F - G."""
        return self.F(x) - self.G(x)
    
    def find_crossings(self, a: float, b: float, 
                      n_samples: int = 100) -> int:
        """Find where F = G in interval [a, b]."""
        zero_set = ZeroSet(self.difference, f"{self.F_name}={self.G_name}")
        found = zero_set.find_zeros_in_interval(a, b, n_samples)
        self.zeros = zero_set.zeros
        return found


# =============================================================================
# CANCELLATION ZEROS
# =============================================================================

@dataclass
class CancellationZero:
    """
    Cancellation zeros: where a weighted sum vanishes.
    
    Z = {x : Σ w_i F_i(x) = 0}
    
    Examples:
    - sin²(x) + cos²(x) - 1 = 0 (always zero!)
    - e^x - e^(-x) = 0 at x = 0
    """
    
    functions: List[Callable[[float], float]]
    weights: List[float]
    
    def weighted_sum(self, x: float) -> float:
        """Compute Σ w_i F_i(x)."""
        return sum(w * f(x) for w, f in zip(self.weights, self.functions))
    
    def find_zeros(self, a: float, b: float) -> List[ZeroPoint]:
        """Find cancellation zeros in [a, b]."""
        zero_set = ZeroSet(self.weighted_sum, "cancellation")
        zero_set.find_zeros_in_interval(a, b)
        return zero_set.zeros


# =============================================================================
# VALIDATION
# =============================================================================

def validate_zeros() -> bool:
    """Validate zeros module."""
    
    # Test ZeroPoint finding
    # f(x) = x^2 - 2 has zeros at ±√2
    sqrt2_constraint = lambda x: x**2 - 2
    zero = ZeroPoint.find(sqrt2_constraint, 1.5, "sqrt2")
    assert zero is not None
    assert abs(zero.value - math.sqrt(2)) < 1e-10
    assert zero.verify()
    
    # Test ZeroHierarchy
    # f(x) = (x - 1)^2 has a double zero at x = 1
    double_zero_fn = lambda x: (x - 1)**2
    hierarchy = ZeroHierarchy(double_zero_fn)
    level = hierarchy.check_hardening(1.0)
    assert level >= 2  # H and H' both vanish at x=1
    
    # Test ZeroSet
    sin_zeros = ZeroSet(math.sin, "sin")
    found = sin_zeros.find_zeros_in_interval(-10, 10)
    assert found >= 5  # Should find several multiples of π
    
    # Test LatticeZero
    phi_lattice = LatticeZero.phi_lattice()
    phi_lens = create_phi_log_lens()
    preimages = phi_lattice.preimage_points(phi_lens)
    # Should include 1, φ, φ², etc.
    assert len(preimages) > 5
    assert any(abs(x - 1.0) < 1e-10 for x in preimages)
    assert any(abs(x - PHI) < 1e-10 for x in preimages)
    
    # Test CrossSymmetryZero
    # sin(x) = cos(x) has solutions
    sin_cos_cross = CrossSymmetryZero(math.sin, math.cos, "sin", "cos")
    found = sin_cos_cross.find_crossings(0, 2*PI)
    assert found >= 2
    # Solutions should be near π/4 and 5π/4
    
    return True


if __name__ == "__main__":
    print("Validating Zeros Module...")
    assert validate_zeros()
    print("✓ Zeros Module validated")
    
    # Demo
    print("\n=== Zero Hierarchy Demo ===")
    
    # Simple zero
    print("\nSimple zero of x² - 2:")
    zero = ZeroPoint.find(lambda x: x**2 - 2, 1.5)
    print(f"  √2 ≈ {zero.value:.10f}")
    
    # Double zero
    print("\nDouble zero of (x - φ)²:")
    double_fn = lambda x: (x - PHI)**2
    hierarchy = ZeroHierarchy(double_fn)
    level = hierarchy.check_hardening(PHI)
    print(f"  Hardening level at φ: {level}")
    
    # φ-lattice preimages
    print("\nφ-Lattice Preimages (φ^n for integer n):")
    phi_lens = create_phi_log_lens()
    phi_lattice = LatticeZero.phi_lattice()
    preimages = phi_lattice.preimage_points(phi_lens)
    for x in sorted([p for p in preimages if 0.1 < p < 10]):
        n = round(math.log(x) / math.log(PHI))
        print(f"  φ^{n} = {x:.6f}")
    
    # Cross-symmetry
    print("\nCross-symmetry: sin(x) = cos(x)")
    cross = CrossSymmetryZero(math.sin, math.cos)
    cross.find_crossings(0, 2*PI)
    for zero in cross.zeros:
        angle = zero.value
        print(f"  x = {angle:.6f} rad = {math.degrees(angle):.1f}°")
