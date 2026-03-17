"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ALGEBRAIC K-THEORY MODULE                             ║
║                                                                              ║
║  Higher Algebraic Structures and the K-groups                                ║
║                                                                              ║
║  Core Principle:                                                             ║
║    K-theory captures deep invariants of rings and spaces.                    ║
║    K₀ = Grothendieck group of projective modules                            ║
║    K₁ = GL(R)/E(R) - units modulo elementary matrices                       ║
║    Higher K-groups via Quillen's Q-construction                              ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Ψ-pole ↔ K-groups as hierarchical invariants                           ║
║    - D-pole ↔ Exact sequences as constraints                                ║
║    - C-pole ↔ Continuous K-theory (topological)                             ║
║    - Gateway ↔ K₂ and Steinberg symbols                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray
from fractions import Fraction


# ═══════════════════════════════════════════════════════════════════════════════
# GROTHENDIECK GROUP (K₀)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProjectiveModule:
    """
    Finitely generated projective module over a ring.
    
    Represented by its rank and additional torsion data.
    """
    rank: int
    ring_name: str = "Z"
    torsion_data: Optional[Dict[str, Any]] = None
    
    def __add__(self, other: 'ProjectiveModule') -> 'ProjectiveModule':
        """Direct sum of projective modules."""
        if self.ring_name != other.ring_name:
            raise ValueError("Modules must be over same ring")
        return ProjectiveModule(self.rank + other.rank, self.ring_name)
    
    def is_free(self) -> bool:
        """Check if module is free (no torsion)."""
        return self.torsion_data is None or len(self.torsion_data) == 0


@dataclass
class K0Element:
    """
    Element of K₀(R) - the Grothendieck group.
    
    Represented as formal difference [P] - [Q] of projective modules.
    """
    positive_rank: int  # rank of P
    negative_rank: int  # rank of Q
    ring_name: str = "Z"
    
    @property
    def virtual_rank(self) -> int:
        """Virtual rank = rank(P) - rank(Q)."""
        return self.positive_rank - self.negative_rank
    
    def __add__(self, other: 'K0Element') -> 'K0Element':
        return K0Element(
            self.positive_rank + other.positive_rank,
            self.negative_rank + other.negative_rank,
            self.ring_name
        )
    
    def __neg__(self) -> 'K0Element':
        return K0Element(self.negative_rank, self.positive_rank, self.ring_name)
    
    def __sub__(self, other: 'K0Element') -> 'K0Element':
        return self + (-other)
    
    def __eq__(self, other: 'K0Element') -> bool:
        return self.virtual_rank == other.virtual_rank
    
    @classmethod
    def from_module(cls, P: ProjectiveModule) -> 'K0Element':
        """Create K₀ element from projective module."""
        return cls(P.rank, 0, P.ring_name)


@dataclass
class GrothendieckGroup:
    """
    K₀(R) - the Grothendieck group of a ring.
    
    For R = ℤ: K₀(ℤ) ≅ ℤ (rank)
    For R = field: K₀(k) ≅ ℤ
    For R = Dedekind domain: K₀(R) ≅ ℤ ⊕ Cl(R)
    """
    ring_name: str
    rank_component: int = 0
    class_group_order: int = 1  # |Cl(R)|
    
    def element(self, virtual_rank: int) -> K0Element:
        """Create element with given virtual rank."""
        if virtual_rank >= 0:
            return K0Element(virtual_rank, 0, self.ring_name)
        else:
            return K0Element(0, -virtual_rank, self.ring_name)
    
    @classmethod
    def integers(cls) -> 'GrothendieckGroup':
        """K₀(ℤ) ≅ ℤ."""
        return cls("Z", class_group_order=1)
    
    @classmethod
    def field(cls, name: str = "k") -> 'GrothendieckGroup':
        """K₀(k) ≅ ℤ for any field k."""
        return cls(name, class_group_order=1)


# ═══════════════════════════════════════════════════════════════════════════════
# K₁ - WHITEHEAD GROUP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class K1Element:
    """
    Element of K₁(R) = GL(R)/E(R).
    
    For R = ℤ: K₁(ℤ) ≅ ℤ/2ℤ = {±1}
    For R = field: K₁(k) ≅ k* (multiplicative group)
    """
    determinant: complex  # Representative in k*
    ring_name: str = "Z"
    
    def __mul__(self, other: 'K1Element') -> 'K1Element':
        return K1Element(self.determinant * other.determinant, self.ring_name)
    
    def inverse(self) -> 'K1Element':
        return K1Element(1.0 / self.determinant, self.ring_name)
    
    @classmethod
    def from_matrix(cls, M: NDArray, ring_name: str = "R") -> 'K1Element':
        """Create K₁ element from invertible matrix."""
        det = np.linalg.det(M)
        return cls(det, ring_name)


@dataclass
class WhiteheadGroup:
    """
    K₁(R) - the Whitehead group.
    """
    ring_name: str
    
    def from_determinant(self, det: complex) -> K1Element:
        return K1Element(det, self.ring_name)
    
    @classmethod
    def integers(cls) -> 'WhiteheadGroup':
        """K₁(ℤ) ≅ {±1}."""
        return cls("Z")
    
    @classmethod
    def reals(cls) -> 'WhiteheadGroup':
        """K₁(ℝ) ≅ ℝ*."""
        return cls("R")


# ═══════════════════════════════════════════════════════════════════════════════
# K₂ - MILNOR K-THEORY AND STEINBERG SYMBOLS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SteinbergSymbol:
    """
    Steinberg symbol {a, b} in K₂(F) for a field F.
    
    Properties:
    - {a, b} = -{b, a}  (antisymmetry)
    - {a, 1-a} = 0      (Steinberg relation)
    - {a, -a} = 0
    - {ab, c} = {a, c} + {b, c}  (bilinearity)
    """
    a: complex
    b: complex
    
    def is_trivial(self) -> bool:
        """Check if symbol is trivial via Steinberg relations."""
        # {a, 1-a} = 0
        if np.isclose(self.b, 1 - self.a):
            return True
        # {a, -a} = 0
        if np.isclose(self.b, -self.a):
            return True
        return False
    
    def antisymmetric(self) -> 'SteinbergSymbol':
        """{a, b} = -{b, a}."""
        return SteinbergSymbol(self.b, self.a)
    
    def tame_symbol(self, prime: int) -> complex:
        """
        Tame symbol at prime p:
        ∂_p{a, b} = (-1)^{v(a)v(b)} a^{v(b)} / b^{v(a)} mod p
        """
        # Simplified: assume a, b are units
        return 1.0


@dataclass
class MilnorK2:
    """
    K₂^M(F) - Milnor K₂ of a field.
    
    Generated by Steinberg symbols modulo relations.
    """
    field_name: str = "Q"
    
    def symbol(self, a: complex, b: complex) -> SteinbergSymbol:
        """Create Steinberg symbol {a, b}."""
        return SteinbergSymbol(a, b)
    
    def hilbert_symbol(self, a: complex, b: complex, p: int) -> int:
        """
        Hilbert symbol (a, b)_p ∈ {±1}.
        
        (a, b)_p = 1 iff z² = ax² + by² has solution in ℚ_p.
        """
        # Simplified computation
        return 1


# ═══════════════════════════════════════════════════════════════════════════════
# HIGHER K-THEORY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HigherKGroup:
    """
    K_n(R) for n ≥ 0.
    
    Computed via:
    - Quillen's Q-construction
    - Waldhausen's S-construction
    - Plus construction on BGL(R)
    """
    n: int
    ring_name: str
    known_structure: Optional[str] = None
    
    @classmethod
    def of_integers(cls, n: int) -> 'HigherKGroup':
        """
        K_n(ℤ) - known for small n:
        K₀(ℤ) = ℤ
        K₁(ℤ) = ℤ/2
        K₂(ℤ) = ℤ/2
        K₃(ℤ) = ℤ/48
        K₄(ℤ) = 0
        """
        structures = {
            0: "Z",
            1: "Z/2",
            2: "Z/2", 
            3: "Z/48",
            4: "0",
            5: "Z",
            6: "0",
            7: "Z/240",
            8: "0"
        }
        return cls(n, "Z", structures.get(n))
    
    @classmethod
    def of_finite_field(cls, n: int, q: int) -> 'HigherKGroup':
        """
        K_n(𝔽_q):
        K₀ = ℤ
        K₁ = ℤ/(q-1)
        K_{2i} = 0 for i > 0
        K_{2i-1} = ℤ/(q^i - 1) for i > 0
        """
        if n == 0:
            structure = "Z"
        elif n == 1:
            structure = f"Z/{q-1}"
        elif n % 2 == 0 and n > 0:
            structure = "0"
        else:
            i = (n + 1) // 2
            structure = f"Z/{q**i - 1}"
        return cls(n, f"F_{q}", structure)


# ═══════════════════════════════════════════════════════════════════════════════
# EXACT SEQUENCES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LocalizationSequence:
    """
    Localization exact sequence in K-theory:
    
    ... → K_n(R/p) → K_n(R) → K_n(R_p) → K_{n-1}(R/p) → ...
    """
    ring_name: str
    prime_ideal: str
    
    def boundary_map(self, n: int) -> str:
        """Description of boundary ∂: K_n(R_p) → K_{n-1}(R/p)."""
        return f"∂_{n}: K_{n}({self.ring_name}_{self.prime_ideal}) → K_{n-1}({self.ring_name}/{self.prime_ideal})"


@dataclass  
class FundamentalTheorem:
    """
    Fundamental theorem of algebraic K-theory:
    
    K_n(R[t]) ≅ K_n(R) ⊕ NK_n(R)
    K_n(R[t, t⁻¹]) ≅ K_n(R) ⊕ K_{n-1}(R) ⊕ NK_n(R) ⊕ NK_n(R)
    
    where NK_n is the nil-K-theory.
    """
    ring_name: str
    
    def polynomial_extension(self, n: int) -> str:
        return f"K_{n}({self.ring_name}[t]) ≅ K_{n}({self.ring_name}) ⊕ NK_{n}({self.ring_name})"
    
    def laurent_extension(self, n: int) -> str:
        return f"K_{n}({self.ring_name}[t,t⁻¹]) ≅ K_{n}({self.ring_name}) ⊕ K_{n-1}({self.ring_name})"


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY-K-THEORY BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewayKTheoryBridge:
    """
    Bridge between gateway algebra and K-theory.
    
    Key connection: K₂ and the Steinberg group relate to
    SL(2) structure via:
    - Steinberg presentation of SL(n)
    - Central extensions by K₂
    """
    
    @staticmethod
    def sl2_steinberg_relation() -> str:
        """
        Steinberg presentation of SL(2):
        
        Generators: x_{ij}(t) for i ≠ j, t ∈ R
        Relations: 
        - [x_{ij}(s), x_{jk}(t)] = x_{ik}(st) for i,j,k distinct
        - [x_{ij}(s), x_{kl}(t)] = 1 for j ≠ k, i ≠ l
        """
        return "SL(2) via Steinberg: ⟨x₁₂(t), x₂₁(t) | relations⟩"
    
    @staticmethod  
    def gateway_to_k2(T: float) -> SteinbergSymbol:
        """
        Map gateway parameter to K₂ element.
        
        T ↦ {1+T, 1-T} (when T ≠ ±1)
        """
        if abs(T) >= 1:
            raise ValueError("|T| must be < 1")
        return SteinbergSymbol(1 + T, 1 - T)
    
    @staticmethod
    def discriminant_in_k0(A: float) -> K0Element:
        """
        Gateway discriminant A as virtual dimension.
        """
        # A = 1/(1-T²) → virtual rank
        rank = int(round(A)) if A > 0 else 0
        return K0Element(rank, 0, "Gateway")


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def k0_integers() -> GrothendieckGroup:
    """Get K₀(ℤ)."""
    return GrothendieckGroup.integers()


def k1_integers() -> WhiteheadGroup:
    """Get K₁(ℤ)."""
    return WhiteheadGroup.integers()


def k_n_integers(n: int) -> HigherKGroup:
    """Get K_n(ℤ)."""
    return HigherKGroup.of_integers(n)


def steinberg_symbol(a: complex, b: complex) -> SteinbergSymbol:
    """Create Steinberg symbol {a, b}."""
    return SteinbergSymbol(a, b)


def projective_module(rank: int, ring: str = "Z") -> ProjectiveModule:
    """Create projective module of given rank."""
    return ProjectiveModule(rank, ring)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # K₀
    'ProjectiveModule',
    'K0Element', 
    'GrothendieckGroup',
    
    # K₁
    'K1Element',
    'WhiteheadGroup',
    
    # K₂
    'SteinbergSymbol',
    'MilnorK2',
    
    # Higher K
    'HigherKGroup',
    
    # Exact sequences
    'LocalizationSequence',
    'FundamentalTheorem',
    
    # Bridge
    'GatewayKTheoryBridge',
    
    # Functions
    'k0_integers',
    'k1_integers',
    'k_n_integers',
    'steinberg_symbol',
    'projective_module',
]
