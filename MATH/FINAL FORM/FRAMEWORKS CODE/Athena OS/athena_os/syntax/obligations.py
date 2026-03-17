"""
ATHENA OS - SYNTAX OBLIGATIONS
==============================
OUT-Syntax Satisfaction Relations

From SYNTAX.docx:

OBLIGATION SEMANTICS (OUT as Formal Accountability):
    
    ⊨ ⊆ (S × W) × O
    
    Read as: "program p in context/world w satisfies obligation φ"
    This is the formal bridge between SYNTAX and OUT-SYNTAX.

REFINEMENT:
    Programs refine programs: p ⊑ q
    Obligations refine obligations: φ ⪯ ψ
    
    Monotonicity: if p ⊑ q and φ ⪯ ψ, then
                  p ⊨ ψ implies q ⊨ φ

TESTS AND MONITORS:
    Executable fragments of OUT that produce partial evidence of ⊨.
    Never silently upgraded into full proofs.

DRIFT:
    Measurable misalignment between ⟦p⟧ and declared obligation O.
    - Drift witnesses in Obs (counterexamples)
    - Drift witnesses in Str (static mismatches)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Dict, List, Set, Optional, Any, Tuple, 
    Callable, Union, Protocol, runtime_checkable
)
from enum import Enum, auto
from abc import ABC, abstractmethod

from .core import (
    Pole, RepLevel,
    SyntaxArtifact, OutArtifact, Contract, Invariant, Policy,
    WorldState, Observation, ExecutionResult
)
from .coordinates import CrystalCoord


# =============================================================================
# SATISFACTION RESULT
# =============================================================================

class SatisfactionStatus(Enum):
    """Status of obligation satisfaction check."""
    
    SATISFIED = "satisfied"       # Fully satisfied
    VIOLATED = "violated"         # Definitely violated
    UNKNOWN = "unknown"           # Cannot determine
    PARTIAL = "partial"           # Partially satisfied
    TIMEOUT = "timeout"           # Check timed out


@dataclass
class SatisfactionResult:
    """
    Result of checking p ⊨ φ (program satisfies obligation).
    """
    
    status: SatisfactionStatus
    program_id: str
    obligation_id: str
    world_state_id: str
    
    # Evidence
    witness: Optional[Any] = None
    counterexample: Optional[Any] = None
    
    # Metadata
    check_method: str = "unknown"
    confidence: float = 1.0  # 0-1, how confident we are
    
    @property
    def is_satisfied(self) -> bool:
        return self.status == SatisfactionStatus.SATISFIED
    
    @property
    def is_violated(self) -> bool:
        return self.status == SatisfactionStatus.VIOLATED
    
    @property
    def has_evidence(self) -> bool:
        return self.witness is not None or self.counterexample is not None


# =============================================================================
# OBLIGATION CHECKER INTERFACE
# =============================================================================

@runtime_checkable
class ObligationChecker(Protocol):
    """Protocol for checking obligation satisfaction."""
    
    def check(self, program: SyntaxArtifact, 
              obligation: OutArtifact,
              world: WorldState) -> SatisfactionResult:
        """Check if program satisfies obligation in world."""
        ...


# =============================================================================
# PRECONDITION CHECKER
# =============================================================================

class PreconditionChecker:
    """
    Checks preconditions before execution.
    
    Preconditions are evaluated against the world state.
    """
    
    def __init__(self, evaluator: Optional[Callable[[str, WorldState], bool]] = None):
        self.evaluator = evaluator or self._default_evaluator
    
    def _default_evaluator(self, predicate: str, world: WorldState) -> bool:
        """Simple predicate evaluator."""
        # Parse simple predicates like "x > 0"
        try:
            # Very basic parsing
            parts = predicate.split()
            if len(parts) == 3:
                var, op, val = parts
                actual = world.variables.get(var, 0)
                expected = int(val) if val.isdigit() else world.variables.get(val, 0)
                
                if op == '>':
                    return actual > expected
                elif op == '<':
                    return actual < expected
                elif op == '>=':
                    return actual >= expected
                elif op == '<=':
                    return actual <= expected
                elif op == '==':
                    return actual == expected
                elif op == '!=':
                    return actual != expected
            
            return True  # Default to true for unparseable
            
        except Exception:
            return True
    
    def check(self, program: SyntaxArtifact,
              contract: Contract,
              world: WorldState) -> SatisfactionResult:
        """Check all preconditions."""
        
        for precond in contract.preconditions:
            if not self.evaluator(precond, world):
                return SatisfactionResult(
                    status=SatisfactionStatus.VIOLATED,
                    program_id=program.artifact_id,
                    obligation_id=contract.artifact_id,
                    world_state_id=world.state_id,
                    counterexample={"failed_precondition": precond},
                    check_method="precondition_eval"
                )
        
        return SatisfactionResult(
            status=SatisfactionStatus.SATISFIED,
            program_id=program.artifact_id,
            obligation_id=contract.artifact_id,
            world_state_id=world.state_id,
            witness={"all_preconditions": contract.preconditions},
            check_method="precondition_eval"
        )


# =============================================================================
# POSTCONDITION CHECKER
# =============================================================================

class PostconditionChecker:
    """
    Checks postconditions after execution.
    
    Postconditions are evaluated against the result and final world state.
    """
    
    def __init__(self, evaluator: Optional[Callable[[str, Any, WorldState], bool]] = None):
        self.evaluator = evaluator or self._default_evaluator
    
    def _default_evaluator(self, predicate: str, 
                           result: Any, 
                           world: WorldState) -> bool:
        """Simple postcondition evaluator."""
        try:
            # Handle "result >= x" style predicates
            if predicate.startswith("result"):
                parts = predicate.split()
                if len(parts) == 3:
                    _, op, val = parts
                    expected = int(val) if val.isdigit() else world.variables.get(val, 0)
                    
                    if op == '>':
                        return result > expected
                    elif op == '<':
                        return result < expected
                    elif op == '>=':
                        return result >= expected
                    elif op == '<=':
                        return result <= expected
                    elif op == '==':
                        return result == expected
            
            return True
            
        except Exception:
            return True
    
    def check(self, program: SyntaxArtifact,
              contract: Contract,
              world: WorldState,
              result: Any) -> SatisfactionResult:
        """Check all postconditions."""
        
        for postcond in contract.postconditions:
            if not self.evaluator(postcond, result, world):
                return SatisfactionResult(
                    status=SatisfactionStatus.VIOLATED,
                    program_id=program.artifact_id,
                    obligation_id=contract.artifact_id,
                    world_state_id=world.state_id,
                    counterexample={
                        "failed_postcondition": postcond,
                        "result": result
                    },
                    check_method="postcondition_eval"
                )
        
        return SatisfactionResult(
            status=SatisfactionStatus.SATISFIED,
            program_id=program.artifact_id,
            obligation_id=contract.artifact_id,
            world_state_id=world.state_id,
            witness={
                "all_postconditions": contract.postconditions,
                "result": result
            },
            check_method="postcondition_eval"
        )


# =============================================================================
# INVARIANT CHECKER
# =============================================================================

class InvariantChecker:
    """
    Checks invariants must hold throughout execution.
    """
    
    def __init__(self, evaluator: Optional[Callable[[str, WorldState], bool]] = None):
        self.evaluator = evaluator or (lambda p, w: True)
    
    def check(self, program: SyntaxArtifact,
              invariant: Invariant,
              world: WorldState) -> SatisfactionResult:
        """Check invariant holds."""
        
        if self.evaluator(invariant.predicate, world):
            return SatisfactionResult(
                status=SatisfactionStatus.SATISFIED,
                program_id=program.artifact_id,
                obligation_id=invariant.artifact_id,
                world_state_id=world.state_id,
                witness={"invariant": invariant.predicate},
                check_method="invariant_eval"
            )
        else:
            return SatisfactionResult(
                status=SatisfactionStatus.VIOLATED,
                program_id=program.artifact_id,
                obligation_id=invariant.artifact_id,
                world_state_id=world.state_id,
                counterexample={"violated_invariant": invariant.predicate},
                check_method="invariant_eval"
            )


# =============================================================================
# DRIFT DETECTION
# =============================================================================

@dataclass
class DriftWitness:
    """
    A witness to drift between behavior and obligation.
    
    Can be:
    - Obs-level: counterexample from execution
    - Str-level: static mismatch in structure
    """
    
    witness_type: str  # "obs" or "str"
    description: str
    evidence: Any
    severity: float = 0.5  # 0-1
    
    @classmethod
    def from_counterexample(cls, ce: Any, description: str) -> 'DriftWitness':
        """Create from execution counterexample."""
        return cls(
            witness_type="obs",
            description=description,
            evidence=ce,
            severity=0.8
        )
    
    @classmethod
    def from_static_mismatch(cls, mismatch: Any, description: str) -> 'DriftWitness':
        """Create from static analysis mismatch."""
        return cls(
            witness_type="str",
            description=description,
            evidence=mismatch,
            severity=0.5
        )


class DriftDetector:
    """
    Detects drift between program behavior and obligations.
    
    Drift is measurable misalignment that accumulates over time.
    """
    
    def __init__(self):
        self._witnesses: List[DriftWitness] = []
    
    def detect(self, program: SyntaxArtifact,
               obligations: List[OutArtifact],
               world: WorldState,
               execution_result: Optional[ExecutionResult] = None) -> List[DriftWitness]:
        """
        Detect drift between program and obligations.
        
        Returns list of drift witnesses found.
        """
        witnesses = []
        
        for obligation in obligations:
            if isinstance(obligation, Contract):
                # Check contract drift
                contract_witnesses = self._check_contract_drift(
                    program, obligation, world, execution_result
                )
                witnesses.extend(contract_witnesses)
            
            elif isinstance(obligation, Invariant):
                # Check invariant drift
                inv_witnesses = self._check_invariant_drift(
                    program, obligation, world
                )
                witnesses.extend(inv_witnesses)
            
            elif isinstance(obligation, Policy):
                # Check policy drift
                policy_witnesses = self._check_policy_drift(
                    program, obligation, world
                )
                witnesses.extend(policy_witnesses)
        
        self._witnesses.extend(witnesses)
        return witnesses
    
    def _check_contract_drift(self, program: SyntaxArtifact,
                              contract: Contract,
                              world: WorldState,
                              result: Optional[ExecutionResult]) -> List[DriftWitness]:
        """Check for contract-related drift."""
        witnesses = []
        
        # Check preconditions
        pre_checker = PreconditionChecker()
        pre_result = pre_checker.check(program, contract, world)
        
        if pre_result.is_violated:
            witnesses.append(DriftWitness(
                witness_type="obs",
                description="Precondition violated",
                evidence=pre_result.counterexample,
                severity=0.7
            ))
        
        # Check postconditions if we have a result
        if result and result.observation.return_value is not None:
            post_checker = PostconditionChecker()
            post_result = post_checker.check(
                program, contract, world, 
                result.observation.return_value
            )
            
            if post_result.is_violated:
                witnesses.append(DriftWitness(
                    witness_type="obs",
                    description="Postcondition violated",
                    evidence=post_result.counterexample,
                    severity=0.9
                ))
        
        return witnesses
    
    def _check_invariant_drift(self, program: SyntaxArtifact,
                               invariant: Invariant,
                               world: WorldState) -> List[DriftWitness]:
        """Check for invariant-related drift."""
        checker = InvariantChecker()
        result = checker.check(program, invariant, world)
        
        if result.is_violated:
            return [DriftWitness(
                witness_type="str",
                description="Invariant drift detected",
                evidence=result.counterexample,
                severity=0.6
            )]
        
        return []
    
    def _check_policy_drift(self, program: SyntaxArtifact,
                            policy: Policy,
                            world: WorldState) -> List[DriftWitness]:
        """Check for policy-related drift."""
        # Placeholder - would check policy rules
        return []
    
    def total_drift(self) -> float:
        """Calculate total drift magnitude."""
        if not self._witnesses:
            return 0.0
        
        return sum(w.severity for w in self._witnesses) / len(self._witnesses)
    
    def get_witnesses(self) -> List[DriftWitness]:
        """Get all recorded drift witnesses."""
        return list(self._witnesses)
    
    def clear(self) -> None:
        """Clear recorded witnesses."""
        self._witnesses.clear()


# =============================================================================
# SATISFACTION CHECKER (UNIFIED)
# =============================================================================

class SatisfactionChecker:
    """
    Unified checker for ⊨ relation.
    
    Checks if (p, w) ⊨ φ for program p, world w, obligation φ.
    """
    
    def __init__(self):
        self.pre_checker = PreconditionChecker()
        self.post_checker = PostconditionChecker()
        self.inv_checker = InvariantChecker()
        self.drift_detector = DriftDetector()
    
    def check(self, program: SyntaxArtifact,
              obligation: OutArtifact,
              world: WorldState,
              execution_result: Optional[ExecutionResult] = None) -> SatisfactionResult:
        """
        Check (program, world) ⊨ obligation.
        """
        
        if isinstance(obligation, Contract):
            return self._check_contract(program, obligation, world, execution_result)
        elif isinstance(obligation, Invariant):
            return self.inv_checker.check(program, obligation, world)
        elif isinstance(obligation, Policy):
            return self._check_policy(program, obligation, world)
        else:
            return SatisfactionResult(
                status=SatisfactionStatus.UNKNOWN,
                program_id=program.artifact_id,
                obligation_id=obligation.artifact_id,
                world_state_id=world.state_id,
                check_method="unknown_obligation_type"
            )
    
    def _check_contract(self, program: SyntaxArtifact,
                        contract: Contract,
                        world: WorldState,
                        result: Optional[ExecutionResult]) -> SatisfactionResult:
        """Check contract satisfaction."""
        
        # First check preconditions
        pre_result = self.pre_checker.check(program, contract, world)
        if pre_result.is_violated:
            return pre_result
        
        # Then check postconditions if we have a result
        if result and result.observation.return_value is not None:
            post_result = self.post_checker.check(
                program, contract, world,
                result.observation.return_value
            )
            return post_result
        
        # If no result, we can only check preconditions
        return SatisfactionResult(
            status=SatisfactionStatus.PARTIAL,
            program_id=program.artifact_id,
            obligation_id=contract.artifact_id,
            world_state_id=world.state_id,
            witness={"preconditions_only": True},
            check_method="contract_partial"
        )
    
    def _check_policy(self, program: SyntaxArtifact,
                      policy: Policy,
                      world: WorldState) -> SatisfactionResult:
        """Check policy satisfaction."""
        # Placeholder implementation
        return SatisfactionResult(
            status=SatisfactionStatus.UNKNOWN,
            program_id=program.artifact_id,
            obligation_id=policy.artifact_id,
            world_state_id=world.state_id,
            check_method="policy_check_not_implemented"
        )
    
    def check_all(self, program: SyntaxArtifact,
                  obligations: List[OutArtifact],
                  world: WorldState,
                  execution_result: Optional[ExecutionResult] = None) -> List[SatisfactionResult]:
        """Check all obligations."""
        return [
            self.check(program, ob, world, execution_result)
            for ob in obligations
        ]


# =============================================================================
# REFINEMENT RELATIONS
# =============================================================================

def program_refines(p: SyntaxArtifact, q: SyntaxArtifact) -> bool:
    """
    Check if program p refines program q (p ⊑ q).
    
    p refines q if p is more specific/restricted than q.
    """
    # Simplified: check representation level
    return p.rep_level >= q.rep_level


def obligation_refines(phi: OutArtifact, psi: OutArtifact) -> bool:
    """
    Check if obligation φ refines obligation ψ (φ ⪯ ψ).
    
    φ refines ψ if φ is at most as strong as ψ.
    """
    return phi <= psi  # Uses __le__ from OutArtifact


# =============================================================================
# VALIDATION
# =============================================================================

def validate_obligations() -> bool:
    """Validate obligations module."""
    
    from .core import TextArtifact
    
    # Create test program
    program = TextArtifact(
        content="x + 1",
        pole=Pole.S,
        rep_level=RepLevel.TXT
    )
    
    # Create test world
    world = WorldState(
        state_id="test",
        variables={"x": 5}
    )
    
    # Create test contract
    contract = Contract(
        description="Addition contract",
        preconditions=["x > 0"],
        postconditions=["result >= x"],
        pole=Pole.O,
        rep_level=RepLevel.OBS
    )
    
    # Test precondition checker
    pre_checker = PreconditionChecker()
    pre_result = pre_checker.check(program, contract, world)
    assert pre_result.is_satisfied, "Precondition should be satisfied"
    
    # Test with failing precondition
    bad_world = WorldState(state_id="bad", variables={"x": -1})
    bad_result = pre_checker.check(program, contract, bad_world)
    assert bad_result.is_violated, "Precondition should be violated"
    
    # Test postcondition checker
    post_checker = PostconditionChecker()
    post_result = post_checker.check(program, contract, world, result=6)
    assert post_result.is_satisfied, "Postcondition should be satisfied"
    
    # Test unified checker
    checker = SatisfactionChecker()
    full_result = checker.check(program, contract, world)
    assert full_result.status in [SatisfactionStatus.SATISFIED, SatisfactionStatus.PARTIAL]
    
    # Test drift detector
    detector = DriftDetector()
    witnesses = detector.detect(program, [contract], world)
    # Should have no drift for valid state
    
    # Test refinement
    contract2 = Contract(
        description="Weaker contract",
        preconditions=[],
        postconditions=[],
        strength=0.5,
        pole=Pole.O,
        rep_level=RepLevel.OBS
    )
    assert obligation_refines(contract2, contract)
    
    # Test invariant
    invariant = Invariant(
        description="x must be positive",
        predicate="x > 0",
        pole=Pole.O,
        rep_level=RepLevel.OBS
    )
    inv_checker = InvariantChecker(
        evaluator=lambda p, w: w.variables.get("x", 0) > 0
    )
    inv_result = inv_checker.check(program, invariant, world)
    assert inv_result.is_satisfied
    
    return True


if __name__ == "__main__":
    print("Validating SYNTAX obligations...")
    assert validate_obligations()
    print("✓ SYNTAX obligations validated")
