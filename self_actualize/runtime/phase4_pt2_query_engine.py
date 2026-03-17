from __future__ import annotations

import heapq
import re
from typing import Any, Dict, Iterable, List, Tuple

from self_actualize.runtime.phase4_query_engine import objective_vector, shorten


PT2_FILTER_ORDER = [
    "authority",
    "witness",
    "zone",
    "surface_class",
    "system",
    "coordinate",
    "lens",
    "root",
    "family",
    "tags",
]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _registry_items(registries: Dict[str, Any], key: str, list_key: str) -> List[Dict[str, Any]]:
    payload = registries.get(key, {})
    return list(payload.get(list_key, []))


def build_alias_map(registries: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    alias_map: Dict[str, Dict[str, Any]] = {}

    def register(alias: str, payload: Dict[str, Any]) -> None:
        key = normalize(alias)
        if key:
            alias_map.setdefault(key, payload)

    for item in _registry_items(registries, "metro_system_registry", "systems"):
        register(item["system_id"], {"kind": "system", "payload": item})
        register(item["label"], {"kind": "system", "payload": item})

    for item in _registry_items(registries, "metro_station_registry", "stations"):
        register(item["station_id"], {"kind": "station", "payload": item})
        register(item["label"], {"kind": "station", "payload": item})

    for item in _registry_items(registries, "carrier_registry", "carriers"):
        register(item["carrier_id"], {"kind": "carrier", "payload": item})
        register(item["label"], {"kind": "carrier", "payload": item})

    for item in _registry_items(registries, "lens_hybrid_registry", "lenses"):
        register(item["lens_id"], {"kind": "lens", "payload": item})
        register(item["label"], {"kind": "lens", "payload": item})

    for item in _registry_items(registries, "field_registry", "fields"):
        register(item["field_id"], {"kind": "field", "payload": item})
        register(item["label"], {"kind": "field", "payload": item})

    for item in _registry_items(registries, "z_point_registry", "zpoints"):
        register(item["zpoint_id"], {"kind": "zpoint", "payload": item})
        register(item["label"], {"kind": "zpoint", "payload": item})

    for item in _registry_items(registries, "aether_point_registry", "aether_points"):
        register(item["point_id"], {"kind": "aether_point", "payload": item})
        register(item["source_record_id"], {"kind": "aether_point", "payload": item})

    for item in _registry_items(registries, "projection_space_registry", "spaces"):
        register(item["space_id"], {"kind": "projection_space", "payload": item})
        register(item["label"], {"kind": "projection_space", "payload": item})

    for item in _registry_items(registries, "lens_state_registry", "lens_states"):
        register(item["record_id"], {"kind": "lens_state", "payload": item})
        register(item["state_id"], {"kind": "lens_state", "payload": item})
        register(item["dominant_lens_system"], {"kind": "lens_state", "payload": item})

    for item in _registry_items(registries, "holo_coordinate_registry", "coordinates"):
        register(item["record_id"], {"kind": "coordinate", "payload": item})
        register(item["coord_id"], {"kind": "coordinate", "payload": item})
        register(item["addr4"], {"kind": "coordinate", "payload": item})

    return alias_map


def _match_text(query_norm: str, fields: Iterable[str]) -> float:
    haystack = normalize(" ".join(str(field) for field in fields if field))
    if not query_norm or not haystack:
        return 0.0
    if query_norm == haystack:
        return 1.0
    if query_norm in haystack:
        return 0.84
    tokens = set(query_norm.split())
    if not tokens:
        return 0.0
    overlap = tokens & set(haystack.split())
    if not overlap:
        return 0.0
    return round(0.4 + (0.45 * (len(overlap) / len(tokens))), 3)


def _requested_lenses(objective: str, registries: Dict[str, Any]) -> List[str]:
    query_norm = normalize(objective)
    requested: List[str] = []
    carrier_map = {"square": "S", "flower": "F", "cloud": "C", "fractal": "R"}
    letters = [value for key, value in carrier_map.items() if key in query_norm]
    if letters:
        requested.append("".join(letter for letter in "SFCR" if letter in letters))
    for item in _registry_items(registries, "lens_hybrid_registry", "lenses"):
        for field in [item["lens_id"], item["label"]]:
            if normalize(field) and normalize(field) in query_norm:
                requested.append(item["lens_id"])
    return list(dict.fromkeys(requested))


def _needs_quarantine(interlock_record: Dict[str, Any], registries: Dict[str, Any]) -> bool:
    if registries["dashboard"]["docs_gate"] != "BLOCKED":
        return False
    text = " ".join(
        [
            interlock_record.get("source_system", ""),
            interlock_record.get("target_system", ""),
            interlock_record.get("dispatch_rule", ""),
            interlock_record.get("note", ""),
            " ".join(interlock_record.get("witness_basis", [])),
        ]
    )
    return any(token in normalize(text) for token in ["trading bot", "historical", "reservoir"])


def locate(query: str, registries: Dict[str, Any], limit: int = 12) -> Dict[str, Any]:
    query_norm = normalize(query)
    results: List[Dict[str, Any]] = []

    collections = [
        ("system", _registry_items(registries, "metro_system_registry", "systems")),
        ("station", _registry_items(registries, "metro_station_registry", "stations")),
        ("carrier", _registry_items(registries, "carrier_registry", "carriers")),
        ("lens", _registry_items(registries, "lens_hybrid_registry", "lenses")),
        ("field", _registry_items(registries, "field_registry", "fields")),
        ("zpoint", _registry_items(registries, "z_point_registry", "zpoints")),
        ("aether_point", _registry_items(registries, "aether_point_registry", "aether_points")),
        ("projection_space", _registry_items(registries, "projection_space_registry", "spaces")),
        ("lens_state", _registry_items(registries, "lens_state_registry", "lens_states")),
        ("coordinate", _registry_items(registries, "holo_coordinate_registry", "coordinates")),
    ]

    for kind, items in collections:
        for item in items:
            score = _match_text(
                query_norm,
                [
                    item.get("system_id"),
                    item.get("station_id"),
                    item.get("carrier_id"),
                    item.get("lens_id"),
                    item.get("field_id"),
                    item.get("zpoint_id"),
                    item.get("point_id"),
                    item.get("space_id"),
                    item.get("state_id"),
                    item.get("coord_id"),
                    item.get("label"),
                    item.get("record_id"),
                    item.get("record_type"),
                    item.get("role"),
                    item.get("note"),
                ],
            )
            if score <= 0.0:
                continue
            label_norm = normalize(
                item.get("label")
                or item.get("record_id")
                or item.get("system_id")
                or item.get("station_id")
                or ""
            )
            if query_norm and query_norm == label_norm:
                score = round(score + 0.12, 3)
            results.append(
                {
                    "kind": kind,
                    "label": item.get("label")
                    or item.get("record_id")
                    or item.get("system_id")
                    or item.get("station_id"),
                    "score": round(score, 3),
                    "payload": item,
                }
            )

    results.sort(key=lambda item: (-item["score"], item["label"]))
    return {
        "mode": "locate",
        "query": query,
        "filter_order": PT2_FILTER_ORDER,
        "results": results[:limit],
    }


def interlock(query: str, registries: Dict[str, Any], limit: int = 12) -> Dict[str, Any]:
    query_norm = normalize(query)
    matches: List[Dict[str, Any]] = []
    for item in _registry_items(registries, "metro_interlock_registry", "interlocks"):
        score = _match_text(
            query_norm,
            [
                item["interlock_id"],
                item["source_system"],
                item["source_station"],
                item["target_system"],
                item["target_station"],
                item["transform_kind"],
                item["dispatch_rule"],
                item["note"],
            ],
        )
        if score <= 0.0:
            continue
        matches.append(
            {
                "interlock_id": item["interlock_id"],
                "score": round(score + (item.get("dispatch_score", 0.0) / 20.0), 3),
                "source_system": item["source_system"],
                "target_system": item["target_system"],
                "transform_kind": item["transform_kind"],
                "dispatch_score": item.get("dispatch_score", 0.0),
                "proof_state": item["proof_state"],
                "route_via": item["route_via"],
                "return_path": item["return_path"],
                "dispatch_rule": item["dispatch_rule"],
                "witness_basis": item["witness_basis"],
                "note": item.get("note", ""),
            }
        )
    matches.sort(key=lambda item: (-item["score"], -item["dispatch_score"], item["interlock_id"]))
    return {
        "mode": "interlock",
        "query": query,
        "results": matches[:limit],
    }


def lens(query: str, registries: Dict[str, Any], limit: int = 12) -> Dict[str, Any]:
    query_norm = normalize(query)
    profiles = _registry_items(registries, "lens_weight_profile_registry", "profiles")
    states = _registry_items(registries, "lens_state_registry", "lens_states")

    profile_hits: List[Dict[str, Any]] = []
    for item in profiles:
        score = _match_text(
            query_norm,
            [
                item["lens_id"],
                item["label"],
                " ".join(item["members"]),
                " ".join(item["preferred_channels"]),
                " ".join(item["preferred_carriers"]),
                item["certificate_rule"],
                item["note"],
            ],
        )
        if score <= 0.0:
            continue
        profile_hits.append(
            {
                "lens_id": item["lens_id"],
                "label": item["label"],
                "score": score,
                "preferred_carriers": item["preferred_carriers"],
                "preferred_rails": item["preferred_rails"],
                "shortcut_chain": item["shortcut_chain"],
                "stop_condition": item["stop_condition"],
            }
        )

    state_hits: List[Dict[str, Any]] = []
    for item in states:
        score = _match_text(
            query_norm,
            [
                item["record_id"],
                item["record_type"],
                item["dominant_lens_system"],
                item["secondary_lens_system"],
                " ".join(item["preferred_carriers"]),
                " ".join(item["preferred_rails"]),
            ],
        )
        if score <= 0.0:
            continue
        dominant_score = float(item["lens_weight_vector"].get(item["dominant_lens_system"], 0.0))
        state_hits.append(
            {
                "record_id": item["record_id"],
                "record_type": item["record_type"],
                "dominant_lens_system": item["dominant_lens_system"],
                "secondary_lens_system": item["secondary_lens_system"],
                "dominant_score": round(dominant_score, 3),
                "score": round(score + dominant_score, 3),
                "field_weight_vector": item["field_weight_vector"],
            }
        )

    profile_hits.sort(key=lambda item: (-item["score"], item["lens_id"]))
    state_hits.sort(key=lambda item: (-item["score"], item["record_id"]))
    return {
        "mode": "lens",
        "query": query,
        "profiles": profile_hits[:limit],
        "states": state_hits[:limit],
    }


def field(query: str, registries: Dict[str, Any], limit: int = 12) -> Dict[str, Any]:
    query_norm = normalize(query)
    field_hits: List[Dict[str, Any]] = []
    for item in _registry_items(registries, "field_registry", "fields"):
        score = _match_text(
            query_norm,
            [
                item["field_id"],
                item["label"],
                item["role"],
                " ".join(item["carrier_binding"]),
                item.get("note", ""),
            ],
        )
        if score <= 0.0:
            continue
        field_hits.append(
            {
                "field_id": item["field_id"],
                "label": item["label"],
                "score": score,
                "carrier_binding": item["carrier_binding"],
                "thresholds": item["thresholds"],
            }
        )

    z_hits: List[Dict[str, Any]] = []
    for item in _registry_items(registries, "z_point_registry", "zpoints"):
        score = _match_text(
            query_norm,
            [
                item["zpoint_id"],
                item["label"],
                item["route_class"],
                item["restart_token"],
                " ".join(item["binding_hubs"]),
                item.get("note", ""),
            ],
        )
        if score <= 0.0:
            continue
        z_hits.append(
            {
                "zpoint_id": item["zpoint_id"],
                "label": item["label"],
                "score": score,
                "route_class": item["route_class"],
                "proof_state": item["proof_state"],
            }
        )

    aether_hits: List[Dict[str, Any]] = []
    for item in _registry_items(registries, "aether_point_registry", "aether_points"):
        score = _match_text(
            query_norm,
            [
                item["point_id"],
                item["source_record_id"],
                item["source_record_type"],
                item["lens_system"],
                item["system_id"],
                item["geodesic_mode"],
                item.get("note", ""),
            ],
        )
        if score <= 0.0:
            continue
        aether_hits.append(
            {
                "point_id": item["point_id"],
                "source_record_id": item["source_record_id"],
                "score": round(score + item["aether_density"], 3),
                "aether_density": item["aether_density"],
                "zero_proximity": item["zero_proximity"],
                "geodesic_mode": item["geodesic_mode"],
            }
        )

    field_hits.sort(key=lambda item: (-item["score"], item["field_id"]))
    z_hits.sort(key=lambda item: (-item["score"], item["zpoint_id"]))
    aether_hits.sort(key=lambda item: (-item["score"], item["point_id"]))
    return {
        "mode": "field",
        "query": query,
        "fields": field_hits[:limit],
        "zpoints": z_hits[:limit],
        "aether_points": aether_hits[:limit],
    }


def project(query: str, registries: Dict[str, Any], limit: int = 12) -> Dict[str, Any]:
    query_norm = normalize(query)
    spaces = _registry_items(registries, "projection_space_registry", "spaces")
    assignments = _registry_items(registries, "projection_assignment_registry", "assignments")

    space_hits: List[Dict[str, Any]] = []
    for item in spaces:
        score = _match_text(
            query_norm,
            [
                item["space_id"],
                item["label"],
                " ".join(item["axes"]),
                " ".join(item["carrier_focus"]),
                " ".join(item["crosswalk_rules"]),
            ],
        )
        if score <= 0.0:
            continue
        if query_norm in {normalize(item["space_id"]), normalize(item["label"])}:
            score = round(score + 0.12, 3)
        space_hits.append(
            {
                "space_id": item["space_id"],
                "label": item["label"],
                "score": score,
                "axes": item["axes"],
                "carrier_focus": item["carrier_focus"],
            }
        )

    assignment_hits: List[Dict[str, Any]] = []
    for item in assignments:
        score = _match_text(
            query_norm,
            [
                item["record_id"],
                item["record_type"],
                item["preferred_space"],
                " ".join(item["supported_spaces"]),
                " ".join(item["unsupported_spaces"]),
            ],
        )
        if score <= 0.0:
            continue
        assignment_hits.append(
            {
                "record_id": item["record_id"],
                "record_type": item["record_type"],
                "preferred_space": item["preferred_space"],
                "supported_spaces": item["supported_spaces"],
                "unsupported_spaces": item["unsupported_spaces"],
                "score": score,
            }
        )

    space_hits.sort(key=lambda item: (-item["score"], item["space_id"]))
    assignment_hits.sort(key=lambda item: (-item["score"], item["record_id"]))
    return {
        "mode": "project",
        "query": query,
        "spaces": space_hits[:limit],
        "assignments": assignment_hits[:limit],
    }


def _resolve_system(query: str, registries: Dict[str, Any]) -> Tuple[str | None, Dict[str, Any] | None]:
    alias_map = build_alias_map(registries)
    hit = alias_map.get(normalize(query))
    if not hit:
        locate_result = locate(query, registries, limit=1).get("results", [])
        hit = locate_result[0] if locate_result else None
        if hit and "payload" in hit:
            hit = {"kind": hit["kind"], "payload": hit["payload"]}
    if not hit:
        return None, None

    kind = hit["kind"]
    payload = hit["payload"]
    if kind == "system":
        return payload["system_id"], payload
    if kind == "station":
        return (payload["system_ids"][0] if payload["system_ids"] else None), payload
    if kind == "coordinate":
        return payload["system_id"], payload
    if kind == "lens_state":
        coordinates = _registry_items(registries, "holo_coordinate_registry", "coordinates")
        match = next((item for item in coordinates if item["record_id"] == payload["record_id"]), None)
        return (match["system_id"] if match else None), payload
    if kind == "aether_point":
        return payload["system_id"], payload
    return None, payload


def route(source: str, target: str, registries: Dict[str, Any]) -> Dict[str, Any]:
    source_system, source_payload = _resolve_system(source, registries)
    target_system, target_payload = _resolve_system(target, registries)
    if not source_system or not target_system:
        return {
            "mode": "route",
            "source": source,
            "target": target,
            "outcome": "ABSTAIN",
            "reason": "Could not resolve one or both endpoints into Pt 2 systems.",
        }

    if source_system == target_system:
        return {
            "mode": "route",
            "source": source,
            "target": target,
            "outcome": "REPAIR",
            "system_path": [source_system],
            "interlocks": [],
            "reason": "Both endpoints resolve inside the same Pt 2 metro system.",
        }

    graph: Dict[str, List[Tuple[float, Dict[str, Any], str]]] = {}
    for item in _registry_items(registries, "metro_interlock_registry", "interlocks"):
        cost = round(max(0.1, 10.0 - float(item.get("dispatch_score", 5.0))), 3)
        graph.setdefault(item["source_system"], []).append((cost, item, item["target_system"]))
        graph.setdefault(item["target_system"], []).append((cost + 0.1, item, item["source_system"]))

    queue: List[Tuple[float, str, List[str], List[Dict[str, Any]]]] = [(0.0, source_system, [source_system], [])]
    best: Dict[str, float] = {source_system: 0.0}

    while queue:
        total_cost, current, path, interlocks_used = heapq.heappop(queue)
        if current == target_system:
            outcome = "PROMOTE"
            if any(_needs_quarantine(interlock, registries) for interlock in interlocks_used):
                outcome = "QUARANTINE"
            return {
                "mode": "route",
                "source": source,
                "target": target,
                "source_system": source_system,
                "target_system": target_system,
                "system_path": path,
                "interlocks": [
                    {
                        "interlock_id": item["interlock_id"],
                        "source_system": item["source_system"],
                        "target_system": item["target_system"],
                        "transform_kind": item["transform_kind"],
                        "route_via": item["route_via"],
                        "dispatch_score": item["dispatch_score"],
                        "witness_basis": item["witness_basis"],
                    }
                    for item in interlocks_used
                ],
                "outcome": outcome,
            }
        for cost, interlock, neighbor in graph.get(current, []):
            candidate_cost = total_cost + cost
            if candidate_cost >= best.get(neighbor, 10_000.0):
                continue
            best[neighbor] = candidate_cost
            heapq.heappush(queue, (candidate_cost, neighbor, path + [neighbor], interlocks_used + [interlock]))

    return {
        "mode": "route",
        "source": source,
        "target": target,
        "outcome": "ABSTAIN",
        "reason": "No lawful interlock chain was found.",
    }


def fire(objective: str, registries: Dict[str, Any], limit: int = 12) -> Dict[str, Any]:
    objective_weights = objective_vector(objective)
    requested_lenses = _requested_lenses(objective, registries)
    candidates: List[Dict[str, Any]] = []
    states = _registry_items(registries, "lens_state_registry", "lens_states")
    profiles = {item["lens_id"]: item for item in _registry_items(registries, "lens_weight_profile_registry", "profiles")}

    for item in states:
        profile = profiles.get(item["dominant_lens_system"])
        if not profile:
            continue
        channel_weights = profile["channel_weights"]
        affective_score = sum(
            float(channel_weights.get(channel, 0.0)) * float(objective_weights.get(channel, 0.0))
            for channel in objective_weights
        )
        lens_score = max(item["lens_weight_vector"].values()) if item["lens_weight_vector"] else 0.0
        requested_bonus = 0.0
        if requested_lenses:
            requested_bonus = max(
                float(item["lens_weight_vector"].get(lens_id, 0.0))
                for lens_id in requested_lenses
            )
        field = item["field_weight_vector"]
        field_bonus = 0.25 * float(field.get("aether_density", 0.0))
        if any(token in normalize(objective) for token in ["zero", "tunnel", "restart", "field", "aether"]):
            field_bonus += 0.2 * float(field.get("zero_proximity", 0.0))
        score = round(affective_score + lens_score + field_bonus + (0.35 * requested_bonus), 4)
        candidates.append(
            {
                "record_id": item["record_id"],
                "record_type": item["record_type"],
                "dominant_lens_system": item["dominant_lens_system"],
                "secondary_lens_system": item["secondary_lens_system"],
                "score": score,
                "field_weight_vector": field,
                "supported_projection_spaces": item["supported_projection_spaces"],
            }
        )

    candidates.sort(key=lambda item: (-item["score"], item["record_id"]))
    return {
        "mode": "fire",
        "objective": objective,
        "topk_policy": "sparse_pt2_lens_and_field_firing",
        "results": candidates[:limit],
    }


def promote(candidate: str | None, registries: Dict[str, Any]) -> Dict[str, Any]:
    if not candidate:
        top = sorted(
            _registry_items(registries, "metro_interlock_registry", "interlocks"),
            key=lambda item: (-item.get("dispatch_score", 0.0), item["interlock_id"]),
        )
        if not top:
            return {
                "mode": "promote",
                "outcome": "ABSTAIN",
                "reason": "No interlocks available for promotion.",
            }
        candidate = top[0]["interlock_id"]

    query_result = interlock(candidate, registries, limit=1).get("results", [])
    if not query_result:
        return {
            "mode": "promote",
            "candidate": candidate,
            "outcome": "ABSTAIN",
            "reason": "Candidate did not resolve to a lawful interlock.",
        }
    item = query_result[0]
    if _needs_quarantine(item, registries):
        outcome = "QUARANTINE"
    elif item["dispatch_score"] >= 7.0 and item["proof_state"] in {"OK", "NEAR"}:
        outcome = "PROMOTE"
    elif item["dispatch_score"] >= 6.0:
        outcome = "REPAIR"
    else:
        outcome = "ABSTAIN"
    return {
        "mode": "promote",
        "candidate": candidate,
        "outcome": outcome,
        "interlock": item,
    }
