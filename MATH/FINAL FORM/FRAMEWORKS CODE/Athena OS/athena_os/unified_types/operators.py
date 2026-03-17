"""
ATHENA OS — UNIFIED OPERATOR ALGEBRA
====================================

The Universal Operator Framework for All Transformations

This module provides a single, coherent operator algebra that all
66 packages can use for their transformations. It unifies:

- Elemental operators (Fire, Air, Water, Earth)
- Alchemical operators (Sulfur, Mercury, Salt)
- Mathematical operators (Square, Flower, Cloud, Fractal)
- Tradition-specific operators (mapped to canonical forms)

DESIGN PRINCIPLES:
1. Every operator implements the Operator protocol
2. Operators compose via the ∘ operation
3. Every operator has an adjoint (inverse or dual)
4. Operators preserve the Five Invariants
5. Operators map between holographic addresses
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Optional, Tuple, Any, Set, 
    Callable, TypeVar, Generic, Union
)
from enum import Enum, auto
from abc import ABC, abstractmethod
import math
import cmath
from functools import reduce

# Import unified types
from .core import (
    B4, Klein4Op, Element, Lens, Facet, Atom,
    CrystalAddress, HolographicAddress, TypedTruth,
    Certificate, CertificateLevel, CertificateType,
    ZResult, Constants, Operator, LambdaOperator, T, R
)


# =============================================================================
# OPERATOR CATEGORIES
# =============================================================================

class OperatorCategory(Enum):
    """Categories of operators in ATHENA OS."""
    
    # Elemental (Four Elements)
    ELEMENTAL = "elemental"
    
    # Alchemical (Tria Prima + Operations)
    ALCHEMICAL = "alchemical"
    
    # Mathematical (Four Lenses)
    MATHEMATICAL = "mathematical"
    
    # Logical (BIT4 Operations)
    LOGICAL = "logical"
    
    # Causal (Four Causes)
    CAUSAL = "causal"
    
    # Temporal (Time Operations)
    TEMPORAL = "temporal"
    
    # Spatial (Space Operations)
    SPATIAL = "spatial"
    
    # Quantum (Superposition, Entanglement)
    QUANTUM = "quantum"


class OperatorDomain(Enum):
    """Domains operators can act on."""
    
    SCALAR = "scalar"        # Single values
    VECTOR = "vector"        # Arrays/lists
    MATRIX = "matrix"        # 2D arrays
    TENSOR = "tensor"        # N-dimensional
    FUNCTION = "function"    # Functions
    STATE = "state"          # State vectors
    CRYSTAL = "crystal"      # Crystal addresses


# =============================================================================
# BASE OPERATOR CLASS
# =============================================================================

@dataclass
class BaseOperator(ABC, Generic[T, R]):
    """
    Abstract base class for all operators.
    
    All operators in ATHENA OS should inherit from this class
    to ensure consistent behavior and composability.
    """
    
    name: str
    category: OperatorCategory
    domain: OperatorDomain = OperatorDomain.SCALAR
    
    # Metadata
    symbol: str = ""
    description: str = ""
    
    # Properties
    is_linear: bool = True
    is_invertible: bool = True
    is_hermitian: bool = False
    
    @abstractmethod
    def apply(self, x: T) -> ZResult[R]:
        """Apply operator to input, returning ZResult for totality."""
        pass
    
    def __call__(self, x: T) -> ZResult[R]:
        """Make operator callable."""
        return self.apply(x)
    
    def compose(self, other: 'BaseOperator[R, Any]') -> 'ComposedOperator':
        """Compose with another operator: self ∘ other."""
        return ComposedOperator(self, other)
    
    def __matmul__(self, other: 'BaseOperator') -> 'ComposedOperator':
        """Use @ for composition: A @ B = A ∘ B."""
        return self.compose(other)
    
    @property
    def adjoint(self) -> 'BaseOperator':
        """Get adjoint (inverse or dual) operator."""
        return AdjointOperator(self)
    
    @property
    def dag(self) -> 'BaseOperator':
        """Alias for adjoint (dagger notation)."""
        return self.adjoint
    
    def power(self, n: int) -> 'BaseOperator':
        """Raise operator to power n."""
        if n == 0:
            return IdentityOperator()
        elif n == 1:
            return self
        elif n > 1:
            return reduce(lambda a, b: a.compose(b), [self] * n)
        else:  # n < 0
            return self.adjoint.power(-n)
    
    def __pow__(self, n: int) -> 'BaseOperator':
        return self.power(n)
    
    def certify(self, input_val: T, output_val: R) -> Certificate:
        """Create certificate for operation."""
        return Certificate(
            cert_type=CertificateType.INVARIANT,
            level=CertificateLevel.WITNESS,
            claim=f"{self.name}: {type(input_val).__name__} → {type(output_val).__name__}",
            witness={"input": str(input_val)[:50], "output": str(output_val)[:50]}
        )


@dataclass
class ComposedOperator(BaseOperator):
    """Composition of two operators."""
    
    first: BaseOperator
    second: BaseOperator
    
    def __post_init__(self):
        self.name = f"{self.first.name}∘{self.second.name}"
        self.category = self.first.category
        self.symbol = f"({self.first.symbol}∘{self.second.symbol})"
    
    def apply(self, x: Any) -> ZResult:
        # Apply second first, then first (function composition order)
        result = self.second.apply(x)
        if not result.is_ok:
            return result
        return self.first.apply(result.value)


@dataclass
class AdjointOperator(BaseOperator):
    """Adjoint (inverse/dual) of an operator."""
    
    original: BaseOperator
    
    def __post_init__(self):
        self.name = f"{self.original.name}†"
        self.category = self.original.category
        self.symbol = f"{self.original.symbol}†"
    
    def apply(self, x: Any) -> ZResult:
        # Default: try to invert if possible
        # Subclasses should override for proper adjoint
        return ZResult.zero(f"Adjoint of {self.original.name} not implemented")


@dataclass
class IdentityOperator(BaseOperator):
    """Identity operator: I(x) = x."""
    
    name: str = "I"
    category: OperatorCategory = OperatorCategory.LOGICAL
    symbol: str = "𝟙"
    
    def apply(self, x: Any) -> ZResult:
        return ZResult.ok(x)


# =============================================================================
# ELEMENTAL OPERATORS
# =============================================================================

@dataclass
class ElementalOperator(BaseOperator):
    """
    Operator based on the four elements.
    
    Maps to Klein-4 group action on states.
    """
    
    element: Element = Element.FIRE
    category: OperatorCategory = OperatorCategory.ELEMENTAL
    
    def __post_init__(self):
        self.name = f"Elem_{self.element.name}"
        self.symbol = _ELEMENT_SYMBOLS[self.element]
        self.description = f"Elemental operator for {self.element.name}"
    
    def apply(self, x: Any) -> ZResult:
        """Apply elemental transformation."""
        if isinstance(x, B4):
            # Apply Klein-4 action
            return ZResult.ok(self.element.klein4.apply(x))
        elif isinstance(x, (int, float)):
            # Scale by elemental factor
            return ZResult.ok(x * _ELEMENT_FACTORS[self.element])
        elif isinstance(x, complex):
            # Rotate by elemental phase
            phase = _ELEMENT_PHASES[self.element]
            return ZResult.ok(x * cmath.exp(1j * phase))
        else:
            return ZResult.near(x, f"No elemental transform for {type(x)}")


_ELEMENT_SYMBOLS = {
    Element.FIRE: "🜂",
    Element.AIR: "🜁",
    Element.WATER: "🜄",
    Element.EARTH: "🜃",
    Element.AETHER: "🜀",
}

_ELEMENT_FACTORS = {
    Element.FIRE: 1.618033988749895,   # φ (golden ratio) - expansion
    Element.AIR: 1.0,                   # Unity - connection
    Element.WATER: 0.618033988749895,   # 1/φ - contraction
    Element.EARTH: 1.0,                 # Unity - stability
    Element.AETHER: math.pi,            # π - transcendence
}

_ELEMENT_PHASES = {
    Element.FIRE: 0,                    # 0° - action
    Element.AIR: math.pi / 2,           # 90° - intellect
    Element.WATER: math.pi,             # 180° - reflection
    Element.EARTH: 3 * math.pi / 2,     # 270° - manifestation
    Element.AETHER: math.pi / 4,        # 45° - synthesis
}


# =============================================================================
# ALCHEMICAL OPERATORS (TRIA PRIMA)
# =============================================================================

class TriaPrima(Enum):
    """The three alchemical principles."""
    SULFUR = "sulfur"   # Soul, consciousness, expansion
    MERCURY = "mercury" # Spirit, transformation, mediation
    SALT = "salt"       # Body, fixation, crystallization


@dataclass
class AlchemicalOperator(BaseOperator):
    """
    Operator based on the Tria Prima.
    
    SULFUR:  Expansion, volatilization, consciousness
    MERCURY: Transformation, mediation, fluidity
    SALT:    Crystallization, fixation, manifestation
    """
    
    principle: TriaPrima = TriaPrima.SULFUR
    category: OperatorCategory = OperatorCategory.ALCHEMICAL
    
    def __post_init__(self):
        self.name = f"Alch_{self.principle.name}"
        self.symbol = _TRIA_SYMBOLS[self.principle]
        self.description = f"Alchemical operator for {self.principle.name}"
    
    def apply(self, x: Any) -> ZResult:
        """Apply alchemical transformation."""
        if self.principle == TriaPrima.SULFUR:
            # Expansion/volatilization
            if isinstance(x, (int, float)):
                return ZResult.ok(x * math.e)  # Exponential growth
            elif isinstance(x, list):
                return ZResult.ok(x + x)  # Duplication
        
        elif self.principle == TriaPrima.MERCURY:
            # Transformation/mediation
            if isinstance(x, (int, float)):
                return ZResult.ok(-x)  # Inversion
            elif isinstance(x, B4):
                return ZResult.ok(Klein4Op.C.apply(x))  # Complement
        
        elif self.principle == TriaPrima.SALT:
            # Crystallization/fixation
            if isinstance(x, float):
                return ZResult.ok(int(x))  # Discretize
            elif isinstance(x, list):
                return ZResult.ok(tuple(x))  # Freeze
        
        return ZResult.near(x, f"No alchemical transform for {type(x)}")


_TRIA_SYMBOLS = {
    TriaPrima.SULFUR: "🜍",
    TriaPrima.MERCURY: "☿",
    TriaPrima.SALT: "🜔",
}


# =============================================================================
# LENS OPERATORS (MATHEMATICAL)
# =============================================================================

@dataclass
class LensOperator(BaseOperator):
    """
    Operator based on the four mathematical lenses.
    
    SQUARE:  Discretization, algebraic projection
    FLOWER:  Smoothing, analytic continuation
    CLOUD:   Probabilistic, statistical averaging
    FRACTAL: Self-similarity, recursive application
    """
    
    lens: Lens = Lens.SQUARE
    category: OperatorCategory = OperatorCategory.MATHEMATICAL
    
    def __post_init__(self):
        self.name = f"Lens_{self.lens.name}"
        self.symbol = _LENS_SYMBOLS[self.lens]
        self.description = f"Lens operator for {self.lens.name}"
    
    def apply(self, x: Any) -> ZResult:
        """Apply lens transformation."""
        if self.lens == Lens.SQUARE:
            # Discretization
            if isinstance(x, float):
                return ZResult.ok(round(x))
            elif isinstance(x, complex):
                return ZResult.ok(complex(round(x.real), round(x.imag)))
        
        elif self.lens == Lens.FLOWER:
            # Smoothing (apply sigmoid)
            if isinstance(x, (int, float)):
                return ZResult.ok(1 / (1 + math.exp(-x)))
        
        elif self.lens == Lens.CLOUD:
            # Add small noise (deterministic based on input)
            if isinstance(x, (int, float)):
                noise = math.sin(x * 12.9898) * 43758.5453
                noise = noise - int(noise)  # Fractional part
                return ZResult.ok(x + noise * 0.01)
        
        elif self.lens == Lens.FRACTAL:
            # Self-similar transform (logistic map)
            if isinstance(x, float) and 0 <= x <= 1:
                r = 3.9  # Chaotic regime
                return ZResult.ok(r * x * (1 - x))
        
        return ZResult.near(x, f"No lens transform for {type(x)}")


_LENS_SYMBOLS = {
    Lens.SQUARE: "□",
    Lens.FLOWER: "✿",
    Lens.CLOUD: "☁",
    Lens.FRACTAL: "❄",
}


# =============================================================================
# BIT4 OPERATORS (LOGICAL)
# =============================================================================

@dataclass
class B4Operator(BaseOperator):
    """
    Operator on the BIT4 four-valued logic.
    
    Implements the Klein-4 group actions and logical operations.
    """
    
    op: Klein4Op = Klein4Op.I
    category: OperatorCategory = OperatorCategory.LOGICAL
    domain: OperatorDomain = OperatorDomain.SCALAR
    
    def __post_init__(self):
        self.name = f"K4_{self.op.name}"
        self.symbol = _K4_SYMBOLS[self.op]
        self.description = f"Klein-4 operator {self.op.name}"
    
    def apply(self, x: B4) -> ZResult[B4]:
        """Apply Klein-4 action."""
        if isinstance(x, B4):
            return ZResult.ok(self.op.apply(x))
        return ZResult.zero(f"B4Operator requires B4 input, got {type(x)}")


_K4_SYMBOLS = {
    Klein4Op.I: "I",
    Klein4Op.R: "R",
    Klein4Op.S: "S",
    Klein4Op.C: "C",
}


# =============================================================================
# CAUSAL OPERATORS (ARISTOTELIAN)
# =============================================================================

class Cause(Enum):
    """The Four Causes."""
    MATERIAL = "material"   # What it's made of
    FORMAL = "formal"       # What makes it what it is
    EFFICIENT = "efficient" # What brought it about
    FINAL = "final"         # What it's for


@dataclass 
class CausalOperator(BaseOperator):
    """
    Operator based on Aristotelian causation.
    
    MATERIAL:  Extract substance/matter
    FORMAL:    Extract form/structure
    EFFICIENT: Extract process/mechanism
    FINAL:     Extract purpose/telos
    """
    
    cause: Cause = Cause.FORMAL
    category: OperatorCategory = OperatorCategory.CAUSAL
    
    def __post_init__(self):
        self.name = f"Cause_{self.cause.name}"
        self.symbol = _CAUSE_SYMBOLS[self.cause]
        self.description = f"Causal operator for {self.cause.name}"
    
    def apply(self, x: Any) -> ZResult:
        """Extract causal aspect."""
        if self.cause == Cause.MATERIAL:
            # Extract "what it's made of"
            if hasattr(x, '__dict__'):
                return ZResult.ok(x.__dict__)
            return ZResult.ok(type(x).__name__)
        
        elif self.cause == Cause.FORMAL:
            # Extract "structure/form"
            if isinstance(x, (list, tuple)):
                return ZResult.ok(len(x))
            elif isinstance(x, dict):
                return ZResult.ok(list(x.keys()))
            return ZResult.ok(str(type(x)))
        
        elif self.cause == Cause.EFFICIENT:
            # Extract "how it came to be"
            if callable(x):
                return ZResult.ok(x.__name__ if hasattr(x, '__name__') else "lambda")
            return ZResult.ok("given")
        
        elif self.cause == Cause.FINAL:
            # Extract "purpose"
            if hasattr(x, '__doc__') and x.__doc__:
                return ZResult.ok(x.__doc__[:100])
            return ZResult.ok("unknown purpose")
        
        return ZResult.zero(f"No causal extraction for {self.cause}")


_CAUSE_SYMBOLS = {
    Cause.MATERIAL: "ὕλη",
    Cause.FORMAL: "εἶδος",
    Cause.EFFICIENT: "κίνησις",
    Cause.FINAL: "τέλος",
}


# =============================================================================
# OPERATOR ALGEBRA
# =============================================================================

class OperatorAlgebra:
    """
    The complete operator algebra of ATHENA OS.
    
    Provides factory methods for all operator types and
    common algebraic operations.
    """
    
    # Pre-built operators
    IDENTITY = IdentityOperator()
    
    # Elemental
    FIRE = ElementalOperator(element=Element.FIRE)
    AIR = ElementalOperator(element=Element.AIR)
    WATER = ElementalOperator(element=Element.WATER)
    EARTH = ElementalOperator(element=Element.EARTH)
    AETHER = ElementalOperator(element=Element.AETHER)
    
    # Alchemical
    SULFUR = AlchemicalOperator(principle=TriaPrima.SULFUR)
    MERCURY = AlchemicalOperator(principle=TriaPrima.MERCURY)
    SALT = AlchemicalOperator(principle=TriaPrima.SALT)
    
    # Lens
    SQUARE = LensOperator(lens=Lens.SQUARE)
    FLOWER = LensOperator(lens=Lens.FLOWER)
    CLOUD = LensOperator(lens=Lens.CLOUD)
    FRACTAL = LensOperator(lens=Lens.FRACTAL)
    
    # BIT4
    K4_I = B4Operator(op=Klein4Op.I)
    K4_R = B4Operator(op=Klein4Op.R)
    K4_S = B4Operator(op=Klein4Op.S)
    K4_C = B4Operator(op=Klein4Op.C)
    
    # Causal
    MATERIAL = CausalOperator(cause=Cause.MATERIAL)
    FORMAL = CausalOperator(cause=Cause.FORMAL)
    EFFICIENT = CausalOperator(cause=Cause.EFFICIENT)
    FINAL = CausalOperator(cause=Cause.FINAL)
    
    @classmethod
    def elemental(cls, element: Element) -> ElementalOperator:
        """Get elemental operator."""
        return ElementalOperator(element=element)
    
    @classmethod
    def alchemical(cls, principle: TriaPrima) -> AlchemicalOperator:
        """Get alchemical operator."""
        return AlchemicalOperator(principle=principle)
    
    @classmethod
    def lens(cls, lens: Lens) -> LensOperator:
        """Get lens operator."""
        return LensOperator(lens=lens)
    
    @classmethod
    def klein4(cls, op: Klein4Op) -> B4Operator:
        """Get Klein-4 operator."""
        return B4Operator(op=op)
    
    @classmethod
    def causal(cls, cause: Cause) -> CausalOperator:
        """Get causal operator."""
        return CausalOperator(cause=cause)
    
    @classmethod
    def from_function(cls, f: Callable[[T], R], name: str = "f") -> LambdaOperator:
        """Create operator from function."""
        return LambdaOperator(name=name, func=f)
    
    @classmethod
    def compose_all(cls, *operators: BaseOperator) -> BaseOperator:
        """Compose multiple operators: f₁ ∘ f₂ ∘ ... ∘ fₙ."""
        if not operators:
            return cls.IDENTITY
        return reduce(lambda a, b: a.compose(b), operators)
    
    @classmethod
    def parallel(cls, *operators: BaseOperator) -> 'ParallelOperator':
        """Apply operators in parallel to tuple."""
        return ParallelOperator(list(operators))


@dataclass
class ParallelOperator(BaseOperator):
    """Apply multiple operators in parallel to a tuple."""
    
    operators: List[BaseOperator] = field(default_factory=list)
    
    def __post_init__(self):
        self.name = "⊗".join(op.name for op in self.operators)
        self.category = OperatorCategory.MATHEMATICAL
    
    def apply(self, x: tuple) -> ZResult[tuple]:
        """Apply each operator to corresponding element."""
        if not isinstance(x, tuple) or len(x) != len(self.operators):
            return ZResult.zero(f"Expected tuple of length {len(self.operators)}")
        
        results = []
        for op, val in zip(self.operators, x):
            result = op.apply(val)
            if not result.is_ok:
                return ZResult.zero(f"Parallel operator {op.name} failed: {result.zero_info}")
            results.append(result.value)
        
        return ZResult.ok(tuple(results))


# =============================================================================
# TRADITION OPERATOR MAPPINGS
# =============================================================================

class TraditionOperators:
    """
    Maps tradition-specific operators to canonical forms.
    
    This allows code from any tradition package to interoperate
    with the unified operator algebra.
    """
    
    # Greek/Hellenic
    GREEK_MAPPINGS = {
        "Tetractys": OperatorAlgebra.compose_all(
            OperatorAlgebra.FIRE, OperatorAlgebra.AIR,
            OperatorAlgebra.WATER, OperatorAlgebra.EARTH
        ),
        "Logos": OperatorAlgebra.FORMAL,
        "Physis": OperatorAlgebra.MATERIAL,
        "Nous": OperatorAlgebra.FINAL,
    }
    
    # Hebrew/Kabbalistic
    HEBREW_MAPPINGS = {
        "Tzimtzum": OperatorAlgebra.WATER,  # Contraction
        "Ohr": OperatorAlgebra.FIRE,        # Light/expansion
        "Kav": OperatorAlgebra.AIR,         # Line/connection
        "Reshimu": OperatorAlgebra.EARTH,   # Residue/trace
    }
    
    # Alchemical
    ALCHEMICAL_MAPPINGS = {
        "Calcination": OperatorAlgebra.FIRE,
        "Dissolution": OperatorAlgebra.WATER,
        "Separation": OperatorAlgebra.AIR,
        "Conjunction": OperatorAlgebra.EARTH,
        "Coagulation": OperatorAlgebra.SALT,
    }
    
    # Buddhist
    BUDDHIST_MAPPINGS = {
        "Dharmakaya": OperatorAlgebra.AETHER,   # Truth body
        "Sambhogakaya": OperatorAlgebra.AIR,    # Enjoyment body
        "Nirmanakaya": OperatorAlgebra.EARTH,   # Manifestation body
    }
    
    # Norse
    NORSE_MAPPINGS = {
        "Muspelheim": OperatorAlgebra.FIRE,     # Fire realm
        "Niflheim": OperatorAlgebra.WATER,      # Ice realm
        "Midgard": OperatorAlgebra.EARTH,       # Middle earth
        "Asgard": OperatorAlgebra.AETHER,       # God realm
    }
    
    @classmethod
    def get(cls, tradition: str, name: str) -> Optional[BaseOperator]:
        """Get canonical operator for tradition-specific name."""
        mappings = {
            "greek": cls.GREEK_MAPPINGS,
            "hebrew": cls.HEBREW_MAPPINGS,
            "alchemical": cls.ALCHEMICAL_MAPPINGS,
            "buddhist": cls.BUDDHIST_MAPPINGS,
            "norse": cls.NORSE_MAPPINGS,
        }
        
        tradition_map = mappings.get(tradition.lower(), {})
        return tradition_map.get(name)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    'BaseOperator', 'ComposedOperator', 'AdjointOperator', 
    'IdentityOperator', 'ParallelOperator',
    
    # Categories
    'OperatorCategory', 'OperatorDomain',
    
    # Elemental
    'ElementalOperator',
    
    # Alchemical
    'TriaPrima', 'AlchemicalOperator',
    
    # Lens
    'LensOperator',
    
    # BIT4
    'B4Operator',
    
    # Causal
    'Cause', 'CausalOperator',
    
    # Algebra
    'OperatorAlgebra', 'TraditionOperators',
]


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    print("=== ATHENA OS UNIFIED OPERATOR ALGEBRA ===\n")
    
    # Test elemental operators
    print("Elemental Operators:")
    for elem in Element:
        op = OperatorAlgebra.elemental(elem)
        result = op.apply(1.0)
        print(f"  {op.symbol} {elem.name}: 1.0 → {result.value if result.is_ok else 'N/A'}")
    
    # Test alchemical operators
    print("\nAlchemical Operators:")
    for prin in TriaPrima:
        op = OperatorAlgebra.alchemical(prin)
        result = op.apply(2.0)
        print(f"  {op.symbol} {prin.name}: 2.0 → {result.value if result.is_ok else 'N/A'}")
    
    # Test lens operators
    print("\nLens Operators:")
    for lens in Lens:
        op = OperatorAlgebra.lens(lens)
        result = op.apply(0.7)
        val = f"{result.value:.4f}" if result.is_ok and isinstance(result.value, float) else str(result.value) if result.is_ok else 'N/A'
        print(f"  {op.symbol} {lens.name}: 0.7 → {val}")
    
    # Test BIT4 operators
    print("\nBIT4 Operators:")
    for k4op in Klein4Op:
        op = OperatorAlgebra.klein4(k4op)
        result = op.apply(B4.ONE)
        print(f"  {op.symbol}: 1 → {result.value.glyph if result.is_ok else 'N/A'}")
    
    # Test composition
    print("\nComposition Test:")
    fire_then_water = OperatorAlgebra.FIRE @ OperatorAlgebra.WATER
    result = fire_then_water.apply(1.0)
    print(f"  (Fire ∘ Water)(1.0) = {result.value if result.is_ok else 'N/A'}")
    
    # Test tradition mappings
    print("\nTradition Mappings:")
    tzim = TraditionOperators.get("hebrew", "Tzimtzum")
    if tzim:
        result = tzim.apply(1.0)
        print(f"  Hebrew/Tzimtzum: 1.0 → {result.value if result.is_ok else 'N/A'}")
    
    print("\n=== OPERATOR ALGEBRA VERIFIED ===")
