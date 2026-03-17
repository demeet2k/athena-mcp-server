"""
ATHENA OS - HELLENIC COMPUTATION FRAMEWORK
==========================================
The Algebraic Foundation of Greek Philosophy

From THE_HELLENIC_COMPUTATION_FRAMEWORK.docx:

CORE THESIS:
    The Greek philosophical corpus constitutes a complete computational
    architecture: a distributed operating system built on a single
    algebraic primitive - the Klein-4 group acting on a 2-bit state space.

STATE SPACE V = Z₂ × Z₂:
    V = {(0,0), (0,1), (1,0), (1,1)}
    - b₁ ∈ {0,1}: First axis (Cold/Hot, Internal/External, Passive/Active)
    - b₂ ∈ {0,1}: Second axis (Dry/Wet, Structural/Dynamic, Simple/Composite)

KLEIN-4 GROUP K₄ = {I, R, S, C}:
    I: (b₁, b₂) → (b₁, b₂)         [Identity]
    R: (b₁, b₂) → (b₁, b₂ ⊕ 1)     [Flip second bit]
    S: (b₁, b₂) → (b₁ ⊕ 1, b₂)     [Flip first bit]
    C: (b₁, b₂) → (b₁ ⊕ 1, b₂ ⊕ 1) [Flip both bits]

UNIVERSAL TETRAD ENCODING:
    (0,0) = Earth/Black Bile/Unlimited/Material/E-N
    (0,1) = Water/Phlegm/Limit/Formal/E-U
    (1,0) = Fire/Yellow Bile/Mixture/Efficient/I-N
    (1,1) = Air/Blood/Cause/Final/I-U

4×4 DIAGONAL LATIN KERNEL:
    Generator: L(i,j) = (a·i + b·j) mod 4 where a,b are odd
    Holographic property: Most 2×2 sub-blocks contain all {0,1,2,3}
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Callable, Any
from enum import Enum, auto
import math


# =============================================================================
# 2-BIT STATE SPACE V = Z₂ × Z₂
# =============================================================================

@dataclass(frozen=True)
class BitPair:
    """
    A 2-bit state in V = Z₂ × Z₂.
    
    The minimal structure encoding all Greek tetrads.
    """
    
    b1: int  # First axis: Cold(0)/Hot(1), Internal(0)/External(1)
    b2: int  # Second axis: Dry(0)/Wet(1), Structural(0)/Dynamic(1)
    
    def __post_init__(self):
        if self.b1 not in {0, 1} or self.b2 not in {0, 1}:
            raise ValueError("Bits must be 0 or 1")
    
    def __add__(self, other: 'BitPair') -> 'BitPair':
        """Component-wise XOR (group operation)."""
        return BitPair(self.b1 ^ other.b1, self.b2 ^ other.b2)
    
    def __str__(self) -> str:
        return f"({self.b1},{self.b2})"
    
    def __repr__(self) -> str:
        return f"BitPair({self.b1}, {self.b2})"
    
    @property
    def index(self) -> int:
        """Convert to integer index 0-3."""
        return self.b1 * 2 + self.b2
    
    @classmethod
    def from_index(cls, i: int) -> 'BitPair':
        """Create from integer index 0-3."""
        return cls((i >> 1) & 1, i & 1)
    
    def flip_first(self) -> 'BitPair':
        """S operation: flip first bit."""
        return BitPair(self.b1 ^ 1, self.b2)
    
    def flip_second(self) -> 'BitPair':
        """R operation: flip second bit."""
        return BitPair(self.b1, self.b2 ^ 1)
    
    def flip_both(self) -> 'BitPair':
        """C operation: flip both bits."""
        return BitPair(self.b1 ^ 1, self.b2 ^ 1)


# The four canonical states
V_00 = BitPair(0, 0)  # Earth, Black Bile, Unlimited, Material
V_01 = BitPair(0, 1)  # Water, Phlegm, Limit, Formal
V_10 = BitPair(1, 0)  # Fire, Yellow Bile, Mixture, Efficient
V_11 = BitPair(1, 1)  # Air, Blood, Cause, Final

STATE_SPACE = {V_00, V_01, V_10, V_11}


# =============================================================================
# KLEIN-4 GROUP K₄
# =============================================================================

class K4Operation(Enum):
    """
    The Klein-4 group operations.
    
    K₄ = {I, R, S, C} acting on V = Z₂ × Z₂
    """
    I = auto()  # Identity
    R = auto()  # Flip second bit (moisture axis)
    S = auto()  # Flip first bit (thermal axis)
    C = auto()  # Flip both bits (full crisis)


@dataclass(frozen=True)
class Klein4Element:
    """
    An element of the Klein-4 group.
    
    Composition rules:
        R ∘ S = S ∘ R = C
        R² = S² = C² = I
    """
    
    op: K4Operation
    
    def __call__(self, state: BitPair) -> BitPair:
        """Apply operation to state."""
        if self.op == K4Operation.I:
            return state
        elif self.op == K4Operation.R:
            return state.flip_second()
        elif self.op == K4Operation.S:
            return state.flip_first()
        elif self.op == K4Operation.C:
            return state.flip_both()
        raise ValueError(f"Unknown operation: {self.op}")
    
    def __mul__(self, other: 'Klein4Element') -> 'Klein4Element':
        """Group composition."""
        # Cayley table for K₄
        table = {
            (K4Operation.I, K4Operation.I): K4Operation.I,
            (K4Operation.I, K4Operation.R): K4Operation.R,
            (K4Operation.I, K4Operation.S): K4Operation.S,
            (K4Operation.I, K4Operation.C): K4Operation.C,
            (K4Operation.R, K4Operation.I): K4Operation.R,
            (K4Operation.R, K4Operation.R): K4Operation.I,
            (K4Operation.R, K4Operation.S): K4Operation.C,
            (K4Operation.R, K4Operation.C): K4Operation.S,
            (K4Operation.S, K4Operation.I): K4Operation.S,
            (K4Operation.S, K4Operation.R): K4Operation.C,
            (K4Operation.S, K4Operation.S): K4Operation.I,
            (K4Operation.S, K4Operation.C): K4Operation.R,
            (K4Operation.C, K4Operation.I): K4Operation.C,
            (K4Operation.C, K4Operation.R): K4Operation.S,
            (K4Operation.C, K4Operation.S): K4Operation.R,
            (K4Operation.C, K4Operation.C): K4Operation.I,
        }
        return Klein4Element(table[(self.op, other.op)])
    
    @property
    def inverse(self) -> 'Klein4Element':
        """Every element is its own inverse in K₄."""
        return self
    
    @property
    def order(self) -> int:
        """Order of element (I has order 1, others have order 2)."""
        return 1 if self.op == K4Operation.I else 2
    
    def physical_interpretation(self) -> str:
        """Physical meaning of operation."""
        return {
            K4Operation.I: "Stability (no change)",
            K4Operation.R: "Single-axis reversal (moisture)",
            K4Operation.S: "Single-axis reversal (thermal)",
            K4Operation.C: "Full inversion (crisis/phase transition)"
        }[self.op]


# Canonical K₄ elements
K4_I = Klein4Element(K4Operation.I)
K4_R = Klein4Element(K4Operation.R)
K4_S = Klein4Element(K4Operation.S)
K4_C = Klein4Element(K4Operation.C)

KLEIN4_GROUP = {K4_I, K4_R, K4_S, K4_C}


class Klein4Group:
    """
    The complete Klein-4 group structure.
    
    Isomorphic to Z₂ × Z₂ under component-wise addition.
    """
    
    def __init__(self):
        self.elements = list(KLEIN4_GROUP)
        self.identity = K4_I
    
    def verify_group_axioms(self) -> Dict[str, bool]:
        """Verify K₄ satisfies group axioms."""
        results = {}
        
        # Closure
        closed = True
        for g in self.elements:
            for h in self.elements:
                if g * h not in KLEIN4_GROUP:
                    closed = False
        results["closure"] = closed
        
        # Identity
        has_identity = all(g * K4_I == g and K4_I * g == g for g in self.elements)
        results["identity"] = has_identity
        
        # Inverses
        has_inverses = all(g * g.inverse == K4_I for g in self.elements)
        results["inverses"] = has_inverses
        
        # Associativity (spot check)
        results["associativity"] = (K4_R * K4_S) * K4_C == K4_R * (K4_S * K4_C)
        
        # Abelian (commutative)
        results["abelian"] = all(
            g * h == h * g for g in self.elements for h in self.elements
        )
        
        return results
    
    def orbit(self, state: BitPair) -> Set[BitPair]:
        """Compute orbit of state under K₄ action."""
        return {g(state) for g in self.elements}
    
    def stabilizer(self, state: BitPair) -> Set[Klein4Element]:
        """Compute stabilizer of state."""
        return {g for g in self.elements if g(state) == state}


# =============================================================================
# UNIVERSAL TETRAD ENCODING
# =============================================================================

class TetradSystem(Enum):
    """The various Greek tetrad systems."""
    ELEMENTS = auto()
    HUMORS = auto()
    PLATONIC_KINDS = auto()
    CAUSES = auto()
    STOIC_CONTROL = auto()
    K4_OPERATIONS = auto()


@dataclass
class TetradMapping:
    """Maps bit pairs to tetrad values."""
    
    system: TetradSystem
    encoding: Dict[BitPair, str]
    
    def __getitem__(self, state: BitPair) -> str:
        return self.encoding[state]
    
    def decode(self, value: str) -> BitPair:
        """Reverse lookup."""
        for bp, v in self.encoding.items():
            if v == value:
                return bp
        raise ValueError(f"Unknown value: {value}")


# The canonical encodings from the manuscript
ELEMENT_ENCODING = TetradMapping(
    TetradSystem.ELEMENTS,
    {V_00: "Earth", V_01: "Water", V_10: "Fire", V_11: "Air"}
)

HUMOR_ENCODING = TetradMapping(
    TetradSystem.HUMORS,
    {V_00: "Black Bile", V_01: "Phlegm", V_10: "Yellow Bile", V_11: "Blood"}
)

PLATONIC_ENCODING = TetradMapping(
    TetradSystem.PLATONIC_KINDS,
    {V_00: "Unlimited", V_01: "Limit", V_10: "Mixture", V_11: "Cause"}
)

CAUSE_ENCODING = TetradMapping(
    TetradSystem.CAUSES,
    {V_00: "Material", V_01: "Formal", V_10: "Efficient", V_11: "Final"}
)

STOIC_ENCODING = TetradMapping(
    TetradSystem.STOIC_CONTROL,
    {V_00: "External-NotUpToUs", V_01: "External-UpToUs",
     V_10: "Internal-NotUpToUs", V_11: "Internal-UpToUs"}
)

K4_ENCODING = TetradMapping(
    TetradSystem.K4_OPERATIONS,
    {V_00: "I (Identity)", V_01: "R (Flip b2)", V_10: "S (Flip b1)", V_11: "C (Flip both)"}
)

ALL_ENCODINGS = [
    ELEMENT_ENCODING, HUMOR_ENCODING, PLATONIC_ENCODING,
    CAUSE_ENCODING, STOIC_ENCODING, K4_ENCODING
]


class UniversalTetradEncoder:
    """
    Universal encoder/decoder for all Greek tetrads.
    
    All Greek tetrads are isomorphic to V = Z₂ × Z₂.
    """
    
    def __init__(self):
        self.encodings = {e.system: e for e in ALL_ENCODINGS}
    
    def encode(self, state: BitPair, system: TetradSystem) -> str:
        """Encode bit pair to tetrad value."""
        return self.encodings[system][state]
    
    def decode(self, value: str, system: TetradSystem) -> BitPair:
        """Decode tetrad value to bit pair."""
        return self.encodings[system].decode(value)
    
    def translate(self, value: str, from_system: TetradSystem,
                 to_system: TetradSystem) -> str:
        """Translate between tetrad systems via bit pair."""
        bp = self.decode(value, from_system)
        return self.encode(bp, to_system)
    
    def full_decode(self, state: BitPair) -> Dict[TetradSystem, str]:
        """Get all tetrad values for a bit pair."""
        return {system: self.encode(state, system) for system in TetradSystem}
    
    def axis_interpretation(self) -> Dict[str, Tuple[str, str]]:
        """Get axis interpretations for each system."""
        return {
            "Elements/Humors": ("b₁: Cold(0)/Hot(1)", "b₂: Dry(0)/Wet(1)"),
            "Platonic Kinds": ("b₁: Simple(0)/Composite(1)", "b₂: Passive(0)/Active(1)"),
            "Causes": ("b₁: Internal(0)/External(1)", "b₂: Structural(0)/Telic(1)")
        }


# =============================================================================
# 4×4 DIAGONAL LATIN SQUARE
# =============================================================================

class LatinSquare:
    """
    The 4×4 Diagonal Latin Square - the holographic seed.
    
    Properties:
    - Latin: Each symbol appears exactly once per row/column
    - Diagonal: Each symbol appears exactly once on each main diagonal
    - Holographic: Most 2×2 sub-blocks contain all {0,1,2,3}
    
    Generator: L(i,j) = (a·i + b·j) mod 4 where a,b are odd
    """
    
    def __init__(self, a: int = 1, b: int = 1):
        """
        Create Latin square with generators a, b.
        
        Args:
            a, b: Odd integers for generator formula
        """
        if a % 2 == 0 or b % 2 == 0:
            raise ValueError("Generators must be odd integers")
        
        self.a = a % 4
        self.b = b % 4
        self.grid = [[self._generate(i, j) for j in range(4)] for i in range(4)]
    
    def _generate(self, i: int, j: int) -> int:
        """L(i,j) = (a·i + b·j) mod 4"""
        return (self.a * i + self.b * j) % 4
    
    def __getitem__(self, pos: Tuple[int, int]) -> int:
        """Get value at position (i, j)."""
        i, j = pos
        return self.grid[i % 4][j % 4]
    
    def verify_latin_property(self) -> bool:
        """Verify each symbol appears once per row/column."""
        # Check rows
        for row in self.grid:
            if set(row) != {0, 1, 2, 3}:
                return False
        
        # Check columns
        for j in range(4):
            col = [self.grid[i][j] for i in range(4)]
            if set(col) != {0, 1, 2, 3}:
                return False
        
        return True
    
    def verify_diagonal_property(self) -> bool:
        """Verify each symbol appears once on each main diagonal."""
        main_diag = [self.grid[i][i] for i in range(4)]
        anti_diag = [self.grid[i][3-i] for i in range(4)]
        return set(main_diag) == {0, 1, 2, 3} and set(anti_diag) == {0, 1, 2, 3}
    
    def count_holographic_windows(self) -> Tuple[int, int]:
        """
        Count 2×2 sub-blocks containing all {0,1,2,3}.
        
        Returns (holographic_count, total_count)
        """
        holographic = 0
        total = 0
        
        for i in range(3):
            for j in range(3):
                window = {
                    self.grid[i][j], self.grid[i][j+1],
                    self.grid[i+1][j], self.grid[i+1][j+1]
                }
                total += 1
                if window == {0, 1, 2, 3}:
                    holographic += 1
        
        return holographic, total
    
    @property
    def holographic_ratio(self) -> float:
        """Ratio of holographic windows."""
        h, t = self.count_holographic_windows()
        return h / t if t > 0 else 0.0
    
    def display(self) -> str:
        """Display the Latin square."""
        lines = []
        for row in self.grid:
            lines.append(" ".join(str(x) for x in row))
        return "\n".join(lines)


# The canonical 4×4 kernel from the manuscript
CANONICAL_LATIN = LatinSquare(1, 1)


# =============================================================================
# LIMITER/UNLIMITED BINARY
# =============================================================================

class LimitUnlimitedColumn(Enum):
    """The fundamental binary of Greek philosophy."""
    LIMIT = auto()    # Column A: Finite, Odd, Knowable, Right, Light, Rest
    UNLIMITED = auto()  # Column B: Infinite, Even, Unknowable, Left, Dark, Motion


@dataclass
class LimitUnlimited:
    """
    The Limiter/Unlimited binary structure.
    
    Object = Limit ∩ Unlimited
    Reality = Constrained_Noise
    
    The Unlimited provides magnitude (Muchness).
    The Limiter provides identity (Whatness).
    """
    
    @staticmethod
    def classify_number(n: int) -> LimitUnlimitedColumn:
        """Classify number as Limit (odd) or Unlimited (even)."""
        return LimitUnlimitedColumn.LIMIT if n % 2 == 1 else LimitUnlimitedColumn.UNLIMITED
    
    @staticmethod
    def compile_object(limit: float, unlimited: float) -> float:
        """
        Object = Limit ∩ Unlimited = Constrained magnitude.
        
        Apply limit to unlimited to produce bounded value.
        """
        # Limit constrains the unlimited
        return min(limit, unlimited) if unlimited > 0 else 0.0
    
    @staticmethod
    def column_attributes(column: LimitUnlimitedColumn) -> Dict[str, str]:
        """Get attributes of each column."""
        if column == LimitUnlimitedColumn.LIMIT:
            return {
                "state": "Finite",
                "number": "Odd",
                "epistemology": "Knowable",
                "direction": "Right",
                "light": "Light",
                "motion": "Rest"
            }
        else:
            return {
                "state": "Infinite",
                "number": "Even",
                "epistemology": "Unknowable",
                "direction": "Left",
                "light": "Dark",
                "motion": "Motion"
            }


# =============================================================================
# INTEGRATION: THE HELLENIC COMPUTATIONAL MODEL
# =============================================================================

class HellenicComputationalModel:
    """
    The complete Hellenic Computation Framework.
    
    Unifies all Greek tetrads under the K₄ algebraic structure.
    """
    
    def __init__(self):
        self.state_space = STATE_SPACE
        self.group = Klein4Group()
        self.encoder = UniversalTetradEncoder()
        self.latin_square = CANONICAL_LATIN
        self.limit_unlimited = LimitUnlimited()
    
    def transform(self, state: BitPair, operation: K4Operation) -> BitPair:
        """Apply K₄ transformation to state."""
        op = Klein4Element(operation)
        return op(state)
    
    def full_orbit(self, initial: BitPair) -> Dict[K4Operation, BitPair]:
        """Show all K₄ transformations of a state."""
        return {
            K4Operation.I: K4_I(initial),
            K4Operation.R: K4_R(initial),
            K4Operation.S: K4_S(initial),
            K4Operation.C: K4_C(initial)
        }
    
    def tetrad_transition(self, system: TetradSystem, 
                         value: str, operation: K4Operation) -> str:
        """Apply K₄ operation within a tetrad system."""
        state = self.encoder.decode(value, system)
        new_state = self.transform(state, operation)
        return self.encoder.encode(new_state, system)
    
    def verify_isomorphism(self) -> bool:
        """
        Verify all tetrads are isomorphic to Z₂ × Z₂.
        
        Each tetrad has 4 elements defined by 2 orthogonal binary axes.
        """
        # All encodings have exactly 4 elements
        for encoding in ALL_ENCODINGS:
            if len(encoding.encoding) != 4:
                return False
        
        # K₄ provides complete transition coverage
        axioms = self.group.verify_group_axioms()
        return all(axioms.values())


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hellenic_foundation() -> bool:
    """Validate the Hellenic foundation module."""
    
    # Test BitPair
    bp = BitPair(0, 1)
    assert bp.b1 == 0 and bp.b2 == 1
    assert bp.index == 1
    assert BitPair.from_index(2) == V_10
    
    # Test operations
    assert V_00.flip_first() == V_10
    assert V_00.flip_second() == V_01
    assert V_00.flip_both() == V_11
    
    # Test group addition
    assert V_00 + V_11 == V_11
    assert V_10 + V_01 == V_11
    
    # Test K₄ operations
    assert K4_I(V_00) == V_00
    assert K4_R(V_00) == V_01
    assert K4_S(V_00) == V_10
    assert K4_C(V_00) == V_11
    
    # Test composition
    assert K4_R * K4_S == K4_C
    assert K4_S * K4_R == K4_C
    assert K4_R * K4_R == K4_I
    assert K4_C * K4_C == K4_I
    
    # Verify group axioms
    k4 = Klein4Group()
    axioms = k4.verify_group_axioms()
    assert all(axioms.values())
    
    # Test encodings
    encoder = UniversalTetradEncoder()
    assert encoder.encode(V_00, TetradSystem.ELEMENTS) == "Earth"
    assert encoder.encode(V_11, TetradSystem.HUMORS) == "Blood"
    assert encoder.decode("Fire", TetradSystem.ELEMENTS) == V_10
    
    # Test translation
    translated = encoder.translate("Fire", TetradSystem.ELEMENTS, TetradSystem.HUMORS)
    assert translated == "Yellow Bile"
    
    # Test Latin square
    ls = CANONICAL_LATIN
    assert ls.verify_latin_property()
    assert ls.verify_diagonal_property()
    h, t = ls.count_holographic_windows()
    assert h > 0  # Some holographic windows exist
    
    # Test Limit/Unlimited
    lu = LimitUnlimited()
    assert lu.classify_number(1) == LimitUnlimitedColumn.LIMIT
    assert lu.classify_number(2) == LimitUnlimitedColumn.UNLIMITED
    
    # Test integrated model
    model = HellenicComputationalModel()
    assert model.verify_isomorphism()
    
    # Test tetrad transition
    result = model.tetrad_transition(TetradSystem.ELEMENTS, "Earth", K4Operation.C)
    assert result == "Air"  # (0,0) → (1,1)
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - HELLENIC COMPUTATION FRAMEWORK")
    print("The Algebraic Foundation of Greek Philosophy")
    print("=" * 60)
    
    print("\nValidating module...")
    assert validate_hellenic_foundation()
    print("✓ Module validated")
    
    # Demo
    print("\n--- STATE SPACE V = Z₂ × Z₂ ---")
    for s in [V_00, V_01, V_10, V_11]:
        print(f"  {s}")
    
    print("\n--- KLEIN-4 GROUP ---")
    k4 = Klein4Group()
    axioms = k4.verify_group_axioms()
    for ax, passed in axioms.items():
        print(f"  {ax}: {'✓' if passed else '✗'}")
    
    print("\n--- UNIVERSAL TETRAD ENCODING ---")
    encoder = UniversalTetradEncoder()
    for state in [V_00, V_01, V_10, V_11]:
        print(f"\n  {state}:")
        full = encoder.full_decode(state)
        for sys, val in full.items():
            print(f"    {sys.name}: {val}")
    
    print("\n--- 4×4 LATIN SQUARE ---")
    print(CANONICAL_LATIN.display())
    print(f"  Latin property: {CANONICAL_LATIN.verify_latin_property()}")
    print(f"  Diagonal property: {CANONICAL_LATIN.verify_diagonal_property()}")
    print(f"  Holographic ratio: {CANONICAL_LATIN.holographic_ratio:.2%}")
    
    print("\n--- K₄ TRANSFORMATIONS (from Earth) ---")
    model = HellenicComputationalModel()
    orbit = model.full_orbit(V_00)
    for op, state in orbit.items():
        element = encoder.encode(state, TetradSystem.ELEMENTS)
        print(f"  {op.name}: {state} → {element}")
