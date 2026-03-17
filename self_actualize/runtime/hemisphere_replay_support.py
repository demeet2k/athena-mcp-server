from __future__ import annotations

from collections import defaultdict
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    REPLAY_MANIFEST_PATH,
    REPLAY_PAGE_REGISTRY_PATH,
    REPLAY_SEED_REGISTRY_PATH,
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
from self_actualize.runtime.hemisphere_guided_tour_support import MAIN_ATLAS_PAGE_IDS, starter_page_ids
from self_actualize.runtime.hemisphere_synthesis_support import (
    load_synthesis_registries,
    record as synthesis_record_query,
)


REPLAY_PASS_ORDER = [
    "seed_orientation",
    "math_structure_pass",
    "myth_relation_pass",
    "gc0_crossing_pass",
    "synthesis_consolidation",
    "atlas_return",
]
REPLAY_GROUPS = ("math", "myth", "bridge")
REPLAY_PAGE_GROUPS = ("main_pages", "family", "anchor", "target_system", "hemisphere")
REPLAY_SEED_CAP = 24


def load_replay_registries() -> dict[str, Any]:
    registries = load_synthesis_registries()
    if REPLAY_SEED_REGISTRY_PATH.exists():
        registries["replay_seed_registry"] = load_json(REPLAY_SEED_REGISTRY_PATH)
    if REPLAY_PAGE_REGISTRY_PATH.exists():
        registries["replay_page_registry"] = load_json(REPLAY_PAGE_REGISTRY_PATH)
    if REPLAY_MANIFEST_PATH.exists():
        registries["replay_manifest"] = load_json(REPLAY_MANIFEST_PATH)
    return registries


def ensure_replay_runtime(registries: dict[str, Any]) -> dict[str, Any]:
    runtime = registries.get("_replay_runtime")
    if runtime is not None:
        return runtime

    expedition_runtime = ensure_expedition_runtime(registries)
    runtime = {
        "expedition": expedition_runtime,
        "guided_tour": expedition_runtime["guided_tour"],
        "navigator": expedition_runtime["navigator"],
        "docs_gate_status": expedition_runtime["docs_gate_status"],
    }
    registries["_replay_runtime"] = runtime
    return runtime


def ordered_support_ids(*sections: dict[str, Any]) -> list[str]:
    support_ids: list[str] = []
    for section in sections:
        for bullet in section.get("bullets", []):
            for support_id in bullet.get("support_ids", []):
                if support_id not in support_ids:
                    support_ids.append(support_id)
    return support_ids


def section_text(section: dict[str, Any], limit: int = 2) -> str:
    bullets = section.get("bullets", [])[:limit]
    return " ".join(bullet.get("text", "") for bullet in bullets if bullet.get("text"))


def checkpoint(pass_id: str, text: str, support_ids: list[str]) -> dict[str, Any]:
    return {
        "pass": pass_id,
        "text": text,
        "support_ids": support_ids,
    }


def build_replay_from_seed(
    expedition_bundle: dict[str, Any],
    synthesis_bundle: dict[str, Any],
    registries: dict[str, Any],
) -> dict[str, Any]:
    runtime = ensure_replay_runtime(registries)
    seed_record = expedition_bundle.get("seed_record") or {}
    if not seed_record.get("record_id"):
        return {
            "query": expedition_bundle.get("query", {}),
            "mode": expedition_bundle.get("mode", ""),
            "seed_record": None,
            "replay_passes": list(REPLAY_PASS_ORDER),
            "checkpoints": [],
            "support_ids": [],
            "return_links": {},
            "proof_summary": {},
            "docs_gate_status": runtime["docs_gate_status"],
        }

    math_section = synthesis_bundle.get("math_synthesis", {})
    myth_section = synthesis_bundle.get("myth_synthesis", {})
    unified_section = synthesis_bundle.get("unified_synthesis", {})
    bridge_section = synthesis_bundle.get("bridge_interpretation", {})
    appendix_section = synthesis_bundle.get("appendix_support", {})
    source_page = expedition_bundle.get("source_page", {}).get("title", "atlas")

    checkpoints = [
        checkpoint(
            "seed_orientation",
            (
                f'Seed orientation starts from "{seed_record.get("title", "")}" through {source_page}, '
                f"using the first MATH and MYTH evidence anchors to fix the study frame."
            ),
            ordered_support_ids(math_section, myth_section)[:4],
        ),
        checkpoint(
            "math_structure_pass",
            section_text(math_section, 2),
            ordered_support_ids(math_section),
        ),
        checkpoint(
            "myth_relation_pass",
            section_text(myth_section, 2),
            ordered_support_ids(myth_section),
        ),
        checkpoint(
            "gc0_crossing_pass",
            " ".join(
                text
                for text in [
                    section_text(unified_section, 1),
                    section_text(bridge_section, 1),
                ]
                if text
            ),
            ordered_support_ids(unified_section, bridge_section)[:6],
        ),
        checkpoint(
            "synthesis_consolidation",
            " ".join(
                text
                for text in [
                    section_text(unified_section, 2),
                    section_text(bridge_section, 2),
                ]
                if text
            ),
            ordered_support_ids(unified_section, bridge_section),
        ),
        checkpoint(
            "atlas_return",
            (
                f"The replay returns through the atlas exits toward "
                f"{', '.join(sorted(expedition_bundle.get('exit_links', {}).keys()))}, keeping appendix support visible."
            ),
            ordered_support_ids(appendix_section, bridge_section, unified_section),
        ),
    ]

    support_ids: list[str] = []
    for item in checkpoints:
        for support_id in item.get("support_ids", []):
            if support_id not in support_ids:
                support_ids.append(support_id)

    payload = {
        "query": expedition_bundle.get("query", {}),
        "mode": expedition_bundle.get("mode", ""),
        "seed_record": seed_record,
        "replay_passes": list(REPLAY_PASS_ORDER),
        "checkpoints": checkpoints,
        "support_ids": support_ids,
        "return_links": expedition_bundle.get("exit_links", {}),
        "proof_summary": {
            "seed": expedition_bundle.get("proof_summary", {}).get("seed", {}),
            "support_count": len(support_ids),
            "bridge_mode": expedition_bundle.get("seed_tour", {})
            .get("hub_crossing", {})
            .get("bridge_mode", ""),
        },
        "docs_gate_status": expedition_bundle.get("docs_gate_status", runtime["docs_gate_status"]),
    }
    if expedition_bundle.get("alternative_seeds"):
        payload["alternative_seeds"] = expedition_bundle["alternative_seeds"][:3]
    return payload


def replay_for_seed_id(
    registries: dict[str, Any],
    seed_id: str,
) -> dict[str, Any]:
    expedition_bundle = expedition_record_query(
        registries,
        record_id=seed_id,
        expanded=False,
    )
    synthesis_bundle = synthesis_record_query(
        registries,
        record_id=seed_id,
        expanded=False,
    )
    return build_replay_from_seed(expedition_bundle, synthesis_bundle, registries)


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
    seed_summary = expedition_bundle.get("seed_record") or {}
    if not seed_summary.get("record_id"):
        return build_replay_from_seed(expedition_bundle, {}, registries)
    synthesis_bundle = synthesis_record_query(
        registries,
        record_id=seed_summary["record_id"],
        expanded=False,
    )
    return build_replay_from_seed(expedition_bundle, synthesis_bundle, registries)


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
    seed_summary = expedition_bundle.get("seed_record") or {}
    if not seed_summary.get("record_id"):
        return build_replay_from_seed(expedition_bundle, {}, registries)
    synthesis_bundle = synthesis_record_query(
        registries,
        record_id=seed_summary["record_id"],
        expanded=False,
    )
    return build_replay_from_seed(expedition_bundle, synthesis_bundle, registries)


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
    seed_summary = expedition_bundle.get("seed_record") or {}
    if not seed_summary.get("record_id"):
        return build_replay_from_seed(expedition_bundle, {}, registries)
    synthesis_bundle = synthesis_record_query(
        registries,
        record_id=seed_summary["record_id"],
        expanded=False,
    )
    return build_replay_from_seed(expedition_bundle, synthesis_bundle, registries)


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
    seed_summary = expedition_bundle.get("seed_record") or {}
    if not seed_summary.get("record_id"):
        return build_replay_from_seed(expedition_bundle, {}, registries)
    synthesis_bundle = synthesis_record_query(
        registries,
        record_id=seed_summary["record_id"],
        expanded=False,
    )
    return build_replay_from_seed(expedition_bundle, synthesis_bundle, registries)


def build_replay_seed_registry(
    registries: dict[str, Any],
    synthesis_seed_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for group_name in REPLAY_GROUPS:
        entries = synthesis_seed_registry.get("groups", {}).get(group_name, [])
        replay_entries: list[dict[str, Any]] = []
        for rank, entry in enumerate(entries[:REPLAY_SEED_CAP], start=1):
            seed_record = entry.get("seed_record") or {}
            if not seed_record.get("record_id"):
                continue
            replay_entries.append(
                {
                    "rank": rank,
                    "seed_record": seed_record,
                    "replay_bundle": replay_for_seed_id(registries, seed_record["record_id"]),
                }
            )
        groups[group_name] = replay_entries
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "starter_cap": REPLAY_SEED_CAP,
        "groups": groups,
        "counts": {
            group_name: len(entries)
            for group_name, entries in sorted(groups.items())
        },
    }


def build_replay_page_registry(
    registries: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    page_groups = starter_page_ids(visual_atlas_page_registry)
    group_lookup: dict[str, list[str]] = defaultdict(list)
    for group_name in REPLAY_PAGE_GROUPS:
        for page_id in page_groups[group_name]:
            group_lookup[page_id].append(group_name)
    unique_page_ids = sorted({page_id for group_name in REPLAY_PAGE_GROUPS for page_id in page_groups[group_name]})
    runtime = ensure_replay_runtime(registries)
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
                "replay_bundle": bundle,
            }
        )
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "page_count": len(pages),
        "pages": pages,
    }


def build_replay_manifest(
    seed_registry: dict[str, Any],
    page_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "replay_pass_order": list(REPLAY_PASS_ORDER),
        "counts": {
            "seed_starters": sum(seed_registry.get("counts", {}).values()),
            "page_starters": page_registry.get("page_count", 0),
            "group_counts": dict(seed_registry.get("counts", {})),
        },
        "main_page_ids": list(MAIN_ATLAS_PAGE_IDS),
        "output_paths": {
            "seed_registry": str(REPLAY_SEED_REGISTRY_PATH),
            "page_registry": str(REPLAY_PAGE_REGISTRY_PATH),
            "manifest": str(REPLAY_MANIFEST_PATH),
        },
        "commands": {
            "record": "python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas record --record-id <record_id>",
            "search": "python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas search --query <text>",
            "facet": "python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas facet --family <family>",
            "page": "python -m self_actualize.runtime.replay_myth_math_hemisphere_atlas page --page-id <page_id>",
        },
    }


def build_replay_payloads(
    *,
    registries: dict[str, Any],
    synthesis_seed_registry: dict[str, Any],
    visual_atlas_page_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    seed_registry = build_replay_seed_registry(
        registries,
        synthesis_seed_registry,
        docs_gate_status,
    )
    page_registry = build_replay_page_registry(
        registries,
        visual_atlas_page_registry,
        docs_gate_status,
    )
    manifest = build_replay_manifest(seed_registry, page_registry, docs_gate_status)
    return seed_registry, page_registry, manifest
