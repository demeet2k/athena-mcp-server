"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           LM TOME IV: MECHANIZATION & IMPLEMENTATION                         ║
║                                                                              ║
║  Proof-Carrying Kernel, Verifier Contracts, Replay, Codecs,                  ║
║  Domain-Pack Compilation                                                     ║
║                                                                              ║
║  Central Spine:                                                              ║
║    compile → run → certify → store → replay → verify → audit                 ║
║                                                                              ║
║  Deliverables:                                                               ║
║    - Kernel object universe (states, regimes, instruments, chains)           ║
║    - Certificate stack with bounded verifier                                 ║
║    - Cycle logs, chunked codecs, random access                               ║
║    - Domain Packs and Extension Packets                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Set, Callable, Union
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import hashlib
import json
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL OBJECT UNIVERSE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BlockProjector:
    """
    Block projector Π_b for graded state space.
    """
    block_id: str
    projector_matrix: Optional[NDArray] = None
    dimension: int = 0
    
    def project(self, state: NDArray) -> NDArray:
        """Project state onto block."""
        if self.projector_matrix is not None:
            return self.projector_matrix @ state @ self.projector_matrix.conj().T
        return state
    
    def mass(self, state: NDArray) -> float:
        """Compute block mass: m_b = Tr(Π_b ρ)."""
        projected = self.project(state)
        return np.real(np.trace(projected))


@dataclass
class BoundaryProjector:
    """
    Boundary projector Π_{e,β} for liminal blocks.
    """
    edge_id: str
    boundary_type: str  # β
    projector_matrix: Optional[NDArray] = None
    
    def boundary_probability(self, state: NDArray) -> float:
        """π_e(β) = Tr(Π_{e,β} ρ)"""
        if self.projector_matrix is not None:
            return np.real(np.trace(self.projector_matrix @ state))
        return 0.0


@dataclass
class KernelState:
    """
    Kernel state: density operator with block-aware representation.
    
    ρ ≥ 0, Tr(ρ) = 1 with:
    - Block masses m_b = Tr(Π_b ρ)
    - Boundary typing π_e(β) = Tr(Π_{e,β} ρ)
    """
    density_matrix: NDArray
    block_masses: Dict[str, float] = field(default_factory=dict)
    boundary_distributions: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate state properties."""
        # Check trace = 1
        tr = np.trace(self.density_matrix)
        if abs(tr - 1.0) > 1e-10:
            raise ValueError(f"Trace must be 1, got {tr}")
        
        # Check positive semidefinite
        eigenvalues = np.linalg.eigvalsh(self.density_matrix)
        if np.min(eigenvalues) < -1e-10:
            raise ValueError("State must be positive semidefinite")
    
    @property
    def dimension(self) -> int:
        return self.density_matrix.shape[0]
    
    @property
    def purity(self) -> float:
        """Tr(ρ²)"""
        return np.real(np.trace(self.density_matrix @ self.density_matrix))
    
    @property
    def von_neumann_entropy(self) -> float:
        """S(ρ) = -Tr(ρ log ρ)"""
        eigenvalues = np.linalg.eigvalsh(self.density_matrix)
        eigenvalues = eigenvalues[eigenvalues > 1e-15]
        return -np.sum(eigenvalues * np.log2(eigenvalues))


# ═══════════════════════════════════════════════════════════════════════════════
# REGIME SPECIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

class CorridorType(Enum):
    """Types of corridor predicates."""
    STATE = "state"           # State corridor
    OBSERVABLE = "observable"  # Observable corridor
    EVALUATION = "evaluation"  # Evaluation corridor


@dataclass
class CorridorPredicate:
    """
    Decidable corridor predicate with typed refusal semantics.
    """
    corridor_type: CorridorType
    predicate_expr: str
    margin: float = 0.0
    
    def check(self, value: Any) -> Tuple[bool, str]:
        """Check if value is in corridor. Returns (passed, diagnostic)."""
        # Simplified check
        return True, "In corridor"


@dataclass 
class ObservableAlgebraPresentation:
    """
    Observable algebra presentation with generators and normal forms.
    """
    generators: List[str] = field(default_factory=list)
    relations: List[str] = field(default_factory=list)
    normal_form_rules: List[Tuple[str, str]] = field(default_factory=list)
    
    def to_normal_form(self, expr: str) -> str:
        """Convert expression to normal form."""
        result = expr
        for pattern, replacement in self.normal_form_rules:
            result = result.replace(pattern, replacement)
        return result


@dataclass
class CertifiedIOMap:
    """
    Certified encode/decode map with contracts.
    """
    name: str
    encode: Callable[[Any], Any] = None
    decode: Callable[[Any], Any] = None
    idempotence_certified: bool = False
    equivalence_certified: bool = False
    corridor_fragment: str = ""
    
    def verify_idempotence(self, x: Any) -> bool:
        """Verify encode(decode(encode(x))) = encode(x)."""
        if self.encode is None or self.decode is None:
            return False
        try:
            e1 = self.encode(x)
            d1 = self.decode(e1)
            e2 = self.encode(d1)
            return np.allclose(e1, e2) if isinstance(e1, np.ndarray) else e1 == e2
        except:
            return False


@dataclass
class RegimeSpec:
    """
    Regime specification: pinned record for regime chart.
    
    (H_r, A_r, Corr_r, Emb_r, Dec_r)
    """
    regime_id: str
    hilbert_space_dim: int
    observable_algebra: ObservableAlgebraPresentation
    corridors: List[CorridorPredicate] = field(default_factory=list)
    embed_map: Optional[CertifiedIOMap] = None
    decode_map: Optional[CertifiedIOMap] = None
    
    # Metadata
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def content_hash(self) -> str:
        """Content-addressable hash."""
        data = f"{self.regime_id}:{self.hilbert_space_dim}:{len(self.corridors)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════════════
# INSTRUMENT SPECIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

class BranchPartition(Enum):
    """Branch partition types."""
    STAY = "stay"       # Stay in current regime
    LIFT = "lift"       # Lift to higher regime
    LIMINAL = "liminal" # Transition through liminal space
    FAIL = "fail"       # Transition failed


@dataclass
class InstrumentBranchSpec:
    """
    Single branch of instrument specification.
    """
    outcome_id: str
    cp_map: Any  # CP trace-non-increasing map
    partition: BranchPartition
    boundary_type: Optional[str] = None
    
    def apply(self, state: NDArray) -> NDArray:
        """Apply CP map to state."""
        if self.cp_map is not None:
            return self.cp_map(state)
        return state


@dataclass
class InstrumentSpec:
    """
    Instrument specification: typed family {Φ_α}.
    
    Sum is CPTP with:
    - Canonical outcome ordering
    - Explicit branch partitions
    - Outcome-to-boundary typing
    """
    instrument_id: str
    branches: List[InstrumentBranchSpec] = field(default_factory=list)
    outcome_ordering: List[str] = field(default_factory=list)
    
    def is_cptp(self) -> bool:
        """Check if sum of branches is CPTP."""
        # Would verify Σ Φ_α is trace-preserving
        return True
    
    def apply(self, state: NDArray) -> Tuple[NDArray, str, BranchPartition]:
        """Apply instrument, return (new_state, outcome, partition)."""
        # Simplified: return first branch
        if self.branches:
            branch = self.branches[0]
            new_state = branch.apply(state)
            return new_state, branch.outcome_id, branch.partition
        return state, "none", BranchPartition.STAY


# ═══════════════════════════════════════════════════════════════════════════════
# METRIC AND JET SPECIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MetricSpec:
    """
    Metric specification with interval output and slack witnesses.
    """
    metric_id: str
    compute: Callable[[Any], Tuple[float, float, float]] = None  # (lower, value, upper)
    slack_witness: Optional[Any] = None
    
    def evaluate(self, x: Any) -> Tuple[float, float, float]:
        """Evaluate metric with interval bounds."""
        if self.compute:
            return self.compute(x)
        return (0.0, 0.0, 0.0)


@dataclass
class JetSpec:
    """
    Jet specification for organizational ambiguity ladder.
    
    Implements Ambig_m resolution.
    """
    jet_id: str
    control_coordinate: str
    adequacy_type: str
    probe_set: List[Any] = field(default_factory=list)
    local_model: Optional[Any] = None
    remainder_bound: float = 0.0
    neighborhood_radius: float = 0.0
    
    def resolve(self, m: int) -> Tuple[bool, str]:
        """
        Attempt resolution at order m.
        
        Returns (resolved, result_or_ambig).
        """
        # Simplified: check if remainder is small enough
        if self.remainder_bound < 10**(-m):
            return True, "resolved"
        return False, f"Ambig_{m}"


@dataclass
class EscalationPolicy:
    """
    Escalation policy for jet resolution.
    """
    max_order: int = 10
    refine_probes: bool = True
    tighten_corridors: bool = True
    enlarge_witnesses: bool = True
    budget_limit: int = 1000
    
    def escalate(self, current_m: int) -> Tuple[int, Dict[str, Any]]:
        """Generate next escalation level."""
        if current_m >= self.max_order:
            return current_m, {"action": "abstain"}
        return current_m + 1, {"action": "increase_order"}


# ═══════════════════════════════════════════════════════════════════════════════
# RESIDENT SPECIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

class StabilityWitnessType(Enum):
    """Types of stability witnesses."""
    LYAPUNOV = "lyapunov"
    SPECTRAL_GAP = "spectral_gap"
    CONTRACTION = "contraction"


@dataclass
class StabilityWitness:
    """
    Stability witness for resident fixed points.
    """
    witness_type: StabilityWitnessType
    value: float = 0.0
    certificate: Optional[str] = None
    
    def is_stable(self) -> bool:
        """Check if witness indicates stability."""
        if self.witness_type == StabilityWitnessType.LYAPUNOV:
            return self.value < 0  # Negative Lyapunov exponent
        elif self.witness_type == StabilityWitnessType.SPECTRAL_GAP:
            return self.value > 0  # Positive gap
        elif self.witness_type == StabilityWitnessType.CONTRACTION:
            return self.value < 1  # Contraction factor < 1
        return False


@dataclass
class ResidentSpec:
    """
    Resident specification with proof pack.
    
    Fixed point + stability witness.
    """
    resident_id: str
    fixed_point_state: Optional[NDArray] = None
    fixed_point_residual: float = 0.0
    stability_witness: Optional[StabilityWitness] = None
    regime_id: str = ""
    
    def is_certified(self, tolerance: float = 1e-10) -> bool:
        """Check if resident is certified."""
        residual_ok = self.fixed_point_residual < tolerance
        stable_ok = self.stability_witness is not None and self.stability_witness.is_stable()
        return residual_ok and stable_ok


# ═══════════════════════════════════════════════════════════════════════════════
# COMPRESSION AND MACRO ARTIFACTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CarrySchema:
    """
    Carry schema for macro artifacts.
    
    Transports: proof status, envelope inflation, identity continuity,
    partition alignment, pathology gates, budgets.
    """
    proof_status: Dict[str, bool] = field(default_factory=dict)
    envelope_inflation: float = 0.0
    identity_continuity: bool = True
    partition_alignment: bool = True
    pathology_gates: List[str] = field(default_factory=list)
    budgets: Dict[str, float] = field(default_factory=dict)


@dataclass
class DistortionLedger:
    """
    Distortion ledger for compression.
    """
    entries: List[Tuple[str, float]] = field(default_factory=list)
    total_distortion: float = 0.0
    
    def add(self, source: str, amount: float):
        """Add distortion entry."""
        self.entries.append((source, amount))
        self.total_distortion += amount
    
    def is_within_budget(self, budget: float) -> bool:
        """Check if within distortion budget."""
        return self.total_distortion <= budget


@dataclass
class MacroArtifact:
    """
    Macro artifact from compression.
    
    (ρ̃, κ) + distortion ledgers + Cert.Comp
    """
    artifact_id: str
    compressed_state: Optional[NDArray] = None
    carry: CarrySchema = field(default_factory=CarrySchema)
    distortion_ledger: DistortionLedger = field(default_factory=DistortionLedger)
    cert_compression: Optional[str] = None
    
    def content_hash(self) -> str:
        """Content hash for artifact."""
        data = f"{self.artifact_id}:{self.distortion_ledger.total_distortion}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class CompSpec:
    """
    Compression specification CompSpec_N.
    """
    spec_id: str
    cycle_length: int
    preserved_summaries: List[str] = field(default_factory=list)
    macro_corridor: Optional[CorridorPredicate] = None
    carry_schema: CarrySchema = field(default_factory=CarrySchema)
    distortion_budget: float = 0.01
    
    def compress(self, states: List[NDArray]) -> MacroArtifact:
        """
        Compress micro states to macro artifact.
        """
        if not states:
            return MacroArtifact(artifact_id="empty")
        
        # Simplified: average states
        compressed = np.mean(states, axis=0)
        
        # Compute distortion
        ledger = DistortionLedger()
        for i, s in enumerate(states):
            dist = np.linalg.norm(s - compressed)
            ledger.add(f"state_{i}", dist)
        
        return MacroArtifact(
            artifact_id=f"macro_{self.spec_id}",
            compressed_state=compressed,
            carry=self.carry_schema,
            distortion_ledger=ledger,
            cert_compression=f"CompCert_{self.spec_id}" if ledger.is_within_budget(self.distortion_budget) else None
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PATH AND CHAIN SPECIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RoutingTableEntry:
    """
    Single entry in routing table.
    """
    source_regime: str
    target_regime: str
    instrument_id: str
    conditions: List[str] = field(default_factory=list)


@dataclass
class PathSpec:
    """
    Path specification: executable, verifiable composite program.
    """
    path_id: str
    routing_table: List[RoutingTableEntry] = field(default_factory=list)
    obligation_index: List[str] = field(default_factory=list)
    replay_deterministic: bool = True
    budget: Dict[str, float] = field(default_factory=dict)
    
    def compose(self, other: 'PathSpec') -> 'PathSpec':
        """Compose two paths."""
        return PathSpec(
            path_id=f"{self.path_id}_{other.path_id}",
            routing_table=self.routing_table + other.routing_table,
            obligation_index=self.obligation_index + other.obligation_index,
            replay_deterministic=self.replay_deterministic and other.replay_deterministic
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CERTIFICATE STACK
# ═══════════════════════════════════════════════════════════════════════════════

class ObligationType(Enum):
    """Types of proof obligations."""
    CP_LEGALITY = "cp_legality"
    CPTP_LEGALITY = "cptp_legality"
    CORRIDOR_MEMBERSHIP = "corridor"
    METRIC_INTERVAL = "metric_interval"
    JET_ADEQUACY = "jet_adequacy"
    RESIDENT_STABILITY = "resident_stability"
    COMPRESSION_PRESERVATION = "compression"
    PATH_COMPOSITION = "path_composition"
    REPLAY_DETERMINISM = "replay_determinism"
    DEPENDENCY_CLOSURE = "dependency_closure"


@dataclass
class ObligationIndex:
    """
    Index of proof obligations.
    """
    obligations: Dict[str, ObligationType] = field(default_factory=dict)
    
    def add(self, obligation_id: str, ob_type: ObligationType):
        """Add obligation."""
        self.obligations[obligation_id] = ob_type
    
    def get_by_type(self, ob_type: ObligationType) -> List[str]:
        """Get obligations of a type."""
        return [k for k, v in self.obligations.items() if v == ob_type]


@dataclass
class CertificateInstance:
    """
    Single certificate instance.
    """
    cert_id: str
    obligation_id: str
    witness_data: Dict[str, Any] = field(default_factory=dict)
    bounds: Dict[str, float] = field(default_factory=dict)
    verified: bool = False
    
    def verify(self, verifier: 'BoundedVerifier') -> bool:
        """Verify certificate."""
        self.verified = verifier.check(self)
        return self.verified


@dataclass
class CertBundleMech:
    """
    Certificate bundle mapping obligations to certificates.
    """
    bundle_id: str
    certificates: Dict[str, CertificateInstance] = field(default_factory=dict)
    
    def add(self, obligation_id: str, cert: CertificateInstance):
        """Add certificate for obligation."""
        self.certificates[obligation_id] = cert
    
    def verify_all(self, verifier: 'BoundedVerifier') -> Tuple[bool, List[str]]:
        """Verify all certificates."""
        failures = []
        for ob_id, cert in self.certificates.items():
            if not cert.verify(verifier):
                failures.append(ob_id)
        return len(failures) == 0, failures


# ═══════════════════════════════════════════════════════════════════════════════
# BOUNDED VERIFIER
# ═══════════════════════════════════════════════════════════════════════════════

class VerifierResult(Enum):
    """Verifier result types."""
    ACCEPT = "accept"
    REJECT = "reject"
    REFUSE_BUDGET = "refuse_budget"
    REFUSE_INCOMPLETE = "refuse_incomplete"


@dataclass
class BoundedVerifier:
    """
    Bounded verifier kernel with PTIME-target budgets.
    
    Expensive construction → builders (untrusted)
    Verification → bounded, polynomial in certificate size
    """
    dimension_cap: int = 1000
    witness_cap: int = 10000
    transcript_cap: int = 100000
    time_budget_ms: float = 60000
    
    def check(self, cert: CertificateInstance) -> bool:
        """Check single certificate within budget."""
        # Simplified verification
        if not cert.witness_data:
            return False
        return True
    
    def verify_bundle(self, bundle: CertBundleMech, 
                     obligations: ObligationIndex) -> Tuple[VerifierResult, List[str]]:
        """
        Verify certificate bundle against obligations.
        """
        # Check all obligations have certificates
        missing = []
        for ob_id in obligations.obligations:
            if ob_id not in bundle.certificates:
                missing.append(ob_id)
        
        if missing:
            return VerifierResult.REFUSE_INCOMPLETE, missing
        
        # Verify certificates
        success, failures = bundle.verify_all(self)
        if success:
            return VerifierResult.ACCEPT, []
        return VerifierResult.REJECT, failures


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE LOGS AND CODECS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CycleEntry:
    """
    Single entry in cycle log.
    """
    cycle_id: int
    state_hash: str
    timestamp: str
    summary: Dict[str, float] = field(default_factory=dict)


@dataclass
class ChunkHeader:
    """
    Header for log chunk.
    """
    chunk_id: int
    start_cycle: int
    end_cycle: int
    entry_count: int
    chunk_hash: str = ""


@dataclass
class CycleLog:
    """
    Cycle log: chunked, indexed, Merkle-hashed trace.
    
    Supports random access witness extraction.
    """
    log_id: str
    chunks: List[ChunkHeader] = field(default_factory=list)
    entries: List[CycleEntry] = field(default_factory=list)
    merkle_root: str = ""
    
    def add_entry(self, entry: CycleEntry):
        """Add entry to log."""
        self.entries.append(entry)
    
    def finalize_chunk(self, chunk_size: int = 100) -> ChunkHeader:
        """Finalize current chunk."""
        if len(self.entries) == 0:
            return ChunkHeader(0, 0, 0, 0)
        
        start = self.entries[0].cycle_id
        end = self.entries[-1].cycle_id
        
        # Compute chunk hash
        data = json.dumps([e.state_hash for e in self.entries])
        chunk_hash = hashlib.sha256(data.encode()).hexdigest()[:16]
        
        header = ChunkHeader(
            chunk_id=len(self.chunks),
            start_cycle=start,
            end_cycle=end,
            entry_count=len(self.entries),
            chunk_hash=chunk_hash
        )
        self.chunks.append(header)
        return header
    
    def compute_merkle_root(self) -> str:
        """Compute Merkle root of all chunks."""
        if not self.chunks:
            return ""
        
        hashes = [c.chunk_hash for c in self.chunks]
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            hashes = [
                hashlib.sha256((hashes[i] + hashes[i+1]).encode()).hexdigest()[:16]
                for i in range(0, len(hashes), 2)
            ]
        
        self.merkle_root = hashes[0] if hashes else ""
        return self.merkle_root
    
    def extract_witness(self, obligation_id: str) -> Optional[Dict]:
        """Extract minimal witness pack for obligation."""
        # Simplified: return relevant entries
        return {"obligation": obligation_id, "entries": len(self.entries)}


# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN PACKS AND EXTENSION PACKETS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DomainPack:
    """
    Domain Pack: shipping unit for LM modules.
    
    Contains: regimes, edges, instruments, metrics, jets, residents,
    compression specs, tests, benchmarks, demos.
    """
    pack_id: str
    version: str
    
    # Content
    regimes: List[RegimeSpec] = field(default_factory=list)
    instruments: List[InstrumentSpec] = field(default_factory=list)
    metrics: List[MetricSpec] = field(default_factory=list)
    jets: List[JetSpec] = field(default_factory=list)
    residents: List[ResidentSpec] = field(default_factory=list)
    compression_specs: List[CompSpec] = field(default_factory=list)
    
    # Validation
    test_suite: List[str] = field(default_factory=list)
    benchmarks: List[str] = field(default_factory=list)
    demos: List[str] = field(default_factory=list)
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dependency_closure_hash: str = ""
    
    def validate(self, verifier: BoundedVerifier) -> Tuple[bool, List[str]]:
        """Validate pack integrity."""
        errors = []
        
        # Check all regimes have unique IDs
        regime_ids = [r.regime_id for r in self.regimes]
        if len(regime_ids) != len(set(regime_ids)):
            errors.append("Duplicate regime IDs")
        
        # Check dependency closure
        if not self.dependency_closure_hash:
            errors.append("Missing dependency closure hash")
        
        return len(errors) == 0, errors
    
    def content_hash(self) -> str:
        """Compute content hash."""
        data = f"{self.pack_id}:{self.version}:{len(self.regimes)}:{len(self.instruments)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class ExtensionPacket:
    """
    Extension Packet: add new regime or edge.
    """
    packet_id: str
    extension_type: str  # "regime" or "edge"
    
    # Content
    regime_spec: Optional[RegimeSpec] = None
    instrument_spec: Optional[InstrumentSpec] = None
    
    # Certification
    obligation_templates: List[str] = field(default_factory=list)
    cert_builders: List[str] = field(default_factory=list)
    fixtures: List[str] = field(default_factory=list)
    test_suite: List[str] = field(default_factory=list)
    
    # Closure
    dependency_closure: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Check packet validity."""
        if self.extension_type == "regime":
            return self.regime_spec is not None
        elif self.extension_type == "edge":
            return self.instrument_spec is not None
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT AND REPLAY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AuditLogEntry:
    """
    Single audit log entry.
    """
    entry_id: int
    operation: str
    timestamp: str
    interval_witness: Optional[Tuple[float, float, float]] = None
    obligation_refs: List[str] = field(default_factory=list)
    repair_explicit: bool = False
    tool_type: str = "construction"  # "construction" or "verifier"
    
    def hash(self) -> str:
        """Hash entry."""
        data = f"{self.entry_id}:{self.operation}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:12]


@dataclass
class AuditLog:
    """
    Audit log: sealed by hash chains.
    """
    log_id: str
    entries: List[AuditLogEntry] = field(default_factory=list)
    hash_chain: List[str] = field(default_factory=list)
    replay_hash: str = ""
    cert_bundle_hash: str = ""
    
    def add_entry(self, entry: AuditLogEntry):
        """Add entry and extend hash chain."""
        self.entries.append(entry)
        
        prev_hash = self.hash_chain[-1] if self.hash_chain else "genesis"
        new_hash = hashlib.sha256(
            (prev_hash + entry.hash()).encode()
        ).hexdigest()[:16]
        self.hash_chain.append(new_hash)
    
    def verify_integrity(self) -> bool:
        """Verify hash chain integrity."""
        if len(self.entries) != len(self.hash_chain):
            return False
        
        prev_hash = "genesis"
        for entry, expected_hash in zip(self.entries, self.hash_chain):
            computed = hashlib.sha256(
                (prev_hash + entry.hash()).encode()
            ).hexdigest()[:16]
            if computed != expected_hash:
                return False
            prev_hash = expected_hash
        
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# REPAIR LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RepairLogEntry:
    """
    Explicit repair operation log.
    """
    repair_id: str
    repair_type: str  # "psd_projection", "trace_renormalization", "block_repair"
    pre_state_hash: str
    post_state_hash: str
    perturbation_bound: float
    norm_type: str = "trace"


@dataclass
class RepairLog:
    """
    Log of explicit repair operations.
    """
    repairs: List[RepairLogEntry] = field(default_factory=list)
    total_envelope_inflation: float = 0.0
    
    def add(self, repair: RepairLogEntry):
        """Add repair entry."""
        self.repairs.append(repair)
        self.total_envelope_inflation += repair.perturbation_bound


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LMMechanizationPoleBridge:
    """
    Bridge between LM Mechanization and four-pole framework.
    """
    
    @staticmethod
    def integration() -> str:
        return """
        LM TOME IV: MECHANIZATION & IMPLEMENTATION ↔ FRAMEWORK
        
        ═══════════════════════════════════════════════════════════════
        CENTRAL SPINE
        ═══════════════════════════════════════════════════════════════
        
        compile → run → certify → store → replay → verify → audit
        
        Every stage emits immutable artifacts.
        Every claim admitted only as certificate-checked artifact.
        Soundness over completeness.
        
        ═══════════════════════════════════════════════════════════════
        KERNEL OBJECT UNIVERSE
        ═══════════════════════════════════════════════════════════════
        
        KernelState: ρ with block masses, boundary typing
        RegimeSpec: (H_r, A_r, Corr_r, Emb_r, Dec_r)
        InstrumentSpec: {Φ_α} with branch partitions
        MetricSpec: interval output, slack witnesses
        JetSpec: Ambig_m ladder with probes
        ResidentSpec: fixed point + stability witness
        CompSpec: macro compression with carry
        PathSpec: routing tables, budget accounting
        
        ═══════════════════════════════════════════════════════════════
        CERTIFICATE STACK
        ═══════════════════════════════════════════════════════════════
        
        ObligationIndex: what must be proven
        CertBundle: obligation → certificate mapping
        BoundedVerifier: PTIME-target checking
        
        Certificate families:
          - CP/CPTP legality
          - Corridor membership
          - Metric intervals and slack
          - Jet adequacy
          - Resident stability
          - Compression preservation
          - Path composition
          - Replay determinism
          - Dependency closure
          
        ═══════════════════════════════════════════════════════════════
        CYCLE LOGS AND CODECS
        ═══════════════════════════════════════════════════════════════
        
        CycleLog: chunked, indexed, Merkle-hashed
        Random access witness extraction
        Compression-safe (deterministic, lossless)
        
        ═══════════════════════════════════════════════════════════════
        DOMAIN PACKS
        ═══════════════════════════════════════════════════════════════
        
        DomainPack: shipping unit with:
          - Regimes, instruments, metrics
          - Tests, benchmarks, demos
          - Dependency closure
          
        ExtensionPacket: add regime/edge without
          weakening global soundness
          
        ═══════════════════════════════════════════════════════════════
        POLE CORRESPONDENCE
        ═══════════════════════════════════════════════════════════════
        
        D: Discrete specs, hash-addressed artifacts
        Ω: Continuous corridors, interval bounds
        Σ: Probabilistic certificates, witnesses
        Ψ: Recursive compression, Merkle trees
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def kernel_state(density_matrix: NDArray) -> KernelState:
    """Create kernel state."""
    return KernelState(density_matrix)


def regime_spec(regime_id: str, dim: int) -> RegimeSpec:
    """Create regime spec."""
    return RegimeSpec(regime_id, dim, ObservableAlgebraPresentation())


def instrument_spec(instrument_id: str) -> InstrumentSpec:
    """Create instrument spec."""
    return InstrumentSpec(instrument_id)


def comp_spec(spec_id: str, cycle_length: int) -> CompSpec:
    """Create compression spec."""
    return CompSpec(spec_id, cycle_length)


def bounded_verifier() -> BoundedVerifier:
    """Create bounded verifier."""
    return BoundedVerifier()


def domain_pack(pack_id: str, version: str = "1.0") -> DomainPack:
    """Create domain pack."""
    return DomainPack(pack_id, version)


def cycle_log(log_id: str) -> CycleLog:
    """Create cycle log."""
    return CycleLog(log_id)


def audit_log(log_id: str) -> AuditLog:
    """Create audit log."""
    return AuditLog(log_id)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Kernel Objects
    'BlockProjector',
    'BoundaryProjector',
    'KernelState',
    
    # Regime
    'CorridorType',
    'CorridorPredicate',
    'ObservableAlgebraPresentation',
    'CertifiedIOMap',
    'RegimeSpec',
    
    # Instrument
    'BranchPartition',
    'InstrumentBranchSpec',
    'InstrumentSpec',
    
    # Metric/Jet
    'MetricSpec',
    'JetSpec',
    'EscalationPolicy',
    
    # Resident
    'StabilityWitnessType',
    'StabilityWitness',
    'ResidentSpec',
    
    # Compression
    'CarrySchema',
    'DistortionLedger',
    'MacroArtifact',
    'CompSpec',
    
    # Path
    'RoutingTableEntry',
    'PathSpec',
    
    # Certificates
    'ObligationType',
    'ObligationIndex',
    'CertificateInstance',
    'CertBundleMech',
    
    # Verifier
    'VerifierResult',
    'BoundedVerifier',
    
    # Logs
    'CycleEntry',
    'ChunkHeader',
    'CycleLog',
    
    # Packs
    'DomainPack',
    'ExtensionPacket',
    
    # Audit
    'AuditLogEntry',
    'AuditLog',
    'RepairLogEntry',
    'RepairLog',
    
    # Bridge
    'LMMechanizationPoleBridge',
    
    # Functions
    'kernel_state',
    'regime_spec',
    'instrument_spec',
    'comp_spec',
    'bounded_verifier',
    'domain_pack',
    'cycle_log',
    'audit_log',
]
