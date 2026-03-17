"""
ATHENA OS - HELLENIC: ALGEBRAIC FOUNDATION
==========================================
The 4×4 Holographic Seed

CORE THESIS:
    The Greek philosophical corpus operates on a single minimal
    algebraic structure: the Cartesian product of the cyclic group
    of order 2 with itself.

THE 2-BIT STATE SPACE:
    V = Z₂ × Z₂ = {(0,0), (0,1), (1,0), (1,1)}
    
    Each element represents a compound state from two binary axes:
    - b₁ ∈ {0,1}: First axis (Cold/Hot, Internal/External)
    - b₂ ∈ {0,1}: Second axis (Dry/Wet, Structural/Dynamic)

THE KLEIN-4 GROUP:
    K₄ = {I, R, S, C} ≅ Z₂ × Z₂ under component-wise addition
    
    I = Identity       (0,0)
    R = Row flip       (1,0)
    S = Column flip    (0,1)
    C = Complement     (1,1)

UNIVERSAL TETRAD ENCODING:
    All Greek tetrads map isomorphically onto V:
    - Four Elements: Earth, Water, Fire, Air
    - Four Humors: Black Bile, Phlegm, Yellow Bile, Blood
    - Four Platonic Kinds: Unlimited, Limit, Mixture, Cause
    - Four Causes: Material, Formal, Efficient, Final
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Callable
from enum import Enum, auto
import numpy as np


# =============================================================================
# 2-BIT STATE SPACE
# =============================================================================

class BitPair:
    """
    Element of V = Z₂ × Z₂.
    
    The minimal state space encoding all Greek tetradic systems.
    """
    
    def __init__(self, b1: int, b2: int):
        """Initialize bit pair (b₁, b₂) ∈ {0,1}²."""
        self.b1 = b1 % 2
        self.b2 = b2 % 2
    
    def __repr__(self) -> str:
        return f"({self.b1},{self.b2})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, BitPair):
            return self.b1 == other.b1 and self.b2 == other.b2
        return False
    
    def __hash__(self) -> int:
        return hash((self.b1, self.b2))
    
    def __add__(self, other: 'BitPair') -> 'BitPair':
        """Component-wise XOR addition in Z₂."""
        return BitPair((self.b1 + other.b1) % 2, (self.b2 + other.b2) % 2)
    
    def __neg__(self) -> 'BitPair':
        """In Z₂, every element is its own inverse."""
        return BitPair(self.b1, self.b2)
    
    @property
    def index(self) -> int:
        """Convert to integer index 0-3."""
        return self.b1 * 2 + self.b2
    
    @classmethod
    def from_index(cls, idx: int) -> 'BitPair':
        """Create from integer index."""
        return cls((idx >> 1) & 1, idx & 1)
    
    def flip_b1(self) -> 'BitPair':
        """Flip first bit (row operation)."""
        return BitPair(1 - self.b1, self.b2)
    
    def flip_b2(self) -> 'BitPair':
        """Flip second bit (column operation)."""
        return BitPair(self.b1, 1 - self.b2)
    
    def complement(self) -> 'BitPair':
        """Flip both bits."""
        return BitPair(1 - self.b1, 1 - self.b2)
    
    def hamming_distance(self, other: 'BitPair') -> int:
        """Count differing bits."""
        return (self.b1 != other.b1) + (self.b2 != other.b2)


class StateSpace:
    """
    The complete 2-bit state space V = Z₂ × Z₂.
    
    V = {(0,0), (0,1), (1,0), (1,1)}
    
    This minimal structure encodes ALL major Greek tetradic systems.
    """
    
    # The four states
    S00 = BitPair(0, 0)  # (Cold, Dry)
    S01 = BitPair(0, 1)  # (Cold, Wet)
    S10 = BitPair(1, 0)  # (Hot, Dry)
    S11 = BitPair(1, 1)  # (Hot, Wet)
    
    @classmethod
    def all_states(cls) -> List[BitPair]:
        """Return all four states."""
        return [cls.S00, cls.S01, cls.S10, cls.S11]
    
    @classmethod
    def adjacency_graph(cls) -> Dict[BitPair, List[BitPair]]:
        """
        Return adjacency graph (single-bit-flip neighbors).
        
        Forms a square/cycle topology.
        """
        return {
            cls.S00: [cls.S01, cls.S10],
            cls.S01: [cls.S00, cls.S11],
            cls.S10: [cls.S00, cls.S11],
            cls.S11: [cls.S01, cls.S10]
        }
    
    @classmethod
    def diagonal_pairs(cls) -> List[Tuple[BitPair, BitPair]]:
        """Return complementary pairs (2-bit-flip)."""
        return [(cls.S00, cls.S11), (cls.S01, cls.S10)]


# =============================================================================
# KLEIN-4 GROUP
# =============================================================================

class Klein4Op(Enum):
    """
    Elements of the Klein-4 group K₄.
    
    K₄ = {I, R, S, C} acting on V = Z₂ × Z₂
    
    - I: Identity
    - R: Row flip (flip b₁)
    - S: Column flip (flip b₂)
    - C: Complement (flip both)
    """
    
    I = (0, 0)  # Identity
    R = (1, 0)  # Row flip
    S = (0, 1)  # Column flip
    C = (1, 1)  # Complement


class Klein4Group:
    """
    The Klein-4 Group K₄ ≅ Z₂ × Z₂.
    
    The natural symmetry group acting on the 2-bit state space.
    
    Multiplication Table:
        | I  R  S  C
      --+------------
      I | I  R  S  C
      R | R  I  C  S
      S | S  C  I  R
      C | C  S  R  I
    
    Properties:
    - Abelian (commutative)
    - Every element is self-inverse (g² = I)
    - Order 4
    """
    
    def __init__(self):
        self.elements = [Klein4Op.I, Klein4Op.R, Klein4Op.S, Klein4Op.C]
        
        # Precompute multiplication table
        self._mult_table = self._compute_multiplication_table()
    
    def _compute_multiplication_table(self) -> Dict[Tuple[Klein4Op, Klein4Op], Klein4Op]:
        """Compute K₄ multiplication table."""
        table = {}
        for g1 in self.elements:
            for g2 in self.elements:
                # Component-wise XOR
                result = ((g1.value[0] + g2.value[0]) % 2,
                         (g1.value[1] + g2.value[1]) % 2)
                for g in self.elements:
                    if g.value == result:
                        table[(g1, g2)] = g
                        break
        return table
    
    def multiply(self, g1: Klein4Op, g2: Klein4Op) -> Klein4Op:
        """Multiply two group elements."""
        return self._mult_table[(g1, g2)]
    
    def apply(self, g: Klein4Op, state: BitPair) -> BitPair:
        """Apply group element to state."""
        return BitPair(
            (state.b1 + g.value[0]) % 2,
            (state.b2 + g.value[1]) % 2
        )
    
    def inverse(self, g: Klein4Op) -> Klein4Op:
        """Every element is self-inverse in K₄."""
        return g
    
    def orbit(self, state: BitPair) -> Set[BitPair]:
        """Compute orbit of state under K₄ action."""
        return {self.apply(g, state) for g in self.elements}
    
    def stabilizer(self, state: BitPair) -> List[Klein4Op]:
        """Elements that fix the state (always just identity for free action)."""
        return [g for g in self.elements if self.apply(g, state) == state]
    
    def cayley_table(self) -> np.ndarray:
        """Return Cayley table as matrix."""
        table = np.zeros((4, 4), dtype=int)
        for i, g1 in enumerate(self.elements):
            for j, g2 in enumerate(self.elements):
                result = self.multiply(g1, g2)
                table[i, j] = self.elements.index(result)
        return table
    
    def is_abelian(self) -> bool:
        """Verify group is abelian."""
        for g1 in self.elements:
            for g2 in self.elements:
                if self.multiply(g1, g2) != self.multiply(g2, g1):
                    return False
        return True


# =============================================================================
# 4×4 DIAGONAL LATIN KERNEL
# =============================================================================

class LatinKernel:
    """
    The 4×4 Diagonal Latin Square.
    
    Encodes the universal algebraic seed of Greek philosophy.
    
    Structure:
        | 0 1 2 3
      --+---------
      0 | 0 1 2 3
      1 | 1 0 3 2
      2 | 2 3 0 1
      3 | 3 2 1 0
    
    Properties:
    - Each row/column contains all symbols {0,1,2,3} exactly once
    - Main diagonal: all zeros (Identity)
    - Anti-diagonal: all threes (Complement)
    - Holographic: most 2×2 sub-blocks contain all four symbols
    """
    
    def __init__(self):
        self.matrix = self._generate_matrix()
    
    def _generate_matrix(self) -> np.ndarray:
        """Generate the canonical Latin kernel."""
        M = np.zeros((4, 4), dtype=int)
        for i in range(4):
            for j in range(4):
                M[i, j] = i ^ j  # XOR gives Klein-4 structure
        return M
    
    def get(self, i: int, j: int) -> int:
        """Get element at position (i, j)."""
        return int(self.matrix[i % 4, j % 4])
    
    def row(self, i: int) -> np.ndarray:
        """Get row i."""
        return self.matrix[i % 4].copy()
    
    def column(self, j: int) -> np.ndarray:
        """Get column j."""
        return self.matrix[:, j % 4].copy()
    
    def is_latin(self) -> bool:
        """Verify Latin square property."""
        for i in range(4):
            if len(set(self.row(i))) != 4:
                return False
            if len(set(self.column(i))) != 4:
                return False
        return True
    
    def check_holographic(self) -> float:
        """
        Check holographic property.
        
        Returns fraction of 2×2 sub-blocks containing all four symbols.
        """
        count = 0
        total = 0
        
        for i in range(3):
            for j in range(3):
                block = {self.matrix[i, j], self.matrix[i, j+1],
                        self.matrix[i+1, j], self.matrix[i+1, j+1]}
                if len(block) == 4:
                    count += 1
                total += 1
        
        return count / total if total > 0 else 0.0
    
    def apply_operation(self, op: Klein4Op) -> np.ndarray:
        """Apply Klein-4 operation to matrix."""
        result = self.matrix.copy()
        
        if op == Klein4Op.R:
            result = result[::-1, :]  # Flip rows
        elif op == Klein4Op.S:
            result = result[:, ::-1]  # Flip columns
        elif op == Klein4Op.C:
            result = result[::-1, ::-1]  # Flip both
        
        return result


# =============================================================================
# UNIVERSAL TETRAD ENCODING
# =============================================================================

class Element(Enum):
    """The Four Elements."""
    EARTH = (0, 0)  # Cold, Dry
    WATER = (0, 1)  # Cold, Wet
    FIRE = (1, 0)   # Hot, Dry
    AIR = (1, 1)    # Hot, Wet


class Humor(Enum):
    """The Four Humors (Hippocratic)."""
    BLACK_BILE = (0, 0)   # Cold, Dry - Melancholic
    PHLEGM = (0, 1)       # Cold, Wet - Phlegmatic
    YELLOW_BILE = (1, 0)  # Hot, Dry - Choleric
    BLOOD = (1, 1)        # Hot, Wet - Sanguine


class PlatonicKind(Enum):
    """The Four Platonic Kinds (Philebus)."""
    UNLIMITED = (0, 0)  # Raw continuum
    LIMIT = (0, 1)      # Discrete boundary
    MIXTURE = (1, 0)    # Instantiated object
    CAUSE = (1, 1)      # Active agent


class AristotelianCause(Enum):
    """The Four Causes (Aristotle)."""
    MATERIAL = (0, 0)   # What it's made of
    FORMAL = (0, 1)     # What it is (essence)
    EFFICIENT = (1, 0)  # What made it
    FINAL = (1, 1)      # What it's for


class TetradEncoder:
    """
    Universal encoder mapping Greek tetrads to V = Z₂ × Z₂.
    
    Axis Definitions:
    - Elements/Humors: b₁ = Hot(1)/Cold(0), b₂ = Wet(1)/Dry(0)
    - Platonic Kinds: b₁ = Composite(1)/Simple(0), b₂ = Active(1)/Passive(0)
    - Causes: b₁ = External(1)/Internal(0), b₂ = Telic(1)/Structural(0)
    """
    
    @staticmethod
    def element_to_bits(element: Element) -> BitPair:
        """Encode element as bit pair."""
        return BitPair(*element.value)
    
    @staticmethod
    def humor_to_bits(humor: Humor) -> BitPair:
        """Encode humor as bit pair."""
        return BitPair(*humor.value)
    
    @staticmethod
    def platonic_to_bits(kind: PlatonicKind) -> BitPair:
        """Encode Platonic kind as bit pair."""
        return BitPair(*kind.value)
    
    @staticmethod
    def cause_to_bits(cause: AristotelianCause) -> BitPair:
        """Encode Aristotelian cause as bit pair."""
        return BitPair(*cause.value)
    
    @staticmethod
    def bits_to_element(bits: BitPair) -> Element:
        """Decode bit pair to element."""
        for e in Element:
            if e.value == (bits.b1, bits.b2):
                return e
        raise ValueError(f"Invalid bits: {bits}")
    
    @staticmethod
    def bits_to_humor(bits: BitPair) -> Humor:
        """Decode bit pair to humor."""
        for h in Humor:
            if h.value == (bits.b1, bits.b2):
                return h
        raise ValueError(f"Invalid bits: {bits}")
    
    @classmethod
    def element_transformation(cls, element: Element, 
                               op: Klein4Op) -> Element:
        """Apply Klein-4 operation to element."""
        bits = cls.element_to_bits(element)
        k4 = Klein4Group()
        new_bits = k4.apply(op, bits)
        return cls.bits_to_element(new_bits)
    
    @classmethod
    def element_to_humor(cls, element: Element) -> Humor:
        """
        Map element to corresponding humor.
        
        Same encoding, different interpretation.
        """
        bits = cls.element_to_bits(element)
        return cls.bits_to_humor(bits)
    
    @classmethod
    def verify_isomorphism(cls) -> bool:
        """Verify all tetrads are isomorphic to V."""
        # Check each tetrad has exactly 4 elements mapping to distinct bit pairs
        for tetrad in [Element, Humor, PlatonicKind, AristotelianCause]:
            values = [member.value for member in tetrad]
            if len(values) != 4:
                return False
            if len(set(values)) != 4:
                return False
            # Check all combinations (0,0), (0,1), (1,0), (1,1) present
            expected = {(0, 0), (0, 1), (1, 0), (1, 1)}
            if set(values) != expected:
                return False
        return True


# =============================================================================
# VALIDATION
# =============================================================================

def validate_algebra() -> bool:
    """Validate algebraic foundation module."""
    
    # Test BitPair
    bp00 = BitPair(0, 0)
    bp01 = BitPair(0, 1)
    bp10 = BitPair(1, 0)
    bp11 = BitPair(1, 1)
    
    assert bp00 + bp01 == bp01
    assert bp01 + bp10 == bp11
    assert bp11 + bp11 == bp00  # Self-inverse
    
    assert bp00.index == 0
    assert bp11.index == 3
    
    assert bp00.hamming_distance(bp11) == 2
    assert bp00.hamming_distance(bp01) == 1
    
    # Test StateSpace
    states = StateSpace.all_states()
    assert len(states) == 4
    
    adj = StateSpace.adjacency_graph()
    assert len(adj[StateSpace.S00]) == 2
    
    # Test Klein4Group
    k4 = Klein4Group()
    
    assert k4.is_abelian()
    
    # Every element is self-inverse
    for g in k4.elements:
        assert k4.multiply(g, g) == Klein4Op.I
    
    # Test action
    assert k4.apply(Klein4Op.I, bp00) == bp00
    assert k4.apply(Klein4Op.R, bp00) == bp10
    assert k4.apply(Klein4Op.S, bp00) == bp01
    assert k4.apply(Klein4Op.C, bp00) == bp11
    
    # Orbit is complete
    orbit = k4.orbit(bp00)
    assert len(orbit) == 4
    
    # Test LatinKernel
    kernel = LatinKernel()
    
    assert kernel.is_latin()
    assert kernel.check_holographic() > 0.5
    
    # Main diagonal is zero
    for i in range(4):
        assert kernel.get(i, i) == 0
    
    # Test TetradEncoder
    assert TetradEncoder.verify_isomorphism()
    
    # Element transformations
    assert TetradEncoder.element_transformation(Element.EARTH, Klein4Op.C) == Element.AIR
    assert TetradEncoder.element_transformation(Element.WATER, Klein4Op.R) == Element.FIRE
    
    # Element-Humor correspondence
    assert TetradEncoder.element_to_humor(Element.EARTH) == Humor.BLACK_BILE
    assert TetradEncoder.element_to_humor(Element.AIR) == Humor.BLOOD
    
    return True


if __name__ == "__main__":
    print("Validating Algebraic Foundation Module...")
    assert validate_algebra()
    print("✓ Algebraic Foundation validated")
    
    print("\n--- Klein-4 Group Cayley Table ---")
    k4 = Klein4Group()
    print(k4.cayley_table())
    
    print("\n--- Latin Kernel ---")
    kernel = LatinKernel()
    print(kernel.matrix)
