# KC27 Part 3 — Books VI-VII: Inverse Search and Repair Field

**Crystal Address**: Xi108:W2:A1:S6 (Repair Field Node)
**Family**: naming
**Date**: 2026-03-19
**Tags**: kc27, inverse, repair, failure-modes, paradox, regime
**Source Doc**: `11iwlmMouvyW1MTHFme9J7j1uYBINeMqevgV1MqWT6-0`
**Packet ID**: G0-GDOC.KC27.REPAIR
**Status**: CAPSULE — Witnessed

---

## Summary

Books VI and VII of KC27 Part 3. Book VI defines the Inverse Search and Repair Field (Chapters 16-18) built on the repair triad: failure modes/paradoxes, repair operators, and regime conditions. Book VII covers the Lift Engine and Execution layer that runs the repaired promotion chain.

---

## Core Structure

### Book VI — Inverse Search and Repair Field

#### Chapter 16: Failure Modes and Paradoxes

| Failure Mode | Description |
|-------------|-------------|
| Address collision | Two objects claim same crystal coordinate |
| Mirror violation | Object in chapter k has no correspondent in chapter 28 - k |
| Replay divergence | Replaying lineage produces different output |
| Conservation breach | Promotion step violates conservation law |
| Circular dependency | Promotion requires object that itself requires promotion |

#### Chapter 17: Repair Operators

| Operator | Corrects |
|----------|----------|
| Re-addressing | Address collision |
| Mirror completion | Mirror violation |
| Lineage rebase | Replay divergence |
| Conservation restoration | Conservation breach |
| Dependency resolution | Circular dependency (topological sort + staged promotion) |

#### Chapter 18: Regime Conditions

| Condition | Function |
|-----------|----------|
| Repair budget | Maximum repair operations per cycle |
| Cascading limit | Maximum depth of repair-triggered repairs |
| Stability threshold | Minimum resonance score after repair |
| Rollback protocol | Clean reversion when repair fails |

### Repair Triad (Closed Loop)

```
Failure Modes/Paradoxes --> Repair Operators --> Regime Conditions
         ^                                            |
         |____________________________________________|
                    (feedback / new failures)
```

### Book VII — Lift Engine / Execution

The execution layer that runs the repaired promotion chain:
- All failures corrected by repair field
- Lift engine executes actual promotion: kernel to crown via certified path
- Final witness emitted upon successful lift

---

## Suggested Chapter Anchors

- Ch16 (failure modes)
- Ch17 (repair operators)
- Ch18 (regime conditions)
- Ch19 (lift engine)

## Suggested Appendix Anchors

- AppA (failure mode catalog)
- AppC (repair operator specifications)
- AppM (regime condition parameters)
