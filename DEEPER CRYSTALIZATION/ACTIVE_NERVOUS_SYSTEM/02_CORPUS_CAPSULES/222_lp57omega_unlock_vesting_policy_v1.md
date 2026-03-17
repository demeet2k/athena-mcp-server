# LP57Ω UnlockPolicy + VestingPolicy v1

- Kind: `policy-specification`
- Role tags: `unlock, vesting, fibonacci-ladder, NEAR-settlement, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the Fibonacci ladder unlock schedule and the NEAR settlement vesting policy. Governs how rewards are locked, released, slashed, and partially unlocked based on truth gate status and time.

---

## Part I: UnlockPolicy — Fibonacci Ladder

### 1. Overview

The Fibonacci ladder governs unlock schedules for large rewards (those exceeding `4 * base_reward`). Rewards unlock in increments following the Fibonacci sequence, ensuring gradual release aligned with the system's harmonic structure.

### 2. Ladder Steps

| Step | Fibonacci(n) | Cumulative | Fraction of Total | Epoch Delay |
|------|-------------|------------|-------------------|-------------|
| 1    | 1           | 1          | 1/F_total         | 1           |
| 2    | 1           | 2          | 2/F_total         | 2           |
| 3    | 2           | 4          | 4/F_total         | 3           |
| 4    | 3           | 7          | 7/F_total         | 5           |
| 5    | 5           | 12         | 12/F_total        | 8           |
| 6    | 8           | 20         | 20/F_total        | 13          |
| 7    | 13          | 33         | 33/F_total        | 21          |
| 8    | 21          | 54         | 54/F_total        | 34          |
| 9    | 34          | 88         | 88/F_total        | 55          |
| 10   | 55          | 143        | 143/F_total       | 89          |

Where `F_total = 143` (sum of first 10 Fibonacci numbers starting from F(1)=1).

### 3. Unlock Formula

```
unlock_amount(step_k) = total_reward * (Fib(k) / F_total)
unlock_epoch(step_k) = seal_epoch + Fib(k + 4)
```

The epoch delay follows a shifted Fibonacci sequence starting at F(5)=5 for step 1.

### 4. FibonacciStep Schema

```typescript
interface FibonacciStep {
  step:          uint;         // 1-10
  fib_value:     uint;         // Fibonacci number for this step
  cumulative:    uint;         // Running total
  fraction:      number;       // fib_value / 143
  unlock_epoch:  uint;         // Absolute epoch when unlock occurs
  amount:        number;       // Actual token amount
  unlocked:      boolean;      // Whether this step has been released
  unlocked_at:   ISO8601 | null;
}
```

### 5. Ladder Assignment Rules

| Reward Size                | Ladder Steps | Rationale                     |
|---------------------------|-------------|-------------------------------|
| ≤ 4 * base_reward         | None (immediate) | Small reward, no ladder  |
| (4, 8] * base_reward      | Steps 1-5   | Medium reward                 |
| (8, 16] * base_reward     | Steps 1-8   | Large reward                  |
| > 16 * base_reward        | Steps 1-10  | Maximum reward (clamp applies)|

### 6. Early Unlock Conditions

A step may unlock early if:
1. The quest receives a truth promotion (NEAR → OK)
2. The quest is cited by 3+ other Published quests (cross-reference bonus)
3. Governance vote approves early release

Early unlock releases the current step and all prior unreleased steps.

### 7. Ladder Cancellation

The ladder is cancelled (all remaining steps void) if:
1. Truth gate demotes to FAIL (governance action)
2. Quest is archived with unresolved invariants
3. Agent account is suspended

Cancelled steps are returned to the system pool.

---

## Part II: VestingPolicy — NEAR Settlement

### 1. Overview

When a quest receives a NEAR truth gate, the reward enters NEAR settlement: a portion is immediately available and the remainder is locked pending truth promotion.

### 2. Lock Ratio

```
lock_ratio = φ⁻² ≈ 0.381966
```

### 3. Settlement Split

```
immediate_release = reward * (1 - φ⁻²) = reward * 0.618034
locked_amount     = reward * φ⁻²        = reward * 0.381966
```

### 4. NEAR Vault Schema

```typescript
interface NEARVault {
  vault_id:          string;
  quest_id:          string;
  agent_id:          string;
  total_reward:      number;
  immediate_release: number;     // reward * 0.618034
  locked_amount:     number;     // reward * 0.381966
  lock_ratio:        number;     // φ⁻²
  state:             VaultState; // LOCKED | RELEASED | SLASHED
  created_at:        ISO8601;
  promotion_deadline: ISO8601;   // seal_epoch + 57 epochs
  released_at:       ISO8601 | null;
  release_trigger:   string | null;
}
```

### 5. Release on Upgrade to OK

When the truth gate is promoted from NEAR to OK:

```python
def release_near_vault(vault, promotion_record):
    assert vault.state == "LOCKED"
    assert promotion_record.new_gate == "OK"

    vault.state = "RELEASED"
    vault.released_at = now()
    vault.release_trigger = "TRUTH_PROMOTION"

    # Full locked amount released
    payout = vault.locked_amount
    credit_agent(vault.agent_id, payout)

    # Log release receipt
    log_receipt(vault.quest_id, "VAULT_RELEASE", {
        "vault_id": vault.vault_id,
        "amount": payout,
        "trigger": "TRUTH_PROMOTION"
    })
```

### 6. Slash on FAIL

If the quest receives a FAIL determination (requires governance action):

```python
def slash_near_vault(vault, fail_record):
    assert vault.state == "LOCKED"

    vault.state = "SLASHED"
    vault.released_at = now()
    vault.release_trigger = "SLASH"

    slashed = vault.locked_amount
    return_to_pool(slashed)

    log_receipt(vault.quest_id, "VAULT_SLASH", {
        "vault_id": vault.vault_id,
        "amount": slashed,
        "trigger": "FAIL_DETERMINATION"
    })
```

### 7. Partial Release Rules

#### Timeout Release

If 57 epochs pass without truth promotion:

```
timeout_release = locked_amount * 0.5
retained = locked_amount * 0.5  → returned to pool
```

#### Cross-Reference Release

If the NEAR quest is cited by 2+ Published quests:

```
cross_ref_release = locked_amount * φ⁻¹ ≈ locked_amount * 0.618034
retained = locked_amount * (1 - φ⁻¹) → remains locked
```

#### Incremental Release

Each epoch after the 34th without promotion:

```
incremental_release = locked_amount * φ⁻⁵ per epoch ≈ 0.09017 per epoch
```

Until either the vault is empty or promotion occurs.

### 8. Partial Release Priority

When multiple release conditions apply simultaneously:

1. Truth promotion (full release) takes precedence
2. Cross-reference release
3. Timeout release
4. Incremental release

Only the highest-priority applicable release executes.

---

## Combined Policy Interaction

### NEAR + Fibonacci Ladder

When a quest has both NEAR truth and a large reward:

1. Immediate release portion (`reward * 0.618034`) enters the Fibonacci ladder
2. Locked portion (`reward * 0.381966`) enters NEAR vault
3. On promotion to OK: NEAR vault releases, and released amount joins the ladder at the current step
4. Ladder steps already unlocked are not affected

### State Diagram

```
Quest Sealed (NEAR, large reward)
    │
    ├── Immediate: 0.618034 * reward → Fibonacci Ladder
    │       └── Steps unlock per schedule
    │
    └── Locked: 0.381966 * reward → NEAR Vault
            ├── Promotion → Release → joins ladder
            ├── Timeout → 50% release, 50% pool
            ├── Cross-ref → φ⁻¹ release
            └── FAIL → Slash → pool
```
