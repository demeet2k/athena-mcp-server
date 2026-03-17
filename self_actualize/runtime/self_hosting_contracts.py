from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class SelfSurfaceLink:
    surface_id: str
    path: str
    surface_class: str
    witness_class: str
    self_bearing: bool
    updates: List[str] = field(default_factory=list)
    note: str = ""


@dataclass
class SelfModelRecord:
    generated_at: str
    derivation_version: str
    docs_gate: str
    governing_equation: str
    coverage: Dict[str, Any]
    capability_map: List[Dict[str, str]] = field(default_factory=list)
    limitation_map: List[Dict[str, str]] = field(default_factory=list)
    burden_map: List[Dict[str, str]] = field(default_factory=list)
    permission_map: List[Dict[str, str]] = field(default_factory=list)
    environment_fit_map: List[Dict[str, str]] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    surface_links: List[SelfSurfaceLink] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ModeLedgerEntry:
    mode: str
    status: str
    witness_class: str
    note: str = ""


@dataclass
class SelfStateRecord:
    generated_at: str
    derivation_version: str
    docs_gate: str
    kernel_status: str
    current_config: Dict[str, Any]
    active_policy: List[str] = field(default_factory=list)
    mode_ledger: List[ModeLedgerEntry] = field(default_factory=list)
    checkpoint_protocol: Dict[str, Any] = field(default_factory=dict)
    restart_protocol: Dict[str, Any] = field(default_factory=dict)
    volatile_memory: Dict[str, Any] = field(default_factory=dict)
    route_context: Dict[str, Any] = field(default_factory=dict)
    truth_citations: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SelfContractRecord:
    generated_at: str
    derivation_version: str
    docs_gate: str
    identity_kernel: List[Dict[str, str]] = field(default_factory=list)
    permitted_transform_classes: List[Dict[str, str]] = field(default_factory=list)
    forbidden_transform_classes: List[Dict[str, str]] = field(default_factory=list)
    required_review_classes: List[Dict[str, str]] = field(default_factory=list)
    transform_classifier: List[Dict[str, str]] = field(default_factory=list)
    unsafe_rewrite_gate: Dict[str, Any] = field(default_factory=dict)
    identity_drift_corridor: Dict[str, Any] = field(default_factory=dict)
    rollback_corridor: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LineageEntry:
    lineage_id: str
    temporal_coordinate: str
    branch_coordinate: str
    delta_class: str
    delta_summary: str
    support_shell: str
    burden_state: str
    proof_state: str
    attached_tunnels: List[str] = field(default_factory=list)


@dataclass
class SelfLineageRecord:
    generated_at: str
    derivation_version: str
    docs_gate: str
    current_branch: str
    predecessor_chain: List[str] = field(default_factory=list)
    lineage_entries: List[LineageEntry] = field(default_factory=list)
    fork_points: List[Dict[str, str]] = field(default_factory=list)
    sufficiency_checks: Dict[str, bool] = field(default_factory=dict)
    comparison_tool: List[Dict[str, str]] = field(default_factory=list)
    drift_band: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeScriptLane:
    script: str
    lane: str
    supports: List[str] = field(default_factory=list)
    note: str = ""


@dataclass
class SelfTransformPacket:
    packet_id: str
    mode: str
    title: str
    source_state: str
    intended_transform_class: str
    contract_status: str
    review_class: str
    lineage_delta: str
    replay_target: str
    publication_target: str
    witness_class: str
    dispatch_score: float
    status: str
    note: str = ""


@dataclass
class DualEngineTarget:
    target_id: str
    priority: str
    target_surface: str
    seed_surface: str
    runtime_packet: str
    witness_class: str
    writeback_targets: List[str] = field(default_factory=list)
    status: str = "READY"
    note: str = ""


@dataclass
class SelfHostingKernelDashboard:
    generated_at: str
    derivation_version: str
    docs_gate: str
    kernel_status: str
    control_plane_surface_coverage: float
    root_self_bearing_coverage: float
    identity_drift: float
    drift_threshold: float
    permitted_packets: int
    blocked_packets: int
    review_packets: int
    lineage_entries: int
    regeneration_targets_ready: int
    runtime_lanes_ok: bool
    top_packets: List[Dict[str, Any]] = field(default_factory=list)
    failure_gates: List[str] = field(default_factory=list)
    substrate: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
