# ATHENA COLLECTIVE GROWTH OPERATORS V1

This layer extends `COLLECTIVE_RUNTIME_V1` from choosing group geometry into actively allocating work, valuing infrastructure, changing topology, propagating scoped failure signals, and pruning/hybridizing memory.

## 1. Demand-sensitive allocation

For task `j` define

`D_j = U_j * G_j * max(epsilon,B_j) * (1-S_j) * (0.5+0.5*Urgency_j)`

where U=utility, G=remaining gap, B=bridge value, S=saturation.

For worker `i`:

`Fit_ij = |Required_j ∩ Capabilities_i| / |Required_j|`

and

`Avail_i = 1-load_i`.

Assignment score:

`A_ij = D_j^alpha * max(epsilon,Fit_ij)^beta * Avail_i`.

The allocator greedily fills highest-demand tasks with highest-fitting available workers under explicit assignment-capacity limits. The invariant is not equal participation; it is maximum marginal contribution per scarce worker slot.

## 2. Living-bridge accounting

For proposed bridge/interface `b`:

`V_b = ExpectedUses * RouteSavingPerUse + QualityGain + ResilienceGain`

`C_b = BuildCost + MaintenanceCost + LockedCapacityCost`

`Net_b = V_b - C_b`.

Build iff `Net_b > 0`.

The runtime also reports break-even future-use count when route saving is positive. This is the army-ant principle made explicit: infrastructure consumes agents/resources and therefore must repay the capacity it immobilizes.

## 3. Fission/fusion controller

Fission pressure:

`F = .35*coordination_overhead + .25*contagion + .20*size_pressure + .20*(1-internal_cohesion)`.

Fusion pressure:

`M = .30*complementarity + .25*duplicate_work + .25*shared_dependencies + .20*interface_maturity - .25*identity_conflict`.

Decision:

- FISSION when F >= .62 and F >= M + .08;
- FUSE when M >= .62 and M >= F + .08;
- HOLD otherwise.

The controller therefore distinguishes growth from indiscriminate accretion. Modules may split to reduce coordination/contagion, or merge when duplicate work and shared dependencies exceed the value of separation.

## 4. Dependency-scoped alarm waves

The caller provides explicit directed influence/dependency edges. A seed severity `s_0` propagates along edge weight `w` and hop decay `rho`:

`s_{h+1} = s_h * w * rho`.

Propagation stops at `max_hops` or when severity falls below threshold.

This forbids default global panic/broadcast. Only descendants reachable through declared influence edges inherit the alert.

## 5. Artifact lifecycle / cognitive apoptosis

Each artifact is classified into one of:

- `KEEP_ACTIVE` — still useful/novel/evidential;
- `KEEP_REFERENCE` — required by lineage or downstream dependents;
- `DORMANT` — low current utility but preserved optionality;
- `QUARANTINE` — weak evidence; audit-visible but excluded from authoritative routing;
- `PRUNE_REFERENCE` — superseded low-reuse/low-novelty object; remove active privilege while retaining tombstone/reference.

Deletion of active priority is never deletion of required lineage.

## MCP operations

- `athena_collective_allocate`
- `athena_bridge_account`
- `athena_collective_restructure`
- `athena_dependency_alarm`
- `athena_artifact_lifecycle`

Resource: `athena://collective/growth`.

## Persistence boundary

All operators are deterministic advisory transforms. Canonical mutation remains controlled by existing expected-VID / Git-head CAS and finalized-output mechanisms. This keeps planning/restructuring recommendations distinguishable from committed organism state.
