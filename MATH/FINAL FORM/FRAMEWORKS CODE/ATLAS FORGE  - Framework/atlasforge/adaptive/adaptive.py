"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 ATLAS FORGE - Adaptive Hybridization Framework                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Discovery-based approach to algorithm design.

Key Insight: There Is No Single Best Strategy
- Sometimes 4-pole equal (25% each) BEATS everything
- Sometimes 3-pole combinations win
- Sometimes 2-pole is optimal
- THE ONLY WAY TO KNOW IS TO TEST

The Master Algorithm:
1. Analyze problem signature
2. Predict promising strategies
3. Test multiple configurations
4. Optimize weights (if budget allows)
5. Return best solution with proof
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math
import time

import numpy as np
from numpy.typing import NDArray

from atlasforge.diagnosis.diagnosis import (
    ProblemSignature, DiagnosticMetrics, ProblemDiagnoser,
    STRATEGY_CONFIGS, predict_best_strategy
)


class Budget(Enum):
    """Computational budget levels."""
    TINY = "tiny"         # < 100 evaluations
    SMALL = "small"       # < 1000 evaluations
    MEDIUM = "medium"     # < 10000 evaluations
    LARGE = "large"       # < 100000 evaluations
    UNLIMITED = "unlimited"


@dataclass
class HybridWeights:
    """Pole weights for hybrid algorithm."""
    psi: float = 0.25      # Ψ - Spectral/Recursive
    omega: float = 0.25    # Ω - Gradient/Continuous
    sigma: float = 0.25    # Σ - Stochastic
    d: float = 0.25        # D - Discrete
    
    def __post_init__(self):
        """Normalize weights."""
        total = self.psi + self.omega + self.sigma + self.d
        if total > 0:
            self.psi /= total
            self.omega /= total
            self.sigma /= total
            self.d /= total
    
    def to_dict(self) -> Dict[str, float]:
        return {'Ψ': self.psi, 'Ω': self.omega, 'Σ': self.sigma, 'D': self.d}
    
    @classmethod
    def from_dict(cls, d: Dict[str, float]) -> 'HybridWeights':
        return cls(
            psi=d.get('Ψ', 0.25),
            omega=d.get('Ω', 0.25),
            sigma=d.get('Σ', 0.25),
            d=d.get('D', 0.25),
        )
    
    @classmethod
    def equal(cls) -> 'HybridWeights':
        return cls(0.25, 0.25, 0.25, 0.25)
    
    @classmethod
    def spectral_dominant(cls) -> 'HybridWeights':
        return cls(psi=0.60, omega=0.0, sigma=0.0, d=0.40)
    
    @classmethod
    def gradient_dominant(cls) -> 'HybridWeights':
        return cls(psi=0.0, omega=0.80, sigma=0.0, d=0.20)
    
    @classmethod
    def stochastic_dominant(cls) -> 'HybridWeights':
        return cls(psi=0.0, omega=0.10, sigma=0.50, d=0.40)


@dataclass
class HybridResult:
    """Result from hybrid optimization."""
    solution: NDArray[np.float64]
    objective_value: float
    strategy: str
    weights: HybridWeights
    iterations: int
    evaluations: int
    time_seconds: float
    convergence_history: List[float] = field(default_factory=list)
    
    def __repr__(self):
        return (f"HybridResult(value={self.objective_value:.6f}, "
                f"strategy='{self.strategy}', iters={self.iterations})")


@dataclass
class StrategyTestResult:
    """Result of testing a single strategy."""
    strategy: str
    weights: Dict[str, float]
    mean_objective: float
    std_objective: float
    best_objective: float
    n_trials: int
    solutions: List[NDArray] = field(default_factory=list)


class HybridOperator:
    """
    Base operator that combines multiple pole operations.
    """
    
    def __init__(
        self,
        objective: Callable[[NDArray], float],
        dimension: int,
        weights: HybridWeights,
        domain: Tuple[float, float] = (-10.0, 10.0),
        Q: Optional[NDArray] = None,
    ):
        self.objective = objective
        self.dimension = dimension
        self.weights = weights
        self.domain = domain
        self.Q = Q
        self.lo, self.hi = domain
        
        # Precompute spectral initialization if matrix available
        self._spectral_init = None
        if Q is not None and weights.psi > 0:
            self._compute_spectral_init()
    
    def _compute_spectral_init(self):
        """Compute spectral initialization from matrix."""
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(self.Q)
            # Use leading eigenvector
            self._spectral_init = eigenvectors[:, -1]
            # Scale to domain
            self._spectral_init = self._spectral_init / (np.linalg.norm(self._spectral_init) + 1e-10)
            self._spectral_init = self._spectral_init * (self.hi - self.lo) / 2
        except Exception:
            self._spectral_init = None
    
    def initialize(self, rng: np.random.Generator) -> NDArray:
        """Initialize solution based on weights."""
        x = np.zeros(self.dimension)
        
        if self.weights.psi > 0 and self._spectral_init is not None:
            # Spectral initialization
            x += self.weights.psi * self._spectral_init
        
        # Random component
        random_weight = self.weights.sigma + (1.0 - self.weights.psi if self._spectral_init is None else 0)
        if random_weight > 0:
            x += random_weight * rng.uniform(self.lo, self.hi, self.dimension)
        
        return np.clip(x, self.lo, self.hi)
    
    def step(
        self,
        x: NDArray,
        f_x: float,
        rng: np.random.Generator,
        temperature: float = 1.0,
    ) -> Tuple[NDArray, float]:
        """Take one hybrid step."""
        x_new = x.copy()
        
        # Gradient component (Ω)
        if self.weights.omega > 0:
            grad = self._numerical_gradient(x, f_x)
            step_size = 0.1 * (self.hi - self.lo) * self.weights.omega
            x_new -= step_size * grad
        
        # Stochastic component (Σ)
        if self.weights.sigma > 0:
            noise = rng.standard_normal(self.dimension)
            x_new += self.weights.sigma * temperature * (self.hi - self.lo) * 0.1 * noise
        
        # Discrete local search component (D)
        if self.weights.d > 0:
            # Try small perturbations
            for _ in range(int(5 * self.weights.d)):
                idx = rng.integers(self.dimension)
                delta = rng.choice([-1, 1]) * (self.hi - self.lo) * 0.01
                x_test = x_new.copy()
                x_test[idx] += delta
                x_test = np.clip(x_test, self.lo, self.hi)
                if self.objective(x_test) < self.objective(x_new):
                    x_new = x_test
        
        x_new = np.clip(x_new, self.lo, self.hi)
        return x_new, self.objective(x_new)
    
    def _numerical_gradient(
        self,
        x: NDArray,
        f_x: Optional[float] = None,
        eps: float = 1e-6,
    ) -> NDArray:
        """Compute numerical gradient."""
        if f_x is None:
            f_x = self.objective(x)
        
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus = x.copy()
            x_plus[i] += eps
            grad[i] = (self.objective(x_plus) - f_x) / eps
        
        return grad


class AdaptiveHybridSolver:
    """
    Adaptive hybrid solver that automatically selects the best strategy.
    
    The master algorithm:
    1. Diagnose problem
    2. Predict promising strategies  
    3. Test multiple configurations
    4. Optimize weights
    5. Return best solution
    """
    
    def __init__(
        self,
        budget: Budget = Budget.MEDIUM,
        n_test_trials: int = 5,
        seed: Optional[int] = None,
    ):
        self.budget = budget
        self.n_test_trials = n_test_trials
        self.rng = np.random.default_rng(seed)
        self.diagnoser = ProblemDiagnoser(seed=seed)
    
    def solve(
        self,
        objective: Callable[[NDArray], float],
        dimension: int,
        Q: Optional[NDArray] = None,
        domain: Tuple[float, float] = (-10.0, 10.0),
        max_iterations: int = 1000,
    ) -> HybridResult:
        """
        Solve optimization problem with adaptive strategy selection.
        """
        start_time = time.time()
        
        # Step 1: Diagnose problem
        metrics = self.diagnoser.diagnose(objective, dimension, Q, domain)
        signature = ProblemSignature.from_metrics(metrics)
        
        # Step 2: Predict promising strategies
        strategies = self._predict_strategies(signature)
        
        # Step 3: Test strategies (if budget allows)
        if self.budget in [Budget.MEDIUM, Budget.LARGE, Budget.UNLIMITED]:
            best_strategy, test_results = self._test_strategies(
                objective, dimension, Q, domain, strategies
            )
        else:
            best_strategy = strategies[0]
            test_results = {}
        
        # Step 4: Run best strategy
        weights = HybridWeights.from_dict(STRATEGY_CONFIGS[best_strategy])
        
        result = self._run_optimization(
            objective, dimension, Q, domain, weights,
            max_iterations=max_iterations,
        )
        
        result.strategy = best_strategy
        result.time_seconds = time.time() - start_time
        
        return result
    
    def _predict_strategies(self, sig: ProblemSignature) -> List[str]:
        """Predict promising strategies based on signature."""
        strategies = []
        
        # Primary prediction
        primary = predict_best_strategy(sig)
        strategies.append(primary)
        
        # Add complementary strategies
        if sig.spectral_gap > 0.1:
            if 'Ψ+D' not in strategies:
                strategies.append('Ψ+D')
            if 'Ψ+Σ+D' not in strategies:
                strategies.append('Ψ+Σ+D')
        
        if sig.gradient_reliability > 0.6:
            if 'Ω+D' not in strategies:
                strategies.append('Ω+D')
        
        if sig.n_local_optima > 5:
            if 'Σ+D' not in strategies:
                strategies.append('Σ+D')
        
        # Always include 4-pole-equal as baseline
        if '4-pole-equal' not in strategies:
            strategies.append('4-pole-equal')
        
        # Add D-only as baseline
        strategies.append('D-only')
        
        return strategies[:5]  # Limit to 5 strategies
    
    def _test_strategies(
        self,
        objective: Callable,
        dimension: int,
        Q: Optional[NDArray],
        domain: Tuple[float, float],
        strategies: List[str],
    ) -> Tuple[str, Dict[str, StrategyTestResult]]:
        """Test multiple strategies and return best."""
        results = {}
        
        for strategy in strategies:
            weights = HybridWeights.from_dict(STRATEGY_CONFIGS[strategy])
            objectives = []
            solutions = []
            
            for trial in range(self.n_test_trials):
                result = self._run_optimization(
                    objective, dimension, Q, domain, weights,
                    max_iterations=100,  # Quick test
                    seed=trial,
                )
                objectives.append(result.objective_value)
                solutions.append(result.solution)
            
            results[strategy] = StrategyTestResult(
                strategy=strategy,
                weights=STRATEGY_CONFIGS[strategy],
                mean_objective=float(np.mean(objectives)),
                std_objective=float(np.std(objectives)),
                best_objective=float(np.min(objectives)),
                n_trials=self.n_test_trials,
                solutions=solutions,
            )
        
        # Select best strategy by mean objective
        best = min(results.keys(), key=lambda s: results[s].mean_objective)
        return best, results
    
    def _run_optimization(
        self,
        objective: Callable,
        dimension: int,
        Q: Optional[NDArray],
        domain: Tuple[float, float],
        weights: HybridWeights,
        max_iterations: int = 1000,
        seed: Optional[int] = None,
    ) -> HybridResult:
        """Run optimization with given weights."""
        rng = np.random.default_rng(seed)
        
        operator = HybridOperator(
            objective=objective,
            dimension=dimension,
            weights=weights,
            domain=domain,
            Q=Q,
        )
        
        # Initialize
        x = operator.initialize(rng)
        f_x = objective(x)
        
        best_x = x.copy()
        best_f = f_x
        
        history = [f_x]
        evaluations = 1
        
        # Annealing schedule
        T0 = 1.0
        T_min = 0.01
        
        for iteration in range(max_iterations):
            # Temperature
            T = max(T_min, T0 * (1 - iteration / max_iterations))
            
            # Take step
            x_new, f_new = operator.step(x, f_x, rng, temperature=T)
            evaluations += dimension + 5  # Approx evaluations per step
            
            # Accept?
            if f_new < f_x:
                x, f_x = x_new, f_new
                if f_x < best_f:
                    best_x, best_f = x.copy(), f_x
            elif rng.random() < np.exp(-(f_new - f_x) / (T + 1e-10)):
                x, f_x = x_new, f_new
            
            history.append(best_f)
            
            # Convergence check
            if iteration > 50 and abs(history[-1] - history[-50]) < 1e-10:
                break
        
        return HybridResult(
            solution=best_x,
            objective_value=best_f,
            strategy="",  # Set later
            weights=weights,
            iterations=iteration + 1,
            evaluations=evaluations,
            time_seconds=0.0,  # Set later
            convergence_history=history,
        )


class StrategyTournament:
    """
    Tournament for comparing multiple strategies on a problem.
    """
    
    def __init__(
        self,
        n_trials: int = 10,
        max_iterations: int = 500,
        seed: Optional[int] = None,
    ):
        self.n_trials = n_trials
        self.max_iterations = max_iterations
        self.rng = np.random.default_rng(seed)
    
    def run(
        self,
        objective: Callable[[NDArray], float],
        dimension: int,
        Q: Optional[NDArray] = None,
        domain: Tuple[float, float] = (-10.0, 10.0),
        strategies: Optional[List[str]] = None,
    ) -> Dict[str, StrategyTestResult]:
        """Run tournament comparing strategies."""
        if strategies is None:
            strategies = list(STRATEGY_CONFIGS.keys())
        
        results = {}
        
        for strategy in strategies:
            weights = HybridWeights.from_dict(STRATEGY_CONFIGS[strategy])
            objectives = []
            solutions = []
            
            for trial in range(self.n_trials):
                solver = AdaptiveHybridSolver(
                    budget=Budget.TINY,
                    seed=trial,
                )
                result = solver._run_optimization(
                    objective, dimension, Q, domain, weights,
                    max_iterations=self.max_iterations,
                    seed=trial,
                )
                objectives.append(result.objective_value)
                solutions.append(result.solution)
            
            results[strategy] = StrategyTestResult(
                strategy=strategy,
                weights=STRATEGY_CONFIGS[strategy],
                mean_objective=float(np.mean(objectives)),
                std_objective=float(np.std(objectives)),
                best_objective=float(np.min(objectives)),
                n_trials=self.n_trials,
                solutions=solutions,
            )
        
        return results
    
    def report(self, results: Dict[str, StrategyTestResult]) -> str:
        """Generate tournament report."""
        # Sort by mean objective
        sorted_strategies = sorted(
            results.keys(),
            key=lambda s: results[s].mean_objective
        )
        
        lines = [
            "═" * 70,
            "STRATEGY TOURNAMENT RESULTS",
            "═" * 70,
            f"{'Strategy':<20} {'Mean':>12} {'Std':>10} {'Best':>12} {'Rank':>6}",
            "─" * 70,
        ]
        
        baseline = results.get('D-only', results[sorted_strategies[-1]])
        
        for rank, strategy in enumerate(sorted_strategies, 1):
            r = results[strategy]
            improvement = (baseline.mean_objective - r.mean_objective) / abs(baseline.mean_objective) * 100
            lines.append(
                f"{strategy:<20} {r.mean_objective:>12.4f} {r.std_objective:>10.4f} "
                f"{r.best_objective:>12.4f} {rank:>6}"
            )
        
        lines.append("═" * 70)
        winner = sorted_strategies[0]
        lines.append(f"WINNER: {winner}")
        lines.append("═" * 70)
        
        return "\n".join(lines)


# Convenience function
def adaptive_solve(
    objective: Callable[[NDArray], float],
    dimension: int,
    Q: Optional[NDArray] = None,
    domain: Tuple[float, float] = (-10.0, 10.0),
    budget: Budget = Budget.MEDIUM,
    max_iterations: int = 1000,
    seed: Optional[int] = None,
) -> HybridResult:
    """
    Convenience function for adaptive hybrid optimization.
    
    Example:
        result = adaptive_solve(
            objective=lambda x: np.sum(x**2),
            dimension=10,
            budget=Budget.MEDIUM,
        )
        print(f"Solution: {result.solution}")
        print(f"Value: {result.objective_value}")
    """
    solver = AdaptiveHybridSolver(budget=budget, seed=seed)
    return solver.solve(objective, dimension, Q, domain, max_iterations)
