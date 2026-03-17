"""
ATHENA OS - HDCS Telemetry
==========================
Observation, Telemetry Processing, and Sensor Sanity

From HDCS.docx Chapter 3:

TELEMETRY TUPLE:
    o_i(t) = (y_i(t), b_i(t), e_i(t), ḃ_i(t), ẏ_i(t), ...)
    
    y_i(t)  : tail-latency statistic (e.g., p95)
    b_i(t)  : backlog
    e_i(t)  : error indicator/rate
    ḃ_i(t)  : backlog derivative
    ẏ_i(t)  : latency derivative

CONTROL TICK SEMANTICS:
    Observe → ModelUpdate → Propose → Certify → Execute → Audit

SENSOR SANITY TESTS:
    1. Nonnegativity: backlog, throughput ≥ 0
    2. Boundedness: latency finite
    3. Derivative spikes: |ẏ_i| bounded
    4. Cross-signal consistency
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import math


# =============================================================================
# TELEMETRY RECORD
# =============================================================================

@dataclass
class TelemetryRecord:
    """
    Per-task telemetry record o_i(t).
    
    Contains all observed signals for a single task at a single tick.
    """
    
    task_id: int
    tick: int
    
    # Primary signals
    latency: float = 0.0           # y_i(t) - tail latency (p95)
    throughput: float = 0.0        # thr_i(t)
    backlog: float = 0.0           # b_i(t)
    error_rate: float = 0.0        # e_i(t) - error indicator/rate
    
    # Derivatives (discrete)
    latency_derivative: float = 0.0   # ẏ_i(t)
    backlog_derivative: float = 0.0   # ḃ_i(t)
    
    # Derived features
    backlog_norm: float = 0.0      # Normalized backlog bn_i = b_i / B_ref
    
    # Validity flags
    is_valid: bool = True
    validity_issues: List[str] = field(default_factory=list)
    
    def compute_backlog_norm(self, b_ref: float = 100.0) -> float:
        """Compute normalized backlog."""
        if b_ref <= 0:
            return 0.0
        self.backlog_norm = min(1.0, max(0.0, self.backlog / b_ref))
        return self.backlog_norm


@dataclass
class NodeTelemetry:
    """Per-node aggregated telemetry."""
    
    node_id: int
    tick: int
    
    # Aggregate metrics
    total_throughput: float = 0.0
    total_backlog: float = 0.0
    avg_latency: float = 0.0
    max_latency: float = 0.0
    task_count: int = 0
    violation_count: int = 0


# =============================================================================
# OBSERVATION
# =============================================================================

@dataclass
class Observation:
    """
    Complete observation o(t) = {o_i(t)}_{i ∈ ??}.
    
    Immutable once produced for a tick.
    """
    
    tick: int
    task_telemetry: Dict[int, TelemetryRecord] = field(default_factory=dict)
    node_telemetry: Dict[int, NodeTelemetry] = field(default_factory=dict)
    
    # Global sanity
    is_valid: bool = True
    global_issues: List[str] = field(default_factory=list)
    
    def get_task(self, task_id: int) -> Optional[TelemetryRecord]:
        """Get telemetry for a specific task."""
        return self.task_telemetry.get(task_id)
    
    def get_node(self, node_id: int) -> Optional[NodeTelemetry]:
        """Get telemetry for a specific node."""
        return self.node_telemetry.get(node_id)
    
    def get_violating_tasks(self, sla_threshold: float) -> List[int]:
        """Get list of tasks violating SLA."""
        return [
            t.task_id for t in self.task_telemetry.values()
            if t.latency > sla_threshold
        ]
    
    def compute_violation_count(self, sla_threshold: float) -> int:
        """Compute V(t) = ∑_i v_i(t)."""
        return len(self.get_violating_tasks(sla_threshold))
    
    def compute_severity(self, sla_threshold: float) -> float:
        """Compute S(t) = ∑_i max(0, (y_i - L) / L)."""
        if sla_threshold <= 0:
            return 0.0
        
        severity = 0.0
        for t in self.task_telemetry.values():
            if t.latency > sla_threshold:
                severity += (t.latency - sla_threshold) / sla_threshold
        return severity


# =============================================================================
# SENSOR SANITY CHECKER
# =============================================================================

class SanitySeverity(Enum):
    """Severity of sanity check failure."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SanityIssue:
    """A single sanity check issue."""
    task_id: Optional[int]
    check_name: str
    severity: SanitySeverity
    message: str
    value: Optional[float] = None


@dataclass
class SensorSanityChecker:
    """
    Sensor sanity tests per HDCS.docx Section 3.3.4.
    
    Checks:
    1. Nonnegativity: backlog, throughput ≥ 0
    2. Boundedness: latency finite, not NaN/Inf
    3. Derivative spikes: |ẏ_i| ≤ max_derivative
    4. Cross-signal consistency
    """
    
    # Bounds
    max_latency: float = 10000.0      # Maximum plausible latency
    max_derivative: float = 1000.0     # Maximum |ẏ| before anomaly
    max_backlog: float = 1e6          # Maximum plausible backlog
    
    def check_task(self, record: TelemetryRecord) -> List[SanityIssue]:
        """Run all sanity checks on a task telemetry record."""
        issues = []
        
        # Check 1: Nonnegativity
        if record.backlog < 0:
            issues.append(SanityIssue(
                task_id=record.task_id,
                check_name="nonnegativity_backlog",
                severity=SanitySeverity.WARNING,
                message=f"Negative backlog: {record.backlog}",
                value=record.backlog
            ))
        
        if record.throughput < 0:
            issues.append(SanityIssue(
                task_id=record.task_id,
                check_name="nonnegativity_throughput",
                severity=SanitySeverity.WARNING,
                message=f"Negative throughput: {record.throughput}",
                value=record.throughput
            ))
        
        # Check 2: Boundedness
        if not math.isfinite(record.latency):
            issues.append(SanityIssue(
                task_id=record.task_id,
                check_name="boundedness_latency",
                severity=SanitySeverity.CRITICAL,
                message=f"Non-finite latency: {record.latency}",
                value=record.latency
            ))
        elif record.latency > self.max_latency:
            issues.append(SanityIssue(
                task_id=record.task_id,
                check_name="boundedness_latency",
                severity=SanitySeverity.WARNING,
                message=f"Latency exceeds max: {record.latency} > {self.max_latency}",
                value=record.latency
            ))
        
        # Check 3: Derivative spikes
        if abs(record.latency_derivative) > self.max_derivative:
            issues.append(SanityIssue(
                task_id=record.task_id,
                check_name="derivative_spike",
                severity=SanitySeverity.WARNING,
                message=f"Latency derivative spike: {record.latency_derivative}",
                value=record.latency_derivative
            ))
        
        # Check 4: Cross-signal consistency
        if record.backlog > self.max_backlog and record.throughput == 0:
            issues.append(SanityIssue(
                task_id=record.task_id,
                check_name="cross_signal_backlog_throughput",
                severity=SanitySeverity.WARNING,
                message=f"High backlog with zero throughput: b={record.backlog}",
                value=record.backlog
            ))
        
        return issues
    
    def check_observation(self, obs: Observation) -> Tuple[bool, List[SanityIssue]]:
        """
        Run sanity checks on complete observation.
        
        Returns (is_valid, issues).
        """
        all_issues = []
        has_critical = False
        
        for record in obs.task_telemetry.values():
            issues = self.check_task(record)
            all_issues.extend(issues)
            
            # Mark record validity
            record.validity_issues = [i.message for i in issues]
            record.is_valid = not any(i.severity == SanitySeverity.CRITICAL for i in issues)
            
            if not record.is_valid:
                has_critical = True
        
        obs.global_issues = [i.message for i in all_issues if i.severity in [SanitySeverity.ERROR, SanitySeverity.CRITICAL]]
        obs.is_valid = not has_critical
        
        return obs.is_valid, all_issues


# =============================================================================
# TELEMETRY PROCESSOR
# =============================================================================

@dataclass
class TelemetryProcessor:
    """
    Processes raw telemetry into normalized observation.
    
    Implements: Ingest: O_prod → O
    """
    
    # Normalization constants
    backlog_reference: float = 100.0   # B_ref for backlog normalization
    latency_window: int = 10           # Window for derivative smoothing
    
    # History for derivative computation
    latency_history: Dict[int, List[float]] = field(default_factory=dict)
    backlog_history: Dict[int, List[float]] = field(default_factory=dict)
    
    # Sanity checker
    sanity_checker: SensorSanityChecker = field(default_factory=SensorSanityChecker)
    
    def compute_derivative(self, history: List[float], new_value: float) -> float:
        """Compute discrete derivative using finite differences."""
        if not history:
            return 0.0
        
        # Simple finite difference
        prev = history[-1]
        return new_value - prev
    
    def update_history(self, task_id: int, latency: float, backlog: float) -> None:
        """Update history buffers for derivative computation."""
        if task_id not in self.latency_history:
            self.latency_history[task_id] = []
        if task_id not in self.backlog_history:
            self.backlog_history[task_id] = []
        
        self.latency_history[task_id].append(latency)
        self.backlog_history[task_id].append(backlog)
        
        # Trim to window size
        if len(self.latency_history[task_id]) > self.latency_window:
            self.latency_history[task_id] = self.latency_history[task_id][-self.latency_window:]
        if len(self.backlog_history[task_id]) > self.latency_window:
            self.backlog_history[task_id] = self.backlog_history[task_id][-self.latency_window:]
    
    def process_raw(self, tick: int, raw_data: Dict[int, Dict[str, float]]) -> Observation:
        """
        Process raw telemetry data into an Observation.
        
        raw_data: {task_id: {"latency": float, "throughput": float, "backlog": float, "error_rate": float}}
        """
        obs = Observation(tick=tick)
        
        for task_id, data in raw_data.items():
            latency = data.get("latency", 0.0)
            throughput = data.get("throughput", 0.0)
            backlog = data.get("backlog", 0.0)
            error_rate = data.get("error_rate", 0.0)
            
            # Compute derivatives
            latency_deriv = self.compute_derivative(
                self.latency_history.get(task_id, []), latency
            )
            backlog_deriv = self.compute_derivative(
                self.backlog_history.get(task_id, []), backlog
            )
            
            # Update history
            self.update_history(task_id, latency, backlog)
            
            # Create record
            record = TelemetryRecord(
                task_id=task_id,
                tick=tick,
                latency=latency,
                throughput=throughput,
                backlog=backlog,
                error_rate=error_rate,
                latency_derivative=latency_deriv,
                backlog_derivative=backlog_deriv
            )
            
            # Compute normalized backlog
            record.compute_backlog_norm(self.backlog_reference)
            
            obs.task_telemetry[task_id] = record
        
        # Run sanity checks
        self.sanity_checker.check_observation(obs)
        
        return obs
    
    def aggregate_node_telemetry(self, obs: Observation,
                                  node_tasks: Dict[int, List[int]],
                                  sla_threshold: float) -> None:
        """Aggregate task telemetry into node telemetry."""
        for node_id, task_ids in node_tasks.items():
            node_tel = NodeTelemetry(node_id=node_id, tick=obs.tick)
            
            latencies = []
            for task_id in task_ids:
                record = obs.get_task(task_id)
                if record:
                    node_tel.total_throughput += record.throughput
                    node_tel.total_backlog += record.backlog
                    latencies.append(record.latency)
                    if record.latency > sla_threshold:
                        node_tel.violation_count += 1
            
            node_tel.task_count = len(task_ids)
            if latencies:
                node_tel.avg_latency = sum(latencies) / len(latencies)
                node_tel.max_latency = max(latencies)
            
            obs.node_telemetry[node_id] = node_tel


# =============================================================================
# VALIDATION
# =============================================================================

def validate_telemetry() -> bool:
    """Validate HDCS telemetry module."""
    
    # Test TelemetryRecord
    record = TelemetryRecord(task_id=0, tick=0, latency=50.0, backlog=200.0)
    record.compute_backlog_norm(b_ref=100.0)
    assert record.backlog_norm == 1.0  # Clipped to 1.0
    
    # Test Observation
    obs = Observation(tick=0)
    obs.task_telemetry[0] = TelemetryRecord(task_id=0, tick=0, latency=50.0)
    obs.task_telemetry[1] = TelemetryRecord(task_id=1, tick=0, latency=150.0)
    
    violating = obs.get_violating_tasks(sla_threshold=100.0)
    assert violating == [1]
    assert obs.compute_violation_count(100.0) == 1
    assert obs.compute_severity(100.0) == 0.5  # (150-100)/100
    
    # Test SensorSanityChecker
    checker = SensorSanityChecker()
    
    # Valid record
    valid_record = TelemetryRecord(task_id=0, tick=0, latency=50.0, backlog=100.0, throughput=10.0)
    issues = checker.check_task(valid_record)
    assert len(issues) == 0
    
    # Invalid records
    invalid_record = TelemetryRecord(task_id=0, tick=0, latency=float('inf'), backlog=-10.0)
    issues = checker.check_task(invalid_record)
    assert len(issues) >= 2  # At least latency and backlog issues
    
    # Test TelemetryProcessor
    processor = TelemetryProcessor()
    
    raw_data = {
        0: {"latency": 50.0, "throughput": 100.0, "backlog": 50.0, "error_rate": 0.01},
        1: {"latency": 75.0, "throughput": 80.0, "backlog": 100.0, "error_rate": 0.02},
    }
    
    obs = processor.process_raw(tick=0, raw_data=raw_data)
    assert len(obs.task_telemetry) == 2
    assert obs.is_valid
    
    # Process another tick to test derivatives
    raw_data_2 = {
        0: {"latency": 60.0, "throughput": 100.0, "backlog": 60.0, "error_rate": 0.01},
        1: {"latency": 80.0, "throughput": 80.0, "backlog": 110.0, "error_rate": 0.02},
    }
    
    obs_2 = processor.process_raw(tick=1, raw_data=raw_data_2)
    assert obs_2.get_task(0).latency_derivative == 10.0  # 60 - 50
    
    return True


if __name__ == "__main__":
    print("Validating HDCS Telemetry...")
    assert validate_telemetry()
    print("✓ HDCS Telemetry validated")
    
    # Demo
    print("\n=== HDCS Telemetry Demo ===")
    
    processor = TelemetryProcessor()
    
    raw_data = {
        0: {"latency": 50.0, "throughput": 100.0, "backlog": 50.0},
        1: {"latency": 120.0, "throughput": 80.0, "backlog": 200.0},
        2: {"latency": 80.0, "throughput": 90.0, "backlog": 75.0},
    }
    
    obs = processor.process_raw(tick=0, raw_data=raw_data)
    
    print(f"\nObservation (tick {obs.tick}):")
    print(f"  Valid: {obs.is_valid}")
    
    sla = 100.0
    print(f"\nSLA Threshold: {sla}")
    print(f"  Violation Count V(t): {obs.compute_violation_count(sla)}")
    print(f"  Severity S(t): {obs.compute_severity(sla):.3f}")
    
    print("\nTask Telemetry:")
    for task_id, record in obs.task_telemetry.items():
        violation = "✗ VIOLATING" if record.latency > sla else "✓"
        print(f"  Task {task_id}: latency={record.latency:.1f} {violation}")
