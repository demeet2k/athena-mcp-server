"""
ATHENA OS - Mathematical Foundations Module
===========================================
Lens-invariant framework for constructing and transforming mathematical objects.

The central claim: Validity-by-construction
If T: D → ℝ is a bijection, then transporting algebra through T yields
internally consistent "alien" mathematics on D isomorphic to standard ℝ.

Core Components:

1. Lens System (lenses.py)
   - Coordinate isomorphisms T: D → ℝ
   - Transported operators f_T = T⁻¹ ∘ f ∘ T
   - Transported arithmetic ⊕_T, ⊗_T
   - Standard lenses: ln, exp, log_φ, φ-phase, warped periodic

2. Symmetry Geometry (symmetry.py)
   - Dihedral D₄ actions (rotations, mirrors)
   - Poles, shadows, crosses
   - Lattice atlas (axis/diagonal preimages)
   - Unification bridge: scale ↔ translation ↔ rotation

3. Zero Calculus (zeros.py)
   - Zero structures Z(H)
   - Order-m zeros ("zero of zero of zero...")
   - Singular seeds (det J = 0)
   - Multiplicity transport theorem

4. Constraint System (constraints.py)
   - Fixed-point, equalization, cancellation locks
   - Jet locks (hardening)
   - Seed ledger (holographic storage)
   - Construction pipeline

5. Crystal Combat (crystal_combat.py)
   - 4×4 problem-solving framework
   - Square/Flower/Cloud/Fractal lenses
   - Pivot + supports rule
   - Z* certificate verification

The Four Items That Reconstruct Everything:
1. Lens Conjugacy: f_T = T⁻¹ ∘ f ∘ T
2. Transported Algebra: ⊕_T, ⊗_T
3. Zero Hierarchy: H=0 → H'=0 → det J=0
4. Lattice Preimage Principle: T⁻¹(L)
"""

from .lenses import (
    # Base classes
    Lens, ComposedLens,
    # Standard lenses
    IdentityLens, LogLens, ExpLens, LogBaseLens,
    PhiLogLens, TrigPhaseLens, WarpedPeriodicLens, PhaseLens,
    # Transported operations
    TransportedField, KappaField, kappa_sum,
    # Registry
    LensRegistry,
    # Constants
    PHI,
)

from .symmetry import (
    # Dihedral group
    DihedralElement, D4Action,
    # Symmetry operators
    SymmetryOperator,
    create_rotation_operator, create_negation_operator,
    create_mirror_operator, create_diagonal_operator,
    # Poles and shadows
    PoleType, Pole,
    # Lattices
    LatticeType, Lattice, LatticeAtlas,
    SIN_ZERO_LATTICE, COS_ZERO_LATTICE,
    DIAGONAL_POS_LATTICE, DIAGONAL_NEG_LATTICE,
    # Unification bridge
    PhaseBridge, PhiSymmetry,
)

from .zeros import (
    # Zero structures
    ZeroType, ZeroPoint, ZeroSet,
    IntersectionZero, MultiwayIntersection, CancellationZero,
    # Singular seeds
    SingularSeed,
    # Zero-of-zero chains
    ZeroOfZeroChain,
    # Multiplicity transport
    MultiplicityTransport,
)

from .constraints import (
    # Constraint types
    ConstraintType, Constraint,
    # Constraint builders
    fixed_point_constraint, equalization_constraint,
    cancellation_constraint, lattice_constraint, jet_lock_constraint,
    # Certificates and seeds
    Certificate, Seed, SeedLedger,
    # Compiler
    SeedCompiler,
    # Hybrid constants
    create_lattice_preimage_constant, create_phase_lock_constant,
    create_hardened_constant,
)

from .crystal_combat import (
    # Lenses
    ProblemLens, LensArtifact,
    # Lens artifacts
    SquareArtifacts, FlowerArtifacts, CloudArtifacts, FractalArtifacts,
    # Problem representation
    Problem,
    # Z* structures
    ZStarLock, ZStarCertificate,
    # Pivot
    Pivot, PivotSelector,
    # Crystal Combat solver
    CrystalCombat, TunnelRule,
)

__all__ = [
    # Lenses
    'Lens', 'ComposedLens',
    'IdentityLens', 'LogLens', 'ExpLens', 'LogBaseLens',
    'PhiLogLens', 'TrigPhaseLens', 'WarpedPeriodicLens', 'PhaseLens',
    'TransportedField', 'KappaField', 'kappa_sum',
    'LensRegistry', 'PHI',
    # Symmetry
    'DihedralElement', 'D4Action',
    'SymmetryOperator',
    'create_rotation_operator', 'create_negation_operator',
    'create_mirror_operator', 'create_diagonal_operator',
    'PoleType', 'Pole',
    'LatticeType', 'Lattice', 'LatticeAtlas',
    'SIN_ZERO_LATTICE', 'COS_ZERO_LATTICE',
    'DIAGONAL_POS_LATTICE', 'DIAGONAL_NEG_LATTICE',
    'PhaseBridge', 'PhiSymmetry',
    # Zeros
    'ZeroType', 'ZeroPoint', 'ZeroSet',
    'IntersectionZero', 'MultiwayIntersection', 'CancellationZero',
    'SingularSeed', 'ZeroOfZeroChain', 'MultiplicityTransport',
    # Constraints
    'ConstraintType', 'Constraint',
    'fixed_point_constraint', 'equalization_constraint',
    'cancellation_constraint', 'lattice_constraint', 'jet_lock_constraint',
    'Certificate', 'Seed', 'SeedLedger', 'SeedCompiler',
    'create_lattice_preimage_constant', 'create_phase_lock_constant',
    'create_hardened_constant',
    # Crystal Combat
    'ProblemLens', 'LensArtifact',
    'SquareArtifacts', 'FlowerArtifacts', 'CloudArtifacts', 'FractalArtifacts',
    'Problem', 'ZStarLock', 'ZStarCertificate',
    'Pivot', 'PivotSelector', 'CrystalCombat', 'TunnelRule',
]
