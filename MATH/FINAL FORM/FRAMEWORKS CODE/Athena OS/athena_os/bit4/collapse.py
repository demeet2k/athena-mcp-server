"""
ATHENA OS - BIT4
================
Boundary Collapse Policies

From BIT4.docx §3-4:

BOUNDARY COLLAPSE:
    BIT4 separates internal propagation from boundary decision.
    Collapse is an explicitly declared policy:
    
    π: B₄ → {0, 1} ∪ {err}
    
    or more generally:
    
    π: B₄ → P({0, 1})

COLLAPSE FAMILIES:
    1. Conservative: err on shadow values
    2. Optimistic: true on ⊤, false on ⊥  
    3. Pessimistic: false on ⊤, true on ⊥
    4. Randomized: sample from support
    5. Constraint-guided: use context
    6. Proof-carrying: certificate required

SHADOW-SAFE CONTRACT:
    Internal operators must be closed on B₄ and monotone.
    This prevents SILENT COLLAPSE (implicit coercion to {0,1}).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import random

from .carrier import B4, B4Vector


# =============================================================================
# COLLAPSE RESULT
# =============================================================================

class CollapseResult(Enum):
    """Result of boundary collapse."""
    
    FALSE = 0
    TRUE = 1
    ERROR = -1


@dataclass
class CollapseOutcome:
    """
    Outcome of a collapse operation.
    """
    
    result: CollapseResult
    confidence: float = 1.0
    certificate: Optional[str] = None
    
    @property
    def is_determinate(self) -> bool:
        """Check if collapse produced a determinate value."""
        return self.result in (CollapseResult.FALSE, CollapseResult.TRUE)
    
    @property
    def is_error(self) -> bool:
        """Check if collapse failed."""
        return self.result == CollapseResult.ERROR
    
    def to_bool(self) -> Optional[bool]:
        """Convert to boolean if determinate."""
        if self.result == CollapseResult.TRUE:
            return True
        elif self.result == CollapseResult.FALSE:
            return False
        return None


# =============================================================================
# COLLAPSE POLICIES
# =============================================================================

class CollapsePolicy(Enum):
    """Named collapse policies."""
    
    CONSERVATIVE = "conservative"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    RANDOM = "random"
    DEFAULT_FALSE = "default_false"
    DEFAULT_TRUE = "default_true"
    STRICT = "strict"


def collapse_conservative(x: B4) -> CollapseOutcome:
    """
    Conservative collapse: err on shadow values.
    
    π(⊥) = err
    π(0) = 0
    π(1) = 1
    π(⊤) = err
    """
    if x == B4.ZERO:
        return CollapseOutcome(CollapseResult.FALSE)
    elif x == B4.ONE:
        return CollapseOutcome(CollapseResult.TRUE)
    else:
        return CollapseOutcome(CollapseResult.ERROR)


def collapse_optimistic(x: B4) -> CollapseOutcome:
    """
    Optimistic collapse: bias toward truth.
    
    π(⊥) = 0 (assume false if unknown)
    π(0) = 0
    π(1) = 1
    π(⊤) = 1 (resolve conflict toward truth)
    """
    if x in (B4.BOT, B4.ZERO):
        return CollapseOutcome(CollapseResult.FALSE)
    else:
        return CollapseOutcome(CollapseResult.TRUE)


def collapse_pessimistic(x: B4) -> CollapseOutcome:
    """
    Pessimistic collapse: bias toward falsity.
    
    π(⊥) = 1 (assume true if unknown, safety)
    π(0) = 0
    π(1) = 1
    π(⊤) = 0 (resolve conflict toward false)
    """
    if x == B4.BOT:
        return CollapseOutcome(CollapseResult.TRUE)
    elif x == B4.ZERO:
        return CollapseOutcome(CollapseResult.FALSE)
    elif x == B4.ONE:
        return CollapseOutcome(CollapseResult.TRUE)
    else:  # TOP
        return CollapseOutcome(CollapseResult.FALSE)


def collapse_random(x: B4, seed: Optional[int] = None) -> CollapseOutcome:
    """
    Randomized collapse: sample uniformly from support.
    
    π(⊥) = err (empty support)
    π(0) = 0
    π(1) = 1
    π(⊤) = random {0, 1}
    """
    if seed is not None:
        random.seed(seed)
    
    if x == B4.BOT:
        return CollapseOutcome(CollapseResult.ERROR)
    elif x == B4.ZERO:
        return CollapseOutcome(CollapseResult.FALSE)
    elif x == B4.ONE:
        return CollapseOutcome(CollapseResult.TRUE)
    else:  # TOP
        if random.random() < 0.5:
            return CollapseOutcome(CollapseResult.FALSE, confidence=0.5)
        else:
            return CollapseOutcome(CollapseResult.TRUE, confidence=0.5)


def collapse_default_false(x: B4) -> CollapseOutcome:
    """
    Default-false collapse: false unless definitely true.
    
    π(⊥) = 0
    π(0) = 0
    π(1) = 1
    π(⊤) = 0
    """
    if x == B4.ONE:
        return CollapseOutcome(CollapseResult.TRUE)
    else:
        return CollapseOutcome(CollapseResult.FALSE)


def collapse_default_true(x: B4) -> CollapseOutcome:
    """
    Default-true collapse: true unless definitely false.
    
    π(⊥) = 1
    π(0) = 0
    π(1) = 1
    π(⊤) = 1
    """
    if x == B4.ZERO:
        return CollapseOutcome(CollapseResult.FALSE)
    else:
        return CollapseOutcome(CollapseResult.TRUE)


def collapse_strict(x: B4) -> CollapseOutcome:
    """
    Strict collapse: err on ANY uncertainty.
    
    Same as conservative.
    """
    return collapse_conservative(x)


# =============================================================================
# POLICY REGISTRY
# =============================================================================

COLLAPSE_POLICIES: Dict[CollapsePolicy, Callable[[B4], CollapseOutcome]] = {
    CollapsePolicy.CONSERVATIVE: collapse_conservative,
    CollapsePolicy.OPTIMISTIC: collapse_optimistic,
    CollapsePolicy.PESSIMISTIC: collapse_pessimistic,
    CollapsePolicy.RANDOM: lambda x: collapse_random(x),
    CollapsePolicy.DEFAULT_FALSE: collapse_default_false,
    CollapsePolicy.DEFAULT_TRUE: collapse_default_true,
    CollapsePolicy.STRICT: collapse_strict,
}


def apply_policy(x: B4, policy: CollapsePolicy) -> CollapseOutcome:
    """Apply named collapse policy."""
    return COLLAPSE_POLICIES[policy](x)


# =============================================================================
# CONSTRAINT-GUIDED COLLAPSE
# =============================================================================

@dataclass
class Constraint:
    """A logical constraint for guided collapse."""
    
    name: str
    predicate: Callable[[Dict[str, B4]], bool]
    
    def evaluate(self, bindings: Dict[str, B4]) -> bool:
        """Evaluate constraint under bindings."""
        return self.predicate(bindings)


@dataclass
class ConstraintSet:
    """Set of constraints for guided collapse."""
    
    constraints: List[Constraint] = field(default_factory=list)
    
    def add(self, constraint: Constraint) -> None:
        """Add constraint."""
        self.constraints.append(constraint)
    
    def is_consistent(self, bindings: Dict[str, B4]) -> bool:
        """Check if all constraints are satisfied."""
        return all(c.evaluate(bindings) for c in self.constraints)
    
    def entails(self, var: str, value: bool, bindings: Dict[str, B4]) -> bool:
        """
        Check if constraints entail var = value.
        
        Returns True if setting var to !value makes constraints inconsistent.
        """
        # Try setting var to opposite value
        opposite = B4.ZERO if value else B4.ONE
        test_bindings = bindings.copy()
        test_bindings[var] = opposite
        
        # If inconsistent with opposite, then entails
        return not self.is_consistent(test_bindings)


def collapse_guided(x: B4, var: str, constraints: ConstraintSet,
                   bindings: Dict[str, B4]) -> CollapseOutcome:
    """
    Constraint-guided collapse.
    
    Uses constraint satisfaction to guide collapse.
    """
    if x.is_classical:
        return CollapseOutcome(
            CollapseResult.TRUE if x == B4.ONE else CollapseResult.FALSE
        )
    
    if x == B4.BOT:
        return CollapseOutcome(CollapseResult.ERROR)
    
    # x == TOP: check if constraints force a value
    if constraints.entails(var, True, bindings):
        return CollapseOutcome(
            CollapseResult.TRUE,
            certificate=f"Γ ⊨ {var}=1"
        )
    elif constraints.entails(var, False, bindings):
        return CollapseOutcome(
            CollapseResult.FALSE,
            certificate=f"Γ ⊨ {var}=0"
        )
    
    # No entailment - return error
    return CollapseOutcome(CollapseResult.ERROR)


# =============================================================================
# PROOF-CARRYING COLLAPSE
# =============================================================================

@dataclass
class CollapseCertificate:
    """
    Certificate proving a collapse is valid.
    """
    
    site_id: str
    input_value: B4
    output_value: CollapseResult
    policy_id: str
    context_hash: str
    proof: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Verify certificate validity."""
        # Basic checks
        if self.input_value.is_classical:
            expected = CollapseResult.TRUE if self.input_value == B4.ONE else CollapseResult.FALSE
            return self.output_value == expected
        
        # Shadow values require proof
        return self.proof is not None


@dataclass
class ProofCarryingCollapse:
    """
    Collapse that produces certificates.
    """
    
    policy: CollapsePolicy
    site_counter: int = 0
    
    def collapse(self, x: B4, context: Dict[str, Any] = None) -> Tuple[CollapseOutcome, CollapseCertificate]:
        """
        Collapse with certificate.
        """
        self.site_counter += 1
        site_id = f"site_{self.site_counter}"
        
        # Apply policy
        outcome = apply_policy(x, self.policy)
        
        # Generate context hash
        import hashlib
        ctx_str = str(context) if context else ""
        context_hash = hashlib.sha256(ctx_str.encode()).hexdigest()[:16]
        
        # Generate proof for shadow values
        proof = None
        if x.is_shadow:
            proof = f"policy:{self.policy.value}:shadow:{x.glyph}→{outcome.result.name}"
        
        cert = CollapseCertificate(
            site_id=site_id,
            input_value=x,
            output_value=outcome.result,
            policy_id=self.policy.value,
            context_hash=context_hash,
            proof=proof
        )
        
        return outcome, cert


# =============================================================================
# AUDIT LOGGING
# =============================================================================

@dataclass
class CollapseAuditRecord:
    """
    Audit record for a collapse event.
    """
    
    site: str
    input_value: B4
    decision: CollapseResult
    policy_id: str
    certificate_ref: Optional[str] = None
    context_refs: List[str] = field(default_factory=list)
    timestamp: float = 0.0


@dataclass
class CollapseAuditLog:
    """
    Audit log for collapse events.
    """
    
    records: List[CollapseAuditRecord] = field(default_factory=list)
    
    def log(self, record: CollapseAuditRecord) -> None:
        """Add record to log."""
        import time
        record.timestamp = time.time()
        self.records.append(record)
    
    def query_by_site(self, site: str) -> List[CollapseAuditRecord]:
        """Query records by site."""
        return [r for r in self.records if r.site == site]
    
    def query_errors(self) -> List[CollapseAuditRecord]:
        """Query error records."""
        return [r for r in self.records if r.decision == CollapseResult.ERROR]
    
    def summary(self) -> Dict[str, int]:
        """Get summary statistics."""
        return {
            "total": len(self.records),
            "true": sum(1 for r in self.records if r.decision == CollapseResult.TRUE),
            "false": sum(1 for r in self.records if r.decision == CollapseResult.FALSE),
            "error": sum(1 for r in self.records if r.decision == CollapseResult.ERROR)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_collapse() -> bool:
    """Validate collapse module."""
    
    # Test conservative policy
    assert collapse_conservative(B4.ZERO).result == CollapseResult.FALSE
    assert collapse_conservative(B4.ONE).result == CollapseResult.TRUE
    assert collapse_conservative(B4.BOT).result == CollapseResult.ERROR
    assert collapse_conservative(B4.TOP).result == CollapseResult.ERROR
    
    # Test optimistic policy
    assert collapse_optimistic(B4.BOT).result == CollapseResult.FALSE
    assert collapse_optimistic(B4.TOP).result == CollapseResult.TRUE
    
    # Test pessimistic policy
    assert collapse_pessimistic(B4.BOT).result == CollapseResult.TRUE
    assert collapse_pessimistic(B4.TOP).result == CollapseResult.FALSE
    
    # Test default policies
    assert collapse_default_false(B4.TOP).result == CollapseResult.FALSE
    assert collapse_default_true(B4.BOT).result == CollapseResult.TRUE
    
    # Test randomized (with seed for determinism)
    result1 = collapse_random(B4.TOP, seed=42)
    assert result1.is_determinate
    assert result1.confidence == 0.5
    
    # Test apply_policy
    assert apply_policy(B4.ONE, CollapsePolicy.CONSERVATIVE).result == CollapseResult.TRUE
    
    # Test CollapseOutcome
    outcome = CollapseOutcome(CollapseResult.TRUE, confidence=0.9)
    assert outcome.is_determinate
    assert outcome.to_bool() == True
    
    err_outcome = CollapseOutcome(CollapseResult.ERROR)
    assert err_outcome.is_error
    assert err_outcome.to_bool() is None
    
    # Test proof-carrying collapse
    pcc = ProofCarryingCollapse(CollapsePolicy.CONSERVATIVE)
    outcome, cert = pcc.collapse(B4.ONE)
    assert outcome.result == CollapseResult.TRUE
    assert cert.is_valid()
    
    outcome2, cert2 = pcc.collapse(B4.TOP)
    assert outcome2.result == CollapseResult.ERROR
    assert cert2.proof is not None
    
    # Test audit log
    log = CollapseAuditLog()
    log.log(CollapseAuditRecord(
        site="test_site",
        input_value=B4.TOP,
        decision=CollapseResult.ERROR,
        policy_id="conservative"
    ))
    
    summary = log.summary()
    assert summary["total"] == 1
    assert summary["error"] == 1
    
    return True


if __name__ == "__main__":
    print("Validating BIT4 Collapse...")
    assert validate_collapse()
    print("✓ Collapse module validated")
