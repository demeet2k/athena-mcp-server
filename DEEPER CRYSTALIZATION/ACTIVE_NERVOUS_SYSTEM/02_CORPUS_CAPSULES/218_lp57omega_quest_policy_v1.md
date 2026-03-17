# LP57Ω QuestPolicy.v1

- Kind: `policy-specification`
- Role tags: `quest-lifecycle, dependencies, truth-promotion, vesting, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the quest lifecycle state machine, dependency resolution rules, witness and replay requirements, truth promotion rules, and vesting modes for the LP57Ω quest system.

---

## 1. Quest Lifecycle

### State Machine

```
Draft → Active → Blocked → Active (unblocked)
                    ↓
Active → Sealed → Published → Archived
```

### State Definitions

| State     | Entry Condition                          | Allowed Transitions       |
|-----------|------------------------------------------|---------------------------|
| Draft     | Quest created, not yet claimed           | Active                    |
| Active    | Claimed by agent(s), work in progress    | Blocked, Sealed           |
| Blocked   | Dependency unmet, certification pending, or ZERO truth | Active (resolved) |
| Sealed    | All corridor stations completed, truth gate evaluated | Published        |
| Published | All publish-block checks pass            | Archived                  |
| Archived  | Explicit archive or epoch expiry         | (terminal)                |

### Transition Rules

#### Draft → Active
- At least one agent must claim the quest
- All hard dependencies must be in {Sealed, Published, Archived} state
- Element assignment must be valid for the corridor

#### Active → Blocked
- Any of:
  - Unresolved dependency transitions to Blocked or Draft
  - Certification queue entry (TempleRite class)
  - Truth gate evaluates to ZERO
  - Ethics watchlist flag raised
  - Invariant violation detected

#### Blocked → Active
- All blocking conditions resolved
- If ZERO truth: repair protocol completed
- If certification: certification receipt issued
- Re-entry timestamp recorded

#### Active → Sealed
- All corridor stations traversed
- Truth gate evaluated (OK or NEAR)
- Witness quorum met
- Replay bundle generated (if required)
- Receipt chain valid

#### Sealed → Published
- No active publish-block sets
- ReleaseManifest.v1 generated
- SealedReceiptBundle.v1 finalized
- Bundle digest verified

#### Published → Archived
- Explicit archive request by creator, or
- Epoch expiry: `current_epoch - epoch_published > 57` epochs

---

## 2. Dependency Resolution

### Dependency Types

| Type     | Semantics                                              | Blocks? |
|----------|--------------------------------------------------------|---------|
| BLOCKS   | Target cannot leave Draft until source is Sealed+      | Yes     |
| REQUIRES | Target cannot be Sealed until source is Published+     | Yes     |
| INFORMS  | Advisory only — source provides context, no gate       | No      |

### Resolution Algorithm

```python
def can_transition(quest, target_state):
    for dep in quest.dependencies:
        if dep.dep_type == "BLOCKS" and target_state == "ACTIVE":
            if dep.source.status not in ["SEALED", "PUBLISHED", "ARCHIVED"]:
                return False
        if dep.dep_type == "REQUIRES" and target_state == "SEALED":
            if dep.source.status not in ["PUBLISHED", "ARCHIVED"]:
                return False
    return True
```

### Circular Dependency Prevention

- The dependency graph must be a DAG (directed acyclic graph)
- Cycle detection runs on every dependency addition
- If a cycle is detected, the dependency is rejected with error code DEP_CYCLE

### Dependency Cascade

When a quest transitions to Blocked:
1. Check all quests that depend on it (reverse edges)
2. If any dependent quest has a BLOCKS dependency, cascade block
3. Record cascade chain in receipt log

---

## 3. Witness Requirements

### By Quest Class

| Quest Class  | Min Witnesses | Self-Witness Allowed | Attestation Rule         |
|-------------|--------------|----------------------|--------------------------|
| Solo        | 1            | Yes                  | Self-attestation OK      |
| Community   | 2            | Yes (but not sole)   | Majority OK required     |
| TempleRite  | 2 + certifier| No                   | Unanimous OK or NEAR     |
| Storm       | 1 per coalition| Yes                 | Majority OK required     |

### Witness Validation

1. Each witness must have traversed at least one corridor station of the quest
2. Witness attestation timestamp must fall within the quest's active epoch range
3. A witness cannot attest to the same quest more than once per epoch
4. Witness identity must be distinct (no duplicate agent_ids in WitnessBundle)

---

## 4. Replay Requirements

### By Quest Class

| Quest Class  | Replay Required | Determinism Check | Min Steps |
|-------------|----------------|-------------------|-----------|
| Solo        | No             | N/A               | N/A       |
| Community   | Yes            | Yes               | 2         |
| TempleRite  | Yes            | Yes               | 3         |
| Storm       | Optional       | If provided, yes  | 1         |

### Replay Validation Rules

1. Every replay step must reference a valid corridor station
2. Step input/output hashes must be reproducible for deterministic replays
3. Step ordering must match corridor traversal order
4. Total replay steps must cover all corridor stations in the quest

---

## 5. Truth Promotion Rules

Truth gates can be promoted (upgraded) but never demoted.

### Promotion Paths

```
ZERO → NEAR → OK
```

### Promotion Conditions

| From  | To   | Condition                                              |
|-------|------|--------------------------------------------------------|
| ZERO  | NEAR | Repair protocol completed, re-evaluation passes        |
| NEAR  | OK   | Additional evidence submitted, full witness quorum met |

### Promotion Rules

1. Each promotion generates a new TruthRecord appended to the quest
2. The original TruthRecord is preserved (immutable)
3. Reward delta is computed: `Δr = R(new_gate) - R(old_gate)`
4. If old reward was in NEAR vesting vault, vault transitions on promotion
5. Promotion is recorded in the receipt chain as a WITNESS entry type

### Demotion Prevention

- Truth gates cannot be demoted (OK cannot become NEAR or ZERO)
- The only negative transition is the initial FAIL evaluation
- FAIL is terminal and cannot be promoted

---

## 6. Vesting Modes

### Mode Assignment by Truth Gate

| Truth Gate | Vesting Mode        | Lock Duration       |
|------------|---------------------|---------------------|
| OK         | IMMEDIATE           | 0 epochs            |
| NEAR       | NEAR_SETTLEMENT     | Until promotion     |
| ZERO       | N/A (no reward)     | N/A                 |
| FAIL       | SLASHED             | Permanent           |

### IMMEDIATE Mode

- Reward is fully available at settlement
- No lock period
- Applied when truth gate is OK

### NEAR_SETTLEMENT Mode

- Reward locked at φ⁻² ratio
- Released portion: `reward * (1 - φ⁻²)` available immediately
- Locked portion: `reward * φ⁻²` held in VestingVault
- On promotion to OK: locked portion released
- On timeout (57 epochs without promotion): locked portion released at 50%
- On FAIL (rare, requires governance action): locked portion slashed

### FIBONACCI_LADDER Mode

- Used for large rewards exceeding `4 * base_reward`
- Unlocks in Fibonacci-step intervals
- See UnlockPolicy for full ladder schedule

---

## 7. Quest Metadata Requirements

### Required Fields by State

| Field          | Draft | Active | Blocked | Sealed | Published | Archived |
|----------------|-------|--------|---------|--------|-----------|----------|
| quest_id       | YES   | YES    | YES     | YES    | YES       | YES      |
| quest_class    | YES   | YES    | YES     | YES    | YES       | YES      |
| element        | YES   | YES    | YES     | YES    | YES       | YES      |
| corridor       | YES   | YES    | YES     | YES    | YES       | YES      |
| creator_id     | YES   | YES    | YES     | YES    | YES       | YES      |
| assignees      | —     | YES    | YES     | YES    | YES       | YES      |
| truth_record   | —     | —      | opt     | YES    | YES       | YES      |
| dependencies   | opt   | opt    | opt     | YES    | YES       | YES      |
| reward_ref     | —     | —      | —       | —      | YES       | YES      |
| receipt_chain  | —     | YES    | YES     | YES    | YES       | YES      |
