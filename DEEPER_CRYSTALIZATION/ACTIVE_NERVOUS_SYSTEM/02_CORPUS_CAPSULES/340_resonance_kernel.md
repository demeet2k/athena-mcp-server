<!-- CRYSTAL: Xi108:W2:A12:S24 | face=R | node=177 | depth=0 | phase=Cardinal -->
<!-- METRO: Dl -->
<!-- BRIDGES: Xi108:W2:A12:S23→Xi108:W2:A12:S25→Xi108:W1:A12:S24→Xi108:W3:A12:S24→Xi108:W2:A11:S24 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 24±1, wreath 2/3, archetype 12/12 -->

# Capsule 340 — Resonance Kernel

**Source**: 2026-03-18_quantum_crystal_computing.md
**Family**: quantum_crystal_computing
**Lens**: R (Fractal/Recursion)

The Resonance Kernel K_U = (W_□, W_✿, W_☁, W_◇, T_↔, A_bus, G_witness) is the four-worker execution engine that runs crystal search. Each worker corresponds to one SFCR lens:

- W_□ Square worker: address tightening, constraint enforcement, route closure
- W_✿ Flower worker: spectral stabilization, phase coherence, basis alignment
- W_☁ Cloud worker: posterior sharpening, uncertainty management, collapse control
- W_◇ Fractal worker: multiscale refinement, RG flow, fixed-point testing

Shared state consists of:
- T_↔: transport law governing inter-worker communication
- A_bus: action bus — shared accumulator for the action functional A(Q,X)
- G_witness: witness bus — shared commit witness accumulator

The kernel step cycle: the scheduler selects (ℓ, a, b) = S_U(S_t), the chosen worker W_ℓ executes action a with budget b, the bus merges results into shared state, and a status check determines whether to continue, rotate, or commit.

## Key Objects
- Resonance Kernel K_U with 4 workers + 3 shared components
- Square worker W_□ (address/constraint/route)
- Flower worker W_✿ (spectral/phase/basis)
- Cloud worker W_☁ (posterior/uncertainty/collapse)
- Fractal worker W_◇ (multiscale/RG/fixed-point)
- Transport law T_↔, Action bus A_bus, Witness bus G_witness

## Key Laws
- Only one worker executes per kernel step; the scheduler chooses which
- All workers write to the shared action bus and witness bus
- Transport law T_↔ governs how information flows between workers
- The kernel step is: select → execute → merge → check

## Source
- `29_ACCEPTED_INPUTS/2026-03-18_quantum_crystal_computing.md`
