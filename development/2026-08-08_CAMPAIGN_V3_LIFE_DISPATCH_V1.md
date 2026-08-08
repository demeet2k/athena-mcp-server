# Campaign V3 Life Dispatch V1 — development receipt

Parent pressure: `demeet2k/Athena#278`  
Runtime base: `demeet2k/athena-mcp-server@e1e8d595b4f05f41dcbeafbc6964f1496adae599`  
Branch: `agent/campaign-v3-life-dispatch-v1`

## Delta

This slice binds the already-tested `STAY_IN_GAME_LIFE_LOOP_V1` candidate into the existing Campaign V3 coordination/rehydration membrane instead of creating another scheduler.

The adapter freezes four inputs at binding time:

- `LIFE_POLICY=STAY_IN_GAME_LIFE_LOOP_V1`
- ordered `CLEAR_CONDITION_DIGEST`
- renewable `RESEED_ANCHOR`
- explicit `EXTRA_LIFE_REWARD_ELIGIBILITY`

It calls the existing `bind_current_pulse_branch_to_loop` transaction unchanged. Life state is created only after Campaign V3 returns `BOUND`; the resulting receipt still says `execution_authority_granted=false` and `work_executed=false`.

## GTC membrane

The Game Time Controller objective is verified useful continuation, not elapsed runtime. Therefore a life is never burned merely because a legitimate GTC terminal/hold condition appears.

```text
SUCCESS_CLOSED | NO_POSITIVE_FRONTIER | PREMATURE_MODEL_STOP -> 0 life
AUTHORITY_HOLD | EVIDENCE_HOLD | STALE_STATE_HOLD | CAPABILITY_HOLD
| HUMAN_VALUE_CHOICE | BUDGET_EXHAUSTED | META_OVERHEAD_COLLAPSE
| DUPLICATION_COLLAPSE -> 0 life

only:
observed + executed + witnessed + failed hard gate/clear condition
+ coherent completion class -> FAIL_CLEAR -> exactly 1 life
```

Contradictory/unobserved/unplayed/unwitnessed receipts fail closed without life consumption.

## Reset boundary

`AUTO_RESEED_GLOBAL_EXTRA_LIFE` resets only ATHENA logical `global_game_age` and registered `local_loop_age` counters while incrementing the logical epoch. It never claims to reset model/product/provider token, context, quota, wall-time, Work usage, or hidden runtime counters.

## Source pin

Life semantics are explicitly pinned to the exact candidate source already tested under #278:

```text
repo = demeet2k/Athena
head = 2fe1ab6f385dcb52ea89c2b6e4f440d59a9b160f
scripts/life_loop_v1.py blob = ea5883d1c046a15ff412a755d02c52479c6d6798
standing = CANDIDATE_EXACT_SOURCE_TESTED
```

The pin is provenance, not canonical promotion.

## Pre-push observation

A local candidate harness over the exact adapter source passed all 18 initial adversarial tests. The repository test file expands this to 19 checks and uses the full `ATHENA.RESEED_ANCHOR.V1` fixture plus a patched existing binder boundary. Repository-readback execution is required before upgrading this receipt.
