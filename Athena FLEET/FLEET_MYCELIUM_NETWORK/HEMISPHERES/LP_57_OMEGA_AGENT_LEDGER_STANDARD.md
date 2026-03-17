# LP-57Omega Agent Ledger Standard

- Docs gate: `BLOCKED`
- Continuity law: `append-only, quest-linked, coordinate-stamped`
- Overlay law: `dense_kernel_ref is optional and never replaces the top-level coordinate stamp`

## Required Fields

| Field | Status |
| --- | --- |
| agent_id | required |
| loop_number | required |
| parent_agent | required |
| coordinate_stamp | required |
| source_region | required |
| action_type | required |
| affected_nodes | required |
| summary_of_change | required |
| reason_for_change | required |
| integration_gain | required |
| compression_gain | required |
| unresolved_followups | required |
| linked_quests | required |
| linked_agents | required |
| revision_confidence | required |
| timestamp_internal | required |
| dense_kernel_ref | optional overlay pointer |

## Overlay Recording Rule

- When a ledger action is routed through a dense-shell focus record, preserve the first lawful `DenseKernelRef65` binding in `dense_kernel_ref`.
- Receipts and change feeds remain witness history; registries and manifests remain canonical state.
