from __future__ import annotations

"""MCP registration for the read-only communication route planner."""

import json

from .communication_route_planner import (
    ARTIFACT,
    EDGE_CONTRACTS,
    LAWS,
    PLANES,
    RESOURCE_URI,
    ROUTE_PLANNER_RESOURCE,
    ROUTE_PLANNER_TOOL,
    TOOL_NAME,
    VERSION,
    plan_route,
)

MANIFEST_MARKER = "COMMUNICATION_ROUTE_PLANNER_V1_READ_ONLY"


def install_communication_route_planner() -> None:
    from . import dispatch, protocol
    from .server import Server

    if getattr(Server, "_athena_communication_route_planner_v1_registered", False):
        return

    if not any(row["name"] == TOOL_NAME for row in protocol.TOOLS):
        protocol.TOOLS.append(ROUTE_PLANNER_TOOL)

    previous_call = Server.call_tool

    def call_with_route_planner(self, name, args):
        if name == TOOL_NAME:
            return plan_route(self, args)
        return previous_call(self, name, args)

    Server.call_tool = call_with_route_planner

    previous_handle = dispatch.handle

    def handle_with_route_planner(server, message):
        method = message.get("method")
        params = message.get("params") or {}
        mid = message.get("id")
        uri = params.get("uri")

        if method == "resources/read" and uri == RESOURCE_URI:
            value = {
                "artifact": ARTIFACT,
                "version": VERSION,
                "tool": TOOL_NAME,
                "planes": sorted(PLANES),
                "edge_contracts": [
                    {
                        "src": key[0],
                        "dst": key[1],
                        **dict(contract),
                    }
                    for key, contract in sorted(EDGE_CONTRACTS.items())
                ],
                "authority": "READ_ONLY_ROUTE_PLANNING",
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
                resources.append(dict(ROUTE_PLANNER_RESOURCE))
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
            value["communication_route_planner"] = {
                "artifact": ARTIFACT,
                "version": VERSION,
                "tool": TOOL_NAME,
                "resource": RESOURCE_URI,
                "authority": "READ_ONLY_ROUTE_PLANNING",
                "laws": list(LAWS),
            }
            contents[0]["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
            return result

        return result

    dispatch.handle = handle_with_route_planner
    Server._athena_communication_route_planner_v1_registered = True


__all__ = ["MANIFEST_MARKER", "install_communication_route_planner"]
