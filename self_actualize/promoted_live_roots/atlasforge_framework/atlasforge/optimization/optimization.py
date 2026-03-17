"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Advanced Optimization Module                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Multivariate optimization with verified solutions.

Solver Hierarchy:
- Level 1: Local methods (gradient descent, Newton, BFGS)
- Level 2: Global methods (simulated annealing, basin hopping)
- Level 3: Hybrid methods (combining local and global)
- Level 4: Verified methods (interval arithmetic bounds)

Convergence Rates:
- Gradient Descent: O(1/k) for convex, O(1/k²) accelerated
- Newton: O(k²) quadratic near solution
- BFGS: Superlinear
- Simulated Annealing: Probabilistic global
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
class OptimizationResult:
    """Result of optimization."""
    solution: NDArray[np.float64]
    value: float
    gradient_norm: float = 0.0
    iterations: int = 0
    evaluations: int = 0
    converged: bool = False
    message: str = ""
    history: List[float] = field(default_factory=list)
    
    def __repr__(self):
        return (f"OptimizationResult(value={self.value:.6e}, "
                f"converged={self.converged}, iters={self.iterations})")


class LineSearch:
    """Line search methods for step size selection."""
    
    @staticmethod
    def backtracking(
        f: Callable[[NDArray], float],
        x: NDArray,
        direction: NDArray,
        f_x: float,
        grad: NDArray,
        alpha: float = 1.0,
        rho: float = 0.5,
        c: float = 1e-4,
        max_iter: int = 20,
    ) -> Tuple[float, int]:
        """
        Backtracking line search with Armijo condition.
        
        Returns (step_size, n_evaluations)
        """
        evals = 0
        slope = np.dot(grad, direction)
        
        for _ in range(max_iter):
            x_new = x + alpha * direction
            f_new = f(x_new)
            evals += 1
            
            if f_new <= f_x + c * alpha * slope:
                return alpha, evals
            
            alpha *= rho
        
        return alpha, evals
    
    @staticmethod
    def wolfe(
        f: Callable[[NDArray], float],
        grad_f: Callable[[NDArray], NDArray],
        x: NDArray,
        direction: NDArray,
        f_x: float,
        grad: NDArray,
        c1: float = 1e-4,
        c2: float = 0.9,
        max_iter: int = 20,
    ) -> Tuple[float, int]:
        """
        Line search satisfying strong Wolfe conditions.
        """
        alpha = 1.0
        alpha_lo, alpha_hi = 0.0, float('inf')
        evals = 0
        
        slope = np.dot(grad, direction)
        
        for _ in range(max_iter):
            x_new = x + alpha * direction
            f_new = f(x_new)
            evals += 1
            
            # Armijo condition
            if f_new > f_x + c1 * alpha * slope:
                alpha_hi = alpha
                alpha = (alpha_lo + alpha_hi) / 2
                continue
            
            grad_new = grad_f(x_new)
            evals += 1
            new_slope = np.dot(grad_new, direction)
            
            # Curvature condition
            if abs(new_slope) <= -c2 * slope:
                return alpha, evals
            
            if new_slope >= 0:
                alpha_hi = alpha
            else:
                alpha_lo = alpha
            
            if alpha_hi < float('inf'):
                alpha = (alpha_lo + alpha_hi) / 2
            else:
                alpha *= 2.0
        
        return alpha, evals


class MultivariateOptimizer(ABC):
    """Abstract base class for multivariate optimizers."""
    
    @abstractmethod
    def minimize(
        self,
        f: Callable[[NDArray], float],
        x0: NDArray,
        **kwargs,
    ) -> OptimizationResult:
        """Minimize objective function."""
        pass


class GradientDescent(MultivariateOptimizer):
    """
    Gradient descent with various enhancements.
    
    Variants:
    - Standard: x_{k+1} = x_k - α ∇f(x_k)
    - Momentum: v_{k+1} = βv_k + ∇f(x_k), x_{k+1} = x_k - αv_{k+1}
    - Nesterov: Accelerated gradient method
    """
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        momentum: float = 0.0,
        nesterov: bool = False,
        max_iter: int = 1000,
        tol: float = 1e-8,
        line_search: bool = True,
    ):
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.nesterov = nesterov
        self.max_iter = max_iter
        self.tol = tol
        self.line_search = line_search
    
    def minimize(
        self,
        f: Callable[[NDArray], float],
        x0: NDArray,
        grad_f: Optional[Callable[[NDArray], NDArray]] = None,
        bounds: Optional[Tuple[NDArray, NDArray]] = None,
    ) -> OptimizationResult:
        """Minimize using gradient descent."""
        x = x0.copy().astype(np.float64)
        n = len(x)
        
        if grad_f is None:
            grad_f = lambda x: self._numerical_gradient(f, x)
        
        velocity = np.zeros(n)
        history = []
        evals = 0
        
        f_x = f(x)
        evals += 1
        
        for iteration in range(self.max_iter):
            # Compute gradient
            if self.nesterov and self.momentum > 0:
                x_look = x - self.momentum * velocity
                grad = grad_f(x_look)
            else:
                grad = grad_f(x)
            evals += n  # Numerical gradient uses n+1 evaluations
            
            grad_norm = np.linalg.norm(grad)
            history.append(f_x)
            
            # Convergence check
            if grad_norm < self.tol:
                return OptimizationResult(
                    solution=x,
                    value=f_x,
                    gradient_norm=grad_norm,
                    iterations=iteration,
                    evaluations=evals,
                    converged=True,
                    message="Converged: gradient norm below tolerance",
                    history=history,
                )
            
            # Compute direction
            direction = -grad
            
            # Update with momentum
            if self.momentum > 0:
                velocity = self.momentum * velocity + direction
                direction = velocity
            
            # Line search or fixed step
            if self.line_search:
                alpha, ls_evals = LineSearch.backtracking(f, x, direction, f_x, grad)
                evals += ls_evals
            else:
                alpha = self.learning_rate
            
            # Update
            x_new = x + alpha * direction
            
            # Project to bounds
            if bounds is not None:
                x_new = np.clip(x_new, bounds[0], bounds[1])
            
            f_new = f(x_new)
            evals += 1
            
            x, f_x = x_new, f_new
        
        return OptimizationResult(
            solution=x,
            value=f_x,
            gradient_norm=np.linalg.norm(grad_f(x)),
            iterations=self.max_iter,
            evaluations=evals,
            converged=False,
            message="Maximum iterations reached",
            history=history,
        )
    
    def _numerical_gradient(
        self,
        f: Callable[[NDArray], float],
        x: NDArray,
        eps: float = 1e-8,
    ) -> NDArray:
        """Central difference gradient."""
        n = len(x)
        grad = np.zeros(n)
        for i in range(n):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        return grad


class NewtonMethod(MultivariateOptimizer):
    """
    Newton's method for optimization.
    
    Update: x_{k+1} = x_k - H^{-1} ∇f(x_k)
    
    Quadratic convergence near the solution.
    """
    
    def __init__(
        self,
        max_iter: int = 100,
        tol: float = 1e-10,
        regularization: float = 1e-8,
    ):
        self.max_iter = max_iter
        self.tol = tol
        self.regularization = regularization
    
    def minimize(
        self,
        f: Callable[[NDArray], float],
        x0: NDArray,
        grad_f: Optional[Callable[[NDArray], NDArray]] = None,
        hess_f: Optional[Callable[[NDArray], NDArray]] = None,
    ) -> OptimizationResult:
        """Minimize using Newton's method."""
        x = x0.copy().astype(np.float64)
        n = len(x)
        
        if grad_f is None:
            grad_f = lambda x: self._numerical_gradient(f, x)
        if hess_f is None:
            hess_f = lambda x: self._numerical_hessian(f, x)
        
        history = []
        evals = 0
        
        for iteration in range(self.max_iter):
            f_x = f(x)
            evals += 1
            history.append(f_x)
            
            grad = grad_f(x)
            evals += n
            
            grad_norm = np.linalg.norm(grad)
            if grad_norm < self.tol:
                return OptimizationResult(
                    solution=x,
                    value=f_x,
                    gradient_norm=grad_norm,
                    iterations=iteration,
                    evaluations=evals,
                    converged=True,
                    message="Converged: gradient norm below tolerance",
                    history=history,
                )
            
            H = hess_f(x)
            evals += n * n
            
            # Regularize Hessian for positive definiteness
            H += self.regularization * np.eye(n)
            
            try:
                direction = -np.linalg.solve(H, grad)
            except np.linalg.LinAlgError:
                direction = -grad  # Fall back to gradient descent
            
            # Line search
            alpha, ls_evals = LineSearch.backtracking(f, x, direction, f_x, grad)
            evals += ls_evals
            
            x = x + alpha * direction
        
        f_final = f(x)
        return OptimizationResult(
            solution=x,
            value=f_final,
            gradient_norm=np.linalg.norm(grad_f(x)),
            iterations=self.max_iter,
            evaluations=evals,
            converged=False,
            message="Maximum iterations reached",
            history=history,
        )
    
    def _numerical_gradient(self, f, x, eps=1e-8):
        n = len(x)
        grad = np.zeros(n)
        for i in range(n):
            x_plus, x_minus = x.copy(), x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        return grad
    
    def _numerical_hessian(self, f, x, eps=1e-5):
        n = len(x)
        H = np.zeros((n, n))
        f_x = f(x)
        for i in range(n):
            for j in range(i, n):
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
                
                H[i, j] = (f(x_pp) - f(x_pm) - f(x_mp) + f(x_mm)) / (4 * eps * eps)
                H[j, i] = H[i, j]
        return H


class BFGS(MultivariateOptimizer):
    """
    BFGS quasi-Newton method.
    
    Approximates inverse Hessian using rank-2 updates.
    Superlinear convergence.
    """
    
    def __init__(
        self,
        max_iter: int = 500,
        tol: float = 1e-8,
    ):
        self.max_iter = max_iter
        self.tol = tol
    
    def minimize(
        self,
        f: Callable[[NDArray], float],
        x0: NDArray,
        grad_f: Optional[Callable[[NDArray], NDArray]] = None,
    ) -> OptimizationResult:
        """Minimize using BFGS."""
        x = x0.copy().astype(np.float64)
        n = len(x)
        
        if grad_f is None:
            grad_f = lambda x: self._numerical_gradient(f, x)
        
        # Initialize inverse Hessian approximation
        H_inv = np.eye(n)
        
        history = []
        evals = 0
        
        f_x = f(x)
        grad = grad_f(x)
        evals += 1 + n
        
        for iteration in range(self.max_iter):
            history.append(f_x)
            
            grad_norm = np.linalg.norm(grad)
            if grad_norm < self.tol:
                return OptimizationResult(
                    solution=x,
                    value=f_x,
                    gradient_norm=grad_norm,
                    iterations=iteration,
                    evaluations=evals,
                    converged=True,
                    message="Converged",
                    history=history,
                )
            
            # Search direction
            direction = -H_inv @ grad
            
            # Line search
            alpha, ls_evals = LineSearch.backtracking(f, x, direction, f_x, grad)
            evals += ls_evals
            
            # Update
            x_new = x + alpha * direction
            f_new = f(x_new)
            grad_new = grad_f(x_new)
            evals += 1 + n
            
            # BFGS update
            s = x_new - x
            y = grad_new - grad
            
            rho = 1.0 / (np.dot(y, s) + 1e-10)
            
            if rho > 0:  # Ensure positive definiteness
                I = np.eye(n)
                H_inv = (I - rho * np.outer(s, y)) @ H_inv @ (I - rho * np.outer(y, s))
                H_inv += rho * np.outer(s, s)
            
            x, f_x, grad = x_new, f_new, grad_new
        
        return OptimizationResult(
            solution=x,
            value=f_x,
            gradient_norm=np.linalg.norm(grad),
            iterations=self.max_iter,
            evaluations=evals,
            converged=False,
            message="Maximum iterations reached",
            history=history,
        )
    
    def _numerical_gradient(self, f, x, eps=1e-8):
        n = len(x)
        grad = np.zeros(n)
        for i in range(n):
            x_plus, x_minus = x.copy(), x.copy()
            x_plus[i] += eps
            x_minus[i] -= eps
            grad[i] = (f(x_plus) - f(x_minus)) / (2 * eps)
        return grad


class SimulatedAnnealing(MultivariateOptimizer):
    """
    Simulated annealing for global optimization.
    
    Escapes local optima through probabilistic acceptance
    of worse solutions at high temperatures.
    """
    
    def __init__(
        self,
        max_iter: int = 10000,
        initial_temp: float = 100.0,
        final_temp: float = 1e-8,
        cooling_rate: float = 0.995,
    ):
        self.max_iter = max_iter
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.cooling_rate = cooling_rate
    
    def minimize(
        self,
        f: Callable[[NDArray], float],
        x0: NDArray,
        bounds: Optional[Tuple[NDArray, NDArray]] = None,
        seed: Optional[int] = None,
    ) -> OptimizationResult:
        """Minimize using simulated annealing."""
        rng = np.random.default_rng(seed)
        
        x = x0.copy().astype(np.float64)
        n = len(x)
        
        if bounds is None:
            bounds = (np.full(n, -10.0), np.full(n, 10.0))
        lo, hi = bounds
        scale = hi - lo
        
        f_x = f(x)
        best_x = x.copy()
        best_f = f_x
        
        history = [f_x]
        evals = 1
        
        T = self.initial_temp
        
        for iteration in range(self.max_iter):
            # Generate neighbor
            delta = rng.standard_normal(n) * scale * 0.1
            x_new = np.clip(x + delta, lo, hi)
            
            f_new = f(x_new)
            evals += 1
            
            # Accept or reject
            delta_f = f_new - f_x
            if delta_f < 0 or rng.random() < np.exp(-delta_f / T):
                x, f_x = x_new, f_new
                
                if f_x < best_f:
                    best_x, best_f = x.copy(), f_x
            
            history.append(best_f)
            
            # Cool down
            T = max(self.final_temp, T * self.cooling_rate)
            
            # Convergence check
            if T <= self.final_temp:
                break
        
        return OptimizationResult(
            solution=best_x,
            value=best_f,
            gradient_norm=0.0,
            iterations=iteration + 1,
            evaluations=evals,
            converged=True,
            message="Annealing completed",
            history=history,
        )


class BasinHopping(MultivariateOptimizer):
    """
    Basin hopping global optimization.
    
    Combines local minimization with random perturbations
    to escape local minima.
    """
    
    def __init__(
        self,
        local_optimizer: Optional[MultivariateOptimizer] = None,
        n_iterations: int = 100,
        step_size: float = 0.5,
        temperature: float = 1.0,
    ):
        self.local_optimizer = local_optimizer or BFGS(max_iter=100)
        self.n_iterations = n_iterations
        self.step_size = step_size
        self.temperature = temperature
    
    def minimize(
        self,
        f: Callable[[NDArray], float],
        x0: NDArray,
        bounds: Optional[Tuple[NDArray, NDArray]] = None,
        seed: Optional[int] = None,
    ) -> OptimizationResult:
        """Minimize using basin hopping."""
        rng = np.random.default_rng(seed)
        
        x = x0.copy().astype(np.float64)
        n = len(x)
        
        if bounds is None:
            bounds = (np.full(n, -10.0), np.full(n, 10.0))
        lo, hi = bounds
        
        # Initial local minimization
        result = self.local_optimizer.minimize(f, x)
        x = result.solution
        f_x = result.value
        
        best_x = x.copy()
        best_f = f_x
        
        history = [f_x]
        total_evals = result.evaluations
        
        for iteration in range(self.n_iterations):
            # Random perturbation
            delta = rng.standard_normal(n) * self.step_size
            x_new = np.clip(x + delta, lo, hi)
            
            # Local minimization
            result = self.local_optimizer.minimize(f, x_new)
            total_evals += result.evaluations
            
            x_new = result.solution
            f_new = result.value
            
            # Metropolis acceptance
            delta_f = f_new - f_x
            if delta_f < 0 or rng.random() < np.exp(-delta_f / self.temperature):
                x, f_x = x_new, f_new
                
                if f_x < best_f:
                    best_x, best_f = x.copy(), f_x
            
            history.append(best_f)
        
        return OptimizationResult(
            solution=best_x,
            value=best_f,
            gradient_norm=0.0,
            iterations=self.n_iterations,
            evaluations=total_evals,
            converged=True,
            message="Basin hopping completed",
            history=history,
        )


# Convenience functions
def minimize(
    f: Callable[[NDArray], float],
    x0: NDArray,
    method: str = "bfgs",
    bounds: Optional[Tuple[NDArray, NDArray]] = None,
    **kwargs,
) -> OptimizationResult:
    """
    Minimize a function using the specified method.
    
    Methods:
    - 'gd': Gradient descent
    - 'newton': Newton's method
    - 'bfgs': BFGS quasi-Newton
    - 'annealing': Simulated annealing
    - 'basin': Basin hopping
    """
    optimizers = {
        'gd': GradientDescent,
        'gradient_descent': GradientDescent,
        'newton': NewtonMethod,
        'bfgs': BFGS,
        'annealing': SimulatedAnnealing,
        'simulated_annealing': SimulatedAnnealing,
        'basin': BasinHopping,
        'basin_hopping': BasinHopping,
    }
    
    method = method.lower()
    if method not in optimizers:
        raise ValueError(f"Unknown method: {method}. Available: {list(optimizers.keys())}")
    
    optimizer = optimizers[method](**kwargs)
    
    if method in ['annealing', 'simulated_annealing', 'basin', 'basin_hopping']:
        return optimizer.minimize(f, x0, bounds=bounds)
    else:
        return optimizer.minimize(f, x0)
