# ATHENA NEXUS-4D Pressure Computer V1

## Status

`ATHENA.NEXUS4D.1` is a durable control-plane organ of the canonical single-`Server` runtime. It does not execute arbitrary code, merge branches, promote releases, or perform external actions. It compiles and advances bounded obligation machines whose state transitions remain subject to ATHENA authority, evidence, freshness, invariants, and optimistic concurrency.

## Canonical identity

The machine state is

\[
\mathfrak N_\tau=(G_\tau,X,O,\Lambda,E,A,Q,H),
\]

where `G` is the versioned typed topology, `X` durable state, `O` obligation lineage, `Λ` typed pressure, `E` evidence, `A` authority observations, `Q` queue/capacity state, and `H` the append-only replay ledger.

Forward state and evidence propagate through producer edges. Goal residuals, missing prerequisites, evidence deficits, repair demand, freshness invalidation, and integration/outcome obligations propagate backward. A node is selectable only when backward demand intersects forward readiness, canonical authority, machine-local scope, freshness, capacity, dependency closure, and writeset conflict freedom.

## Hard laws

1. Pressure is derived from recomputed residuals; self-reported urgency has no authority.
2. Pressure schedules only among lawful candidates and never grants authority.
3. `UNKNOWN` is a live residual and never collapses to zero.
4. Candidate, verified, committed, consumed, and outcome-observed are distinct lifecycle stages.
5. A producer cannot close its root goal. Terminal standing is recomputed from shared state, evidence, consumption, outcome, and hard invariants.
6. Every obligation fork, conversion, hold, invalidation, and closure remains lineage-addressable.
7. Every durable commit is optimistic, writeset-bounded, evidence-gated, authority-gated, freshness-bound, and invariant-preserving.
8. Relevant drift invalidates the affected decision cone. Disjoint drift permits reuse. Unknown relevance holds the candidate.
9. Topology promotion requires a full replacement specification, bounded test, positive observed gain, zero invariant regressions, falsifier, rollback contract, and the stronger union of outgoing/incoming canonical authority claims.
10. Replay proves event-ledger integrity and deterministic reconstruction only; it does not manufacture external truth, behavioral gain, or causal gain.

## MCP surface

- `athena_nexus_compile`
- `athena_nexus_plan`
- `athena_nexus_advance`
- `athena_nexus_state`
- `athena_nexus_replay`
- `athena_nexus_terminal`
- `athena_nexus_recent`
- resource: `athena://nexus4d`

All seven operations are control-plane operations. `plan` emits a lawful batch but performs no execution. `advance` accepts witnessed state-machine events; it does not run a node implementation.

## Pressure channels

`goal`, `constraint`, `evidence`, `uncertainty`, `freshness`, `integration`, `repair`, `queue`, and `outcome` remain independent channels. Edge-specific projections may select among them, but no scalar score can erase a failed hard gate.

## Evidence lattice

Claims carry a componentwise profile over provenance, local, replay, integration, hosted, behavioral, causal, and freshness dimensions. Promotion requires the claim-specific threshold in every required dimension. Strength in one dimension cannot substitute for absence in another.

## Lifecycle

`OPEN → CLAIMED → CANDIDATE → VERIFIED → COMMITTED → CONSUMED → OUTCOME_OBSERVED`

Failure routes include `HELD`, `INVALIDATED`, lawful release/reclaim, contradiction records, and topology rollback. Claim leases, idempotency keys, event digests, snapshot digests, and exact cold replay make the lifecycle auditable.

## Authority bridge

Nodes can require ATHENA Y1 claims with minimum levels in `? → + → ! → #`. Planning and commit read the canonical `AuthorityLedger`. Claim, commit, topology promotion, and topology rollback freeze the observed authority receipts into event lineage so replay is deterministic. Later challenge prevents new commits but cannot rewrite historical receipts.

## Compatibility

This organ subsumes the executable control semantics of the existing forward-pressure and organism-closure layers without erasing their lineage:

- forward-pressure becomes the forward readiness/state plane;
- closure pressure becomes terminal residual and obligation propagation;
- evidence ceilings remain componentwise admission gates;
- existing branch, claim, backpressure, replay, field, transport, and promotion organs remain authoritative in their own scopes.

## Terminal proof

A finite machine is terminal only when all normalized goals are observably closed, every required evidence dimension passes, declared consumers have consumed committed results, required outcome receipts exist, and all hard invariants hold. A persistent organism may be quiescent while remaining reactive; quiescence is not organism termination.
