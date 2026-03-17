"""
ATHENA OS - Quantum Hugging Framework
=====================================
Omega Encoders: Sub-Threshold Signal Encoding

From The_Quantum_Hugging_Framework.docx §2-3:

OMEGA-VALID ENCODING:
    E: S → (z₁, ..., z_N) such that:
    
    1. Sub-threshold: |z_k| < ε for all k
    2. Reconstruction: Σz_k = S
    3. Finiteness: N < ∞

ENCODER FAMILIES:
    - Uniform: equal-sized packets
    - Geometric: metallic ratio decay
    - Nested: hierarchical encoding
    - Randomized: stochastic variants

CAPACITY:
    C ≈ log₂(2ε/δ) bits per packet
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math
import random


# =============================================================================
# PACKET
# =============================================================================

@dataclass
class Packet:
    """
    A single packet z_k in an Omega encoding.
    """
    
    value: float
    index: int = 0
    
    # Metadata
    channel: int = 0
    sign: int = 1
    
    @property
    def magnitude(self) -> float:
        """Absolute value |z_k|."""
        return abs(self.value)
    
    def is_valid(self, epsilon: float) -> bool:
        """Check sub-threshold condition |z_k| < ε."""
        return self.magnitude < epsilon
    
    def __repr__(self) -> str:
        return f"z[{self.index}]={self.value:.6f}"


@dataclass
class PacketSequence:
    """
    Sequence of packets (z₁, ..., z_N).
    """
    
    packets: List[Packet] = field(default_factory=list)
    
    @property
    def N(self) -> int:
        """Number of packets."""
        return len(self.packets)
    
    @property
    def total(self) -> float:
        """Sum of packets Σz_k."""
        return sum(p.value for p in self.packets)
    
    @property
    def max_magnitude(self) -> float:
        """Maximum |z_k|."""
        if not self.packets:
            return 0.0
        return max(p.magnitude for p in self.packets)
    
    def is_omega_valid(self, epsilon: float) -> bool:
        """Check all packets are sub-threshold."""
        return all(p.is_valid(epsilon) for p in self.packets)
    
    def reconstruction_error(self, target: float) -> float:
        """Error |Σz_k - S|."""
        return abs(self.total - target)
    
    def add_packet(self, value: float, channel: int = 0) -> None:
        """Add packet to sequence."""
        idx = len(self.packets)
        self.packets.append(Packet(value=value, index=idx, channel=channel))
    
    def to_list(self) -> List[float]:
        """Get packet values as list."""
        return [p.value for p in self.packets]


# =============================================================================
# OMEGA ENCODER BASE
# =============================================================================

@dataclass
class OmegaEncoder:
    """
    Base class for Omega encoders.
    
    E: S → (z₁, ..., z_N) with:
    - |z_k| < ε
    - Σz_k = S
    """
    
    epsilon: float = 1.0          # Threshold
    tolerance: float = 1e-10      # Reconstruction tolerance
    max_packets: int = 10000      # Safety limit
    
    def encode(self, S: float) -> PacketSequence:
        """Encode signal S into packet sequence."""
        raise NotImplementedError
    
    def decode(self, packets: PacketSequence) -> float:
        """Decode packet sequence to signal."""
        return packets.total
    
    def verify(self, S: float, packets: PacketSequence) -> Dict[str, Any]:
        """Verify encoding validity."""
        return {
            "signal": S,
            "packets": packets.N,
            "reconstruction": packets.total,
            "error": packets.reconstruction_error(S),
            "max_magnitude": packets.max_magnitude,
            "epsilon": self.epsilon,
            "sub_threshold": packets.is_omega_valid(self.epsilon),
            "valid": (
                packets.is_omega_valid(self.epsilon) and
                packets.reconstruction_error(S) < self.tolerance
            )
        }
    
    def capacity_bits(self) -> float:
        """Theoretical capacity per packet in bits."""
        # C ≈ log₂(2ε/δ) where δ is precision
        return math.log2(2 * self.epsilon / self.tolerance)


# =============================================================================
# UNIFORM ENCODER
# =============================================================================

@dataclass
class UniformEncoder(OmegaEncoder):
    """
    Uniform Omega encoder.
    
    Divides S into N equal packets of size S/N.
    N = ⌈|S|/ε⌉ + 1 ensures |z_k| < ε.
    """
    
    def encode(self, S: float) -> PacketSequence:
        """Encode using uniform packets."""
        if S == 0:
            return PacketSequence([Packet(0.0, 0)])
        
        # Compute number of packets needed
        N = max(1, int(math.ceil(abs(S) / self.epsilon)) + 1)
        N = min(N, self.max_packets)
        
        # Create uniform packets
        packet_value = S / N
        packets = PacketSequence()
        
        for i in range(N):
            packets.add_packet(packet_value)
        
        return packets


# =============================================================================
# GEOMETRIC ENCODER
# =============================================================================

@dataclass
class GeometricEncoder(OmegaEncoder):
    """
    Geometric Omega encoder using metallic ratios.
    
    z_k = S · r^k · (1-r) for k = 0, 1, 2, ...
    until |z_k| < tolerance
    """
    
    ratio: float = 0.618          # Default: golden ratio inverse (φ-1)
    
    def encode(self, S: float) -> PacketSequence:
        """Encode using geometric decay."""
        packets = PacketSequence()
        
        if abs(S) < self.tolerance:
            packets.add_packet(S)
            return packets
        
        remaining = S
        r = self.ratio
        k = 0
        
        while abs(remaining) > self.tolerance and k < self.max_packets:
            # Packet value
            z_k = remaining * (1 - r)
            
            # Ensure sub-threshold
            if abs(z_k) >= self.epsilon:
                # Split into smaller packets
                n_split = int(math.ceil(abs(z_k) / (self.epsilon * 0.9)))
                for _ in range(n_split):
                    packets.add_packet(z_k / n_split)
            else:
                packets.add_packet(z_k)
            
            remaining *= r
            k += 1
        
        # Add remainder if non-zero
        if abs(remaining) > self.tolerance:
            packets.add_packet(remaining)
        
        return packets
    
    @classmethod
    def golden(cls, epsilon: float = 1.0) -> 'GeometricEncoder':
        """Create golden ratio encoder (φ⁻¹ ≈ 0.618)."""
        phi = (1 + math.sqrt(5)) / 2
        return cls(epsilon=epsilon, ratio=phi - 1)
    
    @classmethod
    def silver(cls, epsilon: float = 1.0) -> 'GeometricEncoder':
        """Create silver ratio encoder (√2 - 1 ≈ 0.414)."""
        return cls(epsilon=epsilon, ratio=math.sqrt(2) - 1)


# =============================================================================
# NESTED ENCODER
# =============================================================================

@dataclass
class NestedEncoder(OmegaEncoder):
    """
    Nested/hierarchical Omega encoder.
    
    Recursively encodes residuals at multiple levels.
    """
    
    base_encoder: OmegaEncoder = None
    depth: int = 3
    
    def __post_init__(self):
        if self.base_encoder is None:
            self.base_encoder = UniformEncoder(epsilon=self.epsilon)
    
    def encode(self, S: float) -> PacketSequence:
        """Encode using nested levels."""
        all_packets = PacketSequence()
        remaining = S
        
        for level in range(self.depth):
            # Encode at this level
            level_packets = self.base_encoder.encode(remaining)
            
            # Add to total
            for p in level_packets.packets:
                all_packets.add_packet(p.value, channel=level)
            
            # Compute residual
            remaining = remaining - level_packets.total
            
            if abs(remaining) < self.tolerance:
                break
        
        # Add final residual if needed
        if abs(remaining) > self.tolerance:
            all_packets.add_packet(remaining)
        
        return all_packets


# =============================================================================
# RANDOMIZED ENCODER
# =============================================================================

@dataclass
class RandomizedEncoder(OmegaEncoder):
    """
    Randomized Omega encoder.
    
    Adds controlled randomness for statistical masking.
    """
    
    noise_scale: float = 0.01    # Scale of random perturbations
    
    def encode(self, S: float) -> PacketSequence:
        """Encode with randomization."""
        packets = PacketSequence()
        
        if abs(S) < self.tolerance:
            packets.add_packet(S)
            return packets
        
        # Compute number of packets
        N = max(2, int(math.ceil(abs(S) / (self.epsilon * 0.8))))
        N = min(N, self.max_packets)
        
        # Generate random partition
        random_vals = [random.random() for _ in range(N)]
        total_rand = sum(random_vals)
        
        # Scale to sum to S
        for i, r in enumerate(random_vals):
            base_value = S * r / total_rand
            
            # Add small noise
            noise = random.gauss(0, self.noise_scale * self.epsilon)
            value = base_value + noise
            
            # Ensure sub-threshold
            if abs(value) >= self.epsilon:
                value = math.copysign(self.epsilon * 0.99, value)
            
            packets.add_packet(value)
        
        # Correct for reconstruction
        error = S - packets.total
        if packets.packets:
            # Distribute error
            correction = error / len(packets.packets)
            for p in packets.packets:
                p.value += correction
        
        return packets


# =============================================================================
# ENCODER FACTORY
# =============================================================================

class EncoderType(Enum):
    """Types of Omega encoders."""
    
    UNIFORM = "uniform"
    GEOMETRIC = "geometric"
    GOLDEN = "golden"
    SILVER = "silver"
    NESTED = "nested"
    RANDOMIZED = "randomized"


def create_encoder(encoder_type: EncoderType, 
                   epsilon: float = 1.0,
                   **kwargs) -> OmegaEncoder:
    """Create Omega encoder of specified type."""
    
    if encoder_type == EncoderType.UNIFORM:
        return UniformEncoder(epsilon=epsilon, **kwargs)
    
    elif encoder_type == EncoderType.GEOMETRIC:
        return GeometricEncoder(epsilon=epsilon, **kwargs)
    
    elif encoder_type == EncoderType.GOLDEN:
        return GeometricEncoder.golden(epsilon=epsilon)
    
    elif encoder_type == EncoderType.SILVER:
        return GeometricEncoder.silver(epsilon=epsilon)
    
    elif encoder_type == EncoderType.NESTED:
        return NestedEncoder(epsilon=epsilon, **kwargs)
    
    elif encoder_type == EncoderType.RANDOMIZED:
        return RandomizedEncoder(epsilon=epsilon, **kwargs)
    
    else:
        return UniformEncoder(epsilon=epsilon)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_omega() -> bool:
    """Validate omega encoder module."""
    
    # Test Packet
    p = Packet(value=0.5, index=0)
    assert p.magnitude == 0.5
    assert p.is_valid(1.0)
    assert not p.is_valid(0.4)
    
    # Test PacketSequence
    seq = PacketSequence()
    seq.add_packet(0.3)
    seq.add_packet(0.7)
    assert seq.N == 2
    assert abs(seq.total - 1.0) < 1e-10
    
    # Test UniformEncoder
    uniform = UniformEncoder(epsilon=1.0)
    packets = uniform.encode(5.0)
    assert packets.is_omega_valid(1.0)
    assert abs(packets.total - 5.0) < 1e-10
    
    verify = uniform.verify(5.0, packets)
    assert verify["valid"]
    
    # Test GeometricEncoder
    golden = GeometricEncoder.golden(epsilon=1.0)
    packets = golden.encode(3.0)
    assert packets.is_omega_valid(1.0)
    assert abs(packets.total - 3.0) < 1e-6
    
    # Test NestedEncoder
    nested = NestedEncoder(epsilon=1.0, depth=2)
    packets = nested.encode(2.5)
    assert abs(packets.total - 2.5) < 1e-6
    
    # Test RandomizedEncoder
    rand_enc = RandomizedEncoder(epsilon=1.0)
    packets = rand_enc.encode(4.0)
    assert abs(packets.total - 4.0) < 0.1  # Looser bound due to noise
    
    # Test negative signals
    packets = uniform.encode(-3.5)
    assert packets.is_omega_valid(1.0)
    assert abs(packets.total - (-3.5)) < 1e-10
    
    return True


if __name__ == "__main__":
    print("Validating Quantum Hugging Omega Module...")
    assert validate_omega()
    print("✓ Omega module validated")
    
    # Demo
    print("\n=== Omega Encoders Demo ===")
    
    S = 3.14159
    epsilon = 0.5
    
    print(f"\nSignal S = {S}")
    print(f"Threshold ε = {epsilon}")
    
    # Test each encoder type
    encoders = [
        ("Uniform", UniformEncoder(epsilon=epsilon)),
        ("Golden", GeometricEncoder.golden(epsilon=epsilon)),
        ("Silver", GeometricEncoder.silver(epsilon=epsilon)),
        ("Nested", NestedEncoder(epsilon=epsilon, depth=3)),
        ("Randomized", RandomizedEncoder(epsilon=epsilon)),
    ]
    
    for name, encoder in encoders:
        packets = encoder.encode(S)
        verify = encoder.verify(S, packets)
        
        print(f"\n{name} Encoder:")
        print(f"  Packets: {verify['packets']}")
        print(f"  Max magnitude: {verify['max_magnitude']:.6f}")
        print(f"  Reconstruction: {verify['reconstruction']:.6f}")
        print(f"  Error: {verify['error']:.2e}")
        print(f"  Valid: {verify['valid']}")
