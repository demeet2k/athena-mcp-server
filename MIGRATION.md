# ATHENA Runtime Migration

## Active-tree provenance

The active `master` tree was rebuilt during the 2026-08-07 rebuild. Older state remains in Git history/archive and is never canonical merely because it exists.

Legacy admission remains:

`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

---

# 2.9.0 -> 3.0.0

`athena-canonical-mcp 3.0.0` adds **Collective Adaptive V11** on top of V1–V10.

The migration is additive. Existing Gaussian/GP beliefs, graph hypotheses, TMLE/AIPW estimates, sensitivity results, POMDP policies and evidence-dependence labels/models remain distinct. V11 does not bulk-reinterpret historical state as adaptive-model evidence.

## New persistent V11 surface

- `collective_v11_gp_hyperfits`.

This journal records finite-grid GP hyperparameter evaluations and whether an explicitly CAS-authorized winner was applied. Existing GP observations remain in the V10 GP model table.

## New V11 MCP tools

- `athena_gp_hyperfit`
- `athena_gp_decision_evsi`
- `athena_latent_project_admg`
- `athena_causal_tmle_ensemble`
- `athena_sensitivity_rr_surface`
- `athena_bapomdp_solve`
- `athena_evidence_dependence_interval`.

New resource:

`athena://collective/v11`.

## Fixed GP -> adaptive GP migration

V10 GP remains an exact bounded posterior conditional on fixed declared RBF hyperparameters.

V11 hyperfit evaluates a finite visible grid using

`log p(y|X,theta) = -1/2 y^T K^-1 y - 1/2 log|K| - n/2 log(2pi)`.

Historical GP observations are not changed during design-only fitting.

Applying a winner is explicit and requires the current `expected_observation_count`; stale observed-row state rejects. This is an additional GP model-state CAS, not a semantic-state mutation.

`MARGINAL_LIKELIHOOD_OPTIMUM != TRUE_KERNEL`.

## EVSI -> GP decision-EVSI migration

V9 EVSI remains correct for Gaussian **linear parameter** measurement designs.

V11 GP-EVSI is a separate nonlinear GP object using joint posterior covariance between action and measurement points:

`mu_a' = mu_a + Cov(f_a,f_e)/(Var(f_e)+sigma_e^2)*(y_e-mu_e)`.

Do not rename V9 EVSI histories as GP-EVSI. Different model/observation assumptions govern them.

GP-EVSI is design-only and never creates GP observations.

## PC/partial graph -> supplied latent projection migration

V7–V10 observational graph hypotheses remain unchanged.

V11 latent projection does not discover hidden variables from those graph outputs. It accepts a separately supplied causal DAG plus an explicit latent-node set and transforms that declared model into restricted observed directed/bidirected geometry.

No PC/partial edge is automatically converted into a bidirected confounding edge. No projection call creates JSPACE edges.

`SUPPLIED_DAG_LATENT_PROJECTION != DATA_DISCOVERED_PAG`.

## TMLE -> stacked TMLE migration

V10 single-logistic-nuisance TMLE remains available.

V11 adds a separate transparent nuisance ensemble using deterministic validation-weighted simple, linear and degree-2 logistic candidates inside cross-fitting. Existing V10 TMLE records are not relabeled as ensemble estimates.

The stronger nuisance surface does not weaken causal identification requirements.

`STACKED_TMLE != SUPER_LEARNER_THEOREM`.

Declared latent-confounding risk still fails closed.

## E-value -> RR sensitivity surface migration

V10 point/CI E-value remains a one-number sensitivity summary.

V11 adds a declared two-dimensional bias-factor grid:

`BF=RR_EU*RR_UY/(RR_EU+RR_UY-1)`.

Historical E-values are not converted into surface cells. The grid encodes explicit hidden-confounding strength assumptions and reports toward-null adjusted associations.

`RR_BIAS_FACTOR_SURFACE != UNIVERSAL_HIDDEN_CONFOUNDING_BOUND`.

## POMDP -> finite-model Bayes-adaptive POMDP migration

V10 assumes one supplied transition/observation model.

V11 `athena_bapomdp_solve` instead takes a finite set of candidate models with explicit priors and common action IDs. Its hidden state is `(M,S)`, with model identity static but uncertain. Observations update posterior mass over both `M` and `S`.

No V10 POMDP policy is silently converted into a model prior.

A completed bounded search certifies only:

`EXACT_FOR_SUPPLIED_STATIC_MODEL_SET_STATE_SPACE_ACTIONS_OBSERVATIONS_AND_HORIZON`.

Node-limited search returns no certificate.

`FINITE_MODEL_BAPOMDP != GENERAL_BAYES_ADAPTIVE_CONTROL`.

## Evidence-dependence uncertainty migration

V10 fitted dependence coefficients and external labels remain the source model/data.

V11 adds a model-conditional Laplace/Hessian uncertainty calculation around those fitted logits. Existing point predictions are not reclassified as calibrated intervals.

`LAPLACE_DEPENDENCE_INTERVAL != CALIBRATED_COVERAGE_GUARANTEE`.

## Authority compatibility

3.0.0 does not weaken earlier authority planes:

- semantic writes retain VID/event-head authority;
- Git writes retain Git-head CAS;
- topology retains topology-version CAS;
- learned policy retains policy-version CAS;
- GP hyperparameter application gains its own exact observed-row-count precondition;
- projection/compensation retain their existing recovery authority;
- V4–V11 prediction, belief, causal-estimation, sensitivity, graph, policy and evidence-dependence surfaces remain evidential/advisory unless separately promoted through canonical mutation law.

A marginal-likelihood optimum, large GP-EVSI, bidirected latent projection, tight stacked-TMLE interval, strong sensitivity surface, exact finite BA-POMDP certificate, or narrow dependence interval never silently mutates canon.

## V11 migration firewall

- marginal-likelihood optimum != true kernel;
- GP decision EVSI != observed evidence;
- supplied-DAG latent projection != data-discovered PAG;
- stacked TMLE != universal Super Learner theorem;
- stacked TMLE estimate != identification proof;
- RR bias-factor surface != universal hidden-confounding theorem;
- finite-model BA-POMDP certificate != general/real-world optimality;
- Laplace dependence interval != calibrated coverage guarantee;
- model exactness != model correctness;
- model/simulation output != observation;
- unknown cost != zero cost.

## Deployment check

After upgrade verify:

1. package and MCP server version both equal `3.0.0`;
2. all seven V11 tools appear in `tools/list`;
3. `athena://collective/v11` reads as `COLLECTIVE_RUNTIME_V11`;
4. legacy V1–V10 tests pass;
5. constructive V11 tests pass;
6. adversarial V11 tests pass;
7. stdio `python -m athena_mcp` crosses V11 GP hyperfit/GP-EVSI, supplied latent projection, ensemble TMLE, sensitivity surface and exact finite-model BA-POMDP before exact emission verification;
8. canonical brain promotion occurs only after the exact final runtime/version/documentation head passes CI.
