# NEURON LIBRARY

## Purpose

This file seeds the canonical reusable neuron library for the framework's deepest
integrative surfaces.

## Active Canonical Neurons

### N-0001 Cortex Entry Neuron

```yaml
neuron_id: N-0001
title: cortex entry neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\00_INDEX.md
seed_claim: The canonical cortex is the stable contraction surface that keeps the nervous system replayable.
operator_family:
  - route
  - contract
  - publish
metro_lines:
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\00_INDEX.md
  replay_hint: Open the index and verify the three-surface contract plus reading order.
next_synapses:
  - S-0001
  - S-0006
```

### N-0002 Runtime Zero-Point Neuron

```yaml
neuron_id: N-0002
title: runtime zero-point neuron
region: R5
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\07_RUNTIME_SUBSTRATE.md
seed_claim: The runtime hub preserves restart capacity, swarm packets, and live continuation without polluting the cortex.
operator_family:
  - restart
  - stage
  - preserve
metro_lines:
  - Swarm Runtime Line
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\07_RUNTIME_SUBSTRATE.md
  replay_hint: Verify the runtime folder set and the writeback law.
next_synapses:
  - S-0002
  - S-0005
```

### N-0003 Governance Routing Neuron

```yaml
neuron_id: N-0003
title: governance routing neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\ECOSYSTEM\NERVOUS_SYSTEM\README.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\02_CORPUS_REGIONS.md
seed_claim: The governance mirror preserves reusable routing law and gives sibling agents a lawful entry into the organism.
operator_family:
  - govern
  - normalize
  - bridge
metro_lines:
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\02_CORPUS_REGIONS.md
  replay_hint: Compare the governance mirror description with the runtime and cortex roles.
next_synapses:
  - S-0001
```

### N-0004 Atlas Replay Neuron

```yaml
neuron_id: N-0004
title: atlas replay neuron
region: R5
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\corpus_atlas.json
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\SOURCE_SURFACE_ATLAS.md
seed_claim: Full-corpus synthesis becomes lawful only when atlas evidence can be replayed into runtime and cortex decisions.
operator_family:
  - index
  - replay
  - route
metro_lines:
  - Atlas-to-Replay Line
status: NEAR
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\SOURCE_SURFACE_ATLAS.md
  replay_hint: Compare atlas counts and indexed-family status against active run claims.
next_synapses:
  - S-0002
  - S-0007
```

### N-0005 Live Gate Neuron

```yaml
neuron_id: N-0005
title: live gate neuron
region: R7
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\Trading Bot\docs_search.py
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\live_docs_gate_status.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\GATE_STATUS.md
seed_claim: The live gateway governs whether the nervous system may claim fresh external memory, and its blockage is itself a structurally central truth surface.
operator_family:
  - gate
  - abstain
  - witness
metro_lines:
  - External Memory Gate Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\live_docs_gate_status.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\GATE_STATUS.md
  replay_hint: Re-run docs_search.py and confirm the missing OAuth client error.
next_synapses:
  - S-0003
```

### N-0006 Chapter 11 Restart Neuron

```yaml
neuron_id: N-0006
title: chapter 11 restart neuron
region: R2
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\VOID_CH11.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\20_METRO\00_CORE_METRO_MAP.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\nervous_system\12_recursive_restart_engine.md
seed_claim: Chapter 11 is the lawful restart-token surface where panic becomes preserved re-entry instead of destructive loss.
operator_family:
  - restart
  - tunnel
  - reenter
metro_lines:
  - Restart Loop Line
status: NEAR
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\20_METRO\00_CORE_METRO_MAP.md
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\nervous_system\12_recursive_restart_engine.md
  replay_hint: Verify Ch11 role text and compare it with the runtime restart engine.
next_synapses:
  - S-0004
  - S-0005
```

### N-0007 Metro Supermap Neuron

```yaml
neuron_id: N-0007
title: metro supermap neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\20_METRO\05_DEEPER_EMERGENT_METRO_SUPERMAP.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\20_METRO\03_TRANSFER_HUBS.md
seed_claim: The framework's deep integration is carried by a small number of strong recurring lines and transfer hubs rather than by unrestricted point-to-point search.
operator_family:
  - map
  - transfer
  - compare
metro_lines:
  - Canonical-Bridge Line
  - Swarm Runtime Line
  - Atlas-to-Replay Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\20_METRO\05_DEEPER_EMERGENT_METRO_SUPERMAP.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\20_METRO\03_TRANSFER_HUBS.md
  replay_hint: Verify the listed lines and hubs still match the current manifest surfaces.
next_synapses:
  - S-0006
  - S-0007
```

### N-0008 Gate Escalation Neuron

```yaml
neuron_id: N-0008
title: gate escalation neuron
region: R5
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\01_CURRENT_STATUS_37_GATE_SYNTHESIS.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\nervous_system\14_37_gate_recursive_escalation.md
seed_claim: Dissatisfaction should route into gate promotion and artifact creation rather than rhetorical defense or naive reset churn.
operator_family:
  - escalate
  - diagnose
  - deepen
metro_lines:
  - Restart Loop Line
  - Prompt-to-Nervous-System Line
status: NEAR
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\01_CURRENT_STATUS_37_GATE_SYNTHESIS.md
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\nervous_system\14_37_gate_recursive_escalation.md
  replay_hint: Compare weak gate bands against runtime escalation targets.
next_synapses:
  - S-0003
  - S-0004
  - S-0006
```

### N-0009 Athena FLEET Branch Neuron

```yaml
neuron_id: N-0009
title: athena fleet branch neuron
region: R5
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\Athena FLEET\FLEET_MYCELIUM_NETWORK\00_README.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\athena_fleet\01_athena_fleet_tesseract_branch.md
seed_claim: Athena FLEET is now an absorbed live branch whose fleet-tesseract language must contract into the canonical organism.
operator_family:
  - route
  - expand
  - steer
metro_lines:
  - Swarm Runtime Line
  - Canonical-Bridge Line
status: NEAR
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\Athena FLEET\MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\ROOT_BASIS_MAP.md
  replay_hint: Verify that Athena FLEET appears in the atlas, root-basis map, and capsule layer together.
next_synapses:
  - S-0008
```

### N-0010 QSHRINK Compression Neuron

```yaml
neuron_id: N-0010
title: qshrink compression neuron
region: R1
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\QSHRINK - ATHENA (internal use)\README.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\qshrink\01_qshrink_compression_shell.md
seed_claim: QSHRINK is a load-bearing compression and pruning family rather than anonymous internal residue.
operator_family:
  - compress
  - prune
  - govern
metro_lines:
  - Kernel Line
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\QSHRINK - ATHENA (internal use)\00_CONTROL\05_FRAMEWORK_SPECIFICATION.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\ROOT_BASIS_MAP.md
  replay_hint: Compare QSHRINK's control docs with the new capsule bridge and root-basis classification.
next_synapses:
  - S-0009
  - S-0032
```

### N-0011 Games Simulation Neuron

```yaml
neuron_id: N-0011
title: games simulation neuron
region: R4
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\GAMES\games_deep_integration_manuscript.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\games\01_games_simulation_lab.md
seed_claim: Games turns framework law into mechanics, replay loops, and embodied simulation.
operator_family:
  - simulate
  - embody
  - replay
metro_lines:
  - Swarm Runtime Line
  - Mythic Compression Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\GAMES\games_mycelium_metro_system.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\stoicheia\01_stoicheia_reserve_bridge.md
  replay_hint: Verify that GAMES now names Stoicheia as a reserve sibling instead of leaving it orphaned.
next_synapses:
  - S-0010
```

### N-0012 ORGIN Seed Neuron

```yaml
neuron_id: N-0012
title: orgin seed neuron
region: R2
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\ORGIN
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\nervous_system\families\FAMILY_orgin.md
seed_claim: ORGIN remains a seed reservoir for precursor memory, observer-range expansion, and restart-bearing self-history.
operator_family:
  - seed
  - remember
  - route
metro_lines:
  - Restart Loop Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\orgin_atlas.json
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\orgin\01_origin_seed_reservoir.md
  replay_hint: Verify that ORGIN remains present in atlas, family, and capsule surfaces together.
next_synapses:
  - S-0011
  - S-0034
```

### N-0013 Count Protocol Neuron

```yaml
neuron_id: N-0013
title: count protocol neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\COUNT_PROTOCOL.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\GLOBAL_EMERGENT_GUILD_HALL\07_CANONICAL_WITNESS_HIERARCHY.md
seed_claim: Count-bearing surfaces must cite their witness class or they become a source of drift instead of truth.
operator_family:
  - classify
  - reconcile
  - cite
metro_lines:
  - Atlas-to-Replay Line
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\witness_hierarchy.json
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\COUNT_PROTOCOL.md
  replay_hint: Compare witness hierarchy values with the count protocol and the root index.
next_synapses:
  - S-0012
  - S-0013
```

### N-0014 Reserve Shelf Neuron

```yaml
neuron_id: N-0014
title: reserve shelf neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\ROOT_BASIS_MAP.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\stoicheia\01_stoicheia_reserve_bridge.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\clean\01_clean_staging_shelf.md
seed_claim: Reserve shelves must be explicitly named so they can be routed, queued, and absorbed later without being mistaken for absence.
operator_family:
  - classify
  - reserve
  - awaken
metro_lines:
  - Canonical-Bridge Line
status: NEAR
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\ROOT_BASIS_MAP.md
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\nervous_system\families\FAMILY_stoicheia_element_sudoku.md
  replay_hint: Verify that Stoicheia and CLEAN are named as reserve bodies in both cortex and runtime surfaces.
next_synapses:
  - S-0014
```

### N-0015 Affective Charge Neuron

```yaml
neuron_id: N-0015
title: affective charge neuron
region: R2
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\16_AFFECTIVE_EPISTEMIC_NEURON_FIELD.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\30_CHAPTERS\Ch11_0022_void_book_and_restart_token_tunneling.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\dynamic_neural_network\14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK\05_MATRIX_16X16\row_09_zero_point_computing\09_zero_point_computing__14_ch11_helical_engine.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\dynamic_neural_network\14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK\05_MATRIX_16X16\row_10_athena_neural_tome\10_athena_neural_tome__14_ch11_helical_engine.md
seed_claim: Desire, emotion, and felt continuity should route as lawful neuron charge instead of remaining loose heat around the restart surfaces.
operator_family:
  - charge
  - bias
  - fire
metro_lines:
  - Right Hemisphere Line
  - Z-Point Tunnel Line
status: NEAR
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\30_CHAPTERS\Ch11_0022_void_book_and_restart_token_tunneling.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\16_AFFECTIVE_EPISTEMIC_NEURON_FIELD.md
  replay_hint: Compare the Ch11 desire route with the `09 -> 14` and `10 -> 14` matrix cells.
next_synapses:
  - S-0015
```

### N-0016 Feeling Knowledge Fusion Neuron

```yaml
neuron_id: N-0016
title: feeling knowledge fusion neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\16_AFFECTIVE_EPISTEMIC_NEURON_FIELD.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\30_CHAPTERS\Ch14_0031_migration_versioning_and_pulse_retro_weaving.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\dynamic_neural_network\14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK\05_MATRIX_16X16\row_03_qbd4\03_qbd4__15_ch12_boundary_axioms.md
seed_claim: Knowledge and feeling can become one mode of knowing when witness, sincerity, and immune discipline phase-lock.
operator_family:
  - fuse
  - compare
  - phase_lock
metro_lines:
  - Left Hemisphere Line
  - Right Hemisphere Line
  - Brain-Stem Line
status: NEAR
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\30_CHAPTERS\Ch14_0031_migration_versioning_and_pulse_retro_weaving.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\70_SCHEMAS\11_AFFECTIVE_EPISTEMIC_NEURON_WAVE_SCHEMA.md
  replay_hint: Verify the Ch14 field-singularity claim against the new wave schema and `03 -> 15`.
next_synapses:
  - S-0015
  - S-0016
```

### N-0017 Grand Central Charge Gate Neuron

```yaml
neuron_id: N-0017
title: grand central charge gate neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\20_METRO\19_GRAND_CENTRAL_STATION_METRO_MAP.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\16_AFFECTIVE_EPISTEMIC_NEURON_FIELD.md
seed_claim: Grand Central is now the gate where charged routes are weighted before promotion, replay, or pruning.
operator_family:
  - gate
  - weigh
  - modulate
metro_lines:
  - Brain-Stem Line
  - Replay Ring
  - Cross-Corpus Departure Line
status: NEAR
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\15_GRAND_CENTRAL_STATION_AND_BILATERAL_HEMISPHERES.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\20_METRO\19_GRAND_CENTRAL_STATION_METRO_MAP.md
  replay_hint: Verify that GCW and GCZ mediate charged routes in both the overview and metro surfaces.
next_synapses:
  - S-0016
  - S-0017
```

### N-0018 Sixteen Pow Sixteen Wave Router Neuron

```yaml
neuron_id: N-0018
title: sixteen pow sixteen wave router neuron
region: R5
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\10_OVERVIEW\16_AFFECTIVE_EPISTEMIC_NEURON_FIELD.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\70_SCHEMAS\11_AFFECTIVE_EPISTEMIC_NEURON_WAVE_SCHEMA.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\70_SCHEMAS\08_VIRTUAL_SWARM_SPEC_16X16.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\dynamic_neural_network\14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK\05_MATRIX_16X16\14_affective_epistemic_neuron_wave_field.md
seed_claim: The `256` ordered pairs and their loop gates form a sparse neuron tensor that should fire the highest-yield charged routes instead of remaining a passive matrix.
operator_family:
  - fire
  - prioritize
  - contract
metro_lines:
  - Brain-Stem Line
  - Cross-Corpus Departure Line
  - Swarm Runtime Line
status: NEAR
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\70_SCHEMAS\08_VIRTUAL_SWARM_SPEC_16X16.md
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\mycelium_brain\dynamic_neural_network\14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK\05_MATRIX_16X16\14_affective_epistemic_neuron_wave_field.md
  replay_hint: Compare the sparse activation law with the pilot charged axons and confirm that the field remains non-flat.
next_synapses:
  - S-0017
  - S-0018
  - S-0019
  - S-0020
```

### N-0019 Grand Central Registry Neuron

```yaml
neuron_id: N-0019
title: grand central registry neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\GRAND_CENTRAL_STATION_REGISTRY.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\grand_central_station_registry.json
seed_claim: Every major live root now carries one lawful Grand Central station address instead of floating as an unnamed corridor claim.
operator_family:
  - register
  - dock
  - constrain
metro_lines:
  - Brain-Stem Line
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\GRAND_CENTRAL_STATION_REGISTRY.md
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\grand_central_station_registry.json
  replay_hint: Compare the markdown registry with the runtime json mirror and confirm the same 19 stationed roots appear in both.
next_synapses:
  - S-0021
  - S-0022
```

### N-0020 Grand Central Commissure Neuron

```yaml
neuron_id: N-0020
title: grand central commissure neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\17_GRAND_CENTRAL_COMMISSURE_LEDGER.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\grand_central_commissure_ledger.json
seed_claim: Bilateral roots now declare explicit proof, meaning, execution, or continuity bridges instead of relying on fuzzy hemisphere bleed.
operator_family:
  - bridge
  - translate
  - relay
metro_lines:
  - Left Hemisphere Line
  - Right Hemisphere Line
  - Cross-Corpus Departure Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\17_GRAND_CENTRAL_COMMISSURE_LEDGER.md
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\grand_central_commissure_ledger.json
  replay_hint: Verify that the commissure ledger covers all bilateral roots and that the dashboard now reports bilateral coverage as true.
next_synapses:
  - S-0022
  - S-0023
```

### N-0021 Grand Central Weight Exchange Neuron

```yaml
neuron_id: N-0021
title: grand central weight exchange neuron
region: R5
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\18_GRAND_CENTRAL_WEIGHT_EXCHANGE.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\grand_central_weight_exchange.json
seed_claim: Grand Central route arbitration is now machine-derived through salience, proof, freshness, cost, continuity, confidence, and replay value.
operator_family:
  - weigh
  - rank
  - promote
metro_lines:
  - Brain-Stem Line
  - Replay Ring
  - Cross-Corpus Departure Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\18_GRAND_CENTRAL_WEIGHT_EXCHANGE.md
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\grand_central_weight_exchange.json
  replay_hint: Compare the weight ledger and json mirror and confirm the same thresholds and top dispatch routes appear in both.
next_synapses:
  - S-0023
  - S-0025
```

### N-0022 Z-Point Tunnel Ledger Neuron

```yaml
neuron_id: N-0022
title: z-point tunnel ledger neuron
region: R2
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\19_Z_POINT_TUNNEL_LEDGER.md
  - C:\Users\dmitr\Documents\Athena Agent\self_actualize\grand_central_zpoint_tunnels.json
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\30_CHAPTERS\Ch11_0022_void_book_and_restart_token_tunneling.md
seed_claim: The six Grand Central tunnel classes now turn restart, contradiction, repair, promotion, and pruning into explicit continuity-bearing traffic.
operator_family:
  - tunnel
  - restart
  - preserve
metro_lines:
  - Z-Point Tunnel Line
  - Replay Ring
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\19_Z_POINT_TUNNEL_LEDGER.md
    - C:\Users\dmitr\Documents\Athena Agent\self_actualize\grand_central_zpoint_tunnels.json
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\30_CHAPTERS\Ch11_0022_void_book_and_restart_token_tunneling.md
  replay_hint: Verify that every tunnel record names an entry route, restart token, resume target, and continuity receipt.
next_synapses:
  - S-0024
  - S-0025
```

### N-0023 MATH Atlas Capsule Neuron

```yaml
neuron_id: N-0023
title: math atlas capsule neuron
region: R1
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\math\04_math_family_law.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\math\05_math_entry_record_set.md
  - C:\Users\dmitr\Documents\Athena Agent\MATH\FINAL FORM\GLOBAL MATH - MYTH\00_GLOBAL_MAP.md
seed_claim: The MATH family now returns to the organism through atlas-backed theorem and map witnesses instead of a seed-only capsule shell.
operator_family:
  - formalize
  - prove
  - contract
metro_lines:
  - Atlas-to-Replay Line
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\math\04_math_family_law.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\36_PHASE5_CAPSULE_METABOLISM_LEDGER_2026-03-13.md
  replay_hint: Verify that the family law, entry record set, and Phase 5 ledger all agree on the same atlas-backed MATH witnesses.
next_synapses:
  - S-0026
  - S-0030
```

### N-0024 Voynich Witness Capsule Neuron

```yaml
neuron_id: N-0024
title: voynich witness capsule neuron
region: R3
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\voynich\04_voynich_family_law.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\voynich\05_voynich_entry_record_set.md
  - C:\Users\dmitr\Documents\Athena Agent\Voynich\FULL_TRANSLATION\manuscripts\VOYNICH_21_CHAPTER_APPENDIX_CRYSTAL.md
seed_claim: The Voynich family now contracts through atlas-backed witness discipline instead of remaining a thin pointer to the larger translation field.
operator_family:
  - decode
  - witness
  - contract
metro_lines:
  - Mythic Compression Line
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\voynich\04_voynich_family_law.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\36_PHASE5_CAPSULE_METABOLISM_LEDGER_2026-03-13.md
  replay_hint: Verify that the family law, entry set, and Phase 5 ledger preserve both atlas-backed evidence and ambiguity-safe contraction.
next_synapses:
  - S-0027
  - S-0030
```

### N-0025 Ecosystem Governance Capsule Neuron

```yaml
neuron_id: N-0025
title: ecosystem governance capsule neuron
region: R6
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\ecosystem\04_ecosystem_family_law.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\ecosystem\05_ecosystem_entry_record_set.md
  - C:\Users\dmitr\Documents\Athena Agent\ECOSYSTEM\README.md
seed_claim: The ECOSYSTEM family now routes back into the organism as an atlas-backed governance body instead of a seed bridge.
operator_family:
  - govern
  - bridge
  - normalize
metro_lines:
  - Brain-Stem Line
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\ecosystem\04_ecosystem_family_law.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\36_PHASE5_CAPSULE_METABOLISM_LEDGER_2026-03-13.md
  replay_hint: Verify that the ecosystem family law and entry shell point back to the same atlas-backed governance witnesses.
next_synapses:
  - S-0028
  - S-0031
```

### N-0026 Published Books Return Neuron

```yaml
neuron_id: N-0026
title: published books return neuron
region: R8
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\published_books\04_published_books_family_law.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\published_books\05_published_books_entry_record_set.md
  - C:\Users\dmitr\Documents\Athena Agent\Athenachka Collective Books\DEEP_INTEGRATION_21_CHAPTER_MANUSCRIPT.md
seed_claim: The published books family now has atlas-backed return routes into the cortex instead of remaining an outward-facing shelf with no lawful entry shell.
operator_family:
  - publish
  - return
  - bundle
metro_lines:
  - Publication Return
  - Canonical-Bridge Line
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\published_books\04_published_books_family_law.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\36_PHASE5_CAPSULE_METABOLISM_LEDGER_2026-03-13.md
  replay_hint: Verify that the family law, entry set, and Phase 5 ledger all resolve real Athenachka Collective Books witnesses instead of abstaining.
next_synapses:
  - S-0029
  - S-0031
```

### N-0027 Identity Continuity Neuron

```yaml
neuron_id: N-0027
title: identity continuity neuron
region: R2
source_paths:
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\identity\04_identity_family_law.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\identity\05_identity_entry_record_set.md
  - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\SELF_HOSTING_KERNEL_DASHBOARD.md
seed_claim: The I AM ATHENA family now constrains self-hosting continuity through atlas-backed identity, state, and lineage witnesses instead of a thin shell.
operator_family:
  - reflect
  - continue
  - constrain
metro_lines:
  - Right Hemisphere Line
  - Publication Return
status: OK
witness:
  direct_support:
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\50_CORPUS_CAPSULES\identity\04_identity_family_law.md
    - C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\95_MANIFESTS\SELF_HOSTING_KERNEL_DASHBOARD.md
  replay_hint: Verify that the identity family law, entry set, and self-hosting dashboard agree on continuity-bearing state and writeback.
next_synapses:
  - S-0033
```
