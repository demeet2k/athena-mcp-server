# LP57Ω Guild Hall and Temple Registry Containers

- Kind: `container-schema`
- Role tags: `guild-hall, temple, board, registry, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the GuildHallBoard and TempleRegistry container schemas: their fields, sort keys, population rules, capacity limits, and query interfaces. These containers serve as the primary operational surfaces for quest management and temple governance.

---

## Part I: GuildHallBoard

### 1. Schema

```typescript
interface GuildHallBoard {
  board_kind:            "GUILD_HALL";
  guild_id:              string;           // Unique guild identifier
  guild_name:            string;           // Display name
  element_affinity:      Element4;         // Guild's primary element
  tier:                  uint;             // Guild tier (orbit-based)

  // Quest Queues
  open_quests:           QuestSlot[];      // Solo quests available for claim
  open_community_quests: QuestSlot[];      // Community quests seeking members
  active_storms:         StormSlot[];      // Currently active storm events

  // Metrics
  total_completed:       uint;             // Lifetime completed quests
  epoch_completed:       uint;             // Quests completed this epoch
  pheromone_summary:     Vec4;             // Element-wise pheromone averages

  // Ordering
  sort_key:              string;           // Deterministic sort key
  last_updated:          ISO8601;
  epoch:                 uint;
  digest:                string;           // SHA-256 of board state
}
```

### 2. QuestSlot

```typescript
interface QuestSlot {
  quest_id:         string;
  quest_class:      QuestClass;
  element:          Element4;
  status:           QuestStatus;
  corridor_length:  uint;
  slots_available:  uint;            // For community: remaining slots
  slots_total:      uint;            // For community: total slots
  truth_gate:       Truth4 | null;   // null if not yet evaluated
  priority:         number;          // Computed sort priority
  listed_at:        ISO8601;
  epoch_listed:     uint;
}
```

### 3. StormSlot

```typescript
interface StormSlot {
  storm_id:         string;
  storm_state:      StormState;
  coalition_size:   uint;
  coalition_cap:    uint;            // 13
  pool_current:     number;
  difficulty:       number;
  epochs_remaining: uint;
  corridor_id:      string;
  element:          Element4;
  priority:         number;
  spawned_at:       ISO8601;
}
```

### 4. Sort Key

The sort key determines display order on the board.

```
sort_key = f"{element_code}:{epoch_listed:08d}:{priority:012.6f}:{quest_id}"
```

Element codes: `F=Fire, W=Water, E=Earth, A=Air`

### Sort Priority Formula

```
priority(quest) = (
    age_weight * epoch_age +
    element_weight * element_match +
    class_weight * class_rank +
    urgency_weight * urgency_score
)
```

| Factor          | Weight         | Description                         |
|-----------------|----------------|-------------------------------------|
| age_weight      | 1.0            | Older quests sort higher            |
| element_weight  | φ⁻¹            | Matching guild element gets boost   |
| class_weight    | φ⁻²            | Storm > TempleRite > Community > Solo|
| urgency_weight  | φ⁻³            | Dependency-blocked quests get boost |

### Class Rank Values

| Quest Class  | Rank |
|-------------|------|
| Solo        | 1    |
| Community   | 2    |
| TempleRite  | 3    |
| Storm       | 4    |

### 5. Capacity Limits

| Queue                  | Max Items | Overflow Behavior              |
|------------------------|-----------|-------------------------------|
| open_quests            | 57        | Oldest archived               |
| open_community_quests  | 34        | Oldest archived               |
| active_storms          | 8         | No new storms until slot opens|

### 6. Board Refresh

The board refreshes at epoch boundaries:

```python
def refresh_guild_board(board):
    # Remove completed/archived quests
    board.open_quests = [q for q in board.open_quests
                         if q.status in ["DRAFT", "ACTIVE"]]
    board.open_community_quests = [q for q in board.open_community_quests
                                    if q.status in ["DRAFT", "ACTIVE"]
                                    and q.slots_available > 0]
    board.active_storms = [s for s in board.active_storms
                           if s.storm_state in ["BREWING", "ACTIVE", "WANING"]]

    # Update metrics
    board.epoch_completed = count_completed_this_epoch(board.guild_id)
    board.pheromone_summary = compute_pheromone_summary(board.guild_id)

    # Recompute sort keys
    for slot in board.open_quests + board.open_community_quests:
        slot.priority = compute_priority(slot, board)

    board.last_updated = now()
    board.epoch = current_epoch()
    board.digest = sha256(canonical(board))
```

### 7. Query Interface

```typescript
interface GuildBoardQuery {
  guild_id:       string;
  element_filter: Element4 | null;      // Filter by element
  class_filter:   QuestClass | null;    // Filter by quest class
  status_filter:  QuestStatus | null;   // Filter by status
  min_priority:   number | null;        // Minimum priority threshold
  limit:          uint;                 // Max results (default 21)
  offset:         uint;                 // Pagination offset
  sort_by:        "priority" | "age" | "element" | "class";
}
```

---

## Part II: TempleRegistry

### 1. Schema

```typescript
interface TempleRegistry {
  registry_kind:         "TEMPLE";
  temple_id:             string;           // Unique temple identifier
  temple_name:           string;           // Display name
  sacred_corridors:      Corridor[];       // Temple's designated corridors
  certifiers:            string[];         // Agent IDs with certification authority

  // Queues
  open_rites:            RiteSlot[];       // Temple rite quests available
  certification_queue:   CertSlot[];       // Awaiting certification
  ethics_watchlist:      EthicsSlot[];     // Flagged for ethical review
  invariant_backlog:     InvariantSlot[];  // Invariant violations pending

  // Metrics
  total_certified:       uint;             // Lifetime certifications
  epoch_certified:       uint;             // This epoch
  grace_field:           number;           // Average grace across rites
  resonance_field:       number;           // Average resonance

  // Ordering
  sort_key:              string;
  last_updated:          ISO8601;
  epoch:                 uint;
  digest:                string;
}
```

### 2. RiteSlot

```typescript
interface RiteSlot {
  quest_id:         string;
  status:           QuestStatus;
  element:          Element4;
  corridor:         Corridor;
  grace_score:      number;           // [0.0, 1.0]
  resonance_score:  number;           // [0.0, 1.0]
  witness_count:    uint;
  certified:        boolean;
  priority:         number;
  listed_at:        ISO8601;
}
```

### 3. CertSlot

```typescript
interface CertSlot {
  quest_id:         string;
  entered_queue:    ISO8601;
  epoch_entered:    uint;
  age_epochs:       uint;              // current_epoch - epoch_entered
  certifier_assigned: string | null;   // null if unassigned
  grace_weight:     number;            // φ⁻¹ * grace_score
  resonance_weight: number;            // φ⁻² * resonance_score
  priority:         number;            // age + grace_weight + resonance_weight
  timeout_at:       uint;              // epoch_entered + 13
  escalated:        boolean;
}
```

### 4. EthicsSlot

```typescript
interface EthicsSlot {
  quest_id:         string;
  flag_type:        string;            // From TemplePolicy flag triggers
  severity:         "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  flagged_at:       ISO8601;
  epoch_flagged:    uint;
  reviewer_ids:     string[];
  cleared:          boolean;
  cleared_at:       ISO8601 | null;
  auto_clear_epoch: uint | null;       // For LOW severity
}
```

### 5. InvariantSlot

```typescript
interface InvariantSlot {
  quest_id:         string;
  invariant_code:   string;            // INV-C, INV-T, INV-R, INV-E, INV-Q, INV-O
  detected_at:      ISO8601;
  epoch_detected:   uint;
  age_epochs:       uint;
  remediation_ref:  string | null;
  resolved:         boolean;
  resolved_at:      ISO8601 | null;
  deadline_epoch:   uint;              // epoch_detected + 21
}
```

### 6. Sort Key

```
sort_key = f"TEMPLE:{priority:012.6f}:{epoch_entered:08d}:{quest_id}"
```

### Certification Priority

```
priority = epoch_age + φ⁻¹ * grace_score + φ⁻² * resonance_score
```

Escalated items receive a flat boost of φ.

### 7. Capacity Limits

| Queue                  | Max Items | Overflow Behavior                |
|------------------------|-----------|----------------------------------|
| open_rites             | 34        | Oldest archived                  |
| certification_queue    | 21        | Escalation to ethics on overflow |
| ethics_watchlist       | 13        | Force-block oldest if overflow   |
| invariant_backlog      | 8 per quest, 55 total | Force-archive on overflow |

### 8. Registry Refresh

```python
def refresh_temple_registry(registry):
    # Update certification queue ages
    for slot in registry.certification_queue:
        slot.age_epochs = current_epoch() - slot.epoch_entered
        slot.priority = (slot.age_epochs +
                        PHI_INV * slot.grace_weight +
                        PHI_NEG2 * slot.resonance_weight)
        if slot.age_epochs >= 13 and not slot.escalated:
            slot.escalated = True
            slot.priority += PHI
            escalate_to_ethics(registry, slot)

    # Clear expired ethics items
    for slot in registry.ethics_watchlist:
        if (slot.severity == "LOW" and
            current_epoch() >= slot.auto_clear_epoch):
            slot.cleared = True
            slot.cleared_at = now()

    # Check invariant deadlines
    for slot in registry.invariant_backlog:
        slot.age_epochs = current_epoch() - slot.epoch_detected
        if slot.age_epochs > 21 and not slot.resolved:
            force_archive_quest(slot.quest_id, "INVARIANT_TIMEOUT")

    # Update metrics
    registry.epoch_certified = count_certified_this_epoch(registry.temple_id)
    registry.grace_field = avg_grace(registry.open_rites)
    registry.resonance_field = avg_resonance(registry.open_rites)

    registry.last_updated = now()
    registry.epoch = current_epoch()
    registry.digest = sha256(canonical(registry))
```

### 9. Query Interface

```typescript
interface TempleRegistryQuery {
  temple_id:       string;
  queue:           "rites" | "certification" | "ethics" | "invariants";
  severity_filter: string | null;
  resolved_filter: boolean | null;
  limit:           uint;
  offset:          uint;
  sort_by:         "priority" | "age" | "severity";
}
```

---

## Interaction Model

Guild Hall generates work items. Temple validates them. A quest may pass through both:

1. Guild board assigns and executes the quest
2. Temple board certifies the result (for TempleRite class)
3. Receipt chain seals the outcome
4. Published quests are archived from both boards
