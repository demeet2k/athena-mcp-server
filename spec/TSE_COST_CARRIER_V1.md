# TSE Cost Carrier V1

Artifact: `ATHENA.TSE.COST.CARRIER.V1`  
Version: `TSE.COST.CARRIER.1`  
Work order: #367  
Stacked parent: `TSE.CLOSED.HELIX.CIRCULATION.1` exact qualified head `6d3afeb53ec8b959af7ca0684113445e79a345a3`

## Purpose

Carry the already-existing scalar `cost={known,total}` contract through the Re-Entry and Rehydration portions of a closed Tri-Solenoidal circulation so the structural cycle denominator can be computed when—and only when—every typed segment carries known cost.

This is an accounting carrier. It does not observe provider token use, context-window use, wall-clock compute, electricity, billing, or tool-service resource consumption.

## Composition

```text
SOURCE_BOUND S7_0
  -> REENTRY_START(cost_reentry)
  -> REHYDRATION_STEP_1(cost_1)
  -> ...
  -> REHYDRATION_STEP_n(cost_n)
  -> HATCH / population / Return / Apply SOURCE_BOUND costs
  -> SOURCE_BOUND S7_1
  -> CLOSED_SEQUENCE_BOUND receipt
  -> COST_CARRIER sidecar
```

The original circulation sequence receipt remains a separate artifact. Cost Carrier V1 does not rewrite its semantic digest.

```text
SEQUENCE_RECEIPT != COST_RECEIPT
```

## Scalar cost contract

Known:

```json
{"known": true, "total": 0.3}
```

Unknown:

```json
{"known": false}
```

Rules:

- `known` is an actual Boolean;
- known `total` is finite, non-Boolean, and nonnegative;
- unknown cost may not carry a numeric total;
- additional fields are rejected in V1;
- missing cost is UNKNOWN, not zero.

## Re-entry carrier

`athena_tse_helix_advance(operation=REENTRY_START)` already receives a required `cost` packet. V1 normalizes that existing packet and carries it into the ordinary `RehydrationLoopRuntime.start` transaction as one reserved machine-readable stop-condition marker:

```text
ATHENA_TSE_REENTRY_COST_V1=<canonical-json>
```

No pre-start cost commit is created. The marker therefore rides inside the same Git mutation that starts the rehydration loop.

Caller injection of the reserved marker is rejected.

The re-entry identity/digest remains task/lineage identity; scalar cost metadata does not silently redefine successor identity. A historical replay with a different carried cost is a cost conflict HOLD.

## Rehydration carrier

The existing rehydration completion object may carry:

```json
"cost": {"known": true, "total": 0.3}
```

The normal rehydration receipt already persists the complete completion object, so no parallel receipt or mutation is required. The extension validates and normalizes the optional cost before delegating to the existing advancement path.

Every rehydration receipt that occurs before the next Hatch parent is part of the cycle denominator. Productive and no-progress steps both consume cost if cost is carried; productivity classification remains a separate predicate.

## Post-closure sidecar

Only after Closed Helix Circulation V1 has already produced or replayed a valid `CLOSED_SEQUENCE_BOUND` receipt does Cost Carrier V1 derive its sidecar.

Storage:

```text
runtime/tse_population/v1/telemetry/circulation_cost/<cycle_id>.json
```

Identity binds:

- cycle ID;
- circulation semantic digest;
- re-entry ID and rehydration loop ID;
- exact re-entry-start carried cost;
- exact rehydration receipt path/digest/commit/step and carried cost;
- existing SOURCE_BOUND next-route TSE known/unknown cost summary;
- verified incorporated delta.

The sidecar has its own `cost_carrier_digest`.

Same basis replays idempotently. Changed basis under the same cycle ID fails closed.

## Structural denominator

Let:

- `C_R` = re-entry-start scalar cost;
- `C_H = Σ C_h` = scalar costs of all rehydration receipts before the next Hatch;
- `C_T` = SOURCE_BOUND TSE route cost already observed by circulation V1.

Known subtotal:

```text
C_known = known(C_R) + known(C_H) + known(C_T)
```

Structural completion:

```text
cost_complete =
  reentry cost known
  AND every included rehydration receipt cost known
  AND every included SOURCE_BOUND TSE event cost known
```

Only if `cost_complete=true`:

```text
total_carried_cost = C_R + C_H + C_T
```

otherwise:

```text
total_carried_cost = UNKNOWN
```

For incorporated delta `Δ`:

```text
incorporated_delta_per_total_cost = Δ / total_carried_cost
```

only when the denominator is complete and strictly positive. Otherwise it is `UNKNOWN`.

## Host-resource firewall

A complete scalar carrier is still not host/provider resource accounting.

V1 always exposes:

```text
cost_authority = DECLARED_STRUCTURAL_ACCOUNTING_ONLY
host_resource_cost_complete = false
incorporated_delta_per_host_resource_cost = UNKNOWN
host_resource_authority = UNOBSERVED
```

A later host-observed carrier may bind real provider/tool/token/latency/compute measurements. It must not reinterpret V1 scalar totals as those measurements.

## Report semantics

The existing circulation report is enriched from separately verified cost sidecars.

For selected closed cycles:

```text
known_total_carried_cost = Σ known scalar components
```

`total_carried_cost` and `incorporated_delta_per_total_cost` become numeric only if every selected closed cycle has one integrity-valid, structurally complete cost sidecar.

Missing sidecar, invalid digest, or unknown component keeps the total denominator `UNKNOWN`.

The existing closed-receipts-only observation model is unchanged:

```text
pending_cycles = UNKNOWN
closure_rate = UNKNOWN
```

## Authority laws

```text
SEQUENCE_RECEIPT != COST_RECEIPT
UNKNOWN_COST != ZERO_COST
COST_CARRIER != EXECUTION_AUTHORITY
COST_COMPLETE != CAUSAL_EFFECT
CARRIED_SCALAR_COST != HOST_RESOURCE_TRUTH
TOTAL_CARRIED_COST != PLATFORM_TOKEN_CONTEXT_QUOTA_USAGE
PRODUCTIVE_STEP != COSTLESS_STEP
NO_PROGRESS_STEP != ZERO_COST_STEP
MECHANISM_PASS != PERFORMANCE_GAIN
```

## Scientific standing

Even after exact-head mechanism qualification:

```text
FIELD_PERFORMANCE = UNKNOWN
BEHAVIORAL_TREATMENT_EFFECT = UNKNOWN
HOST_RESOURCE_EFFICIENCY = UNKNOWN
CANONICAL_PROMOTION = HOLD
```

The next scientific question is still comparative: whether the TSE treatment increases verified incorporated productive transitions per **measured** total resource cost under a matched field design. Structural scalar accounting is a prerequisite for that experiment, not its result.
