# PHASE SPEC

## Purpose

This schema defines the visible `2/16 -> 14/16` working cycle as a strict operator
stack.

## Phase Packet

```yaml
phase_spec_id: PHASE-06
phase_fraction: 6/16
phase_name: born-coordinate-discovery
operator: BirthMine
entry_condition: contradiction pressure has been witnessed
required_inputs:
  - current loop state
  - current active swarm slice
required_outputs:
  - born-coordinate candidates
  - bridge candidates
required_metrics:
  - m3
  - m4
  - m16
artifact_minimum:
  - ledger update
advance_condition: born-coordinate candidates are typed and witnessed
status: NEAR
```

## Phase Registry

| Phase | Name | Operator | Primary Obligation |
|------|------|----------|--------------------|
| `2/16` | seed unpack | `SeedLoad` | load the prior layer's distilled seed |
| `3/16` | corpus decomposition | `Decompose` | split corpus, process, and growth channels into workable fronts |
| `4/16` | deep synthesis | `Synthesize` | run high-yield synthesis over the active sparse swarm |
| `5/16` | contradiction and residual pressure | `ResidualAudit` | expose contradictions, overcompression, and unresolved fibers |
| `6/16` | born-coordinate discovery | `BirthMine` | mine missing coordinates and bridge candidates |
| `7/16` | operator extraction | `ExtractOperators` | derive transform laws, actions, and update terms |
| `8/16` | representation / registry synthesis | `SynthesizeRegistry` | rewrite discoveries into schema, registry, and composition contracts |
| `9/16` | meta-observation | `MetaObserve` | observe the process itself and identify recurring yield paths |
| `10/16` | adversarial audit | `AdversarialAudit` | attack false closures, fake equivalences, and unsupported claims |
| `11/16` | expansion improvement generation | `BuildImprovements` | emit the full improvement ledger |
| `12/16` | prune bloat | `Prune` | remove low-yield, replayless, duplicate, and stale tissue |
| `13/16` | compress | `Compress` | distill operators, bridges, proofs, seeds, and open frontiers |
| `14/16` | liminal transfer / pre-closure | `LiftPrepare` | prepare the bridge into the next layer and expose Fool-reset pressure |

## Phase Advancement Rules

1. No phase may advance without a metric pass over the active state.
2. `11/16` must emit an improvement ledger rather than a generic summary.
3. `12/16` must preserve load-bearing invariants while pruning fluff.
4. `13/16` must preserve unresolved frontiers instead of pretending closure.
5. `14/16` must either:
   - generate a valid lift packet, or
   - trigger the ceremonial Fool reset while preserving deep artifacts.

## Phase-to-Metric Binding

Every phase must evaluate the 16-metric tensor, but each phase has dominant metrics:

- `2/16`: `m7`, `m8`, `m16`
- `3/16`: `m1`, `m8`, `m14`
- `4/16`: `m1`, `m2`, `m10`
- `5/16`: `m3`, `m16`
- `6/16`: `m4`, `m13`, `m16`
- `7/16`: `m5`, `m6`
- `8/16`: `m2`, `m7`, `m9`
- `9/16`: `m14`, `m15`
- `10/16`: `m3`, `m6`, `m7`
- `11/16`: `m10`, `m11`, `m16`
- `12/16`: `m11`, `m12`
- `13/16`: `m5`, `m12`, `m16`
- `14/16`: `m2`, `m7`, `m15`, `m16`

## Terminal Rule

The visible ring ends at `14/16`, but the executable phase machine does not terminate
there. It must hand off to `11_LIFT_SPEC.md`.
