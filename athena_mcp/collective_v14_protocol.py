from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {
        'name': name,
        'description': description,
        'inputSchema': {
            'type': 'object',
            'required': list(required),
            'properties': properties or {},
            'additionalProperties': False,
        },
    }

STR={'type':'string'};NUM={'type':'number'};OBJ={'type':'object'};BOOL={'type':'boolean'};INT={'type':'integer'}

COLLECTIVE_V14_TOOLS=[
    _tool(
        'athena_joint_factor_belief',
        'Compose a bounded finite joint science-twin belief across 2..5 caller-declared factor axes, compatibility multipliers and optional state likelihoods. Read-only; not a universal joint posterior.',
        ('axes',),
        {
            'axes': OBJ,
            'compatibility': {'type':'array','maxItems':256,'items':{'type':'object'}},
            'likelihood_by_state': OBJ,
        },
    ),
    _tool(
        'athena_structural_bootstrap_ensemble',
        'Bootstrap the bounded V13 FCI-lite discovery surface and return procedural graph-variant/marked-edge stability. Read-only; bootstrap frequency is not a causal posterior.',
        ('samples',),
        {
            'samples': {'type':'array','minItems':40,'maxItems':10000,'items':{'type':'object'}},
            'variables': {'type':'array','minItems':3,'maxItems':8,'items':STR},
            'bootstrap_runs': {'type':'integer','minimum':8,'maximum':128},
            'alpha': NUM,
            'max_conditioning': {'type':'integer','minimum':0,'maximum':3},
            'stable_threshold': NUM,
            'seed': INT,
        },
    ),
    _tool(
        'athena_joint_science_evi',
        'Compute exact finite decision EVI plus entropy reduction over supplied weighted joint science-twin states and declared outcome likelihoods. DESIGN_ONLY.',
        ('joint_states','actions','experiments'),
        {
            'joint_states': {'type':'array','minItems':2,'maxItems':512,'items':{'type':'object'}},
            'actions': {'type':'array','minItems':1,'maxItems':32,'items':{'type':'object'}},
            'experiments': {'type':'array','minItems':1,'maxItems':32,'items':{'type':'object'}},
            'information_weight': NUM,
            'decision_weight': NUM,
            'cost_weight': NUM,
            'risk_weight': NUM,
        },
    ),
    _tool(
        'athena_sequential_dr_policy_value',
        'Estimate deterministic two-timepoint dynamic-policy value with sequential AIPW augmentation and explicit history preservation. Assumption-scoped; not a general longitudinal causal theorem.',
        ('samples','treatment1','intermediate','treatment2','outcome','policies'),
        {
            'samples': {'type':'array','minItems':120,'maxItems':20000,'items':{'type':'object'}},
            'treatment1': STR,
            'intermediate': STR,
            'treatment2': STR,
            'outcome': STR,
            'policies': {'type':'array','minItems':1,'maxItems':32,'items':{'type':'object'}},
            'baseline': {'type':'array','maxItems':16,'items':STR},
            'assumptions': OBJ,
            'propensity_clip': NUM,
        },
    ),
    _tool(
        'athena_joint_policy_robust',
        'Rank policies over a bounded weighted joint-state ensemble using expected utility, lower-tail CVaR, worst case, expected/max regret and Pareto preservation. PLAN_ONLY.',
        ('joint_states','policies'),
        {
            'joint_states': {'type':'array','minItems':2,'maxItems':512,'items':{'type':'object'}},
            'policies': {'type':'array','minItems':1,'maxItems':64,'items':{'type':'object'}},
            'cvar_alpha': NUM,
            'risk_weight': NUM,
            'regret_weight': NUM,
            'cost_weight': NUM,
        },
    ),
    _tool(
        'athena_gp_resolution_route',
        'Choose the shallowest tested FITC/full-GP representation that preserves the exact current decision on the supplied action/query set under a declared decision-margin error rule.',
        ('context_key','actions'),
        {
            'context_key': STR,
            'actions': {'type':'array','minItems':1,'maxItems':32,'items':{'type':'object'}},
            'inducing_counts': {'type':'array','minItems':1,'maxItems':12,'items':{'type':'integer','minimum':1,'maximum':48}},
            'margin_safety': NUM,
            'include_observation_noise': BOOL,
        },
    ),
    _tool(
        'athena_two_stage_resource_plan',
        'Solve a bounded finite two-stage resource problem: choose first-stage candidates, then best feasible one-option recourse per declared scenario. Exact enumeration only below the finite threshold.',
        ('first_stage','scenarios'),
        {
            'first_stage': {'type':'array','minItems':1,'maxItems':24,'items':{'type':'object'}},
            'scenarios': {'type':'array','minItems':1,'maxItems':16,'items':{'type':'object'}},
            'risk_weight': NUM,
            'exact_limit': {'type':'integer','minimum':1,'maximum':18},
        },
    ),
]

from .collective_v15_protocol import COLLECTIVE_V15_TOOLS
COLLECTIVE_V14_TOOLS.extend(t for t in COLLECTIVE_V15_TOOLS if t['name'] not in {x['name'] for x in COLLECTIVE_V14_TOOLS})
