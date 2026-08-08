---
name: git-rehydration-campaign
description: Coordinate several explicit Git rehydration loops as a bounded branch graph, preserving ambiguous successor paths without claiming hidden parallel work or merge authority.
---

# ATHENA Rehydration Campaign V2

Use this skill when a long objective cannot be represented honestly as one linear self-prompt chain—for example when the successor baton contains several tied lawful paths that deserve independent investigation.

## Coordinate

`ATHENA.KC144::GITΩ::REHYDRATION-CAMPAIGN::V2`

## Core composition

A campaign does not replace the V1 loop. Each real branch of work still runs through a normal `ATHENA.REHYDRATION.LOOP.V1` instance.

```text
campaign branch graph
    ├── branch A → V1 loop → observed receipts
    ├── branch B → V1 loop → observed receipts
    └── branch C → V1 loop → observed receipts
                  ↓
           witnessed reconciliation
```

Campaign branches are coordination objects, not background workers.

## Branch lifecycle

```text
OPEN
→ CLAIMED
→ ACTIVE
→ WITNESSED
→ ACCEPTED
```

Alternative paths:

```text
ACTIVE → BLOCKED
WITNESSED/BLOCKED → EXPANDED
WITNESSED/BLOCKED → SUPERSEDED   (explicit only)
CLAIMED → OPEN                   (release)
```

## Successor expansion

A valid V1.1 successor baton may expand a completed/blocked branch:

- `SELECTED` → one child branch;
- `AMBIGUOUS` → one child per retained tie;
- `NO_SUCCESSOR` / `TERMINAL` → no child.

The caller may explicitly provide `selected_candidate_ids` to narrow an ambiguous frontier. The campaign never silently drops tied branches merely to fit a budget.

## Hard branch budgets

Every campaign defines:

```text
max_width
max_depth
max_branches
lease_steps
```

If expansion exceeds a bound, it returns a typed hold without mutating campaign state:

```text
HOLD_WIDTH
HOLD_DEPTH
HOLD_BRANCH_BUDGET
```

This is the anti-explosion membrane.

## Claims and leases

A branch must be claimed before a V1 loop is bound to it.

Claims use the campaign logical clock instead of pretending wall-clock time is universally authoritative:

```text
claimed_clock
lease_until_clock
agent
```

An unexpired claim blocks a competing agent. A lease holder may release a CLAIMED/BLOCKED branch back to OPEN.

`CLAIMED_BRANCH != ACTIVE_WORKER`: a lease is coordination state only. Actual work exists only when an explicitly invoked agent performs the branch's V1 loop cycle.

## Loop binding

`bind_loop` records:

```text
loop_id
loop state digest
loop chain digest
loop checkpoint head
loop step
loop status
```

`sync_branch` projects the bound loop into campaign status:

```text
ACTIVE             → ACTIVE
COMPLETE           → WITNESSED
HOLD_MAX_STEPS     → BLOCKED
HOLD_NO_PROGRESS   → BLOCKED
ABORTED            → BLOCKED
```

It also captures observed completion summary, evidence references, and the branch's latest successor baton.

## Reconciliation

Only `WITNESSED` branches may be accepted.

A reconciliation requires:

```text
observed=true
selected_branch_ids
summary
evidence_refs
```

Supersession is explicit. Only IDs listed in `supersede_branch_ids` may move from `WITNESSED`/`BLOCKED` to `SUPERSEDED`. Unmentioned branches remain untouched. This prevents one local decision from silently erasing an independent exploration branch.

A nonterminal reconciliation enters `RECONCILED`; this means the exploration decision is recorded but does **not** mean code was merged.

A terminal campaign may become `COMPLETE` only when:

- it carries an observed integration witness;
- the witness Git head equals the currently observed Git head;
- no unselected, unsuperseded branch remains in an active frontier state.

```text
RECONCILED != GIT_MERGED
```

## Persistence

```text
prompts/rehydration_campaigns/<campaign_id>/
├── state.json
├── events/<sequence>-<event>.json
└── batons/<sequence>-<digest>.json
```

Every mutation is CAS-guarded against the current campaign checkpoint and extends a state/event hash chain.

## Verification

Campaign verification checks:

- current state digest;
- sequential event chain;
- branch identity and valid states;
- parent/depth consistency, including root depth zero;
- max depth;
- max total branch count;
- active frontier width at every depth;
- event/state tip equality.

`PASS` is causal/topological integrity evidence only. It does not prove that any branch's implementation or scientific claim is correct.

## Current installation stage

V2 is intentionally introduced as an additive runtime library/harness with tests and a machine-readable contract before MCP surface promotion. This prevents the stable V1/V1.1 tool membranes from changing merely because the campaign graph is structurally plausible.

There is also an explicit promotion hold: campaign and sibling-loop coordination commits live in the same Git history as branch work. Before MCP promotion, V1 substantive-work accounting must exclude `prompts/rehydration/**` and `prompts/rehydration_campaigns/**` coordination-only changes so control-plane commits cannot satisfy a work-progress gate by themselves.

## Laws

- `CAMPAIGN_BRANCH != BACKGROUND_WORKER`.
- `AMBIGUITY MAY EXPAND INTO BOUNDED BRANCHES`.
- `WIDTH/DEPTH/BRANCH BUDGETS FAIL CLOSED`.
- `BRANCH_ROUTING != AUTHORITY`.
- `UNMENTIONED BRANCH != SUPERSEDED BRANCH`.
- `RECONCILIATION != GIT_MERGE`.
- `CAMPAIGN COMPLETE REQUIRES OBSERVED INTEGRATION WITNESS`.
- `CAMPAIGN VERIFY != BRANCH WORK TRUTH`.
