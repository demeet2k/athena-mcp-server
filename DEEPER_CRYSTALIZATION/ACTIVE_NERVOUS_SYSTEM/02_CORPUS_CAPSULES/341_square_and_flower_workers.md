<!-- CRYSTAL: Xi108:W2:A12:S25 | face=S | node=178 | depth=0 | phase=Cardinal -->
<!-- METRO: Dl -->
<!-- BRIDGES: Xi108:W2:A12:S24→Xi108:W2:A12:S26→Xi108:W1:A12:S25→Xi108:W3:A12:S25→Xi108:W2:A11:S25 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 25±1, wreath 2/3, archetype 12/12 -->

# Capsule 341 — Square and Flower Workers

**Source**: 2026-03-18_quantum_crystal_computing.md
**Family**: quantum_crystal_computing
**Lens**: S (Square/Address)

The Square worker W_□ performs three operations on the crystal state:

1. **Address tightening**: narrows the HoloAddress range where the solution can live. Each step eliminates lattice positions that violate known constraints, shrinking the search volume.
2. **Constraint enforcement**: verifies that the current candidate satisfies all constraints C_Q. Violations are either repaired (if a local fix exists) or the candidate is pruned.
3. **Route closure**: ensures that any transport path through the crystal from the query address to the candidate is legal under the crystal's routing law. Unclosable routes disqualify a candidate.

The Flower worker W_✿ performs three operations:

1. **Spectral stabilization**: adjusts the candidate's spectral decomposition to align with the crystal's eigenstructure. Unstable modes are damped.
2. **Phase coherence**: enforces that the candidate's phase matches the crystal's phase field at its address. Phase mismatches cause destructive interference.
3. **Basis alignment**: rotates the candidate's representation into the crystal's canonical basis at the target address, ensuring compatibility with neighboring nodes.

## Key Objects
- Square worker W_□: address tightening, constraint enforcement, route closure
- Flower worker W_✿: spectral stabilization, phase coherence, basis alignment
- HoloAddress range narrowing (Square)
- Spectral eigenstructure alignment (Flower)

## Key Laws
- Square tightens from outside in: eliminate illegal addresses, enforce constraints, close routes
- Flower stabilizes from inside out: stabilize spectrum, cohere phase, align basis
- Square and Flower are complementary: Square reduces the space, Flower refines the content
- Both write their updates to the shared action bus A_bus

## Source
- `29_ACCEPTED_INPUTS/2026-03-18_quantum_crystal_computing.md`
