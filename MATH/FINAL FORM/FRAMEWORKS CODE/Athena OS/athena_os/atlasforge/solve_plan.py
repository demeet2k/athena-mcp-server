"""
ATHENA OS - AtlasForge: SOLVE PLAN
==================================
Explicit Construction Plans and Solver Ladders

SOLVEPLAN DEFINITION:
    An explicit object describing:
    - Chosen charts and corridor commitments
    - Solver ladders (sequence of algorithms)
    - Budgets and tolerances
    - Decision branches and tie-break rules
    
    No decision affecting replay may remain implicit.

SOLVER LADDER:
    Ordered sequence of solvers with fallback logic:
    1. Try fast/approximate solver first
    2. Fall back to robust/expensive solver
    3. Escalate to verified/certified solver
    
    Each step has budget and tolerance constraints.

CONSTRUCTION PHASES:
    1. Chart Selection - choose coordinate transformation
    2. Normalization - canonicalize problem form
    3. Solve - apply solver ladder
    4. Certify - generate proof obligations
    5. Store - persist as content-addressed artifact

REPLAY CONTRACT:
    SolvePlan must be sufficient for deterministic replay:
    - All parameters explicit
    - RNG seeds recorded
    - Tie-break rules specified
    - Platform contract documented

SOURCES:
    - AtlasForge.docx Construction Pipeline
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
import hashlib
import time


# =============================================================================
# SOLVER TYPES
# =============================================================================

class SolverType(Enum):
    """Types of solvers available."""
    
    # Root finders
    BISECTION = "bisection"
    NEWTON = "newton"
    SECANT = "secant"
    BRENT = "brent"
    RIDDER = "ridder"
    
    # Fixed point
    PICARD = "picard"
    MANN = "mann"
    KRASNOSELSKII = "krasnoselskii"
    
    # Optimization
    GRADIENT_DESCENT = "gradient_descent"
    BFGS = "bfgs"
    NELDER_MEAD = "nelder_mead"
    
    # Linear
    LU = "lu"
    QR = "qr"
    SVD = "svd"
    CHOLESKY = "cholesky"
    
    # Interval
    INTERVAL_NEWTON = "interval_newton"
    INTERVAL_BISECTION = "interval_bisection"
    
    # Custom
    CUSTOM = "custom"


class SolverTier(Enum):
    """Solver tiers for ladder construction."""
    
    FAST = "fast"           # Quick but may fail
    ROBUST = "robust"       # Reliable but slower
    CERTIFIED = "certified" # Produces certificates


class PlanPhase(Enum):
    """Phases in the construction plan."""
    
    CHART_SELECT = "chart_select"
    NORMALIZE = "normalize"
    SOLVE = "solve"
    CERTIFY = "certify"
    STORE = "store"


class TieBreakRule(Enum):
    """Rules for breaking ties in solver decisions."""
    
    FIRST = "first"           # Take first solution
    MINIMUM = "minimum"       # Take minimum value
    MAXIMUM = "maximum"       # Take maximum value
    MEDIAN = "median"         # Take median
    LEFTMOST = "leftmost"     # Leftmost in domain
    RIGHTMOST = "rightmost"   # Rightmost in domain
    DETERMINISTIC = "deterministic"  # Use deterministic hash


# =============================================================================
# SOLVER CONFIGURATION
# =============================================================================

@dataclass
class SolverConfig:
    """
    Configuration for a single solver.
    """
    
    solver_type: SolverType
    tier: SolverTier = SolverTier.ROBUST
    
    # Iteration limits
    max_iterations: int = 1000
    
    # Tolerances
    abs_tolerance: float = 1e-10
    rel_tolerance: float = 1e-10
    
    # Budget (computational)
    max_function_evals: int = 10000
    max_time_seconds: float = 60.0
    
    # Algorithm-specific parameters
    params: Dict[str, Any] = field(default_factory=dict)
    
    # RNG seed for stochastic solvers
    rng_seed: Optional[int] = None
    
    def __post_init__(self):
        # Set tier-specific defaults
        if self.tier == SolverTier.FAST:
            self.max_iterations = min(self.max_iterations, 100)
            self.abs_tolerance = max(self.abs_tolerance, 1e-6)
        elif self.tier == SolverTier.CERTIFIED:
            self.abs_tolerance = min(self.abs_tolerance, 1e-12)
    
    @property
    def config_id(self) -> str:
        """Get configuration hash."""
        content = f"{self.solver_type.value}:{self.max_iterations}:{self.abs_tolerance}"
        return hashlib.sha256(content.encode()).hexdigest()[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "solver_type": self.solver_type.value,
            "tier": self.tier.value,
            "max_iterations": self.max_iterations,
            "abs_tolerance": self.abs_tolerance,
            "rel_tolerance": self.rel_tolerance,
            "max_function_evals": self.max_function_evals,
            "params": self.params,
            "rng_seed": self.rng_seed
        }


# =============================================================================
# SOLVER LADDER
# =============================================================================

@dataclass
class SolverLadder:
    """
    Ordered sequence of solvers with fallback logic.
    
    Tries solvers in order until one succeeds.
    """
    
    name: str
    solvers: List[SolverConfig] = field(default_factory=list)
    
    # Fallback behavior
    fail_on_all_fail: bool = True
    
    # Escalation triggers
    escalate_on_slow: bool = True
    slow_threshold_seconds: float = 10.0
    
    def add_solver(self, config: SolverConfig) -> None:
        """Add a solver to the ladder."""
        self.solvers.append(config)
    
    def add_tier(self, solver_type: SolverType, tier: SolverTier,
                **kwargs) -> None:
        """Add a solver by type and tier."""
        config = SolverConfig(solver_type=solver_type, tier=tier, **kwargs)
        self.add_solver(config)
    
    @classmethod
    def root_finder_ladder(cls) -> SolverLadder:
        """Create a standard root-finding ladder."""
        ladder = cls(name="root_finder")
        
        # Fast: Secant method
        ladder.add_tier(SolverType.SECANT, SolverTier.FAST,
                       max_iterations=50)
        
        # Robust: Brent's method
        ladder.add_tier(SolverType.BRENT, SolverTier.ROBUST,
                       max_iterations=500)
        
        # Certified: Interval bisection
        ladder.add_tier(SolverType.INTERVAL_BISECTION, SolverTier.CERTIFIED,
                       max_iterations=100, abs_tolerance=1e-14)
        
        return ladder
    
    @classmethod
    def fixed_point_ladder(cls) -> SolverLadder:
        """Create a standard fixed-point ladder."""
        ladder = cls(name="fixed_point")
        
        # Fast: Picard iteration
        ladder.add_tier(SolverType.PICARD, SolverTier.FAST,
                       max_iterations=100)
        
        # Robust: Mann iteration
        ladder.add_tier(SolverType.MANN, SolverTier.ROBUST,
                       max_iterations=1000, params={"alpha": 0.5})
        
        # Certified: Krasnoselskii-Mann
        ladder.add_tier(SolverType.KRASNOSELSKII, SolverTier.CERTIFIED,
                       max_iterations=5000)
        
        return ladder
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "solvers": [s.to_dict() for s in self.solvers],
            "fail_on_all_fail": self.fail_on_all_fail,
            "escalate_on_slow": self.escalate_on_slow,
            "slow_threshold_seconds": self.slow_threshold_seconds
        }


# =============================================================================
# CHART SELECTION
# =============================================================================

@dataclass
class ChartSelection:
    """
    Chart selection decision in the solve plan.
    """
    
    chart_id: str
    chart_type: str
    
    # Corridor commitment
    corridor_lower: float
    corridor_upper: float
    
    # Selection rationale
    rationale: str = ""
    
    # Alternative charts considered
    alternatives: List[str] = field(default_factory=list)
    
    # Selection criteria scores
    scores: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "chart_type": self.chart_type,
            "corridor": [self.corridor_lower, self.corridor_upper],
            "rationale": self.rationale,
            "alternatives": self.alternatives,
            "scores": self.scores
        }


# =============================================================================
# SOLVE PLAN
# =============================================================================

@dataclass
class SolvePlan:
    """
    Explicit construction plan for solving constraints.
    
    Contains all decisions affecting replay.
    """
    
    name: str
    
    # Chart selection
    chart_selections: List[ChartSelection] = field(default_factory=list)
    
    # Solver ladders
    ladders: Dict[str, SolverLadder] = field(default_factory=dict)
    
    # Global parameters
    global_tolerance: float = 1e-10
    global_max_iterations: int = 10000
    global_timeout_seconds: float = 300.0
    
    # Tie-break rules
    tie_break_rule: TieBreakRule = TieBreakRule.DETERMINISTIC
    
    # RNG state
    master_rng_seed: int = 42
    
    # Environment contract
    platform: str = ""
    float_model: str = "ieee754"
    
    # Phase timings
    phase_budgets: Dict[PlanPhase, float] = field(default_factory=dict)
    
    # Decision log
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Creation time
    created_at: float = field(default_factory=time.time)
    
    def add_chart_selection(self, selection: ChartSelection) -> None:
        """Add a chart selection."""
        self.chart_selections.append(selection)
        self._log_decision("chart_select", selection.to_dict())
    
    def add_ladder(self, name: str, ladder: SolverLadder) -> None:
        """Add a solver ladder."""
        self.ladders[name] = ladder
        self._log_decision("add_ladder", {"name": name})
    
    def set_phase_budget(self, phase: PlanPhase, budget: float) -> None:
        """Set time budget for a phase."""
        self.phase_budgets[phase] = budget
    
    def _log_decision(self, decision_type: str, data: Dict[str, Any]) -> None:
        """Log a decision."""
        self.decisions.append({
            "type": decision_type,
            "data": data,
            "timestamp": time.time()
        })
    
    @property
    def plan_id(self) -> str:
        """Get content-addressed plan ID."""
        content = (f"{self.name}:{self.global_tolerance}:{self.master_rng_seed}:"
                  f"{len(self.chart_selections)}:{len(self.ladders)}")
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the solve plan."""
        errors = []
        
        # Check for chart selections
        if not self.chart_selections:
            errors.append("No chart selections")
        
        # Check for solver ladders
        if not self.ladders:
            errors.append("No solver ladders")
        
        # Check each ladder has solvers
        for name, ladder in self.ladders.items():
            if not ladder.solvers:
                errors.append(f"Ladder '{name}' has no solvers")
        
        # Check tolerances
        if self.global_tolerance <= 0:
            errors.append("Global tolerance must be positive")
        
        # Check RNG seed
        if self.master_rng_seed is None:
            errors.append("Master RNG seed not set (required for replay)")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "chart_selections": [c.to_dict() for c in self.chart_selections],
            "ladders": {k: v.to_dict() for k, v in self.ladders.items()},
            "global_tolerance": self.global_tolerance,
            "global_max_iterations": self.global_max_iterations,
            "global_timeout_seconds": self.global_timeout_seconds,
            "tie_break_rule": self.tie_break_rule.value,
            "master_rng_seed": self.master_rng_seed,
            "platform": self.platform,
            "float_model": self.float_model,
            "phase_budgets": {k.value: v for k, v in self.phase_budgets.items()},
            "decisions": self.decisions,
            "created_at": self.created_at
        }


# =============================================================================
# SOLVE PLAN BUILDER
# =============================================================================

class SolvePlanBuilder:
    """Builder for constructing solve plans."""
    
    def __init__(self, name: str):
        self.plan = SolvePlan(name=name)
    
    def with_chart(self, chart_id: str, chart_type: str,
                  lower: float, upper: float,
                  rationale: str = "") -> SolvePlanBuilder:
        """Add a chart selection."""
        selection = ChartSelection(
            chart_id=chart_id,
            chart_type=chart_type,
            corridor_lower=lower,
            corridor_upper=upper,
            rationale=rationale
        )
        self.plan.add_chart_selection(selection)
        return self
    
    def with_root_finder_ladder(self, name: str = "roots") -> SolvePlanBuilder:
        """Add a standard root-finder ladder."""
        self.plan.add_ladder(name, SolverLadder.root_finder_ladder())
        return self
    
    def with_fixed_point_ladder(self, name: str = "fixed_points") -> SolvePlanBuilder:
        """Add a standard fixed-point ladder."""
        self.plan.add_ladder(name, SolverLadder.fixed_point_ladder())
        return self
    
    def with_custom_ladder(self, name: str, 
                          ladder: SolverLadder) -> SolvePlanBuilder:
        """Add a custom solver ladder."""
        self.plan.add_ladder(name, ladder)
        return self
    
    def with_tolerance(self, tolerance: float) -> SolvePlanBuilder:
        """Set global tolerance."""
        self.plan.global_tolerance = tolerance
        return self
    
    def with_max_iterations(self, max_iter: int) -> SolvePlanBuilder:
        """Set global max iterations."""
        self.plan.global_max_iterations = max_iter
        return self
    
    def with_timeout(self, seconds: float) -> SolvePlanBuilder:
        """Set global timeout."""
        self.plan.global_timeout_seconds = seconds
        return self
    
    def with_tie_break(self, rule: TieBreakRule) -> SolvePlanBuilder:
        """Set tie-break rule."""
        self.plan.tie_break_rule = rule
        return self
    
    def with_rng_seed(self, seed: int) -> SolvePlanBuilder:
        """Set master RNG seed."""
        self.plan.master_rng_seed = seed
        return self
    
    def with_platform(self, platform: str, 
                     float_model: str = "ieee754") -> SolvePlanBuilder:
        """Set platform contract."""
        self.plan.platform = platform
        self.plan.float_model = float_model
        return self
    
    def with_phase_budget(self, phase: PlanPhase, 
                         budget: float) -> SolvePlanBuilder:
        """Set phase time budget."""
        self.plan.set_phase_budget(phase, budget)
        return self
    
    def build(self) -> SolvePlan:
        """Build and return the solve plan."""
        valid, errors = self.plan.validate()
        if not valid:
            raise ValueError(f"Invalid solve plan: {errors}")
        return self.plan


# =============================================================================
# SOLVER RESULT
# =============================================================================

@dataclass
class SolverResult:
    """Result from running a solver."""
    
    success: bool
    value: Optional[float] = None
    
    # Convergence info
    iterations: int = 0
    function_evaluations: int = 0
    elapsed_seconds: float = 0.0
    
    # Residual
    residual: float = float('inf')
    
    # Which solver succeeded
    solver_type: Optional[SolverType] = None
    solver_tier: Optional[SolverTier] = None
    
    # Error info if failed
    error_message: str = ""
    
    # Enclosure (for certified solvers)
    enclosure_lower: Optional[float] = None
    enclosure_upper: Optional[float] = None
    
    @property
    def has_enclosure(self) -> bool:
        return self.enclosure_lower is not None and self.enclosure_upper is not None
    
    @property
    def enclosure_width(self) -> float:
        if self.has_enclosure:
            return self.enclosure_upper - self.enclosure_lower
        return float('inf')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "value": self.value,
            "iterations": self.iterations,
            "function_evaluations": self.function_evaluations,
            "elapsed_seconds": self.elapsed_seconds,
            "residual": self.residual,
            "solver_type": self.solver_type.value if self.solver_type else None,
            "solver_tier": self.solver_tier.value if self.solver_tier else None,
            "error_message": self.error_message,
            "enclosure": [self.enclosure_lower, self.enclosure_upper] 
                        if self.has_enclosure else None
        }


# =============================================================================
# PLAN EXECUTOR (Interface)
# =============================================================================

class PlanExecutor(ABC):
    """
    Abstract interface for plan execution.
    
    Concrete implementations handle actual solving.
    """
    
    @abstractmethod
    def execute(self, plan: SolvePlan, 
               constraint: Any) -> SolverResult:
        """Execute a solve plan on a constraint."""
        pass
    
    @abstractmethod
    def replay(self, plan: SolvePlan,
              constraint: Any) -> SolverResult:
        """Replay a solve plan (deterministic)."""
        pass


# =============================================================================
# VALIDATION
# =============================================================================

def validate_solve_plan() -> bool:
    """Validate solve plan module."""
    
    # Test solver config
    config = SolverConfig(
        solver_type=SolverType.BISECTION,
        tier=SolverTier.CERTIFIED,
        max_iterations=100,
        abs_tolerance=1e-12
    )
    assert config.tier == SolverTier.CERTIFIED
    assert config.abs_tolerance == 1e-12
    
    # Test solver ladder
    ladder = SolverLadder.root_finder_ladder()
    assert len(ladder.solvers) == 3
    assert ladder.solvers[0].tier == SolverTier.FAST
    assert ladder.solvers[-1].tier == SolverTier.CERTIFIED
    
    # Test solve plan builder
    plan = (SolvePlanBuilder("test_plan")
            .with_chart("log_chart", "logarithmic", 0.1, 100.0,
                       "Log chart simplifies exponential constraints")
            .with_root_finder_ladder()
            .with_tolerance(1e-10)
            .with_rng_seed(12345)
            .with_platform("linux_x86_64")
            .build())
    
    assert plan.name == "test_plan"
    assert len(plan.chart_selections) == 1
    assert "roots" in plan.ladders
    assert plan.master_rng_seed == 12345
    
    valid, errors = plan.validate()
    assert valid, f"Plan should be valid: {errors}"
    
    # Test serialization
    plan_dict = plan.to_dict()
    assert "plan_id" in plan_dict
    assert plan_dict["name"] == "test_plan"
    
    # Test solver result
    result = SolverResult(
        success=True,
        value=1.4142,
        iterations=23,
        residual=1e-12,
        solver_type=SolverType.BRENT,
        solver_tier=SolverTier.ROBUST,
        enclosure_lower=1.4141,
        enclosure_upper=1.4143
    )
    assert result.has_enclosure
    assert result.enclosure_width < 0.001
    
    return True


if __name__ == "__main__":
    print("Validating Solve Plan Module...")
    assert validate_solve_plan()
    print("✓ Solve Plan Module validated")
    
    # Demo
    print("\n--- SolvePlan Demo ---")
    
    # Build a complete solve plan
    plan = (SolvePlanBuilder("sqrt2_finder")
            .with_chart("identity", "identity", 1.0, 2.0,
                       "Identity chart sufficient for polynomial")
            .with_chart("log_chart", "logarithmic", 0.1, 10.0,
                       "Log chart for exponential verification")
            .with_root_finder_ladder("primary")
            .with_fixed_point_ladder("iteration")
            .with_tolerance(1e-14)
            .with_max_iterations(10000)
            .with_timeout(60.0)
            .with_tie_break(TieBreakRule.MINIMUM)
            .with_rng_seed(42)
            .with_platform("linux_x86_64", "ieee754")
            .with_phase_budget(PlanPhase.SOLVE, 30.0)
            .with_phase_budget(PlanPhase.CERTIFY, 10.0)
            .build())
    
    print(f"\nPlan ID: {plan.plan_id}")
    print(f"Name: {plan.name}")
    
    print(f"\nChart Selections ({len(plan.chart_selections)}):")
    for cs in plan.chart_selections:
        print(f"  {cs.chart_id}: [{cs.corridor_lower}, {cs.corridor_upper}]")
        print(f"    Rationale: {cs.rationale}")
    
    print(f"\nSolver Ladders ({len(plan.ladders)}):")
    for name, ladder in plan.ladders.items():
        print(f"  {name}: {len(ladder.solvers)} solvers")
        for solver in ladder.solvers:
            print(f"    - {solver.solver_type.value} ({solver.tier.value})")
    
    print(f"\nGlobal Settings:")
    print(f"  Tolerance: {plan.global_tolerance}")
    print(f"  Max Iterations: {plan.global_max_iterations}")
    print(f"  Timeout: {plan.global_timeout_seconds}s")
    print(f"  Tie-break: {plan.tie_break_rule.value}")
    print(f"  RNG Seed: {plan.master_rng_seed}")
    
    print(f"\nEnvironment Contract:")
    print(f"  Platform: {plan.platform}")
    print(f"  Float Model: {plan.float_model}")
    
    print(f"\nDecision Log ({len(plan.decisions)} decisions recorded)")
