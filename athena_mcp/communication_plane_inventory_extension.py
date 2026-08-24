from __future__ import annotations

"""Install the typed communication-plane inventory on the synapse observer."""

import json

from .communication_plane_inventory import (
    ARTIFACT,
    LAWS,
    RESOURCE_URI,
    VERSION,
    build_plane_inventory,
)

RESOURCE = {
    "uri": RESOURCE_URI,
    "name": "ATHENA Communication Plane Inventory V1",
    "mimeType": "application/json",
}
MANIFEST_MARKER = "COMMUNICATION_PLANE_INVENTORY_V1_READ_ONLY"


def install_communication_plane_inventory() -> None:
    from . import dispatch
    from .server import Server
    from .synapse_observer import SynapseObserverRuntime

    if getattr(SynapseObserverRuntime, "_athena_communication_plane_inventory_v1_registered", False):
        return

    previous_observe = SynapseObserverRuntime.observe

    def observe_with_plane_inventory(self, *args, **kwargs):
        value = dict(previous_observe(self, *args, **kwargs))
        value["communication_plane_inventory"] = build_plane_inventory(
            self.server,
            value,
            limit=kwargs.get("limit", 100),
        )
        return value

    SynapseObserverRuntime.observe = observe_with_plane_inventory
    SynapseObserverRuntime._athena_communication_plane_inventory_v1_registered = True

    previous_handle = dispatch.handle

    def handle_with_plane_inventory(server, message):
        method = message.get("method")
        params = message.get("params") or {}
        mid = message.get("id")
        uri = params.get("uri")

        if method == "resources/read" and uri == RESOURCE_URI:
            runtime = getattr(server, "_synapse_observer_runtime_v1", None)
            if runtime is None:
                runtime = SynapseObserverRuntime(server)
                server._synapse_observer_runtime_v1 = runtime
            try:
                observed = runtime.observe(shared_remote_mode="BEST_EFFORT", limit=100)
                value = observed["communication_plane_inventory"]
            except Exception as exc:
                value = {
                    "artifact": ARTIFACT,
                    "version": VERSION,
                    "status": "COMMUNICATION_PLANE_INVENTORY_HOLD",
                    "error": f"{type(exc).__name__}: {exc}",
                    "authority": "READ_ONLY_NAVIGATION_OBSERVER",
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
            value["communication_plane_inventory"] = {
                "artifact": ARTIFACT,
                "version": VERSION,
                "resource": RESOURCE_URI,
                "authority": "READ_ONLY_NAVIGATION_OBSERVER",
                "identity_join_policy": "NO_AUTOMATIC_CROSS_PLANE_IDENTITY_JOIN",
                "laws": list(LAWS),
            }
            contents[0]["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
            return result

        return result

    dispatch.handle = handle_with_plane_inventory
    Server._athena_communication_plane_inventory_v1_registered = True


__all__ = [
    "RESOURCE",
    "MANIFEST_MARKER",
    "install_communication_plane_inventory",
]
