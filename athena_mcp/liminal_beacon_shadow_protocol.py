from __future__ import annotations

"""Read-only MCP surface for Liminal Beacon Shadow V1."""

LIMINAL_BEACON_SHADOW_TOOLS = [
    {
        "name": "athena_liminal_beacon_shadow_status",
        "description": (
            "Read bounded no-injection Liminal Beacon shadow telemetry. Shadow observations are not delivery, "
            "presentation, consumption, evidence, authority, default activation, or hidden-process proof."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
                "include_records": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    }
]

LIMINAL_BEACON_SHADOW_TOOL_NAMES = {tool["name"] for tool in LIMINAL_BEACON_SHADOW_TOOLS}
LIMINAL_BEACON_SHADOW_RESOURCE = {
    "uri": "athena://liminal/beacon-shadow",
    "name": "ATHENA Liminal Beacon Shadow V1 Candidate",
    "mimeType": "application/json",
}

__all__ = [
    "LIMINAL_BEACON_SHADOW_TOOLS",
    "LIMINAL_BEACON_SHADOW_TOOL_NAMES",
    "LIMINAL_BEACON_SHADOW_RESOURCE",
]
