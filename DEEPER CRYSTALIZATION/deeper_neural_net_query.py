#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from chapter_frontier_compiler import CHAPTER_FRONTIER_CODES, build_frontier_payload
from frontier_plan_lattice import ARTIFACT_LANES, INTEGRATION_PASSES, PLAN_GRID_NAME, PLAN_LENSES, plan_paths
from nervous_system_core import (
    lookup_tokens,
    normalize_lookup_text,
    presentation_name,
    slugify,
    write_json,
    write_text,
)


PROJECT_ROOT = Path(__file__).resolve().parent
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
NETWORK_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM" / "13_DEEPER_NEURAL_NET"
RUNTIME_DIR = NETWORK_ROOT / "09_RUNTIME"
QUERY_LAST_DIR = NETWORK_ROOT / "10_QUERY" / "last"
DEFAULT_LIMIT = 10


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def network_paths() -> dict[str, Path]:
    return {
        "network_manifest": RUNTIME_DIR / "00_network_manifest.json",
        "element_registry": RUNTIME_DIR / "01_element_registry.json",
        "ordered_pair_matrix": RUNTIME_DIR / "02_ordered_pair_matrix.json",
        "query_index": RUNTIME_DIR / "03_query_index.json",
        "facet_index": RUNTIME_DIR / "04_facet_index.json",
        "neighbor_index": RUNTIME_DIR / "05_neighbor_index.json",
        "zero_point_index": RUNTIME_DIR / "06_zero_point_index.json",
    }


def plan_runtime_paths() -> dict[str, Path]:
    paths = plan_paths(ACTIVE_ROOT)
    return {
        "plan_manifest": paths["manifest"],
        "plan_grid_json": paths["grid_json"],
        "plan_grid_markdown": paths["grid_markdown"],
        "execution_tiers_markdown": paths["execution_tiers"],
        "dependency_routes_markdown": paths["dependency_routes"],
    }


def relation_kind(src: dict, dst: dict) -> str:
    same_element = src["element"] == dst["element"]
    same_family = src["family"] == dst["family"]
    if same_element and same_family:
        return "intra_family"
    if same_element:
        return "same_element_cross_family"
    if same_family:
        return "cross_element_same_family"
    return "cross_element_cross_family"


def canonical_pair_key(src_id: str, dst_id: str) -> str:
    ordered = sorted((src_id, dst_id))
    return f"{ordered[0]}::{ordered[1]}"


def canonical_pair_card(pair: dict, docs_by_id: dict[str, dict]) -> dict:
    src_id, dst_id = sorted((pair["src"], pair["dst"]))
    src = docs_by_id[src_id]
    dst = docs_by_id[dst_id]
    return {
        "src_id": src_id,
        "dst_id": dst_id,
        "canonical_pair_key": canonical_pair_key(src_id, dst_id),
        "score": pair["score"],
        "kind": relation_kind(src, dst),
        "shared_chapters": pair["shared_chapters"],
        "shared_appendices": pair["shared_appendices"],
        "shared_tokens": pair["shared_tokens"],
        "src_element": src["element"],
        "dst_element": dst["element"],
        "src_family": src["family"],
        "dst_family": dst["family"],
        "src_gate": src["gate"],
        "dst_gate": dst["gate"],
        "src_display_name": presentation_name(src["display_name"]),
        "dst_display_name": presentation_name(dst["display_name"]),
    }


def build_canonical_pair_map(pairs: list[dict], docs_by_id: dict[str, dict]) -> dict[str, dict]:
    canonical: dict[str, dict] = {}
    for pair in pairs:
        if pair["kind"] != "ordered_pair" or pair["src"] == pair["dst"]:
            continue
        key = canonical_pair_key(pair["src"], pair["dst"])
        existing = canonical.get(key)
        if existing is None or pair["score"] > existing["score"]:
            canonical[key] = canonical_pair_card(pair, docs_by_id)
    return canonical


def load_runtime() -> dict[str, object]:
    paths = network_paths()
    manifest = load_json(paths["network_manifest"])
    registry = load_json(paths["element_registry"])
    pairs = load_json(paths["ordered_pair_matrix"])
    query_index = load_json(paths["query_index"])
    facet_index = load_json(paths["facet_index"])
    neighbor_index = load_json(paths["neighbor_index"])
    zero_point_index = load_json(paths["zero_point_index"])
    docs_by_id = {item["id"]: item for item in registry}
    canonical_map = build_canonical_pair_map(pairs, docs_by_id)
    return {
        "paths": paths,
        "manifest": manifest,
        "registry": registry,
        "pairs": pairs,
        "query_index": query_index,
        "facet_index": facet_index,
        "neighbor_index": neighbor_index,
        "zero_point_index": zero_point_index,
        "docs_by_id": docs_by_id,
        "canonical_pair_map": canonical_map,
    }


def compact_doc_card(document: dict) -> dict:
    return {
        "id": document["id"],
        "display_name": presentation_name(document["display_name"]),
        "family": document["family"],
        "family_label": document.get("family_label"),
        "element": document["element"],
        "secondary_element": document.get("secondary_element"),
        "gate": document["gate"],
        "chapters": document["chapters"],
        "appendices": document["appendices"],
        "source_layer": document["source_layer"],
        "relative_path": document["relative_path"],
    }


def ambiguity_candidates(ids: list[str], docs_by_id: dict[str, dict]) -> list[dict]:
    ordered = sorted(ids, key=lambda item: (presentation_name(docs_by_id[item]["display_name"]), item))
    return [compact_doc_card(docs_by_id[item]) for item in ordered[:12]]


def maybe_doc_id(value: str) -> str | None:
    match = re.fullmatch(r"doc(\d{1,4})", value.strip().lower())
    if not match:
        return None
    return f"DOC{int(match.group(1)):04d}"


def resolve_document_ref(ref: str, runtime: dict[str, object]) -> dict:
    query_index = runtime["query_index"]
    docs_by_id = runtime["docs_by_id"]
    aliases = query_index["exact_aliases"]
    token_index = query_index["token_index"]

    doc_id = maybe_doc_id(ref)
    if doc_id and doc_id in docs_by_id:
        return {"status": "resolved", "document": docs_by_id[doc_id]}

    normalized = normalize_lookup_text(ref)
    if normalized in aliases:
        ids = aliases[normalized]
        if len(ids) == 1:
            return {"status": "resolved", "document": docs_by_id[ids[0]]}
        return {"status": "ambiguous", "candidates": ambiguity_candidates(ids, docs_by_id)}

    substring_matches: list[str] = []
    for doc_id, document in query_index["documents"].items():
        haystacks = [
            document["normalized_name"],
            document["normalized_display_name"],
            document["slug"].replace("_", " "),
            document["relative_path"].lower(),
        ]
        if any(normalized and normalized in haystack for haystack in haystacks):
            substring_matches.append(doc_id)
    if len(substring_matches) == 1:
        return {"status": "resolved", "document": docs_by_id[substring_matches[0]]}
    if substring_matches:
        return {"status": "ambiguous", "candidates": ambiguity_candidates(sorted(set(substring_matches)), docs_by_id)}

    token_scores: Counter[str] = Counter()
    query_tokens = lookup_tokens(ref)
    for token in query_tokens:
        for doc_id in token_index.get(token, []):
            token_scores[doc_id] += 1
    if token_scores:
        top_score = max(token_scores.values())
        best_ids = [doc_id for doc_id, score in token_scores.items() if score == top_score]
        if len(best_ids) == 1:
            return {"status": "resolved", "document": docs_by_id[best_ids[0]]}
        return {"status": "ambiguous", "candidates": ambiguity_candidates(best_ids, docs_by_id)}

    return {"status": "not_found", "candidates": []}


def split_pair_sections(pairs: list[dict], limit: int) -> dict[str, list[dict]]:
    overall = pairs[:limit]
    cross_element = [pair for pair in pairs if pair["src_element"] != pair["dst_element"]][:limit]
    cross_family = [pair for pair in pairs if pair["src_family"] != pair["dst_family"]][:limit]
    return {
        "overall": overall,
        "cross_element": cross_element,
        "cross_family": cross_family,
    }


def pair_endpoint_label(pair: dict, side: str) -> str:
    label = pair[f"{side}_display_name"]
    other_side = "dst" if side == "src" else "src"
    if label == pair[f"{other_side}_display_name"]:
        return f"{label} [{pair[f'{side}_id']}]"
    return label


def pair_label_disambiguators(pairs: list[dict]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for pair in pairs:
        for side in ("src", "dst"):
            label = pair[f"{side}_display_name"]
            mapping.setdefault(label, set()).add(pair[f"{side}_id"])
    return mapping


def render_pair_endpoint_label(pair: dict, side: str, duplicate_labels: dict[str, set[str]]) -> str:
    label = pair_endpoint_label(pair, side)
    display_name = pair[f"{side}_display_name"]
    if len(duplicate_labels.get(display_name, set())) > 1:
        return f"{display_name} [{pair[f'{side}_id']}]"
    return label


def build_doc_payload(ref: str, runtime: dict[str, object], limit: int) -> dict:
    resolved = resolve_document_ref(ref, runtime)
    if resolved["status"] != "resolved":
        return {
            "query_type": "doc",
            "query_ref": ref,
            "resolved_documents": [],
            "summary": {"status": resolved["status"], "title": "Document lookup unresolved"},
            "results": {"candidates": resolved.get("candidates", [])},
            "counts": {"candidate_count": len(resolved.get("candidates", []))},
            "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
            "manifest_refs": {name: str(path) for name, path in runtime["paths"].items()},
        }

    document = resolved["document"]
    neighbors = runtime["neighbor_index"]["neighbors"].get(document["id"], {})
    payload = {
        "query_type": "doc",
        "query_ref": ref,
        "resolved_documents": [compact_doc_card(document)],
        "summary": {
            "status": "resolved",
            "title": presentation_name(document["display_name"]),
            "detail": f"{document['id']} in {document['element']} / {document['family']} at gate {document['gate']}",
        },
        "results": {
            "document": compact_doc_card(document),
            "placement": {
                "element": document["element"],
                "secondary_element": document.get("secondary_element"),
                "family": document["family"],
                "family_label": document.get("family_label"),
                "gate": document["gate"],
                "source_layer": document["source_layer"],
            },
            "strongest_overall": neighbors.get("overall", [])[:limit],
            "strongest_cross_element": neighbors.get("cross_element", [])[:limit],
            "strongest_cross_family": neighbors.get("cross_family", [])[:limit],
        },
        "counts": {
            "resolved_document_count": 1,
            "overall_neighbor_count": len(neighbors.get("overall", [])),
            "cross_element_neighbor_count": len(neighbors.get("cross_element", [])),
            "cross_family_neighbor_count": len(neighbors.get("cross_family", [])),
        },
        "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
        "manifest_refs": {name: str(path) for name, path in runtime["paths"].items()},
    }
    return payload


def build_neighbors_payload(ref: str, mode: str, runtime: dict[str, object], limit: int) -> dict:
    payload = build_doc_payload(ref, runtime, limit)
    if payload["summary"]["status"] != "resolved":
        payload["query_type"] = "neighbors"
        return payload

    document = payload["resolved_documents"][0]
    neighbor_modes = {
        "overall": payload["results"]["strongest_overall"],
        "cross_element": payload["results"]["strongest_cross_element"],
        "cross_family": payload["results"]["strongest_cross_family"],
    }
    return {
        "query_type": "neighbors",
        "query_ref": ref,
        "resolved_documents": payload["resolved_documents"],
        "summary": {
            "status": "resolved",
            "title": f"Neighbors for {document['display_name']}",
            "detail": f"Mode {mode}, top {limit} entries",
        },
        "results": {
            "document": document,
            "mode": mode,
            "strongest_overall": payload["results"]["strongest_overall"],
            "strongest_cross_element": payload["results"]["strongest_cross_element"],
            "strongest_cross_family": payload["results"]["strongest_cross_family"],
            "selected_mode_results": neighbor_modes[mode],
        },
        "counts": payload["counts"],
        "live_docs_blocked": payload["live_docs_blocked"],
        "manifest_refs": payload["manifest_refs"],
    }


def build_pair_payload(src_ref: str, dst_ref: str, runtime: dict[str, object]) -> dict:
    src_resolved = resolve_document_ref(src_ref, runtime)
    dst_resolved = resolve_document_ref(dst_ref, runtime)
    unresolved = [item for item in (src_resolved, dst_resolved) if item["status"] != "resolved"]
    if unresolved:
        return {
            "query_type": "pair",
            "query_ref": {"src": src_ref, "dst": dst_ref},
            "resolved_documents": [],
            "summary": {"status": "unresolved", "title": "Pair lookup unresolved"},
            "results": {
                "src": src_resolved if src_resolved["status"] != "resolved" else compact_doc_card(src_resolved["document"]),
                "dst": dst_resolved if dst_resolved["status"] != "resolved" else compact_doc_card(dst_resolved["document"]),
            },
            "counts": {"candidate_count": sum(len(item.get("candidates", [])) for item in unresolved)},
            "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
            "manifest_refs": {name: str(path) for name, path in runtime["paths"].items()},
        }

    src_doc = src_resolved["document"]
    dst_doc = dst_resolved["document"]
    key = canonical_pair_key(src_doc["id"], dst_doc["id"])
    pair = runtime["canonical_pair_map"].get(key)
    if pair is None:
        summary = {"status": "not_found", "title": "Canonical pair not found"}
        results = {}
    else:
        summary = {
            "status": "resolved",
            "title": f"{pair_endpoint_label(pair, 'src')} <-> {pair_endpoint_label(pair, 'dst')}",
            "detail": f"Score {pair['score']} via {pair['kind']}",
        }
        results = {"pair": pair}

    return {
        "query_type": "pair",
        "query_ref": {"src": src_ref, "dst": dst_ref},
        "resolved_documents": [compact_doc_card(src_doc), compact_doc_card(dst_doc)],
        "summary": summary,
        "results": results,
        "counts": {"resolved_document_count": 2},
        "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
        "manifest_refs": {name: str(path) for name, path in runtime["paths"].items()},
    }


def resolve_facet_value(facet: str, value: str, facet_entries: dict[str, list[str]]) -> str | None:
    if value in facet_entries:
        return value
    lowered = {entry.lower(): entry for entry in facet_entries}
    if value.lower() in lowered:
        return lowered[value.lower()]
    normalized = normalize_lookup_text(value)
    for entry in facet_entries:
        if normalize_lookup_text(entry) == normalized:
            return entry
    return None


def build_slice_payload(facet: str, value: str, runtime: dict[str, object], limit: int) -> dict:
    facet_entries = runtime["facet_index"]["facets"][facet]
    resolved_value = resolve_facet_value(facet, value, facet_entries)
    if resolved_value is None:
        return {
            "query_type": "slice",
            "query_ref": {facet: value},
            "resolved_documents": [],
            "summary": {"status": "not_found", "title": "Facet slice not found"},
            "results": {"available_values": sorted(facet_entries)[:20]},
            "counts": {"available_value_count": len(facet_entries)},
            "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
            "manifest_refs": {name: str(path) for name, path in runtime["paths"].items()},
        }

    doc_ids = facet_entries[resolved_value]
    documents = [compact_doc_card(runtime["docs_by_id"][doc_id]) for doc_id in doc_ids]
    doc_id_set = set(doc_ids)
    slice_pairs = [
        pair for pair in runtime["canonical_pair_map"].values()
        if pair["src_id"] in doc_id_set and pair["dst_id"] in doc_id_set
    ]
    slice_pairs.sort(key=lambda item: (-item["score"], item["src_display_name"], item["dst_display_name"]))
    sections = split_pair_sections(slice_pairs, limit)
    return {
        "query_type": "slice",
        "query_ref": {facet: value},
        "resolved_documents": documents,
        "summary": {
            "status": "resolved",
            "title": f"{facet} slice: {resolved_value}",
            "detail": f"{len(documents)} documents, top {limit} routes per section",
        },
        "results": {
            "facet": facet,
            "value": resolved_value,
            "documents": documents[:limit],
            "strongest_overall": sections["overall"],
            "strongest_cross_element": sections["cross_element"],
            "strongest_cross_family": sections["cross_family"],
        },
        "counts": {
            "resolved_document_count": len(documents),
            "overall_pair_count": len(slice_pairs),
            "cross_element_pair_count": len([pair for pair in slice_pairs if pair["src_element"] != pair["dst_element"]]),
            "cross_family_pair_count": len([pair for pair in slice_pairs if pair["src_family"] != pair["dst_family"]]),
        },
        "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
        "manifest_refs": {name: str(path) for name, path in runtime["paths"].items()},
    }


def build_zero_point_payload(runtime: dict[str, object], limit: int) -> dict:
    routes = runtime["zero_point_index"]["routes"]
    sections = split_pair_sections(routes, limit)
    return {
        "query_type": "zero-point",
        "query_ref": "zero-point",
        "resolved_documents": [],
        "summary": {
            "status": "resolved",
            "title": "Zero-point convergence routes",
            "detail": f"Top {limit} convergence surfaces",
        },
        "results": {
            "zero_point_chapters": runtime["zero_point_index"]["zero_point_chapters"],
            "zero_point_appendices": runtime["zero_point_index"]["zero_point_appendices"],
            "strongest_overall": sections["overall"],
            "strongest_cross_element": sections["cross_element"],
            "strongest_cross_family": sections["cross_family"],
        },
        "counts": {
            "route_count": len(routes),
            "cross_element_route_count": len([pair for pair in routes if pair["src_element"] != pair["dst_element"]]),
            "cross_family_route_count": len([pair for pair in routes if pair["src_family"] != pair["dst_family"]]),
        },
        "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
        "manifest_refs": {name: str(path) for name, path in runtime["paths"].items()},
    }


def build_chapter_pack_payload(chapter_code: str, runtime: dict[str, object], limit: int) -> dict:
    build_root = PROJECT_ROOT / "_build"
    self_actualize_root = PROJECT_ROOT.parent / "self_actualize"
    return build_frontier_payload(
        NETWORK_ROOT.parent,
        build_root,
        self_actualize_root,
        [],
        chapter_code,
        runtime["manifest"]["live_docs_blocked"],
        limit=limit,
    )


def load_plan_grid_payload() -> tuple[dict, dict[str, Path]]:
    paths = plan_runtime_paths()
    if not paths["plan_grid_json"].exists():
        raise FileNotFoundError(paths["plan_grid_json"])
    return load_json(paths["plan_grid_json"]), paths


def filter_plan_cells(
    cells: list[dict],
    chapter: str | None,
    lane: str | None,
    lens: str | None,
    integration_pass: str | None,
) -> list[dict]:
    filtered = []
    for cell in cells:
        if chapter and cell["chapter_code"] != chapter:
            continue
        if lane and cell["artifact_lane"] != lane:
            continue
        if lens and cell["lens"] != lens:
            continue
        if integration_pass and cell["integration_pass"] != integration_pass:
            continue
        filtered.append(cell)
    return filtered


def build_filtered_execution_tiers(cells: list[dict]) -> dict[str, list[str]]:
    tiers = {"P0": [], "P1": [], "P2": [], "P3": []}
    for cell in cells:
        tiers.setdefault(cell["priority"], []).append(cell["cell_id"])
    return {tier: sorted(entries) for tier, entries in tiers.items() if entries}


def build_plan_grid_payload(
    grid_name: str,
    runtime: dict[str, object],
    limit: int,
    chapter: str | None = None,
    lane: str | None = None,
    lens: str | None = None,
    integration_pass: str | None = None,
) -> dict:
    if grid_name != PLAN_GRID_NAME:
        return {
            "query_type": "plan-grid",
            "query_ref": grid_name,
            "resolved_documents": [],
            "summary": {"status": "not_found", "title": "Plan grid not found"},
            "results": {"available_grids": [PLAN_GRID_NAME]},
            "counts": {"available_grid_count": 1},
            "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
            "manifest_refs": {name: str(path) for name, path in {**runtime["paths"], **plan_runtime_paths()}.items()},
        }

    try:
        grid_payload, plan_paths_map = load_plan_grid_payload()
    except FileNotFoundError:
        return {
            "query_type": "plan-grid",
            "query_ref": grid_name,
            "resolved_documents": [],
            "summary": {"status": "not_found", "title": "Plan grid artifacts not built yet"},
            "results": {"expected_grid": str(plan_runtime_paths()["plan_grid_json"])},
            "counts": {"cell_count": 0},
            "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
            "manifest_refs": {name: str(path) for name, path in {**runtime["paths"], **plan_runtime_paths()}.items()},
        }
    all_cells = grid_payload["cells"]
    filtered_cells = filter_plan_cells(all_cells, chapter, lane, lens, integration_pass)
    execution_tiers = build_filtered_execution_tiers(filtered_cells)
    blocked_cells = [cell["cell_id"] for cell in filtered_cells if cell["blocking_state"]["status"] == "blocked"]
    ready_cells = [cell["cell_id"] for cell in filtered_cells if cell["blocking_state"]["status"] == "ready"]
    dependency_routes = grid_payload["dependency_routes"]
    if chapter:
        dependency_routes = [
            route
            for route in dependency_routes
            if route["chapter_code"] in {chapter, grid_payload["chapter_template_reference"]}
        ]

    limited_cells = filtered_cells[:limit] if limit > 0 else filtered_cells
    applied_filters = {
        "chapter": chapter,
        "lane": lane,
        "lens": lens,
        "integration_pass": integration_pass,
    }
    filter_bits = [f"{key}={value}" for key, value in applied_filters.items() if value]
    filter_detail = ", ".join(filter_bits) if filter_bits else "no filters"

    return {
        "query_type": "plan-grid",
        "query_ref": grid_name,
        "resolved_documents": [],
        "summary": {
            "status": "resolved",
            "title": f"{grid_name} parallel plan lattice",
            "detail": f"{len(filtered_cells)} matching cells ({filter_detail}), showing {len(limited_cells)}",
        },
        "results": {
            "axes": grid_payload["axes"],
            "applied_filters": applied_filters,
            "cells": limited_cells,
            "execution_tiers": execution_tiers,
            "dependency_routes": dependency_routes,
            "chapter_template_reference": grid_payload["chapter_template_reference"],
            "blocked_cells": blocked_cells,
            "ready_cells": ready_cells,
        },
        "counts": {
            "cell_count": len(filtered_cells),
            "displayed_cell_count": len(limited_cells),
            "total_cell_count": grid_payload["counts"]["cell_count"],
            "blocked_cell_count": len(blocked_cells),
            "ready_cell_count": len(ready_cells),
            "chapter_count": len(grid_payload["axes"]["chapter_basis"]),
            "artifact_lane_count": len(grid_payload["axes"]["artifact_lanes"]),
            "lens_count": len(grid_payload["axes"]["lenses"]),
            "integration_pass_count": len(grid_payload["axes"]["integration_passes"]),
        },
        "live_docs_blocked": runtime["manifest"]["live_docs_blocked"],
        "manifest_refs": {
            **{name: str(path) for name, path in runtime["paths"].items()},
            **{name: str(path) for name, path in plan_paths_map.items()},
        },
    }


def render_pair_lines(pairs: list[dict]) -> list[str]:
    if not pairs:
        return ["- None"]
    lines: list[str] = []
    duplicate_labels = pair_label_disambiguators(pairs)
    for pair in pairs:
        pair_score = pair.get("route_score", pair.get("convergence_score", pair["score"]))
        pair_kind = pair.get("kind", "route")
        lines.append(
            f"- `{render_pair_endpoint_label(pair, 'src', duplicate_labels)}` <-> `{render_pair_endpoint_label(pair, 'dst', duplicate_labels)}` score=`{pair_score}` kind=`{pair_kind}` shared_chapters=`{', '.join(pair['shared_chapters']) or 'none'}` shared_appendices=`{', '.join(pair['shared_appendices']) or 'none'}`"
        )
    return lines


def render_markdown(payload: dict) -> str:
    lines = [
        f"# Query Result - {payload['query_type']}",
        "",
        f"- Query ref: `{payload['query_ref']}`",
        f"- Status: `{payload['summary']['status']}`",
        f"- Live Google Docs: `{'BLOCKED' if payload['live_docs_blocked'] else 'PASS'}`",
        "",
    ]
    if payload["summary"].get("title"):
        lines.append(f"## {payload['summary']['title']}")
        lines.append("")
    if payload["summary"].get("detail"):
        lines.append(payload["summary"]["detail"])
        lines.append("")

    if payload["query_type"] in {"doc", "neighbors"} and payload["summary"]["status"] == "resolved":
        document = payload["results"]["document"]
        lines.extend(
            [
                "## Document",
                "",
                f"- `{document['id']}` `{document['display_name']}`",
                f"- Family: `{document['family']}`",
                f"- Element: `{document['element']}` secondary=`{document['secondary_element'] or 'none'}`",
                f"- Gate: `{document['gate']}`",
                f"- Chapters: `{', '.join(document['chapters']) or 'none'}`",
                f"- Appendices: `{', '.join(document['appendices']) or 'none'}`",
                f"- Source layer: `{document['source_layer']}`",
                f"- Path: `{document['relative_path']}`",
                "",
                "## Strongest overall syntheses",
                "",
                *render_pair_lines(payload["results"]["strongest_overall"]),
                "",
                "## Strongest cross-element syntheses",
                "",
                *render_pair_lines(payload["results"]["strongest_cross_element"]),
                "",
                "## Strongest cross-family syntheses",
                "",
                *render_pair_lines(payload["results"]["strongest_cross_family"]),
            ]
        )
        return "\n".join(lines)

    if payload["query_type"] == "pair" and payload["summary"]["status"] == "resolved":
        pair = payload["results"]["pair"]
        lines.extend(
            [
                "## Canonical Pair",
                "",
                f"- Key: `{pair['canonical_pair_key']}`",
                f"- Score: `{pair['score']}`",
                f"- Kind: `{pair['kind']}`",
                f"- Pair: `{pair_endpoint_label(pair, 'src')}` <-> `{pair_endpoint_label(pair, 'dst')}`",
                f"- Shared chapters: `{', '.join(pair['shared_chapters']) or 'none'}`",
                f"- Shared appendices: `{', '.join(pair['shared_appendices']) or 'none'}`",
                f"- Shared tokens: `{', '.join(pair['shared_tokens']) or 'none'}`",
            ]
        )
        return "\n".join(lines)

    if payload["query_type"] == "slice" and payload["summary"]["status"] == "resolved":
        lines.extend(
            [
                "## Slice Documents",
                "",
                *[
                    f"- `{document['id']}` `{document['display_name']}` family=`{document['family']}` element=`{document['element']}` gate=`{document['gate']}`"
                    for document in payload["results"]["documents"]
                ],
                "",
                "## Strongest overall syntheses",
                "",
                *render_pair_lines(payload["results"]["strongest_overall"]),
                "",
                "## Strongest cross-element syntheses",
                "",
                *render_pair_lines(payload["results"]["strongest_cross_element"]),
                "",
                "## Strongest cross-family syntheses",
                "",
                *render_pair_lines(payload["results"]["strongest_cross_family"]),
            ]
        )
        return "\n".join(lines)

    if payload["query_type"] == "zero-point":
        lines.extend(
            [
                "## Zero-Point Core",
                "",
                f"- Chapters: `{', '.join(payload['results']['zero_point_chapters'])}`",
                f"- Appendices: `{', '.join(payload['results']['zero_point_appendices'])}`",
                "",
                "## Strongest overall syntheses",
                "",
                *render_pair_lines(payload["results"]["strongest_overall"]),
                "",
                "## Strongest cross-element syntheses",
                "",
                *render_pair_lines(payload["results"]["strongest_cross_element"]),
                "",
                "## Strongest cross-family syntheses",
                "",
                *render_pair_lines(payload["results"]["strongest_cross_family"]),
            ]
        )
        return "\n".join(lines)

    if payload["query_type"] == "chapter-pack" and payload["summary"]["status"] == "resolved":
        frontier_lines = [
            f"- `{item['id']}` `{item['display_name']}` family=`{item['family']}` layer=`{item['source_layer']}` rank=`{item['rank_score']}`"
            for item in payload["results"]["frontier_sources"]
        ] or ["- None"]
        open_cell_lines = [
            f"- `{cell['cell_code']}` `{cell['title']}` -> {cell['summary']}"
            for cell in payload["results"]["open_cells"]
        ] or ["- None"]
        lines.extend(
            [
                f"## {payload['chapter_code']} Compiler State",
                "",
                f"- Frontier bundle: `{payload['results']['frontier_bundle_path']}`",
                f"- Existing manuscript draft: `{payload['results']['existing_manuscript_draft_path']}`",
                f"- Manuscript handoff path: `{payload['results']['manuscript_handoff_path']}`",
                f"- Candidate cells: `{payload['counts']['candidate_cell_count']}`",
                f"- Open cells: `{payload['counts']['open_cell_count']}`",
                "",
                "## Strongest local frontier sources",
                "",
                *frontier_lines,
                "",
                "## Strongest cross-family routes",
                "",
                *render_pair_lines(payload["results"]["cross_family_routes"]),
                "",
                "## Strongest zero-point-adjacent routes",
                "",
                *render_pair_lines(payload["results"]["zero_point_routes"]),
                "",
                "## Witness obligations",
                "",
                *[f"- {item}" for item in payload["results"]["witness_obligations"]],
                "",
                "## Recommended drafting order",
                "",
                *[f"{idx}. {step}" for idx, step in enumerate(payload["results"]["drafting_order"], start=1)],
                "",
                "## Open cells",
                "",
                *open_cell_lines,
            ]
        )
        return "\n".join(lines)

    if payload["query_type"] == "plan-grid" and payload["summary"]["status"] == "resolved":
        lines.extend(
            [
                "## Axes",
                "",
                f"- Chapters: `{', '.join(payload['results']['axes']['chapter_basis'])}`",
                f"- Artifact lanes: `{', '.join(payload['results']['axes']['artifact_lanes'])}`",
                f"- Lenses: `{', '.join(payload['results']['axes']['lenses'])}`",
                f"- Integration passes: `{', '.join(payload['results']['axes']['integration_passes'])}`",
                f"- Template reference: `{payload['results']['chapter_template_reference']}`",
                "",
                "## Execution Tiers",
                "",
            ]
        )
        execution_tiers = payload["results"]["execution_tiers"] or {}
        if execution_tiers:
            for tier in ("P0", "P1", "P2", "P3"):
                if tier in execution_tiers:
                    lines.append(f"- `{tier}` -> `{', '.join(execution_tiers[tier])}`")
        else:
            lines.append("- None")
        lines.extend(["", "## Cells", ""])
        if payload["results"]["cells"]:
            for cell in payload["results"]["cells"]:
                lines.append(
                    f"- `{cell['cell_id']}` priority=`{cell['priority']}` block=`{cell['blocking_state']['status']}` lane=`{cell['artifact_lane']}` lens=`{cell['lens']}` pass=`{cell['integration_pass']}` delta=`{cell['template_delta_from_ch12']}`"
                )
                lines.append(f"  intent: {cell['intent']}")
                lines.append(f"  accept: {cell['acceptance_check']}")
        else:
            lines.append("- None")
        lines.extend(["", "## Dependency Routes", ""])
        if payload["results"]["dependency_routes"]:
            for route in payload["results"]["dependency_routes"]:
                lines.append(f"- `{route['route_id']}` {route['summary']}")
        else:
            lines.append("- None")
        lines.extend(
            [
                "",
                "## State",
                "",
                f"- Blocked cells: `{len(payload['results']['blocked_cells'])}`",
                f"- Ready cells: `{len(payload['results']['ready_cells'])}`",
            ]
        )
        return "\n".join(lines)

    candidates = payload["results"].get("candidates")
    if candidates:
        lines.extend(["## Candidate Matches", ""])
        for candidate in candidates:
            lines.append(
                f"- `{candidate['id']}` `{candidate['display_name']}` family=`{candidate['family']}` element=`{candidate['element']}` gate=`{candidate['gate']}`"
            )
        return "\n".join(lines)

    available_values = payload["results"].get("available_values")
    if available_values:
        lines.extend(["## Available Values", "", *[f"- `{value}`" for value in available_values]])
        return "\n".join(lines)

    src = payload["results"].get("src")
    dst = payload["results"].get("dst")
    if src or dst:
        lines.extend(["## Unresolved Endpoints", ""])
        for label, entry in (("Source", src), ("Target", dst)):
            if not entry:
                continue
            if entry.get("status"):
                lines.append(f"- {label}: `{entry['status']}`")
                for candidate in entry.get("candidates", []):
                    lines.append(
                        f"  - `{candidate['id']}` `{candidate['display_name']}` family=`{candidate['family']}` element=`{candidate['element']}`"
                    )
            else:
                lines.append(f"- {label}: `{entry['id']}` `{entry['display_name']}`")
        return "\n".join(lines)

    return "\n".join(lines + ["No results."])


def deterministic_output_stem(args: argparse.Namespace) -> str:
    if args.command == "doc":
        return f"doc_{slugify(args.ref)}"
    if args.command == "neighbors":
        return f"neighbors_{slugify(args.ref)}_{slugify(args.mode)}_{args.limit}"
    if args.command == "pair":
        return f"pair_{slugify(args.src)}__{slugify(args.dst)}"
    if args.command == "slice":
        facet_name = args.slice_facet
        return f"slice_{slugify(facet_name)}_{slugify(args.slice_value)}_{args.limit}"
    if args.command == "chapter-pack":
        return f"chapter_pack_{slugify(args.chapter_code)}_{args.limit}"
    if args.command == "plan-grid":
        parts = [
            "plan_grid",
            slugify(args.grid_name),
            slugify(args.chapter or "all_chapters"),
            slugify(args.lane or "all_lanes"),
            slugify(args.lens or "all_lenses"),
            slugify(args.integration_pass or "all_passes"),
            str(args.limit),
        ]
        return "_".join(parts)
    return f"zero_point_{args.limit}"


def write_outputs(args: argparse.Namespace, payload: dict, markdown: str) -> None:
    stem = deterministic_output_stem(args)
    QUERY_LAST_DIR.mkdir(parents=True, exist_ok=True)
    write_text(QUERY_LAST_DIR / f"{stem}.md", markdown)
    write_json(QUERY_LAST_DIR / f"{stem}.json", payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the deeper integrated neural net.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doc_parser = subparsers.add_parser("doc", help="Resolve one document and return its registry card.")
    doc_parser.add_argument("ref")
    doc_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    doc_parser.add_argument("--json", action="store_true", dest="as_json")
    doc_parser.add_argument("--write", action="store_true")

    neighbors_parser = subparsers.add_parser("neighbors", help="Return strongest neighbors for one document.")
    neighbors_parser.add_argument("ref")
    neighbors_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    neighbors_parser.add_argument("--mode", choices=("overall", "cross-element", "cross-family"), default="overall")
    neighbors_parser.add_argument("--json", action="store_true", dest="as_json")
    neighbors_parser.add_argument("--write", action="store_true")

    pair_parser = subparsers.add_parser("pair", help="Return the canonical pair card for two documents.")
    pair_parser.add_argument("src")
    pair_parser.add_argument("dst")
    pair_parser.add_argument("--json", action="store_true", dest="as_json")
    pair_parser.add_argument("--write", action="store_true")

    slice_parser = subparsers.add_parser("slice", help="Return a facet slice plus top routes inside it.")
    facet_group = slice_parser.add_mutually_exclusive_group(required=True)
    facet_group.add_argument("--element")
    facet_group.add_argument("--family")
    facet_group.add_argument("--chapter")
    facet_group.add_argument("--appendix")
    facet_group.add_argument("--gate")
    facet_group.add_argument("--source-layer")
    slice_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    slice_parser.add_argument("--json", action="store_true", dest="as_json")
    slice_parser.add_argument("--write", action="store_true")

    zero_parser = subparsers.add_parser("zero-point", help="Return top zero-point convergence routes.")
    zero_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    zero_parser.add_argument("--json", action="store_true", dest="as_json")
    zero_parser.add_argument("--write", action="store_true")

    chapter_pack_parser = subparsers.add_parser("chapter-pack", help="Return the compiled drafting-prep pack for one chapter.")
    chapter_pack_parser.add_argument("chapter_code", choices=CHAPTER_FRONTIER_CODES)
    chapter_pack_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    chapter_pack_parser.add_argument("--json", action="store_true", dest="as_json")
    chapter_pack_parser.add_argument("--write", action="store_true")

    plan_grid_parser = subparsers.add_parser("plan-grid", help="Query the materialized frontier plan lattice.")
    plan_grid_parser.add_argument("grid_name", choices=(PLAN_GRID_NAME,))
    plan_grid_parser.add_argument("--chapter", choices=CHAPTER_FRONTIER_CODES)
    plan_grid_parser.add_argument("--lane", choices=ARTIFACT_LANES)
    plan_grid_parser.add_argument("--lens", choices=PLAN_LENSES)
    plan_grid_parser.add_argument("--pass", dest="integration_pass", choices=INTEGRATION_PASSES)
    plan_grid_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    plan_grid_parser.add_argument("--json", action="store_true", dest="as_json")
    plan_grid_parser.add_argument("--write", action="store_true")

    args = parser.parse_args()
    if args.command == "neighbors":
        args.mode = args.mode.replace("-", "_")
    if args.command == "slice":
        for facet in ("element", "family", "chapter", "appendix", "gate", "source_layer"):
            candidate = getattr(args, facet, None)
            if candidate is not None:
                args.slice_facet = facet
                args.slice_value = candidate
                break
    return args


def main() -> int:
    args = parse_args()
    runtime = load_runtime()

    if args.command == "doc":
        payload = build_doc_payload(args.ref, runtime, args.limit)
    elif args.command == "neighbors":
        payload = build_neighbors_payload(args.ref, args.mode, runtime, args.limit)
    elif args.command == "pair":
        payload = build_pair_payload(args.src, args.dst, runtime)
    elif args.command == "slice":
        payload = build_slice_payload(args.slice_facet, args.slice_value, runtime, args.limit)
    elif args.command == "chapter-pack":
        payload = build_chapter_pack_payload(args.chapter_code, runtime, args.limit)
    elif args.command == "plan-grid":
        payload = build_plan_grid_payload(
            args.grid_name,
            runtime,
            args.limit,
            chapter=args.chapter,
            lane=args.lane,
            lens=args.lens,
            integration_pass=args.integration_pass,
        )
    else:
        payload = build_zero_point_payload(runtime, args.limit)

    markdown = render_markdown(payload)
    if args.write:
        write_outputs(args, payload, markdown)

    if getattr(args, "as_json", False):
        sys.stdout.buffer.write((json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    else:
        sys.stdout.buffer.write((markdown + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
