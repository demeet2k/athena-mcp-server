from __future__ import annotations

BIONANO_VERSION='BNMK.1'
BIONANO_RESOURCE={
    'uri':'athena://bio/nanomachines/v1',
    'name':'ATHENA Bionanomachine Mechanism Kernel V1',
    'description':'12-archetype/12-facet KC144 mechanism atlas with evidence-aware biological-to-computational transfer.'
}

BIONANO_TOOLS=[
    {
        'name':'athena_bionano_catalog',
        'description':'Return the BNMK 12-archetype/14-seed catalog, 12 mechanism facets, KC144 coordinate law, and epistemic firewalls. User seed values remain distinct from verified empirical constants.',
        'inputSchema':{
            'type':'object',
            'properties':{'include_atlas':{'type':'boolean'}},
            'additionalProperties':False
        }
    },
    {
        'name':'athena_bionano_compile',
        'description':'Compile one known seed machine into the evidence-aware 4D/12D/KC144 machine contract. Unknown IDs HOLD rather than fabricating a classification.',
        'inputSchema':{
            'type':'object','required':['machine_id'],
            'properties':{'machine_id':{'type':'string','minLength':1}},
            'additionalProperties':False
        }
    },
    {
        'name':'athena_bionano_transfer',
        'description':'Map a known biological mechanism into a target ATHENA problem as an explicit COMPUTATIONAL_ANALOGY with portable operators, nonportable context and transfer loss. It does not assert causal equivalence.',
        'inputSchema':{
            'type':'object','required':['machine_id','target'],
            'properties':{
                'machine_id':{'type':'string','minLength':1},
                'target':{'type':'string','minLength':1},
                'constraints':{'type':'array','items':{'type':'string'}},
            },
            'additionalProperties':False
        }
    },
    {
        'name':'athena_bionano_interface_match',
        'description':'Score a normalized producer/consumer interface profile over rate, latency, error tolerance, statefulness, reversibility and coupling. Smith-chart-inspired compatibility proxy; not physical electrical impedance.',
        'inputSchema':{
            'type':'object','required':['producer','consumer'],
            'properties':{
                'producer':{'$ref':'#/$defs/profile'},
                'consumer':{'$ref':'#/$defs/profile'}
            },
            '$defs':{
                'profile':{
                    'type':'object',
                    'required':['rate','latency','error_tolerance','statefulness','reversibility','coupling'],
                    'properties':{
                        'rate':{'type':'number','minimum':0,'maximum':1},
                        'latency':{'type':'number','minimum':0,'maximum':1},
                        'error_tolerance':{'type':'number','minimum':0,'maximum':1},
                        'statefulness':{'type':'number','minimum':0,'maximum':1},
                        'reversibility':{'type':'number','minimum':0,'maximum':1},
                        'coupling':{'type':'number','minimum':0,'maximum':1},
                    },
                    'additionalProperties':False
                }
            },
            'additionalProperties':False
        }
    },
    {
        'name':'athena_bionano_convergence_gate',
        'description':'Evaluate only caller-supplied convergence/stability witnesses: nth-term limit, ratio/root limit, contraction constant, or spectral radius. Assumption-incompatible or inconclusive values return HOLD.',
        'inputSchema':{
            'type':'object',
            'properties':{
                'nth_term_limit':{'type':['number','null']},
                'ratio_limit':{'type':['number','null'],'minimum':0},
                'root_limit':{'type':['number','null'],'minimum':0},
                'contraction_q':{'type':['number','null'],'minimum':0},
                'spectral_radius':{'type':['number','null'],'minimum':0},
            },
            'additionalProperties':False
        }
    },
    {
        'name':'athena_bionano_assembly',
        'description':'Return a parts/subassembly/functional-sequence machine packet. The T4-like phage seed preserves the supplied 15-part exploded drawing and four-stage sequence as USER_VISUAL provenance, not independently verified nomenclature.',
        'inputSchema':{
            'type':'object','required':['machine_id'],
            'properties':{'machine_id':{'type':'string','minLength':1}},
            'additionalProperties':False
        }
    },
]

BIONANO_TOOL_NAMES={tool['name'] for tool in BIONANO_TOOLS}
