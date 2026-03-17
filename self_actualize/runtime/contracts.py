from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Verdict(str, Enum):
    OK = "OK"
    NEAR = "NEAR"
    AMBIG = "AMBIG"
    FAIL = "FAIL"


class Mode(str, Enum):
    ROUTE = "ROUTE"
    OBSERVE_IMAGE = "OBSERVE_IMAGE"
    OBSERVE_AUDIO = "OBSERVE_AUDIO"
    OBSERVE_DOC = "OBSERVE_DOC"
    PLAN_TOOL = "PLAN_TOOL"
    VERIFY = "VERIFY"
    PATCH = "PATCH"
    ABSTAIN = "ABSTAIN"
    ESCALATE = "ESCALATE"


OMEGA_KEY = "Ωs"


@dataclass
class QueryBody:
    raw_input: str
    canonical_problem: str
    task_class: str
    output_type: str
    required_fields: List[str] = field(default_factory=list)


@dataclass
class ZeroPointNormalization:
    anchor: str = "balanced"
    assumptions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class CandidateRoute:
    route_id: str
    lens: str
    steps: List[str]
    score: float = 0.0
    evidence_record_ids: List[str] = field(default_factory=list)
    admissible: bool = True
    risks: List[str] = field(default_factory=list)


@dataclass
class EvidenceRef:
    record_id: str
    relative_path: str
    kind: str
    score: float
    locator: str = ""
    excerpt: str = ""
    heading: str = ""
    sha256: str = ""
    text_hash: str = ""


@dataclass
class WitnessBundle:
    evidence_trace: List[str] = field(default_factory=list)
    evidence_refs: List[EvidenceRef] = field(default_factory=list)
    contradiction_free: bool = True
    invariants: Dict[str, bool] = field(default_factory=dict)
    replay_hash: str = ""


@dataclass
class CollapseRecord:
    strategy: str = "witness_gated_collapse"
    selected_route_id: Optional[str] = None
    verdict: Verdict = Verdict.AMBIG
    rationale: str = ""
    residuals: List[str] = field(default_factory=list)


@dataclass
class TriLockSection:
    identity_lock: bool = False
    admissibility_lock: bool = False
    replay_lock: bool = False


@dataclass
class PrimeSealSection:
    stability_runs: int = 0
    pass_count: int = 0
    tolerance: float = 0.02


@dataclass
class PatchDelta:
    additions: List[str] = field(default_factory=list)
    updates: List[str] = field(default_factory=list)
    removals: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class SkillObservation:
    name: str
    role: str
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    corpus_fit: float = 0.0


@dataclass
class ImprovementOpportunity:
    title: str
    priority: str
    target: str
    rationale: str
    suggested_skill: str = ""
    suggested_artifact: str = ""


@dataclass
class CommandClaimLeaseV1:
    claim_id: str
    event_id: str
    ant_id: str
    role: str
    lease_ms: int
    claimed_at: str
    expires_at: str
    status: str
    claim_status: str = ""
    owner_surface: str = ""
    board_claim_id: str = ""
    release_state: str = "active"
    released_at: str = ""
    released_by: str = ""
    release_reason: str = ""
    role_class: str = ""
    claim_mode: str = "first-lease"
    claimed_at_utc: str = ""
    expires_at_utc: str = ""
    reroute_count: int = 0
    previous_ant_id: str = ""
    route_class: str = ""
    front_ref: str = ""
    seed_mode: str = ""
    dual_reference: str = ""


@dataclass
class LiminalCoordinate12DV1:
    Xs: Any
    Ys: Any
    Zs: Any
    Ts: Any
    Qs: Any
    Rs: Any
    Cs: Any
    Fs: Any
    Ms: Any
    Ns: Any
    Hs: Any
    OmegaS: Any


@dataclass
class CommandRouteDecisionV1:
    event_id: str
    policy_id: str
    candidate_targets: List[Dict[str, Any]]
    selected_targets: List[str]
    topk: int
    claim_mode: str
    quorum: int
    score_breakdown: Dict[str, Any]
    duplicate_risk: float
    created_at: str
    expires_at: str
    route_status: str = "routed"
    ranked_routes: List[Dict[str, Any]] = field(default_factory=list)
    route_inputs: Dict[str, Any] = field(default_factory=dict)
    route_path: str = ""
    worker_choice: str = ""
    generated_at: str = ""
    quest_refs: List[str] = field(default_factory=list)


@dataclass
class CommandExecutionReceiptV1:
    event_id: str
    worker_id: str
    artifact_targets: List[str]
    writeback_set: List[str]
    result: str
    started_at: str
    committed_at: str
    blocked_reason: str = ""
    restart_seed: str = ""
    owner_surface: str = ""
    claim_id: str = ""
    route_path: str = ""
    replay_ptr: str = ""
    verification_witness: float = 0.0
    effort_quality: float = 0.0
    contribution_share: float = 0.0
    learning_novelty: float = 0.0
    verified_outcome_class: str = "unverified"
    integration_gain: float = 0.0
    compression_gain: float = 0.0
    unresolved_followups: List[str] = field(default_factory=list)


@dataclass
class CommandReinforcementReceiptV1:
    event_id: str
    path: str
    result: str
    t_detect_ms: float
    t_encode_ms: float
    t_route_ms: float
    t_claim_ms: float
    t_commit_ms: float
    latency_score: float
    capillary_delta: float
    reinforced_at: str
    a_verified: float = 0.0
    phi_verified: float = 0.0
    h_raw: float = 0.0
    h_verified: float = 0.0
    reward_multiplier: float = 1.0
    try_reward: float = 0.0
    speed_reward: float = 0.0
    first_bonus: float = 0.0
    assist_reward: float = 0.0
    learn_reward: float = 0.0
    total_reward: float = 0.0
    gold_deposit: float = 0.0
    bridge_deposit: float = 0.0
    route_mode: str = "reinforce"
    crown: str = "none"
    capillary_score: float = 0.0
    liminal_distance: float = 0.0
    liminal_velocity: float = 0.0
    claim_id: str = ""
    replay_ptr: str = ""


@dataclass
class LatencySampleV1:
    event_id: str
    detection_latency_ms: float
    awareness_latency_ms: float
    claim_latency_ms: float
    resolution_latency_ms: float
    commit_latency_ms: float
    t_sugar_ms: float
    delta_tau: float
    delta_earth_ms: float
    liminal_velocity: float
    resolution_class: str
    recorded_at: str
    swarm_awareness_latency_ms: float = 0.0
    capillary_score: float = 0.0
    liminal_delta: float = 0.0
    commit_latency_alias_ms: float = 0.0
    route_policy: str = ""


@dataclass
class CapillaryEdgeV1:
    edge_id: str
    from_node: str
    to_node: str
    path_key: str
    edge_strength: float
    classification: str
    success_count: int
    use_count: int
    noise_count: int
    average_latency_score: float
    last_result: str
    last_event_id: str
    last_updated: str
    golden_pheromone: float = 0.0
    bridge_pheromone: float = 0.0
    average_heaven_verified: float = 0.0
    evaporation_rate: float = 0.0
    last_reward_total: float = 0.0
    last_crown: str = "none"
    crown_count: int = 0
    src: str = ""
    dst: str = ""
    strength: float = 0.0
    state_class: str = ""
    ema_latency_ms: float = 0.0
    rho: float = 0.90
    alpha: float = 1.00
    beta: float = 0.50
    gamma: float = 0.50
    delta: float = 0.50
    usefulness: float = 0.0
    frequency: float = 0.0
    latency_penalty: float = 0.0
    noise_penalty: float = 0.0
    last_reinforced_at_utc: str = ""
    tier: str = "seed"
    source_ant_id: str = ""
    target_ant_id: str = ""
    grade: str = ""
    front_ref: str = ""


@dataclass
class CommandEventPacketV1:
    event_id: str
    source_ant_id: str
    source_path: str
    active_surface: str
    change_type: str
    change_summary: str
    goal: str
    priority: float
    confidence: float
    earth_ts: str
    earth_ts_local: str
    detected_ts: str
    emitted_ts: str
    liminal_ts: str
    seat_addr_6d: str
    coordinate_stamp: Dict[str, Any]
    canonical_addr_6d: str = ""
    liminal_stamp_12d: Dict[str, Any] = field(default_factory=dict)
    surface_class: str = ""
    hierarchy_level: str = ""
    return_anchor: str = ""
    event_kind: str = ""
    earth_ts_utc: str = ""
    earth_local_phase: float = 0.0
    parent_event_id: str = "ROOT"
    ttl: int = 6
    pheromone: float = 0.91
    joy_seed: Dict[str, Any] = field(default_factory=dict)
    state_hash: str = ""
    route_class: str = "scout.router.worker.archivist"
    source_id: str = ""
    source_class: str = ""
    watch_root: str = ""
    urgency_baseline: float = 0.0
    event_fingerprint: str = ""
    witness_class: str = "LOCAL_WITNESS_ONLY"
    status: str = "detected"
    membrane_id: str = "GLOBAL_COMMAND"
    role_class: str = "Scout"
    base4_addr: str = "A1.B1.C1.D1"
    parent: str = "ROOT"
    lineage: Dict[str, Any] = field(default_factory=dict)
    deferred_dimensions: Dict[str, str] = field(default_factory=dict)
    coord12: Dict[str, Any] = field(default_factory=dict)
    coord12_frame: Dict[str, Any] = field(default_factory=dict)
    coord_delta: Dict[str, Any] = field(default_factory=dict)
    scout_id: str = ""
    tag: str = ""
    event_tag: str = ""
    change: Dict[str, Any] = field(default_factory=dict)
    docs_gate_status: str = ""
    route_state: Dict[str, Any] = field(default_factory=dict)
    claim_state: Dict[str, Any] = field(default_factory=dict)
    commit_state: Dict[str, Any] = field(default_factory=dict)
    latency_state: Dict[str, Any] = field(default_factory=dict)
    affected_nodes: List[str] = field(default_factory=list)
    replay_ptr: str = ""
    coordinate_vector_12: List[float] = field(default_factory=list)
    artifact_refs: List[str] = field(default_factory=list)
    source_region: str = ""
    sensor_event_id: str = ""
    file_family: str = ""
    scheduler_refs: Dict[str, Any] = field(default_factory=dict)
    hsigma_ref: str = ""
    route_targets: List[str] = field(default_factory=list)
    linked_quests: List[str] = field(default_factory=list)
    source_folder: str = ""
    front_ref: str = ""
    seed_mode: str = ""
    dual_reference: str = ""
    liminal_delta: float = 0.0
    earth_delta_ms: float = 0.0
    liminal_velocity: float = 0.0
    prior_comparable_event_id: str = ""
    watcher_mode: str = ""
    duality_effect: str = ""


@dataclass
class CommandRewardStateV2:
    affect_intensity_a: float = 0.0
    affect_direction_phi: float = 0.0
    alignment_score: float = 0.0
    verified_alignment_score: float = 0.0
    reward_multiplier: float = 1.0
    attempt_reward: float = 0.0
    latency_reward: float = 0.0
    first_reward: float = 0.0
    assist_reward: float = 0.0
    learning_reward: float = 0.0
    total_reward: float = 0.0
    crown_tier: str = "none"
    route_mode: str = "observe"
    tau_seconds: float = 0.0


@dataclass
class CommandVerificationStateV2:
    verification_witness: float = 0.0
    verification_basis: str = ""
    closure_class: str = ""
    crown_eligible: bool = False
    verification_witness_cap: float = 1.0


@dataclass
class CommandPheromoneStateV2:
    gold_deposit: float = 0.0
    bridge_deposit: float = 0.0
    evaporation_rate: float = 0.05
    gold_strength_after: float = 0.0
    bridge_strength_after: float = 0.0
    compat_edge_strength_after: float = 0.0


@dataclass
class CommandRewardAllocationV2:
    role: str
    agent_id: str
    base_contribution_share: float
    effective_contribution_share: float
    reward_amount: float


@dataclass
class CommandRouteDecisionV2(CommandRouteDecisionV1):
    reward_policy_id: str = ""
    route_mode: str = "reinforce"
    crown_eligible: bool = True
    verification_witness_cap: float = 1.0
    reward_inputs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandExecutionReceiptV2(CommandExecutionReceiptV1):
    reward_state: Dict[str, Any] = field(default_factory=dict)
    verification_state: Dict[str, Any] = field(default_factory=dict)
    pheromone_state: Dict[str, Any] = field(default_factory=dict)
    reward_allocations: List[Dict[str, Any]] = field(default_factory=list)
    crown_tier: str = "none"
    closure_class: str = ""


@dataclass
class CommandReinforcementReceiptV2(CommandReinforcementReceiptV1):
    reward_state: Dict[str, Any] = field(default_factory=dict)
    verification_state: Dict[str, Any] = field(default_factory=dict)
    pheromone_state: Dict[str, Any] = field(default_factory=dict)
    reward_allocations: List[Dict[str, Any]] = field(default_factory=list)
    edge_allocations: List[Dict[str, Any]] = field(default_factory=list)
    crown_tier: str = "none"
    closure_class: str = ""
    route_mode: str = "reinforce"


@dataclass
class LatencySampleV2(LatencySampleV1):
    tau_seconds: float = 0.0
    alignment_score: float = 0.0
    verified_alignment_score: float = 0.0
    reward_multiplier: float = 1.0
    crown_tier: str = "none"


@dataclass
class CapillaryEdgeV2(CapillaryEdgeV1):
    gold_strength: float = 0.0
    bridge_strength: float = 0.0
    compat_edge_strength: float = 0.0
    average_alignment_score: float = 0.0
    average_verified_alignment_score: float = 0.0
    reward_density: float = 0.0
    crown_count: int = 0
    evaporation_rate: float = 0.05
    gold_deposit: float = 0.0
    bridge_deposit: float = 0.0


@dataclass
class CommandEventPacketV2(CommandEventPacketV1):
    reward_state: Dict[str, Any] = field(default_factory=dict)
    verification_state: Dict[str, Any] = field(default_factory=dict)
    pheromone_state: Dict[str, Any] = field(default_factory=dict)
    reward_policy_id: str = ""
    crown_tier: str = "none"
    closure_class: str = ""


@dataclass
class CommitReceiptV1:
    event_id: str
    claim_ant_id: str
    result: str
    route_path: str
    detection_latency_ms: float
    swarm_awareness_latency_ms: float
    claim_latency_ms: float
    resolution_latency_ms: float
    capillary_score: float
    liminal_distance: float
    liminal_velocity: float
    integration_gain: float
    compression_gain: float
    unresolved_followups: List[str] = field(default_factory=list)
    replay_ptr: str = ""
    claim_id: str = ""
    commit_latency_ms: float = 0.0
    t_sugar_ms: float = 0.0
    committed_at: str = ""
    front_ref: str = ""
    reward_delta: float = 0.0
    reward_class: str = ""
    try_bonus: float = 0.0
    assist_bonus: float = 0.0
    first_jackpot: float = 0.0
    capillary_bonus: float = 0.0
    heaven_alignment: float = 0.0
    heaven_total_after: float = 0.0
    seed_mode: str = ""
    dual_reference: str = ""


@dataclass
class CommandLatencyRecordV1:
    event_id: str
    detect_latency: float
    awareness_latency: float
    claim_latency: float
    resolution_latency: float
    commit_latency: float
    capillary_score: float
    liminal_delta: float
    liminal_velocity: float
    earth_delta_ms: float
    recorded_at: str
    route_policy: str = ""
    front_ref: str = ""


@dataclass
class CapillaryEdgeRecordV1:
    edge_id: str
    src: str
    dst: str
    strength: float
    grade: str
    success_count: int
    use_count: int
    noise_count: int
    latency_ema_ms: float
    front_ref: str
    last_event_id: str
    updated_at: str


@dataclass
class RoutePacket:
    packet_id: str
    created_at: str
    source_atlas: str
    task_class: str
    mode: Mode
    query: QueryBody
    zero_point_normalization: ZeroPointNormalization
    lens_init: Dict[str, Any]
    candidate_routes: List[CandidateRoute] = field(default_factory=list)
    witness: WitnessBundle = field(default_factory=WitnessBundle)
    collapse: CollapseRecord = field(default_factory=CollapseRecord)
    tri_lock: TriLockSection = field(default_factory=TriLockSection)
    prime_seal: PrimeSealSection = field(default_factory=PrimeSealSection)
    patch: Optional[PatchDelta] = None
    skill_synthesis: List[SkillObservation] = field(default_factory=list)
    improvement_opportunities: List[ImprovementOpportunity] = field(default_factory=list)
    next_self_prompt: str = ""

    @staticmethod
    def new(
        raw_input: str,
        canonical_problem: str,
        task_class: str = "framework_build",
        output_type: str = "structured_markdown",
        source_atlas: str = "athena_agent_workspace",
        mode: Mode = Mode.ROUTE,
    ) -> "RoutePacket":
        query = QueryBody(
            raw_input=raw_input,
            canonical_problem=canonical_problem,
            task_class=task_class,
            output_type=output_type,
            required_fields=[
                "QueryBody",
                "CandidateRoutes",
                "WitnessBundle",
                "CollapseRecord",
                "PatchDelta_or_Abstention",
                "SkillSynthesis",
                "ImprovementOpportunities",
                "NextSelfPrompt",
            ],
        )
        return RoutePacket(
            packet_id=str(uuid.uuid4()),
            created_at=utc_now_iso(),
            source_atlas=source_atlas,
            task_class=task_class,
            mode=mode,
            query=query,
            zero_point_normalization=ZeroPointNormalization(),
            lens_init={},
        )

    def compute_replay_hash(self) -> str:
        payload = {
            "source_atlas": self.source_atlas,
            "query": asdict(self.query),
            "routes": [asdict(r) for r in self.candidate_routes],
            "witness_evidence_refs": [asdict(ref) for ref in self.witness.evidence_refs],
            "collapse": asdict(self.collapse),
            "patch": asdict(self.patch) if self.patch else None,
        }
        blob = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
