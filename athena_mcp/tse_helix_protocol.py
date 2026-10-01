COST_SCHEMA={
    'type':'object','required':['known'],
    'properties':{'known':{'type':'boolean'},'total':{}},
    'additionalProperties':False,
}
WITNESS_SCHEMA={'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True}

TSE_HELIX_OPEN_TOOL={
    'name':'athena_tse_helix_open',
    'description':(
        'Validate one TSE Hatch through the population planner and persist a source-bound HATCH_CREATED telemetry root. '
        'Composition-only: the telemetry write creates no assignment, claim, Return authority, life or causal evidence.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['mission_id','hatch','parent_agent_id','capabilities','actor_id','witnesses','cost'],
        'properties':{
            'mission_id':{'type':'string','minLength':1},
            'hatch':{'type':'object'},
            'parent_agent_id':{'type':'string','minLength':1},
            'capabilities':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
            'actor_id':{'type':'string','minLength':1},
            'witnesses':WITNESS_SCHEMA,
            'cost':COST_SCHEMA,
            'targets':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'dependencies':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'role':{'type':'string'},
            'needed_units':{'type':'integer','minimum':1,'maximum':64},
            'constraints':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'life_policy':{'type':['string','null']},
            'clear_condition_digest':{'type':['string','null']},
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

TSE_HELIX_ADVANCE_TOOL={
    'name':'athena_tse_helix_advance',
    'description':(
        'Advance one TSE Helix transition. PUBLISH/MATCH/HANDOFF/CLAIM_STATE/RETURN_CHECK execute the real population source and '
        'append a source-bound observation. APPLY observes an externally completed shared Git ancestry adoption. REENTRY_PREVIEW '
        'validates SOURCE_BOUND RETURN_APPLIED against the fresh shared frontier and compiles a routing-only successor without '
        'executing it. REENTRY_START explicitly delegates the selected or ambiguity-preserving task to the existing Git rehydration '
        'loop. Re-entry is never background execution and never grants merge, claim, evidence or provider-counter-reset authority.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['mission_id','operation','route','parent_event_id','actor_id','witnesses','cost'],
        'properties':{
            'mission_id':{'type':'string','minLength':1},
            'operation':{'type':'string','enum':['PUBLISH','MATCH','HANDOFF','CLAIM_STATE','RETURN_CHECK','APPLY','REENTRY_PREVIEW','REENTRY_START']},
            'route':{'type':'object'},
            'parent_event_id':{
                'type':'string','minLength':1,
                'description':'For APPLY this is the exact SOURCE_BOUND CHILD_VERIFIED_RETURN event. For REENTRY_* it is the exact SOURCE_BOUND RETURN_APPLIED event.'
            },
            'actor_id':{'type':'string','minLength':1},
            'witnesses':WITNESS_SCHEMA,
            'cost':COST_SCHEMA,
            'child_return':{
                'type':['object','null'],
                'description':(
                    'RETURN_CHECK: child Return payload. APPLY: {hatch,apply_receipt}. REENTRY_PREVIEW/REENTRY_START: '
                    '{hatch,reentry:{schema_version:ATHENA.TSE.REENTRY.PACKET.V1,reentry_id,goal?,successor_candidates?,successor_policy?,profile?,source_ref?,use_frontier?,fetch?,allow_parent_residual_fallback?,allow_ambiguity_resolution?,terminal_request?,terminal_witnesses?,max_steps?,max_no_progress?,max_prompt_chars?,depth_mode?,required_passes?,stop_conditions?,platform_counter_reset_claimed:false}}.'
                ),
            },
            'min_score':{'type':'number','minimum':0,'maximum':100},
            'limit':{'type':'integer','minimum':1,'maximum':50},
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },
        'additionalProperties':False,
    },
}

TSE_HELIX_CONSUMPTION_TOOL={
    'name':'athena_tse_helix_observe_consumption',
    'description':(
        'Read the current shared Message Board and emit HANDOFF_CONSUMED only when the exact routed TSE envelope remains bound and '
        'the exact matched agent has an actual ACK for that handoff message. ACK remains distinct from claim.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['mission_id','route','parent_event_id','actor_id','witnesses','cost'],
        'properties':{
            'mission_id':{'type':'string','minLength':1},
            'route':{'type':'object'},
            'parent_event_id':{'type':'string','minLength':1},
            'actor_id':{'type':'string','minLength':1},
            'witnesses':WITNESS_SCHEMA,
            'cost':COST_SCHEMA,
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },
        'additionalProperties':False,
    },
}

TSE_HELIX_RECONCILE_TOOL={
    'name':'athena_tse_helix_reconcile',
    'description':(
        'Re-derive a missing source-bound population telemetry event from current authoritative TSE/Cohesion/Message-Board state '
        'without replaying the original source mutation. Historical state that can no longer be reproduced fails closed. APPLY and '
        'REENTRY use their own idempotent observation/start membranes and are never reconstructed by replaying a merge or a loop start.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['mission_id','operation','route','parent_event_id','actor_id','witnesses','cost'],
        'properties':{
            'mission_id':{'type':'string','minLength':1},
            'operation':{'type':'string','enum':['PUBLISH','MATCH','HANDOFF','CLAIM_STATE','RETURN_CHECK']},
            'route':{'type':'object'},
            'parent_event_id':{'type':'string','minLength':1},
            'actor_id':{'type':'string','minLength':1},
            'witnesses':WITNESS_SCHEMA,
            'cost':COST_SCHEMA,
            'child_return':{'type':['object','null']},
            'min_score':{'type':'number','minimum':0,'maximum':100},
            'limit':{'type':'integer','minimum':1,'maximum':50},
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },
        'additionalProperties':False,
    },
}

TSE_HELIX_TOOLS=[TSE_HELIX_OPEN_TOOL,TSE_HELIX_ADVANCE_TOOL,TSE_HELIX_CONSUMPTION_TOOL,TSE_HELIX_RECONCILE_TOOL]
TSE_HELIX_TOOL_NAMES={tool['name'] for tool in TSE_HELIX_TOOLS}
TSE_HELIX_RESOURCE={
    'uri':'athena://tse-helix/v2',
    'name':'ATHENA TSE Helical Handoff Composition V2',
    'mimeType':'application/json',
}
