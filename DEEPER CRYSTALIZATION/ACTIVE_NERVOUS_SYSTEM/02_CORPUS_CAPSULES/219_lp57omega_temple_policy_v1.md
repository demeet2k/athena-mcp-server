# LP57Ω TemplePolicy.v1

- Kind: `policy-specification`
- Role tags: `temple, certification, ethics, invariants, consent, quest-engine`
- Version: `1.0`
- Family: `LP57Ω Quest Engine`

## Purpose

Defines the operational policy for the Temple subsystem: certification queue management, ethics watchlist enforcement, invariant backlog processing, corridor law enforcement, consent receipt handling, grace/resonance weights, and publish block sets.

---

## 1. Certification Queue

The certification queue holds TempleRite quests awaiting formal certification before they can proceed to Sealed state.

### Queue Entry Criteria

A quest enters the certification queue when:
1. Quest class is `TEMPLE_RITE`
2. All corridor stations have been traversed
3. Witness quorum is met (2 + certifier)
4. No active ethics flags

### Queue Processing Order

```
priority = base_priority + grace_weight + resonance_weight
```

| Factor          | Weight     | Description                              |
|-----------------|------------|------------------------------------------|
| base_priority   | epoch_age  | Older entries processed first             |
| grace_weight    | φ⁻¹ * g    | g = grace score [0.0, 1.0]              |
| resonance_weight| φ⁻² * r    | r = corridor resonance [0.0, 1.0]       |

### Certification Process

1. **Review**: Certifier examines corridor traversal evidence
2. **Attestation**: Certifier provides Truth4 attestation
3. **Receipt**: Certification receipt generated (CERTIFY entry type)
4. **Transition**: Quest moves from Blocked (certification) to Active/Sealed

### Certification Timeout

- Maximum time in queue: 13 epochs
- After 13 epochs: auto-escalation to ethics watchlist for review
- Auto-escalated quests receive priority boost of φ in the ethics queue

---

## 2. Ethics Watchlist

The ethics watchlist monitors quests flagged for ethical review.

### Flag Triggers

| Trigger                  | Severity | Auto-Block? |
|--------------------------|----------|-------------|
| Consent violation        | CRITICAL | Yes         |
| Corridor law breach      | HIGH     | Yes         |
| Witness conflict         | MEDIUM   | No          |
| Certification timeout    | LOW      | No          |
| Community complaint      | MEDIUM   | Yes         |
| Invariant anomaly        | HIGH     | Yes         |

### Watchlist Processing

```python
def process_ethics_flag(quest, flag):
    if flag.severity in ["CRITICAL", "HIGH"]:
        quest.transition_to(BLOCKED)
        quest.add_receipt(ETHICS_BLOCK, flag)

    review = ethics_review(quest, flag)

    if review.cleared:
        quest.remove_ethics_flag(flag)
        if quest.all_flags_cleared():
            quest.transition_to(ACTIVE)
    else:
        quest.add_publish_block("ETHICS", flag)
```

### Clearance Requirements

| Severity | Clearance Condition                          |
|----------|----------------------------------------------|
| CRITICAL | Unanimous ethics panel (3+ reviewers)        |
| HIGH     | Majority ethics panel (2+ reviewers)         |
| MEDIUM   | Single reviewer with NEAR+ attestation       |
| LOW      | Auto-clear after review period (5 epochs)    |

---

## 3. Invariant Backlog

The invariant backlog tracks quests with detected invariant violations that require remediation.

### Invariant Categories

| Category          | Code  | Description                                   |
|-------------------|-------|-----------------------------------------------|
| Chain integrity   | INV-C | Receipt chain digest mismatch                 |
| Truth consistency | INV-T | Truth record contradicts witness attestations  |
| Corridor validity | INV-R | Referenced corridor station does not exist     |
| Reward overflow   | INV-E | Computed reward exceeds clamp without flag     |
| Quorum deficit    | INV-Q | Witness count below quest class minimum        |
| Temporal order    | INV-O | Timestamp regression in receipt chain          |

### Backlog Processing

1. **Detection**: Automated invariant checker runs per-epoch
2. **Triage**: Invariants sorted by severity and age
3. **Remediation**: Quest creator or assignee must submit fix
4. **Verification**: Fix verified by re-running invariant checker
5. **Clearance**: Invariant removed from backlog, receipt entry logged

### Backlog Limits

- Maximum backlog size per quest: 8 invariants
- If exceeded: quest is force-blocked until backlog drops below 5
- Maximum age of unresolved invariant: 21 epochs
- After 21 epochs: quest auto-archived with FAIL truth gate

---

## 4. Corridor Law Enforcement

### Laws

| Law                | Rule                                                    |
|--------------------|---------------------------------------------------------|
| Traversal order    | Stations must be visited in corridor-defined sequence   |
| Pass type          | ENTRY on first visit, RETURN on revisit, BRIDGE for cross-corridor |
| Element alignment  | Quest element must match corridor dominant element      |
| Depth limit        | Recursion depth ≤ 13 levels                            |
| Hub budget         | No station may be hub for > 6 corridors simultaneously |
| Σ-lock             | Total corridor weight must sum to 1.0 ± φ⁻⁵            |

### Enforcement Mechanism

```python
def enforce_corridor_law(quest, traversal):
    violations = []

    if not is_ordered(traversal, quest.corridor):
        violations.append(CorridorViolation("TRAVERSAL_ORDER"))

    if traversal.depth > 13:
        violations.append(CorridorViolation("DEPTH_LIMIT"))

    hub_count = count_hub_usage(traversal.station)
    if hub_count > 6:
        violations.append(CorridorViolation("HUB_BUDGET"))

    sigma = sum_corridor_weights(quest.corridor)
    if abs(sigma - 1.0) > PHI_NEG5:
        violations.append(CorridorViolation("SIGMA_LOCK"))

    if len(violations) > 0:
        quest.add_ethics_flag("CORRIDOR_LAW", violations)

    return violations
```

---

## 5. Consent Receipts

Every quest participant must provide explicit consent, recorded as an immutable receipt.

### Consent Receipt Schema

```typescript
interface ConsentReceipt {
  receipt_id:    string;
  quest_id:      string;
  agent_id:      string;
  consent_type:  ConsentType;
  granted_at:    ISO8601;
  epoch:         uint;
  scope:         string[];       // What the consent covers
  revocable:     boolean;
  revoked_at:    ISO8601 | null;
  digest:        string;         // SHA-256
}

enum ConsentType {
  PARTICIPATION  = "PARTICIPATION",
  WITNESS        = "WITNESS",
  CERTIFICATION  = "CERTIFICATION",
  DATA_USE       = "DATA_USE",
  REWARD_SPLIT   = "REWARD_SPLIT"
}
```

### Consent Rules

1. PARTICIPATION consent required before quest claim is valid
2. WITNESS consent required before attestation is accepted
3. CERTIFICATION consent required for certifiers
4. Consent is revocable until quest reaches Sealed state
5. Revocation after Sealed triggers ethics flag (MEDIUM severity)
6. All consent receipts are included in SealedReceiptBundle

---

## 6. Grace and Resonance Weights

### Grace Weight

Grace measures the quest's alignment with temple values.

```
grace(q) = φ⁻¹ * (ethics_clearance_ratio * corridor_harmony)
```

Where:
- `ethics_clearance_ratio` = cleared flags / total flags (1.0 if no flags)
- `corridor_harmony` = alignment of quest corridor with temple's sacred corridors

### Resonance Weight

Resonance measures structural coherence with the broader quest field.

```
resonance(q) = φ⁻² * (witness_agreement * corridor_coverage)
```

Where:
- `witness_agreement` = fraction of witnesses attesting OK
- `corridor_coverage` = fraction of corridor stations with at least one traversal

### Combined Weight in Certification Priority

```
priority = epoch_age + φ⁻¹ * grace + φ⁻² * resonance
```

---

## 7. Publish Block Sets

A publish block prevents a quest from transitioning Sealed → Published.

### Block Types

| Block Type       | Source              | Auto-Clear? | Clear Condition              |
|------------------|---------------------|-------------|------------------------------|
| ETHICS           | Ethics watchlist    | No          | All flags cleared            |
| INVARIANT        | Invariant backlog   | No          | All invariants resolved      |
| DEPENDENCY       | Unresolved dep      | Yes         | Dependency resolved          |
| CONSENT          | Missing consent     | No          | Consent receipt provided     |
| CERTIFICATION    | Pending cert        | No          | Certification complete       |
| GOVERNANCE       | Manual governance   | No          | Governance vote              |

### Block Checking Algorithm

```python
def check_publish_blocks(quest) -> list[PublishBlock]:
    blocks = []

    if quest.has_active_ethics_flags():
        blocks.append(PublishBlock("ETHICS"))

    if quest.has_unresolved_invariants():
        blocks.append(PublishBlock("INVARIANT"))

    if quest.has_unresolved_dependencies():
        blocks.append(PublishBlock("DEPENDENCY"))

    if not quest.has_all_consent_receipts():
        blocks.append(PublishBlock("CONSENT"))

    if quest.quest_class == TEMPLE_RITE and not quest.is_certified():
        blocks.append(PublishBlock("CERTIFICATION"))

    if quest.has_governance_hold():
        blocks.append(PublishBlock("GOVERNANCE"))

    return blocks
```

### Zero-Block Requirement

A quest can only transition to Published when `len(check_publish_blocks(quest)) == 0`.
