from __future__ import annotations

"""Runtime-facing KC144 command hub."""

from collections import Counter
from copy import deepcopy
from typing import Any, Callable, Iterable

from . import kc144_topology as topo
from .runtime_truth import ACTIVE_PARENT_RUNTIME_SHA, overlay_summary, runtime_organ_overlay


class KC144CommandHub:
    def __init__(
        self,
        tool_names: Callable[[], Iterable[str]] | None = None,
        runtime_probe: Callable[[], dict[str, Any]] | None = None,
        resource_uris: Iterable[str] = (),
    ) -> None:
        self._tool_names = tool_names or (lambda: ())
        self._runtime_probe = runtime_probe or (lambda: {})
        self._resource_uris = tuple(resource_uris)

    def _tool_name_snapshot(self) -> tuple[str, ...]:
        return tuple(sorted(set(self._tool_names())))

    def _resource_uri_snapshot(self) -> tuple[str, ...]:
        return tuple(sorted(set((*topo.BASE_RESOURCE_URIS, *self._resource_uris))))

    def _runtime_overlay(self) -> dict[str, Any]:
        return overlay_summary(self._tool_name_snapshot(), self._resource_uri_snapshot())

    def _dynamic_inventory(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for name in self._tool_name_snapshot():
            items.append({
                "id": f"TOOL.{name}",
                "kind": "TOOL",
                "state": "LIVE_DISCOVERED",
                "gid": topo.stable_carrier_gid(f"TOOL:{name}"),
                "payload": {"name": name},
            })
        for uri in self._resource_uri_snapshot():
            items.append({
                "id": f"RESOURCE.{uri}",
                "kind": "RESOURCE",
                "state": "LIVE_DISCOVERED",
                "gid": topo.stable_carrier_gid(f"RESOURCE:{uri}"),
                "payload": {"uri": uri},
            })
        return items

    def _static_inventory_with_runtime_truth(self) -> list[dict[str, Any]]:
        overlay = runtime_organ_overlay(self._tool_name_snapshot(), self._resource_uri_snapshot())
        items: list[dict[str, Any]] = []
        for original in topo.static_inventory():
            item = deepcopy(original)
            runtime = overlay.get(item["id"])
            if runtime is not None:
                item["structural_state"] = item["state"]
                item["state"] = runtime["state"]
                payload = dict(item.get("payload") or {})
                payload["runtime_overlay"] = runtime
                item["payload"] = payload
            items.append(item)
        return items

    def inventory(
        self,
        kind: str | None = None,
        state: str | None = None,
        gid: int | None = None,
        query: str | None = None,
        limit: int = 1000,
    ) -> dict[str, Any]:
        if not 1 <= limit <= 5000:
            raise ValueError("limit must be in 1..5000")
        items = self._static_inventory_with_runtime_truth() + self._dynamic_inventory()
        needle = query.casefold() if query else None
        filtered = []
        for item in items:
            if kind and item["kind"] != kind:
                continue
            if state and item["state"] != state:
                continue
            if gid is not None and item["gid"] != gid:
                continue
            if needle and needle not in topo.canonical_json(item).casefold():
                continue
            filtered.append(item)
        filtered.sort(key=lambda item: (item["gid"], item["kind"], item["id"]))
        counts = Counter(item["kind"] for item in filtered)
        return {
            "total": len(filtered),
            "returned": min(len(filtered), limit),
            "counts_by_kind": dict(sorted(counts.items())),
            "items": filtered[:limit],
            "inventory_digest": topo.digest(filtered),
            "active_parent_runtime_sha": ACTIVE_PARENT_RUNTIME_SHA,
        }

    def seat(self, gid: int, include_fibres: bool = True) -> dict[str, Any]:
        result = topo.seat(gid)
        if include_fibres:
            result["fibres"] = self.inventory(gid=gid, limit=5000)["items"]
            result["fibre_count"] = len(result["fibres"])
        return result

    def manifest(self, include_edges: bool = False, include_dynamic_inventory: bool = True) -> dict[str, Any]:
        result = topo.manifest(include_edges=include_edges)
        overlay = self._runtime_overlay()
        overlay_by_id = overlay["organs"]
        for organ in result["organs"]:
            runtime = overlay_by_id.get(organ["id"])
            if runtime is not None:
                organ["structural_state"] = organ["state"]
                organ["state"] = runtime["state"]
                organ["runtime_overlay"] = runtime
        result["structural_source_snapshot_sha"] = result["parent_runtime_sha"]
        result["active_parent_runtime_sha"] = ACTIVE_PARENT_RUNTIME_SHA
        result["runtime_organ_overlay"] = overlay
        if include_dynamic_inventory:
            inventory = self.inventory(limit=5000)
            result["inventory"] = inventory
            result["runtime_manifest_digest"] = topo.digest({
                "structural": result["manifest_digest"],
                "active_parent": ACTIVE_PARENT_RUNTIME_SHA,
                "overlay": overlay,
                "inventory": inventory["inventory_digest"],
            })
        return result

    def graph(self, name: str, include_edges: bool = True) -> dict[str, Any]:
        return topo.graph(name, include_edges=include_edges)

    def route(self, src: int, dst: int, graphs: Iterable[str]) -> dict[str, Any]:
        result = topo.route(src, dst, graphs)
        result["src_seat"] = topo.seat(src)
        result["dst_seat"] = topo.seat(dst)
        result["route_digest"] = topo.digest({
            key: value
            for key, value in result.items()
            if key not in ("src_seat", "dst_seat", "route_digest")
        })
        return result

    def datasets(self, kind: str | None = None, state: str | None = None) -> dict[str, Any]:
        items = [dict(item) for item in topo.SOURCE_DATASETS]
        if kind:
            items = [item for item in items if item["kind"] == kind]
        if state:
            items = [item for item in items if item["state"] == state]
        return {
            "count": len(items),
            "items": items,
            "digest": topo.digest(items),
            "boundary": "index and source locator only; raw bodies are not copied into Git",
        }

    def communication(self) -> dict[str, Any]:
        result = deepcopy(topo.communication_graph())
        result["runtime_organ_overlay"] = self._runtime_overlay()
        result["runtime_digest"] = topo.digest({
            "structural": result["digest"],
            "overlay": result["runtime_organ_overlay"],
        })
        return result

    def readiness(self) -> dict[str, Any]:
        result = deepcopy(topo.readiness())
        overlay = self._runtime_overlay()
        result["runtime_organ_overlay"] = overlay
        result["progress_delta"] = {
            "newly_live_since_structural_snapshot": overlay["live"],
            "not_live": overlay["not_live"],
        }
        result["blockers"] = [
            "mount FIELD.1 provenance-preserving candidate assembly on the unified surface",
            "braid SURFACE.1, COMPOSITION.1, and PROMOTION.1 after FIELD.1",
            "mechanize pheromone->RAG, JSPACE alarm->GAP, witnessed RGO->reward, and AOR->Collective resource-demand transports",
            "run exact-head whole-suite, smoke, migration, surface, and composition witnesses after every parent rebase",
            "produce replayable exact-head promotion and source-return receipts without rewriting historical promotion",
        ]
        return result

    def validate(self) -> dict[str, Any]:
        result = topo.validate_topology()
        tool_names = list(self._tool_name_snapshot())
        resource_uris = list(self._resource_uri_snapshot())
        overlay = runtime_organ_overlay(tool_names, resource_uris)
        integrated_prefix = (
            "ORGAN.EQ1",
            "ORGAN.SX1",
            "ORGAN.RAG1",
            "ORGAN.HUG_ABI1",
            "ORGAN.GAP1",
        )
        prefix_live = all(overlay[organ]["surface_pass"] for organ in integrated_prefix)
        overlay_consistent = all(
            value["surface_pass"]
            == (not value["missing_tools"] and not value["missing_resources"])
            for value in overlay.values()
        )
        runtime_checks = [
            {
                "id": "LIVE_TOOL_NAMES_UNIQUE",
                "pass": len(tool_names) == len(set(tool_names)),
                "observed": len(tool_names),
                "expected": len(set(tool_names)),
            },
            {
                "id": "LIVE_RESOURCE_URIS_UNIQUE",
                "pass": len(resource_uris) == len(set(resource_uris)),
                "observed": len(resource_uris),
                "expected": len(set(resource_uris)),
            },
            {
                "id": "COMMAND_HUB_TOOL_COUNT",
                "pass": sum(1 for name in tool_names if name.startswith("athena_kc144_hub_")) == 10,
                "observed": sum(1 for name in tool_names if name.startswith("athena_kc144_hub_")),
                "expected": 10,
            },
            {
                "id": "EQ_SX_RAG_HUG_GAP_SURFACE_LIVE",
                "pass": prefix_live,
                "observed": [overlay[organ]["state"] for organ in integrated_prefix],
                "expected": [
                    "LIVE_UNIFIED",
                    "LIVE_UNIFIED",
                    "LIVE_UNIFIED",
                    "LIVE_UNIFIED_FAIL_CLOSED",
                    "LIVE_UNIFIED",
                ],
            },
            {
                "id": "RUNTIME_ORGAN_STATE_DERIVED_NOT_FABRICATED",
                "pass": overlay_consistent,
                "observed": {organ: value["state"] for organ, value in overlay.items()},
                "expected": "surface_pass iff every declared tool and resource is discovered",
            },
        ]
        result["runtime_checks"] = runtime_checks
        result["runtime_organ_overlay"] = overlay
        result["runtime_status"] = "PASS" if all(item["pass"] for item in runtime_checks) else "FAIL"
        result["overall_status"] = (
            "PASS"
            if result["status"] == "PASS" and result["runtime_status"] == "PASS"
            else "FAIL"
        )
        result["overall_receipt_digest"] = topo.digest(result)
        return result

    def status(self) -> dict[str, Any]:
        validation = self.validate()
        dynamic = self._dynamic_inventory()
        runtime = self._runtime_probe()
        return {
            "id": topo.HUB_VERSION,
            "state": (
                "TOPOLOGY_PASS__RUNTIME_SURFACE_PASS__ORGANISM_INTEGRATION_PARTIAL__PROMOTION_HOLD"
                if validation["overall_status"] == "PASS"
                else "TOPOLOGY_OR_RUNTIME_SURFACE_FAIL__PROMOTION_HOLD"
            ),
            "entrypoint": "athena_mcp.hub_server:main",
            "active_parent_runtime_sha": ACTIVE_PARENT_RUNTIME_SHA,
            "structural_source_snapshot_sha": topo.PARENT_RUNTIME_SHA,
            "full_aor_source_sha": topo.FULL_AOR_SOURCE_SHA,
            "git_brain_source_sha": topo.GIT_BRAIN_SOURCE_SHA,
            "topology": {
                "seats": 144,
                "bands": 8,
                "coordinate_systems": len(topo.COORDINATE_SYSTEMS),
                "graphs": len(topo.GRAPH_BUILDERS) + 2,
            },
            "inventory": {
                "static": len(topo.static_inventory()),
                "dynamic": len(dynamic),
                "tools": sum(1 for item in dynamic if item["kind"] == "TOOL"),
                "resources": sum(1 for item in dynamic if item["kind"] == "RESOURCE"),
            },
            "validation": {
                "status": validation["overall_status"],
                "receipt": validation["overall_receipt_digest"],
            },
            "runtime_organ_overlay": self._runtime_overlay(),
            "readiness": self.readiness(),
            "runtime_probe": runtime,
            "authority_boundary": "structural command center; no truth promotion, merge, deployment, or production authority",
        }
