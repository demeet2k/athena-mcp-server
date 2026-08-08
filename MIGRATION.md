# ATHENA Runtime Migration

## Active-tree provenance

The active `master` tree was rebuilt during the 2026-08-07 rebuild. Older state remains in Git history/archive and is never canonical merely because it exists.

Legacy admission remains:

`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

---

# 2.8.0 -> 2.9.0

`athena-canonical-mcp 2.9.0` adds **Collective Probabilistic V10** on top of the V1–V9 organization/memory/learning/ecology/science/discovery/dual-control/belief/inference stack.

The migration is additive. Existing V8/V9 finite/Gaussian beliefs, causal estimates, graph hypotheses and evidence-dependence surfaces are not silently converted into V10 GP, PC-stable, TMLE, POMDP or calibrated-dependence objects.

## New persistent V10 surfaces

V10 creates lazily and non-destructively:

- `collective_v10_gp_models`
- `collective_v10_dependence_labels`
- `collective_v10_dependence_models`.

A GP model is a separate explicitly registered object with fixed kernel/noise hyperparameters and its own observed rows.

Dependence labels are externally supplied calibration observations. Historical witness metadata or V9 dependence probabilities are **not** silently relabeled as ground truth.

## New V10 MCP tools

- `athena_gp_register`
- `athena_gp_state`
- `athena_gp_observe`
- `athena_gp_predict`
- `athena_pc_stable_discover`
- `athena_causal_tmle_binary`
- `athena_sensitivity_evalue`
- `athena_pomdp_solve`
- `athena_evidence_dependence_observe`
- `athena_evidence_dependence_fit`
- `athena_evidence_dependence_predict`.

New resource:

`athena://collective/v10`.

## Gaussian-linear -> fixed-kernel GP migration

V9 Gaussian belief remains the correct state for a finite-dimensional linear observation model:

`theta|D ~ N(mu,Sigma)`.

V10 GP is a different nonlinear model family over observed input-output rows with a declared fixed RBF kernel:

`k(x,z)=sigma_f^2 exp(-||x-z||^2/(2 l^2))`.

No V9 Gaussian belief is silently converted into GP training data or hyperparameters.

A V10 GP must be explicitly registered. Only `athena_gp_observe` appends observed targets. `athena_gp_predict` is read-only.

The exact posterior calculation is conditional on the declared fixed kernel/noise values and the bounded stored dataset.

`FIXED_KERNEL_GP != GENERAL_WORLD_TRUTH`.

## Structure migration

V7 association skeletons, V8 bootstrap stability and V9 heuristic partial graphs remain valid scoped hypotheses.

V10 `athena_pc_stable_discover` adds a separate bounded Gaussian PC-stable procedure:

- Fisher-z conditional-independence testing;
- stable-level edge removals;
- explicit separation sets;
- collider orientation;
- bounded Meek R1/R2 closure;
- conditioning depth <=3 and variables <=10.

Existing V9 `o-o` edges are not retroactively relabeled as PC-stable output. PC-stable output itself is not FCI/PAG hidden-confounder discovery and creates no canonical JSPACE edge.

## AIPW -> TMLE migration

V9 AIPW remains available for binary treatment with numeric outcome under its declared nuisance models/assumptions.

V10 adds a separate binary-treatment/binary-outcome TMLE surface with cross-fitted logistic nuisance fits, propensity clipping, a logistic targeting fluctuation, targeted counterfactual risks and an influence-curve interval.

Historical AIPW estimates are not reclassified as TMLE estimates. Identification remains a separate prerequisite/authority surface.

`TMLE_ESTIMATE != IDENTIFICATION_PROOF`.

Declared latent-confounding risk fails closed.

## Sensitivity migration

V9 leave-one-adjustment robustness remains an observed-specification perturbation diagnostic.

V10 adds the standard risk-ratio E-value metric:

`E=RR+sqrt(RR(RR-1))`

for `RR>=1`, with reciprocal handling for protective associations and optional closest-to-null CI limit.

Do not rename old robustness shifts as E-values; these are different sensitivity objects.

`E_VALUE != UNIVERSAL_HIDDEN_CONFOUNDING_BOUND`.

## Finite multistage policy -> POMDP migration

V9 finite-belief policy recursion operates over model likelihood/utility branches without hidden-state transition dynamics.

V10 `athena_pomdp_solve` is a distinct finite-state control model with:

- hidden-state belief;
- action reward by state;
- state transitions;
- observation emissions;
- Bayes filtering;
- finite horizon `H<=4`.

No V9 policy tree is automatically migrated into a POMDP model.

Exact certificate is returned only when the entire supplied finite action/observation tree completes before the node limit:

`EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON`.

A node-limited run returns `NODE_LIMIT_NO_EXACT_CERTIFICATE`.

`FINITE_POMDP_CERTIFICATE != INFINITE_HORIZON_OR_REAL_WORLD_OPTIMALITY`.

## Evidence-dependence calibration migration

V9 can calculate dependence probabilities from caller-declared coefficients.

V10 adds explicit supervised calibration:

1. record externally labelled pair examples;
2. require at least 20 labels with complete shared features;
3. fit a scoped logistic dependence model;
4. expose training log loss/accuracy;
5. predict under that fitted scope.

V9 model outputs cannot become V10 calibration labels automatically.

Predictions never create labels or retrain themselves.

`LEARNED_DEPENDENCE_MODEL != FORMAL_INDEPENDENCE_PROOF`.

## Authority compatibility

2.9.0 does not weaken earlier authority planes:

- semantic writes retain VID/event-head authority;
- Git writes retain Git-head CAS;
- topology retains topology-version CAS;
- V3 policy retains policy-version CAS;
- projection/compensation retain explicit recovery authority;
- V4–V10 predictions, posteriors, graph hypotheses, causal estimates, sensitivity metrics, plans and evidence-dependence state remain evidential/advisory unless separately promoted under canonical mutation law.

A very narrow GP posterior variance, highly stable PC orientation, small TMLE p-like interval, large E-value, exact finite POMDP certificate or high learned dependence probability does not silently mutate canon.

## V10 migration firewall

- fixed-kernel GP != general world truth;
- GP posterior != observation;
- bounded PC-stable != FCI/hidden-confounder discovery;
- TMLE estimate != identification proof;
- E-value != universal hidden-confounding bound;
- finite POMDP certificate != infinite-horizon/real-world optimum;
- learned dependence probability != formal statistical independence;
- model/simulation output != observation;
- unknown cost != zero cost;
- computational exactness within a model != correctness of the model.

## Deployment check

After upgrade verify:

1. package version and MCP `SERVER_INFO.version` both equal `2.9.0`;
2. every V10 tool appears in `tools/list`;
3. `athena://collective/v10` appears and reads as `COLLECTIVE_RUNTIME_V10`;
4. legacy V1–V9 tests pass;
5. constructive V10 tests pass;
6. adversarial V10 tests pass;
7. stdio `python -m athena_mcp` crosses V9 continuous inference plus V10 GP observation/prediction, TMLE, E-value, exact finite POMDP and exact emission verification;
8. canonical brain promotion occurs only after the exact final runtime/version/documentation head passes CI.
