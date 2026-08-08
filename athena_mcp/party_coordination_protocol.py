TASK_RELATION_ENUM=[
    'IDENTICAL','INDEPENDENT','COMMUTATIVE','ORDERED','CONDITIONAL','CONFLICT','INCOMPARABLE'
]
COORDINATION_MODE_ENUM=['PARALLEL_COMPLEMENT','INDEPENDENT_VERIFY']
PARTY_POST_KIND_ENUM=['WORKING_ON','NEED','OFFER','DECISION','BLOCKER','RESULT']

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

PARTY_COORDINATION_TOOLS=[
    {
        'name':'athena_party_form',
        'description':(
            'Form an authority-neutral multi-goal agent party with explicit communication channels. '
            'The leader is registered as the first member. Formation alone earns no XP.'
        ),
        'inputSchema':{
            'type':'object',
            'required':['party_id','task_ref','leader','goals','channels'],
            'properties':{
                'party_id':{'type':'string','minLength':1},
                'task_ref':{'type':'string','minLength':1},
                'leader':{'type':'string','minLength':1},
                'goals':{'type':'array','minItems':2,'items':GOAL_SCHEMA},
                'channels':{
                    'type':'array','minItems':1,
                    'items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'purpose':{'type':'string'},
                'capacity':{'type':'integer','minimum':2,'maximum':16},
                'role':{'type':'string'},
                'capabilities':{
                    'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'claim_refs':{
                    'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True
                },
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_party_join',
        'description':(
            'Join an open party while declaring task relation, capabilities, claims, and a registered '
            'communication channel. CONFLICT work is held; IDENTICAL work requires INDEPENDENT_VERIFY.'
        ),
        'inputSchema':{
            'type':'object',
            'required':['party_id','agent','channel_ref','task_relation'],
            'properties':{
                'party_id':{'type':'string','minLength':1},
                'agent':{'type':'string','minLength':1},
                'channel_ref':{'type':'string','minLength':1},
                'task_relation':{'type':'string','enum':TASK_RELATION_ENUM},
                'coordination_mode':{'type':'string','enum':COORDINATION_MODE_ENUM},
                'role':{'type':'string'},
                'capabilities':{
                    'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'claim_refs':{
                    'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True
                },
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_party_board_post',
        'description':(
            'Post presence/work/need/offer/decision/blocker/result state to a party message board. '
            'Posts must use a registered channel; DECISION and RESULT posts require witness_ref.'
        ),
        'inputSchema':{
            'type':'object',
            'required':['post_id','party_id','agent','kind','channel_ref','body'],
            'properties':{
                'post_id':{'type':'string','minLength':1},
                'party_id':{'type':'string','minLength':1},
                'agent':{'type':'string','minLength':1},
                'kind':{'type':'string','enum':PARTY_POST_KIND_ENUM},
                'channel_ref':{'type':'string','minLength':1},
                'body':{'type':'string','minLength':1},
                'goal_refs':{
                    'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'claim_refs':{
                    'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'witness_ref':{'type':'string','minLength':1},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_party_state',
        'description':'Return one party, members, board posts, Big-3 coordination score, and XP receipts.',
        'inputSchema':{
            'type':'object',
            'required':['party_id'],
            'properties':{'party_id':{'type':'string','minLength':1}},
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_party_list',
        'description':'List party summaries and coordination activity counts.',
        'inputSchema':{
            'type':'object',
            'properties':{
                'status':{'type':'string','enum':['OPEN','CLOSED']},
                'limit':{'type':'integer','minimum':1,'maximum':500},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_party_observe',
        'description':(
            'Record a witnessed multi-goal party outcome and calculate a small receipt-gated '
            'coordination XP bonus. Membership itself never earns XP; awarded bonus is capped at 5%.'
        ),
        'inputSchema':{
            'type':'object',
            'required':[
                'observation_id','party_id','observer','base_xp','advanced_goal_ids','witness_ref'
            ],
            'properties':{
                'observation_id':{'type':'string','minLength':1},
                'party_id':{'type':'string','minLength':1},
                'observer':{'type':'string','minLength':1},
                'base_xp':{'type':'number','minimum':0},
                'advanced_goal_ids':{
                    'type':'array','minItems':2,
                    'items':{'type':'string','minLength':1},'uniqueItems':True
                },
                'witness_ref':{'type':'string','minLength':1},
            },
            'additionalProperties':False,
        },
    },
]

PARTY_COORDINATION_TOOL_NAMES={tool['name'] for tool in PARTY_COORDINATION_TOOLS}
PARTY_COORDINATION_RESOURCE={
    'uri':'athena://party-coordination/v1',
    'name':'ATHENA Party Coordination + Message Board V1',
    'mimeType':'application/json',
}
