from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Any

from .ledger_writer import (
    append_jsonl,
    claim_ledger_path,
    event_ledger_path,
    front_memory_path,
    hall_fronts_path,
    promotion_receipts_path,
    read_json,
    read_jsonl,
    route_receipts_path,
    temple_fronts_path,
    write_json,
)
from .route_engine import classify_path


TEMPLE_KEYWORDS = {
    "law",
    "ontology",
    "coordinate",
    "mapping",
    "compression",
    "continuity",
    "restart",
    "protocol",
    "governance",
    "purity",
    "decree",
    "charter",
}

HALL_KEYWORDS = {
    "implementation",
    "repair",
    "index",
    "indexing",
    "math",
    "algorithm",
    "algorithmization",
    "runtime",
    "worker",
    "queue",
    "build",
    "execute",
    "executable",
    "rewrite",
    "code",
    "route",
}

TEMPLE_LANES = ["M1-SYNTH", "M2-PLAN", "Athena-A", "M4-PRUNE"]
HALL_LANES = ["M3-WORK", "Athena-G", "Athena-P", "A2", "A6", "A8", "M4-PRUNE"]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "untyped"


def _latest_event_record(event_id: str) -> dict[str, Any]:
    for row in reversed(read_jsonl(event_ledger_path())):
        if row["packet"]["event_id"] == event_id:
            return row
    raise KeyError(f"unknown event id: {event_id}")


def _latest_route_decision(event_id: str) -> dict[str, Any] | None:
    for row in reversed(read_jsonl(route_receipts_path())):
        if row.get("event_id") == event_id and row.get("receipt_type") == "route_decision":
            return row
    return None


def _latest_claim(event_id: str) -> dict[str, Any] | None:
    for row in reversed(read_jsonl(claim_ledger_path())):
        if row.get("event_id") == event_id:
            return row
    return None


def _latest_latency(event_id: str) -> dict[str, Any] | None:
    for row in reversed(read_jsonl(route_receipts_path())):
        if row.get("event_id") == event_id and row.get("receipt_type") == "latency_receipt":
            return row
    return None


def _event_text(event_record: dict[str, Any]) -> str:
    packet = event_record["packet"]
    pieces = [
        event_record.get("source_path", ""),
        packet.get("tag", ""),
        packet.get("goal", ""),
        packet.get("change", ""),
    ]
    return " ".join(piece.lower() for piece in pieces if piece)


def _planes_for_event(event_record: dict[str, Any]) -> tuple[bool, bool]:
    text = _event_text(event_record)
    path_class = classify_path(event_record)
    temple_hit = path_class == "structural" or any(keyword in text for keyword in TEMPLE_KEYWORDS)
    hall_hit = path_class in {"quest", "executable"} or any(keyword in text for keyword in HALL_KEYWORDS)
    return temple_hit, hall_hit


def _front_key(event_record: dict[str, Any], plane: str) -> str:
    packet = event_record["packet"]
    lookup = event_record["lookup_addr"]
    path_class = classify_path(event_record)
    return ":".join(
        [
            plane,
            _slug(packet["goal"]),
            _slug(packet["tag"]),
            path_class,
            lookup["ZeroClass"],
            lookup["OrganClass"],
            lookup["Current"],
        ]
    )


def _front_id(front_key: str) -> str:
    digest = hashlib.sha1(front_key.encode("utf-8")).hexdigest().upper()[:10]
    return f"CF-{digest}"


def _quest_id(front_id: str, plane: str) -> str:
    prefix = "TQ-CMD" if plane == "temple" else "Q-CMD"
    return f"{prefix}-{front_id.split('-')[-1]}"


def _best_lane(plane: str, route_receipt: dict[str, Any] | None) -> str:
    if route_receipt:
        selected = route_receipt.get("selected_targets", [])
        preferred = TEMPLE_LANES if plane == "temple" else HALL_LANES
        for candidate in preferred:
            if candidate in selected:
                return candidate
        if selected:
            return selected[0]
    return "M2-PLAN" if plane == "temple" else "M3-WORK"


def _route_quality(route_receipt: dict[str, Any] | None) -> float:
    if not route_receipt:
        return 0.0
    ranked = route_receipt.get("ranked_routes", [])
    if not ranked:
        return 0.0
    return round(float(ranked[0].get("score", 0.0)), 6)


def _truth(event_record: dict[str, Any]) -> str:
    witness_class = event_record["lookup_addr"]["WitnessClass"]
    if witness_class == "OK":
        return "OK"
    return "NEAR"


def _witness_needed(event_record: dict[str, Any]) -> list[str]:
    base = ["route_receipt", "claim_receipt"]
    if _truth(event_record) != "OK":
        base.append("witness_closure")
    return base


def _target_surfaces(plane: str) -> list[str]:
    if plane == "temple":
        return [
            "ATHENA TEMPLE/BOARDS/04_COMMAND_PROMOTION_BOARD.md",
            "ATHENA TEMPLE/BOARDS/02_TEMPLE_QUEST_BOARD.md",
        ]
    return [
        "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/09_COMMAND_EVENT_QUEUE_BOARD.md",
        "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
    ]


def _writeback(plane: str) -> list[str]:
    if plane == "temple":
        return [
            "ATHENA TEMPLE/BOARDS/04_COMMAND_PROMOTION_BOARD.md",
            "ATHENA TEMPLE/BOARDS/02_TEMPLE_QUEST_BOARD.md",
            "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
        ]
    return [
        "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/09_COMMAND_EVENT_QUEUE_BOARD.md",
        "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/10_COMMAND_CLAIM_LEASE_BOARD.md",
        "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/11_COMMAND_ROUTE_QUALITY_BOARD.md",
        "C:/Users/dmitr/Documents/CLAUDE/Q-SHRINK/NERVOUS_SYSTEM/analysis/COMMAND_PROTOCOL_MIRROR.md",
    ]


def _objective(event_record: dict[str, Any], plane: str) -> str:
    packet = event_record["packet"]
    path_class = classify_path(event_record)
    if plane == "temple":
        return f"Promote command event `{packet['event_id']}` into lawful Temple pressure for {path_class} coherence."
    return f"Promote command event `{packet['event_id']}` into ownerable Hall work for {path_class} execution."


def _why_now(event_record: dict[str, Any], plane: str) -> str:
    packet = event_record["packet"]
    if plane == "temple":
        return f"Committed command change `{packet['tag']}` touches governance-relevant structure and should not remain only a routed event."
    return f"Committed command change `{packet['tag']}` has executable pressure and should become claimable Hall work."


def _load_front_memory() -> dict[str, Any]:
    return read_json(
        front_memory_path(),
        {
            "schema_id": "COMMAND_FRONT_MEMORY_V1",
            "active_fronts": {},
        },
    )


def _store_front_memory(memory: dict[str, Any]) -> None:
    write_json(front_memory_path(), memory)


def _front_record(
    *,
    event_record: dict[str, Any],
    plane: str,
    route_receipt: dict[str, Any] | None,
    mode: str,
) -> dict[str, Any]:
    packet = event_record["packet"]
    lookup = event_record["lookup_addr"]
    front_key = _front_key(event_record, plane)
    front_id = _front_id(front_key)
    return {
        "front_id": front_id,
        "source_event_id": packet["event_id"],
        "source_path": event_record.get("source_path", ""),
        "plane": plane,
        "front_key": front_key,
        "objective": _objective(event_record, plane),
        "why_now": _why_now(event_record, plane),
        "target_surfaces": _target_surfaces(plane),
        "best_lane": _best_lane(plane, route_receipt),
        "witness_needed": _witness_needed(event_record),
        "writeback": _writeback(plane),
        "status": "ACTIVE",
        "zero_class": lookup["ZeroClass"],
        "organ_class": lookup["OrganClass"],
        "current": lookup["Current"],
        "truth": _truth(event_record),
        "route_quality": _route_quality(route_receipt),
        "quest_id": _quest_id(front_id, plane),
        "path_class": classify_path(event_record),
        "op": mode,
        "promoted_at": datetime.now(tz=UTC).isoformat(),
    }


def _upsert_front(memory: dict[str, Any], front: dict[str, Any]) -> tuple[dict[str, Any], str]:
    now = datetime.now(tz=UTC).isoformat()
    active = memory["active_fronts"].get(front["front_key"])
    quest_id = front["quest_id"]
    if active:
        active["occurrence_count"] = int(active.get("occurrence_count", 1)) + 1
        active["latest_source_event"] = front["source_event_id"]
        active["last_updated_at"] = now
        active["truth"] = front["truth"]
        active["route_quality"] = front["route_quality"]
        active["linked_quests"] = sorted(set(active.get("linked_quests", []) + [quest_id]))
        active["decay_eligible"] = True
        active["best_lane"] = front["best_lane"]
        memory["active_fronts"][front["front_key"]] = active
        front["quest_id"] = quest_id
        return active, "updated"
    memory["active_fronts"][front["front_key"]] = {
        "front_id": front["front_id"],
        "plane": front["plane"],
        "front_key": front["front_key"],
        "occurrence_count": 1,
        "latest_source_event": front["source_event_id"],
        "linked_quests": [quest_id],
        "decay_eligible": True,
        "truth": front["truth"],
        "route_quality": front["route_quality"],
        "best_lane": front["best_lane"],
        "last_updated_at": now,
    }
    return memory["active_fronts"][front["front_key"]], "created"


def promote_event(event_id: str) -> dict[str, Any]:
    event_record = _latest_event_record(event_id)
    route_receipt = _latest_route_decision(event_id)
    claim_receipt = _latest_claim(event_id)
    latency_receipt = _latest_latency(event_id)
    promoted_at = datetime.now(tz=UTC).isoformat()

    if route_receipt is None:
        receipt = {
            "receipt_type": "promotion_receipt",
            "source_event_id": event_id,
            "promoted_at": promoted_at,
            "verdict": "NEAR",
            "skipped": True,
            "reason": "missing_route_decision",
            "planes": [],
            "fronts": [],
        }
        append_jsonl(promotion_receipts_path(), receipt)
        return receipt

    if claim_receipt is None or claim_receipt.get("status") != "claimed":
        receipt = {
            "receipt_type": "promotion_receipt",
            "source_event_id": event_id,
            "promoted_at": promoted_at,
            "verdict": "NEAR",
            "skipped": True,
            "reason": "missing_committed_claim",
            "planes": [],
            "fronts": [],
        }
        append_jsonl(promotion_receipts_path(), receipt)
        return receipt

    temple_hit, hall_hit = _planes_for_event(event_record)
    memory = _load_front_memory()
    promoted_fronts: list[dict[str, Any]] = []
    promoted_planes: list[str] = []
    for plane, hit in (("temple", temple_hit), ("hall", hall_hit)):
        if not hit:
            continue
        front = _front_record(
            event_record=event_record,
            plane=plane,
            route_receipt=route_receipt,
            mode="pending",
        )
        active_front, mode = _upsert_front(memory, front)
        front["op"] = mode
        front["occurrence_count"] = active_front["occurrence_count"]
        target_path = temple_fronts_path() if plane == "temple" else hall_fronts_path()
        append_jsonl(target_path, front)
        promoted_planes.append(plane)
        promoted_fronts.append(
            {
                "plane": plane,
                "front_id": front["front_id"],
                "front_key": front["front_key"],
                "quest_id": front["quest_id"],
                "target_board": front["target_surfaces"][0],
                "mode": mode,
                "truth": front["truth"],
            }
        )

    _store_front_memory(memory)
    receipt = {
        "receipt_type": "promotion_receipt",
        "source_event_id": event_id,
        "promoted_at": promoted_at,
        "verdict": "OK" if promoted_fronts and all(front["truth"] == "OK" for front in promoted_fronts) else ("NEAR" if promoted_fronts else "NEAR"),
        "skipped": not promoted_fronts,
        "reason": None if promoted_fronts else "no_promotable_plane",
        "planes": promoted_planes,
        "fronts": promoted_fronts,
        "claim_receipt": claim_receipt,
        "route_quality": _route_quality(route_receipt),
        "latency_receipt": latency_receipt,
    }
    append_jsonl(promotion_receipts_path(), receipt)
    return receipt
