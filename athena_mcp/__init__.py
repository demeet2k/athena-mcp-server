"""ATHENA canonical MCP package registrations plus Message Board V1.

The exact v3.2.0 registration body preceding Message Board V1 is preserved in
`_init_v32_legacy.py` and executed in this package namespace. Keeping that body
byte-identical makes this extension additive instead of reimplementing the
existing frontier/rehydration/bootstrap compatibility stack.
"""

from pathlib import Path as _Path

_legacy_init = _Path(__file__).with_name("_init_v32_legacy.py")
exec(compile(_legacy_init.read_text(encoding="utf-8"), str(_legacy_init), "exec"), globals(), globals())

del _legacy_init

from .message_board import MESSAGE_BOARD_TOOLS, MESSAGE_BOARD_TOOL_NAMES, MessageBoardRuntime

for _tool in MESSAGE_BOARD_TOOLS:
    if _tool["name"] not in PROMPT_RUNTIME_TOOL_NAMES:
        PROMPT_RUNTIME_TOOLS.append(_tool)
        PROMPT_RUNTIME_TOOL_NAMES.add(_tool["name"])
    if not any(existing["name"] == _tool["name"] for existing in _protocol.TOOLS):
        _protocol.TOOLS.append(_tool)

if not getattr(PromptRuntime, "_athena_message_board_v1_registered", False):
    _prompt_call_without_message_board = PromptRuntime.call_tool

    def _prompt_call_with_message_board(self, name, arguments):
        if name in MESSAGE_BOARD_TOOL_NAMES:
            runtime = getattr(self, "_message_board_runtime_v1", None)
            if runtime is None:
                runtime = MessageBoardRuntime(self.git)
                self._message_board_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return _prompt_call_without_message_board(self, name, arguments)

    PromptRuntime.call_tool = _prompt_call_with_message_board
    PromptRuntime._athena_message_board_v1_registered = True

# BOOT-MB-001: Message Board is the sole coordination authority. Install the
# mechanism first, then the activation policy that distinguishes observing a
# boot context from actually starting a mutable work lane.
from .agent_bootstrap_message_board import install_agent_bootstrap_message_board
from .agent_bootstrap_message_board_activation import (
    install_agent_bootstrap_message_board_activation,
)

install_agent_bootstrap_message_board(AgentBootstrapRuntime)
install_agent_bootstrap_message_board_activation(AgentBootstrapRuntime)

# BOOT-C3-001: deterministic BOOT-MB holds receive a read-only Cohesion C3-11
# treatment projection. Install after BOOT-MB activation so this wrapper can
# observe final pre-dispatch standing without changing claim authority.
from .agent_bootstrap_cohesion_treatment import (
    install_agent_bootstrap_cohesion_treatment,
)

install_agent_bootstrap_cohesion_treatment(AgentBootstrapRuntime)

# DEPLOYMENT-002: compose digest/source-bound activation through the current
# PromptRuntime + AorDevelopmentSurface seams. The canonical Server root remains
# unchanged; deployment planning and receipt verification grant no execution or
# truth authority.
from .deployment_extension import install_deployment_extension

install_deployment_extension()
