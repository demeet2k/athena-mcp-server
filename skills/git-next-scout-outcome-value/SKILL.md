---
name: git-next-scout-outcome-value
description: Associate earlier staged prep with later observed focus outcomes after the quest actually completes, while preserving the distinction between downstream association and causal effect.
---

# NEXT Scout Outcome Value V7

Use after a quest that previously received Breadth/Scout preparation has rotated into Q1 and actually completed focus execution.

## Flow

```text
prep observations for Q2/Q3
→ quest later becomes Q1
→ explicit focus execution
→ pipeline completion
→ athena_next_focus_outcome_record
→ athena_next_scout_value_calibrate
→ optional athena_next_scout_value_overlay
```

## Rules

- A scout never rates its own value.
- Record only sourced downstream outcome measurements.
- Missing measurements remain missing; never synthesize zeros.
- V7 reports delayed observational association by prep kind.
- `OBSERVED_ASSOCIATION != CAUSAL_EFFECT`.
- V7 does not alter V5/V6 benefit priors or allocation decisions.
- The explanatory overlay has `allocation_effect=NONE`.
- Message Board remains claim authority; V7 has no claim/execution/promotion/merge/release authority.

## Supported downstream metrics

- `focus_success` — sourced observed boolean.
- `test_pass_ratio` — sourced observed value in [0,1].
- `rework_count` — sourced observed integer >=0.
- `blocker_resolution_ratio` — sourced observed value in [0,1].

## Why delayed observation matters

Preparation can only be evaluated after the prepared quest reaches focus and produces a real downstream result. Even then, V7 records correlation/association because several prep kinds may coexist and other factors may drive the outcome. Counterfactual or held-out evidence is required before causal credit can be assigned.
