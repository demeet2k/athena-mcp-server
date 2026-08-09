from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {'name':name,'description':description,'inputSchema':{'type':'object','required':list(required),'properties':properties or {},'additionalProperties':False}}

STR={'type':'string'};NUM={'type':'number'};OBJ={'type':'object'};BOOL={'type':'boolean'};INT={'type':'integer'}

COLLECTIVE_V13_TOOLS=[
    _tool('athena_gp_hyperqmc','Approximate a continuous log-uniform GP hyperparameter posterior over a declared positive box using deterministic Halton quasi-Monte Carlo particles. Read-only.',('context_key',),{'context_key':STR,'bounds':OBJ,'samples':{'type':'integer','minimum':32,'maximum':512},'seed':INT}),
    _tool('athena_gp_fitc_predict','Predict with a deterministic inducing-point FITC GP approximation and expose query-level error against the exact current bounded GP reference.',('context_key','features'),{'context_key':STR,'features':OBJ,'inducing_count':{'type':'integer','minimum':1,'maximum':48},'include_observation_noise':BOOL}),
    _tool('athena_gp_joint_design','Rank candidate GP measurements by downstream decision EVSI plus expected hypermodel entropy reduction under the QMC hyperposterior. DESIGN_ONLY.',('context_key','actions','experiments'),{'context_key':STR,'actions':{'type':'array','minItems':1,'maxItems':24,'items':{'type':'object'}},'experiments':{'type':'array','minItems':1,'maxItems':48,'items':{'type':'object'}},'bounds':OBJ,'hyper_samples':{'type':'integer','minimum':32,'maximum':512},'mc_samples':{'type':'integer','minimum':80,'maximum':1200},'seed':INT,'information_weight':NUM,'decision_weight':NUM,'cost_weight':NUM,'risk_weight':NUM}),
    _tool('athena_fci_lite_discover','Build a bounded FCI-inspired partial ancestral candidate using all observed-variable conditioning subsets up to a declared order, collider orientation and limited propagation. Not full FCI/RFCI.',('samples',),{'samples':{'type':'array','minItems':30,'maxItems':10000,'items':{'type':'object'}},'variables':{'type':'array','minItems':3,'maxItems':8,'items':STR},'alpha':NUM,'max_conditioning':{'type':'integer','minimum':0,'maximum':3}}),
    _tool('athena_longitudinal_tmle','Estimate static two-timepoint binary treatment-regime risks with sequential logistic targeting. Assumption-scoped and not a general longitudinal-TMLE theorem.',('samples','treatment1','intermediate','treatment2','outcome'),{'samples':{'type':'array','minItems':100,'maxItems':20000,'items':{'type':'object'}},'treatment1':STR,'intermediate':STR,'treatment2':STR,'outcome':STR,'baseline':{'type':'array','maxItems':16,'items':STR},'regimes':{'type':'array','maxItems':16,'items':{'type':'object'}},'assumptions':OBJ,'propensity_clip':NUM}),
    _tool('athena_dynamic_policy_value','Value deterministic two-timepoint treatment policies through the bounded longitudinal parametric g-formula. Assumption-scoped and PLAN_ONLY.',('samples','treatment1','intermediate','treatment2','outcome','policies'),{'samples':{'type':'array','minItems':80,'maxItems':20000,'items':{'type':'object'}},'treatment1':STR,'intermediate':STR,'treatment2':STR,'outcome':STR,'policies':{'type':'array','minItems':1,'maxItems':32,'items':{'type':'object'}},'baseline':{'type':'array','maxItems':16,'items':STR},'assumptions':OBJ}),
    _tool('athena_dro_resource_select','Select a finite candidate subset under correlated Gaussian resource covariance plus ellipsoidal mean ambiguity; exact enumeration only below the declared threshold.',('candidates','budgets','covariances'),{'candidates':{'type':'array','minItems':1,'maxItems':24,'items':{'type':'object'}},'budgets':OBJ,'covariances':OBJ,'ambiguity_radius':NUM,'alpha':NUM,'exact_limit':{'type':'integer','minimum':1,'maximum':18}}),
]

from .collective_v14_protocol import COLLECTIVE_V14_TOOLS
COLLECTIVE_V13_TOOLS.extend(t for t in COLLECTIVE_V14_TOOLS if t['name'] not in {x['name'] for x in COLLECTIVE_V13_TOOLS})
