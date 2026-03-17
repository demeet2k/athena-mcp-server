"""
ATHENA OS - Quantum Hugging Framework
=====================================
Quantum Hugging: Observer-Matched Statistical Masking

From The_Quantum_Hugging_Framework.docx §5:

OBSERVER MODEL:
    - Feature map φ: ℝ* → ℝᵈ (measurable statistics)
    - Null distribution F₀ over features
    - Detection functional D_O: ℝ* → [0,1]

QUANTUM HUGGING OBJECTIVE:
    Given S, ε, φ, F₀, construct encoding E such that:
    1. E(S) is Omega-valid
    2. φ(E(S)) matches F₀ as closely as possible

EXPONENTIAL FAMILY HUGGING:
    f_λ(φ) = f₀(φ)·exp(λᵀφ) / Z(λ)
    
    Minimizes KL(f‖f₀) subject to moment constraints
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math
import random

from .omega import PacketSequence, OmegaEncoder, UniformEncoder


# =============================================================================
# FEATURE MAPS
# =============================================================================

class FeatureType(Enum):
    """Types of observable features."""
    
    MEAN = "mean"
    VARIANCE = "variance"
    SKEWNESS = "skewness"
    KURTOSIS = "kurtosis"
    AUTOCORR = "autocorrelation"
    SPECTRUM = "spectrum"
    ENTROPY = "entropy"


@dataclass
class FeatureMap:
    """
    Feature map φ: ℝ* → ℝᵈ.
    
    Extracts measurable statistics from packet sequences.
    """
    
    feature_types: List[FeatureType] = field(default_factory=lambda: [
        FeatureType.MEAN,
        FeatureType.VARIANCE,
        FeatureType.SKEWNESS
    ])
    
    @property
    def dimension(self) -> int:
        """Feature dimension d."""
        return len(self.feature_types)
    
    def extract(self, packets: PacketSequence) -> List[float]:
        """Extract feature vector φ(z)."""
        values = packets.to_list()
        if not values:
            return [0.0] * self.dimension
        
        features = []
        for ft in self.feature_types:
            features.append(self._compute_feature(values, ft))
        
        return features
    
    def _compute_feature(self, values: List[float], 
                        feature_type: FeatureType) -> float:
        """Compute single feature."""
        n = len(values)
        if n == 0:
            return 0.0
        
        if feature_type == FeatureType.MEAN:
            return sum(values) / n
        
        elif feature_type == FeatureType.VARIANCE:
            mean = sum(values) / n
            return sum((x - mean)**2 for x in values) / n
        
        elif feature_type == FeatureType.SKEWNESS:
            mean = sum(values) / n
            var = sum((x - mean)**2 for x in values) / n
            if var < 1e-10:
                return 0.0
            std = math.sqrt(var)
            return sum((x - mean)**3 for x in values) / (n * std**3)
        
        elif feature_type == FeatureType.KURTOSIS:
            mean = sum(values) / n
            var = sum((x - mean)**2 for x in values) / n
            if var < 1e-10:
                return 0.0
            return sum((x - mean)**4 for x in values) / (n * var**2) - 3
        
        elif feature_type == FeatureType.AUTOCORR:
            if n < 2:
                return 0.0
            mean = sum(values) / n
            var = sum((x - mean)**2 for x in values) / n
            if var < 1e-10:
                return 0.0
            autocov = sum((values[i] - mean) * (values[i+1] - mean) 
                         for i in range(n-1)) / (n - 1)
            return autocov / var
        
        elif feature_type == FeatureType.ENTROPY:
            # Discretize and compute entropy
            if n < 2:
                return 0.0
            min_v, max_v = min(values), max(values)
            if max_v - min_v < 1e-10:
                return 0.0
            bins = 10
            counts = [0] * bins
            for v in values:
                idx = min(bins - 1, int((v - min_v) / (max_v - min_v) * bins))
                counts[idx] += 1
            entropy = 0.0
            for c in counts:
                if c > 0:
                    p = c / n
                    entropy -= p * math.log(p + 1e-10)
            return entropy
        
        elif feature_type == FeatureType.SPECTRUM:
            # Simple spectral energy (sum of squares)
            return sum(x**2 for x in values) / n
        
        return 0.0


# =============================================================================
# NULL DISTRIBUTION
# =============================================================================

@dataclass
class NullDistribution:
    """
    Null/baseline feature distribution F₀.
    
    Represents observer's expectation of "normal" behavior.
    """
    
    # Target moments
    mean: List[float] = field(default_factory=list)
    covariance: List[List[float]] = field(default_factory=list)
    
    @property
    def dimension(self) -> int:
        return len(self.mean)
    
    def log_density(self, features: List[float]) -> float:
        """Log density log f₀(φ)."""
        if not self.mean or len(features) != len(self.mean):
            return 0.0
        
        # Gaussian null model
        d = len(features)
        
        # Compute Mahalanobis distance (simplified: diagonal covariance)
        dist = 0.0
        for i in range(d):
            var = self.covariance[i][i] if self.covariance else 1.0
            dist += (features[i] - self.mean[i])**2 / max(var, 1e-10)
        
        return -0.5 * dist - 0.5 * d * math.log(2 * math.pi)
    
    def sample(self) -> List[float]:
        """Sample from null distribution."""
        if not self.mean:
            return []
        
        sample = []
        for i in range(len(self.mean)):
            var = self.covariance[i][i] if self.covariance else 1.0
            sample.append(random.gauss(self.mean[i], math.sqrt(var)))
        
        return sample
    
    @classmethod
    def uniform_null(cls, dim: int) -> 'NullDistribution':
        """Create uniform null (zero mean, unit variance)."""
        return cls(
            mean=[0.0] * dim,
            covariance=[[1.0 if i == j else 0.0 for j in range(dim)] 
                       for i in range(dim)]
        )
    
    @classmethod
    def from_samples(cls, samples: List[List[float]]) -> 'NullDistribution':
        """Estimate null distribution from samples."""
        if not samples:
            return cls()
        
        n = len(samples)
        d = len(samples[0])
        
        # Compute mean
        mean = [sum(s[i] for s in samples) / n for i in range(d)]
        
        # Compute covariance
        cov = [[0.0] * d for _ in range(d)]
        for i in range(d):
            for j in range(d):
                cov[i][j] = sum(
                    (s[i] - mean[i]) * (s[j] - mean[j]) 
                    for s in samples
                ) / n
        
        return cls(mean=mean, covariance=cov)


# =============================================================================
# OBSERVER
# =============================================================================

@dataclass
class Observer:
    """
    Observer with feature map and null model.
    """
    
    name: str = "Observer"
    feature_map: FeatureMap = field(default_factory=FeatureMap)
    null_distribution: NullDistribution = field(default_factory=NullDistribution)
    
    # Detection threshold
    detection_threshold: float = 0.5
    
    def observe(self, packets: PacketSequence) -> List[float]:
        """Extract features from packets."""
        return self.feature_map.extract(packets)
    
    def detection_score(self, packets: PacketSequence) -> float:
        """
        Compute detection score D_O(z) ∈ [0,1].
        
        Higher = more anomalous.
        """
        features = self.observe(packets)
        
        if not self.null_distribution.mean:
            return 0.5
        
        # Compute divergence from null
        log_p = self.null_distribution.log_density(features)
        
        # Convert to probability via sigmoid
        return 1.0 / (1.0 + math.exp(log_p + 5))
    
    def is_detected(self, packets: PacketSequence) -> bool:
        """Check if packets are detected as anomalous."""
        return self.detection_score(packets) > self.detection_threshold
    
    def divergence(self, packets: PacketSequence) -> float:
        """
        Compute KL divergence estimate from null.
        """
        features = self.observe(packets)
        
        if not self.null_distribution.mean:
            return 0.0
        
        # Simplified KL: squared Mahalanobis distance / 2
        d = len(features)
        dist = 0.0
        for i in range(d):
            var = (self.null_distribution.covariance[i][i] 
                   if self.null_distribution.covariance else 1.0)
            dist += (features[i] - self.null_distribution.mean[i])**2 / max(var, 1e-10)
        
        return 0.5 * dist


# =============================================================================
# EXPONENTIAL FAMILY TILTING
# =============================================================================

@dataclass
class ExponentialTilting:
    """
    Exponential family tilting for quantum hugging.
    
    f_λ(φ) = f₀(φ)·exp(λᵀφ) / Z(λ)
    """
    
    null_distribution: NullDistribution
    
    # Tilting parameters
    lambda_params: List[float] = field(default_factory=list)
    
    # Normalization (log partition)
    log_partition: float = 0.0
    
    def tilt(self, features: List[float]) -> float:
        """Compute tilted log density."""
        base = self.null_distribution.log_density(features)
        
        if not self.lambda_params:
            return base
        
        tilt_term = sum(l * f for l, f in zip(self.lambda_params, features))
        
        return base + tilt_term - self.log_partition
    
    def fit_to_moments(self, target_moments: List[float], 
                      learning_rate: float = 0.1,
                      max_iterations: int = 100) -> None:
        """
        Fit λ to achieve target moments.
        
        min_λ KL(f_λ ‖ f₀) s.t. E[φ] = target_moments
        """
        d = len(target_moments)
        
        if not self.lambda_params:
            self.lambda_params = [0.0] * d
        
        for _ in range(max_iterations):
            # Estimate current moments (via sampling)
            samples = [self.null_distribution.sample() for _ in range(100)]
            
            # Importance-weighted moments
            weights = []
            for s in samples:
                tilt = sum(l * f for l, f in zip(self.lambda_params, s))
                weights.append(math.exp(tilt))
            
            total_weight = sum(weights)
            if total_weight < 1e-10:
                break
            
            current_moments = [
                sum(w * s[i] for w, s in zip(weights, samples)) / total_weight
                for i in range(d)
            ]
            
            # Gradient step
            for i in range(d):
                gradient = target_moments[i] - current_moments[i]
                self.lambda_params[i] += learning_rate * gradient
            
            # Update partition
            self.log_partition = math.log(total_weight / len(samples))


# =============================================================================
# QUANTUM HUGGING LAYER
# =============================================================================

@dataclass
class QuantumHuggingLayer:
    """
    Quantum Hugging layer for observer-matched encoding.
    
    Modifies Omega encoding to match observer's null model.
    """
    
    observer: Observer
    base_encoder: OmegaEncoder = None
    
    # Hugging parameters
    hugging_weight: float = 0.5    # Balance: capacity vs stealth
    max_iterations: int = 50
    
    def __post_init__(self):
        if self.base_encoder is None:
            self.base_encoder = UniformEncoder()
    
    def encode_hugged(self, S: float) -> PacketSequence:
        """
        Encode signal with quantum hugging.
        
        Optimizes packets to minimize detection while preserving reconstruction.
        """
        # Initial encoding
        packets = self.base_encoder.encode(S)
        
        # Iteratively adjust to reduce detection
        best_packets = packets
        best_score = self.observer.detection_score(packets)
        
        for _ in range(self.max_iterations):
            # Perturb packets
            perturbed = self._perturb(packets, S)
            
            # Evaluate
            score = self.observer.detection_score(perturbed)
            
            if score < best_score:
                best_packets = perturbed
                best_score = score
                packets = perturbed
        
        return best_packets
    
    def _perturb(self, packets: PacketSequence, 
                 target_sum: float) -> PacketSequence:
        """Perturb packets while preserving sum."""
        if packets.N < 2:
            return packets
        
        # Create perturbed copy
        new_packets = PacketSequence()
        values = packets.to_list()
        
        # Random redistribution
        i, j = random.sample(range(len(values)), 2)
        
        # Transfer amount
        max_transfer = min(
            abs(values[i]),
            self.base_encoder.epsilon - abs(values[j])
        ) * 0.5
        
        if max_transfer > 0:
            transfer = random.uniform(-max_transfer, max_transfer)
            values[i] -= transfer
            values[j] += transfer
        
        for v in values:
            new_packets.add_packet(v)
        
        return new_packets
    
    def hugging_effectiveness(self, packets: PacketSequence) -> float:
        """Measure hugging effectiveness (1 - detection score)."""
        return 1.0 - self.observer.detection_score(packets)
    
    def report(self, S: float, packets: PacketSequence) -> Dict[str, Any]:
        """Generate hugging report."""
        features = self.observer.observe(packets)
        
        return {
            "signal": S,
            "packets": packets.N,
            "reconstruction": packets.total,
            "detection_score": self.observer.detection_score(packets),
            "divergence": self.observer.divergence(packets),
            "features": features,
            "effectiveness": self.hugging_effectiveness(packets),
            "detected": self.observer.is_detected(packets)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hugging() -> bool:
    """Validate quantum hugging module."""
    
    # Test FeatureMap
    fm = FeatureMap()
    packets = PacketSequence()
    for v in [0.1, 0.2, 0.3, 0.2, 0.2]:
        packets.add_packet(v)
    
    features = fm.extract(packets)
    assert len(features) == fm.dimension
    assert abs(features[0] - 0.2) < 0.01  # Mean
    
    # Test NullDistribution
    null = NullDistribution.uniform_null(3)
    assert null.dimension == 3
    
    log_p = null.log_density([0.0, 0.0, 0.0])
    assert log_p > -10
    
    # Test Observer
    observer = Observer(
        feature_map=fm,
        null_distribution=null
    )
    
    score = observer.detection_score(packets)
    assert 0 <= score <= 1
    
    # Test QuantumHuggingLayer
    layer = QuantumHuggingLayer(observer=observer)
    hugged = layer.encode_hugged(1.0)
    
    assert abs(hugged.total - 1.0) < 0.1
    
    report = layer.report(1.0, hugged)
    assert "effectiveness" in report
    
    return True


if __name__ == "__main__":
    print("Validating Quantum Hugging Observer Module...")
    assert validate_hugging()
    print("✓ Hugging module validated")
    
    # Demo
    print("\n=== Quantum Hugging Demo ===")
    
    # Create observer
    fm = FeatureMap(feature_types=[
        FeatureType.MEAN,
        FeatureType.VARIANCE,
        FeatureType.SKEWNESS,
        FeatureType.ENTROPY
    ])
    
    null = NullDistribution(
        mean=[0.0, 0.1, 0.0, 2.0],
        covariance=[
            [0.1, 0, 0, 0],
            [0, 0.05, 0, 0],
            [0, 0, 0.5, 0],
            [0, 0, 0, 0.5]
        ]
    )
    
    observer = Observer(
        name="Gatekeeper",
        feature_map=fm,
        null_distribution=null,
        detection_threshold=0.3
    )
    
    # Create hugging layer
    layer = QuantumHuggingLayer(
        observer=observer,
        hugging_weight=0.7,
        max_iterations=100
    )
    
    # Encode with and without hugging
    S = 2.5
    
    print(f"\nSignal S = {S}")
    print(f"Observer: {observer.name}")
    
    # Without hugging
    plain_packets = layer.base_encoder.encode(S)
    plain_report = layer.report(S, plain_packets)
    
    print(f"\nWithout Hugging:")
    print(f"  Packets: {plain_report['packets']}")
    print(f"  Detection score: {plain_report['detection_score']:.4f}")
    print(f"  Detected: {plain_report['detected']}")
    
    # With hugging
    hugged_packets = layer.encode_hugged(S)
    hugged_report = layer.report(S, hugged_packets)
    
    print(f"\nWith Quantum Hugging:")
    print(f"  Packets: {hugged_report['packets']}")
    print(f"  Detection score: {hugged_report['detection_score']:.4f}")
    print(f"  Effectiveness: {hugged_report['effectiveness']:.4f}")
    print(f"  Detected: {hugged_report['detected']}")
    
    # Improvement
    improvement = plain_report['detection_score'] - hugged_report['detection_score']
    print(f"\nDetection reduction: {improvement:.4f}")
