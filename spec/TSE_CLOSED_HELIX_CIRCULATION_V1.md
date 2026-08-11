# ATHENA TSE Closed Helix Circulation V1

## Status

Candidate measurement mechanism.

Qualified parents:

- Self-Tightening Knot Apply R2: `cbd6e2c5ee445d6134a6ce1aeea5d2c19ba07403`.
- Re-Entry / Succession V1: `d6770140ada8c728cfcaa6e0bdc198a12cdee3f9`.

Scientific standing:

```text
FIELD_PERFORMANCE = UNKNOWN
BEHAVIORAL_TREATMENT_EFFECT = UNKNOWN
CANONICAL_PROMOTION = HOLD
```

## Purpose

The engine now has lawful mechanisms for:

```text
Hatch -> population routing -> claim -> verified Return -> shared Apply -> explicit Re-entry
```

but mechanism availability is not evidence that an agent colony remains productively in game.

This V1 therefore measures the stronger sequence:

```text
S7_0 SOURCE_BOUND RETURN_APPLIED
 -> marked TSE REENTRY_START
 -> >=1 observed productive rehydration receipt
 -> next Hatch rooted after that productive receipt
 -> next verified child Return
 -> S7_1 SOURCE_BOUND RETURN_APPLIED
 -> CLOSED_SEQUENCE_BOUND receipt
```

The measurement is deliberately **sequence-bound, not causal**.

## Primary laws

```text
MORE_WALL_TIME != MORE_GAME_TIME
MORE_MESSAGES != MORE_GAME_TIME
MORE_HATCHES != MORE_GAME_TIME
MORE_RETRIES != MORE_GAME_TIME
REENTRY_START != PRODUCTIVE_CYCLE
GIT_ANCESTRY != SEMANTIC_CAUSALITY
SEQUENCE_BOUND != CAUSAL_EFFECT
KNOWN_COST != TOTAL_COST
UNKNOWN_COST != ZERO_COST
MECHANISM_PASS != PERFORMANCE_GAIN
```

## Why V1 has no mutable OPEN window

A conventional observation window would persist an OPEN record before work begins. In a Git-coordinated system that observation write changes HEAD and therefore perturbs the very continuation coordinate being measured.

V1 avoids that unnecessary observer mutation.

It persists only a **closed receipt**, after all source states already exist. Consequently:

```text
observation_model = CLOSED_RECEIPTS_ONLY_NO_OPEN_WINDOW_MUTATION
```

This has an epistemic cost: the denominator of all started/pending cycles is not known from this V1 ledger alone. Therefore:

```text
pending_cycles = UNKNOWN
closure_rate = UNKNOWN
```

rather than silently treating unrecorded starts as zero or failure.

## Closed-cycle coordinates

For one observed cycle define:

- `A0` — origin semantic applied head from source-bound S7_0;
- `E7_0` — Git commit that records S7_0;
- `H0` — re-entry loop base head;
- `L0` — re-entry loop start commit;
- `W_i` — substantive work commit for rehydration receipt `i`;
- `R_i` — Git commit that records rehydration receipt `i`;
- `P1` — frozen Git parent of the next Hatch;
- `C1` — verified child Return commit of the next Hatch;
- `A1` — next semantic applied head;
- `E7_1` — Git commit that records S7_1;
- `H+` — current shared head when the closed-cycle receipt is observed.

The intended sequence witness is:

```text
A0 <=git E7_0 <=git H0 <=git L0 <=git R_productive <=git P1 <=git A1 <=git E7_1 <=git H+
```

and Knot Apply separately proves:

```text
P1 <=git A1
C1 <=git A1
```

The circulation observer re-derives the available typed and Git evidence. This proves ordered inclusion only.

It does not prove:

```text
reentry caused next Hatch
rehydration work caused child success
child success improved long-horizon treatment outcome
```

## Origin S7 validation

The origin event is accepted only through the Re-Entry V1 admission membrane:

- exact mission/route/hatch/child claim;
- `RETURN_APPLIED`;
- SOURCE_BOUND;
- source kind `TSE_SHARED_GIT_ADOPTION`;
- source authority `FRESH_SHARED_GIT_ANCESTRY_ADOPTION`;
- exact SOURCE_BOUND `CHILD_VERIFIED_RETURN` parent;
- positive verified delta;
- semantic applied head present;
- `S7.git_parent == semantic applied head`;
- semantic applied head and S7 observation commit contained in the current shared frontier.

## Re-entry loop validation

The supplied normal rehydration loop must:

1. pass the existing `RehydrationLoopRuntime.verify()` chain-integrity verifier;
2. contain the machine-readable goal marker:

```text
[[ATHENA_TSE_REENTRY_V1 id=<reentry_id> digest=<reentry_digest>]]
```

3. expose a base head `H0` and a durable start event commit `L0`;
4. satisfy `H0 <=git L0`;
5. satisfy `L0 <=git P1` for the next Hatch parent.

The observer never creates or edits rehydration state.

## Productive rehydration receipt predicate

For a rehydration receipt `r` to count toward this cycle, its receipt commit must be an ancestor of next Hatch parent `P1` and:

```text
r.completion.observed = true
r.completion.status in {SUCCEEDED, PARTIAL}
r.completion.progress_delta > 0
r.no_progress = false
(material_work_paths != empty OR completion.evidence_refs != empty)
```

This explicitly excludes:

- self-reported unobserved progress;
- HELD / FAILED / NO_PROGRESS cycles;
- zero/negative progress;
- loop bookkeeping with neither material work nor public evidence;
- receipts created after the next Hatch had already frozen its parent coordinate.

At least one productive receipt must exist.

## Next Hatch and next S7 validation

The next route/Hatch must validate independently and must not reuse the origin Hatch.

The next frozen parent `P1` must satisfy:

```text
A0 <=git P1
E7_0 <=git P1
L0 <=git P1
R_productive <=git P1  for at least one productive receipt
P1 <=git A1
```

The next event then passes the same strict Re-Entry S7 validator, so it is an actual SOURCE_BOUND shared-adoption observation with an exact SOURCE_BOUND verified-Return parent.

The origin and next S7 event IDs must differ.

## Semantic receipt identity

One closed circulation receipt binds:

```text
cycle_id
mission_id
origin route/hatch digests
origin S7 event/semantic/source digests
A0 + E7_0
reentry id/digest
rehydration loop id/base/start commit
productive receipt path/digest/receipt-commit/work-head set
next route/hatch digests
P1
next S7 event/semantic/source digests
A1 + E7_1
next verified incorporated delta
```

Dynamic current shared head and observation time are excluded from semantic identity.

Exact same cycle ID + same semantic digest is historical idempotency.

Same cycle ID + changed semantic digest is a conflict HOLD.

## Productivity metrics

The receipt exposes:

```text
productive_rehydration_steps
rehydration_steps_total
no_progress_steps
material_work_paths_unique
verified_incorporated_delta
```

The key numerator is:

```text
verified_incorporated_delta = S7_1.verified_delta
```

not message count, task count, wall time, token count, Hatch count, or raw event count.

## Cost semantics

V1 aggregates only cost fields on SOURCE_BOUND telemetry events of the next TSE route up through S7_1.

For event `e`:

```text
known(e) = cost.known == true AND cost.total is finite nonnegative
```

Then:

```text
known_source_bound_tse_cost_total = sum(cost.total for known source-bound route events)
```

Unknown/invalid source-bound TSE cost rows are explicitly listed.

Critically, the current public re-entry and rehydration receipts do not persist a complete execution-cost model. Therefore every V1 closed-cycle receipt declares at least:

```text
unknown_cost_components = [
  reentry_start_control_cost_not_persisted,
  rehydration_execution_cost_not_persisted
]
cost_complete = false
```

Thus:

```text
incorporated_delta_per_known_source_bound_tse_cost = delta / known TSE cost, when denominator > 0
incorporated_delta_per_total_cost = UNKNOWN
```

The partial ratio is diagnostic and must never be relabeled as total efficiency.

## Report semantics

`athena_tse_circulation_report` aggregates only persisted closed receipts.

It returns:

```text
closed_cycles
verified_incorporated_delta_total
productive_rehydration_steps_total
no_progress_steps_total
known_source_bound_tse_cost_total
incorporated_delta_per_known_source_bound_tse_cost
incorporated_delta_per_total_cost = UNKNOWN
pending_cycles = UNKNOWN
closure_rate = UNKNOWN
```

Because this V1 intentionally has no OPEN-window mutation, it has no lawful denominator for started-but-not-closed cycles.

## Public surfaces

Tools:

```text
athena_tse_circulation_observe
athena_tse_circulation_report
```

Resource:

```text
athena://tse-circulation/v1
```

The resource advertises `authority=MEASUREMENT_ONLY` and `causal_effect=UNKNOWN`.

## Tri-Solenoidal interpretation

### Square

The productive rehydration receipt requires actual bounded work/evidence and positive observed progress.

### Circle

Git ancestry and fresh shared-frontier synchronization constrain which receipts and Hatches are temporally admissible.

### Triangle

Origin Apply, Re-entry, next Hatch, Return, and next Apply create the recursive control gates.

### Self-Tightening Knot

Each verified child must become part of shared state before it can count as an incorporated delta.

### Circulation

A closed receipt proves that one incorporated boundary was followed by lawful re-entry, productive bounded work, a later Hatch, and another incorporated boundary.

That is the first operational approximation of:

```text
productive_game_time := verified incorporated state transitions that successfully circulate into a later bounded cycle
```

It is still not proof of causal superiority.

## Next scientific gate

After exact-head mechanism qualification, the next valid experiment is a matched treatment comparison using circulation receipts plus separately complete cost observation.

A useful target quantity is:

```text
Gamma = verified incorporated delta from closed cycles / complete total cycle cost
```

but V1 must report `Gamma = UNKNOWN` until complete cost instrumentation exists.
