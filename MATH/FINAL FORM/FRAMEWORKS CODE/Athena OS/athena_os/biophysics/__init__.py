"""
ATHENA OS - Biophysics Module (Biology-Physics Crystal Extension)
=================================================================
The crystal framework extended to biological systems.

Core Thesis:
- Physics: conserved ENERGY/ACTION in REVERSIBLE dynamics
- Biology: conserved INFORMATION in DISSIPATIVE dynamics

Biology begins when Earth clamps become persistent and heritable.

The Four Pillars in Biology:
- ?? Fire: Metabolism / Energy acquisition
- ?? Water: Replication / Growth / Population flow
- ?? Air: Sensing / Signaling / Regulation
- ?? Earth: Structure / Boundary / Genome / Membrane

Life exists ONLY when all four are present simultaneously.

The 256 Bio-Atlas:
- 16 Parent Archetypes (4×4 Primary[Influence])
- 64 Expansion (+Flavor: stress/dynamics/rewiring/lock)
- 256 Full Address (+Refinement: threshold/regime/channel/lock)

The 8 Bio Hubs (Metro Map):
- BH1 Energy: ATP budget, redox, fuel
- BH2 Replication: DNA copying, cell cycle
- BH3 Regulation: Signaling, hormones
- BH4 Boundary: Membranes, compartments
- BH5 Code: Genome, transcription
- BH6 Error Control: Repair, checkpoints
- BH7 Selection: Fitness, competition
- BH8 Transport: Diffusion, circulation

Viability Corridor:
K_bio = {S : energy > 0, boundary exists, error < catastrophe}

Shadow System:
- Inner Shadow: Information depth (code complexity)
- Outer Shadow: Saturation horizons (error catastrophe, starvation)

Anti-Aether (Bio):
- No free replication
- No lineage rollback
- No infinite growth
"""

# Aether foundation
from .aether import (
    # Pillars
    BioPillar,
    
    # Zero point
    BiologicalZeroPoint,
    
    # State bundle
    BioState,
    
    # Aether
    BiologicalAether,
    
    # Invariants
    BiologicalInvariant,
    SURVIVAL_INVARIANT,
    LINEAGE_INVARIANT,
    ERROR_TOLERANCE_INVARIANT,
    
    # Validation
    validate_aether,
)

# Biological clans (16 archetypes)
from .clans import (
    # Address
    BioAddress,
    
    # Archetypes
    BioArchetype,
    ARCHETYPES,
    
    # Fire clan
    FIRE_FIRE, FIRE_WATER, FIRE_AIR, FIRE_EARTH,
    
    # Water clan
    WATER_FIRE, WATER_WATER, WATER_AIR, WATER_EARTH,
    
    # Air clan
    AIR_FIRE, AIR_WATER, AIR_AIR, AIR_EARTH,
    
    # Earth clan
    EARTH_FIRE, EARTH_WATER, EARTH_AIR, EARTH_EARTH,
    
    # Utilities
    get_archetype,
    get_archetype_by_index,
    get_clan,
    expand_to_64,
    expand_to_256,
    
    # Validation
    validate_clans,
)

# Bio Metro Map
from .metro import (
    # Hubs
    BioHub,
    
    # Lines
    BioMetroLine,
    LINE_IMMUNE,
    LINE_METABOLIC,
    LINE_DEVELOPMENT,
    LINE_CANCER,
    LINE_GENETIC,
    LINE_STRUCTURAL,
    LINE_EVOLUTIONARY,
    LINE_LIFE_CYCLE,
    METRO_LINES,
    
    # Metro map
    BioMetroMap,
    BIO_METRO,
    
    # Router
    PhenomenonRoute,
    BioRouter,
    BIO_ROUTER,
    
    # Validation
    validate_metro,
)

# Corridors and shadows
from .corridors import (
    # Constraints
    CorridorConstraint,
    ENERGY_CORRIDOR,
    ATP_CORRIDOR,
    BOUNDARY_CORRIDOR,
    ERROR_CORRIDOR,
    VIABILITY_CORRIDOR,
    STANDARD_CONSTRAINTS,
    
    # Viability corridor
    ViabilityCorridor,
    VIABILITY,
    
    # Shadows
    InnerShadow,
    OuterShadow,
    detect_shadow_pole,
    
    # Anti-Aether
    AntiAether,
    
    # Validation
    validate_corridors,
)


def validate_biophysics() -> bool:
    """Validate complete biophysics module."""
    assert validate_aether()
    assert validate_clans()
    assert validate_metro()
    assert validate_corridors()
    return True


__all__ = [
    # Pillars
    'BioPillar',
    
    # State
    'BioState', 'BiologicalZeroPoint', 'BiologicalAether',
    
    # Address
    'BioAddress', 'BioArchetype', 'ARCHETYPES',
    
    # Clans
    'FIRE_FIRE', 'FIRE_WATER', 'FIRE_AIR', 'FIRE_EARTH',
    'WATER_FIRE', 'WATER_WATER', 'WATER_AIR', 'WATER_EARTH',
    'AIR_FIRE', 'AIR_WATER', 'AIR_AIR', 'AIR_EARTH',
    'EARTH_FIRE', 'EARTH_WATER', 'EARTH_AIR', 'EARTH_EARTH',
    
    # Metro
    'BioHub', 'BioMetroLine', 'BioMetroMap', 'BIO_METRO',
    'PhenomenonRoute', 'BioRouter', 'BIO_ROUTER',
    
    # Corridors
    'ViabilityCorridor', 'VIABILITY',
    'InnerShadow', 'OuterShadow', 'AntiAether',
    
    # Validation
    'validate_biophysics',
]
