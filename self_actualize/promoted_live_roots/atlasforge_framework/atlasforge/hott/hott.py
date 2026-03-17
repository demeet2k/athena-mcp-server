"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    HOMOTOPY TYPE THEORY MODULE                               ║
║                                                                              ║
║  Types as Spaces, Proofs as Paths                                            ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Types are spaces, terms are points, identities are paths.                 ║
║    Univalence: (A ≃ B) ≃ (A = B)                                            ║
║    Higher inductive types: spaces defined by generators & relations.         ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Ψ-pole ↔ Universe hierarchy (U₀ : U₁ : U₂ : ...)                       ║
║    - C-pole ↔ Path types (continuous identity)                              ║
║    - D-pole ↔ Inductive types (discrete construction)                       ║
║    - Gateway ↔ Univalence (equivalence = identity)                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Generic, TypeVar
from enum import Enum, auto


T = TypeVar('T')
A = TypeVar('A')
B = TypeVar('B')


# ═══════════════════════════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HType:
    """
    A type in HoTT.
    
    Types are interpreted as spaces:
    - Terms a : A are points
    - Identity type a =_A b is path space
    - Higher identity types are higher paths
    """
    name: str
    universe_level: int = 0
    
    def __str__(self) -> str:
        return self.name
    
    def in_universe(self) -> str:
        """A : U_n."""
        return f"{self.name} : U_{self.universe_level}"
    
    @classmethod
    def unit(cls) -> 'HType':
        """Unit type 𝟙."""
        return cls("𝟙", 0)
    
    @classmethod
    def empty(cls) -> 'HType':
        """Empty type 𝟘."""
        return cls("𝟘", 0)
    
    @classmethod
    def nat(cls) -> 'HType':
        """Natural numbers ℕ."""
        return cls("ℕ", 0)
    
    @classmethod
    def bool(cls) -> 'HType':
        """Boolean 𝟚."""
        return cls("𝟚", 0)


@dataclass
class Universe:
    """
    Universe U_n - the type of types.
    
    Hierarchy: U_0 : U_1 : U_2 : ...
    Avoids Russell's paradox.
    """
    level: int
    
    @property
    def symbol(self) -> str:
        return f"U_{self.level}"
    
    def contains(self, A: HType) -> bool:
        """Check if A : U_n."""
        return A.universe_level == self.level
    
    def successor(self) -> 'Universe':
        """U_{n+1}."""
        return Universe(self.level + 1)


# ═══════════════════════════════════════════════════════════════════════════════
# TYPE FORMERS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProductType:
    """
    Product type A × B.
    
    Introduction: (a, b) : A × B for a : A, b : B
    Elimination: π₁, π₂ projections
    """
    A: HType
    B: HType
    
    @property
    def symbol(self) -> str:
        return f"{self.A.name} × {self.B.name}"
    
    def pair(self, a: str, b: str) -> str:
        """Pair constructor."""
        return f"({a}, {b})"
    
    def fst(self, p: str) -> str:
        """First projection."""
        return f"π₁({p})"
    
    def snd(self, p: str) -> str:
        """Second projection."""
        return f"π₂({p})"


@dataclass
class SumType:
    """
    Sum type A + B (coproduct).
    
    Introduction: inl(a) : A + B for a : A
                  inr(b) : A + B for b : B
    Elimination: case analysis
    """
    A: HType
    B: HType
    
    @property
    def symbol(self) -> str:
        return f"{self.A.name} + {self.B.name}"
    
    def inl(self, a: str) -> str:
        """Left injection."""
        return f"inl({a})"
    
    def inr(self, b: str) -> str:
        """Right injection."""
        return f"inr({b})"


@dataclass
class FunctionType:
    """
    Function type A → B.
    
    Introduction: λ(x).e : A → B
    Elimination: f(a) for f : A → B, a : A
    """
    domain: HType
    codomain: HType
    
    @property
    def symbol(self) -> str:
        return f"{self.domain.name} → {self.codomain.name}"
    
    def lambda_term(self, var: str, body: str) -> str:
        """Lambda abstraction."""
        return f"λ({var}).{body}"
    
    def apply(self, f: str, a: str) -> str:
        """Function application."""
        return f"{f}({a})"


@dataclass
class DependentProduct:
    """
    Dependent product Π(x:A). B(x) (dependent function type).
    
    Special case: A → B when B doesn't depend on x.
    """
    base: HType
    family: str  # B(x)
    
    @property
    def symbol(self) -> str:
        return f"Π(x:{self.base.name}). {self.family}"
    
    def is_simple_function(self) -> bool:
        """Check if it's a non-dependent function type."""
        return False


@dataclass
class DependentSum:
    """
    Dependent sum Σ(x:A). B(x) (dependent pair type).
    
    Special case: A × B when B doesn't depend on x.
    """
    base: HType
    family: str  # B(x)
    
    @property
    def symbol(self) -> str:
        return f"Σ(x:{self.base.name}). {self.family}"
    
    def pair(self, a: str, b: str) -> str:
        """Dependent pair."""
        return f"({a}, {b})"


# ═══════════════════════════════════════════════════════════════════════════════
# IDENTITY TYPES (PATH SPACES)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class IdentityType:
    """
    Identity type a =_A b (path type).
    
    Interpretation: space of paths from a to b in A.
    
    Introduction: refl_a : a =_A a
    Elimination: path induction (J)
    """
    type_A: HType
    left: str
    right: str
    
    @property
    def symbol(self) -> str:
        return f"{self.left} =_{{{self.type_A.name}}} {self.right}"
    
    def refl(self) -> str:
        """Reflexivity path."""
        if self.left == self.right:
            return f"refl_{{{self.left}}}"
        return "∅"  # No canonical path if different
    
    def is_loop(self) -> bool:
        """Check if path is a loop (a = a)."""
        return self.left == self.right


@dataclass
class PathSpace:
    """
    Path space of a type.
    
    Ω(A, a) = (a =_A a) - loop space at a
    """
    base_type: HType
    basepoint: str
    
    @property
    def symbol(self) -> str:
        return f"Ω({self.base_type.name}, {self.basepoint})"
    
    def iterated(self, n: int) -> str:
        """n-fold loop space Ωⁿ."""
        return f"Ω^{n}({self.base_type.name}, {self.basepoint})"
    
    def fundamental_group(self) -> str:
        """π₁(A, a) = ||Ω(A, a)||₀."""
        return f"π₁({self.base_type.name}, {self.basepoint})"


# ═══════════════════════════════════════════════════════════════════════════════
# HOMOTOPY LEVELS (n-TYPES)
# ═══════════════════════════════════════════════════════════════════════════════

class HLevel(Enum):
    """Homotopy levels / truncation levels."""
    CONTRACTIBLE = -2  # Unique point
    PROP = -1          # At most one point (proposition)
    SET = 0            # Discrete (set)
    GROUPOID = 1       # 1-groupoid
    TWO_GROUPOID = 2   # 2-groupoid
    # n-type for any n


@dataclass
class NType:
    """
    n-type: type with trivial homotopy above level n.
    
    - (-2)-type: contractible
    - (-1)-type: proposition (mere proposition)
    - 0-type: set (homotopy set)
    - 1-type: groupoid
    """
    base_type: HType
    level: int
    
    @property
    def symbol(self) -> str:
        if self.level == -2:
            return f"isContr({self.base_type.name})"
        elif self.level == -1:
            return f"isProp({self.base_type.name})"
        elif self.level == 0:
            return f"isSet({self.base_type.name})"
        else:
            return f"is-{self.level}-type({self.base_type.name})"
    
    def truncation(self) -> str:
        """n-truncation ||A||_n."""
        return f"||{self.base_type.name}||_{self.level}"


# ═══════════════════════════════════════════════════════════════════════════════
# UNIVALENCE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Equivalence:
    """
    Type equivalence A ≃ B.
    
    f : A → B is an equivalence if it has:
    - A left inverse g with g ∘ f ~ id_A
    - A right inverse h with f ∘ h ~ id_B
    """
    source: HType
    target: HType
    function: str = "f"
    
    @property
    def symbol(self) -> str:
        return f"{self.source.name} ≃ {self.target.name}"
    
    def is_equiv(self) -> str:
        """isEquiv(f) predicate."""
        return f"isEquiv({self.function})"
    
    def inverse(self) -> str:
        """Inverse equivalence."""
        return f"{self.function}⁻¹"


@dataclass
class UnivalenceAxiom:
    """
    Univalence Axiom: (A ≃ B) ≃ (A = B).
    
    The fundamental axiom of HoTT.
    Equivalence of types is the same as identity of types.
    """
    A: HType
    B: HType
    
    def ua(self) -> str:
        """ua: (A ≃ B) → (A = B)."""
        return f"ua: ({self.A.name} ≃ {self.B.name}) → ({self.A.name} = {self.B.name})"
    
    def transport(self) -> str:
        """Transport along path."""
        return f"transport: {self.A.name} = {self.B.name} → {self.A.name} → {self.B.name}"
    
    def is_equiv_ua(self) -> str:
        """ua is an equivalence."""
        return "isEquiv(ua)"


# ═══════════════════════════════════════════════════════════════════════════════
# HIGHER INDUCTIVE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HigherInductiveType:
    """
    Higher inductive type (HIT).
    
    Defined by:
    - Point constructors (0-cells)
    - Path constructors (1-cells)
    - Higher path constructors (n-cells)
    """
    name: str
    point_constructors: List[str]
    path_constructors: List[str] = field(default_factory=list)
    higher_constructors: List[str] = field(default_factory=list)
    
    @classmethod
    def circle(cls) -> 'HigherInductiveType':
        """
        Circle S¹:
        - base : S¹
        - loop : base = base
        """
        return cls("S¹", ["base"], ["loop : base = base"])
    
    @classmethod
    def sphere(cls, n: int) -> 'HigherInductiveType':
        """
        n-sphere Sⁿ.
        """
        return cls(f"S^{n}", ["base"], [f"surf : refl = refl (in Ω^{{n-1}})"])
    
    @classmethod
    def torus(cls) -> 'HigherInductiveType':
        """
        Torus T²:
        - base : T²
        - p, q : base = base
        - f : p · q = q · p
        """
        return cls("T²", ["base"], ["p : base = base", "q : base = base"],
                  ["f : p · q = q · p"])
    
    @classmethod
    def quotient(cls, A: str, R: str) -> 'HigherInductiveType':
        """
        Quotient A/R.
        """
        return cls(f"{A}/R", [f"[a] for a : {A}"],
                  [f"eq : a R b → [a] = [b]"])


# ═══════════════════════════════════════════════════════════════════════════════
# SYNTHETIC HOMOTOPY THEORY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HomotopyGroup:
    """
    Homotopy group πₙ(A, a).
    
    πₙ(A, a) = ||Ωⁿ(A, a)||₀ (set-truncation of n-fold loops)
    """
    space: HType
    basepoint: str
    n: int
    
    @property
    def symbol(self) -> str:
        return f"π_{self.n}({self.space.name}, {self.basepoint})"
    
    def is_abelian(self) -> bool:
        """πₙ is abelian for n ≥ 2."""
        return self.n >= 2
    
    def loop_space(self) -> str:
        """Corresponding loop space."""
        return f"Ω^{self.n}({self.space.name}, {self.basepoint})"


@dataclass
class Fibration:
    """
    Fibration in HoTT: type family B : A → U.
    
    Total space: Σ(x:A). B(x)
    Fiber over a: B(a)
    """
    base: HType
    fiber_family: str
    
    @property
    def symbol(self) -> str:
        return f"{self.fiber_family} : {self.base.name} → U"
    
    def total_space(self) -> str:
        """Total space Σ(x:A). B(x)."""
        return f"Σ(x:{self.base.name}). {self.fiber_family}(x)"
    
    def fiber(self, a: str) -> str:
        """Fiber B(a)."""
        return f"{self.fiber_family}({a})"
    
    def long_exact_sequence(self) -> str:
        """Long exact sequence of homotopy groups."""
        return "... → πₙ(F) → πₙ(E) → πₙ(B) → π_{n-1}(F) → ..."


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HoTTPoleBridge:
    """
    Bridge between HoTT and pole structure.
    """
    
    @staticmethod
    def psi_pole_as_universe() -> str:
        """
        Ψ-pole (hierarchical) corresponds to universe hierarchy.
        U₀ : U₁ : U₂ : ... is hierarchical structure.
        """
        return "Ψ-pole ↔ Universes: U₀ : U₁ : U₂ : ... hierarchy"
    
    @staticmethod
    def c_pole_as_paths() -> str:
        """
        C-pole (continuous) corresponds to path types.
        Identity types = continuous paths in spaces.
        """
        return "C-pole ↔ Paths: a =_A b continuous identity"
    
    @staticmethod
    def d_pole_as_inductive() -> str:
        """
        D-pole (discrete) corresponds to inductive types.
        Discrete constructors build types step by step.
        """
        return "D-pole ↔ Inductive: data constructors, discrete building"
    
    @staticmethod
    def gateway_as_univalence() -> str:
        """
        Gateway corresponds to univalence.
        (A ≃ B) ≃ (A = B) - equivalence = identity.
        """
        return "Gateway ↔ Univalence: (A ≃ B) ≃ (A = B)"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def htype(name: str, level: int = 0) -> HType:
    """Create a type."""
    return HType(name, level)


def identity_type(A: HType, a: str, b: str) -> IdentityType:
    """Create identity type a =_A b."""
    return IdentityType(A, a, b)


def equivalence(A: HType, B: HType) -> Equivalence:
    """Create equivalence A ≃ B."""
    return Equivalence(A, B)


def circle() -> HigherInductiveType:
    """The circle S¹."""
    return HigherInductiveType.circle()


def sphere(n: int) -> HigherInductiveType:
    """The n-sphere Sⁿ."""
    return HigherInductiveType.sphere(n)


def homotopy_group(A: HType, a: str, n: int) -> HomotopyGroup:
    """Create πₙ(A, a)."""
    return HomotopyGroup(A, a, n)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Types
    'HType',
    'Universe',
    
    # Type formers
    'ProductType',
    'SumType',
    'FunctionType',
    'DependentProduct',
    'DependentSum',
    
    # Identity
    'IdentityType',
    'PathSpace',
    
    # n-types
    'HLevel',
    'NType',
    
    # Univalence
    'Equivalence',
    'UnivalenceAxiom',
    
    # HITs
    'HigherInductiveType',
    
    # Homotopy
    'HomotopyGroup',
    'Fibration',
    
    # Bridge
    'HoTTPoleBridge',
    
    # Functions
    'htype',
    'identity_type',
    'equivalence',
    'circle',
    'sphere',
    'homotopy_group',
]
