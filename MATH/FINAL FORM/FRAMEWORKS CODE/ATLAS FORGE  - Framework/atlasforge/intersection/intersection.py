"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     INTERSECTION THEORY MODULE                               ║
║                                                                              ║
║  Algebraic Cycles, Chow Rings, and Intersection Numbers                      ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Count intersections of algebraic cycles in proper position:               ║
║    - Chow groups CH^*(X) = algebraic cycles modulo rational equivalence     ║
║    - Intersection product makes CH*(X) a ring                               ║
║    - Degree map CH^n(X) → ℤ for n-dimensional variety                       ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - D-pole ↔ Discrete intersection numbers                                 ║
║    - C-pole ↔ Cycle classes in cohomology                                   ║
║    - Ψ-pole ↔ Filtration by codimension                                     ║
║    - Gateway ↔ Cycle class map CH*(X) → H*(X)                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# ALGEBRAIC CYCLES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AlgebraicCycle:
    """
    Algebraic cycle Z = Σ nᵢ [Vᵢ] on variety X.
    
    Formal ℤ-linear combination of irreducible subvarieties.
    """
    components: Dict[str, int]  # Vᵢ → nᵢ
    codimension: int
    ambient: str = "X"
    
    def degree(self) -> int:
        """Degree = Σ nᵢ deg(Vᵢ) for 0-cycles."""
        return sum(self.components.values())
    
    def support(self) -> List[str]:
        """Support = union of components with nonzero coefficient."""
        return [v for v, n in self.components.items() if n != 0]
    
    def __add__(self, other: 'AlgebraicCycle') -> 'AlgebraicCycle':
        """Add cycles."""
        new_components = self.components.copy()
        for v, n in other.components.items():
            new_components[v] = new_components.get(v, 0) + n
        return AlgebraicCycle(new_components, self.codimension, self.ambient)
    
    def __mul__(self, scalar: int) -> 'AlgebraicCycle':
        """Scalar multiplication."""
        return AlgebraicCycle(
            {v: n * scalar for v, n in self.components.items()},
            self.codimension,
            self.ambient
        )
    
    @classmethod
    def point(cls, name: str, ambient: str = "X") -> 'AlgebraicCycle':
        """0-cycle: single point."""
        return cls({name: 1}, codimension=-1, ambient=ambient)  # codim = dim X
    
    @classmethod
    def divisor(cls, name: str, ambient: str = "X") -> 'AlgebraicCycle':
        """Codimension 1 cycle (divisor)."""
        return cls({name: 1}, codimension=1, ambient=ambient)


# ═══════════════════════════════════════════════════════════════════════════════
# EQUIVALENCE RELATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class EquivalenceType(Enum):
    """Types of equivalence on cycles."""
    RATIONAL = "Rational equivalence"
    ALGEBRAIC = "Algebraic equivalence"
    HOMOLOGICAL = "Homological equivalence"
    NUMERICAL = "Numerical equivalence"


@dataclass
class RationalEquivalence:
    """
    Rational equivalence on cycles.
    
    Z ~ 0 if Z = div(f) for f ∈ k(Y)* on some Y.
    """
    
    @staticmethod
    def definition() -> str:
        return "Z ~ 0 ⟺ Z = div(f) for some f ∈ k(Y)*"
    
    @staticmethod
    def push_pull() -> str:
        return "Push-forward f_* and pull-back f* respect rational equivalence"


# ═══════════════════════════════════════════════════════════════════════════════
# CHOW GROUPS AND RINGS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ChowGroup:
    """
    Chow group CH^k(X) = Z^k(X) / ~_rat.
    
    k-codimensional cycles modulo rational equivalence.
    """
    variety: str
    codimension: int
    
    def __repr__(self) -> str:
        return f"CH^{self.codimension}({self.variety})"
    
    def cycle_class(self, Z: AlgebraicCycle) -> str:
        """[Z] ∈ CH^k(X)."""
        return f"[{Z}] ∈ {self}"
    
    @classmethod
    def of_point(cls) -> 'ChowGroup':
        """CH^0(pt) = ℤ."""
        return cls("pt", 0)
    
    @classmethod
    def picard_group(cls, X: str) -> 'ChowGroup':
        """CH^1(X) ≅ Pic(X) for smooth X."""
        return cls(X, 1)


@dataclass
class ChowRing:
    """
    Chow ring CH*(X) = ⊕ CH^k(X).
    
    Graded ring with intersection product.
    """
    variety: str
    dimension: int
    
    def graded_piece(self, k: int) -> ChowGroup:
        """CH^k(X)."""
        return ChowGroup(self.variety, k)
    
    def intersection_product(self) -> str:
        """· : CH^i × CH^j → CH^{i+j}."""
        return "· : CH^i(X) × CH^j(X) → CH^{i+j}(X)"
    
    def degree_map(self) -> str:
        """deg: CH^n(X) → ℤ for n-dimensional X."""
        return f"deg: CH^{self.dimension}({self.variety}) → ℤ"
    
    @classmethod
    def projective_space(cls, n: int) -> 'ChowRing':
        """CH*(ℙⁿ) = ℤ[H]/(H^{n+1})."""
        return cls(f"ℙ^{n}", n)
    
    @classmethod
    def grassmannian(cls, k: int, n: int) -> 'ChowRing':
        """CH*(Gr(k,n)) generated by Schubert classes."""
        return cls(f"Gr({k},{n})", k * (n - k))


# ═══════════════════════════════════════════════════════════════════════════════
# INTERSECTION PRODUCT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class IntersectionProduct:
    """
    Intersection product of cycles.
    
    [V] · [W] when V, W intersect properly (expected dimension).
    """
    
    @staticmethod
    def proper_intersection(V: str, W: str, dim_V: int, dim_W: int, dim_X: int) -> str:
        """
        Proper intersection: dim(V ∩ W) = dim V + dim W - dim X.
        """
        expected = dim_V + dim_W - dim_X
        return f"dim({V} ∩ {W}) = {expected} (proper)"
    
    @staticmethod
    def bezout_theorem(d1: int, d2: int) -> int:
        """
        Bézout: deg(V ∩ W) = deg(V) · deg(W) in ℙⁿ.
        """
        return d1 * d2
    
    @staticmethod
    def moving_lemma() -> str:
        """Moving lemma: can move cycles to proper position."""
        return "Any two cycles can be moved to intersect properly"


@dataclass
class IntersectionNumber:
    """
    Intersection number (D₁ · D₂ · ... · Dₙ).
    
    For divisors D₁, ..., Dₙ on n-dimensional X.
    """
    divisors: List[str]
    value: int
    
    def notation(self) -> str:
        """(D₁ · D₂ · ... · Dₙ)."""
        return f"({' · '.join(self.divisors)})"
    
    @classmethod
    def self_intersection(cls, D: str, power: int, value: int) -> 'IntersectionNumber':
        """(D^n)."""
        return cls([D] * power, value)


# ═══════════════════════════════════════════════════════════════════════════════
# CHERN CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ChernClass:
    """
    Chern class c_i(E) ∈ CH^i(X) for vector bundle E.
    """
    bundle: str
    index: int  # i in c_i
    
    def __repr__(self) -> str:
        return f"c_{self.index}({self.bundle})"
    
    @staticmethod
    def total_chern(E: str) -> str:
        """c(E) = 1 + c_1(E) + c_2(E) + ..."""
        return f"c({E}) = 1 + c_1({E}) + c_2({E}) + ..."
    
    @staticmethod
    def whitney_sum(E: str, F: str) -> str:
        """c(E ⊕ F) = c(E) · c(F)."""
        return f"c({E} ⊕ {F}) = c({E}) · c({F})"


@dataclass
class ChernCharacter:
    """
    Chern character ch(E) ∈ CH*(X) ⊗ ℚ.
    
    ch(E) = rk(E) + c_1(E) + (c_1²-2c_2)/2 + ...
    """
    bundle: str
    
    def definition(self) -> str:
        return f"ch({self.bundle}) = Σ ch_i({self.bundle})"
    
    def additivity(self, F: str) -> str:
        """ch(E ⊕ F) = ch(E) + ch(F)."""
        return f"ch({self.bundle} ⊕ {F}) = ch({self.bundle}) + ch({F})"
    
    def multiplicativity(self, F: str) -> str:
        """ch(E ⊗ F) = ch(E) · ch(F)."""
        return f"ch({self.bundle} ⊗ {F}) = ch({self.bundle}) · ch({F})"


@dataclass
class ToddClass:
    """
    Todd class td(E) for vector bundle E.
    
    td(E) = 1 + c_1/2 + (c_1² + c_2)/12 + ...
    """
    bundle: str
    
    def definition(self) -> str:
        return f"td({self.bundle}) = Π (xᵢ/(1-e^{{-xᵢ}})) where c(E) = Π(1+xᵢ)"


# ═══════════════════════════════════════════════════════════════════════════════
# GROTHENDIECK-RIEMANN-ROCH
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GRR:
    """
    Grothendieck-Riemann-Roch theorem.
    
    For f: X → Y proper:
    ch(f_! E) · td(Y) = f_*(ch(E) · td(X))
    """
    
    @staticmethod
    def statement() -> str:
        return "ch(f_! E) · td(Y) = f_*(ch(E) · td(X))"
    
    @staticmethod
    def hirzebruch() -> str:
        """Special case: HRR for X → pt."""
        return "χ(X, E) = ∫_X ch(E) · td(X)"
    
    @staticmethod
    def noether_formula() -> str:
        """For surfaces: χ(O_X) = (c_1² + c_2)/12."""
        return "χ(O_X) = (c_1(X)² + c_2(X))/12"


# ═══════════════════════════════════════════════════════════════════════════════
# SCHUBERT CALCULUS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SchubertClass:
    """
    Schubert class σ_λ ∈ CH*(Gr(k,n)).
    
    Indexed by partitions λ fitting in k × (n-k) box.
    """
    partition: Tuple[int, ...]
    k: int  # Gr(k,n)
    n: int
    
    def __repr__(self) -> str:
        return f"σ_{self.partition}"
    
    def codimension(self) -> int:
        """codim = |λ|."""
        return sum(self.partition)
    
    def is_valid(self) -> bool:
        """Check if λ fits in k × (n-k) box."""
        if len(self.partition) > self.k:
            return False
        return all(p <= self.n - self.k for p in self.partition)


@dataclass
class SchubertCalculus:
    """
    Schubert calculus on Grassmannian.
    """
    k: int
    n: int
    
    def pieri_rule(self) -> str:
        """Pieri's formula for σ_p · σ_λ."""
        return "σ_p · σ_λ = Σ σ_μ (horizontal strip of size p)"
    
    def giambelli_formula(self) -> str:
        """Giambelli: σ_λ as determinant."""
        return "σ_λ = det(σ_{λ_i-i+j})"
    
    def littlewood_richardson(self) -> str:
        """L-R rule for σ_λ · σ_μ."""
        return "σ_λ · σ_μ = Σ c^ν_{λμ} σ_ν"


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE CLASS MAP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CycleClassMap:
    """
    Cycle class map cl: CH^k(X) → H^{2k}(X).
    
    Connects Chow theory to cohomology.
    """
    
    @staticmethod
    def definition() -> str:
        return "cl: CH^k(X) → H^{2k}(X, ℤ)"
    
    @staticmethod
    def compatibility() -> str:
        return "cl respects intersection product and cup product"
    
    @staticmethod
    def hodge_conjecture() -> str:
        """Hodge conjecture on image."""
        return "Image of cl ⊗ ℚ = Hodge classes (Hodge conjecture)"


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class IntersectionPoleBridge:
    """
    Bridge between intersection theory and pole structure.
    """
    
    @staticmethod
    def d_pole_as_intersection() -> str:
        """
        D-pole corresponds to discrete intersection numbers.
        """
        return "D ↔ Intersection: (D₁ · ... · Dₙ) ∈ ℤ discrete"
    
    @staticmethod
    def c_pole_as_cohomology() -> str:
        """
        C-pole corresponds to cycle classes in cohomology.
        """
        return "C ↔ Cohomology: cl: CH*(X) → H*(X) continuous"
    
    @staticmethod
    def psi_pole_as_filtration() -> str:
        """
        Ψ-pole corresponds to codimension filtration.
        """
        return "Ψ ↔ Filtration: CH^0 ⊂ CH^1 ⊂ ... hierarchical"
    
    @staticmethod
    def gateway_as_cycle_map() -> str:
        """
        Gateway corresponds to cycle class map.
        """
        return "Gateway ↔ Cycle map: cl: CH*(X) → H*(X)"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def algebraic_cycle(components: Dict[str, int], codim: int) -> AlgebraicCycle:
    """Create algebraic cycle."""
    return AlgebraicCycle(components, codim)


def chow_group(X: str, k: int) -> ChowGroup:
    """Create Chow group."""
    return ChowGroup(X, k)


def chow_ring(X: str, dim: int) -> ChowRing:
    """Create Chow ring."""
    return ChowRing(X, dim)


def intersection_number(divisors: List[str], value: int) -> IntersectionNumber:
    """Create intersection number."""
    return IntersectionNumber(divisors, value)


def chern_class(E: str, i: int) -> ChernClass:
    """Create Chern class."""
    return ChernClass(E, i)


def schubert_class(partition: Tuple[int, ...], k: int, n: int) -> SchubertClass:
    """Create Schubert class."""
    return SchubertClass(partition, k, n)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Cycles
    'AlgebraicCycle',
    'EquivalenceType',
    'RationalEquivalence',
    
    # Chow
    'ChowGroup',
    'ChowRing',
    
    # Intersection
    'IntersectionProduct',
    'IntersectionNumber',
    
    # Chern classes
    'ChernClass',
    'ChernCharacter',
    'ToddClass',
    'GRR',
    
    # Schubert
    'SchubertClass',
    'SchubertCalculus',
    
    # Cycle map
    'CycleClassMap',
    
    # Bridge
    'IntersectionPoleBridge',
    
    # Functions
    'algebraic_cycle',
    'chow_group',
    'chow_ring',
    'intersection_number',
    'chern_class',
    'schubert_class',
]
