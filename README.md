# ATHENA Canonical MCP v2.2 — Executable Polycoordinate Crystal Runtime

A from-first-principles ATHENA Git/MCP nervous substrate.

Core law: one canonical state, explicit versions, exact ancestry, stale-write rejection, typed JSPACE graph/hypergraph, SCALE, KC144, open-world coordinate atlas, mathematical-object registry, executable transform calculus, public liminal telemetry, exact final-emission bytes, lossless RETURN, and a cost-aware collective-intelligence controller with persistent organizational memory.

## Runtime cycle

`HYDRATE → RECONSTRUCT → PHEROMONE/ANTIBODY MEMORY → JSPACE → SCALE → KC144/POLYATLAS → CUT/MAXDEV → COLLECTIVE PLAN → RGO CALIBRATE → DEMAND ALLOCATE → BUILD/BRIDGE → QUORUM/VERIFY → HEALTH/RESTRUCTURE → JSPACE ALARM/TOPOLOGY CAS → LIFECYCLE/PHEROMONE → OBSERVED RGO → FINALIZE_OUTPUT → VERIFY → CONDITIONAL COMMIT → GLOBAL DIFFUSION`

## Identity

`SID != OID != MID != VID != CID != EID != CRYS != ENV`.

## Stale state

Semantic CAS: `expected VID == current VID` else `STALE_TARGET`.

Git CAS: `expected Git HEAD == current Git HEAD` else `STALE_GIT_HEAD`.

Collective topology CAS: `expected topology version == current topology version` else `STALE_TOPOLOGY`.

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

## Run

`python -m athena_mcp --db ./state/athena.db`

MCP protocol revision: `2025-11-25`.
