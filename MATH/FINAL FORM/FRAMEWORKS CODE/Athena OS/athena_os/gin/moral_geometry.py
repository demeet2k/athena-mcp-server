"""
ATHENA OS - GLOBAL INFORMATION NETWORK
======================================
Moral Geometry: The Metric of Dharmic Deviation

From GLOBAL_INFORMATION_NETWORK.docx §13:

MORAL METRIC TENSOR (g^(moral)_μν):
    
    D(m): Scalar moral potential (dharmic deviation)
    D(m) = 0 at moral equilibrium
    ∇D drives corrective flow
    
    The moral metric satisfies:
    1. Local comparability - induces cost norm
    2. Compatibility with deviation - anchored to ontological geometry
    3. Geodesic deviation meaning - squared moral distance

KURUKSHETRA (K_F):
    The battlefield manifold where constraint violation is high.
    
    V_F(m): Constraint violation potential
    K_F(λ) := {m ∈ M_F : V_F(m) ≥ λ}
    
    Fire sector operates on K_F where action selection,
    deadlock, and resolution require principled runtime calculus.

WILL VECTOR:
    W(m) := argmin_{u ∈ U} ⟨∇Φ(m), u⟩_moral
    
    Best descent direction under moral metric.
    Will collapse: W(m) = 0 while ||∇Φ||_moral > 0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod


# =============================================================================
# MORAL POTENTIAL
# =============================================================================

@dataclass
class MoralPotential:
    """
    D: M_F → R - Scalar moral potential.
    
    D(m) = 0 at moral equilibrium
    D(m) > 0 indicates dharmic deviation
    ∇D drives corrective flow
    """
    
    dim: int = 4
    equilibrium: np.ndarray = field(default_factory=lambda: np.zeros(4))
    
    # Potential parameters
    curvature: float = 1.0    # How sharply potential increases with deviation
    anisotropy: np.ndarray = field(default_factory=lambda: np.ones(4))
    
    def __call__(self, state: np.ndarray) -> float:
        """Compute moral potential at state."""
        deviation = state - self.equilibrium
        weighted = deviation * self.anisotropy
        return float(self.curvature * np.sum(weighted ** 2))
    
    def gradient(self, state: np.ndarray) -> np.ndarray:
        """Compute gradient ∇D at state."""
        deviation = state - self.equilibrium
        return 2.0 * self.curvature * self.anisotropy * deviation
    
    def hessian(self, state: np.ndarray) -> np.ndarray:
        """Compute Hessian ∇²D at state."""
        return 2.0 * self.curvature * np.diag(self.anisotropy)
    
    def at_equilibrium(self, state: np.ndarray, threshold: float = 1e-6) -> bool:
        """Check if state is at moral equilibrium."""
        return self(state) < threshold


# =============================================================================
# MORAL METRIC TENSOR
# =============================================================================

@dataclass
class MoralMetric:
    """
    g^(moral)_μν: The moral metric tensor.
    
    Measures the cost of infinitesimal deviation directions.
    Compatible with dharmic deviation potential.
    
    g^(moral) = α(m) ∇∇D + β(m) g^(onto)
    """
    
    dim: int = 4
    potential: MoralPotential = field(default_factory=MoralPotential)
    
    # Coupling parameters
    alpha: float = 1.0    # Weight of dharmic curvature
    beta: float = 0.1     # Weight of ontological metric
    
    def tensor(self, state: np.ndarray) -> np.ndarray:
        """
        Compute metric tensor at state.
        
        g_μν = α ∇_μ∇_ν D + β δ_μν
        """
        hess = self.potential.hessian(state)
        onto = np.eye(self.dim)  # Ontological metric (identity)
        
        return self.alpha * hess + self.beta * onto
    
    def inverse(self, state: np.ndarray) -> np.ndarray:
        """Compute inverse metric g^μν."""
        g = self.tensor(state)
        return np.linalg.inv(g + 1e-10 * np.eye(self.dim))
    
    def norm(self, state: np.ndarray, vector: np.ndarray) -> float:
        """
        Compute moral norm of vector at state.
        
        ||v||²_moral = g_μν v^μ v^ν
        """
        g = self.tensor(state)
        return float(np.sqrt(vector @ g @ vector + 1e-10))
    
    def inner_product(self, state: np.ndarray, 
                      v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Compute moral inner product.
        
        ⟨v1, v2⟩_moral = g_μν v1^μ v2^ν
        """
        g = self.tensor(state)
        return float(v1 @ g @ v2)
    
    def distance(self, m0: np.ndarray, m1: np.ndarray, 
                 steps: int = 100) -> float:
        """
        Compute approximate geodesic distance.
        
        d_moral(m0, m1)² = inf_γ (∫ √(g_γ(γ̇, γ̇)) dt)²
        
        Approximated by line integral along straight path.
        """
        total = 0.0
        
        for i in range(steps):
            t = i / steps
            state = m0 + t * (m1 - m0)
            tangent = (m1 - m0) / steps
            total += self.norm(state, tangent)
        
        return total
    
    def christoffel(self, state: np.ndarray) -> np.ndarray:
        """
        Compute Christoffel symbols Γ^ρ_μν.
        
        Used for geodesic equation and parallel transport.
        """
        eps = 1e-6
        g_inv = self.inverse(state)
        gamma = np.zeros((self.dim, self.dim, self.dim))
        
        for mu in range(self.dim):
            for nu in range(self.dim):
                for rho in range(self.dim):
                    # Approximate ∂_σ g_μν
                    for sigma in range(self.dim):
                        e_sigma = np.zeros(self.dim)
                        e_sigma[sigma] = eps
                        
                        g_plus = self.tensor(state + e_sigma)
                        g_minus = self.tensor(state - e_sigma)
                        dg = (g_plus - g_minus) / (2 * eps)
                        
                        # Γ^ρ_μν = (1/2) g^ρσ (∂_μ g_νσ + ∂_ν g_μσ - ∂_σ g_μν)
                        gamma[rho, mu, nu] += 0.5 * g_inv[rho, sigma] * (
                            dg[nu, sigma] + dg[mu, sigma] - dg[mu, nu]
                        )
        
        return gamma


# =============================================================================
# KURUKSHETRA MANIFOLD
# =============================================================================

@dataclass
class ConstraintViolation:
    """
    V_F: M_F → R - Constraint violation potential.
    
    Measures how strongly constraints are violated at state.
    """
    
    constraints: List[Callable[[np.ndarray], float]] = field(default_factory=list)
    weights: List[float] = field(default_factory=list)
    
    def add_constraint(self, constraint: Callable[[np.ndarray], float], 
                       weight: float = 1.0) -> None:
        """Add a constraint function. Returns > 0 when violated."""
        self.constraints.append(constraint)
        self.weights.append(weight)
    
    def __call__(self, state: np.ndarray) -> float:
        """Compute total violation potential."""
        if not self.constraints:
            return 0.0
        
        total = 0.0
        for c, w in zip(self.constraints, self.weights):
            violation = max(0.0, c(state))  # Only positive violations count
            total += w * violation ** 2
        
        return total
    
    def gradient(self, state: np.ndarray, eps: float = 1e-6) -> np.ndarray:
        """Compute gradient of violation potential."""
        grad = np.zeros(len(state))
        
        for i in range(len(state)):
            e_i = np.zeros(len(state))
            e_i[i] = eps
            grad[i] = (self(state + e_i) - self(state - e_i)) / (2 * eps)
        
        return grad


@dataclass
class Kurukshetra:
    """
    K_F: The Battlefield Manifold.
    
    The region where constraint violation is high and
    action selection becomes critical.
    
    K_F(λ) := {m ∈ M_F : V_F(m) ≥ λ}
    """
    
    violation: ConstraintViolation = field(default_factory=ConstraintViolation)
    metric: MoralMetric = field(default_factory=MoralMetric)
    
    # Threshold for battlefield entry
    lambda_threshold: float = 0.1
    
    def in_battlefield(self, state: np.ndarray) -> bool:
        """Check if state is in Kurukshetra (high violation region)."""
        return self.violation(state) >= self.lambda_threshold
    
    def violation_level(self, state: np.ndarray) -> float:
        """Get violation level at state."""
        return self.violation(state)
    
    def gradient_pressure(self, state: np.ndarray) -> float:
        """
        Compute ||∇V_F||_moral.
        
        The pressure to reduce violation.
        """
        grad = self.violation.gradient(state)
        return self.metric.norm(state, grad)
    
    def moral_curvature(self, state: np.ndarray) -> float:
        """
        Estimate local moral curvature (scalar).
        
        Higher curvature = sharper constraints.
        """
        # Use trace of metric tensor as proxy
        g = self.metric.tensor(state)
        return float(np.trace(g))


# =============================================================================
# WILL VECTOR
# =============================================================================

@dataclass
class WillVector:
    """
    W(m): The Will Vector - best descent direction.
    
    W(m) := argmin_{u ∈ U} ⟨∇Φ(m), u⟩_moral
    subject to ||u||_moral ≤ ρ(m)
    
    Where U is the set of feasible directions.
    """
    
    metric: MoralMetric = field(default_factory=MoralMetric)
    step_budget: float = 1.0  # ρ(m) - maximum step size
    
    def compute(self, state: np.ndarray, 
                objective_gradient: np.ndarray,
                feasible_directions: Optional[List[np.ndarray]] = None) -> np.ndarray:
        """
        Compute will vector at state.
        
        Args:
            state: Current state m
            objective_gradient: ∇Φ(m)
            feasible_directions: U ⊂ T_m M_F (None = all directions)
        
        Returns:
            Will vector W(m)
        """
        g = self.metric.tensor(state)
        g_inv = self.metric.inverse(state)
        
        if feasible_directions is None:
            # Unconstrained: W = -ρ * ∇Φ / ||∇Φ||_moral
            grad_norm = self.metric.norm(state, objective_gradient)
            
            if grad_norm < 1e-10:
                return np.zeros_like(state)
            
            # Natural gradient direction
            natural_grad = g_inv @ objective_gradient
            natural_norm = self.metric.norm(state, natural_grad)
            
            if natural_norm < 1e-10:
                return np.zeros_like(state)
            
            return -self.step_budget * natural_grad / natural_norm
        
        else:
            # Constrained: find best feasible direction
            best_direction = np.zeros_like(state)
            best_descent = 0.0
            
            for u in feasible_directions:
                # Normalize to budget
                u_norm = self.metric.norm(state, u)
                if u_norm < 1e-10:
                    continue
                
                u_normalized = u * self.step_budget / u_norm
                
                # Compute descent
                descent = -self.metric.inner_product(state, objective_gradient, u_normalized)
                
                if descent > best_descent:
                    best_descent = descent
                    best_direction = u_normalized
            
            return best_direction
    
    def is_collapsed(self, state: np.ndarray,
                     objective_gradient: np.ndarray,
                     feasible_directions: Optional[List[np.ndarray]] = None,
                     threshold: float = 1e-6) -> bool:
        """
        Check for will vector collapse.
        
        Collapse: W(m) = 0 while ||∇Φ||_moral > 0
        
        This is the geometric form of deadlock.
        """
        grad_norm = self.metric.norm(state, objective_gradient)
        
        if grad_norm < threshold:
            return False  # No gradient pressure, not collapse
        
        will = self.compute(state, objective_gradient, feasible_directions)
        will_norm = self.metric.norm(state, will)
        
        return will_norm < threshold
    
    def descent_rate(self, state: np.ndarray,
                     objective_gradient: np.ndarray,
                     feasible_directions: Optional[List[np.ndarray]] = None) -> float:
        """
        Compute expected descent rate ⟨∇Φ, W⟩_moral.
        
        Negative = descent, Zero = collapse, Positive = impossible (bug)
        """
        will = self.compute(state, objective_gradient, feasible_directions)
        return self.metric.inner_product(state, objective_gradient, will)


# =============================================================================
# STRESS-ENERGY TENSOR
# =============================================================================

@dataclass 
class StressEnergy:
    """
    T_μν: Stress-Energy Tensor (Density of Adharma)
    
    Couples runtime "matter" (constraint violation, cost flux,
    action-induced forcing) to moral geometry.
    """
    
    dim: int = 4
    
    def compute(self, state: np.ndarray,
                violation: float,
                flux: np.ndarray,
                action_force: np.ndarray) -> np.ndarray:
        """
        Compute stress-energy tensor at state.
        
        T_μν = ρ u_μ u_ν + p (g_μν + u_μ u_ν) + π_μν
        
        Where:
        - ρ: violation density
        - u: flow vector
        - p: constraint pressure
        - π: shear from action forcing
        """
        # Energy density (violation)
        rho = violation
        
        # Flow direction (normalized flux)
        flux_norm = np.linalg.norm(flux) + 1e-10
        u = flux / flux_norm
        
        # Pressure (isotropic)
        p = violation * 0.3  # Equation of state
        
        # Construct tensor
        T = np.zeros((self.dim, self.dim))
        
        for mu in range(self.dim):
            for nu in range(self.dim):
                # Perfect fluid part
                T[mu, nu] = rho * u[mu] * u[nu]
                if mu == nu:
                    T[mu, nu] += p
                T[mu, nu] += p * u[mu] * u[nu]
                
                # Shear from action
                T[mu, nu] += 0.5 * (action_force[mu] * u[nu] + 
                                    action_force[nu] * u[mu])
        
        return T
    
    def trace(self, T: np.ndarray, metric_inv: np.ndarray) -> float:
        """Compute trace T = g^μν T_μν."""
        return float(np.sum(metric_inv * T))
    
    def energy_density(self, T: np.ndarray) -> float:
        """Extract energy density T_00."""
        return float(T[0, 0])


# =============================================================================
# VALIDATION
# =============================================================================

def validate_moral_geometry() -> bool:
    """Validate moral geometry module."""
    
    # Test MoralPotential
    potential = MoralPotential(dim=4)
    state = np.array([0.1, 0.2, 0.0, 0.0])
    
    assert potential(np.zeros(4)) == 0.0  # Equilibrium
    assert potential(state) > 0.0  # Deviation
    
    grad = potential.gradient(state)
    assert grad.shape == (4,)
    
    hess = potential.hessian(state)
    assert hess.shape == (4, 4)
    
    # Test MoralMetric
    metric = MoralMetric(dim=4, potential=potential)
    
    g = metric.tensor(state)
    assert g.shape == (4, 4)
    assert np.allclose(g, g.T)  # Symmetric
    
    v = np.array([1.0, 0.0, 0.0, 0.0])
    norm = metric.norm(state, v)
    assert norm > 0
    
    # Test distance
    m0 = np.zeros(4)
    m1 = np.array([1.0, 0.0, 0.0, 0.0])
    d = metric.distance(m0, m1)
    assert d > 0
    
    # Test ConstraintViolation
    violation = ConstraintViolation()
    violation.add_constraint(lambda s: s[0] - 0.5)  # s[0] <= 0.5
    
    low_state = np.array([0.3, 0.0, 0.0, 0.0])
    high_state = np.array([0.7, 0.0, 0.0, 0.0])
    
    assert violation(low_state) == 0.0  # Not violated
    assert violation(high_state) > 0.0  # Violated
    
    # Test Kurukshetra
    kuru = Kurukshetra(violation=violation, metric=metric)
    
    assert not kuru.in_battlefield(low_state)
    assert kuru.in_battlefield(high_state)
    
    # Test WillVector
    will = WillVector(metric=metric)
    
    obj_grad = np.array([1.0, 0.0, 0.0, 0.0])
    w = will.compute(state, obj_grad)
    assert w.shape == (4,)
    assert w[0] < 0  # Should point opposite to gradient
    
    # Test collapse detection
    is_collapsed = will.is_collapsed(state, obj_grad)
    assert not is_collapsed  # Should have valid descent
    
    # Test with blocked direction (simulate collapse)
    blocked = [np.array([0.0, 1.0, 0.0, 0.0]),  # Orthogonal to gradient
               np.array([0.0, 0.0, 1.0, 0.0])]
    is_collapsed = will.is_collapsed(state, obj_grad, blocked, threshold=0.01)
    # May or may not collapse depending on metric
    
    # Test StressEnergy
    T_tensor = StressEnergy(dim=4)
    flux = np.array([0.1, 0.0, 0.0, 0.0])
    force = np.array([0.0, 0.1, 0.0, 0.0])
    
    T = T_tensor.compute(state, violation=0.5, flux=flux, action_force=force)
    assert T.shape == (4, 4)
    
    return True


if __name__ == "__main__":
    print("Validating Moral Geometry...")
    assert validate_moral_geometry()
    print("✓ Moral geometry module validated")
