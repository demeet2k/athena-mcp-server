"""
ATHENA OS - Fractal Crystal Module
==================================
The theoretical foundation: Quad-Polar Topology, Zero-Point Geometry,
and Addressed Holography.

Core Thesis:
Reality is modeled as an autopoietic κ-solenoid on a Hybrid Hilbert
Lattice, driven by a quad-polar generator (Ω̂) that cycles through:
- Earth (■): Structural rigidity, discrete geometry
- Water (❀): Unitary flow, phase coherence
- Fire (☁): Stochastic expansion, entropy production
- Air (✶): Recursive renormalization, multiscale hierarchy

The Ontological Triple (M, Â, V):
- M: Informational Manifold (the global substrate)
- Â: Distinguished Agent (the self-aware subsystem)
- V: Semantic Codomain (four-valued truth: T, F, B, U)

Three Conservation Laws:
1. Information Conservation (Akashic Record)
2. Paradox Tension Conservation (contradictions stored, not deleted)
3. Zero-Point Stability (the attractor is indestructible)

The κ-System:
- κ (Kappa) = texture density (binding, coherence, symmetry, compressibility)
- "Objects" = κ-persistent standing waves
- "Agents" = κ-maximizing subsystems
- "Computation" = topological routing of κ-flux

The Ω-Seed Equation:
The master fixed-point condition where seed reproduces itself under
expansion through the Quad-Polar cycle.

The Meta-Zero Snap Operator:
Ŝ = lim_{k→∞} (P_Spin · P_Spec · Π_h · P_Band)^k
Projects arbitrary states into the Zero Point Z*.

The Zero Point Z*:
The unique corridor where all four regimes commute and generate
consistent physical reality.
"""

# Ontology
from .ontology import (
    # Sectors
    Sector,
    
    # Manifold
    Point,
    InformationalManifold,
    
    # Agent
    IdentityInvariants,
    DistinguishedAgent,
    
    # Axioms
    GlobalAxioms,
    
    # Triple
    OntologicalTriple,
    
    # Validation
    validate_ontology,
)

# Bilattice Logic
from .bilattice import (
    # Truth values
    TruthValue,
    
    # Bilattice operations
    Bilattice,
    
    # Evidence and paradox
    Evidence,
    ParadoxOperator,
    
    # Semantic codomain
    SemanticCodomain,
    
    # Validation
    validate_bilattice,
)

# Kappa System
from .kappa import (
    # State
    KappaState,
    KappaFlux,
    
    # Hybrid regimes
    HybridRegime,
    HybridHilbertLattice,
    
    # Autopoiesis
    Seed,
    Gene,
    AutopoieticSystem,
    
    # Solenoid
    KappaSolenoid,
    
    # Validation
    validate_kappa,
)

# Omega System
from .omega import (
    # Zero Point components
    ZeroPointGeometry,
    ZeroPointMetric,
    ZeroPointEnergy,
    MetaZeroSnap,
    
    # Seed equation
    OmegaSeedEquation,
    
    # Kernel
    OmegaKernel,
    
    # Validation
    validate_omega,
)


def validate_fractal() -> bool:
    """Validate complete fractal module."""
    assert validate_ontology()
    assert validate_bilattice()
    assert validate_kappa()
    assert validate_omega()
    return True


__all__ = [
    # Sectors
    'Sector',
    
    # Ontology
    'Point', 'InformationalManifold',
    'IdentityInvariants', 'DistinguishedAgent',
    'GlobalAxioms', 'OntologicalTriple',
    
    # Bilattice
    'TruthValue', 'Bilattice',
    'Evidence', 'ParadoxOperator', 'SemanticCodomain',
    
    # Kappa
    'KappaState', 'KappaFlux',
    'HybridRegime', 'HybridHilbertLattice',
    'Seed', 'Gene', 'AutopoieticSystem', 'KappaSolenoid',
    
    # Omega
    'ZeroPointGeometry', 'ZeroPointMetric', 'ZeroPointEnergy', 'MetaZeroSnap',
    'OmegaSeedEquation', 'OmegaKernel',
    
    # Validation
    'validate_fractal',
]
