"""
ATHENA OS - HDCS Operators
==========================
Quad-Polar Operator Algebra (D, Ω, Σ, Ψ)

From HDCS.docx Chapter 5:

QUAD-POLAR FORMULATION:
    ??(x, o) = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ

OPERATOR DEFINITIONS:
    D (Discrete): Bounded action proposals under hard constraints
        D: ?? × ?? → ??
        
    Ω (Continuous): Predictive modeling and continuous targets
        Ω: ?? × ?? → ??
        
    Σ (Stochastic): Certificate-constrained exploration
        Σ: ?? × ?? → ?? (stochastic kernels)
        
    Ψ (Recursive): Hierarchical/structural reasoning
        Ψ: ?? × ?? → ℋ (hierarchy structures)

COMPOSITION:
    Plan = D(Ψ(Ω(x, o))) with Σ-modulated exploration
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import math
import random

from .primitives import (
    ControllerState, TaskState, Node, Plan, Action, ActionType,
    TrustRegion
)
from .telemetry import Observation, TelemetryRecord
from .objectives import ObjectiveCalculator, ObjectiveValues, ObjectivePredictor


# =============================================================================
# CONTINUOUS TARGET (??)
# =============================================================================

@dataclass
class ContinuousTarget:
    """
    Continuous target object produced by Ω.
    
    Contains target allocations, pressures, and predictions.
    """
    
    # Target allocations (real-valued)
    target_allocations: Dict[int, float] = field(default_factory=dict)
    
    # Reserve pressures (positive = add reserve, negative = release)
    reserve_pressures: Dict[int, float] = field(default_factory=dict)
    
    # Migration pressures (task_id → node preference scores)
    migration_pressures: Dict[int, Dict[int, float]] = field(default_factory=dict)
    
    # Predictions
    predicted_latencies: Dict[int, float] = field(default_factory=dict)
    predicted_objectives: Optional[ObjectiveValues] = None
    
    # Rankings
    donor_ranking: List[int] = field(default_factory=list)      # Nodes with slack
    receiver_ranking: List[int] = field(default_factory=list)   # Nodes needing help


# =============================================================================
# HIERARCHY STRUCTURE (ℋ)
# =============================================================================

@dataclass
class NodePool:
    """A pool of nodes for hierarchical reasoning."""
    pool_id: int
    node_ids: List[int] = field(default_factory=list)
    task_ids: List[int] = field(default_factory=list)
    
    # Aggregate metrics
    total_capacity: float = 0.0
    total_used: float = 0.0
    violation_count: int = 0


@dataclass
class HierarchyStructure:
    """
    Hierarchical structure produced by Ψ.
    
    Contains pools, partitions, and multi-scale summaries.
    """
    
    # Node pools
    pools: Dict[int, NodePool] = field(default_factory=dict)
    
    # Hotspots (nodes with high violations)
    hotspot_nodes: List[int] = field(default_factory=list)
    
    # Separation candidates (tasks to consider for migration)
    separation_candidates: List[Tuple[int, int]] = field(default_factory=list)
    
    # Cross-pool migration suggestions
    cross_pool_migrations: List[Tuple[int, int, int]] = field(default_factory=list)


# =============================================================================
# STOCHASTIC KERNEL (??)
# =============================================================================

@dataclass
class StochasticKernel:
    """
    Stochastic kernel for exploration (Σ operator output).
    
    Represents distribution over candidate actions for safe probes.
    """
    
    # Candidate actions with probabilities
    candidates: List[Tuple[Action, float]] = field(default_factory=list)
    
    # Probe budget
    max_probes: int = 1
    
    def sample(self, n: int = 1) -> List[Action]:
        """Sample actions from the kernel."""
        if not self.candidates:
            return []
        
        actions, probs = zip(*self.candidates)
        
        # Normalize probabilities
        total = sum(probs)
        if total <= 0:
            return []
        
        probs = [p / total for p in probs]
        
        # Sample
        sampled = []
        for _ in range(min(n, len(actions))):
            r = random.random()
            cumsum = 0.0
            for action, prob in zip(actions, probs):
                cumsum += prob
                if r <= cumsum:
                    sampled.append(action)
                    break
        
        return sampled


# =============================================================================
# DISCRETE OPERATOR (D)
# =============================================================================

@dataclass
class DiscreteOperator:
    """
    D operator: Maps continuous targets to discrete action plans.
    
    D: ?? × ?? → ??
    
    Converts continuous targets into bounded discrete moves
    while enforcing feasibility constraints and action budgets.
    """
    
    trust_region: TrustRegion = field(default_factory=TrustRegion)
    
    # Action budgets per tick
    max_moves: int = 5
    max_migrations: int = 2
    
    def project_allocation(self, task: TaskState, target: float) -> Optional[Action]:
        """
        Project continuous allocation target to discrete action.
        
        Returns SCALE_UP or SCALE_DOWN action, or None if no change needed.
        """
        delta = target - task.allocation
        
        # Apply trust region
        delta = self.trust_region.clip_allocation_delta(delta)
        
        # Check bounds
        new_alloc = task.bounds.clip(task.allocation + delta)
        delta = new_alloc - task.allocation
        
        # Minimum threshold
        if abs(delta) < 0.1:
            return None
        
        if delta > 0:
            return Action(ActionType.SCALE_UP, task.task_id, delta=delta)
        else:
            return Action(ActionType.SCALE_DOWN, task.task_id, delta=abs(delta))
    
    def project_reserve(self, task: TaskState, pressure: float) -> Optional[Action]:
        """
        Project reserve pressure to discrete action.
        
        Returns RESERVE_UP or RESERVE_DOWN action, or None.
        """
        # Apply trust region
        delta = self.trust_region.clip_reserve_delta(pressure)
        
        # Check nonnegativity
        if task.reserve + delta < 0:
            delta = -task.reserve
        
        # Minimum threshold
        if abs(delta) < 0.1:
            return None
        
        if delta > 0:
            return Action(ActionType.RESERVE_UP, task.task_id, delta=delta)
        else:
            return Action(ActionType.RESERVE_DOWN, task.task_id, delta=abs(delta))
    
    def project_migration(self, task: TaskState,
                         node_scores: Dict[int, float]) -> Optional[Action]:
        """
        Project migration pressure to discrete action.
        
        Selects best node if migration is beneficial.
        """
        if not node_scores:
            return None
        
        current_node = task.placement
        current_score = node_scores.get(current_node, 0.0)
        
        # Find best alternative
        best_node = current_node
        best_score = current_score
        
        for node_id, score in node_scores.items():
            if score > best_score:
                best_score = score
                best_node = node_id
        
        # Only migrate if significantly better
        if best_node != current_node and best_score > current_score + 0.1:
            return Action(ActionType.MIGRATE, task.task_id, target_node=best_node)
        
        return None
    
    def apply(self, state: ControllerState, target: ContinuousTarget) -> Plan:
        """
        Apply D operator: Convert continuous target to discrete plan.
        """
        actions = []
        move_count = 0
        migration_count = 0
        
        # Process allocation targets
        for task_id, target_alloc in target.target_allocations.items():
            if move_count >= self.max_moves:
                break
            
            task = state.get_task(task_id)
            if task and not task.is_on_cooldown():
                action = self.project_allocation(task, target_alloc)
                if action:
                    actions.append(action)
                    move_count += 1
        
        # Process reserve pressures
        for task_id, pressure in target.reserve_pressures.items():
            if move_count >= self.max_moves:
                break
            
            task = state.get_task(task_id)
            if task and not task.is_on_cooldown():
                action = self.project_reserve(task, pressure)
                if action:
                    actions.append(action)
                    move_count += 1
        
        # Process migrations
        for task_id, node_scores in target.migration_pressures.items():
            if migration_count >= self.max_migrations:
                break
            
            task = state.get_task(task_id)
            if task and not task.is_on_cooldown():
                action = self.project_migration(task, node_scores)
                if action:
                    actions.append(action)
                    migration_count += 1
        
        return Plan(actions=actions)


# =============================================================================
# CONTINUOUS OPERATOR (Ω)
# =============================================================================

@dataclass
class ContinuousOperator:
    """
    Ω operator: Predictive modeling and continuous target construction.
    
    Ω: ?? × ?? → ??
    
    Solves approximate continuous subproblems and constructs targets.
    """
    
    sla_threshold: float = 100.0
    
    # Predictor
    predictor: ObjectivePredictor = field(default_factory=ObjectivePredictor)
    
    def compute_target_allocation(self, task: TaskState,
                                  record: TelemetryRecord) -> float:
        """
        Compute target allocation for a task.
        
        Uses marginal benefit analysis to determine optimal allocation.
        """
        current = task.allocation
        
        # If violating SLA, compute allocation needed to meet target
        if record.latency > self.sla_threshold:
            # Simple proportional controller
            ratio = record.latency / self.sla_threshold
            target = current * ratio
            return min(target, task.bounds.upper)
        
        # If well under SLA, consider reducing
        if record.latency < self.sla_threshold * 0.5:
            # Conservative reduction
            return max(task.bounds.lower, current * 0.9)
        
        return current
    
    def compute_reserve_pressure(self, task: TaskState,
                                record: TelemetryRecord) -> float:
        """
        Compute reserve pressure for a task.
        
        Positive = need more headroom, Negative = can release
        """
        # If near threshold, add reserve
        if record.latency > self.sla_threshold * 0.8:
            return 5.0
        
        # If violating, more reserve
        if record.latency > self.sla_threshold:
            return 10.0
        
        # If far from threshold, can release
        if record.latency < self.sla_threshold * 0.5 and task.reserve > 0:
            return -task.reserve * 0.5
        
        return 0.0
    
    def compute_node_ranking(self, state: ControllerState,
                            obs: Observation) -> Tuple[List[int], List[int]]:
        """
        Compute donor and receiver node rankings.
        
        Donors: nodes with slack capacity and good performance
        Receivers: nodes with violations or near capacity
        """
        donors = []
        receivers = []
        
        for node in state.nodes.values():
            node_tasks = state.get_node_tasks(node.node_id)
            violation_count = sum(
                1 for t in node_tasks
                if obs.get_task(t.task_id) and obs.get_task(t.task_id).latency > self.sla_threshold
            )
            
            if violation_count > 0:
                receivers.append((node.node_id, violation_count))
            elif node.utilization < 0.7:
                donors.append((node.node_id, node.available))
        
        # Sort by priority
        donors.sort(key=lambda x: -x[1])  # Most available first
        receivers.sort(key=lambda x: -x[1])  # Most violations first
        
        return [d[0] for d in donors], [r[0] for r in receivers]
    
    def apply(self, state: ControllerState, obs: Observation) -> ContinuousTarget:
        """
        Apply Ω operator: Construct continuous target from state and observation.
        """
        target = ContinuousTarget()
        
        for task_id, task in state.tasks.items():
            record = obs.get_task(task_id)
            if not record:
                continue
            
            # Compute target allocation
            target.target_allocations[task_id] = self.compute_target_allocation(task, record)
            
            # Compute reserve pressure
            target.reserve_pressures[task_id] = self.compute_reserve_pressure(task, record)
            
            # Predict latency
            interf = state.compute_interference_score(task_id)
            target.predicted_latencies[task_id] = self.predictor.predict_latency(
                task_id, task.effective_allocation, record.backlog_norm, interf, task.theta
            )
        
        # Compute node rankings
        target.donor_ranking, target.receiver_ranking = self.compute_node_ranking(state, obs)
        
        return target


# =============================================================================
# STOCHASTIC OPERATOR (Σ)
# =============================================================================

@dataclass
class StochasticOperator:
    """
    Σ operator: Certificate-constrained exploration.
    
    Σ: ?? × ?? → ??
    
    Generates safe exploration probes to improve model identification.
    """
    
    # Exploration parameters
    exploration_rate: float = 0.1
    probe_budget: int = 1
    
    # Confidence threshold for exploration
    confidence_threshold: float = 0.5
    
    def identify_exploration_needs(self, state: ControllerState,
                                   obs: Observation) -> List[int]:
        """
        Identify tasks that need exploration.
        
        Low confidence interference estimates trigger exploration.
        """
        needs_exploration = []
        
        for task_id, task in state.tasks.items():
            # Check if interference confidence is low
            node_tasks = state.get_node_tasks(task.placement)
            for other in node_tasks:
                if other.task_id != task_id:
                    conf = state.get_confidence(task_id, other.task_id)
                    if conf < self.confidence_threshold:
                        needs_exploration.append(task_id)
                        break
        
        return needs_exploration
    
    def generate_probe_candidates(self, state: ControllerState,
                                 task_ids: List[int]) -> List[Tuple[Action, float]]:
        """
        Generate candidate probe actions.
        
        Small perturbations to improve identification.
        """
        candidates = []
        
        for task_id in task_ids:
            task = state.get_task(task_id)
            if not task or task.is_on_cooldown():
                continue
            
            # Small scale up probe
            if task.allocation + 2.0 <= task.bounds.upper:
                action = Action(ActionType.SCALE_UP, task_id, delta=2.0)
                candidates.append((action, 0.5))
            
            # Small scale down probe
            if task.allocation - 2.0 >= task.bounds.lower:
                action = Action(ActionType.SCALE_DOWN, task_id, delta=2.0)
                candidates.append((action, 0.5))
        
        return candidates
    
    def apply(self, state: ControllerState, obs: Observation) -> StochasticKernel:
        """
        Apply Σ operator: Generate exploration kernel.
        """
        # Decide if exploration is needed
        if random.random() > self.exploration_rate:
            return StochasticKernel()  # No exploration this tick
        
        # Identify tasks needing exploration
        exploration_needs = self.identify_exploration_needs(state, obs)
        
        if not exploration_needs:
            return StochasticKernel()
        
        # Generate probe candidates
        candidates = self.generate_probe_candidates(state, exploration_needs)
        
        return StochasticKernel(
            candidates=candidates,
            max_probes=self.probe_budget
        )


# =============================================================================
# RECURSIVE OPERATOR (Ψ)
# =============================================================================

@dataclass
class RecursiveOperator:
    """
    Ψ operator: Hierarchical/structural reasoning.
    
    Ψ: ?? × ?? → ℋ
    
    Handles node pools, hotspots, and separation logic.
    """
    
    sla_threshold: float = 100.0
    
    # Hotspot thresholds
    hotspot_violation_threshold: int = 2
    hotspot_utilization_threshold: float = 0.9
    
    def identify_hotspots(self, state: ControllerState,
                         obs: Observation) -> List[int]:
        """
        Identify hotspot nodes.
        
        A node is a hotspot if it has high violations or high utilization.
        """
        hotspots = []
        
        for node in state.nodes.values():
            node_tasks = state.get_node_tasks(node.node_id)
            
            # Count violations
            violation_count = sum(
                1 for t in node_tasks
                if obs.get_task(t.task_id) and obs.get_task(t.task_id).latency > self.sla_threshold
            )
            
            if violation_count >= self.hotspot_violation_threshold:
                hotspots.append(node.node_id)
            elif node.utilization >= self.hotspot_utilization_threshold:
                hotspots.append(node.node_id)
        
        return hotspots
    
    def identify_separation_candidates(self, state: ControllerState,
                                       hotspots: List[int]) -> List[Tuple[int, int]]:
        """
        Identify task pairs that should be separated.
        
        High-interference pairs on hotspot nodes.
        """
        candidates = []
        
        for node_id in hotspots:
            node_tasks = state.get_node_tasks(node_id)
            
            # Find high-interference pairs
            for i, t1 in enumerate(node_tasks):
                for t2 in node_tasks[i+1:]:
                    interf = state.get_interference(t1.task_id, t2.task_id)
                    if interf > 0.5:  # High interference threshold
                        candidates.append((t1.task_id, t2.task_id))
        
        return candidates
    
    def create_pools(self, state: ControllerState) -> Dict[int, NodePool]:
        """
        Create node pools for hierarchical reasoning.
        
        Simple pooling by node index (could be more sophisticated).
        """
        pools = {}
        pool_size = max(1, len(state.nodes) // 2)
        
        for i, node in enumerate(state.nodes.values()):
            pool_id = i // pool_size
            
            if pool_id not in pools:
                pools[pool_id] = NodePool(pool_id=pool_id)
            
            pool = pools[pool_id]
            pool.node_ids.append(node.node_id)
            pool.total_capacity += node.capacity
            pool.total_used += node.used
            
            for task in state.get_node_tasks(node.node_id):
                pool.task_ids.append(task.task_id)
        
        return pools
    
    def apply(self, state: ControllerState, obs: Observation) -> HierarchyStructure:
        """
        Apply Ψ operator: Build hierarchical structure.
        """
        hierarchy = HierarchyStructure()
        
        # Create pools
        hierarchy.pools = self.create_pools(state)
        
        # Identify hotspots
        hierarchy.hotspot_nodes = self.identify_hotspots(state, obs)
        
        # Identify separation candidates
        hierarchy.separation_candidates = self.identify_separation_candidates(
            state, hierarchy.hotspot_nodes
        )
        
        return hierarchy


# =============================================================================
# QUAD-POLAR ENGINE
# =============================================================================

@dataclass
class QuadPolarHDCSEngine:
    """
    Complete Quad-Polar Engine for HDCS.
    
    Combines D, Ω, Σ, Ψ operators into a unified control system.
    
    ??(x, o) = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ
    """
    
    # Operators
    discrete: DiscreteOperator = field(default_factory=DiscreteOperator)
    continuous: ContinuousOperator = field(default_factory=ContinuousOperator)
    stochastic: StochasticOperator = field(default_factory=StochasticOperator)
    recursive: RecursiveOperator = field(default_factory=RecursiveOperator)
    
    # Operator weights (strategy-dependent)
    alpha_d: float = 1.0
    alpha_omega: float = 1.0
    alpha_sigma: float = 0.1
    alpha_psi: float = 1.0
    
    def apply(self, state: ControllerState, obs: Observation) -> Tuple[Plan, ContinuousTarget, HierarchyStructure]:
        """
        Apply complete quad-polar control.
        
        Returns (plan, target, hierarchy)
        """
        # Ψ: Build hierarchical structure
        hierarchy = self.recursive.apply(state, obs)
        
        # Ω: Construct continuous targets
        target = self.continuous.apply(state, obs)
        
        # Σ: Generate exploration kernel
        kernel = self.stochastic.apply(state, obs)
        
        # D: Project to discrete plan
        plan = self.discrete.apply(state, target)
        
        # Add exploration probes if any
        if kernel.candidates and self.alpha_sigma > 0:
            probes = kernel.sample(kernel.max_probes)
            plan.actions.extend(probes)
        
        return plan, target, hierarchy


# =============================================================================
# VALIDATION
# =============================================================================

def validate_operators() -> bool:
    """Validate HDCS operators module."""
    from .primitives import create_controller_state
    
    # Create test state
    state = create_controller_state(n_tasks=6, n_nodes=2)
    
    # Create test observation
    obs = Observation(tick=0)
    for task_id in state.tasks:
        obs.task_telemetry[task_id] = TelemetryRecord(
            task_id=task_id, tick=0,
            latency=50.0 + task_id * 20,  # Varying latency
            backlog=100.0,
            throughput=50.0
        )
        obs.task_telemetry[task_id].compute_backlog_norm()
    
    # Test Ω operator
    omega = ContinuousOperator(sla_threshold=100.0)
    target = omega.apply(state, obs)
    assert len(target.target_allocations) > 0
    
    # Test D operator
    d_op = DiscreteOperator()
    plan = d_op.apply(state, target)
    assert isinstance(plan, Plan)
    
    # Test Σ operator
    sigma = StochasticOperator(exploration_rate=1.0)  # Force exploration
    kernel = sigma.apply(state, obs)
    assert isinstance(kernel, StochasticKernel)
    
    # Test Ψ operator
    psi = RecursiveOperator(sla_threshold=100.0)
    hierarchy = psi.apply(state, obs)
    assert isinstance(hierarchy, HierarchyStructure)
    
    # Test complete engine
    engine = QuadPolarHDCSEngine()
    plan, target, hierarchy = engine.apply(state, obs)
    assert isinstance(plan, Plan)
    
    return True


if __name__ == "__main__":
    print("Validating HDCS Operators...")
    assert validate_operators()
    print("✓ HDCS Operators validated")
    
    # Demo
    print("\n=== HDCS Quad-Polar Operators Demo ===")
    
    print("\nOperator Algebra: ??(x, o) = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ")
    print("\n  D (Discrete): Bounded action proposals")
    print("  Ω (Continuous): Predictive modeling")
    print("  Σ (Stochastic): Certificate-constrained exploration")
    print("  Ψ (Recursive): Hierarchical reasoning")
