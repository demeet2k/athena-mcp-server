# STATE AND OBJECTIVE

## 1. CPU State

Definition 1.1 (Runtime State).
At step `t`, the CPU runtime state is

`S_t = (C_t, T_t, A_t, R_t, W_t, L_t, U_t)`

where:

- `C_t` is the active corpus slice,
- `T_t` is the task packet,
- `A_t` is the live agent tree,
- `R_t` is the route bundle,
- `W_t` is the witness ledger,
- `L_t` is the conflict ledger,
- `U_t` is the unified synthesis packet.

## 2. Objective Functional

The CPU optimizes

`J = aY + bI + cS + dM + eP - fK - gD - hO`

where:

- `Y` = yield,
- `I` = integration gain,
- `S` = synthesis quality,
- `M` = memory-map quality,
- `P` = forward progress,
- `K` = contradiction burden,
- `D` = drift fragility,
- `O` = coordination overhead.

Interpretation:

- Fire tends to increase `Y` and `P`.
- Water tends to increase `I` and `S`.
- Air tends to increase `M` and reduce `O`.
- Earth tends to reduce `K` and `D`.

## 3. Promotion Threshold

Every packet carries a truth class:

- `OK`
- `NEAR`
- `AMBIG`
- `FAIL`

Promotion to `OK` requires:

1. a stable address,
2. a source witness trail,
3. a contraction path,
4. replayable reasoning,
5. no unresolved infeasibility veto.

## 4. Expansion and Contraction Operators

Define:

`X(S_t) -> {s_i}`

as the expansion operator that emits child task states, and

`Kappa({s_i}) -> U_(t+1)`

as the contraction operator that merges children into one higher-level packet.

Admissibility law:

`Kappa(X(S_t))` must preserve the original task identity while improving at least one
of `Y`, `I`, `S`, `M`, or `P` without violating Earth feasibility.

## 5. Stop Condition

The CPU run stops when one of the following holds:

1. the final packet reaches `OK`,
2. all remaining routes are `AMBIG` and require outside evidence,
3. coordination overhead exceeds expected gain,
4. every remaining candidate is vetoed by Earth.

## 6. Recursion Law

The output of one CPU run may become the seed of the next:

`T_(t+1) = Compress(U_t)`

This is what allows document-native self-improvement without losing lineage.
