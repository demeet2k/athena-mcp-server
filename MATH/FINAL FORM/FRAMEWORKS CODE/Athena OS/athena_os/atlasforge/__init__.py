"""
ATHENA OS - AtlasForge
======================
A Proof-Carrying Recipe Compiler for Chart-Rewritten Constraint Systems

From AtlasForge.docx:

AtlasForge treats a "result" not as an ephemeral number or transient
program output, but as a replayable, verifiable, content-addressed 
object—a Recipe that:

(i)   Specifies the object by explicit constraints over explicit domains
(ii)  Records the exact construction plan used to produce witnesses
(iii) Carries a machine-checkable ProofPack of typed certificates
(iv)  Admits deterministic replay under an explicit environment contract

PIPELINE:
    parse → normalize → plan → solve → certify → store → verify

KEY PRINCIPLES:
    - Separation of construction (expensive) and verification (bounded)
    - Content-addressed artifacts for reproducibility
    - Verifier-gated promotion
    - DAG compositionality
    - Generator-first storage

CRYSTAL ADDRESS MODEL:
    4-ary addressing α ∈ D₄⁴ with fixed semantics
    Quadrants: Specification / Symmetry / Guarantees / Engineering

COMPONENTS:
    - Domains: intervals, unions, graphs, manifolds
    - Constraints: roots, fixed points, lattice families
    - Recipes: proof-carrying artifacts
    - Registry: content-addressed DAG store
    - Blueprint: DSL for specifications
    - Verifier: certificate validation kernel
"""

from __future__ import annotations

# Domains
from .domains import (
    DomainKind,
    BoundaryType,
    Interval,
    UnionDomain,
    GraphDomain,
    ManifoldDomain,
    Domain,
    validate_domains,
)

# Constraints
from .constraints import (
    ConstraintType,
    ObligationType,
    Expression,
    Constraint,
    RootConstraint,
    FixedPointConstraint,
    LatticeConstraint,
    EqualityConstraint,
    ConstraintIR,
    ConstraintCompiler,
    validate_constraints,
)

# Recipes
from .recipes import (
    CertificateType,
    CertificateLevel,
    Certificate,
    ProofPack,
    SolveStrategy,
    SolvePlan,
    ReplayStep,
    ReplayLog,
    RecipeOutput,
    Recipe,
    RecipeBuilder,
    validate_recipes,
)

# Registry
from .registry import (
    VerificationStatus,
    IndexKeys,
    RegistryEntry,
    DependencyGraph,
    Registry,
    VerifiedCorpus,
    validate_registry,
)

# Crystal Address
from .crystal import (
    Quadrant,
    CrystalAddress,
    CrystalIndex,
    TokenType,
    Token,
    DomainSpec,
    ChartSpec,
    ConstraintSpec,
    SolveSpec,
    CertifySpec,
    OutputSpec,
    Blueprint,
    BlueprintParser,
    validate_crystal,
)

# Verification
from .verify import (
    TruthProfile,
    VerificationResult,
    VerificationItem,
    VerificationReport,
    Validator,
    CorridorValidator,
    EnclosureValidator,
    SignChangeValidator,
    ReplayValidator,
    VerifierKernel,
    SolveVerifyPipeline,
    validate_verify,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_atlasforge() -> bool:
    """Validate complete AtlasForge module."""
    assert validate_domains()
    assert validate_constraints()
    assert validate_recipes()
    assert validate_registry()
    assert validate_crystal()
    assert validate_verify()
    return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def forge_root(name: str, 
               expr: Expression,
               a: float, b: float) -> Tuple[Recipe, VerificationReport]:
    """
    Complete pipeline: forge a root constraint.
    
    Returns (recipe, report).
    """
    constraint = RootConstraint(
        name=name,
        expression=expr,
        domain=Domain.interval(a, b)
    )
    
    pipeline = SolveVerifyPipeline()
    return pipeline.run(constraint, a, b)


def create_forge_registry() -> Registry:
    """Create new AtlasForge registry."""
    return Registry()


def parse_blueprint(source: str) -> Blueprint:
    """Parse blueprint from source."""
    return BlueprintParser.from_string(source)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Domains
    "DomainKind", "BoundaryType", "Interval", "UnionDomain",
    "GraphDomain", "ManifoldDomain", "Domain",
    
    # Constraints
    "ConstraintType", "ObligationType", "Expression", "Constraint",
    "RootConstraint", "FixedPointConstraint", "LatticeConstraint",
    "EqualityConstraint", "ConstraintIR", "ConstraintCompiler",
    
    # Recipes
    "CertificateType", "CertificateLevel", "Certificate", "ProofPack",
    "SolveStrategy", "SolvePlan", "ReplayStep", "ReplayLog",
    "RecipeOutput", "Recipe", "RecipeBuilder",
    
    # Registry
    "VerificationStatus", "IndexKeys", "RegistryEntry",
    "DependencyGraph", "Registry", "VerifiedCorpus",
    
    # Crystal
    "Quadrant", "CrystalAddress", "CrystalIndex",
    "Blueprint", "BlueprintParser",
    
    # Verification
    "TruthProfile", "VerificationResult", "VerificationReport",
    "Validator", "VerifierKernel", "SolveVerifyPipeline",
    
    # Convenience
    "forge_root", "create_forge_registry", "parse_blueprint",
    
    # Validation
    "validate_atlasforge",
]

__version__ = "1.0.0"
__module_name__ = "atlasforge"


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - AtlasForge")
    print("Proof-Carrying Recipe Compiler")
    print("=" * 60)
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_atlasforge():
        print("✓ All components validated")
    
    print("\n--- AtlasForge Summary ---")
    
    print("\n1. DOMAIN OBJECTS:")
    print("   Interval, Union, Graph, Manifold")
    print("   Structure: topology, metric, differential")
    
    print("\n2. CONSTRAINT SYSTEMS:")
    print("   Root: H(x) = 0")
    print("   Fixed Point: x = F(x)")
    print("   Lattice: T(x_k) = θ + kΔ")
    
    print("\n3. RECIPES:")
    print("   Content-addressed artifacts")
    print("   ProofPacks with certificates")
    print("   Replay logs for reproducibility")
    
    print("\n4. REGISTRY:")
    print("   DAG-based artifact store")
    print("   Verifier-gated promotion")
    print("   Dependency tracking")
    
    print("\n5. CRYSTAL ADDRESS:")
    print("   4-ary addressing α ∈ D₄⁴")
    print("   Quadrants: Spec/Symmetry/Guarantees/Engineering")
    
    print("\n6. VERIFICATION:")
    print("   Truth profiles: Explore/Validate/Prove")
    print("   Certificate validation")
    print("   Corridor/Enclosure checking")
    
    # Demo
    print("\n--- Demo: Forge √2 ---")
    
    x = Expression.variable("x")
    expr = Expression.sub(
        Expression.mul(x, x),
        Expression.constant(2.0)
    )
    
    recipe, report = forge_root("sqrt2", expr, 1.0, 2.0)
    
    print(f"\nRecipe ID: {recipe.recipe_id}")
    print(f"Solution: {recipe.output.value:.10f}")
    print(f"Verified: {report.passed}")
    print(f"Certificates: {len(recipe.proofpack.certificates)}")
    print(f"Duration: {report.duration_ms:.2f}ms")
