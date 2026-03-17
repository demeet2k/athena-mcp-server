from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class MetroSystemRecord:
    system_id: str
    label: str
    authority_surface: str
    category: str
    station_family: str
    replay_class: str
    drift_status: str
    primary_zone: str
    entry_station_ids: List[str] = field(default_factory=list)
    exit_station_ids: List[str] = field(default_factory=list)
    default_return_path: List[str] = field(default_factory=list)
    source_paths: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetroStationRecord:
    station_id: str
    label: str
    system_ids: List[str]
    station_type: str
    authority_surface: str
    lane_membership: List[str] = field(default_factory=list)
    coordinate_hint: str = ""
    source_paths: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetroInterlockRecord:
    interlock_id: str
    source_system: str
    source_station: str
    target_system: str
    target_station: str
    transform_kind: str
    witness_basis: List[str]
    dispatch_rule: str
    dispatch_score: float
    return_path: List[str]
    route_via: List[str]
    proof_state: str
    status: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HoloCoordinateRecord:
    coord_id: str
    record_id: str
    record_type: str
    addr4: str
    face6: str
    arc7: str
    rail3: str
    depth5: str
    lens15: str
    system_id: str
    truth: str
    surface: str
    authority_surface: str
    source_paths: List[str] = field(default_factory=list)
    replay_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CarrierRecord:
    carrier_id: str
    label: str
    role: str
    authority_surface: str
    transform_neighbors: List[str] = field(default_factory=list)
    dominant_zone: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RailRecord:
    rail_id: str
    label: str
    chapter_ids: List[str]
    control_purpose: str
    allowed_transfer_kinds: List[str]
    authority_surface: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ArcRotationRecord:
    arc_id: str
    omega_range: List[int]
    rho: int
    rotated_triad: List[str]
    chapter_assignments: List[Dict[str, str]]
    authority_surface: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CarrierTransformRecord:
    transform_id: str
    source_carriers: List[str]
    target_carriers: List[str]
    transform_law: str
    authority_surface: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LensRecord:
    lens_id: str
    label: str
    class_type: str
    members: List[str]
    role: str
    default_gate: str
    authority_surface: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LensWeightProfileRecord:
    lens_id: str
    label: str
    members: List[str]
    preferred_channels: List[str]
    preferred_carriers: List[str]
    preferred_rails: List[str]
    appendix_support: List[str]
    shortcut_chain: List[str]
    stop_condition: str
    writeback_targets: List[str]
    channel_weights: Dict[str, float] = field(default_factory=dict)
    certificate_rule: str = ""
    authority_surface: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LensStateRecord:
    state_id: str
    record_id: str
    record_type: str
    dominant_lens_system: str
    secondary_lens_system: str
    lens_weight_vector: Dict[str, float]
    preferred_carriers: List[str]
    preferred_rails: List[str]
    supported_projection_spaces: List[str]
    unsupported_projection_spaces: List[str]
    field_weight_vector: Dict[str, float]
    authority_surface: str
    source_paths: List[str] = field(default_factory=list)
    replay_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FieldRecord:
    field_id: str
    label: str
    carrier_binding: List[str]
    role: str
    authority_surface: str
    thresholds: Dict[str, Any] = field(default_factory=dict)
    source_paths: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ZPointRecord:
    zpoint_id: str
    label: str
    route_class: str
    restart_token: str
    binding_hubs: List[str]
    proof_state: str
    authority_surface: str
    source_paths: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AetherPointRecord:
    point_id: str
    source_record_id: str
    source_record_type: str
    lens_system: str
    system_id: str
    aether_density: float
    zero_proximity: float
    tunnel_cost: float
    rail_hardness: float
    resonance_pressure: float
    repair_gain: float
    geodesic_mode: str
    authority_surface: str
    source_paths: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectionSpaceRecord:
    space_id: str
    label: str
    axes: List[str]
    carrier_focus: List[str]
    authority_surface: str
    crosswalk_rules: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectionAssignmentRecord:
    assignment_id: str
    record_id: str
    record_type: str
    supported_spaces: List[str]
    unsupported_spaces: List[str]
    preferred_space: str
    authority_surface: str
    source_paths: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Pt2ShortcutRecord:
    shortcut_id: str
    label: str
    trigger: str
    preferred_zones: List[str]
    preferred_surface_classes: List[str]
    ranking_stack: List[str]
    stop_condition: str
    required_inputs: List[str]
    authority_surface: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Pt2QueryPresetRecord:
    query_id: str
    mode: str
    scope: str
    active_shortcuts: List[str]
    stop_rule: str
    default_exploration_order: List[str]
    writeback_targets: List[str]
    authority_surface: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CrosswalkEdgeRecord:
    edge_id: str
    source_id: str
    target_id: str
    edge_kind: str
    bridge_reason: str
    weight: float
    witness_basis: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Phase4Pt2Dashboard:
    generated_at: str
    derivation_version: str
    docs_gate: str
    canonical_scope: str
    metro_system_count: int
    station_count: int
    interlock_count: int
    coordinate_count: int
    carrier_count: int
    rail_count: int
    lens_count: int
    lens_state_count: int
    field_count: int
    zpoint_count: int
    aether_point_count: int
    projection_space_count: int
    projection_assignment_count: int
    shortcut_count: int
    query_count: int
    edge_count: int
    validation: Dict[str, bool] = field(default_factory=dict)
    top_interlocks: List[Dict[str, Any]] = field(default_factory=list)
    top_lens_states: List[Dict[str, Any]] = field(default_factory=list)
    top_aether_points: List[Dict[str, Any]] = field(default_factory=list)
    next_frontier: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
