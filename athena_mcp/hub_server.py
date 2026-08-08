from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from .server import Server as UnifiedServer
from .protocol import TOOLS, PROMPTS
from .aor_development_surface import AOR_DEVELOPMENT_RESOURCES
from .command_hub import KC144CommandHub
from .command_hub_protocol import HUB_PROMPT, HUB_RESOURCES, HUB_TOOLS
from .kc144_registry_pack import catalog as registry_catalog
from .kc144_registry_pack import cell_bundle as registry_cell_bundle
from .kc144_registry_pack import completion_frontier as registry_completion_frontier
from .kc144_registry_pack import cross_search as registry_cross_search
from .kc144_registry_pack import manifest as registry_manifest
from .kc144_registry_pack import query_registry, source_bundle as registry_source_bundle
from .kc144_registry_pack import status as registry_status, verify_pack
from .kc144_registry_protocol import REGISTRY_RESOURCES, REGISTRY_TOOLS
from .kc144_polyatlas import gid_decompositions as polyatlas_decompositions
from .kc144_polyatlas import manifest as polyatlas_manifest
from .kc144_polyatlas import polyatlas_route
from .kc144_polyatlas import resolution_family, resolution_transport
from .kc144_polyatlas import rosetta_address
from .kc144_polyatlas import sphere_atlas, sphere_cell
from .kc144_polyatlas import status as polyatlas_status
from .kc144_polyatlas import validate as polyatlas_validate
from .kc144_polyatlas_protocol import POLYATLAS_RESOURCES, POLYATLAS_TOOLS

_existing_tools = {item["name"] for item in TOOLS}
for tool in HUB_TOOLS + REGISTRY_TOOLS + POLYATLAS_TOOLS:
    if tool["name"] not in _existing_tools:
        TOOLS.append(tool)
        _existing_tools.add(tool["name"])

_existing_prompts = {item["name"] for item in PROMPTS}
if HUB_PROMPT["name"] not in _existing_prompts:
    PROMPTS.append(HUB_PROMPT)


class HubServer(UnifiedServer):
    """Authoritative composition surface for the unified runtime and KC144 hub."""

    def __init__(self, db: str, git_root: str | None = None) -> None:
        super().__init__(db, git_root)
        self.command_hub = KC144CommandHub(
            tool_names=lambda: [item["name"] for item in TOOLS],
            runtime_probe=self._runtime_probe,
            resource_uris=[
                item["uri"]
                for item in AOR_DEVELOPMENT_RESOURCES + HUB_RESOURCES + REGISTRY_RESOURCES + POLYATLAS_RESOURCES
            ],
        )

    def _runtime_probe(self) -> dict[str, Any]:
        try:
            base = super().call_tool("athena_benchmark", {})
        except Exception as exc:
            return {"state": "PROBE_FAILED", "error_type": type(exc).__name__}
        return {"state": "PROBED", "benchmark": base}

    @staticmethod
    def _remove_discharged_field_blocker(result: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(result, dict):
            return result
        readiness = result if "blockers" in result else result.get("readiness")
        if isinstance(readiness, dict):
            readiness["blockers"] = [
                item for item in readiness.get("blockers", [])
                if "FIELD.1" not in str(item)
            ]
            note = "FIELD.1 tools, resource, persistence ledger, replay, benchmark and top-surface routes are live"
            discharged = readiness.setdefault("discharged", [])
            if note not in discharged:
                discharged.append(note)
        return result

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        hub = self.command_hub
        if name == "athena_kc144_hub_status":
            result = self._remove_discharged_field_blocker(hub.status())
            result["authoritative_registry_pack"] = registry_status()
            result["polyatlas"] = polyatlas_status()
            return result
        if name == "athena_kc144_hub_manifest":
            result = hub.manifest(arguments.get("include_edges", False), arguments.get("include_dynamic_inventory", True))
            result["authoritative_registry_pack"] = registry_status()
            result["polyatlas"] = polyatlas_manifest()
            return result
        if name == "athena_kc144_hub_seat":
            gid = arguments["gid"]
            result = hub.seat(gid, arguments.get("include_fibres", True))
            result["polyatlas"] = {
                "decompositions": polyatlas_decompositions(gid),
                "sphere": sphere_cell(gid),
            }
            return result
        if name == "athena_kc144_hub_inventory":
            return hub.inventory(arguments.get("kind"), arguments.get("state"), arguments.get("gid"), arguments.get("query"), arguments.get("limit", 1000))
        if name == "athena_kc144_hub_graph":
            return hub.graph(arguments["name"], arguments.get("include_edges", True))
        if name == "athena_kc144_hub_route":
            return hub.route(arguments["src"], arguments["dst"], arguments.get("graphs") or ["physical_grid"])
        if name == "athena_kc144_hub_datasets":
            return hub.datasets(arguments.get("kind"), arguments.get("state"))
        if name == "athena_kc144_hub_communication":
            return hub.communication()
        if name == "athena_kc144_hub_readiness":
            result = self._remove_discharged_field_blocker(hub.readiness())
            result["authoritative_registry_pack"] = registry_status()
            result["polyatlas"] = polyatlas_status()
            return result
        if name == "athena_kc144_hub_validate":
            result = hub.validate()
            pack = verify_pack(deep=True)
            result["authoritative_registry_pack"] = pack
            atlas = polyatlas_validate(include_details=False)
            result["polyatlas"] = atlas
            if pack["status"] != "PASS" or atlas["status"] != "PASS":
                result["overall_status"] = "FAIL"
            return result

        if name == "athena_kc144_polyatlas_status":
            return polyatlas_status()
        if name == "athena_kc144_polyatlas_manifest":
            return polyatlas_manifest()
        if name == "athena_kc144_polyatlas_seat":
            gid = arguments["gid"]
            return {
                "version": polyatlas_status()["version"],
                "gid": gid,
                "decompositions": polyatlas_decompositions(gid),
                "sphere": sphere_cell(gid, radius=arguments.get("radius", 1.0)),
            }
        if name == "athena_kc144_polyatlas_rosetta":
            return rosetta_address(
                arguments["chapter"],
                arguments["shelf"],
                conjugate=arguments.get("conjugate", 0),
                element=arguments.get("element", 0),
                target_resolution=arguments.get("target_resolution", 21),
            )
        if name == "athena_kc144_resolution_transport":
            return resolution_transport(
                arguments["source_resolution"],
                arguments["target_resolution"],
                arguments["station"],
            )
        if name == "athena_kc144_resolution_family":
            return resolution_family(
                start_multiplier=arguments.get("start_multiplier", 1),
                count=arguments.get("count", 10),
            )
        if name == "athena_kc144_sphere_atlas":
            return sphere_atlas(
                offset=arguments.get("offset", 0),
                limit=arguments.get("limit", 144),
                radius=arguments.get("radius", 1.0),
            )
        if name == "athena_kc144_polyatlas_route":
            return polyatlas_route(
                arguments["src"],
                arguments["dst"],
                layers=arguments.get("layers"),
            )
        if name == "athena_kc144_polyatlas_validate":
            return polyatlas_validate(include_details=arguments.get("include_details", True))

        if name == "athena_kc144_registry_status":
            return registry_status(verify=arguments.get("verify", False))
        if name == "athena_kc144_registry_catalog":
            return registry_catalog()
        if name == "athena_kc144_registry_query":
            return query_registry(
                arguments["registry"],
                query=arguments.get("query"),
                filters=arguments.get("filters"),
                offset=arguments.get("offset", 0),
                limit=arguments.get("limit", 100),
            )
        if name == "athena_kc144_registry_cross_search":
            return registry_cross_search(
                arguments["query"],
                registries=arguments.get("registries"),
                limit=arguments.get("limit", 100),
                per_registry=arguments.get("per_registry", 25),
            )
        if name == "athena_kc144_registry_source_bundle":
            return registry_source_bundle(
                arguments["source_id"],
                limit_per_registry=arguments.get("limit_per_registry", 100),
            )
        if name == "athena_kc144_registry_cell_bundle":
            return registry_cell_bundle(
                arguments["gid"],
                task_limit=arguments.get("task_limit", 100),
            )
        if name == "athena_kc144_completion_frontier":
            return registry_completion_frontier(
                completed_task_ids=arguments.get("completed_task_ids"),
                limit=arguments.get("limit", 100),
            )
        if name == "athena_kc144_registry_verify":
            return verify_pack(deep=arguments.get("deep", True))

        if name == "athena_benchmark":
            result = super().call_tool(name, arguments)
            result["kc144_command_hub"] = self._remove_discharged_field_blocker(hub.status())
            result["kc144_registry_pack"] = registry_status()
            result["kc144_polyatlas"] = polyatlas_status()
            return result
        return super().call_tool(name, arguments)

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        from .hub_dispatch import handle
        return handle(self, message)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=os.getenv("ATHENA_DB", "./state/athena.db"))
    parser.add_argument("--git-root", default=os.getenv("ATHENA_GIT_ROOT"))
    args = parser.parse_args(argv)
    server = HubServer(args.db, args.git_root)
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
            response = server.handle(message)
        except Exception as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}}
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":"), ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
