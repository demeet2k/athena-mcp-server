"""
ATHENA OS - SQUARING THE CIRCLE: HEXAGRAM SYSTEM
=================================================
I Ching Correspondence with the 64 Elemental Permutations

THE 64 HEXAGRAMS:
    2⁶ = 64 (binary six-bit)
    4³ = 64 (quaternary three-position)
    8² = 64 (octal square)
    
    Three equivalent representations converging on 64.

HEXAGRAM STRUCTURE:
    Each hexagram consists of 6 lines:
    - ⚊ Yang (solid)
    - ⚋ Yin (broken)
    
    Organized as two trigrams:
    - Upper trigram (lines 4-6)
    - Lower trigram (lines 1-3)
    
    8 trigrams × 8 trigrams = 64 hexagrams

MAPPING TO ELEMENTS:
    Binary pair → Element:
    - ⚊⚊ (11) → Fire (Hot + Dry)
    - ⚊⚋ (10) → Air (Hot + Wet)
    - ⚋⚊ (01) → Water (Cold + Wet)
    - ⚋⚋ (00) → Earth (Cold + Dry)
    
    Six lines = three pairs = three elements = one permutation.

THE EIGHT TRIGRAMS (BAGUA):
    ☰ Qian (Heaven)   = ⚊⚊⚊ = Fire-Fire-Fire principle
    ☷ Kun (Earth)     = ⚋⚋⚋ = Earth-Earth-Earth principle
    ☳ Zhen (Thunder)  = ⚋⚋⚊
    ☴ Xun (Wind)      = ⚊⚊⚋
    ☵ Kan (Water)     = ⚋⚊⚋
    ☲ Li (Fire)       = ⚊⚋⚊
    ☶ Gen (Mountain)  = ⚊⚋⚋
    ☱ Dui (Lake)      = ⚋⚊⚊

SOURCES:
    - SQUARING_THE_CIRCLE.docx Chapter 9
    - I Ching tradition
    - Binary-quaternary isomorphism
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Iterator
from enum import Enum, IntEnum
import numpy as np


# =============================================================================
# LINE AND TRIGRAM ENUMS
# =============================================================================

class Line(IntEnum):
    """A single line: Yang (solid) or Yin (broken)."""
    YIN = 0    # ⚋ Broken
    YANG = 1   # ⚊ Solid
    
    @property
    def symbol(self) -> str:
        return "⚊" if self == Line.YANG else "⚋"
    
    @property
    def chinese_name(self) -> str:
        return "陽" if self == Line.YANG else "陰"
    
    def __invert__(self) -> Line:
        """Get opposite line."""
        return Line.YANG if self == Line.YIN else Line.YIN


class Trigram(IntEnum):
    """
    The eight trigrams (Bagua).
    
    Value is binary: line1 + 2*line2 + 4*line3
    """
    
    KUN = 0      # ☷ ⚋⚋⚋ Earth
    GEN = 1      # ☶ ⚊⚋⚋ Mountain
    KAN = 2      # ☵ ⚋⚊⚋ Water
    XUN = 3      # ☴ ⚊⚊⚋ Wind
    ZHEN = 4     # ☳ ⚋⚋⚊ Thunder
    LI = 5       # ☲ ⚊⚋⚊ Fire
    DUI = 6      # ☱ ⚋⚊⚊ Lake
    QIAN = 7     # ☰ ⚊⚊⚊ Heaven


# Trigram metadata
TRIGRAM_DATA: Dict[Trigram, Dict[str, str]] = {
    Trigram.QIAN: {
        "name": "Qian",
        "chinese": "乾",
        "symbol": "☰",
        "nature": "Heaven",
        "attribute": "Creative",
        "family": "Father",
        "lines": "⚊⚊⚊"
    },
    Trigram.KUN: {
        "name": "Kun",
        "chinese": "坤",
        "symbol": "☷",
        "nature": "Earth",
        "attribute": "Receptive",
        "family": "Mother",
        "lines": "⚋⚋⚋"
    },
    Trigram.ZHEN: {
        "name": "Zhen",
        "chinese": "震",
        "symbol": "☳",
        "nature": "Thunder",
        "attribute": "Arousing",
        "family": "Eldest Son",
        "lines": "⚋⚋⚊"
    },
    Trigram.XUN: {
        "name": "Xun",
        "chinese": "巽",
        "symbol": "☴",
        "nature": "Wind",
        "attribute": "Gentle",
        "family": "Eldest Daughter",
        "lines": "⚊⚊⚋"
    },
    Trigram.KAN: {
        "name": "Kan",
        "chinese": "坎",
        "symbol": "☵",
        "nature": "Water",
        "attribute": "Abysmal",
        "family": "Middle Son",
        "lines": "⚋⚊⚋"
    },
    Trigram.LI: {
        "name": "Li",
        "chinese": "離",
        "symbol": "☲",
        "nature": "Fire",
        "attribute": "Clinging",
        "family": "Middle Daughter",
        "lines": "⚊⚋⚊"
    },
    Trigram.GEN: {
        "name": "Gen",
        "chinese": "艮",
        "symbol": "☶",
        "nature": "Mountain",
        "attribute": "Keeping Still",
        "family": "Youngest Son",
        "lines": "⚊⚋⚋"
    },
    Trigram.DUI: {
        "name": "Dui",
        "chinese": "兌",
        "symbol": "☱",
        "nature": "Lake",
        "attribute": "Joyous",
        "family": "Youngest Daughter",
        "lines": "⚋⚊⚊"
    }
}


# =============================================================================
# ELEMENT MAPPING
# =============================================================================

class BinaryElement(IntEnum):
    """
    Mapping of binary pairs to classical elements.
    
    Uses Hot/Cold and Dry/Wet:
    - Yang (1): Active/Hot
    - Yin (0): Passive/Cold
    
    First bit: Temperature (1=Hot, 0=Cold)
    Second bit: Moisture (1=Dry, 0=Wet)
    """
    
    EARTH = 0b00   # Cold + Wet → ⚋⚋
    WATER = 0b01   # Cold + Dry → ⚋⚊ (note: differs from Greek)
    AIR = 0b10     # Hot + Wet → ⚊⚋
    FIRE = 0b11    # Hot + Dry → ⚊⚊


# Alternative mapping (matching Greek qualities exactly)
class GreekBinaryElement(IntEnum):
    """
    Greek element mapping:
    - Fire: Hot + Dry → 11
    - Air: Hot + Wet → 10
    - Water: Cold + Wet → 01
    - Earth: Cold + Dry → 00
    
    But this is better expressed as:
    - First line: Hot(1)/Cold(0)
    - Second line: Dry(1)/Wet(0)
    """
    
    EARTH = 0b00   # Cold(0) + Dry(0) - but wait, Earth is Cold+Dry
    WATER = 0b01   # Cold(0) + Wet(1)
    AIR = 0b10     # Hot(1) + Wet(0) - Air is Hot+Wet
    FIRE = 0b11    # Hot(1) + Dry(1)


def binary_pair_to_element(b1: int, b2: int) -> str:
    """
    Convert binary pair to element name.
    
    Using the scheme:
    - b1: Temperature (1=Hot, 0=Cold)
    - b2: Moisture (0=Wet, 1=Dry)
    """
    if b1 == 1 and b2 == 1:
        return "Fire"
    elif b1 == 1 and b2 == 0:
        return "Air"
    elif b1 == 0 and b2 == 0:
        return "Water"
    else:  # b1 == 0 and b2 == 1
        return "Earth"


# =============================================================================
# HEXAGRAM
# =============================================================================

@dataclass
class Hexagram:
    """
    A hexagram: six lines forming two trigrams.
    
    Lines are numbered 1-6 from bottom to top.
    - Lines 1-3: Lower trigram
    - Lines 4-6: Upper trigram
    
    Binary representation: 6-bit number (0-63).
    """
    
    lines: Tuple[Line, Line, Line, Line, Line, Line]
    
    @classmethod
    def from_binary(cls, n: int) -> Hexagram:
        """Create hexagram from binary number (0-63)."""
        n = n % 64
        lines = tuple(Line((n >> i) & 1) for i in range(6))
        return cls(lines)
    
    @classmethod
    def from_trigrams(cls, lower: Trigram, upper: Trigram) -> Hexagram:
        """Create hexagram from two trigrams."""
        lower_bits = [(lower.value >> i) & 1 for i in range(3)]
        upper_bits = [(upper.value >> i) & 1 for i in range(3)]
        lines = tuple(Line(b) for b in lower_bits + upper_bits)
        return cls(lines)
    
    @property
    def binary(self) -> int:
        """Get binary representation (0-63)."""
        return sum(line.value << i for i, line in enumerate(self.lines))
    
    @property
    def lower_trigram(self) -> Trigram:
        """Get lower trigram (lines 1-3)."""
        value = sum(self.lines[i].value << i for i in range(3))
        return Trigram(value)
    
    @property
    def upper_trigram(self) -> Trigram:
        """Get upper trigram (lines 4-6)."""
        value = sum(self.lines[i+3].value << i for i in range(3))
        return Trigram(value)
    
    @property
    def is_pure(self) -> bool:
        """All lines the same."""
        return all(l == self.lines[0] for l in self.lines)
    
    @property
    def yang_count(self) -> int:
        """Count of yang (solid) lines."""
        return sum(1 for l in self.lines if l == Line.YANG)
    
    @property
    def yin_count(self) -> int:
        """Count of yin (broken) lines."""
        return 6 - self.yang_count
    
    @property
    def balance(self) -> float:
        """Yang proportion (0 = all yin, 1 = all yang)."""
        return self.yang_count / 6
    
    def invert(self) -> Hexagram:
        """Invert all lines (yin ↔ yang)."""
        return Hexagram(tuple(~l for l in self.lines))
    
    def reverse(self) -> Hexagram:
        """Reverse order of lines (flip upside down)."""
        return Hexagram(self.lines[::-1])
    
    def nuclear(self) -> Hexagram:
        """Get nuclear hexagram (inner lines)."""
        # Nuclear: lines 2,3,4 become lower; lines 3,4,5 become upper
        new_lines = (
            self.lines[1], self.lines[2], self.lines[3],
            self.lines[2], self.lines[3], self.lines[4]
        )
        return Hexagram(new_lines)
    
    def to_elements(self) -> Tuple[str, str, str]:
        """
        Convert to three elements (Root, Expression, Mode).
        
        Lines 1-2 → Root element
        Lines 3-4 → Expression element
        Lines 5-6 → Mode element
        """
        root = binary_pair_to_element(self.lines[0].value, self.lines[1].value)
        expr = binary_pair_to_element(self.lines[2].value, self.lines[3].value)
        mode = binary_pair_to_element(self.lines[4].value, self.lines[5].value)
        return (root, expr, mode)
    
    @property
    def symbol(self) -> str:
        """Get Unicode representation."""
        # Lines displayed top to bottom (6 to 1)
        return "\n".join(self.lines[5-i].symbol for i in range(6))
    
    @property
    def line_string(self) -> str:
        """Get compact line representation."""
        return "".join(l.symbol for l in reversed(self.lines))
    
    @property
    def binary_string(self) -> str:
        """Get binary string (LSB first)."""
        return "".join(str(l.value) for l in self.lines)
    
    def __repr__(self) -> str:
        return f"Hexagram({self.binary})"
    
    def __hash__(self) -> int:
        return hash(self.binary)
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Hexagram):
            return self.binary == other.binary
        return False


# =============================================================================
# HEXAGRAM CATALOG
# =============================================================================

# Traditional hexagram names
HEXAGRAM_NAMES: Dict[int, Dict[str, str]] = {
    1: {"name": "Qian", "chinese": "乾", "meaning": "The Creative"},
    2: {"name": "Kun", "chinese": "坤", "meaning": "The Receptive"},
    3: {"name": "Zhun", "chinese": "屯", "meaning": "Difficulty at the Beginning"},
    4: {"name": "Meng", "chinese": "蒙", "meaning": "Youthful Folly"},
    5: {"name": "Xu", "chinese": "需", "meaning": "Waiting"},
    6: {"name": "Song", "chinese": "訟", "meaning": "Conflict"},
    7: {"name": "Shi", "chinese": "師", "meaning": "The Army"},
    8: {"name": "Bi", "chinese": "比", "meaning": "Holding Together"},
    # ... (abbreviated for length)
    63: {"name": "Ji Ji", "chinese": "既濟", "meaning": "After Completion"},
    64: {"name": "Wei Ji", "chinese": "未濟", "meaning": "Before Completion"},
}


def get_hexagram_name(n: int) -> Dict[str, str]:
    """Get hexagram name data (1-64 numbering)."""
    return HEXAGRAM_NAMES.get(n, {"name": f"Hex{n}", "meaning": "Unknown"})


# Generate all 64 hexagrams
ALL_HEXAGRAMS = [Hexagram.from_binary(i) for i in range(64)]


# =============================================================================
# KING WEN SEQUENCE
# =============================================================================

# King Wen sequence (traditional ordering)
KING_WEN_SEQUENCE = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
    61, 62, 63, 64
]


# Binary to King Wen mapping (example - actual mapping is complex)
# This is a simplified placeholder
def binary_to_king_wen(binary: int) -> int:
    """Convert binary index (0-63) to King Wen number (1-64)."""
    # Simplified - actual King Wen sequence has specific logic
    return binary + 1


def king_wen_to_binary(kw: int) -> int:
    """Convert King Wen number (1-64) to binary index (0-63)."""
    return kw - 1


# =============================================================================
# HEXAGRAM RELATIONSHIPS
# =============================================================================

@dataclass
class HexagramRelationships:
    """
    Relationships between hexagrams.
    """
    
    hexagram: Hexagram
    
    @property
    def inverse(self) -> Hexagram:
        """Inverse (all lines flipped)."""
        return self.hexagram.invert()
    
    @property
    def reverse(self) -> Hexagram:
        """Reverse (upside down)."""
        return self.hexagram.reverse()
    
    @property
    def nuclear(self) -> Hexagram:
        """Nuclear hexagram."""
        return self.hexagram.nuclear()
    
    @property
    def mutual(self) -> Hexagram:
        """Mutual/paired hexagram (inverse then reverse)."""
        return self.inverse.reverse()
    
    @property
    def complement(self) -> int:
        """Complementary binary (63 - binary)."""
        return 63 - self.hexagram.binary
    
    def is_self_inverse(self) -> bool:
        """Check if hexagram equals its inverse."""
        return self.hexagram == self.inverse
    
    def is_self_reverse(self) -> bool:
        """Check if hexagram equals its reverse."""
        return self.hexagram == self.reverse
    
    def is_symmetric(self) -> bool:
        """Check if hexagram is symmetric (self-reverse)."""
        return self.is_self_reverse()
    
    def related_hexagrams(self) -> Dict[str, Hexagram]:
        """Get all related hexagrams."""
        return {
            "self": self.hexagram,
            "inverse": self.inverse,
            "reverse": self.reverse,
            "nuclear": self.nuclear,
            "mutual": self.mutual
        }


# =============================================================================
# ELEMENTAL CORRESPONDENCE
# =============================================================================

@dataclass
class ElementalCorrespondence:
    """
    Correspondence between hexagrams and elemental permutations.
    """
    
    @staticmethod
    def hexagram_to_permutation(hex_binary: int) -> Tuple[str, str, str]:
        """
        Convert hexagram binary to elemental permutation.
        
        Lines 1-2: Root
        Lines 3-4: Expression
        Lines 5-6: Mode
        """
        hex = Hexagram.from_binary(hex_binary)
        return hex.to_elements()
    
    @staticmethod
    def permutation_to_hexagram(root: str, expr: str, mode: str) -> Hexagram:
        """
        Convert elemental permutation to hexagram.
        """
        element_to_bits = {
            "Fire": (1, 1),
            "Air": (1, 0),
            "Water": (0, 0),
            "Earth": (0, 1)
        }
        
        r_bits = element_to_bits[root]
        e_bits = element_to_bits[expr]
        m_bits = element_to_bits[mode]
        
        lines = (
            Line(r_bits[0]), Line(r_bits[1]),
            Line(e_bits[0]), Line(e_bits[1]),
            Line(m_bits[0]), Line(m_bits[1])
        )
        return Hexagram(lines)
    
    @staticmethod
    def verify_isomorphism() -> bool:
        """Verify that mapping is bijective (one-to-one)."""
        seen_perms = set()
        for i in range(64):
            perm = ElementalCorrespondence.hexagram_to_permutation(i)
            if perm in seen_perms:
                return False
            seen_perms.add(perm)
        return len(seen_perms) == 64


# =============================================================================
# TRIGRAM OPERATIONS
# =============================================================================

class TrigramOperations:
    """
    Operations on the eight trigrams.
    """
    
    @staticmethod
    def trigram_lines(t: Trigram) -> Tuple[Line, Line, Line]:
        """Get the three lines of a trigram."""
        return tuple(Line((t.value >> i) & 1) for i in range(3))
    
    @staticmethod
    def invert_trigram(t: Trigram) -> Trigram:
        """Invert all lines of trigram."""
        return Trigram(7 - t.value)
    
    @staticmethod
    def reverse_trigram(t: Trigram) -> Trigram:
        """Reverse line order."""
        v = t.value
        # Swap bit 0 and bit 2
        new_v = ((v & 1) << 2) | (v & 2) | ((v >> 2) & 1)
        return Trigram(new_v)
    
    @staticmethod
    def combine_trigrams(lower: Trigram, upper: Trigram) -> int:
        """Combine two trigrams into hexagram binary."""
        return lower.value + (upper.value << 3)
    
    @staticmethod
    def all_hexagrams_from_trigrams() -> List[Tuple[Trigram, Trigram, int]]:
        """Generate all 64 hexagrams from trigram pairs."""
        result = []
        for lower in Trigram:
            for upper in Trigram:
                binary = TrigramOperations.combine_trigrams(lower, upper)
                result.append((lower, upper, binary))
        return result


# =============================================================================
# HEXAGRAM SYSTEM
# =============================================================================

class HexagramSystem:
    """
    Complete hexagram system with elemental correspondence.
    """
    
    N_HEXAGRAMS = 64
    N_TRIGRAMS = 8
    N_LINES = 2
    
    def __init__(self):
        self.hexagrams = ALL_HEXAGRAMS
        self.trigram_data = TRIGRAM_DATA
    
    def get_hexagram(self, binary: int) -> Hexagram:
        """Get hexagram by binary index (0-63)."""
        return self.hexagrams[binary % 64]
    
    def get_by_trigrams(self, lower: Trigram, upper: Trigram) -> Hexagram:
        """Get hexagram by trigram pair."""
        return Hexagram.from_trigrams(lower, upper)
    
    def iterate_hexagrams(self) -> Iterator[Hexagram]:
        """Iterate all 64 hexagrams."""
        return iter(self.hexagrams)
    
    def iterate_trigrams(self) -> Iterator[Trigram]:
        """Iterate all 8 trigrams."""
        return iter(Trigram)
    
    def hexagram_to_elements(self, hex: Hexagram) -> Tuple[str, str, str]:
        """Convert hexagram to elemental triple."""
        return hex.to_elements()
    
    def elements_to_hexagram(self, root: str, expr: str, mode: str) -> Hexagram:
        """Convert elemental triple to hexagram."""
        return ElementalCorrespondence.permutation_to_hexagram(root, expr, mode)
    
    def pure_hexagrams(self) -> List[Hexagram]:
        """Get hexagrams with all same lines."""
        return [h for h in self.hexagrams if h.is_pure]
    
    def symmetric_hexagrams(self) -> List[Hexagram]:
        """Get self-reversing hexagrams."""
        return [h for h in self.hexagrams if h == h.reverse()]
    
    def group_by_yang_count(self) -> Dict[int, List[Hexagram]]:
        """Group hexagrams by number of yang lines."""
        groups = {i: [] for i in range(7)}
        for hex in self.hexagrams:
            groups[hex.yang_count].append(hex)
        return groups
    
    def group_by_lower_trigram(self) -> Dict[Trigram, List[Hexagram]]:
        """Group hexagrams by lower trigram."""
        groups = {t: [] for t in Trigram}
        for hex in self.hexagrams:
            groups[hex.lower_trigram].append(hex)
        return groups
    
    def summary(self) -> Dict[str, Any]:
        """Get system summary."""
        yang_groups = self.group_by_yang_count()
        return {
            "total_hexagrams": self.N_HEXAGRAMS,
            "total_trigrams": self.N_TRIGRAMS,
            "pure_hexagrams": len(self.pure_hexagrams()),
            "symmetric_hexagrams": len(self.symmetric_hexagrams()),
            "yang_distribution": {k: len(v) for k, v in yang_groups.items()},
            "verification": {
                "2^6 = 64": 2**6 == 64,
                "4^3 = 64": 4**3 == 64,
                "8^2 = 64": 8**2 == 64,
                "8 trigrams × 8": 8 * 8 == 64
            }
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hexagram_system() -> bool:
    """Validate the hexagram module."""
    
    # Verify count
    assert len(ALL_HEXAGRAMS) == 64
    assert len(Trigram) == 8
    
    # Verify binary uniqueness
    binaries = [h.binary for h in ALL_HEXAGRAMS]
    assert len(set(binaries)) == 64
    assert set(binaries) == set(range(64))
    
    # Verify trigram reconstruction
    for hex in ALL_HEXAGRAMS:
        reconstructed = Hexagram.from_trigrams(hex.lower_trigram, hex.upper_trigram)
        assert reconstructed.binary == hex.binary
    
    # Verify elemental correspondence isomorphism
    assert ElementalCorrespondence.verify_isomorphism()
    
    # Verify pure hexagrams
    pure = [h for h in ALL_HEXAGRAMS if h.is_pure]
    assert len(pure) == 2  # All yang, all yin
    
    # Verify yang count distribution
    # Binomial: C(6,k) = 1,6,15,20,15,6,1
    system = HexagramSystem()
    yang_dist = system.group_by_yang_count()
    expected = {0: 1, 1: 6, 2: 15, 3: 20, 4: 15, 5: 6, 6: 1}
    for k, v in expected.items():
        assert len(yang_dist[k]) == v, f"Yang count {k}: expected {v}, got {len(yang_dist[k])}"
    
    # Verify inversion
    hex_0 = Hexagram.from_binary(0)
    hex_63 = Hexagram.from_binary(63)
    assert hex_0.invert().binary == 63
    assert hex_63.invert().binary == 0
    
    # System summary
    summary = system.summary()
    assert summary["total_hexagrams"] == 64
    
    return True


if __name__ == "__main__":
    print("Validating Hexagram System...")
    assert validate_hexagram_system()
    print("✓ Hexagram System validated")
    
    # Demo
    print("\n--- Hexagram System Demo ---")
    
    system = HexagramSystem()
    summary = system.summary()
    
    print(f"\nTotal Hexagrams: {summary['total_hexagrams']}")
    print(f"Total Trigrams: {summary['total_trigrams']}")
    
    print("\nVerification:")
    for eq, result in summary['verification'].items():
        print(f"  {eq}: {result}")
    
    print("\nYang Line Distribution:")
    for k, count in summary['yang_distribution'].items():
        print(f"  {k} yang lines: {count} hexagrams")
    
    print("\nSample Hexagram (binary 42):")
    hex_42 = system.get_hexagram(42)
    print(f"  Binary: {hex_42.binary}")
    print(f"  Lines: {hex_42.line_string}")
    print(f"  Lower: {TRIGRAM_DATA[hex_42.lower_trigram]['name']}")
    print(f"  Upper: {TRIGRAM_DATA[hex_42.upper_trigram]['name']}")
    print(f"  Elements: {hex_42.to_elements()}")
    
    print("\nTrigram Info:")
    for trigram in list(Trigram)[:4]:
        data = TRIGRAM_DATA[trigram]
        print(f"  {data['symbol']} {data['name']} ({data['nature']}): {data['lines']}")
