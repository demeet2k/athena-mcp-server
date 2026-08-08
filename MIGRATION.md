# ATHENA Unified Migration Law — v3.2 / Collective V1–V13

Migration distinguishes **content**, **runtime integration**, **release identity**, **verification**, **authority**, **attestation**, **trusted qualification**, **control-plane state**, and **Git ancestry**.

`UNKNOWN / LEGACY != GARBAGE`

`FILE EXISTS != ORGAN INTEGRATED`

`CONTENT COPIED != LINEAGE MERGED`

`GREEN OLD HEAD != QUALIFIED NEW HEAD`

`CALLER_ATTESTATION != TRUSTED_EXTERNAL_VERIFICATION`

`ATTESTED_READY != QUALIFIED`

`CI PASS != LIVE TRUSTED PROMRUN`

`RUNTIME STATE != GITHUB CONTROL-PLANE STATE`.

## 1. Current executable target

`athena-canonical-mcp 3.2.0`

`ATHENA.RUNTIME.UNIFIED.8`

One composed runtime contains base CCR/JSPACE/SCALE/KC144/polycoordinate/crystal/Git, resident Collective V1–V4, lazy V5–V13 science/inference/control layers, AOR/Y1/EQ/developmental organs, CYCLE.1, SCHEMA.2/OMEGA.1/RECON.1, SELFTEST/STARTUP/SURFACE/COMPOSITION/PROMOTION.2 and final-emission verification.

## 2. Ancestry law

Pre-rebuild state remains in Git history. Legacy existence is not canonicality.

A successor branch must preserve current master ancestry. If master moves while the successor is being developed:

`FETCH(master) -> CLASSIFY(delta) -> BRAID -> FOUR_GATE_CI -> RACE_CHECK`.

Copying current files is not equivalent to preserving parent history. Do not reuse CI evidence from an older head for a newer head.

## 3. Schema / persistence

SCHEMA.2 remains additive and receipt-bearing. Unknown legacy tables/rows survive unless an explicitly authorized migration owns them.

V12 and V13 add no required persistent SQL table for their new model outputs. QMC particles, FITC predictions, joint designs, structural candidates, longitudinal estimates/policy values and robust resource plans are read-only computation surfaces unless an existing explicit observation/persistence operator owns a write.

`NO_NEW_TABLE != NO_NEW_CAPABILITY`.

PROMOTION.2 reuses the versioned `promotion_runs` ledger and preserves PROMOTION.1 replay semantics separately.

## 4. Authority firewall

Canonical Y1 remains `athena_claim_*`. Science-shadow replication/falsification remains `athena_discovery_claim_*`.

`SCIENCE_SHADOW --explicit witnessed evidence route--> Y1 consideration`

never

`SCIENCE_SHADOW --adjacency--> Y1 mutation`.

V7–V13 model/control surfaces cannot mutate Y1 merely because a prediction, estimate, policy, graph or resource plan looks strong.

## 5. Observer-effect law

OMEGA/schema status/SELFTEST/STARTUP/SURFACE/manifest/MAXDEV/benchmark/Git-status/reconstruction and model-design/prediction calls must not mutate the state they inspect merely by observation.

`OBSERVE != TRAIN`.

`DESIGN != OBSERVATION`.

## 6. Live-organ integration rule

A successor organ is live only when:

1. schema advertised;
2. dispatcher route exists;
3. resident/lazy classification is explicit;
4. resource surface exists;
5. SURFACE.2 requires it;
6. COMPOSITION.2 describes it correctly;
7. constructive/adversarial/unified tests exist;
8. CI has a dedicated stage when constitutionally important;
9. subprocess smoke crosses representative behavior;
10. manifest and OMEGA describe it;
11. README/ARCHITECTURE/MIGRATION/current unified spec agree.

Documentation drift is a CI-visible defect.

## 7. Preserved V10–V12 semantics

V10 fixed-kernel GP / bounded PC / TMLE / POMDP remains V10 state.

V11 GP hyperfit winner / supplied-DAG latent projection / stacked TMLE / finite-model BA-POMDP remains V11 state.

V12 finite-grid GP hyperposterior / BMA / subset-GP / bounded PAG / two-timepoint g-formula / independent-Gaussian chance plan remains V12 state.

No historical result is silently relabelled as the stronger V13 algorithm.

## 8. V12 -> V13 — finite model sets to bounded continuous/robust approximations

V13 is a **bounded successor**, not proof that the general forms are solved.

### 8.1 Finite hyperparameter grid -> continuous-domain QMC

V12:

`pi(theta)=sum_i w_i delta(theta_i)` on an explicit finite grid.

V13 `athena_gp_hyperqmc` instead samples a declared positive continuous hyperparameter box in log coordinates using deterministic Halton points and reweights them by exact bounded GP marginal likelihood.

`QMC_CONTINUOUS_HYPERPOSTERIOR != EXACT_CONTINUOUS_HYPERPARAMETER_BAYES`.

Existing V12 finite posterior rows/outputs are not retroactively interpreted as continuous quadrature.

### 8.2 Subset approximation -> FITC inducing approximation

V12 subset-GP performs exact GP inference on a selected observed subset.

V13 FITC retains all observations through a diagonal conditional-residual correction while using a smaller inducing representation and returns query-level error against the exact current bounded GP.

`FITC_INDUCING_GP != FULL_GP_POSTERIOR_OR_VARIATIONAL_OPTIMUM`.

`QUERY_REFERENCE_ERROR != GLOBAL_ERROR_GUARANTEE`.

### 8.3 Decision EVSI -> joint decision + model information

V13 `athena_gp_joint_design` keeps downstream decision improvement and expected hypermodel entropy reduction as separate reported quantities before explicit scalar weighting.

No hypothetical measurement becomes a GP row.

### 8.4 Bounded PAG -> bounded FCI-lite

V13 expands observational conditioning to all observed-variable subsets up to a declared small order, retains separation sets and applies collider/limited propagation rules.

`BOUNDED_FCI_LITE != FCI_RFCI_PAG_THEOREM`.

Complete possible-d-sep, discriminating paths, selection-bias semantics and PAG completeness remain unresolved. Existing V9/V10/V12 graph objects stay typed as the algorithm that produced them. No V13 call writes JSPACE.

### 8.5 Parametric g-formula -> history-preserving sequential targeting

V13 `athena_longitudinal_tmle` targets a binary two-timepoint static regime over

`X -> A1 -> L1 -> A2 -> Y`.

Critical migration invariant:

`STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION`.

Stage 2 evaluates target A2 while retaining each row's observed A1/L1 history; the stage-2 clever covariate is zero when observed A1 is incompatible with target A1. Stage 1 then learns the targeted pseudo-outcome over observed A1 before evaluating target A1.

`TWO_TIMEPOINT_SEQUENTIAL_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM_OR_IDENTIFICATION_PROOF`.

Declared latent confounding fails closed.

### 8.6 Static regimes -> deterministic dynamic two-timepoint policies

V13 supports deterministic static or linear-threshold policies:

`A1=pi1(X)`

`A2=pi2(X,A1,L1)`.

Value is computed through the bounded parametric longitudinal model.

`DYNAMIC_GFORMULA_POLICY_VALUE != GENERAL_OFF_POLICY_CAUSAL_VALUE`.

Policy ranking remains PLAN_ONLY.

### 8.7 Independent Gaussian resources -> correlated Gaussian + ellipsoidal mean ambiguity

V13 accepts caller-declared covariance `Sigma_r` and per-candidate mean uncertainty `u_i` with radius `rho`:

`mu_r(S)+rho||u_r(S)||_2+z_(1-alpha)sqrt(1_S^T Sigma_r 1_S) <= B_r`.

Small finite problems can be exhaustively enumerated under that declared model. Larger problems return greedy selection with no exact certificate.

`ELLIPSOIDAL_GAUSSIAN_ROBUST_PLAN != GENERAL_DISTRIBUTIONALLY_ROBUST_OPTIMIZATION`.

No plan spends resources by itself.

## 9. OMEGA / manifest migration

OMEGA remains `ATHENA.OMEGA.1` as a versioned whole-state projection ABI while its contents expand. It now names lazy V5–V13 surfaces.

Live architecture becomes:

`ATHENA.RUNTIME.UNIFIED.8`.

Compatibility retains `.1` through `.7`.

Manifest navigation/cycle/claim-namespace law/MAXDEV/unresolved boundaries all advance to V13 while retaining PROMOTION.2 trust separation.

## 10. CI migration

Release gate remains:

`syntax ∧ unit ∧ critical-invariants ∧ dependent-smoke`.

The critical lattice now contains a dedicated:

`V13 robust continuous-bayes causal-control and authority boundaries`

stage running constructive, adversarial and unified V13 tests.

Smoke runs only after syntax, unit and critical gates pass and traverses V13 QMC/FITC/joint-design/FCI-lite/longitudinal/policy/resource behavior plus state/AOR/fail-closed CYCLE/final emission/PROMOTION.2 readiness.

## 11. PROMOTION.2

MCP-visible exact-head caller packets may reach `ATTESTED_READY` only.

Current `QUALIFIED` additionally requires a genuinely host-internal trusted verifier receipt binding the exact head and exact CI/smoke references.

The V13 runtime intentionally **does not expose** a caller-callable trusted verifier. Such an endpoint would let the same trust domain mint its own independent verification and would recreate the boundary PROMOTION.2 was designed to prevent.

`UNRESOLVED_EXTERNAL_PROMOTION_VERIFIER` remains correct until a real host/control-plane verifier exists.

## 12. Final release / private canonical pin

The final merged public `master` SHA must independently pass all four gates. Feature-branch PASS is insufficient.

Only after exact merged-master readback and CI PASS may the private canonical brain pin the runtime. The private brain may cite GitHub Actions as external evidence but may not claim a runtime PROMOTION.2 `QUALIFIED` receipt without a real trusted verifier receipt.

## 13. External control-plane boundary

Branch protection, repository settings/description, tags, Releases, PR/merge state and trusted promotion verification remain external control-plane state. They require actual GitHub/host APIs and are never inferred from runtime OMEGA/SELFTEST/CI or caller attestations.
