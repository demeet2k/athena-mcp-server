"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Problem Diagnosis System                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Diagnose problem structure to determine optimal pole selection.

The Four Diagnostic Dimensions:
1. STRUCTURE - Does the problem have exploitable mathematical structure?
2. LANDSCAPE - Is the objective smooth, rugged, or mixed?
3. CONSTRAINTS - Are there hard constraints that must be satisfied?
4. SCALE - What is the problem size and computational budget?

Problem Classes:
- CLASS A: SPECTRAL-DOMINANT (Ψ + D) - Matrix problems with large spectral gap
- CLASS B: GRADIENT-DOMINANT (Ω + D) - Convex, smooth landscapes
- CLASS C: STOCHASTIC-DOMINANT (Σ + D) - Rugged landscapes, many local optima
- CLASS D: CONSTRAINT-DOMINANT (D + Ω) - Hard feasibility constraints
- CLASS E: HIERARCHICAL (Ψ + all) - Multi-scale structure
- CLASS F: MIXED (4-pole equal) - No clear dominant structure
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum, auto
import math
import random

import numpy as np
from numpy.typing import NDArray


class ProblemClass(Enum):
    """Problem classification for pole selection."""
    SPECTRAL_DOMINANT = "spectral"      # Ψ + D
    GRADIENT_DOMINANT = "gradient"       # Ω + D
    STOCHASTIC_DOMINANT = "stochastic"   # Σ + D
    CONSTRAINT_DOMINANT = "constraint"   # D + Ω
    HIERARCHICAL = "hierarchical"        # Ψ + all
    MIXED = "mixed"                      # 4-pole equal
    UNKNOWN = "unknown"


class LandscapeType(Enum):
    """Landscape characterization."""
    SMOOTH = "smooth"           # Few local optima, gradients reliable
    RUGGED = "rugged"           # Many local optima, traps everywhere
    MIXED = "mixed"             # Smooth in some regions, rugged in others
    FLAT = "flat"               # Many equivalent solutions


@dataclass
class SpectralAnalysis:
    """Analysis of matrix spectral properties."""
    eigenvalues: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    spectral_gap: float = 0.0           # (λ₂ - λ₁) / (λₙ - λ₁)
    condition_number: float = float('inf')
    effective_rank: int = 0
    decay_rate: float = 0.0
    
    @classmethod
    def from_matrix(cls, Q: NDArray) -> 'SpectralAnalysis':
        """Compute spectral analysis from matrix."""
        try:
            eigenvalues = np.linalg.eigvalsh(Q)
            eigenvalues = np.sort(np.abs(eigenvalues))
            
            spectral_gap = 0.0
            if len(eigenvalues) > 1 and eigenvalues[-1] > eigenvalues[0]:
                spectral_gap = (eigenvalues[1] - eigenvalues[0]) / (
                    eigenvalues[-1] - eigenvalues[0] + 1e-10
                )
            
            condition_number = float('inf')
            if eigenvalues[0] > 1e-10:
                condition_number = eigenvalues[-1] / eigenvalues[0]
            
            # Effective rank (number of significant eigenvalues)
            threshold = eigenvalues[-1] * 1e-6
            effective_rank = np.sum(eigenvalues > threshold)
            
            # Decay rate
            decay_rate = 0.0
            if len(eigenvalues) > 2:
                ratios = eigenvalues[1:] / (eigenvalues[:-1] + 1e-10)
                decay_rate = np.mean(ratios)
            
            return cls(
                eigenvalues=eigenvalues,
                spectral_gap=spectral_gap,
                condition_number=condition_number,
                effective_rank=int(effective_rank),
                decay_rate=decay_rate,
            )
        except Exception:
            return cls()
    
    def psi_relevance(self) -> str:
        """Determine Ψ pole relevance."""
        if self.spectral_gap > 0.2:
            return "Ψ DOMINATES - Large spectral gap"
        elif self.spectral_gap > 0.1:
            return "Ψ useful - Moderate spectral gap"
        elif self.spectral_gap > 0.05:
            return "Ψ marginal - Small spectral gap"
        else:
            return "Ψ not useful - Negligible spectral gap"


@dataclass
class LandscapeAnalysis:
    """Analysis of objective landscape."""
    n_local_optima: int = 0
    optima_values: List[float] = field(default_factory=list)
    variance: float = 0.0
    landscape_type: LandscapeType = LandscapeType.MIXED
    basin_sizes: List[float] = field(default_factory=list)
    
    def sigma_relevance(self) -> str:
        """Determine Σ pole relevance."""
        if self.n_local_optima > 10:
            return "Σ DOMINATES - Many local optima (rugged)"
        elif self.n_local_optima > 3:
            return "Σ useful - Some local optima (mixed)"
        else:
            return "Σ not needed - Few local optima (smooth)"


@dataclass 
class GradientAnalysis:
    """Analysis of gradient reliability."""
    reliability: float = 0.0            # Cosine consistency
    lipschitz_estimate: float = float('inf')
    is_convex: bool = False
    smoothness: float = 0.0
    
    def omega_relevance(self) -> str:
        """Determine Ω pole relevance."""
        if self.is_convex and self.reliability > 0.8:
            return "Ω DOMINATES - Convex with reliable gradients"
        elif self.reliability > 0.7:
            return "Ω useful - Gradients reliable"
        elif self.reliability > 0.4:
            return "Ω marginal - Gradients somewhat reliable"
        else:
            return "Ω unreliable - Use Σ instead"


@dataclass
class ConstraintAnalysis:
    """Analysis of constraint structure."""
    has_hard_constraints: bool = False
    feasibility_ratio: float = 1.0
    n_constraints: int = 0
    tightness: float = 0.0
    
    def d_relevance(self) -> str:
        """Determine D pole relevance."""
        if self.has_hard_constraints and self.feasibility_ratio < 0.1:
            return "D DOMINATES - Hard constraints, tight feasibility"
        elif self.has_hard_constraints:
            return "D essential - Must maintain feasibility"
        else:
            return "D baseline - Standard local search"


@dataclass
class DiagnosticMetrics:
    """Comprehensive diagnostic metrics for a problem."""
    
    # Component analyses
    spectral: SpectralAnalysis = field(default_factory=SpectralAnalysis)
    landscape: LandscapeAnalysis = field(default_factory=LandscapeAnalysis)
    gradient: GradientAnalysis = field(default_factory=GradientAnalysis)
    constraint: ConstraintAnalysis = field(default_factory=ConstraintAnalysis)
    
    # Problem metadata
    dimension: int = 1
    has_matrix: bool = False
    computational_budget: str = "medium"
    
    def classify(self) -> ProblemClass:
        """Classify problem based on metrics."""
        scores = self._compute_pole_scores()
        
        max_pole = max(scores, key=scores.get)
        max_score = scores[max_pole]
        
        other_scores = [s for p, s in scores.items() if p != max_pole]
        second_max = max(other_scores) if other_scores else 0
        
        # Check for clear dominance
        if max_score > second_max * 1.5:
            if max_pole == 'Ψ':
                return ProblemClass.SPECTRAL_DOMINANT
            elif max_pole == 'Ω':
                return ProblemClass.GRADIENT_DOMINANT
            elif max_pole == 'Σ':
                return ProblemClass.STOCHASTIC_DOMINANT
            elif max_pole == 'D':
                return ProblemClass.CONSTRAINT_DOMINANT
        
        # Check for hierarchical
        if (self.has_matrix and 
            self.spectral.spectral_gap > 0.1 and 
            self.landscape.n_local_optima > 5):
            return ProblemClass.HIERARCHICAL
        
        return ProblemClass.MIXED
    
    def _compute_pole_scores(self) -> Dict[str, float]:
        """Compute relevance scores for each pole."""
        scores = {'Ψ': 0.0, 'Ω': 0.0, 'Σ': 0.0, 'D': 1.0}
        
        # Ψ scoring
        if self.has_matrix:
            scores['Ψ'] += 3.0
            if self.spectral.spectral_gap > 0.2:
                scores['Ψ'] += 2.0
            elif self.spectral.spectral_gap > 0.1:
                scores['Ψ'] += 1.0
        
        # Ω scoring
        if self.gradient.is_convex:
            scores['Ω'] += 3.0
        scores['Ω'] += 2.0 * self.gradient.reliability
        if self.spectral.condition_number < 100:
            scores['Ω'] += 1.0
        
        # Σ scoring
        if self.landscape.landscape_type == LandscapeType.RUGGED:
            scores['Σ'] += 3.0
        elif self.landscape.landscape_type == LandscapeType.MIXED:
            scores['Σ'] += 1.0
        if self.landscape.n_local_optima > 10:
            scores['Σ'] += 2.0
        elif self.landscape.n_local_optima > 3:
            scores['Σ'] += 1.0
        
        # D scoring
        if self.constraint.has_hard_constraints:
            scores['D'] += 2.0
        if self.constraint.feasibility_ratio < 0.1:
            scores['D'] += 1.0
        
        return scores
    
    def recommended_weights(self) -> Dict[str, float]:
        """Get recommended pole weights."""
        problem_class = self.classify()
        
        weight_map = {
            ProblemClass.SPECTRAL_DOMINANT: {'Ψ': 0.60, 'Ω': 0.00, 'Σ': 0.00, 'D': 0.40},
            ProblemClass.GRADIENT_DOMINANT: {'Ψ': 0.00, 'Ω': 0.80, 'Σ': 0.00, 'D': 0.20},
            ProblemClass.STOCHASTIC_DOMINANT: {'Ψ': 0.00, 'Ω': 0.10, 'Σ': 0.50, 'D': 0.40},
            ProblemClass.CONSTRAINT_DOMINANT: {'Ψ': 0.00, 'Ω': 0.20, 'Σ': 0.00, 'D': 0.80},
            ProblemClass.HIERARCHICAL: {'Ψ': 0.40, 'Ω': 0.20, 'Σ': 0.10, 'D': 0.30},
            ProblemClass.MIXED: {'Ψ': 0.25, 'Ω': 0.25, 'Σ': 0.25, 'D': 0.25},
            ProblemClass.UNKNOWN: {'Ψ': 0.25, 'Ω': 0.25, 'Σ': 0.25, 'D': 0.25},
        }
        
        return weight_map.get(problem_class, weight_map[ProblemClass.MIXED])


@dataclass
class ProblemSignature:
    """Compact problem signature for strategy selection."""
    spectral_gap: float = 0.0
    n_local_optima: int = 0
    gradient_reliability: float = 0.0
    has_constraints: bool = False
    dimension: int = 1
    
    def to_vector(self) -> NDArray[np.float64]:
        """Convert to feature vector."""
        return np.array([
            self.spectral_gap,
            min(self.n_local_optima / 20.0, 1.0),
            self.gradient_reliability,
            1.0 if self.has_constraints else 0.0,
            min(self.dimension / 1000.0, 1.0),
        ])
    
    @classmethod
    def from_metrics(cls, metrics: DiagnosticMetrics) -> 'ProblemSignature':
        """Create from full metrics."""
        return cls(
            spectral_gap=metrics.spectral.spectral_gap,
            n_local_optima=metrics.landscape.n_local_optima,
            gradient_reliability=metrics.gradient.reliability,
            has_constraints=metrics.constraint.has_hard_constraints,
            dimension=metrics.dimension,
        )


class ProblemDiagnoser:
    """
    Comprehensive problem diagnosis system.
    
    Usage:
        diagnoser = ProblemDiagnoser()
        metrics = diagnoser.diagnose(objective, dimension, Q=matrix)
        report = diagnoser.report(metrics)
    """
    
    def __init__(
        self,
        n_landscape_samples: int = 100,
        n_gradient_samples: int = 20,
        local_search_iters: int = 50,
        seed: Optional[int] = None,
    ):
        self.n_landscape_samples = n_landscape_samples
        self.n_gradient_samples = n_gradient_samples
        self.local_search_iters = local_search_iters
        self.rng = np.random.default_rng(seed)
    
    def diagnose(
        self,
        objective: Callable[[NDArray], float],
        dimension: int,
        Q: Optional[NDArray] = None,
        domain: Optional[Tuple[float, float]] = None,
        has_constraints: bool = False,
    ) -> DiagnosticMetrics:
        """Perform comprehensive problem diagnosis."""
        metrics = DiagnosticMetrics(
            dimension=dimension,
            has_matrix=(Q is not None),
        )
        
        if domain is None:
            domain = (-10.0, 10.0)
        
        # Spectral analysis
        if Q is not None:
            metrics.spectral = SpectralAnalysis.from_matrix(Q)
        
        # Landscape analysis
        metrics.landscape = self._analyze_landscape(objective, dimension, domain)
        
        # Gradient analysis
        metrics.gradient = self._analyze_gradient(objective, dimension, domain)
        
        # Constraint analysis
        metrics.constraint = ConstraintAnalysis(has_hard_constraints=has_constraints)
        
        return metrics
    
    def _analyze_landscape(
        self,
        objective: Callable,
        dimension: int,
        domain: Tuple[float, float],
    ) -> LandscapeAnalysis:
        """Analyze objective landscape."""
        lo, hi = domain
        optima = []
        
        for _ in range(self.n_landscape_samples):
            x = self.rng.uniform(lo, hi, dimension)
            best_val = objective(x)
            
            # Simple local search
            for _ in range(self.local_search_iters):
                grad = self._numerical_gradient(objective, x, best_val)
                step = 0.1 * (hi - lo)
                x_new = np.clip(x - step * grad, lo, hi)
                new_val = objective(x_new)
                if new_val < best_val:
                    x, best_val = x_new, new_val
            
            optima.append(round(best_val, 2))
        
        n_distinct = len(set(optima))
        variance = float(np.var(optima))
        
        if n_distinct <= 3:
            landscape_type = LandscapeType.SMOOTH
        elif n_distinct <= 10:
            landscape_type = LandscapeType.MIXED
        else:
            landscape_type = LandscapeType.RUGGED
        
        return LandscapeAnalysis(
            n_local_optima=n_distinct,
            optima_values=optima,
            variance=variance,
            landscape_type=landscape_type,
        )
    
    def _analyze_gradient(
        self,
        objective: Callable,
        dimension: int,
        domain: Tuple[float, float],
    ) -> GradientAnalysis:
        """Analyze gradient reliability."""
        lo, hi = domain
        consistencies = []
        
        for _ in range(self.n_gradient_samples):
            x = self.rng.uniform(lo, hi, dimension)
            f_x = objective(x)
            g1 = self._numerical_gradient(objective, x, f_x)
            
            # Perturbed gradient
            perturb = 0.01 * (hi - lo) * self.rng.standard_normal(dimension)
            x2 = np.clip(x + perturb, lo, hi)
            f_x2 = objective(x2)
            g2 = self._numerical_gradient(objective, x2, f_x2)
            
            # Cosine similarity
            n1, n2 = np.linalg.norm(g1), np.linalg.norm(g2)
            if n1 > 1e-10 and n2 > 1e-10:
                consistencies.append(max(0, np.dot(g1, g2) / (n1 * n2)))
        
        reliability = float(np.mean(consistencies)) if consistencies else 0.0
        
        return GradientAnalysis(
            reliability=reliability,
            is_convex=(reliability > 0.9),
        )
    
    def _numerical_gradient(
        self,
        objective: Callable,
        x: NDArray,
        f_x: Optional[float] = None,
        eps: float = 1e-6,
    ) -> NDArray:
        """Compute numerical gradient."""
        if f_x is None:
            f_x = objective(x)
        
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus = x.copy()
            x_plus[i] += eps
            grad[i] = (objective(x_plus) - f_x) / eps
        
        return grad
    
    def report(self, metrics: DiagnosticMetrics) -> str:
        """Generate diagnosis report."""
        problem_class = metrics.classify()
        weights = metrics.recommended_weights()
        
        lines = [
            "═" * 60,
            "PROBLEM DIAGNOSIS REPORT",
            "═" * 60,
            f"Problem Class: {problem_class.value.upper()}",
            f"Dimension: {metrics.dimension}",
            "",
            "SPECTRAL ANALYSIS (Ψ relevance):",
            f"  Spectral Gap: {metrics.spectral.spectral_gap:.4f}",
            f"  Condition Number: {metrics.spectral.condition_number:.2e}",
            f"  → {metrics.spectral.psi_relevance()}",
            "",
            "LANDSCAPE ANALYSIS (Σ relevance):",
            f"  Local Optima: {metrics.landscape.n_local_optima}",
            f"  Type: {metrics.landscape.landscape_type.value}",
            f"  → {metrics.landscape.sigma_relevance()}",
            "",
            "GRADIENT ANALYSIS (Ω relevance):",
            f"  Reliability: {metrics.gradient.reliability:.4f}",
            f"  Convex: {metrics.gradient.is_convex}",
            f"  → {metrics.gradient.omega_relevance()}",
            "",
            "CONSTRAINT ANALYSIS (D relevance):",
            f"  Hard Constraints: {metrics.constraint.has_hard_constraints}",
            f"  → {metrics.constraint.d_relevance()}",
            "",
            "RECOMMENDED WEIGHTS:",
        ]
        
        for pole, w in weights.items():
            bar = "█" * int(w * 20)
            lines.append(f"  {pole}: {w:.2f} {bar}")
        
        lines.append("═" * 60)
        return "\n".join(lines)


class QuickDiagnoser:
    """Fast diagnostic for quick pole selection."""
    
    @staticmethod
    def from_matrix(Q: NDArray) -> Dict[str, float]:
        """Quick diagnosis from matrix."""
        analysis = SpectralAnalysis.from_matrix(Q)
        
        if analysis.spectral_gap > 0.2:
            return {'Ψ': 0.60, 'Ω': 0.00, 'Σ': 0.00, 'D': 0.40}
        elif analysis.spectral_gap > 0.1:
            return {'Ψ': 0.40, 'Ω': 0.10, 'Σ': 0.20, 'D': 0.30}
        else:
            return {'Ψ': 0.25, 'Ω': 0.25, 'Σ': 0.25, 'D': 0.25}
    
    @staticmethod
    def from_signature(sig: ProblemSignature) -> Dict[str, float]:
        """Quick diagnosis from signature."""
        if sig.spectral_gap > 0.2 and sig.n_local_optima < 5:
            return {'Ψ': 0.60, 'Ω': 0.00, 'Σ': 0.00, 'D': 0.40}
        elif sig.spectral_gap > 0.1 and sig.n_local_optima > 5:
            return {'Ψ': 0.40, 'Ω': 0.00, 'Σ': 0.30, 'D': 0.30}
        elif sig.gradient_reliability > 0.7:
            return {'Ψ': 0.00, 'Ω': 0.60, 'Σ': 0.10, 'D': 0.30}
        elif sig.n_local_optima > 10:
            return {'Ψ': 0.00, 'Ω': 0.00, 'Σ': 0.60, 'D': 0.40}
        else:
            return {'Ψ': 0.25, 'Ω': 0.25, 'Σ': 0.25, 'D': 0.25}


# Strategy configurations based on empirical findings
STRATEGY_CONFIGS = {
    # 4-pole configurations
    '4-pole-equal': {'Ψ': 0.25, 'Ω': 0.25, 'Σ': 0.25, 'D': 0.25},
    '4-pole-psi-heavy': {'Ψ': 0.50, 'Ω': 0.15, 'Σ': 0.15, 'D': 0.20},
    '4-pole-omega-heavy': {'Ψ': 0.15, 'Ω': 0.50, 'Σ': 0.15, 'D': 0.20},
    '4-pole-sigma-heavy': {'Ψ': 0.15, 'Ω': 0.15, 'Σ': 0.50, 'D': 0.20},
    
    # 3-pole configurations
    'Ψ+Σ+D': {'Ψ': 0.40, 'Ω': 0.00, 'Σ': 0.30, 'D': 0.30},
    'Ψ+Ω+D': {'Ψ': 0.40, 'Ω': 0.30, 'Σ': 0.00, 'D': 0.30},
    'Ω+Σ+D': {'Ψ': 0.00, 'Ω': 0.35, 'Σ': 0.35, 'D': 0.30},
    
    # 2-pole configurations
    'Ψ+D': {'Ψ': 0.60, 'Ω': 0.00, 'Σ': 0.00, 'D': 0.40},
    'Ω+D': {'Ψ': 0.00, 'Ω': 0.70, 'Σ': 0.00, 'D': 0.30},
    'Σ+D': {'Ψ': 0.00, 'Ω': 0.00, 'Σ': 0.60, 'D': 0.40},
    
    # 1-pole configurations
    'D-only': {'Ψ': 0.00, 'Ω': 0.00, 'Σ': 0.00, 'D': 1.00},
}


def predict_best_strategy(sig: ProblemSignature) -> str:
    """Predict best strategy from problem signature."""
    # Decision tree based on empirical findings
    if 0.05 < sig.spectral_gap < 0.25 and 5 < sig.n_local_optima < 20:
        return '4-pole-equal'
    elif sig.spectral_gap > 0.2 and sig.n_local_optima < 5:
        return 'Ψ+D'
    elif sig.spectral_gap > 0.1 and sig.n_local_optima > 5:
        return 'Ψ+Σ+D'
    elif sig.gradient_reliability > 0.7 and sig.n_local_optima < 5:
        return 'Ω+D'
    elif sig.n_local_optima > 10:
        return 'Σ+D'
    else:
        return '4-pole-equal'
