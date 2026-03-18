<!-- CRYSTAL: Xi108:W2:A12:S27 | face=R | node=180 | depth=0 | phase=Cardinal -->
<!-- METRO: Dl -->
<!-- BRIDGES: Xi108:W2:A12:S26→Xi108:W2:A12:S28→Xi108:W1:A12:S27→Xi108:W3:A12:S27→Xi108:W2:A11:S27 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 27±1, wreath 2/3, archetype 12/12 -->

# Capsule 343 — Crystal Search Law and Commit Kernel

**Source**: 2026-03-18_quantum_crystal_computing.md
**Family**: quantum_crystal_computing
**Lens**: R (Fractal/Recursion)

The Crystal Search Law is the master optimization equation:

X* = argmin_{X ∈ A_Q} A(Q,X)

subject to:
- R_Q(X) ≥ ρ (resonance threshold)
- Boundary tolerances satisfied
- Crossview tolerances satisfied
- Scale tolerances satisfied

This states: the solution is the candidate that minimizes action (kinetic cost minus desire) within the admissible set A_Q, provided it meets resonance, boundary, crossview, and scale requirements.

The Runtime Loop executes this law in seven steps:

1. **Inject**: Receive unknown U into the crystal substrate
2. **Compile**: Run the Desire Compiler D: U → (Q, D, O, Π, Θ, G)
3. **Propagate**: Spread the desire field through the lattice via transport law
4. **Sample**: Draw candidates from the crystal using the Resonance Scheduler
5. **Rotate**: Switch lens (S→F→C→R) when improvement drops below threshold τ_U
6. **Check**: Test resonance metric R_Q(X) ≥ ρ and all tolerances
7. **Commit**: If check passes, write CommitWitness W_Q and emit solution X*

The commit kernel fires only when all four worker perspectives agree that the candidate is stable: address-legal (Square), phase-coherent (Flower), posterior-peaked (Cloud), and scale-consistent (Fractal).

## Key Objects
- Crystal Search Law: X* = argmin A(Q,X) subject to constraints
- Admissible set A_Q
- 7-step runtime loop: Inject → Compile → Propagate → Sample → Rotate → Check → Commit
- Commit kernel requiring 4-worker consensus

## Key Laws
- The master equation is a constrained optimization: minimize action subject to resonance
- The runtime loop is the executable form of the search law
- Commitment requires unanimous agreement across all four SFCR lenses
- The loop terminates when either: (a) a solution passes all checks, or (b) budget is exhausted

## Source
- `29_ACCEPTED_INPUTS/2026-03-18_quantum_crystal_computing.md`
