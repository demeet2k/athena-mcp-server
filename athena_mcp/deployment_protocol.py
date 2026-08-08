from __future__ import annotations

from .deployment import HTTP_ADAPTER_VERSION

DEPLOYMENT_TOOLS = [
    {
        "name": "athena_deployment_manifest",
        "description": "Return the digest-pinned OCI, secure HTTP host, single-writer persistence, canary, rollback, and supply-chain deployment contract. Surface availability is not activation evidence.",
        "inputSchema": {"type": "object", "additionalProperties": False},
    },
    {
        "name": "athena_deployment_validate",
        "description": "Validate an ATHENA.DEPLOYMENT.BUNDLE.1 as fail-closed activation intent without contacting infrastructure or moving traffic.",
        "inputSchema": {
            "type": "object",
            "required": ["bundle"],
            "properties": {"bundle": {"type": "object"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_deployment_activation_plan",
        "description": "Compile a PLAN_ONLY isolated-canary and single-writer cutover sequence for one exact OCI digest. This never deploys or authorizes cutover.",
        "inputSchema": {
            "type": "object",
            "required": [
                "image_ref",
                "state_snapshot_ref",
                "token_secret_ref",
            ],
            "properties": {
                "image_ref": {"type": "string"},
                "replicas": {"type": "integer", "minimum": 1, "maximum": 1},
                "canary_percent": {"type": "integer", "minimum": 1, "maximum": 50},
                "state_snapshot_ref": {"type": "string", "minLength": 1},
                "token_secret_ref": {"type": "string", "minLength": 1},
                "actor": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_deployment_assess_canary",
        "description": "Evaluate supplied external canary observations against explicit readiness, schema, replay, error, latency, and restart gates; missing data HOLDs and failed gates ROLLBACK.",
        "inputSchema": {
            "type": "object",
            "required": ["baseline", "canary"],
            "properties": {
                "baseline": {"type": "object"},
                "canary": {"type": "object"},
                "thresholds": {
                    "type": "object",
                    "properties": {
                        "max_error_rate_delta": {"type": "number", "minimum": 0.0},
                        "max_p95_ratio": {"type": "number", "minimum": 1.0},
                        "max_restart_delta": {"type": "integer", "minimum": 0}
                    },
                    "additionalProperties": False
                },
            },
            "additionalProperties": False,
        },
    },
]

DEPLOYMENT_RESOURCES = [
    {
        "uri": "athena://deployment",
        "name": "ATHENA Deployment Contract",
        "mimeType": "application/json",
    },
    {
        "uri": "athena://deployment/security",
        "name": "ATHENA Host and Supply-Chain Security Contract",
        "mimeType": "application/json",
    },
    {
        "uri": "athena://deployment/rollout",
        "name": "ATHENA Canary, Single-Writer Cutover and Rollback Contract",
        "mimeType": "application/json",
    },
]

DEPLOYMENT_PROMPT = {
    "name": "athena_deployment_activation",
    "title": "ATHENA Deployment Activation Control",
    "description": "Compile and evaluate a digest-pinned, isolated-canary, single-writer activation without collapsing plan, image, health, cutover, deployment, or authority.",
    "arguments": [
        {"name": "objective", "required": True},
        {"name": "environment", "required": False},
        {"name": "actor", "required": False},
    ],
    "adapter": HTTP_ADAPTER_VERSION,
}
