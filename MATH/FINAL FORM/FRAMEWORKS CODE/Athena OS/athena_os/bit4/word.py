"""
ATHENA OS - BIT4 WORD-LEVEL COMPLETION
======================================
Exact Word-Level Completion: W_n = P({0,1}^n)

From Bit4_CODE_-working-.docx:

WORD-LEVEL COMPLETION:
    For n-bit words, the completion is:
    
    W_n = {0,1}^n  (classical n-bit words)
    ??_n = P(W_n)   (sets of possible words)
    
    This preserves correlations between bits that are lost
    when treating each bit independently.

FOUR CANONICAL WORD-STATES:
    ⊥_n = ∅           (no admissible word - impossible)
    Sing_n = |S|=1    (determinate - exactly one word)
    Multi_n = 1<|S|<2^n  (indeterminate but constrained)
    ⊤_n = W_n         (all words possible - no information)

LIFTED OPERATIONS:
    For any classical operation g: W_n → W_n:
    
    ĝ(S) = {g(x) : x ∈ S}
    
    This is exact - no correlation loss.

COLLAPSE PROTOCOLS:
    Point measurement: pick one w ∈ S (needs seed)
    Must-measurement: extract only invariants across S
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    FrozenSet, Set, Dict, List, Tuple, Optional, 
    Callable, Iterator, Any, TypeVar, Generic
)
from enum import Enum, auto
import numpy as np
from functools import lru_cache
import hashlib

from .core import B4, BOT, ZERO, ONE, TOP


# =============================================================================
# WORD REPRESENTATION
# =============================================================================

@dataclass(frozen=True)
class Word:
    """
    Classical n-bit word.
    
    Represents a single classical bitstring.
    """
    bits: Tuple[int, ...]
    
    def __post_init__(self):
        """Validate bits are 0 or 1."""
        for b in self.bits:
            if b not in (0, 1):
                raise ValueError(f"Bit must be 0 or 1, got {b}")
    
    @property
    def n(self) -> int:
        """Word width."""
        return len(self.bits)
    
    def __len__(self) -> int:
        return len(self.bits)
    
    def __getitem__(self, idx: int) -> int:
        return self.bits[idx]
    
    def __int__(self) -> int:
        """Convert to integer (LSB first)."""
        result = 0
        for i, b in enumerate(self.bits):
            result |= b << i
        return result
    
    def __str__(self) -> str:
        return ''.join(str(b) for b in reversed(self.bits))
    
    def __repr__(self) -> str:
        return f"Word({self})"
    
    @classmethod
    def from_int(cls, value: int, n: int) -> 'Word':
        """Create word from integer."""
        bits = tuple((value >> i) & 1 for i in range(n))
        return cls(bits)
    
    @classmethod
    def zeros(cls, n: int) -> 'Word':
        """All zeros word."""
        return cls(tuple(0 for _ in range(n)))
    
    @classmethod
    def ones(cls, n: int) -> 'Word':
        """All ones word."""
        return cls(tuple(1 for _ in range(n)))
    
    def flip(self, idx: int) -> 'Word':
        """Flip bit at index."""
        bits = list(self.bits)
        bits[idx] = 1 - bits[idx]
        return Word(tuple(bits))
    
    def bitwise_not(self) -> 'Word':
        """Bitwise NOT."""
        return Word(tuple(1 - b for b in self.bits))
    
    def bitwise_and(self, other: 'Word') -> 'Word':
        """Bitwise AND."""
        return Word(tuple(a & b for a, b in zip(self.bits, other.bits)))
    
    def bitwise_or(self, other: 'Word') -> 'Word':
        """Bitwise OR."""
        return Word(tuple(a | b for a, b in zip(self.bits, other.bits)))
    
    def bitwise_xor(self, other: 'Word') -> 'Word':
        """Bitwise XOR."""
        return Word(tuple(a ^ b for a, b in zip(self.bits, other.bits)))


# =============================================================================
# WORD SET (COMPLETED WORD)
# =============================================================================

class WordClass(Enum):
    """Four canonical word-state classes."""
    
    IMPOSSIBLE = auto()   # ⊥_n: |S| = 0
    DETERMINATE = auto()  # Sing_n: |S| = 1
    CONSTRAINED = auto()  # Multi_n: 1 < |S| < 2^n
    UNCONSTRAINED = auto()  # ⊤_n: |S| = 2^n


@dataclass
class WordSet:
    """
    Completed n-bit word: a set of possible classical words.
    
    ??_n = P(W_n)
    
    This represents epistemic uncertainty about which classical
    word is the actual value.
    """
    
    words: FrozenSet[Word]
    n: int
    
    def __post_init__(self):
        """Validate all words have same width."""
        for w in self.words:
            if w.n != self.n:
                raise ValueError(f"Word width mismatch: {w.n} vs {self.n}")
    
    @classmethod
    def empty(cls, n: int) -> 'WordSet':
        """Create ⊥_n (impossible/no admissible word)."""
        return cls(frozenset(), n)
    
    @classmethod
    def singleton(cls, word: Word) -> 'WordSet':
        """Create determinate word set."""
        return cls(frozenset([word]), word.n)
    
    @classmethod
    def full(cls, n: int) -> 'WordSet':
        """Create ⊤_n (all words possible)."""
        words = frozenset(Word.from_int(i, n) for i in range(2**n))
        return cls(words, n)
    
    @classmethod
    def from_ints(cls, values: List[int], n: int) -> 'WordSet':
        """Create from list of integers."""
        words = frozenset(Word.from_int(v, n) for v in values)
        return cls(words, n)
    
    @classmethod
    def from_constraint(cls, n: int, 
                       constraint: Callable[[Word], bool]) -> 'WordSet':
        """Create from constraint function."""
        words = frozenset(
            Word.from_int(i, n) 
            for i in range(2**n) 
            if constraint(Word.from_int(i, n))
        )
        return cls(words, n)
    
    def __len__(self) -> int:
        return len(self.words)
    
    def __contains__(self, word: Word) -> bool:
        return word in self.words
    
    def __iter__(self) -> Iterator[Word]:
        return iter(self.words)
    
    def __and__(self, other: 'WordSet') -> 'WordSet':
        """Intersection (conjunction of constraints)."""
        return WordSet(self.words & other.words, self.n)
    
    def __or__(self, other: 'WordSet') -> 'WordSet':
        """Union (disjunction of constraints)."""
        return WordSet(self.words | other.words, self.n)
    
    def __sub__(self, other: 'WordSet') -> 'WordSet':
        """Set difference."""
        return WordSet(self.words - other.words, self.n)
    
    def __str__(self) -> str:
        if len(self) == 0:
            return f"⊥_{self.n}"
        elif len(self) == 2**self.n:
            return f"⊤_{self.n}"
        elif len(self) == 1:
            w = next(iter(self.words))
            return f"{{{w}}}"
        elif len(self) <= 4:
            words_str = ", ".join(str(w) for w in sorted(self.words, key=int))
            return f"{{{words_str}}}"
        else:
            return f"WordSet(|S|={len(self)}, n={self.n})"
    
    @property
    def word_class(self) -> WordClass:
        """Get canonical word-state class."""
        size = len(self)
        max_size = 2 ** self.n
        
        if size == 0:
            return WordClass.IMPOSSIBLE
        elif size == 1:
            return WordClass.DETERMINATE
        elif size == max_size:
            return WordClass.UNCONSTRAINED
        else:
            return WordClass.CONSTRAINED
    
    @property
    def is_classical(self) -> bool:
        """Check if determinate (exactly one word)."""
        return len(self) == 1
    
    @property
    def is_empty(self) -> bool:
        """Check if impossible (no words)."""
        return len(self) == 0
    
    @property
    def is_full(self) -> bool:
        """Check if unconstrained (all words)."""
        return len(self) == 2 ** self.n
    
    def get_word(self) -> Optional[Word]:
        """Get the single word if determinate, else None."""
        if self.is_classical:
            return next(iter(self.words))
        return None
    
    def refine(self, constraint: Callable[[Word], bool]) -> 'WordSet':
        """Refine by adding constraint."""
        new_words = frozenset(w for w in self.words if constraint(w))
        return WordSet(new_words, self.n)
    
    def to_b4_vector(self) -> List[B4]:
        """
        Project to per-bit B4 values.
        
        This LOSES correlation information but is useful for
        approximate analysis.
        """
        result = []
        for i in range(self.n):
            has_zero = any(w[i] == 0 for w in self.words)
            has_one = any(w[i] == 1 for w in self.words)
            
            if not has_zero and not has_one:
                result.append(BOT)
            elif has_zero and not has_one:
                result.append(ZERO)
            elif has_one and not has_zero:
                result.append(ONE)
            else:
                result.append(TOP)
        
        return result
    
    @classmethod
    def from_b4_vector(cls, vec: List[B4]) -> 'WordSet':
        """
        Create from per-bit B4 values.
        
        This creates the Cartesian product of per-bit possibilities.
        """
        n = len(vec)
        
        # Generate all compatible words
        def compatible_words(idx: int, prefix: List[int]) -> List[Word]:
            if idx == n:
                return [Word(tuple(prefix))]
            
            b4 = vec[idx]
            results = []
            
            if b4 == BOT:
                return []  # No compatible words
            elif b4 == ZERO:
                results.extend(compatible_words(idx + 1, prefix + [0]))
            elif b4 == ONE:
                results.extend(compatible_words(idx + 1, prefix + [1]))
            else:  # TOP
                results.extend(compatible_words(idx + 1, prefix + [0]))
                results.extend(compatible_words(idx + 1, prefix + [1]))
            
            return results
        
        words = frozenset(compatible_words(0, []))
        return cls(words, n)


# =============================================================================
# LIFTED OPERATIONS
# =============================================================================

def lift_unary(f: Callable[[Word], Word], ws: WordSet) -> WordSet:
    """
    Lift unary operation to word sets.
    
    ĝ(S) = {g(x) : x ∈ S}
    """
    if ws.is_empty:
        return ws
    
    new_words = frozenset(f(w) for w in ws.words)
    return WordSet(new_words, ws.n)


def lift_binary(f: Callable[[Word, Word], Word], 
               ws1: WordSet, ws2: WordSet) -> WordSet:
    """
    Lift binary operation to word sets.
    
    ĝ(S, T) = {g(x, y) : x ∈ S, y ∈ T}
    """
    if ws1.is_empty or ws2.is_empty:
        return WordSet.empty(ws1.n)
    
    new_words = frozenset(
        f(w1, w2) for w1 in ws1.words for w2 in ws2.words
    )
    return WordSet(new_words, ws1.n)


# =============================================================================
# WORD ARITHMETIC
# =============================================================================

def word_add(w1: Word, w2: Word) -> Word:
    """Add two words (modulo 2^n)."""
    n = w1.n
    result = (int(w1) + int(w2)) % (2 ** n)
    return Word.from_int(result, n)


def word_sub(w1: Word, w2: Word) -> Word:
    """Subtract words (modulo 2^n)."""
    n = w1.n
    result = (int(w1) - int(w2)) % (2 ** n)
    return Word.from_int(result, n)


def word_mul(w1: Word, w2: Word) -> Word:
    """Multiply words (modulo 2^n)."""
    n = w1.n
    result = (int(w1) * int(w2)) % (2 ** n)
    return Word.from_int(result, n)


def lifted_add(ws1: WordSet, ws2: WordSet) -> WordSet:
    """
    Exact lifted addition on word sets.
    
    S ⊞ T = {add(x, y) : x ∈ S, y ∈ T}
    
    This preserves correlations exactly.
    """
    return lift_binary(word_add, ws1, ws2)


def lifted_sub(ws1: WordSet, ws2: WordSet) -> WordSet:
    """Exact lifted subtraction."""
    return lift_binary(word_sub, ws1, ws2)


def lifted_mul(ws1: WordSet, ws2: WordSet) -> WordSet:
    """Exact lifted multiplication."""
    return lift_binary(word_mul, ws1, ws2)


def lifted_not(ws: WordSet) -> WordSet:
    """Lifted bitwise NOT."""
    return lift_unary(lambda w: w.bitwise_not(), ws)


def lifted_and(ws1: WordSet, ws2: WordSet) -> WordSet:
    """Lifted bitwise AND."""
    return lift_binary(lambda w1, w2: w1.bitwise_and(w2), ws1, ws2)


def lifted_or(ws1: WordSet, ws2: WordSet) -> WordSet:
    """Lifted bitwise OR."""
    return lift_binary(lambda w1, w2: w1.bitwise_or(w2), ws1, ws2)


def lifted_xor(ws1: WordSet, ws2: WordSet) -> WordSet:
    """Lifted bitwise XOR."""
    return lift_binary(lambda w1, w2: w1.bitwise_xor(w2), ws1, ws2)


# =============================================================================
# COLLAPSE PROTOCOLS
# =============================================================================

class CollapsePolicy(Enum):
    """Word-level collapse policies."""
    
    CONSERVATIVE = auto()  # Return err if not determinate
    OPTIMISTIC = auto()    # Pick arbitrary element
    SEEDED = auto()        # Deterministic pick based on seed
    MINIMUM = auto()       # Pick minimum value
    MAXIMUM = auto()       # Pick maximum value


@dataclass
class CollapseResult:
    """Result of word collapse."""
    
    word: Optional[Word]
    success: bool
    policy: CollapsePolicy
    original_size: int
    
    @property
    def is_error(self) -> bool:
        return not self.success


def collapse_word(ws: WordSet, policy: CollapsePolicy,
                  seed: int = 0) -> CollapseResult:
    """
    Collapse word set to single word.
    
    Point measurement: pick one w ∈ S
    """
    if ws.is_empty:
        return CollapseResult(None, False, policy, 0)
    
    if ws.is_classical:
        return CollapseResult(ws.get_word(), True, policy, 1)
    
    if policy == CollapsePolicy.CONSERVATIVE:
        return CollapseResult(None, False, policy, len(ws))
    
    elif policy == CollapsePolicy.MINIMUM:
        word = min(ws.words, key=int)
        return CollapseResult(word, True, policy, len(ws))
    
    elif policy == CollapsePolicy.MAXIMUM:
        word = max(ws.words, key=int)
        return CollapseResult(word, True, policy, len(ws))
    
    elif policy == CollapsePolicy.SEEDED:
        # Deterministic selection based on seed
        words_sorted = sorted(ws.words, key=int)
        idx = seed % len(words_sorted)
        return CollapseResult(words_sorted[idx], True, policy, len(ws))
    
    else:  # OPTIMISTIC - pick first
        word = next(iter(ws.words))
        return CollapseResult(word, True, policy, len(ws))


# =============================================================================
# MUST-MEASUREMENT (MONOTONE KNOWLEDGE EXTRACTION)
# =============================================================================

@dataclass
class MustMeasurement:
    """
    Must-measurement: extract only what's invariant across all words.
    
    This never contradicts under refinement - it only becomes more specific.
    """
    
    ws: WordSet
    
    def must_bit(self, i: int) -> Optional[int]:
        """
        Get bit i if it's constant across all words.
        
        Returns None if bit varies.
        """
        if self.ws.is_empty:
            return None
        
        first_bit = None
        for w in self.ws.words:
            if first_bit is None:
                first_bit = w[i]
            elif w[i] != first_bit:
                return None
        
        return first_bit
    
    def must_bits(self) -> Dict[int, int]:
        """Get all constant bits."""
        result = {}
        for i in range(self.ws.n):
            bit = self.must_bit(i)
            if bit is not None:
                result[i] = bit
        return result
    
    def must_value(self) -> Optional[Word]:
        """Get the word if all bits are determined."""
        bits = []
        for i in range(self.ws.n):
            bit = self.must_bit(i)
            if bit is None:
                return None
            bits.append(bit)
        return Word(tuple(bits))
    
    def uncertainty(self) -> int:
        """Count uncertain bits."""
        return self.ws.n - len(self.must_bits())
    
    def entropy_bits(self) -> float:
        """Estimate entropy in bits."""
        if self.ws.is_empty:
            return 0.0
        return np.log2(len(self.ws))


# =============================================================================
# HALF-ADDER IN WORD SPACE
# =============================================================================

def half_adder_word(a: Word, b: Word) -> Tuple[Word, Word]:
    """
    Classical half-adder returning (sum, carry).
    
    For single-bit words only.
    """
    assert a.n == 1 and b.n == 1
    
    sum_bit = a[0] ^ b[0]
    carry_bit = a[0] & b[0]
    
    return Word((sum_bit,)), Word((carry_bit,))


def lifted_half_adder(ws_a: WordSet, ws_b: WordSet) -> Tuple[WordSet, WordSet]:
    """
    Lifted half-adder preserving correlations.
    
    Returns (sum_set, carry_set).
    """
    if ws_a.is_empty or ws_b.is_empty:
        return WordSet.empty(1), WordSet.empty(1)
    
    sums = set()
    carries = set()
    
    for a in ws_a.words:
        for b in ws_b.words:
            s, c = half_adder_word(a, b)
            sums.add(s)
            carries.add(c)
    
    return WordSet(frozenset(sums), 1), WordSet(frozenset(carries), 1)


# =============================================================================
# FULL ADDER
# =============================================================================

def full_adder_word(a: Word, b: Word, cin: Word) -> Tuple[Word, Word]:
    """
    Classical full-adder returning (sum, carry_out).
    """
    assert a.n == 1 and b.n == 1 and cin.n == 1
    
    xor_ab = a[0] ^ b[0]
    sum_bit = xor_ab ^ cin[0]
    carry_bit = (a[0] & b[0]) | (xor_ab & cin[0])
    
    return Word((sum_bit,)), Word((carry_bit,))


def lifted_full_adder(ws_a: WordSet, ws_b: WordSet, 
                      ws_cin: WordSet) -> Tuple[WordSet, WordSet]:
    """
    Lifted full-adder preserving correlations.
    """
    if ws_a.is_empty or ws_b.is_empty or ws_cin.is_empty:
        return WordSet.empty(1), WordSet.empty(1)
    
    sums = set()
    carries = set()
    
    for a in ws_a.words:
        for b in ws_b.words:
            for cin in ws_cin.words:
                s, cout = full_adder_word(a, b, cin)
                sums.add(s)
                carries.add(cout)
    
    return WordSet(frozenset(sums), 1), WordSet(frozenset(carries), 1)


# =============================================================================
# N-BIT RIPPLE CARRY ADDER
# =============================================================================

def ripple_carry_add(ws_a: WordSet, ws_b: WordSet) -> WordSet:
    """
    N-bit ripple carry addition using lifted full adders.
    
    This is slower than lifted_add but demonstrates the gate structure.
    """
    n = ws_a.n
    
    # Split into per-bit word sets
    a_bits = [
        WordSet(frozenset(Word((w[i],)) for w in ws_a.words), 1)
        for i in range(n)
    ]
    b_bits = [
        WordSet(frozenset(Word((w[i],)) for w in ws_b.words), 1)
        for i in range(n)
    ]
    
    # Initial carry = 0
    carry = WordSet.singleton(Word((0,)))
    
    # Result bits
    sum_bits = []
    
    for i in range(n):
        s, carry = lifted_full_adder(a_bits[i], b_bits[i], carry)
        sum_bits.append(s)
    
    # Combine sum bits back to word set
    # This is approximate - we lose correlation between bits
    if any(s.is_empty for s in sum_bits):
        return WordSet.empty(n)
    
    # Build all possible combinations
    result_words = set()
    
    def build_words(idx: int, bits: List[int]) -> None:
        if idx == n:
            result_words.add(Word(tuple(bits)))
            return
        
        for w in sum_bits[idx].words:
            build_words(idx + 1, bits + [w[0]])
    
    build_words(0, [])
    
    return WordSet(frozenset(result_words), n)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_word() -> bool:
    """Validate word module."""
    
    # Test Word
    w = Word((0, 1, 1, 0))
    assert w.n == 4
    assert int(w) == 6  # 0110 binary = 6
    assert str(w) == "0110"
    
    w2 = Word.from_int(6, 4)
    assert w == w2
    
    w_not = w.bitwise_not()
    assert w_not.bits == (1, 0, 0, 1)
    
    # Test WordSet
    ws = WordSet.empty(4)
    assert ws.is_empty
    assert ws.word_class == WordClass.IMPOSSIBLE
    
    ws_full = WordSet.full(2)
    assert ws_full.is_full
    assert len(ws_full) == 4
    assert ws_full.word_class == WordClass.UNCONSTRAINED
    
    ws_single = WordSet.singleton(Word((1, 0)))
    assert ws_single.is_classical
    assert ws_single.word_class == WordClass.DETERMINATE
    
    # Test lifted operations
    ws1 = WordSet.from_ints([0, 1], 2)  # {00, 01}
    ws2 = WordSet.from_ints([0, 1], 2)  # {00, 01}
    
    # Add: 0+0=0, 0+1=1, 1+0=1, 1+1=2
    ws_sum = lifted_add(ws1, ws2)
    expected = {0, 1, 2}
    actual = {int(w) for w in ws_sum.words}
    assert actual == expected, f"Got {actual}, expected {expected}"
    
    # Test B4 projection
    ws = WordSet.from_ints([1, 3], 2)  # {01, 11} - bit 0 varies, bit 1 always 1
    b4_vec = ws.to_b4_vector()
    assert b4_vec[0] == TOP   # varies
    assert b4_vec[1] == ONE   # always 1
    
    # Test must-measurement
    mm = MustMeasurement(ws)
    assert mm.must_bit(0) is None
    assert mm.must_bit(1) == 1
    assert mm.must_bits() == {1: 1}
    
    # Test collapse
    ws = WordSet.from_ints([0, 1, 2], 2)
    
    result = collapse_word(ws, CollapsePolicy.CONSERVATIVE)
    assert result.is_error
    
    result = collapse_word(ws, CollapsePolicy.MINIMUM)
    assert result.success
    assert int(result.word) == 0
    
    result = collapse_word(ws, CollapsePolicy.MAXIMUM)
    assert result.success
    assert int(result.word) == 2
    
    # Test half adder
    a = WordSet.singleton(Word((1,)))
    b = WordSet.singleton(Word((1,)))
    s, c = lifted_half_adder(a, b)
    assert s.get_word()[0] == 0  # 1 XOR 1 = 0
    assert c.get_word()[0] == 1  # 1 AND 1 = 1
    
    # Test with uncertainty
    a = WordSet.full(1)  # {0, 1}
    b = WordSet.full(1)  # {0, 1}
    s, c = lifted_half_adder(a, b)
    assert len(s) == 2   # sum can be 0 or 1
    assert len(c) == 2   # carry can be 0 or 1
    
    return True


if __name__ == "__main__":
    print("Validating Word module...")
    assert validate_word()
    print("✓ Word module validated")
