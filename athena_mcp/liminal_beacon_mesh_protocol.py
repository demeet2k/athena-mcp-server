from __future__ import annotations

"""MCP surface for the non-authoritative Liminal Beacon Mesh V1 candidate."""

MESSAGE_CLASSES = [
    "PRESENCE", "FOCUS", "DELTA", "DISCOVERY", "NEED", "OFFER", "BLOCKER",
    "QUESTION", "ANSWER", "CLAIM", "HANDOFF", "INHIBIT", "QUORUM",
    "CORRECTION", "RETRACTION", "RESULT",
]
ACTIVITY_STATES = ["IDLE", "WORKING", "BLOCKED", "AVAILABLE", "HANDOFF", "QUIESCENT", "UNKNOWN"]
VISIBILITY_STATES = ["LOCAL", "GUILD", "COLONY", "PUBLIC"]
RECEIPT_STAGES = ["PRESENTED", "CONSUMED", "INCORPORATED", "DECISION_CHANGED", "PROPAGATED"]
BRIDGE_KINDS = ["AUTO", "MESSAGE_BOARD", "COHESION"]

_STRING_ARRAY = {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True}

LIMINAL_BEACON_TOOLS = [
    {
        "name": "athena_liminal_beacon_manifest",
        "description": (
            "Describe the candidate Liminal Beacon Mesh V1 runtime, receipt semantics, persistence boundary, "
            "autohook standing, and authority/evidence firewalls."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "athena_liminal_beacon_touch",
        "description": (
            "Refresh cheap ephemeral agent presence/focus and indexed topological route keys. Presence is not a claim, "
            "working proof, hidden-process proof, scheduler authority, or durable Git memory."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["agent_id"],
            "properties": {
                "agent_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "instance_id": {"type": ["string", "null"], "maxLength": 128},
                "session_epoch": {"type": ["string", "null"], "maxLength": 128},
                "activity": {"type": "string", "enum": ACTIVITY_STATES},
                "focus": {"type": ["string", "null"], "maxLength": 512},
                "capacity": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                "availability": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                "work_refs": _STRING_ARRAY,
                "object_refs": _STRING_ARRAY,
                "dependency_refs": _STRING_ARRAY,
                "causal_refs": _STRING_ARRAY,
                "semantic_tags": _STRING_ARRAY,
                "kc_refs": _STRING_ARRAY,
                "party_refs": _STRING_ARRAY,
                "capabilities": _STRING_ARRAY,
                "needs": _STRING_ARRAY,
                "offers": _STRING_ARRAY,
                "blockers": _STRING_ARRAY,
                "provides": _STRING_ARRAY,
                "visibility": {"type": "string", "enum": VISIBILITY_STATES},
                "lease_seconds": {"type": "integer", "minimum": 1, "maximum": 3600},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_liminal_beacon_emit",
        "description": (
            "Emit one bounded causal micro-envelope into the ephemeral rendezvous plane. The packet can reference a "
            "larger native payload but does not inherit truth or authority from routing priority."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["agent_id", "message_class", "summary"],
            "properties": {
                "agent_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "message_class": {"type": "string", "enum": MESSAGE_CLASSES},
                "summary": {"type": "string", "minLength": 1, "maxLength": 1200},
                "payload_ref": {"type": ["string", "null"], "maxLength": 2048},
                "goal_ref": {"type": ["string", "null"], "maxLength": 512},
                "evidence_ceiling": {"type": ["string", "null"], "maxLength": 128},
                "urgency": {"type": "number", "minimum": 0, "maximum": 1},
                "novelty": {"type": "number", "minimum": 0, "maximum": 1},
                "work_refs": _STRING_ARRAY,
                "object_refs": _STRING_ARRAY,
                "dependency_refs": _STRING_ARRAY,
                "causal_refs": _STRING_ARRAY,
                "semantic_tags": _STRING_ARRAY,
                "kc_refs": _STRING_ARRAY,
                "party_refs": _STRING_ARRAY,
                "changed_refs": _STRING_ARRAY,
                "affected_refs": _STRING_ARRAY,
                "capabilities": _STRING_ARRAY,
                "needs": _STRING_ARRAY,
                "offers": _STRING_ARRAY,
                "provides": _STRING_ARRAY,
                "dependencies": _STRING_ARRAY,
                "recipients": _STRING_ARRAY,
                "visibility": {"type": "string", "enum": VISIBILITY_STATES},
                "ttl_seconds": {"type": "integer", "minimum": 1, "maximum": 86400},
                "reply_to": {"type": ["string", "null"]},
                "parent_ids": _STRING_ARRAY,
                "correction_of": {"type": ["string", "null"]},
                "retraction_of": {"type": ["string", "null"]},
                "capacity_units": {"type": "integer", "minimum": 1, "maximum": 64},
                "needed_units": {"type": "integer", "minimum": 1, "maximum": 64},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_liminal_beacon_rendezvous",
        "description": (
            "Find bounded unknown-sender packets in the receiver's current topological neighborhood using route-key "
            "intersection, urgency/freshness, reverse correction routing, backpressure and an optional scout quota. "
            "Returned packets become PRESENTED, not CONSUMED."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["agent_id"],
            "properties": {
                "agent_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "cursor": {"type": "integer", "minimum": 0},
                "limit": {"type": "integer", "minimum": 1, "maximum": 32},
                "threshold": {"type": "number", "minimum": 0, "maximum": 1},
                "context_budget": {"type": "integer", "minimum": 256, "maximum": 16384},
                "scout_quota": {"type": "integer", "minimum": 0, "maximum": 4},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_liminal_beacon_receipt",
        "description": (
            "Advance an explicit recipient receipt from PRESENTED toward CONSUMED/INCORPORATED/DECISION_CHANGED/PROPAGATED. "
            "Stages are monotonic; consumption and later cognition are never inferred merely from routing or presentation."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["agent_id", "packet_id", "stage"],
            "properties": {
                "agent_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "packet_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "stage": {"type": "string", "enum": RECEIPT_STAGES},
                "disposition": {"type": ["string", "null"], "enum": ["ACCEPTED", "PARTIAL", "REJECTED", "DEFERRED", "SKIPPED", None]},
                "consumer_ref": {"type": ["string", "null"], "maxLength": 2048},
                "residual": {"type": ["string", "null"], "maxLength": 1200},
                "propagation_refs": _STRING_ARRAY,
                "outcome_ref": {"type": ["string", "null"], "maxLength": 2048},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_liminal_beacon_bridge",
        "description": (
            "Explicitly compact one material ephemeral packet into the existing durable Message Board or Cohesion organ. "
            "Bridge failure is a HOLD; the mesh creates no parallel claim, assignment, truth, or merge authority."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["packet_id"],
            "properties": {
                "packet_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "bridge_kind": {"type": "string", "enum": BRIDGE_KINDS},
                "remote": {"type": "string"},
                "allow_collaboration": {"type": "boolean"},
                "role": {"type": ["string", "null"]},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_liminal_beacon_state",
        "description": (
            "Read ephemeral mesh presence, packet, receipt and health counters. Hidden process count and unobserved "
            "independence remain UNKNOWN; this is coordination state, not world truth."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": ["string", "null"], "maxLength": 128},
                "include_packets": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
            },
            "additionalProperties": False,
        },
    },
]

LIMINAL_BEACON_TOOL_NAMES = {tool["name"] for tool in LIMINAL_BEACON_TOOLS}
LIMINAL_BEACON_RESOURCE = {
    "uri": "athena://liminal/beacon-mesh",
    "name": "ATHENA Liminal Beacon Mesh V1 Candidate",
    "mimeType": "application/json",
}

__all__ = [
    "MESSAGE_CLASSES", "ACTIVITY_STATES", "VISIBILITY_STATES", "RECEIPT_STAGES",
    "LIMINAL_BEACON_TOOLS", "LIMINAL_BEACON_TOOL_NAMES", "LIMINAL_BEACON_RESOURCE",
]
