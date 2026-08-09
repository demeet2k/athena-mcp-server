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

STR={'type':'string'};NUM={'type':'number'};OBJ={'type':'object'};INT={'type':'integer'}

COLLECTIVE_V16_TOOLS=[
    _tool(
        'athena_ordered_dag_posterior',
        'Enumerate the exact finite DAG family consistent with a caller-declared topological order and score it with a bounded linear-Gaussian BIC/edge-prior model. Optional external isotonic calibration maps edge posterior probabilities to empirical reliability. Read-only; not general causal graph posterior discovery.',
        ('samples','order'),
        {
            'samples': {'type':'array','minItems':40,'maxItems':5000,'items':OBJ},
            'order': {'type':'array','minItems':2,'maxItems':5,'uniqueItems':True,'items':STR},
            'prior_edge_probability': {'type':'number','minimum':0.001,'maximum':0.999},
            'top_k': {'type':'integer','minimum':1,'maximum':64},
            'calibration_examples': {'type':'array','minItems':40,'maxItems':10000,'items':OBJ},
        },
    ),
    _tool(
        'athena_longitudinal_dr_multistage_crossfit',
        'Estimate supplied dynamic-policy values with bounded cross-fitted sequential regression and inverse-propensity augmentation across 1..6 binary treatment stages under explicit caller-declared decision-time histories. PLAN_ONLY; not an arbitrary-horizon causal theorem.',
        ('samples','stages','outcome','policies'),
        {
            'samples': {'type':'array','minItems':120,'maxItems':20000,'items':OBJ},
            'stages': {'type':'array','minItems':1,'maxItems':6,'items':OBJ},
            'outcome': STR,
            'policies': {'type':'array','minItems':1,'maxItems':32,'items':OBJ},
            'folds': {'type':'integer','minimum':2,'maximum':10},
            'seed': INT,
            'propensity_clip': {'type':'number','minimum':0.01,'maximum':0.25},
        },
    ),
    _tool(
        'athena_gaussian_mixture_update',
        'Perform the exact posterior update for a supplied finite Gaussian-mixture prior under one shared linear-Gaussian observation. This is a bounded non-Gaussian family, not general non-Gaussian Bayes.',
        ('variables','components','observation'),
        {
            'variables': {'type':'array','minItems':1,'maxItems':12,'uniqueItems':True,'items':STR},
            'components': {'type':'array','minItems':2,'maxItems':16,'items':OBJ},
            'observation': OBJ,
        },
    ),
    _tool(
        'athena_approx_error_field',
        'Learn a bounded RBF-kernel approximation-error field from explicit error witnesses and report out-of-fold residual-calibrated query envelopes plus support distance. Read-only; not a formal distribution-free or global regularity certificate.',
        ('feature_order','witnesses','queries'),
        {
            'feature_order': {'type':'array','minItems':1,'maxItems':8,'uniqueItems':True,'items':STR},
            'witnesses': {'type':'array','minItems':30,'maxItems':96,'items':OBJ},
            'queries': {'type':'array','minItems':1,'maxItems':256,'items':OBJ},
            'bandwidth': {'type':'number','exclusiveMinimum':0},
            'ridge': {'type':'number','exclusiveMinimum':0},
            'folds': {'type':'integer','minimum':2,'maximum':10},
            'coverage': {'type':'number','minimum':0.5,'exclusiveMaximum':1},
            'seed': INT,
            'max_support_distance': {'type':'number','minimum':0},
        },
    ),
    _tool(
        'athena_coupled_model_robust_policy',
        'Exactly evaluate a supplied finite policy set across a finite family of complete transition/reward models when one adversarial model is held fixed for the whole horizon. Coupled ambiguity is non-rectangular across state/time, but this is evaluation of supplied policies rather than general non-rectangular DRO optimization.',
        ('states','initial_state','models','policies','horizon'),
        {
            'states': {'type':'array','minItems':1,'maxItems':8,'uniqueItems':True,'items':STR},
            'initial_state': STR,
            'models': {'type':'array','minItems':2,'maxItems':8,'items':OBJ},
            'policies': {'type':'array','minItems':1,'maxItems':32,'items':OBJ},
            'horizon': {'type':'integer','minimum':1,'maximum':6},
            'discount': {'type':'number','minimum':0,'maximum':1},
        },
    ),
]
COLLECTIVE_V16_TOOL_NAMES={tool['name'] for tool in COLLECTIVE_V16_TOOLS}
