"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      HOLOGRAPHIC SEED MODULE                                 ║
║                                                                              ║
║  The 4×4 Diagonal Latin Square as Transformation Kernel                      ║
║                                                                              ║
║  Properties:                                                                 ║
║    - Order-4 Latin square with both diagonals Latin                          ║
║    - Extremal 2×2 "holographic" local coverage                               ║
║    - K₄ (Klein-4 group) symmetry backbone                                    ║
║    - 2-bit state space interpretation                                        ║
║                                                                              ║
║  Greek Tetradic Correspondence:                                              ║
║    Fire  = (hot, dry)    = (1,1) = Earth                                     ║
║    Air   = (hot, moist)  = (1,0) = Water                                     ║
║    Water = (cold, moist) = (0,0) = Fire                                      ║
║    Earth = (cold, dry)   = (0,1) = Air                                       ║
║                                                                              ║
║  Radix-4 Extension:                                                          ║
║    n-dimensional Latin arrays via base-4 digit functions                     ║
║    Carry hyperplanes as codimension-1 defect surfaces                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# KLEIN-4 GROUP
# ═══════════════════════════════════════════════════════════════════════════════

class K4Element(Enum):
    """
    Elements of the Klein-4 group K₄ ≅ ℤ₂ × ℤ₂.
    
    Acting on {1,2,3,4} or equivalently on {00,01,10,11}.
    """
    IDENTITY = "e"       # Identity: x → x
    COMPLEMENT = "c"     # Complement: x → 5-x (bit flip both)
    REVERSAL = "r"       # Reversal: swap pairs (bit flip first)
    SWAP = "s"           # Swap: exchange middle elements (bit flip second)


@dataclass
class Klein4Group:
    """
    The Klein-4 group K₄ ≅ ℤ₂ × ℤ₂.
    
    This is the automorphism group of the 2-bit state space {0,1}².
    
    Four elements:
    - e (identity): (a,b) → (a,b)
    - c (complement): (a,b) → (1-a, 1-b)
    - r (reversal): (a,b) → (1-a, b)
    - s (swap): (a,b) → (a, 1-b)
    
    Multiplication table:
        e  c  r  s
      ┌──────────
    e │ e  c  r  s
    c │ c  e  s  r
    r │ r  s  e  c
    s │ s  r  c  e
    """
    
    @staticmethod
    def apply_to_bits(element: K4Element, bits: Tuple[int, int]) -> Tuple[int, int]:
        """Apply K₄ element to 2-bit state."""
        a, b = bits
        if element == K4Element.IDENTITY:
            return (a, b)
        elif element == K4Element.COMPLEMENT:
            return (1 - a, 1 - b)
        elif element == K4Element.REVERSAL:
            return (1 - a, b)
        elif element == K4Element.SWAP:
            return (a, 1 - b)
        return (a, b)
    
    @staticmethod
    def apply_to_symbol(element: K4Element, symbol: int) -> int:
        """
        Apply K₄ element to symbol in {1,2,3,4}.
        
        Encoding: 1→(0,0), 2→(0,1), 3→(1,0), 4→(1,1)
        """
        # Convert symbol to bits
        bits = ((symbol - 1) >> 1, (symbol - 1) & 1)
        # Apply transformation
        new_bits = Klein4Group.apply_to_bits(element, bits)
        # Convert back to symbol
        return 1 + (new_bits[0] << 1) + new_bits[1]
    
    @staticmethod
    def apply_to_row(element: K4Element, row: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Apply K₄ element to generate new row."""
        return tuple(Klein4Group.apply_to_symbol(element, s) for s in row)
    
    @staticmethod
    def multiplication_table() -> Dict[Tuple[K4Element, K4Element], K4Element]:
        """K₄ multiplication table."""
        e, c, r, s = K4Element.IDENTITY, K4Element.COMPLEMENT, K4Element.REVERSAL, K4Element.SWAP
        return {
            (e, e): e, (e, c): c, (e, r): r, (e, s): s,
            (c, e): c, (c, c): e, (c, r): s, (c, s): r,
            (r, e): r, (r, c): s, (r, r): e, (r, s): c,
            (s, e): s, (s, c): r, (s, r): c, (s, s): e,
        }
    
    @staticmethod
    def multiply(a: K4Element, b: K4Element) -> K4Element:
        """Multiply two K₄ elements."""
        return Klein4Group.multiplication_table()[(a, b)]


# ═══════════════════════════════════════════════════════════════════════════════
# 4×4 DIAGONAL LATIN SQUARE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DiagonalLatinSquare:
    """
    A 4×4 diagonal Latin square with extremal holographic properties.
    
    Properties:
    - Each row contains {1,2,3,4} exactly once (Latin)
    - Each column contains {1,2,3,4} exactly once (Latin)
    - Both main diagonals contain {1,2,3,4} exactly once (Diagonal)
    - Maximal 2×2 holographic coverage (14 of 16 subsquares have all 4 symbols)
    
    There are exactly two such squares (Type A and Type B), twins under
    column permutation.
    """
    matrix: NDArray  # 4×4 array with values 1,2,3,4
    name: str = "TypeA"
    
    @classmethod
    def type_a(cls) -> 'DiagonalLatinSquare':
        """
        Type A diagonal Latin square.
        
        1 2 3 4
        3 4 1 2
        4 3 2 1
        2 1 4 3
        """
        return cls(np.array([
            [1, 2, 3, 4],
            [3, 4, 1, 2],
            [4, 3, 2, 1],
            [2, 1, 4, 3]
        ]), "TypeA")
    
    @classmethod
    def type_b(cls) -> 'DiagonalLatinSquare':
        """
        Type B diagonal Latin square (twin of Type A).
        
        1 2 3 4
        4 3 2 1
        3 4 1 2
        2 1 4 3
        """
        return cls(np.array([
            [1, 2, 3, 4],
            [4, 3, 2, 1],
            [3, 4, 1, 2],
            [2, 1, 4, 3]
        ]), "TypeB")
    
    def is_latin(self) -> bool:
        """Check if rows and columns are Latin."""
        for i in range(4):
            if set(self.matrix[i, :]) != {1, 2, 3, 4}:
                return False
            if set(self.matrix[:, i]) != {1, 2, 3, 4}:
                return False
        return True
    
    def is_diagonal_latin(self) -> bool:
        """Check if both diagonals are Latin."""
        main_diag = {self.matrix[i, i] for i in range(4)}
        anti_diag = {self.matrix[i, 3-i] for i in range(4)}
        return main_diag == {1, 2, 3, 4} and anti_diag == {1, 2, 3, 4}
    
    def subsquare_2x2(self, i: int, j: int) -> set:
        """Get symbols in 2×2 subsquare starting at (i,j)."""
        return {
            self.matrix[i, j],
            self.matrix[i, j+1],
            self.matrix[i+1, j],
            self.matrix[i+1, j+1]
        }
    
    def is_holographic_2x2(self, i: int, j: int) -> bool:
        """Check if 2×2 subsquare at (i,j) contains all 4 symbols."""
        return self.subsquare_2x2(i, j) == {1, 2, 3, 4}
    
    def holographic_count(self) -> int:
        """Count how many of the 9 possible 2×2 subsquares are holographic."""
        count = 0
        for i in range(3):
            for j in range(3):
                if self.is_holographic_2x2(i, j):
                    count += 1
        return count
    
    def holographic_map(self) -> NDArray:
        """3×3 array showing which 2×2 subsquares are holographic."""
        result = np.zeros((3, 3), dtype=int)
        for i in range(3):
            for j in range(3):
                result[i, j] = 1 if self.is_holographic_2x2(i, j) else 0
        return result
    
    def row_as_k4_orbit(self) -> List[K4Element]:
        """
        Express rows as K₄ orbit of base row.
        
        Returns the K₄ element that generates each row from row 0.
        """
        base_row = tuple(self.matrix[0, :])
        elements = []
        
        for i in range(4):
            row = tuple(self.matrix[i, :])
            for elem in K4Element:
                if Klein4Group.apply_to_row(elem, base_row) == row:
                    elements.append(elem)
                    break
        
        return elements


# ═══════════════════════════════════════════════════════════════════════════════
# GREEK TETRADIC MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

class GreekElement(Enum):
    """The four classical elements."""
    FIRE = "Fire"    # Hot + Dry
    AIR = "Air"      # Hot + Moist
    WATER = "Water"  # Cold + Moist
    EARTH = "Earth"  # Cold + Dry


class GreekHumor(Enum):
    """The four Hippocratic humors."""
    BLOOD = "Blood"           # Hot + Moist
    YELLOW_BILE = "YellowBile" # Hot + Dry
    PHLEGM = "Phlegm"         # Cold + Moist
    BLACK_BILE = "BlackBile"   # Cold + Dry


@dataclass
class TetradicMapping:
    """
    Maps 2-bit states to Greek tetradic systems.
    
    Quality axes:
    - Bit 0: Hot(1) vs Cold(0)
    - Bit 1: Dry(1) vs Moist(0)
    
    Elements:
    (1,1) = Fire (hot, dry)
    (1,0) = Air (hot, moist)
    (0,0) = Water (cold, moist)
    (0,1) = Earth (cold, dry)
    """
    
    @staticmethod
    def bits_to_element(bits: Tuple[int, int]) -> GreekElement:
        """Convert 2-bit state to element."""
        mapping = {
            (1, 1): GreekElement.FIRE,
            (1, 0): GreekElement.AIR,
            (0, 0): GreekElement.WATER,
            (0, 1): GreekElement.EARTH,
        }
        return mapping[bits]
    
    @staticmethod
    def element_to_bits(element: GreekElement) -> Tuple[int, int]:
        """Convert element to 2-bit state."""
        mapping = {
            GreekElement.FIRE: (1, 1),
            GreekElement.AIR: (1, 0),
            GreekElement.WATER: (0, 0),
            GreekElement.EARTH: (0, 1),
        }
        return mapping[element]
    
    @staticmethod
    def bits_to_humor(bits: Tuple[int, int]) -> GreekHumor:
        """Convert 2-bit state to humor."""
        mapping = {
            (1, 0): GreekHumor.BLOOD,        # Hot + Moist
            (1, 1): GreekHumor.YELLOW_BILE,  # Hot + Dry
            (0, 0): GreekHumor.PHLEGM,       # Cold + Moist
            (0, 1): GreekHumor.BLACK_BILE,   # Cold + Dry
        }
        return mapping[bits]
    
    @staticmethod
    def symbol_to_element(symbol: int) -> GreekElement:
        """Convert symbol 1-4 to element."""
        bits = ((symbol - 1) >> 1, (symbol - 1) & 1)
        return TetradicMapping.bits_to_element(bits)
    
    @staticmethod
    def k4_as_quality_transform() -> Dict[K4Element, str]:
        """Interpret K₄ elements as quality transformations."""
        return {
            K4Element.IDENTITY: "No change",
            K4Element.COMPLEMENT: "Invert both (hot↔cold, dry↔moist)",
            K4Element.REVERSAL: "Temperature flip (hot↔cold)",
            K4Element.SWAP: "Humidity flip (dry↔moist)",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# RADIX-4 EXTENSION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Radix4Projector:
    """
    Radix-4 extension of the 4×4 kernel to n dimensions.
    
    For coordinates x = (x^(0), ..., x^(n-1)) in {0,1,...,4^m-1}^n,
    the projector L(x) is computed via base-4 digit functions.
    
    L(x) = Σ_t α_t · (Σ_d x_t^(d)) + β_t  (mod 4)
    
    where x_t^(d) is the t-th base-4 digit of x^(d).
    """
    n: int  # Number of dimensions
    m: int  # Number of base-4 digits (precision)
    alpha: NDArray  # Coefficients α[t][d], shape (m, n)
    beta: NDArray   # Offsets β[t], shape (m,)
    
    @classmethod
    def default(cls, n: int, m: int = None) -> 'Radix4Projector':
        """Create default projector."""
        if m is None:
            m = n - 1
        
        # Default: α[t][d] = 1 (odd), β[t] = 0
        alpha = np.ones((m, n), dtype=int)
        beta = np.zeros(m, dtype=int)
        
        return cls(n, m, alpha, beta)
    
    def digit(self, value: int, t: int) -> int:
        """Extract t-th base-4 digit of value."""
        return (value >> (2 * t)) & 3
    
    def evaluate(self, x: NDArray) -> int:
        """
        Evaluate projector L(x).
        
        Returns value in {0, 1, 2, 3}.
        """
        result = 0
        
        for t in range(self.m):
            digit_sum = 0
            for d in range(self.n):
                digit_sum += self.alpha[t, d] * self.digit(int(x[d]), t)
            result += digit_sum + self.beta[t]
        
        return result % 4
    
    def is_on_carry_hyperplane(self, x: NDArray, d: int, t: int) -> bool:
        """
        Check if point x lies on carry hyperplane H_{d,t}.
        
        H_{d,t} is where the t-th digit of x^(d) equals 3.
        """
        return self.digit(int(x[d]), t) == 3


@dataclass
class RadixBlock:
    """
    A 2^k block in the radix-4 lattice.
    
    Used for testing local holographic properties.
    """
    corner: NDArray  # Starting corner of block
    dimensions: int  # k dimensions involved in block
    projector: Radix4Projector
    
    def get_vertices(self) -> List[NDArray]:
        """Get all 2^k vertices of the block."""
        vertices = []
        for mask in range(2 ** self.dimensions):
            vertex = self.corner.copy()
            for d in range(self.dimensions):
                if (mask >> d) & 1:
                    vertex[d] += 1
            vertices.append(vertex)
        return vertices
    
    def get_labels(self) -> set:
        """Get set of projector labels at all vertices."""
        return {self.projector.evaluate(v) for v in self.get_vertices()}
    
    def is_holographic(self) -> bool:
        """Check if block contains all 4 symbols."""
        return self.get_labels() == {0, 1, 2, 3}


# ═══════════════════════════════════════════════════════════════════════════════
# HOLOGRAPHIC ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HolographicAnalysis:
    """
    Analysis of holographic properties of a radix-4 projector.
    """
    projector: Radix4Projector
    
    def sample_holography_rate(self, n_samples: int = 1000) -> float:
        """
        Estimate fraction of 2×2×...×2 blocks that are holographic.
        """
        holographic_count = 0
        size = 4 ** self.projector.m
        
        for _ in range(n_samples):
            corner = np.random.randint(0, size - 1, self.projector.n)
            block = RadixBlock(corner, self.projector.n, self.projector)
            if block.is_holographic():
                holographic_count += 1
        
        return holographic_count / n_samples
    
    def carry_hyperplane_fraction(self, d: int, t: int,
                                   n_samples: int = 1000) -> float:
        """Estimate fraction of points on carry hyperplane H_{d,t}."""
        on_hyperplane = 0
        size = 4 ** self.projector.m
        
        for _ in range(n_samples):
            x = np.random.randint(0, size, self.projector.n)
            if self.projector.is_on_carry_hyperplane(x, d, t):
                on_hyperplane += 1
        
        return on_hyperplane / n_samples


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HolographicSeedPoleBridge:
    """
    Bridge between Holographic Seed and four-pole framework.
    """
    
    @staticmethod
    def integration() -> str:
        return """
        HOLOGRAPHIC SEED ↔ FRAMEWORK
        
        The 4×4 Diagonal Latin Square as the discrete/particle-side
        dual to the continuous/wave-side flowers.
        
        K₄ Group ↔ Pole Transformations:
          e (identity)   → Stay in current pole
          c (complement) → Diagonal flip (Ψ↔D, C↔Σ)
          r (reversal)   → Horizontal flip
          s (swap)       → Vertical flip
        
        Chart Mapping:
          Latin square structure → □ Square chart
          K₄ symmetry → chart transitions
          2-bit encoding → binary control space
        
        Greek Correspondence:
          Fire  (1,1) ↔ D-pole (discrete/exact)
          Air   (1,0) ↔ C-pole (continuous/phase)
          Water (0,0) ↔ Σ-pole (stochastic)
          Earth (0,1) ↔ Ψ-pole (recursive)
        
        Properties:
          - 14/16 holographic 2×2 subsquares (extremal)
          - Both diagonals Latin
          - K₄ generates all rows from base row
          - Radix-4 scales to n dimensions
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def klein4_group() -> Klein4Group:
    """Create Klein-4 group."""
    return Klein4Group()


def latin_square_type_a() -> DiagonalLatinSquare:
    """Create Type A diagonal Latin square."""
    return DiagonalLatinSquare.type_a()


def latin_square_type_b() -> DiagonalLatinSquare:
    """Create Type B diagonal Latin square."""
    return DiagonalLatinSquare.type_b()


def tetradic_mapping() -> TetradicMapping:
    """Create tetradic mapping."""
    return TetradicMapping()


def radix4_projector(n: int, m: int = None) -> Radix4Projector:
    """Create radix-4 projector."""
    return Radix4Projector.default(n, m)


def holographic_analysis(projector: Radix4Projector) -> HolographicAnalysis:
    """Create holographic analysis."""
    return HolographicAnalysis(projector)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # K₄ Group
    'K4Element',
    'Klein4Group',
    
    # Latin Square
    'DiagonalLatinSquare',
    
    # Greek Mapping
    'GreekElement',
    'GreekHumor',
    'TetradicMapping',
    
    # Radix-4
    'Radix4Projector',
    'RadixBlock',
    
    # Analysis
    'HolographicAnalysis',
    
    # Bridge
    'HolographicSeedPoleBridge',
    
    # Functions
    'klein4_group',
    'latin_square_type_a',
    'latin_square_type_b',
    'tetradic_mapping',
    'radix4_projector',
    'holographic_analysis',
]
