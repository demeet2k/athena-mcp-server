"""
ATHENA OS - GLOBAL INFORMATION NETWORK
======================================
Valuation: Four-Valued Paraconsistent Logic

From GLOBAL_INFORMATION_NETWORK.docx §3:

THE FOUR-VALUED LOGIC (V):
    
    V = {T, F, B, U}
    
    T: True       - sufficient positive evidence, no negative
    F: False      - sufficient negative evidence, no positive
    B: Both       - overdetermined, paradox, contradiction
    U: Undetermined - void, insufficient determination

PARACONSISTENT SEMANTICS:
    - Contradictions do not imply arbitrary conclusions
    - B-valued propositions can be designated for action
    - U-valued propositions signal incomplete information
    
DESIGNATED SET:
    D ⊆ V, typically D = {T, B}
    Allows controlled coexistence of contradictory constraints
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Callable
from enum import Enum
import numpy as np


# =============================================================================
# FOUR-VALUED LOGIC
# =============================================================================

class V4(Enum):
    """
    The four-valued logic V = {T, F, B, U}.
    
    This is distinct from BIT4 in interpretation:
    - BIT4: information/knowledge lattice
    - V4: paraconsistent truth valuation for decision logic
    """
    
    T = "true"           # True: E+(φ) ∧ ¬E-(φ)
    F = "false"          # False: E-(φ) ∧ ¬E+(φ)
    B = "both"           # Both: E+(φ) ∧ E-(φ) - overdetermined
    U = "undetermined"   # Undetermined: ¬E+(φ) ∧ ¬E-(φ)
    
    @property
    def is_designated(self) -> bool:
        """Check if value is in default designated set {T, B}."""
        return self in {V4.T, V4.B}
    
    @property
    def has_positive_evidence(self) -> bool:
        """E+(φ) - positive evidence exists."""
        return self in {V4.T, V4.B}
    
    @property
    def has_negative_evidence(self) -> bool:
        """E-(φ) - negative evidence exists."""
        return self in {V4.F, V4.B}
    
    @property
    def is_determined(self) -> bool:
        """Has at least some evidence."""
        return self != V4.U
    
    @property
    def is_consistent(self) -> bool:
        """Not overdetermined (not Both)."""
        return self != V4.B


# =============================================================================
# LOGICAL OPERATIONS
# =============================================================================

def v4_negation(v: V4) -> V4:
    """
    Negation in V4.
    
    ¬T = F, ¬F = T
    ¬B = B (contradiction remains)
    ¬U = U (indeterminacy remains)
    """
    if v == V4.T:
        return V4.F
    elif v == V4.F:
        return V4.T
    else:
        return v  # B and U are self-dual under negation


def v4_conjunction(a: V4, b: V4) -> V4:
    """
    Conjunction (∧) in V4 - Kleene strong.
    
    Truth table follows "both must support":
    - T ∧ T = T
    - F ∧ _ = F (F dominates)
    - B ∧ T = B, B ∧ B = B
    - U ∧ T = U, U ∧ U = U
    """
    # F dominates
    if a == V4.F or b == V4.F:
        return V4.F
    
    # Both T yields T
    if a == V4.T and b == V4.T:
        return V4.T
    
    # B propagates
    if a == V4.B or b == V4.B:
        return V4.B
    
    # U propagates
    return V4.U


def v4_disjunction(a: V4, b: V4) -> V4:
    """
    Disjunction (∨) in V4 - Kleene strong.
    
    Truth table follows "at least one supports":
    - T ∨ _ = T (T dominates)
    - F ∨ F = F
    - B ∨ F = B, B ∨ B = B
    - U ∨ F = U, U ∨ U = U
    """
    # T dominates
    if a == V4.T or b == V4.T:
        return V4.T
    
    # Both F yields F
    if a == V4.F and b == V4.F:
        return V4.F
    
    # B propagates
    if a == V4.B or b == V4.B:
        return V4.B
    
    # U propagates
    return V4.U


def v4_implication(a: V4, b: V4) -> V4:
    """
    Material implication: a → b ≡ ¬a ∨ b
    """
    return v4_disjunction(v4_negation(a), b)


# =============================================================================
# EVIDENCE-BASED VALUATION
# =============================================================================

@dataclass
class Evidence:
    """
    Evidence for a proposition.
    
    E+(φ): positive evidence strength [0, 1]
    E-(φ): negative evidence strength [0, 1]
    """
    
    positive: float = 0.0   # E+
    negative: float = 0.0   # E-
    
    threshold: float = 0.5  # Threshold for "sufficient" evidence
    
    def __post_init__(self):
        self.positive = max(0.0, min(1.0, self.positive))
        self.negative = max(0.0, min(1.0, self.negative))
    
    @property
    def valuation(self) -> V4:
        """Compute V4 valuation from evidence."""
        has_pos = self.positive >= self.threshold
        has_neg = self.negative >= self.threshold
        
        if has_pos and has_neg:
            return V4.B  # Both - overdetermined
        elif has_pos:
            return V4.T  # True
        elif has_neg:
            return V4.F  # False
        else:
            return V4.U  # Undetermined
    
    def update(self, pos_delta: float = 0.0, neg_delta: float = 0.0) -> 'Evidence':
        """Update evidence with new observations."""
        return Evidence(
            positive=self.positive + pos_delta,
            negative=self.negative + neg_delta,
            threshold=self.threshold
        )
    
    @property
    def conflict(self) -> float:
        """Measure of evidence conflict (0 = no conflict, 1 = max)."""
        return min(self.positive, self.negative)
    
    @property
    def uncertainty(self) -> float:
        """Measure of uncertainty (0 = certain, 1 = unknown)."""
        return 1.0 - max(self.positive, self.negative)


# =============================================================================
# VALUATION FUNCTION
# =============================================================================

@dataclass
class Valuation:
    """
    A valuation function v: P → V
    
    Maps propositions to four-valued truth values.
    """
    
    assignments: Dict[str, V4] = field(default_factory=dict)
    evidence: Dict[str, Evidence] = field(default_factory=dict)
    designated_set: Set[V4] = field(default_factory=lambda: {V4.T, V4.B})
    
    def __getitem__(self, prop: str) -> V4:
        """Get valuation of proposition."""
        if prop in self.evidence:
            return self.evidence[prop].valuation
        return self.assignments.get(prop, V4.U)
    
    def __setitem__(self, prop: str, value: V4) -> None:
        """Set valuation directly."""
        self.assignments[prop] = value
    
    def set_evidence(self, prop: str, positive: float, negative: float) -> None:
        """Set evidence-based valuation."""
        self.evidence[prop] = Evidence(positive=positive, negative=negative)
    
    def is_designated(self, prop: str) -> bool:
        """Check if proposition is designated (accepted for action)."""
        return self[prop] in self.designated_set
    
    def get_contradictions(self) -> List[str]:
        """Get all B-valued propositions."""
        result = []
        for prop in set(self.assignments.keys()) | set(self.evidence.keys()):
            if self[prop] == V4.B:
                result.append(prop)
        return result
    
    def get_undetermined(self) -> List[str]:
        """Get all U-valued propositions."""
        result = []
        for prop in set(self.assignments.keys()) | set(self.evidence.keys()):
            if self[prop] == V4.U:
                result.append(prop)
        return result
    
    def evaluate(self, formula: str) -> V4:
        """
        Evaluate a formula string.
        
        Supports: NOT, AND, OR, IMPLIES, and proposition names.
        Simple recursive descent parser.
        """
        formula = formula.strip()
        
        # Handle NOT
        if formula.startswith("NOT "):
            inner = formula[4:]
            return v4_negation(self.evaluate(inner))
        
        # Handle binary operators (simple parsing)
        for op, func in [(" AND ", v4_conjunction), 
                         (" OR ", v4_disjunction),
                         (" IMPLIES ", v4_implication)]:
            if op in formula:
                parts = formula.split(op, 1)
                left = self.evaluate(parts[0])
                right = self.evaluate(parts[1])
                return func(left, right)
        
        # Handle parentheses
        if formula.startswith("(") and formula.endswith(")"):
            return self.evaluate(formula[1:-1])
        
        # Base case: proposition lookup
        return self[formula]


# =============================================================================
# PARADOX LIFT OPERATOR
# =============================================================================

@dataclass
class ParadoxLift:
    """
    The Lift operator P that converts bivalent paradoxes
    into four-valued navigational signals.
    
    Instead of "resolve by exclusion", we "classify by evidence".
    Contradiction becomes a signal for sector rotation or
    tunnel selection, not system failure.
    """
    
    def lift(self, classical_value: bool, 
             contradicted: bool = False,
             underdetermined: bool = False) -> V4:
        """
        Lift classical valuation to V4.
        
        Args:
            classical_value: The classical T/F assignment
            contradicted: Whether there's contradicting evidence
            underdetermined: Whether evidence is insufficient
        """
        if underdetermined:
            return V4.U
        
        if contradicted:
            return V4.B
        
        return V4.T if classical_value else V4.F
    
    def route_paradox(self, prop: str, valuation: Valuation) -> str:
        """
        Route a paradox (B-valued proposition) to resolution.
        
        Returns routing instruction.
        """
        v = valuation[prop]
        
        if v == V4.B:
            return "SECTOR_ROTATION"  # Cross-sector resolution
        elif v == V4.U:
            return "INFORMATION_GATHER"  # Need more evidence
        else:
            return "PROCEED"  # No special routing needed
    
    def tension_contribution(self, valuation: Valuation) -> float:
        """
        Compute paradox tension contribution from valuation.
        
        E_tension = Σ conflict(φ) for all propositions
        """
        tension = 0.0
        
        for prop in set(valuation.assignments.keys()) | set(valuation.evidence.keys()):
            v = valuation[prop]
            if v == V4.B:
                tension += 1.0
                if prop in valuation.evidence:
                    tension += valuation.evidence[prop].conflict
            elif v == V4.U:
                tension += 0.5  # Undetermined also contributes
        
        return tension


# =============================================================================
# INFERENCE ENGINE
# =============================================================================

@dataclass
class ParaconsistentInference:
    """
    Paraconsistent inference engine.
    
    Key property: Contradictions do not explode.
    From A and ¬A, we cannot derive arbitrary B.
    """
    
    valuation: Valuation = field(default_factory=Valuation)
    
    def entails(self, premises: List[str], conclusion: str) -> V4:
        """
        Check if premises entail conclusion in paraconsistent logic.
        
        Premises are conjoined, then implication to conclusion evaluated.
        """
        if not premises:
            return self.valuation[conclusion]
        
        # Conjoin premises
        conjoined = premises[0]
        for p in premises[1:]:
            conjoined = f"({conjoined}) AND ({p})"
        
        # Evaluate implication
        implication = f"({conjoined}) IMPLIES ({conclusion})"
        return self.valuation.evaluate(implication)
    
    def is_explosive(self, prop: str) -> bool:
        """
        Check if adding prop and ¬prop would cause explosion.
        
        In classical logic, this always returns True.
        In our paraconsistent logic, this returns False.
        """
        # We explicitly prevent explosion
        return False
    
    def consistent_subset(self, props: List[str]) -> List[str]:
        """
        Find maximal consistent subset of propositions.
        
        Removes B-valued propositions that create inconsistency.
        """
        consistent = []
        
        for prop in props:
            v = self.valuation[prop]
            if v != V4.B:
                consistent.append(prop)
        
        return consistent
    
    def resolve_to_classical(self, prop: str) -> Optional[bool]:
        """
        Attempt to resolve V4 value to classical boolean.
        
        Returns None if not resolvable (B or U).
        """
        v = self.valuation[prop]
        
        if v == V4.T:
            return True
        elif v == V4.F:
            return False
        else:
            return None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_valuation() -> bool:
    """Validate valuation module."""
    
    # Test V4 values
    assert V4.T.is_designated
    assert V4.B.is_designated
    assert not V4.F.is_designated
    assert not V4.U.is_designated
    
    # Test negation
    assert v4_negation(V4.T) == V4.F
    assert v4_negation(V4.F) == V4.T
    assert v4_negation(V4.B) == V4.B
    assert v4_negation(V4.U) == V4.U
    
    # Test conjunction
    assert v4_conjunction(V4.T, V4.T) == V4.T
    assert v4_conjunction(V4.T, V4.F) == V4.F
    assert v4_conjunction(V4.T, V4.B) == V4.B
    assert v4_conjunction(V4.T, V4.U) == V4.U
    
    # Test disjunction
    assert v4_disjunction(V4.T, V4.F) == V4.T
    assert v4_disjunction(V4.F, V4.F) == V4.F
    assert v4_disjunction(V4.F, V4.B) == V4.B
    
    # Test Evidence
    ev = Evidence(positive=0.7, negative=0.2)
    assert ev.valuation == V4.T
    
    ev_both = Evidence(positive=0.7, negative=0.7)
    assert ev_both.valuation == V4.B
    
    ev_none = Evidence(positive=0.2, negative=0.2)
    assert ev_none.valuation == V4.U
    
    # Test Valuation
    v = Valuation()
    v["p"] = V4.T
    v["q"] = V4.F
    v["r"] = V4.B
    
    assert v["p"] == V4.T
    assert v.is_designated("p")
    assert not v.is_designated("q")
    assert v.is_designated("r")  # B is designated
    
    # Test formula evaluation
    assert v.evaluate("p AND q") == V4.F
    assert v.evaluate("p OR q") == V4.T
    assert v.evaluate("NOT q") == V4.T
    
    # Test ParadoxLift
    lift = ParadoxLift()
    assert lift.lift(True, contradicted=False) == V4.T
    assert lift.lift(True, contradicted=True) == V4.B
    assert lift.lift(False, underdetermined=True) == V4.U
    
    # Test inference
    engine = ParaconsistentInference(valuation=v)
    assert not engine.is_explosive("p")  # Key: no explosion
    
    return True


if __name__ == "__main__":
    print("Validating Four-Valued Logic...")
    assert validate_valuation()
    print("✓ Valuation module validated")
