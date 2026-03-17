# Earth 6D Admissibility And Zero Point

## Gate zero point

The local Earth zero point is `Z_earth.gate`.

It is the smallest immune and legal bundle that can decide whether a higher-dimensional
route may persist without contradiction leakage, appendix drift, or replay loss.

## Earth gate registry

`EarthGate6D = (NSCoord, AIRRef, BoundaryClass, AdmissibilityMode, ConflictEnvelope, RequiredAppendices, ReturnCheckpoint, TruthCap, DocsGate)`

- `AIRRef` points to the AIR overlay labels already on disk.
- `BoundaryClass` is `SEALED`, `FILTERED`, or `QUARANTINED`.
- `AdmissibilityMode` is `ALLOW`, `HOLD_NEAR`, `REQUIRE_EVIDENCE`, or `REJECT`.
- `ConflictEnvelope` is `NONE`, `Q_INGRESS`, `O_RETURN`, `QO_LOOP`, or `REVERSE_OVERLAY`.
- `RequiredAppendices` is the exact gate stack for the route.
- `ReturnCheckpoint` is the lawful re-entry surface or anchor.
- `TruthCap` reuses `{OK, NEAR, AMBIG, FAIL}`.
- `DocsGate` remains `BLOCKED` until OAuth material exists.

## Gate laws

- No Earth 6D route may rename `ChXX<dddd>...`, `AppA-AppP`, or `AppQ`.
- Earth reuses AIR topology, Water continuity, and FIRE bridge state instead of re-defining them.
- Any route touching `Q`, `O`, or `QO` remains overlay-only and must publish its exact guard set.
- While Docs are `BLOCKED`, no route may self-promote above local witnessed truth already present on disk.
- Any `H6 -> Seed-6D` return must explicitly reference `Ch12<0023>`, `Ch13<0030>`, `Ch16<0033>`, plus `AppI` and `AppM`. Add `AppK` when conflict survives. Add `AppN` when the carrier persists.

## Admissibility routes

| route_id | basis_refs | metro_refs | appendix_refs | local_zero_point | collapse_via | return_checkpoint | truth_state | replay_source | gate_verdict | boundary_class | conflict_envelope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gate_level4_carrier` | `02,09,15` | `03_level_4_transcendence_metro_map.md` | `AppA,AppB,AppI,AppM,AppN` | `Z_earth.gate.level4` | `Z*` | `12_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md` | `NEAR` | `03_AIR/07_registryschemas.md` | `HOLD_NEAR` | `FILTERED` | `NONE` |
| `gate_q_ingress_overlay` | `02,13,15` | `05_level_5_mobius_bridge_map.md` | `AppA,AppB,AppI,AppK,AppM,AppQ` | `Z_earth.gate.q_ingress` | `Z*` | `08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md` | `NEAR` | `08_APPENDIX_CRYSTAL/01_reverse_appendix_overlay_ledger.md` | `REQUIRE_EVIDENCE` | `FILTERED` | `Q_INGRESS` |
| `gate_h6_seed_return` | `09,15,16` | `06_level_6_hologram_weave_map.md` | `AppH,AppI,AppK,AppM,AppN` | `Z_earth.gate.seed_return` | `Z*` | `Ch12<0023>/Ch13<0030>/Ch16<0033>` | `NEAR` | `08_APPENDIX_CRYSTAL/AppM_replay_kernel.md` | `HOLD_NEAR` | `SEALED` | `QO_LOOP` |
