# AppM Replay Closure

## Role

`AppM` owns replay-safe closure, deterministic restart, and manifest carryforward.

## Closure Law

A run is only closed if it leaves:

- one restart token
- one wave summary
- one packet truth state
- one next frontier

## Current Operators

- `restart-seed-orchestrator`
- `session-handoff-packer`
- `weakest-front-reopener`

## Failure Mode

If replay path is missing, closure is false and the run remains `NEAR`.
