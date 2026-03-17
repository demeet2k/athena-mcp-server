"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      DYNAMICAL SYSTEMS MODULE                                ║
║                                                                              ║
║  Fixed Points, Bifurcations, Chaos, and Lyapunov Analysis                    ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Dynamical systems theory provides the language for understanding          ║
║    algorithm convergence, stability, and phase transitions. The              ║
║    shortcut engine exploits bifurcation structure.                          ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Fixed points: f(x*) = x*, stability via eigenvalues                    ║
║    - Bifurcations: Qualitative changes as parameters vary                   ║
║    - Lyapunov exponents: Rate of separation of nearby trajectories          ║
║    - Attractors: Limit sets, basins of attraction                           ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Gateway hops ↔ discrete dynamical system                               ║
║    - Pole weights ↔ control parameters                                      ║
║    - Shortcuts ↔ bifurcation-induced fast transitions                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# FIXED POINT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

class StabilityType(Enum):
    """Classification of fixed point stability."""
    STABLE_NODE = "stable_node"           # All eigenvalues < 0
    UNSTABLE_NODE = "unstable_node"       # All eigenvalues > 0
    SADDLE = "saddle"                     # Mixed signs
    STABLE_FOCUS = "stable_focus"         # Complex, Re < 0
    UNSTABLE_FOCUS = "unstable_focus"     # Complex, Re > 0
    CENTER = "center"                     # Pure imaginary
    NONHYPERBOLIC = "nonhyperbolic"       # Zero eigenvalue


@dataclass
class FixedPointInfo:
    """
    Information about a fixed point.
    """
    location: NDArray[np.float64]
    jacobian: NDArray[np.float64]
    eigenvalues: NDArray[np.complex128]
    eigenvectors: NDArray[np.complex128]
    stability: StabilityType
    
    @classmethod
    def analyze(cls, f: Callable, x_star: NDArray, 
               epsilon: float = 1e-7) -> 'FixedPointInfo':
        """
        Analyze fixed point at x_star.
        """
        x_star = np.asarray(x_star, dtype=np.float64)
        n = len(x_star)
        
        # Compute Jacobian numerically
        J = np.zeros((n, n))
        for i in range(n):
            e_i = np.zeros(n)
            e_i[i] = epsilon
            J[:, i] = (f(x_star + e_i) - f(x_star - e_i)) / (2 * epsilon)
        
        # Eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eig(J)
        
        # Classify stability
        stability = cls._classify_stability(eigenvalues)
        
        return cls(
            location=x_star,
            jacobian=J,
            eigenvalues=eigenvalues,
            eigenvectors=eigenvectors,
            stability=stability
        )
    
    @staticmethod
    def _classify_stability(eigenvalues: NDArray) -> StabilityType:
        """Classify based on eigenvalues."""
        real_parts = np.real(eigenvalues)
        imag_parts = np.imag(eigenvalues)
        
        has_zero = np.any(np.abs(real_parts) < 1e-10)
        if has_zero:
            return StabilityType.NONHYPERBOLIC
        
        all_negative = np.all(real_parts < 0)
        all_positive = np.all(real_parts > 0)
        has_complex = np.any(np.abs(imag_parts) > 1e-10)
        
        if all_negative:
            if has_complex:
                return StabilityType.STABLE_FOCUS
            return StabilityType.STABLE_NODE
        elif all_positive:
            if has_complex:
                return StabilityType.UNSTABLE_FOCUS
            return StabilityType.UNSTABLE_NODE
        else:
            return StabilityType.SADDLE
    
    @property
    def spectral_radius(self) -> float:
        """Maximum absolute eigenvalue."""
        return float(np.max(np.abs(self.eigenvalues)))
    
    @property
    def is_stable(self) -> bool:
        """Check if asymptotically stable."""
        return self.stability in [StabilityType.STABLE_NODE, StabilityType.STABLE_FOCUS]


# ═══════════════════════════════════════════════════════════════════════════════
# DISCRETE DYNAMICAL SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DiscreteMap:
    """
    Discrete dynamical system x_{n+1} = f(x_n).
    """
    f: Callable[[NDArray], NDArray]
    dimension: int
    
    def iterate(self, x0: NDArray, n_steps: int) -> NDArray[np.float64]:
        """
        Iterate map n_steps times.
        
        Returns trajectory of shape (n_steps + 1, dimension).
        """
        trajectory = np.zeros((n_steps + 1, self.dimension))
        trajectory[0] = x0
        
        x = np.asarray(x0, dtype=np.float64)
        for i in range(n_steps):
            x = self.f(x)
            trajectory[i + 1] = x
        
        return trajectory
    
    def find_fixed_points(self, x_init: NDArray, 
                         tolerance: float = 1e-10,
                         max_iter: int = 1000) -> Optional[NDArray]:
        """
        Find fixed point starting from x_init.
        
        Uses simple iteration; may not converge for unstable points.
        """
        x = np.asarray(x_init, dtype=np.float64)
        
        for _ in range(max_iter):
            x_new = self.f(x)
            if np.linalg.norm(x_new - x) < tolerance:
                return x_new
            x = x_new
        
        return None
    
    def find_period_n_points(self, n: int, x_init: NDArray,
                            tolerance: float = 1e-10) -> List[NDArray]:
        """Find period-n points (including period-k for k|n)."""
        # Compose f with itself n times
        def f_n(x):
            for _ in range(n):
                x = self.f(x)
            return x
        
        composed_map = DiscreteMap(f_n, self.dimension)
        fixed = composed_map.find_fixed_points(x_init, tolerance)
        
        if fixed is None:
            return []
        
        # Verify it's actually period-n
        orbit = [fixed.copy()]
        x = fixed.copy()
        for _ in range(n - 1):
            x = self.f(x)
            orbit.append(x.copy())
        
        return orbit


@dataclass
class LogisticMap:
    """
    The logistic map: x_{n+1} = r·x_n·(1 - x_n).
    
    Classic example of period-doubling route to chaos.
    """
    r: float = 3.5
    
    def __post_init__(self):
        self.dimension = 1
    
    def f(self, x: NDArray) -> NDArray:
        """Apply logistic map."""
        return self.r * x * (1 - x)
    
    def iterate(self, x0: NDArray, n_steps: int) -> NDArray[np.float64]:
        """Iterate map n_steps times."""
        trajectory = np.zeros((n_steps + 1, self.dimension))
        trajectory[0] = x0
        
        x = np.asarray(x0, dtype=np.float64)
        for i in range(n_steps):
            x = self.f(x)
            trajectory[i + 1] = x
        
        return trajectory
    
    @property
    def fixed_points(self) -> List[float]:
        """Analytical fixed points: 0 and (r-1)/r."""
        if self.r <= 1:
            return [0.0]
        return [0.0, (self.r - 1) / self.r]
    
    def bifurcation_diagram(self, r_range: Tuple[float, float],
                           n_r: int = 500, 
                           n_transient: int = 500,
                           n_record: int = 100) -> Dict[str, NDArray]:
        """
        Compute bifurcation diagram.
        
        Returns dict with 'r' and 'x' arrays.
        """
        r_values = np.linspace(r_range[0], r_range[1], n_r)
        r_all = []
        x_all = []
        
        for r in r_values:
            # Random initial condition
            x = np.array([0.5])
            
            # Transient
            for _ in range(n_transient):
                x = r * x * (1 - x)
            
            # Record
            for _ in range(n_record):
                x = r * x * (1 - x)
                r_all.append(r)
                x_all.append(float(x[0]))
        
        return {'r': np.array(r_all), 'x': np.array(x_all)}


# ═══════════════════════════════════════════════════════════════════════════════
# CONTINUOUS DYNAMICAL SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContinuousFlow:
    """
    Continuous dynamical system dx/dt = f(x).
    """
    f: Callable[[NDArray], NDArray]  # Vector field
    dimension: int
    
    def integrate_rk4(self, x0: NDArray, t_span: Tuple[float, float],
                     n_steps: int = 1000) -> Tuple[NDArray, NDArray]:
        """
        Integrate using 4th-order Runge-Kutta.
        
        Returns (times, trajectory).
        """
        t0, t1 = t_span
        dt = (t1 - t0) / n_steps
        
        times = np.linspace(t0, t1, n_steps + 1)
        trajectory = np.zeros((n_steps + 1, self.dimension))
        trajectory[0] = x0
        
        x = np.asarray(x0, dtype=np.float64)
        
        for i in range(n_steps):
            k1 = self.f(x)
            k2 = self.f(x + 0.5 * dt * k1)
            k3 = self.f(x + 0.5 * dt * k2)
            k4 = self.f(x + dt * k3)
            
            x = x + (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)
            trajectory[i + 1] = x
        
        return times, trajectory
    
    def equilibria_newton(self, x_init: NDArray,
                         tolerance: float = 1e-10,
                         max_iter: int = 100) -> Optional[NDArray]:
        """Find equilibrium using Newton's method."""
        x = np.asarray(x_init, dtype=np.float64)
        n = self.dimension
        epsilon = 1e-7
        
        for _ in range(max_iter):
            fx = self.f(x)
            
            if np.linalg.norm(fx) < tolerance:
                return x
            
            # Jacobian
            J = np.zeros((n, n))
            for i in range(n):
                e_i = np.zeros(n)
                e_i[i] = epsilon
                J[:, i] = (self.f(x + e_i) - self.f(x - e_i)) / (2 * epsilon)
            
            # Newton step
            try:
                dx = np.linalg.solve(J, -fx)
            except np.linalg.LinAlgError:
                return None
            
            x = x + dx
        
        return None


@dataclass
class LorenzSystem:
    """
    Lorenz system: classic chaotic attractor.
    
    dx/dt = σ(y - x)
    dy/dt = x(ρ - z) - y
    dz/dt = xy - βz
    """
    sigma: float = 10.0
    rho: float = 28.0
    beta: float = 8/3
    
    def __post_init__(self):
        self.dimension = 3
    
    def f(self, state: NDArray) -> NDArray:
        """Lorenz vector field."""
        x, y, z = state
        return np.array([
            self.sigma * (y - x),
            x * (self.rho - z) - y,
            x * y - self.beta * z
        ])
    
    def integrate_rk4(self, x0: NDArray, t_span: Tuple[float, float],
                     n_steps: int = 1000) -> Tuple[NDArray, NDArray]:
        """Integrate using RK4."""
        t0, t1 = t_span
        dt = (t1 - t0) / n_steps
        
        times = np.linspace(t0, t1, n_steps + 1)
        trajectory = np.zeros((n_steps + 1, self.dimension))
        trajectory[0] = x0
        
        x = np.asarray(x0, dtype=np.float64)
        
        for i in range(n_steps):
            k1 = self.f(x)
            k2 = self.f(x + 0.5 * dt * k1)
            k3 = self.f(x + 0.5 * dt * k2)
            k4 = self.f(x + dt * k3)
            
            x = x + (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)
            trajectory[i + 1] = x
        
        return times, trajectory
    
    @property
    def equilibria(self) -> List[NDArray]:
        """Analytical equilibria."""
        origin = np.array([0.0, 0.0, 0.0])
        
        if self.rho <= 1:
            return [origin]
        
        # Non-trivial equilibria
        c = np.sqrt(self.beta * (self.rho - 1))
        eq_plus = np.array([c, c, self.rho - 1])
        eq_minus = np.array([-c, -c, self.rho - 1])
        
        return [origin, eq_plus, eq_minus]


# ═══════════════════════════════════════════════════════════════════════════════
# LYAPUNOV EXPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LyapunovAnalyzer:
    """
    Compute Lyapunov exponents for dynamical systems.
    
    Lyapunov exponent measures exponential rate of divergence
    of nearby trajectories: |δx(t)| ~ |δx(0)| e^{λt}
    """
    
    @staticmethod
    def maximal_lyapunov_discrete(dmap: DiscreteMap, x0: NDArray,
                                  n_steps: int = 10000,
                                  n_transient: int = 1000) -> float:
        """
        Estimate maximal Lyapunov exponent for discrete map.
        """
        epsilon = 1e-8
        dimension = dmap.dimension
        
        x = np.asarray(x0, dtype=np.float64)
        
        # Transient
        for _ in range(n_transient):
            x = dmap.f(x)
        
        # Compute Lyapunov exponent
        lyapunov_sum = 0.0
        
        # Initialize perturbation
        delta = np.random.randn(dimension)
        delta = delta / np.linalg.norm(delta) * epsilon
        
        for _ in range(n_steps):
            x_new = dmap.f(x)
            x_pert = dmap.f(x + delta)
            
            # New perturbation
            delta_new = x_pert - x_new
            
            # Record stretching
            stretch = np.linalg.norm(delta_new)
            if stretch > 0:
                lyapunov_sum += np.log(stretch / epsilon)
            
            # Renormalize
            delta = delta_new / stretch * epsilon if stretch > 0 else delta
            x = x_new
        
        return lyapunov_sum / n_steps
    
    @staticmethod
    def lyapunov_spectrum_continuous(flow: ContinuousFlow, x0: NDArray,
                                    t_total: float = 100,
                                    dt: float = 0.01) -> NDArray[np.float64]:
        """
        Estimate full Lyapunov spectrum for continuous flow.
        
        Uses QR decomposition method.
        """
        n = flow.dimension
        n_steps = int(t_total / dt)
        
        x = np.asarray(x0, dtype=np.float64)
        Q = np.eye(n)  # Orthonormal basis
        
        lyapunov_sums = np.zeros(n)
        epsilon = 1e-7
        
        for step in range(n_steps):
            # Integrate main trajectory
            k1 = flow.f(x)
            k2 = flow.f(x + 0.5 * dt * k1)
            k3 = flow.f(x + 0.5 * dt * k2)
            k4 = flow.f(x + dt * k3)
            x = x + (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)
            
            # Estimate Jacobian
            J = np.zeros((n, n))
            for i in range(n):
                e_i = np.zeros(n)
                e_i[i] = epsilon
                J[:, i] = (flow.f(x + e_i) - flow.f(x - e_i)) / (2 * epsilon)
            
            # Evolve tangent vectors
            Q = Q + dt * (J @ Q)
            
            # Reorthonormalize periodically
            if step % 10 == 0:
                Q, R = np.linalg.qr(Q)
                lyapunov_sums += np.log(np.abs(np.diag(R)) + 1e-15)
        
        return lyapunov_sums / t_total


# ═══════════════════════════════════════════════════════════════════════════════
# BIFURCATION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

class BifurcationType(Enum):
    """Types of bifurcations."""
    SADDLE_NODE = "saddle_node"       # Fixed points appear/disappear
    TRANSCRITICAL = "transcritical"    # Exchange of stability
    PITCHFORK = "pitchfork"           # Symmetric branching
    HOPF = "hopf"                     # Limit cycle appears
    PERIOD_DOUBLING = "period_doubling"  # Period doubles
    FLIP = "flip"                     # Period doubling for maps


@dataclass
class BifurcationDetector:
    """
    Detect and classify bifurcations.
    """
    
    @staticmethod
    def detect_eigenvalue_crossing(jacobian_func: Callable[[float], NDArray],
                                  param_range: Tuple[float, float],
                                  n_samples: int = 100) -> List[Dict[str, Any]]:
        """
        Detect where eigenvalues cross imaginary axis or unit circle.
        """
        params = np.linspace(param_range[0], param_range[1], n_samples)
        crossings = []
        
        prev_eigenvalues = None
        
        for i, p in enumerate(params):
            J = jacobian_func(p)
            eigenvalues = np.linalg.eigvals(J)
            
            if prev_eigenvalues is not None:
                # Check for sign change in real part
                for ev_new, ev_old in zip(sorted(eigenvalues, key=np.real),
                                          sorted(prev_eigenvalues, key=np.real)):
                    if np.real(ev_new) * np.real(ev_old) < 0:
                        crossings.append({
                            'parameter': p,
                            'eigenvalue': ev_new,
                            'type': 'real_axis_crossing'
                        })
            
            prev_eigenvalues = eigenvalues
        
        return crossings


# ═══════════════════════════════════════════════════════════════════════════════
# BASIN OF ATTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BasinAnalyzer:
    """
    Analyze basins of attraction.
    """
    dmap: DiscreteMap
    
    def compute_basin_2d(self, x_range: Tuple[float, float],
                        y_range: Tuple[float, float],
                        resolution: int = 100,
                        attractors: List[NDArray] = None,
                        max_iter: int = 500,
                        tolerance: float = 1e-6) -> NDArray[np.int32]:
        """
        Compute basin of attraction in 2D.
        
        Returns grid where each cell indicates which attractor is reached.
        """
        if self.dmap.dimension != 2:
            raise ValueError("Basin computation requires 2D map")
        
        x_vals = np.linspace(x_range[0], x_range[1], resolution)
        y_vals = np.linspace(y_range[0], y_range[1], resolution)
        
        basin = np.zeros((resolution, resolution), dtype=np.int32)
        
        for i, x in enumerate(x_vals):
            for j, y in enumerate(y_vals):
                point = np.array([x, y])
                
                # Iterate to find attractor
                for _ in range(max_iter):
                    point = self.dmap.f(point)
                
                # Classify
                if attractors is not None:
                    for k, attr in enumerate(attractors):
                        if np.linalg.norm(point - attr) < tolerance:
                            basin[j, i] = k + 1
                            break
                else:
                    basin[j, i] = 1  # Single basin
        
        return basin


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_fixed_point(f: Callable, x_star: NDArray) -> FixedPointInfo:
    """Analyze stability of fixed point."""
    return FixedPointInfo.analyze(f, x_star)


def lyapunov_exponent(system, x0: NDArray, n_steps: int = 10000) -> float:
    """Compute maximal Lyapunov exponent."""
    # Handle LogisticMap specially
    if hasattr(system, 'r') and hasattr(system, 'dimension'):
        # LogisticMap
        epsilon = 1e-8
        x = np.asarray(x0, dtype=np.float64).flatten()
        
        # Transient
        for _ in range(1000):
            x = system.f(x)
        
        lyapunov_sum = 0.0
        delta = np.array([epsilon])
        
        for _ in range(n_steps):
            x_new = system.f(x)
            x_pert = system.f(x + delta)
            
            delta_new = x_pert - x_new
            stretch = np.abs(delta_new[0])
            
            if stretch > 0:
                lyapunov_sum += np.log(stretch / epsilon)
                delta = delta_new / stretch * epsilon
            
            x = x_new
        
        return lyapunov_sum / n_steps
    
    # DiscreteMap
    return LyapunovAnalyzer.maximal_lyapunov_discrete(system, x0, n_steps)


def logistic_bifurcation(r_range: Tuple[float, float] = (2.5, 4.0)
                        ) -> Dict[str, NDArray]:
    """Compute logistic map bifurcation diagram."""
    lmap = LogisticMap()
    return lmap.bifurcation_diagram(r_range)


def integrate_lorenz(x0: NDArray = None, t_span: Tuple[float, float] = (0, 50),
                    n_steps: int = 5000) -> Tuple[NDArray, NDArray]:
    """Integrate Lorenz system."""
    if x0 is None:
        x0 = np.array([1.0, 1.0, 1.0])
    lorenz = LorenzSystem()
    return lorenz.integrate_rk4(x0, t_span, n_steps)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'StabilityType',
    'BifurcationType',
    
    # Fixed points
    'FixedPointInfo',
    
    # Discrete systems
    'DiscreteMap',
    'LogisticMap',
    
    # Continuous systems
    'ContinuousFlow',
    'LorenzSystem',
    
    # Analysis
    'LyapunovAnalyzer',
    'BifurcationDetector',
    'BasinAnalyzer',
    
    # Functions
    'analyze_fixed_point',
    'lyapunov_exponent',
    'logistic_bifurcation',
    'integrate_lorenz',
]
