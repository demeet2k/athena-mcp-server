# TSE Helix Route-Window Calculus V1

Artifact: `ATHENA.TSE.HELIX.ROUTE.WINDOW.V1`  
Status: candidate observation mechanism  
Authority: observation scope only  
Behavioral treatment effect: `UNKNOWN`

## 1. Problem statement

The source-bound Helix ledger records public transition attempts. An event ledger alone is not a valid conversion denominator because event multiplicity and route multiplicity are different objects.

Let `E` be the set of source-bound telemetry events and let a route identity be

```
r = (mission_id, route_id, hatch_id)
```

Define the projection

```
pi : E -> R
```

that maps each event to its route. Conversion is measured over `R`; attempt pressure and coordination cost remain measured over `E`.

The governing distinction is:

```
EVENT_COUNT != ROUTE_COUNT
```

## 2. Stage lattice

Canonical observed stages are

```
S0 = HATCH_CREATED
S1 = HATCH_NEED_PUBLISHED
S2 = MATCH_FOUND
S3 = HANDOFF_ROUTED
S4 = HANDOFF_CONSUMED
S5 = CHILD_CLAIMED
S6 = CHILD_VERIFIED_RETURN
S7 = RETURN_APPLIED
```

`S4` is an optional observational side-channel. The legal operational path permits `S3 -> S5` without `S4`, because an ACK is not execution authority and is not a prerequisite for an independently established claim.

For each route `r`, define stage attainment

```
A_s(r) = 1 iff at least one SOURCE_BOUND event for stage s exists on r
```

and attempt multiplicity

```
N_s(r) = number of SOURCE_BOUND events for stage s on r.
```

Then

```
retry_pressure_s = sum_r N_s(r) - sum_r A_s(r).
```

Retries therefore affect pressure/cost but cannot inflate route attainment.

## 3. Observation window

A window `W` is a measurement scope, never a control authority:

```
W = <window_id,
     mission_id,
     route_scope,
     opened_at,
     closed_at?,
     complete_seams,
     resolved_routes,
     source_refs,
     authority=OBSERVATION_SCOPE_ONLY>
```

An open window may use an explicit route set or a mission-dynamic set. Closing a dynamic window freezes the source-bound route set visible at close.

Window closure does not stop execution. It only states what the observer is prepared to treat as mature for descriptive measurement.

## 4. Right-censoring

For a conversion edge `A -> B`, define

```
D_A(W) = routes in W that attained A
S_B(W) = routes in D_A(W) that attained B
```

A route in `D_A` is mature for seam `q` if:

1. it attained B; or
2. the closed window marks q complete for all scoped routes; or
3. it is explicitly listed in `resolved_routes[q]`.

Let

```
M_B(W) = mature routes for B
P_B(W) = D_A(W) \ M_B(W)
F_B(W) = M_B(W) \ S_B(W).
```

`P_B` is right-censored/pending. `F_B` is observed mature non-attainment.

## 5. Conversion interval

The resolved conversion is

```
eta_resolved(A->B) = |S_B| / |M_B|
```

when `|M_B| > 0`; otherwise `UNKNOWN`.

The current attainment lower bound is

```
eta_lower = |S_B| / |D_A|
```

and the optimistic upper bound under unresolved pending routes is

```
eta_upper = (|S_B| + |P_B|) / |D_A|.
```

When the seam is complete, `P_B=0`, so lower and upper collapse to one observed value.

This distinguishes

```
PENDING != FAILURE.
```

## 6. Primary conversions

The report exposes:

```
eta_publish          S0 -> S1
eta_match            S1 -> S2
eta_handoff          S2 -> S3
eta_consumption      S3 -> S4   # optional side channel
eta_claim            S2 -> S5   # preserves original evaluation contract
eta_claim_from_handoff S3 -> S5 # diagnostic routing conversion
eta_return           S5 -> S6
eta_apply            S6 -> S7
```

Because ACK is optional, `eta_claim` and `eta_claim_from_handoff` do not depend on `S4`.

## 7. Apply-observation membrane

The current Helix composition surface does not implement operational Return application. Therefore absence of an apply event is not automatically an observed zero.

The report classifies apply observation as:

```
OBSERVED
COMPLETE_ZERO
UNAVAILABLE_OR_INCOMPLETE
```

Rules:

- any source-bound `RETURN_APPLIED` event => `OBSERVED`;
- no apply event + closed window with `APPLY` complete => `COMPLETE_ZERO`;
- otherwise => `UNAVAILABLE_OR_INCOMPLETE` and `eta_apply.resolved_eta=UNKNOWN`.

Thus:

```
ABSENCE_OF_APPLY_EVENT != ZERO_APPLY_RATE
```

unless observation maturity is explicitly established.

## 8. Cost and eta_helix

Event cost remains attached to source-bound observations. Let `C(E_W)` be the sum of known event costs in W. Let `Delta_apply(r)` be the verified delta on the unique applied Return for route r.

If every counted event cost is known, `C>0`, and at least one unique applied Return exists:

```
eta_helix = sum_r Delta_apply(r) / C(E_W).
```

If cost is unknown, no apply is observed, or a route contains multiple apply-success events, `eta_helix=UNKNOWN`.

The cost field is reported accounting, not proof that the measured cost causally produced the delta.

## 9. Hold pressure

Source-bound `HELIX_HOLD` events are projected by seam:

```
P_hold(q) = number of source-bound HELIX_HOLD events whose canonical seam is q.
```

A later success does not erase earlier hold pressure. The route may attain the stage once while retaining all witnessed failed/retry attempts as friction evidence.

This preserves failure metabolism without letting failure count distort conversion identity.

## 10. Identity conflict

A single `route_id` mapping to multiple `hatch_id` values is an epistemic conflict. The report fails closed rather than merging those identities.

Likewise multiple source-bound `RETURN_APPLIED` successes on one route make applied-value aggregation ambiguous; `eta_helix` remains `UNKNOWN` until adjudicated.

## 11. Window lifecycle

### OPEN

- request identity is deterministic over mission, initial route scope and source refs;
- same open request is idempotent;
- changed semantics under the same window ID conflict;
- dynamic mission scope may grow while the window is open.

### CLOSED

- route scope is frozen;
- complete seams and explicit resolved routes are frozen;
- same close request is idempotent;
- changed close semantics conflict;
- later mission events outside frozen route scope do not alter the closed report population.

## 12. Epistemic ladder

```
DECLARED_ONLY event
    < SOURCE_BOUND event
    < route-level observed attainment
    < mature-window descriptive conversion
    < matched comparative evidence
    < causal treatment effect
```

No lower level silently promotes itself to a higher level.

In particular:

```
SOURCE_BOUND != CAUSAL
ROUTE_ATTAINMENT != PERFORMANCE_GAIN
WINDOW_CLOSURE != WORLD_CLOSURE
```

## 13. Anti-Goodhart laws

```
MORE_EVENTS != MORE_ROUTES
MORE_RETRIES != MORE_CONVERSION
MORE_ACKS != MORE_CLAIMS
MORE_HOLDS != NEGATIVE_CAUSAL_EFFECT
MORE_HATCHES != MORE_PRODUCTIVE_GAME_TIME
LONGER_WALL_TIME != MORE_ATHENA
```

The eventual field objective remains verified useful continuation and parent-state delta per total coordination cost while preserving legitimate HOLD/STOP behavior.

## 14. Qualification

Mechanism qualification requires distributed two-clone tests for:

- pending route censoring;
- complete-seam zero conversion;
- retry multiplicity without route inflation;
- hold-then-success preservation;
- explicit per-route maturity;
- optional ACK skip;
- apply-channel UNKNOWN/COMPLETE_ZERO distinction;
- unique applied delta aggregation;
- declared-event exclusion;
- dynamic scope freeze at close;
- idempotent close and scope-drift conflict;
- unknown cost handling.

Even a complete mechanism pass leaves:

```
FIELD_PERFORMANCE = UNKNOWN
BEHAVIORAL_TREATMENT_EFFECT = UNKNOWN
CANONICAL_PROMOTION = HOLD
```

until matched field evidence justifies a stronger claim.
