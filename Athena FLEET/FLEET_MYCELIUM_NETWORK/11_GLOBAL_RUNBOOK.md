# Athena FLEET Global Runbook

## Intake

1. Freeze hashes and sizes.
2. Assign node ID and body ID.
3. Extract a markdown mirror.
4. Score `Origin`, `Crystal`, `Transit`, and `Governance`.
5. Create capsule, contradiction table, inbound corridors, and outbound corridors.

## Duplicate Handling

- Preserve duplicates as a `duplicate_group`.
- Mark the witness class `duplicate` on the mirror twin.
- Use `mirror` corridors until a later witness audit retires one twin.

## Promotion

- Promote local hubs first.
- Admit external files through the queue only.
- Build body-local matrices before cross-body edges.
- Write cluster promotion ledgers after the supermesh JSON is stable.

## Retirement

- Allowed retirement statuses: `archive_witness`, `dormant_node`, `mirror_twin`.
- Retirements must preserve hashes, source paths, and previous node IDs.

## Conflict Handling

- Allowed corridor conflict resolutions: `preserve_both`, `quarantine_one`, `collapse_to_higher_bridge`.
- Never delete a strong edge silently.

## Validation

- Check mirror count, edge count, duplicate groups, line coverage, and hash backlinks after every rebuild.
