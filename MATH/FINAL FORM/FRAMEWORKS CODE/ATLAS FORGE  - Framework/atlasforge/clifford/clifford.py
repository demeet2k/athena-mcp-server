"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      CLIFFORD ALGEBRAS MODULE                                ║
║                                                                              ║
║  Geometric Algebra, Spinors, and Reflections                                 ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Clifford algebras unify geometry and algebra through the relation        ║
║    vw + wv = 2⟨v,w⟩. They provide natural descriptions of rotations,       ║
║    reflections, and spinors in the quad-polar framework.                    ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Clifford algebra: Cl(V, Q) with v² = Q(v)                              ║
║    - Geometric product: ab = a·b + a∧b                                      ║
║    - Spinor group: Pin(n), Spin(n)                                          ║
║    - Multivectors: scalars, vectors, bivectors, etc.                        ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Ω-pole rotation ↔ Spin group action                                    ║
║    - Gateway boost ↔ hyperbolic Clifford element                            ║
║    - Pole mixing ↔ geometric product                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# MULTIVECTOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Multivector:
    """
    Element of Clifford algebra Cl(n).
    
    Represented as coefficients for each basis blade.
    For Cl(n), there are 2^n basis elements.
    """
    dim: int  # Vector space dimension
    coeffs: NDArray[np.float64]  # Coefficients for 2^n blades
    signature: Tuple[int, int, int] = None  # (p, q, r) for Cl(p,q,r)
    
    def __post_init__(self):
        expected_len = 2 ** self.dim
        if len(self.coeffs) != expected_len:
            raise ValueError(f"Expected {expected_len} coefficients, got {len(self.coeffs)}")
        
        if self.signature is None:
            self.signature = (self.dim, 0, 0)  # Euclidean by default
    
    @property
    def grade_dim(self) -> int:
        """Number of grades (0 to dim)."""
        return self.dim + 1
    
    def grade(self, k: int) -> 'Multivector':
        """Extract grade-k part."""
        result = np.zeros_like(self.coeffs)
        
        for i in range(len(self.coeffs)):
            if bin(i).count('1') == k:
                result[i] = self.coeffs[i]
        
        return Multivector(self.dim, result, self.signature)
    
    def scalar(self) -> float:
        """Extract scalar (grade 0) part."""
        return float(self.coeffs[0])
    
    def vector(self) -> NDArray[np.float64]:
        """Extract vector (grade 1) part."""
        return np.array([self.coeffs[2**i] for i in range(self.dim)])
    
    def __add__(self, other: 'Multivector') -> 'Multivector':
        if self.dim != other.dim:
            raise ValueError("Dimensions must match")
        return Multivector(self.dim, self.coeffs + other.coeffs, self.signature)
    
    def __sub__(self, other: 'Multivector') -> 'Multivector':
        if self.dim != other.dim:
            raise ValueError("Dimensions must match")
        return Multivector(self.dim, self.coeffs - other.coeffs, self.signature)
    
    def __mul__(self, other) -> 'Multivector':
        if isinstance(other, (int, float)):
            return Multivector(self.dim, self.coeffs * other, self.signature)
        elif isinstance(other, Multivector):
            return self._geometric_product(other)
        raise TypeError(f"Cannot multiply Multivector by {type(other)}")
    
    def __rmul__(self, other) -> 'Multivector':
        if isinstance(other, (int, float)):
            return Multivector(self.dim, self.coeffs * other, self.signature)
        raise TypeError(f"Cannot multiply {type(other)} by Multivector")
    
    def _geometric_product(self, other: 'Multivector') -> 'Multivector':
        """
        Geometric product in Clifford algebra.
        
        Uses the multiplication table derived from e_i e_j + e_j e_i = 2η_{ij}.
        """
        if self.dim != other.dim:
            raise ValueError("Dimensions must match")
        
        p, q, r = self.signature
        n = self.dim
        
        # Metric signature: +1 for first p, -1 for next q, 0 for last r
        metric = [1] * p + [-1] * q + [0] * r
        
        result = np.zeros(2 ** n)
        
        for i in range(2 ** n):
            for j in range(2 ** n):
                if abs(self.coeffs[i]) < 1e-15 or abs(other.coeffs[j]) < 1e-15:
                    continue
                
                # Compute product of basis blades
                sign, k = self._blade_product(i, j, metric)
                result[k] += sign * self.coeffs[i] * other.coeffs[j]
        
        return Multivector(self.dim, result, self.signature)
    
    def _blade_product(self, i: int, j: int, metric: List[int]) -> Tuple[int, int]:
        """
        Product of basis blades indexed by i and j.
        
        Returns (sign, result_index).
        """
        n = self.dim
        sign = 1
        result = i ^ j  # XOR gives symmetric difference
        
        # Count swaps and contractions
        for k in range(n):
            if i & (1 << k) and j & (1 << k):
                # e_k appears in both - contracts
                sign *= metric[k]
                
                # Count how many basis vectors of i are to the right of k
                count = bin(i & ((1 << k) - 1)).count('1')
                # Count how many basis vectors of j are to the left of k  
                count += bin(j >> (k + 1)).count('1')
                sign *= (-1) ** count
            elif i & (1 << k):
                # e_k only in i - count swaps with j
                count = bin(j & ((1 << k) - 1)).count('1')
                sign *= (-1) ** count
        
        return sign, result
    
    def reverse(self) -> 'Multivector':
        """
        Reverse: reverses order of vectors in each blade.
        
        Grade k part gets sign (-1)^{k(k-1)/2}.
        """
        result = np.zeros_like(self.coeffs)
        
        for i in range(len(self.coeffs)):
            k = bin(i).count('1')
            sign = (-1) ** (k * (k - 1) // 2)
            result[i] = sign * self.coeffs[i]
        
        return Multivector(self.dim, result, self.signature)
    
    def conjugate(self) -> 'Multivector':
        """
        Clifford conjugate: reverse + grade involution on odd grades.
        """
        result = np.zeros_like(self.coeffs)
        
        for i in range(len(self.coeffs)):
            k = bin(i).count('1')
            sign = (-1) ** k * (-1) ** (k * (k - 1) // 2)
            result[i] = sign * self.coeffs[i]
        
        return Multivector(self.dim, result, self.signature)
    
    def norm_squared(self) -> float:
        """
        Squared norm: ⟨A Ã⟩_0 where Ã is reverse.
        """
        product = self * self.reverse()
        return product.scalar()
    
    def norm(self) -> float:
        """Norm √|⟨A Ã⟩_0|."""
        ns = self.norm_squared()
        return np.sqrt(abs(ns))
    
    def inverse(self) -> 'Multivector':
        """
        Inverse: A^{-1} = Ã / (A Ã) for invertible elements.
        """
        rev = self.reverse()
        norm_sq = (self * rev).scalar()
        
        if abs(norm_sq) < 1e-15:
            raise ValueError("Multivector is not invertible")
        
        return (1 / norm_sq) * rev
    
    @classmethod
    def scalar_mv(cls, dim: int, value: float, 
                 signature: Tuple[int, int, int] = None) -> 'Multivector':
        """Create scalar multivector."""
        coeffs = np.zeros(2 ** dim)
        coeffs[0] = value
        return cls(dim, coeffs, signature or (dim, 0, 0))
    
    @classmethod
    def vector_mv(cls, components: List[float],
                 signature: Tuple[int, int, int] = None) -> 'Multivector':
        """Create vector multivector from components."""
        dim = len(components)
        coeffs = np.zeros(2 ** dim)
        for i, c in enumerate(components):
            coeffs[2 ** i] = c
        return cls(dim, coeffs, signature or (dim, 0, 0))
    
    @classmethod
    def basis_vector(cls, dim: int, index: int,
                    signature: Tuple[int, int, int] = None) -> 'Multivector':
        """Create basis vector e_i."""
        coeffs = np.zeros(2 ** dim)
        coeffs[2 ** index] = 1.0
        return cls(dim, coeffs, signature or (dim, 0, 0))


# ═══════════════════════════════════════════════════════════════════════════════
# CLIFFORD ALGEBRA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CliffordAlgebra:
    """
    Clifford algebra Cl(p, q) with signature (p, q).
    
    p positive, q negative directions.
    """
    p: int  # Positive dimensions
    q: int  # Negative dimensions
    
    @property
    def dim(self) -> int:
        """Vector space dimension."""
        return self.p + self.q
    
    @property
    def algebra_dim(self) -> int:
        """Algebra dimension = 2^n."""
        return 2 ** self.dim
    
    @property
    def signature(self) -> Tuple[int, int, int]:
        return (self.p, self.q, 0)
    
    def scalar(self, value: float) -> Multivector:
        """Create scalar element."""
        return Multivector.scalar_mv(self.dim, value, self.signature)
    
    def vector(self, components: List[float]) -> Multivector:
        """Create vector element."""
        if len(components) != self.dim:
            raise ValueError(f"Expected {self.dim} components")
        return Multivector.vector_mv(components, self.signature)
    
    def basis(self, index: int) -> Multivector:
        """Get basis vector e_i."""
        return Multivector.basis_vector(self.dim, index, self.signature)
    
    def pseudoscalar(self) -> Multivector:
        """
        Pseudoscalar I = e_1 e_2 ... e_n.
        """
        coeffs = np.zeros(self.algebra_dim)
        coeffs[-1] = 1.0  # Highest grade blade
        return Multivector(self.dim, coeffs, self.signature)
    
    def inner_product(self, a: Multivector, b: Multivector) -> float:
        """
        Inner product: ⟨a, b⟩ = (ab̃)_0.
        """
        return (a * b.reverse()).scalar()
    
    def outer_product(self, a: Multivector, b: Multivector) -> Multivector:
        """
        Outer (wedge) product: a ∧ b.
        
        Extracts highest-grade part of geometric product.
        """
        product = a * b
        
        # Grade of wedge product
        ga = sum(bin(i).count('1') for i in range(len(a.coeffs)) 
                if abs(a.coeffs[i]) > 1e-15)
        gb = sum(bin(i).count('1') for i in range(len(b.coeffs)) 
                if abs(b.coeffs[i]) > 1e-15)
        
        # Simplified: assume a, b are homogeneous
        target_grade = ga + gb
        return product.grade(min(target_grade, self.dim))


# ═══════════════════════════════════════════════════════════════════════════════
# ROTORS AND SPINORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Rotor:
    """
    Rotor: even-grade element with RR̃ = 1.
    
    Represents rotation via v ↦ RvR̃.
    """
    multivector: Multivector
    
    def __post_init__(self):
        # Verify rotor condition
        product = self.multivector * self.multivector.reverse()
        if abs(product.scalar() - 1) > 1e-10:
            # Normalize
            norm = self.multivector.norm()
            self.multivector = (1 / norm) * self.multivector
    
    def apply(self, v: Multivector) -> Multivector:
        """Apply rotor to vector: v ↦ RvR̃."""
        return self.multivector * v * self.multivector.reverse()
    
    def compose(self, other: 'Rotor') -> 'Rotor':
        """Compose rotors: R_2 R_1 applies R_1 then R_2."""
        return Rotor(self.multivector * other.multivector)
    
    def inverse(self) -> 'Rotor':
        """Inverse rotor R̃."""
        return Rotor(self.multivector.reverse())
    
    @classmethod
    def from_angle_plane(cls, algebra: CliffordAlgebra, 
                        angle: float, i: int, j: int) -> 'Rotor':
        """
        Create rotor for rotation by angle in e_i ∧ e_j plane.
        
        R = cos(θ/2) - sin(θ/2) e_i e_j
        """
        e_i = algebra.basis(i)
        e_j = algebra.basis(j)
        bivector = e_i * e_j
        
        c = np.cos(angle / 2)
        s = np.sin(angle / 2)
        
        scalar_part = algebra.scalar(c)
        bivector_part = (-s) * bivector
        
        return cls(scalar_part + bivector_part)
    
    @classmethod
    def from_vectors(cls, algebra: CliffordAlgebra,
                    u: List[float], v: List[float]) -> 'Rotor':
        """
        Create rotor that rotates u to v.
        
        R = (1 + vu) / |1 + vu|
        """
        u_mv = algebra.vector(u)
        v_mv = algebra.vector(v)
        
        one = algebra.scalar(1.0)
        unnorm = one + v_mv * u_mv
        
        return cls(unnorm)


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIFIC ALGEBRAS
# ═══════════════════════════════════════════════════════════════════════════════

class GeometricAlgebras:
    """Standard geometric algebras."""
    
    @staticmethod
    def G2() -> CliffordAlgebra:
        """2D Euclidean geometric algebra Cl(2,0)."""
        return CliffordAlgebra(2, 0)
    
    @staticmethod
    def G3() -> CliffordAlgebra:
        """3D Euclidean geometric algebra Cl(3,0)."""
        return CliffordAlgebra(3, 0)
    
    @staticmethod
    def spacetime() -> CliffordAlgebra:
        """Spacetime algebra Cl(1,3)."""
        return CliffordAlgebra(1, 3)
    
    @staticmethod
    def complex_numbers() -> CliffordAlgebra:
        """Complex numbers as Cl(0,1)."""
        return CliffordAlgebra(0, 1)
    
    @staticmethod
    def quaternions() -> CliffordAlgebra:
        """Quaternions as even subalgebra of Cl(0,2)."""
        return CliffordAlgebra(0, 2)
    
    @staticmethod
    def split_quaternions() -> CliffordAlgebra:
        """Split quaternions as Cl(1,1)."""
        return CliffordAlgebra(1, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def clifford_algebra(p: int, q: int = 0) -> CliffordAlgebra:
    """Create Clifford algebra Cl(p,q)."""
    return CliffordAlgebra(p, q)


def multivector(dim: int, coeffs: List[float], 
               signature: Tuple[int, int, int] = None) -> Multivector:
    """Create multivector."""
    return Multivector(dim, np.array(coeffs), signature)


def rotor_from_angle(algebra: CliffordAlgebra, angle: float, 
                    plane: Tuple[int, int]) -> Rotor:
    """Create rotation rotor."""
    return Rotor.from_angle_plane(algebra, angle, plane[0], plane[1])


def geometric_product(a: Multivector, b: Multivector) -> Multivector:
    """Compute geometric product."""
    return a * b


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core
    'Multivector',
    'CliffordAlgebra',
    
    # Rotors
    'Rotor',
    
    # Standard algebras
    'GeometricAlgebras',
    
    # Functions
    'clifford_algebra',
    'multivector',
    'rotor_from_angle',
    'geometric_product',
]
