"""ATHENA canonical MCP package release identity and runtime registrations.

`protocol.py` remains the mature schema registry. Package initialization owns the
release identity and patches compatibility surfaces before dispatch observes them.
Frontier V1 is registered as an explicit extension of the Git prompt runtime so it
reuses the existing MCP dispatcher rather than creating a second control plane.
"""

__version__ = "3.2.0"

from . import protocol as _protocol

SERVER_INFO = {
    "name": "athena-canonical-mcp",
    "version": __version__,
    "description": "Canonical KC144/JSPACE/SCALE developmental control with QMC/FITC probabilistic inference, bounded FCI-lite and longitudinal policy inference, and correlated robust resource planning",
}

_protocol.SERVER_INFO = dict(SERVER_INFO)

# Prompt × frontier braid registration.  The dispatcher already routes the
# PROMPT_RUNTIME_TOOL_NAMES family through PromptRuntime.call_tool, so frontier
# tools extend that family rather than duplicating dispatch/state/authority code.
from .prompt_runtime import PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES
from .frontier_runtime import FrontierRuntime, FRONTIER_TOOLS, FRONTIER_TOOL_NAMES

for _tool in FRONTIER_TOOLS:
    if _tool["name"] not in PROMPT_RUNTIME_TOOL_NAMES:
        PROMPT_RUNTIME_TOOLS.append(_tool)
        PROMPT_RUNTIME_TOOL_NAMES.add(_tool["name"])
    if not any(existing["name"] == _tool["name"] for existing in _protocol.TOOLS):
        _protocol.TOOLS.append(_tool)

if not getattr(PromptRuntime, "_athena_frontier_v1_registered", False):
    _prompt_call_without_frontier = PromptRuntime.call_tool

    def _prompt_call_with_frontier(self, name, arguments):
        if name in FRONTIER_TOOL_NAMES:
            runtime = getattr(self, "_frontier_runtime_v1", None)
            if runtime is None:
                runtime = FrontierRuntime(self.git, self)
                self._frontier_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return _prompt_call_without_frontier(self, name, arguments)

    PromptRuntime.call_tool = _prompt_call_with_frontier
    PromptRuntime._athena_frontier_v1_registered = True
