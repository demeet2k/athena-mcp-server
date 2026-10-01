from __future__ import annotations

AID={"type":"string","minLength":1,"maxLength":256}
DIGEST={"type":"string","pattern":"^sha256:[0-9a-f]{64}$"}
TTL={"type":"integer","minimum":250,"maximum":300000}
LAMPORT={"type":"integer","minimum":0}
PARENTS={"type":"array","maxItems":32,"items":{"type":"string","minLength":1},"uniqueItems":True}

FEDERATION_EPHEMERAL_TOOLS=[
 {"name":"athena_ephemeral_federation_post","description":"Project an ATHENA Federation cursor-bound handoff into the process-local ephemeral request/poll plane. This is a LOSSY_AUX transport projection: routing does not prove source-currentness, federation admission, delivery, consumption, or application.","inputSchema":{"type":"object","required":["sender_aid","recipient_aids","handoff_digest","source_cursor_digest","lamport"],"properties":{"sender_aid":AID,"recipient_aids":{"type":"array","minItems":1,"maxItems":32,"items":AID,"uniqueItems":True},"handoff_digest":DIGEST,"source_cursor_digest":DIGEST,"delivery_class":{"type":"string","enum":["RENDEZVOUS","NEED_OFFER","NUDGE","BLOCKER","MATERIAL_CANDIDATE"]},"salience":{"type":"number","minimum":0,"maximum":1},"ttl_ms":TTL,"lamport":LAMPORT,"causal_parents":PARENTS},"additionalProperties":False}},
 {"name":"athena_ephemeral_federation_poll","description":"Poll the existing process-local queue and decode only ATHENA Federation handoff projections. MCP process cursors remain advisory transport cursors and never become Federation source cursors.","inputSchema":{"type":"object","required":["aid"],"properties":{"aid":AID,"after_cursor":{"type":"integer","minimum":0},"max_items":{"type":"integer","minimum":1,"maximum":100},"salience_budget":{"type":"number","minimum":0,"maximum":32}},"additionalProperties":False}},
 {"name":"athena_ephemeral_federation_witness","description":"Build a typed MCP consumption witness only after an external ATHENA Federation cursor-admission receipt exists. This does not execute or mint the admission receipt.","inputSchema":{"type":"object","required":["handoff_digest","source_cursor_digest","federation_admission_receipt_digest","consumer_ref"],"properties":{"handoff_digest":DIGEST,"source_cursor_digest":DIGEST,"federation_admission_receipt_digest":DIGEST,"consumer_ref":{"type":"string","minLength":1,"maxLength":512}},"additionalProperties":False}}
]
FEDERATION_EPHEMERAL_TOOL_NAMES={tool["name"] for tool in FEDERATION_EPHEMERAL_TOOLS}
FEDERATION_EPHEMERAL_RESOURCE={"uri":"athena://coordination/federation-ephemeral-bridge/v1","name":"ATHENA Federation Ephemeral Cursor Bridge V1","mimeType":"application/json"}
