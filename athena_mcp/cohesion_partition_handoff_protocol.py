PARTITION_PACKET_SCHEMA={
    'type':'object',
    'required':[
        'packet_id','work_key','targets','dependencies','shared_sinks','integration_order',
        'merge_strategy','exact_refs','verification_requirements','handoff_conditions'
    ],
    'properties':{
        'packet_id':{'type':'string','minLength':1},
        'work_key':{'type':'string','minLength':1},
        'targets':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
        'dependencies':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
        'shared_sinks':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
        'integration_order':{'type':'integer','minimum':0},
        'merge_strategy':{'type':'string','minLength':1},
        'exact_refs':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
        'verification_requirements':{
            'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True
        },
        'handoff_conditions':{
            'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True
        },
        'acceptance_criteria':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
        'assignee_hint':{'type':['string','null']},
    },
    'additionalProperties':False,
}

PARTITION_TOOL={
    'name':'athena_cohesion_partition',
    'description':(
        'Validate and persist an advisory partition proposal over explicit caller-supplied work packets. '
        'Unique exact work keys and disjoint owned targets are required for parallel execution. Declared shared sinks '
        'must carry distinct integration order and are serialized. Dependency/shared-sink edges must remain acyclic. '
        'The tool never creates assignments, claims, presence, scheduler authority, or execution authority.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['partition_id','proposer_id','goal_ref','packets'],
        'properties':{
            'partition_id':{'type':'string','minLength':1},
            'proposer_id':{'type':'string','minLength':1},
            'goal_ref':{'type':'string','minLength':1},
            'packets':{'type':'array','minItems':2,'items':PARTITION_PACKET_SCHEMA},
            'party_id':{'type':['string','null']},
            'quest_ref':{'type':['string','null']},
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

HANDOFF_TOOL={
    'name':'athena_cohesion_handoff',
    'description':(
        'Route or inspect a typed baton transfer through Message Board V1. The handoff freezes sender/receiver, exact refs, '
        'completed delta, residual, invariants, tests, blockers, next edge and the sender claim id. MESSAGE_ACK is the '
        'consumption receipt. Cohesion reports claim-release readiness and early-release policy violations but never '
        'releases a claim itself.'
    ),
    'inputSchema':{
        'type':'object',
        'required':[
            'handoff_id','sender','receiver','exact_refs','completed_delta','residual','invariants','tests',
            'blockers','next_edge','required_receipt'
        ],
        'properties':{
            'handoff_id':{'type':'string','minLength':1},
            'sender':{'type':'string','minLength':1},
            'receiver':{'type':'string','minLength':1},
            'exact_refs':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
            'completed_delta':{'type':'string','minLength':1},
            'residual':{'type':'string','minLength':1},
            'invariants':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
            'tests':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
            'blockers':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'next_edge':{'type':'string','minLength':1},
            'required_receipt':{'type':'string','enum':['MESSAGE_ACK','NONE']},
            'partition_id':{'type':['string','null']},
            'packet_id':{'type':['string','null']},
            'work_key':{'type':['string','null']},
            'party_id':{'type':['string','null']},
            'goal_refs':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

COHESION_PARTITION_HANDOFF_TOOLS=[PARTITION_TOOL,HANDOFF_TOOL]
COHESION_PARTITION_HANDOFF_TOOL_NAMES={tool['name'] for tool in COHESION_PARTITION_HANDOFF_TOOLS}
