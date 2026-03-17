"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - MCMC & Sampling Module                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Implements sampling algorithms in the quad-polar framework:

Overdamped Langevin (D+Σ):
    dX_t = -∇V(X_t)dt + √(2)dW_t
    - D: gradient drift toward low energy
    - Σ: stochastic exploration via Brownian motion

Underdamped Langevin / HMC (D+Ω+Σ):
    dX_t = P_t dt
    dP_t = -γP_t dt - ∇V(X_t)dt + √(2γ)dW_t
    - D: friction/dissipation
    - Ω: Hamiltonian transport (long coherent trajectories)
    - Σ: momentum refresh

Hierarchical MCMC (D+Σ+Ψ):
    - D: structure-aware drift at each level
    - Σ: local random proposals
    - Ψ: cross-level transitions (tempering, coarsening)

Mixing Time Analysis:
    t_mix(ε) ≤ (1/gap) log(1/(ε π_min))
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


@dataclass
class SamplingResult:
    """Result of MCMC sampling."""
    samples: NDArray[np.float64]        # Shape: (n_samples, dimension)
    accept_rate: float
    effective_sample_size: float
    autocorrelation_time: float
    final_state: NDArray[np.float64]
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def n_samples(self) -> int:
        return len(self.samples)
    
    def mean(self) -> NDArray[np.float64]:
        return np.mean(self.samples, axis=0)
    
    def std(self) -> NDArray[np.float64]:
        return np.std(self.samples, axis=0)
    
    def cov(self) -> NDArray[np.float64]:
        return np.cov(self.samples.T)


class Sampler(ABC):
    """Abstract base class for MCMC samplers."""
    
    @abstractmethod
    def sample(
        self,
        log_prob: Callable[[NDArray], float],
        x0: NDArray,
        n_samples: int,
        **kwargs,
    ) -> SamplingResult:
        """Generate samples from target distribution."""
        pass


class OverdampedLangevin(Sampler):
    """
    Overdamped Langevin dynamics (D+Σ).
    
    dX_t = -∇V(X_t)dt + √(2τ)dW_t
    
    where V(x) = -log π(x) is the potential.
    
    Quad-polar decomposition:
    - D: gradient drift (-∇V)
    - Σ: Brownian diffusion (√(2τ)dW)
    """
    
    def __init__(
        self,
        step_size: float = 0.01,
        temperature: float = 1.0,
        seed: Optional[int] = None,
    ):
        self.step_size = step_size
        self.temperature = temperature
        self.rng = np.random.default_rng(seed)
    
    def sample(
        self,
        log_prob: Callable[[NDArray], float],
        x0: NDArray,
        n_samples: int,
        burn_in: int = 100,
        thin: int = 1,
        grad_log_prob: Optional[Callable] = None,
    ) -> SamplingResult:
        """
        Sample using Unadjusted Langevin Algorithm (ULA).
        """
        x = x0.copy().astype(np.float64)
        d = len(x)
        
        if grad_log_prob is None:
            grad_log_prob = lambda x: self._numerical_gradient(log_prob, x)
        
        samples = []
        total_steps = burn_in + n_samples * thin
        
        for step in range(total_steps):
            # Langevin update: x' = x + ε∇log π(x) + √(2ετ)ξ
            grad = grad_log_prob(x)
            noise = self.rng.standard_normal(d)
            
            x = (x + 
                 self.step_size * grad +                           # D: gradient
                 np.sqrt(2 * self.step_size * self.temperature) * noise)  # Σ: noise
            
            # Collect sample
            if step >= burn_in and (step - burn_in) % thin == 0:
                samples.append(x.copy())
        
        samples = np.array(samples)
        
        # Compute diagnostics
        ess = self._effective_sample_size(samples)
        act = n_samples / ess if ess > 0 else float('inf')
        
        return SamplingResult(
            samples=samples,
            accept_rate=1.0,  # ULA always accepts
            effective_sample_size=ess,
            autocorrelation_time=act,
            final_state=x,
            diagnostics={'method': 'ULA', 'step_size': self.step_size},
        )
    
    def _numerical_gradient(
        self,
        f: Callable[[NDArray], float],
        x: NDArray,
        eps: float = 1e-6,
    ) -> NDArray:
        """Central difference gradient."""
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        return grad
    
    def _effective_sample_size(self, samples: NDArray) -> float:
        """Estimate effective sample size using autocorrelation."""
        n = len(samples)
        if n < 2:
            return float(n)
        
        # Use first component for ESS estimation
        x = samples[:, 0] - np.mean(samples[:, 0])
        acf = np.correlate(x, x, mode='full')[n-1:] / (np.var(x) * n)
        
        # Sum autocorrelations until they become negative
        tau = 1.0
        for k in range(1, min(n // 2, 100)):
            if acf[k] < 0:
                break
            tau += 2 * acf[k]
        
        return n / tau


class MetropolisAdjustedLangevin(Sampler):
    """
    MALA: Langevin with Metropolis-Hastings correction.
    
    Corrects the discretization bias of ULA to sample exactly
    from the target distribution.
    """
    
    def __init__(
        self,
        step_size: float = 0.1,
        temperature: float = 1.0,
        seed: Optional[int] = None,
    ):
        self.step_size = step_size
        self.temperature = temperature
        self.rng = np.random.default_rng(seed)
    
    def sample(
        self,
        log_prob: Callable[[NDArray], float],
        x0: NDArray,
        n_samples: int,
        burn_in: int = 100,
        thin: int = 1,
        grad_log_prob: Optional[Callable] = None,
    ) -> SamplingResult:
        """Sample using MALA."""
        x = x0.copy().astype(np.float64)
        d = len(x)
        
        if grad_log_prob is None:
            grad_log_prob = lambda x: self._numerical_gradient(log_prob, x)
        
        samples = []
        n_accept = 0
        total_steps = burn_in + n_samples * thin
        
        log_p_x = log_prob(x)
        grad_x = grad_log_prob(x)
        
        for step in range(total_steps):
            # Propose: y = x + ε∇log π(x) + √(2ε)ξ
            noise = self.rng.standard_normal(d)
            y = (x + 
                 self.step_size * grad_x + 
                 np.sqrt(2 * self.step_size * self.temperature) * noise)
            
            log_p_y = log_prob(y)
            grad_y = grad_log_prob(y)
            
            # Compute proposal log-densities
            log_q_xy = -np.sum((y - x - self.step_size * grad_x)**2) / (4 * self.step_size * self.temperature)
            log_q_yx = -np.sum((x - y - self.step_size * grad_y)**2) / (4 * self.step_size * self.temperature)
            
            # Metropolis-Hastings acceptance
            log_alpha = (log_p_y - log_p_x) + (log_q_yx - log_q_xy)
            
            if np.log(self.rng.random()) < log_alpha:
                x = y
                log_p_x = log_p_y
                grad_x = grad_y
                n_accept += 1
            
            # Collect sample
            if step >= burn_in and (step - burn_in) % thin == 0:
                samples.append(x.copy())
        
        samples = np.array(samples)
        accept_rate = n_accept / total_steps
        
        ess = self._effective_sample_size(samples)
        
        return SamplingResult(
            samples=samples,
            accept_rate=accept_rate,
            effective_sample_size=ess,
            autocorrelation_time=n_samples / ess if ess > 0 else float('inf'),
            final_state=x,
            diagnostics={'method': 'MALA', 'accept_rate': accept_rate},
        )
    
    def _numerical_gradient(self, f, x, eps=1e-6):
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus, x_minus = x.copy(), x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        return grad
    
    def _effective_sample_size(self, samples):
        n = len(samples)
        if n < 2:
            return float(n)
        x = samples[:, 0] - np.mean(samples[:, 0])
        acf = np.correlate(x, x, mode='full')[n-1:] / (np.var(x) * n + 1e-10)
        tau = 1.0
        for k in range(1, min(n // 2, 100)):
            if acf[k] < 0:
                break
            tau += 2 * acf[k]
        return n / tau


class HamiltonianMonteCarlo(Sampler):
    """
    Hamiltonian Monte Carlo (D+Ω+Σ).
    
    H(x, p) = V(x) + p²/2
    
    Quad-polar decomposition:
    - D: friction in underdamped version
    - Ω: Hamiltonian flow (symplectic, volume-preserving)
    - Σ: momentum refresh (Gaussian resampling)
    
    Key insight: Ω provides LONG COHERENT TRAJECTORIES
    that can cross wide valleys, unlike random walk.
    """
    
    def __init__(
        self,
        step_size: float = 0.1,
        n_leapfrog: int = 10,
        mass: Optional[NDArray] = None,
        seed: Optional[int] = None,
    ):
        self.step_size = step_size
        self.n_leapfrog = n_leapfrog
        self.mass = mass
        self.rng = np.random.default_rng(seed)
    
    def sample(
        self,
        log_prob: Callable[[NDArray], float],
        x0: NDArray,
        n_samples: int,
        burn_in: int = 100,
        thin: int = 1,
        grad_log_prob: Optional[Callable] = None,
    ) -> SamplingResult:
        """Sample using HMC."""
        x = x0.copy().astype(np.float64)
        d = len(x)
        
        if self.mass is None:
            M = np.eye(d)
            M_inv = np.eye(d)
        else:
            M = np.diag(self.mass)
            M_inv = np.diag(1.0 / self.mass)
        
        if grad_log_prob is None:
            grad_log_prob = lambda x: self._numerical_gradient(log_prob, x)
        
        samples = []
        n_accept = 0
        total_steps = burn_in + n_samples * thin
        
        for step in range(total_steps):
            # === Σ: Momentum refresh ===
            p = self.rng.multivariate_normal(np.zeros(d), M)
            
            # Store initial state
            x_init, p_init = x.copy(), p.copy()
            H_init = -log_prob(x) + 0.5 * p @ M_inv @ p
            
            # === Ω: Leapfrog integration (Hamiltonian flow) ===
            grad = grad_log_prob(x)
            
            # Half step for momentum
            p = p + 0.5 * self.step_size * grad
            
            # Full steps
            for _ in range(self.n_leapfrog - 1):
                x = x + self.step_size * M_inv @ p
                grad = grad_log_prob(x)
                p = p + self.step_size * grad
            
            # Final position and half momentum step
            x = x + self.step_size * M_inv @ p
            grad = grad_log_prob(x)
            p = p + 0.5 * self.step_size * grad
            
            # Negate momentum for reversibility
            p = -p
            
            # Compute Hamiltonian
            H_final = -log_prob(x) + 0.5 * p @ M_inv @ p
            
            # Metropolis acceptance
            if np.log(self.rng.random()) < H_init - H_final:
                n_accept += 1
            else:
                x = x_init
            
            # Collect sample
            if step >= burn_in and (step - burn_in) % thin == 0:
                samples.append(x.copy())
        
        samples = np.array(samples)
        accept_rate = n_accept / total_steps
        
        ess = self._effective_sample_size(samples)
        
        return SamplingResult(
            samples=samples,
            accept_rate=accept_rate,
            effective_sample_size=ess,
            autocorrelation_time=n_samples / ess if ess > 0 else float('inf'),
            final_state=x,
            diagnostics={
                'method': 'HMC',
                'n_leapfrog': self.n_leapfrog,
                'accept_rate': accept_rate,
            },
        )
    
    def _numerical_gradient(self, f, x, eps=1e-6):
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus, x_minus = x.copy(), x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        return grad
    
    def _effective_sample_size(self, samples):
        n = len(samples)
        if n < 2:
            return float(n)
        x = samples[:, 0] - np.mean(samples[:, 0])
        acf = np.correlate(x, x, mode='full')[n-1:] / (np.var(x) * n + 1e-10)
        tau = 1.0
        for k in range(1, min(n // 2, 100)):
            if acf[k] < 0:
                break
            tau += 2 * acf[k]
        return n / tau


class ParallelTempering(Sampler):
    """
    Parallel Tempering / Replica Exchange (D+Σ+Ψ).
    
    Run multiple chains at different temperatures:
    π_β(x) ∝ exp(-β V(x))
    
    Quad-polar decomposition:
    - D: gradient drift at each temperature
    - Σ: local MCMC moves at each level
    - Ψ: CROSS-LEVEL SWAPS between temperatures
    
    Ψ is the KEY SHORTCUT: allows low-temperature chain
    to escape local minima via high-temperature exploration.
    """
    
    def __init__(
        self,
        temperatures: List[float],
        local_sampler: str = 'mala',
        n_swap_attempts: int = 1,
        seed: Optional[int] = None,
    ):
        self.temperatures = sorted(temperatures, reverse=True)
        self.n_temps = len(temperatures)
        self.local_sampler = local_sampler
        self.n_swap_attempts = n_swap_attempts
        self.rng = np.random.default_rng(seed)
    
    def sample(
        self,
        log_prob: Callable[[NDArray], float],
        x0: NDArray,
        n_samples: int,
        burn_in: int = 100,
        thin: int = 1,
        step_size: float = 0.1,
    ) -> SamplingResult:
        """Sample using parallel tempering."""
        d = len(x0)
        
        # Initialize chains at all temperatures
        chains = [x0.copy() for _ in range(self.n_temps)]
        log_probs = [log_prob(x0) for _ in range(self.n_temps)]
        
        samples = []
        n_swaps = 0
        total_steps = burn_in + n_samples * thin
        
        for step in range(total_steps):
            # === Σ: Local MCMC moves at each temperature ===
            for i, T in enumerate(self.temperatures):
                # Simple Metropolis step
                proposal = chains[i] + step_size * np.sqrt(T) * self.rng.standard_normal(d)
                log_p_prop = log_prob(proposal)
                
                # Accept/reject with temperature
                log_alpha = (log_p_prop - log_probs[i]) / T
                if np.log(self.rng.random()) < log_alpha:
                    chains[i] = proposal
                    log_probs[i] = log_p_prop
            
            # === Ψ: Cross-level swap attempts ===
            for _ in range(self.n_swap_attempts):
                # Choose adjacent pair
                i = self.rng.integers(self.n_temps - 1)
                j = i + 1
                
                T_i, T_j = self.temperatures[i], self.temperatures[j]
                
                # Swap acceptance probability
                log_alpha = ((1/T_j - 1/T_i) * log_probs[i] + 
                            (1/T_i - 1/T_j) * log_probs[j])
                
                if np.log(self.rng.random()) < log_alpha:
                    chains[i], chains[j] = chains[j], chains[i]
                    log_probs[i], log_probs[j] = log_probs[j], log_probs[i]
                    n_swaps += 1
            
            # Collect sample from coldest chain (T=1 or lowest)
            if step >= burn_in and (step - burn_in) % thin == 0:
                samples.append(chains[-1].copy())  # Coldest chain
        
        samples = np.array(samples)
        swap_rate = n_swaps / (total_steps * self.n_swap_attempts)
        
        ess = self._effective_sample_size(samples)
        
        return SamplingResult(
            samples=samples,
            accept_rate=swap_rate,
            effective_sample_size=ess,
            autocorrelation_time=n_samples / ess if ess > 0 else float('inf'),
            final_state=chains[-1],
            diagnostics={
                'method': 'ParallelTempering',
                'temperatures': self.temperatures,
                'swap_rate': swap_rate,
            },
        )
    
    def _effective_sample_size(self, samples):
        n = len(samples)
        if n < 2:
            return float(n)
        x = samples[:, 0] - np.mean(samples[:, 0])
        acf = np.correlate(x, x, mode='full')[n-1:] / (np.var(x) * n + 1e-10)
        tau = 1.0
        for k in range(1, min(n // 2, 100)):
            if acf[k] < 0:
                break
            tau += 2 * acf[k]
        return n / tau


class SimulatedAnnealing:
    """
    Simulated Annealing for optimization (Ω+Σ with cooling).
    
    Temperature schedule T(t) → 0 balances:
    - High T: exploration (Σ dominates)
    - Low T: exploitation (Ω/D dominates)
    """
    
    def __init__(
        self,
        initial_temp: float = 10.0,
        final_temp: float = 0.01,
        cooling_rate: float = 0.99,
        seed: Optional[int] = None,
    ):
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.cooling_rate = cooling_rate
        self.rng = np.random.default_rng(seed)
    
    def minimize(
        self,
        energy: Callable[[NDArray], float],
        x0: NDArray,
        max_iterations: int = 10000,
    ) -> Tuple[NDArray, float, List[float]]:
        """Minimize energy function."""
        x = x0.copy()
        d = len(x)
        
        E = energy(x)
        best_x = x.copy()
        best_E = E
        
        T = self.initial_temp
        history = [E]
        
        for _ in range(max_iterations):
            # Propose move
            x_new = x + T * self.rng.standard_normal(d)
            E_new = energy(x_new)
            
            # Accept/reject
            delta_E = E_new - E
            if delta_E < 0 or self.rng.random() < np.exp(-delta_E / T):
                x, E = x_new, E_new
                if E < best_E:
                    best_x, best_E = x.copy(), E
            
            history.append(best_E)
            
            # Cool down
            T = max(self.final_temp, T * self.cooling_rate)
        
        return best_x, best_E, history


@dataclass
class MixingDiagnostics:
    """Diagnostics for mixing analysis."""
    spectral_gap: float
    mixing_time_bound: float
    relaxation_time: float
    effective_sample_size: float
    
    def summary(self) -> str:
        return (f"Mixing Diagnostics:\n"
                f"  Spectral gap: {self.spectral_gap:.4f}\n"
                f"  Mixing time: {self.mixing_time_bound:.2f}\n"
                f"  Relaxation time: {self.relaxation_time:.2f}\n"
                f"  ESS: {self.effective_sample_size:.2f}")


def estimate_mixing_time(
    samples: NDArray,
    target_ess_fraction: float = 0.5,
) -> MixingDiagnostics:
    """Estimate mixing diagnostics from samples."""
    n = len(samples)
    if n < 10:
        return MixingDiagnostics(0, float('inf'), float('inf'), n)
    
    # Compute autocorrelation
    x = samples[:, 0] - np.mean(samples[:, 0])
    var_x = np.var(x)
    if var_x < 1e-15:
        return MixingDiagnostics(1.0, 1.0, 1.0, float(n))
    
    acf = np.correlate(x, x, mode='full')[n-1:] / (var_x * n)
    
    # Estimate integrated autocorrelation time
    tau = 1.0
    for k in range(1, min(n // 2, 100)):
        if acf[k] < 0.05:
            break
        tau += 2 * acf[k]
    
    ess = n / tau
    
    # Spectral gap estimate from first autocorrelation
    if len(acf) > 1 and acf[1] > 0:
        rho = acf[1]
        gap = 1 - rho
        relaxation = 1 / gap if gap > 0 else float('inf')
    else:
        gap = 1.0
        relaxation = 1.0
    
    # Mixing time bound
    mixing_time = tau * np.log(1 / (1 - target_ess_fraction))
    
    return MixingDiagnostics(
        spectral_gap=gap,
        mixing_time_bound=mixing_time,
        relaxation_time=relaxation,
        effective_sample_size=ess,
    )


# Convenience functions
def langevin_sample(
    log_prob: Callable,
    x0: NDArray,
    n_samples: int = 1000,
    step_size: float = 0.01,
    **kwargs,
) -> SamplingResult:
    """Convenience function for Langevin sampling."""
    sampler = OverdampedLangevin(step_size=step_size, **kwargs)
    return sampler.sample(log_prob, x0, n_samples)


def hmc_sample(
    log_prob: Callable,
    x0: NDArray,
    n_samples: int = 1000,
    step_size: float = 0.1,
    n_leapfrog: int = 10,
    **kwargs,
) -> SamplingResult:
    """Convenience function for HMC sampling."""
    sampler = HamiltonianMonteCarlo(step_size=step_size, n_leapfrog=n_leapfrog, **kwargs)
    return sampler.sample(log_prob, x0, n_samples)
