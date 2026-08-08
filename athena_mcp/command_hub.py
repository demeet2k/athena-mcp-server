from __future__ import annotations

"""Runtime-facing KC144 command hub with measured organism truth."""

from collections import Counter
from copy import deepcopy
from typing import Any, Callable, Iterable

from . import kc144_topology as topo
from .runtime_truth import (
    ACTIVE_PARENT_RUNTIME_SHA,
    INTEGRATION_BASE_SHA,
    overlay_summary,
    runtime_organ_overlay,
    transport_overlay_summary,
)


class KC144CommandHub:
    def __init__(
        self,
        tool_names: Callable[[], Iterable[str]] | None = None,
        runtime_probe: Callable[[], dict[str, Any]] | None = None,
        resource_uris: Iterable[str] | Callable[[], Iterable[str]] = (),
    ) -> None:
        self._tool_names = tool_names or (lambda: ())
        self._runtime_probe = runtime_probe or (lambda: {})
        self._resource_uris = resource_uris

    def _tool_name_snapshot(self) -> tuple[str, ...]:
        return tuple(sorted(set(self._tool_names())))

    def _resource_uri_snapshot(self) -> tuple[str, ...]:
        values = self._resource_uris() if callable(self._resource_uris) else self._resource_uris
        return tuple(sorted(set((*topo.BASE_RESOURCE_URIS, *tuple(values)))))

    def _runtime_overlay(self) -> dict[str, Any]:
        return overlay_summary(self._tool_name_snapshot(), self._resource_uri_snapshot())

    def _transport_overlay(self) -> dict[str, Any]:
        return transport_overlay_summary(
            self._tool_name_snapshot(), self._resource_uri_snapshot()
        )

    def _dynamic_inventory(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for name in self._tool_name_snapshot():
            items.append(
                {
                    "id": f"TOOL.{name}",
                    "kind": "TOOL",
                    "state": "LIVE_DISCOVERED",
                    "gid": topo.stable_carrier_gid(f"TOOL:{name}"),
                    "payload": {"name": name},
                }
            )
        for uri in self._resource_uri_snapshot():
            items.append(
                {
                    "id": f"RESOURCE.{uri}",
                    "kind": "RESOURCE",
                    "state": "LIVE_DISCOVERED",
                    "gid": topo.stable_carrier_gid(f"RESOURCE:{uri}"),
                    "payload": {"uri": uri},
                }
            )
        return items

    def _static_inventory_with_runtime_truth(self) -> list[dict[str, Any]]:
        overlay = runtime_organ_overlay(
            self._tool_name_snapshot(), self._resource_uri_snapshot()
        )
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
            "integration_base_sha": INTEGRATION_BASE_SHA,
            "active_parent_runtime_sha": ACTIVE_PARENT_RUNTIME_SHA,
        }

    def seat(self, gid: int, include_fibres: bool = True) -> dict[str, Any]:
        result = topo.seat(gid)
        if include_fibres:
            result["fibres"] = self.inventory(gid=gid, limit=5000)["items"]
            result["fibre_count"] = len(result["fibres"])
        return result

    def manifest(
        self, include_edges: bool = False, include_dynamic_inventory: bool = True
    ) -> dict[str, Any]:
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
        result["integration_base_sha"] = INTEGRATION_BASE_SHA
        result["active_parent_runtime_sha"] = ACTIVE_PARENT_RUNTIME_SHA
        result["runtime_organ_overlay"] = overlay
        result["runtime_transport_overlay"] = self._transport_overlay()
        result["readiness"] = self.readiness()
        if include_dynamic_inventory:
            inventory = self.inventory(limit=5000)
            result["inventory"] = inventory
            result["runtime_manifest_digest"] = topo.digest(
                {
                    "structural": result["manifest_digest"],
                    "integration_base": INTEGRATION_BASE_SHA,
                    "overlay": overlay,
                    "transports": result["runtime_transport_overlay"],
                    "readiness": result["readiness"],
                    "inventory": inventory["inventory_digest"],
                }
            )
        return result

    def graph(self, name: str, include_edges: bool = True) -> dict[str, Any]:
        return topo.graph(name, include_edges=include_edges)

    def route(
        self, src: int, dst: int, graphs: Iterable[str]
    ) -> dict[str, Any]:
        result = topo.route(src, dst, graphs)
        result["src_seat"] = topo.seat(src)
        result["dst_seat"] = topo.seat(dst)
        result["route_digest"] = topo.digest(
            {
                key: value
                for key, value in result.items()
                if key not in ("src_seat", "dst_seat", "route_digest")
            }
        )
        return result

    def datasets(
        self, kind: str | None = None, state: str | None = None
    ) -> dict[str, Any]:
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
        organ_overlay = self._runtime_overlay()
        transport_overlay = self._transport_overlay()
        for edge in result.get("edges", []):
            transport_id = edge.get("transport_id")
            runtime = (transport_overlay.get("transports") or {}).get(transport_id)
            if runtime is not None:
                edge["structural_state"] = edge.get("state")
                edge["state"] = runtime["state"]
                edge["runtime_overlay"] = runtime
        result["runtime_organ_overlay"] = organ_overlay
        result["runtime_transport_overlay"] = transport_overlay
        result["runtime_digest"] = topo.digest(
            {
                "structural": result["digest"],
                "organs": organ_overlay,
                "transports": transport_overlay,
                "edges": result.get("edges"),
            }
        )
        return result

    def _probe_readiness(self) -> tuple[dict[str, Any], dict[str, Any] | None]:
        try:
            probe = self._runtime_probe() or {}
        except Exception as exc:
            return (
                {"state": "PROBE_FAILED", "error": f"{type(exc).__name__}: {exc}"},
                None,
            )
        measured = probe.get("system_upgrade")
        if not isinstance(measured, dict):
            measured = None
        return probe, measured

    def readiness(self) -> dict[str, Any]:
        structural = deepcopy(topo.readiness())
        overlay = self._runtime_overlay()
        transports = self._transport_overlay()
        probe, measured = self._probe_readiness()
        if measured and isinstance(measured.get("gate_matrix"), dict):
            gate_matrix = measured["gate_matrix"]
            static_by_symbol = {
                item["symbol"]: item for item in topo.READINESS_GATES
            }
            gates = []
            for symbol in ("C", "I", "E", "P", "R", "V", "O", "M", "S", "X"):
                source = static_by_symbol[symbol]
                current = gate_matrix.get(symbol) or {
                    "status": "FAIL",
                    "evidence": {"defect": "measured gate absent"},
                    "boundary": "missing measured gate fails closed",
                }
                gates.append(
                    {
                        "id": source["id"],
                        "symbol": symbol,
                        "gid": source["gid"],
                        "state": current.get("status", "FAIL"),
                        "reason": current.get("boundary"),
                        "evidence": current.get("evidence"),
                        "structural_snapshot_state": source["state"],
                        "structural_snapshot_reason": source["reason"],
                    }
                )
            gate_states = {item["symbol"]: item["state"] for item in gates}
            ready = all(value == "PASS" for value in gate_states.values())
            blockers = [
                {
                    "gate": item["symbol"],
                    "id": item["id"],
                    "evidence": item.get("evidence"),
                    "reason": item.get("reason"),
                }
                for item in gates
                if item["state"] != "PASS"
            ]
            discharged = [
                {
                    "gate": item["symbol"],
                    "id": item["id"],
                    "evidence": item.get("evidence"),
                }
                for item in gates
                if item["state"] == "PASS"
            ]
            return {
                "version": "KC144.IC10.MEASURED.2",
                "equation": structural["equation"],
                "gates": gates,
                "gate_states": gate_states,
                "athena_ready": ready,
                "athena_ready_local": ready,
                "verdict": "PASS_LOCAL" if ready else "HOLD_LOCAL",
                "structural_topology": "PASS",
                "organism_integration": "PASS" if ready else "MEASURED_HOLD",
                "promotion": (
                    "EXTERNAL_EXACT_HEAD_ATTESTATION_REQUIRED"
                    if ready
                    else "BLOCKED_BY_LOCAL_GATES"
                ),
                "blockers": blockers,
                "discharged": discharged,
                "progress_delta": {
                    "live_organs": overlay["live"],
                    "not_live_organs": overlay["not_live"],
                    "live_transports": transports["live"],
                    "not_live_transports": transports["not_live"],
                },
                "snapshot_digest": measured.get("snapshot_digest"),
                "runtime_probe": {
                    "state": probe.get("state"),
                    "system_upgrade_status": measured.get("status"),
                },
                "boundary": (
                    "PASS_LOCAL is measured local readiness only. Merge, deployment, empirical "
                    "truth and exact-head external promotion remain separately gated."
                ),
            }
        blockers = [
            {
                "gate": "O",
                "id": "IC07.OBSERVABILITY",
                "reason": "whole-system runtime probe did not return a measured gate matrix",
            }
        ]
        return {
            **structural,
            "version": "KC144.IC10.MEASURED.2",
            "athena_ready_local": False,
            "verdict": "HOLD_LOCAL",
            "organism_integration": "MEASUREMENT_UNAVAILABLE",
            "promotion": "BLOCKED_BY_LOCAL_GATES",
            "blockers": blockers,
            "discharged": [],
            "runtime_organ_overlay": overlay,
            "runtime_transport_overlay": transports,
            "runtime_probe": probe,
            "boundary": "absence of a measured runtime packet fails closed; structural snapshot does not self-promote",
        }

    def validate(self) -> dict[str, Any]:
        result = topo.validate_topology()
        tool_names = list(self._tool_name_snapshot())
        resource_uris = list(self._resource_uri_snapshot())
        overlay = self._runtime_overlay()
        transports = self._transport_overlay()
        raw_organs = overlay["organs"]
        overlay_consistent = all(
            value["surface_pass"]
            == (not value["missing_tools"] and not value["missing_resources"])
            for value in raw_organs.values()
        )
        transport_consistent = all(
            value["surface_pass"]
            == (not value["missing_tools"] and not value["missing_resources"])
            for value in transports["transports"].values()
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
                "pass": sum(
                    1 for name in tool_names if name.startswith("athena_kc144_hub_")
                )
                == 10,
                "observed": sum(
                    1 for name in tool_names if name.startswith("athena_kc144_hub_")
                ),
                "expected": 10,
            },
            {
                "id": "COMPLETE_RUNTIME_ORGAN_SURFACE_LIVE",
                "pass": overlay["all_required_live"],
                "observed": {
                    organ: value["state"] for organ, value in raw_organs.items()
                },
                "expected": "all declared runtime organs surface-pass",
            },
            {
                "id": "COMPLETE_TRANSPORT_MEMBRANE_LIVE",
                "pass": transports["all_required_live"],
                "observed": {
                    transport: value["state"]
                    for transport, value in transports["transports"].items()
                },
                "expected": "all declared typed transports surface-pass",
            },
            {
                "id": "RUNTIME_STATE_DERIVED_NOT_FABRICATED",
                "pass": overlay_consistent and transport_consistent,
                "observed": {
                    "organs_consistent": overlay_consistent,
                    "transports_consistent": transport_consistent,
                },
                "expected": "surface_pass iff every declared tool and resource is discovered",
            },
        ]
        result["runtime_checks"] = runtime_checks
        result["runtime_organ_overlay"] = raw_organs
        result["runtime_transport_overlay"] = transports["transports"]
        result["runtime_status"] = (
            "PASS" if all(item["pass"] for item in runtime_checks) else "FAIL"
        )
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
        readiness = self.readiness()
        probe = self._runtime_probe()
        if validation["overall_status"] != "PASS":
            state = "TOPOLOGY_OR_RUNTIME_SURFACE_FAIL__LOCAL_AND_PROMOTION_HOLD"
        elif readiness.get("athena_ready_local"):
            state = (
                "TOPOLOGY_PASS__RUNTIME_SURFACE_PASS__LOCAL_READY__"
                "EXTERNAL_PROMOTION_REQUIRED"
            )
        else:
            state = "TOPOLOGY_PASS__RUNTIME_SURFACE_PASS__LOCAL_GATES_HOLD"
        return {
            "id": topo.HUB_VERSION,
            "state": state,
            "entrypoint": "athena_mcp.hub_server:main",
            "integration_base_sha": INTEGRATION_BASE_SHA,
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
                "resources": sum(
                    1 for item in dynamic if item["kind"] == "RESOURCE"
                ),
            },
            "validation": {
                "status": validation["overall_status"],
                "receipt": validation["overall_receipt_digest"],
            },
            "runtime_organ_overlay": self._runtime_overlay(),
            "runtime_transport_overlay": self._transport_overlay(),
            "readiness": readiness,
            "runtime_probe": probe,
            "authority_boundary": (
                "Measured command center; no automatic truth promotion, merge, deployment "
                "or production authority. Exact-head release requires RELCERT/PROMRUN witnesses."
            ),
        }
