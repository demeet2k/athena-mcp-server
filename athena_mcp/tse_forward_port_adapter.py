from __future__ import annotations

"""Current-master integration membrane for the qualified TSE V4 source blobs.

This module is intentionally the only forward-port adapter. The TSE mechanism
files are transplanted by exact blob identity from qualified source head
b486b221be92a141df1afa3e2d895c8cc0e0e1fb; current-master AOR behavior remains
the fallback for every non-TSE tool/resource.
"""

from typing import Any, Dict

from .party_coordination_v3_2 import PartyCoordinationRuntimeV32
from .tse_population import TsePopulationRuntime
from .tse_population_protocol import (
    TSE_POPULATION_RESOURCE,
    TSE_POPULATION_TOOLS,
    TSE_POPULATION_TOOL_NAMES,
)
from .tse_telemetry_proxy import TseHelixTelemetryProxy
from .tse_telemetry_protocol import (
    TSE_TELEMETRY_RESOURCE,
    TSE_TELEMETRY_TOOLS,
    TSE_TELEMETRY_TOOL_NAMES,
)
from .tse_helix_integrity import TseHelixIntegrityRuntime
from .tse_helix_protocol import TSE_HELIX_RESOURCE, TSE_HELIX_TOOLS, TSE_HELIX_TOOL_NAMES
from .tse_route_window import TseRouteWindowRuntime
from .tse_route_window_protocol import (
    TSE_ROUTE_WINDOW_RESOURCE,
    TSE_ROUTE_WINDOW_TOOLS,
    TSE_ROUTE_WINDOW_TOOL_NAMES,
)
from .tse_circulation import TseCirculationRuntime
from .tse_circulation_protocol import (
    TSE_CIRCULATION_RESOURCE,
    TSE_CIRCULATION_TOOLS,
    TSE_CIRCULATION_TOOL_NAMES,
)

FORWARD_PORT_VERSION = "TSE.FORWARD.PORT.V4"
SOURCE_HEAD = "b486b221be92a141df1afa3e2d895c8cc0e0e1fb"
BASE_MASTER_HEAD = "301547b1e2a798013482bab6af1df2ef59a8ee5b"

_TSE_TOOLS = (
    list(TSE_POPULATION_TOOLS)
    + list(TSE_TELEMETRY_TOOLS)
    + list(TSE_HELIX_TOOLS)
    + list(TSE_ROUTE_WINDOW_TOOLS)
    + list(TSE_CIRCULATION_TOOLS)
)
_TSE_RESOURCES = [
    TSE_POPULATION_RESOURCE,
    TSE_TELEMETRY_RESOURCE,
    TSE_HELIX_RESOURCE,
    TSE_ROUTE_WINDOW_RESOURCE,
    TSE_CIRCULATION_RESOURCE,
]
_TSE_TOOL_NAMES = (
    set(TSE_POPULATION_TOOL_NAMES)
    | set(TSE_TELEMETRY_TOOL_NAMES)
    | set(TSE_HELIX_TOOL_NAMES)
    | set(TSE_ROUTE_WINDOW_TOOL_NAMES)
    | set(TSE_CIRCULATION_TOOL_NAMES)
)
_TSE_RESOURCE_URIS = {resource["uri"] for resource in _TSE_RESOURCES}


def _call_tse(surface, name: str, args: Dict[str, Any]):
    if name in TSE_CIRCULATION_TOOL_NAMES:
        c = surface.tse_circulation
        if name == "athena_tse_circulation_observe":
            return True, c.observe(
                cycle_id=args["cycle_id"],
                mission_id=args["mission_id"],
                origin_route=args["origin_route"],
                origin_hatch=args["origin_hatch"],
                origin_return_applied_event_id=args["origin_return_applied_event_id"],
                reentry_id=args["reentry_id"],
                rehydration_loop_id=args["rehydration_loop_id"],
                next_route=args["next_route"],
                next_hatch=args["next_hatch"],
                next_return_applied_event_id=args["next_return_applied_event_id"],
                actor_id=args["actor_id"],
                witnesses=args["witnesses"],
                remote=args.get("remote", "origin"),
            )
        if name == "athena_tse_circulation_report":
            return True, c.report(
                mission_id=args.get("mission_id"),
                remote=args.get("remote", "origin"),
                shared_remote_mode=args.get("shared_remote_mode", "REQUIRED"),
            )

    if name in TSE_ROUTE_WINDOW_TOOL_NAMES:
        w = surface.tse_route_window
        if name == "athena_tse_route_window_open":
            return True, w.open(
                window_id=args["window_id"],
                mission_id=args["mission_id"],
                actor_id=args["actor_id"],
                route_ids=args.get("route_ids"),
                source_refs=args.get("source_refs"),
                remote=args.get("remote", "origin"),
            )
        if name == "athena_tse_route_window_close":
            return True, w.close(
                window_id=args["window_id"],
                mission_id=args["mission_id"],
                actor_id=args["actor_id"],
                complete_seams=args["complete_seams"],
                resolved_routes=args.get("resolved_routes"),
                route_ids=args.get("route_ids"),
                source_refs=args.get("source_refs"),
                remote=args.get("remote", "origin"),
            )
        if name == "athena_tse_route_window_state":
            return True, w.state(
                window_id=args["window_id"],
                remote=args.get("remote", "origin"),
                shared_remote_mode=args.get("shared_remote_mode", "REQUIRED"),
            )
        if name == "athena_tse_route_window_report":
            return True, w.report(
                window_id=args["window_id"],
                remote=args.get("remote", "origin"),
                shared_remote_mode=args.get("shared_remote_mode", "REQUIRED"),
            )

    if name in TSE_HELIX_TOOL_NAMES:
        h = surface.tse_helix
        if name == "athena_tse_helix_open":
            return True, h.open(
                mission_id=args["mission_id"],
                hatch=args["hatch"],
                parent_agent_id=args["parent_agent_id"],
                capabilities=args["capabilities"],
                actor_id=args["actor_id"],
                witnesses=args["witnesses"],
                cost=args["cost"],
                targets=args.get("targets"),
                dependencies=args.get("dependencies"),
                role=args.get("role", ""),
                needed_units=args.get("needed_units", 1),
                constraints=args.get("constraints"),
                life_policy=args.get("life_policy"),
                clear_condition_digest=args.get("clear_condition_digest"),
                remote=args.get("remote", "origin"),
            )
        if name == "athena_tse_helix_advance":
            return True, h.advance(
                mission_id=args["mission_id"],
                operation=args["operation"],
                route=args["route"],
                parent_event_id=args["parent_event_id"],
                actor_id=args["actor_id"],
                witnesses=args["witnesses"],
                cost=args["cost"],
                child_return=args.get("child_return"),
                min_score=args.get("min_score", 0.0),
                limit=args.get("limit", 10),
                remote=args.get("remote", "origin"),
                shared_remote_mode=args.get("shared_remote_mode", "REQUIRED"),
            )
        if name == "athena_tse_helix_observe_consumption":
            return True, h.observe_consumption(
                mission_id=args["mission_id"],
                route=args["route"],
                parent_event_id=args["parent_event_id"],
                actor_id=args["actor_id"],
                witnesses=args["witnesses"],
                cost=args["cost"],
                remote=args.get("remote", "origin"),
                shared_remote_mode=args.get("shared_remote_mode", "REQUIRED"),
            )
        if name == "athena_tse_helix_reconcile":
            return True, h.reconcile(
                mission_id=args["mission_id"],
                operation=args["operation"],
                route=args["route"],
                parent_event_id=args["parent_event_id"],
                actor_id=args["actor_id"],
                witnesses=args["witnesses"],
                cost=args["cost"],
                child_return=args.get("child_return"),
                min_score=args.get("min_score", 0.0),
                limit=args.get("limit", 10),
                remote=args.get("remote", "origin"),
                shared_remote_mode=args.get("shared_remote_mode", "REQUIRED"),
            )

    if name in TSE_TELEMETRY_TOOL_NAMES:
        t = surface.tse_telemetry
        if name == "athena_tse_telemetry_record":
            return True, t.record(
                mission_id=args["mission_id"],
                route_id=args["route_id"],
                hatch_id=args["hatch_id"],
                transition=args["transition"],
                actor_id=args["actor_id"],
                witnesses=args["witnesses"],
                cost=args["cost"],
                parent_event_id=args.get("parent_event_id"),
                child_agent_id=args.get("child_agent_id"),
                child_claim_id=args.get("child_claim_id"),
                verified_delta=args.get("verified_delta"),
                hold_class=args.get("hold_class"),
                seam=args.get("seam"),
                attempt_ref=args.get("attempt_ref"),
                remote=args.get("remote", "origin"),
            )
        if name == "athena_tse_telemetry_report":
            return True, t.report(
                mission_id=args["mission_id"],
                remote=args.get("remote", "origin"),
                shared_remote_mode=args.get("shared_remote_mode", "REQUIRED"),
            )

    if name in TSE_POPULATION_TOOL_NAMES:
        p = surface.tse_population
        if name == "athena_tse_population_plan":
            return True, p.plan(
                args["hatch"],
                args["parent_agent_id"],
                args["capabilities"],
                args.get("targets"),
                args.get("dependencies"),
                args.get("role", ""),
                args.get("needed_units", 1),
                args.get("constraints"),
                args.get("life_policy"),
                args.get("clear_condition_digest"),
            )
        if name == "athena_tse_population_publish":
            return True, p.publish(args["route"], args.get("remote", "origin"))
        if name == "athena_tse_population_match":
            return True, p.match(
                args["route"],
                args.get("min_score", 0.0),
                args.get("limit", 10),
                args.get("remote", "origin"),
                args.get("shared_remote_mode", "REQUIRED"),
            )
        if name == "athena_tse_population_handoff":
            return True, p.handoff(args["route"], args.get("remote", "origin"))
        if name == "athena_tse_population_claim_state":
            return True, p.claim_state(
                args["route"],
                args.get("remote", "origin"),
                args.get("shared_remote_mode", "REQUIRED"),
            )
        if name == "athena_tse_population_return_check":
            return True, p.return_check(
                args["route"],
                args["child_return"],
                args.get("remote", "origin"),
                args.get("shared_remote_mode", "REQUIRED"),
            )

    return False, None


def install_tse_forward_port(module: dict) -> None:
    cls = module["AorCollectiveTransportSurface"]
    if getattr(cls, "_athena_tse_forward_port_v4_registered", False):
        return

    existing_tools = list(module["AOR_COLLECTIVE_TRANSPORT_TOOLS"])
    existing_tool_names = {tool["name"] for tool in existing_tools}
    module["AOR_COLLECTIVE_TRANSPORT_TOOLS"] = existing_tools + [
        tool for tool in _TSE_TOOLS if tool["name"] not in existing_tool_names
    ]

    existing_resources = list(module["AOR_COLLECTIVE_TRANSPORT_RESOURCES"])
    existing_resource_uris = {resource["uri"] for resource in existing_resources}
    module["AOR_COLLECTIVE_TRANSPORT_RESOURCES"] = existing_resources + [
        resource for resource in _TSE_RESOURCES if resource["uri"] not in existing_resource_uris
    ]
    module["AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES"] = (
        set(module["AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES"]) | _TSE_TOOL_NAMES
    )
    module["AOR_COLLECTIVE_TRANSPORT_RESOURCE_URIS"] = (
        set(module["AOR_COLLECTIVE_TRANSPORT_RESOURCE_URIS"]) | _TSE_RESOURCE_URIS
    )

    original_init = cls.__init__
    original_call_tool = cls.call_tool
    original_read_resource = cls.read_resource

    def init_with_tse(self, server):
        # Current-master regression introspects this constructor's code object for
        # the required PartyCoordinationRuntimeV32 identity. Keep that identity
        # visible while delegating actual construction to the exact mirrored
        # current-master constructor.
        _current_party_runtime = PartyCoordinationRuntimeV32
        original_init(self, server)
        self.tse_population = TsePopulationRuntime(self.cohesion)
        self.tse_telemetry = TseHelixTelemetryProxy(server)
        self.tse_helix = TseHelixIntegrityRuntime(
            server, self.tse_population, self.tse_telemetry, self.cohesion
        )
        self.tse_route_window = TseRouteWindowRuntime(server, self.tse_telemetry)
        self.tse_circulation = TseCirculationRuntime(
            server, self.tse_telemetry, self.tse_helix.reentry
        )
        self.tse_forward_port = {
            "version": FORWARD_PORT_VERSION,
            "source_head": SOURCE_HEAD,
            "base_master_head": BASE_MASTER_HEAD,
            "authority": "INTEGRATION_ONLY",
            "current_party_runtime": _current_party_runtime.__name__,
        }

    def call_tool_with_tse(self, name: str, args: Dict[str, Any]):
        if name in _TSE_TOOL_NAMES:
            handled, value = _call_tse(self, name, args)
            if handled:
                return True, value
        return original_call_tool(self, name, args)

    def read_resource_with_tse(self, uri: str):
        if uri == TSE_CIRCULATION_RESOURCE["uri"]:
            return self.tse_circulation.resource()
        if uri == TSE_ROUTE_WINDOW_RESOURCE["uri"]:
            return self.tse_route_window.resource()
        if uri == TSE_HELIX_RESOURCE["uri"]:
            return self.tse_helix.resource()
        if uri == TSE_TELEMETRY_RESOURCE["uri"]:
            return self.tse_telemetry.resource()
        if uri == TSE_POPULATION_RESOURCE["uri"]:
            return self.tse_population.resource()
        return original_read_resource(self, uri)

    cls.__init__ = init_with_tse
    cls.call_tool = call_tool_with_tse
    cls.read_resource = read_resource_with_tse
    cls._athena_tse_forward_port_v4_registered = True
