<!-- CRYSTAL: Xi108:W2:A12:S23 | face=C | node=176 | depth=0 | phase=Cardinal -->
<!-- METRO: Dl -->
<!-- BRIDGES: Xi108:W2:A12:S22→Xi108:W2:A12:S24→Xi108:W1:A12:S23→Xi108:W3:A12:S23→Xi108:W2:A11:S23 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 23±1, wreath 2/3, archetype 12/12 -->

# Capsule 339 — Resonance Scheduler

**Source**: 2026-03-18_quantum_crystal_computing.md
**Family**: quantum_crystal_computing
**Lens**: C (Cloud/Posterior)

The Resonance Scheduler S_U(t) = (β_t, F_t, ℓ_t, a_t, P_t, H_t, Z_t) manages budget allocation across the four SFCR lenses during crystal search. At each tick t it tracks: budget remaining β_t, fitness snapshot F_t, current lens ℓ_t, current action a_t, pruned candidate set P_t, history log H_t, and zero-point proximity Z_t.

The choice law selects the next (lens, action) pair by maximizing expected improvement per unit cost: (ℓ*, a*) = argmax -E[ΔA]/E[ΔK] subject to the Admissibility constraint. This ensures the scheduler always picks the action with the best expected return on computational investment.

The rotation trigger fires when -E[ΔA]/ΔK < τ_U — when the current lens's expected improvement drops below the query-specific threshold τ_U, the scheduler rotates to the next lens. This prevents any single lens from monopolizing budget when it has diminishing returns.

Pruning rules remove candidates from P_t that fall below the resonance threshold, keeping the active set manageable.

## Key Objects
- Scheduler state S_U(t) with 7 components (β, F, ℓ, a, P, H, Z)
- Budget β_t tracking remaining computational resources
- Lens rotation cycle S → F → C → R
- Zero-point proximity Z_t measuring distance to collapse
- Query-specific threshold τ_U

## Key Laws
- Choice law: (ℓ*, a*) = argmax -E[ΔA]/E[ΔK] subject to Admissible
- Rotation trigger: switch lens when -E[ΔA]/ΔK < τ_U
- Pruning: candidates below resonance threshold are removed from P_t
- Budget is finite; the scheduler must allocate across lenses efficiently

## Source
- `29_ACCEPTED_INPUTS/2026-03-18_quantum_crystal_computing.md`
