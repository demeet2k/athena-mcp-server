from __future__ import annotations

from .git_backend import GitBackend
from .prompt_runtime import PromptRuntime
from .rehydration_loop import RehydrationLoopRuntime
from .successor_baton import SuccessorBatonRuntime

ARTIFACT = "ATHENA.REHYDRATION.HANDOFF.DELTA.V1"

_STATUS_MAP = {
    "BATON_READY": "HANDOFF_READY",
    "SUCCESSOR_READY": "HANDOFF_RESUME_READY",
    "STALE_BATON_HOLD": "STALE_HANDOFF_HOLD",
    "STALE_BATON_AFTER_SYNC_HOLD": "STALE_HANDOFF_AFTER_SYNC_HOLD",
    "NO_TRANSITION_FULL_REHYDRATE_REQUIRED": "NO_TRANSITION_FULL_REHYDRATE_REQUIRED",
    "FULL_REHYDRATE_REQUIRED": "FULL_REHYDRATE_REQUIRED",
    "HEAD_MOVED_REHYDRATE_REQUIRED": "HEAD_MOVED_REHYDRATE_REQUIRED",
    "LIVE_COORDINATE_DRIFT_HOLD": "LIVE_COORDINATE_DRIFT_HOLD",
    "SHARED_FRONTIER_HOLD": "SHARED_FRONTIER_HOLD",
    "INTEGRITY_HOLD": "INTEGRITY_HOLD",
}


class _LocalVerifiedLoopView:
    """Local-read view used only after the public handoff membrane handles sync.

    PR #48 makes verify/resume/index shared-fresh by default. The handoff facade
    performs that shared read membrane explicitly so the projection core can then
    replay the already-fetched local tip without causing a second, differently
    configured freshness decision.
    """

    def __init__(self, loop: RehydrationLoopRuntime):
        self._loop = loop

    def verify(self, loop_id: str):
        return self._loop.verify(loop_id, shared_remote_mode="DISABLED")

    def resume(self, loop_id: str, include_prompt: bool = True):
        return self._loop.resume(loop_id, include_prompt=include_prompt, shared_remote_mode="DISABLED")

    def __getattr__(self, name):
        return getattr(self._loop, name)


class RehydrationHandoffRuntime:
    """Public shared-fresh handoff compression over the verified delta core.

    The sibling rehydration-successor operator answers WHAT NEXT. This operator
    answers WHAT THE NEXT AGENT MUST REHYDRATE. If a routing successor baton is
    embedded in the durable completion receipt, it is transported as receipt-bound
    context without being re-scored or promoted to authority.
    """

    def __init__(
        self,
        git: GitBackend,
        prompt_runtime: PromptRuntime | None = None,
        rehydration_runtime: RehydrationLoopRuntime | None = None,
    ):
        self.git = git
        self.prompt_runtime = prompt_runtime or PromptRuntime(git)
        self.loop = rehydration_runtime or RehydrationLoopRuntime(git, self.prompt_runtime)
        self.core = SuccessorBatonRuntime(
            self.git,
            self.prompt_runtime,
            _LocalVerifiedLoopView(self.loop),
        )

    @staticmethod
    def _mode(value: str | None) -> str:
        mode = str(value or "REQUIRED").upper()
        if mode not in {"REQUIRED", "BEST_EFFORT", "DISABLED"}:
            raise ValueError("shared_remote_mode must be REQUIRED, BEST_EFFORT, or DISABLED")
        return mode

    def _sync_before_read(self, shared_remote_mode: str, remote: str) -> tuple[str, dict]:
        mode = self._mode(shared_remote_mode)
        if mode == "DISABLED":
            return mode, {
                "status": "DISABLED",
                "remote": remote,
                "shared_frontier_verified": False,
            }
        sync = self.loop.remote_sync.sync(remote)
        if mode == "REQUIRED" and not sync.get("shared_frontier_verified"):
            return mode, sync
        return mode, sync

    def _routing_successor(self, loop_id: str, core_result: dict) -> dict | None:
        packet = core_result.get("baton") or {}
        receipt_path = (packet.get("transition") or {}).get("receipt_path")
        if not receipt_path:
            return None
        try:
            receipt = self.loop._read_json(receipt_path)
        except Exception:
            return None
        completion = receipt.get("completion") or {}
        value = completion.get("successor_baton")
        return value if isinstance(value, dict) else None

    @staticmethod
    def _map_status(value: str | None) -> str | None:
        return _STATUS_MAP.get(str(value), value)

    def _derive_local(self, loop_id: str, remote_sync: dict, mode: str) -> dict:
        core = self.core.derive(loop_id)
        packet = core.get("baton")
        routing = self._routing_successor(loop_id, core) if isinstance(packet, dict) else None
        status = self._map_status(core.get("status"))
        shared_verified = bool(remote_sync.get("shared_frontier_verified"))
        if mode == "BEST_EFFORT" and not shared_verified and status == "HANDOFF_READY":
            status = "HANDOFF_READY_UNVERIFIED"
        return {
            "artifact": ARTIFACT,
            "status": status,
            "loop_id": loop_id,
            "handoff": packet,
            "handoff_digest": core.get("baton_digest"),
            "routing_successor": routing,
            "routing_successor_bound_by": (packet.get("transition") or {}).get("receipt_digest") if isinstance(packet, dict) and routing else None,
            "verification": core.get("verification"),
            "observation": core.get("observation"),
            "remote_sync": remote_sync,
            "shared_frontier_verified": shared_verified,
            "freshness_law": "HANDOFF_SYNC_SHARED_GIT_BEFORE_VERIFYING_TRANSITION",
            "laws": [
                "WHAT_NEXT != WHAT_TO_REHYDRATE",
                "ROUTING_SUCCESSOR != HANDOFF_DELTA",
                "HANDOFF_DELTA != HIGHER_AUTHORITY",
                "DERIVED_HANDOFF != NEW_GIT_PROGRESS",
                "HANDOFF_IDENTITY != OBSERVER_FRESHNESS",
                "ROUTING_SUCCESSOR_IF_PRESENT_IS_RECEIPT_BOUND_CONTEXT",
                "LOCAL_HANDOFF_VIEW != SHARED_CURRENT_HANDOFF_VIEW",
            ],
        }

    def derive(
        self,
        loop_id: str,
        *,
        shared_remote_mode: str = "REQUIRED",
        remote: str = "origin",
    ) -> dict:
        mode, sync = self._sync_before_read(shared_remote_mode, remote)
        if mode == "REQUIRED" and not sync.get("shared_frontier_verified"):
            return {
                "artifact": ARTIFACT,
                "status": "HANDOFF_SHARED_FRONTIER_HOLD",
                "loop_id": loop_id,
                "handoff": None,
                "handoff_digest": None,
                "remote_sync": sync,
                "shared_frontier_verified": False,
                "freshness_law": "HANDOFF_SYNC_SHARED_GIT_BEFORE_VERIFYING_TRANSITION",
                "laws": ["LOCAL_HANDOFF_VIEW != SHARED_CURRENT_HANDOFF_VIEW"],
            }
        return self._derive_local(loop_id, sync, mode)

    def consume(
        self,
        *,
        loop_id: str,
        expected_handoff_digest: str,
        shared_remote_mode: str = "REQUIRED",
        remote: str = "origin",
        include_full_prompt_on_change: bool = True,
        include_frontier_on_change: bool = True,
    ) -> dict:
        before = self.derive(
            loop_id,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
        current_digest = before.get("handoff_digest")
        if current_digest != expected_handoff_digest:
            return {
                "artifact": ARTIFACT,
                "status": "STALE_HANDOFF_HOLD",
                "expected_handoff_digest": expected_handoff_digest,
                "current_handoff_digest": current_digest,
                "detail": before,
                "durable_return": False,
                "laws": ["HANDOFF_DIGEST_MISMATCH => HOLD"],
            }
        if before.get("status") not in {"HANDOFF_READY", "HANDOFF_READY_UNVERIFIED"}:
            fallback = self.loop.resume(
                loop_id,
                include_prompt=True,
                shared_remote_mode=shared_remote_mode,
                remote=remote,
            )
            return {
                "artifact": ARTIFACT,
                "status": before.get("status"),
                "handoff_digest": expected_handoff_digest,
                "handoff": before.get("handoff"),
                "fallback": fallback,
                "remote_sync": before.get("remote_sync"),
                "durable_return": False,
                "laws": before.get("laws") or [],
            }

        # A second shared read closes the race between handoff derivation and
        # actual consumption. If the sibling frontier advanced, the re-derived
        # handoff or exact-tip observation changes and consumption holds.
        after = self.derive(
            loop_id,
            shared_remote_mode=shared_remote_mode,
            remote=remote,
        )
        if after.get("handoff_digest") != expected_handoff_digest:
            return {
                "artifact": ARTIFACT,
                "status": "STALE_HANDOFF_AFTER_SYNC_HOLD",
                "expected_handoff_digest": expected_handoff_digest,
                "current_handoff_digest": after.get("handoff_digest"),
                "detail": after,
                "durable_return": False,
                "laws": ["HEAD_CHANGE => REHYDRATE"],
            }
        if after.get("status") not in {"HANDOFF_READY", "HANDOFF_READY_UNVERIFIED"}:
            fallback = self.loop.resume(
                loop_id,
                include_prompt=True,
                shared_remote_mode=shared_remote_mode,
                remote=remote,
            )
            return {
                "artifact": ARTIFACT,
                "status": after.get("status"),
                "handoff_digest": expected_handoff_digest,
                "handoff": after.get("handoff"),
                "fallback": fallback,
                "remote_sync": after.get("remote_sync"),
                "durable_return": False,
                "laws": after.get("laws") or [],
            }

        core = self.core.consume(
            loop_id=loop_id,
            expected_baton_digest=expected_handoff_digest,
            shared_remote_mode="DISABLED",
            include_full_prompt_on_change=include_full_prompt_on_change,
            include_frontier_on_change=include_frontier_on_change,
        )
        result = dict(core)
        result["artifact"] = ARTIFACT
        result["status"] = self._map_status(core.get("status"))
        result["handoff_digest"] = core.get("baton_digest") or expected_handoff_digest
        result.pop("baton_digest", None)
        if "successor_prompt" in result:
            result["handoff_prompt"] = result.pop("successor_prompt")
        compression = result.get("compression")
        if isinstance(compression, dict) and "successor_delta_prompt_chars" in compression:
            compression = dict(compression)
            compression["handoff_delta_prompt_chars"] = compression.pop("successor_delta_prompt_chars")
            result["compression"] = compression
        result["routing_successor"] = after.get("routing_successor")
        result["routing_successor_bound_by"] = after.get("routing_successor_bound_by")
        result["remote_sync"] = after.get("remote_sync")
        result["shared_frontier_verified"] = after.get("shared_frontier_verified")
        result["freshness_law"] = after.get("freshness_law")
        if self._mode(shared_remote_mode) != "DISABLED":
            result["durable_return"] = bool(after.get("shared_frontier_verified"))
        laws = list(result.get("laws") or [])
        for law in (
            "WHAT_NEXT != WHAT_TO_REHYDRATE",
            "ROUTING_SUCCESSOR != HANDOFF_DELTA",
            "HANDOFF_DELTA != HIGHER_AUTHORITY",
            "HANDOFF_SYNC_SHARED_GIT_BEFORE_VERIFYING_TRANSITION",
        ):
            if law not in laws:
                laws.append(law)
        result["laws"] = laws
        return result

    def call_tool(self, name: str, arguments: dict):
        if name == "athena_rehydration_handoff_delta":
            return self.derive(
                arguments["loop_id"],
                shared_remote_mode=arguments.get("shared_remote_mode", "REQUIRED"),
                remote=arguments.get("remote", "origin"),
            )
        if name == "athena_rehydration_handoff_resume":
            return self.consume(
                loop_id=arguments["loop_id"],
                expected_handoff_digest=arguments["expected_handoff_digest"],
                shared_remote_mode=arguments.get("shared_remote_mode", "REQUIRED"),
                remote=arguments.get("remote", "origin"),
                include_full_prompt_on_change=arguments.get("include_full_prompt_on_change", True),
                include_frontier_on_change=arguments.get("include_frontier_on_change", True),
            )
        raise KeyError(name)


REHYDRATION_HANDOFF_TOOLS = [
    {
        "name": "athena_rehydration_handoff_delta",
        "description": "Fresh-sync the shared Git branch, then derive a read-only, content-addressed handoff delta describing what a successor agent must rehydrate. Distinct from successor task routing.",
        "inputSchema": {
            "type": "object",
            "required": ["loop_id"],
            "properties": {
                "loop_id": {"type": "string"},
                "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
                "remote": {"type": "string"}
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_rehydration_handoff_resume",
        "description": "Fresh-sync and consume an exact handoff delta, reject drift, and hydrate only the affected dependency cone. Falls back to full rehydration when delta coverage is insufficient.",
        "inputSchema": {
            "type": "object",
            "required": ["loop_id", "expected_handoff_digest"],
            "properties": {
                "loop_id": {"type": "string"},
                "expected_handoff_digest": {"type": "string"},
                "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
                "remote": {"type": "string"},
                "include_full_prompt_on_change": {"type": "boolean"},
                "include_frontier_on_change": {"type": "boolean"}
            },
            "additionalProperties": False,
        },
    },
]
REHYDRATION_HANDOFF_TOOL_NAMES = {tool["name"] for tool in REHYDRATION_HANDOFF_TOOLS}
