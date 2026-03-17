# Ganglion: Quest Atlas Integration

**Ganglion ID**: `quest_atlas`
**Council**: `council_quest_atlas`
**Element**: Crown (all four)
**Status**: ACTIVE

## Thread Binding

Primary thread: `quest_atlas_integration`

## Capsule Ownership

Capsules 198-226: LP-57Omega Self Play Quest Atlas specification

## Code Ownership

All modules under `28_SELF_PLAY_QUEST_ATLAS/code/`:
- `constants.py` — KernelConst.v1
- `types.py` — Economic ABI
- `station_atlas.py` — 19 station definitions
- `route_compiler.py` — Deterministic route compilation
- `board_kernel.py` — Board engine
- `pheromone_engine.py` — 4+4 pheromone channels
- `storm_engine.py` — PhiStorm lifecycle
- `seat_election.py` — Host/steward election
- `party_matcher.py` — Community quest party assembly
- `leveling_engine.py` — Infinite-cap levels
- `reward_engine.py` — Full settlement
- `receipt_engine.py` — Receipt bundle builders
- `pack_linter.py` — Receipt verifier/linter
- `verifier.py` — Golden test vector runner

## Verification State

15/15 golden vectors PASS. Determinism verified.

## Frontier

- Board kernel ready for integration with live orchestration loop
- Pheromone engine ready for real corpus field data
- Receipt chain verified with synthetic 3-quest bundle
