# ATHENA Canonical MCP v2.3 — Executable Polycoordinate Crystal + Collective Ecology Runtime

A from-first-principles ATHENA Git/MCP nervous substrate.

Core law: one canonical state, explicit versions, exact ancestry, stale-write rejection, typed JSPACE graph/hypergraph, SCALE, KC144, open-world coordinate atlas, mathematical-object registry, executable transform calculus, public liminal telemetry, exact final-emission bytes, lossless RETURN, and a cost-aware collective-intelligence ecology with persistent memory, bounded learning, uncertainty-aware exploration and explicit causal/evidential boundaries.

## Runtime cycle

`HYDRATE → MEMORY/ANTIBODY/ELDER QUERY → REGIME → BUDGET/POLICY/POSTERIOR STATE → JSPACE → SCALE → KC144/POLYATLAS → CUT/MAXDEV → COLLECTIVE PLAN → RGO CALIBRATE → UCB EXPERIMENT SELECT → OPTIONAL ROLLOUT → BUDGET-AWARE SCHEDULE → EXECUTE/METER → QUORUM/VERIFY → OBSERVE → CAUSAL-CREDIT SURFACE → BANDIT/POLICY/WORKER-COST UPDATE → ADAPTIVE PHEROMONE/ANTIBODY/ELDER UPDATE → JSPACE ALARM/TOPOLOGY CAS/OPTIONAL PROJECTION SAGA → LIFECYCLE → FINALIZE_OUTPUT → VERIFY → CONDITIONAL COMMIT → GLOBAL DIFFUSION`

## Identity

`SID != OID != MID != VID != CID != EID != CRYS != ENV`.

## Authority / stale state

Semantic CAS: `expected VID == current VID` else `STALE_TARGET`.

Git CAS: `expected Git HEAD == current Git HEAD` else `STALE_GIT_HEAD`.

Collective topology CAS: `expected topology version == current topology version` else `STALE_TOPOLOGY`.

Learned organization policy CAS: `expected policy version == current policy version` else `STALE_POLICY`.

Topology-to-JSPACE projection is a recoverable saga over separate semantic/Git stores; it is explicitly **not** represented as one atomic distributed transaction.

## Exact visible text

Body, derived header, and final visible emission are separate manifestations. Final emission tokens use:

`KC144.G###.R##.C##/OID:.../VID:.../MID:.../P:#####/S:#####/T:#######/C:#########-#########`.

## Coordinate synesthesia

A coordinate list is not navigation. Transform modes separate `LOOKUP` from derivational operations. The runtime measures:

- `rho_nav` registered navigation density,
- `rho_exec` executable transform density,
- `rho_der` genuine derivational density.

Closed-loop holonomy is auto-measured only when every edge is derivational.

## Collective Runtime V1

The collective layer converts hive/swarm/pack/flock/herd/pod design priors into explicit control laws rather than decorative metaphors.

Core laws:

- `MAX_GROWTH != MAX_ACTIVITY`;
- `MAX_INTEGRATION != MAX_CONNECTIVITY`;
- `CONSENSUS_SCORE != EVIDENCE_SCORE`;
- preserve reserve capacity;
- stop adding workers when marginal output no longer exceeds marginal coordination cost;
- prefer strong modules plus sparse bridges to all-to-all connectivity;
- pair recruitment with inhibition, contradiction routing and attractor evaporation.

MCP tools:

- `athena_collective_plan` — select collective form, right-size active workers, allocate roles/topology/reserve, and emit `COLLECTIVE=<F,R,N,D,Q,C,O,H,L>`;
- `athena_collective_evaluate` — explicit cost/output vectors and return-on-group-organization;
- `athena_collective_quorum` — evidence-sensitive commitment with cross-inhibition;
- `athena_stigmergy_update` — reinforcement plus decay of artifact/routing priority;
- `athena_collective_health` — homeostatic overload detection and corrective actions.

Resource: `athena://collective/runtime`.

Specification: `spec/COLLECTIVE_RUNTIME.md`.

## Collective Growth Operators V1

- `athena_collective_allocate` — scarce workers follow demand × capability fit × available capacity;
- `athena_bridge_account` — infrastructure must repay build + maintenance + locked-capacity cost;
- `athena_collective_restructure` — FISSION/FUSE/HOLD from coordination, contagion, cohesion, complementarity and duplication pressure;
- `athena_dependency_alarm` — weighted decaying alarm waves over explicit influence/dependency edges;
- `athena_artifact_lifecycle` — KEEP_ACTIVE / KEEP_REFERENCE / DORMANT / QUARANTINE / PRUNE_REFERENCE while preserving required lineage.

Resource: `athena://collective/growth`.

Specification: `spec/COLLECTIVE_GROWTH.md`.

## Collective Runtime V2 — Persistent Organizational Memory

V2 promotes the highest-value advisory residuals into durable control state while preserving semantic/Git authority.

- `athena_pheromone_reinforce` / `athena_pheromone_field` — database-backed stigmergic priority with reinforcement and evaporation;
- `athena_jspace_alarm` — typed JSPACE relations become bounded invalidation transport; unknown relation orientation is ignored rather than fabricated;
- `athena_rgo_observe` / `athena_rgo_calibrate` — predicted-vs-observed RGO calibration;
- `athena_topology_get` / `athena_topology_apply` / `athena_topology_rollback` — versioned topology CAS, lineage-preserving FISSION/FUSE and rollback witnesses;
- `athena_failure_antibody_register` / `athena_failure_antibody_match` — detector + repair + evidence + regression/replay memory.

Resource: `athena://collective/v2`.

Specification: `spec/COLLECTIVE_RUNTIME_V2.md`.

## Collective Runtime V3 — Self-Learning Collective Ecology

V3 converts persistent memory into bounded empirical adaptation.

### ΩBUDGET

- `athena_budget_record` persists observable resource measurements;
- `athena_budget_summary` aggregates them plus MCP tool-call wall time automatically metered by dispatch;
- unavailable token/compute dimensions remain UNKNOWN.

### ΩPOLICY

- `athena_policy_state` / `athena_policy_score` expose a bounded learned organization policy;
- `athena_policy_update` requires explicit observed reward and current expected policy version;
- coefficients are bounded, regularized, and learned with a sample-count-decaying step size;
- `athena_policy_rollback` restores a prior before-state as a new witnessed version.

### ΩCOUNTERFACTUAL

- `athena_counterfactual_simulate` ranks candidate organizations using deterministic RGO, V2 calibration, V3 policy reliability, risk and budget pressure;
- result is always `SIMULATE_ONLY`.

### ΩELDER

- `athena_elder_observe` accumulates measured reuse/prediction/repair/regression/generalization outcomes with contradiction penalty;
- `athena_elder_rank` exposes defeasible longitudinal authority;
- age, repetition or popularity alone confer no seniority.

### ΩIMMUNE++

- `athena_antibody_record_outcome` records repair/regression outcomes and false positives;
- `athena_antibody_evolve` creates variants with family/parent lineage and optional expiry;
- `athena_antibody_select` combines semantic match with empirical reliability and status.

### ΩPHEROMONE^N

- `athena_pheromone_multiscale_reinforce` propagates reinforcement over declared `token → artifact → module → domain → system` coordinates with fixed distance attenuation;
- `athena_pheromone_multiscale_field` returns the resulting persistent scale fiber.

Resource: `athena://collective/v3`.

Specification: `spec/COLLECTIVE_RUNTIME_V3.md`.

## Collective Runtime V4 — Uncertainty-Aware Experimental Ecology

V4 attacks the next limiting factor: **how to explore, attribute, schedule and project without allowing the learning system to certify its own assumptions**.

### ΩREGIME + ΩBANDIT

- `athena_regime_resolve` maps observable task signals into an interpretable collective/task regime;
- `athena_bandit_select` uses a diagonal contextual-UCB approximation with local-regime posterior, reliability-weighted GLOBAL transfer, explicit uncertainty bands, and the V3 policy only as a prior when evidence is sparse;
- `athena_bandit_observe` updates posteriors only from explicit observed reward.

Law: `UCB != TRUTH`; exploration value can select an experiment without raising factual confidence.

### ΩCREDIT

- `athena_credit_assign` decomposes an observed outcome across interventions while carrying design-dependent causal confidence and preserving unattributed residual;
- `athena_credit_summary` exposes intervention credit history.

Randomization, control groups, direct measurement, isolation, replication and explicit counterfactuals increase causal confidence. Weak designs remain `ASSOCIATIONAL`; they are not relabeled causal because a learner wants a reward signal.

### ΩSCHEDULER

- `athena_worker_cost_observe` stores observable per-worker resources, budget pressure, useful output and empirical efficiency;
- `athena_budget_schedule` combines demand × capability fit × availability × measured efficiency while enforcing known budget feasibility;
- missing constrained costs are marked UNKNOWN and penalized for uncertainty rather than treated as free.

V4 additionally accepts observable CPU/GPU/energy/memory/network dimensions when callers can actually measure them.

### ΩDIFFUSION

- `athena_diffusion_observe` records observed cross-scale transfer utility plus evidence/causal-confidence metadata;
- `athena_diffusion_matrix` returns shrinkage-learned token/artifact/module/domain/system coefficients;
- `athena_pheromone_adaptive_reinforce` uses those coefficients for subsequent multiscale reinforcement.

Learned coefficients remain shrunk toward V3 distance priors until evidence accumulates.

### ΩREGRESSION

- `athena_antibody_execute_regressions` can execute stored repository-owned Python unittest witnesses of the exact form `tests/...py::TestCase::test_method`;
- traversal, shell syntax and arbitrary commands are rejected;
- execution uses `shell=False`, isolated Python mode and a hard timeout;
- pass/fail can feed the antibody evolution record.

This is a deliberately restricted repository subprocess, not an OS-level hermetic security sandbox.

### ΩROLLOUT

- `athena_rollout_simulate` evaluates explicit multi-step organization trajectories;
- each step exposes expected/lower/upper utility using counterfactual baseline plus empirical bandit information;
- only explicit `context_delta` values change simulated state;
- result is always `SIMULATE_ONLY`.

### ΩPROJECTION

- `athena_projection_prepare` derives and journals a topology→JSPACE structural projection plan;
- `athena_projection_status` exposes its recovery state;
- `athena_topology_project_jspace` performs topology-version + semantic-head + optional Git-head preflight, deduplicates structural edges, writes provenance attributes, and optionally checkpoints Git;
- failures before semantic writes become `ABORTED`; failures after partial semantic application become `COMPENSATION_REQUIRED`.

This is intentionally a recovery **saga**, because SQLite semantic state and Git are separate stores. V4 does not claim impossible atomic rollback across them.

Resource: `athena://collective/v4`.

Specification: `spec/COLLECTIVE_RUNTIME_V4.md`.

### V4 learning firewall

- `EXPLORATION_SCORE != EVIDENCE`
- `ASSOCIATION != CAUSATION`
- `COUNTERFACTUAL != OBSERVATION`
- `BANDIT_PREDICTION != REWARD`
- `REGIME_TRANSFER != IDENTITY`
- `UNKNOWN_COST != ZERO_COST`
- `DIFFUSION_POSTERIOR != CAUSAL_PATH`
- `REGRESSION_PASS != UNIVERSAL_PROOF`
- `ROLLOUT != COMMIT`
- `PROJECTION_SAGA != ATOMIC_TRANSACTION`

## Run

`python -m athena_mcp --db ./state/athena.db`

MCP protocol revision: `2025-11-25`.
