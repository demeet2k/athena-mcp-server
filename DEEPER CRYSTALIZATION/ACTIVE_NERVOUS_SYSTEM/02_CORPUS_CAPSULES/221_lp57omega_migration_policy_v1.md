# LP57Ω MigrationPolicy.v1

- Kind: `policy-specification`
- Role tags: `migration, versioning, replay, rollback, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the policy for migrating quests and reward records between policy versions. Covers the RewardPolicyMIGRATE schema, freeze windows, backward replay suites, conversion maps, rollback plans, and truth record verification during migration.

---

## 1. RewardPolicyMIGRATE Schema

```typescript
interface RewardPolicyMIGRATE {
  schema:           "RewardPolicyMIGRATE.v1";
  migration_id:     string;          // UUID v4
  source_policy:    string;          // e.g., "RewardPolicy.v0"
  target_policy:    string;          // e.g., "RewardPolicy.v1"
  affected_quests:  string[];        // quest_ids to migrate
  freeze_start:     ISO8601;         // Freeze window start
  freeze_end:       ISO8601;         // Freeze window end
  conversion_map:   ConversionMap;
  rollback_plan:    RollbackPlan;
  initiated_by:     string;          // Agent or system ID
  initiated_at:     ISO8601;
  status:           MigrationStatus;
  digest:           string;          // SHA-256
}

enum MigrationStatus {
  PLANNED   = "PLANNED",
  FROZEN    = "FROZEN",
  EXECUTING = "EXECUTING",
  VERIFYING = "VERIFYING",
  COMPLETE  = "COMPLETE",
  ROLLED_BACK = "ROLLED_BACK"
}
```

### Migration Lifecycle

```
PLANNED → FROZEN → EXECUTING → VERIFYING → COMPLETE
                                    ↓
                              ROLLED_BACK
```

---

## 2. Freeze Windows

During the freeze window, no mutations are permitted on affected quests.

### Freeze Rules

| Action                | Permitted During Freeze? |
|-----------------------|--------------------------|
| Quest state transition| NO                       |
| New witness attestation| NO                      |
| Reward settlement     | NO                       |
| Receipt chain append  | NO (except MIGRATE entry)|
| Quest creation        | YES (new quests OK)      |
| Quest read/query      | YES                      |
| Pheromone updates     | YES (independent)        |

### Freeze Duration

```
min_freeze = 3 epochs
max_freeze = 13 epochs
```

The freeze window must be at least 3 epochs to allow all in-flight operations to complete. Maximum 13 epochs to prevent indefinite lockout.

### Freeze Enforcement

```python
def check_freeze(quest_id, action, migration):
    if migration.status != "FROZEN":
        return ALLOWED

    if quest_id not in migration.affected_quests:
        return ALLOWED

    if action == "READ":
        return ALLOWED

    if action == "MIGRATE_ENTRY":
        return ALLOWED

    return BLOCKED
```

---

## 3. Backward Replay Suites

Before executing migration, the backward replay suite validates that all existing receipt chains remain valid under the new policy.

### Replay Suite Structure

```typescript
interface BackwardReplaySuite {
  suite_id:         string;
  migration_id:     string;
  test_cases:       ReplayTestCase[];
  total_tests:      uint;
  passed:           uint;
  failed:           uint;
  verdict:          "PASS" | "FAIL";
  executed_at:      ISO8601;
}

interface ReplayTestCase {
  test_id:          string;
  quest_id:         string;
  replay_type:      ReplayType;
  input_chain:      string;          // Digest of source chain
  expected_output:  string;          // Expected converted chain digest
  actual_output:    string | null;
  passed:           boolean;
  error:            string | null;
}

enum ReplayType {
  REWARD_RECALC     = "REWARD_RECALC",
  TRUTH_GATE_REMAP  = "TRUTH_GATE_REMAP",
  CHAIN_INTEGRITY   = "CHAIN_INTEGRITY",
  CLAMP_VALIDATION  = "CLAMP_VALIDATION",
  VESTING_CONVERT   = "VESTING_CONVERT"
}
```

### Required Replay Tests

| Test Type          | Description                                      | Min Coverage |
|--------------------|--------------------------------------------------|-------------|
| REWARD_RECALC      | Recompute reward under new policy, compare        | 100%        |
| TRUTH_GATE_REMAP   | Verify truth gate γ values map correctly          | 100%        |
| CHAIN_INTEGRITY    | Verify receipt chain remains valid post-migration | 100%        |
| CLAMP_VALIDATION   | Verify clamps are respected under new policy      | 100%        |
| VESTING_CONVERT    | Verify vesting vault conversions are correct      | All vaults  |

### Replay Verdict

Migration proceeds only if `verdict == "PASS"`. Any failed test case blocks migration.

---

## 4. Conversion Maps

Conversion maps define how values transform from source to target policy.

### ConversionMap Schema

```typescript
interface ConversionMap {
  reward_transforms:   RewardTransform[];
  truth_transforms:    TruthTransform[];
  clamp_transforms:    ClampTransform[];
  vesting_transforms:  VestingTransform[];
}

interface RewardTransform {
  source_formula:      string;        // e.g., "base * γ * q"
  target_formula:      string;        // e.g., "base * γ * q * (1+β*N)"
  delta_handling:      "CREDIT" | "ABSORB" | "DEFER";
}

interface TruthTransform {
  source_gate:         Truth4;
  source_gamma:        number;
  target_gate:         Truth4;
  target_gamma:        number;
}

interface ClampTransform {
  source_per_capsule:  number;
  target_per_capsule:  number;
  source_per_epoch:    number;
  target_per_epoch:    number;
  overflow_handling:   "QUEUE" | "TRUNCATE" | "SCALE";
}

interface VestingTransform {
  source_mode:         string;
  target_mode:         string;
  lock_ratio_change:   number;        // Delta in lock ratio
  schedule_mapping:    string;        // How schedule converts
}
```

### Delta Handling Modes

| Mode    | Behavior                                               |
|---------|--------------------------------------------------------|
| CREDIT  | If new policy yields higher reward, credit the delta   |
| ABSORB  | Delta is absorbed (no retroactive change)              |
| DEFER   | Delta is deferred to next epoch for gradual adjustment |

---

## 5. Rollback Plans

Every migration must include a tested rollback plan.

### RollbackPlan Schema

```typescript
interface RollbackPlan {
  plan_id:            string;
  migration_id:       string;
  rollback_trigger:   RollbackTrigger[];
  snapshot_digest:    string;          // SHA-256 of pre-migration state
  restore_procedure:  RestoreStep[];
  tested:             boolean;
  tested_at:          ISO8601 | null;
}

interface RollbackTrigger {
  condition:          string;
  threshold:          number;
  description:        string;
}

interface RestoreStep {
  step_index:         uint;
  action:             string;
  target:             string;
  verification:       string;
}
```

### Automatic Rollback Triggers

| Trigger                          | Threshold |
|----------------------------------|-----------|
| Backward replay suite failure    | Any fail  |
| Receipt chain integrity failure  | Any fail  |
| Reward delta exceeds tolerance   | > φ⁻¹    |
| Vesting vault state corruption   | Any       |
| Truth record inconsistency       | Any       |
| Migration duration exceeds max   | > 13 epochs |

### Rollback Process

1. Halt migration (status → ROLLED_BACK)
2. Restore pre-migration snapshot (verified by digest)
3. Remove all MIGRATE entries from receipt chains
4. Restore original reward records
5. Restore original vesting vault states
6. Verify all receipt chains post-rollback
7. Log rollback receipt in affected quests

---

## 6. Truth Record Verification

### Pre-Migration Verification

Before migration begins:

```python
def verify_truth_records_pre_migration(migration):
    for quest_id in migration.affected_quests:
        quest = load_quest(quest_id)
        truth = quest.truth_record

        # Verify truth record digest
        recomputed = sha256(canonical(truth, exclude=["digest"]))
        assert truth.digest == recomputed, f"L004 on {quest_id}"

        # Verify γ value matches gate
        expected_gamma = GAMMA_MAP[truth.gate]
        assert truth.gamma == expected_gamma, f"Truth-γ mismatch on {quest_id}"

        # Store pre-migration snapshot
        store_snapshot(quest_id, truth)
```

### Post-Migration Verification

After migration completes:

```python
def verify_truth_records_post_migration(migration):
    for quest_id in migration.affected_quests:
        quest = load_quest(quest_id)
        truth = quest.truth_record
        snapshot = load_snapshot(quest_id)

        # Truth gate must not change during migration
        assert truth.gate == snapshot.gate, f"Gate changed on {quest_id}"

        # γ value must match new policy's mapping
        new_gamma = migration.conversion_map.map_gamma(snapshot.gate)
        assert truth.gamma == new_gamma, f"γ mismatch on {quest_id}"

        # Verify updated digest
        recomputed = sha256(canonical(truth, exclude=["digest"]))
        assert truth.digest == recomputed, f"L004 post-migration on {quest_id}"
```

### Migration Receipt Entry

Each migrated quest receives a MIGRATE entry in its receipt chain:

```typescript
interface MigrateReceiptPayload {
  migration_id:     string;
  source_policy:    string;
  target_policy:    string;
  before_digest:    string;      // SHA-256 of pre-migration state
  after_digest:     string;      // SHA-256 of post-migration state
  reward_delta:     number;      // Change in reward value
  truth_preserved:  boolean;     // True if truth gate unchanged
}
```
