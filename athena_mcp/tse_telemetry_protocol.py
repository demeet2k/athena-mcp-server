TSE_TELEMETRY_RECORD_TOOL={
    'name':'athena_tse_telemetry_record',
    'description':(
        'Persist one caller-declared public TSE Helical Handoff observation to the shared Git ledger. '
        'Declared events are audit-visible but excluded from primary source-bound conversion metrics; use the TSE Helix composition tools '
        'when the transition can be re-derived from actual TSE/Cohesion/Message-Board state.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['mission_id','route_id','hatch_id','transition','actor_id','witnesses','cost'],
        'properties':{
            'mission_id':{'type':'string','minLength':1},
            'route_id':{'type':'string','minLength':1},
            'hatch_id':{'type':'string','minLength':1},
            'transition':{'type':'string','enum':[
                'HATCH_CREATED','HATCH_NEED_PUBLISHED','MATCH_FOUND','HANDOFF_ROUTED','HANDOFF_CONSUMED',
                'CHILD_CLAIMED','CHILD_VERIFIED_RETURN','RETURN_APPLIED','HELIX_HOLD'
            ]},
            'actor_id':{'type':'string','minLength':1},
            'witnesses':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
            'cost':{
                'type':'object','required':['known'],
                'properties':{'known':{'type':'boolean'},'total':{}},
                'additionalProperties':False,
            },
            'parent_event_id':{'type':['string','null']},
            'child_agent_id':{'type':['string','null']},
            'child_claim_id':{'type':['string','null']},
            'verified_delta':{'type':['number','null'],'minimum':0},
            'hold_class':{'type':['string','null'],'enum':[
                'CAPABILITY_HOLD','STALE_STATE_HOLD','DUPLICATION_COLLAPSE','ROUTED_NOT_CONSUMED',
                'ACKED_NOT_CLAIMED','AUTHORITY_HOLD','EVIDENCE_HOLD','NO_POSITIVE_HATCH',None
            ]},
            'seam':{'type':['string','null']},
            'attempt_ref':{'type':['string','null']},
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

TSE_TELEMETRY_REPORT_TOOL={
    'name':'athena_tse_telemetry_report',
    'description':(
        'Read one mission helix ledger and report source-bound funnel conversion separately from caller-declared observations. '
        'Primary eta metrics count SOURCE_BOUND events only; zero denominators and unknown costs remain UNKNOWN and the report has no causal authority.'
    ),
    'inputSchema':{
        'type':'object','required':['mission_id'],
        'properties':{
            'mission_id':{'type':'string','minLength':1},
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },
        'additionalProperties':False,
    },
}

TSE_TELEMETRY_TOOLS=[TSE_TELEMETRY_RECORD_TOOL,TSE_TELEMETRY_REPORT_TOOL]
TSE_TELEMETRY_TOOL_NAMES={tool['name'] for tool in TSE_TELEMETRY_TOOLS}
TSE_TELEMETRY_RESOURCE={
    'uri':'athena://tse-telemetry/v1',
    'name':'ATHENA TSE Helical Handoff Telemetry V2',
    'mimeType':'application/json',
}
