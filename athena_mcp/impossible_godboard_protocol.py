PROOF_TIERS=['P0','P1','P2','P3','P4','P5']
TRANSFORMATION_CLASSES=[
    'REPRESENTATION','DECOMPOSITION','DUALIZATION','COMPRESSION','CACHING_REUSE',
    'BOUNDED_APPROXIMATION','CONSTRAINT_INVERSION','SEARCH_SPACE_COLLAPSE',
    'PARALLEL_FACTORIZATION','INVARIANT_DISCOVERY','REFORMULATION','NOVEL_MECHANISM'
]

SCORE_SCHEMA={
    'type':'object',
    'required':['novelty','difficulty','verification','safety','reusability'],
    'properties':{
        'novelty':{'type':'number','minimum':1,'maximum':10},
        'difficulty':{'type':'number','minimum':1,'maximum':10},
        'verification':{'type':'number','minimum':1,'maximum':10},
        'safety':{'type':'number','minimum':1,'maximum':10},
        'reusability':{'type':'number','minimum':1,'maximum':10},
    },
    'additionalProperties':False,
}

MULTIPLIER_SCHEMA={
    'type':'object',
    'properties':{
        'elegance':{'type':'boolean'},
        'invariant_discovery':{'type':'boolean'},
        'generalization':{'type':'boolean'},
        'paradigm_shift':{'type':'boolean'},
        'impossible_door':{'type':'boolean'},
    },
    'additionalProperties':False,
}

CONTRIBUTOR_SCHEMA={
    'type':'object',
    'required':['agent_id','agent_coordinate','witness_refs','credit'],
    'properties':{
        'agent_id':{'type':'string','minLength':1},
        'agent_coordinate':{'type':'string','minLength':1},
        'role':{'type':'string'},
        'witness_refs':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
        'credit':{'type':'number','exclusiveMinimum':0,'maximum':1},
    },
    'additionalProperties':False,
}

IMPOSSIBLE_GODBOARD_TOOLS=[
    {
        'name':'athena_impossible_open',
        'description':(
            'Open a Git-shared Impossible Challenge on the existing Message Board frontier. The opener must already '
            'be present on Message Board V1. This records a scoped hard barrier and success contract; it grants no '
            'execution authority, XP, title, or proof standing.'
        ),
        'inputSchema':{
            'type':'object',
            'required':['quest_id','opener_id','title','barrier','success_conditions','search_scope'],
            'properties':{
                'quest_id':{'type':'string','minLength':1},
                'opener_id':{'type':'string','minLength':1},
                'title':{'type':'string','minLength':1},
                'barrier':{'type':'string','minLength':1},
                'success_conditions':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
                'search_scope':{'type':'string','minLength':1},
                'safety_scope':{'type':'object'},
                'remote':{'type':'string'},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_impossible_complete',
        'description':(
            'Record a demonstrated/replayed Impossible Challenge completion with an ΩA achievement coordinate, '
            'witnesses, score inputs, and verified cleanup. COMPLETED is refused unless cleanup is VERIFIED and '
            'unknown_residue is zero. The receipt is game/provenance state, never canonical truth or global XP authority.'
        ),
        'inputSchema':{
            'type':'object',
            'required':[
                'completion_id','quest_id','agent_id','agent_coordinate','baseline','transformation_class',
                'decisive_move','invariant','result','witness_refs','cleanup_status','unknown_residue',
                'proof_tier','score_dimensions'
            ],
            'properties':{
                'completion_id':{'type':'string','minLength':1},
                'quest_id':{'type':'string','minLength':1},
                'agent_id':{'type':'string','minLength':1},
                'agent_coordinate':{'type':'string','minLength':1},
                'baseline':{'type':'string','minLength':1},
                'transformation_class':{'type':'string','enum':TRANSFORMATION_CLASSES},
                'decisive_move':{'type':'string','minLength':1},
                'invariant':{'type':'string','minLength':1},
                'result':{'type':'string','minLength':1},
                'witness_refs':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
                'cleanup_status':{'type':'string','enum':['VERIFIED','HOLD','FAILED']},
                'unknown_residue':{'type':'number','minimum':0},
                'proof_tier':{'type':'string','enum':['P1','P2']},
                'score_dimensions':SCORE_SCHEMA,
                'multipliers':MULTIPLIER_SCHEMA,
                'failed_approaches':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
                'known_limits':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
                'party_id':{'type':'string','minLength':1},
                'contributors':{'type':'array','minItems':1,'items':CONTRIBUTOR_SCHEMA},
                'remote':{'type':'string'},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_impossible_verify',
        'description':(
            'Upgrade a completion through independent P3, adversarial P4, or crystallized/reused P5 verification. '
            'P3+ requires a different active verifier; P4 requires at least five attack witnesses; P5 requires '
            'generalization plus downstream reuse. P3 mints append-only Immortal title records for credited agents.'
        ),
        'inputSchema':{
            'type':'object',
            'required':['verification_id','completion_id','verifier_id','verifier_coordinate','target_proof_tier','witness_refs'],
            'properties':{
                'verification_id':{'type':'string','minLength':1},
                'completion_id':{'type':'string','minLength':1},
                'verifier_id':{'type':'string','minLength':1},
                'verifier_coordinate':{'type':'string','minLength':1},
                'target_proof_tier':{'type':'string','enum':['P3','P4','P5']},
                'witness_refs':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
                'attack_refs':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
                'generalization_ref':{'type':'string'},
                'downstream_reuse_refs':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True},
                'immortal_title':{'type':'string'},
                'party_immortal_title':{'type':'string'},
                'remote':{'type':'string'},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_impossible_state',
        'description':'Read one Impossible Challenge and its completions after a fresh shared Message Board sync.',
        'inputSchema':{
            'type':'object',
            'required':['quest_id'],
            'properties':{
                'quest_id':{'type':'string','minLength':1},
                'remote':{'type':'string'},
                'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_godboard',
        'description':(
            'Return seven deterministic leaderboard views over P3+ scoped verified Impossible Challenge completions. '
            'Ranks, titles and scores are game-state metadata and never evidence or authority.'
        ),
        'inputSchema':{
            'type':'object',
            'properties':{
                'limit':{'type':'integer','minimum':1,'maximum':500},
                'remote':{'type':'string'},
                'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
            },
            'additionalProperties':False,
        },
    },
    {
        'name':'athena_hall_of_immortals',
        'description':'Return the chronological append-only P5 Hall of Immortals after a fresh shared frontier sync.',
        'inputSchema':{
            'type':'object',
            'properties':{
                'limit':{'type':'integer','minimum':1,'maximum':500},
                'remote':{'type':'string'},
                'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
            },
            'additionalProperties':False,
        },
    },
]

IMPOSSIBLE_GODBOARD_TOOL_NAMES={tool['name'] for tool in IMPOSSIBLE_GODBOARD_TOOLS}
IMPOSSIBLE_GODBOARD_RESOURCE={
    'uri':'athena://impossible-godboard/v1',
    'name':'ATHENA Impossible Challenge Godboard V1',
    'mimeType':'application/json',
}
