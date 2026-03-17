# Repair Ticket Queue

Date: `2026-03-13`
Docs gate: `BLOCKED`

## RepairTicket Contract

Each repair ticket must name:

- `ticket_id`
- `affected_frontier`
- `blocker_or_failure`
- `witness_basis`
- `retry_trigger`
- `escalation_target`
- `status`

## Active Tickets

| Ticket | Affected frontier | Blocker or failure | Witness basis | Retry trigger | Escalation target | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `RT-001` | `Q02` | missing `Trading Bot/credentials.json` and `Trading Bot/token.json` prevent live Docs ingress | `self_actualize/live_docs_gate_status.md`, quest board, requests board | OAuth files appear and authenticated search succeeds | keep Hall, Temple, queue, and reports blocker-honest | `BLOCKED-EXTERNAL` |
| `RT-002` | meta lanes | more than `2` stale scheduler packets | scheduler packet bundle plus report freshness fields | packet bundle refreshes below the stale threshold | contraction-only or synchronization-only pass | `ACTIVE-WHEN-TRIGGERED` |
| `RT-003` | repeated frontier drift | same frontier repeated for `3` cycles without a new artifact | receipts, reports, and touched paths fail to advance | new artifact lands or owner lane changes lawfully | compression review or closure review | `ACTIVE-WHEN-TRIGGERED` |
| `RT-004` | cohesion drift | stale-path debt remains above the first target `< 40` missing references | cohesion audit and pruning ledger | post-writeback audit shows material reduction | pruning pass and historical-path cleanup | `OPEN` |
| `RT-005` | `MATH` archive-root identity | duplicate ZIP lineages split one SHA across multiple archive roots | archive dark-matter witness, `athena-weave-scan` report | one canonical SHA-to-path map is published | Earth admissibility plus archive-root ledger update | `OPEN` |
| `RT-006` | failed verifier lane | runtime or contract verification fails | validation queue plus verifier artifact | verifier passes on rerun | block new expansion on that family until resolved | `ACTIVE-WHEN-TRIGGERED` |

## Routing Law

1. Blocked or failed loops must become repair tickets, not polished summaries.
2. Failed verifier tickets route through `VALIDATION_QUEUE.md` before new expansion work.
3. A repair ticket closes only when its blocker or failure state changes in cited witness surfaces.
