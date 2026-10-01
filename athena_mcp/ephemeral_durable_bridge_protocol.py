from __future__ import annotations

AID = {"type": "string", "minLength": 1, "maxLength": 256}
BOARD_ID = {"type": "string", "pattern": "^[A-Za-z0-9_.-]{1,128}$"}
RECEIPT_STAGE = {
    "type": "string",
    "enum": ["ROUTED", "DELIVERED", "PRESENTED", "CONSUMED", "INCORPORATED", "DECISION_CHANGED"],
}

_COMMON = {
    "packet_id": {"type": "string", "minLength": 1, "maxLength": 128},
    "ephemeral_actor_aid": AID,
    "actor_role": {"type": "string", "enum": ["SENDER", "RECIPIENT"]},
    "actor_binding_ref": {"type": "string", "minLength": 1, "maxLength": 2048},
    "board_agent_id": BOARD_ID,
    "board_recipients": {
        "type": "array",
        "minItems": 1,
        "maxItems": 32,
        "items": BOARD_ID,
        "uniqueItems": True,
    },
    "minimum_receipt_stage": RECEIPT_STAGE,
    "note": {"type": ["string", "null"], "maxLength": 1200},
    "remote": {"type": "string", "minLength": 1, "maxLength": 256},
}

EPHEMERAL_DURABLE_TOOLS = [
    {
        "name": "athena_ephemeral_durable_plan",
        "description": (
            "Read and validate one live MATERIAL_CANDIDATE in the process-local ephemeral plane against an explicit "
            "durable Message Board actor/recipient route. This is a non-mutating escalation plan: ephemeral AID, "
            "Message Board identity, routing, receipt stage and authority remain distinct."
        ),
        "inputSchema": {
            "type": "object",
            "required": [
                "packet_id", "ephemeral_actor_aid", "actor_role", "actor_binding_ref",
                "board_agent_id", "board_recipients",
            ],
            "properties": {
                **_COMMON,
                "shared_remote_mode": {
                    "type": "string",
                    "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"],
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_ephemeral_durable_escalate",
        "description": (
            "Explicitly persist one live ephemeral MATERIAL_CANDIDATE into the existing Git-backed Message Board as "
            "an idempotent MESSAGE event. No durable claim, assignment, consumption, source-currentness or identity "
            "equivalence is inferred. Writes require the Message Board's fresh shared remote frontier."
        ),
        "inputSchema": {
            "type": "object",
            "required": [
                "packet_id", "ephemeral_actor_aid", "actor_role", "actor_binding_ref",
                "board_agent_id", "board_recipients",
            ],
            "properties": dict(_COMMON),
            "additionalProperties": False,
        },
    },
]

EPHEMERAL_DURABLE_TOOL_NAMES = {tool["name"] for tool in EPHEMERAL_DURABLE_TOOLS}
EPHEMERAL_DURABLE_RESOURCE = {
    "uri": "athena://coordination/ephemeral-durable-bridge/v1",
    "name": "ATHENA Ephemeral to Durable Message Board Bridge V1",
    "mimeType": "application/json",
}

__all__ = [
    "EPHEMERAL_DURABLE_TOOLS",
    "EPHEMERAL_DURABLE_TOOL_NAMES",
    "EPHEMERAL_DURABLE_RESOURCE",
]
