from .cohesion_dependency_cone_protocol import CALLER_EDGE_SCHEMA, CHANGE_SCHEMA

CONSUMPTION_DECISIONS = [
    "ACCEPTED_CHANGED",
    "ACCEPTED_NO_CHANGE",
    "REJECTED",
    "PARTIAL",
    "UNRESOLVED",
]

CONSUME_TOOL = {
    "name": "athena_cohesion_consume",
    "description": (
        "Record an explicit recipient consumption decision for one immutable Message Board MESSAGE route. "
        "Route and ACK alone do not establish consumption. Writes only a typed Message Board consumption event; "
        "creates no compliance, truth, claim, assignment, execution, scheduler, party-membership, or XP authority."
    ),
    "inputSchema": {
        "type": "object",
        "required": ["consumption_id", "recipient_id", "route_ref", "decision", "behavior_change"],
        "properties": {
            "consumption_id": {"type": "string", "minLength": 1},
            "recipient_id": {"type": "string", "minLength": 1},
            "route_ref": {"type": "string", "minLength": 1},
            "decision": {"type": "string", "enum": CONSUMPTION_DECISIONS},
            "behavior_change": {"type": "boolean"},
            "behavior_change_ref": {"type": ["string", "null"]},
            "reason": {"type": ["string", "null"]},
            "evidence_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
            "expected_route_digest": {"type": ["string", "null"]},
            "remote": {"type": "string"},
        },
        "additionalProperties": False,
    },
}

OUTCOME_ROW_SCHEMA = {
    "type": "object",
    "required": ["outcome_id"],
    "properties": {
        "outcome_id": {"type": "string", "minLength": 1},
        "execution_ref": {"type": ["string", "null"]},
        "observation_ref": {"type": ["string", "null"]},
        "verification_ref": {"type": ["string", "null"]},
        "evidence_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
        "consumption_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
    },
    "additionalProperties": False,
}

OUTCOME_CREDIT_TOOL = {
    "name": "athena_cohesion_outcome_credit",
    "description": (
        "Read-only descriptive outcome-attribution membrane. Separates execution contribution, observed outcome, "
        "coordination consumption association, truth-verification standing, and causal effect. Detects duplicate "
        "evidence/consumption attribution and never emits scalar XP/reward, truth authority, or causal treatment proof."
    ),
    "inputSchema": {
        "type": "object",
        "required": ["credit_id", "observer_id", "outcomes"],
        "properties": {
            "credit_id": {"type": "string", "minLength": 1},
            "observer_id": {"type": "string", "minLength": 1},
            "outcomes": {"type": "array", "items": OUTCOME_ROW_SCHEMA, "minItems": 1},
            "remote": {"type": "string"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
        },
        "additionalProperties": False,
    },
}

PULSE_TOOL = {
    "name": "athena_cohesion_pulse",
    "description": (
        "Read-only CUT-02 collective steering front door. Projects current shared Cohesion/Message Board state into "
        "observable pressure coordinates and ranked advisory interventions. It may optionally compute a targeted "
        "DependencyCone for one explicit change. COHESION::PULSE is not QUEST::PULSE, a scheduler, dispatcher, or authority."
    ),
    "inputSchema": {
        "type": "object",
        "required": ["observer_id"],
        "properties": {
            "observer_id": {"type": "string", "minLength": 1},
            "comparison_id": {"type": ["string", "null"]},
            "change": {"anyOf": [CHANGE_SCHEMA, {"type": "null"}]},
            "caller_edges": {"type": ["array", "null"], "items": CALLER_EDGE_SCHEMA},
            "remote": {"type": "string"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]},
        },
        "additionalProperties": False,
    },
}

CUT02_TOOLS = [CONSUME_TOOL, OUTCOME_CREDIT_TOOL, PULSE_TOOL]
CUT02_TOOL_NAMES = {tool["name"] for tool in CUT02_TOOLS}
