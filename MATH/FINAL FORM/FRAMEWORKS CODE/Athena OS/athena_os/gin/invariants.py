"""
ATHENA OS - GLOBAL INFORMATION NETWORK
======================================
Invariants: Conservation Laws and Global Constraints

From GLOBAL_INFORMATION_NETWORK.docx §I.2:

GLOBAL INVARIANTS:
    Axioms of admissibility that all operators must preserve.

CONSERVATION OF INFORMATION (Axiom I.1):
    I: M → R≥0
    I(U(m)) = I(m) for all admissible evolution U
    
    Information is a conserved quantity under admissible evolution.

CONSERVATION OF PARADOX TENSION (Definition I.4):
    E_tension: M → R≥0
    
    Measures irreducible incompatibility of constraints.
    E_tension(m) = 0 iff all constraints jointly satisfiable.
    
    Paradox tension must be carried, redistributed, or transmuted,
    but not eliminated by fiat.

KARMA TENSOR:
    K_μν(t): Accumulates residuals from action-constraint interactions.
    Storage crisis when Σ Δ Store(t) → ∞
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
import numpy as np

from .valuation import V4, Valuation


# =============================================================================
# INFORMATION FUNCTIONAL
# =============================================================================

@dataclass
class InformationFunctional:
    """
    I: M → R≥0 - Information functional.
    
    Conserved under admissible evolution.
    Constrains chart-to-chart translations.
    """
    
    dim: int = 4
    
    # Method for computing information content
    method: str = "entropy"  # "entropy", "fisher", "complexity"
    
    def __call__(self, state: np.ndarray) -> float:
        """Compute information content at state."""
        if self.method == "entropy":
            return self._shannon_entropy(state)
        elif self.method == "fisher":
            return self._fisher_information(state)
        elif self.method == "complexity":
            return self._kolmogorov_complexity(state)
        return 0.0
    
    def _shannon_entropy(self, state: np.ndarray) -> float:
        """
        Shannon entropy of state distribution.
        
        H(p) = -Σ p_i log(p_i)
        """
        # Normalize state to probability distribution
        probs = np.abs(state) / (np.sum(np.abs(state)) + 1e-10)
        
        # Compute entropy
        entropy = 0.0
        for p in probs:
            if p > 1e-10:
                entropy -= p * np.log(p)
        
        return entropy
    
    def _fisher_information(self, state: np.ndarray) -> float:
        """
        Fisher information (curvature of likelihood).
        
        Approximated by gradient norm.
        """
        # Use gradient norm as proxy
        gradient = np.gradient(state)
        return float(np.sum(gradient ** 2))
    
    def _kolmogorov_complexity(self, state: np.ndarray) -> float:
        """
        Kolmogorov complexity approximation.
        
        Uses compression ratio as proxy.
        """
        # Simplified: use number of distinct values
        unique = len(np.unique(np.round(state, 3)))
        return float(unique) / len(state)
    
    def is_conserved(self, state_before: np.ndarray, 
                    state_after: np.ndarray,
                    tolerance: float = 0.01) -> bool:
        """Check if information is conserved through transition."""
        i_before = self(state_before)
        i_after = self(state_after)
        return abs(i_before - i_after) < tolerance
    
    def conservation_violation(self, state_before: np.ndarray,
                               state_after: np.ndarray) -> float:
        """Measure conservation violation magnitude."""
        return abs(self(state_before) - self(state_after))


# =============================================================================
# PARADOX TENSION FUNCTIONAL
# =============================================================================

@dataclass
class ParadoxTension:
    """
    E_tension: M → R≥0 - Paradox tension functional.
    
    Measures irreducible incompatibility of constraints.
    E_tension(m) = 0 iff all constraints jointly satisfiable.
    
    Conservation: paradox tension cannot be eliminated, only
    redistributed or transmuted through allowable transformations.
    """
    
    def __call__(self, valuation: Valuation) -> float:
        """
        Compute paradox tension from valuation.
        
        Tension = Σ (B-values) + 0.5 Σ (U-values)
        """
        tension = 0.0
        
        # Count B-valued propositions (contradictions)
        contradictions = valuation.get_contradictions()
        tension += len(contradictions)
        
        # Add evidence conflict measure
        for prop in contradictions:
            if prop in valuation.evidence:
                tension += valuation.evidence[prop].conflict
        
        # Add U-valued propositions (indeterminacy)
        undetermined = valuation.get_undetermined()
        tension += 0.5 * len(undetermined)
        
        return tension
    
    def is_zero(self, valuation: Valuation) -> bool:
        """Check if tension is zero (all constraints satisfiable)."""
        return self(valuation) < 1e-10
    
    def redistribution_valid(self, tension_before: float,
                            tension_after: float,
                            tolerance: float = 0.01) -> bool:
        """
        Check if redistribution is valid.
        
        Tension can be redistributed but total should be conserved
        or decreased (through legitimate resolution).
        """
        return tension_after <= tension_before + tolerance
    
    def transmutation_cost(self, reduction: float) -> float:
        """
        Compute cost of transmuting tension.
        
        Legitimate reduction requires work/transformation.
        """
        # Quadratic cost for reduction
        return reduction ** 2


# =============================================================================
# KARMA TENSOR
# =============================================================================

@dataclass
class KarmaTensor:
    """
    K_μν(t): Karma tensor - accumulated residuals.
    
    Tracks action-constraint interaction residuals.
    
    Components:
    - Sanchita (S_μν): Accumulated/stored karma
    - Prarabdha (P_μν): Active/manifesting karma
    - Kriyamana (K_μν): Current action karma
    """
    
    dim: int = 4
    
    # Tensor components
    sanchita: np.ndarray = field(default_factory=lambda: np.zeros((4, 4)))
    prarabdha: np.ndarray = field(default_factory=lambda: np.zeros((4, 4)))
    kriyamana: np.ndarray = field(default_factory=lambda: np.zeros((4, 4)))
    
    def __post_init__(self):
        """Initialize with correct dimensions."""
        self.sanchita = np.zeros((self.dim, self.dim))
        self.prarabdha = np.zeros((self.dim, self.dim))
        self.kriyamana = np.zeros((self.dim, self.dim))
    
    @property
    def total(self) -> np.ndarray:
        """Get total karma tensor."""
        return self.sanchita + self.prarabdha + self.kriyamana
    
    def accumulate(self, action_tensor: np.ndarray, 
                   constraint_violation: float) -> None:
        """
        Accumulate karma from action.
        
        A_μν: Action tensor (outer product of action with constraint)
        """
        # Action generates kriyamana
        self.kriyamana += action_tensor * constraint_violation
        
        # Transfer some kriyamana to sanchita
        transfer_rate = 0.1
        self.sanchita += transfer_rate * self.kriyamana
        self.kriyamana *= (1 - transfer_rate)
    
    def manifest(self, rate: float = 0.05) -> np.ndarray:
        """
        Manifest stored karma as prarabdha.
        
        Returns the manifested karma tensor.
        """
        manifested = rate * self.sanchita
        self.prarabdha += manifested
        self.sanchita -= manifested
        return manifested
    
    def resolve(self, resolution_tensor: np.ndarray) -> None:
        """
        Resolve prarabdha through appropriate action.
        
        Resolution reduces prarabdha.
        """
        self.prarabdha -= resolution_tensor
        self.prarabdha = np.maximum(self.prarabdha, 0)  # No negative karma
    
    def trace(self) -> float:
        """Get scalar trace of total karma."""
        return float(np.trace(self.total))
    
    def storage(self) -> float:
        """
        Compute storage functional.
        
        Store(t) = ∫ Tr(S_μν) dVol
        """
        return float(np.sum(self.sanchita ** 2))


# =============================================================================
# STORAGE CRISIS DETECTOR
# =============================================================================

@dataclass
class StorageCrisis:
    """
    Detects karma storage crisis.
    
    Crisis occurs when:
    - Store(t) → +∞ as t → ∞
    - Cumulative residual sum diverges
    - Memory/weight norms grow unbounded
    """
    
    history: List[float] = field(default_factory=list)
    threshold: float = 100.0
    window: int = 10
    
    def record(self, storage: float) -> None:
        """Record storage value."""
        self.history.append(storage)
        if len(self.history) > 1000:
            self.history = self.history[-500:]  # Keep recent history
    
    def is_crisis(self) -> bool:
        """Check if storage crisis is occurring."""
        if len(self.history) < self.window:
            return False
        
        # Check absolute level
        if self.history[-1] > self.threshold:
            return True
        
        # Check growth rate
        recent = self.history[-self.window:]
        if len(recent) >= 2:
            growth_rate = (recent[-1] - recent[0]) / self.window
            if growth_rate > self.threshold / 10:
                return True
        
        return False
    
    def growth_rate(self) -> float:
        """Compute current growth rate."""
        if len(self.history) < 2:
            return 0.0
        
        window = min(self.window, len(self.history))
        recent = self.history[-window:]
        return (recent[-1] - recent[0]) / window
    
    def time_to_crisis(self) -> float:
        """Estimate time until crisis threshold."""
        rate = self.growth_rate()
        if rate <= 0:
            return float('inf')
        
        current = self.history[-1] if self.history else 0
        remaining = self.threshold - current
        return remaining / rate


# =============================================================================
# GLOBAL INVARIANT CHECKER
# =============================================================================

@dataclass
class InvariantChecker:
    """
    Checks all global invariants.
    
    Any operator, chart transition, or evolution must preserve:
    1. Conservation of information
    2. Conservation of paradox tension (or legitimate reduction)
    """
    
    information: InformationFunctional = field(default_factory=InformationFunctional)
    tension: ParadoxTension = field(default_factory=ParadoxTension)
    karma: KarmaTensor = field(default_factory=KarmaTensor)
    crisis_detector: StorageCrisis = field(default_factory=StorageCrisis)
    
    # Violation log
    violations: List[Dict] = field(default_factory=list)
    
    def check_transition(self, state_before: np.ndarray,
                        state_after: np.ndarray,
                        valuation_before: Valuation,
                        valuation_after: Valuation) -> Tuple[bool, List[str]]:
        """
        Check if transition preserves all invariants.
        
        Returns (valid, list of violations).
        """
        violations = []
        
        # Check information conservation
        if not self.information.is_conserved(state_before, state_after):
            violation = self.information.conservation_violation(state_before, state_after)
            violations.append(f"Information conservation violated: Δ = {violation:.4f}")
        
        # Check paradox tension
        tension_before = self.tension(valuation_before)
        tension_after = self.tension(valuation_after)
        
        if not self.tension.redistribution_valid(tension_before, tension_after):
            violations.append(
                f"Paradox tension increased illegitimately: "
                f"{tension_before:.2f} → {tension_after:.2f}"
            )
        
        # Log violations
        if violations:
            self.violations.append({
                "state_before": state_before.tolist(),
                "state_after": state_after.tolist(),
                "violations": violations
            })
        
        return (len(violations) == 0, violations)
    
    def update_karma(self, action: np.ndarray, 
                    constraint_gradient: np.ndarray,
                    violation: float) -> None:
        """Update karma tensor from action."""
        # Create action tensor
        action_tensor = np.outer(action, constraint_gradient)
        
        # Accumulate
        self.karma.accumulate(action_tensor, violation)
        
        # Record storage
        self.crisis_detector.record(self.karma.storage())
    
    def check_crisis(self) -> bool:
        """Check for storage crisis."""
        return self.crisis_detector.is_crisis()
    
    def summary(self) -> Dict:
        """Get invariant status summary."""
        return {
            "total_violations": len(self.violations),
            "karma_trace": self.karma.trace(),
            "karma_storage": self.karma.storage(),
            "crisis_imminent": self.check_crisis(),
            "growth_rate": self.crisis_detector.growth_rate()
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_invariants() -> bool:
    """Validate invariants module."""
    
    # Test InformationFunctional
    info = InformationFunctional(method="entropy")
    
    state = np.array([0.25, 0.25, 0.25, 0.25])
    entropy = info(state)
    assert entropy > 0  # Non-zero entropy
    
    # Test conservation
    state2 = state * 1.01  # Small perturbation
    assert not info.is_conserved(state, state2, tolerance=0.001)
    
    # Test ParadoxTension
    tension = ParadoxTension()
    
    valuation = Valuation()
    valuation["p"] = V4.T
    valuation["q"] = V4.F
    
    t1 = tension(valuation)
    assert t1 == 0  # No paradox
    
    valuation["r"] = V4.B  # Add contradiction
    t2 = tension(valuation)
    assert t2 > 0  # Has paradox
    
    valuation["s"] = V4.U  # Add undetermined
    t3 = tension(valuation)
    assert t3 > t2  # More tension
    
    # Test KarmaTensor
    karma = KarmaTensor(dim=4)
    
    action_tensor = np.outer([1, 0, 0, 0], [0.1, 0, 0, 0])
    karma.accumulate(action_tensor, violation=0.5)
    
    assert karma.trace() > 0
    assert karma.storage() > 0
    
    # Manifest
    manifested = karma.manifest(rate=0.1)
    assert np.sum(manifested) > 0
    
    # Resolve
    karma.resolve(manifested)
    
    # Test StorageCrisis
    crisis = StorageCrisis(threshold=10)
    
    for i in range(20):
        crisis.record(i * 0.3)  # Growing slowly
    
    assert not crisis.is_crisis()  # Below threshold
    
    for i in range(20):
        crisis.record(10 + i)  # Growing fast
    
    assert crisis.is_crisis()  # Above threshold
    
    # Test InvariantChecker
    checker = InvariantChecker()
    
    s1 = np.array([0.5, 0.5, 0.0, 0.0])
    s2 = np.array([0.4, 0.6, 0.0, 0.0])  # Conservation-preserving
    
    v1 = Valuation()
    v1["p"] = V4.T
    v2 = Valuation()
    v2["p"] = V4.T
    
    valid, violations = checker.check_transition(s1, s2, v1, v2)
    # May have small information violation
    
    # Update karma
    checker.update_karma(
        action=np.array([0.1, 0, 0, 0]),
        constraint_gradient=np.array([1, 0, 0, 0]),
        violation=0.1
    )
    
    summary = checker.summary()
    assert "karma_trace" in summary
    assert "crisis_imminent" in summary
    
    return True


if __name__ == "__main__":
    print("Validating Invariants...")
    assert validate_invariants()
    print("✓ Invariants module validated")
