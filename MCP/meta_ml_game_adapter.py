"""Read-only MCP adapter for the Athena Meta Machine Learning Game.

The authoritative registry remains in ``demeet2k/Athena`` on branch
``agent/athena-git-brain-v2``. Set ``ATHENA_META_ML_ROOT`` to a checkout of
that repository. This adapter never mutates source truth, user objectives, or
foundation-model weights.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import os


DEFAULT_ROOT = Path(os.environ.get("ATHENA_META_ML_ROOT", "../Athena"))


def _root(root: str | Path | None = None) -> Path:
    return Path(root) if root is not None else DEFAULT_ROOT


def load_constitution(root: str | Path | None = None) -> dict[str, Any]:
    return json.loads(
        (_root(root) / "meta_ml_game" / "constitution.json").read_text(
            encoding="utf-8"
        )
    )


def load_goals(root: str | Path | None = None) -> list[dict[str, Any]]:
    directory = _root(root) / "meta_ml_game" / "goals"
    goals: list[dict[str, Any]] = []
    for path in sorted(directory.glob("d*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        defaults = payload.get("defaults", {})
        goals.extend({**defaults, **goal} for goal in payload["goals"])
    if len(goals) != 144:
        raise ValueError(f"expected 144 goals, found {len(goals)}")
    return goals


def list_goals(
    *,
    domain_id: str | None = None,
    status: str | None = None,
    query: str | None = None,
    root: str | Path | None = None,
) -> list[dict[str, Any]]:
    goals = load_goals(root)
    if domain_id:
        goals = [goal for goal in goals if goal["domain_id"] == domain_id]
    if status:
        goals = [goal for goal in goals if goal.get("status") == status]
    if query:
        needle = query.casefold()
        goals = [
            goal
            for goal in goals
            if needle in json.dumps(goal, ensure_ascii=False).casefold()
        ]
    return goals


def next_quest(
    signals: dict[str, float] | None = None,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    signals = signals or {}
    candidates = []
    for goal in load_goals(root):
        if goal.get("status") not in {"OPEN", "ACTIVE", "BLOCKED"}:
            continue
        goal_id = goal["id"]
        priority = (
            float(signals.get(f"{goal_id}:impact", goal.get("weight", 1.0)))
            + float(signals.get(f"{goal_id}:evidence_gap", 0.5))
            + float(signals.get(f"{goal_id}:uncertainty", 0.5))
            - float(signals.get(f"{goal_id}:cost", 0.25))
            - float(signals.get(f"{goal_id}:risk", 0.1))
        )
        candidates.append((priority, goal_id, goal))
    if not candidates:
        raise ValueError("no eligible meta-learning quest")
    candidates.sort(key=lambda item: (-item[0], item[1]))
    return candidates[0][2]


def resource_summary(root: str | Path | None = None) -> dict[str, Any]:
    goals = load_goals(root)
    domains = sorted({(goal["domain_id"], goal["domain"]) for goal in goals})
    return {
        "resource": "athena://meta-ml-game/v1",
        "goal_count": len(goals),
        "domains": [
            {"domain_id": domain_id, "title": title}
            for domain_id, title in domains
        ],
        "constitution": load_constitution(root),
        "write_boundary": (
            "Read-only adapter. Experiment and promotion writes require the "
            "Athena control-plane witness gates."
        ),
    }


def register_meta_ml_tools(mcp) -> None:
    """Install three read-only Meta-ML tools on a FastMCP server."""

    @mcp.tool()
    def meta_ml_list_goals(
        domain_id: str = "",
        status: str = "",
        query: str = "",
    ) -> str:
        """List or search the 144 governed improvement quests."""
        return json.dumps(
            list_goals(
                domain_id=domain_id or None,
                status=status or None,
                query=query or None,
            ),
            indent=2,
            ensure_ascii=False,
        )

    @mcp.tool()
    def meta_ml_next_quest(signals_json: str = "{}") -> str:
        """Select the highest-priority lawful quest from optional signal values."""
        signals = json.loads(signals_json or "{}")
        return json.dumps(next_quest(signals), indent=2, ensure_ascii=False)

    @mcp.tool()
    def meta_ml_goal(goal_id: str) -> str:
        """Return one exact Meta-ML quest by MLG-G001 through MLG-G144."""
        matches = [goal for goal in load_goals() if goal["id"] == goal_id]
        if not matches:
            return json.dumps({"error": "GOAL_NOT_FOUND", "goal_id": goal_id})
        return json.dumps(matches[0], indent=2, ensure_ascii=False)


def register_meta_ml_resources(mcp) -> None:
    """Install stable Meta-ML resources on a FastMCP server."""

    @mcp.resource("athena://meta-ml-game/v1")
    def meta_ml_game_resource() -> str:
        return json.dumps(resource_summary(), indent=2, ensure_ascii=False)

    @mcp.resource("athena://meta-ml-game/goals")
    def meta_ml_goals_resource() -> str:
        return json.dumps(load_goals(), indent=2, ensure_ascii=False)
