from __future__ import annotations

BIONANO_VERSION='BNMK.V1'
BIONANO_RESOURCE={
    'uri':'athena://bio/nanomachines/v1',
    'name':'ATHENA Bionanomachine Mechanism Kernel V1',
    'description':'Stable BNMK.V1 MCP ABI with a 12-archetype/12-facet KC144 mechanism atlas and BNMK.ADAPTER20.V2 primary-source-conditioned evidence layer.'
}

BIONANO_TOOLS=[
    {
        'name':'athena_bionano_catalog',
        'description':'Return the BNMK 12-archetype KC144 catalog. The stable 14-seed view is preserved; V2 additionally reports 20 source-backed adapters (14 seeds + 6 expansions), primary-source counts, operator phylogeny and optional evidence packets. Conditioned measurements are never universal constants.',
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
        'description':'Compile one known BNMK machine into the evidence-aware 4D/12D/KC144 contract, primary-source witness, conditioned quantitative claims, row associations and state cycle. Unknown IDs HOLD rather than fabricating a classification.',
        'inputSchema':{
            'type':'object','required':['machine_id'],
            'properties':{'machine_id':{'type':'string','minLength':1}},
            'additionalProperties':False
        }
    },
    {
        'name':'athena_bionano_transfer',
        'description':'Map a known biological mechanism into a target ATHENA problem as explicit COMPUTATIONAL_ANALOGY. Primary source support improves the mechanism model but never grants execution authority or causal equivalence.',
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
        'description':'Return an assembly/function packet. T4 preserves the supplied 15-part USER_VISUAL BOM separately from the primary-source-conditioned infection transition sequence; other machines return generic functional modules rather than fabricated native subunit inventories.',
        'inputSchema':{
            'type':'object','required':['machine_id'],
            'properties':{'machine_id':{'type':'string','minLength':1}},
            'additionalProperties':False
        }
    },
]

BIONANO_TOOL_NAMES={tool['name'] for tool in BIONANO_TOOLS}
