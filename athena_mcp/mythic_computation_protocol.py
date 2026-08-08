from __future__ import annotations

MCK_VERSION="MCK.RUNTIME.V1"
MCK_RESOURCE={
    "uri":"athena://symbolic/computation/mck/v1",
    "name":"ATHENA Mythic Computation Kernel Runtime V1",
    "description":"Bounded symbolic-computation operators; symbolic/source/tradition state never becomes empirical causation or execution authority by inference.",
}
STATUS_ENUM=["OBSERVED","SOURCE_REPORTED","TRADITION_INTERNAL","SYMBOLIC_INFERENCE","EXPERIMENTAL_HYPOTHESIS","UNKNOWN"]
USE_CASE_ENUM=["GENERAL","CREATIVE","MEDICAL","LEGAL","FINANCIAL","SAFETY_CRITICAL"]


def _obj(required=None,properties=None):
    return {"type":"object","required":list(required or []),"properties":dict(properties or {}),"additionalProperties":False}


ADDRESS_ENTRY=_obj(["id","terms"],{
    "id":{"type":"string","minLength":1},
    "terms":{"type":"array","items":{"type":"string"}},
    "source_ref":{"type":"string"},
    "standing":{"type":"string","enum":STATUS_ENUM},
    "payload":{},
})
EDGE=_obj(["src","dst","relation","standing"],{
    "src":{"type":"string","minLength":1},"dst":{"type":"string","minLength":1},
    "relation":{"type":"string","minLength":1},"standing":{"type":"string","enum":STATUS_ENUM},
    "source_ref":{"type":"string"},"directed":{"type":"boolean"},
})
CODE=_obj(["code","interpretation"],{
    "code":{"type":"string","minLength":1},"interpretation":{"type":"string"},
    "source_ref":{"type":"string"},"standing":{"type":"string","enum":STATUS_ENUM},
})
CLAIM=_obj(["claim","status"],{
    "claim":{"type":"string","minLength":1},"status":{"type":"string","enum":STATUS_ENUM},
    "witness_ref":{"type":"string"},"source_ref":{"type":"string"},"independent":{"type":"boolean"},
    "provenance_type":{"type":"string","enum":["PRIMARY_HISTORICAL_SOURCE","SECONDARY_SCHOLARSHIP","LIVING_TRADITION_SOURCE","MODERN_RECONSTRUCTION","UNKNOWN"]},
})

MCK_TOOLS=[
    {"name":"athena_mck_symbolic_address","description":"SAC: select only from a caller-supplied symbolic address space; preserve provenance/loss and HOLD rather than invent a match.","inputSchema":_obj(["query","address_space"],{
        "query":{"type":"string","minLength":1},"context":{"type":"string"},
        "address_space":{"type":"array","minItems":1,"items":ADDRESS_ENTRY},
    })},
    {"name":"athena_mck_correspondence_route","description":"CGR: route through caller-supplied typed edges without upgrading standing or claiming a causal path.","inputSchema":_obj(["src","dst","edges"],{
        "src":{"type":"string","minLength":1},"dst":{"type":"string","minLength":1},
        "max_depth":{"type":"integer","minimum":1,"maximum":32},
        "edges":{"type":"array","items":EDGE},
    })},
    {"name":"athena_mck_oracle_decode","description":"OSD: deterministically select/decode a caller-supplied codebook from explicit sample/seed; symbolic-only, no factual prediction or high-stakes authority.","inputSchema":_obj(["query","codebook"],{
        "query":{"type":"string","minLength":1},"sample":{"type":["integer","null"]},"seed":{"type":["string","null"]},
        "use_case":{"type":"string","enum":USE_CASE_ENUM},
        "codebook":{"type":"array","minItems":1,"items":CODE},
    })},
    {"name":"athena_mck_protocol_machine","description":"RSM: simulate B->Theta->Pi workflow gating; missing boundary/phase and declared hazardous classes HOLD; simulation grants no execution authority.","inputSchema":_obj(["boundary","phase","steps"],{
        "boundary":_obj(["authorized"],{"authorized":{"type":"boolean"},"scope":{"type":"string"},"authority_ref":{"type":"string"}}),
        "phase":_obj(["ready"],{"ready":{"type":"boolean"},"label":{"type":"string"},"witness_ref":{"type":"string"}}),
        "steps":{"type":"array","minItems":1,"items":{"type":"string"}},
        "mode":{"type":"string","enum":["TRANSFORMING","QUERYING"]},
        "risk_class":{"type":"string","enum":["NONE","TOXIC","HARM_DIRECTED","COERCIVE","ILLEGAL","DANGEROUS"]},
        "witness":{},
    })},
    {"name":"athena_mck_model_bridge","description":"MMTB: explicit lossy field transport between scoped models; retain residue/provenance and never assert cultural identity/equivalence.","inputSchema":_obj(["source_model","target_model","field_map"],{
        "source_model":{"type":"object"},"target_model":{"type":"object"},
        "field_map":{"type":"object","additionalProperties":{"type":"string"}},
        "invariants":{"type":"array","items":{"type":"string"}},"source_ref":{"type":"string"},"target_ref":{"type":"string"},
    })},
    {"name":"athena_mck_epistemic_split","description":"ESCPF: split claims by standing and evaluate explicit promotion requests; unsupported OBSERVED/EMPIRICAL/HISTORICAL_PRIMARY and high-stakes symbolic use HOLD.","inputSchema":_obj(["items"],{
        "items":{"type":"array","items":CLAIM},
        "requested_promotion":{"type":["string","null"],"enum":["OBSERVED","EMPIRICAL_SUPPORT","HISTORICAL_PRIMARY",None]},
        "use_case":{"type":"string","enum":USE_CASE_ENUM},
    })},
]
MCK_TOOL_NAMES={tool["name"] for tool in MCK_TOOLS}
