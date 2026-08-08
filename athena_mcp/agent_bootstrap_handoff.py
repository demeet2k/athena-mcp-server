from __future__ import annotations

import hashlib
import json
from typing import Any

from . import agent_bootstrap as _boot
from .agent_bootstrap import AGENT_BOOT_TOOLS
from .rehydration_handoff import RehydrationHandoffRuntime
from .rehydration_loop import RehydrationLoopRuntime

CONTINUATION_ADDRESS_KEY = "rehydration_continuation_digest"
SIBLING_ADDRESS_KEY = "sibling_state_digest"
_ACTIVE_STATUS = "ACTIVE"
_HOLD_STATUSES = {
    "CONTINUATION_AMBIGUOUS_HOLD",
    "CONTINUATION_LOOP_NOT_FOUND_HOLD",
    "CONTINUATION_NOT_ACTIVE_HOLD",
    "CONTINUATION_INDEX_HOLD",
    "CONTINUATION_HANDOFF_HOLD",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _continuation_runtime(self):
    loop = getattr(self, "_agent_bootstrap_rehydration_loop_v1", None)
    if loop is None:
        loop = RehydrationLoopRuntime(self.git, self.prompt_runtime, self.frontier_runtime)
        self._agent_bootstrap_rehydration_loop_v1 = loop
    handoff = getattr(self, "_agent_bootstrap_handoff_runtime_v1", None)
    if handoff is None:
        handoff = RehydrationHandoffRuntime(self.git, self.prompt_runtime, loop)
        self._agent_bootstrap_handoff_runtime_v1 = handoff
    return loop, handoff


def _active_summary(row: dict) -> dict:
    return {
        "loop_id": row.get("loop_id"),
        "status": row.get("status"),
        "step_index": row.get("step_index"),
        "goal": row.get("goal"),
        "task": row.get("task"),
        "state_digest": row.get("state_digest"),
        "chain_digest": row.get("chain_digest"),
        "checkpoint_head": row.get("checkpoint_head"),
        "updated_at": row.get("updated_at"),
    }


def _continuation_snapshot(
    self,
    *,
    continuation_loop_id: str | None,
    shared_remote_mode: str,
    remote: str,
) -> dict:
    loop, handoff = _continuation_runtime(self)
    try:
        index = loop.index(shared_remote_mode=shared_remote_mode, remote=remote)
    except Exception as exc:
        packet = {
            "status": "CONTINUATION_INDEX_HOLD",
            "selected_loop_id": None,
            "active_loops": [],
            "handoff": None,
            "handoff_digest": None,
            "routing_successor": None,
            "shared_frontier_verified": False,
            "detail_type": type(exc).__name__,
        }
        packet["digest"] = _sha(packet)
        return packet

    loops = [row for row in index.get("loops") or [] if isinstance(row, dict)]
    active = [_active_summary(row) for row in loops if row.get("status") == _ACTIVE_STATUS]
    active.sort(key=lambda row: str(row.get("loop_id")))

    selected = None
    if continuation_loop_id:
        selected = next((row for row in loops if row.get("loop_id") == continuation_loop_id), None)
        if selected is None:
            status = "CONTINUATION_LOOP_NOT_FOUND_HOLD"
        elif selected.get("status") != _ACTIVE_STATUS:
            status = "CONTINUATION_NOT_ACTIVE_HOLD"
        else:
            status = "SELECTED"
    elif not active:
        status = "NO_ACTIVE_CONTINUATION"
    elif len(active) == 1:
        selected = active[0]
        status = "SELECTED"
    else:
        status = "CONTINUATION_AMBIGUOUS_HOLD"

    handoff_packet = None
    handoff_digest = None
    routing_successor = None
    hydration_mode = None
    affected_cone = None
    if status == "SELECTED" and selected is not None:
        selected_loop_id = str(selected.get("loop_id"))
        try:
            handoff_packet = handoff.derive(
                selected_loop_id,
                shared_remote_mode=shared_remote_mode,
                remote=remote,
            )
        except Exception as exc:
            handoff_packet = {
                "status": "CONTINUATION_HANDOFF_HOLD",
                "detail_type": type(exc).__name__,
            }
        handoff_digest = handoff_packet.get("handoff_digest")
        routing_successor = handoff_packet.get("routing_successor")
        handoff_body = handoff_packet.get("handoff") or {}
        hydration_mode = (handoff_body.get("hydration") or {}).get("mode")
        affected_cone = handoff_body.get("affected_cone")
        if handoff_packet.get("status") not in {"HANDOFF_READY", "HANDOFF_READY_UNVERIFIED"}:
            status = "CONTINUATION_HANDOFF_HOLD"
    else:
        selected_loop_id = None

    digest_basis = {
        "status": status,
        "selected_loop_id": selected_loop_id,
        "active_loops": active,
        "handoff_digest": handoff_digest,
        "hydration_mode": hydration_mode,
    }
    packet = {
        "status": status,
        "selected_loop_id": selected_loop_id,
        "active_loops": active,
        "active_count": len(active),
        "handoff": handoff_packet,
        "handoff_digest": handoff_digest,
        "hydration_mode": hydration_mode,
        "affected_cone": affected_cone,
        "routing_successor": routing_successor,
        "index_witness": {
            "status": index.get("status"),
            "shared_frontier_verified": index.get("shared_frontier_verified"),
            "freshness_law": index.get("freshness_law"),
            "remote_sync": index.get("remote_sync"),
        },
        "shared_frontier_verified": bool(index.get("shared_frontier_verified")),
        "standing": "CONTINUATION_CONTEXT_ONLY",
        "laws": [
            "CONTINUATION_STATE != EXECUTION_AUTHORIZATION",
            "WORLD_STATE != CONTINUATION_STATE",
            "WHAT_NEXT != WHAT_TO_REHYDRATE",
            "MULTIPLE_ACTIVE_LOOPS => AMBIGUITY_HOLD_UNLESS_EXPLICIT_LOOP",
            "NO_ACTIVE_LOOP != CONTINUATION_FAILURE",
        ],
    }
    packet["digest"] = _sha(digest_basis)
    return packet


def install_agent_bootstrap_handoff(runtime_cls) -> None:
    if getattr(runtime_cls, "_athena_boot_handoff_v1_registered", False):
        return

    for key in (SIBLING_ADDRESS_KEY, CONTINUATION_ADDRESS_KEY):
        if key not in _boot._ADDRESS_KEYS:
            _boot._ADDRESS_KEYS = tuple(_boot._ADDRESS_KEYS) + (key,)

    original_bootstrap = runtime_cls.bootstrap
    original_refresh = runtime_cls.refresh
    original_call_tool = runtime_cls.call_tool

    def bootstrap_with_handoff(
        self,
        *args,
        continuation_loop_id=None,
        continuation_shared_remote_mode="BEST_EFFORT",
        **kwargs,
    ):
        override = getattr(self, "_agent_bootstrap_continuation_override", None) or {}
        if continuation_loop_id is None:
            continuation_loop_id = override.get("continuation_loop_id")
        if continuation_shared_remote_mode == "BEST_EFFORT" and override.get("continuation_shared_remote_mode"):
            continuation_shared_remote_mode = override["continuation_shared_remote_mode"]

        packet = original_bootstrap(self, *args, **kwargs)
        remote = kwargs.get("remote", "origin")
        continuation = _continuation_snapshot(
            self,
            continuation_loop_id=continuation_loop_id,
            shared_remote_mode=continuation_shared_remote_mode,
            remote=remote,
        )
        packet["continuation"] = continuation
        sibling_digest = _sha(packet.get("siblings") or {})
        address = dict(packet.get("address") or {})
        address[SIBLING_ADDRESS_KEY] = sibling_digest
        address[CONTINUATION_ADDRESS_KEY] = continuation.get("digest")
        packet["address"] = address
        packet["composite_digest"] = _sha(address)
        packet["sibling_state_digest"] = sibling_digest
        packet["rehydration_continuation_digest"] = continuation.get("digest")
        packet.setdefault("witnesses", {})["continuation"] = continuation.get("index_witness")
        packet.setdefault("laws", [])
        for law in (
            "WORLD_STATE != CONTINUATION_STATE",
            "CONTINUATION_STATE != EXECUTION_AUTHORIZATION",
            "WHAT_NEXT != WHAT_TO_REHYDRATE",
        ):
            if law not in packet["laws"]:
                packet["laws"].append(law)
        if continuation.get("status") in _HOLD_STATUSES:
            holds = set(str(x) for x in packet.get("holds") or [])
            holds.add(str(continuation.get("status")))
            packet["holds"] = sorted(holds)
            packet["status"] = "BOOTSTRAP_HOLD"

        session_id = packet.get("session_id")
        if session_id and hasattr(self, "_sessions") and session_id in self._sessions:
            self._sessions[session_id]["address"] = dict(address)
            self._sessions[session_id]["continuation_loop_id"] = continuation_loop_id
            self._sessions[session_id]["continuation_shared_remote_mode"] = continuation_shared_remote_mode
        return packet

    def refresh_with_handoff(
        self,
        *args,
        continuation_loop_id=None,
        continuation_shared_remote_mode=None,
        **kwargs,
    ):
        session_id = kwargs.get("session_id")
        remembered = self._sessions.get(session_id or "") if session_id and hasattr(self, "_sessions") else None
        if continuation_loop_id is None and remembered is not None:
            continuation_loop_id = remembered.get("continuation_loop_id")
        if continuation_shared_remote_mode is None and remembered is not None:
            continuation_shared_remote_mode = remembered.get("continuation_shared_remote_mode")
        if continuation_shared_remote_mode is None:
            continuation_shared_remote_mode = "BEST_EFFORT"

        self._agent_bootstrap_continuation_override = {
            "continuation_loop_id": continuation_loop_id,
            "continuation_shared_remote_mode": continuation_shared_remote_mode,
        }
        try:
            packet = original_refresh(self, *args, **kwargs)
        finally:
            self._agent_bootstrap_continuation_override = None
        refresh = packet.get("refresh")
        if isinstance(refresh, dict):
            changed = refresh.get("changed") or {}
            affected = list(refresh.get("affected_dependency_cone") or [])
            if changed.get(SIBLING_ADDRESS_KEY) and "sibling_state" not in affected:
                affected.append("sibling_state")
            if changed.get(CONTINUATION_ADDRESS_KEY) and "rehydration_handoff" not in affected:
                affected.append("rehydration_handoff")
            refresh["affected_dependency_cone"] = affected
            refresh["requires_replan"] = any(bool(v) for v in changed.values())
            refresh["continuation_changed"] = bool(changed.get(CONTINUATION_ADDRESS_KEY))
            refresh["sibling_state_changed"] = bool(changed.get(SIBLING_ADDRESS_KEY))
        return packet

    def call_tool_with_handoff(self, name: str, a: dict):
        if name == "athena_agent_bootstrap":
            return self.bootstrap(
                agent_id=a["agent_id"],
                task=a.get("task", ""),
                profile=a.get("profile"),
                source_ref=a.get("source_ref", _boot.DEFAULT_SOURCE_REF),
                remote=a.get("remote", "origin"),
                fetch=a.get("fetch", True),
                issue_repo=a.get("issue_repo"),
                issue_limit=a.get("issue_limit", 10),
                continuation_loop_id=a.get("continuation_loop_id"),
                continuation_shared_remote_mode=a.get("continuation_shared_remote_mode", "BEST_EFFORT"),
            )
        if name == "athena_agent_refresh":
            return self.refresh(
                session_id=a.get("session_id"),
                prior_address=a.get("prior_address"),
                agent_id=a.get("agent_id"),
                task=a.get("task"),
                profile=a.get("profile"),
                source_ref=a.get("source_ref"),
                remote=a.get("remote"),
                fetch=a.get("fetch"),
                issue_repo=a.get("issue_repo"),
                issue_limit=a.get("issue_limit"),
                continuation_loop_id=a.get("continuation_loop_id"),
                continuation_shared_remote_mode=a.get("continuation_shared_remote_mode"),
            )
        return original_call_tool(self, name, a)

    runtime_cls.bootstrap = bootstrap_with_handoff
    runtime_cls.refresh = refresh_with_handoff
    runtime_cls.call_tool = call_tool_with_handoff
    runtime_cls._athena_boot_handoff_v1_registered = True

    for tool in AGENT_BOOT_TOOLS:
        props = (tool.get("inputSchema") or {}).setdefault("properties", {})
        props.setdefault("continuation_loop_id", {"type": ["string", "null"]})
        props.setdefault(
            "continuation_shared_remote_mode",
            {"type": ["string", "null"], "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED", None]},
        )
        if tool.get("name") == "athena_agent_bootstrap":
            tool["description"] = (
                "Cold-start one AGENT_BOOT_V1 packet from prompt policy, replayable SCHED frontier, issue pressure, "
                "sibling activity, and an independently versioned rehydration-handoff continuation coordinate."
            )
        elif tool.get("name") == "athena_agent_refresh":
            tool["description"] = (
                "Refresh AGENT_BOOT_V1 factorized coordinates and report affected dependency cones, including "
                "rehydration handoff when continuation state changes independently."
            )

    # BOOT-003 must be outermost: shared Git freshness has to precede prompt/world
    # composition as well as continuation indexing. Installing it here guarantees
    # the handoff wrapper exists first, then the shared-fresh snapshot membrane
    # wraps the complete one-call boot/refresh surface.
    from .agent_bootstrap_shared_fresh import install_agent_bootstrap_shared_fresh

    install_agent_bootstrap_shared_fresh(runtime_cls)
