from __future__ import annotations

from collections import defaultdict
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    EXPEDITION_MANIFEST_PATH,
    EXPEDITION_PAGE_REGISTRY_PATH,
    EXPEDITION_SEED_REGISTRY_PATH,
    UNIFIED_HUB_ID,
    load_json,
    utc_now,
)
from self_actualize.runtime.hemisphere_guided_tour_support import (
    MAIN_ATLAS_PAGE_IDS,
    build_page_value_map,
    ensure_guided_tour_runtime,
    facet as guided_facet_query,
    load_guided_tour_registries,
    page as guided_page_query,
    page_ref,
    page_seed_ids,
    record as guided_record_query,
    search as guided_search_query,
    starter_page_ids,
)


EXPEDITION_GROUPS = ("main_pages", "family", "anchor", "target_system", "hemisphere")
BASE_COMPANION_LIMIT = 3
EXPANDED_COMPANION_LIMIT = 5
COMPANION_BUCKETS = (
    ("same_primary_target", "same_primary_target"),
    ("same_anchor", "same_anchor"),
    ("same_corridor", "same_corridor"),
    ("commissure_peers", "commissure_peers"),
)


def short_text(value: str, limit: int = 160) -> str:
    collapsed = " ".join(str(value).split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "..."


def load_expedition_registries() -> dict[str, Any]:
    registries = load_guided_tour_registries()
    if EXPEDITION_SEED_REGISTRY_PATH.exists():
        registries["expedition_seed_registry"] = load_json(EXPEDITION_SEED_REGISTRY_PATH)
    if EXPEDITION_PAGE_REGISTRY_PATH.exists():
        registries["expedition_page_registry"] = load_json(EXPEDITION_PAGE_REGISTRY_PATH)
    if EXPEDITION_MANIFEST_PATH.exists():
        registries["expedition_manifest"] = load_json(EXPEDITION_MANIFEST_PATH)
    return registries


def ensure_expedition_runtime(registries: dict[str, Any]) -> dict[str, Any]:
    runtime = registries.get("_expedition_runtime")
    if runtime is not None:
        return runtime

    guided_runtime = ensure_guided_tour_runtime(registries)
    runtime = {
        "guided_tour": guided_runtime,
        "navigator": guided_runtime["navigator"],
        "page_map": guided_runtime["page_map"],
        "docs_gate_status": guided_runtime["docs_gate_status"],
    }
    registries["_expedition_runtime"] = runtime
    return runtime


def tour_header(tour_bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "seed_record": tour_bundle.get("seed_record"),
        "source_page": tour_bundle.get("source_page", {}),
        "math_route_id": tour_bundle.get("math_leg", {})
        .get("selected_route_header", {})
        .get("route_id", ""),
        "myth_route_id": tour_bundle.get("myth_leg", {})
        .get("selected_route_header", {})
        .get("route_id", ""),
        "bridge_mode": tour_bundle.get("hub_crossing", {}).get("bridge_mode", ""),
        "page_spine_ids": [page.get("page_id", "") for page in tour_bundle.get("page_spine", [])],
        "docs_gate_status": tour_bundle.get("docs_gate_status", ""),
    }


def synthesis_landing_header(tour_bundle: dict[str, Any]) -> dict[str, Any]:
    landing = tour_bundle.get("synthesis_landing", {})
    return {
        "surface_id": landing.get("surface_id", ""),
        "title": landing.get("title", ""),
        "section_count": len(landing.get("sections", [])),
        "sections": landing.get("sections", []),
    }


def facet_page_id(runtime: dict[str, Any], facet_name: str, facet_value: str) -> str:
    page_type_map = {
        "family": ("family_shard", runtime["guided_tour"].get("family_page_map", {})),
        "anchor": ("anchor_shard", runtime["guided_tour"].get("anchor_page_map", {})),
        "target_system": ("target_system_shard", runtime["guided_tour"].get("target_page_map", {})),
        "hemisphere": ("hemisphere", runtime["guided_tour"].get("hemisphere_page_map", {})),
    }
    _, lookup = page_type_map.get(facet_name, ("", {}))
    return lookup.get(facet_value, "VA-OVERVIEW")


def source_page_id_from_tour(runtime: dict[str, Any], guided_tour: dict[str, Any]) -> str:
    source_page = guided_tour.get("source_page", {})
    page_id = source_page.get("page_id", "")
    return page_id if page_id in runtime["page_map"] else "VA-OVERVIEW"


def companion_limit(expanded: bool) -> int:
    return EXPANDED_COMPANION_LIMIT if expanded else BASE_COMPANION_LIMIT


def companion_record_ids(seed_record: dict[str, Any], runtime: dict[str, Any], expanded: bool) -> dict[str, list[str]]:
    limit = companion_limit(expanded)
    neighbor_entry = runtime["navigator"]["neighbor_lookup"].get(seed_record["record_id"], {})
    record_ids: dict[str, list[str]] = {}
    for bucket_name, neighbor_key in COMPANION_BUCKETS:
        bundle = neighbor_entry.get(neighbor_key, {})
        if bucket_name == "commissure_peers" and not bundle.get("enabled"):
            record_ids[bucket_name] = []
            continue
        record_ids[bucket_name] = list(bundle.get("record_ids", [])[:limit])
    return record_ids


def build_companion_tour(
    registries: dict[str, Any],
    record_id: str,
) -> dict[str, Any]:
    return guided_record_query(
        registries,
        record_id=record_id,
        expanded=False,
    )


def companion_entry(
    registries: dict[str, Any],
    record_id: str,
) -> dict[str, Any]:
    tour_bundle = build_companion_tour(registries, record_id)
    return {
        "record": tour_bundle.get("seed_record"),
        "tour_header": tour_header(tour_bundle),
        "synthesis_landing": synthesis_landing_header(tour_bundle),
        "page_spine": [page.get("page_id", "") for page in tour_bundle.get("page_spine", [])],
        "proof_summary": tour_bundle.get("proof_summary", {}),
        "guided_tour": tour_bundle,
    }


def collect_companion_tours(
    registries: dict[str, Any],
    seed_record: dict[str, Any],
    runtime: dict[str, Any],
    expanded: bool,
) -> dict[str, list[dict[str, Any]]]:
    bucket_ids = companion_record_ids(seed_record, runtime, expanded)
    payload: dict[str, list[dict[str, Any]]] = {}
    for bucket_name, record_ids in bucket_ids.items():
        payload[bucket_name] = [companion_entry(registries, record_id) for record_id in record_ids]
    return payload


def shared_hubs(seed_tour: dict[str, Any], companions: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    hub_ids: list[str] = []
    for bundle in [seed_tour, *[entry["guided_tour"] for values in companions.values() for entry in values]]:
        hub_crossing = bundle.get("hub_crossing", {})
        for hub_id in (
            hub_crossing.get("source_hub_id", ""),
            hub_crossing.get("unified_hub_id", ""),
            hub_crossing.get("target_hub_id", ""),
        ):
            if hub_id and hub_id not in hub_ids:
                hub_ids.append(hub_id)
    if UNIFIED_HUB_ID not in hub_ids:
        hub_ids.append(UNIFIED_HUB_ID)
    return {
        "hub_ids": hub_ids,
        "seed_bridge_mode": seed_tour.get("hub_crossing", {}).get("bridge_mode", ""),
    }


def page_matrix(runtime: dict[str, Any], seed_tour: dict[str, Any], companions: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    unique_page_ids: list[str] = []

    def ordered_page_refs(page_ids: list[str]) -> list[dict[str, Any]]:
        refs: list[dict[str, Any]] = []
        for page_id in page_ids:
            if page_id and page_id not in unique_page_ids:
                unique_page_ids.append(page_id)
            if page_id:
                refs.append(page_ref(runtime["guided_tour"], page_id))
        return refs

    seed_page_ids = [page.get("page_id", "") for page in seed_tour.get("page_spine", [])]
    companion_pages: dict[str, list[dict[str, Any]]] = {}
    for bucket_name, entries in companions.items():
        companion_pages[bucket_name] = []
        for entry in entries:
            page_ids = [page_id for page_id in entry.get("page_spine", []) if page_id]
            companion_pages[bucket_name].append(
                {
                    "record_id": entry.get("record", {}).get("record_id", ""),
                    "pages": ordered_page_refs(page_ids),
                }
            )

    return {
        "seed_pages": ordered_page_refs(seed_page_ids),
        "companion_pages": companion_pages,
        "unique_pages": ordered_page_refs(unique_page_ids),
    }


def synthesis_landings(seed_tour: dict[str, Any], companions: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "seed": synthesis_landing_header(seed_tour),
        "companions": {
            bucket_name: [entry.get("synthesis_landing", {}) for entry in entries]
            for bucket_name, entries in companions.items()
        },
    }


def build_proof_summary(seed_tour: dict[str, Any], companions: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "seed": seed_tour.get("proof_summary", {}),
        "companion_counts": {
            bucket_name: len(entries)
            for bucket_name, entries in sorted(companions.items())
        },
        "companion_record_ids": {
            bucket_name: [entry.get("record", {}).get("record_id", "") for entry in entries]
            for bucket_name, entries in companions.items()
        },
        "docs_gate_status": seed_tour.get("docs_gate_status", ""),
    }


def empty_bundle(
    runtime: dict[str, Any],
    *,
    query: dict[str, Any],
    mode: str,
    source_page_id: str,
) -> dict[str, Any]:
    return {
        "query": query,
        "mode": mode,
        "seed_record": None,
        "seed_tour": {},
        "companion_tours": {
            "same_primary_target": [],
            "same_anchor": [],
            "same_corridor": [],
            "commissure_peers": [],
        },
        "shared_hubs": {},
        "page_matrix": {
            "seed_pages": [],
            "companion_pages": {},
            "unique_pages": [],
        },
        "synthesis_landings": {"seed": {}, "companions": {}},
        "exit_links": {},
        "proof_summary": {},
        "docs_gate_status": runtime["docs_gate_status"],
        "source_page": page_ref(runtime["guided_tour"], source_page_id),
    }


def build_expedition_from_tour(
    registries: dict[str, Any],
    guided_tour: dict[str, Any],
    *,
    source_page_id: str | None = None,
) -> dict[str, Any]:
    runtime = ensure_expedition_runtime(registries)
    seed_record = guided_tour.get("seed_record") or {}
    resolved_source_page_id = source_page_id or source_page_id_from_tour(runtime, guided_tour)
    if not seed_record.get("record_id"):
        return empty_bundle(
            runtime,
            query=guided_tour.get("query", {}),
            mode=guided_tour.get("mode", ""),
            source_page_id=resolved_source_page_id,
        )

    canonical_seed = runtime["navigator"]["record_map"][seed_record["record_id"]]
    companions = collect_companion_tours(
        registries,
        canonical_seed,
        runtime,
        bool(guided_tour.get("alternative_seeds")),
    )
    payload = {
        "query": guided_tour.get("query", {}),
        "mode": guided_tour.get("mode", ""),
        "seed_record": seed_record,
        "source_page": page_ref(runtime["guided_tour"], resolved_source_page_id),
        "seed_tour": guided_tour,
        "companion_tours": companions,
        "shared_hubs": shared_hubs(guided_tour, companions),
        "page_matrix": page_matrix(runtime, guided_tour, companions),
        "synthesis_landings": synthesis_landings(guided_tour, companions),
        "exit_links": guided_tour.get("exit_links", {}),
        "proof_summary": build_proof_summary(guided_tour, companions),
        "docs_gate_status": guided_tour.get("docs_gate_status", runtime["docs_gate_status"]),
    }
    if guided_tour.get("alternative_seeds"):
        payload["alternative_seeds"] = guided_tour["alternative_seeds"][:3]
    return payload


def record(
    registries: dict[str, Any],
    *,
    record_id: str = "",
    path: str = "",
    title: str = "",
    query_text: str = "",
    expanded: bool = False,
) -> dict[str, Any]:
    seed_tour = guided_record_query(
        registries,
        record_id=record_id,
        path=path,
        title=title,
        query_text=query_text,
        expanded=expanded,
    )
    return build_expedition_from_tour(registries, seed_tour)


def search(
    query_text: str,
    registries: dict[str, Any],
    *,
    filters: dict[str, str] | None = None,
    expanded: bool = False,
) -> dict[str, Any]:
    seed_tour = guided_search_query(
        query_text,
        registries,
        filters=filters or {},
        expanded=expanded,
    )
    return build_expedition_from_tour(registries, seed_tour)


def facet(
    registries: dict[str, Any],
    *,
    facet_name: str,
    facet_value: str,
    expanded: bool = False,
) -> dict[str, Any]:
    seed_tour = guided_facet_query(
        registries,
        facet_name=facet_name,
        facet_value=facet_value,
        expanded=expanded,
    )
    runtime = ensure_expedition_runtime(registries)
    source_page_id = facet_page_id(runtime, facet_name, facet_value)
    return build_expedition_from_tour(
        registries,
        seed_tour,
        source_page_id=source_page_id,
    )


def page(
    registries: dict[str, Any],
    *,
    page_id: str,
    expanded: bool = False,
) -> dict[str, Any]:
    seed_tour = guided_page_query(
        registries,
        page_id=page_id,
        expanded=expanded,
    )
    return build_expedition_from_tour(
        registries,
        seed_tour,
        source_page_id=page_id,
    )


def build_expedition_seed_registry(
    registries: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    runtime = ensure_expedition_runtime(registries)
    page_groups = starter_page_ids(visual_atlas_page_registry)
    groups = {
        group_name: page_groups[group_name]
        for group_name in EXPEDITION_GROUPS
    }

    page_bundle_cache: dict[str, dict[str, Any]] = {}
    unique_page_ids = sorted({page_id for page_ids in groups.values() for page_id in page_ids})
    for page_id in unique_page_ids:
        page_bundle_cache[page_id] = page(
            registries,
            page_id=page_id,
            expanded=False,
        )

    payload_groups: dict[str, list[dict[str, Any]]] = {}
    for group_name, page_ids in groups.items():
        entries: list[dict[str, Any]] = []
        for order, page_id in enumerate(page_ids, start=1):
            bundle = page_bundle_cache[page_id]
            entries.append(
                {
                    "order": order,
                    "page_id": page_id,
                    "page_title": runtime["page_map"][page_id]["title"],
                    "seed_record": bundle.get("seed_record"),
                    "expedition_bundle": bundle,
                }
            )
        payload_groups[group_name] = entries

    return (
        {
            "generated_at": utc_now(),
            "docs_gate_status": docs_gate_status,
            "groups": payload_groups,
            "counts": {
                group_name: len(entries)
                for group_name, entries in sorted(payload_groups.items())
            },
            "companion_caps": {
                "default": BASE_COMPANION_LIMIT,
                "expanded": EXPANDED_COMPANION_LIMIT,
            },
        },
        page_bundle_cache,
    )


def build_expedition_page_registry(
    page_bundle_cache: dict[str, dict[str, Any]],
    runtime: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    page_groups = starter_page_ids(visual_atlas_page_registry)
    group_lookup: dict[str, list[str]] = defaultdict(list)
    for group_name in EXPEDITION_GROUPS:
        for page_id in page_groups[group_name]:
            group_lookup[page_id].append(group_name)

    pages = []
    for page_id in sorted(page_bundle_cache):
        pages.append(
            {
                "page_id": page_id,
                "page_title": runtime["page_map"][page_id]["title"],
                "page_type": runtime["page_map"][page_id].get("page_type", ""),
                "starter_groups": sorted(group_lookup.get(page_id, [])),
                "seed_record": page_bundle_cache[page_id].get("seed_record"),
                "expedition_bundle": page_bundle_cache[page_id],
            }
        )
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "page_count": len(pages),
        "pages": pages,
    }


def build_expedition_manifest(
    seed_registry: dict[str, Any],
    page_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "counts": {
            "seed_starters": sum(seed_registry.get("counts", {}).values()),
            "page_starters": page_registry.get("page_count", 0),
            "group_counts": dict(seed_registry.get("counts", {})),
        },
        "main_page_ids": list(MAIN_ATLAS_PAGE_IDS),
        "companion_caps": {
            "default": BASE_COMPANION_LIMIT,
            "expanded": EXPANDED_COMPANION_LIMIT,
        },
        "output_paths": {
            "seed_registry": str(EXPEDITION_SEED_REGISTRY_PATH),
            "page_registry": str(EXPEDITION_PAGE_REGISTRY_PATH),
            "manifest": str(EXPEDITION_MANIFEST_PATH),
        },
        "commands": {
            "record": "python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas record --record-id <record_id>",
            "search": "python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas search --query <text>",
            "facet": "python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas facet --family <family>",
            "page": "python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas page --page-id <page_id>",
        },
    }


def build_expedition_payloads(
    *,
    registries: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    seed_registry, page_bundle_cache = build_expedition_seed_registry(
        registries,
        visual_atlas_page_registry,
        docs_gate_status,
    )
    runtime = ensure_expedition_runtime(registries)
    page_registry = build_expedition_page_registry(
        page_bundle_cache,
        runtime,
        visual_atlas_page_registry,
        docs_gate_status,
    )
    manifest = build_expedition_manifest(seed_registry, page_registry, docs_gate_status)
    return seed_registry, page_registry, manifest
