---
name: git-next-scout-benefit-canary
description: Apply a V9 held-out NEXT scout benefit candidate through a bounded reversible control-vs-canary routing membrane without mutating canonical V5 benefit priors or Message Board claim authority.
---

# NEXT Scout Benefit Canary V10

Use when a rolling NEXT pipeline has a V9 `BENEFIT_PRIOR_PROMOTION_CANDIDATE` and the next task is to let that learned value influence routing safely.

## Required sequence

1. Read/revalidate the V9 cohort evaluation.
2. Start a V10 canary with a bounded `lambda_weight` (default 0.10; hard max 0.25), cycle budget, and plan-set divergence bound.
3. Preserve two explicit lanes:
   - CONTROL = V6 calibrated costs + unchanged V5 benefits.
   - CANARY = same costs/feasibility + uniform bounded multiplier on the single validated prep kind.
4. Preview both lanes before applying.
5. If V9 evaluation drifted, the canonical benefit-table digest changed, the canary exceeds the frozen divergence bound, or the cycle budget is exhausted: route to CONTROL and roll back/expire the canary.
6. `athena_next_scout_canary_apply` may persist one routing decision only. Returned plan IDs still require the normal `athena_next_scout_claim` / Message Board ownership path.
7. Never call the canary decision scout execution, promotion, release, merge, truth, or a global reward-function update.

## Tools

- `athena_next_scout_canary_start`
- `athena_next_scout_canary_preview`
- `athena_next_scout_canary_apply`
- `athena_next_scout_canary_rollback`
- `athena_next_scout_canary_state`

## Core law

```text
V9_PROMOTION_CANDIDATE
  -> bounded canary routing influence
  -> normal Message Board claim
  -> explicit scout work

V9_PROMOTION_CANDIDATE
  != canonical V5 benefit prior mutation
```

The canary multiplier is deliberately generic across the target prep kind's existing V5 benefit coordinates. It is a bounded routing experiment, not evidence that a downstream outcome metric causally corresponds to any specific V5 semantic value dimension.

## Control/rollback

Structural rollback is executable in V10. Performance rollback is not yet claimed: V10 does not itself identify the causal effect of using the canary policy. That requires a later prospective control-vs-canary outcome membrane.
