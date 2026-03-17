"""Hybrid Coupling Module - Phase coupling, spectral invariants, eigenvalue detectors."""

from atlasforge.coupling.coupling import (
    PhaseVector,
    HybridOperator,
    TraceMoments,
    DeterminantInvariants,
    HeatKernelTrace,
    EigenvalueSpikeDetector,
    PhaseCoherence,
    HybridInvariantBundle,
    create_hybrid_coupling,
    analyze_hybrid,
    check_coherence,
    trace_fingerprint,
)

__all__ = [
    'PhaseVector',
    'HybridOperator',
    'TraceMoments',
    'DeterminantInvariants',
    'HeatKernelTrace',
    'EigenvalueSpikeDetector',
    'PhaseCoherence',
    'HybridInvariantBundle',
    'create_hybrid_coupling',
    'analyze_hybrid',
    'check_coherence',
    'trace_fingerprint',
]
