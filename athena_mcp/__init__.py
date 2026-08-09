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

from .agent_bootstrap_message_board import install_agent_bootstrap_message_board
from .agent_bootstrap_message_board_activation import install_agent_bootstrap_message_board_activation
install_agent_bootstrap_message_board(AgentBootstrapRuntime)
install_agent_bootstrap_message_board_activation(AgentBootstrapRuntime)

from .agent_bootstrap_cohesion_treatment import install_agent_bootstrap_cohesion_treatment
install_agent_bootstrap_cohesion_treatment(AgentBootstrapRuntime)

from .collective_v14_install import install_release_v14 as _install_release_v14
_install_release_v14(globals())
del _install_release_v14

from .deployment_extension import install_deployment_extension
install_deployment_extension()

# NEXT V1→V6: rolling focus, staged preparation, exact prep-plan scouts,
# bounded allocation, resource economics, observed-cost metabolism, then a
# calibrated-economy reader. Only cost priors learn from observed receipts;
# benefit priors remain V5 policy priors and no layer gains claim/promotion authority.
from .next_quest_pipeline import install_next_pipeline_extension
from .next_quest_pipeline_hardening import install_next_pipeline_successor_authority_hardening
from .next_quest_pipeline_bridge import install_next_pipeline_bridge
from .next_quest_pipeline_breadth import install_next_pipeline_breadth
from .next_quest_pipeline_breadth_hardening import install_next_pipeline_breadth_idempotency_hardening
from .next_quest_scout import install_next_scout_extension
from .next_scout_allocation import install_next_scout_allocation_extension
from .next_scout_economy import install_next_scout_economy_extension
from .next_scout_metabolism import install_next_scout_metabolism_extension
from .next_scout_calibrated_economy import install_next_scout_calibrated_economy_extension

install_next_pipeline_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_pipeline_successor_authority_hardening()
install_next_pipeline_bridge(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_pipeline_breadth(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_pipeline_breadth_idempotency_hardening()
install_next_scout_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_scout_allocation_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_scout_economy_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_scout_metabolism_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)
install_next_scout_calibrated_economy_extension(PromptRuntime, PROMPT_RUNTIME_TOOLS, PROMPT_RUNTIME_TOOL_NAMES)

for _tool in PROMPT_RUNTIME_TOOLS:
    if not any(existing["name"] == _tool["name"] for existing in _protocol.TOOLS):
        _protocol.TOOLS.append(_tool)
