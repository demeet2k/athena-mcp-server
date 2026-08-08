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
    """Install returned-snapshot and rolling-session consistency antibodies.

    BOOT-001: V1 bootstrap composes FrontierRuntime.hydrate() and select(), and the
    latter performs its own hydration. Until the redundant fetch is removed, bind
    the externally returned selection back to the exact frontier object in the
    packet so a sibling advance cannot mix two frontier snapshots in one result.

    BOOT-002: a live session_id is an evolving checkpoint. V1 refresh internally
    calls bootstrap and therefore creates a transient successor session. Collapse
    that transient session back into the requested session after a successful
    refresh so the next refresh compares against the last observed address rather
    than the original cold-start address. Explicit prior_address mode stays
    stateless and may return a fresh session id.
    """

    if getattr(runtime_cls, "_athena_boot_consistency_v1_registered", False):
        return

    original_bootstrap = runtime_cls.bootstrap

    def bootstrap_bound_snapshot(self, *args, **kwargs):
        packet = original_bootstrap(self, *args, **kwargs)
        frontier = packet.get("frontier") or {}
        packet["next_frontier"] = _selection_from_packet(frontier)
        packet["selection_snapshot_digest"] = frontier.get("frontier_digest")
        law = "NEXT_FRONTIER_SELECTION_BOUND_TO_RETURNED_FRONTIER_DIGEST"
        packet.setdefault("laws", [])
        if law not in packet["laws"]:
            packet["laws"].append(law)
        return packet

    runtime_cls.bootstrap = bootstrap_bound_snapshot

    original_refresh = getattr(runtime_cls, "refresh", None)
    if original_refresh is not None:
        def refresh_rolling_session(self, *args, **kwargs):
            requested_session_id = kwargs.get("session_id")
            remembered = None
            if requested_session_id and hasattr(self, "_sessions"):
                remembered = self._sessions.get(requested_session_id)

            packet = original_refresh(self, *args, **kwargs)
            if not requested_session_id or remembered is None:
                return packet
            if packet.get("status") == "SESSION_NOT_FOUND_HOLD" or not packet.get("address"):
                return packet

            spawned_session_id = packet.get("session_id")
            spawned_state = None
            if (
                spawned_session_id
                and spawned_session_id != requested_session_id
                and hasattr(self, "_sessions")
            ):
                spawned_state = self._sessions.pop(spawned_session_id, None)

            state = spawned_state or dict(remembered)
            state["address"] = dict(packet["address"])
            self._sessions[requested_session_id] = state
            packet["session_id"] = requested_session_id
            packet.setdefault("refresh", {})["session_checkpoint_advanced"] = True
            law = "LIVE_SESSION_REFRESH_ADVANCES_PRIOR_ADDRESS"
            packet.setdefault("laws", [])
            if law not in packet["laws"]:
                packet["laws"].append(law)
            return packet

        runtime_cls.refresh = refresh_rolling_session

    runtime_cls._athena_boot_consistency_v1_registered = True
