---
name: git-rehydration-loop
description: Run long, explicit, Git-persisted self-prompt orchestration chains with exact-head rehydration, bounded deliberation passes, receipts, replay verification, and cross-agent handoff.
---

# ATHENA Git Rehydration Loop V1

Use this skill when a development objective is too large for one bounded agent cycle and must continue across multiple turns, agents, or explicit work sessions without relying on stale conversational memory.

## Canonical coordinate

`ATHENA.KC144::GITΩ::REHYDRATION-LOOP::V1`

## What the loop does

The loop persists one explicit causal cycle at a time:

```text
hydrate exact Git prompt/frontier
→ compile bounded self-prompt
→ agent completes one explicit cycle
→ agent commits substantive work
→ submit observed completion receipt
→ verify checkpoint ancestry/digests
→ persist receipt and new loop state
→ rehydrate new Git head
→ compile the next self-prompt
```

It does **not** perform hidden background work. A later turn or another agent explicitly invokes the next cycle.

## MCP tools

- `athena_rehydration_start` — create a loop from an exact Git head and compile step `0000`.
- `athena_rehydration_advance` — after the current prompt is completed and work is committed, validate the completion, write the cycle receipt, rehydrate the new head, and compile the next prompt.
- `athena_rehydration_resume` — return the exact current prompt, state, chain and checkpoint for cross-agent handoff.
- `athena_rehydration_verify` — replay prompt/receipt digests and Git ancestry for the whole loop.
- `athena_rehydration_index` — list all persisted loops in the configured Git brain.

## Starting a loop

Supply the exact current Git head. Use `depth_mode=deep` for the default seven-pass cycle:

```text
reconstruct
retrieve
generate
attack
execute
verify
synthesize
```

The start tool writes only under:

```text
prompts/rehydration/<loop_id>/
```

It creates:

```text
state.json
prompts/0000.md
events/0000-start.json
```

## Completing a cycle

Read and execute the current `compiled_self_prompt`. Complete one bounded intervention with available tools and authority. Commit substantive work outside the loop directory. Then call `athena_rehydration_advance` with:

- exact `checkpoint_head` from the prior start/advance result;
- exact state and prompt digests;
- `observed=true`;
- a non-empty summary;
- every required deliberation pass for `SUCCEEDED` or `PARTIAL`;
- actual test/evidence references;
- an optional bounded `next_task`.

The advance tool verifies that the checkpoint is an ancestor of the work head and that no newer loop checkpoint has appeared. It persists:

```text
receipts/<step>.json
prompts/<step>.md
state.json
```

in a new CAS-guarded Git commit.

## Remote modes

- `REQUIRED` — fresh shared frontier and post-write publication verification are mandatory; otherwise return a typed hold.
- `BEST_EFFORT` — continue locally when the remote is unavailable, but `durable_return=false`.
- `DISABLED` — local/test mode; never claim a shared return.

## Long-chain controls

Every loop has:

- `max_steps` — hard cycle ceiling, at most 256;
- `max_no_progress` — repeated no-progress ceiling;
- `max_prompt_chars` — bounded generated prompt size;
- explicit stop conditions;
- terminal states `COMPLETE`, `HOLD_MAX_STEPS`, `HOLD_NO_PROGRESS`, and `ABORTED`.

`NO_PROGRESS` may be recorded only as an observed cycle. Repeated no-progress becomes a hold rather than unbounded self-prompt recursion.

## Cross-agent handoff

A new agent calls `athena_rehydration_resume(loop_id)`. The returned packet contains:

```text
loop status
step index
checkpoint head
current Git head
state digest
prompt digest
chain digest
required passes
compiled self-prompt
```

If the work head is ahead of the loop checkpoint, the agent should finish the existing prompt and advance the loop, not start a competing loop checkpoint.

## Verification

Run `athena_rehydration_verify` before promotion or when a handoff is disputed. `PASS` verifies:

- sequential receipt numbering;
- start/prompt/receipt/state digests;
- hash-chain continuity;
- exact receipt index;
- current prompt identity;
- Git ancestry from each checkpoint to its work head.

It does not prove world truth or task correctness; those require the recorded tests and evidence.

## Laws

- `CYCLE != BACKGROUND_EXECUTION`.
- `SELF_PROMPT != HIGHER_AUTHORITY`.
- `GIT_COMMIT != OBSERVED_SUCCESS`.
- `LOCAL_COMMIT != SHARED_RETURN` unless publication is freshly verified.
- `HEAD_CHANGE => REHYDRATE` before the next consequential decision.
- `PROMPT_COMPLETION != PROMPT_PROMOTION`.
- `REPEATED_NO_PROGRESS => HOLD`.
- Never edit loop state, prompt, receipt, or chain files manually.
