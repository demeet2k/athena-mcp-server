"""
ATHENA OS - THE MATH OF ALCHEMY
================================
The Mathematical System of Alchemy

A rigorous mathematical framework treating alchemy as a dynamical system:

    A = (S, O, D)

where:
    S = State Space (elemental × quality × planetary × zodiacal)
    O = Operator Family (Tria Prima + Planetary + Zodiacal)
    D = Dynamical Law (evolution, cycles, attractors)

MODULES:
    elements.py      - Four Elements and Quality Space
    tria_prima.py    - Sulfur, Mercury, Salt Operators
    planetary.py     - Seven Planetary Operators
    zodiac.py        - Twelve Zodiacal Archetypes
    stone.py         - Philosopher's Stone as Attractor

CORE CONCEPTS:
    Four Elements: Fire (??), Air (??), Water (??), Earth (??)
    Four Qualities: Hot/Cold, Moist/Dry
    Three Principles: Sulfur (??), Mercury (☿), Salt (??)
    Seven Planets: ☉, ☾, ☿, ♀, ♂, ♃, ♄
    Twelve Signs: ♈♉♊♋♌♍♎♏♐♑♒♓
    Four Stages: Nigredo, Albedo, Citrinitas, Rubedo

MATHEMATICAL STRUCTURES:
    V_elem ≅ ℝ⁴ or ℂ⁴ - Elemental state space
    Q_qual ≅ ℝ² - Quality space (heat, moisture)
    Δ³ - Elemental 3-simplex
    Lie algebra of archetypes
    Dynamical systems theory

SOURCES:
    THE MATH OF ALCHEMY
    Classical Alchemical Tradition
"""

__version__ = "1.0.0"
__author__ = "ATHENA OS"

# =============================================================================
# IMPORTS
# =============================================================================

# Elements Module
from .elements import (
    # Types
    Element,
    Quality,
    
    # Classes
    ElementalState,
    QualityState,
    QualityMapping,
    ElementalSimplex,
    ElementalSystem,
    
    # Validation
    validate_elements,
)

# Tria Prima Module
from .tria_prima import (
    # Types
    PrincipleType,
    Modality,
    
    # Classes
    SulfurOperator,
    MercuryOperator,
    SaltOperator,
    TriaPrimaSystem,
    
    # Validation
    validate_tria_prima,
)

# Planetary Module
from .planetary import (
    # Types
    Planet,
    
    # Classes
    PlanetaryMatrices,
    PlanetaryOperator,
    PlanetarySystem,
    MetallicTransformation,
    
    # Validation
    validate_planetary,
)

# Zodiac Module
from .zodiac import (
    # Types
    ZodiacSign,
    AlchemicalOperation,
    
    # Classes
    ZodiacMatrices,
    ZodiacOperator,
    ZodiacSystem,
    MagnumOpus,
    
    # Validation
    validate_zodiac,
)

# Stone Module
from .stone import (
    # Types
    WorkStage,
    
    # Classes
    PhilosophersStone,
    StoneFinder,
    StabilityAnalyzer,
    AlchemicalSystem,
    
    # Validation
    validate_stone,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Elements
    'Element', 'Quality', 'ElementalState', 'QualityState',
    'QualityMapping', 'ElementalSimplex', 'ElementalSystem',
    
    # Tria Prima
    'PrincipleType', 'Modality', 'SulfurOperator', 'MercuryOperator',
    'SaltOperator', 'TriaPrimaSystem',
    
    # Planetary
    'Planet', 'PlanetaryMatrices', 'PlanetaryOperator',
    'PlanetarySystem', 'MetallicTransformation',
    
    # Zodiac
    'ZodiacSign', 'AlchemicalOperation', 'ZodiacMatrices',
    'ZodiacOperator', 'ZodiacSystem', 'MagnumOpus',
    
    # Stone
    'WorkStage', 'PhilosophersStone', 'StoneFinder',
    'StabilityAnalyzer', 'AlchemicalSystem',
    
    # Validation
    'validate_math_of_alchemy',
]


# =============================================================================
# UNIFIED CONSTANTS
# =============================================================================

SYSTEM_CONSTANTS = {
    # Dimensions
    "elements": 4,
    "qualities": 2,
    "principles": 3,
    "planets": 7,
    "zodiac_signs": 12,
    "operations": 12,
    "work_stages": 4,
    
    # Element to Quality Matrix
    "Q_matrix": [
        [+1, +1, -1, -1],  # Heat row
        [-1, +1, +1, -1],  # Moisture row
    ],
    
    # Aristotelian Square coordinates
    "element_coords": {
        "Fire": (+1, -1),   # Hot & Dry
        "Air": (+1, +1),    # Hot & Moist
        "Water": (-1, +1),  # Cold & Moist
        "Earth": (-1, -1),  # Cold & Dry
    },
}


# =============================================================================
# VALIDATION
# =============================================================================

def validate_math_of_alchemy() -> bool:
    """Validate the complete Math of Alchemy module."""
    
    print("Validating Math of Alchemy...")
    
    # Validate sub-modules
    assert validate_elements(), "Elements validation failed"
    print("  ✓ Elements module")
    
    assert validate_tria_prima(), "Tria Prima validation failed"
    print("  ✓ Tria Prima module")
    
    assert validate_planetary(), "Planetary validation failed"
    print("  ✓ Planetary module")
    
    assert validate_zodiac(), "Zodiac validation failed"
    print("  ✓ Zodiac module")
    
    assert validate_stone(), "Stone validation failed"
    print("  ✓ Stone module")
    
    # Validate unified system
    system = AlchemicalSystem()
    
    # Test complete evolution
    initial = ElementalState(fire=0.3, air=0.3, water=0.2, earth=0.2)
    trajectory = system.evolve(initial, duration=30.0, dt=1.0)
    assert len(trajectory) > 1
    print("  ✓ System evolution")
    
    # Test Stone finding
    stone = system.find_stone(initial, max_time=100.0)
    assert stone.elemental_state.magnitude > 0
    print("  ✓ Stone finding")
    
    # Test summary
    summary = system.get_summary()
    assert "state_space" in summary
    print("  ✓ System integration")
    
    return True


# =============================================================================
# QUICK ACCESS FUNCTIONS
# =============================================================================

def create_state(fire: float = 0.25, air: float = 0.25,
                 water: float = 0.25, earth: float = 0.25) -> ElementalState:
    """Create an elemental state."""
    return ElementalState(fire=fire, air=air, water=water, earth=earth)


def create_system() -> AlchemicalSystem:
    """Create a complete alchemical system."""
    return AlchemicalSystem()


def execute_great_work(initial_state: ElementalState,
                       max_cycles: int = 12) -> PhilosophersStone:
    """Execute the Great Work from an initial state."""
    system = AlchemicalSystem()
    return system.find_stone(initial_state, max_time=max_cycles * 365.0)


# =============================================================================
# MODULE INFO
# =============================================================================

def get_module_info() -> dict:
    """Get module information."""
    return {
        "name": "Math of Alchemy",
        "version": __version__,
        "description": "Alchemy as a Complete Calculus of Archetypal Transformation",
        "modules": ["elements", "tria_prima", "planetary", "zodiac", "stone"],
        "constants": SYSTEM_CONSTANTS,
        "formula": "A = (S, O, D)",
    }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("THE MATH OF ALCHEMY")
    print("=" * 60)
    
    # Validate
    assert validate_math_of_alchemy()
    print("\n✓ All modules validated successfully!")
    
    # Demo
    print("\n" + "=" * 60)
    print("DEMONSTRATION")
    print("=" * 60)
    
    # Create Lead-like state
    lead = create_state(fire=0.05, air=0.05, water=0.1, earth=0.8)
    print(f"\nInitial State (Lead):")
    print(f"  Fire={lead.fire.real:.3f}, Air={lead.air.real:.3f}, "
          f"Water={lead.water.real:.3f}, Earth={lead.earth.real:.3f}")
    
    # Execute Great Work
    print("\nExecuting Great Work...")
    stone = execute_great_work(lead, max_cycles=3)
    
    s = stone.elemental_state
    print(f"\nResulting Stone:")
    print(f"  Fire={s.fire.real:.3f}, Air={s.air.real:.3f}, "
          f"Water={s.water.real:.3f}, Earth={s.earth.real:.3f}")
    print(f"  Valid Stone: {stone.is_valid_stone}")
    print(f"  Stability: {stone.stability_measure():.4f}")
    
    # Module info
    print("\n" + "=" * 60)
    print("MODULE INFO")
    print("=" * 60)
    info = get_module_info()
    print(f"Name: {info['name']}")
    print(f"Version: {info['version']}")
    print(f"Formula: {info['formula']}")
    print(f"Modules: {', '.join(info['modules'])}")
