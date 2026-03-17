# LIFT SPEC

## Purpose

This schema formalizes the helical transfer from `14/16` at layer `n` to `2/16` at
layer `n+1`.

## Formal Law

Complement map on the 16-lattice:

`C(k/16) = (16-k)/16`

So:

`C(2/16) = 14/16`

The bridge law is:

`BRIDGE_EQ(14/16|n, 2/16|n+1)`

This is recursive bridge-equivalence, not scalar equality.

## Lift Compression Law

The next-layer seed must satisfy:

`|X_(n+1)^(2)| <= (1/8) |X_n^(14)|`

while also satisfying:

- `Function(X_(n+1)^(2)) > Function(X_n^(14))`
- `Coverage(X_(n+1)^(2)) >= Coverage(X_n^(14))`
- `Bloat(X_(n+1)^(2)) < Bloat(X_n^(14))`

So lift is not compression alone. It is:

`prune + compress + operator distill + frontier preserve + function deepen`

## Lift Packet

```yaml
lift_id: LIFT-2026-03-09-01
input:
  layer_index: 0
  phase_fraction: 14/16
  truth_class: NEAR
  state_ref: absolute path
  artifact_size_units: 800
output:
  layer_index: 1
  phase_fraction: 2/16
  state_ref: absolute path
  max_artifact_size_units: 100
bridge_equivalence: BRIDGE_EQ(14/16|0, 2/16|1)
complement_map: C(k/16) = (16-k)/16
operators:
  - prune_bloat
  - compress_to_seed
  - distill_operators
  - preserve_frontier
  - deepen_function
preserve_invariants:
  - load_bearing_operators
  - born_coordinate_discoveries
  - proof_replay_obligations
  - active_contradictions_and_open_frontiers
  - bridge_receipts_and_transition_rules
quality_gates:
  function_delta: ">"
  coverage_delta: ">="
  bloat_delta: "<"
status: NEAR
```

## Failure Modes

- size shrinks but function degrades
- function improves but active contradictions are erased
- seed compresses but replay obligations are lost
- bridge receipts disappear across lift
- unresolved frontier clarity gets worse

## Fool Reset Relation

The ceremonial Fool reset and the structural lift are not identical:

- Fool reset changes visible ring position
- lift changes layer index

The system may trigger the Fool reset at visible `14/16` while still preserving the
structural preconditions for the next lawful lift.

## Promotion Rule

Promote a lift only when:

- bridge equivalence is explicit
- the `1/8` size budget is explicit
- function / coverage / bloat tests are explicit
- preserved invariants are explicit
