from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    COMMISSURE_REGISTRY_PATH,
    COMPOSER_FACET_REGISTRY_PATH,
    COMPOSER_MANIFEST_PATH,
    COMPOSER_SEED_REGISTRY_PATH,
    DIRECT_EDGE_REGISTRY_PATH,
    DOCS_GATE_PATH,
    DUAL_ROUTE_REGISTRY_PATH,
    EXPEDITION_MANIFEST_PATH,
    EXPEDITION_PAGE_REGISTRY_PATH,
    EXPEDITION_SEED_REGISTRY_PATH,
    FAMILY_LABELS,
    FLEET_MIRROR_ROOT,
    GUIDED_TOUR_MANIFEST_PATH,
    GUIDED_TOUR_PAGE_REGISTRY_PATH,
    GUIDED_TOUR_SEED_REGISTRY_PATH,
    HEMISPHERE_ATLAS_PATH,
    HUB_REGISTRY_PATH,
    KNOWLEDGE_FABRIC_SHORTCUTS_PATH,
    MANIFEST_PATH,
    METRO_REGISTRY_PATH,
    NAVIGATOR_ALIAS_INDEX_PATH,
    NAVIGATOR_FACET_INDEX_PATH,
    NAVIGATOR_MANIFEST_PATH,
    NAVIGATOR_NEIGHBOR_INDEX_PATH,
    MATH_HUB_ID,
    MYTH_HUB_ID,
    OBSERVATORY_MANIFEST_PATH,
    OBSERVATORY_PAGE_REGISTRY_PATH,
    OBSERVATORY_SEED_REGISTRY_PATH,
    PRIMARY_HF_ROUTE_KEYS,
    PT2_METRO_INTERLOCKS_PATH,
    PT2_SHORTCUT_REGISTRY_PATH,
    RECORD_REGISTRY_PATH,
    REPLAY_MANIFEST_PATH,
    REPLAY_PAGE_REGISTRY_PATH,
    REPLAY_SEED_REGISTRY_PATH,
    ROUTE_COVERAGE_REGISTRY_PATH,
    ROUTE_MANIFEST_PATH,
    SYNTHESIS_EVIDENCE_REGISTRY_PATH,
    SYNTHESIS_FACET_REGISTRY_PATH,
    SYNTHESIS_MANIFEST_PATH,
    SYNTHESIS_SEED_REGISTRY_PATH,
    CONSTELLATION_EDGE_REGISTRY_PATH,
    CONSTELLATION_MANIFEST_PATH,
    CONSTELLATION_NODE_REGISTRY_PATH,
    CONSTELLATION_PAGE_REGISTRY_PATH,
    UNIFIED_HUB_ID,
    VISUAL_ATLAS_EDGE_REGISTRY_PATH,
    VISUAL_ATLAS_MANIFEST_PATH,
    VISUAL_ATLAS_NODE_REGISTRY_PATH,
    VISUAL_ATLAS_PAGE_REGISTRY_PATH,
    VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH,
    VERIFY_PATH,
    load_docs_gate_status,
    load_json,
    normalize_path,
    write_json,
)
from self_actualize.runtime.hemisphere_navigator_query_engine import (
    facet as navigator_facet_query,
    load_navigator_registries,
    record as navigator_record_query,
    search as navigator_search_query,
)
from self_actualize.runtime.hemisphere_navigator_support import (
    normalize as navigator_normalize,
)
from self_actualize.runtime.hemisphere_route_composer_support import (
    ROUTE_STAGE_ORDER,
    facet as composer_facet_query,
    load_route_composer_registries,
    record as composer_record_query,
    search as composer_search_query,
)
from self_actualize.runtime.hemisphere_synthesis_support import (
    facet as synthesis_facet_query,
    load_synthesis_registries,
    record as synthesis_record_query,
    search as synthesis_search_query,
)
from self_actualize.runtime.hemisphere_guided_tour_support import (
    GUIDED_TOUR_STAGE_ORDER,
    load_guided_tour_registries,
    page as guided_tour_page_query,
    page_seed_ids,
    facet as guided_tour_facet_query,
    record as guided_tour_record_query,
    search as guided_tour_search_query,
)
from self_actualize.runtime.hemisphere_expedition_support import (
    load_expedition_registries,
    page as expedition_page_query,
    facet as expedition_facet_query,
    record as expedition_record_query,
    search as expedition_search_query,
)
from self_actualize.runtime.hemisphere_constellation_support import (
    CONSTELLATION_RECORD_CAP,
    load_constellation_registries,
    page as constellation_page_query,
    facet as constellation_facet_query,
    record as constellation_record_query,
    search as constellation_search_query,
)
from self_actualize.runtime.hemisphere_replay_support import (
    REPLAY_PASS_ORDER,
    load_replay_registries,
    page as replay_page_query,
    facet as replay_facet_query,
    record as replay_record_query,
    search as replay_search_query,
)
from self_actualize.runtime.hemisphere_observatory_support import (
    load_observatory_registries,
    page as observatory_page_query,
    facet as observatory_facet_query,
    record as observatory_record_query,
    search as observatory_search_query,
)
from self_actualize.runtime.hemisphere_full_corpus_integration_support import (
    CORPUS_ATLAS_PATH,
    ARCHIVE_ATLAS_PATH,
    FULL_CORPUS_AUTHORITY_REGISTRY_PATH,
    FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH,
    FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH,
    FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH,
    FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH,
    FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH,
    FULL_CORPUS_INTEGRATION_MANIFEST_PATH,
)
from self_actualize.runtime.hemisphere_ap6d_57_loop_support import (
    AP6D_57_AGENT_LANE_REGISTRY_PATH,
    AP6D_57_ATLAS_SEAT_TOTAL,
    AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH,
    AP6D_57_DEEP_CONTROL_DOC_PATH,
    AP6D_57_GUILD_HALL_DOC_PATH,
    AP6D_57_HEMISPHERE_DOCS,
    AP6D_57_LIMINAL_PACKET_COUNT,
    AP6D_57_LOOP_CONTROL_REGISTRY_PATH,
    AP6D_57_LOOP_COUNT,
    AP6D_57_LOOP_MANIFEST_PATH,
    AP6D_57_MASTER_AGENT_COUNT,
    AP6D_57_NESTED_SEAT_MANIFEST_PATH,
    AP6D_57_OWNERABLE_PACKET_COUNT,
    AP6D_57_PRUNING_REGISTRY_PATH,
    AP6D_57_QUEST_BUNDLE_REGISTRY_PATH,
    AP6D_57_RECEIPT_PATH,
    AP6D_57_RESTART_SEED_REGISTRY_PATH,
    AP6D_57_SYNAPTIC_SEAT_COUNT,
    AP6D_57_GOVERNANCE_FIBER_COUNT,
    AP6D_57_TEMPLE_DOC_PATH,
    AP6D_57_WORKER_ACTION_REGISTRY_PATH,
    GUILD_HALL_BOARD_PATH,
    TEMPLE_QUEST_BOARD_PATH,
)
from self_actualize.runtime.hemisphere_lp57omega_support import (
    COORDINATE_DIMENSIONS as LP57OMEGA_COORDINATE_DIMENSIONS,
    LEDGER_FIELDS as LP57OMEGA_LEDGER_FIELDS,
    LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH,
    LP57OMEGA_COORDINATE_REGISTRY_PATH,
    LP57OMEGA_DEEP_CONTROL_DOC_PATH,
    LP57OMEGA_GUILD_HALL_DOC_PATH,
    LP57OMEGA_HEMISPHERE_DOCS,
    LP57OMEGA_LOOP_COUNT,
    LP57OMEGA_LOOP_REGISTRY_PATH,
    LP57OMEGA_MANIFEST_PATH,
    LP57OMEGA_MASTER_AGENT_COUNT,
    LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH,
    LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH,
    LP57OMEGA_RECEIPT_PATH,
    LP57OMEGA_TEMPLE_DOC_PATH,
    MASTER_AGENT_STATE_PATH,
    MASTER_LOOP_SHARED_LATTICE_PATH,
    MASTER_LOOP_STATE_PATH,
    QUEST_CONTRACT_FIELDS as LP57OMEGA_QUEST_CONTRACT_FIELDS,
)
from self_actualize.runtime.hemisphere_dense_65_shell_support import (
    DENSE_65_GROUP_COUNTS,
    DENSE_65_HEMISPHERE_DOCS,
    DENSE_65_MANIFEST_PATH,
    DENSE_65_PRIMARY_CAP,
    DENSE_65_PRIOR_SEED_POSITION,
    DENSE_65_RQT_OVERFLOW_REGISTRY_PATH,
    DENSE_65_RQT_WITNESS_REGISTRY_PATH,
    DENSE_65_RING_ORDER,
    DENSE_65_SHELL_REGISTRY_PATH,
    DENSE_65_SHELL_ROWS,
    DENSE_65_R_ROWS,
    DENSE_65_Q_ROWS,
    DENSE_65_T_ROWS,
    canonical_hide_pole,
)
from self_actualize.runtime.hemisphere_command_membrane_support import (
    COMMAND_MEMBRANE_ANT_CLASSES,
    COMMAND_MEMBRANE_CAPILLARY_COEFFICIENTS,
    COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH,
    COMMAND_MEMBRANE_CLAIM_FIELDS,
    COMMAND_MEMBRANE_CLAIM_LEDGER_PATH,
    COMMAND_MEMBRANE_EVENT_REGISTRY_PATH,
    COMMAND_MEMBRANE_EXPECTED_SOURCE_IDS,
    COMMAND_MEMBRANE_HEMISPHERE_DOCS,
    COMMAND_MEMBRANE_LATENCY_METRICS,
    COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH,
    COMMAND_MEMBRANE_MANIFEST_PATH,
    COMMAND_MEMBRANE_PACKET_FIELDS,
    COMMAND_MEMBRANE_PACKET_SCHEMA_PATH,
    COMMAND_MEMBRANE_PUBLIC_TOPK,
    COMMAND_MEMBRANE_ROUTE_CLASS,
    COMMAND_MEMBRANE_ROUTE_POLICY,
    COMMAND_MEMBRANE_TTL,
    COMMAND_MEMBRANE_VESSEL_THRESHOLDS,
    COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH,
)


VERIFY_COMMAND = "python -m self_actualize.runtime.verify_myth_math_hemisphere_brain"
FLOAT_TOLERANCE = 0.00001
FIXTURE_EXPECTATIONS = {
    "complete tomes/aqm - lm - n+7/aqm master tome.docx": "MATH",
    "myth - math/khipu/working/andean myth encoding.docx": "MYTH",
}
ROUTE_REQUIRED_FIELDS = [
    "route_id",
    "hemisphere",
    "route_role",
    "route_mode",
    "hub_id",
    "grand_central_exchange",
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
    "addr4",
    "face6",
    "arc7",
    "depth5",
    "dynamic_weights",
    "replay_policy",
    "proof_state",
    "docs_gate_status",
]
EXPECTED_DYNAMIC_WEIGHT_KEYS = {
    "salience",
    "proof",
    "freshness",
    "cost",
    "continuity",
    "confidence",
    "replay_value",
}
EXPECTED_LIMINAL_KEYS = {"omega", "integration", "coherence", "function"}
ROUTE_SIDES = ("MATH", "MYTH")


def run_check(label: str, ok: bool, details: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": label,
        "status": "OK" if ok else "FAIL",
        "details": details,
    }


def record_lookup(records: list[dict[str, Any]], suffix: str) -> dict[str, Any] | None:
    suffix_normalized = normalize_path(suffix).lower()
    for record in records:
        relative_path = normalize_path(record.get("relative_path", "")).lower()
        if relative_path.endswith(suffix_normalized):
            return record
    return None


def expected_route_role(record: dict[str, Any], hemisphere: str) -> str:
    return "primary" if record.get("primary_hemisphere") == hemisphere else "secondary"


def expected_route_mode(record: dict[str, Any], hemisphere: str) -> str:
    if record.get("primary_hemisphere") == hemisphere:
        return "direct_native"
    if record.get("bridge_intensity", 0.0) >= 0.45:
        return "commissure_direct"
    return "cross_hemisphere_transfer"


def expected_exchange(hemisphere: str, route_mode: str) -> str:
    if route_mode == "commissure_direct":
        return "commissure"
    return "GCL" if hemisphere == "MATH" else "GCR"


def expected_field_id(field_vector: dict[str, float]) -> str:
    if field_vector["aether_density"] >= 0.78 and field_vector["tunnel_cost"] <= 0.55:
        return "Aether"
    if field_vector["zero_proximity"] >= 0.61 and field_vector["tunnel_cost"] <= 0.58:
        return "TunnelGeodesic"
    if field_vector["aether_density"] >= 0.65 and field_vector["resonance_pressure"] >= 0.56:
        return "CloudManifold"
    if field_vector["resonance_pressure"] >= 0.52:
        return "ResonancePressureBand"
    if field_vector["rail_hardness"] >= 0.62:
        return "RailHardeningBand"
    return "Zero"


def expected_zpoint_id(record: dict[str, Any], route_packet: dict[str, Any]) -> str:
    if route_packet["field_id"] == "Aether":
        return "Z5"
    if route_packet["target_system"] == "HDSCTMetro":
        return "Z3"
    if route_packet["target_system"] in {"AthenaFleetMetro", "CrossCorpusMycelial"}:
        return "Z4"
    if (
        route_packet["tract"] == "replay"
        or record.get("family") in {"void-and-collapse", "helical-recursion-engine"}
    ):
        return "Z1"
    if (
        route_packet["route_role"] == "secondary"
        and record.get("bridge_intensity", 0.0) >= 0.70
    ):
        return "Z2"
    return "Z0"


def expected_geodesic_mode(field_vector: dict[str, float]) -> str:
    if field_vector["zero_proximity"] >= 0.64:
        return "z-point tunnel"
    if field_vector["aether_density"] >= 0.72:
        return "aether geodesic"
    return "rail transit"


def expected_preferred_space(route_packet: dict[str, Any]) -> str:
    if (
        route_packet["field_id"] in {"Aether", "CloudManifold", "TunnelGeodesic"}
        or route_packet["geodesic_mode"] != "rail transit"
    ):
        return "Field3D"
    if route_packet["route_role"] == "primary":
        return "Organism3D"
    if len(route_packet["dominant_lens_system"]) >= 2:
        return "Lens3D"
    return "Transit3D"


def route_field_present(field: str, value: Any) -> bool:
    if field == "interlock_ids":
        return isinstance(value, list)
    if field in {
        "station_path",
        "return_path",
        "basis_anchor_ids",
        "metro_line_ids",
        "transform_chain",
        "supported_spaces",
    }:
        return isinstance(value, list) and bool(value)
    if field in {
        "lens_weight_vector",
        "liminal_vector",
        "aether_point",
        "dynamic_weights",
    }:
        return isinstance(value, dict) and bool(value)
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None


def build_route_lookup(
    routes: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    lookup: dict[str, dict[str, dict[str, Any]]] = {}
    for route in routes:
        lookup.setdefault(route["record_id"], {})[route["hemisphere"]] = route
    return lookup


def build_edge_lookup(
    edges: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    lookup: dict[str, dict[str, dict[str, Any]]] = {}
    for edge in edges:
        lookup.setdefault(edge["record_id"], {})[edge["hemisphere"]] = edge
    return lookup


def build_coverage_lookup(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {row["record_id"]: row for row in rows}


def build_atlas_edge_lookup(
    edges: list[dict[str, Any]],
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    lookup: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for edge in edges:
        record_id = edge.get("record_id")
        if not record_id:
            continue
        lookup.setdefault(record_id, {}).setdefault(edge.get("edge_type", ""), []).append(edge)
    return lookup


def page_exists(page_entry: dict[str, Any]) -> bool:
    canonical_path = Path(page_entry.get("canonical_path", ""))
    mirror_path = Path(page_entry.get("mirror_path", ""))
    return canonical_path.is_file() and mirror_path.is_file()


def alias_has_record(
    alias_index: dict[str, Any],
    alias_value: str,
    record_id: str,
    allowed_kinds: set[str] | None = None,
) -> bool:
    entries = alias_index.get("aliases_by_norm", {}).get(navigator_normalize(alias_value), [])
    for entry in entries:
        if entry.get("record_id") != record_id:
            continue
        if allowed_kinds is not None and entry.get("alias_kind") not in allowed_kinds:
            continue
        return True
    return False


def response_has_record(response: dict[str, Any], record_id: str) -> bool:
    if response.get("best_match", {}).get("record_id") == record_id:
        return True
    for candidate in response.get("candidates", []):
        if candidate.get("record_id") == record_id:
            return True
    return False


def itinerary_stage_map(itinerary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        stage.get("stage", ""): stage
        for stage in itinerary.get("stages", [])
    }


def composer_response_shape_ok(response: dict[str, Any]) -> bool:
    seed_record = response.get("seed_record")
    if not seed_record or not seed_record.get("record_id"):
        return False
    for hemisphere_key in ("math_itinerary", "myth_itinerary"):
        itinerary = response.get(hemisphere_key, {})
        if itinerary.get("stage_order") != ROUTE_STAGE_ORDER:
            return False
        stages = itinerary.get("stages", [])
        if [stage.get("stage", "") for stage in stages] != ROUTE_STAGE_ORDER:
            return False
        stage_map = itinerary_stage_map(itinerary)
        seed_stage = stage_map.get("seed", {})
        hub_stage = stage_map.get("hemisphere_hub", {})
        exit_stage = stage_map.get("exit", {})
        if seed_stage.get("kind") != "record_stop":
            return False
        if "MATH" not in seed_stage.get("paired_routes", {}) or "MYTH" not in seed_stage.get("paired_routes", {}):
            return False
        if hub_stage.get("kind") != "hub_stop":
            return False
        if exit_stage.get("kind") != "exit":
            return False
    shared_spine = response.get("shared_spine", {}).get("sequence", [])
    if [item.get("kind", "") for item in shared_spine] != ["record_seed", "hub", "hub", "hub"]:
        return False
    if len(shared_spine) < 4 or shared_spine[2].get("hub_id") != "GC0-UNIFIED-CORPUS":
        return False
    return bool(response.get("bridge_profile", {}).get("mode"))


def synthesis_response_shape_ok(response: dict[str, Any]) -> bool:
    seed_record = response.get("seed_record")
    if not seed_record or not seed_record.get("record_id"):
        return False
    if response.get("section_order") != ["MATH", "MYTH", "Unified", "Bridge", "Appendix Support"]:
        return False
    evidence_ledger = response.get("evidence_ledger", {})
    if not isinstance(evidence_ledger, dict) or not evidence_ledger:
        return False
    required_sections = [
        response.get("math_synthesis", {}),
        response.get("myth_synthesis", {}),
        response.get("unified_synthesis", {}),
        response.get("bridge_interpretation", {}),
    ]
    for section in required_sections:
        bullets = section.get("bullets", [])
        if not bullets:
            return False
        for bullet in bullets:
            support_ids = bullet.get("support_ids", [])
            if not bullet.get("text", "").strip() or not support_ids:
                return False
            for support_id in support_ids:
                row = evidence_ledger.get(support_id)
                if row is None:
                    return False
                if not {
                    "support_id",
                    "record_id",
                    "relative_path",
                    "hemisphere",
                    "stage",
                    "evidence_kind",
                }.issubset(row):
                    return False
    appendix_support = response.get("appendix_support", {})
    appendix_bullets = appendix_support.get("bullets", [])
    if not appendix_bullets:
        return False
    for bullet in appendix_bullets:
        support_ids = bullet.get("support_ids", [])
        if not bullet.get("text", "").strip() or not support_ids:
            return False
        for support_id in support_ids:
            if support_id not in evidence_ledger:
                return False
    if len(response.get("alternative_seeds", [])) > 3:
        return False
    return True


def guided_tour_response_shape_ok(
    response: dict[str, Any],
    page_lookup: dict[str, dict[str, Any]],
) -> bool:
    seed_record = response.get("seed_record")
    if not seed_record or not seed_record.get("record_id"):
        return False
    if response.get("tour_stage_order") != GUIDED_TOUR_STAGE_ORDER:
        return False
    source_page = response.get("source_page", {})
    if not source_page.get("page_id"):
        return False
    if source_page.get("page_id") not in page_lookup:
        return False
    for leg_key in ("math_leg", "myth_leg"):
        leg = response.get(leg_key, {})
        if not leg.get("selected_route_header", {}).get("route_id"):
            return False
        if not leg.get("composer_itinerary_header", {}).get("stages"):
            return False
        if not leg.get("synthesis_section_preview", {}).get("bullets"):
            return False
        for page_id in leg.get("atlas_page_ids", []):
            if page_id not in page_lookup:
                return False
    hub_crossing = response.get("hub_crossing", {})
    if (
        not hub_crossing.get("source_hub_id")
        or hub_crossing.get("unified_hub_id") != "GC0-UNIFIED-CORPUS"
        or not hub_crossing.get("target_hub_id")
        or not hub_crossing.get("bridge_mode")
    ):
        return False
    synthesis_landing = response.get("synthesis_landing", {})
    if not synthesis_landing.get("surface_id") or not synthesis_landing.get("sections"):
        return False
    page_spine = response.get("page_spine", [])
    if not page_spine:
        return False
    for page in page_spine:
        if page.get("page_id") not in page_lookup:
            return False
    exit_links = response.get("exit_links", {})
    for key in ("record_locator", "family", "first_anchor", "math_topology", "myth_topology"):
        page_id = exit_links.get(key, {}).get("page_id", "")
        if page_id and page_id not in page_lookup:
            return False
    if not exit_links.get("synthesis_surface", {}).get("surface_id"):
        return False
    if not response.get("proof_summary", {}):
        return False
    if len(response.get("alternative_seeds", [])) > 3:
        return False
    return True


def expedition_response_shape_ok(
    response: dict[str, Any],
    page_lookup: dict[str, dict[str, Any]],
) -> bool:
    seed_record = response.get("seed_record")
    if not seed_record or not seed_record.get("record_id"):
        return False
    source_page = response.get("source_page", {})
    if source_page.get("page_id") not in page_lookup:
        return False
    seed_tour = response.get("seed_tour", {})
    if seed_tour.get("seed_record", {}).get("record_id") != seed_record.get("record_id"):
        return False
    if not response.get("shared_hubs", {}).get("hub_ids"):
        return False
    unique_pages = response.get("page_matrix", {}).get("unique_pages", [])
    if not unique_pages:
        return False
    for page in unique_pages:
        if page.get("page_id") not in page_lookup:
            return False
    if not response.get("synthesis_landings", {}).get("seed", {}).get("surface_id"):
        return False
    for bucket_name in ("same_primary_target", "same_anchor", "same_corridor", "commissure_peers"):
        for entry in response.get("companion_tours", {}).get(bucket_name, []):
            if not entry.get("record", {}).get("record_id"):
                return False
            if not entry.get("tour_header", {}).get("page_spine_ids"):
                return False
    if len(response.get("alternative_seeds", [])) > 3:
        return False
    return bool(response.get("exit_links")) and bool(response.get("proof_summary"))


def constellation_response_shape_ok(
    response: dict[str, Any],
    page_lookup: dict[str, dict[str, Any]],
) -> bool:
    seed_record = response.get("seed_record")
    if not seed_record or not seed_record.get("record_id"):
        return False
    record_nodes = [
        node for node in response.get("constellation_nodes", [])
        if node.get("kind") == "record"
    ]
    if not record_nodes or len(record_nodes) > CONSTELLATION_RECORD_CAP:
        return False
    if record_nodes[0].get("record_id") != seed_record.get("record_id"):
        return False
    hub_ids = {
        node.get("hub_id", "")
        for node in response.get("constellation_nodes", [])
        if node.get("kind") == "hub"
    }
    if {MATH_HUB_ID, MYTH_HUB_ID, UNIFIED_HUB_ID} - hub_ids:
        return False
    if not response.get("constellation_edges", {}):
        return False
    if not response.get("gc0_bridge", {}).get("bridge_mode"):
        return False
    for page in response.get("page_spine", []):
        if page.get("page_id") not in page_lookup:
            return False
    if len(response.get("alternative_seeds", [])) > 3:
        return False
    return bool(response.get("exit_links")) and bool(response.get("proof_summary"))


def replay_response_shape_ok(
    response: dict[str, Any],
    evidence_ledger: dict[str, Any],
) -> bool:
    seed_record = response.get("seed_record")
    if not seed_record or not seed_record.get("record_id"):
        return False
    if response.get("replay_passes") != REPLAY_PASS_ORDER:
        return False
    checkpoints = response.get("checkpoints", [])
    if [checkpoint.get("pass", "") for checkpoint in checkpoints] != REPLAY_PASS_ORDER:
        return False
    if not response.get("support_ids"):
        return False
    for support_id in response.get("support_ids", []):
        if support_id not in evidence_ledger:
            return False
    for checkpoint in checkpoints:
        if not checkpoint.get("text", "").strip():
            return False
        if not checkpoint.get("support_ids"):
            return False
        for support_id in checkpoint.get("support_ids", []):
            if support_id not in evidence_ledger:
                return False
    if len(response.get("alternative_seeds", [])) > 3:
        return False
    return bool(response.get("return_links")) and bool(response.get("proof_summary"))


def observatory_response_shape_ok(response: dict[str, Any]) -> bool:
    seed_record = response.get("seed_record")
    if not seed_record or not seed_record.get("record_id"):
        return False
    if not response.get("field_status", {}).get("docs_gate_status"):
        return False
    if not response.get("best_tour", {}).get("bridge_mode"):
        return False
    if not response.get("best_expedition", {}).get("companion_counts"):
        return False
    if not response.get("best_constellation", {}).get("record_node_count"):
        return False
    if not response.get("best_replay", {}).get("pass_count"):
        return False
    if not response.get("best_synthesis_landing", {}).get("surface_id"):
        return False
    if not response.get("operator_links"):
        return False
    if len(response.get("alternative_seeds", [])) > 3:
        return False
    return bool(response.get("watchpoints"))


def verify_payload() -> dict[str, Any]:
    atlas_payload = load_json(HEMISPHERE_ATLAS_PATH)
    record_registry = load_json(RECORD_REGISTRY_PATH)
    commissure_registry = load_json(COMMISSURE_REGISTRY_PATH)
    metro_registry = load_json(METRO_REGISTRY_PATH)
    hub_registry = load_json(HUB_REGISTRY_PATH)
    manifest = load_json(MANIFEST_PATH)
    dual_route_registry = load_json(DUAL_ROUTE_REGISTRY_PATH)
    direct_edge_registry = load_json(DIRECT_EDGE_REGISTRY_PATH)
    route_coverage_registry = load_json(ROUTE_COVERAGE_REGISTRY_PATH)
    route_manifest = load_json(ROUTE_MANIFEST_PATH)
    navigator_alias_index = load_json(NAVIGATOR_ALIAS_INDEX_PATH)
    navigator_facet_index = load_json(NAVIGATOR_FACET_INDEX_PATH)
    navigator_neighbor_index = load_json(NAVIGATOR_NEIGHBOR_INDEX_PATH)
    navigator_manifest = load_json(NAVIGATOR_MANIFEST_PATH)
    composer_seed_registry = load_json(COMPOSER_SEED_REGISTRY_PATH)
    composer_facet_registry = load_json(COMPOSER_FACET_REGISTRY_PATH)
    composer_manifest = load_json(COMPOSER_MANIFEST_PATH)
    synthesis_evidence_registry = load_json(SYNTHESIS_EVIDENCE_REGISTRY_PATH)
    synthesis_seed_registry = load_json(SYNTHESIS_SEED_REGISTRY_PATH)
    synthesis_facet_registry = load_json(SYNTHESIS_FACET_REGISTRY_PATH)
    synthesis_manifest = load_json(SYNTHESIS_MANIFEST_PATH)
    visual_atlas_node_registry = load_json(VISUAL_ATLAS_NODE_REGISTRY_PATH)
    visual_atlas_edge_registry = load_json(VISUAL_ATLAS_EDGE_REGISTRY_PATH)
    visual_atlas_page_registry = load_json(VISUAL_ATLAS_PAGE_REGISTRY_PATH)
    visual_atlas_record_locator_registry = load_json(VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH)
    visual_atlas_manifest = load_json(VISUAL_ATLAS_MANIFEST_PATH)
    guided_tour_seed_registry = load_json(GUIDED_TOUR_SEED_REGISTRY_PATH)
    guided_tour_page_registry = load_json(GUIDED_TOUR_PAGE_REGISTRY_PATH)
    guided_tour_manifest = load_json(GUIDED_TOUR_MANIFEST_PATH)
    expedition_seed_registry = load_json(EXPEDITION_SEED_REGISTRY_PATH)
    expedition_page_registry = load_json(EXPEDITION_PAGE_REGISTRY_PATH)
    expedition_manifest = load_json(EXPEDITION_MANIFEST_PATH)
    constellation_node_registry = load_json(CONSTELLATION_NODE_REGISTRY_PATH)
    constellation_edge_registry = load_json(CONSTELLATION_EDGE_REGISTRY_PATH)
    constellation_page_registry = load_json(CONSTELLATION_PAGE_REGISTRY_PATH)
    constellation_manifest = load_json(CONSTELLATION_MANIFEST_PATH)
    replay_seed_registry = load_json(REPLAY_SEED_REGISTRY_PATH)
    replay_page_registry = load_json(REPLAY_PAGE_REGISTRY_PATH)
    replay_manifest = load_json(REPLAY_MANIFEST_PATH)
    observatory_seed_registry = load_json(OBSERVATORY_SEED_REGISTRY_PATH)
    observatory_page_registry = load_json(OBSERVATORY_PAGE_REGISTRY_PATH)
    observatory_manifest = load_json(OBSERVATORY_MANIFEST_PATH)
    full_corpus_authority_registry = load_json(FULL_CORPUS_AUTHORITY_REGISTRY_PATH)
    full_corpus_basis_crosswalk_registry = load_json(
        FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH
    )
    full_corpus_route_coverage_registry = load_json(
        FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH
    )
    full_corpus_awakening_stage_registry = load_json(
        FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH
    )
    full_corpus_awakening_agent_transition_registry = load_json(
        FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH
    )
    full_corpus_appendix_governance_ledger = load_json(
        FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH
    )
    full_corpus_integration_manifest = load_json(FULL_CORPUS_INTEGRATION_MANIFEST_PATH)
    ap6d_57_loop_control_registry = load_json(AP6D_57_LOOP_CONTROL_REGISTRY_PATH)
    ap6d_57_agent_lane_registry = load_json(AP6D_57_AGENT_LANE_REGISTRY_PATH)
    ap6d_57_nested_seat_manifest = load_json(AP6D_57_NESTED_SEAT_MANIFEST_PATH)
    ap6d_57_quest_bundle_registry = load_json(AP6D_57_QUEST_BUNDLE_REGISTRY_PATH)
    ap6d_57_worker_action_registry = load_json(AP6D_57_WORKER_ACTION_REGISTRY_PATH)
    ap6d_57_pruning_registry = load_json(AP6D_57_PRUNING_REGISTRY_PATH)
    ap6d_57_awakening_transition_registry = load_json(AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH)
    ap6d_57_restart_seed_registry = load_json(AP6D_57_RESTART_SEED_REGISTRY_PATH)
    ap6d_57_loop_manifest = load_json(AP6D_57_LOOP_MANIFEST_PATH)
    master_loop_state = load_json(MASTER_LOOP_STATE_PATH)
    master_agent_state = load_json(MASTER_AGENT_STATE_PATH)
    master_loop_shared_lattice = load_json(MASTER_LOOP_SHARED_LATTICE_PATH)
    lp57omega_loop_registry = load_json(LP57OMEGA_LOOP_REGISTRY_PATH)
    lp57omega_agent_identity_registry = load_json(LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH)
    lp57omega_coordinate_registry = load_json(LP57OMEGA_COORDINATE_REGISTRY_PATH)
    lp57omega_quest_contract_registry = load_json(LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH)
    lp57omega_master_ledger_registry = load_json(LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH)
    lp57omega_manifest = load_json(LP57OMEGA_MANIFEST_PATH)
    dense_65_shell_registry = load_json(DENSE_65_SHELL_REGISTRY_PATH)
    dense_65_rqt_witness_registry = load_json(DENSE_65_RQT_WITNESS_REGISTRY_PATH)
    dense_65_rqt_overflow_registry = load_json(DENSE_65_RQT_OVERFLOW_REGISTRY_PATH)
    dense_65_manifest = load_json(DENSE_65_MANIFEST_PATH)
    command_membrane_packet_schema = load_json(COMMAND_MEMBRANE_PACKET_SCHEMA_PATH)
    command_membrane_watched_surface_registry = load_json(COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH)
    command_membrane_event_registry = load_json(COMMAND_MEMBRANE_EVENT_REGISTRY_PATH)
    command_membrane_claim_ledger = load_json(COMMAND_MEMBRANE_CLAIM_LEDGER_PATH)
    command_membrane_capillary_registry = load_json(COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH)
    command_membrane_latency_registry = load_json(COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH)
    command_membrane_manifest = load_json(COMMAND_MEMBRANE_MANIFEST_PATH)
    full_live_atlas = load_json(CORPUS_ATLAS_PATH)
    full_archive_atlas = load_json(ARCHIVE_ATLAS_PATH)

    live_interlocks = {
        item["interlock_id"]
        for item in load_json(PT2_METRO_INTERLOCKS_PATH).get("interlocks", [])
    }
    live_pt2_shortcuts = {
        item["shortcut_id"]
        for item in load_json(PT2_SHORTCUT_REGISTRY_PATH).get("shortcuts", [])
    }
    live_kf_shortcuts = {
        item["shortcut_id"]
        for item in load_json(KNOWLEDGE_FABRIC_SHORTCUTS_PATH).get("shortcuts", [])
    }

    records = record_registry.get("records", [])
    routes = dual_route_registry.get("routes", [])
    edges = direct_edge_registry.get("edges", [])
    coverage_rows = route_coverage_registry.get("records", [])
    route_lookup = build_route_lookup(routes)
    edge_lookup = build_edge_lookup(edges)
    coverage_lookup = build_coverage_lookup(coverage_rows)
    atlas_edge_lookup = build_atlas_edge_lookup(visual_atlas_edge_registry.get("edges", []))

    unique_sha_count = len({record["sha256"] for record in atlas_payload.get("records", [])})
    checks: list[dict[str, Any]] = []

    checks.append(
        run_check(
            "registry_count",
            len(records) == unique_sha_count,
            {
                "registry_count": len(records),
                "unique_sha_count": unique_sha_count,
            },
        )
    )

    route_count_ok = (
        len(routes) == len(records) * 2
        and len(edges) == len(records) * 2
        and len(coverage_rows) == len(records)
        and dual_route_registry.get("route_count") == len(routes)
        and direct_edge_registry.get("edge_count") == len(edges)
        and route_coverage_registry.get("record_count") == len(coverage_rows)
    )
    checks.append(
        run_check(
            "dual_route_counts",
            route_count_ok,
            {
                "record_count": len(records),
                "route_count": len(routes),
                "edge_count": len(edges),
                "coverage_rows": len(coverage_rows),
            },
        )
    )

    weight_violations = []
    required_field_violations = []
    missing_navigation = []
    bridge_records = []
    metadata_confidence_violations = []
    route_shape_violations = []
    route_alignment_violations = []
    route_registry_violations = []
    route_projection_violations = []
    interlock_violations = []
    shortcut_violations = []
    edge_violations = []
    coverage_violations = []
    metadata_route_violations = []
    navigator_alias_violations = []
    navigator_facet_violations = []
    navigator_neighbor_violations = []
    composer_seed_violations = []
    composer_facet_violations = []
    synthesis_evidence_violations = []
    synthesis_seed_violations = []
    synthesis_facet_violations = []
    visual_atlas_node_violations = []
    visual_atlas_edge_violations = []
    visual_atlas_page_violations = []
    visual_atlas_locator_violations = []

    for record in records:
        missing = [field for field in record_registry["required_fields"] if field not in record]
        if missing:
            required_field_violations.append(
                {"record_id": record["record_id"], "missing_fields": missing}
            )

        total = round(record["math_weight"] + record["myth_weight"], 6)
        if abs(total - 1.0) > FLOAT_TOLERANCE:
            weight_violations.append({"record_id": record["record_id"], "total": total})

        if (
            not record.get("primary_hemisphere")
            or not record.get("hub_id")
            or not record.get("basis_anchor_ids")
            or not record.get("holo_address")
        ):
            missing_navigation.append(record["record_id"])

        if record.get("bridge_class") == "commissure_bridge":
            bridge_records.append(record["record_id"])

        if not record.get("text_extractable") and record.get("confidence", 1.0) > 0.65:
            metadata_confidence_violations.append(
                {
                    "record_id": record["record_id"],
                    "confidence": record.get("confidence"),
                }
            )

        record_routes = record.get("hemisphere_routes", {})
        record_direct_edge_ids = set(record.get("direct_edge_ids", []))
        record_coverage = record.get("route_coverage", {})
        registry_routes = route_lookup.get(record["record_id"], {})
        registry_edges = edge_lookup.get(record["record_id"], {})
        registry_coverage = coverage_lookup.get(record["record_id"])

        if set(record_routes) != set(ROUTE_SIDES):
            route_shape_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "hemisphere_routes_missing_sides",
                    "keys": sorted(record_routes.keys()),
                }
            )

        if len(record_direct_edge_ids) != 2:
            edge_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "direct_edge_id_count",
                    "direct_edge_ids": sorted(record_direct_edge_ids),
                }
            )

        if record_coverage.get("record_id") != record["record_id"]:
            coverage_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "record_embedded_coverage_missing",
                }
            )

        roles = set()
        for hemisphere in ROUTE_SIDES:
            route_packet = record_routes.get(hemisphere)
            registry_route = registry_routes.get(hemisphere)
            edge_payload = registry_edges.get(hemisphere)
            coverage = record_coverage.get(hemisphere) or {}

            if route_packet is None:
                route_shape_violations.append(
                    {
                        "record_id": record["record_id"],
                        "reason": "missing_route_packet",
                        "hemisphere": hemisphere,
                    }
                )
                continue

            if registry_route is None or registry_route.get("route_id") != route_packet.get("route_id"):
                route_registry_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "reason": "route_registry_mismatch",
                    }
                )

            missing_route_fields = [
                field for field in ROUTE_REQUIRED_FIELDS if field not in route_packet
            ]
            empty_route_fields = [
                field
                for field in ROUTE_REQUIRED_FIELDS
                if field in route_packet and not route_field_present(field, route_packet[field])
            ]
            if missing_route_fields or empty_route_fields:
                route_shape_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "missing_fields": missing_route_fields,
                        "empty_fields": empty_route_fields,
                    }
                )

            expected_role = expected_route_role(record, hemisphere)
            expected_mode = expected_route_mode(record, hemisphere)
            expected_hub = "HC-MATH" if hemisphere == "MATH" else "HC-MYTH"
            expected_gc_exchange = expected_exchange(hemisphere, expected_mode)
            roles.add(route_packet.get("route_role"))
            if (
                route_packet.get("hemisphere") != hemisphere
                or route_packet.get("route_role") != expected_role
                or route_packet.get("route_mode") != expected_mode
                or route_packet.get("hub_id") != expected_hub
                or route_packet.get("grand_central_exchange") != expected_gc_exchange
                or route_packet.get("family") != record.get("family")
                or route_packet.get("tract") != record.get("tract")
                or route_packet.get("basis_anchor_ids") != record.get("basis_anchor_ids")
            ):
                route_alignment_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "expected_role": expected_role,
                        "actual_role": route_packet.get("route_role"),
                        "expected_mode": expected_mode,
                        "actual_mode": route_packet.get("route_mode"),
                        "expected_exchange": expected_gc_exchange,
                        "actual_exchange": route_packet.get("grand_central_exchange"),
                    }
                )

            if route_packet.get("depth5") != "D0" or not all(
                route_packet.get(key) for key in ("addr4", "face6", "arc7", "rail3")
            ):
                route_shape_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "reason": "missing_holo_coordinate",
                    }
                )

            if set(route_packet.get("liminal_vector", {})) != EXPECTED_LIMINAL_KEYS:
                route_projection_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "reason": "liminal_vector_keys",
                        "keys": sorted(route_packet.get("liminal_vector", {}).keys()),
                    }
                )

            if set(route_packet.get("dynamic_weights", {})) != EXPECTED_DYNAMIC_WEIGHT_KEYS:
                route_projection_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "reason": "dynamic_weight_keys",
                        "keys": sorted(route_packet.get("dynamic_weights", {}).keys()),
                    }
                )

            continuity = route_packet.get("dynamic_weights", {}).get("continuity")
            expected_continuity = (
                1.0
                if route_packet.get("route_role") == "primary"
                else round(float(record.get("bridge_intensity", 0.0)), 3)
            )
            if continuity is None or abs(float(continuity) - expected_continuity) > 0.001:
                route_projection_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "reason": "continuity_mismatch",
                        "expected": expected_continuity,
                        "actual": continuity,
                    }
                )

            field_vector = route_packet.get("aether_point", {})
            expected_field = expected_field_id(field_vector)
            expected_zpoint = expected_zpoint_id(record, route_packet)
            expected_geodesic = expected_geodesic_mode(field_vector)
            expected_space = expected_preferred_space(route_packet)
            if (
                route_packet.get("field_id") != expected_field
                or route_packet.get("zpoint_id") != expected_zpoint
                or route_packet.get("geodesic_mode") != expected_geodesic
                or route_packet.get("preferred_space") != expected_space
                or route_packet.get("preferred_space") not in route_packet.get("supported_spaces", [])
            ):
                route_projection_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "field_id": route_packet.get("field_id"),
                        "expected_field_id": expected_field,
                        "zpoint_id": route_packet.get("zpoint_id"),
                        "expected_zpoint_id": expected_zpoint,
                        "geodesic_mode": route_packet.get("geodesic_mode"),
                        "expected_geodesic_mode": expected_geodesic,
                        "preferred_space": route_packet.get("preferred_space"),
                        "expected_preferred_space": expected_space,
                    }
                )

            unknown_interlocks = [
                interlock_id
                for interlock_id in route_packet.get("interlock_ids", [])
                if interlock_id not in live_interlocks
            ]
            if unknown_interlocks:
                interlock_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "unknown_interlocks": unknown_interlocks,
                    }
                )

            if route_packet.get("pt2_shortcut_id") not in live_pt2_shortcuts:
                shortcut_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "reason": "unknown_pt2_shortcut",
                        "shortcut_id": route_packet.get("pt2_shortcut_id"),
                    }
                )
            if route_packet.get("knowledge_fabric_shortcut_id") not in live_kf_shortcuts:
                shortcut_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "reason": "unknown_knowledge_fabric_shortcut",
                        "shortcut_id": route_packet.get("knowledge_fabric_shortcut_id"),
                    }
                )

            if edge_payload is None:
                edge_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "reason": "missing_direct_edge",
                    }
                )
            else:
                expected_weight = record["math_weight"] if hemisphere == "MATH" else record["myth_weight"]
                if (
                    edge_payload.get("edge_id") not in record_direct_edge_ids
                    or edge_payload.get("route_role") != expected_role
                    or edge_payload.get("route_mode") != expected_mode
                    or edge_payload.get("target_hub_id") != expected_hub
                    or abs(float(edge_payload.get("weight", 0.0)) - float(expected_weight)) > FLOAT_TOLERANCE
                    or edge_payload.get("grand_central_exchange") != expected_gc_exchange
                ):
                    edge_violations.append(
                        {
                            "record_id": record["record_id"],
                            "hemisphere": hemisphere,
                            "expected_weight": expected_weight,
                            "actual_weight": edge_payload.get("weight"),
                            "expected_role": expected_role,
                            "actual_role": edge_payload.get("route_role"),
                        }
                    )

            expected_coverage_keys = set(PRIMARY_HF_ROUTE_KEYS)
            if (
                not expected_coverage_keys.issubset(set(coverage))
                or not all(bool(coverage.get(key)) for key in expected_coverage_keys)
            ):
                coverage_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "coverage_keys": sorted(coverage.keys()),
                        "false_keys": [key for key in expected_coverage_keys if not coverage.get(key)],
                    }
                )

            if route_packet.get("docs_gate_status") != manifest.get("docs_gate_status"):
                route_alignment_violations.append(
                    {
                        "record_id": record["record_id"],
                        "hemisphere": hemisphere,
                        "reason": "docs_gate_route_mismatch",
                    }
                )

        if roles != {"primary", "secondary"}:
            route_alignment_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "route_roles_invalid",
                    "roles": sorted(roles),
                }
            )

        if registry_coverage is None or registry_coverage != record_coverage:
            coverage_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "coverage_registry_mismatch",
                }
            )

        if record_coverage.get("complete") is not True:
            coverage_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "coverage_incomplete",
                }
            )

        if not record.get("text_extractable"):
            for hemisphere in ROUTE_SIDES:
                packet = record_routes.get(hemisphere, {})
                if packet.get("proof_state") == "OK":
                    metadata_route_violations.append(
                        {
                            "record_id": record["record_id"],
                            "hemisphere": hemisphere,
                            "reason": "metadata_route_overclaimed",
                            "proof_state": packet.get("proof_state"),
                        }
                    )

        if not alias_has_record(
            navigator_alias_index,
            record["record_id"],
            record["record_id"],
            {"record_id"},
        ):
            navigator_alias_violations.append(
                {"record_id": record["record_id"], "reason": "missing_record_id_alias"}
            )
        if not alias_has_record(
            navigator_alias_index,
            record.get("title", ""),
            record["record_id"],
            {"title"},
        ):
            navigator_alias_violations.append(
                {"record_id": record["record_id"], "reason": "missing_title_alias"}
            )
        if not alias_has_record(
            navigator_alias_index,
            record.get("relative_path", ""),
            record["record_id"],
            {"relative_path"},
        ):
            navigator_alias_violations.append(
                {"record_id": record["record_id"], "reason": "missing_relative_path_alias"}
            )
        if record.get("duplicate_paths"):
            duplicate_alias = record["duplicate_paths"][0]
            if not alias_has_record(
                navigator_alias_index,
                duplicate_alias,
                record["record_id"],
                {"duplicate_path"},
            ):
                navigator_alias_violations.append(
                    {
                        "record_id": record["record_id"],
                        "reason": "missing_duplicate_alias",
                    }
                )

        neighbor_entry = navigator_neighbor_index.get("records", {}).get(record["record_id"])
        if neighbor_entry is None:
            navigator_neighbor_violations.append(
                {"record_id": record["record_id"], "reason": "missing_neighbor_entry"}
            )
        else:
            if neighbor_entry.get("entrypoint_summary", {}).get("first_anchor") != record["basis_anchor_ids"][0]:
                navigator_neighbor_violations.append(
                    {
                        "record_id": record["record_id"],
                        "reason": "neighbor_anchor_mismatch",
                    }
                )
            commissure_enabled = neighbor_entry.get("commissure_peers", {}).get("enabled")
            if (record.get("bridge_class") == "commissure_bridge") != bool(commissure_enabled):
                navigator_neighbor_violations.append(
                    {
                        "record_id": record["record_id"],
                        "reason": "commissure_neighbor_flag_mismatch",
                    }
                )

        for hemisphere in ROUTE_SIDES:
            route_packet = record_routes.get(hemisphere)
            if route_packet is None:
                continue
            ref = f"{record['record_id']}::{hemisphere}"
            facet_checks = {
                "hemisphere": hemisphere,
                "target_system": route_packet["target_system"],
                "origin_system": route_packet["origin_system"],
                "family": record["family"],
                "tract": route_packet["tract"],
                "route_role": route_packet["route_role"],
                "route_mode": route_packet["route_mode"],
                "field": route_packet["field_id"],
                "zpoint": route_packet["zpoint_id"],
                "projection_space": route_packet["preferred_space"],
                "proof_state": route_packet["proof_state"],
                "top_level": record["top_level"],
            }
            for facet_name, facet_value in facet_checks.items():
                refs = navigator_facet_index.get("facets", {}).get(facet_name, {}).get(facet_value, [])
                if ref not in refs:
                    navigator_facet_violations.append(
                        {
                            "record_id": record["record_id"],
                            "hemisphere": hemisphere,
                            "facet": facet_name,
                            "value": facet_value,
                        }
                    )
            anchor_refs = navigator_facet_index.get("facets", {}).get("anchor", {})
            for anchor_id in record.get("basis_anchor_ids", []):
                if ref not in anchor_refs.get(anchor_id, []):
                    navigator_facet_violations.append(
                        {
                            "record_id": record["record_id"],
                            "hemisphere": hemisphere,
                            "facet": "anchor",
                            "value": anchor_id,
                        }
                    )

    checks.append(
        run_check(
            "weight_normalization",
            not weight_violations,
            {"violations": weight_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "required_fields",
            not required_field_violations,
            {"violations": required_field_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "navigation_fields",
            not missing_navigation,
            {"missing_navigation": missing_navigation[:20]},
        )
    )

    commissure_edges = {edge["record_id"] for edge in commissure_registry.get("edges", [])}
    missing_edges = [
        record_id for record_id in bridge_records if record_id not in commissure_edges
    ]
    checks.append(
        run_check(
            "commissure_edges",
            not missing_edges,
            {
                "bridge_records": len(bridge_records),
                "missing_edges": missing_edges[:20],
            },
        )
    )
    checks.append(
        run_check(
            "metadata_only_confidence",
            not metadata_confidence_violations,
            {"violations": metadata_confidence_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "dual_route_shape",
            not route_shape_violations,
            {"violations": route_shape_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "dual_route_alignment",
            not route_alignment_violations,
            {"violations": route_alignment_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "route_registry_consistency",
            not route_registry_violations,
            {"violations": route_registry_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "direct_edges",
            not edge_violations,
            {"violations": edge_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "route_coverage",
            not coverage_violations,
            {"violations": coverage_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "route_projection_rules",
            not route_projection_violations,
            {"violations": route_projection_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "route_interlocks",
            not interlock_violations,
            {"violations": interlock_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "route_shortcuts",
            not shortcut_violations,
            {"violations": shortcut_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "metadata_only_dual_routes",
            not metadata_route_violations,
            {"violations": metadata_route_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "navigator_counts",
            navigator_alias_index.get("record_count") == len(records)
            and navigator_facet_index.get("record_count") == len(records)
            and navigator_facet_index.get("route_ref_count") == len(records) * 2
            and navigator_neighbor_index.get("record_count") == len(records)
            and navigator_manifest.get("counts", {}).get("records") == len(records),
            {
                "records": len(records),
                "alias_record_count": navigator_alias_index.get("record_count"),
                "facet_record_count": navigator_facet_index.get("record_count"),
                "facet_route_refs": navigator_facet_index.get("route_ref_count"),
                "neighbor_record_count": navigator_neighbor_index.get("record_count"),
                "manifest_record_count": navigator_manifest.get("counts", {}).get("records"),
            },
        )
    )
    checks.append(
        run_check(
            "navigator_alias_index",
            not navigator_alias_violations,
            {"violations": navigator_alias_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "navigator_facet_index",
            not navigator_facet_violations,
            {"violations": navigator_facet_violations[:20]},
        )
    )
    checks.append(
        run_check(
            "navigator_neighbor_index",
            not navigator_neighbor_violations,
            {"violations": navigator_neighbor_violations[:20]},
        )
    )

    expected_seed_counts = {
        "math": min(24, sum(1 for record in records if record.get("primary_hemisphere") == "MATH")),
        "myth": min(24, sum(1 for record in records if record.get("primary_hemisphere") == "MYTH")),
        "bridge": min(24, len(bridge_records)),
    }
    composer_seed_counts_ok = composer_manifest.get("counts", {}).get("seed_groups") == 3
    for group_name, expected_count in expected_seed_counts.items():
        entries = composer_seed_registry.get("groups", {}).get(group_name, [])
        if len(entries) != expected_count:
            composer_seed_counts_ok = False
            composer_seed_violations.append(
                {
                    "group": group_name,
                    "reason": "starter_count",
                    "expected": expected_count,
                    "actual": len(entries),
                }
            )
        for index, entry in enumerate(entries, start=1):
            route_bundle = entry.get("route_bundle", {})
            seed_record = route_bundle.get("seed_record", {}) or {}
            if entry.get("rank") != index or not composer_response_shape_ok(route_bundle):
                composer_seed_violations.append(
                    {
                        "group": group_name,
                        "reason": "route_bundle_shape",
                        "rank": entry.get("rank"),
                        "record_id": seed_record.get("record_id", ""),
                    }
                )
            if (
                group_name == "math" and seed_record.get("primary_hemisphere") != "MATH"
            ) or (
                group_name == "myth" and seed_record.get("primary_hemisphere") != "MYTH"
            ) or (
                group_name == "bridge"
                and route_bundle.get("bridge_profile", {}).get("mode") != "commissure_active"
            ):
                composer_seed_violations.append(
                    {
                        "group": group_name,
                        "reason": "seed_group_alignment",
                        "record_id": seed_record.get("record_id", ""),
                    }
                )
    checks.append(
        run_check(
            "composer_seed_registry",
            composer_seed_counts_ok and not composer_seed_violations,
            {
                "expected_counts": expected_seed_counts,
                "actual_counts": composer_seed_registry.get("counts", {}),
                "violations": composer_seed_violations[:20],
            },
        )
    )

    expected_facet_counts = {
        "anchor": navigator_facet_index.get("facet_cardinalities", {}).get("anchor", 0),
        "family": navigator_facet_index.get("facet_cardinalities", {}).get("family", 0),
        "target_system": navigator_facet_index.get("facet_cardinalities", {}).get("target_system", 0),
        "hemisphere": navigator_facet_index.get("facet_cardinalities", {}).get("hemisphere", 0),
    }
    composer_facet_counts_ok = composer_manifest.get("counts", {}).get("facet_starters") == sum(
        expected_facet_counts.values()
    )
    for facet_name, expected_count in expected_facet_counts.items():
        entries = composer_facet_registry.get("facets", {}).get(facet_name, {})
        if len(entries) != expected_count:
            composer_facet_counts_ok = False
            composer_facet_violations.append(
                {
                    "facet": facet_name,
                    "reason": "facet_count",
                    "expected": expected_count,
                    "actual": len(entries),
                }
            )
        for facet_value, entry in entries.items():
            route_bundle = entry.get("route_bundle", {})
            if not composer_response_shape_ok(route_bundle):
                composer_facet_violations.append(
                    {
                        "facet": facet_name,
                        "value": facet_value,
                        "reason": "route_bundle_shape",
                    }
                )
    checks.append(
        run_check(
            "composer_facet_registry",
            composer_facet_counts_ok and not composer_facet_violations,
            {
                "expected_counts": expected_facet_counts,
                "actual_counts": composer_facet_registry.get("facet_counts", {}),
                "violations": composer_facet_violations[:20],
            },
        )
    )

    synthesis_records = synthesis_evidence_registry.get("records", {})
    synthesis_evidence_ok = synthesis_evidence_registry.get("record_count") == len(records)
    for record in records:
        evidence_row = synthesis_records.get(record["record_id"])
        if evidence_row is None:
            synthesis_evidence_ok = False
            synthesis_evidence_violations.append(
                {"record_id": record["record_id"], "reason": "missing_evidence_row"}
            )
            continue
        required_keys = {
            "record_id",
            "title",
            "relative_path",
            "heading_candidates",
            "excerpt",
            "family",
            "basis_anchor_ids",
            "appendix_support",
        }
        if not required_keys.issubset(evidence_row):
            synthesis_evidence_ok = False
            synthesis_evidence_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "missing_fields",
                    "missing": sorted(required_keys - set(evidence_row)),
                }
            )
    checks.append(
        run_check(
            "synthesis_evidence_registry",
            synthesis_evidence_ok and not synthesis_evidence_violations,
            {
                "record_count": synthesis_evidence_registry.get("record_count"),
                "violations": synthesis_evidence_violations[:20],
            },
        )
    )

    synthesis_seed_counts_ok = synthesis_manifest.get("counts", {}).get("seed_groups") == 3
    for group_name, expected_count in expected_seed_counts.items():
        entries = synthesis_seed_registry.get("groups", {}).get(group_name, [])
        if len(entries) != expected_count:
            synthesis_seed_counts_ok = False
            synthesis_seed_violations.append(
                {
                    "group": group_name,
                    "reason": "starter_count",
                    "expected": expected_count,
                    "actual": len(entries),
                }
            )
        for index, entry in enumerate(entries, start=1):
            synthesis_bundle = entry.get("synthesis_bundle", {})
            seed_record = synthesis_bundle.get("seed_record", {}) or {}
            if entry.get("rank") != index or not synthesis_response_shape_ok(synthesis_bundle):
                synthesis_seed_violations.append(
                    {
                        "group": group_name,
                        "reason": "synthesis_bundle_shape",
                        "rank": entry.get("rank"),
                        "record_id": seed_record.get("record_id", ""),
                    }
                )
            if (
                group_name == "math" and seed_record.get("primary_hemisphere") != "MATH"
            ) or (
                group_name == "myth" and seed_record.get("primary_hemisphere") != "MYTH"
            ) or (
                group_name == "bridge"
                and seed_record.get("record_id") not in bridge_records
            ):
                synthesis_seed_violations.append(
                    {
                        "group": group_name,
                        "reason": "seed_group_alignment",
                        "record_id": seed_record.get("record_id", ""),
                    }
                )
    checks.append(
        run_check(
            "synthesis_seed_registry",
            synthesis_seed_counts_ok and not synthesis_seed_violations,
            {
                "expected_counts": expected_seed_counts,
                "actual_counts": synthesis_seed_registry.get("counts", {}),
                "violations": synthesis_seed_violations[:20],
            },
        )
    )

    synthesis_facet_counts_ok = synthesis_manifest.get("counts", {}).get("facet_starters") == sum(
        expected_facet_counts.values()
    )
    for facet_name, expected_count in expected_facet_counts.items():
        entries = synthesis_facet_registry.get("facets", {}).get(facet_name, {})
        if len(entries) != expected_count:
            synthesis_facet_counts_ok = False
            synthesis_facet_violations.append(
                {
                    "facet": facet_name,
                    "reason": "facet_count",
                    "expected": expected_count,
                    "actual": len(entries),
                }
            )
        for facet_value, entry in entries.items():
            synthesis_bundle = entry.get("synthesis_bundle", {})
            if not synthesis_response_shape_ok(synthesis_bundle):
                synthesis_facet_violations.append(
                    {
                        "facet": facet_name,
                        "value": facet_value,
                        "reason": "synthesis_bundle_shape",
                    }
                )
    checks.append(
        run_check(
            "synthesis_facet_registry",
            synthesis_facet_counts_ok and not synthesis_facet_violations,
            {
                "expected_counts": expected_facet_counts,
                "actual_counts": synthesis_facet_registry.get("facet_counts", {}),
                "violations": synthesis_facet_violations[:20],
            },
        )
    )

    atlas_nodes = visual_atlas_node_registry.get("nodes", [])
    atlas_node_counts = Counter(node.get("node_type", "") for node in atlas_nodes)
    expected_node_counts = {
        "hub": 3,
        "hemisphere": 2,
        "family": len({record.get("family", "") for record in records}),
        "target_system": len(
            {
                route_lookup[record["record_id"]][hemisphere].get("target_system", "")
                for record in records
                for hemisphere in ROUTE_SIDES
            }
            - {""}
        ),
        "anchor": len({anchor for record in records for anchor in record.get("basis_anchor_ids", [])}),
        "record": len(records),
    }
    if visual_atlas_node_registry.get("node_count") != len(atlas_nodes):
        visual_atlas_node_violations.append(
            {
                "reason": "node_count",
                "declared": visual_atlas_node_registry.get("node_count"),
                "actual": len(atlas_nodes),
            }
        )
    for node_type, expected_count in expected_node_counts.items():
        if atlas_node_counts.get(node_type, 0) != expected_count:
            visual_atlas_node_violations.append(
                {
                    "reason": "node_type_count",
                    "node_type": node_type,
                    "expected": expected_count,
                    "actual": atlas_node_counts.get(node_type, 0),
                }
            )
    checks.append(
        run_check(
            "visual_atlas_node_registry",
            not visual_atlas_node_violations,
            {
                "expected_counts": expected_node_counts,
                "actual_counts": dict(sorted(atlas_node_counts.items())),
                "violations": visual_atlas_node_violations[:20],
            },
        )
    )

    atlas_edges = visual_atlas_edge_registry.get("edges", [])
    for record in records:
        record_edges = atlas_edge_lookup.get(record["record_id"], {})
        if len(record_edges.get("record_to_hub", [])) != 2:
            visual_atlas_edge_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "record_to_hub_count",
                    "actual": len(record_edges.get("record_to_hub", [])),
                }
            )
        if len(record_edges.get("record_to_unified_hub", [])) != 1:
            visual_atlas_edge_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "record_to_unified_hub_count",
                    "actual": len(record_edges.get("record_to_unified_hub", [])),
                }
            )
        if len(record_edges.get("record_to_family", [])) != 1:
            visual_atlas_edge_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "record_to_family_count",
                    "actual": len(record_edges.get("record_to_family", [])),
                }
            )
        if not record_edges.get("record_to_target_system"):
            visual_atlas_edge_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "missing_target_system_edge",
                }
            )
        if not record_edges.get("record_to_anchor"):
            visual_atlas_edge_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "missing_anchor_edge",
                }
            )
    spine_edge_ids = {
        edge.get("edge_id", "")
        for edge in atlas_edges
        if edge.get("edge_type") == "hub_spine"
    }
    if {
        "VA-SPINE-HC-MATH-GC0",
        "VA-SPINE-GC0-HC-MATH",
        "VA-SPINE-HC-MYTH-GC0",
        "VA-SPINE-GC0-HC-MYTH",
    } - spine_edge_ids:
        visual_atlas_edge_violations.append(
            {
                "reason": "missing_hub_spine_edges",
                "missing": sorted(
                    {
                        "VA-SPINE-HC-MATH-GC0",
                        "VA-SPINE-GC0-HC-MATH",
                        "VA-SPINE-HC-MYTH-GC0",
                        "VA-SPINE-GC0-HC-MYTH",
                    }
                    - spine_edge_ids
                ),
            }
        )
    checks.append(
        run_check(
            "visual_atlas_edge_registry",
            not visual_atlas_edge_violations,
            {
                "edge_count": visual_atlas_edge_registry.get("edge_count"),
                "edge_type_counts": visual_atlas_edge_registry.get("edge_counts", {}),
                "violations": visual_atlas_edge_violations[:20],
            },
        )
    )

    atlas_pages = visual_atlas_page_registry.get("pages", [])
    atlas_page_counts = Counter(page.get("page_type", "") for page in atlas_pages)
    page_lookup = {page.get("page_id", ""): page for page in atlas_pages}
    expected_page_counts = {
        "main_index": 1,
        "overview": 1,
        "hemisphere": 2,
        "anchor_index": 1,
        "target_system_index": 1,
        "record_locator_index": 1,
        "coverage": 1,
        "family_shard": expected_facet_counts["family"],
        "anchor_shard": expected_facet_counts["anchor"],
        "target_system_shard": expected_facet_counts["target_system"],
        "record_locator_shard": navigator_facet_index.get("facet_cardinalities", {}).get("top_level", 0),
    }
    if visual_atlas_page_registry.get("page_count") != len(atlas_pages):
        visual_atlas_page_violations.append(
            {
                "reason": "page_count",
                "declared": visual_atlas_page_registry.get("page_count"),
                "actual": len(atlas_pages),
            }
        )
    for page_type, expected_count in expected_page_counts.items():
        if atlas_page_counts.get(page_type, 0) != expected_count:
            visual_atlas_page_violations.append(
                {
                    "reason": "page_type_count",
                    "page_type": page_type,
                    "expected": expected_count,
                    "actual": atlas_page_counts.get(page_type, 0),
                }
            )
    for page in atlas_pages:
        if not page_exists(page):
            visual_atlas_page_violations.append(
                {
                    "reason": "missing_page_file",
                    "page_id": page.get("page_id", ""),
                }
            )
    checks.append(
        run_check(
            "visual_atlas_page_registry",
            not visual_atlas_page_violations,
            {
                "expected_counts": expected_page_counts,
                "actual_counts": dict(sorted(atlas_page_counts.items())),
                "violations": visual_atlas_page_violations[:20],
            },
        )
    )

    locator_records = visual_atlas_record_locator_registry.get("records", {})
    if visual_atlas_record_locator_registry.get("record_count") != len(locator_records):
        visual_atlas_locator_violations.append(
            {
                "reason": "locator_count",
                "declared": visual_atlas_record_locator_registry.get("record_count"),
                "actual": len(locator_records),
            }
        )
    for record in records:
        locator_entry = locator_records.get(record["record_id"])
        if locator_entry is None:
            visual_atlas_locator_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "missing_locator_entry",
                }
            )
            continue
        expected_primary_page = "VA-HEM-MATH" if record.get("primary_hemisphere") == "MATH" else "VA-HEM-MYTH"
        expected_secondary_page = "VA-HEM-MYTH" if expected_primary_page == "VA-HEM-MATH" else "VA-HEM-MATH"
        target_system_page_ids = locator_entry.get("target_system_page_ids", [])
        missing_page_ids = [
            page_id
            for page_id in [
                locator_entry.get("primary_hemisphere_page_id"),
                locator_entry.get("secondary_hemisphere_page_id"),
                locator_entry.get("overview_page_id"),
                locator_entry.get("family_page_id"),
                locator_entry.get("anchor_page_id"),
                locator_entry.get("record_locator_page_id"),
                *target_system_page_ids,
            ]
            if page_id and page_id not in page_lookup
        ]
        if missing_page_ids:
            visual_atlas_locator_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "missing_page_ids",
                    "missing_page_ids": missing_page_ids,
                }
            )
        if locator_entry.get("primary_hemisphere_page_id") != expected_primary_page:
            visual_atlas_locator_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "primary_page_alignment",
                    "expected": expected_primary_page,
                    "actual": locator_entry.get("primary_hemisphere_page_id"),
                }
            )
        if locator_entry.get("secondary_hemisphere_page_id") != expected_secondary_page:
            visual_atlas_locator_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "secondary_page_alignment",
                    "expected": expected_secondary_page,
                    "actual": locator_entry.get("secondary_hemisphere_page_id"),
                }
            )
        if locator_entry.get("overview_page_id") != "VA-OVERVIEW":
            visual_atlas_locator_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "overview_page_alignment",
                    "actual": locator_entry.get("overview_page_id"),
                }
            )
        if len(locator_entry.get("overview_edge_ids", [])) != 3:
            visual_atlas_locator_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "overview_edge_count",
                    "actual": len(locator_entry.get("overview_edge_ids", [])),
                }
            )
        if not locator_entry.get("composer_seed_id") or not locator_entry.get("synthesis_seed_id"):
            visual_atlas_locator_violations.append(
                {
                    "record_id": record["record_id"],
                    "reason": "missing_seed_ids",
                }
            )
    checks.append(
        run_check(
            "visual_atlas_record_locator_registry",
            not visual_atlas_locator_violations,
            {
                "record_count": visual_atlas_record_locator_registry.get("record_count"),
                "violations": visual_atlas_locator_violations[:20],
            },
        )
    )
    visual_atlas_manifest_ok = (
        visual_atlas_manifest.get("counts", {}).get("node_count") == visual_atlas_node_registry.get("node_count")
        and visual_atlas_manifest.get("counts", {}).get("edge_count") == visual_atlas_edge_registry.get("edge_count")
        and visual_atlas_manifest.get("counts", {}).get("page_count") == visual_atlas_page_registry.get("page_count")
        and visual_atlas_manifest.get("counts", {}).get("record_locator_rows")
        == visual_atlas_record_locator_registry.get("record_count")
    )
    checks.append(
        run_check(
            "visual_atlas_manifest",
            visual_atlas_manifest_ok,
            {
                "manifest_counts": visual_atlas_manifest.get("counts", {}),
                "node_count": visual_atlas_node_registry.get("node_count"),
                "edge_count": visual_atlas_edge_registry.get("edge_count"),
                "page_count": visual_atlas_page_registry.get("page_count"),
                "locator_count": visual_atlas_record_locator_registry.get("record_count"),
            },
        )
    )

    expected_guided_seed_counts = {
        "main_pages": 8,
        "family": expected_facet_counts["family"],
        "anchor": expected_facet_counts["anchor"],
        "target_system": expected_facet_counts["target_system"],
        "hemisphere": 2,
    }
    guided_tour_seed_violations = []
    actual_guided_seed_counts = guided_tour_seed_registry.get("counts", {})
    for group_name, expected_count in expected_guided_seed_counts.items():
        if actual_guided_seed_counts.get(group_name, 0) != expected_count:
            guided_tour_seed_violations.append(
                {
                    "reason": "group_count",
                    "group": group_name,
                    "expected": expected_count,
                    "actual": actual_guided_seed_counts.get(group_name, 0),
                }
            )
        for entry in guided_tour_seed_registry.get("groups", {}).get(group_name, []):
            tour_bundle = entry.get("guided_tour", {})
            if not guided_tour_response_shape_ok(tour_bundle, page_lookup):
                guided_tour_seed_violations.append(
                    {
                        "reason": "starter_shape",
                        "group": group_name,
                        "page_id": entry.get("page_id", ""),
                    }
                )
            if tour_bundle.get("source_page", {}).get("page_id") != entry.get("page_id"):
                guided_tour_seed_violations.append(
                    {
                        "reason": "starter_source_page",
                        "group": group_name,
                        "page_id": entry.get("page_id", ""),
                        "actual": tour_bundle.get("source_page", {}).get("page_id"),
                    }
                )
    checks.append(
        run_check(
            "guided_tour_seed_registry",
            not guided_tour_seed_violations,
            {
                "expected_counts": expected_guided_seed_counts,
                "actual_counts": actual_guided_seed_counts,
                "violations": guided_tour_seed_violations[:20],
            },
        )
    )

    expected_guided_page_ids = {
        page.get("page_id", "")
        for page in atlas_pages
        if page.get("page_type") in {
            "main_index",
            "overview",
            "hemisphere",
            "anchor_index",
            "target_system_index",
            "record_locator_index",
            "coverage",
            "family_shard",
            "anchor_shard",
            "target_system_shard",
        }
    }
    guided_tour_page_entries = guided_tour_page_registry.get("pages", [])
    actual_guided_page_ids = {entry.get("page_id", "") for entry in guided_tour_page_entries}
    guided_tour_page_violations = []
    if guided_tour_page_registry.get("page_count") != len(guided_tour_page_entries):
        guided_tour_page_violations.append(
            {
                "reason": "page_count",
                "declared": guided_tour_page_registry.get("page_count"),
                "actual": len(guided_tour_page_entries),
            }
        )
    if actual_guided_page_ids != expected_guided_page_ids:
        guided_tour_page_violations.append(
            {
                "reason": "page_id_coverage",
                "missing": sorted(expected_guided_page_ids - actual_guided_page_ids),
                "extra": sorted(actual_guided_page_ids - expected_guided_page_ids),
            }
        )
    for entry in guided_tour_page_entries:
        if not guided_tour_response_shape_ok(entry.get("guided_tour", {}), page_lookup):
            guided_tour_page_violations.append(
                {
                    "reason": "page_registry_shape",
                    "page_id": entry.get("page_id", ""),
                }
            )
    checks.append(
        run_check(
            "guided_tour_page_registry",
            not guided_tour_page_violations,
            {
                "page_count": guided_tour_page_registry.get("page_count"),
                "violations": guided_tour_page_violations[:20],
            },
        )
    )

    guided_tour_manifest_ok = (
        guided_tour_manifest.get("counts", {}).get("seed_starters")
        == sum(actual_guided_seed_counts.values())
        and guided_tour_manifest.get("counts", {}).get("page_starters")
        == guided_tour_page_registry.get("page_count")
        and guided_tour_manifest.get("counts", {}).get("group_counts") == actual_guided_seed_counts
        and guided_tour_manifest.get("tour_stage_order") == GUIDED_TOUR_STAGE_ORDER
    )
    checks.append(
        run_check(
            "guided_tour_manifest",
            guided_tour_manifest_ok,
            {
                "manifest_counts": guided_tour_manifest.get("counts", {}),
                "seed_counts": actual_guided_seed_counts,
                "page_count": guided_tour_page_registry.get("page_count"),
                "tour_stage_order": guided_tour_manifest.get("tour_stage_order", []),
            },
        )
    )

    fixture_failures = []
    for suffix, expected in FIXTURE_EXPECTATIONS.items():
        fixture_record = record_lookup(records, suffix)
        if fixture_record is None:
            fixture_failures.append({"fixture": suffix, "reason": "missing"})
            continue
        if fixture_record["primary_hemisphere"] != expected:
            fixture_failures.append(
                {
                    "fixture": suffix,
                    "expected": expected,
                    "actual": fixture_record["primary_hemisphere"],
                }
            )

    bridge_fixture = next(
        (record for record in records if record.get("bridge_class") == "commissure_bridge"),
        None,
    )
    if bridge_fixture is None:
        fixture_failures.append({"fixture": "bridge_document", "reason": "missing"})
    elif bridge_fixture.get("route_coverage", {}).get("complete") is not True:
        fixture_failures.append(
            {
                "fixture": "bridge_document",
                "record_id": bridge_fixture["record_id"],
                "reason": "coverage_incomplete",
            }
        )

    metadata_fixture = next(
        (record for record in records if not record.get("text_extractable")),
        None,
    )
    if metadata_fixture is None:
        fixture_failures.append({"fixture": "metadata_witness", "reason": "missing"})
    elif metadata_fixture.get("confidence", 1.0) > 0.65:
        fixture_failures.append(
            {
                "fixture": "metadata_witness",
                "record_id": metadata_fixture["record_id"],
                "reason": "confidence_too_high",
                "confidence": metadata_fixture.get("confidence"),
            }
        )

    checks.append(
        run_check(
            "fixture_classification",
            not fixture_failures,
            {"fixture_failures": fixture_failures},
        )
    )

    navigator_query_failures = []
    navigator_registries = load_navigator_registries()
    unique_title_counts: dict[str, int] = {}
    for record in records:
        title_norm = navigator_normalize(record.get("title", ""))
        if title_norm:
            unique_title_counts[title_norm] = unique_title_counts.get(title_norm, 0) + 1

    math_fixture = record_lookup(
        records,
        "deeper crystalization/active_nervous_system/02_corpus_capsules/05_aqm_text_book.md",
    )
    myth_fixture = record_lookup(
        records,
        "deeper crystalization/active_nervous_system/02_corpus_capsules/73_andean_myth_encoding.md",
    )
    duplicate_fixture = next((record for record in records if record.get("duplicate_paths")), None)

    if math_fixture is not None:
        record_by_id = navigator_record_query(
            navigator_registries,
            record_id=math_fixture["record_id"],
        )
        if record_by_id.get("best_match", {}).get("record_id") != math_fixture["record_id"]:
            navigator_query_failures.append({"reason": "record_id_lookup", "record_id": math_fixture["record_id"]})

        record_by_path = navigator_record_query(
            navigator_registries,
            path=math_fixture["relative_path"],
        )
        if record_by_path.get("best_match", {}).get("record_id") != math_fixture["record_id"]:
            navigator_query_failures.append({"reason": "path_lookup", "record_id": math_fixture["record_id"]})

        if unique_title_counts.get(navigator_normalize(math_fixture.get("title", ""))) == 1:
            record_by_title = navigator_record_query(
                navigator_registries,
                title=math_fixture["title"],
            )
            if record_by_title.get("best_match", {}).get("record_id") != math_fixture["record_id"]:
                navigator_query_failures.append({"reason": "title_lookup", "record_id": math_fixture["record_id"]})

        focused_search = navigator_search_query(
            math_fixture["title"],
            navigator_registries,
            filters={
                "hemisphere": math_fixture["primary_hemisphere"],
                "system": math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["target_system"],
                "family": math_fixture["family"],
                "anchor": math_fixture["basis_anchor_ids"][0],
            },
        )
        if not response_has_record(focused_search, math_fixture["record_id"]):
            navigator_query_failures.append({"reason": "mixed_filter_search", "record_id": math_fixture["record_id"]})
        if (
            "MATH" not in focused_search.get("routes", {})
            or "MYTH" not in focused_search.get("routes", {})
            or len(focused_search.get("reverse_neighborhood", {}).get("same_anchor", {}).get("records", [])) > 3
        ):
            navigator_query_failures.append({"reason": "focused_shape", "record_id": math_fixture["record_id"]})

        expanded_search = navigator_search_query(
            math_fixture["title"],
            navigator_registries,
            filters={"family": math_fixture["family"]},
            expanded=True,
        )
        full_bundle_search = navigator_search_query(
            math_fixture["title"],
            navigator_registries,
            filters={"family": math_fixture["family"]},
            full_bundle=True,
        )
        if (
            not response_has_record(expanded_search, math_fixture["record_id"])
            or not response_has_record(full_bundle_search, math_fixture["record_id"])
            or "matched_facet_buckets" not in full_bundle_search
        ):
            navigator_query_failures.append({"reason": "expanded_full_bundle", "record_id": math_fixture["record_id"]})

        facet_queries = [
            ("target_system", math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["target_system"]),
            ("family", math_fixture["family"]),
            ("anchor", math_fixture["basis_anchor_ids"][0]),
            ("lens", math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["dominant_lens_system"]),
            ("field", math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["field_id"]),
            ("zpoint", math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["zpoint_id"]),
            ("projection_space", math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["preferred_space"]),
        ]
        for facet_name, facet_value in facet_queries:
            facet_result = navigator_facet_query(
                navigator_registries,
                facet_name=facet_name,
                facet_value=facet_value,
            )
            if facet_result.get("candidate_count", 0) <= 0 or facet_result.get("best_match") is None:
                navigator_query_failures.append(
                    {"reason": "facet_query", "facet": facet_name, "value": facet_value}
                )

    if duplicate_fixture is not None:
        duplicate_result = navigator_record_query(
            navigator_registries,
            path=duplicate_fixture["duplicate_paths"][0],
        )
        if duplicate_result.get("best_match", {}).get("record_id") != duplicate_fixture["record_id"]:
            navigator_query_failures.append({"reason": "duplicate_alias_lookup", "record_id": duplicate_fixture["record_id"]})

    if bridge_fixture is not None:
        bridge_query = navigator_record_query(
            navigator_registries,
            record_id=bridge_fixture["record_id"],
        )
        if not bridge_query.get("reverse_neighborhood", {}).get("commissure_peers", {}).get("enabled"):
            navigator_query_failures.append({"reason": "bridge_commissure_peers", "record_id": bridge_fixture["record_id"]})

    non_bridge_fixture = next(
        (record for record in records if record.get("bridge_class") != "commissure_bridge"),
        None,
    )
    if non_bridge_fixture is not None:
        non_bridge_query = navigator_record_query(
            navigator_registries,
            record_id=non_bridge_fixture["record_id"],
        )
        if non_bridge_query.get("reverse_neighborhood", {}).get("commissure_peers", {}).get("enabled"):
            navigator_query_failures.append({"reason": "non_bridge_commissure_flag", "record_id": non_bridge_fixture["record_id"]})

    if metadata_fixture is not None:
        metadata_query = navigator_record_query(
            navigator_registries,
            record_id=metadata_fixture["record_id"],
        )
        if metadata_query.get("best_match", {}).get("record_id") != metadata_fixture["record_id"]:
            navigator_query_failures.append({"reason": "metadata_lookup", "record_id": metadata_fixture["record_id"]})
        route_packets = metadata_query.get("routes", {})
        if any(route_packets.get(side, {}).get("proof_state") == "OK" for side in ROUTE_SIDES):
            navigator_query_failures.append({"reason": "metadata_proof_overclaim", "record_id": metadata_fixture["record_id"]})

    checks.append(
        run_check(
            "navigator_queries",
            not navigator_query_failures,
            {"violations": navigator_query_failures[:20]},
        )
    )

    composer_query_failures = []
    composer_registries = load_route_composer_registries()
    if math_fixture is not None:
        composer_record_by_id = composer_record_query(
            composer_registries,
            record_id=math_fixture["record_id"],
        )
        if (
            composer_record_by_id.get("seed_record", {}).get("record_id") != math_fixture["record_id"]
            or not composer_response_shape_ok(composer_record_by_id)
        ):
            composer_query_failures.append(
                {"reason": "composer_record_id_lookup", "record_id": math_fixture["record_id"]}
            )

        composer_record_by_path = composer_record_query(
            composer_registries,
            path=math_fixture["relative_path"],
        )
        if composer_record_by_path.get("seed_record", {}).get("record_id") != math_fixture["record_id"]:
            composer_query_failures.append(
                {"reason": "composer_path_lookup", "record_id": math_fixture["record_id"]}
            )

        if unique_title_counts.get(navigator_normalize(math_fixture.get("title", ""))) == 1:
            composer_record_by_title = composer_record_query(
                composer_registries,
                title=math_fixture["title"],
            )
            if composer_record_by_title.get("seed_record", {}).get("record_id") != math_fixture["record_id"]:
                composer_query_failures.append(
                    {"reason": "composer_title_lookup", "record_id": math_fixture["record_id"]}
                )

        navigator_search_result = navigator_search_query(
            math_fixture["title"],
            composer_registries,
            filters={
                "hemisphere": math_fixture["primary_hemisphere"],
                "system": math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["target_system"],
                "family": math_fixture["family"],
                "anchor": math_fixture["basis_anchor_ids"][0],
            },
        )
        composer_search_result = composer_search_query(
            math_fixture["title"],
            composer_registries,
            filters={
                "hemisphere": math_fixture["primary_hemisphere"],
                "system": math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["target_system"],
                "family": math_fixture["family"],
                "anchor": math_fixture["basis_anchor_ids"][0],
            },
            expanded=True,
        )
        if (
            composer_search_result.get("seed_record", {}).get("record_id")
            != navigator_search_result.get("best_match", {}).get("record_id")
            or not composer_response_shape_ok(composer_search_result)
            or len(composer_search_result.get("alternative_seeds", [])) > 3
        ):
            composer_query_failures.append(
                {"reason": "composer_search_alignment", "record_id": math_fixture["record_id"]}
            )

        navigator_facet_result = navigator_facet_query(
            composer_registries,
            facet_name="family",
            facet_value=math_fixture["family"],
        )
        composer_facet_result = composer_facet_query(
            composer_registries,
            facet_name="family",
            facet_value=math_fixture["family"],
        )
        if (
            composer_facet_result.get("seed_record", {}).get("record_id")
            != navigator_facet_result.get("best_match", {}).get("record_id")
            or not composer_response_shape_ok(composer_facet_result)
        ):
            composer_query_failures.append(
                {"reason": "composer_facet_alignment", "facet": "family", "value": math_fixture["family"]}
            )

        composer_record_repeat = composer_record_query(
            composer_registries,
            record_id=math_fixture["record_id"],
        )
        if composer_record_repeat != composer_record_by_id:
            composer_query_failures.append(
                {"reason": "composer_repeat_stability", "record_id": math_fixture["record_id"]}
            )

    if bridge_fixture is not None:
        composer_bridge = composer_record_query(
            composer_registries,
            record_id=bridge_fixture["record_id"],
        )
        if composer_bridge.get("bridge_profile", {}).get("mode") != "commissure_active":
            composer_query_failures.append(
                {"reason": "composer_bridge_mode", "record_id": bridge_fixture["record_id"]}
            )

    if non_bridge_fixture is not None:
        composer_non_bridge = composer_record_query(
            composer_registries,
            record_id=non_bridge_fixture["record_id"],
        )
        if composer_non_bridge.get("bridge_profile", {}).get("mode") != "hub_transfer":
            composer_query_failures.append(
                {"reason": "composer_non_bridge_mode", "record_id": non_bridge_fixture["record_id"]}
            )

    if metadata_fixture is not None:
        composer_metadata = composer_record_query(
            composer_registries,
            record_id=metadata_fixture["record_id"],
        )
        if (
            composer_metadata.get("seed_record", {}).get("record_id") != metadata_fixture["record_id"]
            or not composer_response_shape_ok(composer_metadata)
        ):
            composer_query_failures.append(
                {"reason": "composer_metadata_lookup", "record_id": metadata_fixture["record_id"]}
            )

    checks.append(
        run_check(
            "composer_queries",
            not composer_query_failures,
            {"violations": composer_query_failures[:20]},
        )
    )

    synthesis_query_failures = []
    synthesis_registries = load_synthesis_registries()
    if math_fixture is not None:
        composer_record_response = composer_record_query(
            synthesis_registries,
            record_id=math_fixture["record_id"],
        )
        synthesis_record_by_id = synthesis_record_query(
            synthesis_registries,
            record_id=math_fixture["record_id"],
        )
        if (
            synthesis_record_by_id.get("seed_record", {}).get("record_id") != composer_record_response.get("seed_record", {}).get("record_id")
            or not synthesis_response_shape_ok(synthesis_record_by_id)
        ):
            synthesis_query_failures.append(
                {"reason": "synthesis_record_id_lookup", "record_id": math_fixture["record_id"]}
            )

        synthesis_record_by_path = synthesis_record_query(
            synthesis_registries,
            path=math_fixture["relative_path"],
        )
        if synthesis_record_by_path.get("seed_record", {}).get("record_id") != math_fixture["record_id"]:
            synthesis_query_failures.append(
                {"reason": "synthesis_path_lookup", "record_id": math_fixture["record_id"]}
            )

        if unique_title_counts.get(navigator_normalize(math_fixture.get("title", ""))) == 1:
            synthesis_record_by_title = synthesis_record_query(
                synthesis_registries,
                title=math_fixture["title"],
            )
            if synthesis_record_by_title.get("seed_record", {}).get("record_id") != math_fixture["record_id"]:
                synthesis_query_failures.append(
                    {"reason": "synthesis_title_lookup", "record_id": math_fixture["record_id"]}
                )

        composer_search_response = composer_search_query(
            math_fixture["title"],
            synthesis_registries,
            filters={
                "hemisphere": math_fixture["primary_hemisphere"],
                "system": math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["target_system"],
                "family": math_fixture["family"],
                "anchor": math_fixture["basis_anchor_ids"][0],
            },
            expanded=True,
        )
        synthesis_search_response = synthesis_search_query(
            math_fixture["title"],
            synthesis_registries,
            filters={
                "hemisphere": math_fixture["primary_hemisphere"],
                "system": math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["target_system"],
                "family": math_fixture["family"],
                "anchor": math_fixture["basis_anchor_ids"][0],
            },
            expanded=True,
        )
        if (
            synthesis_search_response.get("seed_record", {}).get("record_id")
            != composer_search_response.get("seed_record", {}).get("record_id")
            or not synthesis_response_shape_ok(synthesis_search_response)
            or len(synthesis_search_response.get("alternative_seeds", [])) > 3
        ):
            synthesis_query_failures.append(
                {"reason": "synthesis_search_alignment", "record_id": math_fixture["record_id"]}
            )

        composer_facet_response = composer_facet_query(
            synthesis_registries,
            facet_name="family",
            facet_value=math_fixture["family"],
        )
        synthesis_facet_response = synthesis_facet_query(
            synthesis_registries,
            facet_name="family",
            facet_value=math_fixture["family"],
        )
        if (
            synthesis_facet_response.get("seed_record", {}).get("record_id")
            != composer_facet_response.get("seed_record", {}).get("record_id")
            or not synthesis_response_shape_ok(synthesis_facet_response)
        ):
            synthesis_query_failures.append(
                {"reason": "synthesis_facet_alignment", "facet": "family", "value": math_fixture["family"]}
            )

        synthesis_record_repeat = synthesis_record_query(
            synthesis_registries,
            record_id=math_fixture["record_id"],
        )
        if synthesis_record_repeat != synthesis_record_by_id:
            synthesis_query_failures.append(
                {"reason": "synthesis_repeat_stability", "record_id": math_fixture["record_id"]}
            )

    if bridge_fixture is not None:
        synthesis_bridge = synthesis_record_query(
            synthesis_registries,
            record_id=bridge_fixture["record_id"],
        )
        bridge_text = " ".join(
            bullet.get("text", "")
            for bullet in synthesis_bridge.get("bridge_interpretation", {}).get("bullets", [])
        ).lower()
        if "commissure" not in bridge_text:
            synthesis_query_failures.append(
                {"reason": "synthesis_bridge_mode", "record_id": bridge_fixture["record_id"]}
            )

    if non_bridge_fixture is not None:
        synthesis_non_bridge = synthesis_record_query(
            synthesis_registries,
            record_id=non_bridge_fixture["record_id"],
        )
        bridge_text = " ".join(
            bullet.get("text", "")
            for bullet in synthesis_non_bridge.get("bridge_interpretation", {}).get("bullets", [])
        ).lower()
        if "hub transfer" not in bridge_text:
            synthesis_query_failures.append(
                {"reason": "synthesis_non_bridge_mode", "record_id": non_bridge_fixture["record_id"]}
            )

    if metadata_fixture is not None:
        synthesis_metadata = synthesis_record_query(
            synthesis_registries,
            record_id=metadata_fixture["record_id"],
        )
        if (
            synthesis_metadata.get("seed_record", {}).get("record_id") != metadata_fixture["record_id"]
            or not synthesis_response_shape_ok(synthesis_metadata)
        ):
            synthesis_query_failures.append(
                {"reason": "synthesis_metadata_lookup", "record_id": metadata_fixture["record_id"]}
            )

    checks.append(
        run_check(
            "synthesis_queries",
            not synthesis_query_failures,
            {"violations": synthesis_query_failures[:20]},
        )
    )

    guided_tour_query_failures = []
    guided_tour_registries = load_guided_tour_registries()
    if math_fixture is not None:
        guided_record_by_id = guided_tour_record_query(
            guided_tour_registries,
            record_id=math_fixture["record_id"],
        )
        if (
            guided_record_by_id.get("seed_record", {}).get("record_id") != math_fixture["record_id"]
            or not guided_tour_response_shape_ok(guided_record_by_id, page_lookup)
        ):
            guided_tour_query_failures.append(
                {"reason": "guided_record_id_lookup", "record_id": math_fixture["record_id"]}
            )

        guided_record_by_path = guided_tour_record_query(
            guided_tour_registries,
            path=math_fixture["relative_path"],
        )
        if guided_record_by_path.get("seed_record", {}).get("record_id") != math_fixture["record_id"]:
            guided_tour_query_failures.append(
                {"reason": "guided_path_lookup", "record_id": math_fixture["record_id"]}
            )

        if unique_title_counts.get(navigator_normalize(math_fixture.get("title", ""))) == 1:
            guided_record_by_title = guided_tour_record_query(
                guided_tour_registries,
                title=math_fixture["title"],
            )
            if guided_record_by_title.get("seed_record", {}).get("record_id") != math_fixture["record_id"]:
                guided_tour_query_failures.append(
                    {"reason": "guided_title_lookup", "record_id": math_fixture["record_id"]}
                )

        guided_search_response = guided_tour_search_query(
            math_fixture["title"],
            guided_tour_registries,
            filters={
                "hemisphere": math_fixture["primary_hemisphere"],
                "system": math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["target_system"],
                "family": math_fixture["family"],
                "anchor": math_fixture["basis_anchor_ids"][0],
            },
            expanded=True,
        )
        composer_search_response = composer_search_query(
            math_fixture["title"],
            guided_tour_registries,
            filters={
                "hemisphere": math_fixture["primary_hemisphere"],
                "system": math_fixture["hemisphere_routes"][math_fixture["primary_hemisphere"]]["target_system"],
                "family": math_fixture["family"],
                "anchor": math_fixture["basis_anchor_ids"][0],
            },
            expanded=True,
        )
        if (
            guided_search_response.get("seed_record", {}).get("record_id")
            != composer_search_response.get("seed_record", {}).get("record_id")
            or not guided_tour_response_shape_ok(guided_search_response, page_lookup)
            or len(guided_search_response.get("alternative_seeds", [])) > 3
        ):
            guided_tour_query_failures.append(
                {"reason": "guided_search_alignment", "record_id": math_fixture["record_id"]}
            )

        guided_facet_response = guided_tour_facet_query(
            guided_tour_registries,
            facet_name="family",
            facet_value=math_fixture["family"],
        )
        composer_facet_response = composer_facet_query(
            guided_tour_registries,
            facet_name="family",
            facet_value=math_fixture["family"],
        )
        if (
            guided_facet_response.get("seed_record", {}).get("record_id")
            != composer_facet_response.get("seed_record", {}).get("record_id")
            or not guided_tour_response_shape_ok(guided_facet_response, page_lookup)
        ):
            guided_tour_query_failures.append(
                {"reason": "guided_facet_alignment", "facet": "family", "value": math_fixture["family"]}
            )

        guided_record_repeat = guided_tour_record_query(
            guided_tour_registries,
            record_id=math_fixture["record_id"],
        )
        if guided_record_repeat != guided_record_by_id:
            guided_tour_query_failures.append(
                {"reason": "guided_repeat_stability", "record_id": math_fixture["record_id"]}
            )

    if metadata_fixture is not None:
        guided_metadata = guided_tour_record_query(
            guided_tour_registries,
            record_id=metadata_fixture["record_id"],
        )
        if (
            guided_metadata.get("seed_record", {}).get("record_id") != metadata_fixture["record_id"]
            or not guided_tour_response_shape_ok(guided_metadata, page_lookup)
        ):
            guided_tour_query_failures.append(
                {"reason": "guided_metadata_lookup", "record_id": metadata_fixture["record_id"]}
            )

    representative_page_ids = []
    family_page = next((page for page in atlas_pages if page.get("page_type") == "family_shard"), None)
    anchor_page = next((page for page in atlas_pages if page.get("page_type") == "anchor_shard"), None)
    target_page = next((page for page in atlas_pages if page.get("page_type") == "target_system_shard"), None)
    locator_page = next((page for page in atlas_pages if page.get("page_type") == "record_locator_shard"), None)
    hemisphere_page = next((page for page in atlas_pages if page.get("page_type") == "hemisphere"), None)
    overview_page = page_lookup.get("VA-OVERVIEW")
    for page in [family_page, anchor_page, target_page, locator_page, hemisphere_page, overview_page]:
        if page is not None:
            representative_page_ids.append(page.get("page_id", ""))

    for page_id in representative_page_ids:
        expected_seed_ids = page_seed_ids(guided_tour_registries, page_id)
        page_response = guided_tour_page_query(
            guided_tour_registries,
            page_id=page_id,
            expanded=True,
        )
        alt_seed_ids = [
            item.get("seed_record", {}).get("record_id", "")
            for item in page_response.get("alternative_seeds", [])
        ]
        if (
            page_response.get("source_page", {}).get("page_id") != page_id
            or page_response.get("seed_record", {}).get("record_id") != (expected_seed_ids[0] if expected_seed_ids else None)
            or alt_seed_ids != expected_seed_ids[1:4]
            or not guided_tour_response_shape_ok(page_response, page_lookup)
        ):
            guided_tour_query_failures.append(
                {
                    "reason": "guided_page_alignment",
                    "page_id": page_id,
                    "expected_seed": expected_seed_ids[0] if expected_seed_ids else None,
                    "actual_seed": page_response.get("seed_record", {}).get("record_id"),
                    "expected_alternatives": expected_seed_ids[1:4],
                    "actual_alternatives": alt_seed_ids,
                }
            )

    checks.append(
        run_check(
            "guided_tour_queries",
            not guided_tour_query_failures,
            {"violations": guided_tour_query_failures[:20]},
        )
    )

    live_docs_status = load_docs_gate_status()
    docs_gate_ok = (
        manifest.get("docs_gate_status") == live_docs_status
        and dual_route_registry.get("docs_gate_status") == live_docs_status
        and direct_edge_registry.get("docs_gate_status") == live_docs_status
        and route_coverage_registry.get("docs_gate_status") == live_docs_status
        and route_manifest.get("docs_gate_status") == live_docs_status
        and navigator_alias_index.get("docs_gate_status") == live_docs_status
        and navigator_facet_index.get("docs_gate_status") == live_docs_status
        and navigator_neighbor_index.get("docs_gate_status") == live_docs_status
        and navigator_manifest.get("docs_gate_status") == live_docs_status
        and composer_seed_registry.get("docs_gate_status") == live_docs_status
        and composer_facet_registry.get("docs_gate_status") == live_docs_status
        and composer_manifest.get("docs_gate_status") == live_docs_status
        and synthesis_evidence_registry.get("docs_gate_status") == live_docs_status
        and synthesis_seed_registry.get("docs_gate_status") == live_docs_status
        and synthesis_facet_registry.get("docs_gate_status") == live_docs_status
        and synthesis_manifest.get("docs_gate_status") == live_docs_status
        and visual_atlas_node_registry.get("docs_gate_status") == live_docs_status
        and visual_atlas_edge_registry.get("docs_gate_status") == live_docs_status
        and visual_atlas_page_registry.get("docs_gate_status") == live_docs_status
        and visual_atlas_record_locator_registry.get("docs_gate_status") == live_docs_status
        and visual_atlas_manifest.get("docs_gate_status") == live_docs_status
        and guided_tour_seed_registry.get("docs_gate_status") == live_docs_status
        and guided_tour_page_registry.get("docs_gate_status") == live_docs_status
        and guided_tour_manifest.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "docs_gate_status",
            docs_gate_ok,
            {
                "manifest": manifest.get("docs_gate_status"),
                "route_registry": dual_route_registry.get("docs_gate_status"),
                "edge_registry": direct_edge_registry.get("docs_gate_status"),
                "coverage_registry": route_coverage_registry.get("docs_gate_status"),
                "route_manifest": route_manifest.get("docs_gate_status"),
                "navigator_alias_index": navigator_alias_index.get("docs_gate_status"),
                "navigator_facet_index": navigator_facet_index.get("docs_gate_status"),
                "navigator_neighbor_index": navigator_neighbor_index.get("docs_gate_status"),
                "navigator_manifest": navigator_manifest.get("docs_gate_status"),
                "composer_seed_registry": composer_seed_registry.get("docs_gate_status"),
                "composer_facet_registry": composer_facet_registry.get("docs_gate_status"),
                "composer_manifest": composer_manifest.get("docs_gate_status"),
                "synthesis_evidence_registry": synthesis_evidence_registry.get("docs_gate_status"),
                "synthesis_seed_registry": synthesis_seed_registry.get("docs_gate_status"),
                "synthesis_facet_registry": synthesis_facet_registry.get("docs_gate_status"),
                "synthesis_manifest": synthesis_manifest.get("docs_gate_status"),
                "visual_atlas_node_registry": visual_atlas_node_registry.get("docs_gate_status"),
                "visual_atlas_edge_registry": visual_atlas_edge_registry.get("docs_gate_status"),
                "visual_atlas_page_registry": visual_atlas_page_registry.get("docs_gate_status"),
                "visual_atlas_record_locator_registry": visual_atlas_record_locator_registry.get("docs_gate_status"),
                "visual_atlas_manifest": visual_atlas_manifest.get("docs_gate_status"),
                "guided_tour_seed_registry": guided_tour_seed_registry.get("docs_gate_status"),
                "guided_tour_page_registry": guided_tour_page_registry.get("docs_gate_status"),
                "guided_tour_manifest": guided_tour_manifest.get("docs_gate_status"),
                "live_docs_gate": live_docs_status,
                "source_path": str(DOCS_GATE_PATH),
            },
        )
    )

    mirror_record_registry = load_json(FLEET_MIRROR_ROOT / RECORD_REGISTRY_PATH.name)
    mirror_hub_registry = load_json(FLEET_MIRROR_ROOT / HUB_REGISTRY_PATH.name)
    mirror_manifest = load_json(FLEET_MIRROR_ROOT / MANIFEST_PATH.name)
    mirror_route_registry = load_json(FLEET_MIRROR_ROOT / DUAL_ROUTE_REGISTRY_PATH.name)
    mirror_edge_registry = load_json(FLEET_MIRROR_ROOT / DIRECT_EDGE_REGISTRY_PATH.name)
    mirror_coverage_registry = load_json(FLEET_MIRROR_ROOT / ROUTE_COVERAGE_REGISTRY_PATH.name)
    mirror_route_manifest = load_json(FLEET_MIRROR_ROOT / ROUTE_MANIFEST_PATH.name)
    mirror_alias_index = load_json(FLEET_MIRROR_ROOT / NAVIGATOR_ALIAS_INDEX_PATH.name)
    mirror_facet_index = load_json(FLEET_MIRROR_ROOT / NAVIGATOR_FACET_INDEX_PATH.name)
    mirror_neighbor_index = load_json(FLEET_MIRROR_ROOT / NAVIGATOR_NEIGHBOR_INDEX_PATH.name)
    mirror_navigator_manifest = load_json(FLEET_MIRROR_ROOT / NAVIGATOR_MANIFEST_PATH.name)
    mirror_composer_seed_registry = load_json(FLEET_MIRROR_ROOT / COMPOSER_SEED_REGISTRY_PATH.name)
    mirror_composer_facet_registry = load_json(FLEET_MIRROR_ROOT / COMPOSER_FACET_REGISTRY_PATH.name)
    mirror_composer_manifest = load_json(FLEET_MIRROR_ROOT / COMPOSER_MANIFEST_PATH.name)
    mirror_synthesis_evidence_registry = load_json(FLEET_MIRROR_ROOT / SYNTHESIS_EVIDENCE_REGISTRY_PATH.name)
    mirror_synthesis_seed_registry = load_json(FLEET_MIRROR_ROOT / SYNTHESIS_SEED_REGISTRY_PATH.name)
    mirror_synthesis_facet_registry = load_json(FLEET_MIRROR_ROOT / SYNTHESIS_FACET_REGISTRY_PATH.name)
    mirror_synthesis_manifest = load_json(FLEET_MIRROR_ROOT / SYNTHESIS_MANIFEST_PATH.name)
    mirror_visual_atlas_node_registry = load_json(FLEET_MIRROR_ROOT / VISUAL_ATLAS_NODE_REGISTRY_PATH.name)
    mirror_visual_atlas_edge_registry = load_json(FLEET_MIRROR_ROOT / VISUAL_ATLAS_EDGE_REGISTRY_PATH.name)
    mirror_visual_atlas_page_registry = load_json(FLEET_MIRROR_ROOT / VISUAL_ATLAS_PAGE_REGISTRY_PATH.name)
    mirror_visual_atlas_record_locator_registry = load_json(
        FLEET_MIRROR_ROOT / VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH.name
    )
    mirror_visual_atlas_manifest = load_json(FLEET_MIRROR_ROOT / VISUAL_ATLAS_MANIFEST_PATH.name)
    mirror_guided_tour_seed_registry = load_json(FLEET_MIRROR_ROOT / GUIDED_TOUR_SEED_REGISTRY_PATH.name)
    mirror_guided_tour_page_registry = load_json(FLEET_MIRROR_ROOT / GUIDED_TOUR_PAGE_REGISTRY_PATH.name)
    mirror_guided_tour_manifest = load_json(FLEET_MIRROR_ROOT / GUIDED_TOUR_MANIFEST_PATH.name)

    hub_ids = [hub["hub_id"] for hub in hub_registry.get("hubs", [])]
    mirror_hub_ids = [hub["hub_id"] for hub in mirror_hub_registry.get("hubs", [])]
    route_ids = [route["route_id"] for route in routes]
    mirror_route_ids = [route["route_id"] for route in mirror_route_registry.get("routes", [])]
    edge_ids = [edge["edge_id"] for edge in edges]
    mirror_edge_ids = [edge["edge_id"] for edge in mirror_edge_registry.get("edges", [])]
    mirror_ok = (
        mirror_record_registry.get("deduplicated_record_count")
        == record_registry.get("deduplicated_record_count")
        and hub_ids == mirror_hub_ids
        and mirror_manifest.get("counts") == manifest.get("counts")
        and mirror_route_registry.get("route_count") == dual_route_registry.get("route_count")
        and mirror_edge_registry.get("edge_count") == direct_edge_registry.get("edge_count")
        and mirror_coverage_registry.get("record_count")
        == route_coverage_registry.get("record_count")
        and mirror_route_ids == route_ids
        and mirror_edge_ids == edge_ids
        and mirror_route_manifest.get("routing_systems") == route_manifest.get("routing_systems")
        and mirror_route_manifest.get("docs_gate_status") == route_manifest.get("docs_gate_status")
        and mirror_alias_index.get("alias_key_count") == navigator_alias_index.get("alias_key_count")
        and mirror_facet_index.get("facet_cardinalities") == navigator_facet_index.get("facet_cardinalities")
        and mirror_neighbor_index.get("record_count") == navigator_neighbor_index.get("record_count")
        and mirror_navigator_manifest.get("counts") == navigator_manifest.get("counts")
        and mirror_composer_seed_registry.get("counts") == composer_seed_registry.get("counts")
        and mirror_composer_facet_registry.get("facet_counts") == composer_facet_registry.get("facet_counts")
        and mirror_composer_manifest.get("counts") == composer_manifest.get("counts")
        and mirror_synthesis_evidence_registry.get("record_count") == synthesis_evidence_registry.get("record_count")
        and mirror_synthesis_seed_registry.get("counts") == synthesis_seed_registry.get("counts")
        and mirror_synthesis_facet_registry.get("facet_counts") == synthesis_facet_registry.get("facet_counts")
        and mirror_synthesis_manifest.get("counts") == synthesis_manifest.get("counts")
        and mirror_visual_atlas_node_registry.get("node_count") == visual_atlas_node_registry.get("node_count")
        and mirror_visual_atlas_edge_registry.get("edge_count") == visual_atlas_edge_registry.get("edge_count")
        and mirror_visual_atlas_page_registry.get("page_count") == visual_atlas_page_registry.get("page_count")
        and mirror_visual_atlas_record_locator_registry.get("record_count")
        == visual_atlas_record_locator_registry.get("record_count")
        and mirror_visual_atlas_manifest.get("counts") == visual_atlas_manifest.get("counts")
        and mirror_guided_tour_seed_registry.get("counts") == guided_tour_seed_registry.get("counts")
        and mirror_guided_tour_page_registry.get("page_count") == guided_tour_page_registry.get("page_count")
        and mirror_guided_tour_manifest.get("counts") == guided_tour_manifest.get("counts")
    )
    checks.append(
        run_check(
            "fleet_mirror_consistency",
            mirror_ok,
            {
                "canonical_count": record_registry.get("deduplicated_record_count"),
                "mirror_count": mirror_record_registry.get("deduplicated_record_count"),
                "canonical_hubs": hub_ids,
                "mirror_hubs": mirror_hub_ids,
                "canonical_route_count": dual_route_registry.get("route_count"),
                "mirror_route_count": mirror_route_registry.get("route_count"),
                "canonical_edge_count": direct_edge_registry.get("edge_count"),
                "mirror_edge_count": mirror_edge_registry.get("edge_count"),
                "canonical_alias_keys": navigator_alias_index.get("alias_key_count"),
                "mirror_alias_keys": mirror_alias_index.get("alias_key_count"),
                "canonical_atlas_pages": visual_atlas_page_registry.get("page_count"),
                "mirror_atlas_pages": mirror_visual_atlas_page_registry.get("page_count"),
                "canonical_guided_seed_starters": sum(guided_tour_seed_registry.get("counts", {}).values()),
                "mirror_guided_seed_starters": sum(mirror_guided_tour_seed_registry.get("counts", {}).values()),
                "canonical_guided_page_starters": guided_tour_page_registry.get("page_count"),
                "mirror_guided_page_starters": mirror_guided_tour_page_registry.get("page_count"),
            },
        )
    )

    metro_levels_ok = len(metro_registry.get("levels", [])) == 4
    checks.append(
        run_check(
            "metro_levels",
            metro_levels_ok,
            {"level_count": len(metro_registry.get("levels", []))},
        )
    )

    no_crystal_duplication_ok = (
        sum(1 for record in records if record.get("primary_hemisphere") == "MATH")
        + sum(1 for record in records if record.get("primary_hemisphere") == "MYTH")
        == len(records)
    )
    checks.append(
        run_check(
            "single_primary_crystal_membership",
            no_crystal_duplication_ok,
            {
                "record_count": len(records),
                "math_primary": sum(
                    1 for record in records if record.get("primary_hemisphere") == "MATH"
                ),
                "myth_primary": sum(
                    1 for record in records if record.get("primary_hemisphere") == "MYTH"
                ),
            },
        )
    )

    authority_records = full_corpus_authority_registry.get("records", [])
    basis_rows = full_corpus_basis_crosswalk_registry.get("rows", [])
    full_route_rows = full_corpus_route_coverage_registry.get("rows", [])
    stage_assignments = full_corpus_awakening_stage_registry.get("record_assignments", [])
    family_notes = full_corpus_awakening_agent_transition_registry.get("family_notes", [])
    basis_notes = full_corpus_awakening_agent_transition_registry.get("basis_role_notes", [])
    stage_family_notes = full_corpus_awakening_agent_transition_registry.get("stage_family_matrix", [])

    merged_scope_ok = (
        full_corpus_authority_registry.get("record_count") == len(authority_records)
        and full_corpus_integration_manifest.get("counts", {}).get("live_atlas_records")
        == full_live_atlas.get("record_count")
        and full_corpus_integration_manifest.get("counts", {}).get("archive_atlas_records")
        == full_archive_atlas.get("record_count")
        and full_corpus_integration_manifest.get("counts", {}).get("merged_canonical_records")
        == len(authority_records)
    )
    checks.append(
        run_check(
            "full_corpus_merged_scope",
            merged_scope_ok,
            {
                "live_atlas_records": full_live_atlas.get("record_count"),
                "archive_atlas_records": full_archive_atlas.get("record_count"),
                "merged_canonical_records": len(authority_records),
                "manifest_counts": full_corpus_integration_manifest.get("counts", {}),
            },
        )
    )

    basis_crosswalk_ok = (
        len(basis_rows) == len(authority_records)
        and all(row.get("basis_anchor_ids") or row.get("abstention_reason") for row in basis_rows)
    )
    checks.append(
        run_check(
            "full_corpus_basis_crosswalk",
            basis_crosswalk_ok,
            {
                "authority_records": len(authority_records),
                "basis_rows": len(basis_rows),
                "weak_or_uncovered": len(
                    full_corpus_basis_crosswalk_registry.get("weak_or_uncovered_rows", [])
                ),
            },
        )
    )

    route_saturation_ok = all(
        row.get("primary_route_id")
        and row.get("secondary_route_id")
        and row.get("gc0_membership") == UNIFIED_HUB_ID
        for row in full_route_rows
    )
    checks.append(
        run_check(
            "full_corpus_route_saturation",
            route_saturation_ok,
            {
                "route_rows": len(full_route_rows),
                "complete_rows": full_corpus_route_coverage_registry.get("complete_count"),
                "gc0_edge_count": full_corpus_route_coverage_registry.get("gc0_edge_count"),
            },
        )
    )

    stage_assignment_ok = (
        len(stage_assignments) == len(authority_records)
        and all(item.get("stage_id") or item.get("abstention_reason") for item in stage_assignments)
        and full_corpus_awakening_stage_registry.get("stage_count") == 7
    )
    checks.append(
        run_check(
            "awakening_stage_matrix",
            stage_assignment_ok,
            {
                "record_assignments": len(stage_assignments),
                "assigned_count": full_corpus_awakening_stage_registry.get("assigned_count"),
                "abstention_count": full_corpus_awakening_stage_registry.get("abstention_count"),
                "stage_count": full_corpus_awakening_stage_registry.get("stage_count"),
            },
        )
    )

    agent_notes_ok = (
        len(family_notes) == len(FAMILY_LABELS)
        and len(basis_notes) == 16
        and len(stage_family_notes) == 7 * len(FAMILY_LABELS)
        and all(note.get("evidence_ids") or note.get("abstention_reason") for note in family_notes)
        and all(note.get("evidence_ids") or note.get("abstention_reason") for note in basis_notes)
        and all(note.get("evidence_ids") or note.get("abstention_reason") for note in stage_family_notes)
    )
    checks.append(
        run_check(
            "awakening_agent_matrix",
            agent_notes_ok,
            {
                "family_notes": len(family_notes),
                "basis_role_notes": len(basis_notes),
                "stage_family_notes": len(stage_family_notes),
            },
        )
    )

    witness_records = [record for record in authority_records if not record.get("text_extractable")]
    witness_ok = all(
        any(
            assignment.get("record_id") == record.get("record_id")
            and (assignment.get("stage_id") or assignment.get("abstention_reason"))
            for assignment in stage_assignments
        )
        for record in witness_records
    )
    checks.append(
        run_check(
            "full_corpus_witness_retention",
            witness_ok,
            {
                "witness_records": len(witness_records),
                "sample_witnesses": [record.get("record_id") for record in witness_records[:5]],
            },
        )
    )

    allowed_appendix_ids = set(full_corpus_appendix_governance_ledger.get("allowed_appendix_ids", []))
    appendix_governance_ok = all(
        set(row.get("appendix_support", [])).issubset(allowed_appendix_ids)
        for row in full_corpus_appendix_governance_ledger.get("rows", [])
    )
    checks.append(
        run_check(
            "full_corpus_appendix_governance",
            appendix_governance_ok,
            {
                "ledger_rows": full_corpus_appendix_governance_ledger.get("record_count"),
                "counts": full_corpus_appendix_governance_ledger.get("counts", {}),
                "allowed_appendix_ids": sorted(allowed_appendix_ids),
            },
        )
    )

    full_docs_gate_ok = all(
        payload.get("docs_gate_status") == live_docs_status
        for payload in (
            full_corpus_authority_registry,
            full_corpus_basis_crosswalk_registry,
            full_corpus_route_coverage_registry,
            full_corpus_awakening_stage_registry,
            full_corpus_awakening_agent_transition_registry,
            full_corpus_appendix_governance_ledger,
            full_corpus_integration_manifest,
        )
    )
    checks.append(
        run_check(
            "full_corpus_docs_gate_propagation",
            full_docs_gate_ok,
            {
                "authority_registry": full_corpus_authority_registry.get("docs_gate_status"),
                "basis_crosswalk_registry": full_corpus_basis_crosswalk_registry.get("docs_gate_status"),
                "route_coverage_registry": full_corpus_route_coverage_registry.get("docs_gate_status"),
                "awakening_stage_registry": full_corpus_awakening_stage_registry.get("docs_gate_status"),
                "awakening_agent_transition_registry": full_corpus_awakening_agent_transition_registry.get("docs_gate_status"),
                "appendix_governance_ledger": full_corpus_appendix_governance_ledger.get("docs_gate_status"),
                "integration_manifest": full_corpus_integration_manifest.get("docs_gate_status"),
                "live_docs_gate": live_docs_status,
            },
        )
    )

    mirror_full_authority = load_json(FLEET_MIRROR_ROOT / FULL_CORPUS_AUTHORITY_REGISTRY_PATH.name)
    mirror_full_basis = load_json(FLEET_MIRROR_ROOT / FULL_CORPUS_BASIS_CROSSWALK_REGISTRY_PATH.name)
    mirror_full_route = load_json(FLEET_MIRROR_ROOT / FULL_CORPUS_ROUTE_COVERAGE_REGISTRY_PATH.name)
    mirror_full_stage = load_json(FLEET_MIRROR_ROOT / FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH.name)
    mirror_full_agent = load_json(
        FLEET_MIRROR_ROOT / FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH.name
    )
    mirror_full_appendix = load_json(
        FLEET_MIRROR_ROOT / FULL_CORPUS_APPENDIX_GOVERNANCE_LEDGER_PATH.name
    )
    mirror_full_manifest = load_json(FLEET_MIRROR_ROOT / FULL_CORPUS_INTEGRATION_MANIFEST_PATH.name)
    full_mirror_ok = (
        mirror_full_authority.get("record_count") == full_corpus_authority_registry.get("record_count")
        and mirror_full_basis.get("record_count") == full_corpus_basis_crosswalk_registry.get("record_count")
        and mirror_full_route.get("record_count") == full_corpus_route_coverage_registry.get("record_count")
        and mirror_full_stage.get("record_assignment_count")
        == full_corpus_awakening_stage_registry.get("record_assignment_count")
        and mirror_full_agent.get("stage_family_note_count")
        == full_corpus_awakening_agent_transition_registry.get("stage_family_note_count")
        and mirror_full_appendix.get("record_count")
        == full_corpus_appendix_governance_ledger.get("record_count")
        and mirror_full_manifest.get("counts") == full_corpus_integration_manifest.get("counts")
    )
    checks.append(
        run_check(
            "full_corpus_fleet_mirror_consistency",
            full_mirror_ok,
            {
                "canonical_records": full_corpus_authority_registry.get("record_count"),
                "mirror_records": mirror_full_authority.get("record_count"),
                "canonical_stage_assignments": full_corpus_awakening_stage_registry.get("record_assignment_count"),
                "mirror_stage_assignments": mirror_full_stage.get("record_assignment_count"),
            },
        )
    )

    ap6d_loops = ap6d_57_loop_control_registry.get("loops", [])
    ap6d_agents = ap6d_57_agent_lane_registry.get("agents", [])
    ap6d_seat_rows = ap6d_57_nested_seat_manifest.get("rows", [])
    ap6d_bundle_rows = ap6d_57_quest_bundle_registry.get("rows", [])
    ap6d_worker_rows = ap6d_57_worker_action_registry.get("rows", [])
    ap6d_pruning_rows = ap6d_57_pruning_registry.get("rows", [])
    ap6d_awakening_rows = ap6d_57_awakening_transition_registry.get("rows", [])
    ap6d_restart_rows = ap6d_57_restart_seed_registry.get("rows", [])

    ap6d_control_ok = (
        ap6d_57_loop_control_registry.get("loop_count") == AP6D_57_LOOP_COUNT
        and len(ap6d_loops) == AP6D_57_LOOP_COUNT
        and all(
            set(loop.get("artifact_ids", {})) == {
                "loop_manifest",
                "research_packet",
                "hall_quest_bundle",
                "temple_quest_bundle",
                "worker_action_bundle",
                "pruning_receipt",
                "restart_seed",
            }
            and loop.get("docs_gate_status") == live_docs_status
            and len(loop.get("focus_record_ids", [])) > 0
            for loop in ap6d_loops
        )
    )
    checks.append(
        run_check(
            "ap6d_57_loop_control_registry",
            ap6d_control_ok,
            {
                "loop_count": len(ap6d_loops),
                "declared_loop_count": ap6d_57_loop_control_registry.get("loop_count"),
                "docs_gate_status": ap6d_57_loop_control_registry.get("docs_gate_status"),
            },
        )
    )

    ap6d_agent_lane_ok = (
        ap6d_57_agent_lane_registry.get("master_agent_count") == AP6D_57_MASTER_AGENT_COUNT
        and len(ap6d_agents) == AP6D_57_MASTER_AGENT_COUNT
        and set(ap6d_57_agent_lane_registry.get("shared_axes", {}))
        == {"scope", "hemisphere", "deep_mode", "resolution", "venue", "phase"}
        and all(len(values) == 4 for values in ap6d_57_agent_lane_registry.get("shared_axes", {}).values())
    )
    checks.append(
        run_check(
            "ap6d_57_agent_lane_registry",
            ap6d_agent_lane_ok,
            {
                "agent_count": len(ap6d_agents),
                "shared_axes": ap6d_57_agent_lane_registry.get("shared_axes", {}),
            },
        )
    )

    ap6d_nested_ok = (
        ap6d_57_nested_seat_manifest.get("row_count") == AP6D_57_LOOP_COUNT * AP6D_57_MASTER_AGENT_COUNT
        and len(ap6d_seat_rows) == AP6D_57_LOOP_COUNT * AP6D_57_MASTER_AGENT_COUNT
        and all(
            row.get("manifest_seat_count") == AP6D_57_ATLAS_SEAT_TOTAL
            and row.get("synaptic_seat_count") == AP6D_57_SYNAPTIC_SEAT_COUNT
            and row.get("governance_fiber_count") == AP6D_57_GOVERNANCE_FIBER_COUNT
            and row.get("ownerable_packet_count") == AP6D_57_OWNERABLE_PACKET_COUNT
            and row.get("liminal_packet_count") == AP6D_57_LIMINAL_PACKET_COUNT
            for row in ap6d_seat_rows
        )
    )
    checks.append(
        run_check(
            "ap6d_57_nested_seat_manifest",
            ap6d_nested_ok,
            {
                "row_count": len(ap6d_seat_rows),
                "seat_totals": ap6d_57_nested_seat_manifest.get("seat_totals", {}),
            },
        )
    )

    ap6d_bundle_ok = (
        ap6d_57_quest_bundle_registry.get("row_count") == AP6D_57_LOOP_COUNT * AP6D_57_MASTER_AGENT_COUNT
        and len(ap6d_bundle_rows) == AP6D_57_LOOP_COUNT * AP6D_57_MASTER_AGENT_COUNT
        and all(
            len(row.get("governance_fiber_ids", [])) == AP6D_57_GOVERNANCE_FIBER_COUNT
            and len(row.get("ownerable_packet_ids", [])) == AP6D_57_OWNERABLE_PACKET_COUNT
            and len(row.get("liminal_packet_ids", [])) == AP6D_57_LIMINAL_PACKET_COUNT
            for row in ap6d_bundle_rows
        )
    )
    checks.append(
        run_check(
            "ap6d_57_quest_bundle_registry",
            ap6d_bundle_ok,
            {
                "row_count": len(ap6d_bundle_rows),
                "sample_hall_bundle": ap6d_bundle_rows[0].get("hall_bundle_id") if ap6d_bundle_rows else "",
            },
        )
    )

    ap6d_worker_ok = (
        ap6d_57_worker_action_registry.get("row_count") == AP6D_57_LOOP_COUNT
        and len(ap6d_worker_rows) == AP6D_57_LOOP_COUNT
        and all(row.get("action_groups") for row in ap6d_worker_rows)
    )
    checks.append(
        run_check(
            "ap6d_57_worker_action_registry",
            ap6d_worker_ok,
            {
                "row_count": len(ap6d_worker_rows),
                "sample_action_count": len(ap6d_worker_rows[0].get("action_groups", [])) if ap6d_worker_rows else 0,
            },
        )
    )

    ap6d_pruning_ok = (
        ap6d_57_pruning_registry.get("row_count") == AP6D_57_LOOP_COUNT
        and len(ap6d_pruning_rows) == AP6D_57_LOOP_COUNT
        and all(row.get("restart_seed_id") for row in ap6d_pruning_rows)
    )
    ap6d_awakening_ok = (
        ap6d_57_awakening_transition_registry.get("row_count") == AP6D_57_LOOP_COUNT
        and len(ap6d_awakening_rows) == AP6D_57_LOOP_COUNT
        and all(
            row.get("family_note_ids")
            and row.get("basis_role_note_ids")
            and row.get("stage_family_note_ids")
            for row in ap6d_awakening_rows
        )
    )
    restart_chain_ok = (
        ap6d_57_restart_seed_registry.get("row_count") == AP6D_57_LOOP_COUNT
        and len(ap6d_restart_rows) == AP6D_57_LOOP_COUNT
        and all(
            row.get("next_loop_id") == f"AP6D-L{(row.get('loop_number') % AP6D_57_LOOP_COUNT) + 1:02d}"
            for row in ap6d_restart_rows
        )
    )
    checks.append(
        run_check(
            "ap6d_57_pruning_registry",
            ap6d_pruning_ok,
            {"row_count": len(ap6d_pruning_rows)},
        )
    )
    checks.append(
        run_check(
            "ap6d_57_awakening_transition_registry",
            ap6d_awakening_ok,
            {"row_count": len(ap6d_awakening_rows)},
        )
    )
    checks.append(
        run_check(
            "ap6d_57_restart_seed_registry",
            restart_chain_ok,
            {
                "row_count": len(ap6d_restart_rows),
                "loop_57_next": ap6d_restart_rows[-1].get("next_loop_id") if ap6d_restart_rows else "",
            },
        )
    )

    ap6d_docs_gate_ok = all(
        payload.get("docs_gate_status") == live_docs_status
        for payload in (
            ap6d_57_loop_control_registry,
            ap6d_57_agent_lane_registry,
            ap6d_57_nested_seat_manifest,
            ap6d_57_quest_bundle_registry,
            ap6d_57_worker_action_registry,
            ap6d_57_pruning_registry,
            ap6d_57_awakening_transition_registry,
            ap6d_57_restart_seed_registry,
            ap6d_57_loop_manifest,
        )
    )
    checks.append(
        run_check(
            "ap6d_57_docs_gate_propagation",
            ap6d_docs_gate_ok,
            {
                "loop_manifest": ap6d_57_loop_manifest.get("docs_gate_status"),
                "live_docs_gate": live_docs_status,
            },
        )
    )

    mirror_ap6d_control = load_json(FLEET_MIRROR_ROOT / AP6D_57_LOOP_CONTROL_REGISTRY_PATH.name)
    mirror_ap6d_lane = load_json(FLEET_MIRROR_ROOT / AP6D_57_AGENT_LANE_REGISTRY_PATH.name)
    mirror_ap6d_seats = load_json(FLEET_MIRROR_ROOT / AP6D_57_NESTED_SEAT_MANIFEST_PATH.name)
    mirror_ap6d_bundles = load_json(FLEET_MIRROR_ROOT / AP6D_57_QUEST_BUNDLE_REGISTRY_PATH.name)
    mirror_ap6d_workers = load_json(FLEET_MIRROR_ROOT / AP6D_57_WORKER_ACTION_REGISTRY_PATH.name)
    mirror_ap6d_pruning = load_json(FLEET_MIRROR_ROOT / AP6D_57_PRUNING_REGISTRY_PATH.name)
    mirror_ap6d_awakening = load_json(FLEET_MIRROR_ROOT / AP6D_57_AWAKENING_TRANSITION_REGISTRY_PATH.name)
    mirror_ap6d_restart = load_json(FLEET_MIRROR_ROOT / AP6D_57_RESTART_SEED_REGISTRY_PATH.name)
    mirror_ap6d_manifest = load_json(FLEET_MIRROR_ROOT / AP6D_57_LOOP_MANIFEST_PATH.name)
    ap6d_mirror_ok = (
        mirror_ap6d_control.get("loop_count") == ap6d_57_loop_control_registry.get("loop_count")
        and mirror_ap6d_lane.get("master_agent_count") == ap6d_57_agent_lane_registry.get("master_agent_count")
        and mirror_ap6d_seats.get("row_count") == ap6d_57_nested_seat_manifest.get("row_count")
        and mirror_ap6d_bundles.get("row_count") == ap6d_57_quest_bundle_registry.get("row_count")
        and mirror_ap6d_workers.get("row_count") == ap6d_57_worker_action_registry.get("row_count")
        and mirror_ap6d_pruning.get("row_count") == ap6d_57_pruning_registry.get("row_count")
        and mirror_ap6d_awakening.get("row_count") == ap6d_57_awakening_transition_registry.get("row_count")
        and mirror_ap6d_restart.get("row_count") == ap6d_57_restart_seed_registry.get("row_count")
        and mirror_ap6d_manifest.get("counts") == ap6d_57_loop_manifest.get("counts")
    )
    checks.append(
        run_check(
            "ap6d_57_fleet_mirror_consistency",
            ap6d_mirror_ok,
            {
                "canonical_loops": ap6d_57_loop_control_registry.get("loop_count"),
                "mirror_loops": mirror_ap6d_control.get("loop_count"),
            },
        )
    )

    ap6d_surface_exists = all(path.is_file() for path in AP6D_57_HEMISPHERE_DOCS.values()) and all(
        path.is_file()
        for path in (
            AP6D_57_GUILD_HALL_DOC_PATH,
            AP6D_57_TEMPLE_DOC_PATH,
            AP6D_57_DEEP_CONTROL_DOC_PATH,
            AP6D_57_RECEIPT_PATH,
            GUILD_HALL_BOARD_PATH,
            TEMPLE_QUEST_BOARD_PATH,
            FLEET_MIRROR_ROOT / AP6D_57_GUILD_HALL_DOC_PATH.name,
            FLEET_MIRROR_ROOT / AP6D_57_TEMPLE_DOC_PATH.name,
            FLEET_MIRROR_ROOT / AP6D_57_DEEP_CONTROL_DOC_PATH.name,
            FLEET_MIRROR_ROOT / AP6D_57_RECEIPT_PATH.name,
        )
    )
    board_marker_ok = (
        "<!-- AP6D_57_LOOP_CYCLE:START -->" in GUILD_HALL_BOARD_PATH.read_text(encoding="utf-8")
        and "<!-- AP6D_57_LOOP_CYCLE:START -->" in TEMPLE_QUEST_BOARD_PATH.read_text(encoding="utf-8")
    )
    checks.append(
        run_check(
            "ap6d_57_surface_existence",
            ap6d_surface_exists and board_marker_ok,
            {
                "hemisphere_docs": len(AP6D_57_HEMISPHERE_DOCS),
                "guild_hall_doc": str(AP6D_57_GUILD_HALL_DOC_PATH),
                "temple_doc": str(AP6D_57_TEMPLE_DOC_PATH),
            },
        )
    )

    navigator_runtime = load_navigator_registries()
    sample_control_record = next((record for record in records if record.get("sha256")), None)
    navigator_awakening_ok = False
    awakening_response = {}
    if sample_control_record is not None:
        awakening_response = navigator_record_query(
            navigator_runtime,
            record_id=sample_control_record["record_id"],
        )
        navigator_awakening_ok = bool(
            awakening_response.get("awakening", {}).get("docs_gate_status")
            and (
                awakening_response.get("awakening", {}).get("stage_id")
                or awakening_response.get("awakening", {}).get("abstention_reason")
            )
        )
    checks.append(
        run_check(
            "navigator_awakening_enrichment",
            navigator_awakening_ok,
            {
                "record_id": sample_control_record.get("record_id") if sample_control_record else "",
                "awakening": awakening_response.get("awakening", {}),
            },
        )
    )

    lp57omega_loop_rows = lp57omega_loop_registry.get("rows", [])
    lp57omega_agent_rows = lp57omega_agent_identity_registry.get("rows", [])
    lp57omega_coordinate_rows = lp57omega_coordinate_registry.get("rows", [])
    lp57omega_contract_rows = lp57omega_quest_contract_registry.get("rows", [])
    lp57omega_ledger_rows = lp57omega_master_ledger_registry.get("rows", [])
    shared_lattice_rows = master_loop_shared_lattice.get("rows", [])

    loop_required_fields = {
        "loop_id",
        "loop_key",
        "title",
        "dominant_focus",
        "synthesis_objective",
        "planning_objective",
        "implementation_objective",
        "compression_objective",
        "expected_structural_gain",
        "expected_mapping_gain",
        "advancement_signature",
        "artifact_ids",
        "receipt_ids",
        "restart_handoff",
        "docs_gate_status",
    }
    lp57omega_loop_ok = (
        lp57omega_loop_registry.get("loop_count") == LP57OMEGA_LOOP_COUNT
        and len(lp57omega_loop_rows) == LP57OMEGA_LOOP_COUNT
        and all(loop_required_fields.issubset(row) for row in lp57omega_loop_rows)
        and len({row.get("advancement_signature") for row in lp57omega_loop_rows})
        == LP57OMEGA_LOOP_COUNT
        and all(row.get("docs_gate_status") == live_docs_status for row in lp57omega_loop_rows)
    )
    checks.append(
        run_check(
            "lp57omega_loop_registry",
            lp57omega_loop_ok,
            {
                "loop_count": len(lp57omega_loop_rows),
                "declared_loop_count": lp57omega_loop_registry.get("loop_count"),
                "unique_advancement_signatures": len(
                    {row.get("advancement_signature") for row in lp57omega_loop_rows}
                ),
            },
        )
    )

    master_loop_state_ok = (
        len(master_loop_state.get("loops", [])) == LP57OMEGA_LOOP_COUNT
        and len(master_loop_state.get("current_cycle_summary", {}).get("required_cycle_outputs", [])) == 7
        and set(master_loop_state.get("canonical_support_registries", {}))
        == {
            "loop_registry",
            "agent_identity_registry",
            "coordinate_registry",
            "quest_contract_registry",
            "master_ledger_registry",
            "manifest",
        }
        and master_loop_state.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "lp57omega_master_loop_state",
            master_loop_state_ok,
            {
                "loop_rows": len(master_loop_state.get("loops", [])),
                "required_cycle_outputs": master_loop_state.get("current_cycle_summary", {}).get(
                    "required_cycle_outputs",
                    [],
                ),
            },
        )
    )

    def valid_agent_id_tag(agent_id_tag: str) -> bool:
        parts = agent_id_tag.split(".")
        if len(parts) != 5:
            return False
        loop_id, master_id, depth, branch, role = parts
        return (
            loop_id.startswith("L")
            and len(loop_id) == 3
            and master_id in {"A1", "A2", "A3", "A4"}
            and depth.startswith("D")
            and depth[1:].isdigit()
            and branch.startswith("B")
            and len(branch) == 5
            and set(branch[1:]).issubset({"0", "1", "2", "3"})
            and bool(role)
        )

    lp57omega_agent_ok = (
        lp57omega_agent_identity_registry.get("row_count")
        == LP57OMEGA_LOOP_COUNT * LP57OMEGA_MASTER_AGENT_COUNT
        and len(lp57omega_agent_rows) == LP57OMEGA_LOOP_COUNT * LP57OMEGA_MASTER_AGENT_COUNT
        and all(
            valid_agent_id_tag(str(row.get("agent_id_tag", "")))
            and set((row.get("coordinate_tuple") or {})) == set(LP57OMEGA_COORDINATE_DIMENSIONS)
            and bool(row.get("coordinate_stamp"))
            and len(row.get("sample_nested_agent_ids", [])) == 3
            for row in lp57omega_agent_rows
        )
        and len(master_agent_state.get("agents", [])) == LP57OMEGA_MASTER_AGENT_COUNT
        and master_agent_state.get("identity_registry_path") == str(LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH)
        and master_agent_state.get("quest_contract_registry_path") == str(LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH)
        and master_agent_state.get("master_ledger_registry_path") == str(LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH)
        and master_agent_state.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "lp57omega_agent_identity_registry",
            lp57omega_agent_ok,
            {
                "row_count": len(lp57omega_agent_rows),
                "declared_row_count": lp57omega_agent_identity_registry.get("row_count"),
                "agent_count": len(master_agent_state.get("agents", [])),
            },
        )
    )

    lp57omega_shared_lattice_ok = (
        master_loop_shared_lattice.get("total_seats") == 4096
        and master_loop_shared_lattice.get("active_seats") == 1024
        and master_loop_shared_lattice.get("dormant_seats") == 3072
        and master_loop_shared_lattice.get("row_count") == 4096
        and len(shared_lattice_rows) == 4096
        and all(
            set((row.get("coordinate_tuple") or {})) == set(LP57OMEGA_COORDINATE_DIMENSIONS)
            and bool(row.get("coordinate_stamp"))
            for row in shared_lattice_rows
        )
        and master_loop_shared_lattice.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "lp57omega_shared_lattice",
            lp57omega_shared_lattice_ok,
            {
                "total_seats": master_loop_shared_lattice.get("total_seats"),
                "active_seats": master_loop_shared_lattice.get("active_seats"),
                "dormant_seats": master_loop_shared_lattice.get("dormant_seats"),
                "row_count": master_loop_shared_lattice.get("row_count"),
            },
        )
    )

    lp57omega_coordinate_ok = (
        lp57omega_coordinate_registry.get("record_count") == len(authority_records)
        and len(lp57omega_coordinate_rows) == len(authority_records)
        and all(
            set((row.get("coordinate_tuple") or {})) == set(LP57OMEGA_COORDINATE_DIMENSIONS)
            and bool(row.get("coordinate_stamp"))
            and bool(row.get("lookup_address"))
            for row in lp57omega_coordinate_rows
        )
        and lp57omega_coordinate_registry.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "lp57omega_coordinate_registry",
            lp57omega_coordinate_ok,
            {
                "record_count": lp57omega_coordinate_registry.get("record_count"),
                "authority_records": len(authority_records),
            },
        )
    )

    lp57omega_contract_ok = (
        lp57omega_quest_contract_registry.get("row_count")
        == LP57OMEGA_LOOP_COUNT * LP57OMEGA_MASTER_AGENT_COUNT
        and len(lp57omega_contract_rows) == LP57OMEGA_LOOP_COUNT * LP57OMEGA_MASTER_AGENT_COUNT
        and lp57omega_quest_contract_registry.get("public_board_caps") == {"hall": 8, "temple": 8}
        and all(
            set(LP57OMEGA_QUEST_CONTRACT_FIELDS).issubset(row.get("hall_contract", {}))
            and set(LP57OMEGA_QUEST_CONTRACT_FIELDS).issubset(row.get("temple_contract", {}))
            and bool(row.get("focus_lookup_addresses", []))
            for row in lp57omega_contract_rows
        )
        and lp57omega_quest_contract_registry.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "lp57omega_quest_contract_registry",
            lp57omega_contract_ok,
            {
                "row_count": len(lp57omega_contract_rows),
                "public_caps": lp57omega_quest_contract_registry.get("public_board_caps"),
            },
        )
    )

    lp57omega_ledger_ok = (
        lp57omega_master_ledger_registry.get("row_count")
        == LP57OMEGA_LOOP_COUNT * LP57OMEGA_MASTER_AGENT_COUNT
        and len(lp57omega_ledger_rows) == LP57OMEGA_LOOP_COUNT * LP57OMEGA_MASTER_AGENT_COUNT
        and all(
            set(LP57OMEGA_LEDGER_FIELDS).issubset(row)
            and bool(row.get("linked_quests", []))
            and bool(row.get("linked_agents", []))
            and bool(row.get("unresolved_followups", []))
            for row in lp57omega_ledger_rows
        )
        and lp57omega_master_ledger_registry.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "lp57omega_master_ledger_registry",
            lp57omega_ledger_ok,
            {
                "row_count": len(lp57omega_ledger_rows),
                "declared_row_count": lp57omega_master_ledger_registry.get("row_count"),
            },
        )
    )

    lp57omega_docs_gate_ok = all(
        payload.get("docs_gate_status") == live_docs_status
        for payload in (
            master_loop_state,
            master_agent_state,
            master_loop_shared_lattice,
            lp57omega_loop_registry,
            lp57omega_agent_identity_registry,
            lp57omega_coordinate_registry,
            lp57omega_quest_contract_registry,
            lp57omega_master_ledger_registry,
            lp57omega_manifest,
        )
    )
    checks.append(
        run_check(
            "lp57omega_docs_gate_propagation",
            lp57omega_docs_gate_ok,
            {
                "manifest": lp57omega_manifest.get("docs_gate_status"),
                "loop_state": master_loop_state.get("docs_gate_status"),
                "live_docs_gate": live_docs_status,
            },
        )
    )

    mirror_lp57omega_loop = load_json(FLEET_MIRROR_ROOT / LP57OMEGA_LOOP_REGISTRY_PATH.name)
    mirror_lp57omega_agent = load_json(
        FLEET_MIRROR_ROOT / LP57OMEGA_AGENT_IDENTITY_REGISTRY_PATH.name
    )
    mirror_lp57omega_coordinate = load_json(
        FLEET_MIRROR_ROOT / LP57OMEGA_COORDINATE_REGISTRY_PATH.name
    )
    mirror_lp57omega_contract = load_json(
        FLEET_MIRROR_ROOT / LP57OMEGA_QUEST_CONTRACT_REGISTRY_PATH.name
    )
    mirror_lp57omega_ledger = load_json(
        FLEET_MIRROR_ROOT / LP57OMEGA_MASTER_LEDGER_REGISTRY_PATH.name
    )
    mirror_lp57omega_manifest = load_json(FLEET_MIRROR_ROOT / LP57OMEGA_MANIFEST_PATH.name)
    lp57omega_mirror_ok = (
        mirror_lp57omega_loop.get("loop_count") == lp57omega_loop_registry.get("loop_count")
        and mirror_lp57omega_agent.get("row_count") == lp57omega_agent_identity_registry.get("row_count")
        and mirror_lp57omega_coordinate.get("record_count") == lp57omega_coordinate_registry.get("record_count")
        and mirror_lp57omega_contract.get("row_count") == lp57omega_quest_contract_registry.get("row_count")
        and mirror_lp57omega_ledger.get("row_count") == lp57omega_master_ledger_registry.get("row_count")
        and mirror_lp57omega_manifest.get("counts") == lp57omega_manifest.get("counts")
    )
    checks.append(
        run_check(
            "lp57omega_fleet_mirror_consistency",
            lp57omega_mirror_ok,
            {
                "canonical_loops": lp57omega_loop_registry.get("loop_count"),
                "mirror_loops": mirror_lp57omega_loop.get("loop_count"),
                "canonical_coordinates": lp57omega_coordinate_registry.get("record_count"),
                "mirror_coordinates": mirror_lp57omega_coordinate.get("record_count"),
            },
        )
    )

    lp57omega_surface_exists = all(path.is_file() for path in LP57OMEGA_HEMISPHERE_DOCS.values()) and all(
        path.is_file()
        for path in (
            LP57OMEGA_GUILD_HALL_DOC_PATH,
            LP57OMEGA_TEMPLE_DOC_PATH,
            LP57OMEGA_DEEP_CONTROL_DOC_PATH,
            LP57OMEGA_RECEIPT_PATH,
            FLEET_MIRROR_ROOT / LP57OMEGA_GUILD_HALL_DOC_PATH.name,
            FLEET_MIRROR_ROOT / LP57OMEGA_TEMPLE_DOC_PATH.name,
            FLEET_MIRROR_ROOT / LP57OMEGA_DEEP_CONTROL_DOC_PATH.name,
            FLEET_MIRROR_ROOT / LP57OMEGA_RECEIPT_PATH.name,
        )
    )
    lp57omega_board_marker_ok = (
        "<!-- MASTER_LOOP_57_HALL_QUEST:START -->" in GUILD_HALL_BOARD_PATH.read_text(encoding="utf-8")
        and "<!-- MASTER_LOOP_57_TEMPLE_QUEST:START -->"
        in TEMPLE_QUEST_BOARD_PATH.read_text(encoding="utf-8")
    )
    checks.append(
        run_check(
            "lp57omega_surface_existence",
            lp57omega_surface_exists and lp57omega_board_marker_ok,
            {
                "hemisphere_docs": len(LP57OMEGA_HEMISPHERE_DOCS),
                "guild_hall_doc": str(LP57OMEGA_GUILD_HALL_DOC_PATH),
                "temple_doc": str(LP57OMEGA_TEMPLE_DOC_PATH),
            },
        )
    )

    dense_65_shell_rows = dense_65_shell_registry.get("rows", [])
    dense_65_witness_rows = dense_65_rqt_witness_registry.get("rows", [])
    dense_65_overflow_rows = dense_65_rqt_overflow_registry.get("overflow_rows", [])
    dense_65_abstention_rows = dense_65_rqt_overflow_registry.get("abstention_rows", [])
    dense_65_cell_summaries = dense_65_rqt_witness_registry.get("cell_summaries", [])
    dense_65_coordinate_lookup = {
        row.get("record_id"): row for row in lp57omega_coordinate_registry.get("rows", [])
    }
    authority_lookup = {row.get("record_id"): row for row in authority_records}
    dense_65_primary_counts = Counter(row.get("cell_id") for row in dense_65_witness_rows)
    dense_65_overflow_counts = Counter(row.get("cell_id") for row in dense_65_overflow_rows)
    dense_65_shell_family_counts = Counter(
        row.get("cell_family") for row in dense_65_shell_rows
    )
    dense_65_shell_ok = (
        dense_65_shell_registry.get("row_count") == 65
        and len(dense_65_shell_rows) == 65
        and dense_65_shell_registry.get("prior_seed_position") == DENSE_65_PRIOR_SEED_POSITION
        and dense_65_shell_registry.get("header_record_id") == "H00"
        and dense_65_shell_registry.get("group_counts") == DENSE_65_GROUP_COUNTS
        and dense_65_shell_family_counts == Counter(DENSE_65_GROUP_COUNTS)
        and dense_65_shell_rows[0].get("cell_id") == "H00"
        and dense_65_shell_rows[0].get("shell_position") == DENSE_65_PRIOR_SEED_POSITION
        and dense_65_shell_registry.get("sigma_path") == ["AppA", "AppI", "AppM"]
        and (dense_65_shell_registry.get("authority_refs") or {}).get("rotation_authority") == "AppF"
        and (dense_65_shell_registry.get("authority_refs") or {}).get("antispin_authority") == "AppG"
        and len(DENSE_65_R_ROWS) == 15
        and len(DENSE_65_Q_ROWS) == 15
        and len(DENSE_65_T_ROWS) == 15
        and all(
            row.get("dense_transfer_signature") and row.get("dense_metro_witness")
            for row in dense_65_shell_rows
            if row.get("cell_family") in {"R", "Q", "T"}
        )
    )
    checks.append(
        run_check(
            "dense_65_shell_registry",
            dense_65_shell_ok,
            {
                "row_count": dense_65_shell_registry.get("row_count"),
                "group_counts": dense_65_shell_registry.get("group_counts"),
            },
        )
    )

    dense_65_witness_violations = []
    for row in dense_65_witness_rows:
        record_id = row.get("record_id")
        authority_row = authority_lookup.get(record_id)
        coordinate_row = dense_65_coordinate_lookup.get(record_id)
        embedded_routes = (authority_row or {}).get("hemisphere_routes") or {}
        primary_side = row.get("primary_hemisphere") or "MATH"
        secondary_side = "MYTH" if primary_side == "MATH" else "MATH"
        primary_route = embedded_routes.get(primary_side) or {}
        secondary_route = embedded_routes.get(secondary_side) or {}
        transfer = row.get("z_star_aether_transfer_signature") or {}
        prior_witness = row.get("prior_metro_route_witness") or {}
        counter_witness = row.get("counter_route_witness") or {}
        opposite_pairs = {("A", "B"), ("C", "D")}
        expected_tunnel_required = any(
            left in (row.get("pole_set") or []) and right in (row.get("pole_set") or [])
            for left, right in opposite_pairs
        )
        expected_zstar_mode = (
            "zstar_tunnel"
            if row.get("cell_family") == "R" and expected_tunnel_required
            else "adjacent_bridge"
            if row.get("cell_family") == "R"
            else "order_4_orbit_with_zstar"
            if row.get("cell_family") == "Q" and expected_tunnel_required
            else "order_4_orbit"
            if row.get("cell_family") == "Q"
            else "order_3_antispin_with_zstar"
            if expected_tunnel_required
            else "order_3_antispin"
        )
        if not authority_row or not primary_route or not secondary_route or not coordinate_row:
            dense_65_witness_violations.append(
                {
                    "record_id": record_id,
                    "cell_id": row.get("cell_id"),
                    "reason": "missing_authority_route_or_coordinate",
                }
            )
            continue
        if (
            row.get("lp57_lookup_address") != coordinate_row.get("lookup_address")
            or set((coordinate_row.get("coordinate_tuple") or {}).keys()) != set(LP57OMEGA_COORDINATE_DIMENSIONS)
        ):
            dense_65_witness_violations.append(
                {
                    "record_id": record_id,
                    "cell_id": row.get("cell_id"),
                    "reason": "lp57_lookup_mismatch",
                }
            )
            continue
        if (
            not row.get("dense_kernel_ref")
            or (row.get("dense_kernel_ref") or {}).get("kernel_record_id") != row.get("cell_id")
            or (row.get("dense_kernel_ref") or {}).get("sigma_path") != ["AppA", "AppI", "AppM"]
        ):
            dense_65_witness_violations.append(
                {
                    "record_id": record_id,
                    "cell_id": row.get("cell_id"),
                    "reason": "dense_kernel_ref_missing_or_mismatch",
                }
            )
            continue
        expected_hide = canonical_hide_pole(list(row.get("pole_set") or []))
        if row.get("cell_family") == "T" and row.get("hide_pole") != expected_hide:
            dense_65_witness_violations.append(
                {
                    "record_id": record_id,
                    "cell_id": row.get("cell_id"),
                    "reason": "hide_pole_rule",
                    "expected": expected_hide,
                    "actual": row.get("hide_pole"),
                }
            )
            continue
        if (
            transfer.get("zpoint_id") != primary_route.get("zpoint_id")
            or transfer.get("field_id") != primary_route.get("field_id")
            or transfer.get("geodesic_mode") != primary_route.get("geodesic_mode")
            or transfer.get("aether_density") != (primary_route.get("aether_point") or {}).get("aether_density")
            or transfer.get("zero_proximity") != (primary_route.get("aether_point") or {}).get("zero_proximity")
            or transfer.get("tunnel_cost") != (primary_route.get("aether_point") or {}).get("tunnel_cost")
            or transfer.get("rail_hardness") != (primary_route.get("aether_point") or {}).get("rail_hardness")
            or transfer.get("resonance_pressure") != (primary_route.get("aether_point") or {}).get("resonance_pressure")
            or transfer.get("repair_gain") != (primary_route.get("aether_point") or {}).get("repair_gain")
            or transfer.get("record_id") != row.get("cell_id")
            or transfer.get("zstar_mode") != expected_zstar_mode
            or transfer.get("sigma_path") != ["AppA", "AppI", "AppM"]
            or transfer.get("rotation_authority") != "AppF"
            or transfer.get("antispin_authority") != "AppG"
            or transfer.get("tunnel_required") != expected_tunnel_required
            or (transfer.get("aether_binding") or {}).get("sigma_path") != ["AppA", "AppI", "AppM"]
        ):
            dense_65_witness_violations.append(
                {
                    "record_id": record_id,
                    "cell_id": row.get("cell_id"),
                    "reason": "z_transfer_mismatch",
                }
            )
            continue
        expected_prior = {
            "witness_side": primary_side,
            "route_id": primary_route.get("route_id"),
            "prior_route_class": "record_matched_route",
            "prior_route_path": ["AppA", "AppI", "AppM"],
            "grand_central_exchange": primary_route.get("grand_central_exchange"),
            "origin_system": primary_route.get("origin_system"),
            "target_system": primary_route.get("target_system"),
            "station_path": primary_route.get("station_path"),
            "interlock_ids": primary_route.get("interlock_ids"),
            "return_path": primary_route.get("return_path"),
            "metro_line_ids": primary_route.get("metro_line_ids"),
            "root_station_address": primary_route.get("root_station_address"),
            "rail3": primary_route.get("rail3"),
            "dominant_lens_system": primary_route.get("dominant_lens_system"),
            "appendix_support": primary_route.get("appendix_support"),
            "appf_rotation_ref": "AppF",
            "appg_antispin_ref": "AppG",
            "appi_truth_ref": "AppI",
            "appm_replay_ref": "AppM",
            "truth_state": primary_route.get("truth_state") or primary_route.get("proof_state") or "UNKNOWN",
        }
        expected_counter = {
            "witness_side": secondary_side,
            "route_id": secondary_route.get("route_id"),
            "prior_route_class": "record_matched_route",
            "prior_route_path": ["AppA", "AppI", "AppM"],
            "grand_central_exchange": secondary_route.get("grand_central_exchange"),
            "origin_system": secondary_route.get("origin_system"),
            "target_system": secondary_route.get("target_system"),
            "station_path": secondary_route.get("station_path"),
            "interlock_ids": secondary_route.get("interlock_ids"),
            "return_path": secondary_route.get("return_path"),
            "metro_line_ids": secondary_route.get("metro_line_ids"),
            "root_station_address": secondary_route.get("root_station_address"),
            "rail3": secondary_route.get("rail3"),
            "dominant_lens_system": secondary_route.get("dominant_lens_system"),
            "appendix_support": secondary_route.get("appendix_support"),
            "appf_rotation_ref": "AppF",
            "appg_antispin_ref": "AppG",
            "appi_truth_ref": "AppI",
            "appm_replay_ref": "AppM",
            "truth_state": secondary_route.get("truth_state") or secondary_route.get("proof_state") or "UNKNOWN",
        }
        if (
            prior_witness != expected_prior
            or counter_witness != expected_counter
            or row.get("dense_metro_witness") != prior_witness
            or row.get("dense_transfer_signature") != transfer
        ):
            dense_65_witness_violations.append(
                {
                    "record_id": record_id,
                    "cell_id": row.get("cell_id"),
                    "reason": "route_witness_mismatch",
                }
            )
            continue
        if row.get("cell_family") == "R":
            expected_row = next(item for item in DENSE_65_R_ROWS if item["cell_id"] == row.get("cell_id"))
            if row.get("rot_plus_set") != expected_row.get("rot_plus_set") or row.get("rot_minus_set") != expected_row.get("rot_minus_set"):
                dense_65_witness_violations.append(
                    {
                        "record_id": record_id,
                        "cell_id": row.get("cell_id"),
                        "reason": "r_overlay_mismatch",
                    }
                )
        elif row.get("cell_family") == "Q":
            expected_row = next(item for item in DENSE_65_Q_ROWS if item["cell_id"] == row.get("cell_id"))
            if row.get("base4_orbit") != expected_row.get("base4_orbit"):
                dense_65_witness_violations.append(
                    {
                        "record_id": record_id,
                        "cell_id": row.get("cell_id"),
                        "reason": "q_overlay_mismatch",
                    }
                )
        elif row.get("cell_family") == "T":
            expected_row = next(item for item in DENSE_65_T_ROWS if item["cell_id"] == row.get("cell_id"))
            if (
                row.get("triad_set") != expected_row.get("triad_set")
                or row.get("anti_plus_orbit") != expected_row.get("anti_plus_orbit")
                or row.get("anti_minus_orbit") != expected_row.get("anti_minus_orbit")
                or (row.get("rail_antispin_lock") or {}).get("lock_mode") != "order_3_antispin"
            ):
                dense_65_witness_violations.append(
                    {
                        "record_id": record_id,
                        "cell_id": row.get("cell_id"),
                        "reason": "t_overlay_mismatch",
                    }
                )
    dense_65_primary_cap_ok = (
        all(count <= DENSE_65_PRIMARY_CAP for count in dense_65_primary_counts.values())
        and dense_65_rqt_witness_registry.get("primary_cap_per_cell") == DENSE_65_PRIMARY_CAP
        and all(
            summary.get("primary_count") == dense_65_primary_counts.get(summary.get("cell_id"), 0)
            and summary.get("overflow_count") == dense_65_overflow_counts.get(summary.get("cell_id"), 0)
            for summary in dense_65_cell_summaries
        )
    )
    dense_65_overflow_ok = all(
        row.get("overflow_reason") == "capacity" for row in dense_65_overflow_rows
    )
    dense_65_abstention_ok = all(
        row.get("overflow_reason") in {"no_elemental_pole_evidence", "missing_cell_mapping_or_coordinate"}
        for row in dense_65_abstention_rows
    )
    checks.append(
        run_check(
            "dense_65_rqt_witness_registry",
            not dense_65_witness_violations and dense_65_primary_cap_ok and dense_65_overflow_ok and dense_65_abstention_ok,
            {
                "row_count": dense_65_rqt_witness_registry.get("row_count"),
                "violations": dense_65_witness_violations[:20],
                "zero_witness_cells": dense_65_manifest.get("coverage", {}).get("zero_witness_cells", []),
            },
        )
    )

    dense_65_docs_gate_ok = all(
        payload.get("docs_gate_status") == live_docs_status
        for payload in (
            dense_65_shell_registry,
            dense_65_rqt_witness_registry,
            dense_65_rqt_overflow_registry,
            dense_65_manifest,
        )
    )
    checks.append(
        run_check(
            "dense_65_docs_gate_propagation",
            dense_65_docs_gate_ok,
            {
                "shell": dense_65_shell_registry.get("docs_gate_status"),
                "manifest": dense_65_manifest.get("docs_gate_status"),
                "live_docs_gate": live_docs_status,
            },
        )
    )

    mirror_dense_65_shell = load_json(FLEET_MIRROR_ROOT / DENSE_65_SHELL_REGISTRY_PATH.name)
    mirror_dense_65_witness = load_json(FLEET_MIRROR_ROOT / DENSE_65_RQT_WITNESS_REGISTRY_PATH.name)
    mirror_dense_65_overflow = load_json(FLEET_MIRROR_ROOT / DENSE_65_RQT_OVERFLOW_REGISTRY_PATH.name)
    mirror_dense_65_manifest = load_json(FLEET_MIRROR_ROOT / DENSE_65_MANIFEST_PATH.name)
    dense_65_mirror_ok = (
        mirror_dense_65_shell.get("row_count") == dense_65_shell_registry.get("row_count")
        and mirror_dense_65_witness.get("row_count") == dense_65_rqt_witness_registry.get("row_count")
        and mirror_dense_65_overflow.get("overflow_count") == dense_65_rqt_overflow_registry.get("overflow_count")
        and mirror_dense_65_manifest.get("counts") == dense_65_manifest.get("counts")
    )
    checks.append(
        run_check(
            "dense_65_fleet_mirror_consistency",
            dense_65_mirror_ok,
            {
                "canonical_shell_rows": dense_65_shell_registry.get("row_count"),
                "mirror_shell_rows": mirror_dense_65_shell.get("row_count"),
                "canonical_primary_rows": dense_65_rqt_witness_registry.get("row_count"),
                "mirror_primary_rows": mirror_dense_65_witness.get("row_count"),
            },
        )
    )

    dense_65_surface_exists = all(path.is_file() for path in DENSE_65_HEMISPHERE_DOCS.values()) and all(
        (FLEET_MIRROR_ROOT / path.name).is_file() for path in DENSE_65_HEMISPHERE_DOCS.values()
    )
    checks.append(
        run_check(
            "dense_65_surface_existence",
            dense_65_surface_exists,
            {
                "hemisphere_docs": len(DENSE_65_HEMISPHERE_DOCS),
                "primary_cap": DENSE_65_PRIMARY_CAP,
            },
        )
    )

    command_membrane_schema_ok = (
        command_membrane_packet_schema.get("packet_fields") == COMMAND_MEMBRANE_PACKET_FIELDS
        and command_membrane_packet_schema.get("latency_metrics") == COMMAND_MEMBRANE_LATENCY_METRICS
        and command_membrane_packet_schema.get("ant_classes") == COMMAND_MEMBRANE_ANT_CLASSES
        and command_membrane_packet_schema.get("routing_defaults", {}).get("policy")
        == COMMAND_MEMBRANE_ROUTE_POLICY
        and command_membrane_packet_schema.get("routing_defaults", {}).get("topk")
        == COMMAND_MEMBRANE_PUBLIC_TOPK
        and command_membrane_packet_schema.get("routing_defaults", {}).get("ttl")
        == COMMAND_MEMBRANE_TTL
        and command_membrane_packet_schema.get("routing_defaults", {}).get("route_class")
        == COMMAND_MEMBRANE_ROUTE_CLASS
        and command_membrane_packet_schema.get("capillary_law", {}).get("coefficients")
        == COMMAND_MEMBRANE_CAPILLARY_COEFFICIENTS
        and command_membrane_packet_schema.get("capillary_law", {}).get("thresholds")
        == COMMAND_MEMBRANE_VESSEL_THRESHOLDS
        and tuple(command_membrane_packet_schema.get("watched_source_ids", ()))
        == COMMAND_MEMBRANE_EXPECTED_SOURCE_IDS
        and command_membrane_packet_schema.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "command_membrane_packet_schema",
            command_membrane_schema_ok,
            {
                "field_count": len(command_membrane_packet_schema.get("packet_fields", [])),
                "ant_classes": command_membrane_packet_schema.get("ant_classes"),
                "route_policy": command_membrane_packet_schema.get("routing_defaults", {}).get("policy"),
            },
        )
    )

    authority_lookup = {row.get("record_id"): row for row in authority_records}
    lp57_coordinate_lookup = {row.get("record_id"): row for row in lp57omega_coordinate_rows}
    dual_route_id_lookup = {
        row.get("route_id"): row for row in dual_route_registry.get("routes", []) if row.get("route_id")
    }
    watched_surface_rows = command_membrane_watched_surface_registry.get("rows", [])
    watched_surface_ids = [row.get("source_id") for row in watched_surface_rows]
    watched_surface_violations = []
    for row in watched_surface_rows:
        if row.get("source_id") not in COMMAND_MEMBRANE_EXPECTED_SOURCE_IDS:
            watched_surface_violations.append({"source_id": row.get("source_id"), "reason": "unexpected_source"})
        if row.get("docs_gate_status") != live_docs_status:
            watched_surface_violations.append({"source_id": row.get("source_id"), "reason": "docs_gate_mismatch"})
        if not row.get("absolute_path") or not row.get("source_class"):
            watched_surface_violations.append({"source_id": row.get("source_id"), "reason": "missing_surface_fields"})
    watched_surface_ok = (
        command_membrane_watched_surface_registry.get("source_count") == len(watched_surface_rows)
        and tuple(sorted(watched_surface_ids)) == tuple(sorted(COMMAND_MEMBRANE_EXPECTED_SOURCE_IDS))
        and not watched_surface_violations
    )
    checks.append(
        run_check(
            "command_membrane_watched_surface_registry",
            watched_surface_ok,
            {
                "source_count": command_membrane_watched_surface_registry.get("source_count"),
                "expected_sources": list(COMMAND_MEMBRANE_EXPECTED_SOURCE_IDS),
                "violations": watched_surface_violations[:20],
            },
        )
    )

    command_event_rows = command_membrane_event_registry.get("rows", [])
    command_event_violations = []
    for row in command_event_rows:
        if not set(COMMAND_MEMBRANE_PACKET_FIELDS).issubset(row):
            command_event_violations.append({"event_id": row.get("event_id"), "reason": "missing_packet_fields"})
            continue
        latency = row.get("latency_metrics") or {}
        if any(metric not in latency for metric in COMMAND_MEMBRANE_LATENCY_METRICS):
            command_event_violations.append({"event_id": row.get("event_id"), "reason": "missing_latency_metrics"})
        if (
            row.get("routing_policy") != COMMAND_MEMBRANE_ROUTE_POLICY
            or row.get("route_class") != COMMAND_MEMBRANE_ROUTE_CLASS
            or row.get("topk") != COMMAND_MEMBRANE_PUBLIC_TOPK
            or row.get("ttl") != COMMAND_MEMBRANE_TTL
            or row.get("docs_gate_status") != live_docs_status
        ):
            command_event_violations.append({"event_id": row.get("event_id"), "reason": "routing_defaults_mismatch"})
        if not row.get("source_id") or not row.get("source_class") or not row.get("event_fingerprint"):
            command_event_violations.append({"event_id": row.get("event_id"), "reason": "missing_source_fields"})
        match_state = row.get("match_state")
        record_id = row.get("record_id")
        if match_state == "canonical_match":
            authority_row = authority_lookup.get(record_id)
            coordinate_row = lp57_coordinate_lookup.get(record_id)
            primary_route = row.get("prior_metro_route_witness") or {}
            secondary_route = row.get("counter_route_witness") or {}
            if authority_row is None or coordinate_row is None:
                command_event_violations.append({"event_id": row.get("event_id"), "reason": "missing_canonical_link"})
            elif (
                row.get("lp57_lookup_address") != coordinate_row.get("lookup_address")
                or row.get("coordinate_tuple") != coordinate_row.get("coordinate_tuple")
            ):
                command_event_violations.append({"event_id": row.get("event_id"), "reason": "coordinate_mismatch"})
            if primary_route.get("route_id") not in dual_route_id_lookup:
                command_event_violations.append({"event_id": row.get("event_id"), "reason": "missing_primary_route"})
            if secondary_route and secondary_route.get("route_id") not in dual_route_id_lookup:
                command_event_violations.append({"event_id": row.get("event_id"), "reason": "missing_secondary_route"})
        elif match_state != "fallback_live_anchor":
            command_event_violations.append({"event_id": row.get("event_id"), "reason": "invalid_match_state"})

    command_event_ok = (
        command_membrane_event_registry.get("event_count") == len(command_event_rows)
        and command_membrane_event_registry.get("matched_event_count")
        + command_membrane_event_registry.get("fallback_event_count")
        == len(command_event_rows)
        and not command_event_violations
    )
    checks.append(
        run_check(
            "command_membrane_event_registry",
            command_event_ok,
            {
                "event_count": command_membrane_event_registry.get("event_count"),
                "matched_event_count": command_membrane_event_registry.get("matched_event_count"),
                "fallback_event_count": command_membrane_event_registry.get("fallback_event_count"),
                "violations": command_event_violations[:20],
            },
        )
    )

    claim_event_ids = {row.get("event_id") for row in command_event_rows}
    command_claim_rows = command_membrane_claim_ledger.get("rows", [])
    command_claim_violations = []
    for row in command_claim_rows:
        if not set(COMMAND_MEMBRANE_CLAIM_FIELDS).issubset(row):
            command_claim_violations.append({"claim_id": row.get("claim_id"), "reason": "missing_claim_fields"})
            continue
        if row.get("event_id") not in claim_event_ids:
            command_claim_violations.append({"claim_id": row.get("claim_id"), "reason": "missing_event"})
        if not row.get("front_ref"):
            command_claim_violations.append({"claim_id": row.get("claim_id"), "reason": "missing_front_ref"})
        if not row.get("route_class"):
            command_claim_violations.append({"claim_id": row.get("claim_id"), "reason": "missing_route_class"})
        if row.get("docs_gate_status") != live_docs_status:
            command_claim_violations.append({"claim_id": row.get("claim_id"), "reason": "docs_gate_mismatch"})
    command_claim_ok = (
        command_membrane_claim_ledger.get("row_count") == len(command_claim_rows)
        and not command_claim_violations
        and command_membrane_claim_ledger.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "command_membrane_claim_ledger",
            command_claim_ok,
            {
                "row_count": command_membrane_claim_ledger.get("row_count"),
                "active_count": command_membrane_claim_ledger.get("active_count"),
                "violations": command_claim_violations[:20],
            },
        )
    )

    command_capillary_rows = command_membrane_capillary_registry.get("rows", [])
    command_capillary_violations = []
    for row in command_capillary_rows:
        strength = float(row.get("next_strength") or row.get("edge_strength") or 0.0)
        if row.get("coefficients") != COMMAND_MEMBRANE_CAPILLARY_COEFFICIENTS:
            command_capillary_violations.append({"edge_id": row.get("edge_id"), "reason": "coefficients_mismatch"})
            continue
        if strength >= COMMAND_MEMBRANE_VESSEL_THRESHOLDS["vein"]:
            expected_class = "vein"
        elif strength >= COMMAND_MEMBRANE_VESSEL_THRESHOLDS["capillary"]:
            expected_class = "capillary"
        elif strength >= COMMAND_MEMBRANE_VESSEL_THRESHOLDS["candidate"]:
            expected_class = "candidate"
        else:
            expected_class = "latent"
        if row.get("vessel_class") not in {expected_class, "dormant", "route"}:
            command_capillary_violations.append({"edge_id": row.get("edge_id"), "reason": "vessel_class_mismatch"})
        if row.get("docs_gate_status") != live_docs_status:
            command_capillary_violations.append({"edge_id": row.get("edge_id"), "reason": "docs_gate_mismatch"})
    command_capillary_ok = (
        command_membrane_capillary_registry.get("edge_count") == len(command_capillary_rows)
        and not command_capillary_violations
        and command_membrane_capillary_registry.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "command_membrane_capillary_registry",
            command_capillary_ok,
            {
                "edge_count": command_membrane_capillary_registry.get("edge_count"),
                "violations": command_capillary_violations[:20],
            },
        )
    )

    command_latency_rows = command_membrane_latency_registry.get("rows", [])
    command_latency_violations = []
    for row in command_latency_rows:
        if row.get("event_id") not in claim_event_ids:
            command_latency_violations.append({"event_id": row.get("event_id"), "reason": "missing_event"})
        if row.get("docs_gate_status") != live_docs_status:
            command_latency_violations.append({"event_id": row.get("event_id"), "reason": "docs_gate_mismatch"})
    command_latency_ok = (
        command_membrane_latency_registry.get("row_count") == len(command_latency_rows)
        and not command_latency_violations
        and command_membrane_latency_registry.get("docs_gate_status") == live_docs_status
    )
    checks.append(
        run_check(
            "command_membrane_latency_registry",
            command_latency_ok,
            {
                "row_count": command_membrane_latency_registry.get("row_count"),
                "violations": command_latency_violations[:20],
            },
        )
    )

    command_membrane_docs_gate_ok = all(
        payload.get("docs_gate_status") == live_docs_status
        for payload in (
            command_membrane_packet_schema,
            command_membrane_watched_surface_registry,
            command_membrane_event_registry,
            command_membrane_claim_ledger,
            command_membrane_capillary_registry,
            command_membrane_latency_registry,
            command_membrane_manifest,
        )
    )
    checks.append(
        run_check(
            "command_membrane_docs_gate_propagation",
            command_membrane_docs_gate_ok,
            {
                "event_registry": command_membrane_event_registry.get("docs_gate_status"),
                "manifest": command_membrane_manifest.get("docs_gate_status"),
                "live_docs_gate": live_docs_status,
            },
        )
    )

    mirror_command_membrane_packet_schema = load_json(
        FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_PACKET_SCHEMA_PATH.name
    )
    mirror_command_membrane_watched_surface_registry = load_json(
        FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH.name
    )
    mirror_command_membrane_event_registry = load_json(
        FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_EVENT_REGISTRY_PATH.name
    )
    mirror_command_membrane_claim_ledger = load_json(
        FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_CLAIM_LEDGER_PATH.name
    )
    mirror_command_membrane_capillary_registry = load_json(
        FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH.name
    )
    mirror_command_membrane_latency_registry = load_json(
        FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH.name
    )
    mirror_command_membrane_manifest = load_json(
        FLEET_MIRROR_ROOT / COMMAND_MEMBRANE_MANIFEST_PATH.name
    )
    command_membrane_mirror_ok = (
        mirror_command_membrane_packet_schema.get("packet_fields")
        == command_membrane_packet_schema.get("packet_fields")
        and mirror_command_membrane_watched_surface_registry.get("source_count")
        == command_membrane_watched_surface_registry.get("source_count")
        and mirror_command_membrane_event_registry.get("event_count")
        == command_membrane_event_registry.get("event_count")
        and mirror_command_membrane_claim_ledger.get("row_count")
        == command_membrane_claim_ledger.get("row_count")
        and mirror_command_membrane_capillary_registry.get("edge_count")
        == command_membrane_capillary_registry.get("edge_count")
        and mirror_command_membrane_latency_registry.get("row_count")
        == command_membrane_latency_registry.get("row_count")
        and mirror_command_membrane_manifest.get("counts")
        == command_membrane_manifest.get("counts")
    )
    checks.append(
        run_check(
            "command_membrane_fleet_mirror_consistency",
            command_membrane_mirror_ok,
            {
                "canonical_sources": command_membrane_watched_surface_registry.get("source_count"),
                "mirror_sources": mirror_command_membrane_watched_surface_registry.get("source_count"),
                "canonical_events": command_membrane_event_registry.get("event_count"),
                "mirror_events": mirror_command_membrane_event_registry.get("event_count"),
                "canonical_claims": command_membrane_claim_ledger.get("row_count"),
                "mirror_claims": mirror_command_membrane_claim_ledger.get("row_count"),
                "canonical_edges": command_membrane_capillary_registry.get("edge_count"),
                "mirror_edges": mirror_command_membrane_capillary_registry.get("edge_count"),
                "canonical_latency": command_membrane_latency_registry.get("row_count"),
                "mirror_latency": mirror_command_membrane_latency_registry.get("row_count"),
            },
        )
    )

    command_membrane_surface_exists = all(
        path.is_file() for path in COMMAND_MEMBRANE_HEMISPHERE_DOCS.values()
    ) and all((FLEET_MIRROR_ROOT / path.name).is_file() for path in COMMAND_MEMBRANE_HEMISPHERE_DOCS.values())
    checks.append(
        run_check(
            "command_membrane_surface_existence",
            command_membrane_surface_exists,
            {
                "hemisphere_docs": len(COMMAND_MEMBRANE_HEMISPHERE_DOCS),
                "event_count": command_membrane_event_registry.get("event_count"),
            },
        )
    )

    failed = [check for check in checks if check["status"] != "OK"]
    return {
        "generated_at": manifest.get("generated_at"),
        "verification_command": VERIFY_COMMAND,
        "truth": "OK" if not failed else "NEAR",
        "check_count": len(checks),
        "failed_checks": [check["label"] for check in failed],
        "checks": checks,
    }


def main() -> int:
    payload = verify_payload()
    write_json(VERIFY_PATH, payload)
    print(f"Wrote hemisphere verification: {VERIFY_PATH}")
    print(f"Truth: {payload['truth']}")
    for check in payload["checks"]:
        print(f"- {check['label']}: {check['status']}")
    return 0 if payload["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
