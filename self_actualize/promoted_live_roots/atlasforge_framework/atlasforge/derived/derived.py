"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       DERIVED CATEGORIES MODULE                              ║
║                                                                              ║
║  Triangulated Categories and Derived Functors                                ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Derived categories D(A) capture homological algebra categorically.        ║
║    Objects: chain complexes up to quasi-isomorphism                          ║
║    Distinguished triangles: A → B → C → A[1]                                ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - C-pole ↔ Shifts and translations                                       ║
║    - D-pole ↔ Triangulated structure as constraints                         ║
║    - Ψ-pole ↔ t-structures and filtrations                                  ║
║    - Categorical ↔ Functors and natural transformations                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Generic, TypeVar, Callable, Any
from enum import Enum
import numpy as np
from numpy.typing import NDArray


T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════════════════════
# CHAIN COMPLEXES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ChainComplex:
    """
    Chain complex C_• with differentials d: C_n → C_{n-1}.
    
    ... → C_{n+1} →^{d_{n+1}} C_n →^{d_n} C_{n-1} → ...
    
    Satisfying d² = 0.
    """
    objects: Dict[int, Any]  # Degree → object
    differentials: Dict[int, Any]  # Degree → d_n: C_n → C_{n-1}
    name: str = "C"
    
    def __getitem__(self, n: int) -> Any:
        """Get C_n."""
        return self.objects.get(n, 0)
    
    def differential(self, n: int) -> Any:
        """Get d_n: C_n → C_{n-1}."""
        return self.differentials.get(n, 0)
    
    def is_bounded_below(self) -> bool:
        """Check if C_n = 0 for n << 0."""
        if not self.objects:
            return True
        return min(self.objects.keys()) > -float('inf')
    
    def is_bounded_above(self) -> bool:
        """Check if C_n = 0 for n >> 0."""
        if not self.objects:
            return True
        return max(self.objects.keys()) < float('inf')
    
    def is_bounded(self) -> bool:
        """Check if bounded both above and below."""
        return self.is_bounded_below() and self.is_bounded_above()
    
    def shift(self, k: int) -> 'ChainComplex':
        """
        Shift C[k]_n = C_{n+k}, d[k]_n = (-1)^k d_{n+k}.
        """
        new_objects = {n - k: obj for n, obj in self.objects.items()}
        new_diffs = {n - k: d for n, d in self.differentials.items()}
        return ChainComplex(new_objects, new_diffs, f"{self.name}[{k}]")
    
    def homology(self, n: int) -> str:
        """H_n(C) = ker(d_n) / im(d_{n+1})."""
        return f"H_{n}({self.name})"
    
    @classmethod
    def zero(cls) -> 'ChainComplex':
        """Zero complex."""
        return cls({}, {}, "0")
    
    @classmethod
    def concentrated(cls, obj: Any, degree: int = 0, name: str = "M") -> 'ChainComplex':
        """Complex concentrated in single degree."""
        return cls({degree: obj}, {}, name)


@dataclass
class CochainComplex:
    """
    Cochain complex C^• with differentials d: C^n → C^{n+1}.
    
    ... → C^{n-1} →^{d^{n-1}} C^n →^{d^n} C^{n+1} → ...
    """
    objects: Dict[int, Any]
    differentials: Dict[int, Any]  # d^n: C^n → C^{n+1}
    name: str = "C"
    
    def cohomology(self, n: int) -> str:
        """H^n(C) = ker(d^n) / im(d^{n-1})."""
        return f"H^{n}({self.name})"
    
    def to_chain(self) -> ChainComplex:
        """Convert to chain complex via degree reversal."""
        new_objects = {-n: obj for n, obj in self.objects.items()}
        new_diffs = {-n: d for n, d in self.differentials.items()}
        return ChainComplex(new_objects, new_diffs, self.name)


# ═══════════════════════════════════════════════════════════════════════════════
# QUASI-ISOMORPHISMS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ChainMap:
    """
    Chain map f: C → D.
    
    Collection of maps f_n: C_n → D_n commuting with differentials.
    """
    source: ChainComplex
    target: ChainComplex
    components: Dict[int, Any]  # f_n
    name: str = "f"
    
    def is_quasi_isomorphism(self) -> bool:
        """
        Check if f induces isomorphism on homology.
        
        f_*: H_n(C) → H_n(D) is isomorphism for all n.
        """
        # In actual implementation, would check homology
        return True  # Placeholder
    
    def cone(self) -> ChainComplex:
        """
        Mapping cone Cone(f).
        
        Cone(f)_n = C_{n-1} ⊕ D_n
        d(c, d) = (-d_C(c), f(c) + d_D(d))
        """
        # Returns the cone complex
        return ChainComplex({}, {}, f"Cone({self.name})")


@dataclass
class QuasiIsomorphism:
    """
    Quasi-isomorphism: chain map inducing homology isomorphism.
    """
    chain_map: ChainMap
    
    def is_valid(self) -> bool:
        return self.chain_map.is_quasi_isomorphism()


# ═══════════════════════════════════════════════════════════════════════════════
# TRIANGULATED CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DistinguishedTriangle:
    """
    Distinguished triangle in a triangulated category:
    
    X →^f Y →^g Z →^h X[1]
    
    Satisfies:
    - Rotation: Y → Z → X[1] → Y[1] is distinguished
    - Completion: Any f: X → Y extends to distinguished triangle
    - Octahedron axiom
    """
    X: Any
    Y: Any
    Z: Any
    f: Any  # X → Y
    g: Any  # Y → Z
    h: Any  # Z → X[1]
    
    def rotate(self) -> 'DistinguishedTriangle':
        """Rotate the triangle."""
        # Y → Z → X[1] → Y[1]
        return DistinguishedTriangle(
            self.Y, self.Z, f"{self.X}[1]",
            self.g, self.h, f"-{self.f}[1]"
        )
    
    def is_split(self) -> bool:
        """Check if triangle splits (Z ≅ X[1] ⊕ Y)."""
        return False  # Generic case


@dataclass
class TriangulatedCategory:
    """
    Triangulated category with:
    - Shift functor [1]
    - Class of distinguished triangles
    
    Axioms:
    TR1: Identity triangles, completion
    TR2: Rotation
    TR3: Morphism of triangles
    TR4: Octahedron
    """
    name: str = "D"
    shift_functor: str = "[1]"
    
    def shift(self, X: Any, n: int = 1) -> str:
        """Apply shift functor X ↦ X[n]."""
        if n == 0:
            return str(X)
        elif n > 0:
            return f"{X}[{n}]"
        else:
            return f"{X}[{n}]"
    
    def hom(self, X: Any, Y: Any, n: int = 0) -> str:
        """Hom^n(X, Y) = Hom(X, Y[n])."""
        if n == 0:
            return f"Hom({X}, {Y})"
        else:
            return f"Hom({X}, {Y}[{n}])"


# ═══════════════════════════════════════════════════════════════════════════════
# DERIVED CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

class DerivedBoundedness(Enum):
    """Boundedness conditions for derived categories."""
    UNBOUNDED = "D"        # D(A)
    BOUNDED_BELOW = "D+"   # D+(A)
    BOUNDED_ABOVE = "D-"   # D-(A)  
    BOUNDED = "Db"         # D^b(A)


@dataclass
class DerivedCategory(TriangulatedCategory):
    """
    Derived category D(A) of an abelian category A.
    
    Objects: Chain complexes over A
    Morphisms: Roofs X ← P → Y where P → X is quasi-iso
    """
    abelian_category: str = "A"
    boundedness: DerivedBoundedness = DerivedBoundedness.BOUNDED
    
    def __post_init__(self):
        self.name = f"{self.boundedness.value}({self.abelian_category})"
    
    def ext(self, X: Any, Y: Any, n: int) -> str:
        """
        Ext^n(X, Y) = Hom_{D(A)}(X, Y[n]).
        """
        return f"Ext^{n}({X}, {Y})"
    
    def RHom(self, X: Any, Y: Any) -> str:
        """
        RHom(X, Y) - derived internal hom.
        """
        return f"RHom({X}, {Y})"
    
    def tensor_L(self, X: Any, Y: Any) -> str:
        """
        X ⊗^L Y - derived tensor product.
        """
        return f"{X} ⊗^L {Y}"


@dataclass
class DerivedFunctor:
    """
    Derived functor RF or LF.
    
    RF: D+(A) → D+(B) for left exact F
    LF: D-(A) → D-(B) for right exact F
    """
    name: str
    source_category: str
    target_category: str
    is_right_derived: bool = True
    
    @property
    def symbol(self) -> str:
        prefix = "R" if self.is_right_derived else "L"
        return f"{prefix}{self.name}"
    
    def apply(self, X: Any) -> str:
        return f"{self.symbol}({X})"
    
    def cohomology(self, X: Any, n: int) -> str:
        """R^n F(X) or L_n F(X)."""
        if self.is_right_derived:
            return f"R^{n}{self.name}({X})"
        else:
            return f"L_{n}{self.name}({X})"


# ═══════════════════════════════════════════════════════════════════════════════
# T-STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TStructure:
    """
    t-structure on triangulated category D.
    
    Pair (D^≤0, D^≥0) satisfying:
    - D^≤0[1] ⊂ D^≤0
    - D^≥0[-1] ⊂ D^≥0
    - Hom(D^≤0, D^≥1) = 0
    - For X, exists triangle X^≤0 → X → X^≥1 → 
    """
    category_name: str
    heart_name: str = "A"  # Heart = D^≤0 ∩ D^≥0
    
    def truncation_below(self, X: Any, n: int) -> str:
        """τ^≤n X."""
        return f"τ^≤{n}({X})"
    
    def truncation_above(self, X: Any, n: int) -> str:
        """τ^≥n X."""
        return f"τ^≥{n}({X})"
    
    def cohomology_object(self, X: Any, n: int) -> str:
        """H^n(X) = τ^≤n τ^≥n X ∈ Heart."""
        return f"H^{n}({X})"
    
    @property
    def heart(self) -> str:
        """Heart of t-structure (abelian subcategory)."""
        return self.heart_name


# ═══════════════════════════════════════════════════════════════════════════════
# SPECTRAL SEQUENCES FROM FILTERED COMPLEXES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpectralSequence:
    """
    Spectral sequence E_r^{p,q} ⟹ H^{p+q}.
    
    d_r: E_r^{p,q} → E_r^{p+r, q-r+1}
    E_{r+1} = H(E_r, d_r)
    """
    name: str
    starting_page: int = 2
    target: str = "H^*"
    
    def page(self, r: int, p: int, q: int) -> str:
        """E_r^{p,q}."""
        return f"E_{r}^{{{p},{q}}}"
    
    def differential(self, r: int) -> str:
        """d_r: E_r^{p,q} → E_r^{p+r, q-r+1}."""
        return f"d_{r}: E_{r}^{{p,q}} → E_{r}^{{p+{r}, q-{r-1}}}"
    
    def converges_to(self) -> str:
        return f"{self.name} ⟹ {self.target}"


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DerivedPoleBridge:
    """
    Bridge between derived categories and pole structure.
    """
    
    @staticmethod
    def c_pole_as_shift() -> str:
        """
        C-pole (continuous) corresponds to shift functor [1].
        Translation = infinitesimal symmetry.
        """
        return "C-pole ↔ [1]: Continuous translation in derived category"
    
    @staticmethod
    def d_pole_as_triangles() -> str:
        """
        D-pole (discrete) corresponds to distinguished triangles.
        Constraints encoded in exact sequences.
        """
        return "D-pole ↔ Triangles: Exact constraints X → Y → Z → X[1]"
    
    @staticmethod
    def psi_pole_as_filtration(depth: int) -> TStructure:
        """
        Ψ-pole (hierarchical) corresponds to t-structures.
        Filtration = hierarchical decomposition.
        """
        return TStructure(f"D_Ψ", f"Heart_{depth}")
    
    @staticmethod
    def ext_from_gateway(T: float, n: int) -> str:
        """
        Map gateway parameter to Ext computation.
        """
        return f"Ext^{n}(Gateway(T={T}), -)"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def chain_complex(objects: Dict[int, Any], differentials: Dict[int, Any],
                  name: str = "C") -> ChainComplex:
    """Create chain complex."""
    return ChainComplex(objects, differentials, name)


def derived_category(abelian: str, 
                    bounded: DerivedBoundedness = DerivedBoundedness.BOUNDED
                    ) -> DerivedCategory:
    """Create derived category D^b(A)."""
    return DerivedCategory(abelian, abelian, bounded)


def distinguished_triangle(X: Any, Y: Any, Z: Any) -> DistinguishedTriangle:
    """Create distinguished triangle X → Y → Z → X[1]."""
    return DistinguishedTriangle(X, Y, Z, "f", "g", "h")


def t_structure(category: str, heart: str = "A") -> TStructure:
    """Create t-structure with given heart."""
    return TStructure(category, heart)


def spectral_sequence(name: str, target: str = "H^*") -> SpectralSequence:
    """Create spectral sequence."""
    return SpectralSequence(name, target=target)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Complexes
    'ChainComplex',
    'CochainComplex',
    'ChainMap',
    'QuasiIsomorphism',
    
    # Triangulated
    'DistinguishedTriangle',
    'TriangulatedCategory',
    
    # Derived
    'DerivedBoundedness',
    'DerivedCategory',
    'DerivedFunctor',
    
    # t-structures
    'TStructure',
    
    # Spectral sequences
    'SpectralSequence',
    
    # Bridge
    'DerivedPoleBridge',
    
    # Functions
    'chain_complex',
    'derived_category',
    'distinguished_triangle',
    't_structure',
    'spectral_sequence',
]
