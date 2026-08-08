WITNESS_SCHEMA={
 "type":"object","required":["observed","ref","head_sha","conclusion"],
 "properties":{
  "observed":{"const":True},
  "ref":{"type":"string","minLength":1},
  "head_sha":{"type":"string","minLength":7},
  "conclusion":{"const":"success"}
 },"additionalProperties":True
}
PROMOTION_TOOLS=[
 {"name":"athena_promotion_evaluate","description":"Evaluate and optionally persist a runtime promotion receipt. Surface/composition certificates are computed locally; CI/smoke are caller-supplied external witness packets bound to the exact Git head and preserved as attestations, not independently fetched evidence.","inputSchema":{"type":"object","required":["git_head","ci_witness","smoke_witness"],"properties":{"git_head":{"type":"string","minLength":7},"ci_witness":WITNESS_SCHEMA,"smoke_witness":WITNESS_SCHEMA,"actor":{"type":"string"},"persist":{"type":"boolean"}},"additionalProperties":False}},
 {"name":"athena_promotion_get","description":"Fetch one persisted PROMRUN including frozen promotion input, surface/composition certificate, external witness packets, status and decision digest.","inputSchema":{"type":"object","required":["run_id"],"properties":{"run_id":{"type":"string","minLength":1}},"additionalProperties":False}},
 {"name":"athena_promotion_replay","description":"Deterministically replay one stored promotion receipt from its frozen certificates and witness packets; replay verifies receipt logic, not the external CI system itself.","inputSchema":{"type":"object","required":["run_id"],"properties":{"run_id":{"type":"string","minLength":1}},"additionalProperties":False}},
 {"name":"athena_promotion_recent","description":"List recent persisted runtime promotion receipts.","inputSchema":{"type":"object","properties":{"limit":{"type":"integer","minimum":1,"maximum":200}},"additionalProperties":False}}
]
PROMOTION_TOOL_NAMES={tool['name'] for tool in PROMOTION_TOOLS}
PROMOTION_RESOURCE={"uri":"athena://promotion","name":"ATHENA Runtime Promotion Receipt Ledger","mimeType":"application/json"}
