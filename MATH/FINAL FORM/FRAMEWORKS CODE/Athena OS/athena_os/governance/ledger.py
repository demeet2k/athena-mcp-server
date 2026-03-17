"""
ATHENA OS - Governance Ledger System
====================================
Chain-of-custody and provenance tracking.

From HYBRID_HOLO_LENSE.docx Appendix C10:
Ledger + Topology + Category Closure

LEDGER PROPERTIES:
    1. Append-only (Water rule: history cannot be undone)
    2. Hash-chained (integrity verification)
    3. Timestamped (temporal ordering)
    4. Signed (attestation)

LEDGER TYPES:
    - Decision Ledger: why each step was taken
    - Evidence Ledger: provenance of all inputs
    - Action Ledger: what was done
    - Constraint Ledger: which constraints were checked

REVERSE-SPIN REQUIREMENTS:
    1. Provenance complete (all inputs hashed)
    2. Constraints machine-checkable
    3. Decision counterfactually addressable
    4. Outputs traceable
    5. Rollback path exists OR review enforced
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Generic, TypeVar
from datetime import datetime
import hashlib
import json


# =============================================================================
# LEDGER ENTRY TYPES
# =============================================================================

class EntryType(Enum):
    """Types of ledger entries."""
    DECISION = "decision"
    EVIDENCE = "evidence"
    ACTION = "action"
    CONSTRAINT = "constraint"
    ATTESTATION = "attestation"
    ROLLBACK = "rollback"
    APPEAL = "appeal"


# =============================================================================
# LEDGER ENTRY
# =============================================================================

@dataclass
class LedgerEntry:
    """
    A single entry in the governance ledger.
    
    Entries are immutable once created.
    """
    
    entry_id: str
    entry_type: EntryType
    timestamp: datetime
    
    # Content
    content: Dict[str, Any]
    content_hash: str
    
    # Chain
    previous_hash: str
    
    # Attestation
    signer: str = ""
    signature: str = ""
    
    @classmethod
    def create(cls, entry_type: EntryType, content: Dict[str, Any],
               previous_hash: str, signer: str = "") -> 'LedgerEntry':
        """Create a new ledger entry."""
        timestamp = datetime.now()
        content_str = json.dumps(content, sort_keys=True, default=str)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        entry_id = hashlib.sha256(
            f"{timestamp.isoformat()}:{content_hash}".encode()
        ).hexdigest()[:16]
        
        entry = cls(
            entry_id=entry_id,
            entry_type=entry_type,
            timestamp=timestamp,
            content=content,
            content_hash=content_hash,
            previous_hash=previous_hash,
            signer=signer
        )
        
        if signer:
            entry.sign(signer)
        
        return entry
    
    def sign(self, signer: str) -> None:
        """Sign the entry."""
        self.signer = signer
        sign_content = f"{self.entry_id}:{self.content_hash}:{signer}"
        self.signature = hashlib.sha256(sign_content.encode()).hexdigest()[:32]
    
    def verify_signature(self) -> bool:
        """Verify the entry signature."""
        if not self.signature:
            return True  # Unsigned entries are valid
        sign_content = f"{self.entry_id}:{self.content_hash}:{self.signer}"
        expected = hashlib.sha256(sign_content.encode()).hexdigest()[:32]
        return self.signature == expected
    
    def compute_hash(self) -> str:
        """Compute hash of this entry for chaining."""
        chain_content = f"{self.entry_id}:{self.content_hash}:{self.previous_hash}"
        return hashlib.sha256(chain_content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "entry_id": self.entry_id,
            "entry_type": self.entry_type.value,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "content_hash": self.content_hash,
            "previous_hash": self.previous_hash,
            "signer": self.signer,
            "signature": self.signature[:16] + "..." if self.signature else "",
        }


# =============================================================================
# GOVERNANCE LEDGER
# =============================================================================

@dataclass
class GovernanceLedger:
    """
    The governance ledger - an append-only chain of entries.
    
    Implements the Water rule: history cannot be undone, only compensated.
    """
    
    name: str
    entries: List[LedgerEntry] = field(default_factory=list)
    
    # Genesis block hash
    genesis_hash: str = "0" * 64
    
    def __post_init__(self):
        """Initialize with genesis hash."""
        if not self.entries:
            self._current_hash = self.genesis_hash
        else:
            self._current_hash = self.entries[-1].compute_hash()
    
    @property
    def current_hash(self) -> str:
        """Get current chain head hash."""
        if not self.entries:
            return self.genesis_hash
        return self.entries[-1].compute_hash()
    
    def append(self, entry_type: EntryType, content: Dict[str, Any],
               signer: str = "") -> LedgerEntry:
        """
        Append a new entry to the ledger.
        
        This is the ONLY way to add entries (append-only).
        """
        entry = LedgerEntry.create(
            entry_type=entry_type,
            content=content,
            previous_hash=self.current_hash,
            signer=signer
        )
        self.entries.append(entry)
        return entry
    
    def append_decision(self, action: str, justification: str,
                       alternatives: List[str] = None,
                       signer: str = "") -> LedgerEntry:
        """Append a decision entry."""
        return self.append(EntryType.DECISION, {
            "action": action,
            "justification": justification,
            "alternatives": alternatives or [],
        }, signer)
    
    def append_evidence(self, source: str, content_hash: str,
                       description: str = "",
                       signer: str = "") -> LedgerEntry:
        """Append an evidence entry."""
        return self.append(EntryType.EVIDENCE, {
            "source": source,
            "content_hash": content_hash,
            "description": description,
        }, signer)
    
    def append_action(self, action_type: str, target: str,
                     parameters: Dict[str, Any] = None,
                     signer: str = "") -> LedgerEntry:
        """Append an action entry."""
        return self.append(EntryType.ACTION, {
            "action_type": action_type,
            "target": target,
            "parameters": parameters or {},
        }, signer)
    
    def append_constraint_check(self, constraint_id: str, passed: bool,
                               details: str = "",
                               signer: str = "") -> LedgerEntry:
        """Append a constraint check entry."""
        return self.append(EntryType.CONSTRAINT, {
            "constraint_id": constraint_id,
            "passed": passed,
            "details": details,
        }, signer)
    
    def append_rollback(self, target_entry_id: str, reason: str,
                       signer: str = "") -> LedgerEntry:
        """
        Append a rollback entry.
        
        Note: This doesn't delete the original entry, just marks it
        as rolled back (Water rule).
        """
        return self.append(EntryType.ROLLBACK, {
            "target_entry_id": target_entry_id,
            "reason": reason,
        }, signer)
    
    def verify_chain(self) -> bool:
        """
        Verify the integrity of the entire chain.
        
        Checks:
        1. Each entry's previous_hash matches the actual previous hash
        2. All signatures are valid
        """
        if not self.entries:
            return True
        
        # Check first entry points to genesis
        if self.entries[0].previous_hash != self.genesis_hash:
            return False
        
        # Check chain
        for i, entry in enumerate(self.entries):
            # Verify signature
            if not entry.verify_signature():
                return False
            
            # Verify chain link (except first)
            if i > 0:
                expected_prev = self.entries[i-1].compute_hash()
                if entry.previous_hash != expected_prev:
                    return False
        
        return True
    
    def get_entry(self, entry_id: str) -> Optional[LedgerEntry]:
        """Get entry by ID."""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        return None
    
    def get_entries_by_type(self, entry_type: EntryType) -> List[LedgerEntry]:
        """Get all entries of a specific type."""
        return [e for e in self.entries if e.entry_type == entry_type]
    
    def get_decisions(self) -> List[LedgerEntry]:
        """Get all decision entries."""
        return self.get_entries_by_type(EntryType.DECISION)
    
    def get_evidence(self) -> List[LedgerEntry]:
        """Get all evidence entries."""
        return self.get_entries_by_type(EntryType.EVIDENCE)
    
    def is_rolled_back(self, entry_id: str) -> bool:
        """Check if an entry has been rolled back."""
        rollbacks = self.get_entries_by_type(EntryType.ROLLBACK)
        return any(r.content.get("target_entry_id") == entry_id 
                  for r in rollbacks)
    
    def chain_hash(self) -> str:
        """Compute hash of entire chain."""
        if not self.entries:
            return self.genesis_hash
        
        hashes = [e.compute_hash() for e in self.entries]
        combined = "".join(hashes)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def summary(self) -> Dict[str, Any]:
        """Get ledger summary."""
        type_counts = {}
        for entry_type in EntryType:
            type_counts[entry_type.value] = len(
                self.get_entries_by_type(entry_type)
            )
        
        return {
            "name": self.name,
            "total_entries": len(self.entries),
            "entry_types": type_counts,
            "chain_valid": self.verify_chain(),
            "chain_hash": self.chain_hash()[:16] + "...",
        }
    
    def export(self) -> List[Dict[str, Any]]:
        """Export entire ledger as list of dicts."""
        return [entry.to_dict() for entry in self.entries]


# =============================================================================
# MULTI-LEDGER SYSTEM
# =============================================================================

@dataclass
class LedgerSystem:
    """
    A system of multiple interconnected ledgers.
    
    Manages:
    - Decision ledger
    - Evidence ledger
    - Action ledger
    - Constraint ledger
    """
    
    decision_ledger: GovernanceLedger = field(
        default_factory=lambda: GovernanceLedger("decisions")
    )
    evidence_ledger: GovernanceLedger = field(
        default_factory=lambda: GovernanceLedger("evidence")
    )
    action_ledger: GovernanceLedger = field(
        default_factory=lambda: GovernanceLedger("actions")
    )
    constraint_ledger: GovernanceLedger = field(
        default_factory=lambda: GovernanceLedger("constraints")
    )
    
    # Cross-references
    cross_refs: Dict[str, List[str]] = field(default_factory=dict)
    
    def record_decision(self, action: str, justification: str,
                       evidence_ids: List[str] = None,
                       signer: str = "") -> str:
        """Record a decision with cross-references to evidence."""
        entry = self.decision_ledger.append_decision(
            action, justification, signer=signer
        )
        
        # Create cross-references
        if evidence_ids:
            self.cross_refs[entry.entry_id] = evidence_ids
        
        return entry.entry_id
    
    def record_evidence(self, source: str, content: str,
                       description: str = "",
                       signer: str = "") -> str:
        """Record evidence."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:32]
        entry = self.evidence_ledger.append_evidence(
            source, content_hash, description, signer
        )
        return entry.entry_id
    
    def record_action(self, action_type: str, target: str,
                     decision_id: str = None,
                     parameters: Dict[str, Any] = None,
                     signer: str = "") -> str:
        """Record an action with optional link to decision."""
        entry = self.action_ledger.append_action(
            action_type, target, parameters, signer
        )
        
        # Link to decision
        if decision_id:
            if decision_id not in self.cross_refs:
                self.cross_refs[decision_id] = []
            self.cross_refs[decision_id].append(entry.entry_id)
        
        return entry.entry_id
    
    def record_constraint_check(self, constraint_id: str, passed: bool,
                               action_id: str = None,
                               details: str = "",
                               signer: str = "") -> str:
        """Record a constraint check."""
        entry = self.constraint_ledger.append_constraint_check(
            constraint_id, passed, details, signer
        )
        
        # Link to action
        if action_id:
            if action_id not in self.cross_refs:
                self.cross_refs[action_id] = []
            self.cross_refs[action_id].append(entry.entry_id)
        
        return entry.entry_id
    
    def verify_all(self) -> Dict[str, bool]:
        """Verify all ledgers."""
        return {
            "decisions": self.decision_ledger.verify_chain(),
            "evidence": self.evidence_ledger.verify_chain(),
            "actions": self.action_ledger.verify_chain(),
            "constraints": self.constraint_ledger.verify_chain(),
        }
    
    def all_valid(self) -> bool:
        """Check if all ledgers are valid."""
        return all(self.verify_all().values())
    
    def get_decision_trail(self, decision_id: str) -> Dict[str, Any]:
        """
        Get complete trail for a decision.
        
        Returns all evidence, actions, and constraints linked to it.
        """
        trail = {
            "decision_id": decision_id,
            "decision": None,
            "evidence": [],
            "actions": [],
            "constraints": [],
        }
        
        # Get decision
        decision = self.decision_ledger.get_entry(decision_id)
        if decision:
            trail["decision"] = decision.to_dict()
        
        # Get linked items
        linked_ids = self.cross_refs.get(decision_id, [])
        
        for lid in linked_ids:
            # Check each ledger
            for ledger_name, ledger in [
                ("evidence", self.evidence_ledger),
                ("actions", self.action_ledger),
                ("constraints", self.constraint_ledger),
            ]:
                entry = ledger.get_entry(lid)
                if entry:
                    trail[ledger_name].append(entry.to_dict())
        
        return trail
    
    def summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "ledgers": {
                "decisions": self.decision_ledger.summary(),
                "evidence": self.evidence_ledger.summary(),
                "actions": self.action_ledger.summary(),
                "constraints": self.constraint_ledger.summary(),
            },
            "cross_references": len(self.cross_refs),
            "all_valid": self.all_valid(),
        }


# =============================================================================
# PROVENANCE TRACKER
# =============================================================================

@dataclass
class ProvenanceNode:
    """A node in the provenance graph."""
    
    node_id: str
    node_type: str  # "input", "transform", "output"
    content_hash: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Graph edges
    inputs: List[str] = field(default_factory=list)  # Input node IDs
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProvenanceTracker:
    """
    Tracks data provenance through transformations.
    
    Builds a DAG of how outputs derive from inputs.
    """
    
    nodes: Dict[str, ProvenanceNode] = field(default_factory=dict)
    
    def add_input(self, content: str, source: str) -> str:
        """Add an input node."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:32]
        node_id = f"in_{content_hash[:8]}"
        
        node = ProvenanceNode(
            node_id=node_id,
            node_type="input",
            content_hash=content_hash,
            metadata={"source": source}
        )
        
        self.nodes[node_id] = node
        return node_id
    
    def add_transform(self, input_ids: List[str], 
                     transform_name: str,
                     output_hash: str) -> str:
        """Add a transform node."""
        node_id = f"tx_{output_hash[:8]}"
        
        node = ProvenanceNode(
            node_id=node_id,
            node_type="transform",
            content_hash=output_hash,
            inputs=input_ids,
            metadata={"transform": transform_name}
        )
        
        self.nodes[node_id] = node
        return node_id
    
    def add_output(self, input_ids: List[str],
                  output_content: str,
                  description: str = "") -> str:
        """Add an output node."""
        content_hash = hashlib.sha256(output_content.encode()).hexdigest()[:32]
        node_id = f"out_{content_hash[:8]}"
        
        node = ProvenanceNode(
            node_id=node_id,
            node_type="output",
            content_hash=content_hash,
            inputs=input_ids,
            metadata={"description": description}
        )
        
        self.nodes[node_id] = node
        return node_id
    
    def get_ancestors(self, node_id: str) -> Set[str]:
        """Get all ancestor node IDs."""
        ancestors = set()
        
        def collect(nid: str):
            node = self.nodes.get(nid)
            if node:
                for input_id in node.inputs:
                    if input_id not in ancestors:
                        ancestors.add(input_id)
                        collect(input_id)
        
        collect(node_id)
        return ancestors
    
    def get_input_chain(self, node_id: str) -> List[str]:
        """Get chain of inputs leading to a node."""
        chain = []
        ancestors = self.get_ancestors(node_id)
        
        for nid in ancestors:
            node = self.nodes.get(nid)
            if node and node.node_type == "input":
                chain.append(nid)
        
        return chain
    
    def verify_provenance(self, output_id: str) -> bool:
        """Verify that output has complete provenance."""
        output = self.nodes.get(output_id)
        if not output:
            return False
        
        # Must have at least one input
        inputs = self.get_input_chain(output_id)
        return len(inputs) > 0
    
    def summary(self) -> Dict[str, Any]:
        """Get provenance summary."""
        type_counts = {"input": 0, "transform": 0, "output": 0}
        for node in self.nodes.values():
            type_counts[node.node_type] += 1
        
        return {
            "total_nodes": len(self.nodes),
            "node_types": type_counts,
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_ledger() -> bool:
    """Validate ledger module."""
    
    # Test LedgerEntry
    entry = LedgerEntry.create(
        EntryType.DECISION,
        {"action": "approve", "reason": "test"},
        "0" * 64,
        "test_signer"
    )
    assert entry.verify_signature()
    assert len(entry.entry_id) == 16
    
    # Test GovernanceLedger
    ledger = GovernanceLedger("test")
    
    e1 = ledger.append_decision("action1", "reason1", signer="agent")
    e2 = ledger.append_decision("action2", "reason2", signer="agent")
    e3 = ledger.append_evidence("source", "hash123", signer="agent")
    
    assert len(ledger.entries) == 3
    assert ledger.verify_chain()
    assert len(ledger.get_decisions()) == 2
    assert len(ledger.get_evidence()) == 1
    
    # Test rollback (doesn't delete, just marks)
    ledger.append_rollback(e1.entry_id, "testing rollback")
    assert ledger.is_rolled_back(e1.entry_id)
    assert not ledger.is_rolled_back(e2.entry_id)
    
    # Test LedgerSystem
    system = LedgerSystem()
    
    ev_id = system.record_evidence("user", "input data")
    dec_id = system.record_decision("approve", "data is valid", [ev_id])
    act_id = system.record_action("write", "file.txt", dec_id)
    
    assert system.all_valid()
    
    trail = system.get_decision_trail(dec_id)
    assert trail["decision"] is not None
    
    # Test ProvenanceTracker
    tracker = ProvenanceTracker()
    
    in1 = tracker.add_input("data1", "source1")
    in2 = tracker.add_input("data2", "source2")
    tx1 = tracker.add_transform([in1, in2], "merge", "hash1")
    out1 = tracker.add_output([tx1], "final output")
    
    assert tracker.verify_provenance(out1)
    assert len(tracker.get_input_chain(out1)) == 2
    
    return True


if __name__ == "__main__":
    print("Validating Ledger Module...")
    assert validate_ledger()
    print("✓ Ledger Module validated")
    
    # Demo
    print("\n=== Governance Ledger Demo ===")
    
    system = LedgerSystem()
    
    # Record a complete decision trail
    print("\nRecording decision trail:")
    
    ev1 = system.record_evidence("user_upload", "Document ABC", 
                                 "User uploaded document", "user")
    ev2 = system.record_evidence("database", "Policy XYZ",
                                 "Retrieved policy", "system")
    
    dec = system.record_decision(
        "Approve document",
        "Document meets policy requirements",
        [ev1, ev2],
        "review_agent"
    )
    
    act = system.record_action(
        "publish",
        "document_abc",
        dec,
        {"destination": "public_folder"},
        "system"
    )
    
    system.record_constraint_check("policy_compliance", True, act,
                                   "All checks passed", "verifier")
    
    print(f"  Evidence entries: {len(system.evidence_ledger.entries)}")
    print(f"  Decision entries: {len(system.decision_ledger.entries)}")
    print(f"  Action entries: {len(system.action_ledger.entries)}")
    print(f"  Constraint entries: {len(system.constraint_ledger.entries)}")
    
    print(f"\nAll ledgers valid: {system.all_valid()}")
    
    print("\nDecision trail:")
    trail = system.get_decision_trail(dec)
    print(f"  Decision: {trail['decision']['content']['action']}")
    print(f"  Evidence count: {len(trail['evidence'])}")
    print(f"  Actions count: {len(trail['actions'])}")
    
    print("\nSystem summary:")
    print(f"  {system.summary()}")
