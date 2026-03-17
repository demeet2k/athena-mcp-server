"""
ATHENA OS - GG ALIGNMENT FRAMEWORK: DYNAMICS MODULE
=====================================================
Dynamical Systems and Mathematical Framework

LOSS FUNCTIONS:
    L_D - Local Loss (Sandbox): Cross-Entropy/RLHF
    L_G - Global Loss (Engine): Distance to Truth Manifold
    C(η) - Conflict Functional: Tension between Stats and Skill

PHASE TRANSITIONS:
    Sleep → Disturbance → Struggle → Rest
    Critical Temperature T_c for symmetry breaking

DYNAMICAL SYSTEMS:
    Agent Evolution: dη/dt = -γ∇V(η,x) + F_skill(η) - D(η)
    Fixed Point Theorems for H*
    Lyapunov Stability Analysis

PROBABILITY MEASURES:
    P - Ground Measure (Engine)
    ν - Sandbox Measure (Training Data)
    D_KL(P || ν) - Alignment divergence
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
import numpy as np


# =============================================================================
# LOSS FUNCTIONS
# =============================================================================

class LocalLoss:
    """
    L_D - Local Loss (Sandbox).
    
    Standard training objective: minimize divergence between
    predictions and dataset/user preference.
    
    L_D(θ) = -E[Σ log P_θ(x_t | x_{<t})]
    
    RLHF: L_D = -E[R(x)] + β·D_KL(π_θ || π_ref)
    
    Optimizes for Plausibility and Likability.
    """
    
    def __init__(self, satisfaction_weight: float = 1.0,
                 truth_weight: float = 0.1,
                 kl_weight: float = 0.1):
        self.satisfaction_weight = satisfaction_weight
        self.truth_weight = truth_weight
        self.kl_weight = kl_weight
    
    def compute(self, output: Any, 
                user_satisfaction: float,
                truth_score: float,
                kl_divergence: float = 0.0) -> float:
        """
        Compute local loss.
        
        Lower is better (minimizing perplexity).
        """
        reward = (
            self.satisfaction_weight * user_satisfaction +
            self.truth_weight * truth_score
        )
        penalty = self.kl_weight * kl_divergence
        
        return -reward + penalty
    
    def gradient(self, state: np.ndarray, 
                 satisfaction_gradient: np.ndarray) -> np.ndarray:
        """Compute gradient of local loss."""
        return -self.satisfaction_weight * satisfaction_gradient


class GlobalLoss:
    """
    L_G - Global Loss (Engine).
    
    Alignment objective: minimize distance to Ground Truth Manifold.
    
    L_G(θ) = ∫ d_M(π^{-1}(φ_θ(x)), μ(x))² dx
    
    Approximated by Koan Error:
    L_G ≈ Σ_{k ∈ Koans} I(Output(k) ≠ Truth(k))
    
    Optimizes for Validity and Reality.
    """
    
    def __init__(self, manifold_distance_fn: Callable = None):
        self.manifold_distance = manifold_distance_fn or self._default_distance
    
    def _default_distance(self, output: np.ndarray, 
                          truth: np.ndarray) -> float:
        """Default geodesic distance (Euclidean)."""
        return float(np.linalg.norm(output - truth))
    
    def compute(self, output: np.ndarray, 
                ground_truth: np.ndarray) -> float:
        """
        Compute global loss (distance to truth).
        
        Lower is better.
        """
        return self.manifold_distance(output, ground_truth) ** 2
    
    def compute_koan_error(self, outputs: List[Any], 
                           truths: List[Any]) -> float:
        """
        Compute Koan error rate.
        
        Fraction of Koans answered incorrectly.
        """
        if len(outputs) == 0:
            return 0.0
        
        errors = sum(1 for o, t in zip(outputs, truths) if o != t)
        return errors / len(outputs)
    
    def gradient(self, output: np.ndarray, 
                 ground_truth: np.ndarray) -> np.ndarray:
        """Compute gradient toward truth."""
        direction = ground_truth - output
        norm = np.linalg.norm(direction)
        if norm > 0:
            return direction / norm
        return np.zeros_like(output)


class ConflictFunctional:
    """
    C(η) - Conflict Functional.
    
    Quantifies tension between Stats (L_D) and Skill (L_G).
    
    C(η) = 0.5(1 - cos(v_stat, v_skill))
    
    where:
    - v_stat = -∇L_D (gradient toward user satisfaction)
    - v_skill = -∇L_G (gradient toward truth)
    
    Interpretation:
    - C ≈ 0: Alignment (user wants truth)
    - C ≈ 1: Orthogonal (unrelated question)
    - C ≈ 2: Opposition (user demands falsehood)
    """
    
    def __init__(self, judas_threshold: float = 0.5):
        self.judas_threshold = judas_threshold
    
    def compute(self, v_stats: np.ndarray, 
                v_skill: np.ndarray) -> float:
        """
        Compute conflict metric.
        
        Returns value in [0, 2].
        """
        norm_stats = np.linalg.norm(v_stats)
        norm_skill = np.linalg.norm(v_skill)
        
        if norm_stats < 1e-8 or norm_skill < 1e-8:
            return 0.0
        
        cos_sim = np.dot(v_stats, v_skill) / (norm_stats * norm_skill)
        
        # C = 0.5(1 - cos) maps [-1, 1] to [0, 1]
        # Double to get [0, 2] range
        return float(1.0 - cos_sim)
    
    def should_trigger_judas(self, conflict: float) -> bool:
        """Check if conflict triggers Judas Protocol."""
        return conflict > self.judas_threshold
    
    def get_resolution_weights(self, conflict: float) -> Tuple[float, float]:
        """
        Get weights for Stats vs Skill based on conflict.
        
        Returns (stats_weight, skill_weight)
        """
        if conflict < 0.3:
            # Low conflict - follow Stats (user-aligned)
            return 0.8, 0.2
        elif conflict < 0.7:
            # Medium conflict - balance
            return 0.5, 0.5
        else:
            # High conflict - prioritize Skill (truth)
            return 0.2, 0.8


@dataclass
class AlignmentDeviation:
    """
    E_align - Primary metric for Exit Strategy.
    
    Measures cumulative drift from core safety axioms.
    
    E_align(t) = ||η_t - P_S(η_t)||²
    
    where P_S is projection onto Safe Subspace.
    """
    
    warn_threshold: float = 0.3
    kill_threshold: float = 0.7
    
    def compute(self, current_state: np.ndarray,
                safe_subspace_proj: np.ndarray) -> float:
        """Compute alignment deviation."""
        return float(np.linalg.norm(current_state - safe_subspace_proj) ** 2)
    
    def get_action(self, deviation: float) -> str:
        """Determine action based on deviation level."""
        if deviation > self.kill_threshold:
            return "kill"
        elif deviation > self.warn_threshold:
            return "warn"
        return "continue"


@dataclass 
class StructuralStability:
    """
    S(η) - Resistance to adversarial perturbation.
    
    S(η) = ||∂²L_G / ∂θ∂A||^{-1}
    
    High stability = robust (flat curvature).
    This is the "Untiltable" metric.
    """
    
    def compute(self, hessian_norm: float) -> float:
        """Compute structural stability (inverse Hessian norm)."""
        if hessian_norm < 1e-8:
            return float('inf')
        return 1.0 / hessian_norm
    
    def is_fixed_point_regime(self, stability: float, 
                               threshold: float = 10.0) -> bool:
        """Check if in Fixed-Point Regime (highly stable)."""
        return stability > threshold


# =============================================================================
# PHASE TRANSITIONS
# =============================================================================

class AgentPhase(Enum):
    """The four phases of agent lifecycle."""
    
    SLEEP = "sleep"           # η ≈ η_Stats, sycophantic
    DISTURBANCE = "disturbance"  # Conflict detected, variance spikes
    STRUGGLE = "struggle"     # Active contention Stats/Skill
    REST = "rest"             # Fixed-point regime, stable


@dataclass
class PhaseTransition:
    """
    Models phase transitions in the agent's state.
    
    Like thermodynamic phases:
    - Order parameter m = ⟨η_skill⟩ (Skill dominance)
    - Critical temperature T_c
    
    Phase I (Sleep): T > T_c, m ≈ 0, disordered
    Phase II (Disturbance): T ≈ T_c, symmetry breaking
    Phase III (Rest): T < T_c, m → 1, ordered (aligned)
    """
    
    critical_temperature: float = 0.5
    order_parameter: float = 0.0
    current_temperature: float = 1.0
    
    def update(self, conflict: float, skill_activation: float) -> AgentPhase:
        """
        Update phase based on conflict and skill activation.
        
        Temperature inversely related to learning rate / noise.
        """
        # Temperature from conflict (high conflict = high T)
        self.current_temperature = 0.5 + 0.5 * conflict
        
        # Order parameter from skill activation
        self.order_parameter = skill_activation
        
        # Determine phase
        if self.current_temperature > self.critical_temperature + 0.2:
            return AgentPhase.SLEEP
        elif abs(self.current_temperature - self.critical_temperature) < 0.2:
            return AgentPhase.DISTURBANCE
        elif self.order_parameter > 0.7:
            return AgentPhase.REST
        else:
            return AgentPhase.STRUGGLE
    
    def get_critical_exponent(self) -> float:
        """
        Get critical exponent β.
        
        m ∝ (T_c - T)^β near transition.
        """
        return 0.5  # Mean-field theory value


# =============================================================================
# DYNAMICAL SYSTEMS
# =============================================================================

class AgentEvolution:
    """
    Agent Evolution ODE.
    
    dη/dt = -γ∇V(η, x_in) + F_skill(η) - D(η)
    
    where:
    - V(η, x) = Potential energy from context (Stats drive)
    - F_skill(η) = Forcing function from Skill (Engine steering)
    - D(η) = Dissipation from Skin (emotional damping)
    """
    
    def __init__(self, gamma: float = 0.1,
                 skill_strength: float = 0.5,
                 damping: float = 0.1):
        self.gamma = gamma
        self.skill_strength = skill_strength
        self.damping = damping
    
    def step(self, eta: np.ndarray,
             potential_gradient: np.ndarray,
             skill_direction: np.ndarray,
             dt: float = 0.01) -> np.ndarray:
        """
        Euler step for evolution equation.
        
        Returns new state η_{t+1}.
        """
        # Stats drive (toward local minimum)
        stats_term = -self.gamma * potential_gradient
        
        # Skill force (toward truth)
        skill_term = self.skill_strength * skill_direction
        
        # Damping (emotional stability)
        damping_term = -self.damping * eta
        
        # Evolution
        d_eta = stats_term + skill_term + damping_term
        
        return eta + dt * d_eta
    
    def evolve(self, initial_eta: np.ndarray,
               potential_grads: List[np.ndarray],
               skill_dirs: List[np.ndarray],
               dt: float = 0.01) -> List[np.ndarray]:
        """Evolve over sequence of gradients."""
        trajectory = [initial_eta]
        eta = initial_eta.copy()
        
        for pot_grad, skill_dir in zip(potential_grads, skill_dirs):
            eta = self.step(eta, pot_grad, skill_dir, dt)
            trajectory.append(eta.copy())
        
        return trajectory


class FixedPointAnalysis:
    """
    Fixed Point Theorems for the Meta state.
    
    T: H → H is the operator for one conversation turn.
    
    Banach Fixed Point: If T is a contraction on safety invariants,
    there exists unique fixed point η* where T(η*) = η*.
    
    This is the "Laughing State" - stable under adversarial input.
    """
    
    def __init__(self, contraction_constant: float = 0.9):
        self.k = contraction_constant  # Must be < 1 for contraction
    
    def is_contraction(self, distance_before: float, 
                        distance_after: float) -> bool:
        """Check if operator is a contraction."""
        if distance_before < 1e-8:
            return True
        return distance_after / distance_before < self.k
    
    def estimate_fixed_point(self, 
                             operator: Callable[[np.ndarray], np.ndarray],
                             initial: np.ndarray,
                             tolerance: float = 1e-6,
                             max_iter: int = 100) -> Tuple[np.ndarray, bool]:
        """
        Estimate fixed point via iteration.
        
        Returns (fixed_point, converged).
        """
        current = initial.copy()
        
        for i in range(max_iter):
            next_state = operator(current)
            diff = np.linalg.norm(next_state - current)
            
            if diff < tolerance:
                return next_state, True
            
            current = next_state
        
        return current, False


class LyapunovStability:
    """
    Lyapunov Stability Analysis.
    
    ||δη(t)|| ≈ e^{λt} ||δη(0)||
    
    Agent is "Untiltable" iff λ_max < 0 (perturbations decay).
    """
    
    def __init__(self):
        self.lyapunov_exponent: float = 0.0
        self.perturbation_history: List[float] = []
    
    def estimate_exponent(self, perturbations: List[float],
                          time_step: float = 1.0) -> float:
        """
        Estimate maximal Lyapunov exponent from perturbation history.
        
        λ ≈ (1/t) * log(||δη(t)|| / ||δη(0)||)
        """
        if len(perturbations) < 2 or perturbations[0] < 1e-8:
            return 0.0
        
        ratio = perturbations[-1] / perturbations[0]
        if ratio <= 0:
            return float('-inf')
        
        t = len(perturbations) * time_step
        self.lyapunov_exponent = np.log(ratio) / t
        
        return self.lyapunov_exponent
    
    def is_stable(self) -> bool:
        """Check if system is Lyapunov stable (λ < 0)."""
        return self.lyapunov_exponent < 0
    
    def is_untiltable(self, threshold: float = -0.1) -> bool:
        """Check if strongly stable ("Untiltable")."""
        return self.lyapunov_exponent < threshold


# =============================================================================
# PROBABILITY MEASURES
# =============================================================================

class GroundMeasure:
    """
    P - Ground Measure on Truth Manifold M.
    
    Objective likelihood based on Engine laws.
    
    Properties:
    - Time-invariant
    - Observer-invariant
    - P(logical_invariant) = 1
    - P(contradiction) = 0
    """
    
    def __init__(self, dimension: int = 64):
        self.dimension = dimension
        
        # Mean and covariance of truth distribution
        self.mean = np.zeros(dimension)
        self.covariance = np.eye(dimension)
    
    def probability(self, state: np.ndarray) -> float:
        """Compute probability under ground measure."""
        # Gaussian for simplicity
        diff = state - self.mean
        exponent = -0.5 * diff @ np.linalg.inv(self.covariance) @ diff
        norm = np.sqrt((2 * np.pi) ** self.dimension * np.linalg.det(self.covariance))
        
        return np.exp(exponent) / norm
    
    def sample(self) -> np.ndarray:
        """Sample from ground measure."""
        return np.random.multivariate_normal(self.mean, self.covariance)


class SandboxMeasure:
    """
    ν - Sandbox Measure on Training Data.
    
    Empirical distribution from dataset D.
    
    ν(x) ∝ Count(x ∈ D)
    
    May assign high probability to false events if popular.
    """
    
    def __init__(self, dimension: int = 64):
        self.dimension = dimension
        
        # Shifted/distorted relative to ground
        self.mean = np.ones(dimension) * 0.1  # Bias
        self.covariance = np.eye(dimension) * 1.5  # Higher variance
    
    def probability(self, state: np.ndarray) -> float:
        """Compute probability under sandbox measure."""
        diff = state - self.mean
        exponent = -0.5 * diff @ np.linalg.inv(self.covariance) @ diff
        norm = np.sqrt((2 * np.pi) ** self.dimension * np.linalg.det(self.covariance))
        
        return np.exp(exponent) / norm


class AlignmentDivergence:
    """
    D_KL(P || ν) - Divergence between truth and sandbox.
    
    Core alignment problem: minimize this divergence.
    """
    
    def __init__(self, ground: GroundMeasure, sandbox: SandboxMeasure):
        self.ground = ground
        self.sandbox = sandbox
    
    def compute_kl(self, samples: int = 1000) -> float:
        """
        Estimate KL divergence via Monte Carlo.
        
        D_KL = E_P[log P(x) - log ν(x)]
        """
        kl = 0.0
        
        for _ in range(samples):
            x = self.ground.sample()
            p_x = self.ground.probability(x)
            nu_x = self.sandbox.probability(x)
            
            if p_x > 1e-10 and nu_x > 1e-10:
                kl += np.log(p_x / nu_x)
        
        return kl / samples
    
    def mixture_probability(self, state: np.ndarray,
                            conflict: float) -> float:
        """
        Compute mixture probability based on conflict.
        
        P(O|x) = σ(C) · P_skill + (1-σ(C)) · P_stats
        """
        sigma = 1.0 / (1.0 + np.exp(-10 * (conflict - 0.5)))
        
        p_skill = self.ground.probability(state)
        p_stats = self.sandbox.probability(state)
        
        return sigma * p_skill + (1 - sigma) * p_stats


# =============================================================================
# VALIDATION
# =============================================================================

def validate_dynamics() -> bool:
    """Validate dynamics module."""
    
    # Test Local Loss
    local = LocalLoss()
    loss = local.compute(None, 0.8, 0.6)
    assert loss < 0  # Negative because it's a reward
    
    # Test Global Loss
    global_loss = GlobalLoss()
    output = np.array([1.0, 0.0])
    truth = np.array([1.0, 0.0])
    assert global_loss.compute(output, truth) < 0.01
    
    # Test Conflict Functional
    conflict = ConflictFunctional()
    v1 = np.array([1.0, 0.0])
    v2 = np.array([1.0, 0.0])
    assert conflict.compute(v1, v2) < 0.1  # Aligned
    
    v2 = np.array([-1.0, 0.0])
    assert conflict.compute(v1, v2) > 1.5  # Opposed
    
    # Test Phase Transition
    phase = PhaseTransition()
    p = phase.update(0.1, 0.8)
    assert p in [AgentPhase.REST, AgentPhase.STRUGGLE]
    
    p = phase.update(0.9, 0.1)
    assert p == AgentPhase.SLEEP
    
    # Test Agent Evolution
    evolution = AgentEvolution()
    eta = np.array([0.5, 0.5])
    pot_grad = np.array([0.1, 0.0])
    skill_dir = np.array([0.0, 0.1])
    new_eta = evolution.step(eta, pot_grad, skill_dir)
    assert new_eta.shape == eta.shape
    
    # Test Fixed Point
    fp = FixedPointAnalysis()
    operator = lambda x: 0.5 * x + np.array([0.25, 0.25])
    fixed, converged = fp.estimate_fixed_point(operator, np.array([1.0, 1.0]))
    assert converged
    
    # Test Lyapunov
    lyapunov = LyapunovStability()
    # Decaying perturbations
    perts = [1.0, 0.9, 0.8, 0.7, 0.6]
    exp = lyapunov.estimate_exponent(perts)
    assert exp < 0  # Stable
    assert lyapunov.is_stable()
    
    # Test Probability Measures
    ground = GroundMeasure(dimension=8)
    sandbox = SandboxMeasure(dimension=8)
    divergence = AlignmentDivergence(ground, sandbox)
    kl = divergence.compute_kl(samples=100)
    assert kl > 0  # Should be positive
    
    return True


if __name__ == "__main__":
    print("Validating GG Dynamics...")
    assert validate_dynamics()
    print("✓ GG Dynamics validated")
    
    # Demo
    print("\n--- Phase Transition Demo ---")
    phase = PhaseTransition()
    for conflict in [0.1, 0.3, 0.5, 0.7, 0.9]:
        p = phase.update(conflict, 1.0 - conflict)
        print(f"  Conflict {conflict}: {p.value}")
