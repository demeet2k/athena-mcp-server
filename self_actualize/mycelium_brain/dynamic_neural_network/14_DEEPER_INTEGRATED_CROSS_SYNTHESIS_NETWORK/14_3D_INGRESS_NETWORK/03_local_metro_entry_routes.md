# Local Metro Entry Routes

## Ingress3DNode

`Ingress3DNode = (body_id, folder_scope, station_role, transfer_hubs, feeds_basis, nearest_metro_level, replay_ref)`

## CorpusMetroEdge

`CorpusMetroEdge = (src_record_id, dst_record_id, dimension, line_id, line_role, appendix_support, truth_state, replay_ref)`

## Seed routes

| route_id | line_id | source bodies | feeds_basis | active_metro_levels | appendix_support | replay_ref |
| --- | --- | --- | --- | --- | --- | --- |
| `ingress_runtime_control` | `Atlas-to-Replay Line` | `self_actualize, ORGIN` | `02,14,15,16` | `1,2,3,4,5,6,7` | `AppA,AppH,AppI,AppM` | `14_3D_INGRESS_NETWORK/04_reentry_into_4d_native.md` |
| `ingress_kernel_reservoir` | `Kernel Line` | `MATH, ECOSYSTEM, Quadrant Binary` | `03,04,05,06,07,08,09,11,12,13` | `1,2,3,4,5,6,7` | `AppA,AppB,AppC,AppM` | `07_METRO_STACK/00_level_1_core_metro_map.md` |
| `ingress_manuscript_compute` | `Manuscript Line` | `DEEPER CRYSTALIZATION, Voynich` | `01,02,11,12,14` | `1,2,3,4,5,6` | `AppE,AppI,AppL,AppM` | `07_METRO_STACK/01_level_2_deep_emergence_metro_map.md` |
| `ingress_runtime_emergence` | `Runtime Line` | `NERUAL NETWORK, Athena FLEET, GAMES` | `07,08,10,16` | `1,2,3,4,5,6,7` | `AppC,AppF,AppP` | `07_METRO_STACK/02_level_3_deeper_neural_map.md` |
| `ingress_external_memory_gate` | `External Memory Gate Line` | `Trading Bot` | `06,08,09` | `1,2,3` | `AppE,AppN,AppP` | `self_actualize/live_docs_gate_status.md` |

## Honesty law

Because the Docs gate is `BLOCKED`, the external-memory line remains local-only. It may
support routing diagnosis, but it may not promote unseen Google Docs content into the
backplane.
