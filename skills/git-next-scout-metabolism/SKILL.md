---
name: git-next-scout-metabolism
description: Record observed resource-cost receipts for completed NEXT scout prep work and calibrate scout-economy cost priors without self-training value, evidence, or authority.
---

# NEXT Scout Metabolism V6

Use this skill after a V3 scout has returned a Breadth V2 prep result and there are actual resource measurements to record.

## Coordinate

`ATHENA.KC144::GITΩ::NEXT::SCOUT-METABOLISM::V6`

## Flow

```text
prep plan
→ explicit scout work
→ Breadth V2 observed result
→ athena_next_scout_receipt_record
→ immutable observed-cost receipt
→ athena_next_scout_calibrate
→ calibrated cost priors
```

## Record only observations

`athena_next_scout_receipt_record` requires the prep result to already exist and accepts only measurement coordinates explicitly marked `observed=true` with a non-empty measurement source.

Supported cost coordinates:

- `tokens`
- `minutes`
- `tool_calls`
- `coordination`
- `git_risk`

Omit unavailable measurements. Never encode a missing measurement as zero.

## Calibration

`athena_next_scout_calibrate` is read-only. For each prep kind and resource coordinate it computes the median of observed receipts, then shrinks that median toward the V5 planning prior:

```text
calibrated = (prior_strength * prior + n * observed_median) / (prior_strength + n)
```

Default `prior_strength=3`.

One receipt therefore cannot abruptly replace a mature prior. As observations accumulate, the calibrated estimate moves toward the empirical median.

## Authority boundary

V6 calibrates cost only. It does not learn or infer task value from scout self-report.

```text
PREDICTION != OBSERVATION
OBSERVED_COST != TASK_VALUE
COST_CALIBRATION != BENEFIT_CALIBRATION
SCOUT_RECEIPT != EVIDENCE_PROMOTION
CALIBRATION != CLAIM
CALIBRATION != EXECUTION
```

A measurement receipt is an observed-measurement assertion bound to its source/evidence reference. It is not automatically an independently verified measurement.

## Long-chain use

For each completed scout return:

1. preserve the Breadth V2 result;
2. record whatever resource coordinates were actually measured;
3. periodically call calibration;
4. use the calibrated profile as the empirical input for the next resource-economy integration layer;
5. never backfill missing measurements with guesses.
