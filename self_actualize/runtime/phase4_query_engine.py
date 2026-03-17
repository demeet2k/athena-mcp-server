from __future__ import annotations

import heapq
import re
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple


SPECIAL_SURFACES = {
    "GC0": {
        "surface_type": "station",
        "label": "Grand Central Station",
        "aliases": ["grand central", "grand central station", "gc0"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
    "GCL": {
        "surface_type": "hemisphere",
        "label": "Left Hemisphere Exchange",
        "aliases": ["gcl", "left hemisphere exchange", "left hemisphere"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
    "GCR": {
        "surface_type": "hemisphere",
        "label": "Right Hemisphere Exchange",
        "aliases": ["gcr", "right hemisphere exchange", "right hemisphere"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
    "GCW": {
        "surface_type": "station",
        "label": "Weight Mezzanine",
        "aliases": ["gcw", "weight mezzanine"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
    "GCZ": {
        "surface_type": "station",
        "label": "Z-Point Tunnel Junction",
        "aliases": ["gcz", "z-point tunnel junction", "z point tunnel junction"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
    "GCX": {
        "surface_type": "station",
        "label": "Cross-Corpus Departure Yard",
        "aliases": ["gcx", "cross corpus departure yard"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
    "GCA": {
        "surface_type": "tract",
        "label": "Address Tract",
        "aliases": ["gca", "address tract"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
    "GCT": {
        "surface_type": "tract",
        "label": "Relation Tract",
        "aliases": ["gct", "relation tract"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
    "GCC": {
        "surface_type": "tract",
        "label": "Chamber Tract",
        "aliases": ["gcc", "chamber tract"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
    "GCP": {
        "surface_type": "tract",
        "label": "Replay Concourse",
        "aliases": ["gcp", "replay concourse"],
        "authority_surface": "NERVOUS_SYSTEM/10_OVERVIEW/15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md",
    },
}

MODE_SHORTCUTS = {
    "locate": ["SC-01", "SC-02", "SC-11", "SC-12", "SC-13"],
    "route": ["SC-01", "SC-02", "SC-04", "SC-05", "SC-06", "SC-13"],
    "neglect": ["SC-01", "SC-08", "SC-09", "SC-10", "SC-12", "SC-13"],
    "fire": ["SC-03", "SC-04", "SC-05", "SC-06", "SC-10", "SC-11", "SC-13"],
    "promote": ["SC-01", "SC-04", "SC-05", "SC-09", "SC-10", "SC-13"],
}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def shorten(text: str, limit: int = 120) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def objective_vector(objective: str) -> Dict[str, float]:
    key = normalize(objective)
    vector = {
        "emotion": 0.12,
        "feeling": 0.12,
        "knowledge": 0.14,
        "desire": 0.12,
        "memory": 0.12,
        "boundary": 0.12,
        "repair": 0.14,
        "imagination": 0.12,
    }
    if any(token in key for token in ["knowledge", "proof", "verify", "witness"]):
        vector.update(
            knowledge=0.28,
            boundary=0.18,
            memory=0.14,
            repair=0.10,
            imagination=0.10,
            emotion=0.08,
            feeling=0.06,
            desire=0.06,
        )
    if any(token in key for token in ["emotion", "feeling", "affective", "care"]):
        vector.update(
            emotion=0.27,
            feeling=0.24,
            desire=0.14,
            imagination=0.14,
            memory=0.09,
            knowledge=0.06,
            boundary=0.03,
            repair=0.03,
        )
    if any(token in key for token in ["memory", "replay", "continuity"]):
        vector.update(
            memory=0.29,
            feeling=0.17,
            repair=0.15,
            knowledge=0.14,
            boundary=0.11,
            imagination=0.08,
            emotion=0.04,
            desire=0.02,
        )
    if any(token in key for token in ["repair", "neglect", "restart", "prune"]):
        vector.update(
            repair=0.24,
            boundary=0.18,
            knowledge=0.14,
            memory=0.14,
            feeling=0.10,
            emotion=0.08,
            imagination=0.07,
            desire=0.05,
        )
    if any(token in key for token in ["promote", "weave", "interconnect", "lift"]):
        vector.update(
            desire=0.22,
            knowledge=0.20,
            repair=0.15,
            imagination=0.15,
            boundary=0.12,
            emotion=0.08,
            feeling=0.05,
            memory=0.03,
        )
    total = sum(vector.values()) or 1.0
    return {key: round(value / total, 3) for key, value in vector.items()}


def lookup_shortcuts(registries: Dict[str, Any], shortcut_ids: Iterable[str]) -> List[Dict[str, Any]]:
    records = {item["shortcut_id"]: item for item in registries["shortcut_registry"]["shortcuts"]}
    return [records[shortcut_id] for shortcut_id in shortcut_ids if shortcut_id in records]


def build_alias_map(registries: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    alias_map: Dict[str, Dict[str, str]] = {}
    for surface_id, payload in SPECIAL_SURFACES.items():
        for alias in payload["aliases"]:
            alias_map[normalize(alias)] = {
                "surface_id": surface_id,
                "surface_type": payload["surface_type"],
                "label": payload["label"],
            }
    for body in registries["body_registry"]["bodies"]:
        aliases = [body["body_id"], body["root"], body["role"]]
        for alias in aliases:
            alias_map[normalize(alias)] = {
                "surface_id": body["body_id"],
                "surface_type": "body",
                "label": body["root"],
            }
    for anchor in registries["body_registry"]["root_anchors"]:
        for alias in [anchor["root_id"], anchor["root"], anchor["current_role"]]:
            alias_map.setdefault(
                normalize(alias),
                {
                "surface_id": anchor["root_id"],
                "surface_type": "root_anchor",
                "label": anchor["root"],
                },
            )
    for kernel in registries["kernel_registry"]["kernels"]:
        for alias in [kernel["kernel_id"], kernel["source_title"], kernel["cluster"]]:
            alias_map.setdefault(
                normalize(alias),
                {
                "surface_id": kernel["kernel_id"],
                "surface_type": "kernel",
                "label": kernel["source_title"],
                },
            )
    for pair in registries["pair_registry"]["pairs"]:
        aliases = [pair["pair_id"], pair["pair_title"], pair["relation_law"]]
        for alias in aliases:
            alias_map.setdefault(
                normalize(alias),
                {
                "surface_id": pair["pair_id"],
                "surface_type": "pair",
                "label": pair["pair_title"],
                },
            )
    for node in registries["node_registry"]["nodes"]:
        for alias in [node["node_id"], node["role"], *node.get("tags", [])]:
            alias_map.setdefault(
                normalize(alias),
                {
                "surface_id": node["node_id"],
                "surface_type": "node",
                "label": node["role"],
                },
            )
    return alias_map


def record_search_fields(record: Dict[str, Any], record_type: str) -> str:
    values: List[str] = []
    if record_type == "body":
        values.extend(
            [
                record["body_id"],
                record["root"],
                record["role"],
                record["authority"],
                record["status"],
            ]
        )
    elif record_type == "root_anchor":
        values.extend(
            [record["root_id"], record["root"], record["current_role"], record["status"]]
        )
    elif record_type == "kernel":
        values.extend(
            [
                record["kernel_id"],
                record["source_title"],
                record["cluster"],
                record["element"],
                record["body_binding"],
            ]
        )
    elif record_type == "pair":
        values.extend(
            [
                record["pair_id"],
                record["pair_title"],
                record["relation_law"],
                record["bridge_opportunity"],
                " ".join(record.get("appendix_support", [])),
            ]
        )
    elif record_type == "node":
        values.extend(
            [
                record["node_id"],
                record["role"],
                record["surface_class"],
                " ".join(record.get("tags", [])),
            ]
        )
    elif record_type == "wave":
        values.extend([record["wave_id"], record["pair_id"], record["objective"]])
    values.extend(record.get("source_paths", []))
    return normalize(" ".join(values))


def locate(query: str, registries: Dict[str, Any], limit: int = 8) -> Dict[str, Any]:
    query_norm = normalize(query)
    results: List[Dict[str, Any]] = []

    for surface_id, payload in SPECIAL_SURFACES.items():
        haystack = normalize(" ".join([payload["label"], *payload["aliases"]]))
        if query_norm in haystack:
            score = 100.0 if query_norm in {normalize(alias) for alias in payload["aliases"]} else 82.0
            results.append(
                {
                    "surface_id": surface_id,
                    "surface_type": payload["surface_type"],
                    "label": payload["label"],
                    "score": score,
                    "authority_surface": payload["authority_surface"],
                    "source_paths": [payload["authority_surface"]],
                }
            )

    collections = [
        ("body", registries["body_registry"]["bodies"]),
        ("root_anchor", registries["body_registry"]["root_anchors"]),
        ("kernel", registries["kernel_registry"]["kernels"]),
        ("node", registries["node_registry"]["nodes"]),
        ("pair", registries["pair_registry"]["pairs"]),
        ("wave", registries["wave_registry"]["waves"]),
    ]
    for record_type, items in collections:
        for item in items:
            haystack = record_search_fields(item, record_type)
            if not query_norm or query_norm not in haystack:
                continue
            exact_id = normalize(item.get("body_id") or item.get("root_id") or item.get("kernel_id") or item.get("node_id") or item.get("pair_id") or item.get("wave_id", ""))
            label = (
                item.get("root")
                or item.get("source_title")
                or item.get("role")
                or item.get("pair_title")
                or item.get("objective")
                or item.get("root")
            )
            score = 72.0
            if exact_id == query_norm:
                score = 100.0
            elif normalize(label) == query_norm:
                score = 94.0
            elif query_norm in normalize(label):
                score = 84.0
            results.append(
                {
                    "surface_id": item.get("body_id")
                    or item.get("root_id")
                    or item.get("kernel_id")
                    or item.get("node_id")
                    or item.get("pair_id")
                    or item.get("wave_id"),
                    "surface_type": record_type,
                    "label": label,
                    "score": score,
                    "authority_surface": item.get("authority_surface", registries["pair_registry"]["authority_surface"]),
                    "source_paths": item.get("source_paths", []),
                }
            )

    deduped: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for result in results:
        key = (result["surface_type"], result["surface_id"])
        if key not in deduped or result["score"] > deduped[key]["score"]:
            deduped[key] = result
    ranked = sorted(deduped.values(), key=lambda item: (-item["score"], item["surface_id"]))[:limit]
    return {
        "mode": "locate",
        "query": query,
        "matches": ranked,
        "active_shortcuts": lookup_shortcuts(registries, MODE_SHORTCUTS["locate"]),
        "stop_condition": "PROMOTE" if ranked else "ABSTAIN",
        "witness_basis": [
            registries["body_registry"]["authority_surface"],
            registries["kernel_registry"]["authority_surface"],
            registries["pair_registry"]["authority_surface"],
        ],
    }


def resolve_surface(reference: str, registries: Dict[str, Any]) -> Dict[str, Any] | None:
    alias_map = build_alias_map(registries)
    key = normalize(reference)
    if key in alias_map:
        return alias_map[key]
    located = locate(reference, registries, limit=1)["matches"]
    return located[0] if located else None


def build_route_graph(registries: Dict[str, Any]) -> Tuple[Dict[str, List[Tuple[str, float, str]]], Dict[str, str]]:
    graph: Dict[str, List[Tuple[str, float, str]]] = defaultdict(list)
    labels: Dict[str, str] = {surface_id: payload["label"] for surface_id, payload in SPECIAL_SURFACES.items()}

    def connect(left: str, right: str, cost: float, reason: str) -> None:
        graph[left].append((right, cost, reason))
        graph[right].append((left, cost, reason))

    connect("GCL", "GCW", 0.20, "hemisphere-to-weight")
    connect("GCR", "GCW", 0.20, "hemisphere-to-weight")
    connect("GCW", "GCA", 0.18, "weight-to-address")
    connect("GCW", "GCT", 0.18, "weight-to-relation")
    connect("GCW", "GCC", 0.18, "weight-to-chamber")
    connect("GCW", "GCP", 0.18, "weight-to-replay")
    connect("GCA", "GCZ", 0.22, "address-to-zpoint")
    connect("GCT", "GCZ", 0.22, "relation-to-zpoint")
    connect("GCC", "GCZ", 0.22, "chamber-to-zpoint")
    connect("GCP", "GCZ", 0.22, "replay-to-zpoint")
    connect("GCP", "GCX", 0.20, "replay-to-departure")
    connect("GC0", "GCW", 0.16, "station-to-weight")
    connect("GC0", "GCZ", 0.16, "station-to-zpoint")
    connect("GC0", "GCX", 0.16, "station-to-departure")

    body_lookup = {body["body_id"]: body for body in registries["body_registry"]["bodies"]}
    kernel_lookup = {kernel["kernel_id"]: kernel for kernel in registries["kernel_registry"]["kernels"]}

    tract_to_node = {"address": "GCA", "relation": "GCT", "chamber": "GCC", "replay": "GCP"}

    for body in body_lookup.values():
        body_id = body["body_id"]
        labels[body_id] = body["root"]
        connect(body_id, "GC0", 0.60, "body-to-station")
        tract_node = tract_to_node.get(body["tract"], "GCT")
        connect(body_id, tract_node, 0.38, "body-to-tract")
        if body["hemisphere_bias"] in {"left", "bilateral"}:
            connect(body_id, "GCL", 0.32, "body-to-left-hemisphere")
        if body["hemisphere_bias"] in {"right", "bilateral"}:
            connect(body_id, "GCR", 0.32, "body-to-right-hemisphere")

    for kernel in kernel_lookup.values():
        kernel_id = kernel["kernel_id"]
        labels[kernel_id] = kernel["source_title"]
        connect(kernel_id, kernel["body_id"], 0.52, "kernel-to-body-binding")
        connect(kernel_id, tract_to_node.get(kernel["tract"], "GCT"), 0.28, "kernel-to-tract")

    for pair in registries["pair_registry"]["pairs"]:
        pair_id = pair["pair_id"]
        labels[pair_id] = pair["pair_title"]
        connect(pair_id, pair["row_kernel_id"], 0.30, "pair-to-row-kernel")
        connect(pair_id, pair["col_kernel_id"], 0.30, "pair-to-col-kernel")
        connect(pair_id, pair["tract"], 0.26, "pair-to-tract")
        if pair["dock"] == "GCZ":
            connect(pair_id, "GCZ", 0.24, "pair-to-zpoint")
        if pair["dock"] == "GCX":
            connect(pair_id, "GCX", 0.24, "pair-to-departure")

    root_links = {
        "R01": ["GCZ", "A02", "A15", "K14", "K15"],
        "R02": ["GCP", "A01", "A02", "K01"],
        "R03": ["GCX", "A16", "A01"],
    }
    for anchor in registries["body_registry"]["root_anchors"]:
        anchor_id = anchor["root_id"]
        labels[anchor_id] = anchor["root"]
        for target in root_links.get(anchor_id, []):
            connect(anchor_id, target, 0.34, "root-anchor-link")

    weights = {item["commissure_id"]: item for item in registries["weight_exchange"]["routes"]}
    body_name_to_id = {body["root"]: body["body_id"] for body in body_lookup.values()}
    for commissure in registries["commissure_ledger"]["commissures"]:
        source = body_name_to_id.get(commissure["source_family"])
        target = body_name_to_id.get(commissure["target_family"])
        if not source or not target:
            continue
        dispatch = weights.get(commissure["commissure_id"], {}).get("dispatch_score", 5.8)
        cost = round(max(0.35, 9.5 - dispatch), 3)
        connect(source, target, cost, commissure["class"])

    return graph, labels


def dijkstra(graph: Dict[str, List[Tuple[str, float, str]]], start: str, goal: str) -> Tuple[float, List[str]]:
    heap: List[Tuple[float, str]] = [(0.0, start)]
    best = {start: 0.0}
    parent: Dict[str, str | None] = {start: None}
    while heap:
        cost, node = heapq.heappop(heap)
        if node == goal:
            break
        if cost > best.get(node, float("inf")):
            continue
        for neighbor, weight, _reason in graph.get(node, []):
            new_cost = round(cost + weight, 6)
            if new_cost < best.get(neighbor, float("inf")):
                best[neighbor] = new_cost
                parent[neighbor] = node
                heapq.heappush(heap, (new_cost, neighbor))
    if goal not in best:
        return float("inf"), []
    path = [goal]
    while path[-1] != start:
        path.append(parent[path[-1]])  # type: ignore[arg-type]
    path.reverse()
    return best[goal], path


def route(source: str, target: str, registries: Dict[str, Any]) -> Dict[str, Any]:
    source_surface = resolve_surface(source, registries)
    target_surface = resolve_surface(target, registries)
    if not source_surface or not target_surface:
        return {
            "mode": "route",
            "source": source,
            "target": target,
            "path": [],
            "active_shortcuts": lookup_shortcuts(registries, MODE_SHORTCUTS["route"]),
            "stop_condition": "ABSTAIN",
            "witness_basis": [registries["body_registry"]["authority_surface"]],
        }

    graph, labels = build_route_graph(registries)
    cost, path = dijkstra(graph, source_surface["surface_id"], target_surface["surface_id"])
    if not path:
        return {
            "mode": "route",
            "source": source_surface,
            "target": target_surface,
            "path": [],
            "active_shortcuts": lookup_shortcuts(registries, MODE_SHORTCUTS["route"]),
            "stop_condition": "ABSTAIN",
            "witness_basis": [registries["body_registry"]["authority_surface"]],
        }

    path_labels = [{"surface_id": node, "label": labels.get(node, node)} for node in path]
    stop_condition = "PROMOTE"
    risk_nodes = {"A07", "K15", "R01"}
    if any(node in risk_nodes for node in path):
        stop_condition = "QUARANTINE" if "A07" in path or "K15" in path else "REPAIR"
    elif cost >= 6.5:
        stop_condition = "REPAIR"

    return {
        "mode": "route",
        "source": source_surface,
        "target": target_surface,
        "path": path_labels,
        "route_cost": round(cost, 3),
        "active_shortcuts": lookup_shortcuts(registries, MODE_SHORTCUTS["route"]),
        "stop_condition": stop_condition,
        "witness_basis": [
            registries["body_registry"]["authority_surface"],
            registries["weight_exchange"]["authority_surface"],
            registries["pair_registry"]["authority_surface"],
        ],
    }


def neglect(registries: Dict[str, Any], limit: int = 8) -> Dict[str, Any]:
    signals = sorted(
        registries["neglect_registry"]["signals"],
        key=lambda item: (-item["score"], item["surface_id"]),
    )[:limit]
    return {
        "mode": "neglect",
        "signals": signals,
        "active_shortcuts": lookup_shortcuts(registries, MODE_SHORTCUTS["neglect"]),
        "stop_condition": "REPAIR" if signals else "ABSTAIN",
        "witness_basis": [
            registries["neglect_registry"]["authority_surface"],
            registries["body_registry"]["authority_surface"],
            registries["pair_registry"]["authority_surface"],
        ],
    }


def score_pair_for_objective(pair: Dict[str, Any], objective: str) -> float:
    weights = objective_vector(objective)
    charge_seed = pair.get("charge_seed", {})
    score = sum(weights[key] * charge_seed.get(key, 0.0) for key in weights)
    objective_key = normalize(objective)
    neglect_bonus = (pair["neglect_score"] / 100.0) if any(
        token in objective_key for token in ["repair", "neglect", "prune", "restart"]
    ) else 0.0
    return round(score + (0.16 * pair.get("witness_floor", 0.0)) + (0.18 * neglect_bonus), 4)


def fire(objective: str, registries: Dict[str, Any], limit: int = 8) -> Dict[str, Any]:
    ranked = sorted(
        (
            {
                "pair_id": pair["pair_id"],
                "pair_title": pair["pair_title"],
                "score": score_pair_for_objective(pair, objective),
                "charge_vector": pair.get("charge_seed", {}),
                "witness_floor": pair.get("witness_floor", 0.0),
                "neglect_score": pair.get("neglect_score", 0.0),
                "dock": pair.get("dock", ""),
                "source_paths": pair.get("source_paths", []),
            }
            for pair in registries["pair_registry"]["pairs"]
        ),
        key=lambda item: (-item["score"], item["pair_id"]),
    )[:limit]

    stop_condition = "PROMOTE"
    if not ranked:
        stop_condition = "ABSTAIN"
    elif ranked[0]["witness_floor"] < 0.55:
        stop_condition = "ABSTAIN"
    elif ranked[0]["charge_vector"].get("boundary", 0.0) >= 0.9 and "promote" in normalize(objective):
        stop_condition = "QUARANTINE"
    elif any(token in normalize(objective) for token in ["repair", "neglect", "restart", "prune"]):
        stop_condition = "REPAIR"

    return {
        "mode": "fire",
        "objective": objective,
        "materialized_waves": ranked,
        "active_shortcuts": lookup_shortcuts(registries, MODE_SHORTCUTS["fire"]),
        "stop_condition": stop_condition,
        "witness_basis": [
            registries["pair_registry"]["authority_surface"],
            registries["wave_registry"]["authority_surface"],
        ],
    }


def promote(candidate_ref: str | None, registries: Dict[str, Any]) -> Dict[str, Any]:
    candidates = registries["weave_registry"]["candidates"]
    candidate = None
    if candidate_ref:
        norm = normalize(candidate_ref)
        for item in candidates:
            if normalize(item["weave_id"]) == norm or normalize(item["src"]) == norm:
                candidate = item
                break
    if candidate is None and candidates:
        candidate = sorted(candidates, key=lambda item: (-item["expected_gain"], item["weave_id"]))[0]
    if candidate is None:
        return {
            "mode": "promote",
            "candidate": None,
            "active_shortcuts": lookup_shortcuts(registries, MODE_SHORTCUTS["promote"]),
            "stop_condition": "ABSTAIN",
            "witness_basis": [registries["weave_registry"]["authority_surface"]],
        }

    stop_condition = "PROMOTE"
    src_target_norm = normalize(candidate["source_surface"] + " " + candidate["target_surface"])
    if "trading bot" in src_target_norm and registries["docs_gate"] == "BLOCKED":
        stop_condition = "QUARANTINE"
    elif candidate["expected_gain"] < 0.45:
        stop_condition = "ABSTAIN"
    elif "reserve" in normalize(candidate.get("note", "")) or "dormant" in normalize(candidate.get("note", "")):
        stop_condition = "REPAIR"

    return {
        "mode": "promote",
        "candidate": candidate,
        "active_shortcuts": lookup_shortcuts(registries, MODE_SHORTCUTS["promote"]),
        "stop_condition": stop_condition,
        "witness_basis": [
            registries["weave_registry"]["authority_surface"],
            registries["body_registry"]["authority_surface"],
        ],
    }
