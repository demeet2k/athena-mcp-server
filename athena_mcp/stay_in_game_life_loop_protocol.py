from __future__ import annotations

LIFE_WORLD_NEW_TOOL = {
    "name": "athena_life_world_new",
    "description": "Create a new public ATHENA Stay-in-Game Life Loop V1 world with logical counters only.",
    "inputSchema": {
        "type": "object",
        "properties": {"game_id": {"type": "string", "minLength": 1}},
        "required": ["game_id"],
        "additionalProperties": False,
    },
}

LIFE_AGENT_ENTER_TOOL = {
    "name": "athena_life_agent_enter",
    "description": "Enter one agent into a Life Loop world with three base lives and an explicit quest identity.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "world": {"type": "object"},
            "agent_id": {"type": "string", "minLength": 1},
            "quest_id": {"type": "string", "minLength": 1},
            "quest_version": {"type": "string", "minLength": 1},
        },
        "required": ["world", "agent_id", "quest_id", "quest_version"],
        "additionalProperties": False,
    },
}

LIFE_RESOLVE_TOOL = {
    "name": "athena_life_resolve",
    "description": "Resolve one public CLEAR, FAIL_CLEAR, or typed HOLD attempt through hardened Stay-in-Game Life Loop V1.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "world": {"type": "object"},
            "agent_id": {"type": "string", "minLength": 1},
            "attempt": {"type": "object"},
        },
        "required": ["world", "agent_id", "attempt"],
        "additionalProperties": False,
    },
}

CAMPAIGN_LIFE_BIND_TOOL = {
    "name": "athena_campaign_life_bind",
    "description": (
        "Compile and bind a Stay-in-Game Life Loop V1 quest packet around an exact Campaign V3 BOUND receipt. "
        "The tool recomputes clear-condition and packet digests, verifies pulse/campaign/quest/agent anchor binding, "
        "and grants no execution, scheduler, reward, life-consumption, reseed-consumption, provider, or platform-reset authority."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "bound_receipt": {"type": "object"},
            "pulse": {"type": "object"},
            "agent_coordinate_name": {"type": "string", "minLength": 1},
            "quest_id": {"type": "string", "minLength": 1},
            "quest_version": {"type": "string", "minLength": 1},
            "clear_conditions": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
            "reseed_anchor": {"type": "object"},
            "extra_life_reward_candidate": {
                "type": "object",
                "properties": {
                    "requested": {"type": "boolean"},
                    "candidate_id": {"type": "string", "minLength": 1},
                    "evidence_refs": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                    },
                },
                "additionalProperties": False,
            },
        },
        "required": [
            "bound_receipt",
            "pulse",
            "agent_coordinate_name",
            "quest_id",
            "quest_version",
            "clear_conditions",
            "reseed_anchor"
        ],
        "additionalProperties": False,
    },
}

STAY_IN_GAME_LIFE_LOOP_TOOLS = [
    LIFE_WORLD_NEW_TOOL,
    LIFE_AGENT_ENTER_TOOL,
    LIFE_RESOLVE_TOOL,
    CAMPAIGN_LIFE_BIND_TOOL,
]
STAY_IN_GAME_LIFE_LOOP_TOOL_NAMES = {tool["name"] for tool in STAY_IN_GAME_LIFE_LOOP_TOOLS}

STAY_IN_GAME_LIFE_LOOP_RESOURCE = {
    "uri": "athena://stay-in-game-life-loop/v1",
    "name": "ATHENA Stay-in-Game Life Loop V1",
    "description": (
        "Public logical-life continuation law over Campaign V3, compiler-backed Life quest packets, and RESEED_ANCHOR_V1. "
        "No product/model/provider counter reset authority."
    ),
    "mimeType": "application/json",
}
STAY_IN_GAME_LIFE_LOOP_RESOURCES = [STAY_IN_GAME_LIFE_LOOP_RESOURCE]
STAY_IN_GAME_LIFE_LOOP_RESOURCE_URIS = {resource["uri"] for resource in STAY_IN_GAME_LIFE_LOOP_RESOURCES}
