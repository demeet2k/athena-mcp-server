from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from self_actualize.runtime.command_spine_adapter import (
    COMMAND_ROUTE_CLASS as LIVE_COMMAND_ROUTE_CLASS,
    COMMAND_ROUTE_POLICY as LIVE_COMMAND_ROUTE_POLICY,
    DEFAULT_SPINE_ROOT,
    FIRST_WAVE_WATCHED_SURFACES,
)
from self_actualize.runtime.hemisphere_brain_support import (
    HEMISPHERE_ROOT,
    REGISTRY_ROOT,
    SELF_ACTUALIZE_ROOT,
    WORKSPACE_ROOT,
    normalize_path,
    utc_now,
)


COMMAND_MEMBRANE_CANON_ROOT = SELF_ACTUALIZE_ROOT / "command_membrane"
COMMAND_MEMBRANE_FALLBACK_CANON_ROOT = DEFAULT_SPINE_ROOT / "ledgers" / "command_membrane"


def _first_existing_path(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


COMMAND_MEMBRANE_LIVE_WATCHED_SURFACE_REGISTRY = _first_existing_path(
    COMMAND_MEMBRANE_CANON_ROOT / "watched_surface_registry.json",
    COMMAND_MEMBRANE_FALLBACK_CANON_ROOT / "watched_surface_registry.json",
)
COMMAND_MEMBRANE_LIVE_EVENT_LEDGER = _first_existing_path(
    COMMAND_MEMBRANE_CANON_ROOT / "command_live_event_ledger.json",
    COMMAND_MEMBRANE_FALLBACK_CANON_ROOT / "command_live_event_ledger.json",
)
COMMAND_MEMBRANE_LIVE_CLAIM_LEDGER = _first_existing_path(
    COMMAND_MEMBRANE_CANON_ROOT / "command_claim_ledger.json",
    COMMAND_MEMBRANE_FALLBACK_CANON_ROOT / "command_claim_ledger.json",
)
COMMAND_MEMBRANE_LIVE_CAPILLARY_LEDGER = _first_existing_path(
    COMMAND_MEMBRANE_CANON_ROOT / "command_capillary_edges.json",
    COMMAND_MEMBRANE_FALLBACK_CANON_ROOT / "command_capillary_edges.json",
)
COMMAND_MEMBRANE_LIVE_LATENCY_LEDGER = _first_existing_path(
    COMMAND_MEMBRANE_CANON_ROOT / "command_latency_benchmark_registry.json",
    COMMAND_MEMBRANE_FALLBACK_CANON_ROOT / "command_latency_benchmark_registry.json",
)
COMMAND_MEMBRANE_LIVE_SURFACE_HEALTH = _first_existing_path(
    COMMAND_MEMBRANE_CANON_ROOT / "command_surface_health.json",
    COMMAND_MEMBRANE_FALLBACK_CANON_ROOT / "command_surface_health.json",
)
COMMAND_MEMBRANE_LIVE_MANIFEST = _first_existing_path(
    COMMAND_MEMBRANE_CANON_ROOT / "command_live_manifest.json",
    COMMAND_MEMBRANE_FALLBACK_CANON_ROOT / "command_live_manifest.json",
)

COMMAND_MEMBRANE_PACKET_SCHEMA_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_command_membrane_packet_schema.json"
)
COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_command_membrane_watched_surface_registry.json"
)
COMMAND_MEMBRANE_EVENT_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_command_membrane_event_registry.json"
)
COMMAND_MEMBRANE_CLAIM_LEDGER_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_command_membrane_claim_ledger.json"
)
COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_command_membrane_capillary_registry.json"
)
COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH = (
    SELF_ACTUALIZE_ROOT / "myth_math_command_membrane_latency_registry.json"
)
COMMAND_MEMBRANE_MANIFEST_PATH = SELF_ACTUALIZE_ROOT / "myth_math_command_membrane_manifest.json"

COMMAND_MEMBRANE_PACKET_SCHEMA_MIRROR = REGISTRY_ROOT / COMMAND_MEMBRANE_PACKET_SCHEMA_PATH.name
COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_MIRROR = (
    REGISTRY_ROOT / COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH.name
)
COMMAND_MEMBRANE_EVENT_REGISTRY_MIRROR = REGISTRY_ROOT / COMMAND_MEMBRANE_EVENT_REGISTRY_PATH.name
COMMAND_MEMBRANE_CLAIM_LEDGER_MIRROR = REGISTRY_ROOT / COMMAND_MEMBRANE_CLAIM_LEDGER_PATH.name
COMMAND_MEMBRANE_CAPILLARY_REGISTRY_MIRROR = (
    REGISTRY_ROOT / COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH.name
)
COMMAND_MEMBRANE_LATENCY_REGISTRY_MIRROR = (
    REGISTRY_ROOT / COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH.name
)
COMMAND_MEMBRANE_MANIFEST_MIRROR = REGISTRY_ROOT / COMMAND_MEMBRANE_MANIFEST_PATH.name

COMMAND_MEMBRANE_HEMISPHERE_DOCS = {
    "index": HEMISPHERE_ROOT / "96_command_membrane_index.md",
    "schema": HEMISPHERE_ROOT / "97_command_packet_schema.md",
    "events": HEMISPHERE_ROOT / "98_command_event_routing_atlas.md",
    "capillaries": HEMISPHERE_ROOT / "99_command_capillary_atlas.md",
    "latency": HEMISPHERE_ROOT / "100_command_latency_receipt.md",
}

COMMAND_MEMBRANE_ANT_CLASSES = ["scout", "router", "worker", "archivist"]
COMMAND_MEMBRANE_ROUTE_POLICY = LIVE_COMMAND_ROUTE_POLICY
COMMAND_MEMBRANE_PUBLIC_TOPK = 5
COMMAND_MEMBRANE_ROUTE_CLASS = LIVE_COMMAND_ROUTE_CLASS
COMMAND_MEMBRANE_TTL = 6
COMMAND_MEMBRANE_EXPECTED_SOURCE_IDS = tuple(
    str(surface["source_id"]) for surface in FIRST_WAVE_WATCHED_SURFACES
)
COMMAND_MEMBRANE_LATENCY_METRICS = [
    "t_detect_ms",
    "t_encode_ms",
    "t_route_ms",
    "t_claim_ms",
    "t_commit_ms",
    "t_sugar_ms",
    "capillary_score",
]
COMMAND_MEMBRANE_PACKET_FIELDS = [
    "event_id",
    "parent_event_id",
    "source_id",
    "source_class",
    "event_fingerprint",
    "source_path",
    "active_surface",
    "source_region",
    "change_type",
    "change_summary",
    "goal",
    "priority",
    "confidence",
    "earth_ts",
    "earth_ts_local",
    "detected_ts",
    "emitted_ts",
    "liminal_ts",
    "coord12",
    "coordinate_stamp",
    "lineage",
    "route_class",
    "routing_policy",
    "topk",
    "ttl",
    "claim_state",
    "reinforcement_state",
    "latency_metrics",
    "match_state",
    "docs_gate_status",
]
COMMAND_MEMBRANE_CLAIM_FIELDS = [
    "claim_id",
    "event_id",
    "ant_id",
    "role",
    "lease_ms",
    "claimed_at",
    "expires_at",
    "status",
    "claim_status",
    "owner_surface",
    "board_claim_id",
    "released_at",
    "release_reason",
    "role_class",
    "claim_mode",
    "claimed_at_utc",
    "expires_at_utc",
    "reroute_count",
    "previous_ant_id",
    "route_class",
    "front_ref",
    "seed_mode",
    "dual_reference",
    "source_id",
    "source_class",
    "record_id",
    "relative_path",
    "linked_route_path",
    "docs_gate_status",
]
COMMAND_MEMBRANE_VESSEL_THRESHOLDS = {
    "vein": 0.85,
    "capillary": 0.60,
    "candidate": 0.35,
}
COMMAND_MEMBRANE_CAPILLARY_COEFFICIENTS = {
    "rho": 0.82,
    "alpha": 0.30,
    "beta": 0.18,
    "gamma": 0.16,
    "delta": 0.14,
}
VALID_VESSEL_CLASSES = {"vein", "capillary", "candidate", "latent", "dormant", "route"}
FIELD_TO_POLE = {
    "fire": "A",
    "air": "C",
    "water": "B",
    "earth": "D",
}


def _read_json(path: Path, default: Any) -> Any:
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def _normalized_path_variants(value: str) -> list[str]:
    if not value:
        return []
    normalized = normalize_path(str(value)).strip("/")
    if not normalized:
        return []
    parts = [part for part in normalized.split("/") if part]
    variants = {normalized.lower()}
    if len(parts) >= 2:
        variants.add("/".join(parts[-2:]).lower())
    if len(parts) >= 3:
        variants.add("/".join(parts[-3:]).lower())
    variants.add(parts[-1].lower())
    return sorted(variants)


def _record_match_keys(record: dict[str, Any]) -> set[str]:
    relative_path = str(record.get("relative_path") or "")
    absolute_path = str(record.get("path") or "")
    title = str(record.get("title") or "")
    keys = set(_normalized_path_variants(relative_path))
    keys.update(_normalized_path_variants(absolute_path))
    if relative_path or absolute_path:
        name = Path(relative_path or absolute_path).name
        stem = Path(relative_path or absolute_path).stem
        if name:
            keys.add(name.lower())
        if stem:
            keys.add(stem.lower())
            keys.add(_normalize_text(stem))
    if title:
        keys.add(_normalize_text(title))
        keys.add(title.lower())
    return {key for key in keys if key}


def _event_match_keys(row: dict[str, Any]) -> set[str]:
    source_path = str(row.get("source_path") or "")
    active_surface = str(row.get("active_surface") or "")
    source_folder = str(row.get("source_folder") or "")
    change = row.get("change") or {}
    keys = set(_normalized_path_variants(source_path))
    keys.update(_normalized_path_variants(active_surface))
    keys.update(_normalized_path_variants(source_folder))
    keys.update(_normalized_path_variants(str(change.get("source_path") or "")))
    keys.update(_normalized_path_variants(str(change.get("relative_path") or "")))
    if source_path:
        keys.add(_normalize_text(Path(source_path).stem))
        keys.add(Path(source_path).name.lower())
    return {key for key in keys if key}


def _build_match_index(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        for key in _record_match_keys(record):
            index[key].append(record)
    return index


def _select_best_record(
    row: dict[str, Any],
    match_index: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, Any] | None, float]:
    scored: dict[str, tuple[float, dict[str, Any]]] = {}
    keys = _event_match_keys(row)
    normalized_source_path = normalize_path(str(row.get("source_path") or "")).lower().strip("/")
    for key in keys:
        for record in match_index.get(key, []):
            record_id = str(record.get("record_id") or "")
            relative_path = normalize_path(str(record.get("relative_path") or "")).lower().strip("/")
            absolute_path = normalize_path(str(record.get("path") or "")).lower().strip("/")
            title = _normalize_text(str(record.get("title") or ""))
            score = 0.0
            if normalized_source_path and normalized_source_path == relative_path:
                score = 120.0
            elif normalized_source_path and normalized_source_path == absolute_path:
                score = 118.0
            elif key == relative_path:
                score = 110.0
            elif key == absolute_path:
                score = 108.0
            elif title and key == title:
                score = 92.0
            elif relative_path.endswith(f"/{key}") or absolute_path.endswith(f"/{key}"):
                score = 84.0
            else:
                score = 72.0
            score += _safe_float(record.get("confidence"), 0.0)
            score += _safe_float(record.get("bridge_intensity"), 0.0)
            current = scored.get(record_id)
            if current is None or score > current[0]:
                scored[record_id] = (score, record)
    if not scored:
        return None, 0.0
    best_score, best_record = sorted(
        scored.values(),
        key=lambda item: (
            -item[0],
            normalize_path(str(item[1].get("relative_path") or "")).lower(),
        ),
    )[0]
    return best_record, best_score


def _surface_descriptor_rows() -> list[dict[str, Any]]:
    rows = []
    for surface in FIRST_WAVE_WATCHED_SURFACES:
        target = Path(surface["absolute_path"])
        watch_root = Path(surface.get("watch_root") or surface["absolute_path"])
        rows.append(
            {
                "source_id": str(surface["source_id"]),
                "absolute_path": str(target),
                "relative_path": normalize_path(str(target.relative_to(WORKSPACE_ROOT))),
                "watch_root": str(watch_root),
                "watch_root_relative": normalize_path(str(watch_root.relative_to(WORKSPACE_ROOT))),
                "target_kind": str(surface.get("target_kind") or "file"),
                "source_class": str(surface.get("source_class") or ""),
                "event_filters": list(surface.get("event_filters") or []),
                "default_lanes": dict(surface.get("default_lanes") or {}),
                "routing_goal": str(surface.get("routing_goal") or ""),
                "urgency_baseline": _safe_float(surface.get("urgency_baseline"), 0.0),
                "coordinate_projection_hints": dict(surface.get("coordinate_projection_hints") or {}),
                "docs_gate_status": "BLOCKED",
            }
        )
    return rows


def _infer_source_descriptor(
    row: dict[str, Any],
    watched_rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    source_path = normalize_path(str(row.get("source_path") or "")).lower().strip("/")
    active_surface = normalize_path(str(row.get("active_surface") or "")).lower().strip("/")
    source_folder = normalize_path(str(row.get("source_folder") or "")).lower().strip("/")
    absolute_source_path = str(row.get("source_path") or "")
    best: tuple[int, dict[str, Any]] | None = None
    for watched in watched_rows:
        absolute_path = str(watched.get("absolute_path") or "")
        relative_path = normalize_path(str(watched.get("relative_path") or "")).lower().strip("/")
        watch_root_relative = normalize_path(str(watched.get("watch_root_relative") or "")).lower().strip("/")
        options = [relative_path, watch_root_relative]
        score = -1
        if absolute_path and absolute_source_path and absolute_source_path.lower().startswith(absolute_path.lower()):
            score = max(score, len(absolute_path))
        for option in options:
            if not option:
                continue
            if source_path == option or active_surface == option or source_folder == option:
                score = max(score, len(option) + 100)
            if source_path.startswith(f"{option}/") or active_surface.startswith(f"{option}/") or source_folder.startswith(
                f"{option}/"
            ):
                score = max(score, len(option))
        if score >= 0 and (best is None or score > best[0]):
            best = (score, watched)
    return best[1] if best else None


def _build_watched_registry(
    watched_surface_registry: dict[str, Any],
    surface_health: dict[str, Any],
    event_rows: list[dict[str, Any]],
    docs_gate_status: str,
) -> dict[str, Any]:
    rows = list(watched_surface_registry.get("rows") or [])
    if not rows:
        rows = _surface_descriptor_rows()
    health_by_id = {row.get("source_id"): row for row in surface_health.get("rows", [])}
    events_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in event_rows:
        source_id = row.get("source_id") or "unregistered_local"
        events_by_source[source_id].append(row)
    output_rows = []
    for row in rows:
        source_id = row.get("source_id")
        health = health_by_id.get(source_id, {})
        source_events = sorted(
            events_by_source.get(source_id, []),
            key=lambda item: str(item.get("earth_ts") or item.get("recorded_at") or ""),
            reverse=True,
        )
        backlog_count = sum(1 for item in source_events if item.get("event_status") != "committed")
        active_claim_count = sum(1 for item in source_events if (item.get("claim_state") or {}).get("status") == "active")
        output_rows.append(
            {
                **row,
                "native_watch_available": bool(health.get("native_watch_available", True)),
                "degraded_mode": bool(health.get("degraded_mode", False)),
                "event_count": len(source_events),
                "backlog_count": backlog_count,
                "active_claim_count": active_claim_count,
                "last_event_id": source_events[0].get("event_id", "") if source_events else "",
                "last_event_ts": source_events[0].get("earth_ts", "") if source_events else "",
                "last_status": source_events[0].get("event_status", "") if source_events else "",
                "docs_gate_status": docs_gate_status,
            }
        )
    return {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "watcher_mode": watched_surface_registry.get("watcher_mode") or "event-driven",
        "source_count": len(output_rows),
        "rows": output_rows,
    }


def _route_lookup(
    full_corpus_authority_registry: dict[str, Any],
    dual_route_registry: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for route in dual_route_registry.get("routes", []):
        route_id = str(route.get("route_id") or "")
        if route_id:
            lookup[route_id] = route
    for record in full_corpus_authority_registry.get("records", []):
        for route in (record.get("hemisphere_routes") or {}).values():
            route_id = str(route.get("route_id") or "")
            if route_id:
                lookup.setdefault(route_id, route)
    return lookup


def _primary_and_secondary_routes(
    record: dict[str, Any],
    route_lookup: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    routes = dict(record.get("hemisphere_routes") or {})
    primary = next(
        (route for route in routes.values() if route.get("route_role") == "primary"),
        routes.get(str(record.get("primary_hemisphere") or "")),
    )
    secondary = next(
        (route for route in routes.values() if route.get("route_role") == "secondary"),
        None,
    )
    if secondary is None:
        for hemisphere, route in routes.items():
            if primary is not None and hemisphere != primary.get("hemisphere"):
                secondary = route
                break
    if primary:
        primary = route_lookup.get(str(primary.get("route_id") or ""), primary)
    if secondary:
        secondary = route_lookup.get(str(secondary.get("route_id") or ""), secondary)
    return primary or {}, secondary or {}


def _appendix_stack(route: dict[str, Any]) -> list[str]:
    stack: list[str] = []
    for raw in list(route.get("appendix_support") or []) + list(route.get("appendix_support_sources") or []):
        value = str(raw or "").strip()
        if value and value not in stack:
            stack.append(value)
    return stack


def _prior_metro_route_witness(route: dict[str, Any], witness_side: str) -> dict[str, Any]:
    if not route:
        return {}
    return {
        "witness_side": witness_side,
        "route_id": route.get("route_id", ""),
        "grand_central_exchange": route.get("grand_central_exchange", ""),
        "origin_system": route.get("origin_system", ""),
        "target_system": route.get("target_system", ""),
        "station_path": list(route.get("station_path") or []),
        "interlock_ids": list(route.get("interlock_ids") or []),
        "return_path": list(route.get("return_path") or []),
        "metro_line_ids": list(route.get("metro_line_ids") or []),
        "root_station_address": route.get("root_station_address", ""),
        "rail3": route.get("rail3", ""),
        "dominant_lens_system": route.get("dominant_lens_system", ""),
        "appendix_support": list(route.get("appendix_support") or []),
        "truth_state": route.get("proof_state") or route.get("truth_state", ""),
    }


def _z_star_aether_transfer_signature(
    primary_route: dict[str, Any],
    secondary_route: dict[str, Any],
) -> dict[str, Any]:
    aether_point = dict(primary_route.get("aether_point") or {})
    liminal_vector = dict(primary_route.get("liminal_vector") or {})
    return {
        "from_z": primary_route.get("zpoint_id", ""),
        "via": "Z*",
        "to_z": secondary_route.get("zpoint_id") or primary_route.get("zpoint_id", ""),
        "zpoint_id": primary_route.get("zpoint_id", ""),
        "field_id": primary_route.get("field_id", ""),
        "geodesic_mode": primary_route.get("geodesic_mode", ""),
        "aether_density": _safe_float(aether_point.get("aether_density")),
        "zero_proximity": _safe_float(aether_point.get("zero_proximity")),
        "tunnel_cost": _safe_float(aether_point.get("tunnel_cost")),
        "rail_hardness": _safe_float(aether_point.get("rail_hardness")),
        "resonance_pressure": _safe_float(aether_point.get("resonance_pressure")),
        "repair_gain": _safe_float(aether_point.get("repair_gain")),
        "appendix_stack": _appendix_stack(primary_route),
        "omega_relation": _safe_float(liminal_vector.get("omega")),
    }


def _event_fingerprint(row: dict[str, Any], source_id: str) -> str:
    existing = str(row.get("event_fingerprint") or "").strip()
    if existing:
        return existing
    digest = hashlib.sha1()
    digest.update(source_id.encode("utf-8"))
    digest.update(str(row.get("source_path") or "").encode("utf-8"))
    digest.update(str(row.get("change_type") or "").encode("utf-8"))
    digest.update(str((row.get("change") or {}).get("state_hash") or row.get("state_hash") or "").encode("utf-8"))
    return f"FP:{digest.hexdigest()}"


def _vessel_class(strength: float, raw: str) -> str:
    lowered = str(raw or "").strip().lower()
    if lowered in VALID_VESSEL_CLASSES:
        return lowered
    if strength >= COMMAND_MEMBRANE_VESSEL_THRESHOLDS["vein"]:
        return "vein"
    if strength >= COMMAND_MEMBRANE_VESSEL_THRESHOLDS["capillary"]:
        return "capillary"
    if strength >= COMMAND_MEMBRANE_VESSEL_THRESHOLDS["candidate"]:
        return "candidate"
    return "latent"


def _face_to_poles(route: dict[str, Any]) -> list[str]:
    value = str(route.get("face6") or "").strip().lower()
    pole = FIELD_TO_POLE.get(value)
    return [pole] if pole else []


def _pole_set_for_record(record: dict[str, Any]) -> list[str]:
    routes = record.get("hemisphere_routes") or {}
    poles: list[str] = []
    for route in routes.values():
        for pole in _face_to_poles(route):
            if pole not in poles:
                poles.append(pole)
    order = ["A", "C", "B", "D"]
    return [pole for pole in order if pole in poles]


def _markdown_list(lines: list[str]) -> str:
    return "\n".join(lines).rstrip() + "\n"


def build_command_membrane_payloads(
    *,
    full_corpus_authority_registry: dict[str, Any],
    dual_route_registry: dict[str, Any],
    lp57omega_coordinate_registry: dict[str, Any],
    docs_gate_status: str,
) -> dict[str, Any]:
    live_watched = _read_json(COMMAND_MEMBRANE_LIVE_WATCHED_SURFACE_REGISTRY, {})
    live_events = _read_json(COMMAND_MEMBRANE_LIVE_EVENT_LEDGER, {})
    live_claims = _read_json(COMMAND_MEMBRANE_LIVE_CLAIM_LEDGER, {})
    live_capillaries = _read_json(COMMAND_MEMBRANE_LIVE_CAPILLARY_LEDGER, {})
    live_latency = _read_json(COMMAND_MEMBRANE_LIVE_LATENCY_LEDGER, {})
    live_surface_health = _read_json(COMMAND_MEMBRANE_LIVE_SURFACE_HEALTH, {})
    live_manifest = _read_json(COMMAND_MEMBRANE_LIVE_MANIFEST, {})

    authority_records = list(full_corpus_authority_registry.get("records") or [])
    match_index = _build_match_index(authority_records)
    coordinate_lookup = {
        str(row.get("record_id") or row.get("node_id") or ""): row
        for row in lp57omega_coordinate_registry.get("rows", [])
        if row.get("record_id") or row.get("node_id")
    }
    route_lookup = _route_lookup(full_corpus_authority_registry, dual_route_registry)

    watched_rows_base = list(live_watched.get("rows") or [])
    if not watched_rows_base:
        watched_rows_base = _surface_descriptor_rows()

    latency_lookup = {
        str(row.get("event_id") or ""): row for row in live_latency.get("rows", []) if row.get("event_id")
    }
    claim_rows_live = list(live_claims.get("rows") or [])
    claims_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in claim_rows_live:
        claims_by_event[str(row.get("event_id") or "")].append(row)

    capillary_rows_live = list((live_capillaries.get("rows") or []))
    if not capillary_rows_live and isinstance(live_capillaries.get("edges"), dict):
        capillary_rows_live = [
            {"path_key": key, **value} for key, value in sorted(live_capillaries.get("edges", {}).items())
        ]
    capillary_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in capillary_rows_live:
        event_id = str(row.get("last_event_id") or "")
        if event_id:
            capillary_by_event[event_id].append(row)

    event_rows: list[dict[str, Any]] = []
    matched_event_count = 0
    fallback_event_count = 0
    for live_row in live_events.get("rows", []):
        source_descriptor = _infer_source_descriptor(live_row, watched_rows_base) or {}
        source_id = str(live_row.get("source_id") or source_descriptor.get("source_id") or "unregistered_local")
        source_class = str(live_row.get("source_class") or source_descriptor.get("source_class") or "unregistered_local")
        routing_goal = str(live_row.get("goal") or source_descriptor.get("routing_goal") or "detect-classify-assign")
        record, match_score = _select_best_record(live_row, match_index)
        primary_route: dict[str, Any] = {}
        secondary_route: dict[str, Any] = {}
        match_state = "fallback_live_anchor"
        record_id = ""
        record_title = ""
        relative_path = ""
        family = ""
        basis_anchor_ids: list[str] = []
        lp57_lookup_address = ""
        coordinate_tuple: dict[str, Any] = {}
        pole_set: list[str] = []
        if record is not None:
            record_id = str(record.get("record_id") or "")
            record_title = str(record.get("title") or "")
            relative_path = str(record.get("relative_path") or "")
            family = str(record.get("family") or "")
            basis_anchor_ids = list(record.get("basis_anchor_ids") or [])
            coordinate_row = coordinate_lookup.get(record_id, {})
            lp57_lookup_address = str(coordinate_row.get("lookup_address") or "")
            coordinate_tuple = dict(coordinate_row.get("coordinate_tuple") or {})
            primary_route, secondary_route = _primary_and_secondary_routes(record, route_lookup)
            pole_set = _pole_set_for_record(record)
            match_state = "canonical_match"
            matched_event_count += 1
        else:
            fallback_event_count += 1
        latency_row = latency_lookup.get(str(live_row.get("event_id") or ""), {})
        event_capillaries = capillary_by_event.get(str(live_row.get("event_id") or ""), [])
        strongest_capillary = sorted(
            event_capillaries,
            key=lambda item: (
                -_safe_float(item.get("edge_strength", item.get("strength"))),
                str(item.get("edge_id") or item.get("path_key") or ""),
            ),
        )[0] if event_capillaries else {}
        latest_claim_rows = sorted(
            claims_by_event.get(str(live_row.get("event_id") or ""), []),
            key=lambda item: str(item.get("claimed_at") or ""),
            reverse=True,
        )
        latest_claim_row = latest_claim_rows[0] if latest_claim_rows else {}
        event_rows.append(
            {
                "event_id": live_row.get("event_id", ""),
                "parent_event_id": live_row.get("parent_event_id") or live_row.get("parent", "ROOT"),
                "source_id": source_id,
                "source_class": source_class,
                "event_fingerprint": _event_fingerprint(live_row, source_id),
                "source_path": live_row.get("source_path", ""),
                "active_surface": live_row.get("active_surface", ""),
                "source_region": live_row.get("source_region") or source_descriptor.get("relative_path", ""),
                "change_type": live_row.get("change_type", ""),
                "change_summary": live_row.get("change_summary") or (live_row.get("change") or {}).get("summary", ""),
                "goal": routing_goal,
                "priority": _safe_float(live_row.get("priority")),
                "confidence": _safe_float(live_row.get("confidence")),
                "earth_ts": live_row.get("earth_ts", ""),
                "earth_ts_local": live_row.get("earth_ts_local", ""),
                "detected_ts": live_row.get("detected_ts", ""),
                "emitted_ts": live_row.get("emitted_ts", ""),
                "liminal_ts": live_row.get("liminal_ts", ""),
                "coord12": dict(live_row.get("coord12") or live_row.get("liminal_stamp_12d") or {}),
                "coordinate_stamp": dict(live_row.get("coordinate_stamp") or {}),
                "lineage": dict(live_row.get("lineage") or {}),
                "route_class": live_row.get("route_class") or COMMAND_MEMBRANE_ROUTE_CLASS,
                "routing_policy": (live_row.get("route_state") or {}).get("policy_id") or COMMAND_MEMBRANE_ROUTE_POLICY,
                "topk": int((live_row.get("route_state") or {}).get("topk") or COMMAND_MEMBRANE_PUBLIC_TOPK),
                "ttl": int(live_row.get("ttl") or COMMAND_MEMBRANE_TTL),
                "claim_state": {
                    "claim_id": latest_claim_row.get("claim_id", ""),
                    "ant_id": latest_claim_row.get("ant_id", ""),
                    "role": latest_claim_row.get("role", ""),
                    "status": latest_claim_row.get("status", latest_claim_row.get("claim_status", "")),
                    "lease_ms": latest_claim_row.get("lease_ms", 0),
                    "front_ref": latest_claim_row.get("front_ref")
                    or (f"{source_id}::{live_row.get('event_id', '')}" if source_id else ""),
                },
                "reinforcement_state": {
                    "route_path": (live_row.get("route_state") or {}).get("route_path")
                    or latency_row.get("route_path", ""),
                    "capillary_score": _safe_float(latency_row.get("capillary_score")),
                    "vessel_class": _vessel_class(
                        _safe_float(strongest_capillary.get("edge_strength", strongest_capillary.get("strength"))),
                        strongest_capillary.get("classification") or strongest_capillary.get("state_class", ""),
                    ),
                    "edge_id": strongest_capillary.get("edge_id") or strongest_capillary.get("path_key", ""),
                    "result": strongest_capillary.get("last_result") or (live_row.get("commit_state") or {}).get("result", ""),
                },
                "latency_metrics": {
                    "t_detect_ms": _safe_float(latency_row.get("t_detect_ms")),
                    "t_encode_ms": _safe_float(latency_row.get("t_encode_ms")),
                    "t_route_ms": _safe_float(latency_row.get("t_route_ms")),
                    "t_claim_ms": _safe_float(latency_row.get("t_claim_ms")),
                    "t_commit_ms": _safe_float(latency_row.get("t_commit_ms")),
                    "t_sugar_ms": _safe_float(latency_row.get("t_sugar_ms")),
                    "capillary_score": _safe_float(latency_row.get("capillary_score")),
                },
                "match_state": match_state,
                "event_status": live_row.get("status", ""),
                "record_id": record_id,
                "title": record_title,
                "relative_path": relative_path,
                "family": family,
                "basis_anchor_ids": basis_anchor_ids,
                "lp57_lookup_address": lp57_lookup_address,
                "coordinate_tuple": coordinate_tuple,
                "primary_hemisphere": record.get("primary_hemisphere", "") if record else "",
                "primary_route_id": primary_route.get("route_id", ""),
                "secondary_route_id": secondary_route.get("route_id", ""),
                "pole_set": pole_set,
                "prior_metro_route_witness": _prior_metro_route_witness(primary_route, "primary"),
                "counter_route_witness": _prior_metro_route_witness(secondary_route, "secondary"),
                "z_star_aether_transfer_signature": _z_star_aether_transfer_signature(primary_route, secondary_route),
                "source_descriptor": {
                    "source_id": source_id,
                    "source_class": source_class,
                    "watch_root": source_descriptor.get("watch_root", ""),
                    "target_kind": source_descriptor.get("target_kind", ""),
                    "urgency_baseline": _safe_float(
                        live_row.get("urgency_baseline", source_descriptor.get("urgency_baseline"))
                    ),
                    "coordinate_projection_hints": dict(source_descriptor.get("coordinate_projection_hints") or {}),
                },
                "match_score": round(match_score, 4),
                "docs_gate_status": docs_gate_status,
            }
        )

    watched_surface_registry = _build_watched_registry(
        live_watched,
        live_surface_health,
        event_rows,
        docs_gate_status,
    )
    events_by_id = {row.get("event_id"): row for row in event_rows}

    claim_rows: list[dict[str, Any]] = []
    for live_row in claim_rows_live:
        event_row = events_by_id.get(live_row.get("event_id"), {})
        source_id = live_row.get("source_id") or event_row.get("source_id", "")
        source_class = live_row.get("source_class") or event_row.get("source_class", "")
        claim_rows.append(
            {
                "claim_id": live_row.get("claim_id", ""),
                "event_id": live_row.get("event_id", ""),
                "ant_id": live_row.get("ant_id", ""),
                "role": live_row.get("role", ""),
                "lease_ms": int(live_row.get("lease_ms") or 0),
                "claimed_at": live_row.get("claimed_at", ""),
                "expires_at": live_row.get("expires_at", ""),
                "status": live_row.get("status", ""),
                "claim_status": live_row.get("claim_status", ""),
                "owner_surface": live_row.get("owner_surface") or source_class,
                "board_claim_id": live_row.get("board_claim_id", ""),
                "released_at": live_row.get("released_at", ""),
                "release_reason": live_row.get("release_reason", ""),
                "role_class": live_row.get("role_class", ""),
                "claim_mode": live_row.get("claim_mode") or "first-lease",
                "claimed_at_utc": live_row.get("claimed_at_utc") or live_row.get("claimed_at", ""),
                "expires_at_utc": live_row.get("expires_at_utc") or live_row.get("expires_at", ""),
                "reroute_count": int(live_row.get("reroute_count") or 0),
                "previous_ant_id": live_row.get("previous_ant_id", ""),
                "route_class": live_row.get("route_class") or event_row.get("route_class", COMMAND_MEMBRANE_ROUTE_CLASS),
                "front_ref": live_row.get("front_ref") or (f"{source_id}::{live_row.get('event_id', '')}" if source_id else ""),
                "seed_mode": live_row.get("seed_mode") or event_row.get("goal", ""),
                "dual_reference": live_row.get("dual_reference") or f"{source_class or 'command'}->archivist",
                "source_id": source_id,
                "source_class": source_class,
                "record_id": event_row.get("record_id", ""),
                "relative_path": event_row.get("relative_path") or event_row.get("source_path", ""),
                "linked_route_path": (event_row.get("reinforcement_state") or {}).get("route_path", ""),
                "docs_gate_status": docs_gate_status,
            }
        )

    capillary_rows: list[dict[str, Any]] = []
    vessel_counts: Counter[str] = Counter()
    for live_row in capillary_rows_live:
        strength = _safe_float(live_row.get("edge_strength", live_row.get("strength")))
        vessel_class = _vessel_class(strength, live_row.get("classification") or live_row.get("state_class", ""))
        vessel_counts[vessel_class] += 1
        last_event = events_by_id.get(live_row.get("last_event_id"), {})
        capillary_rows.append(
            {
                "edge_id": live_row.get("edge_id") or live_row.get("path_key", ""),
                "path_key": live_row.get("path_key") or live_row.get("edge_id", ""),
                "source_ant_id": live_row.get("from_node") or live_row.get("src", ""),
                "target_ant_id": live_row.get("to_node") or live_row.get("dst", ""),
                "edge_strength": round(strength, 6),
                "current_strength": round(strength, 6),
                "next_strength": round(strength, 4),
                "vessel_class": vessel_class,
                "success_count": int(live_row.get("success_count") or 0),
                "use_count": int(live_row.get("use_count") or 0),
                "noise_count": int(live_row.get("noise_count") or 0),
                "average_latency_score": _safe_float(live_row.get("average_latency_score")),
                "ema_latency_ms": _safe_float(live_row.get("ema_latency_ms")),
                "usefulness_score": _safe_float(live_row.get("usefulness")),
                "success_frequency": _safe_float(live_row.get("frequency")),
                "latency_penalty": _safe_float(live_row.get("latency_penalty")),
                "noise_penalty": _safe_float(live_row.get("noise_penalty")),
                "coefficients": dict(COMMAND_MEMBRANE_CAPILLARY_COEFFICIENTS),
                "front_ref": live_row.get("front_ref") or last_event.get("claim_state", {}).get("front_ref", ""),
                "last_result": live_row.get("last_result", ""),
                "last_event_id": live_row.get("last_event_id", ""),
                "source_id": last_event.get("source_id", ""),
                "source_class": last_event.get("source_class", ""),
                "docs_gate_status": docs_gate_status,
            }
        )

    latency_rows = []
    for live_row in live_latency.get("rows", []):
        event_row = events_by_id.get(live_row.get("event_id"), {})
        latency_rows.append(
            {
                "event_id": live_row.get("event_id", ""),
                "source_id": event_row.get("source_id") or live_row.get("source_id", ""),
                "source_class": event_row.get("source_class") or live_row.get("source_class", ""),
                "active_surface": event_row.get("active_surface") or live_row.get("active_surface", ""),
                "t_detect_ms": _safe_float(live_row.get("t_detect_ms")),
                "t_encode_ms": _safe_float(live_row.get("t_encode_ms")),
                "t_route_ms": _safe_float(live_row.get("t_route_ms")),
                "t_claim_ms": _safe_float(live_row.get("t_claim_ms")),
                "t_commit_ms": _safe_float(live_row.get("t_commit_ms")),
                "t_sugar_ms": _safe_float(live_row.get("t_sugar_ms")),
                "capillary_score": _safe_float(live_row.get("capillary_score")),
                "route_path": live_row.get("route_path") or (event_row.get("reinforcement_state") or {}).get("route_path", ""),
                "recorded_at": live_row.get("recorded_at", ""),
                "docs_gate_status": docs_gate_status,
            }
        )

    packet_schema = {
        "generated_at": utc_now(),
        "schema_id": "LOCAL_MULTI_SURFACE_SWARM_PACKET_V1",
        "docs_gate_status": docs_gate_status,
        "packet_fields": COMMAND_MEMBRANE_PACKET_FIELDS,
        "latency_metrics": COMMAND_MEMBRANE_LATENCY_METRICS,
        "ant_classes": COMMAND_MEMBRANE_ANT_CLASSES,
        "routing_defaults": {
            "policy": COMMAND_MEMBRANE_ROUTE_POLICY,
            "topk": COMMAND_MEMBRANE_PUBLIC_TOPK,
            "ttl": COMMAND_MEMBRANE_TTL,
            "route_class": COMMAND_MEMBRANE_ROUTE_CLASS,
            "claim_mode": "first-lease",
            "quorum": 1,
        },
        "capillary_law": {
            "coefficients": COMMAND_MEMBRANE_CAPILLARY_COEFFICIENTS,
            "thresholds": COMMAND_MEMBRANE_VESSEL_THRESHOLDS,
        },
        "watched_source_ids": list(COMMAND_MEMBRANE_EXPECTED_SOURCE_IDS),
        "runtime_sources": {
            "watched_surface_registry": str(COMMAND_MEMBRANE_LIVE_WATCHED_SURFACE_REGISTRY),
            "live_event_ledger": str(COMMAND_MEMBRANE_LIVE_EVENT_LEDGER),
            "claim_ledger": str(COMMAND_MEMBRANE_LIVE_CLAIM_LEDGER),
            "capillary_ledger": str(COMMAND_MEMBRANE_LIVE_CAPILLARY_LEDGER),
            "latency_ledger": str(COMMAND_MEMBRANE_LIVE_LATENCY_LEDGER),
            "live_manifest": str(COMMAND_MEMBRANE_LIVE_MANIFEST),
        },
    }
    event_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "event_count": len(event_rows),
        "matched_event_count": matched_event_count,
        "fallback_event_count": fallback_event_count,
        "source_counts": dict(Counter(row.get("source_id") or "unregistered_local" for row in event_rows)),
        "rows": event_rows,
    }
    claim_ledger = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "row_count": len(claim_rows),
        "active_count": sum(1 for row in claim_rows if row.get("status") == "active"),
        "rows": claim_rows,
    }
    capillary_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "edge_count": len(capillary_rows),
        "counts_by_vessel": dict(vessel_counts),
        "rows": capillary_rows,
    }
    latency_registry = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "row_count": len(latency_rows),
        "rows": latency_rows,
    }
    manifest = {
        "generated_at": utc_now(),
        "docs_gate_status": docs_gate_status,
        "compatibility_role": "derived-reporting-view-over-live-ledger",
        "live_authority": {
            "watched_surface_registry": str(COMMAND_MEMBRANE_LIVE_WATCHED_SURFACE_REGISTRY),
            "event_ledger": str(COMMAND_MEMBRANE_LIVE_EVENT_LEDGER),
            "claim_ledger": str(COMMAND_MEMBRANE_LIVE_CLAIM_LEDGER),
            "capillary_ledger": str(COMMAND_MEMBRANE_LIVE_CAPILLARY_LEDGER),
            "latency_ledger": str(COMMAND_MEMBRANE_LIVE_LATENCY_LEDGER),
            "surface_health": str(COMMAND_MEMBRANE_LIVE_SURFACE_HEALTH),
            "live_manifest": str(COMMAND_MEMBRANE_LIVE_MANIFEST),
        },
        "counts": {
            "watched_surfaces": watched_surface_registry.get("source_count", 0),
            "events": event_registry.get("event_count", 0),
            "matched_events": matched_event_count,
            "fallback_events": fallback_event_count,
            "claim_rows": claim_ledger.get("row_count", 0),
            "capillary_edges": capillary_registry.get("edge_count", 0),
            "latency_rows": latency_registry.get("row_count", 0),
            "veins": vessel_counts.get("vein", 0),
            "capillaries": vessel_counts.get("capillary", 0),
            "candidates": vessel_counts.get("candidate", 0),
            "latent_edges": vessel_counts.get("latent", 0) + vessel_counts.get("dormant", 0),
        },
        "outputs": {
            "packet_schema": str(COMMAND_MEMBRANE_PACKET_SCHEMA_PATH),
            "watched_surface_registry": str(COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH),
            "event_registry": str(COMMAND_MEMBRANE_EVENT_REGISTRY_PATH),
            "claim_ledger": str(COMMAND_MEMBRANE_CLAIM_LEDGER_PATH),
            "capillary_registry": str(COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH),
            "latency_registry": str(COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH),
            "manifest": str(COMMAND_MEMBRANE_MANIFEST_PATH),
        },
        "live_manifest_counts": dict(live_manifest.get("outputs") or {}),
    }

    watched_preview = watched_surface_registry.get("rows", [])[:7]
    top_events = sorted(
        event_rows,
        key=lambda row: (
            -_safe_float((row.get("latency_metrics") or {}).get("capillary_score")),
            -_safe_float(row.get("priority")),
            str(row.get("event_id") or ""),
        ),
    )[:8]
    top_capillaries = sorted(
        capillary_rows,
        key=lambda row: (-_safe_float(row.get("edge_strength")), str(row.get("edge_id") or "")),
    )[:8]

    markdown_pages = {
        "index": _markdown_list(
            [
                "# Command Membrane Index",
                "",
                f"- Generated: `{manifest['generated_at']}`",
                f"- Docs gate: `{docs_gate_status}`",
                f"- Watched surfaces: `{watched_surface_registry.get('source_count', 0)}`",
                f"- Events: `{event_registry.get('event_count', 0)}`",
                f"- Claims: `{claim_ledger.get('row_count', 0)}`",
                f"- Capillary edges: `{capillary_registry.get('edge_count', 0)}`",
                f"- Latency rows: `{latency_registry.get('row_count', 0)}`",
                "",
                "## First-Wave Watched Surfaces",
                "",
                *[
                    f"- `{row.get('source_id')}` :: `{row.get('source_class')}` :: `{row.get('event_count', 0)}` events :: degraded=`{row.get('degraded_mode', False)}`"
                    for row in watched_preview
                ],
                "",
                "## Runtime Contract",
                "",
                f"- Policy: `{COMMAND_MEMBRANE_ROUTE_POLICY}`",
                f"- Route class: `{COMMAND_MEMBRANE_ROUTE_CLASS}`",
                f"- Claim mode: `first-lease`",
                f"- TTL: `{COMMAND_MEMBRANE_TTL}`",
                f"- Top-k: `{COMMAND_MEMBRANE_PUBLIC_TOPK}`",
                "",
                f"- JSON packet schema: `{COMMAND_MEMBRANE_PACKET_SCHEMA_PATH.name}`",
                f"- JSON watched surfaces: `{COMMAND_MEMBRANE_WATCHED_SURFACE_REGISTRY_PATH.name}`",
                f"- JSON events: `{COMMAND_MEMBRANE_EVENT_REGISTRY_PATH.name}`",
                f"- JSON claims: `{COMMAND_MEMBRANE_CLAIM_LEDGER_PATH.name}`",
                f"- JSON capillaries: `{COMMAND_MEMBRANE_CAPILLARY_REGISTRY_PATH.name}`",
                f"- JSON latency: `{COMMAND_MEMBRANE_LATENCY_REGISTRY_PATH.name}`",
            ]
        ),
        "schema": _markdown_list(
            [
                "# Command Packet Schema",
                "",
                f"- Docs gate: `{docs_gate_status}`",
                f"- Packet field count: `{len(COMMAND_MEMBRANE_PACKET_FIELDS)}`",
                f"- Claim field count: `{len(COMMAND_MEMBRANE_CLAIM_FIELDS)}`",
                "",
                "## Event Fields",
                "",
                *[f"- `{field}`" for field in COMMAND_MEMBRANE_PACKET_FIELDS],
                "",
                "## Claim Fields",
                "",
                *[f"- `{field}`" for field in COMMAND_MEMBRANE_CLAIM_FIELDS],
                "",
                "## Latency Metrics",
                "",
                *[f"- `{metric}`" for metric in COMMAND_MEMBRANE_LATENCY_METRICS],
            ]
        ),
        "events": _markdown_list(
            [
                "# Command Event Routing Atlas",
                "",
                f"- Docs gate: `{docs_gate_status}`",
                f"- Matched events: `{matched_event_count}`",
                f"- Fallback live anchors: `{fallback_event_count}`",
                "",
                "## Highest-Signal Events",
                "",
                *[
                    f"- `{row.get('event_id')}` :: `{row.get('source_id')}` :: match=`{row.get('match_state')}` :: record=`{row.get('record_id') or 'none'}` :: route=`{(row.get('reinforcement_state') or {}).get('route_path', '') or 'pending'}`"
                    for row in top_events
                ],
            ]
        ),
        "capillaries": _markdown_list(
            [
                "# Command Capillary Atlas",
                "",
                f"- Docs gate: `{docs_gate_status}`",
                f"- Veins: `{vessel_counts.get('vein', 0)}`",
                f"- Capillaries: `{vessel_counts.get('capillary', 0)}`",
                f"- Candidates: `{vessel_counts.get('candidate', 0)}`",
                "",
                "## Strongest Edges",
                "",
                *[
                    f"- `{row.get('edge_id')}` :: `{row.get('source_ant_id')}` -> `{row.get('target_ant_id')}` :: class=`{row.get('vessel_class')}` :: strength=`{row.get('edge_strength')}`"
                    for row in top_capillaries
                ],
            ]
        ),
        "latency": _markdown_list(
            [
                "# Command Latency Receipt",
                "",
                f"- Docs gate: `{docs_gate_status}`",
                f"- Latency rows: `{latency_registry.get('row_count', 0)}`",
                f"- Live authority manifest: `{COMMAND_MEMBRANE_LIVE_MANIFEST}`",
                "",
                "## Coverage",
                "",
                f"- Event count: `{event_registry.get('event_count', 0)}`",
                f"- Claim rows: `{claim_ledger.get('row_count', 0)}`",
                f"- Zero-witness fallback events: `{fallback_event_count}`",
                "",
                "## Benchmarks",
                "",
                *[
                    f"- `{row.get('event_id')}` :: `T_sugar={row.get('t_sugar_ms')}` :: `capillary_score={row.get('capillary_score')}` :: source=`{row.get('source_id') or 'unregistered_local'}`"
                    for row in latency_rows[:8]
                ],
            ]
        ),
    }

    return {
        "packet_schema": packet_schema,
        "watched_surface_registry": watched_surface_registry,
        "event_registry": event_registry,
        "claim_ledger": claim_ledger,
        "capillary_registry": capillary_registry,
        "latency_registry": latency_registry,
        "manifest": manifest,
        "markdown_pages": markdown_pages,
    }
