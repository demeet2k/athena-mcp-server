# IMPROVEMENT LEDGER SPEC

## Purpose

This schema makes the post-loop improvement output deterministic.

Every macro loop must leave the same 16 required sections so expansion improvements are comparable across dimensions and passes.

## YAML Schema

```yaml
improvementledgerspec_id: ILEDGER-16-SECTION-01
title: full-loop improvement ledger
loop_binding: LOOPSPEC-16-HELIX-01
required_sections:
  01_missing_distinctions: distinctions discovered but not yet stabilized
  02_contradictions_and_tensions: unresolved tensions and competing hypotheses
  03_born_coordinate_candidates: candidate new coordinates or missing dimensions
  04_bridge_candidates_and_receipts: bridge opportunities and witnessed bridges
  05_operator_improvements: transform and action-law upgrades
  06_representation_improvements: framing and representational refinements
  07_registry_and_schema_improvements: schema, contract, and registry upgrades
  08_verifier_and_certificate_improvements: proof and verifier upgrades
  09_replay_and_determinism_improvements: replayability and closure upgrades
  10_retrieval_and_index_improvements: search and indexing upgrades
  11_compression_opportunities: stronger seed or kernel contractions
  12_pruning_targets: stale, duplicated, unsupported, or dead tissue
  13_cross_domain_transfer_opportunities: reusable mappings across bodies
  14_process_improvements: better loop process and swarm orchestration
  15_self_growth_improvements: journey and self-growth implications
  16_next_loop_experiments: next experiments and changed dependencies
required_metrics:
  - coverage
  - coherence
  - contradiction_pressure
  - born_coordinate_discovery_rate
  - operator_closure
  - proof_density
  - replayability
  - retrieval_quality
  - schema_completeness
  - novelty_gain
  - pruning_efficiency
  - compression_ratio
  - cross_domain_transfer
  - meta_process_quality
  - self_growth_gain
  - unresolved_frontier_clarity
required_outputs:
  - metrics_before
  - metrics_after
  - unresolved_frontier
  - restart_seed
status: OK
```

## Required Contract

Every improvement ledger must answer:

1. what distinction was discovered
2. what contradiction survived
3. what coordinate was born
4. what bridge became more plausible
5. what operator improved
6. what representation sharpened
7. what schema changed
8. what proof burden remains
9. what replay path improved
10. what retrieval path improved
11. what should compress
12. what should be pruned
13. what should transfer
14. what process should improve
15. what growth changed
16. what the next loop should test

## Refusal Law

Do not call something an improvement ledger if it only summarizes progress.
It must change the next loop's action space.
