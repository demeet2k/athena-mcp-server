"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         MODULAR FORMS MODULE                                 ║
║                                                                              ║
║  Eisenstein Series, j-Invariant, and Modular Transformations                 ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Modular forms are functions on the upper half-plane ℍ that transform     ║
║    nicely under PSL(2,ℤ). They encode deep arithmetic information and       ║
║    connect to the gateway algebra through the modular group action.         ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Eisenstein series: G_k(τ) = Σ' (m + nτ)^{-k}                           ║
║    - Discriminant: Δ = g₂³ - 27g₃²                                          ║
║    - j-invariant: j = 1728 g₂³/Δ                                            ║
║    - Dedekind eta: η(τ) = q^{1/24} Π(1 - q^n)                               ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - PSL(2,ℤ) = modular group = gateway group                               ║
║    - Fundamental domain = gateway chart boundaries                          ║
║    - q-series = fold ladder structure                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# q-SERIES UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def nome(tau: complex) -> complex:
    """
    The nome q = e^{2πiτ}.
    
    For τ in upper half-plane, |q| < 1.
    """
    return np.exp(2j * np.pi * tau)


def inverse_nome(q: complex) -> complex:
    """
    Recover τ from q.
    
    τ = log(q)/(2πi)
    """
    return np.log(q) / (2j * np.pi)


# ═══════════════════════════════════════════════════════════════════════════════
# EISENSTEIN SERIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EisensteinSeries:
    """
    Eisenstein series G_k(τ) for even k ≥ 4.
    
    G_k(τ) = Σ'_{m,n} (m + nτ)^{-k}
    
    where the sum is over all (m,n) ≠ (0,0).
    
    Normalized Eisenstein: E_k = G_k / (2ζ(k))
    """
    weight: int  # Must be even ≥ 4
    terms: int = 100  # Number of q-series terms
    
    def __post_init__(self):
        if self.weight < 4 or self.weight % 2 != 0:
            raise ValueError(f"Weight must be even ≥ 4, got {self.weight}")
        self._precompute_bernoulli()
    
    def _precompute_bernoulli(self):
        """Precompute Bernoulli number B_k for normalization."""
        # B_4 = -1/30, B_6 = 1/42, B_8 = -1/30, ...
        bernoulli = {
            4: -1/30, 6: 1/42, 8: -1/30, 10: 5/66,
            12: -691/2730, 14: 7/6
        }
        self.bernoulli_k = bernoulli.get(self.weight, 0)
    
    def sigma(self, n: int, k: int) -> int:
        """
        Divisor function σ_k(n) = Σ_{d|n} d^k.
        """
        if n <= 0:
            return 0
        total = 0
        for d in range(1, n + 1):
            if n % d == 0:
                total += d ** k
        return total
    
    def q_expansion(self, n_terms: int = None) -> NDArray[np.float64]:
        """
        q-expansion coefficients of normalized E_k.
        
        E_k(τ) = 1 - (2k/B_k) Σ_{n≥1} σ_{k-1}(n) q^n
        """
        if n_terms is None:
            n_terms = self.terms
        
        k = self.weight
        coeffs = np.zeros(n_terms)
        coeffs[0] = 1.0
        
        if abs(self.bernoulli_k) > 1e-15:
            factor = -2 * k / self.bernoulli_k
            for n in range(1, n_terms):
                coeffs[n] = factor * self.sigma(n, k - 1)
        
        return coeffs
    
    def evaluate(self, tau: complex) -> complex:
        """
        Evaluate E_k(τ) using q-expansion.
        """
        if tau.imag <= 0:
            raise ValueError("τ must be in upper half-plane")
        
        q = nome(tau)
        coeffs = self.q_expansion()
        
        result = coeffs[0]
        q_power = q
        for n in range(1, len(coeffs)):
            result += coeffs[n] * q_power
            q_power *= q
        
        return result


@dataclass
class EisensteinE4E6:
    """
    The fundamental Eisenstein series E_4 and E_6.
    
    All modular forms for SL(2,ℤ) are polynomials in E_4 and E_6.
    """
    terms: int = 100
    
    def __post_init__(self):
        self.E4 = EisensteinSeries(4, self.terms)
        self.E6 = EisensteinSeries(6, self.terms)
    
    def g2(self, tau: complex) -> complex:
        """
        Weierstrass invariant g₂ = (4π⁴/3) E_4.
        """
        return (4 * np.pi**4 / 3) * self.E4.evaluate(tau)
    
    def g3(self, tau: complex) -> complex:
        """
        Weierstrass invariant g₃ = (8π⁶/27) E_6.
        """
        return (8 * np.pi**6 / 27) * self.E6.evaluate(tau)
    
    def discriminant(self, tau: complex) -> complex:
        """
        Modular discriminant Δ = g₂³ - 27g₃².
        
        Also Δ = (2π)^{12} η^{24} where η is Dedekind eta.
        """
        g2 = self.g2(tau)
        g3 = self.g3(tau)
        return g2**3 - 27 * g3**2
    
    def j_invariant(self, tau: complex) -> complex:
        """
        j-invariant: j(τ) = 1728 g₂³/Δ.
        
        The j-invariant uniquely classifies elliptic curves
        and is a modular function (weight 0).
        """
        g2 = self.g2(tau)
        delta = self.discriminant(tau)
        
        if abs(delta) < 1e-50:
            return complex(float('inf'), 0)
        
        return 1728 * g2**3 / delta


# ═══════════════════════════════════════════════════════════════════════════════
# DEDEKIND ETA FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DedekindEta:
    """
    Dedekind eta function: η(τ) = q^{1/24} Π_{n=1}^∞ (1 - q^n)
    
    Weight 1/2 modular form. Transforms as:
        η(τ + 1) = e^{iπ/12} η(τ)
        η(-1/τ) = √(-iτ) η(τ)
    """
    terms: int = 100
    
    def evaluate(self, tau: complex) -> complex:
        """
        Evaluate η(τ).
        """
        if tau.imag <= 0:
            raise ValueError("τ must be in upper half-plane")
        
        q = nome(tau)
        
        # q^{1/24} factor
        result = np.exp(2j * np.pi * tau / 24)
        
        # Product
        q_power = q
        for n in range(1, self.terms):
            result *= (1 - q_power)
            q_power *= q
        
        return result
    
    def evaluate_24th_power(self, tau: complex) -> complex:
        """
        Evaluate η(τ)^{24} = Δ(τ)/(2π)^{12}.
        
        This is the Ramanujan tau function generating function.
        """
        eta = self.evaluate(tau)
        return eta ** 24


# ═══════════════════════════════════════════════════════════════════════════════
# MODULAR GROUP ELEMENTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ModularElement:
    """
    Element of PSL(2,ℤ), the modular group.
    
    Acts on τ ∈ ℍ as: τ ↦ (aτ + b)/(cτ + d)
    where ad - bc = 1 and a,b,c,d ∈ ℤ.
    """
    a: int
    b: int
    c: int
    d: int
    
    def __post_init__(self):
        det = self.a * self.d - self.b * self.c
        if det != 1:
            raise ValueError(f"Determinant must be 1, got {det}")
    
    def apply(self, tau: complex) -> complex:
        """Apply transformation to τ."""
        denom = self.c * tau + self.d
        if abs(denom) < 1e-15:
            return complex(float('inf'), 0)
        return (self.a * tau + self.b) / denom
    
    def compose(self, other: 'ModularElement') -> 'ModularElement':
        """Matrix multiplication."""
        return ModularElement(
            self.a * other.a + self.b * other.c,
            self.a * other.b + self.b * other.d,
            self.c * other.a + self.d * other.c,
            self.c * other.b + self.d * other.d
        )
    
    def inverse(self) -> 'ModularElement':
        """Inverse element."""
        return ModularElement(self.d, -self.b, -self.c, self.a)
    
    @classmethod
    def S(cls) -> 'ModularElement':
        """Generator S: τ ↦ -1/τ."""
        return cls(0, -1, 1, 0)
    
    @classmethod
    def T(cls) -> 'ModularElement':
        """Generator T: τ ↦ τ + 1."""
        return cls(1, 1, 0, 1)
    
    @classmethod
    def identity(cls) -> 'ModularElement':
        """Identity element."""
        return cls(1, 0, 0, 1)
    
    def word_in_ST(self) -> str:
        """
        Express as word in S and T (approximately).
        
        Uses continued fraction algorithm.
        """
        # This is a simplified version
        words = []
        M = ModularElement(self.a, self.b, self.c, self.d)
        
        for _ in range(50):  # Safety limit
            if M.c == 0:
                # Pure translation
                if M.b != 0:
                    words.append(f"T^{M.b}")
                break
            
            # Apply S to swap c,d with a,b
            words.append("S")
            M = ModularElement.S().compose(M)
            
            # Reduce via T
            if M.c != 0:
                k = M.a // M.c
                if k != 0:
                    words.append(f"T^{k}")
                    T_k = ModularElement(1, k, 0, 1)
                    M = T_k.inverse().compose(M)
        
        return " · ".join(reversed(words))


# ═══════════════════════════════════════════════════════════════════════════════
# MODULAR FORMS RING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ModularFormRing:
    """
    The ring of modular forms for SL(2,ℤ).
    
    M_* = ℂ[E_4, E_6]
    
    Dimension formula: dim M_k = floor(k/12) + 1 for k ≡ 2 (mod 12)
    """
    max_weight: int = 24
    terms: int = 100
    
    def __post_init__(self):
        self.eisenstein = EisensteinE4E6(self.terms)
    
    def dimension(self, k: int) -> int:
        """Dimension of M_k (space of weight-k modular forms)."""
        if k < 0 or k % 2 != 0:
            return 0
        if k == 0:
            return 1
        if k == 2:
            return 0
        
        # For k ≥ 4
        r = k % 12
        base = k // 12
        
        if r == 0:
            return base + 1
        elif r == 2:
            return base
        elif r == 4:
            return base + 1
        elif r == 6:
            return base + 1
        elif r == 8:
            return base + 1
        elif r == 10:
            return base + 1
        
        return 0
    
    def basis_exponents(self, k: int) -> List[Tuple[int, int]]:
        """
        Basis of M_k in terms of E_4^a E_6^b.
        
        Returns list of (a, b) such that 4a + 6b = k.
        """
        if k < 0 or k % 2 != 0:
            return []
        
        basis = []
        # 4a + 6b = k, so a = (k - 6b)/4
        for b in range(k // 6 + 1):
            if (k - 6 * b) % 4 == 0:
                a = (k - 6 * b) // 4
                basis.append((a, b))
        
        return basis
    
    def evaluate_monomial(self, tau: complex, a: int, b: int) -> complex:
        """Evaluate E_4^a E_6^b at τ."""
        e4 = self.eisenstein.E4.evaluate(tau)
        e6 = self.eisenstein.E6.evaluate(tau)
        return (e4 ** a) * (e6 ** b)


# ═══════════════════════════════════════════════════════════════════════════════
# THETA FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class JacobiTheta:
    """
    Jacobi theta functions θ_i(z, τ).
    
    θ_3(0, τ) = Σ q^{n²} (Jacobi theta)
    Related to partition function and lattice sums.
    """
    terms: int = 100
    
    def theta3(self, z: complex, tau: complex) -> complex:
        """
        θ_3(z, τ) = Σ_{n=-∞}^∞ q^{n²} e^{2πinz}
        
        where q = e^{πiτ}.
        """
        if tau.imag <= 0:
            raise ValueError("τ must be in upper half-plane")
        
        q = np.exp(1j * np.pi * tau)
        w = np.exp(2j * np.pi * z)
        
        result = 1.0  # n = 0 term
        
        q_n_sq = q  # q^{1²}
        w_n = w      # e^{2πi·1·z}
        w_neg_n = 1 / w
        
        for n in range(1, self.terms):
            # n and -n terms
            result += q_n_sq * (w_n + w_neg_n)
            
            # Update for next iteration
            q_n_sq *= q ** (2 * n + 1)  # q^{(n+1)²} = q^{n²} · q^{2n+1}
            w_n *= w
            w_neg_n /= w
        
        return result
    
    def theta3_at_zero(self, tau: complex) -> complex:
        """θ_3(0, τ) = Σ q^{n²}."""
        return self.theta3(0, tau)
    
    def theta2(self, z: complex, tau: complex) -> complex:
        """θ_2(z, τ) = Σ q^{(n+1/2)²} e^{2πi(n+1/2)z}."""
        if tau.imag <= 0:
            raise ValueError("τ must be in upper half-plane")
        
        q = np.exp(1j * np.pi * tau)
        
        result = 0.0
        
        for n in range(-self.terms, self.terms):
            m = n + 0.5
            term = q ** (m * m) * np.exp(2j * np.pi * m * z)
            result += term
        
        return result
    
    def theta4(self, z: complex, tau: complex) -> complex:
        """θ_4(z, τ) = Σ (-1)^n q^{n²} e^{2πinz}."""
        if tau.imag <= 0:
            raise ValueError("τ must be in upper half-plane")
        
        q = np.exp(1j * np.pi * tau)
        w = np.exp(2j * np.pi * z)
        
        result = 1.0  # n = 0
        
        q_n_sq = q
        w_n = w
        w_neg_n = 1 / w
        sign = -1
        
        for n in range(1, self.terms):
            result += sign * q_n_sq * (w_n + w_neg_n)
            sign *= -1
            q_n_sq *= q ** (2 * n + 1)
            w_n *= w
            w_neg_n /= w
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def j_invariant(tau: complex) -> complex:
    """Compute j-invariant at τ."""
    return EisensteinE4E6().j_invariant(tau)


def dedekind_eta(tau: complex) -> complex:
    """Compute Dedekind eta at τ."""
    return DedekindEta().evaluate(tau)


def eisenstein_E4(tau: complex) -> complex:
    """Evaluate E_4(τ)."""
    return EisensteinSeries(4).evaluate(tau)


def eisenstein_E6(tau: complex) -> complex:
    """Evaluate E_6(τ)."""
    return EisensteinSeries(6).evaluate(tau)


def modular_discriminant(tau: complex) -> complex:
    """Evaluate Δ(τ)."""
    return EisensteinE4E6().discriminant(tau)


def theta_function(tau: complex) -> complex:
    """Jacobi theta θ_3(0, τ)."""
    return JacobiTheta().theta3_at_zero(tau)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # q-series
    'nome',
    'inverse_nome',
    
    # Eisenstein
    'EisensteinSeries',
    'EisensteinE4E6',
    
    # Eta
    'DedekindEta',
    
    # Modular group
    'ModularElement',
    
    # Ring structure
    'ModularFormRing',
    
    # Theta
    'JacobiTheta',
    
    # Functions
    'j_invariant',
    'dedekind_eta',
    'eisenstein_E4',
    'eisenstein_E6',
    'modular_discriminant',
    'theta_function',
]
