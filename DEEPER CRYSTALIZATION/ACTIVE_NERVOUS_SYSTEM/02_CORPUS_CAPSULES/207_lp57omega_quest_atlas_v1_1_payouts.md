# LP-57Omega Quest Atlas v1.1 — Payout Matrices

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `reward-specification`
- Role tags: `payout, xp, reward, economy`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the payout matrices per station, the master payout formula, element-weighted distribution, and pass-transform modulation. BASE_XP_UNIT = 64.

## Master Payout Formula

```
payout_e = BASE_XP
         * station.payout_base
         * element_vector_e
         * pass_transform.d[e]
         * pass_transform.chi

Where:
  BASE_XP = 64
  e in {F, A, W, E}
  payout_total = payout_F + payout_A + payout_W + payout_E
```

### Component Breakdown

| Component               | Source          | Range       |
|--------------------------|-----------------|-------------|
| BASE_XP                 | Global constant | 64          |
| station.payout_base     | Station spec    | [0.5, 2.0]  |
| element_vector_e        | Quest/artifact  | [0.0, 1.0]  |
| pass_transform.d[e]     | Pass spec       | [0.4, 1.0]  |
| pass_transform.chi      | Pass spec       | {1.0, 0.809, 0.618} |

## Station Payout Bases

| Station | Name                | payout_base | Rationale                        |
|---------|---------------------|-------------|----------------------------------|
| S01     | Genesis Spark       | 1.0         | Standard generation reward       |
| S02     | Foundation Stone    | 0.8         | Structural work, moderate reward |
| S03     | First Breath        | 0.9         | Analysis, slightly below base    |
| S04     | Mirror Pool         | 1.1         | Recursion detection premium      |
| S05     | Cross Bridge        | 1.2         | Bridge-building premium          |
| S06     | Deep Root           | 1.0         | Standard deep work               |
| S07     | Alchemical Forge    | 1.5         | Heavy transformation premium     |
| S08     | Temple Gate         | 1.3         | Deep focus premium               |
| S09     | Triple Junction     | 1.0         | Routing is standard work         |
| S10     | Shadow Well         | 1.8         | Dangerous void work premium      |
| S11     | Crown Approach      | 1.4         | Integration premium              |
| S12     | Storm Threshold     | 1.2         | Pre-storm assessment             |
| S13     | PhiStorm Eye        | 2.0         | Maximum premium (storm risk)     |
| S14     | Certification Hall  | 1.3         | Verification premium             |
| S15     | Resonance Chamber   | 1.1         | Harmonic testing                 |
| S16     | Publish Gate        | 1.5         | Publication milestone            |
| S17     | Seeding Ground      | 0.8         | Future-oriented (deferred value) |
| S18     | Policy Forum        | 1.0         | Governance work                  |
| S19     | Migration Council   | 1.6         | Critical orbit transition        |

## Pass Transform Matrices

### Sulfur Pass (chi = 1.0)

```
d_Sulfur = Vec4(1.0, 0.8, 0.6, 0.4)

Fire-favoring: rewards action and generation.
Maximum total modifier: 1.0 * 1.0 = 1.0 (fire element)
Minimum total modifier: 0.4 * 1.0 = 0.4 (earth element)
```

### Mercury Pass (chi = 0.809)

```
d_Mercury = Vec4(0.6, 1.0, 0.8, 0.4)

Air-favoring: rewards connection and analysis.
Maximum total modifier: 1.0 * 0.809 = 0.809 (air element)
Minimum total modifier: 0.4 * 0.809 = 0.324 (earth element)
```

### Salt Pass (chi = 0.618)

```
d_Salt = Vec4(0.4, 0.6, 0.8, 1.0)

Earth-favoring: rewards structure and compression.
Maximum total modifier: 1.0 * 0.618 = 0.618 (earth element)
Minimum total modifier: 0.4 * 0.618 = 0.247 (fire element)
```

## Worked Examples

### Example 1: Fire-dominant quest at S07 (Alchemical Forge), Sulfur Pass

```
Quest element_vector = Vec4(0.8, 0.1, 0.05, 0.05)

payout_F = 64 * 1.5 * 0.8 * 1.0 * 1.0 = 76.80
payout_A = 64 * 1.5 * 0.1 * 0.8 * 1.0 =  7.68
payout_W = 64 * 1.5 * 0.05 * 0.6 * 1.0 = 2.88
payout_E = 64 * 1.5 * 0.05 * 0.4 * 1.0 = 1.92

payout_total = 76.80 + 7.68 + 2.88 + 1.92 = 89.28 XP
```

### Example 2: Balanced quest at S13 (PhiStorm Eye), Salt Pass

```
Quest element_vector = Vec4(0.25, 0.25, 0.25, 0.25)

payout_F = 64 * 2.0 * 0.25 * 0.4 * 0.618 =  7.91
payout_A = 64 * 2.0 * 0.25 * 0.6 * 0.618 = 11.87
payout_W = 64 * 2.0 * 0.25 * 0.8 * 0.618 = 15.82
payout_E = 64 * 2.0 * 0.25 * 1.0 * 0.618 = 19.78

payout_total = 7.91 + 11.87 + 15.82 + 19.78 = 55.38 XP
```

### Example 3: Water-dominant quest at S10 (Shadow Well), Mercury Pass

```
Quest element_vector = Vec4(0.05, 0.1, 0.75, 0.1)

payout_F = 64 * 1.8 * 0.05 * 0.6 * 0.809 =  2.80
payout_A = 64 * 1.8 * 0.1  * 1.0 * 0.809 =  9.32
payout_W = 64 * 1.8 * 0.75 * 0.8 * 0.809 = 55.91
payout_E = 64 * 1.8 * 0.1  * 0.4 * 0.809 =  3.73

payout_total = 2.80 + 9.32 + 55.91 + 3.73 = 71.76 XP
```

## Amplifier Application

The raw payout is further modified by the level amplifier:

```
final_payout = payout_total * amp(level)

Where amp(level) = 1 + φ⁻¹ * log_φ(1 + level)

Example at level 19:
  amp(19) ≈ 2.43
  final_payout = 89.28 * 2.43 = 216.95 XP
```

## PhiStorm Bonus

During an active PhiStorm (at S13), payouts receive additional multipliers:

```
storm_payout = final_payout * φ² * storm_intensity

Where:
  φ² ≈ 2.618
  storm_intensity in [0.0, 1.0]

Maximum storm payout at S13 with balanced quest, level 19:
  base: 55.38 * 2.43 * 2.618 * 1.0 = 352.14 XP
```

## Payout Distribution Summary

### By Station (average across balanced quest, Sulfur pass)

```
S01:  44.80    S07:  67.20    S13:  89.60
S02:  35.84    S08:  58.24    S14:  58.24
S03:  40.32    S09:  44.80    S15:  49.28
S04:  49.28    S10:  80.64    S16:  67.20
S05:  53.76    S11:  62.72    S17:  35.84
S06:  44.80    S12:  53.76    S18:  44.80
                               S19:  71.68
```

### By Pass (average across all stations, balanced quest)

```
Sulfur:  sum_d = 2.8, chi = 1.0  -> effective = 2.800
Mercury: sum_d = 2.8, chi = 0.809 -> effective = 2.265
Salt:    sum_d = 2.8, chi = 0.618 -> effective = 1.730

Ratio Sulfur:Mercury:Salt = 1.00 : 0.809 : 0.618
(Exactly the chi values, as expected)
```

## Economy Balance Targets

```
XP minted per orbit (all 57 loops):
  Low estimate:   ~3,200 XP  (conservative play)
  Medium estimate: ~6,400 XP  (standard play)
  High estimate:  ~12,800 XP  (aggressive + storm)

XP needed for full L19 unlock: ~433,160 XP
Orbits to reach L19: ~34-68 orbits (medium play)
```

## Invariants

1. BASE_XP = 64 is immutable
2. All payout components are non-negative
3. payout_total is always positive for any non-zero element vector
4. Storm bonus applies only at S13 during active PhiStorm
5. Amplifier is always >= 1.0 (payouts never decrease with level)
6. Pass chi values are fixed: {1.0, 0.809, 0.618}

## Suggested chapter anchors

- `Ch08` — Synchronization calculus
- `Ch12` — Legality certificates and closure
- `Ch18` — Macro invariants and universal math stack
