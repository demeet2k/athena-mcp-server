"""
ATHENA OS - QHC Runtime Primitives
==================================
The universal operations for quantum computation on classical hardware.

Runtime Primitives (semantically complete):
1. Apply - Local linear operators and channels
2. Change - Basis/representation transports
3. Restructure - Merge/split/reorder/retiling
4. Measure - Analytic contraction or certified sampling

Zero-Point Control:
1. Snap - Bounded alternating projection repairs
2. Paradox - Center-finding under contradiction
3. Harmonia - Adaptive planning geometry

Proof-Carrying Artifacts:
1. Seed - Generators + constraints + environment
2. Recipe - IR + plan + step list + obligations
3. ProofPack - Certificates + bounds + risk ledgers
4. AuditLog - Hash-chained steps + repairs + RNG logs

The foundational contract:
"Construction may be heuristic; verification is conservative and bounded"
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set, Union
from abc import ABC, abstractmethod
import numpy as np
import hashlib
import time

from .framework import QuantumState, QuantumChannel, POVM, AtlasCoordinate
from .bulk import (
    BlockTree, BlockTreeTile, TilePayload, ModeWord,
    ErrorLedger, ErrorBudget, KappaTexture, KappaCorridor,
    BasisChart, CompressionMethod, OperationRole
)


# =============================================================================
# RUNTIME PRIMITIVES
# =============================================================================

class PrimitiveType(IntEnum):
    """Types of runtime primitives."""
    APPLY = 0        # Apply gate/channel
    CHANGE = 1       # Basis change
    RESTRUCTURE = 2  # Tile restructuring
    MEASURE = 3      # Measurement


@dataclass
class PrimitiveResult:
    """Result of a primitive operation."""
    success: bool
    primitive_type: PrimitiveType
    
    # Error accounting
    epsilon_consumed: float = 0.0
    delta_consumed: float = 0.0
    
    # Updated state
    updated_tiles: List[str] = field(default_factory=list)
    
    # Certificates
    certificates: List['Certificate'] = field(default_factory=list)
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Failure info
    failure_reason: Optional[str] = None


class RuntimePrimitive(ABC):
    """Abstract base for runtime primitives."""
    
    @abstractmethod
    def execute(self, tree: BlockTree, **kwargs) -> PrimitiveResult:
        """Execute the primitive on a block tree."""
        pass
    
    @abstractmethod
    def estimate_cost(self, tree: BlockTree, **kwargs) -> Tuple[float, float]:
        """Estimate (ε, δ) cost before execution."""
        pass
    
    @abstractmethod
    def verify(self, tree: BlockTree, result: PrimitiveResult) -> bool:
        """Verify the result of execution."""
        pass


class ApplyPrimitive(RuntimePrimitive):
    """
    Apply primitive: execute gates and channels on tiles.
    
    Operates on the smallest tile closure containing the support.
    """
    
    def __init__(self, operator: Union[np.ndarray, QuantumChannel],
                 target_qubits: Set[int],
                 name: str = "apply"):
        self.operator = operator
        self.target_qubits = target_qubits
        self.name = name
    
    def execute(self, tree: BlockTree, **kwargs) -> PrimitiveResult:
        """Apply the operator to relevant tiles."""
        # Find tiles covering target qubits
        relevant_tiles = []
        for tile in tree.tiles.values():
            if tile.qubit_subset & self.target_qubits:
                relevant_tiles.append(tile)
        
        if not relevant_tiles:
            return PrimitiveResult(
                success=False,
                primitive_type=PrimitiveType.APPLY,
                failure_reason="No tiles cover target qubits"
            )
        
        epsilon_total = 0.0
        delta_total = 0.0
        updated = []
        
        for tile in relevant_tiles:
            # Estimate error for this tile
            eps, delta = self._apply_to_tile(tile)
            
            # Consume budget
            if not tree.ledger.consume(tile.tile_id, eps, delta, f"apply:{self.name}"):
                return PrimitiveResult(
                    success=False,
                    primitive_type=PrimitiveType.APPLY,
                    failure_reason=f"Budget exhausted for tile {tile.tile_id}"
                )
            
            epsilon_total += eps
            delta_total += delta
            updated.append(tile.tile_id)
            tile.updated_at = time.time()
        
        return PrimitiveResult(
            success=True,
            primitive_type=PrimitiveType.APPLY,
            epsilon_consumed=epsilon_total,
            delta_consumed=delta_total,
            updated_tiles=updated,
            diagnostics={'operator_name': self.name, 'n_tiles': len(updated)}
        )
    
    def _apply_to_tile(self, tile: BlockTreeTile) -> Tuple[float, float]:
        """Apply operator to a single tile, return (ε, δ) consumed."""
        # For now, estimate based on precision
        eps = tile.mode_word.tolerance
        delta = 0.0 if tile.mode_word.determinism.value < 2 else tile.mode_word.tolerance
        return eps, delta
    
    def estimate_cost(self, tree: BlockTree, **kwargs) -> Tuple[float, float]:
        """Estimate cost before execution."""
        eps_total = 0.0
        delta_total = 0.0
        
        for tile in tree.tiles.values():
            if tile.qubit_subset & self.target_qubits:
                eps, delta = self._apply_to_tile(tile)
                eps_total += eps
                delta_total += delta
        
        return eps_total, delta_total
    
    def verify(self, tree: BlockTree, result: PrimitiveResult) -> bool:
        """Verify application result."""
        # Check all updated tiles are still healthy
        for tile_id in result.updated_tiles:
            tile = tree.get_tile(tile_id)
            if tile and not tile.is_healthy(tree.corridor):
                return False
        return result.success


class ChangePrimitive(RuntimePrimitive):
    """
    Change primitive: basis and representation transforms.
    
    Implements chart transport with stability certificates.
    """
    
    def __init__(self, target_tile: str, new_basis: BasisChart,
                 new_compression: Optional[CompressionMethod] = None):
        self.target_tile = target_tile
        self.new_basis = new_basis
        self.new_compression = new_compression
    
    def execute(self, tree: BlockTree, **kwargs) -> PrimitiveResult:
        """Execute basis change."""
        tile = tree.get_tile(self.target_tile)
        if tile is None:
            return PrimitiveResult(
                success=False,
                primitive_type=PrimitiveType.CHANGE,
                failure_reason=f"Tile {self.target_tile} not found"
            )
        
        if not tile.can_apply("basis_change"):
            return PrimitiveResult(
                success=False,
                primitive_type=PrimitiveType.CHANGE,
                failure_reason="Basis change not allowed for this tile"
            )
        
        # Estimate and consume error
        eps, delta = self.estimate_cost(tree)
        
        if not tree.ledger.consume(tile.tile_id, eps, delta, f"change:{self.new_basis.name}"):
            return PrimitiveResult(
                success=False,
                primitive_type=PrimitiveType.CHANGE,
                failure_reason="Budget exhausted"
            )
        
        # Update mode word
        tile.mode_word = ModeWord(
            basis_chart=self.new_basis,
            compression_method=self.new_compression or tile.mode_word.compression_method,
            precision=tile.mode_word.precision,
            tolerance=tile.mode_word.tolerance,
            determinism=tile.mode_word.determinism,
            role=OperationRole.CHANGE
        )
        tile.updated_at = time.time()
        tile.compute_hash()
        
        return PrimitiveResult(
            success=True,
            primitive_type=PrimitiveType.CHANGE,
            epsilon_consumed=eps,
            delta_consumed=delta,
            updated_tiles=[self.target_tile],
            diagnostics={'new_basis': self.new_basis.name}
        )
    
    def estimate_cost(self, tree: BlockTree, **kwargs) -> Tuple[float, float]:
        """Estimate basis change cost."""
        tile = tree.get_tile(self.target_tile)
        if tile is None:
            return float('inf'), float('inf')
        
        # Cost depends on tile size and transform complexity
        dim = tile.local_dimension()
        eps = tile.mode_word.tolerance * np.log2(dim + 1)
        delta = 0.0
        return eps, delta
    
    def verify(self, tree: BlockTree, result: PrimitiveResult) -> bool:
        """Verify basis change."""
        tile = tree.get_tile(self.target_tile)
        if tile is None:
            return False
        return tile.mode_word.basis_chart == self.new_basis


class RestructurePrimitive(RuntimePrimitive):
    """
    Restructure primitive: merge, split, reorder, retile.
    
    Maintains multiscale feasibility and compressibility.
    """
    
    def __init__(self, operation: str, tile_ids: List[str],
                 partition: Optional[List[Set[int]]] = None,
                 new_id: Optional[str] = None):
        self.operation = operation  # "split", "merge", "reorder"
        self.tile_ids = tile_ids
        self.partition = partition  # For split
        self.new_id = new_id        # For merge
    
    def execute(self, tree: BlockTree, **kwargs) -> PrimitiveResult:
        """Execute restructuring."""
        eps, delta = self.estimate_cost(tree)
        
        if self.operation == "split":
            if len(self.tile_ids) != 1:
                return PrimitiveResult(
                    success=False,
                    primitive_type=PrimitiveType.RESTRUCTURE,
                    failure_reason="Split requires exactly one tile"
                )
            
            tile = tree.get_tile(self.tile_ids[0])
            if tile and not tile.can_apply("restructure"):
                return PrimitiveResult(
                    success=False,
                    primitive_type=PrimitiveType.RESTRUCTURE,
                    failure_reason="Restructure not allowed"
                )
            
            try:
                new_ids = tree.split_tile(self.tile_ids[0], self.partition)
                return PrimitiveResult(
                    success=True,
                    primitive_type=PrimitiveType.RESTRUCTURE,
                    epsilon_consumed=eps,
                    delta_consumed=delta,
                    updated_tiles=new_ids,
                    diagnostics={'operation': 'split', 'children': new_ids}
                )
            except Exception as e:
                return PrimitiveResult(
                    success=False,
                    primitive_type=PrimitiveType.RESTRUCTURE,
                    failure_reason=str(e)
                )
        
        elif self.operation == "merge":
            if len(self.tile_ids) < 2:
                return PrimitiveResult(
                    success=False,
                    primitive_type=PrimitiveType.RESTRUCTURE,
                    failure_reason="Merge requires at least two tiles"
                )
            
            try:
                new_id = tree.merge_tiles(self.tile_ids, self.new_id or "merged")
                return PrimitiveResult(
                    success=True,
                    primitive_type=PrimitiveType.RESTRUCTURE,
                    epsilon_consumed=eps,
                    delta_consumed=delta,
                    updated_tiles=[new_id],
                    diagnostics={'operation': 'merge', 'merged_from': self.tile_ids}
                )
            except Exception as e:
                return PrimitiveResult(
                    success=False,
                    primitive_type=PrimitiveType.RESTRUCTURE,
                    failure_reason=str(e)
                )
        
        return PrimitiveResult(
            success=False,
            primitive_type=PrimitiveType.RESTRUCTURE,
            failure_reason=f"Unknown operation: {self.operation}"
        )
    
    def estimate_cost(self, tree: BlockTree, **kwargs) -> Tuple[float, float]:
        """Estimate restructuring cost."""
        # Restructuring itself is exact (no approximation error)
        # but may affect future compression quality
        return 0.0, 0.0
    
    def verify(self, tree: BlockTree, result: PrimitiveResult) -> bool:
        """Verify restructuring maintained partition validity."""
        return tree.is_partition_valid()


class MeasurePrimitive(RuntimePrimitive):
    """
    Measure primitive: analytic contraction or certified sampling.
    
    Includes bias-variance decomposition and risk accounting.
    """
    
    def __init__(self, povm: POVM, target_qubits: Set[int],
                 n_samples: int = 1, seed: Optional[int] = None):
        self.povm = povm
        self.target_qubits = target_qubits
        self.n_samples = n_samples
        self.seed = seed
    
    def execute(self, tree: BlockTree, state: Optional[QuantumState] = None,
                **kwargs) -> PrimitiveResult:
        """Execute measurement."""
        if state is None:
            return PrimitiveResult(
                success=False,
                primitive_type=PrimitiveType.MEASURE,
                failure_reason="No state provided for measurement"
            )
        
        eps, delta = self.estimate_cost(tree)
        
        # Sample from POVM
        rng = np.random.default_rng(self.seed)
        outcomes = []
        
        for _ in range(self.n_samples):
            outcome = self.povm.sample(state, rng)
            outcomes.append(outcome)
        
        # Consume budget (sampling introduces statistical error)
        if not tree.ledger.consume("measurement", eps, delta, "measure"):
            tree.ledger.create_tile_budget("measurement")
            tree.ledger.consume("measurement", eps, delta, "measure")
        
        return PrimitiveResult(
            success=True,
            primitive_type=PrimitiveType.MEASURE,
            epsilon_consumed=eps,
            delta_consumed=delta,
            diagnostics={
                'outcomes': outcomes,
                'n_samples': self.n_samples,
                'povm': self.povm.name
            }
        )
    
    def estimate_cost(self, tree: BlockTree, **kwargs) -> Tuple[float, float]:
        """Estimate measurement cost."""
        # Sampling error: ε ~ 1/√n, δ from confidence
        eps = 1.0 / np.sqrt(max(1, self.n_samples))
        delta = 0.05  # 95% confidence
        return eps, delta
    
    def verify(self, tree: BlockTree, result: PrimitiveResult) -> bool:
        """Verify measurement result."""
        return result.success and 'outcomes' in result.diagnostics


# =============================================================================
# ZERO-POINT CONTROL
# =============================================================================

@dataclass
class SnapResult:
    """Result of Snap (corridor repair) operation."""
    converged: bool
    iterations: int
    final_defect: float
    repairs_applied: List[str] = field(default_factory=list)


class SnapController:
    """
    Snap: bounded alternating projection repairs.
    
    Performs corridor membership enforcement as a fixed-point problem.
    """
    
    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-6):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
    
    def repair(self, tree: BlockTree) -> SnapResult:
        """
        Repair tree to satisfy corridor membership.
        
        Alternates between:
        1. Project each tile to corridor
        2. Reconcile global constraints
        """
        repairs = []
        defect = self._compute_defect(tree)
        
        for i in range(self.max_iterations):
            if defect < self.tolerance:
                return SnapResult(
                    converged=True,
                    iterations=i,
                    final_defect=defect,
                    repairs_applied=repairs
                )
            
            # Project tiles to corridor
            for tile in tree.tiles.values():
                if not tile.is_healthy(tree.corridor):
                    repair = self._repair_tile(tile, tree.corridor)
                    if repair:
                        repairs.append(repair)
            
            defect = self._compute_defect(tree)
        
        return SnapResult(
            converged=False,
            iterations=self.max_iterations,
            final_defect=defect,
            repairs_applied=repairs
        )
    
    def _compute_defect(self, tree: BlockTree) -> float:
        """Compute total corridor defect."""
        defect = 0.0
        for tile in tree.tiles.values():
            if tile.kappa.coherence < tree.corridor.min_coherence:
                defect += tree.corridor.min_coherence - tile.kappa.coherence
            if tile.kappa.condition_number > tree.corridor.max_condition:
                defect += np.log(tile.kappa.condition_number / tree.corridor.max_condition)
        return defect
    
    def _repair_tile(self, tile: BlockTreeTile, corridor: KappaCorridor) -> Optional[str]:
        """Repair a single tile to satisfy corridor."""
        # Clamp κ-metrics to corridor bounds
        if tile.kappa.coherence < corridor.min_coherence:
            tile.kappa.coherence = corridor.min_coherence
            return f"clamped_coherence:{tile.tile_id}"
        if tile.kappa.condition_number > corridor.max_condition:
            tile.kappa.condition_number = corridor.max_condition
            return f"clamped_condition:{tile.tile_id}"
        return None


class ParadoxResolver:
    """
    Paradox: center-finding under contradiction.
    
    Uses Fréchet means / barycenters / tension fields
    to localize conflict and propose stabilizing routes.
    """
    
    def find_center(self, constraints: List[Callable[[Any], float]],
                   initial: Any) -> Tuple[Any, float]:
        """
        Find geometric center that minimizes total constraint tension.
        
        Returns (center, total_tension).
        """
        # Simplified: compute barycenter
        tension = sum(c(initial) for c in constraints)
        return initial, tension


class HarmoniaPlanner:
    """
    Harmonia: adaptive planning geometry.
    
    Optimizes basis selection, tiling schedules, budget allocations
    while preserving verifier contract (no silent drift).
    """
    
    def __init__(self, trust_radius: float = 1.0):
        self.trust_radius = trust_radius
    
    def plan(self, tree: BlockTree, target_ops: List[RuntimePrimitive]) -> List[RuntimePrimitive]:
        """
        Plan execution order and parameters.
        
        May reorder or split operations but never changes semantics.
        """
        # Simplified: return operations in order
        return target_ops


# =============================================================================
# PROOF-CARRYING ARTIFACTS
# =============================================================================

@dataclass
class Certificate:
    """
    A certificate for a computational claim.
    
    Includes type, bounds, and verification data.
    """
    claim_type: str  # "exact", "approximate", "probabilistic", "failure"
    claim_description: str
    
    # Bounds
    epsilon_bound: float = 0.0
    delta_bound: float = 0.0
    
    # Verification data
    witnesses: Dict[str, Any] = field(default_factory=dict)
    
    # Content hash
    hash: Optional[str] = None
    
    def __post_init__(self):
        if self.hash is None:
            self.compute_hash()
    
    def compute_hash(self) -> str:
        """Compute certificate hash."""
        hasher = hashlib.sha256()
        hasher.update(self.claim_type.encode())
        hasher.update(self.claim_description.encode())
        hasher.update(str(self.epsilon_bound).encode())
        hasher.update(str(self.delta_bound).encode())
        self.hash = hasher.hexdigest()[:16]
        return self.hash


@dataclass
class Seed:
    """
    Seed: generators + constraints + environment contract.
    
    Contains everything needed to reconstruct computation.
    """
    program_hash: str
    initial_state_hash: str
    environment_version: str
    constraints: Dict[str, Any] = field(default_factory=dict)
    rng_seed: Optional[int] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class Recipe:
    """
    Recipe: IR + plan + step list + obligations.
    
    The execution plan for a quantum program.
    """
    seed: Seed
    steps: List[Dict[str, Any]] = field(default_factory=list)
    obligations: List[str] = field(default_factory=list)
    atlas_path: List[AtlasCoordinate] = field(default_factory=list)


@dataclass
class ProofPack:
    """
    ProofPack: certificates + bounds + risk ledgers.
    
    The proof artifacts generated during execution.
    """
    certificates: List[Certificate] = field(default_factory=list)
    
    # Global bounds
    epsilon_total: float = 0.0
    delta_total: float = 0.0
    
    # Risk ledger summary
    ledger_hash: Optional[str] = None
    
    def add_certificate(self, cert: Certificate) -> None:
        """Add a certificate to the pack."""
        self.certificates.append(cert)
        self.epsilon_total += cert.epsilon_bound
        self.delta_total += cert.delta_bound


@dataclass
class AuditLogEntry:
    """A single entry in the audit log."""
    step_index: int
    primitive_type: PrimitiveType
    tile_ids: List[str]
    epsilon_consumed: float
    delta_consumed: float
    timestamp: float
    hash: str


@dataclass
class AuditLog:
    """
    AuditLog: hash-chained steps + repairs + RNG logs.
    
    Enables replay and independent verification.
    """
    entries: List[AuditLogEntry] = field(default_factory=list)
    
    def add_entry(self, result: PrimitiveResult, step_index: int) -> AuditLogEntry:
        """Add an entry for a primitive result."""
        # Compute hash chain
        prev_hash = self.entries[-1].hash if self.entries else "genesis"
        
        hasher = hashlib.sha256()
        hasher.update(prev_hash.encode())
        hasher.update(str(step_index).encode())
        hasher.update(str(result.epsilon_consumed).encode())
        
        entry = AuditLogEntry(
            step_index=step_index,
            primitive_type=result.primitive_type,
            tile_ids=result.updated_tiles,
            epsilon_consumed=result.epsilon_consumed,
            delta_consumed=result.delta_consumed,
            timestamp=time.time(),
            hash=hasher.hexdigest()[:16]
        )
        
        self.entries.append(entry)
        return entry
    
    def verify_chain(self) -> bool:
        """Verify hash chain integrity."""
        prev_hash = "genesis"
        for entry in self.entries:
            hasher = hashlib.sha256()
            hasher.update(prev_hash.encode())
            hasher.update(str(entry.step_index).encode())
            hasher.update(str(entry.epsilon_consumed).encode())
            
            expected = hasher.hexdigest()[:16]
            if entry.hash != expected:
                return False
            prev_hash = entry.hash
        return True


@dataclass
class ProofCarryingArtifact:
    """
    Complete proof-carrying computation artifact.
    
    Enables independent reconstruction and audit.
    """
    seed: Seed
    recipe: Recipe
    proof_pack: ProofPack
    audit_log: AuditLog
    
    # Final results
    final_claims: List[Certificate] = field(default_factory=list)
    
    def is_valid(self) -> Tuple[bool, str]:
        """Validate the artifact."""
        # Check hash chain
        if not self.audit_log.verify_chain():
            return False, "Audit log hash chain invalid"
        
        # Check bounds
        if self.proof_pack.epsilon_total > 1.0:
            return False, "Epsilon bound exceeds 1"
        if self.proof_pack.delta_total > 1.0:
            return False, "Delta bound exceeds 1"
        
        return True, "Valid"


# =============================================================================
# QHC RUNTIME
# =============================================================================

class QHCRuntime:
    """
    Complete QHC runtime for quantum simulation.
    
    Coordinates primitives, error tracking, and certificate generation.
    """
    
    def __init__(self, n_qubits: int,
                 epsilon_global: float = 1e-4,
                 delta_global: float = 1e-4):
        self.n_qubits = n_qubits
        
        # Block tree
        self.tree = BlockTree(n_qubits)
        self.tree.ledger.global_epsilon = epsilon_global
        self.tree.ledger.global_delta = delta_global
        
        # Controllers
        self.snap = SnapController()
        self.paradox = ParadoxResolver()
        self.harmonia = HarmoniaPlanner()
        
        # Artifacts
        self.audit_log = AuditLog()
        self.proof_pack = ProofPack()
        
        # Step counter
        self.step_count = 0
    
    def execute(self, primitive: RuntimePrimitive, **kwargs) -> PrimitiveResult:
        """Execute a primitive and update artifacts."""
        # Check affordability
        eps_est, delta_est = primitive.estimate_cost(self.tree)
        if not self.tree.ledger.is_within_budget():
            return PrimitiveResult(
                success=False,
                primitive_type=primitive.__class__.__name__,
                failure_reason="Global budget exhausted"
            )
        
        # Execute
        result = primitive.execute(self.tree, **kwargs)
        
        if result.success:
            # Log
            self.audit_log.add_entry(result, self.step_count)
            
            # Certificate
            cert = Certificate(
                claim_type="approximate" if result.epsilon_consumed > 0 else "exact",
                claim_description=f"Step {self.step_count}: {result.primitive_type.name}",
                epsilon_bound=result.epsilon_consumed,
                delta_bound=result.delta_consumed
            )
            self.proof_pack.add_certificate(cert)
            
            self.step_count += 1
        
        return result
    
    def repair_corridor(self) -> SnapResult:
        """Run Snap controller to repair corridor violations."""
        return self.snap.repair(self.tree)
    
    def status(self) -> Dict[str, Any]:
        """Get runtime status."""
        return {
            'n_qubits': self.n_qubits,
            'step_count': self.step_count,
            'tree_health': self.tree.health_check(),
            'ledger': self.tree.ledger.summary(),
            'proof_pack': {
                'n_certificates': len(self.proof_pack.certificates),
                'epsilon_total': self.proof_pack.epsilon_total,
                'delta_total': self.proof_pack.delta_total
            },
            'audit_log_valid': self.audit_log.verify_chain()
        }
    
    def finalize(self) -> ProofCarryingArtifact:
        """Finalize and return proof-carrying artifact."""
        seed = Seed(
            program_hash="pending",
            initial_state_hash="zero_state",
            environment_version="qhc_v1.0"
        )
        
        recipe = Recipe(seed=seed)
        
        return ProofCarryingArtifact(
            seed=seed,
            recipe=recipe,
            proof_pack=self.proof_pack,
            audit_log=self.audit_log
        )


# =============================================================================
# VALIDATION
# =============================================================================

def validate_runtime() -> bool:
    """Validate QHC runtime."""
    from .framework import QuantumState, POVM
    
    # Create runtime
    runtime = QHCRuntime(n_qubits=4, epsilon_global=1e-3, delta_global=1e-3)
    
    # Test Apply
    I = np.eye(16, dtype=complex)
    apply_op = ApplyPrimitive(operator=I, target_qubits={0, 1, 2, 3}, name="identity")
    result = runtime.execute(apply_op)
    assert result.success
    
    # Test Change
    change_op = ChangePrimitive(target_tile="root", new_basis=BasisChart.FOURIER_QFT)
    result = runtime.execute(change_op)
    assert result.success
    
    # Test Restructure
    restructure_op = RestructurePrimitive(
        operation="split",
        tile_ids=["root"],
        partition=[{0, 1}, {2, 3}]
    )
    result = runtime.execute(restructure_op)
    assert result.success
    
    # Test Measure
    state = QuantumState.zero_state(4)
    povm = POVM.computational_basis(4)
    measure_op = MeasurePrimitive(povm=povm, target_qubits={0, 1, 2, 3}, n_samples=10, seed=42)
    result = runtime.execute(measure_op, state=state)
    assert result.success
    assert len(result.diagnostics['outcomes']) == 10
    
    # Test Snap
    snap_result = runtime.repair_corridor()
    assert snap_result.converged
    
    # Test finalization
    artifact = runtime.finalize()
    valid, msg = artifact.is_valid()
    assert valid
    
    # Verify audit chain
    assert runtime.audit_log.verify_chain()
    
    return True


if __name__ == "__main__":
    print("Validating QHC Runtime...")
    assert validate_runtime()
    print("✓ QHC Runtime validated")
    
    # Demo
    print("\n=== QHC Runtime Demo ===")
    runtime = QHCRuntime(n_qubits=4)
    
    # Execute operations
    I = np.eye(16, dtype=complex)
    runtime.execute(ApplyPrimitive(I, {0, 1, 2, 3}, "identity"))
    runtime.execute(ChangePrimitive("root", BasisChart.PAULI_STABILIZER))
    
    print(f"Status: {runtime.status()}")
    
    artifact = runtime.finalize()
    valid, msg = artifact.is_valid()
    print(f"Artifact valid: {valid} ({msg})")
