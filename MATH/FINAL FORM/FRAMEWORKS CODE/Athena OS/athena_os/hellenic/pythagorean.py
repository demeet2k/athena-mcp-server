"""
ATHENA OS - HELLENIC: PYTHAGOREAN COMPUTATION ENGINE
=====================================================
The Dimensional Bootstrapping System

THE TETRACTYS:
    T = {1, 2, 3, 4} with ΣT = 10
    
    Encodes complete dimensional expansion:
    Row 1 (Monad):  Point      (0D) - Unity/Limit
    Row 2 (Dyad):   Line       (1D) - Flow/Direction
    Row 3 (Triad):  Triangle   (2D) - Surface/Enclosure
    Row 4 (Tetrad): Tetrahedron(3D) - Volume/Body

THE HARMONIC RATIOS:
    Integers {1,2,3,4} define ratio operations on frequency:
    - 1:1 Unison     - Identity (no data transfer)
    - 2:1 Octave     - Loop boundary (recursion)
    - 3:2 Fifth      - Generation (expansion)
    - 4:3 Fourth     - Frame (structure)

THE PYTHAGOREAN COMMA:
    12 fifths ≠ 7 octaves
    (3/2)^12 / 2^7 ≈ 1.0136 (The Schism)
    
    This "error" is actually the security feature that prevents
    infinite precision attacks on the harmonic system.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum, auto
import numpy as np
from fractions import Fraction


# =============================================================================
# THE TETRACTYS
# =============================================================================

class DimensionalState(Enum):
    """Dimensional states of the Tetractys."""
    
    MONAD = 1   # 0D - Point
    DYAD = 2    # 1D - Line
    TRIAD = 3   # 2D - Surface
    TETRAD = 4  # 3D - Volume


@dataclass
class TetractysRow:
    """A row of the Tetractys."""
    
    level: int              # 1-4
    dimension: int          # 0-3
    count: int              # Number of points
    geometry: str           # Geometric name
    metaphysical: str       # Metaphysical meaning
    
    def __post_init__(self):
        assert 1 <= self.level <= 4
        assert self.dimension == self.level - 1
        assert self.count == self.level


class Tetractys:
    """
    The Sacred Tetractys.
    
        *           (1 - Monad)
       * *          (2 - Dyad)
      * * *         (3 - Triad)
     * * * *        (4 - Tetrad)
    
    Checksum: 1 + 2 + 3 + 4 = 10 = 1 + 0 = 1 (Return to Monad)
    
    This encodes the complete dimensional bootstrap sequence.
    """
    
    def __init__(self):
        self.rows = [
            TetractysRow(1, 0, 1, "Point", "Unity/Limit"),
            TetractysRow(2, 1, 2, "Line", "Flow/Direction"),
            TetractysRow(3, 2, 3, "Triangle", "Surface/Mean"),
            TetractysRow(4, 3, 4, "Tetrahedron", "Volume/Body"),
        ]
        
        self.total = sum(r.count for r in self.rows)
        assert self.total == 10
    
    def checksum(self) -> int:
        """
        Compute digital root checksum.
        
        10 → 1 + 0 = 1 (Return to Monad)
        """
        n = self.total
        while n >= 10:
            n = sum(int(d) for d in str(n))
        return n
    
    def dimensional_ladder(self) -> List[Tuple[int, str]]:
        """Return the dimensional progression."""
        return [(r.dimension, r.geometry) for r in self.rows]
    
    def point_count(self, level: int) -> int:
        """Get count of points at level."""
        if 1 <= level <= 4:
            return level
        return 0
    
    def cumulative_count(self, level: int) -> int:
        """Get cumulative point count up to level."""
        return sum(range(1, min(level, 4) + 1))
    
    def get_row(self, level: int) -> Optional[TetractysRow]:
        """Get row by level (1-4)."""
        if 1 <= level <= 4:
            return self.rows[level - 1]
        return None
    
    def triangular_number(self, n: int) -> int:
        """
        Compute nth triangular number.
        
        T_n = n(n+1)/2
        
        Tetractys = T_4 = 10
        """
        return n * (n + 1) // 2
    
    def inverse_triangular(self, t: int) -> Optional[int]:
        """
        Find n such that T_n = t.
        
        n = (-1 + √(1 + 8t)) / 2
        """
        discriminant = 1 + 8 * t
        sqrt_d = np.sqrt(discriminant)
        
        if sqrt_d != int(sqrt_d):
            return None
        
        n = (-1 + int(sqrt_d)) / 2
        if n == int(n) and n > 0:
            return int(n)
        return None
    
    def generate_ascii(self) -> str:
        """Generate ASCII representation."""
        lines = []
        for i, row in enumerate(self.rows):
            spaces = " " * (3 - i)
            points = " ".join(["*"] * row.count)
            lines.append(spaces + points)
        return "\n".join(lines)


# =============================================================================
# HARMONIC RATIOS
# =============================================================================

class HarmonicInterval(Enum):
    """Musical intervals from the Tetractys."""
    
    UNISON = (1, 1)          # 1:1 - Identity
    OCTAVE = (2, 1)          # 2:1 - Diapason
    FIFTH = (3, 2)           # 3:2 - Diapente
    FOURTH = (4, 3)          # 4:3 - Diatessaron
    TWELFTH = (3, 1)         # 3:1 - Octave + Fifth
    DOUBLE_OCTAVE = (4, 1)   # 4:1 - Two octaves
    TONE = (9, 8)            # 9:8 - Major second (derived)


@dataclass
class HarmonicRatio:
    """
    A harmonic ratio from the Pythagorean system.
    
    Superparticular ratios (n+1)/n are maximally consonant.
    """
    
    numerator: int
    denominator: int
    
    def __post_init__(self):
        # Reduce to lowest terms
        gcd = np.gcd(self.numerator, self.denominator)
        self.numerator //= gcd
        self.denominator //= gcd
    
    @property
    def fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)
    
    @property
    def value(self) -> float:
        return self.numerator / self.denominator
    
    @property
    def cents(self) -> float:
        """Convert to cents (1200 log₂ of ratio)."""
        return 1200 * np.log2(self.value)
    
    @property
    def is_superparticular(self) -> bool:
        """Check if (n+1)/n form."""
        return self.numerator == self.denominator + 1
    
    def __mul__(self, other: 'HarmonicRatio') -> 'HarmonicRatio':
        """Combine ratios (stacking intervals)."""
        return HarmonicRatio(
            self.numerator * other.numerator,
            self.denominator * other.denominator
        )
    
    def __truediv__(self, other: 'HarmonicRatio') -> 'HarmonicRatio':
        """Difference of intervals."""
        return HarmonicRatio(
            self.numerator * other.denominator,
            self.denominator * other.numerator
        )
    
    def inverse(self) -> 'HarmonicRatio':
        """Invert the ratio."""
        return HarmonicRatio(self.denominator, self.numerator)


class HarmonicSystem:
    """
    The Pythagorean Harmonic System.
    
    All consonant intervals derived from ratios of {1, 2, 3, 4}.
    
    Harmonic Instruction Set:
    - 1:1 Unison   - Identity()    - No data transfer
    - 2:1 Octave   - Loop(x2)      - Recursion boundary
    - 3:2 Fifth    - Generate()    - Active driver
    - 4:3 Fourth   - Frame()       - Structural anchor
    """
    
    def __init__(self):
        # Primary intervals
        self.unison = HarmonicRatio(1, 1)
        self.octave = HarmonicRatio(2, 1)
        self.fifth = HarmonicRatio(3, 2)
        self.fourth = HarmonicRatio(4, 3)
        
        # Derived intervals
        self.tone = self.fifth / self.fourth  # 9:8
        self.semitone = self._compute_limma()  # 256:243
    
    def _compute_limma(self) -> HarmonicRatio:
        """
        Compute Pythagorean limma (semitone).
        
        Limma = Fourth - 2×Tone = 256:243
        """
        two_tones = self.tone * self.tone
        return self.fourth / two_tones
    
    def stack_fifths(self, n: int) -> HarmonicRatio:
        """Stack n fifths."""
        result = self.unison
        for _ in range(n):
            result = result * self.fifth
        return result
    
    def reduce_to_octave(self, ratio: HarmonicRatio) -> HarmonicRatio:
        """Reduce ratio to within one octave."""
        value = ratio.value
        while value >= 2.0:
            value /= 2
        while value < 1.0:
            value *= 2
        
        # Find close rational approximation
        frac = Fraction(value).limit_denominator(1000)
        return HarmonicRatio(frac.numerator, frac.denominator)
    
    def pythagorean_scale(self) -> List[Tuple[str, HarmonicRatio]]:
        """
        Generate Pythagorean scale.
        
        Uses circle of fifths reduced to octave.
        """
        notes = ["C", "D", "E", "F", "G", "A", "B"]
        scale = []
        
        # C = 1:1
        scale.append(("C", self.unison))
        
        # D = Two fifths up = 9:8
        scale.append(("D", self.tone))
        
        # E = Four fifths up = 81:64
        e_ratio = self.tone * self.tone
        scale.append(("E", e_ratio))
        
        # F = One fourth up = 4:3
        scale.append(("F", self.fourth))
        
        # G = One fifth up = 3:2
        scale.append(("G", self.fifth))
        
        # A = Three fifths up = 27:16
        a_ratio = self.fifth * self.tone
        scale.append(("A", a_ratio))
        
        # B = Five fifths up = 243:128
        b_ratio = a_ratio * self.tone
        scale.append(("B", b_ratio))
        
        return scale
    
    def consonance_ranking(self) -> List[Tuple[str, HarmonicRatio, float]]:
        """
        Rank intervals by consonance.
        
        Simpler ratios (smaller numbers) = more consonant.
        """
        intervals = [
            ("Unison", self.unison),
            ("Octave", self.octave),
            ("Fifth", self.fifth),
            ("Fourth", self.fourth),
            ("Tone", self.tone),
        ]
        
        # Consonance score: 1/(n+d) where n,d are numerator, denominator
        ranked = []
        for name, ratio in intervals:
            score = 1 / (ratio.numerator + ratio.denominator)
            ranked.append((name, ratio, score))
        
        return sorted(ranked, key=lambda x: -x[2])


# =============================================================================
# THE PYTHAGOREAN COMMA
# =============================================================================

class PythagoreanComma:
    """
    The Pythagorean Comma: 12 fifths ≠ 7 octaves.
    
    (3/2)^12 / 2^7 = 531441/524288 ≈ 1.0136433
    
    This is approximately 23.46 cents.
    
    The comma is not an "error" but a SECURITY FEATURE:
    It prevents infinite precision attacks and ensures
    the system remains bounded and computable.
    """
    
    def __init__(self):
        # 12 fifths
        self.twelve_fifths = Fraction(3, 2) ** 12
        
        # 7 octaves
        self.seven_octaves = Fraction(2, 1) ** 7
        
        # The comma
        self.comma = self.twelve_fifths / self.seven_octaves
    
    @property
    def ratio(self) -> Fraction:
        """The comma as a fraction: 531441/524288."""
        return self.comma
    
    @property
    def value(self) -> float:
        """The comma as a decimal."""
        return float(self.comma)
    
    @property
    def cents(self) -> float:
        """The comma in cents."""
        return 1200 * np.log2(self.value)
    
    def verify_inequality(self) -> bool:
        """Verify 12 fifths ≠ 7 octaves."""
        return self.twelve_fifths != self.seven_octaves
    
    def spiral_of_fifths(self, n: int) -> List[Tuple[int, float]]:
        """
        Trace the spiral of fifths.
        
        Shows divergence from closed circle.
        """
        spiral = []
        position = Fraction(1, 1)
        
        for i in range(n):
            # Stack another fifth
            position = position * Fraction(3, 2)
            
            # Reduce to octave
            while position >= 2:
                position = position / 2
            
            # Compute deviation from nearest octave
            deviation_cents = 1200 * np.log2(float(position))
            spiral.append((i + 1, deviation_cents))
        
        return spiral
    
    def schisma(self) -> Fraction:
        """
        The schisma: syntonic comma / Pythagorean comma difference.
        
        Approximately 1.95 cents.
        """
        syntonic = Fraction(81, 80)
        return self.comma / syntonic


# =============================================================================
# LIMITER/UNLIMITED BINARY
# =============================================================================

class LimiterUnlimited:
    """
    The Pythagorean Limiter/Unlimited duality.
    
    - Unlimited (ἄπειρον): Continuous, unbounded, potential
    - Limiter (πέρας): Discrete, bounded, actual
    
    All things are harmonies of these opposites.
    """
    
    class Unlimited:
        """The infinite, continuous substrate."""
        
        def __init__(self, extent: float = float('inf')):
            self.extent = extent
            self.divisible = True
            self.continuous = True
        
        def sample(self, n: int) -> np.ndarray:
            """Sample n points from unlimited continuum."""
            if np.isinf(self.extent):
                return np.random.randn(n)
            return np.random.uniform(-self.extent, self.extent, n)
    
    class Limiter:
        """The finite, discrete boundary."""
        
        def __init__(self, ratio: Tuple[int, int] = (1, 1)):
            self.ratio = ratio
            self.discrete = True
            self.bounded = True
        
        def apply(self, unlimited_value: float) -> float:
            """Apply limit to unlimited value."""
            n, d = self.ratio
            return unlimited_value * (n / d)
        
        def quantize(self, value: float, levels: int = 12) -> int:
            """Quantize continuous to discrete."""
            return int(value * levels) % levels
    
    @staticmethod
    def harmonize(unlimited: 'LimiterUnlimited.Unlimited',
                  limiter: 'LimiterUnlimited.Limiter',
                  n_samples: int = 100) -> np.ndarray:
        """
        Create harmony from unlimited + limiter.
        
        This is the fundamental creative act.
        """
        raw = unlimited.sample(n_samples)
        return np.array([limiter.apply(x) for x in raw])


# =============================================================================
# VALIDATION
# =============================================================================

def validate_pythagorean() -> bool:
    """Validate Pythagorean module."""
    
    # Test Tetractys
    tetractys = Tetractys()
    
    assert tetractys.total == 10
    assert tetractys.checksum() == 1
    
    ladder = tetractys.dimensional_ladder()
    assert len(ladder) == 4
    assert ladder[0] == (0, "Point")
    assert ladder[3] == (3, "Tetrahedron")
    
    # Triangular numbers
    assert tetractys.triangular_number(4) == 10
    assert tetractys.inverse_triangular(10) == 4
    
    # Test HarmonicRatio
    fifth = HarmonicRatio(3, 2)
    fourth = HarmonicRatio(4, 3)
    
    assert fifth.is_superparticular
    assert fourth.is_superparticular
    
    # Fifth + Fourth = Octave
    octave = fifth * fourth
    assert octave.value == 2.0
    
    # Fifth - Fourth = Tone
    tone = fifth / fourth
    assert tone.numerator == 9 and tone.denominator == 8
    
    # Test HarmonicSystem
    system = HarmonicSystem()
    
    scale = system.pythagorean_scale()
    assert len(scale) == 7
    assert scale[0][0] == "C"
    
    ranking = system.consonance_ranking()
    assert ranking[0][0] == "Unison"  # Most consonant
    
    # Test PythagoreanComma
    comma = PythagoreanComma()
    
    assert comma.verify_inequality()
    assert comma.ratio == Fraction(531441, 524288)
    assert abs(comma.cents - 23.46) < 0.1
    
    spiral = comma.spiral_of_fifths(12)
    assert len(spiral) == 12
    
    # Test LimiterUnlimited
    unlimited = LimiterUnlimited.Unlimited()
    limiter = LimiterUnlimited.Limiter((3, 2))
    
    harmony = LimiterUnlimited.harmonize(unlimited, limiter, 100)
    assert len(harmony) == 100
    
    return True


if __name__ == "__main__":
    print("Validating Pythagorean Engine...")
    assert validate_pythagorean()
    print("✓ Pythagorean Engine validated")
    
    print("\n--- Tetractys ---")
    t = Tetractys()
    print(t.generate_ascii())
    print(f"Total: {t.total}, Checksum: {t.checksum()}")
    
    print("\n--- Pythagorean Scale ---")
    system = HarmonicSystem()
    for name, ratio in system.pythagorean_scale():
        print(f"  {name}: {ratio.numerator}/{ratio.denominator} = {ratio.cents:.1f} cents")
    
    print("\n--- Pythagorean Comma ---")
    comma = PythagoreanComma()
    print(f"  Ratio: {comma.ratio}")
    print(f"  Cents: {comma.cents:.2f}")
