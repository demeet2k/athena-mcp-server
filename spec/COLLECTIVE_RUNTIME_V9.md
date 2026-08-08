# ATHENA COLLECTIVE RUNTIME V9 — CONTINUOUS INFERENCE + ROBUST CAUSAL DECISION VALUE

V9 extends V8 finite belief-state decision intelligence with a tractable continuous parameter posterior, Monte-Carlo value-of-information surfaces, bounded multistage finite-belief policies, cross-fitted AIPW causal estimation, specification-robustness diagnostics, uncertainty-preserving partial graphs and explicit probabilistic evidence-dependence models.

The design objective is to increase inferential resolution while keeping every stronger-sounding term scoped to the exact model actually implemented.

## 0. Constitutional boundaries

`GAUSSIAN_LINEAR_POSTERIOR != GENERAL_CONTINUOUS_BAYES`

`MONTE_CARLO_EVPI_EVSI != EXACT_ANALYTIC_VALUE`

`MULTISTAGE_FINITE_BELIEF_POLICY != GENERAL_POMDP`

`AIPW_ESTIMATE != IDENTIFICATION_PROOF`

`ROBUSTNESS_PERTURBATION != HIDDEN_CONFOUNDING_BOUND`

`HEURISTIC_PARTIAL_GRAPH != FCI_PAG_OR_CPDAG_THEOREM`

`DEPENDENCE_PROBABILITY_MODEL != FORMAL_EVIDENCE_INDEPENDENCE`.

All V1–V8 semantic/Git/topology/policy/projection authority surfaces remain unchanged.

## 1. ΩGAUSSIAN-BELIEF — continuous finite-dimensional parameter state

For parameter vector `theta in R^d`, V9 stores a Gaussian linear posterior in natural coordinates:

`p(theta|D) = N(mu, Sigma)`

with precision

`A = Sigma^-1`

and natural vector

`b = A mu`.

An explicit linear observation

`y = x^T theta + epsilon`, `epsilon ~ N(0,sigma^2)`

updates

`A' = A + w xx^T/sigma^2`

and

`b' = b + w xy/sigma^2`.

Then

`Sigma' = A'^-1`, `mu' = Sigma' b'`.

Tools:

- `athena_gaussian_belief_register`
- `athena_gaussian_belief_state`
- `athena_gaussian_belief_observe`.

Feature values are required for every declared parameter. Predictions/design calls never update this state.

This is a finite-dimensional Bayesian linear model, not a GP, neural posterior or arbitrary continuous model family.

## 2. ΩEVPI — value ceiling under continuous belief

For action utility

`U(a,theta)=c_a + q_a^T theta`,

current decision value is

`V0 = max_a U(a,E[theta])`.

V9 estimates perfect-information value by posterior Monte Carlo:

`V_PI ~= (1/N) sum_n max_a U(a,theta_n)`,

`theta_n ~ N(mu,Sigma)`.

Then

`EVPI ~= max(0,V_PI-V0)`.

Tool:

- `athena_decision_evpi`.

The output includes Monte-Carlo standard error and seed. It is a model-conditional numerical estimate, not a universal value-of-truth theorem.

## 3. ΩEVSI — sample information value

For experiment design vector `x_e` and noise variance `sigma_e^2`, V9 simulates posterior predictive measurements and hypothetical posterior updates. For each simulated observation it recomputes the optimal downstream action.

`EVSI(e) ~= E_y[max_a EU(a|y,e)] - max_a EU(a)`.

The result is cost/risk/feasibility adjusted and remains `DESIGN_ONLY`.

Tool:

- `athena_decision_evsi`.

`EVSI <= EVPI` is the intended conceptual ceiling under the same decision/model assumptions; Monte-Carlo error means numerical estimates should be interpreted with their returned sampling error.

## 4. ΩMULTISTAGE-BELIEF — bounded contingent policy recursion

V8 exposed depth-1 finite belief control. V9 performs exact recursion over the caller-declared finite model/outcome surface for horizon `H<=3`.

At each policy node, an action can create observation branches, hypothetical Bayes updates, and a subsequent optimal action subtree.

Tool:

- `athena_belief_policy_multistage`.

Output:

`FINITE_BELIEF_MULTISTAGE_POLICY_PLAN_ONLY`.

No hypothetical branch updates persistent belief or execution history. The operation is bounded finite recursion, not a general POMDP solver or continuous belief-space Bellman engine.

## 5. ΩAIPW — cross-fitted doubly-robust effect estimator

For binary treatment `T`, adjustment covariates `X`, propensity `e(X)=P(T=1|X)` and outcome regressions `m_t(X)`, V9 computes the augmented inverse-probability score

`psi = m1(X)-m0(X) + T(Y-m1(X))/e(X) - (1-T)(Y-m0(X))/(1-e(X))`.

The runtime uses deterministic two-fold cross-fitting, ridge linear outcome nuisance fits and logistic propensity nuisance fits with explicit propensity clipping.

Estimate:

`tau_hat = mean(psi)`.

Influence-function standard error:

`SE ~= sd(psi)/sqrt(n)`.

Tool:

- `athena_causal_aipw`.

The returned interval is a bounded large-sample diagnostic. AIPW's double-robust property remains conditional on causal identification, positivity, consistency and nuisance-model regularity. Declared latent-confounding risk fails closed.

## 6. ΩROBUSTNESS — specification perturbation

V9 computes a transparent leave-one-adjustment-out surface around V8's linear back-door estimate.

For adjustment set `Z`, each member is omitted in turn and the estimate shift is recorded.

Tool:

- `athena_causal_robustness`.

This answers "how sensitive is this fitted estimate to these observed adjustment choices?" It does not provide a formal Rosenbaum bound, E-value or hidden-confounding identification theorem.

## 7. ΩPARTIAL-GRAPH — uncertainty-preserving structural surface

V9 reuses V8 bootstrap association stability and converts stable undirected hypotheses into explicit endpoint uncertainty:

`X o-o Y`.

Tool:

- `athena_structure_partial`.

Stable collider hypotheses remain separate. The result is `HEURISTIC_PARTIAL_GRAPH`; it is not an FCI PAG, CPDAG theorem, causal posterior or canonical JSPACE mutation.

## 8. ΩEVIDENCE-DEPENDENCE — explicit probability model

V8 spectral/effective-N geometry summarizes redundancy. V9 adds a caller-declared logistic metadata model for pairwise witness dependence.

For metadata comparison features `z_ij`,

`P(dep_ij=1|z_ij) = sigmoid(beta_0 + beta^T z_ij)`.

Matching independence keys force dependence probability 1. Missing metadata contributes a caller/configuration-visible conservative term rather than being interpreted as independence.

Tool:

- `athena_evidence_dependence_probability`.

The probabilities are conditional on the declared metadata model. They are not empirically identified formal dependence probabilities unless an external calibration procedure establishes that separately.

## 9. V9 coordinate fiber

A materially governing V9 run may expose

`COLLECTIVE_INFERENCE=<GB,EVPI,EVSI,MP,AIPW,RB,PG,ED,L>`

where:

- `GB`: Gaussian parameter-belief state;
- `EVPI`: perfect-information value estimate;
- `EVSI`: sample-information value estimate;
- `MP`: multistage finite-belief policy;
- `AIPW`: robust causal-effect estimate;
- `RB`: robustness perturbation surface;
- `PG`: partial structural-uncertainty graph;
- `ED`: evidence-dependence model;
- `L`: lineage/native context.

This coordinate is additive to all V1–V8 fibers.

## 10. V10 residual boundary — not claimed by V9

1. genuine Gaussian-process or neural Bayesian posterior world models;
2. nonparametric continuous model spaces;
3. exact recursive Bayes-adaptive POMDP/belief-MDP solution;
4. continuous-observation analytic EVSI/EVPPI with convergence certificates;
5. cross-fitted flexible nuisance ensembles / Super Learner;
6. TMLE and broader semiparametric estimators with formal finite-sample diagnostics;
7. formal hidden-confounding sensitivity bounds;
8. calibrated PC/FCI/GES/NOTEARS discovery and valid PAG/CPDAG semantics;
9. learned/calibrated evidence-dependence probability from independent ground truth;
10. globally certified stochastic scheduling/control under uncertain resource dynamics;
11. microVM/VM attested hostile-code witnesses;
12. distributed semantic/Git transactional commit and policy-authorized Git compensation.

These remain successor work rather than being renamed complete by adjacency.
