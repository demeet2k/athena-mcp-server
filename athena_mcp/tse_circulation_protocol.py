WITNESS_SCHEMA={'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True}

TSE_CIRCULATION_OBSERVE_TOOL={
    'name':'athena_tse_circulation_observe',
    'description':(
        'Observe and persist one closed, sequence-bound TSE circulation receipt from a SOURCE_BOUND origin RETURN_APPLIED '
        'through a marked re-entry loop with at least one observed productive rehydration receipt to a later SOURCE_BOUND '
        'RETURN_APPLIED. Measurement only: Git ancestry and typed lineage do not establish causal treatment effect, execution '
        'authority, total cost, or background continuation.'
    ),
    'inputSchema':{
        'type':'object',
        'required':[
            'cycle_id','mission_id','origin_route','origin_hatch','origin_return_applied_event_id','reentry_id',
            'rehydration_loop_id','next_route','next_hatch','next_return_applied_event_id','actor_id','witnesses'
        ],
        'properties':{
            'cycle_id':{'type':'string','minLength':1},
            'mission_id':{'type':'string','minLength':1},
            'origin_route':{'type':'object'},
            'origin_hatch':{'type':'object'},
            'origin_return_applied_event_id':{'type':'string','minLength':1},
            'reentry_id':{'type':'string','minLength':1},
            'rehydration_loop_id':{'type':'string','minLength':1},
            'next_route':{'type':'object'},
            'next_hatch':{'type':'object'},
            'next_return_applied_event_id':{'type':'string','minLength':1},
            'actor_id':{'type':'string','minLength':1},
            'witnesses':WITNESS_SCHEMA,
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

TSE_CIRCULATION_REPORT_TOOL={
    'name':'athena_tse_circulation_report',
    'description':(
        'Report persisted closed TSE circulation receipts. The V1 denominator contains only observed closed receipts, so '
        'pending-cycle count and closure rate remain UNKNOWN rather than silently treating unobserved starts as failures or zeros.'
    ),
    'inputSchema':{
        'type':'object',
        'properties':{
            'mission_id':{'type':['string','null']},
            'remote':{'type':'string'},
            'shared_remote_mode':{'type':'string','enum':['REQUIRED','BEST_EFFORT','DISABLED']},
        },
        'additionalProperties':False,
    },
}

TSE_CIRCULATION_TOOLS=[TSE_CIRCULATION_OBSERVE_TOOL,TSE_CIRCULATION_REPORT_TOOL]
TSE_CIRCULATION_TOOL_NAMES={tool['name'] for tool in TSE_CIRCULATION_TOOLS}
TSE_CIRCULATION_RESOURCE={
    'uri':'athena://tse-circulation/v1',
    'name':'ATHENA TSE Closed Helix Circulation V1',
    'mimeType':'application/json',
}

# COST-367: carry the existing scalar cost contract through the already-qualified
# Re-Entry/Rehydration/Circulation path. The extension mutates no scheduler or
# execution authority and keeps host/provider resource truth explicitly UNKNOWN.
from .tse_cost_carrier import install_tse_cost_carrier_extension

install_tse_cost_carrier_extension(TSE_CIRCULATION_TOOLS)

# Harden the additive carrier after its wrappers are installed: storage markers
# remain persisted but are not presented as semantic stop conditions, and report
# aggregation refuses top-level mirrors that disagree with the digested basis.
from .tse_cost_carrier_hardening import install_tse_cost_carrier_hardening

install_tse_cost_carrier_hardening()
