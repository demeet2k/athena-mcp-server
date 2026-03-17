"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Stochastic Operators (Σ Pole)                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Implements the Σ (Sigma) pole: Stochastic/Probabilistic operators.

Markov Chains:
    p_{t+1} = p_t K  (row-stochastic convention)
    
Key Properties:
- Mass conservation: Σ_j K_{ij} = 1
- Irreducibility → unique stationary distribution π
- Detailed balance: π_i K_{ij} = π_j K_{ji} (reversibility)
- Spectral gap: 1 - λ_2 controls mixing time

Fokker-Planck (continuous):
    ∂_t ρ = -∇·(bρ) + (1/2)∇²(aρ)
    
This is L* acting on densities (Fire-side evolution).

Mixing Time:
    t_mix(ε) ≤ (1/gap) log(1/(ε π_min))
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


@dataclass
class MarkovChain:
    """
    Finite-state discrete-time Markov chain.
    
    Uses row-stochastic convention: p' = pK where p is a row vector.
    """
    transition_matrix: NDArray[np.float64]  # K[i,j] = P(j|i)
    state_names: Optional[List[str]] = None
    
    def __post_init__(self):
        self._validate()
        self._compute_stationary()
    
    def _validate(self):
        """Validate transition matrix."""
        K = self.transition_matrix
        n = K.shape[0]
        
        # Check square
        assert K.shape == (n, n), "Transition matrix must be square"
        
        # Check non-negative
        assert np.all(K >= -1e-10), "Transition probabilities must be non-negative"
        
        # Check row-stochastic
        row_sums = np.sum(K, axis=1)
        assert np.allclose(row_sums, 1.0), f"Rows must sum to 1, got {row_sums}"
    
    def _compute_stationary(self):
        """Compute stationary distribution."""
        K = self.transition_matrix
        n = K.shape[0]
        
        # Find left eigenvector with eigenvalue 1
        eigenvalues, eigenvectors = np.linalg.eig(K.T)
        
        # Find eigenvalue closest to 1
        idx = np.argmin(np.abs(eigenvalues - 1))
        pi = np.real(eigenvectors[:, idx])
        
        # Normalize to probability
        pi = np.abs(pi)
        self._stationary = pi / np.sum(pi)
        
        # Sort eigenvalues by magnitude
        sorted_eigs = np.sort(np.abs(eigenvalues))[::-1]
        self._eigenvalues = sorted_eigs
        self._spectral_gap = 1 - sorted_eigs[1] if len(sorted_eigs) > 1 else 1.0
    
    @property
    def n_states(self) -> int:
        return self.transition_matrix.shape[0]
    
    @property
    def stationary(self) -> NDArray[np.float64]:
        """Stationary distribution π."""
        return self._stationary
    
    @property
    def spectral_gap(self) -> float:
        """Spectral gap 1 - λ_2."""
        return self._spectral_gap
    
    @property
    def mixing_time(self, eps: float = 0.25) -> float:
        """Mixing time bound t_mix(ε)."""
        if self._spectral_gap < 1e-10:
            return float('inf')
        pi_min = np.min(self._stationary[self._stationary > 1e-15])
        return (1 / self._spectral_gap) * np.log(1 / (eps * pi_min))
    
    @property
    def relaxation_time(self) -> float:
        """Relaxation time 1/gap."""
        if self._spectral_gap < 1e-10:
            return float('inf')
        return 1 / self._spectral_gap
    
    def is_reversible(self) -> bool:
        """Check detailed balance."""
        K = self.transition_matrix
        pi = self._stationary
        n = self.n_states
        
        for i in range(n):
            for j in range(n):
                if abs(pi[i] * K[i, j] - pi[j] * K[j, i]) > 1e-10:
                    return False
        return True
    
    def is_irreducible(self) -> bool:
        """Check if chain is irreducible (single communicating class)."""
        K = self.transition_matrix
        n = self.n_states
        
        # Use matrix powers to check reachability
        reach = np.eye(n) > 0
        power = K.copy()
        
        for _ in range(n):
            reach = reach | (power > 1e-10)
            power = power @ K
        
        return np.all(reach)
    
    def evolve(self, p: NDArray, steps: int = 1) -> NDArray:
        """Evolve distribution p forward by given steps."""
        K = self.transition_matrix
        for _ in range(steps):
            p = p @ K
        return p
    
    def simulate(
        self,
        initial_state: int,
        n_steps: int,
        seed: Optional[int] = None,
    ) -> List[int]:
        """Simulate trajectory of the chain."""
        rng = np.random.default_rng(seed)
        K = self.transition_matrix
        
        trajectory = [initial_state]
        state = initial_state
        
        for _ in range(n_steps):
            state = rng.choice(self.n_states, p=K[state])
            trajectory.append(state)
        
        return trajectory
    
    def hitting_time(
        self,
        target_states: List[int],
        initial_dist: Optional[NDArray] = None,
    ) -> float:
        """Expected hitting time to target states."""
        if initial_dist is None:
            initial_dist = self._stationary
        
        n = self.n_states
        target_set = set(target_states)
        
        # Solve (I - K_A) h = 1 for non-target states
        non_target = [i for i in range(n) if i not in target_set]
        
        if not non_target:
            return 0.0
        
        # Restricted transition matrix
        K_A = self.transition_matrix[np.ix_(non_target, non_target)]
        
        # Solve for hitting times
        A = np.eye(len(non_target)) - K_A
        b = np.ones(len(non_target))
        
        try:
            h = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            return float('inf')
        
        # Average over initial distribution
        h_full = np.zeros(n)
        for i, idx in enumerate(non_target):
            h_full[idx] = h[i]
        
        return np.dot(initial_dist, h_full)
    
    @classmethod
    def random_walk_on_graph(
        cls,
        adjacency: NDArray,
        lazy: float = 0.0,
    ) -> 'MarkovChain':
        """Create random walk on graph from adjacency matrix."""
        n = adjacency.shape[0]
        
        # Compute degree
        degree = np.sum(adjacency, axis=1)
        
        # Transition matrix
        K = np.zeros((n, n))
        for i in range(n):
            if degree[i] > 0:
                K[i] = adjacency[i] / degree[i]
            else:
                K[i, i] = 1.0  # Self-loop for isolated vertex
        
        # Add laziness
        if lazy > 0:
            K = (1 - lazy) * K + lazy * np.eye(n)
        
        return cls(transition_matrix=K)
    
    @classmethod
    def metropolis_hastings(
        cls,
        energy: NDArray,
        temperature: float = 1.0,
        proposal: Optional[NDArray] = None,
    ) -> 'MarkovChain':
        """Create Metropolis-Hastings chain for given energy."""
        n = len(energy)
        
        if proposal is None:
            # Uniform proposal on all states
            proposal = np.ones((n, n)) / n
        
        # Gibbs distribution
        pi = np.exp(-energy / temperature)
        pi = pi / np.sum(pi)
        
        # Build transition matrix with detailed balance
        K = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Acceptance probability
                    alpha = min(1.0, (pi[j] * proposal[j, i]) / (pi[i] * proposal[i, j] + 1e-15))
                    K[i, j] = proposal[i, j] * alpha
            
            # Self-loop probability
            K[i, i] = 1.0 - np.sum(K[i])
        
        return cls(transition_matrix=K)


@dataclass
class ContinuousTimeMarkovChain:
    """
    Continuous-time Markov chain with generator Q.
    
    Evolution: ∂_t p = p Q  (row convention)
    
    Q has:
    - q_{ij} ≥ 0 for i ≠ j (jump rates)
    - q_{ii} = -Σ_{j≠i} q_{ij} (rows sum to zero)
    """
    generator: NDArray[np.float64]  # Q matrix
    
    def __post_init__(self):
        self._validate()
        self._compute_stationary()
    
    def _validate(self):
        Q = self.generator
        n = Q.shape[0]
        
        # Check rows sum to zero
        row_sums = np.sum(Q, axis=1)
        assert np.allclose(row_sums, 0, atol=1e-10), "Generator rows must sum to 0"
        
        # Check off-diagonal non-negative
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert Q[i, j] >= -1e-10, "Off-diagonal entries must be non-negative"
    
    def _compute_stationary(self):
        """Compute stationary distribution."""
        Q = self.generator
        n = Q.shape[0]
        
        # Solve πQ = 0 with constraint Σπ = 1
        # Equivalent to finding null space of Q^T
        
        # Replace one equation with normalization
        A = Q.T.copy()
        A[-1] = np.ones(n)
        b = np.zeros(n)
        b[-1] = 1.0
        
        try:
            pi = np.linalg.solve(A, b)
            pi = np.maximum(pi, 0)  # Ensure non-negative
            self._stationary = pi / np.sum(pi)
        except np.linalg.LinAlgError:
            self._stationary = np.ones(n) / n
    
    @property
    def n_states(self) -> int:
        return self.generator.shape[0]
    
    @property
    def stationary(self) -> NDArray:
        return self._stationary
    
    def transition_matrix(self, dt: float) -> NDArray:
        """Compute transition matrix P(dt) = exp(dt Q)."""
        from scipy.linalg import expm
        return expm(dt * self.generator)
    
    def evolve(self, p: NDArray, t: float) -> NDArray:
        """Evolve distribution to time t."""
        P = self.transition_matrix(t)
        return p @ P


@dataclass
class DiffusionOperator:
    """
    Diffusion operator (Fokker-Planck generator).
    
    L f = b·∇f + (1/2) a:∇²f
    
    Adjoint L* acts on densities:
    ∂_t ρ = L* ρ = -∇·(bρ) + (1/2)∇²(aρ)
    """
    drift: Callable[[NDArray], NDArray]     # b(x)
    diffusion: Callable[[NDArray], NDArray] # a(x) (scalar or matrix)
    
    def apply(self, f: Callable, x: NDArray, eps: float = 1e-6) -> float:
        """Apply L to function f at point x."""
        d = len(x)
        b = self.drift(x)
        a = self.diffusion(x)
        
        # Gradient term
        grad_f = np.zeros(d)
        for i in range(d):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad_f[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        
        # Laplacian term
        laplacian_f = 0.0
        for i in range(d):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            laplacian_f += (f(x_plus) - 2*f(x) + f(x_minus)) / (eps**2)
        
        if np.isscalar(a):
            return np.dot(b, grad_f) + 0.5 * a * laplacian_f
        else:
            # Full diffusion matrix
            hessian = np.zeros((d, d))
            for i in range(d):
                for j in range(d):
                    # Mixed partial
                    x_pp = x.copy()
                    x_pm = x.copy()
                    x_mp = x.copy()
                    x_mm = x.copy()
                    x_pp[i] += eps
                    x_pp[j] += eps
                    x_pm[i] += eps
                    x_pm[j] -= eps
                    x_mp[i] -= eps
                    x_mp[j] += eps
                    x_mm[i] -= eps
                    x_mm[j] -= eps
                    hessian[i, j] = (f(x_pp) - f(x_pm) - f(x_mp) + f(x_mm)) / (4 * eps**2)
            
            return np.dot(b, grad_f) + 0.5 * np.sum(a * hessian)


class FireMixingOperator:
    """
    Fire mixing operator: p' = (1-α)p + αu
    
    Contracts toward reference distribution u (often uniform).
    
    Properties:
    - Affine contraction: ||T(p) - u|| ≤ (1-α)||p - u||
    - Spectral gap: α
    - Mixing time: O(1/α log(1/ε))
    """
    
    def __init__(self, reference: NDArray, alpha: float = 0.1):
        """
        Args:
            reference: Target distribution to mix toward
            alpha: Mixing rate (0 < α ≤ 1)
        """
        self.reference = reference / np.sum(reference)
        self.alpha = alpha
    
    def apply(self, p: NDArray) -> NDArray:
        """Apply mixing operator."""
        return (1 - self.alpha) * p + self.alpha * self.reference
    
    def iterate(self, p: NDArray, n_steps: int) -> NDArray:
        """Apply mixing n_steps times."""
        for _ in range(n_steps):
            p = self.apply(p)
        return p
    
    @property
    def spectral_gap(self) -> float:
        return self.alpha
    
    def mixing_time(self, eps: float = 0.25) -> float:
        """Time to reach ε-close to reference."""
        return np.log(1 / eps) / np.log(1 / (1 - self.alpha))


def create_random_walk_laplacian(adjacency: NDArray) -> NDArray:
    """
    Create normalized graph Laplacian for random walk.
    
    L = I - D^{-1}A
    
    Eigenvalues in [0, 2], with 0 corresponding to stationary.
    """
    n = adjacency.shape[0]
    degree = np.sum(adjacency, axis=1)
    
    # Normalized Laplacian
    D_inv = np.diag(1.0 / (degree + 1e-10))
    L = np.eye(n) - D_inv @ adjacency
    
    return L


def spectral_gap_from_laplacian(L: NDArray) -> float:
    """Compute spectral gap from Laplacian."""
    eigenvalues = np.sort(np.linalg.eigvalsh(L))
    
    # Second smallest eigenvalue (first is 0)
    if len(eigenvalues) > 1:
        return eigenvalues[1]
    return 0.0


def mixing_time_bound(
    spectral_gap: float,
    n_states: int,
    eps: float = 0.25,
) -> float:
    """
    Compute mixing time bound from spectral gap.
    
    t_mix(ε) ≤ (1/gap) log(n/ε)
    """
    if spectral_gap < 1e-15:
        return float('inf')
    return (1 / spectral_gap) * np.log(n_states / eps)
