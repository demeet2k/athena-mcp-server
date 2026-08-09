from __future__ import annotations

from .shso_readonly import SHSO_READONLY_VERSION

SHSO_READONLY_TOOL_NAME = "athena_shso_project_organism_pressure"
SHSO_READONLY_RESOURCE_URI = "athena://shso/readonly"

SHSO_READONLY_TOOLS = [
    {
        "name": SHSO_READONLY_TOOL_NAME,
        "description": (
            "Project caller-supplied SHSO HEALTH_ADVISORY and ECOLOGY_ADVISORY packets plus bounded work-state "
            "facts into a read-only organism pressure label. The tool cannot dispatch, schedule, execute, mutate "
            "Git/morphology/prompts, prove advisory truth, deploy SHSO, or establish behavioral gain."
        ),
        "inputSchema": {
            "type": "object",
            "required": [
                "health_advisory",
                "ecology_advisory",
                "ready_build_exists",
                "previous_transition_classes",
                "verification_barrier_due",
                "verification_barrier_mandatory",
            ],
            "properties": {
                "health_advisory": {
                    "type": "object",
                    "required": [
                        "kind",
                        "diagnostic_phase",
                        "criticality_proven",
                        "phase_is_heuristic",
                        "behavioral_gain_proven",
                    ],
                },
                "ecology_advisory": {
                    "type": "object",
                    "required": ["kind", "status", "world_truth_proven"],
                },
                "ready_build_exists": {"type": "boolean"},
                "previous_transition_classes": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "maxItems": 32,
                },
                "verification_barrier_due": {"type": "boolean"},
                "verification_barrier_mandatory": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    }
]
SHSO_READONLY_TOOL_NAMES = {tool["name"] for tool in SHSO_READONLY_TOOLS}

SHSO_READONLY_RESOURCES = [
    {
        "uri": SHSO_READONLY_RESOURCE_URI,
        "name": "ATHENA SHSO Read-Only Organism Pressure Bridge V1",
        "mimeType": "application/json",
        "version": SHSO_READONLY_VERSION,
    }
]
SHSO_READONLY_RESOURCE_URIS = {resource["uri"] for resource in SHSO_READONLY_RESOURCES}

__all__ = [
    "SHSO_READONLY_RESOURCE_URI",
    "SHSO_READONLY_RESOURCE_URIS",
    "SHSO_READONLY_RESOURCES",
    "SHSO_READONLY_TOOL_NAME",
    "SHSO_READONLY_TOOL_NAMES",
    "SHSO_READONLY_TOOLS",
]
