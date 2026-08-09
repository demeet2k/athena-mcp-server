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

COLLECTIVE_V15_TOOLS=[
    _tool(
        'athena_structural_reliability_calibrate',
        'Calibrate bootstrap structural support against externally labelled correctness with out-of-fold isotonic reliability. Read-only; calibrated reliability is not a causal graph posterior.',
        ('calibration_examples',),
        {
            'calibration_examples': {'type':'array','minItems':40,'maxItems':10000,'items':{'type':'object'}},
            'supports': {'type':'array','maxItems':512,'items':NUM},
            'folds': {'type':'integer','minimum':2,'maximum':10},
            'seed': INT,
        },
    ),
    _tool(
        'athena_longitudinal_tmle_crossfit',
        'Cross-fit the bounded two-timepoint sequential logistic TMLE surface across held-out folds. Assumption-scoped; not a general longitudinal TMLE theorem.',
        ('samples','treatment1','intermediate','treatment2','outcome'),
        {
            'samples': {'type':'array','minItems':160,'maxItems':20000,'items':{'type':'object'}},
            'treatment1': STR,
            'intermediate': STR,
            'treatment2': STR,
            'outcome': STR,
            'baseline': {'type':'array','maxItems':16,'items':STR},
            'regimes': {'type':'array','minItems':1,'maxItems':16,'items':{'type':'object'}},
            'assumptions': OBJ,
            'propensity_clip': NUM,
            'folds': {'type':'integer','minimum':2,'maximum':10},
            'seed': INT,
        },
    ),
    _tool(
        'athena_sequential_dr_policy_crossfit',
        'Estimate deterministic two-timepoint dynamic-policy value with out-of-fold sequential AIPW nuisance predictions. PLAN_ONLY and assumption-scoped.',
        ('samples','treatment1','intermediate','treatment2','outcome','policies'),
        {
            'samples': {'type':'array','minItems':180,'maxItems':20000,'items':{'type':'object'}},
            'treatment1': STR,
            'intermediate': STR,
            'treatment2': STR,
            'outcome': STR,
            'policies': {'type':'array','minItems':1,'maxItems':32,'items':{'type':'object'}},
            'baseline': {'type':'array','maxItems':16,'items':STR},
            'assumptions': OBJ,
            'propensity_clip': NUM,
            'folds': {'type':'integer','minimum':2,'maximum':10},
            'seed': INT,
        },
    ),
    _tool(
        'athena_joint_gaussian_update',
        'Perform the exact finite-dimensional multivariate-Gaussian posterior update for one declared linear-Gaussian observation. Model state only; not general continuous Bayes.',
        ('variables','mean','covariance','observation'),
        {
            'variables': {'type':'array','minItems':1,'maxItems':16,'items':STR},
            'mean': {'type':'array','minItems':1,'maxItems':16,'items':NUM},
            'covariance': {'type':'array','minItems':1,'maxItems':16,'items':{'type':'array','items':NUM}},
            'observation': OBJ,
        },
    ),
    _tool(
        'athena_joint_gaussian_control',
        'Rank linear actions under a declared multivariate Gaussian belief using exact moments, lower-tail Normal CVaR, cost and Pareto preservation. PLAN_ONLY.',
        ('variables','mean','covariance','actions'),
        {
            'variables': {'type':'array','minItems':1,'maxItems':16,'items':STR},
            'mean': {'type':'array','minItems':1,'maxItems':16,'items':NUM},
            'covariance': {'type':'array','minItems':1,'maxItems':16,'items':{'type':'array','items':NUM}},
            'actions': {'type':'array','minItems':1,'maxItems':64,'items':{'type':'object'}},
            'cvar_alpha': NUM,
            'risk_weight': NUM,
            'cost_weight': NUM,
        },
    ),
    _tool(
        'athena_approx_error_transport',
        'Transport witnessed approximation error to nearby queries through a caller-declared Lipschitz envelope that must be consistent with supplied witness pairs. Certificate is conditional on that bound.',
        ('feature_order','witnesses','queries','lipschitz_bound'),
        {
            'feature_order': {'type':'array','minItems':1,'maxItems':32,'items':STR},
            'witnesses': {'type':'array','minItems':2,'maxItems':4096,'items':{'type':'object'}},
            'queries': {'type':'array','minItems':1,'maxItems':512,'items':{'type':'object'}},
            'lipschitz_bound': NUM,
            'max_transport_radius': NUM,
            'margin_safety': NUM,
        },
    ),
    _tool(
        'athena_multistage_tv_dro_plan',
        'Solve a bounded finite-horizon robust dynamic program under state-action rectangular total-variation ambiguity around supplied transition distributions. PLAN_ONLY.',
        ('states','initial_state','actions_by_state','horizon','tv_radius'),
        {
            'states': {'type':'array','minItems':1,'maxItems':24,'items':STR},
            'initial_state': STR,
            'actions_by_state': OBJ,
            'horizon': {'type':'integer','minimum':1,'maximum':8},
            'tv_radius': NUM,
            'discount': NUM,
        },
    ),
]
