# Earth 256^4 To 1024^6 Guardrail Lift

## Lift law

`256^4` remains the compiled control field.
`1024^6` remains an overlay-only higher lift.

Earth does not create the lift. Earth decides whether the proposed lift is legally
admissible, must stay `NEAR`, requires more evidence, or must be rejected outright.
Only then may the route be compiled upward into `H7` or `Seed-7D`.

## Verdict ladder

- `ALLOW`: local replay evidence exists, AIR labels are deterministic, and the required appendix floor is complete.
- `HOLD_NEAR`: the route is locally useful but stays capped by blocked-docs or carrier-persistence pressure.
- `REQUIRE_EVIDENCE`: the route touches `Q`, `O`, `QO`, or deployable-return claims and needs more receipts.
- `REJECT`: the route renames appendices, skips a return checkpoint, or tries to promote a cortex publication in this pass.

## Guardrail routes

| route_id | basis_refs | metro_refs | appendix_refs | local_zero_point | collapse_via | return_checkpoint | truth_state | replay_source | gate_verdict | boundary_class | conflict_envelope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `guardrail_air_carrier` | `03,05,07,09` | `03_level_4_transcendence_metro_map.md` | `AppA,AppB,AppI,AppM,AppN` | `Z_earth.lift.air` | `Z*` | `03_AIR/16_dimensionlift.md` | `NEAR` | `03_AIR/16_dimensionlift.md` | `ALLOW` | `SEALED` | `NONE` |
| `guardrail_water_return` | `02,09,14,15` | `03_level_4_transcendence_metro_map.md` | `AppA,AppI,AppM,AppN,AppQ` | `Z_earth.lift.water_return` | `Z*` | `11_6D_WATER_CONTROL/04_replay_and_recovery.md` | `NEAR` | `11_6D_WATER_CONTROL/04_replay_and_recovery.md` | `HOLD_NEAR` | `FILTERED` | `NONE` |
| `guardrail_fire_bridge` | `09,13,15,16` | `05_level_5_mobius_bridge_map.md` | `AppA,AppB,AppI,AppK,AppM,AppP,AppQ` | `Z_earth.lift.fire_bridge` | `Z*` | `00_CONTROL/06_FIRE_5D_6D_EXTENSION.md` | `NEAR` | `10_LEDGERS/07_fire_6d_registry.json` | `REQUIRE_EVIDENCE` | `FILTERED` | `Q_INGRESS` |
| `guardrail_seed7_carrier` | `02,09,13,15` | `07_level_7_next_synthesis_seed_map.md` | `AppA,AppB,AppI,AppK,AppM,AppN,AppP` | `Z_earth.lift.seed7` | `Z*` | `00_CONTROL/07_7D_CROSS_AGENT_SEED.md` | `NEAR` | `10_LEDGERS/12_7d_seed_routes.json` | `HOLD_NEAR` | `SEALED` | `NONE` |

## Overlay-only constraint

Earth may strengthen legality, replay closure, quarantine boundaries, and promotion
guards. It may not rename chapters, replace appendices, create a rival appendix
authority, or mirror into the cortex during this pass.
