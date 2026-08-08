from __future__ import annotations

FIELD_TOOLS=[
{"name":"athena_field_compile","description":"Assemble and optionally persist a FIELD.1 provenance-preserving action field from actual module outputs/residuals plus optional explicit candidates. Generated actions receive no invented AOR metrics; exact signature merges preserve provenance and metric conflicts fail closed.","inputSchema":{"type":"object","required":["seed_ref","module_outputs"],"properties":{"seed_ref":{"type":"string","minLength":1},"module_outputs":{"type":"object"},"explicit_candidates":{"type":"array","items":{"type":"object"}},"ecosystem":{"type":"object"},"actor":{"type":"string"},"persist":{"type":"boolean"}},"additionalProperties":False}},
{"name":"athena_field_get","description":"Fetch one persisted FIELDRUN with exact module inputs, ecosystem constraints, candidate field, provenance edges and digest.","inputSchema":{"type":"object","required":["run_id"],"properties":{"run_id":{"type":"string"}},"additionalProperties":False}},
{"name":"athena_field_replay","description":"Rebuild one FIELDRUN from its frozen module outputs and compare field digest, candidate identities and provenance edges.","inputSchema":{"type":"object","required":["run_id"],"properties":{"run_id":{"type":"string"}},"additionalProperties":False}},
{"name":"athena_field_recent","description":"List recent persisted FIELDRUN receipts.","inputSchema":{"type":"object","properties":{"limit":{"type":"integer","minimum":1,"maximum":500}},"additionalProperties":False}},
]
FIELD_RESOURCE={"uri":"athena://field","name":"FIELD.1 Provenance-Preserving Candidate Assembler","mimeType":"application/json"}
