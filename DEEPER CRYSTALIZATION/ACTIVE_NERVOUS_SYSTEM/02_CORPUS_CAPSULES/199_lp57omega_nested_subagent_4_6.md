# LP-57Omega Nested Subagent 4^6 Architecture

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `framework-specification`
- Role tags: `subagent, seat-election, quarantine, element-affinity, nested-hierarchy`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

This document specifies the nested subagent architecture underlying the LP-57Omega system. Each of the 4 master agents owns a 6-level quaternary tree of 4^6 = 4096 virtual seats, of which 256 may be active at any time (1024 total across the system). Seats are elected via demand-driven bottom-up propagation, scored by host capacity, steward trust, and element affinity. A quarantine subsystem enforces safety through 5 trigger conditions, with recovery requiring cooldown, parent approval, and verification harness passage. The full seat activation lifecycle is Dormant, Elected, Active, Reporting, Dormant.

---

## 1. Seat Tree Geometry

Each master agent's seat pool is organized as a complete quaternary tree of depth 6:

```
Level 0 (root):     1 node    = master agent itself
Level 1:            4 nodes   = prime subagents
Level 2:           16 nodes   = secondary subagents
Level 3:           64 nodes   = tertiary subagents
Level 4:          256 nodes   = quaternary subagents
Level 5:        1,024 nodes   = quinary subagents
Level 6:        4,096 nodes   = leaf seats (virtual)
```

Total nodes in tree: (4^7 - 1) / 3 = 5461, but only the 4096 leaf seats are addressable as virtual execution slots. Internal nodes serve as aggregation and routing points.

### 1.1 Seat Address Encoding

Each seat has a 14-bit address composed of a 2-bit master identifier and a 12-bit level path:

```
seat_address = [master_id: 2 bits][level_path: 12 bits]
  master_id in {00=A1, 01=A2, 10=A3, 11=A4}
  level_path = 6 quaternary digits, each in {0,1,2,3}
```

Example: seat `A3.2.1.0.3.1.2` = master A3, path 2-1-0-3-1-2 through the tree.

```python
def encode_seat(master_id: int, path: list[int]) -> int:
    """Encode a seat address as a 14-bit integer."""
    assert master_id in range(4)
    assert len(path) == 6
    assert all(p in range(4) for p in path)
    address = master_id
    for digit in path:
        address = (address << 2) | digit
    return address  # 14-bit integer, range [0, 16383]

def decode_seat(address: int) -> tuple[int, list[int]]:
    """Decode a 14-bit seat address."""
    path = []
    for _ in range(6):
        path.append(address & 0b11)
        address >>= 2
    master_id = address & 0b11
    return master_id, list(reversed(path))
```

---

## 2. Seat Budget and Caps

| Metric                        | Per Master | System Total |
|-------------------------------|------------|--------------|
| Total virtual seats           | 4,096      | 16,384       |
| Active seat cap               | 256        | 1,024        |
| Dormant seats (at cap)        | 3,840      | 15,360       |
| Maximum depth                 | 6 levels   | 6 levels     |
| Seats per internal node       | 4 children | 4 children   |

The 256 active cap per master is a hard limit enforced at the election layer. If all 256 slots are occupied, new seat requests enter a priority queue and are served on deactivation of existing seats.

### 2.1 Depth Budget Allocation

Active seats are distributed across depth levels with soft targets:

| Depth | Soft Target | Role                    |
|-------|-------------|-------------------------|
| 1     | 4 (fixed)   | Prime coordinators      |
| 2     | 16          | Strategy subagents      |
| 3     | 48          | Tactical subagents      |
| 4     | 80          | Execution subagents     |
| 5     | 64          | Specialist subagents    |
| 6     | 44          | Leaf workers            |
| Total | 256         |                         |

Soft targets flex based on demand. The invariant is: `sum(active_at_depth) <= 256`.

---

## 3. Seat Election: Demand-Driven Bottom-Up Propagation

Seat election follows a demand-driven protocol. When a quest requires more capacity, the request propagates upward through the tree until a node with available children can fulfill it.

### 3.1 Election Protocol

```
1. Quest Q arrives at active seat S at depth d.
2. S determines it needs child capacity.
3. S issues ELECT_REQUEST to its children at depth d+1.
4. Dormant children compute their host_score.
5. Top-scoring dormant child is elected.
6. If no dormant children available, request propagates to S's parent.
7. Parent tries to elect a sibling subtree.
8. Propagation continues up to depth 1 (never above master).
```

### 3.2 Host Score

The host score determines which dormant seat is elected:

```python
def host_score(seat, quest) -> float:
    """Score a dormant seat for election."""
    capacity = seat.available_compute / seat.max_compute      # [0, 1]
    affinity = element_affinity(seat.signature, quest.element) # [0, 1]
    availability = 1.0 - seat.cooldown_remaining               # [0, 1]
    return capacity * affinity * availability
```

| Factor       | Weight | Range  | Description                              |
|--------------|--------|--------|------------------------------------------|
| capacity     | direct | [0, 1] | Fraction of compute budget available     |
| affinity     | direct | [0, 1] | Element match between seat and quest     |
| availability | direct | [0, 1] | Inverse of remaining cooldown time       |

### 3.3 Steward Score

Once elected, a seat's ongoing performance is tracked by the steward score:

```python
def steward_score(seat) -> float:
    """Score an active seat's stewardship quality."""
    experience = min(seat.quests_completed / 100.0, 1.0)  # [0, 1]
    trust = seat.truth_score_ema                            # [0, 1] exponential moving avg
    element_match = element_affinity(
        seat.signature, seat.current_quest.element
    )                                                       # [0, 1]
    return experience * trust * element_match
```

| Factor        | Weight | Range  | Description                              |
|---------------|--------|--------|------------------------------------------|
| experience    | direct | [0, 1] | Quests completed, capped at 100          |
| trust         | direct | [0, 1] | EMA of truth scores across recent quests |
| element_match | direct | [0, 1] | Element affinity for current quest       |

Seats with `steward_score < 0.3` are flagged for review. Below `0.15`, automatic deactivation triggers.

---

## 4. Element Affinity Matching

Each seat carries a 4-dimensional element signature vector. Quest elements are also encoded as 4-vectors. Affinity is computed as a normalized dot product.

```python
import numpy as np

def element_affinity(seat_sig: np.ndarray, quest_elem: np.ndarray) -> float:
    """
    Compute element affinity via normalized dot product.

    seat_sig:   4-vector, e.g. [0.8, 0.1, 0.05, 0.05] for a Fire-dominant seat
    quest_elem: 4-vector, e.g. [0.6, 0.3, 0.05, 0.05] for a Fire-Air quest

    Returns: float in [0, 1]
    """
    dot = np.dot(seat_sig, quest_elem)
    norm_product = np.linalg.norm(seat_sig) * np.linalg.norm(quest_elem)
    if norm_product == 0:
        return 0.0
    return float(np.clip(dot / norm_product, 0.0, 1.0))
```

### 4.1 Element Signature Examples

| Seat Type           | Fire | Air  | Water | Earth | Description                 |
|---------------------|------|------|-------|-------|-----------------------------|
| Pure Fire           | 1.0  | 0.0  | 0.0   | 0.0   | Synthesis specialist        |
| Fire-Air hybrid     | 0.6  | 0.4  | 0.0   | 0.0   | Speculative planner         |
| Balanced            | 0.25 | 0.25 | 0.25  | 0.25  | Generalist                  |
| Water-Earth hybrid  | 0.0  | 0.0  | 0.5   | 0.5   | Verified execution          |
| Earth dominant      | 0.05 | 0.05 | 0.1   | 0.8   | Pruning and archival        |

### 4.2 Quest Element Vector Assignment

Quest element vectors are derived from the loop's alchemical pass and station domain:

```python
def quest_element_vector(pass_id: int, station_code: str) -> np.ndarray:
    """Derive quest element vector from pass and station."""
    # Pass base vectors
    pass_base = {
        1: np.array([0.6, 0.2, 0.1, 0.1]),   # Sulfur: Fire-dominant
        2: np.array([0.1, 0.6, 0.2, 0.1]),   # Mercury: Air-dominant
        3: np.array([0.1, 0.1, 0.2, 0.6]),   # Salt: Earth-dominant
    }
    # Station modifiers (examples)
    station_mod = {
        'KRN': np.array([0.2, 0.0, 0.0, 0.0]),
        'TUN': np.array([0.0, 0.2, 0.0, 0.0]),
        'RET': np.array([0.0, 0.1, 0.1, 0.0]),
        'VOD': np.array([0.0, 0.0, 0.2, 0.0]),
        'CUT': np.array([0.0, 0.0, 0.0, 0.2]),
    }
    base = pass_base[pass_id]
    mod = station_mod.get(station_code, np.zeros(4))
    combined = base + mod
    return combined / np.linalg.norm(combined)  # normalize
```

---

## 5. Quarantine System

The quarantine system protects the system from runaway or corrupted seats. Five distinct triggers can place a seat into quarantine.

### 5.1 Quarantine Triggers

| #  | Trigger                 | Threshold       | Description                                      |
|----|-------------------------|-----------------|--------------------------------------------------|
| Q1 | truth_violation         | score < 0.3     | Seat's truth score drops below minimum           |
| Q2 | repeated_failure        | count >= 3      | 3 consecutive quest failures                     |
| Q3 | risk_escalation         | risk > 0.8      | Seat's computed risk exceeds safety ceiling      |
| Q4 | contradiction_cascade   | count >= 2      | 2+ contradictions detected in seat's output chain|
| Q5 | resource_exhaustion     | usage > 0.95    | Seat consumes >95% of allocated compute budget   |

### 5.2 Quarantine State Machine

```
                    trigger
  Active --------------------------> Quarantined
    ^                                    |
    |                                    | cooldown expires
    |                                    v
    |                              CooldownComplete
    |                                    |
    |                                    | parent_approval
    |                                    v
    |                              ParentApproved
    |                                    |
    |                                    | verification_harness passes
    +------------------------------------+
                  recovered
```

### 5.3 Quarantine Implementation

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time

class QuarantineReason(Enum):
    TRUTH_VIOLATION = "truth_violation"
    REPEATED_FAILURE = "repeated_failure"
    RISK_ESCALATION = "risk_escalation"
    CONTRADICTION_CASCADE = "contradiction_cascade"
    RESOURCE_EXHAUSTION = "resource_exhaustion"

QUARANTINE_THRESHOLDS = {
    QuarantineReason.TRUTH_VIOLATION: 0.3,
    QuarantineReason.REPEATED_FAILURE: 3,
    QuarantineReason.RISK_ESCALATION: 0.8,
    QuarantineReason.CONTRADICTION_CASCADE: 2,
    QuarantineReason.RESOURCE_EXHAUSTION: 0.95,
}

@dataclass
class QuarantineRecord:
    seat_address: int
    reason: QuarantineReason
    triggered_at: float = field(default_factory=time.time)
    cooldown_seconds: float = 300.0  # 5 minutes default
    parent_approved: bool = False
    harness_passed: bool = False

    @property
    def cooldown_complete(self) -> bool:
        return (time.time() - self.triggered_at) >= self.cooldown_seconds

    @property
    def recoverable(self) -> bool:
        return (
            self.cooldown_complete
            and self.parent_approved
            and self.harness_passed
        )

def check_quarantine_triggers(seat) -> Optional[QuarantineReason]:
    """Check if any quarantine trigger fires for the given seat."""
    if seat.truth_score < QUARANTINE_THRESHOLDS[QuarantineReason.TRUTH_VIOLATION]:
        return QuarantineReason.TRUTH_VIOLATION
    if seat.consecutive_failures >= QUARANTINE_THRESHOLDS[QuarantineReason.REPEATED_FAILURE]:
        return QuarantineReason.REPEATED_FAILURE
    if seat.risk_score > QUARANTINE_THRESHOLDS[QuarantineReason.RISK_ESCALATION]:
        return QuarantineReason.RISK_ESCALATION
    if seat.contradiction_count >= QUARANTINE_THRESHOLDS[QuarantineReason.CONTRADICTION_CASCADE]:
        return QuarantineReason.CONTRADICTION_CASCADE
    if seat.resource_usage > QUARANTINE_THRESHOLDS[QuarantineReason.RESOURCE_EXHAUSTION]:
        return QuarantineReason.RESOURCE_EXHAUSTION
    return None
```

### 5.4 Quarantine Cooldown Durations

Cooldown scales with severity:

| Trigger                 | Base Cooldown | Repeat Multiplier | Max Cooldown |
|-------------------------|---------------|-------------------|--------------|
| truth_violation         | 300s          | 2x per repeat     | 3600s        |
| repeated_failure        | 180s          | 1.5x per repeat   | 1800s        |
| risk_escalation         | 600s          | 3x per repeat     | 7200s        |
| contradiction_cascade   | 450s          | 2.5x per repeat   | 5400s        |
| resource_exhaustion     | 120s          | 1.2x per repeat   | 600s         |

---

## 6. Seat Activation Lifecycle

Every virtual seat follows a strict 5-state lifecycle:

```
Dormant --> Elected --> Active --> Reporting --> Dormant
   ^                                               |
   +-----------------------------------------------+
```

### 6.1 State Definitions

| State     | Duration    | Description                                            |
|-----------|-------------|--------------------------------------------------------|
| Dormant   | indefinite  | Seat is inactive, available for election                |
| Elected   | 1 tick      | Seat has been chosen, initializing context              |
| Active    | quest-bound | Seat is executing quest work, producing artifacts       |
| Reporting | 1 tick      | Seat submits results, computes steward score            |
| Dormant   | (re-entry)  | Seat returns to pool after reporting                    |

### 6.2 Lifecycle Transitions

```python
class SeatState(Enum):
    DORMANT = "dormant"
    ELECTED = "elected"
    ACTIVE = "active"
    REPORTING = "reporting"
    QUARANTINED = "quarantined"

VALID_TRANSITIONS = {
    SeatState.DORMANT: [SeatState.ELECTED],
    SeatState.ELECTED: [SeatState.ACTIVE, SeatState.DORMANT],  # can abort
    SeatState.ACTIVE: [SeatState.REPORTING, SeatState.QUARANTINED],
    SeatState.REPORTING: [SeatState.DORMANT],
    SeatState.QUARANTINED: [SeatState.DORMANT],  # after recovery
}

def transition(seat, new_state: SeatState):
    """Transition seat to new state with validation."""
    if new_state not in VALID_TRANSITIONS[seat.state]:
        raise ValueError(
            f"Invalid transition: {seat.state} -> {new_state}. "
            f"Valid targets: {VALID_TRANSITIONS[seat.state]}"
        )
    seat.state = new_state
    seat.state_entered_at = time.time()
```

---

## 7. Subagent Depth Limit

The maximum nesting depth is 6 levels. This is a hard architectural constraint.

| Depth | Role                  | Typical Count (active) | Delegation Rights          |
|-------|-----------------------|------------------------|----------------------------|
| 1     | Prime subagent        | 4                      | Full delegation to depth 2 |
| 2     | Strategy subagent     | 16                     | Delegate to depth 3        |
| 3     | Tactical subagent     | 48                     | Delegate to depth 4        |
| 4     | Execution subagent    | 80                     | Delegate to depth 5        |
| 5     | Specialist subagent   | 64                     | Delegate to depth 6 only   |
| 6     | Leaf worker           | 44                     | No delegation (terminal)   |

Depth-6 seats are terminal: they execute work directly and cannot spawn children. Any attempt to delegate from depth 6 is rejected and logged as a `depth_violation`.

---

## 8. System-Wide Invariants

The following invariants must hold at all times across the full 4-master system:

```yaml
invariants:
  - name: active_cap_per_master
    rule: "for each master M: count(active_seats(M)) <= 256"
  - name: active_cap_system
    rule: "sum(active_seats(all_masters)) <= 1024"
  - name: depth_limit
    rule: "no seat exists at depth > 6"
  - name: no_orphan_active
    rule: "every active seat at depth d>1 has an active ancestor at depth d-1"
  - name: quarantine_isolation
    rule: "quarantined seats cannot receive or send quest messages"
  - name: element_conservation
    rule: "sum(element_vector) is constant across election and deactivation"
  - name: single_quest_per_seat
    rule: "each active seat processes at most one quest at a time"
```

---

## 9. Cross-References

- `198_lp57omega_master_framework.md` -- Parent framework: orbit structure, loop lifecycle, reward kernel
- `03_METRO/02_parallel_agent_grid.md` -- Agent grid routing used during seat election
- `Ch05` -- Paradox regimes: quarantine trigger Q4 (contradiction_cascade) aligns with paradox calculus
- `06_RUNTIME/` -- Runtime manifests encode active seat state per tick
