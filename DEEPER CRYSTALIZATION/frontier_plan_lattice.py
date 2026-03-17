#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from chapter_frontier_compiler import CHAPTER_FRONTIER_CODES, TEMPLATE_CHAPTER_CODE, chapter_from_code
from nervous_system_core import utc_now, write_json, write_text


PLAN_GRID_NAME = "frontier4"
PLAN_DIR_NAME = "14_PARALLEL_PLANS"
ARTIFACT_LANES = ("frontier_bundle", "evidence_pack", "chapter_tile_and_handoff", "runtime_and_query")
PLAN_LENSES = ("S", "F", "C", "R")
INTEGRATION_PASSES = ("local_witness", "cross_family_bridge", "zero_point_route", "manuscript_closure")


def plan_paths(active_root: Path) -> dict[str, Path]:
    plan_root = active_root / PLAN_DIR_NAME
    return {
        "plan_root": plan_root,
        "grid_markdown": plan_root / "00_master_4x4x4x4_grid.md",
        "grid_json": plan_root / "01_master_4x4x4x4_grid.json",
        "execution_tiers": plan_root / "02_execution_tiers.md",
        "dependency_routes": plan_root / "03_dependency_routes.md",
        "manifest": plan_root / "04_plan_manifest.json",
        "shadow_report": active_root / "11_SHADOWS" / "00_shadow_report.md",
        "chapter_frontier_manifest": active_root / "06_RUNTIME" / "13_chapter_frontier_manifest.json",
        "full_stack_manifest": active_root / "06_RUNTIME" / "12_full_stack_manifest.json",
        "network_manifest": active_root / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "00_network_manifest.json",
        "facet_index": active_root / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "04_facet_index.json",
        "zero_point_index": active_root / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "06_zero_point_index.json",
    }


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def lens_summary(payload: dict) -> dict[str, dict]:
    summary: dict[str, dict] = {}
    cells = payload["results"]["cell_fill_map"].values()
    for lens in PLAN_LENSES:
        lens_cells = [cell for cell in cells if cell["lens"] == lens]
        open_cells = [cell for cell in lens_cells if cell["status"] == "OPEN"]
        summary[lens] = {
            "cell_count": len(lens_cells),
            "candidate_count": len([cell for cell in lens_cells if cell["status"] != "OPEN"]),
            "open_count": len(open_cells),
            "open_titles": [cell["title"] for cell in open_cells],
        }
    return summary


def template_delta(chapter_code: str, lens: str, chapter_lens: dict[str, dict], template_lens: dict[str, dict], lane: str) -> str:
    if chapter_code == TEMPLATE_CHAPTER_CODE:
        return "template_reference"
    open_delta = chapter_lens[lens]["open_count"] - template_lens[lens]["open_count"]
    candidate_delta = chapter_lens[lens]["candidate_count"] - template_lens[lens]["candidate_count"]
    if lane == "runtime_and_query":
        return "inherits_template_query_surface"
    if open_delta > 0:
        return f"behind_template_on_{lens}: +{open_delta} open cells vs Ch12"
    if candidate_delta < 0:
        return f"lighter_than_template_on_{lens}: {candidate_delta} candidate delta vs Ch12"
    if open_delta == 0 and candidate_delta == 0:
        return f"matches_template_on_{lens}"
    return f"meets_or_exceeds_template_on_{lens}"


def manuscript_mode(payload: dict, lens: str) -> str:
    if payload["chapter_code"] == TEMPLATE_CHAPTER_CODE and payload["counts"]["open_cell_count"] == 0:
        return "ready for final drafter"
    if not payload["results"]["existing_manuscript_draft_present"] and lens_summary(payload)[lens]["open_count"] > 0:
        return "blocked by source gap"
    if not payload["results"]["existing_manuscript_draft_present"]:
        return "new additive handoff only"
    if lens_summary(payload)[lens]["open_count"] > 0:
        return "blocked by source gap"
    return "existing draft reorder"


def blocking_state(payload: dict, lens: str, lane: str, integration_pass: str, live_docs_blocked: bool) -> dict:
    lens_state = lens_summary(payload)[lens]
    reasons: list[str] = []
    status = "ready"
    manuscript_state = None

    if integration_pass == "local_witness" and lens_state["open_count"] > 0:
        status = "blocked"
        reasons.append(f"{lens_state['open_count']} OPEN cells remain on lens {lens}")
    if integration_pass == "cross_family_bridge" and not payload["results"]["cross_family_routes"]:
        status = "blocked"
        reasons.append("no cross-family routes available")
    if integration_pass == "zero_point_route" and not payload["results"]["zero_point_routes"]:
        status = "blocked"
        reasons.append("no zero-point routes available")
    if integration_pass == "manuscript_closure":
        manuscript_state = manuscript_mode(payload, lens)
        if manuscript_state == "blocked by source gap":
            status = "blocked"
        reasons.append(manuscript_state)
    if live_docs_blocked:
        reasons.append("live docs blocked -> local-only evidence regime")
    if lane == "runtime_and_query" and status == "ready":
        reasons.append("query and manifest surfaces can be updated without new live witnesses")

    return {
        "status": status,
        "reason": "; ".join(dict.fromkeys(reasons)),
        "live_docs_blocked": live_docs_blocked,
        "manuscript_mode": manuscript_state,
    }


def priority_for_cell(chapter_code: str, lane: str, state: dict, delta: str) -> str:
    if chapter_code != TEMPLATE_CHAPTER_CODE and state["status"] == "blocked":
        return "P0"
    if lane == "runtime_and_query":
        return "P2"
    if chapter_code != TEMPLATE_CHAPTER_CODE and not delta.startswith(("matches_template", "meets_or_exceeds_template")):
        return "P1"
    return "P3"


def intent_for_cell(chapter_code: str, lane: str, lens: str, integration_pass: str) -> str:
    chapter = chapter_from_code(chapter_code)
    lane_targets = {
        "frontier_bundle": "curate the chapter frontier bundle",
        "evidence_pack": "stabilize the evidence-pack payload",
        "chapter_tile_and_handoff": "promote the chapter tile and manuscript handoff",
        "runtime_and_query": "expose the chapter through runtime and query surfaces",
    }
    pass_targets = {
        "local_witness": "local witnesses",
        "cross_family_bridge": "cross-family bridges",
        "zero_point_route": "zero-point routes",
        "manuscript_closure": "manuscript closure",
    }
    return f"Use the {lens} lens to {lane_targets[lane]} for {chapter.code} by tightening {pass_targets[integration_pass]} around `{chapter.title}`."


def upstream_inputs_for_cell(payload: dict, lane: str, integration_pass: str, paths: dict[str, Path]) -> list[str]:
    inputs = [
        payload["results"]["frontier_bundle_path"],
        payload["results"]["existing_manuscript_draft_path"],
        str(paths["shadow_report"]),
        str(paths["facet_index"]),
        str(paths["zero_point_index"]),
    ]
    if lane == "runtime_and_query":
        inputs.extend([str(paths["network_manifest"]), str(paths["chapter_frontier_manifest"])])
    if integration_pass == "manuscript_closure":
        inputs.append(payload["results"]["manuscript_handoff_path"])
    return [item for item in dict.fromkeys(inputs) if item and item != "(none)"]


def target_outputs_for_cell(payload: dict, chapter_code: str, lane: str, integration_pass: str, paths: dict[str, Path]) -> list[str]:
    outputs = {
        "frontier_bundle": [payload["results"]["frontier_bundle_path"]],
        "evidence_pack": [payload["results"]["evidence_pack_path"], payload["results"]["drafting_prep_path"]],
        "chapter_tile_and_handoff": [payload["results"]["manuscript_handoff_path"]],
        "runtime_and_query": [
            str(paths["manifest"]),
            str(paths["grid_json"]),
            f'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" chapter-pack {chapter_code}',
            f'python "C:\\Users\\dmitr\\Documents\\Athena Agent\\DEEPER CRYSTALIZATION\\deeper_neural_net_query.py" plan-grid {PLAN_GRID_NAME} --chapter {chapter_code} --pass {integration_pass}',
        ],
    }[lane]
    if lane == "chapter_tile_and_handoff":
        outputs = [
            payload["results"]["chapter_tile_path"],
            payload["results"]["manuscript_handoff_path"],
            payload["results"].get("existing_manuscript_draft_path"),
            payload["results"].get("drafting_prep_path"),
        ]
    return [item for item in dict.fromkeys(outputs) if item and item != "(none)"]


def acceptance_check_for_cell(chapter_code: str, lane: str, integration_pass: str) -> str:
    checks = {
        ("frontier_bundle", "local_witness"): f"{chapter_code} frontier bundle must name lens-specific local witnesses and preserve BLOCKED live-doc status.",
        ("frontier_bundle", "cross_family_bridge"): f"{chapter_code} frontier bundle must expose canonical cross-family routes with disambiguated labels.",
        ("frontier_bundle", "zero_point_route"): f"{chapter_code} frontier bundle must surface zero-point-adjacent routes without self-pairs.",
        ("frontier_bundle", "manuscript_closure"): f"{chapter_code} frontier bundle must end with drafting order and witness obligations.",
        ("evidence_pack", "local_witness"): f"{chapter_code} evidence pack must contain `frontier_sources`, `cell_fill_map`, and lens-ready witness counts.",
        ("evidence_pack", "cross_family_bridge"): f"{chapter_code} evidence pack must contain `cross_family_routes` with canonical pair metadata.",
        ("evidence_pack", "zero_point_route"): f"{chapter_code} evidence pack must contain `zero_point_routes` and inherited blocked-state truth.",
        ("evidence_pack", "manuscript_closure"): f"{chapter_code} evidence pack must encode manuscript draft presence, handoff path, and closure mode.",
        ("chapter_tile_and_handoff", "local_witness"): f"{chapter_code} chapter tile must show candidate or OPEN status for the selected lens without blank cells.",
        ("chapter_tile_and_handoff", "cross_family_bridge"): f"{chapter_code} handoff must weave cross-family bridges into prose-ready routing notes.",
        ("chapter_tile_and_handoff", "zero_point_route"): f"{chapter_code} handoff must include zero-point routes when they exist and preserve gaps honestly when they do not.",
        ("chapter_tile_and_handoff", "manuscript_closure"): f"{chapter_code} handoff must encode one of the allowed manuscript-closure modes without overwriting existing drafts.",
        ("runtime_and_query", "local_witness"): f"`chapter-pack {chapter_code}` must return resolved local witness counts.",
        ("runtime_and_query", "cross_family_bridge"): f"`chapter-pack {chapter_code}` must return cross-family routes with no self-pairs.",
        ("runtime_and_query", "zero_point_route"): f"`plan-grid {PLAN_GRID_NAME} --chapter {chapter_code} --pass zero_point_route` must return filtered cells from the materialized grid.",
        ("runtime_and_query", "manuscript_closure"): f"The plan manifest and full-stack manifest must advertise {chapter_code} manuscript closure state explicitly.",
    }
    return checks[(lane, integration_pass)]


def build_dependency_routes(chapter_payloads: dict[str, dict]) -> list[dict]:
    routes = []
    for chapter_code, payload in chapter_payloads.items():
        chapter = chapter_from_code(chapter_code)
        routes.append(
            {
                "route_id": f"{chapter_code}_route_01",
                "chapter_code": chapter_code,
                "summary": f"{chapter.code} local witnesses feed evidence, which feeds the chapter tile and handoff, which then feeds query/runtime exposure.",
                "sequence": [
                    payload["results"]["frontier_bundle_path"],
                    payload["results"]["evidence_pack_path"],
                    payload["results"]["drafting_prep_path"],
                    payload["results"]["chapter_tile_path"],
                    payload["results"]["manuscript_handoff_path"],
                    f'chapter-pack {chapter_code}',
                ],
            }
        )
    routes.append(
        {
            "route_id": "template_propagation",
            "chapter_code": TEMPLATE_CHAPTER_CODE,
            "summary": "Ch12 is the template branch. Its lens readiness and closure mode become the delta baseline for Ch03, Ch10, and Ch14.",
            "sequence": ["Ch12 chapter-pack", "template delta map", "non-template P0/P1 cells"],
        }
    )
    return routes


def build_execution_tiers(cells: list[dict]) -> dict[str, list[str]]:
    tiers: dict[str, list[str]] = defaultdict(list)
    for cell in cells:
        tiers[cell["priority"]].append(cell["cell_id"])
    return {tier: sorted(items) for tier, items in sorted(tiers.items())}


def build_cells(active_root: Path, chapter_payloads: dict[str, dict], live_docs_blocked: bool) -> tuple[list[dict], dict[str, list[str]], list[dict]]:
    paths = plan_paths(active_root)
    template_lens = lens_summary(chapter_payloads[TEMPLATE_CHAPTER_CODE])
    cells: list[dict] = []
    for chapter_code in CHAPTER_FRONTIER_CODES:
        payload = chapter_payloads[chapter_code]
        chapter_lens = lens_summary(payload)
        for lane in ARTIFACT_LANES:
            for lens in PLAN_LENSES:
                for integration_pass in INTEGRATION_PASSES:
                    delta = template_delta(chapter_code, lens, chapter_lens, template_lens, lane)
                    state = blocking_state(payload, lens, lane, integration_pass, live_docs_blocked)
                    cell = {
                        "cell_id": f"{chapter_code}::{lane}::{lens}::{integration_pass}",
                        "chapter_code": chapter_code,
                        "artifact_lane": lane,
                        "lens": lens,
                        "integration_pass": integration_pass,
                        "intent": intent_for_cell(chapter_code, lane, lens, integration_pass),
                        "upstream_inputs": upstream_inputs_for_cell(payload, lane, integration_pass, paths),
                        "target_outputs": target_outputs_for_cell(payload, chapter_code, lane, integration_pass, paths),
                        "blocking_state": state,
                        "priority": priority_for_cell(chapter_code, lane, state, delta),
                        "template_delta_from_ch12": delta,
                        "acceptance_check": acceptance_check_for_cell(chapter_code, lane, integration_pass),
                    }
                    cells.append(cell)
    execution_tiers = build_execution_tiers(cells)
    dependency_routes = build_dependency_routes(chapter_payloads)
    return cells, execution_tiers, dependency_routes


def render_grid_markdown(grid_payload: dict) -> str:
    lines = [
        "# Frontier4 Parallel Plan Lattice",
        "",
        f"- Template chapter: `{grid_payload['chapter_template_reference']}`",
        f"- Live Google Docs: `{'BLOCKED' if grid_payload['live_docs_blocked'] else 'PASS'}`",
        f"- Cell count: `{grid_payload['counts']['cell_count']}`",
        "",
        "## Axes",
        "",
        f"- Chapters: `{', '.join(grid_payload['axes']['chapter_basis'])}`",
        f"- Artifact lanes: `{', '.join(grid_payload['axes']['artifact_lanes'])}`",
        f"- Lenses: `{', '.join(grid_payload['axes']['lenses'])}`",
        f"- Integration passes: `{', '.join(grid_payload['axes']['integration_passes'])}`",
        "",
    ]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for cell in grid_payload["cells"]:
        grouped[cell["chapter_code"]].append(cell)
    for chapter_code in CHAPTER_FRONTIER_CODES:
        lines.extend([f"## {chapter_code}", ""])
        chapter_cells = sorted(
            grouped[chapter_code],
            key=lambda item: (ARTIFACT_LANES.index(item["artifact_lane"]), PLAN_LENSES.index(item["lens"]), INTEGRATION_PASSES.index(item["integration_pass"])),
        )
        for cell in chapter_cells:
            lines.append(
                f"- `{cell['cell_id']}` priority=`{cell['priority']}` block=`{cell['blocking_state']['status']}` delta=`{cell['template_delta_from_ch12']}`: {cell['intent']}"
            )
        lines.append("")
    return "\n".join(lines)


def render_execution_tiers_markdown(execution_tiers: dict[str, list[str]]) -> str:
    lines = ["# Execution Tiers", ""]
    for tier in ("P0", "P1", "P2", "P3"):
        lines.extend([f"## {tier}", ""])
        for cell_id in execution_tiers.get(tier, []):
            lines.append(f"- `{cell_id}`")
        if not execution_tiers.get(tier):
            lines.append("- None")
        lines.append("")
    return "\n".join(lines)


def render_dependency_routes_markdown(dependency_routes: list[dict]) -> str:
    lines = ["# Dependency Routes", ""]
    for route in dependency_routes:
        lines.extend([f"## {route['route_id']}", "", route["summary"], ""])
        for index, step in enumerate(route["sequence"], start=1):
            lines.append(f"{index}. `{step}`")
        lines.append("")
    return "\n".join(lines)


def build_frontier_plan_lattice(active_root: Path, chapter_payloads: dict[str, dict], live_docs_blocked: bool) -> dict:
    paths = plan_paths(active_root)
    shadow_text = paths["shadow_report"].read_text(encoding="utf-8") if paths["shadow_report"].exists() else ""
    cells, execution_tiers, dependency_routes = build_cells(active_root, chapter_payloads, live_docs_blocked)
    blocked_cells = [cell["cell_id"] for cell in cells if cell["blocking_state"]["status"] == "blocked"]
    ready_cells = [cell["cell_id"] for cell in cells if cell["blocking_state"]["status"] == "ready"]
    counts = {
        "cell_count": len(cells),
        "chapter_count": len(CHAPTER_FRONTIER_CODES),
        "artifact_lane_count": len(ARTIFACT_LANES),
        "lens_count": len(PLAN_LENSES),
        "integration_pass_count": len(INTEGRATION_PASSES),
        "blocked_cell_count": len(blocked_cells),
        "ready_cell_count": len(ready_cells),
        "cells_per_chapter": dict(sorted(Counter(cell["chapter_code"] for cell in cells).items())),
        "cells_per_lane": dict(sorted(Counter(cell["artifact_lane"] for cell in cells).items())),
        "cells_per_lens": dict(sorted(Counter(cell["lens"] for cell in cells).items())),
        "cells_per_pass": dict(sorted(Counter(cell["integration_pass"] for cell in cells).items())),
    }
    return {
        "generated_at": utc_now(),
        "grid_name": PLAN_GRID_NAME,
        "axes": {
            "chapter_basis": list(CHAPTER_FRONTIER_CODES),
            "artifact_lanes": list(ARTIFACT_LANES),
            "lenses": list(PLAN_LENSES),
            "integration_passes": list(INTEGRATION_PASSES),
        },
        "chapter_template_reference": TEMPLATE_CHAPTER_CODE,
        "cells": cells,
        "execution_tiers": execution_tiers,
        "dependency_routes": dependency_routes,
        "blocked_cells": blocked_cells,
        "ready_cells": ready_cells,
        "counts": counts,
        "live_docs_blocked": live_docs_blocked,
        "shadow_report_excerpt": "\n".join(shadow_text.splitlines()[:24]),
        "manifest_refs": {
            "shadow_report": str(paths["shadow_report"]),
            "chapter_frontier_manifest": str(paths["chapter_frontier_manifest"]),
            "network_manifest": str(paths["network_manifest"]),
            "facet_index": str(paths["facet_index"]),
            "zero_point_index": str(paths["zero_point_index"]),
        },
    }


def write_frontier_plan_lattice(active_root: Path, grid_payload: dict) -> dict:
    paths = plan_paths(active_root)
    paths["plan_root"].mkdir(parents=True, exist_ok=True)
    write_text(paths["grid_markdown"], render_grid_markdown(grid_payload))
    write_json(paths["grid_json"], grid_payload)
    write_text(paths["execution_tiers"], render_execution_tiers_markdown(grid_payload["execution_tiers"]))
    write_text(paths["dependency_routes"], render_dependency_routes_markdown(grid_payload["dependency_routes"]))

    manifest = {
        "generated_at": utc_now(),
        "grid_name": PLAN_GRID_NAME,
        "cell_count": grid_payload["counts"]["cell_count"],
        "chapter_basis": list(CHAPTER_FRONTIER_CODES),
        "artifact_lanes": list(ARTIFACT_LANES),
        "lenses": list(PLAN_LENSES),
        "integration_passes": list(INTEGRATION_PASSES),
        "template_reference": TEMPLATE_CHAPTER_CODE,
        "live_docs_blocked": grid_payload["live_docs_blocked"],
        "grid_json": str(paths["grid_json"]),
        "grid_markdown": str(paths["grid_markdown"]),
        "execution_tiers_markdown": str(paths["execution_tiers"]),
        "dependency_routes_markdown": str(paths["dependency_routes"]),
        "blocked_cell_count": grid_payload["counts"]["blocked_cell_count"],
        "ready_cell_count": grid_payload["counts"]["ready_cell_count"],
    }
    write_json(paths["manifest"], manifest)
    return manifest


def build_and_write_frontier_plan_lattice(active_root: Path, chapter_payloads: dict[str, dict], live_docs_blocked: bool) -> tuple[dict, dict]:
    grid_payload = build_frontier_plan_lattice(active_root, chapter_payloads, live_docs_blocked)
    manifest = write_frontier_plan_lattice(active_root, grid_payload)
    return grid_payload, manifest
