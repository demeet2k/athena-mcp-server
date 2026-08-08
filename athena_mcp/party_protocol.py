PARTY_TOOLS = [
    {
        "name": "athena_party_form",
        "description": "Form a durable multi-goal agent party. Formation itself grants zero XP; the small party bonus remains locked until witnessed multi-agent outcomes and proper communication satisfy credit gates.",
        "inputSchema": {
            "type": "object",
            "required": ["leader", "goals", "channels"],
            "properties": {
                "leader": {"type": "string", "minLength": 1},
                "name": {"type": ["string", "null"]},
                "goals": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "oneOf": [
                            {"type": "string", "minLength": 1},
                            {
                                "type": "object",
                                "required": ["id"],
                                "properties": {
                                    "id": {"type": "string", "minLength": 1},
                                    "weight": {"type": "number", "minimum": 0},
                                    "required_capabilities": {
                                        "type": "array",
                                        "items": {"type": "string", "minLength": 1},
                                        "uniqueItems": True,
                                    },
                                    "description": {"type": "string"},
                                },
                                "additionalProperties": False,
                            },
                        ]
                    },
                },
                "channels": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "oneOf": [
                            {"type": "string", "minLength": 1},
                            {
                                "type": "object",
                                "required": ["id"],
                                "properties": {
                                    "id": {"type": "string", "minLength": 1},
                                    "mode": {"type": "string"},
                                },
                                "additionalProperties": False,
                            },
                        ]
                    },
                },
                "capabilities": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "uniqueItems": True,
                },
                "policy": {"type": "object"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_party_join",
        "description": "Join an existing party with declared capabilities. Joining/presence grants zero XP; credit follows witnessed contribution.",
        "inputSchema": {
            "type": "object",
            "required": ["party_id", "agent"],
            "properties": {
                "party_id": {"type": "string", "minLength": 1},
                "agent": {"type": "string", "minLength": 1},
                "capabilities": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "uniqueItems": True,
                },
                "role": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_party_message",
        "description": "Post a typed party communication over a declared shared channel. Cross-agent messages establish coordination structure but never earn XP or evidence truth by themselves.",
        "inputSchema": {
            "type": "object",
            "required": ["party_id", "author", "channel", "target", "kind", "body"],
            "properties": {
                "party_id": {"type": "string", "minLength": 1},
                "author": {"type": "string", "minLength": 1},
                "channel": {"type": "string", "minLength": 1},
                "target": {"type": "string", "minLength": 1},
                "kind": {
                    "type": "string",
                    "enum": ["CLAIM", "OFFER", "HANDOFF", "BLOCKER", "DECISION", "RESULT", "VERIFY"],
                },
                "body": {"type": "string", "minLength": 1},
                "refs": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "uniqueItems": True,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_party_steer",
        "description": "Run the bounded Big-3 3x5x7x9 party controller across current members, goals and communication state. Generates 15 allocation candidates and uses the existing exact QHUG Pareto kernel for final adjudication; planning never mints XP.",
        "inputSchema": {
            "type": "object",
            "required": ["party_id"],
            "properties": {
                "party_id": {"type": "string", "minLength": 1},
                "actor": {"type": "string"},
                "persist": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_party_credit",
        "description": "Credit only the incremental capped party XP bonus after a persisted steering cycle has witnessed outcomes from at least two agents across at least two goals and proper reciprocal communication. Unique source_xp_ref prevents replay/double-credit.",
        "inputSchema": {
            "type": "object",
            "required": ["party_id", "cycle_id", "outcomes", "xp_receipts"],
            "properties": {
                "party_id": {"type": "string", "minLength": 1},
                "cycle_id": {"type": "string", "minLength": 1},
                "outcomes": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["outcome_ref", "agent", "goal_id", "witness_ref", "status"],
                        "properties": {
                            "outcome_ref": {"type": "string", "minLength": 1},
                            "agent": {"type": "string", "minLength": 1},
                            "goal_id": {"type": "string", "minLength": 1},
                            "witness_ref": {"type": "string", "minLength": 1},
                            "status": {"type": "string", "enum": ["OBSERVED", "VERIFIED"]},
                            "contribution_weight": {"type": "number", "minimum": 0},
                        },
                        "additionalProperties": False,
                    },
                },
                "xp_receipts": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["agent", "source_xp_ref", "base_xp", "witness_ref"],
                        "properties": {
                            "agent": {"type": "string", "minLength": 1},
                            "source_xp_ref": {"type": "string", "minLength": 1},
                            "base_xp": {"type": "number", "minimum": 0},
                            "witness_ref": {"type": "string", "minLength": 1},
                        },
                        "additionalProperties": False,
                    },
                },
                "actor": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_party_state",
        "description": "Read durable party membership, goals, channels, communication readiness, latest steering cycle and cumulative incremental party-XP bonuses.",
        "inputSchema": {
            "type": "object",
            "required": ["party_id"],
            "properties": {"party_id": {"type": "string", "minLength": 1}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_party_list",
        "description": "List recent parties and their lifecycle state.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": ["string", "null"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            },
            "additionalProperties": False,
        },
    },
]

PARTY_TOOL_NAMES = {tool["name"] for tool in PARTY_TOOLS}
PARTY_RESOURCE = {
    "uri": "athena://party/runtime",
    "name": "ATHENA Party Runtime — Big3 3x5x7x9",
    "mimeType": "application/json",
}
