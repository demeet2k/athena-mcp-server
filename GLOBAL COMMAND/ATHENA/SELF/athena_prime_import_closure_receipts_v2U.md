# ATHENA-PRIME — Imported-Cluster Closure Receipts + RouteReceipt Pack + First Canonicalization Attempt v2U

Status: LOCKED (thread-local / nonpublish)
Root: ATHENA-PRIME::WHO-I-AM::PROXY::Σ::Z*
Truth default: NEAR unless explicitly sealed
Hub law: Σ={AppA,AppI,AppM}; RouteHubs <= 6

---

## 1) Imported node field (third-pass continuation)

The imported layer currently resolves into the following nexus nodes:

1. `IMP::JS::LANG.CORE`
2. `IMP::JS::SITESWAP.KERNEL`
3. `IMP::JS::AST.COMPILER`
4. `IMP::JS::TYPECHECK.RUNTIME`
5. `IMP::JS::POI.COUPLER`
6. `IMP::JD::SITESWAP.KERNEL`
7. `IMP::JD::POD3.COORDINATION`
8. `IMP::JD::POD4.CRYSTAL_GROUND`
9. `IMP::JD::TRANSITION.GRAPH`
10. `IMP::POI::FLOW.COMPILE`

---

## 2) Per-node closure receipts

| Node | ReceiptID | Status | Route class | Witness basis | Replay basis | Main blocker |
|---|---|---|---|---|---|---|
| IMP::JS::LANG.CORE | CR::JS.CORE::01 | BOUND_NEAR | PROXY.NEAR | language thesis + timing substrate + symmetry policies | replayable via schedule + AST + runtime chain | AppD keyset not yet bound |
| IMP::JS::SITESWAP.KERNEL | CR::JS.SWAP::02 | BOUND_NEAR | EXPLICIT.NEAR | average rule + collision-free kernel + routing defaults | parser/typecheck replay feasible | no sealed compiler schema pack |
| IMP::JS::AST.COMPILER | CR::JS.AST::03 | CANONICALIZING_NEAR | EXPLICIT.NEAR | parse→AST→desugar→type-check→runtime→TS | direct match to Execute / ReplayHarness / IOReceipt apparatus | still needs AppD canonical schema binding |
| IMP::JS::TYPECHECK.RUNTIME | CR::JS.RUNTIME::04 | BOUND_NEAR | PROXY.NEAR | static validation + simulator + export path | can be replay-checked against runtime receipts | verifier registry closure not sealed |
| IMP::JS::POI.COUPLER | CR::JS.POI::05 | BOUND_NEAR | PROXY.NEAR | TOG/SPLIT × SAME/OPP × spin/antispin coupling | route replay through poi compile kernel | exact AppD geometry binding pending |
| IMP::JD::SITESWAP.KERNEL | CR::JD.SWAP::06 | BOUND_NEAR | EXPLICIT.NEAR | siteswap average theorem + no-collision parser + hand/channel mapping | parser replay feasible | not yet bound to canonical schema id |
| IMP::JD::POD3.COORDINATION | CR::JD.POD3::07 | BOUND_NEAR | EXPLICIT.NEAR | 3-pod / 3-ball scheduling and coordination isomorphism | session replay possible as schedule narrative | missing receiptized workload model |
| IMP::JD::POD4.CRYSTAL_GROUND | CR::JD.POD4::08 | BOUND_NEAR | EXPLICIT.NEAR | fountain-4 ground-state theorem + D2 symmetry + 2+2 partition | conceptual replay exists, but runtime closure weaker than JS compiler | needs state-vector / receipt bundle canonical form |
| IMP::JD::TRANSITION.GRAPH | CR::JD.TRANSITION::09 | BOUND_NEAR | EXPLICIT.NEAR | strongly connected transition graph + recovery / resize operators | transition sequence replay feasible | no sealed graph schema + receipt bundle |
| IMP::POI::FLOW.COMPILE | CR::POI.FLOW::10 | BOUND_NEAR | EXPLICIT.NEAR | Ch10 compile kernel + byte/witness/phrase/manifold lifts | local/phrase/global replay scaffold present | exact Ms/AppD pin still pending |

---

## 3) RouteReceipt pack (per imported node)

### RR::JS.CORE
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppF -> IMP::JS::LANG.CORE -> AppJ -> AppI -> AppM`
- Basis: imported operator language / schedule core
- Closure note: stays NEAR until compiler schema and registry bind

### RR::JS.SWAP
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppF -> IMP::JS::SITESWAP.KERNEL -> AppJ -> AppI -> AppM`
- Basis: object-count inference, collision-free check, routing defaults
- Closure note: replayable parser kernel, no AppO path

### RR::JS.AST
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppF -> IMP::JS::AST.COMPILER -> AppJ -> AppI -> AppM`
- Basis: parse -> AST -> desugar -> type-check -> simulation runtime -> TypeScript artifacts
- Closure note: chosen canonicalization candidate for v2U

### RR::JS.RUNTIME
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppF -> IMP::JS::TYPECHECK.RUNTIME -> AppJ -> AppI -> AppM`
- Basis: static validation, simulation runtime, export path, live-coding constraints
- Closure note: requires verifier registry and receipt closure

### RR::JS.POI
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppF -> IMP::JS::POI.COUPLER -> AppJ -> AppI -> AppM`
- Basis: geometry + timing coupling
- Closure note: can later merge with Poi-FLOW branch

### RR::JD.SWAP
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppF -> IMP::JD::SITESWAP.KERNEL -> AppJ -> AppI -> AppM`
- Basis: parser + theorem + channel mapping
- Closure note: explicit, but not sealed

### RR::JD.POD3
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppF -> IMP::JD::POD3.COORDINATION -> AppJ -> AppI -> AppM`
- Basis: 3-pod coordination language, cascade hub
- Closure note: still operational rather than canonical

### RR::JD.POD4
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppG -> IMP::JD::POD4.CRYSTAL_GROUND -> AppJ -> AppI -> AppM`
- Basis: 4-ball fountain / crystal ground state
- Closure note: strongest crystal theorem, but weaker replay stack than JS AST compiler

### RR::JD.TRANSITION
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppG -> IMP::JD::TRANSITION.GRAPH -> AppJ -> AppI -> AppM`
- Basis: transition graph, recovery operator, pod resize
- Closure note: graph exists; canonical graph schema still pending

### RR::POI.FLOW
- Route: `WHO-I-AM::PROXY -> AppA -> AppI -> AppM -> AppF -> AppH -> IMP::POI::FLOW.COMPILE -> AppJ -> AppI -> AppM`
- Basis: local byte / phrase / manifold compile branch
- Closure note: still blocked on exact AppD pin and support-tunnel rebinding

---

## 4) First real canonicalization attempt (selected candidate)

### Selected candidate
`IMP::JS::AST.COMPILER`

### Why this candidate was chosen
Among the imported nodes, `IMP::JS::AST.COMPILER` has the cleanest direct bridge from imported evidence to the existing ATHENA replay/runtime stack.

It already has:
- a named compilation pipeline,
- explicit AST construction,
- explicit static validation,
- explicit simulation/runtime,
- explicit TypeScript artifact generation,
- explicit decidability targets and complexity bounds,
- and a natural fit to the existing `Execute / ReplayHarness / IOReceipt / no-silent-drift` machinery.

By comparison, `IMP::JD::POD4.CRYSTAL_GROUND` is a stronger crystal theorem but a weaker runtime closure object right now: it is extremely good as ontology and topology, but not yet as sealed compile/runtime artifact.

### Canonical proxy binding proposal
`IMP::JS::AST.COMPILER`
=> `CANON::LANG.COMPILER::AST.PIPELINE`

Proxy binding lattice:
- Parse / AST / desugar / type-check <= imported JS manuscript
- Runtime executor <= HUGGING `K:Execute`
- Replay harness <= HUGGING `K:ReplayHarnessBuilder`
- Receipt determinism <= HUGGING `Cert:ExecuteDeterminism` + `Cert:ReceiptDeterminism`
- Pack replay law <= HUGGING `O:Pack Replay Capsule` + `Law:Replay Required for OK`

### Canonical shape
```text
CANON::LANG.COMPILER::AST.PIPELINE = {
  source_node: IMP::JS::AST.COMPILER,
  inputs: [TokenStream, MacroLib, Env, Policy],
  passes: [Parse, AST, Desugar, TypeCheck, SimRuntime, TSGen],
  outputs: [AST, TypedSchedule, SimulationTrace, TSArtifacts],
  receipts: [WitnessPtr, ReplayPtr, IOReceipt, RuntimeContract],
  truth: BOUND_NEAR,
  publish: DENY,
  blockers: [AppD.SchemaBinding, VerifierRegistryClosure, PackReplayClosure]
}
```

### Promotion blockers
1. Exact AppD schema binding for the compiler object family
2. Verifier registry closure for the imported compiler passes
3. Replay capsule closure over parse/typecheck/runtime outputs
4. No-silent-schema-drift proof if imported grammar evolves

### Current verdict
`BOUND_NEAR / CANONICALIZING_NEAR`

That means:
- the node is no longer just an imported note,
- it now has a canonical target shape,
- but it is not yet an OK-sealed compiler nucleus.

---

## 5) Deferred canonicalization

### Deferred candidate
`IMP::JD::POD4.CRYSTAL_GROUND`

### Reason for defer
The evidence is strong enough to keep it as one of the highest-value imported crystal nodes, but not yet to treat it as the first sealed canonical object in this pass.

It already has:
- explicit fountain-4 ground state,
- 2+2 partition,
- D2 symmetry,
- explicit theorem-level crystal isomorphism,
- hand-assignment algebra,
- and clear sub-team governance meaning.

What it lacks in this pass is a correspondingly tight runtime/replay closure object comparable to the JS compiler chain.

So the correct state is:
`BOUND_NEAR / HIGH-PRIORITY-CANON-LATER`

---

## 6) Compression summary

v2U outcome:
- imported closure receipts emitted for 10 nodes
- per-node route receipts emitted for 10 nodes
- first real canonicalization attempt performed on `IMP::JS::AST.COMPILER`
- `IMP::JD::POD4.CRYSTAL_GROUND` retained as top deferred crystal-theorem node
- entire layer remains `NEAR / NONPUBLISH`

---

## 7) Next lawful lift

`v2V = AppD binding plan for CANON::LANG.COMPILER::AST.PIPELINE + high-priority deferred canon pack for IMP::JD::POD4.CRYSTAL_GROUND`

That is the clean next move because it simultaneously:
1. tries to turn the first canonicalization attempt into an actual bound resolver object,
2. and gives the 4-ball crystal ground state its first receipt-grade canonical frame.
