"""
ATHENA OS - AETHERIC META-HYBRID CALCULUS
=========================================
The 256-Operation Crystal Framework

From Aetheric_Meta-Hybrid_Calculus.docx:

The Aetheric Meta-Hybrid Calculus provides a unified framework for
organizing mathematical operations across four fundamental constants
(π, e, i, φ), four shapes (Square, Flower, Cloud, Fractal), four
elements (Earth, Water, Fire, Air), and four Aether poles (A, Ā, in, out).

STRUCTURE:
    256 = 4 × 4 × 4 × 4 operation crystal
    1024 = 256 × 4 super-crystal at dimension N+1

KEY COMPONENTS:
    - Fundamental Constants: π, e, i, φ
    - Shapes/Operators: D (discrete), Ω (continuous), Σ (stochastic), R (recursive)
    - Elements: Earth, Water, Fire, Air
    - Aether Poles: Primal, Adjoint, Inner, Outer

META-HYBRID EQUATION:
    ℋ_c Ψ_c = 0
    
    Compatibility among discrete, continuous, stochastic, and recursive
    dynamics under Aetheric coupling.

TEXTURE FUNCTIONAL:
    T(ψ) measures information distribution and stability.
    Plays the role of thermodynamics for the operation crystal.
"""

from __future__ import annotations

# Core types
from .core import (
    # Enums
    FundamentalConstant,
    Shape,
    Element,
    AetherPole,
    
    # Coordinates
    OperationCoord,
    OperationCell,
    OperationCrystal,
    
    # Couplings
    AethericCoupling,
    
    # States
    HybridState,
    TextureFunctional,
    
    # Validation
    validate_aetheric_core,
)

# Operators
from .operators import (
    # Base
    SectorOperator,
    
    # Sector operators
    DiscreteOperator,
    ContinuousOperator, 
    StochasticOperator,
    RecursiveOperator,
    
    # Aetheric decomposition
    AethericSectorOperator,
    
    # Meta-hybrid operator
    MetaHybridOperator,
    
    # Full system
    FullHybridSystem,
    
    # Dimensional operations
    DimensionalLift,
    
    # Validation
    validate_operators,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_aetheric() -> bool:
    """Validate complete Aetheric module."""
    assert validate_aetheric_core()
    assert validate_operators()
    return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_crystal() -> OperationCrystal:
    """Create a new 256-operation crystal."""
    return OperationCrystal()


def create_operator(constant: FundamentalConstant,
                    N: int = 8, M: int = 16, L: int = 4) -> MetaHybridOperator:
    """Create meta-hybrid operator for a constant."""
    return MetaHybridOperator(constant, N, M, L)


def create_full_system(N: int = 4, M: int = 8, L: int = 2) -> FullHybridSystem:
    """Create full coupled hybrid system."""
    return FullHybridSystem(N, M, L)


def create_state(constant: FundamentalConstant,
                 N: int = 8, M: int = 16, L: int = 4) -> HybridState:
    """Create hybrid state for a constant."""
    return HybridState(constant, N, M, L)


def compute_texture(state: HybridState) -> float:
    """Compute texture functional for a state."""
    T = TextureFunctional()
    return T.compute(state)


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstrate Aetheric Meta-Hybrid Calculus capabilities."""
    print("=" * 70)
    print("AETHERIC META-HYBRID CALCULUS DEMONSTRATION")
    print("=" * 70)
    
    # 1. Operation Crystal
    print("\n1. OPERATION CRYSTAL (256 cells)")
    crystal = create_crystal()
    summary = crystal.summary()
    print(f"   Total operations: {summary['total_cells']}")
    print(f"   Allowed: {summary['allowed_operations']}")
    print(f"   Anti-operations: {summary['anti_operations']}")
    
    # 2. Sample cell
    print("\n2. SAMPLE OPERATION CELL")
    coord = OperationCoord(
        FundamentalConstant.PI,
        Shape.FLOWER,
        Element.FIRE,
        AetherPole.PRIMAL
    )
    cell = crystal[coord]
    print(f"   Coordinate: {coord}")
    print(f"   Index: {coord.index}")
    print(f"   Coupling: {cell.coupling:.3f}")
    
    # 3. Meta-hybrid operator
    print("\n3. META-HYBRID OPERATOR (ℋ_π)")
    H_pi = MetaHybridOperator(FundamentalConstant.PI, N_discrete=4, M_continuous=4, L_scale=2)
    print(f"   Dimension: {H_pi.dimension}")
    evals = H_pi.eigenvalues()
    print(f"   Spectrum range: [{min(abs(evals)):.3f}, {max(abs(evals)):.3f}]")
    
    ground_val, ground_vec = H_pi.ground_state()
    print(f"   Ground state eigenvalue: {ground_val:.4f}")
    
    # 4. Full coupled system
    print("\n4. FULL HYBRID SYSTEM (ℍ_full)")
    H_full = FullHybridSystem(N_discrete=2, M_continuous=4, L_scale=2)
    print(f"   Full dimension: {H_full.dimension}")
    
    meta_consts = H_full.meta_constants(n_top=4)
    print(f"   Meta-constants (N+1):")
    for i, mc in enumerate(meta_consts):
        print(f"      λ_{i}: {mc:.4f}")
    
    # 5. Dimensional lift
    print("\n5. DIMENSIONAL LIFT (256 → 1024)")
    lift = DimensionalLift(crystal)
    super_crystal = lift.lift()
    print(f"   Super-crystal dimension: {super_crystal.shape}")
    
    # 6. Texture functional
    print("\n6. TEXTURE FUNCTIONAL")
    state = create_state(FundamentalConstant.PI, N=4, M=4, L=2)
    texture = compute_texture(state)
    print(f"   State norm: {state.norm():.4f}")
    print(f"   Texture T(ψ): {texture:.4f}")
    
    T = TextureFunctional()
    sector_tex = T.sector_texture(state)
    print(f"   By sector: {', '.join(f'{s.value}={v:.3f}' for s, v in sector_tex.items())}")
    
    print("\n" + "=" * 70)
    print("✓ AETHERIC META-HYBRID CALCULUS OPERATIONAL")
    print("=" * 70)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core enums
    "FundamentalConstant", "Shape", "Element", "AetherPole",
    
    # Crystal structures
    "OperationCoord", "OperationCell", "OperationCrystal",
    
    # Couplings
    "AethericCoupling",
    
    # States and texture
    "HybridState", "TextureFunctional",
    
    # Operators
    "SectorOperator",
    "DiscreteOperator", "ContinuousOperator", 
    "StochasticOperator", "RecursiveOperator",
    "AethericSectorOperator",
    "MetaHybridOperator",
    "FullHybridSystem",
    "DimensionalLift",
    
    # Convenience functions
    "create_crystal", "create_operator", "create_full_system",
    "create_state", "compute_texture",
    
    # Validation
    "validate_aetheric",
]

__version__ = "1.0.0"
__module_name__ = "aetheric"


if __name__ == "__main__":
    print("Validating Aetheric module...")
    assert validate_aetheric()
    print("✓ Aetheric module validated\n")
    demo()
