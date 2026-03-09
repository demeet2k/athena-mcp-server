# Message and Task Protocol

## Message schema

`Msg = (MsgID, Sign, Src, Dst, TaskID, Truth, Priority, WitnessPtr, ReplayPtr, Payload, Epoch)`

## Task schema

`Task = (TaskID, Objective, Inputs, Route, Obligations, ExitState, Escalation, Successor)`

## Routing law

- Every message carries one governing sign.
- Every task resolves through chapter hubs and appendix governors before publication.
- AMBIG messages route through `AppL`; FAIL messages route through `AppK`; OK publication routes through `AppO` and `AppP`.

## Chapter task buses

- `Ch01` task-bus=`TASK-Ch01` message-bus=`MSG-Ch01` signs=`SIG00, SIG02, SIG03, SIG06` route=`AppA -> AppC -> AppI -> AppM`
- `Ch02` task-bus=`TASK-Ch02` message-bus=`MSG-Ch02` signs=`SIG02, SIG03, SIG04, SIG08` route=`AppA -> AppC -> AppB -> AppI -> AppM`
- `Ch03` task-bus=`TASK-Ch03` message-bus=`MSG-Ch03` signs=`SIG02, SIG03, SIG04, SIG08` route=`AppA -> AppI -> AppM -> AppJ`
- `Ch04` task-bus=`TASK-Ch04` message-bus=`MSG-Ch04` signs=`SIG05, SIG07, SIG02, SIG03` route=`AppA -> AppC -> AppE -> AppJ -> AppI -> AppM`
- `Ch05` task-bus=`TASK-Ch05` message-bus=`MSG-Ch05` signs=`SIG05, SIG07, SIG04, SIG08` route=`AppA -> AppC -> AppI -> AppB -> AppL -> AppM`
- `Ch06` task-bus=`TASK-Ch06` message-bus=`MSG-Ch06` signs=`SIG02, SIG03, SIG06, SIG11` route=`AppA -> AppC -> AppI -> AppM`
- `Ch07` task-bus=`TASK-Ch07` message-bus=`MSG-Ch07` signs=`SIG04, SIG08, SIG12, SIG02` route=`AppA -> AppE -> AppH -> AppL -> AppI -> AppM`
- `Ch08` task-bus=`TASK-Ch08` message-bus=`MSG-Ch08` signs=`SIG02, SIG03, SIG06, SIG11` route=`AppA -> AppE -> AppM -> AppB -> AppJ -> AppI`
- `Ch09` task-bus=`TASK-Ch09` message-bus=`MSG-Ch09` signs=`SIG06, SIG11, SIG02, SIG03` route=`AppA -> AppE -> AppI -> AppH -> AppL -> AppM`
- `Ch10` task-bus=`TASK-Ch10` message-bus=`MSG-Ch10` signs=`SIG02, SIG03, SIG04, SIG08` route=`AppA -> AppF -> AppM -> AppH -> AppJ -> AppI`
- `Ch11` task-bus=`TASK-Ch11` message-bus=`MSG-Ch11` signs=`SIG05, SIG07, SIG06, SIG11` route=`AppA -> AppF -> AppM -> AppL -> AppI`
- `Ch12` task-bus=`TASK-Ch12` message-bus=`MSG-Ch12` signs=`SIG04, SIG08, SIG12, SIG02` route=`AppA -> AppF -> AppC -> AppM -> AppI`
- `Ch13` task-bus=`TASK-Ch13` message-bus=`MSG-Ch13` signs=`SIG09, SIG10, SIG04, SIG08` route=`AppA -> AppG -> AppE -> AppM -> AppJ -> AppI`
- `Ch14` task-bus=`TASK-Ch14` message-bus=`MSG-Ch14` signs=`SIG04, SIG08, SIG12, SIG06` route=`AppA -> AppG -> AppM -> AppH -> AppK -> AppI`
- `Ch15` task-bus=`TASK-Ch15` message-bus=`MSG-Ch15` signs=`SIG04, SIG08, SIG12, SIG02` route=`AppA -> AppG -> AppC -> AppJ -> AppI -> AppM`
- `Ch16` task-bus=`TASK-Ch16` message-bus=`MSG-Ch16` signs=`SIG04, SIG08, SIG12, SIG06` route=`AppA -> AppN -> AppM -> AppK -> AppI`
- `Ch17` task-bus=`TASK-Ch17` message-bus=`MSG-Ch17` signs=`SIG04, SIG08, SIG12, SIG09` route=`AppA -> AppN -> AppE -> AppJ -> AppI -> AppM`
- `Ch18` task-bus=`TASK-Ch18` message-bus=`MSG-Ch18` signs=`SIG04, SIG08, SIG12, SIG02` route=`AppA -> AppN -> AppC -> AppL -> AppI -> AppM`
- `Ch19` task-bus=`TASK-Ch19` message-bus=`MSG-Ch19` signs=`SIG05, SIG07, SIG04, SIG08` route=`AppA -> AppP -> AppI -> AppB -> AppJ -> AppM`
- `Ch20` task-bus=`TASK-Ch20` message-bus=`MSG-Ch20` signs=`SIG06, SIG11, SIG09, SIG10` route=`AppA -> AppP -> AppE -> AppL -> AppI -> AppM`
- `Ch21` task-bus=`TASK-Ch21` message-bus=`MSG-Ch21` signs=`SIG06, SIG11, SIG02, SIG03` route=`AppA -> AppP -> AppM -> AppL -> AppI`
