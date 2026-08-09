---
name: git-next-quest-breadth
description: Prepare staged Q2/Q3 quests while Q1 remains the sole focus, accumulating dependency/retrieval/test/risk/source/interface context for future rehydration without claiming or completing staged work.
---

# ATHENA Rolling NEXT Breadth V2

Use this skill after a rolling three-quest pipeline exists and the user wants deeper mass orchestration without pretending Q2/Q3 are already executing.

## Geometry

```text
Q1 = sole mutable focus
Q2 = staged + preparation allowed
Q3 = staged + preparation allowed
```

Preparation may happen around Q2/Q3 as explicit bounded work products:

```text
DEPENDENCY_MAP
RETRIEVAL_PLAN
TEST_DESIGN
RISK_SCAN
SOURCE_REVIEW
INTERFACE_MAP
```

These packets are not quest execution.

## Workflow

1. Read `athena_next_pipeline_state` and preserve exact `pipeline_state_digest`.
2. Call `athena_next_pipeline_prepare_staged` for Q2/Q3.
3. Execute any selected preparation packet explicitly using available read/research/test-design tools.
4. Record the observed result with `athena_next_pipeline_record_prep`.
5. Do not mark Q2/Q3 complete and do not mutate Q1.
6. When Q2 later rotates into Q1, call `athena_next_pipeline_prep_context` to recover its accumulated preparation packet set.
7. Treat that set as rehydration context only; validate any facts/evidence again according to the owning subsystem.

## Core law

```text
PREPARATION != EXECUTION
```

A staged quest may become better prepared without becoming completed.

## Authority

Preparation packets grant no:

- Message Board claim;
- campaign worker lease;
- execution authority;
- evidence/truth standing;
- promotion authority;
- merge/release/deployment authority.

## Freshness

Every prep plan/result is bound to the exact rolling pipeline state digest. If the pipeline has rotated since a plan was issued, late result admission fails closed. Existing observations already persisted for a quest remain readable by quest identity when that quest later becomes Q1.

## Why

The goal is to combine:

```text
longitudinal momentum: Q1 -> Q2 -> Q3 -> ...
```

with:

```text
anticipatory preparation: staged future quests are already mapped before focus arrives
```

without inventing hidden parallel execution.
