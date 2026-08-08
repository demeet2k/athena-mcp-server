from __future__ import annotations

import json
from typing import Any

from .dispatch import handle as base_handle
from .command_hub_protocol import HUB_PROMPT, HUB_RESOURCES
from . import kc144_topology as topo

_RESOURCE_URIS = {item["uri"] for item in HUB_RESOURCES}


def _resource_value(server: Any, uri: str) -> Any:
    hub = server.command_hub
    if uri == "athena://kc144/hub":
        return hub.status()
    if uri == "athena://kc144/hub/manifest":
        return hub.manifest(include_edges=False, include_dynamic_inventory=True)
    if uri == "athena://kc144/hub/inventory":
        return hub.inventory(limit=5000)
    if uri == "athena://kc144/hub/graphs":
        return {"graphs": topo.graph_summaries(), "digest": topo.digest(topo.graph_summaries())}
    if uri == "athena://kc144/hub/datasets":
        return hub.datasets()
    if uri == "athena://kc144/hub/communication":
        return hub.communication()
    if uri == "athena://kc144/hub/readiness":
        return hub.readiness()
    if uri == "athena://kc144/hub/validation":
        return hub.validate()
    raise KeyError(uri)


def _prompt(task: str, agent: str) -> str:
    return f"""ATHENA KC144 TOPOLOGICAL COMMAND CENTER
AGENT={agent}
TASK={task}
1 HYDRATE athena://kc144/hub before acting. Preserve GID!=object!=coordinate!=claim!=evidence!=authority and adjacency!=bridge.
2 READ readiness C/I/E/P/R/V/O/M/S/X. A structural PASS never overrides an integration, witness, migration, surface, or promotion HOLD.
3 LOCATE work through athena_kc144_hub_inventory and athena_kc144_hub_seat. Every tool, resource, harness, skill, math object, coordinate, graph, gate, and source dataset is a fibre attached to an immutable seat; the fibre is not the seat identity.
4 ROUTE only over typed executable graph layers. compiler_declared cardinality may be inspected but unavailable edge records must not be fabricated.
5 RECONSTRUCT the organ dependency DAG and transport membrane. Source presence or staged code is not live integration. Pheromone!=evidence; predicted RGO!=observed RGO; route replay!=independent witness.
6 ATTACK the highest-leverage open gate or transport while preserving mature unrelated organs. Missing measurements remain UNKNOWN, not zero.
7 TEST with procedure+observation+result+witness. Persist with commit+receipt+verify. Replay against immutable inputs. Repair and retest failures.
8 VALIDATE with athena_kc144_hub_validate and the existing surface/composition/smoke suites. Do not self-promote.
9 RETURN exact deltas, receipts, blockers, source lineage, and successor coordinate to GID144/H01_PRIME.
"""


def handle(server: Any, message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    params = message.get("params") or {}
    mid = message.get("id")

    if method == "initialize":
        result = base_handle(server, message)
        if result and "result" in result:
            info = dict(result["result"].get("serverInfo") or {})
            info.update({"name": "athena-kc144-topological-command-hub", "hubVersion": topo.HUB_VERSION})
            result["result"]["serverInfo"] = info
        return result

    if method == "resources/list":
        result = base_handle(server, message)
        resources = list(result["result"]["resources"])
        seen = {item["uri"] for item in resources}
        resources.extend(item for item in HUB_RESOURCES if item["uri"] not in seen)
        result["result"]["resources"] = sorted(resources, key=lambda item: item["uri"])
        return result

    if method == "resources/read" and params.get("uri") in _RESOURCE_URIS:
        uri = params["uri"]
        value = _resource_value(server, uri)
        return server.result(mid, {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(value, ensure_ascii=False, sort_keys=True)}]})

    if method == "resources/read" and params.get("uri") == "athena://manifest":
        result = base_handle(server, message)
        if result and "result" in result:
            content = result["result"]["contents"][0]
            value = json.loads(content["text"])
            layers = list(value.get("layers") or [])
            if "KC144_TOPOLOGICAL_COMMAND_HUB" not in layers:
                layers.append("KC144_TOPOLOGICAL_COMMAND_HUB")
            value["layers"] = layers
            value["command_hub"] = {"uri": "athena://kc144/hub", "version": topo.HUB_VERSION, "promotion_ready": False}
            content["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
        return result

    if method == "prompts/get" and params.get("name") == HUB_PROMPT["name"]:
        args = params.get("arguments") or {}
        task = args.get("task", "")
        agent = args.get("agent", "ATHENA")
        return server.result(mid, {"description": HUB_PROMPT["description"], "messages": [{"role": "user", "content": {"type": "text", "text": _prompt(task, agent)}}]})

    return base_handle(server, message)
