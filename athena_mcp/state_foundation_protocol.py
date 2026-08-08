STATE_FOUNDATION_TOOLS=[
 {'name':'athena_schema_status','description':'Return the runtime DB schema-ledger version, component versions and current additive SQLite schema fingerprint.','inputSchema':{'type':'object','additionalProperties':False}},
 {'name':'athena_schema_plan','description':'Return the non-destructive migration plan from the current schema-ledger version to this runtime target. A future/newer DB schema blocks silent downgrade.','inputSchema':{'type':'object','additionalProperties':False}},
 {'name':'athena_schema_migrate','description':'Apply the next explicit additive schema migration receipt. Version 1 inventories/pins the already-created modular schema; it does not destructively rewrite organ tables.','inputSchema':{'type':'object','properties':{'actor':{'type':'string'}},'additionalProperties':False}},
 {'name':'athena_schema_verify','description':'Verify schema-ledger target version plus presence of critical unified-organ tables. Additive schema drift is reported separately from corruption.','inputSchema':{'type':'object','additionalProperties':False}},
 {'name':'athena_omega_state','description':'Project current accessible ATHENA runtime state into one Ω packet spanning semantic head, Git, base/crystal, Collective, branch/Y, AOR, development, cycle, promotion and migration state. Unavailable components remain UNKNOWN.','inputSchema':{'type':'object','additionalProperties':False}},
 {'name':'athena_reconstruct_state','description':'Persist a RECONRUN freezing current Ω plus the exact source refs actually consulted and optional expected refs. Missing expected refs become explicit defects; unlisted/unavailable sources are never implied searched.','inputSchema':{'type':'object','required':['task_ref','source_refs'],'properties':{'task_ref':{'type':'string','minLength':1},'source_refs':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},'expected_refs':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},'actor':{'type':'string'},'persist':{'type':'boolean'}},'additionalProperties':False}},
 {'name':'athena_reconstruction_get','description':'Fetch one frozen RECONRUN with exact consulted/expected source sets, Ω snapshot, defects and digest.','inputSchema':{'type':'object','required':['run_id'],'properties':{'run_id':{'type':'string','minLength':1}},'additionalProperties':False}},
 {'name':'athena_reconstruction_verify','description':'Recompute one RECONRUN digest from its frozen source contract and Ω snapshot. This verifies receipt integrity, not freshness of current state.','inputSchema':{'type':'object','required':['run_id'],'properties':{'run_id':{'type':'string','minLength':1}},'additionalProperties':False}},
 {'name':'athena_reconstruction_recent','description':'List recent reconstruction receipts without expanding full Ω snapshots.','inputSchema':{'type':'object','properties':{'limit':{'type':'integer','minimum':1,'maximum':500}},'additionalProperties':False}},
]
STATE_FOUNDATION_TOOL_NAMES={tool['name'] for tool in STATE_FOUNDATION_TOOLS}
STATE_FOUNDATION_RESOURCES=[
 {'uri':'athena://schema','name':'ATHENA Runtime Schema/Migration Ledger','mimeType':'application/json'},
 {'uri':'athena://state/omega','name':'ATHENA Ω Unified State Projection','mimeType':'application/json'},
 {'uri':'athena://reconstruction','name':'ATHENA RECONRUN Reconstruction Ledger','mimeType':'application/json'},
]
STATE_FOUNDATION_RESOURCE_URIS={resource['uri'] for resource in STATE_FOUNDATION_RESOURCES}
