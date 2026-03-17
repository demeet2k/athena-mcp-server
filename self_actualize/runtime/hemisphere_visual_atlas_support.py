from __future__ import annotations

import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    COMPOSER_SEED_REGISTRY_PATH,
    FAMILY_LABELS,
    FLEET_MIRROR_ROOT,
    HEMISPHERE_ROOT,
    MATH_HUB_ID,
    MYTH_HUB_ID,
    NAVIGATOR_FACET_INDEX_PATH,
    RECORD_REGISTRY_PATH,
    ROUTE_MANIFEST_PATH,
    SYNTHESIS_SEED_REGISTRY_PATH,
    UNIFIED_HUB_ID,
    VISUAL_ATLAS_EDGE_REGISTRY_PATH,
    VISUAL_ATLAS_MANIFEST_PATH,
    VISUAL_ATLAS_NODE_REGISTRY_PATH,
    VISUAL_ATLAS_PAGE_REGISTRY_PATH,
    VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH,
    slugify,
    utc_now,
)


VISUAL_ATLAS_SUBDIR = Path("visual_atlas")
SOURCE_REGISTRY_NAMES = [
    "record_registry",
    "dual_route_registry",
    "direct_edge_registry",
    "navigator_facet_index",
    "composer_seed_registry",
    "synthesis_seed_registry",
]
FIXED_PAGE_SPECS = [
    ("VA-INDEX", "Visual Atlas Index", Path("31_visual_atlas_index.md"), "main_index"),
    ("VA-OVERVIEW", "Corpus Overview Map", Path("32_corpus_overview_map.md"), "overview"),
    ("VA-HEM-MATH", "MATH Route Topology Atlas", Path("33_math_route_topology_atlas.md"), "hemisphere"),
    ("VA-HEM-MYTH", "MYTH Route Topology Atlas", Path("34_myth_route_topology_atlas.md"), "hemisphere"),
    ("VA-ANCHOR", "Anchor Crosswalk Atlas", Path("35_anchor_crosswalk_atlas.md"), "anchor_index"),
    ("VA-TARGET-SYSTEM", "Target-System Atlas", Path("36_target_system_atlas.md"), "target_system_index"),
    ("VA-LOCATOR", "Record Locator Index", Path("37_record_locator_index.md"), "record_locator_index"),
    ("VA-COVERAGE", "Atlas Coverage Receipt", Path("38_atlas_coverage_receipt.md"), "coverage"),
]


def safe_text(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def short_text(value: str, limit: int = 72) -> str:
    collapsed = " ".join(value.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "..."


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(safe_text(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def rel_link(current_rel: Path, target_rel: Path, label: str) -> str:
    relative = os.path.relpath(target_rel, start=current_rel.parent if current_rel.parent != Path(".") else Path("."))
    return f"[{label}]({relative.replace(os.sep, '/')})"


def mermaid_block(lines: list[str]) -> str:
    return "```mermaid\nflowchart LR\n" + "\n".join(lines) + "\n```"


def node_id(prefix: str, value: str) -> str:
    return f"{prefix}-{slugify(value)}"


def route_lookup(record: dict[str, Any], hemisphere: str) -> dict[str, Any]:
    return record.get("hemisphere_routes", {}).get(hemisphere, {})


def opposite_hemisphere(hemisphere: str) -> str:
    return "MYTH" if hemisphere == "MATH" else "MATH"


def build_seed_group_lookup(seed_registry: dict[str, Any]) -> dict[str, list[str]]:
    lookup: dict[str, list[str]] = defaultdict(list)
    for group_name, entries in seed_registry.get("groups", {}).items():
        for entry in entries:
            record_id = entry.get("seed_record", {}).get("record_id")
            if record_id:
                lookup[record_id].append(group_name)
    return {record_id: sorted(groups) for record_id, groups in lookup.items()}


def output_paths() -> list[str]:
    return [
        str(VISUAL_ATLAS_NODE_REGISTRY_PATH),
        str(VISUAL_ATLAS_EDGE_REGISTRY_PATH),
        str(VISUAL_ATLAS_PAGE_REGISTRY_PATH),
        str(VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH),
        str(VISUAL_ATLAS_MANIFEST_PATH),
    ]


def command_block(record_id: str | None = None, family: str | None = None) -> str:
    if record_id:
        query_line = f"python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id {record_id}"
        compose_line = f"python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id {record_id}"
        synth_line = f"python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id {record_id}"
    elif family:
        query_line = f"python -m self_actualize.runtime.query_myth_math_hemisphere_brain facet --family {family}"
        compose_line = f"python -m self_actualize.runtime.compose_myth_math_hemisphere_routes facet --family {family}"
        synth_line = f"python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes facet --family {family}"
    else:
        query_line = "python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>"
        compose_line = "python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>"
        synth_line = "python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>"
    return (
        "```powershell\n"
        f"{query_line}\n"
        f"{compose_line}\n"
        f"{synth_line}\n"
        "```"
    )


def register_page(
    pages: list[dict[str, Any]],
    markdown_pages: dict[str, str],
    *,
    page_id: str,
    title: str,
    relative_path: Path,
    page_type: str,
    slice_payload: dict[str, Any],
    counts: dict[str, Any],
    content: str,
) -> None:
    rel_str = relative_path.as_posix()
    markdown_pages[rel_str] = content
    pages.append(
        {
            "page_id": page_id,
            "title": title,
            "page_type": page_type,
            "relative_path": rel_str,
            "canonical_path": str(HEMISPHERE_ROOT / relative_path),
            "mirror_path": str(FLEET_MIRROR_ROOT / relative_path),
            "slice": slice_payload,
            "counts": counts,
            "linked_outputs": output_paths(),
            "source_registries": SOURCE_REGISTRY_NAMES,
        }
    )


def build_visual_atlas_payloads(
    *,
    record_registry: dict[str, Any],
    dual_route_registry: dict[str, Any],
    direct_edge_registry: dict[str, Any],
    manifest: dict[str, Any],
    navigator_facet_index: dict[str, Any],
    composer_seed_registry: dict[str, Any],
    synthesis_seed_registry: dict[str, Any],
    docs_gate_status: str,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, str],
]:
    del dual_route_registry, manifest
    records = sorted(
        record_registry.get("records", []),
        key=lambda item: item.get("relative_path", "").lower(),
    )
    direct_edge_lookup = {
        (edge["record_id"], edge["hemisphere"]): edge
        for edge in direct_edge_registry.get("edges", [])
    }
    composer_seed_groups = build_seed_group_lookup(composer_seed_registry)
    synthesis_seed_groups = build_seed_group_lookup(synthesis_seed_registry)

    family_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    anchor_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    system_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    top_level_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    family_primary_counts = Counter()
    family_bridge_counts = Counter()
    anchor_primary_counts: dict[str, Counter[str]] = defaultdict(Counter)
    anchor_member_counts = Counter()
    system_route_counts: dict[str, Counter[str]] = defaultdict(Counter)
    hemisphere_primary_counts = Counter(record.get("primary_hemisphere", "") for record in records)
    hemisphere_route_system_counts = {
        "MATH": Counter(),
        "MYTH": Counter(),
    }

    record_locator_rows: dict[str, dict[str, Any]] = {}
    record_nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    main_page_map = {page_id: rel_path for page_id, _, rel_path, _ in FIXED_PAGE_SPECS}
    family_page_map: dict[str, tuple[str, Path]] = {}
    anchor_page_map: dict[str, tuple[str, Path]] = {}
    target_page_map: dict[str, tuple[str, Path]] = {}
    locator_page_map: dict[str, tuple[str, Path]] = {}

    for record in records:
        family = record.get("family", "")
        family_records[family].append(record)
        family_primary_counts[(family, record.get("primary_hemisphere", ""))] += 1
        if record.get("bridge_class") == "commissure_bridge":
            family_bridge_counts[family] += 1
        top_level_records[record.get("top_level", "<unknown>")].append(record)
        for anchor in record.get("basis_anchor_ids", []):
            anchor_records[anchor].append(record)
            anchor_member_counts[anchor] += 1
            anchor_primary_counts[anchor][record.get("primary_hemisphere", "")] += 1
        for hemisphere in ("MATH", "MYTH"):
            route_packet = route_lookup(record, hemisphere)
            target_system = route_packet.get("target_system", "")
            if target_system:
                system_records[target_system].append(record)
                system_route_counts[target_system][hemisphere] += 1
                hemisphere_route_system_counts[hemisphere][target_system] += 1

    families = sorted(family_records)
    anchors = sorted(anchor_records)
    target_systems = sorted(system_records)
    top_levels = sorted(top_level_records)

    for family in families:
        family_page_map[family] = (
            f"VA-FAMILY-{slugify(family)}",
            VISUAL_ATLAS_SUBDIR / f"family_{slugify(family)}.md",
        )
    for anchor in anchors:
        anchor_page_map[anchor] = (
            f"VA-ANCHOR-{anchor}",
            VISUAL_ATLAS_SUBDIR / f"anchor_{slugify(anchor)}.md",
        )
    for target_system in target_systems:
        target_page_map[target_system] = (
            f"VA-TARGET-{slugify(target_system)}",
            VISUAL_ATLAS_SUBDIR / f"target_system_{slugify(target_system)}.md",
        )
    for top_level in top_levels:
        locator_page_map[top_level] = (
            f"VA-LOCATOR-{slugify(top_level)}",
            VISUAL_ATLAS_SUBDIR / f"record_locator_{slugify(top_level)}.md",
        )

    def unique_system_record_count(target_system: str) -> int:
        return len({record["record_id"] for record in system_records[target_system]})

    for record in records:
        record_id = record["record_id"]
        record_node_id = f"REC-{record_id}"
        primary_hemisphere = record.get("primary_hemisphere", "MATH")
        secondary_hemisphere = opposite_hemisphere(primary_hemisphere)
        primary_route = route_lookup(record, primary_hemisphere)
        secondary_route = route_lookup(record, secondary_hemisphere)
        first_anchor = (record.get("basis_anchor_ids") or [""])[0]
        family = record.get("family", "")
        top_level = record.get("top_level", "<unknown>")

        primary_page_id = "VA-HEM-MATH" if primary_hemisphere == "MATH" else "VA-HEM-MYTH"
        secondary_page_id = "VA-HEM-MYTH" if primary_hemisphere == "MATH" else "VA-HEM-MATH"
        family_page_id = family_page_map[family][0]
        anchor_page_id = anchor_page_map[first_anchor][0] if first_anchor else ""
        target_page_ids = []
        for target_system in {
            primary_route.get("target_system", ""),
            secondary_route.get("target_system", ""),
        } - {""}:
            target_page_ids.append(target_page_map[target_system][0])
        target_page_ids.sort()
        locator_page_id = locator_page_map[top_level][0]

        primary_hub = MATH_HUB_ID if primary_hemisphere == "MATH" else MYTH_HUB_ID
        opposite_hub = MYTH_HUB_ID if primary_hub == MATH_HUB_ID else MATH_HUB_ID
        overview_edge_ids = [
            f"VA-{direct_edge_lookup[(record_id, primary_hemisphere)]['edge_id']}",
            f"VA-SPINE-{primary_hub}-GC0",
            f"VA-SPINE-GC0-{opposite_hub}",
        ]
        composer_seed_id = f"COMP-SEED-{record_id}"
        synthesis_seed_id = f"SYNTH-SEED-{record_id}"

        atlas_page_ids = [
            "VA-OVERVIEW",
            primary_page_id,
            secondary_page_id,
            family_page_id,
            anchor_page_id,
            locator_page_id,
            *target_page_ids,
        ]
        atlas_page_ids = [page_id for page_id in atlas_page_ids if page_id]

        record_locator_rows[record_id] = {
            "record_id": record_id,
            "title": record.get("title", ""),
            "relative_path": record.get("relative_path", ""),
            "top_level": top_level,
            "primary_hemisphere": primary_hemisphere,
            "secondary_hemisphere": secondary_hemisphere,
            "target_systems": {
                "MATH": route_lookup(record, "MATH").get("target_system", ""),
                "MYTH": route_lookup(record, "MYTH").get("target_system", ""),
            },
            "first_anchor": first_anchor,
            "atlas_page_ids": atlas_page_ids,
            "primary_hemisphere_page_id": primary_page_id,
            "secondary_hemisphere_page_id": secondary_page_id,
            "overview_page_id": "VA-OVERVIEW",
            "family_page_id": family_page_id,
            "anchor_page_id": anchor_page_id,
            "target_system_page_ids": target_page_ids,
            "record_locator_page_id": locator_page_id,
            "route_ids": {
                "MATH": route_lookup(record, "MATH").get("route_id", ""),
                "MYTH": route_lookup(record, "MYTH").get("route_id", ""),
            },
            "overview_edge_ids": overview_edge_ids,
            "composer_seed_id": composer_seed_id,
            "synthesis_seed_id": synthesis_seed_id,
            "composer_seed_groups": composer_seed_groups.get(record_id, []),
            "synthesis_seed_groups": synthesis_seed_groups.get(record_id, []),
            "docs_gate_status": docs_gate_status,
        }

        record_nodes.append(
            {
                "node_id": record_node_id,
                "node_type": "record",
                "record_id": record_id,
                "label": short_text(record.get("title", "")),
                "relative_path": record.get("relative_path", ""),
                "primary_hemisphere": primary_hemisphere,
                "family": family,
                "first_anchor": first_anchor,
                "locator_page_id": locator_page_id,
            }
        )

        for hemisphere in ("MATH", "MYTH"):
            edge_packet = direct_edge_lookup[(record_id, hemisphere)]
            edges.append(
                {
                    "edge_id": f"VA-{edge_packet['edge_id']}",
                    "edge_type": "record_to_hub",
                    "record_id": record_id,
                    "source_node_id": record_node_id,
                    "target_node_id": edge_packet.get("target_hub_id", ""),
                    "hemisphere": hemisphere,
                    "weight": edge_packet.get("weight", 0.0),
                    "route_id": route_lookup(record, hemisphere).get("route_id", ""),
                    "source_edge_id": edge_packet["edge_id"],
                    "docs_gate_status": docs_gate_status,
                }
            )
        edges.append(
            {
                "edge_id": f"VA-GC0-{record_id}",
                "edge_type": "record_to_unified_hub",
                "record_id": record_id,
                "source_node_id": record_node_id,
                "target_node_id": UNIFIED_HUB_ID,
                "weight": 1.0,
                "route_ids": [
                    route_lookup(record, "MATH").get("route_id", ""),
                    route_lookup(record, "MYTH").get("route_id", ""),
                ],
                "docs_gate_status": docs_gate_status,
            }
        )
        edges.append(
            {
                "edge_id": f"VA-FAMILY-{record_id}",
                "edge_type": "record_to_family",
                "record_id": record_id,
                "source_node_id": record_node_id,
                "target_node_id": node_id("FAMILY", family),
                "docs_gate_status": docs_gate_status,
            }
        )
        for target_system in {
            route_lookup(record, "MATH").get("target_system", ""),
            route_lookup(record, "MYTH").get("target_system", ""),
        } - {""}:
            edges.append(
                {
                    "edge_id": f"VA-SYSTEM-{record_id}-{slugify(target_system)}",
                    "edge_type": "record_to_target_system",
                    "record_id": record_id,
                    "source_node_id": record_node_id,
                    "target_node_id": node_id("SYSTEM", target_system),
                    "target_system": target_system,
                    "docs_gate_status": docs_gate_status,
                }
            )
        for anchor in record.get("basis_anchor_ids", []):
            edges.append(
                {
                    "edge_id": f"VA-ANCHOR-{record_id}-{anchor}",
                    "edge_type": "record_to_anchor",
                    "record_id": record_id,
                    "source_node_id": record_node_id,
                    "target_node_id": node_id("ANCHOR", anchor),
                    "anchor_id": anchor,
                    "docs_gate_status": docs_gate_status,
                }
            )

    hub_nodes = [
        {
            "node_id": UNIFIED_HUB_ID,
            "node_type": "hub",
            "label": "Unified Corpus Hub",
            "page_id": "VA-OVERVIEW",
        },
        {
            "node_id": MATH_HUB_ID,
            "node_type": "hub",
            "label": "MATH Hemisphere Hub",
            "page_id": "VA-HEM-MATH",
        },
        {
            "node_id": MYTH_HUB_ID,
            "node_type": "hub",
            "label": "MYTH Hemisphere Hub",
            "page_id": "VA-HEM-MYTH",
        },
    ]
    hemisphere_nodes = [
        {
            "node_id": "HEM-MATH",
            "node_type": "hemisphere",
            "label": "MATH Hemisphere",
            "hub_id": MATH_HUB_ID,
            "page_id": "VA-HEM-MATH",
        },
        {
            "node_id": "HEM-MYTH",
            "node_type": "hemisphere",
            "label": "MYTH Hemisphere",
            "hub_id": MYTH_HUB_ID,
            "page_id": "VA-HEM-MYTH",
        },
    ]
    family_nodes = [
        {
            "node_id": node_id("FAMILY", family),
            "node_type": "family",
            "label": FAMILY_LABELS.get(family, family),
            "family": family,
            "page_id": family_page_map[family][0],
        }
        for family in families
    ]
    system_nodes = [
        {
            "node_id": node_id("SYSTEM", target_system),
            "node_type": "target_system",
            "label": target_system,
            "target_system": target_system,
            "page_id": target_page_map[target_system][0],
        }
        for target_system in target_systems
    ]
    anchor_nodes = [
        {
            "node_id": node_id("ANCHOR", anchor),
            "node_type": "anchor",
            "label": anchor,
            "anchor_id": anchor,
            "page_id": anchor_page_map[anchor][0],
        }
        for anchor in anchors
    ]

    edges.extend(
        [
            {
                "edge_id": "VA-HEM-MATH-HUB",
                "edge_type": "hemisphere_to_hub",
                "source_node_id": "HEM-MATH",
                "target_node_id": MATH_HUB_ID,
                "docs_gate_status": docs_gate_status,
            },
            {
                "edge_id": "VA-HEM-MYTH-HUB",
                "edge_type": "hemisphere_to_hub",
                "source_node_id": "HEM-MYTH",
                "target_node_id": MYTH_HUB_ID,
                "docs_gate_status": docs_gate_status,
            },
            {
                "edge_id": f"VA-SPINE-{MATH_HUB_ID}-GC0",
                "edge_type": "hub_spine",
                "source_node_id": MATH_HUB_ID,
                "target_node_id": UNIFIED_HUB_ID,
                "docs_gate_status": docs_gate_status,
            },
            {
                "edge_id": f"VA-SPINE-GC0-{MATH_HUB_ID}",
                "edge_type": "hub_spine",
                "source_node_id": UNIFIED_HUB_ID,
                "target_node_id": MATH_HUB_ID,
                "docs_gate_status": docs_gate_status,
            },
            {
                "edge_id": f"VA-SPINE-{MYTH_HUB_ID}-GC0",
                "edge_type": "hub_spine",
                "source_node_id": MYTH_HUB_ID,
                "target_node_id": UNIFIED_HUB_ID,
                "docs_gate_status": docs_gate_status,
            },
            {
                "edge_id": f"VA-SPINE-GC0-{MYTH_HUB_ID}",
                "edge_type": "hub_spine",
                "source_node_id": UNIFIED_HUB_ID,
                "target_node_id": MYTH_HUB_ID,
                "docs_gate_status": docs_gate_status,
            },
        ]
    )

    nodes = sorted(
        [*hub_nodes, *hemisphere_nodes, *family_nodes, *system_nodes, *anchor_nodes, *record_nodes],
        key=lambda item: (item["node_type"], item["node_id"]),
    )
    edges.sort(key=lambda item: item["edge_id"])

    pages: list[dict[str, Any]] = []
    markdown_pages: dict[str, str] = {}

    current_rel = FIXED_PAGE_SPECS[0][2]
    surface_rows = [
        [
            rel_link(current_rel, rel_path, title),
            page_id,
            page_type.replace("_", " "),
        ]
        for page_id, title, rel_path, page_type in FIXED_PAGE_SPECS[1:]
    ]
    linked_outputs = "\n".join(f"- `{path}`" for path in output_paths())
    register_page(
        pages,
        markdown_pages,
        page_id="VA-INDEX",
        title="Visual Atlas Index",
        relative_path=current_rel,
        page_type="main_index",
        slice_payload={"layer": "visual_atlas"},
        counts={
            "record_count": len(records),
            "page_count": 8 + len(families) + len(anchors) + len(target_systems) + len(top_levels),
            "family_shards": len(families),
            "anchor_shards": len(anchors),
            "target_system_shards": len(target_systems),
            "locator_shards": len(top_levels),
        },
        content=f"""# Visual Atlas Index

Docs gate: `{docs_gate_status}`

## Summary

- records: `{len(records)}`
- visual atlas nodes: `{len(nodes)}`
- visual atlas edges: `{len(edges)}`
- fixed atlas pages: `8`
- family shards: `{len(families)}`
- anchor shards: `{len(anchors)}`
- target-system shards: `{len(target_systems)}`
- record-locator shards: `{len(top_levels)}`

## Main Surfaces

{markdown_table(["Page", "Page ID", "Type"], surface_rows)}

## Machine Outputs

{linked_outputs}

## Commands

{command_block()}
""",
    )

    current_rel = FIXED_PAGE_SPECS[1][2]
    family_lines = [
        '  GC0["GC0-UNIFIED-CORPUS"]',
        f'  HM["{MATH_HUB_ID} ({hemisphere_primary_counts["MATH"]} primary)"]',
        f'  HY["{MYTH_HUB_ID} ({hemisphere_primary_counts["MYTH"]} primary)"]',
        "  HM --> GC0",
        "  GC0 --> HY",
    ]
    for family in families:
        family_node = node_id("FAM", family)
        family_lines.append(f'  {family_node}["{family} ({len(family_records[family])})"]')
        dominant = "HM" if family_primary_counts[(family, "MATH")] >= family_primary_counts[(family, "MYTH")] else "HY"
        family_lines.append(f"  {dominant} --> {family_node}")
    target_lines = [
        '  HM["HC-MATH"]',
        '  GC0["GC0-UNIFIED-CORPUS"]',
        '  HY["HC-MYTH"]',
        "  HM --> GC0",
        "  GC0 --> HY",
    ]
    for target_system in target_systems:
        target_node = node_id("SYS", target_system)
        target_lines.append(f'  {target_node}["{target_system} ({unique_system_record_count(target_system)})"]')
        if system_route_counts[target_system]["MATH"]:
            target_lines.append(f"  HM --> {target_node}")
        if system_route_counts[target_system]["MYTH"]:
            target_lines.append(f"  HY --> {target_node}")
    anchor_lines = ['  GC0["GC0-UNIFIED-CORPUS"]']
    for anchor in anchors:
        anchor_node = node_id("ANC", anchor)
        anchor_lines.append(f'  {anchor_node}["{anchor} ({anchor_member_counts[anchor]})"]')
        anchor_lines.append(f"  GC0 --> {anchor_node}")
    register_page(
        pages,
        markdown_pages,
        page_id="VA-OVERVIEW",
        title="Corpus Overview Map",
        relative_path=current_rel,
        page_type="overview",
        slice_payload={"layer": "visual_atlas", "focus": "record_to_hub"},
        counts={
            "record_count": len(records),
            "family_count": len(families),
            "target_system_count": len(target_systems),
            "anchor_count": len(anchors),
        },
        content=f"""# Corpus Overview Map

Docs gate: `{docs_gate_status}`

## Hub Spine

{mermaid_block([
    '  HM["HC-MATH"]',
    '  GC0["GC0-UNIFIED-CORPUS"]',
    '  HY["HC-MYTH"]',
    '  HM --> GC0',
    '  GC0 --> HY',
    '  HY --> GC0',
    '  GC0 --> HM',
])}

## Family Lines

{mermaid_block(family_lines)}

## Target Systems

{mermaid_block(target_lines)}

## Anchor Lattice

{mermaid_block(anchor_lines)}

## Jump Points

- {rel_link(current_rel, main_page_map["VA-HEM-MATH"], "MATH Route Topology Atlas")}
- {rel_link(current_rel, main_page_map["VA-HEM-MYTH"], "MYTH Route Topology Atlas")}
- {rel_link(current_rel, main_page_map["VA-ANCHOR"], "Anchor Crosswalk Atlas")}
- {rel_link(current_rel, main_page_map["VA-TARGET-SYSTEM"], "Target-System Atlas")}
- {rel_link(current_rel, main_page_map["VA-LOCATOR"], "Record Locator Index")}

## Commands

{command_block()}
""",
    )

    for hemisphere, page_id, rel_path in (
        ("MATH", "VA-HEM-MATH", FIXED_PAGE_SPECS[2][2]),
        ("MYTH", "VA-HEM-MYTH", FIXED_PAGE_SPECS[3][2]),
    ):
        other = opposite_hemisphere(hemisphere)
        system_rows = []
        topology_lines = [
            f'  HUB["{"HC-MATH" if hemisphere == "MATH" else "HC-MYTH"}"]',
            '  GC0["GC0-UNIFIED-CORPUS"]',
            "  HUB --> GC0",
        ]
        for target_system, count in sorted(
            hemisphere_route_system_counts[hemisphere].items(),
            key=lambda item: (-item[1], item[0]),
        ):
            system_rows.append(
                [
                    target_system,
                    str(count),
                    rel_link(rel_path, target_page_map[target_system][1], target_page_map[target_system][0]),
                ]
            )
            target_node = node_id("SYS", f"{hemisphere}-{target_system}")
            topology_lines.append(f'  {target_node}["{target_system} ({count})"]')
            topology_lines.append(f"  HUB --> {target_node}")
        family_rows = []
        for family in families:
            primary_count = family_primary_counts[(family, hemisphere)]
            secondary_count = family_primary_counts[(family, other)]
            family_rows.append(
                [
                    family,
                    str(primary_count),
                    str(secondary_count),
                    rel_link(rel_path, family_page_map[family][1], family_page_map[family][0]),
                ]
            )
        register_page(
            pages,
            markdown_pages,
            page_id=page_id,
            title=f"{hemisphere} Route Topology Atlas",
            relative_path=rel_path,
            page_type="hemisphere",
            slice_payload={"facet": "hemisphere", "value": hemisphere},
            counts={
                "route_ref_count": len(records),
                "primary_record_count": hemisphere_primary_counts[hemisphere],
                "secondary_record_count": hemisphere_primary_counts[other],
                "target_system_count": len(hemisphere_route_system_counts[hemisphere]),
            },
            content=f"""# {hemisphere} Route Topology Atlas

Docs gate: `{docs_gate_status}`

## Route Topology

{mermaid_block(topology_lines)}

## Family Shards

{markdown_table(["Family", "Primary", "Secondary", "Shard"], family_rows)}

## Target-System Shards

{markdown_table(["Target System", "Route Refs", "Shard"], system_rows or [["<none>", "0", "-"]])}

## Commands

{command_block()}
""",
        )

    current_rel = FIXED_PAGE_SPECS[4][2]
    anchor_rows = []
    anchor_graph = ['  HM["HC-MATH"]', '  HY["HC-MYTH"]']
    for anchor in anchors:
        anchor_rows.append(
            [
                anchor,
                str(anchor_primary_counts[anchor]["MATH"]),
                str(anchor_primary_counts[anchor]["MYTH"]),
                rel_link(current_rel, anchor_page_map[anchor][1], anchor_page_map[anchor][0]),
            ]
        )
        anchor_node = node_id("A", anchor)
        anchor_graph.append(f'  {anchor_node}["{anchor} ({anchor_member_counts[anchor]})"]')
        if anchor_primary_counts[anchor]["MATH"]:
            anchor_graph.append(f"  HM --> {anchor_node}")
        if anchor_primary_counts[anchor]["MYTH"]:
            anchor_graph.append(f"  HY --> {anchor_node}")
    register_page(
        pages,
        markdown_pages,
        page_id="VA-ANCHOR",
        title="Anchor Crosswalk Atlas",
        relative_path=current_rel,
        page_type="anchor_index",
        slice_payload={"facet": "anchor"},
        counts={"anchor_count": len(anchors), "record_count": len(records)},
        content=f"""# Anchor Crosswalk Atlas

Docs gate: `{docs_gate_status}`

## Crosswalk Graph

{mermaid_block(anchor_graph)}

## Anchor Shards

{markdown_table(["Anchor", "Primary MATH", "Primary MYTH", "Shard"], anchor_rows)}

## Commands

{command_block()}
""",
    )

    current_rel = FIXED_PAGE_SPECS[5][2]
    system_rows = []
    system_graph = [
        '  HM["HC-MATH"]',
        '  HY["HC-MYTH"]',
        '  GC0["GC0-UNIFIED-CORPUS"]',
        "  HM --> GC0",
        "  GC0 --> HY",
    ]
    for target_system in target_systems:
        system_rows.append(
            [
                target_system,
                str(system_route_counts[target_system]["MATH"]),
                str(system_route_counts[target_system]["MYTH"]),
                rel_link(current_rel, target_page_map[target_system][1], target_page_map[target_system][0]),
            ]
        )
        system_node = node_id("TS", target_system)
        system_graph.append(f'  {system_node}["{target_system} ({unique_system_record_count(target_system)})"]')
        if system_route_counts[target_system]["MATH"]:
            system_graph.append(f"  HM --> {system_node}")
        if system_route_counts[target_system]["MYTH"]:
            system_graph.append(f"  HY --> {system_node}")
    register_page(
        pages,
        markdown_pages,
        page_id="VA-TARGET-SYSTEM",
        title="Target-System Atlas",
        relative_path=current_rel,
        page_type="target_system_index",
        slice_payload={"facet": "target_system"},
        counts={"target_system_count": len(target_systems), "record_count": len(records)},
        content=f"""# Target-System Atlas

Docs gate: `{docs_gate_status}`

## Target-System Graph

{mermaid_block(system_graph)}

## Target-System Shards

{markdown_table(["Target System", "MATH Route Refs", "MYTH Route Refs", "Shard"], system_rows)}

## Commands

{command_block()}
""",
    )

    current_rel = FIXED_PAGE_SPECS[6][2]
    locator_rows = []
    for top_level in top_levels:
        locator_rows.append(
            [
                top_level,
                str(len(top_level_records[top_level])),
                rel_link(current_rel, locator_page_map[top_level][1], locator_page_map[top_level][0]),
            ]
        )
    register_page(
        pages,
        markdown_pages,
        page_id="VA-LOCATOR",
        title="Record Locator Index",
        relative_path=current_rel,
        page_type="record_locator_index",
        slice_payload={"facet": "top_level"},
        counts={"top_level_count": len(top_levels), "record_count": len(records)},
        content=f"""# Record Locator Index

Docs gate: `{docs_gate_status}`

## Top-Level Root Shards

{markdown_table(["Top Level Root", "Records", "Shard"], locator_rows)}

## Locator Contract

- every canonical record appears once in exactly one top-level locator shard
- each locator row links to primary and secondary hemisphere atlas shards
- each locator row carries both route ids plus composer and synthesis seed ids

## Commands

{command_block()}
""",
    )

    current_rel = FIXED_PAGE_SPECS[7][2]
    coverage_rows = [
        ["Records", str(len(records))],
        ["Node registry", str(len(nodes))],
        ["Edge registry", str(len(edges))],
        ["Page registry", str(8 + len(families) + len(anchors) + len(target_systems) + len(top_levels))],
        ["Record locator rows", str(len(record_locator_rows))],
        ["Family shards", str(len(families))],
        ["Anchor shards", str(len(anchors))],
        ["Target-system shards", str(len(target_systems))],
        ["Record-locator shards", str(len(top_levels))],
    ]
    facet_rows = [
        [facet, str(value)]
        for facet, value in sorted(navigator_facet_index.get("facet_cardinalities", {}).items())
        if facet in {"anchor", "family", "target_system", "top_level"}
    ]
    register_page(
        pages,
        markdown_pages,
        page_id="VA-COVERAGE",
        title="Atlas Coverage Receipt",
        relative_path=current_rel,
        page_type="coverage",
        slice_payload={"layer": "visual_atlas", "coverage": "full"},
        counts={
            "record_count": len(records),
            "page_count": 8 + len(families) + len(anchors) + len(target_systems) + len(top_levels),
            "docs_gate_status": docs_gate_status,
        },
        content=f"""# Atlas Coverage Receipt

Docs gate: `{docs_gate_status}`

## Atlas Counts

{markdown_table(["Metric", "Value"], coverage_rows)}

## Facet Coverage

{markdown_table(["Facet", "Cardinality"], facet_rows)}

## Machine Outputs

{linked_outputs}
""",
    )

    for family in families:
        current_rel = family_page_map[family][1]
        family_slice = sorted(
            family_records[family],
            key=lambda item: (-item.get("salience", 0.0), item.get("relative_path", "").lower()),
        )
        top_records = family_slice[:20]
        record_rows = []
        for record in top_records:
            locator_entry = record_locator_rows[record["record_id"]]
            record_rows.append(
                [
                    record["record_id"],
                    short_text(record.get("title", ""), 42),
                    record.get("primary_hemisphere", ""),
                    locator_entry["route_ids"]["MATH"],
                    locator_entry["route_ids"]["MYTH"],
                ]
            )
        graph_lines = [
            f'  FAM["{family} ({len(family_slice)})"]',
            '  HM["HC-MATH"]',
            '  HY["HC-MYTH"]',
            "  FAM --> HM",
            "  FAM --> HY",
        ]
        target_nodes = sorted(
            {
                route_lookup(record, "MATH").get("target_system", "")
                for record in family_slice
            }
            | {
                route_lookup(record, "MYTH").get("target_system", "")
                for record in family_slice
            }
            - {""}
        )[:8]
        for target_system in target_nodes:
            target_node = node_id("TSF", target_system)
            graph_lines.append(f'  {target_node}["{target_system}"]')
            graph_lines.append(f"  FAM --> {target_node}")
        register_page(
            pages,
            markdown_pages,
            page_id=family_page_map[family][0],
            title=f"Family Atlas: {family}",
            relative_path=current_rel,
            page_type="family_shard",
            slice_payload={"facet": "family", "value": family},
            counts={
                "record_count": len(family_slice),
                "primary_math": family_primary_counts[(family, "MATH")],
                "primary_myth": family_primary_counts[(family, "MYTH")],
                "bridge_records": family_bridge_counts[family],
            },
            content=f"""# Family Atlas: {family}

Docs gate: `{docs_gate_status}`

## Topology

{mermaid_block(graph_lines)}

## Stats

- label: `{FAMILY_LABELS.get(family, family)}`
- records: `{len(family_slice)}`
- primary MATH: `{family_primary_counts[(family, "MATH")]}`
- primary MYTH: `{family_primary_counts[(family, "MYTH")]}`
- bridge records: `{family_bridge_counts[family]}`
- composer starter groups present: `{len({group for record in family_slice for group in composer_seed_groups.get(record['record_id'], [])})}`
- synthesis starter groups present: `{len({group for record in family_slice for group in synthesis_seed_groups.get(record['record_id'], [])})}`

## Top Records

{markdown_table(["Record", "Title", "Primary", "MATH Route", "MYTH Route"], record_rows or [["<none>", "-", "-", "-", "-"]])}

## Commands

{command_block(family=family)}
""",
        )

    for anchor in anchors:
        current_rel = anchor_page_map[anchor][1]
        anchor_slice = sorted(
            {record["record_id"]: record for record in anchor_records[anchor]}.values(),
            key=lambda item: (-item.get("salience", 0.0), item.get("relative_path", "").lower()),
        )
        family_counts = Counter(record.get("family", "") for record in anchor_slice)
        record_rows = [
            [
                record["record_id"],
                short_text(record.get("title", ""), 42),
                record.get("primary_hemisphere", ""),
                record.get("family", ""),
            ]
            for record in anchor_slice[:20]
        ]
        register_page(
            pages,
            markdown_pages,
            page_id=anchor_page_map[anchor][0],
            title=f"Anchor Atlas: {anchor}",
            relative_path=current_rel,
            page_type="anchor_shard",
            slice_payload={"facet": "anchor", "value": anchor},
            counts={
                "record_count": len(anchor_slice),
                "primary_math": anchor_primary_counts[anchor]["MATH"],
                "primary_myth": anchor_primary_counts[anchor]["MYTH"],
            },
            content=f"""# Anchor Atlas: {anchor}

Docs gate: `{docs_gate_status}`

## Crosswalk

{mermaid_block([
    f'  ANC["{anchor} ({len(anchor_slice)})"]',
    '  HM["HC-MATH"]',
    '  HY["HC-MYTH"]',
    '  ANC --> HM',
    '  ANC --> HY',
])}

## Family Mix

{markdown_table(["Family", "Records"], [[family, str(count)] for family, count in family_counts.most_common(8)] or [["<none>", "0"]])}

## Top Records

{markdown_table(["Record", "Title", "Primary", "Family"], record_rows or [["<none>", "-", "-", "-"]])}

## Commands

{command_block()}
""",
        )

    for target_system in target_systems:
        current_rel = target_page_map[target_system][1]
        system_slice = sorted(
            {record["record_id"]: record for record in system_records[target_system]}.values(),
            key=lambda item: (-item.get("salience", 0.0), item.get("relative_path", "").lower()),
        )
        family_counts = Counter(record.get("family", "") for record in system_slice)
        record_rows = [
            [
                record["record_id"],
                short_text(record.get("title", ""), 42),
                route_lookup(record, "MATH").get("target_system", ""),
                route_lookup(record, "MYTH").get("target_system", ""),
            ]
            for record in system_slice[:20]
        ]
        register_page(
            pages,
            markdown_pages,
            page_id=target_page_map[target_system][0],
            title=f"Target-System Atlas: {target_system}",
            relative_path=current_rel,
            page_type="target_system_shard",
            slice_payload={"facet": "target_system", "value": target_system},
            counts={
                "record_count": len(system_slice),
                "math_route_refs": system_route_counts[target_system]["MATH"],
                "myth_route_refs": system_route_counts[target_system]["MYTH"],
            },
            content=f"""# Target-System Atlas: {target_system}

Docs gate: `{docs_gate_status}`

## Topology

{mermaid_block([
    f'  SYS["{target_system} ({len(system_slice)})"]',
    '  HM["HC-MATH"]',
    '  HY["HC-MYTH"]',
    '  HM --> SYS',
    '  HY --> SYS',
])}

## Family Mix

{markdown_table(["Family", "Records"], [[family, str(count)] for family, count in family_counts.most_common(8)] or [["<none>", "0"]])}

## Top Records

{markdown_table(["Record", "Title", "MATH Target", "MYTH Target"], record_rows or [["<none>", "-", "-", "-"]])}

## Commands

{command_block()}
""",
        )

    for top_level in top_levels:
        current_rel = locator_page_map[top_level][1]
        shard_records = sorted(
            top_level_records[top_level],
            key=lambda item: item.get("relative_path", "").lower(),
        )
        locator_rows = []
        for record in shard_records:
            locator_entry = record_locator_rows[record["record_id"]]
            locator_rows.append(
                [
                    record["record_id"],
                    short_text(record.get("title", ""), 34),
                    rel_link(current_rel, main_page_map[locator_entry["primary_hemisphere_page_id"]], locator_entry["primary_hemisphere"]),
                    rel_link(current_rel, main_page_map[locator_entry["secondary_hemisphere_page_id"]], locator_entry["secondary_hemisphere"]),
                    rel_link(current_rel, family_page_map[record.get("family", "")][1], record.get("family", "")),
                    rel_link(current_rel, anchor_page_map[locator_entry["first_anchor"]][1], locator_entry["first_anchor"]) if locator_entry["first_anchor"] else "-",
                    locator_entry["route_ids"]["MATH"],
                    locator_entry["route_ids"]["MYTH"],
                    locator_entry["composer_seed_id"],
                    locator_entry["synthesis_seed_id"],
                ]
            )
        register_page(
            pages,
            markdown_pages,
            page_id=locator_page_map[top_level][0],
            title=f"Record Locator: {top_level}",
            relative_path=current_rel,
            page_type="record_locator_shard",
            slice_payload={"facet": "top_level", "value": top_level},
            counts={"record_count": len(shard_records)},
            content=f"""# Record Locator: {top_level}

Docs gate: `{docs_gate_status}`

## Records

{markdown_table(
    ["Record", "Title", "Primary", "Secondary", "Family", "Anchor", "MATH Route", "MYTH Route", "Composer Seed", "Synthesis Seed"],
    locator_rows or [["<none>", "-", "-", "-", "-", "-", "-", "-", "-", "-"]],
)}

## Commands

{command_block()}
""",
        )

    node_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "node_count": len(nodes),
        "node_counts": dict(sorted(Counter(node["node_type"] for node in nodes).items())),
        "nodes": nodes,
    }
    edge_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "edge_count": len(edges),
        "edge_counts": dict(sorted(Counter(edge["edge_type"] for edge in edges).items())),
        "edges": edges,
    }
    page_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "page_count": len(pages),
        "page_counts": dict(sorted(Counter(page["page_type"] for page in pages).items())),
        "pages": sorted(pages, key=lambda item: item["page_id"]),
    }
    record_locator_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "record_count": len(record_locator_rows),
        "records": dict(sorted(record_locator_rows.items())),
    }
    atlas_manifest = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "counts": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "page_count": len(pages),
            "record_locator_rows": len(record_locator_rows),
            "family_shards": len(families),
            "anchor_shards": len(anchors),
            "target_system_shards": len(target_systems),
            "record_locator_shards": len(top_levels),
        },
        "facet_cardinalities": {
            "family": len(families),
            "anchor": len(anchors),
            "target_system": len(target_systems),
            "top_level": len(top_levels),
        },
        "commands": {
            "derive": "python -m self_actualize.runtime.derive_myth_math_hemisphere_brain",
            "verify": "python -m self_actualize.runtime.verify_myth_math_hemisphere_brain",
            "query": "python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id <record_id>",
            "compose": "python -m self_actualize.runtime.compose_myth_math_hemisphere_routes record --record-id <record_id>",
            "synthesize": "python -m self_actualize.runtime.synthesize_myth_math_hemisphere_routes record --record-id <record_id>",
        },
        "outputs": {
            "node_registry": str(VISUAL_ATLAS_NODE_REGISTRY_PATH),
            "edge_registry": str(VISUAL_ATLAS_EDGE_REGISTRY_PATH),
            "page_registry": str(VISUAL_ATLAS_PAGE_REGISTRY_PATH),
            "record_locator_registry": str(VISUAL_ATLAS_RECORD_LOCATOR_REGISTRY_PATH),
            "manifest": str(VISUAL_ATLAS_MANIFEST_PATH),
            "record_registry": str(RECORD_REGISTRY_PATH),
            "route_manifest": str(ROUTE_MANIFEST_PATH),
            "navigator_facet_index": str(NAVIGATOR_FACET_INDEX_PATH),
            "composer_seed_registry": str(COMPOSER_SEED_REGISTRY_PATH),
            "synthesis_seed_registry": str(SYNTHESIS_SEED_REGISTRY_PATH),
        },
        "page_ids": sorted(page["page_id"] for page in pages),
    }
    return (
        node_registry,
        edge_registry,
        page_registry,
        record_locator_registry,
        atlas_manifest,
        markdown_pages,
    )
