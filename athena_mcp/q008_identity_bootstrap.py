from __future__ import annotations

from . import protocol as _protocol
from .omega29_q008_bridge import bridge
from .q008_invocation_identity import compile_transition
from .prompt_runtime import PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES, PromptRuntime

BRIDGE_TOOL_NAME = "athena_omega29_q008_bridge"
IDENTITY_TOOL_NAME = "athena_q008_identity_compile"
Q008_IDENTITY_TOOL_NAMES = {BRIDGE_TOOL_NAME, IDENTITY_TOOL_NAME}

BRIDGE_TOOL = {
    "name": BRIDGE_TOOL_NAME,
    "description": (
        "Recompute and bind an Ω29 V2 decision to an exact Q008 local terminal state and cursor. "
        "The result remains pending for a distinct idempotent consumer invocation and performs no mutation."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "omega_packet": {"type": "object"}, "source_binding": {"type": "object"},
            "runtime_context": {"type": "object"}, "omega_decision": {"type": "object"},
            "q008_terminal": {"type": "string", "enum": ["CHECKPOINT_CONTINUE", "READY_TO_CLOSE", "REJECTED_EARLY_EXIT", "BLOCKED_EXTERNAL", "HOST_CUTOFF_PENDING"]},
            "terminal_attempt": {"type": "boolean"},
            "cursor": {
                "type": "object",
                "properties": {
                    "invocation_index": {"type": "integer", "minimum": 0},
                    "segment_index": {"type": "integer", "minimum": 0},
                    "checkpoint_index": {"type": "integer", "minimum": 0},
                },
                "required": ["invocation_index", "segment_index", "checkpoint_index"],
                "additionalProperties": False,
            },
            "run_id": {"type": "string", "minLength": 1},
            "invocation_id": {"type": "string", "minLength": 1},
        },
        "required": ["omega_packet", "source_binding", "runtime_context", "omega_decision", "q008_terminal", "terminal_attempt", "cursor", "run_id", "invocation_id"],
        "additionalProperties": False,
    },
}

IDENTITY_TOOL = {
    "name": IDENTITY_TOOL_NAME,
    "description": (
        "Compile one pure Q008 consumer transition into invocation-bound cursor, event, receipt, abort-set, "
        "optional provider-observation receipt, and identity-closure receipt. Identity closure is not execution, admission, promotion, or provider-effect proof."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "bridge": {"type": "object"},
            "consumer_invocation_id": {"type": "string", "minLength": 1},
            "move": {"type": "string", "enum": ["NONE", "CHECKPOINT", "SEGMENT"]},
            "event_index": {"type": "integer", "minimum": 0},
            "event_type": {"type": "string", "enum": ["CONSUMER_OPEN", "CHECKPOINT_RECORDED", "SEGMENT_ADVANCED", "ABORT_RECORDED", "PROVIDER_OBSERVED", "TERMINAL_CANDIDATE"]},
            "payload_digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "decision": {"type": "string", "enum": ["CONTINUE", "HOLD", "ABORT", "COMPLETE_CANDIDATE", "PROVIDER_OBSERVED"]},
            "abort_reasons": {"type": "array", "items": {"type": "string", "minLength": 1}, "default": []},
            "provider_observation": {
                "type": ["object", "null"],
                "properties": {
                    "provider": {"type": "string", "minLength": 1},
                    "provider_operation_id": {"type": "string", "minLength": 1},
                    "observation_id": {"type": "string", "minLength": 1},
                    "request_digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "observation_digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "observed_state": {"type": "string", "minLength": 1},
                },
                "required": ["provider", "provider_operation_id", "observation_id", "request_digest", "observation_digest", "observed_state"],
                "additionalProperties": False,
            },
        },
        "required": ["bridge", "consumer_invocation_id", "move", "event_index", "event_type", "payload_digest", "decision"],
        "additionalProperties": False,
    },
}


def install() -> None:
    for tool in (BRIDGE_TOOL, IDENTITY_TOOL):
        if tool["name"] not in PROMPT_RUNTIME_TOOL_NAMES:
            PROMPT_RUNTIME_TOOLS.append(dict(tool)); PROMPT_RUNTIME_TOOL_NAMES.add(tool["name"])
        if not any(item.get("name") == tool["name"] for item in _protocol.TOOLS):
            _protocol.TOOLS.append(dict(tool))

    flag = "_athena_q008_identity_boundary_v1_registered"
    if getattr(PromptRuntime, flag, False):
        return
    original_call_tool = PromptRuntime.call_tool

    def call_tool_with_q008_identity(self, name: str, arguments: dict):
        if name == BRIDGE_TOOL_NAME:
            return bridge(**arguments)
        if name == IDENTITY_TOOL_NAME:
            return compile_transition(
                arguments["bridge"],
                consumer_invocation_id=arguments["consumer_invocation_id"],
                move=arguments["move"], event_index=arguments["event_index"],
                event_type=arguments["event_type"], payload_digest=arguments["payload_digest"],
                decision=arguments["decision"], abort_reasons=arguments.get("abort_reasons", ()),
                provider_observation=arguments.get("provider_observation"),
            )
        return original_call_tool(self, name, arguments)

    PromptRuntime.call_tool = call_tool_with_q008_identity
    setattr(PromptRuntime, flag, True)
