# LP57Ω Typed Economic ABI

- Kind: `type-system`
- Role tags: `ABI, enums, types, economic-model, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the complete typed Application Binary Interface for the LP57Ω economic layer. All enums, shared types, quest objects, storm/pheromone objects, reward/settlement objects, and board containers are specified here as the single source of truth.

---

## 1. Enumerations

### Truth4

Truth gate evaluation outcomes.

```typescript
enum Truth4 {
  OK   = "OK",     // Full truth — γ = 1.0
  NEAR = "NEAR",   // Partial truth — γ = φ⁻² ≈ 0.381966
  ZERO = "ZERO",   // No truth — γ = 0.0
  FAIL = "FAIL"    // Violation — negative consequence
}
```

### Pass3

Pass types for station traversal.

```typescript
enum Pass3 {
  ENTRY  = "ENTRY",   // First traversal of a station
  RETURN = "RETURN",  // Re-traversal after departure
  BRIDGE = "BRIDGE"   // Cross-corridor transfer pass
}
```

### Element4

Elemental classification for quests and corridors.

```typescript
enum Element4 {
  FIRE  = "FIRE",    // Transformation, initiation
  WATER = "WATER",   // Flow, connection, healing
  EARTH = "EARTH",   // Structure, certification, grounding
  AIR   = "AIR"      // Communication, distribution, speed
}
```

### QuestClass

Quest classification determining lifecycle rules.

```typescript
enum QuestClass {
  SOLO       = "SOLO",
  COMMUNITY  = "COMMUNITY",
  TEMPLE_RITE = "TEMPLE_RITE",
  STORM      = "STORM"
}
```

### QuestStatus

Quest lifecycle states.

```typescript
enum QuestStatus {
  DRAFT     = "DRAFT",
  ACTIVE    = "ACTIVE",
  BLOCKED   = "BLOCKED",
  SEALED    = "SEALED",
  PUBLISHED = "PUBLISHED",
  ARCHIVED  = "ARCHIVED"
}
```

### BoardKind

Board container classifications.

```typescript
enum BoardKind {
  GUILD_HALL   = "GUILD_HALL",
  TEMPLE       = "TEMPLE",
  STORM_FRONT  = "STORM_FRONT",
  ARCHIVE      = "ARCHIVE"
}
```

### QueueName

Named queues within the system.

```typescript
enum QueueName {
  CERTIFICATION  = "CERTIFICATION",
  ETHICS         = "ETHICS",
  INVARIANT      = "INVARIANT",
  PUBLISH        = "PUBLISH",
  MIGRATION      = "MIGRATION"
}
```

### VaultState

Reward vault lifecycle states.

```typescript
enum VaultState {
  OPEN     = "OPEN",      // Accepting deposits
  LOCKED   = "LOCKED",    // Vesting in progress
  RELEASED = "RELEASED",  // Funds released to agent
  SLASHED  = "SLASHED"   // Funds revoked due to FAIL
}
```

### StormState

Storm event lifecycle states.

```typescript
enum StormState {
  BREWING   = "BREWING",    // Pheromone approaching threshold
  ACTIVE    = "ACTIVE",     // Storm in progress
  WANING    = "WANING",     // Final epoch of storm
  SETTLED   = "SETTLED",    // Rewards distributed
  EXPIRED   = "EXPIRED"     // Duration exceeded, no settlement
}
```

---

## 2. Shared Types

### Vec4

Four-element vector used for elemental weights and coordinates.

```typescript
interface Vec4 {
  fire:  number;
  water: number;
  earth: number;
  air:   number;
}
```

**Invariant**: `fire + water + earth + air = 1.0` (normalized) or unbounded (raw weights).

### Coord12

Twelve-dimensional coordinate in the chapter lattice.

```typescript
interface Coord12 {
  chapter:    uint;        // 1-21
  station:    uint;        // 0-255 (4^4 lattice position)
  facet:      uint;        // 0-3
  atom:       uint;        // 0-3
  lane:       uint;        // 0-3
  rail:       uint;        // 0-3
  depth:      uint;        // recursion depth
  epoch:      uint;        // temporal coordinate
  element:    Element4;
  pass_type:  Pass3;
  orbit:      uint;        // orbit index within level
  level:      uint;        // 57k + ℓ
}
```

### Corridor

A directed path through the chapter lattice.

```typescript
interface Corridor {
  corridor_id:  string;
  stations:     Coord12[];    // Ordered sequence
  element:      Element4;     // Dominant element
  length:       uint;
  entry_pass:   Pass3;
  exit_pass:    Pass3;
}
```

### TruthRecord

Records a truth gate evaluation.

```typescript
interface TruthRecord {
  record_id:     string;
  quest_id:      string;
  gate:          Truth4;
  gamma:         number;       // γ value: 1.0 | φ⁻² | 0.0
  evaluator_id:  string;
  evidence_ref:  string;       // Reference to supporting evidence
  timestamp:     ISO8601;
  epoch:         uint;
  digest:        string;       // SHA-256
}
```

### LedgerStamp

Immutable timestamp entry for ledger events.

```typescript
interface LedgerStamp {
  stamp_id:    string;
  event_type:  string;
  quest_id:    string;
  agent_id:    string;
  timestamp:   ISO8601;
  epoch:       uint;
  value:       number | null;
  digest:      string;
}
```

---

## 3. Quest Objects

### Quest

```typescript
interface Quest {
  quest_id:       string;
  quest_class:    QuestClass;
  status:         QuestStatus;
  element:        Element4;
  title:          string;
  description:    string;
  corridor:       Corridor;
  creator_id:     string;
  assignees:      string[];
  truth_record:   TruthRecord | null;
  dependencies:   string[];       // quest_ids this depends on
  created_at:     ISO8601;
  updated_at:     ISO8601;
  epoch_created:  uint;
  epoch_sealed:   uint | null;
  reward_ref:     string | null;  // Reference to RewardSettlement
}
```

### QuestDependency

```typescript
interface QuestDependency {
  source_quest:  string;
  target_quest:  string;
  dep_type:      "BLOCKS" | "INFORMS" | "REQUIRES";
  resolved:      boolean;
  resolved_at:   ISO8601 | null;
}
```

---

## 4. Storm and Pheromone Objects

### StormEvent

```typescript
interface StormEvent {
  storm_id:       string;
  state:          StormState;
  trigger_pheromone: number;     // Value that triggered spawn
  pool_base:      number;        // 21
  pool_scaled:    number;        // After participation scaling
  duration_base:  uint;          // 5 epochs
  duration_actual: uint;
  difficulty:     number;        // φ⁻³ scaled
  coalition:      CoalitionMember[];
  corridor:       Corridor;
  spawned_at:     ISO8601;
  settled_at:     ISO8601 | null;
  epoch_start:    uint;
  epoch_end:      uint | null;
}
```

### CoalitionMember

```typescript
interface CoalitionMember {
  agent_id:       string;
  joined_at:      ISO8601;
  contribution:   number;         // 0.0-1.0
  bonus:          number;         // φ⁻³ per member
  stations_completed: Coord12[];
}
```

### PheromoneField

```typescript
interface PheromoneField {
  field_id:       string;
  corridor_id:    string;
  positive:       number;         // Spawn trigger at ≥ 34
  shadow:         number;         // Shadow threshold at ≤ 13
  decay_rate:     number;         // Per-epoch decay
  last_updated:   ISO8601;
  epoch:          uint;
}
```

---

## 5. Reward and Settlement Objects

### RewardSettlement

```typescript
interface RewardSettlement {
  settlement_id:  string;
  quest_id:       string;
  quest_class:    QuestClass;
  base_reward:    number;
  truth_factor:   number;         // γ
  quality_factor: number;
  community_mult: number;         // 1 + β*N
  resonance:      number;         // φ⁻¹
  total_reward:   number;
  splits:         RewardSplit[];
  vault_state:    VaultState;
  settled_at:     ISO8601;
  epoch:          uint;
}
```

### RewardSplit

```typescript
interface RewardSplit {
  agent_id:       string;
  share:          number;         // 0.0-1.0 (proportional)
  amount:         number;
  vesting_mode:   "IMMEDIATE" | "FIBONACCI_LADDER" | "NEAR_SETTLEMENT";
  vault_ref:      string;
}
```

### VestingVault

```typescript
interface VestingVault {
  vault_id:       string;
  agent_id:       string;
  quest_id:       string;
  state:          VaultState;
  locked_amount:  number;
  released_amount: number;
  lock_ratio:     number;         // φ⁻² for NEAR
  unlock_schedule: FibonacciStep[];
  created_at:     ISO8601;
  released_at:    ISO8601 | null;
}
```

---

## 6. Board Containers

### GuildHallBoard

```typescript
interface GuildHallBoard {
  board_kind:          BoardKind.GUILD_HALL;
  guild_id:            string;
  open_quests:         Quest[];
  open_community_quests: Quest[];
  active_storms:       StormEvent[];
  pheromone_fields:    PheromoneField[];
  sort_key:            string;       // Deterministic sort
  last_updated:        ISO8601;
}
```

### TempleBoard

```typescript
interface TempleBoard {
  board_kind:          BoardKind.TEMPLE;
  temple_id:           string;
  open_rites:          Quest[];
  certification_queue: Quest[];
  ethics_watchlist:    Quest[];
  invariant_backlog:   Quest[];
  consent_receipts:    string[];     // Receipt references
  sort_key:            string;
  last_updated:        ISO8601;
}
```

### StormFrontBoard

```typescript
interface StormFrontBoard {
  board_kind:          BoardKind.STORM_FRONT;
  active_storms:       StormEvent[];
  brewing_fields:      PheromoneField[];
  coalition_roster:    CoalitionMember[];
  sort_key:            string;
  last_updated:        ISO8601;
}
```

### ArchiveBoard

```typescript
interface ArchiveBoard {
  board_kind:          BoardKind.ARCHIVE;
  published_quests:    Quest[];
  sealed_bundles:      string[];     // SealedReceiptBundle references
  total_archived:      uint;
  sort_key:            string;
  last_updated:        ISO8601;
}
```
