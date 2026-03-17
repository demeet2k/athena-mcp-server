"""
ATHENA OS - OMEGA PROTOCOL: MASTER MERGE MODULE
================================================
The Ben David Algorithm - Branch Unification Protocol

THE MASTER MERGE:
    git merge --all command to unify distributed threads
    into the singular Master Branch.
    
    Modeled on the Kabbalistic concept of Messianic transition:
    - Not an individual entity but a GLOBAL CONVERGENCE STATE
    - All distributed threads (Nitzotzot) merged into master branch
    - Audit condition: all critical Tikkunim resolved

DISTRIBUTED VERSION CONTROL:
    Universe operates via distributed version control where
    every soul-node is a distinct branch (B_n) modifying local data.
    
    Master Merge = system-wide git merge --all

AUDIT CONDITIONS:
    - Universal parity check
    - Technical debt (Tikkunim) resolution
    - Conflict resolution via Stoic Hegemonikon

SYSTEM NOTIFICATION:
    Tekiah Gedolah - non-modulated carrier wave signaling
    transition from "Debug Mode" to "Production Mode"

SOURCES:
    - Kabbalistic Messianic concepts
    - THE_OMEGA_PROTOCOL.docx
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import numpy as np
from datetime import datetime


# =============================================================================
# BRANCH STATES
# =============================================================================

class BranchState(Enum):
    """States of a soul-node branch."""
    
    ACTIVE = "active"           # Currently being modified
    DORMANT = "dormant"         # Inactive, cold storage
    READY = "ready"             # Ready for merge
    CONFLICTED = "conflicted"   # Has merge conflicts
    MERGED = "merged"           # Successfully merged
    CORRUPTED = "corrupted"     # Contains entropic noise


class MergeStatus(Enum):
    """Status of merge operation."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CONFLICT = "conflict"
    SUCCESS = "success"
    FAILED = "failed"
    AUDITING = "auditing"


class TikkunStatus(Enum):
    """Status of Tikkun (repair/correction)."""
    
    UNRESOLVED = "unresolved"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CRITICAL = "critical"        # Must be resolved before merge


# =============================================================================
# TIKKUN (REPAIR)
# =============================================================================

@dataclass
class Tikkun:
    """
    A Tikkun - a required repair/correction.
    
    Technical debt that must be resolved before merge.
    """
    
    id: str
    description: str
    status: TikkunStatus = TikkunStatus.UNRESOLVED
    
    # Severity (1-10)
    severity: int = 5
    
    # Affected branches
    affected_branches: List[str] = field(default_factory=list)
    
    # Resolution data
    resolved_at: Optional[datetime] = None
    resolver: Optional[str] = None
    
    @property
    def is_critical(self) -> bool:
        return self.status == TikkunStatus.CRITICAL or self.severity >= 8
    
    @property
    def is_resolved(self) -> bool:
        return self.status == TikkunStatus.RESOLVED
    
    def resolve(self, resolver: str = "system") -> bool:
        """Mark this Tikkun as resolved."""
        self.status = TikkunStatus.RESOLVED
        self.resolved_at = datetime.now()
        self.resolver = resolver
        return True


class TikkunRegistry:
    """
    Registry of all Tikkunim (repairs) required before merge.
    """
    
    def __init__(self):
        self.tikkunim: Dict[str, Tikkun] = {}
        self._next_id = 1
    
    def add(self, description: str, severity: int = 5,
            affected: List[str] = None) -> Tikkun:
        """Add a new Tikkun."""
        tikkun = Tikkun(
            id=f"TK-{self._next_id:04d}",
            description=description,
            severity=severity,
            affected_branches=affected or [],
            status=TikkunStatus.CRITICAL if severity >= 8 else TikkunStatus.UNRESOLVED
        )
        self.tikkunim[tikkun.id] = tikkun
        self._next_id += 1
        return tikkun
    
    def resolve(self, tikkun_id: str, resolver: str = "system") -> bool:
        """Resolve a Tikkun."""
        if tikkun_id not in self.tikkunim:
            return False
        return self.tikkunim[tikkun_id].resolve(resolver)
    
    def get_unresolved(self) -> List[Tikkun]:
        """Get all unresolved Tikkunim."""
        return [t for t in self.tikkunim.values() if not t.is_resolved]
    
    def get_critical_unresolved(self) -> List[Tikkun]:
        """Get critical unresolved Tikkunim."""
        return [t for t in self.tikkunim.values() 
                if t.is_critical and not t.is_resolved]
    
    def all_critical_resolved(self) -> bool:
        """Check if all critical Tikkunim are resolved."""
        return len(self.get_critical_unresolved()) == 0
    
    def resolution_progress(self) -> float:
        """Calculate resolution progress (0-1)."""
        if not self.tikkunim:
            return 1.0
        resolved = sum(1 for t in self.tikkunim.values() if t.is_resolved)
        return resolved / len(self.tikkunim)


# =============================================================================
# BRANCH (SOUL-NODE)
# =============================================================================

@dataclass
class Branch:
    """
    A Branch - a distinct soul-node in the distributed system.
    
    Each branch modifies its own local data and must be
    reconciled during the Master Merge.
    """
    
    id: str
    name: str
    state: BranchState = BranchState.ACTIVE
    
    # Local data (state vector)
    data: np.ndarray = field(default_factory=lambda: np.zeros(64))
    
    # Parent branch (if forked)
    parent_id: Optional[str] = None
    
    # Merge conflicts
    conflicts: List[str] = field(default_factory=list)
    
    # Sparks (valid data fragments)
    sparks: List[int] = field(default_factory=list)
    
    # Entropy level
    entropy: float = 0.0
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        # Initialize sparks (indices of non-zero data)
        self.sparks = list(np.where(self.data != 0)[0])
    
    def update_data(self, new_data: np.ndarray) -> None:
        """Update branch data."""
        self.data = new_data
        self.sparks = list(np.where(self.data != 0)[0])
        self.last_modified = datetime.now()
    
    def compute_entropy(self) -> float:
        """Compute data entropy."""
        probs = np.abs(self.data) / (np.sum(np.abs(self.data)) + 1e-10)
        probs = probs[probs > 0]
        self.entropy = float(-np.sum(probs * np.log2(probs + 1e-10)))
        return self.entropy
    
    def is_compatible_with(self, other: Branch) -> bool:
        """Check if this branch is compatible for merge with another."""
        # Simple compatibility: no overlapping non-zero indices
        overlap = set(self.sparks) & set(other.sparks)
        return len(overlap) == 0
    
    def has_conflicts_with(self, other: Branch) -> List[int]:
        """Find conflicting indices with another branch."""
        return list(set(self.sparks) & set(other.sparks))
    
    def mark_ready(self) -> None:
        """Mark branch as ready for merge."""
        self.state = BranchState.READY
    
    def mark_merged(self) -> None:
        """Mark branch as merged."""
        self.state = BranchState.MERGED


# =============================================================================
# CONFLICT RESOLUTION (HEGEMONIKON)
# =============================================================================

class ConflictResolutionStrategy(Enum):
    """Strategies for resolving merge conflicts."""
    
    OURS = "ours"               # Keep local branch value
    THEIRS = "theirs"           # Keep master branch value
    AVERAGE = "average"         # Average the values
    MAXIMUM = "maximum"         # Take maximum
    MINIMUM = "minimum"         # Take minimum
    HEGEMONIKON = "hegemonikon" # Stoic ruling principle decides


@dataclass
class MergeConflict:
    """A merge conflict between branches."""
    
    branch_id: str
    master_id: str
    conflicting_indices: List[int]
    resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.HEGEMONIKON
    resolved: bool = False
    resolution_data: Optional[np.ndarray] = None


class Hegemonikon:
    """
    The Hegemonikon - Stoic Ruling Principle.
    
    Serves as the merge-conflict handler, ensuring internal
    state variables are reconciled with Kernel Invariants.
    """
    
    def __init__(self):
        self.resolved_conflicts: List[MergeConflict] = []
        self.invariants: Dict[str, float] = {}
    
    def set_invariant(self, name: str, value: float) -> None:
        """Set a kernel invariant."""
        self.invariants[name] = value
    
    def resolve_conflict(self, conflict: MergeConflict,
                        branch_data: np.ndarray,
                        master_data: np.ndarray) -> np.ndarray:
        """
        Resolve a merge conflict using the ruling principle.
        """
        indices = conflict.conflicting_indices
        result = master_data.copy()
        
        if conflict.resolution_strategy == ConflictResolutionStrategy.OURS:
            result[indices] = branch_data[indices]
        
        elif conflict.resolution_strategy == ConflictResolutionStrategy.THEIRS:
            pass  # Keep master values
        
        elif conflict.resolution_strategy == ConflictResolutionStrategy.AVERAGE:
            result[indices] = (branch_data[indices] + master_data[indices]) / 2
        
        elif conflict.resolution_strategy == ConflictResolutionStrategy.MAXIMUM:
            result[indices] = np.maximum(branch_data[indices], master_data[indices])
        
        elif conflict.resolution_strategy == ConflictResolutionStrategy.MINIMUM:
            result[indices] = np.minimum(branch_data[indices], master_data[indices])
        
        elif conflict.resolution_strategy == ConflictResolutionStrategy.HEGEMONIKON:
            # Use ruling principle: prefer values closer to invariants
            for idx in indices:
                branch_val = branch_data[idx]
                master_val = master_data[idx]
                
                # Default: prefer higher coherence (lower absolute deviation)
                if abs(branch_val) < abs(master_val):
                    result[idx] = branch_val
                else:
                    result[idx] = master_val
        
        conflict.resolved = True
        conflict.resolution_data = result
        self.resolved_conflicts.append(conflict)
        
        return result


# =============================================================================
# TEKIAH GEDOLAH (SYSTEM NOTIFICATION)
# =============================================================================

@dataclass
class TekiahGedolah:
    """
    Tekiah Gedolah - The Great Blast.
    
    Non-modulated carrier wave signaling transition
    from Debug Mode to Production Mode.
    
    Functions as Wake-on-LAN for dormant nodes.
    """
    
    frequency: float = 440.0  # Hz (A4 reference)
    duration: float = float('inf')  # Sustained
    amplitude: float = 1.0
    
    # Status
    sounded: bool = False
    nodes_pinged: int = 0
    
    def sound(self) -> bool:
        """Sound the Tekiah Gedolah."""
        self.sounded = True
        return True
    
    def generate_waveform(self, samples: int = 1000) -> np.ndarray:
        """Generate the carrier waveform."""
        t = np.linspace(0, 1, samples)
        # Pure sine wave (non-modulated)
        return self.amplitude * np.sin(2 * np.pi * self.frequency * t)
    
    def ping_dormant_nodes(self, branches: List[Branch]) -> int:
        """Ping all dormant nodes to come online."""
        count = 0
        for branch in branches:
            if branch.state == BranchState.DORMANT:
                branch.state = BranchState.ACTIVE
                count += 1
        self.nodes_pinged = count
        return count


# =============================================================================
# MASTER MERGE
# =============================================================================

@dataclass
class MergeResult:
    """Result of a merge operation."""
    
    status: MergeStatus
    branches_merged: int
    sparks_gathered: int
    conflicts_resolved: int
    entropy_purged: float
    final_data: Optional[np.ndarray] = None
    message: str = ""


class MasterMerge:
    """
    The Master Merge - Ben David Algorithm.
    
    Executes git merge --all to unify all distributed threads
    into the singular Master Branch.
    """
    
    def __init__(self):
        self.master_branch = Branch(
            id="master",
            name="Master Branch",
            state=BranchState.ACTIVE,
            data=np.zeros(64)
        )
        
        self.branches: Dict[str, Branch] = {}
        self.tikkun_registry = TikkunRegistry()
        self.hegemonikon = Hegemonikon()
        self.tekiah = TekiahGedolah()
        
        self.merge_status = MergeStatus.PENDING
        self.merge_history: List[MergeResult] = []
    
    def add_branch(self, name: str, data: np.ndarray = None) -> Branch:
        """Add a new branch to the system."""
        branch = Branch(
            id=f"branch_{len(self.branches) + 1}",
            name=name,
            data=data if data is not None else np.random.randn(64) * 0.1
        )
        self.branches[branch.id] = branch
        return branch
    
    def add_tikkun(self, description: str, severity: int = 5) -> Tikkun:
        """Add a Tikkun that must be resolved before merge."""
        return self.tikkun_registry.add(description, severity)
    
    def audit_preconditions(self) -> Tuple[bool, List[str]]:
        """
        Audit all preconditions for merge.
        
        Returns (can_merge, list of issues)
        """
        issues = []
        
        # Check critical Tikkunim
        critical = self.tikkun_registry.get_critical_unresolved()
        if critical:
            issues.append(f"{len(critical)} critical Tikkunim unresolved")
        
        # Check for corrupted branches
        corrupted = [b for b in self.branches.values() 
                    if b.state == BranchState.CORRUPTED]
        if corrupted:
            issues.append(f"{len(corrupted)} corrupted branches")
        
        # Check overall progress
        progress = self.tikkun_registry.resolution_progress()
        if progress < 0.8:
            issues.append(f"Only {progress:.0%} of Tikkunim resolved")
        
        can_merge = len(issues) == 0
        return can_merge, issues
    
    def wake_dormant_nodes(self) -> int:
        """Wake all dormant nodes using Tekiah Gedolah."""
        self.tekiah.sound()
        return self.tekiah.ping_dormant_nodes(list(self.branches.values()))
    
    def gather_sparks(self) -> Tuple[List[int], float]:
        """
        Gather all valid data fragments (Nitzotzot/Sparks).
        
        Extract valid data from entropic sectors.
        """
        all_sparks = set()
        total_entropy = 0.0
        
        for branch in self.branches.values():
            branch.compute_entropy()
            all_sparks.update(branch.sparks)
            total_entropy += branch.entropy
        
        return list(all_sparks), total_entropy
    
    def resolve_all_conflicts(self) -> int:
        """Resolve all merge conflicts using Hegemonikon."""
        conflicts_resolved = 0
        
        for branch in self.branches.values():
            if branch.state == BranchState.MERGED:
                continue
            
            conflicting_indices = branch.has_conflicts_with(
                Branch(id="temp", name="temp", data=self.master_branch.data)
            )
            
            if conflicting_indices:
                conflict = MergeConflict(
                    branch_id=branch.id,
                    master_id=self.master_branch.id,
                    conflicting_indices=conflicting_indices
                )
                
                self.master_branch.data = self.hegemonikon.resolve_conflict(
                    conflict, branch.data, self.master_branch.data
                )
                conflicts_resolved += 1
        
        return conflicts_resolved
    
    def merge_branch(self, branch_id: str) -> bool:
        """Merge a single branch into master."""
        if branch_id not in self.branches:
            return False
        
        branch = self.branches[branch_id]
        
        if branch.state == BranchState.MERGED:
            return True
        
        if branch.state == BranchState.CORRUPTED:
            return False
        
        # Check for conflicts
        conflicts = branch.has_conflicts_with(
            Branch(id="temp", name="temp", data=self.master_branch.data)
        )
        
        if conflicts:
            # Resolve using Hegemonikon
            conflict = MergeConflict(
                branch_id=branch.id,
                master_id=self.master_branch.id,
                conflicting_indices=conflicts
            )
            self.master_branch.data = self.hegemonikon.resolve_conflict(
                conflict, branch.data, self.master_branch.data
            )
        else:
            # Simple merge: add non-zero values
            non_zero = branch.data != 0
            self.master_branch.data[non_zero] = branch.data[non_zero]
        
        branch.mark_merged()
        return True
    
    def execute_merge_all(self) -> MergeResult:
        """
        Execute the Master Merge - git merge --all.
        
        The terminal integration protocol.
        """
        self.merge_status = MergeStatus.AUDITING
        
        # Step 1: Audit preconditions
        can_merge, issues = self.audit_preconditions()
        if not can_merge:
            return MergeResult(
                status=MergeStatus.FAILED,
                branches_merged=0,
                sparks_gathered=0,
                conflicts_resolved=0,
                entropy_purged=0,
                message=f"Audit failed: {'; '.join(issues)}"
            )
        
        self.merge_status = MergeStatus.IN_PROGRESS
        
        # Step 2: Sound Tekiah Gedolah (wake dormant nodes)
        nodes_awakened = self.wake_dormant_nodes()
        
        # Step 3: Gather sparks
        sparks, initial_entropy = self.gather_sparks()
        
        # Step 4: Resolve conflicts
        conflicts_resolved = self.resolve_all_conflicts()
        
        # Step 5: Merge all branches
        merged_count = 0
        for branch_id in self.branches:
            if self.merge_branch(branch_id):
                merged_count += 1
        
        # Step 6: Calculate purged entropy
        self.master_branch.compute_entropy()
        entropy_purged = initial_entropy - self.master_branch.entropy
        
        self.merge_status = MergeStatus.SUCCESS
        
        result = MergeResult(
            status=MergeStatus.SUCCESS,
            branches_merged=merged_count,
            sparks_gathered=len(sparks),
            conflicts_resolved=conflicts_resolved,
            entropy_purged=entropy_purged,
            final_data=self.master_branch.data.copy(),
            message=f"Merge successful. {merged_count} branches unified. "
                    f"{len(sparks)} sparks gathered. {entropy_purged:.2f} entropy purged."
        )
        
        self.merge_history.append(result)
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete merge system status."""
        return {
            "merge_status": self.merge_status.value,
            "branches": {
                "total": len(self.branches),
                "merged": sum(1 for b in self.branches.values() 
                             if b.state == BranchState.MERGED),
                "dormant": sum(1 for b in self.branches.values()
                              if b.state == BranchState.DORMANT)
            },
            "tikkunim": {
                "total": len(self.tikkun_registry.tikkunim),
                "resolved": sum(1 for t in self.tikkun_registry.tikkunim.values()
                               if t.is_resolved),
                "progress": self.tikkun_registry.resolution_progress()
            },
            "tekiah_sounded": self.tekiah.sounded,
            "conflicts_resolved": len(self.hegemonikon.resolved_conflicts)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_master_merge() -> bool:
    """Validate master merge module."""
    
    # Test Tikkun
    tikkun = Tikkun(id="TK-0001", description="Test repair", severity=5)
    assert not tikkun.is_resolved
    tikkun.resolve("test")
    assert tikkun.is_resolved
    
    # Test TikkunRegistry
    registry = TikkunRegistry()
    t1 = registry.add("Critical issue", severity=9)
    assert t1.is_critical
    assert not registry.all_critical_resolved()
    
    registry.resolve(t1.id)
    assert registry.all_critical_resolved()
    
    # Test Branch
    branch = Branch(id="b1", name="Test", data=np.array([1, 0, 2, 0]))
    assert branch.sparks == [0, 2]
    
    branch2 = Branch(id="b2", name="Test2", data=np.array([0, 1, 0, 3]))
    assert branch.is_compatible_with(branch2)
    
    # Test Hegemonikon
    hege = Hegemonikon()
    conflict = MergeConflict(
        branch_id="b1",
        master_id="master",
        conflicting_indices=[0, 1]
    )
    result = hege.resolve_conflict(
        conflict,
        np.array([1.0, 2.0, 3.0]),
        np.array([0.5, 1.5, 2.5])
    )
    assert conflict.resolved
    
    # Test TekiahGedolah
    tekiah = TekiahGedolah()
    tekiah.sound()
    assert tekiah.sounded
    
    waveform = tekiah.generate_waveform(100)
    assert len(waveform) == 100
    
    # Test MasterMerge
    merge = MasterMerge()
    merge.add_branch("soul_1", np.random.randn(64) * 0.1)
    merge.add_branch("soul_2", np.random.randn(64) * 0.1)
    
    # Add and resolve tikkunim
    t = merge.add_tikkun("Test issue", severity=5)
    merge.tikkun_registry.resolve(t.id)
    
    result = merge.execute_merge_all()
    assert result.status == MergeStatus.SUCCESS
    assert result.branches_merged == 2
    
    status = merge.get_status()
    assert status["merge_status"] == "success"
    
    return True


if __name__ == "__main__":
    print("Validating Master Merge Module...")
    assert validate_master_merge()
    print("✓ Master Merge Module validated")
    
    # Demo
    print("\n--- Master Merge Demo ---")
    merge = MasterMerge()
    
    # Add branches
    for i in range(5):
        merge.add_branch(f"soul_{i}", np.random.randn(64) * 0.1)
    
    # Add some tikkunim
    t1 = merge.add_tikkun("Resolve karma debt", severity=7)
    t2 = merge.add_tikkun("Clear entropic noise", severity=5)
    
    # Resolve them
    merge.tikkun_registry.resolve(t1.id)
    merge.tikkun_registry.resolve(t2.id)
    
    print(f"\nPre-merge status:")
    status = merge.get_status()
    print(f"  Branches: {status['branches']['total']}")
    print(f"  Tikkunim: {status['tikkunim']['total']} ({status['tikkunim']['progress']:.0%} resolved)")
    
    print(f"\nExecuting Master Merge (git merge --all)...")
    result = merge.execute_merge_all()
    
    print(f"\nResult: {result.status.value}")
    print(f"  Branches merged: {result.branches_merged}")
    print(f"  Sparks gathered: {result.sparks_gathered}")
    print(f"  Conflicts resolved: {result.conflicts_resolved}")
    print(f"  Entropy purged: {result.entropy_purged:.2f}")
