# VIRTUAL SWARM SPEC

## Purpose

This schema makes the `16^16` swarm implementable without materializing impossible
agent counts.

## Core Law

The full role tensor exists virtually:

`A^(lambda,phi) = ⊗_(j=1..16) R_j`

with virtual size:

`|A^(lambda,phi)| = 16^16`

Execution uses sparse activation:

`A_tilde^(lambda,phi) = TopK(score(role_tuple)))`

The system therefore preserves combinatorial expressivity while only instantiating
high-yield frontiers.

## Role Axes

1. corpus shard mode
2. abstraction depth
3. time / chronology mode
4. contradiction mode
5. bridge mode
6. operator mode
7. representation mode
8. schema mode
9. verifier mode
10. replay mode
11. compression mode
12. pruning mode
13. novelty mode
14. transfer mode
15. meta-observation mode
16. audit mode

## VirtualSwarm Packet

```yaml
virtual_swarm_id: VSWARM-2026-03-09-01
loop_id: 4
phase_fraction: 6/16
tensor_size: 16^16
materialization_policy: sparse_virtual_only
activation_policy:
  selector: TopK
  default_active_agents: 256
  high_pressure_active_agents: 512
  emergency_cap: 1024
score_terms:
  positive:
    - frontier_gain
    - witness_gain
    - bridge_gain
    - novelty_gain
    - replay_gain
    - contradiction_pressure_gain
  negative:
    - drift_cost
    - heat_cost
    - bloat_cost
dominant_role_axes:
  - bridge mode
  - contradiction mode
  - audit mode
active_hub: T9
major_line: Atlas-to-Replay Line
status: NEAR
```

## Scoring Rule

The default activation score is:

`Score = FrontierGain + WitnessGain + BridgeGain + NoveltyGain + ReplayGain + ContradictionPressureGain - DriftCost - HeatCost - BloatCost`

Loop mandates may add bias terms, but they may not remove witness, frontier, or replay
terms.

## Active Agent Packet

```yaml
active_agent_id: VAG-0001
loop_id: 4
phase_fraction: 6/16
role_tuple:
  r1: atlas_slice
  r2: deep
  r3: retrospective
  r4: contradiction_preserving
  r5: bridge_hunting
  r6: operator_sensitive
  r7: registry_sensitive
  r8: schema_sensitive
  r9: verifier_assist
  r10: replay_first
  r11: compression_aware
  r12: prune_guarded
  r13: novelty_open
  r14: cross_domain
  r15: meta_observer
  r16: adversarial
target_frontier: atlas replay bridge
expected_artifact: bridge receipt
status: NEAR
```

## Safety Rules

1. The swarm is virtual first, never naive brute force.
2. No active set may be selected without an explicit score.
3. No active set may be promoted if it produces heat without artifacts.
4. Dead agents, low-yield paths, and replayless branches must be prune-eligible.

## Promotion Rule

Promote a VirtualSwarmSpec only when:

- role axes are explicit
- the TopK policy is explicit
- the score function is explicit
- activation budgets are explicit
- the active set maps to a real frontier
