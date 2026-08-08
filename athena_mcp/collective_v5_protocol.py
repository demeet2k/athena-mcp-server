from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {"name":name,"description":description,"inputSchema":{"type":"object","required":list(required),"properties":properties or {},"additionalProperties":False}}

STR={"type":"string"}; NUM={"type":"number"}; OBJ={"type":"object"}; BOOL={"type":"boolean"}; INT={"type":"integer"}

COLLECTIVE_V5_TOOLS=[
    _tool("athena_bayes_predict","Full-covariance Bayesian contextual prediction with empirical interval calibration. Posterior/intervals remain model-conditional.",( "features","regime","arm_id"),{"features":OBJ,"regime":STR,"arm_id":STR,"scope":STR,"target_coverage":NUM,"ridge":NUM}),
    _tool("athena_bayes_observe","Update full-covariance Bayesian contextual state from one explicit observed reward; retains pre-update prediction for calibration.",( "features","reward","regime","arm_id"),{"features":OBJ,"reward":NUM,"regime":STR,"arm_id":STR,"scope":STR,"actor":STR,"weight":NUM,"target_coverage":NUM,"ridge":NUM}),
    _tool("athena_uncertainty_calibrate","Return empirical coverage/error/width and a reliability-shrunk sigma correction for Bayesian intervals.",(),{"scope":STR,"regime":STR,"arm_id":STR,"target_coverage":NUM}),
    _tool("athena_experiment_design","Rank binary-outcome experiments by expected information gain under supplied hypothesis priors/likelihoods, cost, risk, feasibility and ethics; returns DESIGN_ONLY.",( "hypotheses","experiments"),{"hypotheses":{"type":"array","minItems":2,"maxItems":64,"items":{"type":"object"}},"experiments":{"type":"array","minItems":1,"maxItems":128,"items":{"type":"object"}},"sample_size":{"type":"integer","minimum":2,"maximum":100000},"control_fraction":NUM,"cost_weight":NUM,"risk_weight":NUM}),
    _tool("athena_interaction_credit","Estimate main and pairwise interaction contrasts from supplied intervention/outcome observations. Missing 2x2 cells remain UNIDENTIFIED.",( "analysis_key","experiments"),{"analysis_key":STR,"experiments":{"type":"array","minItems":2,"maxItems":1000,"items":{"type":"object"}},"actor":STR}),
    _tool("athena_delayed_credit_record","Persist one confidence-weighted delayed action credit with explicit temporal discount; delay alone is not causation.",( "action_id","outcome_key","outcome_delta","delay_cycles","causal_confidence"),{"action_id":STR,"outcome_key":STR,"outcome_delta":NUM,"delay_cycles":{"type":"integer","minimum":0,"maximum":100000},"causal_confidence":NUM,"discount":NUM,"regime":STR,"actor":STR}),
    _tool("athena_delayed_credit_summary","Summarize delayed confidence-weighted credit by action.",(),{"action_id":STR,"regime":STR,"limit":{"type":"integer","minimum":1,"maximum":5000}}),
    _tool("athena_transition_observe","Record one observed context transition for an organizational action and update shrinkage transition statistics.",( "action_id","before","after"),{"action_id":STR,"before":OBJ,"after":OBJ,"evidence_weight":NUM,"actor":STR}),
    _tool("athena_transition_predict","Predict context deltas/uncertainty from observed action transitions. Missing features are not synthesized.",( "action_id","context"),{"action_id":STR,"context":OBJ,"prior_strength":NUM}),
    _tool("athena_rollout_learned","Simulate multi-step trajectories through the learned transition model with uncertainty-banded discounted return. Always SIMULATE_ONLY.",( "initial_context","trajectories"),{"initial_context":OBJ,"trajectories":{"type":"array","minItems":1,"maxItems":64,"items":{"type":"object"}},"discount":NUM,"uncertainty_alpha":NUM,"prior_strength":NUM}),
    _tool("athena_schedule_multiperiod","Bounded beam-search finite-horizon scheduler over task dependencies, worker capacity and observable resource budgets; does not claim global optimality.",( "tasks","workers"),{"tasks":{"type":"array","minItems":1,"maxItems":14,"items":{"type":"object"}},"workers":{"type":"array","minItems":1,"maxItems":32,"items":{"type":"object"}},"horizon":{"type":"integer","minimum":1,"maximum":100},"budget":OBJ,"beam_width":{"type":"integer","minimum":1,"maximum":1024},"scope":STR,"discount":NUM}),
    _tool("athena_witness_cell","Execute one repository-owned unittest witness with isolated Python mode, sanitized environment, timeout, network-socket monkeypatch and POSIX resource caps when available. Not claimed OS-hermetic.",( "regression_ref",),{"regression_ref":STR,"timeout_s":NUM,"memory_mb":{"type":"integer","minimum":64,"maximum":16384},"cpu_s":{"type":"integer","minimum":1,"maximum":60},"actor":STR}),
    _tool("athena_regime_geometry_observe","Update a learned task-regime centroid from observable signals and measured reward. Learned geometry is routing context, not semantic identity.",( "signals","reward"),{"signals":OBJ,"reward":NUM,"cluster_id":STR,"domain":STR,"weight":NUM}),
    _tool("athena_regime_geometry_resolve","Return nearest evidence-weighted learned regime centroids plus the coarse V4 regime.",( "signals",),{"signals":OBJ,"top_k":{"type":"integer","minimum":1,"maximum":50},"domain":STR}),
    _tool("athena_pareto_frontier","Compute the exact non-dominated frontier for the supplied candidate set, optionally using interval-robust dominance and min/max metric directions.",( "candidates",),{"candidates":{"type":"array","minItems":1,"maxItems":1000,"items":{"type":"object"}},"directions":OBJ,"epsilon":NUM,"robust":BOOL}),
    _tool("athena_projection_compensate","Apply the explicit semantic inverse for active JSPACE edges created by one topology projection, under semantic-head CAS. Git compensation remains separately surfaced.",( "projection_id","expected_semantic_eid"),{"projection_id":STR,"expected_semantic_eid":{"type":["string","null"]},"actor":STR}),
]

# V6 discovery is chained through the V5 registry so the existing V4 compatibility
# surface advertises and routes V5+V6 without another Server inheritance layer.
from .collective_v6_protocol import COLLECTIVE_V6_TOOLS
_existing={tool['name'] for tool in COLLECTIVE_V5_TOOLS}
COLLECTIVE_V5_TOOLS.extend(tool for tool in COLLECTIVE_V6_TOOLS if tool['name'] not in _existing)
