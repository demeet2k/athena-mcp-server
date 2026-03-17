"""Unified Integration Module - Cross-module connectors, pole synthesis."""

from atlasforge.integration.integration import (
    Pole,
    PoleWeights,
    UnifiedState,
    CrossPoleConnector,
    HybridPathStep,
    HybridPath,
    ShortcutDetector,
    UnifiedSolver,
    create_unified_state,
    pole_weights,
    diagnose_state,
    find_shortcut,
    hybrid_evolution,
)

__all__ = [
    'Pole',
    'PoleWeights',
    'UnifiedState',
    'CrossPoleConnector',
    'HybridPathStep',
    'HybridPath',
    'ShortcutDetector',
    'UnifiedSolver',
    'create_unified_state',
    'pole_weights',
    'diagnose_state',
    'find_shortcut',
    'hybrid_evolution',
]
