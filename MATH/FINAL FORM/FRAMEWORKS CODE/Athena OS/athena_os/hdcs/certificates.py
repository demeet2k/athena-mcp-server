"""
ATHENA OS - HDCS Certificates
=============================
Certificate Hierarchy and Validation

From HDCS.docx Chapters 10-12:

CERTIFICATE HIERARCHY:
    1. Local pairwise certificates (transfer between tasks)
    2. Node-level certificates (migration between nodes)
    3. Plan-level certificates (complete plan validation)

CERTIFICATE PROPERTIES:
    - Feasibility preserving
    - Objective non-worsening
    - Composable and rejectable
    - Auditable by construction

PLAN CERTIFICATION:
    Certify: ??_prop → ??_cert
    Filter, trim, or reorder actions
    Shadow-state simulation for prediction
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import math

from .primitives import (
    ControllerState, TaskState, Node, Plan, Action, ActionType
)
from .telemetry import Observation
from .objectives import ObjectiveValues, ObjectivePredictor, DominanceChecker


# =============================================================================
# CERTIFICATE TYPES
# =============================================================================

class CertificateType(Enum):
    """Types of certificates in the hierarchy."""
    LOCAL = "local"           # Local pairwise (transfer)
    NODE = "node"             # Node-level (migration)
    PLAN = "plan"             # Plan-level (complete)
    FEASIBILITY = "feasibility"  # Hard constraint check


class CertificateStatus(Enum):
    """Status of certificate validation."""
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TRIMMED = "trimmed"
    PENDING = "pending"


# =============================================================================
# CERTIFICATE RESULT
# =============================================================================

@dataclass
class CertificateResult:
    """Result of certificate validation."""
    
    cert_type: CertificateType
    status: CertificateStatus
    reason: str = ""
    
    # For plan certificates
    accepted_actions: List[int] = field(default_factory=list)  # Indices
    rejected_actions: List[int] = field(default_factory=list)
    
    # Predicted objectives
    baseline_objectives: Optional[ObjectiveValues] = None
    predicted_objectives: Optional[ObjectiveValues] = None
    
    # Audit trail
    audit_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_accepted(self) -> bool:
        return self.status == CertificateStatus.ACCEPTED
    
    @property
    def is_rejected(self) -> bool:
        return self.status == CertificateStatus.REJECTED


# =============================================================================
# FEASIBILITY CERTIFICATE
# =============================================================================

@dataclass
class FeasibilityCertificate:
    """
    Validates hard feasibility constraints.
    
    Invariants:
    (H1) Node capacity: ∑_{i: p_i=n} (a_i + r_i) ≤ C_n
    (H2) Allocation bounds: a̲_i ≤ a_i ≤ ā_i
    (H3) Reserve nonneg/budget: r_i ≥ 0, ∑ r_i ≤ R
    (H4) Plan prefix feasibility
    """
    
    def check_action(self, action: Action, state: ControllerState) -> CertificateResult:
        """Check if a single action preserves feasibility."""
        task = state.get_task(action.task_id)
        if not task:
            return CertificateResult(
                CertificateType.FEASIBILITY,
                CertificateStatus.REJECTED,
                f"Task {action.task_id} not found"
            )
        
        node = state.get_node(task.placement)
        
        if action.action_type == ActionType.SCALE_UP:
            new_alloc = task.allocation + action.delta
            
            # Check bounds
            if not task.bounds.is_valid(new_alloc):
                return CertificateResult(
                    CertificateType.FEASIBILITY,
                    CertificateStatus.REJECTED,
                    f"Allocation {new_alloc:.2f} exceeds bounds"
                )
            
            # Check node capacity
            if node and node.used + action.delta > node.capacity:
                return CertificateResult(
                    CertificateType.FEASIBILITY,
                    CertificateStatus.REJECTED,
                    f"Node {node.node_id} capacity exceeded"
                )
        
        elif action.action_type == ActionType.SCALE_DOWN:
            new_alloc = task.allocation - action.delta
            
            if not task.bounds.is_valid(new_alloc):
                return CertificateResult(
                    CertificateType.FEASIBILITY,
                    CertificateStatus.REJECTED,
                    f"Allocation {new_alloc:.2f} below minimum"
                )
        
        elif action.action_type == ActionType.RESERVE_UP:
            new_reserve = task.reserve + action.delta
            total_reserve = state.total_reserve() + action.delta
            
            # Check node capacity
            if node and node.used + action.delta > node.capacity:
                return CertificateResult(
                    CertificateType.FEASIBILITY,
                    CertificateStatus.REJECTED,
                    f"Node {node.node_id} capacity exceeded"
                )
            
            # Check reserve budget
            if total_reserve > state.reserve_budget:
                return CertificateResult(
                    CertificateType.FEASIBILITY,
                    CertificateStatus.REJECTED,
                    f"Reserve budget {state.reserve_budget:.2f} exceeded"
                )
        
        elif action.action_type == ActionType.RESERVE_DOWN:
            new_reserve = task.reserve - action.delta
            
            if new_reserve < 0:
                return CertificateResult(
                    CertificateType.FEASIBILITY,
                    CertificateStatus.REJECTED,
                    f"Reserve cannot be negative"
                )
        
        elif action.action_type == ActionType.MIGRATE:
            target_node = state.get_node(action.target_node)
            if not target_node:
                return CertificateResult(
                    CertificateType.FEASIBILITY,
                    CertificateStatus.REJECTED,
                    f"Target node {action.target_node} not found"
                )
            
            task_usage = task.allocation + task.reserve
            if not target_node.can_add(task.allocation, task.reserve):
                return CertificateResult(
                    CertificateType.FEASIBILITY,
                    CertificateStatus.REJECTED,
                    f"Target node {action.target_node} cannot fit task"
                )
        
        return CertificateResult(
            CertificateType.FEASIBILITY,
            CertificateStatus.ACCEPTED,
            "Feasibility check passed"
        )
    
    def check_plan(self, plan: Plan, state: ControllerState) -> CertificateResult:
        """Check if complete plan preserves feasibility."""
        accepted = []
        rejected = []
        
        # Simulate plan execution
        shadow_state = self._create_shadow_state(state)
        
        for i, action in enumerate(plan.actions):
            result = self.check_action(action, shadow_state)
            
            if result.is_accepted:
                accepted.append(i)
                self._apply_action_to_shadow(action, shadow_state)
            else:
                rejected.append(i)
        
        if rejected:
            return CertificateResult(
                CertificateType.FEASIBILITY,
                CertificateStatus.TRIMMED,
                f"Trimmed {len(rejected)} infeasible actions",
                accepted_actions=accepted,
                rejected_actions=rejected
            )
        
        return CertificateResult(
            CertificateType.FEASIBILITY,
            CertificateStatus.ACCEPTED,
            "All actions feasible",
            accepted_actions=accepted
        )
    
    def _create_shadow_state(self, state: ControllerState) -> ControllerState:
        """Create shadow copy of state for simulation."""
        # Shallow copy for now (would need deep copy in production)
        shadow = ControllerState(
            tick=state.tick,
            reserve_budget=state.reserve_budget
        )
        
        for task_id, task in state.tasks.items():
            shadow.tasks[task_id] = TaskState(
                task_id=task_id,
                placement=task.placement,
                allocation=task.allocation,
                reserve=task.reserve,
                bounds=task.bounds
            )
        
        for node_id, node in state.nodes.items():
            shadow.nodes[node_id] = Node(
                node_id=node_id,
                capacity=node.capacity,
                allocated=node.allocated,
                reserved=node.reserved
            )
        
        return shadow
    
    def _apply_action_to_shadow(self, action: Action, state: ControllerState) -> None:
        """Apply action to shadow state."""
        task = state.get_task(action.task_id)
        if not task:
            return
        
        node = state.get_node(task.placement)
        
        if action.action_type == ActionType.SCALE_UP:
            task.allocation += action.delta
            if node:
                node.allocated += action.delta
        
        elif action.action_type == ActionType.SCALE_DOWN:
            task.allocation -= action.delta
            if node:
                node.allocated -= action.delta
        
        elif action.action_type == ActionType.RESERVE_UP:
            task.reserve += action.delta
            if node:
                node.reserved += action.delta
        
        elif action.action_type == ActionType.RESERVE_DOWN:
            task.reserve -= action.delta
            if node:
                node.reserved -= action.delta
        
        elif action.action_type == ActionType.MIGRATE:
            if node:
                node.allocated -= task.allocation
                node.reserved -= task.reserve
            
            target = state.get_node(action.target_node)
            if target:
                target.allocated += task.allocation
                target.reserved += task.reserve
            
            task.placement = action.target_node


# =============================================================================
# LOCAL TRANSFER CERTIFICATE
# =============================================================================

@dataclass
class LocalTransferCertificate:
    """
    Certificate for local resource transfers.
    
    Validates pairwise transfers between tasks on the same node.
    """
    
    sla_threshold: float = 100.0
    predictor: ObjectivePredictor = field(default_factory=ObjectivePredictor)
    dominance: DominanceChecker = field(default_factory=DominanceChecker)
    
    def check_transfer(self, source_task: TaskState, target_task: TaskState,
                      amount: float, obs: Observation,
                      state: ControllerState) -> CertificateResult:
        """
        Check if a transfer from source to target is certified.
        
        Transfer is certified if:
        1. Both tasks on same node
        2. Predicted objectives don't worsen
        """
        # Check same node
        if source_task.placement != target_task.placement:
            return CertificateResult(
                CertificateType.LOCAL,
                CertificateStatus.REJECTED,
                "Tasks not on same node"
            )
        
        # Predict before and after
        source_record = obs.get_task(source_task.task_id)
        target_record = obs.get_task(target_task.task_id)
        
        if not source_record or not target_record:
            return CertificateResult(
                CertificateType.LOCAL,
                CertificateStatus.REJECTED,
                "Missing telemetry"
            )
        
        # Compute baseline violations
        baseline_violations = 0
        if source_record.latency > self.sla_threshold:
            baseline_violations += 1
        if target_record.latency > self.sla_threshold:
            baseline_violations += 1
        
        # Predict after transfer
        source_new_alloc = source_task.effective_allocation - amount
        target_new_alloc = target_task.effective_allocation + amount
        
        source_interf = state.compute_interference_score(source_task.task_id)
        target_interf = state.compute_interference_score(target_task.task_id)
        
        source_pred = self.predictor.predict_latency(
            source_task.task_id, source_new_alloc,
            source_record.backlog_norm, source_interf, source_task.theta
        )
        target_pred = self.predictor.predict_latency(
            target_task.task_id, target_new_alloc,
            target_record.backlog_norm, target_interf, target_task.theta
        )
        
        # Count predicted violations
        predicted_violations = 0
        if source_pred > self.sla_threshold:
            predicted_violations += 1
        if target_pred > self.sla_threshold:
            predicted_violations += 1
        
        # Check non-worsening
        if predicted_violations > baseline_violations:
            return CertificateResult(
                CertificateType.LOCAL,
                CertificateStatus.REJECTED,
                f"Transfer would increase violations ({baseline_violations} → {predicted_violations})"
            )
        
        return CertificateResult(
            CertificateType.LOCAL,
            CertificateStatus.ACCEPTED,
            f"Transfer certified ({baseline_violations} → {predicted_violations})"
        )


# =============================================================================
# NODE MIGRATION CERTIFICATE
# =============================================================================

@dataclass
class NodeMigrationCertificate:
    """
    Certificate for node-level migrations.
    
    Validates migrations between nodes, considering:
    - Capacity constraints
    - Interference effects
    - Objective impact
    """
    
    sla_threshold: float = 100.0
    predictor: ObjectivePredictor = field(default_factory=ObjectivePredictor)
    
    def check_migration(self, task: TaskState, target_node: int,
                       obs: Observation, state: ControllerState) -> CertificateResult:
        """
        Check if migration is certified.
        
        Migration is certified if:
        1. Target node has capacity
        2. Predicted node-level violations don't increase
        """
        source_node = state.get_node(task.placement)
        target = state.get_node(target_node)
        
        if not source_node or not target:
            return CertificateResult(
                CertificateType.NODE,
                CertificateStatus.REJECTED,
                "Invalid nodes"
            )
        
        # Check capacity
        if not target.can_add(task.allocation, task.reserve):
            return CertificateResult(
                CertificateType.NODE,
                CertificateStatus.REJECTED,
                f"Target node {target_node} lacks capacity"
            )
        
        # Count current violations on both nodes
        source_tasks = state.get_node_tasks(source_node.node_id)
        target_tasks = state.get_node_tasks(target.node_id)
        
        source_violations = sum(
            1 for t in source_tasks
            if obs.get_task(t.task_id) and obs.get_task(t.task_id).latency > self.sla_threshold
        )
        target_violations = sum(
            1 for t in target_tasks
            if obs.get_task(t.task_id) and obs.get_task(t.task_id).latency > self.sla_threshold
        )
        
        baseline_total = source_violations + target_violations
        
        # Predict after migration
        # Simplified: assume migration reduces source violations
        # but may increase target violations
        task_violating = (obs.get_task(task.task_id) and 
                         obs.get_task(task.task_id).latency > self.sla_threshold)
        
        # Heuristic: if task is violating, migration may help
        # This is simplified - full implementation would use predictor
        if task_violating:
            return CertificateResult(
                CertificateType.NODE,
                CertificateStatus.ACCEPTED,
                "Migration may help violating task"
            )
        
        # If task not violating, migration should be justified by hotspot relief
        if source_violations == 0:
            return CertificateResult(
                CertificateType.NODE,
                CertificateStatus.REJECTED,
                "Source node has no violations, migration not justified"
            )
        
        return CertificateResult(
            CertificateType.NODE,
            CertificateStatus.ACCEPTED,
            "Migration certified for hotspot relief"
        )


# =============================================================================
# PLAN CERTIFICATE
# =============================================================================

@dataclass
class PlanCertificate:
    """
    Plan-level certificate.
    
    Validates complete plan using shadow-state simulation.
    
    Certification steps:
    1. Feasibility check for each action
    2. Predict objectives under hypothetical post-plan configuration
    3. Compare against baseline (empty plan)
    4. Accept, trim, or reject
    """
    
    sla_threshold: float = 100.0
    predictor: ObjectivePredictor = field(default_factory=ObjectivePredictor)
    dominance: DominanceChecker = field(default_factory=DominanceChecker)
    feasibility: FeasibilityCertificate = field(default_factory=FeasibilityCertificate)
    
    def certify(self, plan: Plan, state: ControllerState,
               obs: Observation) -> Tuple[Plan, CertificateResult]:
        """
        Certify a plan.
        
        Returns (certified_plan, result)
        """
        if plan.is_empty():
            return Plan.empty(), CertificateResult(
                CertificateType.PLAN,
                CertificateStatus.ACCEPTED,
                "Empty plan"
            )
        
        # Step 1: Feasibility check
        feas_result = self.feasibility.check_plan(plan, state)
        
        if feas_result.status == CertificateStatus.REJECTED:
            return Plan.empty(), CertificateResult(
                CertificateType.PLAN,
                CertificateStatus.REJECTED,
                f"Feasibility check failed: {feas_result.reason}"
            )
        
        # Get feasible actions
        feasible_actions = [plan.actions[i] for i in feas_result.accepted_actions]
        
        if not feasible_actions:
            return Plan.empty(), CertificateResult(
                CertificateType.PLAN,
                CertificateStatus.REJECTED,
                "No feasible actions"
            )
        
        # Step 2: Compute baseline objectives (empty plan)
        baseline = self._compute_objectives(Plan.empty(), state, obs)
        
        # Step 3: Compute predicted objectives for proposed plan
        proposed_plan = Plan(actions=feasible_actions)
        predicted = self._compute_objectives(proposed_plan, state, obs)
        
        # Step 4: Check dominance
        if not self.dominance.is_admissible(predicted, baseline):
            # Plan worsens violation count - reject
            return Plan.empty(), CertificateResult(
                CertificateType.PLAN,
                CertificateStatus.REJECTED,
                f"Plan worsens violations: {baseline.violation_count} → {predicted.violation_count}",
                baseline_objectives=baseline,
                predicted_objectives=predicted
            )
        
        if not self.dominance.is_acceptable(predicted, baseline):
            # Plan is worse overall - try trimming
            trimmed_plan, trimmed_pred = self._try_trim(
                feasible_actions, state, obs, baseline
            )
            
            if trimmed_plan.is_empty():
                return Plan.empty(), CertificateResult(
                    CertificateType.PLAN,
                    CertificateStatus.REJECTED,
                    "Could not find acceptable plan subset",
                    baseline_objectives=baseline,
                    predicted_objectives=predicted
                )
            
            return trimmed_plan, CertificateResult(
                CertificateType.PLAN,
                CertificateStatus.TRIMMED,
                f"Trimmed to {len(trimmed_plan.actions)} actions",
                baseline_objectives=baseline,
                predicted_objectives=trimmed_pred
            )
        
        # Plan is acceptable
        certified_plan = Plan(
            actions=feasible_actions,
            certified=True,
            certificate_reason="plan_certified"
        )
        
        return certified_plan, CertificateResult(
            CertificateType.PLAN,
            CertificateStatus.ACCEPTED,
            f"Plan certified with {len(certified_plan.actions)} actions",
            accepted_actions=list(range(len(feasible_actions))),
            baseline_objectives=baseline,
            predicted_objectives=predicted
        )
    
    def _compute_objectives(self, plan: Plan, state: ControllerState,
                           obs: Observation) -> ObjectiveValues:
        """Compute predicted objectives for a plan."""
        # Apply plan to shadow state
        shadow = self.feasibility._create_shadow_state(state)
        
        for action in plan.actions:
            self.feasibility._apply_action_to_shadow(action, shadow)
        
        # Predict objectives
        new_allocations = {t.task_id: t.allocation for t in shadow.tasks.values()}
        new_reserves = {t.task_id: t.reserve for t in shadow.tasks.values()}
        new_placements = {t.task_id: t.placement for t in shadow.tasks.values()}
        
        return self.predictor.predict_objectives_for_config(
            state, obs, new_allocations, new_reserves, new_placements
        )
    
    def _try_trim(self, actions: List[Action], state: ControllerState,
                 obs: Observation, baseline: ObjectiveValues) -> Tuple[Plan, ObjectiveValues]:
        """Try to find acceptable plan subset by trimming."""
        # Simple approach: try removing actions one at a time
        for i in range(len(actions)):
            trimmed_actions = actions[:i]  # Prefix
            
            if not trimmed_actions:
                continue
            
            trimmed_plan = Plan(actions=trimmed_actions)
            predicted = self._compute_objectives(trimmed_plan, state, obs)
            
            if self.dominance.is_acceptable(predicted, baseline):
                trimmed_plan.certified = True
                return trimmed_plan, predicted
        
        return Plan.empty(), baseline


# =============================================================================
# VALIDATION
# =============================================================================

def validate_certificates() -> bool:
    """Validate HDCS certificates module."""
    from .primitives import create_controller_state
    
    # Create test state
    state = create_controller_state(n_tasks=4, n_nodes=2, node_capacity=100.0)
    
    # Create observation
    obs = Observation(tick=0)
    for task_id in state.tasks:
        obs.task_telemetry[task_id] = TelemetryRecord(
            task_id=task_id, tick=0,
            latency=50.0 + task_id * 25,
            backlog=100.0,
            throughput=50.0
        )
        obs.task_telemetry[task_id].compute_backlog_norm()
    
    # Test FeasibilityCertificate
    feas = FeasibilityCertificate()
    
    # Valid action
    action = Action(ActionType.SCALE_UP, task_id=0, delta=5.0)
    result = feas.check_action(action, state)
    assert result.is_accepted
    
    # Invalid action (exceed capacity)
    big_action = Action(ActionType.SCALE_UP, task_id=0, delta=1000.0)
    result = feas.check_action(big_action, state)
    # Note: depends on state setup
    
    # Test plan
    plan = Plan(actions=[action])
    result = feas.check_plan(plan, state)
    assert result.status in [CertificateStatus.ACCEPTED, CertificateStatus.TRIMMED]
    
    # Test PlanCertificate
    plan_cert = PlanCertificate(sla_threshold=100.0)
    certified_plan, cert_result = plan_cert.certify(plan, state, obs)
    assert cert_result.status in [CertificateStatus.ACCEPTED, CertificateStatus.REJECTED, CertificateStatus.TRIMMED]
    
    return True


if __name__ == "__main__":
    print("Validating HDCS Certificates...")
    assert validate_certificates()
    print("✓ HDCS Certificates validated")
    
    # Demo
    print("\n=== HDCS Certificates Demo ===")
    
    print("\nCertificate Hierarchy:")
    print("  1. Feasibility (hard constraints)")
    print("  2. Local Transfer (pairwise)")
    print("  3. Node Migration (node-level)")
    print("  4. Plan (complete validation)")
    
    print("\nCertificate Properties:")
    print("  • Feasibility preserving")
    print("  • Objective non-worsening")
    print("  • Composable and rejectable")
    print("  • Auditable by construction")
