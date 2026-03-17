"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CONTINUED FRACTIONS MODULE                                ║
║                                                                              ║
║  Rational Approximations, Convergents, and Pell Equations                    ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Continued fractions are the HEART of the gateway algebra.                ║
║    They encode the hyperbolic structure, solve Pell equations,              ║
║    and generate metallic means.                                             ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Simple CF: x = a₀ + 1/(a₁ + 1/(a₂ + ...))                             ║
║    - Convergents: p_n/q_n best rational approximations                      ║
║    - Quadratic irrationals: eventually periodic CFs                         ║
║    - Pell solutions: fundamental unit via CF of √D                          ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Gateway: T → CF expansion, rapidity → CF length                        ║
║    - Metallic means: δ_n = [n; n, n, n, ...]                               ║
║    - Hyperbolic: geodesic coding via CF                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Iterator, Union
from fractions import Fraction
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# CONTINUED FRACTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContinuedFraction:
    """
    Simple continued fraction [a₀; a₁, a₂, ...].
    
    x = a₀ + 1/(a₁ + 1/(a₂ + ...))
    
    Finite for rationals, infinite for irrationals.
    """
    coefficients: List[int]
    periodic_part: Optional[List[int]] = None  # For quadratic irrationals
    
    @property
    def is_finite(self) -> bool:
        return self.periodic_part is None
    
    @property
    def is_periodic(self) -> bool:
        return self.periodic_part is not None
    
    def __repr__(self) -> str:
        if self.is_finite:
            return f"[{'; '.join(map(str, self.coefficients))}]"
        else:
            prefix = ', '.join(map(str, self.coefficients))
            period = ', '.join(map(str, self.periodic_part))
            return f"[{self.coefficients[0]}; {prefix[2:]}, ̅{period}̅]"
    
    def evaluate(self, n_terms: Optional[int] = None) -> float:
        """Evaluate CF to given number of terms."""
        coeffs = self.coefficients[:]
        
        if self.is_periodic and n_terms:
            # Extend with periodic part
            while len(coeffs) < n_terms:
                coeffs.extend(self.periodic_part)
            coeffs = coeffs[:n_terms]
        
        if not coeffs:
            return 0.0
        
        # Evaluate from the end
        result = float(coeffs[-1])
        for a in reversed(coeffs[:-1]):
            if result != 0:
                result = a + 1.0 / result
            else:
                result = float('inf')
        
        return result
    
    def convergent(self, n: int) -> Fraction:
        """
        Compute n-th convergent p_n/q_n.
        
        Uses recurrence:
            p_n = a_n p_{n-1} + p_{n-2}
            q_n = a_n q_{n-1} + q_{n-2}
        """
        coeffs = self._get_coeffs(n + 1)
        
        # p_{-2} = 0, p_{-1} = 1
        # q_{-2} = 1, q_{-1} = 0
        p_prev2, p_prev1 = 0, 1
        q_prev2, q_prev1 = 1, 0
        
        for i, a in enumerate(coeffs[:n + 1]):
            p = a * p_prev1 + p_prev2
            q = a * q_prev1 + q_prev2
            
            p_prev2, p_prev1 = p_prev1, p
            q_prev2, q_prev1 = q_prev1, q
        
        return Fraction(p, q)
    
    def _get_coeffs(self, n: int) -> List[int]:
        """Get first n coefficients, extending periodic part if needed."""
        coeffs = self.coefficients[:]
        if self.is_periodic:
            while len(coeffs) < n:
                coeffs.extend(self.periodic_part)
        return coeffs[:n]
    
    def convergents(self, max_n: int = 10) -> Iterator[Fraction]:
        """Generate convergents."""
        for n in range(max_n):
            yield self.convergent(n)
    
    def best_approximations(self, max_denom: int) -> List[Fraction]:
        """Best rational approximations with denominator ≤ max_denom."""
        result = []
        for conv in self.convergents(100):
            if conv.denominator > max_denom:
                break
            result.append(conv)
        return result
    
    @classmethod
    def from_float(cls, x: float, max_terms: int = 20, 
                  tolerance: float = 1e-12) -> 'ContinuedFraction':
        """Compute CF expansion of a float."""
        coeffs = []
        remaining = x
        
        for _ in range(max_terms):
            a = int(np.floor(remaining))
            coeffs.append(a)
            
            frac = remaining - a
            if abs(frac) < tolerance:
                break
            
            remaining = 1.0 / frac
        
        return cls(coeffs)
    
    @classmethod
    def from_fraction(cls, frac: Fraction) -> 'ContinuedFraction':
        """Compute CF expansion of a rational."""
        coeffs = []
        p, q = frac.numerator, frac.denominator
        
        while q != 0:
            a = p // q
            coeffs.append(a)
            p, q = q, p - a * q
        
        return cls(coeffs)
    
    @classmethod
    def from_sqrt(cls, D: int, max_period: int = 100) -> 'ContinuedFraction':
        """
        CF expansion of √D.
        
        √D = [a₀; a₁, a₂, ..., a_k] where period = (a₁, ..., a_k) with a_k = 2a₀.
        """
        if D < 0:
            raise ValueError("D must be non-negative")
        
        a0 = int(np.floor(np.sqrt(D)))
        
        # Check if perfect square
        if a0 * a0 == D:
            return cls([a0])
        
        # Find periodic part using standard algorithm
        coeffs = [a0]
        
        m, d, a = 0, 1, a0
        seen = {}
        
        for _ in range(max_period):
            m = d * a - m
            d = (D - m * m) // d
            a = (a0 + m) // d
            
            state = (m, d)
            if state in seen:
                # Found period - extract it
                period_start = seen[state]
                period = coeffs[period_start:]
                coeffs = coeffs[:period_start]
                return cls(coeffs, period)
            
            seen[state] = len(coeffs)
            coeffs.append(a)
        
        # If no period found in max iterations, return what we have
        return cls(coeffs, None)
    
    @classmethod
    def metallic_mean(cls, n: int) -> 'ContinuedFraction':
        """
        Metallic mean δ_n = [n; n, n, n, ...].
        
        δ_n = (n + √(n² + 4))/2
        """
        return cls([n], [n])


# ═══════════════════════════════════════════════════════════════════════════════
# PELL EQUATION SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PellSolution:
    """Solution (x, y) to Pell equation x² - Dy² = ±1."""
    x: int
    y: int
    D: int
    negative_one: bool = False  # True if x² - Dy² = -1
    
    def verify(self) -> bool:
        """Verify this is indeed a solution."""
        target = -1 if self.negative_one else 1
        return self.x**2 - self.D * self.y**2 == target
    
    def __repr__(self) -> str:
        sign = "-1" if self.negative_one else "1"
        return f"({self.x}, {self.y}): x² - {self.D}y² = {sign}"


@dataclass
class PellEquation:
    """
    Pell equation x² - Dy² = 1.
    
    Fundamental solution via continued fraction of √D.
    """
    D: int
    
    def __post_init__(self):
        # Check D is not a perfect square
        sqrt_D = int(np.sqrt(self.D))
        if sqrt_D * sqrt_D == self.D:
            raise ValueError(f"D = {self.D} is a perfect square")
    
    def fundamental_solution(self) -> PellSolution:
        """
        Find fundamental solution using CF of √D.
        
        The fundamental solution (x₁, y₁) is the smallest positive solution.
        """
        cf = ContinuedFraction.from_sqrt(self.D)
        
        if cf.periodic_part is None:
            raise ValueError("Expected periodic CF for √D")
        
        period_len = len(cf.periodic_part)
        
        # Check convergents until we find a solution
        for n in range(1, 200):
            conv = cf.convergent(n)
            x, y = conv.numerator, conv.denominator
            
            val = x * x - self.D * y * y
            if val == 1:
                return PellSolution(x, y, self.D, False)
            elif val == -1:
                # x² - Dy² = -1 solution; (x, y)² gives x² - Dy² = 1
                return PellSolution(x, y, self.D, True)
        
        raise RuntimeError("Could not find fundamental solution")
    
    def solutions(self, max_count: int = 10) -> Iterator[PellSolution]:
        """Generate solutions starting from fundamental."""
        fund = self.fundamental_solution()
        x1, y1 = fund.x, fund.y
        
        # If fundamental gives -1, we need to square it
        if fund.negative_one:
            x1 = fund.x**2 + self.D * fund.y**2
            y1 = 2 * fund.x * fund.y
        
        x, y = x1, y1
        for _ in range(max_count):
            yield PellSolution(x, y, self.D)
            # Next solution: (x + y√D)^{n+1} = (x_n + y_n√D)(x_1 + y_1√D)
            x_new = x * x1 + self.D * y * y1
            y_new = x * y1 + y * x1
            x, y = x_new, y_new
    
    def fundamental_unit(self) -> Tuple[int, int]:
        """
        Fundamental unit ε = x + y√D of ℤ[√D].
        """
        fund = self.fundamental_solution()
        if fund.negative_one:
            # ε = x + y√D, ε² has norm 1
            return fund.x, fund.y
        return fund.x, fund.y
    
    def regulator(self) -> float:
        """Regulator R = log(ε) where ε is fundamental unit."""
        x, y = self.fundamental_unit()
        epsilon = x + y * np.sqrt(self.D)
        return np.log(epsilon)


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY-CF BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewayCFBridge:
    """
    Deep connection between gateway algebra and continued fractions.
    
    The gateway discriminant A determines the CF structure.
    """
    
    @staticmethod
    def gateway_to_cf(T: float) -> ContinuedFraction:
        """
        Map gateway parameter T to continued fraction.
        
        Uses: T = tanh(α) where α is CF-related.
        """
        if abs(T) >= 1:
            raise ValueError("|T| must be < 1")
        
        # α = arctanh(T)
        alpha = np.arctanh(T)
        return ContinuedFraction.from_float(alpha)
    
    @staticmethod
    def metallic_as_gateway(n: int) -> Tuple[float, float]:
        """
        Express metallic mean as gateway state.
        
        δ_n = (n + √(n² + 4))/2
        T = tanh(log(δ_n))
        
        Returns (T, A) where A = n² + 4 is discriminant.
        """
        A = n * n + 4
        delta_n = (n + np.sqrt(A)) / 2
        T = np.tanh(np.log(delta_n))
        return T, float(A)
    
    @staticmethod
    def cf_to_matrix_product(cf: ContinuedFraction, n: int
                            ) -> NDArray[np.float64]:
        """
        Express CF convergent as matrix product.
        
        p_n/q_n corresponds to product of [[a_i, 1], [1, 0]] matrices.
        """
        coeffs = cf._get_coeffs(n)
        
        result = np.eye(2)
        for a in coeffs:
            M = np.array([[a, 1], [1, 0]], dtype=np.float64)
            result = result @ M
        
        return result
    
    @staticmethod
    def hyperbolic_coding(geodesic_word: str) -> ContinuedFraction:
        """
        Geodesic word (L/R) to continued fraction.
        
        L = left, R = right in cutting sequence.
        """
        coeffs = []
        current_count = 0
        current_char = geodesic_word[0] if geodesic_word else 'L'
        
        for c in geodesic_word:
            if c == current_char:
                current_count += 1
            else:
                coeffs.append(current_count)
                current_count = 1
                current_char = c
        
        if current_count > 0:
            coeffs.append(current_count)
        
        return ContinuedFraction(coeffs if coeffs else [0])


# ═══════════════════════════════════════════════════════════════════════════════
# DIOPHANTINE APPROXIMATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DiophantineApproximation:
    """
    Diophantine approximation via continued fractions.
    """
    
    @staticmethod
    def best_rational(x: float, max_denom: int) -> Fraction:
        """Best rational approximation with denominator ≤ max_denom."""
        cf = ContinuedFraction.from_float(x)
        
        best = Fraction(0, 1)
        best_error = abs(x)
        
        for conv in cf.convergents(100):
            if conv.denominator > max_denom:
                break
            error = abs(x - float(conv))
            if error < best_error:
                best_error = error
                best = conv
        
        return best
    
    @staticmethod
    def hurwitz_constant() -> float:
        """
        Hurwitz constant √5.
        
        For any irrational x, infinitely many p/q satisfy:
        |x - p/q| < 1/(√5 · q²)
        """
        return np.sqrt(5)
    
    @staticmethod
    def markov_spectrum_first() -> List[float]:
        """First few values of Markov spectrum."""
        return [
            np.sqrt(5),           # Golden ratio
            2 * np.sqrt(2),       # Silver ratio
            np.sqrt(221) / 5,     # Third Markov number
        ]
    
    @staticmethod
    def irrationality_measure(x: float, p: int, q: int) -> float:
        """
        Compute |x - p/q| · q².
        
        For irrationals, infinitely many (p, q) give this < 1/√5.
        """
        return abs(x - p / q) * q * q


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def continued_fraction(x: Union[float, Fraction]) -> ContinuedFraction:
    """Compute continued fraction expansion."""
    if isinstance(x, Fraction):
        return ContinuedFraction.from_fraction(x)
    return ContinuedFraction.from_float(x)


def sqrt_cf(D: int) -> ContinuedFraction:
    """Continued fraction of √D."""
    return ContinuedFraction.from_sqrt(D)


def metallic_cf(n: int) -> ContinuedFraction:
    """Continued fraction of metallic mean δ_n."""
    return ContinuedFraction.metallic_mean(n)


def solve_pell(D: int) -> PellSolution:
    """Solve Pell equation x² - Dy² = 1."""
    return PellEquation(D).fundamental_solution()


def convergent(cf: ContinuedFraction, n: int) -> Fraction:
    """Get n-th convergent of continued fraction."""
    return cf.convergent(n)


def best_rational_approximation(x: float, max_denom: int) -> Fraction:
    """Best rational approximation to x."""
    return DiophantineApproximation.best_rational(x, max_denom)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core
    'ContinuedFraction',
    
    # Pell
    'PellSolution',
    'PellEquation',
    
    # Bridge
    'GatewayCFBridge',
    
    # Approximation
    'DiophantineApproximation',
    
    # Functions
    'continued_fraction',
    'sqrt_cf',
    'metallic_cf',
    'solve_pell',
    'convergent',
    'best_rational_approximation',
]
