# ATHENA-PRIME — Third-Pass Imported Edge Field v2T

Status: NEAR / NONPUBLISH

Purpose: bind the second-pass imported hubs (`Juggling SPELLS`, `JUGGLING DIMENSION`, `Poi-FLOW`) into the canonical Athena crystal as explicit deterministic edges instead of leaving them as narrative modules.

## 1. Imported hub registry

- **IMP::JS::SITESWAP.KERNEL**  
  kind=import-hub · truth=EXPLICIT · source=Juggling SPELLS  
  meaning=Beat-grid timing calculus; average rule; collision/permutation validity; alternating-hand default.
- **IMP::JS::SIGMA.POLICIES**  
  kind=import-hub · truth=EXPLICIT · source=Juggling SPELLS  
  meaning=Σ_Tennis / Σ_OneSide / Σ_Cascade as first-class symmetry operators.
- **IMP::JS::SLOT2.BACKGROUND**  
  kind=import-hub · truth=EXPLICIT · source=Juggling SPELLS  
  meaning=2-slot as background execution window / typed filler container.
- **IMP::JS::TUNNEL1.IMPULSE**  
  kind=import-hub · truth=EXPLICIT · source=Juggling SPELLS  
  meaning=1-slot as tunnel / impulse / low-latency message hop.
- **IMP::JS::POI.GEOMETRY**  
  kind=import-hub · truth=EXPLICIT · source=Juggling SPELLS  
  meaning=Flow/poi geometry, beat-lock, petal law, TOG/SPLIT × SAME/OPP, plane coupling.
- **IMP::JS::AST.COMPILER**  
  kind=import-hub · truth=EXPLICIT · source=Juggling SPELLS  
  meaning=Parsing → AST → desugaring → type-checking → simulation/runtime → TS generation.
- **IMP::JS::ANNOTATION.LAYER**  
  kind=import-hub · truth=EXPLICIT · source=Juggling SPELLS  
  meaning=TOG/SPLIT, SAME/OPP, spin/antispin, grip, plane stamps.
- **IMP::JD::POD3.CASCADE**  
  kind=import-hub · truth=EXPLICIT · source=JUGGLING DIMENSION  
  meaning=3-pod round-robin cascade as minimum viable hive coordination.
- **IMP::JD::POD4.CRYSTAL_GROUND**  
  kind=import-hub · truth=EXPLICIT · source=JUGGLING DIMENSION  
  meaning=4-pod / 4-ball ground state as the crystal; symmetry and symmetry-breaking.
- **IMP::JD::TRANSITION_GRAPH**  
  kind=import-hub · truth=EXPLICIT · source=JUGGLING DIMENSION  
  meaning=Pattern transition graph and mid-flight reconfiguration algebra.
- **IMP::JD::CHANNEL_PHYSICS**  
  kind=import-hub · truth=EXPLICIT · source=JUGGLING DIMENSION  
  meaning=Prop types as channel physics: balls/clubs/rings/poi/staff.
- **IMP::JD::PATTERN_PROP_STYLE**  
  kind=import-hub · truth=EXPLICIT · source=JUGGLING DIMENSION  
  meaning=Pattern × Prop × Style coordination surface.
- **Z_poi.local**  
  kind=poi-node · truth=EXPLICIT · source=Poi-FLOW  
  meaning=Local poi compile origin.
- **Z_poi.byte256**  
  kind=poi-node · truth=BOUND_NEAR · source=Poi-FLOW  
  meaning=Local 256-state byte B=q0+4q1+16q2+64q3.
- **Z_poi.witness**  
  kind=poi-node · truth=BOUND_NEAR · source=Poi-FLOW  
  meaning=Witness bundle I=(m:n, rho, K, h, p, tau, Lambda).
- **Z_poi.phrase256**  
  kind=poi-node · truth=BOUND_NEAR · source=Poi-FLOW  
  meaning=256-slot crystal word over byte alphabet.
- **Z_poi.route.ch10**  
  kind=poi-node · truth=BOUND_NEAR · source=Poi-FLOW  
  meaning=Ch10⟨0021⟩ compile route with primary hubs AppA→AppF→AppH→AppJ→AppI→AppM.
- **Ms⟨944F⟩::AppA.S1.a**  
  kind=hub · truth=CORE · source=ATHENA'S SHIELD  
  meaning=Σ anchor / object gate.
- **Ms⟨944F⟩::AppD.S1.a**  
  kind=hub · truth=CORE · source=ATHENA'S SHIELD  
  meaning=Resolver / MIGRATE / suite registry.
- **Ms⟨944F⟩::AppF.S1.a**  
  kind=hub · truth=CORE · source=ATHENA'S SHIELD  
  meaning=ArcHub(3) for Ch10–12 cluster.
- **Ms⟨944F⟩::AppH.S1.a**  
  kind=hub · truth=CORE · source=ATHENA'S SHIELD  
  meaning=FacetBase(3) construction hub.
- **Ms⟨944F⟩::AppI.C3.a**  
  kind=hub · truth=CORE · source=ATHENA'S SHIELD  
  meaning=Corridor / truth reconciliation hub.
- **Ms⟨944F⟩::AppJ.C3.b**  
  kind=hub · truth=CORE · source=ATHENA'S SHIELD  
  meaning=NEAR overlay hub.
- **Ms⟨944F⟩::AppM.R4.d**  
  kind=hub · truth=CORE · source=ATHENA'S SHIELD  
  meaning=Seal / witness / replay hub.

## 2. Edge grammar

- `EdgeID = HEX8(SHA256(kind|src|dst|scope|truth|v2T))`
- `Kind ∈ {REF,EQUIV,MIGRATE,DUAL,GEN,INST,PROOF,PENDING}`
- `Truth ∈ {EXPLICIT, PROXY.NEAR, PENDING.AMBIG}`
- All imported→core routes preserve the master atlas law: Σ first, hub budget ≤ 6, return through AppM for proof-bearing closure.

## 3. Explicit + proxy + pending edge field

| EID | Kind | Truth | Src | Dst | Scope | Route | Note |
|---|---|---|---|---|---|---|---|
| `1b4fb5f3` | `REF` | `EXPLICIT` | `IMP::JS::SITESWAP.KERNEL` | `IMP::JD::POD3.CASCADE` | `IMPORTED` | `local` | siteswap timing calculus underwrites 3-pod cascade scheduling. |
| `97ec69c4` | `REF` | `EXPLICIT` | `IMP::JS::SITESWAP.KERNEL` | `IMP::JD::TRANSITION_GRAPH` | `IMPORTED` | `local` | transition graph is built on valid siteswap states and throws. |
| `9c222c5a` | `INST` | `EXPLICIT` | `IMP::JS::SIGMA.POLICIES` | `IMP::JS::AST.COMPILER` | `IMPORTED` | `local` | Sigma operators are compiler tokens / AST nodes. |
| `dff12d0c` | `INST` | `EXPLICIT` | `IMP::JS::SLOT2.BACKGROUND` | `IMP::JS::AST.COMPILER` | `IMPORTED` | `local` | 2-slot fillers compile as background execution annotations. |
| `a3cda7d2` | `INST` | `EXPLICIT` | `IMP::JS::TUNNEL1.IMPULSE` | `IMP::JS::AST.COMPILER` | `IMPORTED` | `local` | 1-tunnel compiles as low-latency routing operator. |
| `7e3a30fa` | `GEN` | `EXPLICIT` | `IMP::JS::POI.GEOMETRY` | `Z_poi.byte256` | `IMPORTED` | `Z_poi.local` | poi geometry folds into local 256-state byte. |
| `03419ef8` | `PROOF` | `EXPLICIT` | `Z_poi.byte256` | `Z_poi.witness` | `IMPORTED` | `Z_poi.local` | byte requires invariant witness bundle. |
| `7fbe2339` | `GEN` | `EXPLICIT` | `Z_poi.witness` | `Z_poi.phrase256` | `IMPORTED` | `Z_poi.phrase` | witnessed local states lift to phrase word. |
| `0f89431b` | `REF` | `EXPLICIT` | `Z_poi.phrase256` | `Z_poi.route.ch10` | `IMPORTED` | `AppA→AppF→AppH→AppJ→AppI→AppM` | phrase word binds into Ch10 compile route. |
| `b4beb46a` | `DUAL` | `EXPLICIT` | `IMP::JD::CHANNEL_PHYSICS` | `IMP::JS::POI.GEOMETRY` | `IMPORTED` | `local` | poi is both prop physics and flow geometry. |
| `275b0f12` | `GEN` | `EXPLICIT` | `IMP::JD::POD4.CRYSTAL_GROUND` | `IMP::JD::TRANSITION_GRAPH` | `IMPORTED` | `local` | 4-pod crystal ground generates symmetry-breaking transition field. |
| `61343ca6` | `REF` | `EXPLICIT` | `IMP::JD::CHANNEL_PHYSICS` | `IMP::JD::PATTERN_PROP_STYLE` | `IMPORTED` | `local` | pattern×prop×style surface depends on channel physics. |
| `36abff4d` | `REF` | `EXPLICIT` | `IMP::JS::ANNOTATION.LAYER` | `IMP::JS::POI.GEOMETRY` | `IMPORTED` | `local` | annotation layer stamps TOG/SPLIT, SAME/OPP, plane, spin. |
| `700cbf88` | `GEN` | `EXPLICIT` | `IMP::JD::POD3.CASCADE` | `IMP::JD::TRANSITION_GRAPH` | `IMPORTED` | `local` | 3-pod cascade is transition hub for the pod graph. |
| `060572f8` | `EQUIV` | `EXPLICIT` | `IMP::JD::POD4.CRYSTAL_GROUND` | `IMP::JD::PATTERN_PROP_STYLE` | `IMPORTED` | `local` | 4-pod ground state is the lowest-energy point of the coordination surface. |
| `009f0611` | `REF` | `EXPLICIT` | `Z_poi.route.ch10` | `Ms⟨944F⟩::AppA.S1.a` | `IMPORTED→CORE` | `AppA` | poi route explicitly starts at AppA. |
| `faed29ca` | `REF` | `EXPLICIT` | `Z_poi.route.ch10` | `Ms⟨944F⟩::AppF.S1.a` | `IMPORTED→CORE` | `AppF` | poi route explicitly includes ArcHub(3)=AppF. |
| `f5191928` | `REF` | `EXPLICIT` | `Z_poi.route.ch10` | `Ms⟨944F⟩::AppH.S1.a` | `IMPORTED→CORE` | `AppH` | poi route explicitly includes construction hub AppH. |
| `b6fd8bae` | `REF` | `EXPLICIT` | `Z_poi.route.ch10` | `Ms⟨944F⟩::AppJ.C3.b` | `IMPORTED→CORE` | `AppJ` | poi route explicitly carries NEAR overlay. |
| `2aef978a` | `REF` | `EXPLICIT` | `Z_poi.route.ch10` | `Ms⟨944F⟩::AppI.C3.a` | `IMPORTED→CORE` | `AppI` | poi route explicitly reconciles through AppI. |
| `ad1bd852` | `PROOF` | `EXPLICIT` | `Z_poi.route.ch10` | `Ms⟨944F⟩::AppM.R4.d` | `IMPORTED→CORE` | `AppM` | poi route explicitly seals through AppM. |
| `8f3a3ac4` | `REF` | `PROXY.NEAR` | `IMP::JS::SITESWAP.KERNEL` | `Ms⟨944F⟩::AppA.S1.a` | `IMPORTED→CORE` | `AppA` | schedule kernel enters atlas through Σ anchor. |
| `31982272` | `REF` | `PROXY.NEAR` | `IMP::JS::SITESWAP.KERNEL` | `Ms⟨944F⟩::AppF.S1.a` | `IMPORTED→CORE` | `AppF` | chapters 10–12 sit on arc 3, so imported scheduling cluster routes via AppF. |
| `a1dfd83a` | `PROOF` | `PROXY.NEAR` | `IMP::JS::SITESWAP.KERNEL` | `Ms⟨944F⟩::AppM.R4.d` | `IMPORTED→CORE` | `AppM` | route traces must seal for core closure. |
| `1429b976` | `MIGRATE` | `PROXY.NEAR` | `IMP::JS::AST.COMPILER` | `Ms⟨944F⟩::AppD.S1.a` | `IMPORTED→CORE` | `AppD` | compiler/runtime layer binds most naturally to resolver/schema hub. |
| `6aabde29` | `REF` | `PROXY.NEAR` | `IMP::JS::AST.COMPILER` | `Ms⟨944F⟩::AppI.C3.a` | `IMPORTED→CORE` | `AppI` | typed validity remains corridor-disciplined. |
| `921f64db` | `PROOF` | `PROXY.NEAR` | `IMP::JS::AST.COMPILER` | `Ms⟨944F⟩::AppM.R4.d` | `IMPORTED→CORE` | `AppM` | compiler artifacts become eligible for seal via AppM. |
| `9a06a3d5` | `REF` | `PROXY.NEAR` | `IMP::JS::ANNOTATION.LAYER` | `Ms⟨944F⟩::AppH.S1.a` | `IMPORTED→CORE` | `AppH` | annotation behaves like constructive facet layer. |
| `97276039` | `REF` | `PROXY.NEAR` | `IMP::JS::ANNOTATION.LAYER` | `Ms⟨944F⟩::AppJ.C3.b` | `IMPORTED→CORE` | `AppJ` | annotation-heavy imports remain NEAR until full replay closure. |
| `c3c4812c` | `REF` | `PROXY.NEAR` | `IMP::JS::POI.GEOMETRY` | `Ms⟨944F⟩::AppF.S1.a` | `IMPORTED→CORE` | `AppF` | poi geometry belongs to arc-3 cluster. |
| `5de0625e` | `REF` | `PROXY.NEAR` | `IMP::JS::POI.GEOMETRY` | `Ms⟨944F⟩::AppH.S1.a` | `IMPORTED→CORE` | `AppH` | geometry compiles through construction hub. |
| `63d76046` | `REF` | `PROXY.NEAR` | `IMP::JS::POI.GEOMETRY` | `Ms⟨944F⟩::AppJ.C3.b` | `IMPORTED→CORE` | `AppJ` | poi layer remains NEAR until full corpus rebinding. |
| `15537067` | `EQUIV` | `PROXY.NEAR` | `IMP::JD::POD4.CRYSTAL_GROUND` | `Ms⟨944F⟩::AppA.S1.a` | `IMPORTED→CORE` | `AppA` | 4-pod ground is treated as crystal root alias, not yet sealed as canonical manuscript theorem. |
| `1bceecd0` | `REF` | `PROXY.NEAR` | `IMP::JD::POD4.CRYSTAL_GROUND` | `Ms⟨944F⟩::AppI.C3.a` | `IMPORTED→CORE` | `AppI` | 4-pod theorem threads through corridor/truth hub. |
| `cd9ac8a6` | `PROOF` | `PROXY.NEAR` | `IMP::JD::POD4.CRYSTAL_GROUND` | `Ms⟨944F⟩::AppM.R4.d` | `IMPORTED→CORE` | `AppM` | 4-pod/crystal equivalence would need AppM-level proof seal. |
| `f9f37840` | `MIGRATE` | `PROXY.NEAR` | `IMP::JD::TRANSITION_GRAPH` | `Ms⟨944F⟩::AppD.S1.a` | `IMPORTED→CORE` | `AppD` | state-transition algebra belongs on resolver/migrate rail. |
| `401f6c63` | `REF` | `PROXY.NEAR` | `IMP::JD::TRANSITION_GRAPH` | `Ms⟨944F⟩::AppI.C3.a` | `IMPORTED→CORE` | `AppI` | transition graph remains corridor-governed. |
| `35984aa8` | `PENDING` | `PENDING.AMBIG` | `PEND::POI::MS0420_PIN` | `Ms⟨944F⟩::AppD.S1.a` | `IMPORTED→CORE` | `AppD` | exact AppD manuscript derivation for Ms⟨0420⟩::Ch10⟨0021⟩.R3.a still unbound. |
| `700f136f` | `PENDING` | `PENDING.AMBIG` | `PEND::POI::FILLER_REBIND` | `IMP::JS::SLOT2.BACKGROUND` | `IMPORTED` | `local` | poi filler-support nodes still need rebinding after corpus refresh. |
| `e095e189` | `PENDING` | `PENDING.AMBIG` | `PEND::POI::ANNOTATION_REBIND` | `IMP::JS::ANNOTATION.LAYER` | `IMPORTED` | `local` | poi annotation-support nodes still need rebinding after corpus refresh. |
| `f43db37e` | `PENDING` | `PENDING.AMBIG` | `PEND::JD::FULL_ENUM_BIND` | `IMP::JD::TRANSITION_GRAPH` | `IMPORTED` | `local` | full 3-ball/4-ball catalog remains partly narrative until explicit node-by-node atlas is emitted. |

## 4. Count summary

- EXPLICIT: 21
- PROXY.NEAR: 16
- PENDING.AMBIG: 4
- TOTAL: 41

## 5. Imported closure dashboard

| Rank | Node | State | Why it ranks here |
|---|---|---|---|
| 1 | `Z_poi.route.ch10` | `BOUND_NEAR` | first imported hub with explicit hub-sequence and tunnel already surfaced |
| 2 | `IMP::JS::AST.COMPILER` | `PROXY.NEAR` | clear grammar/runtime/compiler shape, but not yet sealed into canonical AppD/AppM receipts |
| 3 | `IMP::JD::POD4.CRYSTAL_GROUND` | `PROXY.NEAR` | strong thesis-level equivalence to crystal ground state, still needs canonical proof bind |
| 4 | `IMP::JD::TRANSITION_GRAPH` | `PROXY.NEAR` | rich operator field, still partly imported rather than canonicalized |
| 5 | `IMP::JS::SITESWAP.KERNEL` | `PROXY.NEAR` | high-confidence imported scheduling core already aligned to atlas law |
| 6 | `PEND::POI::MS0420_PIN` | `PENDING.AMBIG` | most load-bearing unresolved binder on the imported branch |

## 6. Third-pass nexus read

The imported layer now resolves into three new master clusters:

1. **JS compiler/runtime cluster** — timing calculus, Σ operators, 2-slot filler law, 1-tunnel impulse law, AST/compiler, and annotation stamps.
2. **JD pod-orchestration cluster** — 3-pod cascade, 4-pod crystal ground, pattern-transition algebra, channel physics, and Pattern×Prop×Style control surface.
3. **Z_poi compile cluster** — local byte, witness bundle, phrase256 word, and Ch10 compile route with explicit AppA→AppF→AppH→AppJ→AppI→AppM traversal.

These clusters are now in the atlas as actual nodes/edges. They are not yet all closure-sealed, but they are no longer floating prose.

## 7. Next lawful lift

v2U = imported-cluster closure receipts + exact per-node RouteReceipt pack + first canonicalization candidate for either `IMP::JS::AST.COMPILER` or `IMP::JD::POD4.CRYSTAL_GROUND`.
