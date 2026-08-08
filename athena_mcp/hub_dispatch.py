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
from .kc144_polyatlas import manifest as polyatlas_manifest
from .kc144_polyatlas import resolution_family as polyatlas_resolution_family
from .kc144_polyatlas import sources as polyatlas_sources
from .kc144_polyatlas import sphere_summary as polyatlas_sphere_summary
from .kc144_polyatlas import status as polyatlas_status
from .kc144_polyatlas import validate as polyatlas_validate
from .kc144_polyatlas_protocol import POLYATLAS_RESOURCES
from .system_upgrade import SYSTEM_RELEASE_VERSION, SYSTEM_UPGRADE_VERSION
from .system_upgrade_protocol import (
    SYSTEM_UPGRADE_PROMPT,
    SYSTEM_UPGRADE_RESOURCES,
)
from . import kc144_topology as topo

_RESOURCE_URIS = {
    item["uri"]
    for item in (
        HUB_RESOURCES
        + REGISTRY_RESOURCES
        + POLYATLAS_RESOURCES
        + SYSTEM_UPGRADE_RESOURCES
    )
}


def _resource_value(server: Any, uri: str) -> Any:
    hub = server.command_hub
    system = server.system_upgrade
    if uri == "athena://system/upgrade":
        return {
            "manifest": system.manifest(),
            "local_snapshot": system.local_snapshot(
                run_replay_samples=False
            ),
            "law": (
                "Create UPGRUN, mutate only through witnessed CAS observations, "
                "refresh measured local gates, replay, then issue exact-head RELCERT."
            ),
        }
    if uri == "athena://system/upgrade/frontier":
        recent = system.recent(1)
        if recent:
            return system.state(recent[0]["run_id"])
        return {
            "version": SYSTEM_UPGRADE_VERSION,
            "state": "NO_PERSISTED_UPGRADE_RUN",
            "frontier": registry_completion_frontier(),
            "local_snapshot": system.local_snapshot(
                run_replay_samples=False
            ),
            "boundary": (
                "The source frontier is a pure projection until a persistent UPGRUN is created."
            ),
        }
    if uri == "athena://system/release":
        return {
            "version": SYSTEM_RELEASE_VERSION,
            "recent": system.release_recent(50),
            "law": (
                "RELCERT requires local IC10 readiness, matching UPGRUN replay, "
                "expected-head match and exact-head PROMOTION.1 CI+smoke witnesses."
            ),
            "boundary": (
                "A qualified certificate is not merge or deployment authority and is not semantic proof."
            ),
        }
    if uri == "athena://kc144/hub":
        value = hub.status()
        value["authoritative_registry_pack"] = registry_status()
        value["polyatlas"] = polyatlas_status()
        value["system_upgrade"] = system.manifest()
        return value
    if uri == "athena://kc144/hub/manifest":
        value = hub.manifest(
            include_edges=False, include_dynamic_inventory=True
        )
        value["authoritative_registry_pack"] = registry_status()
        value["polyatlas"] = polyatlas_manifest()
        value["system_upgrade"] = system.manifest()
        return value
    if uri == "athena://kc144/hub/inventory":
        return hub.inventory(limit=5000)
    if uri == "athena://kc144/hub/graphs":
        return {
            "graphs": topo.graph_summaries(),
            "digest": topo.digest(topo.graph_summaries()),
        }
    if uri == "athena://kc144/hub/datasets":
        return hub.datasets()
    if uri == "athena://kc144/hub/communication":
        return hub.communication()
    if uri == "athena://kc144/hub/readiness":
        value = hub.readiness()
        value["polyatlas"] = polyatlas_status()
        value["system_upgrade"] = system.manifest()
        return value
    if uri == "athena://kc144/hub/validation":
        value = hub.validate()
        pack = verify_pack(deep=True)
        atlas = polyatlas_validate(include_details=False)
        value["authoritative_registry_pack"] = pack
        value["polyatlas"] = atlas
        value["system_upgrade"] = {
            "manifest": system.manifest(),
            "local_snapshot": system.local_snapshot(
                run_replay_samples=False
            ),
        }
        if pack["status"] != "PASS" or atlas["status"] != "PASS":
            value["overall_status"] = "FAIL"
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
    if uri == "athena://kc144/polyatlas/status":
        return polyatlas_status()
    if uri == "athena://kc144/polyatlas/manifest":
        return polyatlas_manifest()
    if uri == "athena://kc144/polyatlas/sources":
        return polyatlas_sources()
    if uri == "athena://kc144/polyatlas/sphere":
        return polyatlas_sphere_summary()
    if uri == "athena://kc144/polyatlas/family":
        return polyatlas_resolution_family()
    if uri == "athena://kc144/polyatlas/validation":
        return polyatlas_validate(include_details=False)
    raise KeyError(uri)


def _hub_prompt(task: str, agent: str) -> str:
    return f"""ATHENA KC144 TOPOLOGICAL COMMAND CENTER
AGENT={agent}
TASK={task}
1 HYDRATE athena://kc144/hub, athena://system/upgrade, athena://kc144/registry/status, and athena://kc144/polyatlas/status before acting.
2 PRESERVE GID!=object!=coordinate!=claim!=evidence!=authority; adjacency!=bridge; plan!=execution; local readiness!=release.
3 READ measured C/I/E/P/R/V/O/M/S/X. Historical structural HOLDs are source snapshots, not current runtime truth.
4 OPEN one persistent UPGRUN for consequential full-system work. Use expected_state_digest CAS for every refresh or task observation.
5 COMPLETE source tasks only with procedure+observation+result+ref witnesses. Dependencies and exact-head requirements fail closed.
6 ROUTE through typed graphs and C01..C16 coordinates without rounding, identity collapse, or converting reachability into proof.
7 USE AOR for lawful WHAT/frontier selection and Collective V1-V7 for HOW resources execute it. Pheromone!=evidence; prediction!=observation.
8 STOP at real measurement, HUG implementation, executor, test, CI, smoke, merge or deployment boundaries instead of simulating them.
9 VERIFY registry, polyatlas, surface, composition, schema, self-test, UPGRUN replay and exact-head promotion.
10 ISSUE RELCERT only when local IC10 gates pass and CI+smoke attest the same exact head. RELCERT is not merge/deployment authority.
11 RETURN exact deltas, receipts, blockers, source lineage and KC144.V1::GID144::SSN12.M12 successor.
"""


def _upgrade_prompt(
    objective: str, target_version: str, agent: str
) -> str:
    return f"""ATHENA COMPLETE SYSTEM UPGRADE
AGENT={agent}
OBJECTIVE={objective}
TARGET_VERSION={target_version}
1 MEASURE current local C/I/E/P/R/V/O/M/S/X through athena_system_upgrade_plan.
2 PERSIST one UPGRUN; never represent a plan as execution.
3 ATTACK only the ready source-bound frontier or a measured failed local gate.
4 OBSERVE completion with procedure, observation, PASS result, provenance ref, and exact head when required.
5 ADVANCE with expected_state_digest CAS; stale writers and blocked dependencies fail closed.
6 REFRESH local gates after meaningful repository/runtime changes.
7 REPLAY the complete upgrade event chain.
8 RUN exact-head unit, invariant, package and subprocess MCP smoke jobs.
9 BIND CI and smoke to the exact head through athena_system_release_certificate.
10 RETURN UPGRUN, state digest, RELCERT or blockers, and the next lawful task.
"""


def handle(
    server: Any, message: dict[str, Any]
) -> dict[str, Any] | None:
    method = message.get("method")
    params = message.get("params") or {}
    mid = message.get("id")

    if method == "initialize":
        result = base_handle(server, message)
        if result and "result" in result:
            info = dict(result["result"].get("serverInfo") or {})
            info.update(
                {
                    "name": "athena-kc144-topological-command-hub",
                    "hubVersion": topo.HUB_VERSION,
                    "registryPack": registry_status(),
                    "polyatlas": polyatlas_status(),
                    "systemUpgrade": server.system_upgrade.describe(),
                }
            )
            result["result"]["serverInfo"] = info
        return result

    if method == "resources/list":
        result = base_handle(server, message)
        resources = list(result["result"]["resources"])
        seen = {item["uri"] for item in resources}
        resources.extend(
            item
            for item in (
                HUB_RESOURCES
                + REGISTRY_RESOURCES
                + POLYATLAS_RESOURCES
                + SYSTEM_UPGRADE_RESOURCES
            )
            if item["uri"] not in seen
        )
        result["result"]["resources"] = sorted(
            resources, key=lambda item: item["uri"]
        )
        return result

    if method == "resources/read" and params.get("uri") in _RESOURCE_URIS:
        uri = params["uri"]
        value = _resource_value(server, uri)
        return server.result(
            mid,
            {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(
                            value,
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                    }
                ]
            },
        )

    if method == "resources/read" and params.get("uri") == "athena://manifest":
        result = base_handle(server, message)
        if result and "result" in result:
            content = result["result"]["contents"][0]
            value = json.loads(content["text"])
            layers = list(value.get("layers") or [])
            for layer in (
                "KC144_TOPOLOGICAL_COMMAND_HUB",
                "KC144_AUTHORITATIVE_REGISTRY_PACK",
                "KC144_16_COORDINATE_POLYATLAS",
                "FIELD1_CANDIDATE_ASSEMBLER",
                "SYSTEM_UPGRADE1_WITNESSED_CAS",
                "SYSTEM_RELEASE1_EXACT_HEAD_CERTIFICATE",
            ):
                if layer not in layers:
                    layers.append(layer)
            value["layers"] = layers
            value["command_hub"] = {
                "uri": "athena://kc144/hub",
                "version": topo.HUB_VERSION,
                "promotion_ready": False,
            }
            value["registry_pack"] = registry_status()
            value["polyatlas"] = polyatlas_status()
            value["system_upgrade"] = server.system_upgrade.manifest()
            content["text"] = json.dumps(
                value, ensure_ascii=False, sort_keys=True
            )
        return result

    if method == "prompts/get":
        name = params.get("name")
        args = params.get("arguments") or {}
        if name == HUB_PROMPT["name"]:
            task = args.get("task", "")
            agent = args.get("agent", "ATHENA")
            return server.result(
                mid,
                {
                    "description": HUB_PROMPT["description"],
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": _hub_prompt(task, agent),
                            },
                        }
                    ],
                },
            )
        if name == SYSTEM_UPGRADE_PROMPT["name"]:
            objective = args.get("objective", "")
            target = args.get("target_version", "2.6.0")
            agent = args.get("agent", "ATHENA")
            return server.result(
                mid,
                {
                    "description": SYSTEM_UPGRADE_PROMPT["description"],
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": _upgrade_prompt(
                                    objective, target, agent
                                ),
                            },
                        }
                    ],
                },
            )

    return base_handle(server, message)
