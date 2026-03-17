from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    FLEET_MIRROR_ROOT,
    GUIDED_TOUR_MANIFEST_PATH,
    GUIDED_TOUR_PAGE_REGISTRY_PATH,
    GUIDED_TOUR_SEED_REGISTRY_PATH,
    HEMISPHERE_ROOT,
    VISUAL_ATLAS_EDGE_REGISTRY_PATH,
    VISUAL_ATLAS_MANIFEST_PATH,
    VISUAL_ATLAS_NODE_REGISTRY_PATH,
    VISUAL_ATLAS_PAGE_REGISTRY_PATH,
    VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH,
    load_json,
    utc_now,
)
from self_actualize.runtime.hemisphere_navigator_query_engine import (
    SEARCH_FILTER_TO_FACET,
    summarize_record,
)
from self_actualize.runtime.hemisphere_route_composer_support import (
    compose_seed_record,
    route_header,
    search as composer_search_query,
    facet as composer_facet_query,
    record as composer_record_query,
)
from self_actualize.runtime.hemisphere_synthesis_support import (
    ensure_synthesis_runtime,
    load_synthesis_registries,
    synthesize_from_composer_payload,
)
from self_actualize.runtime.hemisphere_visual_atlas_support import FIXED_PAGE_SPECS


GUIDED_TOUR_STAGE_ORDER = [
    "seed",
    "primary_hemisphere_page",
    "family_or_anchor_lift",
    "target_system_lift",
    "gc0_crossing",
    "opposite_hemisphere_page",
    "synthesis_landing",
    "locator_exit",
]
MAIN_ATLAS_PAGE_IDS = [page_id for page_id, _, _, _ in FIXED_PAGE_SPECS]
GUIDED_TOUR_GROUPS = ("main_pages", "family", "anchor", "target_system", "hemisphere")
SYNTHESIS_SURFACES = {
    "math": {
        "surface_id": "SYNTH-MATH-STARTERS",
        "title": "MATH Starter Syntheses",
        "relative_path": "27_math_starter_syntheses.md",
    },
    "myth": {
        "surface_id": "SYNTH-MYTH-STARTERS",
        "title": "MYTH Starter Syntheses",
        "relative_path": "28_myth_starter_syntheses.md",
    },
    "commissure": {
        "surface_id": "SYNTH-COMMISSURE-STARTERS",
        "title": "Commissure Starter Syntheses",
        "relative_path": "29_commissure_starter_syntheses.md",
    },
    "facet": {
        "surface_id": "SYNTH-FACET-ATLAS",
        "title": "Facet Synthesis Atlas",
        "relative_path": "30_facet_synthesis_atlas.md",
    },
}


def opposite_hemisphere(hemisphere: str) -> str:
    return "MYTH" if hemisphere == "MATH" else "MATH"


def short_text(value: str, limit: int = 180) -> str:
    collapsed = " ".join(str(value).split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "..."


def load_guided_tour_registries() -> dict[str, Any]:
    if not VISUAL_ATLAS_PAGE_REGISTRY_PATH.exists():
        raise FileNotFoundError(
            "Missing visual atlas registry. Run "
            "`python -m self_actualize.runtime.derive_myth_math_hemisphere_brain` first."
        )
    registries = load_synthesis_registries()
    registries["visual_atlas_node_registry"] = load_json(VISUAL_ATLAS_NODE_REGISTRY_PATH)
    registries["visual_atlas_edge_registry"] = load_json(VISUAL_ATLAS_EDGE_REGISTRY_PATH)
    registries["visual_atlas_page_registry"] = load_json(VISUAL_ATLAS_PAGE_REGISTRY_PATH)
    registries["visual_atlas_record_locator_registry"] = load_json(
        VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH
    )
    registries["visual_atlas_manifest"] = load_json(VISUAL_ATLAS_MANIFEST_PATH)
    if GUIDED_TOUR_SEED_REGISTRY_PATH.exists():
        registries["guided_tour_seed_registry"] = load_json(GUIDED_TOUR_SEED_REGISTRY_PATH)
    if GUIDED_TOUR_PAGE_REGISTRY_PATH.exists():
        registries["guided_tour_page_registry"] = load_json(GUIDED_TOUR_PAGE_REGISTRY_PATH)
    if GUIDED_TOUR_MANIFEST_PATH.exists():
        registries["guided_tour_manifest"] = load_json(GUIDED_TOUR_MANIFEST_PATH)
    return registries


def build_page_value_map(page_map: dict[str, dict[str, Any]], page_type: str) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for page_id, page in page_map.items():
        if page.get("page_type") != page_type:
            continue
        value = page.get("slice", {}).get("value")
        if value:
            lookup[value] = page_id
    return lookup


def first_anchor_id(record: dict[str, Any]) -> str:
    anchors = record.get("basis_anchor_ids") or []
    return anchors[0] if anchors else ""


def score_sort_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -float(record.get("salience", 0.0)),
        -float(record.get("confidence", 0.0)),
        record.get("relative_path", "").lower(),
        record.get("record_id", ""),
    )


def locator_sort_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record.get("relative_path", "").lower(),
        record.get("record_id", ""),
    )


def dedupe_page_ids(page_ids: list[str], page_map: dict[str, dict[str, Any]]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for page_id in page_ids:
        if not page_id or page_id not in page_map or page_id in seen:
            continue
        seen.add(page_id)
        ordered.append(page_id)
    return ordered


def ensure_guided_tour_runtime(registries: dict[str, Any]) -> dict[str, Any]:
    runtime = registries.get("_guided_tour_runtime")
    if runtime is not None:
        return runtime

    synthesis_runtime = ensure_synthesis_runtime(registries)
    navigator_runtime = synthesis_runtime["composer"]["navigator"]
    page_registry = registries["visual_atlas_page_registry"]
    locator_registry = registries["visual_atlas_record_locator_registry"]

    page_map = {page["page_id"]: page for page in page_registry.get("pages", [])}
    records = navigator_runtime["records"]
    family_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    anchor_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    anchor_member_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    system_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    top_level_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    hemisphere_records: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        family_records[record.get("family", "")].append(record)
        first_anchor = first_anchor_id(record)
        if first_anchor:
            anchor_records[first_anchor].append(record)
        for anchor in record.get("basis_anchor_ids", []):
            anchor_member_records[anchor].append(record)
        top_level_records[record.get("top_level", "")].append(record)
        hemisphere_records[record.get("primary_hemisphere", "")].append(record)
        target_systems = {
            record.get("hemisphere_routes", {}).get("MATH", {}).get("target_system", ""),
            record.get("hemisphere_routes", {}).get("MYTH", {}).get("target_system", ""),
        } - {""}
        for target_system in sorted(target_systems):
            system_records[target_system].append(record)

    runtime = {
        "synthesis": synthesis_runtime,
        "composer": synthesis_runtime["composer"],
        "navigator": navigator_runtime,
        "page_map": page_map,
        "locator_lookup": locator_registry.get("records", {}),
        "family_page_map": build_page_value_map(page_map, "family_shard"),
        "anchor_page_map": build_page_value_map(page_map, "anchor_shard"),
        "target_page_map": build_page_value_map(page_map, "target_system_shard"),
        "locator_page_map": build_page_value_map(page_map, "record_locator_shard"),
        "hemisphere_page_map": build_page_value_map(page_map, "hemisphere"),
        "family_records": dict(family_records),
        "anchor_records": dict(anchor_records),
        "anchor_member_records": dict(anchor_member_records),
        "system_records": dict(system_records),
        "top_level_records": dict(top_level_records),
        "hemisphere_records": dict(hemisphere_records),
        "global_records": list(records),
        "docs_gate_status": registries["manifest"].get("docs_gate_status", "UNKNOWN"),
    }
    registries["_guided_tour_runtime"] = runtime
    return runtime


def page_ref(runtime: dict[str, Any], page_id: str) -> dict[str, Any]:
    page = runtime["page_map"].get(page_id)
    if page is None:
        return {
            "page_id": page_id,
            "title": "",
            "page_type": "",
            "relative_path": "",
            "canonical_path": "",
            "mirror_path": "",
        }
    return {
        "page_id": page["page_id"],
        "title": page.get("title", ""),
        "page_type": page.get("page_type", ""),
        "relative_path": page.get("relative_path", ""),
        "canonical_path": page.get("canonical_path", ""),
        "mirror_path": page.get("mirror_path", ""),
        "slice": page.get("slice", {}),
        "counts": page.get("counts", {}),
    }


def synthesis_surface_ref(surface_key: str) -> dict[str, Any]:
    surface = SYNTHESIS_SURFACES[surface_key]
    relative_path = surface["relative_path"]
    return {
        "surface_id": surface["surface_id"],
        "title": surface["title"],
        "relative_path": relative_path,
        "canonical_path": str(HEMISPHERE_ROOT / relative_path),
        "mirror_path": str(FLEET_MIRROR_ROOT / relative_path),
    }


def select_synthesis_surface(
    seed_record: dict[str, Any],
    query: dict[str, Any],
    bridge_mode: str = "",
) -> dict[str, Any]:
    if query.get("facet") or query.get("filters"):
        facet_name = query.get("facet")
        filters = query.get("filters", {})
        if facet_name in {"family", "anchor", "target_system", "hemisphere"} or any(
            name in filters for name in ("family", "anchor", "system", "hemisphere")
        ):
            return synthesis_surface_ref("facet")
    if bridge_mode == "commissure_active" or seed_record.get("bridge_class") == "commissure_bridge":
        return synthesis_surface_ref("commissure")
    if seed_record.get("primary_hemisphere") == "MATH":
        return synthesis_surface_ref("math")
    return synthesis_surface_ref("myth")


def preview_bullets(section_payload: dict[str, Any], limit: int = 2) -> list[dict[str, Any]]:
    previews: list[dict[str, Any]] = []
    for bullet in section_payload.get("bullets", [])[:limit]:
        previews.append(
            {
                "text": short_text(bullet.get("text", "")),
                "support_ids": list(bullet.get("support_ids") or []),
            }
        )
    return previews


def itinerary_header(itinerary: dict[str, Any]) -> dict[str, Any]:
    stage_headers: list[dict[str, Any]] = []
    for stage in itinerary.get("stages", []):
        header = {
            "stage": stage.get("stage", ""),
            "kind": stage.get("kind", ""),
        }
        if stage.get("kind") == "record_stop":
            header.update(
                {
                    "record_id": stage.get("record", {}).get("record_id", ""),
                    "title": stage.get("record", {}).get("title", ""),
                    "proof_state": stage.get("selected_route", {}).get("proof_state", ""),
                    "target_system": stage.get("selected_route", {}).get("target_system", ""),
                }
            )
        elif stage.get("kind") == "hub_stop":
            header.update(
                {
                    "hub_id": stage.get("hub_id", ""),
                    "proof_state": stage.get("proof_state", ""),
                    "target_system": stage.get("target_system", ""),
                }
            )
        elif stage.get("kind") == "exit":
            header.update(
                {
                    "preferred_space": stage.get("preferred_space", ""),
                    "return_path": list(stage.get("return_path") or []),
                    "proof_state": stage.get("proof_state", ""),
                }
            )
        else:
            header["reason"] = stage.get("reason", "")
        stage_headers.append(header)
    return {
        "hemisphere": itinerary.get("hemisphere", ""),
        "stage_order": list(itinerary.get("stage_order") or []),
        "stages": stage_headers,
    }


def target_page_id_for_hemisphere(
    runtime: dict[str, Any],
    seed_record: dict[str, Any],
    hemisphere: str,
) -> str:
    target_system = (
        seed_record.get("hemisphere_routes", {})
        .get(hemisphere, {})
        .get("target_system", "")
    )
    return runtime["target_page_map"].get(target_system, "")


def select_family_or_anchor_page_id(
    runtime: dict[str, Any],
    locator_entry: dict[str, Any],
    source_page_id: str,
) -> str:
    source_page_type = runtime["page_map"].get(source_page_id, {}).get("page_type", "")
    anchor_page_id = locator_entry.get("anchor_page_id", "")
    family_page_id = locator_entry.get("family_page_id", "")
    if source_page_type in {"anchor_shard", "anchor_index"} and anchor_page_id:
        return anchor_page_id
    if source_page_type == "family_shard" and family_page_id:
        return family_page_id
    if anchor_page_id:
        return anchor_page_id
    return family_page_id


def page_spine_ids(
    runtime: dict[str, Any],
    seed_record: dict[str, Any],
    locator_entry: dict[str, Any],
    source_page_id: str,
) -> list[str]:
    primary = seed_record.get("primary_hemisphere", "MATH")
    secondary = opposite_hemisphere(primary)
    return dedupe_page_ids(
        [
            source_page_id,
            locator_entry.get("primary_hemisphere_page_id", ""),
            select_family_or_anchor_page_id(runtime, locator_entry, source_page_id),
            target_page_id_for_hemisphere(runtime, seed_record, primary),
            "VA-OVERVIEW",
            runtime["hemisphere_page_map"].get(secondary, ""),
            locator_entry.get("record_locator_page_id", ""),
        ],
        runtime["page_map"],
    )


def facet_page_id(
    runtime: dict[str, Any],
    facet_name: str,
    facet_value: str,
) -> str:
    if facet_name in {"family"}:
        return runtime["family_page_map"].get(facet_value, "")
    if facet_name in {"anchor"}:
        return runtime["anchor_page_map"].get(facet_value, "")
    if facet_name in {"target_system", "system"}:
        return runtime["target_page_map"].get(facet_value, "")
    if facet_name in {"hemisphere"}:
        return runtime["hemisphere_page_map"].get(facet_value, "")
    if facet_name in {"top_level"}:
        return runtime["locator_page_map"].get(facet_value, "")
    return ""


def source_page_id_from_payload(
    runtime: dict[str, Any],
    composer_payload: dict[str, Any],
) -> str:
    seed_record = composer_payload.get("seed_record") or {}
    locator_entry = runtime["locator_lookup"].get(seed_record.get("record_id", ""), {})
    if composer_payload.get("mode") == "facet":
        page_id = facet_page_id(
            runtime,
            composer_payload.get("query", {}).get("facet", ""),
            composer_payload.get("query", {}).get("value", ""),
        )
        if page_id:
            return page_id
    if composer_payload.get("mode") == "search":
        filters = composer_payload.get("query", {}).get("filters", {})
        for field_name in ("anchor", "family", "system", "hemisphere", "top_level"):
            if not filters.get(field_name):
                continue
            page_id = facet_page_id(
                runtime,
                SEARCH_FILTER_TO_FACET.get(field_name, field_name),
                filters[field_name],
            )
            if page_id:
                return page_id
    return locator_entry.get("record_locator_page_id", "VA-LOCATOR")


def build_leg(
    runtime: dict[str, Any],
    seed_record: dict[str, Any],
    locator_entry: dict[str, Any],
    composer_payload: dict[str, Any],
    synthesis_payload: dict[str, Any],
    hemisphere: str,
    source_page_id: str,
) -> dict[str, Any]:
    itinerary_key = "math_itinerary" if hemisphere == "MATH" else "myth_itinerary"
    synthesis_key = "math_synthesis" if hemisphere == "MATH" else "myth_synthesis"
    family_or_anchor_page = select_family_or_anchor_page_id(runtime, locator_entry, source_page_id)
    linked_page_ids = dedupe_page_ids(
        [
            runtime["hemisphere_page_map"].get(hemisphere, ""),
            family_or_anchor_page,
            target_page_id_for_hemisphere(runtime, seed_record, hemisphere),
            locator_entry.get("record_locator_page_id", ""),
        ],
        runtime["page_map"],
    )
    route_packet = seed_record.get("hemisphere_routes", {}).get(hemisphere, {})
    return {
        "hemisphere": hemisphere,
        "selected_route_header": route_header(route_packet),
        "atlas_page_ids": linked_page_ids,
        "atlas_pages": [page_ref(runtime, page_id) for page_id in linked_page_ids],
        "composer_itinerary_header": itinerary_header(composer_payload.get(itinerary_key, {})),
        "synthesis_section_preview": {
            "section": synthesis_payload.get(synthesis_key, {}).get("section", hemisphere),
            "bullets": preview_bullets(synthesis_payload.get(synthesis_key, {})),
        },
    }


def build_hub_crossing(
    composer_payload: dict[str, Any],
    synthesis_payload: dict[str, Any],
) -> dict[str, Any]:
    shared_spine = composer_payload.get("shared_spine", {})
    bridge_profile = composer_payload.get("bridge_profile", {})
    return {
        "source_hub_id": shared_spine.get("source_hub_id", ""),
        "unified_hub_id": "GC0-UNIFIED-CORPUS",
        "target_hub_id": shared_spine.get("target_hub_id", ""),
        "bridge_mode": bridge_profile.get("mode", ""),
        "direct_edge_ids": list(bridge_profile.get("direct_edge_ids") or []),
        "commissure_edge_ids": list(bridge_profile.get("commissure_edge_ids") or []),
        "bridge_preview": preview_bullets(synthesis_payload.get("bridge_interpretation", {}), limit=2),
    }


def build_synthesis_landing(
    seed_record: dict[str, Any],
    composer_payload: dict[str, Any],
    synthesis_payload: dict[str, Any],
) -> dict[str, Any]:
    surface = select_synthesis_surface(
        seed_record,
        composer_payload.get("query", {}),
        composer_payload.get("bridge_profile", {}).get("mode", ""),
    )
    return {
        **surface,
        "sections": {
            "MATH": preview_bullets(synthesis_payload.get("math_synthesis", {})),
            "MYTH": preview_bullets(synthesis_payload.get("myth_synthesis", {})),
            "Unified": preview_bullets(synthesis_payload.get("unified_synthesis", {})),
            "Bridge": preview_bullets(synthesis_payload.get("bridge_interpretation", {})),
        },
    }


def build_exit_links(
    runtime: dict[str, Any],
    seed_record: dict[str, Any],
    locator_entry: dict[str, Any],
    composer_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "record_locator": page_ref(runtime, locator_entry.get("record_locator_page_id", "")),
        "family": page_ref(runtime, locator_entry.get("family_page_id", "")),
        "first_anchor": page_ref(runtime, locator_entry.get("anchor_page_id", "")),
        "math_topology": page_ref(runtime, "VA-HEM-MATH"),
        "myth_topology": page_ref(runtime, "VA-HEM-MYTH"),
        "synthesis_surface": select_synthesis_surface(
            seed_record,
            composer_payload.get("query", {}),
            composer_payload.get("bridge_profile", {}).get("mode", ""),
        ),
    }


def build_proof_summary(
    composer_payload: dict[str, Any],
    synthesis_payload: dict[str, Any],
) -> dict[str, Any]:
    proof_summary = dict(composer_payload.get("proof_summary", {}))
    proof_summary["evidence_row_count"] = len(synthesis_payload.get("evidence_ledger", {}))
    proof_summary["docs_gate_status"] = synthesis_payload.get(
        "docs_gate_status",
        composer_payload.get("docs_gate_status", "UNKNOWN"),
    )
    return proof_summary


def build_tour_payload(
    composer_payload: dict[str, Any],
    synthesis_payload: dict[str, Any],
    registries: dict[str, Any],
    *,
    source_page_id: str,
) -> dict[str, Any]:
    runtime = ensure_guided_tour_runtime(registries)
    seed_summary = composer_payload.get("seed_record") or {}
    if not seed_summary.get("record_id"):
        return {
            "query": composer_payload.get("query", {}),
            "mode": composer_payload.get("mode", ""),
            "seed_record": None,
            "source_page": page_ref(runtime, source_page_id),
            "tour_stage_order": list(GUIDED_TOUR_STAGE_ORDER),
            "math_leg": {},
            "hub_crossing": {},
            "myth_leg": {},
            "synthesis_landing": {},
            "page_spine": [],
            "exit_links": {},
            "proof_summary": {},
            "docs_gate_status": composer_payload.get("docs_gate_status", runtime["docs_gate_status"]),
        }

    seed_record = runtime["navigator"]["record_map"][seed_summary["record_id"]]
    locator_entry = runtime["locator_lookup"].get(seed_record["record_id"], {})
    page_spine = page_spine_ids(runtime, seed_record, locator_entry, source_page_id)
    payload = {
        "query": composer_payload.get("query", {}),
        "mode": composer_payload.get("mode", ""),
        "seed_record": seed_summary,
        "source_page": page_ref(runtime, source_page_id),
        "tour_stage_order": list(GUIDED_TOUR_STAGE_ORDER),
        "math_leg": build_leg(
            runtime,
            seed_record,
            locator_entry,
            composer_payload,
            synthesis_payload,
            "MATH",
            source_page_id,
        ),
        "hub_crossing": build_hub_crossing(composer_payload, synthesis_payload),
        "myth_leg": build_leg(
            runtime,
            seed_record,
            locator_entry,
            composer_payload,
            synthesis_payload,
            "MYTH",
            source_page_id,
        ),
        "synthesis_landing": build_synthesis_landing(
            seed_record,
            composer_payload,
            synthesis_payload,
        ),
        "page_spine": [page_ref(runtime, page_id) for page_id in page_spine],
        "exit_links": build_exit_links(runtime, seed_record, locator_entry, composer_payload),
        "proof_summary": build_proof_summary(composer_payload, synthesis_payload),
        "docs_gate_status": synthesis_payload.get("docs_gate_status", runtime["docs_gate_status"]),
    }
    if composer_payload.get("alternative_seeds"):
        payload["alternative_seeds"] = composer_payload["alternative_seeds"][:3]
    return payload


def tour_from_composer_payload(
    composer_payload: dict[str, Any],
    registries: dict[str, Any],
    *,
    source_page_id: str | None = None,
) -> dict[str, Any]:
    runtime = ensure_guided_tour_runtime(registries)
    source_page = source_page_id or source_page_id_from_payload(runtime, composer_payload)
    synthesis_payload = synthesize_from_composer_payload(composer_payload, registries)
    return build_tour_payload(
        composer_payload,
        synthesis_payload,
        registries,
        source_page_id=source_page,
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
    composer_payload = composer_record_query(
        registries,
        record_id=record_id,
        path=path,
        title=title,
        query_text=query_text,
        expanded=expanded,
    )
    return tour_from_composer_payload(composer_payload, registries)


def search(
    query_text: str,
    registries: dict[str, Any],
    *,
    filters: dict[str, str] | None = None,
    expanded: bool = False,
) -> dict[str, Any]:
    composer_payload = composer_search_query(
        query_text,
        registries,
        filters=filters or {},
        expanded=expanded,
    )
    return tour_from_composer_payload(composer_payload, registries)


def facet(
    registries: dict[str, Any],
    *,
    facet_name: str,
    facet_value: str,
    expanded: bool = False,
) -> dict[str, Any]:
    composer_payload = composer_facet_query(
        registries,
        facet_name=facet_name,
        facet_value=facet_value,
        expanded=expanded,
    )
    source_page_id = facet_page_id(
        ensure_guided_tour_runtime(registries),
        facet_name,
        facet_value,
    )
    return tour_from_composer_payload(
        composer_payload,
        registries,
        source_page_id=source_page_id or None,
    )


def page_seed_ids(registries: dict[str, Any], page_id: str) -> list[str]:
    runtime = ensure_guided_tour_runtime(registries)
    page = runtime["page_map"].get(page_id)
    if page is None:
        raise ValueError(f"Unknown atlas page id: {page_id}")

    page_type = page.get("page_type", "")
    slice_value = page.get("slice", {}).get("value", "")

    if page_type == "family_shard":
        records = sorted(runtime["family_records"].get(slice_value, []), key=score_sort_key)
    elif page_type == "anchor_shard":
        records = sorted(runtime["anchor_records"].get(slice_value, []), key=score_sort_key)
        if not records:
            records = sorted(runtime["anchor_member_records"].get(slice_value, []), key=score_sort_key)
    elif page_type == "target_system_shard":
        records = sorted(runtime["system_records"].get(slice_value, []), key=score_sort_key)
    elif page_type == "record_locator_shard":
        records = sorted(runtime["top_level_records"].get(slice_value, []), key=locator_sort_key)
    elif page_type == "hemisphere":
        records = sorted(runtime["hemisphere_records"].get(slice_value, []), key=score_sort_key)
    else:
        records = sorted(runtime["global_records"], key=score_sort_key)

    return [record["record_id"] for record in records]


def page(
    registries: dict[str, Any],
    *,
    page_id: str,
    expanded: bool = False,
) -> dict[str, Any]:
    runtime = ensure_guided_tour_runtime(registries)
    seed_ids = page_seed_ids(registries, page_id)
    if not seed_ids:
        return {
            "query": {"page_id": page_id, "expanded": expanded},
            "mode": "page",
            "seed_record": None,
            "source_page": page_ref(runtime, page_id),
            "tour_stage_order": list(GUIDED_TOUR_STAGE_ORDER),
            "math_leg": {},
            "hub_crossing": {},
            "myth_leg": {},
            "synthesis_landing": {},
            "page_spine": [],
            "exit_links": {},
            "proof_summary": {},
            "docs_gate_status": runtime["docs_gate_status"],
        }

    seed_id = seed_ids[0]
    alternative_ids = seed_ids[1:4] if expanded else []
    seed_record = runtime["navigator"]["record_map"][seed_id]
    navigator_response = {
        "best_match": summarize_record(seed_record),
        "facet_summary": {
            "matched_filters": [{"field": "page_id", "value": page_id}],
            "target_systems": {
                hemisphere: seed_record.get("hemisphere_routes", {}).get(hemisphere, {}).get("target_system", "")
                for hemisphere in ("MATH", "MYTH")
            },
            "origin_systems": {
                hemisphere: seed_record.get("hemisphere_routes", {}).get(hemisphere, {}).get("origin_system", "")
                for hemisphere in ("MATH", "MYTH")
            },
            "route_modes": {
                hemisphere: seed_record.get("hemisphere_routes", {}).get(hemisphere, {}).get("route_mode", "")
                for hemisphere in ("MATH", "MYTH")
            },
        },
        "candidate_count": len(seed_ids),
    }
    composer_payload = compose_seed_record(
        registries,
        seed_id,
        mode="page",
        query={"page_id": page_id, "expanded": expanded},
        navigator_response=navigator_response,
        alternative_record_ids=alternative_ids,
    )
    return tour_from_composer_payload(
        composer_payload,
        registries,
        source_page_id=page_id,
    )


def starter_page_ids(page_registry: dict[str, Any]) -> dict[str, list[str]]:
    pages = page_registry.get("pages", [])
    family_pages = sorted(
        [page["page_id"] for page in pages if page.get("page_type") == "family_shard"]
    )
    anchor_pages = sorted(
        [page["page_id"] for page in pages if page.get("page_type") == "anchor_shard"]
    )
    target_pages = sorted(
        [page["page_id"] for page in pages if page.get("page_type") == "target_system_shard"]
    )
    hemisphere_pages = ["VA-HEM-MATH", "VA-HEM-MYTH"]
    return {
        "main_pages": list(MAIN_ATLAS_PAGE_IDS),
        "family": family_pages,
        "anchor": anchor_pages,
        "target_system": target_pages,
        "hemisphere": hemisphere_pages,
    }


def build_guided_tour_seed_registry(
    registries: dict[str, Any],
    page_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    runtime = ensure_guided_tour_runtime(registries)
    page_groups = starter_page_ids(page_registry)
    page_bundle_cache: dict[str, dict[str, Any]] = {}
    unique_page_ids = sorted(
        {page_id for page_ids in page_groups.values() for page_id in page_ids}
    )
    for page_id in unique_page_ids:
        page_bundle_cache[page_id] = page(
            registries,
            page_id=page_id,
            expanded=False,
        )

    groups: dict[str, list[dict[str, Any]]] = {}
    for group_name in GUIDED_TOUR_GROUPS:
        entries: list[dict[str, Any]] = []
        for order, page_id in enumerate(page_groups[group_name], start=1):
            tour_bundle = page_bundle_cache[page_id]
            entries.append(
                {
                    "order": order,
                    "page_id": page_id,
                    "page_title": runtime["page_map"][page_id]["title"],
                    "seed_record": tour_bundle.get("seed_record"),
                    "guided_tour": tour_bundle,
                }
            )
        groups[group_name] = entries

    seed_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "groups": groups,
        "counts": {
            group_name: len(entries)
            for group_name, entries in sorted(groups.items())
        },
    }
    return seed_registry, page_bundle_cache


def build_guided_tour_page_registry(
    page_bundle_cache: dict[str, dict[str, Any]],
    runtime: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    starter_groups = starter_page_ids({"pages": list(runtime["page_map"].values())})
    page_group_lookup: dict[str, list[str]] = defaultdict(list)
    for group_name, page_ids in starter_groups.items():
        for page_id in page_ids:
            page_group_lookup[page_id].append(group_name)

    pages = []
    for page_id in sorted(page_bundle_cache):
        tour_bundle = page_bundle_cache[page_id]
        page_entry = runtime["page_map"][page_id]
        pages.append(
            {
                "page_id": page_id,
                "page_title": page_entry.get("title", ""),
                "page_type": page_entry.get("page_type", ""),
                "starter_groups": sorted(page_group_lookup.get(page_id, [])),
                "seed_record": tour_bundle.get("seed_record"),
                "guided_tour": tour_bundle,
            }
        )
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "page_count": len(pages),
        "pages": pages,
    }


def build_guided_tour_manifest(
    seed_registry: dict[str, Any],
    page_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "tour_stage_order": list(GUIDED_TOUR_STAGE_ORDER),
        "counts": {
            "seed_starters": sum(seed_registry.get("counts", {}).values()),
            "page_starters": page_registry.get("page_count", 0),
            "group_counts": dict(seed_registry.get("counts", {})),
        },
        "main_page_ids": list(MAIN_ATLAS_PAGE_IDS),
        "output_paths": {
            "seed_registry": str(GUIDED_TOUR_SEED_REGISTRY_PATH),
            "page_registry": str(GUIDED_TOUR_PAGE_REGISTRY_PATH),
            "manifest": str(GUIDED_TOUR_MANIFEST_PATH),
        },
        "commands": {
            "record": "python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas record --record-id <record_id>",
            "search": "python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas search --query <text>",
            "facet": "python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas facet --family <family>",
            "page": "python -m self_actualize.runtime.guide_myth_math_hemisphere_atlas page --page-id <page_id>",
        },
    }


def build_guided_tour_payloads(
    *,
    registries: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    seed_registry, page_bundle_cache = build_guided_tour_seed_registry(
        registries,
        visual_atlas_page_registry,
        docs_gate_status,
    )
    runtime = ensure_guided_tour_runtime(registries)
    page_registry = build_guided_tour_page_registry(
        page_bundle_cache,
        runtime,
        docs_gate_status,
    )
    manifest = build_guided_tour_manifest(seed_registry, page_registry, docs_gate_status)
    return seed_registry, page_registry, manifest
