# KC27 Admissibility Engine — SFCR.DLS4.C2

**Crystal Address**: Xi108:W2:A1:S4 (Admissibility Gate)
**Family**: crystal
**Date**: 2026-03-19
**Tags**: kc27, admissibility, DLS, 4x4, mobius, SFCR, kernel, crown
**Source Doc**: `1Ad9mXq0127AVwdteuFRIs0x_rzDeo9Y6h_-eektnmHQ`
**Packet ID**: G0-GDOC.KC27.ADMISSIBILITY
**Status**: CAPSULE — Witnessed

---

## Summary

Defines the admissibility engine for the 4x4 DLS quantum crystal. Five-stage pipeline: Mobius/SFCR kernel, live-cell substrate, replay-certified chooser-lineage (C2), replay-valid map, crown admission filtering. Provides real-time diagnostics via the 5-component status vector Sigma_now.

---

## Core Structure

### Admissibility Pipeline

```
Mobius/SFCR Kernel --> Live-Cell Substrate --> C2 Chooser-Lineage --> Replay-Valid Map --> Crown Admission
```

| Stage | Input | Output | Gate |
|-------|-------|--------|------|
| 1. Kernel | SFCR decomposition | Admissibility field | Mobius symmetry |
| 2. Substrate | Kernel field | Running process | Live-cell activation |
| 3. C2 Lineage | Running process | Certified lineage | Replay certification |
| 4. Map | Certified lineage | Valid map | Replay validity |
| 5. Crown | Valid map | Admitted object | Crown filter |

### Status Vector

Sigma_now = (K, C, L, M, P) = (OPEN, FROZEN, OPEN, BLOCKED, FILTERED)

| Component | Symbol | Current | Meaning |
|-----------|--------|---------|---------|
| Kernel | K | OPEN | Accepting inputs |
| Chooser | C | FROZEN | Locked after C2 certification |
| Lineage | L | OPEN | Still accumulating |
| Map | M | BLOCKED | Encountered blockage |
| Promotion | P | FILTERED | Crown filter active |

### 4x4 DLS Quantum Crystal

- 16-cell lattice with full double-link coverage
- Each cell: 4 row constraints + 4 column constraints
- Doubly-linked square structure ensures every path is bidirectional

---

## Suggested Chapter Anchors

- Ch04 (kernel structure)
- Ch08 (live-cell substrate)
- Ch12 (replay certification)
- Ch16 (crown filtering)

## Suggested Appendix Anchors

- AppA (DLS specification)
- AppC (C2 certification protocol)
- AppM (Mobius group tables)
