# Meta Lane Decision Contract

## Purpose

Every meta-lane run must emit one blocker-honest decision record instead of a loose summary.

## Required Fields

- `lane_id`
- `role`
- `chosen_frontier`
- `frontier_family`
- `active_frontier_tuple`
- `packet_freshness`
- `blocker_truth`
- `witness_basis`
- `allowed_writeback_set`
- `restart_seed`
- `receipt_surface`

## Active Frontier Tuple

The tuple must keep these control facts separate:

- `front_id`
- `current_carried_witness`
- `active_local_subfront`
- `next_hall_seed`
- `next_temple_handoff`
- `reserve_frontier`
- `blocked_external_front`
- `separate_runtime_seed`

## Decision Rules

1. Read all six scheduler packets before choosing a frontier.
2. Treat scheduler packets as timing context only.
3. If more than `2` packet lanes are stale, do not open a new Hall-local frontier unless the move is a repair, contraction, or synchronization pass.
4. If packet suggestions disagree, choose by witness class, leverage, replay value, blocker honesty, and boundary safety.
5. If the same frontier repeats for `3` consecutive cycles without a new artifact, emit a repair or compression escalation instead of cosmetic rewording.
6. Do not close a frontier unless the active tuple agrees across Hall, Temple, queue, manifests, and the cited receipt.

## Non-Compressible Fields

- blocker truth
- active frontier tuple
- packet freshness
- allowed writeback set
- restart seed

## Minimum Report Law

Each meta-lane report must separate:

1. packet freshness
2. frontier continuity
3. actual writebacks landed
4. next restart law
