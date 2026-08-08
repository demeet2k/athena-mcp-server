from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {"name":name,"description":description,"inputSchema":{"type":"object","required":list(required),"properties":properties or {},"additionalProperties":False}}

STR={"type":"string"}; NUM={"type":"number"}; OBJ={"type":"object"}; BOOL={"type":"boolean"}; INT={"type":"integer"}

COLLECTIVE_V7_TOOLS=[
    _tool("athena_uncertainty_decompose","Return a model-conditional proxy decomposition into aleatoric, parameter-epistemic, distribution-shift and calibration-error components. Diagnostic only.",( "features","regime","arm_id"),{
        "features":OBJ,"regime":STR,"arm_id":STR,"scope":STR,"target_coverage":NUM,"ridge":NUM,"ood_gain":NUM}),
    _tool("athena_prequential_interval","Build an empirical prequential residual band from retained pre-update V5 observations and inflate it under current OOD pressure. Not a distribution-free conformal guarantee.",( "features","regime","arm_id"),{
        "features":OBJ,"regime":STR,"arm_id":STR,"scope":STR,"coverage":NUM,"min_scores":{"type":"integer","minimum":1,"maximum":10000},"ood_gain":NUM}),
    _tool("athena_causal_skeleton_discover","Generate a heuristic observational association skeleton and candidate v-structures using marginal/one-variable partial-correlation thresholds. Hypothesis generation only.",( "samples",),{
        "samples":{"type":"array","minItems":5,"maxItems":5000,"items":{"type":"object"}},"variables":{"type":"array","items":{"type":"string"},"maxItems":16},"association_threshold":NUM,"max_conditioning":{"type":"integer","minimum":0,"maximum":1}}),
    _tool("athena_state_transition_model","Fit a ridge state-dependent multivariate transition-delta regression from observed before/after action rows and expose predictive covariance plus parameter-information leverage.",( "action_id","context"),{
        "action_id":STR,"context":OBJ,"ridge":NUM,"max_features":{"type":"integer","minimum":1,"maximum":12}}),
    _tool("athena_scenario_evaluate","Evaluate caller-supplied finite action sequences on bounded three-branch moment scenario trees with expected return and lower-tail CVaR. SIMULATE_ONLY.",( "initial_context","actions","trajectories"),{
        "initial_context":OBJ,"actions":{"type":"array","minItems":1,"maxItems":64,"items":{"type":"object"}},"trajectories":{"type":"array","minItems":1,"maxItems":128,"items":{"type":"object"}},"discount":NUM,"scenario_sigma":NUM,"cvar_alpha":NUM,"risk_aversion":NUM,"ridge":NUM}),
    _tool("athena_dual_control_plan","Bounded proxy dual-control planner combining control reward, transition-parameter information value and predictive risk. PLAN_ONLY; execute first action then observe/replan.",( "initial_context","actions"),{
        "initial_context":OBJ,"actions":{"type":"array","minItems":1,"maxItems":64,"items":{"type":"object"}},"horizon":{"type":"integer","minimum":1,"maximum":5},"beam_width":{"type":"integer","minimum":1,"maximum":512},"discount":NUM,"risk_aversion":NUM,"information_weight":NUM,"ridge":NUM}),
    _tool("athena_causal_identify_extended","Perform supplied-DAG conditional identification for BACKDOOR, FRONTDOOR or INSTRUMENT criteria. Results are conditional on graph/observed-node/assumption correctness.",( "method","treatment","outcome","edges"),{
        "method":STR,"treatment":STR,"outcome":STR,"edges":{"type":"array","maxItems":256,"items":{}},"observed_nodes":{"type":"array","items":{"type":"string"}},"mediators":{"type":"array","items":{"type":"string"}},"instruments":{"type":"array","items":{"type":"string"}},"assumptions":OBJ,"max_adjustment_size":{"type":"integer","minimum":0,"maximum":8},"actor":STR}),
    _tool("athena_replication_independence","Estimate effective evidential replication/falsification diversity from witness confidence, independence keys and declared dataset/implementation/method/operator/environment/seed metadata.",( "claim_id",),{
        "claim_id":STR,"dimensions":{"type":"array","items":{"type":"string"},"maxItems":16},"min_confidence":NUM}),
    _tool("athena_replication_design","Rank proposed REPLICATION or FALSIFIER designs by expected power, metadata novelty, feasibility, cost and risk. DESIGN_ONLY.",( "claim_id","candidates"),{
        "claim_id":STR,"candidates":{"type":"array","minItems":1,"maxItems":512,"items":{"type":"object"}},"mode":STR,"dimensions":{"type":"array","items":{"type":"string"},"maxItems":16},"cost_weight":NUM,"risk_weight":NUM}),
]
