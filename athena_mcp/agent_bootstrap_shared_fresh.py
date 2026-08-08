from __future__ import annotations

from .agent_bootstrap import AGENT_BOOT_TOOLS
from .prompt_remote import PromptRemoteSync

_MODES = {"REQUIRED", "BEST_EFFORT", "DISABLED"}


def _mode(value: str | None) -> str:
    mode = str(value or "BEST_EFFORT").upper()
    if mode not in _MODES:
        raise ValueError("shared_remote_mode must be REQUIRED, BEST_EFFORT, or DISABLED")
    return mode


def install_agent_bootstrap_shared_fresh(runtime_cls) -> None:
    """BOOT-003: shared Git freshness precedes every composite boot snapshot.

    The continuation extension may itself sync during index/handoff derivation, but
    that is too late to protect prompt/world fields already computed by the base
    bootstrap. This outer membrane synchronizes the current named branch first, so
    every address coordinate in the one-call packet is observed after the same
    shared Git freshness decision.
    """

    if getattr(runtime_cls, "_athena_boot_shared_fresh_v1_registered", False):
        return

    original_bootstrap = runtime_cls.bootstrap
    original_refresh = runtime_cls.refresh
    original_call_tool = runtime_cls.call_tool

    def _sync(self, remote: str, shared_remote_mode: str):
        mode = _mode(shared_remote_mode)
        if mode == "DISABLED":
            return mode, {
                "status": "DISABLED",
                "remote": remote,
                "shared_frontier_verified": False,
            }
        syncer = getattr(self, "_agent_bootstrap_prompt_remote_v1", None)
        if syncer is None:
            syncer = PromptRemoteSync(self.git)
            self._agent_bootstrap_prompt_remote_v1 = syncer
        return mode, syncer.sync(remote)

    def bootstrap_shared_fresh(
        self,
        *args,
        shared_remote_mode="BEST_EFFORT",
        **kwargs,
    ):
        override = getattr(self, "_agent_bootstrap_shared_mode_override", None)
        if override is not None and shared_remote_mode == "BEST_EFFORT":
            shared_remote_mode = override
        mode = _mode(shared_remote_mode)
        remote = kwargs.get("remote", "origin")
        mode, sync = _sync(self, remote, mode)

        # Unless continuation freshness was explicitly chosen, inherit the same
        # world-snapshot mode so one boot call does not claim two incompatible
        # shared-current standings.
        kwargs.setdefault("continuation_shared_remote_mode", mode)
        packet = original_bootstrap(self, *args, **kwargs)
        packet.setdefault("witnesses", {})["shared_git"] = sync
        packet["shared_frontier_verified"] = bool(sync.get("shared_frontier_verified"))
        packet["boot_shared_remote_mode"] = mode
        packet["boot_freshness_law"] = "BOOT_SYNC_SHARED_GIT_BEFORE_COMPOSITE_SNAPSHOT"
        packet.setdefault("laws", [])
        for law in (
            "ONE_CALL_BOOT != SKIP_FRESHNESS",
            "BOOT_SYNC_SHARED_GIT_BEFORE_COMPOSITE_SNAPSHOT",
            "LOCAL_BOOT_VIEW != SHARED_CURRENT_BOOT_VIEW",
        ):
            if law not in packet["laws"]:
                packet["laws"].append(law)

        if mode == "REQUIRED" and not packet["shared_frontier_verified"]:
            holds = set(str(x) for x in packet.get("holds") or [])
            holds.add("BOOTSTRAP_SHARED_FRONTIER_HOLD")
            packet["holds"] = sorted(holds)
            packet["status"] = "BOOTSTRAP_HOLD"
        elif (
            mode == "BEST_EFFORT"
            and not packet["shared_frontier_verified"]
            and packet.get("status") == "BOOTSTRAPPED"
        ):
            packet["status"] = "BOOTSTRAPPED_UNVERIFIED"

        session_id = packet.get("session_id")
        if session_id and hasattr(self, "_sessions") and session_id in self._sessions:
            self._sessions[session_id]["shared_remote_mode"] = mode
        return packet

    def refresh_shared_fresh(
        self,
        *args,
        shared_remote_mode=None,
        **kwargs,
    ):
        session_id = kwargs.get("session_id")
        remembered = self._sessions.get(session_id or "") if session_id and hasattr(self, "_sessions") else None
        if shared_remote_mode is None and remembered is not None:
            shared_remote_mode = remembered.get("shared_remote_mode")
        if shared_remote_mode is None:
            shared_remote_mode = "BEST_EFFORT"
        self._agent_bootstrap_shared_mode_override = _mode(shared_remote_mode)
        try:
            packet = original_refresh(self, *args, **kwargs)
        finally:
            self._agent_bootstrap_shared_mode_override = None
        session_id = packet.get("session_id") or session_id
        if session_id and hasattr(self, "_sessions") and session_id in self._sessions:
            self._sessions[session_id]["shared_remote_mode"] = _mode(shared_remote_mode)
        return packet

    def call_tool_shared_fresh(self, name: str, a: dict):
        if name == "athena_agent_bootstrap":
            return self.bootstrap(
                agent_id=a["agent_id"],
                task=a.get("task", ""),
                profile=a.get("profile"),
                source_ref=a.get("source_ref"),
                remote=a.get("remote", "origin"),
                fetch=a.get("fetch", True),
                issue_repo=a.get("issue_repo"),
                issue_limit=a.get("issue_limit", 10),
                continuation_loop_id=a.get("continuation_loop_id"),
                continuation_shared_remote_mode=a.get("continuation_shared_remote_mode"),
                shared_remote_mode=a.get("shared_remote_mode", "BEST_EFFORT"),
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
                shared_remote_mode=a.get("shared_remote_mode"),
            )
        return original_call_tool(self, name, a)

    runtime_cls.bootstrap = bootstrap_shared_fresh
    runtime_cls.refresh = refresh_shared_fresh
    runtime_cls.call_tool = call_tool_shared_fresh
    runtime_cls._athena_boot_shared_fresh_v1_registered = True

    for tool in AGENT_BOOT_TOOLS:
        props = (tool.get("inputSchema") or {}).setdefault("properties", {})
        props.setdefault(
            "shared_remote_mode",
            {"type": ["string", "null"], "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED", None]},
        )
        if tool.get("name") == "athena_agent_bootstrap":
            tool["description"] = (
                "Shared-sync the current Git branch first, then cold-start one AGENT_BOOT_V1 packet from prompt, "
                "frontier, issue, sibling, and continuation state. REQUIRED mode holds rather than returning a stale local snapshot."
            )
        elif tool.get("name") == "athena_agent_refresh":
            tool["description"] = (
                "Shared-sync before recomputing AGENT_BOOT_V1, then report factorized changed coordinates and affected cones."
            )
