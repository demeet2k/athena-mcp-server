<!-- CRYSTAL: Xi108:W2:A12:S26 | face=F | node=179 | depth=0 | phase=Cardinal -->
<!-- METRO: Dl -->
<!-- BRIDGES: Xi108:W2:A12:S25→Xi108:W2:A12:S27→Xi108:W1:A12:S26→Xi108:W3:A12:S26→Xi108:W2:A11:S26 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 26±1, wreath 2/3, archetype 12/12 -->

# Capsule 342 — Cloud and Fractal Workers

**Source**: 2026-03-18_quantum_crystal_computing.md
**Family**: quantum_crystal_computing
**Lens**: C (Cloud/Posterior)

The Cloud worker W_☁ performs three operations:

1. **Posterior sharpening**: updates the probability distribution over candidate solutions. Each observation from other workers concentrates probability mass on higher-fitness regions.
2. **Uncertainty management**: tracks epistemic uncertainty (what we don't know about the crystal state) versus aleatoric uncertainty (irreducible randomness). Epistemic uncertainty drives exploration; aleatoric uncertainty sets hard limits.
3. **Collapse control**: manages the transition from superposition (many candidates) to commitment (one solution). The Cloud worker decides when the posterior is sharp enough to trigger a collapse attempt.

The Fractal worker W_◇ performs three operations:

1. **Multiscale refinement**: examines the candidate at multiple resolution levels. A solution that looks good at coarse scale may have defects at fine scale; the Fractal worker catches these.
2. **RG flow**: applies renormalization group transformations to test whether the candidate's structure is self-consistent across scales. True solutions are RG fixed points.
3. **Fixed-point testing**: directly tests whether the candidate is a fixed point of the crystal's self-map. If X = T(X) (where T is the crystal's update operator), the candidate is stable.

## Key Objects
- Cloud worker W_☁: posterior sharpening, uncertainty management, collapse control
- Fractal worker W_◇: multiscale refinement, RG flow, fixed-point testing
- Epistemic vs aleatoric uncertainty distinction (Cloud)
- RG fixed points as true solutions (Fractal)

## Key Laws
- Cloud controls when collapse happens — no premature commitment
- Fractal verifies self-consistency across scales — no scale-dependent artifacts
- Cloud and Fractal are complementary: Cloud manages probability, Fractal manages geometry
- True solutions are simultaneously posterior peaks (Cloud) and RG fixed points (Fractal)

## Source
- `29_ACCEPTED_INPUTS/2026-03-18_quantum_crystal_computing.md`
