"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ALGEBRAIC GEOMETRY MODULE                               ║
║                                                                              ║
║  Schemes, Varieties, and Divisors                                            ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Varieties are solution sets of polynomial equations.                      ║
║    Schemes generalize via locally ringed spaces.                             ║
║    Divisors encode zeros and poles of rational functions.                    ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - C-pole ↔ Smooth varieties, tangent spaces                              ║
║    - D-pole ↔ Points, zero-dimensional schemes                              ║
║    - Gateway ↔ Projective duality P(V) ↔ P(V*)                              ║
║    - Modular ↔ Moduli spaces of curves and abelian varieties                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set, Any, Callable
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# AFFINE VARIETIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Polynomial:
    """Polynomial in n variables over a field."""
    coefficients: Dict[Tuple[int, ...], complex]  # monomial exponents → coefficient
    num_variables: int
    
    def __call__(self, *args) -> complex:
        """Evaluate polynomial at a point."""
        if len(args) != self.num_variables:
            raise ValueError(f"Expected {self.num_variables} variables")
        result = 0
        for exponents, coef in self.coefficients.items():
            term = coef
            for i, exp in enumerate(exponents):
                term *= args[i] ** exp
            result += term
        return result
    
    @property
    def degree(self) -> int:
        """Total degree of polynomial."""
        if not self.coefficients:
            return 0
        return max(sum(exp) for exp in self.coefficients.keys())
    
    @classmethod
    def from_string(cls, expr: str, n: int = 2) -> 'Polynomial':
        """Parse simple polynomial string (placeholder)."""
        return cls({(1, 0): 1}, n)  # x


@dataclass
class AffineVariety:
    """
    Affine variety V(I) ⊂ 𝔸^n.
    
    The zero locus of an ideal I ⊂ k[x₁, ..., xₙ].
    """
    defining_polynomials: List[Polynomial]
    ambient_dimension: int
    name: str = "V"
    
    @property
    def dimension(self) -> Optional[int]:
        """Dimension of the variety (if known)."""
        # Krull dimension: dim V = n - height(I)
        return None  # Would need Gröbner basis
    
    def contains_point(self, point: Tuple[complex, ...]) -> bool:
        """Check if point lies on variety."""
        return all(abs(p(*point)) < 1e-10 for p in self.defining_polynomials)
    
    def is_smooth_at(self, point: Tuple[complex, ...]) -> bool:
        """Check smoothness at a point via Jacobian rank."""
        # Would check rank of Jacobian matrix
        return True
    
    @classmethod
    def affine_space(cls, n: int) -> 'AffineVariety':
        """𝔸^n (empty ideal)."""
        return cls([], n, f"𝔸^{n}")
    
    @classmethod
    def hypersurface(cls, f: Polynomial) -> 'AffineVariety':
        """Hypersurface V(f)."""
        return cls([f], f.num_variables, f"V(f)")


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECTIVE VARIETIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProjectiveVariety:
    """
    Projective variety V(I) ⊂ ℙ^n.
    
    Defined by homogeneous polynomials.
    """
    defining_polynomials: List[Polynomial]  # Homogeneous
    ambient_dimension: int
    name: str = "X"
    
    @property
    def degree(self) -> int:
        """Degree of the variety."""
        if len(self.defining_polynomials) == 1:
            return self.defining_polynomials[0].degree
        return 1  # Would need intersection theory
    
    @classmethod
    def projective_space(cls, n: int) -> 'ProjectiveVariety':
        """ℙ^n."""
        return cls([], n, f"ℙ^{n}")
    
    @classmethod
    def plane_curve(cls, f: Polynomial) -> 'ProjectiveVariety':
        """Plane curve in ℙ²."""
        return cls([f], 2, f"C")
    
    def affine_chart(self, i: int) -> AffineVariety:
        """Affine chart U_i where x_i ≠ 0."""
        return AffineVariety([], self.ambient_dimension, f"{self.name} ∩ U_{i}")


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMES
# ═══════════════════════════════════════════════════════════════════════════════

class SchemeType(Enum):
    """Types of schemes."""
    AFFINE = auto()
    PROJECTIVE = auto()
    QUASI_PROJECTIVE = auto()
    PROPER = auto()
    SEPARATED = auto()
    FINITE_TYPE = auto()


@dataclass
class Scheme:
    """
    Scheme (X, O_X).
    
    A locally ringed space locally isomorphic to Spec(R).
    """
    name: str
    base_ring: str = "k"  # Base field/ring
    dimension: Optional[int] = None
    properties: Set[SchemeType] = field(default_factory=set)
    
    def structure_sheaf(self) -> str:
        """Structure sheaf O_X."""
        return f"O_{self.name}"
    
    def tangent_sheaf(self) -> str:
        """Tangent sheaf T_X."""
        return f"T_{self.name}"
    
    def canonical_sheaf(self) -> str:
        """Canonical sheaf ω_X."""
        return f"ω_{self.name}"
    
    def is_smooth(self) -> bool:
        """Check if scheme is smooth."""
        return True  # Placeholder
    
    def is_proper(self) -> bool:
        return SchemeType.PROPER in self.properties
    
    @classmethod
    def spec(cls, ring: str) -> 'Scheme':
        """Affine scheme Spec(R)."""
        return cls(f"Spec({ring})", ring, properties={SchemeType.AFFINE})
    
    @classmethod
    def proj(cls, graded_ring: str) -> 'Scheme':
        """Projective scheme Proj(S)."""
        return cls(f"Proj({graded_ring})", properties={SchemeType.PROJECTIVE})


@dataclass
class MorphismOfSchemes:
    """
    Morphism f: X → Y of schemes.
    """
    source: Scheme
    target: Scheme
    name: str = "f"
    is_proper: bool = False
    is_flat: bool = False
    is_smooth: bool = False
    is_finite: bool = False
    
    def fiber(self, point: str) -> str:
        """Fiber f⁻¹(y) over a point y."""
        return f"{self.name}⁻¹({point})"
    
    def pullback_sheaf(self, F: str) -> str:
        """Pullback f*F."""
        return f"{self.name}*({F})"
    
    def pushforward_sheaf(self, F: str) -> str:
        """Pushforward f_*F."""
        return f"{self.name}_*({F})"


# ═══════════════════════════════════════════════════════════════════════════════
# DIVISORS
# ═══════════════════════════════════════════════════════════════════════════════

class DivisorType(Enum):
    """Types of divisors."""
    WEIL = auto()
    CARTIER = auto()
    EFFECTIVE = auto()
    AMPLE = auto()
    VERY_AMPLE = auto()
    NEF = auto()
    BIG = auto()
    CANONICAL = auto()
    ANTICANONICAL = auto()


@dataclass
class Divisor:
    """
    Divisor D on a variety/scheme.
    
    Weil divisor: D = Σ n_i [Y_i] (formal sum of codim-1 subvarieties)
    Cartier divisor: Locally principal (f = 0)
    """
    components: Dict[str, int]  # Prime divisor → multiplicity
    variety_name: str
    divisor_type: DivisorType = DivisorType.WEIL
    
    @property
    def degree(self) -> int:
        """Degree of divisor (sum of multiplicities)."""
        return sum(self.components.values())
    
    def is_effective(self) -> bool:
        """D ≥ 0 iff all coefficients non-negative."""
        return all(n >= 0 for n in self.components.values())
    
    def __add__(self, other: 'Divisor') -> 'Divisor':
        """Sum of divisors."""
        result = self.components.copy()
        for prime, mult in other.components.items():
            result[prime] = result.get(prime, 0) + mult
        return Divisor(result, self.variety_name)
    
    def __neg__(self) -> 'Divisor':
        """Negation -D."""
        return Divisor({p: -n for p, n in self.components.items()}, self.variety_name)
    
    def __sub__(self, other: 'Divisor') -> 'Divisor':
        """Difference D - D'."""
        return self + (-other)
    
    def scalar_mult(self, n: int) -> 'Divisor':
        """Scalar multiplication nD."""
        return Divisor({p: n * m for p, m in self.components.items()}, self.variety_name)
    
    def linear_system(self) -> str:
        """|D| - complete linear system."""
        return f"|D| = ℙ(H⁰({self.variety_name}, O(D)))"
    
    @classmethod
    def canonical(cls, variety: str) -> 'Divisor':
        """Canonical divisor K_X."""
        return cls({"K": 1}, variety, DivisorType.CANONICAL)
    
    @classmethod  
    def anticanonical(cls, variety: str) -> 'Divisor':
        """Anticanonical divisor -K_X."""
        return cls({"K": -1}, variety, DivisorType.ANTICANONICAL)


@dataclass
class PicardGroup:
    """
    Picard group Pic(X) of a variety.
    
    Pic(X) = Div(X) / principal divisors
           = isomorphism classes of line bundles
    """
    variety_name: str
    rank: Optional[int] = None  # Picard number ρ
    torsion: Optional[str] = None
    
    def class_of(self, D: Divisor) -> str:
        """Class [D] in Pic(X)."""
        return f"[D] ∈ Pic({self.variety_name})"
    
    @classmethod
    def of_projective_space(cls, n: int) -> 'PicardGroup':
        """Pic(ℙ^n) ≅ ℤ."""
        return cls(f"ℙ^{n}", 1)


# ═══════════════════════════════════════════════════════════════════════════════
# LINE BUNDLES AND SHEAVES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LineBundle:
    """
    Line bundle L on a variety.
    
    Corresponds to Cartier divisor / element of Pic(X).
    """
    variety_name: str
    name: str = "L"
    degree: Optional[int] = None
    
    def tensor_power(self, n: int) -> 'LineBundle':
        """Tensor power L^⊗n."""
        return LineBundle(self.variety_name, f"{self.name}^⊗{n}",
                         self.degree * n if self.degree else None)
    
    def dual(self) -> 'LineBundle':
        """Dual bundle L^∨."""
        return LineBundle(self.variety_name, f"{self.name}^∨",
                         -self.degree if self.degree else None)
    
    def global_sections(self) -> str:
        """H⁰(X, L)."""
        return f"H⁰({self.variety_name}, {self.name})"
    
    def first_chern_class(self) -> str:
        """c₁(L) ∈ H²(X, ℤ)."""
        return f"c₁({self.name})"
    
    @classmethod
    def O(cls, n: int, variety: str = "ℙ") -> 'LineBundle':
        """O(n) on projective space."""
        return cls(variety, f"O({n})", n)
    
    @classmethod
    def canonical_bundle(cls, variety: str) -> 'LineBundle':
        """Canonical bundle ω_X."""
        return cls(variety, f"ω_{variety}")


@dataclass
class CoherentSheaf:
    """
    Coherent sheaf F on a scheme X.
    """
    variety_name: str
    name: str
    rank: Optional[int] = None
    is_locally_free: bool = False
    
    def dual(self) -> 'CoherentSheaf':
        """Dual sheaf F^∨."""
        return CoherentSheaf(self.variety_name, f"{self.name}^∨", self.rank)
    
    def tensor(self, other: 'CoherentSheaf') -> 'CoherentSheaf':
        """Tensor product F ⊗ G."""
        new_rank = self.rank * other.rank if self.rank and other.rank else None
        return CoherentSheaf(self.variety_name, f"{self.name}⊗{other.name}", new_rank)
    
    def chern_classes(self) -> str:
        """Chern classes c_i(F)."""
        return f"c₁({self.name}), c₂({self.name}), ..."
    
    def hilbert_polynomial(self) -> str:
        """Hilbert polynomial χ(F(n))."""
        return f"χ({self.name}(n))"


# ═══════════════════════════════════════════════════════════════════════════════
# INTERSECTION THEORY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ChowRing:
    """
    Chow ring A*(X) of algebraic cycles.
    
    A^k(X) = codimension k cycles modulo rational equivalence.
    """
    variety_name: str
    dimension: int
    
    def cycle_class(self, codim: int) -> str:
        """A^k(X)."""
        return f"A^{codim}({self.variety_name})"
    
    def intersection_product(self, alpha: str, beta: str) -> str:
        """Intersection product α · β."""
        return f"{alpha} · {beta}"
    
    def degree(self, alpha: str) -> str:
        """Degree map deg: A^n(X) → ℤ."""
        return f"deg({alpha})"
    
    @classmethod
    def of_projective_space(cls, n: int) -> 'ChowRing':
        """A*(ℙ^n) = ℤ[h]/(h^{n+1})."""
        return cls(f"ℙ^{n}", n)


@dataclass
class IntersectionNumber:
    """
    Intersection number of divisors/cycles.
    """
    cycles: List[str]
    variety: str
    value: Optional[int] = None
    
    def formula(self) -> str:
        """Intersection as integral."""
        cycles_str = " · ".join(self.cycles)
        return f"∫_{self.variety} {cycles_str}"


# ═══════════════════════════════════════════════════════════════════════════════
# MODULI SPACES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ModuliSpace:
    """
    Moduli space parameterizing geometric objects.
    """
    name: str
    parameterizes: str
    dimension: Optional[int] = None
    is_coarse: bool = True
    is_fine: bool = False
    
    @classmethod
    def curves(cls, g: int) -> 'ModuliSpace':
        """M_g - moduli of genus g curves."""
        dim = 3 * g - 3 if g >= 2 else (0 if g <= 1 else None)
        return cls(f"M_{g}", f"curves of genus {g}", dim)
    
    @classmethod
    def pointed_curves(cls, g: int, n: int) -> 'ModuliSpace':
        """M_{g,n} - moduli of pointed curves."""
        return cls(f"M_{{{g},{n}}}", f"genus {g} curves with {n} marked points")
    
    @classmethod
    def abelian_varieties(cls, g: int) -> 'ModuliSpace':
        """A_g - moduli of abelian varieties."""
        return cls(f"A_{g}", f"principally polarized abelian varieties of dim {g}")
    
    @classmethod
    def vector_bundles(cls, X: str, r: int, d: int) -> 'ModuliSpace':
        """M(r, d) - moduli of vector bundles."""
        return cls(f"M({r},{d})", f"rank {r} degree {d} bundles on {X}")


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY-ALGEBRAIC GEOMETRY BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewayAlgGeomBridge:
    """
    Bridge between gateway algebra and algebraic geometry.
    """
    
    @staticmethod
    def projective_duality() -> str:
        """
        Gateway T ↔ -T corresponds to projective duality.
        ℙ(V) ↔ ℙ(V*)
        """
        return "T ↔ -T ~ ℙ(V) ↔ ℙ(V*) (projective duality)"
    
    @staticmethod
    def serre_duality_as_gateway() -> str:
        """
        Serre duality H^i(F) ↔ H^{n-i}(F^∨ ⊗ ω) reflects gateway.
        """
        return "H^i ↔ H^{n-i} ~ rapidity reflection"
    
    @staticmethod
    def moduli_from_gateway(g: int) -> ModuliSpace:
        """
        Gateway parameter relates to position in moduli.
        """
        return ModuliSpace.curves(g)
    
    @staticmethod
    def picard_as_discrete_pole() -> str:
        """
        Picard group (discrete invariant) → D-pole.
        """
        return "Pic(X) ∈ D-pole: discrete classification of line bundles"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def affine_variety(polynomials: List[Polynomial], n: int) -> AffineVariety:
    """Create affine variety."""
    return AffineVariety(polynomials, n)


def projective_variety(polynomials: List[Polynomial], n: int) -> ProjectiveVariety:
    """Create projective variety."""
    return ProjectiveVariety(polynomials, n)


def scheme(name: str, base: str = "k") -> Scheme:
    """Create a scheme."""
    return Scheme(name, base)


def divisor(components: Dict[str, int], variety: str) -> Divisor:
    """Create a divisor."""
    return Divisor(components, variety)


def line_bundle(variety: str, name: str = "L") -> LineBundle:
    """Create a line bundle."""
    return LineBundle(variety, name)


def moduli_curves(g: int) -> ModuliSpace:
    """Moduli space of genus g curves."""
    return ModuliSpace.curves(g)


def chow_ring(variety: str, dim: int) -> ChowRing:
    """Create Chow ring."""
    return ChowRing(variety, dim)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Polynomials
    'Polynomial',
    
    # Varieties
    'AffineVariety',
    'ProjectiveVariety',
    
    # Schemes
    'SchemeType',
    'Scheme',
    'MorphismOfSchemes',
    
    # Divisors
    'DivisorType',
    'Divisor',
    'PicardGroup',
    
    # Bundles
    'LineBundle',
    'CoherentSheaf',
    
    # Intersection theory
    'ChowRing',
    'IntersectionNumber',
    
    # Moduli
    'ModuliSpace',
    
    # Bridge
    'GatewayAlgGeomBridge',
    
    # Functions
    'affine_variety',
    'projective_variety',
    'scheme',
    'divisor',
    'line_bundle',
    'moduli_curves',
    'chow_ring',
]
