"""
ATHENA OS - SQUARING THE CIRCLE: STATE SPACE
=============================================
The Complete 2304-State Unified Field

THE STATE SPACE:
    Complete description requires both temporal (36) and structural (64).
    Total states: 36 × 64 = 2304 = 48²
    Vocabulary: 36 + 64 = 100 (Pythagorean completion)

THE COORDINATES:
    - Temporal (θ): Which of 36 faces (when)
    - Structural (σ): Which of 64 permutations (what)
    - Together: Complete (when × what)

THE MATHEMATICS:
    gcd(36, 64) = 4   → Elemental common ground
    lcm(36, 64) = 576 = 24² → Full alignment cycle
    36 × 64 = 2304 = 48²   → Complete state space
    36 + 64 = 100 = 10²    → Pythagorean completion

All four quantities are perfect squares!

THE TORUS:
    The state space has torus topology: S¹ × T⁶
    - S¹: Circle of 36 faces (temporal)
    - T⁶: 6-torus of binary choices (structural)
    
    Paths can wind around either dimension or both.

SOURCES:
    - SQUARING_THE_CIRCLE.docx Chapters 14-15
    - Group theory (cyclic and power groups)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Iterator, Set
from enum import Enum, IntEnum
import numpy as np
import math
from itertools import product


# =============================================================================
# CONSTANTS
# =============================================================================

# Circle system
N_FACES = 36
N_SIGNS = 12
N_MODES = 3
N_ELEMENTS = 4

# Square system
N_PERMUTATIONS = 64
ELEMENT_COUNT = 4
POSITION_COUNT = 3  # root, expression, mode

# Integration
PYTHAGOREAN_COMPLETION = 100
STATE_SPACE_SIZE = N_FACES * N_PERMUTATIONS  # 2304
GCD_36_64 = 4
LCM_36_64 = 576


# =============================================================================
# ELEMENT ENCODING
# =============================================================================

class Element(IntEnum):
    """The four classical elements."""
    FIRE = 0
    WATER = 1
    AIR = 2
    EARTH = 3


ELEMENT_SYMBOLS = {
    Element.FIRE: "??",
    Element.WATER: "??",
    Element.AIR: "??",
    Element.EARTH: "??"
}

ELEMENT_LETTERS = {
    Element.FIRE: "F",
    Element.WATER: "W",
    Element.AIR: "A",
    Element.EARTH: "E"
}


# =============================================================================
# TEMPORAL COORDINATE (FACE)
# =============================================================================

@dataclass(frozen=True)
class Face:
    """
    A temporal coordinate - one of 36 faces.
    
    Properties:
        index: 0-35
        sign: 0-11 (Aries=0 through Pisces=11)
        decan: 1-3 (face within sign)
        element: Element of the sign
        mode: 0-2 (Cardinal=0, Fixed=1, Mutable=2)
    """
    
    index: int
    
    def __post_init__(self):
        if not 0 <= self.index < 36:
            raise ValueError(f"Face index must be 0-35, got {self.index}")
    
    @property
    def sign(self) -> int:
        """Zodiacal sign (0-11)."""
        return self.index // 3
    
    @property
    def decan(self) -> int:
        """Decan within sign (1-3)."""
        return (self.index % 3) + 1
    
    @property
    def element(self) -> Element:
        """Element of the sign (Fire-Earth-Air-Water cycle)."""
        element_cycle = [Element.FIRE, Element.EARTH, Element.AIR, Element.WATER]
        return element_cycle[self.sign % 4]
    
    @property
    def mode(self) -> int:
        """Mode of the sign (Cardinal=0, Fixed=1, Mutable=2)."""
        return self.sign % 3
    
    @property
    def mode_name(self) -> str:
        """Name of the mode."""
        return ["Cardinal", "Fixed", "Mutable"][self.mode]
    
    @property
    def degree_start(self) -> int:
        """Starting degree (0-359)."""
        return self.index * 10
    
    @property
    def degree_end(self) -> int:
        """Ending degree."""
        return self.degree_start + 10
    
    @property
    def symbol(self) -> str:
        """Compact symbol representation."""
        sign_symbols = "♈♉♊♋♌♍♎♏♐♑♒♓"
        return f"{sign_symbols[self.sign]}{self.decan}"
    
    def __repr__(self) -> str:
        return f"Face({self.index}: {self.symbol})"
    
    def __hash__(self) -> int:
        return hash(self.index)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Face):
            return self.index == other.index
        return False


# Generate all 36 faces
ALL_FACES = [Face(i) for i in range(36)]


# =============================================================================
# STRUCTURAL COORDINATE (PERMUTATION)
# =============================================================================

@dataclass(frozen=True)
class Permutation:
    """
    A structural coordinate - one of 64 permutations.
    
    Each permutation is a triple (root, expression, mode) of elements.
    Encodes as 4³ = 64 combinations.
    """
    
    root: Element
    expression: Element  
    mode: Element
    
    @property
    def index(self) -> int:
        """Index 0-63 in base-4 encoding."""
        return self.root * 16 + self.expression * 4 + self.mode
    
    @property
    def code(self) -> str:
        """Three-letter code (e.g., 'FWA')."""
        return (ELEMENT_LETTERS[self.root] + 
                ELEMENT_LETTERS[self.expression] + 
                ELEMENT_LETTERS[self.mode])
    
    @property
    def is_pure(self) -> bool:
        """All three elements the same."""
        return self.root == self.expression == self.mode
    
    @property
    def is_double(self) -> bool:
        """Exactly two elements the same."""
        elements = [self.root, self.expression, self.mode]
        return len(set(elements)) == 2
    
    @property
    def is_triple_distinct(self) -> bool:
        """All three elements different."""
        elements = [self.root, self.expression, self.mode]
        return len(set(elements)) == 3
    
    @property
    def element_counts(self) -> Dict[Element, int]:
        """Count of each element in the permutation."""
        counts = {e: 0 for e in Element}
        for e in [self.root, self.expression, self.mode]:
            counts[e] += 1
        return counts
    
    @property
    def dominant_element(self) -> Optional[Element]:
        """Element appearing most often (None if tied)."""
        counts = self.element_counts
        max_count = max(counts.values())
        if max_count == 1:
            return None  # All different
        dominants = [e for e, c in counts.items() if c == max_count]
        return dominants[0] if len(dominants) == 1 else None
    
    @classmethod
    def from_index(cls, index: int) -> Permutation:
        """Create from index 0-63."""
        if not 0 <= index < 64:
            raise ValueError(f"Permutation index must be 0-63, got {index}")
        root = Element(index // 16)
        expression = Element((index // 4) % 4)
        mode = Element(index % 4)
        return cls(root, expression, mode)
    
    @classmethod
    def from_code(cls, code: str) -> Permutation:
        """Create from code like 'FWA'."""
        if len(code) != 3:
            raise ValueError(f"Code must be 3 characters, got {code}")
        letter_to_element = {v: k for k, v in ELEMENT_LETTERS.items()}
        return cls(
            letter_to_element[code[0].upper()],
            letter_to_element[code[1].upper()],
            letter_to_element[code[2].upper()]
        )
    
    def __repr__(self) -> str:
        return f"Permutation({self.code})"
    
    def __hash__(self) -> int:
        return hash((self.root, self.expression, self.mode))
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Permutation):
            return (self.root == other.root and 
                    self.expression == other.expression and 
                    self.mode == other.mode)
        return False


# Generate all 64 permutations
ALL_PERMUTATIONS = [Permutation.from_index(i) for i in range(64)]

# Special permutations
PURE_FIRE = Permutation(Element.FIRE, Element.FIRE, Element.FIRE)
PURE_WATER = Permutation(Element.WATER, Element.WATER, Element.WATER)
PURE_AIR = Permutation(Element.AIR, Element.AIR, Element.AIR)
PURE_EARTH = Permutation(Element.EARTH, Element.EARTH, Element.EARTH)

PURE_PERMUTATIONS = [PURE_FIRE, PURE_WATER, PURE_AIR, PURE_EARTH]


# =============================================================================
# STATE (FACE × PERMUTATION)
# =============================================================================

@dataclass(frozen=True)
class State:
    """
    A complete state in the unified field.
    
    Combines temporal (face) and structural (permutation) coordinates.
    There are 36 × 64 = 2304 possible states.
    """
    
    face: Face
    permutation: Permutation
    
    @property
    def index(self) -> int:
        """Linear index 0-2303."""
        return self.face.index * 64 + self.permutation.index
    
    @property
    def temporal(self) -> int:
        """Temporal coordinate (face index)."""
        return self.face.index
    
    @property
    def structural(self) -> int:
        """Structural coordinate (permutation index)."""
        return self.permutation.index
    
    @property
    def coordinates(self) -> Tuple[int, int]:
        """(temporal, structural) pair."""
        return (self.temporal, self.structural)
    
    @property
    def code(self) -> str:
        """Combined code like 'F12-FWA'."""
        return f"{self.face.symbol}-{self.permutation.code}"
    
    @classmethod
    def from_index(cls, index: int) -> State:
        """Create from linear index 0-2303."""
        if not 0 <= index < 2304:
            raise ValueError(f"State index must be 0-2303, got {index}")
        face_idx = index // 64
        perm_idx = index % 64
        return cls(Face(face_idx), Permutation.from_index(perm_idx))
    
    @classmethod
    def from_coordinates(cls, temporal: int, structural: int) -> State:
        """Create from (temporal, structural) coordinates."""
        return cls(Face(temporal), Permutation.from_index(structural))
    
    def __repr__(self) -> str:
        return f"State({self.code})"
    
    def __hash__(self) -> int:
        return hash((self.face, self.permutation))


# =============================================================================
# NUMBER THEORY
# =============================================================================

class NumberTheory:
    """
    Number-theoretic properties of 36 and 64.
    """
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Greatest common divisor."""
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Least common multiple."""
        return (a * b) // NumberTheory.gcd(a, b)
    
    @staticmethod
    def prime_factorization(n: int) -> Dict[int, int]:
        """Prime factorization as {prime: exponent}."""
        factors = {}
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors[d] = factors.get(d, 0) + 1
                n //= d
            d += 1
        if n > 1:
            factors[n] = factors.get(n, 0) + 1
        return factors
    
    @staticmethod
    def is_perfect_square(n: int) -> bool:
        """Check if n is a perfect square."""
        root = int(math.sqrt(n))
        return root * root == n


# Pre-computed values
GCD = NumberTheory.gcd(36, 64)  # 4
LCM = NumberTheory.lcm(36, 64)  # 576
PRODUCT = 36 * 64  # 2304
SUM = 36 + 64  # 100

# Verify perfect squares
assert GCD == 4 == 2**2
assert LCM == 576 == 24**2
assert PRODUCT == 2304 == 48**2
assert SUM == 100 == 10**2


@dataclass
class IntegrationMathematics:
    """
    Mathematical properties of circle-square integration.
    """
    
    circle: int = 36
    square: int = 64
    
    @property
    def sum(self) -> int:
        """Pythagorean sum: 36 + 64 = 100."""
        return self.circle + self.square
    
    @property
    def gcd(self) -> int:
        """Elemental common ground: gcd(36, 64) = 4."""
        return NumberTheory.gcd(self.circle, self.square)
    
    @property
    def lcm(self) -> int:
        """Full alignment cycle: lcm(36, 64) = 576."""
        return NumberTheory.lcm(self.circle, self.square)
    
    @property
    def product(self) -> int:
        """State space size: 36 × 64 = 2304."""
        return self.circle * self.square
    
    @property
    def all_perfect_squares(self) -> bool:
        """All four quantities are perfect squares."""
        return all(NumberTheory.is_perfect_square(n) for n in 
                   [self.sum, self.gcd, self.lcm, self.product])
    
    @property
    def square_roots(self) -> Dict[str, int]:
        """Square roots of the key quantities."""
        return {
            "√sum": int(math.sqrt(self.sum)),      # 10
            "√gcd": int(math.sqrt(self.gcd)),      # 2
            "√lcm": int(math.sqrt(self.lcm)),      # 24
            "√product": int(math.sqrt(self.product)) # 48
        }
    
    @property
    def circle_cycles_in_lcm(self) -> int:
        """How many circle cycles fit in LCM: 576 / 36 = 16."""
        return self.lcm // self.circle
    
    @property
    def square_cycles_in_lcm(self) -> int:
        """How many square cycles fit in LCM: 576 / 64 = 9."""
        return self.lcm // self.square
    
    def summary(self) -> Dict[str, Any]:
        """Get complete mathematical summary."""
        return {
            "circle": self.circle,
            "square": self.square,
            "sum": f"{self.sum} = 10²",
            "gcd": f"{self.gcd} = 2²",
            "lcm": f"{self.lcm} = 24²",
            "product": f"{self.product} = 48²",
            "all_perfect_squares": self.all_perfect_squares,
            "pythagorean": f"6² + 8² = {6**2} + {8**2} = 10² = {10**2}",
            "alignment_cycles": {
                "circle_in_lcm": self.circle_cycles_in_lcm,
                "square_in_lcm": self.square_cycles_in_lcm
            }
        }


# =============================================================================
# STATE SPACE OPERATIONS
# =============================================================================

class StateSpace:
    """
    The complete 2304-state unified field.
    """
    
    N_FACES = 36
    N_PERMUTATIONS = 64
    N_STATES = 2304
    
    def __init__(self):
        self.faces = ALL_FACES
        self.permutations = ALL_PERMUTATIONS
        self.math = IntegrationMathematics()
    
    def state(self, temporal: int, structural: int) -> State:
        """Get state at given coordinates."""
        return State.from_coordinates(temporal, structural)
    
    def state_by_index(self, index: int) -> State:
        """Get state by linear index."""
        return State.from_index(index)
    
    def all_states(self) -> Iterator[State]:
        """Iterate all 2304 states."""
        for face in self.faces:
            for perm in self.permutations:
                yield State(face, perm)
    
    def states_at_face(self, face: Face) -> List[State]:
        """All 64 states at a given face."""
        return [State(face, p) for p in self.permutations]
    
    def states_with_permutation(self, perm: Permutation) -> List[State]:
        """All 36 states with a given permutation."""
        return [State(f, perm) for f in self.faces]
    
    def temporal_neighbor(self, state: State, delta: int = 1) -> State:
        """Move in temporal dimension (circular)."""
        new_face_idx = (state.face.index + delta) % 36
        return State(Face(new_face_idx), state.permutation)
    
    def structural_neighbor(self, state: State, 
                           position: int, element: Element) -> State:
        """Change one position in the permutation."""
        perm = state.permutation
        elements = [perm.root, perm.expression, perm.mode]
        elements[position] = element
        new_perm = Permutation(*elements)
        return State(state.face, new_perm)
    
    def hamming_distance(self, s1: State, s2: State) -> int:
        """Structural distance (number of differing elements)."""
        p1, p2 = s1.permutation, s2.permutation
        return sum([
            p1.root != p2.root,
            p1.expression != p2.expression,
            p1.mode != p2.mode
        ])
    
    def temporal_distance(self, s1: State, s2: State) -> int:
        """Shortest temporal distance (circular)."""
        diff = abs(s1.face.index - s2.face.index)
        return min(diff, 36 - diff)
    
    def pure_states(self) -> List[State]:
        """States with pure permutations (FFF, WWW, AAA, EEE)."""
        return [State(f, p) for f in self.faces for p in PURE_PERMUTATIONS]
    
    def cardinal_states(self) -> List[State]:
        """States at cardinal points (equinoxes/solstices)."""
        cardinal_faces = [Face(i * 9) for i in range(4)]  # Aries, Cancer, Libra, Capricorn
        return [State(f, p) for f in cardinal_faces for p in self.permutations]
    
    def grid_48x48(self) -> np.ndarray:
        """
        Represent state space as 48×48 grid.
        
        The 2304 = 48² states can be arranged in a square.
        """
        grid = np.zeros((48, 48), dtype=int)
        for i, state in enumerate(self.all_states()):
            row, col = divmod(i, 48)
            grid[row, col] = state.index
        return grid
    
    def summary(self) -> Dict[str, Any]:
        """Get state space summary."""
        return {
            "n_faces": self.N_FACES,
            "n_permutations": self.N_PERMUTATIONS,
            "n_states": self.N_STATES,
            "mathematics": self.math.summary(),
            "topology": "Torus (S¹ × T⁶)",
            "grid_dimension": "48 × 48"
        }


# =============================================================================
# ALIGNMENT CYCLES
# =============================================================================

class AlignmentCycles:
    """
    Analysis of how circle and square systems align.
    """
    
    def __init__(self):
        self.circle_period = 36
        self.square_period = 64
        self.alignment_period = LCM  # 576
    
    def circle_position(self, t: int) -> int:
        """Circle position at time t (0-35)."""
        return t % self.circle_period
    
    def square_position(self, t: int) -> int:
        """Square position at time t (0-63)."""
        return t % self.square_period
    
    def both_positions(self, t: int) -> Tuple[int, int]:
        """Both positions at time t."""
        return (self.circle_position(t), self.square_position(t))
    
    def is_aligned(self, t: int) -> bool:
        """Both systems at origin at time t."""
        return (t % self.circle_period == 0 and t % self.square_period == 0)
    
    def alignment_times(self, max_t: int = None) -> List[int]:
        """Times when both systems are at origin."""
        if max_t is None:
            max_t = self.alignment_period * 2
        return [t for t in range(max_t + 1) if self.is_aligned(t)]
    
    def phase_difference(self, t: int) -> Tuple[float, float]:
        """Phase of each system as fraction of its period."""
        c_phase = self.circle_position(t) / self.circle_period
        s_phase = self.square_position(t) / self.square_period
        return (c_phase, s_phase)
    
    def cycle_count(self, t: int) -> Tuple[int, int]:
        """Number of complete cycles of each system."""
        return (t // self.circle_period, t // self.square_period)
    
    def period_properties(self) -> Dict[str, Any]:
        """Properties of the alignment period."""
        return {
            "period": self.alignment_period,
            "is_perfect_square": NumberTheory.is_perfect_square(self.alignment_period),
            "sqrt": int(math.sqrt(self.alignment_period)),  # 24
            "circle_cycles": self.alignment_period // self.circle_period,  # 16
            "square_cycles": self.alignment_period // self.square_period,  # 9
            "interpretation": "24 'hours' squared, or 24 'days' of 24 'hours'"
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_state_space() -> bool:
    """Validate the state space module."""
    
    # Verify counts
    assert len(ALL_FACES) == 36
    assert len(ALL_PERMUTATIONS) == 64
    
    # Verify face properties
    for i, face in enumerate(ALL_FACES):
        assert face.index == i
        assert 0 <= face.sign < 12
        assert 1 <= face.decan <= 3
        assert face.degree_start == i * 10
    
    # Verify permutation properties
    for i, perm in enumerate(ALL_PERMUTATIONS):
        assert perm.index == i
        reconstructed = Permutation.from_index(i)
        assert perm == reconstructed
    
    # Verify pure permutations
    assert len(PURE_PERMUTATIONS) == 4
    for pure in PURE_PERMUTATIONS:
        assert pure.is_pure
    
    # Verify state space
    space = StateSpace()
    state_count = sum(1 for _ in space.all_states())
    assert state_count == 2304
    
    # Verify mathematics
    math = IntegrationMathematics()
    assert math.sum == 100
    assert math.gcd == 4
    assert math.lcm == 576
    assert math.product == 2304
    assert math.all_perfect_squares
    
    # Verify square roots
    roots = math.square_roots
    assert roots["√sum"] == 10
    assert roots["√gcd"] == 2
    assert roots["√lcm"] == 24
    assert roots["√product"] == 48
    
    # Verify alignment
    cycles = AlignmentCycles()
    times = cycles.alignment_times(1200)
    assert times == [0, 576, 1152]  # Every 576
    
    # Verify Pythagorean relation
    assert 6**2 + 8**2 == 10**2
    assert 36 + 64 == 100
    
    return True


if __name__ == "__main__":
    print("Validating State Space Module...")
    assert validate_state_space()
    print("✓ State Space Module validated")
    
    # Demo
    print("\n--- State Space Demo ---")
    
    math = IntegrationMathematics()
    print("\nIntegration Mathematics:")
    print(f"  Sum: {math.circle} + {math.square} = {math.sum} = 10²")
    print(f"  GCD: gcd({math.circle}, {math.square}) = {math.gcd} = 2²")
    print(f"  LCM: lcm({math.circle}, {math.square}) = {math.lcm} = 24²")
    print(f"  Product: {math.circle} × {math.square} = {math.product} = 48²")
    print(f"  All perfect squares: {math.all_perfect_squares}")
    
    space = StateSpace()
    print(f"\nState Space: {space.N_STATES} states")
    print(f"  Grid: 48 × 48")
    
    # Sample states
    s0 = space.state(0, 0)
    s1 = space.state(17, 42)
    print(f"\nSample states:")
    print(f"  Origin: {s0.code}")
    print(f"  (17, 42): {s1.code}")
    
    # Pure states
    pures = space.pure_states()
    print(f"\nPure states: {len(pures)} (36 faces × 4 pure permutations)")
    
    # Alignment cycles
    cycles = AlignmentCycles()
    props = cycles.period_properties()
    print(f"\nAlignment Period: {props['period']} = {props['sqrt']}²")
    print(f"  Circle cycles: {props['circle_cycles']}")
    print(f"  Square cycles: {props['square_cycles']}")
