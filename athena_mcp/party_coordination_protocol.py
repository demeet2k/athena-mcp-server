TASK_RELATION_ENUM=[
    'INDEPENDENT','COMMUTATIVE','ORDERED','CONDITIONAL','IDENTICAL','INCOMPARABLE','CONFLICT'
]

GOAL_SCHEMA={
    'type':'object',
    'required':['goal_id'],
    'properties':{
        'goal_id':{'type':'string','minLength':1},
        'required_capabilities':{
            'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True
        },
    },
    'additionalProperties':False,
}

RESULT_SCHEMA={
    'type':'object',
    'required':['goal_id','agent_id','witness_ref'],
    'properties':{
        'goal_id':{'type':'string','minLength':1},
        'agent_id':{'type':'string','minLength':1},
        'witness_ref':{'type':'string','minLength':1},
        'result_event_ref':{'type':['string','null']},
    },
    'additionalProperties':False,
}

PARTY_COORDINATION_TOOLS=[
    {
        'name':'athena_party_form',
        'description':(
            'Form a Git-shared multi-goal party on top of Message Board V1. The leader must already '
            'be actively present on the shared board. Formation emits a durable party event but earns no XP.'
        ),
        'inputSchema':{
            'type':'object',
            'required':['party_id','leader','goals','leader_goal_refs'],
            'properties':{
                'party_id':{'type':'string','minLength':1},
                'leader':{'type':'string','minLength':1},
                'purpose':{'type':'string'},
                'goals':{'type':'array','minItems':2,'items':GOAL_SCHEMA},
                'leader_goal_refs':{
                    'type':'array','minItems':1,
                    'items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'role':{'type':'string'},
                'capabilities':{
                    'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'capacity':{'type':'integer','minimum':2,'maximum':16},
                'remote':{'type':'string'},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_party_join',
        'description':(
            'Join an existing party while already present on Message Board V1. Goal ownership, role, '
            'capabilities, task relation, and current board claim are frozen into the shared party record.'
        ),
        'inputSchema':{
            'type':'object',
            'required':['party_id','agent','goal_refs','task_relation'],
            'properties':{
                'party_id':{'type':'string','minLength':1},
                'agent':{'type':'string','minLength':1},
                'goal_refs':{
                    'type':'array','minItems':1,
                    'items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'task_relation':{'type':'string','enum':TASK_RELATION_ENUM},
                'role':{'type':'string'},
                'capabilities':{
                    'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'remote':{'type':'string'},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_party_state',
        'description':(
            'Read one party after a fresh shared-board sync, including members, current board presence, '
            'acknowledged communication evidence, Big-3 score, and reward receipts.'
        ),
        'inputSchema':{
            'type':'object',
            'required':['party_id'],
            'properties':{
                'party_id':{'type':'string','minLength':1},
                'remote':{'type':'string'},
                'shared_remote_mode':{
                    'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']
                },
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_party_list',
        'description':'List Git-shared parties after synchronizing the Message Board frontier.',
        'inputSchema':{
            'type':'object',
            'properties':{
                'remote':{'type':'string'},
                'shared_remote_mode':{
                    'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']
                },
                'limit':{'type':'integer','minimum':1,'maximum':500},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_party_observe',
        'description':(
            'Record a witnessed multi-goal party outcome and calculate a small receipt-gated coordination '
            'XP bonus candidate. Party Reward Provenance V3 requires current frozen claims, ACKed typed result '
            'events, and a globally unused source_xp_ref before an award; legacy calls missing those coordinates '
            'remain parseable but HOLD. The tool never mutates global XP authority.'
        ),
        'inputSchema':{
            'type':'object',
            'required':['observation_id','party_id','observer','base_xp','results','witness_ref'],
            'properties':{
                'observation_id':{'type':'string','minLength':1},
                'party_id':{'type':'string','minLength':1},
                'observer':{'type':'string','minLength':1},
                'base_xp':{'type':'number','minimum':0},
                'source_xp_ref':{'type':['string','null']},
                'source_xp_witness_ref':{'type':['string','null']},
                'results':{'type':'array','minItems':2,'items':RESULT_SCHEMA},
                'witness_ref':{'type':'string','minLength':1},
                'remote':{'type':'string'},
            },
            'additionalProperties':False,
        },
    },
]

PARTY_COORDINATION_TOOL_NAMES={tool['name'] for tool in PARTY_COORDINATION_TOOLS}
PARTY_COORDINATION_RESOURCE={
    'uri':'athena://party-coordination/v1',
    'name':'ATHENA Party Coordination V1 over Message Board V1',
    'mimeType':'application/json',
}
