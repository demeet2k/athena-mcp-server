PARTY_CHANNEL_TOOL={
    'name':'athena_party_message',
    'description':(
        'Post a party-scoped coordination message through canonical Message Board V1. The message is tagged '
        'with party_id and explicit party goal refs; only acknowledged party-tagged messages in the current '
        'reward window can contribute to party XP eligibility. Posting itself earns zero XP.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['party_id','sender','recipients','goal_refs','message'],
        'properties':{
            'party_id':{'type':'string','minLength':1},
            'sender':{'type':'string','minLength':1},
            'recipients':{
                'type':'array','minItems':1,
                'items':{'type':'string','minLength':1},'uniqueItems':True
            },
            'goal_refs':{
                'type':'array','minItems':1,
                'items':{'type':'string','minLength':1},'uniqueItems':True
            },
            'message':{'type':'string','minLength':1},
            'message_kind':{
                'type':'string',
                'enum':['INFO','UPDATE','QUESTION','ANSWER','BLOCKER','DISCOVERY','HELP','HANDOFF']
            },
            'reply_to':{'type':['string','null']},
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

PARTY_CHANNEL_TOOLS=[PARTY_CHANNEL_TOOL]
PARTY_CHANNEL_TOOL_NAMES={PARTY_CHANNEL_TOOL['name']}
