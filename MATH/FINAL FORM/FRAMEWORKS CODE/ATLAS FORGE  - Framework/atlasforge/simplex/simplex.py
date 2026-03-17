"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Operator Simplex & Splitting                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

The Operator Simplex: 4-Pole Space of Hybrid Generators

The generator G lives in span{D, Ω, Σ, Ψ}:

    G = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ

where (α_D, α_Ω, α_Σ, α_Ψ) ∈ Δ³ (the 3-simplex).

Canonical Faces:
- Vertices: Pure poles (D, Ω, Σ, Ψ)
- Edges: 2-pole hybrids (D+Ω, D+Σ, D+Ψ, Ω+Σ, Ω+Ψ, Σ+Ψ)
- Faces: 3-pole hybrids
- Interior: Full 4-pole hybrids

Splitting Schemes:
- Lie-Trotter: e^{τ(A+B)} ≈ e^{τA}e^{τB} (first-order)
- Strang: e^{τ(A+B)} ≈ e^{(τ/2)A}e^{τB}e^{(τ/2)A} (second-order)
- Yoshida: Higher-order symmetric splittings

Error is controlled by commutator [A, B] = AB - BA.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


class PoleType(Enum):
    """The four canonical poles."""
    D = "D"         # Discrete/Dissipative (Earth)
    OMEGA = "Ω"     # Oscillatory/Continuous (Water)
    SIGMA = "Σ"     # Stochastic (Fire)
    PSI = "Ψ"       # Recursive/Hierarchical (Air)


@dataclass(frozen=True)
class SimplexPoint:
    """
    A point in the operator simplex Δ³.
    
    Represents weights (α_D, α_Ω, α_Σ, α_Ψ) with Σα = 1.
    """
    alpha_D: float = 0.25
    alpha_Omega: float = 0.25
    alpha_Sigma: float = 0.25
    alpha_Psi: float = 0.25
    
    def __post_init__(self):
        # Normalize
        total = self.alpha_D + self.alpha_Omega + self.alpha_Sigma + self.alpha_Psi
        if abs(total - 1.0) > 1e-10:
            object.__setattr__(self, 'alpha_D', self.alpha_D / total)
            object.__setattr__(self, 'alpha_Omega', self.alpha_Omega / total)
            object.__setattr__(self, 'alpha_Sigma', self.alpha_Sigma / total)
            object.__setattr__(self, 'alpha_Psi', self.alpha_Psi / total)
    
    @property
    def weights(self) -> Tuple[float, float, float, float]:
        return (self.alpha_D, self.alpha_Omega, self.alpha_Sigma, self.alpha_Psi)
    
    @property
    def active_poles(self) -> List[PoleType]:
        """Poles with non-negligible weight."""
        poles = []
        if self.alpha_D > 1e-6:
            poles.append(PoleType.D)
        if self.alpha_Omega > 1e-6:
            poles.append(PoleType.OMEGA)
        if self.alpha_Sigma > 1e-6:
            poles.append(PoleType.SIGMA)
        if self.alpha_Psi > 1e-6:
            poles.append(PoleType.PSI)
        return poles
    
    @property
    def n_active_poles(self) -> int:
        return len(self.active_poles)
    
    @property
    def dominant_pole(self) -> PoleType:
        """Pole with highest weight."""
        weights = {
            PoleType.D: self.alpha_D,
            PoleType.OMEGA: self.alpha_Omega,
            PoleType.SIGMA: self.alpha_Sigma,
            PoleType.PSI: self.alpha_Psi,
        }
        return max(weights, key=weights.get)
    
    def to_barycentric(self) -> NDArray[np.float64]:
        """Convert to barycentric coordinates."""
        return np.array([self.alpha_D, self.alpha_Omega, 
                        self.alpha_Sigma, self.alpha_Psi])
    
    @classmethod
    def from_barycentric(cls, coords: NDArray) -> 'SimplexPoint':
        """Create from barycentric coordinates."""
        return cls(coords[0], coords[1], coords[2], coords[3])
    
    # Canonical points
    @classmethod
    def pure_D(cls) -> 'SimplexPoint':
        return cls(1, 0, 0, 0)
    
    @classmethod
    def pure_Omega(cls) -> 'SimplexPoint':
        return cls(0, 1, 0, 0)
    
    @classmethod
    def pure_Sigma(cls) -> 'SimplexPoint':
        return cls(0, 0, 1, 0)
    
    @classmethod
    def pure_Psi(cls) -> 'SimplexPoint':
        return cls(0, 0, 0, 1)
    
    @classmethod
    def center(cls) -> 'SimplexPoint':
        return cls(0.25, 0.25, 0.25, 0.25)
    
    @classmethod
    def edge_D_Omega(cls, t: float = 0.5) -> 'SimplexPoint':
        """Point on D-Ω edge (horizontal hybrid)."""
        return cls(1-t, t, 0, 0)
    
    @classmethod
    def edge_Sigma_Psi(cls, t: float = 0.5) -> 'SimplexPoint':
        """Point on Σ-Ψ edge (vertical hybrid)."""
        return cls(0, 0, 1-t, t)
    
    def interpolate(self, other: 'SimplexPoint', t: float) -> 'SimplexPoint':
        """Linear interpolation in simplex."""
        return SimplexPoint(
            (1-t) * self.alpha_D + t * other.alpha_D,
            (1-t) * self.alpha_Omega + t * other.alpha_Omega,
            (1-t) * self.alpha_Sigma + t * other.alpha_Sigma,
            (1-t) * self.alpha_Psi + t * other.alpha_Psi,
        )


class PoleOperator(ABC):
    """Abstract base class for pole operators."""
    
    @property
    @abstractmethod
    def pole_type(self) -> PoleType:
        pass
    
    @abstractmethod
    def apply(self, state: NDArray, dt: float = 1.0) -> NDArray:
        """Apply operator for time dt."""
        pass
    
    @abstractmethod
    def generator(self, state: NDArray) -> NDArray:
        """Return Gx for generator G at state x."""
        pass


class DissipativeOperator(PoleOperator):
    """
    D-pole: Discrete/Dissipative operator.
    
    Gradient descent, projection, local search.
    """
    
    def __init__(
        self,
        gradient: Optional[Callable[[NDArray], NDArray]] = None,
        matrix: Optional[NDArray] = None,
    ):
        self._gradient = gradient
        self._matrix = matrix
    
    @property
    def pole_type(self) -> PoleType:
        return PoleType.D
    
    def apply(self, state: NDArray, dt: float = 1.0) -> NDArray:
        if self._gradient is not None:
            # Gradient step
            return state - dt * self._gradient(state)
        elif self._matrix is not None:
            # Matrix exponential (approximated)
            return state + dt * self._matrix @ state
        return state
    
    def generator(self, state: NDArray) -> NDArray:
        if self._gradient is not None:
            return -self._gradient(state)
        elif self._matrix is not None:
            return self._matrix @ state
        return np.zeros_like(state)


class OscillatoryOperator(PoleOperator):
    """
    Ω-pole: Oscillatory/Hamiltonian operator.
    
    Symplectic, volume-preserving, wave-like dynamics.
    """
    
    def __init__(
        self,
        hamiltonian: Optional[Callable[[NDArray], float]] = None,
        J_matrix: Optional[NDArray] = None,  # Symplectic structure
    ):
        self._hamiltonian = hamiltonian
        self._J = J_matrix
    
    @property
    def pole_type(self) -> PoleType:
        return PoleType.OMEGA
    
    def apply(self, state: NDArray, dt: float = 1.0) -> NDArray:
        if self._hamiltonian is not None and self._J is not None:
            # Symplectic Euler
            grad_H = self._numerical_gradient(self._hamiltonian, state)
            return state + dt * self._J @ grad_H
        return state
    
    def generator(self, state: NDArray) -> NDArray:
        if self._hamiltonian is not None and self._J is not None:
            grad_H = self._numerical_gradient(self._hamiltonian, state)
            return self._J @ grad_H
        return np.zeros_like(state)
    
    def _numerical_gradient(self, f: Callable, x: NDArray, eps: float = 1e-7) -> NDArray:
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus, x_minus = x.copy(), x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        return grad


class StochasticOperator(PoleOperator):
    """
    Σ-pole: Stochastic operator.
    
    Random perturbations, diffusion, noise injection.
    """
    
    def __init__(
        self,
        noise_scale: float = 1.0,
        diffusion_matrix: Optional[NDArray] = None,
        seed: Optional[int] = None,
    ):
        self.noise_scale = noise_scale
        self._diffusion = diffusion_matrix
        self._rng = np.random.default_rng(seed)
    
    @property
    def pole_type(self) -> PoleType:
        return PoleType.SIGMA
    
    def apply(self, state: NDArray, dt: float = 1.0) -> NDArray:
        d = len(state)
        if self._diffusion is not None:
            # Colored noise
            noise = self._rng.standard_normal(d)
            return state + np.sqrt(dt) * self.noise_scale * self._diffusion @ noise
        else:
            # White noise
            return state + np.sqrt(dt) * self.noise_scale * self._rng.standard_normal(d)
    
    def generator(self, state: NDArray) -> NDArray:
        # Stochastic generator is the diffusion coefficient
        # For Fokker-Planck, this would be the Laplacian term
        return np.zeros_like(state)  # Mean zero drift


class RecursiveOperator(PoleOperator):
    """
    Ψ-pole: Recursive/Hierarchical operator.
    
    Multigrid, renormalization, coarse-graining.
    """
    
    def __init__(
        self,
        restriction: Optional[Callable[[NDArray], NDArray]] = None,
        prolongation: Optional[Callable[[NDArray], NDArray]] = None,
        coarse_solver: Optional[Callable[[NDArray], NDArray]] = None,
    ):
        self._restrict = restriction
        self._prolong = prolongation
        self._coarse_solve = coarse_solver
    
    @property
    def pole_type(self) -> PoleType:
        return PoleType.PSI
    
    def apply(self, state: NDArray, dt: float = 1.0) -> NDArray:
        if self._restrict and self._prolong and self._coarse_solve:
            # V-cycle style: restrict, solve coarse, prolong
            coarse = self._restrict(state)
            coarse_solution = self._coarse_solve(coarse)
            correction = self._prolong(coarse_solution)
            return state + dt * correction
        return state
    
    def generator(self, state: NDArray) -> NDArray:
        if self._restrict and self._prolong and self._coarse_solve:
            coarse = self._restrict(state)
            coarse_solution = self._coarse_solve(coarse)
            return self._prolong(coarse_solution)
        return np.zeros_like(state)


@dataclass
class HybridOperator:
    """
    Hybrid operator combining multiple poles.
    
    G = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ
    """
    simplex_point: SimplexPoint
    D_op: Optional[DissipativeOperator] = None
    Omega_op: Optional[OscillatoryOperator] = None
    Sigma_op: Optional[StochasticOperator] = None
    Psi_op: Optional[RecursiveOperator] = None
    
    def apply(self, state: NDArray, dt: float = 1.0) -> NDArray:
        """Apply hybrid operator (additive combination)."""
        result = state.copy()
        
        if self.D_op and self.simplex_point.alpha_D > 1e-10:
            d_contrib = self.D_op.generator(state)
            result = result + dt * self.simplex_point.alpha_D * d_contrib
        
        if self.Omega_op and self.simplex_point.alpha_Omega > 1e-10:
            omega_contrib = self.Omega_op.generator(state)
            result = result + dt * self.simplex_point.alpha_Omega * omega_contrib
        
        if self.Sigma_op and self.simplex_point.alpha_Sigma > 1e-10:
            # Stochastic component scaled by weight
            sigma_result = self.Sigma_op.apply(np.zeros_like(state), dt)
            result = result + self.simplex_point.alpha_Sigma * sigma_result
        
        if self.Psi_op and self.simplex_point.alpha_Psi > 1e-10:
            psi_contrib = self.Psi_op.generator(state)
            result = result + dt * self.simplex_point.alpha_Psi * psi_contrib
        
        return result
    
    def generator(self, state: NDArray) -> NDArray:
        """Return combined generator Gx."""
        result = np.zeros_like(state)
        
        if self.D_op:
            result += self.simplex_point.alpha_D * self.D_op.generator(state)
        if self.Omega_op:
            result += self.simplex_point.alpha_Omega * self.Omega_op.generator(state)
        if self.Psi_op:
            result += self.simplex_point.alpha_Psi * self.Psi_op.generator(state)
        
        return result


class SplittingScheme(Enum):
    """Operator splitting schemes."""
    LIE_TROTTER = "lie_trotter"     # First order: e^{τA}e^{τB}
    STRANG = "strang"                # Second order: e^{τA/2}e^{τB}e^{τA/2}
    YOSHIDA = "yoshida"              # Fourth order
    SYMMETRIC = "symmetric"          # General symmetric


@dataclass
class SplittingIntegrator:
    """
    Splitting integrator for hybrid operators.
    
    For G = A + B, approximate e^{τG} using products of e^{ατA} and e^{βτB}.
    
    Error Analysis:
    - Lie-Trotter: O(τ²[A,B]) per step → O(τ) global
    - Strang: O(τ³[[A,B],A] + τ³[[A,B],B]) → O(τ²) global
    """
    scheme: SplittingScheme = SplittingScheme.STRANG
    
    def integrate(
        self,
        operators: List[PoleOperator],
        state: NDArray,
        dt: float,
        n_steps: int = 1,
    ) -> NDArray:
        """Integrate using splitting scheme."""
        x = state.copy()
        
        for _ in range(n_steps):
            x = self._one_step(operators, x, dt)
        
        return x
    
    def _one_step(
        self,
        operators: List[PoleOperator],
        state: NDArray,
        dt: float,
    ) -> NDArray:
        """Single integration step."""
        if self.scheme == SplittingScheme.LIE_TROTTER:
            return self._lie_trotter(operators, state, dt)
        elif self.scheme == SplittingScheme.STRANG:
            return self._strang(operators, state, dt)
        elif self.scheme == SplittingScheme.YOSHIDA:
            return self._yoshida(operators, state, dt)
        else:
            return self._strang(operators, state, dt)
    
    def _lie_trotter(
        self,
        operators: List[PoleOperator],
        state: NDArray,
        dt: float,
    ) -> NDArray:
        """Lie-Trotter splitting: e^{τA}e^{τB}..."""
        x = state.copy()
        for op in operators:
            x = op.apply(x, dt)
        return x
    
    def _strang(
        self,
        operators: List[PoleOperator],
        state: NDArray,
        dt: float,
    ) -> NDArray:
        """Strang splitting: e^{τA/2}e^{τB}e^{τA/2}..."""
        if len(operators) < 2:
            return operators[0].apply(state, dt) if operators else state
        
        x = state.copy()
        n = len(operators)
        
        # Forward half-steps
        for i in range(n - 1):
            x = operators[i].apply(x, dt / 2)
        
        # Full step for last operator
        x = operators[-1].apply(x, dt)
        
        # Backward half-steps
        for i in range(n - 2, -1, -1):
            x = operators[i].apply(x, dt / 2)
        
        return x
    
    def _yoshida(
        self,
        operators: List[PoleOperator],
        state: NDArray,
        dt: float,
    ) -> NDArray:
        """Fourth-order Yoshida splitting."""
        # Yoshida coefficients
        w1 = 1.0 / (2 - 2**(1/3))
        w0 = 1 - 2*w1
        
        x = state.copy()
        x = self._strang(operators, x, w1 * dt)
        x = self._strang(operators, x, w0 * dt)
        x = self._strang(operators, x, w1 * dt)
        
        return x


def estimate_commutator_error(
    A: PoleOperator,
    B: PoleOperator,
    state: NDArray,
    dt: float = 0.01,
) -> float:
    """
    Estimate commutator [A, B] = AB - BA at a state.
    
    The commutator controls splitting error.
    """
    # AB - BA via finite differences
    x = state.copy()
    
    # A then B
    x_AB = B.apply(A.apply(x, dt), dt)
    
    # B then A
    x_BA = A.apply(B.apply(x, dt), dt)
    
    return np.linalg.norm(x_AB - x_BA) / (dt**2)


@dataclass
class SimplexTrajectory:
    """
    Trajectory through the operator simplex.
    
    Useful for adaptive algorithms that move through pole space.
    """
    points: List[SimplexPoint] = field(default_factory=list)
    times: List[float] = field(default_factory=list)
    
    def add(self, point: SimplexPoint, t: float):
        self.points.append(point)
        self.times.append(t)
    
    def interpolate(self, t: float) -> SimplexPoint:
        """Get simplex point at time t."""
        if not self.times:
            return SimplexPoint.center()
        
        if t <= self.times[0]:
            return self.points[0]
        if t >= self.times[-1]:
            return self.points[-1]
        
        # Find bracketing indices
        for i in range(len(self.times) - 1):
            if self.times[i] <= t <= self.times[i+1]:
                s = (t - self.times[i]) / (self.times[i+1] - self.times[i])
                return self.points[i].interpolate(self.points[i+1], s)
        
        return self.points[-1]


# Horizontal generator: G_hor = D + Ω
def create_horizontal_generator(
    D_op: DissipativeOperator,
    Omega_op: OscillatoryOperator,
    alpha: float = 0.5,
) -> HybridOperator:
    """
    Create horizontal generator G_hor = αD + (1-α)Ω.
    
    Horizontal hybrids combine discrete structure with continuous flow.
    """
    return HybridOperator(
        simplex_point=SimplexPoint(alpha, 1-alpha, 0, 0),
        D_op=D_op,
        Omega_op=Omega_op,
    )


# Vertical generator: G_vert = Σ + Ψ
def create_vertical_generator(
    Sigma_op: StochasticOperator,
    Psi_op: RecursiveOperator,
    alpha: float = 0.5,
) -> HybridOperator:
    """
    Create vertical generator G_vert = αΣ + (1-α)Ψ.
    
    Vertical hybrids combine stochastic exploration with hierarchical structure.
    """
    return HybridOperator(
        simplex_point=SimplexPoint(0, 0, alpha, 1-alpha),
        Sigma_op=Sigma_op,
        Psi_op=Psi_op,
    )


# Full 4-pole generator
def create_4pole_generator(
    D_op: Optional[DissipativeOperator] = None,
    Omega_op: Optional[OscillatoryOperator] = None,
    Sigma_op: Optional[StochasticOperator] = None,
    Psi_op: Optional[RecursiveOperator] = None,
    weights: Tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25),
) -> HybridOperator:
    """
    Create full 4-pole hybrid generator.
    
    G = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ
    """
    return HybridOperator(
        simplex_point=SimplexPoint(*weights),
        D_op=D_op,
        Omega_op=Omega_op,
        Sigma_op=Sigma_op,
        Psi_op=Psi_op,
    )


# Convenience: run hybrid dynamics
def hybrid_dynamics(
    hybrid_op: HybridOperator,
    x0: NDArray,
    T: float,
    dt: float = 0.01,
    scheme: SplittingScheme = SplittingScheme.STRANG,
) -> Tuple[NDArray, List[NDArray]]:
    """
    Run hybrid dynamics and return final state and trajectory.
    """
    n_steps = int(T / dt)
    trajectory = [x0.copy()]
    
    x = x0.copy()
    for _ in range(n_steps):
        x = hybrid_op.apply(x, dt)
        trajectory.append(x.copy())
    
    return x, trajectory
