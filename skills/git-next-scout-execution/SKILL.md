---
name: git-next-scout-execution
description: Use Message Board to claim and return bounded staged PREP work for Q2/Q3 in a rolling NEXT pipeline without mutating Q1 or completing the parent quest.
---

# ATHENA NEXT Scout Execution V3

Use this skill after a rolling NEXT pipeline has Q1 focus plus staged Q2/Q3 and Breadth V2 prep plans exist.

## Geometry

```text
Q1 = sole mutable focus
Q2 = staged + scoutable prep
Q3 = staged + scoutable prep
```

Scouts claim prep units, not quests:

```text
next-prep:<pipeline_id>:<plan_id>
```

## Claim

Call `athena_next_scout_claim` for exactly one Breadth V2 `plan_id`. Message Board remains the sole coordination/claim authority.

The returned scope includes one target packet path. A scout may perform explicit research/retrieval/test-design/risk/dependency work outside the runtime, but its runtime return is limited to one prep result.

## Return saga

Use `athena_next_scout_return` only after the scout has actually observed its preparation result.

```text
active exact Message Board claim
→ Breadth V2 result record
→ shared Git publication
→ claim release
```

If publication fails, do not abandon the claim. The tool returns `SCOUT_RESULT_LOCAL_PUBLISH_HOLD` and preserves ownership for recovery.

## Recovery

- `athena_next_scout_status` observes shared claim standing.
- `athena_next_scout_release` explicitly releases/pauses an active scout claim.
- A stale pipeline-state digest means the result must be re-evaluated against the new rolling state; do not silently import it.

## Firewalls

```text
SCOUT_CLAIM != QUEST_CLAIM
SCOUT_WORK != BACKGROUND_EXECUTION
SCOUT_MAY_NOT_MUTATE_Q1
SCOUT_MAY_NOT_COMPLETE_STAGED_QUEST
SCOUT_RESULT != EVIDENCE_PROMOTION
RESULT_PERSISTED_BEFORE_SCOUT_RELEASE
LOCAL_RESULT != SHARED_RETURN_UNTIL_PUBLISHED
```

Scout preparation can reduce future reconstruction cost when Q2/Q3 rotate into focus, but it does not mean those quests have already executed.
