# TSE Self-Tightening Knot Apply V1

Artifact: `ATHENA.TSE.SELF.TIGHTENING.KNOT.APPLY.V1`  
Status: candidate observation mechanism  
Merge authority: none  
Execution authority: none  
Behavioral treatment effect: `UNKNOWN`

## 1. Purpose

The public TSE continuation stack deliberately distinguishes a verified child Return from adoption into the parent. A verified child result is not proof that the shared parent frontier contains that result.

```text
CHILD_VERIFIED_RETURN != SHARED_ADOPTION
RETURN_READY != RETURN_APPLIED
```

This layer closes the operational Self-Tightening Knot only by observing an **already completed shared Git adoption**. It does not perform the merge.

## 2. Operational knot

Let:

- `P` = frozen parent commit bound by the original Hatch;
- `C` = child commit bound by the exact SOURCE_BOUND `CHILD_VERIFIED_RETURN`;
- `A` = applied commit that is the freshly verified shared local+remote frontier.

The knot is observable iff:

```text
P <= A
C <= A
A == local HEAD == verified remote HEAD
```

where `<=` is Git ancestry.

The applied frontier may be a fast-forward or merge descendant. Content similarity, declaration, or route digest alone is insufficient.

## 3. Authority boundary

TSE Apply V1 never runs merge, rebase, cherry-pick, push, or force-update operations.

```text
KNOT_OBSERVATION != MERGE_AUTHORITY
TSE_TELEMETRY != GIT_WRITE_AUTHORITY
GIT_ANCESTRY_PROOF != CAUSAL_PERFORMANCE_PROOF
```

External repository/PR/maintainer machinery performs adoption; this surface verifies the public result.

## 4. Existing Helix ABI

No second top-level apply tool is introduced. Existing `athena_tse_helix_advance` accepts `operation=APPLY`.

For APPLY:

- `parent_event_id` = exact SOURCE_BOUND `CHILD_VERIFIED_RETURN` event;
- `route` = exact validated population route including child claim binding;
- `child_return` carries:

```text
{
  hatch: <original validated Hatch>,
  apply_receipt: {
    schema_version: ATHENA.TSE.KNOT.APPLY.RECEIPT.V1,
    apply_id,
    mode: ANCESTRY_ADOPTION,
    parent_head,
    child_head,
    applied_head,
    apply_witnesses: [...],
    platform_counter_reset_claimed: false
  }
}
```

## 5. Parent coordinate

The original Hatch must pass all existing digest checks and must match route `hatch_id`, `hatch_digest`, and `parent_checkpoint_digest`.

Frozen parent Git position is read from:

1. `hatch.parent_git_position`, or
2. `hatch.parent_checkpoint.git_position`.

The receipt's `parent_head` must equal that frozen position exactly.

## 6. Child coordinate

The child event must satisfy all of:

```text
transition = CHILD_VERIFIED_RETURN
source.verification = SOURCE_BOUND
source.kind = TSE_RETURN_CHECK
mission_id = current mission
route_id = current route
hatch_id = current hatch
child_agent_id = route.child_claim.agent_id
child_claim_id = route.child_claim.claim_id
verified_delta > 0
source.git_head = apply_receipt.child_head
```

The apply observer inherits the already-verified delta; it does not mint or revise child value.

## 7. Shared frontier gate

For a new application observation:

1. Git must be enabled;
2. worktree must be clean;
3. shared remote sync must succeed;
4. `shared_frontier_verified=true`;
5. local HEAD equals `applied_head`;
6. remote HEAD equals `applied_head`;
7. P, C and A resolve to commits;
8. P is ancestor of A;
9. C is ancestor of A;
10. C is not already contained in frozen P.

Any failure returns a typed HOLD. No conflict repair is attempted.

## 8. Source-bound RETURN_APPLIED

After all gates pass, append exactly one SOURCE_BOUND event:

```text
transition = RETURN_APPLIED
source.kind = TSE_SHARED_GIT_ADOPTION
source.ref = apply_id
source.git_head = applied_head
source.authority = FRESH_SHARED_GIT_ANCESTRY_ADOPTION
parent_event_id = exact CHILD_VERIFIED_RETURN event
verified_delta = inherited child verified delta
```

This is the first lawful public source for Helix stage S7.

## 9. Self-tightening output

A successful observation returns:

```text
status = TSE_KNOT_APPLY_OBSERVED
knot_status = TIGHTENED_SHARED_GIT
parent_head = P
child_head = C
applied_head = A
return_applied_event_id = E7
next_parent_git_position.head = A
merge_authority = false
execution_authority = false
```

`next_parent_git_position` is a continuation coordinate for the next cycle, not authorization to write.

## 10. Idempotency and stale semantics

An exact already-recorded apply may be replayed after telemetry has advanced HEAD. That replay is historical idempotency only:

```text
IDEMPOTENT_REPLAY != CURRENT_FRONTIER_ASSERTION
```

A new apply ID referring to an old applied head must pass the current shared-frontier gate and therefore fails stale once the frontier has advanced.

Changed semantic content under the same apply ID is a conflict HOLD.

## 11. Route-window consequence

Before S7 source exists:

```text
S6 > 0
APPLY observation incomplete
=> eta_apply = UNKNOWN
```

After source-bound S7:

```text
S6 -> S7 is observed for that route
```

Thus application conversion becomes measurable without treating absence as zero.

## 12. Firewalls

```text
RETURN_READY != RETURN_APPLIED
CHILD_VERIFIED_RETURN != SHARED_ADOPTION
LOCAL_COMMIT != SHARED_RETURN
KNOT_OBSERVATION != MERGE_AUTHORITY
GIT_ANCESTRY_PROOF != CAUSAL_PERFORMANCE_PROOF
RESEED != PLATFORM_TOKEN_CONTEXT_QUOTA_USAGE_RESET
MECHANISM_PASS != PERFORMANCE_GAIN
```

## 13. Qualification

Mechanism tests must include:

- real divergent child commit and real shared merge;
- source-bound S6 -> source-bound S7;
- exact replay after telemetry moves HEAD;
- changed-same-apply-ID conflict;
- stale new apply ID after frontier advancement;
- applied head without child ancestry;
- wrong parent binding;
- reset claim fail-closed;
- no merge/execution authority in outputs.

Even complete mechanism qualification leaves:

```text
FIELD_PERFORMANCE = UNKNOWN
BEHAVIORAL_TREATMENT_EFFECT = UNKNOWN
CANONICAL_PROMOTION = HOLD
```

until matched field observations justify a stronger claim.
