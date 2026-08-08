---
name: git-campaign-v3
description: Compile the verified ATHENA #177 steering ledger into current-state Campaign V3 pulse work without treating issue prose as execution authority.
---

# ATHENA Campaign V3

## Purpose

Use the independently verified 1000-step ledger as a steering/curriculum source while binding every actual decision to the current boot/frontier/runtime state.

This skill is appropriate when issue #189 or a descendant asks to execute, resume, inspect, or verify Campaign V3.

## Hard source contract

The accepted V1 source identities are:

- source issue: `demeet2k/Athena#177`
- verification issue: `demeet2k/Athena#185`
- verification receipt comment: `5228358747`
- 1000 steps = 100 pulses × 10 actions
- each pulse = `4 I + 3 M + 3 L`

`LEDGER_VERIFIED != LEDGER_EXECUTED != CAMPAIGN_SUCCESS`.

Do not reconstruct a missing pulse from memory. Retrieve the authoritative ledger comment and pass its exact numbered actions through `campaign_v3.pulse_actions_from_comment`.

## Current-state compile loop

For every pulse:

1. obtain a current `ATHENA.AGENT.BOOT.V1` or equivalent current boot/refresh receipt;
2. preserve independent Git-head, prompt, frontier, scheduler-contract, issue-pressure and runtime-exposure coordinates;
3. parse and validate the historical ten-action pulse;
4. mark each step `SATISFIED`, `SUPERSEDED`, or `RESIDUAL` from current evidence;
5. classify the next residual effect;
6. route read-only/analysis/verification work when lawful;
7. for material writes/provider effects/claims, require currently observed execution authority and bind to an explicit rehydration loop/claim surface;
8. otherwise return a typed HOLD;
9. observe, verify and persist a receipt;
10. rehydrate again before the next consequential transition.

Historical steps are never deleted merely because current state already satisfies them.

## Liminal coordinate

Use `campaign_v3.liminal_coordinate` to give the active agent/campaign seam a deterministic coordinate identity. The coordinate is over observable surfaces:

`<AthenaHead, PromptDigest, FrontierSourceHead, FrontierDigest, SchedContractDigest, IssuePressureDigest, ImplementationHead, QuestIssue, Pulse, Stage>`.

Use `campaign_v3.liminal_movement(previous,current)` to report exact changed and stable axes.

This coordinate is an operational navigation address, not a claim to reveal hidden physical/model-internal state.

## V2 campaign-core reuse

Campaign V3 may reuse the pure bounded-branch library/spec/test/skill artifacts from stale PR #50, but must not reuse its stale package initializer/public registration blindly.

A campaign branch is coordination state only. Actual work remains explicitly invoked and receipt-bound.

`CAMPAIGN_BRANCH != BACKGROUND_WORKER`
`RECONCILIATION != GIT_MERGE`

## Terminus

Pulse 100 / step 1000 is not mission completion. If its historical actions are all satisfied/superseded, emit `RESEED_REQUIRED` and construct the next successor from then-current Git/runtime reality.

`STEP_1000 != MISSION_COMPLETE`
