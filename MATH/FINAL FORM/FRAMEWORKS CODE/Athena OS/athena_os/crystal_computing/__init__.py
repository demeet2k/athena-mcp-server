"""
ATHENA OS - Crystal Computing Framework
========================================
Quad-Polar, κ-Conserving Computational Framework

From CRYSTAL_COMPUTING_FRAMEWORK.docx:

ABSTRACT:
    Crystal Computing treats every algorithm as a path through a fixed
    1024-cell meta-crystal of canonical operations. Each cell is indexed by:
    
    - Constant (C ∈ {π, e, i, φ})
    - Shape (S ∈ {Square, Flower, Cloud, Fractal})  
    - Element (E ∈ {Earth, Water, Air, Fire})
    - Level (L ∈ {L0, L1, L2, L3})
    - Pole (P ∈ {Aether, Anti-Aether, Inner-Shadow, Outer-Shadow})

ONTOLOGY:
    κ-conserving computational universe
    Reality = evolving κ-fields on information manifolds
    κ = coherence, capacity, computational value

AETHERIC STATES:
    Decorated Hilbert spaces or κ-fields
    Primal/anti-primal magnitudes
    Inner/outer phases
    Fractal scale depth
    Shadow links (entanglement)

LEGAL COMPUTATIONS:
    κ-conserving flows of Aetheric states
    Operators from Aether and Inner-Shadow sectors
    Anti-Aether and Outer-Shadow = guardrails/diagnostics

META-IR:
    Crystal Computing = substrate-agnostic meta-IR
    QHC, classical, hybrid = backend realizations
"""

from __future__ import annotations

# Lattice (1024-cell meta-crystal)
from .lattice import (
    # Enums
    Constant, Shape, Element, Level, Pole,
    
    # Classes
    CrystalCell,
    CrystalAdjacency,
    MetaCrystal,
    
    # Validation
    validate_lattice,
)

# Kappa (κ-fields and conservation)
from .kappa import (
    # Classes
    KappaField,
    KappaMass, KappaMetrics,
    Texture,
    KappaBudget,
    KappaFlow, KappaFlowGraph,
    
    # Enums
    ConservationType,
    
    # Classes
    ConservationLaw,
    
    # Validation
    validate_kappa,
)

# States (Aetheric states)
from .states import (
    # Enums
    GeometryType,
    
    # Classes
    Geometry, VectorGeometry, GraphGeometry, GridGeometry,
    FieldData,
    AethericState,
    StateEnsemble,
    AethericStateSpace,
    
    # Validation
    validate_states,
)

# Operators (crystal cell operators)
from .operators import (
    # Enums
    KappaBehavior,
    
    # Classes
    KappaSpec, CostModel,
    CrystalOperator,
    IdentityOperator, PhaseOperator, ScaleOperator,
    ExponentialOperator, HadamardOperator, ProjectionOperator,
    ComposedOperator,
    OperatorRegistry, OperatorFactory,
    
    # Validation
    validate_operators,
)

# Programs (paths through crystal)
from .programs import (
    # Classes
    ProgramStep,
    CrystalProgram,
    ProgramBuilder,
    PathAnalysis,
    ProgramLibrary,
    
    # Validation
    validate_programs,
)

# Runtime
from .runtime import (
    # Classes
    SubstrateBackend, VectorBackend, GraphBackend,
    ExecutionContext,
    CrystalRuntime,
    
    # Functions
    get_runtime, reset_runtime,
    
    # Validation
    validate_runtime,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_crystal_computing() -> bool:
    """Validate complete Crystal Computing module."""
    assert validate_lattice()
    assert validate_kappa()
    assert validate_states()
    assert validate_operators()
    assert validate_programs()
    assert validate_runtime()
    return True


# =============================================================================
# CONVENIENCE FACTORIES
# =============================================================================

def create_meta_crystal() -> MetaCrystal:
    """Create a fresh 1024-cell meta-crystal."""
    return MetaCrystal()


def create_aetheric_state(dimension: int, state_type: str = "vacuum") -> AethericState:
    """Create an Aetheric state."""
    if state_type == "vacuum":
        return AethericState.vacuum(dimension)
    elif state_type == "superposition":
        return AethericState.superposition(dimension)
    else:
        return AethericState.vacuum(dimension)


def create_program(name: str = "program") -> ProgramBuilder:
    """Create a program builder."""
    return ProgramBuilder().named(name)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Lattice
    "Constant", "Shape", "Element", "Level", "Pole",
    "CrystalCell", "CrystalAdjacency", "MetaCrystal",
    
    # Kappa
    "KappaField", "KappaMass", "KappaMetrics", "Texture",
    "KappaBudget", "KappaFlow", "KappaFlowGraph",
    "ConservationType", "ConservationLaw",
    
    # States
    "GeometryType",
    "Geometry", "VectorGeometry", "GraphGeometry", "GridGeometry",
    "FieldData", "AethericState", "StateEnsemble", "AethericStateSpace",
    
    # Operators
    "KappaBehavior", "KappaSpec", "CostModel",
    "CrystalOperator",
    "IdentityOperator", "PhaseOperator", "ScaleOperator",
    "ExponentialOperator", "HadamardOperator", "ProjectionOperator",
    "ComposedOperator",
    "OperatorRegistry", "OperatorFactory",
    
    # Programs
    "ProgramStep", "CrystalProgram", "ProgramBuilder",
    "PathAnalysis", "ProgramLibrary",
    
    # Runtime
    "SubstrateBackend", "VectorBackend", "GraphBackend",
    "ExecutionContext", "CrystalRuntime",
    "get_runtime", "reset_runtime",
    
    # Factories
    "create_meta_crystal", "create_aetheric_state", "create_program",
    
    # Validation
    "validate_crystal_computing",
]

__version__ = "1.0.0"
__module_name__ = "crystal_computing"


if __name__ == "__main__":
    print("=== ATHENA OS Crystal Computing Framework ===")
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_crystal_computing():
        print("✓ All components validated")
    
    print("\n--- Module Summary ---")
    
    crystal = create_meta_crystal()
    summary = crystal.summary()
    
    print(f"\n1024-Cell Meta-Crystal (4⁵ = {summary['total_cells']})")
    print(f"\nAxes:")
    print(f"  C (Constants): {summary['axes']['constants']} - π/e/i/φ")
    print(f"  S (Shapes): {summary['axes']['shapes']} - □/❀/☁/✶")
    print(f"  E (Elements): {summary['axes']['elements']} - ??/??/??/??")
    print(f"  L (Levels): {summary['axes']['levels']}")
    print(f"  P (Poles): {summary['axes']['poles']} - Æ/∄/⊂/∞")
    
    print(f"\nStructure:")
    print(f"  Dimension: {summary['dimension']}")
    print(f"  Degree: {summary['degree']} neighbors per cell")
    print(f"  Cells per pole: {summary['cells_per_pole']}")
    
    print("\nκ-Conservation:")
    print("  Aetheric operators preserve total κ")
    print("  Anti-Aether = forbidden operations")
    print("  Texture T = α·H + β·D + γ·λ")
    
    print("\nPrograms as Paths:")
    print("  Crystal Program = sequence of (cell, operator) pairs")
    print("  κ-flows tracked along paths")
    print("  Safety = staying in Aether/Inner-Shadow poles")
    
    # Demo
    print("\n--- Demo ---")
    
    state = create_aetheric_state(4, "vacuum")
    print(f"\nVacuum state |0⟩: dim={state.dimension}, κ={state.total_kappa}")
    
    builder = create_program("demo")
    program = (builder
               .apply(HadamardOperator(0))
               .apply(PhaseOperator(0.5))
               .build())
    
    runtime = get_runtime()
    result = runtime.execute_program(program, state)
    
    print(f"\nProgram '{program.name}' executed:")
    print(f"  Steps: {program.length}")
    print(f"  Final κ: {result.total_kappa:.4f}")
    print(f"  Conserving: {program.is_conserving()}")
