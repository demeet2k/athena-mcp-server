"""
ATHENA OS - Bilattice Logic: The Semantic Codomain V
====================================================
The four-valued truth structure for handling contradiction and
indeterminacy.

We reject classical bivalence. The semantic logic maps propositions
not to {0, 1} but to a structured codomain V.

V = {T, F, B, U}
- T: True (confirmed)
- F: False (refuted)
- B: Both (paradox/contradiction/overdetermined)
- U: Undetermined (void/gap/underdetermined)

This forms a BILATTICE structure where:
- B represents overdetermination (contradiction)
- U represents underdetermination (gap)

Contradiction is not an error; it is a conserved charge.
The system forbids "deleting" contradiction. If ν(φ) = B,
this tension must be stored or routed, not ignored.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import numpy as np


# =============================================================================
# FOUR-VALUED TRUTH
# =============================================================================

class TruthValue(IntEnum):
    """
    The four truth values forming the bilattice.
    
    Arranged in a lattice with two orderings:
    1. Truth ordering: F < U < T, F < B < T (classical true/false)
    2. Knowledge ordering: U < F < B, U < T < B (information content)
    """
    FALSE = 0  # F: Refuted
    TRUE = 1   # T: Confirmed
    BOTH = 2   # B: Paradox (both true and false)
    UNDER = 3  # U: Undetermined (neither true nor false)
    
    @property
    def symbol(self) -> str:
        symbols = {
            TruthValue.FALSE: '⊥',
            TruthValue.TRUE: '⊤',
            TruthValue.BOTH: '⊕',
            TruthValue.UNDER: '○'
        }
        return symbols[self]
    
    @property
    def name_full(self) -> str:
        names = {
            TruthValue.FALSE: 'False',
            TruthValue.TRUE: 'True',
            TruthValue.BOTH: 'Both (Paradox)',
            TruthValue.UNDER: 'Undetermined (Void)'
        }
        return names[self]
    
    def is_classical(self) -> bool:
        """Check if value is classical (T or F)."""
        return self in (TruthValue.TRUE, TruthValue.FALSE)
    
    def is_overdetermined(self) -> bool:
        """Check if value is overdetermined (paradox)."""
        return self == TruthValue.BOTH
    
    def is_underdetermined(self) -> bool:
        """Check if value is underdetermined (void)."""
        return self == TruthValue.UNDER


# =============================================================================
# BILATTICE OPERATIONS
# =============================================================================

class Bilattice:
    """
    The bilattice structure over V = {T, F, B, U}.
    
    Two lattice orderings:
    1. Truth ordering (≤_t): measures truth content
       F ≤_t U ≤_t T, F ≤_t B ≤_t T
       
    2. Knowledge ordering (≤_k): measures information content
       U ≤_k F ≤_k B, U ≤_k T ≤_k B
       
    Operations:
    - meet_t, join_t: Truth lattice operations
    - meet_k, join_k: Knowledge lattice operations
    - negation: Classical negation (swaps T↔F, preserves B,U)
    - conflation: Swaps B↔U
    """
    
    # Truth ordering: more true is higher
    TRUTH_ORDER = {
        TruthValue.FALSE: 0,
        TruthValue.UNDER: 1,
        TruthValue.TRUE: 2,
        TruthValue.BOTH: 1,  # B is between F and T
    }
    
    # Knowledge ordering: more information is higher
    KNOWLEDGE_ORDER = {
        TruthValue.UNDER: 0,
        TruthValue.FALSE: 1,
        TruthValue.TRUE: 1,
        TruthValue.BOTH: 2,  # B has maximum information
    }
    
    @staticmethod
    def negation(v: TruthValue) -> TruthValue:
        """
        Classical negation: ¬v
        
        ¬T = F, ¬F = T, ¬B = B, ¬U = U
        """
        if v == TruthValue.TRUE:
            return TruthValue.FALSE
        elif v == TruthValue.FALSE:
            return TruthValue.TRUE
        else:
            return v  # B and U are self-dual under negation
    
    @staticmethod
    def conflation(v: TruthValue) -> TruthValue:
        """
        Conflation: swaps overdetermination and underdetermination.
        
        -B = U, -U = B, -T = T, -F = F
        """
        if v == TruthValue.BOTH:
            return TruthValue.UNDER
        elif v == TruthValue.UNDER:
            return TruthValue.BOTH
        else:
            return v
    
    @staticmethod
    def meet_t(a: TruthValue, b: TruthValue) -> TruthValue:
        """
        Truth meet (conjunction in truth ordering): a ∧_t b
        
        Takes the "less true" of the two values.
        """
        # Truth table for meet_t
        table = {
            (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.TRUE, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.TRUE, TruthValue.UNDER): TruthValue.UNDER,
            (TruthValue.FALSE, TruthValue.TRUE): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.BOTH): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.UNDER): TruthValue.FALSE,
            (TruthValue.BOTH, TruthValue.TRUE): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.BOTH, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.UNDER): TruthValue.FALSE,
            (TruthValue.UNDER, TruthValue.TRUE): TruthValue.UNDER,
            (TruthValue.UNDER, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.UNDER, TruthValue.BOTH): TruthValue.FALSE,
            (TruthValue.UNDER, TruthValue.UNDER): TruthValue.UNDER,
        }
        return table[(a, b)]
    
    @staticmethod
    def join_t(a: TruthValue, b: TruthValue) -> TruthValue:
        """
        Truth join (disjunction in truth ordering): a ∨_t b
        
        Takes the "more true" of the two values.
        """
        table = {
            (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.FALSE): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.BOTH): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.UNDER): TruthValue.TRUE,
            (TruthValue.FALSE, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.FALSE, TruthValue.UNDER): TruthValue.UNDER,
            (TruthValue.BOTH, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.BOTH, TruthValue.FALSE): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.UNDER): TruthValue.BOTH,
            (TruthValue.UNDER, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.UNDER, TruthValue.FALSE): TruthValue.UNDER,
            (TruthValue.UNDER, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.UNDER, TruthValue.UNDER): TruthValue.UNDER,
        }
        return table[(a, b)]
    
    @staticmethod
    def meet_k(a: TruthValue, b: TruthValue) -> TruthValue:
        """
        Knowledge meet (consensus): a ⊗ b
        
        Takes the "less informed" of the two values.
        """
        table = {
            (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.FALSE): TruthValue.UNDER,
            (TruthValue.TRUE, TruthValue.BOTH): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.UNDER): TruthValue.UNDER,
            (TruthValue.FALSE, TruthValue.TRUE): TruthValue.UNDER,
            (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.BOTH): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.UNDER): TruthValue.UNDER,
            (TruthValue.BOTH, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.BOTH, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.BOTH, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.UNDER): TruthValue.UNDER,
            (TruthValue.UNDER, TruthValue.TRUE): TruthValue.UNDER,
            (TruthValue.UNDER, TruthValue.FALSE): TruthValue.UNDER,
            (TruthValue.UNDER, TruthValue.BOTH): TruthValue.UNDER,
            (TruthValue.UNDER, TruthValue.UNDER): TruthValue.UNDER,
        }
        return table[(a, b)]
    
    @staticmethod
    def join_k(a: TruthValue, b: TruthValue) -> TruthValue:
        """
        Knowledge join (gullibility): a ⊕ b
        
        Takes the "more informed" of the two values.
        """
        table = {
            (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.FALSE): TruthValue.BOTH,
            (TruthValue.TRUE, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.TRUE, TruthValue.UNDER): TruthValue.TRUE,
            (TruthValue.FALSE, TruthValue.TRUE): TruthValue.BOTH,
            (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.FALSE, TruthValue.UNDER): TruthValue.FALSE,
            (TruthValue.BOTH, TruthValue.TRUE): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.FALSE): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.UNDER): TruthValue.BOTH,
            (TruthValue.UNDER, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.UNDER, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.UNDER, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.UNDER, TruthValue.UNDER): TruthValue.UNDER,
        }
        return table[(a, b)]


# =============================================================================
# PARADOX OPERATOR
# =============================================================================

@dataclass
class Evidence:
    """Evidence for a proposition."""
    support: float = 0.0    # E+ (evidence for)
    refutation: float = 0.0  # E- (evidence against)
    
    def to_truth_value(self, threshold: float = 0.5) -> TruthValue:
        """
        Map evidence to four-valued truth.
        
        Based on support (E+) and refutation (E-):
        - High E+, Low E-  → TRUE
        - Low E+, High E-  → FALSE
        - High E+, High E- → BOTH (paradox)
        - Low E+, Low E-   → UNDER (void)
        """
        high_support = self.support >= threshold
        high_refute = self.refutation >= threshold
        
        if high_support and not high_refute:
            return TruthValue.TRUE
        elif not high_support and high_refute:
            return TruthValue.FALSE
        elif high_support and high_refute:
            return TruthValue.BOTH
        else:
            return TruthValue.UNDER


class ParadoxOperator:
    """
    The Paradox Operator P.
    
    Maps bivalent predicates to four-valued semantics based on
    evidence support and refutation.
    
    P: Pred(M) → V^M
    
    Conservation: The system forbids "deleting" contradiction.
    If ν(φ) = B, this tension must be stored or routed, not ignored.
    """
    
    def __init__(self):
        self.paradox_ledger: List[Tuple[str, float]] = []
        self.total_tension: float = 0.0
    
    def evaluate(self, proposition: str, evidence: Evidence) -> TruthValue:
        """Evaluate a proposition given evidence."""
        value = evidence.to_truth_value()
        
        # Log paradoxes (conserve tension)
        if value == TruthValue.BOTH:
            tension = evidence.support * evidence.refutation
            self.paradox_ledger.append((proposition, tension))
            self.total_tension += tension
        
        return value
    
    def conserved_tension(self) -> float:
        """Get total conserved paradox tension."""
        return self.total_tension
    
    def route_paradox(self, proposition: str, target_sector: str) -> bool:
        """
        Route a paradox to another sector for resolution.
        
        Paradoxes can be:
        - Stored (Water sector - memory)
        - Randomized (Fire sector - probability)
        - Recursed (Air sector - meta-level)
        - Constrained (Earth sector - structural resolution)
        """
        # In practice, this would transform the paradox
        return True


# =============================================================================
# SEMANTIC CODOMAIN V
# =============================================================================

@dataclass
class SemanticCodomain:
    """
    The Semantic Codomain V = {T, F, B, U}.
    
    The complete truth structure for the system.
    """
    
    bilattice: Bilattice = field(default_factory=Bilattice)
    paradox_op: ParadoxOperator = field(default_factory=ParadoxOperator)
    
    # Proposition valuations
    valuations: Dict[str, TruthValue] = field(default_factory=dict)
    
    def assign(self, prop: str, value: TruthValue) -> None:
        """Assign a truth value to a proposition."""
        self.valuations[prop] = value
    
    def evaluate_evidence(self, prop: str, evidence: Evidence) -> TruthValue:
        """Evaluate proposition from evidence."""
        value = self.paradox_op.evaluate(prop, evidence)
        self.valuations[prop] = value
        return value
    
    def query(self, prop: str) -> Optional[TruthValue]:
        """Query truth value of proposition."""
        return self.valuations.get(prop)
    
    def conjunction(self, prop1: str, prop2: str) -> TruthValue:
        """Compute conjunction (truth meet)."""
        v1 = self.valuations.get(prop1, TruthValue.UNDER)
        v2 = self.valuations.get(prop2, TruthValue.UNDER)
        return self.bilattice.meet_t(v1, v2)
    
    def disjunction(self, prop1: str, prop2: str) -> TruthValue:
        """Compute disjunction (truth join)."""
        v1 = self.valuations.get(prop1, TruthValue.UNDER)
        v2 = self.valuations.get(prop2, TruthValue.UNDER)
        return self.bilattice.join_t(v1, v2)
    
    def negate(self, prop: str) -> TruthValue:
        """Negate a proposition."""
        v = self.valuations.get(prop, TruthValue.UNDER)
        return self.bilattice.negation(v)
    
    def consensus(self, prop1: str, prop2: str) -> TruthValue:
        """Compute consensus (knowledge meet)."""
        v1 = self.valuations.get(prop1, TruthValue.UNDER)
        v2 = self.valuations.get(prop2, TruthValue.UNDER)
        return self.bilattice.meet_k(v1, v2)
    
    def accept_both(self, prop1: str, prop2: str) -> TruthValue:
        """Accept both sources (knowledge join)."""
        v1 = self.valuations.get(prop1, TruthValue.UNDER)
        v2 = self.valuations.get(prop2, TruthValue.UNDER)
        return self.bilattice.join_k(v1, v2)
    
    def paradox_count(self) -> int:
        """Count paradoxical propositions."""
        return sum(1 for v in self.valuations.values() if v == TruthValue.BOTH)
    
    def void_count(self) -> int:
        """Count undetermined propositions."""
        return sum(1 for v in self.valuations.values() if v == TruthValue.UNDER)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_bilattice() -> bool:
    """Validate bilattice logic."""
    
    # Test truth values
    assert len(TruthValue) == 4
    assert TruthValue.TRUE.symbol == '⊤'
    assert TruthValue.BOTH.is_overdetermined()
    assert TruthValue.UNDER.is_underdetermined()
    
    # Test negation
    assert Bilattice.negation(TruthValue.TRUE) == TruthValue.FALSE
    assert Bilattice.negation(TruthValue.FALSE) == TruthValue.TRUE
    assert Bilattice.negation(TruthValue.BOTH) == TruthValue.BOTH
    assert Bilattice.negation(TruthValue.UNDER) == TruthValue.UNDER
    
    # Test conflation
    assert Bilattice.conflation(TruthValue.BOTH) == TruthValue.UNDER
    assert Bilattice.conflation(TruthValue.UNDER) == TruthValue.BOTH
    
    # Test truth meet/join
    assert Bilattice.meet_t(TruthValue.TRUE, TruthValue.TRUE) == TruthValue.TRUE
    assert Bilattice.meet_t(TruthValue.TRUE, TruthValue.FALSE) == TruthValue.FALSE
    assert Bilattice.join_t(TruthValue.TRUE, TruthValue.FALSE) == TruthValue.TRUE
    
    # Test knowledge meet/join
    assert Bilattice.join_k(TruthValue.TRUE, TruthValue.FALSE) == TruthValue.BOTH
    assert Bilattice.meet_k(TruthValue.TRUE, TruthValue.FALSE) == TruthValue.UNDER
    
    # Test evidence
    e1 = Evidence(support=0.8, refutation=0.1)
    assert e1.to_truth_value() == TruthValue.TRUE
    
    e2 = Evidence(support=0.1, refutation=0.8)
    assert e2.to_truth_value() == TruthValue.FALSE
    
    e3 = Evidence(support=0.8, refutation=0.8)
    assert e3.to_truth_value() == TruthValue.BOTH
    
    e4 = Evidence(support=0.1, refutation=0.1)
    assert e4.to_truth_value() == TruthValue.UNDER
    
    # Test semantic codomain
    V = SemanticCodomain()
    V.assign("p", TruthValue.TRUE)
    V.assign("q", TruthValue.FALSE)
    
    assert V.conjunction("p", "q") == TruthValue.FALSE
    assert V.disjunction("p", "q") == TruthValue.TRUE
    assert V.negate("p") == TruthValue.FALSE
    assert V.accept_both("p", "q") == TruthValue.BOTH
    
    # Test paradox conservation
    V.evaluate_evidence("r", Evidence(0.9, 0.9))
    assert V.paradox_count() == 1
    assert V.paradox_op.total_tension > 0
    
    return True


if __name__ == "__main__":
    print("Validating Bilattice Logic...")
    assert validate_bilattice()
    print("✓ Bilattice Logic validated")
    
    # Demo
    print("\n=== Bilattice Demo ===")
    
    print("\nTruth Values:")
    for v in TruthValue:
        print(f"  {v.symbol} {v.name_full}")
    
    print("\nBilattice Operations:")
    print(f"  T ∧_t F = {Bilattice.meet_t(TruthValue.TRUE, TruthValue.FALSE).symbol}")
    print(f"  T ∨_t F = {Bilattice.join_t(TruthValue.TRUE, TruthValue.FALSE).symbol}")
    print(f"  T ⊕ F = {Bilattice.join_k(TruthValue.TRUE, TruthValue.FALSE).symbol} (paradox!)")
    print(f"  T ⊗ F = {Bilattice.meet_k(TruthValue.TRUE, TruthValue.FALSE).symbol} (void!)")
    
    print("\n=== Evidence Mapping ===")
    cases = [
        ("high support, low refute", Evidence(0.8, 0.2)),
        ("low support, high refute", Evidence(0.2, 0.8)),
        ("high both (paradox)", Evidence(0.8, 0.8)),
        ("low both (void)", Evidence(0.2, 0.2)),
    ]
    for name, ev in cases:
        print(f"  {name}: {ev.to_truth_value().name_full}")
