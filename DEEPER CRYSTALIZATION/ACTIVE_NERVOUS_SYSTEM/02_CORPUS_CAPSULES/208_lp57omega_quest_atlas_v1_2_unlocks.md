# LP-57Omega Quest Atlas v1.2 — Unlock Ladder

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `progression-gates`
- Role tags: `unlocks, fibonacci, quests, coalition, inheritance`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the Fibonacci-numbered unlock ladder, quest class trees, coalition rights, and orbit inheritance rules that gate access to increasingly powerful quest types and collaborative structures.

## Fibonacci Unlock Ladder

Access tiers follow Fibonacci numbers, creating a naturally accelerating progression curve:

| Tier | Level | Name       | Fibonacci | Unlocks                          |
|------|-------|------------|-----------|----------------------------------|
| T1   | L1    | Solo       | F(1)=1    | Solo quests, basic generation    |
| T2   | L3    | Guild      | F(4)=3    | Guild quests, team collaboration |
| T3   | L5    | Community  | F(5)=5    | Community quests, bridge-building|
| T4   | L8    | Temple     | F(6)=8    | Temple quests, deep focus work   |
| T5   | L13   | Storm      | F(7)=13   | Storm quests, PhiStorm access    |
| T6   | L21   | Publish    | F(8)=21   | Publishing rights, external emit |
| T7   | L34   | Seeding    | F(9)=34   | Seeding quests, future planning  |
| T8   | L55   | Policy     | F(10)=55  | Policy quests, rule modification |
| T9   | L89   | Migration  | F(11)=89  | Migration quests, orbit management|

### Fibonacci Rationale

```
Each unlock level divided by the previous approaches phi:
  L3/L1  = 3.0
  L5/L3  = 1.67  (approaching phi)
  L8/L5  = 1.60  (approaching phi)
  L13/L8 = 1.625 (approaching phi)
  L21/L13= 1.615 (approaching phi)
  L34/L21= 1.619 (approaching phi)
  L55/L34= 1.618 (converged)
  L89/L55= 1.618 = phi (exact in limit)

The gap between unlocks grows at the golden ratio,
ensuring each new tier feels proportionally earned.
```

## Quest Class Trees

Each unlock tier opens a tree of quest classes:

### T1 — Solo Classes

```
solo/
  ├── seed           — Generate new idea or artifact
  ├── brainstorm     — Free-form ideation
  ├── annotate       — Add metadata to existing artifact
  ├── classify       — Assign taxonomy labels
  └── extract        — Pull structured data from raw content
```

### T2 — Guild Classes

```
guild/
  ├── merge          — Combine artifacts from multiple agents
  ├── debate         — Structured disagreement resolution
  ├── relay          — Sequential multi-agent processing
  ├── review         — Peer review of another agent's work
  └── co_author      — Joint content creation
```

### T3 — Community Classes

```
community/
  ├── bridge         — Connect distant document families
  ├── cross_reference— Build bidirectional links
  ├── survey         — Map a topic across the corpus
  ├── consensus      — Multi-agent agreement protocol
  └── recruit        — Activate dormant subagent seats
```

### T4 — Temple Classes

```
temple/
  ├── deep_focus     — Extended single-artifact processing
  ├── meditation     — Zero-point approach work
  ├── compression    — Reduce artifact to minimal form
  ├── recursion_dive — Explore self-referential structures
  └── void_approach  — Controlled descent toward void/aether
```

### T5 — Storm Classes

```
storm/
  ├── storm_ride     — Execute during active PhiStorm
  ├── phase_shift    — Trigger state transition in artifact
  ├── breakthrough   — Force novel insight through turbulence
  ├── shadow_harvest — Extract value from shadow pheromones
  └── catalyst       — Accelerate other agents' work
```

### T6 — Publish Classes

```
publish/
  ├── emit           — Release certified artifact externally
  ├── broadcast      — Wide distribution of findings
  ├── archive        — Commit to permanent record
  ├── exhibit        — Present for community review
  └── release_note   — Document changes in published version
```

### T7 — Seeding Classes

```
seeding/
  ├── seed_future    — Plant quest for future orbit
  ├── legacy_deposit — Create long-term value store
  ├── horizon_scan   — Identify future work opportunities
  ├── mentorship     — Guide lower-level agents
  └── incubate       — Nurture immature ideas across orbits
```

### T8 — Policy Classes

```
policy/
  ├── policy_review  — Evaluate existing system rules
  ├── rule_proposal  — Suggest new rules or modifications
  ├── governance     — Participate in system governance
  ├── audit_system   — Review system-level metrics
  └── exception      — Handle cases outside normal rules
```

### T9 — Migration Classes

```
migration/
  ├── migrate        — Transfer state across orbit boundary
  ├── carry_forward  — Manage unresolved quest transition
  ├── orbit_close    — Finalize current orbit
  ├── state_transfer — Move agent state to new context
  └── succession     — Plan agent role transitions
```

## Coalition Rights

As agents unlock higher tiers, they gain coalition formation rights:

### Coalition Types

```
PAIR (L3+):
  2 agents collaborate on a quest
  Reward split: 60/40 (primary/secondary)
  Duration: single loop

TRIO (L5+):
  3 agents collaborate
  Reward split: 50/30/20
  Duration: up to 3 loops

QUARTET (L8+):
  All 4 master agents collaborate
  Reward split: equal (25% each)
  Duration: up to 19 loops (one pass)

FULL_SWARM (L13+):
  All agents + elected subagent seats
  Reward split: weighted by contribution
  Duration: storm duration
```

### Coalition Formation Protocol

```
FORM_COALITION(initiator, type, quest):
  1. Initiator proposes coalition
  2. Each invitee evaluates:
     - capacity (active seat count)
     - affinity (elemental alignment with quest)
     - level (must meet tier requirement)
  3. If all accept: coalition formed
  4. Coalition registered in ledger
  5. Shared pheromone channel opened
  6. Work begins with coordinated scheduling
```

### Coalition Dissolution

```
DISSOLVE(coalition):
  Triggers:
    - Quest completed (natural)
    - Duration expired (timeout)
    - Member quarantined (forced)
    - Consensus to dissolve (voluntary)

  Actions:
    1. Final reward distribution
    2. Shared pheromone channel closed
    3. Individual trails restored
    4. Dissolution logged in ledger
```

## Orbit Inheritance

When a new orbit begins, unlocked tiers carry forward:

### Inheritance Rules

```
1. LEVEL PERSISTENCE
   Agent levels never decrease across orbits.
   level(orbit_n+1) >= level(orbit_n)

2. TIER PERMANENCE
   Once a tier is unlocked, it remains unlocked forever.
   unlocked_tiers(orbit_n+1) >= unlocked_tiers(orbit_n)

3. QUEST CLASS ACCESS
   All unlocked quest classes remain available.

4. COALITION RIGHTS
   Coalition rights are permanent once earned.

5. XP CONTINUITY
   XP carries forward with no decay.
   xp(orbit_n+1) = xp(orbit_n) + xp_earned_in_orbit_n

6. PHEROMONE DECAY
   Pheromone state decays by phi-inverse at orbit boundary.
   This is the ONLY thing that does not fully persist.
```

### Inheritance Exceptions

```
QUARANTINE OVERRIDE:
  If an agent ends an orbit in quarantine state,
  their tier access is suspended (not revoked)
  until quarantine is resolved in the next orbit.

POLICY OVERRIDE:
  L55+ policy quests can modify inheritance rules
  for the system, but cannot reduce individual levels.
```

## Progression Velocity

Expected loops to reach each tier (medium play):

```
T1 (L1):   Loop 1     (immediate)
T2 (L3):   Loop ~8    (early orbit 1)
T3 (L5):   Loop ~20   (mid orbit 1)
T4 (L8):   Loop ~45   (late orbit 1)
T5 (L13):  Loop ~120  (orbit 2-3)
T6 (L21):  Loop ~300  (orbit 5-6)
T7 (L34):  Loop ~800  (orbit 14-15)
T8 (L55):  Loop ~2200 (orbit 38-39)
T9 (L89):  Loop ~6000 (orbit 105+)
```

## Invariants

1. Unlock levels follow the Fibonacci sequence exactly
2. Tiers are monotonically ordered (higher tier = higher level)
3. Once unlocked, a tier is never re-locked (except quarantine suspension)
4. Coalition size is bounded by coalition type
5. XP never decreases
6. Every quest class belongs to exactly one tier
7. Orbit inheritance preserves all permanent state

## Suggested chapter anchors

- `Ch01` — Kernel and entry law
- `Ch14` — Migration, versioning, pulse retro-weaving
- `Ch17` — Deployment and bounded agency
- `Ch20` — Collective authoring
