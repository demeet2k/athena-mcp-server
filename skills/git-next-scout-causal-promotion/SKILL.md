---
name: git-next-scout-causal-promotion
description: Use the NEXT V9 held-out causal-promotion membrane when V8 has produced matched counterfactual candidates and the task is to validate them out of sample without mutating live scout benefit priors.
---

# NEXT Scout Causal Promotion V9

Use V9 after V8 counterfactual pair receipts exist. V9 is a validation/promotion-candidate layer, not live economy authority.

## Flow

1. Freeze discovery and validation pair IDs with `athena_next_scout_validation_freeze`.
2. Require the split basis to be independently sourced and explicitly assigned before outcome observation.
3. Keep discovery and validation pair IDs disjoint.
4. Keep every underlying treated/control V7 outcome receipt identity disjoint across the two cohorts.
5. Evaluate with `athena_next_scout_validation_evaluate`.
6. Use `athena_next_scout_validation_overlay` for a compact read-only standing.

## Default validation gates

- at least 3 pairs in discovery and 3 in validation;
- no within-cohort pseudoreplication;
- median effect >= +0.05 in both cohorts;
- sign consistency >= 2/3 in both cohorts;
- validation median retains >= 50% of discovery median;
- validation lower quartile is nonnegative.

Passing yields `BENEFIT_PRIOR_PROMOTION_CANDIDATE`. This is reversible nomination only.

## Hard laws

```text
DISCOVERY_SET != VALIDATION_SET
VALIDATION_ASSIGNMENT_MUST_PRECEDE_OUTCOME_OBSERVATION
RECEIPT_IDENTITY_CANNOT_LEAK_ACROSS_COHORTS
HELD_OUT_REPLICATION != RANDOMIZED_CAUSAL_PROOF
VALIDATION_FAILURE => ABSTAIN
V9_PROMOTION_CANDIDATE != LIVE_ECONOMY_MUTATION
```

Never use a V9 candidate to claim truth, promotion, merge, release, deployment, or live-benefit-prior authority. A later bounded apply/rollback membrane is required before routing priors can change.
