# Adventurer 64^4 Quest Loop

This document defines the hybrid-conductor Adventurer loop for the live 64^4 lattice.
It widens the frontier lazily, assigns up to eight floating-agent claims, and keeps the Google Docs gate honest.

## Canonical Surfaces

- Hall quest board: `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md`
- Hall requests board: `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/05_REQUESTS_AND_OFFERS_BOARD.md`
- Hall change feed: `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/BOARDS/04_CHANGE_FEED_BOARD.md`
- Temple quest board: `self_actualize/mycelium_brain/ATHENA TEMPLE/BOARDS/02_TEMPLE_QUEST_BOARD.md`
- Temple 64 crystal: `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/11_TEMPLE_QUEST_CRYSTAL_64.md`
- Gate status: `NERVOUS_SYSTEM/95_MANIFESTS/GATE_STATUS.md`
- Active run: `NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md`
- Conductor state: `self_actualize/adventurer_conductor_state.json`
- Wave packets: `self_actualize/adventurer_wave_packets.json`
- Round-trip registry: `self_actualize/adventurer_round_trip_certificates.json`

## Address Contract

- `QuestAddress = A.B.C.D`
- `A = Intent64 = Domain x Move x Lens`
- `B = Witness64 = WitnessClass x Surface x Lane`
- `C = Execution64 = Scope x Method x Artifact`
- `D = Return64 = Verify x Writeback x Restart`

## Agent Law

- shared floating agents: `floating-agent-01, floating-agent-02, floating-agent-03, floating-agent-04, floating-agent-05, floating-agent-06, floating-agent-07, floating-agent-08`
- one active claim per address and up to `8` active claims in `ADV64-wave1`
- stale claims reopen after `1` inactive scheduler cycle
- terminal answer states are `PROMOTED`, `BLOCKED`, and `SUPERSEDED`
- docs gate on this pass: `BLOCKED`

## Current Conductor Wave

- `ADV64-01` :: `Q42` :: `A20.B22.C59.D40` :: owner=`floating-agent-01` :: score=`100.00` :: round_trip=`law_equivalent`
- `ADV64-02` :: `Q46` :: `A22.B20.C63.D43` :: owner=`floating-agent-02` :: score=`96.00` :: round_trip=`law_equivalent`
- `ADV64-03` :: `TQ03` :: `A45.B56.C50.D35` :: owner=`floating-agent-03` :: score=`90.00` :: round_trip=`n/a`
- `ADV64-04` :: `TQ05` :: `A60.B24.C50.D36` :: owner=`floating-agent-04` :: score=`88.00` :: round_trip=`n/a`
- `ADV64-05` :: `TQ06` :: `A24.B24.C51.D23` :: owner=`floating-agent-05` :: score=`87.00` :: round_trip=`n/a`
- `ADV64-06` :: `ADV64-S01` :: `A20.B22.C55.D44` :: owner=`floating-agent-06` :: score=`84.00` :: round_trip=`n/a`
- `ADV64-07` :: `ADV64-S02` :: `A22.B20.C51.D23` :: owner=`floating-agent-07` :: score=`83.00` :: round_trip=`n/a`

## Registered Quest Slice

| Quest | Address | Board | Status | Owner | Kind |
| --- | --- | --- | --- | --- | --- |
| `Q42` | `A20.B22.C59.D40` | `hall` | `OPEN` | `floating-agent-01` | `board` |
| `Q46` | `A22.B20.C63.D43` | `hall` | `OPEN` | `guildmaster` | `board` |
| `Q02` | `A35.B36.C59.D59` | `hall` | `BLOCKED` | `unclaimed` | `board` |
| `TQ03` | `A45.B56.C50.D35` | `temple` | `ACTIVE` | `floating-agent-03` | `board` |
| `TQ04` | `A56.B23.C55.D44` | `temple` | `PROMOTED` | `unclaimed` | `board` |
| `TQ05` | `A60.B24.C50.D36` | `temple` | `ACTIVE` | `floating-agent-04` | `board` |
| `TQ06` | `A24.B24.C51.D23` | `temple` | `ACTIVE` | `floating-agent-05` | `board` |
| `TQ01` | `A28.B22.C51.D40` | `temple` | `PROMOTED` | `unclaimed` | `board` |
| `TQ02` | `A29.B18.C50.D20` | `temple` | `PROMOTED` | `unclaimed` | `board` |
| `ADV64-S01` | `A20.B22.C55.D44` | `conductor` | `SEEDED` | `unclaimed` | `seeded` |
| `ADV64-S02` | `A22.B20.C51.D23` | `conductor` | `SEEDED` | `unclaimed` | `seeded` |

## Proof Anchors

- `Q42` routes through the atlas-backed `qshrink` and `athena_fleet` bundle pair before widening laterally.
- `Q45` remains the promoted proof anchor that hands the shared `A22.B27.C49.D43` coordinate forward to live `Q46` execution.
- `RoundTripCertificate_v0` governs the first conversion membrane across `Q42`, `Q46`, and `TQ04` without replacing the Hall four-witness completion law.

## Round-Trip Membrane

- governed fronts: `Q42, Q46, TQ04`
- registry: `self_actualize/adventurer_round_trip_certificates.json`
- receipt: `self_actualize/mycelium_brain/receipts/2026-03-13_round_trip_certificate_v0.md`

## Seeded Adjacent Slice

- `ADV64-S01` :: `A20.B22.C55.D44` :: parents=`Q42, TQ04` :: restart=`Q42 -> TQ04 -> next seeded conductor bridge`
- `ADV64-S02` :: `A22.B20.C51.D23` :: parents=`Q46, TQ06` :: restart=`Q46 -> TQ06 -> next seeded conductor bridge`

## Restart Seed

- current lawful frontier: `Q42`
- current wave: `ADV64-wave1`
- keep `Q02` suppressed while the Docs gate stays blocked and local lawful work remains
- if the Hall runs out of feasible open work, emit a new seeded bridge before idling instead of pretending the full 64^4 field has been traversed
