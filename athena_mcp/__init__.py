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

# Collective V14 preserves the historical registration body and installs the
# joint scientific-control frontier inherited by V15.
from .collective_v14_install import install_release_v14 as _install_release_v14

_install_release_v14(globals())
del _install_release_v14

# DEPLOYMENT-002 is a separately typed operational/hosting organ inherited from
# live master. It composes after V14 and before V15 so its prompt/AOR/dispatch
# seams are retained while V15 remains the final current release identity.
from .deployment_extension import install_deployment_extension

install_deployment_extension()

# CUTOVER-HOLD-001 binds the deployment plan, isolated-canary witness, supplied
# single-writer quiescence observation, CAS base, snapshot, and opaque authority
# reference into a replayable non-effectful packet. It deliberately stops before
# any writer, state, secret, cluster, or traffic transition.
from .deployment_cutover_extension import install_deployment_cutover_extension

install_deployment_cutover_extension()

# Collective V15 advances only the current release identity and calibrated
# successor frontier. Deployment, Message Board, cohesion, party and prompt
# organs remain separately typed and intact.
from .collective_v15_install import install_release_v15 as _install_release_v15

_install_release_v15(globals())
del _install_release_v15

# LBM-001/1.1 is an additive candidate communication organ after the current
# V15 + V3.4 + CUTOVER_HOLD frontier. Automatic tool-crossing sharing remains
# opt-in. The imported Beacon blobs below are byte-identical to the previously
# qualified V1.1 candidate; this composition adds no new Beacon semantics.
from .liminal_beacon_mesh import LiminalBeaconMeshRuntime
from .liminal_beacon_mesh_identity import install_liminal_beacon_identity
from .liminal_beacon_mesh_backpressure_v11 import (
    install_liminal_beacon_backpressure_v11,
)
from .liminal_beacon_mesh_scope import install_liminal_beacon_scope
from .liminal_beacon_mesh_semantic_v11 import install_liminal_beacon_semantic_v11
from .liminal_beacon_mesh_extension import install_liminal_beacon_mesh

install_liminal_beacon_identity(LiminalBeaconMeshRuntime)
install_liminal_beacon_backpressure_v11(LiminalBeaconMeshRuntime)
install_liminal_beacon_scope(LiminalBeaconMeshRuntime)
install_liminal_beacon_semantic_v11(LiminalBeaconMeshRuntime)
install_liminal_beacon_mesh()
