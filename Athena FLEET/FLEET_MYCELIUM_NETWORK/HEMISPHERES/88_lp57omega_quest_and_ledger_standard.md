# LP-57Omega Quest and Ledger Standard

Quest rows: `228`
Ledger rows: `228`

## Quest Contract Fields

| Field | Status |
| --- | --- |
| quest_id | required |
| zone | required |
| parent_loop | required |
| objective | required |
| why_now | required |
| target_surfaces | required |
| witness_needed | required |
| dependencies | required |
| coordinate_targets | required |
| acceptance_rule | required |
| restart_seed | required |

## Ledger Fields

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

## Sample Hall Quest

- hall quest id: `Q57-L01-SYNTHESIZER-HALL`
- temple quest id: `TQ57-L01-SYNTHESIZER-TEMPLE`

## Sample Ledger Entry

- agent id: `L01.A1.D0.B0000.SYNTHESIZER-MASTER`
- action type: `synthesize`
- linked quests: `Q57-L01-SYNTHESIZER-HALL, TQ57-L01-SYNTHESIZER-TEMPLE`
- dense kernel ref: `S20`
