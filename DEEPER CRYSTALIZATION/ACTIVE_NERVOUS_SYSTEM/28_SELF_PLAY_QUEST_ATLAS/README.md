# Layer 28 — Self Play Quest Atlas

LP-57Omega deterministic board engine for the 19-station x 3-pass quest atlas.

## Structure

```
28_SELF_PLAY_QUEST_ATLAS/
├── README.md                        (this file)
├── 00_QUEST_ATLAS_INDEX.md          (index of all artifacts)
├── 01_STATION_DEFINITIONS.json      (v1.0 - 19 stations)
├── 02_PAYOUT_MATRICES.json          (v1.1)
├── 03_UNLOCK_TREE.json              (v1.2)
├── 05_GOLDEN_TEST_VECTORS.json      (v1.6)
├── 07_RECEIPT_BUNDLE_SCHEMA.json    (v1.8)
├── code/                            (16 Python modules)
│   ├── __init__.py
│   ├── constants.py                 KernelConst.v1
│   ├── types.py                     Economic ABI
│   ├── station_atlas.py             19 stations + payouts
│   ├── route_compiler.py            Sigma-lock route compilation
│   ├── board_kernel.py              Deterministic board engine
│   ├── pheromone_engine.py          4+4 pheromone channels
│   ├── storm_engine.py              PhiStorm lifecycle
│   ├── seat_election.py             Host/steward election
│   ├── party_matcher.py             Community quest parties
│   ├── leveling_engine.py           Infinite-cap levels
│   ├── reward_engine.py             Full settlement engine
│   ├── receipt_engine.py            Receipt bundle builders
│   ├── pack_linter.py               Receipt verifier/linter
│   ├── verifier.py                  Golden test vectors
│   └── test_golden_vectors.py       pytest suite
└── policies/                        (12 JSON policy files)
    ├── BundleManifest.json
    ├── BoardKernelPolicy.json
    ├── RouteCompilerPolicy.json
    ├── StormPolicy.json
    ├── RewardPolicy_v1.json
    ├── KernelConst_v1.json
    ├── QuestPolicy_v1.json
    ├── TemplePolicy_v1.json
    ├── MigrationPolicy_v1.json
    ├── UnlockPolicy_v1.json
    ├── SeatElectionPolicy.json
    └── PromotionBoundaryPolicy.json
```

## Running Tests

```bash
cd ACTIVE_NERVOUS_SYSTEM
python -m 28_SELF_PLAY_QUEST_ATLAS.code.verifier
```

Expected output: 15/15 golden vectors PASS.

## Manifests

- `06_RUNTIME/23_quest_atlas_manifest.json`
- `06_RUNTIME/24_self_play_board_manifest.json`

## Corpus Capsules

Capsules 198-226 in `02_CORPUS_CAPSULES/` document the full specification.
See `05_APPENDICES/AppQ_quest_atlas_and_board_kernel.md` for cross-references.
