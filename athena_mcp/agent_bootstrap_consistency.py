from __future__ import annotations

import json

from .frontier_runtime import FrontierRuntime
from .git_backend import GitStateError
from .rehydration_loop import REHYDRATION_TOOLS, RehydrationLoopRuntime
from .rehydration_terminal import install_terminal_gate
from .rehydration_epoch import install_epoch_rollover


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


def _install_shared_fresh_verify_index(runtime_cls) -> None:
    """Compatibility only for pre-RHL-002/003 parents.

    Current master already owns the canonical `_athena_remote_fresh_reads_v2_registered`
    membrane. Bootstrap must consume that law rather than double-wrap verify/index.
    """

    if getattr(runtime_cls, "_athena_remote_fresh_reads_v2_registered", False):
        return
    flag = "_athena_remote_fresh_verify_index_compat_v1_registered"
    if getattr(runtime_cls, flag, False):
        return
    local_verify = runtime_cls.verify
    local_index = runtime_cls.index

    def _sync(self, operation: str, shared_remote_mode: str = "REQUIRED", remote: str = "origin"):
        mode = self._remote_mode(shared_remote_mode)
        if mode == "DISABLED":
            return mode, {
                "status": "DISABLED",
                "remote": remote,
                "shared_frontier_verified": False,
            }
        remote_sync = self.remote_sync.sync(remote)
        if mode == "REQUIRED" and not remote_sync.get("shared_frontier_verified"):
            raise GitStateError(
                json.dumps(
                    {
                        "status": f"REHYDRATION_{operation}_SHARED_FRONTIER_HOLD",
                        "remote_sync": remote_sync,
                        "law": "LOCAL_LOOP_VIEW != SHARED_CURRENT_LOOP_VIEW",
                    },
                    sort_keys=True,
                )
            )
        return mode, remote_sync

    def verify_remote_fresh(
        self,
        loop_id,
        shared_remote_mode: str = "REQUIRED",
        remote: str = "origin",
    ):
        mode, remote_sync = _sync(self, "VERIFY", shared_remote_mode, remote)
        result = local_verify(self, loop_id)
        result["remote_sync"] = remote_sync
        result["shared_frontier_verified"] = bool(remote_sync.get("shared_frontier_verified"))
        result["freshness_law"] = "VERIFY_SYNC_SHARED_GIT_BEFORE_REPLAYING_LOOP_CHAIN"
        if (
            mode == "BEST_EFFORT"
            and not result["shared_frontier_verified"]
            and result.get("status") == "PASS"
        ):
            result["status"] = "PASS_UNVERIFIED"
        return result

    def index_remote_fresh(
        self,
        shared_remote_mode: str = "REQUIRED",
        remote: str = "origin",
    ):
        mode, remote_sync = _sync(self, "INDEX", shared_remote_mode, remote)
        result = local_index(self)
        result["remote_sync"] = remote_sync
        result["shared_frontier_verified"] = bool(remote_sync.get("shared_frontier_verified"))
        result["freshness_law"] = "INDEX_SYNC_SHARED_GIT_BEFORE_LISTING_LOOP_TIPS"
        if (
            mode == "BEST_EFFORT"
            and not result["shared_frontier_verified"]
            and result.get("status") == "OK"
        ):
            result["status"] = "OK_UNVERIFIED"
        return result

    runtime_cls.verify = verify_remote_fresh
    runtime_cls.index = index_remote_fresh
    setattr(runtime_cls, flag, True)


def install_bootstrap_consistency(runtime_cls) -> None:
    """Install BOOT-001/002 while preserving canonical rehydration antibodies."""

    _install_shared_fresh_verify_index(RehydrationLoopRuntime)
    if not getattr(RehydrationLoopRuntime, "_athena_terminal_gate_v1_installed", False):
        install_terminal_gate(RehydrationLoopRuntime, REHYDRATION_TOOLS)
    # RHL-007 is additive and must be installed before __init__ forms the MCP
    # REHYDRATION tool union. It composes around the already-installed terminal
    # membrane and is later wrapped by canonical remote-fresh resume/index.
    install_epoch_rollover(RehydrationLoopRuntime, REHYDRATION_TOOLS)

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
