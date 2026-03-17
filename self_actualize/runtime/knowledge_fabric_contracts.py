from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class StorageZoneRecord:
    zone_id: str
    zone_name: str
    purpose: str
    authority_surface: str
    witness_floor: str
    canonical_paths: List[str] = field(default_factory=list)
    artifact_classes: List[str] = field(default_factory=list)
    query_methods: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FabricRecord:
    record_id: str
    relative_path: str
    source_substrate: str
    root_id: str
    root_name: str
    root_status: str
    family_id: str
    title_hint: str
    surface_class: str
    storage_zone: str
    secondary_zones: List[str]
    witness_class: str
    truth_role: str
    authority_surface: str
    authority_rank: int
    semantic_role: str
    query_tags: List[str]
    freshness: Dict[str, Any]
    proof_state: str
    replay_class: str
    artifact_class: str
    modified_at: str
    size_bytes: int
    text_extractable: bool
    locator: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FabricEdge:
    edge_id: str
    source_record: str
    target_record: str
    edge_kind: str
    bridge_reason: str
    weight: float
    witness_basis: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShortcutPlanRecord:
    shortcut_id: str
    intent_class: str
    title: str
    entry_filters: Dict[str, Any]
    preferred_zones: List[str]
    preferred_surface_classes: List[str]
    ranking_stack: List[str]
    stop_condition: str
    fallback_zones: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExplorationPacketRecord:
    packet_id: str
    query_intent: str
    title: str
    query_text: str
    seed_records: List[str]
    traversal_mode: str
    budget: Dict[str, Any]
    shortcut_chain: List[str]
    visited_zones: List[str]
    result_class: str
    matched_record_ids: List[str] = field(default_factory=list)
    route_summary: str = ""
    witness_basis: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KnowledgeFabricDashboard:
    generated_at: str
    derivation_version: str
    docs_gate: str
    canonical_scope: str
    total_records: int
    indexed_records: int
    archive_records: int
    physical_stub_records: int
    generated_records: int
    zone_count: int
    edge_count: int
    shortcut_count: int
    packet_count: int
    validations: Dict[str, Any] = field(default_factory=dict)
    zone_health: List[Dict[str, Any]] = field(default_factory=list)
    blocked_lanes: List[Dict[str, Any]] = field(default_factory=list)
    stale_zones: List[Dict[str, Any]] = field(default_factory=list)
    ambiguous_zones: List[Dict[str, Any]] = field(default_factory=list)
    shortcut_performance: List[Dict[str, Any]] = field(default_factory=list)
    top_entry_records: List[Dict[str, Any]] = field(default_factory=list)
    next_frontier: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
