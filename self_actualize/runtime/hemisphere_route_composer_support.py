from __future__ import annotations

from collections import defaultdict
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    COMMISSURE_REGISTRY_PATH,
    COMPOSER_FACET_REGISTRY_PATH,
    COMPOSER_MANIFEST_PATH,
    COMPOSER_SEED_REGISTRY_PATH,
    DIRECT_EDGE_REGISTRY_PATH,
    DUAL_ROUTE_REGISTRY_PATH,
    MANIFEST_PATH,
    MATH_HUB_ID,
    MYTH_HUB_ID,
    NAVIGATOR_ALIAS_INDEX_PATH,
    NAVIGATOR_FACET_INDEX_PATH,
    NAVIGATOR_MANIFEST_PATH,
    NAVIGATOR_NEIGHBOR_INDEX_PATH,
    RECORD_REGISTRY_PATH,
    UNIFIED_HUB_ID,
    load_json,
    utc_now,
)
from self_actualize.runtime.hemisphere_navigator_query_engine import (
    SEARCH_FILTER_TO_FACET,
    ensure_runtime as ensure_navigator_runtime,
    facet as navigator_facet_query,
    load_navigator_registries,
    record as navigator_record_query,
    search as navigator_search_query,
    summarize_record,
)


ROUTE_STAGE_ORDER = [
    "seed",
    "anchor_lift",
    "corridor_lift",
    "system_lift",
    "hemisphere_hub",
    "exit",
]
STARTER_CAP = 24
STARTER_FACETS = ("anchor", "family", "target_system", "hemisphere")


def opposite_hemisphere(hemisphere: str) -> str:
    return "MYTH" if hemisphere == "MATH" else "MATH"


def route_header(route_packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "route_id": route_packet.get("route_id", ""),
        "hemisphere": route_packet.get("hemisphere", ""),
        "route_role": route_packet.get("route_role", ""),
        "route_mode": route_packet.get("route_mode", ""),
        "chapter_station": route_packet.get("chapter_station", ""),
        "local_addr": route_packet.get("local_addr", ""),
        "global_addr": route_packet.get("global_addr", ""),
        "tesseract_header": route_packet.get("tesseract_header", ""),
        "truth_state": route_packet.get("truth_state", ""),
        "target_system": route_packet.get("target_system", ""),
        "proof_state": route_packet.get("proof_state", ""),
        "field_id": route_packet.get("field_id", ""),
        "zpoint_id": route_packet.get("zpoint_id", ""),
        "preferred_space": route_packet.get("preferred_space", ""),
        "appendix_support": list(route_packet.get("appendix_support", [])),
        "appendix_support_sources": route_packet.get("appendix_support_sources", {}),
        "hubs_seq": list(route_packet.get("hubs_seq", [])),
        "tunnel_plan": route_packet.get("tunnel_plan", {}),
        "primary_hubs_text": route_packet.get("primary_hubs_text", ""),
        "tunnel_text": route_packet.get("tunnel_text", ""),
        "truth_state_text": route_packet.get("truth_state_text", ""),
        "hcrl_text": route_packet.get("hcrl_text", {}),
        "dominant_lens_system": route_packet.get("dominant_lens_system", ""),
        "basis_anchor_ids": route_packet.get("basis_anchor_ids", []),
    }


def load_route_composer_registries() -> dict[str, Any]:
    registries = load_navigator_registries()
    registries["commissure_registry"] = load_json(COMMISSURE_REGISTRY_PATH)
    if COMPOSER_SEED_REGISTRY_PATH.exists():
        registries["composer_seed_registry"] = load_json(COMPOSER_SEED_REGISTRY_PATH)
    if COMPOSER_FACET_REGISTRY_PATH.exists():
        registries["composer_facet_registry"] = load_json(COMPOSER_FACET_REGISTRY_PATH)
    if COMPOSER_MANIFEST_PATH.exists():
        registries["composer_manifest"] = load_json(COMPOSER_MANIFEST_PATH)
    return registries


def ensure_composer_runtime(registries: dict[str, Any]) -> dict[str, Any]:
    runtime = registries.get("_composer_runtime")
    if runtime is not None:
        return runtime

    navigator_runtime = ensure_navigator_runtime(registries)
    commissure_lookup: dict[str, list[str]] = defaultdict(list)
    for edge in registries.get("commissure_registry", {}).get("edges", []):
        commissure_lookup[edge["record_id"]].append(edge["edge_id"])

    runtime = {
        "navigator": navigator_runtime,
        "commissure_lookup": dict(commissure_lookup),
        "docs_gate_status": navigator_runtime["docs_gate_status"],
    }
    registries["_composer_runtime"] = runtime
    return runtime


def record_stop(
    runtime: dict[str, Any],
    record_id: str,
    stage: str,
    hemisphere: str,
) -> dict[str, Any]:
    nav = runtime["navigator"]
    record = nav["record_map"][record_id]
    routes = nav["route_lookup"][record_id]
    return {
        "stage": stage,
        "kind": "record_stop",
        "hemisphere": hemisphere,
        "record": summarize_record(record),
        "selected_route": routes[hemisphere],
        "paired_routes": {
            "MATH": routes["MATH"],
            "MYTH": routes["MYTH"],
        },
        "direct_edges": nav["edge_lookup"][record_id],
    }


def empty_stage(stage: str, hemisphere: str, reason: str) -> dict[str, Any]:
    return {
        "stage": stage,
        "kind": "empty",
        "hemisphere": hemisphere,
        "reason": reason,
    }


def hub_stage(runtime: dict[str, Any], record_id: str, hemisphere: str) -> dict[str, Any]:
    edge = runtime["navigator"]["edge_lookup"][record_id][hemisphere]
    return {
        "stage": "hemisphere_hub",
        "kind": "hub_stop",
        "hemisphere": hemisphere,
        "hub_id": MATH_HUB_ID if hemisphere == "MATH" else MYTH_HUB_ID,
        "grand_central_exchange": edge.get("grand_central_exchange", ""),
        "target_system": edge.get("target_system", ""),
        "proof_state": edge.get("proof_state", ""),
        "edge": edge,
    }


def exit_stage(seed_record: dict[str, Any], route_packet: dict[str, Any], hemisphere: str) -> dict[str, Any]:
    return {
        "stage": "exit",
        "kind": "exit",
        "hemisphere": hemisphere,
        "return_path": route_packet.get("return_path", []),
        "pt2_shortcut_id": route_packet.get("pt2_shortcut_id", ""),
        "knowledge_fabric_shortcut_id": route_packet.get("knowledge_fabric_shortcut_id", ""),
        "preferred_space": route_packet.get("preferred_space", ""),
        "supported_spaces": route_packet.get("supported_spaces", []),
        "appendix_support": seed_record.get("appendix_support", []),
        "proof_state": route_packet.get("proof_state", ""),
        "docs_gate_status": route_packet.get("docs_gate_status", ""),
    }


def first_unused_record_id(bundle: dict[str, Any], used_ids: set[str]) -> str | None:
    for record_id in bundle.get("record_ids", []):
        if record_id not in used_ids:
            return record_id
    return None


def itinerary_bundle_key(seed_record: dict[str, Any], hemisphere: str) -> str:
    if hemisphere == seed_record.get("primary_hemisphere"):
        return "same_primary_target"
    return "same_secondary_target"


def compose_itinerary(
    runtime: dict[str, Any],
    seed_record: dict[str, Any],
    hemisphere: str,
) -> dict[str, Any]:
    nav = runtime["navigator"]
    seed_id = seed_record["record_id"]
    used_ids = {seed_id}
    neighbor_entry = nav["neighbor_lookup"].get(seed_id, {})
    seed_routes = nav["route_lookup"][seed_id]
    stages: list[dict[str, Any]] = []

    stages.append(record_stop(runtime, seed_id, "seed", hemisphere))

    anchor_record_id = first_unused_record_id(neighbor_entry.get("same_anchor", {}), used_ids)
    if anchor_record_id is None:
        stages.append(empty_stage("anchor_lift", hemisphere, "no_unused_same_anchor_candidate"))
    else:
        used_ids.add(anchor_record_id)
        stages.append(record_stop(runtime, anchor_record_id, "anchor_lift", hemisphere))

    corridor_record_id = first_unused_record_id(neighbor_entry.get("same_corridor", {}), used_ids)
    if corridor_record_id is None:
        stages.append(empty_stage("corridor_lift", hemisphere, "no_unused_same_corridor_candidate"))
    else:
        used_ids.add(corridor_record_id)
        stages.append(record_stop(runtime, corridor_record_id, "corridor_lift", hemisphere))

    system_bundle = neighbor_entry.get(itinerary_bundle_key(seed_record, hemisphere), {})
    system_record_id = first_unused_record_id(system_bundle, used_ids)
    if system_record_id is None:
        stages.append(empty_stage("system_lift", hemisphere, "no_unused_same_system_candidate"))
    else:
        used_ids.add(system_record_id)
        stages.append(record_stop(runtime, system_record_id, "system_lift", hemisphere))

    stages.append(hub_stage(runtime, seed_id, hemisphere))
    stages.append(exit_stage(seed_record, seed_routes[hemisphere], hemisphere))

    return {
        "hemisphere": hemisphere,
        "stage_order": ROUTE_STAGE_ORDER,
        "stages": stages,
    }


def compose_shared_spine(runtime: dict[str, Any], seed_record: dict[str, Any]) -> dict[str, Any]:
    source_hemisphere = seed_record.get("primary_hemisphere", "MATH")
    source_hub = MATH_HUB_ID if source_hemisphere == "MATH" else MYTH_HUB_ID
    opposite_hub = MYTH_HUB_ID if source_hub == MATH_HUB_ID else MATH_HUB_ID
    return {
        "source_hemisphere": source_hemisphere,
        "source_hub_id": source_hub,
        "target_hub_id": opposite_hub,
        "sequence": [
            {
                "kind": "record_seed",
                "record": summarize_record(seed_record),
            },
            {
                "kind": "hub",
                "hub_id": source_hub,
            },
            {
                "kind": "hub",
                "hub_id": UNIFIED_HUB_ID,
            },
            {
                "kind": "hub",
                "hub_id": opposite_hub,
            },
        ],
    }


def compose_bridge_profile(runtime: dict[str, Any], seed_record: dict[str, Any]) -> dict[str, Any]:
    record_id = seed_record["record_id"]
    direct_edges = runtime["navigator"]["edge_lookup"][record_id]
    direct_edge_ids = [direct_edges["MATH"]["edge_id"], direct_edges["MYTH"]["edge_id"]]
    if seed_record.get("bridge_class") == "commissure_bridge":
        return {
            "mode": "commissure_active",
            "commissure_edge_ids": runtime["commissure_lookup"].get(record_id, []),
            "direct_edge_ids": direct_edge_ids,
            "unified_hub_id": UNIFIED_HUB_ID,
        }
    return {
        "mode": "hub_transfer",
        "commissure_edge_ids": [],
        "direct_edge_ids": direct_edge_ids,
        "spine_hub_ids": [
            MATH_HUB_ID if seed_record.get("primary_hemisphere") == "MATH" else MYTH_HUB_ID,
            UNIFIED_HUB_ID,
            MYTH_HUB_ID if seed_record.get("primary_hemisphere") == "MATH" else MATH_HUB_ID,
        ],
    }


def compose_facet_context(
    seed_record: dict[str, Any],
    navigator_response: dict[str, Any],
) -> dict[str, Any]:
    facet_summary = navigator_response.get("facet_summary", {})
    return {
        "top_level": seed_record.get("top_level", ""),
        "family": seed_record.get("family", ""),
        "basis_anchor_ids": seed_record.get("basis_anchor_ids", []),
        "tract": seed_record.get("tract", ""),
        "matched_filters": facet_summary.get("matched_filters", []),
        "target_systems": facet_summary.get("target_systems", {}),
        "origin_systems": facet_summary.get("origin_systems", {}),
        "route_modes": facet_summary.get("route_modes", {}),
    }


def compose_proof_summary(runtime: dict[str, Any], seed_record: dict[str, Any]) -> dict[str, Any]:
    routes = runtime["navigator"]["route_lookup"][seed_record["record_id"]]
    edges = runtime["navigator"]["edge_lookup"][seed_record["record_id"]]
    return {
        "record_confidence": seed_record.get("confidence", 0.0),
        "bridge_class": seed_record.get("bridge_class", ""),
        "bridge_intensity": seed_record.get("bridge_intensity", 0.0),
        "route_proof_states": {
            hemisphere: route_packet.get("proof_state", "")
            for hemisphere, route_packet in routes.items()
        },
        "edge_proof_states": {
            hemisphere: edge_packet.get("proof_state", "")
            for hemisphere, edge_packet in edges.items()
        },
        "docs_gate_status": runtime["docs_gate_status"],
    }


def alternative_seed_payload(runtime: dict[str, Any], record_id: str) -> dict[str, Any]:
    nav = runtime["navigator"]
    record = nav["record_map"][record_id]
    routes = nav["route_lookup"][record_id]
    return {
        "seed_record": summarize_record(record),
        "route_headers": {
            "MATH": route_header(routes["MATH"]),
            "MYTH": route_header(routes["MYTH"]),
        },
    }


def compose_seed_record(
    registries: dict[str, Any],
    record_id: str,
    *,
    mode: str,
    query: dict[str, Any],
    navigator_response: dict[str, Any],
    alternative_record_ids: list[str] | None = None,
) -> dict[str, Any]:
    runtime = ensure_composer_runtime(registries)
    nav = runtime["navigator"]
    seed_record = nav["record_map"][record_id]
    payload = {
        "query": query,
        "mode": mode,
        "seed_record": summarize_record(seed_record),
        "math_itinerary": compose_itinerary(runtime, seed_record, "MATH"),
        "myth_itinerary": compose_itinerary(runtime, seed_record, "MYTH"),
        "shared_spine": compose_shared_spine(runtime, seed_record),
        "bridge_profile": compose_bridge_profile(runtime, seed_record),
        "facet_context": compose_facet_context(seed_record, navigator_response),
        "proof_summary": compose_proof_summary(runtime, seed_record),
        "docs_gate_status": runtime["docs_gate_status"],
    }
    if alternative_record_ids:
        payload["alternative_seeds"] = [
            alternative_seed_payload(runtime, alt_record_id)
            for alt_record_id in alternative_record_ids[:3]
            if alt_record_id in nav["record_map"]
        ]
    return payload


def extract_alternative_record_ids(navigator_response: dict[str, Any], seed_record_id: str) -> list[str]:
    alternatives: list[str] = []
    for candidate in navigator_response.get("candidates", []):
        record_id = candidate.get("record_id")
        if record_id and record_id != seed_record_id and record_id not in alternatives:
            alternatives.append(record_id)
    return alternatives


def compose_from_navigator_response(
    navigator_response: dict[str, Any],
    registries: dict[str, Any],
    *,
    mode: str,
    query: dict[str, Any],
    expanded: bool = False,
) -> dict[str, Any]:
    best_match = navigator_response.get("best_match") or {}
    seed_record_id = best_match.get("record_id")
    if not seed_record_id:
        return {
            "query": query,
            "mode": mode,
            "seed_record": None,
            "math_itinerary": {"hemisphere": "MATH", "stage_order": ROUTE_STAGE_ORDER, "stages": []},
            "myth_itinerary": {"hemisphere": "MYTH", "stage_order": ROUTE_STAGE_ORDER, "stages": []},
            "shared_spine": {"sequence": []},
            "bridge_profile": {"mode": "unresolved", "reason": "no_seed_record"},
            "facet_context": {
                "matched_filters": navigator_response.get("facet_summary", {}).get("matched_filters", []),
            },
            "proof_summary": {"docs_gate_status": navigator_response.get("docs_gate_status", "UNKNOWN")},
            "docs_gate_status": navigator_response.get("docs_gate_status", "UNKNOWN"),
        }
    alternative_record_ids = (
        extract_alternative_record_ids(navigator_response, seed_record_id)
        if expanded
        else []
    )
    return compose_seed_record(
        registries,
        seed_record_id,
        mode=mode,
        query=query,
        navigator_response=navigator_response,
        alternative_record_ids=alternative_record_ids,
    )


def record(
    registries: dict[str, Any],
    *,
    record_id: str = "",
    path: str = "",
    title: str = "",
    query_text: str = "",
    expanded: bool = False,
) -> dict[str, Any]:
    navigator_response = navigator_record_query(
        registries,
        record_id=record_id,
        path=path,
        title=title,
        query_text=query_text,
        limit=4,
        expanded=expanded,
    )
    return compose_from_navigator_response(
        navigator_response,
        registries,
        mode="record",
        query={
            "record_id": record_id,
            "path": path,
            "title": title,
            "text": query_text,
            "expanded": expanded,
        },
        expanded=expanded,
    )


def search(
    query_text: str,
    registries: dict[str, Any],
    *,
    filters: dict[str, str] | None = None,
    expanded: bool = False,
) -> dict[str, Any]:
    active_filters = {key: value for key, value in (filters or {}).items() if value}
    navigator_response = navigator_search_query(
        query_text,
        registries,
        filters=active_filters,
        limit=4,
        expanded=expanded,
    )
    return compose_from_navigator_response(
        navigator_response,
        registries,
        mode="search",
        query={
            "text": query_text,
            "filters": active_filters,
            "expanded": expanded,
        },
        expanded=expanded,
    )


def facet(
    registries: dict[str, Any],
    *,
    facet_name: str,
    facet_value: str,
    expanded: bool = False,
) -> dict[str, Any]:
    navigator_response = navigator_facet_query(
        registries,
        facet_name=facet_name,
        facet_value=facet_value,
        limit=4,
        expanded=expanded,
    )
    return compose_from_navigator_response(
        navigator_response,
        registries,
        mode="facet",
        query={
            "facet": facet_name,
            "value": facet_value,
            "expanded": expanded,
        },
        expanded=expanded,
    )


def starter_sort_key(record: dict[str, Any], group: str) -> tuple[Any, ...]:
    if group == "math":
        score = float(record.get("salience", 0.0))
    elif group == "myth":
        score = float(record.get("salience", 0.0))
    else:
        score = float(record.get("bridge_intensity", 0.0)) * float(record.get("salience", 0.0))
    return (
        -score,
        -float(record.get("confidence", 0.0)),
        record.get("relative_path", "").lower(),
    )


def build_seed_registry(
    registries: dict[str, Any],
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    groups = {
        "math": [
            record for record in records if record.get("primary_hemisphere") == "MATH"
        ],
        "myth": [
            record for record in records if record.get("primary_hemisphere") == "MYTH"
        ],
        "bridge": [
            record for record in records if record.get("bridge_class") == "commissure_bridge"
        ],
    }
    payload_groups: dict[str, list[dict[str, Any]]] = {}
    for group_name, group_records in groups.items():
        ordered = sorted(group_records, key=lambda item: starter_sort_key(item, group_name))[:STARTER_CAP]
        entries = []
        for index, record_entry in enumerate(ordered, start=1):
            route_bundle = compose_seed_record(
                registries,
                record_entry["record_id"],
                mode="seed_registry",
                query={
                    "seed_group": group_name,
                    "record_id": record_entry["record_id"],
                },
                navigator_response={
                    "facet_summary": {
                        "matched_filters": [
                            {
                                "field": "seed_group",
                                "facet": "seed_group",
                                "requested_value": group_name,
                                "canonical_value": group_name,
                            }
                        ]
                    },
                    "docs_gate_status": docs_gate_status,
                },
            )
            entries.append(
                {
                    "rank": index,
                    "seed_record": route_bundle["seed_record"],
                    "route_bundle": route_bundle,
                }
            )
        payload_groups[group_name] = entries
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "starter_cap": STARTER_CAP,
        "groups": payload_groups,
        "counts": {
            group_name: len(entries)
            for group_name, entries in sorted(payload_groups.items())
        },
    }


def facet_records_for_name(facet_index: dict[str, Any], facet_name: str) -> list[str]:
    return sorted(facet_index.get("facets", {}).get(facet_name, {}))


def build_facet_registry(
    registries: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    facet_index = registries["navigator_facet_index"]
    facet_payloads: dict[str, dict[str, Any]] = {}
    for facet_name in STARTER_FACETS:
        facet_payloads[facet_name] = {}
        for facet_value in facet_records_for_name(facet_index, facet_name):
            route_bundle = facet(
                registries,
                facet_name=facet_name,
                facet_value=facet_value,
            )
            facet_payloads[facet_name][facet_value] = {
                "seed_record": route_bundle.get("seed_record"),
                "route_bundle": route_bundle,
            }
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "facets": facet_payloads,
        "facet_counts": {
            facet_name: len(values)
            for facet_name, values in sorted(facet_payloads.items())
        },
    }


def build_composer_manifest(
    seed_registry: dict[str, Any],
    facet_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "stage_order": ROUTE_STAGE_ORDER,
        "starter_cap": STARTER_CAP,
        "counts": {
            "seed_groups": len(seed_registry.get("groups", {})),
            "math_starters": seed_registry.get("counts", {}).get("math", 0),
            "myth_starters": seed_registry.get("counts", {}).get("myth", 0),
            "bridge_starters": seed_registry.get("counts", {}).get("bridge", 0),
            "facet_starters": sum(facet_registry.get("facet_counts", {}).values()),
        },
        "facet_coverage": facet_registry.get("facet_counts", {}),
        "commands": [
            "python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>",
            "python -m self_actualize.runtime.compose_myth_math_hemisphere_routes search --query <text> --system <system>",
            "python -m self_actualize.runtime.compose_myth_math_hemisphere_routes facet --family <family>",
        ],
    }


def build_route_composer_payloads(
    *,
    record_registry: dict[str, Any],
    commissure_registry: dict[str, Any],
    dual_route_registry: dict[str, Any],
    direct_edge_registry: dict[str, Any],
    manifest: dict[str, Any],
    navigator_alias_index: dict[str, Any],
    navigator_facet_index: dict[str, Any],
    navigator_neighbor_index: dict[str, Any],
    navigator_manifest: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    registries = {
        "record_registry": record_registry,
        "route_registry": dual_route_registry,
        "edge_registry": direct_edge_registry,
        "manifest": manifest,
        "commissure_registry": commissure_registry,
        "navigator_alias_index": navigator_alias_index,
        "navigator_facet_index": navigator_facet_index,
        "navigator_neighbor_index": navigator_neighbor_index,
        "navigator_manifest": navigator_manifest,
    }
    seed_registry = build_seed_registry(
        registries,
        record_registry.get("records", []),
        docs_gate_status,
    )
    facet_registry = build_facet_registry(registries, docs_gate_status)
    composer_manifest = build_composer_manifest(
        seed_registry,
        facet_registry,
        docs_gate_status,
    )
    return seed_registry, facet_registry, composer_manifest
