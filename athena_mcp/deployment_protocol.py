from __future__ import annotations

from .deployment import HTTP_ADAPTER_VERSION

DEPLOYMENT_TOOLS = [
    {
        "name": "athena_deployment_manifest",
        "description": "Return ATHENA.DEPLOYMENT.2: exact OCI identity, source-head binding, single-writer persistence, secure HTTP host, canary, CAS cutover, rollback, and receipt laws. Surface availability is not activation evidence.",
        "inputSchema": {"type": "object", "additionalProperties": False},
    },
    {
        "name": "athena_deployment_validate",
        "description": "Fail-closed validation of ATHENA.DEPLOYMENT.BUNDLE.2 intent without contacting infrastructure, resolving secrets, or moving traffic.",
        "inputSchema": {
            "type": "object",
            "required": ["bundle"],
            "properties": {"bundle": {"type": "object"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_deployment_activation_plan",
        "description": "Compile a PLAN_ONLY source-bound, digest-pinned, isolated-canary, CAS single-writer cutover. It never deploys or grants cutover authority.",
        "inputSchema": {
            "type": "object",
            "required": [
                "image_ref",
                "source_head",
                "state_snapshot_ref",
                "state_snapshot_digest",
                "token_secret_ref",
                "release_attestation_ref",
                "sbom_ref"
            ],
            "properties": {
                "image_ref": {"type": "string", "minLength": 1},
                "source_head": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "state_snapshot_ref": {"type": "string", "minLength": 1},
                "state_snapshot_digest": {"type": "string", "minLength": 64},
                "token_secret_ref": {"type": "string", "minLength": 1},
                "release_attestation_ref": {"type": "string", "minLength": 1},
                "sbom_ref": {"type": "string", "minLength": 1},
                "expected_current_image_ref": {"type": ["string", "null"]},
                "replicas": {"type": "integer", "minimum": 1, "maximum": 1},
                "canary_percent": {"type": "integer", "minimum": 1, "maximum": 50},
                "actor": {"type": "string"}
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_deployment_assess_canary",
        "description": "Evaluate supplied external canary observations. Missing metrics HOLD; thin sample/window evidence ROLLBACK; failed health/error/latency/restart gates ROLLBACK.",
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
                        "max_restart_delta": {"type": "integer", "minimum": 0},
                        "min_sample_count": {"type": "integer", "minimum": 1},
                        "min_observation_window_seconds": {"type": "integer", "minimum": 1}
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_deployment_verify_receipt",
        "description": "Replay the exact plan/image/source/state bindings of a supplied activation receipt. PASS verifies receipt structure, not independent cluster observation.",
        "inputSchema": {
            "type": "object",
            "required": [
                "receipt",
                "expected_plan_digest",
                "expected_image_ref",
                "expected_source_head",
                "expected_state_snapshot_ref",
                "expected_state_snapshot_digest"
            ],
            "properties": {
                "receipt": {"type": "object"},
                "expected_plan_digest": {"type": "string"},
                "expected_image_ref": {"type": "string"},
                "expected_source_head": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "expected_state_snapshot_ref": {"type": "string", "minLength": 1},
                "expected_state_snapshot_digest": {"type": "string"}
            },
            "additionalProperties": False,
        },
    },
]

DEPLOYMENT_TOOL_NAMES = {tool["name"] for tool in DEPLOYMENT_TOOLS}

DEPLOYMENT_RESOURCES = [
    {
        "uri": "athena://deployment",
        "name": "ATHENA Deployment V2 Contract",
        "mimeType": "application/json",
    },
    {
        "uri": "athena://deployment/security",
        "name": "ATHENA Deployment Host and Supply-Chain Security",
        "mimeType": "application/json",
    },
    {
        "uri": "athena://deployment/rollout",
        "name": "ATHENA Canary, CAS Cutover and Rollback Contract",
        "mimeType": "application/json",
    },
    {
        "uri": "athena://deployment/evidence",
        "name": "ATHENA Deployment Evidence and Receipt Boundary",
        "mimeType": "application/json",
    },
]
DEPLOYMENT_RESOURCE_URIS = {resource["uri"] for resource in DEPLOYMENT_RESOURCES}

DEPLOYMENT_PROMPT = {
    "name": "athena_deployment_activation",
    "title": "ATHENA Deployment Activation V2",
    "description": "Compile and evaluate a source-bound, digest-pinned, isolated-canary, CAS single-writer activation without collapsing plan, image, provenance, health, cutover, deployment, or authority.",
    "arguments": [
        {"name": "objective", "required": True},
        {"name": "environment", "required": False},
        {"name": "actor", "required": False},
    ],
    "adapter": HTTP_ADAPTER_VERSION,
}
