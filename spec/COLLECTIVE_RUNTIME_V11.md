# ATHENA COLLECTIVE RUNTIME V11 — ADAPTIVE WORLD MODEL + LATENT CAUSAL GEOMETRY

V11 extends V10 with model adaptation while preserving the separation between model state, observations, causal assumptions, plans, and canonical semantics.

## Operators

- `athena_gp_hyperfit`
- `athena_gp_decision_evsi`
- `athena_latent_project_admg`
- `athena_causal_tmle_ensemble`
- `athena_sensitivity_rr_surface`
- `athena_bapomdp_solve`
- `athena_evidence_dependence_interval`

Resource: `athena://collective/v11`.

## GP hyperparameter adaptation

For the current V10 RBF GP data, V11 evaluates a finite declared grid of length scale, signal variance, and noise variance. Each candidate is scored by exact Gaussian log marginal likelihood

`log p(y|X,theta) = -1/2 y^T K^-1 y - 1/2 log|K| - n/2 log(2pi)`.

Default result is `GP_HYPERPARAMETER_DESIGN_ONLY`. Applying the winner requires `apply=true` and an exact `expected_observation_count` matching the current GP dataset. Every fit is journaled in `collective_v11_gp_hyperfits`.

`MARGINAL_LIKELIHOOD_OPTIMUM != TRUE_KERNEL`.

## GP decision EVSI

For action latent values and a candidate measurement, V11 uses the conditional Gaussian update

`mu_a' = mu_a + Cov(f_a,f_e)/(Var(f_e)+sigma_e^2) * (y_e-mu_e)`

and Monte Carlo predictive observations to estimate downstream expected improvement in the best action. Ethics, feasibility, cost, and risk remain separate gates. The operation is design-only and never creates GP observations.

`GP_DECISION_EVSI != OBSERVATION`.

## Supplied latent projection

Given a supplied DAG and explicit latent-node set, V11 projects to an observed mixed graph:

- observed directed edge when a directed path has only latent internal nodes;
- observed bidirected edge when an explicit latent node is a common ancestor through latent-only internal paths.

The graph must be acyclic. This is a transform of the supplied causal model, not discovery from observational data, and it never writes JSPACE.

`SUPPLIED_DAG_LATENT_PROJECTION != DATA_DISCOVERED_PAG`.

## Stacked nuisance TMLE

V11 retains binary treatment/outcome TMLE while replacing each single nuisance fit with a transparent validation-weighted library of intercept/treatment-only, linear logistic, and degree-2 polynomial/interaction logistic candidates. Outer cross-fitting remains deterministic; the targeting fluctuation, influence-curve standard error, and interval are retained.

The library is bounded and transparent, not a claim of universal Super Learner optimality. Identification assumptions remain separate and declared latent-confounding risk fails closed.

`STACKED_TMLE != SUPER_LEARNER_THEOREM`.

## Risk-ratio sensitivity surface

For declared `RR_EU>=1` and `RR_UY>=1`, V11 computes

`BF = RR_EU * RR_UY / (RR_EU + RR_UY - 1)`

and the observed association shifted toward the null by that bias factor. The full declared two-dimensional grid is returned together with the first supplied pair able to explain the observed magnitude to the null.

`RR_BIAS_FACTOR_SURFACE != UNIVERSAL_HIDDEN_CONFOUNDING_BOUND`.

## Finite-model Bayes-adaptive POMDP

V10 solved one known finite POMDP model. V11 adds a static uncertain model index `M`, so the hidden state is `(M,S)`. Each candidate model supplies its own reward, transition, and observation distributions under common action IDs. Observations update the joint posterior over model identity and physical state.

Bounds:

- <=4 models;
- <=6 states;
- <=6 common actions;
- <=8 observation symbols per action/model;
- horizon <=3.

If the complete supplied tree is exhausted before the node cap, status is

`FINITE_MODEL_BAYES_ADAPTIVE_POMDP_EXACT_HORIZON_CERTIFIED`

with certificate

`EXACT_FOR_SUPPLIED_STATIC_MODEL_SET_STATE_SPACE_ACTIONS_OBSERVATIONS_AND_HORIZON`.

Truncated search receives no certificate. Every result is plan-only.

`FINITE_MODEL_BAPOMDP != GENERAL_BAYES_ADAPTIVE_CONTROL`.

## Evidence-dependence uncertainty

V10 fits evidence-dependence logistic coefficients from external labels. V11 reconstructs the observed-information/Hessian matrix and uses a Laplace approximation for query-logit uncertainty:

`Var(eta) ~= phi^T H^-1 phi`.

The logit interval is transformed through the sigmoid. It is model- and sample-conditional.

`LAPLACE_DEPENDENCE_INTERVAL != CALIBRATED_COVERAGE_GUARANTEE`.

## Coordinate

`COLLECTIVE_ADAPTIVE=<GH,GV,LP,SL,SS,BP,EU,L>`

- `GH`: GP hyperparameter adaptation
- `GV`: GP decision value
- `LP`: latent projection geometry
- `SL`: stacked TMLE
- `SS`: sensitivity surface
- `BP`: finite-model Bayes-adaptive policy
- `EU`: evidence-dependence uncertainty
- `L`: lineage/native context

## Authority

V11 adds no semantic-authority shortcut. GP model updates remain model-state mutations; graph transforms are hypotheses/transforms; effect estimators and sensitivity surfaces remain evidence state; policies remain plans. Existing semantic VID, Git HEAD, topology version, policy version, and projection/compensation authority planes remain unchanged.

## Successor boundary

V11 does not claim continuous GP hyperparameter posteriors, sparse scalable GP inference, neural Bayesian world models, data-discovered FCI/RFCI PAGs, broad Super Learner oracle guarantees, longitudinal/continuous-treatment TMLE, general continuous-parameter Bayes-adaptive control, long-horizon joint GP/POMDP experiment optimization, chance-constrained stochastic resource certification, or formal coverage guarantees for evidence-dependence intervals.
