# LP57Ω Infinite-Cap Orbit Law

- Kind: `mathematical-specification`
- Role tags: `leveling, orbit, XP, infinite-cap, phi-scaling, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the infinite-cap level system based on the orbit period k=57. Covers the level formula, XP threshold progression scaled by φ, the amplifier function, orbit decomposition, and station-pass mapping.

---

## 1. Level Formula

### Definition

```
level = 57k + ℓ
```

Where:
- **k** = orbit index (0, 1, 2, 3, ...) — unbounded
- **ℓ** = station within orbit (0, 1, 2, ..., 56)

### Properties

- Level 0 corresponds to orbit 0, station 0
- Level 57 corresponds to orbit 1, station 0
- Level 114 corresponds to orbit 2, station 0
- There is no level cap — orbits extend infinitely

### Decomposition

```python
def decompose_level(level):
    k = level // 57       # orbit index
    ell = level % 57      # station within orbit
    return (k, ell)
```

---

## 2. XP Threshold

### Formula

```
XP(n) = BASE_XP * φ^(n / 19)
```

Where:
- **BASE_XP** = 100 (configurable base)
- **n** = target level
- **φ** = 1.618033988749895
- The exponent divides by 19 (inner loop length), creating a φ-scaled progression where every 19 levels multiplies the threshold by φ

### XP Threshold Table (Selected Levels)

| Level | Orbit.Station | XP Threshold           | Ratio to Previous |
|-------|--------------|------------------------|-------------------|
| 0     | 0.0          | 100.000                | —                 |
| 1     | 0.1          | 100 * φ^(1/19)         | ≈ 1.0255          |
| 19    | 0.19         | 100 * φ                | ≈ 161.80          |
| 38    | 0.38         | 100 * φ²               | ≈ 261.80          |
| 57    | 1.0          | 100 * φ³               | ≈ 423.61          |
| 76    | 1.19         | 100 * φ⁴               | ≈ 685.41          |
| 114   | 2.0          | 100 * φ⁶               | ≈ 1793.07         |
| 171   | 3.0          | 100 * φ⁹               | ≈ 12291.70        |
| 228   | 4.0          | 100 * φ¹²              | ≈ 84279.10        |
| 570   | 10.0         | 100 * φ³⁰              | ≈ 1.3467e6        |

### Growth Rate

Every 19 levels: XP threshold multiplies by φ ≈ 1.618.
Every 57 levels (1 orbit): XP threshold multiplies by φ³ ≈ 4.236.

### Cumulative XP to Reach Level n

```
XP_cumulative(n) = Σ_{i=0}^{n-1} BASE_XP * φ^(i/19)
```

This is a geometric series with ratio r = φ^(1/19):

```
XP_cumulative(n) = BASE_XP * (r^n - 1) / (r - 1)
```

---

## 3. Amplifier Function

### Definition

```
A(level) = 1 + φ⁻¹ * log_φ(1 + level)
```

Where:
- **φ⁻¹** ≈ 0.618034 — the golden ratio inverse
- **log_φ(x)** = ln(x) / ln(φ) — logarithm base φ

### Properties

- A(0) = 1 + φ⁻¹ * log_φ(1) = 1 + 0 = 1.0
- A(1) = 1 + φ⁻¹ * log_φ(2) ≈ 1 + 0.618 * 1.4404 ≈ 1.890
- Grows logarithmically — never diverges but always increases
- Provides diminishing returns at higher levels

### Amplifier Table

| Level | log_φ(1+level) | Amplifier A(level) |
|-------|----------------|-------------------|
| 0     | 0.000          | 1.000             |
| 1     | 1.440          | 1.890             |
| 5     | 3.720          | 3.300             |
| 10    | 4.983          | 4.081             |
| 19    | 6.228          | 4.851             |
| 57    | 8.423          | 6.207             |
| 100   | 9.594          | 6.931             |
| 228   | 11.268         | 7.966             |
| 570   | 13.161         | 9.137             |
| 1000  | 14.349         | 9.872             |

### Application

The amplifier scales XP gains and reward factors:

```
effective_xp_gain = raw_xp_gain * A(level)
effective_reward = base_reward * A(level) * other_factors
```

This means higher-level agents earn slightly more XP per action but with diminishing returns, keeping the system balanced at all scales.

---

## 4. Orbit Decomposition

### Orbit Structure

Each orbit of 57 stations decomposes into three loops:

```
Orbit(k) = InnerLoop(k) ∪ MidLoop(k) ∪ OuterLoop(k)
```

| Loop        | Stations           | Length | Character              |
|-------------|-------------------|--------|------------------------|
| InnerLoop   | ℓ ∈ [0, 18]       | 19     | Foundation, core skills |
| MidLoop     | ℓ ∈ [19, 37]      | 19     | Expansion, community   |
| OuterLoop   | ℓ ∈ [38, 56]      | 19     | Mastery, teaching      |

### Loop Properties

- Each loop has exactly 19 stations (matching the XP exponent divisor)
- Completing a full loop multiplies cumulative XP by φ
- Completing a full orbit multiplies cumulative XP by φ³

### Orbit Milestones

| Milestone              | Condition         | Reward                        |
|-----------------------|-------------------|-------------------------------|
| Loop completion       | ℓ = 18, 37, or 56| Bonus = BASE_XP * φ^(loop#)  |
| Orbit completion      | ℓ = 56            | Orbit bonus = BASE_XP * φ³   |
| Multi-orbit milestone | k mod 3 = 0       | Tier bonus = BASE_XP * φ^(k) |

---

## 5. Station-Pass Mapping

### Pass Type Assignment

Each station within an orbit has a deterministic pass type based on its position:

```python
def station_pass(ell):
    if ell % 19 == 0:
        return Pass3.ENTRY       # Loop entry points
    elif ell in hub_stations(ell):
        return Pass3.BRIDGE      # Hub crossings
    else:
        return Pass3.RETURN      # Standard progression
```

### Hub Stations

Hub stations occur at φ-ratio positions within each loop:

```python
def hub_stations(loop_start):
    hubs = []
    for i in range(1, 6):  # Up to HUB_CAP
        pos = loop_start + round(19 * (1 - PHI_INV**i))
        if pos < loop_start + 19:
            hubs.append(pos)
    return hubs
```

### Hub Station Table (Loop 0, stations 0-18)

| Station | Position Formula          | Pass Type | Hub? |
|---------|---------------------------|-----------|------|
| 0       | Loop entry                | ENTRY     | No   |
| 7       | round(19 * (1 - φ⁻¹))    | BRIDGE    | Yes  |
| 12      | round(19 * (1 - φ⁻²))    | BRIDGE    | Yes  |
| 14      | round(19 * (1 - φ⁻³))    | BRIDGE    | Yes  |
| 16      | round(19 * (1 - φ⁻⁴))    | BRIDGE    | Yes  |
| 17      | round(19 * (1 - φ⁻⁵))    | BRIDGE    | Yes  |
| Others  | —                         | RETURN    | No   |

### Pass Weight Impact

| Pass Type | XP Multiplier | Route Cost | Description               |
|-----------|--------------|------------|---------------------------|
| ENTRY     | 1.0          | 1.0        | Standard first traversal   |
| RETURN    | φ⁻¹          | φ⁻¹        | Revisit with reduced yield |
| BRIDGE    | φ             | φ⁻²        | High XP, low cost hub hop  |

---

## 6. Level-Dependent Unlocks

### Unlock Thresholds

| Level | Orbit.Station | Unlock                              |
|-------|--------------|-------------------------------------|
| 0     | 0.0          | Basic quests, solo class            |
| 19    | 0.19         | Community quest participation       |
| 38    | 0.38         | Storm participation                 |
| 57    | 1.0          | Temple rite eligibility             |
| 76    | 1.19         | Witness certification               |
| 114   | 2.0          | Quest creation (any class)          |
| 171   | 3.0          | Storm coalition leadership          |
| 228   | 4.0          | Temple certification authority      |
| 285   | 5.0          | Governance voting rights            |
| 570   | 10.0         | Full system authority               |

### Level Check

```python
def has_unlock(agent_level, required_level):
    return agent_level >= required_level
```
