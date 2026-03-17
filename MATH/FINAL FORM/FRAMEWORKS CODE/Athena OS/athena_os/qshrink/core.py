"""
ATHENA OS - Q-SHRINK COMPRESSION FRAMEWORK
==========================================
Volume I & II: A Unified Crystal Calculus for Compression

From Q-SHRINK Volumes I & II:

Q-SHRINK is a unified mathematical framework for compression where
the codec is not primarily an entropy coder, but a COORDINATE SYSTEM
CONSTRUCTOR: it transforms heterogeneous data into a representation
where structure becomes explicit, residual uncertainty becomes sharply
concentrated, and decoding remains DETERMINISTIC, STREAM-LEGAL,
REPAIRABLE, and optionally SEEK-LEGAL.

THE FOUR-OPERATOR PIPELINE:
    ℰ = C ∘ B ∘ Q ∘ P
    ?? = P⁻¹ ∘ Q⁻¹ ∘ B⁻¹ ∘ C⁻¹

    P (Partition/Coordinate): Structure coordinate system
    Q (Quantize): Rate-distortion control law
    B (Bucket/Split): Coherent bulk vs escapes
    C (Code+Containerize): Entropy coding + container

THE FOUR-LENS TAXONOMY:
    □ Square:  Determinism, addressing, schedules, seek lattices
    ✿ Flower:  Coupling, phase geometry, petals, anchors
    ☁ Cloud:   Probability, entropy, contracts, tables
    ⟡ Fractal: Recursion, self-reference, modularity

CORE INVARIANTS:
    1. Deterministic decode
    2. Explicit legality boundaries
    3. Controlled distortion (when permitted)
    4. Bounded corruption impact
    5. Streaming and random-access legality
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Set, Optional, Tuple, Callable,
    Any, Union, TypeVar, Generic, FrozenSet
)
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np
import hashlib
from datetime import datetime


# =============================================================================
# FUNDAMENTAL TYPES (Chapter 1.1)
# =============================================================================

class Alphabet(Enum):
    """Alphabet types for signal encoding."""
    
    BINARY = "binary"           # {0, 1}
    TERNARY = "ternary"         # {-1, 0, 1}
    INTEGER = "integer"         # Z
    REAL = "real"               # R (quantized)
    SYMBOL = "symbol"           # Finite alphabet


@dataclass(frozen=True)
class SignalType:
    """
    Signal type specification.
    
    A signal object is a finite, typed datum with canonical sampling geometry.
    """
    
    name: str
    alphabet: Alphabet
    dimensions: Tuple[int, ...]
    sample_type: str = "scalar"  # "scalar", "vector", "tensor"
    
    @property
    def total_samples(self) -> int:
        """Total number of samples."""
        result = 1
        for d in self.dimensions:
            result *= d
        return result


@dataclass
class SignalObject:
    """
    X ∈ ?? - A finite signal object.
    
    The primary data unit in Q-SHRINK.
    """
    
    signal_type: SignalType
    data: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate signal dimensions."""
        expected_shape = self.signal_type.dimensions
        if self.data.shape != expected_shape:
            # Allow flattening
            if self.data.size != self.signal_type.total_samples:
                raise ValueError(
                    f"Data size {self.data.size} doesn't match "
                    f"expected {self.signal_type.total_samples}"
                )
    
    @property
    def samples(self) -> np.ndarray:
        """Get flattened samples."""
        return self.data.flatten()
    
    def reshape(self) -> np.ndarray:
        """Reshape to canonical dimensions."""
        return self.data.reshape(self.signal_type.dimensions)


# =============================================================================
# DISTORTION METRICS (Chapter 1.2)
# =============================================================================

class DistortionMetric(ABC):
    """
    Base class for distortion metrics.
    
    d: ?? × ?? → ℝ≥0
    """
    
    @abstractmethod
    def __call__(self, x: np.ndarray, x_hat: np.ndarray) -> float:
        """Compute distortion between original and reconstruction."""
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Metric name."""
        pass


class MSEMetric(DistortionMetric):
    """Mean Squared Error distortion."""
    
    def __call__(self, x: np.ndarray, x_hat: np.ndarray) -> float:
        return float(np.mean((x - x_hat) ** 2))
    
    def name(self) -> str:
        return "MSE"


class MAEMetric(DistortionMetric):
    """Mean Absolute Error distortion."""
    
    def __call__(self, x: np.ndarray, x_hat: np.ndarray) -> float:
        return float(np.mean(np.abs(x - x_hat)))
    
    def name(self) -> str:
        return "MAE"


class LInfMetric(DistortionMetric):
    """L-infinity (max absolute) distortion."""
    
    def __call__(self, x: np.ndarray, x_hat: np.ndarray) -> float:
        return float(np.max(np.abs(x - x_hat)))
    
    def name(self) -> str:
        return "L_inf"


class WeightedDistortion(DistortionMetric):
    """
    Weighted distortion metric.
    
    d_W(x, x̂) = ||W(x - x̂)||
    """
    
    def __init__(self, weights: np.ndarray, base_metric: DistortionMetric):
        self.weights = weights
        self.base = base_metric
    
    def __call__(self, x: np.ndarray, x_hat: np.ndarray) -> float:
        weighted_diff = self.weights * (x - x_hat)
        return self.base(weighted_diff, np.zeros_like(weighted_diff))
    
    def name(self) -> str:
        return f"Weighted_{self.base.name()}"


# =============================================================================
# RATE-DISTORTION OBJECTIVES (Chapter 1.2)
# =============================================================================

@dataclass
class RateDistortionObjective:
    """
    Rate-distortion objective function.
    
    Minimize R(X) subject to Δ(X) ≤ τ
    """
    
    distortion_metric: DistortionMetric
    distortion_bound: float  # τ
    
    # Resource constraints
    decode_time_bound: Optional[float] = None
    decode_memory_bound: Optional[float] = None
    encode_time_bound: Optional[float] = None
    encode_memory_bound: Optional[float] = None
    
    def is_feasible(self, rate: float, distortion: float,
                   decode_time: float = 0, decode_memory: float = 0) -> bool:
        """Check if solution is feasible."""
        if distortion > self.distortion_bound:
            return False
        if self.decode_time_bound and decode_time > self.decode_time_bound:
            return False
        if self.decode_memory_bound and decode_memory > self.decode_memory_bound:
            return False
        return True


# =============================================================================
# ACCESS MODES (Chapter 1.2.1)
# =============================================================================

class AccessMode(Enum):
    """Stream access modes."""
    
    STREAM_ONLY = "stream_only"         # Forward decode only
    SEEKABLE_LINEAR = "seekable_linear" # Seek via linear scan
    SEEKABLE_INDEXED = "seekable_indexed"  # Fast indexed seek


@dataclass
class StreamingConstraint:
    """
    Streaming decodability constraint.
    
    A bitstream is streaming-decodable if there exists a monotone
    parsing function with bounded lookahead Λ.
    """
    
    lookahead_bound: int  # Λ
    unit_granularity: str = "block"  # "block", "tile", "frame"
    
    def is_streaming_legal(self, lookahead: int) -> bool:
        """Check if lookahead is within bound."""
        return lookahead <= self.lookahead_bound


@dataclass
class RandomAccessConstraint:
    """
    Random access decodability constraint.
    
    Support random access at granularity g with bounded dependency closure.
    """
    
    granularity: str  # "block", "tile", "frame", "sample"
    max_dependency_depth: int = 1
    requires_seek_lattice: bool = True
    
    def dependency_closure_size(self, unit_id: int) -> int:
        """Estimate dependency closure size for unit."""
        return self.max_dependency_depth


# =============================================================================
# CORRUPTION MODEL (Chapter 1.2.2)
# =============================================================================

class CorruptionType(Enum):
    """Types of corruption."""
    
    BIT_FLIP = "bit_flip"
    BURST_ERROR = "burst"
    TRUNCATION = "truncation"
    SPLICE = "splice"


@dataclass
class CorruptionModel:
    """
    Corruption model for robustness analysis.
    
    A corruption model is a distribution over operators ??
    acting on bitstrings: b̃ = ??(b).
    """
    
    corruption_type: CorruptionType
    error_rate: float  # Probability of error per unit
    burst_length: int = 1  # For burst errors
    
    def apply(self, bitstream: bytes) -> bytes:
        """Apply corruption to bitstream (for testing)."""
        data = bytearray(bitstream)
        
        if self.corruption_type == CorruptionType.BIT_FLIP:
            for i in range(len(data)):
                if np.random.random() < self.error_rate:
                    bit_pos = np.random.randint(8)
                    data[i] ^= (1 << bit_pos)
        
        elif self.corruption_type == CorruptionType.TRUNCATION:
            if np.random.random() < self.error_rate:
                cut_point = np.random.randint(len(data))
                data = data[:cut_point]
        
        return bytes(data)


# =============================================================================
# LEGALITY SET (Chapter 1.3)
# =============================================================================

@dataclass
class LegalityCheck:
    """A single legality check predicate."""
    
    name: str
    predicate: Callable[[bytes], bool]
    is_local: bool = True  # Can be checked locally
    
    def check(self, data: bytes) -> bool:
        """Run the legality check."""
        return self.predicate(data)


class LegalitySet:
    """
    Ω - The legality set.
    
    A bitstream is legal only if it passes all decidable local checks:
    - Prefix repair
    - Length delimitation  
    - Checksums/hashes
    - Contract-grammar validation
    """
    
    def __init__(self):
        self._checks: List[LegalityCheck] = []
    
    def add_check(self, check: LegalityCheck) -> None:
        """Add a legality check."""
        self._checks.append(check)
    
    def is_legal(self, bitstream: bytes) -> Tuple[bool, List[str]]:
        """
        Check if bitstream is legal.
        
        Returns (is_legal, list_of_failures).
        """
        failures = []
        for check in self._checks:
            if not check.check(bitstream):
                failures.append(check.name)
        
        return len(failures) == 0, failures
    
    def add_length_check(self, expected_length: int) -> None:
        """Add length delimitation check."""
        self.add_check(LegalityCheck(
            name="length_check",
            predicate=lambda d: len(d) == expected_length
        ))
    
    def add_checksum_check(self, expected_checksum: str) -> None:
        """Add checksum validation."""
        self.add_check(LegalityCheck(
            name="checksum",
            predicate=lambda d: hashlib.sha256(d).hexdigest()[:16] == expected_checksum
        ))


# =============================================================================
# AXIOM SYSTEM (Chapter 1.1)
# =============================================================================

@dataclass
class CompressionAxiom:
    """
    A compression axiom that any valid codec must satisfy.
    """
    
    id: str
    name: str
    description: str
    
    # Predicate to check axiom satisfaction
    check: Optional[Callable[[Any], bool]] = None


# Core axioms from Q-SHRINK
AXIOM_DETERMINISM = CompressionAxiom(
    id="A1",
    name="Determinism",
    description="Given a legal bitstream and declared contracts, decoding is unique"
)

AXIOM_CORRECTNESS = CompressionAxiom(
    id="A2", 
    name="Correctness",
    description="Lossless mode is a left-inverse pipeline; lossy mode yields controlled reconstruction"
)

AXIOM_NO_DESYNC = CompressionAxiom(
    id="A3",
    name="No-Desync",
    description="Lockstep multi-lane coding and self-delimited chunk law prevent silent schedule drift"
)

AXIOM_BOUNDED_DAMAGE = CompressionAxiom(
    id="A4",
    name="Bounded-Damage",
    description="Corruption is locally contained; invalid chunks can be skipped without poisoning later boundaries"
)

AXIOM_SEEK_LEGALITY = CompressionAxiom(
    id="A5",
    name="Seek-Legality",
    description="Domains claiming random access must ship seek lattices or restrict access claims"
)

AXIOM_EXTENSIBILITY = CompressionAxiom(
    id="A6",
    name="Extensibility",
    description="New ideas become new opcodes + proof obligations, not new file formats"
)

COMPRESSION_AXIOMS = [
    AXIOM_DETERMINISM,
    AXIOM_CORRECTNESS,
    AXIOM_NO_DESYNC,
    AXIOM_BOUNDED_DAMAGE,
    AXIOM_SEEK_LEGALITY,
    AXIOM_EXTENSIBILITY
]


# =============================================================================
# VALIDATION
# =============================================================================

def validate_core() -> bool:
    """Validate Q-SHRINK core module."""
    np.random.seed(42)
    
    # Test signal types
    img_type = SignalType(
        name="image",
        alphabet=Alphabet.INTEGER,
        dimensions=(256, 256, 3)
    )
    assert img_type.total_samples == 256 * 256 * 3
    
    # Test signal object
    data = np.random.randint(0, 256, (256, 256, 3))
    signal = SignalObject(img_type, data)
    assert signal.samples.shape == (256 * 256 * 3,)
    
    # Test distortion metrics
    x = np.array([1.0, 2.0, 3.0])
    x_hat = np.array([1.1, 2.2, 3.3])
    
    mse = MSEMetric()
    mae = MAEMetric()
    linf = LInfMetric()
    
    assert mse(x, x_hat) > 0
    assert mae(x, x_hat) > 0
    assert np.isclose(linf(x, x_hat), 0.3, atol=1e-12)
    
    # Test rate-distortion objective
    rd = RateDistortionObjective(
        distortion_metric=mse,
        distortion_bound=0.1
    )
    assert rd.is_feasible(100, 0.05)
    assert not rd.is_feasible(100, 0.2)
    
    # Test streaming constraint
    stream = StreamingConstraint(lookahead_bound=1024)
    assert stream.is_streaming_legal(512)
    assert not stream.is_streaming_legal(2048)
    
    # Test legality set
    legality = LegalitySet()
    legality.add_length_check(10)
    
    is_legal, failures = legality.is_legal(b"0123456789")
    assert is_legal
    
    is_legal, failures = legality.is_legal(b"short")
    assert not is_legal
    assert "length_check" in failures
    
    # Test corruption model
    corruption = CorruptionModel(
        corruption_type=CorruptionType.BIT_FLIP,
        error_rate=0.01
    )
    # Just ensure it runs
    corrupted = corruption.apply(b"test data")
    assert isinstance(corrupted, bytes)
    
    return True


if __name__ == "__main__":
    print("Validating Q-SHRINK Core...")
    assert validate_core()
    print("✓ Q-SHRINK Core validated")
