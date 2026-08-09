---
name: git-next-quest-pipeline
description: Maintain a rolling three-quest NEXT window so long development chains continuously rotate focus and reseed future work from canonical successor batons.
---

# ATHENA Rolling NEXT Quest Pipeline V1

Use this skill when the user says `next`, requests mass orchestration, or wants a long-running sequence of explicit quests rather than a single isolated task.

## Core geometry

Execution order:

```text
Q1 = FOCUS NOW
Q2 = STAGED NEXT
Q3 = STAGED AFTER NEXT
```

User-facing reverse window:

```text
(Q3, Q2, Q1)
```

Rotation law:

```text
(Q3, Q2, Q1)
   Q1 completes
        ↓
(Q4, Q3, Q2)
```

where Q2 becomes the new focus and Q4 enters the far end of the pipeline.

## Canonical ownership

- Rehydration Successor owns **WHAT NEXT / far-end reseed candidate generation** and produces `ATHENA.REHYDRATION.SUCCESSOR.BATON.V1`.
- Rehydration Campaign owns bounded branch graphs and campaign-level parallel work.
- Freshness Train owns moving-master classification.
- Message Board remains coordination/claim authority where installed.
- Rolling NEXT Pipeline owns only the three-slot focus/staging window.

Do not duplicate those authorities inside this skill.

## Preferred composite NEXT operation

When Q1 is backed by a Rehydration Loop, prefer `athena_next_pipeline_advance_focus`.

It performs one explicit composite transition:

```text
observe Q1 completion
→ verify Q1 == loop current task
→ prove substantive Git delta outside orchestration bookkeeping
→ compile Q4 from residual/candidate evidence using canonical SuccessorCompiler
   (staged Q2 is intentionally omitted from Q4 candidate generation)
→ advance RehydrationLoop with self_steer=false and next_task=Q2
→ rotate pipeline Q1→history, Q2→focus, Q3→stage, Q4→far-end
→ return loop + pipeline receipts
```

The central law is:

```text
Q4_RESEED != Q2_FOCUS
```

A fresh successor must never steal the immediate focus position from the already staged Q2.

## Manual workflow

1. Start with exactly three distinct quests using `athena_next_pipeline_start`.
2. Work only Q1 as the main focus. Q2/Q3 are staged context, not background execution.
3. When Q1 is actually completed, obtain/retain the canonical Rehydration Successor baton from observed completion residuals/candidates.
4. Call `athena_next_pipeline_rotate` with exact state/checkpoint coordinates, or use the preferred composite bridge above.
5. The pipeline removes Q1 to completed history, shifts Q2→Q1 and Q3→Q2, then appends Q4 from the successor baton.
6. Continue on the newly returned Q1.
7. If the successor baton is ambiguous, preserve the tie as `RESEED_HOLD`. Resolve it explicitly with `athena_next_pipeline_resolve_reseed`; never use a hidden lexical/random tie-break.
8. Resolve any pending reseed hold before completing another focus quest so the three-quest planning horizon does not silently collapse.
9. Run `athena_next_pipeline_verify` when handing off or before relying on a long chain.

## Long engagement behavior

The pipeline keeps a useful horizon visible while attention stays narrow:

```text
focus depth = 1
planning horizon = 3
completed memory = bounded history
reseed = one quest per completed focus quest
```

This lets a sequence evolve as:

```text
(Q3,Q2,Q1)
(Q4,Q3,Q2)
(Q5,Q4,Q3)
(Q6,Q5,Q4)
...
```

without forcing the agent to rediscover the next two tasks after every completion.

## Reseed rules

A Q4 candidate must:

- come from a valid canonical successor baton;
- contain a concrete task;
- not duplicate an active quest;
- not silently repeat completed work unless `allow_revisit=true` is explicitly chosen;
- preserve ambiguity when several tied candidates remain lawful;
- never replace an inadmissible canonical SELECTED successor with a lower-ranked candidate. Inadmissible SELECTED => typed reseed hold.

## Substantive work guard

The composite NEXT bridge does not count changes confined to these namespaces as quest progress:

```text
prompts/rehydration/<loop_id>/
prompts/next_quest_pipelines/<pipeline_id>/
prompts/message_board/
```

So:

```text
BOOKKEEPING_COMMIT != SUBSTANTIVE_QUEST_PROGRESS
```

## Mass orchestration versus parallel execution

This skill increases **orchestration horizon**, not hidden concurrency.

```text
STAGED_QUEST != EXECUTING_QUEST
MASS_ORCHESTRATION != BACKGROUND_EXECUTION
```

Use Rehydration Campaign/Cohesion partition mechanics for actual lawful parallel branches. The rolling NEXT window instead guarantees that completing the current focus immediately exposes the next focus and reseeds the planning horizon.

## Freshness law

Before mutating a stale branch or relying on old CI, use the existing Freshness Train semantics. A master-head change can require rehydration/requalification even when the rolling quest state itself is valid.

```text
HEAD_CHANGE => FRESHNESS_RECHECK
HISTORICAL_CI_PASS != CURRENT_INTEGRATION_PASS
```

## Authority boundary

The pipeline grants no:

- execution authority;
- Message Board claim authority;
- evidence/truth standing;
- promotion authority;
- merge authority;
- release/deployment authority.

It is a persistent routing membrane for explicit agent cycles.
