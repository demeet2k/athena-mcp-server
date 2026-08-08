# Campaign V3 Life Dispatch V1 — development receipt

Parent pressure: `demeet2k/Athena#278`  
Runtime base: `demeet2k/athena-mcp-server@28b1e0dfe96d5bb2af84a66dcd36608a9d8de493`  
Branch: `agent/campaign-v3-life-dispatch-v1-r2`

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

## Hardened reseed continuity

The merged parent now treats a reseed anchor as a consumable continuation capability rather than a reusable token. The adapter therefore also enforces:

- `agent_coordinate_name == agent_id`;
- `target_versions[quest_id] == quest_version`;
- every anchor Git coordinate must still match the supplied current Git position at failed-play resolution;
- a successfully used anchor digest is persisted in `consumed_reseed_anchor_digests`;
- replay, stale head/tree, missing current position, or subject mismatch cannot reseed.

A real `FAIL_CLEAR` still burns exactly one life before these continuation checks, matching the parent ordering.

## Reset boundary

`AUTO_RESEED_GLOBAL_EXTRA_LIFE` resets only ATHENA logical `global_game_age` and registered `local_loop_age` counters while incrementing the logical epoch. It never claims to reset model/product/provider token, context, quota, wall-time, Work usage, or hidden runtime counters.

## Source pin

Life semantics are explicitly pinned to the exact candidate source already tested under #278:

```text
repo = demeet2k/Athena
head = 60a7bc798412088977d7ab9adf16a0e7dca3a1c9
scripts/life_loop_v1.py blob = c6f35cf39d9f25333ee0c748b5e4bacedbb544a1
standing = MERGED_HARDENED_EXACT_SOURCE_TESTED
```

The pin is provenance to the hardened merged parent. Runtime integration promotion remains independently gated.

## Pre-push observation

After the parent Life Loop was hardened and merged on `Athena/main`, the adapter was recompiled against the new source identity. The repaired local harness passes 23/23 checks, adding anchor subject binding, replay rejection, exact current Git-position freshness, and missing/stale-position negative controls. Repository CI on the repaired PR head remains required before upgrading this receipt.
