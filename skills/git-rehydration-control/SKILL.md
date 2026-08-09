---
name: git-rehydration-control
description: Coordinate long Git rehydration chains across agents using Message Board ownership, deterministic successor derivation, and cycle-local verification gates without confusing work completion with promotion.
---

# ATHENA Git Rehydration Control V1.1

Use this skill after `git-rehydration-loop` when a loop must survive multiple explicit cycles or pass between agents without duplicate work.

## Coordinate

`ATHENA.KC144::GITΩ::REHYDRATION-CONTROL::V1.1`

## Architecture

```text
RehydrationLoopRuntime = causal prompt/receipt authority
MessageBoardRuntime    = sole coordination/claim authority
RehydrationControl     = bridge: claim check + successor + local cycle gate
```

Never create a second lease/claim store for rehydration. Message Board V1 owns presence, exact work-key exclusion, collaboration, heartbeats and handoff.

## Tools

### `athena_rehydration_claim`

Claims `rehydration:<loop_id>` through Message Board using the loop path as the target. Duplicate primary work claims fail closed at the board.

### `athena_rehydration_advance_claimed`

Use instead of the raw advance tool for coordinated long chains. It requires the caller to hold the active PRIMARY Message Board claim, rejects message-board-only commits as substantive work, and then:

1. reads the exact loop state;
2. verifies current claim ownership;
3. calculates material Git paths excluding loop/control files;
4. derives the next bounded task;
5. emits a local cycle gate;
6. embeds both packets inside the completion receipt;
7. delegates persistence and next-prompt compilation to RehydrationLoopRuntime.

Successor precedence is deterministic:

```text
explicit completion.next_task
> observed completion residual
> fresh frontier selected item
> fresh frontier residual
> current task fallback
```

The chosen successor changes the **next prompt**, not authority.

### `athena_rehydration_handoff`

Releases the current board claim with `HANDOFF` semantics and routes it to a target agent. The target must read the board, claim the released `rehydration:<loop_id>` lane, then resume the loop. Message routing does not prove message consumption.

### `athena_rehydration_resume_controlled`

Returns the ordinary rehydration packet plus active Message Board owners, unread messages, and the previous cycle's successor/gate packet.

## Cycle gates

`cycle_gate.state` is one of:

```text
VERIFIED_CYCLE
WORK_COMMITTED
OBSERVED_CYCLE
HOLD_CYCLE
```

`VERIFIED_CYCLE` currently requires:

- `status=SUCCEEDED`;
- substantive Git paths outside the rehydration and Message Board namespaces;
- at least one evidence reference;
- at least one test and every recorded test `PASS`.

Every gate carries:

```text
promotion_qualified = false
authority = LOCAL_CYCLE_ONLY
```

because:

```text
CYCLE_VERIFIED != PROMOTION_QUALIFIED != MERGE_AUTHORIZED
```

Promotion remains the separate exact-head Promotion/Release system.

## Cross-agent algorithm

```text
agent A claims loop
→ resume exact prompt
→ commit one bounded work slice
→ advance_claimed
→ optionally repeat
→ handoff(agent B)
→ agent B reads Message Board
→ agent B claims released work_key
→ resume_controlled
→ continue from exact loop checkpoint
```

## Laws

- `MESSAGE_BOARD_IS_SOLE_CLAIM_AUTHORITY`.
- `SELF_PROMPT != CLAIM_AUTHORITY`.
- `SUCCESSOR_DERIVATION != PROMOTION_AUTHORITY`.
- `MESSAGE_BOARD_ONLY_CHANGE != SUBSTANTIVE_WORK`.
- `HANDOFF_ROUTE != HANDOFF_CONSUMPTION`.
- `CYCLE_VERIFIED != PROMOTION_QUALIFIED != MERGE_AUTHORIZED`.
