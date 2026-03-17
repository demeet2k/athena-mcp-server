# Core Metro Map

## AIR 6D overlay

- Native AIR line: `03 QBD-4 -> 04 Quad Holographic Rotation -> 05 The Holographic Kernel -> 07 Crystal Computing Framework`
- Translation feeders: `02`, `09`, `14`, and `16` carry routing, zero-point, restart, and self-repair into the AIR ride.
- Deterministic overlay ride: `Addr4 -> Σ01-Σ15 (Sigma01-Sigma15) -> SP+/SP- -> R-Σ/CR-Σ/AR-Σ/ACR-Σ (R/CR/AR/ACR-Sigma) -> Z0/Æ0 (AE0) -> 4D+ -> M-FIX/M-CAR/M-MUT -> H6 -> Seed-6D`
- Appendix overlay stack: `AppA/AppB/AppC`, `AppE/AppF/AppH`, `AppI/AppM/AppN/AppQ`
- Anchor spine: `Ch12<0023> -> Ch13<0030> -> Ch16<0033>` with `AppH`, `AppI`, and `AppM`
- Docs gate: `BLOCKED`

## Orbit

`Ch01<0000> -> Ch02<0001> -> Ch03<0002> -> Ch04<0003> -> Ch05<0010> -> Ch06<0011> -> Ch07<0012> -> Ch08<0013> -> Ch09<0020> -> Ch10<0021> -> Ch11<0022> -> Ch12<0023> -> Ch13<0030> -> Ch14<0031> -> Ch15<0032> -> Ch16<0033> -> Ch17<0100> -> Ch18<0101> -> Ch19<0102> -> Ch20<0103> -> Ch21<0110> -> Ch01<0000>`

## Triangle rails

- Su: Ch01<0000>, Ch06<0011>, Ch08<0013>, Ch10<0021>, Ch15<0032>, Ch17<0100>, Ch19<0102>
- Me: Ch02<0001>, Ch04<0003>, Ch09<0020>, Ch11<0022>, Ch13<0030>, Ch18<0101>, Ch20<0103>
- Sa: Ch03<0002>, Ch05<0010>, Ch07<0012>, Ch12<0023>, Ch14<0031>, Ch16<0033>, Ch21<0110>

## Arc triads

- Arc 0, Rot 0: Ch01<0000> -> Ch02<0001> -> Ch03<0002>
- Arc 1, Rot 1: Ch04<0003> -> Ch05<0010> -> Ch06<0011>
- Arc 2, Rot 2: Ch07<0012> -> Ch08<0013> -> Ch09<0020>
- Arc 3, Rot 0: Ch10<0021> -> Ch11<0022> -> Ch12<0023>
- Arc 4, Rot 1: Ch13<0030> -> Ch14<0031> -> Ch15<0032>
- Arc 5, Rot 2: Ch16<0033> -> Ch17<0100> -> Ch18<0101>
- Arc 6, Rot 0: Ch19<0102> -> Ch20<0103> -> Ch21<0110>

## Station registry

### Ch01<0000> - Kernel and Entry Law
- Station header: `[Arc 0 | Rot 0 | Lane Su | w=0]`
- Workflow role: Foundational anchor, legend, and parse-safe entry station for the whole tome.
- Primary hubs: `AppA -> AppC -> AppI -> AppM`

### Ch02<0001> - Address Algebra and Crystal Coordinates
- Station header: `[Arc 0 | Rot 0 | Lane Me | w=1]`
- Workflow role: Canonical addressing, base-4 station coding, and identity-preserving lattice placement.
- Primary hubs: `AppA -> AppC -> AppB -> AppI -> AppM`

### Ch03<0002> - Truth Corridors and Witness Discipline
- Station header: `[Arc 0 | Rot 0 | Lane Sa | w=2]`
- Workflow role: Corridor truth typing, admissibility, residual law, and replay obligations.
- Primary hubs: `AppA -> AppI -> AppM -> AppJ`

### Ch04<0003> - Zero-Point Stabilization
- Station header: `[Arc 1 | Rot 1 | Lane Me | w=3]`
- Workflow role: PZPM intake, normalization, and paradox-safe fixed-point preparation.
- Primary hubs: `AppA -> AppC -> AppE -> AppJ -> AppI -> AppM`

### Ch05<0010> - Paradox Regimes and Quarantine Calculus
- Station header: `[Arc 1 | Rot 1 | Lane Sa | w=4]`
- Workflow role: Classical, stratified, and quarantine regimes for stabilized contradiction management.
- Primary hubs: `AppA -> AppC -> AppI -> AppB -> AppL -> AppM`

### Ch06<0011> - Documents-as-Theories
- Station header: `[Arc 1 | Rot 1 | Lane Su | w=5]`
- Workflow role: Theory-documents, manuscript objects, and theorem-bearing document shells.
- Primary hubs: `AppA -> AppC -> AppI -> AppM`

### Ch07<0012> - Tunnels as Morphisms
- Station header: `[Arc 2 | Rot 2 | Lane Sa | w=6]`
- Workflow role: Lawful transports, shadow-axis rotation, and typed tunnel semantics.
- Primary hubs: `AppA -> AppE -> AppH -> AppL -> AppI -> AppM`

### Ch08<0013> - Synchronization Calculus
- Station header: `[Arc 2 | Rot 2 | Lane Su | w=7]`
- Workflow role: The operator S, latent-core semantics z, and cross-document sync budgets.
- Primary hubs: `AppA -> AppE -> AppM -> AppB -> AppJ -> AppI`

### Ch09<0020> - Retrieval and Metro Routing
- Station header: `[Arc 2 | Rot 2 | Lane Me | w=8]`
- Workflow role: Address-first search, metro rides, and route competition over the mycelium graph.
- Primary hubs: `AppA -> AppE -> AppI -> AppH -> AppL -> AppM`

### Ch10<0021> - Multi-Lens Solution Construction
- Station header: `[Arc 3 | Rot 0 | Lane Su | w=9]`
- Workflow role: Synthesis of routed evidence into canonical answer objects and patch-bearing artifacts.
- Primary hubs: `AppA -> AppF -> AppM -> AppH -> AppJ -> AppI`

### Ch11<0022> - Void Book and Restart-Token Tunneling
- Station header: `[Arc 3 | Rot 0 | Lane Me | w=10]`
- Workflow role: Aether versus Void transport, restart continuity, and lawful reset by capsule.
- Primary hubs: `AppA -> AppF -> AppM -> AppL -> AppI`

### Ch12<0023> - Legality, Certificates, and Closure
- Station header: `[Arc 3 | Rot 0 | Lane Sa | w=11]`
- Workflow role: Proof-carrying closure, certificate bundles, and OK-promotion obligations.
- Primary hubs: `AppA -> AppF -> AppC -> AppM -> AppI`

### Ch13<0030> - Memory, Regeneration, and Persistence
- Station header: `[Arc 4 | Rot 1 | Lane Me | w=12]`
- Workflow role: Replayable memory objects, regeneration economics, and long-range continuity.
- Primary hubs: `AppA -> AppG -> AppE -> AppM -> AppJ -> AppI`

### Ch14<0031> - Migration, Versioning, and Pulse Retro Weaving
- Station header: `[Arc 4 | Rot 1 | Lane Sa | w=13]`
- Workflow role: MIGRATE discipline, compat matrices, delta packs, and rollback governance.
- Primary hubs: `AppA -> AppG -> AppM -> AppH -> AppK -> AppI`

### Ch15<0032> - CUT Architecture
- Station header: `[Arc 4 | Rot 1 | Lane Su | w=14]`
- Workflow role: Computation Universe Toolkit modules, APIs, and implementable system contracts.
- Primary hubs: `AppA -> AppG -> AppC -> AppJ -> AppI -> AppM`

### Ch16<0033> - Verification Harnesses and Replay Kernels
- Station header: `[Arc 5 | Rot 2 | Lane Sa | w=15]`
- Workflow role: Deterministic re-checks, test capsules, and correctness enforcement.
- Primary hubs: `AppA -> AppN -> AppM -> AppK -> AppI`

### Ch17<0100> - Deployment and Bounded Agency
- Station header: `[Arc 5 | Rot 2 | Lane Su | w=16]`
- Workflow role: Cloud limbs, execution workers, and governed action under explicit corridors.
- Primary hubs: `AppA -> AppN -> AppE -> AppJ -> AppI -> AppM`

### Ch18<0101> - Macro Invariants and Universal Math Stack
- Station header: `[Arc 5 | Rot 2 | Lane Me | w=17]`
- Workflow role: Global invariants across Macro, PZPM, and CUT coordinate layers.
- Primary hubs: `AppA -> AppN -> AppC -> AppL -> AppI -> AppM`

### Ch19<0102> - Convergence, Fixed Points, and Controlled Non-Convergence
- Station header: `[Arc 6 | Rot 0 | Lane Su | w=18]`
- Workflow role: Banach-style convergence, residual persistence, and sanctioned non-closure.
- Primary hubs: `AppA -> AppP -> AppI -> AppB -> AppJ -> AppM`

### Ch20<0103> - Collective Authoring and Three-Agent Synchrony
- Station header: `[Arc 6 | Rot 0 | Lane Me | w=19]`
- Workflow role: Parallel manuscript governance, merge discipline, and collaborative mycelium control.
- Primary hubs: `AppA -> AppP -> AppE -> AppL -> AppI -> AppM`

### Ch21<0110> - Self-Replication, Open Problems, and the Next Crystal
- Station header: `[Arc 6 | Rot 0 | Lane Sa | w=20]`
- Workflow role: The manuscript as seed, generator, and future metro for the next tome.
- Primary hubs: `AppA -> AppP -> AppM -> AppL -> AppI`

## Appendix hub grid (4x4)

```
Row 0 (Square):   AppA  AppB  AppC  AppD
Row 1 (Flower):   AppE  AppF  AppG  AppH
Row 2 (Cloud):    AppI  AppJ  AppK  AppL
Row 3 (Fractal):  AppM  AppN  AppO  AppP
```

## Appendix hub roles

- **AppA** — Addressing, symbols, parsing grammar, entry station
- **AppB** — Canon laws, equivalence/commutation budgets, normal forms
- **AppC** — Square kernel pack: DLS/DLS++ schedules, discrete mixing, index algebra
- **AppD** — Registry: Ms derivation, router profiles, pinned policies, version ids
- **AppE** — Circle gear: mixed-radix clock, phase lock constraints, integer bridges
- **AppF** — Transport: rotation-as-conjugacy, DUAL legality, commutation harness
- **AppG** — Triangle control: Tria Prima, carry/hatch triggers, recursion legality
- **AppH** — Coupling/topology: dependency closure, isolation/coupling invariants
- **AppI** — Corridors + truth lattice, admissibility budgets, abstain law procedures
- **AppJ** — Residual ledgers, drift envelopes, bounded approximation machinery (NEAR)
- **AppK** — Conflict/quarantine/revocation receipts (FAIL/CONFLICT)
- **AppL** — Evidence-plan templates, PRW delta discipline, "promote AMBIG" harness
- **AppM** — Replay kernel, verifier capsule formats, determinism checklists
- **AppN** — Container formats, virtual mount, salvage/seek doctrine
- **AppO** — Publication import/export bundles, signatures, revocation rules
- **AppP** — Deployment profiles, conformance reports, monitoring templates
