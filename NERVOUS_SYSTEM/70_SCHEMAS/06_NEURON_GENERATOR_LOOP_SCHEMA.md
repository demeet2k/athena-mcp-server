# NEURON GENERATOR LOOP SCHEMA

## Purpose

This schema normalizes the official 16-loop restart-aware control surface.

## Loop State Packet

```yaml
run_id: NG-2026-03-09-01
mode: neuron-generator-16-loop
gate:
  status: BLOCKED
  checked_at: 2026-03-09
  blocker: Missing OAuth client file: credentials.json
deep_loop:
  current: 1
  target: 16
ceremonial_loop:
  current: 1
  trigger_reset_at: 14
  restart_floor: 2
reset_count: 0
fool_checkpoint:
  status: PENDING
  target_surface: Ch11 / restart-token / neuron humility audit
frontier:
  primary: reusable neuron library and synapse integration
  secondary:
    - atlas-to-runtime replay bridge
    - chapter and appendix contraction
major_lines:
  - Canonical-Bridge Line
  - Restart Loop Line
transfer_hub: T3
artifact_targets:
  cortex:
    - absolute path
  runtime:
    - absolute path
  manifests:
    - absolute path
truth_class: NEAR
next_seed: short restart-safe instruction
```

## Field Notes

- `deep_loop.current` is the true artifact-bearing progress counter.
- `ceremonial_loop.current` is the visible progress counter that can reset.
- `reset_count` records how many times the Fool event fired.
- `fool_checkpoint.status` should be `PENDING`, `TRIGGERED`, or `INTEGRATED`.
- `major_lines` should include the line actually ridden in the current loop.
- `artifact_targets` should name the writeback surfaces for the loop.

## Formal Helix Fields

The loop state packet should also preserve:

- `complement_map: C(k/16) = (16-k)/16`
- `bridge_equivalence: BRIDGE_EQ(14/16|n, 2/16|n+1)`
- `scalar_seed_value: 1/8`
- `root_seed_address: 1/4`

These fields should be treated as distinct semantic layers rather than collapsed into
ordinary arithmetic equality.

## Determinism Rule

The state packet should change only when one of the following occurs:

1. a loop lands an artifact
2. a Fool reset fires
3. the primary frontier changes
4. the gate status changes

## Completion Rule

Mark the packet `truth_class: OK` only when:

1. `deep_loop.current = 16`
2. at least one Fool reset has been integrated
3. the next seed is preserved
4. the cortex, runtime, and manifest surfaces all received writeback

## Companion Specs

- `07_LOOP_SPEC.md`
- `08_PHASE_SPEC.md`
- `09_VIRTUAL_SWARM_SPEC.md`
- `10_IMPROVEMENT_LEDGER_SPEC.md`
- `11_LIFT_SPEC.md`
