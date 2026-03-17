# Knowledge Fabric Dashboard

Date: `2026-03-13`
Generated: `2026-03-13T20:44:37.135414+00:00`
Docs gate: `BLOCKED`
Fabric scope: `federated_canonical_local_corpus_scope`

## Totals

- total records: `16708`
- indexed: `7882`
- archive: `2041`
- physical stubs: `6771`
- generated: `14`
- zones: `12`
- edges: `45658`
- shortcuts: `8`
- packets: `8`

## Validation

- `indexed_records_have_zone`: `True`
- `archive_records_have_zone`: `True`
- `records_have_authority_surface`: `True`
- `records_have_witness_class`: `True`
- `shortcut_filter_order_is_deterministic`: `True`
- `packets_leave_replay_trace`: `True`
- `dual_engine_targets_are_mapped`: `True`
- `blocked_docs_lane_preserved`: `True`
- `media_records_preserved`: `True`
- `cost_reduction_positive`: `True`

## Shortcut Performance

| Packet | Intent | Matches | Reduction Vs Full Scan | Result |
| --- | --- | --- | --- | --- |
| KFP-001 | locate | 8 | 0.9995 | answer |
| KFP-002 | browse | 10 | 0.9994 | answer |
| KFP-003 | compare | 8 | 0.9995 | answer |
| KFP-004 | synthesize | 12 | 0.9993 | answer |
| KFP-005 | audit | 10 | 0.9994 | answer |
| KFP-006 | repair | 0 | 0.9999 | abstain |
| KFP-007 | regenerate | 10 | 0.9994 | answer |
| KFP-008 | publish | 10 | 0.9994 | answer |

## Blocked Lanes

| Lane | Status | Reason |
| --- | --- | --- |
| Google Docs ingress | BLOCKED | Trading Bot/credentials.json and Trading Bot/token.json are still missing |

## Stale Zones

| Zone | Records | Stale | Ambiguous | State |
| --- | --- | --- | --- | --- |
| Cortex | 9700 | 675 | 0 | GOOD |
| ReserveQuarantine | 145 | 126 | 6 | WATCH |

## Ambiguous Zones

| Zone | Records | Stale | Ambiguous | State |
| --- | --- | --- | --- | --- |
| ReserveQuarantine | 145 | 126 | 6 | WATCH |
