from __future__ import annotations

import hashlib
import heapq
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from self_actualize.runtime.hemisphere_brain_support import (
    COMMISSURE_LEDGER_PATH,
    KNOWLEDGE_FABRIC_SHORTCUTS_PATH,
    MATH_HUB_ID,
    MYTH_HUB_ID,
    PT2_CARRIER_REGISTRY_PATH,
    PT2_CARRIER_TRANSFORM_PATH,
    PT2_FIELD_REGISTRY_PATH,
    PT2_LENS_PROFILES_PATH,
    PT2_METRO_INTERLOCKS_PATH,
    PT2_METRO_STATIONS_PATH,
    PT2_METRO_SYSTEMS_PATH,
    PT2_PROJECTION_SPACE_PATH,
    PT2_SHORTCUT_REGISTRY_PATH,
    PT2_SYSTEM_CROSSWALK_PATH,
    PT2_ZPOINT_REGISTRY_PATH,
    PRIMARY_HF_ROUTE_KEYS,
    WEIGHT_EXCHANGE_PATH,
    ZPOINT_TUNNELS_PATH,
    load_json,
    normalize_path,
    slugify,
    utc_now,
)


MATH_LEANING_FAMILIES = {
    "higher-dimensional-geometry",
    "transport-and-runtime",
    "civilization-and-governance",
}
MYTH_LEANING_FAMILIES = {
    "mythic-sign-systems",
    "identity-and-instruction",
    "void-and-collapse",
}
MATH_SYSTEM_DEFAULTS = {
    "higher-dimensional-geometry": "HDSCTMetro",
    "transport-and-runtime": "GrandCentral",
    "civilization-and-governance": "CoreMetro",
    "manuscript-architecture": "BrainStem64",
    "general-corpus": "Plexus256",
    "live-orchestration": "L3Neural",
    "mythic-sign-systems": "Mycelial4D",
    "identity-and-instruction": "L2DeepEmergence",
    "void-and-collapse": "DeepRootMetroStack",
    "helical-recursion-engine": "AppendixOnlyMetro",
}
MYTH_SYSTEM_DEFAULTS = {
    "mythic-sign-systems": "Mycelial4D",
    "identity-and-instruction": "EmergentSupermap",
    "void-and-collapse": "DeepRootMetroStack",
    "helical-recursion-engine": "AppendixOnlyMetro",
    "manuscript-architecture": "L2DeepEmergence",
    "general-corpus": "CrossCorpusMycelial",
    "live-orchestration": "AthenaFleetMetro",
    "transport-and-runtime": "GrandCentral",
    "higher-dimensional-geometry": "HDSCTMetro",
    "civilization-and-governance": "CoreMetro",
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def unique_strings(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def parse_iso_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def load_list_registry(path: Path, list_key: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = load_json(path)
    return list(payload.get(list_key, []))


def load_dual_route_runtime() -> dict[str, Any]:
    systems = load_list_registry(PT2_METRO_SYSTEMS_PATH, "systems")
    interlocks = load_list_registry(PT2_METRO_INTERLOCKS_PATH, "interlocks")
    carriers = load_list_registry(PT2_CARRIER_REGISTRY_PATH, "carriers")
    profiles = load_list_registry(PT2_LENS_PROFILES_PATH, "profiles")
    pt2_shortcuts = load_list_registry(PT2_SHORTCUT_REGISTRY_PATH, "shortcuts")
    kf_shortcuts = load_list_registry(KNOWLEDGE_FABRIC_SHORTCUTS_PATH, "shortcuts")
    return {
        "systems": systems,
        "system_map": {item["system_id"]: item for item in systems},
        "stations": load_list_registry(PT2_METRO_STATIONS_PATH, "stations"),
        "interlocks": interlocks,
        "carrier_map": {item["carrier_id"]: item for item in carriers},
        "transforms": load_list_registry(PT2_CARRIER_TRANSFORM_PATH, "transforms"),
        "profile_map": {item["lens_id"]: item for item in profiles},
        "fields": load_list_registry(PT2_FIELD_REGISTRY_PATH, "fields"),
        "zpoints": load_list_registry(PT2_ZPOINT_REGISTRY_PATH, "zpoints"),
        "spaces": load_list_registry(PT2_PROJECTION_SPACE_PATH, "spaces"),
        "pt2_shortcuts": {item["shortcut_id"]: item for item in pt2_shortcuts},
        "kf_shortcuts": {item["shortcut_id"]: item for item in kf_shortcuts},
        "crosswalk_edges": load_list_registry(PT2_SYSTEM_CROSSWALK_PATH, "edges"),
        "commissures": load_list_registry(COMMISSURE_LEDGER_PATH, "commissures"),
        "weight_exchange": load_list_registry(WEIGHT_EXCHANGE_PATH, "routes"),
        "zpoint_tunnels": load_list_registry(ZPOINT_TUNNELS_PATH, "tunnels"),
    }


def root_station_for_record(
    record: dict[str, Any],
    station_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    top_level = record.get("top_level") or ""
    if top_level in station_map:
        return station_map[top_level]
    normalized = normalize_path(record.get("relative_path", "")).lower()
    for candidate in ("self_actualize", "NERVOUS_SYSTEM", "Athena FLEET", "MATH", "Voynich"):
        station = station_map.get(candidate)
        if station and candidate.lower().replace(" ", "/") in normalized:
            return station
    return station_map.get("self_actualize") or next(iter(station_map.values()), {})


def origin_system_from_station(station: dict[str, Any]) -> str:
    hemisphere = station.get("hemisphere", "bilateral")
    if hemisphere == "left":
        return "CoreMetro"
    if hemisphere == "right":
        return "Mycelial4D"
    return "GrandCentral"


def route_role_for_side(record: dict[str, Any], hemisphere: str) -> str:
    return "primary" if record["primary_hemisphere"] == hemisphere else "secondary"


def route_mode_for_side(record: dict[str, Any], hemisphere: str) -> str:
    if record["primary_hemisphere"] == hemisphere:
        return "direct_native"
    if record.get("bridge_intensity", 0.0) >= 0.45:
        return "commissure_direct"
    return "cross_hemisphere_transfer"


def grand_central_exchange_for_route(hemisphere: str, route_mode: str) -> str:
    if route_mode == "commissure_direct":
        return "commissure"
    return "GCL" if hemisphere == "MATH" else "GCR"


def target_system_for_route(record: dict[str, Any], hemisphere: str, route_role: str) -> str:
    if not record.get("text_extractable"):
        return "GrandCentral" if route_role == "primary" else "CrossCorpusMycelial"
    if record.get("appendix_only_mode") or "AppQ" in set(record.get("appendix_support", [])):
        return "AppendixOnlyMetro"
    if (
        not record.get("tesseract_header")
        and {"AppM", "AppQ"} & set(record.get("appendix_support", []))
    ):
        return "AppendixOnlyMetro"
    if route_role == "secondary" and record.get("bridge_intensity", 0.0) >= 0.65:
        return "GrandCentral"
    if record.get("top_level") == "Athena FLEET" and hemisphere == "MYTH":
        return "AthenaFleetMetro"
    if (
        record.get("family") in {"void-and-collapse", "helical-recursion-engine"}
        and record.get("tract") == "replay"
    ):
        return "DeepRootMetroStack"
    defaults = MATH_SYSTEM_DEFAULTS if hemisphere == "MATH" else MYTH_SYSTEM_DEFAULTS
    return defaults.get(record.get("family", "general-corpus"), "GrandCentral")


def interlock_edge_cost(interlock: dict[str, Any]) -> float:
    cost = 10.0 - float(interlock.get("dispatch_score", 7.0))
    if interlock.get("proof_state") != "OK":
        cost += 0.35
    note = interlock.get("note", "").lower()
    if "historical" in note or "trading bot" in note:
        cost += 0.25
    return round(cost, 6)


def build_interlock_graph(interlocks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    graph: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for interlock in interlocks:
        graph[interlock["source_system"]].append(
            {"next_system": interlock["target_system"], "interlock": interlock, "reversed": False, "cost": interlock_edge_cost(interlock)}
        )
        graph[interlock["target_system"]].append(
            {"next_system": interlock["source_system"], "interlock": interlock, "reversed": True, "cost": interlock_edge_cost(interlock)}
        )
    return graph


def pathfind_system_path(origin_system: str, target_system: str, interlocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if origin_system == target_system:
        return []
    graph = build_interlock_graph(interlocks)
    heap: list[tuple[float, int, str, str, list[dict[str, Any]]]] = [(0.0, 0, "", origin_system, [])]
    best: dict[str, tuple[float, int, str]] = {}
    while heap:
        cost, hops, signature, system_id, path = heapq.heappop(heap)
        rank = (round(cost, 6), hops, signature)
        if system_id in best and rank > best[system_id]:
            continue
        best[system_id] = rank
        if system_id == target_system:
            return path
        for edge in graph.get(system_id, []):
            next_signature = f"{signature},{edge['interlock']['interlock_id']}{'R' if edge['reversed'] else 'F'}" if signature else f"{edge['interlock']['interlock_id']}{'R' if edge['reversed'] else 'F'}"
            next_rank = (round(cost + edge["cost"], 6), hops + 1, next_signature)
            if edge["next_system"] in best and next_rank >= best[edge["next_system"]]:
                continue
            heapq.heappush(heap, (next_rank[0], next_rank[1], next_rank[2], edge["next_system"], [*path, edge]))
    return []


def extract_station_path(interlock_path: list[dict[str, Any]], target_system: str, runtime: dict[str, Any]) -> list[str]:
    if not interlock_path:
        system = runtime["system_map"].get(target_system, {})
        return list(system.get("entry_station_ids") or system.get("exit_station_ids") or ["ST-T10"])
    stations: list[str] = []
    for edge in interlock_path:
        interlock = edge["interlock"]
        if edge["reversed"]:
            sequence = [interlock["target_station"], *reversed(interlock.get("route_via", [])), interlock["source_station"]]
        else:
            sequence = [interlock["source_station"], *interlock.get("route_via", []), interlock["target_station"]]
        for station_id in sequence:
            if not stations or stations[-1] != station_id:
                stations.append(station_id)
    return stations


def seed_lens_members(record: dict[str, Any], hemisphere: str, target_system: str, station_path: list[str]) -> list[str]:
    members: list[str] = []
    family = record.get("family", "general-corpus")
    tract = record.get("tract", "address")
    appendix = set(record.get("appendix_support", []))
    if hemisphere == "MATH" or tract == "address" or family in MATH_LEANING_FAMILIES:
        members.append("S")
    if hemisphere == "MYTH" or tract == "relation" or family in MYTH_LEANING_FAMILIES:
        members.append("F")
    if record.get("bridge_intensity", 0.0) >= 0.45 or "ST-GCZ" in station_path or {"AppI", "AppQ"} & appendix or target_system in {"GrandCentral", "DeepRootMetroStack", "HDSCTMetro", "CrossCorpusMycelial"}:
        members.append("C")
    if tract == "replay" or "ST-GCP" in station_path or "AppM" in appendix or record.get("duplicate_count", 0) > 0 or family in {"void-and-collapse", "helical-recursion-engine", "transport-and-runtime"}:
        members.append("R")
    ordered = [member for member in "SFCR" if member in members]
    return ordered or (["S"] if hemisphere == "MATH" else ["F"])


def compute_lens_vector(record: dict[str, Any], hemisphere: str, route_role: str, target_system: str, seed_members: list[str], runtime: dict[str, Any]) -> dict[str, float]:
    seed_set = set(seed_members)
    vector: dict[str, float] = {}
    for lens_id, profile in runtime["profile_map"].items():
        members = set(profile.get("members", []))
        overlap = len(seed_set & members)
        score = 0.48 * (overlap / max(len(members), 1)) + 0.22 * (overlap / max(len(seed_set), 1))
        if route_role == "primary" and hemisphere == "MATH" and "S" in members:
            score += 0.08
        if route_role == "primary" and hemisphere == "MYTH" and "F" in members:
            score += 0.08
        if record.get("bridge_intensity", 0.0) >= 0.45 and "C" in members:
            score += 0.06
        if record.get("tract") == "replay" and "R" in members:
            score += 0.06
        if target_system in {"DeepRootMetroStack", "HDSCTMetro"} and "C" in members:
            score += 0.06
        if target_system == "GrandCentral" and "R" in members:
            score += 0.05
        vector[lens_id] = round(clamp(score, 0.0, 1.0), 3)
    return vector


def base4(value: int, digits: int = 4) -> str:
    if value <= 0:
        return "0".rjust(digits, "0")
    chars: list[str] = []
    current = value
    while current:
        chars.append(str(current % 4))
        current //= 4
    return "".join(reversed(chars)).rjust(digits, "0")


def stable_index(text: str, modulo: int) -> int:
    return int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16) % modulo


def field_vector_for_route(dominant_lens: str, target_system: str, rail3: str, proof_state: str) -> dict[str, float]:
    return {
        "aether_density": round(clamp(0.46 + (0.20 if "C" in dominant_lens else 0.0) + (0.05 if "F" in dominant_lens else 0.0) + (0.09 if target_system == "HDSCTMetro" else 0.0), 0.0, 1.0), 3),
        "zero_proximity": round(clamp(0.28 + (0.18 if "R" in dominant_lens else 0.0) + (0.08 if target_system in {"DeepRootMetroStack", "GrandCentral"} else 0.0), 0.0, 1.0), 3),
        "tunnel_cost": round(clamp(0.66 - (0.08 if "C" in dominant_lens else 0.0) - (0.06 if "R" in dominant_lens else 0.0) - (0.06 if target_system in {"DeepRootMetroStack", "GrandCentral"} else 0.0), 0.0, 1.0), 3),
        "rail_hardness": round(clamp({"Su": 0.57, "Me": 0.66, "Sa": 0.81}[rail3] + (0.08 if "S" in dominant_lens else 0.0), 0.0, 1.0), 3),
        "resonance_pressure": round(clamp(0.42 + (0.18 if "F" in dominant_lens else 0.0) + (0.06 if "C" in dominant_lens else 0.0), 0.0, 1.0), 3),
        "repair_gain": round(clamp(0.39 + (0.16 if "R" in dominant_lens else 0.0) + (0.05 if "S" in dominant_lens else 0.0) + (0.06 if proof_state == "OK" else 0.0), 0.0, 1.0), 3),
    }


def field_id_from_vector(field_vector: dict[str, float]) -> str:
    if field_vector["aether_density"] >= 0.78 and field_vector["tunnel_cost"] <= 0.55:
        return "Aether"
    if field_vector["zero_proximity"] >= 0.61 and field_vector["tunnel_cost"] <= 0.58:
        return "TunnelGeodesic"
    if field_vector["aether_density"] >= 0.65 and field_vector["resonance_pressure"] >= 0.56:
        return "CloudManifold"
    if field_vector["resonance_pressure"] >= 0.52:
        return "ResonancePressureBand"
    if field_vector["rail_hardness"] >= 0.62:
        return "RailHardeningBand"
    return "Zero"


def geodesic_mode_from_vector(field_vector: dict[str, float]) -> str:
    if field_vector["zero_proximity"] >= 0.64:
        return "z-point tunnel"
    if field_vector["aether_density"] >= 0.72:
        return "aether geodesic"
    return "rail transit"


def zpoint_id_for_route(
    record: dict[str, Any],
    route_role: str,
    target_system: str,
    field_id: str,
) -> str:
    if field_id == "Aether":
        return "Z5"
    if target_system == "HDSCTMetro":
        return "Z3"
    if target_system in {"AthenaFleetMetro", "CrossCorpusMycelial"}:
        return "Z4"
    if (
        record.get("tract") == "replay"
        or record.get("family") in {"void-and-collapse", "helical-recursion-engine"}
    ):
        return "Z1"
    if route_role == "secondary" and record.get("bridge_intensity", 0.0) >= 0.70:
        return "Z2"
    return "Z0"


def route_proof_state(record: dict[str, Any], interlock_path: list[dict[str, Any]], route_mode: str) -> str:
    if record.get("truth_state") == "FAIL":
        return "FAIL"
    if record.get("truth_state") == "AMBIG":
        return "AMBIG"
    if not record.get("text_extractable"):
        return "AMBIG"
    if any("historical" in edge["interlock"].get("note", "").lower() or "trading bot" in edge["interlock"].get("note", "").lower() for edge in interlock_path):
        return "AMBIG"
    if record.get("confidence", 0.0) < 0.55:
        return "AMBIG"
    if record.get("truth_state") == "NEAR":
        return "NEAR"
    if route_mode == "cross_hemisphere_transfer" or any(edge["interlock"].get("proof_state") != "OK" for edge in interlock_path):
        return "NEAR"
    return "OK" if record.get("confidence", 0.0) >= 0.72 else "NEAR"


def dynamic_weight_vector(record: dict[str, Any], route_role: str, route_hop_count: int) -> dict[str, float]:
    modified_at = parse_iso_timestamp(record.get("modified_at", ""))
    age_days = (datetime.now(timezone.utc) - modified_at).total_seconds() / 86400.0 if modified_at else 365.0
    freshness = round(clamp(1.0 - age_days / 365.0, 0.35, 1.0), 3)
    return {
        "salience": round(float(record.get("salience", 0.0)), 6),
        "proof": round(float(record.get("confidence", 0.0)), 3),
        "freshness": freshness,
        "cost": round(clamp(1.0 - route_hop_count / 6.0, 0.35, 1.0), 3),
        "continuity": 1.0 if route_role == "primary" else round(float(record.get("bridge_intensity", 0.0)), 3),
        "confidence": round(float(record.get("confidence", 0.0)), 3),
        "replay_value": 1.0 if record.get("tract") == "replay" else round(float(record.get("route_quality", 1.0)), 3),
    }


def transform_chain_for_route(
    primary_carrier: str,
    dominant_lens: str,
    target_system: str,
    field_id: str,
    runtime: dict[str, Any],
) -> list[str]:
    candidates: list[str] = []
    for transform in runtime["transforms"]:
        if primary_carrier in transform.get("source_carriers", []):
            candidates.extend(transform.get("target_carriers", []))
    candidates.extend(
        runtime["carrier_map"].get(primary_carrier, {}).get("transform_neighbors", [])
    )
    if "R" in dominant_lens:
        candidates.append("Fractal")
    if "C" in dominant_lens or field_id in {"Aether", "CloudManifold", "TunnelGeodesic"}:
        candidates.extend(["Cloud", "Aether"])
    if target_system in {"Mycelial4D", "CrossCorpusMycelial"}:
        candidates.append("Mycelium")
    if target_system in {"CoreMetro", "GrandCentral"}:
        candidates.append("Nervous")
    return unique_strings(candidates)[:3]


def supported_spaces_for_route(
    preferred_space: str,
    route_role: str,
    dominant_lens: str,
    field_id: str,
    runtime: dict[str, Any],
) -> list[str]:
    candidates = ["Transit3D", "Carrier3D", "Lens3D"]
    if route_role == "primary":
        candidates.append("Organism3D")
    if field_id in {"Aether", "CloudManifold", "TunnelGeodesic"} or "C" in dominant_lens:
        candidates.append("Field3D")
    allowed = {item["space_id"] for item in runtime["spaces"]}
    ordered = [space for space in unique_strings([preferred_space, *candidates]) if space in allowed]
    return ordered or [preferred_space]


def preferred_space_for_route(
    route_role: str,
    dominant_lens: str,
    field_id: str,
    geodesic_mode: str,
    runtime: dict[str, Any],
) -> str:
    if field_id in {"Aether", "CloudManifold", "TunnelGeodesic"} or geodesic_mode != "rail transit":
        candidate = "Field3D"
    elif route_role == "primary":
        candidate = "Organism3D"
    elif len(dominant_lens) >= 2:
        candidate = "Lens3D"
    else:
        candidate = "Transit3D"
    allowed = {item["space_id"] for item in runtime["spaces"]}
    return candidate if candidate in allowed else "Transit3D"


def pt2_shortcut_for_route(
    profile: dict[str, Any],
    route_role: str,
    dominant_lens: str,
    target_system: str,
    geodesic_mode: str,
    runtime: dict[str, Any],
) -> str:
    candidates: list[str] = []
    if geodesic_mode == "z-point tunnel":
        candidates.append("SCPT2-10")
    if target_system in {"HDSCTMetro", "DeepRootMetroStack"}:
        candidates.append("SCPT2-13")
    if route_role == "secondary":
        candidates.append("SCPT2-09")
    candidates.extend(profile.get("shortcut_chain", []))
    if "R" in dominant_lens:
        candidates.append("SCPT2-06")
    if "C" in dominant_lens:
        candidates.append("SCPT2-05")
    if "F" in dominant_lens:
        candidates.append("SCPT2-04")
    candidates.append("SCPT2-01")
    for shortcut_id in unique_strings(candidates):
        if shortcut_id in runtime["pt2_shortcuts"]:
            return shortcut_id
    return next(iter(runtime["pt2_shortcuts"]), "")


def knowledge_fabric_shortcut_for_route(
    record: dict[str, Any],
    route_role: str,
    dominant_lens: str,
    runtime: dict[str, Any],
) -> str:
    candidates: list[str] = []
    if not record.get("text_extractable"):
        candidates.append("KF-S05")
    if route_role == "secondary":
        candidates.append("KF-S03")
    if record.get("tract") == "replay" or "R" in dominant_lens:
        candidates.append("KF-S06")
    if record.get("primary_hemisphere") == "MYTH" and route_role == "primary":
        candidates.append("KF-S04")
    candidates.append("KF-S01")
    for shortcut_id in unique_strings(candidates):
        if shortcut_id in runtime["kf_shortcuts"]:
            return shortcut_id
    return next(iter(runtime["kf_shortcuts"]), "")


def route_packet_for_side(record: dict[str, Any], hemisphere: str, station_map: dict[str, dict[str, Any]], runtime: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, bool]]:
    route_role = route_role_for_side(record, hemisphere)
    route_mode = route_mode_for_side(record, hemisphere)
    grand_central_exchange = grand_central_exchange_for_route(hemisphere, route_mode)
    root_station = root_station_for_record(record, station_map)
    origin_system = origin_system_from_station(root_station)
    target_system = target_system_for_route(record, hemisphere, route_role)
    interlock_path = pathfind_system_path(origin_system, target_system, runtime["interlocks"])
    station_path = extract_station_path(interlock_path, target_system, runtime)
    seed_members = seed_lens_members(record, hemisphere, target_system, station_path)
    lens_weight_vector = compute_lens_vector(record, hemisphere, route_role, target_system, seed_members, runtime)
    ranked = sorted(lens_weight_vector.items(), key=lambda item: (-item[1], item[0]))
    dominant_lens = ranked[0][0]
    secondary_lens = ranked[1][0] if len(ranked) > 1 else ranked[0][0]
    profile = runtime["profile_map"].get(dominant_lens, {})
    rail3 = (profile.get("preferred_rails") or ["Sa" if hemisphere == "MATH" else "Su"])[0]
    proof_state = route_proof_state(record, interlock_path, route_mode)
    field_vector = field_vector_for_route(dominant_lens, target_system, rail3, proof_state)
    field_id = field_id_from_vector(field_vector)
    geodesic_mode = geodesic_mode_from_vector(field_vector)
    dynamic_weights = dynamic_weight_vector(record, route_role, len(interlock_path))
    primary_carrier = (profile.get("preferred_carriers") or ["Square" if hemisphere == "MATH" else "Flower"])[0]
    transform_chain = transform_chain_for_route(
        primary_carrier=primary_carrier,
        dominant_lens=dominant_lens,
        target_system=target_system,
        field_id=field_id,
        runtime=runtime,
    )
    preferred_space = preferred_space_for_route(
        route_role=route_role,
        dominant_lens=dominant_lens,
        field_id=field_id,
        geodesic_mode=geodesic_mode,
        runtime=runtime,
    )
    supported_spaces = supported_spaces_for_route(
        preferred_space=preferred_space,
        route_role=route_role,
        dominant_lens=dominant_lens,
        field_id=field_id,
        runtime=runtime,
    )
    route_id = f"RTE-{record['record_id']}-{hemisphere}"
    route_signature = f"{record['record_id']}:{hemisphere}"
    pt2_shortcut_id = pt2_shortcut_for_route(
        profile=profile,
        route_role=route_role,
        dominant_lens=dominant_lens,
        target_system=target_system,
        geodesic_mode=geodesic_mode,
        runtime=runtime,
    )
    knowledge_fabric_shortcut_id = knowledge_fabric_shortcut_for_route(
        record=record,
        route_role=route_role,
        dominant_lens=dominant_lens,
        runtime=runtime,
    )
    zpoint_id = zpoint_id_for_route(record, route_role, target_system, field_id)
    route_id = f"RTE-{record['record_id']}-{hemisphere}"
    route_packet = {
        "route_id": route_id,
        "record_id": record["record_id"],
        "hemisphere": hemisphere,
        "route_role": route_role,
        "route_mode": route_mode,
        "hub_id": MATH_HUB_ID if hemisphere == "MATH" else MYTH_HUB_ID,
        "grand_central_exchange": grand_central_exchange,
        "chapter_station": record.get("chapter_station", ""),
        "local_addr": record.get("local_addr", ""),
        "global_addr": record.get("global_addr", ""),
        "tesseract_header": record.get("tesseract_header", ""),
        "truth_state": record.get("truth_state", ""),
        "root_station_address": root_station.get("station_address", ""),
        "origin_system": origin_system,
        "target_system": target_system,
        "station_path": station_path,
        "interlock_ids": [edge["interlock"]["interlock_id"] for edge in interlock_path],
        "return_path": list(runtime["system_map"].get(target_system, {}).get("default_return_path", [])),
        "family": record.get("family"),
        "basis_anchor_ids": list(record.get("basis_anchor_ids", [])),
        "tract": record.get("tract"),
        "metro_line_ids": [f"L1-{hemisphere}", f"L2-FAMILY-{slugify(record.get('family', 'general-corpus'))}", f"L2-ANCHOR-{(record.get('basis_anchor_ids') or ['DN00'])[0]}", f"L3-TRACT-{record.get('tract', 'address').upper()}", f"L3-CORRIDOR-{slugify(record.get('family', 'general-corpus'))}-{(record.get('basis_anchor_ids') or ['DN00'])[0]}-{record.get('tract', 'address').upper()}", f"L4-SUPERMESH-{record['record_id']}"],
        "rail3": rail3,
        "appendix_support": list(record.get("appendix_support", [])),
        "appendix_support_sources": record.get("appendix_support_sources", {}),
        "primary_carrier": primary_carrier,
        "transform_chain": transform_chain,
        "dominant_lens_system": dominant_lens,
        "secondary_lens_system": secondary_lens,
        "lens_weight_vector": lens_weight_vector,
        "liminal_vector": {"omega": round(float(record.get("route_quality", 1.0)), 3), "integration": round(float(record.get("bridge_intensity", 0.0)), 3), "coherence": round(float(record.get("confidence", 0.0)), 3), "function": dynamic_weights["cost"]},
        "field_id": field_id,
        "zpoint_id": zpoint_id,
        "aether_point": field_vector,
        "geodesic_mode": geodesic_mode,
        "preferred_space": preferred_space,
        "supported_spaces": supported_spaces,
        "pt2_shortcut_id": pt2_shortcut_id,
        "knowledge_fabric_shortcut_id": knowledge_fabric_shortcut_id,
        "hubs_seq": list(record.get("hubs_seq", [])),
        "tunnel_plan": record.get("tunnel_plan", {}),
        "hcrl_pass": record.get("hcrl_pass", {}),
        "obligations": list(record.get("obligations", [])),
        "drop_log": list(record.get("drop_log", [])),
        "overlay_annotations": record.get("overlay_annotations", {}),
        "truth_intent": record.get("truth_intent", {}),
        "route_plan_id": record.get("route_plan_id", ""),
        "graph_edge_ids": list(record.get("graph_edge_ids", [])),
        "primary_hubs_text": record.get("primary_hubs_text", ""),
        "tunnel_text": record.get("tunnel_text", ""),
        "truth_state_text": record.get("truth_state_text", ""),
        "hcrl_text": record.get("hcrl_text", {}),
        "addr4": f"{record['record_id']}<{base4(stable_index(route_signature, 256))}>",
        "face6": "Void" if grand_central_exchange == "commissure" else ("Aether" if "C" in dominant_lens and target_system in {"DeepRootMetroStack", "HDSCTMetro", "GrandCentral"} else ("Water" if record.get("tract") == "replay" else ("Air" if record.get("tract") == "relation" else ("Fire" if record.get("tract") == "chamber" else "Earth")))),
        "arc7": f"Arc{stable_index(route_id, 7) + 1}",
        "depth5": "D0",
        "dynamic_weights": dynamic_weights,
        "replay_policy": "close through GCZ and replay closure" if geodesic_mode == "z-point tunnel" else ("close through GCP before promotion" if record.get("tract") == "replay" else "preserve docs gate status and proof state at writeback"),
        "proof_state": proof_state,
        "docs_gate_status": record.get("docs_gate_status", "UNKNOWN"),
    }
    edge_payload = {
        "edge_id": f"DE-{record['record_id']}-{hemisphere}",
        "record_id": record["record_id"],
        "relative_path": record.get("relative_path", ""),
        "source_id": record["record_id"],
        "target_hub_id": route_packet["hub_id"],
        "hemisphere": hemisphere,
        "route_role": route_role,
        "route_mode": route_mode,
        "weight": record["math_weight"] if hemisphere == "MATH" else record["myth_weight"],
        "global_addr": record.get("global_addr", ""),
        "local_addr": record.get("local_addr", ""),
        "truth_state": record.get("truth_state", ""),
        "grand_central_exchange": grand_central_exchange,
        "origin_system": origin_system,
        "target_system": target_system,
        "proof_state": proof_state,
        "docs_gate_status": record.get("docs_gate_status", "UNKNOWN"),
    }
    coverage = {
        "hemisphere_edge": bool(route_packet["hub_id"]),
        "grand_central": bool(route_packet["grand_central_exchange"]),
        "metro": bool(route_packet["target_system"]),
        "interlock": bool(route_packet["station_path"]),
        "carrier": bool(route_packet["primary_carrier"]),
        "rail": bool(route_packet["rail3"]),
        "lens": bool(route_packet["dominant_lens_system"]),
        "liminal": bool(route_packet["liminal_vector"]),
        "field": bool(route_packet["field_id"]),
        "zpoint": bool(route_packet["zpoint_id"]),
        "apoint": bool(route_packet["aether_point"]),
        "projection_space": bool(route_packet["preferred_space"]),
        "knowledge_fabric": bool(route_packet["knowledge_fabric_shortcut_id"]),
        "basis_anchor": bool(route_packet["basis_anchor_ids"]),
        "family": bool(route_packet["family"]),
        "holo_coordinate": bool(route_packet["addr4"] and route_packet["face6"] and route_packet["arc7"] and route_packet["depth5"]),
        "tesseract": bool(route_packet["global_addr"] and route_packet["tesseract_header"]),
    }
    return route_packet, edge_payload, coverage


def build_dual_route_payloads(records: list[dict[str, Any]], station_map: dict[str, dict[str, Any]], docs_gate_status: str) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    runtime = load_dual_route_runtime()
    updated_records: list[dict[str, Any]] = []
    route_entries: list[dict[str, Any]] = []
    edge_entries: list[dict[str, Any]] = []
    coverage_rows: list[dict[str, Any]] = []
    primary_targets: Counter[str] = Counter()
    secondary_targets: Counter[str] = Counter()
    for record in records:
        route_packets: dict[str, dict[str, Any]] = {}
        coverage_map: dict[str, dict[str, bool]] = {}
        direct_edge_ids: list[str] = []
        for hemisphere in ("MATH", "MYTH"):
            route_packet, edge_payload, coverage = route_packet_for_side(record, hemisphere, station_map, runtime)
            route_packets[hemisphere] = route_packet
            coverage_map[hemisphere] = coverage
            direct_edge_ids.append(edge_payload["edge_id"])
            route_entries.append(route_packet)
            edge_entries.append(edge_payload)
            if route_packet["route_role"] == "primary":
                primary_targets[route_packet["target_system"]] += 1
            else:
                secondary_targets[route_packet["target_system"]] += 1
        route_coverage = {
            "record_id": record["record_id"],
            "relative_path": record.get("relative_path", ""),
            "MATH": coverage_map["MATH"],
            "MYTH": coverage_map["MYTH"],
            "complete": all(all(item.values()) for item in coverage_map.values()),
        }
        coverage_rows.append(route_coverage)
        updated = dict(record)
        updated["hemisphere_routes"] = route_packets
        updated["direct_edge_ids"] = direct_edge_ids
        updated["route_coverage"] = route_coverage
        updated_records.append(updated)
    dual_route_registry = {"generated_at": utc_now(), "docs_gate_status": docs_gate_status, "route_count": len(route_entries), "routes": route_entries}
    direct_edge_registry = {"generated_at": utc_now(), "docs_gate_status": docs_gate_status, "edge_count": len(edge_entries), "edges": edge_entries}
    route_coverage_registry = {"generated_at": utc_now(), "docs_gate_status": docs_gate_status, "record_count": len(coverage_rows), "complete_count": sum(1 for row in coverage_rows if row["complete"]), "records": coverage_rows}
    route_manifest = {"generated_at": utc_now(), "docs_gate_status": docs_gate_status, "counts": {"records": len(updated_records), "route_packets": len(route_entries), "direct_edges": len(edge_entries), "coverage_rows": len(coverage_rows)}, "primary_target_distribution": dict(sorted(primary_targets.items())), "secondary_target_distribution": dict(sorted(secondary_targets.items())), "routing_systems": PRIMARY_HF_ROUTE_KEYS}
    return updated_records, dual_route_registry, direct_edge_registry, route_coverage_registry, route_manifest
