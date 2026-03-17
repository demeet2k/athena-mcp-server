"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ATLAS FORGE - Generators                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Mathematical generator operators for hybrid evolution systems.

The four fundamental generator types:
- D (Dissipative): Contractive, smoothing, entropy-decreasing
- Ω (Oscillatory): Phase-preserving, conservative, transport
- Σ (Stochastic): Markovian expansion, mixing, noise injection  
- Ψ (Recursive): Scale transformation, coarse-graining, renormalization

A general hybrid generator is:
    G = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ

The induced flow is:
    U_t = e^{tG}
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Generic, List, Optional, 
    Protocol, Tuple, Type, TypeVar, Union
)
import math
import numpy as np
from numpy.typing import NDArray

from atlasforge.core.enums import Pole, FlowType
from atlasforge.core.types import Interval, Domain
from atlasforge.core.base import AtlasObject, register_type


# Type aliases
State = Union[float, NDArray[np.float64]]
Operator = Callable[[State], State]


class Generator(ABC):
    """
    Abstract base class for evolution generators.
    
    A generator G defines an infinitesimal evolution rule:
        du/dt = G(u)  or  u(t) = e^{tG} u_0
    
    The generator must specify:
    - The pole type (D, Ω, Σ, Ψ)
    - The action on states
    - Spectral properties
    - Invariants preserved/destroyed
    """
    
    @property
    @abstractmethod
    def pole(self) -> Pole:
        """The pole type of this generator."""
        pass
    
    @property
    @abstractmethod
    def symbol(self) -> str:
        """Symbolic representation."""
        pass
    
    @abstractmethod
    def __call__(self, u: State) -> State:
        """Apply generator to state: G(u)."""
        pass
    
    @abstractmethod
    def apply(self, u: State) -> State:
        """Apply generator to state (alias for __call__)."""
        pass
    
    def exp(self, t: float, u: State) -> State:
        """
        Apply exponential flow: e^{tG} u.
        
        Default implementation uses matrix exponential for linear operators
        or numerical integration for nonlinear.
        """
        # Default: Euler approximation for small t
        dt = 0.01
        steps = max(1, int(abs(t) / dt))
        dt = t / steps
        
        result = u
        for _ in range(steps):
            result = result + dt * self.apply(result)
        return result
    
    @property
    def is_linear(self) -> bool:
        """Whether this generator is linear."""
        return False
    
    @property
    def is_bounded(self) -> bool:
        """Whether this generator is bounded."""
        return False
    
    def __add__(self, other: 'Generator') -> 'HybridGenerator':
        """Combine generators: G1 + G2."""
        return HybridGenerator.combine(self, other)
    
    def __mul__(self, scalar: float) -> 'ScaledGenerator':
        """Scale generator: α·G."""
        return ScaledGenerator(self, scalar)
    
    def __rmul__(self, scalar: float) -> 'ScaledGenerator':
        return self.__mul__(scalar)
    
    def commutator(self, other: 'Generator', u: State) -> State:
        """
        Compute commutator [G1, G2] at state u.
        
        [G1, G2](u) = G1(G2(u)) - G2(G1(u))
        """
        return self.apply(other.apply(u)) - other.apply(self.apply(u))


@dataclass
class ScaledGenerator(Generator):
    """A generator scaled by a coefficient: α·G."""
    
    base: Generator
    coefficient: float
    
    @property
    def pole(self) -> Pole:
        return self.base.pole
    
    @property
    def symbol(self) -> str:
        return f"{self.coefficient}·{self.base.symbol}"
    
    def __call__(self, u: State) -> State:
        return self.coefficient * self.base(u)
    
    def apply(self, u: State) -> State:
        return self(u)
    
    def exp(self, t: float, u: State) -> State:
        return self.base.exp(t * self.coefficient, u)


@dataclass
class DissipativeGenerator(Generator):
    """
    D (Dissipative) Generator: Contractive, smoothing, entropy-decreasing.
    
    Examples:
    - Laplacian: ∇² (heat equation)
    - Gradient flow: -∇V(u)
    - Damping: -γu
    
    Properties:
    - Spectrum in left half-plane (Re(λ) ≤ 0)
    - Lyapunov function decreases under flow
    - Contracts distances between trajectories
    """
    
    # Dissipation rate (γ)
    rate: float = field(default=1.0)
    
    # Optional potential for gradient flow
    potential: Optional[Callable[[State], float]] = field(default=None)
    
    # Optional Laplacian matrix for discrete Laplacian
    laplacian_matrix: Optional[NDArray[np.float64]] = field(default=None)
    
    @property
    def pole(self) -> Pole:
        return Pole.D
    
    @property
    def symbol(self) -> str:
        return "D"
    
    def __call__(self, u: State) -> State:
        return self.apply(u)
    
    def apply(self, u: State) -> State:
        """
        Apply dissipative generator.
        
        Default: simple damping -γu
        With potential: gradient descent -∇V(u)
        With Laplacian: discrete diffusion L·u
        """
        if self.laplacian_matrix is not None:
            # Discrete Laplacian
            u_arr = np.atleast_1d(u)
            return -self.rate * self.laplacian_matrix @ u_arr
        
        if self.potential is not None:
            # Gradient flow: numerical gradient
            return self._gradient_descent(u)
        
        # Simple damping
        return -self.rate * u
    
    def _gradient_descent(self, u: State) -> State:
        """Compute gradient of potential numerically."""
        eps = 1e-7
        if isinstance(u, (int, float)):
            grad = (self.potential(u + eps) - self.potential(u - eps)) / (2 * eps)
            return -self.rate * grad
        else:
            u_arr = np.atleast_1d(u)
            grad = np.zeros_like(u_arr)
            for i in range(len(u_arr)):
                u_plus = u_arr.copy()
                u_minus = u_arr.copy()
                u_plus[i] += eps
                u_minus[i] -= eps
                grad[i] = (self.potential(u_plus) - self.potential(u_minus)) / (2 * eps)
            return -self.rate * grad
    
    def exp(self, t: float, u: State) -> State:
        """
        Exact exponential for linear dissipation.
        """
        if self.laplacian_matrix is not None:
            # Matrix exponential
            from scipy.linalg import expm
            u_arr = np.atleast_1d(u)
            exp_mat = expm(-self.rate * t * self.laplacian_matrix)
            return exp_mat @ u_arr
        
        if self.potential is None:
            # Simple damping: u(t) = u_0 * e^{-γt}
            return u * math.exp(-self.rate * t)
        
        # Use default numerical integration
        return super().exp(t, u)
    
    @property
    def is_linear(self) -> bool:
        return self.potential is None
    
    def lyapunov(self, u: State) -> float:
        """
        Compute Lyapunov function value.
        
        For gradient flow: V(u)
        For damping: |u|²/2
        """
        if self.potential is not None:
            return self.potential(u)
        
        if isinstance(u, (int, float)):
            return 0.5 * u ** 2
        else:
            return 0.5 * np.sum(u ** 2)


@dataclass
class OscillatoryGenerator(Generator):
    """
    Ω (Oscillatory) Generator: Phase-preserving, conservative, transport.
    
    Examples:
    - Skew-adjoint: iH (Schrödinger)
    - Symplectic: J·∇H (Hamilton)
    - Wave transport: ∂_t u = c·∂_x u
    
    Properties:
    - Spectrum on imaginary axis (Re(λ) = 0)
    - Energy/norm conserved
    - Unitary/symplectic flow
    """
    
    # Frequency (ω)
    frequency: float = field(default=1.0)
    
    # Optional Hamiltonian matrix (skew-symmetric)
    hamiltonian: Optional[NDArray[np.float64]] = field(default=None)
    
    # Phase offset
    phase: float = field(default=0.0)
    
    @property
    def pole(self) -> Pole:
        return Pole.OMEGA
    
    @property
    def symbol(self) -> str:
        return "Ω"
    
    def __call__(self, u: State) -> State:
        return self.apply(u)
    
    def apply(self, u: State) -> State:
        """
        Apply oscillatory generator.
        
        Default: rotation generator -iω (for real: skew rotation)
        With Hamiltonian: H·u
        """
        if self.hamiltonian is not None:
            u_arr = np.atleast_1d(u)
            return self.hamiltonian @ u_arr
        
        # Simple rotation in phase space
        # For scalar: treat as (u, v) pair and rotate
        if isinstance(u, (int, float)):
            # Return derivative of rotation
            return -self.frequency * u * math.sin(self.phase)
        else:
            u_arr = np.atleast_1d(u)
            # Skew rotation: J·u where J is block-diagonal rotation
            n = len(u_arr)
            result = np.zeros_like(u_arr)
            for i in range(0, n - 1, 2):
                result[i] = -self.frequency * u_arr[i + 1]
                result[i + 1] = self.frequency * u_arr[i]
            if n % 2 == 1:
                result[-1] = 0
            return result
    
    def exp(self, t: float, u: State) -> State:
        """
        Exact exponential for linear oscillation.
        """
        if self.hamiltonian is not None:
            from scipy.linalg import expm
            u_arr = np.atleast_1d(u)
            exp_mat = expm(t * self.hamiltonian)
            return exp_mat @ u_arr
        
        # Simple rotation
        if isinstance(u, (int, float)):
            angle = self.frequency * t + self.phase
            return u * math.cos(angle)
        else:
            u_arr = np.atleast_1d(u)
            angle = self.frequency * t
            c, s = math.cos(angle), math.sin(angle)
            n = len(u_arr)
            result = np.zeros_like(u_arr)
            for i in range(0, n - 1, 2):
                result[i] = c * u_arr[i] - s * u_arr[i + 1]
                result[i + 1] = s * u_arr[i] + c * u_arr[i + 1]
            if n % 2 == 1:
                result[-1] = u_arr[-1]
            return result
    
    @property
    def is_linear(self) -> bool:
        return True
    
    def energy(self, u: State) -> float:
        """
        Compute conserved energy (norm squared).
        """
        if isinstance(u, (int, float)):
            return 0.5 * u ** 2
        else:
            return 0.5 * np.sum(u ** 2)


@dataclass
class StochasticGenerator(Generator):
    """
    Σ (Stochastic) Generator: Markovian expansion, mixing, noise injection.
    
    Examples:
    - Diffusion: σ²∇² (Brownian motion generator)
    - Jump process: Q (Markov jump generator)
    - Langevin: -∇V + σ·dW/dt
    
    Properties:
    - Generates ensembles from initial conditions
    - Produces stationary measures
    - Entropy production
    """
    
    # Noise intensity (σ²)
    noise_intensity: float = field(default=1.0)
    
    # Temperature (for thermal fluctuations)
    temperature: float = field(default=1.0)
    
    # Optional Markov transition rate matrix Q
    rate_matrix: Optional[NDArray[np.float64]] = field(default=None)
    
    # Random seed for reproducibility
    seed: Optional[int] = field(default=None)
    
    @property
    def pole(self) -> Pole:
        return Pole.SIGMA
    
    @property
    def symbol(self) -> str:
        return "Σ"
    
    def __call__(self, u: State) -> State:
        return self.apply(u)
    
    def apply(self, u: State) -> State:
        """
        Apply stochastic generator (deterministic part).
        
        Note: Full stochastic evolution requires sampling.
        This returns the drift term.
        """
        if self.rate_matrix is not None:
            u_arr = np.atleast_1d(u)
            return self.rate_matrix @ u_arr
        
        # Diffusion drift (Fokker-Planck style)
        # For scalar: drift toward mean
        if isinstance(u, (int, float)):
            return -u / self.temperature
        else:
            u_arr = np.atleast_1d(u)
            return -u_arr / self.temperature
    
    def exp(self, t: float, u: State) -> State:
        """
        Stochastic evolution with noise.
        
        Uses Euler-Maruyama for SDE integration.
        """
        rng = np.random.default_rng(self.seed)
        
        dt = 0.01
        steps = max(1, int(abs(t) / dt))
        dt = t / steps
        
        if isinstance(u, (int, float)):
            result = float(u)
            for _ in range(steps):
                drift = self.apply(result)
                noise = math.sqrt(2 * self.noise_intensity * dt) * rng.standard_normal()
                result = result + dt * drift + noise
            return result
        else:
            result = np.array(u, dtype=float)
            sqrt_2dt = math.sqrt(2 * self.noise_intensity * dt)
            for _ in range(steps):
                drift = self.apply(result)
                noise = sqrt_2dt * rng.standard_normal(result.shape)
                result = result + dt * drift + noise
            return result
    
    def sample_stationary(self, n_samples: int, initial: State) -> List[State]:
        """
        Sample from the stationary distribution.
        
        Uses MCMC / long-time integration.
        """
        rng = np.random.default_rng(self.seed)
        samples = []
        
        # Burn-in
        state = self.exp(10.0, initial)
        
        # Collect samples
        for _ in range(n_samples):
            state = self.exp(1.0, state)
            samples.append(state)
        
        return samples
    
    def entropy_production(self, u: State, du: State) -> float:
        """
        Compute instantaneous entropy production rate.
        """
        # Simplified: use |du|² / (2T)
        if isinstance(du, (int, float)):
            return du ** 2 / (2 * self.temperature)
        else:
            return np.sum(du ** 2) / (2 * self.temperature)


@dataclass
class RecursiveGenerator(Generator):
    """
    Ψ (Recursive) Generator: Scale transformation, coarse-graining, renormalization.
    
    Examples:
    - Restriction-prolongation: R, P
    - Wavelet decomposition
    - RG transformation: T_b
    
    Properties:
    - Acts across scales
    - Preserves slow/relevant modes
    - Compresses fast/irrelevant modes
    """
    
    # Coarse-graining factor
    scale_factor: float = field(default=2.0)
    
    # Recursion depth limit
    max_depth: int = field(default=10)
    
    # Optional restriction operator (fine → coarse)
    restriction: Optional[NDArray[np.float64]] = field(default=None)
    
    # Optional prolongation operator (coarse → fine)
    prolongation: Optional[NDArray[np.float64]] = field(default=None)
    
    @property
    def pole(self) -> Pole:
        return Pole.PSI
    
    @property
    def symbol(self) -> str:
        return "Ψ"
    
    def __call__(self, u: State) -> State:
        return self.apply(u)
    
    def apply(self, u: State) -> State:
        """
        Apply recursive/scale generator.
        
        Default: coarse-graining by averaging.
        """
        if self.restriction is not None:
            u_arr = np.atleast_1d(u)
            return self.restriction @ u_arr
        
        # Simple coarse-graining: average pairs
        if isinstance(u, (int, float)):
            return u / self.scale_factor
        else:
            u_arr = np.atleast_1d(u)
            n = len(u_arr)
            factor = int(self.scale_factor)
            if n % factor == 0:
                return u_arr.reshape(-1, factor).mean(axis=1)
            else:
                # Pad and average
                padded = np.pad(u_arr, (0, factor - n % factor), mode='edge')
                return padded.reshape(-1, factor).mean(axis=1)
    
    def prolong(self, u_coarse: State) -> State:
        """
        Prolongation: lift from coarse to fine scale.
        """
        if self.prolongation is not None:
            u_arr = np.atleast_1d(u_coarse)
            return self.prolongation @ u_arr
        
        # Simple prolongation: repeat values
        if isinstance(u_coarse, (int, float)):
            return u_coarse * self.scale_factor
        else:
            u_arr = np.atleast_1d(u_coarse)
            factor = int(self.scale_factor)
            return np.repeat(u_arr, factor)
    
    def v_cycle(self, u: State, rhs: State, depth: int = 0) -> State:
        """
        Perform one V-cycle (multigrid pattern).
        """
        if depth >= self.max_depth or (isinstance(u, np.ndarray) and len(u) <= 2):
            # Coarsest level: direct solve
            return rhs
        
        # Pre-smoothing (apply dissipative step)
        u_smoothed = 0.5 * (u + rhs)
        
        # Restrict residual
        residual = rhs - u_smoothed
        residual_coarse = self.apply(residual)
        
        # Recursive solve
        correction_coarse = self.v_cycle(
            np.zeros_like(residual_coarse) if isinstance(residual_coarse, np.ndarray) else 0.0,
            residual_coarse,
            depth + 1
        )
        
        # Prolongate correction
        correction = self.prolong(correction_coarse)
        
        # Correct and post-smooth
        u_corrected = u_smoothed + correction[:len(np.atleast_1d(u))] if isinstance(u, np.ndarray) else u_smoothed + correction
        
        return 0.5 * (u_corrected + rhs)
    
    def exp(self, t: float, u: State) -> State:
        """
        Recursive flow: iterated coarse-graining.
        """
        n_steps = max(1, int(abs(t) * self.scale_factor))
        result = u
        for _ in range(n_steps):
            result = self.apply(result)
        return result


@dataclass
class HybridGenerator(Generator):
    """
    Hybrid generator combining multiple poles:
    
    G = α_D·D + α_Ω·Ω + α_Σ·Σ + α_Ψ·Ψ
    
    The coefficients form a point on the operator simplex.
    """
    
    dissipative: Optional[DissipativeGenerator] = field(default=None)
    oscillatory: Optional[OscillatoryGenerator] = field(default=None)
    stochastic: Optional[StochasticGenerator] = field(default=None)
    recursive: Optional[RecursiveGenerator] = field(default=None)
    
    alpha_d: float = field(default=0.0)
    alpha_omega: float = field(default=0.0)
    alpha_sigma: float = field(default=0.0)
    alpha_psi: float = field(default=0.0)
    
    @property
    def pole(self) -> Pole:
        """Return dominant pole (highest coefficient)."""
        coeffs = {
            Pole.D: self.alpha_d,
            Pole.OMEGA: self.alpha_omega,
            Pole.SIGMA: self.alpha_sigma,
            Pole.PSI: self.alpha_psi,
        }
        return max(coeffs, key=coeffs.get)
    
    @property
    def symbol(self) -> str:
        parts = []
        if self.alpha_d != 0:
            parts.append(f"{self.alpha_d}D")
        if self.alpha_omega != 0:
            parts.append(f"{self.alpha_omega}Ω")
        if self.alpha_sigma != 0:
            parts.append(f"{self.alpha_sigma}Σ")
        if self.alpha_psi != 0:
            parts.append(f"{self.alpha_psi}Ψ")
        return " + ".join(parts) if parts else "0"
    
    @property
    def coefficients(self) -> Tuple[float, float, float, float]:
        """Return coefficient tuple (α_D, α_Ω, α_Σ, α_Ψ)."""
        return (self.alpha_d, self.alpha_omega, self.alpha_sigma, self.alpha_psi)
    
    @property
    def on_simplex(self) -> bool:
        """Check if coefficients form a valid simplex point."""
        coeffs = self.coefficients
        return all(c >= 0 for c in coeffs) and abs(sum(coeffs) - 1.0) < 1e-10
    
    def normalize_to_simplex(self) -> 'HybridGenerator':
        """Normalize coefficients to lie on the simplex."""
        total = sum(self.coefficients)
        if total == 0:
            return HybridGenerator(
                self.dissipative, self.oscillatory, self.stochastic, self.recursive,
                0.25, 0.25, 0.25, 0.25
            )
        return HybridGenerator(
            self.dissipative, self.oscillatory, self.stochastic, self.recursive,
            self.alpha_d / total,
            self.alpha_omega / total,
            self.alpha_sigma / total,
            self.alpha_psi / total
        )
    
    def __call__(self, u: State) -> State:
        return self.apply(u)
    
    def apply(self, u: State) -> State:
        """
        Apply hybrid generator: sum of scaled component generators.
        """
        result = np.zeros_like(np.atleast_1d(u)) if isinstance(u, np.ndarray) else 0.0
        
        if self.dissipative and self.alpha_d != 0:
            result = result + self.alpha_d * self.dissipative(u)
        
        if self.oscillatory and self.alpha_omega != 0:
            result = result + self.alpha_omega * self.oscillatory(u)
        
        if self.stochastic and self.alpha_sigma != 0:
            result = result + self.alpha_sigma * self.stochastic(u)
        
        if self.recursive and self.alpha_psi != 0:
            result = result + self.alpha_psi * self.recursive(u)
        
        return result
    
    def exp(self, t: float, u: State) -> State:
        """
        Approximate hybrid exponential using splitting.
        
        Uses Strang splitting for better accuracy.
        """
        dt = 0.01
        steps = max(1, int(abs(t) / dt))
        dt = t / steps
        
        result = u
        for _ in range(steps):
            # Strang splitting: A(dt/2) B(dt) A(dt/2)
            # Here: D → Ω → Σ → Ψ → Σ → Ω → D pattern
            if self.dissipative and self.alpha_d != 0:
                result = self.dissipative.exp(self.alpha_d * dt / 2, result)
            
            if self.oscillatory and self.alpha_omega != 0:
                result = self.oscillatory.exp(self.alpha_omega * dt, result)
            
            if self.stochastic and self.alpha_sigma != 0:
                result = self.stochastic.exp(self.alpha_sigma * dt, result)
            
            if self.recursive and self.alpha_psi != 0:
                result = self.recursive.exp(self.alpha_psi * dt, result)
            
            if self.dissipative and self.alpha_d != 0:
                result = self.dissipative.exp(self.alpha_d * dt / 2, result)
        
        return result
    
    @classmethod
    def combine(cls, *generators: Generator) -> 'HybridGenerator':
        """Combine multiple generators into a hybrid."""
        D = None
        Omega = None
        Sigma = None
        Psi = None
        alpha_d = 0.0
        alpha_omega = 0.0
        alpha_sigma = 0.0
        alpha_psi = 0.0
        
        for gen in generators:
            if isinstance(gen, ScaledGenerator):
                coef = gen.coefficient
                gen = gen.base
            else:
                coef = 1.0
            
            if isinstance(gen, DissipativeGenerator):
                D = gen
                alpha_d += coef
            elif isinstance(gen, OscillatoryGenerator):
                Omega = gen
                alpha_omega += coef
            elif isinstance(gen, StochasticGenerator):
                Sigma = gen
                alpha_sigma += coef
            elif isinstance(gen, RecursiveGenerator):
                Psi = gen
                alpha_psi += coef
            elif isinstance(gen, HybridGenerator):
                # Merge hybrid
                if gen.dissipative:
                    D = D or gen.dissipative
                    alpha_d += gen.alpha_d * coef
                if gen.oscillatory:
                    Omega = Omega or gen.oscillatory
                    alpha_omega += gen.alpha_omega * coef
                if gen.stochastic:
                    Sigma = Sigma or gen.stochastic
                    alpha_sigma += gen.alpha_sigma * coef
                if gen.recursive:
                    Psi = Psi or gen.recursive
                    alpha_psi += gen.alpha_psi * coef
        
        return cls(D, Omega, Sigma, Psi, alpha_d, alpha_omega, alpha_sigma, alpha_psi)
    
    def commutator_budget(self, u: State) -> Dict[str, float]:
        """
        Compute commutator norms for all pairs.
        
        Returns dict mapping edge names to commutator magnitudes.
        """
        budget = {}
        
        generators = [
            ("D", self.dissipative, self.alpha_d),
            ("Ω", self.oscillatory, self.alpha_omega),
            ("Σ", self.stochastic, self.alpha_sigma),
            ("Ψ", self.recursive, self.alpha_psi),
        ]
        
        for i, (name_i, gen_i, alpha_i) in enumerate(generators):
            if gen_i is None or alpha_i == 0:
                continue
            for name_j, gen_j, alpha_j in generators[i+1:]:
                if gen_j is None or alpha_j == 0:
                    continue
                
                # Compute commutator
                comm = gen_i.commutator(gen_j, u)
                if isinstance(comm, np.ndarray):
                    mag = np.linalg.norm(comm)
                else:
                    mag = abs(comm)
                
                budget[f"[{name_i},{name_j}]"] = mag * alpha_i * alpha_j
        
        return budget
