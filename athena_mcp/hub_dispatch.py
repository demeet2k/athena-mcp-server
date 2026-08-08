from __future__ import annotations

import json
from typing import Any

from .dispatch import handle as base_handle
from .command_hub_protocol import HUB_PROMPT, HUB_RESOURCES
from .kc144_registry_pack import catalog as registry_catalog
from .kc144_registry_pack import completion_frontier as registry_completion_frontier
from .kc144_registry_pack import manifest as registry_manifest
from .kc144_registry_pack import status as registry_status, verify_pack
from .kc144_registry_protocol import REGISTRY_RESOURCES
from . import kc144_topology as topo

_RESOURCE_URIS = {item["uri"] for item in HUB_RESOURCES + REGISTRY_RESOURCES}


def _resource_value(server: Any, uri: str) -> Any:
    hub = server.command_hub
    if uri == "athena://kc144/hub":
        value = server._remove_discharged_field_blocker(hub.status())
        value["authoritative_registry_pack"] = registry_status()
        return value
    if uri == "athena://kc144/hub/manifest":
        value = hub.manifest(include_edges=False, include_dynamic_inventory=True)
        value["authoritative_registry_pack"] = registry_status()
        return value
    if uri == "athena://kc144/hub/inventory":
        return hub.inventory(limit=5000)
    if uri == "athena://kc144/hub/graphs":
        return {"graphs": topo.graph_summaries(), "digest": topo.digest(topo.graph_summaries())}
    if uri == "athena://kc144/hub/datasets":
        return hub.datasets()
    if uri == "athena://kc144/hub/communication":
        return hub.communication()
    if uri == "athena://kc144/hub/readiness":
        return server._remove_discharged_field_blocker(hub.readiness())
    if uri == "athena://kc144/hub/validation":
        value = hub.validate()
        value["authoritative_registry_pack"] = verify_pack(deep=True)
        return value
    if uri == "athena://kc144/registry/status":
        return registry_status()
    if uri == "athena://kc144/registry/catalog":
        return registry_catalog()
    if uri == "athena://kc144/registry/manifest":
        return registry_manifest()
    if uri == "athena://kc144/registry/verification":
        return verify_pack(deep=True)
    if uri == "athena://kc144/completion/frontier":
        return registry_completion_frontier()
    raise KeyError(uri)


def _prompt(task: str, agent: str) -> str:
    return f"""ATHENA KC144 TOPOLOGICAL COMMAND CENTER
AGENT={agent}
TASK={task}
1 HYDRATE athena://kc144/hub and athena://kc144/registry/status before acting. Preserve GID!=object!=coordinate!=claim!=evidence!=authority and adjacency!=bridge.
2 VERIFY the digest-bound registry pack when work depends on its bodies. It contains all committed cells, maths, graph, coordinate, harness, tool, skill, dataset, source, transport and completion registries.
3 READ readiness C/I/E/P/R/V/O/M/S/X. A structural PASS never overrides an integration, witness, migration, surface, or promotion HOLD.
4 LOCATE work through athena_kc144_hub_inventory, immutable cell bundles, bounded registry queries, cross-registry lexical search, exact source bundles and the source-bound completion frontier. Fibres are attached to immutable seats; a fibre is not the seat identity.
5 ROUTE only over typed executable graph layers. Source-bounded graph records may be queried, but unavailable executable edges must not be fabricated.
6 RECONSTRUCT the organ dependency DAG and transport membrane. Pheromone!=evidence; predicted RGO!=observed RGO; route replay!=independent witness.
7 COMPILE actual residuals through FIELD.1. Generated candidates remain UNMEASURED, semantic similarity never collapses identity, and explicit metric/routing conflict fails closed.
8 ATTACK the highest-leverage open gate or transport while preserving mature unrelated organs. Missing measurements remain UNKNOWN, not zero.
9 TEST with procedure+observation+result+witness. Persist with commit+receipt+verify. Replay against immutable inputs. Repair and retest failures.
10 VALIDATE with athena_kc144_hub_validate, athena_kc144_registry_verify and the existing surface/composition/smoke suites. Do not self-promote.
11 RETURN exact deltas, receipts, blockers, source lineage, and successor coordinate to GID144/H01_PRIME.
"""


def handle(server: Any, message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    params = message.get("params") or {}
    mid = message.get("id")

    if method == "initialize":
        result = base_handle(server, message)
        if result and "result" in result:
            info = dict(result["result"].get("serverInfo") or {})
            info.update({
                "name": "athena-kc144-topological-command-hub",
                "hubVersion": topo.HUB_VERSION,
                "registryPack": registry_status(),
            })
            result["result"]["serverInfo"] = info
        return result

    if method == "resources/list":
        result = base_handle(server, message)
        resources = list(result["result"]["resources"])
        seen = {item["uri"] for item in resources}
        resources.extend(item for item in HUB_RESOURCES + REGISTRY_RESOURCES if item["uri"] not in seen)
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
            for layer in ("KC144_TOPOLOGICAL_COMMAND_HUB", "KC144_AUTHORITATIVE_REGISTRY_PACK", "FIELD1_CANDIDATE_ASSEMBLER"):
                if layer not in layers:
                    layers.append(layer)
            value["layers"] = layers
            value["command_hub"] = {"uri": "athena://kc144/hub", "version": topo.HUB_VERSION, "promotion_ready": False}
            value["registry_pack"] = registry_status()
            content["text"] = json.dumps(value, ensure_ascii=False, sort_keys=True)
        return result

    if method == "prompts/get" and params.get("name") == HUB_PROMPT["name"]:
        args = params.get("arguments") or {}
        task = args.get("task", "")
        agent = args.get("agent", "ATHENA")
        return server.result(mid, {"description": HUB_PROMPT["description"], "messages": [{"role": "user", "content": {"type": "text", "text": _prompt(task, agent)}}]})

    return base_handle(server, message)
