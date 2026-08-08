# ATHENA COLLECTIVE RUNTIME V11 — ADAPTIVE PROBABILISTIC CAUSAL CONTROL

V11 extends V10 with stronger adaptive—but still explicitly bounded—probabilistic, causal and belief-control surfaces.

## Constitutional boundaries

`MARGINAL_LIKELIHOOD_OPTIMUM != TRUE_KERNEL`

`GP_DECISION_EVSI != OBSERVATION`

`SUPPLIED_DAG_LATENT_PROJECTION != DATA_DISCOVERED_PAG`

`STACKED_TMLE != SUPER_LEARNER_THEOREM`

`RR_BIAS_FACTOR_SURFACE != UNIVERSAL_HIDDEN_CONFOUNDING_BOUND`

`FINITE_MODEL_BAPOMDP != GENERAL_BAYES_ADAPTIVE_POMDP`

`LAPLACE_DEPENDENCE_INTERVAL != CALIBRATED_COVERAGE_GUARANTEE`

All model/design/projection/policy/interval outputs remain non-authoritative until explicit observed/witnessed transport into evidence/authority surfaces.

## 1. GP hyperparameter adaptation

`athena_gp_hyperfit` searches caller-declared finite grids of RBF length-scale, signal variance and noise variance using exact small-data log marginal likelihood under the existing GP dataset.

`apply=false` is design-only. `apply=true` is permitted only when `expected_observation_count` matches the live GP dataset, preventing stale hyperparameter writes.

## 2. GP decision EVSI

`athena_gp_decision_evsi` values hypothetical GP measurements for a finite caller-declared action/experiment set. It is Monte-Carlo design state and never appends GP observations.

## 3. Supplied-DAG latent projection

`athena_latent_project_admg` accepts an explicit acyclic DAG with caller-declared latent and observed nodes and computes a restricted latent-projection ADMG over the observed set. It is projection under supplied structure, not data-discovered PAG/FCI output, and it writes no canonical JSPACE edge.

## 4. Ensemble binary TMLE

`athena_causal_tmle_ensemble` preserves the V10 binary treatment/outcome scope and identification assumptions while using a bounded validation-weighted nuisance ensemble. Explicit latent-confounding risk fails closed. Ensemble weighting is not a super-learner oracle theorem.

## 5. RR sensitivity surface

`athena_sensitivity_rr_surface` evaluates a caller-declared two-dimensional risk-ratio bias-factor surface. It is a sensitivity geometry, not a universal theorem about hidden confounding.

## 6. Finite-model Bayes-adaptive POMDP

`athena_bapomdp_solve` performs exhaustive finite-horizon planning over a supplied finite static model set, state set, action models and observations. Exact certification is returned only when bounded search completes; node truncation removes certification. The policy is PLAN_ONLY.

## 7. Evidence-dependence intervals

`athena_evidence_dependence_interval` computes a Laplace/Hessian model-conditional probability interval around the externally labelled V10 dependence model. Interval reads never create labels, and nominal interval width is not a calibrated coverage guarantee.

## V11 residual boundary

V11 does not claim general kernel learning, sparse/scalable GP inference, learned latent causal discovery, universal hidden-confounder control, general Bayes-adaptive POMDP solution, or calibrated evidence-dependence coverage guarantees. These remain successor work.
