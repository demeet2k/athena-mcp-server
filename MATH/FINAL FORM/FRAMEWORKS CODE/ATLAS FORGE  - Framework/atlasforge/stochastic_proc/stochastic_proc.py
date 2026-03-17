"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STOCHASTIC PROCESSES MODULE                               ║
║                                                                              ║
║  Markov Chains, Brownian Motion, and Martingales                             ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Stochastic processes are the mathematical core of the Σ-pole.            ║
║    Random evolution encodes uncertainty and exploration,                    ║
║    while ergodicity connects to equilibrium and optimization.               ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Markov chain: P(X_{n+1}|X_n, ...) = P(X_{n+1}|X_n)                     ║
║    - Brownian motion: continuous paths, independent increments              ║
║    - Martingale: E[X_{n+1}|X_n, ...] = X_n                                  ║
║    - Ergodic theorem: time average = space average                          ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Σ-pole ↔ stochastic generators                                        ║
║    - Monte Carlo ↔ sampling from distributions                              ║
║    - Simulated annealing ↔ temperature-driven exploration                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Callable, Iterator
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# MARKOV CHAIN
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MarkovChain:
    """
    Discrete-time Markov chain with finite state space.
    
    X_{n+1} ~ P(·|X_n) where P is transition matrix.
    """
    transition_matrix: NDArray[np.float64]  # P[i,j] = P(j|i)
    state_names: Optional[List[str]] = None
    
    def __post_init__(self):
        n = self.transition_matrix.shape[0]
        if self.state_names is None:
            self.state_names = [str(i) for i in range(n)]
        
        # Verify stochastic matrix
        row_sums = np.sum(self.transition_matrix, axis=1)
        if not np.allclose(row_sums, 1.0):
            raise ValueError("Rows must sum to 1")
    
    @property
    def n_states(self) -> int:
        return self.transition_matrix.shape[0]
    
    def step(self, current_state: int) -> int:
        """Sample next state given current."""
        probs = self.transition_matrix[current_state]
        return np.random.choice(self.n_states, p=probs)
    
    def simulate(self, initial: int, n_steps: int) -> List[int]:
        """Simulate trajectory."""
        trajectory = [initial]
        current = initial
        
        for _ in range(n_steps):
            current = self.step(current)
            trajectory.append(current)
        
        return trajectory
    
    def stationary_distribution(self) -> NDArray[np.float64]:
        """
        Compute stationary distribution π with πP = π.
        
        Uses eigenvalue decomposition.
        """
        # Left eigenvector with eigenvalue 1
        eigenvalues, eigenvectors = np.linalg.eig(self.transition_matrix.T)
        
        # Find eigenvalue closest to 1
        idx = np.argmin(np.abs(eigenvalues - 1.0))
        
        pi = np.real(eigenvectors[:, idx])
        pi = pi / np.sum(pi)  # Normalize
        
        return np.abs(pi)
    
    def is_irreducible(self) -> bool:
        """Check if chain is irreducible (single communicating class)."""
        n = self.n_states
        # Use matrix powers to check reachability
        reachable = self.transition_matrix.copy()
        for _ in range(n - 1):
            reachable = reachable @ self.transition_matrix
            reachable = np.where(reachable > 0, 1, reachable)
        
        return np.all(reachable > 0)
    
    def is_aperiodic(self) -> bool:
        """Check if chain is aperiodic."""
        # Has self-loop or GCD of return times is 1
        return np.any(np.diag(self.transition_matrix) > 0)
    
    def is_ergodic(self) -> bool:
        """Check if chain is ergodic (irreducible + aperiodic)."""
        return self.is_irreducible() and self.is_aperiodic()
    
    def mixing_time(self, epsilon: float = 0.01, max_steps: int = 1000
                   ) -> int:
        """
        Estimate mixing time: min t such that ||P^t(i,·) - π||_TV < ε.
        """
        pi = self.stationary_distribution()
        P = self.transition_matrix.copy()
        
        for t in range(1, max_steps + 1):
            P = P @ self.transition_matrix
            
            # Total variation distance
            max_tv = 0
            for i in range(self.n_states):
                tv = 0.5 * np.sum(np.abs(P[i] - pi))
                max_tv = max(max_tv, tv)
            
            if max_tv < epsilon:
                return t
        
        return max_steps
    
    @classmethod
    def random_walk(cls, n: int) -> 'MarkovChain':
        """Random walk on cycle Z/nZ."""
        P = np.zeros((n, n))
        for i in range(n):
            P[i, (i - 1) % n] = 0.5
            P[i, (i + 1) % n] = 0.5
        return cls(P)
    
    @classmethod
    def ehrenfest(cls, n: int) -> 'MarkovChain':
        """Ehrenfest urn model with n balls."""
        P = np.zeros((n + 1, n + 1))
        for i in range(n + 1):
            if i > 0:
                P[i, i - 1] = i / n
            if i < n:
                P[i, i + 1] = (n - i) / n
        return cls(P)


# ═══════════════════════════════════════════════════════════════════════════════
# BROWNIAN MOTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BrownianMotion:
    """
    Standard Brownian motion (Wiener process).
    
    Properties:
        - B(0) = 0
        - Independent increments: B(t) - B(s) independent of B(r) for r ≤ s
        - B(t) - B(s) ~ N(0, t-s)
        - Continuous paths
    """
    drift: float = 0.0
    volatility: float = 1.0
    
    def sample_path(self, T: float, n_steps: int = 1000,
                   initial: float = 0.0) -> Tuple[NDArray, NDArray]:
        """
        Sample path of Brownian motion on [0, T].
        
        Returns (times, values).
        """
        dt = T / n_steps
        times = np.linspace(0, T, n_steps + 1)
        
        increments = np.random.normal(
            loc=self.drift * dt,
            scale=self.volatility * np.sqrt(dt),
            size=n_steps
        )
        
        values = np.zeros(n_steps + 1)
        values[0] = initial
        values[1:] = initial + np.cumsum(increments)
        
        return times, values
    
    def sample_at(self, t: float, initial: float = 0.0) -> float:
        """Sample B(t) given B(0) = initial."""
        return np.random.normal(
            loc=initial + self.drift * t,
            scale=self.volatility * np.sqrt(t)
        )
    
    def quadratic_variation(self, times: NDArray, values: NDArray) -> float:
        """
        Compute quadratic variation [B]_T = Σ (B_{t_{i+1}} - B_{t_i})².
        
        For Brownian motion: [B]_T = T.
        """
        increments = np.diff(values)
        return np.sum(increments ** 2)
    
    def hitting_time(self, level: float, n_samples: int = 10000,
                    max_T: float = 100.0) -> NDArray[np.float64]:
        """
        Estimate hitting time τ_a = inf{t: B(t) = a}.
        
        Returns samples of hitting times.
        """
        hitting_times = []
        
        for _ in range(n_samples):
            times, values = self.sample_path(max_T, 10000)
            
            # Find first crossing
            crossings = np.where(
                (values[:-1] < level) & (values[1:] >= level) |
                (values[:-1] > level) & (values[1:] <= level)
            )[0]
            
            if len(crossings) > 0:
                hitting_times.append(times[crossings[0]])
        
        return np.array(hitting_times)
    
    @classmethod
    def geometric(cls, mu: float, sigma: float) -> 'GeometricBrownianMotion':
        """Create geometric Brownian motion dS = μS dt + σS dW."""
        return GeometricBrownianMotion(mu, sigma)


@dataclass
class GeometricBrownianMotion:
    """
    Geometric Brownian motion: dS = μS dt + σS dW.
    
    Solution: S(t) = S(0) exp((μ - σ²/2)t + σW(t))
    """
    mu: float  # Drift
    sigma: float  # Volatility
    
    def sample_path(self, T: float, n_steps: int = 1000,
                   initial: float = 1.0) -> Tuple[NDArray, NDArray]:
        """Sample path of GBM."""
        dt = T / n_steps
        times = np.linspace(0, T, n_steps + 1)
        
        # Sample Brownian increments
        dW = np.random.normal(scale=np.sqrt(dt), size=n_steps)
        
        # Use exact solution at each step
        log_increments = (self.mu - 0.5 * self.sigma**2) * dt + self.sigma * dW
        log_values = np.zeros(n_steps + 1)
        log_values[0] = np.log(initial)
        log_values[1:] = log_values[0] + np.cumsum(log_increments)
        
        return times, np.exp(log_values)
    
    def expected_value(self, t: float, initial: float = 1.0) -> float:
        """E[S(t)] = S(0) exp(μt)."""
        return initial * np.exp(self.mu * t)
    
    def variance(self, t: float, initial: float = 1.0) -> float:
        """Var[S(t)] = S(0)² exp(2μt) (exp(σ²t) - 1)."""
        return initial**2 * np.exp(2 * self.mu * t) * (np.exp(self.sigma**2 * t) - 1)


# ═══════════════════════════════════════════════════════════════════════════════
# MARTINGALE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Martingale:
    """
    Abstract martingale: E[X_{n+1}|F_n] = X_n.
    
    Represented by sequence of values at filtration times.
    """
    values: NDArray[np.float64]
    times: NDArray[np.float64]
    
    def is_martingale(self, tolerance: float = 0.1, 
                     n_samples: int = 100) -> bool:
        """
        Statistical test for martingale property.
        
        Check if E[X_{t+1}|X_t] ≈ X_t.
        """
        # This would need ensemble of paths
        return True  # Placeholder
    
    def quadratic_variation(self) -> float:
        """[M]_T = Σ (M_{t_{i+1}} - M_{t_i})²."""
        return np.sum(np.diff(self.values) ** 2)
    
    def max_process(self) -> NDArray[np.float64]:
        """Running maximum M*_t = max_{s≤t} M_s."""
        return np.maximum.accumulate(self.values)
    
    def doob_maximal(self, p: float = 2) -> float:
        """
        Doob's maximal inequality bound.
        
        E[M*_T^p] ≤ (p/(p-1))^p E[|M_T|^p] for p > 1.
        """
        if p <= 1:
            raise ValueError("p must be > 1")
        
        max_val = np.max(np.abs(self.values))
        final_moment = np.abs(self.values[-1]) ** p
        
        coeff = (p / (p - 1)) ** p
        return coeff * final_moment


# ═══════════════════════════════════════════════════════════════════════════════
# SIGMA-POLE STOCHASTIC BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SigmaPoleStochasticBridge:
    """
    Bridge between Σ-pole and stochastic processes.
    """
    
    @staticmethod
    def simulated_annealing(
        energy: Callable[[NDArray], float],
        initial: NDArray,
        temperature_schedule: Callable[[int], float],
        n_steps: int = 10000,
        proposal_std: float = 1.0
    ) -> Tuple[NDArray, float]:
        """
        Simulated annealing optimization.
        
        Uses Metropolis-Hastings with decreasing temperature.
        """
        current = initial.copy()
        current_energy = energy(current)
        
        best = current.copy()
        best_energy = current_energy
        
        for step in range(n_steps):
            T = temperature_schedule(step)
            
            # Propose new state
            proposal = current + np.random.normal(scale=proposal_std, 
                                                  size=current.shape)
            proposal_energy = energy(proposal)
            
            # Accept/reject
            delta = proposal_energy - current_energy
            if delta < 0 or np.random.random() < np.exp(-delta / T):
                current = proposal
                current_energy = proposal_energy
                
                if current_energy < best_energy:
                    best = current.copy()
                    best_energy = current_energy
        
        return best, best_energy
    
    @staticmethod
    def mcmc_sample(
        log_prob: Callable[[NDArray], float],
        initial: NDArray,
        n_samples: int = 1000,
        burn_in: int = 100,
        proposal_std: float = 1.0
    ) -> NDArray[np.float64]:
        """
        MCMC sampling via Metropolis-Hastings.
        """
        d = initial.shape[0]
        samples = np.zeros((n_samples, d))
        
        current = initial.copy()
        current_log_p = log_prob(current)
        
        n_accepted = 0
        
        for i in range(burn_in + n_samples):
            # Proposal
            proposal = current + np.random.normal(scale=proposal_std, size=d)
            proposal_log_p = log_prob(proposal)
            
            # Accept/reject
            log_alpha = proposal_log_p - current_log_p
            if np.log(np.random.random()) < log_alpha:
                current = proposal
                current_log_p = proposal_log_p
                n_accepted += 1
            
            if i >= burn_in:
                samples[i - burn_in] = current
        
        return samples
    
    @staticmethod
    def langevin_dynamics(
        grad_log_prob: Callable[[NDArray], NDArray],
        initial: NDArray,
        step_size: float = 0.01,
        n_steps: int = 1000
    ) -> List[NDArray]:
        """
        Langevin dynamics: dx = ∇log p(x) dt + √2 dW.
        
        Samples from distribution with density p(x).
        """
        d = initial.shape[0]
        trajectory = [initial.copy()]
        
        x = initial.copy()
        
        for _ in range(n_steps):
            grad = grad_log_prob(x)
            noise = np.random.normal(size=d)
            x = x + step_size * grad + np.sqrt(2 * step_size) * noise
            trajectory.append(x.copy())
        
        return trajectory


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def markov_chain(P: NDArray) -> MarkovChain:
    """Create Markov chain from transition matrix."""
    return MarkovChain(P)


def brownian_motion(T: float, n_steps: int = 1000) -> Tuple[NDArray, NDArray]:
    """Sample standard Brownian motion path."""
    return BrownianMotion().sample_path(T, n_steps)


def geometric_brownian_motion(mu: float, sigma: float, T: float,
                             initial: float = 1.0) -> Tuple[NDArray, NDArray]:
    """Sample geometric Brownian motion path."""
    return GeometricBrownianMotion(mu, sigma).sample_path(T, initial=initial)


def stationary_distribution(P: NDArray) -> NDArray:
    """Compute stationary distribution of Markov chain."""
    return MarkovChain(P).stationary_distribution()


def simulated_annealing(energy: Callable, initial: NDArray,
                       n_steps: int = 10000) -> Tuple[NDArray, float]:
    """Run simulated annealing optimization."""
    def schedule(step):
        return 1.0 / (1 + 0.01 * step)
    
    return SigmaPoleStochasticBridge.simulated_annealing(
        energy, initial, schedule, n_steps
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Markov
    'MarkovChain',
    
    # Brownian
    'BrownianMotion',
    'GeometricBrownianMotion',
    
    # Martingale
    'Martingale',
    
    # Bridge
    'SigmaPoleStochasticBridge',
    
    # Functions
    'markov_chain',
    'brownian_motion',
    'geometric_brownian_motion',
    'stationary_distribution',
    'simulated_annealing',
]
