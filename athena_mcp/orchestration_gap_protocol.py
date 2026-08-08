from __future__ import annotations

from .orchestration_gap import AOR_EDGE_TYPES

EDGE_SCHEMA={"type":"object","required":["src","dst","relation"],"properties":{"id":{"type":"string"},"edge_id":{"type":"string"},"src":{"type":"string","minLength":1},"dst":{"type":"string","minLength":1},"relation":{"enum":list(AOR_EDGE_TYPES)},"verified":{"type":"boolean"},"witness_ref":{"type":"string"},"status":{"type":"string"}},"additionalProperties":True}
TARGET_SCHEMA={"type":"object","required":["node"],"properties":{"id":{"type":"string"},"node":{"type":"string","minLength":1},"severity":{"type":"number","minimum":0},"leverage":{"type":"number","minimum":0},"information_gain":{"type":"number","minimum":0},"cost":{"type":"number","exclusiveMinimum":0}},"additionalProperties":True}
POLICY_SCHEMA={"type":"object","required":["traversable_relations"],"properties":{"traversable_relations":{"type":"array","items":{"enum":list(AOR_EDGE_TYPES)},"uniqueItems":True},"max_depth":{"type":"integer","minimum":0},"require_witness":{"type":"boolean"},"allowed_statuses":{"type":"array","items":{"type":"string"},"uniqueItems":True}},"additionalProperties":False}
SOURCES_SCHEMA={"type":"object","additionalProperties":{"type":"array","items":{"type":"string"},"uniqueItems":True}}

GAP_TOOLS=[
{"name":"athena_gap_compile","description":"Compile and optionally persist GAP.1 = explicit target nodes minus witnessed directed reachability closure over frozen source groups and typed graph edges. This is navigation closure, not logical/causal entailment. Unknown residual metrics route to measurement.","inputSchema":{"type":"object","required":["task_ref","sources","edges","targets","policy"],"properties":{"task_ref":{"type":"string","minLength":1},"sources":SOURCES_SCHEMA,"edges":{"type":"array","items":EDGE_SCHEMA},"targets":{"type":"array","items":TARGET_SCHEMA},"policy":POLICY_SCHEMA,"actor":{"type":"string"},"persist":{"type":"boolean"}},"additionalProperties":False}},
{"name":"athena_gap_get","description":"Fetch one persisted GAPRUN with exact source/edge/target/policy snapshot, closure paths, residuals, grow decision and digest.","inputSchema":{"type":"object","required":["run_id"],"properties":{"run_id":{"type":"string","minLength":1}},"additionalProperties":False}},
{"name":"athena_gap_replay","description":"Recompile one GAPRUN from frozen inputs and compare closure nodes, gap, grow and decision digest.","inputSchema":{"type":"object","required":["run_id"],"properties":{"run_id":{"type":"string","minLength":1}},"additionalProperties":False}},
{"name":"athena_gap_recent","description":"List recent persisted GAPRUN receipts without expanding full graph snapshots.","inputSchema":{"type":"object","properties":{"limit":{"type":"integer","minimum":1,"maximum":500}},"additionalProperties":False}},
]
GAP_TOOL_NAMES={tool['name'] for tool in GAP_TOOLS}
GAP_RESOURCE={"uri":"athena://gap","name":"GAP.1 Witnessed Reachability Closure / Target Residual Compiler","mimeType":"application/json"}
