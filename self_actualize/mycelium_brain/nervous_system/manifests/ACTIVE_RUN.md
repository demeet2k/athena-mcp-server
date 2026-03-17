# Active Run

run_id: NS-2026-03-10-02
mode: source-pinning-then-leaf-cashout
scale: mixed-S8-B12-G4
restart_law: active
active_gate: Gate37->Gate01

## FrontID

`FRONT-Q36-BRUNO-LEAF-PROMOTION`

## Quest

`Q36: Convert One AMBIG Leaf Using New Family Witness`

## State

`PROMOTED`

## Truth

`OK`

## Objective

Use the new Bruno family witness to convert one downstream replay-side leaf from `AMBIG`
to `OK`.

## Why Now

`Q08` turned Bruno into a lawful source-pinned bronze wheel, so the next honest gain was
to cash that truth into a named node instead of stopping at family rhetoric.

## Route

`docs blocker preserved -> bruno source pinning -> bronze wheel -> address-c leaf evidence ladder -> hall -> queue -> manifest -> receipt -> restart seed`

## Inputs

- `self_actualize/bruno_b12_operator_table.json`
- `nervous_system/families/BRUNO_B12_OPERATOR_TABLE.md`
- `nervous_system/families/FAMILY_bruno_route_map.md`
- `nervous_system/families/FAMILY_bruno_primary_sources.md`
- `nervous_system/manifests/BRUNO_ACTIVE_FRONT.md`

## Targets

- `self_actualize/runtime/derive_bruno_address_c_leaf_promotion.py`
- `self_actualize/tools/derive_bruno_address_c_leaf_promotion.py`
- `self_actualize/bruno_address_c_leaf_promotion.json`
- `nervous_system/families/BRUNO_ADDRESS_C_LEAF_PROMOTION.md`
- `manifests/NEXT_SELF_PROMPT.md`

## Witness

- one machine-derived leaf-promotion witness
- one explicit `AMBIG -> OK` leaf conversion
- one Hall and queue writeback
- one restart-safe manifest refresh

## Writeback

- `GLOBAL_EMERGENT_GUILD_HALL/BOARDS/01_ACTIVE_FRONTS_BOARD.md`
- `GLOBAL_EMERGENT_GUILD_HALL/BOARDS/04_CHANGE_FEED_BOARD.md`
- `GLOBAL_EMERGENT_GUILD_HALL/BOARDS/05_REQUESTS_AND_OFFERS_BOARD.md`
- `GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md`
- `nervous_system/06_active_queue.md`
- `manifests/ACTIVE_RUN.md`
- `manifests/DEEPER_ENHANCEMENT_ACTIVE_FRONT.md`
- `manifests/NEXT_SELF_PROMPT.md`

## Blockers

- live Docs gate remains blocked because `Trading Bot/credentials.json` and `Trading Bot/token.json` are still missing

## Active Tensor Anchor

`NSCoord = (Q36_BrunoLeafPromotion, S8+B12+G4, Fire+Air+Earth, O36, Arc4, Me, AppB+AppM+AppI, Source+Family+Hall+Manifest, promote, leaf, OK)`

## Secondary Tensor Anchor

`NSCoord2 = (Q08_BrunoB12, Bronze, Air, OT08, Arc4, Me, AppB+AppF+AppM, Source+Family+Hall, pin, wheel, OK)`

## Next Seed

`FRONT-Q35-ORGIN-MIRROR`
