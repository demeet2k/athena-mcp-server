# AppI Corridor Truth

## Role

`AppI` owns corridor admissibility, health-aware truth, and transition safety.

## Current Operators

- `observer-corridor-nudge-compiler`
- `health-corridor-monitor`
- `truth-promotion-governor`

## Truth Flow

1. read corridor health
2. score evidence completeness
3. assign `OK`, `NEAR`, `AMBIG`, or `FAIL`
4. forward the verdict to promotion, quarantine, or replay

## Current Warning

Do not treat activity as truth when confidence is low or cooldown is still active.
