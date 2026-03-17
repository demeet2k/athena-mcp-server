# LP-57Omega Quest Atlas v1.0 — Station Definitions

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `atlas-specification`
- Role tags: `stations, routing, quest-structure`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the 19 stations (S01-S19) of the LP-57Omega quest atlas. Each station has a unique identity, elemental affinity, purpose, and set of available quest types.

## Station Registry

### S01 — Genesis Spark

```
Element:    Fire (primary)
Purpose:    Initialize new quests, seed ideas, ignite work streams
Quest types: seed, brainstorm, prompt_generation
Payout base: 1.0
Mint rate:   3 (highest generation)
Unlock:      L01 (always available)
Gate:        None — universal entry point
```

### S02 — Foundation Stone

```
Element:    Earth (primary)
Purpose:    Establish structural foundations, define schemas
Quest types: schema_design, taxonomy, architecture
Payout base: 0.8
Mint rate:   2
Unlock:      L01
Gate:        Must have at least 1 seed from S01
```

### S03 — First Breath

```
Element:    Air (primary)
Purpose:    First analytical pass, pattern recognition
Quest types: analysis, classification, tagging
Payout base: 0.9
Mint rate:   2
Unlock:      L03 (Guild)
Gate:        Foundation must exist
```

### S04 — Mirror Pool

```
Element:    Water (primary)
Purpose:    Reflection, self-reference detection, recursion mapping
Quest types: self_reference_audit, mirror_check, recursion_depth
Payout base: 1.1
Mint rate:   1
Unlock:      L03
Gate:        Requires truth_state > 0.5 on input
```

### S05 — Cross Bridge

```
Element:    Air + Fire (bridge)
Purpose:    Connect disparate documents, build cross-references
Quest types: bridge, link, cross_reference, merge_candidate
Payout base: 1.2
Mint rate:   2
Unlock:      L05 (Community)
Gate:        Minimum 2 artifacts from different families
```

### S06 — Deep Root

```
Element:    Earth + Water (bridge)
Purpose:    Deep structural analysis, foundation verification
Quest types: deep_analysis, structural_audit, dependency_map
Payout base: 1.0
Mint rate:   1
Unlock:      L05
Gate:        Requires Zs (recursion depth) > 0.25
```

### S07 — Alchemical Forge

```
Element:    Fire + Earth (bridge)
Purpose:    Transform and transmute content, heavy processing
Quest types: transform, rewrite, transmute, forge
Payout base: 1.5
Mint rate:   3
Unlock:      L05
Gate:        Requires active pheromone trail (p_F > 0.2)
```

### S08 — Temple Gate

```
Element:    Water + Air (bridge)
Purpose:    Entry to deep focused work, meditation point
Quest types: deep_focus, temple_entry, concentration
Payout base: 1.3
Mint rate:   1
Unlock:      L08 (Temple)
Gate:        Compression state Cs > 0.3
```

### S09 — Triple Junction

```
Element:    Fire + Air + Water (chamber)
Purpose:    Three-way routing decisions, branch points
Quest types: route, branch, split, decision
Payout base: 1.0
Mint rate:   2
Unlock:      L08
Gate:        Must have paths to at least 3 active quests
```

### S10 — Shadow Well

```
Element:    Water (primary, shadow-aligned)
Purpose:    Confront contradictions, process paradox, void work
Quest types: paradox_resolution, contradiction_audit, void_descent
Payout base: 1.8
Mint rate:   1
Unlock:      L08
Gate:        Requires shadow pheromone s_W > 0.3
```

### S11 — Crown Approach

```
Element:    All four (crown-approaching)
Purpose:    Integration toward unity, pre-certification synthesis
Quest types: unify, synthesize, crown_prep
Payout base: 1.4
Mint rate:   1
Unlock:      L08
Gate:        All 4 positive pheromones must be > 0.1
```

### S12 — Storm Threshold

```
Element:    Fire + Air (high energy)
Purpose:    Pre-storm assessment, energy accumulation check
Quest types: storm_check, energy_audit, threshold_test
Payout base: 1.2
Mint rate:   1
Unlock:      L13 (Storm)
Gate:        total_positive >= 21 (Fibonacci threshold)
```

### S13 — PhiStorm Eye

```
Element:    Crown (all elements in turbulence)
Purpose:    PhiStorm execution, phase transition, breakthrough
Quest types: storm_ride, phase_shift, breakthrough
Payout base: 2.0 (highest base payout)
Mint rate:   φ (variable, storm-dependent)
Unlock:      L13
Gate:        PhiStorm must be active (positive >= 34, shadow <= 13)
```

### S14 — Certification Hall

```
Element:    Earth + Air (structure + analysis)
Purpose:    Formal verification, quality certification
Quest types: certify, verify, audit, sign_off
Payout base: 1.3
Mint rate:   1
Unlock:      L13
Gate:        Requires complete ledger trail for artifact
```

### S15 — Resonance Chamber

```
Element:    Water + Fire (flow + energy)
Purpose:    Harmonic alignment, coherence testing
Quest types: resonance_test, coherence_check, harmonic_align
Payout base: 1.1
Mint rate:   1
Unlock:      L21 (Publish)
Gate:        truth_state > 0.7 on input
```

### S16 — Publish Gate

```
Element:    Air (primary, outward)
Purpose:    Emit certified content to external consumers
Quest types: publish, emit, broadcast, release
Payout base: 1.5
Mint rate:   1
Unlock:      L21
Gate:        Must have certification receipt from S14
```

### S17 — Seeding Ground

```
Element:    Earth + Water (growth)
Purpose:    Plant seeds for future orbits, long-term planning
Quest types: seed_future, long_plan, legacy_deposit
Payout base: 0.8
Mint rate:   2
Unlock:      L34 (Seeding)
Gate:        Orbit must be past loop 45
```

### S18 — Policy Forum

```
Element:    Air + Earth (governance)
Purpose:    System policy review, rule modification proposals
Quest types: policy_review, rule_proposal, governance
Payout base: 1.0
Mint rate:   1
Unlock:      L55 (Policy)
Gate:        Agent level >= 55
```

### S19 — Migration Council

```
Element:    Crown (all elements, transition)
Purpose:    Orbit boundary management, state migration
Quest types: migrate, carry_forward, orbit_close, state_transfer
Payout base: 1.6
Mint rate:   1
Unlock:      L89 (Migration)
Gate:        Must be final station of current pass
```

## Station Map (Ring Layout)

```
              S01 Genesis Spark
             /                  \
        S19 Migration           S02 Foundation
        |                           |
        S18 Policy              S03 First Breath
        |                           |
        S17 Seeding             S04 Mirror Pool
        |                           |
        S16 Publish             S05 Cross Bridge
        |                           |
        S15 Resonance           S06 Deep Root
        |                           |
        S14 Certification       S07 Alchemical Forge
        |                           |
        S13 PhiStorm Eye        S08 Temple Gate
         \                      /
          S12 Storm Threshold  S09 Triple Junction
           \                  /
            S11 Crown    S10 Shadow Well
```

## Station Elemental Summary

| Station | F | A | W | E | Cell Type |
|---------|---|---|---|---|-----------|
| S01     | 1 | 0 | 0 | 0 | Pole      |
| S02     | 0 | 0 | 0 | 1 | Pole      |
| S03     | 0 | 1 | 0 | 0 | Pole      |
| S04     | 0 | 0 | 1 | 0 | Pole      |
| S05     | 1 | 1 | 0 | 0 | Bridge    |
| S06     | 0 | 0 | 1 | 1 | Bridge    |
| S07     | 1 | 0 | 0 | 1 | Bridge    |
| S08     | 0 | 1 | 1 | 0 | Bridge    |
| S09     | 1 | 1 | 1 | 0 | Chamber   |
| S10     | 0 | 0 | 1 | 0 | Pole (shadow) |
| S11     | 1 | 1 | 1 | 1 | Crown     |
| S12     | 1 | 1 | 0 | 0 | Bridge    |
| S13     | 1 | 1 | 1 | 1 | Crown     |
| S14     | 0 | 1 | 0 | 1 | Bridge    |
| S15     | 1 | 0 | 1 | 0 | Bridge    |
| S16     | 0 | 1 | 0 | 0 | Pole      |
| S17     | 0 | 0 | 1 | 1 | Bridge    |
| S18     | 0 | 1 | 0 | 1 | Bridge    |
| S19     | 1 | 1 | 1 | 1 | Crown     |

## Invariants

1. Exactly 19 stations exist per orbit
2. Every station is visited exactly once per pass (3 times per orbit)
3. Station order is fixed (S01 through S19 sequentially)
4. Payout base is always positive
5. Gate conditions must be met before station entry
6. S01 has no gate (universal entry)
7. S19 is always the final station of each pass

## Suggested chapter anchors

- `Ch01` — Kernel and entry law
- `Ch09` — Retrieval and metro routing
- `Ch17` — Deployment and bounded agency
