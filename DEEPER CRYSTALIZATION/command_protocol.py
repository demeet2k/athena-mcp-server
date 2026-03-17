#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import os
import socket
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
RUNTIME_ROOT = ACTIVE_ROOT / "06_RUNTIME"
COMMAND_ROOT = WORKSPACE_ROOT / "GLOBAL COMMAND" / "ATHENA"
COMMAND_LAYER_ROOT = ACTIVE_ROOT / "19_COMMAND_PROTOCOL"
COMMAND_MANIFEST_PATH = RUNTIME_ROOT / "21_command_protocol_manifest.json"
LIVE_DOCS_GATE_PATH = ACTIVE_ROOT / "00_RECEIPTS" / "00_live_docs_gate_status.md"
WITNESS_HIERARCHY_JSON = WORKSPACE_ROOT / "self_actualize" / "witness_hierarchy.json"
WITNESS_HIERARCHY_MD = (
    WORKSPACE_ROOT
    / "self_actualize"
    / "mycelium_brain"
    / "GLOBAL_EMERGENT_GUILD_HALL"
    / "07_CANONICAL_WITNESS_HIERARCHY.md"
)
RUNNER_MANIFEST_PATH = RUNTIME_ROOT / "19_super_cycle_57_runner_manifest.json"
FULL_STACK_MANIFEST_PATH = RUNTIME_ROOT / "12_full_stack_manifest.json"
ACTIVE_README_PATH = ACTIVE_ROOT / "README.md"
BOARD_THREAD_ROOT = (
    ACTIVE_ROOT
    / "07_FULL_PROJECT_INTEGRATION_256"
    / "06_REALTIME_BOARD"
    / "02_ACTIVE_THREADS"
    / "global_command"
)
BOARD_CHANGE_FEED_ROOT = (
    ACTIVE_ROOT
    / "07_FULL_PROJECT_INTEGRATION_256"
    / "06_REALTIME_BOARD"
    / "04_CHANGE_FEED"
)
SECTIONS_DIR = WORKSPACE_ROOT / "self_actualize" / "manuscript_sections"
SUPPLEMENTS_OUTPUT_PATH = WORKSPACE_ROOT / "self_actualize" / "VOID_MANUSCRIPT_SUPPLEMENTS.md"

COMMAND_SPEC_MD = COMMAND_LAYER_ROOT / "00_command_protocol_v1.md"
PACKET_SCHEMA_JSON = COMMAND_LAYER_ROOT / "01_command_packet_schema.json"
ANT_CLASSES_MD = COMMAND_LAYER_ROOT / "02_ant_classes.md"
COORDINATE_SCHEMA_MD = COMMAND_LAYER_ROOT / "03_liminal_coordinate_schema.md"
CAPILLARY_LAW_MD = COMMAND_LAYER_ROOT / "04_capillary_weight_law.md"
ROUTE_LEDGER_JSON = COMMAND_LAYER_ROOT / "05_route_ledger.json"
CAPILLARY_REGISTRY_JSON = COMMAND_LAYER_ROOT / "06_capillary_registry.json"
MEMBRANE_STATUS_JSON = COMMAND_LAYER_ROOT / "07_membrane_status.json"
PACKET_LOG_JSON = COMMAND_LAYER_ROOT / "08_command_packets.json"
CLAIM_REGISTRY_JSON = COMMAND_LAYER_ROOT / "09_claim_registry.json"
WATCHER_HEALTH_JSON = COMMAND_LAYER_ROOT / "10_watcher_health.json"
FIXTURES_DIR = COMMAND_LAYER_ROOT / "11_fixtures"
READABLE_REGISTRY_MD = COMMAND_LAYER_ROOT / "12_command_packet_and_capillary_registry.md"
THREAD_STATUS_MD = BOARD_THREAD_ROOT / "COMMAND_PROTOCOL_STATUS.md"
THREAD_EVENT_FEED_MD = BOARD_THREAD_ROOT / "COMMAND_EVENT_FEED.md"
BOARD_EVENT_FEED_MD = BOARD_CHANGE_FEED_ROOT / "02_COMMAND_PROTOCOL_EVENTS.md"
COMMAND_SUPPLEMENT_PATH = SECTIONS_DIR / "027_command_protocol_v1.md"
COMMAND_REGISTRY_SUPPLEMENT_PATH = SECTIONS_DIR / "028_command_packet_and_capillary_law_registry.md"

TRUTH_STATUS = "NEAR-derived"
COMMAND_STATUS = "command-protocol-v1"
WATCH_BACKEND_NATIVE = "native-watchdog"
WATCH_BACKEND_FALLBACK = "polling-watchdog"
DEFAULT_TTL = 6
DEFAULT_TOPK = 5
DEFAULT_LEASE_MS = 1200
DEFAULT_ROUTE_CLASS = "scout.router.worker.archivist"
DEFAULT_PRIORITY = 0.75
DEFAULT_CONFIDENCE = 0.9
SIGMA_PATH = ["AppA", "AppI", "AppM"]
CONTROL_STACK = ["Q42", "TQ04", "Q50", "Q46", "Q02"]
WATCHDOG_AVAILABLE = importlib.util.find_spec("watchdog") is not None

COORDINATE_DIMENSIONS = [
    "utc_time_fraction",
    "local_earth_rotation_phase",
    "earth_orbital_phase",
    "local_node_anchor",
    "solar_phase",
    "lunar_phase",
    "sidereal_phase",
    "sky_anchor_slot",
    "runtime_node_anchor",
    "queue_pressure",
    "goal_salience_vector",
    "novelty_routing_concentration",
]

EVENT_PACKET_FIELDS = [
    "event_id",
    "parent",
    "source_root",
    "source_path",
    "change_type",
    "tag",
    "goal",
    "priority",
    "confidence",
    "earth_ts",
    "liminal_ts",
    "coord12",
    "ttl",
    "pheromone",
    "state_hash",
    "route_class",
    "claim_state",
    "truth_status",
]

LEDGER_FIELDS = [
    "agent_id",
    "runtime_sequence_id",
    "coordinate_stamp",
    "source_region",
    "action_type",
    "affected_nodes",
    "summary_of_change",
    "reason_for_change",
    "integration_gain",
    "compression_gain",
    "unresolved_followups",
    "linked_quests",
    "linked_agents",
    "confidence",
    "timestamp_internal",
]

CAPILLARY_PARAMS = {
    "retention": 0.92,
    "alpha_usefulness": 0.35,
    "beta_frequency": 0.2,
    "gamma_latency": 0.15,
    "delta_noise": 0.1,
    "weak_threshold": 0.75,
    "vein_threshold": 1.75,
}

ANT_REGISTRY = [
    {
        "ant_id": "CMD.A1.D1.B0001.SCOUT-01",
        "ant_class": "Scout",
        "role_tag": "SCOUT-01",
        "route_specialization": "command-root detection and packetization",
        "output_organ": "runtime",
        "coord_anchor": "GLOBAL_COMMAND.sensor_boundary",
    },
    {
        "ant_id": "CMD.A2.D1.B0010.ROUTER-01",
        "ant_class": "Router",
        "role_tag": "ROUTER-01",
        "route_specialization": "board-thread and change-feed routing",
        "output_organ": "board",
        "coord_anchor": "global_command.thread",
    },
    {
        "ant_id": "CMD.A2.D1.B0011.ROUTER-02",
        "ant_class": "Router",
        "role_tag": "ROUTER-02",
        "route_specialization": "motion, Hall, and Temple routing",
        "output_organ": "hall_temple",
        "coord_anchor": "motion_constitution.bridge",
    },
    {
        "ant_id": "CMD.A3.D1.B0100.WORKER-01",
        "ant_class": "Worker",
        "role_tag": "WORKER-01",
        "route_specialization": "manuscript and docx surfaces",
        "output_organ": "supplement",
        "coord_anchor": "manuscript.command",
    },
    {
        "ant_id": "CMD.A3.D1.B0101.WORKER-02",
        "ant_class": "Worker",
        "role_tag": "WORKER-02",
        "route_specialization": "runtime and board surfaces",
        "output_organ": "runtime",
        "coord_anchor": "runtime.command",
    },
    {
        "ant_id": "CMD.A3.D1.B0110.WORKER-03",
        "ant_class": "Worker",
        "role_tag": "WORKER-03",
        "route_specialization": "math, equations, and algorithm grafts",
        "output_organ": "temple",
        "coord_anchor": "math.command",
    },
    {
        "ant_id": "CMD.A3.D1.B0111.WORKER-04",
        "ant_class": "Worker",
        "role_tag": "WORKER-04",
        "route_specialization": "archive, atlas, and corpus intake surfaces",
        "output_organ": "hall",
        "coord_anchor": "atlas.command",
    },
    {
        "ant_id": "CMD.A4.D1.B1000.ARCHIVIST-01",
        "ant_class": "Archivist",
        "role_tag": "ARCHIVIST-01",
        "route_specialization": "ledger, route, and capillary persistence",
        "output_organ": "runtime",
        "coord_anchor": "ledger.command",
    },
    {
        "ant_id": "CMD.A4.D1.B1001.ARCHIVIST-02",
        "ant_class": "Archivist",
        "role_tag": "ARCHIVIST-02",
        "route_specialization": "board mirror and event feed compression",
        "output_organ": "board",
        "coord_anchor": "change_feed.command",
    },
]


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalized_hash_float(text: str) -> float:
    value = int(stable_hash(text)[:8], 16)
    return round(value / 0xFFFFFFFF, 6)


def live_docs_error() -> str:
    if not LIVE_DOCS_GATE_PATH.exists():
        return "Error: Missing OAuth client file: credentials.json"
    for line in LIVE_DOCS_GATE_PATH.read_text(encoding="utf-8").splitlines():
        if "Missing OAuth client file" in line:
            return line.strip()
    return "Google Docs gate remains blocked."


def watch_backend_name() -> str:
    if os.name == "nt":
        return "windows-native-watch"
    return WATCH_BACKEND_FALLBACK


def local_timezone() -> ZoneInfo:
    try:
        return ZoneInfo("America/Los_Angeles")
    except Exception:
        return ZoneInfo("UTC")


def utc_now_dt() -> datetime:
    return datetime.now(UTC)


def liminal_timestamp(dt: datetime | None = None) -> str:
    dt = dt or utc_now_dt()
    return f"LT-{dt.strftime('%Y%m%d%H%M%S')}.{int(dt.microsecond / 1000):03d}"


def fraction_of_day(dt: datetime) -> float:
    total_seconds = dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1_000_000
    return round(total_seconds / 86400.0, 6)


def fraction_of_year(dt: datetime) -> float:
    start = datetime(dt.year, 1, 1, tzinfo=dt.tzinfo)
    end = datetime(dt.year + 1, 1, 1, tzinfo=dt.tzinfo)
    total = (end - start).total_seconds()
    elapsed = (dt - start).total_seconds()
    return round(elapsed / total, 6)


def lunar_phase_fraction(dt: datetime) -> float:
    reference = datetime(2000, 1, 6, 18, 14, tzinfo=UTC)
    synodic_days = 29.53058867
    phase_days = ((dt - reference).total_seconds() / 86400.0) % synodic_days
    return round(phase_days / synodic_days, 6)


def sidereal_phase_fraction(dt: datetime) -> float:
    sidereal_day_seconds = 86164.0905
    unix_seconds = dt.timestamp()
    return round((unix_seconds % sidereal_day_seconds) / sidereal_day_seconds, 6)


def sky_anchor_slot(dt: datetime) -> float:
    return round(((dt.hour * 60 + dt.minute) / (24 * 60)), 6)


def local_node_anchor() -> float:
    return normalized_hash_float(str(COMMAND_ROOT.resolve()))


def runtime_node_anchor() -> float:
    return normalized_hash_float(socket.gethostname())


def canonical_relative_path(path: Path | str) -> str:
    raw = Path(path)
    try:
        return str(raw.resolve().relative_to(COMMAND_ROOT.resolve())).replace("\\", "/")
    except Exception:
        try:
            return str(raw.resolve().relative_to(WORKSPACE_ROOT.resolve())).replace("\\", "/")
        except Exception:
            return str(raw).replace("\\", "/")


def source_state_hash(path: Path | str, change_type: str, extra: str = "") -> str:
    candidate = Path(path)
    if candidate.exists():
        stat = candidate.stat()
        basis = f"{canonical_relative_path(candidate)}|{change_type}|{stat.st_size}|{stat.st_mtime_ns}|{extra}"
    else:
        basis = f"{canonical_relative_path(candidate)}|{change_type}|missing|{extra}"
    return f"H:{stable_hash(basis)[:16].upper()}"


def command_membrane_snapshot(root: Path = COMMAND_ROOT) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    if not root.exists():
        return snapshot
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = canonical_relative_path(path)
        stat = path.stat()
        snapshot[relative] = {
            "source_path": str(path.resolve()),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "state_hash": source_state_hash(path, "snapshot"),
        }
    return snapshot


def diff_snapshots(
    old_snapshot: dict[str, dict[str, Any]],
    new_snapshot: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    all_paths = sorted(set(old_snapshot) | set(new_snapshot))
    for relative in all_paths:
        old = old_snapshot.get(relative)
        new = new_snapshot.get(relative)
        if old is None and new is not None:
            events.append({"source_path": new["source_path"], "change_type": "created"})
        elif old is not None and new is None:
            events.append({"source_path": str(COMMAND_ROOT / relative), "change_type": "deleted"})
        elif old and new and (old["mtime_ns"] != new["mtime_ns"] or old["size"] != new["size"]):
            events.append({"source_path": new["source_path"], "change_type": "modified"})
    return events


def infer_goal(change_type: str, source_path: str) -> str:
    lower = source_path.lower()
    if "math" in lower or "equation" in lower or "compiler" in lower:
        return "detect-classify-assign-math"
    if "runtime" in lower or "queue" in lower or "board" in lower:
        return "detect-classify-assign-runtime"
    if change_type == "deleted":
        return "detect-classify-repair"
    return "detect-classify-assign"


def infer_tag(change_type: str, source_path: str) -> str:
    lower = source_path.lower()
    if "command" in lower:
        return f"command.{change_type}"
    if "math" in lower:
        return f"math.{change_type}"
    if "runtime" in lower or "board" in lower:
        return f"runtime.{change_type}"
    return f"command.mem.{change_type}"


def novelty_score(source_path: str, prior_snapshot: dict[str, dict[str, Any]] | None = None) -> float:
    relative = canonical_relative_path(source_path)
    if not prior_snapshot or relative not in prior_snapshot:
        return 1.0
    return 0.55


def infer_priority(source_path: str, change_type: str) -> float:
    lower = source_path.lower()
    priority = DEFAULT_PRIORITY
    if change_type == "deleted":
        priority += 0.15
    if any(token in lower for token in ["runtime", "queue", "board", "protocol", "manifest"]):
        priority += 0.1
    if any(token in lower for token in ["math", "equation", "compiler"]):
        priority += 0.05
    return min(1.0, round(priority, 3))


def infer_confidence(source_path: str, change_type: str) -> float:
    confidence = DEFAULT_CONFIDENCE
    if change_type == "deleted":
        confidence -= 0.1
    if source_path.lower().endswith(".docx"):
        confidence -= 0.03
    return round(max(0.55, confidence), 3)


def coord12_named(
    earth_dt: datetime,
    queue_pressure: float,
    goal_salience: float,
    novelty: float,
) -> dict[str, float]:
    local_dt = earth_dt.astimezone(local_timezone())
    return {
        "utc_time_fraction": fraction_of_day(earth_dt),
        "local_earth_rotation_phase": fraction_of_day(local_dt),
        "earth_orbital_phase": fraction_of_year(earth_dt),
        "local_node_anchor": local_node_anchor(),
        "solar_phase": fraction_of_day(local_dt),
        "lunar_phase": lunar_phase_fraction(earth_dt),
        "sidereal_phase": sidereal_phase_fraction(earth_dt),
        "sky_anchor_slot": sky_anchor_slot(local_dt),
        "runtime_node_anchor": runtime_node_anchor(),
        "queue_pressure": round(queue_pressure, 6),
        "goal_salience_vector": round(goal_salience, 6),
        "novelty_routing_concentration": round(novelty, 6),
    }


def coord12_tuple(named: dict[str, float]) -> list[float]:
    return [named[name] for name in COORDINATE_DIMENSIONS]


def coordinate_stamp(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "Xs": "GLOBAL_COMMAND",
        "Ys": packet["tag"],
        "Zs": packet["event_id"],
        "Ts": packet["earth_ts"],
        "Qs": packet["goal"],
        "Rs": packet["route_class"],
        "Cs": packet["claim_state"],
        "Fs": "command",
        "Ms": "command-protocol",
        "Ns": "command-membrane",
        "Hs": packet["state_hash"],
        "OmegaS": packet["truth_status"],
        "coord12": packet["coord12"],
    }


def packet_sequence(existing_packets: list[dict[str, Any]]) -> int:
    return len(existing_packets) + 1


def make_event_id(sequence: int, earth_dt: datetime | None = None) -> str:
    earth_dt = earth_dt or utc_now_dt()
    return f"EVT-{earth_dt.strftime('%Y%m%d')}-{sequence:04d}"


def build_event_packet(
    source_path: str,
    change_type: str,
    *,
    existing_packets: list[dict[str, Any]] | None = None,
    seed: dict[str, Any] | None = None,
    prior_snapshot: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    seed = seed or {}
    existing_packets = existing_packets or []
    earth_dt = utc_now_dt()
    priority = float(seed.get("priority", infer_priority(source_path, change_type)))
    confidence = float(seed.get("confidence", infer_confidence(source_path, change_type)))
    novelty = float(seed.get("novelty_score", novelty_score(source_path, prior_snapshot)))
    queue_pressure = min(1.0, len(existing_packets) / 50.0)
    goal = seed.get("goal", infer_goal(change_type, source_path))
    goal_salience = min(1.0, round((priority + confidence) / 2.0, 6))
    coord_named = coord12_named(earth_dt, queue_pressure, goal_salience, novelty)
    event_id = seed.get("event_id", make_event_id(packet_sequence(existing_packets), earth_dt))
    packet = {
        "event_id": event_id,
        "parent": seed.get("parent", "ROOT"),
        "source_root": str(COMMAND_ROOT.resolve()),
        "source_path": str(Path(source_path).resolve()) if Path(source_path).exists() else source_path,
        "source_relpath": canonical_relative_path(source_path),
        "change_type": change_type,
        "tag": seed.get("tag", infer_tag(change_type, source_path)),
        "goal": goal,
        "priority": priority,
        "confidence": confidence,
        "earth_ts": seed.get("earth_ts", earth_dt.isoformat()),
        "liminal_ts": seed.get("liminal_ts", liminal_timestamp(earth_dt)),
        "coord12": coord12_tuple(coord_named),
        "coord12_named": coord_named,
        "ttl": int(seed.get("ttl", DEFAULT_TTL)),
        "pheromone": float(seed.get("pheromone", round((goal_salience + novelty) / 2.0, 6))),
        "state_hash": seed.get("state_hash", source_state_hash(source_path, change_type, goal)),
        "route_class": seed.get("route_class", DEFAULT_ROUTE_CLASS),
        "claim_state": seed.get("claim_state", "unclaimed"),
        "truth_status": seed.get("truth_status", TRUTH_STATUS),
        "witness_refs": seed.get(
            "witness_refs",
            [
                str(LIVE_DOCS_GATE_PATH.resolve()),
                str(WITNESS_HIERARCHY_JSON.resolve()),
                str(WITNESS_HIERARCHY_MD.resolve()),
                str(COMMAND_ROOT.resolve()),
                source_path,
            ],
        ),
        "detected_by": seed.get("detected_by", ANT_REGISTRY[0]["ant_id"]),
        "queue_pressure": queue_pressure,
        "novelty_score": novelty,
        "goal_salience": goal_salience,
    }
    packet["coordinate_stamp"] = coordinate_stamp(packet)
    return packet


def ant_relevance(packet: dict[str, Any], ant: dict[str, Any]) -> float:
    source = packet["source_path"].lower()
    goal = packet["goal"].lower()
    score = 0.1
    if ant["ant_class"] == "Router":
        score += 0.55
    if ant["ant_class"] == "Worker":
        score += 0.25
    if ant["ant_class"] == "Archivist":
        score += 0.2
    specialization = ant["route_specialization"].lower()
    if "math" in source or "equation" in source or "algorithm" in goal:
        if "math" in specialization:
            score += 0.45
    if "runtime" in source or "board" in source or "protocol" in source:
        if "runtime" in specialization or "board" in specialization:
            score += 0.4
    if source.endswith(".docx") or source.endswith(".md"):
        if "manuscript" in specialization:
            score += 0.35
    if any(token in source for token in ["archive", "atlas", "tome", "capsule"]):
        if "archive" in specialization:
            score += 0.35
    if ant["ant_class"] == "Router" and "assign" in goal:
        score += 0.15
    return round(min(1.0, score), 6)


def stage_targets(packet: dict[str, Any], topk: int = DEFAULT_TOPK) -> list[dict[str, Any]]:
    router_targets = sorted(
        [dict(ant, relevance=ant_relevance(packet, ant)) for ant in ANT_REGISTRY if ant["ant_class"] == "Router"],
        key=lambda item: item["relevance"],
        reverse=True,
    )
    worker_targets = sorted(
        [dict(ant, relevance=ant_relevance(packet, ant)) for ant in ANT_REGISTRY if ant["ant_class"] == "Worker"],
        key=lambda item: item["relevance"],
        reverse=True,
    )
    archivist_targets = sorted(
        [dict(ant, relevance=ant_relevance(packet, ant)) for ant in ANT_REGISTRY if ant["ant_class"] == "Archivist"],
        key=lambda item: item["relevance"],
        reverse=True,
    )
    staged: list[dict[str, Any]] = []
    if router_targets:
        staged.append(router_targets[0])
    staged.extend(worker_targets[: max(0, topk - 2)])
    if archivist_targets:
        staged.append(archivist_targets[0])
    return staged[:topk]


def route_signature(packet: dict[str, Any], targets: list[dict[str, Any]]) -> str:
    chain = [packet["detected_by"], *(target["ant_id"] for target in targets)]
    return ">".join(chain)


def motion_candidate_world(packet: dict[str, Any], targets: list[dict[str, Any]]) -> dict[str, Any]:
    blocked_classes = []
    flags: dict[str, Any] = {}
    lowered = packet["source_path"].lower()
    if "q02" in lowered:
        blocked_classes.append("external-blocker:q02")
        flags["inadmissible_scope"] = True
    if packet["confidence"] < 0.7:
        flags["truth_burden_unsatisfied"] = True
    if packet["change_type"] == "deleted":
        flags["timing_not_lawful"] = True
    return {
        "brainstem_state": {
            "G": "GLOBAL COMMAND -> realtime board -> motion constitution -> Hall/Temple membrane",
            "Pi": "command pressure field over surprise-to-awareness latency",
            "Omega": {
                "status": "MIXED",
                "denied_packet_ids": ["Q02"] if "q02" in lowered else [],
            },
            "I": {
                "quarantine_classes": ["external-blocker:q02", "quarantine:contradiction"],
                "unresolved_failure_classes": ["unresolved-failure:route"],
                "committee_pending_routes": [],
            },
            "R": {
                "replay_capacity": 0.8,
                "replay_memory_quality": 0.85,
            },
        },
        "parameters": {
            "beta": 0.5,
        },
        "candidates": [
            {
                "id": packet["event_id"],
                "title": f"Command event {packet['source_relpath']}",
                "source_queue": "QuestBoard",
                "role_family": "command",
                "source_organ": "GLOBAL_COMMAND",
                "target_organ": "BrainstemChamber",
                "current_family": "transport",
                "truth_burden": "moderate" if packet["confidence"] >= 0.7 else "heavy",
                "packet_type_expected": "command_packet",
                "continuation_seed": f"seed::{packet['event_id']}",
                "dependencies": [],
                "blockers": ["q02-blocked"] if "q02" in lowered else [],
                "blocker_classes": blocked_classes,
                "axes": {
                    "truth_readiness": round(packet["confidence"], 6),
                    "integration_yield": round(min(1.0, packet["priority"] + 0.05), 6),
                    "replay_cost": 0.2,
                    "contradiction_heat": 0.85 if "q02" in lowered else 0.1,
                    "pressure_gradient": round(packet["priority"], 6),
                    "organ_adjacency": 0.85,
                    "branch_burden": round(max(0.1, len(targets) / 10.0), 6),
                    "seed_value": round(packet["novelty_score"], 6),
                    "closure_gain": round(packet["priority"], 6),
                    "heart_need": round(packet["priority"], 6),
                    "replay_readiness": 0.85,
                    "failure_debt": 0.7 if packet["change_type"] == "deleted" else 0.15,
                    "risk": 0.85 if "q02" in lowered else 0.2,
                    "cost": 0.25,
                },
                "flags": flags,
            }
        ],
    }


def capillary_registry_template() -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "truth_status": TRUTH_STATUS,
        "params": CAPILLARY_PARAMS,
        "edges": {},
    }


def route_ledger_template() -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "truth_status": TRUTH_STATUS,
        "entries": [],
    }


def claim_registry_template() -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "truth_status": TRUTH_STATUS,
        "claims": [],
    }


def watcher_health_template() -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "truth_status": TRUTH_STATUS,
        "watch_backend": watch_backend_name(),
        "native_watch_available": os.name == "nt",
        "mode": "native-watch" if os.name == "nt" else "degraded-polling",
        "last_watch_ts": None,
        "last_event_ts": None,
        "last_error": None,
    }


def membrane_status_template(snapshot: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "truth_status": TRUTH_STATUS,
        "sensor_root": str(COMMAND_ROOT.resolve()),
        "watch_backend": watch_backend_name(),
        "snapshot_file_count": len(snapshot),
        "last_snapshot_ts": datetime.now(UTC).isoformat(),
        "current_state": "ready",
        "docs_gate": "BLOCKED",
        "control_stack": CONTROL_STACK,
        "primary_thread_root": str(BOARD_THREAD_ROOT.resolve()),
        "change_feed_root": str(BOARD_CHANGE_FEED_ROOT.resolve()),
        "snapshot": snapshot,
    }


def classify_edge_maturity(weight: float) -> str:
    if weight >= CAPILLARY_PARAMS["vein_threshold"]:
        return "vein"
    if weight >= CAPILLARY_PARAMS["weak_threshold"]:
        return "capillary"
    return "weak-edge"


def update_capillary_weight(
    current_weight: float,
    usefulness: float,
    frequency: float,
    latency_penalty: float,
    noise_penalty: float,
) -> float:
    updated = (
        CAPILLARY_PARAMS["retention"] * current_weight
        + CAPILLARY_PARAMS["alpha_usefulness"] * usefulness
        + CAPILLARY_PARAMS["beta_frequency"] * frequency
        - CAPILLARY_PARAMS["gamma_latency"] * latency_penalty
        - CAPILLARY_PARAMS["delta_noise"] * noise_penalty
    )
    return round(max(0.0, min(3.0, updated)), 6)


def command_packet_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Command Protocol v1 Packet",
        "type": "object",
        "required": EVENT_PACKET_FIELDS,
        "properties": {
            "event_id": {"type": "string"},
            "parent": {"type": "string"},
            "source_root": {"type": "string"},
            "source_path": {"type": "string"},
            "change_type": {"type": "string", "enum": ["created", "modified", "deleted", "synthetic"]},
            "tag": {"type": "string"},
            "goal": {"type": "string"},
            "priority": {"type": "number"},
            "confidence": {"type": "number"},
            "earth_ts": {"type": "string"},
            "liminal_ts": {"type": "string"},
            "coord12": {
                "type": "array",
                "minItems": 12,
                "maxItems": 12,
                "items": {"type": "number"},
            },
            "ttl": {"type": "integer"},
            "pheromone": {"type": "number"},
            "state_hash": {"type": "string"},
            "route_class": {"type": "string"},
            "claim_state": {"type": "string"},
            "truth_status": {"type": "string"},
        },
    }


def fixture_event_seeds() -> list[dict[str, Any]]:
    global_readme = COMMAND_ROOT / "ATHENA" / "READ ME.txt"
    blocked_path = COMMAND_ROOT / "ATHENA" / "Q02_BLOCKED_SIGNAL.txt"
    return [
        {
            "name": "created_event",
            "source_path": str(global_readme),
            "change_type": "created",
            "goal": "detect-classify-assign",
            "tag": "command.created",
        },
        {
            "name": "modified_event",
            "source_path": str(global_readme),
            "change_type": "modified",
            "goal": "detect-classify-assign-runtime",
            "tag": "runtime.modified",
        },
        {
            "name": "repeat_success_event",
            "source_path": str(global_readme),
            "change_type": "modified",
            "goal": "detect-classify-assign",
            "tag": "command.repeat",
            "priority": 0.82,
            "confidence": 0.95,
        },
        {
            "name": "duplicate_noise_event",
            "source_path": str(global_readme),
            "change_type": "modified",
            "goal": "detect-classify-assign",
            "tag": "command.duplicate",
            "priority": 0.55,
            "confidence": 0.72,
        },
        {
            "name": "blocked_q02_event",
            "source_path": str(blocked_path),
            "change_type": "created",
            "goal": "detect-classify-assign-runtime",
            "tag": "command.blocked",
            "priority": 0.95,
            "confidence": 0.91,
        },
    ]


__all__ = [
    "ACTIVE_README_PATH",
    "ANT_CLASSES_MD",
    "ANT_REGISTRY",
    "BOARD_CHANGE_FEED_MD",
    "BOARD_CHANGE_FEED_ROOT",
    "BOARD_EVENT_FEED_MD",
    "BOARD_THREAD_ROOT",
    "CAPILLARY_LAW_MD",
    "CAPILLARY_PARAMS",
    "CAPILLARY_REGISTRY_JSON",
    "CLAIM_REGISTRY_JSON",
    "COMMAND_LAYER_ROOT",
    "COMMAND_MANIFEST_PATH",
    "COMMAND_REGISTRY_SUPPLEMENT_PATH",
    "COMMAND_ROOT",
    "COMMAND_SPEC_MD",
    "COMMAND_STATUS",
    "COMMAND_SUPPLEMENT_PATH",
    "CONTROL_STACK",
    "COORDINATE_DIMENSIONS",
    "COORDINATE_SCHEMA_MD",
    "EVENT_PACKET_FIELDS",
    "FIXTURES_DIR",
    "FULL_STACK_MANIFEST_PATH",
    "LEDGER_FIELDS",
    "LIVE_DOCS_GATE_PATH",
    "MEMBRANE_STATUS_JSON",
    "PACKET_LOG_JSON",
    "PACKET_SCHEMA_JSON",
    "READABLE_REGISTRY_MD",
    "ROUTE_LEDGER_JSON",
    "RUNNER_MANIFEST_PATH",
    "SECTIONS_DIR",
    "SIGMA_PATH",
    "SUPPLEMENTS_OUTPUT_PATH",
    "THREAD_EVENT_FEED_MD",
    "THREAD_STATUS_MD",
    "TRUTH_STATUS",
    "WATCHER_HEALTH_JSON",
    "WATCHDOG_AVAILABLE",
    "WITNESS_HIERARCHY_JSON",
    "WITNESS_HIERARCHY_MD",
    "build_event_packet",
    "canonical_relative_path",
    "capillary_registry_template",
    "claim_registry_template",
    "classify_edge_maturity",
    "command_membrane_snapshot",
    "command_packet_schema",
    "coord12_named",
    "coord12_tuple",
    "coordinate_stamp",
    "diff_snapshots",
    "fixture_event_seeds",
    "live_docs_error",
    "membrane_status_template",
    "motion_candidate_world",
    "route_ledger_template",
    "route_signature",
    "stage_targets",
    "update_capillary_weight",
    "watch_backend_name",
    "watcher_health_template",
]
