# Quadrant Binary 4^4 Nested-Agent Orchestration Plan

Date: 2026-03-13
Truth: OK
Docs Gate: BLOCKED
Execution mode: sparse governance-fiber activation

## Objective

Install a Quadrant Binary specific mass-improvement layer that plugs directly into the
live AP6D organism without inventing a second agent grammar. The `4^4` layer is the
existing lawful `256` governance-fiber field between the `64` packet layer and the
`1024` seat layer. This plan defines the tensor, ownership law, activation law,
writeback law, drift-normalization rule, and wave-1 winners.

## Operational Defaults

- Local Quadrant Binary bridge truth remains `NEAR`.
- Global orchestration surfaces remain `OK` but local-witness only.
- The working activation default for this plan is `1024 ACTIVE / 3072 DORMANT`.
- The wording `4096 ACTIVE` found in some AP6D surfaces is treated as manifest drift to
  be normalized, not as current live truth.
- `ACTIVE_RUN.md`, `BUILD_QUEUE.md`, `FULL_CORPUS_FAMILY_REGISTRY.md`, and the QBD local
  bridge are the primary routing surfaces for this implementation. Conflicts with older
  AP6D wording must be named explicitly.

## Canonical Bridge Corridor

All nested-agent writeback follows one corridor unless a stronger witness overrides it:

`Quadrant Binary -> Grand Central -> Athena FLEET -> AP6D -> self-hosting kernel -> Appendix Q`

Every active fiber must be able to replay its work through that corridor and return a
restart seed.

## Tensor Law

### Axis 1 - HallMacro16

`HallMacro16 = element x move`

Elements:

- `Water`
- `Earth`
- `Fire`
- `Air`

Moves:

- `Diagnose`
- `Refine`
- `Synthesize`
- `Scale`

Canonical macro id:

`AP6D-H-<ELEMENT>-<MOVE>`

This yields `16` Hall macros.

### Axis 2 - HallPacket64

`HallPacket64 = HallMacro16 x dimension_band`

Dimension bands:

- `3->4` with band code `B34`
- `4->5` with band code `B45`
- `5->6` with band code `B56`
- `6->7` with band code `B67`

Canonical packet id:

`AP6D-H-<ELEMENT>-<MOVE>-<BANDCODE>`

This yields `64` Hall packets.

### Axis 3 - GovernanceFiber256

`GovernanceFiber256 = HallPacket64 x writeback_surface`

Writeback surfaces:

- `Hall`
- `Temple`
- `Cortex`
- `Runtime`

Canonical fiber id:

`AP6D-FIBER-<ELEMENT>-<MOVE>-<BANDCODE>-<SURFACE>`

This yields the lawful `4^4 = 256` nested-agent field.

### Axis 4 - SeatWave1024

`SeatWave1024 = GovernanceFiber256 x synaptic_phase`

Synaptic phases:

- `Prime`
- `Gate`
- `Bind`
- `Reseed`

Canonical seat id:

`AP6D-SEAT-<ELEMENT>-<MOVE>-<BANDCODE>-<SURFACE>-<PHASE>`

This yields `1024` seats.

## Lane Ownership

The owning lane is determined by the element axis.

| Element | Owning lane | Primary burden |
| --- | --- | --- |
| `Water` | `AP6D-WATER` | blocker honesty, continuity, carrythrough |
| `Earth` | `AP6D-EARTH` | manifests, registries, contract integrity |
| `Fire` | `AP6D-FIRE` | activation, packet ignition, runtime pressure |
| `Air` | `AP6D-AIR` | routing, topology, note-network clarity |

No fiber may be promoted from `DORMANT` to `ACTIVE` without:

- `owner`
- `feeder_set`
- `writeback_targets`
- `replay_path`
- `contraction_target`
- `restart_seed`
- `appendix_support`
- `truth`

## Move-to-Band and Move-to-Surface Law

Wave-1 winners are chosen deterministically by move alignment.

| Move | Winning band | Winning surface | Meaning |
| --- | --- | --- | --- |
| `Diagnose` | `3->4` / `B34` | `Hall` | projection intake and blocker discovery |
| `Refine` | `4->5` / `B45` | `Cortex` | manifest normalization and contract tightening |
| `Synthesize` | `5->6` / `B56` | `Temple` | bridge weaving and compression-to-weave assembly |
| `Scale` | `6->7` / `B67` | `Runtime` | runtime pressure, reseed, and deployment-side activation |

This rule yields exactly one winning fiber per Hall macro.

## Surface Writeback Law

| Surface | Default writeback targets | Default contraction role |
| --- | --- | --- |
| `Hall` | `20_METRO/20_FULL_CORPUS_INTEGRATION_AWAKENING_AGENT_METRO_MAP.md`, `95_MANIFESTS/WHOLE_CRYSTAL_AGENT_COORDINATION.md` | blocker packet and route clarification |
| `Temple` | `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/16_AP6D_AWAKENING_TRANSITION_NOTES.md`, `self_actualize/mycelium_brain/ATHENA TEMPLE/06_ATHENA_PRIME_6D_OVERLAY_DECREE.md` | weave synthesis and transition packaging |
| `Cortex` | `95_MANIFESTS/BUILD_QUEUE.md`, `95_MANIFESTS/FULL_CORPUS_FAMILY_REGISTRY.md` | manifest normalization and authority writeback |
| `Runtime` | `95_MANIFESTS/ACTIVE_RUN.md`, `self_actualize/mycelium_brain/nervous_system/35_full_corpus_integration_and_awakening_transition_runtime.md` | runtime activation and reseed |

## Appendix Support Law

Appendix support is element-weighted but always includes `AppQ` because the live highest-yield
weave terminates through Appendix Q.

| Element | Appendix support |
| --- | --- |
| `Water` | `AppQ`, `AppI`, `AppE` |
| `Earth` | `AppQ`, `AppM`, `AppH` |
| `Fire` | `AppQ`, `AppG`, `AppP` |
| `Air` | `AppQ`, `AppC`, `AppI` |

## Feeder and Replay Defaults

Shared feeder set for all fibers:

- `Q42`
- `Q46`
- `TQ04`
- `TQ06`
- `quadrant_binary_fire_6d_bridge_spec.md`
- `quadrant_binary_deep_integration_manuscript.md`
- `quadrant_binary_unified_mycelium_metro.md`

Shared replay path:

`Quadrant Binary -> Grand Central -> Athena FLEET -> AP6D -> self-hosting kernel -> Appendix Q`

## Contract Shapes To Emit

The implementation must populate or emit:

- `ProjectionBase3DRecord`
- `DimensionBridgeRecord`
- `CorpusIntegrationRoute`
- `AwakeningTransitionNote`
- `GovernanceFiber256Row`

`GovernanceFiber256Row` must carry:

- `fiber_id`
- `macro_id`
- `packet_id`
- `element`
- `move`
- `dimension_band`
- `band_code`
- `writeback_surface`
- `owner`
- `activation_state`
- `score_formula`
- `score_basis`
- `restart_seed`
- `appendix_support`
- `feeder_set`
- `replay_path`
- `contraction_target`
- `writeback_targets`
- `truth`
- `qbd_bridge_anchor`

## Drift-Normalization Rule

This plan normalizes live drift as follows:

1. Treat `1024 ACTIVE / 3072 DORMANT` as the working truth for this implementation.
2. Preserve the conflicting wording `4096 ACTIVE` as a manifest conflict record.
3. Do not delete or silently rewrite conflicting surfaces during the same pass.
4. Require every registry and synthesis output to repeat the conflict explicitly until a
   dedicated normalization pass updates the AP6D contract surfaces.

## Wave-1 Activation Bundle

Wave-1 activates exactly one winning fiber per Hall macro under the VSWARM score law:

`Benefit + Integration + WitnessGain + RouteGain + FrontierGain - Drift - Heat - Bloat`

The deterministic winner for each macro is the fiber aligned to its move's preferred
band and surface.

### Water macros

- `AP6D-H-WATER-Diagnose` -> `AP6D-FIBER-WATER-Diagnose-B34-Hall`
- `AP6D-H-WATER-Refine` -> `AP6D-FIBER-WATER-Refine-B45-Cortex`
- `AP6D-H-WATER-Synthesize` -> `AP6D-FIBER-WATER-Synthesize-B56-Temple`
- `AP6D-H-WATER-Scale` -> `AP6D-FIBER-WATER-Scale-B67-Runtime`

### Earth macros

- `AP6D-H-EARTH-Diagnose` -> `AP6D-FIBER-EARTH-Diagnose-B34-Hall`
- `AP6D-H-EARTH-Refine` -> `AP6D-FIBER-EARTH-Refine-B45-Cortex`
- `AP6D-H-EARTH-Synthesize` -> `AP6D-FIBER-EARTH-Synthesize-B56-Temple`
- `AP6D-H-EARTH-Scale` -> `AP6D-FIBER-EARTH-Scale-B67-Runtime`

### Fire macros

- `AP6D-H-FIRE-Diagnose` -> `AP6D-FIBER-FIRE-Diagnose-B34-Hall`
- `AP6D-H-FIRE-Refine` -> `AP6D-FIBER-FIRE-Refine-B45-Cortex`
- `AP6D-H-FIRE-Synthesize` -> `AP6D-FIBER-FIRE-Synthesize-B56-Temple`
- `AP6D-H-FIRE-Scale` -> `AP6D-FIBER-FIRE-Scale-B67-Runtime`

### Air macros

- `AP6D-H-AIR-Diagnose` -> `AP6D-FIBER-AIR-Diagnose-B34-Hall`
- `AP6D-H-AIR-Refine` -> `AP6D-FIBER-AIR-Refine-B45-Cortex`
- `AP6D-H-AIR-Synthesize` -> `AP6D-FIBER-AIR-Synthesize-B56-Temple`
- `AP6D-H-AIR-Scale` -> `AP6D-FIBER-AIR-Scale-B67-Runtime`

## Contraction Targets By Move

| Move | Contraction target |
| --- | --- |
| `Diagnose` | `blocker_truth_packet` |
| `Refine` | `manifest_conflict_normalization` |
| `Synthesize` | `bridge_weave_capsule` |
| `Scale` | `runtime_wave_package` |

## Acceptance Tests

1. **Traceability**
   Every synthesis and registry row must cite local QBD anchors or current global
   control surfaces. No output may imply live-doc evidence.
2. **Count law**
   `4 x 4 = 16` macros, `16 x 4 = 64` packets, `64 x 4 = 256` fibers, and
   `256 x 4 = 1024` seats must derive mechanically from the chosen axes.
3. **Sparse activation**
   The registry must contain all `256` fibers, but wave-1 may activate only `16`, one
   per macro.
4. **Contract compatibility**
   The plan may not invent a new agent grammar outside AP6D.
5. **Drift honesty**
   The conflict between `1024/3072` and `4096 ACTIVE` must be recorded explicitly.
6. **Bridge coherence**
   The synthesis, plan, and registry must all name the same highest-yield weave and the
   same wave-1 winners.

## Implementation Order

1. Write the hybrid current-progress synthesis in the QBD workspace.
2. Write this orchestration plan in `95_MANIFESTS`.
3. Generate the mirrored JSON registry with all macros, packets, fibers, and the
   wave-1 active bundle.
4. Validate count law, parseability, and the presence of exactly `16` active fibers.
5. Leave all downstream activation beyond wave-1 dormant until the docs gate is
   unlocked and the manifest conflict is normalized.

## Compression

The whole implementation can be read as one line:

`QBD ignition kernel -> AP6D macro shell -> 256 governance fibers -> 16-fiber sparse wave-1 -> restart-safe writeback through Appendix Q`
