"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       CATEGORY THEORY MODULE                                 ║
║                                                                              ║
║  The Language of Modern Mathematics                                          ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Categories organize mathematical structures via objects and morphisms.    ║
║    Functors preserve structure; natural transformations compare functors.    ║
║    Universal properties characterize objects up to unique isomorphism.       ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Ψ-pole ↔ Adjoint functors (hierarchical structure)                     ║
║    - Σ-pole ↔ Kan extensions (universal approximations)                     ║
║    - C-pole ↔ Continuous functors (preserve limits)                         ║
║    - D-pole ↔ Discrete categories, finite diagrams                          ║
║    - Gateway ↔ Duality: C ↔ C^op                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Optional, Tuple, List, Dict, Set, Any, Callable, 
    TypeVar, Generic, Union, Iterator
)
from enum import Enum, auto
import numpy as np


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Object:
    """Object in a category."""
    name: str
    category: Optional[str] = None
    
    def __hash__(self):
        return hash((self.name, self.category))
    
    def __eq__(self, other):
        if not isinstance(other, Object):
            return False
        return self.name == other.name and self.category == other.category
    
    def __repr__(self):
        return self.name


@dataclass
class Morphism:
    """Morphism f: A → B in a category."""
    source: Object
    target: Object
    name: str = "f"
    
    def __repr__(self):
        return f"{self.name}: {self.source} → {self.target}"
    
    def __hash__(self):
        return hash((self.name, self.source, self.target))
    
    def compose(self, other: 'Morphism') -> 'Morphism':
        """Composition g ∘ f where self = f, other = g."""
        if self.target != other.source:
            raise ValueError(f"Cannot compose: {self.target} ≠ {other.source}")
        return Morphism(self.source, other.target, f"{other.name}∘{self.name}")
    
    def __matmul__(self, other: 'Morphism') -> 'Morphism':
        """Use @ for composition: g @ f = g ∘ f."""
        return other.compose(self)


@dataclass
class Category:
    """
    A category C consists of:
    - A collection of objects Ob(C)
    - For each pair (A, B), a set Hom(A, B) of morphisms
    - Composition ∘: Hom(B, C) × Hom(A, B) → Hom(A, C)
    - Identity morphisms id_A for each object A
    
    Satisfying associativity and identity laws.
    """
    name: str
    objects: Set[Object] = field(default_factory=set)
    morphisms: Set[Morphism] = field(default_factory=set)
    
    def add_object(self, obj: Object) -> None:
        """Add an object to the category."""
        obj.category = self.name
        self.objects.add(obj)
    
    def add_morphism(self, mor: Morphism) -> None:
        """Add a morphism to the category."""
        self.objects.add(mor.source)
        self.objects.add(mor.target)
        self.morphisms.add(mor)
    
    def identity(self, obj: Object) -> Morphism:
        """Identity morphism id_A: A → A."""
        return Morphism(obj, obj, f"id_{obj.name}")
    
    def hom(self, A: Object, B: Object) -> Set[Morphism]:
        """Hom set Hom(A, B)."""
        return {m for m in self.morphisms if m.source == A and m.target == B}
    
    def opposite(self) -> 'Category':
        """Opposite category C^op with reversed morphisms."""
        op = Category(f"{self.name}^op")
        op.objects = self.objects.copy()
        for m in self.morphisms:
            op.morphisms.add(Morphism(m.target, m.source, f"{m.name}^op"))
        return op
    
    def product(self, other: 'Category') -> 'Category':
        """Product category C × D."""
        prod = Category(f"{self.name}×{other.name}")
        for A in self.objects:
            for B in other.objects:
                prod.add_object(Object(f"({A.name},{B.name})"))
        return prod
    
    @classmethod
    def discrete(cls, objects: List[str]) -> 'Category':
        """Discrete category with only identity morphisms."""
        cat = cls("Discrete")
        for name in objects:
            cat.add_object(Object(name))
        return cat
    
    @classmethod
    def arrow(cls) -> 'Category':
        """Arrow category 2 = (• → •)."""
        cat = cls("2")
        A, B = Object("0"), Object("1")
        cat.add_object(A)
        cat.add_object(B)
        cat.add_morphism(Morphism(A, B, "→"))
        return cat


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Functor:
    """
    Functor F: C → D mapping:
    - Objects: A ↦ F(A)
    - Morphisms: (f: A → B) ↦ (F(f): F(A) → F(B))
    
    Preserving composition and identities.
    """
    name: str
    source_category: str
    target_category: str
    object_map: Dict[Object, Object] = field(default_factory=dict)
    morphism_map: Dict[Morphism, Morphism] = field(default_factory=dict)
    is_contravariant: bool = False
    
    def __call__(self, x: Union[Object, Morphism]) -> Union[Object, Morphism]:
        """Apply functor to object or morphism."""
        if isinstance(x, Object):
            return self.object_map.get(x, Object(f"{self.name}({x.name})"))
        else:
            return self.morphism_map.get(x, Morphism(
                self(x.source), self(x.target), f"{self.name}({x.name})"
            ))
    
    def compose(self, other: 'Functor') -> 'Functor':
        """Composition G ∘ F."""
        composed = Functor(
            f"{other.name}∘{self.name}",
            self.source_category,
            other.target_category
        )
        for obj, img in self.object_map.items():
            composed.object_map[obj] = other(img)
        return composed
    
    @classmethod
    def identity(cls, category: str) -> 'Functor':
        """Identity functor Id_C."""
        return cls(f"Id_{category}", category, category)
    
    @classmethod
    def constant(cls, source: str, target_obj: Object) -> 'Functor':
        """Constant functor Δ_X sending everything to X."""
        return cls(f"Δ_{target_obj.name}", source, target_obj.category or "")
    
    @classmethod
    def hom_functor(cls, A: Object, category: str) -> 'Functor':
        """Representable functor Hom(A, -)."""
        return cls(f"Hom({A.name},-)", category, "Set", is_contravariant=False)
    
    @classmethod
    def contravariant_hom(cls, B: Object, category: str) -> 'Functor':
        """Contravariant representable Hom(-, B)."""
        return cls(f"Hom(-,{B.name})", category, "Set", is_contravariant=True)


# ═══════════════════════════════════════════════════════════════════════════════
# NATURAL TRANSFORMATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NaturalTransformation:
    """
    Natural transformation η: F ⟹ G between functors F, G: C → D.
    
    Components η_A: F(A) → G(A) for each object A ∈ C
    satisfying naturality: G(f) ∘ η_A = η_B ∘ F(f) for all f: A → B.
    """
    name: str
    source_functor: Functor
    target_functor: Functor
    components: Dict[Object, Morphism] = field(default_factory=dict)
    
    def __getitem__(self, obj: Object) -> Morphism:
        """Get component η_A."""
        return self.components.get(obj, Morphism(
            self.source_functor(obj),
            self.target_functor(obj),
            f"{self.name}_{obj.name}"
        ))
    
    def is_natural_isomorphism(self) -> bool:
        """Check if all components are isomorphisms."""
        # Would need inverse checking
        return True  # Placeholder
    
    def vertical_compose(self, other: 'NaturalTransformation') -> 'NaturalTransformation':
        """Vertical composition β ∘ η: F ⟹ H."""
        composed = NaturalTransformation(
            f"{other.name}∘{self.name}",
            self.source_functor,
            other.target_functor
        )
        for obj in self.components:
            composed.components[obj] = self[obj].compose(other[obj])
        return composed
    
    @classmethod
    def identity(cls, F: Functor) -> 'NaturalTransformation':
        """Identity natural transformation id_F: F ⟹ F."""
        return cls(f"id_{F.name}", F, F)


# ═══════════════════════════════════════════════════════════════════════════════
# LIMITS AND COLIMITS
# ═══════════════════════════════════════════════════════════════════════════════

class LimitType(Enum):
    """Types of limits and colimits."""
    PRODUCT = auto()
    COPRODUCT = auto()
    EQUALIZER = auto()
    COEQUALIZER = auto()
    PULLBACK = auto()
    PUSHOUT = auto()
    TERMINAL = auto()
    INITIAL = auto()
    LIMIT = auto()
    COLIMIT = auto()


@dataclass
class UniversalCone:
    """
    Universal cone (limit) of a diagram D: J → C.
    
    Consists of:
    - Apex object L
    - Projection morphisms π_j: L → D(j) for each j ∈ J
    - Universal property: unique factorization
    """
    apex: Object
    projections: Dict[Object, Morphism]
    diagram_shape: str
    limit_type: LimitType = LimitType.LIMIT
    
    @classmethod
    def product(cls, A: Object, B: Object) -> 'UniversalCone':
        """Product A × B with projections π₁, π₂."""
        apex = Object(f"{A.name}×{B.name}")
        return cls(
            apex,
            {A: Morphism(apex, A, "π₁"), B: Morphism(apex, B, "π₂")},
            "•  •",
            LimitType.PRODUCT
        )
    
    @classmethod
    def equalizer(cls, f: Morphism, g: Morphism) -> 'UniversalCone':
        """Equalizer eq(f, g) where f, g: A → B."""
        apex = Object(f"eq({f.name},{g.name})")
        return cls(
            apex,
            {f.source: Morphism(apex, f.source, "e")},
            "• ⇉ •",
            LimitType.EQUALIZER
        )
    
    @classmethod
    def pullback(cls, f: Morphism, g: Morphism) -> 'UniversalCone':
        """Pullback A ×_C B where f: A → C, g: B → C."""
        apex = Object(f"{f.source.name}×_{f.target.name}{g.source.name}")
        return cls(
            apex,
            {
                f.source: Morphism(apex, f.source, "p₁"),
                g.source: Morphism(apex, g.source, "p₂")
            },
            "pullback square",
            LimitType.PULLBACK
        )
    
    @classmethod
    def terminal(cls, category: str) -> 'UniversalCone':
        """Terminal object 1."""
        return cls(Object("1"), {}, "empty", LimitType.TERMINAL)


@dataclass
class UniversalCocone:
    """
    Universal cocone (colimit) of a diagram D: J → C.
    """
    apex: Object
    injections: Dict[Object, Morphism]
    diagram_shape: str
    colimit_type: LimitType = LimitType.COLIMIT
    
    @classmethod
    def coproduct(cls, A: Object, B: Object) -> 'UniversalCocone':
        """Coproduct A ⊔ B with injections ι₁, ι₂."""
        apex = Object(f"{A.name}⊔{B.name}")
        return cls(
            apex,
            {A: Morphism(A, apex, "ι₁"), B: Morphism(B, apex, "ι₂")},
            "•  •",
            LimitType.COPRODUCT
        )
    
    @classmethod
    def coequalizer(cls, f: Morphism, g: Morphism) -> 'UniversalCocone':
        """Coequalizer coeq(f, g)."""
        apex = Object(f"coeq({f.name},{g.name})")
        return cls(
            apex,
            {f.target: Morphism(f.target, apex, "q")},
            "• ⇉ •",
            LimitType.COEQUALIZER
        )
    
    @classmethod
    def pushout(cls, f: Morphism, g: Morphism) -> 'UniversalCocone':
        """Pushout A ⊔_C B where f: C → A, g: C → B."""
        apex = Object(f"{f.target.name}⊔_{f.source.name}{g.target.name}")
        return cls(
            apex,
            {
                f.target: Morphism(f.target, apex, "i₁"),
                g.target: Morphism(g.target, apex, "i₂")
            },
            "pushout square",
            LimitType.PUSHOUT
        )
    
    @classmethod
    def initial(cls, category: str) -> 'UniversalCocone':
        """Initial object 0."""
        return cls(Object("0"), {}, "empty", LimitType.INITIAL)


# ═══════════════════════════════════════════════════════════════════════════════
# ADJUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Adjunction:
    """
    Adjunction F ⊣ G between categories C and D.
    
    F: C → D is left adjoint to G: D → C
    
    Characterized by natural isomorphism:
    Hom_D(F(A), B) ≅ Hom_C(A, G(B))
    
    With unit η: Id_C ⟹ GF and counit ε: FG ⟹ Id_D.
    """
    left_adjoint: Functor
    right_adjoint: Functor
    unit: Optional[NaturalTransformation] = None
    counit: Optional[NaturalTransformation] = None
    
    @property
    def symbol(self) -> str:
        return f"{self.left_adjoint.name} ⊣ {self.right_adjoint.name}"
    
    def triangle_identities(self) -> Tuple[str, str]:
        """
        Triangle identities:
        (εF) ∘ (Fη) = id_F
        (Gε) ∘ (ηG) = id_G
        """
        return (
            f"(ε{self.left_adjoint.name}) ∘ ({self.left_adjoint.name}η) = id",
            f"({self.right_adjoint.name}ε) ∘ (η{self.right_adjoint.name}) = id"
        )
    
    @classmethod
    def free_forgetful(cls, free_name: str = "F", forgetful_name: str = "U") -> 'Adjunction':
        """Free-forgetful adjunction F ⊣ U."""
        F = Functor(free_name, "Set", "Grp")
        U = Functor(forgetful_name, "Grp", "Set")
        return cls(F, U)


# ═══════════════════════════════════════════════════════════════════════════════
# KAN EXTENSIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KanExtension:
    """
    Kan extension of F: C → E along K: C → D.
    
    Left Kan extension Lan_K F: D → E
    Right Kan extension Ran_K F: D → E
    
    Universal property makes Kan extensions "best approximations".
    """
    original_functor: Functor  # F: C → E
    along_functor: Functor      # K: C → D
    is_left: bool = True
    extension: Optional[Functor] = None
    
    @property
    def name(self) -> str:
        prefix = "Lan" if self.is_left else "Ran"
        return f"{prefix}_{self.along_functor.name}({self.original_functor.name})"
    
    @property  
    def pointwise_formula(self) -> str:
        """Pointwise formula for Kan extensions."""
        if self.is_left:
            return f"(Lan_K F)(d) = colim_{{(c,k)∈(K↓d)}} F(c)"
        else:
            return f"(Ran_K F)(d) = lim_{{(c,k)∈(d↓K)}} F(c)"


# ═══════════════════════════════════════════════════════════════════════════════
# YONEDA LEMMA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class YonedaEmbedding:
    """
    Yoneda embedding y: C → [C^op, Set].
    
    y(A) = Hom(-, A)
    
    Yoneda Lemma: Nat(Hom(-, A), F) ≅ F(A)
    """
    category_name: str
    
    def embed(self, A: Object) -> Functor:
        """Yoneda embedding y(A) = Hom(-, A)."""
        return Functor.contravariant_hom(A, self.category_name)
    
    def yoneda_lemma(self, A: Object, F: Functor) -> str:
        """Statement of Yoneda lemma."""
        return f"Nat(Hom(-, {A.name}), {F.name}) ≅ {F.name}({A.name})"
    
    def is_fully_faithful(self) -> bool:
        """Yoneda embedding is fully faithful."""
        return True
    
    def presheaf_category(self) -> str:
        """Target presheaf category."""
        return f"[{self.category_name}^op, Set]"


# ═══════════════════════════════════════════════════════════════════════════════
# MONOIDAL CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MonoidalStructure:
    """
    Monoidal structure on a category C.
    
    (C, ⊗, I, α, λ, ρ) where:
    - ⊗: C × C → C is the tensor product
    - I is the unit object
    - α: (A ⊗ B) ⊗ C → A ⊗ (B ⊗ C) is associator
    - λ: I ⊗ A → A is left unitor
    - ρ: A ⊗ I → A is right unitor
    """
    category_name: str
    tensor_symbol: str = "⊗"
    unit_object: Object = field(default_factory=lambda: Object("I"))
    is_symmetric: bool = False
    is_closed: bool = False
    
    def tensor(self, A: Object, B: Object) -> Object:
        """Tensor product A ⊗ B."""
        return Object(f"{A.name}{self.tensor_symbol}{B.name}")
    
    def internal_hom(self, A: Object, B: Object) -> Object:
        """Internal hom [A, B] (if closed)."""
        if not self.is_closed:
            raise ValueError("Category is not closed monoidal")
        return Object(f"[{A.name},{B.name}]")
    
    def braiding(self, A: Object, B: Object) -> Morphism:
        """Braiding σ: A ⊗ B → B ⊗ A (if symmetric)."""
        if not self.is_symmetric:
            raise ValueError("Category is not symmetric")
        return Morphism(
            self.tensor(A, B),
            self.tensor(B, A),
            "σ"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY-CATEGORY BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GatewayCategoryBridge:
    """
    Bridge between gateway algebra and category theory.
    """
    
    @staticmethod
    def opposite_as_reflection() -> str:
        """
        Gateway T ↔ -T corresponds to C ↔ C^op.
        Duality is the categorical reflection.
        """
        return "T ↔ -T ~ C ↔ C^op (categorical duality)"
    
    @staticmethod
    def adjunction_from_gateway(T: float) -> Adjunction:
        """
        Gateway parameter encodes adjunction data.
        """
        F = Functor("F_T", "C", "D")
        G = Functor("G_T", "D", "C")
        return Adjunction(F, G)
    
    @staticmethod
    def poles_as_limits() -> Dict[str, str]:
        """
        Each pole corresponds to limit/colimit behavior.
        """
        return {
            "Ψ": "Inverse limits (projective systems)",
            "Σ": "Filtered colimits (inductive systems)",
            "C": "Continuous functors (preserve limits)",
            "D": "Finite limits (discrete diagrams)"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def category(name: str) -> Category:
    """Create a category."""
    return Category(name)


def obj(name: str, cat: Optional[str] = None) -> Object:
    """Create an object."""
    return Object(name, cat)


def morphism(source: Object, target: Object, name: str = "f") -> Morphism:
    """Create a morphism."""
    return Morphism(source, target, name)


def functor(name: str, source: str, target: str) -> Functor:
    """Create a functor."""
    return Functor(name, source, target)


def product_cone(A: Object, B: Object) -> UniversalCone:
    """Create product cone."""
    return UniversalCone.product(A, B)


def coproduct_cocone(A: Object, B: Object) -> UniversalCocone:
    """Create coproduct cocone."""
    return UniversalCocone.coproduct(A, B)


def adjunction(left: Functor, right: Functor) -> Adjunction:
    """Create adjunction F ⊣ G."""
    return Adjunction(left, right)


def yoneda(category: str) -> YonedaEmbedding:
    """Create Yoneda embedding."""
    return YonedaEmbedding(category)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core
    'Object',
    'Morphism', 
    'Category',
    
    # Functors
    'Functor',
    'NaturalTransformation',
    
    # Limits
    'LimitType',
    'UniversalCone',
    'UniversalCocone',
    
    # Adjunctions
    'Adjunction',
    'KanExtension',
    
    # Yoneda
    'YonedaEmbedding',
    
    # Monoidal
    'MonoidalStructure',
    
    # Bridge
    'GatewayCategoryBridge',
    
    # Functions
    'category',
    'obj',
    'morphism',
    'functor',
    'product_cone',
    'coproduct_cocone',
    'adjunction',
    'yoneda',
]
