# LP57Ω Quest Atlas v1.7 — Fixture Specimens

- Kind: `fixture-suite`
- Role tags: `testing, quest-atlas, fixtures, corpus-backed`
- Version: `1.7`
- Family: `LP57Ω Quest Engine`

## Purpose

Eight corpus-backed fixture specimens for integration and regression testing of the Quest Atlas pipeline. Each fixture is a self-contained, deterministic test case that exercises a distinct quest lifecycle path.

---

## Fixture 001 — Solo Quest Fixture

```yaml
fixture_id: FIX-001-SOLO
quest_class: Solo
status: Active
truth_gate: OK
element: Fire
corridor: [Ch01, Ch07, Ch13]
witness_count: 1
replay_required: false
expected_reward: base * γ_OK * quality
```

### Scenario

A single agent claims a solo quest, completes all corridor stations, passes the truth gate with OK status, and collects the base reward. No witness endorsement beyond self-attestation.

### Assertions

- Quest transitions: Draft → Active → Sealed → Published
- Truth record: `{gate: OK, γ: 1.0, stamp: epoch_N}`
- Reward minted at `base * 1.0 * quality_factor`
- No community multiplier applied
- Receipt chain length: 3 (claim, seal, publish)

---

## Fixture 002 — Community Quest Fixture

```yaml
fixture_id: FIX-002-COMMUNITY
quest_class: Community
status: Active
truth_gate: OK
element: Water
corridor: [Ch03, Ch09, Ch15, Ch21]
witness_count: 3
replay_required: true
expected_reward: base * γ_OK * quality * (1 + β*N)
```

### Scenario

Three agents collaborate on a community quest spanning four corridor stations. All three provide witness attestations. Replay bundle is generated and verified. Community multiplier β=0.25 applies.

### Assertions

- Quest transitions: Draft → Active → Sealed → Published
- WitnessBundle contains 3 signed attestations
- ReplayBundle hash-chains all three witness records
- Reward includes community multiplier: `base * 1.0 * q * (1 + 0.25*3)`
- Contribution split: proportional to corridor-station completion count
- Receipt chain length: 5 (claim, 3×witness, seal)

---

## Fixture 003 — Temple Rite Fixture

```yaml
fixture_id: FIX-003-TEMPLE
quest_class: TempleRite
status: Active
truth_gate: NEAR
element: Earth
corridor: [Ch05, Ch11, Ch17]
witness_count: 2
replay_required: true
certification_required: true
expected_reward: base * γ_NEAR * quality
```

### Scenario

A temple rite quest enters the certification queue, passes ethics watchlist check, clears invariant backlog validation, and receives NEAR truth status. Reward is scaled by φ⁻² due to NEAR gate.

### Assertions

- Quest transitions: Draft → Active → Blocked (certification) → Active → Sealed
- Certification receipt present in chain
- Ethics watchlist clearance logged
- γ_NEAR = φ⁻² ≈ 0.381966
- Reward: `base * 0.381966 * quality`
- Consent receipt attached to ReceiptRegistry

---

## Fixture 004 — Storm Event Fixture

```yaml
fixture_id: FIX-004-STORM
quest_class: Storm
status: Active
truth_gate: OK
element: Air
corridor: [Ch02, Ch08, Ch14, Ch20]
witness_count: 5
storm_pool: 21
storm_duration: 5
coalition_size: 4
expected_reward: storm_pool * split * coalition_bonus
```

### Scenario

A storm event spawns when positive pheromone reaches threshold (≥34). Four coalition members participate across four corridors. Storm runs for 5 epochs with difficulty boost φ⁻³.

### Assertions

- Storm spawn triggered at pheromone_positive ≥ 34
- Pool allocation: base=21, scaled by participation
- Duration: 5 epochs
- Coalition bonus: φ⁻³ per member = 4 * 0.2360...
- All participants receive proportional storm reward
- Storm receipt includes spawn_trigger, pool_state, duration_actual

---

## Fixture 005 — Publish Candidate Fixture

```yaml
fixture_id: FIX-005-PUBLISH
quest_class: Solo
status: Sealed
truth_gate: OK
element: Fire
corridor: [Ch01, Ch07]
witness_count: 1
replay_required: false
publish_block_check: true
expected_state: Published
```

### Scenario

A sealed quest passes all publish-block checks (no ethics flags, no invariant violations, no pending dependencies) and transitions to Published state. ReleaseManifest.v1 is generated.

### Assertions

- No publish block sets active
- ReleaseManifest.v1 generated with SHA-256 digest
- Quest state: Sealed → Published
- SealedReceiptBundle.v1 finalized
- All receipt entries have valid chain digests
- Published timestamp recorded in LedgerStamp

---

## Fixture 006 — Repair Fixture

```yaml
fixture_id: FIX-006-REPAIR
quest_class: Solo
status: Blocked
truth_gate: ZERO
element: Water
corridor: [Ch04, Ch10]
witness_count: 0
repair_required: true
expected_state: Active
```

### Scenario

A quest enters ZERO truth state due to failed verification. Repair protocol activates: corridor stations are re-traversed, truth gate is re-evaluated, and quest returns to Active status upon passing.

### Assertions

- Quest transitions: Active → Blocked (ZERO) → Active (repaired)
- γ_ZERO = 0.0 (no reward while blocked)
- Repair receipt logged with re-traversal proof
- Truth record updated from ZERO to pending re-evaluation
- No reward minted during ZERO state
- Receipt chain includes repair entry between block and reactivation

---

## Fixture 007 — Convergence Fixture

```yaml
fixture_id: FIX-007-CONVERGE
quest_class: Community
status: Active
truth_gate: OK
element: Earth
corridor: [Ch06, Ch12, Ch18]
witness_count: 4
convergence_target: fixed_point
expected_reward: base * γ_OK * quality * convergence_amplifier
```

### Scenario

A community quest targets a convergence fixed point. Multiple agents iterate toward the fixed point across three corridor stations. Convergence is verified when successive iterations differ by less than φ⁻⁵.

### Assertions

- Convergence verified: |iter_n - iter_(n-1)| < φ⁻⁵
- Fixed point recorded in TruthRecord
- Convergence amplifier applied to reward
- All 4 witnesses attest convergence
- ReplayBundle includes iteration history
- Receipt chain includes convergence proof entry

---

## Fixture 008 — Migration Fixture

```yaml
fixture_id: FIX-008-MIGRATE
quest_class: Solo
status: Published
truth_gate: OK
element: Air
corridor: [Ch01, Ch07, Ch13, Ch19]
source_policy: RewardPolicy.v0
target_policy: RewardPolicy.v1
expected_state: Published (migrated)
```

### Scenario

A previously published quest undergoes policy migration from RewardPolicy.v0 to RewardPolicy.v1. Freeze window is respected, backward replay suite validates consistency, and conversion map transforms legacy reward records.

### Assertions

- Freeze window enforced: no mutations during migration
- Backward replay suite passes all legacy checks
- Conversion map applied: v0 reward → v1 reward
- Rollback plan available and tested
- Truth records verified post-migration
- SealedReceiptBundle.v1 re-sealed with migration entry
- Receipt chain includes MIGRATE entry with before/after digests

---

## Cross-Fixture Invariants

All eight fixtures must satisfy:

1. **Receipt chain integrity**: Every receipt chain is a valid SHA-256 hash chain from genesis to tip
2. **Truth gate consistency**: γ values match the gate enum (OK=1.0, NEAR=φ⁻², ZERO=0.0)
3. **Corridor coverage**: Every referenced corridor station exists in the chapter lattice
4. **Witness quorum**: Community quests require ≥ 2 witnesses; solo quests require ≥ 1
5. **Idempotent replay**: Running any fixture twice produces identical receipt chains
6. **Element assignment**: Each fixture's element is deterministic from its corridor set

## Fixture Execution Order

Fixtures are independent and may run in any order. For full integration testing, the recommended sequence is:

```
FIX-001 → FIX-002 → FIX-003 → FIX-005 → FIX-004 → FIX-006 → FIX-007 → FIX-008
```

This sequence exercises the lifecycle from solo through community, temple certification, publishing, storms, repair, convergence, and finally migration.
