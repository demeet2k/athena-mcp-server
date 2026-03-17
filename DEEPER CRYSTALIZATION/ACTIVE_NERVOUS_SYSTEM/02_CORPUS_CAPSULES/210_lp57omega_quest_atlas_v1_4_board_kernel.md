# LP-57Omega Quest Atlas v1.4 — Deterministic Board Kernel

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `kernel-specification`
- Role tags: `kernel, determinism, board, functions`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the deterministic board kernel: the core set of pure functions that transform candidates into boards. The fundamental invariant is that identical input always produces identical output.

## Core Invariant

```
DETERMINISM LAW:
  For all candidate lists C:
    emit_orbit_boards(C) == emit_orbit_boards(C)

  No randomness. No external state. No side effects.
  Same input -> same output. Always.
```

## Kernel Function Signatures

### normalize_candidate()

```python
def normalize_candidate(c: Candidate) -> Candidate:
    """
    Clamp and validate all candidate fields.
    Pure function: no side effects.

    Input:  Raw candidate with potentially invalid fields
    Output: Normalized candidate with all fields in valid ranges

    Operations:
      - station: clamp to [1, 19]
      - orbit_index: max(0, value)
      - pass_index: clamp to [1, 3]
      - elemental_signature: normalize to unit Vec4
      - quest_class: validate against station allowed set
      - truth_state: assert in {OK, NEAR, AMBIG, FAIL}
      - coordinate_stamp: infer if missing

    Postconditions:
      - All numeric fields in valid ranges
      - elemental_signature is unit vector
      - quest_class is valid for station
    """
```

### guild_score()

```python
def guild_score(c: NormalizedCandidate, route: Route) -> float:
    """
    Compute guild board score for a candidate.
    Pure function: deterministic float output.

    Formula:
      score = base * truth_weight * difficulty * pressure
            * community * guild_amp

    Components:
      base:        station.payout_base (from station definition)
      truth_weight: OK=1.0, NEAR=0.618, AMBIG=0.382, FAIL=0.0
      difficulty:  1.0 + 0.25 * (station - 1) / 18
      pressure:    sum of route.obligations (0.0 if empty)
      community:   1.0 + 0.25 * (party_size - 1) for community classes
                   1.0 for non-community classes
      guild_amp:   1.0 + 0.10 * |target_set|

    Range: [0.0, ~15.0] (theoretical maximum)

    Note: FAIL truth always produces score = 0.0
    """
```

### temple_score()

```python
def temple_score(c: NormalizedCandidate, route: Route) -> float:
    """
    Compute temple board score for a candidate.
    Pure function: deterministic float output.

    Formula:
      score = base * truth_weight * depth * temple_amp

    Components:
      base:        station.payout_base (from station definition)
      truth_weight: OK=1.0, NEAR=0.618, AMBIG=0.382, FAIL=0.0
      depth:       1.0 + 0.1 * |witnesses| + 0.1 * |replays|
      temple_amp:  1.0 + 0.15 * |evidence_set|

    Range: [0.0, ~10.0] (theoretical maximum)

    Note: Temple scoring favors depth over breadth.
          More witnesses and evidence = higher score.
    """
```

### assign_guild_queue()

```python
def assign_guild_queue(c: NormalizedCandidate, route: Route) -> str:
    """
    Assign candidate to a guild queue.
    Pure function: deterministic queue name.

    Decision tree:
      if truth == FAIL:           return 'overflow'
      if quest_class in REPAIR:   return 'repair'
      if publish_intent and OK:   return 'featured'
      if quest_class in STORM:    return 'storm'
      if quest_class in COMMUNITY:return 'recruit'
      else:                       return 'ladder'

    Queue names: featured | ladder | repair | storm | recruit | overflow

    Note: Decision tree is evaluated top-to-bottom.
          First matching condition wins.
    """
```

### assign_temple_queue()

```python
def assign_temple_queue(c: NormalizedCandidate, route: Route) -> str:
    """
    Assign candidate to a temple queue.
    Pure function: deterministic queue name.

    Decision tree:
      if truth == FAIL:                return 'overflow'
      if quest_class in CERTIFY:       return 'certification'
      if truth == NEAR and closure_ready: return 'near_closure'
      if truth == AMBIG:               return 'ambiguities'
      if coord.Cs > 0.5:              return 'compression'
      if quest_class == publish:       return 'sovereign'
      else:                            return 'compression'  (default)

    Queue names: certification | near_closure | ambiguities |
                 compression | sovereign | overflow

    Note: Compression is the default temple queue.
    """
```

### build_guild_board()

```python
def build_guild_board(candidates: list[Candidate]) -> list[BoardEntry]:
    """
    Full guild board construction pipeline.
    Pure function: deterministic board output.

    Pipeline:
      1. Normalize all candidates
      2. Compile routes for each
      3. Filter to guild-channel candidates
      4. Score each with guild_score()
      5. Assign queue with assign_guild_queue()
      6. Sort by score descending
      7. Enforce capacity limit (max 16)
      8. Excess -> overflow

    Output: List of BoardEntry, sorted by score descending
    """
    normalized = [normalize_candidate(c) for c in candidates]
    routed = [compile_route(c) for c in normalized]
    guild = [rc for rc in routed if channel_split(rc) == 'GUILD']

    entries = []
    for rc in guild:
        score = guild_score(rc.candidate, rc.route)
        queue = assign_guild_queue(rc.candidate, rc.route)
        entries.append(BoardEntry(score=score, queue=queue, rc=rc))

    entries.sort(key=lambda e: -e.score)

    # Capacity enforcement
    if len(entries) > 16:
        overflow = entries[16:]
        entries = entries[:16]
        for e in overflow:
            e.queue = 'overflow'
        entries.extend(overflow)

    return entries
```

### build_temple_board()

```python
def build_temple_board(candidates: list[Candidate]) -> list[BoardEntry]:
    """
    Full temple board construction pipeline.
    Pure function: deterministic board output.

    Pipeline: Same as guild but with temple scoring/queuing.
    Capacity limit: max 8 entries.

    Output: List of BoardEntry, sorted by score descending
    """
    normalized = [normalize_candidate(c) for c in candidates]
    routed = [compile_route(c) for c in normalized]
    temple = [rc for rc in routed if channel_split(rc) == 'TEMPLE']

    entries = []
    for rc in temple:
        score = temple_score(rc.candidate, rc.route)
        queue = assign_temple_queue(rc.candidate, rc.route)
        entries.append(BoardEntry(score=score, queue=queue, rc=rc))

    entries.sort(key=lambda e: -e.score)

    if len(entries) > 8:
        overflow = entries[8:]
        entries = entries[:8]
        for e in overflow:
            e.queue = 'overflow'
        entries.extend(overflow)

    return entries
```

### emit_orbit_boards()

```python
def emit_orbit_boards(candidates: list[Candidate]) -> dict:
    """
    Top-level kernel driver. Produces both boards.
    Pure function: THE determinism guarantee lives here.

    Input:  Raw candidate list
    Output: {"guild": [...], "temple": [...]}

    This function is the single entry point for board generation.
    All internal calls are to pure functions.
    No external state is read or modified.

    The golden test vector test_board_determinism verifies:
      emit_orbit_boards(C) == emit_orbit_boards(C)
    for a fixed canonical candidate set C.
    """
    return {
        "guild":  build_guild_board(candidates),
        "temple": build_temple_board(candidates),
    }
```

## Data Types

```typescript
interface Candidate {
  artifact_id:         string;
  station:             int;        // 1..19
  orbit_index:         int;        // >= 0
  pass_index:          int;        // 1..3
  quest_class:         string;
  elemental_signature: Vec4;
  truth_state:         TruthState; // OK|NEAR|AMBIG|FAIL
  coordinate_stamp:    Coord12;
  publish_intent:      boolean;
  party_size:          int;        // >= 1
  target_set:          string[];
  evidence_set:        string[];
  dependencies:        string[];
}

interface Route {
  sigma:       string[];    // Always ['AppA', 'AppI', 'AppM']
  lens_hub:    string;
  overlay:     string | null;
  publish_hub: string | null;
  tunnels:     Tunnel[];
  obligations: float[];
  witnesses:   string[];
  replays:     string[];
  legal:       boolean;
  droplog:     string[];
}

interface BoardEntry {
  score:     float;
  queue:     string;
  candidate: Candidate;
  route:     Route;
}

enum TruthState {
  OK   = "OK",
  NEAR = "NEAR",
  AMBIG = "AMBIG",
  FAIL = "FAIL"
}
```

## Truth Weight Constants

```
TRUTH_WEIGHTS = {
  'OK':    1.000,
  'NEAR':  0.618,   // = phi-inverse
  'AMBIG': 0.382,   // = phi-inverse-squared
  'FAIL':  0.000
}

Note: NEAR/AMBIG weights are phi-derived.
  OK/NEAR ratio = 1/0.618 = phi
  NEAR/AMBIG ratio = 0.618/0.382 = phi
  This creates a phi-scaled truth gradient.
```

## Kernel Verification

The kernel is verified by the golden test vector suite (v1.6):

```
Required passing vectors for kernel certification:
  - board_determinism:   Same input produces same output
  - board_guild_scoring: Station ordering preserved in scores
  - route_sigma_lock:    Sigma path always present
  - route_hub_budget:    Hub count <= 6

All 4 must pass. Any failure blocks release.
```

## Invariants

1. All kernel functions are pure (no side effects)
2. emit_orbit_boards() is the sole entry point
3. Same input always produces same output (determinism)
4. FAIL truth always produces score = 0.0
5. Truth weights follow phi scaling
6. Guild capacity = 16, Temple capacity = 8
7. Overflow queue catches all excess
8. Sigma path is never removed

## Suggested chapter anchors

- `Ch01` — Kernel and entry law
- `Ch09` — Retrieval and metro routing
- `Ch15` — Cut architecture
- `Ch16` — Verification harnesses and replay kernels
