# LP-57Omega Quest Atlas v1.6 — Golden Test Vectors and Verifier

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `verification-specification`
- Role tags: `testing, verification, golden-vectors, certification`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the golden test vector suite: 6 categories, 15 individual vectors, deterministic replay verification, and the release certification gate. All vectors must pass for any release to be certified.

## Verification Architecture

```
GOLDEN TEST VECTORS (15 total)
     │
     ├── Category 1: Route Compilation (4 vectors)
     ├── Category 2: Board Kernel (2 vectors)
     ├── Category 3: Storm (3 vectors)
     ├── Category 4: Seat Election (1 vector)
     ├── Category 5: Reward Settlement (2 vectors)
     └── Category 6: Receipt Chain (3 vectors)
     │
     ▼
  VERIFIER (deterministic replay)
     │
     ▼
  RESULT: 15/15 PASS → CERTIFIED
          < 15  PASS → REJECTED
```

## Category 1: Route Compilation (4 Vectors)

### V01 — route_sigma_lock

```
Purpose:  Verify sigma path is always present in every route
Input:    10 candidates with varying stations, truth states, elements
Expected: Every route.sigma == ['AppA', 'AppI', 'AppM']
Test:
  for each candidate c in test_set:
    route = compile_route(normalize_candidate(c))
    assert route.sigma == ['AppA', 'AppI', 'AppM']
Result:   PASS if all routes contain exact sigma path
```

### V02 — route_hub_budget

```
Purpose:  Verify hub count never exceeds 6
Input:    5 candidates designed to maximize hub count
          (publish_intent=True, truth=NEAR, high dependency count)
Expected: All routes have total_hubs <= 6
Test:
  for each candidate c in maxhub_set:
    route = compile_route(normalize_candidate(c))
    total = len(route.sigma) + bool(route.lens_hub) \
          + bool(route.overlay) + bool(route.publish_hub)
    assert total <= 6
    if trimmed: assert len(route.droplog) > 0
Result:   PASS if no route exceeds 6 hubs
```

### V03 — route_fail_illegal

```
Purpose:  Verify FAIL truth state makes route illegal
Input:    3 candidates with truth_state='FAIL'
Expected: route.legal == False for all
Test:
  for each candidate c in fail_set:
    route = compile_route(normalize_candidate(c))
    assert route.legal == False
    assert route.overlay == 'AppK'
Result:   PASS if all FAIL routes are illegal
```

### V04 — route_publish_overlay

```
Purpose:  Verify AppO hub added for OK + publish_intent
Input:    4 candidates:
          - OK + publish_intent=True  -> expects AppO
          - OK + publish_intent=False -> no AppO
          - NEAR + publish_intent=True -> no AppO
          - FAIL + publish_intent=True -> no AppO
Expected: Only first candidate gets AppO
Test:
  routes = [compile_route(normalize_candidate(c)) for c in pub_set]
  assert routes[0].publish_hub == 'AppO'
  assert routes[1].publish_hub is None
  assert routes[2].publish_hub is None
  assert routes[3].publish_hub is None
Result:   PASS if publish overlay logic correct
```

## Category 2: Board Kernel (2 Vectors)

### V05 — board_determinism

```
Purpose:  Verify determinism of board kernel
Input:    20 canonical candidates (fixed seed, reproducible)
Expected: Two calls produce identical output
Test:
  candidates = load_canonical_candidates()
  result_a = emit_orbit_boards(candidates)
  result_b = emit_orbit_boards(candidates)
  assert result_a == result_b  # deep equality
  # Additionally verify:
  assert len(result_a['guild']) == len(result_b['guild'])
  assert len(result_a['temple']) == len(result_b['temple'])
  for i in range(len(result_a['guild'])):
    assert result_a['guild'][i].score == result_b['guild'][i].score
    assert result_a['guild'][i].queue == result_b['guild'][i].queue
Result:   PASS if both runs produce byte-identical output
```

### V06 — board_guild_scoring

```
Purpose:  Verify guild scoring respects station ordering
Input:    4 identical candidates except station = {1, 5, 10, 19}
Expected: Higher station number -> higher score (difficulty scales)
Test:
  candidates = [make_candidate(station=s) for s in [1, 5, 10, 19]]
  scores = [guild_score(normalize_candidate(c), compile_route(c))
            for c in candidates]
  assert scores[0] < scores[1] < scores[2] < scores[3]
Result:   PASS if scores are strictly increasing with station
```

## Category 3: Storm (3 Vectors)

### V07 — storm_trigger

```
Purpose:  Verify PhiStorm triggers at correct thresholds
Input:    Pheromone state: positive=[10, 10, 8, 8]=36, shadow=[3, 3, 3, 3]=12
Expected: Storm triggers (36 >= 34 AND 12 <= 13)
Test:
  state = PheromoneState(
    positive=Vec4(10, 10, 8, 8),
    shadow=Vec4(3, 3, 3, 3)
  )
  assert storm_check(state) == True
  assert storm_intensity(state) > 0.0
Result:   PASS if storm correctly triggers
```

### V08 — storm_no_trigger

```
Purpose:  Verify storm does NOT trigger when shadow too high
Input:    Pheromone state: positive=[10, 10, 8, 8]=36, shadow=[5, 5, 5, 5]=20
Expected: No storm (36 >= 34 BUT 20 > 13)
Test:
  state = PheromoneState(
    positive=Vec4(10, 10, 8, 8),
    shadow=Vec4(5, 5, 5, 5)
  )
  assert storm_check(state) == False
Result:   PASS if storm correctly does not trigger
```

### V09 — coalition_bonus_scaling

```
Purpose:  Verify coalition bonus scales with party size
Input:    Coalitions of size 2, 3, 4
Expected: Larger coalition -> larger bonus
Test:
  bonus_2 = coalition_bonus(party_size=2)
  bonus_3 = coalition_bonus(party_size=3)
  bonus_4 = coalition_bonus(party_size=4)
  assert bonus_2 < bonus_3 < bonus_4
  assert abs(bonus_2 - 0.236) < 0.001  # single bonus unit
  assert abs(bonus_3 - 0.472) < 0.001  # 2 * 0.236
  assert abs(bonus_4 - 0.708) < 0.001  # 3 * 0.236
Result:   PASS if coalition bonus scales linearly
```

## Category 4: Seat Election (1 Vector)

### V10 — seat_quarantine_exclusion

```
Purpose:  Verify quarantined seats cannot be elected
Input:    8 seats, 3 quarantined, 1 quest
Expected: Only non-quarantined seats appear in election results
Test:
  seats = [make_seat(i, quarantined=(i in [2, 5, 7])) for i in range(8)]
  quest = make_quest(element_vector=Vec4(0.5, 0.3, 0.1, 0.1))
  elected = elect_seats(quest, seats)
  for seat in elected:
    assert seat.state != QUARANTINED
    assert seat.index not in [2, 5, 7]
Result:   PASS if no quarantined seat is elected
```

## Category 5: Reward Settlement (2 Vectors)

### V11 — reward_truth_gate

```
Purpose:  Verify truth state gates rewards correctly
Input:    4 identical quests with truth = {OK, NEAR, AMBIG, FAIL}
Expected: OK=1.0, 0<NEAR<OK, 0<AMBIG<NEAR, FAIL=0.0
Test:
  quest_base = make_quest(station=5, element=Vec4(0.5,0.3,0.1,0.1))
  rewards = {}
  for truth in ['OK', 'NEAR', 'AMBIG', 'FAIL']:
    q = quest_base.copy(truth_state=truth)
    rewards[truth] = compute_reward(q)
  assert rewards['OK'] > 0
  assert rewards['NEAR'] > 0
  assert rewards['AMBIG'] > 0
  assert rewards['FAIL'] == 0
  assert rewards['OK'] > rewards['NEAR'] > rewards['AMBIG']
Result:   PASS if truth gates are correctly ordered
```

### V12 — reward_settlement

```
Purpose:  Verify non-zero XP for valid quest completion
Input:    Solo quest at S05, truth=OK, element=Vec4(0.5,0.3,0.1,0.1)
Expected: payout > 0
Test:
  quest = make_quest(
    station=5, quest_class='bridge',
    truth_state='OK',
    element_vector=Vec4(0.5, 0.3, 0.1, 0.1),
    pass_index=1  # Sulfur
  )
  payout = settle_reward(quest)
  assert payout > 0
  # Verify formula:
  expected = 64 * 1.2 * 0.5 * 1.0 * 1.0  # BASE * S05_base * F * d_F * chi
  assert abs(payout - expected) / expected < 0.01  # within 1%
Result:   PASS if settlement produces expected non-zero XP
```

## Category 6: Receipt Chain (3 Vectors)

### V13 — receipt_chain_integrity

```
Purpose:  Verify receipt chain forms unbroken hash chain
Input:    Sequence of 5 actions producing 5 receipts
Expected: Each receipt references previous receipt hash
Test:
  actions = [make_action(i) for i in range(5)]
  receipts = []
  for action in actions:
    entry = write_ledger_entry(action)
    receipt = compute_receipt(entry)
    receipts.append(receipt)
  for i in range(1, len(receipts)):
    expected_chain = sha256(receipts[i-1].hash + receipts[i].entry_hash)
    assert receipts[i].chain_hash == expected_chain
Result:   PASS if chain hashes are consistent
```

### V14 — receipt_seal_verification

```
Purpose:  Verify sealed quest produces valid closure receipt
Input:    3-quest sequence: create -> process -> seal
Expected: Seal receipt references all prior receipts, lint=0 failures
Test:
  r1 = process_quest(make_quest('create'))
  r2 = process_quest(make_quest('process'))
  r3 = seal_quest(quest_id, [r1, r2])
  lint_result = lint_receipt_chain([r1, r2, r3])
  assert lint_result.failures == 0
  assert r3.closure_status == 'CLOSED'
Result:   PASS if seal is valid and lint clean
```

### V15 — orbit_level_decomposition

```
Purpose:  Verify level/orbit decomposition is correct
Input:    Levels: [0, 1, 56, 57, 113, 570]
Expected: Correct orbit and position decomposition
Test:
  cases = [
    (0,   0, 0),    # orbit 0, position 0
    (1,   0, 1),    # orbit 0, position 1
    (56,  0, 56),   # orbit 0, position 56
    (57,  1, 0),    # orbit 1, position 0
    (113, 1, 56),   # orbit 1, position 56
    (570, 10, 0),   # orbit 10, position 0
  ]
  for level, expected_orbit, expected_pos in cases:
    orbit = level // 57
    pos = level % 57
    assert orbit == expected_orbit
    assert pos == expected_pos

  # Also verify amplifier monotonicity
  amps = [amplifier(level) for level in range(200)]
  for i in range(1, len(amps)):
    assert amps[i] >= amps[i-1]  # monotonically non-decreasing
Result:   PASS if decomposition and amplifier are correct
```

## Verifier Execution

### Running the Verifier

```
Entry point: verifier.py

Usage:
  python -m verifier --all          # Run all 15 vectors
  python -m verifier --category 1   # Run category 1 only
  python -m verifier --vector V05   # Run single vector

Output format:
  [PASS] V01 route_sigma_lock         (0.003s)
  [PASS] V02 route_hub_budget         (0.002s)
  ...
  [PASS] V15 orbit_level_decomposition (0.001s)

  ════════════════════════════════
  RESULT: 15/15 PASSED
  STATUS: CERTIFIED
  ════════════════════════════════
```

### Release Certification Gate

```
CERTIFY_RELEASE(bundle):
  1. Load BundleManifest.v1
  2. Verify bundle integrity (all policies present, hashes match)
  3. Run all 15 golden test vectors
  4. If 15/15 PASS:
       emit CERTIFICATION_RECEIPT
       status = CERTIFIED
       release_allowed = True
  5. If < 15 PASS:
       emit FAILURE_REPORT (list failed vectors)
       status = REJECTED
       release_allowed = False
  6. Log result to ledger

  CERTIFICATION_RECEIPT contains:
    - bundle_hash
    - vector_results (15 entries)
    - timestamp
    - verifier_version
    - chain_hash (links to previous certification)
```

## Deterministic Replay

All vectors support deterministic replay:

```
REPLAY(vector_id):
  1. Load vector input from canonical dataset
  2. Execute vector test function
  3. Compare output against expected result
  4. Output is binary: PASS or FAIL
  5. No randomness, no external dependencies
  6. Same hardware, same result. Different hardware, same result.
```

## Vector Summary Table

| ID  | Category     | Name                        | Critical |
|-----|-------------|-----------------------------|-----------|
| V01 | Route       | route_sigma_lock            | Yes      |
| V02 | Route       | route_hub_budget            | Yes      |
| V03 | Route       | route_fail_illegal          | Yes      |
| V04 | Route       | route_publish_overlay       | Yes      |
| V05 | Board       | board_determinism           | Yes      |
| V06 | Board       | board_guild_scoring         | Yes      |
| V07 | Storm       | storm_trigger               | Yes      |
| V08 | Storm       | storm_no_trigger            | Yes      |
| V09 | Storm       | coalition_bonus_scaling     | No       |
| V10 | Seat        | seat_quarantine_exclusion   | Yes      |
| V11 | Reward      | reward_truth_gate           | Yes      |
| V12 | Reward      | reward_settlement           | Yes      |
| V13 | Receipt     | receipt_chain_integrity     | Yes      |
| V14 | Receipt     | receipt_seal_verification   | Yes      |
| V15 | Receipt     | orbit_level_decomposition   | No       |

Critical vectors (13 of 15) are mandatory for release. Non-critical vectors are advisory.

## Invariants

1. All 15 vectors must pass for release certification
2. Vectors are deterministic (no randomness)
3. Vector inputs are canonical and version-controlled
4. Vector expected outputs are fixed at specification time
5. The verifier itself is deterministic
6. Certification receipts form a hash chain
7. Any vector failure blocks release

## Suggested chapter anchors

- `Ch03` — Truth corridors and witness discipline
- `Ch12` — Legality certificates and closure
- `Ch16` — Verification harnesses and replay kernels
