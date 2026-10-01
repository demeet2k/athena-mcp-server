from __future__ import annotations

SYNAPSE_LIMINAL_TOOLS = [
    {
        "name": "athena_synapse_liminal_export_packet",
        "description": (
            "Export one current public Liminal Beacon packet capsule as an ATHENA Synapse V1 envelope. "
            "The projection is explicitly LOSSY_AUX relative to the full ephemeral packet; routing state is not truth."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["packet_id"],
            "properties": {
                "packet_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "source_revision": {"type": ["string", "null"], "maxLength": 128}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_synapse_liminal_export_receipt",
        "description": (
            "Export one explicit recipient Liminal receipt as a Synapse V1 RECEIPT envelope. "
            "Causality is packet -> prior receipt stage -> current stage; timestamps do not establish stage order."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["agent_id", "packet_id"],
            "properties": {
                "agent_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "packet_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "source_revision": {"type": ["string", "null"], "maxLength": 128}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_synapse_liminal_plan_ingress",
        "description": (
            "Translate a foreign Synapse V1 envelope into bounded Liminal Beacon emit arguments without mutating runtime. "
            "Foreign causal IDs remain causal references, not fabricated local packet parents."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["agent_id", "envelope"],
            "properties": {
                "agent_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "envelope": {"type": "object"}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_synapse_liminal_ingest",
        "description": (
            "Explicitly emit a validated foreign Synapse V1 envelope into the existing ephemeral Liminal Beacon plane "
            "as a new non-authoritative coordination signal. This is not source-event identity, consumption, or execution authority."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["agent_id", "envelope"],
            "properties": {
                "agent_id": {"type": "string", "minLength": 1, "maxLength": 128},
                "envelope": {"type": "object"}
            },
            "additionalProperties": False
        }
    }
]

SYNAPSE_LIMINAL_TOOL_NAMES = {tool["name"] for tool in SYNAPSE_LIMINAL_TOOLS}

__all__ = ["SYNAPSE_LIMINAL_TOOLS", "SYNAPSE_LIMINAL_TOOL_NAMES"]
