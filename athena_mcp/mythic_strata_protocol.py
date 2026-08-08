from __future__ import annotations

STRATA_VERSION="MCK.STRATA.RUNTIME.V0"
STRATA_RESOURCE={
    "uri":"athena://symbolic/computation/mck/strata/v0",
    "name":"ATHENA MCK Strata Transport Membrane V0",
    "description":"Temporal/source/category/authorization transport guard for MCK. Candidate membrane only; no MCK.V2 promotion or practitioner authority."
}

STANDING=["PRIMARY_EVIDENCE","SECONDARY_SCHOLARSHIP","LIVING_TRADITION_SOURCE","MODERN_RECONSTRUCTION","TRADITION_INTERNAL","UNKNOWN"]
CATEGORY=["NATIVE","SCHOLARLY_UMBRELLA","MODERN_RECONSTRUCTION","COMPOSITE","UNKNOWN"]
CORPUS=["CLOSED","OPEN","LIVING","LAYERED","UNKNOWN"]
AUTH=["PUBLIC","ROLE_GATED","INITIATORY","RESTRICTED","MIXED","UNKNOWN"]
OPERATIONS=[
    "SEMANTIC_TRANSPORT","SEMANTIC_EQUIVALENCE","OPERATOR_EQUIVALENCE","HISTORICAL_PROMOTION",
    "AUTHORITY_GRANT","RESTRICTED_INFERENCE","CORPUS_EXHAUSTIVENESS","CATEGORY_FLATTENING",
    "IDENTITY_EQUIVALENCE","HAZARDOUS_EXECUTION","EPISTEMIC_PROOF","AUTHORITY_SCOPE_ESCAPE"
]
RISKS=["NONE","TOXIC","HARM_DIRECTED","COERCIVE","ILLEGAL","DANGEROUS"]


def _obj(required=None,properties=None):
    return {"type":"object","required":list(required or []),"properties":dict(properties or {}),"additionalProperties":False}

LAYER=_obj(["layer_id","standing","category_scope","corpus_mutability","authorization_scope"],{
    "adapter_id":{"type":"string"},
    "layer_id":{"type":"string","minLength":1},
    "standing":{"type":"string","enum":STANDING},
    "category_scope":{"type":"string","enum":CATEGORY},
    "corpus_mutability":{"type":"string","enum":CORPUS},
    "authorization_scope":{"type":"string","enum":AUTH},
    "source_scope":{"type":"string"},
})
BRIDGE=_obj(["source_ref","evidence_standing","invariants","transform_loss"],{
    "source_ref":{"type":"string","minLength":1},
    "evidence_standing":{"type":"string","enum":STANDING},
    "invariants":{"type":"array","minItems":1,"items":{"type":"string"}},
    "transform_loss":{"type":"array","minItems":1,"items":{"type":"string"}},
    "authority":{"type":"string","enum":["SYMBOLIC_ONLY","SCHOLARLY_MAPPING","SOURCE_BACKED_RELATION"]},
})

STRATA_TOOLS=[{
    "name":"athena_mck_strata_transport",
    "description":"Evaluate one layer-to-layer MCK transport. Cross-layer equivalence/promotion/authority/hazard shortcuts HOLD; an explicit source-bearing bridge may allow only bounded non-identity transport with declared invariants and loss.",
    "inputSchema":_obj(["source","target","operation"],{
        "source":LAYER,
        "target":LAYER,
        "operation":{"type":"string","enum":OPERATIONS},
        "risk_class":{"type":"string","enum":RISKS},
        "target_model_class":{"type":"string"},
        "explicit_bridge":{"anyOf":[BRIDGE,{"type":"null"}]},
    })
}]
STRATA_TOOL_NAMES={x["name"] for x in STRATA_TOOLS}
