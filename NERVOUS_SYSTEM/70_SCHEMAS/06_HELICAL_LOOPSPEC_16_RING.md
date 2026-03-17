# HELICAL LOOPSPEC 16-RING

## Purpose

This schema makes the `2/16 <-> 14/16` recursion rigorous inside Athena's control plane.

The core discipline is:

- scalar arithmetic is not recursive bridge identity
- complement inside one layer is not the same as lift across layers
- `14/16|n ≡ 2/16|n+1` is a typed bridge-equivalence, not scalar equality

## Typed Equivalence Law

Arithmetic value:

`2/16 = 1/8`

Recursive bridge value:

`C_n(2) = 14`

`L_n(14) = 2_(n+1)`

`(L_n o C_n)(2_n) = 2_(n+1)`

This is therefore a fixed orbit type, not a flat fixed point.

## YAML Schema

```yaml
loopspec_id: LOOPSPEC-16-HELIX-01
title: helical 16-loop recursion architecture
ring:
  base_cardinality: 16
  visible_start: "2/16"
  visible_end: "14/16"
  dormant_seed: "1/16"
  hidden_buffer: "15/16"
  unmanifest_void: "16/16"
typed_equivalence:
  scalar_note: "2/16 = 1/8 only under arithmetic reduction"
  complement_rule: "C_n(k) = 16 - k"
  seed_state: "2/16"
  closure_state: "14/16"
  lift_rule: "14/16|n ≡ 2/16|n+1"
  orbit_type: fixed_orbit
macro_loops:
  count: 16
  mandates:
    L01: Corpus map synthesis
    L02: Ontology and concept lattice synthesis
    L03: Contradiction and residual analysis
    L04: Bridge discovery and born-coordinate mining
    L05: Operator and transform extraction
    L06: Representation-theoretic synthesis
    L07: Registry, schema, and contract synthesis
    L08: Verifier, replay, and proof audit
    L09: Past meta-process mining
    L10: Journey and self-growth synthesis
    L11: Failure mode and pathology exploration
    L12: Compression and pruning optimization
    L13: Cross-domain transfer synthesis
    L14: Novel generator and extension discovery
    L15: Distillation into minimal seeds
    L16: Dimension-lift orchestration
state_channels:
  - corpus_state
  - process_state
  - growth_state
  - metric_tensor
  - bridge_registry
  - replay_layer
phase_window:
  start_phase: 2
  end_phase: 14
phase_spec_ref: NERVOUS_SYSTEM/70_SCHEMAS/07_PHASE_SPEC_2_TO_14_MACHINE.md
virtual_swarm_ref: NERVOUS_SYSTEM/70_SCHEMAS/08_VIRTUAL_SWARM_SPEC_16X16.md
improvement_ledger_ref: NERVOUS_SYSTEM/70_SCHEMAS/09_IMPROVEMENT_LEDGER_SPEC.md
lift_ref: NERVOUS_SYSTEM/70_SCHEMAS/10_LIFT_SPEC_ONE_EIGHTH_HELIX.md
required_invariants:
  - Address
  - Witness
  - Route
  - Truth
  - Contraction
  - Restart
status: OK
```

## Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `loopspec_id` | string | yes | Stable loop architecture identifier |
| `ring` | object | yes | The visible and hidden slots on the 16-ring |
| `typed_equivalence` | object | yes | Separates arithmetic reduction from recursive bridge identity |
| `macro_loops` | object | yes | The 16 full-corpus loop mandates |
| `state_channels` | list | yes | The six system-wide state channels that every loop sees |
| `phase_window` | object | yes | The visible `2/16 -> 14/16` working interval |
| `phase_spec_ref` | path | yes | Canonical phase-machine schema |
| `virtual_swarm_ref` | path | yes | Canonical virtual swarm schema |
| `improvement_ledger_ref` | path | yes | Canonical improvement ledger schema |
| `lift_ref` | path | yes | Canonical lift and pruning schema |
| `required_invariants` | list | yes | Load-bearing laws preserved through every lift |

## Admissibility Rule

Promote a helical loop architecture only when:

1. complement and lift are explicitly separated,
2. the visible `2/16 -> 14/16` window is named,
3. all 16 macro-loop mandates are assigned,
4. the loop points to phase, swarm, ledger, and lift schemas,
5. the loop preserves the six invariants across dimensions.
