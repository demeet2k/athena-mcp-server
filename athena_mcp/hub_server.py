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
from .system_upgrade import SystemUpgradeRuntime
from .system_upgrade_protocol import (
    SYSTEM_UPGRADE_PROMPT,
    SYSTEM_UPGRADE_RESOURCES,
    SYSTEM_UPGRADE_TOOLS,
)

_existing_tools = {item["name"] for item in TOOLS}
for tool in HUB_TOOLS + REGISTRY_TOOLS + POLYATLAS_TOOLS + SYSTEM_UPGRADE_TOOLS:
    if tool["name"] not in _existing_tools:
        TOOLS.append(tool)
        _existing_tools.add(tool["name"])

_existing_prompts = {item["name"] for item in PROMPTS}
for prompt in (HUB_PROMPT, SYSTEM_UPGRADE_PROMPT):
    if prompt["name"] not in _existing_prompts:
        PROMPTS.append(prompt)
        _existing_prompts.add(prompt["name"])


class HubServer(UnifiedServer):
    """Canonical composed runtime: unified organism + KC144 + system upgrade plane."""

    def __init__(self, db: str, git_root: str | None = None) -> None:
        super().__init__(db, git_root)
        self.command_hub = KC144CommandHub(
            tool_names=lambda: [item["name"] for item in TOOLS],
            runtime_probe=self._runtime_probe,
            resource_uris=self._all_resource_uris,
        )
        self.system_upgrade = SystemUpgradeRuntime(
            self, self.aor_development.integrity
        )

    def _base_resource_uris(self) -> list[str]:
        response = UnifiedServer.handle(
            self,
            {
                "jsonrpc": "2.0",
                "id": "hub:base-resources",
                "method": "resources/list",
            },
        )
        return [
            item["uri"]
            for item in ((response or {}).get("result") or {}).get("resources", [])
        ]

    def _all_resource_uris(self) -> list[str]:
        values = self._base_resource_uris()
        values.extend(
            item["uri"]
            for item in (
                list(AOR_DEVELOPMENT_RESOURCES)
                + HUB_RESOURCES
                + REGISTRY_RESOURCES
                + POLYATLAS_RESOURCES
                + SYSTEM_UPGRADE_RESOURCES
            )
        )
        return sorted(set(values))

    def _runtime_probe(self) -> dict[str, Any]:
        try:
            base = super().call_tool("athena_benchmark", {})
            system = getattr(self, "system_upgrade", None)
            snapshot = (
                system.local_snapshot(run_replay_samples=False)
                if system is not None
                else {
                    "status": "INITIALIZING",
                    "athena_ready_local": False,
                    "gate_matrix": {},
                }
            )
        except Exception as exc:
            return {
                "state": "PROBE_FAILED",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        return {
            "state": "PROBED",
            "benchmark": base,
            "system_upgrade": snapshot,
        }

    @staticmethod
    def _remove_discharged_field_blocker(
        result: dict[str, Any],
    ) -> dict[str, Any]:
        """Compatibility shim retained for older callers; readiness is now measured."""
        return result

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        hub = self.command_hub
        system = self.system_upgrade

        if name == "athena_system_upgrade_manifest":
            return system.manifest()
        if name == "athena_system_upgrade_plan":
            return system.plan(
                arguments["objective"],
                target_version=arguments.get("target_version", "2.6.0"),
                expected_git_head=arguments.get("expected_git_head"),
                completion_witnesses=arguments.get("completion_witnesses"),
                actor=arguments.get("actor", "agent"),
                persist=arguments.get("persist", True),
            )
        if name == "athena_system_upgrade_state":
            return system.state(arguments["run_id"])
        if name == "athena_system_upgrade_observe":
            return system.observe(
                arguments["run_id"],
                arguments["task_id"],
                arguments["witness"],
                arguments["expected_state_digest"],
                require_exact_head=arguments.get("require_exact_head", False),
                refresh_local=arguments.get("refresh_local", True),
                actor=arguments.get("actor", "agent"),
            )
        if name == "athena_system_upgrade_refresh":
            return system.refresh(
                arguments["run_id"],
                arguments["expected_state_digest"],
                run_replay_samples=arguments.get("run_replay_samples", True),
                actor=arguments.get("actor", "agent"),
            )
        if name == "athena_system_upgrade_replay":
            return system.replay(arguments["run_id"])
        if name == "athena_system_upgrade_recent":
            return system.recent(arguments.get("limit", 50))
        if name == "athena_system_release_certificate":
            return system.release_certificate(
                arguments["run_id"],
                arguments["git_head"],
                arguments["ci_witness"],
                arguments["smoke_witness"],
                require_source_completion=arguments.get(
                    "require_source_completion", False
                ),
                actor=arguments.get("actor", "agent"),
                persist=arguments.get("persist", True),
            )
        if name == "athena_system_release_get":
            return system.release_get(arguments["certificate_id"])
        if name == "athena_system_release_replay":
            return system.release_replay(arguments["certificate_id"])
        if name == "athena_system_release_recent":
            return system.release_recent(arguments.get("limit", 50))

        if name == "athena_kc144_hub_status":
            result = hub.status()
            result["authoritative_registry_pack"] = registry_status()
            result["polyatlas"] = polyatlas_status()
            result["system_upgrade"] = system.manifest()
            return result
        if name == "athena_kc144_hub_manifest":
            result = hub.manifest(
                arguments.get("include_edges", False),
                arguments.get("include_dynamic_inventory", True),
            )
            result["authoritative_registry_pack"] = registry_status()
            result["polyatlas"] = polyatlas_manifest()
            result["system_upgrade"] = system.manifest()
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
            return hub.inventory(
                arguments.get("kind"),
                arguments.get("state"),
                arguments.get("gid"),
                arguments.get("query"),
                arguments.get("limit", 1000),
            )
        if name == "athena_kc144_hub_graph":
            return hub.graph(
                arguments["name"], arguments.get("include_edges", True)
            )
        if name == "athena_kc144_hub_route":
            return hub.route(
                arguments["src"],
                arguments["dst"],
                arguments.get("graphs") or ["physical_grid"],
            )
        if name == "athena_kc144_hub_datasets":
            return hub.datasets(
                arguments.get("kind"), arguments.get("state")
            )
        if name == "athena_kc144_hub_communication":
            return hub.communication()
        if name == "athena_kc144_hub_readiness":
            result = hub.readiness()
            result["authoritative_registry_pack"] = registry_status()
            result["polyatlas"] = polyatlas_status()
            result["system_upgrade"] = system.manifest()
            return result
        if name == "athena_kc144_hub_validate":
            result = hub.validate()
            pack = verify_pack(deep=True)
            atlas = polyatlas_validate(include_details=False)
            result["authoritative_registry_pack"] = pack
            result["polyatlas"] = atlas
            result["system_upgrade"] = {
                "manifest": system.manifest(),
                "local_snapshot": system.local_snapshot(
                    run_replay_samples=False
                ),
            }
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
                "sphere": sphere_cell(
                    gid, radius=arguments.get("radius", 1.0)
                ),
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
            return polyatlas_validate(
                include_details=arguments.get("include_details", True)
            )

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
            result["kc144_command_hub"] = hub.status()
            result["kc144_registry_pack"] = registry_status()
            result["kc144_polyatlas"] = polyatlas_status()
            result.update(system.benchmark())
            return result
        return super().call_tool(name, arguments)

    def handle(
        self, message: dict[str, Any]
    ) -> dict[str, Any] | None:
        from .hub_dispatch import handle

        return handle(self, message)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db", default=os.getenv("ATHENA_DB", "./state/athena.db")
    )
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
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {exc}",
                },
            }
        if response is not None:
            sys.stdout.write(
                json.dumps(
                    response,
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
                + "\n"
            )
            sys.stdout.flush()


if __name__ == "__main__":
    main()
