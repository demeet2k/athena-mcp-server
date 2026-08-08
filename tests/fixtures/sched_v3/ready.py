from __future__ import annotations

from typing import Any, Mapping, Sequence

from .common import KernelError

TERMINAL_NODE_STATES = {"SUCCEEDED", "FAILED", "HELD"}


def node_states(events: Sequence[Mapping[str, Any]], node_ids: set[str]) -> dict[str, str]:
    states = {node_id: "PENDING" for node_id in node_ids}
    transitions = {
        "NODE_READY": "READY",
        "CLAIM_ACQUIRED": "CLAIMED",
        "ACTION_ATTEMPTED": "RUNNING",
        "CHECKPOINT_WRITTEN": "CHECKPOINTED",
        "NODE_SUCCEEDED": "SUCCEEDED",
        "NODE_FAILED": "FAILED",
        "NODE_HELD": "HELD",
    }
    for event in sorted(events, key=lambda item: int(item["sequence"])):
        event_type = event.get("event_type")
        node_id = event.get("node_id")
        if event_type not in transitions:
            continue
        if node_id not in states:
            raise KernelError(f"event references unknown node: {node_id}")
        states[str(node_id)] = transitions[str(event_type)]
    return states


def ready_nodes(
    run: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    *,
    capability: str | None = None,
    current_pulse: int = 0,
) -> list[str]:
    """Return nodes ready from durable state, never from scheduled-time assumptions."""

    nodes = {str(node["node_id"]): node for node in run["nodes"]}
    states = node_states(events, set(nodes))
    result: list[str] = []
    for node_id in sorted(nodes):
        node = nodes[node_id]
        if states[node_id] != "PENDING":
            continue
        if capability is not None and node["role_capability"] != capability:
            continue
        if int(node["not_before_pulse"]) > current_pulse:
            continue
        if all(states[str(dependency)] == "SUCCEEDED" for dependency in node["depends_on"]):
            result.append(node_id)
    return result
