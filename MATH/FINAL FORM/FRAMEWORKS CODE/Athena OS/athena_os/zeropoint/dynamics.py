"""
ATHENA OS - Zero-Point Computing
================================
Dynamics, Gradient Flows, and Stability

From ZERO-POINT_COMPUTING.docx Chapter 3:

METRIC STRUCTURES:
    - Euclidean: d_E(x,y) = ‖φ(x) - φ(y)‖₂
    - Riemannian: d_g via geodesic lengths
    - Divergence-based: KL, Fisher-Rao

CENTERS:
    - Fréchet mean: argmin_μ Σ d(x_i, μ)²
    - Geometric center: zero of potential
    - κ-center: minimum texture point

STABILITY:
    - Hyperbolic attractor: Re(λ) < 0 for all eigenvalues
    - Saddle: mixed eigenvalue signs
    - Bifurcation node: eigenvalues cross imaginary axis

GRADIENT FLOWS:
    dx/dt = -∇V(x)
    
    Flow toward minima of potential V
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math

from .agent import InternalState


# =============================================================================
# METRIC TYPES
# =============================================================================

class MetricType(Enum):
    """Types of metrics on state space."""
    
    EUCLIDEAN = "euclidean"
    RIEMANNIAN = "riemannian"
    MANHATTAN = "manhattan"
    KAPPA = "kappa"           # κ-based metric
    FISHER = "fisher"         # Fisher-Rao metric


@dataclass
class Metric:
    """
    Metric on state space.
    
    d: X × X → [0,∞)
    """
    
    metric_type: MetricType = MetricType.EUCLIDEAN
    
    # Riemannian metric tensor (simplified as scaling)
    metric_scale: List[float] = field(default_factory=list)
    
    def distance(self, x: List[float], y: List[float]) -> float:
        """Compute distance d(x, y)."""
        if len(x) != len(y):
            return float('inf')
        
        if self.metric_type == MetricType.EUCLIDEAN:
            return math.sqrt(sum((a - b)**2 for a, b in zip(x, y)))
        
        elif self.metric_type == MetricType.MANHATTAN:
            return sum(abs(a - b) for a, b in zip(x, y))
        
        elif self.metric_type == MetricType.RIEMANNIAN:
            # Weighted Euclidean (simplified Riemannian)
            if not self.metric_scale:
                self.metric_scale = [1.0] * len(x)
            return math.sqrt(sum(
                s * (a - b)**2 
                for s, a, b in zip(self.metric_scale, x, y)
            ))
        
        elif self.metric_type == MetricType.KAPPA:
            # κ-based: distance weighted by texture
            kappa_x = math.sqrt(sum(a**2 for a in x))
            kappa_y = math.sqrt(sum(b**2 for b in y))
            euclidean = math.sqrt(sum((a - b)**2 for a, b in zip(x, y)))
            return euclidean * (1 + abs(kappa_x - kappa_y))
        
        else:
            return math.sqrt(sum((a - b)**2 for a, b in zip(x, y)))
    
    def geodesic(self, x: List[float], y: List[float], 
                 t: float) -> List[float]:
        """
        Point on geodesic from x to y at parameter t ∈ [0,1].
        
        For Euclidean: linear interpolation.
        """
        return [(1 - t) * a + t * b for a, b in zip(x, y)]


# =============================================================================
# CENTER COMPUTATION
# =============================================================================

@dataclass
class CenterFinder:
    """
    Find centers of point sets.
    """
    
    metric: Metric = field(default_factory=Metric)
    max_iterations: int = 100
    tolerance: float = 1e-6
    
    def frechet_mean(self, points: List[List[float]]) -> List[float]:
        """
        Compute Fréchet mean.
        
        μ* = argmin_μ Σ d(x_i, μ)²
        """
        if not points:
            return []
        
        dim = len(points[0])
        n = len(points)
        
        # Start with arithmetic mean
        mean = [sum(p[i] for p in points) / n for i in range(dim)]
        
        # Iterate (Weiszfeld algorithm for general metrics)
        for _ in range(self.max_iterations):
            weights = []
            for p in points:
                d = self.metric.distance(p, mean)
                weights.append(1.0 / max(d, 1e-10))
            
            total_weight = sum(weights)
            new_mean = [
                sum(w * p[i] for w, p in zip(weights, points)) / total_weight
                for i in range(dim)
            ]
            
            if self.metric.distance(mean, new_mean) < self.tolerance:
                break
            
            mean = new_mean
        
        return mean
    
    def geometric_center(self, points: List[List[float]]) -> List[float]:
        """Compute geometric center (centroid)."""
        if not points:
            return []
        
        dim = len(points[0])
        n = len(points)
        
        return [sum(p[i] for p in points) / n for i in range(dim)]
    
    def kappa_center(self, points: List[List[float]],
                    kappa_fn: Callable[[List[float]], float]) -> List[float]:
        """
        Find κ-center: point of minimum texture.
        """
        if not points:
            return []
        
        # Start from geometric center
        center = self.geometric_center(points)
        
        # Gradient descent to minimize κ
        lr = 0.1
        for _ in range(self.max_iterations):
            kappa = kappa_fn(center)
            
            # Numerical gradient
            grad = []
            for i in range(len(center)):
                perturbed = list(center)
                perturbed[i] += 0.01
                grad.append((kappa_fn(perturbed) - kappa) / 0.01)
            
            # Descent step
            new_center = [c - lr * g for c, g in zip(center, grad)]
            
            if self.metric.distance(center, new_center) < self.tolerance:
                break
            
            center = new_center
        
        return center


# =============================================================================
# STABILITY ANALYSIS
# =============================================================================

class StabilityType(Enum):
    """Types of stability for equilibrium points."""
    
    ATTRACTOR = "attractor"           # All Re(λ) < 0
    REPELLER = "repeller"             # All Re(λ) > 0
    SADDLE = "saddle"                 # Mixed signs
    CENTER = "center"                  # Pure imaginary
    BIFURCATION = "bifurcation"       # Eigenvalue at imaginary axis


@dataclass
class Eigenvalue:
    """Eigenvalue with real and imaginary parts."""
    
    real: float
    imag: float = 0.0
    
    @property
    def is_stable(self) -> bool:
        """Stable if Re(λ) < 0."""
        return self.real < 0
    
    @property
    def is_oscillatory(self) -> bool:
        """Oscillatory if Im(λ) ≠ 0."""
        return abs(self.imag) > 1e-10
    
    @property
    def magnitude(self) -> float:
        return math.sqrt(self.real**2 + self.imag**2)


@dataclass
class StabilityAnalysis:
    """
    Stability analysis of equilibrium points.
    """
    
    equilibrium: List[float]
    eigenvalues: List[Eigenvalue] = field(default_factory=list)
    stability_type: StabilityType = StabilityType.CENTER
    
    # Manifold dimensions
    stable_dim: int = 0      # dim W^s
    unstable_dim: int = 0    # dim W^u
    center_dim: int = 0      # dim W^c
    
    def classify(self) -> StabilityType:
        """Classify stability from eigenvalues."""
        if not self.eigenvalues:
            return StabilityType.CENTER
        
        n_stable = sum(1 for e in self.eigenvalues if e.real < -1e-10)
        n_unstable = sum(1 for e in self.eigenvalues if e.real > 1e-10)
        n_center = len(self.eigenvalues) - n_stable - n_unstable
        
        self.stable_dim = n_stable
        self.unstable_dim = n_unstable
        self.center_dim = n_center
        
        if n_unstable == 0 and n_center == 0:
            self.stability_type = StabilityType.ATTRACTOR
        elif n_stable == 0 and n_center == 0:
            self.stability_type = StabilityType.REPELLER
        elif n_center > 0 and n_stable == 0 and n_unstable == 0:
            self.stability_type = StabilityType.CENTER
        elif n_center > 0:
            self.stability_type = StabilityType.BIFURCATION
        else:
            self.stability_type = StabilityType.SADDLE
        
        return self.stability_type
    
    def is_hyperbolic(self) -> bool:
        """Check if equilibrium is hyperbolic (no center eigenvalues)."""
        return self.center_dim == 0


# =============================================================================
# POTENTIAL FUNCTION
# =============================================================================

@dataclass
class Potential:
    """
    Potential function V: X → ℝ.
    
    Dynamics: dx/dt = -∇V(x)
    """
    
    name: str = "V"
    
    # Potential function
    potential_fn: Optional[Callable[[List[float]], float]] = None
    
    def value(self, x: List[float]) -> float:
        """Compute V(x)."""
        if self.potential_fn:
            return self.potential_fn(x)
        
        # Default: quadratic bowl
        return 0.5 * sum(xi**2 for xi in x)
    
    def gradient(self, x: List[float], epsilon: float = 0.01) -> List[float]:
        """Compute ∇V(x) numerically."""
        grad = []
        v0 = self.value(x)
        
        for i in range(len(x)):
            perturbed = list(x)
            perturbed[i] += epsilon
            grad.append((self.value(perturbed) - v0) / epsilon)
        
        return grad
    
    def hessian_eigenvalues(self, x: List[float], 
                           epsilon: float = 0.01) -> List[Eigenvalue]:
        """
        Estimate eigenvalues of Hessian at x.
        
        Simplified: uses diagonal approximation.
        """
        eigenvalues = []
        v0 = self.value(x)
        
        for i in range(len(x)):
            perturbed_plus = list(x)
            perturbed_plus[i] += epsilon
            
            perturbed_minus = list(x)
            perturbed_minus[i] -= epsilon
            
            # Second derivative approximation
            v_plus = self.value(perturbed_plus)
            v_minus = self.value(perturbed_minus)
            
            hess_ii = (v_plus - 2*v0 + v_minus) / (epsilon**2)
            eigenvalues.append(Eigenvalue(real=hess_ii))
        
        return eigenvalues
    
    def zero_manifold(self, points: List[List[float]], 
                      tolerance: float = 1e-6) -> List[List[float]]:
        """
        Find points where V(x) ≈ 0.
        """
        return [p for p in points if abs(self.value(p)) < tolerance]


# =============================================================================
# GRADIENT FLOW
# =============================================================================

@dataclass
class GradientFlow:
    """
    Gradient flow dynamics.
    
    dx/dt = -∇V(x)
    """
    
    potential: Potential
    step_size: float = 0.01
    max_steps: int = 1000
    tolerance: float = 1e-6
    
    def step(self, x: List[float]) -> List[float]:
        """Single gradient descent step."""
        grad = self.potential.gradient(x)
        return [xi - self.step_size * gi for xi, gi in zip(x, grad)]
    
    def flow(self, x0: List[float]) -> List[List[float]]:
        """
        Compute gradient flow trajectory.
        
        Returns list of points along trajectory.
        """
        trajectory = [list(x0)]
        x = list(x0)
        
        for _ in range(self.max_steps):
            x_new = self.step(x)
            trajectory.append(x_new)
            
            # Check convergence
            dist = math.sqrt(sum((a - b)**2 for a, b in zip(x, x_new)))
            if dist < self.tolerance:
                break
            
            x = x_new
        
        return trajectory
    
    def find_minimum(self, x0: List[float]) -> Tuple[List[float], float]:
        """Find local minimum starting from x0."""
        trajectory = self.flow(x0)
        final = trajectory[-1]
        return final, self.potential.value(final)
    
    def stability_at_minimum(self, x: List[float]) -> StabilityAnalysis:
        """Analyze stability at local minimum."""
        eigenvalues = self.potential.hessian_eigenvalues(x)
        
        # For gradient flow, stability eigenvalues are -Hessian eigenvalues
        stability_eigs = [Eigenvalue(real=-e.real, imag=-e.imag) for e in eigenvalues]
        
        analysis = StabilityAnalysis(
            equilibrium=x,
            eigenvalues=stability_eigs
        )
        analysis.classify()
        
        return analysis


# =============================================================================
# ZERO-POINT DYNAMICS
# =============================================================================

@dataclass
class ZeroPointDynamics:
    """
    Dynamics specialized for zero-point systems.
    
    The zero point is a distinguished equilibrium.
    """
    
    dimension: int = 3
    
    # Potential centered at zero
    potential: Potential = None
    
    # Flow
    flow: GradientFlow = None
    
    # Metric
    metric: Metric = field(default_factory=Metric)
    
    def __post_init__(self):
        if self.potential is None:
            # Default: κ-potential (distance to zero)
            def kappa_potential(x):
                return 0.5 * sum(xi**2 for xi in x)
            
            self.potential = Potential(
                name="κ",
                potential_fn=kappa_potential
            )
        
        if self.flow is None:
            self.flow = GradientFlow(potential=self.potential)
    
    def zero_point(self) -> List[float]:
        """The zero point."""
        return [0.0] * self.dimension
    
    def is_at_zero(self, x: List[float], tolerance: float = 1e-6) -> bool:
        """Check if x is at zero point."""
        return self.metric.distance(x, self.zero_point()) < tolerance
    
    def flow_to_zero(self, x0: List[float]) -> List[List[float]]:
        """Flow from x0 toward zero."""
        return self.flow.flow(x0)
    
    def convergence_time(self, x0: List[float]) -> int:
        """Steps to converge to zero."""
        trajectory = self.flow_to_zero(x0)
        return len(trajectory)
    
    def stability_at_zero(self) -> StabilityAnalysis:
        """Analyze stability of zero point."""
        return self.flow.stability_at_minimum(self.zero_point())
    
    def basin_of_attraction(self, n_samples: int = 100) -> float:
        """Estimate basin of attraction radius."""
        import random
        
        converged = 0
        max_radius = 2.0
        
        for _ in range(n_samples):
            # Random point
            x0 = [random.uniform(-max_radius, max_radius) for _ in range(self.dimension)]
            
            # Flow
            final, _ = self.flow.find_minimum(x0)
            
            if self.is_at_zero(final, tolerance=0.1):
                converged += 1
        
        return converged / n_samples


# =============================================================================
# VALIDATION
# =============================================================================

def validate_dynamics() -> bool:
    """Validate dynamics module."""
    
    # Test Metric
    metric = Metric(MetricType.EUCLIDEAN)
    d = metric.distance([0, 0], [3, 4])
    assert abs(d - 5.0) < 1e-10
    
    # Test CenterFinder
    finder = CenterFinder()
    points = [[0, 0], [2, 0], [1, 1]]
    center = finder.geometric_center(points)
    assert abs(center[0] - 1.0) < 1e-10
    assert abs(center[1] - 1/3) < 1e-10
    
    # Test Potential
    pot = Potential()
    v = pot.value([1, 0, 0])
    assert abs(v - 0.5) < 1e-10
    
    grad = pot.gradient([1, 0, 0])
    assert abs(grad[0] - 1.0) < 0.1
    
    # Test GradientFlow
    flow = GradientFlow(pot)
    trajectory = flow.flow([1, 0, 0])
    assert len(trajectory) > 1
    
    final, _ = flow.find_minimum([1, 0, 0])
    assert abs(final[0]) < 0.1
    
    # Test StabilityAnalysis
    eigs = [Eigenvalue(real=-1), Eigenvalue(real=-2)]
    analysis = StabilityAnalysis([0, 0], eigs)
    assert analysis.classify() == StabilityType.ATTRACTOR
    
    # Test ZeroPointDynamics
    zpd = ZeroPointDynamics(dimension=3)
    assert zpd.zero_point() == [0, 0, 0]
    
    trajectory = zpd.flow_to_zero([1, 1, 1])
    assert len(trajectory) > 0
    
    return True


if __name__ == "__main__":
    print("Validating Zero-Point Dynamics Module...")
    assert validate_dynamics()
    print("✓ Dynamics module validated")
    
    # Demo
    print("\n=== Zero-Point Dynamics Demo ===")
    
    # Create dynamics
    zpd = ZeroPointDynamics(dimension=3)
    
    print("\n1. Zero Point:")
    print(f"   z = {zpd.zero_point()}")
    
    # Flow from initial point
    x0 = [2.0, 1.0, 0.5]
    print(f"\n2. Gradient Flow from {x0}:")
    
    trajectory = zpd.flow_to_zero(x0)
    print(f"   Steps to converge: {len(trajectory)}")
    print(f"   Final point: {[f'{x:.4f}' for x in trajectory[-1]]}")
    
    # Stability
    print("\n3. Stability at Zero:")
    stability = zpd.stability_at_zero()
    print(f"   Type: {stability.stability_type.value}")
    print(f"   Stable dimension: {stability.stable_dim}")
    print(f"   Is hyperbolic: {stability.is_hyperbolic()}")
    
    # Basin of attraction
    print("\n4. Basin of Attraction:")
    basin_prob = zpd.basin_of_attraction(n_samples=50)
    print(f"   Convergence probability: {basin_prob:.2%}")
    
    # Show trajectory
    print("\n5. Trajectory Sample:")
    for i in [0, len(trajectory)//4, len(trajectory)//2, -1]:
        point = trajectory[i]
        pot = zpd.potential.value(point)
        print(f"   t={i:4d}: {[f'{x:.4f}' for x in point]}, V={pot:.6f}")
