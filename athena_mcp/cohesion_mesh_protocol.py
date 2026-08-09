REQUEST_KIND_ENUM=['NEED','OFFER']

REQUEST_OFFER_TOOL={
    'name':'athena_cohesion_request_offer',
    'description':(
        'Publish an idempotent typed NEED/OFFER envelope through Message Board V1. '
        'The publishing agent must already have active shared-board presence. This does not assign work.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['request_id','agent_id','kind','capabilities','goal_ref'],
        'properties':{
            'request_id':{'type':'string','minLength':1},
            'agent_id':{'type':'string','minLength':1},
            'kind':{'type':'string','enum':REQUEST_KIND_ENUM},
            'capabilities':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'goal_ref':{'type':'string','minLength':1},
            'role':{'type':'string'},
            'work_key':{'type':['string','null']},
            'targets':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'dependencies':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'provides':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'capacity_units':{'type':'integer','minimum':1,'maximum':64},
            'needed_units':{'type':'integer','minimum':1,'maximum':64},
            'constraints':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'acceptance_criteria':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'party_id':{'type':['string','null']},
            'quest_ref':{'type':['string','null']},
            'life_policy':{'type':['string','null']},
            'clear_condition_digest':{'type':['string','null']},
            'allow_collaboration':{'type':'boolean'},
            'expires_at':{'type':['string','null']},
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

MATCHMAKE_TOOL={
    'name':'athena_cohesion_matchmake',
    'description':(
        'Advisory deterministic matchmaking for one active NEED using explicit active OFFER envelopes, '
        'Message Board presence/claim state, capability fit, dependency unlock, capacity, and collision risk. '
        'It never creates a claim, assignment, party membership, or truth authority.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['need_id'],
        'properties':{
            'need_id':{'type':'string','minLength':1},
            'limit':{'type':'integer','minimum':1,'maximum':50},
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },
        'additionalProperties':False,
    },
}

COALITION_TOOL={
    'name':'athena_cohesion_coalition',
    'description':(
        'Build and persist a Message Board-backed campaign/coalition proposal over multiple active NEEDs. '
        'The proposal greedily respects explicit OFFER capacity and is advisory only; it creates no presence, claims, '
        'party membership, scheduler authority, or execution authority.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['campaign_id','proposer_id','need_ids'],
        'properties':{
            'campaign_id':{'type':'string','minLength':1},
            'proposer_id':{'type':'string','minLength':1},
            'need_ids':{'type':'array','minItems':2,'items':{'type':'string','minLength':1},'uniqueItems':True},
            'max_participants':{'type':'integer','minimum':2,'maximum':32},
            'exit_criteria':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'rendezvous_refs':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

MISSION_SAMPLE_SCHEMA={
    'type':'object',
    'required':[
        'mission_id','match_key','evidence_refs','productive_transition_count','verified_delta','cost',
        'duplicate_actions','stale_actions','human_interrupts','merge_debt','meta_overhead','closure',
        'stop_class','authority_evidence_violations'
    ],
    'properties':{
        'mission_id':{'type':'string','minLength':1},
        'match_key':{'type':'string','minLength':1},
        'evidence_refs':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
        'productive_transition_count':{'type':'number','minimum':0},
        'verified_delta':{'type':'number','minimum':0},
        'cost':{'type':'number','exclusiveMinimum':0},
        'duplicate_actions':{'type':'number','minimum':0},
        'stale_actions':{'type':'number','minimum':0},
        'human_interrupts':{'type':'number','minimum':0},
        'merge_debt':{'type':'number','minimum':0},
        'meta_overhead':{'type':'number','minimum':0},
        'closure':{'type':'boolean'},
        'stop_class':{'type':'string','minLength':1},
        'authority_evidence_violations':{'type':'number','minimum':0},
        'consumption_latency':{'type':'number','minimum':0},
        'failure_count':{'type':'number','minimum':0},
        'escaped_defects':{'type':'number','minimum':0},
        'wasted_overrun':{'type':'number','minimum':0},
        'reseed_quality':{'type':['number','null'],'minimum':0,'maximum':1},
    },
    'additionalProperties':False,
}

DECISION_RULE_SCHEMA={
    'type':'object',
    'required':[
        'rule_ref','frozen_before_results','min_pairs','min_primary_effect','max_duplicate_regression',
        'max_stale_regression','max_human_interrupt_regression','max_meta_overhead_regression'
    ],
    'properties':{
        'rule_ref':{'type':'string','minLength':1},
        'frozen_before_results':{'type':'boolean'},
        'min_pairs':{'type':'integer','minimum':2,'maximum':100},
        'min_primary_effect':{'type':'number'},
        'max_duplicate_regression':{'type':'number','minimum':0},
        'max_stale_regression':{'type':'number','minimum':0},
        'max_human_interrupt_regression':{'type':'number','minimum':0},
        'max_meta_overhead_regression':{'type':'number','minimum':0},
    },
    'additionalProperties':False,
}

SOLO_PARTY_COMPARE_TOOL={
    'name':'athena_cohesion_solo_party_compare',
    'description':(
        'Evidence-gated matched descriptive comparison of SOLO versus PARTY mission samples under a supplied '
        'predeclared rule. Weak/ambiguous matching returns UNKNOWN. A rule pass is descriptive observed evidence only, '
        'not a causal effect claim or canonical promotion witness.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['comparison_id','observer_id','solo_samples','party_samples','decision_rule'],
        'properties':{
            'comparison_id':{'type':'string','minLength':1},
            'observer_id':{'type':'string','minLength':1},
            'solo_samples':{'type':'array','minItems':1,'items':MISSION_SAMPLE_SCHEMA},
            'party_samples':{'type':'array','minItems':1,'items':MISSION_SAMPLE_SCHEMA},
            'decision_rule':DECISION_RULE_SCHEMA,
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

COHESION_MESH_TOOLS=[REQUEST_OFFER_TOOL,MATCHMAKE_TOOL,COALITION_TOOL,SOLO_PARTY_COMPARE_TOOL]
COHESION_MESH_TOOL_NAMES={tool['name'] for tool in COHESION_MESH_TOOLS}
COHESION_MESH_RESOURCE={
    'uri':'athena://cohesion/v1',
    'name':'ATHENA Cohesion Mesh V1 — Matchmaking Vertical Slice',
    'mimeType':'application/json',
}
