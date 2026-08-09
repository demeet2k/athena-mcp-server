from __future__ import annotations

"""Additive no-injection installer for Liminal Beacon Shadow V1."""

import json
import os
from typing import Any

from .liminal_beacon_mesh_protocol import LIMINAL_BEACON_TOOL_NAMES
from .liminal_beacon_shadow import LiminalBeaconShadowRuntime
from .liminal_beacon_shadow_protocol import (
    LIMINAL_BEACON_SHADOW_RESOURCE,
    LIMINAL_BEACON_SHADOW_TOOLS,
    LIMINAL_BEACON_SHADOW_TOOL_NAMES,
)


def _truthy(value: Any) -> bool:
    return str(value or "").strip().casefold() in {"1", "true", "yes", "on"}


def shadow_requested() -> bool:
    return _truthy(os.getenv("ATHENA_LIMINAL_SHADOW", ""))


def live_autohook_enabled() -> bool:
    return _truthy(os.getenv("ATHENA_LIMINAL_AUTOHOOK", ""))


def shadow_mode() -> str:
    if not shadow_requested():
        return "OFF"
    if live_autohook_enabled():
        return "HOLD_AUTOHOOK_ACTIVE"
    return "SHADOW"


def _runtime(server: Any) -> LiminalBeaconShadowRuntime:
    runtime = getattr(server, "_liminal_beacon_shadow_runtime_v1", None)
    if runtime is None:
        runtime = LiminalBeaconShadowRuntime(server)
        server._liminal_beacon_shadow_runtime_v1 = runtime
    return runtime


def install_liminal_beacon_shadow() -> None:
    from . import dispatch, protocol
    from .server import Server

    if getattr(Server, "_athena_liminal_beacon_shadow_v1_registered", False):
        return

    existing = {tool["name"] for tool in protocol.TOOLS}
    for tool in LIMINAL_BEACON_SHADOW_TOOLS:
        if tool["name"] not in existing:
            protocol.TOOLS.append(tool)
            existing.add(tool["name"])

    previous_server_call = Server.call_tool

    def server_call_with_shadow(self, name, arguments):
        if name in LIMINAL_BEACON_SHADOW_TOOL_NAMES:
            args = dict(arguments or {})
            value = _runtime(self).status(
                limit=int(args.get("limit") or 20),
                include_records=bool(args.get("include_records", False)),
            )
            value["mode"] = shadow_mode()
            return value
        return previous_server_call(self, name, arguments)

    Server.call_tool = server_call_with_shadow
    previous_handle = dispatch.handle
    excluded = set(LIMINAL_BEACON_TOOL_NAMES) | set(LIMINAL_BEACON_SHADOW_TOOL_NAMES)

    def handle_with_shadow(server, message):
        method = message.get("method")
        params = message.get("params") or {}
        mid = message.get("id")
        uri = params.get("uri")

        if method == "resources/read" and uri == LIMINAL_BEACON_SHADOW_RESOURCE["uri"]:
            value = _runtime(server).status(limit=20, include_records=False)
            value["mode"] = shadow_mode()
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

        tool_name = params.get("name") if method == "tools/call" else None
        arguments = params.get("arguments") or {}
        token = None
        mode = shadow_mode()
        if method == "tools/call" and tool_name not in excluded and shadow_requested():
            runtime = _runtime(server)
            if mode != "SHADOW":
                runtime.record_hold("AUTOHOOK_ACTIVE_CONTAMINATION", tool_name=str(tool_name))
            else:
                try:
                    token = runtime.begin_crossing(str(tool_name), dict(arguments))
                except Exception as exc:
                    runtime.record_error("BEFORE", exc, tool_name=str(tool_name))

        result = previous_handle(server, message)
        if not result or "result" not in result:
            return result

        if method == "resources/list":
            resources = result["result"].get("resources") or []
            if not any(row.get("uri") == LIMINAL_BEACON_SHADOW_RESOURCE["uri"] for row in resources):
                resources.append(dict(LIMINAL_BEACON_SHADOW_RESOURCE))
            return result

        if method == "resources/read" and uri == "athena://manifest":
            contents = result["result"].get("contents") or []
            if contents:
                try:
                    value = json.loads(contents[0]["text"])
                except (KeyError, TypeError, json.JSONDecodeError):
                    return result
                extensions = list(value.get("extensions") or [])
                marker = "LIMINAL_BEACON_SHADOW_V1_CANDIDATE_NO_INJECTION"
                if marker not in extensions:
                    extensions.append(marker)
                value["extensions"] = extensions
                value["liminal_beacon_shadow"] = {
                    **_runtime(server).manifest(),
                    "mode": shadow_mode(),
                }
                contents[0]["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
            return result

        if method == "tools/call" and token is not None and mode == "SHADOW":
            runtime = _runtime(server)
            try:
                payload = result["result"]
                structured = payload.get("structuredContent") if isinstance(payload, dict) else None
                successful = isinstance(payload, dict) and not bool(payload.get("isError"))
                runtime.end_crossing(
                    token,
                    str(tool_name),
                    dict(arguments),
                    structured,
                    result,
                    successful=successful,
                )
            except Exception as exc:
                # Shadow cannot seize execution authority from an already completed
                # tool call. The HOLD is visible through the separate shadow surface.
                runtime.record_error("AFTER", exc, tool_name=str(tool_name))
            return result

        return result

    dispatch.handle = handle_with_shadow
    Server._athena_liminal_beacon_shadow_v1_registered = True


__all__ = [
    "install_liminal_beacon_shadow",
    "shadow_requested",
    "live_autohook_enabled",
    "shadow_mode",
]
