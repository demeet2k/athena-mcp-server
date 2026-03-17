# LP-57Omega Agent Ledger v2

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `data-schema`
- Role tags: `ledger, accounting, audit, traceability`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the agent ledger schema: the per-action accounting record that tracks every meaningful operation across the LP-57Omega system. The ledger is the single source of truth for audit, replay, and verification.

## Ledger Entry Schema

```typescript
interface LedgerEntry {
  // === Identity ===
  entry_id:         string;    // Unique entry ID (UUID v7, time-ordered)
  agent_id:         string;    // Master agent ID: A1|A2|A3|A4
  seat_address:     string;    // 6-digit base-4 subagent address

  // === Temporal ===
  timestamp:        ISO8601;   // Wall-clock time of action
  loop_number:      int;       // Current loop within orbit (1..57)
  orbit_number:     int;       // Current orbit (monotonically increasing)
  pass_index:       int;       // 1=Sulfur, 2=Mercury, 3=Salt
  station_id:       string;    // S01..S19

  // === Spatial ===
  coordinate_stamp: Coord12;   // 12-slot liminal coordinate at action time

  // === Action ===
  action_type:      ActionType; // Enumerated action class
  action_detail:    string;     // Free-text description of specific action
  target_artifact:  string;     // ID of artifact acted upon

  // === Metrics ===
  integration_gain: float;     // [0.0, 1.0] — cross-document fusion value
  compression_gain: float;     // [0.0, 1.0] — information density increase
  truth_state:      float;     // [0.0, 1.0] — verification confidence
  novelty_gain:     float;     // [0.0, 1.0] — new information introduced
  risk_level:       float;     // [0.0, 1.0] — danger/uncertainty level

  // === Status ===
  closure_status:   ClosureStatus; // open|partial|closed|voided

  // === Extensions ===
  carry_forward_class: CarryForwardClass; // Classification for orbit transition
  pheromone_deposit:   Vec8;              // 4 positive + 4 shadow channels
  xp_awarded:          float;            // Experience points earned
  level_at_action:     int;              // Agent level when action occurred
}
```

## Enumerated Types

### ActionType

```
GENERATE     — Create new content from scratch
MERGE        — Combine multiple artifacts into one
REFINE       — Improve existing content quality
COMPRESS     — Reduce content while preserving meaning
VERIFY       — Check truth claims against evidence
BRIDGE       — Create connection between distant artifacts
PRUNE        — Remove dead or redundant content
CERTIFY      — Issue formal certification of quality
QUARANTINE   — Isolate problematic content
RECOVER      — Restore quarantined content after review
SCHEDULE     — Plan future work allocation
DELEGATE     — Assign work to subagent
ESCALATE     — Push unresolvable issue to parent
PUBLISH      — Emit content to external consumers
MIGRATE      — Transfer state across orbit boundary
STORM        — PhiStorm-triggered emergency action
ELECT        — Activate a dormant seat
RETIRE       — Permanently deactivate a seat
```

### ClosureStatus

```
OPEN     — Action initiated, not yet resolved
PARTIAL  — Action partially completed, work remains
CLOSED   — Action fully completed and verified
VOIDED   — Action cancelled or invalidated
```

### CarryForwardClass

```
NONE           — Entry does not carry forward
UNRESOLVED     — Quest incomplete, must continue next orbit
PERSISTENT     — Permanent state (level, XP) always carries
DECAYING       — Pheromone state, decays by phi-inverse per orbit
DEFERRED       — Intentionally postponed to future orbit
CONTESTED      — Under dispute, requires resolution before carry
MIGRATING      — Active migration between manuscript branches
```

## Ledger Operations

### Write Entry

```python
def write_entry(entry: LedgerEntry) -> Receipt:
    """Write a new ledger entry. Immutable once written."""
    validate(entry)                    # Schema validation
    entry.entry_id = generate_uuid_v7() # Time-ordered ID
    append_to_ledger(entry)            # Append-only storage
    receipt = compute_receipt(entry)    # Hash-based receipt
    return receipt
```

### Query Patterns

```python
# By agent
entries = ledger.query(agent_id="A1")

# By time range
entries = ledger.query(orbit=42, loop_range=(1, 19))

# By station
entries = ledger.query(station_id="S07")

# By coordinate proximity
entries = ledger.query(near_coord=target_coord, radius=0.15)

# By closure status
entries = ledger.query(closure_status="OPEN")

# By carry forward class
entries = ledger.query(carry_forward_class="UNRESOLVED")
```

### Aggregate Metrics

```python
def orbit_summary(orbit_number: int) -> OrbitSummary:
    entries = ledger.query(orbit=orbit_number)
    return OrbitSummary(
        total_actions     = len(entries),
        avg_integration   = mean(e.integration_gain for e in entries),
        avg_compression   = mean(e.compression_gain for e in entries),
        avg_truth         = mean(e.truth_state for e in entries),
        avg_novelty       = mean(e.novelty_gain for e in entries),
        max_risk          = max(e.risk_level for e in entries),
        closure_rate      = count(e.closure_status == CLOSED) / len(entries),
        carry_forward     = [e for e in entries if e.carry_forward_class != NONE],
        total_xp          = sum(e.xp_awarded for e in entries),
    )
```

## Receipt Generation

Every ledger entry produces a cryptographic receipt:

```python
def compute_receipt(entry: LedgerEntry) -> Receipt:
    """Generate tamper-evident receipt from ledger entry."""
    payload = serialize(entry)
    entry_hash = sha256(payload)
    chain_hash = sha256(previous_receipt.hash + entry_hash)
    return Receipt(
        entry_id   = entry.entry_id,
        entry_hash = entry_hash,
        chain_hash = chain_hash,
        timestamp  = entry.timestamp,
    )
```

## Carry Forward Protocol

At orbit boundary (after S19, before next S01):

```
CARRY_FORWARD(orbit_n -> orbit_n+1):
  1. Collect all entries with carry_forward_class != NONE
  2. For UNRESOLVED: create new quest in next orbit queue
  3. For PERSISTENT: copy to next orbit's initial state
  4. For DECAYING: multiply pheromone values by phi-inverse
  5. For DEFERRED: check deferral conditions, re-queue if met
  6. For CONTESTED: flag for priority review in next orbit
  7. For MIGRATING: update manuscript branch coordinates
  8. Generate orbit_digest = hash of all carry_forward entries
  9. Write MIGRATION entry to ledger
```

## Invariants

1. Ledger is append-only; entries are never modified or deleted
2. Every entry has a unique, time-ordered entry_id
3. Every entry produces exactly one receipt
4. Receipts form a hash chain (each references the previous)
5. All metric values are in [0.0, 1.0]
6. carry_forward_class is evaluated at orbit boundary only
7. The ledger digest at orbit end is deterministic given the entries

## Suggested chapter anchors

- `Ch03` — Truth corridors and witness discipline
- `Ch12` — Legality certificates and closure
- `Ch13` — Memory regeneration and persistence
- `Ch16` — Verification harnesses and replay kernels
