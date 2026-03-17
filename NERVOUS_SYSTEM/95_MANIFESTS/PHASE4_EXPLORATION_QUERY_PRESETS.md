# Phase 4 Exploration Query Presets

| ID | Mode | Scope | Shortcuts | Writeback |
| --- | --- | --- | --- | --- |
| Q-LOCATE | locate | live_19_body_organism + K01-K16 + active nodes | SC-01, SC-02, SC-11, SC-12, SC-13 | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\29_PHASE4_REPLAY_RECEIPT_LEDGER.md |
| Q-ROUTE | route | Grand Central graph | SC-01, SC-02, SC-04, SC-05, SC-06, SC-13 | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\29_PHASE4_REPLAY_RECEIPT_LEDGER.md |
| Q-NEGLECT | neglect | body + pair gap field | SC-01, SC-08, SC-09, SC-10, SC-12, SC-13 | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\27_PHASE4_NEGLECT_SIGNAL_LEDGER.md |
| Q-FIRE | fire | pair registry with sparse wave materialization | SC-03, SC-04, SC-05, SC-06, SC-10, SC-11, SC-13 | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\29_PHASE4_REPLAY_RECEIPT_LEDGER.md |
| Q-PROMOTE | promote | validated weave candidates | SC-01, SC-04, SC-05, SC-09, SC-10, SC-13 | C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\28_PHASE4_WEAVE_CANDIDATE_LEDGER.md |

## Runtime

```powershell
python -m self_actualize.runtime.query_phase4_structured_neuron_storage locate "Grand Central Station"
python -m self_actualize.runtime.query_phase4_structured_neuron_storage route --source "Athena FLEET" --target "Ch11 The Helical Manifestation Engine"
python -m self_actualize.runtime.query_phase4_structured_neuron_storage neglect --limit 6
```
