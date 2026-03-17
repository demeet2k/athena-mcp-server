# Council: Quest Atlas & Board Kernel

**Council ID**: `council_quest_atlas`
**Element**: Fire-Air-Water-Earth (Crown)
**Status**: ACTIVE

## Jurisdiction

Owns all artifacts in layer `28_SELF_PLAY_QUEST_ATLAS/`:
- Corpus capsules 198-226 (LP-57Omega Self Play specification)
- 16 Python code modules (board kernel, reward engine, pheromone engine, etc.)
- 12 policy JSON files
- 5 data JSON files
- Golden test vector suite (15 vectors, 6 categories)

## Responsibilities

1. **Board Kernel Integrity**: Ensure deterministic board output (same input = same output)
2. **Route Law Enforcement**: Sigma-lock (AppA, AppI, AppM), hub budget <= 6
3. **Reward Settlement**: Truth gate, quality law, per-capsule and per-epoch clamps
4. **Storm Management**: PhiStorm spawn/lifecycle from pheromone triggers
5. **Receipt Chain**: Sealed receipt bundle integrity, lint verification
6. **Policy Versioning**: Track policy migrations, freeze windows

## Cross-Council Links

- `council_transport_and_runtime` — Route compilation shares sigma path
- `council_higher_dimensional_geometry` — Phi constants, element ring geometry
- `council_manuscript_architecture` — Corpus capsule integration
- `council_live_orchestration` — Board emission feeds orchestration loop

## Manifests

- `06_RUNTIME/23_quest_atlas_manifest.json`
- `06_RUNTIME/24_self_play_board_manifest.json`

## Key Metrics

| Metric | Value |
|--------|-------|
| Stations | 19 |
| Loops/Orbit | 57 |
| Code Modules | 16 |
| Golden Vectors | 15/15 PASS |
| Policy Files | 12 |
| Capsule Range | 198-226 |
