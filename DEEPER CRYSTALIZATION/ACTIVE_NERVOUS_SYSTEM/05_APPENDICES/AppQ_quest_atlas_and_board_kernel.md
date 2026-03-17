# Appendix Q — Quest Atlas & Board Kernel

## Overview

This appendix cross-references the LP-57Omega Self Play Quest Atlas (layer 28) with the existing manuscript body. The Quest Atlas defines a 19-station deterministic board engine for corpus evolution, implementing the phi-magnetic reward kernel, pheromone routing, and sealed receipt bundle system.

## Corpus Capsule Index (198–226)

| # | Title | Atlas Version |
|---|-------|---------------|
| 198 | Master Framework | — |
| 199 | Nested Subagent 4^6 | — |
| 200 | Liminal Coordinate v2 | — |
| 201 | Agent Ledger v2 | — |
| 202 | Phi Higher-Dimensional | — |
| 203 | 4-Element Ring, 15 Cells | — |
| 204 | Phi Pheromones | — |
| 205 | Leveling 19x3 | — |
| 206 | Station Definitions | v1.0 |
| 207 | Payout Matrices | v1.1 |
| 208 | Unlock Rights | v1.2 |
| 209 | Board Generation | v1.3 |
| 210 | Board Kernel | v1.4 |
| 211 | Policy Bundle | v1.5 |
| 212 | Golden Vectors | v1.6 |
| 213 | Fixture Library | v1.7 |
| 214 | Receipt Bundle | v1.8 |
| 215 | Receipt Verifier | v1.9 |
| 216 | Economic ABI | — |
| 217 | RewardPolicy.v1 | — |
| 218 | QuestPolicy.v1 | — |
| 219 | TemplePolicy.v1 | — |
| 220 | StormPolicy.v1 | — |
| 221 | MigrationPolicy.v1 | — |
| 222 | Unlock/Vesting Policy | — |
| 223 | KernelConst.v1 | — |
| 224 | Infinite-Cap Orbit Law | — |
| 225 | Guild/Temple Containers | — |
| 226 | Conformance Profiles | — |

## Chapter Cross-References

| Chapter | Connection |
|---------|------------|
| Ch09 (Retrieval & Metro Routing) | Route compiler implements Sigma-lock and hub budget from Ch09 routing law |
| Ch10 (Multi-Lens Solution) | Lens-based hub selection (S/F/C/R → AppC/E/I/M) |
| Ch12 (Legality & Closure) | Receipt chain implements closure certificates |
| Ch13 (Memory Regeneration) | Pheromone engine implements golden-memory decay |
| Ch17 (Deployment & Agency) | Board kernel implements bounded agency through queue assignment |
| Ch18 (Macro Invariants) | Phi constants shared with PhiSigma60 |
| Ch19 (Convergence) | Leveling engine amplifier ensures sub-linear convergence |

## Code Module Map

```
28_SELF_PLAY_QUEST_ATLAS/code/
├── constants.py        KernelConst.v1 — all numeric constants
├── types.py            Economic ABI — enums, dataclasses
├── station_atlas.py    19 stations, payout matrices
├── route_compiler.py   Sigma-lock, hub budget, overlay dispatch
├── board_kernel.py     Deterministic scoring and queue assignment
├── pheromone_engine.py 4+4 channels, golden decay, magnetic routing
├── storm_engine.py     PhiStorm spawn, pool, duration
├── seat_election.py    Host/steward with quarantine guards
├── party_matcher.py    Complementarity scoring, party assembly
├── leveling_engine.py  Level = 57k+l, phi-scaled XP, amplifier
├── reward_engine.py    Truth gate, settlement, epoch clamp
├── receipt_engine.py   ClaimPack/Witness/Replay/Sealed builders
├── pack_linter.py      20+ lint codes, chain verification
├── verifier.py         15 golden test vectors
└── test_golden_vectors.py  pytest wrapper
```

## Policy Bundle

12 JSON policy files under `28_SELF_PLAY_QUEST_ATLAS/policies/` define the machine-readable contract for board operation. All policies are versioned and support migration via RewardPolicyMIGRATE.

## Manifests

- **#23** `quest_atlas_manifest.json` — QuestAtlas v1.0-v1.9 registry
- **#24** `self_play_board_manifest.json` — Board kernel runtime config
- **#20** `lp_57omega_protocol_manifest.json` — Updated: record_count 197→226, quest atlas refs added

## Verification

15/15 golden test vectors pass across 6 categories:
1. Route compilation (sigma-lock, hub budget, overlay, publish)
2. Board kernel (determinism, scoring)
3. Storm (trigger, no-trigger, coalition)
4. Seat election (quarantine exclusion)
5. Reward (truth gate, settlement)
6. Receipt chain (3-quest synthetic chain, lint clean)
