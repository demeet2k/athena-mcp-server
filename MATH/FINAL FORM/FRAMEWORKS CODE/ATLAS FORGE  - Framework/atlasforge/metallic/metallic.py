"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       METALLIC SEQUENCES MODULE                              ║
║                                                                              ║
║  Generalized Fibonacci/Lucas, Continued Fractions, Metallic Means            ║
║                                                                              ║
║  Core Principle:                                                             ║
║    The metallic mean δ_n is the positive root of x² - nx - 1 = 0.           ║
║    It satisfies δ_n = n + 1/δ_n with continued fraction [n; n, n, ...].     ║
║    Powers δ_n^k = F_k^(n)·δ_n + F_{k-1}^(n) are exact integer arithmetic.   ║
║                                                                              ║
║  Key Sequences:                                                              ║
║    n=1: Golden ratio φ, Fibonacci sequence                                   ║
║    n=2: Silver ratio δ_s = 1+√2, Pell numbers                                ║
║    n=3: Bronze ratio, etc.                                                   ║
║                                                                              ║
║  Transfer Matrix:                                                            ║
║    M_n = [[n, 1], [1, 0]], M_n^k gives F_{k+1}, F_k, F_{k-1}                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Iterator, Generator
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray
import math
from fractions import Fraction


# ═══════════════════════════════════════════════════════════════════════════════
# METALLIC MEAN - THE FUNDAMENTAL CONSTANT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MetallicMean:
    """
    The metallic mean δ_n, positive root of x² - nx - 1 = 0.
    
    δ_n = (n + √(n² + 4))/2
    
    Properties:
        - δ_n · δ̄_n = -1 (unit of norm -1 in ℤ[δ_n])
        - δ̄_n = -1/δ_n (conjugate is negative reciprocal)
        - δ_n + δ̄_n = n (trace)
        - δ_n = n + 1/δ_n (self-reference)
        - δ_n = [n; n, n, n, ...] (purely periodic continued fraction)
    
    Named ratios:
        n=1: Golden ratio φ ≈ 1.618
        n=2: Silver ratio δ_s ≈ 2.414
        n=3: Bronze ratio ≈ 3.303
    """
    index: int  # n
    
    def __post_init__(self):
        if self.index < 1:
            raise ValueError(f"Metallic index must be ≥ 1, got {self.index}")
    
    @property
    def value(self) -> float:
        """δ_n = (n + √(n² + 4))/2."""
        n = self.index
        return (n + np.sqrt(n**2 + 4)) / 2
    
    @property
    def conjugate(self) -> float:
        """δ̄_n = (n - √(n² + 4))/2 = -1/δ_n."""
        n = self.index
        return (n - np.sqrt(n**2 + 4)) / 2
    
    @property
    def discriminant(self) -> int:
        """Δ = n² + 4, the discriminant of x² - nx - 1."""
        return self.index**2 + 4
    
    @property
    def norm(self) -> int:
        """N(δ_n) = δ_n · δ̄_n = -1."""
        return -1
    
    @property
    def trace(self) -> int:
        """Tr(δ_n) = δ_n + δ̄_n = n."""
        return self.index
    
    @property
    def minimal_polynomial(self) -> Tuple[int, int, int]:
        """Coefficients of x² - nx - 1."""
        return (1, -self.index, -1)
    
    @property
    def transfer_matrix(self) -> NDArray[np.int64]:
        """
        M_n = [[n, 1], [1, 0]]
        δ_n is the dominant eigenvalue of M_n.
        """
        return np.array([[self.index, 1], [1, 0]], dtype=np.int64)
    
    def power(self, k: int) -> Tuple[int, int]:
        """
        Compute δ_n^k = a·δ_n + b in the basis {1, δ_n}.
        Returns (a, b) = (F_k^(n), F_{k-1}^(n)).
        """
        if k == 0:
            return (0, 1)  # δ_n^0 = 1
        if k < 0:
            # δ_n^{-k} = (-1)^k · δ̄_n^k since δ_n · δ̄_n = -1
            a, b = self.power(-k)
            if (-k) % 2 == 0:
                return (-a, b)  # δ̄_n^k = -a·δ_n + b for even k
            else:
                return (a, -b)
        
        # Use matrix exponentiation
        M = self.transfer_matrix
        result = np.linalg.matrix_power(M, k)
        # M^k = [[F_{k+1}, F_k], [F_k, F_{k-1}]]
        F_k = int(result[0, 1])
        F_k_minus_1 = int(result[1, 1])
        return (F_k, F_k_minus_1)
    
    def power_value(self, k: int) -> float:
        """Numerical value of δ_n^k."""
        a, b = self.power(k)
        return a * self.value + b
    
    def continued_fraction_coefficients(self, length: int) -> List[int]:
        """
        δ_n = [n; n, n, n, ...] (purely periodic).
        """
        return [self.index] * length
    
    def __float__(self) -> float:
        return self.value
    
    def __repr__(self) -> str:
        return f"MetallicMean(n={self.index}, δ={self.value:.6f})"


# ═══════════════════════════════════════════════════════════════════════════════
# GENERALIZED FIBONACCI SEQUENCE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GeneralizedFibonacci:
    """
    Generalized Fibonacci sequence F_k^(n).
    
    Recurrence:
        F_0^(n) = 0
        F_1^(n) = 1
        F_{k+1}^(n) = n·F_k^(n) + F_{k-1}^(n)
    
    Properties:
        - F_k^(n) → δ_n^k / √(n² + 4) as k → ∞
        - F_{k+1}^(n) / F_k^(n) → δ_n
        - δ_n^k = F_k^(n)·δ_n + F_{k-1}^(n)
    
    Special cases:
        n=1: Classical Fibonacci (1, 1, 2, 3, 5, 8, ...)
        n=2: Pell numbers (1, 2, 5, 12, 29, ...)
    """
    index: int  # n
    _cache: Dict[int, int] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        self._cache[0] = 0
        self._cache[1] = 1
    
    def __getitem__(self, k: int) -> int:
        """F_k^(n)."""
        if k in self._cache:
            return self._cache[k]
        
        if k < 0:
            # F_{-k}^(n) = (-1)^{k+1} F_k^(n)
            return ((-1) ** (k + 1)) * self[abs(k)]
        
        # Use matrix exponentiation for large k
        if k > 100:
            M = np.array([[self.index, 1], [1, 0]], dtype=np.int64)
            result = np.linalg.matrix_power(M, k)
            val = int(result[0, 1])
            self._cache[k] = val
            return val
        
        # Build up cache
        if k - 1 not in self._cache:
            self[k - 1]
        if k - 2 not in self._cache:
            self[k - 2]
        
        val = self.index * self._cache[k - 1] + self._cache[k - 2]
        self._cache[k] = val
        return val
    
    def ratio(self, k: int) -> float:
        """F_{k+1}^(n) / F_k^(n), converges to δ_n."""
        if self[k] == 0:
            return float('inf')
        return self[k + 1] / self[k]
    
    def sequence(self, length: int) -> List[int]:
        """Generate sequence F_0, F_1, ..., F_{length-1}."""
        return [self[k] for k in range(length)]
    
    def binet_approximation(self, k: int) -> float:
        """
        Binet formula approximation.
        F_k^(n) ≈ δ_n^k / √(n² + 4)
        """
        delta = MetallicMean(self.index)
        return delta.value ** k / np.sqrt(self.index**2 + 4)


# ═══════════════════════════════════════════════════════════════════════════════
# GENERALIZED LUCAS SEQUENCE  
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GeneralizedLucas:
    """
    Generalized Lucas sequence L_k^(n).
    
    Recurrence:
        L_0^(n) = 2
        L_1^(n) = n
        L_{k+1}^(n) = n·L_k^(n) + L_{k-1}^(n)
    
    Properties:
        - L_k^(n) = δ_n^k + δ̄_n^k (trace of k-th power)
        - L_k^(n)² - (n² + 4)·F_k^(n)² = 4·(-1)^k
    
    Special cases:
        n=1: Classical Lucas (2, 1, 3, 4, 7, 11, ...)
        n=2: Companion Pell-Lucas (2, 2, 6, 14, 34, ...)
    """
    index: int  # n
    _cache: Dict[int, int] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        self._cache[0] = 2
        self._cache[1] = self.index
    
    def __getitem__(self, k: int) -> int:
        """L_k^(n)."""
        if k in self._cache:
            return self._cache[k]
        
        if k < 0:
            # L_{-k}^(n) = (-1)^k L_k^(n)
            return ((-1) ** k) * self[abs(k)]
        
        # Build up cache
        if k - 1 not in self._cache:
            self[k - 1]
        if k - 2 not in self._cache:
            self[k - 2]
        
        val = self.index * self._cache[k - 1] + self._cache[k - 2]
        self._cache[k] = val
        return val
    
    def sequence(self, length: int) -> List[int]:
        """Generate sequence L_0, L_1, ..., L_{length-1}."""
        return [self[k] for k in range(length)]
    
    def trace_identity(self, k: int) -> float:
        """
        Verify L_k^(n) = δ_n^k + δ̄_n^k.
        """
        delta = MetallicMean(self.index)
        return delta.value ** k + delta.conjugate ** k


# ═══════════════════════════════════════════════════════════════════════════════
# CONTINUED FRACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContinuedFraction:
    """
    Continued fraction representation and convergent computation.
    
    [a_0; a_1, a_2, ...] = a_0 + 1/(a_1 + 1/(a_2 + ...))
    
    Convergents p_k/q_k satisfy:
        p_{k+1} = a_{k+1}·p_k + p_{k-1}
        q_{k+1} = a_{k+1}·q_k + q_{k-1}
    """
    coefficients: List[int]
    
    @classmethod
    def from_float(cls, x: float, max_terms: int = 20, 
                   tol: float = 1e-12) -> 'ContinuedFraction':
        """Convert float to continued fraction."""
        coeffs = []
        remaining = x
        
        for _ in range(max_terms):
            a = int(np.floor(remaining))
            coeffs.append(a)
            
            frac = remaining - a
            if abs(frac) < tol:
                break
            
            remaining = 1 / frac
        
        return cls(coefficients=coeffs)
    
    @classmethod
    def from_sqrt(cls, n: int, max_terms: int = 50) -> 'ContinuedFraction':
        """
        Continued fraction of √n (for non-square n).
        √n = [a_0; a_1, a_2, ..., a_h] with periodic tail.
        """
        if n <= 0:
            raise ValueError(f"n must be positive, got {n}")
        
        sqrt_n = int(np.sqrt(n))
        if sqrt_n * sqrt_n == n:
            return cls(coefficients=[sqrt_n])  # Perfect square
        
        coeffs = [sqrt_n]
        m, d, a = 0, 1, sqrt_n
        
        seen = {}
        for _ in range(max_terms):
            m = d * a - m
            d = (n - m * m) // d
            a = (sqrt_n + m) // d
            
            state = (m, d)
            if state in seen:
                break
            seen[state] = len(coeffs)
            coeffs.append(a)
        
        return cls(coefficients=coeffs)
    
    @classmethod
    def periodic(cls, a0: int, period: List[int], repetitions: int = 10) -> 'ContinuedFraction':
        """Create periodic continued fraction [a_0; period, period, ...]."""
        coeffs = [a0] + period * repetitions
        return cls(coefficients=coeffs)
    
    @property
    def length(self) -> int:
        return len(self.coefficients)
    
    def convergent(self, k: int) -> Tuple[int, int]:
        """
        Compute k-th convergent p_k/q_k.
        Returns (p_k, q_k).
        """
        if k < 0 or k >= self.length:
            raise ValueError(f"k must be in [0, {self.length-1}]")
        
        # Initial values
        p_prev, p_curr = 1, self.coefficients[0]
        q_prev, q_curr = 0, 1
        
        for i in range(1, k + 1):
            a_i = self.coefficients[i]
            p_prev, p_curr = p_curr, a_i * p_curr + p_prev
            q_prev, q_curr = q_curr, a_i * q_curr + q_prev
        
        return (p_curr, q_curr)
    
    def convergents(self) -> List[Tuple[int, int]]:
        """All convergents."""
        return [self.convergent(k) for k in range(self.length)]
    
    def value(self) -> float:
        """Evaluate continued fraction to float."""
        result = 0.0
        for a in reversed(self.coefficients):
            if result == 0:
                result = float(a)
            else:
                result = a + 1 / result
        return result
    
    def as_fraction(self) -> Fraction:
        """Evaluate as exact fraction (using last convergent)."""
        p, q = self.convergent(self.length - 1)
        return Fraction(p, q)
    
    def __repr__(self) -> str:
        if len(self.coefficients) <= 5:
            return f"CF[{self.coefficients[0]}; {', '.join(map(str, self.coefficients[1:]))}]"
        return f"CF[{self.coefficients[0]}; {', '.join(map(str, self.coefficients[1:4]))}, ... ({self.length} terms)]"


# ═══════════════════════════════════════════════════════════════════════════════
# METALLIC POWER ENGINE - EXACT ARITHMETIC
# ═══════════════════════════════════════════════════════════════════════════════

class MetallicPowerEngine:
    """
    Engine for exact computation of metallic powers using integer arithmetic.
    
    Key insight: δ_n^k lives in ℤ[δ_n] = {a + b·δ_n : a,b ∈ ℤ}.
    All operations reduce to integer operations on pairs (a, b).
    """
    
    def __init__(self, index: int):
        """
        Initialize engine for metallic mean δ_n.
        
        Args:
            index: The metallic index n
        """
        self.index = index
        self.fib = GeneralizedFibonacci(index)
        self.luc = GeneralizedLucas(index)
        self.delta = MetallicMean(index)
    
    def power_coefficients(self, k: int) -> Tuple[int, int]:
        """
        Compute coefficients for δ_n^k = a·δ_n + b.
        Returns (a, b) = (F_k^(n), F_{k-1}^(n)).
        """
        return self.delta.power(k)
    
    def multiply(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[int, int]:
        """
        Multiply two elements of ℤ[δ_n].
        (a1·δ_n + b1)(a2·δ_n + b2) = ...
        
        Using δ_n² = n·δ_n + 1:
        = a1·a2·δ_n² + (a1·b2 + a2·b1)·δ_n + b1·b2
        = a1·a2·(n·δ_n + 1) + (a1·b2 + a2·b1)·δ_n + b1·b2
        = (n·a1·a2 + a1·b2 + a2·b1)·δ_n + (a1·a2 + b1·b2)
        """
        a1, b1 = p1
        a2, b2 = p2
        n = self.index
        
        new_a = n * a1 * a2 + a1 * b2 + a2 * b1
        new_b = a1 * a2 + b1 * b2
        
        return (new_a, new_b)
    
    def add(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[int, int]:
        """Add two elements of ℤ[δ_n]."""
        return (p1[0] + p2[0], p1[1] + p2[1])
    
    def negate(self, p: Tuple[int, int]) -> Tuple[int, int]:
        """Negate element."""
        return (-p[0], -p[1])
    
    def conjugate(self, p: Tuple[int, int]) -> Tuple[int, int]:
        """
        Conjugate: a·δ_n + b ↦ a·δ̄_n + b = -a/δ_n + b
        Since δ̄_n = -1/δ_n and using δ_n·δ̄_n = -1:
        a·δ̄_n + b = -a·(1/δ_n) + b
        
        In the basis {1, δ_n}, the conjugate of (a, b) is:
        (-a, b + n·a)  [using δ̄_n = n - δ_n]
        """
        a, b = p
        return (-a, b + self.index * a)
    
    def norm(self, p: Tuple[int, int]) -> int:
        """
        Norm: N(a·δ_n + b) = (a·δ_n + b)(a·δ̄_n + b)
        = a²·δ_n·δ̄_n + ab(δ_n + δ̄_n) + b²
        = -a² + n·ab + b²
        """
        a, b = p
        return -a**2 + self.index * a * b + b**2
    
    def to_float(self, p: Tuple[int, int]) -> float:
        """Convert to float: a·δ_n + b."""
        a, b = p
        return a * self.delta.value + b
    
    def inverse(self, p: Tuple[int, int]) -> Tuple[float, float]:
        """
        Multiplicative inverse (may not be in ℤ[δ_n]).
        1/(a·δ_n + b) = conjugate / norm
        """
        conj = self.conjugate(p)
        n = self.norm(p)
        if n == 0:
            raise ZeroDivisionError("Element has zero norm")
        return (conj[0] / n, conj[1] / n)
    
    def power_fast(self, k: int) -> Tuple[int, int]:
        """
        Fast power computation using binary exponentiation.
        Returns coefficients for δ_n^k.
        """
        if k == 0:
            return (0, 1)  # 1
        if k < 0:
            # For negative powers, use conjugate property
            pos = self.power_fast(-k)
            # δ_n^{-k} = (-1)^k · (something involving conjugate)
            # This gets complicated for non-unit norms
            raise NotImplementedError("Negative powers require field arithmetic")
        
        result = (0, 1)  # 1
        base = (1, 0)    # δ_n
        
        while k > 0:
            if k % 2 == 1:
                result = self.multiply(result, base)
            base = self.multiply(base, base)
            k //= 2
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# CONVERGENT LADDER - RATIONAL APPROXIMATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ConvergentLadder:
    """
    Ladder of rational approximations to a metallic mean.
    
    Convergents p_k/q_k satisfy:
        |δ_n - p_k/q_k| < 1/q_k²
    
    The convergents form the "best rational approximations" to δ_n.
    """
    metallic: MetallicMean
    fib: GeneralizedFibonacci = field(init=False)
    
    def __post_init__(self):
        self.fib = GeneralizedFibonacci(self.metallic.index)
    
    def convergent(self, k: int) -> Tuple[int, int]:
        """
        k-th convergent p_k/q_k to δ_n.
        p_k = F_{k+1}^(n), q_k = F_k^(n)
        """
        p = self.fib[k + 1]
        q = self.fib[k]
        return (p, q)
    
    def convergent_value(self, k: int) -> float:
        """Numerical value p_k/q_k."""
        p, q = self.convergent(k)
        if q == 0:
            return float('inf')
        return p / q
    
    def error(self, k: int) -> float:
        """|δ_n - p_k/q_k|."""
        return abs(self.metallic.value - self.convergent_value(k))
    
    def error_bound(self, k: int) -> float:
        """Upper bound 1/q_k²."""
        _, q = self.convergent(k)
        if q == 0:
            return float('inf')
        return 1 / (q ** 2)
    
    def ladder(self, length: int) -> List[Dict]:
        """Generate ladder of convergents with errors."""
        results = []
        for k in range(length):
            p, q = self.convergent(k)
            val = self.convergent_value(k)
            err = self.error(k)
            results.append({
                'k': k,
                'p': p,
                'q': q,
                'value': val,
                'error': err,
                'bound': self.error_bound(k)
            })
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIAL METALLIC RATIOS
# ═══════════════════════════════════════════════════════════════════════════════

class SpecialMetallics:
    """Library of named metallic ratios."""
    
    @staticmethod
    def golden() -> MetallicMean:
        """φ = (1 + √5)/2 ≈ 1.618, n=1."""
        return MetallicMean(1)
    
    @staticmethod
    def silver() -> MetallicMean:
        """δ_s = 1 + √2 ≈ 2.414, n=2."""
        return MetallicMean(2)
    
    @staticmethod
    def bronze() -> MetallicMean:
        """(3 + √13)/2 ≈ 3.303, n=3."""
        return MetallicMean(3)
    
    @staticmethod
    def copper() -> MetallicMean:
        """(4 + √20)/2 = 2 + √5 ≈ 4.236, n=4."""
        return MetallicMean(4)
    
    @staticmethod
    def nickel() -> MetallicMean:
        """(5 + √29)/2 ≈ 5.193, n=5."""
        return MetallicMean(5)
    
    @staticmethod
    def fibonacci_sequence(length: int = 20) -> List[int]:
        """Classical Fibonacci: F_k^(1)."""
        return GeneralizedFibonacci(1).sequence(length)
    
    @staticmethod
    def pell_numbers(length: int = 20) -> List[int]:
        """Pell numbers: F_k^(2)."""
        return GeneralizedFibonacci(2).sequence(length)
    
    @staticmethod
    def lucas_numbers(length: int = 20) -> List[int]:
        """Classical Lucas: L_k^(1)."""
        return GeneralizedLucas(1).sequence(length)


# ═══════════════════════════════════════════════════════════════════════════════
# QUADRATIC FIELD ARITHMETIC
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QuadraticInteger:
    """
    Element of ℤ[√D] represented as a + b√D.
    
    When D = n² + 4, this contains the metallic mean δ_n.
    """
    a: int
    b: int
    D: int  # Discriminant
    
    @property
    def value(self) -> float:
        """a + b√D."""
        return self.a + self.b * np.sqrt(self.D)
    
    @property
    def conjugate_value(self) -> float:
        """a - b√D."""
        return self.a - self.b * np.sqrt(self.D)
    
    @property
    def norm(self) -> int:
        """N(α) = a² - D·b²."""
        return self.a**2 - self.D * self.b**2
    
    @property
    def trace(self) -> int:
        """Tr(α) = 2a."""
        return 2 * self.a
    
    def __add__(self, other: 'QuadraticInteger') -> 'QuadraticInteger':
        if self.D != other.D:
            raise ValueError("Discriminants must match")
        return QuadraticInteger(self.a + other.a, self.b + other.b, self.D)
    
    def __mul__(self, other: 'QuadraticInteger') -> 'QuadraticInteger':
        if self.D != other.D:
            raise ValueError("Discriminants must match")
        # (a + b√D)(c + d√D) = (ac + bd·D) + (ad + bc)√D
        new_a = self.a * other.a + self.b * other.b * self.D
        new_b = self.a * other.b + self.b * other.a
        return QuadraticInteger(new_a, new_b, self.D)
    
    def __pow__(self, n: int) -> 'QuadraticInteger':
        if n < 0:
            raise ValueError("Negative powers not supported")
        if n == 0:
            return QuadraticInteger(1, 0, self.D)
        
        result = QuadraticInteger(1, 0, self.D)
        base = QuadraticInteger(self.a, self.b, self.D)
        
        while n > 0:
            if n % 2 == 1:
                result = result * base
            base = base * base
            n //= 2
        
        return result
    
    def __repr__(self) -> str:
        sign = '+' if self.b >= 0 else '-'
        return f"{self.a} {sign} {abs(self.b)}√{self.D}"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def metallic_mean(n: int) -> float:
    """Quick access to δ_n value."""
    return MetallicMean(n).value


def fibonacci(k: int, n: int = 1) -> int:
    """F_k^(n), generalized Fibonacci."""
    return GeneralizedFibonacci(n)[k]


def lucas(k: int, n: int = 1) -> int:
    """L_k^(n), generalized Lucas."""
    return GeneralizedLucas(n)[k]


def golden_ratio() -> float:
    """φ = (1 + √5)/2."""
    return SpecialMetallics.golden().value


def silver_ratio() -> float:
    """δ_s = 1 + √2."""
    return SpecialMetallics.silver().value


def continued_fraction_sqrt(n: int, terms: int = 20) -> List[int]:
    """Continued fraction coefficients of √n."""
    cf = ContinuedFraction.from_sqrt(n, max_terms=terms)
    return cf.coefficients


def metallic_power(n: int, k: int) -> Tuple[int, int]:
    """
    Compute δ_n^k = a·δ_n + b.
    Returns (a, b).
    """
    return MetallicMean(n).power(k)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core classes
    'MetallicMean',
    'GeneralizedFibonacci',
    'GeneralizedLucas',
    'ContinuedFraction',
    'MetallicPowerEngine',
    'ConvergentLadder',
    'SpecialMetallics',
    'QuadraticInteger',
    
    # Convenience functions
    'metallic_mean',
    'fibonacci',
    'lucas',
    'golden_ratio',
    'silver_ratio',
    'continued_fraction_sqrt',
    'metallic_power',
]
