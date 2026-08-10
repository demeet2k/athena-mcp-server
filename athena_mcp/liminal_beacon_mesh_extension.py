from __future__ import annotations

"""Additive installer for Liminal Beacon Mesh V1.

The manual MCP surface is always registered. Automatic tool-crossing touch/share
is opt-in via ATHENA_LIMINAL_AUTOHOOK=1 until measured regression evidence exists.
"""

import json
import os
from typing import Any

from .liminal_beacon_mesh import LiminalBeaconMeshRuntime
from .liminal_beacon_mesh_protocol import (
    LIMINAL_BEACON_RESOURCE,
    LIMINAL_BEACON_TOOLS,
    LIMINAL_BEACON_TOOL_NAMES,
)


def _enabled() -> bool:
    return str(os.getenv("ATHENA_LIMINAL_AUTOHOOK", "")).strip().casefold() in {"1", "true", "yes", "on"}


def _runtime(server: Any) -> LiminalBeaconMeshRuntime:
    runtime = getattr(server, "_liminal_beacon_mesh_runtime_v1", None)
    if runtime is None:
        runtime = LiminalBeaconMeshRuntime(server)
        server._liminal_beacon_mesh_runtime_v1 = runtime
    return runtime


def install_liminal_beacon_mesh() -> None:
    from . import protocol
    from .server import Server
    from . import dispatch

    if getattr(Server, "_athena_liminal_beacon_mesh_v1_registered", False):
        return

    existing = {tool["name"] for tool in protocol.TOOLS}
    for tool in LIMINAL_BEACON_TOOLS:
        if tool["name"] not in existing:
            protocol.TOOLS.append(tool)
            existing.add(tool["name"])

    previous_server_call = Server.call_tool

    def server_call_with_liminal(self, name, arguments):
        if name in LIMINAL_BEACON_TOOL_NAMES:
            return _runtime(self).call_tool(name, arguments)
        return previous_server_call(self, name, arguments)

    Server.call_tool = server_call_with_liminal

    previous_handle = dispatch.handle

    def handle_with_liminal(server, message):
        method = message.get("method")
        params = message.get("params") or {}
        mid = message.get("id")
        uri = params.get("uri")

        if method == "resources/read" and uri == LIMINAL_BEACON_RESOURCE["uri"]:
            value = _runtime(server).manifest()
            value["state"] = _runtime(server).state(include_packets=False, limit=20)
            return server.result(
                mid,
                {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(value, ensure_ascii=False, sort_keys=True),
                        }
                    ]
                },
            )

        autohook = None
        tool_name = params.get("name") if method == "tools/call" else None
        arguments = params.get("arguments") or {}
        if (
            method == "tools/call"
            and _enabled()
            and tool_name not in LIMINAL_BEACON_TOOL_NAMES
        ):
            try:
                autohook = {"before": _runtime(server).auto_before_tool(str(tool_name), arguments)}
            except Exception as exc:
                # The candidate communication membrane is fail-open for unrelated
                # tools. Its own failures remain visible without taking execution
                # authority from the pre-existing runtime.
                autohook = {"before_error": f"{type(exc).__name__}: {exc}"}

        result = previous_handle(server, message)
        if not result or "result" not in result:
            return result

        if method == "resources/list":
            resources = result["result"].get("resources") or []
            if not any(row.get("uri") == LIMINAL_BEACON_RESOURCE["uri"] for row in resources):
                resources.append(dict(LIMINAL_BEACON_RESOURCE))
            return result

        if method == "resources/read" and uri == "athena://manifest":
            contents = result["result"].get("contents") or []
            if contents:
                try:
                    value = json.loads(contents[0]["text"])
                except (KeyError, TypeError, json.JSONDecodeError):
                    return result
                extensions = list(value.get("extensions") or [])
                marker = "LIMINAL_BEACON_MESH_V1_CANDIDATE_MANUAL_SURFACE"
                if marker not in extensions:
                    extensions.append(marker)
                if _enabled():
                    auto = "LIMINAL_BEACON_MESH_V1_AUTOHOOK_OPT_IN_ACTIVE"
                    if auto not in extensions:
                        extensions.append(auto)
                value["extensions"] = extensions
                value["liminal_beacon_mesh"] = _runtime(server).manifest()
                contents[0]["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
            return result

        if method == "tools/call" and autohook is not None:
            payload = result["result"]
            if not bool(payload.get("isError")):
                structured = payload.get("structuredContent")
                if isinstance(structured, dict):
                    try:
                        autohook["after"] = _runtime(server).auto_after_tool(str(tool_name), arguments, structured)
                    except Exception as exc:
                        autohook["after_error"] = f"{type(exc).__name__}: {exc}"
                    structured["_liminal_beacon"] = autohook
                    contents = payload.get("content") or []
                    if contents and contents[0].get("type") == "text":
                        contents[0]["text"] = json.dumps(structured, ensure_ascii=False, sort_keys=True)
            return result

        return result

    dispatch.handle = handle_with_liminal
    Server._athena_liminal_beacon_mesh_v1_registered = True


__all__ = ["install_liminal_beacon_mesh"]
