# LP-57Omega Phi-Pheromone System

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `agent-signaling`
- Role tags: `pheromones, swarm, stigmergy, storm`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the 8-channel pheromone system (4 positive + 4 shadow), the deposit law, golden-memory decay, and the PhiStorm trigger conditions that emerge from pheromone saturation.

## Channel Architecture

The pheromone system has 8 channels arranged as 4 complementary pairs:

```
Positive Channels          Shadow Channels
─────────────────          ────────────────
p_F  (Fire pheromone)      s_F  (Fire shadow)
p_A  (Air pheromone)       s_A  (Air shadow)
p_W  (Water pheromone)     s_W  (Water shadow)
p_E  (Earth pheromone)     s_E  (Earth shadow)
```

### Channel Semantics

| Channel | Positive Signal                  | Shadow Signal                    |
|---------|----------------------------------|----------------------------------|
| Fire    | Action taken, progress made      | Burnout, overcommitment          |
| Air     | Insight gained, pattern found    | Overthinking, abstraction excess |
| Water   | Connection formed, flow achieved | Drift, loss of direction         |
| Earth   | Structure built, form stabilized | Rigidity, premature closure      |

### Vec8 Pheromone State

```typescript
type PheromoneState = {
  positive: Vec4;  // [p_F, p_A, p_W, p_E]
  shadow:   Vec4;  // [s_F, s_A, s_W, s_E]
};

// Total pheromone magnitude
total_positive = p_F + p_A + p_W + p_E
total_shadow   = s_F + s_A + s_W + s_E
```

## Deposit Law

When an agent completes an action, it deposits pheromone proportional to the action's quality:

```
DEPOSIT(action, pheromone_state):

  For each element e in {F, A, W, E}:
    delta_e = action.element_vector[e] * action.quality_score
    p_e += kappa * delta_e          // positive deposit
    s_e += kappa * (1 - delta_e)    // shadow deposit (inverse)

  Where:
    kappa = deposit_coefficient = φ⁻² ≈ 0.382
```

### Deposit Coefficient (kappa)

```
kappa = φ⁻² ≈ 0.382

Rationale: kappa = φ⁻² ensures that:
  - A perfect action (quality=1.0) deposits 0.382 positive per element
  - The deposit rate is self-similar with the decay rate
  - kappa * φ = φ⁻¹ (deposit * one decay cycle = next lower power)
```

### Deposit Examples

```
Action: Fire-dominant merge (quality=0.8)
  element_vector = Vec4(0.7, 0.2, 0.05, 0.05)

  Positive deposits:
    p_F += 0.382 * 0.7 * 0.8 = 0.214
    p_A += 0.382 * 0.2 * 0.8 = 0.061
    p_W += 0.382 * 0.05 * 0.8 = 0.015
    p_E += 0.382 * 0.05 * 0.8 = 0.015

  Shadow deposits:
    s_F += 0.382 * (1 - 0.56) = 0.168
    s_A += 0.382 * (1 - 0.16) = 0.321
    s_W += 0.382 * (1 - 0.04) = 0.367
    s_E += 0.382 * (1 - 0.04) = 0.367
```

## Golden-Memory Decay

Every epoch (one complete loop), all pheromone values decay by the golden ratio inverse:

```
DECAY(pheromone_state):
  For each channel c in all 8 channels:
    c *= φ⁻¹

  Equivalently:
    p_e(t+1) = p_e(t) * φ⁻¹    for all e
    s_e(t+1) = s_e(t) * φ⁻¹    for all e
```

### Decay Properties

```
Half-life:
  φ⁻ⁿ = 0.5  →  n = log(0.5) / log(φ⁻¹) ≈ 1.44 epochs
  (pheromone halves roughly every 1.44 loops)

Effective memory window:
  After 5 epochs:  φ⁻⁵ ≈ 0.090  (9% remaining)
  After 10 epochs: φ⁻¹⁰ ≈ 0.008 (< 1% remaining)
  After 19 epochs: φ⁻¹⁹ ≈ 0.00007 (negligible)

One full pass (19 loops) effectively erases pheromone memory,
allowing each pass to build fresh trails.
```

### Self-Similarity of Decay

The golden decay has a unique self-similar property:

```
p(t) - p(t+1) = p(t) * (1 - φ⁻¹) = p(t) * φ⁻²
p(t+1) / p(t) = φ⁻¹
(p(t) - p(t+1)) / p(t+1) = φ⁻¹

The ratio of lost pheromone to remaining pheromone
equals the ratio of remaining to original.
```

## Steady-State Analysis

Under constant deposit rate d per epoch:

```
Steady state: p_ss = d / (1 - φ⁻¹) = d / φ⁻² = d * φ²

For d = kappa = φ⁻²:
  p_ss = φ⁻² * φ² = 1.0

A single agent depositing at base rate reaches steady state p = 1.0.
```

### Multi-Agent Accumulation

```
With N agents depositing simultaneously:
  p_ss = N * kappa * φ² = N * 1.0 = N

4 master agents: p_ss = 4.0 per element (if all deposit equally)
```

## PhiStorm Trigger

A PhiStorm occurs when pheromone accumulation crosses critical thresholds, indicating the system has reached a phase-transition point.

### Trigger Conditions

```
STORM_CHECK(pheromone_state) -> bool:

  Condition 1 — Positive Saturation:
    total_positive = p_F + p_A + p_W + p_E
    positive_saturated = (total_positive >= 34)

  Condition 2 — Shadow Suppression:
    total_shadow = s_F + s_A + s_W + s_E
    shadow_low = (total_shadow <= 13)

  PhiStorm triggered = positive_saturated AND shadow_low
```

### Threshold Derivation

```
34 and 13 are Fibonacci numbers.

34 = F(9)   — ninth Fibonacci number
13 = F(7)   — seventh Fibonacci number

Ratio: 34/13 ≈ 2.615 ≈ φ²

The storm triggers when positive pheromone exceeds
shadow pheromone by approximately φ² ratio.
```

### Storm Intensity

```
storm_intensity = (total_positive - 34) / 34 + (13 - total_shadow) / 13

Clamped to [0.0, 1.0]:
  0.0 = barely triggered
  1.0 = maximum storm (positive >> 34, shadow << 13)
```

### Storm Effects

```
When PhiStorm is active (at station S13):

1. ACCELERATION
   - Quest processing speed doubles
   - Mint rates increase by factor φ
   - Seat election threshold lowered

2. AMPLIFICATION
   - Pheromone deposits multiplied by φ
   - XP rewards multiplied by φ²
   - Quality thresholds raised by φ⁻¹

3. TURBULENCE
   - Random quest reassignment (shuffle rate = storm_intensity * 0.3)
   - Cross-agent bridges forced (minimum 2 per loop)
   - Shadow channels receive burst deposits

4. DURATION
   - Storm lasts until total_positive < 21 (F(8))
   - OR total_shadow > 21 (balancing point)
   - Natural decay handles most dissipation
```

## Pheromone Visualization

```
Channel strengths displayed as bar chart:

p_F: ████████████████░░░░  (0.80)
p_A: ██████████░░░░░░░░░░  (0.50)
p_W: ████░░░░░░░░░░░░░░░░  (0.20)
p_E: ██████████████░░░░░░  (0.65)
────────────────────────────
s_F: ██░░░░░░░░░░░░░░░░░░  (0.10)
s_A: ████░░░░░░░░░░░░░░░░  (0.20)
s_W: ████████████████░░░░  (0.80)
s_E: ████░░░░░░░░░░░░░░░░  (0.18)
```

## Invariants

1. All pheromone values are non-negative
2. Decay is applied uniformly to all 8 channels every epoch
3. Deposit always affects both positive and shadow channels
4. PhiStorm requires BOTH positive saturation AND shadow suppression
5. Storm thresholds are Fibonacci numbers (34, 13)
6. The decay rate (phi-inverse) is constant and never changes
7. Pheromone state is part of the carry_forward_bundle (class: DECAYING)

## Suggested chapter anchors

- `Ch04` — Zero-point stabilization
- `Ch08` — Synchronization calculus
- `Ch11` — Void book and restart token tunneling
- `Ch13` — Memory regeneration and persistence
