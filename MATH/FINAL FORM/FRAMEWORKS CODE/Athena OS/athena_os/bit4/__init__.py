"""
ATHENA OS - BIT4
================
The Four-State Completion of the Bit

BIT4 is a mathematically rigorous completion of the classical bit that
makes the "shadow pole" of binary computation explicit, first-class,
and computable.

CARRIER SET:
    B₄ = P({0,1}) = {⊥, 0, 1, ⊤}
    
    ⊥ = ∅      (gap/unknown/no evidence)
    0 = {0}    (only false supported)
    1 = {1}    (only true supported)  
    ⊤ = {0,1}  (conflict/both supported)

BILATTICE STRUCTURE:
    Two orthogonal partial orders:
    
    Knowledge order ≤_k (information inclusion):
        ⊥ ≤_k 0, 1 ≤_k ⊤
        
    Truth order ≤_t (truth increases):
        0 ≤_t ⊥, ⊤ ≤_t 1

SYMMETRY GROUP:
    Klein four group V₄ = {id, ¬, κ, ~}
    
    ¬ : truth-negation (bit-flip)
    κ : conflation (shadow swap)
    ~ : set complement

DATAFLOW SEMANTICS:
    Transfer function F: B₄ⁿ → B₄ⁿ
    Stable meaning: x* = lfp(F)
    
BOUNDARY COLLAPSE:
    π: B₄ → {0,1} ∪ {err}
    
    Conservative, optimistic, pessimistic, randomized,
    constraint-guided, proof-carrying policies.
"""

from __future__ import annotations

# Carrier set and encodings
from .carrier import (
    B4,
    TwoRail,
    OneHot,
    B4Vector,
    two_rail_to_one_hot,
    one_hot_to_two_rail,
    validate_carrier,
)

# Orders and bilattice structure  
from .orders import (
    # Comparisons
    leq_k, lt_k,
    leq_t, lt_t,
    comparable_k, comparable_t,
    
    # Lattice operations
    join_k, meet_k,
    join_t, meet_t,
    oplus_k, otimes_k,  # Aliases
    or_t, and_t,        # Aliases
    
    # Properties
    is_lattice_k_bounded,
    is_lattice_t_bounded,
    verify_distributivity_k,
    verify_distributivity_t,
    
    # Monotonicity
    is_monotone_k, is_monotone_t,
    is_antitone_k, is_antitone_t,
    
    # Bilattice
    Bilattice,
    
    # Tables
    print_join_k_table, print_meet_k_table,
    print_join_t_table, print_meet_t_table,
    
    validate_orders,
)

# Symmetry and Klein group
from .symmetry import (
    # Involutions
    neg, kappa, complement,
    identity,
    NOT, SWAP, COMP, ID,
    
    # Klein group
    KleinElement,
    KLEIN_TABLE,
    klein_compose,
    klein_inverse,
    klein_apply,
    
    # Dihedral
    DihedralElement,
    
    # Automorphisms
    is_k_automorphism, is_k_anti_automorphism,
    is_t_automorphism, is_t_anti_automorphism,
    classify_symmetry,
    
    # Orbits
    orbit_under_klein,
    orbits_klein,
    
    # Tables
    print_involution_table,
    print_klein_table,
    
    validate_symmetry,
)

# Gates and circuits
from .gates import (
    # Lift schemas
    LiftSchema,
    
    # Boolean gates
    bool_not, bool_and, bool_or, bool_xor,
    bool_nand, bool_nor, bool_impl,
    
    # Rail-dual lifting
    lift_unary_rd, lift_binary_rd,
    b4_not_rd, b4_and_rd, b4_or_rd,
    b4_xor_rd, b4_nand_rd, b4_nor_rd,
    
    # Support-based lifting
    lift_unary_support, lift_binary_support,
    b4_and_sup, b4_or_sup, b4_not_sup,
    
    # Gate specifications
    GateSpec,
    GateLibrary,
    
    # Circuits
    Wire, GateInstance, Circuit,
    
    validate_gates,
)

# Dataflow and fixed points
from .dataflow import (
    TransferFunction,
    FixpointMode,
    FixpointResult,
    
    # Iteration methods
    kleene_iteration,
    greatest_fixpoint,
    widening_iteration,
    widen_k, narrow_k,
    
    # Solvers
    WorklistSolver,
    StratifiedSolver,
    tarjan_scc,
    
    # Abstract interpretation
    AbstractDomain,
    
    validate_dataflow,
)

# Collapse policies
from .collapse import (
    CollapseResult,
    CollapseOutcome,
    CollapsePolicy,
    
    # Policy functions
    collapse_conservative,
    collapse_optimistic,
    collapse_pessimistic,
    collapse_random,
    collapse_default_false,
    collapse_default_true,
    collapse_strict,
    
    COLLAPSE_POLICIES,
    apply_policy,
    
    # Constraint-guided
    Constraint,
    ConstraintSet,
    collapse_guided,
    
    # Proof-carrying
    CollapseCertificate,
    ProofCarryingCollapse,
    
    # Audit
    CollapseAuditRecord,
    CollapseAuditLog,
    
    validate_collapse,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_bit4() -> bool:
    """Validate complete BIT4 module."""
    assert validate_carrier()
    assert validate_orders()
    assert validate_symmetry()
    assert validate_gates()
    assert validate_dataflow()
    assert validate_collapse()
    return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def merge(x: B4, y: B4) -> B4:
    """Merge information from two sources (⊕_k)."""
    return join_k(x, y)


def refine(x: B4, y: B4) -> B4:
    """Refine to common information (⊗_k)."""
    return meet_k(x, y)


def flip(x: B4) -> B4:
    """Truth-negation (¬)."""
    return neg(x)


def shadow_swap(x: B4) -> B4:
    """Conflation (κ): swap ⊥ ↔ ⊤."""
    return kappa(x)


def from_bool(b: bool) -> B4:
    """Embed boolean into B₄."""
    return B4.from_bool(b)


def to_bool(x: B4, policy: CollapsePolicy = CollapsePolicy.CONSERVATIVE) -> bool:
    """Collapse B₄ to boolean using policy."""
    outcome = apply_policy(x, policy)
    if outcome.is_error:
        raise ValueError(f"Cannot collapse {x.glyph} to boolean with {policy.value} policy")
    return outcome.to_bool()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core types
    "B4", "TwoRail", "OneHot", "B4Vector",
    
    # Orders
    "leq_k", "leq_t", "lt_k", "lt_t",
    "join_k", "meet_k", "join_t", "meet_t",
    "oplus_k", "otimes_k", "or_t", "and_t",
    "Bilattice",
    
    # Symmetry
    "neg", "kappa", "complement", "identity",
    "KleinElement", "klein_compose", "klein_apply",
    
    # Gates
    "LiftSchema", "GateSpec", "GateLibrary",
    "Circuit", "Wire", "GateInstance",
    
    # Dataflow
    "TransferFunction", "FixpointMode", "FixpointResult",
    "kleene_iteration", "greatest_fixpoint",
    "WorklistSolver", "StratifiedSolver",
    
    # Collapse
    "CollapseResult", "CollapseOutcome", "CollapsePolicy",
    "apply_policy", "collapse_conservative",
    "ProofCarryingCollapse", "CollapseAuditLog",
    
    # Convenience
    "merge", "refine", "flip", "shadow_swap",
    "from_bool", "to_bool",
    
    # Validation
    "validate_bit4",
]

__version__ = "1.0.0"
__module_name__ = "bit4"


if __name__ == "__main__":
    print("=" * 60)
    print("ATHENA OS - BIT4")
    print("The Four-State Completion of the Bit")
    print("=" * 60)
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_bit4():
        print("✓ All components validated")
    
    print("\n--- BIT4 Summary ---")
    
    print("\n1. CARRIER SET B₄ = {⊥, 0, 1, ⊤}")
    for v in [B4.BOT, B4.ZERO, B4.ONE, B4.TOP]:
        enc = TwoRail.encode(v)
        print(f"   {v.glyph}: support={set(v.support)}, rail={enc}")
    
    print("\n2. BILATTICE ORDERS")
    print("   Knowledge: ⊥ ≤_k {0,1} ≤_k ⊤")
    print("   Truth: 0 ≤_t {⊥,⊤} ≤_t 1")
    
    print("\n3. KLEIN GROUP V₄")
    print("   ¬: bit-flip (0↔1, ⊥→⊥, ⊤→⊤)")
    print("   κ: shadow swap (⊥↔⊤, 0→0, 1→1)")
    print("   ~: complement (¬∘κ)")
    
    print("\n4. DATAFLOW")
    print("   Transfer: F: B₄ⁿ → B₄ⁿ")
    print("   Fixed point: x* = lfp(F)")
    
    print("\n5. COLLAPSE POLICIES")
    for policy in CollapsePolicy:
        print(f"   {policy.value}")
    
    # Demo
    print("\n--- Demo ---")
    
    # Merge conflicting information
    a = B4.ZERO  # Evidence for false
    b = B4.ONE   # Evidence for true
    merged = merge(a, b)
    print(f"\nMerge: {a.glyph} ⊕_k {b.glyph} = {merged.glyph} (conflict!)")
    
    # Collapse with different policies
    print(f"\nCollapse {merged.glyph}:")
    print(f"  Conservative: {apply_policy(merged, CollapsePolicy.CONSERVATIVE).result.name}")
    print(f"  Optimistic: {apply_policy(merged, CollapsePolicy.OPTIMISTIC).result.name}")
    print(f"  Pessimistic: {apply_policy(merged, CollapsePolicy.PESSIMISTIC).result.name}")
