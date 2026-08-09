from __future__ import annotations

from .agent_bootstrap import AGENT_BOOT_TOOLS

_WORK_ID_FIELDS = ("work_key", "targets", "coordination_claim_mode")
_LAWS = [
    "BOOT_OBSERVATION != WORK_START",
    "TOOL_BOOT_DEFAULT => MESSAGE_BOARD_HANDSHAKE",
    "IMPLICIT_TASK_ONLY_BOOT != PRIMARY_CLAIM",
    "EXPLICIT_WORK_ID_OR_EXPLICIT_AUTO => CLAIM_INTENT",
    "DIRECT_PYTHON_BOOT != IMPLICIT_SHARED_MUTATION",
]


def _has_explicit_work_identity(arguments: dict) -> bool:
    work_key = str(arguments.get("work_key") or "").strip()
    if work_key:
        return True
    if any(str(value or "").strip() for value in (arguments.get("targets") or [])):
        return True
    if arguments.get("coordination_claim_mode") is not None:
        return True
    return False


def _annotate(packet: dict, resolution: str | None) -> dict:
    if not resolution or not isinstance(packet, dict):
        return packet
    coordination = packet.get("coordination")
    if isinstance(coordination, dict):
        coordination["requested_mode"] = "AUTO"
        coordination["auto_resolution"] = resolution
    laws = packet.setdefault("laws", [])
    for law in _LAWS:
        if law not in laws:
            laws.append(law)
    return packet


def install_agent_bootstrap_message_board_activation(runtime_cls) -> None:
    """Separate tool-default activation policy from the Message Board mechanism.

    Direct Python method calls remain non-mutating by default. The MCP/tool surface
    performs an automatic handshake: task-only observation is READ_ONLY, while an
    explicit work identity means the caller is crossing the start-work boundary and
    AUTO may establish/reuse/renew Message Board presence. Explicit
    coordination_mode always wins.
    """

    if getattr(runtime_cls, "_athena_boot_message_board_activation_v1_registered", False):
        return

    inner_bootstrap = runtime_cls.bootstrap
    inner_call_tool = runtime_cls.call_tool

    def bootstrap_activation(self, *args, coordination_mode=None, **kwargs):
        # Python callers historically used bootstrap as a pure composite read. Keep
        # that API side-effect free unless they explicitly opt into coordination.
        resolved = coordination_mode if coordination_mode is not None else "DISABLED"
        return inner_bootstrap(
            self, *args, coordination_mode=resolved, **kwargs
        )

    def call_tool_activation(self, name: str, arguments: dict):
        if name not in {"athena_agent_bootstrap", "athena_agent_refresh"}:
            return inner_call_tool(self, name, arguments)

        args = dict(arguments or {})
        explicit_mode = args.get("coordination_mode") is not None
        resolution = None

        if not explicit_mode:
            if _has_explicit_work_identity(args):
                args["coordination_mode"] = "AUTO"
                resolution = "CLAIM_EXPLICIT_WORK_ID"
            elif name == "athena_agent_bootstrap":
                # Boot can be an observer/reconstructor. Reading the board is the
                # automatic handshake; creating a claim requires start-work intent.
                args["coordination_mode"] = "READ_ONLY"
                resolution = "READ_ONLY_NO_EXPLICIT_WORK_ID"
            # Refresh without new work coordinates inherits the session's prior
            # coordination config. A READ_ONLY observer stays an observer; a
            # claimed worker keeps/reuses its claim.

        value = inner_call_tool(self, name, args)
        return _annotate(value, resolution)

    runtime_cls.bootstrap = bootstrap_activation
    runtime_cls.call_tool = call_tool_activation
    runtime_cls._athena_boot_message_board_activation_v1_registered = True

    for tool in AGENT_BOOT_TOOLS:
        if tool.get("name") == "athena_agent_bootstrap":
            tool["description"] = (
                "Cold-start AGENT_BOOT_V1 with an automatic Message Board handshake. "
                "A task-only tool call observes shared-current coordination without "
                "claiming work; explicit work_key/targets/claim mode or explicit "
                "coordination_mode=AUTO crosses the start-work boundary and may "
                "establish/reuse presence. Duplicate claimed work holds."
            )
        elif tool.get("name") == "athena_agent_refresh":
            tool["description"] = (
                "Refresh AGENT_BOOT_V1 and its Message Board projection. Existing "
                "session coordination intent is preserved; new explicit work "
                "coordinates activate AUTO claiming, while observer sessions remain "
                "read-only unless promoted deliberately."
            )
