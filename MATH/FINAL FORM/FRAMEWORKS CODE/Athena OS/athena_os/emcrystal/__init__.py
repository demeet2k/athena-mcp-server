"""
ATHENA OS - EM Crystal Module
=============================
The EM-Duality-Axion Crystal and 256-Atlas System.

From CORE_CRYSTAL__biology_physics_.docx:
This module implements the physics side of the crystal framework,
providing the complete EM duality stack with:

1. DUALITY STACK
   - τ parameter: τ = θ/(2π) + 4πi/e²
   - SL(2,Z) modular group transformations
   - Field doublet (F, G) and source doublet (J_m, J_e)
   - Schwinger-Zwanziger quantization
   - Axion field dynamics

2. AETHER OBJECT
   - The 4→1 artifact containing Z* (zero point)
   - Four face projectors (Fire/Water/Air/Earth)
   - Generator set {d, *, □, M(τ), Ω, ∂}
   - Invariant set {d²=0, conservation, periodicity}
   - Expand/Collapse operations

3. 256-ATLAS
   - Address structure T[i,j,k,ℓ] (primary/influence/flavor/refinement)
   - 16 archetypes (Plasma, Lightning, Spark, Forge, etc.)
   - 64 families (16 × 4 flavors)
   - 256 leaves (64 × 4 refinements)
   - Marginal compression: 256→64→16→4→Aether

4. HUB ROUTING
   - 9 hubs (H0-H8): Curvature, Sources, Gate, Propagation, etc.
   - Decision tree for phenomenon routing
   - Parent/Flavor determination

5. SEED ENCODING
   - 14-byte compact representation
   - Quantized θ and e²
   - Mode enums (clamp, boundary, medium, symmetry)
   - Round-trip: encode(decode(seed)) = seed

KEY EQUATIONS:
    dF = *J_m           (Bianchi with magnetic sources)
    dG = *J_e           (Ampère-Maxwell)
    G = M(τ)·(F,*F)     (Constitutive with τ tilt)
    τ → (aτ+b)/(cτ+d)   (SL(2,Z) action)

The system regenerates Maxwell-Zwanziger-Witten-Axion from compact seeds.
"""

# Duality
from .duality import (
    # Constants
    PI, TAU, I,
    
    # Parameters
    TauParameter,
    
    # SL(2,Z) group
    SL2ZElement,
    
    # Doublets
    FieldDoublet, SourceDoublet,
    
    # Charges
    DyonCharge,
    
    # Axion
    AxionField,
    
    # Stack
    EMDualityStack,
    
    # Validation
    validate_duality,
)

# Aether
from .aether import (
    # Face
    Face,
    
    # Projectors
    FaceProjector, ProjectorSet,
    
    # Generators
    Generator, GeneratorSet,
    
    # Invariants
    Invariant, InvariantSet,
    
    # Zero Point
    ZeroPoint,
    
    # Aether
    Aether, AetherFactory,
    
    # Validation
    validate_aether,
)

# Atlas
from .atlas import (
    # Elements
    Element,
    
    # Address
    AtlasAddress,
    
    # Distribution
    AtlasDistribution,
    
    # Archetypes
    Archetype, ARCHETYPE_CATALOG,
    get_archetype,
    
    # Compression
    AtlasCompressor,
    
    # Validation
    validate_atlas,
)

# Hubs
from .hubs import (
    # Hub
    Hub,
    
    # Routes
    HubRoute, ARCHETYPE_ROUTES,
    get_route,
    
    # Network
    HubNetwork,
    
    # Decision
    PhenomenonQuery, DecisionTree,
    
    # Validation
    validate_hubs,
)

# Seeds
from .seeds import (
    # Enums
    ZStarMode, ClampMode, BoundaryMode, MediumMode, SymmetryMode,
    
    # Quantization
    quantize_theta, dequantize_theta,
    quantize_e_squared, dequantize_e_squared,
    
    # Seed
    AetherSeed,
    
    # Encoder/Decoder
    AetherEncoder, AetherDecoder,
    encode, decode,
    
    # Presets
    PresetSeeds,
    
    # Validation
    validate_seeds,
)


def validate_emcrystal() -> bool:
    """Validate complete EM crystal module."""
    assert validate_duality()
    assert validate_aether()
    assert validate_atlas()
    assert validate_hubs()
    assert validate_seeds()
    return True


__all__ = [
    # Constants
    'PI', 'TAU', 'I',
    
    # Duality
    'TauParameter', 'SL2ZElement',
    'FieldDoublet', 'SourceDoublet', 'DyonCharge',
    'AxionField', 'EMDualityStack',
    
    # Aether
    'Face', 'FaceProjector', 'ProjectorSet',
    'Generator', 'GeneratorSet',
    'Invariant', 'InvariantSet',
    'ZeroPoint', 'Aether', 'AetherFactory',
    
    # Atlas
    'Element', 'AtlasAddress', 'AtlasDistribution',
    'Archetype', 'ARCHETYPE_CATALOG', 'get_archetype',
    'AtlasCompressor',
    
    # Hubs
    'Hub', 'HubRoute', 'ARCHETYPE_ROUTES', 'get_route',
    'HubNetwork', 'PhenomenonQuery', 'DecisionTree',
    
    # Seeds
    'ZStarMode', 'ClampMode', 'BoundaryMode', 'MediumMode', 'SymmetryMode',
    'AetherSeed', 'encode', 'decode', 'PresetSeeds',
    
    # Validation
    'validate_emcrystal',
]
