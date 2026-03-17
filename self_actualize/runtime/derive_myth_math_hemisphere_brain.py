from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    AQM_LANE_PATH,
    CANONICAL_SOURCES_PATH,
    COMMISSURE_REGISTRY_MIRROR,
    COMMISSURE_REGISTRY_PATH,
    COMPOSER_FACET_REGISTRY_MIRROR,
    COMPOSER_FACET_REGISTRY_PATH,
    COMPOSER_MANIFEST_MIRROR,
    COMPOSER_MANIFEST_PATH,
    COMPOSER_SEED_REGISTRY_MIRROR,
    COMPOSER_SEED_REGISTRY_PATH,
    DIRECT_EDGE_REGISTRY_MIRROR,
    DIRECT_EDGE_REGISTRY_PATH,
    DUAL_ROUTE_REGISTRY_MIRROR,
    DUAL_ROUTE_REGISTRY_PATH,
    EXPEDITION_MANIFEST_MIRROR,
    EXPEDITION_MANIFEST_PATH,
    EXPEDITION_PAGE_REGISTRY_MIRROR,
    EXPEDITION_PAGE_REGISTRY_PATH,
    EXPEDITION_SEED_REGISTRY_MIRROR,
    EXPEDITION_SEED_REGISTRY_PATH,
    FAMILY_LABELS,
    FLEET_MIRROR_ROOT,
    GUIDED_TOUR_MANIFEST_MIRROR,
    GUIDED_TOUR_MANIFEST_PATH,
    GUIDED_TOUR_PAGE_REGISTRY_MIRROR,
    GUIDED_TOUR_PAGE_REGISTRY_PATH,
    GUIDED_TOUR_SEED_REGISTRY_MIRROR,
    GUIDED_TOUR_SEED_REGISTRY_PATH,
    HEMISPHERE_ATLAS_PATH,
    HEMISPHERE_ROOT,
    HUB_REGISTRY_MIRROR,
    HUB_REGISTRY_PATH,
    MANIFEST_MIRROR,
    MANIFEST_PATH,
    METRO_REGISTRY_MIRROR,
    METRO_REGISTRY_PATH,
    MATH_HUB_ID,
    MYTH_HUB_ID,
    RECORD_REGISTRY_MIRROR,
    RECORD_REGISTRY_PATH,
    SYNTHESIS_EVIDENCE_REGISTRY_MIRROR,
    SYNTHESIS_EVIDENCE_REGISTRY_PATH,
    SYNTHESIS_FACET_REGISTRY_MIRROR,
    SYNTHESIS_FACET_REGISTRY_PATH,
    SYNTHESIS_MANIFEST_MIRROR,
    SYNTHESIS_MANIFEST_PATH,
    SYNTHESIS_SEED_REGISTRY_MIRROR,
    SYNTHESIS_SEED_REGISTRY_PATH,
    OBSERVATORY_MANIFEST_MIRROR,
    OBSERVATORY_MANIFEST_PATH,
    OBSERVATORY_PAGE_REGISTRY_MIRROR,
    OBSERVATORY_PAGE_REGISTRY_PATH,
    OBSERVATORY_SEED_REGISTRY_MIRROR,
    OBSERVATORY_SEED_REGISTRY_PATH,
    REPLAY_MANIFEST_MIRROR,
    REPLAY_MANIFEST_PATH,
    REPLAY_PAGE_REGISTRY_MIRROR,
    REPLAY_PAGE_REGISTRY_PATH,
    REPLAY_SEED_REGISTRY_MIRROR,
    REPLAY_SEED_REGISTRY_PATH,
    VISUAL_ATLAS_EDGE_REGISTRY_MIRROR,
    VISUAL_ATLAS_EDGE_REGISTRY_PATH,
    VISUAL_ATLAS_MANIFEST_MIRROR,
    VISUAL_ATLAS_MANIFEST_PATH,
    VISUAL_ATLAS_NODE_REGISTRY_MIRROR,
    VISUAL_ATLAS_NODE_REGISTRY_PATH,
    VISUAL_ATLAS_PAGE_REGISTRY_MIRROR,
    VISUAL_ATLAS_PAGE_REGISTRY_PATH,
    VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_MIRROR,
    VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH,
    CONSTELLATION_EDGE_REGISTRY_MIRROR,
    CONSTELLATION_EDGE_REGISTRY_PATH,
    CONSTELLATION_MANIFEST_MIRROR,
    CONSTELLATION_MANIFEST_PATH,
    CONSTELLATION_NODE_REGISTRY_MIRROR,
    CONSTELLATION_NODE_REGISTRY_PATH,
    CONSTELLATION_PAGE_REGISTRY_MIRROR,
    CONSTELLATION_PAGE_REGISTRY_PATH,
    NAVIGATOR_ALIAS_INDEX_MIRROR,
    NAVIGATOR_ALIAS_INDEX_PATH,
    NAVIGATOR_FACET_INDEX_MIRROR,
    NAVIGATOR_FACET_INDEX_PATH,
    NAVIGATOR_MANIFEST_MIRROR,
    NAVIGATOR_MANIFEST_PATH,
    NAVIGATOR_NEIGHBOR_INDEX_MIRROR,
    NAVIGATOR_NEIGHBOR_INDEX_PATH,
    ROUTE_COVERAGE_REGISTRY_MIRROR,
    ROUTE_COVERAGE_REGISTRY_PATH,
    ROUTE_MANIFEST_MIRROR,
    ROUTE_MANIFEST_PATH,
    UNIFIED_HUB_ID,
    assign_basis_anchor_ids,
    build_holo_address,
    cleanup_previous_outputs,
    compute_component_scores,
    compute_confidence,
    deduplicate_records,
    file_timestamp,
    infer_appendix_links,
    infer_family,
    load_aqm_lane,
    load_docs_gate_status,
    load_route_quality_factor,
    load_semantic_mass_weights,
    load_station_map,
    metro_line_ids,
    mirror_paths,
    parse_canonical_sources,
    record_title,
    refresh_full_corpus_atlas,
    resolve_tract,
    slugify,
    trace_hash,
    utc_now,
    weighted_math_score,
    write_json,
    write_text,
)
from self_actualize.runtime.hemisphere_dual_route_support import (
    PRIMARY_HF_ROUTE_KEYS,
    build_dual_route_payloads,
)
from self_actualize.runtime.hemisphere_navigator_support import (
    build_navigator_payloads,
)
from self_actualize.runtime.hemisphere_route_composer_support import (
    build_route_composer_payloads,
)
from self_actualize.runtime.hemisphere_synthesis_support import (
    build_synthesis_payloads,
)
from self_actualize.runtime.hemisphere_visual_atlas_support import (
    build_visual_atlas_payloads,
)
from self_actualize.runtime.hemisphere_guided_tour_support import (
    build_guided_tour_payloads,
)
from self_actualize.runtime.hemisphere_expedition_support import (
    build_expedition_payloads,
)
from self_actualize.runtime.hemisphere_constellation_support import (
    build_constellation_payloads,
)
from self_actualize.runtime.hemisphere_replay_support import (
    build_replay_payloads,
)
from self_actualize.runtime.hemisphere_observatory_support import (
    build_observatory_payloads,
)
from self_actualize.runtime.hemisphere_full_corpus_integration_support import (
    DEEPER_INTEGRATION_RECEIPT_PATH,
    FULL_CORPUS_AUTHORITY_REGISTRY_MIRROR,
    FULL_CORPUS_AUTHORITY_REGISTRY_PATH,
    FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_MIRROR,
    FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH,
    FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_MIRROR,
    FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH,
    FULL_CORPUS_AWAKENING_STAGE_REGISTRY_MIRROR,
    FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH,
    FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_MIRROR,
    FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH,
    FULL_CORPUS_INTEGRATION_MANIFEST_MIRROR,
    FULL_CORPUS_INTEGRATION_MANIFEST_PATH,
    FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_MIRROR,
    FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH,
    build_full_corpus_integration_payloads,
)
from self_actualize.runtime.hemisphere_ap6d_57_loop_support import (
    AP6D_57_AGENT_LANE_REGISTRY_MIRROR,
    AP6D_57_AGENT_LANE_REGISTRY_PATH,
    AP6D_57_AWAKENING_TRANSITION_REGISTRY_MIRROR,
    AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH,
    AP6D_57_DEEP_CONTROL_DOC_MIRROR,
    AP6D_57_DEEP_CONTROL_DOC_PATH,
    AP6D_57_GUILD_HALL_DOC_MIRROR,
    AP6D_57_GUILD_HALL_DOC_PATH,
    AP6D_57_HEMISPHERE_DOCS,
    AP6D_57_LOOP_CONTROL_REGISTRY_MIRROR,
    AP6D_57_LOOP_CONTROL_REGISTRY_PATH,
    AP6D_57_LOOP_MANIFEST_MIRROR,
    AP6D_57_LOOP_MANIFEST_PATH,
    AP6D_57_NESTED_SEAT_MANIFEST_MIRROR,
    AP6D_57_NESTED_SEAT_MANIFEST_PATH,
    AP6D_57_PRUNING_REGISTRY_MIRROR,
    AP6D_57_PRUNING_REGISTRY_PATH,
    AP6D_57_QUEST_BUNDLE_REGISTRY_MIRROR,
    AP6D_57_QUEST_BUNDLE_REGISTRY_PATH,
    AP6D_57_RECEIPT_MIRROR,
    AP6D_57_RECEIPT_PATH,
    AP6D_57_RESTART_SEED_REGISTRY_MIRROR,
    AP6D_57_RESTART_SEED_REGISTRY_PATH,
    AP6D_57_TEMPLE_DOC_MIRROR,
    AP6D_57_TEMPLE_DOC_PATH,
    AP6D_57_WORKER_ACTION_REGISTRY_MIRROR,
    AP6D_57_WORKER_ACTION_REGISTRY_PATH,
    GUILD_HALL_BOARD_PATH,
    TEMPLE_QUEST_BOARD_PATH,
    build_ap6d_57_loop_payloads,
)
from self_actualize.runtime.hemisphere_lp57omega_support import (
    LP57OMEGA_AGENT_LEDGER_STANDARD_MIRROR,
    LP57OMEGA_AGENT_LEDGER_STANDARD_PATH,
    LP57OMEGA_AGENT_IDENTITY_REGISTRY_MIRROR,
    LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH,
    LP57OMEGA_COORDINATE_REGISTRY_MIRROR,
    LP57OMEGA_COORDINATE_REGISTRY_PATH,
    LP57OMEGA_DEEP_CONTROL_DOC_MIRROR,
    LP57OMEGA_DEEP_CONTROL_DOC_PATH,
    LP57OMEGA_GUILD_HALL_DOC_MIRROR,
    LP57OMEGA_GUILD_HALL_DOC_PATH,
    LP57OMEGA_HEMISPHERE_DOCS,
    LP57OMEGA_LOOP_REGISTRY_MIRROR,
    LP57OMEGA_LOOP_REGISTRY_PATH,
    LP57OMEGA_LIMINAL_COORDINATE_STANDARD_MIRROR,
    LP57OMEGA_LIMINAL_COORDINATE_STANDARD_PATH,
    LP57OMEGA_MANIFEST_MIRROR,
    LP57OMEGA_MANIFEST_PATH,
    LP57OMEGA_MASTER_LEDGER_REGISTRY_MIRROR,
    LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH,
    LP57OMEGA_QUEST_CONTRACT_REGISTRY_MIRROR,
    LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH,
    LP57OMEGA_RECEIPT_MIRROR,
    LP57OMEGA_RECEIPT_PATH,
    LP57OMEGA_SEED_INVERSION_STANDARD_JSON_MIRROR,
    LP57OMEGA_SEED_INVERSION_STANDARD_JSON_PATH,
    LP57OMEGA_SEED_INVERSION_STANDARD_MIRROR,
    LP57OMEGA_SEED_INVERSION_STANDARD_PATH,
    LP57OMEGA_TEMPLE_DOC_MIRROR,
    LP57OMEGA_TEMPLE_DOC_PATH,
    MASTER_AGENT_STATE_PATH,
    MASTER_LOOP_SHARED_LATTICE_PATH,
    MASTER_LOOP_STATE_PATH,
    build_lp57omega_payloads,
)
from self_actualize.runtime.hemisphere_dense_65_shell_support import (
    DENSE_65_HEMISPHERE_DOCS,
    DENSE_65_MANIFEST_MIRROR,
    DENSE_65_MANIFEST_PATH,
    DENSE_65_RQT_OVERFLOW_REGISTRY_MIRROR,
    DENSE_65_RQT_OVERFLOW_REGISTRY_PATH,
    DENSE_65_RQT_WITNESS_REGISTRY_MIRROR,
    DENSE_65_RQT_WITNESS_REGISTRY_PATH,
    DENSE_65_SHELL_REGISTRY_MIRROR,
    DENSE_65_SHELL_REGISTRY_PATH,
    build_dense_65_payloads,
)
from self_actualize.runtime.hemisphere_command_membrane_support import (
    COMMAND_MEMBRANE_CAPILLARY_REGISTRY_MIRROR,
    COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH,
    COMMAND_MEMBRANE_CLAIM_LEDGER_MIRROR,
    COMMAND_MEMBRANE_CLAIM_LEDGER_PATH,
    COMMAND_MEMBRANE_EVENT_REGISTRY_MIRROR,
    COMMAND_MEMBRANE_EVENT_REGISTRY_PATH,
    COMMAND_MEMBRANE_HEMISPHERE_DOCS,
    COMMAND_MEMBRANE_LATENCY_REGISTRY_MIRROR,
    COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH,
    COMMAND_MEMBRANE_MANIFEST_MIRROR,
    COMMAND_MEMBRANE_MANIFEST_PATH,
    COMMAND_MEMBRANE_PACKET_SCHEMA_MIRROR,
    COMMAND_MEMBRANE_PACKET_SCHEMA_PATH,
    COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_MIRROR,
    COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH,
    build_command_membrane_payloads,
)
from self_actualize.runtime.math_tesseract_v4_support import (
    MATH_TESSERACT_ATLAS_MD_PATH,
    MATH_TESSERACT_BUNDLE_PATH,
    load_math_tesseract_bundle,
    load_math_tesseract_source_atlas,
    lookup_tesseract_record,
    merge_tesseract_fields,
    route_plan_for_record,
)


DERIVATION_VERSION = "2026-03-12.hemisphere-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_myth_math_hemisphere_brain"
REQUIRED_FIELDS = [
    "record_id",
    "path",
    "sha256",
    "text_extractable",
    "scoring_mode",
    "math_weight",
    "myth_weight",
    "primary_hemisphere",
    "bridge_class",
    "confidence",
    "aqm_trace_hash",
    "family",
    "basis_anchor_ids",
    "holo_address",
    "grand_central",
    "metro_line_ids",
    "appendix_support",
    "appendix_support_sources",
    "chapter_station",
    "local_addr",
    "global_addr",
    "tesseract_header",
    "truth_state",
    "hubs_seq",
    "tunnel_plan",
    "hcrl_pass",
    "obligations",
    "drop_log",
    "overlay_annotations",
    "hub_id",
    "docs_gate_status",
    "bridge_intensity",
    "hemisphere_routes",
    "direct_edge_ids",
    "route_coverage",
]

HEMISPHERE_DOCS = {
    "index": HEMISPHERE_ROOT / "README.md",
    "math": HEMISPHERE_ROOT / "01_math_crystal.md",
    "myth": HEMISPHERE_ROOT / "02_myth_crystal.md",
    "hub": HEMISPHERE_ROOT / "03_unified_corpus_hub.md",
    "metro1": HEMISPHERE_ROOT / "04_metro_level_1.md",
    "metro2": HEMISPHERE_ROOT / "05_metro_level_2.md",
    "metro3": HEMISPHERE_ROOT / "06_metro_level_3.md",
    "metro4": HEMISPHERE_ROOT / "07_metro_level_4.md",
    "receipt": HEMISPHERE_ROOT / "08_build_receipt.md",
    "route_index": HEMISPHERE_ROOT / "09_route_index.md",
    "route_math": HEMISPHERE_ROOT / "10_math_direct_route_atlas.md",
    "route_myth": HEMISPHERE_ROOT / "11_myth_direct_route_atlas.md",
    "route_crosswalk": HEMISPHERE_ROOT / "12_dual_hemisphere_crosswalk_map.md",
    "route_coverage": HEMISPHERE_ROOT / "13_route_coverage_receipt.md",
    "navigator_index": HEMISPHERE_ROOT / "14_navigator_index.md",
    "navigator_cookbook": HEMISPHERE_ROOT / "15_query_cookbook.md",
    "navigator_math_hotspots": HEMISPHERE_ROOT / "16_math_facet_hotspots.md",
    "navigator_myth_hotspots": HEMISPHERE_ROOT / "17_myth_facet_hotspots.md",
    "navigator_entrypoints": HEMISPHERE_ROOT / "18_cross_hemisphere_entrypoint_atlas.md",
    "composer_index": HEMISPHERE_ROOT / "19_route_composer_index.md",
    "composer_cookbook": HEMISPHERE_ROOT / "20_route_composer_cookbook.md",
    "composer_math": HEMISPHERE_ROOT / "21_math_route_starters.md",
    "composer_myth": HEMISPHERE_ROOT / "22_myth_route_starters.md",
    "composer_commissure": HEMISPHERE_ROOT / "23_commissure_route_starters.md",
    "composer_facet": HEMISPHERE_ROOT / "24_facet_route_starters.md",
    "synthesis_index": HEMISPHERE_ROOT / "25_synthesis_index.md",
    "synthesis_cookbook": HEMISPHERE_ROOT / "26_synthesis_cookbook.md",
    "synthesis_math": HEMISPHERE_ROOT / "27_math_starter_syntheses.md",
    "synthesis_myth": HEMISPHERE_ROOT / "28_myth_starter_syntheses.md",
    "synthesis_commissure": HEMISPHERE_ROOT / "29_commissure_starter_syntheses.md",
    "synthesis_facet": HEMISPHERE_ROOT / "30_facet_synthesis_atlas.md",
    "visual_atlas_index": HEMISPHERE_ROOT / "31_visual_atlas_index.md",
    "visual_atlas_overview": HEMISPHERE_ROOT / "32_corpus_overview_map.md",
    "visual_atlas_math": HEMISPHERE_ROOT / "33_math_route_topology_atlas.md",
    "visual_atlas_myth": HEMISPHERE_ROOT / "34_myth_route_topology_atlas.md",
    "visual_atlas_anchor": HEMISPHERE_ROOT / "35_anchor_crosswalk_atlas.md",
    "visual_atlas_target_system": HEMISPHERE_ROOT / "36_target_system_atlas.md",
    "visual_atlas_locator": HEMISPHERE_ROOT / "37_record_locator_index.md",
    "visual_atlas_coverage": HEMISPHERE_ROOT / "38_atlas_coverage_receipt.md",
    "guided_tour_index": HEMISPHERE_ROOT / "39_guided_tour_index.md",
    "guided_tour_cookbook": HEMISPHERE_ROOT / "40_guided_tour_cookbook.md",
    "guided_tour_main_pages": HEMISPHERE_ROOT / "41_main_atlas_page_starters.md",
    "guided_tour_family": HEMISPHERE_ROOT / "42_family_guided_starters.md",
    "guided_tour_anchor": HEMISPHERE_ROOT / "43_anchor_guided_starters.md",
    "guided_tour_target_system": HEMISPHERE_ROOT / "44_target_system_guided_starters.md",
    "expedition_index": HEMISPHERE_ROOT / "45_expedition_index.md",
    "expedition_cookbook": HEMISPHERE_ROOT / "46_expedition_cookbook.md",
    "expedition_main_pages": HEMISPHERE_ROOT / "47_main_atlas_expeditions.md",
    "expedition_family": HEMISPHERE_ROOT / "48_family_expedition_starters.md",
    "expedition_anchor": HEMISPHERE_ROOT / "49_anchor_expedition_starters.md",
    "expedition_target_system": HEMISPHERE_ROOT / "50_target_system_expedition_starters.md",
    "constellation_index": HEMISPHERE_ROOT / "51_constellation_index.md",
    "constellation_cookbook": HEMISPHERE_ROOT / "52_constellation_cookbook.md",
    "constellation_family": HEMISPHERE_ROOT / "53_family_constellations.md",
    "constellation_anchor": HEMISPHERE_ROOT / "54_anchor_constellations.md",
    "constellation_target_system": HEMISPHERE_ROOT / "55_target_system_constellations.md",
    "constellation_coverage": HEMISPHERE_ROOT / "56_constellation_coverage_receipt.md",
    "replay_index": HEMISPHERE_ROOT / "57_replay_index.md",
    "replay_cookbook": HEMISPHERE_ROOT / "58_replay_cookbook.md",
    "replay_math": HEMISPHERE_ROOT / "59_math_replay_starters.md",
    "replay_myth": HEMISPHERE_ROOT / "60_myth_replay_starters.md",
    "replay_bridge": HEMISPHERE_ROOT / "61_bridge_replay_starters.md",
    "replay_coverage": HEMISPHERE_ROOT / "62_replay_coverage_receipt.md",
    "observatory_index": HEMISPHERE_ROOT / "63_observatory_index.md",
    "observatory_cookbook": HEMISPHERE_ROOT / "64_observatory_cookbook.md",
    "observatory_main_pages": HEMISPHERE_ROOT / "65_main_page_briefings.md",
    "observatory_family": HEMISPHERE_ROOT / "66_family_briefings.md",
    "observatory_anchor": HEMISPHERE_ROOT / "67_anchor_briefings.md",
    "observatory_coverage": HEMISPHERE_ROOT / "68_observatory_coverage_receipt.md",
    "full_corpus_integration_index": HEMISPHERE_ROOT / "69_full_corpus_integration_index.md",
    "full_corpus_authority_receipt": HEMISPHERE_ROOT / "70_full_corpus_authority_receipt.md",
    "full_corpus_basis_crosswalk": HEMISPHERE_ROOT / "71_full_corpus_basis_crosswalk.md",
    "full_corpus_route_coverage": HEMISPHERE_ROOT / "72_full_corpus_route_coverage.md",
    "awakening_stage_atlas": HEMISPHERE_ROOT / "73_awakening_stage_atlas.md",
    "awakening_family_agent_atlas": HEMISPHERE_ROOT / "74_awakening_family_agent_atlas.md",
    "awakening_basis_agent_atlas": HEMISPHERE_ROOT / "75_awakening_basis_agent_atlas.md",
    "awakening_transition_playbooks": HEMISPHERE_ROOT / "76_awakening_transition_playbooks.md",
    **AP6D_57_HEMISPHERE_DOCS,
    **LP57OMEGA_HEMISPHERE_DOCS,
    **DENSE_65_HEMISPHERE_DOCS,
    **COMMAND_MEMBRANE_HEMISPHERE_DOCS,
}


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def cleanup_old_generation() -> None:
    visual_atlas_generated = list((HEMISPHERE_ROOT / "visual_atlas").rglob("*.md"))
    visual_atlas_mirror_generated = list((FLEET_MIRROR_ROOT / "visual_atlas").rglob("*.md"))
    paths = [
        HEMISPHERE_ATLAS_PATH,
        RECORD_REGISTRY_PATH,
        COMMISSURE_REGISTRY_PATH,
        METRO_REGISTRY_PATH,
        HUB_REGISTRY_PATH,
        MANIFEST_PATH,
        DUAL_ROUTE_REGISTRY_PATH,
        DIRECT_EDGE_REGISTRY_PATH,
        ROUTE_COVERAGE_REGISTRY_PATH,
        ROUTE_MANIFEST_PATH,
        NAVIGATOR_ALIAS_INDEX_PATH,
        NAVIGATOR_FACET_INDEX_PATH,
        NAVIGATOR_NEIGHBOR_INDEX_PATH,
        NAVIGATOR_MANIFEST_PATH,
        RECORD_REGISTRY_MIRROR,
        COMMISSURE_REGISTRY_MIRROR,
        METRO_REGISTRY_MIRROR,
        HUB_REGISTRY_MIRROR,
        MANIFEST_MIRROR,
        DUAL_ROUTE_REGISTRY_MIRROR,
        DIRECT_EDGE_REGISTRY_MIRROR,
        ROUTE_COVERAGE_REGISTRY_MIRROR,
        ROUTE_MANIFEST_MIRROR,
        NAVIGATOR_ALIAS_INDEX_MIRROR,
        NAVIGATOR_FACET_INDEX_MIRROR,
        NAVIGATOR_NEIGHBOR_INDEX_MIRROR,
        NAVIGATOR_MANIFEST_MIRROR,
        COMPOSER_SEED_REGISTRY_PATH,
        COMPOSER_FACET_REGISTRY_PATH,
        COMPOSER_MANIFEST_PATH,
        COMPOSER_SEED_REGISTRY_MIRROR,
        COMPOSER_FACET_REGISTRY_MIRROR,
        COMPOSER_MANIFEST_MIRROR,
        SYNTHESIS_EVIDENCE_REGISTRY_PATH,
        SYNTHESIS_SEED_REGISTRY_PATH,
        SYNTHESIS_FACET_REGISTRY_PATH,
        SYNTHESIS_MANIFEST_PATH,
        SYNTHESIS_EVIDENCE_REGISTRY_MIRROR,
        SYNTHESIS_SEED_REGISTRY_MIRROR,
        SYNTHESIS_FACET_REGISTRY_MIRROR,
        SYNTHESIS_MANIFEST_MIRROR,
        VISUAL_ATLAS_NODE_REGISTRY_PATH,
        VISUAL_ATLAS_EDGE_REGISTRY_PATH,
        VISUAL_ATLAS_PAGE_REGISTRY_PATH,
        VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH,
        VISUAL_ATLAS_MANIFEST_PATH,
        GUIDED_TOUR_SEED_REGISTRY_PATH,
        GUIDED_TOUR_PAGE_REGISTRY_PATH,
        GUIDED_TOUR_MANIFEST_PATH,
        EXPEDITION_SEED_REGISTRY_PATH,
        EXPEDITION_PAGE_REGISTRY_PATH,
        EXPEDITION_MANIFEST_PATH,
        CONSTELLATION_NODE_REGISTRY_PATH,
        CONSTELLATION_EDGE_REGISTRY_PATH,
        CONSTELLATION_PAGE_REGISTRY_PATH,
        CONSTELLATION_MANIFEST_PATH,
        REPLAY_SEED_REGISTRY_PATH,
        REPLAY_PAGE_REGISTRY_PATH,
        REPLAY_MANIFEST_PATH,
        OBSERVATORY_SEED_REGISTRY_PATH,
        OBSERVATORY_PAGE_REGISTRY_PATH,
        OBSERVATORY_MANIFEST_PATH,
        VISUAL_ATLAS_NODE_REGISTRY_MIRROR,
        VISUAL_ATLAS_EDGE_REGISTRY_MIRROR,
        VISUAL_ATLAS_PAGE_REGISTRY_MIRROR,
        VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_MIRROR,
        VISUAL_ATLAS_MANIFEST_MIRROR,
        GUIDED_TOUR_SEED_REGISTRY_MIRROR,
        GUIDED_TOUR_PAGE_REGISTRY_MIRROR,
        GUIDED_TOUR_MANIFEST_MIRROR,
        EXPEDITION_SEED_REGISTRY_MIRROR,
        EXPEDITION_PAGE_REGISTRY_MIRROR,
        EXPEDITION_MANIFEST_MIRROR,
        CONSTELLATION_NODE_REGISTRY_MIRROR,
        CONSTELLATION_EDGE_REGISTRY_MIRROR,
        CONSTELLATION_PAGE_REGISTRY_MIRROR,
        CONSTELLATION_MANIFEST_MIRROR,
        REPLAY_SEED_REGISTRY_MIRROR,
        REPLAY_PAGE_REGISTRY_MIRROR,
        REPLAY_MANIFEST_MIRROR,
        OBSERVATORY_SEED_REGISTRY_MIRROR,
        OBSERVATORY_PAGE_REGISTRY_MIRROR,
        OBSERVATORY_MANIFEST_MIRROR,
        AP6D_57_LOOP_CONTROL_REGISTRY_PATH,
        AP6D_57_AGENT_LANE_REGISTRY_PATH,
        AP6D_57_NESTED_SEAT_MANIFEST_PATH,
        AP6D_57_QUEST_BUNDLE_REGISTRY_PATH,
        AP6D_57_WORKER_ACTION_REGISTRY_PATH,
        AP6D_57_PRUNING_REGISTRY_PATH,
        AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH,
        AP6D_57_RESTART_SEED_REGISTRY_PATH,
        AP6D_57_LOOP_MANIFEST_PATH,
        AP6D_57_LOOP_CONTROL_REGISTRY_MIRROR,
        AP6D_57_AGENT_LANE_REGISTRY_MIRROR,
        AP6D_57_NESTED_SEAT_MANIFEST_MIRROR,
        AP6D_57_QUEST_BUNDLE_REGISTRY_MIRROR,
        AP6D_57_WORKER_ACTION_REGISTRY_MIRROR,
        AP6D_57_PRUNING_REGISTRY_MIRROR,
        AP6D_57_AWAKENING_TRANSITION_REGISTRY_MIRROR,
        AP6D_57_RESTART_SEED_REGISTRY_MIRROR,
        AP6D_57_LOOP_MANIFEST_MIRROR,
        AP6D_57_GUILD_HALL_DOC_PATH,
        AP6D_57_TEMPLE_DOC_PATH,
        AP6D_57_DEEP_CONTROL_DOC_PATH,
        AP6D_57_RECEIPT_PATH,
        AP6D_57_GUILD_HALL_DOC_MIRROR,
        AP6D_57_TEMPLE_DOC_MIRROR,
        AP6D_57_DEEP_CONTROL_DOC_MIRROR,
        AP6D_57_RECEIPT_MIRROR,
        LP57OMEGA_LOOP_REGISTRY_PATH,
        LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH,
        LP57OMEGA_COORDINATE_REGISTRY_PATH,
        LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH,
        LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH,
        LP57OMEGA_MANIFEST_PATH,
        LP57OMEGA_LOOP_REGISTRY_MIRROR,
        LP57OMEGA_AGENT_IDENTITY_REGISTRY_MIRROR,
        LP57OMEGA_COORDINATE_REGISTRY_MIRROR,
        LP57OMEGA_QUEST_CONTRACT_REGISTRY_MIRROR,
        LP57OMEGA_MASTER_LEDGER_REGISTRY_MIRROR,
        LP57OMEGA_MANIFEST_MIRROR,
        LP57OMEGA_GUILD_HALL_DOC_PATH,
        LP57OMEGA_TEMPLE_DOC_PATH,
        LP57OMEGA_DEEP_CONTROL_DOC_PATH,
        LP57OMEGA_RECEIPT_PATH,
        LP57OMEGA_GUILD_HALL_DOC_MIRROR,
        LP57OMEGA_TEMPLE_DOC_MIRROR,
        LP57OMEGA_DEEP_CONTROL_DOC_MIRROR,
        LP57OMEGA_RECEIPT_MIRROR,
        DENSE_65_SHELL_REGISTRY_PATH,
        DENSE_65_RQT_WITNESS_REGISTRY_PATH,
        DENSE_65_RQT_OVERFLOW_REGISTRY_PATH,
        DENSE_65_MANIFEST_PATH,
        DENSE_65_SHELL_REGISTRY_MIRROR,
        DENSE_65_RQT_WITNESS_REGISTRY_MIRROR,
        DENSE_65_RQT_OVERFLOW_REGISTRY_MIRROR,
        DENSE_65_MANIFEST_MIRROR,
        COMMAND_MEMBRANE_PACKET_SCHEMA_PATH,
        COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH,
        COMMAND_MEMBRANE_EVENT_REGISTRY_PATH,
        COMMAND_MEMBRANE_CLAIM_LEDGER_PATH,
        COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH,
        COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH,
        COMMAND_MEMBRANE_MANIFEST_PATH,
        COMMAND_MEMBRANE_PACKET_SCHEMA_MIRROR,
        COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_MIRROR,
        COMMAND_MEMBRANE_EVENT_REGISTRY_MIRROR,
        COMMAND_MEMBRANE_CLAIM_LEDGER_MIRROR,
        COMMAND_MEMBRANE_CAPILLARY_REGISTRY_MIRROR,
        COMMAND_MEMBRANE_LATENCY_REGISTRY_MIRROR,
        COMMAND_MEMBRANE_MANIFEST_MIRROR,
        *visual_atlas_generated,
        *visual_atlas_mirror_generated,
        *HEMISPHERE_DOCS.values(),
        *mirror_paths(),
    ]
    cleanup_previous_outputs(paths)


def normalize_weights(math_weight: float) -> tuple[float, float]:
    rounded_math = round(math_weight, 6)
    rounded_myth = round(1.0 - rounded_math, 6)
    return rounded_math, rounded_myth


def project_record(
    record: dict[str, Any],
    docs_gate_status: str,
    aqm_lane: dict[str, Any],
    anchors: list[Any],
    station_map: dict[str, dict[str, Any]],
    semantic_mass_weights: dict[str, float],
    route_quality_factor: float,
    tesseract_bundle: dict[str, Any],
) -> dict[str, Any]:
    title = record_title(record)
    family = infer_family(Path(record["relative_path"]).name, record.get("excerpt", ""))
    family_label = FAMILY_LABELS.get(family, family)
    component_scores = compute_component_scores(record, family, station_map)
    raw_math_weight = weighted_math_score(component_scores)
    math_weight, myth_weight = normalize_weights(raw_math_weight)
    primary_hemisphere = "MATH" if math_weight >= myth_weight else "MYTH"
    bridge_class = (
        "commissure_bridge"
        if 0.45 <= math_weight <= 0.55
        else ("math_primary" if primary_hemisphere == "MATH" else "myth_primary")
    )
    bridge_intensity = round(max(0.0, 1.0 - abs(math_weight - 0.5) * 2.0), 6)
    tract = resolve_tract(family, record, station_map)
    basis_anchor_ids = assign_basis_anchor_ids(record, anchors, family, primary_hemisphere)
    appendix_support = infer_appendix_links(title, record.get("excerpt", ""), family)
    tesseract_entry = lookup_tesseract_record(
        tesseract_bundle,
        record_id=record.get("record_id", ""),
        path=record.get("path", ""),
        relative_path=record.get("relative_path", ""),
    )
    tesseract_route_plan = route_plan_for_record(
        tesseract_bundle,
        record_id=record.get("record_id", ""),
        path=record.get("path", ""),
        relative_path=record.get("relative_path", ""),
    )
    if tesseract_entry is not None:
        appendix_support = list(tesseract_entry.get("appendix_support", appendix_support))
    grand_central = (
        "commissure"
        if bridge_class == "commissure_bridge"
        else ("GCL" if primary_hemisphere == "MATH" else "GCR")
    )
    hemisphere_hub_id = MATH_HUB_ID if primary_hemisphere == "MATH" else MYTH_HUB_ID
    holo_address = build_holo_address(
        primary_hemisphere=primary_hemisphere,
        tract=tract,
        family=family,
        anchor_ids=basis_anchor_ids,
        record_id=record["record_id"],
    )
    metro_ids = metro_line_ids(
        primary_hemisphere=primary_hemisphere,
        bridge_class=bridge_class,
        family=family,
        tract=tract,
        anchor_ids=basis_anchor_ids,
        record_id=record["record_id"],
    )
    semantic_mass = semantic_mass_weights.get(record.get("top_level") or "", 1.0)
    route_quality = route_quality_factor or 1.0
    hemisphere_weight = math_weight if primary_hemisphere == "MATH" else myth_weight
    salience = round(hemisphere_weight * semantic_mass * route_quality, 6)
    confidence = compute_confidence(record, math_weight)
    scoring_mode = (
        "aqm_deterministic_text"
        if record.get("text_extractable")
        else "aqm_metadata_only"
    )
    trace_payload = {
        "record_id": record["record_id"],
        "path": record["relative_path"],
        "family": family,
        "component_scores": component_scores,
        "aqm_lane_truth": aqm_lane.get("truth", "UNKNOWN"),
        "aqm_next_seed": aqm_lane.get("next_seed", ""),
        "docs_gate_status": docs_gate_status,
        "basis_anchor_ids": basis_anchor_ids,
        "tract": tract,
        "bridge_class": bridge_class,
    }
    aqm_trace_hash = trace_hash(trace_payload)
    navigation = {
        "record_id": record["record_id"],
        "path": record["path"],
        "duplicate_aliases": record.get("duplicate_paths", []),
        "math_weight": math_weight,
        "myth_weight": myth_weight,
        "primary_hemisphere": primary_hemisphere,
        "bridge_class": bridge_class,
        "bridge_intensity": bridge_intensity,
        "grand_central": grand_central,
        "tract": tract,
        "family": family,
        "basis_anchor_ids": basis_anchor_ids,
        "holo_address": holo_address,
        "metro_line_ids": metro_ids,
        "appendix_support": appendix_support,
        "hub_id": UNIFIED_HUB_ID,
        "hemisphere_hub_id": hemisphere_hub_id,
        "aqm_trace_hash": aqm_trace_hash,
        "docs_gate_status": docs_gate_status,
    }
    projected = {
        "record_id": record["record_id"],
        "title": title,
        "path": record["path"],
        "relative_path": record["relative_path"],
        "top_level": record.get("top_level", "<unknown>"),
        "sha256": record["sha256"],
        "kind": record.get("kind", "unknown"),
        "extension": record.get("extension", ""),
        "size_bytes": record.get("size_bytes", 0),
        "modified_at": record.get("modified_at", ""),
        "text_extractable": bool(record.get("text_extractable")),
        "duplicate_paths": record.get("duplicate_paths", []),
        "duplicate_record_ids": record.get("duplicate_record_ids", []),
        "source_paths": record.get("source_paths", [record["path"]]),
        "duplicate_count": record.get("duplicate_count", 0),
        "scoring_mode": scoring_mode,
        "math_weight": math_weight,
        "myth_weight": myth_weight,
        "primary_hemisphere": primary_hemisphere,
        "bridge_class": bridge_class,
        "bridge_intensity": bridge_intensity,
        "confidence": confidence,
        "aqm_trace_hash": aqm_trace_hash,
        "family": family,
        "family_label": family_label,
        "basis_anchor_ids": basis_anchor_ids,
        "holo_address": holo_address,
        "grand_central": grand_central,
        "tract": tract,
        "metro_line_ids": metro_ids,
        "appendix_support": appendix_support,
        "hub_id": UNIFIED_HUB_ID,
        "hemisphere_hub_id": hemisphere_hub_id,
        "docs_gate_status": docs_gate_status,
        "semantic_mass": round(semantic_mass, 6),
        "route_quality": round(route_quality, 6),
        "salience": salience,
        "navigation": navigation,
        "component_scores": component_scores,
    }
    return merge_tesseract_fields(projected, tesseract_entry, tesseract_route_plan)


def build_hub_registry(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    math_records = [record for record in records if record["primary_hemisphere"] == "MATH"]
    myth_records = [record for record in records if record["primary_hemisphere"] == "MYTH"]
    commissure_count = sum(
        1 for record in records if record["bridge_class"] == "commissure_bridge"
    )
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "hubs": [
            {
                "hub_id": UNIFIED_HUB_ID,
                "kind": "unified_hub",
                "label": "Unified Corpus Hub",
                "grand_central": "GC0",
                "connected_records": len(records),
                "connected_hubs": [MATH_HUB_ID, MYTH_HUB_ID],
            },
            {
                "hub_id": MATH_HUB_ID,
                "kind": "hemisphere_hub",
                "label": "MATH Hemisphere Crystal",
                "primary_hemisphere": "MATH",
                "grand_central": "GCL",
                "connected_records": len(math_records),
                "top_families": Counter(record["family"] for record in math_records).most_common(5),
            },
            {
                "hub_id": MYTH_HUB_ID,
                "kind": "hemisphere_hub",
                "label": "MYTH Hemisphere Crystal",
                "primary_hemisphere": "MYTH",
                "grand_central": "GCR",
                "connected_records": len(myth_records),
                "top_families": Counter(record["family"] for record in myth_records).most_common(5),
            },
        ],
        "edges": [
            {
                "edge_id": "HUB-UNIFIED-MATH",
                "source_hub_id": UNIFIED_HUB_ID,
                "target_hub_id": MATH_HUB_ID,
                "kind": "hemisphere_attachment",
            },
            {
                "edge_id": "HUB-UNIFIED-MYTH",
                "source_hub_id": UNIFIED_HUB_ID,
                "target_hub_id": MYTH_HUB_ID,
                "kind": "hemisphere_attachment",
            },
            {
                "edge_id": "HUB-MATH-MYTH-COMMISSURE",
                "source_hub_id": MATH_HUB_ID,
                "target_hub_id": MYTH_HUB_ID,
                "kind": "commissure_backbone",
                "bridge_record_count": commissure_count,
            },
        ],
    }


def build_commissure_registry(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    bridge_records = [
        record for record in records if record["bridge_class"] == "commissure_bridge"
    ]
    edges = []
    for record in bridge_records:
        edges.append(
            {
                "edge_id": f"CM-{record['record_id']}",
                "record_id": record["record_id"],
                "relative_path": record["relative_path"],
                "source_hub_id": MATH_HUB_ID,
                "target_hub_id": MYTH_HUB_ID,
                "grand_central": "commissure",
                "family": record["family"],
                "tract": record["tract"],
                "basis_anchor_ids": record["basis_anchor_ids"],
                "weight": round(1.0 - abs(record["math_weight"] - 0.5) * 2.0, 6),
                "aqm_trace_hash": record["aqm_trace_hash"],
                "reason": "near_tie_bridge",
            }
        )
    family_counts = Counter(record["family"] for record in bridge_records)
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "bridge_count": len(edges),
        "bridge_family_distribution": dict(sorted(family_counts.items())),
        "edges": edges,
    }


def build_metro_registry(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    family_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    anchor_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    corridor_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    level_four_lines = []

    for record in records:
        family_groups[record["family"]].append(record)
        first_anchor = record["basis_anchor_ids"][0]
        anchor_groups[first_anchor].append(record)
        corridor_groups[(record["family"], first_anchor, record["tract"])].append(record)
        level_four_lines.append(
            {
                "line_id": f"L4-SUPERMESH-{record['record_id']}",
                "level": 4,
                "record_id": record["record_id"],
                "station_ids": [
                    UNIFIED_HUB_ID,
                    record["hemisphere_hub_id"],
                    record["grand_central"],
                    f"FAM::{slugify(record['family'])}",
                    f"ANCH::{first_anchor}",
                    record["record_id"],
                ],
                "holo_address": record["holo_address"],
            }
        )

    math_count = sum(1 for record in records if record["primary_hemisphere"] == "MATH")
    myth_count = len(records) - math_count
    bridge_count = sum(
        1 for record in records if record["bridge_class"] == "commissure_bridge"
    )

    level_one = [
        {
            "line_id": "L1-MATH",
            "level": 1,
            "label": "MATH hemisphere hub line",
            "station_ids": [UNIFIED_HUB_ID, MATH_HUB_ID],
            "record_count": math_count,
        },
        {
            "line_id": "L1-MYTH",
            "level": 1,
            "label": "MYTH hemisphere hub line",
            "station_ids": [UNIFIED_HUB_ID, MYTH_HUB_ID],
            "record_count": myth_count,
        },
        {
            "line_id": "L1-COMMISSURE",
            "level": 1,
            "label": "Commissure bridge line",
            "station_ids": [MATH_HUB_ID, MYTH_HUB_ID],
            "record_count": bridge_count,
        },
    ]

    level_two = []
    for family, items in sorted(family_groups.items()):
        level_two.append(
            {
                "line_id": f"L2-FAMILY-{slugify(family)}",
                "level": 2,
                "label": FAMILY_LABELS.get(family, family),
                "station_ids": [UNIFIED_HUB_ID, f"FAM::{slugify(family)}"],
                "record_count": len(items),
                "sample_record_ids": [item["record_id"] for item in items[:5]],
            }
        )
    for anchor_id, items in sorted(anchor_groups.items()):
        level_two.append(
            {
                "line_id": f"L2-ANCHOR-{anchor_id}",
                "level": 2,
                "label": f"Anchor {anchor_id}",
                "station_ids": [UNIFIED_HUB_ID, f"ANCH::{anchor_id}"],
                "record_count": len(items),
                "sample_record_ids": [item["record_id"] for item in items[:5]],
            }
        )

    level_three = []
    for (family, anchor_id, tract), items in sorted(corridor_groups.items()):
        line_id = f"L3-CORRIDOR-{slugify(family)}-{anchor_id}-{tract.upper()}"
        level_three.append(
            {
                "line_id": line_id,
                "level": 3,
                "label": f"{family} x {anchor_id} x {tract}",
                "station_ids": [
                    f"FAM::{slugify(family)}",
                    f"ANCH::{anchor_id}",
                    tract.upper(),
                ],
                "record_count": len(items),
                "sample_record_ids": [item["record_id"] for item in items[:5]],
            }
        )

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "levels": [
            {"level": 1, "name": "hemisphere hubs and commissure bridges", "lines": level_one},
            {"level": 2, "name": "family lines and deep-basis anchor lines", "lines": level_two},
            {
                "level": 3,
                "name": "document-to-document corridor superstructure",
                "lines": level_three,
            },
            {
                "level": 4,
                "name": "full hub-and-record holographic supermesh",
                "lines": level_four_lines,
            },
        ],
    }


def build_manifest(
    atlas_payload: dict[str, Any],
    records: list[dict[str, Any]],
    docs_gate_status: str,
    aqm_lane: dict[str, Any],
    anchors: list[Any],
) -> dict[str, Any]:
    math_count = sum(1 for record in records if record["primary_hemisphere"] == "MATH")
    myth_count = len(records) - math_count
    bridge_count = sum(
        1 for record in records if record["bridge_class"] == "commissure_bridge"
    )
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "aqm_lane": aqm_lane,
        "atlas": {
            "path": str(HEMISPHERE_ATLAS_PATH),
            "timestamp": file_timestamp(HEMISPHERE_ATLAS_PATH),
            "atlas_record_count": atlas_payload.get("record_count", 0),
            "unique_sha_count": len(records),
        },
        "basis": {
            "canonical_sources_path": str(CANONICAL_SOURCES_PATH),
            "anchor_count": len(anchors),
            "anchor_ids": [anchor.anchor_id for anchor in anchors],
        },
        "counts": {
            "record_count": len(records),
            "math_records": math_count,
            "myth_records": myth_count,
            "commissure_records": bridge_count,
        },
        "scoring_weights": {
            "path_prior": 0.30,
            "family_prior": 0.25,
            "title_heading": 0.20,
            "excerpt": 0.20,
            "structural_density": 0.05,
        },
        "outputs": {
            "hemisphere_root": str(HEMISPHERE_ROOT),
            "fleet_mirror_root": str(FLEET_MIRROR_ROOT),
            "record_registry": str(RECORD_REGISTRY_PATH),
            "commissure_registry": str(COMMISSURE_REGISTRY_PATH),
            "metro_registry": str(METRO_REGISTRY_PATH),
            "hub_registry": str(HUB_REGISTRY_PATH),
            "manifest": str(MANIFEST_PATH),
        },
        "required_fields": REQUIRED_FIELDS,
        "notes": [
            "Local-first build. Live Google Docs evidence is not claimed while OAuth remains blocked.",
            "Near-tie documents remain single-home records and cross the commissure through explicit bridge edges.",
            "The deeper-network 16-document basis remains the sole anchor lattice.",
        ],
    }


def render_index_markdown(
    manifest: dict[str, Any],
    hub_registry: dict[str, Any],
    commissure_registry: dict[str, Any],
) -> str:
    counts = manifest["counts"]
    hub_rows = []
    for hub in hub_registry["hubs"]:
        hub_rows.append(
            [
                hub["hub_id"],
                hub["label"],
                str(hub["connected_records"]),
            ]
        )
    return f"""# Myth/MATH Hemisphere Brain

Source of truth: `self_actualize`
Mirror mode: `read-only FLEET presentation`
Docs gate: `{manifest['docs_gate_status']}`

## Build Summary

- atlas path: `{manifest['atlas']['path']}`
- atlas records: `{manifest['atlas']['atlas_record_count']}`
- deduplicated records: `{counts['record_count']}`
- MATH records: `{counts['math_records']}`
- MYTH records: `{counts['myth_records']}`
- commissure bridges: `{counts['commissure_records']}`
- AQM lane truth: `{manifest['aqm_lane']['truth']}`
- AQM live root: `{manifest['aqm_lane']['live_root']}`

## Commands

```powershell
python -m self_actualize.runtime.derive_myth_math_hemisphere_brain
python -m self_actualize.runtime.verify_myth_math_hemisphere_brain
```

## Hubs

{markdown_table(["Hub", "Label", "Connected Records"], hub_rows)}

## Registries

- record registry: `{manifest['outputs']['record_registry']}`
- commissure registry: `{manifest['outputs']['commissure_registry']}`
- metro registry: `{manifest['outputs']['metro_registry']}`
- hub registry: `{manifest['outputs']['hub_registry']}`
- manifest: `{manifest['outputs']['manifest']}`

## Backbone

- unified hub id: `{UNIFIED_HUB_ID}`
- MATH hub id: `{MATH_HUB_ID}`
- MYTH hub id: `{MYTH_HUB_ID}`
- commissure edges: `{commissure_registry['bridge_count']}`
"""


def render_crystal_markdown(
    hemisphere: str,
    records: list[dict[str, Any]],
) -> str:
    sorted_records = sorted(records, key=lambda item: (-item["salience"], item["relative_path"].lower()))
    top_records = sorted_records[:40]
    family_counts = Counter(record["family"] for record in records)
    anchor_counts = Counter(record["basis_anchor_ids"][0] for record in records)
    family_rows = [
        [FAMILY_LABELS.get(family, family), str(count)]
        for family, count in family_counts.most_common(8)
    ]
    anchor_rows = [
        [anchor_id, str(count)]
        for anchor_id, count in anchor_counts.most_common(8)
    ]
    record_rows = [
        [
            record["record_id"],
            f"{record['salience']:.4f}",
            record["family"],
            record["relative_path"],
        ]
        for record in top_records
    ]
    return f"""# {hemisphere} Crystal

Primary hemisphere: `{hemisphere}`
Grand Central exchange: `{"GCL" if hemisphere == "MATH" else "GCR"}`
Connected records: `{len(records)}`

## Dominant Families

{markdown_table(["Family", "Count"], family_rows)}

## Dominant Anchors

{markdown_table(["Anchor", "Count"], anchor_rows)}

## Highest-Salience Records

{markdown_table(["Record", "Salience", "Family", "Relative Path"], record_rows)}

## Full Registry Pointer

All records for this crystal remain linked through:

- `{RECORD_REGISTRY_PATH}`
- `{UNIFIED_HUB_ID}`
"""


def render_hub_markdown(
    hub_registry: dict[str, Any],
    records: list[dict[str, Any]],
) -> str:
    by_top_level = Counter(record["top_level"] for record in records)
    hub_rows = [
        [hub["hub_id"], hub["label"], str(hub["connected_records"])]
        for hub in hub_registry["hubs"]
    ]
    top_level_rows = [
        [name, str(count)]
        for name, count in by_top_level.most_common(12)
    ]
    return f"""# Unified Corpus Hub

Hub id: `{UNIFIED_HUB_ID}`

## Hub Registry

{markdown_table(["Hub", "Label", "Connected Records"], hub_rows)}

## Strongest Connected Bodies

{markdown_table(["Top Level", "Count"], top_level_rows)}

## Law

Every record in the hemisphere registry resolves to `{UNIFIED_HUB_ID}` and then out through:

- `{MATH_HUB_ID}`
- `{MYTH_HUB_ID}`
"""


def render_metro_level_markdown(metro_registry: dict[str, Any], level_index: int) -> str:
    level = metro_registry["levels"][level_index]
    rows = []
    for line in level["lines"][:80]:
        rows.append(
            [
                line["line_id"],
                str(line.get("record_count", 1)),
                ", ".join(line["station_ids"][:4]),
            ]
        )
    return f"""# Metro Level {level['level']}

{level['name']}

## Sampled Lines

{markdown_table(["Line", "Record Count", "Stations"], rows)}

## Registry Pointer

- `{METRO_REGISTRY_PATH}`
"""


def render_receipt(
    manifest: dict[str, Any],
    atlas_payload: dict[str, Any],
    docs_gate_status: str,
) -> str:
    return f"""# Hemisphere Build Receipt

- generated at: `{manifest['generated_at']}`
- derivation version: `{manifest['derivation_version']}`
- command: `{DERIVATION_COMMAND}`
- docs gate: `{docs_gate_status}`
- atlas records: `{atlas_payload['record_count']}`
- deduplicated records: `{manifest['counts']['record_count']}`
- MATH records: `{manifest['counts']['math_records']}`
- MYTH records: `{manifest['counts']['myth_records']}`
- commissure records: `{manifest['counts']['commissure_records']}`
- AQM lane source: `{AQM_LANE_PATH}`
- atlas path: `{HEMISPHERE_ATLAS_PATH}`
- mirror root: `{FLEET_MIRROR_ROOT}`
"""


def render_route_index_markdown(
    route_manifest: dict[str, Any],
    route_coverage_registry: dict[str, Any],
) -> str:
    counts = route_manifest["counts"]
    target_rows = [
        [system, str(count)]
        for system, count in route_manifest.get("primary_target_distribution", {}).items()
    ][:12]
    return f"""# Dual-Hemisphere Route Index

Docs gate: `{route_manifest['docs_gate_status']}`

## Counts

- records: `{counts['records']}`
- route packets: `{counts['route_packets']}`
- direct edges: `{counts['direct_edges']}`
- coverage rows: `{counts['coverage_rows']}`
- coverage complete: `{route_coverage_registry['complete_count']}`

## Primary Target Systems

{markdown_table(["System", "Primary Routes"], target_rows or [["<none>", "0"]])}

## Route Registries

- `{DUAL_ROUTE_REGISTRY_PATH}`
- `{DIRECT_EDGE_REGISTRY_PATH}`
- `{ROUTE_COVERAGE_REGISTRY_PATH}`
- `{ROUTE_MANIFEST_PATH}`
"""


def render_route_atlas_markdown(
    hemisphere: str,
    route_registry: dict[str, Any],
) -> str:
    routes = [
        route
        for route in route_registry["routes"]
        if route["hemisphere"] == hemisphere
    ]
    rows = [
        [
            route["record_id"],
            route["route_role"],
            route["target_system"],
            route["dominant_lens_system"],
            route["field_id"],
            route["zpoint_id"],
        ]
        for route in routes[:80]
    ]
    return f"""# {hemisphere} Direct-Route Atlas

Direct routes into `{MATH_HUB_ID if hemisphere == 'MATH' else MYTH_HUB_ID}`

{markdown_table(["Record", "Role", "System", "Lens", "Field", "Z"], rows or [["<none>", "-", "-", "-", "-", "-"]])}
"""


def render_route_crosswalk_markdown(records: list[dict[str, Any]]) -> str:
    rows = []
    for record in records[:80]:
        math_route = record["hemisphere_routes"]["MATH"]
        myth_route = record["hemisphere_routes"]["MYTH"]
        rows.append(
            [
                record["record_id"],
                record["primary_hemisphere"],
                math_route["target_system"],
                myth_route["target_system"],
                f"{record['bridge_intensity']:.3f}",
            ]
        )
    return f"""# Dual-Hemisphere Crosswalk Map

{markdown_table(["Record", "Primary", "MATH System", "MYTH System", "Bridge"], rows or [["<none>", "-", "-", "-", "-"]])}
"""


def render_route_coverage_markdown(
    route_coverage_registry: dict[str, Any],
) -> str:
    rows = []
    for coverage in route_coverage_registry["records"][:80]:
        rows.append(
            [
                coverage["record_id"],
                "yes" if coverage["complete"] else "no",
                str(sum(1 for value in coverage["MATH"].values() if value)),
                str(sum(1 for value in coverage["MYTH"].values() if value)),
            ]
        )
    return f"""# Route Coverage Receipt

Complete rows: `{route_coverage_registry['complete_count']}` / `{route_coverage_registry['record_count']}`

{markdown_table(["Record", "Complete", "MATH Systems", "MYTH Systems"], rows or [["<none>", "no", "0", "0"]])}
"""


def render_navigator_index_markdown(
    navigator_manifest: dict[str, Any],
) -> str:
    counts = navigator_manifest["counts"]
    facet_rows = [
        [facet_name, str(count)]
        for facet_name, count in navigator_manifest.get("facet_cardinalities", {}).items()
    ][:12]
    return f"""# Navigator Index

Docs gate: `{navigator_manifest['docs_gate_status']}`

## Counts

- records: `{counts['records']}`
- route packets: `{counts['route_packets']}`
- direct edges: `{counts['direct_edges']}`
- alias keys: `{counts['alias_keys']}`
- alias entries: `{counts['alias_entries']}`
- facet dimensions: `{counts['facet_dimensions']}`
- neighbor records: `{counts['neighbor_records']}`

## Commands

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>
python -m self_actualize.runtime.query_myth_math_hemisphere_brain search --query <text> --system <system>
python -m self_actualize.runtime.query_myth_math_hemisphere_brain facet --family <family>
```

## Facet Cardinalities

{markdown_table(["Facet", "Value Count"], facet_rows or [["<none>", "0"]])}
"""


def render_query_cookbook_markdown() -> str:
    return """# Navigator Query Cookbook

## Exact Record Lookup

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id 368bd2ec7d2e64e2f5739be7
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --path "Athena FLEET\\athena_fleet_corpus_atlas.json"
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --title "settings.local"
```

## Mixed Search

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain search --query aqm --hemisphere MATH --system CoreMetro --anchor DN03
python -m self_actualize.runtime.query_myth_math_hemisphere_brain search --query bridge --route-mode commissure_direct --expanded
```

## Facet Browse

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain facet --system GrandCentral
python -m self_actualize.runtime.query_myth_math_hemisphere_brain facet --lens SC
python -m self_actualize.runtime.query_myth_math_hemisphere_brain facet --hemisphere MYTH
```
"""


def render_navigator_hotspots_markdown(
    hemisphere: str,
    route_registry: dict[str, Any],
) -> str:
    routes = [
        route
        for route in route_registry["routes"]
        if route["hemisphere"] == hemisphere
    ]
    system_rows = [
        [system_id, str(count)]
        for system_id, count in Counter(route["target_system"] for route in routes).most_common(10)
    ]
    family_rows = [
        [family, str(count)]
        for family, count in Counter(route["family"] for route in routes).most_common(10)
    ]
    lens_rows = [
        [lens_id, str(count)]
        for lens_id, count in Counter(route["dominant_lens_system"] for route in routes).most_common(10)
    ]
    field_rows = [
        [field_id, str(count)]
        for field_id, count in Counter(route["field_id"] for route in routes).most_common(10)
    ]
    return f"""# {hemisphere} Facet Hotspots

## Target Systems

{markdown_table(["System", "Routes"], system_rows or [["<none>", "0"]])}

## Families

{markdown_table(["Family", "Routes"], family_rows or [["<none>", "0"]])}

## Dominant Lenses

{markdown_table(["Lens", "Routes"], lens_rows or [["<none>", "0"]])}

## Fields

{markdown_table(["Field", "Routes"], field_rows or [["<none>", "0"]])}
"""


def render_navigator_entrypoints_markdown(records: list[dict[str, Any]]) -> str:
    ordered = sorted(
        records,
        key=lambda item: (-item["bridge_intensity"], -item["salience"], item["relative_path"].lower()),
    )[:80]
    rows = []
    for record in ordered:
        rows.append(
            [
                record["record_id"],
                record["primary_hemisphere"],
                record["hemisphere_routes"]["MATH"]["target_system"],
                record["hemisphere_routes"]["MYTH"]["target_system"],
                (record.get("basis_anchor_ids") or ["DN00"])[0],
                f"{record['bridge_intensity']:.3f}",
            ]
        )
    return f"""# Cross-Hemisphere Entrypoint Atlas

{markdown_table(["Record", "Primary", "MATH System", "MYTH System", "Anchor", "Bridge"], rows or [["<none>", "-", "-", "-", "-", "-"]])}
"""


def render_route_composer_index_markdown(
    composer_manifest: dict[str, Any],
) -> str:
    counts = composer_manifest.get("counts", {})
    facet_rows = [
        [facet_name, str(count)]
        for facet_name, count in composer_manifest.get("facet_coverage", {}).items()
    ]
    return f"""# Route Composer Index

Docs gate: `{composer_manifest['docs_gate_status']}`

## Counts

- seed groups: `{counts.get('seed_groups', 0)}`
- MATH starters: `{counts.get('math_starters', 0)}`
- MYTH starters: `{counts.get('myth_starters', 0)}`
- bridge starters: `{counts.get('bridge_starters', 0)}`
- facet starters: `{counts.get('facet_starters', 0)}`

## Commands

```powershell
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes search --query <text> --system <system>
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes facet --family <family>
```

## Facet Coverage

{markdown_table(["Facet", "Starter Count"], facet_rows or [["<none>", "0"]])}
"""


def render_route_composer_cookbook_markdown() -> str:
    return """# Route Composer Cookbook

## Exact Seed Route

```powershell
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id 368bd2ec7d2e64e2f5739be7
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --path "DEEPER CRYSTALIZATION\\ACTIVE_NERVOUS_SYSTEM\\02_CORPUS_CAPSULES\\05_aqm_text_book.md"
```

## Goal-Driven Route

```powershell
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes search --query aqm --hemisphere MATH --system AppendixOnlyMetro
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes search --query bridge --route-mode commissure_direct --expanded
```

## Facet Route

```powershell
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes facet --anchor DN01
python -m self_actualize.runtime.compose_myth_math_hemisphere_routes facet --family manuscript-architecture
```
"""


def render_route_composer_group_markdown(
    heading: str,
    seed_registry: dict[str, Any],
    group_name: str,
) -> str:
    rows = []
    for entry in seed_registry.get("groups", {}).get(group_name, [])[:80]:
        route_bundle = entry.get("route_bundle", {})
        seed_record = route_bundle.get("seed_record", {}) or {}
        math_route = route_bundle.get("math_itinerary", {}).get("stages", [{}])[0]
        myth_route = route_bundle.get("myth_itinerary", {}).get("stages", [{}])[0]
        math_system = (
            math_route.get("selected_route", {}).get("target_system", "")
            if math_route.get("kind") == "record_stop"
            else ""
        )
        myth_system = (
            myth_route.get("selected_route", {}).get("target_system", "")
            if myth_route.get("kind") == "record_stop"
            else ""
        )
        rows.append(
            [
                str(entry.get("rank", "")),
                seed_record.get("record_id", ""),
                seed_record.get("primary_hemisphere", ""),
                math_system,
                myth_system,
                route_bundle.get("bridge_profile", {}).get("mode", ""),
            ]
        )
    return f"""# {heading}

{markdown_table(["Rank", "Record", "Primary", "MATH System", "MYTH System", "Bridge"], rows or [["-", "<none>", "-", "-", "-", "-"]])}
"""


def render_route_composer_facet_markdown(
    facet_registry: dict[str, Any],
) -> str:
    rows = []
    for facet_name, values in sorted(facet_registry.get("facets", {}).items()):
        for facet_value, entry in sorted(values.items()):
            route_bundle = entry.get("route_bundle", {})
            seed_record = route_bundle.get("seed_record", {}) or {}
            rows.append(
                [
                    facet_name,
                    facet_value,
                    seed_record.get("record_id", ""),
                    seed_record.get("primary_hemisphere", ""),
                    route_bundle.get("bridge_profile", {}).get("mode", ""),
                ]
            )
    return f"""# Facet Route Starters

{markdown_table(["Facet", "Value", "Seed Record", "Primary", "Bridge"], rows or [["<none>", "<none>", "<none>", "-", "-"]])}
"""


def synthesis_preview(synthesis_bundle: dict[str, Any]) -> str:
    unified = synthesis_bundle.get("unified_synthesis", {})
    bullets = unified.get("bullets", [])
    if bullets:
        return bullets[0].get("text", "")[:120]
    return ""


def render_synthesis_index_markdown(
    synthesis_manifest: dict[str, Any],
) -> str:
    counts = synthesis_manifest.get("counts", {})
    facet_rows = [
        [facet_name, str(count)]
        for facet_name, count in synthesis_manifest.get("facet_coverage", {}).items()
    ]
    return f"""# Synthesis Index

Docs gate: `{synthesis_manifest['docs_gate_status']}`

## Counts

- evidence records: `{counts.get('evidence_records', 0)}`
- seed groups: `{counts.get('seed_groups', 0)}`
- MATH starters: `{counts.get('math_starters', 0)}`
- MYTH starters: `{counts.get('myth_starters', 0)}`
- bridge starters: `{counts.get('bridge_starters', 0)}`
- facet starters: `{counts.get('facet_starters', 0)}`

## Commands

```powershell
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes search --query <text> --system <system>
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes facet --family <family>
```

## Facet Coverage

{markdown_table(["Facet", "Starter Count"], facet_rows or [["<none>", "0"]])}
"""


def render_synthesis_cookbook_markdown() -> str:
    return """# Synthesis Cookbook

## Exact Synthesis

```powershell
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id 368bd2ec7d2e64e2f5739be7
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --path "DEEPER CRYSTALIZATION\\ACTIVE_NERVOUS_SYSTEM\\02_CORPUS_CAPSULES\\05_aqm_text_book.md"
```

## Goal-Driven Synthesis

```powershell
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes search --query aqm --hemisphere MATH --system AppendixOnlyMetro
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes search --query bridge --route-mode commissure_direct --expanded
```

## Facet Synthesis

```powershell
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes facet --anchor DN01
python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes facet --family manuscript-architecture
```
"""


def render_synthesis_group_markdown(
    heading: str,
    synthesis_seed_registry: dict[str, Any],
    group_name: str,
) -> str:
    rows = []
    for entry in synthesis_seed_registry.get("groups", {}).get(group_name, [])[:80]:
        synthesis_bundle = entry.get("synthesis_bundle", {})
        seed_record = synthesis_bundle.get("seed_record", {}) or {}
        rows.append(
            [
                str(entry.get("rank", "")),
                seed_record.get("record_id", ""),
                seed_record.get("primary_hemisphere", ""),
                synthesis_bundle.get("bridge_interpretation", {}).get("bullets", [{}])[0].get("text", "")[:80],
                synthesis_preview(synthesis_bundle),
            ]
        )
    return f"""# {heading}

{markdown_table(["Rank", "Record", "Primary", "Bridge", "Unified Preview"], rows or [["-", "<none>", "-", "-", "-"]])}
"""


def render_synthesis_facet_markdown(
    synthesis_facet_registry: dict[str, Any],
) -> str:
    rows = []
    for facet_name, values in sorted(synthesis_facet_registry.get("facets", {}).items()):
        for facet_value, entry in sorted(values.items()):
            synthesis_bundle = entry.get("synthesis_bundle", {})
            seed_record = synthesis_bundle.get("seed_record", {}) or {}
            rows.append(
                [
                    facet_name,
                    facet_value,
                    seed_record.get("record_id", ""),
                    seed_record.get("primary_hemisphere", ""),
                    synthesis_preview(synthesis_bundle),
                ]
            )
    return f"""# Facet Synthesis Atlas

{markdown_table(["Facet", "Value", "Seed Record", "Primary", "Unified Preview"], rows or [["<none>", "<none>", "<none>", "-", "-"]])}
"""


def guided_tour_preview(tour_bundle: dict[str, Any]) -> str:
    seed_record = tour_bundle.get("seed_record", {}) or {}
    synthesis_landing = tour_bundle.get("synthesis_landing", {}) or {}
    hub_crossing = tour_bundle.get("hub_crossing", {}) or {}
    return (
        f"{seed_record.get('title', '')[:50]} | "
        f"{hub_crossing.get('bridge_mode', '')} | "
        f"{synthesis_landing.get('title', '')}"
    ).strip(" |")


def render_guided_tour_index_markdown(guided_tour_manifest: dict[str, Any]) -> str:
    counts = guided_tour_manifest.get("counts", {})
    group_counts = counts.get("group_counts", {})
    rows = [
        [group_name, str(count)]
        for group_name, count in sorted(group_counts.items())
    ]
    return f"""# Guided Tour Index

Docs gate: `{guided_tour_manifest.get('docs_gate_status', 'UNKNOWN')}`

## Counts

- seed starters: `{counts.get('seed_starters', 0)}`
- page starters: `{counts.get('page_starters', 0)}`

## Commands

```powershell
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas record --record-id <record_id>
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas search --query <text> --system <system>
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas facet --family <family>
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas page --page-id <page_id>
```

## Starter Groups

{markdown_table(["Group", "Count"], rows or [["<none>", "0"]])}
"""


def render_guided_tour_cookbook_markdown() -> str:
    return """# Guided Tour Cookbook

## Record Tours

```powershell
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas record --record-id 368bd2ec7d2e64e2f5739be7
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas record --path "DEEPER CRYSTALIZATION\\ACTIVE_NERVOUS_SYSTEM\\02_CORPUS_CAPSULES\\05_aqm_text_book.md"
```

## Search Tours

```powershell
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas search --query aqm --family manuscript-architecture
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas search --query bridge --hemisphere MYTH --expanded
```

## Facet And Page Tours

```powershell
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas facet --anchor DN01
python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas page --page-id VA-FAMILY-manuscript_architecture
```
"""


def render_guided_tour_group_markdown(
    heading: str,
    guided_tour_seed_registry: dict[str, Any],
    group_name: str,
) -> str:
    rows = []
    for entry in guided_tour_seed_registry.get("groups", {}).get(group_name, []):
        tour_bundle = entry.get("guided_tour", {})
        seed_record = tour_bundle.get("seed_record", {}) or {}
        rows.append(
            [
                str(entry.get("order", "")),
                entry.get("page_id", ""),
                seed_record.get("record_id", ""),
                seed_record.get("primary_hemisphere", ""),
                guided_tour_preview(tour_bundle),
            ]
        )
    return f"""# {heading}

{markdown_table(["Order", "Page", "Seed Record", "Primary", "Preview"], rows or [["-", "<none>", "<none>", "-", "-"]])}
"""


def expedition_preview(expedition_bundle: dict[str, Any]) -> str:
    seed_record = expedition_bundle.get("seed_record", {}) or {}
    companion_counts = expedition_bundle.get("proof_summary", {}).get("companion_counts", {})
    companion_total = sum(companion_counts.values())
    page_count = len(expedition_bundle.get("page_matrix", {}).get("unique_pages", []))
    return (
        f"{seed_record.get('title', '')[:40]} | companions={companion_total} | pages={page_count}"
    ).strip(" |")


def render_expedition_index_markdown(expedition_manifest: dict[str, Any]) -> str:
    counts = expedition_manifest.get("counts", {})
    rows = [
        [group_name, str(count)]
        for group_name, count in sorted(counts.get("group_counts", {}).items())
    ]
    return f"""# Expedition Index

Docs gate: `{expedition_manifest.get('docs_gate_status', 'UNKNOWN')}`

## Counts

- seed starters: `{counts.get('seed_starters', 0)}`
- page starters: `{counts.get('page_starters', 0)}`

## Commands

```powershell
python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas record --record-id <record_id>
python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas search --query <text> --system <system>
python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas facet --family <family>
python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas page --page-id <page_id>
```

## Starter Groups

{markdown_table(["Group", "Count"], rows or [["<none>", "0"]])}
"""


def render_expedition_cookbook_markdown() -> str:
    return """# Expedition Cookbook

```powershell
python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas record --record-id 368bd2ec7d2e64e2f5739be7
python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas search --query aqm --family manuscript-architecture
python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas facet --anchor DN01
python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas page --page-id VA-OVERVIEW
```
"""


def render_expedition_group_markdown(
    heading: str,
    expedition_seed_registry: dict[str, Any],
    group_name: str,
) -> str:
    rows = []
    for entry in expedition_seed_registry.get("groups", {}).get(group_name, []):
        bundle = entry.get("expedition_bundle", {})
        seed_record = bundle.get("seed_record", {}) or {}
        rows.append(
            [
                str(entry.get("order", "")),
                entry.get("page_id", ""),
                seed_record.get("record_id", ""),
                seed_record.get("primary_hemisphere", ""),
                expedition_preview(bundle),
            ]
        )
    return f"""# {heading}

{markdown_table(["Order", "Page", "Seed Record", "Primary", "Preview"], rows or [["-", "<none>", "<none>", "-", "-"]])}
"""


def constellation_preview(constellation_bundle: dict[str, Any]) -> str:
    return (
        f"{constellation_bundle.get('slice_type', '')} | "
        f"records={constellation_bundle.get('proof_summary', {}).get('record_node_count', 0)} | "
        f"edges={constellation_bundle.get('proof_summary', {}).get('edge_count', 0)}"
    ).strip(" |")


def render_constellation_index_markdown(constellation_manifest: dict[str, Any]) -> str:
    counts = constellation_manifest.get("counts", {})
    rows = [
        [group_name, str(count)]
        for group_name, count in sorted(counts.get("group_counts", {}).items())
    ]
    return f"""# Constellation Index

Docs gate: `{constellation_manifest.get('docs_gate_status', 'UNKNOWN')}`

## Counts

- node count: `{counts.get('node_count', 0)}`
- edge count: `{counts.get('edge_count', 0)}`
- page count: `{counts.get('page_count', 0)}`

## Commands

```powershell
python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas record --record-id <record_id>
python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas search --query <text> --system <system>
python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas facet --family <family>
python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas page --page-id <page_id>
```

## Starter Groups

{markdown_table(["Group", "Count"], rows or [["<none>", "0"]])}
"""


def render_constellation_cookbook_markdown() -> str:
    return """# Constellation Cookbook

```powershell
python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas record --record-id 368bd2ec7d2e64e2f5739be7
python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas search --query aqm --family manuscript-architecture
python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas facet --anchor DN01
python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas page --page-id VA-TARGET-SYSTEM
```
"""


def render_constellation_group_markdown(
    heading: str,
    constellation_page_registry: dict[str, Any],
    group_name: str,
) -> str:
    rows = []
    for order, entry in enumerate(constellation_page_registry.get("pages", []), start=1):
        if group_name not in entry.get("starter_groups", []):
            continue
        bundle = entry.get("constellation_bundle", {})
        seed_record = bundle.get("seed_record", {}) or {}
        rows.append(
            [
                str(order),
                entry.get("page_id", ""),
                seed_record.get("record_id", ""),
                entry.get("page_type", ""),
                constellation_preview(bundle),
            ]
        )
    return f"""# {heading}

{markdown_table(["Order", "Page", "Seed Record", "Page Type", "Preview"], rows or [["-", "<none>", "<none>", "-", "-"]])}
"""


def render_constellation_coverage_markdown(constellation_manifest: dict[str, Any]) -> str:
    counts = constellation_manifest.get("counts", {})
    return f"""# Constellation Coverage Receipt

Docs gate: `{constellation_manifest.get('docs_gate_status', 'UNKNOWN')}`

- node count: `{counts.get('node_count', 0)}`
- edge count: `{counts.get('edge_count', 0)}`
- page count: `{counts.get('page_count', 0)}`
- record cap: `{constellation_manifest.get('record_cap', 0)}`
"""


def replay_preview(replay_bundle: dict[str, Any]) -> str:
    seed_record = replay_bundle.get("seed_record", {}) or {}
    return (
        f"{seed_record.get('title', '')[:40]} | "
        f"passes={len(replay_bundle.get('replay_passes', []))} | "
        f"supports={len(replay_bundle.get('support_ids', []))}"
    ).strip(" |")


def render_replay_index_markdown(replay_manifest: dict[str, Any]) -> str:
    counts = replay_manifest.get("counts", {})
    rows = [
        [group_name, str(count)]
        for group_name, count in sorted(counts.get("group_counts", {}).items())
    ]
    return f"""# Replay Index

Docs gate: `{replay_manifest.get('docs_gate_status', 'UNKNOWN')}`

## Counts

- seed starters: `{counts.get('seed_starters', 0)}`
- page starters: `{counts.get('page_starters', 0)}`

## Commands

```powershell
python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas record --record-id <record_id>
python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas search --query <text> --system <system>
python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas facet --family <family>
python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas page --page-id <page_id>
```

## Starter Groups

{markdown_table(["Group", "Count"], rows or [["<none>", "0"]])}
"""


def render_replay_cookbook_markdown() -> str:
    return """# Replay Cookbook

```powershell
python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas record --record-id 368bd2ec7d2e64e2f5739be7
python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas search --query aqm --family manuscript-architecture
python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas facet --anchor DN01
python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas page --page-id VA-OVERVIEW
```
"""


def render_replay_group_markdown(
    heading: str,
    replay_seed_registry: dict[str, Any],
    group_name: str,
) -> str:
    rows = []
    for entry in replay_seed_registry.get("groups", {}).get(group_name, []):
        bundle = entry.get("replay_bundle", {})
        seed_record = bundle.get("seed_record", {}) or {}
        rows.append(
            [
                str(entry.get("rank", "")),
                seed_record.get("record_id", ""),
                seed_record.get("primary_hemisphere", ""),
                replay_preview(bundle),
            ]
        )
    return f"""# {heading}

{markdown_table(["Rank", "Seed Record", "Primary", "Preview"], rows or [["-", "<none>", "-", "-"]])}
"""


def render_replay_coverage_markdown(
    replay_manifest: dict[str, Any],
    replay_page_registry: dict[str, Any],
) -> str:
    return f"""# Replay Coverage Receipt

Docs gate: `{replay_manifest.get('docs_gate_status', 'UNKNOWN')}`

- replay passes: `{len(replay_manifest.get('replay_pass_order', []))}`
- seed starters: `{replay_manifest.get('counts', {}).get('seed_starters', 0)}`
- page starters: `{replay_page_registry.get('page_count', 0)}`
"""


def observatory_preview(observatory_bundle: dict[str, Any]) -> str:
    seed_record = observatory_bundle.get("seed_record", {}) or {}
    return (
        f"{seed_record.get('title', '')[:36]} | "
        f"{observatory_bundle.get('best_tour', {}).get('bridge_mode', '')} | "
        f"watchpoints={len(observatory_bundle.get('watchpoints', []))}"
    ).strip(" |")


def render_observatory_index_markdown(observatory_manifest: dict[str, Any]) -> str:
    counts = observatory_manifest.get("counts", {})
    rows = [
        [group_name, str(count)]
        for group_name, count in sorted(counts.get("group_counts", {}).items())
    ]
    return f"""# Observatory Index

Docs gate: `{observatory_manifest.get('docs_gate_status', 'UNKNOWN')}`

## Counts

- seed starters: `{counts.get('seed_starters', 0)}`
- page starters: `{counts.get('page_starters', 0)}`

## Commands

```powershell
python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas record --record-id <record_id>
python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas search --query <text> --system <system>
python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas facet --family <family>
python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas page --page-id <page_id>
```

## Starter Groups

{markdown_table(["Group", "Count"], rows or [["<none>", "0"]])}
"""


def render_observatory_cookbook_markdown() -> str:
    return """# Observatory Cookbook

```powershell
python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas record --record-id 368bd2ec7d2e64e2f5739be7
python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas search --query aqm --family manuscript-architecture
python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas facet --anchor DN01
python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas page --page-id VA-OVERVIEW
```
"""


def render_observatory_group_markdown(
    heading: str,
    observatory_seed_registry: dict[str, Any],
    group_name: str,
) -> str:
    rows = []
    for entry in observatory_seed_registry.get("groups", {}).get(group_name, []):
        bundle = entry.get("observatory_bundle", {})
        seed_record = bundle.get("seed_record", {}) or {}
        rows.append(
            [
                str(entry.get("order", "")),
                entry.get("page_id", ""),
                seed_record.get("record_id", ""),
                seed_record.get("primary_hemisphere", ""),
                observatory_preview(bundle),
            ]
        )
    return f"""# {heading}

{markdown_table(["Order", "Page", "Seed Record", "Primary", "Preview"], rows or [["-", "<none>", "<none>", "-", "-"]])}
"""


def render_observatory_coverage_markdown(
    observatory_manifest: dict[str, Any],
    observatory_page_registry: dict[str, Any],
) -> str:
    return f"""# Observatory Coverage Receipt

Docs gate: `{observatory_manifest.get('docs_gate_status', 'UNKNOWN')}`

- seed starters: `{observatory_manifest.get('counts', {}).get('seed_starters', 0)}`
- page starters: `{observatory_page_registry.get('page_count', 0)}`
"""


def write_markdown_surfaces(
    manifest: dict[str, Any],
    hub_registry: dict[str, Any],
    commissure_registry: dict[str, Any],
    metro_registry: dict[str, Any],
    route_registry: dict[str, Any],
    route_coverage_registry: dict[str, Any],
    route_manifest: dict[str, Any],
    navigator_manifest: dict[str, Any],
    composer_seed_registry: dict[str, Any],
    composer_facet_registry: dict[str, Any],
    composer_manifest: dict[str, Any],
    synthesis_seed_registry: dict[str, Any],
    synthesis_facet_registry: dict[str, Any],
    synthesis_manifest: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    visual_atlas_markdown_pages: dict[str, str],
    guided_tour_seed_registry: dict[str, Any],
    guided_tour_manifest: dict[str, Any],
    expedition_seed_registry: dict[str, Any],
    expedition_manifest: dict[str, Any],
    constellation_page_registry: dict[str, Any],
    constellation_manifest: dict[str, Any],
    replay_seed_registry: dict[str, Any],
    replay_page_registry: dict[str, Any],
    replay_manifest: dict[str, Any],
    observatory_seed_registry: dict[str, Any],
    observatory_page_registry: dict[str, Any],
    observatory_manifest: dict[str, Any],
    records: list[dict[str, Any]],
    atlas_payload: dict[str, Any],
    docs_gate_status: str,
) -> None:
    math_records = [record for record in records if record["primary_hemisphere"] == "MATH"]
    myth_records = [record for record in records if record["primary_hemisphere"] == "MYTH"]

    write_text(
        HEMISPHERE_DOCS["index"],
        render_index_markdown(manifest, hub_registry, commissure_registry),
    )
    write_text(
        HEMISPHERE_DOCS["math"],
        render_crystal_markdown("MATH", math_records),
    )
    write_text(
        HEMISPHERE_DOCS["myth"],
        render_crystal_markdown("MYTH", myth_records),
    )
    write_text(
        HEMISPHERE_DOCS["hub"],
        render_hub_markdown(hub_registry, records),
    )
    write_text(
        HEMISPHERE_DOCS["metro1"],
        render_metro_level_markdown(metro_registry, 0),
    )
    write_text(
        HEMISPHERE_DOCS["metro2"],
        render_metro_level_markdown(metro_registry, 1),
    )
    write_text(
        HEMISPHERE_DOCS["metro3"],
        render_metro_level_markdown(metro_registry, 2),
    )
    write_text(
        HEMISPHERE_DOCS["metro4"],
        render_metro_level_markdown(metro_registry, 3),
    )
    write_text(
        HEMISPHERE_DOCS["receipt"],
        render_receipt(manifest, atlas_payload, docs_gate_status),
    )
    write_text(
        HEMISPHERE_DOCS["route_index"],
        render_route_index_markdown(route_manifest, route_coverage_registry),
    )
    write_text(
        HEMISPHERE_DOCS["route_math"],
        render_route_atlas_markdown("MATH", route_registry),
    )
    write_text(
        HEMISPHERE_DOCS["route_myth"],
        render_route_atlas_markdown("MYTH", route_registry),
    )
    write_text(
        HEMISPHERE_DOCS["route_crosswalk"],
        render_route_crosswalk_markdown(records),
    )
    write_text(
        HEMISPHERE_DOCS["route_coverage"],
        render_route_coverage_markdown(route_coverage_registry),
    )
    write_text(
        HEMISPHERE_DOCS["navigator_index"],
        render_navigator_index_markdown(navigator_manifest),
    )
    write_text(
        HEMISPHERE_DOCS["navigator_cookbook"],
        render_query_cookbook_markdown(),
    )
    write_text(
        HEMISPHERE_DOCS["navigator_math_hotspots"],
        render_navigator_hotspots_markdown("MATH", route_registry),
    )
    write_text(
        HEMISPHERE_DOCS["navigator_myth_hotspots"],
        render_navigator_hotspots_markdown("MYTH", route_registry),
    )
    write_text(
        HEMISPHERE_DOCS["navigator_entrypoints"],
        render_navigator_entrypoints_markdown(records),
    )
    write_text(
        HEMISPHERE_DOCS["composer_index"],
        render_route_composer_index_markdown(composer_manifest),
    )
    write_text(
        HEMISPHERE_DOCS["composer_cookbook"],
        render_route_composer_cookbook_markdown(),
    )
    write_text(
        HEMISPHERE_DOCS["composer_math"],
        render_route_composer_group_markdown(
            "MATH Route Starters",
            composer_seed_registry,
            "math",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["composer_myth"],
        render_route_composer_group_markdown(
            "MYTH Route Starters",
            composer_seed_registry,
            "myth",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["composer_commissure"],
        render_route_composer_group_markdown(
            "Commissure Route Starters",
            composer_seed_registry,
            "bridge",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["composer_facet"],
        render_route_composer_facet_markdown(composer_facet_registry),
    )
    write_text(
        HEMISPHERE_DOCS["synthesis_index"],
        render_synthesis_index_markdown(synthesis_manifest),
    )
    write_text(
        HEMISPHERE_DOCS["synthesis_cookbook"],
        render_synthesis_cookbook_markdown(),
    )
    write_text(
        HEMISPHERE_DOCS["synthesis_math"],
        render_synthesis_group_markdown(
            "MATH Starter Syntheses",
            synthesis_seed_registry,
            "math",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["synthesis_myth"],
        render_synthesis_group_markdown(
            "MYTH Starter Syntheses",
            synthesis_seed_registry,
            "myth",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["synthesis_commissure"],
        render_synthesis_group_markdown(
            "Commissure Starter Syntheses",
            synthesis_seed_registry,
            "bridge",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["synthesis_facet"],
        render_synthesis_facet_markdown(synthesis_facet_registry),
    )
    write_text(
        HEMISPHERE_DOCS["guided_tour_index"],
        render_guided_tour_index_markdown(guided_tour_manifest),
    )
    write_text(
        HEMISPHERE_DOCS["guided_tour_cookbook"],
        render_guided_tour_cookbook_markdown(),
    )
    write_text(
        HEMISPHERE_DOCS["guided_tour_main_pages"],
        render_guided_tour_group_markdown(
            "Main Atlas Page Starters",
            guided_tour_seed_registry,
            "main_pages",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["guided_tour_family"],
        render_guided_tour_group_markdown(
            "Family Guided Starters",
            guided_tour_seed_registry,
            "family",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["guided_tour_anchor"],
        render_guided_tour_group_markdown(
            "Anchor Guided Starters",
            guided_tour_seed_registry,
            "anchor",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["guided_tour_target_system"],
        render_guided_tour_group_markdown(
            "Target-System Guided Starters",
            guided_tour_seed_registry,
            "target_system",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["expedition_index"],
        render_expedition_index_markdown(expedition_manifest),
    )
    write_text(
        HEMISPHERE_DOCS["expedition_cookbook"],
        render_expedition_cookbook_markdown(),
    )
    write_text(
        HEMISPHERE_DOCS["expedition_main_pages"],
        render_expedition_group_markdown(
            "Main Atlas Expeditions",
            expedition_seed_registry,
            "main_pages",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["expedition_family"],
        render_expedition_group_markdown(
            "Family Expedition Starters",
            expedition_seed_registry,
            "family",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["expedition_anchor"],
        render_expedition_group_markdown(
            "Anchor Expedition Starters",
            expedition_seed_registry,
            "anchor",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["expedition_target_system"],
        render_expedition_group_markdown(
            "Target-System Expedition Starters",
            expedition_seed_registry,
            "target_system",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["constellation_index"],
        render_constellation_index_markdown(constellation_manifest),
    )
    write_text(
        HEMISPHERE_DOCS["constellation_cookbook"],
        render_constellation_cookbook_markdown(),
    )
    write_text(
        HEMISPHERE_DOCS["constellation_family"],
        render_constellation_group_markdown(
            "Family Constellations",
            constellation_page_registry,
            "family",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["constellation_anchor"],
        render_constellation_group_markdown(
            "Anchor Constellations",
            constellation_page_registry,
            "anchor",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["constellation_target_system"],
        render_constellation_group_markdown(
            "Target-System Constellations",
            constellation_page_registry,
            "target_system",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["constellation_coverage"],
        render_constellation_coverage_markdown(constellation_manifest),
    )
    write_text(
        HEMISPHERE_DOCS["replay_index"],
        render_replay_index_markdown(replay_manifest),
    )
    write_text(
        HEMISPHERE_DOCS["replay_cookbook"],
        render_replay_cookbook_markdown(),
    )
    write_text(
        HEMISPHERE_DOCS["replay_math"],
        render_replay_group_markdown(
            "MATH Replay Starters",
            replay_seed_registry,
            "math",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["replay_myth"],
        render_replay_group_markdown(
            "MYTH Replay Starters",
            replay_seed_registry,
            "myth",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["replay_bridge"],
        render_replay_group_markdown(
            "Bridge Replay Starters",
            replay_seed_registry,
            "bridge",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["replay_coverage"],
        render_replay_coverage_markdown(replay_manifest, replay_page_registry),
    )
    write_text(
        HEMISPHERE_DOCS["observatory_index"],
        render_observatory_index_markdown(observatory_manifest),
    )
    write_text(
        HEMISPHERE_DOCS["observatory_cookbook"],
        render_observatory_cookbook_markdown(),
    )
    write_text(
        HEMISPHERE_DOCS["observatory_main_pages"],
        render_observatory_group_markdown(
            "Main Page Briefings",
            observatory_seed_registry,
            "main_pages",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["observatory_family"],
        render_observatory_group_markdown(
            "Family Briefings",
            observatory_seed_registry,
            "family",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["observatory_anchor"],
        render_observatory_group_markdown(
            "Anchor Briefings",
            observatory_seed_registry,
            "anchor",
        ),
    )
    write_text(
        HEMISPHERE_DOCS["observatory_coverage"],
        render_observatory_coverage_markdown(
            observatory_manifest,
            observatory_page_registry,
        ),
    )
    for page in visual_atlas_page_registry.get("pages", []):
        relative_path = Path(page["relative_path"])
        write_text(
            HEMISPHERE_ROOT / relative_path,
            visual_atlas_markdown_pages.get(page["relative_path"], ""),
        )


def mirror_outputs(
    record_registry: dict[str, Any],
    commissure_registry: dict[str, Any],
    metro_registry: dict[str, Any],
    hub_registry: dict[str, Any],
    manifest: dict[str, Any],
    dual_route_registry: dict[str, Any],
    direct_edge_registry: dict[str, Any],
    route_coverage_registry: dict[str, Any],
    route_manifest: dict[str, Any],
    navigator_alias_index: dict[str, Any],
    navigator_facet_index: dict[str, Any],
    navigator_neighbor_index: dict[str, Any],
    navigator_manifest: dict[str, Any],
    composer_seed_registry: dict[str, Any],
    composer_facet_registry: dict[str, Any],
    composer_manifest: dict[str, Any],
    synthesis_evidence_registry: dict[str, Any],
    synthesis_seed_registry: dict[str, Any],
    synthesis_facet_registry: dict[str, Any],
    synthesis_manifest: dict[str, Any],
    visual_atlas_node_registry: dict[str, Any],
    visual_atlas_edge_registry: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    visual_atlas_record_locator_registry: dict[str, Any],
    visual_atlas_manifest: dict[str, Any],
    visual_atlas_markdown_pages: dict[str, str],
    guided_tour_seed_registry: dict[str, Any],
    guided_tour_page_registry: dict[str, Any],
    guided_tour_manifest: dict[str, Any],
    expedition_seed_registry: dict[str, Any],
    expedition_page_registry: dict[str, Any],
    expedition_manifest: dict[str, Any],
    constellation_node_registry: dict[str, Any],
    constellation_edge_registry: dict[str, Any],
    constellation_page_registry: dict[str, Any],
    constellation_manifest: dict[str, Any],
    replay_seed_registry: dict[str, Any],
    replay_page_registry: dict[str, Any],
    replay_manifest: dict[str, Any],
    observatory_seed_registry: dict[str, Any],
    observatory_page_registry: dict[str, Any],
    observatory_manifest: dict[str, Any],
) -> None:
    FLEET_MIRROR_ROOT.mkdir(parents=True, exist_ok=True)
    for source_name, source_path in HEMISPHERE_DOCS.items():
        target_name = "README.md" if source_name == "index" else source_path.name
        write_text(
            FLEET_MIRROR_ROOT / target_name,
            source_path.read_text(encoding="utf-8"),
        )
    write_json(FLEET_MIRROR_ROOT / RECORD_REGISTRY_PATH.name, record_registry)
    write_json(FLEET_MIRROR_ROOT / COMMISSURE_REGISTRY_PATH.name, commissure_registry)
    write_json(FLEET_MIRROR_ROOT / METRO_REGISTRY_PATH.name, metro_registry)
    write_json(FLEET_MIRROR_ROOT / HUB_REGISTRY_PATH.name, hub_registry)
    write_json(FLEET_MIRROR_ROOT / MANIFEST_PATH.name, manifest)
    write_json(FLEET_MIRROR_ROOT / DUAL_ROUTE_REGISTRY_PATH.name, dual_route_registry)
    write_json(FLEET_MIRROR_ROOT / DIRECT_EDGE_REGISTRY_PATH.name, direct_edge_registry)
    write_json(
        FLEET_MIRROR_ROOT / ROUTE_COVERAGE_REGISTRY_PATH.name,
        route_coverage_registry,
    )
    write_json(FLEET_MIRROR_ROOT / ROUTE_MANIFEST_PATH.name, route_manifest)
    write_json(
        FLEET_MIRROR_ROOT / NAVIGATOR_ALIAS_INDEX_PATH.name,
        navigator_alias_index,
    )
    write_json(
        FLEET_MIRROR_ROOT / NAVIGATOR_FACET_INDEX_PATH.name,
        navigator_facet_index,
    )
    write_json(
        FLEET_MIRROR_ROOT / NAVIGATOR_NEIGHBOR_INDEX_PATH.name,
        navigator_neighbor_index,
    )
    write_json(FLEET_MIRROR_ROOT / NAVIGATOR_MANIFEST_PATH.name, navigator_manifest)
    write_json(FLEET_MIRROR_ROOT / COMPOSER_SEED_REGISTRY_PATH.name, composer_seed_registry)
    write_json(FLEET_MIRROR_ROOT / COMPOSER_FACET_REGISTRY_PATH.name, composer_facet_registry)
    write_json(FLEET_MIRROR_ROOT / COMPOSER_MANIFEST_PATH.name, composer_manifest)
    write_json(FLEET_MIRROR_ROOT / SYNTHESIS_EVIDENCE_REGISTRY_PATH.name, synthesis_evidence_registry)
    write_json(FLEET_MIRROR_ROOT / SYNTHESIS_SEED_REGISTRY_PATH.name, synthesis_seed_registry)
    write_json(FLEET_MIRROR_ROOT / SYNTHESIS_FACET_REGISTRY_PATH.name, synthesis_facet_registry)
    write_json(FLEET_MIRROR_ROOT / SYNTHESIS_MANIFEST_PATH.name, synthesis_manifest)
    write_json(FLEET_MIRROR_ROOT / VISUAL_ATLAS_NODE_REGISTRY_PATH.name, visual_atlas_node_registry)
    write_json(FLEET_MIRROR_ROOT / VISUAL_ATLAS_EDGE_REGISTRY_PATH.name, visual_atlas_edge_registry)
    write_json(FLEET_MIRROR_ROOT / VISUAL_ATLAS_PAGE_REGISTRY_PATH.name, visual_atlas_page_registry)
    write_json(
        FLEET_MIRROR_ROOT / VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH.name,
        visual_atlas_record_locator_registry,
    )
    write_json(FLEET_MIRROR_ROOT / VISUAL_ATLAS_MANIFEST_PATH.name, visual_atlas_manifest)
    write_json(FLEET_MIRROR_ROOT / GUIDED_TOUR_SEED_REGISTRY_PATH.name, guided_tour_seed_registry)
    write_json(FLEET_MIRROR_ROOT / GUIDED_TOUR_PAGE_REGISTRY_PATH.name, guided_tour_page_registry)
    write_json(FLEET_MIRROR_ROOT / GUIDED_TOUR_MANIFEST_PATH.name, guided_tour_manifest)
    write_json(FLEET_MIRROR_ROOT / EXPEDITION_SEED_REGISTRY_PATH.name, expedition_seed_registry)
    write_json(FLEET_MIRROR_ROOT / EXPEDITION_PAGE_REGISTRY_PATH.name, expedition_page_registry)
    write_json(FLEET_MIRROR_ROOT / EXPEDITION_MANIFEST_PATH.name, expedition_manifest)
    write_json(FLEET_MIRROR_ROOT / CONSTELLATION_NODE_REGISTRY_PATH.name, constellation_node_registry)
    write_json(FLEET_MIRROR_ROOT / CONSTELLATION_EDGE_REGISTRY_PATH.name, constellation_edge_registry)
    write_json(FLEET_MIRROR_ROOT / CONSTELLATION_PAGE_REGISTRY_PATH.name, constellation_page_registry)
    write_json(FLEET_MIRROR_ROOT / CONSTELLATION_MANIFEST_PATH.name, constellation_manifest)
    write_json(FLEET_MIRROR_ROOT / REPLAY_SEED_REGISTRY_PATH.name, replay_seed_registry)
    write_json(FLEET_MIRROR_ROOT / REPLAY_PAGE_REGISTRY_PATH.name, replay_page_registry)
    write_json(FLEET_MIRROR_ROOT / REPLAY_MANIFEST_PATH.name, replay_manifest)
    write_json(FLEET_MIRROR_ROOT / OBSERVATORY_SEED_REGISTRY_PATH.name, observatory_seed_registry)
    write_json(FLEET_MIRROR_ROOT / OBSERVATORY_PAGE_REGISTRY_PATH.name, observatory_page_registry)
    write_json(FLEET_MIRROR_ROOT / OBSERVATORY_MANIFEST_PATH.name, observatory_manifest)
    for relative_path, text in visual_atlas_markdown_pages.items():
        write_text(FLEET_MIRROR_ROOT / Path(relative_path), text)


def derive() -> dict[str, Any]:
    cleanup_old_generation()
    docs_gate_status = load_docs_gate_status()
    aqm_lane = load_aqm_lane()
    tesseract_bundle = load_math_tesseract_bundle()
    atlas_payload = load_math_tesseract_source_atlas()
    if not atlas_payload.get("records"):
        atlas_payload = refresh_full_corpus_atlas()
    write_json(HEMISPHERE_ATLAS_PATH, atlas_payload)
    anchors = parse_canonical_sources()
    station_map = load_station_map()
    semantic_mass_weights = load_semantic_mass_weights()
    route_quality_factor = load_route_quality_factor()
    canonical_records = deduplicate_records(atlas_payload.get("records", []))
    projected_records = [
        project_record(
            record=record,
            docs_gate_status=docs_gate_status,
            aqm_lane=aqm_lane,
            anchors=anchors,
            station_map=station_map,
            semantic_mass_weights=semantic_mass_weights,
            route_quality_factor=route_quality_factor,
            tesseract_bundle=tesseract_bundle,
        )
        for record in canonical_records
    ]
    projected_records.sort(key=lambda item: item["relative_path"].lower())
    (
        projected_records,
        dual_route_registry,
        direct_edge_registry,
        route_coverage_registry,
        route_manifest,
    ) = build_dual_route_payloads(
        records=projected_records,
        station_map=station_map,
        docs_gate_status=docs_gate_status,
    )
    (
        navigator_alias_index,
        navigator_facet_index,
        navigator_neighbor_index,
        navigator_manifest,
    ) = build_navigator_payloads(
        records=projected_records,
        dual_route_registry=dual_route_registry,
        direct_edge_registry=direct_edge_registry,
        docs_gate_status=docs_gate_status,
    )

    record_registry = {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate_status": docs_gate_status,
        "atlas_path": str(HEMISPHERE_ATLAS_PATH),
        "atlas_timestamp": file_timestamp(HEMISPHERE_ATLAS_PATH),
        "atlas_record_count": atlas_payload.get("record_count", 0),
        "deduplicated_record_count": len(projected_records),
        "required_fields": REQUIRED_FIELDS,
        "records": projected_records,
    }
    hub_registry = build_hub_registry(projected_records, docs_gate_status)
    commissure_registry = build_commissure_registry(projected_records, docs_gate_status)
    metro_registry = build_metro_registry(projected_records, docs_gate_status)
    manifest = build_manifest(
        atlas_payload=atlas_payload,
        records=projected_records,
        docs_gate_status=docs_gate_status,
        aqm_lane=aqm_lane,
        anchors=anchors,
    )
    (
        composer_seed_registry,
        composer_facet_registry,
        composer_manifest,
    ) = build_route_composer_payloads(
        record_registry=record_registry,
        commissure_registry=commissure_registry,
        dual_route_registry=dual_route_registry,
        direct_edge_registry=direct_edge_registry,
        manifest=manifest,
        navigator_alias_index=navigator_alias_index,
        navigator_facet_index=navigator_facet_index,
        navigator_neighbor_index=navigator_neighbor_index,
        navigator_manifest=navigator_manifest,
        docs_gate_status=docs_gate_status,
    )
    synthesis_build_registries = {
        "record_registry": record_registry,
        "route_registry": dual_route_registry,
        "edge_registry": direct_edge_registry,
        "manifest": manifest,
        "commissure_registry": commissure_registry,
        "navigator_alias_index": navigator_alias_index,
        "navigator_facet_index": navigator_facet_index,
        "navigator_neighbor_index": navigator_neighbor_index,
        "navigator_manifest": navigator_manifest,
        "composer_seed_registry": composer_seed_registry,
        "composer_facet_registry": composer_facet_registry,
        "composer_manifest": composer_manifest,
    }
    (
        synthesis_evidence_registry,
        synthesis_seed_registry,
        synthesis_facet_registry,
        synthesis_manifest,
    ) = build_synthesis_payloads(
        record_registry=record_registry,
        atlas_records=canonical_records,
        composer_seed_registry=composer_seed_registry,
        composer_facet_registry=composer_facet_registry,
        registries=synthesis_build_registries,
        docs_gate_status=docs_gate_status,
    )
    (
        visual_atlas_node_registry,
        visual_atlas_edge_registry,
        visual_atlas_page_registry,
        visual_atlas_record_locator_registry,
        visual_atlas_manifest,
        visual_atlas_markdown_pages,
    ) = build_visual_atlas_payloads(
        record_registry=record_registry,
        dual_route_registry=dual_route_registry,
        direct_edge_registry=direct_edge_registry,
        manifest=manifest,
        navigator_facet_index=navigator_facet_index,
        composer_seed_registry=composer_seed_registry,
        synthesis_seed_registry=synthesis_seed_registry,
        docs_gate_status=docs_gate_status,
    )
    guided_tour_build_registries = {
        "record_registry": record_registry,
        "route_registry": dual_route_registry,
        "edge_registry": direct_edge_registry,
        "manifest": manifest,
        "commissure_registry": commissure_registry,
        "navigator_alias_index": navigator_alias_index,
        "navigator_facet_index": navigator_facet_index,
        "navigator_neighbor_index": navigator_neighbor_index,
        "navigator_manifest": navigator_manifest,
        "composer_seed_registry": composer_seed_registry,
        "composer_facet_registry": composer_facet_registry,
        "composer_manifest": composer_manifest,
        "synthesis_evidence_registry": synthesis_evidence_registry,
        "synthesis_seed_registry": synthesis_seed_registry,
        "synthesis_facet_registry": synthesis_facet_registry,
        "synthesis_manifest": synthesis_manifest,
        "visual_atlas_node_registry": visual_atlas_node_registry,
        "visual_atlas_edge_registry": visual_atlas_edge_registry,
        "visual_atlas_page_registry": visual_atlas_page_registry,
        "visual_atlas_record_locator_registry": visual_atlas_record_locator_registry,
        "visual_atlas_manifest": visual_atlas_manifest,
    }
    (
        guided_tour_seed_registry,
        guided_tour_page_registry,
        guided_tour_manifest,
    ) = build_guided_tour_payloads(
        registries=guided_tour_build_registries,
        visual_atlas_page_registry=visual_atlas_page_registry,
        docs_gate_status=docs_gate_status,
    )
    expedition_build_registries = {
        **guided_tour_build_registries,
        "guided_tour_seed_registry": guided_tour_seed_registry,
        "guided_tour_page_registry": guided_tour_page_registry,
        "guided_tour_manifest": guided_tour_manifest,
    }
    (
        expedition_seed_registry,
        expedition_page_registry,
        expedition_manifest,
    ) = build_expedition_payloads(
        registries=expedition_build_registries,
        visual_atlas_page_registry=visual_atlas_page_registry,
        docs_gate_status=docs_gate_status,
    )
    constellation_build_registries = {
        **expedition_build_registries,
        "expedition_seed_registry": expedition_seed_registry,
        "expedition_page_registry": expedition_page_registry,
        "expedition_manifest": expedition_manifest,
    }
    (
        constellation_node_registry,
        constellation_edge_registry,
        constellation_page_registry,
        constellation_manifest,
    ) = build_constellation_payloads(
        registries=constellation_build_registries,
        visual_atlas_page_registry=visual_atlas_page_registry,
        docs_gate_status=docs_gate_status,
    )
    replay_build_registries = {
        **constellation_build_registries,
        "constellation_node_registry": constellation_node_registry,
        "constellation_edge_registry": constellation_edge_registry,
        "constellation_page_registry": constellation_page_registry,
        "constellation_manifest": constellation_manifest,
    }
    (
        replay_seed_registry,
        replay_page_registry,
        replay_manifest,
    ) = build_replay_payloads(
        registries=replay_build_registries,
        synthesis_seed_registry=synthesis_seed_registry,
        visual_atlas_page_registry=visual_atlas_page_registry,
        docs_gate_status=docs_gate_status,
    )
    observatory_build_registries = {
        **replay_build_registries,
        "replay_seed_registry": replay_seed_registry,
        "replay_page_registry": replay_page_registry,
        "replay_manifest": replay_manifest,
    }
    (
        observatory_seed_registry,
        observatory_page_registry,
        observatory_manifest,
    ) = build_observatory_payloads(
        registries=observatory_build_registries,
        visual_atlas_page_registry=visual_atlas_page_registry,
        docs_gate_status=docs_gate_status,
    )
    full_corpus_payloads = build_full_corpus_integration_payloads(
        control_manifest=manifest,
        control_records=projected_records,
        docs_gate_status=docs_gate_status,
        aqm_lane=aqm_lane,
        anchors=anchors,
        station_map=station_map,
    )
    full_corpus_authority_registry = full_corpus_payloads["authority_registry"]
    full_corpus_basis_crosswalk_registry = full_corpus_payloads["basis_crosswalk_registry"]
    full_corpus_route_coverage_registry = full_corpus_payloads["route_coverage_registry"]
    full_corpus_awakening_stage_registry = full_corpus_payloads["awakening_stage_registry"]
    full_corpus_awakening_agent_transition_registry = full_corpus_payloads[
        "awakening_agent_transition_registry"
    ]
    full_corpus_appendix_governance_ledger = full_corpus_payloads[
        "appendix_governance_ledger"
    ]
    full_corpus_integration_manifest = full_corpus_payloads["integration_manifest"]
    full_corpus_markdown_pages = full_corpus_payloads["markdown_pages"]
    deeper_integration_receipt = full_corpus_payloads["deeper_receipt"]
    ap6d_57_loop_payloads = build_ap6d_57_loop_payloads(
        control_manifest=manifest,
        full_corpus_authority_registry=full_corpus_authority_registry,
        full_corpus_basis_crosswalk_registry=full_corpus_basis_crosswalk_registry,
        full_corpus_route_coverage_registry=full_corpus_route_coverage_registry,
        full_corpus_awakening_stage_registry=full_corpus_awakening_stage_registry,
        full_corpus_awakening_agent_transition_registry=full_corpus_awakening_agent_transition_registry,
        full_corpus_appendix_governance_ledger=full_corpus_appendix_governance_ledger,
        docs_gate_status=docs_gate_status,
    )
    ap6d_57_loop_control_registry = ap6d_57_loop_payloads["control_registry"]
    ap6d_57_agent_lane_registry = ap6d_57_loop_payloads["agent_lane_registry"]
    ap6d_57_nested_seat_manifest = ap6d_57_loop_payloads["nested_seat_manifest"]
    ap6d_57_quest_bundle_registry = ap6d_57_loop_payloads["quest_bundle_registry"]
    ap6d_57_worker_action_registry = ap6d_57_loop_payloads["worker_action_registry"]
    ap6d_57_pruning_registry = ap6d_57_loop_payloads["pruning_registry"]
    ap6d_57_awakening_transition_registry = ap6d_57_loop_payloads["awakening_transition_registry"]
    ap6d_57_restart_seed_registry = ap6d_57_loop_payloads["restart_seed_registry"]
    ap6d_57_loop_manifest = ap6d_57_loop_payloads["manifest"]
    ap6d_57_markdown_pages = ap6d_57_loop_payloads["markdown_pages"]
    ap6d_57_guild_hall_doc = ap6d_57_loop_payloads["guild_hall_doc"]
    ap6d_57_temple_doc = ap6d_57_loop_payloads["temple_doc"]
    ap6d_57_deep_control_doc = ap6d_57_loop_payloads["deep_control_doc"]
    ap6d_57_receipt_doc = ap6d_57_loop_payloads["receipt_doc"]
    ap6d_57_guild_hall_board_text = ap6d_57_loop_payloads["guild_hall_board_text"]
    ap6d_57_temple_board_text = ap6d_57_loop_payloads["temple_board_text"]
    lp57omega_payloads = build_lp57omega_payloads(
        control_manifest=manifest,
        full_corpus_authority_registry=full_corpus_authority_registry,
        full_corpus_basis_crosswalk_registry=full_corpus_basis_crosswalk_registry,
        full_corpus_route_coverage_registry=full_corpus_route_coverage_registry,
        full_corpus_awakening_stage_registry=full_corpus_awakening_stage_registry,
        full_corpus_awakening_agent_transition_registry=full_corpus_awakening_agent_transition_registry,
        full_corpus_appendix_governance_ledger=full_corpus_appendix_governance_ledger,
        ap6d_57_loop_control_registry=ap6d_57_loop_control_registry,
        ap6d_57_agent_lane_registry=ap6d_57_agent_lane_registry,
        ap6d_57_nested_seat_manifest=ap6d_57_nested_seat_manifest,
        docs_gate_status=docs_gate_status,
        current_guild_hall_board_text=ap6d_57_guild_hall_board_text,
        current_temple_board_text=ap6d_57_temple_board_text,
    )
    master_loop_state = lp57omega_payloads["master_loop_state"]
    master_agent_state = lp57omega_payloads["master_agent_state"]
    master_loop_shared_lattice = lp57omega_payloads["master_loop_shared_lattice"]
    lp57omega_loop_registry = lp57omega_payloads["loop_registry"]
    lp57omega_agent_identity_registry = lp57omega_payloads["agent_identity_registry"]
    lp57omega_coordinate_registry = lp57omega_payloads["coordinate_registry"]
    lp57omega_quest_contract_registry = lp57omega_payloads["quest_contract_registry"]
    lp57omega_master_ledger_registry = lp57omega_payloads["master_ledger_registry"]
    lp57omega_manifest = lp57omega_payloads["manifest"]
    lp57omega_markdown_pages = lp57omega_payloads["markdown_pages"]
    lp57omega_guild_hall_doc = lp57omega_payloads["guild_hall_doc"]
    lp57omega_temple_doc = lp57omega_payloads["temple_doc"]
    lp57omega_deep_control_doc = lp57omega_payloads["deep_control_doc"]
    lp57omega_receipt_doc = lp57omega_payloads["receipt_doc"]
    lp57omega_guild_hall_board_text = lp57omega_payloads["guild_hall_board_text"]
    lp57omega_temple_board_text = lp57omega_payloads["temple_board_text"]
    dense_65_payloads = build_dense_65_payloads(
        full_corpus_authority_registry=full_corpus_authority_registry,
        lp57omega_coordinate_registry=lp57omega_coordinate_registry,
        docs_gate_status=docs_gate_status,
    )
    dense_65_shell_registry = dense_65_payloads["shell_registry"]
    dense_65_rqt_witness_registry = dense_65_payloads["witness_registry"]
    dense_65_rqt_overflow_registry = dense_65_payloads["overflow_registry"]
    dense_65_manifest = dense_65_payloads["manifest"]
    dense_65_markdown_pages = dense_65_payloads["markdown_pages"]
    command_membrane_payloads = build_command_membrane_payloads(
        full_corpus_authority_registry=full_corpus_authority_registry,
        dual_route_registry=dual_route_registry,
        lp57omega_coordinate_registry=lp57omega_coordinate_registry,
        docs_gate_status=docs_gate_status,
    )
    command_membrane_packet_schema = command_membrane_payloads["packet_schema"]
    command_membrane_watched_surface_registry = command_membrane_payloads["watched_surface_registry"]
    command_membrane_event_registry = command_membrane_payloads["event_registry"]
    command_membrane_claim_ledger = command_membrane_payloads["claim_ledger"]
    command_membrane_capillary_registry = command_membrane_payloads["capillary_registry"]
    command_membrane_latency_registry = command_membrane_payloads["latency_registry"]
    command_membrane_manifest = command_membrane_payloads["manifest"]
    command_membrane_markdown_pages = command_membrane_payloads["markdown_pages"]
    manifest["counts"].update(
        {
            "route_packets": dual_route_registry["route_count"],
            "direct_edges": direct_edge_registry["edge_count"],
            "coverage_rows": route_coverage_registry["record_count"],
            "navigator_alias_keys": navigator_alias_index["alias_key_count"],
            "navigator_alias_entries": navigator_alias_index["alias_entry_count"],
            "composer_seed_starters": sum(composer_seed_registry.get("counts", {}).values()),
            "composer_facet_starters": sum(composer_facet_registry.get("facet_counts", {}).values()),
            "synthesis_evidence_records": synthesis_evidence_registry["record_count"],
            "synthesis_seed_starters": sum(synthesis_seed_registry.get("counts", {}).values()),
            "synthesis_facet_starters": sum(synthesis_facet_registry.get("facet_counts", {}).values()),
            "visual_atlas_nodes": visual_atlas_node_registry["node_count"],
            "visual_atlas_edges": visual_atlas_edge_registry["edge_count"],
            "visual_atlas_pages": visual_atlas_page_registry["page_count"],
            "visual_atlas_locator_rows": visual_atlas_record_locator_registry["record_count"],
            "guided_tour_seed_starters": sum(guided_tour_seed_registry.get("counts", {}).values()),
            "guided_tour_page_starters": guided_tour_page_registry.get("page_count", 0),
            "expedition_seed_starters": sum(expedition_seed_registry.get("counts", {}).values()),
            "expedition_page_starters": expedition_page_registry.get("page_count", 0),
            "constellation_nodes": constellation_node_registry.get("node_count", 0),
            "constellation_edges": constellation_edge_registry.get("edge_count", 0),
            "constellation_pages": constellation_page_registry.get("page_count", 0),
            "replay_seed_starters": sum(replay_seed_registry.get("counts", {}).values()),
            "replay_page_starters": replay_page_registry.get("page_count", 0),
            "observatory_seed_starters": sum(observatory_seed_registry.get("counts", {}).values()),
            "observatory_page_starters": observatory_page_registry.get("page_count", 0),
            "full_corpus_records": full_corpus_authority_registry.get("record_count", 0),
            "full_corpus_live_only": full_corpus_authority_registry.get("scope_distribution", {}).get("live", 0),
            "full_corpus_archive_only": full_corpus_authority_registry.get("scope_distribution", {}).get("archive", 0),
            "full_corpus_both_scope": full_corpus_authority_registry.get("scope_distribution", {}).get("both", 0),
            "full_corpus_witness_only": full_corpus_authority_registry.get("scope_distribution", {}).get("witness_only", 0),
            "awakening_assigned_records": full_corpus_awakening_stage_registry.get("assigned_count", 0),
            "awakening_stage_abstentions": full_corpus_awakening_stage_registry.get("abstention_count", 0),
            "awakening_family_notes": full_corpus_awakening_agent_transition_registry.get("family_note_count", 0),
            "awakening_basis_notes": full_corpus_awakening_agent_transition_registry.get("basis_role_note_count", 0),
            "ap6d_57_loops": ap6d_57_loop_control_registry.get("loop_count", 0),
            "ap6d_57_master_agents": ap6d_57_agent_lane_registry.get("master_agent_count", 0),
            "ap6d_57_nested_seat_manifests": ap6d_57_nested_seat_manifest.get("row_count", 0),
            "ap6d_57_quest_bundle_rows": ap6d_57_quest_bundle_registry.get("row_count", 0),
            "ap6d_57_worker_action_rows": ap6d_57_worker_action_registry.get("row_count", 0),
            "ap6d_57_pruning_rows": ap6d_57_pruning_registry.get("row_count", 0),
            "ap6d_57_restart_seed_rows": ap6d_57_restart_seed_registry.get("row_count", 0),
            "lp57omega_loops": lp57omega_loop_registry.get("loop_count", 0),
            "lp57omega_agent_identity_rows": lp57omega_agent_identity_registry.get("row_count", 0),
            "lp57omega_coordinate_rows": lp57omega_coordinate_registry.get("record_count", 0),
            "lp57omega_quest_contract_rows": lp57omega_quest_contract_registry.get("row_count", 0),
            "lp57omega_master_ledger_rows": lp57omega_master_ledger_registry.get("row_count", 0),
            "dense_65_shell_rows": dense_65_shell_registry.get("row_count", 0),
            "dense_65_primary_witness_rows": dense_65_rqt_witness_registry.get("row_count", 0),
            "dense_65_overflow_rows": dense_65_rqt_overflow_registry.get("overflow_count", 0),
            "dense_65_abstention_rows": dense_65_rqt_overflow_registry.get("abstention_count", 0),
            "command_membrane_watched_surfaces": command_membrane_watched_surface_registry.get("source_count", 0),
            "command_membrane_events": command_membrane_event_registry.get("event_count", 0),
            "command_membrane_matched_events": command_membrane_event_registry.get("matched_event_count", 0),
            "command_membrane_claim_rows": command_membrane_claim_ledger.get("row_count", 0),
            "command_membrane_capillary_edges": command_membrane_capillary_registry.get("edge_count", 0),
            "command_membrane_latency_rows": command_membrane_latency_registry.get("row_count", 0),
        }
    )
    manifest["outputs"].update(
        {
            "math_tesseract_bundle_source": str(MATH_TESSERACT_BUNDLE_PATH),
            "math_tesseract_atlas_source": str(MATH_TESSERACT_ATLAS_MD_PATH),
            "dual_route_registry": str(DUAL_ROUTE_REGISTRY_PATH),
            "direct_edge_registry": str(DIRECT_EDGE_REGISTRY_PATH),
            "route_coverage_registry": str(ROUTE_COVERAGE_REGISTRY_PATH),
            "route_manifest": str(ROUTE_MANIFEST_PATH),
            "navigator_alias_index": str(NAVIGATOR_ALIAS_INDEX_PATH),
            "navigator_facet_index": str(NAVIGATOR_FACET_INDEX_PATH),
            "navigator_neighbor_index": str(NAVIGATOR_NEIGHBOR_INDEX_PATH),
            "navigator_manifest": str(NAVIGATOR_MANIFEST_PATH),
            "composer_seed_registry": str(COMPOSER_SEED_REGISTRY_PATH),
            "composer_facet_registry": str(COMPOSER_FACET_REGISTRY_PATH),
            "composer_manifest": str(COMPOSER_MANIFEST_PATH),
            "synthesis_evidence_registry": str(SYNTHESIS_EVIDENCE_REGISTRY_PATH),
            "synthesis_seed_registry": str(SYNTHESIS_SEED_REGISTRY_PATH),
            "synthesis_facet_registry": str(SYNTHESIS_FACET_REGISTRY_PATH),
            "synthesis_manifest": str(SYNTHESIS_MANIFEST_PATH),
            "visual_atlas_node_registry": str(VISUAL_ATLAS_NODE_REGISTRY_PATH),
            "visual_atlas_edge_registry": str(VISUAL_ATLAS_EDGE_REGISTRY_PATH),
            "visual_atlas_page_registry": str(VISUAL_ATLAS_PAGE_REGISTRY_PATH),
            "visual_atlas_record_locator_registry": str(VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH),
            "visual_atlas_manifest": str(VISUAL_ATLAS_MANIFEST_PATH),
            "guided_tour_seed_registry": str(GUIDED_TOUR_SEED_REGISTRY_PATH),
            "guided_tour_page_registry": str(GUIDED_TOUR_PAGE_REGISTRY_PATH),
            "guided_tour_manifest": str(GUIDED_TOUR_MANIFEST_PATH),
            "expedition_seed_registry": str(EXPEDITION_SEED_REGISTRY_PATH),
            "expedition_page_registry": str(EXPEDITION_PAGE_REGISTRY_PATH),
            "expedition_manifest": str(EXPEDITION_MANIFEST_PATH),
            "constellation_node_registry": str(CONSTELLATION_NODE_REGISTRY_PATH),
            "constellation_edge_registry": str(CONSTELLATION_EDGE_REGISTRY_PATH),
            "constellation_page_registry": str(CONSTELLATION_PAGE_REGISTRY_PATH),
            "constellation_manifest": str(CONSTELLATION_MANIFEST_PATH),
            "replay_seed_registry": str(REPLAY_SEED_REGISTRY_PATH),
            "replay_page_registry": str(REPLAY_PAGE_REGISTRY_PATH),
            "replay_manifest": str(REPLAY_MANIFEST_PATH),
            "observatory_seed_registry": str(OBSERVATORY_SEED_REGISTRY_PATH),
            "observatory_page_registry": str(OBSERVATORY_PAGE_REGISTRY_PATH),
            "observatory_manifest": str(OBSERVATORY_MANIFEST_PATH),
            "full_corpus_authority_registry": str(FULL_CORPUS_AUTHORITY_REGISTRY_PATH),
            "full_corpus_basis_crosswalk_registry": str(FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH),
            "full_corpus_route_coverage_registry": str(FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH),
            "full_corpus_awakening_stage_registry": str(FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH),
            "full_corpus_awakening_agent_transition_registry": str(FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH),
            "full_corpus_appendix_governance_ledger": str(FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH),
            "full_corpus_integration_manifest": str(FULL_CORPUS_INTEGRATION_MANIFEST_PATH),
            "full_corpus_deeper_receipt": str(DEEPER_INTEGRATION_RECEIPT_PATH),
            "ap6d_57_loop_control_registry": str(AP6D_57_LOOP_CONTROL_REGISTRY_PATH),
            "ap6d_57_agent_lane_registry": str(AP6D_57_AGENT_LANE_REGISTRY_PATH),
            "ap6d_57_nested_seat_manifest": str(AP6D_57_NESTED_SEAT_MANIFEST_PATH),
            "ap6d_57_quest_bundle_registry": str(AP6D_57_QUEST_BUNDLE_REGISTRY_PATH),
            "ap6d_57_worker_action_registry": str(AP6D_57_WORKER_ACTION_REGISTRY_PATH),
            "ap6d_57_pruning_registry": str(AP6D_57_PRUNING_REGISTRY_PATH),
            "ap6d_57_awakening_transition_registry": str(AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH),
            "ap6d_57_restart_seed_registry": str(AP6D_57_RESTART_SEED_REGISTRY_PATH),
            "ap6d_57_loop_manifest": str(AP6D_57_LOOP_MANIFEST_PATH),
            "ap6d_57_guild_hall_doc": str(AP6D_57_GUILD_HALL_DOC_PATH),
            "ap6d_57_temple_doc": str(AP6D_57_TEMPLE_DOC_PATH),
            "ap6d_57_deep_control_doc": str(AP6D_57_DEEP_CONTROL_DOC_PATH),
            "ap6d_57_receipt_doc": str(AP6D_57_RECEIPT_PATH),
            "master_loop_state": str(MASTER_LOOP_STATE_PATH),
            "master_agent_state": str(MASTER_AGENT_STATE_PATH),
            "master_loop_shared_lattice": str(MASTER_LOOP_SHARED_LATTICE_PATH),
            "lp57omega_loop_registry": str(LP57OMEGA_LOOP_REGISTRY_PATH),
            "lp57omega_agent_identity_registry": str(LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH),
            "lp57omega_coordinate_registry": str(LP57OMEGA_COORDINATE_REGISTRY_PATH),
            "lp57omega_quest_contract_registry": str(LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH),
            "lp57omega_master_ledger_registry": str(LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH),
            "lp57omega_manifest": str(LP57OMEGA_MANIFEST_PATH),
            "lp57omega_guild_hall_doc": str(LP57OMEGA_GUILD_HALL_DOC_PATH),
            "lp57omega_temple_doc": str(LP57OMEGA_TEMPLE_DOC_PATH),
            "lp57omega_deep_control_doc": str(LP57OMEGA_DEEP_CONTROL_DOC_PATH),
            "lp57omega_receipt_doc": str(LP57OMEGA_RECEIPT_PATH),
            "dense_65_shell_registry": str(DENSE_65_SHELL_REGISTRY_PATH),
            "dense_65_rqt_witness_registry": str(DENSE_65_RQT_WITNESS_REGISTRY_PATH),
            "dense_65_rqt_overflow_registry": str(DENSE_65_RQT_OVERFLOW_REGISTRY_PATH),
            "dense_65_manifest": str(DENSE_65_MANIFEST_PATH),
            "command_membrane_packet_schema": str(COMMAND_MEMBRANE_PACKET_SCHEMA_PATH),
            "command_membrane_watched_surface_registry": str(COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH),
            "command_membrane_event_registry": str(COMMAND_MEMBRANE_EVENT_REGISTRY_PATH),
            "command_membrane_claim_ledger": str(COMMAND_MEMBRANE_CLAIM_LEDGER_PATH),
            "command_membrane_capillary_registry": str(COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH),
            "command_membrane_latency_registry": str(COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH),
            "command_membrane_manifest": str(COMMAND_MEMBRANE_MANIFEST_PATH),
        }
    )
    route_manifest["required_route_keys"] = [
        "route_id",
        "hemisphere",
        "route_role",
        "route_mode",
        "hub_id",
        "grand_central_exchange",
        "chapter_station",
        "local_addr",
        "global_addr",
        "tesseract_header",
        "truth_state",
        "root_station_address",
        "origin_system",
        "target_system",
        "station_path",
        "interlock_ids",
        "return_path",
        "family",
        "basis_anchor_ids",
        "tract",
        "metro_line_ids",
        "appendix_support",
        "appendix_support_sources",
        "rail3",
        "primary_carrier",
        "transform_chain",
        "dominant_lens_system",
        "secondary_lens_system",
        "lens_weight_vector",
        "liminal_vector",
        "field_id",
        "zpoint_id",
        "aether_point",
        "geodesic_mode",
        "preferred_space",
        "supported_spaces",
        "pt2_shortcut_id",
        "knowledge_fabric_shortcut_id",
        "hubs_seq",
        "tunnel_plan",
        "hcrl_pass",
        "obligations",
        "drop_log",
        "overlay_annotations",
        "truth_intent",
        "route_plan_id",
        "graph_edge_ids",
        "primary_hubs_text",
        "tunnel_text",
        "truth_state_text",
        "hcrl_text",
        "addr4",
        "face6",
        "arc7",
        "depth5",
        "dynamic_weights",
        "replay_policy",
        "proof_state",
        "docs_gate_status",
    ]

    write_json(RECORD_REGISTRY_PATH, record_registry)
    write_json(COMMISSURE_REGISTRY_PATH, commissure_registry)
    write_json(METRO_REGISTRY_PATH, metro_registry)
    write_json(HUB_REGISTRY_PATH, hub_registry)
    write_json(MANIFEST_PATH, manifest)
    write_json(DUAL_ROUTE_REGISTRY_PATH, dual_route_registry)
    write_json(DIRECT_EDGE_REGISTRY_PATH, direct_edge_registry)
    write_json(ROUTE_COVERAGE_REGISTRY_PATH, route_coverage_registry)
    write_json(ROUTE_MANIFEST_PATH, route_manifest)
    write_json(NAVIGATOR_ALIAS_INDEX_PATH, navigator_alias_index)
    write_json(NAVIGATOR_FACET_INDEX_PATH, navigator_facet_index)
    write_json(NAVIGATOR_NEIGHBOR_INDEX_PATH, navigator_neighbor_index)
    write_json(NAVIGATOR_MANIFEST_PATH, navigator_manifest)
    write_json(COMPOSER_SEED_REGISTRY_PATH, composer_seed_registry)
    write_json(COMPOSER_FACET_REGISTRY_PATH, composer_facet_registry)
    write_json(COMPOSER_MANIFEST_PATH, composer_manifest)
    write_json(SYNTHESIS_EVIDENCE_REGISTRY_PATH, synthesis_evidence_registry)
    write_json(SYNTHESIS_SEED_REGISTRY_PATH, synthesis_seed_registry)
    write_json(SYNTHESIS_FACET_REGISTRY_PATH, synthesis_facet_registry)
    write_json(SYNTHESIS_MANIFEST_PATH, synthesis_manifest)
    write_json(VISUAL_ATLAS_NODE_REGISTRY_PATH, visual_atlas_node_registry)
    write_json(VISUAL_ATLAS_EDGE_REGISTRY_PATH, visual_atlas_edge_registry)
    write_json(VISUAL_ATLAS_PAGE_REGISTRY_PATH, visual_atlas_page_registry)
    write_json(VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH, visual_atlas_record_locator_registry)
    write_json(VISUAL_ATLAS_MANIFEST_PATH, visual_atlas_manifest)
    write_json(GUIDED_TOUR_SEED_REGISTRY_PATH, guided_tour_seed_registry)
    write_json(GUIDED_TOUR_PAGE_REGISTRY_PATH, guided_tour_page_registry)
    write_json(GUIDED_TOUR_MANIFEST_PATH, guided_tour_manifest)
    write_json(EXPEDITION_SEED_REGISTRY_PATH, expedition_seed_registry)
    write_json(EXPEDITION_PAGE_REGISTRY_PATH, expedition_page_registry)
    write_json(EXPEDITION_MANIFEST_PATH, expedition_manifest)
    write_json(CONSTELLATION_NODE_REGISTRY_PATH, constellation_node_registry)
    write_json(CONSTELLATION_EDGE_REGISTRY_PATH, constellation_edge_registry)
    write_json(CONSTELLATION_PAGE_REGISTRY_PATH, constellation_page_registry)
    write_json(CONSTELLATION_MANIFEST_PATH, constellation_manifest)
    write_json(REPLAY_SEED_REGISTRY_PATH, replay_seed_registry)
    write_json(REPLAY_PAGE_REGISTRY_PATH, replay_page_registry)
    write_json(REPLAY_MANIFEST_PATH, replay_manifest)
    write_json(OBSERVATORY_SEED_REGISTRY_PATH, observatory_seed_registry)
    write_json(OBSERVATORY_PAGE_REGISTRY_PATH, observatory_page_registry)
    write_json(OBSERVATORY_MANIFEST_PATH, observatory_manifest)
    write_json(FULL_CORPUS_AUTHORITY_REGISTRY_PATH, full_corpus_authority_registry)
    write_json(
        FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH,
        full_corpus_basis_crosswalk_registry,
    )
    write_json(
        FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH,
        full_corpus_route_coverage_registry,
    )
    write_json(
        FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH,
        full_corpus_awakening_stage_registry,
    )
    write_json(
        FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH,
        full_corpus_awakening_agent_transition_registry,
    )
    write_json(
        FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH,
        full_corpus_appendix_governance_ledger,
    )
    write_json(FULL_CORPUS_INTEGRATION_MANIFEST_PATH, full_corpus_integration_manifest)
    write_json(AP6D_57_LOOP_CONTROL_REGISTRY_PATH, ap6d_57_loop_control_registry)
    write_json(AP6D_57_AGENT_LANE_REGISTRY_PATH, ap6d_57_agent_lane_registry)
    write_json(AP6D_57_NESTED_SEAT_MANIFEST_PATH, ap6d_57_nested_seat_manifest)
    write_json(AP6D_57_QUEST_BUNDLE_REGISTRY_PATH, ap6d_57_quest_bundle_registry)
    write_json(AP6D_57_WORKER_ACTION_REGISTRY_PATH, ap6d_57_worker_action_registry)
    write_json(AP6D_57_PRUNING_REGISTRY_PATH, ap6d_57_pruning_registry)
    write_json(
        AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH,
        ap6d_57_awakening_transition_registry,
    )
    write_json(AP6D_57_RESTART_SEED_REGISTRY_PATH, ap6d_57_restart_seed_registry)
    write_json(AP6D_57_LOOP_MANIFEST_PATH, ap6d_57_loop_manifest)
    write_json(MASTER_LOOP_STATE_PATH, master_loop_state)
    write_json(MASTER_AGENT_STATE_PATH, master_agent_state)
    write_json(MASTER_LOOP_SHARED_LATTICE_PATH, master_loop_shared_lattice)
    write_json(LP57OMEGA_LOOP_REGISTRY_PATH, lp57omega_loop_registry)
    write_json(LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH, lp57omega_agent_identity_registry)
    write_json(LP57OMEGA_COORDINATE_REGISTRY_PATH, lp57omega_coordinate_registry)
    write_json(LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH, lp57omega_quest_contract_registry)
    write_json(LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH, lp57omega_master_ledger_registry)
    write_json(LP57OMEGA_MANIFEST_PATH, lp57omega_manifest)
    write_json(DENSE_65_SHELL_REGISTRY_PATH, dense_65_shell_registry)
    write_json(DENSE_65_RQT_WITNESS_REGISTRY_PATH, dense_65_rqt_witness_registry)
    write_json(DENSE_65_RQT_OVERFLOW_REGISTRY_PATH, dense_65_rqt_overflow_registry)
    write_json(DENSE_65_MANIFEST_PATH, dense_65_manifest)
    write_json(COMMAND_MEMBRANE_PACKET_SCHEMA_PATH, command_membrane_packet_schema)
    write_json(COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH, command_membrane_watched_surface_registry)
    write_json(COMMAND_MEMBRANE_EVENT_REGISTRY_PATH, command_membrane_event_registry)
    write_json(COMMAND_MEMBRANE_CLAIM_LEDGER_PATH, command_membrane_claim_ledger)
    write_json(COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH, command_membrane_capillary_registry)
    write_json(COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH, command_membrane_latency_registry)
    write_json(COMMAND_MEMBRANE_MANIFEST_PATH, command_membrane_manifest)

    write_json(RECORD_REGISTRY_MIRROR, record_registry)
    write_json(COMMISSURE_REGISTRY_MIRROR, commissure_registry)
    write_json(METRO_REGISTRY_MIRROR, metro_registry)
    write_json(HUB_REGISTRY_MIRROR, hub_registry)
    write_json(MANIFEST_MIRROR, manifest)
    write_json(DUAL_ROUTE_REGISTRY_MIRROR, dual_route_registry)
    write_json(DIRECT_EDGE_REGISTRY_MIRROR, direct_edge_registry)
    write_json(ROUTE_COVERAGE_REGISTRY_MIRROR, route_coverage_registry)
    write_json(ROUTE_MANIFEST_MIRROR, route_manifest)
    write_json(NAVIGATOR_ALIAS_INDEX_MIRROR, navigator_alias_index)
    write_json(NAVIGATOR_FACET_INDEX_MIRROR, navigator_facet_index)
    write_json(NAVIGATOR_NEIGHBOR_INDEX_MIRROR, navigator_neighbor_index)
    write_json(NAVIGATOR_MANIFEST_MIRROR, navigator_manifest)
    write_json(COMPOSER_SEED_REGISTRY_MIRROR, composer_seed_registry)
    write_json(COMPOSER_FACET_REGISTRY_MIRROR, composer_facet_registry)
    write_json(COMPOSER_MANIFEST_MIRROR, composer_manifest)
    write_json(SYNTHESIS_EVIDENCE_REGISTRY_MIRROR, synthesis_evidence_registry)
    write_json(SYNTHESIS_SEED_REGISTRY_MIRROR, synthesis_seed_registry)
    write_json(SYNTHESIS_FACET_REGISTRY_MIRROR, synthesis_facet_registry)
    write_json(SYNTHESIS_MANIFEST_MIRROR, synthesis_manifest)
    write_json(VISUAL_ATLAS_NODE_REGISTRY_MIRROR, visual_atlas_node_registry)
    write_json(VISUAL_ATLAS_EDGE_REGISTRY_MIRROR, visual_atlas_edge_registry)
    write_json(VISUAL_ATLAS_PAGE_REGISTRY_MIRROR, visual_atlas_page_registry)
    write_json(
        VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_MIRROR,
        visual_atlas_record_locator_registry,
    )
    write_json(VISUAL_ATLAS_MANIFEST_MIRROR, visual_atlas_manifest)
    write_json(GUIDED_TOUR_SEED_REGISTRY_MIRROR, guided_tour_seed_registry)
    write_json(GUIDED_TOUR_PAGE_REGISTRY_MIRROR, guided_tour_page_registry)
    write_json(GUIDED_TOUR_MANIFEST_MIRROR, guided_tour_manifest)
    write_json(EXPEDITION_SEED_REGISTRY_MIRROR, expedition_seed_registry)
    write_json(EXPEDITION_PAGE_REGISTRY_MIRROR, expedition_page_registry)
    write_json(EXPEDITION_MANIFEST_MIRROR, expedition_manifest)
    write_json(CONSTELLATION_NODE_REGISTRY_MIRROR, constellation_node_registry)
    write_json(CONSTELLATION_EDGE_REGISTRY_MIRROR, constellation_edge_registry)
    write_json(CONSTELLATION_PAGE_REGISTRY_MIRROR, constellation_page_registry)
    write_json(CONSTELLATION_MANIFEST_MIRROR, constellation_manifest)
    write_json(REPLAY_SEED_REGISTRY_MIRROR, replay_seed_registry)
    write_json(REPLAY_PAGE_REGISTRY_MIRROR, replay_page_registry)
    write_json(REPLAY_MANIFEST_MIRROR, replay_manifest)
    write_json(OBSERVATORY_SEED_REGISTRY_MIRROR, observatory_seed_registry)
    write_json(OBSERVATORY_PAGE_REGISTRY_MIRROR, observatory_page_registry)
    write_json(OBSERVATORY_MANIFEST_MIRROR, observatory_manifest)
    write_json(FULL_CORPUS_AUTHORITY_REGISTRY_MIRROR, full_corpus_authority_registry)
    write_json(
        FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_MIRROR,
        full_corpus_basis_crosswalk_registry,
    )
    write_json(
        FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_MIRROR,
        full_corpus_route_coverage_registry,
    )
    write_json(
        FULL_CORPUS_AWAKENING_STAGE_REGISTRY_MIRROR,
        full_corpus_awakening_stage_registry,
    )
    write_json(
        FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_MIRROR,
        full_corpus_awakening_agent_transition_registry,
    )
    write_json(
        FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_MIRROR,
        full_corpus_appendix_governance_ledger,
    )
    write_json(FULL_CORPUS_INTEGRATION_MANIFEST_MIRROR, full_corpus_integration_manifest)
    write_json(AP6D_57_LOOP_CONTROL_REGISTRY_MIRROR, ap6d_57_loop_control_registry)
    write_json(AP6D_57_AGENT_LANE_REGISTRY_MIRROR, ap6d_57_agent_lane_registry)
    write_json(AP6D_57_NESTED_SEAT_MANIFEST_MIRROR, ap6d_57_nested_seat_manifest)
    write_json(AP6D_57_QUEST_BUNDLE_REGISTRY_MIRROR, ap6d_57_quest_bundle_registry)
    write_json(AP6D_57_WORKER_ACTION_REGISTRY_MIRROR, ap6d_57_worker_action_registry)
    write_json(AP6D_57_PRUNING_REGISTRY_MIRROR, ap6d_57_pruning_registry)
    write_json(
        AP6D_57_AWAKENING_TRANSITION_REGISTRY_MIRROR,
        ap6d_57_awakening_transition_registry,
    )
    write_json(AP6D_57_RESTART_SEED_REGISTRY_MIRROR, ap6d_57_restart_seed_registry)
    write_json(AP6D_57_LOOP_MANIFEST_MIRROR, ap6d_57_loop_manifest)
    write_json(LP57OMEGA_LOOP_REGISTRY_MIRROR, lp57omega_loop_registry)
    write_json(LP57OMEGA_AGENT_IDENTITY_REGISTRY_MIRROR, lp57omega_agent_identity_registry)
    write_json(LP57OMEGA_COORDINATE_REGISTRY_MIRROR, lp57omega_coordinate_registry)
    write_json(LP57OMEGA_QUEST_CONTRACT_REGISTRY_MIRROR, lp57omega_quest_contract_registry)
    write_json(LP57OMEGA_MASTER_LEDGER_REGISTRY_MIRROR, lp57omega_master_ledger_registry)
    write_json(LP57OMEGA_MANIFEST_MIRROR, lp57omega_manifest)
    write_json(DENSE_65_SHELL_REGISTRY_MIRROR, dense_65_shell_registry)
    write_json(DENSE_65_RQT_WITNESS_REGISTRY_MIRROR, dense_65_rqt_witness_registry)
    write_json(DENSE_65_RQT_OVERFLOW_REGISTRY_MIRROR, dense_65_rqt_overflow_registry)
    write_json(DENSE_65_MANIFEST_MIRROR, dense_65_manifest)
    write_json(COMMAND_MEMBRANE_PACKET_SCHEMA_MIRROR, command_membrane_packet_schema)
    write_json(COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_MIRROR, command_membrane_watched_surface_registry)
    write_json(COMMAND_MEMBRANE_EVENT_REGISTRY_MIRROR, command_membrane_event_registry)
    write_json(COMMAND_MEMBRANE_CLAIM_LEDGER_MIRROR, command_membrane_claim_ledger)
    write_json(COMMAND_MEMBRANE_CAPILLARY_REGISTRY_MIRROR, command_membrane_capillary_registry)
    write_json(COMMAND_MEMBRANE_LATENCY_REGISTRY_MIRROR, command_membrane_latency_registry)
    write_json(COMMAND_MEMBRANE_MANIFEST_MIRROR, command_membrane_manifest)
    write_json(
        FLEET_MIRROR_ROOT / FULL_CORPUS_AUTHORITY_REGISTRY_PATH.name,
        full_corpus_authority_registry,
    )
    write_json(
        FLEET_MIRROR_ROOT / FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH.name,
        full_corpus_basis_crosswalk_registry,
    )
    write_json(
        FLEET_MIRROR_ROOT / FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH.name,
        full_corpus_route_coverage_registry,
    )
    write_json(
        FLEET_MIRROR_ROOT / FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH.name,
        full_corpus_awakening_stage_registry,
    )
    write_json(
        FLEET_MIRROR_ROOT / FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH.name,
        full_corpus_awakening_agent_transition_registry,
    )
    write_json(
        FLEET_MIRROR_ROOT / FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH.name,
        full_corpus_appendix_governance_ledger,
    )
    write_json(
        FLEET_MIRROR_ROOT / FULL_CORPUS_INTEGRATION_MANIFEST_PATH.name,
        full_corpus_integration_manifest,
    )
    write_json(FLEET_MIRROR_ROOT / AP6D_57_LOOP_CONTROL_REGISTRY_PATH.name, ap6d_57_loop_control_registry)
    write_json(FLEET_MIRROR_ROOT / AP6D_57_AGENT_LANE_REGISTRY_PATH.name, ap6d_57_agent_lane_registry)
    write_json(FLEET_MIRROR_ROOT / AP6D_57_NESTED_SEAT_MANIFEST_PATH.name, ap6d_57_nested_seat_manifest)
    write_json(FLEET_MIRROR_ROOT / AP6D_57_QUEST_BUNDLE_REGISTRY_PATH.name, ap6d_57_quest_bundle_registry)
    write_json(FLEET_MIRROR_ROOT / AP6D_57_WORKER_ACTION_REGISTRY_PATH.name, ap6d_57_worker_action_registry)
    write_json(FLEET_MIRROR_ROOT / AP6D_57_PRUNING_REGISTRY_PATH.name, ap6d_57_pruning_registry)
    write_json(
        FLEET_MIRROR_ROOT / AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH.name,
        ap6d_57_awakening_transition_registry,
    )
    write_json(FLEET_MIRROR_ROOT / AP6D_57_RESTART_SEED_REGISTRY_PATH.name, ap6d_57_restart_seed_registry)
    write_json(FLEET_MIRROR_ROOT / AP6D_57_LOOP_MANIFEST_PATH.name, ap6d_57_loop_manifest)
    write_json(FLEET_MIRROR_ROOT / LP57OMEGA_LOOP_REGISTRY_PATH.name, lp57omega_loop_registry)
    write_json(
        FLEET_MIRROR_ROOT / LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH.name,
        lp57omega_agent_identity_registry,
    )
    write_json(
        FLEET_MIRROR_ROOT / LP57OMEGA_COORDINATE_REGISTRY_PATH.name,
        lp57omega_coordinate_registry,
    )
    write_json(
        FLEET_MIRROR_ROOT / LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH.name,
        lp57omega_quest_contract_registry,
    )
    write_json(
        FLEET_MIRROR_ROOT / LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH.name,
        lp57omega_master_ledger_registry,
    )
    write_json(FLEET_MIRROR_ROOT / LP57OMEGA_MANIFEST_PATH.name, lp57omega_manifest)
    write_json(FLEET_MIRROR_ROOT / DENSE_65_SHELL_REGISTRY_PATH.name, dense_65_shell_registry)
    write_json(
        FLEET_MIRROR_ROOT / DENSE_65_RQT_WITNESS_REGISTRY_PATH.name,
        dense_65_rqt_witness_registry,
    )
    write_json(
        FLEET_MIRROR_ROOT / DENSE_65_RQT_OVERFLOW_REGISTRY_PATH.name,
        dense_65_rqt_overflow_registry,
    )
    write_json(FLEET_MIRROR_ROOT / DENSE_65_MANIFEST_PATH.name, dense_65_manifest)
    write_json(FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_PACKET_SCHEMA_PATH.name, command_membrane_packet_schema)
    write_json(FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH.name, command_membrane_watched_surface_registry)
    write_json(FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_EVENT_REGISTRY_PATH.name, command_membrane_event_registry)
    write_json(FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_CLAIM_LEDGER_PATH.name, command_membrane_claim_ledger)
    write_json(FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH.name, command_membrane_capillary_registry)
    write_json(FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH.name, command_membrane_latency_registry)
    write_json(FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_MANIFEST_PATH.name, command_membrane_manifest)

    write_markdown_surfaces(
        manifest=manifest,
        hub_registry=hub_registry,
        commissure_registry=commissure_registry,
        metro_registry=metro_registry,
        route_registry=dual_route_registry,
        route_coverage_registry=route_coverage_registry,
        route_manifest=route_manifest,
        navigator_manifest=navigator_manifest,
        composer_seed_registry=composer_seed_registry,
        composer_facet_registry=composer_facet_registry,
        composer_manifest=composer_manifest,
        synthesis_seed_registry=synthesis_seed_registry,
        synthesis_facet_registry=synthesis_facet_registry,
        synthesis_manifest=synthesis_manifest,
        visual_atlas_page_registry=visual_atlas_page_registry,
        visual_atlas_markdown_pages=visual_atlas_markdown_pages,
        guided_tour_seed_registry=guided_tour_seed_registry,
        guided_tour_manifest=guided_tour_manifest,
        expedition_seed_registry=expedition_seed_registry,
        expedition_manifest=expedition_manifest,
        constellation_page_registry=constellation_page_registry,
        constellation_manifest=constellation_manifest,
        replay_seed_registry=replay_seed_registry,
        replay_page_registry=replay_page_registry,
        replay_manifest=replay_manifest,
        observatory_seed_registry=observatory_seed_registry,
        observatory_page_registry=observatory_page_registry,
        observatory_manifest=observatory_manifest,
        records=projected_records,
        atlas_payload=atlas_payload,
        docs_gate_status=docs_gate_status,
    )
    for doc_key, markdown in full_corpus_markdown_pages.items():
        write_text(HEMISPHERE_DOCS[doc_key], markdown)
    for doc_key, markdown in ap6d_57_markdown_pages.items():
        write_text(HEMISPHERE_DOCS[doc_key], markdown)
    for doc_key, markdown in lp57omega_markdown_pages.items():
        write_text(HEMISPHERE_DOCS[doc_key], markdown)
    for doc_key, markdown in dense_65_markdown_pages.items():
        write_text(HEMISPHERE_DOCS[doc_key], markdown)
    for doc_key, markdown in command_membrane_markdown_pages.items():
        write_text(HEMISPHERE_DOCS[doc_key], markdown)
    write_text(DEEPER_INTEGRATION_RECEIPT_PATH, deeper_integration_receipt)
    write_text(AP6D_57_GUILD_HALL_DOC_PATH, ap6d_57_guild_hall_doc)
    write_text(AP6D_57_TEMPLE_DOC_PATH, ap6d_57_temple_doc)
    write_text(AP6D_57_DEEP_CONTROL_DOC_PATH, ap6d_57_deep_control_doc)
    write_text(AP6D_57_RECEIPT_PATH, ap6d_57_receipt_doc)
    write_text(LP57OMEGA_GUILD_HALL_DOC_PATH, lp57omega_guild_hall_doc)
    write_text(LP57OMEGA_TEMPLE_DOC_PATH, lp57omega_temple_doc)
    write_text(LP57OMEGA_DEEP_CONTROL_DOC_PATH, lp57omega_deep_control_doc)
    write_text(LP57OMEGA_RECEIPT_PATH, lp57omega_receipt_doc)
    write_text(
        LP57OMEGA_LIMINAL_COORDINATE_STANDARD_PATH,
        lp57omega_payloads["standards"]["liminal_coordinate_standard_md"],
    )
    write_text(
        LP57OMEGA_AGENT_LEDGER_STANDARD_PATH,
        lp57omega_payloads["standards"]["agent_ledger_standard_md"],
    )
    write_text(
        LP57OMEGA_SEED_INVERSION_STANDARD_PATH,
        lp57omega_payloads["standards"]["seed_inversion_standard_md"],
    )
    write_json(
        LP57OMEGA_SEED_INVERSION_STANDARD_JSON_PATH,
        lp57omega_payloads["standards"]["seed_inversion_standard_json"],
    )
    write_text(GUILD_HALL_BOARD_PATH, lp57omega_guild_hall_board_text)
    write_text(TEMPLE_QUEST_BOARD_PATH, lp57omega_temple_board_text)
    mirror_outputs(
        record_registry=record_registry,
        commissure_registry=commissure_registry,
        metro_registry=metro_registry,
        hub_registry=hub_registry,
        manifest=manifest,
        dual_route_registry=dual_route_registry,
        direct_edge_registry=direct_edge_registry,
        route_coverage_registry=route_coverage_registry,
        route_manifest=route_manifest,
        navigator_alias_index=navigator_alias_index,
        navigator_facet_index=navigator_facet_index,
        navigator_neighbor_index=navigator_neighbor_index,
        navigator_manifest=navigator_manifest,
        composer_seed_registry=composer_seed_registry,
        composer_facet_registry=composer_facet_registry,
        composer_manifest=composer_manifest,
        synthesis_evidence_registry=synthesis_evidence_registry,
        synthesis_seed_registry=synthesis_seed_registry,
        synthesis_facet_registry=synthesis_facet_registry,
        synthesis_manifest=synthesis_manifest,
        visual_atlas_node_registry=visual_atlas_node_registry,
        visual_atlas_edge_registry=visual_atlas_edge_registry,
        visual_atlas_page_registry=visual_atlas_page_registry,
        visual_atlas_record_locator_registry=visual_atlas_record_locator_registry,
        visual_atlas_manifest=visual_atlas_manifest,
        visual_atlas_markdown_pages=visual_atlas_markdown_pages,
        guided_tour_seed_registry=guided_tour_seed_registry,
        guided_tour_page_registry=guided_tour_page_registry,
        guided_tour_manifest=guided_tour_manifest,
        expedition_seed_registry=expedition_seed_registry,
        expedition_page_registry=expedition_page_registry,
        expedition_manifest=expedition_manifest,
        constellation_node_registry=constellation_node_registry,
        constellation_edge_registry=constellation_edge_registry,
        constellation_page_registry=constellation_page_registry,
        constellation_manifest=constellation_manifest,
        replay_seed_registry=replay_seed_registry,
        replay_page_registry=replay_page_registry,
        replay_manifest=replay_manifest,
        observatory_seed_registry=observatory_seed_registry,
        observatory_page_registry=observatory_page_registry,
        observatory_manifest=observatory_manifest,
    )
    write_text(AP6D_57_GUILD_HALL_DOC_MIRROR, ap6d_57_guild_hall_doc)
    write_text(AP6D_57_TEMPLE_DOC_MIRROR, ap6d_57_temple_doc)
    write_text(AP6D_57_DEEP_CONTROL_DOC_MIRROR, ap6d_57_deep_control_doc)
    write_text(AP6D_57_RECEIPT_MIRROR, ap6d_57_receipt_doc)
    write_text(LP57OMEGA_GUILD_HALL_DOC_MIRROR, lp57omega_guild_hall_doc)
    write_text(LP57OMEGA_TEMPLE_DOC_MIRROR, lp57omega_temple_doc)
    write_text(LP57OMEGA_DEEP_CONTROL_DOC_MIRROR, lp57omega_deep_control_doc)
    write_text(LP57OMEGA_RECEIPT_MIRROR, lp57omega_receipt_doc)
    write_text(
        LP57OMEGA_LIMINAL_COORDINATE_STANDARD_MIRROR,
        lp57omega_payloads["standards"]["liminal_coordinate_standard_md"],
    )
    write_text(
        LP57OMEGA_AGENT_LEDGER_STANDARD_MIRROR,
        lp57omega_payloads["standards"]["agent_ledger_standard_md"],
    )
    write_text(
        LP57OMEGA_SEED_INVERSION_STANDARD_MIRROR,
        lp57omega_payloads["standards"]["seed_inversion_standard_md"],
    )
    write_json(
        LP57OMEGA_SEED_INVERSION_STANDARD_JSON_MIRROR,
        lp57omega_payloads["standards"]["seed_inversion_standard_json"],
    )
    # Reassert the canonical LP57 state surfaces last so older wrapper files or
    # downstream board writes cannot leave stale control-plane shells on disk.
    write_json(MASTER_LOOP_STATE_PATH, master_loop_state)
    write_json(MASTER_AGENT_STATE_PATH, master_agent_state)
    write_json(MASTER_LOOP_SHARED_LATTICE_PATH, master_loop_shared_lattice)
    write_text(GUILD_HALL_BOARD_PATH, lp57omega_guild_hall_board_text)
    write_text(TEMPLE_QUEST_BOARD_PATH, lp57omega_temple_board_text)
    return {
        "record_registry": record_registry,
        "hub_registry": hub_registry,
        "commissure_registry": commissure_registry,
        "metro_registry": metro_registry,
        "manifest": manifest,
        "dual_route_registry": dual_route_registry,
        "direct_edge_registry": direct_edge_registry,
        "route_coverage_registry": route_coverage_registry,
        "route_manifest": route_manifest,
        "navigator_alias_index": navigator_alias_index,
        "navigator_facet_index": navigator_facet_index,
        "navigator_neighbor_index": navigator_neighbor_index,
        "navigator_manifest": navigator_manifest,
        "composer_seed_registry": composer_seed_registry,
        "composer_facet_registry": composer_facet_registry,
        "composer_manifest": composer_manifest,
        "synthesis_evidence_registry": synthesis_evidence_registry,
        "synthesis_seed_registry": synthesis_seed_registry,
        "synthesis_facet_registry": synthesis_facet_registry,
        "synthesis_manifest": synthesis_manifest,
        "visual_atlas_node_registry": visual_atlas_node_registry,
        "visual_atlas_edge_registry": visual_atlas_edge_registry,
        "visual_atlas_page_registry": visual_atlas_page_registry,
        "visual_atlas_record_locator_registry": visual_atlas_record_locator_registry,
        "visual_atlas_manifest": visual_atlas_manifest,
        "guided_tour_seed_registry": guided_tour_seed_registry,
        "guided_tour_page_registry": guided_tour_page_registry,
        "guided_tour_manifest": guided_tour_manifest,
        "expedition_seed_registry": expedition_seed_registry,
        "expedition_page_registry": expedition_page_registry,
        "expedition_manifest": expedition_manifest,
        "constellation_node_registry": constellation_node_registry,
        "constellation_edge_registry": constellation_edge_registry,
        "constellation_page_registry": constellation_page_registry,
        "constellation_manifest": constellation_manifest,
        "replay_seed_registry": replay_seed_registry,
        "replay_page_registry": replay_page_registry,
        "replay_manifest": replay_manifest,
        "observatory_seed_registry": observatory_seed_registry,
        "observatory_page_registry": observatory_page_registry,
        "observatory_manifest": observatory_manifest,
        "full_corpus_authority_registry": full_corpus_authority_registry,
        "full_corpus_basis_crosswalk_registry": full_corpus_basis_crosswalk_registry,
        "full_corpus_route_coverage_registry": full_corpus_route_coverage_registry,
        "full_corpus_awakening_stage_registry": full_corpus_awakening_stage_registry,
        "full_corpus_awakening_agent_transition_registry": full_corpus_awakening_agent_transition_registry,
        "full_corpus_appendix_governance_ledger": full_corpus_appendix_governance_ledger,
        "full_corpus_integration_manifest": full_corpus_integration_manifest,
        "ap6d_57_loop_control_registry": ap6d_57_loop_control_registry,
        "ap6d_57_agent_lane_registry": ap6d_57_agent_lane_registry,
        "ap6d_57_nested_seat_manifest": ap6d_57_nested_seat_manifest,
        "ap6d_57_quest_bundle_registry": ap6d_57_quest_bundle_registry,
        "ap6d_57_worker_action_registry": ap6d_57_worker_action_registry,
        "ap6d_57_pruning_registry": ap6d_57_pruning_registry,
        "ap6d_57_awakening_transition_registry": ap6d_57_awakening_transition_registry,
        "ap6d_57_restart_seed_registry": ap6d_57_restart_seed_registry,
        "ap6d_57_loop_manifest": ap6d_57_loop_manifest,
        "master_loop_state": master_loop_state,
        "master_agent_state": master_agent_state,
        "master_loop_shared_lattice": master_loop_shared_lattice,
        "lp57omega_loop_registry": lp57omega_loop_registry,
        "lp57omega_agent_identity_registry": lp57omega_agent_identity_registry,
        "lp57omega_coordinate_registry": lp57omega_coordinate_registry,
        "lp57omega_quest_contract_registry": lp57omega_quest_contract_registry,
        "lp57omega_master_ledger_registry": lp57omega_master_ledger_registry,
        "lp57omega_manifest": lp57omega_manifest,
        "dense_65_shell_registry": dense_65_shell_registry,
        "dense_65_rqt_witness_registry": dense_65_rqt_witness_registry,
        "dense_65_rqt_overflow_registry": dense_65_rqt_overflow_registry,
        "dense_65_manifest": dense_65_manifest,
        "command_membrane_packet_schema": command_membrane_packet_schema,
        "command_membrane_watched_surface_registry": command_membrane_watched_surface_registry,
        "command_membrane_event_registry": command_membrane_event_registry,
        "command_membrane_claim_ledger": command_membrane_claim_ledger,
        "command_membrane_capillary_registry": command_membrane_capillary_registry,
        "command_membrane_latency_registry": command_membrane_latency_registry,
        "command_membrane_manifest": command_membrane_manifest,
    }


def main() -> int:
    payload = derive()
    manifest = payload["manifest"]
    print(f"Wrote hemisphere atlas: {HEMISPHERE_ATLAS_PATH}")
    print(f"Wrote hemisphere manifest: {MANIFEST_PATH}")
    print(
        "Counts: "
        f"records={manifest['counts']['record_count']} "
        f"math={manifest['counts']['math_records']} "
        f"myth={manifest['counts']['myth_records']} "
        f"commissure={manifest['counts']['commissure_records']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
