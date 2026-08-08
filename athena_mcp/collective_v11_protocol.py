from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {"name":name,"description":description,"inputSchema":{"type":"object","required":list(required),"properties":properties or {},"additionalProperties":False}}

STR={"type":"string"}; NUM={"type":"number"}; OBJ={"type":"object"}; BOOL={"type":"boolean"}; INT={"type":"integer"}

COLLECTIVE_V11_TOOLS=[
    _tool("athena_gp_hyperfit","Grid-search fixed RBF GP hyperparameters by exact marginal likelihood; optional CAS application to current GP model.",( "context_key",),{"context_key":STR,"length_scales":{"type":"array","items":NUM,"maxItems":16},"signal_variances":{"type":"array","items":NUM,"maxItems":16},"noise_variances":{"type":"array","items":NUM,"maxItems":16},"apply":BOOL,"expected_observation_count":INT}),
    _tool("athena_gp_decision_evsi","Estimate downstream decision value of candidate GP measurements by conditional-Gaussian Monte Carlo. DESIGN_ONLY.",( "context_key","actions","experiments"),{"context_key":STR,"actions":{"type":"array","minItems":1,"maxItems":64,"items":{"type":"object"}},"experiments":{"type":"array","minItems":1,"maxItems":128,"items":{"type":"object"}},"samples":{"type":"integer","minimum":50,"maximum":2000},"seed":INT,"cost_weight":NUM,"risk_weight":NUM}),
    _tool("athena_latent_project_admg","Project a supplied causal DAG with explicit latent nodes into a restricted observed ADMG using latent-only internal directed paths/common latent ancestors. Not data discovery.",( "edges","latent_nodes"),{"edges":{"type":"array","minItems":1,"maxItems":512,"items":{"type":"object"}},"latent_nodes":{"type":"array","minItems":1,"maxItems":128,"items":{"type":"string"}},"observed_nodes":{"type":"array","items":{"type":"string"},"maxItems":128}}),
    _tool("athena_causal_tmle_ensemble","Binary-treatment/binary-outcome TMLE with deterministic cross-fitted validation-weighted linear/quadratic logistic nuisance ensemble. Assumption-scoped.",( "samples","treatment","outcome"),{"samples":{"type":"array","minItems":60,"maxItems":20000,"items":{"type":"object"}},"treatment":STR,"outcome":STR,"adjustment":{"type":"array","items":{"type":"string"},"maxItems":16},"assumptions":OBJ,"propensity_clip":NUM}),
    _tool("athena_sensitivity_rr_surface","Compute a two-dimensional risk-ratio bias-factor sensitivity surface across declared exposure-confounder and confounder-outcome strengths.",( "observed_rr","exposure_confounder_rrs","outcome_confounder_rrs"),{"observed_rr":NUM,"exposure_confounder_rrs":{"type":"array","minItems":1,"maxItems":50,"items":NUM},"outcome_confounder_rrs":{"type":"array","minItems":1,"maxItems":50,"items":NUM}}),
    _tool("athena_bapomdp_solve","Exactly solve a bounded finite-horizon POMDP with a static uncertain model index when the full joint model-state tree completes. PLAN_ONLY.",( "states","initial_state_belief","models"),{"states":{"type":"array","minItems":1,"maxItems":6,"items":{"type":"string"}},"initial_state_belief":OBJ,"models":{"type":"array","minItems":1,"maxItems":4,"items":{"type":"object"}},"horizon":{"type":"integer","minimum":1,"maximum":3},"discount":NUM,"max_nodes":{"type":"integer","minimum":100,"maximum":300000}}),
    _tool("athena_evidence_dependence_interval","Return a Laplace/Hessian logit interval around a fitted V10 evidence-dependence probability. Model-conditional diagnostic.",( "scope","features"),{"scope":STR,"features":OBJ,"confidence_z":NUM,"l2":NUM}),
]

from .collective_v12_protocol import COLLECTIVE_V12_TOOLS
COLLECTIVE_V11_TOOLS.extend(t for t in COLLECTIVE_V12_TOOLS if t['name'] not in {x['name'] for x in COLLECTIVE_V11_TOOLS})
