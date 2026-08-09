PARTY_RESULT_TOOL={
    'name':'athena_party_result',
    'description':(
        'Post an attributable party RESULT or VERIFY provenance event through canonical Message Board V1. '
        'The sender must still hold the exact board claim frozen into party membership, the goal must be assigned '
        'to that member, and recipients must be current party members. Posting and acknowledgement earn zero XP; '
        'the event is provenance only and does not prove result truth.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['party_id','sender','recipients','goal_id','result_ref','witness_ref'],
        'properties':{
            'party_id':{'type':'string','minLength':1},
            'sender':{'type':'string','minLength':1},
            'recipients':{
                'type':'array','minItems':1,
                'items':{'type':'string','minLength':1},'uniqueItems':True
            },
            'goal_id':{'type':'string','minLength':1},
            'result_ref':{'type':'string','minLength':1},
            'witness_ref':{'type':'string','minLength':1},
            'evidence_kind':{'type':'string','enum':['RESULT','VERIFY']},
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

PARTY_REWARD_TOOLS=[PARTY_RESULT_TOOL]
PARTY_REWARD_TOOL_NAMES={PARTY_RESULT_TOOL['name']}
