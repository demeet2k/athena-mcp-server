"""
ATHENA OS - Crystal Seed Module
===============================
The Complete 1024-Expression Meta-Crystal: The Periodic Table of Computation.

This module implements THE_CRYSTAL_SEED framework - a comprehensive
structure for organizing all mathematical operations into a navigable lattice.

Structure: 5-Dimensional Lattice (4^5 = 1024 expressions)
- Meta-Pole (4): Aether, Anti-Aether, Inner Shadow, Outer Shadow
- Constant (4): π, e, i, φ
- Sector (4): Square, Flower, Cloud, Fractal
- Element (4): Earth, Water, Fire, Air
- Level (4): L0, L1, L2, L3

The Four Meta-Poles:
1. AETHER (Positive): Operations that CONSERVE complexity (κ-budget)
   - "The Yes of Existence" - what CAN happen
   
2. ANTI-AETHER (Negative): Operations that VIOLATE complexity
   - "The No That Shapes Yes" - what CANNOT happen
   
3. INNER SHADOW (Logarithmic): The information-theoretic encoding
   - "The Code of Operations" - bit-depth of each move
   
4. OUTER SHADOW (Exponential): The boundary/saturation conditions
   - "The Texture Horizon" - where operations saturate

The Four Constants:
- π: Density, normalization, geometric closure
- e: Growth, decay, completeness
- i: Reconstruction, reversal, phase coherence
- φ: Self-similarity, recursion, scale invariance

Tunneling Mechanism:
When a trajectory approaches a barrier, it rotates 90° through the shadow axis:
- Aether ↔ Anti-Aether (Horizontal: Magnitude axis)
- Inner ↔ Outer Shadow (Vertical: Structure axis)

Verification Protocol:
- Basin Identification System (BIS): Clustering states into semantic basins
- Hoeffding confidence intervals with delta ledger
- Tunnel certification: baseline-low AND capture-high
- F9.4 controls: drift, timing, ablation, random edit, replication

Core Components:
- lattice.py: 1024-expression Crystal Lattice structure
- expressions.py: Expression validators and impossible move catalog
- tunneling.py: 90° rotation mechanism and shadow encodings
- verification.py: Statistical verification protocol for tunneling
"""

from .lattice import (
    # Enums
    MetaPole,
    Constant,
    Sector,
    Element,
    Level,
    
    # Core classes
    CrystalAddress,
    CrystalExpression,
    ExpressionCatalog,
    CrystalLattice,
)

from .expressions import (
    # Enums
    ViolationType,
    
    # Classes
    ImpossibleMove,
    ExpressionValidator,
    
    # Catalogs
    ANTI_PI_MOVES,
    ANTI_E_MOVES,
    ANTI_I_MOVES,
    ANTI_PHI_MOVES,
)

from .tunneling import (
    # Enums
    TunnelDirection,
    
    # Classes
    TunnelPath,
    ShadowEncoding,
    TunnelingEngine,
    CirculationPath,
    
    # Shadow encodings
    PI_INNER_SHADOWS,
    E_INNER_SHADOWS,
    I_INNER_SHADOWS,
    PHI_INNER_SHADOWS,
)

from .verification import (
    # Enums
    BasinType,
    TunnelVerdict,
    
    # Classes
    Basin,
    BasinIdentificationSystem,
    ConfidenceInterval,
    LedgerRow,
    DeltaLedger,
    BarrierMetrics,
    BridgeCandidate,
    VerificationResult,
    VerificationProtocol,
    
    # Functions
    hoeffding_half_width,
    compute_confidence_interval,
    compute_barrier,
)

__all__ = [
    # Lattice
    'MetaPole', 'Constant', 'Sector', 'Element', 'Level',
    'CrystalAddress', 'CrystalExpression', 'ExpressionCatalog', 'CrystalLattice',
    
    # Expressions
    'ViolationType', 'ImpossibleMove', 'ExpressionValidator',
    'ANTI_PI_MOVES', 'ANTI_E_MOVES', 'ANTI_I_MOVES', 'ANTI_PHI_MOVES',
    
    # Tunneling
    'TunnelDirection', 'TunnelPath', 'ShadowEncoding',
    'TunnelingEngine', 'CirculationPath',
    'PI_INNER_SHADOWS', 'E_INNER_SHADOWS', 'I_INNER_SHADOWS', 'PHI_INNER_SHADOWS',
    
    # Verification
    'BasinType', 'TunnelVerdict',
    'Basin', 'BasinIdentificationSystem',
    'ConfidenceInterval', 'LedgerRow', 'DeltaLedger',
    'BarrierMetrics', 'BridgeCandidate', 'VerificationResult', 'VerificationProtocol',
    'hoeffding_half_width', 'compute_confidence_interval', 'compute_barrier',
]
