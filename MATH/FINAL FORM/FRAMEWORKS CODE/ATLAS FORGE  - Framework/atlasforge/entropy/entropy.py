"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ENTROPY AND INFORMATION GEOMETRY                          ║
║                                                                              ║
║  Information-Theoretic Functionals and Σ-Pole Realization                    ║
║                                                                              ║
║  Core Principle:                                                             ║
║    The Σ (stochastic/probabilistic) pole is characterized by entropy         ║
║    functionals, which measure uncertainty and information content.           ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - Shannon entropy: H[p] = -Σ p_i log p_i                                 ║
║    - Relative entropy (KL divergence): D(p||q) = Σ p_i log(p_i/q_i)        ║
║    - Fisher information: I(θ) = E[(∂log p/∂θ)²]                             ║
║    - Information geometry: Riemannian structure on probability simplex       ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Entropy ↔ uncertainty in stochastic representation                     ║
║    - KL divergence ↔ distance in Cloud representation                       ║
║    - Fisher metric ↔ natural geometry of parameter space                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# BASIC ENTROPY FUNCTIONALS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EntropyFunctional:
    """
    Collection of entropy functionals.
    
    All functionals operate on probability distributions
    (non-negative arrays that sum to 1).
    """
    base: float = np.e  # Logarithm base (e for nats, 2 for bits)
    
    def _normalize(self, p: NDArray) -> NDArray:
        """Normalize to probability distribution."""
        p = np.asarray(p, dtype=np.float64)
        p = np.maximum(p, 0)  # Ensure non-negative
        total = np.sum(p)
        return p / total if total > 0 else p
    
    def shannon_entropy(self, p: NDArray) -> float:
        """
        Shannon entropy: H[p] = -Σ p_i log p_i
        
        Measures average information content / uncertainty.
        Maximum for uniform distribution: log(n)
        """
        p = self._normalize(p)
        # Avoid log(0) by filtering zeros
        mask = p > 0
        return -np.sum(p[mask] * np.log(p[mask]) / np.log(self.base))
    
    def cross_entropy(self, p: NDArray, q: NDArray) -> float:
        """
        Cross-entropy: H(p, q) = -Σ p_i log q_i
        
        Measures average bits needed to encode p using code from q.
        """
        p = self._normalize(p)
        q = self._normalize(q)
        
        # Handle zeros in q
        q = np.maximum(q, 1e-15)
        
        return -np.sum(p * np.log(q) / np.log(self.base))
    
    def kl_divergence(self, p: NDArray, q: NDArray) -> float:
        """
        Kullback-Leibler divergence: D_KL(p||q) = Σ p_i log(p_i/q_i)
        
        Measures information lost when q is used to approximate p.
        Not symmetric: D(p||q) ≠ D(q||p)
        """
        p = self._normalize(p)
        q = self._normalize(q)
        
        # Handle zeros
        mask = (p > 0) & (q > 0)
        return np.sum(p[mask] * np.log(p[mask] / q[mask]) / np.log(self.base))
    
    def js_divergence(self, p: NDArray, q: NDArray) -> float:
        """
        Jensen-Shannon divergence: JS(p||q) = (D(p||m) + D(q||m))/2
        where m = (p + q)/2
        
        Symmetric and bounded: 0 ≤ JS ≤ log(2)
        """
        p = self._normalize(p)
        q = self._normalize(q)
        m = (p + q) / 2
        
        return (self.kl_divergence(p, m) + self.kl_divergence(q, m)) / 2
    
    def renyi_entropy(self, p: NDArray, alpha: float) -> float:
        """
        Rényi entropy: H_α[p] = (1/(1-α)) log(Σ p_i^α)
        
        Generalizes Shannon entropy (α → 1).
        α = 0: Hartley entropy (log of support size)
        α = 2: Collision entropy
        α = ∞: Min-entropy
        """
        p = self._normalize(p)
        
        if abs(alpha - 1) < 1e-10:
            return self.shannon_entropy(p)
        
        if alpha == 0:
            return np.log(np.sum(p > 0)) / np.log(self.base)
        
        if alpha == np.inf:
            return -np.log(np.max(p)) / np.log(self.base)
        
        return np.log(np.sum(p ** alpha)) / ((1 - alpha) * np.log(self.base))
    
    def tsallis_entropy(self, p: NDArray, q: float) -> float:
        """
        Tsallis entropy: S_q[p] = (1 - Σ p_i^q)/(q - 1)
        
        Non-additive generalization of Shannon entropy.
        q → 1: Shannon entropy
        """
        p = self._normalize(p)
        
        if abs(q - 1) < 1e-10:
            return self.shannon_entropy(p)
        
        return (1 - np.sum(p ** q)) / (q - 1)


# ═══════════════════════════════════════════════════════════════════════════════
# FISHER INFORMATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FisherInformation:
    """
    Fisher information matrix for parametric families.
    
    I(θ)_{ij} = E[(∂log p/∂θ_i)(∂log p/∂θ_j)]
    
    Measures how much information data X carries about parameter θ.
    """
    
    @staticmethod
    def for_bernoulli(p: float) -> float:
        """Fisher information for Bernoulli(p): I(p) = 1/(p(1-p))"""
        if p <= 0 or p >= 1:
            return float('inf')
        return 1 / (p * (1 - p))
    
    @staticmethod
    def for_gaussian_mean(sigma: float) -> float:
        """Fisher info for N(μ, σ²) w.r.t. μ: I(μ) = 1/σ²"""
        return 1 / (sigma ** 2)
    
    @staticmethod
    def for_gaussian_variance(sigma: float) -> float:
        """Fisher info for N(μ, σ²) w.r.t. σ²: I(σ²) = 1/(2σ⁴)"""
        return 1 / (2 * sigma ** 4)
    
    @staticmethod
    def for_exponential(rate: float) -> float:
        """Fisher info for Exp(λ): I(λ) = 1/λ²"""
        return 1 / (rate ** 2)
    
    def numerical_estimate(self, log_likelihood: Callable[[float], float],
                          theta: float, h: float = 1e-5) -> float:
        """
        Numerically estimate Fisher information.
        
        Uses I(θ) ≈ -E[∂²log p/∂θ²]
        """
        # Second derivative via finite differences
        d2 = (log_likelihood(theta + h) - 2 * log_likelihood(theta) + 
              log_likelihood(theta - h)) / (h ** 2)
        return -d2
    
    def matrix_for_multinomial(self, p: NDArray) -> NDArray[np.float64]:
        """
        Fisher information matrix for multinomial distribution.
        
        I_{ij} = δ_{ij}/p_i - 1
        (in natural parametrization)
        """
        p = np.asarray(p, dtype=np.float64)
        p = p / np.sum(p)
        
        n = len(p)
        I = np.diag(1 / p) - np.ones((n, n))
        
        return I


# ═══════════════════════════════════════════════════════════════════════════════
# INFORMATION GEOMETRY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProbabilitySimplex:
    """
    The probability simplex Δ^{n-1} = {p ∈ ℝ^n : p_i ≥ 0, Σp_i = 1}.
    
    This is the natural configuration space for the Σ-pole.
    """
    dimension: int
    
    @property
    def embedding_dim(self) -> int:
        """Ambient dimension."""
        return self.dimension
    
    @property
    def intrinsic_dim(self) -> int:
        """Intrinsic dimension (one less due to sum constraint)."""
        return self.dimension - 1
    
    def uniform(self) -> NDArray[np.float64]:
        """Uniform distribution (center of simplex)."""
        return np.ones(self.dimension) / self.dimension
    
    def vertices(self) -> List[NDArray[np.float64]]:
        """Vertices (pure states)."""
        return [np.eye(1, self.dimension, i).flatten() for i in range(self.dimension)]
    
    def random_point(self, rng: np.random.Generator = None) -> NDArray[np.float64]:
        """Sample uniformly from simplex."""
        if rng is None:
            rng = np.random.default_rng()
        
        # Dirichlet(1, 1, ..., 1) gives uniform on simplex
        return rng.dirichlet(np.ones(self.dimension))
    
    def project(self, x: NDArray) -> NDArray[np.float64]:
        """Project point onto simplex."""
        # Simple projection: normalize after clipping negatives
        x = np.maximum(x, 0)
        total = np.sum(x)
        return x / total if total > 0 else self.uniform()


@dataclass
class FisherRaoMetric:
    """
    Fisher-Rao metric (information metric) on probability simplex.
    
    ds² = Σ (dp_i)²/p_i
    
    This is the unique metric (up to scale) that is:
    - Invariant under reparametrization
    - Induced by the Fisher information
    """
    
    def metric_tensor(self, p: NDArray) -> NDArray[np.float64]:
        """
        Metric tensor g_{ij}(p) = δ_{ij}/p_i.
        
        Returns n×n matrix.
        """
        return np.diag(1 / p)
    
    def geodesic_distance(self, p: NDArray, q: NDArray) -> float:
        """
        Geodesic (Fisher-Rao) distance between distributions.
        
        d(p, q) = 2 arccos(Σ √(p_i q_i))
        """
        p = np.asarray(p, dtype=np.float64)
        q = np.asarray(q, dtype=np.float64)
        
        # Normalize
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        # Bhattacharyya coefficient
        bc = np.sum(np.sqrt(p * q))
        
        # Clamp for numerical stability
        bc = np.clip(bc, -1, 1)
        
        return 2 * np.arccos(bc)
    
    def hellinger_distance(self, p: NDArray, q: NDArray) -> float:
        """
        Hellinger distance: H(p, q) = √(1 - Σ√(p_i q_i))
        
        Related to geodesic distance: H = √2 sin(d/4)
        """
        p = np.asarray(p, dtype=np.float64)
        q = np.asarray(q, dtype=np.float64)
        
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        bc = np.sum(np.sqrt(p * q))
        return np.sqrt(1 - bc)
    
    def exponential_map(self, p: NDArray, v: NDArray, t: float = 1.0
                       ) -> NDArray[np.float64]:
        """
        Exponential map: move from p in direction v for time t.
        
        On the simplex with Fisher metric, geodesics are great circles
        on the sphere when embedded via √p.
        """
        # Embed on sphere
        sqrt_p = np.sqrt(p / np.sum(p))
        
        # Normalize tangent vector
        v_norm = np.linalg.norm(v)
        if v_norm < 1e-10:
            return p
        v_unit = v / v_norm
        
        # Great circle
        result = np.cos(t * v_norm) * sqrt_p + np.sin(t * v_norm) * v_unit
        
        # Back to simplex
        return result ** 2


# ═══════════════════════════════════════════════════════════════════════════════
# SIGMA-POLE CONNECTOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SigmaPoleConnector:
    """
    Connect entropy/information geometry to Σ-pole of framework.
    
    The Σ-pole represents stochastic/probabilistic structure.
    """
    entropy: EntropyFunctional = field(default_factory=EntropyFunctional)
    metric: FisherRaoMetric = field(default_factory=FisherRaoMetric)
    
    def state_entropy(self, state: NDArray) -> float:
        """Compute entropy of a state vector."""
        # Interpret state as unnormalized distribution
        probs = np.abs(state) ** 2
        probs = probs / np.sum(probs)
        return self.entropy.shannon_entropy(probs)
    
    def state_distance(self, state1: NDArray, state2: NDArray) -> float:
        """Fisher-Rao distance between states."""
        p1 = np.abs(state1) ** 2
        p2 = np.abs(state2) ** 2
        return self.metric.geodesic_distance(p1, p2)
    
    def entropy_gradient(self, p: NDArray) -> NDArray[np.float64]:
        """
        Gradient of Shannon entropy on simplex.
        
        ∂H/∂p_i = -(1 + log p_i)
        """
        p = np.asarray(p, dtype=np.float64)
        p = np.maximum(p, 1e-15)
        return -(1 + np.log(p))
    
    def maximum_entropy_distribution(self, constraints: Dict[str, float],
                                    support_size: int) -> NDArray[np.float64]:
        """
        Find maximum entropy distribution satisfying constraints.
        
        Uses exponential family form: p_i ∝ exp(Σ_k λ_k f_k(i))
        
        Args:
            constraints: Dict mapping constraint name to expected value
                        Currently supports 'mean' for linear constraint
            support_size: Number of outcomes
        """
        # For simple mean constraint: p_i ∝ exp(λ·i)
        if 'mean' in constraints:
            target_mean = constraints['mean']
            
            # Binary search for λ
            def compute_mean(lam):
                weights = np.exp(lam * np.arange(support_size))
                probs = weights / np.sum(weights)
                return np.sum(np.arange(support_size) * probs)
            
            lam_lo, lam_hi = -10, 10
            for _ in range(100):
                lam_mid = (lam_lo + lam_hi) / 2
                current_mean = compute_mean(lam_mid)
                if current_mean < target_mean:
                    lam_lo = lam_mid
                else:
                    lam_hi = lam_mid
            
            weights = np.exp(lam_mid * np.arange(support_size))
            return weights / np.sum(weights)
        
        # Default: uniform
        return np.ones(support_size) / support_size
    
    def relative_entropy_to_uniform(self, p: NDArray) -> float:
        """
        KL divergence from p to uniform distribution.
        
        D(p || u) = log(n) - H(p)
        """
        n = len(p)
        return np.log(n) - self.entropy.shannon_entropy(p)
    
    def mutual_information(self, joint: NDArray) -> float:
        """
        Mutual information I(X; Y) from joint distribution.
        
        I(X; Y) = H(X) + H(Y) - H(X, Y)
        """
        # Marginals
        p_x = np.sum(joint, axis=1)
        p_y = np.sum(joint, axis=0)
        
        H_X = self.entropy.shannon_entropy(p_x)
        H_Y = self.entropy.shannon_entropy(p_y)
        H_XY = self.entropy.shannon_entropy(joint.flatten())
        
        return H_X + H_Y - H_XY


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def shannon_entropy(p: NDArray, base: float = np.e) -> float:
    """Shannon entropy H[p] = -Σ p_i log p_i."""
    return EntropyFunctional(base=base).shannon_entropy(p)


def kl_divergence(p: NDArray, q: NDArray) -> float:
    """KL divergence D(p||q)."""
    return EntropyFunctional().kl_divergence(p, q)


def js_divergence(p: NDArray, q: NDArray) -> float:
    """Jensen-Shannon divergence."""
    return EntropyFunctional().js_divergence(p, q)


def fisher_rao_distance(p: NDArray, q: NDArray) -> float:
    """Fisher-Rao geodesic distance."""
    return FisherRaoMetric().geodesic_distance(p, q)


def hellinger_distance(p: NDArray, q: NDArray) -> float:
    """Hellinger distance."""
    return FisherRaoMetric().hellinger_distance(p, q)


def mutual_information(joint: NDArray) -> float:
    """Mutual information from joint distribution."""
    return SigmaPoleConnector().mutual_information(joint)


def maximum_entropy(constraints: Dict[str, float], support_size: int) -> NDArray:
    """Maximum entropy distribution."""
    return SigmaPoleConnector().maximum_entropy_distribution(constraints, support_size)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Entropy
    'EntropyFunctional',
    
    # Fisher information
    'FisherInformation',
    
    # Information geometry
    'ProbabilitySimplex',
    'FisherRaoMetric',
    
    # Framework connection
    'SigmaPoleConnector',
    
    # Functions
    'shannon_entropy',
    'kl_divergence',
    'js_divergence',
    'fisher_rao_distance',
    'hellinger_distance',
    'mutual_information',
    'maximum_entropy',
]
