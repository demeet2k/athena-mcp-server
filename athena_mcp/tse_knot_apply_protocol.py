TSE_KNOT_APPLY_TOOL={
    'name':'athena_tse_knot_observe_apply',
    'description':(
        'Observe an externally completed shared Git adoption of a SOURCE_BOUND TSE child Return. '
        'This tool never merges, rebases, cherry-picks, pushes, assigns work, creates claims, or resets platform counters. '
        'It emits RETURN_APPLIED only when the frozen parent and verified child commits are both ancestors of the exact freshly verified shared applied HEAD.'
    ),
    'inputSchema':{
        'type':'object',
        'required':['mission_id','route','hatch','child_return_event_id','apply_receipt','actor_id','witnesses','cost'],
        'properties':{
            'mission_id':{'type':'string','minLength':1},
            'route':{'type':'object'},
            'hatch':{'type':'object'},
            'child_return_event_id':{'type':'string','minLength':1},
            'apply_receipt':{
                'type':'object',
                'required':['schema_version','apply_id','mode','parent_head','child_head','applied_head','apply_witnesses','platform_counter_reset_claimed'],
                'properties':{
                    'schema_version':{'type':'string','const':'ATHENA.TSE.KNOT.APPLY.RECEIPT.V1'},
                    'apply_id':{'type':'string','minLength':1},
                    'mode':{'type':'string','const':'ANCESTRY_ADOPTION'},
                    'parent_head':{'type':'string','minLength':1},
                    'child_head':{'type':'string','minLength':1},
                    'applied_head':{'type':'string','minLength':1},
                    'apply_witnesses':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
                    'platform_counter_reset_claimed':{'type':'boolean','const':False},
                },
                'additionalProperties':False,
            },
            'actor_id':{'type':'string','minLength':1},
            'witnesses':{'type':'array','minItems':1,'items':{'type':'string','minLength':1},'uniqueItems':True},
            'cost':{
                'type':'object','required':['known'],
                'properties':{'known':{'type':'boolean'},'total':{}},
                'additionalProperties':False,
            },
            'remote':{'type':'string'},
        },
        'additionalProperties':False,
    },
}

TSE_KNOT_APPLY_TOOLS=[TSE_KNOT_APPLY_TOOL]
TSE_KNOT_APPLY_TOOL_NAMES={tool['name'] for tool in TSE_KNOT_APPLY_TOOLS}
TSE_KNOT_APPLY_RESOURCE={
    'uri':'athena://tse-knot-apply/v1',
    'name':'ATHENA TSE Self-Tightening Knot Apply V1',
    'mimeType':'application/json',
}
