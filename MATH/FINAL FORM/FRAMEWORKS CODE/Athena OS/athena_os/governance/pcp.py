"""
ATHENA OS - Proof-Carrying Procedures (PCP)
===========================================
The governance interface that makes procedures legible.

PCP = (Spec, Evidence, Decision, Proof, AuditLog, Appeal)

CORE PRINCIPLE:
    Legibility ≡ existence of PCP for decisions/actions
    No PCP → opacity → ungovernable complexity
    PCP → reverse-spin (appeal/audit) is possible

From HYBRID_HOLO_LENSE.docx:
A procedure becomes governable only if it carries:
1. what it did
2. why it did it  
3. under what authority
4. with what evidence
5. and how to appeal

AUTO-LEDGER MAPPING:
When an AI agent takes any action, map it to PCP fields:
- Spec auto-fill: objective, ruleset_id, constraints, allowed/prohibited
- Evidence auto-fill: inputs hashed, assumptions explicit, confidence
- Decision auto-fill: action + alternatives + "why" links
- Proof auto-fill: constraint compliance, safety bounds, permissions
- AuditLog auto-fill: every tool call, file read/write
- Appeal auto-fill: rollback possible?, review before irreversible
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from datetime import datetime
import hashlib
import json
import uuid


# =============================================================================
# CLAIM TYPES
# =============================================================================

class ClaimType(Enum):
    """Types of claims with different verification requirements."""
    DER = "DER"      # Derived - formally proven
    HEUR = "HEUR"    # Heuristic - empirically supported
    CONJ = "CONJ"    # Conjecture - untested hypothesis
    AXIOM = "AXIOM"  # Axiom - assumed true


class ConstraintType(Enum):
    """Types of constraints."""
    HARD = "HARD"    # Must be satisfied (violation = failure)
    SOFT = "SOFT"    # Should be satisfied (violation = penalty)
    GUIDE = "GUIDE"  # Recommended (violation = warning)


class ActionType(Enum):
    """Types of actions."""
    REVERSIBLE = "REVERSIBLE"      # Can be undone
    IRREVERSIBLE = "IRREVERSIBLE"  # Cannot be undone
    CONDITIONAL = "CONDITIONAL"    # Reversible under conditions


# =============================================================================
# SPECIFICATION
# =============================================================================

@dataclass
class Constraint:
    """A single constraint."""
    
    id: str
    description: str
    constraint_type: ConstraintType = ConstraintType.HARD
    check_fn: Optional[Callable] = None
    
    def check(self, context: Dict[str, Any]) -> bool:
        """Check if constraint is satisfied."""
        if self.check_fn:
            return self.check_fn(context)
        return True  # Default: satisfied


@dataclass
class Specification:
    """
    The Spec component of PCP.
    
    Spec (Air/Earth): formal policy / constraints / definitions
    
    Contains:
    - objective: what we're trying to achieve
    - ruleset_id: which policy set is active
    - constraints: list of hard/soft constraints
    - allowed_actions: permitted operations
    - prohibited_actions: forbidden operations
    - ontology_id: domain schema being used
    """
    
    objective: str
    ruleset_id: str = "default"
    constraints: List[Constraint] = field(default_factory=list)
    allowed_actions: Set[str] = field(default_factory=set)
    prohibited_actions: Set[str] = field(default_factory=set)
    ontology_id: str = "general"
    
    def is_action_allowed(self, action: str) -> bool:
        """Check if action is allowed."""
        if action in self.prohibited_actions:
            return False
        if self.allowed_actions and action not in self.allowed_actions:
            return False
        return True
    
    def check_constraints(self, context: Dict[str, Any]) -> Dict[str, bool]:
        """Check all constraints, return results."""
        return {c.id: c.check(context) for c in self.constraints}
    
    def all_hard_satisfied(self, context: Dict[str, Any]) -> bool:
        """Check if all hard constraints are satisfied."""
        for c in self.constraints:
            if c.constraint_type == ConstraintType.HARD:
                if not c.check(context):
                    return False
        return True


# =============================================================================
# EVIDENCE
# =============================================================================

@dataclass
class EvidenceItem:
    """A single piece of evidence."""
    
    id: str
    content_hash: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    content_type: str = "text"
    
    @classmethod
    def from_content(cls, content: str, source: str) -> 'EvidenceItem':
        """Create evidence item from content."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return cls(
            id=f"ev_{content_hash[:8]}",
            content_hash=content_hash,
            source=source
        )


@dataclass
class Evidence:
    """
    The Evidence component of PCP.
    
    Evidence (Water): provenance + measurements
    
    Contains:
    - inputs: hashed input documents/queries
    - assumptions: explicit assumptions made
    - confidence: confidence level (0-1)
    - known_unknowns: what we know we don't know
    """
    
    inputs: List[EvidenceItem] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    confidence: float = 1.0
    known_unknowns: List[str] = field(default_factory=list)
    
    def add_input(self, content: str, source: str) -> EvidenceItem:
        """Add an input and return the evidence item."""
        item = EvidenceItem.from_content(content, source)
        self.inputs.append(item)
        return item
    
    def add_assumption(self, assumption: str) -> None:
        """Add an assumption."""
        self.assumptions.append(assumption)
    
    def provenance_chain(self) -> List[str]:
        """Get chain of evidence hashes."""
        return [item.content_hash for item in self.inputs]


# =============================================================================
# DECISION
# =============================================================================

@dataclass
class Alternative:
    """An alternative action that was considered."""
    
    action: str
    reason_rejected: str
    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class Decision:
    """
    The Decision component of PCP.
    
    Decision: action chosen + rejected alternatives
    
    Contains:
    - action: the chosen action
    - alternatives: rejected alternatives (at least 1)
    - justification: why this action was chosen
    - evidence_refs: references to evidence items
    - counterfactual_hooks: what evidence would flip the decision
    """
    
    action: str
    action_type: ActionType = ActionType.REVERSIBLE
    alternatives: List[Alternative] = field(default_factory=list)
    justification: str = ""
    evidence_refs: List[str] = field(default_factory=list)
    counterfactual_hooks: List[str] = field(default_factory=list)
    
    def add_alternative(self, action: str, reason: str) -> None:
        """Add a rejected alternative."""
        self.alternatives.append(Alternative(
            action=action,
            reason_rejected=reason
        ))
    
    def add_counterfactual(self, condition: str) -> None:
        """Add a counterfactual hook."""
        self.counterfactual_hooks.append(condition)


# =============================================================================
# PROOF
# =============================================================================

@dataclass
class ProofItem:
    """A single proof/verification item."""
    
    check_type: str
    passed: bool
    details: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Proof:
    """
    The Proof component of PCP (the "Earth clamp").
    
    Proof (Earth): verifiable certificate that constraints were respected
    
    Contains:
    - constraint_compliance: results of constraint checks
    - safety_bounds: safety metric results
    - permission_checks: tool permission results
    - attestations: signatures/approvals
    """
    
    constraint_compliance: List[ProofItem] = field(default_factory=list)
    safety_bounds: List[ProofItem] = field(default_factory=list)
    permission_checks: List[ProofItem] = field(default_factory=list)
    attestations: Dict[str, str] = field(default_factory=dict)
    
    def add_constraint_check(self, check_type: str, passed: bool, 
                            details: str = "") -> None:
        """Add a constraint compliance check."""
        self.constraint_compliance.append(ProofItem(
            check_type=check_type,
            passed=passed,
            details=details
        ))
    
    def add_safety_check(self, check_type: str, passed: bool,
                        details: str = "") -> None:
        """Add a safety bounds check."""
        self.safety_bounds.append(ProofItem(
            check_type=check_type,
            passed=passed,
            details=details
        ))
    
    def add_attestation(self, agent: str, signature: str) -> None:
        """Add an attestation."""
        self.attestations[agent] = signature
    
    def all_passed(self) -> bool:
        """Check if all proofs passed."""
        all_items = (
            self.constraint_compliance + 
            self.safety_bounds + 
            self.permission_checks
        )
        return all(item.passed for item in all_items)
    
    def summary(self) -> Dict[str, int]:
        """Get summary of pass/fail counts."""
        all_items = (
            self.constraint_compliance + 
            self.safety_bounds + 
            self.permission_checks
        )
        passed = sum(1 for i in all_items if i.passed)
        failed = sum(1 for i in all_items if not i.passed)
        return {"passed": passed, "failed": failed, "total": len(all_items)}


# =============================================================================
# AUDIT LOG
# =============================================================================

@dataclass
class AuditEvent:
    """A single audit log event."""
    
    event_id: str
    event_type: str
    timestamp: datetime
    reference: str
    content_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, event_type: str, reference: str, 
               content: str = "") -> 'AuditEvent':
        """Create an audit event."""
        return cls(
            event_id=str(uuid.uuid4())[:8],
            event_type=event_type,
            timestamp=datetime.now(),
            reference=reference,
            content_hash=hashlib.sha256(content.encode()).hexdigest()[:16]
        )


@dataclass
class AuditLog:
    """
    The AuditLog component of PCP (chain-of-custody).
    
    AuditLog (Water/Earth): chain-of-custody trace
    
    Every tool call, file read/write, message send is appended as an event.
    """
    
    events: List[AuditEvent] = field(default_factory=list)
    
    def append(self, event_type: str, reference: str, 
               content: str = "") -> AuditEvent:
        """Append an event to the log."""
        event = AuditEvent.create(event_type, reference, content)
        self.events.append(event)
        return event
    
    def log_tool_call(self, tool_name: str, args: str = "") -> AuditEvent:
        """Log a tool call."""
        return self.append("tool_call", tool_name, args)
    
    def log_file_read(self, path: str) -> AuditEvent:
        """Log a file read."""
        return self.append("file_read", path)
    
    def log_file_write(self, path: str, content: str = "") -> AuditEvent:
        """Log a file write."""
        return self.append("file_write", path, content)
    
    def log_message(self, recipient: str, content: str = "") -> AuditEvent:
        """Log a message send."""
        return self.append("message_send", recipient, content)
    
    def chain_hash(self) -> str:
        """Compute hash of entire chain."""
        chain_content = "".join(e.content_hash for e in self.events)
        return hashlib.sha256(chain_content.encode()).hexdigest()[:32]


# =============================================================================
# APPEAL
# =============================================================================

@dataclass
class Appeal:
    """
    The Appeal component of PCP.
    
    Appeal (Air): counterfactual hooks ("what would change outcome?")
    
    Contains:
    - rollback_possible: whether action can be undone
    - review_required: whether human review is required
    - reviewers: who can review
    - grievance_procedure: how to file a grievance
    """
    
    rollback_possible: bool = True
    review_required: bool = False
    reviewers: List[str] = field(default_factory=list)
    grievance_procedure: str = ""
    
    def requires_review_before_action(self, decision: Decision) -> bool:
        """Check if review is required before action."""
        if decision.action_type == ActionType.IRREVERSIBLE:
            return True
        return self.review_required


# =============================================================================
# PROOF-CARRYING PROCEDURE (PCP)
# =============================================================================

@dataclass
class PCP:
    """
    Proof-Carrying Procedure - the complete governance artifact.
    
    PCP = (Spec, Evidence, Decision, Proof, AuditLog, Appeal)
    
    This is the stable AI×Society interface.
    
    A procedure becomes governable only if it carries:
    1. what it did (Decision)
    2. why it did it (Evidence + Justification)
    3. under what authority (Spec)
    4. with what evidence (Evidence)
    5. and how to appeal (Appeal)
    """
    
    pcp_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    spec: Specification = field(default_factory=lambda: Specification(""))
    evidence: Evidence = field(default_factory=Evidence)
    decision: Decision = field(default_factory=lambda: Decision(""))
    proof: Proof = field(default_factory=Proof)
    audit_log: AuditLog = field(default_factory=AuditLog)
    appeal: Appeal = field(default_factory=Appeal)
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        """Check if PCP is valid (all proofs passed)."""
        return self.proof.all_passed()
    
    def is_reversible(self) -> bool:
        """Check if the action is reversible."""
        return self.appeal.rollback_possible
    
    def requires_review(self) -> bool:
        """Check if review is required."""
        return self.appeal.requires_review_before_action(self.decision)
    
    def provenance_complete(self) -> bool:
        """Check if provenance is complete (all inputs hashed)."""
        return len(self.evidence.inputs) > 0
    
    def constraints_checkable(self) -> bool:
        """Check if constraints are machine-checkable."""
        return len(self.spec.constraints) > 0
    
    def counterfactual_addressable(self) -> bool:
        """Check if decision is counterfactually addressable."""
        return len(self.decision.counterfactual_hooks) > 0
    
    def outputs_traceable(self) -> bool:
        """Check if outputs are traceable."""
        return len(self.audit_log.events) > 0
    
    def reverse_spin_ready(self) -> bool:
        """
        Check if reverse-spin (audit/appeal/rollback) is possible.
        
        Requires:
        1. Provenance complete
        2. Constraints machine-checkable
        3. Decision counterfactually addressable
        4. Outputs traceable
        5. Rollback path exists OR review enforced
        """
        return (
            self.provenance_complete() and
            self.constraints_checkable() and
            self.counterfactual_addressable() and
            self.outputs_traceable() and
            (self.is_reversible() or self.requires_review())
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "pcp_id": self.pcp_id,
            "created_at": self.created_at.isoformat(),
            "spec": {
                "objective": self.spec.objective,
                "ruleset_id": self.spec.ruleset_id,
                "constraints": len(self.spec.constraints),
            },
            "evidence": {
                "inputs": len(self.evidence.inputs),
                "assumptions": len(self.evidence.assumptions),
                "confidence": self.evidence.confidence,
            },
            "decision": {
                "action": self.decision.action,
                "action_type": self.decision.action_type.value,
                "alternatives": len(self.decision.alternatives),
            },
            "proof": self.proof.summary(),
            "audit_log": {
                "events": len(self.audit_log.events),
                "chain_hash": self.audit_log.chain_hash(),
            },
            "appeal": {
                "rollback_possible": self.appeal.rollback_possible,
                "review_required": self.appeal.review_required,
            },
            "valid": self.is_valid(),
            "reverse_spin_ready": self.reverse_spin_ready(),
        }


# =============================================================================
# PCP BUILDER
# =============================================================================

class PCPBuilder:
    """Builder for creating PCP records."""
    
    def __init__(self, objective: str):
        self.pcp = PCP(spec=Specification(objective=objective))
    
    def with_ruleset(self, ruleset_id: str) -> 'PCPBuilder':
        """Set ruleset."""
        self.pcp.spec.ruleset_id = ruleset_id
        return self
    
    def add_constraint(self, constraint_id: str, description: str,
                      constraint_type: ConstraintType = ConstraintType.HARD,
                      check_fn: Optional[Callable] = None) -> 'PCPBuilder':
        """Add a constraint."""
        self.pcp.spec.constraints.append(Constraint(
            id=constraint_id,
            description=description,
            constraint_type=constraint_type,
            check_fn=check_fn
        ))
        return self
    
    def add_evidence(self, content: str, source: str) -> 'PCPBuilder':
        """Add evidence."""
        self.pcp.evidence.add_input(content, source)
        return self
    
    def add_assumption(self, assumption: str) -> 'PCPBuilder':
        """Add assumption."""
        self.pcp.evidence.add_assumption(assumption)
        return self
    
    def set_confidence(self, confidence: float) -> 'PCPBuilder':
        """Set confidence level."""
        self.pcp.evidence.confidence = confidence
        return self
    
    def set_decision(self, action: str, justification: str,
                    action_type: ActionType = ActionType.REVERSIBLE) -> 'PCPBuilder':
        """Set decision."""
        self.pcp.decision.action = action
        self.pcp.decision.justification = justification
        self.pcp.decision.action_type = action_type
        return self
    
    def add_alternative(self, action: str, reason: str) -> 'PCPBuilder':
        """Add rejected alternative."""
        self.pcp.decision.add_alternative(action, reason)
        return self
    
    def add_counterfactual(self, condition: str) -> 'PCPBuilder':
        """Add counterfactual hook."""
        self.pcp.decision.add_counterfactual(condition)
        return self
    
    def verify_constraint(self, check_type: str, passed: bool,
                         details: str = "") -> 'PCPBuilder':
        """Add constraint verification."""
        self.pcp.proof.add_constraint_check(check_type, passed, details)
        return self
    
    def verify_safety(self, check_type: str, passed: bool,
                     details: str = "") -> 'PCPBuilder':
        """Add safety verification."""
        self.pcp.proof.add_safety_check(check_type, passed, details)
        return self
    
    def attest(self, agent: str, signature: str) -> 'PCPBuilder':
        """Add attestation."""
        self.pcp.proof.add_attestation(agent, signature)
        return self
    
    def log_action(self, event_type: str, reference: str,
                  content: str = "") -> 'PCPBuilder':
        """Log an action."""
        self.pcp.audit_log.append(event_type, reference, content)
        return self
    
    def set_appeal(self, rollback: bool = True, 
                  review_required: bool = False) -> 'PCPBuilder':
        """Configure appeal options."""
        self.pcp.appeal.rollback_possible = rollback
        self.pcp.appeal.review_required = review_required
        return self
    
    def build(self) -> PCP:
        """Build and return the PCP."""
        return self.pcp


# =============================================================================
# VALIDATION
# =============================================================================

def validate_pcp() -> bool:
    """Validate PCP module."""
    
    # Test building a complete PCP
    pcp = (PCPBuilder("Test objective")
        .with_ruleset("test_rules")
        .add_constraint("c1", "Must be positive", ConstraintType.HARD)
        .add_evidence("Input data", "user")
        .add_assumption("Data is accurate")
        .set_confidence(0.95)
        .set_decision("Approve", "All criteria met")
        .add_alternative("Reject", "Not all criteria met")
        .add_counterfactual("If confidence < 0.8, would reject")
        .verify_constraint("c1", True, "Value is positive")
        .verify_safety("bounds", True, "Within limits")
        .attest("agent_1", "sig_123")
        .log_action("decision_made", "approval")
        .set_appeal(rollback=True, review_required=False)
        .build())
    
    assert pcp.is_valid()
    assert pcp.reverse_spin_ready()
    assert pcp.provenance_complete()
    assert pcp.counterfactual_addressable()
    
    # Test serialization
    data = pcp.to_dict()
    assert data["valid"] == True
    assert data["reverse_spin_ready"] == True
    
    # Test evidence
    evidence = Evidence()
    item = evidence.add_input("test content", "test source")
    assert len(evidence.inputs) == 1
    assert len(item.content_hash) == 16
    
    # Test audit log
    log = AuditLog()
    log.log_tool_call("test_tool", "arg1")
    log.log_file_read("/path/to/file")
    assert len(log.events) == 2
    assert len(log.chain_hash()) == 32
    
    return True


if __name__ == "__main__":
    print("Validating PCP Module...")
    assert validate_pcp()
    print("✓ PCP Module validated")
    
    # Demo
    print("\n=== Proof-Carrying Procedure Demo ===")
    
    pcp = (PCPBuilder("Approve document for publication")
        .with_ruleset("publication_policy")
        .add_constraint("accuracy", "Content must be factually accurate")
        .add_constraint("safety", "No harmful content")
        .add_evidence("Document content hash: abc123", "user_upload")
        .add_assumption("Document has been spell-checked")
        .set_confidence(0.92)
        .set_decision(
            "Approve with minor edits",
            "Document meets all criteria with minor corrections needed"
        )
        .add_alternative("Full rejection", "Would require major rewrite")
        .add_alternative("Conditional approval", "Pending further review")
        .add_counterfactual("If factual errors found, would reject")
        .verify_constraint("accuracy", True, "Fact-checked against sources")
        .verify_constraint("safety", True, "No harmful content detected")
        .verify_safety("compliance", True, "Meets publication standards")
        .attest("review_agent", hashlib.sha256(b"review").hexdigest()[:16])
        .log_action("review_started", "doc_123")
        .log_action("review_completed", "doc_123")
        .set_appeal(rollback=True, review_required=False)
        .build())
    
    print(f"\nPCP ID: {pcp.pcp_id}")
    print(f"Objective: {pcp.spec.objective}")
    print(f"Decision: {pcp.decision.action}")
    print(f"Valid: {pcp.is_valid()}")
    print(f"Reverse-spin ready: {pcp.reverse_spin_ready()}")
    print(f"\nSummary: {json.dumps(pcp.to_dict(), indent=2)}")
