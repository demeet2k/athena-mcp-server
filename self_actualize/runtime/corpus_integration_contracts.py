from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any


class DeploymentState(str, Enum):
    ACTIVE = "active"
    GATED = "gated"
    BLOCKED = "blocked"


class RuntimeLane(str, Enum):
    OFFLINE_REPLAY = "offline_replay"
    INTERNAL_PREVIEW = "internal_preview"
    PUBLIC_RELEASE = "public_release"
    FEDERATION_RELEASE = "federation_release"
    LIVE_AUTONOMOUS = "live_autonomous"


class MonitorDecision(str, Enum):
    SUSTAIN = "sustain"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"
    BLOCK = "block"


class RegionClass(str, Enum):
    LIVE_AUTHORITY = "live_authority"
    MIRROR = "mirror"
    ARCHIVE_BACKED = "archive_backed"
    EXPERIMENTAL = "experimental"
    RESIDUAL = "residual"


class ReceiptClass(str, Enum):
    REPLAY = "replay_receipt"
    MONITOR = "monitor_receipt"
    PROMOTION = "promotion_ledger"
    BLOCKED = "blocked_notice"


OBJECT_FAMILY = [
    "CorpusIntegrationWave",
    "DeploymentMonitoringSurface",
    "DeploymentProfile",
    "RuntimeLane",
    "ActivationGate",
    "ObservabilitySurface",
    "MonitoringProbe",
    "AlertPolicy",
    "HealthWindow",
    "RollbackTrigger",
    "EscalationRoute",
    "ExecutionReceipt",
    "DeploymentMonitorResult",
    "AwakeningAgentProfile",
    "TransitionSupportNote",
    "RegionLaneAssignment",
    "IntegrationMonitorResult",
]

DEPLOYMENT_POLICY_MAP = {
    RuntimeLane.OFFLINE_REPLAY.value: DeploymentState.ACTIVE,
    RuntimeLane.INTERNAL_PREVIEW.value: DeploymentState.ACTIVE,
    RuntimeLane.PUBLIC_RELEASE.value: DeploymentState.GATED,
    RuntimeLane.FEDERATION_RELEASE.value: DeploymentState.GATED,
    RuntimeLane.LIVE_AUTONOMOUS.value: DeploymentState.BLOCKED,
}

WHOLE_WAVE_DATAFLOW = (
    "CorpusRegion -> AgentOwner -> MotionGate -> RouteTable -> SemanticEmbassy -> "
    "DeploymentProfile -> Monitoring -> Receipt -> Dashboard -> Seed/Promote"
)


def serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize(item) for item in value]
    return value


def stable_json(value: Any) -> str:
    return json.dumps(serialize(value), indent=2, sort_keys=True)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


@dataclass
class MonitoringProbe:
    probe_id: str
    signal: str
    cadence: str
    success_condition: str


@dataclass
class AlertPolicy:
    policy_id: str
    drift_rule: str
    silence_rule: str
    contradiction_rule: str
    overload_rule: str
    replay_failure_rule: str


@dataclass
class HealthWindow:
    window_id: str
    expected_cadence: str
    observation_window: str
    failure_threshold: str


@dataclass
class RollbackTrigger:
    trigger_id: str
    trigger_condition: str
    rollback_target: str


@dataclass
class EscalationRoute:
    route_id: str
    source_lane: str
    destination: str
    reason: str


@dataclass
class ActivationGate:
    gate_id: str
    route_required: bool
    replay_required: bool
    semantic_pass_required: bool
    federation_terms_required: bool
    docs_gate_required_ready: bool


@dataclass
class ObservabilitySurface:
    surface_id: str
    probes: list[MonitoringProbe]
    alert_policy: AlertPolicy
    health_window: HealthWindow


@dataclass
class DeploymentProfile:
    lane: str
    status: DeploymentState
    audience: str
    activation_gate: ActivationGate
    observability_surface: ObservabilitySurface
    rollback_trigger: RollbackTrigger
    escalation_route: EscalationRoute
    notes: list[str]


@dataclass
class ExecutionReceipt:
    receipt_id: str
    source_packet: str
    route_receipt: str
    semantic_validation_ref: str
    deployment_lane: str
    emitted_state: str


@dataclass
class DeploymentMonitorResult:
    result_id: str
    decision: MonitorDecision
    reasons: list[str]
    receipt_ref: str
    next_seed: str


@dataclass
class TransitionSupportNote:
    note_id: str
    profile_id: str
    transition_burden: str
    support_note: str
    writeback_surface: str
    escalation_target: str


@dataclass
class AwakeningAgentProfile:
    profile_id: str
    layer: str
    display_name: str
    role_class: str
    transition_burden: str
    responsibilities: list[str]
    handoff_targets: list[str]
    contraction_target: str


@dataclass
class RegionLaneAssignment:
    region_name: str
    region_class: RegionClass
    owner_profile_id: str
    runtime_lane: str
    receipt_class: ReceiptClass
    authority_surface: str
    status_note: str


@dataclass
class IntegrationMonitorResult:
    result_id: str
    route_ok: bool
    semantic_ok: bool
    deployment_ok: bool
    monitor_decision: MonitorDecision
    blocked_reasons: list[str]


@dataclass
class DeploymentMonitoringSurface:
    surface_id: str
    docs_gate_status: str
    deployment_profiles: list[DeploymentProfile]
    policy_hash: str
    route_basis: list[str]
    whole_wave_dataflow: str


@dataclass
class CorpusIntegrationWave:
    wave_id: str
    transition_label: str
    truth_class: str
    zero_point: str
    success_criterion: str
    docs_gate_status: str
    authority_surfaces: list[str]
    object_family: list[str]
    region_assignments: list[RegionLaneAssignment]
    agent_profiles: list[AwakeningAgentProfile]
    transition_support_notes: list[TransitionSupportNote]
    deployment_surface: DeploymentMonitoringSurface
    passing_receipt: ExecutionReceipt
    passing_monitor_result: DeploymentMonitorResult
