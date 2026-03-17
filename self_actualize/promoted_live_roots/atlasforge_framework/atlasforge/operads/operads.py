"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    OPERADS AND HIGHER ALGEBRA MODULE                         ║
║                                                                              ║
║  Operads, A∞-algebras, and Higher Categorical Structures                     ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Operads encode algebraic operations with multiple inputs.                 ║
║    P(n) = "space of n-ary operations"                                        ║
║    Composition: P(k) × P(n₁) × ... × P(n_k) → P(n₁ + ... + n_k)             ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Ψ-pole ↔ Tree structures (hierarchical composition)                    ║
║    - C-pole ↔ Smooth operads (E_∞, L_∞)                                     ║
║    - D-pole ↔ Combinatorial operads (Assoc, Com)                            ║
║    - Gateway ↔ Koszul duality (P ↔ P!)                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Set
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# OPERADS
# ═══════════════════════════════════════════════════════════════════════════════

class OperadType(Enum):
    """Standard types of operads."""
    ASSOC = "Assoc"      # Associative algebras
    COM = "Com"          # Commutative algebras
    LIE = "Lie"          # Lie algebras
    POISSON = "Pois"     # Poisson algebras
    E_N = "E_n"          # Little n-disks
    A_INFTY = "A_∞"      # A-infinity
    L_INFTY = "L_∞"      # L-infinity
    E_INFTY = "E_∞"      # E-infinity


@dataclass
class Operad:
    """
    An operad P in a symmetric monoidal category.
    
    Components:
    - P(n): space of n-ary operations
    - γ: composition maps
    - η: unit 1 → P(1)
    - Σ_n action on P(n)
    """
    name: str
    arity_spaces: Dict[int, Any] = field(default_factory=dict)
    is_symmetric: bool = True
    
    def arity(self, n: int) -> Any:
        """Get P(n) - the n-ary operations."""
        return self.arity_spaces.get(n)
    
    def dimension(self, n: int) -> int:
        """Dimension of P(n) (if vector space)."""
        space = self.arity_spaces.get(n)
        if space is None:
            return 0
        if isinstance(space, int):
            return space
        return len(space) if hasattr(space, '__len__') else 1
    
    def generating_function(self, max_n: int = 10) -> List[int]:
        """Dimensions dim P(n) for n = 1, ..., max_n."""
        return [self.dimension(n) for n in range(1, max_n + 1)]
    
    @classmethod
    def associative(cls) -> 'Operad':
        """
        Associative operad: Assoc(n) = k[Σ_n] (regular representation).
        Algebras = associative algebras.
        """
        import math
        return cls("Assoc", {n: math.factorial(n) for n in range(1, 10)})
    
    @classmethod
    def commutative(cls) -> 'Operad':
        """
        Commutative operad: Com(n) = k (trivial representation).
        Algebras = commutative algebras.
        """
        return cls("Com", {n: 1 for n in range(1, 10)})
    
    @classmethod
    def lie(cls) -> 'Operad':
        """
        Lie operad: Lie(n) = Lie(n) (Lie representation).
        Algebras = Lie algebras.
        """
        # dim Lie(n) = (n-1)!
        import math
        return cls("Lie", {n: math.factorial(n-1) for n in range(1, 10)})


@dataclass
class OperadMorphism:
    """
    Morphism of operads f: P → Q.
    
    Collection of maps f(n): P(n) → Q(n) compatible with composition.
    """
    source: Operad
    target: Operad
    name: str = "f"
    
    def __call__(self, n: int) -> str:
        return f"{self.name}({n}): {self.source.name}({n}) → {self.target.name}({n})"


# ═══════════════════════════════════════════════════════════════════════════════
# KOSZUL DUALITY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KoszulDuality:
    """
    Koszul duality for operads: P ↔ P!
    
    Key examples:
    - Assoc! = Assoc
    - Com! = Lie
    - Lie! = Com
    - Pois! = Pois
    """
    operad: Operad
    
    def dual_name(self) -> str:
        """Name of Koszul dual operad."""
        duality_map = {
            "Assoc": "Assoc",
            "Com": "Lie",
            "Lie": "Com",
            "Pois": "Pois",
            "Leib": "Zinb"
        }
        return duality_map.get(self.operad.name, f"{self.operad.name}!")
    
    def is_self_dual(self) -> bool:
        """Check if P! ≅ P."""
        return self.operad.name in ["Assoc", "Pois"]
    
    def bar_cobar_resolution(self) -> str:
        """Bar-cobar resolution: Ω(B(P)) → P quasi-iso."""
        return f"Ω(B({self.operad.name})) ≃ {self.operad.name}"


# ═══════════════════════════════════════════════════════════════════════════════
# A-INFINITY ALGEBRAS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AInfinityAlgebra:
    """
    A∞-algebra: algebra over the A∞ operad.
    
    Structure maps: m_n: A^⊗n → A[2-n] for n ≥ 1
    
    Relations (A∞ relations):
    Σ_{i+j+k=n} (-1)^{ik+j} m_{i+1+k}(1^⊗i ⊗ m_j ⊗ 1^⊗k) = 0
    
    Special cases:
    - m_1: differential (d² = 0)
    - m_2: multiplication
    - m_3: homotopy for associativity
    """
    name: str
    base_space: Any = None
    max_arity: int = 5
    
    def m(self, n: int) -> str:
        """n-ary operation m_n."""
        if n < 1:
            return "0"
        return f"m_{n}: {self.name}^⊗{n} → {self.name}[{2-n}]"
    
    def differential(self) -> str:
        """m_1 is the differential."""
        return self.m(1)
    
    def product(self) -> str:
        """m_2 is the product."""
        return self.m(2)
    
    def is_strictly_associative(self) -> bool:
        """Check if m_n = 0 for n ≥ 3."""
        return False  # Generic A∞ has higher operations
    
    def a_infinity_relation(self, n: int) -> str:
        """The n-th A∞ relation."""
        return f"Σ_{{i+j+k={n}}} ±m_{{i+1+k}}(1^⊗i ⊗ m_j ⊗ 1^⊗k) = 0"


@dataclass 
class AInfinityMorphism:
    """
    A∞-morphism f: A → B.
    
    Components: f_n: A^⊗n → B[1-n] for n ≥ 1
    
    f is strict if f_n = 0 for n ≥ 2.
    f is quasi-isomorphism if f_1 is quasi-iso of complexes.
    """
    source: AInfinityAlgebra
    target: AInfinityAlgebra
    name: str = "f"
    
    def component(self, n: int) -> str:
        return f"{self.name}_{n}: {self.source.name}^⊗{n} → {self.target.name}[{1-n}]"
    
    def is_strict(self) -> bool:
        """Strict = only f_1 nonzero."""
        return False  # Generic


# ═══════════════════════════════════════════════════════════════════════════════
# L-INFINITY ALGEBRAS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LInfinityAlgebra:
    """
    L∞-algebra (strong homotopy Lie algebra).
    
    Brackets: ℓ_n: L^⊗n → L[2-n] for n ≥ 1
    Graded antisymmetric: ℓ_n(..., x, y, ...) = -(-1)^{|x||y|} ℓ_n(..., y, x, ...)
    
    L∞ relations (generalized Jacobi):
    Σ_{i+j=n+1} Σ_σ ±ℓ_j(ℓ_i(x_σ), x_σ') = 0
    """
    name: str
    base_space: Any = None
    
    def bracket(self, n: int) -> str:
        """n-ary bracket ℓ_n."""
        return f"ℓ_{n}: {self.name}^⊗{n} → {self.name}[{2-n}]"
    
    def differential(self) -> str:
        """ℓ_1 is the differential."""
        return self.bracket(1)
    
    def lie_bracket(self) -> str:
        """ℓ_2 is the Lie bracket."""
        return self.bracket(2)
    
    def jacobiator(self) -> str:
        """ℓ_3 measures failure of Jacobi."""
        return self.bracket(3)
    
    def maurer_cartan_equation(self) -> str:
        """
        Maurer-Cartan equation:
        Σ_{n≥1} (1/n!) ℓ_n(x, ..., x) = 0
        """
        return f"Σ_{{n≥1}} (1/n!) ℓ_n(x^⊗n) = 0"


# ═══════════════════════════════════════════════════════════════════════════════
# E_N OPERADS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EnOperad:
    """
    E_n operad (little n-disks/cubes operad).
    
    E_n(k) = Config(k disks in unit n-disk, disjoint)
    
    Key facts:
    - E_1 ≃ Assoc (A∞)
    - E_2 algebras have multiplication + homotopy commutativity
    - E_∞ ≃ Com (fully homotopy commutative)
    """
    n: int
    
    @property
    def symbol(self) -> str:
        if self.n == float('inf'):
            return "E_∞"
        return f"E_{self.n}"
    
    def algebra_description(self) -> str:
        """What kind of algebras this encodes."""
        if self.n == 1:
            return "A∞-algebras (associative up to homotopy)"
        elif self.n == 2:
            return "Algebras with homotopy-commutative multiplication"
        elif self.n == float('inf'):
            return "E∞-algebras (fully homotopy commutative)"
        else:
            return f"E_{self.n}-algebras (intermediate coherent commutativity)"
    
    def homology_operad(self) -> str:
        """H_*(E_n) as operad."""
        if self.n == 1:
            return "Assoc"
        elif self.n >= 2:
            return "Com (Poisson for n=2)"
        return f"H_*(E_{self.n})"
    
    @classmethod
    def e_infinity(cls) -> 'EnOperad':
        """E_∞ operad."""
        return cls(float('inf'))


# ═══════════════════════════════════════════════════════════════════════════════
# HIGHER CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class InfinityCategory:
    """
    (∞,1)-category (quasi-category, ∞-category).
    
    Model-independent notion:
    - Objects
    - Morphisms
    - 2-morphisms (homotopies between morphisms)
    - n-morphisms for all n (higher homotopies)
    - Composition defined up to coherent homotopy
    """
    name: str
    model: str = "quasi-category"  # or "complete Segal space", "Segal category"
    
    def hom_space(self, X: str, Y: str) -> str:
        """Hom_C(X, Y) is a space (∞-groupoid)."""
        return f"Hom_{self.name}({X}, {Y})"
    
    def mapping_space(self, X: str, Y: str) -> str:
        """Mapping space Map(X, Y)."""
        return f"Map_{self.name}({X}, {Y})"
    
    def is_stable(self) -> bool:
        """Check if category is stable (has loops/suspensions)."""
        return False  # Generic


@dataclass
class StableInfinityCategory:
    """
    Stable (∞,1)-category.
    
    Key properties:
    - Has zero object
    - Has finite limits and colimits
    - A square is pushout iff pullback
    - Suspension Σ is an equivalence
    """
    name: str
    
    def suspension(self, X: str) -> str:
        """Suspension functor Σ."""
        return f"Σ{X}"
    
    def loop(self, X: str) -> str:
        """Loop functor Ω."""
        return f"Ω{X}"
    
    def fiber_sequence(self, F: str, E: str, B: str) -> str:
        """Fiber sequence F → E → B."""
        return f"{F} → {E} → {B} → Σ{F}"
    
    def homotopy_groups(self, X: str, n: int) -> str:
        """π_n(X) in stable category."""
        return f"π_{n}({X})"


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORIZATION ALGEBRAS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FactorizationAlgebra:
    """
    Factorization algebra on a manifold M.
    
    A: Open(M) → Chain complexes
    
    Satisfying:
    - Locality: A(U ⊔ V) ≅ A(U) ⊗ A(V) for disjoint U, V
    - Descent: Čech condition for covers
    
    Key example: Observables in QFT form a factorization algebra.
    """
    manifold: str
    name: str = "A"
    
    def on_open(self, U: str) -> str:
        """A(U) - value on open set."""
        return f"{self.name}({U})"
    
    def factorization(self, U: str, V: str) -> str:
        """Factorization for disjoint opens."""
        return f"{self.name}({U} ⊔ {V}) ≅ {self.name}({U}) ⊗ {self.name}({V})"
    
    def global_sections(self) -> str:
        """Global observables A(M)."""
        return f"{self.name}({self.manifold})"


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OperadicPoleBridge:
    """
    Bridge between operadic structures and pole structure.
    """
    
    @staticmethod
    def psi_pole_as_trees() -> str:
        """
        Ψ-pole (hierarchical) corresponds to tree structures.
        Operadic composition = tree grafting.
        """
        return "Ψ-pole ↔ Trees: Hierarchical operadic composition"
    
    @staticmethod
    def c_pole_as_smooth_operads() -> str:
        """
        C-pole (continuous) corresponds to smooth operads.
        E_∞, L_∞ encode smooth/continuous operations.
        """
        return "C-pole ↔ E_∞/L_∞: Continuous homotopy operations"
    
    @staticmethod
    def d_pole_as_combinatorial() -> str:
        """
        D-pole (discrete) corresponds to combinatorial operads.
        Assoc, Com are discrete algebraic structures.
        """
        return "D-pole ↔ Assoc/Com: Discrete algebraic operations"
    
    @staticmethod
    def gateway_as_koszul() -> str:
        """
        Gateway corresponds to Koszul duality.
        P ↔ P! mirrors T ↔ -T reflection.
        """
        return "Gateway ↔ Koszul duality: P ↔ P!"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def operad(name: str) -> Operad:
    """Create an operad."""
    standard = {
        "Assoc": Operad.associative,
        "Com": Operad.commutative,
        "Lie": Operad.lie
    }
    if name in standard:
        return standard[name]()
    return Operad(name)


def a_infinity(name: str) -> AInfinityAlgebra:
    """Create an A∞-algebra."""
    return AInfinityAlgebra(name)


def l_infinity(name: str) -> LInfinityAlgebra:
    """Create an L∞-algebra."""
    return LInfinityAlgebra(name)


def e_n_operad(n: int) -> EnOperad:
    """Create E_n operad."""
    return EnOperad(n)


def infinity_category(name: str) -> InfinityCategory:
    """Create an ∞-category."""
    return InfinityCategory(name)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Operads
    'OperadType',
    'Operad',
    'OperadMorphism',
    
    # Koszul
    'KoszulDuality',
    
    # A-infinity
    'AInfinityAlgebra',
    'AInfinityMorphism',
    
    # L-infinity
    'LInfinityAlgebra',
    
    # E_n
    'EnOperad',
    
    # Higher categories
    'InfinityCategory',
    'StableInfinityCategory',
    
    # Factorization
    'FactorizationAlgebra',
    
    # Bridge
    'OperadicPoleBridge',
    
    # Functions
    'operad',
    'a_infinity',
    'l_infinity',
    'e_n_operad',
    'infinity_category',
]
