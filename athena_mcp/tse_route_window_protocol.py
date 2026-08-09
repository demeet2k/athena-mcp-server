ROUTE_IDS_SCHEMA={'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True}
SOURCE_REFS_SCHEMA={'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True}
SEAMS=['PUBLISH','MATCH','HANDOFF','CONSUMPTION','CLAIM','RETURN','APPLY']

TSE_ROUTE_WINDOW_OPEN_TOOL={
    'name':'athena_tse_route_window_open',
    'description':(
        'Open a Git-backed observation scope for one TSE Helix mission. The window scopes descriptive measurement only; '
        'it creates no assignment, claim, stop, life, Return or causal authority.'
    ),
    'inputSchema':{
        'type':'object','required':['window_id','mission_id','actor_id'],
        'properties':{
            'window_id':{'type':'string','minLength':1},
            'mission_id':{'type':'string','minLength':1},
            'actor_id':{'type':'string','minLength':1},
            'route_ids':ROUTE_IDS_SCHEMA,
            'source_refs':SOURCE_REFS_SCHEMA,
            'remote':{'type':'string'},
        },'additionalProperties':False,
    },
}

TSE_ROUTE_WINDOW_CLOSE_TOOL={
    'name':'athena_tse_route_window_close',
    'description':(
        'Close a TSE Helix observation window and freeze route scope plus explicit observation maturity. '
        'Complete seams and resolved routes describe what was observed, not what execution must do.'
    ),
    'inputSchema':{
        'type':'object','required':['window_id','mission_id','actor_id','complete_seams'],
        'properties':{
            'window_id':{'type':'string','minLength':1},
            'mission_id':{'type':'string','minLength':1},
            'actor_id':{'type':'string','minLength':1},
            'complete_seams':{'type':'array','items':{'type':'string','enum':SEAMS},'uniqueItems':True},
            'resolved_routes':{
                'type':'object',
                'additionalProperties':ROUTE_IDS_SCHEMA,
            },
            'route_ids':ROUTE_IDS_SCHEMA,
            'source_refs':SOURCE_REFS_SCHEMA,
            'remote':{'type':'string'},
        },'additionalProperties':False,
    },
}

TSE_ROUTE_WINDOW_STATE_TOOL={
    'name':'athena_tse_route_window_state',
    'description':'Read one TSE Helix observation-window packet with shared-frontier status.',
    'inputSchema':{
        'type':'object','required':['window_id'],
        'properties':{
            'window_id':{'type':'string','minLength':1},
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },'additionalProperties':False,
    },
}

TSE_ROUTE_WINDOW_REPORT_TOOL={
    'name':'athena_tse_route_window_report',
    'description':(
        'Project SOURCE_BOUND Helix telemetry into unique-route stage attainment, retry/hold pressure, censoring intervals, '
        'resolved conversion and apply-channel state. Event retries cannot inflate route conversion.'
    ),
    'inputSchema':{
        'type':'object','required':['window_id'],
        'properties':{
            'window_id':{'type':'string','minLength':1},
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },'additionalProperties':False,
    },
}

TSE_ROUTE_WINDOW_TOOLS=[
    TSE_ROUTE_WINDOW_OPEN_TOOL,TSE_ROUTE_WINDOW_CLOSE_TOOL,TSE_ROUTE_WINDOW_STATE_TOOL,TSE_ROUTE_WINDOW_REPORT_TOOL,
]
TSE_ROUTE_WINDOW_TOOL_NAMES={tool['name'] for tool in TSE_ROUTE_WINDOW_TOOLS}
TSE_ROUTE_WINDOW_RESOURCE={
    'uri':'athena://tse-route-window/v1',
    'name':'ATHENA TSE Helix Route Window Calculus V1',
    'mimeType':'application/json',
}
