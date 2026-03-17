"""
ATHENA OS - BIT4
================
Orders and Bilattice Structure

From BIT4.docx §2:

TWO ORTHOGONAL ORDERS (bilattice core):

1. KNOWLEDGE ORDER ≤_k (information inclusion):
    x ≤_k y ⟺ x ⊆ y
    
    ⊥ is least informative
    ⊤ is most informative  
    0, 1 are incomparable
    
    Hasse diagram (≤_k):
           ⊤
          / \
         0   1
          \ /
           ⊥

2. TRUTH ORDER ≤_t (truth increases, falsity decreases):
    x ≤_t y ⟺ t(x) ≤ t(y) ∧ f(y) ≤ f(x)
    
    0 is least true (most false)
    1 is most true (least false)
    ⊥, ⊤ are incomparable
    
    Hasse diagram (≤_t):
           1
          / \
         ⊥   ⊤
          \ /
           0

The bilattice (B₄, ≤_k, ≤_t) separates:
- "How much information is present" (knowledge)
- "How true the proposition is" (truth)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Set, Optional
from enum import Enum

from .carrier import B4, TwoRail


# =============================================================================
# ORDER COMPARISONS
# =============================================================================

def leq_k(x: B4, y: B4) -> bool:
    """
    Knowledge order: x ≤_k y ⟺ x ⊆ y
    
    Information inclusion ordering.
    """
    return x.support <= y.support


def lt_k(x: B4, y: B4) -> bool:
    """Strict knowledge order: x <_k y"""
    return leq_k(x, y) and x != y


def leq_t(x: B4, y: B4) -> bool:
    """
    Truth order: x ≤_t y ⟺ t(x) ≤ t(y) ∧ f(y) ≤ f(x)
    
    Truth increases while falsity decreases.
    """
    ex = TwoRail.encode(x)
    ey = TwoRail.encode(y)
    return ex.t <= ey.t and ey.f <= ex.f


def lt_t(x: B4, y: B4) -> bool:
    """Strict truth order: x <_t y"""
    return leq_t(x, y) and x != y


def comparable_k(x: B4, y: B4) -> bool:
    """Check if x and y are comparable in ≤_k."""
    return leq_k(x, y) or leq_k(y, x)


def comparable_t(x: B4, y: B4) -> bool:
    """Check if x and y are comparable in ≤_t."""
    return leq_t(x, y) or leq_t(y, x)


# =============================================================================
# LATTICE OPERATIONS
# =============================================================================

def join_k(x: B4, y: B4) -> B4:
    """
    Knowledge join: x ⊕_k y = x ∪ y
    
    Merge information from both sources.
    """
    return B4.from_support(x.support | y.support)


def meet_k(x: B4, y: B4) -> B4:
    """
    Knowledge meet: x ⊗_k y = x ∩ y
    
    Refine to common information.
    """
    return B4.from_support(x.support & y.support)


def join_t(x: B4, y: B4) -> B4:
    """
    Truth join: x ∨_t y = sup_{≤_t}{x, y}
    
    In rail coordinates: (t∨t', f∧f')
    """
    ex = TwoRail.encode(x)
    ey = TwoRail.encode(y)
    
    t_result = max(ex.t, ey.t)
    f_result = min(ex.f, ey.f)
    
    return TwoRail(t_result, f_result).decode()


def meet_t(x: B4, y: B4) -> B4:
    """
    Truth meet: x ∧_t y = inf_{≤_t}{x, y}
    
    In rail coordinates: (t∧t', f∨f')
    """
    ex = TwoRail.encode(x)
    ey = TwoRail.encode(y)
    
    t_result = min(ex.t, ey.t)
    f_result = max(ex.f, ey.f)
    
    return TwoRail(t_result, f_result).decode()


# =============================================================================
# OPERATION ALIASES (Unicode-friendly)
# =============================================================================

# Knowledge lattice
oplus_k = join_k   # ⊕_k
otimes_k = meet_k  # ⊗_k

# Truth lattice  
or_t = join_t      # ∨_t
and_t = meet_t     # ∧_t


# =============================================================================
# LATTICE PROPERTIES
# =============================================================================

def is_lattice_k_bounded() -> bool:
    """Verify (B₄, ≤_k) is a bounded lattice."""
    all_values = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    
    # Check ⊥ is bottom
    if not all(leq_k(B4.BOT, x) for x in all_values):
        return False
    
    # Check ⊤ is top
    if not all(leq_k(x, B4.TOP) for x in all_values):
        return False
    
    return True


def is_lattice_t_bounded() -> bool:
    """Verify (B₄, ≤_t) is a bounded lattice."""
    all_values = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    
    # Check 0 is bottom
    if not all(leq_t(B4.ZERO, x) for x in all_values):
        return False
    
    # Check 1 is top
    if not all(leq_t(x, B4.ONE) for x in all_values):
        return False
    
    return True


def verify_distributivity_k() -> bool:
    """
    Verify distributivity in knowledge lattice.
    
    x ⊗_k (y ⊕_k z) = (x ⊗_k y) ⊕_k (x ⊗_k z)
    """
    all_values = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    
    for x in all_values:
        for y in all_values:
            for z in all_values:
                lhs = meet_k(x, join_k(y, z))
                rhs = join_k(meet_k(x, y), meet_k(x, z))
                if lhs != rhs:
                    return False
    return True


def verify_distributivity_t() -> bool:
    """
    Verify distributivity in truth lattice.
    
    x ∧_t (y ∨_t z) = (x ∧_t y) ∨_t (x ∧_t z)
    """
    all_values = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    
    for x in all_values:
        for y in all_values:
            for z in all_values:
                lhs = meet_t(x, join_t(y, z))
                rhs = join_t(meet_t(x, y), meet_t(x, z))
                if lhs != rhs:
                    return False
    return True


# =============================================================================
# BILATTICE STRUCTURE
# =============================================================================

@dataclass
class Bilattice:
    """
    The BIT4 bilattice (B₄, ≤_k, ≤_t).
    
    Interlaces two lattice structures:
    - Knowledge lattice (B₄, ⊕_k, ⊗_k) with ⊥ ≤_k ⊤
    - Truth lattice (B₄, ∨_t, ∧_t) with 0 ≤_t 1
    """
    
    @staticmethod
    def knowledge_bottom() -> B4:
        """Knowledge-least element: ⊥"""
        return B4.BOT
    
    @staticmethod
    def knowledge_top() -> B4:
        """Knowledge-greatest element: ⊤"""
        return B4.TOP
    
    @staticmethod
    def truth_bottom() -> B4:
        """Truth-least element: 0"""
        return B4.ZERO
    
    @staticmethod
    def truth_top() -> B4:
        """Truth-greatest element: 1"""
        return B4.ONE
    
    @staticmethod
    def atoms_k() -> List[B4]:
        """Atoms in knowledge order: {0, 1}"""
        return [B4.ZERO, B4.ONE]
    
    @staticmethod
    def atoms_t() -> List[B4]:
        """Atoms in truth order: {⊥, ⊤}"""
        return [B4.BOT, B4.TOP]
    
    @staticmethod
    def hasse_k() -> Dict[B4, List[B4]]:
        """Hasse diagram edges for ≤_k (covers)."""
        return {
            B4.BOT: [B4.ZERO, B4.ONE],
            B4.ZERO: [B4.TOP],
            B4.ONE: [B4.TOP],
            B4.TOP: []
        }
    
    @staticmethod
    def hasse_t() -> Dict[B4, List[B4]]:
        """Hasse diagram edges for ≤_t (covers)."""
        return {
            B4.ZERO: [B4.BOT, B4.TOP],
            B4.BOT: [B4.ONE],
            B4.TOP: [B4.ONE],
            B4.ONE: []
        }
    
    @staticmethod
    def rank_k(x: B4) -> int:
        """Height in knowledge lattice."""
        return {
            B4.BOT: 0,
            B4.ZERO: 1,
            B4.ONE: 1,
            B4.TOP: 2
        }[x]
    
    @staticmethod
    def rank_t(x: B4) -> int:
        """Height in truth lattice."""
        return {
            B4.ZERO: 0,
            B4.BOT: 1,
            B4.TOP: 1,
            B4.ONE: 2
        }[x]


# =============================================================================
# MONOTONICITY CHECKING
# =============================================================================

def is_monotone_k(f, domain: List[B4] = None) -> bool:
    """
    Check if f is ≤_k-monotone.
    
    x ≤_k y ⟹ f(x) ≤_k f(y)
    """
    if domain is None:
        domain = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    
    for x in domain:
        for y in domain:
            if leq_k(x, y):
                if not leq_k(f(x), f(y)):
                    return False
    return True


def is_monotone_t(f, domain: List[B4] = None) -> bool:
    """
    Check if f is ≤_t-monotone.
    
    x ≤_t y ⟹ f(x) ≤_t f(y)
    """
    if domain is None:
        domain = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    
    for x in domain:
        for y in domain:
            if leq_t(x, y):
                if not leq_t(f(x), f(y)):
                    return False
    return True


def is_antitone_k(f, domain: List[B4] = None) -> bool:
    """
    Check if f is ≤_k-antitone (order-reversing).
    
    x ≤_k y ⟹ f(y) ≤_k f(x)
    """
    if domain is None:
        domain = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    
    for x in domain:
        for y in domain:
            if leq_k(x, y):
                if not leq_k(f(y), f(x)):
                    return False
    return True


def is_antitone_t(f, domain: List[B4] = None) -> bool:
    """
    Check if f is ≤_t-antitone (order-reversing).
    
    x ≤_t y ⟹ f(y) ≤_t f(x)
    """
    if domain is None:
        domain = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    
    for x in domain:
        for y in domain:
            if leq_t(x, y):
                if not leq_t(f(y), f(x)):
                    return False
    return True


# =============================================================================
# OPERATION TABLES
# =============================================================================

def print_join_k_table() -> str:
    """Generate ⊕_k operation table."""
    values = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    header = "⊕_k | " + " ".join(v.glyph for v in values)
    sep = "-" * len(header)
    
    rows = []
    for x in values:
        row = f" {x.glyph}  | " + " ".join(join_k(x, y).glyph for y in values)
        rows.append(row)
    
    return header + "\n" + sep + "\n" + "\n".join(rows)


def print_meet_k_table() -> str:
    """Generate ⊗_k operation table."""
    values = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    header = "⊗_k | " + " ".join(v.glyph for v in values)
    sep = "-" * len(header)
    
    rows = []
    for x in values:
        row = f" {x.glyph}  | " + " ".join(meet_k(x, y).glyph for y in values)
        rows.append(row)
    
    return header + "\n" + sep + "\n" + "\n".join(rows)


def print_join_t_table() -> str:
    """Generate ∨_t operation table."""
    values = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    header = "∨_t | " + " ".join(v.glyph for v in values)
    sep = "-" * len(header)
    
    rows = []
    for x in values:
        row = f" {x.glyph}  | " + " ".join(join_t(x, y).glyph for y in values)
        rows.append(row)
    
    return header + "\n" + sep + "\n" + "\n".join(rows)


def print_meet_t_table() -> str:
    """Generate ∧_t operation table."""
    values = [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]
    header = "∧_t | " + " ".join(v.glyph for v in values)
    sep = "-" * len(header)
    
    rows = []
    for x in values:
        row = f" {x.glyph}  | " + " ".join(meet_t(x, y).glyph for y in values)
        rows.append(row)
    
    return header + "\n" + sep + "\n" + "\n".join(rows)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_orders() -> bool:
    """Validate orders module."""
    
    # Test knowledge order
    assert leq_k(B4.BOT, B4.BOT)
    assert leq_k(B4.BOT, B4.ZERO)
    assert leq_k(B4.BOT, B4.ONE)
    assert leq_k(B4.BOT, B4.TOP)
    assert leq_k(B4.ZERO, B4.TOP)
    assert leq_k(B4.ONE, B4.TOP)
    assert not leq_k(B4.TOP, B4.BOT)
    assert not leq_k(B4.ZERO, B4.ONE)  # Incomparable
    
    # Test truth order
    assert leq_t(B4.ZERO, B4.ZERO)
    assert leq_t(B4.ZERO, B4.BOT)
    assert leq_t(B4.ZERO, B4.TOP)
    assert leq_t(B4.ZERO, B4.ONE)
    assert leq_t(B4.BOT, B4.ONE)
    assert leq_t(B4.TOP, B4.ONE)
    assert not leq_t(B4.ONE, B4.ZERO)
    assert not leq_t(B4.BOT, B4.TOP)  # Incomparable
    
    # Test knowledge lattice operations
    assert join_k(B4.BOT, B4.ZERO) == B4.ZERO
    assert join_k(B4.ZERO, B4.ONE) == B4.TOP
    assert meet_k(B4.TOP, B4.ZERO) == B4.ZERO
    assert meet_k(B4.ZERO, B4.ONE) == B4.BOT
    
    # Test truth lattice operations
    assert join_t(B4.ZERO, B4.ONE) == B4.ONE
    assert join_t(B4.BOT, B4.TOP) == B4.ONE
    assert meet_t(B4.ZERO, B4.ONE) == B4.ZERO
    assert meet_t(B4.BOT, B4.TOP) == B4.ZERO
    
    # Verify bounded lattice properties
    assert is_lattice_k_bounded()
    assert is_lattice_t_bounded()
    
    # Verify distributivity
    assert verify_distributivity_k()
    assert verify_distributivity_t()
    
    # Test bilattice
    bl = Bilattice()
    assert bl.knowledge_bottom() == B4.BOT
    assert bl.knowledge_top() == B4.TOP
    assert bl.truth_bottom() == B4.ZERO
    assert bl.truth_top() == B4.ONE
    
    return True


if __name__ == "__main__":
    print("Validating BIT4 Orders...")
    assert validate_orders()
    print("✓ Orders module validated")
    
    print("\n--- Operation Tables ---")
    print("\n" + print_join_k_table())
    print("\n" + print_meet_k_table())
    print("\n" + print_join_t_table())
    print("\n" + print_meet_t_table())
