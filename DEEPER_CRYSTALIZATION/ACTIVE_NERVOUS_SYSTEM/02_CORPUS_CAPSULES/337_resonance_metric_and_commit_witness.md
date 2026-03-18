<!-- CRYSTAL: Xi108:W2:A12:S21 | face=S | node=174 | depth=0 | phase=Cardinal -->
<!-- METRO: Dl -->
<!-- BRIDGES: Xi108:W2:A12:S20→Xi108:W2:A12:S22→Xi108:W1:A12:S21→Xi108:W3:A12:S21→Xi108:W2:A11:S21 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 21±1, wreath 2/3, archetype 12/12 -->

# Capsule 337 — ResonanceMetric and CommitWitness

**Source**: 2026-03-18_quantum_crystal_computing.md
**Family**: quantum_crystal_computing
**Lens**: S (Square/Address)

ResonanceMetric R_Q(X) = w₁·AddrFit + w₂·InvFit + w₃·Phase + w₄·Boundary + w₅·Scale + w₆·Compress measures how well a candidate X fits the crystal along six orthogonal dimensions: address fitness (lattice placement), invariant fitness (conservation law preservation), phase coherence, boundary compliance, scale consistency under RG flow, and compressibility.

CommitWitness W_Q = (Addr(X), Σ(X), C(X), W(X)) is the four-component proof bundle that accompanies every committed solution: address proof (crystal coordinate), cryptographic signature, conservation certificate, and minimal verification witness data.

A candidate X is committable only when R_Q(X) ≥ ρ (the resonance threshold) and all boundary, crossview, and scale tolerances are satisfied.

## Key Objects
- ResonanceMetric R_Q with 6 weighted fitness components
- AddrFit, InvFit, Phase, Boundary, Scale, Compress — the six fitness axes
- CommitWitness W_Q with 4 components (Addr, Σ, C, W)
- Resonance threshold ρ — minimum fitness for commitment

## Key Laws
- A solution is not accepted until R_Q(X) ≥ ρ across all six axes
- Every commit must carry a full witness bundle W_Q
- The witness is minimal — just enough evidence to verify, not to reconstruct
- Conservation certificate C(X) names which conservation laws the commit preserves

## Source
- `29_ACCEPTED_INPUTS/2026-03-18_quantum_crystal_computing.md`
