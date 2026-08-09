from __future__ import annotations

from .deployment_cutover import (
    CUTOVER_HOLD_VERSION,
    QUIESCENCE_OBSERVATION_VERSION,
)

DEPLOYMENT_CUTOVER_TOOLS = [
    {
        "name": "athena_deployment_assess_quiescence",
        "description": (
            "Evaluate a supplied single-writer quiescence observation against exact current-image and "
            "state-snapshot coordinates. PASS validates supplied evidence only; it does not stop a writer, "
            "install a fence, verify a snapshot, or contact production."
        ),
        "inputSchema": {
            "type": "object",
            "required": [
                "observation",
                "expected_current_image_ref",
                "expected_state_snapshot_ref",
                "expected_state_snapshot_digest",
            ],
            "properties": {
                "observation": {"type": "object"},
                "expected_current_image_ref": {"type": "string", "minLength": 1},
                "expected_state_snapshot_ref": {"type": "string", "minLength": 1},
                "expected_state_snapshot_digest": {"type": "string", "minLength": 64},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_deployment_cutover_hold",
        "description": (
            "Bind a PLAN_ONLY activation plan, checksum-valid isolated canary witness, supplied quiescence "
            "observation, and authority reference into ATHENA.CUTOVER.HOLD.1. The result cannot deploy, "
            "resolve secrets, mutate state, stop/start a writer, or activate traffic."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["plan", "canary_witness", "quiescence_observation"],
            "properties": {
                "plan": {"type": "object"},
                "canary_witness": {"type": "object"},
                "quiescence_observation": {"type": "object"},
                "cutover_authority_ref": {"type": ["string", "null"]},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_deployment_verify_cutover_hold",
        "description": (
            "Replay an ATHENA.CUTOVER.HOLD.1 packet against exact expected bindings. PASS verifies supplied "
            "packet bytes only and is not current cluster observation, authority verification, cutover, or an "
            "activation receipt."
        ),
        "inputSchema": {
            "type": "object",
            "required": [
                "packet",
                "expected_plan_digest",
                "expected_image_ref",
                "expected_source_head",
                "expected_current_image_ref",
                "expected_state_snapshot_ref",
                "expected_state_snapshot_digest",
                "expected_canary_witness_digest",
                "expected_quiescence_assessment_digest",
                "expected_cutover_authority_ref",
            ],
            "properties": {
                "packet": {"type": "object"},
                "expected_plan_digest": {"type": "string", "minLength": 64},
                "expected_image_ref": {"type": "string", "minLength": 1},
                "expected_source_head": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{40}$",
                },
                "expected_current_image_ref": {"type": "string", "minLength": 1},
                "expected_state_snapshot_ref": {"type": "string", "minLength": 1},
                "expected_state_snapshot_digest": {"type": "string", "minLength": 64},
                "expected_canary_witness_digest": {"type": "string", "minLength": 64},
                "expected_quiescence_assessment_digest": {
                    "type": "string",
                    "minLength": 64,
                },
                "expected_cutover_authority_ref": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
]
DEPLOYMENT_CUTOVER_TOOL_NAMES = {tool["name"] for tool in DEPLOYMENT_CUTOVER_TOOLS}

DEPLOYMENT_CUTOVER_RESOURCES = [
    {
        "uri": "athena://deployment/cutover-hold",
        "name": "ATHENA CUTOVER_HOLD V1 Contract",
        "mimeType": "application/json",
    }
]
DEPLOYMENT_CUTOVER_RESOURCE_URIS = {
    resource["uri"] for resource in DEPLOYMENT_CUTOVER_RESOURCES
}

DEPLOYMENT_CUTOVER_PROMPT = {
    "name": "athena_deployment_cutover_hold",
    "title": "ATHENA Deployment CUTOVER_HOLD V1",
    "description": (
        "Compile and replay a non-effectful cutover hold from exact plan, canary, CAS, snapshot, "
        "quiescence, and authority-reference coordinates without granting execution authority."
    ),
    "arguments": [
        {"name": "objective", "required": True},
        {"name": "environment", "required": False},
        {"name": "actor", "required": False},
    ],
    "packet_version": CUTOVER_HOLD_VERSION,
    "quiescence_observation_version": QUIESCENCE_OBSERVATION_VERSION,
}
