"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      FIXED POINT COMPILER MODULE                             ║
║                                                                              ║
║  Fixed Point Iteration, Contraction Mappings, and Convergence Analysis      ║
║                                                                              ║
║  Core Schema:                                                                ║
║    F(x*) = x*  (fixed point equation)                                       ║
║    e_{t+1} = F'(ξ) · e_t  (error dynamics)                                  ║
║                                                                              ║
║  The Four Chart Views:                                                       ║
║    □ (Square):  Exact rational/algebraic iterations                         ║
║    ✿ (Flower):  Error kernel, Jacobian, spectral radius                     ║
║    ☁ (Cloud):   Noise floor bounds, convergence rates                        ║
║    ⟂ (Fractal): FixedPointSeed with uniqueness selector                     ║
║                                                                              ║
║  Idempotence: Collapse(Expand(Seed)) = Seed                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Generic, TypeVar
from enum import Enum
import numpy as np
from numpy.typing import NDArray


T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════════════════════
# FIXED POINT TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class FixedPointType(Enum):
    """Classification of fixed point."""
    STABLE = "stable"           # |F'(x*)| < 1, attracting
    UNSTABLE = "unstable"       # |F'(x*)| > 1, repelling
    NEUTRAL = "neutral"         # |F'(x*)| = 1
    SUPERSTABLE = "superstable" # F'(x*) = 0


class ConvergenceType(Enum):
    """Type of convergence."""
    LINEAR = "linear"           # |e_{n+1}| ≤ r|e_n|, 0 < r < 1
    QUADRATIC = "quadratic"     # |e_{n+1}| ≤ C|e_n|²
    SUPERLINEAR = "superlinear" # |e_{n+1}| ≤ C|e_n|^p, p > 1
    SUBLINEAR = "sublinear"     # Slower than linear


# ═══════════════════════════════════════════════════════════════════════════════
# FIXED POINT DEFINITION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FixedPoint:
    """
    A fixed point x* of F: F(x*) = x*.
    """
    value: Any
    map_name: str
    derivative: Optional[float] = None  # F'(x*)
    basin: Optional[Tuple[float, float]] = None  # Attraction basin
    
    @property
    def fp_type(self) -> FixedPointType:
        """Classify fixed point by derivative."""
        if self.derivative is None:
            return FixedPointType.NEUTRAL
        d = abs(self.derivative)
        if d == 0:
            return FixedPointType.SUPERSTABLE
        elif d < 1:
            return FixedPointType.STABLE
        elif d > 1:
            return FixedPointType.UNSTABLE
        else:
            return FixedPointType.NEUTRAL
    
    @property
    def is_attracting(self) -> bool:
        """Check if fixed point is attracting."""
        return self.fp_type in [FixedPointType.STABLE, FixedPointType.SUPERSTABLE]


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR KERNEL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ErrorKernel:
    """
    Error dynamics near fixed point.
    
    e_{t+1} = K(e_t) where K is the error kernel.
    
    For Newton-like methods: e_{t+1} = C · e_t² / x_t
    """
    kernel_formula: str
    convergence_type: ConvergenceType
    rate_constant: float
    order: float = 1.0  # Convergence order
    
    @classmethod
    def linear(cls, rate: float) -> 'ErrorKernel':
        """Linear convergence kernel."""
        return cls(
            kernel_formula="e_{t+1} = r · e_t",
            convergence_type=ConvergenceType.LINEAR,
            rate_constant=rate,
            order=1.0
        )
    
    @classmethod
    def quadratic(cls, constant: float) -> 'ErrorKernel':
        """Quadratic convergence kernel (Newton)."""
        return cls(
            kernel_formula="e_{t+1} = C · e_t²",
            convergence_type=ConvergenceType.QUADRATIC,
            rate_constant=constant,
            order=2.0
        )
    
    @classmethod
    def babylonian_sqrt(cls) -> 'ErrorKernel':
        """
        Error kernel for x_{t+1} = (x_t + a/x_t)/2.
        
        e_{t+1} = e_t² / (2x_t)
        """
        return cls(
            kernel_formula="e_{t+1} = e_t² / (2x_t)",
            convergence_type=ConvergenceType.QUADRATIC,
            rate_constant=0.5,
            order=2.0
        )
    
    def predict_iterations(self, initial_error: float, target_error: float) -> int:
        """Predict iterations needed to reach target error."""
        if self.convergence_type == ConvergenceType.LINEAR:
            # r^n · e_0 ≤ ε → n ≥ log(ε/e_0)/log(r)
            if self.rate_constant >= 1:
                return -1  # Won't converge
            return int(np.ceil(np.log(target_error / initial_error) / np.log(self.rate_constant)))
        elif self.convergence_type == ConvergenceType.QUADRATIC:
            # After n iterations: e_n ≈ (C·e_0)^{2^n} / C
            # Roughly: 2^n ≈ log(ε)/log(C·e_0) iterations of doubling
            return int(np.ceil(np.log2(-np.log(target_error) / np.log(initial_error))))
        return -1


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACTION MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContractionMapping:
    """
    Contraction mapping with Lipschitz constant.
    
    |F(x) - F(y)| ≤ L|x - y| with L < 1.
    """
    lipschitz_constant: float  # L < 1
    domain: Tuple[float, float]
    
    @property
    def is_contraction(self) -> bool:
        """Check if valid contraction."""
        return 0 <= self.lipschitz_constant < 1
    
    def banach_estimate(self, x0: float, x1: float, tolerance: float) -> int:
        """
        Banach fixed point theorem iteration estimate.
        
        n ≥ log(ε(1-L)/(|x1-x0|)) / log(L)
        """
        if not self.is_contraction:
            return -1
        L = self.lipschitz_constant
        d = abs(x1 - x0)
        return int(np.ceil(np.log(tolerance * (1 - L) / d) / np.log(L)))
    
    def error_bound(self, x_n: float, x_prev: float) -> float:
        """
        A posteriori error bound.
        
        |x* - x_n| ≤ L/(1-L) · |x_n - x_{n-1}|
        """
        L = self.lipschitz_constant
        return L / (1 - L) * abs(x_n - x_prev)


# ═══════════════════════════════════════════════════════════════════════════════
# ITERATION SCHEMES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FixedPointIteration:
    """
    General fixed point iteration x_{n+1} = F(x_n).
    """
    F: Callable[[float], float]
    F_prime: Optional[Callable[[float], float]] = None
    name: str = "Fixed Point Iteration"
    
    def iterate(self, x0: float, max_iter: int = 100, 
                tolerance: float = 1e-12) -> Tuple[float, List[float], bool]:
        """
        Run iteration until convergence.
        
        Returns (x*, history, converged).
        """
        x = x0
        history = [x]
        
        for _ in range(max_iter):
            x_new = self.F(x)
            history.append(x_new)
            
            if abs(x_new - x) < tolerance:
                return x_new, history, True
            x = x_new
        
        return x, history, False
    
    def analyze_convergence(self, history: List[float]) -> ErrorKernel:
        """
        Analyze convergence from iteration history.
        """
        if len(history) < 3:
            return ErrorKernel.linear(1.0)
        
        # Compute successive error ratios
        errors = [abs(history[i+1] - history[i]) for i in range(len(history)-1)]
        
        if len(errors) < 2:
            return ErrorKernel.linear(1.0)
        
        # Check for linear: r = e_{n+1}/e_n
        ratios = [errors[i+1] / (errors[i] + 1e-15) for i in range(len(errors)-1)]
        avg_ratio = np.mean(ratios[-5:]) if len(ratios) >= 5 else np.mean(ratios)
        
        # Check for quadratic: e_{n+1} ≈ C·e_n²
        quad_ratios = [errors[i+1] / (errors[i]**2 + 1e-15) for i in range(len(errors)-1)]
        quad_const = np.mean(quad_ratios[-5:]) if len(quad_ratios) >= 5 else np.mean(quad_ratios)
        
        # Determine type
        if abs(avg_ratio) < 0.01 and quad_const < 100:
            return ErrorKernel.quadratic(quad_const)
        elif avg_ratio < 1:
            return ErrorKernel.linear(avg_ratio)
        else:
            return ErrorKernel("divergent", ConvergenceType.SUBLINEAR, avg_ratio)


@dataclass
class NewtonIteration(FixedPointIteration):
    """
    Newton-Raphson iteration for f(x) = 0.
    
    x_{n+1} = x_n - f(x_n)/f'(x_n)
    """
    f: Callable[[float], float] = None
    f_prime: Callable[[float], float] = None
    
    def __post_init__(self):
        if self.f is not None and self.f_prime is not None:
            self.F = lambda x: x - self.f(x) / self.f_prime(x)
            self.name = "Newton-Raphson"
    
    @classmethod
    def for_sqrt(cls, a: float) -> 'NewtonIteration':
        """
        Newton iteration for √a.
        
        f(x) = x² - a, f'(x) = 2x
        x_{n+1} = (x_n + a/x_n)/2  (Babylonian method)
        """
        instance = cls()
        instance.f = lambda x: x**2 - a
        instance.f_prime = lambda x: 2*x
        instance.F = lambda x: (x + a/x) / 2
        instance.name = f"Babylonian √{a}"
        return instance


@dataclass
class BabylonianSqrt:
    """
    Babylonian/Heron method for square roots.
    
    x_{n+1} = (x_n + a/x_n) / 2
    
    Special case with exact rational lift.
    """
    a: float
    
    def iterate_float(self, x0: float, n_iter: int) -> List[float]:
        """Float iteration."""
        history = [x0]
        x = x0
        for _ in range(n_iter):
            x = (x + self.a / x) / 2
            history.append(x)
        return history
    
    def iterate_rational(self, p0: int, q0: int, n_iter: int) -> List[Tuple[int, int, int]]:
        """
        Exact rational iteration.
        
        (p, q) → (p² + aq², 2pq)
        R' = p'² - a·q'² = R²  where R = p² - a·q²
        """
        history = [(p0, q0, p0**2 - int(self.a) * q0**2)]
        p, q = p0, q0
        
        for _ in range(n_iter):
            p_new = p**2 + int(self.a) * q**2
            q_new = 2 * p * q
            R_new = p_new**2 - int(self.a) * q_new**2
            history.append((p_new, q_new, R_new))
            p, q = p_new, q_new
        
        return history
    
    def exact_error_identity(self, p: int, q: int) -> str:
        """
        The residual squaring identity.
        
        R' = R² where R = p² - a·q²
        """
        R = p**2 - int(self.a) * q**2
        return f"R = p² - {int(self.a)}·q² = {R}, so R' = R² = {R**2}"


# ═══════════════════════════════════════════════════════════════════════════════
# FIXED POINT SEED
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FixedPointSeed:
    """
    Minimal seed for fixed point reconstruction.
    
    Contains:
    - Iteration map F
    - Uniqueness selector
    - Convergence certificate
    - RT⟂ checksum
    """
    map_formula: str
    fixed_point: float
    selector: str  # e.g., "x > 0" for √a
    convergence_proof: str
    checksum: str = ""
    
    def __post_init__(self):
        """Compute checksum."""
        import hashlib
        data = f"{self.map_formula}|{self.selector}|{self.fixed_point}"
        self.checksum = hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @classmethod
    def sqrt_seed(cls, a: float) -> 'FixedPointSeed':
        """Seed for √a."""
        return cls(
            map_formula=f"F(x) = (x + {a}/x) / 2",
            fixed_point=np.sqrt(a),
            selector="x > 0",
            convergence_proof=f"F'(√{a}) = 0, superstable fixed point"
        )
    
    def verify_idempotence(self, F: Callable[[float], float], 
                           x0: float, tolerance: float = 1e-10) -> bool:
        """
        Verify Collapse(Expand(Seed)) = Seed.
        
        Expand: run iteration from x0
        Collapse: verify converges to same fixed_point
        """
        result, _, converged = FixedPointIteration(F).iterate(x0, tolerance=tolerance)
        return converged and abs(result - self.fixed_point) < tolerance


# ═══════════════════════════════════════════════════════════════════════════════
# NOISY FIXED POINT ITERATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NoisyFixedPointIteration:
    """
    Fixed point iteration with noise: x_{n+1} = F(x_n) + ξ_n.
    
    Cloud chart: noise floor bounds.
    """
    F: Callable[[float], float]
    noise_std: float
    lipschitz: float
    
    def noise_floor_bound(self) -> float:
        """
        Asymptotic noise floor under Lipschitz condition.
        
        E[|E_t|] ≤ 2^{-t}|E_0| + 2σ under L < 1/2
        """
        if self.lipschitz >= 0.5:
            return np.inf
        return 2 * self.noise_std / (1 - 2 * self.lipschitz)
    
    def iterate_noisy(self, x0: float, n_iter: int) -> Tuple[List[float], List[float]]:
        """
        Run noisy iteration.
        
        Returns (trajectory, noise_samples).
        """
        x = x0
        trajectory = [x]
        noises = []
        
        for _ in range(n_iter):
            xi = np.random.normal(0, self.noise_std)
            noises.append(xi)
            x = self.F(x) + xi
            trajectory.append(x)
        
        return trajectory, noises


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FixedPointPoleBridge:
    """
    Bridge between fixed point theory and four-pole framework.
    """
    
    @staticmethod
    def four_chart_view() -> str:
        return """
        FIXED POINT ↔ FOUR CHARTS
        
        □ (Square):   Exact rational lift (p,q) → (p²+aq², 2pq)
        ✿ (Flower):   Error kernel e_{t+1} = K(e_t)
        ☁ (Cloud):    Noise floor bounds, convergence rates
        ⟂ (Fractal):  FixedPointSeed with selector + RT⟂
        """
    
    @staticmethod
    def c_pole() -> str:
        """C-pole ↔ Jacobian/spectral analysis."""
        return "C-pole ↔ F'(x*), spectral radius, continuous analysis"
    
    @staticmethod
    def psi_pole() -> str:
        """Ψ-pole ↔ Recursive structure."""
        return "Ψ-pole ↔ Iteration hierarchy, nested convergence"
    
    @staticmethod
    def d_pole() -> str:
        """D-pole ↔ Exact arithmetic."""
        return "D-pole ↔ Rational lift, exact residual R' = R²"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def fixed_point(value: Any, map_name: str, derivative: float = None) -> FixedPoint:
    """Create fixed point."""
    return FixedPoint(value, map_name, derivative)


def error_kernel_linear(rate: float) -> ErrorKernel:
    """Create linear error kernel."""
    return ErrorKernel.linear(rate)


def error_kernel_quadratic(constant: float) -> ErrorKernel:
    """Create quadratic error kernel."""
    return ErrorKernel.quadratic(constant)


def contraction_mapping(L: float, domain: Tuple[float, float]) -> ContractionMapping:
    """Create contraction mapping."""
    return ContractionMapping(L, domain)


def newton_sqrt(a: float) -> NewtonIteration:
    """Create Newton iteration for √a."""
    return NewtonIteration.for_sqrt(a)


def babylonian_sqrt(a: float) -> BabylonianSqrt:
    """Create Babylonian sqrt iteration."""
    return BabylonianSqrt(a)


def fixed_point_seed(formula: str, fp: float, selector: str) -> FixedPointSeed:
    """Create fixed point seed."""
    return FixedPointSeed(formula, fp, selector, "")


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'FixedPointType',
    'ConvergenceType',
    
    # Core
    'FixedPoint',
    'ErrorKernel',
    'ContractionMapping',
    
    # Iterations
    'FixedPointIteration',
    'NewtonIteration',
    'BabylonianSqrt',
    
    # Seed
    'FixedPointSeed',
    
    # Noisy
    'NoisyFixedPointIteration',
    
    # Bridge
    'FixedPointPoleBridge',
    
    # Functions
    'fixed_point',
    'error_kernel_linear',
    'error_kernel_quadratic',
    'contraction_mapping',
    'newton_sqrt',
    'babylonian_sqrt',
    'fixed_point_seed',
]
