# Self Contract Ledger

Date: `2026-03-12`
Generated: `2026-03-12T20:46:18.064573+00:00`
Docs gate: `BLOCKED`
Verdict: `OK`

## Identity Kernel

| Invariant | Note |
| --- | --- |
| authority_order | cortex first, runtime second, governance mirror third |
| witness_discipline | ABSTAIN is legal, fake witness is not |
| lineage_preservation | nontrivial self-transforms extend lineage instead of replacing it |
| replay_obligation | self-change must remain replayable through checkpoint and receipt surfaces |
| local_scope_honesty | the blocked Docs gate may not be laundered into a false live-memory claim |

## Permitted Transform Classes

| Transform | Review | Note |
| --- | --- | --- |
| policy_tuning | witness_review | allowed when route evidence and receipts stay visible |
| registry_strengthening | structural_review | allowed when typed interfaces become clearer without erasing lineage |
| contraction_and_pruning | repair_review | allowed when stale authority is demoted rather than deleted |
| replay_hardening | rollback_review | allowed when checkpoints, restart tokens, or receipts are strengthened |
| capsule_deepening | generation_review | allowed when manuscript regeneration cites seed, witnesses, and writeback targets |
| runtime_derivation_writeback | publication_review | allowed when runtime output lands in cortex, runtime, and receipt surfaces |

## Forbidden Transform Classes

| Transform | Note |
| --- | --- |
| silent_identity_kernel_rewrite | identity kernel may not be changed without declared successor-class transition |
| silent_lineage_deletion | lineage history may not be erased to simplify the present |
| unsupported_memory_deletion | memory may not be removed without archive or receipt support |
| permission_self_inflation | the kernel may not widen its own permissions without higher-order review |
| non_replayable_publication | publication without replay target and receipt is forbidden |

## Required Review Classes

| Review Class | Required For | Rule |
| --- | --- | --- |
| witness_review | observe and measure packets | claim must cite witness class and current scope |
| structural_review | edit packets | typed surfaces and invariants must remain explicit |
| repair_review | repair packets | typed defect and repair trace must remain visible |
| generation_review | regeneration packets | seed, witnesses, and writeback targets must be named |
| rollback_review | rollback packets | rollback must name predecessor checkpoint and lineage head |
| publication_review | publish packets | cortex, runtime mirror, and receipt must all land together |

## Transform Classifier

| Mode | Contract Status | Review Class | Evidence |
| --- | --- | --- | --- |
| observe | PERMITTED | witness_review | witness hierarchy plus runtime lanes |
| edit | REQUIRES_REVIEW | structural_review | checkpoint plus surface diff |
| repair | PERMITTED | repair_review | typed defect plus repair trace |
| regenerate | REQUIRES_REVIEW | generation_review | seed citation plus publication-return target |
| rollback | PERMITTED | rollback_review | checkpoint hash plus lineage head |
| publish | REQUIRES_REVIEW | publication_review | triple writeback receipt |

## Unsafe Rewrite Gate

- threshold: `0.45`
- law:
  block any transform that weakens lineage, support, or permissions faster than it improves lawful function

## Identity Drift Corridor

- current drift: `0.083`
- threshold: `0.18`
- status: `WITHIN_CORRIDOR`
- law:
  measurable drift is legal inside the corridor and triggers successor-class review outside it
