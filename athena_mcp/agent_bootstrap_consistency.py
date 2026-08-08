from __future__ import annotations

import hashlib
import json

from . import agent_bootstrap as _boot
from . import protocol as _protocol
from .agent_bootstrap import AGENT_BOOT_TOOL_NAMES
from .capability_basis import (
    CAPABILITY_BASIS_TOOLS,
    CAPABILITY_BASIS_TOOL_NAMES,
    RUNTIME_WITNESS,
    derive_operational_basis,
)
from .frontier_runtime import FrontierRuntime
from .git_backend import GitStateError
from .prompt_runtime import (
    PROMPT_RUNTIME_TOOLS,
    PROMPT_RUNTIME_TOOL_NAMES,
)
from .rehydration_loop import REHYDRATION_TOOLS, RehydrationLoopRuntime
from .rehydration_terminal import install_terminal_gate

BASIS_ADDRESS_KEY = "operational_basis_digest"


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


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


def _register_capability_basis_tool() -> None:
    """Register the read-only basis through existing PromptRuntime dispatch.

    The name joins AGENT_BOOT_TOOL_NAMES so the already-installed PromptRuntime
    agent-boot dispatcher routes it to AgentBootstrapRuntime.call_tool, but it is
    intentionally not inserted into AGENT_BOOT_TOOLS: the later handoff schema
    extension must not add continuation arguments to this zero-argument read.
    """

    for tool in CAPABILITY_BASIS_TOOLS:
        name = tool["name"]
        AGENT_BOOT_TOOL_NAMES.add(name)
        if name not in PROMPT_RUNTIME_TOOL_NAMES:
            PROMPT_RUNTIME_TOOLS.append(tool)
            PROMPT_RUNTIME_TOOL_NAMES.add(name)
        if not any(existing.get("name") == name for existing in _protocol.TOOLS):
            _protocol.TOOLS.append(tool)


def _current_operational_basis() -> dict:
    return derive_operational_basis(
        PROMPT_RUNTIME_TOOL_NAMES,
        runtime_identity=RUNTIME_WITNESS,
    )


def _install_capability_basis(runtime_cls) -> None:
    _register_capability_basis_tool()

    if BASIS_ADDRESS_KEY not in _boot._ADDRESS_KEYS:
        _boot._ADDRESS_KEYS = tuple(_boot._ADDRESS_KEYS) + (BASIS_ADDRESS_KEY,)

    flag = "_athena_capability_basis_v1_registered"
    if getattr(runtime_cls, flag, False):
        return

    original_bootstrap = runtime_cls.bootstrap
    original_refresh = runtime_cls.refresh
    original_call_tool = runtime_cls.call_tool

    def bootstrap_with_operational_basis(self, *args, **kwargs):
        packet = original_bootstrap(self, *args, **kwargs)
        basis = _current_operational_basis()
        packet["operational_basis"] = basis
        packet.setdefault("execution_surface", {})["operational_basis_digest"] = basis.get("basis_digest")
        packet["execution_surface"]["capability_classes"] = basis.get("capability_classes") or {}
        packet["execution_surface"]["unclassified"] = basis.get("unclassified") or []

        address = dict(packet.get("address") or {})
        address[BASIS_ADDRESS_KEY] = basis.get("basis_digest")
        packet["address"] = address
        packet["composite_digest"] = _sha(address)

        if basis.get("status") != "PASS":
            holds = set(str(value) for value in packet.get("holds") or [])
            holds.add(str(basis.get("status") or "CAPABILITY_BASIS_HOLD"))
            packet["holds"] = sorted(holds)
            packet["status"] = "BOOTSTRAP_HOLD"

        packet.setdefault("laws", [])
        for law in (
            "OPERATIONAL_BASIS != HIGHER_AUTHORITY",
            "DESCRIPTOR != PERMISSION",
            "UNCLASSIFIED_RUNTIME_CAPABILITY => SEMANTIC_SELECTION_HOLD",
            "BASIS_DIGEST != GIT_HEAD",
        ):
            if law not in packet["laws"]:
                packet["laws"].append(law)

        session_id = packet.get("session_id")
        if session_id and hasattr(self, "_sessions") and session_id in self._sessions:
            self._sessions[session_id]["address"] = dict(address)
        return packet

    def refresh_with_operational_basis(self, *args, **kwargs):
        packet = original_refresh(self, *args, **kwargs)
        refresh = packet.get("refresh")
        if isinstance(refresh, dict):
            changed = refresh.get("changed") or {}
            affected = list(refresh.get("affected_dependency_cone") or [])
            if changed.get(BASIS_ADDRESS_KEY) and "operational_basis" not in affected:
                affected.append("operational_basis")
            refresh["affected_dependency_cone"] = affected
            refresh["operational_basis_changed"] = bool(changed.get(BASIS_ADDRESS_KEY))
            refresh["requires_replan"] = any(bool(value) for value in changed.values())
        return packet

    def call_tool_with_operational_basis(self, name: str, arguments: dict):
        if name in CAPABILITY_BASIS_TOOL_NAMES:
            return _current_operational_basis()
        return original_call_tool(self, name, arguments)

    runtime_cls.bootstrap = bootstrap_with_operational_basis
    runtime_cls.refresh = refresh_with_operational_basis
    runtime_cls.call_tool = call_tool_with_operational_basis
    setattr(runtime_cls, flag, True)


def install_bootstrap_consistency(runtime_cls) -> None:
    """Install BOOT-001/002 while preserving canonical rehydration antibodies."""

    _install_shared_fresh_verify_index(RehydrationLoopRuntime)
    if not getattr(RehydrationLoopRuntime, "_athena_terminal_gate_v1_installed", False):
        install_terminal_gate(RehydrationLoopRuntime, REHYDRATION_TOOLS)

    if not getattr(runtime_cls, "_athena_boot_consistency_v1_registered", False):
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

    _install_capability_basis(runtime_cls)
