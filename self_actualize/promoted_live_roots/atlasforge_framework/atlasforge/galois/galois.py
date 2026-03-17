"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        GALOIS THEORY MODULE                                  ║
║                                                                              ║
║  Field Extensions, Automorphisms, and Solvability                            ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Galois theory connects field extensions to group theory. The             ║
║    gateway algebra involves quadratic extensions, and understanding         ║
║    Galois groups reveals the structure of gateway compositions.             ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Field extension K/F with degree [K:F]                                  ║
║    - Galois group Gal(K/F) = Aut_F(K)                                       ║
║    - Fundamental theorem: subgroups ↔ intermediate fields                   ║
║    - Solvability by radicals ↔ solvable Galois group                       ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - ℚ(√D)/ℚ has Gal ≅ ℤ/2ℤ                                                ║
║    - Quadratic character determines gateway structure                       ║
║    - Compositum of fields ↔ composed gateways                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set, Callable
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# POLYNOMIAL RING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Polynomial:
    """
    Polynomial with rational coefficients.
    
    coeffs[i] is coefficient of x^i.
    """
    coeffs: List[Fraction]
    
    def __post_init__(self):
        # Convert to Fraction and remove trailing zeros
        self.coeffs = [Fraction(c) for c in self.coeffs]
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()
    
    @property
    def degree(self) -> int:
        """Degree of polynomial."""
        return len(self.coeffs) - 1
    
    def __call__(self, x: complex) -> complex:
        """Evaluate polynomial at x."""
        result = 0
        for i, c in enumerate(self.coeffs):
            result += float(c) * (x ** i)
        return result
    
    def __add__(self, other: 'Polynomial') -> 'Polynomial':
        n = max(len(self.coeffs), len(other.coeffs))
        result = [Fraction(0)] * n
        for i, c in enumerate(self.coeffs):
            result[i] += c
        for i, c in enumerate(other.coeffs):
            result[i] += c
        return Polynomial(result)
    
    def __mul__(self, other: 'Polynomial') -> 'Polynomial':
        n = self.degree + other.degree + 1
        result = [Fraction(0)] * n
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                result[i + j] += a * b
        return Polynomial(result)
    
    def __neg__(self) -> 'Polynomial':
        return Polynomial([-c for c in self.coeffs])
    
    def __sub__(self, other: 'Polynomial') -> 'Polynomial':
        return self + (-other)
    
    def derivative(self) -> 'Polynomial':
        """Formal derivative."""
        if self.degree == 0:
            return Polynomial([Fraction(0)])
        return Polynomial([Fraction(i) * self.coeffs[i] 
                          for i in range(1, len(self.coeffs))])
    
    def is_irreducible_quadratic(self) -> bool:
        """Check if degree-2 polynomial is irreducible over ℚ."""
        if self.degree != 2:
            return False
        
        a, b, c = float(self.coeffs[2]), float(self.coeffs[1]), float(self.coeffs[0])
        discriminant = b * b - 4 * a * c
        
        # Irreducible iff discriminant is not a perfect square
        if discriminant < 0:
            return True
        sqrt_disc = np.sqrt(discriminant)
        return abs(sqrt_disc - round(sqrt_disc)) > 1e-10
    
    def roots_numerical(self) -> List[complex]:
        """Find roots numerically."""
        if self.degree <= 0:
            return []
        
        coeffs_float = [float(c) for c in reversed(self.coeffs)]
        return list(np.roots(coeffs_float))
    
    @classmethod
    def from_roots(cls, roots: List[complex]) -> 'Polynomial':
        """Construct polynomial from roots (approximately)."""
        result = cls([Fraction(1)])
        for r in roots:
            # (x - r)
            factor = cls([Fraction(-int(round(r.real))) if abs(r.imag) < 1e-10 
                         else Fraction(0), Fraction(1)])
            result = result * factor
        return result
    
    @classmethod
    def cyclotomic(cls, n: int) -> 'Polynomial':
        """n-th cyclotomic polynomial Φ_n(x)."""
        # Φ_n(x) = Π_{d|n} (x^d - 1)^{μ(n/d)}
        # For simplicity, compute for small n
        
        if n == 1:
            return cls([Fraction(-1), Fraction(1)])  # x - 1
        elif n == 2:
            return cls([Fraction(1), Fraction(1)])   # x + 1
        elif n == 3:
            return cls([Fraction(1), Fraction(1), Fraction(1)])  # x² + x + 1
        elif n == 4:
            return cls([Fraction(1), Fraction(0), Fraction(1)])  # x² + 1
        elif n == 6:
            return cls([Fraction(1), Fraction(-1), Fraction(1)])  # x² - x + 1
        else:
            # General case would need Möbius function
            raise NotImplementedError(f"Cyclotomic polynomial Φ_{n} not implemented")
    
    def __repr__(self) -> str:
        terms = []
        for i, c in enumerate(self.coeffs):
            if c == 0:
                continue
            if i == 0:
                terms.append(str(c))
            elif i == 1:
                if c == 1:
                    terms.append("x")
                else:
                    terms.append(f"{c}x")
            else:
                if c == 1:
                    terms.append(f"x^{i}")
                else:
                    terms.append(f"{c}x^{i}")
        return " + ".join(terms) if terms else "0"


# ═══════════════════════════════════════════════════════════════════════════════
# FIELD EXTENSION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QuadraticExtension:
    """
    Quadratic field extension ℚ(√D)/ℚ.
    
    Elements: a + b√D with a, b ∈ ℚ
    """
    D: int  # Squarefree integer
    
    def __post_init__(self):
        # Ensure D is squarefree
        self.D = self._squarefree_part(self.D)
        self.minimal_poly = Polynomial([Fraction(-self.D), Fraction(0), Fraction(1)])
    
    @staticmethod
    def _squarefree_part(n: int) -> int:
        """Extract squarefree part of n."""
        if n == 0:
            return 0
        sign = 1 if n > 0 else -1
        n = abs(n)
        result = 1
        d = 2
        while d * d <= n:
            if n % (d * d) == 0:
                n //= (d * d)
            elif n % d == 0:
                result *= d
                n //= d
                d += 1
            else:
                d += 1
        return sign * result * n
    
    @property
    def degree(self) -> int:
        """Extension degree [K:F]."""
        return 2
    
    @property
    def discriminant(self) -> int:
        """Field discriminant."""
        if self.D % 4 == 1:
            return self.D
        return 4 * self.D
    
    @property
    def is_real(self) -> bool:
        """Real quadratic field."""
        return self.D > 0
    
    def conjugate(self, a: Fraction, b: Fraction) -> Tuple[Fraction, Fraction]:
        """Galois conjugate: √D ↦ -√D."""
        return (a, -b)
    
    def norm(self, a: Fraction, b: Fraction) -> Fraction:
        """Field norm: N(a + b√D) = a² - Db²."""
        return a * a - Fraction(self.D) * b * b
    
    def trace(self, a: Fraction, b: Fraction) -> Fraction:
        """Field trace: Tr(a + b√D) = 2a."""
        return 2 * a
    
    def multiply(self, elem1: Tuple[Fraction, Fraction], 
                elem2: Tuple[Fraction, Fraction]) -> Tuple[Fraction, Fraction]:
        """Multiply two elements."""
        a1, b1 = elem1
        a2, b2 = elem2
        return (a1 * a2 + Fraction(self.D) * b1 * b2, a1 * b2 + a2 * b1)


@dataclass
class CyclotomicExtension:
    """
    Cyclotomic field extension ℚ(ζ_n)/ℚ where ζ_n = e^{2πi/n}.
    """
    n: int
    
    def __post_init__(self):
        self.zeta = np.exp(2j * np.pi / self.n)
        self.minimal_poly = Polynomial.cyclotomic(self.n)
    
    @property
    def degree(self) -> int:
        """Extension degree = φ(n) (Euler totient)."""
        return self._euler_phi(self.n)
    
    @staticmethod
    def _euler_phi(n: int) -> int:
        """Euler's totient function."""
        result = n
        p = 2
        while p * p <= n:
            if n % p == 0:
                while n % p == 0:
                    n //= p
                result -= result // p
            p += 1
        if n > 1:
            result -= result // n
        return result
    
    def primitive_roots(self) -> List[complex]:
        """All primitive n-th roots of unity."""
        return [np.exp(2j * np.pi * k / self.n) 
                for k in range(self.n) if np.gcd(k, self.n) == 1]
    
    @property
    def galois_group_order(self) -> int:
        """Order of Galois group = degree = φ(n)."""
        return self.degree


# ═══════════════════════════════════════════════════════════════════════════════
# GALOIS GROUP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GaloisGroup:
    """
    Galois group of a field extension.
    """
    extension_type: str  # 'quadratic', 'cyclotomic', etc.
    order: int
    elements: List[str]
    is_abelian: bool
    is_cyclic: bool
    
    @classmethod
    def of_quadratic(cls, D: int) -> 'GaloisGroup':
        """Galois group of ℚ(√D)/ℚ is ℤ/2ℤ."""
        return cls(
            extension_type='quadratic',
            order=2,
            elements=['id', 'σ'],  # σ: √D ↦ -√D
            is_abelian=True,
            is_cyclic=True
        )
    
    @classmethod
    def of_cyclotomic(cls, n: int) -> 'GaloisGroup':
        """Galois group of ℚ(ζ_n)/ℚ is (ℤ/nℤ)*."""
        phi_n = CyclotomicExtension._euler_phi(n)
        elements = [f"σ_{k}" for k in range(1, n) if np.gcd(k, n) == 1]
        
        # (Z/nZ)* is cyclic iff n = 1, 2, 4, p^k, or 2p^k
        is_cyclic = cls._is_cyclic_unit_group(n)
        
        return cls(
            extension_type='cyclotomic',
            order=phi_n,
            elements=elements,
            is_abelian=True,
            is_cyclic=is_cyclic
        )
    
    @staticmethod
    def _is_cyclic_unit_group(n: int) -> bool:
        """Check if (ℤ/nℤ)* is cyclic."""
        if n <= 2:
            return True
        if n == 4:
            return True
        
        # Check if n = p^k or 2p^k for odd prime p
        m = n
        if m % 2 == 0:
            m //= 2
        
        # Check if m is a prime power
        for p in range(2, int(np.sqrt(m)) + 1):
            if m % p == 0:
                while m % p == 0:
                    m //= p
                return m == 1
        
        return True  # m is prime
    
    def is_solvable(self) -> bool:
        """Check if group is solvable."""
        # Abelian groups are always solvable
        return self.is_abelian


# ═══════════════════════════════════════════════════════════════════════════════
# SPLITTING FIELD
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SplittingField:
    """
    Splitting field of a polynomial.
    
    The minimal extension where polynomial factors completely.
    """
    polynomial: Polynomial
    
    def __post_init__(self):
        self.roots = self.polynomial.roots_numerical()
    
    def degree_over_Q(self) -> int:
        """
        Degree of splitting field over ℚ.
        
        For degree-n polynomial, at most n!
        """
        n = self.polynomial.degree
        
        # Check for special cases
        if n == 2:
            if self.polynomial.is_irreducible_quadratic():
                return 2
            return 1
        
        # General bound
        return np.math.factorial(n)
    
    def galois_group_order(self) -> int:
        """Order of Galois group = [K:ℚ] for Galois extension."""
        return self.degree_over_Q()


# ═══════════════════════════════════════════════════════════════════════════════
# RADICAL EXTENSIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RadicalExtension:
    """
    Extension by radicals: K(ⁿ√a)/K.
    """
    base_element: complex
    root_degree: int
    
    @property
    def extension_degree(self) -> int:
        """
        Degree divides root_degree.
        
        Equals root_degree if x^n - a is irreducible.
        """
        return self.root_degree
    
    def all_roots(self) -> List[complex]:
        """All n-th roots of base element."""
        principal = self.base_element ** (1 / self.root_degree)
        zeta = np.exp(2j * np.pi / self.root_degree)
        return [principal * (zeta ** k) for k in range(self.root_degree)]


@dataclass
class SolvabilityChecker:
    """
    Check solvability of polynomial equations by radicals.
    
    Abel-Ruffini: General degree ≥ 5 polynomial not solvable.
    Galois criterion: Solvable iff Galois group is solvable.
    """
    polynomial: Polynomial
    
    def is_solvable_by_radicals(self) -> Tuple[bool, str]:
        """
        Check if polynomial equation is solvable by radicals.
        
        Returns (is_solvable, reason).
        """
        n = self.polynomial.degree
        
        if n <= 1:
            return True, "Linear: x = -a_0/a_1"
        
        if n == 2:
            return True, "Quadratic formula: x = (-b ± √(b²-4ac))/(2a)"
        
        if n == 3:
            return True, "Cardano's formula for cubic"
        
        if n == 4:
            return True, "Ferrari's method for quartic"
        
        # Degree ≥ 5: depends on Galois group
        # For generic polynomial, S_n is not solvable for n ≥ 5
        return False, f"Degree {n} ≥ 5: Generic polynomial has Galois group S_{n}, which is not solvable"


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY GALOIS CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewayGaloisBridge:
    """
    Connection between gateway algebra and Galois theory.
    
    Gateway discriminant A determines quadratic extension ℚ(√A)/ℚ.
    """
    
    @staticmethod
    def gateway_galois_automorphism(u: int, v: int, A: int
                                   ) -> Tuple[int, int]:
        """
        Apply Galois automorphism to Pell unit u + v√A.
        
        σ(u + v√A) = u - v√A
        """
        return (u, -v)
    
    @staticmethod
    def gateway_field_extension(A: int) -> QuadraticExtension:
        """Quadratic extension for gateway discriminant."""
        return QuadraticExtension(A)
    
    @staticmethod
    def metallic_galois_group(n: int) -> GaloisGroup:
        """
        Galois group for metallic mean field.
        
        δ_n = (n + √(n²+4))/2 generates ℚ(√(n²+4))/ℚ.
        """
        D = n * n + 4
        D_sf = QuadraticExtension._squarefree_part(D)
        return GaloisGroup.of_quadratic(D_sf)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def polynomial(*coeffs) -> Polynomial:
    """Create polynomial from coefficients (constant term first)."""
    return Polynomial([Fraction(c) for c in coeffs])


def quadratic_extension(D: int) -> QuadraticExtension:
    """Create quadratic extension ℚ(√D)."""
    return QuadraticExtension(D)


def cyclotomic_extension(n: int) -> CyclotomicExtension:
    """Create cyclotomic extension ℚ(ζ_n)."""
    return CyclotomicExtension(n)


def galois_group_quadratic(D: int) -> GaloisGroup:
    """Galois group of ℚ(√D)/ℚ."""
    return GaloisGroup.of_quadratic(D)


def is_solvable_by_radicals(poly: Polynomial) -> bool:
    """Check if polynomial is solvable by radicals."""
    return SolvabilityChecker(poly).is_solvable_by_radicals()[0]


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Polynomials
    'Polynomial',
    
    # Extensions
    'QuadraticExtension',
    'CyclotomicExtension',
    
    # Galois theory
    'GaloisGroup',
    'SplittingField',
    
    # Radicals
    'RadicalExtension',
    'SolvabilityChecker',
    
    # Bridge
    'GatewayGaloisBridge',
    
    # Functions
    'polynomial',
    'quadratic_extension',
    'cyclotomic_extension',
    'galois_group_quadratic',
    'is_solvable_by_radicals',
]
