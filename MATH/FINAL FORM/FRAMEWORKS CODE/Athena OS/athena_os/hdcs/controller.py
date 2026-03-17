"""
ATHENA OS - HDCS Controller
===========================
Main Control Loop and Meta-Controller

From HDCS.docx Chapters 1, 13, 17:

CONTROL TICK SEMANTICS:
    Observe → ModelUpdate → Propose → Certify → Execute → Audit

META-CONTROLLER STRATEGIES:
    NONE: No action (empty plan)
    D: Discrete housekeeping only
    D+Ω: Enable continuous targets
    D+Ω+Ψ: Enable hierarchical reasoning
    D+Ω+Ψ+Σ: Full quad-polar with exploration

STRATEGY SELECTION:
    Based on violation trends, model confidence, and regime detection
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import math

from .primitives import (
    ControllerState, TaskState, Node, Plan, Action, ActionType,
    create_controller_state
)
from .telemetry import Observation, TelemetryProcessor, TelemetryRecord
from .objectives import (
    ObjectiveValues, ObjectiveCalculator, ObjectivePredictor, DominanceChecker
)
from .operators import (
    QuadPolarHDCSEngine, DiscreteOperator, ContinuousOperator,
    StochasticOperator, RecursiveOperator,
    ContinuousTarget, HierarchyStructure
)
from .certificates import PlanCertificate, CertificateResult, CertificateStatus


# =============================================================================
# STRATEGY DEFINITIONS
# =============================================================================

class Strategy(Enum):
    """Meta-controller strategy set."""
    NONE = "none"              # No action
    D = "d"                    # Discrete only
    D_OMEGA = "d_omega"        # D + Ω
    D_OMEGA_PSI = "d_omega_psi"    # D + Ω + Ψ
    FULL = "full"              # D + Ω + Ψ + Σ


@dataclass
class StrategyConfig:
    """Configuration for a strategy."""
    
    strategy: Strategy
    
    # Operator enablement
    enable_d: bool = True
    enable_omega: bool = False
    enable_psi: bool = False
    enable_sigma: bool = False
    
    # Strategy-specific parameters
    exploration_rate: float = 0.0
    max_moves: int = 5
    max_migrations: int = 2
    
    @classmethod
    def from_strategy(cls, strategy: Strategy) -> 'StrategyConfig':
        """Create config from strategy enum."""
        configs = {
            Strategy.NONE: cls(strategy, enable_d=False),
            Strategy.D: cls(strategy, enable_d=True),
            Strategy.D_OMEGA: cls(strategy, enable_d=True, enable_omega=True),
            Strategy.D_OMEGA_PSI: cls(strategy, enable_d=True, enable_omega=True, enable_psi=True),
            Strategy.FULL: cls(strategy, enable_d=True, enable_omega=True, enable_psi=True,
                              enable_sigma=True, exploration_rate=0.1),
        }
        return configs.get(strategy, cls(strategy))


# =============================================================================
# AUDIT LEDGER
# =============================================================================

@dataclass
class AuditEntry:
    """Single entry in the audit ledger."""
    
    tick: int
    strategy: Strategy
    
    # Input summary
    violation_count: int
    severity: float
    
    # Plan summary
    proposed_actions: int
    certified_actions: int
    certificate_status: CertificateStatus
    certificate_reason: str
    
    # Objective predictions
    baseline_objectives: Optional[ObjectiveValues] = None
    predicted_objectives: Optional[ObjectiveValues] = None
    
    # Execution status
    executed: bool = False
    execution_errors: List[str] = field(default_factory=list)


@dataclass
class AuditLedger:
    """Audit ledger for controller decisions."""
    
    entries: List[AuditEntry] = field(default_factory=list)
    
    def add(self, entry: AuditEntry) -> None:
        """Add entry to ledger."""
        self.entries.append(entry)
    
    def get_tick(self, tick: int) -> Optional[AuditEntry]:
        """Get entry for specific tick."""
        for e in self.entries:
            if e.tick == tick:
                return e
        return None
    
    def get_recent(self, n: int = 10) -> List[AuditEntry]:
        """Get n most recent entries."""
        return self.entries[-n:]
    
    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.entries:
            return {}
        
        accepted = sum(1 for e in self.entries if e.certificate_status == CertificateStatus.ACCEPTED)
        rejected = sum(1 for e in self.entries if e.certificate_status == CertificateStatus.REJECTED)
        
        return {
            "total_ticks": len(self.entries),
            "accepted": accepted,
            "rejected": rejected,
            "acceptance_rate": accepted / len(self.entries) if self.entries else 0,
            "avg_violations": sum(e.violation_count for e in self.entries) / len(self.entries),
        }


# =============================================================================
# META-CONTROLLER
# =============================================================================

@dataclass
class MetaController:
    """
    Meta-controller for strategy selection.
    
    Selects among strategies based on:
    - Violation trends
    - Model confidence
    - Regime detection
    """
    
    # Current strategy
    current_strategy: Strategy = Strategy.D_OMEGA
    
    # Strategy history
    strategy_history: List[Tuple[int, Strategy]] = field(default_factory=list)
    
    # Macro window for strategy evaluation
    macro_window: int = 10
    
    # Violation history
    violation_history: List[int] = field(default_factory=list)
    
    # Thresholds
    escalation_threshold: int = 3    # Violations to escalate
    deescalation_threshold: int = 0  # Violations to de-escalate
    
    def update(self, tick: int, objectives: ObjectiveValues,
              model_confidence: float) -> Strategy:
        """
        Update strategy based on current state.
        
        Returns selected strategy for this tick.
        """
        # Update history
        self.violation_history.append(objectives.violation_count)
        if len(self.violation_history) > self.macro_window:
            self.violation_history = self.violation_history[-self.macro_window:]
        
        # Compute trend
        if len(self.violation_history) >= 2:
            recent = self.violation_history[-3:] if len(self.violation_history) >= 3 else self.violation_history
            trend = sum(recent) / len(recent)
        else:
            trend = objectives.violation_count
        
        # Strategy selection logic
        new_strategy = self._select_strategy(objectives.violation_count, trend, model_confidence)
        
        if new_strategy != self.current_strategy:
            self.strategy_history.append((tick, new_strategy))
            self.current_strategy = new_strategy
        
        return self.current_strategy
    
    def _select_strategy(self, current_violations: int, trend: float,
                        confidence: float) -> Strategy:
        """Select strategy based on metrics."""
        
        # If no violations and trend is low, use minimal strategy
        if current_violations == 0 and trend < 0.5:
            return Strategy.D  # Just housekeeping
        
        # If low violations, use D+Ω
        if current_violations <= 1:
            return Strategy.D_OMEGA
        
        # If moderate violations, add Ψ for structure
        if current_violations <= self.escalation_threshold:
            return Strategy.D_OMEGA_PSI
        
        # If high violations and low confidence, add Σ for exploration
        if confidence < 0.5:
            return Strategy.FULL
        
        # Otherwise use D+Ω+Ψ
        return Strategy.D_OMEGA_PSI
    
    def get_config(self) -> StrategyConfig:
        """Get configuration for current strategy."""
        return StrategyConfig.from_strategy(self.current_strategy)


# =============================================================================
# HDCS CONTROLLER
# =============================================================================

@dataclass
class HDCSController:
    """
    Complete HDCS Controller.
    
    Implements the certified quad-polar adaptive scheduling system.
    
    Control tick: Observe → ModelUpdate → Propose → Certify → Execute → Audit
    """
    
    # Configuration
    sla_threshold: float = 100.0
    
    # State
    state: ControllerState = field(default_factory=lambda: create_controller_state(4, 2))
    
    # Components
    telemetry_processor: TelemetryProcessor = field(default_factory=TelemetryProcessor)
    objective_calculator: ObjectiveCalculator = field(default_factory=ObjectiveCalculator)
    engine: QuadPolarHDCSEngine = field(default_factory=QuadPolarHDCSEngine)
    plan_certificate: PlanCertificate = field(default_factory=PlanCertificate)
    meta_controller: MetaController = field(default_factory=MetaController)
    
    # Audit
    ledger: AuditLedger = field(default_factory=AuditLedger)
    
    def __post_init__(self):
        """Initialize components with SLA threshold."""
        self.objective_calculator.sla_threshold = self.sla_threshold
        self.engine.continuous.sla_threshold = self.sla_threshold
        self.engine.recursive.sla_threshold = self.sla_threshold
        self.plan_certificate.sla_threshold = self.sla_threshold
    
    def initialize(self, n_tasks: int, n_nodes: int,
                  node_capacity: float = 100.0,
                  reserve_budget: float = 100.0) -> None:
        """Initialize controller with fresh state."""
        self.state = create_controller_state(n_tasks, n_nodes, node_capacity, reserve_budget)
    
    def tick(self, raw_telemetry: Dict[int, Dict[str, float]]) -> Tuple[Plan, CertificateResult]:
        """
        Execute one control tick.
        
        Observe → ModelUpdate → Propose → Certify → Execute → Audit
        
        Returns (certified_plan, certificate_result)
        """
        # OBSERVE
        obs = self._observe(raw_telemetry)
        
        # MODEL UPDATE
        self._update_models(obs)
        
        # Compute current objectives
        current_objectives = self.objective_calculator.compute_objectives(
            obs, Plan.empty(), self.state
        )
        
        # Update meta-controller
        model_confidence = self._compute_model_confidence()
        strategy = self.meta_controller.update(
            self.state.tick, current_objectives, model_confidence
        )
        config = self.meta_controller.get_config()
        
        # PROPOSE
        proposed_plan = self._propose(obs, config)
        
        # CERTIFY
        certified_plan, cert_result = self._certify(proposed_plan, obs)
        
        # EXECUTE (update state)
        if certified_plan.certified and not certified_plan.is_empty():
            self._execute(certified_plan)
        
        # AUDIT
        self._audit(obs, proposed_plan, certified_plan, cert_result,
                   current_objectives, strategy)
        
        # Advance tick
        self.state.tick += 1
        
        return certified_plan, cert_result
    
    def _observe(self, raw_telemetry: Dict[int, Dict[str, float]]) -> Observation:
        """OBSERVE: Process raw telemetry into observation."""
        obs = self.telemetry_processor.process_raw(self.state.tick, raw_telemetry)
        
        # Aggregate node telemetry
        node_tasks = {
            node_id: [t.task_id for t in self.state.get_node_tasks(node_id)]
            for node_id in self.state.nodes
        }
        self.telemetry_processor.aggregate_node_telemetry(obs, node_tasks, self.sla_threshold)
        
        # Update violation tracking
        self.objective_calculator.update_violations(obs)
        
        return obs
    
    def _update_models(self, obs: Observation) -> None:
        """MODEL UPDATE: Update predictive models."""
        # Update task cooldowns
        for task in self.state.tasks.values():
            task.decrement_cooldown()
        
        # Update violation persistence
        for task_id, task in self.state.tasks.items():
            record = obs.get_task(task_id)
            if record:
                is_violating = record.latency > self.sla_threshold
                task.update_violation_persistence(is_violating)
        
        # Online model updates would happen here
        # For simplicity, we skip detailed θ̂ updates
    
    def _compute_model_confidence(self) -> float:
        """Compute overall model confidence."""
        # Average confidence across interference estimates
        if not self.state.confidence_matrix:
            return 0.5  # Default
        
        confidences = list(self.state.confidence_matrix.values())
        if not confidences:
            return 0.5
        
        return sum(confidences) / len(confidences)
    
    def _propose(self, obs: Observation, config: StrategyConfig) -> Plan:
        """PROPOSE: Generate candidate plan based on strategy."""
        if not config.enable_d:
            return Plan.empty()
        
        # Configure engine based on strategy
        self.engine.alpha_d = 1.0 if config.enable_d else 0.0
        self.engine.alpha_omega = 1.0 if config.enable_omega else 0.0
        self.engine.alpha_psi = 1.0 if config.enable_psi else 0.0
        self.engine.alpha_sigma = config.exploration_rate if config.enable_sigma else 0.0
        
        # Apply quad-polar engine
        plan, target, hierarchy = self.engine.apply(self.state, obs)
        
        return plan
    
    def _certify(self, plan: Plan, obs: Observation) -> Tuple[Plan, CertificateResult]:
        """CERTIFY: Validate plan through certificate hierarchy."""
        return self.plan_certificate.certify(plan, self.state, obs)
    
    def _execute(self, plan: Plan) -> None:
        """EXECUTE: Apply certified plan to state."""
        for action in plan.actions:
            self._apply_action(action)
    
    def _apply_action(self, action: Action) -> None:
        """Apply a single action to state."""
        task = self.state.get_task(action.task_id)
        if not task:
            return
        
        node = self.state.get_node(task.placement)
        
        if action.action_type == ActionType.SCALE_UP:
            if node:
                node.allocated -= task.allocation
            task.allocation = task.bounds.clip(task.allocation + action.delta)
            if node:
                node.allocated += task.allocation
            task.set_cooldown(3)
        
        elif action.action_type == ActionType.SCALE_DOWN:
            if node:
                node.allocated -= task.allocation
            task.allocation = task.bounds.clip(task.allocation - action.delta)
            if node:
                node.allocated += task.allocation
            task.set_cooldown(3)
        
        elif action.action_type == ActionType.RESERVE_UP:
            if node:
                node.reserved -= task.reserve
            task.reserve = max(0, task.reserve + action.delta)
            if node:
                node.reserved += task.reserve
            task.set_cooldown(2)
        
        elif action.action_type == ActionType.RESERVE_DOWN:
            if node:
                node.reserved -= task.reserve
            task.reserve = max(0, task.reserve - action.delta)
            if node:
                node.reserved += task.reserve
            task.set_cooldown(2)
        
        elif action.action_type == ActionType.MIGRATE:
            # Remove from old node
            if node:
                node.allocated -= task.allocation
                node.reserved -= task.reserve
                node.task_ids.discard(task.task_id)
            
            # Add to new node
            target = self.state.get_node(action.target_node)
            if target:
                target.allocated += task.allocation
                target.reserved += task.reserve
                target.task_ids.add(task.task_id)
            
            task.placement = action.target_node
            task.set_cooldown(5)  # Longer cooldown for migrations
    
    def _audit(self, obs: Observation, proposed: Plan, certified: Plan,
              cert_result: CertificateResult, objectives: ObjectiveValues,
              strategy: Strategy) -> None:
        """AUDIT: Record decision in ledger."""
        entry = AuditEntry(
            tick=self.state.tick,
            strategy=strategy,
            violation_count=objectives.violation_count,
            severity=objectives.severity,
            proposed_actions=len(proposed.actions),
            certified_actions=len(certified.actions),
            certificate_status=cert_result.status,
            certificate_reason=cert_result.reason,
            baseline_objectives=cert_result.baseline_objectives,
            predicted_objectives=cert_result.predicted_objectives,
            executed=certified.certified and not certified.is_empty()
        )
        
        self.ledger.add(entry)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current controller status."""
        is_feasible, violations = self.state.check_feasibility()
        
        return {
            "tick": self.state.tick,
            "tasks": len(self.state.tasks),
            "nodes": len(self.state.nodes),
            "strategy": self.meta_controller.current_strategy.value,
            "feasible": is_feasible,
            "feasibility_violations": violations,
            "ledger_summary": self.ledger.summary(),
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_controller() -> bool:
    """Validate HDCS controller module."""
    
    # Create controller
    controller = HDCSController(sla_threshold=100.0)
    controller.initialize(n_tasks=4, n_nodes=2, node_capacity=100.0)
    
    # Generate test telemetry
    raw_telemetry = {
        0: {"latency": 50.0, "throughput": 100.0, "backlog": 50.0, "error_rate": 0.0},
        1: {"latency": 120.0, "throughput": 80.0, "backlog": 200.0, "error_rate": 0.01},
        2: {"latency": 80.0, "throughput": 90.0, "backlog": 75.0, "error_rate": 0.0},
        3: {"latency": 150.0, "throughput": 70.0, "backlog": 300.0, "error_rate": 0.02},
    }
    
    # Run a tick
    plan, result = controller.tick(raw_telemetry)
    
    assert isinstance(plan, Plan)
    assert isinstance(result, CertificateResult)
    assert controller.state.tick == 1
    
    # Run more ticks
    for _ in range(5):
        plan, result = controller.tick(raw_telemetry)
    
    assert controller.state.tick == 6
    assert len(controller.ledger.entries) == 6
    
    # Test MetaController
    meta = MetaController()
    obj = ObjectiveValues(violation_count=3, severity=0.5)
    strategy = meta.update(0, obj, 0.7)
    assert isinstance(strategy, Strategy)
    
    # Test StrategyConfig
    config = StrategyConfig.from_strategy(Strategy.FULL)
    assert config.enable_d
    assert config.enable_omega
    assert config.enable_psi
    assert config.enable_sigma
    
    return True


if __name__ == "__main__":
    print("Validating HDCS Controller...")
    assert validate_controller()
    print("✓ HDCS Controller validated")
    
    # Demo
    print("\n=== HDCS Controller Demo ===")
    
    controller = HDCSController(sla_threshold=100.0)
    controller.initialize(n_tasks=6, n_nodes=3, node_capacity=100.0)
    
    print(f"\nInitial Status:")
    status = controller.get_status()
    print(f"  Tasks: {status['tasks']}")
    print(f"  Nodes: {status['nodes']}")
    print(f"  Strategy: {status['strategy']}")
    
    # Simulate several ticks
    print("\nSimulating 10 ticks...")
    for t in range(10):
        # Generate varying telemetry
        raw = {}
        for i in range(6):
            latency = 50.0 + i * 15 + (t % 3) * 10
            raw[i] = {"latency": latency, "throughput": 100.0, "backlog": 100.0}
        
        plan, result = controller.tick(raw)
        print(f"  Tick {t}: strategy={controller.meta_controller.current_strategy.value}, "
              f"actions={len(plan.actions)}, status={result.status.value}")
    
    print(f"\nFinal Status:")
    status = controller.get_status()
    print(f"  Strategy: {status['strategy']}")
    summary = status['ledger_summary']
    print(f"  Acceptance Rate: {summary.get('acceptance_rate', 0):.1%}")
    print(f"  Avg Violations: {summary.get('avg_violations', 0):.1f}")
