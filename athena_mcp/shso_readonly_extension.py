from __future__ import annotations

"""Additive public-runtime registration for the SHSO read-only pressure bridge."""

import json
from typing import Any

from .shso_readonly import benchmark as shso_benchmark
from .shso_readonly import manifest as shso_manifest
from .shso_readonly import project_organism_pressure
from .shso_readonly_protocol import (
    SHSO_READONLY_RESOURCE_URIS,
    SHSO_READONLY_RESOURCES,
    SHSO_READONLY_TOOL_NAME,
    SHSO_READONLY_TOOL_NAMES,
    SHSO_READONLY_TOOLS,
)


class ShsoReadonlyRuntime:
    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == SHSO_READONLY_TOOL_NAME:
            return project_organism_pressure(
                arguments["health_advisory"],
                arguments["ecology_advisory"],
                ready_build_exists=arguments["ready_build_exists"],
                previous_transition_classes=arguments["previous_transition_classes"],
                verification_barrier_due=arguments["verification_barrier_due"],
                verification_barrier_mandatory=arguments[
                    "verification_barrier_mandatory"
                ],
            )
        raise KeyError(name)

    def read_resource(self, uri: str) -> dict[str, Any]:
        if uri in SHSO_READONLY_RESOURCE_URIS:
            return shso_manifest()
        raise KeyError(uri)

    def benchmark(self) -> dict[str, Any]:
        return shso_benchmark()


def install_shso_readonly_extension() -> None:
    """Install the SHSO bridge additively without changing release identity."""
    from . import protocol as protocol
    from .aor_development_surface import (
        AOR_DEVELOPMENT_RESOURCES,
        AOR_DEVELOPMENT_RESOURCE_URIS,
        AorDevelopmentSurface,
    )
    from .prompt_runtime import (
        PROMPT_RUNTIME_TOOLS,
        PROMPT_RUNTIME_TOOL_NAMES,
        PromptRuntime,
    )

    if getattr(PromptRuntime, "_athena_shso_readonly_v1_registered", False):
        return

    for tool in SHSO_READONLY_TOOLS:
        if tool["name"] not in PROMPT_RUNTIME_TOOL_NAMES:
            PROMPT_RUNTIME_TOOLS.append(tool)
            PROMPT_RUNTIME_TOOL_NAMES.add(tool["name"])
        if not any(existing["name"] == tool["name"] for existing in protocol.TOOLS):
            protocol.TOOLS.append(tool)

    known_resources = {resource["uri"] for resource in AOR_DEVELOPMENT_RESOURCES}
    for resource in SHSO_READONLY_RESOURCES:
        if resource["uri"] not in known_resources:
            AOR_DEVELOPMENT_RESOURCES.append(resource)
            known_resources.add(resource["uri"])
        AOR_DEVELOPMENT_RESOURCE_URIS.add(resource["uri"])

    previous_prompt_call = PromptRuntime.call_tool

    def prompt_call_with_shso_readonly(self, name, arguments):
        if name in SHSO_READONLY_TOOL_NAMES:
            runtime = getattr(self, "_athena_shso_readonly_runtime_v1", None)
            if runtime is None:
                runtime = ShsoReadonlyRuntime()
                self._athena_shso_readonly_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return previous_prompt_call(self, name, arguments)

    PromptRuntime.call_tool = prompt_call_with_shso_readonly

    previous_resource_read = AorDevelopmentSurface.read_resource

    def resource_read_with_shso_readonly(self, uri):
        if uri in SHSO_READONLY_RESOURCE_URIS:
            runtime = getattr(self, "_athena_shso_readonly_runtime_v1", None)
            if runtime is None:
                runtime = ShsoReadonlyRuntime()
                self._athena_shso_readonly_runtime_v1 = runtime
            return runtime.read_resource(uri)
        return previous_resource_read(self, uri)

    AorDevelopmentSurface.read_resource = resource_read_with_shso_readonly

    previous_benchmark = AorDevelopmentSurface.benchmark

    def benchmark_with_shso_readonly(self):
        result = previous_benchmark(self)
        result.update(ShsoReadonlyRuntime().benchmark())
        return result

    AorDevelopmentSurface.benchmark = benchmark_with_shso_readonly

    from . import dispatch

    previous_handle = dispatch.handle

    def handle_with_shso_readonly(server, message):
        result = previous_handle(server, message)
        if not result or "result" not in result:
            return result
        method = message.get("method")
        params = message.get("params") or {}
        if method == "resources/read" and params.get("uri") == "athena://manifest":
            contents = result["result"].get("contents") or []
            if contents:
                value = json.loads(contents[0]["text"])
                value["shso_readonly"] = shso_manifest()
                extensions = list(value.get("extensions") or [])
                marker = "SHSO_READONLY_RUNTIME_V1"
                if marker not in extensions:
                    extensions.append(marker)
                value["extensions"] = extensions
                contents[0]["text"] = json.dumps(
                    value, ensure_ascii=False, sort_keys=True
                )
        return result

    dispatch.handle = handle_with_shso_readonly
    PromptRuntime._athena_shso_readonly_v1_registered = True


__all__ = ["ShsoReadonlyRuntime", "install_shso_readonly_extension"]
