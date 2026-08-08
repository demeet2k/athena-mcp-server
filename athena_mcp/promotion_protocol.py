WITNESS_SCHEMA={
 'type':'object','required':['observed','ref','head_sha','conclusion'],
 'properties':{'observed':{'const':True},'ref':{'type':'string','minLength':1},'head_sha':{'type':'string','minLength':7},'conclusion':{'const':'success'}},
 'additionalProperties':True,
}
PROMOTION_TOOLS=[
 {'name':'athena_promotion_evaluate','description':'Evaluate and optionally persist PROMOTION.2 exact-head readiness. Caller-supplied CI/smoke packets may produce ATTESTED_READY but can never mint QUALIFIED; QUALIFIED is reserved for a host-internal trusted external-verification receipt that is not exposed in this MCP input schema.','inputSchema':{'type':'object','required':['git_head','ci_witness','smoke_witness'],'properties':{'git_head':{'type':'string','minLength':7},'ci_witness':WITNESS_SCHEMA,'smoke_witness':WITNESS_SCHEMA,'actor':{'type':'string'},'persist':{'type':'boolean'}},'additionalProperties':False}},
 {'name':'athena_promotion_get','description':'Fetch one persisted versioned PROMRUN with frozen local certificates, caller attestations, trust state, status and decision digest. Historical PROMOTION.1 receipts remain readable.','inputSchema':{'type':'object','required':['run_id'],'properties':{'run_id':{'type':'string','minLength':1}},'additionalProperties':False}},
 {'name':'athena_promotion_replay','description':'Replay a stored PROMOTION.1 or PROMOTION.2 predicate from its frozen inputs using the matching historical evaluator version. Replay checks receipt determinism; it does not independently query the external CI provider.','inputSchema':{'type':'object','required':['run_id'],'properties':{'run_id':{'type':'string','minLength':1}},'additionalProperties':False}},
 {'name':'athena_promotion_recent','description':'List recent persisted unified runtime promotion receipts across historical PROMOTION.1 and current PROMOTION.2 semantics.','inputSchema':{'type':'object','properties':{'limit':{'type':'integer','minimum':1,'maximum':200}},'additionalProperties':False}},
]
PROMOTION_TOOL_NAMES={tool['name'] for tool in PROMOTION_TOOLS}
PROMOTION_RESOURCE={'uri':'athena://promotion','name':'ATHENA Unified Runtime Promotion Receipt Ledger','mimeType':'application/json'}
