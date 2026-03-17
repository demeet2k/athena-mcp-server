"""
ATHENA OS - Forces Module
=========================
A (4^4) Lens Calculus for the Four Fundamental Forces.

Components:
- framework: Core structures (Lens, Force, ForceTheory, etc.)
- implementations: Concrete force implementations (EM, Weak, Strong, Gravity)
- rotation: Rotation calculus (gauge, duality, RG flow, etc.)

The Four Forces:
1. Electromagnetism (U(1) gauge)
2. Weak Force (SU(2)×U(1) → U(1))
3. Strong Force (SU(3) QCD)
4. Gravity (Diffeomorphisms)

The Four Lenses:
1. Square/Earth: Structure, carriers, constraints
2. Flower/Water: Symmetry, coherence, transport
3. Cloud/Fire: Measure, probability, path integrals
4. Fractal/Air: Scale, RG, effective theories
"""

from .framework import (
    # Enums
    Lens, Role, Force,
    # Address
    ForceAddress,
    # Core objects
    Carrier, ConstraintObject, Presentation,
    ForceTheory, Rotation, RotationType,
    Certificate, WitnessBunde,
)

from .implementations import (
    # Force creators
    create_electromagnetism,
    create_weak_force,
    create_strong_force,
    create_gravity,
    # Registry
    ForceRegistry,
    # Standard rotations
    create_gauge_rotation,
    create_duality_rotation,
    create_weinberg_rotation,
)

from .rotation import (
    # Transport maps
    TransportMap,
    GaugeRotation,
    CongruenceRotation,
    DualityRotation,
    DiffeomorphismRotation,
    DiscretizationRotation,
    RGFlowRotation,
    # Algebra
    RotationAlgebra,
    # Certification
    SnapCertificate,
    compute_snap,
)

__all__ = [
    # Enums
    'Lens', 'Role', 'Force',
    # Address
    'ForceAddress',
    # Core objects
    'Carrier', 'ConstraintObject', 'Presentation',
    'ForceTheory', 'Rotation', 'RotationType',
    'Certificate', 'WitnessBunde',
    # Force creators
    'create_electromagnetism', 'create_weak_force',
    'create_strong_force', 'create_gravity',
    'ForceRegistry',
    # Standard rotations
    'create_gauge_rotation', 'create_duality_rotation',
    'create_weinberg_rotation',
    # Transport maps
    'TransportMap', 'GaugeRotation', 'CongruenceRotation',
    'DualityRotation', 'DiffeomorphismRotation',
    'DiscretizationRotation', 'RGFlowRotation',
    # Algebra
    'RotationAlgebra',
    # Certification
    'SnapCertificate', 'compute_snap',
]
