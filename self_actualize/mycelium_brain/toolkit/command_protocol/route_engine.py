from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from datetime import UTC, datetime

from .capillary_memory import load_memory
from .ledger_writer import append_jsonl, route_receipts_path
from .liminal_coord import load_config


def _registry_root() -> Path:
    return Path(load_config().registry_root)


def _load_registry(name: str) -> Any:
    return json.loads((_registry_root() / name).read_text(encoding="utf-8"))


def _path_tags(source_path: str) -> set[str]:
    lowered = source_path.lower()
    tags = set(Path(lowered).parts)
    if lowered.endswith((".md", ".txt", ".docx", ".pdf")):
        tags.add("readable")
    if lowered.endswith((".py", ".rs", ".toml", ".json", ".yaml", ".yml")):
        tags.add("runtime")
    return tags


def _coord_proximity(packet_record: dict[str, Any], agent: dict[str, Any]) -> float:
    packet_goal = float(packet_record["packet"]["coord12"]["dimensions"]["goal_salience_vector"])
    target = float(agent.get("goal_bias", 0.5))
    return max(0.0, 1.0 - abs(packet_goal - target))


def _capillary_strength(agent_id: str) -> float:
    memory = load_memory()
    strengths = [
        edge["Strength"]
        for key, edge in memory["edges"].items()
        if key.endswith(f">{agent_id}")
    ]
    if not strengths:
        return memory["initial_strength"]
    return max(strengths)


def classify_path(packet_record: dict[str, Any]) -> str:
    source_path = packet_record.get("source_path", "")
    lowered = source_path.lower()
    if any(token in lowered for token in ["temple", "law", "decree"]):
        return "structural"
    if any(token in lowered for token in ["quest", "board", "queue"]):
        return "quest"
    if lowered.endswith((".py", ".rs", ".toml", ".json")):
        return "executable"
    return "document"


def route_packet(packet_record: dict[str, Any], topk: int = 5, quorum: int = 1) -> dict[str, Any]:
    agent_registry = _load_registry("agent_target_registry_v1.json")
    route_registry = _load_registry("route_registry_v1.json")
    source_tags = _path_tags(packet_record.get("source_path", ""))
    packet = packet_record["packet"]
    lookup = packet_record["lookup_addr"]
    path_class = classify_path(packet_record)

    candidates: list[dict[str, Any]] = []
    for agent in agent_registry["agents"]:
        score = 0.0
        if packet["goal"] in agent["goal_tags"]:
            score += 0.35
        if packet["tag"] in agent["tag_matches"]:
            score += 0.20
        if lookup["ZeroClass"] in agent["zero_classes"]:
            score += 0.10
        if lookup["OrganClass"] in agent["organ_classes"]:
            score += 0.08
        if lookup["Current"] in agent["currents"]:
            score += 0.08
        if path_class in agent["path_classes"]:
            score += 0.07
        if any(tag in source_tags for tag in agent["path_tags"]):
            score += 0.06
        score += 0.07 * _coord_proximity(packet_record, agent)
        score += 0.04 * _capillary_strength(agent["agent_id"])
        score -= 0.05 * float(agent.get("queue_penalty", 0.0))
        candidates.append(
            {
                "agent_id": agent["agent_id"],
                "score": round(max(0.0, min(1.0, score)), 6),
                "role": agent["role"],
                "path_class": path_class,
            }
        )

    ranked = sorted(candidates, key=lambda item: (-item["score"], item["agent_id"]))
    selected = ranked[:topk]
    receipt = {
        "receipt_type": "route_decision",
        "event_id": packet["event_id"],
        "policy": route_registry["policy_name"],
        "topk": topk,
        "quorum": quorum,
        "routed_at": datetime.now(tz=UTC).isoformat(),
        "candidate_targets": [candidate["agent_id"] for candidate in ranked],
        "selected_targets": [candidate["agent_id"] for candidate in selected],
        "ranked_routes": selected,
        "route_inputs": {
            "goal": packet["goal"],
            "tag": packet["tag"],
            "path_class": path_class,
            "zero_class": lookup["ZeroClass"],
            "organ_class": lookup["OrganClass"],
            "current": lookup["Current"],
        },
    }
    append_jsonl(route_receipts_path(), receipt)
    return receipt
