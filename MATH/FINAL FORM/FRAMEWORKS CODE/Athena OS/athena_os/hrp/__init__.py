"""
ATHENA OS - HOLOGRAPHIC ROTATION PROTOCOL (HRP)
================================================
Quad-Polar Framework for Mathematical Texture and Problem Solving

From Holographic_Rotation_Protocol.docx:

The Holographic Rotation Protocol is a quad-polar framework for
studying difficult mathematical and computational systems by viewing
them through four complementary elemental lenses:

    WATER (W): Continuous fields and flows
    EARTH (E): Discrete structures and algorithms  
    FIRE (F): Probability and spectra
    AIR (A): Information, compression, and fractals

CORE CONCEPTS:

1. HOLOGRAPHIC ROTATION
   - Systematic passage between four frame representations
   - Each rotation operator R_{α→β} transforms one view to another
   
2. THEORY OF TEXTURE (T)
   - Quantifies medium's resistance to global structure
   - Texture triple: (H, D, λ)
     - H: Information entropy rate
     - D: Effective/fractal dimension
     - λ: Spectral gap / mixing rate
   
3. BINDING ENERGY
   - E_bind(S): Robustness of structure S
   - Texture inequality: T_medium ≤ E_bind(S)
   
4. CANONICAL CONSTANTS
   - π, e, i, φ as "basis behaviors" across elements
   - Metallic means as generalization of φ
   
5. HARD PROBLEMS
   - Collatz, Navier-Stokes, Riemann, P vs NP
   - Each viewed as holographic object with four frames

META-PRINCIPLE:
    Global structures (loops, singularities, efficient algorithms)
    are low-entropy configurations whose survival depends on
    binding energy exceeding surrounding texture.
"""

from __future__ import annotations

# Frames
from .frames import (
    # Core types
    Element,
    StateSpaceType,
    DynamicsType,
    MeasureType,
    
    # Descriptors
    StateSpace,
    Dynamics,
    Measure,
    
    # Frame classes
    Frame,
    WaterFrame,
    EarthFrame,
    FireFrame,
    AirFrame,
    
    # Factory
    create_frame,
    
    validate_frames,
)

# Texture
from .texture import (
    # Core
    TextureTriple,
    
    # Estimators
    EntropyEstimator,
    DimensionEstimator,
    SpectralEstimator,
    
    # Functional
    TextureFunctional,
    
    # Binding and coherence
    BindingEnergy,
    CoherenceTracker,
    
    # Analyzer
    TextureAnalyzer,
    
    validate_texture,
)

# Rotation
from .rotation import (
    # Base
    RotationOperator,
    
    # Specific rotations
    WaterToEarth,
    EarthToFire,
    FireToAir,
    AirToWater,
    
    # Composition
    RotationChain,
    RotationCycle,
    
    # Factory
    get_rotation,
    
    validate_rotation,
)

# Objects
from .objects import (
    # Holographic object
    HolographicObject,
    
    # Constants
    ConstantType,
    CanonicalConstant,
    PI, E, I, PHI,
    
    # Metallic means
    MetallicMean,
    GOLDEN, SILVER, BRONZE,
    
    # Problems
    ProblemType,
    ProblemObject,
    
    # Factories
    create_constant,
    create_problem,
    create_metallic_mean,
    
    validate_objects,
)

# Protocol
from .protocol import (
    # Configuration
    ProtocolConfig,
    ProtocolResult,
    
    # Main protocol
    HolographicRotationProtocol,
    
    # Convenience functions
    create_protocol,
    run_protocol,
    analyze_problem,
    analyze_constant,
    
    validate_protocol,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_hrp() -> bool:
    """Validate complete HRP module."""
    assert validate_frames()
    assert validate_texture()
    assert validate_rotation()
    assert validate_objects()
    assert validate_protocol()
    return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def holographic_rotation(obj: HolographicObject,
                        config: ProtocolConfig = None) -> ProtocolResult:
    """
    Main entry point: Run holographic rotation protocol.
    
    Args:
        obj: Object to analyze
        config: Optional configuration
    
    Returns:
        ProtocolResult with frames, textures, and analysis
    """
    return run_protocol(obj, config)


def create_water_frame(**kwargs) -> WaterFrame:
    """Create Water frame with defaults."""
    return create_frame(Element.WATER, **kwargs)


def create_earth_frame(**kwargs) -> EarthFrame:
    """Create Earth frame with defaults."""
    return create_frame(Element.EARTH, **kwargs)


def create_fire_frame(**kwargs) -> FireFrame:
    """Create Fire frame with defaults."""
    return create_frame(Element.FIRE, **kwargs)


def create_air_frame(**kwargs) -> AirFrame:
    """Create Air frame with defaults."""
    return create_frame(Element.AIR, **kwargs)


def texture_from_sequence(sequence) -> TextureTriple:
    """Compute texture from discrete sequence."""
    import numpy as np
    analyzer = TextureAnalyzer()
    return analyzer.analyze_sequence(np.array(sequence))


def texture_from_points(points) -> TextureTriple:
    """Compute texture from point cloud."""
    import numpy as np
    analyzer = TextureAnalyzer()
    return analyzer.analyze_points(np.array(points))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Frames
    "Element", "StateSpaceType", "DynamicsType", "MeasureType",
    "StateSpace", "Dynamics", "Measure",
    "Frame", "WaterFrame", "EarthFrame", "FireFrame", "AirFrame",
    "create_frame",
    
    # Texture
    "TextureTriple",
    "EntropyEstimator", "DimensionEstimator", "SpectralEstimator",
    "TextureFunctional", "BindingEnergy", "CoherenceTracker",
    "TextureAnalyzer",
    
    # Rotation
    "RotationOperator",
    "WaterToEarth", "EarthToFire", "FireToAir", "AirToWater",
    "RotationChain", "RotationCycle",
    "get_rotation",
    
    # Objects
    "HolographicObject",
    "ConstantType", "CanonicalConstant", "PI", "E", "I", "PHI",
    "MetallicMean", "GOLDEN", "SILVER", "BRONZE",
    "ProblemType", "ProblemObject",
    "create_constant", "create_problem", "create_metallic_mean",
    
    # Protocol
    "ProtocolConfig", "ProtocolResult",
    "HolographicRotationProtocol",
    "create_protocol", "run_protocol", "analyze_problem", "analyze_constant",
    
    # Convenience
    "holographic_rotation",
    "create_water_frame", "create_earth_frame", "create_fire_frame", "create_air_frame",
    "texture_from_sequence", "texture_from_points",
    
    # Validation
    "validate_hrp",
]

__version__ = "1.0.0"
__module_name__ = "hrp"


if __name__ == "__main__":
    import numpy as np
    
    print("=" * 70)
    print("ATHENA OS - HOLOGRAPHIC ROTATION PROTOCOL (HRP)")
    print("Quad-Polar Framework for Mathematical Texture")
    print("=" * 70)
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_hrp():
        print("✓ All components validated")
    
    print("\n--- Module Overview ---")
    
    print("\n1. FOUR ELEMENTAL FRAMES")
    for elem in Element:
        print(f"   {elem.symbol} {elem.value.upper():8} - {elem.description}")
    
    print("\n2. TEXTURE TRIPLE (H, D, λ)")
    t = TextureTriple(H=1.5, D=2.0, lam=0.8)
    print(f"   Example: {t}")
    print(f"   Roughness: {t.roughness:.4f}")
    
    print("\n3. ROTATION OPERATORS")
    print("   ??→??  Water→Earth   (Discretization)")
    print("   ??→??  Earth→Fire    (Randomization)")
    print("   ??→??  Fire→Air      (Information lifting)")
    print("   ??→??  Air→Water     (Reconstruction)")
    
    print("\n4. CANONICAL CONSTANTS")
    print(f"   π = {PI.value:.6f} - {PI.manifestations[Element.WATER][:40]}...")
    print(f"   e = {E.value:.6f} - {E.manifestations[Element.WATER][:40]}...")
    print(f"   φ = {PHI.value:.6f} - {PHI.manifestations[Element.WATER][:40]}...")
    
    print("\n5. METALLIC MEANS")
    for mm in [GOLDEN, SILVER, BRONZE]:
        print(f"   φ_{mm.n} = {mm.value:.6f} ({mm.name})")
    
    print("\n6. PROBLEM OBJECTS")
    for pt in ProblemType:
        p = create_problem(pt)
        print(f"   {pt.value.upper():12} - {p.name}")
    
    # Demo analysis
    print("\n--- Demo: Collatz Analysis ---")
    config = ProtocolConfig(grid_resolution=5, verbose=True)
    result = analyze_problem(ProblemType.COLLATZ, config)
    
    print(f"\nTextures:")
    for elem, tex in result.textures.items():
        print(f"   {elem.value}: {tex}")
    
    print(f"\nInvariants:")
    for name, value in list(result.invariants.items())[:5]:
        print(f"   {name}: {value:.4f}")
    
    print("\n" + "=" * 70)
