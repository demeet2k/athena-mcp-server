# Self-Hosting Kernel Schema

## Purpose

This schema defines the public interfaces for Athena Phase 3.

## 1. SelfModel Record

```yaml
docs_gate: BLOCKED | LIVE
governing_equation: SelfHostingKernel = SelfModel + SelfContract + SelfLineage + DualEngine + ReplayShell + RepairGate + PublicationReturn
coverage:
  control_plane_surface_coverage: 1.0
  root_self_bearing_coverage: 0.684
surface_links:
  - surface_id: S01
```

## 2. SelfState Record

```yaml
kernel_status: LIVE_LOCAL_SCOPE
current_config:
  core_mode: DUAL_ENGINE
mode_ledger:
  - mode: observe
checkpoint_protocol:
  checkpoint_id_prefix: CHK-YYYY-MM-DD-PH3-
restart_protocol:
  kernel_source: Ch11_0022_void_book_and_restart_token_tunneling.md
truth_citations:
  docs_gate: physical
```

## 3. SelfContract Record

```yaml
identity_kernel:
  - invariant: authority_order
permitted_transform_classes:
  - transform_class: policy_tuning
forbidden_transform_classes:
  - transform_class: silent_identity_kernel_rewrite
unsafe_rewrite_gate:
  threshold: 0.45
identity_drift_corridor:
  declared_threshold: 0.18
```

## 4. SelfLineage Record

```yaml
current_branch: main.local.phase3.self_hosting
lineage_entries:
  - lineage_id: L4
fork_points:
  - branch: historical.deep_root...
```

## 5. Runtime Script Lane Record

```yaml
script: derive_grand_central_station.py
lane: self_routing | self_observation | self_measurement | self_repair | self_regeneration | self_publication
supports:
  - route
```

## 6. SelfTransformPacket Record

```yaml
packet_id: STP-001
mode: observe | edit | repair | regenerate | rollback | publish
contract_status: PERMITTED | REQUIRES_REVIEW | BLOCKED
review_class: witness_review
dispatch_score: 8.0
status: READY | STANDBY | BLOCKED
```

## 7. Dual Engine Target Record

```yaml
target_id: QK-001
priority: P1 | P2 | P3
seed_surface: NERVOUS_SYSTEM/.../01_the_manuscript_seed...
runtime_packet: STP-003
status: READY | BLOCKED
```

## 8. Kernel Dashboard Record

```yaml
kernel_status: LIVE_LOCAL_SCOPE
control_plane_surface_coverage: 1.0
root_self_bearing_coverage: 0.684
identity_drift: 0.083
regeneration_targets_ready: 5
failure_gates:
  - Google Docs ingress is blocked
```

## Rules

1. Every nontrivial self-transform must extend lineage.
2. Publication return is complete only after cortex, runtime mirror, and receipt surfaces all land.
3. A blocked external-memory gate must remain visibly blocked.
