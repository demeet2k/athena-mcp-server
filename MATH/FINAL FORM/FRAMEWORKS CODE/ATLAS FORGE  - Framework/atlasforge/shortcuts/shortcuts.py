"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Algorithmic Shortcut Analysis                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Formalizes "shortcuts" in the quad-polar framework.

Definition: A hybrid algorithm is a SHORTCUT when its evolution operator
reaches a target in substantially fewer steps than any evolution
restricted to a single pole.

Shortcut Types:
1. State-space shortcuts: Traverse regions inaccessible to single poles
2. Scale-space shortcuts: Move information between resolutions efficiently

Shortcut Mechanisms:
- Adding Ω to D: Geometric acceleration via continuous relaxation
- Adding Σ to Ω: Escape local minima via stochastic exploration
- Adding Ψ to any: Compress across scales, eliminate slow modes

Shortcut Factor S(ε):
    C_hybrid(P, ε) ≤ C_baseline(P, ε) / S(ε)
    
where C is cost (iterations, evaluations, or time).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


class ShortcutType(Enum):
    """Types of algorithmic shortcuts."""
    STATE_SPACE = "state"       # Traverse state space more efficiently
    SCALE_SPACE = "scale"       # Move between resolutions
    SPECTRAL = "spectral"       # Improve spectral properties
    MIXING = "mixing"           # Faster mixing to equilibrium


class FailureMode(Enum):
    """Common failure modes that shortcuts can address."""
    SLOW_CONVERGENCE = "slow_convergence"       # High condition number
    LOCAL_MINIMA = "local_minima"               # Trapped in local optima
    POOR_EXPLORATION = "poor_exploration"       # Limited state space coverage
    SCALE_SEPARATION = "scale_separation"       # Slow modes dominate
    ILL_CONDITIONING = "ill_conditioning"       # Numerical instability
    HIGH_VARIANCE = "high_variance"             # Noisy estimates


@dataclass
class BaselineMethod:
    """Characterization of a baseline (single-pole) method."""
    name: str
    dominant_pole: str              # D, Ω, Σ, or Ψ
    complexity: str                 # Big-O complexity
    convergence_rate: str           # Rate description
    failure_modes: List[FailureMode]
    typical_factor: float           # Typical convergence factor
    
    def describe(self) -> str:
        return f"{self.name} ({self.dominant_pole}): {self.convergence_rate}"


@dataclass
class HybridMethod:
    """Characterization of a hybrid (multi-pole) method."""
    name: str
    poles: List[str]                # Active poles
    weights: Dict[str, float]       # Pole weights
    complexity: str
    convergence_rate: str
    addresses: List[FailureMode]    # Which failure modes it addresses
    typical_factor: float
    
    def describe(self) -> str:
        pole_str = "+".join(self.poles)
        return f"{self.name} ({pole_str}): {self.convergence_rate}"


@dataclass
class ShortcutAnalysis:
    """Complete analysis of a shortcut transformation."""
    baseline: BaselineMethod
    hybrid: HybridMethod
    shortcut_type: ShortcutType
    
    # Quantitative improvements
    iteration_speedup: float        # Baseline_iters / Hybrid_iters
    complexity_speedup: str         # e.g., "O(κ) → O(√κ)"
    spectral_improvement: float     # Spectral gap improvement
    
    # Conditions for shortcut
    conditions: List[str]           # When does this shortcut apply?
    counter_conditions: List[str]   # When does it fail?
    
    def summary(self) -> str:
        lines = [
            "=" * 60,
            "SHORTCUT ANALYSIS",
            "=" * 60,
            f"Baseline: {self.baseline.describe()}",
            f"Hybrid:   {self.hybrid.describe()}",
            f"Type:     {self.shortcut_type.value}",
            "",
            f"Speedup:  {self.iteration_speedup:.1f}x iterations",
            f"Complexity: {self.complexity_speedup}",
            "",
            "Applies when:",
        ]
        for cond in self.conditions:
            lines.append(f"  ✓ {cond}")
        
        if self.counter_conditions:
            lines.append("")
            lines.append("May fail when:")
            for cond in self.counter_conditions:
                lines.append(f"  ✗ {cond}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


# Pre-defined baseline methods (single pole)
BASELINE_METHODS = {
    'gradient_descent': BaselineMethod(
        name="Gradient Descent",
        dominant_pole="Ω",
        complexity="O(κ n²)",
        convergence_rate="Linear: (κ-1)/(κ+1) per iter",
        failure_modes=[FailureMode.SLOW_CONVERGENCE, FailureMode.LOCAL_MINIMA],
        typical_factor=0.99,
    ),
    'random_walk': BaselineMethod(
        name="Random Walk",
        dominant_pole="Σ",
        complexity="O(n² t_mix)",
        convergence_rate="Mixing time t_mix",
        failure_modes=[FailureMode.POOR_EXPLORATION, FailureMode.HIGH_VARIANCE],
        typical_factor=0.95,
    ),
    'local_search': BaselineMethod(
        name="Local Search",
        dominant_pole="D",
        complexity="O(n k)",
        convergence_rate="Problem-dependent",
        failure_modes=[FailureMode.LOCAL_MINIMA, FailureMode.SCALE_SEPARATION],
        typical_factor=0.9,
    ),
    'jacobi': BaselineMethod(
        name="Jacobi Iteration",
        dominant_pole="D",
        complexity="O(n² k)",
        convergence_rate="Linear: ρ per iter",
        failure_modes=[FailureMode.SLOW_CONVERGENCE, FailureMode.ILL_CONDITIONING],
        typical_factor=0.95,
    ),
}

# Pre-defined hybrid methods (multi-pole)
HYBRID_METHODS = {
    'accelerated_gd': HybridMethod(
        name="Accelerated GD (Nesterov)",
        poles=["Ω", "D"],
        weights={"Ω": 0.7, "D": 0.3},
        complexity="O(√κ n²)",
        convergence_rate="Accelerated: (√κ-1)/(√κ+1)",
        addresses=[FailureMode.SLOW_CONVERGENCE],
        typical_factor=0.9,
    ),
    'simulated_annealing': HybridMethod(
        name="Simulated Annealing",
        poles=["Ω", "Σ"],
        weights={"Ω": 0.5, "Σ": 0.5},
        complexity="O(n log(n) T)",
        convergence_rate="Probabilistic global",
        addresses=[FailureMode.LOCAL_MINIMA, FailureMode.POOR_EXPLORATION],
        typical_factor=0.85,
    ),
    'multigrid': HybridMethod(
        name="Multigrid",
        poles=["D", "Ψ"],
        weights={"D": 0.4, "Ψ": 0.6},
        complexity="O(n)",
        convergence_rate="Optimal: ~0.1 per V-cycle",
        addresses=[FailureMode.SLOW_CONVERGENCE, FailureMode.SCALE_SEPARATION],
        typical_factor=0.1,
    ),
    'hmc': HybridMethod(
        name="Hamiltonian Monte Carlo",
        poles=["Ω", "Σ"],
        weights={"Ω": 0.6, "Σ": 0.4},
        complexity="O(n √κ)",
        convergence_rate="√κ improvement over RW",
        addresses=[FailureMode.POOR_EXPLORATION, FailureMode.HIGH_VARIANCE],
        typical_factor=0.7,
    ),
    'hybrid_sa_local': HybridMethod(
        name="SA + Local Search",
        poles=["D", "Σ"],
        weights={"D": 0.5, "Σ": 0.5},
        complexity="O(n k T)",
        convergence_rate="Global + local polish",
        addresses=[FailureMode.LOCAL_MINIMA],
        typical_factor=0.8,
    ),
    '4_pole_equal': HybridMethod(
        name="4-Pole Equal",
        poles=["D", "Ω", "Σ", "Ψ"],
        weights={"D": 0.25, "Ω": 0.25, "Σ": 0.25, "Ψ": 0.25},
        complexity="Problem-dependent",
        convergence_rate="Adaptive",
        addresses=[FailureMode.SLOW_CONVERGENCE, FailureMode.LOCAL_MINIMA, 
                   FailureMode.SCALE_SEPARATION],
        typical_factor=0.5,
    ),
}


class ShortcutDesigner:
    """
    Design shortcuts by analyzing failure modes and adding poles.
    
    The quad-polar framework provides a design grammar:
    1. Start from baseline pole
    2. Identify failure mode
    3. Add minimal missing pole to counteract failure
    """
    
    # Pole -> Failure mode it addresses
    POLE_REMEDIES = {
        'D': [FailureMode.POOR_EXPLORATION],  # Discrete structure
        'Ω': [FailureMode.SLOW_CONVERGENCE, FailureMode.ILL_CONDITIONING],
        'Σ': [FailureMode.LOCAL_MINIMA, FailureMode.HIGH_VARIANCE],
        'Ψ': [FailureMode.SCALE_SEPARATION, FailureMode.SLOW_CONVERGENCE],
    }
    
    @classmethod
    def diagnose_failure(
        cls,
        baseline: str,
        problem_signature: Dict[str, Any],
    ) -> List[FailureMode]:
        """Diagnose likely failure modes for a baseline method."""
        failures = []
        method = BASELINE_METHODS.get(baseline)
        
        if method:
            failures.extend(method.failure_modes)
        
        # Additional diagnosis based on problem signature
        if problem_signature.get('condition_number', 1) > 100:
            failures.append(FailureMode.SLOW_CONVERGENCE)
        
        if problem_signature.get('n_local_optima', 1) > 5:
            failures.append(FailureMode.LOCAL_MINIMA)
        
        if problem_signature.get('spectral_gap', 1) < 0.1:
            failures.append(FailureMode.SCALE_SEPARATION)
        
        return list(set(failures))
    
    @classmethod
    def recommend_pole(cls, failure: FailureMode) -> str:
        """Recommend pole to add for given failure mode."""
        for pole, failures in cls.POLE_REMEDIES.items():
            if failure in failures:
                return pole
        return 'D'  # Default to discrete
    
    @classmethod
    def design_shortcut(
        cls,
        baseline: str,
        problem_signature: Dict[str, Any],
    ) -> Tuple[str, Dict[str, float]]:
        """
        Design a shortcut hybrid method.
        
        Returns:
            (hybrid_name, weights)
        """
        failures = cls.diagnose_failure(baseline, problem_signature)
        
        # Start with baseline pole
        base_method = BASELINE_METHODS.get(baseline)
        current_poles = {base_method.dominant_pole} if base_method else {'D'}
        
        # Add poles to address failures
        for failure in failures:
            new_pole = cls.recommend_pole(failure)
            current_poles.add(new_pole)
        
        # Determine weights based on problem
        poles = list(current_poles)
        n_poles = len(poles)
        
        # Default: equal weights
        weights = {p: 1.0 / n_poles for p in poles}
        
        # Adjust based on problem signature
        if problem_signature.get('spectral_gap', 0) > 0.2:
            if 'Ψ' in weights:
                weights['Ψ'] *= 2.0
        
        if problem_signature.get('gradient_reliability', 1) > 0.7:
            if 'Ω' in weights:
                weights['Ω'] *= 1.5
        
        # Normalize
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}
        
        # Find matching hybrid or create name
        pole_set = frozenset(poles)
        for name, method in HYBRID_METHODS.items():
            if frozenset(method.poles) == pole_set:
                return name, weights
        
        return '+'.join(sorted(poles)), weights


def analyze_shortcut(
    baseline: str,
    hybrid: str,
    condition_number: float = 100,
) -> ShortcutAnalysis:
    """
    Analyze the shortcut between baseline and hybrid methods.
    """
    base = BASELINE_METHODS.get(baseline)
    hyb = HYBRID_METHODS.get(hybrid)
    
    if not base or not hyb:
        raise ValueError(f"Unknown method: {baseline} or {hybrid}")
    
    # Compute speedup based on condition number
    kappa = condition_number
    
    if baseline == 'gradient_descent' and hybrid == 'accelerated_gd':
        speedup = np.sqrt(kappa)
        complexity = f"O(κ) → O(√κ) where κ={kappa:.0f}"
        shortcut_type = ShortcutType.SPECTRAL
        
    elif baseline == 'jacobi' and hybrid == 'multigrid':
        speedup = kappa  # Multigrid is O(N) vs O(κN)
        complexity = "O(κ N) → O(N)"
        shortcut_type = ShortcutType.SCALE_SPACE
        
    elif baseline == 'random_walk' and hybrid == 'hmc':
        speedup = np.sqrt(kappa)
        complexity = f"O(κ) → O(√κ) mixing"
        shortcut_type = ShortcutType.MIXING
        
    elif baseline == 'local_search' and hybrid == 'simulated_annealing':
        speedup = 10  # Approximate
        complexity = "Local → Global search"
        shortcut_type = ShortcutType.STATE_SPACE
        
    else:
        speedup = base.typical_factor / hyb.typical_factor
        complexity = f"{base.complexity} → {hyb.complexity}"
        shortcut_type = ShortcutType.STATE_SPACE
    
    # Conditions
    conditions = [
        f"Problem has structure exploitable by {', '.join(hyb.poles)}",
    ]
    if 'Ψ' in hyb.poles:
        conditions.append("Multi-scale structure exists")
    if 'Σ' in hyb.poles:
        conditions.append("Need to escape local minima")
    
    counter_conditions = [
        "Pole overhead exceeds savings",
        "Problem lacks exploitable structure",
    ]
    
    return ShortcutAnalysis(
        baseline=base,
        hybrid=hyb,
        shortcut_type=shortcut_type,
        iteration_speedup=speedup,
        complexity_speedup=complexity,
        spectral_improvement=speedup,
        conditions=conditions,
        counter_conditions=counter_conditions,
    )


# Common shortcut patterns
SHORTCUT_PATTERNS = {
    'relax_project': {
        'description': 'Continuous relaxation + discrete projection',
        'baseline': 'D',
        'addition': 'Ω',
        'mechanism': 'Solve in continuous space, project to discrete',
        'examples': ['LP relaxation', 'SDP rounding'],
    },
    'accelerate': {
        'description': 'Add momentum/inertia to gradient flow',
        'baseline': 'Ω',
        'addition': 'D (inertia)',
        'mechanism': 'Heavy-ball/Nesterov acceleration',
        'examples': ['Accelerated GD', 'Momentum SGD'],
    },
    'anneal': {
        'description': 'Add stochastic escape to local search',
        'baseline': 'D',
        'addition': 'Σ',
        'mechanism': 'Random perturbations with cooling schedule',
        'examples': ['Simulated annealing', 'Basin hopping'],
    },
    'multigrid': {
        'description': 'Add hierarchical coarsening',
        'baseline': 'D (smoother)',
        'addition': 'Ψ',
        'mechanism': 'Coarse-grid correction eliminates slow modes',
        'examples': ['Multigrid', 'FMG'],
    },
    'hmc': {
        'description': 'Add Hamiltonian dynamics to MCMC',
        'baseline': 'Σ',
        'addition': 'Ω',
        'mechanism': 'Long-range moves via Hamiltonian flow',
        'examples': ['HMC', 'NUTS'],
    },
}


def list_shortcut_patterns() -> str:
    """List all known shortcut patterns."""
    lines = [
        "=" * 70,
        "ALGORITHMIC SHORTCUT PATTERNS",
        "=" * 70,
    ]
    
    for name, pattern in SHORTCUT_PATTERNS.items():
        lines.append(f"\n{name.upper()}")
        lines.append("-" * 40)
        lines.append(f"Description: {pattern['description']}")
        lines.append(f"Baseline:    {pattern['baseline']}")
        lines.append(f"Addition:    {pattern['addition']}")
        lines.append(f"Mechanism:   {pattern['mechanism']}")
        lines.append(f"Examples:    {', '.join(pattern['examples'])}")
    
    lines.append("\n" + "=" * 70)
    return "\n".join(lines)
