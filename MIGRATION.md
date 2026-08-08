# ATHENA Runtime Migration

## Active-tree provenance

The active `master` tree was rebuilt during the 2026-08-07 rebuild. Older state remains in Git history/archive and is never canonical merely because it exists.

Legacy admission remains:

`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

---

# 2.7.0 -> 2.8.0

`athena-canonical-mcp 2.8.0` adds **Collective Inference V9** on top of the V1–V8 organization/memory/learning/ecology/science/discovery/dual-control/belief stack.

The migration is additive. No finite V8 belief, canonical object, graph edge, policy state, transition row or science-shadow witness is silently reinterpreted as a stronger V9 inference object.

## New persistent V9 surfaces

V9 creates lazily and non-destructively:

- `collective_v9_gaussian_beliefs`
- `collective_v9_robust_effects`.

Gaussian parameter beliefs are distinct from V8 finite model beliefs and V5 contextual Bayesian arms. Existing finite probabilities are not transformed into Gaussian means/covariances.

Robust effect rows are distinct from V8 point estimators and V6/V7 identification records.

## New V9 MCP tools

- `athena_gaussian_belief_register`
- `athena_gaussian_belief_state`
- `athena_gaussian_belief_observe`
- `athena_decision_evpi`
- `athena_decision_evsi`
- `athena_belief_policy_multistage`
- `athena_causal_aipw`
- `athena_causal_robustness`
- `athena_structure_partial`
- `athena_evidence_dependence_probability`.

New resource:

`athena://collective/v9`.

## Finite -> continuous belief migration

V8 finite belief remains

`P(M_i|D)`

over an explicit discrete model set.

V9 Gaussian belief is a different object:

`theta|D ~ N(mu,Sigma)`

for a declared finite-dimensional linear parameter vector.

It must be explicitly registered. Historical model scores or V8 probabilities are not silently moment-matched into a Gaussian posterior.

The V9 update path requires one actual numeric target and a complete design vector:

`A'=A+wxx^T/sigma^2`

`b'=b+wxy/sigma^2`.

Only `athena_gaussian_belief_observe` mutates that posterior. EVPI/EVSI/policy calls are read-only.

`GAUSSIAN_LINEAR_POSTERIOR != GENERAL_CONTINUOUS_BAYES`.

## EVI -> EVPI / EVSI migration

V8 EVI remains the correct operator for finite discrete model/outcome designs.

V9 EVPI is a Monte-Carlo estimate of the value ceiling under a Gaussian linear parameter/utility model:

`EVPI ~= E_theta[max_a U(a,theta)]-max_a U(a,Etheta)`.

V9 EVSI estimates the expected downstream decision improvement from one declared noisy linear measurement design.

Do not rename historical EIG or EVI values as EVPI/EVSI. These quantities condition on different model spaces and observation assumptions.

Returned Monte-Carlo standard error and seed are part of the witness.

`MONTE_CARLO_EVPI_EVSI != EXACT_ANALYTIC_VALUE`.

## Belief-policy migration

V8 contingent policy is depth-1.

V9 `athena_belief_policy_multistage` exactly recurses over the caller-declared finite model/outcome surface for horizon up to three.

No previous scenario or contingent branch is converted into history. Policy construction is read-only and `PLAN_ONLY`.

`MULTISTAGE_FINITE_BELIEF_POLICY != GENERAL_POMDP`.

## Causal-estimation migration

V6/V7 identification checks remain the authority surface for whether an effect is recoverable under a supplied graph/design.

V8 narrow linear/Wald/mediation point estimators remain available.

V9 adds deterministic two-fold cross-fitted AIPW for binary treatment, with logistic propensity nuisance fit, ridge outcome nuisance fits, propensity clipping, influence-function standard error and approximate 95% interval.

The operation does not promote old linear estimates or identification checks automatically.

AIPW's double-robust interpretation remains conditional on identification, positivity, consistency and nuisance-model conditions.

`AIPW_ESTIMATE != IDENTIFICATION_PROOF`.

Explicit `latent_confounding_possible=true` fails closed.

## Robustness migration

V9 leave-one-adjustment-out robustness recomputes V8 back-door linear estimates while omitting each declared observed adjustment in turn.

It diagnoses specification sensitivity among observed covariates only.

It is not a hidden-confounding sensitivity theorem, E-value or Rosenbaum bound.

## Partial-graph migration

V7/V8 association-skeleton/bootstrap objects remain unchanged.

V9 `athena_structure_partial` presents stable undirected hypotheses as `o-o` endpoints to preserve unresolved orientation.

This is a heuristic partial graph. It must not be migrated or relabeled as an FCI PAG/CPDAG without a future valid structural-discovery procedure.

No call creates canonical JSPACE causal edges.

## Evidence-dependence migration

V7 effective-N and V8 spectral participation ratio remain descriptive redundancy surfaces.

V9 adds a caller-declared logistic metadata-dependence model. Pairwise probabilities are conditional on those visible coefficients and metadata comparisons.

Existing independence keys and witness metadata are not reinterpreted as ground-truth dependence labels.

Missing comparable metadata contributes conservative dependence pressure rather than zero dependence.

`DEPENDENCE_PROBABILITY_MODEL != FORMAL_EVIDENCE_INDEPENDENCE`.

## Authority compatibility

2.8.0 does not weaken earlier authority planes:

- semantic writes retain VID/event-head authority;
- Git writes retain Git-head CAS;
- topology retains topology-version CAS;
- V3 policy retains policy-version CAS;
- projection/compensation retain explicit recovery authority;
- V4–V9 statistical, belief, estimator, graph-hypothesis, experiment and control state remains evidential/advisory unless separately promoted through canonical mutation law.

A narrow posterior interval, large AIPW t-ratio or high dependence probability never silently mutates canon.

## V9 migration firewall

- Gaussian linear posterior != general continuous Bayes;
- Monte-Carlo EVPI/EVSI != exact analytic decision value;
- EVPI/EVSI design value != observed evidence;
- multistage finite belief policy != general POMDP or executed history;
- AIPW estimate != identification proof;
- robustness perturbation != hidden-confounding bound;
- heuristic partial graph != PAG/FCI/CPDAG theorem;
- dependence probability model != formal statistical independence;
- model/simulation output != observation;
- unknown cost != zero cost;
- higher mathematical resolution != semantic authority.

## Deployment check

After upgrade verify:

1. package version and MCP `SERVER_INFO.version` both equal `2.8.0`;
2. every V9 tool appears in `tools/list`;
3. `athena://collective/v9` appears and reads as `COLLECTIVE_RUNTIME_V9`;
4. legacy V1–V8 tests pass;
5. constructive V9 tests pass;
6. adversarial V9 tests pass;
7. stdio `python -m athena_mcp` crosses V8 finite belief plus V9 Gaussian belief registration/observation, EVPI/EVSI, AIPW and exact emission verification;
8. canonical brain promotion occurs only after the exact final runtime/version/documentation head passes CI.
