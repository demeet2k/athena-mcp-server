TSE_TELEMETRY_RECORD_TOOL={
    'name':'athena_tse_telemetry_record',
    'description':(
        'Persist one public TSE Helical Handoff transition receipt to the shared Git telemetry ledger. '
        'Telemetry is observation-only: it creates no claim, assignment, execution authority, life, Return application, or causal evidence.'
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
        'Read the shared TSE Helical Handoff ledger for one mission and report funnel conversion, typed residuals and value efficiency. '
        'Zero denominators and unknown costs remain UNKNOWN. The report has no causal promotion authority.'
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
    'name':'ATHENA TSE Helical Handoff Telemetry V1',
    'mimeType':'application/json',
}
