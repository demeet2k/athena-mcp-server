# PACKET SCHEMA

## 1. Task Packet

```yaml
task_id: TASK_YYYYMMDD_slug
title: short task name
objective: one-sentence target
depth: 3
sources:
  - absolute path
constraints:
  - feasibility rule
  - output rule
deliverable: expected final artifact
truth_target: OK
stop_conditions:
  - witness closure reached
  - outside evidence required
```

## 2. Worker Packet

```yaml
packet_id: PKT_task_addr
address: E-W-F
role: short worker role
source_shard:
  path: absolute path
  lines_or_region: freeform locator
question: what this worker must answer
output_type: note | schema | theorem | route | contradiction
dependencies:
  - parent packet ids
witness:
  sources_seen:
    - path
  replay_hint: short rerun instruction
status: AMBIG
next_contraction_target: E-W
```

## 3. Archetype Packet

```yaml
packet_id: ARCH_task_E-W
address: E-W
children:
  - E-W-E
  - E-W-W
  - E-W-F
  - E-W-A
retained_claims:
  - claim
discarded_claims:
  - claim
conflicts:
  - unresolved issue
status: NEAR
```

## 4. Final Synthesis Packet

```yaml
synthesis_id: SYN_task
task_id: TASK_YYYYMMDD_slug
pillars:
  earth: summary
  water: summary
  fire: summary
  air: summary
canonical_output: final integrated artifact
witness_summary:
  supporting_sources:
    - absolute path
  unresolved_items:
    - item
status: OK
next_seed: optional follow-on task
```

## 5. Status Semantics

- `OK`
  - source-backed, replayable, and ready for reuse
- `NEAR`
  - structurally useful but still missing one or more witness items
- `AMBIG`
  - multiple admissible readings remain open
- `FAIL`
  - infeasible or contradicted under current evidence
