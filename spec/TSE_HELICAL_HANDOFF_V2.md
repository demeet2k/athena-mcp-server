# ATHENA TSE Helical Handoff V2

Status: CANDIDATE_MECHANISM  
Authority: composition and observation only  
Performance claim: UNKNOWN  
Behavioral treatment effect: UNKNOWN

## 1. Purpose

TSE Helical Handoff V2 is the operational composition boundary that turns a bounded Tri-Solenoidal Hatch into a cross-agent circulation path without creating a second assignment, claim, truth, life, Return-application, or causal-evidence authority.

The implementation composes existing organs rather than replacing them:

- TSE population routing owns the deterministic Hatch -> NEED -> advisory match projection.
- Cohesion owns typed NEED/OFFER projection and advisory matchmaking only.
- Message Board owns public presence, handoff messages, acknowledgements and work claims.
- TSE Return check owns only the current-claim-bound Return readiness gate.
- Helix telemetry records public observations and owns no execution semantics.

## 2. Solenoidal interpretation

The operational mapping is:

- Square = executed/verified productive work in a bounded claimed child lane.
- Circle = phase alignment across Git freshness, NEED/OFFER fit, handoff routing and current shared state.
- Triangle = bounded control transitions: Hatch, HOLD, claim gate, Return gate, and legitimate stop.

The cross-agent recurrence is therefore:

```
parent Triangle
  -> population Circle
  -> child Square
  -> Return Triangle
  -> tightened parent Square/Circle boundary
```

This is a systems mapping, not a claim that geometry itself confers execution authority.

## 3. Authoritative state machine

```
VALID_HATCH
  -> HATCH_CREATED [source-bound telemetry root]
  -> NEED_READY
  -> NEED_PUBLISHED [Cohesion + parent Message Board presence]
  -> MATCH_FOUND [advisory only]
  -> HANDOFF_ROUTED [Message Board MESSAGE]
  -> HANDOFF_CONSUMED? [exact matched-agent ACK, optional]
  -> CHILD_CLAIMED [independent current Message Board claim]
  -> CHILD_VERIFIED_RETURN [TSE Return check + current claim revalidation]
  -> RETURN_APPLIED [external operational source; not implemented by this surface]
```

`HANDOFF_CONSUMED` is observationally useful but is not an execution prerequisite: a compatible independent claim may be established without an ACK. Conversely, ACK never creates a claim.

## 4. Authority lattice

The following distinctions are hard firewalls:

```
PLAN != PUBLICATION
MATCH != CLAIM
MESSAGE_ROUTE != CONSUMPTION
ACK != CLAIM
CLAIM != COMPLETION
COHESION_SIGNAL != EXECUTION_AUTHORITY
ROUTE_DIGEST != AUTHORIZATION
PAST_CLAIM != CURRENT_RETURN_AUTHORITY
RETURN_READY != RETURN_APPLIED
TELEMETRY != SOURCE_AUTHORITY
DECLARED_EVENT != SOURCE_BOUND_EVENT
SOURCE_BOUND_EVENT != CAUSAL_EFFECT
TELEMETRY_FAILURE != SOURCE_ROLLBACK
RESEED != PLATFORM_TOKEN_CONTEXT_QUOTA_USAGE_RESET
MECHANISM_PASS != PERFORMANCE_GAIN
```

No Helix tool may call Message Board `present` or `join` on behalf of a matched agent.

## 5. Telemetry epistemic classes

### DECLARED_ONLY

`athena_tse_telemetry_record` accepts a public caller declaration for audit/debugging. The event is persisted with `source.verification=DECLARED_ONLY`.

Declared events:

- are visible in the report;
- are counted separately under `declared_counts` / `declared_residuals`;
- never enter primary `eta_*` conversion metrics;
- cannot be the parent of a SOURCE_BOUND child event.

### SOURCE_BOUND

A SOURCE_BOUND event is emitted only by a composition adapter that derives the transition from an actual public source result/state. It carries:

- source kind;
- source reference;
- deterministic source payload digest;
- source Git coordinate when meaningful;
- source authority label;
- exact Helix parent event.

SOURCE_BOUND means the observation is bound to a checked public source. It does not mean that telemetry has become source authority or that the event demonstrates causality.

## 6. Source adapters

| Helix transition | Required source | Source authority retained |
|---|---|---|
| HATCH_CREATED | validated TSE Hatch + population plan | Hatch/route integrity only |
| HATCH_NEED_PUBLISHED | persisted Cohesion NEED | Cohesion publication + Message Board parent claim |
| MATCH_FOUND | current Cohesion advisory ranking | advisory only |
| HANDOFF_ROUTED | exact Message Board HANDOFF message | route only |
| HANDOFF_CONSUMED | exact matched-agent Message Board ACK | consumption observation only |
| CHILD_CLAIMED | current shared matched-agent claim | Message Board claim truth |
| CHILD_VERIFIED_RETURN | TSE Return-check result + current claim | Return readiness only |
| RETURN_APPLIED | external operational apply receipt | not available in this surface |

## 7. Saga semantics

A source operation and its telemetry append are deliberately not represented as one atomic transaction.

For mutation-bearing operations such as NEED publication or HANDOFF routing:

1. execute the source operation under its own authority;
2. inspect the returned source result;
3. derive a SOURCE_BOUND telemetry packet;
4. append telemetry under fresh shared Git state;
5. if telemetry fails, preserve the already-valid source result and emit a recovery packet.

The source operation is never rolled back merely because observation failed.

`athena_tse_helix_reconcile` repairs this observation gap by re-reading/re-deriving source state without replaying the original mutation. If current state can no longer prove the historical source binding, reconciliation fails closed.

## 8. Conversion measurements

Primary report metrics are derived from SOURCE_BOUND events only:

```
eta_match  = MATCH_FOUND / HATCH_NEED_PUBLISHED
eta_claim  = CHILD_CLAIMED / MATCH_FOUND
eta_return = CHILD_VERIFIED_RETURN / CHILD_CLAIMED
eta_apply  = RETURN_APPLIED / CHILD_VERIFIED_RETURN
eta_helix  = applied_verified_delta / known_source_bound_cost
```

These are descriptive circulation measurements, not causal treatment effects.

Unknown denominator remains `UNKNOWN`. Unknown cost remains unknown. The current cost field is a reported cost attached to a source-bound observation; it is not independently proven causal resource accounting.

A future hardening may add route-window maturity/censoring semantics so an unresolved in-flight route is distinguished from a completed zero-conversion route. Until then the report must be interpreted as a current-snapshot descriptive funnel.

## 9. Anti-Goodhart constraints

The following carry zero intrinsic reward:

- elapsed wall time;
- token count;
- message count;
- number of workers;
- number of Hatches;
- number of matches;
- number of ACKs;
- number of telemetry events;
- number of coordinate systems.

The desired field outcome is increased verified useful parent-state delta per total coordination cost while preserving legitimate HOLD/STOP behavior.

## 10. Failure metabolism

Typed Helix holds include:

- `CAPABILITY_HOLD`
- `STALE_STATE_HOLD`
- `DUPLICATION_COLLAPSE`
- `ROUTED_NOT_CONSUMED`
- `ACKED_NOT_CLAIMED`
- `AUTHORITY_HOLD`
- `EVIDENCE_HOLD`
- `NO_POSITIVE_HATCH`

A hold is not silently converted into a success event. Source-bound holds are recorded separately from source-bound successful transitions.

## 11. Qualification gates

Mechanism promotion requires, at minimum:

1. syntax/compile pass;
2. distributed two-clone source-bound integration tests;
3. full repository unit suite;
4. critical-invariant suite;
5. MCP smoke pass;
6. trusted exact-head promotion qualification where applicable;
7. current-master ancestry at qualification time;
8. no authority-firewall regression.

Even complete mechanism qualification does not establish field performance.

Field promotion remains dependent on matched mission observations under the Game Time Controller evaluation design and must preserve:

```
FIELD_PERFORMANCE = UNKNOWN
BEHAVIORAL_TREATMENT_EFFECT = UNKNOWN
```

until observations support a stronger claim.

## 12. Next hardening frontier

The next rigorous layer is route-window and censoring calculus:

- identify in-flight versus resolved stage denominators;
- prevent repeated retries from inflating event-count ratios;
- report route-level attainment as well as attempt-level pressure;
- establish a real operational `RETURN_APPLIED` source adapter before interpreting absence of apply receipts as zero application conversion;
- bind ACK observation to the decoded TSE handoff envelope, not only message identity/sender/recipient;
- feed matched field windows into the existing Cohesion evidence guard without upgrading descriptive association into causal effect.
