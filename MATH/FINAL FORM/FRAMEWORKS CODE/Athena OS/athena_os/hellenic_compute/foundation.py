"""
ATHENA OS - HELLENIC COMPUTATION FRAMEWORK
==========================================
Part I: The Algebraic Foundation

CORE THESIS:
    The Greek philosophical corpus constitutes a complete computational
    architecture: a distributed operating system built on a single
    algebraic primitive—the Klein-4 group acting on a 2-bit state space.

THE 2-BIT STATE SPACE:
    V = Z₂ × Z₂ = {(0,0), (0,1), (1,0), (1,1)}
    
    b₁ ∈ {0,1}: First axis (Cold/Hot, Passive/Active)
    b₂ ∈ {0,1}: Second axis (Dry/Wet, Static/Dynamic)

THE KLEIN-4 GROUP:
    K₄ = {I, R, S, C}
    
    I: (b₁, b₂) → (b₁, b₂)       [Identity]
    R: (b₁, b₂) → (b₁, b₂ ⊕ 1)   [Flip second bit]
    S: (b₁, b₂) → (b₁ ⊕ 1, b₂)   [Flip first bit]
    C: (b₁, b₂) → (b₁ ⊕ 1, b₂ ⊕ 1) [Flip both bits]

THE 4×4 DIAGONAL LATIN KERNEL:
    The minimal finite realization of Klein-4 structure
    with maximal local diversity (holographic property).

SOURCES:
    - THE_HELLENIC_COMPUTATION_FRAMEWORK.docx Part I
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Callable, Any
from enum import Enum, IntEnum
import numpy as np
from functools import reduce


# =============================================================================
# THE 2-BIT STATE SPACE
# =============================================================================

class BitState(IntEnum):
    """A single bit value."""
    ZERO = 0
    ONE = 1
    
    def __xor__(self, other: BitState) -> BitState:
        return BitState((self.value ^ other.value) % 2)
    
    def flip(self) -> BitState:
        return BitState(1 - self.value)


@dataclass(frozen=True)
class StateVector:
    """
    Element of V = Z₂ × Z₂
    
    The 2-bit state space underlying all Greek tetradic systems.
    """
    
    b1: int  # First axis: Cold(0)/Hot(1)
    b2: int  # Second axis: Dry(0)/Wet(1)
    
    def __post_init__(self):
        # Ensure binary values
        object.__setattr__(self, 'b1', self.b1 % 2)
        object.__setattr__(self, 'b2', self.b2 % 2)
    
    @classmethod
    def from_tuple(cls, t: Tuple[int, int]) -> StateVector:
        return cls(t[0], t[1])
    
    @classmethod
    def from_index(cls, index: int) -> StateVector:
        """Create from index 0-3."""
        return cls(index // 2, index % 2)
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.b1, self.b2)
    
    def to_index(self) -> int:
        """Convert to index 0-3."""
        return self.b1 * 2 + self.b2
    
    def __xor__(self, other: StateVector) -> StateVector:
        """Component-wise XOR (group operation)."""
        return StateVector(
            self.b1 ^ other.b1,
            self.b2 ^ other.b2
        )
    
    def flip_first(self) -> StateVector:
        """Flip first bit (S operation)."""
        return StateVector(1 - self.b1, self.b2)
    
    def flip_second(self) -> StateVector:
        """Flip second bit (R operation)."""
        return StateVector(self.b1, 1 - self.b2)
    
    def flip_both(self) -> StateVector:
        """Flip both bits (C operation)."""
        return StateVector(1 - self.b1, 1 - self.b2)
    
    def hamming_distance(self, other: StateVector) -> int:
        """Compute Hamming distance."""
        return (self.b1 ^ other.b1) + (self.b2 ^ other.b2)
    
    def is_adjacent(self, other: StateVector) -> bool:
        """Check if states differ by single bit."""
        return self.hamming_distance(other) == 1
    
    def __repr__(self) -> str:
        return f"({self.b1},{self.b2})"


# The four states of V
V_00 = StateVector(0, 0)  # Cold-Dry
V_01 = StateVector(0, 1)  # Cold-Wet
V_10 = StateVector(1, 0)  # Hot-Dry
V_11 = StateVector(1, 1)  # Hot-Wet

STATE_SPACE = [V_00, V_01, V_10, V_11]


# =============================================================================
# ELEMENT MAPPING
# =============================================================================

class Element(Enum):
    """The four classical elements."""
    
    EARTH = "earth"   # Cold-Dry = (0,0)
    WATER = "water"   # Cold-Wet = (0,1)
    FIRE = "fire"     # Hot-Dry = (1,0)
    AIR = "air"       # Hot-Wet = (1,1)
    
    @classmethod
    def from_state(cls, state: StateVector) -> Element:
        """Map state to element."""
        mapping = {
            (0, 0): cls.EARTH,
            (0, 1): cls.WATER,
            (1, 0): cls.FIRE,
            (1, 1): cls.AIR,
        }
        return mapping[state.to_tuple()]
    
    def to_state(self) -> StateVector:
        """Map element to state."""
        mapping = {
            Element.EARTH: StateVector(0, 0),
            Element.WATER: StateVector(0, 1),
            Element.FIRE: StateVector(1, 0),
            Element.AIR: StateVector(1, 1),
        }
        return mapping[self]
    
    @property
    def is_hot(self) -> bool:
        return self.to_state().b1 == 1
    
    @property
    def is_cold(self) -> bool:
        return self.to_state().b1 == 0
    
    @property
    def is_wet(self) -> bool:
        return self.to_state().b2 == 1
    
    @property
    def is_dry(self) -> bool:
        return self.to_state().b2 == 0


# =============================================================================
# THE KLEIN-4 GROUP
# =============================================================================

class Klein4Op(Enum):
    """
    The Klein-4 group operators.
    
    K₄ = {I, R, S, C}
    """
    
    I = "identity"      # (b₁, b₂) → (b₁, b₂)
    R = "flip_second"   # (b₁, b₂) → (b₁, b₂ ⊕ 1)
    S = "flip_first"    # (b₁, b₂) → (b₁ ⊕ 1, b₂)
    C = "flip_both"     # (b₁, b₂) → (b₁ ⊕ 1, b₂ ⊕ 1)
    
    def apply(self, state: StateVector) -> StateVector:
        """Apply this operator to a state."""
        if self == Klein4Op.I:
            return state
        elif self == Klein4Op.R:
            return state.flip_second()
        elif self == Klein4Op.S:
            return state.flip_first()
        elif self == Klein4Op.C:
            return state.flip_both()
    
    def compose(self, other: Klein4Op) -> Klein4Op:
        """
        Compose two operators (self ∘ other).
        
        Cayley table for K₄:
          | I R S C
        --+--------
        I | I R S C
        R | R I C S
        S | S C I R
        C | C S R I
        """
        table = {
            (Klein4Op.I, Klein4Op.I): Klein4Op.I,
            (Klein4Op.I, Klein4Op.R): Klein4Op.R,
            (Klein4Op.I, Klein4Op.S): Klein4Op.S,
            (Klein4Op.I, Klein4Op.C): Klein4Op.C,
            
            (Klein4Op.R, Klein4Op.I): Klein4Op.R,
            (Klein4Op.R, Klein4Op.R): Klein4Op.I,
            (Klein4Op.R, Klein4Op.S): Klein4Op.C,
            (Klein4Op.R, Klein4Op.C): Klein4Op.S,
            
            (Klein4Op.S, Klein4Op.I): Klein4Op.S,
            (Klein4Op.S, Klein4Op.R): Klein4Op.C,
            (Klein4Op.S, Klein4Op.S): Klein4Op.I,
            (Klein4Op.S, Klein4Op.C): Klein4Op.R,
            
            (Klein4Op.C, Klein4Op.I): Klein4Op.C,
            (Klein4Op.C, Klein4Op.R): Klein4Op.S,
            (Klein4Op.C, Klein4Op.S): Klein4Op.R,
            (Klein4Op.C, Klein4Op.C): Klein4Op.I,
        }
        return table[(self, other)]
    
    def inverse(self) -> Klein4Op:
        """Every element is its own inverse in K₄."""
        return self
    
    @property
    def order(self) -> int:
        """Order of this element in the group."""
        if self == Klein4Op.I:
            return 1
        return 2  # All non-identity elements have order 2


class Klein4Group:
    """
    The Klein-4 group K₄ ≅ Z₂ × Z₂.
    
    The fundamental symmetry group of the Hellenic framework.
    """
    
    # Group elements
    ELEMENTS = [Klein4Op.I, Klein4Op.R, Klein4Op.S, Klein4Op.C]
    
    @classmethod
    def cayley_table(cls) -> np.ndarray:
        """Get the Cayley table as a matrix."""
        table = np.zeros((4, 4), dtype=int)
        for i, g1 in enumerate(cls.ELEMENTS):
            for j, g2 in enumerate(cls.ELEMENTS):
                result = g1.compose(g2)
                table[i, j] = cls.ELEMENTS.index(result)
        return table
    
    @classmethod
    def is_abelian(cls) -> bool:
        """K₄ is abelian (commutative)."""
        for g1 in cls.ELEMENTS:
            for g2 in cls.ELEMENTS:
                if g1.compose(g2) != g2.compose(g1):
                    return False
        return True
    
    @classmethod
    def orbit(cls, state: StateVector) -> Set[StateVector]:
        """Get the orbit of a state under K₄."""
        return {g.apply(state) for g in cls.ELEMENTS}
    
    @classmethod
    def stabilizer(cls, state: StateVector) -> Set[Klein4Op]:
        """Get elements that fix this state."""
        return {g for g in cls.ELEMENTS if g.apply(state) == state}
    
    @classmethod
    def transition(cls, from_state: StateVector, 
                  to_state: StateVector) -> Klein4Op:
        """Find the unique operator transforming from_state to to_state."""
        xor = from_state ^ to_state
        if xor.b1 == 0 and xor.b2 == 0:
            return Klein4Op.I
        elif xor.b1 == 0 and xor.b2 == 1:
            return Klein4Op.R
        elif xor.b1 == 1 and xor.b2 == 0:
            return Klein4Op.S
        else:
            return Klein4Op.C


# =============================================================================
# THE 4×4 DIAGONAL LATIN KERNEL
# =============================================================================

class LatinKernel:
    """
    The 4×4 Diagonal Latin Kernel.
    
    Properties:
    - Latin: Each symbol appears exactly once per row/column
    - Diagonal: Each symbol appears exactly once on each diagonal
    - Holographic: Most 2×2 sub-blocks contain all four symbols
    
    Generator formula: L(i,j) = (a·i + b·j) mod 4, where a,b are odd
    """
    
    def __init__(self, a: int = 1, b: int = 1):
        """
        Initialize Latin kernel.
        
        a, b: Generator parameters (must be odd for Latin property)
        """
        self.a = a | 1  # Ensure odd
        self.b = b | 1  # Ensure odd
        self._build_kernel()
    
    def _build_kernel(self) -> None:
        """Build the 4×4 kernel matrix."""
        self.matrix = np.zeros((4, 4), dtype=int)
        for i in range(4):
            for j in range(4):
                self.matrix[i, j] = (self.a * i + self.b * j) % 4
    
    def __getitem__(self, key: Tuple[int, int]) -> int:
        """Get element at (i, j)."""
        i, j = key
        return int(self.matrix[i % 4, j % 4])
    
    def is_latin(self) -> bool:
        """Verify Latin property."""
        for i in range(4):
            if len(set(self.matrix[i, :])) != 4:
                return False
            if len(set(self.matrix[:, i])) != 4:
                return False
        return True
    
    def is_diagonal(self) -> bool:
        """Verify diagonal property."""
        main_diag = {self.matrix[i, i] for i in range(4)}
        anti_diag = {self.matrix[i, 3-i] for i in range(4)}
        return len(main_diag) == 4 and len(anti_diag) == 4
    
    def holographic_ratio(self) -> float:
        """
        Calculate ratio of 2×2 sub-blocks with all 4 symbols.
        
        Perfect holography = 1.0
        """
        count = 0
        total = 9  # 3×3 possible positions for 2×2 blocks
        
        for i in range(3):
            for j in range(3):
                block = {
                    self.matrix[i, j],
                    self.matrix[i, j+1],
                    self.matrix[i+1, j],
                    self.matrix[i+1, j+1]
                }
                if len(block) == 4:
                    count += 1
        
        return count / total
    
    def to_states(self) -> np.ndarray:
        """Convert to StateVector matrix."""
        result = np.empty((4, 4), dtype=object)
        for i in range(4):
            for j in range(4):
                result[i, j] = StateVector.from_index(self.matrix[i, j])
        return result
    
    def to_elements(self) -> np.ndarray:
        """Convert to Element matrix."""
        result = np.empty((4, 4), dtype=object)
        for i in range(4):
            for j in range(4):
                state = StateVector.from_index(self.matrix[i, j])
                result[i, j] = Element.from_state(state)
        return result
    
    def __repr__(self) -> str:
        lines = []
        for row in self.matrix:
            lines.append(" ".join(str(x) for x in row))
        return "\n".join(lines)


# =============================================================================
# UNIVERSAL TETRAD ENCODING
# =============================================================================

@dataclass
class TetradMapping:
    """
    A mapping from a tetrad concept to the 2-bit state space.
    
    Every Greek tetrad maps isomorphically onto V = Z₂ × Z₂.
    """
    
    name: str
    axis1_name: str  # Name of first binary axis
    axis2_name: str  # Name of second binary axis
    
    labels: Dict[Tuple[int, int], str] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.labels:
            self.labels = {
                (0, 0): f"{self.axis1_name}=0, {self.axis2_name}=0",
                (0, 1): f"{self.axis1_name}=0, {self.axis2_name}=1",
                (1, 0): f"{self.axis1_name}=1, {self.axis2_name}=0",
                (1, 1): f"{self.axis1_name}=1, {self.axis2_name}=1",
            }
    
    def get_label(self, state: StateVector) -> str:
        """Get label for a state."""
        return self.labels.get(state.to_tuple(), "unknown")
    
    def encode(self, label: str) -> Optional[StateVector]:
        """Encode a label to a state."""
        for coords, lbl in self.labels.items():
            if lbl.lower() == label.lower():
                return StateVector.from_tuple(coords)
        return None


# Pre-defined tetrad mappings
ELEMENT_TETRAD = TetradMapping(
    name="Elements",
    axis1_name="Temperature",
    axis2_name="Moisture",
    labels={
        (0, 0): "Earth",
        (0, 1): "Water",
        (1, 0): "Fire",
        (1, 1): "Air",
    }
)

HUMOR_TETRAD = TetradMapping(
    name="Humors",
    axis1_name="Temperature",
    axis2_name="Moisture",
    labels={
        (0, 0): "Black Bile (Melancholic)",
        (0, 1): "Phlegm (Phlegmatic)",
        (1, 0): "Yellow Bile (Choleric)",
        (1, 1): "Blood (Sanguine)",
    }
)

CAUSE_TETRAD = TetradMapping(
    name="Causes",
    axis1_name="Temporal",
    axis2_name="Structural",
    labels={
        (0, 0): "Material Cause",
        (0, 1): "Formal Cause",
        (1, 0): "Efficient Cause",
        (1, 1): "Final Cause",
    }
)

CONTROL_TETRAD = TetradMapping(
    name="Control",
    axis1_name="Internal",
    axis2_name="Preferred",
    labels={
        (0, 0): "External Dispreferred",
        (0, 1): "External Preferred",
        (1, 0): "Internal Dispreferred",
        (1, 1): "Internal Preferred",
    }
)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_foundation() -> bool:
    """Validate algebraic foundation module."""
    
    # Test StateVector
    s = StateVector(0, 1)
    assert s.b1 == 0 and s.b2 == 1
    assert s.to_index() == 1
    assert StateVector.from_index(1) == s
    
    # Test XOR
    s1 = StateVector(0, 1)
    s2 = StateVector(1, 0)
    s3 = s1 ^ s2
    assert s3.b1 == 1 and s3.b2 == 1
    
    # Test flips
    assert s.flip_first() == StateVector(1, 1)
    assert s.flip_second() == StateVector(0, 0)
    assert s.flip_both() == StateVector(1, 0)
    
    # Test Klein4Op
    state = StateVector(0, 0)
    assert Klein4Op.I.apply(state) == state
    assert Klein4Op.R.apply(state) == StateVector(0, 1)
    assert Klein4Op.S.apply(state) == StateVector(1, 0)
    assert Klein4Op.C.apply(state) == StateVector(1, 1)
    
    # Test composition
    assert Klein4Op.R.compose(Klein4Op.S) == Klein4Op.C
    assert Klein4Op.S.compose(Klein4Op.R) == Klein4Op.C
    assert Klein4Op.R.compose(Klein4Op.R) == Klein4Op.I
    
    # Test Klein4Group
    assert Klein4Group.is_abelian()
    assert len(Klein4Group.orbit(StateVector(0, 0))) == 4
    
    # Test transition
    assert Klein4Group.transition(StateVector(0, 0), StateVector(1, 1)) == Klein4Op.C
    
    # Test LatinKernel
    kernel = LatinKernel()
    assert kernel.is_latin()
    assert kernel.is_diagonal()
    assert kernel.holographic_ratio() > 0.5
    
    # Test Element mapping
    assert Element.FIRE.to_state() == StateVector(1, 0)
    assert Element.from_state(StateVector(0, 1)) == Element.WATER
    
    # Test TetradMapping
    fire_state = ELEMENT_TETRAD.encode("Fire")
    assert fire_state == StateVector(1, 0)
    
    return True


if __name__ == "__main__":
    print("Validating Hellenic Computation Foundation...")
    assert validate_foundation()
    print("✓ Foundation validated")
    
    # Demo
    print("\n--- Algebraic Foundation Demo ---")
    
    print("\n1. State Space V = Z₂ × Z₂:")
    for s in STATE_SPACE:
        elem = Element.from_state(s)
        print(f"   {s} → {elem.value}")
    
    print("\n2. Klein-4 Group Cayley Table:")
    print("     I  R  S  C")
    for i, g in enumerate(Klein4Group.ELEMENTS):
        row = [g.compose(h).name[0] for h in Klein4Group.ELEMENTS]
        print(f"   {g.name[0]}  {' '.join(row)}")
    
    print("\n3. Latin Kernel (4×4):")
    kernel = LatinKernel()
    print(kernel)
    print(f"\n   Latin: {kernel.is_latin()}")
    print(f"   Diagonal: {kernel.is_diagonal()}")
    print(f"   Holographic Ratio: {kernel.holographic_ratio():.2f}")
    
    print("\n4. Element Matrix:")
    elems = kernel.to_elements()
    for row in elems:
        print(f"   {' '.join(e.value[:5] for e in row)}")
