# WAVE_2026-03-09_future_skill_meta_swarm

## Goal

Synchronize the hypermap and swarm skill families into one bounded execution wave.

## Active Pods

1. hypermap pod
2. ganglion pod
3. neuron pod
4. wave and cortex pod

## Skills

- `face-manifold-router` | deps: regime-router
- `arc-rail-phase-router` | deps: face-manifold-router, chapter-map-ledger
- `packet-truth-typist` | deps: witness-bundle-assembler
- `metallic-scale-planner` | deps: face-manifold-router, microcell-specializer
- `ganglion-bootstrapper` | deps: none
- `neuron-library-builder` | deps: ganglion-bootstrapper
- `pod-frontier-splitter` | deps: ganglion-bootstrapper
- `wave-synchronizer` | deps: pod-frontier-splitter, packet-wave-planner
- `cortex-writeback-manager` | deps: wave-synchronizer
- `session-handoff-packer` | deps: cortex-writeback-manager
- `family-swarm-conductor` | deps: ganglion-bootstrapper, neuron-library-builder, wave-synchronizer
- `microcell-specializer` | deps: family-swarm-conductor
- `swarm-benchmark-ledger` | deps: family-swarm-conductor, route-quality-auditor

## Residuals

- live Docs remains blocked until OAuth files exist
- family ganglia should deepen from seed notes into live queues and receipts
