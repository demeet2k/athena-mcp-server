"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Multigrid & Multiscale Module                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Implements the Ψ (Psi) pole: Recursive/Hierarchical operators.

Multigrid achieves O(N) complexity for elliptic problems by:
- High-frequency error: damped by local smoothers on fine grid
- Low-frequency error: becomes high-frequency on coarser grid

Key Components:
- V-cycle: Descend once to coarsest, ascend once
- W-cycle: Multiple coarse corrections per level
- F-cycle: Full multigrid with nested iteration
- Prolongation (P): Coarse → Fine (interpolation)
- Restriction (R): Fine → Coarse (averaging/injection)
- Galerkin coarsening: A_c = R A_f P
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


class CycleType(Enum):
    """Multigrid cycle types."""
    V_CYCLE = "v"       # Single descent/ascent
    W_CYCLE = "w"       # Double recursion at each level
    F_CYCLE = "f"       # Full multigrid


class SmootherType(Enum):
    """Smoother types for relaxation."""
    JACOBI = "jacobi"
    GAUSS_SEIDEL = "gauss_seidel"
    SOR = "sor"                     # Successive over-relaxation
    SYMMETRIC_GS = "symmetric_gs"   # Symmetric Gauss-Seidel
    DAMPED_JACOBI = "damped_jacobi"


@dataclass
class MultigridLevel:
    """Represents one level in the multigrid hierarchy."""
    level: int                          # Level index (0 = finest)
    size: int                           # Number of unknowns
    operator: NDArray[np.float64]       # System matrix A_ℓ
    prolongation: Optional[NDArray] = None    # P: coarse → this level
    restriction: Optional[NDArray] = None     # R: this level → coarse
    smoother_matrix: Optional[NDArray] = None # Precomputed smoother
    
    @property
    def is_coarsest(self) -> bool:
        return self.prolongation is None


@dataclass
class MultigridResult:
    """Result of multigrid solve."""
    solution: NDArray[np.float64]
    residual_norm: float
    iterations: int
    convergence_factor: float
    residual_history: List[float] = field(default_factory=list)
    converged: bool = False


class TransferOperator(ABC):
    """Abstract base for grid transfer operators."""
    
    @abstractmethod
    def restrict(self, fine: NDArray) -> NDArray:
        """Restrict from fine to coarse grid."""
        pass
    
    @abstractmethod
    def prolongate(self, coarse: NDArray) -> NDArray:
        """Prolongate from coarse to fine grid."""
        pass


class LinearInterpolation(TransferOperator):
    """
    Linear interpolation for 1D problems.
    
    Fine grid has 2n-1 points, coarse has n points.
    Coarse points align with every other fine point.
    """
    
    def __init__(self, fine_size: int, coarse_size: int):
        self.fine_size = fine_size
        self.coarse_size = coarse_size
        self._build_matrices()
    
    def _build_matrices(self):
        """Build prolongation and restriction matrices."""
        n_f = self.fine_size
        n_c = self.coarse_size
        
        # Prolongation: coarse → fine (injection + interpolation)
        P = np.zeros((n_f, n_c))
        for i in range(n_c):
            # Injection at coincident points
            P[2*i, i] = 1.0
            # Interpolation at intermediate points
            if 2*i + 1 < n_f:
                if i + 1 < n_c:
                    P[2*i + 1, i] = 0.5
                    P[2*i + 1, i + 1] = 0.5
                else:
                    P[2*i + 1, i] = 1.0
        
        self._P = P
        
        # Restriction: fine → coarse (full weighting)
        # R = (1/2) P^T for variational property
        self._R = 0.5 * P.T
    
    def restrict(self, fine: NDArray) -> NDArray:
        return self._R @ fine
    
    def prolongate(self, coarse: NDArray) -> NDArray:
        return self._P @ coarse
    
    @property
    def P(self) -> NDArray:
        return self._P
    
    @property
    def R(self) -> NDArray:
        return self._R


class FullWeighting(TransferOperator):
    """
    Full weighting restriction with linear prolongation.
    
    Standard choice for self-adjoint problems.
    """
    
    def __init__(self, fine_size: int):
        self.fine_size = fine_size
        self.coarse_size = (fine_size + 1) // 2
        self._build_matrices()
    
    def _build_matrices(self):
        n_f = self.fine_size
        n_c = self.coarse_size
        
        # Prolongation (linear interpolation)
        P = np.zeros((n_f, n_c))
        for j in range(n_c):
            i = 2 * j
            if i < n_f:
                P[i, j] = 1.0
            if i - 1 >= 0 and j > 0:
                P[i - 1, j] = 0.5
            if i + 1 < n_f:
                P[i + 1, j] = 0.5
        
        self._P = P
        
        # Full weighting restriction
        R = np.zeros((n_c, n_f))
        for j in range(n_c):
            i = 2 * j
            if i < n_f:
                R[j, i] = 0.5
            if i - 1 >= 0:
                R[j, i - 1] = 0.25
            if i + 1 < n_f:
                R[j, i + 1] = 0.25
        
        self._R = R
    
    def restrict(self, fine: NDArray) -> NDArray:
        return self._R @ fine
    
    def prolongate(self, coarse: NDArray) -> NDArray:
        return self._P @ coarse
    
    @property
    def P(self) -> NDArray:
        return self._P
    
    @property
    def R(self) -> NDArray:
        return self._R


class Smoother(ABC):
    """Abstract base for smoothers."""
    
    @abstractmethod
    def smooth(
        self,
        A: NDArray,
        x: NDArray,
        b: NDArray,
        iterations: int = 1,
    ) -> NDArray:
        """Apply smoothing iterations."""
        pass


class JacobiSmoother(Smoother):
    """
    Weighted Jacobi iteration.
    
    x_{k+1} = x_k + ω D^{-1} (b - A x_k)
    
    Optimal ω = 2/3 for standard discretizations.
    """
    
    def __init__(self, omega: float = 2/3):
        self.omega = omega
    
    def smooth(
        self,
        A: NDArray,
        x: NDArray,
        b: NDArray,
        iterations: int = 1,
    ) -> NDArray:
        D_inv = 1.0 / np.diag(A)
        
        for _ in range(iterations):
            r = b - A @ x
            x = x + self.omega * D_inv * r
        
        return x


class GaussSeidelSmoother(Smoother):
    """
    Gauss-Seidel iteration (forward sweep).
    
    For symmetric problems, use symmetric version.
    """
    
    def __init__(self, symmetric: bool = False):
        self.symmetric = symmetric
    
    def smooth(
        self,
        A: NDArray,
        x: NDArray,
        b: NDArray,
        iterations: int = 1,
    ) -> NDArray:
        n = len(x)
        
        for _ in range(iterations):
            # Forward sweep
            for i in range(n):
                sigma = b[i]
                for j in range(n):
                    if j != i:
                        sigma -= A[i, j] * x[j]
                x[i] = sigma / A[i, i]
            
            # Backward sweep (if symmetric)
            if self.symmetric:
                for i in range(n - 1, -1, -1):
                    sigma = b[i]
                    for j in range(n):
                        if j != i:
                            sigma -= A[i, j] * x[j]
                    x[i] = sigma / A[i, i]
        
        return x


class SORSmoother(Smoother):
    """
    Successive Over-Relaxation.
    
    x_i^{new} = (1-ω)x_i + ω * GS_update
    
    Optimal ω depends on spectral radius.
    """
    
    def __init__(self, omega: float = 1.5):
        self.omega = omega
    
    def smooth(
        self,
        A: NDArray,
        x: NDArray,
        b: NDArray,
        iterations: int = 1,
    ) -> NDArray:
        n = len(x)
        
        for _ in range(iterations):
            for i in range(n):
                sigma = b[i]
                for j in range(n):
                    if j != i:
                        sigma -= A[i, j] * x[j]
                gs_update = sigma / A[i, i]
                x[i] = (1 - self.omega) * x[i] + self.omega * gs_update
        
        return x


class MultigridHierarchy:
    """
    Complete multigrid hierarchy with all levels.
    """
    
    def __init__(
        self,
        A: NDArray[np.float64],
        n_levels: int = 0,
        coarsening_factor: int = 2,
    ):
        """
        Build multigrid hierarchy.
        
        Args:
            A: Fine grid operator
            n_levels: Number of levels (0 = automatic)
            coarsening_factor: Size reduction per level
        """
        self.levels: List[MultigridLevel] = []
        self._build_hierarchy(A, n_levels, coarsening_factor)
    
    def _build_hierarchy(
        self,
        A: NDArray,
        n_levels: int,
        coarsening_factor: int,
    ):
        """Build the complete hierarchy."""
        n = A.shape[0]
        
        # Determine number of levels
        if n_levels <= 0:
            n_levels = max(1, int(np.log2(n)) - 2)
        
        # Finest level
        self.levels.append(MultigridLevel(
            level=0,
            size=n,
            operator=A.copy(),
        ))
        
        current_A = A
        current_size = n
        
        for ell in range(1, n_levels):
            # Compute coarse size
            coarse_size = max(2, current_size // coarsening_factor)
            
            if coarse_size < 2:
                break
            
            # Build transfer operators
            transfer = FullWeighting(current_size)
            
            # Galerkin coarsening: A_c = R A_f P
            P = transfer.P[:current_size, :coarse_size]
            R = transfer.R[:coarse_size, :current_size]
            coarse_A = R @ current_A @ P
            
            # Store level
            level = MultigridLevel(
                level=ell,
                size=coarse_size,
                operator=coarse_A,
                prolongation=P,
                restriction=R,
            )
            self.levels.append(level)
            
            # Update for next level
            self.levels[ell - 1].prolongation = P
            self.levels[ell - 1].restriction = R
            
            current_A = coarse_A
            current_size = coarse_size
    
    @property
    def n_levels(self) -> int:
        return len(self.levels)
    
    @property
    def finest(self) -> MultigridLevel:
        return self.levels[0]
    
    @property
    def coarsest(self) -> MultigridLevel:
        return self.levels[-1]


class MultigridSolver:
    """
    Multigrid solver implementing V-cycle, W-cycle, and F-cycle.
    
    This is the core Ψ operator implementation.
    
    Usage:
        hierarchy = MultigridHierarchy(A)
        solver = MultigridSolver(hierarchy)
        result = solver.solve(b, x0)
    """
    
    def __init__(
        self,
        hierarchy: MultigridHierarchy,
        cycle_type: CycleType = CycleType.V_CYCLE,
        smoother: Optional[Smoother] = None,
        pre_smoothing: int = 2,
        post_smoothing: int = 2,
        max_iterations: int = 100,
        tol: float = 1e-10,
    ):
        self.hierarchy = hierarchy
        self.cycle_type = cycle_type
        self.smoother = smoother or JacobiSmoother(omega=2/3)
        self.pre_smoothing = pre_smoothing
        self.post_smoothing = post_smoothing
        self.max_iterations = max_iterations
        self.tol = tol
    
    def solve(
        self,
        b: NDArray[np.float64],
        x0: Optional[NDArray[np.float64]] = None,
    ) -> MultigridResult:
        """
        Solve Ax = b using multigrid.
        """
        n = self.hierarchy.finest.size
        x = x0.copy() if x0 is not None else np.zeros(n)
        
        A = self.hierarchy.finest.operator
        
        residual_history = []
        r0_norm = np.linalg.norm(b - A @ x)
        residual_history.append(r0_norm)
        
        for iteration in range(self.max_iterations):
            # Apply one multigrid cycle
            x = self._cycle(0, x, b)
            
            # Check convergence
            r_norm = np.linalg.norm(b - A @ x)
            residual_history.append(r_norm)
            
            if r_norm < self.tol * r0_norm or r_norm < 1e-15:
                return MultigridResult(
                    solution=x,
                    residual_norm=r_norm,
                    iterations=iteration + 1,
                    convergence_factor=r_norm / r0_norm if r0_norm > 0 else 0,
                    residual_history=residual_history,
                    converged=True,
                )
        
        # Compute convergence factor
        if len(residual_history) > 1:
            conv_factor = (residual_history[-1] / residual_history[0]) ** (1 / len(residual_history))
        else:
            conv_factor = 1.0
        
        return MultigridResult(
            solution=x,
            residual_norm=residual_history[-1],
            iterations=self.max_iterations,
            convergence_factor=conv_factor,
            residual_history=residual_history,
            converged=False,
        )
    
    def _cycle(
        self,
        level: int,
        x: NDArray,
        b: NDArray,
    ) -> NDArray:
        """Apply one multigrid cycle at given level."""
        hierarchy = self.hierarchy
        current = hierarchy.levels[level]
        A = current.operator
        
        # Coarsest level: direct solve
        if level == hierarchy.n_levels - 1:
            try:
                return np.linalg.solve(A, b)
            except np.linalg.LinAlgError:
                return np.linalg.lstsq(A, b, rcond=None)[0]
        
        # Pre-smoothing
        x = self.smoother.smooth(A, x, b, self.pre_smoothing)
        
        # Compute residual
        r = b - A @ x
        
        # Restrict residual to coarse grid
        R = current.restriction
        r_coarse = R @ r
        
        # Coarse grid correction
        coarse_size = hierarchy.levels[level + 1].size
        e_coarse = np.zeros(coarse_size)
        
        # Number of coarse grid cycles
        n_cycles = 1 if self.cycle_type == CycleType.V_CYCLE else 2
        
        for _ in range(n_cycles):
            e_coarse = self._cycle(level + 1, e_coarse, r_coarse)
        
        # Prolongate correction
        P = current.prolongation
        e = P @ e_coarse
        
        # Apply correction
        x = x + e
        
        # Post-smoothing
        x = self.smoother.smooth(A, x, b, self.post_smoothing)
        
        return x
    
    def estimate_convergence_factor(
        self,
        n_iterations: int = 10,
    ) -> float:
        """Estimate asymptotic convergence factor."""
        n = self.hierarchy.finest.size
        A = self.hierarchy.finest.operator
        
        # Random initial guess and RHS
        x = np.random.randn(n)
        b = A @ np.random.randn(n)
        
        norms = []
        for _ in range(n_iterations):
            x = self._cycle(0, x, b)
            norms.append(np.linalg.norm(b - A @ x))
        
        if len(norms) > 1 and norms[0] > 1e-15:
            return (norms[-1] / norms[0]) ** (1 / len(norms))
        return 1.0


class MultigridPreconditioner:
    """
    Use multigrid as a preconditioner for iterative methods.
    
    For conjugate gradient: M^{-1} ≈ one V-cycle
    """
    
    def __init__(
        self,
        hierarchy: MultigridHierarchy,
        n_cycles: int = 1,
    ):
        self.solver = MultigridSolver(
            hierarchy,
            cycle_type=CycleType.V_CYCLE,
            pre_smoothing=1,
            post_smoothing=1,
        )
        self.n_cycles = n_cycles
    
    def apply(self, r: NDArray) -> NDArray:
        """Apply preconditioner: M^{-1} r."""
        x = np.zeros_like(r)
        for _ in range(self.n_cycles):
            x = self.solver._cycle(0, x, r)
        return x


def create_1d_laplacian(n: int, h: float = 1.0) -> NDArray[np.float64]:
    """Create 1D discrete Laplacian matrix."""
    A = np.zeros((n, n))
    for i in range(n):
        A[i, i] = 2.0 / (h * h)
        if i > 0:
            A[i, i-1] = -1.0 / (h * h)
        if i < n - 1:
            A[i, i+1] = -1.0 / (h * h)
    return A


def create_2d_laplacian(n: int, h: float = 1.0) -> NDArray[np.float64]:
    """Create 2D discrete Laplacian matrix (5-point stencil)."""
    N = n * n
    A = np.zeros((N, N))
    
    for i in range(n):
        for j in range(n):
            idx = i * n + j
            A[idx, idx] = 4.0 / (h * h)
            
            if i > 0:
                A[idx, idx - n] = -1.0 / (h * h)
            if i < n - 1:
                A[idx, idx + n] = -1.0 / (h * h)
            if j > 0:
                A[idx, idx - 1] = -1.0 / (h * h)
            if j < n - 1:
                A[idx, idx + 1] = -1.0 / (h * h)
    
    return A


# Convenience function
def multigrid_solve(
    A: NDArray[np.float64],
    b: NDArray[np.float64],
    x0: Optional[NDArray[np.float64]] = None,
    tol: float = 1e-10,
    max_iter: int = 100,
    cycle: str = "v",
) -> MultigridResult:
    """
    Solve Ax = b using multigrid.
    
    Example:
        A = create_1d_laplacian(100)
        b = np.ones(100)
        result = multigrid_solve(A, b)
        print(f"Converged: {result.converged}, iters: {result.iterations}")
    """
    hierarchy = MultigridHierarchy(A)
    
    cycle_map = {
        'v': CycleType.V_CYCLE,
        'w': CycleType.W_CYCLE,
        'f': CycleType.F_CYCLE,
    }
    
    solver = MultigridSolver(
        hierarchy,
        cycle_type=cycle_map.get(cycle.lower(), CycleType.V_CYCLE),
        max_iterations=max_iter,
        tol=tol,
    )
    
    return solver.solve(b, x0)
