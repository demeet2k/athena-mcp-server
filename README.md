# ATHENA Canonical MCP v2.2 — Executable Polycoordinate Crystal Runtime

A from-first-principles ATHENA Git/MCP nervous substrate.

Core law: one canonical state, explicit versions, exact ancestry, stale-write rejection, typed JSPACE graph/hypergraph, SCALE, KC144, open-world coordinate atlas, mathematical-object registry, executable transform calculus, public liminal telemetry, exact final-emission bytes, lossless RETURN, and a cost-aware collective-intelligence controller with persistent organizational memory and bounded empirical learning.

## Runtime cycle

`HYDRATE → RECONSTRUCT → PHEROMONE/ANTIBODY MEMORY → BUDGET/POLICY STATE → JSPACE → SCALE → KC144/POLYATLAS → CUT/MAXDEV → COLLECTIVE PLAN → RGO CALIBRATE → COUNTERFACTUAL RANK → DEMAND ALLOCATE → EXECUTE/METER → QUORUM/VERIFY → HEALTH/RESTRUCTURE → JSPACE ALARM/TOPOLOGY CAS → OBSERVED RGO/POLICY UPDATE → MULTISCALE PHEROMONE/ELDER/ANTIBODY UPDATE → LIFECYCLE → FINALIZE_OUTPUT → VERIFY → CONDITIONAL COMMIT → GLOBAL DIFFUSION`

## Identity

`SID != OID != MID != VID != CID != EID != CRYS != ENV`.

## Stale state

Semantic CAS: `expected VID == current VID` else `STALE_TARGET`.

Git CAS: `expected Git HEAD == current Git HEAD` else `STALE_GIT_HEAD`.

Collective topology CAS: `expected topology version == current topology version` else `STALE_TOPOLOGY`.

Learned organization policy CAS: `expected policy version == current policy version` else `STALE_POLICY`.

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

The growth layer turns the controller into an active organizational metabolism:

- `athena_collective_allocate` — scarce workers follow demand × capability fit × available capacity;
- `athena_bridge_account` — interfaces/infrastructure must repay build + maintenance + locked-capacity cost;
- `athena_collective_restructure` — FISSION/FUSE/HOLD from coordination, contagion, cohesion, complementarity and duplication pressure;
- `athena_dependency_alarm` — weighted, decaying failure/change waves only along explicit dependency/influence edges;
- `athena_artifact_lifecycle` — KEEP_ACTIVE / KEEP_REFERENCE / DORMANT / QUARANTINE / PRUNE_REFERENCE while preserving required lineage.

Resource: `athena://collective/growth`.

Specification: `spec/COLLECTIVE_GROWTH.md`.

## Collective Runtime V2 — Persistent Organizational Memory

V2 promotes the most valuable advisory residuals into durable, inspectable control state without bypassing canonical semantic/Git authority.

Persistent operators:

- `athena_pheromone_reinforce` / `athena_pheromone_field` — database-backed stigmergic priority with reinforcement and evaporation;
- `athena_jspace_alarm` — compile typed JSPACE relations into bounded invalidation transport; dependency relations reverse direction so a failed dependency reaches its dependents, while unknown relation semantics are ignored by default;
- `athena_rgo_observe` / `athena_rgo_calibrate` — record predicted versus observed RGO and shrink an online calibration surface toward measured downstream performance;
- `athena_topology_get` / `athena_topology_apply` / `athena_topology_rollback` — versioned collective-control topology with expected-version CAS, reversible before/after witnesses, FISSION/FUSE lineage preservation, and rollback as a new transaction;
- `athena_failure_antibody_register` / `athena_failure_antibody_match` — durable detector + repair + evidence + regression/replay memory for diagnosed failures.

Resource: `athena://collective/v2`.

Specification: `spec/COLLECTIVE_RUNTIME_V2.md`.

Authority law: collective V2 state may steer organization, but canonical semantic mutation still requires expected-VID CAS and Git persistence still requires Git-head CAS. Collective topology never silently rewrites JSPACE.

## Collective Runtime V3 — Self-Learning Collective Ecology

V3 converts persistent memory into bounded empirical adaptation while keeping learning subordinate to measurement, versioning and rollback.

### ΩBUDGET

- `athena_budget_record` persists observed tokens/wall time/tool calls/compute/retrieval/storage/human-attention dimensions when available;
- `athena_budget_summary` aggregates those observations plus MCP tool-call wall time automatically metered by dispatch;
- token or compute usage is never fabricated when the host does not expose it.

### ΩPOLICY

- `athena_policy_state` / `athena_policy_score` expose the current bounded learned organization policy;
- `athena_policy_update` requires an explicit normalized outcome and current expected policy version;
- coefficients are bounded, L2-regularized, and updated with a sample-count-decaying learning rate;
- `athena_policy_rollback` restores a prior before-state as a new version without erasing history.

### ΩCOUNTERFACTUAL

- `athena_counterfactual_simulate` ranks candidate organizations using deterministic RGO, V2 calibration, learned-policy reliability, risk and budget pressure;
- its result is always `SIMULATE_ONLY`; it cannot mutate topology or certify its own prediction.

### ΩELDER

- `athena_elder_observe` accumulates measured reuse, prediction, repair, regression and generalization outcomes with contradiction penalty;
- `athena_elder_rank` returns defeasible longitudinal authority;
- age, repetition or popularity alone confer no seniority.

### ΩIMMUNE++

- `athena_antibody_record_outcome` records repair/regression outcomes and false positives;
- `athena_antibody_evolve` creates variant families with parent lineage and optional expiry;
- `athena_antibody_select` combines semantic match with empirical repair/regression reliability and status.

### ΩPHEROMONE^N

- `athena_pheromone_multiscale_reinforce` propagates reinforcement over declared `token → artifact → module → domain → system` coordinates with distance attenuation;
- `athena_pheromone_multiscale_field` returns the resulting persistent scale fiber;
- missing coordinates are never synthesized and local success does not receive global-strength reinforcement.

Resource: `athena://collective/v3`.

Specification: `spec/COLLECTIVE_RUNTIME_V3.md`.

V3 authority law: `MEASURED_COST != ESTIMATED_COST`, `PREDICTION != OBSERVATION`, `LEARNED_POLICY != CANONICAL_TRUTH`, and `COUNTERFACTUAL != COMMIT`. Semantic/Git/topology/policy authority planes remain separate and versioned.

## Run

`python -m athena_mcp --db ./state/athena.db`

MCP protocol revision: `2025-11-25`.
