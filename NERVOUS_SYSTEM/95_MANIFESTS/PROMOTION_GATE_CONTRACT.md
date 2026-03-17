# Promotion Gate Contract

## Purpose

No Hall, Temple, queue, manifest, or frontier closure may promote without the same gate checklist.

## Required Gate Checks

1. `witness_class`: direct evidence is named and cited.
2. `replay_proof`: rerun or verification surface exists and is readable.
3. `boundary_check`: contradiction and blocker handling remain explicit.
4. `economy_rank`: the move is lawful under current salience and build-budget pressure.
5. `writeback_quorum`: Hall, Temple, queue, manifest/restart, and receipt surfaces agree on the active frontier tuple.
6. `closure_condition`: successor frontier has a named owner lane, target artifact, and lawful writeback destination.

## Promotion Failure Law

- Missing witness keeps the frontier `NEAR` or `AMBIG`.
- Missing replay proof routes to `REPAIR_TICKET_QUEUE.md`.
- Failed boundary check routes to quarantine, not promotion.
- Missing writeback quorum forbids closure.
- Missing successor owner keeps the current frontier active.

## Quorum Surfaces

The minimum closure quorum is:

- Guild Hall quest or change surface
- Temple state or Temple quest surface
- active queue
- restart or control-state manifest
- one cited receipt or verification artifact
