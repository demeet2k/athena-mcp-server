from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class CrystalBodyRecord:
    body_id: str
    root: str
    body_state: str
    crystal_role: str
    authority: str
    dock: str
    lineage_class: str
    primary_zone: str
    family_surface: str
    capsule_surface: str
    dashboard_surface: str
    return_surface: str
    direct_synapse_targets: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CrystalFamilyContractRecord:
    contract_id: str
    body_id: str
    root: str
    role: str
    family_surface: str
    route_surface: str
    restart_seed: str
    lineage_class: str
    witness_basis: List[str] = field(default_factory=list)
    chapter_anchors: List[str] = field(default_factory=list)
    appendix_anchors: List[str] = field(default_factory=list)
    active_front: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DirectSynapseRecord:
    edge_id: str
    source_body_id: str
    source_root: str
    target_body_id: str
    target_root: str
    relation: str
    weight: float
    route: List[str] = field(default_factory=list)
    witness_basis: List[str] = field(default_factory=list)
    expected_writeback: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SynapticHandoffPacketRecord:
    packet_id: str
    source_agent: str
    target_agent: str
    source_body_id: str
    target_body_id: str
    trigger: str
    witness_basis: List[str] = field(default_factory=list)
    route: List[str] = field(default_factory=list)
    expected_writeback: List[str] = field(default_factory=list)
    proof_state: str = "NEAR"
    bridge_family_id: str = ""
    phase: str = ""
    replay_surface: str = ""
    verification_surface: str = ""
    weave_id: str = ""
    source_pair_id: str = ""
    target_pair_id: str = ""
    metro_level: str = ""
    appendix_stack: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RhythmStepRecord:
    step_id: str
    phase: str
    purpose: str
    primary_surface: str
    writeback_target: str
    stop_condition: str
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CapsuleSliceContractRecord:
    slice_id: str
    body_id: str
    root: str
    family_surface: str
    capsule_surface: str
    route_surface: str
    chapter_anchor: str
    appendix_anchor: str
    restart_seed: str
    truth_state: str
    writeback_target: str = ""
    witness_basis: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BridgeEdgeWitnessRecord:
    edge_id: str
    source_body_id: str
    source_root: str
    target_body_id: str
    target_root: str
    edge_class: str
    authority_rank: str
    runtime_surface: str
    replay_surface: str
    witness_basis: List[str] = field(default_factory=list)
    route: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocsIngressPacketRecord:
    packet_id: str
    status: str
    credentials_present: bool
    token_present: bool
    source_doc_id: str
    mirror_path: str
    ingest_time: str
    fallback_mode: str
    gate_surface: str = ""
    witness_basis: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WaveCheckpointRecord:
    checkpoint_id: str
    phase: str
    required_derivations: List[str] = field(default_factory=list)
    required_verifiers: List[str] = field(default_factory=list)
    atlas_refreshed: bool = False
    truth: str = "NEAR"
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeCorridorMembraneRecord:
    corridor_id: str
    source_body_id: str
    target_runtime_surface: str
    writeback_surface: str
    witness_basis: List[str] = field(default_factory=list)
    truth_state: str = "NEAR"
    next_seed: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SeedPacketWitnessRecord:
    packet_witness_id: str
    source_body_id: str
    mirror_surface: str
    packet_index_surface: str
    writeback_target: str
    witness_basis: List[str] = field(default_factory=list)
    truth_state: str = "NEAR"
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeCarrierContractRecord:
    carrier_id: str
    source_body_id: str
    runtime_surface: str
    membrane_surface: str
    verification_surfaces: List[str] = field(default_factory=list)
    replay_surface: str = ""
    writeback_surfaces: List[str] = field(default_factory=list)
    truth_state: str = "NEAR"
    selection_state: str = "PROMOTE_NEXT"
    next_seed: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeSquareContractRecord:
    square_contract_id: str
    source_body_id: str
    runtime_surface: str
    upstream_membrane_surface: str
    upstream_carrier_surface: str
    crosswalk_surface: str
    writeback_surfaces: List[str] = field(default_factory=list)
    truth_state: str = "NEAR"
    active_subfront: str = ""
    next_seed: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DirectBridgeFamilyContractRecord:
    bridge_family_id: str
    edge_id: str
    source_body_id: str
    source_root: str
    target_body_id: str
    target_root: str
    source_family_surface: str
    target_family_surface: str
    route_surface: str
    replay_surface: str
    runtime_surface: str
    restart_seed: str
    authority_rank: str
    packet_ids: List[str] = field(default_factory=list)
    slice_ids: List[str] = field(default_factory=list)
    witness_basis: List[str] = field(default_factory=list)
    primary_writeback_target: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BridgeSliceContractRecord:
    bridge_family_id: str
    slice_id: str
    phase: str
    source_anchor_ref: str
    target_anchor_ref: str
    packet_id: str
    writeback_target: str
    truth_state: str
    capsule_surface: str = ""
    route_surface: str = ""
    chapter_anchor: str = ""
    appendix_anchor: str = ""
    witness_basis: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BridgeBacklogEntryRecord:
    weave_id: str
    source_id: str
    source_surface: str
    target_id: str
    target_surface: str
    entry_class: str
    promotion_blocker: str
    next_lawful_action: str
    route: List[str] = field(default_factory=list)
    authority_rank: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["class"] = payload.pop("entry_class")
        return payload


@dataclass
class DeepPairwiseFamilyContractRecord:
    pairwise_family_id: str
    weave_id: str
    source_pair_id: str
    target_pair_id: str
    source_pair_surface: str
    target_pair_surface: str
    relation_stack: List[str] = field(default_factory=list)
    metro_level: str = ""
    appendix_stack: List[str] = field(default_factory=list)
    route_surface: str = ""
    replay_surface: str = ""
    runtime_surface: str = ""
    restart_seed: str = ""
    authority_rank: str = ""
    packet_ids: List[str] = field(default_factory=list)
    slice_ids: List[str] = field(default_factory=list)
    primary_writeback_target: str = ""
    witness_basis: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DeepPairwiseSliceContractRecord:
    pairwise_family_id: str
    slice_id: str
    phase: str
    source_anchor_ref: str
    target_anchor_ref: str
    packet_id: str
    writeback_target: str
    truth_state: str
    witness_basis: List[str] = field(default_factory=list)
    surface: str = ""
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
