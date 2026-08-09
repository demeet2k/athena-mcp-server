# COLLECTIVE RUNTIME V15 — CALIBRATED CONTINUOUS SCIENTIFIC CONTROL

Coordinate:

`COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>`

V15 is an additive successor to V14. It does not replace the operational organism, Deployment.2, Y1, JSPACE, PROMOTION.2, or the Git-backed prompt/coordination surfaces.

## SR — structural reliability calibration

`athena_structural_reliability_calibrate` accepts externally labelled examples `(bootstrap_support, correct)` and fits a weighted monotone isotonic reliability map. Calibration predictions used for diagnostics are out-of-fold; the final curve is refit on the complete labelled calibration set for future read-only use.

Identical support coordinates are aggregated before pool-adjacent-violators (PAV). This is required because one semantic coordinate cannot lawfully retain multiple fitted reliabilities merely because equal-support rows happened to sort by different labels. Diagnostics use the same declared positive weights as the fitted reliability curve. The prediction convention is explicit: right-continuous monotone step interpolation with endpoint extension.

`IDENTICAL_CALIBRATION_COORDINATE != MULTIPLE_FITTED_VALUES`.

`OUT_OF_FOLD_ISOTONIC_RELIABILITY != CAUSAL_GRAPH_POSTERIOR`.

The operator estimates empirical correctness reliability conditional on the supplied labels and support statistic. It does not infer hidden confounding, causal identifiability, graph equivalence, or a Bayesian posterior over graphs. Labels are caller-supplied external witnesses and are never manufactured from bootstrap support itself.

## XT — cross-fitted two-timepoint sequential TMLE

`athena_longitudinal_tmle_crossfit` is bounded to binary history:

`X -> A1 -> L1 -> A2 -> Y`.

Rows are assigned deterministically to 2..10 folds. For each held-out fold, propensity/outcome/targeting models are fit without that fold; held-out target predictions are then aggregated. The stage-2 pseudo outcome retains observed `A1,L1` before stage-1 intervention/evaluation.

Critical invariant:

`STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION`.

Named treatment/intermediate/outcome fields cannot also be supplied as baseline covariates. Baseline values must be finite. The four named longitudinal fields must be distinct. These checks prevent temporal variables from being smuggled into the pre-treatment nuisance surface through aliases.

`CROSS_FITTED_TWO_TIMEPOINT_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM`.

Cross-fitting reduces nuisance/evaluation reuse. It does not establish sequential exchangeability, positivity, consistency, no relevant interference, temporal correctness, or nuisance-model adequacy. Declared latent confounding fails closed. The current standard-error field is explicitly a finite-sample proxy over held-out target predictions, not an efficient-influence-curve theorem.

## XD — cross-fitted sequential doubly robust policy value

`athena_sequential_dr_policy_crossfit` fits `g1,g2,Q2,Q1` on training folds and evaluates a sequential AIPW score on held-out rows for deterministic two-timepoint policies.

Decision-time history is explicit:

`A1_POLICY_FEATURES = baseline`

`A2_POLICY_FEATURES = baseline + {A1,L1}`.

A stage-1 policy cannot condition on `L1`, `A2`, or `Y`. A stage-2 policy cannot condition on `A2` or `Y`. Policy coefficients, intercepts, thresholds and baseline history values must be finite. Policy ids must be unique.

Critical invariant:

`A1_POLICY_USES_BASELINE_ONLY__A2_POLICY_USES_BASELINE_A1_L1_ONLY`.

`DECISION_TIME_HISTORY != FULL_ROW_STATE`.

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

Covariance is required to be finite, symmetric and PSD; the observation variance must be finite and positive. Observation/action coefficients may reference only declared Gaussian variables. Unknown coordinates are rejected rather than silently interpreted as zero coefficients. Action ids are unique; costs and scalarization weights must be finite and non-negative.

`UNKNOWN_COEFFICIENT != ZERO_COEFFICIENT`.

`NONFINITE_NUMERIC_STATE != MODEL_COORDINATE`.

`LINEAR_GAUSSIAN_UPDATE != GENERAL_CONTINUOUS_JOINT_BAYES`.

`athena_joint_gaussian_control` propagates linear action utilities exactly through the declared Gaussian belief and computes expected utility, standard deviation and lower-tail Normal CVaR, retaining a Pareto frontier before visible scalarization.

`GAUSSIAN_LINEAR_CONTROL != GENERAL_BELIEF_MDP`.

Neither operator mutates canonical Y1/JSPACE or execution state by adjacency.

## AT — approximation-error transport

`athena_approx_error_transport` receives witnessed approximation errors at explicit finite feature coordinates and a caller-declared Lipschitz envelope `L`. The declaration is first checked against all supplied witness pairs:

`|e_i-e_j| <= L ||x_i-x_j||_2`.

The global mathematical envelope is:

`e_hat_global(x) <= min_i [e_i + L ||x-x_i||_2]`.

Three coordinates are kept distinct:

1. the geometrically nearest witness;
2. the witness giving the tightest global envelope;
3. when `max_transport_radius` is declared, the radius-eligible witness giving the tightest local certificate.

If a radius is present, `transported_error_upper_bound` uses the tightest **eligible** witness inside that radius; the unrestricted global envelope is reported separately. This prevents a farther low-error witness from incorrectly making the local radius gate fail even though a valid nearby certificate exists.

If a radius is declared and **no witness is radius-eligible**, the local transport certificate does not exist. V15 returns `local_certificate_available=false` and sets the local `transported_error_upper_bound`, `transport_witness_index`, and `transport_witness_distance` fields to `null`. The unrestricted `global_envelope_upper_bound` and its witness remain visible in separate fields but cannot satisfy the declared local radius constraint.

`GEOMETRIC_NEAREST_WITNESS != TIGHTEST_ERROR_ENVELOPE_WITNESS`.

`GLOBAL_ENVELOPE != RADIUS_ELIGIBLE_LOCAL_CERTIFICATE`.

`NO_RADIUS_ELIGIBLE_WITNESS != GLOBAL_FALLBACK_CERTIFICATE`.

Optional decision-margin checks can mark a query as decision-preserving only when a radius-eligible certificate exists and its bound clears the declared safety fraction of the margin. A missing local certificate therefore yields no decision-preservation certificate even if the unrestricted global envelope is numerically small.

`DECLARED_LIPSCHITZ_ERROR_ENVELOPE != EMPIRICAL_GLOBAL_ERROR_TRUTH`.

`TRANSPORT_CERTIFICATE_CONDITIONAL_ON_LIPSCHITZ_BOUND`.

Witness consistency cannot prove the global Lipschitz law beyond the observed domain.

## MD — finite-horizon rectangular TV-DRO

`athena_multistage_tv_dro_plan` solves a finite state/action robust dynamic program for horizon `H<=8` under state-action rectangular total-variation ambiguity around each supplied transition distribution:

`V_t(s)=max_a [ r(s,a) + gamma min_{q: TV(q,p_sa)<=rho} q^T V_{t+1} ]`.

For a finite support, the inner TV minimization is solved exactly by transporting probability mass from the highest-value successor states to the lowest-value successors up to the TV radius. Backward induction is exact for the declared finite rectangular ambiguity model.

State/action identities must be non-empty and unique in their local scope. Extra state keys, unknown successor coordinates, non-finite rewards/probabilities and invalid distributions fail closed instead of being ignored or normalized silently.

`UNKNOWN_STATE_COORDINATE != UNUSED_METADATA`.

`NONFINITE_TRANSITION != PROBABILITY_MODEL`.

Certificate:

`EXACT_DYNAMIC_PROGRAM_FOR_SUPPLIED_FINITE_RECTANGULAR_TV_AMBIGUITY_MODEL`.

`RECTANGULAR_TV_ROBUST_MDP != GENERAL_MULTISTAGE_DRO`.

The certificate does not cover non-rectangular ambiguity, continuous states/actions, learned transition correctness, real-world safety, or execution authority.

## V15 numerical and temporal membrane

Across V15 operators:

`NONFINITE_NUMERIC_STATE != MODEL_COORDINATE`.

`UNKNOWN_COORDINATE != ZERO_COORDINATE`.

`DECISION_TIME_HISTORY != FULL_ROW_STATE`.

`IDENTICAL_SEMANTIC_COORDINATE != ORDER_DEPENDENT_DUPLICATE_STATE`.

These are input/model-contract laws, not scientific-identification claims. They prevent numerical or coordinate ambiguity from masquerading as valid model evidence.

## V15 authority membrane

All V15 outputs remain calibration/model/science/control state:

`V15_STATE != Y1_AUTHORITY`

`V15_STATE != CANONICAL_JSPACE`

`PLAN != EXECUTION`

`CALIBRATION != OBSERVATION`

`MODEL_ROBUSTNESS != REAL_WORLD_GUARANTEE`

`COLLECTIVE_CALIBRATED != DEPLOYMENT_AUTHORITY != COORDINATION_AUTHORITY`.

Deployment.2 remains a separately typed host/control-plane organ. Message Board/Party/Cohesion remain separately typed coordination organs. PROMOTION.2 remains the exact-head trust membrane.

## Release-overlay synchronization membrane

V15 also exposed import-time chart drift in the composed runtime. Package/protocol attributes, imported values, imported callables, copied resource lists and derived URI sets can represent the same semantic release coordinate without sharing Python object identity.

The V15 installer therefore advances every live authority-bearing projection used by initialize/HTTP, manifest resources, public resource discovery and MAXDEV fallback.

`MODULE_ATTRIBUTE_ADVANCE != IMPORTED_VALUE_SNAPSHOT_ADVANCE`.

`MODULE_FUNCTION_REPLACEMENT != IMPORTED_FUNCTION_SNAPSHOT_ADVANCE`.

`SOURCE_LIST_MUTATION != COPIED_RESOURCE_REGISTRY_MUTATION`.

Public navigation paths claiming the current manifest coordinate must agree on the same runtime artifact.

## Proof-selection membrane

V3.4 release critical checks validate that every `unittest discover -p` selector names an actual repository test file. A successful process with zero selected tests is not proof.

`ZERO_TEST_SELECTION != PROOF`.

`TEST_COMMAND_EXIT_0 != WITNESSED_ASSERTION_EXECUTION`.

## Residual boundary

V15 intentionally leaves unresolved: calibrated probabilistic graph posteriors/full FCI-RFCI, arbitrary-horizon longitudinal TMLE/DML, non-Gaussian continuous joint Bayes, general continuous belief-MDP control, learned/calibrated approximation-error fields without declared envelopes, non-rectangular/Wasserstein/f-divergence ambiguity, continuous-state multistage stochastic/DRO optimization, and empirical validation of model robustness against world dynamics.
