from __future__ import annotations

from .orchestration_field import FIELD_KINDS

EXPLICIT_CANDIDATE_SCHEMA = {
    "type": "object",
    "required": ["kind", "operation", "target_ref"],
    "properties": {
        "kind": {"enum": list(FIELD_KINDS)},
        "operation": {"type": "string", "minLength": 1},
        "target_ref": {"type": "string", "minLength": 1},
        "payload": {"type": "object"},
        "source_refs": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        "dependencies": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        "field_origin": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        "readiness": {"type": "number"}, "gain": {"type": "number"}, "independence": {"type": "number"},
        "bridge": {"type": "number"}, "cost": {"type": "number"}, "resource_cost": {"type": "number"},
        "delta_j": {"type": "number"}, "information_gain": {"type": "number"}, "option_value": {"type": "number"},
        "evidence": {"type": "number"}, "connection": {"type": "number"}, "replay": {"type": "number"},
        "navigation": {"type": "number"}, "reconstruction": {"type": "number"}, "implementation": {"type": "number"},
        "novelty": {"type": "number"}, "duplicate": {"type": ["number", "boolean"]},
        "fake": {"type": ["number", "boolean"]}, "bloat": {"type": "number"},
        "unsupported": {"type": ["number", "boolean"]}, "unhandled_contradiction": {"type": ["number", "boolean"]},
        "coordinate_loss": {"type": "number"}, "claim_id": {"type": "string"},
        "min_authority": {"enum": ["?", "+", "!", "#"]}, "resolved": {"type": "boolean"},
        "branch_id": {"type": "string"}, "requires": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        "require_coordinates": {"type": "boolean"}, "coordinates": {"type": "object"},
    },
    "additionalProperties": True,
}

FIELD_TOOLS = [
    {
        "name": "athena_field_compile",
        "description": "Assemble actual SX/RAG/Y/GAP/HUG/branch/AOR residuals into typed FIELD.1 action candidates. Generated proposals are UNMEASURED; exact same action signatures may merge provenance only; conflicting explicit ranking/routing data fail closed to CONFLICT and disputed operands are removed. Semantic similarity never merges.",
        "inputSchema": {
            "type": "object", "required": ["seed_ref", "module_outputs"],
            "properties": {
                "seed_ref": {"type": "string", "minLength": 1}, "module_outputs": {"type": "object"},
                "explicit_candidates": {"type": "array", "items": EXPLICIT_CANDIDATE_SCHEMA},
                "ecosystem": {"type": "object"}, "actor": {"type": "string"}, "persist": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
    {"name": "athena_field_get", "description": "Fetch one persisted FIELDRUN with frozen module inputs, candidates, metric states, provenance edges and digest.", "inputSchema": {"type": "object", "required": ["run_id"], "properties": {"run_id": {"type": "string", "minLength": 1}}, "additionalProperties": False}},
    {"name": "athena_field_replay", "description": "Rebuild one FIELDRUN from frozen module inputs and compare candidate IDs, conflict state, provenance edges and field digest.", "inputSchema": {"type": "object", "required": ["run_id"], "properties": {"run_id": {"type": "string", "minLength": 1}}, "additionalProperties": False}},
    {"name": "athena_field_recent", "description": "List recent persisted FIELDRUN receipts without expanding full candidate payloads.", "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 500}}, "additionalProperties": False}},
]
FIELD_TOOL_NAMES = {tool["name"] for tool in FIELD_TOOLS}
FIELD_RESOURCE = {"uri": "athena://field", "name": "FIELD.1 Provenance-Preserving Candidate Assembler", "mimeType": "application/json"}
