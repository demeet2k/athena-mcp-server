"""
ATHENA OS - Hybrid Holo-Lens Module
====================================
The 4⁴ Crystal Framework for Hybrid Reality Representation.

Core Thesis:
Reality is modeled as an autopoietic κ-solenoid evolving on a
hybrid Hilbert lattice. The framework provides uniform extraction
and verification across all representations.

The Four Lenses:
- ■ Square (D): Discrete, dissipative, local rules, constraints
- ❀ Flower (Ω): Oscillatory, conservative, spectral, phase
- ☁ Cloud (Σ): Stochastic, ensemble, mixing, uncertainty
- ✶ Fractal (Ψ): Recursive, multiscale, renormalization

The Four Cells:
- Atoms: Formal objects, axioms, definitions
- Rotations: Operators, transformations, constructions
- Shadows: Invariants, theorems, preserved quantities
- Patches: Protocols, artifacts, repair mechanisms

Key Components:
1. Crystal Structure: 4⁴ extraction lattice (21 chapters × 4 lenses × 4 cells × 4 artifacts)
2. Anti-Symmetry: Defect detection and repair operators
3. Verification: Invariant ledgers, commutator budgets, snap controller
4. Seed-Flower Bridge: Phase quantization between discrete and continuous
5. Hybrid Hilbert Lattice: Unified state space with four corners

The Snap Operator:
Z★ = P_spin,ε ○ P_≤Λ ○ Π_h ○ P_B
Produces verified shared state across all crystal corners.
"""

# Crystal structure
from .crystal import (
    # Enums
    Lens,
    Cell,
    Corner,
    
    # Coordinates
    CrystalCoordinate,
    CrystalNode,
    CrystalLattice,
    
    # Operators
    LensOperator,
    SquareOperator,
    FlowerOperator,
    CloudOperator,
    FractalOperator,
    
    # Validation
    validate_crystal,
)

# Anti-symmetry framework
from .antisymmetry import (
    # Types
    DefectType,
    Defect,
    
    # Detection
    DefectDetector,
    
    # Repair operators
    RepairOperator,
    TikhonovRegularizer,
    AntiAliasFilter,
    WindowTaper,
    MultiscaleSmoother,
    
    # Budget
    CommutatorBudget,
    
    # Validation
    validate_antisymmetry,
)

# Verification harness
from .verification import (
    # Invariants
    InvariantType,
    Invariant,
    InvariantLedger,
    
    # Stability
    StabilityRegion,
    
    # Snap controller
    SnapController,
    
    # Certificates
    CrossScaleCertificate,
    
    # Validation
    validate_verification,
)

# Seed-Flower bridge
from .bridge import (
    # Phase structure
    PhaseClass,
    
    # Seed crystal
    SeedCrystal,
    
    # Flower pattern
    FlowerPattern,
    
    # Bridge
    SeedFlowerBridge,
    
    # Hybrid lattice
    HybridHilbertLattice,
    
    # Validation
    validate_bridge,
)


def validate_hololens() -> bool:
    """Validate complete hololens module."""
    assert validate_crystal()
    assert validate_antisymmetry()
    assert validate_verification()
    assert validate_bridge()
    return True


__all__ = [
    # Crystal
    'Lens', 'Cell', 'Corner',
    'CrystalCoordinate', 'CrystalNode', 'CrystalLattice',
    'LensOperator', 'SquareOperator', 'FlowerOperator',
    'CloudOperator', 'FractalOperator',
    
    # Anti-symmetry
    'DefectType', 'Defect', 'DefectDetector',
    'RepairOperator', 'TikhonovRegularizer', 'AntiAliasFilter',
    'WindowTaper', 'MultiscaleSmoother', 'CommutatorBudget',
    
    # Verification
    'InvariantType', 'Invariant', 'InvariantLedger',
    'StabilityRegion', 'SnapController', 'CrossScaleCertificate',
    
    # Bridge
    'PhaseClass', 'SeedCrystal', 'FlowerPattern',
    'SeedFlowerBridge', 'HybridHilbertLattice',
    
    # Validation
    'validate_hololens',
]
