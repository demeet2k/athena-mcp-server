# KC27 ADMISSIBILITY — SFCR.DLS4.C2

**Ingested**: 2026-03-19
**Source**: Google Doc — "KC27 Admissibility SFCR.DLS4.C2" (1Ad9mXq0127AVwdteuFRIs0x_rzDeo9Y6h_-eektnmHQ)
**Size**: 88KB

---

## Summary

The admissibility engine for the 4x4 DLS quantum crystal. This document defines the complete pipeline from Mobius/SFCR kernel through live-cell substrate to the first replay-certified chooser-lineage, then to replay-valid map, and finally to crown admission filtering.

## Key Formal Objects

### 1. Admissibility Pipeline

Five-stage cascade:

1. **Mobius/SFCR Kernel**: The foundational kernel that generates the admissibility field from the Mobius symmetry group and SFCR element decomposition
2. **Live-Cell Substrate**: The kernel output is planted into the live-cell substrate where it becomes a running process
3. **Replay-Certified Chooser-Lineage**: The first chooser-lineage that can be replayed from its origin — the C2 certification
4. **Replay-Valid Map**: The chooser-lineage produces a map that is replay-valid: every path through it can be reconstructed
5. **Crown Admission Filtering**: The final gate — the crown filters the replay-valid map for admission into the promoted layer

### 2. Status Vector

The system's current state is encoded as a 5-component status vector:

Sigma_now = (K, C, L, M, P) = (OPEN, FROZEN, OPEN, BLOCKED, FILTERED)

Where:
- K (Kernel): OPEN — the Mobius/SFCR kernel is active and accepting inputs
- C (Chooser): FROZEN — the chooser-lineage is locked after C2 certification
- L (Lineage): OPEN — the lineage record is still accumulating
- M (Map): BLOCKED — the replay-valid map has encountered a blockage
- P (Promotion): FILTERED — the crown admission filter is active, selectively passing

### 3. 4x4 DLS Quantum Crystal

The substrate is a 4x4 doubly-linked square (DLS) — a quantum crystal where each cell participates in exactly 4 row constraints and 4 column constraints simultaneously, creating a 16-cell lattice with full double-link coverage.

## Structural Role

This document is the admissibility gate for the KC27 system. Nothing enters the promoted crown layer without passing through this pipeline. The status vector provides real-time diagnostics of where the pipeline is open, frozen, or blocked.
