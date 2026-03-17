"""
ATHENA OS - HDCS Primitives
===========================
Task, Node, Resource, and State Primitives

From HDCS.docx Chapter 3:

SYSTEM MODEL:
    Let t ∈ ℕ index control ticks
    Let ?? = {1,...,N} be tasks
    Let ?? = {1,...,M} be nodes

TASK STATE:
    x_i(t) = (p_i, a_i, r_i, τ_i, θ̂_i, ρ_i, κ_i, ν_i, ...)
    
    p_i(t) ∈ ??          : placement (node assignment)
    a_i(t) ∈ [a̲_i, ā_i] : primary allocation
    r_i(t) ∈ ℝ≥0        : reserve allocation
    τ_i(t) ∈ ℕ          : cooldown counter
    θ̂_i(t)             : online model parameters
    ρ_i(t) ≥ 0          : uncertainty proxy
    κ_i(t) ∈ ℕ          : feasibility ticket counter
    ν_i(t) ∈ ℕ          : violation persistence counter

NODE FEASIBILITY:
    ∑_{i: p_i(t)=n} (a_i(t) + r_i(t)) ≤ C_n  ∀n ∈ ??
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import math


# =============================================================================
# ACTION PRIMITIVES
# =============================================================================

class ActionType(Enum):
    """Primitive action types for the controller."""
    NONE = "none"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RESERVE_UP = "reserve_up"
    RESERVE_DOWN = "reserve_down"
    MIGRATE = "migrate"


@dataclass
class Action:
    """A single primitive action."""
    action_type: ActionType
    task_id: int
    delta: float = 0.0  # For scale/reserve actions
    target_node: Optional[int] = None  # For migrate actions
    
    def __str__(self) -> str:
        if self.action_type == ActionType.MIGRATE:
            return f"{self.action_type.value}(task={self.task_id}, node={self.target_node})"
        elif self.action_type == ActionType.NONE:
            return "NONE"
        else:
            return f"{self.action_type.value}(task={self.task_id}, Δ={self.delta:.3f})"


@dataclass
class Plan:
    """A finite list of primitive actions."""
    actions: List[Action] = field(default_factory=list)
    certified: bool = False
    certificate_reason: str = ""
    
    def __len__(self) -> int:
        return len(self.actions)
    
    def is_empty(self) -> bool:
        return len(self.actions) == 0 or all(a.action_type == ActionType.NONE for a in self.actions)
    
    @classmethod
    def empty(cls) -> 'Plan':
        """Create empty (no-op) plan."""
        return cls(actions=[], certified=True, certificate_reason="empty_plan")


# =============================================================================
# RESOURCE BOUNDS
# =============================================================================

@dataclass
class AllocationBounds:
    """Bounds for task allocation."""
    lower: float = 0.0  # a̲_i
    upper: float = 100.0  # ā_i
    
    def clip(self, value: float) -> float:
        """Clip value to bounds."""
        return max(self.lower, min(self.upper, value))
    
    def is_valid(self, value: float) -> bool:
        """Check if value is within bounds."""
        return self.lower <= value <= self.upper


@dataclass
class TrustRegion:
    """Trust region for bounded actions."""
    max_delta_a: float = 10.0  # Max allocation change per tick
    max_delta_r: float = 5.0   # Max reserve change per tick
    
    def clip_allocation_delta(self, delta: float) -> float:
        return max(-self.max_delta_a, min(self.max_delta_a, delta))
    
    def clip_reserve_delta(self, delta: float) -> float:
        return max(-self.max_delta_r, min(self.max_delta_r, delta))


# =============================================================================
# NODE
# =============================================================================

@dataclass
class Node:
    """
    A compute node with capacity.
    
    Each node n ∈ ?? has capacity C_n > 0.
    Feasibility: ∑_{i: p_i=n} (a_i + r_i) ≤ C_n
    """
    
    node_id: int
    capacity: float  # C_n
    
    # Current state
    allocated: float = 0.0  # Sum of allocations
    reserved: float = 0.0   # Sum of reserves
    task_ids: Set[int] = field(default_factory=set)
    
    @property
    def used(self) -> float:
        """Total used capacity."""
        return self.allocated + self.reserved
    
    @property
    def available(self) -> float:
        """Available capacity."""
        return max(0.0, self.capacity - self.used)
    
    @property
    def utilization(self) -> float:
        """Utilization ratio [0, 1]."""
        if self.capacity <= 0:
            return 1.0
        return min(1.0, self.used / self.capacity)
    
    def is_feasible(self) -> bool:
        """Check if node capacity constraint is satisfied."""
        return self.used <= self.capacity
    
    def can_add(self, allocation: float, reserve: float) -> bool:
        """Check if additional allocation/reserve fits."""
        return self.used + allocation + reserve <= self.capacity


# =============================================================================
# TASK STATE
# =============================================================================

@dataclass
class TaskState:
    """
    Per-task state tuple x_i(t).
    
    Contains:
    - Configuration state (placement, allocation, reserve)
    - Learned model state (θ̂, ρ)
    - Discrete gating state (τ, κ, ν)
    """
    
    task_id: int
    
    # Configuration state x_cfg
    placement: int = 0            # p_i(t) ∈ ??
    allocation: float = 1.0       # a_i(t) ∈ [a̲_i, ā_i]
    reserve: float = 0.0          # r_i(t) ∈ ℝ≥0
    
    # Allocation bounds
    bounds: AllocationBounds = field(default_factory=AllocationBounds)
    
    # Discrete gating state
    cooldown: int = 0             # τ_i(t) - suppresses reconfiguration
    ticket_counter: int = 0       # κ_i(t) - feasibility ticket
    violation_persistence: int = 0  # ν_i(t) - SLA persistence
    
    # Learned model state x_epi
    theta: List[float] = field(default_factory=lambda: [1.0, 0.0, 0.0, 0.0])
    uncertainty: float = 0.1      # ρ_i(t) - residual EMA
    
    # Feature cache
    feature_cache: Dict[str, float] = field(default_factory=dict)
    
    @property
    def effective_allocation(self) -> float:
        """Effective allocation a^eff = a + η*r (with η=1 for simplicity)."""
        return self.allocation + self.reserve
    
    def is_on_cooldown(self) -> bool:
        """Check if task is on cooldown."""
        return self.cooldown > 0
    
    def decrement_cooldown(self) -> None:
        """Decrement cooldown counter."""
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def set_cooldown(self, ticks: int) -> None:
        """Set cooldown after action."""
        self.cooldown = max(self.cooldown, ticks)
    
    def update_violation_persistence(self, is_violating: bool) -> None:
        """Update violation persistence counter."""
        if is_violating:
            self.violation_persistence += 1
        else:
            self.violation_persistence = 0
    
    def is_persistently_violating(self, threshold: int = 3) -> bool:
        """Check if task has persistent violations."""
        return self.violation_persistence >= threshold


# =============================================================================
# CONTROLLER STATE
# =============================================================================

@dataclass
class ControllerState:
    """
    Full controller state x(t).
    
    x(t) = (x_cfg(t), x_epi(t), τ(t), κ(t), ν(t))
    
    where:
    - x_cfg = (p, a, r) is physical configuration
    - x_epi = (θ̂, ρ, f, Î, conf, s) is learned internal state
    - τ, κ, ν are discrete gating states
    """
    
    tick: int = 0
    
    # Task states
    tasks: Dict[int, TaskState] = field(default_factory=dict)
    
    # Node states
    nodes: Dict[int, Node] = field(default_factory=dict)
    
    # Global learned state
    interference_matrix: Dict[Tuple[int, int], float] = field(default_factory=dict)
    confidence_matrix: Dict[Tuple[int, int], float] = field(default_factory=dict)
    sample_counts: Dict[Tuple[int, int], int] = field(default_factory=dict)
    
    # Global budgets
    reserve_budget: float = 100.0  # R - global reserve budget
    max_moves_per_tick: int = 5
    max_migrations_per_tick: int = 2
    trust_region: TrustRegion = field(default_factory=TrustRegion)
    
    def get_task(self, task_id: int) -> Optional[TaskState]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_node(self, node_id: int) -> Optional[Node]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def get_node_tasks(self, node_id: int) -> List[TaskState]:
        """Get all tasks on a node."""
        return [t for t in self.tasks.values() if t.placement == node_id]
    
    def total_reserve(self) -> float:
        """Get total reserve across all tasks."""
        return sum(t.reserve for t in self.tasks.values())
    
    def is_reserve_budget_valid(self) -> bool:
        """Check if reserve budget constraint is satisfied."""
        return self.total_reserve() <= self.reserve_budget
    
    def get_interference(self, task_i: int, task_j: int) -> float:
        """Get interference estimate Î_ij."""
        return self.interference_matrix.get((task_i, task_j), 0.0)
    
    def get_confidence(self, task_i: int, task_j: int) -> float:
        """Get confidence estimate for interference."""
        return self.confidence_matrix.get((task_i, task_j), 0.0)
    
    def compute_interference_score(self, task_id: int, conf_min: float = 0.1) -> float:
        """
        Compute interference score for a task:
        s_i = ∑_{j ∈ ??_n \ {i}} Î_ij · max(conf_min, conf̂_ij)
        """
        task = self.get_task(task_id)
        if not task:
            return 0.0
        
        node_tasks = self.get_node_tasks(task.placement)
        score = 0.0
        for other in node_tasks:
            if other.task_id != task_id:
                interference = self.get_interference(task_id, other.task_id)
                confidence = max(conf_min, self.get_confidence(task_id, other.task_id))
                score += interference * confidence
        
        return score
    
    def check_feasibility(self) -> Tuple[bool, List[str]]:
        """
        Check all feasibility constraints.
        
        Returns (is_feasible, list_of_violations)
        """
        violations = []
        
        # Check node capacities
        for node in self.nodes.values():
            # Recompute node usage from tasks
            allocated = sum(t.allocation for t in self.tasks.values() 
                          if t.placement == node.node_id)
            reserved = sum(t.reserve for t in self.tasks.values()
                         if t.placement == node.node_id)
            
            if allocated + reserved > node.capacity:
                violations.append(
                    f"Node {node.node_id}: usage {allocated + reserved:.2f} > capacity {node.capacity:.2f}"
                )
        
        # Check allocation bounds
        for task in self.tasks.values():
            if not task.bounds.is_valid(task.allocation):
                violations.append(
                    f"Task {task.task_id}: allocation {task.allocation:.2f} outside bounds [{task.bounds.lower}, {task.bounds.upper}]"
                )
        
        # Check reserve nonnegativity and budget
        for task in self.tasks.values():
            if task.reserve < 0:
                violations.append(f"Task {task.task_id}: negative reserve {task.reserve:.2f}")
        
        if self.total_reserve() > self.reserve_budget:
            violations.append(
                f"Total reserve {self.total_reserve():.2f} > budget {self.reserve_budget:.2f}"
            )
        
        return len(violations) == 0, violations


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_controller_state(n_tasks: int, n_nodes: int,
                           node_capacity: float = 100.0,
                           reserve_budget: float = 100.0) -> ControllerState:
    """Create a fresh controller state with initialized tasks and nodes."""
    state = ControllerState(reserve_budget=reserve_budget)
    
    # Create nodes
    for n in range(n_nodes):
        state.nodes[n] = Node(node_id=n, capacity=node_capacity)
    
    # Create tasks and distribute across nodes
    for i in range(n_tasks):
        node_id = i % n_nodes
        task = TaskState(
            task_id=i,
            placement=node_id,
            allocation=10.0,  # Initial allocation
            bounds=AllocationBounds(lower=1.0, upper=50.0)
        )
        state.tasks[i] = task
        state.nodes[node_id].task_ids.add(i)
        state.nodes[node_id].allocated += task.allocation
    
    return state


# =============================================================================
# VALIDATION
# =============================================================================

def validate_primitives() -> bool:
    """Validate HDCS primitives module."""
    
    # Test Action
    action = Action(ActionType.SCALE_UP, task_id=0, delta=5.0)
    assert action.action_type == ActionType.SCALE_UP
    
    migrate = Action(ActionType.MIGRATE, task_id=1, target_node=2)
    assert migrate.target_node == 2
    
    # Test Plan
    plan = Plan(actions=[action, migrate])
    assert len(plan) == 2
    assert not plan.is_empty()
    
    empty_plan = Plan.empty()
    assert empty_plan.is_empty()
    
    # Test AllocationBounds
    bounds = AllocationBounds(lower=0.0, upper=100.0)
    assert bounds.clip(-5.0) == 0.0
    assert bounds.clip(150.0) == 100.0
    assert bounds.is_valid(50.0)
    assert not bounds.is_valid(150.0)
    
    # Test Node
    node = Node(node_id=0, capacity=100.0)
    node.allocated = 50.0
    node.reserved = 20.0
    assert node.used == 70.0
    assert node.available == 30.0
    assert node.is_feasible()
    assert node.can_add(20.0, 5.0)
    assert not node.can_add(40.0, 0.0)
    
    # Test TaskState
    task = TaskState(task_id=0, placement=0, allocation=10.0)
    assert task.effective_allocation == 10.0
    task.reserve = 5.0
    assert task.effective_allocation == 15.0
    
    task.set_cooldown(3)
    assert task.is_on_cooldown()
    task.decrement_cooldown()
    assert task.cooldown == 2
    
    task.update_violation_persistence(True)
    task.update_violation_persistence(True)
    task.update_violation_persistence(True)
    assert task.is_persistently_violating(threshold=3)
    
    # Test ControllerState
    state = create_controller_state(n_tasks=10, n_nodes=3)
    assert len(state.tasks) == 10
    assert len(state.nodes) == 3
    
    is_feasible, violations = state.check_feasibility()
    assert is_feasible, f"Violations: {violations}"
    
    return True


if __name__ == "__main__":
    print("Validating HDCS Primitives...")
    assert validate_primitives()
    print("✓ HDCS Primitives validated")
    
    # Demo
    print("\n=== HDCS Primitives Demo ===")
    
    state = create_controller_state(n_tasks=8, n_nodes=2, node_capacity=100.0)
    print(f"\nController State (tick {state.tick}):")
    print(f"  Tasks: {len(state.tasks)}")
    print(f"  Nodes: {len(state.nodes)}")
    print(f"  Reserve Budget: {state.reserve_budget}")
    
    for node in state.nodes.values():
        print(f"\n  Node {node.node_id}:")
        print(f"    Capacity: {node.capacity}")
        print(f"    Allocated: {node.allocated:.1f}")
        print(f"    Utilization: {node.utilization:.1%}")
    
    print("\nFeasibility Check:")
    is_feasible, violations = state.check_feasibility()
    print(f"  Feasible: {is_feasible}")
    if violations:
        for v in violations:
            print(f"  ✗ {v}")
