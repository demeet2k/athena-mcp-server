# LEDGER_truth_promotion_control_plane

## SurfaceClass

`ledger`

## Front

Truth-promotion control plane alignment

## State

`NEAR`

## Objective

Keep packet verdicts, corridor truth, replay safety, and benchmark evidence aligned
enough that truth promotion does not outrun witness.

## Targets

- hub control surfaces for `AppG`, `AppI`, `AppL`, and `AppM`
- restart engine manifest
- weakest-front queue
- restart neuron

## Witness

- hub control surfaces exist for `AppG`, `AppI`, `AppL`, and `AppM`
- restart engine manifest exists
- weakest-front queue exists
- restart neuron exists

## Active Truth Rule

Packet verdicts must be informed by:

- corridor health
- evidence completeness
- replay safety
- benchmark receipts

## Current Residual

Family-local queue density is still thinner than the control plane.

## Next Writeback

- `22_control_plane_grammar.md`
- one aligned packet
- one aligned manifest

## RestartSeed

Promote the next truth-bearing front only after its packet and manifest expose the same
state, witness path, and writeback destination.
