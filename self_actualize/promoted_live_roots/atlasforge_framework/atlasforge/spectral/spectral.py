"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Spectral Analysis Module                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Spectral properties control:
- Convergence rates (spectral gap)
- Mixing times (for Markov chains)
- Condition numbers (for linear systems)
- Stability (eigenvalue distribution)

Key Concepts:
- Spectral Gap: λ₂ - λ₁ (gap between first two eigenvalues)
- Mixing Time: t_mix(ε) = time to reach ε-close to equilibrium
- Condition Number: κ = λ_max / λ_min
- Spectral Radius: ρ(A) = max|λ_i|

Convergence Rates:
- Gradient descent: O(κ) iterations
- Accelerated (Nesterov): O(√κ) iterations  
- Conjugate gradient: O(√κ) iterations
- Multigrid: O(1) iterations (independent of N!)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


@dataclass
class SpectralDecomposition:
    """Complete spectral decomposition of an operator."""
    eigenvalues: NDArray[np.float64]
    eigenvectors: NDArray[np.float64]
    is_symmetric: bool = False
    is_positive_definite: bool = False
    
    @property
    def n(self) -> int:
        return len(self.eigenvalues)
    
    @property
    def spectral_gap(self) -> float:
        """Gap between smallest and second-smallest eigenvalues."""
        if self.n < 2:
            return 0.0
        sorted_eigs = np.sort(np.abs(self.eigenvalues))
        return sorted_eigs[1] - sorted_eigs[0]
    
    @property
    def normalized_spectral_gap(self) -> float:
        """Spectral gap normalized by spectral range."""
        if self.n < 2:
            return 0.0
        sorted_eigs = np.sort(np.abs(self.eigenvalues))
        range_val = sorted_eigs[-1] - sorted_eigs[0]
        if range_val < 1e-15:
            return 0.0
        return (sorted_eigs[1] - sorted_eigs[0]) / range_val
    
    @property
    def condition_number(self) -> float:
        """Condition number κ = λ_max / λ_min."""
        abs_eigs = np.abs(self.eigenvalues)
        min_eig = np.min(abs_eigs[abs_eigs > 1e-15])
        max_eig = np.max(abs_eigs)
        return max_eig / min_eig if min_eig > 0 else float('inf')
    
    @property
    def spectral_radius(self) -> float:
        """Spectral radius ρ(A) = max|λ|."""
        return np.max(np.abs(self.eigenvalues))
    
    @property
    def effective_rank(self) -> int:
        """Number of significant eigenvalues."""
        threshold = self.spectral_radius * 1e-10
        return int(np.sum(np.abs(self.eigenvalues) > threshold))
    
    def energy_distribution(self) -> NDArray[np.float64]:
        """Distribution of energy across modes."""
        abs_eigs = np.abs(self.eigenvalues)
        total = np.sum(abs_eigs)
        if total < 1e-15:
            return np.zeros(self.n)
        return abs_eigs / total
    
    def mode_contribution(self, vector: NDArray) -> NDArray[np.float64]:
        """Decompose vector into modal contributions."""
        if self.is_symmetric:
            # For symmetric matrices, eigenvectors are orthonormal
            return np.abs(self.eigenvectors.T @ vector) ** 2
        else:
            # General case: use least squares
            coeffs = np.linalg.lstsq(self.eigenvectors, vector, rcond=None)[0]
            return np.abs(coeffs) ** 2


@dataclass
class MixingAnalysis:
    """Analysis of mixing properties for Markov chains."""
    transition_matrix: NDArray[np.float64]
    stationary_distribution: NDArray[np.float64]
    spectral_gap: float
    mixing_time_bound: float
    relaxation_time: float
    second_eigenvalue: float
    
    @property
    def is_reversible(self) -> bool:
        """Check if chain satisfies detailed balance."""
        P = self.transition_matrix
        pi = self.stationary_distribution
        n = len(pi)
        
        for i in range(n):
            for j in range(n):
                if abs(pi[i] * P[i, j] - pi[j] * P[j, i]) > 1e-10:
                    return False
        return True


@dataclass
class ConvergenceRate:
    """Convergence rate analysis for iterative methods."""
    
    method: str
    rate_type: str              # "linear", "quadratic", "superlinear"
    asymptotic_factor: float    # ρ for linear: x_{k+1} ≤ ρ x_k
    iterations_to_eps: int      # Iterations to reach ε accuracy
    complexity_per_iter: str    # O(n), O(n²), etc.
    total_complexity: str       # Total work
    
    def __repr__(self):
        return (f"ConvergenceRate({self.method}: {self.rate_type}, "
                f"factor={self.asymptotic_factor:.4f}, "
                f"iters={self.iterations_to_eps})")


class SpectralAnalyzer:
    """
    Comprehensive spectral analysis for operators.
    
    Provides:
    - Eigenvalue decomposition
    - Convergence rate estimation
    - Mixing time analysis
    - Condition number computation
    """
    
    def __init__(self, tol: float = 1e-12):
        self.tol = tol
    
    def decompose(self, A: NDArray[np.float64]) -> SpectralDecomposition:
        """Compute full spectral decomposition."""
        n = A.shape[0]
        
        # Check symmetry
        is_symmetric = np.allclose(A, A.T, rtol=1e-10)
        
        if is_symmetric:
            eigenvalues, eigenvectors = np.linalg.eigh(A)
        else:
            eigenvalues, eigenvectors = np.linalg.eig(A)
            # Sort by magnitude
            idx = np.argsort(np.abs(eigenvalues))
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]
        
        # Check positive definiteness
        is_pd = is_symmetric and np.all(eigenvalues > -1e-10)
        
        return SpectralDecomposition(
            eigenvalues=np.real(eigenvalues) if is_symmetric else eigenvalues,
            eigenvectors=eigenvectors,
            is_symmetric=is_symmetric,
            is_positive_definite=is_pd,
        )
    
    def analyze_convergence(
        self,
        A: NDArray[np.float64],
        method: str = "gradient_descent",
        target_eps: float = 1e-8,
    ) -> ConvergenceRate:
        """
        Analyze convergence rate for solving Ax = b.
        
        Methods:
        - gradient_descent: O(κ log(1/ε)) iterations
        - accelerated_gd: O(√κ log(1/ε)) iterations
        - conjugate_gradient: O(√κ log(1/ε)) iterations
        - jacobi: O(ρ^k) where ρ = spectral radius of iteration matrix
        - gauss_seidel: Similar to Jacobi but often faster
        """
        decomp = self.decompose(A)
        kappa = decomp.condition_number
        n = decomp.n
        
        if method == "gradient_descent":
            # Rate: (κ-1)/(κ+1) per iteration
            factor = (kappa - 1) / (kappa + 1) if kappa > 1 else 0
            iters = int(np.ceil(kappa * np.log(1 / target_eps)))
            return ConvergenceRate(
                method="Gradient Descent",
                rate_type="linear",
                asymptotic_factor=factor,
                iterations_to_eps=iters,
                complexity_per_iter="O(n²)",
                total_complexity=f"O(κ n² log(1/ε)) = O({kappa:.0f} n²)",
            )
        
        elif method == "accelerated_gd" or method == "nesterov":
            # Rate: (√κ-1)/(√κ+1) per iteration
            sqrt_kappa = np.sqrt(kappa)
            factor = (sqrt_kappa - 1) / (sqrt_kappa + 1)
            iters = int(np.ceil(sqrt_kappa * np.log(1 / target_eps)))
            return ConvergenceRate(
                method="Accelerated GD (Nesterov)",
                rate_type="linear (accelerated)",
                asymptotic_factor=factor,
                iterations_to_eps=iters,
                complexity_per_iter="O(n²)",
                total_complexity=f"O(√κ n² log(1/ε)) = O({sqrt_kappa:.0f} n²)",
            )
        
        elif method == "conjugate_gradient":
            sqrt_kappa = np.sqrt(kappa)
            factor = (sqrt_kappa - 1) / (sqrt_kappa + 1)
            iters = int(np.ceil(sqrt_kappa * np.log(2 / target_eps)))
            return ConvergenceRate(
                method="Conjugate Gradient",
                rate_type="linear (CG)",
                asymptotic_factor=factor,
                iterations_to_eps=iters,
                complexity_per_iter="O(nnz)",  # Sparse matrix-vector
                total_complexity=f"O(√κ nnz log(1/ε))",
            )
        
        elif method == "jacobi":
            # Iteration matrix: D^{-1}(L+U)
            D = np.diag(np.diag(A))
            R = A - D
            D_inv = np.diag(1.0 / np.diag(A))
            T_j = D_inv @ R
            rho = np.max(np.abs(np.linalg.eigvals(T_j)))
            
            if rho >= 1:
                iters = -1  # Does not converge
            else:
                iters = int(np.ceil(np.log(target_eps) / np.log(rho)))
            
            return ConvergenceRate(
                method="Jacobi",
                rate_type="linear",
                asymptotic_factor=rho,
                iterations_to_eps=max(0, iters),
                complexity_per_iter="O(n²)",
                total_complexity=f"O(n² log(1/ε) / log(1/ρ))",
            )
        
        elif method == "multigrid":
            # Multigrid: O(N) work total, ~constant iterations
            return ConvergenceRate(
                method="Multigrid (V-cycle)",
                rate_type="constant",
                asymptotic_factor=0.1,  # Typical for good MG
                iterations_to_eps=int(np.ceil(np.log(1/target_eps) / np.log(10))),
                complexity_per_iter="O(n)",
                total_complexity="O(n log(1/ε))",
            )
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def analyze_mixing(
        self,
        P: NDArray[np.float64],
    ) -> MixingAnalysis:
        """
        Analyze mixing properties of a Markov transition matrix.
        
        Args:
            P: Row-stochastic transition matrix (P_{ij} = Pr(j|i))
        
        Returns:
            MixingAnalysis with spectral gap, mixing time, etc.
        """
        n = P.shape[0]
        
        # Find stationary distribution (left eigenvector for eigenvalue 1)
        eigenvalues, left_eigenvectors = np.linalg.eig(P.T)
        
        # Find eigenvalue closest to 1
        idx_stationary = np.argmin(np.abs(eigenvalues - 1))
        pi = np.real(left_eigenvectors[:, idx_stationary])
        pi = pi / np.sum(pi)  # Normalize
        
        # Sort eigenvalues by magnitude
        sorted_eigs = np.sort(np.abs(eigenvalues))[::-1]
        
        # Second largest eigenvalue
        lambda_2 = sorted_eigs[1] if len(sorted_eigs) > 1 else 0
        
        # Spectral gap
        gap = 1 - lambda_2
        
        # Relaxation time
        if gap > 1e-15:
            relaxation_time = 1.0 / gap
        else:
            relaxation_time = float('inf')
        
        # Mixing time bound: t_mix(ε) ≤ (1/gap) log(1/(ε π_min))
        pi_min = np.min(pi[pi > 1e-15])
        if gap > 1e-15:
            eps = 0.25  # Standard ε for mixing time
            mixing_bound = relaxation_time * np.log(1 / (eps * pi_min))
        else:
            mixing_bound = float('inf')
        
        return MixingAnalysis(
            transition_matrix=P,
            stationary_distribution=pi,
            spectral_gap=gap,
            mixing_time_bound=mixing_bound,
            relaxation_time=relaxation_time,
            second_eigenvalue=lambda_2,
        )
    
    def compare_methods(
        self,
        A: NDArray[np.float64],
        target_eps: float = 1e-8,
    ) -> Dict[str, ConvergenceRate]:
        """Compare convergence rates of multiple methods."""
        methods = [
            "gradient_descent",
            "accelerated_gd", 
            "conjugate_gradient",
            "jacobi",
            "multigrid",
        ]
        
        results = {}
        for method in methods:
            try:
                results[method] = self.analyze_convergence(A, method, target_eps)
            except Exception:
                pass
        
        return results


def spectral_gap(A: NDArray) -> float:
    """Compute spectral gap of matrix A."""
    analyzer = SpectralAnalyzer()
    decomp = analyzer.decompose(A)
    return decomp.spectral_gap


def condition_number(A: NDArray) -> float:
    """Compute condition number of matrix A."""
    analyzer = SpectralAnalyzer()
    decomp = analyzer.decompose(A)
    return decomp.condition_number


def mixing_time(P: NDArray, eps: float = 0.25) -> float:
    """Estimate mixing time of Markov chain."""
    analyzer = SpectralAnalyzer()
    analysis = analyzer.analyze_mixing(P)
    return analysis.mixing_time_bound


def estimate_convergence_factor(A: NDArray, method: str = "gd") -> float:
    """Estimate per-iteration convergence factor."""
    analyzer = SpectralAnalyzer()
    rate = analyzer.analyze_convergence(A, method)
    return rate.asymptotic_factor


@dataclass
class ShortcutFactor:
    """
    Quantifies algorithmic shortcut improvement.
    
    Shortcut factor S = C_baseline / C_hybrid
    where C is cost (iterations, time, or operations).
    """
    baseline_method: str
    hybrid_method: str
    baseline_iterations: int
    hybrid_iterations: int
    speedup_factor: float
    complexity_improvement: str
    
    def __repr__(self):
        return (f"ShortcutFactor({self.baseline_method} → {self.hybrid_method}: "
                f"{self.speedup_factor:.2f}x speedup)")


def compute_shortcut_factor(
    A: NDArray,
    baseline: str = "gradient_descent",
    hybrid: str = "conjugate_gradient",
    target_eps: float = 1e-8,
) -> ShortcutFactor:
    """
    Compute the shortcut factor when moving from baseline to hybrid method.
    
    Based on the quad-polar framework definition:
    A hybrid has ε-shortcut factor S(ε) if
    C_hybrid(P, ε) ≤ C_baseline(P, ε) / S(ε)
    """
    analyzer = SpectralAnalyzer()
    
    baseline_rate = analyzer.analyze_convergence(A, baseline, target_eps)
    hybrid_rate = analyzer.analyze_convergence(A, hybrid, target_eps)
    
    if hybrid_rate.iterations_to_eps > 0:
        speedup = baseline_rate.iterations_to_eps / hybrid_rate.iterations_to_eps
    else:
        speedup = float('inf')
    
    # Determine complexity improvement
    kappa = condition_number(A)
    if baseline == "gradient_descent" and hybrid in ["accelerated_gd", "conjugate_gradient"]:
        improvement = f"O(κ) → O(√κ), κ={kappa:.0f}: {np.sqrt(kappa):.1f}x"
    elif hybrid == "multigrid":
        improvement = f"O(√κ n²) → O(n log(1/ε)): {np.sqrt(kappa):.0f}x"
    else:
        improvement = f"{baseline_rate.iterations_to_eps} → {hybrid_rate.iterations_to_eps} iterations"
    
    return ShortcutFactor(
        baseline_method=baseline,
        hybrid_method=hybrid,
        baseline_iterations=baseline_rate.iterations_to_eps,
        hybrid_iterations=hybrid_rate.iterations_to_eps,
        speedup_factor=speedup,
        complexity_improvement=improvement,
    )
