from __future__ import annotations

"""Additive installer for the ephemeral -> durable Message Board bridge.

The installer mutates the existing AOR development registries in place so the
Server/dispatch references imported earlier continue to see the same registry
objects. The runtime wrapper reuses AorDevelopmentSurface.ephemeral_coordination
rather than allocating a second SQLite membrane.
"""

from .ephemeral_durable_bridge import EphemeralDurableBridgeSurface
from .ephemeral_durable_bridge_protocol import (
    EPHEMERAL_DURABLE_RESOURCE,
    EPHEMERAL_DURABLE_TOOLS,
    EPHEMERAL_DURABLE_TOOL_NAMES,
)


def install_ephemeral_durable_bridge() -> None:
    from . import protocol
    from . import aor_development_surface as aor

    surface_cls = aor.AorDevelopmentSurface
    if getattr(surface_cls, "_athena_ephemeral_durable_bridge_v1_registered", False):
        return

    existing_tools = {tool["name"] for tool in aor.AOR_DEVELOPMENT_TOOLS}
    for tool in EPHEMERAL_DURABLE_TOOLS:
        if tool["name"] not in existing_tools:
            aor.AOR_DEVELOPMENT_TOOLS.append(tool)
            existing_tools.add(tool["name"])
        aor.AOR_DEVELOPMENT_TOOL_NAMES.add(tool["name"])
        if not any(row["name"] == tool["name"] for row in protocol.TOOLS):
            protocol.TOOLS.append(tool)

    if not any(row["uri"] == EPHEMERAL_DURABLE_RESOURCE["uri"] for row in aor.AOR_DEVELOPMENT_RESOURCES):
        aor.AOR_DEVELOPMENT_RESOURCES.append(dict(EPHEMERAL_DURABLE_RESOURCE))
    aor.AOR_DEVELOPMENT_RESOURCE_URIS.add(EPHEMERAL_DURABLE_RESOURCE["uri"])

    previous_init = surface_cls.__init__
    previous_call = surface_cls.call_tool
    previous_read = surface_cls.read_resource
    previous_benchmark = surface_cls.benchmark

    def init_with_ephemeral_durable(self, server):
        previous_init(self, server)
        self.ephemeral_durable_bridge = EphemeralDurableBridgeSurface(
            server,
            self.ephemeral_coordination.runtime,
        )

    def call_with_ephemeral_durable(self, name, args):
        if name in EPHEMERAL_DURABLE_TOOL_NAMES:
            handled, value = self.ephemeral_durable_bridge.call_tool(name, args)
            if handled:
                return True, value
        return previous_call(self, name, args)

    def read_with_ephemeral_durable(self, uri):
        if uri == EPHEMERAL_DURABLE_RESOURCE["uri"]:
            return self.ephemeral_durable_bridge.read_resource(uri)
        return previous_read(self, uri)

    def benchmark_with_ephemeral_durable(self):
        value = dict(previous_benchmark(self))
        value.update(self.ephemeral_durable_bridge.benchmark())
        return value

    surface_cls.__init__ = init_with_ephemeral_durable
    surface_cls.call_tool = call_with_ephemeral_durable
    surface_cls.read_resource = read_with_ephemeral_durable
    surface_cls.benchmark = benchmark_with_ephemeral_durable
    surface_cls._athena_ephemeral_durable_bridge_v1_registered = True


__all__ = ["install_ephemeral_durable_bridge"]
