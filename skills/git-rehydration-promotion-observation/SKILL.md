---
name: git-rehydration-promotion-observation
description: Observe exact-head PROMOTION.2 standing and host-verified GitHub checks from a persisted rehydration loop without granting promotion, merge, release, or deployment authority.
---

# ATHENA Rehydration Promotion Observation V1.2

Use this skill when a Git rehydration chain needs to know whether its current or cycle-specific Git head has already been externally qualified.

## Coordinate

`ATHENA.KC144::GITΩ::REHYDRATION-PROMOTION-OBSERVATION::V1.2`

## Tool

`athena_rehydration_promotion_observe`

The tool is deliberately read-only. It observes four independent coordinates:

1. the persisted rehydration-loop causal state;
2. the exact target Git head;
3. persisted `PROMOTION.2` receipts for that exact head and deterministic replay standing;
4. current host-bound GitHub check-suite verification when configured.

It never calls `PromotionLedger.evaluate` and never creates a `PROMRUN`.

## Target head modes

- `CURRENT_GIT` — current configured Git checkout head.
- `CYCLE_WORK` — `work_head` recorded in the latest rehydration receipt.
- `LOOP_CHECKPOINT` — Git commit that last wrote the loop `state.json`.
- `EXPLICIT` — caller provides `explicit_head`; identity is not inferred.

Keep these coordinates separate. A cycle work commit, loop checkpoint commit, PR candidate head, and current checkout may legitimately differ.

## Promotion observation states

- `PERSISTED_QUALIFIED_OBSERVED` — an exact-head replay-valid persisted standing is unambiguously `QUALIFIED`.
- `ATTESTED_READY_OBSERVED` — persisted current semantics are caller-attested ready but not host-qualified.
- `PROMOTION_BLOCKED_OBSERVED` — exact-head persisted standing is blocked.
- `PROMOTION_CONTESTED` — replay-valid exact-head PROMRUNs disagree in standing; do not choose one silently.
- `PROMOTION_REPLAY_HOLD` — receipts exist but no exact-head receipt replayed deterministically.
- `CHECKS_VERIFIED_PROMOTION_UNQUALIFIED` — host GitHub checks are independently verified but no persisted exact-head `QUALIFIED` standing was observed.
- `PROMOTION_UNOBSERVED` — neither persisted promotion standing nor qualifying external checks establish current promotion state.
- `LOOP_INTEGRITY_HOLD` — the local persisted rehydration chain itself does not replay cleanly.

## Critical distinction

`GithubPromotionVerifier.verify(head)` verifies one coherent required GitHub Actions check suite for the exact head. That is external evidence only.

It is **not** equivalent to a persisted `PROMOTION.2 QUALIFIED` receipt:

```text
CHECKS_VERIFIED != PROMOTION_QUALIFIED
```

The privileged promotion bridge remains the only path that can evaluate and persist a trusted `QUALIFIED` PROMRUN.

## V1.1 compatibility

If Rehydration Control V1.1 is installed, V1.2 also observes its receipt-bound `cycle_gate` and preserves:

```text
VERIFIED_CYCLE != PROMOTION_QUALIFIED
```

If V1.1 is absent, `cycle_gate` is simply null; V1.2 does not manufacture it.

The routing successor baton is also read from the frozen completion receipt when present. It remains routing context, not authority.

## Usage algorithm

1. Call `athena_rehydration_promotion_observe` with the loop ID.
2. Choose the target-head mode explicitly when current Git is not the intended promotion candidate.
3. Inspect `loop.loop_verification` first.
4. Inspect `persisted_promotion.standing` and every returned run/replay packet.
5. Treat `external_checks` as a separate observation plane.
6. If persisted exact-head statuses disagree, preserve `PROMOTION_CONTESTED`.
7. Continue routing based on policy, but never merge/release merely because this observer reports qualification.

## Laws

- `REHYDRATION_MAY_OBSERVE_PROMOTION_BUT_MAY_NOT_GRANT_PROMOTION`.
- `CHECKS_VERIFIED != PROMOTION_QUALIFIED`.
- `PROMOTION_RUN != MERGE_AUTHORITY`.
- `EXACT_HEAD_IDENTITY_IS_EXPLICIT_NOT_INFERRED`.
- `CONTESTED_PROMRUNS_REMAIN_CONTESTED`.
- `REPLAY_MATCH != EXTERNAL_REVERIFICATION`.
- `CYCLE_VERIFIED != PROMOTION_QUALIFIED != MERGE_AUTHORIZED`.
