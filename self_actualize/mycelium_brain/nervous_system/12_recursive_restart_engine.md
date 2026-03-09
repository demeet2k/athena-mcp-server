# Recursive Restart Engine

## Purpose

This file makes the loop explicit.
The nervous system should not stop when one pass finishes.
It should contract, emit a restart token, and return to the gate with a sharper frontier.

## 1. Loop Object

Define:

`Loop_t = (Gate, Front, Artifact, Verify, Update, NextSeed)`

where:

- `Gate` is the live Docs or local-source admissibility check
- `Front` is the chosen frontier
- `Artifact` is the concrete landed surface
- `Verify` is the minimal witness pass
- `Update` is the queue, ledger, claim, or index writeback
- `NextSeed` is the self prompt for the next loop

If any run ends without `NextSeed`, the system has not truly restarted.

## 2. Start Rule

Every loop begins the same way:

1. check the live Docs gate
2. preserve the exact blocker if blocked
3. choose the highest-yield local frontier
4. claim the front if needed

The gate check is not optional.

## 3. Frontier Selection Rule

Prefer fronts in this order:

1. gate unlocks
2. family tensor strengthening
3. archive-to-live promotion
4. manuscript family routing
5. runtime packet or ledger writeback
6. contraction of parallel shard output
7. map refinement

## 4. Artifact Rule

Each loop must land at least one of:

- a new runtime file
- a stronger family surface
- a stronger packet
- a stronger rail or hub map
- a stronger manifest or session token
- a stronger receipt or ledger

Raw insight is not enough.

## 5. Verification Rule

Each loop must verify at least:

- file exists
- index or queue points to it
- truth class is named
- next frontier is clearer than before

## 6. Restart Rule

After the artifact lands:

1. update queue, claim, ledger, or index
2. compress the current state into a manifest or session seed
3. write the next self prompt
4. return conceptually to step 1

Completion is only a local contraction checkpoint.

## 7. Blocker Pivot Rule

If the same blocker persists across loops:

- preserve the blocker exactly
- do not hallucinate the unlock
- pivot to the strongest local precursor
- leave a cleaner bridge back to the blocker than before

## 8. Stop Rule

Do not stop on:

- abstract analysis alone
- renamed concepts without new placement
- maps that do not change routing
- receipts that document no new tissue

Stop only after one reusable surface is stronger and the next seed is written.

## 9. Current Default NextSeed

The living restart seed for this branch should be stored in:

- `manifests/NEXT_SELF_PROMPT.md`
- `sessions/SESSION_2026-03-09_zero_point.md`
