# SYNAPTIC HANDOFF PROTOCOL

## Packet Contract

- `bridge_family_id`
- `phase`
- `source_agent`
- `target_agent`
- `trigger`
- `witness_basis`
- `route`
- `expected_writeback`
- `replay_surface`
- `verification_surface`
- `proof_state`

## Active Packets

| Packet | Bridge Family | Phase | Source Agent | Target Agent | Source Body | Target Body | Trigger | Route |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SHP-001 | - | - | overseer | corridor-builder | A02 | A16 | admit remaster front | A02 -> GCL+GCR -> GCZ -> A16 |
| SHP-002 | - | - | corridor-builder | proof-compiler | A16 | A06 | materialize fleet-to-proof bridge | A16 -> GCL+GCR -> GCZ -> A06 |
| SHP-003 | - | - | proof-compiler | corridor-builder | A06 | A09 | bind proof-safe compression | A06 -> GCR -> GCW -> A09 |
| SHP-004 | - | - | corridor-builder | overseer | A16 | A15 | inherit origin memory | A16 -> GCL+GCR -> GCP -> A15 -> A02 |
| SHP-005 | - | - | overseer | proof-compiler | A02 | A06 | run verification closure | A02 -> A06 -> A01 |
| SHP-006 | - | - | proof-compiler | overseer | A06 | A02 | publish remaster return | A06 -> A01 -> A02 |
