# LP-57Omega Leveling System (19x3)

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `progression-system`
- Role tags: `leveling, passes, alchemy, amplifier, infinite-cap`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the 19-level by 3-pass leveling system yielding 57 loops per orbit, the alchemical pass signatures, infinite-cap level extension, and the amplifier law governing power scaling.

## Core Structure

```
One Orbit = 3 Passes x 19 Stations = 57 Loops

Pass 1 (Sulfur):  Loops  1-19   Levels L01-L19
Pass 2 (Mercury): Loops 20-38   Levels L01-L19 (second traversal)
Pass 3 (Salt):    Loops 39-57   Levels L01-L19 (third traversal)
```

## The Three Alchemical Passes

### Pass 1 — Sulfur (Expansion)

```
Symbol:     🜍
Chi (χ):    1.000
Character:  Raw generation, exploration, divergence
Goal:       Produce maximum novel content
Bias:       Novelty gain weighted highest
Risk:       High — accepts uncertain outputs
Metaphor:   The combustible principle; what burns and transforms
```

### Pass 2 — Mercury (Refinement)

```
Symbol:     ☿
Chi (χ):    0.809 (= φ⁻² + φ⁻¹ * φ⁻² = approximation)
            More precisely: χ_Mercury = φ⁻² ≈ 0.382 ... [corrected: 0.809]
Character:  Bridging, connecting, refining
Goal:       Link disparate outputs, resolve contradictions
Bias:       Integration gain weighted highest
Risk:       Medium — validates connections
Metaphor:   The fluid principle; what flows and connects
```

Chi derivation for Mercury:
```
χ_Mercury = (1 + φ⁻¹) / φ = 2φ⁻¹ / φ...
Practical value: χ_Mercury = φ⁻¹ * φ⁰·⁵ ≈ 0.809
Used as: 0.809 in all calculations.
```

### Pass 3 — Salt (Crystallization)

```
Symbol:     🜔
Chi (χ):    φ⁻¹ ≈ 0.618
Character:  Compression, closure, crystallization
Goal:       Reduce to essential form, certify, close
Bias:       Compression gain and truth state weighted highest
Risk:       Low — demands verified, compact output
Metaphor:   The fixed principle; what remains after burning
```

## Pass Transform Matrix

Each pass applies a transform to the base payout vector:

```typescript
interface PassTransform {
  chi: float;           // global scaling factor
  d: Vec4;              // per-element directional weights
  name: string;
  symbol: string;
}

const SULFUR: PassTransform = {
  chi: 1.000,
  d: Vec4(1.0, 0.8, 0.6, 0.4),  // Fire-favoring
  name: "Sulfur",
  symbol: "🜍"
};

const MERCURY: PassTransform = {
  chi: 0.809,
  d: Vec4(0.6, 1.0, 0.8, 0.4),  // Air-favoring
  name: "Mercury",
  symbol: "☿"
};

const SALT: PassTransform = {
  chi: 0.618,
  d: Vec4(0.4, 0.6, 0.8, 1.0),  // Earth-favoring
  name: "Salt",
  symbol: "🜔"
};
```

## The 19 Levels

Each pass traverses 19 levels corresponding to the 19 stations:

| Level | Station              | Threshold (Fibonacci) | Unlock              |
|-------|---------------------|-----------------------|----------------------|
| L01   | Genesis Spark       | 0                     | Solo quests          |
| L02   | Foundation Stone    | 1                     | —                    |
| L03   | First Breath        | 2                     | Guild quests         |
| L04   | Mirror Pool         | 3                     | —                    |
| L05   | Cross Bridge        | 5                     | Community quests     |
| L06   | Deep Root           | 8                     | —                    |
| L07   | Alchemical Forge    | 13                    | —                    |
| L08   | Temple Gate         | 21                    | Temple quests        |
| L09   | Triple Junction     | 34                    | —                    |
| L10   | Shadow Well         | 55                    | —                    |
| L11   | Crown Approach      | 89                    | —                    |
| L12   | Storm Threshold     | 144                   | —                    |
| L13   | PhiStorm Eye        | 233                   | Storm quests         |
| L14   | Certification Hall  | 377                   | —                    |
| L15   | Resonance Chamber   | 610                   | —                    |
| L16   | Publish Gate        | 987                   | —                    |
| L17   | Seeding Ground      | 1597                  | —                    |
| L18   | Policy Forum        | 2584                  | —                    |
| L19   | Migration Council   | 4181                  | —                    |

### Level-Up Formula

```
xp_threshold(level) = BASE_XP * fib(level + 1)

Where:
  BASE_XP = 64
  fib(n) = nth Fibonacci number (fib(1)=1, fib(2)=1, fib(3)=2, ...)

Examples:
  L01: 64 * fib(2) = 64 * 1   = 64 XP
  L05: 64 * fib(6) = 64 * 8   = 512 XP
  L10: 64 * fib(11) = 64 * 89 = 5696 XP
  L19: 64 * fib(20) = 64 * 6765 = 433,160 XP
```

## Infinite-Cap Extension

Beyond the first orbit (57 loops), levels continue without bound:

```
level = 57 * k + ℓ

Where:
  k = completed orbit count (0, 1, 2, ...)
  ℓ = current loop within orbit (0, 1, ..., 56)

Examples:
  Orbit 0, Loop 0:  level = 0
  Orbit 0, Loop 56: level = 56
  Orbit 1, Loop 0:  level = 57
  Orbit 1, Loop 56: level = 113
  Orbit 5, Loop 30: level = 315
```

### XP Scaling Across Orbits

```
xp_threshold(level) = BASE_XP * fib((level mod 19) + 2) * φ^(floor(level/19))

The fib() component cycles every 19 levels.
The φ^(floor(level/19)) component provides geometric growth per pass.
```

## Amplifier Law

The amplifier modulates all rewards based on accumulated level:

```
amp(level) = 1 + φ⁻¹ * log_φ(1 + level)

Where:
  log_φ(x) = ln(x) / ln(φ)
```

### Amplifier Table

| Level | log_φ(1+level) | amp     | Effective multiplier |
|-------|----------------|---------|----------------------|
| 0     | 0.000          | 1.000   | 1.00x                |
| 1     | 1.440          | 1.890   | 1.89x                |
| 4     | 3.344          | 3.068   | 3.07x                |
| 9     | 4.784          | 3.958   | 3.96x                |
| 18    | 6.128          | 4.789   | 4.79x                |
| 38    | 7.620          | 5.711   | 5.71x                |
| 56    | 8.388          | 6.186   | 6.19x                |
| 113   | 9.820          | 7.071   | 7.07x                |
| 570   | 13.160         | 9.136   | 9.14x                |

### Amplifier Properties

```
1. Monotonically increasing (never decreases)
2. Logarithmic growth (diminishing returns)
3. amp(0) = 1.0 (no bonus at level 0)
4. amp(φ^n - 1) = 1 + φ⁻¹ * n (clean values at Fibonacci-related levels)
5. Growth rate: d(amp)/d(level) = φ⁻¹ / ((1+level) * ln(φ))
```

## Complete Payout Formula

```
payout_xp(station, pass, level) =
    BASE_XP                          // = 64
  * station.payout_base              // per-station base (0.5..2.0)
  * pass.d[dominant_element]         // directional element weight
  * pass.chi                         // pass scaling (1.0, 0.809, 0.618)
  * amp(level)                       // amplifier from level
```

## Pass Progression Dynamics

```
Pass 1 (Sulfur): High payouts, many new quests minted
  - Agents explore broadly
  - Pheromone trails begin forming
  - Risk tolerance high

Pass 2 (Mercury): Moderate payouts, connections prioritized
  - Agents bridge and refine
  - Pheromone trails strengthen on productive paths
  - Risk tolerance medium

Pass 3 (Salt): Lower base payouts but higher compression rewards
  - Agents crystallize and certify
  - Weak pheromone trails decay to zero
  - Only verified outputs survive
  - Carry-forward bundles prepared
```

## Invariants

1. Every orbit has exactly 57 loops (3 x 19)
2. Chi values decrease across passes: 1.0 > 0.809 > 0.618
3. Level is monotonically non-decreasing
4. The amplifier is always >= 1.0
5. XP thresholds follow Fibonacci scaling
6. Infinite-cap ensures no level ceiling exists
7. Pass order is fixed: Sulfur then Mercury then Salt

## Suggested chapter anchors

- `Ch01` — Kernel and entry law
- `Ch08` — Synchronization calculus
- `Ch14` — Migration, versioning, pulse retro-weaving
- `Ch19` — Convergence fixed points
