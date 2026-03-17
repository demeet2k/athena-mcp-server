# LP-57Omega Six Roles of Phi (Golden Ratio) in the Corpus

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `mathematical-framework`
- Role tags: `phi, golden-ratio, scaling, reward, decay`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the six distinct roles that the golden ratio phi (φ ≈ 1.618033988749895) plays across the LP-57Omega system: reward scaling, pheromone decay, quality weights, difficulty coefficients, mint rates, and level progression.

## Fundamental Constants

```
φ   = (1 + sqrt(5)) / 2  ≈ 1.618033988749895
φ⁻¹ = φ - 1              ≈ 0.618033988749895
φ⁻² = 2 - φ              ≈ 0.381966011250105
φ²  = φ + 1              ≈ 2.618033988749895

Key identity: φ² = φ + 1
Key identity: φ⁻¹ = φ - 1
Key identity: φ * φ⁻¹ = 1
```

## Role 1 — Reward Scaling

Phi scales experience point rewards across the level system to maintain geometric growth that feels natural.

### Reward Multiplier

```
reward_multiplier(level) = φ^(level / 19)

Examples:
  Level 1:  φ^(1/19)  ≈ 1.026
  Level 5:  φ^(5/19)  ≈ 1.135
  Level 10: φ^(10/19) ≈ 1.289
  Level 19: φ^(19/19) = φ ≈ 1.618
  Level 38: φ^(38/19) = φ² ≈ 2.618
  Level 57: φ^(57/19) = φ³ ≈ 4.236
```

### Payout Formula

```
payout_xp = BASE_XP * station.payout_base * reward_multiplier(level)

Where BASE_XP = 64
```

## Role 2 — Pheromone Decay

Phi-inverse governs the memory decay rate of the pheromone system, creating a golden-memory curve.

### Decay Law

```
p_e(t+1) = p_e(t) * φ⁻¹

After n epochs:
  p_e(t+n) = p_e(t) * φ⁻ⁿ
```

### Decay Curve

```
Epoch 0:  p = 1.000  (full strength)
Epoch 1:  p = 0.618  (golden fraction)
Epoch 2:  p = 0.382  (phi-squared inverse)
Epoch 3:  p = 0.236
Epoch 4:  p = 0.146
Epoch 5:  p = 0.090
Epoch 10: p = 0.008  (effectively zero)
```

### Significance

The φ⁻¹ decay rate is uniquely self-similar: the ratio between consecutive values equals the ratio between the value and 1. This means pheromone trails maintain proportional relationships regardless of absolute strength.

## Role 3 — Quality Weights

Phi partitions quality assessment into naturally balanced components.

### Quality Vector Weights

```
quality_score = w_truth * truth_state
             + w_integration * integration_gain
             + w_compression * compression_gain
             + w_novelty * novelty_gain

Where weights follow the phi partition:
  w_truth       = φ⁻¹ * φ⁻¹  = φ⁻²  ≈ 0.382
  w_integration = φ⁻¹ * φ⁻²  ≈ 0.236
  w_compression = φ⁻² * φ⁻¹  ≈ 0.236
  w_novelty     = φ⁻² * φ⁻²  ≈ 0.146

Sum = 0.382 + 0.236 + 0.236 + 0.146 = 1.000
```

### Agent-Specific Weight Overrides

Each master agent applies a phi-rotated weight vector:

```
A1 Synthesizer: [φ⁻², φ⁻¹, φ⁻², φ⁻²]  — integration boosted
A2 Planner:     [φ⁻², φ⁻², φ⁻¹, φ⁻²]  — compression boosted
A3 Worker:      [φ⁻², φ⁻², φ⁻², φ⁻¹]  — novelty boosted
A4 Pruner:      [φ⁻¹, φ⁻², φ⁻², φ⁻²]  — truth boosted
```

## Role 4 — Difficulty Coefficients

Phi governs how difficulty scales across stations and passes.

### Station Difficulty

```
difficulty(station_index) = 1 + (station_index - 1) * φ⁻¹ / 18

S01: 1.000  (easiest)
S10: 1.309  (midpoint)
S19: 1.618  (hardest, = φ)
```

### Pass Difficulty Transform

```
pass_difficulty(pass, base_diff) =
  Pass 1 (Sulfur):  base_diff * 1.0        (raw)
  Pass 2 (Mercury): base_diff * φ⁻¹ * φ    (= base_diff, neutral)
  Pass 3 (Salt):    base_diff * φ           (amplified)
```

### Combined Difficulty

```
combined_difficulty(station, pass) = station_diff * pass_chi * φ^(orbit/10)

The φ^(orbit/10) term provides slow long-term difficulty escalation.
```

## Role 5 — Mint Rates

Phi controls the creation rate of new quests, artifacts, and connections.

### Quest Mint Rate

```
quests_per_loop = floor(φ * station.base_mint_rate * pass_chi)

Typical base_mint_rates by station type:
  Generation stations (S01, S07): base = 3
  Routing stations (S05, S09):    base = 2
  Verification stations (S14):    base = 1
  Storm stations (S13):           base = φ (variable)
```

### Connection Mint Rate

```
connections_per_loop = floor(φ⁻¹ * active_quests * neural_connectivity)

This ensures connections grow slower than quests,
maintaining a sparse but meaningful graph.
```

### Artifact Compression Mint

```
compressed_artifacts = floor(φ⁻² * raw_artifacts)

Approximately 38% of raw artifacts survive compression,
matching the phi-squared inverse ratio.
```

## Role 6 — Level Progression

Phi structures the experience curve and level boundaries.

### XP Required per Level

```
xp_for_level(n) = BASE_XP * φ^(n-1)

Level 1:   64 XP
Level 2:  104 XP  (64 * φ)
Level 3:  168 XP  (64 * φ²)
Level 5:  439 XP  (64 * φ⁴)
Level 10: 4,674 XP
Level 19: 422,576 XP
```

### Amplifier Law

```
amp(level) = 1 + φ⁻¹ * log_φ(1 + level)

Level 1:  amp = 1.000
Level 5:  amp = 1.618  (= 1 + φ⁻¹ * 1)
Level 10: amp = 2.000
Level 19: amp = 2.427
Level 57: amp = 3.191
```

### Infinite-Cap Level Formula

```
For orbits beyond the first:
  level = 57 * k + ℓ

Where:
  k = completed orbit count (0-indexed)
  ℓ = current loop within orbit (0..56)

This allows unbounded progression while maintaining
the 57-loop orbit structure.
```

## Phi Unification Table

| Role              | Formula                           | Primary Phi Power |
|-------------------|-----------------------------------|-------------------|
| Reward scaling    | φ^(level/19)                      | φ^(fractional)    |
| Pheromone decay   | p *= φ⁻¹                         | φ⁻¹               |
| Quality weights   | w = φ⁻ⁿ partition                 | φ⁻², φ⁻¹          |
| Difficulty coeff  | 1 + (s-1)*φ⁻¹/18                 | φ⁻¹, φ            |
| Mint rates        | floor(φ * base)                   | φ, φ⁻¹, φ⁻²      |
| Level progression | 1 + φ⁻¹ * log_φ(1+level)         | φ⁻¹, log_φ        |

## Invariants

1. All phi-derived values are deterministic and reproducible
2. φ * φ⁻¹ = 1 is preserved in all ratio calculations
3. Decay never reaches exactly zero (asymptotic)
4. Quality weights always sum to 1.0
5. Level progression is monotonically increasing
6. Mint rates are always non-negative integers (floored)

## Suggested chapter anchors

- `Ch04` — Zero-point stabilization
- `Ch08` — Synchronization calculus
- `Ch18` — Macro invariants and universal math stack
- `Ch19` — Convergence fixed points
