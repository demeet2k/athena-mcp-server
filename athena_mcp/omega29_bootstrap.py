from __future__ import annotations

from . import protocol as _protocol
from .omega29_operate import decide
from .prompt_runtime import PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES, PromptRuntime

TOOL_NAME = "athena_omega29_operate"

OMEGA29_OPERATE_TOOL = {
    "name": TOOL_NAME,
    "description": (
        "Classify an Ω29 plan/execution/world-state evidence packet against caller-supplied, "
        "content-addressed source and clock observations. This pure reducer cannot establish "
        "source freshness, mutate providers, admit evidence, promote state, or authorize execution."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "packet": {"type": "object"},
            "source_binding": {"type": "object"},
            "runtime_context": {"type": "object"},
        },
        "required": ["packet", "source_binding", "runtime_context"],
        "additionalProperties": False,
    },
}


def install() -> None:
    if TOOL_NAME not in PROMPT_RUNTIME_TOOL_NAMES:
        PROMPT_RUNTIME_TOOLS.append(dict(OMEGA29_OPERATE_TOOL))
        PROMPT_RUNTIME_TOOL_NAMES.add(TOOL_NAME)
    if not any(tool.get("name") == TOOL_NAME for tool in _protocol.TOOLS):
        _protocol.TOOLS.append(dict(OMEGA29_OPERATE_TOOL))

    flag = "_athena_omega29_operate_v2_registered"
    if getattr(PromptRuntime, flag, False):
        return
    original_call_tool = PromptRuntime.call_tool

    def call_tool_with_omega29(self, name: str, arguments: dict):
        if name == TOOL_NAME:
            return decide(
                arguments["packet"],
                source_binding=arguments["source_binding"],
                runtime_context=arguments["runtime_context"],
            )
        return original_call_tool(self, name, arguments)

    PromptRuntime.call_tool = call_tool_with_omega29
    setattr(PromptRuntime, flag, True)
