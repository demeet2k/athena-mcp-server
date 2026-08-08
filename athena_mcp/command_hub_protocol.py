from __future__ import annotations

HUB_TOOLS = [
    {"name": "athena_kc144_hub_status", "description": "Return the live topological command-center status, exact source lineage, structural validation, runtime census, blockers, and promotion boundary.", "inputSchema": {"type": "object", "additionalProperties": False}},
    {"name": "athena_kc144_hub_manifest", "description": "Return the complete 144-seat structural crystal with coordinate, graph, organ, dataset, transport, readiness, and RETURN fibres.", "inputSchema": {"type": "object", "properties": {"include_edges": {"type": "boolean"}, "include_dynamic_inventory": {"type": "boolean"}}, "additionalProperties": False}},
    {"name": "athena_kc144_hub_seat", "description": "Resolve one immutable GID into all implemented coordinate charts, native subcrystal coordinates, D4 views, and attached runtime/source fibres.", "inputSchema": {"type": "object", "required": ["gid"], "properties": {"gid": {"type": "integer", "minimum": 1, "maximum": 144}, "include_fibres": {"type": "boolean"}}, "additionalProperties": False}},
    {"name": "athena_kc144_hub_inventory", "description": "Search the unified fibre inventory of live tools/resources, staged organs, harnesses, skills, mathematics, coordinates, graphs, gates, and source datasets.", "inputSchema": {"type": "object", "properties": {"kind": {"type": "string"}, "state": {"type": "string"}, "gid": {"type": "integer", "minimum": 1, "maximum": 144}, "query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 5000}}, "additionalProperties": False}},
    {"name": "athena_kc144_hub_graph", "description": "Return an exact generated KC144 graph or a source-bounded declared graph summary without fabricating unavailable edges.", "inputSchema": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string", "enum": ["physical_grid", "radial_ring", "mirror", "br21_native", "kc15_native", "kc27_native", "compiler_declared", "combined"]}, "include_edges": {"type": "boolean"}}, "additionalProperties": False}},
    {"name": "athena_kc144_hub_route", "description": "Compute a deterministic shortest typed route over one or more executable KC144 graph layers.", "inputSchema": {"type": "object", "required": ["src", "dst"], "properties": {"src": {"type": "integer", "minimum": 1, "maximum": 144}, "dst": {"type": "integer", "minimum": 1, "maximum": 144}, "graphs": {"type": "array", "items": {"type": "string", "enum": ["physical_grid", "radial_ring", "mirror", "br21_native", "kc15_native", "kc27_native"]}, "minItems": 1, "uniqueItems": True}}, "additionalProperties": False}},
    {"name": "athena_kc144_hub_datasets", "description": "Return the source-bound Google Drive and Git commit dataset index; raw bodies are not copied into Git.", "inputSchema": {"type": "object", "properties": {"kind": {"type": "string"}, "state": {"type": "string"}}, "additionalProperties": False}},
    {"name": "athena_kc144_hub_communication", "description": "Return the organ dependency DAG and typed cross-organ transport membrane with live/staged/held state.", "inputSchema": {"type": "object", "additionalProperties": False}},
    {"name": "athena_kc144_hub_readiness", "description": "Evaluate the ten conjunctive IC gates C/I/E/P/R/V/O/M/S/X and expose exact blockers; structural closure never self-promotes.", "inputSchema": {"type": "object", "additionalProperties": False}},
    {"name": "athena_kc144_hub_validate", "description": "Recompute the 144-seat, coordinate-roundtrip, D4, graph-cardinality, inventory, dataset, and command-surface checks and emit a deterministic receipt.", "inputSchema": {"type": "object", "additionalProperties": False}},
]

HUB_RESOURCES = [
    {"uri": "athena://kc144/hub", "name": "KC144 Topological Command Hub Status", "mimeType": "application/json"},
    {"uri": "athena://kc144/hub/manifest", "name": "KC144 Topological Crystal Manifest", "mimeType": "application/json"},
    {"uri": "athena://kc144/hub/inventory", "name": "KC144 Unified Fibre Inventory", "mimeType": "application/json"},
    {"uri": "athena://kc144/hub/graphs", "name": "KC144 Typed Graph Atlas", "mimeType": "application/json"},
    {"uri": "athena://kc144/hub/datasets", "name": "KC144 Source Dataset Index", "mimeType": "application/json"},
    {"uri": "athena://kc144/hub/communication", "name": "KC144 Organ Communication Graph", "mimeType": "application/json"},
    {"uri": "athena://kc144/hub/readiness", "name": "KC144 IC10 Readiness Membrane", "mimeType": "application/json"},
    {"uri": "athena://kc144/hub/validation", "name": "KC144 Structural Validation Receipt", "mimeType": "application/json"},
]

HUB_PROMPT = {
    "name": "athena_kc144_command_center",
    "title": "ATHENA KC144 Topological Command Center",
    "description": "Hydrate the giant KC144 crystal, locate every live/staged organ and source fibre, route through typed graphs, expose blockers, and select only witnessed lawful next work.",
    "arguments": [{"name": "task", "required": True}, {"name": "agent", "required": False}],
}
