"""
ATHENA OS - Math Fundamentals Module
====================================
The Lens-Zero Crystal Framework for Hybrid Constants and Alien Operations.

CORE THESIS (Square/Formal):
Validity-by-construction: if a lens T: D → ℝ is a bijection, then
transporting algebra and analysis through T yields internally consistent
"alien" mathematics on D that is isomorphic to standard mathematics on ℝ.

GEOMETRIC THESIS (Flower):
All major operator families unify under one geometric bridge:
    x^i = e^(i·ln(x)) = cos(ln(x)) + i·sin(ln(x))

Thus:
- Multiplication in x becomes translation in ln(x)
- Translation becomes rotation in phase
- Powers become scalings: ln(x^p) = p·ln(x)

ALGORITHMIC THESIS (Cloud):
Every result is produced by a standardized pipeline:
1. Normalize expressions to lens-aware canonical form
2. Reduce constraints (equality → root; products → logs)
3. Enumerate discrete lattice indices (k, m, n, ...)
4. Solve numerically (bracketing/Newton/homotopy)
5. Certify (interval enclosures, monotonicity, Jacobian rank)
6. Ledger-store (lens + generators + certificates)

PROGRAM THESIS (Fractal):
- Hybrid constants as certified seeds and infinite families
- Alien operations (transported fields + engineered hybrids)
- Transformation algorithms (conjugacy maps between manuscripts)
- A tile grammar enabling recombination under corridor constraints

FOUR GENERATORS:
1. Lens Conjugacy: f_T = T⁻¹∘f∘T (the rotation law)
2. Transported Algebra: ⊕_T, ⊗_T (validity-by-construction)
3. Zero Hierarchy: H=0 → H'=0 → det J=0 (precision hardening)
4. Lattice Preimage Principle: cross symmetries in t-space become
   infinite constant families in x-space via T⁻¹

Everything else unfolds deterministically from these four generators.
"""

# Lenses
from .lenses import (
    # Constants
    PHI, PHI_INV, LN_PHI, PHI_CONJUGATE,
    E, PI, TAU, GOLDEN_ANGLE,
    
    # Domain
    DomainType, Domain,
    
    # Lens
    Lens, LensRegistry,
    TransportedOperator, PoleStructure,
    
    # Lens factories
    create_ln_lens, create_exp_lens, create_log_base_lens,
    create_phi_log_lens, create_quarter_turn_lens,
    create_phase_lens, create_affine_lens,
    create_power_lens, create_identity_lens,
    
    # Validation
    validate_lenses,
)

# Algebra
from .algebra import (
    # Transported field
    TransportedField,
    LogField, PhiField,
    
    # Alien operations
    AlienOperation, AlienOperationFactory,
    HybridOperation,
    
    # Identity transport
    transport_identity,
    pythagorean_identity, exponential_identity, log_identity,
    
    # Validation
    validate_algebra,
)

# Zeros
from .zeros import (
    # Zero types
    ZeroType,
    
    # Zero structures
    ZeroPoint, ZeroSet, ZeroHierarchy,
    IntersectionZero, CrossSymmetryZero,
    CancellationZero,
    
    # Lattice zeros
    LatticeZero,
    
    # Validation
    validate_zeros,
)

# Compiler
from .compiler import (
    # Tile specification
    TileType, TileSpec,
    
    # Normalization
    NormalizedConstraint, Normalizer,
    
    # Solving
    Solver,
    
    # Certification
    CertificateType, Certificate,
    
    # Ledger
    LedgerEntry, Ledger,
    
    # Compiler
    ConstantCompiler,
    
    # Validation
    validate_compiler,
)


def validate_mathfund() -> bool:
    """Validate complete math fundamentals module."""
    assert validate_lenses()
    assert validate_algebra()
    assert validate_zeros()
    assert validate_compiler()
    return True


__all__ = [
    # Constants
    'PHI', 'PHI_INV', 'LN_PHI', 'PHI_CONJUGATE',
    'E', 'PI', 'TAU', 'GOLDEN_ANGLE',
    
    # Lenses
    'DomainType', 'Domain', 'Lens', 'LensRegistry',
    'TransportedOperator', 'PoleStructure',
    'create_ln_lens', 'create_exp_lens', 'create_log_base_lens',
    'create_phi_log_lens', 'create_quarter_turn_lens',
    'create_phase_lens', 'create_affine_lens',
    'create_power_lens', 'create_identity_lens',
    
    # Algebra
    'TransportedField', 'LogField', 'PhiField',
    'AlienOperation', 'AlienOperationFactory', 'HybridOperation',
    'transport_identity',
    
    # Zeros
    'ZeroType', 'ZeroPoint', 'ZeroSet', 'ZeroHierarchy',
    'IntersectionZero', 'CrossSymmetryZero', 'CancellationZero',
    'LatticeZero',
    
    # Compiler
    'TileType', 'TileSpec',
    'NormalizedConstraint', 'Normalizer', 'Solver',
    'CertificateType', 'Certificate',
    'LedgerEntry', 'Ledger', 'ConstantCompiler',
    
    # Validation
    'validate_mathfund',
]
