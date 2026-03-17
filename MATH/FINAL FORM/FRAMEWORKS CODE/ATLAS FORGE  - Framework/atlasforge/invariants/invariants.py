"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Invariant Conservation (κ)                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

κ-Invariants: Quantities preserved across transformations.

Types of Invariants:
- Mass/Probability: Σ ρ = 1 (Markov, Fokker-Planck)
- Energy: H(x,p) = const (Hamiltonian flow)
- Momentum: p = const (translation symmetry)
- Information: I(X;Y) (channel capacity)
- Topology: Betti numbers, homology classes

Conservation Laws:
- Noether's theorem: symmetry ↔ conservation
- Continuity equation: ∂ρ/∂t + ∇·J = 0
- Lyapunov functions: V decreasing along trajectories

For hybrid operators:
- Each pole may preserve different invariants
- Splitting must be designed to preserve shared invariants
- Commutators can violate conservation → splitting error

κ-Structure:
    κ = (κ₁, κ₂, ..., κₙ) ∈ ℝⁿ
    
satisfies:
    d/dt κ(u(t)) = 0  along trajectories
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


class InvariantType(Enum):
    """Types of invariants."""
    MASS = "mass"                   # Total mass/probability
    ENERGY = "energy"               # Total energy
    MOMENTUM = "momentum"           # Linear momentum
    ANGULAR_MOMENTUM = "angular"    # Angular momentum
    CHARGE = "charge"               # Conserved charge
    ENTROPY = "entropy"             # Entropy (non-decreasing)
    LYAPUNOV = "lyapunov"           # Lyapunov function
    TOPOLOGICAL = "topological"     # Topological invariant
    SYMPLECTIC = "symplectic"       # Symplectic structure
    CUSTOM = "custom"               # User-defined


@dataclass
class Invariant:
    """
    A conserved quantity or invariant.
    """
    name: str
    invariant_type: InvariantType
    compute: Callable[[NDArray], float]  # κ(x) → ℝ
    tolerance: float = 1e-10             # Tolerance for conservation check
    is_exact: bool = True                # Exactly or approximately conserved
    
    def evaluate(self, state: NDArray) -> float:
        """Compute invariant value at state."""
        return self.compute(state)
    
    def is_conserved(
        self,
        state_before: NDArray,
        state_after: NDArray,
    ) -> bool:
        """Check if invariant is conserved."""
        before = self.evaluate(state_before)
        after = self.evaluate(state_after)
        return abs(after - before) < self.tolerance
    
    def conservation_error(
        self,
        state_before: NDArray,
        state_after: NDArray,
    ) -> float:
        """Compute conservation error."""
        before = self.evaluate(state_before)
        after = self.evaluate(state_after)
        return abs(after - before)


@dataclass
class InvariantBundle:
    """
    Collection of invariants (κ-structure).
    
    κ = (κ₁, κ₂, ..., κₙ)
    """
    invariants: List[Invariant] = field(default_factory=list)
    
    def add(self, invariant: Invariant):
        self.invariants.append(invariant)
    
    def evaluate_all(self, state: NDArray) -> Dict[str, float]:
        """Evaluate all invariants."""
        return {inv.name: inv.evaluate(state) for inv in self.invariants}
    
    def to_vector(self, state: NDArray) -> NDArray:
        """Return κ as vector."""
        return np.array([inv.evaluate(state) for inv in self.invariants])
    
    def all_conserved(
        self,
        state_before: NDArray,
        state_after: NDArray,
    ) -> bool:
        """Check if all invariants are conserved."""
        return all(
            inv.is_conserved(state_before, state_after)
            for inv in self.invariants
        )
    
    def conservation_report(
        self,
        state_before: NDArray,
        state_after: NDArray,
    ) -> Dict[str, Dict[str, float]]:
        """Detailed conservation report."""
        report = {}
        for inv in self.invariants:
            before = inv.evaluate(state_before)
            after = inv.evaluate(state_after)
            report[inv.name] = {
                'before': before,
                'after': after,
                'error': abs(after - before),
                'conserved': inv.is_conserved(state_before, state_after),
            }
        return report


class ConservationChecker:
    """
    Check conservation along trajectories.
    """
    
    def __init__(self, invariant_bundle: InvariantBundle):
        self.bundle = invariant_bundle
    
    def check_trajectory(
        self,
        trajectory: List[NDArray],
    ) -> Dict[str, List[float]]:
        """Check conservation along a trajectory."""
        values = {inv.name: [] for inv in self.bundle.invariants}
        
        for state in trajectory:
            for inv in self.bundle.invariants:
                values[inv.name].append(inv.evaluate(state))
        
        return values
    
    def drift_analysis(
        self,
        trajectory: List[NDArray],
    ) -> Dict[str, Dict[str, float]]:
        """Analyze drift in invariants."""
        values = self.check_trajectory(trajectory)
        
        analysis = {}
        for name, vals in values.items():
            vals = np.array(vals)
            analysis[name] = {
                'initial': vals[0],
                'final': vals[-1],
                'max': np.max(vals),
                'min': np.min(vals),
                'mean': np.mean(vals),
                'std': np.std(vals),
                'total_drift': vals[-1] - vals[0],
            }
        
        return analysis


# Common invariants
def mass_invariant(tolerance: float = 1e-12) -> Invariant:
    """Total mass/probability invariant."""
    return Invariant(
        name="mass",
        invariant_type=InvariantType.MASS,
        compute=lambda x: np.sum(x),
        tolerance=tolerance,
    )


def l2_norm_invariant(tolerance: float = 1e-12) -> Invariant:
    """L2 norm invariant."""
    return Invariant(
        name="L2_norm",
        invariant_type=InvariantType.ENERGY,
        compute=lambda x: np.linalg.norm(x),
        tolerance=tolerance,
    )


def quadratic_energy(A: NDArray, tolerance: float = 1e-12) -> Invariant:
    """Quadratic energy (1/2)x^T A x."""
    return Invariant(
        name="quadratic_energy",
        invariant_type=InvariantType.ENERGY,
        compute=lambda x: 0.5 * x @ A @ x,
        tolerance=tolerance,
    )


def hamiltonian_invariant(
    H: Callable[[NDArray], float],
    tolerance: float = 1e-10,
) -> Invariant:
    """Hamiltonian energy invariant."""
    return Invariant(
        name="hamiltonian",
        invariant_type=InvariantType.ENERGY,
        compute=H,
        tolerance=tolerance,
    )


def momentum_invariant(
    dimension: int,
    tolerance: float = 1e-12,
) -> Invariant:
    """Linear momentum (assumes state = [x, p])."""
    def compute_momentum(state: NDArray) -> float:
        # Assume second half of state is momentum
        n = len(state)
        return np.sum(state[n//2:])
    
    return Invariant(
        name="momentum",
        invariant_type=InvariantType.MOMENTUM,
        compute=compute_momentum,
        tolerance=tolerance,
    )


def symplectic_form(tolerance: float = 1e-10) -> Invariant:
    """Symplectic 2-form (area in phase space)."""
    def compute_symplectic(state: NDArray) -> float:
        n = len(state)
        if n % 2 != 0:
            return 0.0
        # Symplectic form: sum of x_i p_i
        return np.sum(state[:n//2] * state[n//2:])
    
    return Invariant(
        name="symplectic_area",
        invariant_type=InvariantType.SYMPLECTIC,
        compute=compute_symplectic,
        tolerance=tolerance,
    )


@dataclass
class LyapunovFunction:
    """
    Lyapunov function: decreases along trajectories.
    
    dV/dt ≤ 0 along solutions.
    """
    name: str
    V: Callable[[NDArray], float]           # V(x) → ℝ
    dVdt: Optional[Callable] = None          # dV/dt if known analytically
    
    def evaluate(self, state: NDArray) -> float:
        return self.V(state)
    
    def is_decreasing(
        self,
        state_before: NDArray,
        state_after: NDArray,
        tolerance: float = 1e-10,
    ) -> bool:
        """Check if V is decreasing."""
        V_before = self.evaluate(state_before)
        V_after = self.evaluate(state_after)
        return V_after <= V_before + tolerance
    
    def decay_rate(
        self,
        trajectory: List[NDArray],
    ) -> float:
        """Estimate decay rate from trajectory."""
        if len(trajectory) < 2:
            return 0.0
        
        V_values = [self.evaluate(x) for x in trajectory]
        
        # Fit exponential decay: V(t) ~ V(0) exp(-λt)
        log_V = np.log(np.maximum(V_values, 1e-15))
        t = np.arange(len(V_values))
        
        # Linear regression
        if np.std(log_V) < 1e-10:
            return 0.0
        
        slope, _ = np.polyfit(t, log_V, 1)
        return -slope


class EntropyFunctional:
    """
    Entropy functional for stochastic systems.
    
    H[ρ] = -∫ ρ log ρ dx
    
    For discrete: H[p] = -Σ p_i log p_i
    """
    
    @staticmethod
    def discrete_entropy(p: NDArray) -> float:
        """Discrete Shannon entropy."""
        # Filter out zeros and negatives
        p_pos = p[p > 1e-15]
        return -np.sum(p_pos * np.log(p_pos))
    
    @staticmethod
    def relative_entropy(p: NDArray, q: NDArray) -> float:
        """KL divergence D(p || q) = Σ p log(p/q)."""
        mask = (p > 1e-15) & (q > 1e-15)
        return np.sum(p[mask] * np.log(p[mask] / q[mask]))
    
    @staticmethod
    def free_energy(p: NDArray, E: NDArray, temperature: float = 1.0) -> float:
        """Free energy F = <E> - T H."""
        entropy = EntropyFunctional.discrete_entropy(p)
        energy = np.sum(p * E)
        return energy - temperature * entropy


class SymplecticStructure:
    """
    Symplectic structure for Hamiltonian systems.
    
    ω = Σ dq_i ∧ dp_i
    
    Preserved by Hamiltonian flow.
    """
    
    def __init__(self, dimension: int):
        """Dimension is number of (q, p) pairs."""
        self.dimension = dimension
        self._build_J()
    
    def _build_J(self):
        """Build canonical symplectic matrix."""
        n = self.dimension
        self.J = np.zeros((2*n, 2*n))
        self.J[:n, n:] = np.eye(n)
        self.J[n:, :n] = -np.eye(n)
    
    def omega(self, u: NDArray, v: NDArray) -> float:
        """Compute ω(u, v) = u^T J v."""
        return u @ self.J @ v
    
    def is_symplectic(self, M: NDArray, tolerance: float = 1e-10) -> bool:
        """Check if matrix M is symplectic: M^T J M = J."""
        check = M.T @ self.J @ M
        return np.allclose(check, self.J, atol=tolerance)
    
    def hamiltonian_vector_field(
        self,
        H: Callable[[NDArray], float],
        x: NDArray,
        eps: float = 1e-7,
    ) -> NDArray:
        """Compute X_H = J ∇H."""
        grad = np.zeros(2 * self.dimension)
        for i in range(len(grad)):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad[i] = (H(x_plus) - H(x_minus)) / (2 * eps)
        
        return self.J @ grad


@dataclass
class ConservationLaw:
    """
    Conservation law: ∂ρ/∂t + ∇·J = 0
    
    Links density evolution to flux.
    """
    density_name: str
    flux_name: str
    
    def check_conservation(
        self,
        density_before: NDArray,
        density_after: NDArray,
        flux: NDArray,
        dt: float,
        dx: float,
    ) -> float:
        """Check conservation law numerically."""
        # ∂ρ/∂t ≈ (ρ_after - ρ_before) / dt
        drho_dt = (density_after - density_before) / dt
        
        # ∇·J ≈ central difference
        n = len(flux)
        div_J = np.zeros(n)
        for i in range(1, n-1):
            div_J[i] = (flux[i+1] - flux[i-1]) / (2 * dx)
        
        # Conservation error
        error = drho_dt + div_J
        return np.linalg.norm(error)


# Invariant-preserving operators
class InvariantPreservingOperator:
    """
    Operator that exactly preserves given invariants.
    """
    
    def __init__(
        self,
        base_operator: Callable[[NDArray, float], NDArray],
        invariants: InvariantBundle,
    ):
        self.base_op = base_operator
        self.invariants = invariants
    
    def apply(
        self,
        state: NDArray,
        dt: float,
    ) -> NDArray:
        """Apply operator with projection to preserve invariants."""
        # Apply base operator
        new_state = self.base_op(state, dt)
        
        # Check conservation
        if not self.invariants.all_conserved(state, new_state):
            # Project back onto invariant manifold
            new_state = self._project(state, new_state)
        
        return new_state
    
    def _project(
        self,
        old_state: NDArray,
        new_state: NDArray,
    ) -> NDArray:
        """Project new state to preserve invariants of old state."""
        projected = new_state.copy()
        
        for inv in self.invariants.invariants:
            if inv.invariant_type == InvariantType.MASS:
                # Scale to preserve mass
                old_mass = inv.evaluate(old_state)
                new_mass = inv.evaluate(projected)
                if new_mass > 1e-15:
                    projected = projected * (old_mass / new_mass)
            
            elif inv.invariant_type == InvariantType.ENERGY:
                # Normalize to preserve energy (for quadratic)
                old_E = inv.evaluate(old_state)
                new_E = inv.evaluate(projected)
                if new_E > 1e-15:
                    projected = projected * np.sqrt(old_E / new_E)
        
        return projected


# Create standard invariant bundles
def hamiltonian_invariants(
    H: Callable[[NDArray], float],
    dimension: int,
) -> InvariantBundle:
    """Standard invariants for Hamiltonian systems."""
    bundle = InvariantBundle()
    bundle.add(hamiltonian_invariant(H))
    bundle.add(symplectic_form())
    return bundle


def probability_invariants() -> InvariantBundle:
    """Invariants for probability distributions."""
    bundle = InvariantBundle()
    bundle.add(mass_invariant())
    return bundle
