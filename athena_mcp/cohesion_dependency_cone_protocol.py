CALLER_EDGE_SCHEMA={
    'type':'object',
    'required':['src','relation','dst'],
    'properties':{
        'src':{'type':'string','minLength':3},
        'relation':{'type':'string','minLength':1},
        'dst':{'type':'string','minLength':3},
        'evidence_refs':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
    },
    'additionalProperties':False,
}

CHANGE_SCHEMA={
    'type':'object',
    'required':['kind'],
    'properties':{
        'kind':{'type':'string','enum':['GIT_RANGE','GIT_PATHS','CLAIM','MESSAGE','WORK_KEY','TARGET','DEPENDENCY','COHESION_ENTRY','DECISION']},
        'base_ref':{'type':['string','null']},
        'head_ref':{'type':['string','null']},
        'changed_paths':{'type':['array','null'],'items':{'type':'string','minLength':1},'uniqueItems':True},
        'claim_id':{'type':['string','null']},
        'agent_id':{'type':['string','null']},
        'work_key':{'type':['string','null']},
        'targets':{'type':['array','null'],'items':{'type':'string','minLength':1},'uniqueItems':True},
        'status_change':{'type':['string','null']},
        'event_id':{'type':['string','null']},
        'sender':{'type':['string','null']},
        'recipients':{'type':['array','null'],'items':{'type':'string','minLength':1},'uniqueItems':True},
        'requires_ack':{'type':['boolean','null']},
        'dependency_refs':{'type':['array','null'],'items':{'type':'string','minLength':1},'uniqueItems':True},
        'entry_id':{'type':['string','null']},
        'goal_ref':{'type':['string','null']},
        'decision_ref':{'type':['string','null']},
        'refs':{'type':['array','null'],'items':{'type':'string','minLength':3},'uniqueItems':True},
    },
    'additionalProperties':False,
}

DEPENDENCY_CONE_TOOL={
    'name':'athena_cohesion_dependency_cone',
    'description':(
        'Compute a bounded read-only targeted invalidation cone over shared-current Message Board, Party, Cohesion, '
        'and exact Git-path/dependency evidence. Returns affected live lanes, explicit propagation paths, required '
        'rehydrate/recheck/read/ack actions, unaffected observed lanes, and unknown residue. Never performs refresh, '
        'ack, claim mutation, assignment, global reset, Freshness-Train requalification, or MATA inference.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['change'],
        'properties':{
            'change':CHANGE_SCHEMA,
            'caller_edges':{'type':['array','null'],'items':CALLER_EDGE_SCHEMA},
            'max_depth':{'type':'integer','minimum':1,'maximum':8},
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },
        'additionalProperties':False,
    },
}

DEPENDENCY_CONE_TOOLS=[DEPENDENCY_CONE_TOOL]
DEPENDENCY_CONE_TOOL_NAMES={tool['name'] for tool in DEPENDENCY_CONE_TOOLS}
