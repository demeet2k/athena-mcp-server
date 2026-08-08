# ATHENA COLLECTIVE RUNTIME V8 — FINITE BELIEF STATE + DECISION VALUE

V8 extends V7 dual-control/conditional-causal-discovery with a finite explicit model-belief state, Bayes updates from declared observed likelihood witnesses, decision-theoretic expected value of information, a depth-1 belief-aware controller, assumption-scoped causal effect estimators, bootstrap stability for observational graph hypotheses, depth-1 contingent policies, and spectral evidence-diversity geometry.

The design objective is **to make uncertainty decision-relevant without allowing model belief, design simulations, or estimator output to become canonical truth by adjacency**.

## 0. Constitutional boundaries

`BELIEF_POSTERIOR != CANONICAL_TRUTH`

`LIKELIHOOD_MODEL != OBSERVATION`

`EVI_DESIGN != EXPERIMENT_RESULT`

`BELIEF_DUAL_CONTROL != EXACT_BAYES_ADAPTIVE_POMDP`

`LINEAR_CAUSAL_ESTIMATE != IDENTIFICATION_PROOF`

`BOOTSTRAP_ASSOCIATION_STABILITY != CAUSAL_EDGE_PROBABILITY`

`CONTINGENT_POLICY != EXECUTION_HISTORY`

`SPECTRAL_EVIDENCE_DIVERSITY != FORMAL_STATISTICAL_INDEPENDENCE`.

All V1–V7 semantic/Git/topology/policy/projection authority surfaces remain unchanged.

## 1. ΩBELIEF — finite discrete model state

For context key `c`, V8 stores models `M_i` with normalized probabilities

`p_i >= 0`, `sum_i p_i = 1`.

Register:

- `athena_belief_register`
- `athena_belief_state`.

Given an actual declared observation `y` and caller-supplied likelihood witness `L_i=P(y|M_i)`, V8 applies

`p_i' = p_i L_i / sum_j p_j L_j`.

Update:

- `athena_belief_observe`.

Likelihood must be supplied for every model. Query/design/planning operations never update belief automatically.

Belief entropy is

`H(M)=-sum_i p_i log2 p_i`.

The posterior is model state only; canonical semantic mutation retains its existing authority path.

## 2. ΩEVI — decision-theoretic value of information

An action `a` supplies utility by model `U(a,M_i)`.

Current expected utility is

`EU(a)=sum_i p_i U(a,M_i)`.

Current decision value:

`V0=max_a EU(a)`.

For experiment `e` with finite outcomes `y` and declared `P(y|M_i,e)`, V8 computes every outcome posterior and its optimal downstream action. Expected post-information decision value is

`V(e)=sum_y P(y|e) max_a EU(a|y,e)`.

Expected value of information:

`EVI(e)=max(0,V(e)-V0)`.

Eligibility/ranking may then subtract declared cost/risk and multiply by feasibility. Ethics remains a hard gate.

Tool:

- `athena_decision_evi`.

Result is always `DESIGN_ONLY`.

Unlike entropy-only EIG, EVI values information only to the extent it can improve the supplied downstream decision.

## 3. ΩBELIEF-DUAL — finite one-step belief-aware control

For action `a`, V8 combines:

- immediate expected utility under current belief;
- expected best next decision utility after the action's declared observation model;
- expected entropy reduction/information gain;
- explicit cost and risk.

A bounded depth-1 score is

`Q(a)=EU_now(a)+gamma E[V_next|a]+lambda_I EIG(a)-lambda_R risk(a)-cost(a)`.

Tool:

- `athena_belief_dual_control`.

Output is `BELIEF_DUAL_CONTROL_DEPTH1_PLAN_ONLY`.

It executes nothing, writes no observation, and does not update belief. It is not an exact Bayes-adaptive POMDP or belief-space Bellman solution.

## 4. ΩEFFECT — assumption-scoped effect estimates

Tool:

- `athena_causal_effect_estimate`.

Implemented methods:

### BACKDOOR_LINEAR

For supplied adjustment variables `Z`, fit a ridge-stabilized linear outcome model

`Y = beta_0 + tau T + gamma^T Z + epsilon`.

Returned estimate is `tau`.

### IV_WALD

For instrument `Z`, return the covariance-ratio estimate

`tau_IV = Cov(Z,Y)/Cov(Z,T)`

only when the first-stage association is non-negligible. Weak instruments fail explicitly.

### FRONTDOOR_LINEAR

For mediator `M`, return the linear product-of-coefficients mediation proxy

`tau_FD = alpha_TM * beta_MY|T`.

These estimators are deliberately narrow. They do not replace V6/V7 identification checks, prove graph assumptions, or claim nonparametric front-door/IV identification. Explicit `latent_confounding_possible=true` fails closed.

Every nontrivial estimate is persisted with method, assumptions and witness metadata.

## 5. ΩBOOTSTRAP-GRAPH — stability, not causal probability

Tool:

- `athena_causal_structure_bootstrap`.

V8 repeatedly resamples the supplied observational rows with replacement and invokes the transparent V7 heuristic association-skeleton procedure.

For edge `e`, support is

`support(e)=count_bootstrap_runs_containing_e / B`.

Stable edges above the caller-declared threshold are returned as undirected `o-o` hypotheses. Stable collider candidates are returned separately.

Bootstrap frequency measures stability of the implemented heuristic under resampling. It is not a Bayesian edge posterior, p-value-calibrated PC/FCI result, PAG theorem, or causal truth.

The operation creates no canonical JSPACE edge.

## 6. ΩCONTINGENT — depth-1 policy trees

Tool:

- `athena_contingent_policy`.

For one supplied experiment and current belief, V8 computes for every possible outcome:

1. outcome probability;
2. hypothetical posterior;
3. best action under that posterior.

Returned object is a depth-1 policy tree:

`outcome -> posterior -> best action`.

Status is `CONTINGENT_POLICY_DEPTH1_DESIGN_ONLY`.

No branch becomes an observation or belief update until an outcome is actually observed through the explicit update path.

## 7. ΩEVIDENCE-SPECTRAL — effective diversity

Tool:

- `athena_evidence_spectral`.

Witness metadata dimensions may include dataset, implementation, method, operator, environment and seed family.

Pairwise metadata similarity forms matrix `S`. Reused V7-style weighted effective count is

`N_eff=(sum_i w_i)^2 / sum_ij w_i w_j S_ij`.

V8 additionally exposes the spectral participation-ratio proxy

`D_PR = Tr(S)^2 / ||S||_F^2`.

Identical witness pipelines collapse toward one effective dimension; metadata-diverse evidence can raise effective dimensionality.

When two witnesses share no comparable metadata, similarity defaults conservatively rather than assuming independence.

These quantities are redundancy/diversity diagnostics, not formal statistical independence proofs.

## 8. V8 coordinate fiber

A materially governing V8 run may expose

`COLLECTIVE_BELIEF=<BS,EVI,BD,CE,CB,CP,ER,L>`

where:

- `BS`: finite belief state;
- `EVI`: decision value-of-information surface;
- `BD`: belief-aware dual-control plan;
- `CE`: conditional effect estimate;
- `CB`: bootstrap causal-structure stability;
- `CP`: contingent policy design;
- `ER`: evidence redundancy/effective-rank geometry;
- `L`: lineage/native context.

This coordinate is additive to all V1–V7 fibers.

## 9. V9 residual boundary — not claimed by V8

1. continuous/nonparametric posterior model space;
2. exact Bayes-adaptive POMDP/belief-state dynamic programming;
3. genuine GP/neural Bayesian world models;
4. statistically calibrated PC/FCI/GES/NOTEARS structure discovery and PAG semantics;
5. nonparametric/semiparametric causal estimators with standard-error/robustness suites;
6. doubly robust/AIPW/TMLE estimation;
7. general multi-stage contingent policy trees;
8. exact expected value of sample information over continuous outcome spaces;
9. formal probabilistic replication-dependence estimation;
10. globally certified large-scale scheduling/control under uncertain resource dynamics;
11. microVM/VM attested hostile-code witnesses;
12. distributed semantic/Git transactional commit and automatic Git compensation.

These remain explicit successor work rather than being renamed complete by adjacency.
