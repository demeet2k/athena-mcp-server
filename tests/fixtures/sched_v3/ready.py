from __future__ import annotations

from typing import Any, Mapping, Sequence

from .common import KernelError
from .reducer import reduce_events


_TERMINAL_NODE_STATES = {"SUCCEEDED", "FAILED", "HELD"}


def ready_nodes(
    run: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    *,
    capability: str | None = None,
    current_pulse: int | None = None,
) -> list[str]:
    """Return deterministic, unclaimed nodes that are actually dependency-ready.

    Wall-clock age is not readiness.  `current_pulse` only gates an explicit
    `not_before_pulse`; it never promotes a node whose dependencies are unresolved.
    """

    projection = reduce_events(run, events)
    if projection["run_state"] in {"COMMITTED", "PARTIAL_HOLD", "BLOCKED", "ABORTED"}:
        return []
    nodes = {str(node["node_id"]): node for node in run["nodes"]}
    ready: list[str] = []
    for node_id in sorted(nodes):
        node = nodes[node_id]
        state = projection["node_states"][node_id]
        if state in _TERMINAL_NODE_STATES or state != "PENDING":
            continue
        if capability is not None and node["role_capability"] != capability:
            continue
        if current_pulse is not None and current_pulse < int(node["not_before_pulse"]):
            continue
        if any(projection["node_states"][dependency] != "SUCCEEDED" for dependency in node["depends_on"]):
            continue
        claim_path = node["claim_path"]
        if claim_path in projection["claim_paths"].values():
            continue
        ready.append(node_id)
    return ready
