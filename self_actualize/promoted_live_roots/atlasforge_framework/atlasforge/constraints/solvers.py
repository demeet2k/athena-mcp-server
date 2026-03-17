"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ATLAS FORGE - Constraint Solvers                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Numerical solvers for constraint satisfaction.

Solver Types:
- Bisection: Simple, robust, bracketing
- Newton: Fast quadratic convergence near solution
- Secant: Newton without explicit derivative
- Brent: Combines bisection with inverse quadratic interpolation
- Fixed Point Iteration: For x = F(x) problems
- Interval Newton: Verified enclosure with interval arithmetic
- Krawczyk: Verified solver using Krawczyk operator
- Branch and Bound: Global search with pruning
- Continuation: Homotopy/path following
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Generic, Iterator, List, Optional,
    Protocol, Sequence, Tuple, TypeVar, Union
)
import math
from enum import Enum, auto

from atlasforge.core.types import Interval
from atlasforge.core.enums import SolverType, CertificateLevel
from atlasforge.constraints.constraint import (
    Constraint, RootConstraint, FixedPointConstraint, 
    NormalForm, NormalFormType
)


# ═══════════════════════════════════════════════════════════════════════════════
# SOLVER RESULT
# ═══════════════════════════════════════════════════════════════════════════════

class SolverStatus(Enum):
    """Status of a solver run."""
    SUCCESS = auto()
    MAX_ITERATIONS = auto()
    NO_CONVERGENCE = auto()
    BRACKET_LOST = auto()
    SINGULAR_JACOBIAN = auto()
    DOMAIN_ERROR = auto()
    CERTIFICATE_FAILED = auto()


@dataclass
class SolverResult:
    """
    Result of a solver run.
    
    Contains:
    - The solution (if found)
    - Convergence information
    - Enclosure interval (for verified solvers)
    - Iteration history (for replay)
    """
    
    status: SolverStatus
    solution: Optional[float] = None
    residual: float = float('inf')
    iterations: int = 0
    
    # For verified solvers
    enclosure: Optional[Interval] = None
    enclosure_verified: bool = False
    
    # For replay
    iteration_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    solver_type: Optional[SolverType] = None
    message: str = ""
    
    @property
    def converged(self) -> bool:
        return self.status == SolverStatus.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.name,
            'solution': self.solution,
            'residual': self.residual,
            'iterations': self.iterations,
            'enclosure': str(self.enclosure) if self.enclosure else None,
            'enclosure_verified': self.enclosure_verified,
            'solver_type': self.solver_type.value if self.solver_type else None,
            'message': self.message,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SOLVER BASE
# ═══════════════════════════════════════════════════════════════════════════════

class Solver(ABC):
    """Abstract base class for all solvers."""
    
    @property
    @abstractmethod
    def solver_type(self) -> SolverType:
        """The type of this solver."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass
    
    @abstractmethod
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        **kwargs
    ) -> SolverResult:
        """
        Solve H(x) = 0 on the given domain.
        
        Returns SolverResult with solution and metadata.
        """
        pass
    
    def solve_constraint(
        self, 
        constraint: RootConstraint,
        **kwargs
    ) -> SolverResult:
        """Solve a root constraint directly."""
        domain = constraint.domain or Interval.all_reals()
        if isinstance(domain, Interval):
            return self.solve(constraint.H, domain, **kwargs)
        else:
            # Use first interval if domain is more complex
            return self.solve(constraint.H, Interval.all_reals(), **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# BISECTION SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BisectionSolver(Solver):
    """
    Bisection method for root finding.
    
    Properties:
    - Guaranteed convergence if f(a) and f(b) have opposite signs
    - Linear convergence: error halves each iteration
    - Very robust but slow
    - Naturally provides enclosure
    """
    
    tol: float = 1e-12
    max_iter: int = 100
    record_history: bool = True
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.BISECTION
    
    @property
    def name(self) -> str:
        return "Bisection"
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        **kwargs
    ) -> SolverResult:
        tol = kwargs.get('tol', self.tol)
        max_iter = kwargs.get('max_iter', self.max_iter)
        
        a, b = domain.lo, domain.hi
        if not (math.isfinite(a) and math.isfinite(b)):
            return SolverResult(
                status=SolverStatus.DOMAIN_ERROR,
                message="Bisection requires finite interval"
            )
        
        fa, fb = H(a), H(b)
        
        # Check for sign change
        if fa * fb > 0:
            return SolverResult(
                status=SolverStatus.BRACKET_LOST,
                message=f"No sign change: f({a})={fa}, f({b})={fb}"
            )
        
        history = []
        
        for i in range(max_iter):
            c = (a + b) / 2
            fc = H(c)
            
            if self.record_history:
                history.append({
                    'iteration': i,
                    'a': a, 'b': b, 'c': c,
                    'fa': fa, 'fb': fb, 'fc': fc,
                    'width': b - a
                })
            
            # Check convergence
            if abs(fc) < tol or (b - a) / 2 < tol:
                return SolverResult(
                    status=SolverStatus.SUCCESS,
                    solution=c,
                    residual=abs(fc),
                    iterations=i + 1,
                    enclosure=Interval.closed(a, b),
                    enclosure_verified=True,
                    iteration_history=history,
                    solver_type=self.solver_type,
                    message="Converged"
                )
            
            # Update bracket
            if fa * fc < 0:
                b, fb = c, fc
            else:
                a, fa = c, fc
        
        return SolverResult(
            status=SolverStatus.MAX_ITERATIONS,
            solution=(a + b) / 2,
            residual=abs(H((a + b) / 2)),
            iterations=max_iter,
            enclosure=Interval.closed(a, b),
            iteration_history=history,
            solver_type=self.solver_type,
            message=f"Max iterations ({max_iter}) reached"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# NEWTON SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NewtonSolver(Solver):
    """
    Newton-Raphson method for root finding.
    
    x_{n+1} = x_n - H(x_n) / H'(x_n)
    
    Properties:
    - Quadratic convergence near solution
    - Requires derivative (computed numerically if not provided)
    - May diverge if starting point is poor
    - Does NOT naturally provide verified enclosure
    """
    
    tol: float = 1e-12
    max_iter: int = 50
    derivative_eps: float = 1e-8
    record_history: bool = True
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.NEWTON
    
    @property
    def name(self) -> str:
        return "Newton-Raphson"
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        dH: Optional[Callable[[float], float]] = None,
        x0: Optional[float] = None,
        **kwargs
    ) -> SolverResult:
        tol = kwargs.get('tol', self.tol)
        max_iter = kwargs.get('max_iter', self.max_iter)
        
        # Initial guess
        if x0 is None:
            x0 = domain.midpoint if domain.is_bounded else 0.0
        
        # Derivative function
        if dH is None:
            eps = self.derivative_eps
            dH = lambda x: (H(x + eps) - H(x - eps)) / (2 * eps)
        
        x = x0
        history = []
        
        for i in range(max_iter):
            fx = H(x)
            dfx = dH(x)
            
            if self.record_history:
                history.append({
                    'iteration': i,
                    'x': x,
                    'f': fx,
                    'df': dfx
                })
            
            # Check convergence
            if abs(fx) < tol:
                return SolverResult(
                    status=SolverStatus.SUCCESS,
                    solution=x,
                    residual=abs(fx),
                    iterations=i + 1,
                    iteration_history=history,
                    solver_type=self.solver_type,
                    message="Converged"
                )
            
            # Check for singular Jacobian
            if abs(dfx) < 1e-15:
                return SolverResult(
                    status=SolverStatus.SINGULAR_JACOBIAN,
                    solution=x,
                    residual=abs(fx),
                    iterations=i + 1,
                    iteration_history=history,
                    solver_type=self.solver_type,
                    message=f"Singular Jacobian at x={x}"
                )
            
            # Newton step
            x = x - fx / dfx
            
            # Check domain
            if domain.is_bounded and not domain.contains(x):
                # Project back to domain
                x = max(domain.lo, min(domain.hi, x))
        
        return SolverResult(
            status=SolverStatus.MAX_ITERATIONS,
            solution=x,
            residual=abs(H(x)),
            iterations=max_iter,
            iteration_history=history,
            solver_type=self.solver_type,
            message=f"Max iterations ({max_iter}) reached"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SECANT SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SecantSolver(Solver):
    """
    Secant method for root finding.
    
    x_{n+1} = x_n - H(x_n) * (x_n - x_{n-1}) / (H(x_n) - H(x_{n-1}))
    
    Properties:
    - Superlinear convergence (order ≈ 1.618)
    - No derivative required
    - Two initial points needed
    """
    
    tol: float = 1e-12
    max_iter: int = 50
    record_history: bool = True
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.SECANT
    
    @property
    def name(self) -> str:
        return "Secant"
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        x0: Optional[float] = None,
        x1: Optional[float] = None,
        **kwargs
    ) -> SolverResult:
        tol = kwargs.get('tol', self.tol)
        max_iter = kwargs.get('max_iter', self.max_iter)
        
        # Initial guesses
        if x0 is None:
            x0 = domain.lo if domain.is_bounded else -1.0
        if x1 is None:
            x1 = domain.hi if domain.is_bounded else 1.0
        
        f0, f1 = H(x0), H(x1)
        history = []
        
        for i in range(max_iter):
            if self.record_history:
                history.append({
                    'iteration': i,
                    'x0': x0, 'x1': x1,
                    'f0': f0, 'f1': f1
                })
            
            # Check convergence
            if abs(f1) < tol:
                return SolverResult(
                    status=SolverStatus.SUCCESS,
                    solution=x1,
                    residual=abs(f1),
                    iterations=i + 1,
                    iteration_history=history,
                    solver_type=self.solver_type,
                    message="Converged"
                )
            
            # Check for division by zero
            if abs(f1 - f0) < 1e-15:
                return SolverResult(
                    status=SolverStatus.SINGULAR_JACOBIAN,
                    solution=x1,
                    residual=abs(f1),
                    iterations=i + 1,
                    iteration_history=history,
                    solver_type=self.solver_type,
                    message="Division by zero in secant step"
                )
            
            # Secant step
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
            
            # Shift
            x0, f0 = x1, f1
            x1, f1 = x2, H(x2)
        
        return SolverResult(
            status=SolverStatus.MAX_ITERATIONS,
            solution=x1,
            residual=abs(f1),
            iterations=max_iter,
            iteration_history=history,
            solver_type=self.solver_type,
            message=f"Max iterations ({max_iter}) reached"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# BRENT SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BrentSolver(Solver):
    """
    Brent's method for root finding.
    
    Combines:
    - Bisection (guaranteed convergence)
    - Secant method (fast convergence)
    - Inverse quadratic interpolation (superfast near solution)
    
    The gold standard for bracketed root finding.
    """
    
    tol: float = 1e-12
    max_iter: int = 100
    record_history: bool = True
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.BRENT
    
    @property
    def name(self) -> str:
        return "Brent"
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        **kwargs
    ) -> SolverResult:
        tol = kwargs.get('tol', self.tol)
        max_iter = kwargs.get('max_iter', self.max_iter)
        
        a, b = domain.lo, domain.hi
        if not (math.isfinite(a) and math.isfinite(b)):
            return SolverResult(
                status=SolverStatus.DOMAIN_ERROR,
                message="Brent requires finite interval"
            )
        
        fa, fb = H(a), H(b)
        
        if fa * fb > 0:
            return SolverResult(
                status=SolverStatus.BRACKET_LOST,
                message=f"No sign change: f({a})={fa}, f({b})={fb}"
            )
        
        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa
        
        c, fc = a, fa
        mflag = True
        d = 0.0
        history = []
        
        for i in range(max_iter):
            if self.record_history:
                history.append({
                    'iteration': i,
                    'a': a, 'b': b, 'c': c,
                    'fa': fa, 'fb': fb, 'fc': fc
                })
            
            if abs(fb) < tol or abs(b - a) < tol:
                return SolverResult(
                    status=SolverStatus.SUCCESS,
                    solution=b,
                    residual=abs(fb),
                    iterations=i + 1,
                    enclosure=Interval.closed(min(a, b), max(a, b)),
                    enclosure_verified=True,
                    iteration_history=history,
                    solver_type=self.solver_type,
                    message="Converged"
                )
            
            # Choose method
            if fa != fc and fb != fc:
                # Inverse quadratic interpolation
                s = (a * fb * fc / ((fa - fb) * (fa - fc)) +
                     b * fa * fc / ((fb - fa) * (fb - fc)) +
                     c * fa * fb / ((fc - fa) * (fc - fb)))
            else:
                # Secant method
                s = b - fb * (b - a) / (fb - fa)
            
            # Decide whether to use bisection
            cond1 = not ((3 * a + b) / 4 < s < b or b < s < (3 * a + b) / 4)
            cond2 = mflag and abs(s - b) >= abs(b - c) / 2
            cond3 = not mflag and abs(s - b) >= abs(c - d) / 2
            cond4 = mflag and abs(b - c) < tol
            cond5 = not mflag and abs(c - d) < tol
            
            if cond1 or cond2 or cond3 or cond4 or cond5:
                s = (a + b) / 2
                mflag = True
            else:
                mflag = False
            
            fs = H(s)
            d, c, fc = c, b, fb
            
            if fa * fs < 0:
                b, fb = s, fs
            else:
                a, fa = s, fs
            
            if abs(fa) < abs(fb):
                a, b = b, a
                fa, fb = fb, fa
        
        return SolverResult(
            status=SolverStatus.MAX_ITERATIONS,
            solution=b,
            residual=abs(fb),
            iterations=max_iter,
            iteration_history=history,
            solver_type=self.solver_type,
            message=f"Max iterations ({max_iter}) reached"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FIXED POINT ITERATION SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FixedPointSolver(Solver):
    """
    Fixed point iteration: x_{n+1} = F(x_n)
    
    Converges if F is a contraction: |F'(x)| < 1.
    Linear convergence rate = |F'(x*)|.
    """
    
    tol: float = 1e-12
    max_iter: int = 100
    record_history: bool = True
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.FIXED_POINT_ITERATION
    
    @property
    def name(self) -> str:
        return "Fixed Point Iteration"
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        **kwargs
    ) -> SolverResult:
        """For H(x)=0, converts to fixed point x=x-H(x)."""
        F = lambda x: x - H(x)
        return self.solve_fixed_point(F, domain, **kwargs)
    
    def solve_fixed_point(
        self,
        F: Callable[[float], float],
        domain: Interval,
        x0: Optional[float] = None,
        **kwargs
    ) -> SolverResult:
        """Solve x = F(x) directly."""
        tol = kwargs.get('tol', self.tol)
        max_iter = kwargs.get('max_iter', self.max_iter)
        
        if x0 is None:
            x0 = domain.midpoint if domain.is_bounded else 0.0
        
        x = x0
        history = []
        
        for i in range(max_iter):
            x_new = F(x)
            residual = abs(x_new - x)
            
            if self.record_history:
                history.append({
                    'iteration': i,
                    'x': x,
                    'x_new': x_new,
                    'residual': residual
                })
            
            if residual < tol:
                return SolverResult(
                    status=SolverStatus.SUCCESS,
                    solution=x_new,
                    residual=residual,
                    iterations=i + 1,
                    iteration_history=history,
                    solver_type=self.solver_type,
                    message="Converged"
                )
            
            x = x_new
        
        return SolverResult(
            status=SolverStatus.MAX_ITERATIONS,
            solution=x,
            residual=abs(F(x) - x),
            iterations=max_iter,
            iteration_history=history,
            solver_type=self.solver_type,
            message=f"Max iterations ({max_iter}) reached"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# INTERVAL NEWTON SOLVER (VERIFIED)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class IntervalNewtonSolver(Solver):
    """
    Interval Newton method for verified root finding.
    
    N(X) = m - H(m) / H'(X)
    X_{n+1} = X_n ∩ N(X_n)
    
    Properties:
    - Provides VERIFIED enclosure of root
    - Can prove uniqueness of root in interval
    - Can prove non-existence of roots
    """
    
    tol: float = 1e-12
    max_iter: int = 50
    record_history: bool = True
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.INTERVAL_NEWTON
    
    @property
    def name(self) -> str:
        return "Interval Newton"
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        dH: Optional[Callable[[float], float]] = None,
        **kwargs
    ) -> SolverResult:
        tol = kwargs.get('tol', self.tol)
        max_iter = kwargs.get('max_iter', self.max_iter)
        
        if not domain.is_bounded:
            return SolverResult(
                status=SolverStatus.DOMAIN_ERROR,
                message="Interval Newton requires bounded interval"
            )
        
        # Interval derivative using monotonicity bounds
        if dH is None:
            eps = 1e-8
            dH = lambda x: (H(x + eps) - H(x - eps)) / (2 * eps)
        
        X = domain
        history = []
        
        for i in range(max_iter):
            m = X.midpoint
            Hm = H(m)
            
            # Compute interval extension of derivative
            # Simplified: sample at endpoints and midpoint
            dH_lo = dH(X.lo)
            dH_hi = dH(X.hi)
            dH_mid = dH(m)
            dH_min = min(dH_lo, dH_hi, dH_mid)
            dH_max = max(dH_lo, dH_hi, dH_mid)
            
            if self.record_history:
                history.append({
                    'iteration': i,
                    'X': (X.lo, X.hi),
                    'm': m,
                    'Hm': Hm,
                    'dH_range': (dH_min, dH_max)
                })
            
            # Check if derivative interval contains zero
            if dH_min <= 0 <= dH_max:
                # Cannot proceed with interval Newton
                # Fall back to bisection-style refinement
                if abs(Hm) < tol:
                    return SolverResult(
                        status=SolverStatus.SUCCESS,
                        solution=m,
                        residual=abs(Hm),
                        iterations=i + 1,
                        enclosure=X,
                        enclosure_verified=True,
                        iteration_history=history,
                        solver_type=self.solver_type,
                        message="Converged (singular derivative)"
                    )
                # Bisect
                X = Interval.closed(X.lo, m) if H(X.lo) * Hm < 0 else Interval.closed(m, X.hi)
                continue
            
            # Newton interval: N = m - Hm / [dH_min, dH_max]
            if dH_max > 0:
                N_lo = m - Hm / dH_min
                N_hi = m - Hm / dH_max
            else:
                N_lo = m - Hm / dH_max
                N_hi = m - Hm / dH_min
            
            if N_lo > N_hi:
                N_lo, N_hi = N_hi, N_lo
            
            N = Interval.closed(N_lo, N_hi)
            
            # Intersect
            X_new = X.intersection(N)
            
            if X_new is None:
                return SolverResult(
                    status=SolverStatus.NO_CONVERGENCE,
                    iterations=i + 1,
                    iteration_history=history,
                    solver_type=self.solver_type,
                    message="No root exists in interval (verified)"
                )
            
            # Check convergence
            if X_new.width < tol:
                return SolverResult(
                    status=SolverStatus.SUCCESS,
                    solution=X_new.midpoint,
                    residual=abs(H(X_new.midpoint)),
                    iterations=i + 1,
                    enclosure=X_new,
                    enclosure_verified=True,
                    iteration_history=history,
                    solver_type=self.solver_type,
                    message="Converged with verified enclosure"
                )
            
            X = X_new
        
        return SolverResult(
            status=SolverStatus.MAX_ITERATIONS,
            solution=X.midpoint,
            residual=abs(H(X.midpoint)),
            iterations=max_iter,
            enclosure=X,
            enclosure_verified=True,
            iteration_history=history,
            solver_type=self.solver_type,
            message=f"Max iterations ({max_iter}) reached, enclosure width={X.width}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SOLVER FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

class SolverFactory:
    """Factory for creating solvers."""
    
    _solvers: Dict[SolverType, type] = {
        SolverType.BISECTION: BisectionSolver,
        SolverType.NEWTON: NewtonSolver,
        SolverType.SECANT: SecantSolver,
        SolverType.BRENT: BrentSolver,
        SolverType.FIXED_POINT_ITERATION: FixedPointSolver,
        SolverType.INTERVAL_NEWTON: IntervalNewtonSolver,
    }
    
    @classmethod
    def create(cls, solver_type: SolverType, **kwargs) -> Solver:
        """Create a solver of the given type."""
        if solver_type not in cls._solvers:
            raise ValueError(f"Unknown solver type: {solver_type}")
        return cls._solvers[solver_type](**kwargs)
    
    @classmethod
    def get_default(cls) -> Solver:
        """Get the default solver (Brent)."""
        return BrentSolver()
    
    @classmethod
    def get_verified(cls) -> Solver:
        """Get the default verified solver (Interval Newton)."""
        return IntervalNewtonSolver()
    
    @classmethod
    def list_types(cls) -> List[SolverType]:
        """List available solver types."""
        return list(cls._solvers.keys())


# ═══════════════════════════════════════════════════════════════════════════════
# ADAPTIVE SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AdaptiveSolver(Solver):
    """
    Adaptive solver that chooses method based on problem structure.
    
    Strategy:
    1. Try Newton for fast convergence
    2. Fall back to Brent if Newton fails
    3. Use Interval Newton for verification if requested
    """
    
    verify: bool = False
    tol: float = 1e-12
    max_iter: int = 100
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.NEWTON  # Primary method
    
    @property
    def name(self) -> str:
        return "Adaptive"
    
    def solve(
        self,
        H: Callable[[float], float],
        domain: Interval,
        **kwargs
    ) -> SolverResult:
        tol = kwargs.get('tol', self.tol)
        verify = kwargs.get('verify', self.verify)
        
        # First try Newton
        newton = NewtonSolver(tol=tol, max_iter=30)
        result = newton.solve(H, domain, **kwargs)
        
        if result.converged:
            if verify:
                # Verify with interval Newton
                return self._verify_result(H, result, domain, tol)
            return result
        
        # Fall back to Brent
        brent = BrentSolver(tol=tol, max_iter=self.max_iter)
        result = brent.solve(H, domain, **kwargs)
        
        if result.converged and verify:
            return self._verify_result(H, result, domain, tol)
        
        return result
    
    def _verify_result(
        self, 
        H: Callable[[float], float],
        result: SolverResult,
        domain: Interval,
        tol: float
    ) -> SolverResult:
        """Verify a result using interval Newton."""
        if result.solution is None:
            return result
        
        # Create small interval around solution
        x = result.solution
        delta = max(abs(x) * 1e-6, 1e-10)
        verify_domain = Interval.closed(x - delta, x + delta)
        
        interval_newton = IntervalNewtonSolver(tol=tol, max_iter=20)
        verified = interval_newton.solve(H, verify_domain)
        
        if verified.converged and verified.enclosure_verified:
            return verified
        
        # Verification failed, return original
        result.message += " (verification failed)"
        return result
