"""ATHENA canonical MCP package registrations plus additive runtime extensions.

The exact v3.2.0 registration body is preserved in `_init_v32_legacy.py` and
executed in this package namespace. Current organs are installed additively so
historical registration lineage remains inspectable instead of being rewritten.
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

# Collective V14 advances only current release identity and the lazy scientific
# frontier; it leaves the preserved v3.2 registration body and later operational
# organs intact.
from .collective_v14_install import install_release_v14 as _install_release_v14

_install_release_v14(globals())
del _install_release_v14

# DEPLOYMENT-002 composes after V14 so initialize/manifest projections preserve
# the current release identity and scientific frontier. It extends existing
# PromptRuntime and AorDevelopmentSurface seams without replacing Server.
from .deployment_extension import install_deployment_extension

install_deployment_extension()

# NEXT V1→V5: rolling focus, staged preparation, exact prep-plan scouts,
# bounded slot allocation, then a read-only resource-vector scout economy.
# Allocation/economics may recommend claims but cannot create them, execute work,
# or acquire evidence/promotion authority.
from .next_quest_pipeline import install_next_pipeline_extension
from .next_quest_pipeline_hardening import install_next_pipeline_successor_authority_hardening
from .next_quest_pipeline_bridge import install_next_pipeline_bridge
from .next_quest_pipeline_breadth import install_next_pipeline_breadth
from .next_quest_pipeline_breadth_hardening import install_next_pipeline_breadth_idempotency_hardening
from .next_quest_scout import install_next_scout_extension
from .next_scout_allocation import install_next_scout_allocation_extension
from .next_scout_economy import install_next_scout_economy_extension

install_next_pipeline_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_pipeline_successor_authority_hardening()
install_next_pipeline_bridge(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_pipeline_breadth(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_pipeline_breadth_idempotency_hardening()
install_next_scout_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_scout_allocation_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_scout_economy_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
for _tool in PROMPT_RUNTIME_TOOLS:
    if not any(existing["name"] == _tool["name"] for existing in _protocol.TOOLS):
        _protocol.TOOLS.append(_tool)
