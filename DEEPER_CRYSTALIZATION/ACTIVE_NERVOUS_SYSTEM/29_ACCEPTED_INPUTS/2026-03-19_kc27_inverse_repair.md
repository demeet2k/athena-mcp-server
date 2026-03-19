# KC27 PART 3 — BOOKS VI-VII: INVERSE SEARCH AND REPAIR FIELD

**Ingested**: 2026-03-19
**Source**: Google Doc — "Untitled (KC27 Part 3 — Books VI-VII)" (11iwlmMouvyW1MTHFme9J7j1uYBINeMqevgV1MqWT6-0)
**Size**: 101KB

---

## Summary

Books VI and VII of the KC27 Part 3 extraction architecture. Book VI defines the Inverse Search and Repair Field (Chapters 16-18). Book VII covers the Lift Engine and Execution layer. The repair field is built on a triad of failure modes/paradoxes, repair operators, and regime conditions.

## Key Formal Objects

### 1. Book VI — Inverse Search and Repair Field (Ch16-18)

The repair field is the organism's self-correction mechanism. When a promotion path fails, the inverse search locates the failure point and the repair field applies corrective operators.

#### Chapter 16 — Failure Modes and Paradoxes

Catalogs the ways promotion can fail:
- Address collision (two objects claim the same crystal coordinate)
- Mirror violation (an object in chapter k has no valid correspondent in chapter 28 - k)
- Replay divergence (replaying a lineage produces different output)
- Conservation breach (a promotion step violates a conservation law)
- Circular dependency (promotion requires an object that itself requires promotion)

#### Chapter 17 — Repair Operators

The operators that correct failures:
- Re-addressing (assign a new crystal coordinate)
- Mirror completion (construct the missing mirror correspondent)
- Lineage rebase (rebuild the lineage from a known-good checkpoint)
- Conservation restoration (inject the missing conserved quantity)
- Dependency resolution (topological sort and staged promotion)

#### Chapter 18 — Regime Conditions

The conditions under which repair operators are permitted to act:
- Repair budget (maximum number of repair operations per cycle)
- Cascading limit (maximum depth of repair-triggered repairs)
- Stability threshold (minimum resonance score after repair)
- Rollback protocol (when repair fails, how to revert cleanly)

### 2. Repair Triad

The three components form a closed diagnostic-corrective loop:

```
Failure Modes/Paradoxes --> Repair Operators --> Regime Conditions
         ^                                            |
         |____________________________________________|
                    (feedback / new failures)
```

### 3. Book VII — Lift Engine / Execution

The execution layer that runs the repaired promotion chain. After the repair field has corrected all failures, the lift engine executes the actual promotion, moving objects from kernel to crown through the certified path.

## Structural Role

Books VI-VII complete the KC27 extraction architecture by providing the error-handling and execution layers. The earlier books define what promotion is and how to certify it; these books define what happens when it fails and how to recover.
