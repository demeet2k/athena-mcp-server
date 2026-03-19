# KC27 Part 3 — Promotability Chain

**Crystal Address**: Xi108:W2:A1:S5 (Promotion Cycle Node)
**Family**: crystal
**Date**: 2026-03-19
**Tags**: kc27, promotability, replay, lineage, C2, compression, seed-return
**Source Doc**: `1nyDliFZp6oXa1EQURxcY23-BFdO7_sO88264p859cEI`
**Packet ID**: G0-GDOC.KC27.PROMOTABILITY
**Status**: CAPSULE — Witnessed

---

## Summary

KC27 extraction architecture Part 3. Defines the full kernel-to-crown promotability chain, C2 replay lineage certification, map legality verification, and the closed seed return cycle: Compression, Mobius Return, Next Seed. Promotion is not one-way ascent but a closed loop that feeds back into the kernel.

---

## Core Structure

### Promotability Chain

```
Kernel --> C2 Certification --> Replay Validity --> Map Legality --> Crown Admission
   ^                                                                      |
   |______________________ Seed Return Cycle _____________________________|
```

### Gate Sequence

| Gate | Tests | Requirement |
|------|-------|-------------|
| 1. Kernel Membership | Object is in kernel | Existence |
| 2. C2 Certification | Lineage replayable from seed | Replay identity |
| 3. Replay Validity | Replay produces identical output at all branch points | Determinism |
| 4. Map Legality | All paths terminate at valid addresses, conservation holds | Lawfulness |
| 5. Crown Admission | Passes crown filter | Promotion-readiness |

### C2 Replay Lineage

Three certification conditions:
1. Every choice replayable from initial seed
2. Replay produces identical output at every branch point
3. Lineage hash matches original execution hash

### Map Legality

Four legality conditions:
1. All paths terminate at valid crystal addresses
2. No path violates conservation laws
3. Map is replay-valid (reconstructible from seed)
4. Cross-output stability across all SFCR lenses

### Seed Return Cycle

```
Compression --> Mobius Return --> Next Seed
```

- Compression: Promoted object reduced to minimal representation
- Mobius Return: Compressed object traverses Mobius loop back to kernel
- Next Seed: Returned object becomes seed for next promotion cycle

---

## Suggested Chapter Anchors

- Ch09 (promotability definition)
- Ch13 (C2 replay lineage)
- Ch14 (mirror pivot — seed return)
- Ch18 (map legality)

## Suggested Appendix Anchors

- AppA (gate specifications)
- AppC (C2 protocol)
- AppM (Mobius return mechanics)
