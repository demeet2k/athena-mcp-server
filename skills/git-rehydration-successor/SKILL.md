---
name: git-rehydration-successor
description: Compile transparent, replayable successor batons for Git-persisted rehydration loops so long agent chains can self-steer without hidden tie-breaking or authority escalation.
---

# ATHENA Rehydration Successor V1

Use this skill when a rehydration loop has completed one bounded cycle and needs to choose the next bounded task from observed residuals, explicit candidates, or a partial current task.

## Coordinate

`ATHENA.KC144::GITΩ::REHYDRATION-SUCCESSOR::V1`

## Default behavior

`athena_rehydration_advance` self-steers by default. Before generating the next prompt it compiles a successor baton from the current completion.

Candidate sources are explicit:

1. `completion.next_task`, if supplied;
2. `completion.residuals`;
3. `completion.successor_candidates`;
4. current-task continuation only when the cycle is `PARTIAL`, `HELD`, or `NO_PROGRESS`.

A terminal completion emits no successor.

## Routing vector

Each candidate carries seven bounded routing coordinates:

```text
maximize:
  utility
  dependency_unblocking
  uncertainty_reduction
  novelty

minimize:
  risk
  cost
  repetition
```

Explicit metric values override source defaults. Missing values use transparent source heuristics and are labeled `SOURCE_HEURISTIC` or `MIXED`.

These scores are for routing only:

```text
ROUTING_SCORE != EVIDENCE
ROUTING_SCORE != AUTHORITY
```

## Selection algorithm

1. Normalize and deduplicate candidate task identities.
2. Pareto-prune candidates dominated on all seven routing coordinates.
3. Score only the nondominated frontier with the current successor policy.
4. If one candidate has a unique best score, emit `SELECTED`.
5. If multiple candidates share the best score inside `tie_epsilon`, emit `AMBIGUOUS` and preserve all tied candidates.
6. If no candidate exists, emit `NO_SUCCESSOR`.

Default tie policy is always `PRESERVE`; there is no hidden lexical winner.

## Baton

The persisted baton includes:

```text
candidate set
candidate IDs
metric origins
Pareto IDs
policy weights
selected candidate or ties
deferred candidates
selection reason
baton digest
```

The baton is embedded inside the normal rehydration completion object. Existing rehydration state, receipt, prompt, and chain digests therefore cover it without introducing a second checkpoint system.

## Ambiguity

`AMBIGUOUS` is not failure. The next prompt becomes a bounded ambiguity-resolution task that asks the next agent to gather evidence, refine policy, split the problem, or preserve the unresolved branch.

Do not choose one tied candidate merely to keep the chain moving.

## Preview

Use `athena_rehydration_successor_preview` to inspect the candidate/Pareto/tie structure without advancing or mutating the loop.

Useful for:

- reviewing an agent-supplied next task against residual alternatives;
- comparing explicit successor candidates;
- checking policy sensitivity;
- cross-agent handoff;
- debugging why a chain selected or refused a successor.

## Self-steering completion fields

`athena_rehydration_advance` accepts these optional completion fields:

```json
{
  "self_steer": true,
  "successor_candidates": [],
  "successor_policy": {
    "weights": {},
    "tie_epsilon": 1e-9
  }
}
```

Set `self_steer=false` only when a higher-level orchestrator intentionally owns the successor decision.

## Laws

- `SELF_STEER != SELF_AUTHORIZE`.
- `SUCCESSOR_BATON != TASK_TRUTH`.
- `ROUTING_SCORE != EVIDENCE`.
- `ROUTING_SCORE != AUTHORITY`.
- `AMBIGUITY != FAILURE`.
- `TIE => PRESERVE_UNTIL_NEW_EVIDENCE_OR_POLICY`.
- `BATON_DIGEST` proves the routing packet identity, not the correctness of the selected work.
