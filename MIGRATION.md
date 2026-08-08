# ATHENA Runtime Migration

## Active-tree provenance

The active `master` tree was rebuilt during the 2026-08-07 rebuild. Older state remains in Git history/archive and is never considered canonical merely because it exists.

Legacy admission remains:

`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

---

# 2.6.0 -> 2.7.0

`athena-canonical-mcp 2.7.0` adds **Collective Belief V8** on top of the V1–V7 organization/memory/learning/ecology/science/discovery/dual-control stack.

The upgrade is additive. No canonical object, JSPACE edge, old policy state, old Bayesian model, old transition observation or science-shadow witness is bulk-rewritten into a stronger V8 meaning.

## New persistent V8 surfaces

V8 creates, lazily and non-destructively:

- `collective_v8_beliefs`
- `collective_v8_effect_estimates`.

Finite beliefs are separate from V5 Bayesian arm posteriors. Existing Bayesian observations are not silently converted into discrete model probabilities.

Effect-estimate records are separate from V6/V7 causal-identification records. An old identification witness does not become an effect estimate until explicit data/model inputs are supplied.

## New MCP tools

- `athena_belief_register`
- `athena_belief_state`
- `athena_belief_observe`
- `athena_decision_evi`
- `athena_belief_dual_control`
- `athena_causal_effect_estimate`
- `athena_causal_structure_bootstrap`
- `athena_contingent_policy`
- `athena_evidence_spectral`.

New resource:

`athena://collective/v8`.

## Belief migration

A V8 belief is an explicit finite distribution over model IDs:

`sum_i p_i = 1`.

It is created only through `athena_belief_register`.

Historical V5/V6/V7 model scores, UCB values, graph candidates, Pareto ranks or science-shadow statuses are **not** automatically transformed into belief probabilities.

If a user wants those objects to become a V8 model set, the prior mapping must be declared explicitly.

Belief update requires one actual declared observation plus one likelihood value per current model:

`p_i' = p_i L_i / sum_j p_j L_j`.

The update path is `athena_belief_observe` only.

`PLANNED_OUTCOME != OBSERVED_OUTCOME`.

`LIKELIHOOD_MODEL != OBSERVATION`.

## EIG -> EVI migration

V5 expected information gain remains useful for hypothesis discrimination:

`EIG = H(prior)-E[H(posterior)]`.

V8 expected value of information is a different object:

`EVI = E[max_a EU(a|new evidence)] - max_a EU(a|current evidence)`.

Do not rename historical EIG values as EVI. EVI requires an explicit action-utility model because it measures decision improvement, not merely entropy reduction.

Use EIG when information itself is the design objective. Use EVI when the question is whether information can change the downstream action.

Both remain design surfaces until an experiment is executed.

## Dual-control migration

V7 `athena_dual_control_plan` uses state-model control reward + parameter-information proxy - predictive risk.

V8 `athena_belief_dual_control` is a separate depth-1 finite-belief operator using:

- immediate expected utility by model;
- expected best next-decision utility after possible outcomes;
- entropy information gain;
- risk/cost.

Neither state is silently migrated into the other. V7 remains preferable when action-conditioned physical/organizational state dynamics matter. V8 is preferable when a small explicit model set and decision-conditional observations dominate the uncertainty.

`BELIEF_DUAL_CONTROL != EXACT_BAYES_ADAPTIVE_POMDP`.

## Causal-effect migration

V6/V7 provide graph-relative identification checks. V8 adds narrow numeric estimators.

Identification and estimation remain separate records.

### BACKDOOR_LINEAR

Requires caller-declared adjustment variables and fits

`Y=beta0+tau*T+gamma^T Z+epsilon`.

### IV_WALD

Requires an instrument and estimates

`tau=Cov(Z,Y)/Cov(Z,T)`

only when the first-stage association is non-negligible.

### FRONTDOOR_LINEAR

Uses a linear product-of-coefficients mediation proxy.

These operations do not retroactively convert old identification statuses into numeric effects and do not prove the identification assumptions.

`CAUSAL_ESTIMATE != IDENTIFICATION_PROOF`.

Explicit declared latent-confounding risk returns an unidentified state rather than an estimate.

## Causal-structure bootstrap migration

V7 observational skeleton output remains a heuristic graph-hypothesis surface.

V8 bootstrap support repeatedly reruns that same procedure on resampled rows. Existing V7 skeletons are not retroactively assigned bootstrap support.

Bootstrap support means stability under that resampling/procedure:

`support(e)=count(e present)/B`.

It does not become a Bayesian causal edge posterior, a PC/FCI p-value, or a canonical JSPACE relation.

## Contingent-policy migration

V7 scenario/dual-control plans remain state-space plans.

V8 contingent policy is a finite outcome branch design:

`outcome -> hypothetical posterior -> best action`.

No old scenario branch is rewritten into V8 belief history.

A branch becomes historical evidence only after the outcome is actually observed and recorded through the explicit update surface.

## Evidence-diversity migration

V7 metadata effective-N remains valid.

V8 adds a spectral participation-ratio diagnostic over the same witness-similarity geometry:

`D_PR=Tr(S)^2/||S||_F^2`.

Historical witnesses remain unchanged. The new value is computed on read from their current metadata.

Missing comparable metadata defaults conservatively; it does not imply independence.

`SPECTRAL_DIVERSITY != FORMAL_STATISTICAL_INDEPENDENCE`.

## Authority compatibility

2.7.0 does not weaken any earlier authority plane:

- semantic writes retain VID/event-head authority;
- Git writes retain Git-head CAS;
- topology retains topology-version CAS;
- V3 policy retains policy-version CAS;
- projection/compensation retain their exact recovery authorities;
- V4–V8 learned/predictive/belief/design/estimation state remains evidence/control state only.

A V8 posterior with probability `0.999` still cannot silently mutate a canonical semantic object.

## V8 firewall during migration

Do not map existing state into stronger labels merely to populate V8:

- belief posterior != canonical truth;
- likelihood model != observation;
- EVI design != executed experiment;
- belief dual control != exact Bayes-adaptive POMDP;
- causal estimate != identification proof;
- bootstrap stability != causal-edge probability;
- contingent policy != execution history;
- spectral evidence diversity != formal independence;
- unknown cost != zero cost;
- scenario/model prediction != observation;
- science-shadow state != canonical truth.

## Deployment check

After upgrade verify:

1. package version and MCP `SERVER_INFO.version` both equal `2.7.0`;
2. all V8 tools appear in `tools/list`;
3. `athena://collective/v8` appears in resources and reads successfully;
4. legacy V1–V7 tests pass;
5. constructive V8 tests pass;
6. adversarial V8 tests pass;
7. `athena://transforms` still reads successfully;
8. stdio `python -m athena_mcp` crosses V8 belief registration, explicit belief observation, EVI, effect estimation, exact finalization and emission verification;
9. canonical brain promotion occurs only after the final runtime/version/documentation head passes CI.
