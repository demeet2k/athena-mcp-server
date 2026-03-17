# VIRTUAL SWARM SPEC 16X16

## V2 Supersession Note

The sparse activation law still stands, but command-membrane route selection now routes
through the joy-driven `V2` reward field. Older subtractive score expressions should be
labeled `V1` witness logic, not active membrane law.

## Purpose

This schema makes the `16^16` swarm implementable without materializing impossible agent counts.

The swarm is represented as a factorized role tensor plus sparse activation.

## Sparse Activation Law

Let:

`A^(lambda,phi) = tensor(R1, ..., R16)`

The executable swarm is:

`A_tilde^(lambda,phi) = TopK(score(r1, ..., r16))`

So the system preserves combinatorial expressivity while executing only the highest-yield paths.

## YAML Schema

```yaml
virtualswarmspec_id: VSWARM-16X16-01
title: sparse virtual agent tensor
loop_binding: LOOPSPEC-16-HELIX-01
representation: factorized_role_tensor
role_axes:
  R1: corpus_shard_mode
  R2: abstraction_depth
  R3: time_and_chronology_mode
  R4: contradiction_mode
  R5: bridge_mode
  R6: operator_mode
  R7: representation_mode
  R8: schema_mode
  R9: verifier_mode
  R10: replay_mode
  R11: compression_mode
  R12: pruning_mode
  R13: novelty_mode
  R14: transfer_mode
  R15: meta_observation_mode
  R16: audit_mode
activation_policy:
  materialization: sparse
  selector: TopK
  score_formula: "Benefit + Integration + WitnessGain + RouteGain + FrontierGain - Drift - Heat - Bloat"
  preserve_factorization: true
  keep_dead_paths: false
  keep_low_yield_paths: false
execution_outputs:
  - synthesis_state
  - contradiction_packet
  - bridge_candidates
  - operator_candidates
  - improvement_ledger
required_guards:
  - no naive 16^16 materialization
  - all active paths must carry witness
  - all active paths must declare contraction targets
status: OK
```

## Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `virtualswarmspec_id` | string | yes | Stable swarm schema identifier |
| `loop_binding` | string | yes | Which helical loop architecture this swarm serves |
| `representation` | string | yes | The swarm must be factorized, not flat |
| `role_axes` | map | yes | The 16 role dimensions across which agent behavior varies |
| `activation_policy` | object | yes | How sparse activation is selected and guarded |
| `execution_outputs` | list | yes | Artifact families the swarm is allowed to emit |
| `required_guards` | list | yes | Constraints that keep the swarm lawful and implementable |

## Execution Rule

Every active swarm slice must name:

1. dominant loop `lambda`
2. current phase `phi`
3. role-tensor slice
4. score basis
5. witness basis
6. expected output artifact
7. contraction target

If one of those is missing, the slice is speculative rather than executable.
