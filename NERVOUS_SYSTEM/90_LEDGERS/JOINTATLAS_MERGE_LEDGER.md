# JOINTATLAS MERGE LEDGER

Date: `2026-03-13`
Truth: `OK`

## Ledger Rule

- append only: `True`
- entry ids monotonic: `True`
- terminal decisions require ledger: `True`

## Non-Authoritative Fixture Ledger

| Fixture | Terminal State | Destination | Entry ID | Continuation Seed |
| --- | --- | --- | --- | --- |
| commit_path | DECIDED_COMMIT | COMMIT | MLE-0001 | SEED-commit_path |
| defer_near_path | DECIDED_DEFER_NEAR | DEFER_NEAR | MLE-0002 | SEED-defer_near_path |
| defer_ambig_path | DECIDED_DEFER_AMBIG | DEFER_AMBIG | MLE-0003 | SEED-defer_ambig_path |
| quarantine_path | DECIDED_QUARANTINE | QUARANTINE_FAIL | MLE-0004 | SEED-quarantine_path |
| refuse_path | DECIDED_REFUSE | REFUSE | MLE-0005 | SEED-refuse_path |

## Restart Seed

`MotionConstitution_L1`
