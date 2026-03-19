# KC27 PART 3 — PROMOTABILITY CHAIN

**Ingested**: 2026-03-19
**Source**: Google Doc — "KC27 3" (1nyDliFZp6oXa1EQURxcY23-BFdO7_sO88264p859cEI)
**Size**: 73KB

---

## Summary

KC27 extraction architecture Part 3. Defines the complete promotability chain from kernel to crown, including C2 replay lineage certification, map legality verification, seed return mechanics, and the compression-Mobius return-next seed cycle.

## Key Formal Objects

### 1. Kernel-to-Crown Promotability

The promotability chain is the sequence of gates an object must pass to travel from the kernel (innermost layer) to the crown (outermost promoted layer). Each gate tests a specific invariant:

- Kernel membership
- Chooser certification (C2)
- Replay validity
- Map legality
- Crown admission

### 2. C2 Replay Lineage

C2 is the replay certification standard. A lineage is C2-certified when:
- Every choice in the lineage can be replayed from the initial seed
- The replay produces identical output at every branch point
- The lineage hash matches the original execution hash

### 3. Map Legality

A map is legal when:
- All paths through the map terminate at valid crystal addresses
- No path violates conservation laws
- The map is replay-valid (reconstructible from seed)
- Cross-output stability holds across all SFCR lenses

### 4. Seed Return Cycle

The terminal sequence of the promotability chain:

```
Compression --> Mobius Return --> Next Seed
```

- **Compression**: The promoted object is compressed to its minimal representation
- **Mobius Return**: The compressed object traverses the Mobius loop back to the kernel
- **Next Seed**: The returned object becomes the seed for the next promotion cycle

This creates a closed loop: promotion is not a one-way ascent but a cycle that feeds back into the kernel.

## Structural Role

Part 3 completes the KC27 extraction architecture by closing the promotion loop. Parts 1 and 2 define the naming law and the admissibility gate; Part 3 shows how the entire system cycles — objects promote, compress, return, and reseed.
