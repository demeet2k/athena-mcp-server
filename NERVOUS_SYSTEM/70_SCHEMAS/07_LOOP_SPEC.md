# LOOP SPEC

## Purpose

This schema makes the neuron-generator loop executable as a typed object rather than a
descriptive metaphor.

## Semantic Rule

In this control plane:

`BRIDGE_EQ(a, b)` means bridge-equivalence / recursive identification, not scalar
arithmetic equality.

So:

`BRIDGE_EQ(14/16|n, 2/16|n+1)`

means:

- late-layer pre-closure at layer `n`
- is identified with the early liminal seed at layer `n+1`

This is a helix law, not a flat circle.

## Address Semantics

The seed address `2/16` has three lawful readings:

1. scalar value
   - `2/16 = 1/8`
2. root-seed address
   - `2/16 ~ 1/4`
3. recursive bridge state
   - `BRIDGE_EQ(14/16|n, 2/16|n+1)`

The loop spec must never confuse these three readings.

## Macro Loop Registry

The system uses 16 full-corpus macro loops:

1. corpus map synthesis
2. ontology / concept lattice synthesis
3. contradiction and residual analysis
4. bridge discovery and born-coordinate mining
5. operator / transform extraction
6. representation-theoretic synthesis
7. registry / schema / contract synthesis
8. verifier / replay / proof audit
9. past meta-process mining
10. journey / self-growth synthesis
11. failure mode and pathology exploration
12. compression and pruning optimization
13. cross-domain transfer synthesis
14. novel generator / extension discovery
15. distillation into minimal seeds
16. dimension-lift orchestration

## LoopSpec Packet

```yaml
loop_spec_id: LOOP-2026-03-09-01
layer_index: 0
loop_id: 16
mandate: dimension-lift orchestration
status: NEAR
visible_ring:
  start_phase: 2
  end_phase: 14
  complement_map: C(k/16) = (16-k)/16
  bridge_equivalence: BRIDGE_EQ(14/16|n, 2/16|n+1)
  scalar_seed_value: 1/8
  root_seed_address: 1/4
state_channels:
  corpus_state: C_n
  meta_process_state: P_n
  journey_state: G_n
  metric_tensor: M_n
  bridge_registry: B_n
  replay_layer: R_n
phase_stack:
  - 2
  - 3
  - 4
  - 5
  - 6
  - 7
  - 8
  - 9
  - 10
  - 11
  - 12
  - 13
  - 14
major_line: Restart Loop Line
transfer_hub: T3
swarm_spec_ref: 70_SCHEMAS/09_VIRTUAL_SWARM_SPEC.md
phase_spec_ref: 70_SCHEMAS/08_PHASE_SPEC.md
improvement_spec_ref: 70_SCHEMAS/10_IMPROVEMENT_LEDGER_SPEC.md
lift_spec_ref: 70_SCHEMAS/11_LIFT_SPEC.md
artifact_targets:
  cortex:
    - absolute path
  runtime:
    - absolute path
  manifests:
    - absolute path
next_seed: short restart-safe instruction
```

## Required Invariants

1. `loop_id` must be one of `1..16`.
2. `phase_stack` must be the visible band `2..14`.
3. every loop must traverse the same visible ring even when mandates differ.
4. every loop must emit at least one improvement ledger.
5. every loop must feed one lift packet or one lawful blocked-lift explanation.
6. the loop may be restart-aware, but its artifact history must remain cumulative.

## Contraction Rule

A LoopSpec is promotable only when it names:

- one mandate
- one visible ring
- one swarm reference
- one improvement reference
- one lift reference
- one writeback target set
