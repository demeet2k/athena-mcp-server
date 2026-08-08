from __future__ import annotations

AUTHORITY_SYMBOLS = ["?", "+", "!", "#"]

VERIFIED_REF_SCHEMA = {
    "type": "object",
    "required": ["verified", "ref"],
    "properties": {
        "verified": {"const": True},
        "ref": {"type": "string", "minLength": 1},
    },
    "additionalProperties": True,
}

EVIDENCE_SCHEMA = {
    "type": "object",
    "required": ["kind", "verified", "ref"],
    "properties": {
        "kind": {"enum": ["support", "derive", "reproduce"]},
        "verified": {"const": True},
        "ref": {"type": "string", "minLength": 1},
    },
    "additionalProperties": True,
}

CANONICAL_AUTHORITY_SCHEMA = {
    "type": "object",
    "required": ["authorized", "ref"],
    "properties": {
        "authorized": {"const": True},
        "ref": {"type": "string", "minLength": 1},
    },
    "additionalProperties": True,
}

TEST_SCHEMA = {
    "type": "object",
    "required": ["procedure", "observation", "result", "witness"],
    "properties": {
        "procedure": {},
        "observation": {},
        "result": {},
        "witness": {
            "oneOf": [
                {"type": "string", "minLength": 1},
                VERIFIED_REF_SCHEMA,
            ]
        },
    },
    "additionalProperties": True,
}

AUTHORITY_TOOLS = [
    {
        "name": "athena_claim_register",
        "description": "Register or reuse a persistent claim authority head at Y='?'. Authority is distinct from confidence, truth, branch reward and canonical identity.",
        "inputSchema": {
            "type": "object",
            "required": ["claim_id", "source_ref"],
            "properties": {
                "claim_id": {"type": "string", "minLength": 1},
                "source_ref": {"type": "string", "minLength": 1},
                "actor": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_claim_state",
        "description": "Return the current typed authority state and accumulated evidence/test/canonical witness routes for one claim.",
        "inputSchema": {
            "type": "object",
            "required": ["claim_id"],
            "properties": {"claim_id": {"type": "string", "minLength": 1}},
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_claim_list",
        "description": "List persistent claim authority heads, optionally filtering by Y or challenge status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "y": {"enum": AUTHORITY_SYMBOLS},
                "status": {"enum": ["ACTIVE", "CHALLENGED", "CANONICAL_CHALLENGED"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_claim_promote",
        "description": "Advance a claim exactly one authority step. ?->+ requires verified support/derive/reproduce evidence; +->! requires witnessed execution; !-># requires explicit canonical authority. Skips are rejected.",
        "inputSchema": {
            "type": "object",
            "required": ["claim_id", "target_y"],
            "properties": {
                "claim_id": {"type": "string", "minLength": 1},
                "target_y": {"enum": AUTHORITY_SYMBOLS},
                "evidence": {"type": "array", "items": EVIDENCE_SCHEMA},
                "test": TEST_SCHEMA,
                "canonical_authority": CANONICAL_AUTHORITY_SCHEMA,
                "actor": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_claim_challenge",
        "description": "Record a verified material challenge. Noncanonical claims return to '?' with CHALLENGED status. Canonicals remain '#' but become CANONICAL_CHALLENGED until authorized resolution.",
        "inputSchema": {
            "type": "object",
            "required": ["claim_id", "witness", "reason"],
            "properties": {
                "claim_id": {"type": "string", "minLength": 1},
                "witness": VERIFIED_REF_SCHEMA,
                "reason": {"type": "string", "minLength": 1},
                "actor": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_claim_resolve_canonical_challenge",
        "description": "Resolve a CANONICAL_CHALLENGED claim using explicit authorized governance: UPHOLD returns '#/ACTIVE'; DEMOTE produces '!/ACTIVE'.",
        "inputSchema": {
            "type": "object",
            "required": ["claim_id", "decision", "authority"],
            "properties": {
                "claim_id": {"type": "string", "minLength": 1},
                "decision": {"enum": ["UPHOLD", "DEMOTE"]},
                "authority": CANONICAL_AUTHORITY_SCHEMA,
                "actor": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
]

AUTHORITY_RESOURCE = {
    "uri": "athena://authority",
    "name": "Typed Claim Authority Registry",
    "mimeType": "application/json",
}


def authority_candidate_schema_fragment():
    """Fields to merge into the global AOR candidate schema at integration time."""
    return {
        "claim_id": {"type": "string", "minLength": 1},
        "min_authority": {"enum": AUTHORITY_SYMBOLS},
    }
