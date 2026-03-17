from __future__ import annotations

from collections import defaultdict
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    OBSERVATORY_MANIFEST_PATH,
    OBSERVATORY_PAGE_REGISTRY_PATH,
    OBSERVATORY_SEED_REGISTRY_PATH,
    load_json,
    utc_now,
)
from self_actualize.runtime.hemisphere_constellation_support import (
    facet as constellation_facet_query,
    load_constellation_registries,
    page as constellation_page_query,
    record as constellation_record_query,
    search as constellation_search_query,
)
from self_actualize.runtime.hemisphere_expedition_support import (
    facet as expedition_facet_query,
    page as expedition_page_query,
    record as expedition_record_query,
    search as expedition_search_query,
)
from self_actualize.runtime.hemisphere_guided_tour_support import (
    MAIN_ATLAS_PAGE_IDS,
    ensure_guided_tour_runtime,
    facet as guided_facet_query,
    page as guided_page_query,
    record as guided_record_query,
    search as guided_search_query,
    starter_page_ids,
)
from self_actualize.runtime.hemisphere_replay_support import (
    facet as replay_facet_query,
    page as replay_page_query,
    record as replay_record_query,
    search as replay_search_query,
)


OBSERVATORY_GROUPS = ("main_pages", "family", "anchor", "target_system", "hemisphere")


def load_observatory_registries() -> dict[str, Any]:
    registries = load_constellation_registries()
    if OBSERVATORY_SEED_REGISTRY_PATH.exists():
        registries["observatory_seed_registry"] = load_json(OBSERVATORY_SEED_REGISTRY_PATH)
    if OBSERVATORY_PAGE_REGISTRY_PATH.exists():
        registries["observatory_page_registry"] = load_json(OBSERVATORY_PAGE_REGISTRY_PATH)
    if OBSERVATORY_MANIFEST_PATH.exists():
        registries["observatory_manifest"] = load_json(OBSERVATORY_MANIFEST_PATH)
    return registries


def ensure_observatory_runtime(registries: dict[str, Any]) -> dict[str, Any]:
    runtime = registries.get("_observatory_runtime")
    if runtime is not None:
        return runtime

    guided_runtime = ensure_guided_tour_runtime(registries)
    runtime = {
        "guided_tour": guided_runtime,
        "navigator": guided_runtime["navigator"],
        "manifest": registries["manifest"],
        "docs_gate_status": registries["manifest"].get("docs_gate_status", "UNKNOWN"),
    }
    registries["_observatory_runtime"] = runtime
    return runtime


def tour_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_page": bundle.get("source_page", {}),
        "bridge_mode": bundle.get("hub_crossing", {}).get("bridge_mode", ""),
        "page_spine_ids": [page.get("page_id", "") for page in bundle.get("page_spine", [])],
        "exit_links": bundle.get("exit_links", {}),
    }


def expedition_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    companions = bundle.get("companion_tours", {})
    return {
        "source_page": bundle.get("source_page", {}),
        "companion_counts": {
            bucket_name: len(entries)
            for bucket_name, entries in sorted(companions.items())
        },
        "shared_hubs": bundle.get("shared_hubs", {}),
        "page_count": len(bundle.get("page_matrix", {}).get("unique_pages", [])),
    }


def constellation_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "slice_type": bundle.get("slice_type", ""),
        "record_node_count": len(
            [node for node in bundle.get("constellation_nodes", []) if node.get("kind") == "record"]
        ),
        "edge_count": len(bundle.get("constellation_edges", [])),
        "page_spine_ids": [page.get("page_id", "") for page in bundle.get("page_spine", [])],
    }


def replay_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "pass_count": len(bundle.get("replay_passes", [])),
        "support_count": len(bundle.get("support_ids", [])),
        "return_links": bundle.get("return_links", {}),
    }


def best_synthesis_landing(bundle: dict[str, Any]) -> dict[str, Any]:
    landing = bundle.get("synthesis_landing", {})
    return {
        "surface_id": landing.get("surface_id", ""),
        "title": landing.get("title", ""),
        "section_count": len(landing.get("sections", [])),
        "sections": landing.get("sections", []),
    }


def build_watchpoints(seed_record: dict[str, Any], guided_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    watchpoints = [
        {
            "type": "bridge_mode",
            "value": guided_bundle.get("hub_crossing", {}).get("bridge_mode", ""),
        },
        {
            "type": "confidence",
            "value": seed_record.get("confidence", 0.0),
        },
        {
            "type": "bridge_intensity",
            "value": seed_record.get("bridge_intensity", 0.0),
        },
    ]
    if not seed_record.get("text_extractable", True):
        watchpoints.append({"type": "metadata_only", "value": True})
    if float(seed_record.get("confidence", 0.0)) < 0.6:
        watchpoints.append({"type": "low_confidence", "value": True})
    return watchpoints


def operator_links(seed_id: str) -> dict[str, Any]:
    return {
        "guided_tour": (
            "python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas "
            f"record --record-id {seed_id}"
        ),
        "expedition": (
            "python -m self_actualize.runtime.expedite_myth_math_hemisphere_atlas "
            f"record --record-id {seed_id}"
        ),
        "constellation": (
            "python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas "
            f"record --record-id {seed_id}"
        ),
        "replay": (
            "python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas "
            f"record --record-id {seed_id}"
        ),
        "synthesis": (
            "python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes "
            f"record --record-id {seed_id}"
        ),
    }


def build_observatory_bundle(
    guided_bundle: dict[str, Any],
    expedition_bundle: dict[str, Any],
    constellation_bundle: dict[str, Any],
    replay_bundle: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    runtime = ensure_observatory_runtime(registries)
    seed_record = guided_bundle.get("seed_record") or {}
    if not seed_record.get("record_id"):
        return {
            "query": guided_bundle.get("query", {}),
            "mode": guided_bundle.get("mode", ""),
            "seed_record": None,
            "field_status": {},
            "best_tour": {},
            "best_expedition": {},
            "best_constellation": {},
            "best_replay": {},
            "best_synthesis_landing": {},
            "watchpoints": [],
            "operator_links": {},
            "docs_gate_status": runtime["docs_gate_status"],
        }

    manifest_counts = runtime["manifest"].get("counts", {})
    payload = {
        "query": guided_bundle.get("query", {}),
        "mode": guided_bundle.get("mode", ""),
        "seed_record": seed_record,
        "field_status": {
            "record_count": manifest_counts.get("record_count", 0),
            "math_records": manifest_counts.get("math_records", 0),
            "myth_records": manifest_counts.get("myth_records", 0),
            "commissure_records": manifest_counts.get("commissure_records", 0),
            "docs_gate_status": runtime["docs_gate_status"],
        },
        "best_tour": tour_summary(guided_bundle),
        "best_expedition": expedition_summary(expedition_bundle),
        "best_constellation": constellation_summary(constellation_bundle),
        "best_replay": replay_summary(replay_bundle),
        "best_synthesis_landing": best_synthesis_landing(guided_bundle),
        "watchpoints": build_watchpoints(seed_record, guided_bundle),
        "operator_links": operator_links(seed_record["record_id"]),
        "docs_gate_status": runtime["docs_gate_status"],
    }
    if guided_bundle.get("alternative_seeds"):
        payload["alternative_seeds"] = guided_bundle["alternative_seeds"][:3]
    return payload


def resolve_stack_for_mode(
    mode: str,
    registries: dict[str, Any],
    **kwargs: Any,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    if mode == "record":
        guided_bundle = guided_record_query(registries, **kwargs)
        expedition_bundle = expedition_record_query(registries, **kwargs)
        constellation_bundle = constellation_record_query(registries, **kwargs)
        replay_bundle = replay_record_query(registries, **kwargs)
    elif mode == "search":
        guided_bundle = guided_search_query(kwargs.pop("query_text"), registries, **kwargs)
        expedition_bundle = expedition_search_query(guided_bundle.get("query", {}).get("query", ""), registries, filters=kwargs.get("filters", {}), expanded=kwargs.get("expanded", False))
        constellation_bundle = constellation_search_query(guided_bundle.get("query", {}).get("query", ""), registries, filters=kwargs.get("filters", {}), expanded=kwargs.get("expanded", False))
        replay_bundle = replay_search_query(guided_bundle.get("query", {}).get("query", ""), registries, filters=kwargs.get("filters", {}), expanded=kwargs.get("expanded", False))
    elif mode == "facet":
        guided_bundle = guided_facet_query(registries, **kwargs)
        expedition_bundle = expedition_facet_query(registries, **kwargs)
        constellation_bundle = constellation_facet_query(registries, **kwargs)
        replay_bundle = replay_facet_query(registries, **kwargs)
    else:
        guided_bundle = guided_page_query(registries, **kwargs)
        expedition_bundle = expedition_page_query(registries, **kwargs)
        constellation_bundle = constellation_page_query(registries, **kwargs)
        replay_bundle = replay_page_query(registries, **kwargs)
    return guided_bundle, expedition_bundle, constellation_bundle, replay_bundle


def record(
    registries: dict[str, Any],
    *,
    record_id: str = "",
    path: str = "",
    title: str = "",
    query_text: str = "",
    expanded: bool = False,
) -> dict[str, Any]:
    guided_bundle, expedition_bundle, constellation_bundle, replay_bundle = resolve_stack_for_mode(
        "record",
        registries,
        record_id=record_id,
        path=path,
        title=title,
        query_text=query_text,
        expanded=expanded,
    )
    return build_observatory_bundle(
        guided_bundle,
        expedition_bundle,
        constellation_bundle,
        replay_bundle,
        registries,
    )


def search(
    query_text: str,
    registries: dict[str, Any],
    *,
    filters: dict[str, str] | None = None,
    expanded: bool = False,
) -> dict[str, Any]:
    guided_bundle, expedition_bundle, constellation_bundle, replay_bundle = resolve_stack_for_mode(
        "search",
        registries,
        query_text=query_text,
        filters=filters or {},
        expanded=expanded,
    )
    return build_observatory_bundle(
        guided_bundle,
        expedition_bundle,
        constellation_bundle,
        replay_bundle,
        registries,
    )


def facet(
    registries: dict[str, Any],
    *,
    facet_name: str,
    facet_value: str,
    expanded: bool = False,
) -> dict[str, Any]:
    guided_bundle, expedition_bundle, constellation_bundle, replay_bundle = resolve_stack_for_mode(
        "facet",
        registries,
        facet_name=facet_name,
        facet_value=facet_value,
        expanded=expanded,
    )
    return build_observatory_bundle(
        guided_bundle,
        expedition_bundle,
        constellation_bundle,
        replay_bundle,
        registries,
    )


def page(
    registries: dict[str, Any],
    *,
    page_id: str,
    expanded: bool = False,
) -> dict[str, Any]:
    guided_bundle, expedition_bundle, constellation_bundle, replay_bundle = resolve_stack_for_mode(
        "page",
        registries,
        page_id=page_id,
        expanded=expanded,
    )
    return build_observatory_bundle(
        guided_bundle,
        expedition_bundle,
        constellation_bundle,
        replay_bundle,
        registries,
    )


def build_observatory_seed_registry(
    registries: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    page_groups = starter_page_ids(visual_atlas_page_registry)
    groups: dict[str, list[dict[str, Any]]] = {}
    for group_name in OBSERVATORY_GROUPS:
        entries: list[dict[str, Any]] = []
        for order, page_id in enumerate(page_groups[group_name], start=1):
            bundle = page(
                registries,
                page_id=page_id,
                expanded=False,
            )
            entries.append(
                {
                    "order": order,
                    "page_id": page_id,
                    "seed_record": bundle.get("seed_record"),
                    "observatory_bundle": bundle,
                }
            )
        groups[group_name] = entries
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "groups": groups,
        "counts": {
            group_name: len(entries)
            for group_name, entries in sorted(groups.items())
        },
    }


def build_observatory_page_registry(
    registries: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    page_groups = starter_page_ids(visual_atlas_page_registry)
    group_lookup: dict[str, list[str]] = defaultdict(list)
    for group_name in OBSERVATORY_GROUPS:
        for page_id in page_groups[group_name]:
            group_lookup[page_id].append(group_name)
    unique_page_ids = sorted({page_id for group_name in OBSERVATORY_GROUPS for page_id in page_groups[group_name]})
    runtime = ensure_observatory_runtime(registries)
    pages = []
    for page_id in unique_page_ids:
        bundle = page(
            registries,
            page_id=page_id,
            expanded=False,
        )
        pages.append(
            {
                "page_id": page_id,
                "page_title": runtime["guided_tour"]["page_map"][page_id]["title"],
                "page_type": runtime["guided_tour"]["page_map"][page_id].get("page_type", ""),
                "starter_groups": sorted(group_lookup.get(page_id, [])),
                "seed_record": bundle.get("seed_record"),
                "observatory_bundle": bundle,
            }
        )
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "page_count": len(pages),
        "pages": pages,
    }


def build_observatory_manifest(
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
        "output_paths": {
            "seed_registry": str(OBSERVATORY_SEED_REGISTRY_PATH),
            "page_registry": str(OBSERVATORY_PAGE_REGISTRY_PATH),
            "manifest": str(OBSERVATORY_MANIFEST_PATH),
        },
        "commands": {
            "record": "python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas record --record-id <record_id>",
            "search": "python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas search --query <text>",
            "facet": "python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas facet --family <family>",
            "page": "python -m self_actualize.runtime.brief_myth_math_hemisphere_atlas page --page-id <page_id>",
        },
    }


def build_observatory_payloads(
    *,
    registries: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    seed_registry = build_observatory_seed_registry(
        registries,
        visual_atlas_page_registry,
        docs_gate_status,
    )
    page_registry = build_observatory_page_registry(
        registries,
        visual_atlas_page_registry,
        docs_gate_status,
    )
    manifest = build_observatory_manifest(seed_registry, page_registry, docs_gate_status)
    return seed_registry, page_registry, manifest
