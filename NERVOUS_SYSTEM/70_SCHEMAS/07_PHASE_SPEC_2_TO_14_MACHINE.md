# PHASE SPEC 2-TO-14 MACHINE

## Purpose

This schema defines the visible helical working cycle from `2/16` through `14/16`.

The machine is not a flat circle.
`14/16` is the pre-closure band whose lawful output is the lifted seed at `2/16` one level higher.

## Phase Law

For loop `lambda` at dimension `n`:

`X_(n,lambda)^(2) -> X_(n,lambda)^(3) -> ... -> X_(n,lambda)^(14)`

with lift:

`X_(n+1,lambda)^(2) = L(X_(n,lambda)^(14))`

## YAML Schema

```yaml
phasespec_id: PHASESPEC-2-14-01
title: visible helical phase machine
visible_range:
  start: 2
  end: 14
phase_table:
  - phase: 2
    phase_id: PH02
    title: Seed unpack
    operator: SeedLoad
    output: seeded loop state
  - phase: 3
    phase_id: PH03
    title: Corpus decomposition
    operator: Decompose
    output: shards, motifs, contradictions, and candidates
  - phase: 4
    phase_id: PH04
    title: Deep synthesis
    operator: Synthesize
    output: integrated working state
  - phase: 5
    phase_id: PH05
    title: Contradiction and residual pressure
    operator: ResidualAudit
    output: unresolved tensions and collapse points
  - phase: 6
    phase_id: PH06
    title: Born-coordinate discovery
    operator: BirthMine
    output: candidate missing coordinates and bridges
  - phase: 7
    phase_id: PH07
    title: Operator extraction
    operator: ExtractOperators
    output: transforms, action terms, and update laws
  - phase: 8
    phase_id: PH08
    title: Representation and registry synthesis
    operator: ReframeAndRegister
    output: schemas, representations, and contracts
  - phase: 9
    phase_id: PH09
    title: Meta-observation
    operator: ObserveProcess
    output: process traces and yield notes
  - phase: 10
    phase_id: PH10
    title: Adversarial audit
    operator: AttackAndVerify
    output: unsupported claims, dead loops, and replay weakness
  - phase: 11
    phase_id: PH11
    title: Expansion improvement generation
    operator: Improve
    output: improvement ledger
  - phase: 12
    phase_id: PH12
    title: Prune bloat
    operator: Prune
    output: reduced but load-bearing state
  - phase: 13
    phase_id: PH13
    title: Compress
    operator: Distill
    output: seed kernel, proof kernel, and frontier packet
  - phase: 14
    phase_id: PH14
    title: Liminal transfer
    operator: Lift
    output: next-dimension seed state
required_metrics_audit: true
required_improvement_ledger: true
required_restart_seed: true
status: OK
```

## Transition Contract

Every phase must expose:

1. `operator`
2. `input_state`
3. `output_state`
4. `witness`
5. `metric_delta`
6. `residual`
7. `restart_seed`

No phase transition is complete if it produces commentary without an output state or witness.

## Lift Boundary

Phase `14` is the only lawful place where:

`14/16|n ≡ 2/16|n+1`

can be applied.

Within a layer, `2/16` and `14/16` are complements.
Across layers, `14/16` becomes the bridge state that re-enters as `2/16`.
