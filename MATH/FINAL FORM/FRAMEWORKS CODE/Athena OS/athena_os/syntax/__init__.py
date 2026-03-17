"""
ATHENA OS - SYNTAX
==================
The Complete Syntax Algebra

A many-sorted partial algebra of programs, failures, metaprograms,
and obligations organized by a 4^4 coordinate atlas.

From SYNTAX.docx:

CORE STRUCTURE:
    ?? = (S, A, I, O; Ω)
    
    S: SYNTAX - Executable artifacts
    A: ANTI-SYNTAX - Collapse/erasure operators  
    I: IN-SYNTAX - Metatransformers (code about code)
    O: OUT-SYNTAX - Obligations and context

COORDINATE SYSTEM:
    4^4 = 256 cells indexed by ⟨P, L, D, R⟩:
    
    P: Pole (S/A/I/O)
    L: Lens (B12/B13/B14/B_outer)
    D: Direction (Spin/Rev/Eq/Drift)
    R: Representation (Txt/Str/Mid/Obs)

ZERO POINT (??_0):
    - Collapse projections κ_X : X ⇀ ??_0
    - Seed generation maps σ_X : ??_0 ⇀ X
    
REPRESENTATION TOWER:
    Txt → Str → Mid → Obs (SPIN)
    Txt ← Str ← Mid ← Obs (REVERSE-SPIN)

SATISFACTION RELATION:
    ⊨ ⊆ (S × W) × O
    "program p in world w satisfies obligation φ"
"""

from __future__ import annotations

# Core types
from .core import (
    # Enums
    Pole,
    RepLevel,
    Direction,
    LensFamily,
    CollapseKind,
    CollapsePhase,
    
    # Artifacts
    Artifact,
    SyntaxArtifact,
    TextArtifact,
    StructArtifact,
    MidArtifact,
    AntiArtifact,
    InArtifact,
    Transform,
    OutArtifact,
    Contract,
    Invariant,
    Policy,
    
    # World and Observations
    WorldState,
    Observation,
    BOTTOM,
    ExecutionResult,
    
    # Provenance
    Provenance,
    
    # Algebra
    SyntaxAlgebra,
    
    # Validation
    validate_core,
)

# Coordinates (4^4 crystal index)
from .coordinates import (
    CrystalCoord,
    CellContent,
    CrystalIndex,
    
    # Utilities
    all_coordinates,
    coordinates_for_artifact,
    dual_pairs,
    
    # Validation
    validate_coordinates,
)

# Zero Point (??_0)
from .zero_point import (
    # Severity and recoverability
    ZSeverity,
    ZRecoverability,
    
    # Z-Record
    ZRecord,
    
    # Collapse projections κ
    CollapseProjection,
    
    # Seed generation σ
    SeedConstraints,
    SeedGenerator,
    
    # Zero Chamber
    ZeroChamber,
    get_zero_chamber,
    reset_zero_chamber,
    
    # Validation
    validate_zero_point,
)

# Representation Tower
from .representation import (
    # Transform result
    TransformResult,
    
    # Base transform
    RepTransform,
    
    # SPIN transforms
    Tokenizer,
    Parser,
    Compiler,
    Executor,
    
    # REVERSE-SPIN transforms
    Decompiler,
    Unparser,
    
    # Tower
    RepresentationTower,
    
    # Validation
    validate_representation,
)

# Obligations
from .obligations import (
    # Satisfaction
    SatisfactionStatus,
    SatisfactionResult,
    ObligationChecker,
    
    # Checkers
    PreconditionChecker,
    PostconditionChecker,
    InvariantChecker,
    SatisfactionChecker,
    
    # Drift
    DriftWitness,
    DriftDetector,
    
    # Refinement
    program_refines,
    obligation_refines,
    
    # Validation
    validate_obligations,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_syntax() -> bool:
    """Validate complete SYNTAX module."""
    assert validate_core()
    assert validate_coordinates()
    assert validate_zero_point()
    assert validate_representation()
    assert validate_obligations()
    return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_algebra() -> SyntaxAlgebra:
    """Create a new syntax algebra instance."""
    return SyntaxAlgebra()


def create_tower() -> RepresentationTower:
    """Create a new representation tower."""
    return RepresentationTower()


def create_index() -> CrystalIndex:
    """Create a new 256-cell crystal index."""
    return CrystalIndex()


def spin(artifact: SyntaxArtifact, target: RepLevel) -> TransformResult:
    """Apply SPIN transforms to artifact."""
    tower = create_tower()
    return tower.spin(artifact, target)


def reverse_spin(artifact: SyntaxArtifact, target: RepLevel) -> TransformResult:
    """Apply REVERSE-SPIN transforms to artifact."""
    tower = create_tower()
    return tower.reverse_spin(artifact, target)


def collapse(artifact: Artifact, 
             coord: CrystalCoord,
             phase: CollapsePhase,
             kind: CollapseKind,
             message: str = "") -> ZRecord:
    """Collapse artifact to Z-record."""
    chamber = get_zero_chamber()
    return chamber.collapse(artifact, coord, phase, kind, message)


def check_satisfaction(program: SyntaxArtifact,
                       obligation: OutArtifact,
                       world: WorldState,
                       result: ExecutionResult = None) -> SatisfactionResult:
    """Check if program satisfies obligation."""
    checker = SatisfactionChecker()
    return checker.check(program, obligation, world, result)


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstrate SYNTAX module capabilities."""
    print("=" * 70)
    print("SYNTAX ALGEBRA DEMONSTRATION")
    print("=" * 70)
    
    # 1. Create source artifact
    print("\n1. SOURCE ARTIFACT")
    source = TextArtifact(
        content="x + 1",
        pole=Pole.S,
        rep_level=RepLevel.TXT
    )
    print(f"   Source: '{source.content}'")
    print(f"   ID: {source.artifact_id}")
    print(f"   Level: {source.rep_level.symbol}")
    
    # 2. Demonstrate representation tower
    print("\n2. REPRESENTATION TOWER (SPIN)")
    tower = create_tower()
    
    # Tokenize
    tok_result = tower.tokenizer.transform(source)
    if tok_result.success:
        print(f"   Txt → Str: {tok_result.artifact.content[:3]}...")
        
        # Parse
        parse_result = tower.parser.transform(tok_result.artifact)
        if parse_result.success:
            # Compile
            compile_result = tower.compiler.transform(parse_result.artifact)
            if compile_result.success:
                print(f"   Str → Mid: {compile_result.artifact.content}")
    
    # 3. Demonstrate crystal coordinates
    print("\n3. CRYSTAL COORDINATES")
    coord = CrystalCoord(
        pole=Pole.S,
        lens=LensFamily.B12,
        direction=Direction.SPIN,
        rep_level=RepLevel.TXT
    )
    print(f"   Coordinate: {coord}")
    print(f"   Index: {coord.index}")
    print(f"   Dual: {coord.dual()}")
    
    # 4. Demonstrate crystal index
    print("\n4. CRYSTAL INDEX")
    index = create_index()
    index.place_artifact(source.artifact_id, coord)
    print(f"   Total cells: {len(index)}")
    print(f"   Populated: {index.populated_count}")
    
    # 5. Demonstrate obligations
    print("\n5. OBLIGATION CHECKING")
    world = WorldState(state_id="demo", variables={"x": 5})
    contract = Contract(
        description="x must be positive",
        preconditions=["x > 0"],
        postconditions=["result >= x"],
        pole=Pole.O,
        rep_level=RepLevel.OBS
    )
    
    result = check_satisfaction(source, contract, world)
    print(f"   Contract: {contract.description}")
    print(f"   Status: {result.status.value}")
    
    # 6. Demonstrate Zero Point
    print("\n6. ZERO POINT CHAMBER")
    reset_zero_chamber()
    chamber = get_zero_chamber()
    
    # Simulate a failure
    anti = AntiArtifact(
        kind=CollapseKind.SYNTACTIC,
        phase=CollapsePhase.PARSE,
        message="Demo parse error",
        pole=Pole.A,
        rep_level=RepLevel.OBS
    )
    z_record = ZRecord.from_anti_artifact(anti, coord)
    chamber.record(z_record)
    
    stats = chamber.statistics()
    print(f"   Total Z-records: {stats['total_records']}")
    print(f"   By phase: {stats['by_phase']}")
    
    print("\n" + "=" * 70)
    print("✓ SYNTAX ALGEBRA OPERATIONAL")
    print("=" * 70)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core enums
    "Pole", "RepLevel", "Direction", "LensFamily",
    "CollapseKind", "CollapsePhase",
    
    # Artifacts
    "Artifact", "SyntaxArtifact", "TextArtifact", "StructArtifact", "MidArtifact",
    "AntiArtifact", "InArtifact", "Transform",
    "OutArtifact", "Contract", "Invariant", "Policy",
    
    # World/Observation
    "WorldState", "Observation", "BOTTOM", "ExecutionResult",
    "Provenance",
    
    # Algebra
    "SyntaxAlgebra",
    
    # Coordinates
    "CrystalCoord", "CellContent", "CrystalIndex",
    "all_coordinates", "coordinates_for_artifact", "dual_pairs",
    
    # Zero Point
    "ZSeverity", "ZRecoverability", "ZRecord",
    "CollapseProjection", "SeedConstraints", "SeedGenerator",
    "ZeroChamber", "get_zero_chamber", "reset_zero_chamber",
    
    # Representation Tower
    "TransformResult", "RepTransform",
    "Tokenizer", "Parser", "Compiler", "Executor",
    "Decompiler", "Unparser",
    "RepresentationTower",
    
    # Obligations
    "SatisfactionStatus", "SatisfactionResult", "ObligationChecker",
    "PreconditionChecker", "PostconditionChecker", "InvariantChecker",
    "SatisfactionChecker",
    "DriftWitness", "DriftDetector",
    "program_refines", "obligation_refines",
    
    # Convenience
    "create_algebra", "create_tower", "create_index",
    "spin", "reverse_spin", "collapse", "check_satisfaction",
    
    # Validation
    "validate_syntax",
]

__version__ = "1.0.0"
__module_name__ = "syntax"


if __name__ == "__main__":
    print("Validating SYNTAX module...")
    assert validate_syntax()
    print("✓ SYNTAX module validated\n")
    demo()
