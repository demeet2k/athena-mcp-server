# MANIFEST AND PACKET SCHEMA

## 1. Purpose

This document defines machine-readable payload formats for runs, packets, outputs, and verification ledgers.

## 2. Run Manifest

Definition 2.1 (Run Manifest).
A run manifest is the canonical record of a parallel execution:

```text
RunManifest = {
  run_id,
  objective,
  source_surfaces[],
  wave_index,
  packet_ids[],
  verdict,
  created_at,
  updated_at
}
```

## 3. Work Packet

Definition 3.1 (Work Packet).

```text
WorkPacket = {
  packet_id,
  parent_id,
  agent_addr,
  packet_type,
  task_body,
  input_refs[],
  output_targets[],
  truth_class,
  witness_ptrs[],
  replay_ptr,
  dependencies[],
  status
}
```

Status values:
- queued
- running
- complete
- ambiguous
- quarantined

## 4. Output Artifact Record

```text
ArtifactRecord = {
  artifact_id,
  addr,
  file_path,
  produced_by,
  truth_class,
  witness_ptrs[],
  replay_ptr,
  migration_from,
  migration_to
}
```

## 5. Residual Ledger

Definition 5.1 (Residual Ledger).
Used for NEAR results where bounded approximation is acceptable.

```text
ResidualLedger = {
  ledger_id,
  subject,
  residual_type,
  bound,
  cause,
  upgrade_plan,
  owner
}
```

## 6. Evidence Plan

Used for AMBIG states:

```text
EvidencePlan = {
  plan_id,
  subject,
  candidates[],
  missing_evidence[],
  acquisition_steps[],
  escalation_rule
}
```

## 7. Conflict Receipt

Used for FAIL or CONFLICT states:

```text
ConflictReceipt = {
  receipt_id,
  src_a,
  src_b,
  contradiction_type,
  minimal_witness_set[],
  quarantine_target,
  next_action
}
```

## 8. Naming Rules

- IDs must be stable within a run.
- File targets must be absolute or workspace-root relative.
- Packet IDs and artifact IDs must not be reused.

## 9. Status

These schemas make the ecosystem legible to both humans and future automation.
