# ATHENA UNIFIED V11 — CURRENT OPERATING CONTRACT

Artifact role: human-readable operating contract for the executable unified runtime.

`release = athena-canonical-mcp 3.0.0`

`manifest = ATHENA.RUNTIME.UNIFIED.6`

`runtime = one composed Server`

Canonical whole-system coordinate:

`ATHENA_UNIFIED_V11=<CCR,JSPACE,SCALE,KC144,AOR,Y1,EQ,SX,RAG,HUG,GAP,FIELD,TRANSPORT,CYCLE,SCHEMA,OMEGA,RECON,SELFTEST,STARTUP,SURFACE,COMPOSITION,PROMOTION,COLLECTIVE(V1-V11),FINAL>`

This contract describes what the runtime currently exposes and what semantic shortcuts remain forbidden. It does not replace the machine-readable manifest or create authority by documentation alone.

## 1. Core separation law

`IDENTITY != COORDINATE != MODEL != EVIDENCE != AUTHORITY != EXECUTION != OBSERVATION != PERSISTENCE`

`UNKNOWN != 0`

`KNOWN != COMPARABLE`

`CONSENSUS != EVIDENCE`

`PHEROMONE / REUSE / POPULARITY != EVIDENCE != Y AUTHORITY`

`PLAN / SIMULATION / DESIGN != EXECUTION / OBSERVATION / RESULT`

`REACHABILITY != LOGICAL_PROOF != CAUSAL_PROOF`

`ATTEMPTED_WRITE != VERIFIED_PERSISTENCE`

The system may transport information between these planes only through explicit typed routes that preserve provenance and the distinction between predicted and observed state.

## 2. Authority namespace law

Canonical Y1 authority owns:

`athena_claim_*`

Discovery/replication/falsification science-shadow state owns:

`athena_discovery_claim_*`

The two RPC families are intentionally disjoint.

`SCIENCE_SHADOW --explicit witnessed evidence route--> Y1 consideration`

never:

`SCIENCE_SHADOW --alias/adjacency--> Y1 mutation`.

Y1 authority progression is typed and non-skippable:

`? → + → ! → #`

Support, execution, and canonicalization remain separate transitions.

## 3. State and CAS law

Three governing write domains are independent:

`CAS_OMEGA = CAS_semantic(VID) × CAS_git(HEAD) × CAS_topology(version)`.

Staleness in one domain must not mutate another.

V11 GP hyperparameter application additionally uses a local observation-count CAS:

`apply=true ⇒ expected_observation_count == live_observation_count`.

That model-local guard does not merge with semantic, Git, or topology authority.

State foundation:

- `SCHEMA.2` — additive verified migration;
- `OMEGA.1` — digest-addressed accessible whole-state projection;
- `RECON.1` — consulted/expected-source reconstruction receipt;
- `CYCLE.1` — resumable fail-closed developmental metabolism;
- `SELFTEST.1` — local organism-health synthesis;
- `STARTUP.1` — local readiness typing;
- `SURFACE.2` — required tool/resource union;
- `COMPOSITION.2` — one composed runtime and resident/lazy classification;
- `PROMOTION.1` — exact-head qualification predicate/ledger when actually invoked.

## 4. Resident and lazy substrate

Resident organizational substrate:

- CCR / JSPACE / SCALE / KC144 / polycoordinate / crystal ABI;
- Collective Runtime V1;
- Growth V1;
- Memory V2;
- Learning V3;
- Ecology V4;
- AOR / Y1 / EQ / developmental organs;
- state/governance organs.

Lazy model/science/control/adaptation surfaces instantiated on tool/resource access:

- Science V5;
- Discovery V6;
- Dual-Control V7;
- Finite Belief V8;
- Continuous Inference V9;
- Probabilistic V10;
- Adaptive V11.

`LAZY != ABSENT` and `LAZY != RESIDENT`.

SURFACE and regression tests certify discoverability/behavior without falsely claiming all model layers are permanently resident objects.

## 5. Developmental metabolism

Canonical developmental cycle:

`HYDRATE → RECONRUN/OMEGA → MEMORY → EXTRACT → RETRIEVE → HUG → GAP → FIELD → MEASURE/CALIBRATE → AUTHORITY/AOR → COLLECTIVE(V1-V11) → EXECUTE → VERIFY → LEARN → SUCCESSOR → COMPLETE`.

Missing prerequisites produce explicit `WAITING_*` state. The runtime never invents an executor, witness, measurement, HUG implementation, or observed result to keep the cycle moving.

AOR chooses **WHAT** is eligible. Collective organizes **HOW** capacity is used. Y1 governs canonical claim authority. EQ1 governs witnessed identity collapse.

## 6. V11 adaptive operator contract

V11 adds seven bounded operator families.

### GH — GP hyperparameter adaptation

`athena_gp_hyperfit`

Finite caller-declared RBF hyperparameter grid scored by exact Gaussian log marginal likelihood under the stored dataset.

Default: `GP_HYPERPARAMETER_DESIGN_ONLY`.

Application requires explicit CAS.

`MARGINAL_LIKELIHOOD_OPTIMUM != TRUE_KERNEL`.

### GV — GP decision EVSI

`athena_gp_decision_evsi`

Conditional-Gaussian Monte-Carlo value of hypothetical measurements for downstream finite decisions.

`GP_DECISION_EVSI != OBSERVATION`.

No hypothetical sample becomes a training row.

### LP — supplied-DAG latent projection

`athena_latent_project_admg`

Transforms an explicit acyclic DAG with declared latent/observed nodes into a restricted observed ADMG.

`SUPPLIED_DAG_LATENT_PROJECTION != DATA_DISCOVERED_PAG`.

Projection writes no canonical JSPACE edge.

### SL — stacked binary TMLE

`athena_causal_tmle_ensemble`

Binary-treatment/binary-outcome TMLE with bounded validation-weighted nuisance library. Identification assumptions remain explicit; declared latent-confounding risk fails closed.

`STACKED_TMLE != SUPER_LEARNER_THEOREM`.

### SS — RR sensitivity surface

`athena_sensitivity_rr_surface`

Two-dimensional caller-declared risk-ratio bias-factor surface.

`RR_BIAS_FACTOR_SURFACE != UNIVERSAL_HIDDEN_CONFOUNDING_BOUND`.

### BP — finite-model Bayes-adaptive policy

`athena_bapomdp_solve`

Bounded static uncertain model index plus finite physical state. Exact certification requires completion of the full supplied finite model/state/action/observation tree within the node cap and bounded horizon.

`FINITE_MODEL_BAPOMDP != GENERAL_BAYES_ADAPTIVE_CONTROL`.

Truncation removes the exact certificate. Output remains PLAN_ONLY.

### EU — evidence-dependence uncertainty

`athena_evidence_dependence_interval`

Laplace/Hessian logit uncertainty around an externally-labelled fitted V10 dependence model.

`LAPLACE_DEPENDENCE_INTERVAL != CALIBRATED_COVERAGE_GUARANTEE`.

Interval reads create no labels.

V11 coordinate fiber:

`COLLECTIVE_ADAPTIVE=<GH,GV,LP,SL,SS,BP,EU,L>`.

## 7. No-self-training law

Forbidden implicit feedback includes:

- prediction → observation;
- EIG/EVSI → evidence;
- rollout/scenario → observed trajectory;
- belief/policy → execution history;
- GP prediction/EVSI → GP training row;
- PC/partial/latent graph → JSPACE edge;
- dependence prediction/interval → calibration label;
- replication design → replication witness;
- model/shadow state → Y1 authority.

General firewall:

`MODEL_OUTPUT --X--> OBSERVATION_WITHOUT_EXTERNAL_WITNESS`.

## 8. Exact output ABI

`FINALIZE_OUTPUT → ENV(HEADER + BODY) → VERIFY_EMISSION`.

Visible bytes become a manifestation and coordinate surface. Finalized bytes are not silently mutated after their verification digest is created.

## 9. CI and qualification semantics

Repository CI gate:

`syntax ∧ full-unit-suite ∧ critical-invariants ∧ dependent-smoke`.

Critical invariants include repository-brain documentation consistency in addition to runtime/state/model firewalls.

A green GitHub head is external evidence for qualification; it is **not itself a live PROMRUN**. A PROMRUN may be claimed only when the runtime actually creates, persists, verifies, and replays that exact receipt.

`CI_PASS != LIVE_PROMRUN`.

## 10. Unresolved boundaries

These remain explicitly unresolved rather than being promoted by adjacency:

- `QHUG_SEMANTICS` — HUG ABI exists; canonical QHUG semantics require a registered/witnessed implementation;
- `STRONGER_CLOSURE` — GAP directed reachability is not deductive/causal closure;
- `MODEL_TO_AUTHORITY_BRIDGE` — model/shadow output requires explicit witnessed transport into Y1/AOR evidence lanes;
- `GENERAL_BELIEF_CONTROL` — bounded finite/Gaussian/POMDP/BAPOMDP layers are not general Bayes-adaptive control;
- `FORMAL_CAUSAL_DISCOVERY` — bootstrap/partial/PC/supplied-DAG projection are not hidden-confounder-complete FCI/RFCI discovery;
- `GENERAL_NONLINEAR_BAYES` — small-data RBF GP and finite-grid adaptation are not general kernel learning, sparse scalable GP, neural Bayesian inference, or world truth.

## 11. External control-plane boundary

GitHub branch protection, repository description/settings, tags, and Releases are external control-plane state.

They are not inferred from:

- OMEGA;
- SELFTEST;
- STARTUP;
- SURFACE;
- COMPOSITION;
- PROMOTION predicate tests;
- GitHub Actions success.

If a control-plane mutation capability is unavailable, the correct state is `UNRESOLVED_EXTERNAL_CONTROL_PLANE`, not a fabricated success claim.

## 12. Successor integration law

Do not invent V12 because V11 is complete.

A successor exists only when a real upstream/runtime delta exists. The integration loop is:

`GREEN_n → FETCH_REAL_DELTA → CLASSIFY → BRAID → SURFACE/OMEGA/MANIFEST/DOCS → CONSTRUCTIVE+ADVERSARIAL+UNIFIED TESTS → FOUR_GATE_CI → RACE_CHECK → MERGE → FOUR_GATE_MASTER_CI`.

If the base moves, recurse on the actual delta. If no real successor delta exists, attack residual defects instead of inflating the version number.
