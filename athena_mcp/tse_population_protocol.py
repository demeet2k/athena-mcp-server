TSE_POPULATION_PLAN_TOOL={
    'name':'athena_tse_population_plan',
    'description':(
        'Project one active TSE Hatch packet into a deterministic population route and Cohesion NEED contract. '
        'Pure planning only: it publishes nothing, assigns nothing, and creates no Message Board claim.'
    ),
    'inputSchema':{
        'type':'object','required':['hatch','parent_agent_id','capabilities'],
        'properties':{
            'hatch':{'type':'object'},
            'parent_agent_id':{'type':'string','minLength':1},
            'capabilities':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
            'targets':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'dependencies':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'role':{'type':'string'},
            'needed_units':{'type':'integer','minimum':1,'maximum':64},
            'constraints':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'life_policy':{'type':['string','null']},
            'clear_condition_digest':{'type':['string','null']},
        },'additionalProperties':False,
    },
}

TSE_POPULATION_PUBLISH_TOOL={
    'name':'athena_tse_population_publish',
    'description':(
        'Publish a planned TSE population NEED through the existing Cohesion/Message Board authority. '
        'The parent must already hold active Message Board presence. This does not match or assign a worker.'
    ),
    'inputSchema':{
        'type':'object','required':['route'],
        'properties':{'route':{'type':'object'},'remote':{'type':'string'}},
        'additionalProperties':False,
    },
}

TSE_POPULATION_MATCH_TOOL={
    'name':'athena_tse_population_match',
    'description':(
        'Run current Cohesion matchmaking for a published TSE NEED and deterministically bind the best eligible advisory candidate. '
        'MATCH remains advisory and never creates assignment, execution authority, or Message Board claim.'
    ),
    'inputSchema':{
        'type':'object','required':['route'],
        'properties':{
            'route':{'type':'object'},
            'min_score':{'type':'number','minimum':0,'maximum':100},
            'limit':{'type':'integer','minimum':1,'maximum':50},
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },'additionalProperties':False,
    },
}

TSE_POPULATION_HANDOFF_TOOL={
    'name':'athena_tse_population_handoff',
    'description':(
        'Route a matched TSE subtask as a Message Board HANDOFF from the parent to the advisory candidate. '
        'Routing is not consumption, ACK is not claim, and this tool never claims or joins on behalf of the matched agent.'
    ),
    'inputSchema':{
        'type':'object','required':['route'],
        'properties':{'route':{'type':'object'},'remote':{'type':'string'}},
        'additionalProperties':False,
    },
}

TSE_POPULATION_CLAIM_STATE_TOOL={
    'name':'athena_tse_population_claim_state',
    'description':(
        'Observe the current shared Message Board and bind a compatible matched-agent claim to a routed TSE subtask. '
        'The matched agent must establish the claim independently; this tool is read-only with respect to ownership.'
    ),
    'inputSchema':{
        'type':'object','required':['route'],
        'properties':{
            'route':{'type':'object'},'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },'additionalProperties':False,
    },
}

TSE_POPULATION_RETURN_CHECK_TOOL={
    'name':'athena_tse_population_return_check',
    'description':(
        'Verify that a TSE child Return is bound to the exact Hatch, population route, matched agent, observed Message Board claim, '
        'positive verified delta and public witnesses. It returns a consumption-ready envelope only; it does not apply the Return.'
    ),
    'inputSchema':{
        'type':'object','required':['route','child_return'],
        'properties':{'route':{'type':'object'},'child_return':{'type':'object'}},
        'additionalProperties':False,
    },
}

TSE_POPULATION_TOOLS=[
    TSE_POPULATION_PLAN_TOOL,TSE_POPULATION_PUBLISH_TOOL,TSE_POPULATION_MATCH_TOOL,
    TSE_POPULATION_HANDOFF_TOOL,TSE_POPULATION_CLAIM_STATE_TOOL,TSE_POPULATION_RETURN_CHECK_TOOL,
]
TSE_POPULATION_TOOL_NAMES={tool['name'] for tool in TSE_POPULATION_TOOLS}
TSE_POPULATION_RESOURCE={
    'uri':'athena://tse-population/v1',
    'name':'ATHENA TSE Population Circulation V1',
    'mimeType':'application/json',
}
