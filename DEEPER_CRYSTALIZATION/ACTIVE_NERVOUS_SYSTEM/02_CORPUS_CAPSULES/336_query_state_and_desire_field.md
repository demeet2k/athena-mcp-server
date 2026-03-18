<!-- CRYSTAL: Xi108:W2:A12:S20 | face=S | node=173 | depth=0 | phase=Cardinal -->
<!-- METRO: Dl -->
<!-- BRIDGES: Xi108:W2:A12:S19→Xi108:W2:A12:S21→Xi108:W1:A12:S20→Xi108:W3:A12:S20→Xi108:W2:A11:S20 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 20±1, wreath 2/3, archetype 12/12 -->

# Capsule 336 — QueryState and DesireField

**Source**: 2026-03-18_quantum_crystal_computing.md
**Family**: quantum_crystal_computing
**Lens**: S (Square/Address)

Quantum Fractal Crystal Computing treats the unknown as a lawful state and pulls solutions from the void by tightening invariants until a unique completion remains. The two foundational formal objects are QueryState Q and DesireField D_Q.

QueryState Q = (h_Q, O_Q, C_Q, R_Q, k_Q, Θ_Q) encodes the full specification of a crystal query: the HoloAddress seed h_Q locates the query in the lattice, O_Q names the object sought, C_Q lists the constraints, R_Q the required rotations, k_Q the depth schedule, and Θ_Q the commit tolerances.

DesireField D_Q(X) = I(Q,X) = λ_a·Align(Q,X) + λ_e·Expl(X) + λ_z·ZPA(Q,X) + λ_c·ConSat(Q,X) is a weighted sum of alignment, exploration, zero-point attractor pull, and constraint satisfaction. The action law A(Q,X) = K(X) - D_Q(X) gives the net action: kinetic cost minus desire. Computation minimizes this action.

## Key Objects
- QueryState Q with 6 components (h_Q, O_Q, C_Q, R_Q, k_Q, Θ_Q)
- DesireField D_Q(X) with 4 weighted terms (Align, Expl, ZPA, ConSat)
- Action law A(Q,X) = K(X) - D_Q(X)
- Kinetic cost K(X) — computational effort to reach candidate X

## Key Laws
- The unknown is a lawful state, not an error condition
- Computation = minimizing action A(Q,X) = K - D over the crystal lattice
- Desire is a field, not a scalar — it varies across the crystal substrate
- The crystal stores generators and constraint-outlines, not bulk expansions

## Source
- `29_ACCEPTED_INPUTS/2026-03-18_quantum_crystal_computing.md`
