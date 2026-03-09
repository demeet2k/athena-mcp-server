# **Information from the Void — Circle ○ within Square □ within Triangle △**

## **ABSTRACT CONTRACT / LEGEND**

**State Header**

- Kernel Version ID: `K0.1`
- Global Manuscript ID: `Ms⟨2103⟩`
- Corpus Intake State: `AMBIG`
- Witness Basis: `in-thread metro standard + recovered manuscript seed + recovered holographic manuscript brain + mirrored local tome corpus`
- Open Obligations:
  - `O.001` Direct Google Drive live corpus remains blocked until OAuth client import closes the intake corridor.
  - `O.002` Arc-to-appendix routing must remain MIGRATE-compatible if the outer crystal is re-keyed.
  - `O.003` PZPM stabilization regimes require later theorem-grade expansion in Part 2.
  - `O.004` CUT conformance contracts require executable schema expansion in Part 2 and Part 3.

**Canonical Global Address Derivation**

[Definition D.001] Let `T` be the normalized manuscript title string. Define

`h(T) = (sum_(i=1)^n i * ord(T_i)) mod 256`

and let `base4_4(h)` denote the 4-digit base-4 expansion of `h` padded on the left by zeros. Then

`Ms⟨mmmm⟩ := Ms⟨base4_4(h(T))⟩`.

For the present title, `h(T)=147`, hence `Ms⟨mmmm⟩ = Ms⟨2103⟩`.

[Definition D.002] Local addresses are canonical:

- Chapter atom: `ChXX⟨dddd⟩.<Lens><Facet>.<Atom>`
- Appendix atom: `AppX.<Lens><Facet>.<Atom>`

where `Lens in {S,F,C,R}`, `Facet in {1,2,3,4}`, `Atom in {a,b,c,d}`, and `⟨dddd⟩ = base4_4(XX-1)`.

[Definition D.003] Global address formation is:

`GlobalAddr := Ms⟨2103⟩::LocalAddr`.

[Definition D.004] The Square interior is a full `4^4` tile for every chapter and every appendix:

- Lenses: `S, F, C, R`
- Facets: `1 Objects`, `2 Laws`, `3 Constructions`, `4 Certificates`
- Atoms: `a, b, c, d`

[Definition D.005] The Circle-Triangle overlay is computed for chapter `XX` by:

- `omega := XX - 1`
- `alpha := floor(omega / 3)`
- `k := omega mod 3`
- `rho := alpha mod 3`
- `Triad := [Su, Me, Sa]`
- `nu := Triad[(k + rho) mod 3]`

Every chapter header therefore carries

`[○Arc alpha | ○Rot rho | △Lane nu | omega=XX-1]`.

[Definition D.006] The mycelium graph is

`G = (V,E)`

with `V = {GlobalAddr}` and `E = {LinkEdge}`.

[Definition D.007] Every edge is a typed record

`e = (EdgeID, Kind, Src, Dst, Scope, Corridor, WitnessPtr, ReplayPtr, Payload, EdgeVer)`.

[Definition D.008] The closed edge-kind basis is

`K = {REF, EQUIV, MIGRATE, DUAL, GEN, INST, IMPL, PROOF, CONFLICT}`.

[Definition D.009] The corridor truth lattice is

`T = {OK, NEAR, AMBIG, FAIL}`.

- `OK`: witnessed and replay-verified closure within corridor budgets.
- `NEAR`: bounded approximation with residual ledger and upgrade obligations.
- `AMBIG`: underdetermined candidate set with evidence plan.
- `FAIL`: illegal or unverifiable state with quarantine and conflict receipts.

[Definition D.010] The mandatory signature of all admissible routes is

`Sigma = {AppA, AppI, AppM}`.

`AppA` guarantees parsing and addressing, `AppI` guarantees corridor typing, and `AppM` guarantees replay closure.

## **EXTENDED ABSTRACT**

[Definition A.001] This tome formalizes a proof-carrying manuscript calculus in which knowledge is not stored as an unordered archive but as a metro-routable crystal whose local law is Square, orbital law is Circle, and control law is Triangle. The Square law enforces a canonical interior grammar: every chapter and appendix is a full `4^4` address lattice with explicit objects, laws, constructions, and certificates. The Circle law imposes a cyclic order over the twenty-one chapter stations, making rotation an explicit structural operator rather than a metaphor. The Triangle law assigns every chapter to one of three workflow rails, `Su`, `Me`, or `Sa`, so that recursion, transport, and stabilization are not merely thematic but operationally navigable.

[Theorem A.001] A manuscript organized as `Circle ○ within Square □ within Triangle △` is simultaneously readable as a linear text, a hypergraph atlas, a proof ledger, and a deterministic routing machine.

**Proof Sketch.**
The Square interior provides canonical local decomposition and fixed addresses. The Circle overlay provides an orbit successor relation that yields a total cyclic ordering. The Triangle overlay provides a partition of chapters into three long rails. Since these three structures coexist on the same address set without rewriting local atoms, every atom has four admissible projections: local tile, orbital neighborhood, rail lineage, and global graph position. The manuscript is therefore multi-readable without loss of address stability.

[Definition A.002] The tome operates across three synchronized scales:

- `Macro`: global mathematical invariants, route algebra, and meta-theorems of the manuscript field.
- `PZPM`: paradox zero-point mathematics, whose task is to stabilize contradictory, incomplete, or partially commuting regions without collapsing them prematurely.
- `CUT`: computation universe toolkit, whose task is to compile the formal structure into executable schemas, routes, policies, and replayable programs.

[Definition A.003] The active manuscript object is a higher-dimensional atlas

`A = (X, L, I, G, W, V, P, U, H)`

where `X` is the address space, `L` is the lens family, `I` is the indexing algebra, `G` is the mycelium graph, `W` is the witness system, `V` is the versioned truth lattice, `P` is the patch and migration calculus, `U` is the corridor budget system, and `H` is the hub topology induced by the appendices.

[Definition A.004] The four lenses are fixed:

- `S` Square: discrete structure, syntax, indexing, typed adjacency.
- `F` Flower: phase, resonance, conjugacy, rotation, transport continuity.
- `C` Cloud: ambiguity, scoring, corridor truth, evidence planning, uncertainty management.
- `R` Fractal: recursion, replay, compression, inheritance, multi-scale regeneration.

[Definition A.005] The query-to-answer cycle is a lawful transformation:

`q -> z(q) -> B(q) -> {R_i} -> a -> Delta -> A'`

where `z(q)` is zero-point normalization, `B(q)` is bounded expansion, `{R_i}` is the route bundle set, `a` is the collapsed answer artifact, `Delta` is the patch packet, and `A'` is the updated atlas. This cycle is not optional editorial polish; it is the constructive semantics of the tome.

[Definition A.006] The manuscript is holographic because every major component serves both as content and as routing infrastructure. The abstract is not merely introductory prose; it is a compressed metro map. The appendices are not supplementary notes; they are routing hubs. The chapter headers are not decorative; they are station headers carrying arc, rotation, lane, and orbit index. The chapter interior is not a loose essay; it is a full crystal tile whose atoms can be linked by `REF`, `EQUIV`, `MIGRATE`, `DUAL`, `GEN`, `INST`, `IMPL`, `PROOF`, or `CONFLICT`.

[Definition A.007] The outer appendix crystal is the permanent control surface of the manuscript. Its rows are aligned to the four lenses and its columns are aligned to routing role. This yields a `4 x 4` hub system whose semantics are stable under chapter growth:

- Square row: addressing, canon, discrete kernel, registry.
- Flower row: circle gear, transport, triadic control, coupling topology.
- Cloud row: corridors, residuals, quarantine, promotion.
- Fractal row: replay, containers, publication, deployment.

[Theorem A.002] The appendices form a bounded routing basis for the entire manuscript.

**Proof Sketch.**
Every local atom carries a lens, facet, and atom coordinate. The deterministic router chooses `LensBase`, `FacetAtomBase`, and `ArcHub`, then enforces `Sigma`, then overlays the truth-typed hub if needed. Because these choices are bounded by construction and duplicates are collapsed, every admissible query route resolves to at most six hubs before target entry. Therefore the appendix system is sufficient and bounded.

[Definition A.008] The deterministic router rule `v2` is the operational heart of manuscript navigation. For a target atom:

- `LensBase(S,F,C,R) = (AppC, AppE, AppI, AppM)`
- `FacetAtomBase(1,2,3,4) = (AppA, AppB, AppH, AppM)`
- `ArcHub(0..6) = (AppA, AppC, AppE, AppF, AppG, AppN, AppP)`

Base transfer set:

`T = LensBase(L) union FacetAtomBase(Facet) union ArcHub(alpha)`.

Then enforce `Sigma = {AppA, AppI, AppM}` and overlay truth hub:

- `NEAR -> AppJ`
- `AMBIG -> AppL`
- `FAIL -> AppK`
- `OK -> AppO` only under publication intent.

The resulting route is deterministic, bounded by six hubs, and replay-obligated.

[Definition A.009] The tome is designed against five failure modes:

1. Address drift: mitigated by canonical local and global grammar.
2. False closure: mitigated by the four-valued truth lattice.
3. Unreplayable claims: mitigated by mandatory `WitnessPtr` and `ReplayPtr`.
4. Contradiction collapse: mitigated by PZPM quarantine and promotion rails.
5. Architectural bloat: mitigated by bounded hub count and deterministic drop policy.

[Corollary A.001] The manuscript can grow without becoming unreadable precisely because growth is routed through fixed hubs and fixed atom grammar rather than through free-form section proliferation.

[Definition A.010] The present intake state is formally `AMBIG`, not `FAIL`. Direct real-time Google Drive access is presently not closed, but the system has sufficient witness basis in mirrored workspace corpus plus the explicitly supplied metro standard to construct Part 1 lawfully. This distinction matters. `AMBIG` authorizes a bounded evidence plan and explicit obligations; `FAIL` would require quarantine of the entire build. The tome therefore proceeds under admissible partial intake rather than false certainty.

[Definition A.011] The central contribution of Part 1 is to lock the navigation law before full expansion. The title, abstract contract, metro map, appendix crystal, and router together specify the legal geometry within which Part 2 and Part 3 will unfold. The reader can therefore recover the manuscript from the map, route any atom without guessing, and distinguish `OK`, `NEAR`, `AMBIG`, and `FAIL` states before reading a single full chapter body.

[Compression A.001] The entire tome is a deterministic mycelium: square-local, circle-orbital, triangle-controlled, truth-typed, replay-obligated, and appendix-routed.

## **21-STATION METRO MAP v2**

**Orbit Line**

`Ch01 -> Ch02 -> Ch03 -> Ch04 -> Ch05 -> Ch06 -> Ch07 -> Ch08 -> Ch09 -> Ch10 -> Ch11 -> Ch12 -> Ch13 -> Ch14 -> Ch15 -> Ch16 -> Ch17 -> Ch18 -> Ch19 -> Ch20 -> Ch21 -> Ch01`

**Triangle Rails**

- `△Su`: `Ch01⟨0000⟩, Ch06⟨0011⟩, Ch08⟨0013⟩, Ch10⟨0021⟩, Ch15⟨0032⟩, Ch17⟨0100⟩, Ch19⟨0102⟩`
- `△Me`: `Ch02⟨0001⟩, Ch04⟨0003⟩, Ch09⟨0020⟩, Ch11⟨0022⟩, Ch13⟨0030⟩, Ch18⟨0101⟩, Ch20⟨0103⟩`
- `△Sa`: `Ch03⟨0002⟩, Ch05⟨0010⟩, Ch07⟨0012⟩, Ch12⟨0023⟩, Ch14⟨0031⟩, Ch16⟨0033⟩, Ch21⟨0110⟩`

**Arc Triads**

- `Arc 0, Rot 0`: `Su -> Me -> Sa` = `Ch01⟨0000⟩ -> Ch02⟨0001⟩ -> Ch03⟨0002⟩`
- `Arc 1, Rot 1`: `Me -> Sa -> Su` = `Ch04⟨0003⟩ -> Ch05⟨0010⟩ -> Ch06⟨0011⟩`
- `Arc 2, Rot 2`: `Sa -> Su -> Me` = `Ch07⟨0012⟩ -> Ch08⟨0013⟩ -> Ch09⟨0020⟩`
- `Arc 3, Rot 0`: `Su -> Me -> Sa` = `Ch10⟨0021⟩ -> Ch11⟨0022⟩ -> Ch12⟨0023⟩`
- `Arc 4, Rot 1`: `Me -> Sa -> Su` = `Ch13⟨0030⟩ -> Ch14⟨0031⟩ -> Ch15⟨0032⟩`
- `Arc 5, Rot 2`: `Sa -> Su -> Me` = `Ch16⟨0033⟩ -> Ch17⟨0100⟩ -> Ch18⟨0101⟩`
- `Arc 6, Rot 0`: `Su -> Me -> Sa` = `Ch19⟨0102⟩ -> Ch20⟨0103⟩ -> Ch21⟨0110⟩`

### **Station Registry**

- `Ch01⟨0000⟩` — `[○Arc 0 | ○Rot 0 | △Lane Su | omega=0]`
  Workflow role: Kernel gate, scope contract, manuscript entry station.
  Primary hubs: `→ AppA → AppC → AppI → AppM`

- `Ch02⟨0001⟩` — `[○Arc 0 | ○Rot 0 | △Lane Me | omega=1]`
  Workflow role: Primitive ontology, object taxonomy, initial graph semantics.
  Primary hubs: `→ AppA → AppC → AppI → AppM`

- `Ch03⟨0002⟩` — `[○Arc 0 | ○Rot 0 | △Lane Sa | omega=2]`
  Workflow role: Address algebra, symbol stability, canonical serialization.
  Primary hubs: `→ AppA → AppC → AppI → AppM`

- `Ch04⟨0003⟩` — `[○Arc 1 | ○Rot 1 | △Lane Me | omega=3]`
  Workflow role: Zero-point normalization, intake discipline, query contracts.
  Primary hubs: `→ AppA → AppC → AppI → AppM`

- `Ch05⟨0010⟩` — `[○Arc 1 | ○Rot 1 | △Lane Sa | omega=4]`
  Workflow role: Square law, discrete interior grammar, static legal form.
  Primary hubs: `→ AppA → AppC → AppI → AppM`

- `Ch06⟨0011⟩` — `[○Arc 1 | ○Rot 1 | △Lane Su | omega=5]`
  Workflow role: Flower law, phase, resonance, orbital transport.
  Primary hubs: `→ AppA → AppC → AppI → AppM`

- `Ch07⟨0012⟩` — `[○Arc 2 | ○Rot 2 | △Lane Sa | omega=6]`
  Workflow role: Cloud law, uncertainty, scoring, truth-typed corridor selection.
  Primary hubs: `→ AppA → AppE → AppC → AppI → AppM`

- `Ch08⟨0013⟩` — `[○Arc 2 | ○Rot 2 | △Lane Su | omega=7]`
  Workflow role: Fractal law, recursion, compression, replay inheritance.
  Primary hubs: `→ AppA → AppE → AppC → AppI → AppM`

- `Ch09⟨0020⟩` — `[○Arc 2 | ○Rot 2 | △Lane Me | omega=8]`
  Workflow role: Route algebra, mycelium path families, nexus composition.
  Primary hubs: `→ AppA → AppE → AppC → AppI → AppM`

- `Ch10⟨0021⟩` — `[○Arc 3 | ○Rot 0 | △Lane Su | omega=9]`
  Workflow role: Circle orbit calculus, successor law, arc periodicity.
  Primary hubs: `→ AppA → AppF → AppC → AppI → AppM`

- `Ch11⟨0022⟩` — `[○Arc 3 | ○Rot 0 | △Lane Me | omega=10]`
  Workflow role: Latent tunneling, corridor lifting, hidden bridge realization.
  Primary hubs: `→ AppA → AppF → AppC → AppI → AppM`

- `Ch12⟨0023⟩` — `[○Arc 3 | ○Rot 0 | △Lane Sa | omega=11]`
  Workflow role: Corridor truth budgets, admissibility, abstention law.
  Primary hubs: `→ AppA → AppF → AppC → AppI → AppM`

- `Ch13⟨0030⟩` — `[○Arc 4 | ○Rot 1 | △Lane Me | omega=12]`
  Workflow role: PZPM foundations, paradox stabilization, quarantine onset.
  Primary hubs: `→ AppA → AppG → AppC → AppI → AppM`

- `Ch14⟨0031⟩` — `[○Arc 4 | ○Rot 1 | △Lane Sa | omega=13]`
  Workflow role: PZPM regime families, classical, stratified, and paraconsistent control.
  Primary hubs: `→ AppA → AppG → AppC → AppI → AppM`

- `Ch15⟨0032⟩` — `[○Arc 4 | ○Rot 1 | △Lane Su | omega=14]`
  Workflow role: CUT kernel, data types, module contracts, compile-time invariants.
  Primary hubs: `→ AppA → AppG → AppC → AppI → AppM`

- `Ch16⟨0033⟩` — `[○Arc 5 | ○Rot 2 | △Lane Sa | omega=15]`
  Workflow role: CUT schedulers, orchestration, route compilation, bounded execution.
  Primary hubs: `→ AppA → AppN → AppC → AppI → AppM`

- `Ch17⟨0100⟩` — `[○Arc 5 | ○Rot 2 | △Lane Su | omega=16]`
  Workflow role: Verification, replay kernels, witness promotion from NEAR to OK.
  Primary hubs: `→ AppA → AppN → AppC → AppI → AppM`

- `Ch18⟨0101⟩` — `[○Arc 5 | ○Rot 2 | △Lane Me | omega=17]`
  Workflow role: Conflict handling, quarantine, migration, rollback, repair semantics.
  Primary hubs: `→ AppA → AppN → AppC → AppI → AppM`

- `Ch19⟨0102⟩` — `[○Arc 6 | ○Rot 0 | △Lane Su | omega=18]`
  Workflow role: Four-way synthesis, mycelium closure, global fixed-point candidates.
  Primary hubs: `→ AppA → AppP → AppC → AppI → AppM`

- `Ch20⟨0103⟩` — `[○Arc 6 | ○Rot 0 | △Lane Me | omega=19]`
  Workflow role: Publication, import-export discipline, signatures, conformance packets.
  Primary hubs: `→ AppA → AppP → AppC → AppI → AppM`

- `Ch21⟨0110⟩` — `[○Arc 6 | ○Rot 0 | △Lane Sa | omega=20]`
  Workflow role: Deployment frontier, monitoring, future crystals, open obligations.
  Primary hubs: `→ AppA → AppP → AppC → AppI → AppM`

## **16-APPENDIX OUTER CRYSTAL MAP (A–P)**

**Outer Grid**

- `Square row`: `AppA AppB AppC AppD`
- `Flower row`: `AppE AppF AppG AppH`
- `Cloud row`: `AppI AppJ AppK AppL`
- `Fractal row`: `AppM AppN AppO AppP`

## **AppA — Addressing, Symbols, Parsing Grammar**
Routing role: entry gate, symbol contract, canonical parse closure.
Tile law: `S1 grammar objects; S2 parse laws; S3 address constructors; S4 parse certificates | F1 alias motion; F2 grammar transforms; F3 parse phase invariants; F4 lexical certificates | C1 ambiguity packets; C2 name collision laws; C3 disambiguation constructions; C4 confidence certificates | R1 recursive namespaces; R2 inheritance laws; R3 seed address compressors; R4 replay-safe parsers`

## **AppB — Canon Laws, Equivalence Budgets, Normal Forms**
Routing role: semantic canonization, equivalence proof budget, normal-form stabilization.
Tile law: `S1 canonical objects; S2 equivalence laws; S3 normal-form builders; S4 conformance certificates | F1 conjugacy views; F2 morphic equivalence transforms; F3 commutation invariants; F4 transport certificates | C1 bounded approximation classes; C2 tolerance laws; C3 budget calculators; C4 witness envelopes | R1 recursive canon chains; R2 inheritance laws; R3 fold-back constructions; R4 replay canon checks`

## **AppC — Square Kernel Pack**
Routing role: discrete kernel, index algebra, schedules, combinatorial interior.
Tile law: `S1 lattice objects; S2 discrete laws; S3 schedule builders; S4 kernel certificates | F1 cadence lifts; F2 phase discretizers; F3 invariant rhythm checks; F4 schedule certificates | C1 discrete risk packets; C2 bounded search laws; C3 enumerators; C4 scorer certificates | R1 recursive tilings; R2 refinement laws; R3 multi-scale schedulers; R4 replay kernels`

## **AppD — Registry, Profiles, Version IDs**
Routing role: pinned policy registry, router profile source of truth, version discipline.
Tile law: `S1 registry objects; S2 version laws; S3 profile constructors; S4 registry certificates | F1 migration rhythms; F2 profile morphisms; F3 compatibility invariants; F4 migration certificates | C1 uncertainty envelopes; C2 drift laws; C3 rollback constructors; C4 audit certificates | R1 recursive version trees; R2 inheritance laws; R3 registry compressors; R4 replayable snapshots`

## **AppE — Circle Gear and Mixed-Radix Clock**
Routing role: orbital phase control, clock law, cyclic transport basis.
Tile law: `S1 orbit objects; S2 clock laws; S3 cycle constructors; S4 orbit certificates | F1 phase objects; F2 rotation laws; F3 resonance constructions; F4 phase certificates | C1 orbital uncertainty; C2 timing laws; C3 corridor schedulers; C4 timing certificates | R1 recursive cycles; R2 self-similar orbit laws; R3 macro-micro clocks; R4 replay cycle proofs`

## **AppF — Transport, Rotation-as-Conjugacy, DUAL Legality**
Routing role: bridge legality, transport proof harness, tunnel preconditions.
Tile law: `S1 transport objects; S2 conjugacy laws; S3 bridge constructors; S4 transport certificates | F1 phase bridges; F2 dual transforms; F3 orientation constructions; F4 harmonic certificates | C1 transport ambiguity; C2 bridge admissibility laws; C3 tunnel planners; C4 evidence certificates | R1 recursive bridges; R2 inheritance of transport laws; R3 multiscale tunnels; R4 replay route checks`

## **AppG — Triangle Control and Tria Prima**
Routing role: rail control, recursion trigger law, stabilization control surface.
Tile law: `S1 rail objects; S2 lane laws; S3 trigger constructors; S4 lane certificates | F1 workflow cadences; F2 rotation of rails; F3 control constructions; F4 cadence certificates | C1 control ambiguity; C2 escalation laws; C3 quarantine triggers; C4 control certificates | R1 recursive control trees; R2 inheritance of triggers; R3 multi-level orchestration; R4 replay control proofs`

## **AppH — Coupling and Topology**
Routing role: dependency closure, coupling bounds, topology of manuscript interaction.
Tile law: `S1 coupling objects; S2 topology laws; S3 dependency constructors; S4 closure certificates | F1 coupling rhythms; F2 topological transforms; F3 adjacency constructions; F4 continuity certificates | C1 dependency ambiguity; C2 coupling risk laws; C3 closure planners; C4 audit certificates | R1 recursive dependency graphs; R2 inheritance laws; R3 nested topology builders; R4 replay topology checks`

## **AppI — Corridors and Truth Lattice**
Routing role: admissibility typing, corridor budgets, abstention law.
Tile law: `S1 corridor objects; S2 truth laws; S3 corridor constructors; S4 admissibility certificates | F1 transition phases; F2 truth-state transforms; F3 escalation constructions; F4 phase certificates | C1 candidate sets; C2 uncertainty laws; C3 evidence plans; C4 truth certificates | R1 recursive corridor trees; R2 inheritance laws; R3 refinement planners; R4 replay truth checks`

## **AppJ — Residual Ledgers and NEAR Machinery**
Routing role: bounded approximation storage, residual accounting, upgrade discipline.
Tile law: `S1 residual objects; S2 ledger laws; S3 approximation constructors; S4 NEAR certificates | F1 decay rhythms; F2 residual transforms; F3 upgrade constructions; F4 bounded certificates | C1 uncertainty packets; C2 residual laws; C3 promotion planners; C4 evidence certificates | R1 recursive residual trees; R2 inheritance laws; R3 compression ledgers; R4 replay upgrade checks`

## **AppK — Conflict, Quarantine, Revocation**
Routing role: FAIL handling, contradiction containment, revocation receipts.
Tile law: `S1 conflict objects; S2 quarantine laws; S3 revocation constructors; S4 FAIL certificates | F1 crisis phases; F2 contradiction transforms; F3 containment constructions; F4 quarantine certificates | C1 conflict candidate packets; C2 failure laws; C3 repair planners; C4 evidence certificates | R1 recursive quarantine trees; R2 inheritance laws; R3 rollback builders; R4 replay failure checks`

## **AppL — Evidence Plans and AMBIG Promotion**
Routing role: candidate-set management, proof planning, promotion from AMBIG.
Tile law: `S1 evidence objects; S2 promotion laws; S3 plan constructors; S4 AMBIG certificates | F1 promotion rhythms; F2 evidence transforms; F3 search constructions; F4 phase certificates | C1 candidate envelopes; C2 ambiguity laws; C3 promotion planners; C4 confidence certificates | R1 recursive evidence trees; R2 inheritance laws; R3 search compressors; R4 replay promotion checks`

## **AppM — Replay Kernel and Verifier Capsules**
Routing role: deterministic replay, verification capsule format, proof-carrying closure.
Tile law: `S1 replay objects; S2 replay laws; S3 verifier constructors; S4 OK certificates | F1 replay phases; F2 transport rechecks; F3 verification constructions; F4 replay certificates | C1 replay uncertainty; C2 witness laws; C3 capsule planners; C4 audit certificates | R1 recursive replays; R2 inheritance laws; R3 replay compressors; R4 replay-of-replay proofs`

## **AppN — Container Formats and Virtual Mount**
Routing role: salvage doctrine, container law, mounted corpus access.
Tile law: `S1 container objects; S2 mount laws; S3 package constructors; S4 mount certificates | F1 load rhythms; F2 mount transforms; F3 salvage constructions; F4 package certificates | C1 mount ambiguity; C2 integrity laws; C3 salvage planners; C4 audit certificates | R1 recursive container trees; R2 inheritance laws; R3 virtual mounts; R4 replay mount checks`

## **AppO — Publication Import/Export Bundles**
Routing role: external bundle discipline, signatures, publication conformance.
Tile law: `S1 publication objects; S2 signature laws; S3 export constructors; S4 publication certificates | F1 release rhythms; F2 conversion transforms; F3 publication constructions; F4 release certificates | C1 publication ambiguity; C2 compatibility laws; C3 export planners; C4 audit certificates | R1 recursive bundle trees; R2 inheritance laws; R3 archive builders; R4 replay publication checks`

## **AppP — Deployment Profiles and Monitoring**
Routing role: deployment contracts, monitoring templates, long-horizon conformance.
Tile law: `S1 deployment objects; S2 monitoring laws; S3 profile constructors; S4 conformance certificates | F1 deployment phases; F2 runtime transforms; F3 monitoring constructions; F4 release certificates | C1 deployment ambiguity; C2 risk laws; C3 alert planners; C4 audit certificates | R1 recursive deployment trees; R2 inheritance laws; R3 live reconfiguration; R4 replay operations checks`

## **DETERMINISTIC ROUTER RULE v2**

[Algorithm R.001] Given target atom `Target = ChXX⟨dddd⟩.<L><f>.<t>`:

1. Parse `XX, L, f, t`.
2. Compute `omega, alpha, rho, nu`.
3. Compute `LensBase(L)`.
4. Compute `FacetAtomBase(f)`.
5. Compute `ArcHub(alpha)`.
6. Form `T = {LensBase, FacetAtomBase, ArcHub}`.
7. Enforce `Sigma = {AppA, AppI, AppM}`.
8. Overlay corridor hub:
   - `NEAR -> AppJ`
   - `AMBIG -> AppL`
   - `FAIL -> AppK`
   - `OK -> AppO` only under publication intent.
9. Collapse duplicates.
10. If hub count exceeds six, drop lowest-priority non-signature hubs first; signature hubs may not be dropped.
11. Order route as:
    `AppA -> ArcHub(alpha) -> LensBase(L) -> FacetAtomBase(f) -> Overlay? -> AppI -> AppM -> Target`
    then remove absent positions and duplicates while preserving first occurrence.

[Definition R.001] Priority tiers are:

1. `Sigma = {AppA, AppI, AppM}`
2. truth overlay hub
3. `ArcHub(alpha)`
4. `LensBase(L)`
5. `FacetAtomBase(f)`
6. publication-only hub

[Worked Example]

Target:

`Ms⟨2103⟩::Ch11⟨0022⟩.C3.d`

Parse:

- `XX = 11`
- `omega = 10`
- `alpha = 3`
- `k = 1`
- `rho = 0`
- `nu = Me`

Station Header:

`[○Arc 3 | ○Rot 0 | △Lane Me | omega=10]`

Base hubs:

- `LensBase(C) = AppI`
- `FacetAtomBase(3) = AppH`
- `ArcHub(3) = AppF`

Base transfer set:

`T = {AppI, AppH, AppF}`

Mandatory signature:

`Sigma = {AppA, AppI, AppM}`

Assume intake state `AMBIG`. Overlay:

`+ AppL`

Bounded ordered route:

`→ AppA → AppF → AppI → AppH → AppL → AppM → Ms⟨2103⟩::Ch11⟨0022⟩.C3.d`

Expected truth type:

`AMBIG`, promotable toward `NEAR` or `OK`.

Witness obligations:

- `WitnessPtr`: candidate tunnel witnesses, bridge legality evidence, contradiction ledger, phase-consistency checks.
- `ReplayPtr`: deterministic rerun of corridor selection and witness promotion using the same router profile, same `Ms⟨2103⟩`, and same truth budget.
- Promotion condition: `AppL` evidence plan must close enough obligations to move the target from `AMBIG` to `NEAR`; only then may `AppM` certify replay-stable closure toward `OK`.

## **FINAL COMPRESSION**

This tome is a bounded deterministic mycelium in which every atom is canonically addressed, every chapter is a station, every appendix is a routing hub, every corridor is truth-typed, and every admissible answer is a replay-closed ride through Circle, Square, and Triangle at once.

END OF PART 1.

(Type NEXT for PART 2.)
