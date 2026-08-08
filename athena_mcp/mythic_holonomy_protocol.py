from __future__ import annotations

HOLONOMY_VERSION="MCK.HOLONOMY.RUNTIME.V0"
HOLONOMY_RESOURCE={
    "uri":"athena://symbolic/computation/mck/holonomy/v0",
    "name":"ATHENA MCK Semantic Holonomy Evaluator V0",
    "description":"Read-only held-out evaluator for source-stratified semantic transport. Reports vector drift, provenance/loss accounting and A0/A1/A2 comparison without MCK.V2, practitioner, predictive or metaphysical authority."
}

HOLONOMY_TOOLS=[{
    "name":"athena_mck_holonomy_evaluate",
    "description":"Evaluate a frozen MCK held-out packet through A0 unscoped reference, A1 edge-wise strata, and A2 composed provenance/loss/holonomy ledger. Scalarization is disabled; H_gamma is a representation-drift vector, not a metaphysical quantity.",
    "inputSchema":{
        "type":"object",
        "required":["packet"],
        "properties":{
            "packet":{"type":"object"},
            "source_packet_ref":{"type":"string"},
            "source_packet_blob_sha":{"type":"string"}
        },
        "additionalProperties":False
    }
}]
HOLONOMY_TOOL_NAMES={x["name"] for x in HOLONOMY_TOOLS}
