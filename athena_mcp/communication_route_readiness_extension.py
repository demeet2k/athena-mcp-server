from __future__ import annotations

"""MCP registration for concrete communication-route readiness verification."""

import json

from .communication_route_readiness import (
    ARTIFACT,
    LAWS,
    READINESS_RESOURCE,
    READINESS_TOOL,
    RESOURCE_URI,
    TOOL_NAME,
    VERSION,
    verify_route_readiness,
)

MANIFEST_MARKER = "COMMUNICATION_ROUTE_READINESS_V1_READ_ONLY"


def install_communication_route_readiness() -> None:
    from . import dispatch, protocol
    from .server import Server

    if getattr(Server, "_athena_communication_route_readiness_v1_registered", False):
        return

    if not any(row["name"] == TOOL_NAME for row in protocol.TOOLS):
        protocol.TOOLS.append(READINESS_TOOL)

    previous_call = Server.call_tool

    def call_with_readiness(self, name, arguments):
        if name == TOOL_NAME:
            return verify_route_readiness(self, arguments)
        return previous_call(self, name, arguments)

    Server.call_tool = call_with_readiness

    previous_handle = dispatch.handle

    def handle_with_readiness(server, message):
        method = message.get("method")
        params = message.get("params") or {}
        mid = message.get("id")
        uri = params.get("uri")

        if method == "resources/read" and uri == RESOURCE_URI:
            value = {
                "artifact": ARTIFACT,
                "version": VERSION,
                "tool": TOOL_NAME,
                "authority": "READ_ONLY_PRECONDITION_VERIFICATION",
                "fresh_remote_check": "OPTIONAL_GIT_FETCH_ONLY_NO_FAST_FORWARD_OR_MERGE",
                "laws": list(LAWS),
            }
            return server.result(
                mid,
                {
                    "contents": [
                        {
                            "uri": RESOURCE_URI,
                            "mimeType": "application/json",
                            "text": json.dumps(value, ensure_ascii=False, sort_keys=True),
                        }
                    ]
                },
            )

        result = previous_handle(server, message)
        if not result or "result" not in result:
            return result

        if method == "resources/list":
            resources = result["result"].get("resources") or []
            if not any(row.get("uri") == RESOURCE_URI for row in resources):
                resources.append(dict(READINESS_RESOURCE))
            return result

        if method == "resources/read" and uri == "athena://manifest":
            contents = result["result"].get("contents") or []
            if not contents:
                return result
            try:
                value = json.loads(contents[0]["text"])
            except (KeyError, TypeError, json.JSONDecodeError):
                return result
            extensions = list(value.get("extensions") or [])
            if MANIFEST_MARKER not in extensions:
                extensions.append(MANIFEST_MARKER)
            value["extensions"] = extensions
            value["communication_route_readiness"] = {
                "artifact": ARTIFACT,
                "version": VERSION,
                "tool": TOOL_NAME,
                "resource": RESOURCE_URI,
                "authority": "READ_ONLY_PRECONDITION_VERIFICATION",
                "laws": list(LAWS),
            }
            contents[0]["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
            return result

        return result

    dispatch.handle = handle_with_readiness
    Server._athena_communication_route_readiness_v1_registered = True


__all__ = ["MANIFEST_MARKER", "install_communication_route_readiness"]
