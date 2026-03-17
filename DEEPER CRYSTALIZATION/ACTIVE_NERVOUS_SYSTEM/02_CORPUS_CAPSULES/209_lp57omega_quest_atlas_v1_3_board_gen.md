# LP-57Omega Quest Atlas v1.3 — Board Generation Rules

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `board-specification`
- Role tags: `board, generation, routing, queues`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the board generation pipeline: candidate normalization, route compilation, guild/temple channel split, scoring, and queue assignment across 11 named queue types.

## Generation Pipeline

```
RAW CANDIDATES
     │
     ▼
[1] NORMALIZE ──── Clamp, validate, fill defaults
     │
     ▼
[2] ROUTE COMPILE ─ Insert sigma path, lens hubs, overlays
     │
     ▼
[3] CHANNEL SPLIT ─ Guild vs Temple routing decision
     │
     ├──── Guild Channel ────┐
     │                       │
     ▼                       ▼
[4a] GUILD SCORE        [4b] TEMPLE SCORE
     │                       │
     ▼                       ▼
[5a] GUILD QUEUE        [5b] TEMPLE QUEUE
     │                       │
     ▼                       ▼
[6a] GUILD BOARD        [6b] TEMPLE BOARD
     │                       │
     └───────────┬───────────┘
                 ▼
         ORBIT BOARDS (output)
```

## Step 1: Candidate Normalization

Every raw candidate passes through normalization before scoring:

```python
def normalize_candidate(c: Candidate) -> Candidate:
    """Clamp and validate all candidate fields."""

    # Station bounds
    c.station = clamp(c.station, 1, 19)

    # Orbit index non-negative
    c.orbit_index = max(0, c.orbit_index)

    # Pass index valid
    c.pass_index = clamp(c.pass_index, 1, 3)

    # Element vector normalization
    if c.elemental_signature is None:
        c.elemental_signature = STATION_DEFAULTS[c.station].element_vector
    else:
        c.elemental_signature = normalize_vec4(c.elemental_signature)

    # Quest class validation
    if c.quest_class not in STATION_ALLOWED_CLASSES[c.station]:
        c.quest_class = fallback_class(c.station)

    # Truth state validation
    assert c.truth_state in {'OK', 'NEAR', 'AMBIG', 'FAIL'}

    # Coordinate stamp required
    if c.coordinate_stamp is None:
        c.coordinate_stamp = infer_coord12(c)

    return c
```

### Normalization Rules

| Field               | Rule                                      | Default           |
|---------------------|-------------------------------------------|-------------------|
| station             | Clamp to [1, 19]                          | Required          |
| orbit_index         | Max(0, value)                             | 0                 |
| pass_index          | Clamp to [1, 3]                           | 1                 |
| elemental_signature | Normalize to unit Vec4                    | Station default   |
| quest_class         | Must be in station's allowed set          | Fallback class    |
| truth_state         | Must be OK/NEAR/AMBIG/FAIL                | Required          |
| coordinate_stamp    | Must be valid Coord12                     | Inferred          |
| artifact_id         | Must be non-empty string                  | Required          |

## Step 2: Route Compilation

The route compiler transforms each candidate into a routed candidate with path information:

```python
def compile_route(c: NormalizedCandidate) -> RoutedCandidate:
    """Build route with sigma path, lens hubs, and overlays."""

    route = Route()

    # Sigma path (always present)
    route.sigma = ['AppA', 'AppI', 'AppM']

    # Lens hub from dominant element
    dominant = dominant_element(c.elemental_signature)
    route.lens_hub = ELEMENT_TO_HUB[dominant]

    # Overlay dispatch based on truth state
    if c.truth_state == 'NEAR':
        route.overlay = 'AppJ'
    elif c.truth_state == 'AMBIG':
        route.overlay = 'AppL'
    elif c.truth_state == 'FAIL':
        route.overlay = 'AppK'
        route.legal = False
    else:
        route.overlay = None

    # Publish overlay
    if c.publish_intent and c.truth_state == 'OK':
        route.publish_hub = 'AppO'

    # Hub budget enforcement
    total_hubs = len(route.sigma) + (1 if route.lens_hub else 0) \
               + (1 if route.overlay else 0) + (1 if route.publish_hub else 0)
    if total_hubs > 6:
        route.droplog.append(trim_excess_hubs(route, total_hubs - 6))

    # Tunnel plan from dependencies
    route.tunnels = build_tunnel_plan(c.dependencies)

    # Obligations
    route.obligations = compute_obligations(c, route)

    return RoutedCandidate(candidate=c, route=route)
```

### Hub Budget

```
Maximum hubs per route: 6

Composition:
  Sigma path:   3 hubs (fixed, always present)
  Lens hub:     1 hub  (element-specific)
  Overlay:      0-1 hub (truth-state dependent)
  Publish hub:  0-1 hub (publish-intent dependent)

Maximum possible: 3 + 1 + 1 + 1 = 6 (at budget limit)

If excess: trim in priority order (overlay last, publish first)
Trimmed hubs logged to droplog for audit.
```

## Step 3: Guild/Temple Channel Split

Each routed candidate is assigned to either the Guild or Temple channel:

```python
def channel_split(rc: RoutedCandidate) -> str:
    """Determine guild or temple assignment."""

    # Temple-only classes
    if rc.candidate.quest_class in TEMPLE_CLASSES:
        return 'TEMPLE'

    # Guild-only classes
    if rc.candidate.quest_class in GUILD_CLASSES:
        return 'GUILD'

    # Dual-channel classes (e.g., Convergence)
    if rc.candidate.quest_class in DUAL_CLASSES:
        guild_s = guild_score(rc)
        temple_s = temple_score(rc)
        return 'TEMPLE' if temple_s > guild_s else 'GUILD'

    # Default routing by depth and compression
    if rc.candidate.coordinate_stamp.Zs > 0.5:
        return 'TEMPLE'  # deep recursion -> temple
    if rc.candidate.coordinate_stamp.Cs > 0.7:
        return 'TEMPLE'  # high compression -> temple

    return 'GUILD'  # default
```

### Channel Classification

```
GUILD_CLASSES = {seed, brainstorm, merge, debate, relay, review,
                 co_author, bridge, cross_reference, survey,
                 consensus, recruit, exhibit}

TEMPLE_CLASSES = {deep_focus, meditation, compression, recursion_dive,
                  void_approach, certify, verify, audit}

DUAL_CLASSES = {storm_ride, phase_shift, breakthrough,
                catalyst, emit, governance}
```

## Step 4: Scoring

### Guild Scoring

```python
def guild_score(rc: RoutedCandidate) -> float:
    base = rc.candidate.station_payout_base
    truth_w = TRUTH_WEIGHTS[rc.candidate.truth_state]
    # truth_w: OK=1.0, NEAR=0.618, AMBIG=0.382, FAIL=0.0
    difficulty = 1.0 + 0.25 * (rc.candidate.station - 1) / 18
    pressure = sum(rc.route.obligations)
    community = 1.0
    if rc.candidate.quest_class in COMMUNITY_CLASSES:
        community = 1.0 + 0.25 * (rc.candidate.party_size - 1)
    guild_amp = 1.0 + 0.10 * len(rc.candidate.target_set)
    return base * truth_w * difficulty * pressure * community * guild_amp
```

### Temple Scoring

```python
def temple_score(rc: RoutedCandidate) -> float:
    base = rc.candidate.station_payout_base
    truth_w = TRUTH_WEIGHTS[rc.candidate.truth_state]
    depth = 1.0 + 0.1 * len(rc.route.witnesses) + 0.1 * len(rc.route.replays)
    temple_amp = 1.0 + 0.15 * len(rc.candidate.evidence_set)
    return base * truth_w * depth * temple_amp
```

## Step 5: Queue Assignment

### Guild Queues (6 types)

| Queue      | Condition                                | Priority |
|------------|------------------------------------------|----------|
| featured   | publish_intent AND truth=OK              | 1        |
| ladder     | Default guild assignment                 | 2        |
| repair     | quest_class in REPAIR_CLASSES            | 3        |
| storm      | quest_class in STORM_CLASSES             | 4        |
| recruit    | quest_class in COMMUNITY_CLASSES         | 5        |
| overflow   | truth=FAIL OR capacity exceeded          | 6        |

### Temple Queues (5 types + overflow)

| Queue          | Condition                                | Priority |
|----------------|------------------------------------------|----------|
| certification  | quest_class in CERTIFY_CLASSES           | 1        |
| near_closure   | truth=NEAR AND closure_ready             | 2        |
| ambiguities    | truth=AMBIG                              | 3        |
| compression    | coordinate_stamp.Cs > 0.5               | 4        |
| sovereign      | quest_class=publish AND certified        | 5        |
| overflow       | truth=FAIL OR capacity exceeded          | 6        |

## Step 6: Board Assembly

```python
def build_guild_board(candidates: list) -> list:
    normalized = [normalize_candidate(c) for c in candidates]
    routed = [compile_route(c) for c in normalized]
    guild_candidates = [rc for rc in routed if channel_split(rc) == 'GUILD']
    scored = [(guild_score(rc), rc) for rc in guild_candidates]
    queued = [(s, assign_guild_queue(rc), rc) for s, rc in scored]
    queued.sort(key=lambda x: (-x[0]))  # descending score
    return [BoardEntry(score=s, queue=q, candidate=rc) for s, q, rc in queued]

def build_temple_board(candidates: list) -> list:
    normalized = [normalize_candidate(c) for c in candidates]
    routed = [compile_route(c) for c in normalized]
    temple_candidates = [rc for rc in routed if channel_split(rc) == 'TEMPLE']
    scored = [(temple_score(rc), rc) for rc in temple_candidates]
    queued = [(s, assign_temple_queue(rc), rc) for s, rc in scored]
    queued.sort(key=lambda x: (-x[0]))  # descending score
    return [BoardEntry(score=s, queue=q, candidate=rc) for s, q, rc in queued]
```

### Board Capacity

```
Guild board:  Maximum 16 entries per loop
Temple board: Maximum 8 entries per loop
Total:        Maximum 24 entries per loop

Excess candidates route to overflow queue.
Overflow is processed in next available loop.
```

## Invariants

1. Pipeline is deterministic: same candidates produce same boards
2. Every candidate passes through all 6 steps
3. Every candidate is assigned to exactly one channel (Guild or Temple)
4. Every candidate is assigned to exactly one queue
5. Hub count never exceeds 6 per route
6. Sigma path (AppA, AppI, AppM) is always present
7. FAIL truth candidates always route to overflow
8. Board capacity limits are enforced

## Suggested chapter anchors

- `Ch09` — Retrieval and metro routing
- `Ch10` — Multi-lens solution construction
- `Ch15` — Cut architecture
- `Ch16` — Verification harnesses
