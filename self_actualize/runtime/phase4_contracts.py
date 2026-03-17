from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class BodyRecord:
    body_id: str
    root: str
    role: str
    indexed_count: int
    authority: str
    status: str
    neighbors: List[Dict[str, Any]] = field(default_factory=list)
    hemisphere_bias: str = ""
    tract: str = ""
    dock: str = ""
    witness_class: str = "indexed"
    dominant_role: str = "source"
    authority_surface: str = ""
    source_paths: List[str] = field(default_factory=list)
    replay_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RootAnchorRecord:
    root_id: str
    root: str
    indexed_count: int
    status: str
    current_role: str
    authority_surface: str
    source_paths: List[str] = field(default_factory=list)
    replay_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KernelRecord:
    kernel_id: str
    source_title: str
    element: str
    cluster: str
    appendix_stack: List[str]
    body_binding: str
    body_id: str
    source_hint: str
    row_dir: str
    authority_surface: str
    status: str
    dominant_role: str
    hemisphere_bias: str
    tract: str
    dock: str
    source_paths: List[str] = field(default_factory=list)
    replay_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NodeRecord:
    node_id: str
    surface_class: str
    role: str
    hemisphere_bias: str
    tract: str
    dock: str
    witness: str
    dominant_role: str
    authority_surface: str
    status: str
    source_paths: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    replay_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PairRecord:
    pair_id: str
    pair_title: str
    row_kernel_id: str
    col_kernel_id: str
    relation_law: str
    loop_gates: List[str]
    appendix_support: List[str]
    neglect_score: float
    line_ids: List[str]
    source_paths: List[str]
    dominant_role: str
    authority_surface: str
    status: str
    replay_hint: str
    hemisphere_bias: str
    tract: str
    dock: str
    witness_floor: float
    bridge_opportunity: str
    charge_seed: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WaveRecord:
    wave_id: str
    pair_id: str
    objective: str
    charge_vector: Dict[str, float]
    thresholds: Dict[str, float]
    active_shortcuts: List[str]
    writeback_targets: List[str]
    stop_condition: str
    evidence_paths: List[str] = field(default_factory=list)
    status: str = "ACTIVE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShortcutRecord:
    shortcut_id: str
    name: str
    trigger: str
    preconditions: List[str]
    scoring_rule: str
    stop_condition: str
    output_type: str
    authority_surface: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExplorationQueryRecord:
    query_id: str
    mode: str
    scope: str
    seed_surface: str
    active_shortcuts: List[str]
    stop_rule: str
    output_bundle: List[str]
    writeback_target: str
    authority_surface: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NeglectSignalRecord:
    neglect_id: str
    surface_id: str
    surface_type: str
    gap_type: str
    coverage_gap: float
    drift: float
    replay_gap: float
    witness_gap: float
    bridge_opportunity: str
    nearest_bridge: str
    score: float
    source_paths: List[str]
    status: str = "OPEN"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WeaveCandidateRecord:
    weave_id: str
    src: str
    dst: str
    expected_gain: float
    required_shortcuts: List[str]
    promotion_route: List[str]
    source_surface: str
    target_surface: str
    status: str
    bridge_edge_id: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReplayReceiptRecord:
    action_id: str
    mode: str
    inputs: Dict[str, Any]
    fired_waves: List[str]
    writeback_paths: List[str]
    outcome: str
    unresolved_frontier: List[str]
    active_shortcuts: List[str]
    stop_condition: str
    witness_basis: List[str]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Phase4Dashboard:
    generated_at: str
    derivation_version: str
    docs_gate: str
    canonical_scope: str
    body_count: int
    kernel_count: int
    node_count: int
    pair_count: int
    wave_count: int
    shortcut_count: int
    neglect_count: int
    weave_count: int
    receipt_count: int
    query_modes: List[str] = field(default_factory=list)
    validation: Dict[str, bool] = field(default_factory=dict)
    top_neglects: List[Dict[str, Any]] = field(default_factory=list)
    top_waves: List[Dict[str, Any]] = field(default_factory=list)
    next_frontier: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
