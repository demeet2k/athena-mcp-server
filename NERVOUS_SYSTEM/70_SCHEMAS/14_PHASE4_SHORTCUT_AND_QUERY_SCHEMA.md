# Phase 4 Shortcut And Query Schema

## Shortcuts

| ID | Name | Trigger | Stop | Output |
| --- | --- | --- | --- | --- |
| SC-01 | WitnessFirst | direct support exists | ABSTAIN | ranked witnesses |
| SC-02 | LoadBearingNearest | load-bearing neighbor exists | REPAIR | nearest bridge |
| SC-03 | ChargeThenVerify | objective has affective or epistemic bias | ABSTAIN | top-k wave slice |
| SC-04 | BoundaryBeforeLift | immune-risk or contradiction signal detected | QUARANTINE | contained route |
| SC-05 | GrandCentralBridge | cross-body transfer needed | REPAIR | station route |
| SC-06 | HemisphereRebalance | left or right bias overload detected | REPAIR | rebalanced route |
| SC-07 | SymmetryJump | pair family overfit detected | REPAIR | neighbor pair |
| SC-08 | NeglectScout | gap scan requested | REPAIR | neglect ranking |
| SC-09 | RepairLoop | surface can heal locally | REPAIR | repair receipt |
| SC-10 | OneEighthLift | candidate weave exceeds minimal useful lift | ABSTAIN | thin lift candidate |
| SC-11 | AppendixSupportJump | appendix support needed | REPAIR | appendix support bundle |
| SC-12 | AtlasBackfill | context is missing or stale | ABSTAIN | backfilled context |
| SC-13 | ReplayClose | query or wave finished | REPAIR | replay receipt |

## Query Modes

| ID | Mode | Shortcuts | Stop rule |
| --- | --- | --- | --- |
| Q-LOCATE | locate | SC-01, SC-02, SC-11, SC-12, SC-13 | ABSTAIN when no witnessed surface can be found |
| Q-ROUTE | route | SC-01, SC-02, SC-04, SC-05, SC-06, SC-13 | QUARANTINE on immune risk, otherwise REPAIR or PROMOTE |
| Q-NEGLECT | neglect | SC-01, SC-08, SC-09, SC-10, SC-12, SC-13 | REPAIR when neglected surfaces exist |
| Q-FIRE | fire | SC-03, SC-04, SC-05, SC-06, SC-10, SC-11, SC-13 | TopK wave slices only |
| Q-PROMOTE | promote | SC-01, SC-04, SC-05, SC-09, SC-10, SC-13 | PROMOTE only when witness, replay, and boundary clear floor |
