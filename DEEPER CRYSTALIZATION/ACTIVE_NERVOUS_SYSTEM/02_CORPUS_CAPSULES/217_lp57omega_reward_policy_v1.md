# LP57Ω RewardPolicy.v1

- Kind: `policy-specification`
- Role tags: `rewards, economics, truth-gate, minting, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the complete reward computation policy for the LP57Ω quest economy. All reward calculations derive from the truth gate, quality law, contribution splits, community multipliers, per-capsule and per-epoch clamps, resonance ratios, and mint rates by quest class.

---

## 1. Truth Gate

The truth gate is the primary multiplicative factor in all reward calculations.

### Gate Coefficients (γ)

| Truth4 | Symbol   | Value               | Numeric       |
|--------|----------|---------------------|---------------|
| OK     | γ_OK     | 1.0                 | 1.000000      |
| NEAR   | γ_NEAR   | φ⁻²                 | 0.381966...   |
| ZERO   | γ_ZERO   | 0.0                 | 0.000000      |
| FAIL   | γ_FAIL   | -φ⁻¹ (slash)        | -0.618033...  |

Where φ = (1 + √5) / 2 ≈ 1.618033988749895.

### Gate Law

```
reward_factor(gate) = γ(gate)
```

- **OK**: Full reward. The quest passed all truth checks.
- **NEAR**: Partial reward at the golden ratio squared inverse. Indicates approximate truth with known gaps.
- **ZERO**: No reward. The quest produced no verifiable truth.
- **FAIL**: Negative consequence. The vault is slashed at φ⁻¹ ratio.

---

## 2. Quality Law

Quality is assessed on a continuous scale [0.0, 1.0] derived from corridor completion depth and witness attestation strength.

```
quality(q) = (stations_completed / stations_total) * witness_strength
```

### Witness Strength

```
witness_strength = (1/W) * Σ_{w ∈ witnesses} strength(w.attestation)
```

Where:
- `strength(OK) = 1.0`
- `strength(NEAR) = φ⁻²`
- `strength(ZERO) = 0.0`
- `strength(FAIL) = 0.0`

### Quality Floor

If `quality(q) < φ⁻⁴ ≈ 0.1459`, the quest is flagged for review and reward is held in escrow.

---

## 3. Contribution Split

For multi-agent quests, rewards are split proportionally to contribution.

```
contribution(agent_i) = stations_by_agent_i / total_stations_completed
```

### Split Rules

1. Each agent receives: `total_reward * contribution(agent_i)`
2. Minimum contribution to receive reward: `φ⁻³ ≈ 0.2360`
3. Contributions below minimum are redistributed proportionally to qualifying agents
4. Creator receives a floor of `φ⁻² ≈ 0.3820` of total if they are a contributor

---

## 4. Community Multiplier

Community quests receive a bonus multiplier based on participant count.

```
community_mult(N) = 1 + β * N
```

Where:
- **β = 0.25** (community coefficient)
- **N** = number of qualifying contributors (contribution ≥ φ⁻³)

### Examples

| Contributors (N) | Multiplier        |
|-------------------|-------------------|
| 1 (solo)          | 1.25              |
| 2                 | 1.50              |
| 3                 | 1.75              |
| 4                 | 2.00              |
| 8                 | 3.00              |

### Community Cap

The community multiplier is capped at `1 + β * 13 = 4.25` (maximum 13 qualifying contributors).

---

## 5. Per-Capsule Clamp

No single quest may mint more than 16 times the base reward.

```
per_capsule_clamp = 16 * base_reward
```

### Enforcement

```
clamped_reward = min(computed_reward, 16 * base_reward)
```

If the clamp activates, a warning (lint code L014) is emitted in the receipt chain.

---

## 6. Per-Epoch Clamp

Total minting across all quests in a single epoch is bounded.

```
per_epoch_clamp = 64 * base_reward
```

### Overflow Handling

When the epoch clamp is reached:
1. Remaining rewards are queued for the next epoch
2. Priority: quests sealed earlier in the epoch are rewarded first
3. Overflow queue drains at the start of the next epoch before new rewards

---

## 7. Resonance Ratio

The resonance ratio modulates long-term reward scaling based on system-wide quest coherence.

```
resonance = φ⁻¹ ≈ 0.618033988749895
```

### Application

```
resonance_bonus = base_reward * resonance * coherence_score
```

Where `coherence_score ∈ [0.0, 1.0]` measures how well the quest's corridor aligns with the global corridor field.

---

## 8. Mint Rates by Quest Class

| Quest Class  | Base Mint | Truth Factor | Quality | Community | Resonance | Formula |
|-------------|-----------|-------------|---------|-----------|-----------|---------|
| Solo        | 1.0       | γ           | q       | 1.0       | optional  | `1.0 * γ * q` |
| Community   | 1.0       | γ           | q       | 1+β*N    | optional  | `1.0 * γ * q * (1+β*N)` |
| TempleRite  | φ         | γ           | q       | 1+β*N    | φ⁻¹      | `φ * γ * q * (1+β*N) * (1+φ⁻¹*c)` |
| Storm       | φ²        | γ           | q       | 1+β*N    | φ⁻¹      | `φ² * γ * q * (1+β*N) * (1+φ⁻¹*c)` |

### Storm Pool Distribution

Storm rewards draw from the storm pool rather than base minting:

```
storm_reward(agent) = storm_pool * contribution(agent) * coalition_bonus
coalition_bonus = 1 + φ⁻³ * (coalition_size - 1)
```

---

## 9. Complete Reward Formula

```
R(quest) = min(
    base_mint(class) * γ(gate) * quality(q) * community_mult(N) * (1 + resonance * coherence),
    per_capsule_clamp
)
```

Subject to:
```
Σ R(quest_i) for epoch_k ≤ per_epoch_clamp
```

---

## 10. Constants Summary

| Constant          | Symbol    | Value                |
|-------------------|-----------|----------------------|
| Golden ratio      | φ         | 1.618033988749895    |
| Truth OK          | γ_OK      | 1.0                  |
| Truth NEAR        | γ_NEAR    | φ⁻² = 0.381966...   |
| Truth ZERO        | γ_ZERO    | 0.0                  |
| Truth FAIL        | γ_FAIL    | -φ⁻¹ = -0.618033... |
| Community β       | β         | 0.25                 |
| Per-capsule clamp |           | 16 * base            |
| Per-epoch clamp   |           | 64 * base            |
| Resonance ratio   |           | φ⁻¹ = 0.618033...   |
| Quality floor     |           | φ⁻⁴ = 0.145898...   |
| Min contribution  |           | φ⁻³ = 0.236067...   |
| Creator floor     |           | φ⁻² = 0.381966...   |
| Community cap     |           | 4.25 (N=13)          |
