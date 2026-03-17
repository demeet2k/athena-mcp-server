# LIFT SPEC ONE-EIGHTH HELIX

## Purpose

This schema formalizes the one-eighth lift law:

the next-dimension seed must be smaller, more functional, and less bloated than the prior pre-closure state.

## Lift Equations

For loop state `X`:

`|X_(n+1)^(2)| <= (1/8) * |X_n^(14)|`

`Function(X_(n+1)^(2)) > Function(X_n^(14))`

`Coverage(X_(n+1)^(2)) >= Coverage(X_n^(14))`

`Bloat(X_(n+1)^(2)) < Bloat(X_n^(14))`

Lift is therefore:

`Lift = Prune + Compress + OperatorDistill + FrontierPreserve + FunctionDeepen`

## YAML Schema

```yaml
liftspec_id: LIFTSPEC-1-8-HELIX-01
title: one-eighth helical lift
input_band: "14/16"
output_band: "2/16"
bridge_equivalence: "14/16|n ≡ 2/16|n+1"
size_rule:
  max_ratio: 0.125
  comparison_basis: load_bearing_state_size
quality_rules:
  function: strictly_increase
  coverage: preserve_or_increase
  bloat: strictly_decrease
prune_components:
  - duplicate_summaries
  - stale_branches
  - unsupported_claims
  - dead_swarm_paths
  - replayless_shells
  - low_yield_expansions
preserved_invariants:
  I1: load_bearing_operators
  I2: born_coordinate_discoveries
  I3: proof_and_replay_obligations
  I4: active_contradictions_and_open_frontiers
  I5: bridge_receipts_and_transition_rules
required_outputs:
  - distilled_seed
  - proof_kernel
  - unresolved_frontier
  - restart_seed
  - lift_quality_score
status: OK
```

## Lift Quality Gate

Do not advance to `2/16` at the next layer unless:

1. the size ratio is at or below one eighth,
2. function improved,
3. bloat decreased,
4. unresolved frontier stayed visible,
5. replay and proof obligations survived the contraction.

## Failure Classes

- `FAIL`: compression destroyed function or erased witness
- `AMBIG`: the seed got smaller but coverage or replay status is unclear
- `NEAR`: the lift is structurally correct but still lacks proof or metric confidence
- `OK`: the lifted seed is smaller, deeper, and restart-safe
