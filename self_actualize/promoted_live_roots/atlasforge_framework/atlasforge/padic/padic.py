"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       P-ADIC NUMBERS MODULE                                  ║
║                                                                              ║
║  Non-Archimedean Analysis, Hensel's Lemma, Local Fields                      ║
║                                                                              ║
║  Core Principle:                                                             ║
║    p-adic numbers complete ℚ with respect to p-adic absolute value.         ║
║    The ultrametric property |x + y| ≤ max(|x|, |y|) creates                ║
║    hierarchical structure connecting to the Ψ-pole.                         ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - ℤ_p: p-adic integers, completion of ℤ                                  ║
║    - ℚ_p: p-adic rationals, field of fractions                              ║
║    - |x|_p = p^{-v_p(x)}: p-adic absolute value                             ║
║    - Hensel's lemma: lifting roots modulo p^n                               ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Ψ-pole hierarchy ↔ p-adic digit expansion                              ║
║    - Renormalization ↔ p-adic scaling                                       ║
║    - Fractal structure ↔ ultrametric topology                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Iterator
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# P-ADIC INTEGER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PadicInteger:
    """
    p-adic integer in ℤ_p.
    
    Represented as sequence of digits (a_0, a_1, a_2, ...) with 0 ≤ a_i < p.
    x = a_0 + a_1·p + a_2·p² + ...
    """
    digits: List[int]  # First `precision` digits
    p: int  # Prime base
    precision: int  # Number of digits stored
    
    def __post_init__(self):
        # Ensure digits are in range [0, p)
        self.digits = [d % self.p for d in self.digits]
        while len(self.digits) < self.precision:
            self.digits.append(0)
        self.digits = self.digits[:self.precision]
    
    def to_int_mod(self, n: int) -> int:
        """Convert to integer mod p^n."""
        result = 0
        power = 1
        for i in range(min(n, len(self.digits))):
            result += self.digits[i] * power
            power *= self.p
        return result
    
    def valuation(self) -> int:
        """p-adic valuation v_p(x) = smallest k with a_k ≠ 0."""
        for i, d in enumerate(self.digits):
            if d != 0:
                return i
        return self.precision  # Effectively zero to this precision
    
    def abs(self) -> float:
        """p-adic absolute value |x|_p = p^{-v_p(x)}."""
        v = self.valuation()
        if v >= self.precision:
            return 0.0
        return self.p ** (-v)
    
    def __add__(self, other: 'PadicInteger') -> 'PadicInteger':
        """p-adic addition with carry."""
        if self.p != other.p:
            raise ValueError("Primes must match")
        
        result = []
        carry = 0
        
        for i in range(self.precision):
            s = self.digits[i] + other.digits[i] + carry
            result.append(s % self.p)
            carry = s // self.p
        
        return PadicInteger(result, self.p, self.precision)
    
    def __neg__(self) -> 'PadicInteger':
        """p-adic negation: -x = (p-1 - x) + 1."""
        # Complement digits
        comp = [(self.p - 1 - d) for d in self.digits]
        # Add 1
        carry = 1
        for i in range(len(comp)):
            s = comp[i] + carry
            comp[i] = s % self.p
            carry = s // self.p
            if carry == 0:
                break
        
        return PadicInteger(comp, self.p, self.precision)
    
    def __sub__(self, other: 'PadicInteger') -> 'PadicInteger':
        return self + (-other)
    
    def __mul__(self, other: 'PadicInteger') -> 'PadicInteger':
        """p-adic multiplication."""
        if self.p != other.p:
            raise ValueError("Primes must match")
        
        result = [0] * self.precision
        
        for i in range(self.precision):
            for j in range(self.precision - i):
                result[i + j] += self.digits[i] * other.digits[j]
        
        # Reduce mod p with carry
        carry = 0
        for i in range(self.precision):
            result[i] += carry
            carry = result[i] // self.p
            result[i] %= self.p
        
        return PadicInteger(result, self.p, self.precision)
    
    def __repr__(self) -> str:
        # Show as ...a_2 a_1 a_0 (reversed order)
        digits_str = ''.join(str(d) for d in reversed(self.digits[-10:]))
        return f"...{digits_str} (base {self.p})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PadicInteger):
            return False
        if self.p != other.p:
            return False
        return self.digits == other.digits
    
    @classmethod
    def from_int(cls, n: int, p: int, precision: int = 20) -> 'PadicInteger':
        """Create p-adic integer from ordinary integer."""
        digits = []
        x = abs(n)
        for _ in range(precision):
            digits.append(x % p)
            x //= p
        
        result = cls(digits, p, precision)
        if n < 0:
            result = -result
        
        return result
    
    @classmethod
    def zero(cls, p: int, precision: int = 20) -> 'PadicInteger':
        return cls([0] * precision, p, precision)
    
    @classmethod
    def one(cls, p: int, precision: int = 20) -> 'PadicInteger':
        return cls([1] + [0] * (precision - 1), p, precision)


# ═══════════════════════════════════════════════════════════════════════════════
# P-ADIC RATIONAL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PadicRational:
    """
    p-adic rational in ℚ_p.
    
    x = p^v · u where u is a unit in ℤ_p.
    """
    unit: PadicInteger
    valuation: int
    
    @property
    def p(self) -> int:
        return self.unit.p
    
    def abs(self) -> float:
        """p-adic absolute value."""
        return self.p ** (-self.valuation)
    
    def __add__(self, other: 'PadicRational') -> 'PadicRational':
        """p-adic addition."""
        if self.p != other.p:
            raise ValueError("Primes must match")
        
        # Align valuations
        if self.valuation < other.valuation:
            shift = other.valuation - self.valuation
            # Multiply other.unit by p^shift
            other_aligned = other.unit
            for _ in range(shift):
                other_aligned = other_aligned * PadicInteger.from_int(self.p, self.p)
            
            result_unit = self.unit + other_aligned
            return PadicRational(result_unit, self.valuation)
        else:
            return other + self  # Swap and recurse
    
    def __mul__(self, other: 'PadicRational') -> 'PadicRational':
        """p-adic multiplication."""
        new_unit = self.unit * other.unit
        new_val = self.valuation + other.valuation
        return PadicRational(new_unit, new_val)
    
    def inverse(self) -> 'PadicRational':
        """
        Multiplicative inverse in ℚ_p.
        
        Uses Newton iteration: x_{n+1} = x_n(2 - a·x_n)
        """
        # For unit u, find u^{-1}
        # Start with approximation mod p
        a0 = self.unit.digits[0]
        x0 = pow(a0, -1, self.p)
        
        x = PadicInteger.from_int(x0, self.p, self.unit.precision)
        
        two = PadicInteger.from_int(2, self.p, self.unit.precision)
        
        for _ in range(int(np.log2(self.unit.precision)) + 1):
            # x = x * (2 - u * x)
            prod = self.unit * x
            diff = two - prod
            x = x * diff
        
        return PadicRational(x, -self.valuation)
    
    @classmethod
    def from_fraction(cls, num: int, den: int, p: int, 
                     precision: int = 20) -> 'PadicRational':
        """Create from ordinary fraction."""
        # Factor out p
        v_num = 0
        while num % p == 0:
            num //= p
            v_num += 1
        
        v_den = 0
        while den % p == 0:
            den //= p
            v_den += 1
        
        valuation = v_num - v_den
        
        # Now num/den is a p-adic unit
        # Compute num * den^{-1} in ℤ_p
        num_padic = PadicInteger.from_int(num, p, precision)
        den_padic = PadicInteger.from_int(den, p, precision)
        
        # Inverse of den
        den_inv = PadicRational(den_padic, 0).inverse()
        
        unit = num_padic * den_inv.unit
        
        return cls(unit, valuation)


# ═══════════════════════════════════════════════════════════════════════════════
# HENSEL'S LEMMA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HenselLifter:
    """
    Hensel's lemma: lift roots from ℤ/pℤ to ℤ_p.
    
    If f(a) ≡ 0 (mod p) and f'(a) ≢ 0 (mod p),
    then there exists unique α ∈ ℤ_p with f(α) = 0 and α ≡ a (mod p).
    """
    coefficients: List[int]  # Polynomial coefficients
    p: int  # Prime
    
    def evaluate(self, x: int, mod: int) -> int:
        """Evaluate polynomial at x mod m."""
        result = 0
        power = 1
        for c in self.coefficients:
            result = (result + c * power) % mod
            power = (power * x) % mod
        return result
    
    def derivative(self, x: int, mod: int) -> int:
        """Evaluate derivative at x mod m."""
        result = 0
        power = 1
        for i, c in enumerate(self.coefficients[1:], 1):
            result = (result + i * c * power) % mod
            power = (power * x) % mod
        return result
    
    def find_roots_mod_p(self) -> List[int]:
        """Find all roots of f(x) ≡ 0 (mod p)."""
        return [a for a in range(self.p) if self.evaluate(a, self.p) == 0]
    
    def can_lift(self, a: int) -> bool:
        """Check if root a mod p can be lifted."""
        return self.derivative(a, self.p) % self.p != 0
    
    def lift(self, a: int, target_precision: int) -> PadicInteger:
        """
        Lift root a from mod p to mod p^n.
        
        Uses Newton iteration: a_{n+1} = a_n - f(a_n)/f'(a_n)
        """
        if not self.can_lift(a):
            raise ValueError(f"Cannot lift: f'({a}) ≡ 0 (mod {self.p})")
        
        current = a
        mod = self.p
        
        for _ in range(target_precision):
            f_val = self.evaluate(current, mod * self.p)
            f_prime = self.derivative(current, self.p)
            
            # f_prime^{-1} mod p
            f_prime_inv = pow(f_prime, -1, self.p)
            
            # Newton step
            delta = (f_val * f_prime_inv) % (mod * self.p)
            current = (current - delta) % (mod * self.p)
            
            mod *= self.p
        
        # Convert to PadicInteger
        return PadicInteger.from_int(current, self.p, target_precision)
    
    def all_padic_roots(self, precision: int = 20) -> List[PadicInteger]:
        """Find all p-adic roots (to given precision)."""
        roots = []
        for a in self.find_roots_mod_p():
            if self.can_lift(a):
                roots.append(self.lift(a, precision))
        return roots


# ═══════════════════════════════════════════════════════════════════════════════
# ULTRAMETRIC SPACE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UltrametricSpace:
    """
    Ultrametric space with strong triangle inequality.
    
    d(x, z) ≤ max(d(x, y), d(y, z))
    """
    points: List[PadicInteger]
    
    def distance(self, i: int, j: int) -> float:
        """Ultrametric distance between points i and j."""
        diff = self.points[i] - self.points[j]
        return diff.abs()
    
    def distance_matrix(self) -> NDArray[np.float64]:
        """Compute all pairwise distances."""
        n = len(self.points)
        D = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                d = self.distance(i, j)
                D[i, j] = d
                D[j, i] = d
        
        return D
    
    def verify_ultrametric(self) -> bool:
        """Verify ultrametric inequality holds."""
        n = len(self.points)
        
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    d_ij = self.distance(i, j)
                    d_jk = self.distance(j, k)
                    d_ik = self.distance(i, k)
                    
                    if d_ik > max(d_ij, d_jk) + 1e-10:
                        return False
        
        return True
    
    def ball(self, center: int, radius: float) -> List[int]:
        """Points within radius of center."""
        return [i for i in range(len(self.points)) 
               if self.distance(center, i) <= radius]


# ═══════════════════════════════════════════════════════════════════════════════
# PSI-POLE P-ADIC BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PsiPolePadicBridge:
    """
    Bridge between Ψ-pole (hierarchical) and p-adic structure.
    
    p-adic digit expansion = hierarchical decomposition.
    """
    
    @staticmethod
    def hierarchy_to_padic(levels: List[int], p: int) -> PadicInteger:
        """
        Convert hierarchical level values to p-adic integer.
        
        Level i contributes digit a_i in p-adic expansion.
        """
        digits = [l % p for l in levels]
        return PadicInteger(digits, p, len(digits))
    
    @staticmethod
    def padic_to_hierarchy(x: PadicInteger) -> List[int]:
        """Convert p-adic integer to hierarchy levels."""
        return list(x.digits)
    
    @staticmethod
    def renormalization_step(x: PadicInteger) -> PadicInteger:
        """
        Renormalization as p-adic shift.
        
        Divide by p: shifts digits down.
        """
        new_digits = x.digits[1:] + [0]
        return PadicInteger(new_digits, x.p, x.precision)
    
    @staticmethod
    def fractal_dimension_estimate(points: List[PadicInteger]) -> float:
        """
        Estimate fractal dimension of p-adic point set.
        
        Uses box-counting in ultrametric.
        """
        if not points:
            return 0.0
        
        p = points[0].p
        
        # Count balls at different scales
        counts = []
        for k in range(1, min(10, points[0].precision)):
            radius = p ** (-k)
            # Count distinct balls
            balls = set()
            for pt in points:
                ball_id = tuple(pt.digits[:k])
                balls.add(ball_id)
            counts.append((k, len(balls)))
        
        if len(counts) < 2:
            return 0.0
        
        # Linear regression for dimension
        ks = np.array([c[0] for c in counts])
        log_counts = np.log(np.array([c[1] for c in counts]) + 1)
        
        slope, _ = np.polyfit(ks, log_counts, 1)
        return slope / np.log(p)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def padic_int(n: int, p: int, precision: int = 20) -> PadicInteger:
    """Create p-adic integer from int."""
    return PadicInteger.from_int(n, p, precision)


def padic_valuation(n: int, p: int) -> int:
    """Compute v_p(n)."""
    if n == 0:
        return float('inf')
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def padic_norm(n: int, p: int) -> float:
    """Compute |n|_p."""
    v = padic_valuation(n, p)
    return p ** (-v) if v != float('inf') else 0.0


def hensel_lift(poly_coeffs: List[int], p: int, 
               precision: int = 20) -> List[PadicInteger]:
    """Find p-adic roots via Hensel lifting."""
    return HenselLifter(poly_coeffs, p).all_padic_roots(precision)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core
    'PadicInteger',
    'PadicRational',
    
    # Hensel
    'HenselLifter',
    
    # Ultrametric
    'UltrametricSpace',
    
    # Bridge
    'PsiPolePadicBridge',
    
    # Functions
    'padic_int',
    'padic_valuation',
    'padic_norm',
    'hensel_lift',
]
