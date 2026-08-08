# ATHENA COLLECTIVE RUNTIME V13 — ROBUST CONTINUOUS-BAYES AND CAUSAL-CONTROL LAYER

Runtime version: `COLLECTIVE_RUNTIME_V13`

Public release target: `athena-canonical-mcp 3.2.0`

Live architecture target: `ATHENA.RUNTIME.UNIFIED.8`

Coordinate:

`COLLECTIVE_ROBUST=<HB,FG,JD,FC,LT,DP,DR,L>`

- `HB` — bounded continuous-domain GP hyperparameter belief by log-space QMC;
- `FG` — deterministic inducing-point FITC GP approximation;
- `JD` — joint model-information + downstream decision-value experiment design;
- `FC` — bounded FCI-inspired partial ancestral candidate;
- `LT` — history-preserving two-timepoint sequential logistic TMLE;
- `DP` — deterministic two-timepoint dynamic-policy g-formula value;
- `DR` — correlated Gaussian + ellipsoidal-mean robust resource selection;
- `L` — lineage/native context.

V13 is a lazy successor surface reached through the existing V11→V12 compatibility membrane. It does not create a second root server, semantic authority path, trusted-promotion path, or canonical write domain.

## 1. Continuous-domain GP hyperbelief — `athena_gp_hyperqmc`

For positive hyperparameter box `Theta=[l_min,l_max]×[sf_min,sf_max]×[sn_min,sn_max]`, V13 generates deterministic Halton particles in log coordinates and scores each using the exact bounded RBF-GP log marginal likelihood already implemented by V12:

`L(theta)=-1/2 y^T K_theta^-1 y -1/2 log|K_theta| -n/2 log(2pi)`.

Posterior weights are normalized by log-sum-exp/softmax. The result exposes entropy, effective sample size and log-space moments.

`QMC_CONTINUOUS_HYPERPOSTERIOR != EXACT_CONTINUOUS_HYPERPARAMETER_BAYES`.

The result approximates a continuous-domain log-uniform posterior over the declared box. Finite quadrature points do not establish the true kernel or exact continuous integration.

## 2. FITC inducing GP — `athena_gp_fitc_predict`

V13 selects deterministic farthest-point inducing rows `Z` from observed GP data and forms a FITC-style approximation. With `Kmm`, `Knm` and diagonal conditional residual

`Lambda_i = k(x_i,x_i) - q_ii + sigma_n^2`,

it computes the inducing posterior with complexity proxy

`O(n m^2 + m^3)`

instead of full `O(n^3)` matrix work. Every query also returns deviation from the exact current bounded GP reference.

`FITC_INDUCING_GP != FULL_GP_POSTERIOR_OR_VARIATIONAL_OPTIMUM`.

A query-level reference error is a witness at that query, not a global approximation theorem.

## 3. Joint model-information / decision-value design — `athena_gp_joint_design`

V13 values a candidate measurement through both:

- expected downstream best-action improvement;
- expected reduction in entropy of the QMC hypermodel belief.

For hypothetical measurement `y_e`, model weights update as

`w_i' ∝ w_i p(y_e|M_i,D)`

while each model updates action means by Gaussian conditioning. The score is a visible weighted combination of decision EVSI, model-information gain, feasibility, cost and risk.

`JOINT_MODEL_INFORMATION_DESIGN != OBSERVATION`.

No hypothetical measurement, posterior reweight or conditional action mean becomes a GP training row, evidence, execution record or Y1 authority state.

## 4. Bounded FCI-lite — `athena_fci_lite_discover`

V13 tests every observed-variable conditioning subset up to a declared bounded order for each candidate pair, retains separation sets, marks unshielded collider arrowheads and applies limited conservative R1-like propagation.

Status:

`BOUNDED_FCI_LITE_CANDIDATE`.

The implementation explicitly omits complete possible-d-sep, discriminating paths, full PAG orientation rules, selection-bias semantics and completeness guarantees.

`BOUNDED_FCI_LITE != FCI_RFCI_PAG_THEOREM`.

No structural candidate writes canonical JSPACE.

## 5. Two-timepoint sequential logistic TMLE — `athena_longitudinal_tmle`

Observed history:

`X -> A1 -> L1 -> A2 -> Y`.

V13 fits:

`g1=P(A1|X)`,

`g2=P(A2|X,A1,L1)`,

`Q2=P(Y|X,A1,L1,A2)`.

It then performs two bounded logistic fluctuation steps. Critically, the stage-2 pseudo-outcome is evaluated at target `A2=a2` while preserving each row's observed `A1,L1` history; the stage-2 clever covariate is zero for histories incompatible with target `A1=a1`. Stage 1 learns that targeted pseudo-outcome over observed `A1`, then evaluates `A1=a1`.

`STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION`.

Declared latent confounding fails closed.

`TWO_TIMEPOINT_SEQUENTIAL_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM_OR_IDENTIFICATION_PROOF`.

The current implementation does not claim cross-fitted semiparametric efficiency, stochastic interventions, arbitrary treatment horizons or identification outside declared assumptions.

## 6. Dynamic two-timepoint policy value — `athena_dynamic_policy_value`

A deterministic policy may specify static binary actions or linear-threshold rules:

`A1=pi1(X)`

`A2=pi2(X,A1,L1)`.

V13 values each policy by integrating over the fitted intermediate distribution and outcome model under the induced two-timepoint history.

`DYNAMIC_GFORMULA_POLICY_VALUE != GENERAL_OFF_POLICY_CAUSAL_VALUE`.

Policy ranking is not execution authorization and is conditional on the parametric longitudinal model and causal assumptions.

## 7. Correlated robust resource selection — `athena_dro_resource_select`

For candidate-resource mean vector `mu`, declared covariance `Sigma`, per-candidate mean-uncertainty magnitudes `u_i`, ellipsoidal radius `rho` and one-sided Gaussian quantile `z_(1-alpha)`, subset feasibility uses

`sum mu_i + rho*sqrt(sum u_i^2) + z_(1-alpha)*sqrt(1_S^T Sigma 1_S) <= B`.

For `n <= exact_limit`, every subset is enumerated and may receive:

`EXACT_ENUMERATION_UNDER_DECLARED_CORRELATED_GAUSSIAN_COVARIANCE_AND_ELLIPSOIDAL_MEAN_AMBIGUITY`.

Above the exact threshold, deterministic greedy selection returns no optimality certificate.

`ELLIPSOIDAL_GAUSSIAN_ROBUST_PLAN != GENERAL_DISTRIBUTIONALLY_ROBUST_OPTIMIZATION`.

`ROBUST_RESOURCE_PLAN != EXECUTION`.

## 8. Authority / mutation / trust firewall

V13 is read-only with respect to canonical semantic, Git, topology and Y1 authority surfaces. The GP design/prediction surfaces do not append observations. FCI-lite does not create JSPACE edges. Longitudinal estimates/policy values do not establish identification or execution. Robust resource plans do not spend resources.

PROMOTION.2 remains unchanged:

`CALLER_ATTESTATION != TRUSTED_EXTERNAL_VERIFICATION`.

`ATTESTED_READY != QUALIFIED`.

A host-internal trusted verifier is intentionally not exposed as a caller-supplied MCP field. V13 does not implement or simulate that unresolved control-plane bridge.

## 9. Successor boundary

V13 does not claim exact continuous GP hyperposterior integration/MCMC/HMC, optimized variational sparse GP, neural Bayesian world models, full FCI/RFCI, calibrated PAG-edge posteriors, cross-fitted general longitudinal TMLE, arbitrary-horizon dynamic regimes, general doubly robust off-policy value, robust POMDP dynamics, Wasserstein/f-divergence DRO, multistage stochastic resource control, or trusted external promotion verification.
