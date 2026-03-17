#!/usr/bin/env python3
"""
LP-57Ω Economic ABI — Typed Schemas

All dataclass definitions for the quest atlas, reward kernel,
board kernel, and sealed receipt bundle system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════

class Truth4(Enum):
    OK = "OK"
    NEAR = "NEAR"
    AMBIG = "AMBIG"
    FAIL = "FAIL"


class Intent(Enum):
    READ = "READ"
    PROVE = "PROVE"
    IMPL = "IMPL"
    PUBLISH = "PUBLISH"
    MIGRATE = "MIGRATE"
    PLAY = "PLAY"
    REWARD = "REWARD"


class Pass3(Enum):
    SULFUR = "Sulfur"
    MERCURY = "Mercury"
    SALT = "Salt"


class Element4(Enum):
    FIRE = "Fire"
    AIR = "Air"
    WATER = "Water"
    EARTH = "Earth"


class QuestClass(Enum):
    # Core classes (KernelConst_v1.json canonical set)
    SOLO = "Solo"
    GUILD = "Guild"
    COMMUNITY = "Community"
    REPAIR = "Repair"
    TEMPLE_RITE = "TempleRite"
    STORM = "Storm"
    CROWN = "Crown"
    CERTIFICATION = "Certification"
    RESONANCE = "Resonance"
    PUBLISH = "Publish"
    SEEDING = "Seeding"
    GOVERNANCE = "Governance"
    POLICY = "Policy"
    MIGRATION = "Migration"
    # Extended classes (used in board_kernel routing)
    EVENT = "Event"
    CONVERGENCE = "Convergence"


class QuestStatus(Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    BLOCKED = "Blocked"
    SEALED = "Sealed"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"


class BoardKind(Enum):
    GUILD = "Guild"
    TEMPLE = "Temple"


class QueueName(Enum):
    FEATURED = "featured"
    LADDER = "ladder"
    REPAIR = "repair"
    STORM = "storm"
    RECRUIT = "recruit"
    OVERFLOW = "overflow"
    CERTIFICATION = "certification"
    NEAR_CLOSURE = "near_closure"
    AMBIGUITIES = "ambiguities"
    COMPRESSION = "compression"
    SOVEREIGN = "sovereign"


class VaultState(Enum):
    LOCKED = "Locked"
    PARTIALLY_RELEASED = "PartiallyReleased"
    RELEASED = "Released"
    BURNED = "Burned"


class StormState(Enum):
    DORMANT = "Dormant"
    SEEDING = "Seeding"
    ACTIVE = "Active"
    SATURATED = "Saturated"
    EXHAUSTED = "Exhausted"


# ═══════════════════════════════════════════════════════════════
# SHARED ABI TYPES
# ═══════════════════════════════════════════════════════════════

Ptr = str        # SHA256Hex content-addressed pointer
GlobalAddr = str  # "Ms⟨....⟩::..."
PolicyID = Ptr
QuestID = Ptr
AgentID = Ptr
Epoch = int


@dataclass
class Vec4:
    """Four-element vector aligned to Fire/Air/Water/Earth."""
    fire: float = 0.0
    air: float = 0.0
    water: float = 0.0
    earth: float = 0.0

    def norm1(self) -> float:
        return abs(self.fire) + abs(self.air) + abs(self.water) + abs(self.earth)

    def normalized(self) -> "Vec4":
        s = self.norm1()
        if s == 0:
            return Vec4()
        return Vec4(self.fire / s, self.air / s, self.water / s, self.earth / s)

    def dot(self, other: "Vec4") -> float:
        return (self.fire * other.fire + self.air * other.air +
                self.water * other.water + self.earth * other.earth)

    def as_tuple(self) -> Tuple[float, float, float, float]:
        return (self.fire, self.air, self.water, self.earth)


@dataclass
class Coord12:
    """12-slot liminal coordinate tuple."""
    Xs: str = ""   # document region
    Ys: str = ""   # concept cluster
    Zs: str = ""   # recursion depth
    Ts: str = ""   # revision layer
    Qs: str = ""   # mathematical density
    Rs: str = ""   # symbolic density
    Cs: str = ""   # compression state
    Fs: str = ""   # framework lens
    Ms: str = ""   # manuscript branch / metro line
    Ns: str = ""   # neural / mycelial connectivity
    Hs: str = ""   # hierarchy level
    Os: str = ""   # zero-point / aether relation (Ωs)


@dataclass
class Corridor:
    """Route corridor constraints."""
    truth: Truth4 = Truth4.AMBIG
    intent: Intent = Intent.READ
    hub_budget: int = 6
    sigma_locked: bool = True
    policy_digests: List[Ptr] = field(default_factory=list)


@dataclass
class TruthRecord:
    """Truth state carrier with obligation-specific fields."""
    truth: Truth4 = Truth4.AMBIG
    obligations: List[Ptr] = field(default_factory=list)
    witness_ptrs: List[Ptr] = field(default_factory=list)
    replay_ptrs: List[Ptr] = field(default_factory=list)
    budgets: List[Ptr] = field(default_factory=list)
    meta: List[Ptr] = field(default_factory=list)
    # NEAR-specific
    residual_ledger: Optional[Ptr] = None
    upgrade_plan: Optional[Ptr] = None
    # AMBIG-specific
    candidate_set: Optional[Ptr] = None
    evidence_plan: Optional[Ptr] = None
    # FAIL-specific
    quarantine_capsule: Optional[Ptr] = None


@dataclass
class LedgerStamp:
    """Agent ledger entry for cumulative tracking."""
    agent_id: AgentID = ""
    loop_number: int = 0
    parent_agent: Optional[AgentID] = None
    coordinate_stamp: Optional[Coord12] = None
    source_region: List[GlobalAddr] = field(default_factory=list)
    action_type: str = ""
    affected_nodes: List[GlobalAddr] = field(default_factory=list)
    summary_of_change: str = ""
    reason_for_change: str = ""
    integration_gain: float = 0.0
    compression_gain: float = 0.0
    unresolved_followups: List[Ptr] = field(default_factory=list)
    linked_quests: List[QuestID] = field(default_factory=list)
    linked_agents: List[AgentID] = field(default_factory=list)
    revision_confidence: float = 0.0
    timestamp_internal: str = ""
    # Extensions
    truth_state: Optional[Truth4] = None
    witness_ref: Optional[Ptr] = None
    replay_ref: Optional[Ptr] = None
    novelty_gain: float = 0.0
    risk_level: float = 0.0
    closure_status: str = ""
    carry_forward_class: str = ""


# ═══════════════════════════════════════════════════════════════
# QUEST OBJECTS
# ═══════════════════════════════════════════════════════════════

@dataclass
class Quest:
    """Base quest object."""
    quest_id: QuestID = ""
    addr: GlobalAddr = ""
    coord12: Optional[Coord12] = None
    ledger_chain: List[Ptr] = field(default_factory=list)
    quest_class: QuestClass = QuestClass.SOLO
    guild_channel: bool = False
    temple_channel: bool = False
    orbit_index: int = 0
    pass3: Pass3 = Pass3.SULFUR
    station19: int = 1
    level_requirement: int = 0
    elemental_signature: Optional[Vec4] = None
    target_set: List[GlobalAddr] = field(default_factory=list)
    dependency_set: List[GlobalAddr] = field(default_factory=list)
    corridor: Optional[Corridor] = None
    truth_record: Optional[TruthRecord] = None
    witness_required: List[Ptr] = field(default_factory=list)
    replay_required: List[Ptr] = field(default_factory=list)
    verifier_required: List[Ptr] = field(default_factory=list)
    reward_policy_id: PolicyID = ""
    pheromone_field_id: Optional[Ptr] = None
    vesting_mode: str = "None"
    status: QuestStatus = QuestStatus.DRAFT


@dataclass
class CommunityQuest(Quest):
    """Quest requiring multi-party coordination."""
    min_party: int = 2
    max_party: int = 8
    quorum: int = 2
    role_slots: Optional[Dict[str, int]] = None
    coalition_cert_ptr: Optional[Ptr] = None
    contribution_root: Optional[Ptr] = None
    cohesion_score: float = 0.0
    diversity_score: float = 0.0
    community_pulse: float = 0.0
    event_pool_share: float = 0.0
    anti_sybil_receipts: List[Ptr] = field(default_factory=list)
    split_policy_id: Optional[Ptr] = None


@dataclass
class TempleRite(Quest):
    """Quest for certification, purity, and corridor law."""
    invariant_set_ptr: List[Ptr] = field(default_factory=list)
    ethics_policy_digest: Optional[Ptr] = None
    consent_receipt_ptrs: List[Ptr] = field(default_factory=list)
    corridor_policy_digest: Optional[Ptr] = None
    validator_suite_ptrs: List[Ptr] = field(default_factory=list)
    grace_weight: float = 0.0
    resonance_weight: float = 0.0
    publish_block_set: List[GlobalAddr] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# STORM / PHEROMONE
# ═══════════════════════════════════════════════════════════════

@dataclass
class PhiStorm:
    """Phi storm event object."""
    storm_id: Ptr = ""
    anchor_addr: GlobalAddr = ""
    coord12: Optional[Coord12] = None
    ledger_chain: List[Ptr] = field(default_factory=list)
    source_field_id: Optional[Ptr] = None
    trigger_epoch: Epoch = 0
    end_epoch: Epoch = 0
    threshold_pos: float = 0.0
    threshold_shadow: float = 0.0
    event_pool: float = 0.0
    difficulty_boost: float = 0.0
    bonus_curve_id: Optional[Ptr] = None
    admission_filter_id: Optional[Ptr] = None
    active: bool = False
    replay_ptr: Optional[Ptr] = None
    witness_ptr: Optional[Ptr] = None


@dataclass
class PheromoneField:
    """Route/quest pheromone field with positive and shadow channels."""
    field_id: Ptr = ""
    anchor_addr: GlobalAddr = ""
    coord12: Optional[Coord12] = None
    ledger_chain: List[Ptr] = field(default_factory=list)
    positive: Optional[Vec4] = None
    shadow: Optional[Vec4] = None
    decay_base: str = "phi_inv"
    last_epoch: Epoch = 0
    storm_threshold: float = 34.0
    shadow_threshold: float = 13.0
    contributor_root: Optional[Ptr] = None
    pulse_score: float = 0.0


# ═══════════════════════════════════════════════════════════════
# REWARD / SETTLEMENT
# ═══════════════════════════════════════════════════════════════

@dataclass
class PoPhiXCapsule:
    """Proof-of-Phi Exchange capsule — the mintable unit."""
    capsule_id: Ptr = ""
    addr: GlobalAddr = ""
    coord12: Optional[Coord12] = None
    ledger_chain: List[Ptr] = field(default_factory=list)
    quest_id: QuestID = ""
    target_addr: GlobalAddr = ""
    route_receipt: Optional[Ptr] = None
    route_edges: List[Ptr] = field(default_factory=list)
    participants: List[AgentID] = field(default_factory=list)
    contribution_weights: Dict[AgentID, float] = field(default_factory=dict)
    truth_record: Optional[TruthRecord] = None
    ethics_receipt_ptr: Optional[Ptr] = None
    consent_receipt_ptrs: List[Ptr] = field(default_factory=list)
    elemental_quality: Optional[Vec4] = None
    difficulty_epoch: Epoch = 0
    load_snapshot: Optional[Ptr] = None
    settled_xp: Dict[AgentID, Vec4] = field(default_factory=dict)
    settled_resonance: Dict[AgentID, float] = field(default_factory=dict)
    settled_mint: Dict[AgentID, float] = field(default_factory=dict)
    settled_vesting: Dict[AgentID, Ptr] = field(default_factory=dict)
    seal_ptr: Optional[Ptr] = None
    replay_ptr: Optional[Ptr] = None
    witness_ptr: Optional[Ptr] = None


@dataclass
class VestingVault:
    """NEAR settlement vesting container."""
    vault_id: Ptr = ""
    owner: AgentID = ""
    coord12: Optional[Coord12] = None
    ledger_chain: List[Ptr] = field(default_factory=list)
    source_capsules: List[Ptr] = field(default_factory=list)
    source_quests: List[QuestID] = field(default_factory=list)
    locked_xp: Optional[Vec4] = None
    locked_resonance: float = 0.0
    locked_mint: float = 0.0
    release_rule_id: Optional[Ptr] = None
    slash_rule_id: Optional[Ptr] = None
    unlock_witness_ptrs: List[Ptr] = field(default_factory=list)
    unlock_replay_ptrs: List[Ptr] = field(default_factory=list)
    state: VaultState = VaultState.LOCKED


@dataclass
class RewardPolicyMIGRATE:
    """Versioned reward policy change object."""
    migrate_id: Ptr = ""
    from_policy_id: PolicyID = ""
    to_policy_id: PolicyID = ""
    effective_epoch: Epoch = 0
    freeze_window_start: Epoch = 0
    freeze_window_end: Epoch = 0
    changed_terms: List[str] = field(default_factory=list)
    reason: str = ""
    impact_digest: Optional[Ptr] = None
    backward_replay_suite: Optional[Ptr] = None
    conversion_map_ptr: Optional[Ptr] = None
    rollback_plan_ptr: Optional[Ptr] = None
    truth_record: Optional[TruthRecord] = None


# ═══════════════════════════════════════════════════════════════
# BOARD CONTAINERS
# ═══════════════════════════════════════════════════════════════

@dataclass
class GuildHallBoard:
    """Guild Hall quest board."""
    board_id: Ptr = ""
    open_quests: List[QuestID] = field(default_factory=list)
    open_community_quests: List[QuestID] = field(default_factory=list)
    active_storms: List[Ptr] = field(default_factory=list)
    sort_key_id: Optional[Ptr] = None
    coord12: Optional[Coord12] = None
    ledger_chain: List[Ptr] = field(default_factory=list)


@dataclass
class TempleRegistry:
    """Temple certification registry."""
    registry_id: Ptr = ""
    open_rites: List[QuestID] = field(default_factory=list)
    certification_queue: List[Ptr] = field(default_factory=list)
    ethics_watchlist: List[GlobalAddr] = field(default_factory=list)
    invariant_backlog: List[Ptr] = field(default_factory=list)
    sort_key_id: Optional[Ptr] = None
    coord12: Optional[Coord12] = None
    ledger_chain: List[Ptr] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# RECEIPT BUNDLE OBJECTS
# ═══════════════════════════════════════════════════════════════

@dataclass
class ClaimPack:
    """Truth-shaped claim container."""
    pack_id: Ptr = ""
    pack_ver: str = "ClaimPack.v1"
    route_profile_id: str = ""
    policy_digest: Ptr = ""
    ms_id: str = ""
    local_addr: str = ""
    global_addr: GlobalAddr = ""
    scope_digest: Ptr = ""
    corridor_digest: Ptr = ""
    truth_record: Optional[TruthRecord] = None
    payload_root: Ptr = ""
    witness_bundle_ref: Optional[Ptr] = None
    replay_bundle_ref: Optional[Ptr] = None
    receipt_registry_ref: Optional[Ptr] = None


@dataclass
class WitnessBundle:
    """Typed witness carrier."""
    bundle_id: Ptr = ""
    bundle_ver: str = "WitnessBundle.v1"
    target_addr: GlobalAddr = ""
    wkind: List[str] = field(default_factory=list)
    claims: List[Ptr] = field(default_factory=list)
    derivations: List[Ptr] = field(default_factory=list)
    aux_data: List[Ptr] = field(default_factory=list)
    discharges: List[Dict[str, Ptr]] = field(default_factory=list)
    witness_digest: Ptr = ""


@dataclass
class ReplayBundle:
    """Deterministic replay carrier."""
    bundle_id: Ptr = ""
    bundle_ver: str = "ReplayBundle.v1"
    target_addr: GlobalAddr = ""
    plan_ref: Optional[Ptr] = None
    inputs_ref: Optional[Ptr] = None
    outputs_ref: Optional[Ptr] = None
    env_fingerprint: Ptr = ""
    logs_ref: Optional[Ptr] = None
    determinism_mode: str = "strict"
    replay_digest: Ptr = ""


@dataclass
class ReceiptEntry:
    """Single receipt in the canonical chain."""
    receipt_type: str = ""
    target_addr: Optional[GlobalAddr] = None
    scope_digest: Optional[Ptr] = None
    source_digest: Ptr = ""
    receipt_digest: Ptr = ""
    receipt_ptr: Optional[Ptr] = None
    feeds_digest: str = ""   # D_replay | D_proof | D_seal | D_rcpt
    phase_rank: int = 0
    type_rank: int = 0


@dataclass
class ReceiptRegistry:
    """Ordered receipt chain."""
    receipt_registry_ver: str = "JointAtlas.v1"
    receipt_entries: List[ReceiptEntry] = field(default_factory=list)
    receipt_chain_root: Ptr = ""


@dataclass
class ReleaseManifest:
    """OK-only release manifest."""
    manifest_ver: str = "ReleaseManifest.v1"
    ok_set_digest: Ptr = ""
    policy_digest: Ptr = ""
    entries: List[Dict[str, str]] = field(default_factory=list)
    manifest_digest: Ptr = ""
    release_id: Ptr = ""


@dataclass
class SealedReceiptBundle:
    """Top-level portable atlas pack."""
    bundle_id: Ptr = ""
    bundle_ver: str = "SealedReceiptBundle.v1"
    route_profile_id: str = ""
    policy_digest: Ptr = ""
    manifest_ref: Optional[Ptr] = None
    digest_root: Ptr = ""
    signatures_ref: Optional[Ptr] = None
    receipt_registry_ref: Optional[Ptr] = None
    claim_packs: List[Ptr] = field(default_factory=list)
    witness_bundles: List[Ptr] = field(default_factory=list)
    replay_bundles: List[Ptr] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# BOARD KERNEL OBJECTS
# ═══════════════════════════════════════════════════════════════

@dataclass
class Candidate:
    """Raw board candidate from planner."""
    candidate_id: str = ""
    station19: int = 1
    pass3: Pass3 = Pass3.SULFUR
    orbit_index: int = 0
    addr: GlobalAddr = ""
    coord12: Optional[Coord12] = None
    origin_kind: str = ""
    quest_class: str = "Solo"  # intentionally str (matches QuestClass.value) for planner flexibility
    target_set: List[str] = field(default_factory=list)
    dependency_set: List[str] = field(default_factory=list)
    truth_estimate: Truth4 = Truth4.AMBIG
    publish_intent: bool = False
    elemental_signature: Optional[Vec4] = None
    pressure: Dict[str, float] = field(default_factory=dict)
    evidence_ptrs: List[str] = field(default_factory=list)
    witness_ptrs: List[str] = field(default_factory=list)
    replay_ptrs: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RouteTicket:
    """Deterministic route compilation result."""
    truth: Truth4
    publish_intent: bool
    hubs: Tuple[str, ...]
    droplog: Tuple[str, ...]
    tunnel_plan: Tuple[str, ...]
    obligations: Tuple[str, ...]
    legal: bool
    mode: str
    overlay: Optional[str]


@dataclass
class BoardEntry:
    """Scored board entry ready for queue assignment."""
    candidate: Candidate
    route: RouteTicket
    board_kind: BoardKind
    score: float
    queue: QueueName
    reason: str = ""


@dataclass
class AgentProfile:
    """Agent capability profile for party matching and seat election."""
    agent_id: AgentID = ""
    guild_rank: int = 0
    temple_seal: int = 0
    element_bias: Optional[Vec4] = None
    replay_quality: float = 0.0
    reciprocity: float = 0.0
    unresolved_critical_ambig: int = 0
    quarantine_active: bool = False
    # Seat election fields (SeatElectionPolicy.json)
    sealed_count: int = 0
    crown_count: int = 0
    witness_count: int = 0
    storm_participation: int = 0
    temple_count: int = 0
    dispute_resolution: int = 0
    policy_contributions: int = 0
