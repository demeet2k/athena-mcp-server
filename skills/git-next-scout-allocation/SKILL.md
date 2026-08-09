---
name: git-next-scout-allocation
description: Allocate bounded scout capacity across rolling NEXT Q2/Q3 prep plans without claiming or executing work.
---

# ATHENA NEXT Scout Allocation V4

Use this skill when a rolling NEXT pipeline has more staged prep plans than available scout capacity.

## Canonical coordinate

`ATHENA.KC144::GITΩ::NEXT::SCOUT-ALLOCATION::V4`

## Tool

`athena_next_scout_allocate`

The allocator is read-only. It observes:

- the exact current rolling-pipeline state;
- Breadth V2 prep plans and observations;
- active Message Board scout claims;
- maximum scout capacity and reserve slots.

It returns which exact `plan_id` values are structurally best to claim next.

## Capacity law

```text
usable_capacity = max_scouts - reserve_slots
available_new_slots = usable_capacity - active_scout_claim_count
```

Reserve capacity is deliberately left unused.

## Candidate exclusions

Do not allocate a prep plan when it is:

- bound to a stale pipeline-state digest;
- attached to Q1 instead of staged Q2/Q3;
- already observed;
- already claimed;
- not in PLANNED state;
- of an unknown prep kind.

## Structural policy

The default policy is deterministic and routing-only:

1. cover both staged quests when capacity permits;
2. maximize structural readiness value;
3. maximize prep-kind diversity;
4. prefer nearer Q2 when otherwise equal.

Kind order:

```text
DEPENDENCY_MAP > TEST_DESIGN > RISK_SCAN > RETRIEVAL_PLAN > INTERFACE_MAP > SOURCE_REVIEW
```

These are routing weights, not evidence or truth values.

## Ambiguity

If several scout subsets have exactly the same optimal policy key, return all of them as `AMBIGUOUS_ALLOCATION`.

A caller may pass `choice_plan_ids`, but only if that exact set is already one of the computed optimal allocations. The allocator never invents an arbitrary tie-break.

## Execution

After a unique or explicitly resolved allocation is returned, use `athena_next_scout_claim` separately for each chosen prep plan. Message Board remains the claim authority.

## Laws

- `ALLOCATION != CLAIM`.
- `ALLOCATION != EXECUTION`.
- `ROUTING_WEIGHT != EVIDENCE`.
- `RESERVE_CAPACITY_IS_NOT_ALLOCATED`.
- `ACTIVE_SCOUT_CLAIMS_CONSUME_CAPACITY`.
- `AMBIGUOUS_OPTIMAL_ALLOCATION != HIDDEN_TIE_BREAK`.
- `MESSAGE_BOARD_REMAINS_CLAIM_AUTHORITY`.
