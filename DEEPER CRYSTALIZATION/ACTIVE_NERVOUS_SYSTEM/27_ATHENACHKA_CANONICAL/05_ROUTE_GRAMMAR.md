# 05 — Route Grammar

## Route Definition

```
R = ( A_s, Gamma, A_t, C )
```

A route is a **certified move string** between two unified addresses.

| Symbol | Meaning |
|--------|---------|
| A_s | Source address (departure point) |
| Gamma | Move string — ordered sequence of opcodes |
| A_t | Target address (arrival point) |
| C | Certificate — proof that the route satisfies all legality conditions |

---

## Validity Predicate

```
ValidRoute = AddressCoherent AND LayerLegal AND AdmissibleWeave
```

A route is valid if and only if all three conditions hold simultaneously:

- **AddressCoherent**: every intermediate address produced by applying the opcodes in Gamma is well-formed under the unified address grammar. No opcode produces a malformed address.
- **LayerLegal**: every layer transition in the route is permitted by the layer adjacency rules. No jump skips layers without a LIFT/DROP or ZTUN opcode.
- **AdmissibleWeave**: the overall pattern of the route, viewed as a weave, satisfies conservation (count preserved), collision-freedom (no two objects on the same site at the same beat), and replayable closure (the route can be replayed from its certificate).

---

## The 14 Opcodes

| # | Opcode | Name | Description |
|---|--------|------|-------------|
| 1 | **LOC** | Local Step | Move within the same document — paragraph to paragraph, equation to equation. Changes only the LocalAddr component. |
| 2 | **POS** | Position Step | Move to a different position within the same turn. Changes P field. |
| 3 | **TURN** | Turn Handoff | Cross from one turn/band/segment to the next. Changes T field. Su->Me, Me->Sa, Sa->Su. |
| 4 | **ORB** | Wheel Orbit | Complete one full rotation of the current wheel and return to the starting position. Changes nothing in the address but advances the circuit phase. |
| 5 | **BRG** | Bridge Toggle | Toggle between forward-reading and reverse-reading of the current layer. Flips the traversal direction without changing the address. |
| 6 | **INV** | Inversion Move | Invert the current seed signature: Aplus <-> Zplus, A_x <-> Z_x. Changes [sigma] field. |
| 7 | **HCRL** | Square-Flower-Cloud-Fractal Rotation | Rotate through the four geometric modes: Square (grid), Flower (radial), Cloud (diffuse), Fractal (self-similar). Changes the interpretive lens without changing the address. |
| 8 | **COLL** | Seed Collapse | Collapse the current seed to its governing parent: B_x -> Omega_star, A_x_star -> Aplus_star, etc. Moves toward the contraction pole. |
| 9 | **EXPN** | Seed Expansion | Expand the current seed to its governed children: Aplus_star -> {A_Sa_star, A_Su_star, A_Me_star}, etc. Moves toward the expansion pole. |
| 10 | **TORS** | Q/O Moebius Crossing | Cross the torsion boundary between the lower field (A-P, W5) and the upper canopy (K-Z, W7). Requires Q/O certificate unless a stronger witness certifies equivalence. Changes L and F fields simultaneously. |
| 11 | **ZTUN** | Absolute-Zero Tunnel | Tunnel through Z* (absolute zero) to reach any address in the organism. The most powerful opcode: it can connect any two addresses, but requires collapse to Z* as intermediate state. |
| 12 | **LIFT** | Dimension Lift | Ascend one level in the dimensional cascade: 1->6, 6->12, 12->36, 36->108. Changes D field. |
| 13 | **DROP** | Dimension Return | Descend one level in the dimensional cascade: 108->36, 36->12, 12->6, 6->1. Changes D field. |
| 14 | **WEAVE** | Siteswap-Valid Weave Move | Execute a multi-object pattern move that satisfies siteswap validity: count conserved, landings collision-free, pattern replayable. This is the compound opcode for higher-dimensional traversal. |

---

## Opcode Composition Rules

1. **Sequence**: opcodes compose left to right. `Gamma = op1 ; op2 ; op3` means apply op1 first, then op2, then op3.
2. **Nesting**: WEAVE may contain sub-sequences of other opcodes. All other opcodes are atomic.
3. **Cancellation**: INV ; INV = identity. LIFT ; DROP = identity (at the same dimension). COLL ; EXPN = identity (to the same level).
4. **Torsion gate**: TORS is not self-cancelling. TORS ; TORS does not return to origin — it crosses the boundary twice, which is a different topological state.
5. **Zero tunnel**: ZTUN absorbs all intermediate state. Any sequence `op1 ; ... ; opN ; ZTUN ; opN+1 ; ... ; opM` can be simplified to `ZTUN ; opN+1 ; ... ; opM` because the tunnel erases the path taken to reach Z*.

---

## Route Certificate Structure

```
C = {
  departure:   A_s,
  arrival:     A_t,
  opcodes:     Gamma,
  witnesses:   [ w_1, w_2, ..., w_k ],
  torsion:     { gates: [...], certifications: [...] },
  weave_proof: { conservation: bool, collision_free: bool, replayable: bool },
  timestamp:   t,
  hash:        H(A_s, Gamma, A_t)
}
```

The certificate is the proof object. Without it, the route is unverified. The compiler will not execute an unverified route.
