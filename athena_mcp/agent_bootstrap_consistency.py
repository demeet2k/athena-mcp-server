from __future__ import annotations

from .frontier_runtime import FrontierRuntime


def _selection_from_packet(frontier: dict) -> dict:
    """Select only from the exact frontier object returned in the boot packet."""

    candidates = list(frontier.get("ready_work") or [])
    status = frontier.get("status")
    if status != "HYDRATED":
        return {
            "status": "FRONTIER_HOLD",
            "selected": None,
            "pareto_front": [],
            "bound_frontier_digest": frontier.get("frontier_digest"),
            "reason": status or "FRONTIER_HOLD",
        }
    front = [
        candidate
        for candidate in candidates
        if not any(
            FrontierRuntime._dominates(other, candidate)
            for other in candidates
            if other is not candidate
        )
    ]
    if not front:
        return {
            "status": "NO_REPLAYABLE_READY_WORK",
            "selected": None,
            "pareto_front": [],
            "bound_frontier_digest": frontier.get("frontier_digest"),
        }
    selected = front[0] if len(front) == 1 else None
    return {
        "status": "SELECTED" if selected else "PARETO_HOLD",
        "selected": selected,
        "pareto_front": front,
        "bound_frontier_digest": frontier.get("frontier_digest"),
    }


def install_bootstrap_consistency(runtime_cls) -> None:
    """Install the BOOT-001 returned-snapshot selection antibody once.

    V1 bootstrap currently composes FrontierRuntime.hydrate() and select(), and the
    latter performs its own hydration. Until the redundant fetch is removed, bind
    the externally returned selection back to the exact frontier object in the
    packet so a sibling advance cannot mix two frontier snapshots in one result.
    """

    if getattr(runtime_cls, "_athena_boot_snapshot_binding_v1_registered", False):
        return
    original = runtime_cls.bootstrap

    def bootstrap_bound_snapshot(self, *args, **kwargs):
        packet = original(self, *args, **kwargs)
        frontier = packet.get("frontier") or {}
        packet["next_frontier"] = _selection_from_packet(frontier)
        packet["selection_snapshot_digest"] = frontier.get("frontier_digest")
        law = "NEXT_FRONTIER_SELECTION_BOUND_TO_RETURNED_FRONTIER_DIGEST"
        packet.setdefault("laws", [])
        if law not in packet["laws"]:
            packet["laws"].append(law)
        return packet

    runtime_cls.bootstrap = bootstrap_bound_snapshot
    runtime_cls._athena_boot_snapshot_binding_v1_registered = True
