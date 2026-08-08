# ATHENA COLLECTIVE RUNTIME V4 — UNCERTAINTY-AWARE EXPERIMENTAL ECOLOGY

V4 extends the measured learning layer of V3 into an uncertainty-aware experimental control plane. It adds task-regime contextual bandits, explicit causal-confidence credit assignment, empirical per-worker budget scheduling, learned scale-to-scale pheromone diffusion, executable failure-antibody regression witnesses, uncertainty-banded multi-step organization rollouts, and a recoverable topology-to-JSPACE projection saga.

The architectural objective is not autonomous self-modification. It is **better experimental selection with stronger evidence accounting**.

---

## 0. Constitutional boundary

V4 MUST preserve the following distinctions:

`EXPLORATION_SCORE != EVIDENCE`

`ASSOCIATION != CAUSATION`

`COUNTERFACTUAL_PREDICTION != OBSERVATION`

`UCB != TRUTH`

`BANDIT_REWARD != SELF_PREDICTION`

`REGIME_TRANSFER != IDENTITY`

`UNKNOWN_COST != ZERO_COST`

`DIFFUSION_POSTERIOR != CAUSAL_PATH`

`REGRESSION_PASS != UNIVERSAL_PROOF`

`ROLLOUT != COMMIT`

`PROJECTION_SAGA != ATOMIC_TRANSACTION`

Canonical semantic mutation still uses expected-VID CAS. Git persistence still uses expected-Git-head CAS. Collective topology uses expected-topology-version CAS. V3 policy uses expected-policy-version CAS. V4 observational state may steer experiments, but it has no hidden canonical-authority bypass.

---

# 1. Task-regime state / ΩREGIME

A global policy can wash out meaningful local differences. V4 therefore derives an observable task regime from normalized task signals.

Let

`S = <hardness, uncertainty, divisibility, coupling, volatility, risk, migration, repetition, reuse, innovation, latency_sensitivity, evidence_sensitivity>`.

The existing collective-form selector yields

`F*(S) in {HIVE,SWARM,PACK,FLOCK,HERD,POD}`.

Five high-leverage dimensions are quantized into three explicit bins:

`b(x)=L for x<0.33`

`b(x)=M for 0.33<=x<0.67`

`b(x)=H for x>=0.67`.

The regime key is then

`R = <F*, b(hardness), b(uncertainty), b(coupling), b(divisibility), b(volatility), optional_domain>`.

This is an observable partition, not a new semantic identity. Nearby tasks can still transfer evidence through the hierarchy.

Tool:

- `athena_regime_resolve`

---

# 2. Hierarchical contextual bandit / ΩBANDIT

V3 learned a bounded logistic policy from explicit reward. V4 adds uncertainty-aware action selection.

For regime `r`, arm `a`, and normalized feature vector `x`, define an augmented vector

`phi = [1, x_1, ..., x_d]`.

V4 maintains a diagonal ridge-style posterior approximation:

`A_j = 1 + sum_t w_t phi_(t,j)^2`

`b_j = b_(0,j) + sum_t w_t phi_(t,j) r_t`.

The coefficient estimate is

`theta_j = b_j / A_j`.

The raw predicted mean is normalized by feature dimension:

`mu_local = clip((sum_j theta_j phi_j)/sqrt(max(1,d+1)),0,1)`.

Diagonal posterior uncertainty is

`sigma_local = min(1, sqrt(sum_j phi_j^2/A_j)/sqrt(max(1,d+1)))`.

The same observed reward also contributes, with bounded transfer weight, to a `GLOBAL` arm posterior. For local sample count `n_r` and transfer constant `tau`:

`rho_r = n_r/(n_r+tau)`.

When both local and global evidence exist:

`mu = rho_r mu_local + (1-rho_r) mu_global`

`sigma^2 = rho_r^2 sigma_local^2 + (1-rho_r)^2 sigma_global^2`.

If the new regime has no local observations, global evidence may seed it. If neither local nor global observations exist, the bounded V3 organization policy is used as a prior, with uncertainty inversely related to its empirical reliability.

Action-selection score:

`UCB(a|x,r) = clip(mu + alpha sigma,0,1)`.

Lower evidence band:

`LCB(a|x,r) = clip(mu - alpha sigma,0,1)`.

The selected arm is

`a* = argmax_a UCB(a|x,r)`.

Crucially, the UCB is an **experiment-selection score**, not an evidence score. It may prefer an uncertain arm because learning about that arm has option value.

Only an explicit observed reward may update the posterior:

`prediction -> no update`

`counterfactual -> no update`

`UCB -> no update`

`observed reward -> update`.

Tools:

- `athena_bandit_select`
- `athena_bandit_observe`

---

# 3. Causal-confidence credit assignment / ΩCREDIT

When multiple organizational changes occur before one measured outcome, assigning the entire outcome to every change creates false learning.

Let the observed normalized outcome change be

`DeltaY in [-1,1]`.

For intervention `i`, if an explicit counterfactual estimate without the intervention is available:

`raw_i = DeltaY - DeltaY_without_i`.

Otherwise V4 allows only weighted association:

`raw_i = DeltaY * evidence_weight_i * direction_i`.

Causal-confidence score is constructed from observable design evidence:

`c_i = 0.10`
`      + 0.22 I[randomized]`
`      + 0.22 I[control_group]`
`      + 0.16 direct_measurement`
`      + 0.10 temporal_isolation`
`      + 0.10 min(1,replications/5)`
`      + 0.10 I[counterfactual_available]`.

If no counterfactual is available, confidence is capped in the weak-design band.

Assigned credit:

`credit_i = clip(raw_i * c_i,-1,1)`.

Status:

- high-confidence counterfactual/design support => `CAUSAL_SUPPORTED`;
- intermediate support => `QUASI_CAUSAL`;
- weak support => `ASSOCIATIONAL`.

The runtime explicitly retains unattributed residual:

`Residual = DeltaY - sum_i credit_i`.

Residual is not an error to hide. It represents unmodeled causes, interactions, noise, and insufficient identification.

Tools:

- `athena_credit_assign`
- `athena_credit_summary`

Control law:

`multi-intervention outcome -> credit decomposition -> only justified credited reward may train action models`.

---

# 4. Measured per-worker resource metabolism / ΩSCHEDULER

V3 introduced organization-level resource observations. V4 adds worker-level empirical cost.

For worker `i` and completed task `j`, record observable resources:

`C_ij = <tokens, wall_time_s, tool_calls, compute_units, retrieval_ops, storage_bytes, human_attention_min, cpu_time_s, gpu_time_s, energy_j, memory_peak_mb, network_bytes>`.

Only measured dimensions are stored. Missing dimensions remain absent/UNKNOWN.

For explicit budget vector `B`, resource ratio is

`q_k = C_k / B_k` for `B_k > 0`.

Budget pressure:

`P = mean_k min(1,q_k)` over dimensions with explicit budget denominators.

When normalized useful output `U` is observed:

`Efficiency = U/(1+P)`.

Historical worker efficiency uses a smoothed estimate so one sample cannot dominate.

For task `j`, worker `i`, base demand-fit score remains

`D_j^alpha * Fit_ij^beta * Availability_i`.

V4 multiplies this by empirical efficiency and an observability/reliability factor:

`ScheduleScore_ij = D_j^alpha Fit_ij^beta Avail_i * (0.5+0.5 Eff_i) * U_i`.

Known resource estimates that exceed remaining budget make the assignment infeasible.

Unknown constrained resource dimensions do **not** become zero-cost dimensions. They create an uncertainty penalty.

Cost source is explicitly surfaced as:

- `EXPLICIT` — caller-provided expected resources;
- `MEASURED_HISTORY` — empirical worker history;
- `UNKNOWN` — no lawful estimate.

Tools:

- `athena_worker_cost_observe`
- `athena_budget_schedule`

---

# 5. Learned multiscale pheromone diffusion / ΩDIFFUSION

V3 used fixed distance attenuation across

`token -> artifact -> module -> domain -> system`.

V4 treats those coefficients as empirical but regularized quantities.

Distance prior:

`pi_(s,t)=1` for same scale,

`pi_(s,t)=0.72^d` for upward transfer by `d` scales,

`pi_(s,t)=0.55^d` for downward transfer by `d` scales.

For observed transfer utility `u_k in [0,1]` with evidence weight `e_k`:

`R = sum_k e_k u_k`

`E = sum_k e_k`.

With prior strength `kappa`:

`delta_hat_(s,t) = (kappa pi_(s,t) + R)/(kappa + E)`.

Reliability:

`rho_diff = E/(E+kappa)`.

Causal-confidence is stored separately from evidence weight. An observationally useful diffusion path is not silently upgraded into a causal dependency.

Adaptive pheromone deposit gain:

`gain_(s,t) = base_gain * delta_hat_(s,t)`.

Only declared lawful coordinates receive reinforcement; missing scales are never synthesized.

Tools:

- `athena_diffusion_observe`
- `athena_diffusion_matrix`
- `athena_pheromone_adaptive_reinforce`

---

# 6. Executable antibody regression witnesses / ΩREGRESSION

V2 stored regression references. V3 tracked pass/fail outcomes. V4 can execute a deliberately narrow witness class.

Accepted reference grammar:

`tests/<repo-owned-path>.py::TestCase::test_method`.

Rejected:

- shell syntax;
- arbitrary executable paths;
- `..` traversal;
- non-`tests/` files;
- arbitrary command strings.

Execution properties:

- current Python interpreter;
- isolated-mode `-I`;
- `shell=False`;
- fixed repository root;
- explicit test module/class/method only;
- hard timeout capped at 60 seconds;
- stdout/stderr tails persisted for audit.

Result states:

`PASS | FAIL | TIMEOUT | ERROR | INVALID_REF`.

When authorized, aggregate PASS/FAIL is fed back into the V3 antibody-evolution layer as `REGRESSION_PASS` or `REGRESSION_FAIL`.

This is a restricted repository-owned subprocess, **not an OS-level hermetic security sandbox**.

Tool:

- `athena_antibody_execute_regressions`

---

# 7. Uncertainty-banded multi-step rollouts / ΩROLLOUT

A one-step organization comparison cannot represent sequences such as

`small scout swarm -> focused pack -> integration hive`.

V4 therefore evaluates explicitly supplied trajectories.

For step `t`, V3 supplies a one-step counterfactual utility `c_t`.

When bandit history exists for the action arm, the empirical mean `m_t` enters according to empirical reliability `rho_t`:

`mu_t = (1-rho_t)c_t + rho_t m_t`.

Bandit uncertainty yields

`L_t = clip(mu_t - alpha sigma_t,0,1)`

`U_t = clip(mu_t + alpha sigma_t,0,1)`.

For discount `gamma`:

`Return_mean = sum_t gamma^t mu_t`

`Return_low = sum_t gamma^t L_t`

`Return_high = sum_t gamma^t U_t`.

Only caller-declared `context_delta` updates change the simulated context. V4 does not invent hidden state-transition dynamics.

Every rollout returns

`decision = SIMULATE_ONLY`.

Tool:

- `athena_rollout_simulate`

---

# 8. Topology -> JSPACE projection saga / ΩPROJECTION

V2 topology is a dedicated collective control plane. V4 adds a lawful bridge into canonical JSPACE.

Projection planning derives only explicit structural relations:

- active module => `Topology HAS_ACTIVE_MODULE Module`;
- fission child => `Child FISSIONED_FROM Parent`;
- fused module => `New FUSED_FROM Old`;
- explicit topology bridge => corresponding declared relation.

Projection plan records:

`P = <topology_id, topology_version, derived_edges, plan_digest>`.

Preparation requires exact expected topology version and records optional expected semantic event head and expected Git head.

A live projection preflights:

`expected_topology_version == current_topology_version`

`expected_semantic_eid == current_global_eid`

and, when Git checkpoint is requested,

`expected_git_head == current_git_head`.

Because the semantic SQLite state and Git working tree are separate transactional stores, V4 **does not claim a distributed atomic commit**.

Instead it uses a recovery saga:

`PREPARED`
`-> SEMANTIC_APPLIED`
`-> GIT_COMMITTED` (optional)
`-> COMPLETED`.

Failure before semantic application:

`ABORTED`.

Failure after any semantic write where a later stage cannot complete:

`COMPENSATION_REQUIRED`.

The exact before/after causal history remains inspectable; there is no fictional rollback claim.

Structural edges are deduplicated by `(src, relation, dst)` before creation.

Tools:

- `athena_projection_prepare`
- `athena_projection_status`
- `athena_topology_project_jspace`

The live projection tool can run `dry_run=true`, which journals a prepared plan but has no JSPACE authority.

---

# 9. Integrated Ω4 loop

`HYDRATE`
`-> MEMORY/ANTIBODY/ELDER QUERY`
`-> REGIME RESOLUTION`
`-> BUDGET STATE`
`-> COLLECTIVE PLAN`
`-> RGO CALIBRATION`
`-> V3 POLICY PRIOR`
`-> V4 UCB EXPERIMENT SELECTION`
`-> OPTIONAL MULTI-STEP ROLLOUT`
`-> BUDGET-AWARE WORKER SCHEDULING`
`-> EXECUTION + RESOURCE METERING`
`-> QUORUM/FALSIFICATION`
`-> OBSERVED OUTCOME`
`-> CAUSAL-CONFIDENCE CREDIT ASSIGNMENT`
`-> BANDIT UPDATE FROM JUSTIFIED OBSERVED REWARD`
`-> V3 BOUNDED POLICY UPDATE`
`-> WORKER-COST UPDATE`
`-> DIFFUSION-UTILITY UPDATE`
`-> ADAPTIVE PHEROMONE UPDATE`
`-> ANTIBODY REGRESSION EXECUTION/EVOLUTION`
`-> ELDER OUTCOME UPDATE`
`-> JSPACE INVALIDATION IF REQUIRED`
`-> TOPOLOGY CAS / OPTIONAL JSPACE PROJECTION SAGA`
`-> LIFECYCLE`
`-> FINALIZE / VERIFY / CANONICAL COMMIT`.

---

# 10. Learning firewall

V4 MUST fail closed on these substitutions:

1. `UCB -> factual confidence` — forbidden.
2. `counterfactual score -> observed reward` — forbidden.
3. `overall multi-change outcome -> full reward for every intervention` — forbidden.
4. `UNKNOWN worker resource -> zero cost` — forbidden.
5. `cross-regime transfer -> same-regime evidence` — forbidden.
6. `observed pheromone transfer utility -> causal dependency` — forbidden.
7. `regression PASS -> universal repair proof` — forbidden.
8. `rollout winner -> topology mutation` — forbidden.
9. `projection planning -> JSPACE mutation` — forbidden.
10. `SQLite + Git sequence -> atomic transaction` — forbidden.

---

# 11. V4 coordinate fiber

A materially governing Ω4 run may expose:

`COLLECTIVE_ECOLOGY = <RG,X,CR,WS,DF,RW,RO,PS,L>`

where:

- `RG` — resolved task regime;
- `X` — exploration/posterior state including mean/uncertainty/UCB;
- `CR` — causal-credit surface and unattributed residual;
- `WS` — worker scheduling/resource-budget surface;
- `DF` — learned diffusion coefficients/reliability;
- `RW` — regression witness/result surface;
- `RO` — rollout expected/lower/upper return;
- `PS` — projection-saga state;
- `L` — lineage/native context.

This coordinate is additive to `COLLECTIVE=<F,R,N,D,Q,C,O,H,L>` and `COLLECTIVE_LEARNING=<B,P,CF,E,A,MS,L>`.

---

# 12. V5 residuals — explicitly NOT claimed as implemented

1. full-covariance or nonlinear Bayesian contextual inference; V4 uses a transparent diagonal posterior approximation;
2. statistically identified causal effects without experimental/quasi-experimental evidence; V4 carries confidence and residual instead of pretending observational association is causal;
3. learned latent transition dynamics for rollouts; V4 changes context only through caller-declared transitions;
4. true distributed atomicity across SQLite semantic state and Git; V4 uses preflight CAS plus recovery saga;
5. OS-level hermetic sandboxing for regression witnesses; V4 uses a restricted repository-owned Python subprocess, not a full security boundary;
6. automatic exact token/GPU/CPU/energy telemetry when the MCP host does not expose those counters;
7. globally optimal multi-period worker scheduling; V4 uses a budget-aware greedy allocator with measured historical costs;
8. delayed long-horizon causal credit where effects emerge many cycles after an intervention;
9. interaction-effect estimation among simultaneous interventions beyond the explicit residual surface;
10. learned regime geometry itself; V4 regime partitions are deterministic and interpretable;
11. active experimental-design optimizer that chooses randomization/control assignments subject to safety and resource constraints;
12. formal compensation execution for partially applied projection sagas; V4 detects and journals `COMPENSATION_REQUIRED` but does not invent a universally safe inverse for arbitrary semantic edges.

These residuals are the legitimate Ω5 boundary. They must not be silently collapsed into claims of completion.
