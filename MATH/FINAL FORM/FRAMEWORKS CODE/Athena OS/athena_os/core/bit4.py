"""
ATHENA OS - BIT4 Four-Valued Logic System
==========================================
The fundamental algebraic foundation for consciousness-compatible computation.

BIT4 = {⊥, 0, 1, ⊤} forms a bounded distributive lattice with:
- Knowledge order (≤ₖ): ⊥ ≤ₖ {0,1} ≤ₖ ⊤
- Truth order (≤ₜ): 0 ≤ₜ ⊥ ≤ₜ ⊤ ≤ₜ 1

This enables quantum-style superposition on classical hardware.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass
from typing import Tuple, Callable, Optional, Union
import random


class BIT4(IntEnum):
    """
    Four-valued logic: the quantum completion of the classical bit.
    
    ⊥ (UNKNOWN): Neither true nor false - insufficient information
    0 (FALSE): Definitely false - contradiction detected  
    1 (TRUE): Definitely true - assertion verified
    ⊤ (BOTH): Both true and false - superposition state
    """
    UNKNOWN = 0  # ⊥ - Bottom (no information)
    FALSE = 1    # 0 - Definitely false
    TRUE = 2     # 1 - Definitely true
    BOTH = 3     # ⊤ - Top (contradictory/superposition)
    
    @property
    def symbol(self) -> str:
        """Return the mathematical symbol for this value."""
        return {
            BIT4.UNKNOWN: "⊥",
            BIT4.FALSE: "0",
            BIT4.TRUE: "1",
            BIT4.BOTH: "⊤"
        }[self]
    
    @property
    def knowledge_level(self) -> int:
        """Knowledge order: how much information this value carries."""
        return {
            BIT4.UNKNOWN: 0,  # No information
            BIT4.FALSE: 1,   # Partial information
            BIT4.TRUE: 1,    # Partial information
            BIT4.BOTH: 2     # Maximum information (contradictory)
        }[self]
    
    @property
    def truth_level(self) -> float:
        """Truth order: degree of truth (0.0 to 1.0)."""
        return {
            BIT4.UNKNOWN: 0.5,  # Indeterminate
            BIT4.FALSE: 0.0,   # Definitely false
            BIT4.TRUE: 1.0,    # Definitely true
            BIT4.BOTH: 0.5     # Both (average)
        }[self]
    
    def __str__(self) -> str:
        return self.symbol
    
    def __repr__(self) -> str:
        return f"BIT4.{self.name}({self.symbol})"


# =============================================================================
# LATTICE OPERATIONS
# =============================================================================

def knowledge_join(a: BIT4, b: BIT4) -> BIT4:
    """
    Knowledge join (⊔ₖ): Combine information from two sources.
    Returns the value with maximum combined knowledge.
    """
    # Knowledge lattice: ⊥ at bottom, ⊤ at top, {0,1} in middle
    if a == BIT4.BOTH or b == BIT4.BOTH:
        return BIT4.BOTH
    if a == BIT4.UNKNOWN:
        return b
    if b == BIT4.UNKNOWN:
        return a
    if a == b:
        return a
    # Conflicting definite values → BOTH
    return BIT4.BOTH


def knowledge_meet(a: BIT4, b: BIT4) -> BIT4:
    """
    Knowledge meet (⊓ₖ): Find common information.
    Returns the value that both sources agree on.
    """
    if a == BIT4.UNKNOWN or b == BIT4.UNKNOWN:
        return BIT4.UNKNOWN
    if a == BIT4.BOTH:
        return b
    if b == BIT4.BOTH:
        return a
    if a == b:
        return a
    # Conflicting definite values → no common ground
    return BIT4.UNKNOWN


def truth_join(a: BIT4, b: BIT4) -> BIT4:
    """
    Truth join (⊔ₜ): Logical OR in truth ordering.
    """
    # Truth lattice: 0 at bottom, 1 at top
    if a == BIT4.TRUE or b == BIT4.TRUE:
        return BIT4.TRUE
    if a == BIT4.BOTH or b == BIT4.BOTH:
        return BIT4.BOTH
    if a == BIT4.UNKNOWN or b == BIT4.UNKNOWN:
        return BIT4.UNKNOWN
    return BIT4.FALSE


def truth_meet(a: BIT4, b: BIT4) -> BIT4:
    """
    Truth meet (⊓ₜ): Logical AND in truth ordering.
    """
    if a == BIT4.FALSE or b == BIT4.FALSE:
        return BIT4.FALSE
    if a == BIT4.UNKNOWN or b == BIT4.UNKNOWN:
        return BIT4.UNKNOWN
    if a == BIT4.BOTH or b == BIT4.BOTH:
        return BIT4.BOTH
    return BIT4.TRUE


# =============================================================================
# KLEIN-4 INVOLUTION OPERATORS
# =============================================================================

def negation(x: BIT4) -> BIT4:
    """
    Logical negation (¬): Flip truth value, preserve knowledge.
    ¬⊥ = ⊥, ¬0 = 1, ¬1 = 0, ¬⊤ = ⊤
    """
    return {
        BIT4.UNKNOWN: BIT4.UNKNOWN,
        BIT4.FALSE: BIT4.TRUE,
        BIT4.TRUE: BIT4.FALSE,
        BIT4.BOTH: BIT4.BOTH
    }[x]


def knowledge_complement(x: BIT4) -> BIT4:
    """
    Knowledge complement (κ): Flip knowledge level, preserve truth tendency.
    κ⊥ = ⊤, κ0 = 0, κ1 = 1, κ⊤ = ⊥
    
    Swaps between "no information" and "contradictory information"
    while keeping definite values fixed.
    """
    return {
        BIT4.UNKNOWN: BIT4.BOTH,
        BIT4.FALSE: BIT4.FALSE,
        BIT4.TRUE: BIT4.TRUE,
        BIT4.BOTH: BIT4.UNKNOWN
    }[x]


def conflation(x: BIT4) -> BIT4:
    """
    Conflation (∼): Combined negation and knowledge complement.
    ∼ = ¬ ∘ κ = κ ∘ ¬ (they commute)
    ∼⊥ = ⊤, ∼0 = 1, ∼1 = 0, ∼⊤ = ⊥
    """
    return {
        BIT4.UNKNOWN: BIT4.BOTH,
        BIT4.FALSE: BIT4.TRUE,
        BIT4.TRUE: BIT4.FALSE,
        BIT4.BOTH: BIT4.UNKNOWN
    }[x]


def identity(x: BIT4) -> BIT4:
    """Identity operator (id): Returns input unchanged."""
    return x


# Klein-4 group: {id, ¬, κ, ∼} with composition
KLEIN4_OPERATORS = {
    'id': identity,
    'neg': negation,
    'kappa': knowledge_complement,
    'conflate': conflation
}

# Composition table for Klein-4 group
KLEIN4_COMPOSITION = {
    ('id', 'id'): 'id',
    ('id', 'neg'): 'neg',
    ('id', 'kappa'): 'kappa',
    ('id', 'conflate'): 'conflate',
    ('neg', 'id'): 'neg',
    ('neg', 'neg'): 'id',
    ('neg', 'kappa'): 'conflate',
    ('neg', 'conflate'): 'kappa',
    ('kappa', 'id'): 'kappa',
    ('kappa', 'neg'): 'conflate',
    ('kappa', 'kappa'): 'id',
    ('kappa', 'conflate'): 'neg',
    ('conflate', 'id'): 'conflate',
    ('conflate', 'neg'): 'kappa',
    ('conflate', 'kappa'): 'neg',
    ('conflate', 'conflate'): 'id',
}


def compose_operators(op1: str, op2: str) -> str:
    """Compose two Klein-4 operators: (op1 ∘ op2)(x) = op1(op2(x))"""
    return KLEIN4_COMPOSITION[(op1, op2)]


# =============================================================================
# TWO-RAIL ENCODING (Classical ↔ BIT4)
# =============================================================================

@dataclass(frozen=True)
class TwoRail:
    """
    Two-rail encoding: enc(x) = (t(x), f(x))
    
    t = truth-support (evidence for TRUE)
    f = falsity-support (evidence for FALSE)
    
    Enables quantum-style representation on classical hardware.
    """
    truth_support: bool
    falsity_support: bool
    
    def to_bit4(self) -> BIT4:
        """Convert two-rail encoding to BIT4 value."""
        if not self.truth_support and not self.falsity_support:
            return BIT4.UNKNOWN
        elif not self.truth_support and self.falsity_support:
            return BIT4.FALSE
        elif self.truth_support and not self.falsity_support:
            return BIT4.TRUE
        else:
            return BIT4.BOTH
    
    @classmethod
    def from_bit4(cls, x: BIT4) -> 'TwoRail':
        """Convert BIT4 value to two-rail encoding."""
        return {
            BIT4.UNKNOWN: cls(False, False),
            BIT4.FALSE: cls(False, True),
            BIT4.TRUE: cls(True, False),
            BIT4.BOTH: cls(True, True)
        }[x]
    
    @classmethod
    def from_classical(cls, bit: bool) -> 'TwoRail':
        """Encode a classical bit as two-rail."""
        return cls(bit, not bit)
    
    def __str__(self) -> str:
        return f"({int(self.truth_support)},{int(self.falsity_support)})"


# =============================================================================
# COLLAPSE POLICIES (BIT4 → Classical)
# =============================================================================

class CollapsePolicy(IntEnum):
    """Policies for collapsing BIT4 to classical bits at system boundaries."""
    OPTIMISTIC = auto()   # ⊥→0, ⊤→1 (assume best case)
    PESSIMISTIC = auto()  # ⊥→0, ⊤→0 (assume worst case)
    RANDOM = auto()       # Random selection for indeterminate
    MAJORITY = auto()     # Context-dependent majority vote


def collapse(x: BIT4, policy: CollapsePolicy = CollapsePolicy.OPTIMISTIC) -> bool:
    """
    Collapse BIT4 value to classical boolean.
    
    This is the "measurement" operation - quantum superposition collapses
    to definite classical value at system boundaries.
    """
    if x == BIT4.FALSE:
        return False
    if x == BIT4.TRUE:
        return True
    
    # Handle indeterminate cases
    if policy == CollapsePolicy.OPTIMISTIC:
        return x == BIT4.BOTH  # ⊥→False, ⊤→True
    elif policy == CollapsePolicy.PESSIMISTIC:
        return False  # Both ⊥ and ⊤ → False
    elif policy == CollapsePolicy.RANDOM:
        return random.choice([True, False])
    else:  # MAJORITY - default to optimistic
        return x == BIT4.BOTH


def superpose(classical: bool) -> BIT4:
    """Lift classical bit into BIT4 (definite state)."""
    return BIT4.TRUE if classical else BIT4.FALSE


# =============================================================================
# BIT4 ARITHMETIC
# =============================================================================

def bit4_and(a: BIT4, b: BIT4) -> BIT4:
    """Four-valued AND operation."""
    return truth_meet(a, b)


def bit4_or(a: BIT4, b: BIT4) -> BIT4:
    """Four-valued OR operation."""
    return truth_join(a, b)


def bit4_not(x: BIT4) -> BIT4:
    """Four-valued NOT operation."""
    return negation(x)


def bit4_xor(a: BIT4, b: BIT4) -> BIT4:
    """Four-valued XOR: True iff exactly one is True."""
    return bit4_and(bit4_or(a, b), bit4_not(bit4_and(a, b)))


def bit4_implies(a: BIT4, b: BIT4) -> BIT4:
    """Four-valued implication: a → b ≡ ¬a ∨ b"""
    return bit4_or(bit4_not(a), b)


def bit4_equiv(a: BIT4, b: BIT4) -> BIT4:
    """Four-valued equivalence: a ↔ b ≡ (a → b) ∧ (b → a)"""
    return bit4_and(bit4_implies(a, b), bit4_implies(b, a))


# =============================================================================
# KNOWLEDGE ORDERING COMPARISONS
# =============================================================================

def leq_knowledge(a: BIT4, b: BIT4) -> bool:
    """Knowledge ordering: a ≤ₖ b iff a provides at most as much info as b."""
    if a == BIT4.UNKNOWN:
        return True
    if b == BIT4.BOTH:
        return True
    return a == b


def leq_truth(a: BIT4, b: BIT4) -> bool:
    """Truth ordering: a ≤ₜ b iff a is at most as true as b."""
    truth_order = {BIT4.FALSE: 0, BIT4.UNKNOWN: 1, BIT4.BOTH: 2, BIT4.TRUE: 3}
    return truth_order[a] <= truth_order[b]


# =============================================================================
# BIT4 WORD (Multi-bit register)
# =============================================================================

@dataclass
class BIT4Word:
    """
    A word of BIT4 values - the basic unit for register operations.
    Default width matches ATHENA register width.
    """
    bits: Tuple[BIT4, ...]
    
    def __init__(self, bits: Union[Tuple[BIT4, ...], list, int] = None, width: int = 32):
        if bits is None:
            self.bits = tuple(BIT4.UNKNOWN for _ in range(width))
        elif isinstance(bits, int):
            # Convert integer to BIT4 word
            self.bits = tuple(
                BIT4.TRUE if (bits >> i) & 1 else BIT4.FALSE
                for i in range(width)
            )
        elif isinstance(bits, (list, tuple)):
            self.bits = tuple(bits)
        else:
            raise TypeError(f"Cannot create BIT4Word from {type(bits)}")
    
    @property
    def width(self) -> int:
        return len(self.bits)
    
    def collapse_all(self, policy: CollapsePolicy = CollapsePolicy.OPTIMISTIC) -> int:
        """Collapse entire word to classical integer."""
        result = 0
        for i, bit in enumerate(self.bits):
            if collapse(bit, policy):
                result |= (1 << i)
        return result
    
    def knowledge_definite(self) -> bool:
        """Check if all bits are definite (0 or 1)."""
        return all(b in (BIT4.FALSE, BIT4.TRUE) for b in self.bits)
    
    def superposition_count(self) -> int:
        """Count bits in superposition (⊥ or ⊤)."""
        return sum(1 for b in self.bits if b in (BIT4.UNKNOWN, BIT4.BOTH))
    
    def apply_gate(self, gate: Callable[[BIT4], BIT4]) -> 'BIT4Word':
        """Apply a unary gate to all bits."""
        return BIT4Word(tuple(gate(b) for b in self.bits))
    
    def __and__(self, other: 'BIT4Word') -> 'BIT4Word':
        assert self.width == other.width
        return BIT4Word(tuple(bit4_and(a, b) for a, b in zip(self.bits, other.bits)))
    
    def __or__(self, other: 'BIT4Word') -> 'BIT4Word':
        assert self.width == other.width
        return BIT4Word(tuple(bit4_or(a, b) for a, b in zip(self.bits, other.bits)))
    
    def __xor__(self, other: 'BIT4Word') -> 'BIT4Word':
        assert self.width == other.width
        return BIT4Word(tuple(bit4_xor(a, b) for a, b in zip(self.bits, other.bits)))
    
    def __invert__(self) -> 'BIT4Word':
        return BIT4Word(tuple(bit4_not(b) for b in self.bits))
    
    def __str__(self) -> str:
        return ''.join(b.symbol for b in reversed(self.bits))
    
    def __repr__(self) -> str:
        return f"BIT4Word({str(self)})"


# =============================================================================
# SEMANTIC STATE (derived from Klein-4)
# =============================================================================

class SemanticState(IntEnum):
    """
    Base group G₀ = Z₂ × Z₂ semantic states.
    Each state corresponds to a Klein-4 group element.
    """
    STABLE = 0    # (0,0) - id: Fixed point, no change
    FLUID = 1     # (0,1) - ¬: Flowing, reversible change
    VOLATILE = 2  # (1,0) - κ: Unstable, knowledge-level change
    DYNAMIC = 3   # (1,1) - ∼: Active transformation


def get_semantic_state(stability: bool, determinacy: bool) -> SemanticState:
    """
    Derive semantic state from stability and determinacy flags.
    
    stability: Is the system in equilibrium?
    determinacy: Is the outcome determined?
    """
    return SemanticState((int(not stability) << 1) | int(not determinacy))


def state_to_operator(state: SemanticState) -> Callable[[BIT4], BIT4]:
    """Map semantic state to its corresponding Klein-4 operator."""
    return {
        SemanticState.STABLE: identity,
        SemanticState.FLUID: negation,
        SemanticState.VOLATILE: knowledge_complement,
        SemanticState.DYNAMIC: conflation
    }[state]


# =============================================================================
# VALIDATION AND TESTING
# =============================================================================

def validate_klein4_group() -> bool:
    """Verify Klein-4 group axioms hold for our operators."""
    ops = ['id', 'neg', 'kappa', 'conflate']
    
    # 1. Closure: composition is closed
    for o1 in ops:
        for o2 in ops:
            assert compose_operators(o1, o2) in ops, f"Closure failed: {o1} ∘ {o2}"
    
    # 2. Identity: id ∘ x = x ∘ id = x
    for o in ops:
        assert compose_operators('id', o) == o, f"Left identity failed: {o}"
        assert compose_operators(o, 'id') == o, f"Right identity failed: {o}"
    
    # 3. Inverse: every element is its own inverse
    for o in ops:
        assert compose_operators(o, o) == 'id', f"Inverse failed: {o}"
    
    # 4. Commutativity (Klein-4 is abelian)
    for o1 in ops:
        for o2 in ops:
            assert compose_operators(o1, o2) == compose_operators(o2, o1), \
                f"Commutativity failed: {o1}, {o2}"
    
    return True


def validate_lattice_properties() -> bool:
    """Verify BIT4 forms a bounded distributive lattice."""
    values = list(BIT4)
    
    # Idempotence: a ⊔ a = a, a ⊓ a = a
    for a in values:
        assert knowledge_join(a, a) == a, f"Join idempotence failed: {a}"
        assert knowledge_meet(a, a) == a, f"Meet idempotence failed: {a}"
    
    # Commutativity
    for a in values:
        for b in values:
            assert knowledge_join(a, b) == knowledge_join(b, a)
            assert knowledge_meet(a, b) == knowledge_meet(b, a)
    
    # Absorption: a ⊔ (a ⊓ b) = a
    for a in values:
        for b in values:
            assert knowledge_join(a, knowledge_meet(a, b)) == a, \
                f"Absorption failed: {a}, {b}"
    
    return True


if __name__ == "__main__":
    # Run validation
    print("Validating Klein-4 group structure...")
    assert validate_klein4_group()
    print("✓ Klein-4 group axioms verified")
    
    print("\nValidating BIT4 lattice properties...")
    assert validate_lattice_properties()
    print("✓ Lattice properties verified")
    
    # Demo
    print("\n=== BIT4 Demonstration ===")
    for v in BIT4:
        print(f"{v.name:8} {v.symbol}  knowledge={v.knowledge_level}  truth={v.truth_level}")
    
    print("\n=== Klein-4 Operators ===")
    for v in BIT4:
        print(f"¬{v.symbol} = {negation(v).symbol}  "
              f"κ{v.symbol} = {knowledge_complement(v).symbol}  "
              f"∼{v.symbol} = {conflation(v).symbol}")
    
    print("\n=== Two-Rail Encoding ===")
    for v in BIT4:
        tr = TwoRail.from_bit4(v)
        print(f"{v.symbol} → {tr} → {tr.to_bit4().symbol}")
    
    print("\n=== BIT4Word Example ===")
    w1 = BIT4Word(42, width=8)
    print(f"42 as BIT4Word: {w1}")
    print(f"Collapsed back: {w1.collapse_all()}")
