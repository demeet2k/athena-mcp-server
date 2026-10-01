# ATHENA TSE Re-Entry / Succession V1

## Status

Candidate mechanism. Parent mechanism: Self-Tightening Knot Apply V1 R2 (`SOURCE_BOUND CHILD_VERIFIED_RETURN -> SOURCE_BOUND RETURN_APPLIED`).

Scientific standing remains:

```text
FIELD_PERFORMANCE = UNKNOWN
BEHAVIORAL_TREATMENT_EFFECT = UNKNOWN
CANONICAL_PROMOTION = HOLD
```

## Objective

Close the next bounded edge of the Tri-Solenoidal continuation engine:

```text
S6 CHILD_VERIFIED_RETURN
 -> S7 RETURN_APPLIED
 -> R0 REENTRY_READY | REENTRY_AMBIGUOUS | REENTRY_HOLD | REENTRY_STOP_REQUESTED
 -> R1 REHYDRATION_STARTED
 -> explicit bounded rehydration cycle
```

Re-entry is not a background worker and is not a second scheduler. It composes the existing TSE Helix with the existing Git rehydration loop.

## Core law

```text
RETURN_APPLIED != NEXT_TASK_TRUTH
RETURN_APPLIED != EXECUTION_AUTHORITY
REENTRY_PREVIEW != BACKGROUND_EXECUTION
REENTRY_START != TASK_EXECUTION
SUCCESSOR_SCORE != EVIDENCE
SUCCESSOR_SCORE != AUTHORITY
```

## Two-head coordinate model

Let:

- `P` = frozen pre-Hatch parent commit;
- `C` = verified child Return commit;
- `A` = semantic applied head at which both `P` and `C` have been adopted;
- `E7` = Git commit that durably records the SOURCE_BOUND `RETURN_APPLIED` event;
- `H+` = current freshly verified shared continuation head at re-entry time.

The Self-Tightening Knot proves:

```text
P <=git A
C <=git A
```

Telemetry then durably records S7, so normally:

```text
A <=git E7 <=git H+
```

Re-entry must preserve both coordinates:

```text
applied_semantic_head = A
continuation_shared_head = H+
```

They are not interchangeable. The semantic adoption source remains `A`; the next Git mutation must CAS against `H+`.

## S7 admission predicate

A re-entry candidate is admitted only when all are true:

1. route digest/invariants validate;
2. original Hatch digest/invariants validate;
3. route/Hatch ID, Hatch digest and parent-checkpoint digest agree;
4. exact requested event exists and is `RETURN_APPLIED`;
5. S7 event is `SOURCE_BOUND`;
6. S7 source kind is `TSE_SHARED_GIT_ADOPTION`;
7. S7 source authority is `FRESH_SHARED_GIT_ANCESTRY_ADOPTION`;
8. S7 mission/route/hatch/child claim agree with the supplied route;
9. S7 has positive verified delta;
10. S7 parent exists and is exact `SOURCE_BOUND CHILD_VERIFIED_RETURN`;
11. S6 source kind is `TSE_RETURN_CHECK`;
12. S6 and S7 verified deltas agree;
13. S7 `source.git_head` gives semantic applied head `A`;
14. S7 `git_parent == A`;
15. shared Git fresh-sync succeeds;
16. local HEAD equals verified remote HEAD;
17. `A <=git H+`;
18. the Git commit containing the S7 event file is an ancestor of `H+`.

Only then is S7 a valid re-entry source.

## Re-entry semantic identity

A re-entry semantic digest binds:

```text
schema/version
reentry_id
mission_id
route_id + route_digest
hatch_id + hatch_digest
parent_checkpoint_digest
RETURN_APPLIED event ID
RETURN_APPLIED semantic digest
RETURN_APPLIED source digest
applied_semantic_head
verified_delta
human goal
explicit successor candidates
successor routing policy
parent-residual-fallback policy
terminal request bit
```

The digest deliberately does **not** include the changing continuation shared head or transient frontier digest. Those are observation coordinates, not semantic re-entry identity.

## Routing calculus

Re-entry reuses the existing `SuccessorCompiler` candidate normalization, source defaults, Pareto dominance relation, score function and tie epsilon.

Candidate sources are ordered by observed availability:

1. current frontier selected candidate;
2. current frontier Pareto candidates;
3. current frontier residuals;
4. explicit caller successor candidates;
5. frozen parent residuals only when `allow_parent_residual_fallback=true` and no stronger current candidate exists.

For candidate `x`, the inherited routing metrics are:

```text
benefit(x) = utility + dependency_unblocking + uncertainty_reduction + novelty
cost(x) = risk + resource_cost + repetition
routing_score(x) = weighted benefit - weighted cost
```

The score is a routing heuristic only.

The nondominated set is:

```text
F = {x | no y dominates x}
```

If one member of `F` has a uniquely highest routing score within tie epsilon:

```text
REENTRY_READY
```

If multiple nondominated members share the highest score:

```text
REENTRY_AMBIGUOUS
```

No lexical or insertion-order tie break is allowed.

If no successor is observed:

```text
REENTRY_HOLD
NO_SUCCESSOR_OBSERVED != GLOBAL_TERMINALITY
```

## Terminal request

A caller may supply `terminal_request=true` only with at least one public terminal witness. The result is:

```text
TSE_REENTRY_STOP_REQUESTED
```

This blocks automatic start but remains policy/request state:

```text
TERMINAL_REQUEST != VERIFIED_GLOBAL_TERMINALITY
```

## PREVIEW

`athena_tse_helix_advance(operation=REENTRY_PREVIEW)`:

- requires exact S7 as `parent_event_id`;
- requires `shared_remote_mode=REQUIRED`;
- consumes `{hatch,reentry}` through the existing `child_return` composition field;
- fresh-validates S7 and Git phase;
- observes requested frontier state;
- compiles inherited successor geometry;
- does not create a rehydration loop;
- does not execute a task;
- does not create claim, evidence, merge, or provider authority.

The preview produces a dynamic `preview_digest` over semantic identity plus current continuation head, S7 observation commit, frontier digest and selected/tied candidate IDs.

## START

`athena_tse_helix_advance(operation=REENTRY_START)` first recomputes PREVIEW.

For unique selection it delegates:

```text
RehydrationLoopRuntime.start(
    expected_git_head = continuation_shared_head,
    task = selected successor,
    shared_remote_mode = REQUIRED
)
```

For ambiguity, START holds by default. If `allow_ambiguity_resolution=true`, it starts one bounded task whose content preserves the complete top tie set:

```text
Resolve successor ambiguity without silent scalarization among: A | B | ...
```

This is not a hidden choice among tied successors.

## One control-plane law

Re-entry obtains or creates the same server `PromptRuntime` used by normal prompt dispatch and caches the same `RehydrationLoopRuntime` under that prompt runtime.

Therefore:

```text
TSE_REENTRY -> EXISTING_REHYDRATION_LOOP
```

not:

```text
TSE_REENTRY -> SECOND_LOOP_UNIVERSE
```

## Idempotency without a second registry

A successful START writes a machine-readable re-entry identity marker into the normal rehydration loop goal:

```text
[[ATHENA_TSE_REENTRY_V1 id=<reentry_id> digest=<semantic_digest>]]
```

Because loop state is already Git-persisted, replay scans the current shared rehydration states:

- same reentry ID + same semantic digest -> `TSE_REENTRY_ALREADY_STARTED`;
- same reentry ID + different semantic digest -> conflict HOLD.

No second mutable re-entry ledger is introduced.

## Explicit-cycle boundary

Starting the loop compiles and persists its first self-prompt. It does not execute that prompt.

The existing loop laws remain authoritative:

```text
CYCLE != BACKGROUND_EXECUTION
SELF_PROMPT != HIGHER_AUTHORITY
GIT_COMMIT != OBSERVED_SUCCESS
LOCAL_COMMIT != SHARED_RETURN unless remote publication is verified
HEAD_CHANGE => REHYDRATE
REPEATED_NO_PROGRESS => HOLD
```

## Tri-Solenoidal mapping

### Square

Actual bounded execution and verified productive delta.

### Circle

Fresh shared Git phase, current frontier observation, successor geometry, resource/route synchronization.

### Triangle

Hatch, Return, Apply, Re-entry READY/AMBIGUOUS/HOLD/STOP gates.

### Self-Tightening Knot

The child result becomes a parent boundary only through verified shared adoption.

### Re-entry operator

The new shared boundary is re-observed and converted into the next explicit bounded task without pretending that adoption itself determines the task.

Conceptually:

```text
H_t -> work_t -> Return_t -> Apply_t -> Reentry_t -> H_{t+1}
```

with every arrow typed and independently witnessable.

## Adversarial requirements

The implementation must fail closed for:

- DECLARED_ONLY S7;
- wrong S7 source kind/authority;
- S7 with wrong mission/route/hatch/child claim;
- S7 parent not exact SOURCE_BOUND S6;
- S6/S7 delta mismatch;
- semantic applied head missing;
- S7 `git_parent` not equal to semantic applied head;
- S7 observation commit absent from current shared history;
- semantic applied head absent from current shared history;
- local/remote phase mismatch;
- BEST_EFFORT or DISABLED shared mode for re-entry;
- no observed successor;
- tie silently broken;
- same reentry ID changed semantically;
- reset/private payload;
- terminal request without a public witness.

## Performance objective

The mechanism should not be evaluated by wall time, message count, token count, spawn count, or raw Hatch count.

The eventual scientific metric is closer to:

```text
incorporated_productivity =
    verified useful deltas that reached shared adoption and lawful next-cycle re-entry
    / total execution + coordination + handoff + verification + adoption + re-entry cost
```

Mechanism qualification cannot establish that treatment effect. Matched field evidence remains required.
