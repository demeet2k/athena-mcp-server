"""
ATHENA OS - HDCS Objectives
===========================
SLA Violation, Severity, and Churn Metrics

From HDCS.docx Chapter 4:

PRIMARY OBJECTIVE - VIOLATION COUNT:
    v_i(t) = ??[y_i(t) > L]    (violation indicator)
    V(t) = ∑_{i∈??} v_i(t)    (total violations)

SECONDARY OBJECTIVE - SEVERITY:
    S(t) = ∑_{i∈??} max(0, (y_i(t) - L) / L)

TERTIARY OBJECTIVE - CHURN:
    C(t) = allocation_deltas + reserve_churn + migrations

LEXICOGRAPHIC OPTIMIZATION:
    Minimize (V, S, C) subject to feasibility
    Actions that worsen violation count are INADMISSIBLE
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import math

from .primitives import ControllerState, Plan, Action, ActionType
from .telemetry import Observation, TelemetryRecord


# =============================================================================
# OBJECTIVE COMPONENTS
# =============================================================================

@dataclass
class ObjectiveValues:
    """
    Complete objective tuple (V, S, C) at a tick.
    
    V: Violation count (primary)
    S: Severity (secondary)
    C: Churn (tertiary)
    """
    
    violation_count: int = 0       # V(t)
    severity: float = 0.0          # S(t)
    churn: float = 0.0             # C(t)
    
    # Component breakdown
    allocation_churn: float = 0.0
    reserve_churn: float = 0.0
    migration_count: int = 0
    
    @property
    def as_tuple(self) -> Tuple[int, float, float]:
        """Get as lexicographic tuple (V, S, C)."""
        return (self.violation_count, self.severity, self.churn)
    
    def dominates(self, other: 'ObjectiveValues') -> bool:
        """
        Check if this objective dominates other (lexicographically).
        
        (V1, S1, C1) dominates (V2, S2, C2) if:
        - V1 < V2, or
        - V1 == V2 and S1 < S2, or
        - V1 == V2 and S1 == S2 and C1 < C2
        """
        if self.violation_count < other.violation_count:
            return True
        if self.violation_count > other.violation_count:
            return False
        
        if self.severity < other.severity:
            return True
        if self.severity > other.severity:
            return False
        
        return self.churn < other.churn
    
    def is_admissible_relative_to(self, baseline: 'ObjectiveValues') -> bool:
        """
        Check if this objective is admissible relative to baseline.
        
        Admissible means: does NOT worsen violation count.
        """
        return self.violation_count <= baseline.violation_count
    
    def improvement_over(self, baseline: 'ObjectiveValues') -> 'ObjectiveDelta':
        """Compute improvement delta from baseline."""
        return ObjectiveDelta(
            delta_v=baseline.violation_count - self.violation_count,
            delta_s=baseline.severity - self.severity,
            delta_c=baseline.churn - self.churn
        )


@dataclass
class ObjectiveDelta:
    """Change in objectives (positive = improvement)."""
    
    delta_v: int = 0      # Δ violations (positive = fewer violations)
    delta_s: float = 0.0  # Δ severity (positive = less severe)
    delta_c: float = 0.0  # Δ churn (positive = less churn)
    
    def is_improvement(self) -> bool:
        """Check if this represents an improvement."""
        if self.delta_v > 0:
            return True
        if self.delta_v < 0:
            return False
        if self.delta_s > 0:
            return True
        if self.delta_s < 0:
            return False
        return self.delta_c > 0


# =============================================================================
# VIOLATION TRACKING
# =============================================================================

@dataclass
class ViolationIndicator:
    """
    Violation indicator v_i(t) = ??[y_i(t) > L].
    
    Also tracks persistence and near-threshold status.
    """
    
    task_id: int
    is_violating: bool = False
    latency: float = 0.0
    threshold: float = 100.0
    
    # Persistence
    persistence_counter: int = 0
    persistence_threshold: int = 3
    
    # Near-threshold
    near_threshold_margin: float = 0.1  # 10% margin
    is_near_threshold: bool = False
    
    @property
    def is_persistently_violating(self) -> bool:
        """Check π_i^(K)(t) = ??[ν_i ≥ K]."""
        return self.persistence_counter >= self.persistence_threshold
    
    def update(self, latency: float) -> None:
        """Update violation status."""
        self.latency = latency
        self.is_violating = latency > self.threshold
        
        # Update persistence
        if self.is_violating:
            self.persistence_counter += 1
        else:
            self.persistence_counter = 0
        
        # Check near-threshold
        near_bound = self.threshold * (1 - self.near_threshold_margin)
        self.is_near_threshold = near_bound <= latency <= self.threshold


# =============================================================================
# OBJECTIVE CALCULATOR
# =============================================================================

@dataclass
class ObjectiveCalculator:
    """
    Computes objective values (V, S, C) from observations and state.
    """
    
    sla_threshold: float = 100.0   # L: SLA latency threshold
    
    # Churn weights
    allocation_weight: float = 1.0
    reserve_weight: float = 0.5
    migration_weight: float = 10.0
    
    # Violation tracking
    violations: Dict[int, ViolationIndicator] = field(default_factory=dict)
    
    def compute_violation_count(self, obs: Observation) -> int:
        """
        Compute V(t) = ∑_{i∈??} v_i(t).
        """
        count = 0
        for record in obs.task_telemetry.values():
            if record.latency > self.sla_threshold:
                count += 1
        return count
    
    def compute_severity(self, obs: Observation) -> float:
        """
        Compute S(t) = ∑_{i∈??} max(0, (y_i - L) / L).
        """
        if self.sla_threshold <= 0:
            return 0.0
        
        severity = 0.0
        for record in obs.task_telemetry.values():
            if record.latency > self.sla_threshold:
                severity += (record.latency - self.sla_threshold) / self.sla_threshold
        return severity
    
    def compute_churn(self, plan: Plan, state: ControllerState) -> Tuple[float, float, float, int]:
        """
        Compute churn components from a plan.
        
        Returns (total_churn, allocation_churn, reserve_churn, migration_count)
        """
        allocation_churn = 0.0
        reserve_churn = 0.0
        migration_count = 0
        
        for action in plan.actions:
            if action.action_type == ActionType.SCALE_UP:
                allocation_churn += abs(action.delta)
            elif action.action_type == ActionType.SCALE_DOWN:
                allocation_churn += abs(action.delta)
            elif action.action_type == ActionType.RESERVE_UP:
                reserve_churn += abs(action.delta)
            elif action.action_type == ActionType.RESERVE_DOWN:
                reserve_churn += abs(action.delta)
            elif action.action_type == ActionType.MIGRATE:
                migration_count += 1
        
        total_churn = (
            self.allocation_weight * allocation_churn +
            self.reserve_weight * reserve_churn +
            self.migration_weight * migration_count
        )
        
        return total_churn, allocation_churn, reserve_churn, migration_count
    
    def compute_objectives(self, obs: Observation, plan: Plan,
                          state: ControllerState) -> ObjectiveValues:
        """
        Compute complete objective values (V, S, C).
        """
        V = self.compute_violation_count(obs)
        S = self.compute_severity(obs)
        C, alloc_c, res_c, mig_c = self.compute_churn(plan, state)
        
        return ObjectiveValues(
            violation_count=V,
            severity=S,
            churn=C,
            allocation_churn=alloc_c,
            reserve_churn=res_c,
            migration_count=mig_c
        )
    
    def update_violations(self, obs: Observation) -> None:
        """Update violation tracking from observation."""
        for task_id, record in obs.task_telemetry.items():
            if task_id not in self.violations:
                self.violations[task_id] = ViolationIndicator(
                    task_id=task_id,
                    threshold=self.sla_threshold
                )
            self.violations[task_id].update(record.latency)
    
    def get_persistently_violating(self) -> List[int]:
        """Get list of persistently violating tasks."""
        return [
            v.task_id for v in self.violations.values()
            if v.is_persistently_violating
        ]
    
    def get_near_threshold(self) -> List[int]:
        """Get list of tasks near SLA threshold."""
        return [
            v.task_id for v in self.violations.values()
            if v.is_near_threshold
        ]


# =============================================================================
# OBJECTIVE PREDICTOR
# =============================================================================

@dataclass
class ObjectivePredictor:
    """
    Predicts objectives under hypothetical configurations.
    
    Uses learned model θ̂ to predict latency:
    ŷ_i = θ̂ · φ_i where φ_i = (1, 1/a_eff, bn, s)
    """
    
    sla_threshold: float = 100.0
    
    def predict_latency(self, task_id: int, effective_allocation: float,
                       backlog_norm: float, interference_score: float,
                       theta: List[float]) -> float:
        """
        Predict latency using linear model.
        
        ŷ = θ_0 + θ_1 / a_eff + θ_2 * bn + θ_3 * s
        """
        if len(theta) < 4:
            theta = theta + [0.0] * (4 - len(theta))
        
        # Avoid division by zero
        inv_alloc = 1.0 / max(0.1, effective_allocation)
        
        predicted = (
            theta[0] +
            theta[1] * inv_alloc +
            theta[2] * backlog_norm +
            theta[3] * interference_score
        )
        
        return max(0.0, predicted)
    
    def predict_violation(self, predicted_latency: float) -> bool:
        """Predict if latency will violate SLA."""
        return predicted_latency > self.sla_threshold
    
    def predict_objectives_for_config(
        self,
        state: ControllerState,
        obs: Observation,
        new_allocations: Dict[int, float],
        new_reserves: Dict[int, float],
        new_placements: Dict[int, int]
    ) -> ObjectiveValues:
        """
        Predict objectives for a hypothetical configuration.
        
        This implements shadow-state simulation for plan-level certificates.
        """
        predicted_V = 0
        predicted_S = 0.0
        
        for task_id, task in state.tasks.items():
            # Get hypothetical values
            alloc = new_allocations.get(task_id, task.allocation)
            reserve = new_reserves.get(task_id, task.reserve)
            placement = new_placements.get(task_id, task.placement)
            
            eff_alloc = alloc + reserve
            
            # Get backlog norm from observation
            record = obs.get_task(task_id)
            backlog_norm = record.backlog_norm if record else 0.0
            
            # Compute interference score with new placement
            # (simplified - would need to recompute based on co-located tasks)
            interf_score = state.compute_interference_score(task_id)
            
            # Predict latency
            predicted_latency = self.predict_latency(
                task_id, eff_alloc, backlog_norm, interf_score, task.theta
            )
            
            # Update objectives
            if predicted_latency > self.sla_threshold:
                predicted_V += 1
                predicted_S += (predicted_latency - self.sla_threshold) / self.sla_threshold
        
        return ObjectiveValues(
            violation_count=predicted_V,
            severity=predicted_S,
            churn=0.0  # Churn computed separately from plan
        )


# =============================================================================
# DOMINANCE CHECKER
# =============================================================================

@dataclass
class DominanceChecker:
    """
    Checks objective dominance and admissibility.
    
    Implements lexicographic comparison: (V, S, C)
    """
    
    # Tolerance for floating point comparison
    epsilon: float = 1e-6
    
    def lexicographic_compare(self, a: ObjectiveValues, b: ObjectiveValues) -> int:
        """
        Compare two objectives lexicographically.
        
        Returns:
            -1 if a < b (a dominates)
             0 if a == b
             1 if a > b (b dominates)
        """
        # Compare violation count (primary)
        if a.violation_count < b.violation_count:
            return -1
        if a.violation_count > b.violation_count:
            return 1
        
        # Compare severity (secondary)
        if a.severity < b.severity - self.epsilon:
            return -1
        if a.severity > b.severity + self.epsilon:
            return 1
        
        # Compare churn (tertiary)
        if a.churn < b.churn - self.epsilon:
            return -1
        if a.churn > b.churn + self.epsilon:
            return 1
        
        return 0
    
    def is_admissible(self, proposed: ObjectiveValues,
                     baseline: ObjectiveValues) -> bool:
        """
        Check if proposed objectives are admissible.
        
        Inadmissible if proposed worsens violation count.
        """
        return proposed.violation_count <= baseline.violation_count
    
    def is_strictly_better(self, proposed: ObjectiveValues,
                          baseline: ObjectiveValues) -> bool:
        """Check if proposed is strictly better than baseline."""
        return self.lexicographic_compare(proposed, baseline) < 0
    
    def is_acceptable(self, proposed: ObjectiveValues,
                     baseline: ObjectiveValues,
                     allow_equal: bool = True) -> bool:
        """
        Check if proposed objectives are acceptable.
        
        Acceptable if:
        - Strictly better, or
        - Equal (if allow_equal)
        """
        cmp = self.lexicographic_compare(proposed, baseline)
        if cmp < 0:
            return True
        if cmp == 0 and allow_equal:
            return True
        return False


# =============================================================================
# VALIDATION
# =============================================================================

def validate_objectives() -> bool:
    """Validate HDCS objectives module."""
    
    # Test ObjectiveValues
    obj1 = ObjectiveValues(violation_count=5, severity=0.5, churn=10.0)
    obj2 = ObjectiveValues(violation_count=5, severity=0.3, churn=10.0)
    obj3 = ObjectiveValues(violation_count=4, severity=1.0, churn=100.0)
    
    assert obj2.dominates(obj1)  # Same V, lower S
    assert obj3.dominates(obj1)  # Lower V (primary)
    assert not obj1.dominates(obj2)
    
    # Test admissibility
    baseline = ObjectiveValues(violation_count=5, severity=0.5, churn=10.0)
    better = ObjectiveValues(violation_count=4, severity=0.3, churn=5.0)
    worse = ObjectiveValues(violation_count=6, severity=0.2, churn=2.0)
    
    assert better.is_admissible_relative_to(baseline)
    assert not worse.is_admissible_relative_to(baseline)
    
    # Test ObjectiveDelta
    delta = better.improvement_over(baseline)
    assert delta.delta_v == 1  # 5 - 4 = 1 improvement
    assert delta.is_improvement()
    
    # Test ViolationIndicator
    vi = ViolationIndicator(task_id=0, threshold=100.0)
    vi.update(120.0)
    assert vi.is_violating
    vi.update(130.0)
    vi.update(140.0)
    assert vi.is_persistently_violating
    
    vi.update(80.0)
    assert not vi.is_violating
    assert vi.persistence_counter == 0
    
    # Test near-threshold
    vi.update(95.0)
    assert vi.is_near_threshold
    
    # Test DominanceChecker
    checker = DominanceChecker()
    assert checker.lexicographic_compare(better, baseline) == -1
    assert checker.lexicographic_compare(worse, baseline) == 1
    assert checker.is_admissible(better, baseline)
    assert not checker.is_admissible(worse, baseline)
    
    return True


if __name__ == "__main__":
    print("Validating HDCS Objectives...")
    assert validate_objectives()
    print("✓ HDCS Objectives validated")
    
    # Demo
    print("\n=== HDCS Objectives Demo ===")
    
    print("\nLexicographic Optimization: minimize (V, S, C)")
    print("  V = Violation Count (primary)")
    print("  S = Severity (secondary)")
    print("  C = Churn (tertiary)")
    
    obj1 = ObjectiveValues(violation_count=5, severity=0.5, churn=10.0)
    obj2 = ObjectiveValues(violation_count=5, severity=0.3, churn=15.0)
    obj3 = ObjectiveValues(violation_count=4, severity=1.0, churn=50.0)
    
    print(f"\nObjective 1: V={obj1.violation_count}, S={obj1.severity}, C={obj1.churn}")
    print(f"Objective 2: V={obj2.violation_count}, S={obj2.severity}, C={obj2.churn}")
    print(f"Objective 3: V={obj3.violation_count}, S={obj3.severity}, C={obj3.churn}")
    
    checker = DominanceChecker()
    print(f"\nObj2 dominates Obj1: {obj2.dominates(obj1)} (same V, lower S)")
    print(f"Obj3 dominates Obj1: {obj3.dominates(obj1)} (lower V)")
    print(f"Obj3 dominates Obj2: {obj3.dominates(obj2)} (lower V)")
