# COLLECTIVE RUNTIME V15 — CALIBRATED CONTINUOUS SCIENTIFIC CONTROL

Coordinate:

`COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>`

V15 is an additive successor to V14. It does not replace the operational organism, Deployment.2, Y1, JSPACE, PROMOTION.2, or the Git-backed prompt/coordination surfaces.

## SR — structural reliability calibration

`athena_structural_reliability_calibrate` accepts externally labelled examples `(bootstrap_support, correct)` and fits a monotone isotonic reliability map. Calibration predictions used for diagnostics are out-of-fold; the final curve is refit on the complete labelled calibration set for future read-only use.

`OUT_OF_FOLD_ISOTONIC_RELIABILITY != CAUSAL_GRAPH_POSTERIOR`.

The operator estimates empirical correctness reliability conditional on the supplied labels and support statistic. It does not infer hidden confounding, causal identifiability, graph equivalence, or a Bayesian posterior over graphs. Labels are external witnesses and are never manufactured from bootstrap support itself.

## XT — cross-fitted two-timepoint sequential TMLE

`athena_longitudinal_tmle_crossfit` is bounded to binary history:

`X -> A1 -> L1 -> A2 -> Y`.

Rows are assigned deterministically to 2..10 folds. For each held-out fold, propensity/outcome/targeting models are fit without that fold; held-out target predictions are then aggregated. The stage-2 pseudo outcome retains observed `A1,L1` before stage-1 intervention/evaluation.

`CROSS_FITTED_TWO_TIMEPOINT_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM`.

Cross-fitting reduces nuisance/evaluation reuse. It does not establish sequential exchangeability, positivity, consistency, no relevant interference, temporal correctness, or nuisance-model adequacy. Declared latent confounding fails closed. The current standard-error field is explicitly a finite sample proxy over held-out target predictions, not an efficient-influence-curve theorem.

## XD — cross-fitted sequential doubly robust policy value

`athena_sequential_dr_policy_crossfit` fits `g1,g2,Q2,Q1` on training folds and evaluates a sequential AIPW score on held-out rows for deterministic two-timepoint policies.

Critical invariant:

`STAGE2_POLICY_EVALUATION_USES_OBSERVED_A1_L1_BEFORE_STAGE1_POLICY_ACTION`.

`CROSS_FITTED_SEQUENTIAL_DR != GENERAL_OFF_POLICY_CAUSAL_VALUE`.

`CROSS_FITTING != IDENTIFICATION`.

Policy estimates are PLAN_ONLY. Higher estimated value is not treatment authorization or execution history.

## CJ — finite-dimensional continuous Gaussian joint belief

`athena_joint_gaussian_update` implements the exact update for a declared Gaussian state and linear Gaussian observation:

`X ~ N(mu,Sigma)`

`y = h^T X + epsilon`, `epsilon ~ N(0,R)`

`S = h^T Sigma h + R`

`K = Sigma h / S`

`mu' = mu + K(y-h^T mu)`

`Sigma' = Sigma - K(Sigma h)^T`.

Covariance is required to be symmetric PSD and the observation variance positive.

`LINEAR_GAUSSIAN_UPDATE != GENERAL_CONTINUOUS_JOINT_BAYES`.

`athena_joint_gaussian_control` propagates linear action utilities exactly through the declared Gaussian belief and computes expected utility, standard deviation and lower-tail Normal CVaR, retaining a Pareto frontier before visible scalarization.

`GAUSSIAN_LINEAR_CONTROL != GENERAL_BELIEF_MDP`.

Neither operator mutates canonical Y1/JSPACE or execution state by adjacency.

## AT — approximation-error transport

`athena_approx_error_transport` receives witnessed approximation errors at explicit feature coordinates and a caller-declared Lipschitz envelope `L`. The declaration is first checked against all supplied witness pairs:

`|e_i-e_j| <= L ||x_i-x_j||_2`.

A query receives the conditional upper envelope:

`e_hat(x) <= min_i [e_i + L ||x-x_i||_2]`.

Optional radius and decision-margin checks can mark a query as decision-preserving under the supplied bound.

`DECLARED_LIPSCHITZ_ERROR_ENVELOPE != EMPIRICAL_GLOBAL_ERROR_TRUTH`.

`TRANSPORT_CERTIFICATE_CONDITIONAL_ON_LIPSCHITZ_BOUND`.

Witness consistency cannot prove the global Lipschitz law beyond the observed domain.

## MD — finite-horizon rectangular TV-DRO

`athena_multistage_tv_dro_plan` solves a finite state/action robust dynamic program for horizon `H<=8` under state-action rectangular total-variation ambiguity around each supplied transition distribution:

`V_t(s)=max_a [ r(s,a) + gamma min_{q: TV(q,p_sa)<=rho} q^T V_{t+1} ]`.

For a finite support, the inner TV minimization is solved exactly by transporting probability mass from the highest-value successor states to the lowest-value successors up to the TV radius. Backward induction is exact for the declared finite rectangular ambiguity model.

Certificate:

`EXACT_DYNAMIC_PROGRAM_FOR_SUPPLIED_FINITE_RECTANGULAR_TV_AMBIGUITY_MODEL`.

`RECTANGULAR_TV_ROBUST_MDP != GENERAL_MULTISTAGE_DRO`.

The certificate does not cover non-rectangular ambiguity, continuous states/actions, learned transition correctness, real-world safety, or execution authority.

## V15 authority membrane

All V15 outputs remain calibration/model/science/control state:

`V15_STATE != Y1_AUTHORITY`

`V15_STATE != CANONICAL_JSPACE`

`PLAN != EXECUTION`

`CALIBRATION != OBSERVATION`

`MODEL_ROBUSTNESS != REAL_WORLD_GUARANTEE`

`COLLECTIVE_CALIBRATED != DEPLOYMENT_AUTHORITY != COORDINATION_AUTHORITY`.

Deployment.2 remains a separately typed host/control-plane organ. Message Board/Party/Cohesion remain separately typed coordination organs. PROMOTION.2 remains the exact-head trust membrane.

## Residual boundary

V15 intentionally leaves unresolved: calibrated probabilistic graph posteriors/full FCI-RFCI, arbitrary-horizon longitudinal TMLE/DML, non-Gaussian continuous joint Bayes, general continuous belief-MDP control, learned/calibrated approximation-error fields without declared envelopes, non-rectangular/Wasserstein/f-divergence ambiguity, continuous-state multistage stochastic/DRO optimization, and empirical validation of model robustness against world dynamics.
