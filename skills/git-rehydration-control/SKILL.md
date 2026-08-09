---
name: git-rehydration-control
description: Add Message Board ownership and cycle-local verification gates to long Git rehydration chains without duplicating the canonical successor-routing or handoff-delta organs.
---

# ATHENA Git Rehydration Control V1.1

Use this skill with `git-rehydration-loop` when a long explicit chain can span several agents and must prevent duplicate work.

## Coordinate

`ATHENA.KC144::GITΩ::REHYDRATION-CONTROL::V1.1`

## Ownership boundaries

```text
MessageBoardRuntime      = claim / lease / coordination handoff authority
rehydration_successor    = WHAT NEXT routing authority
rehydration_handoff      = WHAT TO REHYDRATE delta/handoff authority
RehydrationLoopRuntime   = causal prompt / receipt / replay authority
RehydrationControl V1.1  = conjunction + local cycle gate only
```

Do not create another lease file, successor selector, or handoff-delta algorithm in this layer.

## Tools

### `athena_rehydration_claim`

Claim exact work key `rehydration:<loop_id>` through Message Board V1. The loop directory is declared as the work target. Duplicate primary claims remain a Message Board hold.

### `athena_rehydration_advance_claimed`

Use this instead of raw `athena_rehydration_advance` for coordinated chains. It requires the caller to hold the current active PRIMARY Message Board claim and rejects Git changes confined to:

```text
prompts/rehydration/<loop_id>/
runtime/message_board/v1/
```

as non-substantive control traffic.

The tool adds `_rehydration_control.cycle_gate` to the completion receipt and then delegates to the existing RehydrationLoopRuntime. Existing successor auto-steering remains responsible for `successor_baton` and next-prompt routing.

### `athena_rehydration_claim_handoff`

Transfers **only coordination ownership** through Message Board `HANDOFF` release semantics. It deliberately does not derive or consume the rehydration handoff delta.

After claim handoff, the target agent should use:

```text
athena_rehydration_handoff_delta
athena_rehydration_handoff_resume
```

or ordinary resume as appropriate.

### `athena_rehydration_resume_controlled`

Returns shared-current loop state plus active Message Board owner(s), unread messages, prior local cycle gate, and the receipt-bound canonical routing successor when present.

## Cycle gate

States:

```text
VERIFIED_CYCLE
WORK_COMMITTED
OBSERVED_CYCLE
HOLD_CYCLE
```

`VERIFIED_CYCLE` requires:

- `completion.status == SUCCEEDED`;
- substantive work outside loop/Message Board control paths;
- at least one evidence reference;
- at least one recorded test;
- all recorded test states `PASS`.

Every cycle gate carries:

```text
promotion_qualified = false
authority = LOCAL_CYCLE_ONLY
```

because local cycle verification is not the Promotion/Release system.

## Long-chain pattern

```text
claim loop through Message Board
→ resume current prompt/handoff
→ execute bounded cycle
→ commit substantive work
→ advance_claimed
→ canonical successor compiler updates next prompt when routing was left open
→ repeat
→ claim_handoff when ownership changes
→ target consumes canonical handoff delta and claims lane
```

## Laws

- `MESSAGE_BOARD_IS_SOLE_CLAIM_AUTHORITY`.
- `WHAT_NEXT_OWNED_BY_REHYDRATION_SUCCESSOR`.
- `WHAT_TO_REHYDRATE_OWNED_BY_REHYDRATION_HANDOFF`.
- `MESSAGE_BOARD_ONLY_CHANGE != SUBSTANTIVE_WORK`.
- `CLAIM_HANDOFF != REHYDRATION_HANDOFF_DELTA`.
- `HANDOFF_ROUTE != HANDOFF_CONSUMPTION`.
- `CYCLE_VERIFIED != PROMOTION_QUALIFIED != MERGE_AUTHORIZED`.
