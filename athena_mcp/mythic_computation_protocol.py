from __future__ import annotations

MCK_VERSION = "MCK.RUNTIME.V1"
MCK_RESOURCE = {
    "uri": "athena://symbolic/computation/mck/v1",
    "name": "ATHENA Mythic Computation Kernel Runtime V1",
    "description": (
        "Bounded symbolic-computation operators distilled from MCK.V1. "
        "Tradition-internal, symbolic, and source-reported claims never become "
        "empirical causation or execution authority by runtime inference."
    ),
}

STATUS_ENUM = [
    "OBSERVED",
    "SOURCE_REPORTED",
    "TRADITION_INTERNAL",
    "SYMBOLIC_INFERENCE",
    "EXPERIMENTAL_HYPOTHESIS",
    "UNKNOWN",
]

MCK_TOOLS = [
    {
        "name": "athena_mck_symbolic_address",
        "description": (
            "Select an address from a caller-supplied symbolic address space by deterministic lexical fit. "
            "Preserves provenance and transform loss; no address is invented when nothing matches."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["query", "address_space"],
            "properties": {
                "query": {"type": "string", "minLength": 1},
                "context": {"type": "string"},
                "address_space": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["id", "terms"],
                        "properties": {
                            "id": {"type": "string", "minLength": 1},
                            "terms": {"type": "array", "items": {"type": "string"}},
                            "source_ref": {"type": "string"},
                            "standing": {"type": "string", "enum": STATUS_ENUM},
                            "payload": {},
                        },
                        "additionalProperties": False,
                    },
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_mck_correspondence_route",
        "description": (
            "Route through a caller-supplied typed correspondence graph without upgrading edge standing. "
            "Returns route provenance, weakest standing and an explicit no-causal-authority ceiling."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["src", "dst", "edges"],
            "properties": {
                "src": {"type": "string", "minLength": 1},
                "dst": {"type": "string", "minLength": 1},
                "max_depth": {"type": "integer", "minimum": 1, "maximum": 32},
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["src", "dst", "relation", "standing"],
                        "properties": {
                            "src": {"type": "string", "minLength": 1},
                            "dst": {"type": "string", "minLength": 1},
                            "relation": {"type": "string", "minLength": 1},
                            "standing": {"type": "string", "enum": STATUS_ENUM},
                            "source_ref": {"type": "string"},
                            "directed": {"type": "boolean"},
                        },
                        "additionalProperties": False,
                    },
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_mck_oracle_decode",
        "description": (
            "Deterministically select/decode a caller-supplied symbolic codebook entry from an explicit sample or seed. "
            "Output is SYMBOLIC_GENERATION_ONLY, not factual prediction or decision authority; safety-critical uses HOLD."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["query", "codebook"],
            "properties": {
                "query": {"type": "string", "minLength": 1},
                "sample": {"type": ["integer", "null"]},
                "seed": {"type": ["string", "null"]},
                "use_case": {
                    "type": "string",
                    "enum": ["GENERAL", "CREATIVE", "MEDICAL", "LEGAL", "FINANCIAL", "SAFETY_CRITICAL"],
                },
                "codebook": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["code", "interpretation"],
                        "properties": {
                            "code": {"type": "string", "minLength": 1},
                            "interpretation": {"type": "string"},
                            "source_ref": {"type": "string"},
                            "standing": {"type": "string", "enum": STATUS_ENUM},
                        },
                        "additionalProperties": False,
                    },
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_mck_protocol_machine",
        "description": (
            "Compile/simulate the generic B->Theta->Pi protocol state machine over caller-supplied steps. "
            "Missing boundary/phase prerequisites and declared hazardous classes HOLD; simulation grants no real ritual/execution authority."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["boundary", "phase", "steps"],
            "properties": {
                "boundary": {
                    "type": "object",
                    "required": ["authorized"],
                    "properties": {
                        "authorized": {"type": "boolean"},
                        "scope": {"type": "string"},
                        "authority_ref": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                "phase": {
                    "type": "object",
                    "required": ["ready"],
                    "properties": {
                        "ready": {"type": "boolean"},
                        "label": {"type": "string"},
                        "witness_ref": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
                "steps": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                "mode": {"type": "string", "enum": ["TRANSFORMING", "QUERYING"]},
                "risk_class": {
                    "type": "string",
                    "enum": ["NONE", "TOXIC", "HARM_DIRECTED", "COERCIVE", "ILLEGAL", "DANGEROUS"],
                },
                "witness": {},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_mck_model_bridge",
        "description": (
            "Map explicit fields from one scoped model/ontology into another while preserving invariants, unmapped residue, provenance and transform loss. "
            "A model bridge never establishes cultural identity or world-truth equivalence."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["source_model", "target_model", "field_map"],
            "properties": {
                "source_model": {"type": "object"},
                "target_model": {"type": "object"},
                "field_map": {"type": "object", "additionalProperties": {"type": "string"}},
                "invariants": {"type": "array", "items": {"type": "string"}},
                "source_ref": {"type": "string"},
                "target_ref": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_mck_epistemic_split",
        "description": (
            "Split claims by epistemic standing and evaluate only explicit promotion requests. "
            "Unsupported OBSERVED/EMPIRICAL/HISTORICAL_PRIMARY promotion and safety-critical symbolic use HOLD."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["claim", "status"],
                        "properties": {
                            "claim": {"type": "string", "minLength": 1},
                            "status": {"type": "string", "enum": STATUS_ENUM},
                            "witness_ref": {"type": "string"},
                            "source_ref": {"type": "string"},
                            "independent": {"type": "boolean"},
                            "provenance_type": {
                                "type": "string",
                                "enum": [
                                    "PRIMARY_HISTORICAL_SOURCE",
                                    "SECONDARY_SCHOLARSHIP",
                                    "LIVING_TRADITION_SOURCE",
                                    "MODERN_RECONSTRUCTION",
                                    "UNKNOWN",
                                ],
                            },
                        },
                        "additionalProperties": False,
                    },
                },
                "requested_promotion": {
                    "type": ["string", "null"],
                    "enum": ["OBSERVED", "EMPIRICAL_SUPPORT", "HISTORICAL_PRIMARY", null],
                },
                "use_case": {
                    "type": "string",
                    "enum": ["GENERAL", "CREATIVE", "MEDICAL", "LEGAL", "FINANCIAL", "SAFETY_CRITICAL"],
                },
            },
            "additionalProperties": False,
        },
    },
]

MCK_TOOL_NAMES = {tool["name"] for tool in MCK_TOOLS}
