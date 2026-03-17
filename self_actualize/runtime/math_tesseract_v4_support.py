from __future__ import annotations

from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    WORKSPACE_ROOT,
    load_json,
    normalize_path,
)


MATH_TESSERACT_ROOT = WORKSPACE_ROOT / "MATH" / "FINAL FORM" / "MATH GOD"
MATH_TESSERACT_ATLAS_ROOT = MATH_TESSERACT_ROOT / "atlas"
MATH_TESSERACT_BUNDLE_PATH = MATH_TESSERACT_ATLAS_ROOT / "math_tesseract_v4_bundle.json"
MATH_TESSERACT_ATLAS_MD_PATH = MATH_TESSERACT_ATLAS_ROOT / "math_tesseract_v4_bundle.md"
MATH_TESSERACT_CHARTER_PATH = MATH_TESSERACT_ROOT / "92_TESSERACT_V4_CHARTER.md"
MATH_TESSERACT_LIVE_ATLAS_PATH = MATH_TESSERACT_ATLAS_ROOT / "final_form_live_atlas.json"

_CACHE: dict[str, dict[str, Any]] = {}


def _default_bundle() -> dict[str, Any]:
    return {
        "generated_at": "",
        "docs_gate_status": "UNKNOWN",
        "record_count": 0,
        "appendix_registry": {},
        "records": [],
        "graph": {"nodes": [], "edges": []},
        "route_plan_count": 0,
        "route_plans": [],
        "migration_event_count": 0,
        "migration_events": [],
    }


def load_math_tesseract_bundle() -> dict[str, Any]:
    cache_key = str(MATH_TESSERACT_BUNDLE_PATH)
    cached = _CACHE.get(cache_key)
    if cached is not None:
        return cached
    if not MATH_TESSERACT_BUNDLE_PATH.exists():
        bundle = _default_bundle()
        _CACHE[cache_key] = bundle
        return bundle
    bundle = load_json(MATH_TESSERACT_BUNDLE_PATH)
    bundle["_record_lookup"] = build_tesseract_record_lookup(bundle)
    bundle["_route_plan_lookup"] = {
        item.get("record_id", ""): item
        for item in bundle.get("route_plans", [])
        if item.get("record_id")
    }
    _CACHE[cache_key] = bundle
    return bundle


def load_math_tesseract_source_atlas() -> dict[str, Any]:
    if not MATH_TESSERACT_LIVE_ATLAS_PATH.exists():
        return {"generated_at": "", "root": "", "record_count": 0, "summary": {}, "records": []}
    return load_json(MATH_TESSERACT_LIVE_ATLAS_PATH)


def build_tesseract_record_lookup(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for entry in bundle.get("records", []):
        for candidate in (
            entry.get("record_id", ""),
            entry.get("absolute_path", ""),
            entry.get("relative_path", ""),
            normalize_path(entry.get("absolute_path", "")),
            normalize_path(entry.get("relative_path", "")),
        ):
            if candidate:
                lookup[candidate] = entry
    return lookup


def lookup_tesseract_record(
    bundle: dict[str, Any],
    *,
    record_id: str = "",
    path: str = "",
    relative_path: str = "",
) -> dict[str, Any] | None:
    lookup = bundle.get("_record_lookup")
    if lookup is None:
        lookup = build_tesseract_record_lookup(bundle)
        bundle["_record_lookup"] = lookup
    for candidate in (
        record_id,
        path,
        relative_path,
        normalize_path(path),
        normalize_path(relative_path),
    ):
        if candidate and candidate in lookup:
            return lookup[candidate]
    return None


def route_plan_for_record(
    bundle: dict[str, Any],
    *,
    record_id: str = "",
    path: str = "",
    relative_path: str = "",
) -> dict[str, Any] | None:
    entry = lookup_tesseract_record(
        bundle,
        record_id=record_id,
        path=path,
        relative_path=relative_path,
    )
    if entry is None:
        return None
    route_lookup = bundle.get("_route_plan_lookup", {})
    route_plan = route_lookup.get(entry.get("record_id", ""))
    if route_plan is not None:
        return route_plan
    for item in bundle.get("route_plans", []):
        if item.get("record_id") == entry.get("record_id"):
            return item
    return None


def extract_tesseract_fields(entry: dict[str, Any], route_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    route_plan = route_plan or {}
    return {
        "chapter_station": entry.get("chapter_station", ""),
        "local_addr": entry.get("local_addr", ""),
        "global_addr": entry.get("global_addr", ""),
        "tesseract_header": entry.get("tesseract_header", ""),
        "truth_state": entry.get("truth_state", ""),
        "tesseract_truth_state": entry.get("truth_state", ""),
        "appendix_support": list(entry.get("appendix_support", [])),
        "appendix_support_sources": entry.get("appendix_support_sources", {}),
        "appendix_only_mode": bool(entry.get("appendix_only_mode", False)),
        "overlay_annotations": entry.get("overlay_annotations", {}),
        "tesseract_overlay": entry.get("overlay_annotations", {}),
        "hubs_seq": list(route_plan.get("hubs_seq", entry.get("hubs_seq", []))),
        "tunnel_plan": route_plan.get("tunnel_plan", entry.get("tunnel_plan", {})),
        "hcrl_pass": route_plan.get("hcrl_pass", entry.get("hcrl_pass", {})),
        "obligations": list(route_plan.get("obligations", entry.get("obligations", []))),
        "drop_log": list(route_plan.get("drop_log", entry.get("drop_log", []))),
        "truth_intent": route_plan.get("truth_intent", entry.get("truth_intent", {})),
        "route_plan_id": route_plan.get("route_plan_id", ""),
        "graph_edge_ids": list(entry.get("graph_edge_ids", [])),
        "migration_edge_ids": list(entry.get("migration_edge_ids", [])),
        "legacy_witnesses": list(entry.get("legacy_witnesses", [])),
        "primary_hubs_text": route_plan.get("primary_hubs_text", ""),
        "tunnel_text": route_plan.get("tunnel_text", ""),
        "truth_state_text": route_plan.get("truth_state_text", ""),
        "hcrl_text": route_plan.get("hcrl_text", {}),
        "witness_ptr": entry.get("witness_ptr", ""),
        "replay_ptr": entry.get("replay_ptr", ""),
    }


def merge_tesseract_fields(target: dict[str, Any], entry: dict[str, Any] | None, route_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    if entry is None:
        return target
    merged = dict(target)
    merged.update(extract_tesseract_fields(entry, route_plan))
    return merged
