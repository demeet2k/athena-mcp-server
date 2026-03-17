# IMPROVEMENT LEDGER SPEC

## Purpose

This schema formalizes the deep post-loop improvement output so each loop produces a
real expansion ledger rather than a vague "go deeper" note.

## Escalation Header

Every improvement ledger must report:

- prior weak gates
- newly promoted gates
- artifacts created
- remaining unresolved gates
- next frontier

## ImprovementLedger Packet

```yaml
improvement_ledger_id: IMP-2026-03-09-01
layer_index: 0
loop_id: 11
phase_origin: 11/16
truth_class: NEAR
prior_weak_gates:
  - G24
  - G26
  - G34
newly_promoted_gates:
  - G27
artifacts_created:
  - absolute path
remaining_unresolved_gates:
  - G24
  - G26
next_frontier: atlas replay bridge
metrics_before:
  m1: 0.0
metrics_after:
  m1: 0.0
sections:
  missing_distinctions_discovered: []
  contradictions_and_unresolved_tensions: []
  born_coordinate_candidates: []
  bridge_candidates_and_receipts: []
  operator_action_improvements: []
  representation_improvements: []
  registry_schema_improvements: []
  verifier_cert_improvements: []
  replay_determinism_improvements: []
  retrieval_index_improvements: []
  compression_opportunities: []
  pruning_targets: []
  cross_domain_transfer_opportunities: []
  process_improvements: []
  self_growth_improvements: []
  next_loop_experiments_and_dependency_changes: []
status: NEAR
```

## Required Sections

Every improvement ledger must contain all 16 sections:

1. missing distinctions discovered
2. contradictions and unresolved tensions
3. new born-coordinate candidates
4. bridge candidates and receipts
5. operator / action improvements
6. representation improvements
7. registry / schema improvements
8. verifier / certificate improvements
9. replay / determinism improvements
10. retrieval / index improvements
11. compression opportunities
12. pruning targets
13. cross-domain transfer opportunities
14. process improvements
15. self-growth / journey synthesis improvements
16. next-loop experiments and upstream/downstream dependency changes

## Ledger Rules

1. Empty sections are allowed only when explicitly witnessed as empty.
2. Contradictions must be preserved, not smoothed away.
3. Bridge claims require receipts.
4. Improvement proposals without artifact targets remain `AMBIG`.
5. Next-loop experiments must identify at least one dependency shift or frontier shift.

## Promotion Rule

An improvement ledger is promotable when:

- all 16 sections are present
- gate movement is explicit
- metrics before/after are recorded
- at least one artifact target is named
