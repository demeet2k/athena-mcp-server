from __future__ import annotations

from .git_backend import GitBackend
from .prompt_runtime import PromptRuntime
from .rehydration_loop import RehydrationLoopRuntime
from .successor_baton import SuccessorBatonRuntime

ARTIFACT = "ATHENA.REHYDRATION.HANDOFF.DELTA.V1"

_STATUS_MAP = {
    "BATON_READY": "HANDOFF_READY",
    "SUCCESSOR_READY": "HANDOFF_SUCCESSOR_READY",
    "STALE_BATON_HOLD": "STALE_HANDOFF_HOLD",
    "STALE_BATON_AFTER_SYNC_HOLD": "STALE_HANDOFF_AFTER_SYNC_HOLD",
    "NO_TRANSITION_FULL_REHYDRATE_REQUIRED": "NO_TRANSITION_FULL_REHYDRATE_REQUIRED",
    "FULL_REHYDRATE_REQUIRED": "FULL_REHYDRATE_REQUIRED",
    "HEAD_MOVED_REHYDRATE_REQUIRED": "HEAD_MOVED_REHYDRATE_REQUIRED",
    "LIVE_COORDINATE_DRIFT_HOLD": "LIVE_COORDINATE_DRIFT_HOLD",
    "SHARED_FRONTIER_HOLD": "SHARED_FRONTIER_HOLD",
    "INTEGRITY_HOLD": "INTEGRITY_HOLD",
}


class RehydrationHandoffRuntime:
    """Public handoff-compression facade over the verified delta projection core.

    The sibling rehydration-successor operator answers WHAT NEXT. This operator
    answers WHAT THE NEXT AGENT MUST REHYDRATE. If a routing successor baton is
    already embedded in the durable completion receipt, it is transported as
    bound context without being re-scored or promoted to authority.
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
        self.core = SuccessorBatonRuntime(self.git, self.prompt_runtime, self.loop)

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

    def derive(self, loop_id: str) -> dict:
        core = self.core.derive(loop_id)
        packet = core.get("baton")
        routing = self._routing_successor(loop_id, core) if isinstance(packet, dict) else None
        result = {
            "artifact": ARTIFACT,
            "status": self._map_status(core.get("status")),
            "loop_id": loop_id,
            "handoff": packet,
            "handoff_digest": core.get("baton_digest"),
            "routing_successor": routing,
            "routing_successor_bound_by": (packet.get("transition") or {}).get("receipt_digest") if isinstance(packet, dict) and routing else None,
            "verification": core.get("verification"),
            "observation": core.get("observation"),
            "laws": [
                "WHAT_NEXT != WHAT_TO_REHYDRATE",
                "ROUTING_SUCCESSOR != HANDOFF_DELTA",
                "HANDOFF_DELTA != HIGHER_AUTHORITY",
                "DERIVED_HANDOFF != NEW_GIT_PROGRESS",
                "HANDOFF_IDENTITY != OBSERVER_FRESHNESS",
                "ROUTING_SUCCESSOR_IF_PRESENT_IS_RECEIPT_BOUND_CONTEXT",
            ],
        }
        return result

    def consume(
        self,
        *,
        loop_id: str,
        expected_handoff_digest: str,
        shared_remote_mode: str = "REQUIRED",
        include_full_prompt_on_change: bool = True,
        include_frontier_on_change: bool = True,
    ) -> dict:
        core = self.core.consume(
            loop_id=loop_id,
            expected_baton_digest=expected_handoff_digest,
            shared_remote_mode=shared_remote_mode,
            include_full_prompt_on_change=include_full_prompt_on_change,
            include_frontier_on_change=include_frontier_on_change,
        )
        derived = self.derive(loop_id)
        result = dict(core)
        result["artifact"] = ARTIFACT
        result["status"] = self._map_status(core.get("status"))
        result["handoff_digest"] = core.get("baton_digest") or expected_handoff_digest
        result.pop("baton_digest", None)
        result["routing_successor"] = derived.get("routing_successor")
        result["routing_successor_bound_by"] = derived.get("routing_successor_bound_by")
        laws = list(result.get("laws") or [])
        for law in (
            "WHAT_NEXT != WHAT_TO_REHYDRATE",
            "ROUTING_SUCCESSOR != HANDOFF_DELTA",
            "HANDOFF_DELTA != HIGHER_AUTHORITY",
        ):
            if law not in laws:
                laws.append(law)
        result["laws"] = laws
        return result

    def call_tool(self, name: str, arguments: dict):
        if name == "athena_rehydration_handoff_delta":
            return self.derive(arguments["loop_id"])
        if name == "athena_rehydration_handoff_resume":
            return self.consume(
                loop_id=arguments["loop_id"],
                expected_handoff_digest=arguments["expected_handoff_digest"],
                shared_remote_mode=arguments.get("shared_remote_mode", "REQUIRED"),
                include_full_prompt_on_change=arguments.get("include_full_prompt_on_change", True),
                include_frontier_on_change=arguments.get("include_frontier_on_change", True),
            )
        raise KeyError(name)


REHYDRATION_HANDOFF_TOOLS = [
    {
        "name": "athena_rehydration_handoff_delta",
        "description": "Derive a read-only, content-addressed handoff delta from the latest verified rehydration transition, describing what a successor agent must rehydrate. This is distinct from successor task routing.",
        "inputSchema": {
            "type": "object",
            "required": ["loop_id"],
            "properties": {"loop_id": {"type": "string"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_rehydration_handoff_resume",
        "description": "Consume an exact handoff delta, refresh shared state, reject drift, and hydrate only the affected dependency cone. Falls back to full rehydration when delta coverage is insufficient.",
        "inputSchema": {
            "type": "object",
            "required": ["loop_id", "expected_handoff_digest"],
            "properties": {
                "loop_id": {"type": "string"},
                "expected_handoff_digest": {"type": "string"},
                "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
                "include_full_prompt_on_change": {"type": "boolean"},
                "include_frontier_on_change": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
]
REHYDRATION_HANDOFF_TOOL_NAMES = {tool["name"] for tool in REHYDRATION_HANDOFF_TOOLS}
