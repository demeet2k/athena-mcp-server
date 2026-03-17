# ATHENA-PRIME — First Mine Bind Receipt v2P

## Result

**Selected mine:** `Poi.MsDerivation`

**Disposition:** `BOUND_NEAR`

This is the first mine in the queue that can be bound **honestly** with the currently uploaded evidence.
It is **not OK-closed**.
It is a lawful **NEAR binding receipt** with an explicit target candidate, route candidate, tunnel plan,
preserved invariants, and remaining obligations.

## Why this mine was chosen

`Poi.MsDerivation` has a concrete surfaced target and route plan in the uploaded poi kernel:

- `Target = Ms⟨0420⟩::Ch10⟨0021⟩.R3.a`
- `Working meaning = local poi flower byte-lattice lifts to a 256-slot crystal word`
- `HubsSeq = AppA -> AppF -> AppH -> AppJ -> AppI -> AppM`
- `TunnelPlan = Z_poi.local -> Z* -> Z_poi.phrase`
- `Truth = NEAR`

By contrast, `LOVE.MultiplicativeGuard` is still only surfaced as a resolver edge:

- `Resolve(AppD,"LOVE.MultiplicativeGuard")`
- `Truth = AMBIG until AppD binding witness`

So LOVE can be pressure-ranked, but it cannot yet be truthfully bound to a concrete GlobalAddr in this shell.

## Receipt

```text
MineBindReceipt_v2P := {
  id: "ATHENA-PRIME::v2P::Poi.MsDerivation",
  root: "ATHENA-PRIME::GPT-5.4-THINKING::THREAD-LOCAL",
  mine: "Poi.MsDerivation",
  truth: "NEAR",
  selected_for: "first-real-bind",
  target_candidate: "Ms⟨0420⟩::Ch10⟨0021⟩.R3.a",
  route_candidate: ["AppA","AppF","AppH","AppJ","AppI","AppM"],
  tunnel: ["Z_poi.local","Z*","Z_poi.phrase"],
  preserved_invariants: ["m:n","ρ","K","d","Δφ","δ","Π"],
  crystal_payload: ["B=q0+4q1+16q2+64q3","Ξ=(B,I)"]
}
```

## Route legality check

The candidate hub set is lawful under the uploaded router grammar.
For a `Ch10⟨0021⟩` chapter target on `○Arc 3`, the corpus pins:

- `ArcHub(3) = AppF`
- `FacetBase(3) = AppH`
- `NEAR -> AppJ`
- `Σ = {AppA, AppI, AppM}`
- `Hub budget H <= 6`

So the poi kernel’s surfaced hub set

`AppA -> AppF -> AppH -> AppJ -> AppI -> AppM`

matches the required nexus family and stays within the hard hub cap.
Order here is retained from the poi kernel’s own HubsSeq; legality comes from the shared hub set and budget discipline.

## Present witnesses already surfaced

The currently uploaded poi file already supplies enough to bind a real candidate object rather than a vague placeholder:

1. **Compile kernel identity**
   - poi flower is treated as a compiled, beat-addressable geometric program
   - `FlowerAddr = (K, IN/ANTI, m:n, h,p,d, TOG/SPLIT, SAME/OPP, plane)`

2. **Local crystal byte / invariant split**
   - local byte `B = q0 + 4q1 + 16q2 + 64q3`
   - local compiled object `Ξ = (B, I)`

3. **Constraint engine**
   - 16-crystal pruning engine for closure, polarity, petals, beat lock, hand phase, direction, plane, admissibility, transition legality, and compression

4. **Manifold lift**
   - explicit claim that a local byte-lattice lifts to a `256-slot crystal word`

These are enough for a real **candidate bind**, but not enough for **OK closure**.

## Missing obligations (blocking OK)

The uploaded poi kernel explicitly lists the remaining obligations:

1. **Pin exact Ms derivation in AppD**
   - the target manuscript id `Ms⟨0420⟩` is not yet bound through AppD.

2. **Rebind auxiliary filler and annotation nodes**
   - the poi file says earlier supporting corpus files expired on that side, so auxiliary filler/annotation node closure is incomplete.

3. **Attach replay witnesses for each lift**
   - one replay witness for each of:
     - local byte
     - phrase word
     - global manifold

4. **Keep HCRL rotation complete**
   - `S -> F -> C -> R`

Until those obligations are satisfied, this mine remains `BOUND_NEAR`, not `OK`.

## Promotion gate

Promotion is blocked by corpus law:

- `NEAR` must carry residual ledger + upgrade plan
- `OK` requires witness + replay closure
- `AppO` publish gate is legal only on `OK`

Therefore this receipt routes through **AppJ**, not AppO.

## Residual ledger for this mine

```text
ResidualLedger_v2P(Poi.MsDerivation) := {
  truth: NEAR,
  missing_witness: [
    "AppD exact Ms derivation for Ms⟨0420⟩",
    "Replay witness: local byte",
    "Replay witness: phrase word",
    "Replay witness: global manifold"
  ],
  missing_evidence: [
    "auxiliary filler-node rebinding",
    "annotation-node rebinding"
  ],
  missing_rotation: ["C-pass completion","R-pass completion if not already sealed"],
  responsible_builders: ["AppD","AppH","AppJ","AppM"],
  route_after_success: ["AppJ","AppM","AppD","AppM"],
  publish: "DENY"
}
```

## Comparison mine: LOVE.MultiplicativeGuard

LOVE is not closable yet with the current upload set.
It remains a resolver edge with no concrete bound target:

```text
Resolve(AppD,"LOVE.MultiplicativeGuard")
Truth = AMBIG until AppD binding witness
```

Its surfaced obligations are real, but they are still obligations, not closure:

- `WB:ConsentReceiptDigest`
- `WB:LoveSpecDigest`
- `RC:LoveGateReplaySuite`
- `Cert:LOVEReceipt`
- `Cert:LOVEReplay`
- AppD binding closure for `LOVE.MultiplicativeGuard`

So LOVE stays in the queue, but it does **not** outrank Poi for first actual bind.

## Next lawful move after v2P

The next real step is not another atlas. It is one of these:

1. **v2Q.a — AppD candidate binder for `Ms⟨0420⟩`**
   - emit the exact AppD candidate-set + evidence plan for the poi target manuscript id.

2. **v2Q.b — Poi replay witness pack**
   - define and seal the three replay witnesses:
     - local byte replay
     - phrase word replay
     - manifold replay

3. **v2Q.c — auxiliary filler / annotation rebinding map**
   - restore the missing side nodes the poi kernel itself says are still incomplete.

Until one of those happens, this mine remains the first **real** bind, but not the first **OK closure**.
