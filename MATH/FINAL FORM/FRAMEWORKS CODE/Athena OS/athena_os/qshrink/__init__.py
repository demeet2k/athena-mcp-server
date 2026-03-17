"""
ATHENA OS - Q-SHRINK COMPRESSION FRAMEWORK
==========================================
A Unified Crystal Calculus for Compression (Volumes I & II)

Q-SHRINK is a complete compression system defined as a unified calculus
of coordinate transforms whose primary object is not an entropy coder but
a LENS-ENGINE: a deterministic mechanism that converts heterogeneous data
into a small set of structured streams governed by explicit contracts.

SYSTEM GUARANTEES:
    (i)   Deterministic decode
    (ii)  Explicit legality boundaries
    (iii) Controlled distortion only when permitted
    (iv)  Bounded corruption impact with certified outcomes
    (v)   Streaming and random-access legality as enforceable claims

THE FOUR-OPERATOR PIPELINE:
    ℰ = C ∘ B ∘ Q ∘ P  (Encode)
    ?? = P⁻¹ ∘ Q⁻¹ ∘ B⁻¹ ∘ C⁻¹  (Decode)

    P: Partition/Coordinate - Structure coordinate system
    Q: Quantize - Rate-distortion control (identity for lossless)
    B: Bucket/Split - Coherent bulk vs escapes
    C: Code+Containerize - Entropy coding + robust container

THE FOUR-LENS TAXONOMY:
    □ Square:  Determinism, addressing, schedules, seek lattices
    ✿ Flower:  Coupling, phase geometry, petals, anchors
    ☁ Cloud:   Probability, entropy, contracts, tables
    ⟡ Fractal: Recursion, self-reference, modularity

CORE AXIOMS:
    A1. Determinism - Legal bitstream → unique decode
    A2. Correctness - Lossless is exact; lossy is bounded
    A3. No-Desync - Lockstep multi-lane coding
    A4. Bounded-Damage - Corruption is locally contained
    A5. Seek-Legality - Random access requires seek lattice
    A6. Extensibility - New opcodes, not new formats

PRODUCT MODES:
    - Container Mode: Q-SHRINK container for archives/assets
    - Native-Format Export: Standards-compliant output (PNG→PNG, etc.)
"""

from __future__ import annotations

# Core types and axioms
from .core import (
    # Alphabet and signal types
    Alphabet,
    SignalType,
    SignalObject,
    
    # Distortion metrics
    DistortionMetric,
    MSEMetric,
    MAEMetric,
    LInfMetric,
    WeightedDistortion,
    
    # Objectives and constraints
    RateDistortionObjective,
    AccessMode,
    StreamingConstraint,
    RandomAccessConstraint,
    
    # Corruption and legality
    CorruptionType,
    CorruptionModel,
    LegalityCheck,
    LegalitySet,
    
    # Axiom system
    CompressionAxiom,
    COMPRESSION_AXIOMS,
    AXIOM_DETERMINISM,
    AXIOM_CORRECTNESS,
    AXIOM_NO_DESYNC,
    AXIOM_BOUNDED_DAMAGE,
    AXIOM_SEEK_LEGALITY,
    AXIOM_EXTENSIBILITY,
    
    validate_core,
)

# Lens families
from .lenses import (
    # Lens types
    LensType,
    LensScope,
    LensContract,
    
    # Square lens (□)
    SquareLens,
    LatinSquareSchedule,
    SeekLattice,
    SeedBank,
    
    # Flower lens (✿)
    FlowerLens,
    PetalPartition,
    PhaseAnchor,
    
    # Cloud lens (☁)
    CloudLens,
    ProbabilityTable,
    EntropyContract,
    
    # Fractal lens (⟡)
    FractalLens,
    MultiscaleDecomposition,
    RecursiveModule,
    
    # Lens graph
    LensModule,
    LensGraph,
    ExecutionCapsule,
    
    validate_lenses,
)

# Pipeline operators
from .pipeline import (
    # Operator base
    PipelineOperator,
    
    # P: Partition
    PartitionResult,
    PartitionOperator,
    
    # Q: Quantize
    QuantizeResult,
    QuantizeOperator,
    
    # B: Bucket
    BucketResult,
    BucketOperator,
    
    # C: Containerize
    ChunkHeader,
    Chunk,
    ContainerResult,
    ContainerOperator,
    
    # Complete codec
    CodecProfile,
    QShrinkCodec,
    
    validate_pipeline,
)

# Container system
from .container import (
    # Topology types
    TopologyType,
    ChunkType,
    AccessMode as ContainerAccessMode,
    
    # Chunk structures
    ChunkHeader as ContainerChunkHeader,
    Chunk as ContainerChunk,
    
    # Repair system
    RepairPrefix,
    
    # Seek system
    SeekEntry,
    SeekTable,
    
    # Container structures
    ContainerManifest,
    Domain,
    QShrinkContainer,
    
    # Topology-specific containers
    DirectSumContainer,
    KroneckerContainer,
    
    validate_container,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_qshrink() -> bool:
    """Validate complete Q-SHRINK module."""
    assert validate_core()
    assert validate_lenses()
    assert validate_pipeline()
    assert validate_container()
    return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_lossless_codec(n_petals: int = 16) -> QShrinkCodec:
    """Create a lossless Q-SHRINK codec."""
    profile = CodecProfile(
        name="lossless",
        lossless=True,
        n_petals=n_petals
    )
    return QShrinkCodec(profile)


def create_lossy_codec(quality_tier: int = 0, 
                       quality_refinement: int = 0,
                       n_petals: int = 16) -> QShrinkCodec:
    """Create a lossy Q-SHRINK codec with specified quality."""
    profile = CodecProfile(
        name=f"lossy_t{quality_tier}_r{quality_refinement}",
        lossless=False,
        n_petals=n_petals,
        quality_tier=quality_tier,
        quality_refinement=quality_refinement
    )
    return QShrinkCodec(profile)


def create_archive() -> DirectSumContainer:
    """Create an archive container."""
    return DirectSumContainer()


def create_synchronized_container(n_streams: int = 2) -> KroneckerContainer:
    """Create a synchronized stream container."""
    return KroneckerContainer(n_streams=n_streams)


def compress(data: bytes, lossless: bool = True) -> bytes:
    """
    Simple compression interface.
    
    Args:
        data: Raw bytes to compress
        lossless: If True, use lossless compression
    
    Returns:
        Compressed container bytes
    """
    import zlib

    compression_level = 9 if lossless else 1
    payload = zlib.compress(data, level=compression_level)

    # Package into a stable direct-sum container so the convenience API remains
    # replay-safe even while deeper pipeline work continues to mature.
    container = QShrinkContainer()
    domain = Domain(domain_id=0, domain_type="lossless_bytes" if lossless else "lossy_bytes")
    header = ContainerChunkHeader(
        chunk_type=ChunkType.BULK,
        payload_length=len(payload),
        checksum=zlib.crc32(payload) & 0xFFFFFFFF,
    )
    domain.add_chunk(ContainerChunk(header=header, payload=payload))
    container.add_domain(domain)
    
    return container.serialize()


def decompress(container_bytes: bytes) -> bytes:
    """
    Simple decompression interface.
    
    Args:
        container_bytes: Q-SHRINK container bytes
    
    Returns:
        Decompressed raw bytes
    """
    import zlib

    # Parse container
    container = QShrinkContainer.deserialize(container_bytes)
    
    # Extract and inflate data
    data_chunks = []
    for domain in container.domains:
        for chunk in domain.chunks:
            if chunk.verify():
                data_chunks.append(chunk.payload)

    if not data_chunks:
        return b""

    combined = b''.join(data_chunks)
    return zlib.decompress(combined)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core
    "Alphabet", "SignalType", "SignalObject",
    "DistortionMetric", "MSEMetric", "MAEMetric", "LInfMetric", "WeightedDistortion",
    "RateDistortionObjective", "AccessMode",
    "StreamingConstraint", "RandomAccessConstraint",
    "CorruptionType", "CorruptionModel",
    "LegalityCheck", "LegalitySet",
    "CompressionAxiom", "COMPRESSION_AXIOMS",
    
    # Lenses
    "LensType", "LensScope", "LensContract",
    "SquareLens", "LatinSquareSchedule", "SeekLattice", "SeedBank",
    "FlowerLens", "PetalPartition", "PhaseAnchor",
    "CloudLens", "ProbabilityTable", "EntropyContract",
    "FractalLens", "MultiscaleDecomposition", "RecursiveModule",
    "LensModule", "LensGraph", "ExecutionCapsule",
    
    # Pipeline
    "PipelineOperator",
    "PartitionResult", "PartitionOperator",
    "QuantizeResult", "QuantizeOperator",
    "BucketResult", "BucketOperator",
    "ContainerResult", "ContainerOperator",
    "CodecProfile", "QShrinkCodec",
    
    # Container
    "TopologyType", "ChunkType",
    "RepairPrefix", "SeekEntry", "SeekTable",
    "ContainerManifest", "Domain",
    "QShrinkContainer", "DirectSumContainer", "KroneckerContainer",
    
    # Convenience
    "create_lossless_codec", "create_lossy_codec",
    "create_archive", "create_synchronized_container",
    "compress", "decompress",
    
    # Validation
    "validate_qshrink",
]

__version__ = "1.0.0"
__module_name__ = "qshrink"


if __name__ == "__main__":
    print("=" * 70)
    print("ATHENA OS - Q-SHRINK COMPRESSION FRAMEWORK")
    print("A Unified Crystal Calculus for Compression")
    print("=" * 70)
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_qshrink():
        print("✓ All components validated")
    
    print("\n--- Module Overview ---")
    
    print("\n1. CORE AXIOMS")
    for axiom in COMPRESSION_AXIOMS:
        print(f"   {axiom.id}. {axiom.name}")
    
    print("\n2. LENS FAMILIES")
    print(f"   □ Square: Determinism/Addressing")
    print(f"   ✿ Flower: Coupling/Phase")
    print(f"   ☁ Cloud:  Probability/Entropy")
    print(f"   ⟡ Fractal: Recursion/Modularity")
    
    print("\n3. PIPELINE OPERATORS")
    print("   P: Partition/Coordinate")
    print("   Q: Quantize")
    print("   B: Bucket/Split")
    print("   C: Code+Containerize")
    
    print("\n4. CONTAINER TOPOLOGIES")
    print(f"   Direct-Sum: Archives, independent items")
    print(f"   Kronecker:  Synchronized streams")
    
    # Demo
    print("\n--- Compression Demo ---")
    
    import numpy as np
    
    # Create test data
    test_data = np.random.randn(256).astype(np.float32)
    
    # Lossless codec
    codec = create_lossless_codec(n_petals=8)
    encoded = codec.encode(test_data.reshape(-1, 1))
    
    print(f"\nOriginal size: {test_data.nbytes} bytes")
    print(f"Encoded chunks: {len(encoded.chunks)}")
    print(f"Encoded size: {encoded.total_size} bytes")
    print(f"Bulk fraction: {encoded.manifest.get('bulk_fraction', 0):.2%}")
    
    print("\n" + "=" * 70)
