"""
ATHENA OS - Crystal Expression Validators
==========================================
Validators for the 1024 Crystal expressions.

Each expression has associated constraints that determine:
1. For AETHER: What conditions must hold for the operation to be valid
2. For ANTI-AETHER: What violation makes the operation impossible
3. For INNER SHADOW: The information-theoretic encoding
4. For OUTER SHADOW: The boundary/saturation condition

The Anti-Expressions (256):
- Anti-π: Violations of density, normalization, geometric closure
- Anti-e: Violations of growth, decay, completeness  
- Anti-i: Violations of reconstruction, reversal, phase coherence
- Anti-φ: Violations of recursion, self-similarity, scale invariance
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from .lattice import (
    MetaPole, Constant, Sector, Element, Level,
    CrystalAddress, CrystalExpression
)


# =============================================================================
# VIOLATION TYPES
# =============================================================================

class ViolationType(IntEnum):
    """Types of mathematical violations."""
    DENSITY = 0           # Ignoring density/normalization factors
    CONVERGENCE = 1       # Violating convergence conditions
    UNITARITY = 2         # Breaking unitarity/normalization
    CAUSALITY = 3         # Violating causal structure
    POSITIVITY = 4        # Negative probabilities/energies
    FINITENESS = 5        # Treating infinite as finite
    DISCRETENESS = 6      # Treating discrete as continuous
    REVERSIBILITY = 7     # Reversing irreversible processes
    PHASE_COHERENCE = 8   # Breaking phase relationships
    SELF_SIMILARITY = 9   # Violating scale invariance


@dataclass
class ImpossibleMove:
    """
    An impossible mathematical operation.
    
    This is the shadow side of the crystal - operations that CANNOT be done
    without violating fundamental constraints.
    """
    name: str
    description: str
    violation_type: ViolationType
    
    # The specific constraint violated
    constraint: str
    
    # Why it fails
    failure_reason: str
    
    # The cost of attempting this (always > 1 for Anti-Aether)
    kappa_cost: float = 2.0
    
    # Reference to the corresponding valid Aether operation
    aether_partner_name: str = ""
    
    def is_impossible(self) -> bool:
        """Check if this is truly impossible (κ > 1)."""
        return self.kappa_cost > 1.0


# =============================================================================
# ANTI-π IMPOSSIBLE MOVES (64)
# =============================================================================

ANTI_PI_MOVES: Dict[Tuple[Sector, Element, Level], ImpossibleMove] = {
    # SQUARE × EARTH
    (Sector.SQUARE, Element.EARTH, Level.L0): ImpossibleMove(
        name="The Singleton",
        description="Mapping infinite lattice to single state with P=1",
        violation_type=ViolationType.DENSITY,
        constraint="Lattice density requires 1/π² normalization",
        failure_reason="Ignoring ζ(2) = π²/6 density factor",
        kappa_cost=np.inf
    ),
    (Sector.SQUARE, Element.EARTH, Level.L1): ImpossibleMove(
        name="The False Sum",
        description="Asserting ΣP(n)=1 on infinite grid without ζ(2) normalization",
        violation_type=ViolationType.DENSITY,
        constraint="Probability normalization on lattice",
        failure_reason="Sum diverges without proper normalization",
        kappa_cost=np.inf
    ),
    (Sector.SQUARE, Element.EARTH, Level.L2): ImpossibleMove(
        name="The Grid Singularity",
        description="Treating discrete point as continuous Dirac δ with infinite density",
        violation_type=ViolationType.DISCRETENESS,
        constraint="Discrete-continuous duality",
        failure_reason="δ-function requires measure-theoretic care",
        kappa_cost=np.inf
    ),
    (Sector.SQUARE, Element.EARTH, Level.L3): ImpossibleMove(
        name="The Blind Trace",
        description="Calculating trace without volume term, setting π=1",
        violation_type=ViolationType.DENSITY,
        constraint="Trace normalization",
        failure_reason="Volume element contains π factors",
        kappa_cost=2.0
    ),
    
    # SQUARE × WATER
    (Sector.SQUARE, Element.WATER, Level.L0): ImpossibleMove(
        name="The Naked Polygon",
        description="Claiming n·sin(π/n) → π without the limit apparatus",
        violation_type=ViolationType.CONVERGENCE,
        constraint="Limit definition of π",
        failure_reason="Finite n gives only approximation",
        kappa_cost=1.5
    ),
    (Sector.SQUARE, Element.WATER, Level.L1): ImpossibleMove(
        name="The Collapsed Interval",
        description="Setting [−π,π] to measure zero while integrating over it",
        violation_type=ViolationType.FINITENESS,
        constraint="Measure positivity",
        failure_reason="Non-trivial interval has positive measure",
        kappa_cost=np.inf
    ),
    (Sector.SQUARE, Element.WATER, Level.L2): ImpossibleMove(
        name="The False Periodicity",
        description="Asserting periodicity 2π on function defined only on (0,1)",
        violation_type=ViolationType.DENSITY,
        constraint="Domain of periodicity",
        failure_reason="Function undefined outside interval",
        kappa_cost=2.0
    ),
    (Sector.SQUARE, Element.WATER, Level.L3): ImpossibleMove(
        name="The Continuous Lattice",
        description="Treating ℤ² as ℝ² without density correction",
        violation_type=ViolationType.DISCRETENESS,
        constraint="Lattice vs continuum",
        failure_reason="Missing density of lattice points",
        kappa_cost=1.5
    ),
    
    # SQUARE × FIRE
    (Sector.SQUARE, Element.FIRE, Level.L0): ImpossibleMove(
        name="The Instant Leibniz",
        description="Claiming π/4 = Σ(−1)ⁿ/(2n+1) converges in finite steps",
        violation_type=ViolationType.CONVERGENCE,
        constraint="Infinite series convergence",
        failure_reason="Series requires infinite terms",
        kappa_cost=np.inf
    ),
    (Sector.SQUARE, Element.FIRE, Level.L1): ImpossibleMove(
        name="The Accelerated Sum",
        description="Ignoring convergence rate, treating conditional as absolute",
        violation_type=ViolationType.CONVERGENCE,
        constraint="Conditional vs absolute convergence",
        failure_reason="Rearrangement changes sum",
        kappa_cost=2.0
    ),
    (Sector.SQUARE, Element.FIRE, Level.L2): ImpossibleMove(
        name="The Frozen Oscillation",
        description="Asserting alternating series reaches limit without oscillation",
        violation_type=ViolationType.CONVERGENCE,
        constraint="Alternating series behavior",
        failure_reason="Must oscillate around limit",
        kappa_cost=1.5
    ),
    (Sector.SQUARE, Element.FIRE, Level.L3): ImpossibleMove(
        name="The Summation Singularity",
        description="Taking derivative of Leibniz series at n=∞",
        violation_type=ViolationType.FINITENESS,
        constraint="Derivative at infinity",
        failure_reason="Infinity is not a number",
        kappa_cost=np.inf
    ),
    
    # SQUARE × AIR
    (Sector.SQUARE, Element.AIR, Level.L0): ImpossibleMove(
        name="The Broken Orthogonality",
        description="Asserting ∫e^{i(n-m)x}dx = δ_{nm} without 1/2π factor",
        violation_type=ViolationType.UNITARITY,
        constraint="Orthonormality of Fourier basis",
        failure_reason="Missing 2π normalization",
        kappa_cost=2.0
    ),
    (Sector.SQUARE, Element.AIR, Level.L1): ImpossibleMove(
        name="The Aliased Kernel",
        description="Using non-orthogonal DFT basis claiming perfect reconstruction",
        violation_type=ViolationType.UNITARITY,
        constraint="Reconstruction condition",
        failure_reason="Aliasing destroys information",
        kappa_cost=np.inf
    ),
    (Sector.SQUARE, Element.AIR, Level.L2): ImpossibleMove(
        name="The Infinite Bandwidth",
        description="Claiming δ-function has finite Fourier representation",
        violation_type=ViolationType.FINITENESS,
        constraint="Bandwidth-localization tradeoff",
        failure_reason="δ requires all frequencies",
        kappa_cost=np.inf
    ),
    (Sector.SQUARE, Element.AIR, Level.L3): ImpossibleMove(
        name="The False Parseval",
        description="Asserting energy conservation without the π normalization",
        violation_type=ViolationType.UNITARITY,
        constraint="Parseval's identity",
        failure_reason="Energy scaling requires π",
        kappa_cost=2.0
    ),
}

# Continue for FLOWER, CLOUD, FRACTAL sectors... (abbreviated for space)


# =============================================================================
# ANTI-e IMPOSSIBLE MOVES (64)
# =============================================================================

ANTI_E_MOVES: Dict[Tuple[Sector, Element, Level], ImpossibleMove] = {
    # SQUARE × EARTH (Combinatorics)
    (Sector.SQUARE, Element.EARTH, Level.L0): ImpossibleMove(
        name="The Finite e",
        description="Truncating e = Σ1/k! at finite k claiming equality",
        violation_type=ViolationType.CONVERGENCE,
        constraint="Infinite series definition of e",
        failure_reason="Finite sum gives only approximation",
        kappa_cost=1.5
    ),
    (Sector.SQUARE, Element.EARTH, Level.L1): ImpossibleMove(
        name="The Integer Derangement",
        description="D(n)/n! exactly 1/e for finite n",
        violation_type=ViolationType.CONVERGENCE,
        constraint="Limit of derangement ratio",
        failure_reason="1/e is only the limit",
        kappa_cost=1.2
    ),
    
    # FLOWER × FIRE (Time Evolution)
    (Sector.FLOWER, Element.FIRE, Level.L0): ImpossibleMove(
        name="The Instant Equilibrium",
        description="e^{λt} at t=0 reaching steady state",
        violation_type=ViolationType.CAUSALITY,
        constraint="Dynamical evolution requires time",
        failure_reason="t=0 is initial condition, not steady state",
        kappa_cost=np.inf
    ),
    (Sector.FLOWER, Element.FIRE, Level.L1): ImpossibleMove(
        name="The Negative Time",
        description="e^{−λt} for t<0 without analytic continuation",
        violation_type=ViolationType.CAUSALITY,
        constraint="Time direction",
        failure_reason="Physical time is positive",
        kappa_cost=2.0
    ),
    
    # CLOUD × EARTH (Poisson)
    (Sector.CLOUD, Element.EARTH, Level.L0): ImpossibleMove(
        name="The Unnormalized Poisson",
        description="P(k) = λᵏ/k! without e^{−λ} factor",
        violation_type=ViolationType.UNITARITY,
        constraint="Probability normalization",
        failure_reason="Sum of probabilities must be 1",
        kappa_cost=np.inf
    ),
}


# =============================================================================
# ANTI-i IMPOSSIBLE MOVES (64)
# =============================================================================

ANTI_I_MOVES: Dict[Tuple[Sector, Element, Level], ImpossibleMove] = {
    # SQUARE × EARTH (Norm)
    (Sector.SQUARE, Element.EARTH, Level.L0): ImpossibleMove(
        name="The Norm Collapse",
        description="z·z̄ = 0 implies z = 0 in ring with zero divisors",
        violation_type=ViolationType.PHASE_COHERENCE,
        constraint="Complex number properties",
        failure_reason="Zero divisors break the norm",
        kappa_cost=np.inf
    ),
    
    # FLOWER × WATER (Cauchy)
    (Sector.FLOWER, Element.WATER, Level.L0): ImpossibleMove(
        name="The Missing 2πi",
        description="Cauchy formula without 1/(2πi) factor",
        violation_type=ViolationType.PHASE_COHERENCE,
        constraint="Cauchy integral normalization",
        failure_reason="Winding number requires 2πi",
        kappa_cost=2.0
    ),
    
    # FLOWER × FIRE (Schrödinger)
    (Sector.FLOWER, Element.FIRE, Level.L0): ImpossibleMove(
        name="The Real Quantum",
        description="iℏ∂ψ/∂t = Hψ without the i",
        violation_type=ViolationType.PHASE_COHERENCE,
        constraint="Quantum unitarity",
        failure_reason="i ensures unitary evolution",
        kappa_cost=np.inf
    ),
    (Sector.FLOWER, Element.FIRE, Level.L1): ImpossibleMove(
        name="The Non-Unitary Evolution",
        description="Quantum evolution with probability not conserved",
        violation_type=ViolationType.UNITARITY,
        constraint="Probability conservation",
        failure_reason="|ψ|² must integrate to 1",
        kappa_cost=np.inf
    ),
}


# =============================================================================
# ANTI-φ IMPOSSIBLE MOVES (64)
# =============================================================================

ANTI_PHI_MOVES: Dict[Tuple[Sector, Element, Level], ImpossibleMove] = {
    # SQUARE × EARTH (Fibonacci)
    (Sector.SQUARE, Element.EARTH, Level.L0): ImpossibleMove(
        name="The Broken Fibonacci",
        description="F_{n+1} = F_n + F_{n-1} with different initial conditions giving φ",
        violation_type=ViolationType.SELF_SIMILARITY,
        constraint="Fibonacci initial conditions",
        failure_reason="F_0=0, F_1=1 required for φ limit",
        kappa_cost=1.5
    ),
    (Sector.SQUARE, Element.EARTH, Level.L1): ImpossibleMove(
        name="The Non-Convergent Ratio",
        description="F_{n+1}/F_n not converging",
        violation_type=ViolationType.CONVERGENCE,
        constraint="Golden ratio limit",
        failure_reason="Ratio always converges to φ",
        kappa_cost=np.inf
    ),
    
    # FLOWER × EARTH (Pentagon)
    (Sector.FLOWER, Element.EARTH, Level.L0): ImpossibleMove(
        name="The Non-Golden Pentagon",
        description="Regular pentagon with diagonal/side ≠ φ",
        violation_type=ViolationType.SELF_SIMILARITY,
        constraint="Pentagon geometry",
        failure_reason="φ is exactly the diagonal/side ratio",
        kappa_cost=np.inf
    ),
    
    # FRACTAL × EARTH (Beatty)
    (Sector.FRACTAL, Element.EARTH, Level.L0): ImpossibleMove(
        name="The Overlapping Beatty",
        description="⌊nφ⌋ and ⌊nφ²⌋ overlapping (not partitioning ℕ)",
        violation_type=ViolationType.SELF_SIMILARITY,
        constraint="Beatty's theorem",
        failure_reason="These sequences partition the positive integers",
        kappa_cost=np.inf
    ),
}


# =============================================================================
# EXPRESSION VALIDATOR
# =============================================================================

class ExpressionValidator:
    """
    Validates Crystal expressions against their constraints.
    
    For Aether: checks that conservation laws hold
    For Anti-Aether: checks that violations are correctly identified
    """
    
    def __init__(self):
        self.anti_pi = ANTI_PI_MOVES
        self.anti_e = ANTI_E_MOVES
        self.anti_i = ANTI_I_MOVES
        self.anti_phi = ANTI_PHI_MOVES
    
    def get_impossible_move(self, addr: CrystalAddress) -> Optional[ImpossibleMove]:
        """Get the impossible move for an Anti-Aether expression."""
        if addr.meta_pole != MetaPole.ANTI_AETHER:
            return None
        
        key = (addr.sector, addr.element, addr.level)
        
        if addr.constant == Constant.PI:
            return self.anti_pi.get(key)
        elif addr.constant == Constant.E:
            return self.anti_e.get(key)
        elif addr.constant == Constant.I:
            return self.anti_i.get(key)
        elif addr.constant == Constant.PHI:
            return self.anti_phi.get(key)
        
        return None
    
    def validate_expression(self, expr: CrystalExpression) -> Tuple[bool, str]:
        """
        Validate an expression.
        
        Returns (is_valid, reason).
        """
        addr = expr.address
        
        if addr.meta_pole == MetaPole.AETHER:
            # Aether expressions must conserve κ
            if expr.kappa_cost <= 1.0:
                return True, "κ-budget conserved"
            else:
                return False, f"κ-budget violated: {expr.kappa_cost} > 1.0"
        
        elif addr.meta_pole == MetaPole.ANTI_AETHER:
            # Anti-Aether expressions must violate κ
            move = self.get_impossible_move(addr)
            if move:
                if move.kappa_cost > 1.0:
                    return True, f"Correctly identified as impossible: {move.name}"
                else:
                    return False, f"Should be impossible but κ={move.kappa_cost}"
            else:
                return True, "No specific impossible move cataloged"
        
        else:
            # Shadow expressions are information-theoretic
            return True, "Shadow expression (information only)"
    
    def get_violation_type(self, addr: CrystalAddress) -> Optional[ViolationType]:
        """Get the type of violation for an Anti-Aether expression."""
        move = self.get_impossible_move(addr)
        return move.violation_type if move else None
    
    def list_violations_by_type(self, vtype: ViolationType) -> List[ImpossibleMove]:
        """Get all impossible moves of a given violation type."""
        all_moves = []
        for moves_dict in [self.anti_pi, self.anti_e, self.anti_i, self.anti_phi]:
            for move in moves_dict.values():
                if move.violation_type == vtype:
                    all_moves.append(move)
        return all_moves


# =============================================================================
# VALIDATION
# =============================================================================

def validate_expressions() -> bool:
    """Validate expression system."""
    validator = ExpressionValidator()
    
    # Check that we have impossible moves cataloged
    assert len(ANTI_PI_MOVES) > 0
    assert len(ANTI_E_MOVES) > 0
    assert len(ANTI_I_MOVES) > 0
    assert len(ANTI_PHI_MOVES) > 0
    
    # Check a specific impossible move
    addr = CrystalAddress(MetaPole.ANTI_AETHER, Constant.PI, 
                          Sector.SQUARE, Element.EARTH, Level.L0)
    move = validator.get_impossible_move(addr)
    assert move is not None
    assert move.name == "The Singleton"
    assert move.is_impossible()
    
    # Check violation type
    vtype = validator.get_violation_type(addr)
    assert vtype == ViolationType.DENSITY
    
    # List violations by type
    density_violations = validator.list_violations_by_type(ViolationType.DENSITY)
    assert len(density_violations) > 0
    
    return True


if __name__ == "__main__":
    print("Validating Expression System...")
    assert validate_expressions()
    print("✓ Expression System validated")
    
    # Demo
    validator = ExpressionValidator()
    
    print("\n=== Sample Impossible Moves ===")
    for const in Constant:
        addr = CrystalAddress(MetaPole.ANTI_AETHER, const,
                             Sector.SQUARE, Element.EARTH, Level.L0)
        move = validator.get_impossible_move(addr)
        if move:
            print(f"\n{const.anti_symbol}: {move.name}")
            print(f"  {move.description}")
            print(f"  Violation: {move.violation_type.name}")
            print(f"  κ-cost: {move.kappa_cost}")
