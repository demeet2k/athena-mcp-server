# ATHENA COLLECTIVE RUNTIME V14 — JOINT POSTERIOR SCIENTIFIC CONTROL

Coordinate:

`COLLECTIVE_SYNTHESIS=<JB,SE,JE,DR,RP,AZ,MR,L>`

V14 is a bounded synthesis layer above `COLLECTIVE_ROBUST_V13`. It joins uncertainty surfaces that previously existed separately while preserving their type boundaries.

## JB — finite joint factor belief

`athena_joint_factor_belief` builds an exact bounded Cartesian product over 2–5 caller-declared axes. Axis priors/weights are normalized, compatibility multipliers may reweight compatible assignments, and an optional complete likelihood map may update every joint state.

For assignment `s=(s_1,...,s_k)`:

`w(s) ∝ [Π_j p_j(s_j)] c(s) L(s)`.

The runtime returns normalized state weights, entropy, effective state count, and axis marginals.

`FINITE_FACTOR_PRODUCT_BELIEF != FULL_JOINT_POSTERIOR`.

The product is a science-twin belief over explicitly supplied finite axes; it is not world truth, Y1 authority, or an arbitrary continuous posterior.

## SE — bootstrap structural ensemble

`athena_structural_bootstrap_ensemble` resamples observed rows and repeatedly executes the bounded V13 FCI-lite surface. It returns graph-variant frequencies and marked-edge support.

`support(g)=count_bootstrap_runs(g)/valid_runs`.

`BOOTSTRAP_GRAPH_FREQUENCY != CAUSAL_POSTERIOR`.

Bootstrap support is procedural stability under row resampling. It is not calibrated Bayesian probability of a causal graph and never mutates canonical JSPACE.

## JE — joint science EVI

`athena_joint_science_evi` consumes explicit weighted finite joint states, complete action utility tables, and experiment outcome likelihoods. For experiment `e`:

`EVI(e)=E_y[max_a E[U(a,S)|y,e]]-max_a E[U(a,S)]`.

It separately returns entropy reduction:

`IG(e)=H(S)-E_y[H(S|y,e)]`.

Decision value and information value remain distinct before visible weighting by feasibility/cost/risk.

`JOINT_SCIENCE_EVI != OBSERVATION_OR_EVIDENCE`.

Hypothetical outcomes and posteriors remain DESIGN_ONLY.

## DR — sequential doubly robust two-timepoint policy value

`athena_sequential_dr_policy_value` supports binary `X -> A1 -> L1 -> A2 -> Y` histories and caller-supplied deterministic policies.

It fits `g1`, `g2`, `Q2`, builds a policy pseudo-outcome `Q2π2` while preserving each row's observed `A1/L1`, fits `Q1`, and evaluates a two-stage AIPW score:

`ψ_i(π)=Q1π(X_i)+H1_i[Q2π(H1_i)-Q1obs(H0_i,A1_i)]+H2_i[Y_i-Q2obs(H2_i,A2_i)]`.

The returned estimate is `mean_i ψ_i(π)` with an empirical standard error and 95% interval.

`STAGE2_POLICY_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_POLICY_EVALUATION`.

The implementation declares `cross_fitted=false`.

`SEQUENTIAL_DR_POLICY_VALUE != GENERAL_LONGITUDINAL_CAUSAL_VALUE_THEOREM`.

Declared latent confounding fails closed. Policy value is not treatment authorization.

## RP — robust policy geometry

`athena_joint_policy_robust` evaluates complete policy utility tables over finite weighted joint states. It retains expected utility, worst-case utility, lower-tail CVaR, expected regret, max regret, cost, and a Pareto frontier before returning a visible scalar ranking.

`FINITE_SCENARIO_ROBUST_POLICY != GENERAL_ROBUST_CONTROL`.

The result is PLAN_ONLY.

## AZ — decision-relative approximation / zoom routing

`athena_gp_resolution_route` compares FITC approximations against the exact current bounded GP on the supplied action/query set. It chooses the shallowest tested FITC representation only when:

1. its winner equals the exact-GP winner; and
2. maximum witnessed utility error is at most `margin_safety * exact_decision_margin`.

Otherwise it returns FULL_GP.

This gives a concrete adaptive zoom law:

`cheapest representation subject to witnessed decision preservation`.

`QUERY_SET_DECISION_PRESERVATION != GLOBAL_APPROXIMATION_CERTIFICATE`.

The certificate does not generalize to unqueried states/actions.

## MR — finite two-stage scenario recourse

`athena_two_stage_resource_plan` chooses a first-stage subset, then chooses the best feasible one-option recourse inside each caller-declared scenario.

For first-stage plan `x` and scenario `ω`:

`V(x,ω)=V0(x)+max_{r feasible under residual budget(x,ω)} V_r`.

The visible objective is expected value with an optional expected-to-worst downside penalty.

Below the first-stage enumeration threshold, V14 exhaustively enumerates all subsets and returns:

`EXACT_ENUMERATION_FOR_SUPPLIED_FINITE_TWO_STAGE_SCENARIO_MODEL`.

Above the threshold it returns a deterministic greedy plan with no exact certificate.

`FINITE_TWO_STAGE_SCENARIO_RECOURSE != GENERAL_MULTISTAGE_STOCHASTIC_PROGRAM`.

## Authority / mutation boundary

The following transitions are forbidden without separate witnessed authority:

`joint belief -> Y1 claim state`

`bootstrap graph frequency -> JSPACE causal edge`

`EVI hypothetical branch -> observation/evidence`

`sequential DR policy value -> treatment execution`

`robust policy plan -> execution history`

`FITC decision-preservation witness -> global model-fidelity theorem`

`two-stage recourse plan -> resource expenditure`.

Host-bound trusted promotion remains `GITHUB_PROMOTION_VERIFIER.1`; V14 does not expose repository, run, token, trusted app, required-check, or verifier-receipt fields to an MCP caller.

## Successor boundary

V14 does not claim a calibrated full joint posterior across model/graph/effect/state, a Bayesian structural posterior, complete FCI/RFCI, cross-fitted arbitrary-horizon TMLE, general sequential doubly robust off-policy evaluation, continuous-state Bayes-adaptive control, global approximation-error transport, or general multistage stochastic/DRO optimization.
