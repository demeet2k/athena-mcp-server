from __future__ import annotations

from collections import defaultdict
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    CONSTELLATION_EDGE_REGISTRY_PATH,
    CONSTELLATION_MANIFEST_PATH,
    CONSTELLATION_NODE_REGISTRY_PATH,
    CONSTELLATION_PAGE_REGISTRY_PATH,
    MATH_HUB_ID,
    MYTH_HUB_ID,
    UNIFIED_HUB_ID,
    load_json,
    utc_now,
)
from self_actualize.runtime.hemisphere_expedition_support import (
    ensure_expedition_runtime,
    facet as expedition_facet_query,
    load_expedition_registries,
    page as expedition_page_query,
    record as expedition_record_query,
    search as expedition_search_query,
)
from self_actualize.runtime.hemisphere_guided_tour_support import (
    MAIN_ATLAS_PAGE_IDS,
    page_ref,
    starter_page_ids,
)


CONSTELLATION_RECORD_CAP = 16
CONSTELLATION_GROUPS = ("main_pages", "family", "anchor", "target_system", "hemisphere")
CONSTELLATION_BUCKET_ORDER = (
    ("same_anchor", "same_anchor"),
    ("same_corridor", "same_corridor"),
    ("same_primary_target", "same_primary_target"),
    ("same_secondary_target", "same_secondary_target"),
    ("commissure_peers", "commissure_peers"),
)


def load_constellation_registries() -> dict[str, Any]:
    registries = load_expedition_registries()
    if CONSTELLATION_NODE_REGISTRY_PATH.exists():
        registries["constellation_node_registry"] = load_json(CONSTELLATION_NODE_REGISTRY_PATH)
    if CONSTELLATION_EDGE_REGISTRY_PATH.exists():
        registries["constellation_edge_registry"] = load_json(CONSTELLATION_EDGE_REGISTRY_PATH)
    if CONSTELLATION_PAGE_REGISTRY_PATH.exists():
        registries["constellation_page_registry"] = load_json(CONSTELLATION_PAGE_REGISTRY_PATH)
    if CONSTELLATION_MANIFEST_PATH.exists():
        registries["constellation_manifest"] = load_json(CONSTELLATION_MANIFEST_PATH)
    return registries


def ensure_constellation_runtime(registries: dict[str, Any]) -> dict[str, Any]:
    runtime = registries.get("_constellation_runtime")
    if runtime is not None:
        return runtime

    expedition_runtime = ensure_expedition_runtime(registries)
    guided_runtime = expedition_runtime["guided_tour"]
    runtime = {
        "expedition": expedition_runtime,
        "guided_tour": guided_runtime,
        "navigator": expedition_runtime["navigator"],
        "page_map": guided_runtime["page_map"],
        "locator_lookup": guided_runtime["locator_lookup"],
        "docs_gate_status": expedition_runtime["docs_gate_status"],
    }
    registries["_constellation_runtime"] = runtime
    return runtime


def slice_type(bundle: dict[str, Any], runtime: dict[str, Any]) -> str:
    mode = bundle.get("mode", "")
    if mode == "page":
        source_page = bundle.get("source_page", {})
        page_id = source_page.get("page_id", "")
        return runtime["page_map"].get(page_id, {}).get("page_type", "page")
    return mode or "record"


def constellation_record_ids(seed_record: dict[str, Any], runtime: dict[str, Any]) -> list[tuple[str, str]]:
    seed_id = seed_record["record_id"]
    neighbor_entry = runtime["navigator"]["neighbor_lookup"].get(seed_id, {})
    selected: list[tuple[str, str]] = [(seed_id, "seed")]
    seen = {seed_id}
    for relation, bundle_key in CONSTELLATION_BUCKET_ORDER:
        bundle = neighbor_entry.get(bundle_key, {})
        if relation == "commissure_peers" and not bundle.get("enabled"):
            continue
        for record_id in bundle.get("record_ids", []):
            if record_id in seen:
                continue
            selected.append((record_id, relation))
            seen.add(record_id)
            if len(selected) >= CONSTELLATION_RECORD_CAP:
                return selected
    return selected


def record_node(
    record: dict[str, Any],
    locator_entry: dict[str, Any],
    relation: str,
) -> dict[str, Any]:
    return {
        "node_id": f"CONST-REC-{record['record_id']}",
        "kind": "record",
        "record_id": record["record_id"],
        "title": record.get("title", ""),
        "relative_path": record.get("relative_path", ""),
        "primary_hemisphere": record.get("primary_hemisphere", ""),
        "family": record.get("family", ""),
        "first_anchor": (record.get("basis_anchor_ids") or [""])[0],
        "relation": relation,
        "salience": record.get("salience", 0.0),
        "confidence": record.get("confidence", 0.0),
        "atlas_page_ids": locator_entry.get("atlas_page_ids", []),
    }


def hub_node(hub_id: str) -> dict[str, Any]:
    return {
        "node_id": f"CONST-{hub_id}",
        "kind": "hub",
        "hub_id": hub_id,
    }


def relation_edge(
    source_id: str,
    target_id: str,
    relation: str,
) -> dict[str, Any]:
    return {
        "edge_id": f"CONST-REL-{source_id}-{target_id}-{relation}",
        "edge_type": relation,
        "source": f"CONST-REC-{source_id}",
        "target": f"CONST-REC-{target_id}",
    }


def direct_hub_edge(record: dict[str, Any], edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "edge_id": f"CONST-{edge.get('edge_id', '')}",
        "edge_type": "direct_hemisphere",
        "source": f"CONST-REC-{record['record_id']}",
        "target": f"CONST-{edge.get('hub_id', '')}",
        "hemisphere": edge.get("hemisphere", ""),
        "weight": edge.get("weight", 0.0),
        "route_mode": edge.get("route_mode", ""),
    }


def build_constellation_from_expedition(
    expedition_bundle: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    runtime = ensure_constellation_runtime(registries)
    seed_summary = expedition_bundle.get("seed_record") or {}
    if not seed_summary.get("record_id"):
        return {
            "query": expedition_bundle.get("query", {}),
            "mode": expedition_bundle.get("mode", ""),
            "seed_record": None,
            "slice_type": slice_type(expedition_bundle, runtime),
            "constellation_nodes": [],
            "constellation_edges": [],
            "math_cluster": {"hub_id": MATH_HUB_ID, "record_node_ids": []},
            "myth_cluster": {"hub_id": MYTH_HUB_ID, "record_node_ids": []},
            "gc0_bridge": {},
            "page_spine": [],
            "exit_links": {},
            "proof_summary": {},
            "docs_gate_status": runtime["docs_gate_status"],
        }

    seed_record = runtime["navigator"]["record_map"][seed_summary["record_id"]]
    record_ids = constellation_record_ids(seed_record, runtime)
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    math_cluster_ids: list[str] = []
    myth_cluster_ids: list[str] = []

    for record_id, relation in record_ids:
        record = runtime["navigator"]["record_map"][record_id]
        locator_entry = runtime["locator_lookup"].get(record_id, {})
        nodes.append(record_node(record, locator_entry, relation))
        if relation != "seed":
            edges.append(relation_edge(seed_record["record_id"], record_id, relation))
        for hemisphere in ("MATH", "MYTH"):
            edge = runtime["navigator"]["edge_lookup"][record_id][hemisphere]
            edges.append(direct_hub_edge(record, edge))
        record_node_id = f"CONST-REC-{record_id}"
        if record.get("primary_hemisphere") == "MATH":
            math_cluster_ids.append(record_node_id)
        else:
            myth_cluster_ids.append(record_node_id)

    nodes.extend([hub_node(MATH_HUB_ID), hub_node(UNIFIED_HUB_ID), hub_node(MYTH_HUB_ID)])
    edges.extend(
        [
            {
                "edge_id": "CONST-SPINE-HC-MATH-GC0",
                "edge_type": "hub_spine",
                "source": f"CONST-{MATH_HUB_ID}",
                "target": f"CONST-{UNIFIED_HUB_ID}",
            },
            {
                "edge_id": "CONST-SPINE-GC0-HC-MYTH",
                "edge_type": "hub_spine",
                "source": f"CONST-{UNIFIED_HUB_ID}",
                "target": f"CONST-{MYTH_HUB_ID}",
            },
        ]
    )
    if f"CONST-REC-{seed_record['record_id']}" not in math_cluster_ids and seed_record.get("primary_hemisphere") == "MATH":
        math_cluster_ids.insert(0, f"CONST-REC-{seed_record['record_id']}")
    if f"CONST-REC-{seed_record['record_id']}" not in myth_cluster_ids and seed_record.get("primary_hemisphere") == "MYTH":
        myth_cluster_ids.insert(0, f"CONST-REC-{seed_record['record_id']}")

    source_page = expedition_bundle.get("source_page", {})
    page_spine_ids = [
        page.get("page_id", "")
        for page in expedition_bundle.get("seed_tour", {}).get("page_spine", [])
        if page.get("page_id")
    ]
    if source_page.get("page_id") and source_page["page_id"] not in page_spine_ids:
        page_spine_ids.insert(0, source_page["page_id"])

    payload = {
        "query": expedition_bundle.get("query", {}),
        "mode": expedition_bundle.get("mode", ""),
        "seed_record": expedition_bundle.get("seed_record"),
        "slice_type": slice_type(expedition_bundle, runtime),
        "constellation_nodes": nodes,
        "constellation_edges": edges,
        "math_cluster": {
            "hub_id": MATH_HUB_ID,
            "record_node_ids": math_cluster_ids,
        },
        "myth_cluster": {
            "hub_id": MYTH_HUB_ID,
            "record_node_ids": myth_cluster_ids,
        },
        "gc0_bridge": {
            "source_hub_id": expedition_bundle.get("shared_hubs", {})
            .get("hub_ids", [MATH_HUB_ID])[0],
            "unified_hub_id": UNIFIED_HUB_ID,
            "target_hub_id": expedition_bundle.get("shared_hubs", {})
            .get("hub_ids", [MATH_HUB_ID, UNIFIED_HUB_ID, MYTH_HUB_ID])[-1],
            "bridge_mode": expedition_bundle.get("seed_tour", {})
            .get("hub_crossing", {})
            .get("bridge_mode", ""),
        },
        "page_spine": [page_ref(runtime["guided_tour"], page_id) for page_id in page_spine_ids],
        "exit_links": expedition_bundle.get("exit_links", {}),
        "proof_summary": {
            **expedition_bundle.get("proof_summary", {}),
            "record_node_count": len([node for node in nodes if node.get("kind") == "record"]),
            "edge_count": len(edges),
        },
        "docs_gate_status": expedition_bundle.get("docs_gate_status", runtime["docs_gate_status"]),
    }
    if expedition_bundle.get("alternative_seeds"):
        payload["alternative_seeds"] = expedition_bundle["alternative_seeds"][:3]
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
    expedition_bundle = expedition_record_query(
        registries,
        record_id=record_id,
        path=path,
        title=title,
        query_text=query_text,
        expanded=expanded,
    )
    return build_constellation_from_expedition(expedition_bundle, registries)


def search(
    query_text: str,
    registries: dict[str, Any],
    *,
    filters: dict[str, str] | None = None,
    expanded: bool = False,
) -> dict[str, Any]:
    expedition_bundle = expedition_search_query(
        query_text,
        registries,
        filters=filters or {},
        expanded=expanded,
    )
    return build_constellation_from_expedition(expedition_bundle, registries)


def facet(
    registries: dict[str, Any],
    *,
    facet_name: str,
    facet_value: str,
    expanded: bool = False,
) -> dict[str, Any]:
    expedition_bundle = expedition_facet_query(
        registries,
        facet_name=facet_name,
        facet_value=facet_value,
        expanded=expanded,
    )
    return build_constellation_from_expedition(expedition_bundle, registries)


def page(
    registries: dict[str, Any],
    *,
    page_id: str,
    expanded: bool = False,
) -> dict[str, Any]:
    expedition_bundle = expedition_page_query(
        registries,
        page_id=page_id,
        expanded=expanded,
    )
    return build_constellation_from_expedition(expedition_bundle, registries)


def build_constellation_page_registry(
    registries: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    runtime = ensure_constellation_runtime(registries)
    page_groups = starter_page_ids(visual_atlas_page_registry)
    group_lookup: dict[str, list[str]] = defaultdict(list)
    for group_name in CONSTELLATION_GROUPS:
        for page_id in page_groups[group_name]:
            group_lookup[page_id].append(group_name)

    unique_page_ids = sorted({page_id for group_name in CONSTELLATION_GROUPS for page_id in page_groups[group_name]})
    page_registry_pages = []
    node_entries = []
    edge_entries = []

    for page_id in unique_page_ids:
        bundle = page(
            registries,
            page_id=page_id,
            expanded=False,
        )
        starter_groups = sorted(group_lookup.get(page_id, []))
        page_registry_pages.append(
            {
                "page_id": page_id,
                "page_title": runtime["page_map"][page_id]["title"],
                "page_type": runtime["page_map"][page_id].get("page_type", ""),
                "starter_groups": starter_groups,
                "seed_record": bundle.get("seed_record"),
                "slice_type": bundle.get("slice_type", ""),
                "constellation_bundle": bundle,
            }
        )
        for node in bundle.get("constellation_nodes", []):
            node_entries.append(
                {
                    "page_id": page_id,
                    "starter_groups": starter_groups,
                    "node": node,
                }
            )
        for edge in bundle.get("constellation_edges", []):
            edge_entries.append(
                {
                    "page_id": page_id,
                    "starter_groups": starter_groups,
                    "edge": edge,
                }
            )

    node_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "node_count": len(node_entries),
        "nodes": node_entries,
    }
    edge_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "edge_count": len(edge_entries),
        "edges": edge_entries,
    }
    page_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "page_count": len(page_registry_pages),
        "pages": page_registry_pages,
    }
    manifest = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_cap": CONSTELLATION_RECORD_CAP,
        "counts": {
            "node_count": node_registry["node_count"],
            "edge_count": edge_registry["edge_count"],
            "page_count": page_registry["page_count"],
            "group_counts": {
                group_name: len(page_groups[group_name])
                for group_name in CONSTELLATION_GROUPS
            },
        },
        "main_page_ids": list(MAIN_ATLAS_PAGE_IDS),
        "output_paths": {
            "node_registry": str(CONSTELLATION_NODE_REGISTRY_PATH),
            "edge_registry": str(CONSTELLATION_EDGE_REGISTRY_PATH),
            "page_registry": str(CONSTELLATION_PAGE_REGISTRY_PATH),
            "manifest": str(CONSTELLATION_MANIFEST_PATH),
        },
        "commands": {
            "record": "python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas record --record-id <record_id>",
            "search": "python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas search --query <text>",
            "facet": "python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas facet --family <family>",
            "page": "python -m self_actualize.runtime.constellate_myth_math_hemisphere_atlas page --page-id <page_id>",
        },
    }
    return node_registry, edge_registry, page_registry, manifest


def build_constellation_payloads(
    *,
    registries: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    del docs_gate_status
    return build_constellation_page_registry(
        registries,
        visual_atlas_page_registry,
        registries["manifest"].get("docs_gate_status", "UNKNOWN"),
    )
