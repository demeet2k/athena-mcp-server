"""
ATHENA OS - BIT4
================
Carrier Set and Canonical Encodings

From BIT4.docx §1.2:

B₄ = P({0,1}) = {∅, {0}, {1}, {0,1}}

GLYPHS:
    ⊥ := ∅      (gap/unknown/no information)
    0 := {0}    (only false supported)
    1 := {1}    (only true supported)
    ⊤ := {0,1}  (conflict/both supported)

BIT4 is NOT a 2-bit integer encoding. It is a four-valued semantic
domain whose elements are SUPPORT SETS of admissible classical outcomes.

TWO-RAIL ENCODING:
    enc: B₄ → {0,1}²
    enc(x) = (t(x), f(x))
    where t(x) = 1[1 ∈ x], f(x) = 1[0 ∈ x]

    ⊥ → (0, 0)
    0 → (0, 1)
    1 → (1, 0)
    ⊤ → (1, 1)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Set, Tuple, Optional, List, FrozenSet
from enum import Enum, auto


# =============================================================================
# BIT4 VALUE CLASS
# =============================================================================

class B4(Enum):
    """
    The four-valued BIT4 state space.
    
    B₄ = P({0,1}) = {⊥, 0, 1, ⊤}
    """
    
    BOT = 0    # ⊥ = ∅ (gap, unknown, no evidence)
    ZERO = 1   # 0 = {0} (only false supported)
    ONE = 2    # 1 = {1} (only true supported)
    TOP = 3    # ⊤ = {0,1} (conflict, both supported)
    
    @property
    def support(self) -> FrozenSet[int]:
        """Get support set representation."""
        if self == B4.BOT:
            return frozenset()
        elif self == B4.ZERO:
            return frozenset({0})
        elif self == B4.ONE:
            return frozenset({1})
        else:  # TOP
            return frozenset({0, 1})
    
    @property
    def glyph(self) -> str:
        """Unicode glyph representation."""
        glyphs = {
            B4.BOT: "⊥",
            B4.ZERO: "0",
            B4.ONE: "1",
            B4.TOP: "⊤"
        }
        return glyphs[self]
    
    @property
    def is_classical(self) -> bool:
        """Check if value is classical (0 or 1)."""
        return self in (B4.ZERO, B4.ONE)
    
    @property
    def is_shadow(self) -> bool:
        """Check if value is in the 'shadow pole' (⊥ or ⊤)."""
        return self in (B4.BOT, B4.TOP)
    
    @property
    def is_gap(self) -> bool:
        """Check if value is gap/unknown (⊥)."""
        return self == B4.BOT
    
    @property
    def is_conflict(self) -> bool:
        """Check if value is conflict/overdetermined (⊤)."""
        return self == B4.TOP
    
    @property
    def width(self) -> int:
        """Support width |x|."""
        return len(self.support)
    
    @classmethod
    def from_support(cls, s: Set[int]) -> 'B4':
        """Create from support set."""
        fs = frozenset(s)
        if fs == frozenset():
            return cls.BOT
        elif fs == frozenset({0}):
            return cls.ZERO
        elif fs == frozenset({1}):
            return cls.ONE
        elif fs == frozenset({0, 1}):
            return cls.TOP
        raise ValueError(f"Invalid support set: {s}")
    
    @classmethod
    def from_bool(cls, b: bool) -> 'B4':
        """Embed classical boolean into B4."""
        return cls.ONE if b else cls.ZERO
    
    def to_bool(self) -> Optional[bool]:
        """Extract classical boolean if determinate."""
        if self == B4.ZERO:
            return False
        elif self == B4.ONE:
            return True
        return None  # ⊥ or ⊤
    
    def __repr__(self) -> str:
        return self.glyph


# =============================================================================
# TWO-RAIL ENCODING
# =============================================================================

@dataclass(frozen=True)
class TwoRail:
    """
    Two-rail encoding of BIT4.
    
    enc(x) = (t, f) where:
        t = 1[1 ∈ x] (truth rail)
        f = 1[0 ∈ x] (falsity rail)
    
    Encoding table:
        ⊥ → (0, 0)
        0 → (0, 1)
        1 → (1, 0)
        ⊤ → (1, 1)
    """
    
    t: int  # Truth rail (0 or 1)
    f: int  # Falsity rail (0 or 1)
    
    def __post_init__(self):
        assert self.t in (0, 1), f"Truth rail must be 0 or 1, got {self.t}"
        assert self.f in (0, 1), f"Falsity rail must be 0 or 1, got {self.f}"
    
    @classmethod
    def encode(cls, x: B4) -> 'TwoRail':
        """Encode B4 value to two-rail."""
        t = 1 if 1 in x.support else 0
        f = 1 if 0 in x.support else 0
        return cls(t, f)
    
    def decode(self) -> B4:
        """Decode two-rail to B4 value."""
        support = set()
        if self.t == 1:
            support.add(1)
        if self.f == 1:
            support.add(0)
        return B4.from_support(support)
    
    @property
    def tuple(self) -> Tuple[int, int]:
        """Get as tuple (t, f)."""
        return (self.t, self.f)
    
    def __repr__(self) -> str:
        return f"({self.t}, {self.f})"


# =============================================================================
# ONE-HOT ENCODING
# =============================================================================

@dataclass(frozen=True)
class OneHot:
    """
    One-hot encoding of BIT4.
    
    Each B4 value gets exactly one active rail.
    
    Encoding:
        ⊥ → (1, 0, 0, 0)
        0 → (0, 1, 0, 0)
        1 → (0, 0, 1, 0)
        ⊤ → (0, 0, 0, 1)
    """
    
    u_bot: int
    u_zero: int
    u_one: int
    u_top: int
    
    def __post_init__(self):
        # Validate exactly-one-hot
        total = self.u_bot + self.u_zero + self.u_one + self.u_top
        assert total == 1, f"One-hot encoding must sum to 1, got {total}"
    
    @classmethod
    def encode(cls, x: B4) -> 'OneHot':
        """Encode B4 value to one-hot."""
        encoding = {
            B4.BOT: (1, 0, 0, 0),
            B4.ZERO: (0, 1, 0, 0),
            B4.ONE: (0, 0, 1, 0),
            B4.TOP: (0, 0, 0, 1)
        }
        u = encoding[x]
        return cls(*u)
    
    def decode(self) -> B4:
        """Decode one-hot to B4 value."""
        if self.u_bot:
            return B4.BOT
        elif self.u_zero:
            return B4.ZERO
        elif self.u_one:
            return B4.ONE
        else:
            return B4.TOP
    
    @property
    def tuple(self) -> Tuple[int, int, int, int]:
        """Get as tuple."""
        return (self.u_bot, self.u_zero, self.u_one, self.u_top)
    
    def __repr__(self) -> str:
        return f"({self.u_bot}, {self.u_zero}, {self.u_one}, {self.u_top})"


# =============================================================================
# ENCODING CONVERSIONS
# =============================================================================

def two_rail_to_one_hot(tr: TwoRail) -> OneHot:
    """Convert two-rail to one-hot encoding."""
    return OneHot.encode(tr.decode())


def one_hot_to_two_rail(oh: OneHot) -> TwoRail:
    """Convert one-hot to two-rail encoding."""
    return TwoRail.encode(oh.decode())


# =============================================================================
# BIT4 VECTOR
# =============================================================================

@dataclass
class B4Vector:
    """
    Vector of BIT4 values.
    
    Represents multi-wire state in circuits.
    """
    
    values: List[B4]
    
    def __len__(self) -> int:
        return len(self.values)
    
    def __getitem__(self, i: int) -> B4:
        return self.values[i]
    
    def __setitem__(self, i: int, v: B4) -> None:
        self.values[i] = v
    
    @classmethod
    def from_bools(cls, bools: List[bool]) -> 'B4Vector':
        """Create from list of booleans."""
        return cls([B4.from_bool(b) for b in bools])
    
    @classmethod
    def bottom(cls, n: int) -> 'B4Vector':
        """Create n-vector of ⊥."""
        return cls([B4.BOT] * n)
    
    @classmethod
    def top(cls, n: int) -> 'B4Vector':
        """Create n-vector of ⊤."""
        return cls([B4.TOP] * n)
    
    @property
    def is_classical(self) -> bool:
        """Check if all values are classical."""
        return all(v.is_classical for v in self.values)
    
    @property
    def has_shadow(self) -> bool:
        """Check if any value is shadow (⊥ or ⊤)."""
        return any(v.is_shadow for v in self.values)
    
    def encode_two_rail(self) -> List[TwoRail]:
        """Encode to list of two-rail values."""
        return [TwoRail.encode(v) for v in self.values]
    
    def __repr__(self) -> str:
        return f"[{', '.join(v.glyph for v in self.values)}]"


# =============================================================================
# VALIDATION
# =============================================================================

def validate_carrier() -> bool:
    """Validate carrier module."""
    
    # Test B4 values
    assert B4.BOT.support == frozenset()
    assert B4.ZERO.support == frozenset({0})
    assert B4.ONE.support == frozenset({1})
    assert B4.TOP.support == frozenset({0, 1})
    
    # Test properties
    assert B4.BOT.is_gap
    assert B4.TOP.is_conflict
    assert B4.ZERO.is_classical
    assert B4.ONE.is_classical
    assert not B4.BOT.is_classical
    
    # Test width
    assert B4.BOT.width == 0
    assert B4.ZERO.width == 1
    assert B4.ONE.width == 1
    assert B4.TOP.width == 2
    
    # Test from_support
    assert B4.from_support(set()) == B4.BOT
    assert B4.from_support({0}) == B4.ZERO
    assert B4.from_support({1}) == B4.ONE
    assert B4.from_support({0, 1}) == B4.TOP
    
    # Test TwoRail encoding
    assert TwoRail.encode(B4.BOT).tuple == (0, 0)
    assert TwoRail.encode(B4.ZERO).tuple == (0, 1)
    assert TwoRail.encode(B4.ONE).tuple == (1, 0)
    assert TwoRail.encode(B4.TOP).tuple == (1, 1)
    
    # Test TwoRail decoding
    assert TwoRail(0, 0).decode() == B4.BOT
    assert TwoRail(0, 1).decode() == B4.ZERO
    assert TwoRail(1, 0).decode() == B4.ONE
    assert TwoRail(1, 1).decode() == B4.TOP
    
    # Test OneHot encoding
    assert OneHot.encode(B4.BOT).tuple == (1, 0, 0, 0)
    assert OneHot.encode(B4.ZERO).tuple == (0, 1, 0, 0)
    assert OneHot.encode(B4.ONE).tuple == (0, 0, 1, 0)
    assert OneHot.encode(B4.TOP).tuple == (0, 0, 0, 1)
    
    # Test B4Vector
    v = B4Vector([B4.ZERO, B4.ONE, B4.TOP])
    assert len(v) == 3
    assert v.has_shadow
    
    v2 = B4Vector.from_bools([True, False, True])
    assert v2.is_classical
    
    return True


if __name__ == "__main__":
    print("Validating BIT4 Carrier...")
    assert validate_carrier()
    print("✓ Carrier module validated")
