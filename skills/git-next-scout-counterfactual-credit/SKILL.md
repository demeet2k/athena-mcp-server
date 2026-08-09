# NEXT Scout Counterfactual Credit V8

Use this skill when the rolling NEXT scout stack has V7 delayed focus-outcome receipts and the task is to compare prepared versus unprepared completed quests without treating raw association as causal proof.

## Coordinate

`ATHENA.KC144::GITΩ::NEXT::SCOUT-COUNTERFACTUAL-CREDIT::V8`

## Tools

- `athena_next_scout_counterfactual_pair_record`
- `athena_next_scout_counterfactual_estimate`
- `athena_next_scout_counterfactual_overlay`

## Pair contract

A lawful matched pair requires:

1. two distinct V7 focus-outcome receipts from the same pipeline;
2. distinct completed quests;
3. the treated receipt contains the target prep kind;
4. the control receipt does not contain the target prep kind;
5. an observed, non-empty matching source;
6. `independent_of_scout=true`;
7. non-empty treated/control pre-treatment covariate objects with identical schemas and exact canonical equality;
8. at least one common downstream V7 outcome score.

Never match on completion status, completion summary, evidence refs, test results, rework, blocker-resolution results, success/failure, or any other post-treatment outcome. Doing so conditions on variables downstream of treatment and invalidates the comparison membrane.

## Estimation

For a prep kind and outcome metric, compute matched pair deltas:

`delta = treated outcome - control outcome`.

Aggregate with the median. Shrink toward a zero-effect prior:

`effect_candidate = n * median_delta / (prior_strength + n)`.

Default gates:

- at least 3 independent pairs;
- no reuse of a treated receipt on the treated side;
- no reuse of a control receipt on the control side;
- at least 2/3 of pair deltas share the dominant sign;
- median effect is at least +0.05.

If any gate fails, abstain. Do not fill missing outcomes with zero.

## Standing and authority

Passing a gate yields `BENEFIT_PRIOR_CANDIDATE`, not causal proof. V8 is quasi-experimental matched observational analysis only. It cannot mutate V5/V6 benefit priors, alter allocation, claim work, promote evidence, merge, deploy, or release.

The V8 overlay must retain:

- `benefit_prior_mutation=NONE`
- `allocation_effect=NONE`
- `claim_effect=NONE`
- `promotion_effect=NONE`

## Laws

- `POST_TREATMENT_VARIABLES_CANNOT_DEFINE_MATCHES`
- `SCOUT_SELF_REPORT != MATCHING_AUTHORITY`
- `MATCHED_OBSERVATIONAL_CONTRAST != RANDOMIZED_CAUSAL_PROOF`
- `PSEUDOREPLICATION => ABSTAIN`
- `WEAK_OR_INCONSISTENT_EFFECT => ABSTAIN`
- `V8_CANDIDATE != LIVE_ECONOMY_MUTATION`
- `GREEN_CI != MERGE_AUTHORITY`

## Next architectural boundary

V9 should be a promotion/validation membrane: held-out validation, prospective randomization where lawful, or another stronger design must qualify a V8 candidate before any calibrated benefit prior can enter the live economy.
