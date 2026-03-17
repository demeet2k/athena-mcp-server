# Earth Replay And Reentry Guards

## Recovery law

Earth is only legal if it can return to the current 4D witnesses without losing
appendix legality, replay closure, contradiction containment, or the exact gate history
required for `7D_SEED`.

The local Earth replay zero point is `Z_earth.replay`.

## Anchor spine

- Closure return: `Ch12<0023>`
- Memory return: `Ch13<0030>`
- Replay return: `Ch16<0033>`
- Existing appendix anchors: `AppH`, `AppI`, `AppM`

## Recovery routes

| route_id | basis_refs | metro_refs | appendix_refs | local_zero_point | collapse_via | return_checkpoint | truth_state | replay_source | gate_verdict | boundary_class | conflict_envelope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `reentry_closure_return` | `09,15` | `03_level_4_transcendence_metro_map.md` | `AppA,AppI,AppM` | `Z_earth.replay.closure` | `Z*` | `Ch12<0023>` | `NEAR` | `08_APPENDIX_CRYSTAL/AppM_replay_kernel.md` | `HOLD_NEAR` | `SEALED` | `NONE` |
| `reentry_memory_return` | `02,09,15` | `03_level_4_transcendence_metro_map.md` | `AppH,AppI,AppM,AppN` | `Z_earth.replay.memory` | `Z*` | `Ch13<0030>` | `NEAR` | `11_6D_WATER_CONTROL/04_replay_and_recovery.md` | `HOLD_NEAR` | `FILTERED` | `NONE` |
| `reentry_replay_return` | `09,15,16` | `06_level_6_hologram_weave_map.md` | `AppI,AppK,AppM` | `Z_earth.replay.repair` | `Z*` | `Ch16<0033>` | `NEAR` | `07_METRO_STACK/06_level_6_hologram_weave_map.md` | `HOLD_NEAR` | `SEALED` | `QO_LOOP` |
| `reentry_seed7_return` | `02,09,13,15` | `07_level_7_next_synthesis_seed_map.md` | `AppA,AppI,AppK,AppM,AppN` | `Z_earth.replay.seed7` | `Z*` | `00_CONTROL/07_7D_CROSS_AGENT_SEED.md` | `NEAR` | `10_LEDGERS/12_7d_seed_routes.json` | `HOLD_NEAR` | `SEALED` | `NONE` |
| `blocked_docs_reconciliation` | `02,09,15,16` | `03_level_4_transcendence_metro_map.md` | `AppA,AppI,AppK,AppM` | `Z_earth.replay.docs_gate` | `Z*` | `self_actualize/live_docs_gate_status.md` | `NEAR` | `self_actualize/live_docs_gate_status.md` | `REQUIRE_EVIDENCE` | `FILTERED` | `NONE` |

## Recovery constraint

If the live Google Docs gate remains blocked, Earth recovery stays in local-authority
mode. No route in this package may upgrade its truth state or request cortex promotion
by guessing at unseen live-docs content.
