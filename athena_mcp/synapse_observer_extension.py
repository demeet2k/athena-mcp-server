from __future__ import annotations

"""Native MCP resource/manifest exposure for the read-only synapse observer."""

import importlib
import json

from .synapse_observer import (
    ARTIFACT,
    LAWS,
    TOOL_NAME,
    VERSION,
    SynapseObserverRuntime,
)

RESOURCE = {
    "uri": "athena://synapse",
    "name": "ATHENA Cross-Plane Synapse Observer V1",
    "mimeType": "application/json",
}
MANIFEST_MARKER = "SYNAPSE_OBSERVER_V1_READ_ONLY_CROSS_PLANE"
EXPECTED_SYNapse_SCHEMA = "ATHENA.SYNAPSE.ENVELOPE.V1"


def _runtime(server):
    runtime = getattr(server, "_synapse_observer_runtime_v1", None)
    if runtime is None:
        runtime = SynapseObserverRuntime(server)
        server._synapse_observer_runtime_v1 = runtime
    return runtime


def _synapse_abi_status() -> dict:
    """Probe the sibling cross-repository ABI without making it a dependency."""

    try:
        adapter = importlib.import_module("athena_mcp.synapse_liminal_adapter")
    except ModuleNotFoundError as exc:
        if exc.name == "athena_mcp.synapse_liminal_adapter":
            return {
                "expected_schema": EXPECTED_SYNapse_SCHEMA,
                "adapter_installed": False,
                "standing": "OPTIONAL_COMPANION_UNOBSERVED",
                "law": "OBSERVER_INTERNALS != CROSS_REPOSITORY_ENVELOPE_ABI",
            }
        raise

    schema = getattr(adapter, "SYNAPSE_SCHEMA", None)
    return {
        "expected_schema": EXPECTED_SYNapse_SCHEMA,
        "adapter_installed": True,
        "observed_schema": schema,
        "packet_profile": getattr(adapter, "PACKET_PROFILE", None),
        "receipt_profile": getattr(adapter, "RECEIPT_PROFILE", None),
        "schema_match": schema == EXPECTED_SYNapse_SCHEMA,
        "standing": "COMPANION_SCHEMA_MATCH" if schema == EXPECTED_SYNapse_SCHEMA else "COMPANION_SCHEMA_MISMATCH_HOLD",
        "law": "BRIDGE_RECEIPT_TOKEN != SYNAPSE_PROJECTION_RETURN_TOKEN",
    }


def _decorate(value: dict) -> dict:
    out = dict(value)
    out["cross_repository_synapse_abi"] = _synapse_abi_status()
    return out


def install_synapse_observer_extension() -> None:
    from . import dispatch
    from .server import Server

    if getattr(Server, "_athena_synapse_observer_resource_v1_registered", False):
        return

    previous_handle = dispatch.handle

    def handle_with_synapse_resource(server, message):
        method = message.get("method")
        params = message.get("params") or {}
        mid = message.get("id")
        uri = params.get("uri")

        if method == "resources/read" and uri == RESOURCE["uri"]:
            try:
                value = _decorate(_runtime(server).observe(shared_remote_mode="BEST_EFFORT", limit=100))
            except Exception as exc:
                value = _decorate({
                    "artifact": ARTIFACT,
                    "version": VERSION,
                    "status": "SYNAPSE_OBSERVER_HOLD",
                    "error": f"{type(exc).__name__}: {exc}",
                    "authority": "READ_ONLY_OBSERVER",
                    "laws": list(LAWS),
                })
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

        result = previous_handle(server, message)
        if not result or "result" not in result:
            return result

        if method == "resources/list":
            resources = result["result"].get("resources") or []
            if not any(row.get("uri") == RESOURCE["uri"] for row in resources):
                resources.append(dict(RESOURCE))
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
            value["synapse_observer"] = {
                "artifact": ARTIFACT,
                "version": VERSION,
                "tool": TOOL_NAME,
                "resource": RESOURCE["uri"],
                "authority": "READ_ONLY_OBSERVER",
                "cross_repository_synapse_abi": _synapse_abi_status(),
                "laws": list(LAWS),
            }
            contents[0]["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
            return result

        return result

    dispatch.handle = handle_with_synapse_resource
    Server._athena_synapse_observer_resource_v1_registered = True


__all__ = [
    "RESOURCE",
    "MANIFEST_MARKER",
    "EXPECTED_SYNapse_SCHEMA",
    "_synapse_abi_status",
    "install_synapse_observer_extension",
]
