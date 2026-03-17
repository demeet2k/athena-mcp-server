from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    WORKSPACE_ROOT,
    normalize_path,
    utc_now,
)


FACET_NAMES = [
    "hemisphere",
    "target_system",
    "origin_system",
    "family",
    "anchor",
    "tract",
    "route_role",
    "route_mode",
    "lens",
    "field",
    "zpoint",
    "projection_space",
    "proof_state",
    "top_level",
]
NEIGHBOR_LIMIT = 12


def normalize(value: str) -> str:
    lowered = value.casefold().strip()
    normalized = re.sub(r"[\W_]+", " ", lowered, flags=re.UNICODE).strip()
    if normalized:
        return normalized
    return re.sub(r"\s+", " ", lowered).strip()


def route_ref(record_id: str, hemisphere: str) -> str:
    return f"{record_id}::{hemisphere}"


def try_relative_path(value: str) -> str | None:
    try:
        return str(Path(value).resolve().relative_to(WORKSPACE_ROOT.resolve()))
    except (ValueError, OSError):
        return None


def add_alias(
    aliases_by_norm: dict[str, list[dict[str, str]]],
    kind_counter: Counter[str],
    record_id: str,
    alias_kind: str,
    alias_value: str,
) -> None:
    alias_norm = normalize(alias_value)
    if not alias_value or not alias_norm:
        return
    entry = {
        "record_id": record_id,
        "alias_kind": alias_kind,
        "alias_value": alias_value,
    }
    existing = aliases_by_norm[alias_norm]
    if entry in existing:
        return
    existing.append(entry)
    kind_counter[alias_kind] += 1


def build_alias_index(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    aliases_by_norm: dict[str, list[dict[str, str]]] = defaultdict(list)
    kind_counter: Counter[str] = Counter()

    for record in records:
        add_alias(aliases_by_norm, kind_counter, record["record_id"], "record_id", record["record_id"])
        add_alias(aliases_by_norm, kind_counter, record["record_id"], "title", record.get("title", ""))
        add_alias(
            aliases_by_norm,
            kind_counter,
            record["record_id"],
            "relative_path",
            normalize_path(record.get("relative_path", "")),
        )
        add_alias(
            aliases_by_norm,
            kind_counter,
            record["record_id"],
            "path",
            record.get("path", ""),
        )
        add_alias(
            aliases_by_norm,
            kind_counter,
            record["record_id"],
            "top_level",
            record.get("top_level", ""),
        )

        for duplicate_path in record.get("duplicate_paths", []):
            add_alias(
                aliases_by_norm,
                kind_counter,
                record["record_id"],
                "duplicate_path",
                duplicate_path,
            )
            relative_alias = try_relative_path(duplicate_path)
            if relative_alias:
                add_alias(
                    aliases_by_norm,
                    kind_counter,
                    record["record_id"],
                    "duplicate_relative_path",
                    normalize_path(relative_alias),
                )

    sorted_aliases = {
        alias_norm: sorted(
            entries,
            key=lambda item: (
                item["record_id"],
                item["alias_kind"],
                item["alias_value"].lower(),
            ),
        )
        for alias_norm, entries in sorted(aliases_by_norm.items())
    }
    alias_entry_count = sum(len(entries) for entries in sorted_aliases.values())
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_count": len(records),
        "alias_key_count": len(sorted_aliases),
        "alias_entry_count": alias_entry_count,
        "alias_kind_counts": dict(sorted(kind_counter.items())),
        "aliases_by_norm": sorted_aliases,
    }


def add_facet_posting(
    facet_postings: dict[str, dict[str, list[str]]],
    facet_name: str,
    facet_value: str,
    ref: str,
) -> None:
    if not facet_value:
        return
    bucket = facet_postings[facet_name].setdefault(facet_value, [])
    if ref not in bucket:
        bucket.append(ref)


def build_facet_index(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    facet_postings: dict[str, dict[str, list[str]]] = {
        facet_name: {} for facet_name in FACET_NAMES
    }

    for record in records:
        for hemisphere in ("MATH", "MYTH"):
            route = record["hemisphere_routes"][hemisphere]
            ref = route_ref(record["record_id"], hemisphere)
            add_facet_posting(facet_postings, "hemisphere", hemisphere, ref)
            add_facet_posting(facet_postings, "target_system", route.get("target_system", ""), ref)
            add_facet_posting(facet_postings, "origin_system", route.get("origin_system", ""), ref)
            add_facet_posting(facet_postings, "family", record.get("family", ""), ref)
            for anchor_id in record.get("basis_anchor_ids", []):
                add_facet_posting(facet_postings, "anchor", anchor_id, ref)
            add_facet_posting(facet_postings, "tract", route.get("tract", ""), ref)
            add_facet_posting(facet_postings, "route_role", route.get("route_role", ""), ref)
            add_facet_posting(facet_postings, "route_mode", route.get("route_mode", ""), ref)
            for lens_id, weight in route.get("lens_weight_vector", {}).items():
                if float(weight) > 0.0:
                    add_facet_posting(facet_postings, "lens", lens_id, ref)
            add_facet_posting(facet_postings, "field", route.get("field_id", ""), ref)
            add_facet_posting(facet_postings, "zpoint", route.get("zpoint_id", ""), ref)
            add_facet_posting(
                facet_postings,
                "projection_space",
                route.get("preferred_space", ""),
                ref,
            )
            for space_id in route.get("supported_spaces", []):
                add_facet_posting(facet_postings, "projection_space", space_id, ref)
            add_facet_posting(facet_postings, "proof_state", route.get("proof_state", ""), ref)
            add_facet_posting(facet_postings, "top_level", record.get("top_level", ""), ref)

    sorted_facets = {
        facet_name: {
            facet_value: sorted(refs)
            for facet_value, refs in sorted(values.items())
        }
        for facet_name, values in sorted(facet_postings.items())
    }
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_count": len(records),
        "route_ref_count": len(records) * 2,
        "facet_cardinalities": {
            facet_name: len(values) for facet_name, values in sorted(sorted_facets.items())
        },
        "facets": sorted_facets,
    }


def sort_record_ids(
    record_ids: list[str],
    record_map: dict[str, dict[str, Any]],
    *,
    bridge_first: bool = False,
) -> list[str]:
    return sorted(
        {record_id for record_id in record_ids if record_id in record_map},
        key=lambda record_id: (
            -float(record_map[record_id].get("bridge_intensity", 0.0)) if bridge_first else 0.0,
            -float(record_map[record_id].get("salience", 0.0)),
            -float(record_map[record_id].get("confidence", 0.0)),
            record_map[record_id].get("relative_path", "").lower(),
        ),
    )


def bundle_payload(
    value: str,
    record_ids: list[str],
    current_record_id: str,
    record_map: dict[str, dict[str, Any]],
    *,
    bridge_first: bool = False,
) -> dict[str, Any]:
    candidates = [record_id for record_id in record_ids if record_id != current_record_id]
    ordered = sort_record_ids(candidates, record_map, bridge_first=bridge_first)
    return {
        "value": value,
        "total": len(ordered),
        "record_ids": ordered[:NEIGHBOR_LIMIT],
    }


def build_neighbor_index(
    records: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    record_map = {record["record_id"]: record for record in records}
    primary_target_groups: dict[str, list[str]] = defaultdict(list)
    secondary_target_groups: dict[str, list[str]] = defaultdict(list)
    anchor_groups: dict[str, list[str]] = defaultdict(list)
    corridor_groups: dict[str, list[str]] = defaultdict(list)
    commissure_records: list[str] = []

    for record in records:
        primary_side = record["primary_hemisphere"]
        secondary_side = "MYTH" if primary_side == "MATH" else "MATH"
        primary_target = record["hemisphere_routes"][primary_side]["target_system"]
        secondary_target = record["hemisphere_routes"][secondary_side]["target_system"]
        first_anchor = (record.get("basis_anchor_ids") or ["DN00"])[0]
        corridor_key = f"{record.get('family', 'general-corpus')}|{first_anchor}|{record.get('tract', 'address')}"

        primary_target_groups[primary_target].append(record["record_id"])
        secondary_target_groups[secondary_target].append(record["record_id"])
        anchor_groups[first_anchor].append(record["record_id"])
        corridor_groups[corridor_key].append(record["record_id"])
        if record.get("bridge_class") == "commissure_bridge":
            commissure_records.append(record["record_id"])

    lookup: dict[str, dict[str, Any]] = {}
    for record in records:
        primary_side = record["primary_hemisphere"]
        secondary_side = "MYTH" if primary_side == "MATH" else "MATH"
        primary_target = record["hemisphere_routes"][primary_side]["target_system"]
        secondary_target = record["hemisphere_routes"][secondary_side]["target_system"]
        first_anchor = (record.get("basis_anchor_ids") or ["DN00"])[0]
        corridor_key = f"{record.get('family', 'general-corpus')}|{first_anchor}|{record.get('tract', 'address')}"
        lookup[record["record_id"]] = {
            "record_id": record["record_id"],
            "entrypoint_summary": {
                "primary_target_system": primary_target,
                "secondary_target_system": secondary_target,
                "first_anchor": first_anchor,
                "corridor": corridor_key,
                "bridge_class": record.get("bridge_class"),
            },
            "same_primary_target": bundle_payload(
                primary_target,
                primary_target_groups[primary_target],
                record["record_id"],
                record_map,
            ),
            "same_secondary_target": bundle_payload(
                secondary_target,
                secondary_target_groups[secondary_target],
                record["record_id"],
                record_map,
            ),
            "same_anchor": bundle_payload(
                first_anchor,
                anchor_groups[first_anchor],
                record["record_id"],
                record_map,
            ),
            "same_corridor": bundle_payload(
                corridor_key,
                corridor_groups[corridor_key],
                record["record_id"],
                record_map,
            ),
            "commissure_peers": {
                "enabled": record.get("bridge_class") == "commissure_bridge",
                **bundle_payload(
                    "commissure_bridge",
                    commissure_records if record.get("bridge_class") == "commissure_bridge" else [],
                    record["record_id"],
                    record_map,
                    bridge_first=True,
                ),
            },
        }

    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_count": len(records),
        "neighbor_limit": NEIGHBOR_LIMIT,
        "records": dict(sorted(lookup.items())),
    }


def build_navigator_manifest(
    records: list[dict[str, Any]],
    dual_route_registry: dict[str, Any],
    direct_edge_registry: dict[str, Any],
    alias_index: dict[str, Any],
    facet_index: dict[str, Any],
    neighbor_index: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "counts": {
            "records": len(records),
            "route_packets": dual_route_registry.get("route_count", 0),
            "direct_edges": direct_edge_registry.get("edge_count", 0),
            "alias_keys": alias_index.get("alias_key_count", 0),
            "alias_entries": alias_index.get("alias_entry_count", 0),
            "facet_dimensions": len(facet_index.get("facets", {})),
            "neighbor_records": neighbor_index.get("record_count", 0),
        },
        "facet_cardinalities": facet_index.get("facet_cardinalities", {}),
        "response_modes": ["focused", "expanded", "full_bundle"],
        "query_modes": ["record", "search", "facet"],
        "neighbor_limit": neighbor_index.get("neighbor_limit", NEIGHBOR_LIMIT),
    }


def build_navigator_payloads(
    records: list[dict[str, Any]],
    dual_route_registry: dict[str, Any],
    direct_edge_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    alias_index = build_alias_index(records, docs_gate_status)
    facet_index = build_facet_index(records, docs_gate_status)
    neighbor_index = build_neighbor_index(records, docs_gate_status)
    manifest = build_navigator_manifest(
        records=records,
        dual_route_registry=dual_route_registry,
        direct_edge_registry=direct_edge_registry,
        alias_index=alias_index,
        facet_index=facet_index,
        neighbor_index=neighbor_index,
        docs_gate_status=docs_gate_status,
    )
    return alias_index, facet_index, neighbor_index, manifest
