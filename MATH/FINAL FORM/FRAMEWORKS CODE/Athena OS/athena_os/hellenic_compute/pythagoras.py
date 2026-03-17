"""
ATHENA OS - HELLENIC COMPUTATION FRAMEWORK
==========================================
Part II: The Dimensional Engine (Pythagoras)

THE TETRACTYS:
    The Pythagorean Tetractys is the set {1, 2, 3, 4} with sum 10.
    
    It generates:
    - Dimensional structure: 0D (point) + 1D (line) + 2D (plane) + 3D (solid) = 10
    - Harmonic ratios: 2:1, 3:2, 4:3, etc.
    - The complete number system

THE HARMONIC RATIOS:
    Consonant intervals from first four integers:
    - 2:1 = Octave (diapason)
    - 3:2 = Fifth (diapente)
    - 4:3 = Fourth (diatessaron)
    - 9:8 = Tone (whole step)

THE LIMITER/UNLIMITED BINARY:
    - Limit (Peras): Quantization, form, definition
    - Unlimited (Apeiron): Continuum, potential, indefinite
    
    The cosmos is Limit applied to Unlimited.

THE PYTHAGOREAN COMMA:
    The gap between 12 fifths and 7 octaves:
    (3/2)^12 / 2^7 ≈ 1.0136...
    
    This irreducible remainder shows that harmonic space
    cannot be perfectly closed—a fundamental asymmetry.

SOURCES:
    - THE_HELLENIC_COMPUTATION_FRAMEWORK.docx Part II
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import numpy as np
import math
from fractions import Fraction

from .foundation import StateVector, Klein4Op


# =============================================================================
# THE TETRACTYS
# =============================================================================

class Tetractys:
    """
    The Pythagorean Tetractys: {1, 2, 3, 4}.
    
    The source of dimensional structure and harmonic ratios.
    """
    
    # The sacred numbers
    NUMBERS = (1, 2, 3, 4)
    
    # Sum = 10 (the Decad)
    SUM = 10
    
    @classmethod
    def dimensional_structure(cls) -> Dict[int, str]:
        """
        Map Tetractys to dimensional structure.
        
        1 → 0D (point)
        2 → 1D (line, 2 points)
        3 → 2D (plane, 3 points)
        4 → 3D (solid, 4 points)
        """
        return {
            1: "0D: Point (monad)",
            2: "1D: Line (dyad)",
            3: "2D: Plane (triad)",
            4: "3D: Solid (tetrad)",
        }
    
    @classmethod
    def generate_dimensions(cls) -> List[int]:
        """
        Generate dimension count from Tetractys.
        
        n elements define an (n-1)-dimensional simplex.
        """
        return [n - 1 for n in cls.NUMBERS]
    
    @classmethod
    def triangular_representation(cls) -> List[List[int]]:
        """
        Get the triangular arrangement:
        
            1
           2 3
          4 5 6
         7 8 9 10
        """
        result = []
        current = 1
        for row in range(1, 5):
            row_items = []
            for _ in range(row):
                row_items.append(current)
                current += 1
            result.append(row_items)
        return result
    
    @classmethod
    def cosmological_correspondences(cls) -> Dict[int, str]:
        """
        Pythagorean cosmological correspondences.
        """
        return {
            1: "The One (Monad): Source, Unity, Identity",
            2: "The Dyad: Division, Polarity, Relation",
            3: "The Triad: Harmony, Mediation, Balance",
            4: "The Tetrad: Completion, Manifestation, Structure",
        }
    
    @classmethod
    def is_sacred(cls, n: int) -> bool:
        """Check if number is in Tetractys."""
        return n in cls.NUMBERS
    
    @classmethod
    def digital_root(cls, n: int) -> int:
        """
        Reduce n to single digit (theosophic reduction).
        
        Pythagorean digit sum.
        """
        while n > 9:
            n = sum(int(d) for d in str(n))
        return n


# =============================================================================
# HARMONIC RATIOS
# =============================================================================

class HarmonicInterval(Enum):
    """
    The fundamental harmonic intervals from the Tetractys.
    """
    
    UNISON = (1, 1)       # 1:1
    OCTAVE = (2, 1)       # 2:1 (diapason)
    FIFTH = (3, 2)        # 3:2 (diapente)
    FOURTH = (4, 3)       # 4:3 (diatessaron)
    TONE = (9, 8)         # 9:8 (whole step)
    SEMITONE = (256, 243) # Pythagorean semitone
    DOUBLE_OCTAVE = (4, 1)  # 4:1
    TWELFTH = (3, 1)      # 3:1 (octave + fifth)
    
    @property
    def ratio(self) -> Fraction:
        """Get ratio as Fraction."""
        return Fraction(self.value[0], self.value[1])
    
    @property
    def cents(self) -> float:
        """Get interval size in cents (1200 cents = 1 octave)."""
        return 1200 * math.log2(self.ratio)
    
    @property
    def frequency_multiplier(self) -> float:
        """Get frequency multiplier."""
        return float(self.ratio)
    
    def is_superparticular(self) -> bool:
        """
        Check if ratio is (n+1)/n form.
        
        Superparticular ratios are maximally consonant.
        """
        n, d = self.value
        return n == d + 1
    
    @classmethod
    def from_tetractys(cls) -> List[HarmonicInterval]:
        """Get all intervals derivable from {1,2,3,4}."""
        return [
            cls.UNISON, cls.OCTAVE, cls.FIFTH, 
            cls.FOURTH, cls.DOUBLE_OCTAVE, cls.TWELFTH
        ]


@dataclass
class HarmonicRatioSystem:
    """
    Complete system of harmonic ratios.
    """
    
    base_frequency: float = 256.0  # Reference frequency (Hz)
    
    def frequency_at_ratio(self, ratio: Fraction) -> float:
        """Get frequency at given ratio from base."""
        return self.base_frequency * float(ratio)
    
    def interval_between(self, f1: float, f2: float) -> Fraction:
        """Get ratio between two frequencies."""
        ratio = f2 / f1
        return Fraction(ratio).limit_denominator(1000)
    
    def build_scale(self, n_octaves: int = 1) -> List[Tuple[str, float]]:
        """
        Build Pythagorean diatonic scale.
        
        Uses circle of fifths: C-G-D-A-E-B-F#...
        """
        scale = []
        notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        
        # Generate frequencies
        # C (base), D (+2 fifths - octave), E (+4 fifths - 2 octaves), etc.
        fifth = Fraction(3, 2)
        octave = Fraction(2, 1)
        
        for i, note in enumerate(notes):
            # Number of fifths from C
            fifths_map = {
                'C': 0, 'G': 1, 'D': 2, 'A': 3, 
                'E': 4, 'B': 5, 'F': -1
            }
            n_fifths = fifths_map[note]
            
            # Calculate ratio
            if n_fifths >= 0:
                ratio = (fifth ** n_fifths)
            else:
                ratio = octave / fifth  # F is fourth from C
            
            # Reduce to within octave
            while ratio >= 2:
                ratio = ratio / 2
            while ratio < 1:
                ratio = ratio * 2
            
            freq = self.base_frequency * float(ratio)
            scale.append((note, freq))
        
        return sorted(scale, key=lambda x: x[1])
    
    def pythagorean_comma(self) -> Fraction:
        """
        Calculate the Pythagorean comma.
        
        (3/2)^12 / 2^7 ≈ 531441/524288 ≈ 1.0136
        """
        return Fraction(3, 2) ** 12 / Fraction(2, 1) ** 7
    
    def comma_cents(self) -> float:
        """Pythagorean comma in cents."""
        return 1200 * math.log2(float(self.pythagorean_comma()))


# =============================================================================
# LIMITER / UNLIMITED
# =============================================================================

class LimitType(Enum):
    """Types of Pythagorean limits."""
    
    PERAS = "limit"        # Definite, bounded, structured
    APEIRON = "unlimited"  # Indefinite, unbounded, potential


@dataclass
class LimiterUnlimited:
    """
    The Pythagorean binary: Limit (Peras) and Unlimited (Apeiron).
    
    The cosmos is Limit applied to Unlimited—form imposed on formlessness.
    """
    
    def __init__(self):
        # Table of opposites (from Aristotle's report on Pythagoreans)
        self.opposites = [
            ("Limit", "Unlimited"),
            ("Odd", "Even"),
            ("One", "Many"),
            ("Right", "Left"),
            ("Male", "Female"),
            ("Rest", "Motion"),
            ("Straight", "Curved"),
            ("Light", "Darkness"),
            ("Good", "Bad"),
            ("Square", "Oblong"),
        ]
    
    def is_limited(self, n: int) -> bool:
        """
        Check if number is 'limited' (odd).
        
        Odd numbers are Limit; even numbers are Unlimited.
        """
        return n % 2 == 1
    
    def apply_limit(self, unlimited: float, 
                   limit_value: int) -> float:
        """
        Quantize unlimited value to limited discrete value.
        
        This is the fundamental operation of cosmic creation.
        """
        return round(unlimited * limit_value) / limit_value
    
    def generate_number(self, position: int) -> int:
        """
        Generate natural number by applying Limit.
        
        The Limit (1) quantizes the Indefinite Dyad.
        """
        # The Dyad produces the "Great and Small"
        # The One limits it to produce integers
        return position  # Simplified
    
    def mean_types(self, a: float, b: float) -> Dict[str, float]:
        """
        Calculate the three Pythagorean means.
        
        These are the fundamental operations of mediation.
        """
        return {
            "arithmetic": (a + b) / 2,
            "geometric": math.sqrt(a * b),
            "harmonic": 2 * a * b / (a + b) if (a + b) != 0 else 0,
        }


# =============================================================================
# DIMENSIONAL ENGINE
# =============================================================================

class DimensionalEngine:
    """
    Engine for generating dimensional structure from Tetractys.
    """
    
    def __init__(self):
        self.tetractys = Tetractys()
        self.harmonics = HarmonicRatioSystem()
        self.limiter = LimiterUnlimited()
    
    def generate_simplex(self, n: int) -> Dict[str, Any]:
        """
        Generate n-dimensional simplex.
        
        n+1 points define an n-dimensional simplex.
        """
        return {
            "dimension": n,
            "vertices": n + 1,
            "edges": (n + 1) * n // 2,
            "faces": self._binomial(n + 1, 3) if n >= 2 else 0,
            "cells": self._binomial(n + 1, 4) if n >= 3 else 0,
        }
    
    def _binomial(self, n: int, k: int) -> int:
        """Binomial coefficient."""
        if k > n or k < 0:
            return 0
        return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))
    
    def musical_space(self, base: float = 256.0) -> Dict[str, float]:
        """
        Generate the musical space from harmonics.
        """
        scale = self.harmonics.build_scale()
        return {note: freq for note, freq in scale}
    
    def cosmic_structure(self) -> Dict[str, str]:
        """
        Generate cosmic structure correspondences.
        """
        return {
            "1 (Monad)": "Fire - The Central Fire (Hestia)",
            "2 (Dyad)": "Earth-Counter-Earth pair",
            "3 (Triad)": "Moon-Sun-Venus triangle",
            "4 (Tetrad)": "Mercury-Mars-Jupiter-Saturn",
            "10 (Decad)": "Complete Cosmos (10 celestial bodies)",
        }
    
    def gnomon_sequence(self, n: int) -> List[int]:
        """
        Generate gnomon numbers.
        
        Gnomons are the L-shaped pieces added to squares.
        The nth gnomon is 2n + 1 (odd numbers).
        """
        return [2 * i + 1 for i in range(n)]
    
    def figurate_number(self, n: int, shape: str) -> int:
        """
        Generate figurate numbers.
        
        shape: "triangular", "square", "pentagonal", etc.
        """
        if shape == "triangular":
            return n * (n + 1) // 2
        elif shape == "square":
            return n * n
        elif shape == "pentagonal":
            return n * (3 * n - 1) // 2
        elif shape == "hexagonal":
            return n * (2 * n - 1)
        return 0


# =============================================================================
# PYTHAGOREAN TUNING SYSTEM
# =============================================================================

class PythagoreanTuning:
    """
    Complete Pythagorean tuning system.
    """
    
    # The fundamental generators
    FIFTH = Fraction(3, 2)
    FOURTH = Fraction(4, 3)
    OCTAVE = Fraction(2, 1)
    TONE = Fraction(9, 8)
    
    def __init__(self, base: float = 256.0):
        self.base = base
        self._build_circle_of_fifths()
    
    def _build_circle_of_fifths(self) -> None:
        """Build the circle of fifths."""
        self.circle = {}
        note_names = ['F', 'C', 'G', 'D', 'A', 'E', 'B']
        
        # Start from F (which is a fourth below C)
        ratio = self.FOURTH  # F is 4/3 above C, or C is 3/2 above F
        ratio = self.OCTAVE / self.FIFTH  # F relative to C
        
        # Build from C
        current = Fraction(1, 1)
        for i, name in enumerate(note_names):
            if i == 0:  # F
                self.circle['F'] = self.OCTAVE / self.FIFTH
            else:
                self.circle[name] = current
                current = current * self.FIFTH
                # Reduce to within octave
                while current >= 2:
                    current = current / 2
    
    def get_frequency(self, note: str) -> float:
        """Get frequency for a note."""
        ratio = self.circle.get(note, Fraction(1, 1))
        return self.base * float(ratio)
    
    def interval_sequence(self, intervals: List[str]) -> float:
        """
        Calculate compound interval from sequence.
        
        intervals: List of interval names
        """
        ratio = Fraction(1, 1)
        for interval in intervals:
            if interval == "fifth":
                ratio *= self.FIFTH
            elif interval == "fourth":
                ratio *= self.FOURTH
            elif interval == "octave":
                ratio *= self.OCTAVE
            elif interval == "tone":
                ratio *= self.TONE
        return float(ratio)
    
    def spiral_of_fifths(self, n: int) -> List[Tuple[int, Fraction]]:
        """
        Generate n steps of the spiral of fifths.
        
        Returns (position, ratio) pairs.
        """
        result = []
        ratio = Fraction(1, 1)
        for i in range(n):
            result.append((i, ratio))
            ratio = ratio * self.FIFTH
        return result


# =============================================================================
# VALIDATION
# =============================================================================

def validate_pythagoras() -> bool:
    """Validate Pythagorean module."""
    
    # Test Tetractys
    assert sum(Tetractys.NUMBERS) == 10
    assert Tetractys.is_sacred(3)
    assert not Tetractys.is_sacred(5)
    assert Tetractys.digital_root(19) == 1
    
    dims = Tetractys.generate_dimensions()
    assert dims == [0, 1, 2, 3]
    
    # Test HarmonicInterval
    fifth = HarmonicInterval.FIFTH
    assert fifth.ratio == Fraction(3, 2)
    assert fifth.is_superparticular()
    assert 700 < fifth.cents < 710  # ~702 cents
    
    # Test HarmonicRatioSystem
    harmonics = HarmonicRatioSystem()
    comma = harmonics.pythagorean_comma()
    assert 1.01 < float(comma) < 1.02
    
    scale = harmonics.build_scale()
    assert len(scale) == 7
    
    # Test LimiterUnlimited
    lu = LimiterUnlimited()
    assert lu.is_limited(1)
    assert lu.is_limited(3)
    assert not lu.is_limited(2)
    
    means = lu.mean_types(4, 9)
    assert means["arithmetic"] == 6.5
    assert means["geometric"] == 6.0
    assert abs(means["harmonic"] - 5.538) < 0.01
    
    # Test DimensionalEngine
    engine = DimensionalEngine()
    simplex = engine.generate_simplex(3)
    assert simplex["vertices"] == 4
    assert simplex["edges"] == 6
    
    gnomons = engine.gnomon_sequence(5)
    assert gnomons == [1, 3, 5, 7, 9]
    
    # Test PythagoreanTuning
    tuning = PythagoreanTuning()
    spiral = tuning.spiral_of_fifths(12)
    assert len(spiral) == 12
    
    return True


if __name__ == "__main__":
    print("Validating Pythagorean Module...")
    assert validate_pythagoras()
    print("✓ Pythagorean module validated")
    
    # Demo
    print("\n--- Pythagorean Dimensional Engine Demo ---")
    
    print("\n1. The Tetractys:")
    print(f"   Numbers: {Tetractys.NUMBERS}")
    print(f"   Sum: {Tetractys.SUM}")
    for n, desc in Tetractys.dimensional_structure().items():
        print(f"   {n} → {desc}")
    
    print("\n2. Harmonic Intervals:")
    for interval in HarmonicInterval.from_tetractys():
        print(f"   {interval.name}: {interval.ratio} = {interval.cents:.1f} cents")
    
    print("\n3. Pythagorean Scale:")
    harmonics = HarmonicRatioSystem(base_frequency=256)
    scale = harmonics.build_scale()
    for note, freq in scale:
        print(f"   {note}: {freq:.2f} Hz")
    
    comma = harmonics.pythagorean_comma()
    print(f"\n   Pythagorean Comma: {comma} ≈ {float(comma):.6f}")
    print(f"   Comma in cents: {harmonics.comma_cents():.2f}")
    
    print("\n4. Figurate Numbers:")
    engine = DimensionalEngine()
    for shape in ["triangular", "square", "pentagonal"]:
        nums = [engine.figurate_number(n, shape) for n in range(1, 8)]
        print(f"   {shape.capitalize()}: {nums}")
    
    print("\n5. Gnomon Sequence (Odd Numbers):")
    gnomons = engine.gnomon_sequence(10)
    print(f"   {gnomons}")
    print(f"   Sum: {sum(gnomons)} = 10² (perfect square)")
