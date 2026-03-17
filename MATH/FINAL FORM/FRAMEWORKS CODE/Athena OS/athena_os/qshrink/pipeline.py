"""
ATHENA OS - Q-SHRINK PIPELINE OPERATORS
=======================================
The Four-Operator Codec Pipeline (Chapters 2-4)

ℰ = C ∘ B ∘ Q ∘ P
?? = P⁻¹ ∘ Q⁻¹ ∘ B⁻¹ ∘ C⁻¹

P (Partition/Coordinate): 
    Construct structure coordinate system, route samples into groups

Q (Quantize):
    Rate-distortion control (identity for lossless)

B (Bucket/Split):
    Separate coherent bulk from escapes

C (Code+Containerize):
    Entropy coding + robust container packaging
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np
import hashlib

from .core import SignalObject, DistortionMetric, MSEMetric
from .lenses import (
    LensType, FlowerLens, PetalPartition, 
    CloudLens, ProbabilityTable, EntropyContract
)


# =============================================================================
# OPERATOR BASE CLASS
# =============================================================================

class PipelineOperator(ABC):
    """Base class for pipeline operators."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Operator name."""
        pass
    
    @property
    @abstractmethod
    def is_bijective(self) -> bool:
        """Is this operator bijective (lossless)?"""
        pass
    
    @abstractmethod
    def forward(self, data: Any) -> Any:
        """Forward transform."""
        pass
    
    @abstractmethod
    def inverse(self, data: Any) -> Any:
        """Inverse transform."""
        pass
    
    def verify_inverse(self, data: Any, tol: float = 1e-10) -> bool:
        """Verify that inverse recovers original."""
        if not self.is_bijective:
            return True  # Can't verify non-bijective
        
        transformed = self.forward(data)
        recovered = self.inverse(transformed)
        
        if isinstance(data, np.ndarray):
            return np.allclose(data, recovered, atol=tol)
        return data == recovered


# =============================================================================
# P: PARTITION / COORDINATE OPERATOR
# =============================================================================

@dataclass
class PartitionResult:
    """Result of partition operation."""
    
    petal_assignments: np.ndarray  # Which petal each sample belongs to
    anchors: np.ndarray            # Anchor for each petal
    residuals: np.ndarray          # Residual from anchor
    n_petals: int
    projection_scales: Optional[np.ndarray] = None
    
    # Metadata
    partition_overhead: int = 0    # Bits to encode partition


class PartitionOperator(PipelineOperator):
    """
    P: Partition/Coordinate Operator.
    
    Constructs an explicit structure coordinate system and routes
    samples into structured groups (petals).
    
    Properties:
    - Geometry-first: select representation that exposes structure
    - Baseline-feasible: works without external resources
    - Reproducible: deterministic given profile
    """
    
    def __init__(self, n_petals: int = 16, dim: int = 4):
        self.n_petals = n_petals
        self.dim = dim
        self._partition = PetalPartition(n_petals=n_petals, dim=dim)
    
    @property
    def name(self) -> str:
        return "Partition"
    
    @property
    def is_bijective(self) -> bool:
        return True  # Partition is bijective
    
    def forward(self, data: np.ndarray) -> PartitionResult:
        """
        Forward partition: assign samples to petals.
        
        x → (π, a, r) where:
        - π: petal assignments
        - a: anchors
        - r: residuals
        """
        n_samples = len(data)
        sample_dim = data.shape[1] if len(data.shape) > 1 else 1
        
        # Flatten if needed
        if len(data.shape) > 1:
            flat_data = data.reshape(n_samples, -1)
        else:
            flat_data = data.reshape(-1, 1)
        
        # Assign samples to petals
        assignments = np.zeros(n_samples, dtype=int)
        for i in range(n_samples):
            sample = np.zeros(self.dim)
            sample[:min(len(flat_data[i]), self.dim)] = flat_data[i][:self.dim]
            assignments[i] = self._partition.assign_petal(sample)
        
        # Get anchors for all petals
        anchors = np.array([
            self._partition.get_anchor(p) for p in range(self.n_petals)
        ])
        
        # Compute residuals
        residuals = np.zeros_like(flat_data)
        projection_scales = np.zeros(n_samples, dtype=np.float64)
        for i in range(n_samples):
            anchor = anchors[assignments[i]]
            sample = flat_data[i]
            sample_len = len(sample)
            copy_len = min(len(anchor), sample_len)
            anchor_padded = np.zeros(sample_len, dtype=flat_data.dtype)
            anchor_padded[:copy_len] = anchor[:copy_len]
            projection_scale = float(np.dot(sample[:copy_len], anchor[:copy_len])) if copy_len > 0 else 0.0
            projection_scales[i] = projection_scale
            residuals[i] = sample - (projection_scale * anchor_padded)
        
        return PartitionResult(
            petal_assignments=assignments,
            anchors=anchors,
            residuals=residuals,
            n_petals=self.n_petals,
            projection_scales=projection_scales,
        )
    
    def inverse(self, result: PartitionResult) -> np.ndarray:
        """
        Inverse partition: reconstruct from petals.
        
        (π, a, r) → x
        """
        n_samples = len(result.residuals)
        data = np.zeros_like(result.residuals)
        
        for i in range(n_samples):
            petal = result.petal_assignments[i]
            anchor = result.anchors[petal]
            residual = result.residuals[i]
            
            # Reconstruct: anchor projection + residual
            sample_len = len(residual)
            anchor_padded = np.zeros(sample_len)
            copy_len = min(len(anchor), sample_len)
            anchor_padded[:copy_len] = anchor[:copy_len]
            
            projection_scale = 1.0
            if result.projection_scales is not None:
                projection_scale = float(result.projection_scales[i])
            data[i] = (projection_scale * anchor_padded) + residual
        
        return data


# =============================================================================
# Q: QUANTIZE OPERATOR
# =============================================================================

@dataclass
class QuantizeResult:
    """Result of quantization operation."""
    
    quantized: np.ndarray      # Quantized values (indices)
    scale: float               # Quantization scale
    reconstruction: np.ndarray # Reconstructed values
    
    # Error bounds
    max_error: float = 0.0


class QuantizeOperator(PipelineOperator):
    """
    Q: Quantize Operator.
    
    The only sanctioned non-bijection for controlled-lossy profiles.
    Lossless mode uses identity quantizer.
    
    Step size determined by metallic-mean ladder:
    Δ_{ℓ,t,q} = σ_ℓ · T(ℓ) · δ^{-t} · φ^{-q}
    """
    
    def __init__(self, step_size: float = 1.0, 
                 lossless: bool = False,
                 tier: int = 0,
                 refinement: int = 0):
        self.base_step = step_size
        self.lossless = lossless
        self.tier = tier
        self.refinement = refinement
        
        # Metallic mean parameters
        self.delta = 2.0   # Coarse spacing
        self.phi = 1.618   # Golden ratio for refinement
        
        # Compute actual step size
        if lossless:
            self.step_size = 0  # No quantization
        else:
            self.step_size = self.base_step * (self.delta ** (-tier)) * (self.phi ** (-refinement))
    
    @property
    def name(self) -> str:
        return "Quantize"
    
    @property
    def is_bijective(self) -> bool:
        return self.lossless
    
    def forward(self, data: np.ndarray) -> QuantizeResult:
        """
        Forward quantization: x → ⌊x/Δ⌉
        """
        if self.lossless:
            return QuantizeResult(
                quantized=data.copy(),
                scale=1.0,
                reconstruction=data.copy(),
                max_error=0.0
            )
        
        # Uniform scalar quantization
        quantized = np.round(data / self.step_size).astype(int)
        reconstruction = quantized * self.step_size
        
        # Compute error bound
        max_error = self.step_size / 2
        
        return QuantizeResult(
            quantized=quantized,
            scale=self.step_size,
            reconstruction=reconstruction,
            max_error=max_error
        )
    
    def inverse(self, result: QuantizeResult) -> np.ndarray:
        """
        Inverse quantization: indices → reconstructed values
        """
        if self.lossless:
            return result.quantized.copy()
        
        return result.quantized * result.scale
    
    def error_bound(self) -> float:
        """Get maximum quantization error."""
        if self.lossless:
            return 0.0
        return self.step_size / 2


# =============================================================================
# B: BUCKET / SPLIT OPERATOR
# =============================================================================

@dataclass
class BucketResult:
    """Result of bucket/split operation."""
    
    bulk: np.ndarray       # Coherent bulk population
    escapes: np.ndarray    # Heavy-tail escape population
    tags: np.ndarray       # Split tags (0=bulk, 1=escape)
    
    # Statistics
    bulk_fraction: float = 0.0
    escape_fraction: float = 0.0


class BucketOperator(PipelineOperator):
    """
    B: Bucket/Split Operator (Phase-Partition Bucketing).
    
    Applies a deterministic phase-partition predicate χ(c) ∈ {0,1}
    to split coefficients into:
    - Coherent channel (χ=0): sharply peaked, highly compressible
    - Escape channel (χ=1): heavy-tailed, sparse
    """
    
    def __init__(self, threshold: float = 2.0):
        self.threshold = threshold  # σ-based threshold
    
    @property
    def name(self) -> str:
        return "Bucket"
    
    @property
    def is_bijective(self) -> bool:
        return True  # Splitting is bijective
    
    def forward(self, data: np.ndarray) -> BucketResult:
        """
        Forward bucket: split into bulk and escapes.
        
        χ(c) = 1 if |c| > threshold * σ, else 0
        """
        flat = data.flatten()
        
        # Estimate scale (robust MAD-based)
        median = np.median(np.abs(flat))
        sigma = median / 0.6745 if median > 0 else 1.0
        
        # Apply phase-partition predicate
        threshold_value = self.threshold * sigma
        tags = (np.abs(flat) > threshold_value).astype(int)
        
        # Split into channels
        bulk_mask = tags == 0
        escape_mask = tags == 1
        
        bulk = flat[bulk_mask]
        escapes = flat[escape_mask]
        
        bulk_frac = len(bulk) / len(flat) if len(flat) > 0 else 0
        escape_frac = len(escapes) / len(flat) if len(flat) > 0 else 0
        
        return BucketResult(
            bulk=bulk,
            escapes=escapes,
            tags=tags,
            bulk_fraction=bulk_frac,
            escape_fraction=escape_frac
        )
    
    def inverse(self, result: BucketResult) -> np.ndarray:
        """
        Inverse bucket: merge bulk and escapes.
        """
        n_total = len(result.tags)
        merged = np.zeros(n_total)
        
        bulk_idx = 0
        escape_idx = 0
        
        for i in range(n_total):
            if result.tags[i] == 0:
                if bulk_idx < len(result.bulk):
                    merged[i] = result.bulk[bulk_idx]
                    bulk_idx += 1
            else:
                if escape_idx < len(result.escapes):
                    merged[i] = result.escapes[escape_idx]
                    escape_idx += 1
        
        return merged


# =============================================================================
# C: CODE + CONTAINERIZE OPERATOR
# =============================================================================

@dataclass
class ChunkHeader:
    """Header for a container chunk."""
    
    chunk_type: str
    payload_length: int
    checksum: str
    
    def to_bytes(self) -> bytes:
        """Serialize header."""
        return f"{self.chunk_type}:{self.payload_length}:{self.checksum}".encode()
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'ChunkHeader':
        """Deserialize header."""
        parts = data.decode().split(":")
        return cls(
            chunk_type=parts[0],
            payload_length=int(parts[1]),
            checksum=parts[2]
        )


@dataclass
class Chunk:
    """A container chunk with header and payload."""
    
    header: ChunkHeader
    payload: bytes
    
    def verify_checksum(self) -> bool:
        """Verify payload checksum."""
        computed = hashlib.sha256(self.payload).hexdigest()[:16]
        return computed == self.header.checksum


@dataclass
class ContainerResult:
    """Result of containerization."""
    
    chunks: List[Chunk]
    manifest: Dict[str, Any]
    total_size: int
    
    # Legality
    is_streaming_legal: bool = True
    is_seek_legal: bool = False


class ContainerOperator(PipelineOperator):
    """
    C: Code + Containerize Operator.
    
    Encodes multiple synchronized streams and packages them in a
    robust, seek-aware, repairable container.
    
    Container properties:
    - Self-delimiting chunks
    - Checksums for integrity
    - Seek lattice for random access
    - Repair prefixes for error correction
    """
    
    def __init__(self, chunk_size: int = 4096,
                 enable_checksums: bool = True,
                 enable_seek: bool = False):
        self.chunk_size = chunk_size
        self.enable_checksums = enable_checksums
        self.enable_seek = enable_seek
        
        # Entropy coder (simplified)
        self._entropy_contract = EntropyContract(n_lanes=4)
    
    @property
    def name(self) -> str:
        return "Container"
    
    @property
    def is_bijective(self) -> bool:
        return True  # Container is bijective
    
    def forward(self, bucket_result: BucketResult) -> ContainerResult:
        """
        Forward containerize: encode and package.
        """
        chunks = []
        
        # Encode bulk stream
        bulk_bytes = self._encode_stream(bucket_result.bulk, lane=0)
        chunks.extend(self._package_chunks(bulk_bytes, "BULK"))
        
        # Encode escape stream
        escape_bytes = self._encode_stream(bucket_result.escapes, lane=1)
        chunks.extend(self._package_chunks(escape_bytes, "ESCP"))
        
        # Encode tags
        tag_bytes = self._encode_tags(bucket_result.tags)
        chunks.extend(self._package_chunks(tag_bytes, "TAGS"))
        
        # Build manifest
        manifest = {
            "n_chunks": len(chunks),
            "bulk_size": len(bucket_result.bulk),
            "escape_size": len(bucket_result.escapes),
            "total_samples": len(bucket_result.tags),
            "bulk_fraction": bucket_result.bulk_fraction
        }
        
        total_size = sum(len(c.header.to_bytes()) + len(c.payload) for c in chunks)
        
        return ContainerResult(
            chunks=chunks,
            manifest=manifest,
            total_size=total_size,
            is_streaming_legal=True,
            is_seek_legal=self.enable_seek
        )
    
    def inverse(self, result: ContainerResult) -> BucketResult:
        """
        Inverse containerize: decode and unpack.
        """
        bulk_bytes = b""
        escape_bytes = b""
        tag_bytes = b""
        
        for chunk in result.chunks:
            # Verify checksum
            if self.enable_checksums and not chunk.verify_checksum():
                raise ValueError(f"Chunk checksum failed: {chunk.header.chunk_type}")
            
            if chunk.header.chunk_type == "BULK":
                bulk_bytes += chunk.payload
            elif chunk.header.chunk_type == "ESCP":
                escape_bytes += chunk.payload
            elif chunk.header.chunk_type == "TAGS":
                tag_bytes += chunk.payload
        
        # Decode streams
        bulk = self._decode_stream(bulk_bytes, lane=0)
        escapes = self._decode_stream(escape_bytes, lane=1)
        tags = self._decode_tags(tag_bytes)
        
        return BucketResult(
            bulk=bulk,
            escapes=escapes,
            tags=tags
        )
    
    def _encode_stream(self, data: np.ndarray, lane: int) -> bytes:
        """Encode a stream with a stable numeric carrier."""
        return np.asarray(data, dtype=np.float64).tobytes()
    
    def _decode_stream(self, data: bytes, lane: int) -> np.ndarray:
        """Decode a stream."""
        if len(data) == 0:
            return np.array([])
        return np.frombuffer(data, dtype=np.float64)
    
    def _encode_tags(self, tags: np.ndarray) -> bytes:
        """Encode tags (simplified RLE)."""
        return tags.astype(np.uint8).tobytes()
    
    def _decode_tags(self, data: bytes) -> np.ndarray:
        """Decode tags."""
        if len(data) == 0:
            return np.array([])
        return np.frombuffer(data, dtype=np.uint8)
    
    def _package_chunks(self, data: bytes, chunk_type: str) -> List[Chunk]:
        """Package data into chunks."""
        chunks = []
        
        for i in range(0, len(data), self.chunk_size):
            payload = data[i:i + self.chunk_size]
            checksum = hashlib.sha256(payload).hexdigest()[:16]
            
            header = ChunkHeader(
                chunk_type=chunk_type,
                payload_length=len(payload),
                checksum=checksum
            )
            
            chunks.append(Chunk(header=header, payload=payload))
        
        return chunks


# =============================================================================
# COMPLETE CODEC PIPELINE
# =============================================================================

@dataclass
class CodecProfile:
    """Codec profile configuration."""
    
    name: str
    lossless: bool = True
    
    # Partition parameters
    n_petals: int = 16
    
    # Quantization parameters
    quality_tier: int = 0
    quality_refinement: int = 0
    
    # Bucket parameters
    escape_threshold: float = 2.0
    
    # Container parameters
    chunk_size: int = 4096
    enable_checksums: bool = True
    enable_seek: bool = False


class QShrinkCodec:
    """
    Complete Q-SHRINK Codec.
    
    ℰ = C ∘ B ∘ Q ∘ P
    ?? = P⁻¹ ∘ Q⁻¹ ∘ B⁻¹ ∘ C⁻¹
    """
    
    def __init__(self, profile: CodecProfile):
        self.profile = profile
        
        # Build pipeline operators
        self.P = PartitionOperator(n_petals=profile.n_petals)
        self.Q = QuantizeOperator(
            lossless=profile.lossless,
            tier=profile.quality_tier,
            refinement=profile.quality_refinement
        )
        self.B = BucketOperator(threshold=profile.escape_threshold)
        self.C = ContainerOperator(
            chunk_size=profile.chunk_size,
            enable_checksums=profile.enable_checksums,
            enable_seek=profile.enable_seek
        )
    
    def encode(self, data: np.ndarray) -> ContainerResult:
        """
        Encode data: ℰ = C ∘ B ∘ Q ∘ P
        """
        # P: Partition
        partition_result = self.P.forward(data)
        
        # Q: Quantize (on residuals)
        quantize_result = self.Q.forward(partition_result.residuals)
        
        # B: Bucket
        bucket_result = self.B.forward(quantize_result.quantized)
        
        # C: Containerize
        container_result = self.C.forward(bucket_result)
        
        # Store partition metadata in manifest
        container_result.manifest["petal_assignments"] = partition_result.petal_assignments.tolist()
        container_result.manifest["anchors"] = partition_result.anchors.tolist()
        container_result.manifest["n_petals"] = partition_result.n_petals
        container_result.manifest["projection_scales"] = partition_result.projection_scales.tolist()
        container_result.manifest["input_shape"] = list(data.shape)
        container_result.manifest["residual_shape"] = list(partition_result.residuals.shape)
        container_result.manifest["quantize_scale"] = quantize_result.scale
        container_result.manifest["quantized_dtype"] = str(np.asarray(quantize_result.quantized).dtype)
        
        return container_result
    
    def decode(self, container: ContainerResult) -> np.ndarray:
        """
        Decode data: ?? = P⁻¹ ∘ Q⁻¹ ∘ B⁻¹ ∘ C⁻¹
        """
        # C⁻¹: Uncontainerize
        bucket_result = self.C.inverse(container)
        
        # B⁻¹: Unbucket
        merged = self.B.inverse(bucket_result)
        
        # Q⁻¹: Dequantize
        quantized_dtype = np.dtype(container.manifest.get("quantized_dtype", "float64"))
        quantize_result = QuantizeResult(
            quantized=merged.astype(quantized_dtype, copy=False),
            scale=container.manifest.get("quantize_scale", 1.0),
            reconstruction=merged
        )
        residuals = self.Q.inverse(quantize_result)
        
        # P⁻¹: Unpartition
        residual_shape = tuple(container.manifest.get("residual_shape", [len(merged), 1]))
        projection_scales = np.array(
            container.manifest.get(
                "projection_scales",
                np.ones(len(container.manifest["petal_assignments"])),
            )
        )
        partition_result = PartitionResult(
            petal_assignments=np.array(container.manifest["petal_assignments"]),
            anchors=np.array(container.manifest["anchors"]),
            residuals=residuals.reshape(residual_shape),
            n_petals=container.manifest["n_petals"],
            projection_scales=projection_scales,
        )
        data = self.P.inverse(partition_result)
        
        input_shape = tuple(container.manifest.get("input_shape", list(data.shape)))
        return data.reshape(input_shape)
    
    def verify_roundtrip(self, data: np.ndarray, tol: float = 1e-6) -> bool:
        """Verify encode-decode roundtrip."""
        encoded = self.encode(data)
        decoded = self.decode(encoded)
        
        if self.profile.lossless:
            return np.allclose(data.flatten(), decoded.flatten(), atol=tol)
        else:
            # For lossy, check within quantization bounds
            max_error = self.Q.error_bound()
            return np.all(np.abs(data.flatten() - decoded.flatten()) <= max_error + tol)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_pipeline() -> bool:
    """Validate Q-SHRINK pipeline operators."""
    np.random.seed(42)
    
    # Test data
    data = np.random.randn(64, 4)
    
    # Test partition operator
    P = PartitionOperator(n_petals=8, dim=4)
    partition_result = P.forward(data)
    assert len(partition_result.petal_assignments) == 64
    assert partition_result.n_petals == 8
    
    # Test partition inverse
    recovered = P.inverse(partition_result)
    assert recovered.shape == data.shape
    
    # Test quantize operator (lossless)
    Q_lossless = QuantizeOperator(lossless=True)
    assert Q_lossless.is_bijective
    q_result = Q_lossless.forward(data)
    assert np.allclose(data, Q_lossless.inverse(q_result))
    
    # Test quantize operator (lossy)
    Q_lossy = QuantizeOperator(step_size=0.1, lossless=False)
    assert not Q_lossy.is_bijective
    q_result = Q_lossy.forward(data)
    assert q_result.max_error <= 0.05
    
    # Test bucket operator
    B = BucketOperator(threshold=2.0)
    bucket_result = B.forward(data.flatten())
    assert len(bucket_result.bulk) + len(bucket_result.escapes) == len(data.flatten())
    
    # Test bucket inverse
    merged = B.inverse(bucket_result)
    assert np.allclose(data.flatten(), merged)
    
    # Test container operator
    C = ContainerOperator(chunk_size=256)
    container_result = C.forward(bucket_result)
    assert len(container_result.chunks) > 0
    
    # Test container inverse
    recovered_bucket = C.inverse(container_result)
    assert np.allclose(bucket_result.bulk, recovered_bucket.bulk)
    assert np.allclose(bucket_result.escapes, recovered_bucket.escapes)
    
    # Test complete codec (lossless)
    profile_lossless = CodecProfile(
        name="lossless_test",
        lossless=True,
        n_petals=4
    )
    codec = QShrinkCodec(profile_lossless)
    
    test_data = np.random.randn(32).reshape(-1, 1)
    assert codec.verify_roundtrip(test_data)

    # Test complete codec (lossy)
    profile_lossy = CodecProfile(
        name="lossy_test",
        lossless=False,
        n_petals=4,
        quality_tier=1,
        quality_refinement=1
    )
    codec_lossy = QShrinkCodec(profile_lossy)
    lossy_data = np.linspace(-3.0, 3.0, 32, dtype=np.float64).reshape(-1, 1)
    assert codec_lossy.verify_roundtrip(lossy_data)
    
    return True


if __name__ == "__main__":
    print("Validating Q-SHRINK Pipeline...")
    assert validate_pipeline()
    print("✓ Q-SHRINK Pipeline validated")
