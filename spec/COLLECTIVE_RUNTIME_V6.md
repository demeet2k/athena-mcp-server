# ATHENA COLLECTIVE RUNTIME V6 — ACTIVE DISCOVERY + STOCHASTIC CONTROL

V6 extends the V5 causal-experimental layer with active experiment generation, distribution-shift awareness, conditional causal identification, higher-order factorial contrasts, multivariate transition uncertainty, receding-horizon control, exact small-model schedule certificates, fail-closed witness capsules, interval-Pareto experiment selection, and persistent replication/falsification science shadows.

The governing objective is **stronger discovery and control while making uncertainty, model assumptions, and authority boundaries harder to erase**.

## 0. Constitutional boundaries

- `NONLINEAR_BASIS != UNIVERSAL_INFERENCE`
- `OOD_SCORE != FACTUAL_FALSEHOOD`
- `GENERATED_EXPERIMENT != EXECUTED_EXPERIMENT`
- `BACKDOOR_SET != CAUSAL_TRUTH INDEPENDENT OF THE SUPPLIED DAG`
- `HIGHER_ORDER_CONTRAST != CAUSAL_INTERACTION WITHOUT IDENTIFICATION`
- `STOCHASTIC_TRANSITION_MODEL != WORLD_TRUTH`
- `MPC_PLAN != EXECUTION`
- `CERTIFIED_SCHEDULE != UNIVERSAL_OPTIMUM OUTSIDE THE DECLARED FINITE MODEL`
- `HERMETIC_CAPSULE != KERNEL/VM SECURITY PROOF`
- `PARETO_EXPERIMENT_SELECTION != SINGLE VALUE ORDERING`
- `REPLICATION_STATE != CANONICAL_SEMANTIC_TRUTH`
- `athena_claim_* != athena_discovery_claim_*`.

The last law is a deliberate unified-runtime correction. `athena_claim_*` belongs to AOR Y.1 canonical claim authority. V6 science-shadow claims use `athena_discovery_claim_*`. Science-shadow state may route experiments, falsifiers, and replication work; it cannot silently promote, demote, challenge, or canonicalize Y.1.

---

## 1. ΩNONLINEAR + ΩOOD

V6 uses a transparent degree-2 polynomial lift rather than labeling a bounded approximation as a Gaussian process or neural posterior:

`phi_2(x) = [x_i, x_i^2, x_i x_j]`.

The lifted vector feeds the tested V5 full-covariance Bayesian surface. Raw context features are tracked separately for regime-specific distribution-shift detection.

For regime `r`, empirical mean `mu_r`, ridge covariance `Sigma_r`, and observed dimension `d`:

`d_M(x) = sqrt((x-mu)^T Sigma^-1 (x-mu) / d)`.

The runtime combines normalized Mahalanobis distance with unseen-feature pressure into bounded `OOD(x)`. Predictive intervals widen under shift:

`width_V6 = width_V5 * (1 + lambda_OOD * OOD(x))`.

`athena_ood_score` is non-training. Only explicit observation calls update empirical context state.

Tools:

- `athena_ood_observe`
- `athena_ood_score`
- `athena_nonlinear_predict`
- `athena_nonlinear_observe`.

---

## 2. ΩEXPERIMENT-GENERATOR

V5 ranks supplied experiments. V6 may enumerate a caller-declared finite factor space.

A factor declares legal levels and may carry cost/risk/feasibility/ethics metadata. A hypothesis declares a prior, base binary-outcome probability, and explicit `factor=value` effects. For assignment `e`:

`P(Y=1 | H_i,e) = clamp(base_i + sum_j effect_i(factor_j=value_j))`.

Generated candidates are passed to V5 expected-information-gain ranking. Forbidden or ethics-blocked candidates remain visible in the audit surface instead of disappearing.

Tool: `athena_experiment_generate`.

All outputs remain `DESIGN_ONLY`.

---

## 3. ΩCAUSAL-ID — conditional back-door identification

`athena_causal_identify` answers a narrow formal question under a caller-supplied DAG: does an observed adjustment set satisfy the back-door criterion for treatment `T` and outcome `Y`?

The implementation removes treatment out-edges, excludes descendants of `T`, restricts to relevant ancestors, moralizes the graph, removes conditioned nodes, and evaluates undirected reachability. Candidate adjustment sets are enumerated by increasing cardinality within an explicit bound.

Possible statuses include:

- `IDENTIFIED_BACKDOOR`
- `UNIDENTIFIED_NO_BACKDOOR_SET`
- `UNIDENTIFIED_LATENT_CONFOUNDING_RISK`
- `UNIDENTIFIED_SEARCH_SPACE_TOO_LARGE`.

Thus:

`VALID_BACKDOOR_SET_UNDER_SUPPLIED_DAG != CAUSE_PROVEN_IN_REALITY`.

---

## 4. ΩHIGHER-ORDER

For intervention set `S={A_1,...,A_k}`, `2 <= k <= 4`, every `2^k` binary factorial cell is required.

`I_S = sum_(b in {0,1}^k) (-1)^(k-sum(b)) mu_b`.

Missing cells remain `UNIDENTIFIED`; they are never filled with zero. Numerical interaction confidence remains distinct from causal-design confidence.

Tool: `athena_interaction_higher_order`.

---

## 5. ΩSTOCHASTIC-TRANSITION

V6 reconstructs multivariate action-conditioned context deltas from actually observed V5 transition rows.

`Delta_t = x_(t+1) - x_t`

`m = sum w_t Delta_t / sum w_t`

`rho = W/(W+kappa)`

`Delta_hat = rho m`.

Empirical covariance is retained with explicit residual uncertainty while evidence is sparse. Unseen actions remain `UNSEEN_ACTION` rather than receiving invented dynamics.

Tool: `athena_transition_distribution`.

---

## 6. ΩMPC — receding-horizon planning

For state `x_t` and action `a`:

`V_t(a) = reward(a,x_t) - lambda_R * transition_uncertainty(a,x_t)`.

For horizon `H`:

`Return = sum_(t=0..H-1) gamma^t V_t(a_t)`.

Bounded beam search retains promising state/action sequences. Every result is `PLAN_ONLY`.

Execution law:

`PLAN_H -> EXECUTE_ONLY_FIRST_AUTHORIZED_ACTION -> OBSERVE_REAL_NEXT_STATE -> REPLAN`.

The planner never creates transition observations by itself.

Tool: `athena_mpc_plan`.

---

## 7. ΩCERTIFIED-SCHEDULE

For small declared task sets, V6 may exhaustively enumerate schedules under:

- dependency precedence;
- worker capability/capacity;
- durations and horizon;
- deadlines;
- explicit resource budgets.

If exhaustive search completes:

`certificate = EXACT_ENUMERATION_CERTIFIED`.

If search is truncated or the task set exceeds the exact-search bound, the certificate is removed and the result explicitly degrades to bounded/heuristic scheduling. Every budget-constrained resource dimension must be declared for every affected task:

`UNKNOWN_COST != ZERO_COST`.

Tool: `athena_schedule_certified`.

---

## 8. ΩHERMETIC-CAPSULE

`athena_witness_capsule` may execute the restricted repository-unittest grammar under Linux bubblewrap when available, with read-only repository bind, separate network namespace, isolated Python, and temporary scratch.

If bubblewrap is unavailable:

`status = HERMETIC_UNAVAILABLE`

and `executed=false`.

The V6 capsule never silently falls back to the weaker V5 witness cell when hermetic execution was requested.

---

## 9. ΩPARETO-BANDIT

A candidate `a` robustly dominates `b` only when its worst-case interval dominates `b`'s best-case interval across every directed objective, with strict improvement on at least one dimension.

Non-dominated candidates form an interval-possible frontier. Within that frontier, uncertainty may justify selecting a candidate for measurement without declaring it factually or normatively superior.

Tool: `athena_pareto_bandit_select`.

Result law: `EXPERIMENT_SELECTION_ONLY`.

---

## 10. ΩREPLICATION/FALSIFICATION GRAPH — unified namespace

V6 science-shadow claims are persistent evidence-navigation objects distinct from canonical Y.1 claims.

A shadow claim stores:

`<claim_id, claim_key, statement, scope>`.

A witness stores:

`<kind, result, confidence, independence_key, evidence, actor, time>`.

Kinds:

- `TEST`
- `REPLICATION`
- `FALSIFIER`.

Results:

- `SUPPORTS`
- `FALSIFIES`
- `INCONCLUSIVE`.

The `independence_key` prevents repeated events from automatically masquerading as independent replication.

Derived science-shadow states include:

- `UNRESOLVED`
- `PRELIMINARY_SUPPORT`
- `REPLICATED_SUPPORT`
- `FALSIFICATION_SIGNAL`
- `CONTESTED`.

Unified tools:

- `athena_discovery_claim_register`
- `athena_discovery_claim_witness`
- `athena_discovery_claim_state`.

Canonical authority remains separately exposed as:

- `athena_claim_register`
- `athena_claim_state`
- `athena_claim_promote`
- `athena_claim_challenge`
- `athena_claim_resolve_canonical_challenge`.

Firewall:

`DISCOVERY_SHADOW_STATE --X--> IMPLICIT_Y1_PROMOTION`

Any model/shadow result that should influence canonical authority must cross an explicit witnessed evidence/authority route.

---

## 11. Ω6 coordinate fiber

A materially governing V6 run may expose:

`COLLECTIVE_DISCOVERY=<NL,OOD,EG,CI,HI,TD,MPC,CS,HC,PB,RF,L>`

where `NL` nonlinear model state, `OOD` shift state, `EG` experiment generation, `CI` causal identification, `HI` higher-order interaction, `TD` transition distribution, `MPC` control plan, `CS` scheduling certificate, `HC` witness capsule, `PB` Pareto experiment surface, `RF` replication/falsification shadow, and `L` lineage/native context.

This fiber is additive to `COLLECTIVE`, `COLLECTIVE_LEARNING`, `COLLECTIVE_ECOLOGY`, `COLLECTIVE_SCIENCE`, AOR/Y.1, and OMEGA coordinates.

---

## 12. Residual boundary — explicitly not claimed by V6

V6 does **not** claim completion of:

1. scalable GP/neural posterior inference;
2. arbitrary-shift calibration guarantees;
3. causal graph discovery without declared assumptions;
4. front-door/IV/RDD/DiD identification operators;
5. scalable sparse high-order interaction discovery;
6. hidden-confounder-aware delayed causal attribution;
7. fully state-dependent stochastic world models;
8. globally certified large mixed-integer scheduling;
9. VM/microVM hostile-code isolation and attestation;
10. distributed atomic commits spanning semantic SQLite and Git;
11. policy-authorized Git revert execution;
12. continuous-space Bayesian/Pareto optimization;
13. formal estimation of replication independence;
14. host-level GPU/token/energy telemetry when the host exposes no such data;
15. automatic model-output promotion into Y.1 authority.

These remain successor work rather than being renamed complete because adjacent mechanisms exist.
