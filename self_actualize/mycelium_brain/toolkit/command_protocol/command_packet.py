from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED_PACKET_FIELDS = [
    "event_id",
    "ant_id",
    "tag",
    "goal",
    "change",
    "priority",
    "confidence",
    "earth_ts",
    "liminal_ts",
    "coord12",
    "parent",
    "ttl",
    "pheromone",
    "state_hash",
    "route_class",
]


def _normalize_float(value: float) -> float:
    return max(0.0, min(1.0, round(float(value), 6)))


def compute_state_hash(source_path: str, event_type: str, content_hint: str) -> str:
    digest = hashlib.sha256(f"{source_path}|{event_type}|{content_hint}".encode("utf-8")).hexdigest().upper()
    return f"H:{digest[:16]}"


def infer_tag(source_path: str, event_type: str) -> str:
    suffix = Path(source_path).suffix.lower()
    if suffix in {".md", ".txt", ".docx", ".pdf"}:
        base = "document"
    elif suffix in {".py", ".rs", ".toml", ".json"}:
        base = "runtime"
    else:
        base = "artifact"
    return f"{base}.{event_type}"


def infer_goal(source_path: str, event_type: str) -> str:
    path = source_path.lower()
    if "temple" in path or "guild" in path or "quest" in path or "board" in path:
        return "detect-classify-assign"
    if event_type in {"create", "move"}:
        return "detect-route-claim"
    if event_type == "delete":
        return "detect-route-prune"
    return "detect-classify-assign"


def infer_route_class(goal: str, event_type: str) -> str:
    if event_type == "delete":
        return "scout.router.archivist"
    if "claim" in goal or "assign" in goal:
        return "scout.router.worker.archivist"
    return "scout.router.worker"


@dataclass(slots=True)
class CommandEventPacket:
    event_id: str
    ant_id: str
    tag: str
    goal: str
    change: str
    priority: float
    confidence: float
    earth_ts: str
    liminal_ts: str
    coord12: dict[str, Any]
    parent: str
    ttl: int
    pheromone: float
    state_hash: str
    route_class: str
    lookup_addr: dict[str, Any] | None = None
    source_path: str | None = None
    event_type: str | None = None
    coord_quality: str | None = None
    watch_fallback: bool = False

    def to_record(self) -> dict[str, Any]:
        record = asdict(self)
        required = {key: record[key] for key in REQUIRED_PACKET_FIELDS}
        optional = {
            key: value
            for key, value in record.items()
            if key not in REQUIRED_PACKET_FIELDS and value is not None
        }
        return {"packet": required, **optional}


def build_packet(
    *,
    event_id: str,
    ant_id: str,
    source_path: str,
    event_type: str,
    change: str,
    earth_ts: str,
    liminal_ts: str,
    coord12: dict[str, Any],
    lookup_addr: dict[str, Any],
    parent: str = "ROOT",
    priority: float = 1.0,
    confidence: float = 0.98,
    ttl: int = 6,
    pheromone: float = 0.91,
    tag: str | None = None,
    goal: str | None = None,
    route_class: str | None = None,
    watch_fallback: bool = False,
) -> CommandEventPacket:
    packet_tag = tag or infer_tag(source_path, event_type)
    packet_goal = goal or infer_goal(source_path, event_type)
    packet_route_class = route_class or infer_route_class(packet_goal, event_type)
    state_hash = compute_state_hash(source_path, event_type, change)
    coord_quality = coord12.get("coord_quality", "NEAR")
    return CommandEventPacket(
        event_id=event_id,
        ant_id=ant_id,
        tag=packet_tag,
        goal=packet_goal,
        change=change,
        priority=_normalize_float(priority),
        confidence=_normalize_float(confidence),
        earth_ts=earth_ts,
        liminal_ts=liminal_ts,
        coord12=coord12,
        parent=parent,
        ttl=int(ttl),
        pheromone=_normalize_float(pheromone),
        state_hash=state_hash,
        route_class=packet_route_class,
        lookup_addr=lookup_addr,
        source_path=source_path,
        event_type=event_type,
        coord_quality=coord_quality,
        watch_fallback=watch_fallback,
    )


def validate_packet_record(record: dict[str, Any]) -> None:
    packet = record.get("packet", {})
    missing = [field for field in REQUIRED_PACKET_FIELDS if field not in packet]
    if missing:
        raise ValueError(f"packet missing required fields: {missing}")
    if "lookup_addr" not in record:
        raise ValueError("packet record missing lookup_addr")


def packet_from_record(record: dict[str, Any]) -> CommandEventPacket:
    validate_packet_record(record)
    packet = record["packet"]
    return CommandEventPacket(
        **packet,
        lookup_addr=record.get("lookup_addr"),
        source_path=record.get("source_path"),
        event_type=record.get("event_type"),
        coord_quality=record.get("coord_quality"),
        watch_fallback=record.get("watch_fallback", False),
    )


def record_to_json(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=True)
