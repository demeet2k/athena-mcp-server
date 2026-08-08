from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {"name":name,"description":description,"inputSchema":{"type":"object","required":list(required),"properties":properties or {},"additionalProperties":False}}

STR={"type":"string"}; NUM={"type":"number"}; OBJ={"type":"object"}; BOOL={"type":"boolean"}; INT={"type":"integer"}

COLLECTIVE_V10_TOOLS=[
    _tool("athena_gp_register","Register/reset an exact small-data Gaussian-process regressor with fixed RBF kernel hyperparameters. Model state only.",( "context_key","features"),{"context_key":STR,"features":{"type":"array","minItems":1,"maxItems":12,"items":{"type":"string"}},"length_scale":NUM,"signal_variance":NUM,"noise_variance":NUM,"metadata":OBJ,"replace":BOOL}),
    _tool("athena_gp_state","Read fixed-kernel GP hyperparameters and observed-point count.",( "context_key",),{"context_key":STR}),
    _tool("athena_gp_observe","Append one actual observed target to the bounded fixed-kernel GP dataset.",( "context_key","features","target"),{"context_key":STR,"features":OBJ,"target":NUM,"evidence_ref":STR,"actor":STR}),
    _tool("athena_gp_predict","Return exact fixed-hyperparameter RBF GP posterior mean/variance for one query. Prediction never self-trains.",( "context_key","features"),{"context_key":STR,"features":OBJ,"include_observation_noise":BOOL}),
    _tool("athena_pc_stable_discover","Run bounded Gaussian PC-stable conditional-independence search with Fisher-z tests and limited Meek orientation. Hypothesis graph only.",( "samples",),{"samples":{"type":"array","minItems":12,"maxItems":10000,"items":{"type":"object"}},"variables":{"type":"array","minItems":2,"maxItems":10,"items":{"type":"string"}},"alpha":NUM,"max_conditioning":{"type":"integer","minimum":0,"maximum":3}}),
    _tool("athena_causal_tmle_binary","Cross-fitted binary-treatment/binary-outcome TMLE with logistic nuisance fits, targeting fluctuation and influence-curve interval. Assumption-scoped.",( "samples","treatment","outcome"),{"samples":{"type":"array","minItems":40,"maxItems":20000,"items":{"type":"object"}},"treatment":STR,"outcome":STR,"adjustment":{"type":"array","maxItems":32,"items":{"type":"string"}},"assumptions":OBJ,"propensity_clip":NUM}),
    _tool("athena_sensitivity_evalue","Compute the standard risk-ratio E-value sensitivity metric for a point estimate and optional closest-to-null CI limit.",( "risk_ratio",),{"risk_ratio":NUM,"ci_limit":NUM}),
    _tool("athena_pomdp_solve","Exhaustively solve one small finite-state finite-horizon POMDP tree when node search completes; otherwise return no certificate.",( "states","initial_belief","actions"),{"states":{"type":"array","minItems":1,"maxItems":8,"items":{"type":"string"}},"initial_belief":OBJ,"actions":{"type":"array","minItems":1,"maxItems":8,"items":{"type":"object"}},"horizon":{"type":"integer","minimum":1,"maximum":4},"discount":NUM,"max_nodes":{"type":"integer","minimum":100,"maximum":500000}}),
    _tool("athena_evidence_dependence_observe","Record one externally labelled evidence-dependence example for later empirical calibration.",( "scope","features","label"),{"scope":STR,"features":OBJ,"label":{"type":"integer","minimum":0,"maximum":1},"weight":NUM,"evidence_ref":STR}),
    _tool("athena_evidence_dependence_fit","Fit a scoped logistic evidence-dependence model from explicit labelled examples.",( "scope",),{"scope":STR,"l2":NUM,"iterations":{"type":"integer","minimum":100,"maximum":3000}}),
    _tool("athena_evidence_dependence_predict","Predict pairwise evidence dependence under a previously fitted scoped calibration model.",( "scope","features"),{"scope":STR,"features":OBJ}),
]
