from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Literal


TruthType = Literal["OK", "NEAR", "AMBIG", "FAIL"]


def stable_hash(payload: Any) -> str:
    """Deterministic hash for replay signatures and checkpoint ids."""
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


@dataclass
class CandidateHypothesis:
    threshold: float
    predicted_class: int
    confidence: float
    quality: float
    disagreement: float
    edge_agreement: float
    probabilities: list[float]
    mask_mass: float


@dataclass
class BornCoordinate:
    name: str
    residual_norm: float
    support: list[str] = field(default_factory=list)
    bridge_receipt: dict[str, Any] = field(default_factory=dict)
    promoted: bool = False


@dataclass
class LoopActivation:
    loop_id: str
    score: float
    phase_budget: int
    corridor_budget: float
    activation_reason: str


@dataclass
class QuestPacket:
    quest_id: str
    address_a256_b256_c256_d256: str
    objective: str
    target_surfaces: list[str]
    witness_needed: str
    writeback: str
    restart_seed: str
    status: str
    owner_class: str


class MergeState(str, Enum):
    PROPOSED = "PROPOSED"
    BUNDLED = "BUNDLED"
    DISSENT_SURFACED = "DISSENT_SURFACED"
    VERIFY_PENDING = "VERIFY_PENDING"
    GOVERNANCE_PENDING = "GOVERNANCE_PENDING"
    DECIDED_COMMIT = "DECIDED_COMMIT"
    DECIDED_DEFER_NEAR = "DECIDED_DEFER_NEAR"
    DECIDED_DEFER_AMBIG = "DECIDED_DEFER_AMBIG"
    DECIDED_REFUSE = "DECIDED_REFUSE"
    DECIDED_QUARANTINE = "DECIDED_QUARANTINE"


class MergeDestination(str, Enum):
    COMMIT = "COMMIT"
    DEFER_NEAR = "DEFER_NEAR"
    DEFER_AMBIG = "DEFER_AMBIG"
    REFUSE = "REFUSE"
    QUARANTINE_FAIL = "QUARANTINE_FAIL"


class MotionAction(str, Enum):
    ACTIVATE_NOW = "ACTIVATE_NOW"
    HOLD = "HOLD"
    REQUEST_WITNESSES = "REQUEST_WITNESSES"
    REQUEST_HELP = "REQUEST_HELP"
    REPLAY_FIRST = "REPLAY_FIRST"
    QUARANTINE = "QUARANTINE"
    COMPRESS_TO_SEED = "COMPRESS_TO_SEED"
    ESCALATE_TO_COMMITTEE = "ESCALATE_TO_COMMITTEE"
    REFUSE_INADMISSIBLE = "REFUSE_INADMISSIBLE"


class AdventureClass(str, Enum):
    F = "F"
    E = "E"
    D = "D"
    C = "C"
    B = "B"
    A = "A"
    S = "S"


class RewardTransform(str, Enum):
    BASE = "BASE"
    PHI = "PHI"
    DOUBLE_PHI = "DOUBLE_PHI"
    SQUARED = "SQUARED"


class AdventureRunState(str, Enum):
    SPAWN_ZERO = "SPAWN_ZERO"
    OBSERVE = "OBSERVE"
    PLAN = "PLAN"
    WORK = "WORK"
    PRUNE = "PRUNE"
    CLOSED_POSITIVE = "CLOSED_POSITIVE"
    CLOSED_NEUTRAL = "CLOSED_NEUTRAL"
    CLOSED_NEGATIVE = "CLOSED_NEGATIVE"
    PROMOTION_ELIGIBLE = "PROMOTION_ELIGIBLE"
    MINI_HIVE_AUTHORIZED = "MINI_HIVE_AUTHORIZED"


class RunOutcome(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


@dataclass
class CommitteePack:
    committee_pack_id: str
    candidate_delta_refs: list[str]
    dissent_refs: list[str] = field(default_factory=list)
    witness_refs: list[str] = field(default_factory=list)
    replay_refs: list[str] = field(default_factory=list)
    governance_profile: dict[str, Any] = field(default_factory=dict)
    continuation_seed_ref: str = ""
    route_witness_ref: str = ""
    replay_closure_ref: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MotionScoreVector:
    closure_gain: float
    heart_need: float
    replay_readiness: float
    integration_yield: float
    organ_adjacency: float
    seed_value: float
    cost: float
    replay_cost: float
    risk: float
    failure_debt: float
    branch_burden: float
    contradiction_heat: float
    pressure_gradient: float
    truth_readiness: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MotionCandidatePacket:
    candidate_id: str
    source_kind: str
    source_ref: str
    source_organ: str
    target_organ: str
    current_family: str
    truth_burden: str
    expected_packet_type: str
    continuation_seed: str
    agent_id: str = ""
    dependencies: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    witness_refs: list[str] = field(default_factory=list)
    replay_refs: list[str] = field(default_factory=list)
    committee_refs: list[str] = field(default_factory=list)
    assist_agent_ids: list[str] = field(default_factory=list)
    parent_chain_ids: list[str] = field(default_factory=list)
    score_vector: MotionScoreVector = field(
        default_factory=lambda: MotionScoreVector(
            closure_gain=0.0,
            heart_need=0.0,
            replay_readiness=0.0,
            integration_yield=0.0,
            organ_adjacency=0.0,
            seed_value=0.0,
            cost=0.0,
            replay_cost=0.0,
            risk=0.0,
            failure_debt=0.0,
            branch_burden=0.0,
            contradiction_heat=0.0,
            pressure_gradient=0.0,
            truth_readiness=0.0,
        )
    )
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["score_vector"] = self.score_vector.to_dict()
        return payload


@dataclass
class MotionConstitutionState:
    route_graph: dict[str, Any] = field(default_factory=dict)
    pressure_field: dict[str, Any] = field(default_factory=dict)
    legality_projector: dict[str, Any] = field(default_factory=dict)
    immune_state: dict[str, Any] = field(default_factory=dict)
    replay_memory: dict[str, Any] = field(default_factory=dict)
    hysteresis_memory: dict[str, Any] = field(default_factory=dict)
    reward_profiles: dict[str, Any] = field(default_factory=dict)
    docs_gate_status: str = "blocked-by-missing-credentials"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MotionReceipt:
    receipt_id: str
    candidate_id: str
    action: MotionAction
    automaton_trace: list[str]
    constitutional_score: float
    replay_store_update: dict[str, Any]
    successor_seed: str
    residuals: list[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["action"] = self.action.value
        return payload


@dataclass
class MotionDecision:
    candidate_id: str
    action: MotionAction
    constitutional_score: float
    legal: bool
    residuals: list[str] = field(default_factory=list)
    replay_obligations: list[str] = field(default_factory=list)
    successor_seed: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["action"] = self.action.value
        return payload


@dataclass
class AwakeningAgentTransitionNote:
    agent_id: str
    role: str
    current_transition: str
    liminal_band: str
    active_feeder: str
    stabilize_now: str
    do_not_do: str
    immediate_move: str
    writeback_targets: list[str] = field(default_factory=list)
    restart_seed: str = ""
    master_role_assist: str = ""
    cycle_entry_rule: str = ""
    quest_emission_scope: str = ""
    compression_rule: str = ""
    handoff_rule: str = ""
    note_family: str = ""
    profile_class: str = ""
    coordinate_stamp: str = ""
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FullCorpusIntegrationState:
    basis_counts: dict[str, Any]
    overlay_counts: dict[str, Any]
    feeder_truth: dict[str, Any]
    control_plane_state: dict[str, Any]
    docs_gate_status: str
    next_seed: str
    truth: TruthType = "NEAR"
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SwarmSeatProjection:
    seat_id: str
    loop_id: str
    lead_role: str
    macro_mandate: str
    resolution_band: str
    feeder_binding: list[str] = field(default_factory=list)
    activation_state: str = "DORMANT"
    quest_bundle_ref: str = ""
    worker_packet_ref: str = ""
    prune_packet_ref: str = ""
    transition_note_ref: str = ""
    restart_seed: str = ""
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SwarmLoopRecord:
    loop_id: str
    ordinal: int
    tranche: str
    lead_role: str
    macro_mandate: str
    objective: str
    observer_bundle_ref: str
    planner_bundle_ref: str
    worker_bundle_ref: str
    prune_bundle_ref: str
    verification_bundle_ref: str
    transition_note_refs: list[str] = field(default_factory=list)
    restart_seed: str = ""
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SwarmMacroBundleRecord:
    bundle_id: str
    loop_id: str
    surface: str
    lead_role: str
    max_macro_updates: int
    macro_updates: list[str] = field(default_factory=list)
    writeback_targets: list[str] = field(default_factory=list)
    restart_seed: str = ""
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FourAgentSwarmState:
    frontier_id: str
    docs_gate_status: str
    deep_root_authority: str
    feeder_set: list[str]
    master_agents: list[dict[str, Any]]
    loop_counts: dict[str, int]
    macro_caps: dict[str, int]
    lattice_totals: dict[str, int]
    control_plane_state: dict[str, Any]
    next_seed: str
    protocol_id: str = "LP-57OMEGA"
    loop_grouping: list[int] = field(default_factory=lambda: [16, 16, 16, 9])
    subagent_projection: dict[str, Any] = field(default_factory=dict)
    liminal_coordinate_schema: dict[str, Any] = field(default_factory=dict)
    lookup_key_schema: str = ""
    reward_state_ref: str = ""
    class_distribution: dict[str, int] = field(default_factory=dict)
    promotion_queue_ref: str = ""
    top_agents: list[dict[str, Any]] = field(default_factory=list)
    reward_pressure_ref: str = ""
    truth: TruthType = "NEAR"
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PrimeLoopCycleRecord:
    loop_id: str
    phase: str
    lead_agent: str
    dominant_focus: str
    entry_state_ref: str
    observer_bundle_ref: str
    planner_bundle_ref: str
    worker_bundle_ref: str
    prune_bundle_ref: str
    verification_ref: str
    restart_seed: str
    dominant_evidence_class: str = ""
    compression_target: str = ""
    packet_contract: list[str] = field(default_factory=list)
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LiminalCoordinateStamp:
    coordinate_id: str
    agent_id: str
    node_ref: str
    coord_tuple: dict[str, str]
    resolution_scale: str
    feeder_binding: list[str] = field(default_factory=list)
    node_stamp: str = ""
    witness_class: str = ""
    quest_refs: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MasterAgentLedgerEntry:
    agent_id: str
    loop_number: int
    parent_agent: str
    coordinate_stamp: str
    source_region: str
    action_type: str
    affected_nodes: list[str] = field(default_factory=list)
    summary_of_change: str = ""
    reason_for_change: str = ""
    integration_gain: str = ""
    compression_gain: str = ""
    unresolved_followups: list[str] = field(default_factory=list)
    linked_quests: list[str] = field(default_factory=list)
    linked_agents: list[str] = field(default_factory=list)
    revision_confidence: float = 0.0
    timestamp_internal: str = ""
    witness_class: str = ""
    artifact_refs: list[str] = field(default_factory=list)
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QuestEmissionBundle:
    bundle_id: str
    loop_id: str
    zone: str
    quest_count: int
    macro_objective: str
    dependency_edges: list[str] = field(default_factory=list)
    writeback_targets: list[str] = field(default_factory=list)
    packet_type: str = ""
    zone_kind: str = ""
    coordinate_stamp: str = ""
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LoopDeltaReceipt:
    loop_id: str
    structural_gain: str
    mapping_gain: str
    ledger_gain: str
    compression_gain: str
    open_residuals: list[str] = field(default_factory=list)
    next_seed: str = ""
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RewardVector:
    integration_gain: float = 0.0
    compression_gain: float = 0.0
    replay_gain: float = 0.0
    witness_gain: float = 0.0
    route_clarity_gain: float = 0.0
    quest_closure_gain: float = 0.0
    blocker_honesty_gain: float = 0.0
    phi_efficiency_gain: float = 0.0
    regression_loss: float = 0.0
    bloat_loss: float = 0.0
    contradiction_increase: float = 0.0
    orphaned_node_loss: float = 0.0
    replay_break_loss: float = 0.0
    control_surface_drift: float = 0.0
    unauthorized_activation_loss: float = 0.0
    docs_dishonesty_loss: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PhiEfficiencySnapshot:
    snapshot_id: str
    agent_id: str
    scope: str
    loop_id: str
    frontier_id: str
    pre_or_post: str
    reward_vector: RewardVector
    net_efficiency_score: float
    truth: TruthType = "NEAR"
    coordinate_stamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reward_vector"] = self.reward_vector.to_dict()
        return payload


@dataclass
class AgentProgressProfile:
    agent_id: str
    parent_agent_id: str
    master_agent_id: str
    loop_origin: str
    coordinate_stamp: str
    xp_total: int = 0
    level: int = 0
    adventure_class: AdventureClass = AdventureClass.F
    demotion_buffer: int = 0
    run_count: int = 0
    quest_count: int = 0
    success_count: int = 0
    net_positive_count: int = 0
    recent_outcomes: list[str] = field(default_factory=list)
    promotion_state: str = "INELIGIBLE"
    mini_hive_count: int = 0
    linked_agents: list[str] = field(default_factory=list)
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["adventure_class"] = self.adventure_class.value
        return payload


@dataclass
class QuestOutcomeCredit:
    quest_id: str
    loop_id: str
    frontier_id: str
    primary_agent_id: str
    assist_agent_ids: list[str] = field(default_factory=list)
    parent_chain_ids: list[str] = field(default_factory=list)
    reward_transform: RewardTransform = RewardTransform.BASE
    base_xp_delta: int = 0
    final_xp_delta: int = 0
    outcome: RunOutcome = RunOutcome.NEUTRAL
    credit_shares: dict[str, int] = field(default_factory=dict)
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reward_transform"] = self.reward_transform.value
        payload["outcome"] = self.outcome.value
        return payload


@dataclass
class RewardRunEvaluation:
    run_id: str
    scope: str
    loop_id: str
    agent_ids: list[str]
    baseline_snapshot_ref: str
    post_snapshot_ref: str
    reward_vector: RewardVector
    positive_score: float
    negative_score: float
    net_efficiency_score: float
    reward_transform: RewardTransform = RewardTransform.BASE
    xp_delta: int = 0
    outcome: RunOutcome = RunOutcome.NEUTRAL
    residuals: list[str] = field(default_factory=list)
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reward_vector"] = self.reward_vector.to_dict()
        payload["reward_transform"] = self.reward_transform.value
        payload["outcome"] = self.outcome.value
        return payload


@dataclass
class PromotionEligibilityRecord:
    agent_id: str
    level: int
    adventure_class: AdventureClass
    eligible: bool
    requirements: list[str] = field(default_factory=list)
    gating_failures: list[str] = field(default_factory=list)
    promotion_seed: str = ""
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["adventure_class"] = self.adventure_class.value
        return payload


@dataclass
class MiniHiveCharter:
    charter_id: str
    agent_id: str
    promotion_ref: str
    sub_hive_frontier_id: str
    seat_budget: int
    governance_required: bool = True
    merge_required: bool = True
    activation_state: str = "LOCKED"
    truth: TruthType = "NEAR"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DissentPacket:
    dissent_packet_id: str
    committee_pack_id: str
    summary: str
    concerns: list[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WitnessPack:
    witness_pack_id: str
    committee_pack_id: str
    witness_refs: list[str]
    route_witness_ref: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReplayPack:
    replay_pack_id: str
    committee_pack_id: str
    replay_refs: list[str]
    replay_closure_ref: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GovernanceApproval:
    approval_id: str
    committee_pack_id: str
    approved: bool
    approver_refs: list[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContinuationSeed:
    seed_id: str
    next_seed: str
    objective: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MergeLedgerEntry:
    entry_id: str
    committee_pack_ref: str
    chosen_destination: MergeDestination
    supporting_witnesses: list[str]
    replay_bundle_ref: str | None
    governance_approval_ref: str | None
    dissent_refs: list[str]
    continuation_seed_ref: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["chosen_destination"] = self.chosen_destination.value
        return payload


@dataclass
class MergeDecision:
    merge_id: str
    current_state: MergeState
    chosen_destination: MergeDestination | None
    required_artifacts: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)
    next_seed: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["current_state"] = self.current_state.value
        payload["chosen_destination"] = (
            self.chosen_destination.value if self.chosen_destination is not None else None
        )
        return payload


@dataclass
class MergeAttempt:
    merge_id: str
    committee_pack: CommitteePack
    current_state: MergeState = MergeState.PROPOSED
    witness_pack: WitnessPack | None = None
    replay_pack: ReplayPack | None = None
    governance_approval: GovernanceApproval | None = None
    continuation_seed: ContinuationSeed | None = None
    residuals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["current_state"] = self.current_state.value
        return payload


@dataclass
class AthenachkaState:
    corpus: dict[str, Any] = field(default_factory=dict)
    process: dict[str, Any] = field(default_factory=dict)
    growth: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    bridges: dict[str, Any] = field(default_factory=dict)
    replay: dict[str, Any] = field(default_factory=dict)
    phase_index: str = "2/16"
    active_loops: list[str] = field(default_factory=list)
    active_fusions: list[str] = field(default_factory=list)
    checkpoint_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AthenaResult:
    prediction: int | None
    truth_type: TruthType
    confidence: float
    candidate_set: list[dict[str, Any]]
    elemental_state: dict[str, Any]
    symmetry_state: dict[str, Any]
    born_coordinates: list[dict[str, Any]]
    witness_bundle: dict[str, Any]
    corridor_profile: dict[str, Any]
    metric_tensor: dict[str, float]
    replay_signature: str
    lineage_delta: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
