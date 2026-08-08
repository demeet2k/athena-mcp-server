# ATHENA COLLECTIVE RUNTIME V7 — DUAL CONTROL + CONDITIONAL CAUSAL DISCOVERY

V7 extends V6 active discovery/stochastic control with a stronger distinction between uncertainty sources, empirical prequential coverage evidence, state-dependent transition dynamics, finite scenario-risk evaluation, a bounded control-plus-information planner, additional supplied-DAG identification criteria, observational causal-skeleton hypothesis generation, and replication-independence geometry.

The design objective is not to maximize the number of models. It is to make **the next intervention simultaneously useful for control and useful for learning whenever the task actually warrants that depth**.

## 0. Constitutional boundaries

`UNCERTAINTY_DECOMPOSITION != UNIQUE_PHYSICAL_DECOMPOSITION`

`PREQUENTIAL_EMPIRICAL_INTERVAL != DISTRIBUTION_FREE_CONFORMAL_GUARANTEE UNDER ARBITRARY SHIFT`

`ASSOCIATION_SKELETON != CAUSAL_DAG`

`V_STRUCTURE_CANDIDATE != ORIENTED_CAUSAL_TRUTH`

`STATE_DEPENDENT_TRANSITION_MODEL != WORLD_TRUTH`

`SCENARIO_TREE != OBSERVED_FUTURE`

`DUAL_CONTROL_PROXY != EXACT_BELIEF_STATE_OPTIMAL_CONTROL`

`FRONTDOOR_OR_IV_IDENTIFICATION != CAUSAL_TRUTH OUTSIDE SUPPLIED DAG/ASSUMPTIONS`

`ESTIMATED_REPLICATION_INDEPENDENCE != FORMAL_STATISTICAL_INDEPENDENCE`

`REPLICATION_DESIGN != REPLICATION_RESULT`.

All V1–V6 semantic/Git/topology/policy/projection authority surfaces remain unchanged.

---

## 1. ΩUNCERTAINTY-DECOMPOSITION

V7 exposes a model-conditional diagnostic decomposition of the V6 nonlinear Bayesian prediction into four explicitly named proxies:

- aleatoric/noise proxy;
- parameter-epistemic proxy;
- distribution-shift proxy;
- retained calibration-error proxy.

For V5/V6 ridge state `A`, query basis `phi`, and residual noise estimate `sigma_n^2`, posterior leverage is

`h(phi) = phi^T A^-1 phi`.

The diagnostic components are approximately

`u_alea = sigma_n`,

`u_epi = sigma_n sqrt(h(phi))`,

`u_shift = sigma_base * lambda_OOD * OOD(x)`,

plus empirical calibration error from retained pre-update predictions.

The returned quadrature total is useful for routing and experiment pressure. It is not claimed to uniquely identify physical randomness, model misspecification, or epistemic uncertainty.

Tool:

- `athena_uncertainty_decompose`.

---

## 2. ΩPREQUENTIAL-INTERVAL

V5 already retains the prediction made **before** each observed reward. V7 reuses the corresponding absolute errors as prequential nonconformity scores.

For target coverage `q`, sorted residual scores `r_(1) <= ... <= r_(n)` produce a finite empirical quantile using

`k = ceil((n+1)q)`

clamped to the observed score range.

The current mean is wrapped by that empirical half-width and widened under V6 OOD pressure.

If too few retained scores exist the operation returns

`INSUFFICIENT_PREQUENTIAL_SCORES`

and falls back to the existing Bayesian/OOD interval without manufacturing a conformal-style claim.

Because these scores are sequential/prequential rather than a guaranteed exchangeable split-conformal sample, V7 deliberately calls the result

`EMPIRICAL_PREQUENTIAL_BAND`.

Tool:

- `athena_prequential_interval`.

---

## 3. ΩCAUSAL-SKELETON — observational hypothesis generation

V7 adds a bounded observational graph-hypothesis surface. It does **not** call the result a causal DAG.

For up to sixteen numeric variables, it computes:

1. marginal Pearson correlations;
2. a caller-declared absolute association threshold;
3. optional one-variable partial-correlation screening;
4. an undirected surviving association skeleton;
5. separation-set metadata;
6. collider/v-structure candidates of the form `X - Z - Y` when `X` and `Y` are nonadjacent and `Z` was not the recorded separator.

For one conditioning variable `Z`, partial correlation is

`r_xy.z = (r_xy - r_xz r_yz) / sqrt((1-r_xz^2)(1-r_yz^2))`.

This is deliberately a small transparent hypothesis generator rather than a p-value-calibrated full PC/FCI implementation.

Returned status:

`HEURISTIC_ASSOCIATION_SKELETON`.

Tool:

- `athena_causal_skeleton_discover`.

---

## 4. ΩSTATE-MODEL — state-dependent stochastic transitions

V6 action-conditioned transition moments do not depend on current state. V7 fits a bounded ridge regression from the retained V5 before/after transition rows.

For action `a`, before-state feature vector `x`, and delta outcome `Delta`, V7 fits

`Delta = B phi(x) + epsilon`

with `phi(x)=[1,x_1,...,x_p]` and ridge precision

`A = lambda I + sum w phi phi^T`.

For every output state coordinate `y`:

`beta_y = A^-1 b_y`.

Current predicted delta:

`Delta_hat_y(x) = phi(x)^T beta_y`.

Residual covariance is estimated across the multivariate fitted delta residuals. Predictive diagonal uncertainty is then increased by posterior leverage at the query state.

The operation also exposes a model-conditional parameter-information proxy

`IG_param ~= 0.5 * d_out * log(1 + h(phi))`.

This is the information surface used by the V7 dual-control proxy.

Unseen actions remain

`UNSEEN_ACTION`

with empty learned deltas.

Tool:

- `athena_state_transition_model`.

---

## 5. ΩSCENARIO — bounded moment scenario trees

V7 can evaluate caller-supplied finite action sequences using a bounded three-branch moment approximation to the state-transition covariance.

For each action/state pair, the dominant covariance eigenpair `(lambda_1,v_1)` is approximated by power iteration. The next-state moment surface is represented by branches

`mean - sigma sqrt(lambda_1) v_1`,

`mean`,

`mean + sigma sqrt(lambda_1) v_1`

with default probabilities `.25/.5/.25` when modeled uncertainty is nonzero.

The resulting fixed-sequence tree returns:

- expected discounted return;
- lower-tail CVaR return;
- risk-adjusted score;
- scenario count/truncation status.

It evaluates a declared trajectory; it does not solve a general contingent-policy tree.

Tool:

- `athena_scenario_evaluate`.

`SCENARIO_TREE != OBSERVED_FUTURE`.

---

## 6. ΩDUAL-CONTROL — control value + information value

V6 MPC optimizes control reward minus predictive uncertainty. V7 adds an explicit information term from state-model parameter leverage.

For action `a` at state `x`:

`step_value(a,x) = control_reward(a,x) + lambda_I * information_value(a,x) - lambda_R * predictive_risk(a,x)`.

A bounded beam search accumulates this score over a short horizon.

For unseen actions, information/risk are explicit priors rather than fabricated transition observations.

The returned decision is

`DUAL_CONTROL_PROXY_PLAN_ONLY`.

The intended execution law remains

`PLAN -> EXECUTE_FIRST_AUTHORIZED_ACTION -> OBSERVE_REAL_NEXT_STATE -> RECORD -> REPLAN`.

No call to the planner writes transition observations or learning reward.

Tool:

- `athena_dual_control_plan`.

This is a tractable dual-control **proxy**, not an exact Bayes-adaptive POMDP/belief-state solution.

---

## 7. ΩCAUSAL-ALGEBRA — back-door + front-door + instrument

V7 preserves V6 back-door identification and adds two supplied-DAG checks.

### FRONTDOOR

For declared mediator set `M`, V7 checks under the supplied DAG:

1. removing all mediators blocks every directed `T -> Y` path;
2. every mediator is on a directed `T -> M -> Y` chain;
3. there is no unblocked treatment→mediator back-door path;
4. conditioning on treatment blocks every mediator→outcome back-door path;
5. mediators are declared observed.

Passing status:

`IDENTIFIED_FRONTDOOR_UNDER_DAG`.

### INSTRUMENT

For candidate `Z`, V7 checks:

1. directed relevance `Z -> ... -> T`;
2. after treatment outgoing causal paths are removed, `Z` is d-separated from `Y` under the supplied graph, jointly representing the runtime's bounded exclusion/exogeneity check;
3. `Z` is observed and not a treatment descendant.

Passing candidates are returned under

`IDENTIFIED_INSTRUMENT_UNDER_DAG`.

Explicit latent-confounding risk fails closed for the extended methods.

Tool:

- `athena_causal_identify_extended`.

These checks establish identification **conditional on the supplied DAG and assumptions**; they do not establish that the supplied DAG is the true causal data-generating graph.

---

## 8. ΩREPLICATION-INDEPENDENCE

V6 uses explicit independence keys so repeated runs are not automatically counted as distinct evidence groups. V7 adds a second diagnostic surface using evidence metadata dimensions such as:

- dataset;
- implementation;
- method;
- operator;
- environment;
- seed family.

For witness pair `(i,j)`, similarity is the fraction of shared known dimensions that match. Identical independence keys force similarity `1`. If no comparable metadata exists, similarity defaults conservatively to `.5` rather than assuming independence.

Using witness confidence weights `w_i`, V7 reports an effective diversity count

`N_eff = (sum_i w_i)^2 / sum_ij w_i w_j s_ij`.

Identical replications therefore collapse toward effective `N=1`; genuinely diverse metadata can raise effective `N` toward the raw witness count.

Tool:

- `athena_replication_independence`.

`ESTIMATED_REPLICATION_INDEPENDENCE != FORMAL_STATISTICAL_INDEPENDENCE`.

---

## 9. ΩREPLICATION-DESIGN

V7 can rank proposed replication or falsifier designs before they are executed.

For candidate `e`, metadata novelty is conservatively measured against existing witness evidence. Candidate score combines:

`expected_power * diversity_factor * feasibility - cost_weight*cost - risk_weight*risk`.

Modes:

- `REPLICATION`;
- `FALSIFIER`.

Output is always

`DESIGN_ONLY`.

Tool:

- `athena_replication_design`.

The selected design is not a result, witness, or canonical fact until executed and measured.

---

## 10. Ω7 coordinate fiber

A materially governing V7 run may expose

`COLLECTIVE_DUAL_CONTROL=<UD,PI,CG,SM,SC,DC,CX,RI,RD,L>`

where:

- `UD`: uncertainty-decomposition diagnostic;
- `PI`: prequential empirical interval state;
- `CG`: observational causal-skeleton hypothesis state;
- `SM`: state-dependent transition model;
- `SC`: scenario/CVaR evaluation;
- `DC`: dual-control proxy plan;
- `CX`: extended conditional causal-identification state;
- `RI`: replication-independence geometry;
- `RD`: replication/falsifier design surface;
- `L`: lineage/native context.

This coordinate is additive to all V1–V6 fibers.

---

## 11. V8 residual boundary — not claimed by V7

1. genuine GP/neural posterior inference;
2. distribution-free coverage guarantees under arbitrary distribution shift;
3. statistically calibrated PC/FCI/GES/NOTEARS-style causal structure discovery;
4. hidden-confounder-aware FCI/PAG semantics;
5. front-door/IV effect estimation rather than identification checks only;
6. regression discontinuity, difference-in-differences, synthetic-control and broader design-specific estimators;
7. exact Bayesian dual control / Bayes-adaptive POMDP solution;
8. fully nonlinear state-dependent probabilistic world models;
9. general contingent scenario-policy optimization;
10. large globally certified MILP/CP-SAT resource scheduling;
11. microVM/VM attested hostile-code execution;
12. formal statistical estimation of replication dependence rather than metadata similarity;
13. continuous-space multiobjective Bayesian optimization;
14. host-level resource telemetry that the runtime cannot observe directly.

These remain successor work rather than being relabeled complete by adjacency.
