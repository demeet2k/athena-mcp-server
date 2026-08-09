PARTITION_PROOF_SCHEMA={
    'type':['object','null'],
    'required':['proof_id','disjoint_targets','shared_sinks','evidence_refs'],
    'properties':{
        'proof_id':{'type':'string','minLength':1},
        'disjoint_targets':{'type':'array','minItems':2,'items':{'type':'string','minLength':1},'uniqueItems':True},
        'shared_sinks':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
        'evidence_refs':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
    },
    'additionalProperties':False,
}

DUPLICATE_GUARD_TOOL={
    'name':'athena_cohesion_duplicate_guard',
    'description':(
        'Read shared-current Message Board claims and classify exact work-key/task/target collisions, fuzzy warnings, '
        'declared JOIN/REPLICA intent, and target-only partition evidence into non-authoritative treatment options. '
        'This tool never mutates claims, auto-joins, assigns work, fabricates MATA semantics, or grants execution authority.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['agent_id','task'],
        'properties':{
            'agent_id':{'type':'string','minLength':1},
            'task':{'type':'string','minLength':1},
            'work_key':{'type':['string','null']},
            'targets':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'intended_mode':{'type':'string','enum':['PRIMARY','REPLICA']},
            'replication_reason':{'type':['string','null']},
            'join_agent_id':{'type':['string','null']},
            'partition_proof':PARTITION_PROOF_SCHEMA,
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },
        'additionalProperties':False,
    },
}

DUPLICATE_GUARD_TOOLS=[DUPLICATE_GUARD_TOOL]
DUPLICATE_GUARD_TOOL_NAMES={tool['name'] for tool in DUPLICATE_GUARD_TOOLS}
