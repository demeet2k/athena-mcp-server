# Depth Tensor Registry and Zero/Lock Layers

## 7-Component Depth Tensor

$$\mathbf{D}(x) = \langle d_S; d_R; d_C; d_G; d_T; d_Z; d_L \rangle$$

| # | Component | Symbol | Meaning |
|---|-----------|--------|---------|
| 1 | Structural Depth | d_S | How many nested structural layers |
| 2 | Routing Depth | d_R | How many metro/corridor hops from seed |
| 3 | Clock Depth | d_C | Which nested clock level governs |
| 4 | Geometry Depth | d_G | Which sacred-geometry tier is active |
| 5 | Transform Depth | d_T | How many operators have been applied from seed |
| 6 | Zero Depth | d_Z | How close to zero-point (lower = deeper) |
| 7 | Lock Depth | d_L | How many live-lock constraints active |

### Depth Tensor Laws
- **Monotonicity:** d_T increases strictly with each operator application
- **Conservation:** d_Z + d_L = constant over any closed 420-beat cycle
- **Nesting:** d_C determines which clocks are visible (smaller d_C = fewer clocks)
- **Restoration:** The restore pointer in LC must be sufficient to recover all 7 components

---

## Zero Registry (13 Entries)

Zero-points are where cyclic structure collapses to a singularity. They represent prima materia — pure potential before differentiation.

| # | Code | Name | Type | Stage First Active |
|---|------|------|------|-------------------|
| 1 | Z_seed | Seed Zero | origin | S3 |
| 2 | Z_face | Face Zero | face collapse | S4 |
| 3 | Z_parity | Parity Zero | orientation collapse | S4M |
| 4 | Z_sigma | Sigma Zero | symmetry collapse | S5S |
| 5 | Z_registry | Registry Zero | compression collapse | S5C |
| 6 | Z_petal | Petal Zero | Mobius center | S6M |
| 7 | Z_crown | Crown Zero | authority origin | S6A |
| 8 | Z_weave3 | 3-Weave Zero | 3-fold center | F3 |
| 9 | Z_weave5 | 5-Weave Zero | 5-fold center | F5 |
| 10 | Z_weave7 | 7-Weave Zero | 7-fold center | F7 |
| 11 | Z_weave9 | 9-Weave Zero | 9-fold center | F9 |
| 12 | Z_spine | Spine Zero | resonant spine origin | PS |
| 13 | Z_omega | Omega Zero | terminal zero | Omega |

### Zero-Point Laws
- Every stage introduces at most one new zero-point type
- Z_omega subsumes all prior zero-points
- The zero registry is append-only (new zeros are added, never removed)
- At Omega: all 13 zeros are simultaneously accessible

---

## Live-Lock Registry (14 Entries)

Live-locks are stable cyclic attractors — states that the system orbits without escaping. They represent crystallized patterns.

| # | Code | Name | Type | Period |
|---|------|------|------|--------|
| 1 | L_face4 | Face Lock | 4-cycle | 4 |
| 2 | L_parity | Parity Lock | 2-cycle | 2 |
| 3 | L_triadic | Triadic Lock | 3-cycle (Su/Me/Sa) | 3 |
| 4 | L_anti4 | Anti-Spin Lock | 4-beat | 4 |
| 5 | L_bridge5 | Bridge Lock | 5-gear | 5 |
| 6 | L_gate7 | Gate Lock | 7-spoke | 7 |
| 7 | L_mobius12 | Mobius Lock | 12-beat petal cycle | 12 |
| 8 | L_weave20 | 5-Weave Lock | 20-beat | 20 |
| 9 | L_weave28 | 7-Weave Lock | 28-beat | 28 |
| 10 | L_weave36 | 9-Weave Lock | 36-beat | 36 |
| 11 | L_sigma60 | Sigma Lock | 60-orbit | 60 |
| 12 | L_crown420 | Crown Lock | 420-beat year | 420 |
| 13 | L_super1260 | Super Lock | 1260-beat supercycle | 1260 |
| 14 | L_omega | Omega Lock | Total lock | all |

### Live-Lock Laws
- Smaller locks nest inside larger ones (L_face4 nests in L_crown420)
- L_crown420 period = lcm(3, 4, 5, 7) = 420
- L_super1260 period = lcm(420, 36) = 1260
- L_omega contains all prior locks simultaneously
- Conservation: over any L_crown420 period, face drift mod 4 = 0, phase drift mod 3 = 0

---

## Zero-Lock Interaction

The zero and lock families are dual:
- **Zeros** are where cycles **collapse** (singularities)
- **Locks** are where cycles **crystallize** (stable orbits)

### Conservation Law
$$d_Z(x) + d_L(x) = \text{const} \quad \text{over any closed 420-beat cycle}$$

A node near a zero-point (low d_Z) has few active locks (low d_L is high).
A node deep in a lock cycle (high d_L) is far from zero (high d_Z).

### Interaction Matrix
| | Near Zero | Far from Zero |
|-|-----------|---------------|
| **Few Locks** | Prima materia — undifferentiated potential | Transient — between states |
| **Many Locks** | Impossible (conservation violation) | Crystallized — fully differentiated |

---

## Omega Seed Canonical Compression

The Omega seed preserves all depth, zero, and lock information:

$$\Omega = \text{QSHRINK}_{tot}(S_4^{A+/Z-})$$

The QSHRINK_tot operator:
1. Preserves the complete depth tensor for every node
2. Preserves all 13 zero-point families
3. Preserves all 14 live-lock families
4. Preserves the transform ledger (all 15 operators with their witnesses)
5. Makes all information latent but recoverable via the restore pointer

**Key property:** From Omega, any prior stage can be fully restored, including its exact depth tensor, zero-point assignments, and active lock cycles.

---

## Siteswap / Throw Mapping Summary

### Universal Throw Coordinate
$$\mu = (x, \kappa, \Delta\kappa, d, \eta)$$

| Component | Meaning |
|-----------|---------|
| x | Source node |
| kappa | Departure beat |
| Delta_kappa | Throw height (how many beats until landing) |
| d | 6-component displacement vector |
| eta | Landing absorption law |

### 6-Component Displacement Vector
$$d = (\Delta_{shell}, \Delta_{wreath}, \Delta_{arch}, \Delta_{scale}, \Delta_{face}, \Delta_{portal})$$

### 9-Component Displacement Basis (Extended)
$$d_9 = (\Delta_{shell}, \Delta_{wreath}, \Delta_{arch}, \Delta_{scale}, \Delta_{face}, \Delta_{portal}, \Delta_{petal}, \Delta_{parity}, \Delta_{weave})$$

### 15 Preferred Harmonic Throw Heights
| Height | Period Divisor | Meaning |
|--------|---------------|---------|
| 1 | trivial | Adjacent step |
| 2 | 2 | Parity flip |
| 3 | 3 | Triadic skip (Su->Me->Sa) |
| 4 | 4 | Face rotation |
| 5 | 5 | Bridge-node gear shift |
| 6 | 6 = 2x3 | Parity + triadic |
| 7 | 7 | Planetary spoke |
| 10 | 10 = 2x5 | Parity + bridge |
| 12 | 12 = 3x4 | Mobius petal cycle |
| 14 | 14 = 2x7 | Parity + planetary |
| 15 | 15 = 3x5 | Triadic + bridge |
| 20 | 20 = 4x5 | Face + bridge |
| 21 | 21 = 3x7 | Triadic + planetary |
| 28 | 28 = 4x7 | Face + planetary |
| 35 | 35 = 5x7 | Bridge + planetary |

All heights divide 420. The 420-beat master clock ensures every throw lands on a valid beat.
