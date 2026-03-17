from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    DIRECT_EDGE_REGISTRY_PATH,
    DUAL_ROUTE_REGISTRY_PATH,
    MANIFEST_PATH,
    NAVIGATOR_ALIAS_INDEX_PATH,
    NAVIGATOR_FACET_INDEX_PATH,
    NAVIGATOR_MANIFEST_PATH,
    NAVIGATOR_NEIGHBOR_INDEX_PATH,
    RECORD_REGISTRY_PATH,
)
from self_actualize.runtime.hemisphere_full_corpus_integration_support import (
    FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH,
    FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH,
)
from self_actualize.runtime.hemisphere_navigator_support import normalize, route_ref


PROOF_WEIGHT = {
    "OK": 1.0,
    "NEAR": 0.78,
    "AMBIG": 0.46,
    "FAIL": 0.1,
}
SEARCH_FILTER_TO_FACET = {
    "hemisphere": "hemisphere",
    "family": "family",
    "anchor": "anchor",
    "system": "target_system",
    "lens": "lens",
    "field": "field",
    "zpoint": "zpoint",
    "space": "projection_space",
    "tract": "tract",
    "route_role": "route_role",
    "route_mode": "route_mode",
    "proof_state": "proof_state",
    "top_level": "top_level",
}
HIGH_BRIDGE_TOKENS = {"bridge", "commissure", "bilateral", "dual", "both hemispheres"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_navigator_registries() -> dict[str, Any]:
    payload = {
        "record_registry": load_json(RECORD_REGISTRY_PATH),
        "route_registry": load_json(DUAL_ROUTE_REGISTRY_PATH),
        "edge_registry": load_json(DIRECT_EDGE_REGISTRY_PATH),
        "manifest": load_json(MANIFEST_PATH),
        "navigator_alias_index": load_json(NAVIGATOR_ALIAS_INDEX_PATH),
        "navigator_facet_index": load_json(NAVIGATOR_FACET_INDEX_PATH),
        "navigator_neighbor_index": load_json(NAVIGATOR_NEIGHBOR_INDEX_PATH),
        "navigator_manifest": load_json(NAVIGATOR_MANIFEST_PATH),
    }
    if FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH.exists():
        payload["awakening_stage_registry"] = load_json(
            FULL_CORPUS_AWAKENING_STAGE_REGISTRY_PATH
        )
    if FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH.exists():
        payload["awakening_agent_transition_registry"] = load_json(
            FULL_CORPUS_AWAKENING_AGENT_TRANSITION_REGISTRY_PATH
        )
    return payload


def build_runtime(registries: dict[str, Any]) -> dict[str, Any]:
    records = registries["record_registry"].get("records", [])
    routes = registries["route_registry"].get("routes", [])
    edges = registries["edge_registry"].get("edges", [])
    record_map = {record["record_id"]: record for record in records}
    route_lookup: dict[str, dict[str, dict[str, Any]]] = {}
    route_ref_lookup: dict[str, dict[str, Any]] = {}
    edge_lookup: dict[str, dict[str, dict[str, Any]]] = {}
    for route in routes:
        route_lookup.setdefault(route["record_id"], {})[route["hemisphere"]] = route
        route_ref_lookup[route_ref(route["record_id"], route["hemisphere"])] = route
    for edge in edges:
        edge_lookup.setdefault(edge["record_id"], {})[edge["hemisphere"]] = edge

    alias_lookup = registries["navigator_alias_index"].get("aliases_by_norm", {})
    facet_lookup = registries["navigator_facet_index"].get("facets", {})
    facet_aliases = {
        facet_name: {normalize(value): value for value in values}
        for facet_name, values in facet_lookup.items()
    }

    search_blobs: dict[str, str] = {}
    for record in records:
        route_packets = route_lookup.get(record["record_id"], {})
        parts = [
            record.get("record_id", ""),
            record.get("title", ""),
            record.get("relative_path", ""),
            record.get("top_level", ""),
            record.get("family", ""),
            record.get("tract", ""),
            record.get("chapter_station", ""),
            record.get("local_addr", ""),
            record.get("global_addr", ""),
            record.get("truth_state", ""),
            record.get("tesseract_header", ""),
            " ".join(record.get("appendix_support", [])),
            " ".join(" ".join(paths) for paths in record.get("appendix_support_sources", {}).values()),
            " ".join(record.get("basis_anchor_ids", [])),
            " ".join(record.get("duplicate_paths", [])),
        ]
        for hemisphere in ("MATH", "MYTH"):
            route_packet = route_packets.get(hemisphere, {})
            parts.extend(
                [
                    hemisphere,
                    route_packet.get("target_system", ""),
                    route_packet.get("origin_system", ""),
                    route_packet.get("route_role", ""),
                    route_packet.get("route_mode", ""),
                    route_packet.get("field_id", ""),
                    route_packet.get("zpoint_id", ""),
                    route_packet.get("preferred_space", ""),
                    route_packet.get("proof_state", ""),
                    route_packet.get("chapter_station", ""),
                    route_packet.get("local_addr", ""),
                    route_packet.get("global_addr", ""),
                    route_packet.get("truth_state", ""),
                    route_packet.get("tesseract_header", ""),
                    " ".join(route_packet.get("appendix_support", [])),
                    " ".join(" ".join(paths) for paths in route_packet.get("appendix_support_sources", {}).values()),
                    " ".join(route_packet.get("hubs_seq", [])),
                    " ".join(route_packet.get("supported_spaces", [])),
                    " ".join(
                        lens_id
                        for lens_id, weight in route_packet.get("lens_weight_vector", {}).items()
                        if float(weight) > 0.0
                    ),
                ]
            )
        search_blobs[record["record_id"]] = normalize(" ".join(parts))

    awakening_assignments = (
        registries.get("awakening_stage_registry", {}).get("record_assignments", [])
    )
    awakening_by_record_id: dict[str, dict[str, Any]] = {}
    for assignment in awakening_assignments:
        awakening_by_record_id[assignment.get("record_id", "")] = assignment
        for control_record_id in assignment.get("control_record_ids", []):
            awakening_by_record_id[control_record_id] = assignment
    family_note_map = {
        note.get("family_id", ""): note
        for note in registries.get("awakening_agent_transition_registry", {}).get("family_notes", [])
    }
    stage_family_note_map = {
        (note.get("stage_id", ""), note.get("family_id", "")): note
        for note in registries.get("awakening_agent_transition_registry", {}).get(
            "stage_family_matrix",
            [],
        )
    }

    return {
        "registries": registries,
        "records": records,
        "record_map": record_map,
        "route_lookup": route_lookup,
        "route_ref_lookup": route_ref_lookup,
        "edge_lookup": edge_lookup,
        "alias_lookup": alias_lookup,
        "facet_lookup": facet_lookup,
        "facet_aliases": facet_aliases,
        "neighbor_lookup": registries["navigator_neighbor_index"].get("records", {}),
        "search_blobs": search_blobs,
        "docs_gate_status": registries["manifest"].get("docs_gate_status", "UNKNOWN"),
        "neighbor_limit": registries["navigator_manifest"].get("neighbor_limit", 12),
        "awakening_by_record_id": awakening_by_record_id,
        "awakening_family_note_map": family_note_map,
        "awakening_stage_family_note_map": stage_family_note_map,
    }


def awakening_summary(runtime: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    assignment = runtime["awakening_by_record_id"].get(record["record_id"], {})
    stage_id = assignment.get("stage_id", "")
    family = record.get("family", "")
    family_note = runtime["awakening_family_note_map"].get(family, {})
    stage_family_note = runtime["awakening_stage_family_note_map"].get((stage_id, family), {})
    note_ids = []
    if family_note.get("note_id"):
        note_ids.append(family_note["note_id"])
    if stage_family_note.get("note_id"):
        note_ids.append(stage_family_note["note_id"])
    return {
        "stage_id": stage_id,
        "stage_label": assignment.get("stage_label", ""),
        "transition_stages": assignment.get("transition_stages", []),
        "family_transition_note_ids": note_ids,
        "basis_role_overlay_ids": assignment.get(
            "basis_role_overlay_ids",
            record.get("basis_anchor_ids", []),
        ),
        "reassessment_window": assignment.get("reassessment_window", ""),
        "docs_gate_status": assignment.get(
            "docs_gate_status",
            runtime["docs_gate_status"],
        ),
        "abstention_reason": assignment.get("abstention_reason", ""),
    }


def ensure_runtime(registries: dict[str, Any]) -> dict[str, Any]:
    runtime = registries.get("_runtime")
    if runtime is None:
        runtime = build_runtime(registries)
        registries["_runtime"] = runtime
    return runtime


def proof_score(value: str) -> float:
    return PROOF_WEIGHT.get(value, 0.35)


def exact_alias_hits(
    runtime: dict[str, Any],
    query_text: str,
    allowed_kinds: set[str] | None = None,
) -> list[dict[str, Any]]:
    hits = list(runtime["alias_lookup"].get(normalize(query_text), []))
    if allowed_kinds is None:
        return hits
    return [hit for hit in hits if hit["alias_kind"] in allowed_kinds]


def text_match_details(
    record: dict[str, Any],
    runtime: dict[str, Any],
    query_text: str,
) -> tuple[int, float, list[str]]:
    query_norm = normalize(query_text)
    if not query_norm:
        return 0, 0.5, []

    hits = exact_alias_hits(runtime, query_text)
    alias_kinds = [hit["alias_kind"] for hit in hits if hit["record_id"] == record["record_id"]]
    if any(kind == "record_id" for kind in alias_kinds):
        return 4, 1.0, alias_kinds
    if any(
        kind in {"relative_path", "path", "duplicate_path", "duplicate_relative_path"}
        for kind in alias_kinds
    ):
        return 3, 0.99, alias_kinds
    if any(kind == "title" for kind in alias_kinds):
        return 2, 0.98, alias_kinds

    haystack = runtime["search_blobs"][record["record_id"]]
    if query_norm == normalize(record.get("top_level", "")):
        return 1, 0.74, ["top_level"]
    if query_norm in haystack:
        return 1, 0.84, []
    query_tokens = set(query_norm.split())
    if not query_tokens:
        return 0, 0.0, []
    overlap = query_tokens & set(haystack.split())
    if not overlap:
        return 0, 0.0, []
    return 1, round(0.38 + (0.5 * (len(overlap) / len(query_tokens))), 3), []


def canonical_facet_value(
    runtime: dict[str, Any],
    facet_name: str,
    requested_value: str,
) -> str | None:
    if not requested_value:
        return None
    return runtime["facet_aliases"].get(facet_name, {}).get(normalize(requested_value))


def filter_route_refs(
    runtime: dict[str, Any],
    filters: dict[str, str],
) -> tuple[set[str], list[dict[str, Any]]]:
    current: set[str] | None = None
    matched_filters: list[dict[str, Any]] = []
    for field_name, facet_name in SEARCH_FILTER_TO_FACET.items():
        requested_value = filters.get(field_name, "")
        if not requested_value:
            continue
        canonical_value = canonical_facet_value(runtime, facet_name, requested_value)
        route_refs = set()
        if canonical_value is not None:
            route_refs = set(runtime["facet_lookup"].get(facet_name, {}).get(canonical_value, []))
        current = route_refs if current is None else current & route_refs
        matched_filters.append(
            {
                "field": field_name,
                "facet": facet_name,
                "requested_value": requested_value,
                "canonical_value": canonical_value or "",
                "route_ref_count": len(route_refs),
            }
        )
    if current is None:
        current = set(runtime["route_ref_lookup"])
    return current, matched_filters


def query_needs_bridge(query_text: str, filters: dict[str, str]) -> bool:
    query_norm = normalize(query_text)
    if any(token in query_norm for token in HIGH_BRIDGE_TOKENS):
        return True
    return filters.get("route_mode", "") == "commissure_direct"


def summarize_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record["record_id"],
        "title": record.get("title", ""),
        "relative_path": record.get("relative_path", ""),
        "primary_hemisphere": record.get("primary_hemisphere"),
        "family": record.get("family"),
        "tract": record.get("tract"),
        "chapter_station": record.get("chapter_station", ""),
        "local_addr": record.get("local_addr", ""),
        "global_addr": record.get("global_addr", ""),
        "truth_state": record.get("truth_state", ""),
        "tesseract_header": record.get("tesseract_header", ""),
        "appendix_support": list(record.get("appendix_support", [])),
        "appendix_support_sources": record.get("appendix_support_sources", {}),
        "bridge_intensity": record.get("bridge_intensity"),
        "confidence": record.get("confidence"),
        "salience": record.get("salience"),
    }


def neighborhood_response(
    runtime: dict[str, Any],
    bundle: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    records = [
        summarize_record(runtime["record_map"][record_id])
        for record_id in bundle.get("record_ids", [])[:limit]
        if record_id in runtime["record_map"]
    ]
    return {
        "value": bundle.get("value", ""),
        "total": bundle.get("total", 0),
        "records": records,
    }


def build_record_response(
    runtime: dict[str, Any],
    record: dict[str, Any],
    matched_filters: list[dict[str, Any]],
    candidate_summaries: list[dict[str, Any]],
    response_mode: str,
) -> dict[str, Any]:
    neighbor_entry = runtime["neighbor_lookup"].get(record["record_id"], {})
    if response_mode == "focused":
        neighbor_limit = 3
    elif response_mode == "expanded":
        neighbor_limit = 6
    else:
        neighbor_limit = runtime["neighbor_limit"]
    routes = runtime["route_lookup"][record["record_id"]]
    direct_edges = runtime["edge_lookup"][record["record_id"]]
    primary_route = routes[record["primary_hemisphere"]]
    secondary_route = routes["MYTH" if record["primary_hemisphere"] == "MATH" else "MATH"]
    response = {
        "best_match": summarize_record(record),
        "routes": routes,
        "primary_route": primary_route,
        "secondary_route": secondary_route,
        "direct_edges": direct_edges,
        "awakening": awakening_summary(runtime, record),
        "facet_summary": {
            "top_level": record.get("top_level", ""),
            "family": record.get("family", ""),
            "basis_anchor_ids": record.get("basis_anchor_ids", []),
            "tract": record.get("tract", ""),
            "target_systems": {
                hemisphere: route_packet.get("target_system", "")
                for hemisphere, route_packet in routes.items()
            },
            "origin_systems": {
                hemisphere: route_packet.get("origin_system", "")
                for hemisphere, route_packet in routes.items()
            },
            "route_modes": {
                hemisphere: route_packet.get("route_mode", "")
                for hemisphere, route_packet in routes.items()
            },
            "proof_states": {
                hemisphere: route_packet.get("proof_state", "")
                for hemisphere, route_packet in routes.items()
            },
            "fields": {
                hemisphere: route_packet.get("field_id", "")
                for hemisphere, route_packet in routes.items()
            },
            "zpoints": {
                hemisphere: route_packet.get("zpoint_id", "")
                for hemisphere, route_packet in routes.items()
            },
            "spaces": {
                hemisphere: route_packet.get("preferred_space", "")
                for hemisphere, route_packet in routes.items()
            },
            "matched_filters": matched_filters,
        },
        "reverse_neighborhood": {
            "same_primary_target": neighborhood_response(
                runtime,
                neighbor_entry.get("same_primary_target", {}),
                neighbor_limit,
            ),
            "same_secondary_target": neighborhood_response(
                runtime,
                neighbor_entry.get("same_secondary_target", {}),
                neighbor_limit,
            ),
            "same_anchor": neighborhood_response(
                runtime,
                neighbor_entry.get("same_anchor", {}),
                neighbor_limit,
            ),
            "same_corridor": neighborhood_response(
                runtime,
                neighbor_entry.get("same_corridor", {}),
                neighbor_limit,
            ),
            "commissure_peers": {
                "enabled": neighbor_entry.get("commissure_peers", {}).get("enabled", False),
                **neighborhood_response(
                    runtime,
                    neighbor_entry.get("commissure_peers", {}),
                    neighbor_limit,
                ),
            },
        },
        "docs_gate_status": runtime["docs_gate_status"],
    }
    if candidate_summaries:
        response["candidates"] = candidate_summaries
    if response_mode == "full_bundle":
        response["matched_facet_buckets"] = matched_filters
        response["neighbor_manifest"] = neighbor_entry
    return response


def candidate_records(
    runtime: dict[str, Any],
    query_text: str,
    route_refs: set[str],
    filters: dict[str, str],
) -> list[dict[str, Any]]:
    route_refs_by_record: dict[str, list[str]] = {}
    for ref in sorted(route_refs):
        route = runtime["route_ref_lookup"].get(ref)
        if route is None:
            continue
        route_refs_by_record.setdefault(route["record_id"], []).append(ref)

    needs_bridge = query_needs_bridge(query_text, filters)
    ranked: list[dict[str, Any]] = []
    for record_id, matching_refs in route_refs_by_record.items():
        record = runtime["record_map"][record_id]
        exactness_tier, text_score, alias_kinds = text_match_details(record, runtime, query_text)
        if query_text and exactness_tier == 0 and text_score <= 0.0:
            continue
        matching_routes = [runtime["route_ref_lookup"][ref] for ref in matching_refs]
        best_proof = max(proof_score(route.get("proof_state", "AMBIG")) for route in matching_routes)
        best_route_salience = max(
            float(route.get("dynamic_weights", {}).get("salience", record.get("salience", 0.0)))
            for route in matching_routes
        )
        bridge_bonus = float(record.get("bridge_intensity", 0.0)) if needs_bridge else 0.0
        ranked.append(
            {
                "record": record,
                "matching_refs": matching_refs,
                "exactness_tier": exactness_tier,
                "text_score": text_score,
                "alias_kinds": alias_kinds,
                "sort_key": (
                    -exactness_tier,
                    -best_proof,
                    -float(record.get("confidence", 0.0)),
                    -best_route_salience,
                    -bridge_bonus,
                    -text_score,
                    record.get("relative_path", "").lower(),
                ),
            }
        )

    ranked.sort(key=lambda item: item["sort_key"])
    return ranked


def response_mode(expanded: bool, full_bundle: bool) -> str:
    if full_bundle:
        return "full_bundle"
    if expanded:
        return "expanded"
    return "focused"


def search(
    query_text: str,
    registries: dict[str, Any],
    *,
    filters: dict[str, str] | None = None,
    limit: int = 8,
    expanded: bool = False,
    full_bundle: bool = False,
) -> dict[str, Any]:
    runtime = ensure_runtime(registries)
    active_filters = {key: value for key, value in (filters or {}).items() if value}
    route_refs, matched_filters = filter_route_refs(runtime, active_filters)
    ranked = candidate_records(runtime, query_text, route_refs, active_filters)
    best = ranked[0]["record"] if ranked else None
    summaries = [summarize_record(item["record"]) for item in ranked[:limit]]
    result = {
        "query": {
            "text": query_text,
            "filters": active_filters,
            "response_mode": response_mode(expanded, full_bundle),
        },
        "mode": "search",
        "candidate_count": len(ranked),
        "docs_gate_status": runtime["docs_gate_status"],
    }
    if best is None:
        result["best_match"] = None
        result["routes"] = {}
        result["direct_edges"] = {}
        result["facet_summary"] = {"matched_filters": matched_filters}
        result["reverse_neighborhood"] = {}
        result["candidates"] = summaries
        return result
    result.update(
        build_record_response(
            runtime,
            best,
            matched_filters,
            summaries,
            response_mode(expanded, full_bundle),
        )
    )
    return result


def record(
    registries: dict[str, Any],
    *,
    record_id: str = "",
    path: str = "",
    title: str = "",
    query_text: str = "",
    limit: int = 8,
    expanded: bool = False,
    full_bundle: bool = False,
) -> dict[str, Any]:
    runtime = ensure_runtime(registries)
    alias_query = record_id or path or title
    if record_id:
        allowed = {"record_id"}
    elif path:
        allowed = {"path", "relative_path", "duplicate_path", "duplicate_relative_path"}
    elif title:
        allowed = {"title"}
    else:
        allowed = None

    if alias_query:
        alias_hits = exact_alias_hits(runtime, alias_query, allowed)
        if alias_hits:
            candidate_ids = {hit["record_id"] for hit in alias_hits}
            route_refs = {
                route_ref(record_id_value, hemisphere)
                for record_id_value in candidate_ids
                for hemisphere in ("MATH", "MYTH")
            }
            ranked = candidate_records(runtime, alias_query, route_refs, {})
            if ranked:
                best = ranked[0]["record"]
                summaries = [summarize_record(item["record"]) for item in ranked[:limit]]
                response = {
                    "query": {
                        "record_id": record_id,
                        "path": path,
                        "title": title,
                        "text": query_text or alias_query,
                        "response_mode": response_mode(expanded, full_bundle),
                    },
                    "mode": "record",
                    "candidate_count": len(ranked),
                }
                response.update(
                    build_record_response(
                        runtime,
                        best,
                        [{"field": "alias", "matched_aliases": alias_hits}],
                        summaries,
                        response_mode(expanded, full_bundle),
                    )
                )
                return response
    result = search(
        query_text or alias_query,
        registries,
        filters={},
        limit=limit,
        expanded=expanded,
        full_bundle=full_bundle,
    )
    result["mode"] = "record"
    return result


def facet(
    registries: dict[str, Any],
    *,
    facet_name: str,
    facet_value: str,
    limit: int = 8,
    expanded: bool = False,
    full_bundle: bool = False,
) -> dict[str, Any]:
    search_filters = {
        field_name: facet_value
        for field_name, mapped_facet in SEARCH_FILTER_TO_FACET.items()
        if mapped_facet == facet_name
    }
    result = search(
        "",
        registries,
        filters=search_filters,
        limit=limit,
        expanded=expanded,
        full_bundle=full_bundle,
    )
    result["mode"] = "facet"
    result["facet"] = facet_name
    result["value"] = facet_value
    return result
