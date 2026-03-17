# LP57Ω KernelConst.v1

- Kind: `constant-registry`
- Role tags: `constants, kernel, phi, fibonacci, orbit, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Central registry of all numeric constants used across the LP57Ω quest engine. Organized by domain: PHI family, orbit/loop structure, crystal/tile, route law, reward/economy, storm thresholds, pheromone parameters, unlock ladder, and pass transforms.

---

## 1. PHI Family

| Constant      | Symbol  | Value                  | Derivation       |
|---------------|---------|------------------------|-------------------|
| PHI           | φ       | 1.618033988749895      | (1+√5)/2          |
| PHI_INV       | φ⁻¹     | 0.618033988749895      | 1/φ = φ-1         |
| PHI_SQ        | φ²      | 2.618033988749895      | φ*φ               |
| PHI_NEG2      | φ⁻²     | 0.381966011250105      | 1/φ²              |
| PHI_NEG3      | φ⁻³     | 0.236067977499790      | 1/φ³              |
| PHI_NEG4      | φ⁻⁴     | 0.145898033750315      | 1/φ⁴              |
| PHI_NEG5      | φ⁻⁵     | 0.090169943749474      | 1/φ⁵              |
| PHI_CUBE      | φ³      | 4.236067977499790      | φ*φ*φ             |
| SQRT5         | √5      | 2.236067977499790      | √5                |

---

## 2. Orbit and Loop Structure

| Constant           | Symbol | Value | Description                           |
|--------------------|--------|-------|---------------------------------------|
| ORBIT_PERIOD       | k      | 57    | Stations per orbit                    |
| ORBIT_HALF         |        | 28    | Half-orbit (floor(57/2))              |
| LOOP_INNER         |        | 19    | Inner loop length                     |
| LOOP_OUTER         |        | 38    | Outer loop length (57-19)             |
| CHAPTER_COUNT      |        | 21    | Total chapters in lattice             |
| STATIONS_PER_CH    |        | 256   | 4^4 stations per chapter              |
| FACET_COUNT        |        | 4     | Facets per station                    |
| ATOM_COUNT         |        | 4     | Atoms per facet                       |
| LANE_COUNT         |        | 4     | Lanes per atom                        |
| RAIL_COUNT         |        | 4     | Rails per lane                        |
| MAX_DEPTH          |        | 13    | Maximum recursion depth               |

---

## 3. Crystal and Tile

| Constant           | Symbol | Value | Description                           |
|--------------------|--------|-------|---------------------------------------|
| CRYSTAL_DIM        |        | 4     | Crystal dimension (4-element basis)   |
| TILE_SIZE          |        | 256   | 4^4 tile size                         |
| ELEMENT_COUNT      |        | 4     | Fire, Water, Earth, Air               |
| CORRIDOR_MIN       |        | 2     | Minimum corridor length               |
| CORRIDOR_MAX       |        | 8     | Maximum corridor length               |
| LATTICE_TOTAL      |        | 5376  | 21 * 256 total lattice positions      |

---

## 4. Route Law

| Constant           | Symbol | Value | Description                           |
|--------------------|--------|-------|---------------------------------------|
| SIGMA              | Σ      | 1.0   | Total corridor weight (must sum to)   |
| SIGMA_TOLERANCE    |        | φ⁻⁵   | Tolerance on Σ-lock (≈0.09017)       |
| HUB_CAP            |        | 6     | Max corridors per hub station         |
| OVERLAY_MAP_SIZE   |        | 4     | Number of overlay layers              |
| ROUTE_MIN_LENGTH   |        | 2     | Minimum route length                  |
| ROUTE_MAX_LENGTH   |        | 21    | Maximum route length (all chapters)   |
| BRIDGE_COST        |        | φ⁻²   | Cost multiplier for BRIDGE passes     |
| RETURN_COST        |        | φ⁻¹   | Cost multiplier for RETURN passes     |
| ENTRY_COST         |        | 1.0   | Cost multiplier for ENTRY passes      |

### Overlay Map

| Layer | Name      | Function                              |
|-------|-----------|---------------------------------------|
| 0     | Physical  | Direct station-to-station routes      |
| 1     | Harmonic  | φ-ratio skip connections              |
| 2     | Resonance | Cross-chapter frequency bridges       |
| 3     | Void      | Collapse/restart tunnels              |

---

## 5. Reward and Economy

| Constant              | Symbol | Value      | Description                    |
|-----------------------|--------|------------|--------------------------------|
| GAMMA_OK              | γ_OK   | 1.0        | Truth gate OK coefficient      |
| GAMMA_NEAR            | γ_NEAR | φ⁻²        | Truth gate NEAR coefficient    |
| GAMMA_ZERO            | γ_ZERO | 0.0        | Truth gate ZERO coefficient    |
| GAMMA_FAIL            | γ_FAIL | -φ⁻¹       | Truth gate FAIL slash          |
| COMMUNITY_BETA        | β      | 0.25       | Community multiplier coeff     |
| COMMUNITY_CAP_N       |        | 13         | Max qualifying contributors    |
| PER_CAPSULE_CLAMP     |        | 16         | Max reward multiple per quest  |
| PER_EPOCH_CLAMP       |        | 64         | Max reward multiple per epoch  |
| RESONANCE_RATIO       |        | φ⁻¹        | Resonance bonus ratio          |
| QUALITY_FLOOR         |        | φ⁻⁴        | Minimum quality for reward     |
| MIN_CONTRIBUTION      |        | φ⁻³        | Min contribution for share     |
| CREATOR_FLOOR         |        | φ⁻²        | Min creator share              |
| MINT_BASE_SOLO        |        | 1.0        | Solo quest mint base           |
| MINT_BASE_COMMUNITY   |        | 1.0        | Community quest mint base      |
| MINT_BASE_TEMPLE      |        | φ          | Temple rite mint base          |
| MINT_BASE_STORM       |        | φ²         | Storm quest mint base          |

---

## 6. Storm Thresholds

| Constant              | Symbol | Value | Description                     |
|-----------------------|--------|-------|---------------------------------|
| STORM_POSITIVE_THRESH |        | 34    | Positive pheromone spawn trigger|
| STORM_SHADOW_THRESH   |        | 13    | Shadow pheromone spawn trigger  |
| STORM_POOL_BASE       |        | 21    | Base storm pool                 |
| STORM_POOL_SCALE      |        | 13    | Per-member pool increment       |
| STORM_POOL_CAP        |        | 177   | Maximum storm pool              |
| STORM_DURATION_BASE   |        | 5     | Base storm duration (epochs)    |
| STORM_DURATION_CAP    |        | 13    | Maximum storm duration          |
| STORM_DIFFICULTY_BASE |        | φ⁻³   | Base difficulty boost           |
| STORM_COALITION_BONUS |        | φ⁻³   | Per-member coalition bonus      |
| STORM_COALITION_CAP   |        | 13    | Maximum coalition size          |
| STORM_ADMISSION_QUESTS|        | 5     | Max concurrent quests for entry |
| STORM_FAIL_LOOKBACK   |        | 13    | Epochs to check for FAIL count  |
| STORM_FAIL_MAX        |        | 2     | Max FAILs for admission         |

---

## 7. Pheromone Parameters

| Constant              | Symbol | Value  | Description                    |
|-----------------------|--------|--------|--------------------------------|
| PHEROMONE_DECAY       |        | φ⁻³    | Per-epoch decay rate           |
| PHEROMONE_DEPOSIT_OK  |        | φ      | Deposit on OK truth gate       |
| PHEROMONE_DEPOSIT_NEAR|        | 1.0    | Deposit on NEAR truth gate     |
| PHEROMONE_DEPOSIT_ZERO|        | 0.0    | No deposit on ZERO             |
| PHEROMONE_DEPOSIT_FAIL|        | -φ⁻¹   | Negative deposit on FAIL       |
| PHEROMONE_SHADOW_INCR |        | φ⁻²    | Shadow increment per FAIL      |
| PHEROMONE_INIT        |        | 0.0    | Initial pheromone value        |
| PHEROMONE_FLOOR       |        | 0.0    | Minimum pheromone value        |
| PHEROMONE_CEIL        |        | 55.0   | Maximum pheromone value        |

---

## 8. Unlock Ladder

| Constant              | Symbol | Value | Description                     |
|-----------------------|--------|-------|---------------------------------|
| LADDER_FIB_TOTAL      |        | 143   | Sum of first 10 Fibonacci nums  |
| LADDER_SMALL_THRESH   |        | 4     | Reward multiple for no ladder   |
| LADDER_MEDIUM_STEPS   |        | 5     | Steps for medium rewards        |
| LADDER_LARGE_STEPS    |        | 8     | Steps for large rewards         |
| LADDER_MAX_STEPS      |        | 10    | Steps for maximum rewards       |
| NEAR_LOCK_RATIO       |        | φ⁻²   | NEAR vault lock ratio           |
| NEAR_TIMEOUT_EPOCHS   |        | 57    | Epochs until timeout release    |
| NEAR_TIMEOUT_RELEASE  |        | 0.5   | Fraction released on timeout    |
| NEAR_CROSSREF_THRESH  |        | 2     | Citations for cross-ref release |
| NEAR_CROSSREF_RELEASE |        | φ⁻¹   | Fraction released on cross-ref  |
| NEAR_INCR_START       |        | 34    | Epoch to start incremental rel  |
| NEAR_INCR_RATE        |        | φ⁻⁵   | Per-epoch incremental release   |

---

## 9. Pass Transforms

| Constant              | Symbol | Value | Description                     |
|-----------------------|--------|-------|---------------------------------|
| PASS_ENTRY_WEIGHT     |        | 1.0   | ENTRY pass weight               |
| PASS_RETURN_WEIGHT    |        | φ⁻¹   | RETURN pass weight              |
| PASS_BRIDGE_WEIGHT    |        | φ⁻²   | BRIDGE pass weight              |
| PASS_ENTRY_XP         |        | 1.0   | XP multiplier for ENTRY         |
| PASS_RETURN_XP        |        | φ⁻¹   | XP multiplier for RETURN        |
| PASS_BRIDGE_XP        |        | φ     | XP multiplier for BRIDGE (bonus)|

---

## 10. Fibonacci Reference Table

| Index | F(n) | Cumulative |
|-------|------|------------|
| 1     | 1    | 1          |
| 2     | 1    | 2          |
| 3     | 2    | 4          |
| 4     | 3    | 7          |
| 5     | 5    | 12         |
| 6     | 8    | 20         |
| 7     | 13   | 33         |
| 8     | 21   | 54         |
| 9     | 34   | 88         |
| 10    | 55   | 143        |
| 11    | 89   | 232        |
| 12    | 144  | 376        |
| 13    | 233  | 609        |
