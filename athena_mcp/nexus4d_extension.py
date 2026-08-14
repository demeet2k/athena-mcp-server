from __future__ import annotations

"""Additive NEXUS-4D installation on the canonical single-Server runtime.

The installer uses the established AorDevelopmentSurface composition seam. It
adds one resident durable organ, mutates the shared MCP tool/resource registries,
and exposes the organ in benchmark, surface-contract, composition and unified
manifest views without subclassing or replacing Server.
"""

import json

from .nexus4d import Nexus4dRuntime, VERSION
from .nexus4d_protocol import (
    NEXUS4D_RESOURCES,
    NEXUS4D_RESOURCE_URIS,
    NEXUS4D_TOOLS,
    NEXUS4D_TOOL_NAMES,
)


def install_nexus4d_extension() -> None:
    from . import protocol
    from .aor_development_surface import (
        AOR_DEVELOPMENT_RESOURCES,
        AOR_DEVELOPMENT_RESOURCE_URIS,
        AOR_DEVELOPMENT_TOOLS,
        AOR_DEVELOPMENT_TOOL_NAMES,
        AorDevelopmentSurface,
    )

    if getattr(AorDevelopmentSurface, "_athena_nexus4d_v1_registered", False):
        return

    for tool in NEXUS4D_TOOLS:
        if tool["name"] not in AOR_DEVELOPMENT_TOOL_NAMES:
            AOR_DEVELOPMENT_TOOLS.append(tool)
            AOR_DEVELOPMENT_TOOL_NAMES.add(tool["name"])
        if not any(existing["name"] == tool["name"] for existing in protocol.TOOLS):
            protocol.TOOLS.append(tool)

    known_resources = {resource["uri"] for resource in AOR_DEVELOPMENT_RESOURCES}
    for resource in NEXUS4D_RESOURCES:
        if resource["uri"] not in known_resources:
            AOR_DEVELOPMENT_RESOURCES.append(resource)
            known_resources.add(resource["uri"])
        AOR_DEVELOPMENT_RESOURCE_URIS.add(resource["uri"])

    previous_init = AorDevelopmentSurface.__init__

    def init_with_nexus4d(self, server):
        previous_init(self, server)
        self.nexus4d = Nexus4dRuntime(server.store, server.authority)

    AorDevelopmentSurface.__init__ = init_with_nexus4d

    previous_call = AorDevelopmentSurface.call_tool

    def call_with_nexus4d(self, name, args):
        if name == "athena_nexus_compile":
            return True, self.nexus4d.compile(args["spec"], args.get("machine_id"), args.get("actor", "agent"))
        if name == "athena_nexus_plan":
            return True, self.nexus4d.plan(args["machine_id"], args.get("expected_revision"), args.get("max_nodes"), args.get("max_cost"))
        if name == "athena_nexus_advance":
            return True, self.nexus4d.advance(args["machine_id"], args["expected_revision"], args["events"], args.get("actor", "agent"))
        if name == "athena_nexus_state":
            return True, self.nexus4d.state(args["machine_id"])
        if name == "athena_nexus_replay":
            return True, self.nexus4d.replay(args["machine_id"])
        if name == "athena_nexus_terminal":
            return True, self.nexus4d.terminal(args["machine_id"])
        if name == "athena_nexus_recent":
            return True, self.nexus4d.recent(args.get("limit", 50))
        return previous_call(self, name, args)

    AorDevelopmentSurface.call_tool = call_with_nexus4d

    previous_resource_read = AorDevelopmentSurface.read_resource

    def resource_read_with_nexus4d(self, uri):
        if uri in NEXUS4D_RESOURCE_URIS:
            return self.nexus4d.describe()
        return previous_resource_read(self, uri)

    AorDevelopmentSurface.read_resource = resource_read_with_nexus4d

    previous_benchmark = AorDevelopmentSurface.benchmark

    def benchmark_with_nexus4d(self):
        result = previous_benchmark(self)
        result.update(self.nexus4d.benchmark())
        return result

    AorDevelopmentSurface.benchmark = benchmark_with_nexus4d

    # Require the newly installed organ in live surface and composition audits.
    # These registries are mutable by design and are consulted at audit time.
    try:
        from . import surface_contract

        surface_contract.REQUIRED_TOOLS["nexus4d"] = set(NEXUS4D_TOOL_NAMES)
        surface_contract.REQUIRED_RESOURCES["nexus4d"] = set(NEXUS4D_RESOURCE_URIS)
    except Exception:
        # A missing audit module must not make package import impossible; clean
        # provider CI exercises the required module and fails there if absent.
        pass

    try:
        from . import composition_integrity

        if "nexus4d" not in composition_integrity.DEVELOPMENT_ORGANS:
            composition_integrity.DEVELOPMENT_ORGANS = tuple(composition_integrity.DEVELOPMENT_ORGANS) + ("nexus4d",)
    except Exception:
        pass

    # Unified runtime manifest is a composed observation. Add the live organ
    # after the canonical builder returns; do not claim external execution.
    from . import dispatch

    previous_handle = dispatch.handle

    def handle_with_nexus4d(server, message):
        result = previous_handle(server, message)
        if not result or "result" not in result:
            return result
        method = message.get("method")
        params = message.get("params") or {}
        if method == "resources/read" and params.get("uri") == "athena://manifest":
            contents = result["result"].get("contents") or []
            if contents:
                value = json.loads(contents[0]["text"])
                value["nexus4d"] = server.aor_development.nexus4d.describe()
                extensions = list(value.get("extensions") or [])
                marker = "NEXUS4D_BIDIRECTIONAL_OBLIGATION_PRESSURE_KERNEL"
                if marker not in extensions:
                    extensions.append(marker)
                value["extensions"] = extensions
                contents[0]["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
        return result

    dispatch.handle = handle_with_nexus4d
    AorDevelopmentSurface._athena_nexus4d_v1_registered = True


__all__ = ["install_nexus4d_extension", "Nexus4dRuntime", "VERSION"]
