from __future__ import annotations

BIONANO_VERSION='BNMK.V1'
BIONANO_RESOURCE={
    'uri':'athena://bio/nanomachines/v1',
    'name':'ATHENA Bionanomachine Mechanism Kernel V1',
    'description':'Stable six-tool BNMK.V1 ABI backed by BNMK.ADAPTER20.V2 primary-source-conditioned mechanism evidence, populated KC144 facets, and explicit quantitative-claim firewalls.'
}

BIONANO_TOOLS=[
    {
        'name':'athena_bionano_catalog',
        'description':'Return the stable 12-archetype/14-seed BNMK catalog. V2 additive fields report 20 source-backed adapters, 20 primary sources, 15 conditioned quantitative claims, bounded expansions, operator phylogeny and optional evidence packets. User seed numbers remain distinct from verified empirical constants.',
        'inputSchema':{
            'type':'object',
            'properties':{
                'include_atlas':{'type':'boolean'},
                'include_evidence':{'type':'boolean'}
            },
            'additionalProperties':False
        }
    },
    {
        'name':'athena_bionano_compile',
        'description':'Compile one known BNMK machine into the source-backed 4D/12D/KC144 contract with primary-source witness, conditioned quantitative claims, state cycle and row associations. Unknown IDs HOLD rather than fabricating a classification.',
        'inputSchema':{
            'type':'object','required':['machine_id'],
            'properties':{'machine_id':{'type':'string','minLength':1}},
            'additionalProperties':False
        }
    },
    {
        'name':'athena_bionano_transfer',
        'description':'Map a source-backed biological mechanism into a target ATHENA problem as explicit COMPUTATIONAL_ANALOGY. Primary-source support improves the mechanism model but never grants execution authority or causal equivalence.',
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
        'description':'Evaluate only caller-supplied convergence/stability witnesses: nth-term limit, ratio/root limit, contraction constant, or spectral radius. Assumption-incompatible or inconclusive values return HOLD; V2 does not change these V1 semantics.',
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
        'description':'Return an assembly/function packet. T4 preserves the supplied 15-part USER_VISUAL BOM separately from the primary-source-conditioned infection transition sequence; other machines return generic functional modules rather than fabricated native molecular subunit inventories.',
        'inputSchema':{
            'type':'object','required':['machine_id'],
            'properties':{'machine_id':{'type':'string','minLength':1}},
            'additionalProperties':False
        }
    },
]

BIONANO_TOOL_NAMES={tool['name'] for tool in BIONANO_TOOLS}
