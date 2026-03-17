# Earth Boundary Quarantine And Mobius Legality

## Boundary classes

- `SEALED`: route is locally admissible and has a deterministic return checkpoint.
- `FILTERED`: route is useful but must stay bounded by local evidence and explicit guards.
- `QUARANTINED`: route carries unresolved contradiction, alias drift, or illegal appendix pressure and may not propagate.

## Q/O legality

- `Q` is legal only through canonical `AppQ`.
- Reverse-field `O` remains an overlay alias and may not be treated as a new appendix file.
- Canonical `AppO` stays the export-bundle appendix and is only referenced as the return-side authority already on disk.
- `QO` loop traffic may never mint a reverse appendix family or bypass the existing appendix crystal.

## Conflict routes

| route_id | basis_refs | metro_refs | appendix_refs | local_zero_point | collapse_via | return_checkpoint | truth_state | replay_source | gate_verdict | boundary_class | conflict_envelope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `boundary_q_ingress` | `02,15,03` | `05_level_5_mobius_bridge_map.md` | `AppA,AppB,AppI,AppK,AppM,AppQ` | `Z_earth.boundary.q` | `Z*` | `08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md` | `NEAR` | `08_APPENDIX_CRYSTAL/01_reverse_appendix_overlay_ledger.md` | `REQUIRE_EVIDENCE` | `FILTERED` | `Q_INGRESS` |
| `boundary_o_return` | `09,13,15` | `05_level_5_mobius_bridge_map.md` | `AppA,AppB,AppI,AppK,AppM,AppO` | `Z_earth.boundary.o` | `Z*` | `08_APPENDIX_CRYSTAL/AppO_export_bundles.md` | `NEAR` | `00_CONTROL/06_FIRE_5D_6D_EXTENSION.md` | `REQUIRE_EVIDENCE` | `FILTERED` | `O_RETURN` |
| `boundary_qo_loop` | `09,15,16` | `06_level_6_hologram_weave_map.md` | `AppA,AppB,AppI,AppK,AppM,AppN` | `Z_earth.boundary.qo` | `Z*` | `12_6D_EARTH_CONTROL/04_replay_and_reentry_guards.md` | `NEAR` | `07_METRO_STACK/06_level_6_hologram_weave_map.md` | `HOLD_NEAR` | `SEALED` | `QO_LOOP` |
| `boundary_reverse_overlay_reject` | `13,15` | `05_level_5_mobius_bridge_map.md` | `AppA,AppB,AppK` | `Z_earth.boundary.reverse_overlay` | `Z*` | `08_APPENDIX_CRYSTAL/01_reverse_appendix_overlay_ledger.md` | `FAIL` | `08_APPENDIX_CRYSTAL/01_reverse_appendix_overlay_ledger.md` | `REJECT` | `QUARANTINED` | `REVERSE_OVERLAY` |

## Promotion constraint

- `AppL` enters only when a route remains `AMBIG` after filtering and needs an evidence plan.
- `AppP` enters only when a route claims stable or deployable return beyond the live deep root.
