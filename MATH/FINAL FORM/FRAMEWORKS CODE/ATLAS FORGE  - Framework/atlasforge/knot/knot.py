"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        KNOT THEORY MODULE                                    ║
║                                                                              ║
║  Jones Polynomial, Reidemeister Moves, and Knot Invariants                   ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Knot theory studies embeddings of circles in 3-space.                    ║
║    Knot invariants connect to quantum groups and physics.                   ║
║    The crossing structure relates to D-pole constraints.                    ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Knot diagram: planar projection with over/under crossings              ║
║    - Reidemeister moves: R1, R2, R3 preserve knot type                      ║
║    - Jones polynomial: V(t) ∈ ℤ[t^{±1/2}]                                   ║
║    - Bracket polynomial: ⟨K⟩ via skein relation                             ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - D-pole constraints ↔ crossing structure                                ║
║    - Quantum invariants ↔ Σ-pole (stochastic)                               ║
║    - Braids ↔ group structure                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# CROSSING
# ═══════════════════════════════════════════════════════════════════════════════

class CrossingSign(Enum):
    """Sign of a crossing in oriented knot diagram."""
    POSITIVE = 1   # Right-handed crossing
    NEGATIVE = -1  # Left-handed crossing


@dataclass
class Crossing:
    """
    A crossing in a knot diagram.
    
    Four arcs meet at a crossing:
        - over_in: arc coming in on top
        - over_out: arc going out on top  
        - under_in: arc coming in on bottom
        - under_out: arc going out on bottom
    """
    index: int
    sign: CrossingSign
    over_in: int  # Arc index
    over_out: int
    under_in: int
    under_out: int
    
    def writhe_contribution(self) -> int:
        """Contribution to writhe."""
        return self.sign.value


# ═══════════════════════════════════════════════════════════════════════════════
# KNOT DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KnotDiagram:
    """
    Planar diagram of a knot or link.
    
    Represented by list of crossings and arc connectivity.
    """
    crossings: List[Crossing]
    n_arcs: int
    
    @property
    def n_crossings(self) -> int:
        return len(self.crossings)
    
    def writhe(self) -> int:
        """
        Writhe w(K) = Σ signs of crossings.
        
        Not a knot invariant alone, but used in Jones polynomial.
        """
        return sum(c.writhe_contribution() for c in self.crossings)
    
    def crossing_number(self) -> int:
        """Number of crossings (upper bound on crossing number invariant)."""
        return self.n_crossings
    
    def is_alternating(self) -> bool:
        """
        Check if diagram is alternating (over/under alternates along each strand).
        
        Simplified check.
        """
        # Track sign changes as we traverse
        # For a proper alternating diagram, each arc connects
        # an over-crossing to an under-crossing
        return True  # Placeholder - would need full arc traversal
    
    @classmethod
    def unknot(cls) -> 'KnotDiagram':
        """Trivial knot (no crossings)."""
        return cls([], 1)
    
    @classmethod
    def trefoil(cls, right_handed: bool = True) -> 'KnotDiagram':
        """
        Trefoil knot (3_1): simplest non-trivial knot.
        
        3 crossings, all same sign.
        """
        sign = CrossingSign.POSITIVE if right_handed else CrossingSign.NEGATIVE
        crossings = [
            Crossing(0, sign, 0, 1, 2, 3),
            Crossing(1, sign, 1, 2, 3, 4),
            Crossing(2, sign, 2, 0, 4, 5),
        ]
        return cls(crossings, 6)
    
    @classmethod
    def figure_eight(cls) -> 'KnotDiagram':
        """
        Figure-eight knot (4_1): simplest alternating knot with 4 crossings.
        
        Amphichiral (same as its mirror).
        """
        crossings = [
            Crossing(0, CrossingSign.POSITIVE, 0, 1, 2, 3),
            Crossing(1, CrossingSign.NEGATIVE, 1, 2, 4, 5),
            Crossing(2, CrossingSign.POSITIVE, 3, 4, 6, 7),
            Crossing(3, CrossingSign.NEGATIVE, 5, 0, 7, 6),
        ]
        return cls(crossings, 8)


# ═══════════════════════════════════════════════════════════════════════════════
# BRACKET POLYNOMIAL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LaurentPolynomial:
    """
    Laurent polynomial in A (or t^{1/2}).
    
    coeffs[i] = coefficient of A^{min_power + i}
    """
    coeffs: List[int]
    min_power: int = 0
    
    def __add__(self, other: 'LaurentPolynomial') -> 'LaurentPolynomial':
        min_pow = min(self.min_power, other.min_power)
        max_pow = max(self.min_power + len(self.coeffs),
                     other.min_power + len(other.coeffs))
        
        result = [0] * (max_pow - min_pow)
        
        for i, c in enumerate(self.coeffs):
            result[self.min_power - min_pow + i] += c
        for i, c in enumerate(other.coeffs):
            result[other.min_power - min_pow + i] += c
        
        return LaurentPolynomial(result, min_pow)
    
    def __mul__(self, other: 'LaurentPolynomial') -> 'LaurentPolynomial':
        if not self.coeffs or not other.coeffs:
            return LaurentPolynomial([0], 0)
        
        new_min = self.min_power + other.min_power
        n1, n2 = len(self.coeffs), len(other.coeffs)
        result = [0] * (n1 + n2 - 1)
        
        for i, c1 in enumerate(self.coeffs):
            for j, c2 in enumerate(other.coeffs):
                result[i + j] += c1 * c2
        
        return LaurentPolynomial(result, new_min)
    
    def scale(self, c: int) -> 'LaurentPolynomial':
        """Multiply by scalar."""
        return LaurentPolynomial([c * x for x in self.coeffs], self.min_power)
    
    def shift(self, n: int) -> 'LaurentPolynomial':
        """Multiply by A^n."""
        return LaurentPolynomial(self.coeffs, self.min_power + n)
    
    def __repr__(self) -> str:
        terms = []
        for i, c in enumerate(self.coeffs):
            if c == 0:
                continue
            power = self.min_power + i
            if power == 0:
                terms.append(str(c))
            elif power == 1:
                terms.append(f"{c}A" if c != 1 else "A")
            else:
                terms.append(f"{c}A^{power}" if c != 1 else f"A^{power}")
        
        return " + ".join(terms) if terms else "0"
    
    @classmethod
    def one(cls) -> 'LaurentPolynomial':
        return cls([1], 0)
    
    @classmethod
    def A(cls) -> 'LaurentPolynomial':
        return cls([1], 1)
    
    @classmethod
    def A_inv(cls) -> 'LaurentPolynomial':
        return cls([1], -1)


@dataclass
class BracketPolynomial:
    """
    Kauffman bracket polynomial ⟨K⟩.
    
    Satisfies:
        ⟨O⟩ = 1  (unknot)
        ⟨K ∪ O⟩ = d⟨K⟩  where d = -A² - A⁻²
        ⟨crossing⟩ = A⟨0-smoothing⟩ + A⁻¹⟨∞-smoothing⟩
    """
    
    @staticmethod
    def d_factor() -> LaurentPolynomial:
        """Loop value d = -A² - A⁻²."""
        return LaurentPolynomial([-1, 0, 0, 0, -1], -2)
    
    @staticmethod
    def compute_unknot() -> LaurentPolynomial:
        """⟨unknot⟩ = 1."""
        return LaurentPolynomial.one()
    
    @staticmethod  
    def compute_trefoil(right_handed: bool = True) -> LaurentPolynomial:
        """
        Bracket polynomial of trefoil.
        
        ⟨trefoil⟩ = A⁷ - A³ - A⁻⁵  (right-handed)
        """
        if right_handed:
            return LaurentPolynomial([1, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, -1], -5)
        else:
            return LaurentPolynomial([-1, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 1], -7)
    
    @staticmethod
    def compute_figure_eight() -> LaurentPolynomial:
        """
        Bracket polynomial of figure-eight.
        
        ⟨4_1⟩ = A⁸ - A⁴ + 1 - A⁻⁴ + A⁻⁸
        """
        return LaurentPolynomial([1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0, 1], -8)


# ═══════════════════════════════════════════════════════════════════════════════
# JONES POLYNOMIAL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class JonesPolynomial:
    """
    Jones polynomial V(t).
    
    Related to bracket by V_K(t) = (-A)^{-3w(K)} ⟨K⟩ with t = A⁻⁴.
    """
    
    @staticmethod
    def from_bracket(bracket: LaurentPolynomial, writhe: int
                    ) -> LaurentPolynomial:
        """
        Convert bracket to Jones polynomial.
        
        V_K(t) = (-A)^{-3w} ⟨K⟩, then substitute A⁴ = t⁻¹.
        """
        # Multiply by (-A)^{-3w} = (-1)^{-3w} A^{-3w}
        sign = (-1) ** (-3 * writhe)
        shifted = bracket.shift(-3 * writhe)
        if sign < 0:
            shifted = shifted.scale(-1)
        
        return shifted
    
    @staticmethod
    def unknot() -> LaurentPolynomial:
        """V(unknot) = 1."""
        return LaurentPolynomial.one()
    
    @staticmethod
    def trefoil(right_handed: bool = True) -> LaurentPolynomial:
        """
        Jones polynomial of trefoil.
        
        V(3_1) = t + t³ - t⁴  (right-handed, in t)
        """
        if right_handed:
            return LaurentPolynomial([1, 0, 1, -1], 1)
        else:
            return LaurentPolynomial([-1, 1, 0, 1], -4)
    
    @staticmethod
    def figure_eight() -> LaurentPolynomial:
        """
        Jones polynomial of figure-eight.
        
        V(4_1) = t² - t + 1 - t⁻¹ + t⁻²
        """
        return LaurentPolynomial([1, -1, 1, -1, 1], -2)
    
    @staticmethod
    def is_same_knot(v1: LaurentPolynomial, v2: LaurentPolynomial) -> bool:
        """
        Check if two Jones polynomials are equal.
        
        Equal Jones → possibly same knot (necessary but not sufficient).
        """
        # Normalize to same min power
        if v1.min_power != v2.min_power:
            return False
        if len(v1.coeffs) != len(v2.coeffs):
            return False
        return v1.coeffs == v2.coeffs


# ═══════════════════════════════════════════════════════════════════════════════
# BRAID GROUP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Braid:
    """
    Element of braid group B_n.
    
    Generators σ_1, ..., σ_{n-1} with relations:
        σ_i σ_j = σ_j σ_i  for |i-j| ≥ 2
        σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1}
    """
    n_strands: int
    word: List[int]  # σ_i = i, σ_i^{-1} = -i
    
    def __mul__(self, other: 'Braid') -> 'Braid':
        """Braid multiplication (concatenation)."""
        if self.n_strands != other.n_strands:
            raise ValueError("Strand numbers must match")
        return Braid(self.n_strands, self.word + other.word)
    
    def inverse(self) -> 'Braid':
        """Inverse braid (reverse and negate)."""
        return Braid(self.n_strands, [-x for x in reversed(self.word)])
    
    def closure(self) -> KnotDiagram:
        """
        Close braid to get knot/link.
        
        Connect top to bottom with parallel arcs.
        """
        # Simplified: return crossing structure
        crossings = []
        arc_counter = 0
        
        for i, gen in enumerate(self.word):
            idx = abs(gen)
            sign = CrossingSign.POSITIVE if gen > 0 else CrossingSign.NEGATIVE
            
            crossings.append(Crossing(
                i, sign,
                arc_counter, arc_counter + 1,
                arc_counter + 2, arc_counter + 3
            ))
            arc_counter += 4
        
        return KnotDiagram(crossings, arc_counter if crossings else 1)
    
    def exponent_sum(self) -> int:
        """Sum of exponents (equals writhe of closure)."""
        return sum(1 if x > 0 else -1 for x in self.word)
    
    @classmethod
    def sigma(cls, n: int, i: int) -> 'Braid':
        """Generator σ_i."""
        if i < 1 or i >= n:
            raise ValueError(f"Generator index must be in [1, {n-1}]")
        return cls(n, [i])
    
    @classmethod
    def identity(cls, n: int) -> 'Braid':
        """Identity braid."""
        return cls(n, [])


# ═══════════════════════════════════════════════════════════════════════════════
# KNOT INVARIANTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KnotInvariants:
    """Collection of knot invariants."""
    
    @staticmethod
    def unknotting_number_bound(diagram: KnotDiagram) -> int:
        """
        Upper bound on unknotting number.
        
        u(K) ≤ (c(K) - 1)/2 for alternating knots.
        """
        c = diagram.n_crossings
        return (c - 1) // 2 if c > 0 else 0
    
    @staticmethod
    def bridge_number_bound(diagram: KnotDiagram) -> int:
        """
        Upper bound on bridge number.
        
        b(K) ≤ c(K)/2 + 1.
        """
        return diagram.n_crossings // 2 + 1
    
    @staticmethod
    def genus_bound(jones: LaurentPolynomial) -> int:
        """
        Lower bound on Seifert genus from Jones polynomial span.
        
        g(K) ≥ (span(V_K) - 1)/2.
        """
        # Find first and last nonzero
        first = 0
        for i, c in enumerate(jones.coeffs):
            if c != 0:
                first = i
                break
        
        last = len(jones.coeffs) - 1
        for i in range(len(jones.coeffs) - 1, -1, -1):
            if jones.coeffs[i] != 0:
                last = i
                break
        
        span = last - first
        return span // 2


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def trefoil_knot(right_handed: bool = True) -> KnotDiagram:
    """Create trefoil knot diagram."""
    return KnotDiagram.trefoil(right_handed)


def figure_eight_knot() -> KnotDiagram:
    """Create figure-eight knot diagram."""
    return KnotDiagram.figure_eight()


def jones_polynomial(knot_name: str) -> LaurentPolynomial:
    """Get Jones polynomial of named knot."""
    if knot_name == "unknot":
        return JonesPolynomial.unknot()
    elif knot_name == "trefoil" or knot_name == "3_1":
        return JonesPolynomial.trefoil()
    elif knot_name == "figure_eight" or knot_name == "4_1":
        return JonesPolynomial.figure_eight()
    else:
        raise ValueError(f"Unknown knot: {knot_name}")


def writhe(diagram: KnotDiagram) -> int:
    """Compute writhe of diagram."""
    return diagram.writhe()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core
    'CrossingSign',
    'Crossing',
    'KnotDiagram',
    
    # Polynomials
    'LaurentPolynomial',
    'BracketPolynomial',
    'JonesPolynomial',
    
    # Braids
    'Braid',
    
    # Invariants
    'KnotInvariants',
    
    # Functions
    'trefoil_knot',
    'figure_eight_knot',
    'jones_polynomial',
    'writhe',
]
