from __future__ import annotations

MACHINE_ID = {"type": "string", "minLength": 1, "maxLength": 256}
REVISION = {"type": "integer", "minimum": 0}

NEXUS4D_TOOLS = [
    {
        "name": "athena_nexus_compile",
        "description": "Compile terminal predicates, typed node contracts, hard invariants and initial state into a durable NEXUS-4D obligation/pressure machine. Compilation creates control-plane state only and grants no execution, merge, promotion or external-action authority.",
        "inputSchema": {
            "type": "object",
            "required": ["spec"],
            "properties": {
                "spec": {"type": "object"},
                "machine_id": MACHINE_ID,
                "actor": {"type": "string", "minLength": 1, "maxLength": 256},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_nexus_plan",
        "description": "Recompute terminal residuals, propagate typed obligation pressure backward, propagate readiness forward and emit one lawful conflict-free executable nexus batch. A plan is selection, not execution.",
        "inputSchema": {
            "type": "object",
            "required": ["machine_id"],
            "properties": {
                "machine_id": MACHINE_ID,
                "expected_revision": REVISION,
                "max_nodes": {"type": "integer", "minimum": 1, "maximum": 1000},
                "max_cost": {"type": "number", "minimum": 0},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_nexus_advance",
        "description": "Atomically append witnessed lifecycle events to a NEXUS-4D machine under optimistic revision control. Candidate, verification, commit, consumption and outcome stages remain distinct; only recomputed residual closure can terminate a goal.",
        "inputSchema": {
            "type": "object",
            "required": ["machine_id", "expected_revision", "events"],
            "properties": {
                "machine_id": MACHINE_ID,
                "expected_revision": REVISION,
                "events": {"type": "array", "minItems": 1, "maxItems": 256, "items": {"type": "object"}},
                "actor": {"type": "string", "minLength": 1, "maxLength": 256},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_nexus_state",
        "description": "Read one durable NEXUS-4D machine with recomputed goals, obligations, pressure, readiness, evidence deficits, terminal standing and exact snapshot digest.",
        "inputSchema": {
            "type": "object",
            "required": ["machine_id"],
            "properties": {"machine_id": MACHINE_ID},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_nexus_replay",
        "description": "Cold-replay a NEXUS-4D event lineage from its normalized genesis and require exact snapshot identity. Replay proves ledger integrity only; it does not independently re-observe external truth or causal gain.",
        "inputSchema": {
            "type": "object",
            "required": ["machine_id"],
            "properties": {"machine_id": MACHINE_ID},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_nexus_terminal",
        "description": "Recompute a bounded terminal proof. Silence, a producer completion string, a verified candidate, a commit or consumption alone cannot produce TERMINAL standing.",
        "inputSchema": {
            "type": "object",
            "required": ["machine_id"],
            "properties": {"machine_id": MACHINE_ID},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_nexus_recent",
        "description": "List recent durable NEXUS-4D machines and their recomputed terminal standing. This is an observational control-plane query.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 1000}},
            "additionalProperties": False,
        },
    },
]

NEXUS4D_TOOL_NAMES = {tool["name"] for tool in NEXUS4D_TOOLS}
NEXUS4D_RESOURCE = {
    "uri": "athena://nexus4d",
    "name": "ATHENA NEXUS-4D Bidirectional Obligation/Pressure Computer",
    "mimeType": "application/json",
}
NEXUS4D_RESOURCES = [NEXUS4D_RESOURCE]
NEXUS4D_RESOURCE_URIS = {resource["uri"] for resource in NEXUS4D_RESOURCES}

__all__ = [
    "NEXUS4D_TOOLS",
    "NEXUS4D_TOOL_NAMES",
    "NEXUS4D_RESOURCE",
    "NEXUS4D_RESOURCES",
    "NEXUS4D_RESOURCE_URIS",
]
