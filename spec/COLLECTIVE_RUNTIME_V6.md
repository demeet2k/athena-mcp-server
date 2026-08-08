# ATHENA COLLECTIVE RUNTIME V6 — ACTIVE DISCOVERY + STOCHASTIC CONTROL

V6 extends V5 causal experimental science with active experiment generation, distribution-shift awareness, conditional causal identification, higher-order factorial contrasts, multivariate transition uncertainty, receding-horizon control, exact small-model scheduling certificates, fail-closed OS witness capsules, Pareto experiment selection, and persistent replication/falsification science shadows.

The objective is **stronger discovery and control while making uncertainty/assumption boundaries harder to erase**.

## 0. Constitutional boundaries

`NONLINEAR_BASIS != UNIVERSAL_INFERENCE`

`OOD_SCORE != FACTUAL_FALSEHOOD`

`GENERATED_EXPERIMENT != EXECUTED_EXPERIMENT`

`BACKDOOR_SET != CAUSAL_TRUTH INDEPENDENT OF THE SUPPLIED DAG`

`HIGHER_ORDER_CONTRAST != CAUSAL_INTERACTION WITHOUT IDENTIFICATION`

`STOCHASTIC_TRANSITION_MODEL != WORLD_TRUTH`

`MPC_PLAN != EXECUTION`

`CERTIFIED_SCHEDULE != UNIVERSAL_OPTIMUM OUTSIDE THE DECLARED FINITE MODEL`

`HERMETIC_CAPSULE != KERNEL/VM SECURITY PROOF`

`PARETO_EXPERIMENT_SELECTION != SINGLE VALUE ORDERING`

`REPLICATION_STATE != CANONICAL_SEMANTIC_TRUTH`.

All earlier semantic/Git/topology/policy/projection authority surfaces remain unchanged.

---

## 1. ΩNONLINEAR + ΩOOD

V6 does not falsely label a small in-repository approximation as a Gaussian process or neural posterior. It adds a degree-2 polynomial feature map over normalized observable features:

`phi_2(x) = [x_i, x_i^2, x_i x_j]`.

This map is passed into the already-tested V5 full-covariance Bayesian surface.

An empirical OOD reference distribution is maintained independently over the raw features. For regime `r`, with sample mean `mu_r` and ridge covariance `Sigma_r`, V6 computes the normalized Mahalanobis distance

`d_M(x) = sqrt((x-mu)^T Sigma^-1 (x-mu) / d)`.

A bounded OOD pressure is derived from that distance and from the fraction of previously unseen features. The exact score is a routing/calibration signal, not a proof that an input or claim is false.

Nonlinear prediction inflates the inherited V5 interval when OOD pressure is high:

`width_V6 = width_V5 * (1 + lambda_OOD * OOD(x))`.

Only `athena_nonlinear_observe` updates the raw-feature OOD reference and nonlinear Bayesian reward state. Prediction and OOD scoring are non-training operations.

Tools:

- `athena_ood_observe`
- `athena_ood_score`
- `athena_nonlinear_predict`
- `athena_nonlinear_observe`.

---

## 2. ΩEXPERIMENT-GENERATOR

V5 ranks supplied experiments. V6 can enumerate experiments from a caller-declared finite factor space.

Each factor supplies:

- `name`;
- legal `levels`;
- optional per-level cost/risk/feasibility;
- optional forbidden levels.

Each hypothesis supplies:

- prior/weight;
- `base_p` for the binary observation model;
- explicit additive `factor_effects` keyed by `factor=value`.

For assignment `e`, V6 constructs only the likelihoods implied by that declared model:

`P(Y=1|H_i,e) = clamp(base_i + sum_j effect_i(factor_j=value_j))`.

It then delegates ranking to V5 expected-information-gain design.

Thus experiment **generation** means combinatorial generation over explicit factor/effect declarations. It does not mean a language model may invent arbitrary interventions and call them causally grounded.

Forbidden generated candidates are retained as `ETHICS_BLOCK` rather than silently disappearing from audit history.

Tool:

- `athena_experiment_generate`.

All results remain `DESIGN_ONLY`.

---

## 3. ΩCAUSAL-ID — conditional back-door identification

V6 accepts a caller-supplied directed causal graph and asks a narrow formal question:

> Does an observed adjustment set satisfy the back-door criterion for treatment `T` and outcome `Y` under this supplied graph?

The implementation:

1. removes outgoing edges from `T` to construct the back-door graph;
2. excludes descendants of `T` from adjustment candidates;
3. evaluates d-separation by restricting to ancestors of `{T,Y,Z}`, moralizing that ancestral graph, deleting conditioned nodes `Z`, and testing ordinary undirected reachability;
4. enumerates minimal sets by increasing cardinality up to the caller-supplied limit.

Possible statuses include:

- `IDENTIFIED_BACKDOOR`;
- `UNIDENTIFIED_NO_BACKDOOR_SET`;
- `UNIDENTIFIED_LATENT_CONFOUNDING_RISK`;
- `UNIDENTIFIED_SEARCH_SPACE_TOO_LARGE`.

Identification is conditional on:

- graph direction/meaning being correct;
- the graph representing the relevant causal variables;
- the caller's latent-confounding assumptions;
- the observed-node declaration;
- the finite adjustment search bound.

V6 therefore never compresses

`VALID_BACKDOOR_SET_UNDER_DAG`

into

`CAUSE_PROVEN_IN_REALITY`.

Tool:

- `athena_causal_identify`.

---

## 4. ΩHIGHER-ORDER

For intervention set `S={A_1,...,A_k}`, `2 <= k <= 4`, V6 requires all `2^k` binary factorial cells.

The k-th order inclusion-exclusion contrast is

`I_S = sum_{b in {0,1}^k} (-1)^(k-sum(b)) mu_b`.

No missing cell receives zero or an inferred value. If any required cell is absent:

`status = UNIDENTIFIED`.

Numerical contrast confidence is separated from causal design confidence. Unless design confidence is high enough, the contrast remains `ASSOCIATIONAL`.

Tool:

- `athena_interaction_higher_order`.

---

## 5. ΩSTOCHASTIC-TRANSITION

V5 learns independent feature delta summaries. V6 reconstructs a multivariate empirical delta distribution directly from the retained V5 observed transition rows.

For action `a` and shared numeric context vector:

`Delta_t = x_(t+1) - x_t`.

Weighted empirical mean:

`m = sum w_t Delta_t / sum w_t`.

Reliability shrinkage:

`rho = W/(W+kappa)`.

Returned mean delta:

`Delta_hat = rho m`.

Empirical covariance:

`Sigma_Delta = sum w_t (Delta_t-m)(Delta_t-m)^T / W`

with explicit residual prior uncertainty on the diagonal while reliability is incomplete.

Only features actually observed before and after are modeled. An unseen action returns `UNSEEN_ACTION` with empty learned deltas.

Tool:

- `athena_transition_distribution`.

---

## 6. ΩMPC — receding-horizon planning

V6 uses the multivariate transition surface in bounded receding-horizon search.

At state `x_t`, action `a` has model-predicted context transition and uncertainty. A risk-adjusted one-step planning value is

`V_t(a) = reward(a,x_t) - lambda_R * transition_uncertainty(a,x_t)`.

For horizon `H`:

`Return = sum_(t=0..H-1) gamma^t V_t(a_t)`.

A bounded beam retains the highest-valued candidate state sequences.

Every result is `PLAN_ONLY`.

The intended execution law is:

`PLAN_H -> EXECUTE_ONLY_FIRST_ACTION -> OBSERVE_REAL_NEXT_STATE -> REPLAN`.

No MPC plan writes transition observations, policy rewards, semantic facts or topology.

Tool:

- `athena_mpc_plan`.

---

## 7. ΩCERTIFIED-SCHEDULE

For small declared task sets V6 can exhaustively enumerate feasible schedules instead of returning an unqualified heuristic result.

Constraints include:

- task dependency precedence;
- worker capability fit;
- one active task per worker in the current model;
- durations;
- finite horizon;
- explicit resource budgets;
- deadline penalties.

The search keeps an admissible optimistic utility bound for pruning.

If complete enumeration finishes before the node bound:

`certificate = EXACT_ENUMERATION_CERTIFIED`

and the returned optimality gap within this declared finite model is zero.

If node search is truncated:

`certificate = NODE_LIMIT_NO_OPTIMALITY_CERTIFICATE`.

If the task set exceeds the exact-search limit, V6 explicitly falls back to V5 bounded beam scheduling and returns no exact certificate.

For an exact certificate every dimension constrained by the supplied budget must be declared in every task's resource-cost model. Missing constrained cost invalidates exact certification:

`UNKNOWN_COST != ZERO_COST`.

Tool:

- `athena_schedule_certified`.

---

## 8. ΩHERMETIC-CAPSULE

V5 strengthened repository-owned unittest execution but correctly reported `hermetic=false`.

V6 adds an optional stronger capsule using Linux bubblewrap when available. The capsule requires:

- tests-only reference grammar;
- read-only repository bind;
- temporary in-memory `/tmp`;
- separate network namespace (`--unshare-net`);
- isolated Python;
- no shell command path.

If `bwrap` is unavailable, V6 returns

`HERMETIC_UNAVAILABLE`

with `executed=false`.

It **never silently falls back** to the weaker V5 cell when the caller requested the V6 capsule.

When bubblewrap is used, `hermetic=true` means the declared namespace/mount controls were actually applied. It is not a proof against kernel, interpreter or native-runtime vulnerabilities.

Tool:

- `athena_witness_capsule`.

---

## 9. ΩPARETO-BANDIT

V5 computes a supplied finite Pareto frontier. V6 adds uncertainty-aware experiment selection on top of interval-valued objective metrics.

Candidate `a` robustly dominates `b` only if

`low_k(a) >= high_k(b)` for every max-oriented metric

(after sign conversion for min metrics), with strict inequality on at least one dimension.

Candidates not robustly dominated form an **interval-possible frontier**.

Within that possible frontier V6 may prioritize uncertainty-rich candidates for experimentation.

The result is

`EXPERIMENT_SELECTION_ONLY`.

This preserves two separations:

- Pareto tradeoffs remain plural;
- uncertainty may justify measuring an option without making it normatively or factually superior.

Tool:

- `athena_pareto_bandit_select`.

---

## 10. ΩREPLICATION/FALSIFICATION GRAPH

V6 introduces persistent science-shadow claims distinct from canonical semantic objects.

A science-shadow claim stores:

`<claim_id, claim_key, statement, scope>`.

Witnesses store:

`<kind, result, confidence, independence_key, evidence, actor, time>`.

Kinds:

- `TEST`;
- `REPLICATION`;
- `FALSIFIER`.

Results:

- `SUPPORTS`;
- `FALSIFIES`;
- `INCONCLUSIVE`.

The `independence_key` prevents multiple events from automatically masquerading as independent replication.

Summary states include:

- `UNRESOLVED`;
- `PRELIMINARY_SUPPORT`;
- `REPLICATED_SUPPORT`;
- `FALSIFICATION_SIGNAL`;
- `CONTESTED`.

A science-shadow state never silently edits the canonical object/registry. It routes future verification, re-evaluation and experiment design.

Tools:

- `athena_claim_register`;
- `athena_claim_witness`;
- `athena_claim_state`.

---

## 11. Ω6 coordinate fiber

A materially governing V6 run may expose:

`COLLECTIVE_DISCOVERY=<NL,OOD,EG,CI,HI,TD,MPC,CS,HC,PB,RF,L>`

where:

- `NL`: nonlinear polynomial-Bayesian surface;
- `OOD`: empirical distribution-shift state;
- `EG`: generated experiment/design surface;
- `CI`: conditional causal-identification state;
- `HI`: higher-order interaction state;
- `TD`: multivariate transition distribution;
- `MPC`: receding-horizon control plan;
- `CS`: schedule certificate/search state;
- `HC`: hermetic-capsule availability/result;
- `PB`: Pareto experiment-selection surface;
- `RF`: replication/falsification science-shadow state;
- `L`: lineage/native context.

This coordinate is additive to `COLLECTIVE`, `COLLECTIVE_LEARNING`, `COLLECTIVE_ECOLOGY` and `COLLECTIVE_SCIENCE`.

---

## 12. Ω7 residual boundary — not claimed by V6

1. actual GP/neural posterior inference and scalable nonlinear Bayesian training;
2. formal OOD/calibration guarantees under arbitrary distribution shift;
3. causal graph discovery from observational data without declared assumptions;
4. front-door/IV/RDD/DiD and other identification operators beyond supplied-DAG back-door checks;
5. scalable sparse higher-than-fourth-order interaction discovery;
6. hidden-confounder-aware delayed causal attribution;
7. fully stochastic state-dependent transition models rather than action-conditioned empirical delta summaries;
8. globally certified large mixed-integer scheduling beyond small exact finite enumeration;
9. VM/microVM-level hostile-code witness isolation and attested images;
10. distributed transactional commit protocols spanning semantic SQLite and Git;
11. policy-authorized Git revert/compensation execution;
12. continuous-space multiobjective Bayesian/Pareto optimization;
13. formal independence estimation for replication witnesses rather than caller-declared independence keys;
14. exact host-level token/GPU/energy telemetry when the host does not expose it.

These remain explicit successor work. V6 does not rename them complete because adjacent mechanisms now exist.
