RECOVERY_RESOURCE = {
    "uri": "athena://recovery/google-docs/v1",
    "name": "Revision-bound Google Docs organ recovery registry V1",
    "mimeType": "application/json",
}

RECOVERY_TOOLS = [
    {
        "name": "athena_recovery_organs",
        "description": "List revision-bound recovered Google Docs organs by status, family, or semantic text. Read-only; search hits/misses are not implementation proof.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "family": {"type": "string"},
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_recovery_organ",
        "description": "Get one recovered organ with Drive source/revision, semantic signature, current-runtime references, residuals, and claim boundary.",
        "inputSchema": {
            "type": "object",
            "required": ["organ_id"],
            "properties": {"organ_id": {"type": "string", "minLength": 1}},
            "additionalProperties": False
        }
    },
    {
        "name": "athena_recovery_frontier",
        "description": "Return the ranked residual implementation/replay frontier derived from recovered Drive organs. Priority is heuristic, not mutation authority.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                "include_theory": {"type": "boolean"}
            },
            "additionalProperties": False
        }
    }
]

RECOVERY_TOOL_NAMES = {tool["name"] for tool in RECOVERY_TOOLS}
