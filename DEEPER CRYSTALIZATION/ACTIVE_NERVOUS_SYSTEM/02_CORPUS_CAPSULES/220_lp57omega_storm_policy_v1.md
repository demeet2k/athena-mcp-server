# LP57Ω StormPolicy.v1

- Kind: `policy-specification`
- Role tags: `storms, pheromone, coalition, difficulty, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the storm event lifecycle policy: spawn triggers from pheromone thresholds, pool allocation formulas, duration rules, difficulty boost scaling, coalition bonus computation, and admission filtering.

---

## 1. Spawn Trigger

Storms spawn when the pheromone field crosses critical thresholds.

### Positive Threshold

```
SPAWN if pheromone_positive ≥ 34
```

The positive pheromone accumulates as quests complete successfully in a corridor. When the corridor's positive pheromone reaches 34, a storm event spawns automatically.

### Shadow Threshold

```
SHADOW_STORM if pheromone_shadow ≤ 13
```

Shadow storms spawn when the shadow pheromone drops to 13 or below, indicating insufficient challenge in the corridor. Shadow storms increase difficulty and reduce base rewards.

### Spawn Conditions Matrix

| Condition              | Positive ≥ 34 | Shadow ≤ 13 | Storm Type   |
|------------------------|---------------|-------------|--------------|
| High activity corridor | YES           | NO          | Standard     |
| Low challenge corridor | NO            | YES         | Shadow       |
| Both thresholds met    | YES           | YES         | Convergence  |
| Neither threshold      | NO            | NO          | No spawn     |

### Pheromone Decay

```
pheromone(t+1) = pheromone(t) * (1 - decay_rate) + deposits(t)
```

Default `decay_rate = φ⁻³ ≈ 0.2360` per epoch.

---

## 2. Pool Allocation

### Base Pool

```
pool_base = 21
```

The base pool is 21 units (Fibonacci number), allocated at storm spawn.

### Scaled Pool

```
pool_scaled = pool_base + scale_factor * (coalition_size - 1)
scale_factor = 13
```

Each coalition member beyond the first adds 13 units (Fibonacci number) to the pool.

### Pool Examples

| Coalition Size | Pool Calculation    | Total Pool |
|---------------|---------------------|------------|
| 1             | 21 + 13*(1-1)       | 21         |
| 2             | 21 + 13*(2-1)       | 34         |
| 3             | 21 + 13*(3-1)       | 47         |
| 5             | 21 + 13*(5-1)       | 73         |
| 8             | 21 + 13*(8-1)       | 112        |

### Pool Cap

Maximum pool size: `21 + 13 * 12 = 177` (coalition cap of 13 members).

### Pool Distribution

```
agent_reward(i) = pool_scaled * contribution(i) * coalition_bonus(i)
```

Subject to: `Σ agent_reward(i) ≤ pool_scaled`

---

## 3. Duration

### Base Duration

```
duration_base = 5 epochs
```

### Duration Modifiers

| Modifier              | Effect                    | Formula                  |
|-----------------------|---------------------------|--------------------------|
| Coalition size > 3    | +1 epoch per 3 members    | `5 + floor((N-1)/3)`    |
| Shadow storm          | -1 epoch                  | `max(3, duration - 1)`  |
| Convergence storm     | +2 epochs                 | `duration + 2`          |
| Difficulty > φ        | +1 epoch                  | `duration + 1`          |

### Duration Cap

```
max_duration = 13 epochs
```

### Epoch Countdown

- Storm state transitions at each epoch boundary
- `ACTIVE` for epochs 1 through (duration - 1)
- `WANING` for the final epoch
- `SETTLED` or `EXPIRED` after final epoch

---

## 4. Difficulty Boost

### Base Difficulty

```
difficulty_base = φ⁻³ ≈ 0.236067977
```

### Scaling Formula

```
difficulty(storm) = difficulty_base * (1 + φ⁻³ * storm_count_in_corridor)
```

Where `storm_count_in_corridor` is the number of storms previously spawned in the same corridor during the current orbit.

### Difficulty Effects

| Difficulty Range      | Effect                                |
|-----------------------|---------------------------------------|
| [0.0, φ⁻³)           | Normal — no modifier                  |
| [φ⁻³, φ⁻²)           | Elevated — witness quorum +1          |
| [φ⁻², φ⁻¹)           | High — replay required                |
| [φ⁻¹, 1.0)           | Extreme — all stations must be hit    |
| ≥ 1.0                | Maximum — coalition minimum 3         |

### Difficulty Decay

After storm settlement:
```
corridor_difficulty *= (1 - φ⁻²)
```

Difficulty decays toward baseline between storms.

---

## 5. Coalition Bonus

### Per-Member Bonus

```
coalition_bonus_per_member = φ⁻³ ≈ 0.236067977
```

### Total Coalition Bonus

```
coalition_bonus(N) = 1 + φ⁻³ * (N - 1)
```

| Coalition Size (N) | Bonus Factor       | Numeric    |
|--------------------|--------------------|------------|
| 1                  | 1.000              | 1.000      |
| 2                  | 1 + φ⁻³            | 1.236      |
| 3                  | 1 + 2φ⁻³           | 1.472      |
| 4                  | 1 + 3φ⁻³           | 1.708      |
| 5                  | 1 + 4φ⁻³           | 1.944      |
| 8                  | 1 + 7φ⁻³           | 2.652      |
| 13                 | 1 + 12φ⁻³          | 3.833      |

### Bonus Application

The coalition bonus multiplies each member's proportional share:

```
member_reward(i) = (pool_scaled / N) * coalition_bonus(N) * contribution_weight(i)
```

Where `contribution_weight` is normalized so that `Σ contribution_weight = N`.

---

## 6. Admission Filter

### Eligibility Criteria

| Criterion                        | Requirement                     |
|----------------------------------|---------------------------------|
| Agent level                      | ≥ storm corridor minimum level  |
| Active quest count               | < 5 concurrent quests           |
| Ethics status                    | No active CRITICAL flags        |
| Consent                          | PARTICIPATION consent provided  |
| Recent FAIL count                | ≤ 2 FAIL gates in last 13 epochs|
| Corridor familiarity             | ≥ 1 completed quest in corridor |

### Filter Algorithm

```python
def admit_to_storm(agent, storm) -> AdmissionResult:
    if agent.level < storm.corridor.min_level:
        return AdmissionResult(admitted=False, reason="LEVEL_TOO_LOW")

    if agent.active_quest_count >= 5:
        return AdmissionResult(admitted=False, reason="QUEST_LIMIT")

    if agent.has_critical_ethics_flag():
        return AdmissionResult(admitted=False, reason="ETHICS_FLAG")

    if not agent.has_consent(PARTICIPATION, storm.quest_id):
        return AdmissionResult(admitted=False, reason="NO_CONSENT")

    recent_fails = agent.fail_count_in_epochs(13)
    if recent_fails > 2:
        return AdmissionResult(admitted=False, reason="FAIL_LIMIT")

    if agent.completed_quests_in_corridor(storm.corridor) < 1:
        return AdmissionResult(admitted=False, reason="NO_FAMILIARITY")

    return AdmissionResult(admitted=True)
```

### Coalition Assembly

1. Storm spawns with empty coalition
2. Eligible agents may join during the first epoch (BREWING state)
3. Minimum coalition size: 1 (solo storm)
4. Maximum coalition size: 13
5. Once storm transitions to ACTIVE, no new members may join
6. A member may leave during ACTIVE but forfeits all storm reward

---

## 7. Storm Settlement

### Settlement Conditions

| Condition            | Result   |
|----------------------|----------|
| Duration complete, quorum met | SETTLED  |
| Duration expired, quorum not met | EXPIRED |
| All members leave    | EXPIRED  |
| Governance halt      | EXPIRED  |

### Settlement Process

1. Compute each member's contribution from corridor station completions
2. Apply coalition bonus to proportional shares
3. Apply truth gate (averaged across all member truth records)
4. Distribute rewards from pool
5. Generate storm receipt in each member's receipt chain
6. Transition storm to SETTLED state
7. Decay corridor pheromone and difficulty
