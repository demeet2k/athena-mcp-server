from __future__ import annotations

SYSTEM_UPGRADE_TOOLS = [
    {
        "name": "athena_system_upgrade_manifest",
        "description": "Return the complete SYSTEM.UPGRADE.1 control-plane manifest, source-task census, ledger identities, tools/resources, recent runs and release receipts.",
        "inputSchema": {"type": "object", "additionalProperties": False},
    },
    {
        "name": "athena_system_upgrade_plan",
        "description": "Create a persistent whole-system UPGRUN from an objective, target version, optional expected Git head and ordered witnessed source-task completions. Planning measures local C/I/E/P/R/V/O/M/S/X gates but never claims later work executed.",
        "inputSchema": {
            "type": "object",
            "required": ["objective"],
            "properties": {
                "objective": {"type": "string", "minLength": 1},
                "target_version": {"type": "string", "minLength": 1},
                "expected_git_head": {"type": ["string", "null"]},
                "completion_witnesses": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["task_id", "witness"],
                        "properties": {
                            "task_id": {"type": "string", "minLength": 1},
                            "require_exact_head": {"type": "boolean"},
                            "witness": {
                                "type": "object",
                                "required": ["observed", "ref", "procedure", "observation", "result"],
                                "properties": {
                                    "observed": {"const": True},
                                    "ref": {"type": "string", "minLength": 1},
                                    "procedure": {},
                                    "observation": {},
                                    "result": {},
                                    "head_sha": {"type": ["string", "null"]},
                                    "independence_key": {"type": ["string", "null"]},
                                    "metadata": {"type": "object"},
                                },
                                "additionalProperties": True,
                            },
                        },
                        "additionalProperties": False,
                    },
                },
                "actor": {"type": "string"},
                "persist": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_system_upgrade_state",
        "description": "Fetch one persisted UPGRUN with measured gate matrix, witnessed source completion, deterministic frontier, state digest, event receipts and RETURN coordinate.",
        "inputSchema": {
            "type": "object",
            "required": ["run_id"],
            "properties": {"run_id": {"type": "string", "minLength": 1}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_system_upgrade_observe",
        "description": "CAS-advance one ready source task using a supplied procedure+observation+result witness. Blocked dependencies, invalid witnesses and stale state digests fail closed.",
        "inputSchema": {
            "type": "object",
            "required": ["run_id", "task_id", "witness", "expected_state_digest"],
            "properties": {
                "run_id": {"type": "string", "minLength": 1},
                "task_id": {"type": "string", "minLength": 1},
                "expected_state_digest": {"type": "string", "minLength": 1},
                "require_exact_head": {"type": "boolean"},
                "refresh_local": {"type": "boolean"},
                "actor": {"type": "string"},
                "witness": {
                    "type": "object",
                    "required": ["observed", "ref", "procedure", "observation", "result"],
                    "properties": {
                        "observed": {"const": True},
                        "ref": {"type": "string", "minLength": 1},
                        "procedure": {},
                        "observation": {},
                        "result": {},
                        "head_sha": {"type": ["string", "null"]},
                        "independence_key": {"type": ["string", "null"]},
                        "metadata": {"type": "object"},
                    },
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_system_upgrade_refresh",
        "description": "CAS-refresh one UPGRUN from the current measured local runtime, preserving all witnessed source-task completions and emitting a new immutable event receipt.",
        "inputSchema": {
            "type": "object",
            "required": ["run_id", "expected_state_digest"],
            "properties": {
                "run_id": {"type": "string", "minLength": 1},
                "expected_state_digest": {"type": "string", "minLength": 1},
                "run_replay_samples": {"type": "boolean"},
                "actor": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_system_upgrade_replay",
        "description": "Verify one UPGRUN's frozen state digest and complete event-chain continuity. Replay never re-simulates external observations.",
        "inputSchema": {
            "type": "object",
            "required": ["run_id"],
            "properties": {"run_id": {"type": "string", "minLength": 1}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_system_upgrade_recent",
        "description": "List recent whole-system upgrade runs without expanding complete state packets.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 500}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_system_release_certificate",
        "description": "Create a replayable exact-head RELCERT from one UPGRUN, measured local IC10 gates, upgrade replay, expected-head match, optional source completion and PROMOTION.1 CI+smoke attestations.",
        "inputSchema": {
            "type": "object",
            "required": ["run_id", "git_head", "ci_witness", "smoke_witness"],
            "properties": {
                "run_id": {"type": "string", "minLength": 1},
                "git_head": {"type": "string", "minLength": 1},
                "ci_witness": {"type": "object"},
                "smoke_witness": {"type": "object"},
                "require_source_completion": {"type": "boolean"},
                "actor": {"type": "string"},
                "persist": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_system_release_get",
        "description": "Fetch one frozen exact-head system release certificate and its bound local/promotion/source gates.",
        "inputSchema": {
            "type": "object",
            "required": ["certificate_id"],
            "properties": {"certificate_id": {"type": "string", "minLength": 1}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_system_release_replay",
        "description": "Replay one RELCERT through certificate digest, UPGRUN event-chain and linked PROMRUN receipt integrity.",
        "inputSchema": {
            "type": "object",
            "required": ["certificate_id"],
            "properties": {"certificate_id": {"type": "string", "minLength": 1}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_system_release_recent",
        "description": "List recent qualified and blocked exact-head system release certificates.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 500}},
            "additionalProperties": False,
        },
    },
]

SYSTEM_UPGRADE_TOOL_NAMES = {item["name"] for item in SYSTEM_UPGRADE_TOOLS}

SYSTEM_UPGRADE_RESOURCES = [
    {
        "uri": "athena://system/upgrade",
        "name": "ATHENA SYSTEM.UPGRADE.1 Control Plane",
        "mimeType": "application/json",
    },
    {
        "uri": "athena://system/upgrade/frontier",
        "name": "ATHENA Whole-System Upgrade Frontier",
        "mimeType": "application/json",
    },
    {
        "uri": "athena://system/release",
        "name": "ATHENA Exact-Head Release Certificates",
        "mimeType": "application/json",
    },
]
SYSTEM_UPGRADE_RESOURCE_URIS = {item["uri"] for item in SYSTEM_UPGRADE_RESOURCES}

SYSTEM_UPGRADE_PROMPT = {
    "name": "athena_system_upgrade",
    "title": "ATHENA Complete System Upgrade",
    "description": "Measure the complete runtime, open a persistent witnessed upgrade transaction, attack the lawful frontier, replay every state transition, and produce an exact-head release certificate without self-promotion.",
    "arguments": [
        {"name": "objective", "required": True},
        {"name": "target_version", "required": False},
        {"name": "agent", "required": False},
    ],
}
