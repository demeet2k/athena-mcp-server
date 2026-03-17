"""
ATHENA OS - HOLOGRAPHIC ROTATION PROTOCOL
==========================================
Texture: The Theory of Texture (H, D, λ)

From Holographic_Rotation_Protocol.docx:

TEXTURE TRIPLE:
    (H, D, λ) - Three fundamental texture parameters
    
    H: Information entropy rate
       - Measures unpredictability/randomness
       - High H = rough texture
       
    D: Effective/fractal dimension
       - Measures geometric complexity
       - High D = complex structure
       
    λ: Spectral gap
       - Measures mixing rate/decay
       - High λ = fast mixing, smooth dynamics

TEXTURE FUNCTIONAL:
    T = T(H, D, λ) ∈ [0, ∞)
    
    Monotone in H and D
    Monotone in λ (mixing convention) or 1/λ (glassy convention)

BINDING ENERGY:
    E_bind(S): Robustness of structure S
    
    Texture inequality:
        T_medium ≤ E_bind(S)
    
    For structure to persist, binding must exceed texture.

COHERENCE EVOLUTION:
    dC/dt = -T · C
    
    Structures decay at rate proportional to texture.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable, Any
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod


# =============================================================================
# TEXTURE PARAMETERS
# =============================================================================

@dataclass
class TextureTriple:
    """
    Texture triple (H, D, λ).
    
    H: Information entropy rate
    D: Effective/fractal dimension  
    λ: Spectral gap
    
    Optional scale parameter for resolution tracking.
    """
    
    H: float = 0.0       # Entropy rate
    D: float = 1.0       # Dimension
    lam: float = 1.0     # Spectral gap (λ)
    
    scale: float = 1.0   # Resolution/scale parameter
    confidence: float = 1.0  # Estimation confidence
    
    def __post_init__(self):
        """Validate and normalize parameters."""
        self.H = max(0.0, self.H)
        self.D = max(0.0, self.D)
        self.lam = max(0.0, self.lam)
    
    def __str__(self) -> str:
        return f"(H={self.H:.3f}, D={self.D:.3f}, λ={self.lam:.3f})"
    
    def __repr__(self) -> str:
        return f"TextureTriple({self})"
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.H, self.D, self.lam])
    
    @classmethod
    def from_array(cls, arr: np.ndarray, **kwargs) -> 'TextureTriple':
        """Create from numpy array."""
        return cls(H=arr[0], D=arr[1], lam=arr[2], **kwargs)
    
    def distance(self, other: 'TextureTriple') -> float:
        """Euclidean distance between texture triples."""
        return float(np.linalg.norm(self.to_array() - other.to_array()))
    
    @property
    def roughness(self) -> float:
        """Combined roughness measure."""
        return self.H * self.D / (self.lam + 0.01)
    
    @property
    def smoothness(self) -> float:
        """Inverse of roughness."""
        return 1.0 / (self.roughness + 0.01)


# =============================================================================
# TEXTURE ESTIMATORS
# =============================================================================

class EntropyEstimator:
    """
    Estimates information entropy rate H.
    
    Methods:
    - Shannon entropy from symbol frequencies
    - Block entropy rate
    - Compression-based estimation
    """
    
    @staticmethod
    def shannon_entropy(data: np.ndarray) -> float:
        """
        Compute Shannon entropy H(X).
        
        H(X) = -Σ p(x) log p(x)
        """
        if len(data) == 0:
            return 0.0
        
        # Get unique values and counts
        unique, counts = np.unique(data, return_counts=True)
        probs = counts / len(data)
        
        # Compute entropy
        h = 0.0
        for p in probs:
            if p > 0:
                h -= p * np.log(p)
        
        return float(h)
    
    @staticmethod
    def block_entropy_rate(sequence: np.ndarray, block_size: int = 2) -> float:
        """
        Estimate entropy rate from block entropies.
        
        H_rate ≈ H(X_1,...,X_n) / n for large n
        """
        n = len(sequence)
        if n < block_size:
            return EntropyEstimator.shannon_entropy(sequence)
        
        # Create blocks
        n_blocks = n // block_size
        blocks = []
        for i in range(n_blocks):
            block = tuple(sequence[i*block_size:(i+1)*block_size])
            blocks.append(block)
        
        # Count block frequencies
        unique_blocks = list(set(blocks))
        counts = [blocks.count(b) for b in unique_blocks]
        probs = np.array(counts) / len(blocks)
        
        # Block entropy
        h_block = 0.0
        for p in probs:
            if p > 0:
                h_block -= p * np.log(p)
        
        # Entropy rate is block entropy divided by block size
        return h_block / block_size
    
    @staticmethod
    def conditional_entropy(joint_data: np.ndarray) -> float:
        """
        Estimate conditional entropy H(X|Y).
        
        joint_data: Array of (x, y) pairs
        """
        if len(joint_data) == 0:
            return 0.0
        
        # Joint entropy H(X,Y)
        h_joint = EntropyEstimator.shannon_entropy(
            np.array([hash(tuple(row)) for row in joint_data])
        )
        
        # Marginal entropy H(Y)
        h_y = EntropyEstimator.shannon_entropy(joint_data[:, 1])
        
        # H(X|Y) = H(X,Y) - H(Y)
        return max(0.0, h_joint - h_y)


class DimensionEstimator:
    """
    Estimates effective/fractal dimension D.
    
    Methods:
    - Box-counting dimension
    - Correlation dimension
    - Participation ratio
    """
    
    @staticmethod
    def box_counting(points: np.ndarray, 
                    box_sizes: Optional[List[float]] = None) -> float:
        """
        Estimate box-counting dimension.
        
        D = lim_{ε→0} log N(ε) / log(1/ε)
        """
        if len(points) < 2:
            return 0.0
        
        # Default box sizes
        if box_sizes is None:
            max_range = np.max(np.ptp(points, axis=0))
            if max_range == 0:
                return 0.0
            box_sizes = [max_range / (2**i) for i in range(1, 8)]
        
        counts = []
        valid_sizes = []
        
        for size in box_sizes:
            if size <= 0:
                continue
            # Count non-empty boxes
            boxes = np.floor(points / size).astype(int)
            n_boxes = len(np.unique(boxes, axis=0))
            if n_boxes > 0:
                counts.append(np.log(n_boxes))
                valid_sizes.append(np.log(1/size))
        
        if len(counts) < 2:
            return float(points.shape[1]) if len(points.shape) > 1 else 1.0
        
        # Linear regression for slope
        slope, _ = np.polyfit(valid_sizes, counts, 1)
        return float(slope)
    
    @staticmethod
    def correlation_dimension(points: np.ndarray, 
                             n_samples: int = 1000) -> float:
        """
        Estimate correlation dimension.
        
        D_2 = lim_{r→0} log C(r) / log r
        """
        n = len(points)
        if n < 2:
            return 0.0
        
        # Sample pairs for efficiency
        if n > n_samples:
            idx = np.random.choice(n, n_samples, replace=False)
            points = points[idx]
            n = n_samples
        
        # Compute pairwise distances
        distances = []
        for i in range(n):
            for j in range(i+1, n):
                d = np.linalg.norm(points[i] - points[j])
                if d > 0:
                    distances.append(d)
        
        if len(distances) < 10:
            return 1.0
        
        distances = np.array(distances)
        
        # Correlation integral at various scales
        r_values = np.percentile(distances, [10, 25, 50, 75, 90])
        c_values = []
        
        for r in r_values:
            c = np.sum(distances < r) / (n * (n-1) / 2)
            if c > 0:
                c_values.append((np.log(r), np.log(c)))
        
        if len(c_values) < 2:
            return 1.0
        
        # Linear fit
        x = [v[0] for v in c_values]
        y = [v[1] for v in c_values]
        slope, _ = np.polyfit(x, y, 1)
        
        return float(max(0, slope))
    
    @staticmethod
    def participation_ratio(weights: np.ndarray) -> float:
        """
        Compute participation ratio (effective dimension).
        
        PR = (Σ w_i)² / Σ w_i²
        
        Measures how many components participate.
        """
        weights = np.abs(weights)
        if np.sum(weights) == 0:
            return 0.0
        
        return float((np.sum(weights)**2) / (np.sum(weights**2) + 1e-10))


class SpectralEstimator:
    """
    Estimates spectral gap λ.
    
    Methods:
    - From transition matrix eigenvalues
    - From correlation decay
    - From Laplacian eigenvalues
    """
    
    @staticmethod
    def from_transition_matrix(P: np.ndarray) -> float:
        """
        Compute spectral gap from Markov transition matrix.
        
        λ = 1 - max{|λ_i| : λ_i ≠ 1}
        """
        eigenvalues = np.linalg.eigvals(P)
        eigenvalues = np.sort(np.abs(eigenvalues))[::-1]
        
        if len(eigenvalues) < 2:
            return 1.0
        
        # Gap is 1 minus second largest eigenvalue
        return float(1.0 - eigenvalues[1])
    
    @staticmethod
    def from_correlation_decay(correlations: np.ndarray) -> float:
        """
        Estimate spectral gap from correlation decay.
        
        Corr(n) ~ exp(-λn) implies λ from decay rate.
        """
        n = len(correlations)
        if n < 2:
            return 1.0
        
        # Filter positive correlations
        positive_idx = np.where(np.abs(correlations) > 1e-10)[0]
        if len(positive_idx) < 2:
            return 1.0
        
        # Log-linear fit for decay rate
        y = np.log(np.abs(correlations[positive_idx]) + 1e-10)
        x = positive_idx
        
        slope, _ = np.polyfit(x, y, 1)
        
        return float(-slope) if slope < 0 else 0.01
    
    @staticmethod
    def from_laplacian(L: np.ndarray) -> float:
        """
        Compute spectral gap from graph Laplacian.
        
        λ = smallest nonzero eigenvalue of -L
        """
        eigenvalues = np.linalg.eigvalsh(L)
        eigenvalues = np.sort(np.abs(eigenvalues))
        
        # Find smallest nonzero eigenvalue
        for ev in eigenvalues:
            if ev > 1e-10:
                return float(ev)
        
        return 0.0


# =============================================================================
# TEXTURE FUNCTIONAL
# =============================================================================

class TextureFunctional:
    """
    Combined texture functional T(H, D, λ).
    
    Properties:
    - Monotone increasing in H and D
    - Configurable in λ (mixing vs glassy convention)
    """
    
    def __init__(self, 
                 alpha: float = 1.0,
                 beta: float = 1.0,
                 gamma: float = 1.0,
                 glassy: bool = False):
        """
        Initialize texture functional.
        
        Args:
            alpha: Weight for entropy H
            beta: Weight for dimension D
            gamma: Weight for spectral λ
            glassy: If True, use 1/λ (glassy convention)
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.glassy = glassy
    
    def __call__(self, triple: TextureTriple) -> float:
        """Compute texture value."""
        H, D, lam = triple.H, triple.D, triple.lam
        
        # Spectral contribution
        if self.glassy:
            spec = 1.0 / (lam + 0.01)
        else:
            spec = lam
        
        # Combined texture
        return self.alpha * H + self.beta * D + self.gamma * spec
    
    def gradient(self, triple: TextureTriple) -> np.ndarray:
        """Compute gradient ∂T/∂(H, D, λ)."""
        if self.glassy:
            dlam = -self.gamma / (triple.lam + 0.01)**2
        else:
            dlam = self.gamma
        
        return np.array([self.alpha, self.beta, dlam])


# =============================================================================
# BINDING ENERGY
# =============================================================================

@dataclass
class BindingEnergy:
    """
    Binding energy of a structure.
    
    E_bind measures how robustly a structure is embedded in the medium.
    
    Static: KL divergence between conditioned and unconditioned measures
    Dynamic: Rate of divergence over time
    """
    
    static_energy: float = 0.0
    dynamic_energy: float = 0.0
    structure_id: str = ""
    
    @property
    def total(self) -> float:
        """Total binding energy."""
        return self.static_energy + self.dynamic_energy
    
    @classmethod
    def from_kl_divergence(cls, p: np.ndarray, q: np.ndarray,
                           structure_id: str = "") -> 'BindingEnergy':
        """
        Compute static binding energy from KL divergence.
        
        E_bind = D(P||Q) = Σ p log(p/q)
        """
        # Ensure valid probability distributions
        p = np.clip(p, 1e-10, 1.0)
        q = np.clip(q, 1e-10, 1.0)
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        kl = float(np.sum(p * np.log(p / q)))
        
        return cls(static_energy=kl, structure_id=structure_id)


# =============================================================================
# COHERENCE EVOLUTION
# =============================================================================

@dataclass
class CoherenceTracker:
    """
    Track coherence evolution under texture.
    
    dC/dt = -T · C
    
    Solution: C(t) = C(0) exp(-T·t)
    """
    
    initial_coherence: float = 1.0
    texture: float = 0.0
    
    history: List[Tuple[float, float]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize history."""
        self.history = [(0.0, self.initial_coherence)]
    
    def coherence_at(self, t: float) -> float:
        """Compute coherence at time t."""
        return self.initial_coherence * np.exp(-self.texture * t)
    
    def half_life(self) -> float:
        """Compute half-life of coherence."""
        if self.texture <= 0:
            return float('inf')
        return np.log(2) / self.texture
    
    def decay_time(self, threshold: float = 0.01) -> float:
        """Time to decay to threshold fraction."""
        if self.texture <= 0:
            return float('inf')
        return -np.log(threshold) / self.texture
    
    def update(self, dt: float) -> float:
        """
        Update coherence by time step dt.
        
        Returns new coherence value.
        """
        t_current = self.history[-1][0]
        c_new = self.coherence_at(t_current + dt)
        self.history.append((t_current + dt, c_new))
        return c_new
    
    def check_persistence(self, binding_energy: float) -> bool:
        """
        Check if structure can persist.
        
        Structure persists if binding_energy >= texture.
        """
        return binding_energy >= self.texture


# =============================================================================
# TEXTURE ANALYZER
# =============================================================================

@dataclass
class TextureAnalyzer:
    """
    Comprehensive texture analysis.
    
    Computes texture triple from various data sources.
    """
    
    def analyze_sequence(self, sequence: np.ndarray) -> TextureTriple:
        """Analyze discrete sequence."""
        H = EntropyEstimator.block_entropy_rate(sequence)
        
        # Embed as 1D points for dimension
        points = sequence.reshape(-1, 1)
        D = DimensionEstimator.participation_ratio(sequence)
        
        # Estimate spectral from autocorrelation
        if len(sequence) > 10:
            autocorr = np.correlate(sequence - np.mean(sequence), 
                                   sequence - np.mean(sequence), 
                                   mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            autocorr = autocorr / (autocorr[0] + 1e-10)
            lam = SpectralEstimator.from_correlation_decay(autocorr[:20])
        else:
            lam = 1.0
        
        return TextureTriple(H=H, D=D, lam=lam)
    
    def analyze_points(self, points: np.ndarray) -> TextureTriple:
        """Analyze point cloud."""
        H = EntropyEstimator.shannon_entropy(
            np.round(points.flatten(), 2)
        )
        D = DimensionEstimator.box_counting(points)
        lam = 1.0  # Default for static points
        
        return TextureTriple(H=H, D=D, lam=lam)
    
    def analyze_transition_matrix(self, P: np.ndarray) -> TextureTriple:
        """Analyze Markov transition matrix."""
        # Entropy rate from stationary distribution
        eigenvalues, eigenvectors = np.linalg.eig(P.T)
        stationary_idx = np.argmax(np.abs(eigenvalues))
        pi = np.abs(eigenvectors[:, stationary_idx])
        pi = pi / np.sum(pi)
        
        H = EntropyEstimator.shannon_entropy(pi)
        D = DimensionEstimator.participation_ratio(pi)
        lam = SpectralEstimator.from_transition_matrix(P)
        
        return TextureTriple(H=H, D=D, lam=lam)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_texture() -> bool:
    """Validate texture module."""
    
    # Test TextureTriple
    t = TextureTriple(H=1.0, D=2.0, lam=0.5)
    assert t.H == 1.0
    assert t.D == 2.0
    assert t.lam == 0.5
    
    arr = t.to_array()
    t2 = TextureTriple.from_array(arr)
    assert t2.H == t.H
    
    dist = t.distance(TextureTriple(H=2.0, D=2.0, lam=0.5))
    assert dist == 1.0
    
    # Test EntropyEstimator
    uniform = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    h_uniform = EntropyEstimator.shannon_entropy(uniform)
    assert h_uniform > 0
    
    constant = np.array([1, 1, 1, 1, 1, 1, 1, 1])
    h_constant = EntropyEstimator.shannon_entropy(constant)
    assert h_constant == 0
    
    # Block entropy
    h_rate = EntropyEstimator.block_entropy_rate(uniform, block_size=2)
    assert h_rate >= 0
    
    # Test DimensionEstimator
    line_points = np.array([[i, 0] for i in range(100)])
    d_line = DimensionEstimator.box_counting(line_points)
    assert 0.5 < d_line < 1.5  # Should be near 1
    
    plane_points = np.random.rand(200, 2)
    d_plane = DimensionEstimator.box_counting(plane_points)
    assert 1.5 < d_plane < 2.5  # Should be near 2
    
    # Participation ratio
    uniform_weights = np.ones(10)
    pr = DimensionEstimator.participation_ratio(uniform_weights)
    assert pr == 10.0
    
    # Test SpectralEstimator
    P = np.array([[0.5, 0.5], [0.5, 0.5]])
    gap = SpectralEstimator.from_transition_matrix(P)
    assert gap == 1.0  # Fast mixing
    
    P_slow = np.array([[0.99, 0.01], [0.01, 0.99]])
    gap_slow = SpectralEstimator.from_transition_matrix(P_slow)
    assert gap_slow < gap  # Slower mixing
    
    # Test TextureFunctional
    func = TextureFunctional(alpha=1.0, beta=1.0, gamma=1.0)
    texture_val = func(t)
    assert texture_val > 0
    
    # Test BindingEnergy
    p = np.array([0.5, 0.5])
    q = np.array([0.9, 0.1])
    be = BindingEnergy.from_kl_divergence(p, q)
    assert be.static_energy > 0
    
    # Test CoherenceTracker
    tracker = CoherenceTracker(initial_coherence=1.0, texture=0.1)
    
    c_1 = tracker.coherence_at(1.0)
    assert c_1 < 1.0
    
    hl = tracker.half_life()
    assert hl > 0
    
    c_hl = tracker.coherence_at(hl)
    assert abs(c_hl - 0.5) < 0.01
    
    # Test TextureAnalyzer
    analyzer = TextureAnalyzer()
    
    seq = np.random.randint(0, 5, 100)
    triple = analyzer.analyze_sequence(seq)
    assert triple.H > 0
    
    return True


if __name__ == "__main__":
    print("Validating Texture...")
    assert validate_texture()
    print("✓ Texture module validated")
