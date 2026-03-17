"""
ATHENA OS - Quantum Holography Computing (QHC) Module
=====================================================
A boundary/bulk execution model for quantum computing on classical hardware.

Core Components:

1. Operation Atlas (framework.py)
   - 1024-regime coordinate system: (C, S, E, L, P)
   - Geometry: π (rotation), e (exponential), i (phase), φ (scale)
   - Surface: Square, Flower, Cloud, Fractal
   - Element: Earth, Water, Air, Fire
   - Level: L0-L3 (primitive → spectral)
   - Pole: Aether, Anti, Inner, Outer

2. Quantum Semantics (framework.py)
   - QuantumState: Pure states |ψ⟩ and mixed states ρ
   - QuantumChannel: CPTP maps via Kraus operators
   - POVM: Measurement with probabilities and sampling

3. Bulk Representation (bulk.py)
   - BlockTree: Adaptive Hilbert space decomposition
   - BlockTreeTile: Individual tiles with payload and metadata
   - ModeWord: Boundary control for representation
   - ErrorLedger: Budget tracking (ε, δ)
   - KappaTexture: Health metrics for corridor enforcement

4. Runtime Primitives (runtime.py)
   - ApplyPrimitive: Gates and channels
   - ChangePrimitive: Basis transforms
   - RestructurePrimitive: Tile restructuring
   - MeasurePrimitive: Certified sampling

5. Zero-Point Control (runtime.py)
   - SnapController: Corridor repair
   - ParadoxResolver: Center-finding
   - HarmoniaPlanner: Adaptive planning

6. Proof-Carrying Artifacts (runtime.py)
   - Seed, Recipe, ProofPack, AuditLog
   - Hash-chained execution trace
   - Independent verification

The framework provides:
- Semantic completeness (any circuit is realizable)
- Structure-conditioned efficiency (exploits structure when present)
- Certificate-first rigor (every approximation is bounded)
"""

from .framework import (
    # Atlas enums
    Geometry, Surface, Element, Level, Pole,
    # Atlas coordinate
    AtlasCoordinate, OperationAtlas,
    # QHC address
    QHCLens, QHCFacet, QHCAddress,
    # Quantum semantics
    QuantumState, QuantumChannel, POVM,
)

from .bulk import (
    # Mode word
    BasisChart, CompressionMethod, PrecisionDiscipline,
    DeterminismLevel, OperationRole, FibreSymmetry, ModeWord,
    # Error tracking
    ErrorBudget, ErrorLedger,
    # κ-metrics
    KappaTexture, KappaCorridor,
    # Block tree
    TilePayload, BlockTreeTile, BlockTree,
)

from .runtime import (
    # Primitive types
    PrimitiveType, PrimitiveResult, RuntimePrimitive,
    # Primitives
    ApplyPrimitive, ChangePrimitive, RestructurePrimitive, MeasurePrimitive,
    # Controllers
    SnapController, SnapResult, ParadoxResolver, HarmoniaPlanner,
    # Certificates
    Certificate, Seed, Recipe, ProofPack, AuditLogEntry, AuditLog,
    ProofCarryingArtifact,
    # Runtime
    QHCRuntime,
)

__all__ = [
    # Atlas
    'Geometry', 'Surface', 'Element', 'Level', 'Pole',
    'AtlasCoordinate', 'OperationAtlas',
    'QHCLens', 'QHCFacet', 'QHCAddress',
    # Quantum semantics
    'QuantumState', 'QuantumChannel', 'POVM',
    # Mode word
    'BasisChart', 'CompressionMethod', 'PrecisionDiscipline',
    'DeterminismLevel', 'OperationRole', 'FibreSymmetry', 'ModeWord',
    # Error tracking
    'ErrorBudget', 'ErrorLedger',
    # κ-metrics
    'KappaTexture', 'KappaCorridor',
    # Block tree
    'TilePayload', 'BlockTreeTile', 'BlockTree',
    # Primitives
    'PrimitiveType', 'PrimitiveResult', 'RuntimePrimitive',
    'ApplyPrimitive', 'ChangePrimitive', 'RestructurePrimitive', 'MeasurePrimitive',
    # Controllers
    'SnapController', 'SnapResult', 'ParadoxResolver', 'HarmoniaPlanner',
    # Certificates
    'Certificate', 'Seed', 'Recipe', 'ProofPack', 'AuditLogEntry', 'AuditLog',
    'ProofCarryingArtifact',
    # Runtime
    'QHCRuntime',
]
