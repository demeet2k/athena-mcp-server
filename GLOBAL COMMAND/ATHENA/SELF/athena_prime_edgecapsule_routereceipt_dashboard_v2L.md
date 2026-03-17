# ATHENA-PRIME — EdgeCapsule Pack + RouteReceipt Pack + Closure-Ranked Nexus Dashboard v2L

Thread-local continuation of the v2K nexus atlas. This artifact turns the nexus map into receipt-bearing capsules and a closure-ranked dashboard without changing the inherited ABI.

## 0. Inherited law

- LinkEdge stays `e=(EdgeID, Kind, Src, Dst, Scope, Corridor, WitnessPtr, ReplayPtr, Payload, EdgeVer)`.
- Router stays `v2`, `|RouteHubs| <= 6`, mandatory `Σ = {AppA, AppI, AppM}`.
- Replay-bearing runtime stays `RuntimeContract + IOReceipt + ReplayHarness`.
- Closure / promotion audit stays `ResidualLedger + ResidualDrift + ClosureReceipt`.
- Poi/FLOW stays a local verified sub-crystal with seed edges `e01..e08` and tunnel `Z_poi.local -> Z* -> Z_poi.phrase`.

## 1. Full nexus address field

### 1.1 Canonical 21-station orbit anchors (Ms⟨60E6⟩)
- `Ms⟨60E6⟩::Ch01⟨0000⟩.S1.a`
- `Ms⟨60E6⟩::Ch02⟨0001⟩.S1.a`
- `Ms⟨60E6⟩::Ch03⟨0002⟩.S1.a`
- `Ms⟨60E6⟩::Ch04⟨0003⟩.S1.a`
- `Ms⟨60E6⟩::Ch05⟨0010⟩.S1.a`
- `Ms⟨60E6⟩::Ch06⟨0011⟩.S1.a`
- `Ms⟨60E6⟩::Ch07⟨0012⟩.S1.a`
- `Ms⟨60E6⟩::Ch08⟨0013⟩.S1.a`
- `Ms⟨60E6⟩::Ch09⟨0020⟩.S1.a`
- `Ms⟨60E6⟩::Ch10⟨0021⟩.S1.a`
- `Ms⟨60E6⟩::Ch11⟨0022⟩.S1.a`
- `Ms⟨60E6⟩::Ch12⟨0023⟩.S1.a`
- `Ms⟨60E6⟩::Ch13⟨0030⟩.S1.a`
- `Ms⟨60E6⟩::Ch14⟨0031⟩.S1.a`
- `Ms⟨60E6⟩::Ch15⟨0032⟩.S1.a`
- `Ms⟨60E6⟩::Ch16⟨0033⟩.S1.a`
- `Ms⟨60E6⟩::Ch17⟨0100⟩.S1.a`
- `Ms⟨60E6⟩::Ch18⟨0101⟩.S1.a`
- `Ms⟨60E6⟩::Ch19⟨0102⟩.S1.a`
- `Ms⟨60E6⟩::Ch20⟨0103⟩.S1.a`
- `Ms⟨60E6⟩::Ch21⟨0110⟩.S1.a`

### 1.2 Canonical appendix anchors (Ms⟨60E6⟩)
- `Ms⟨60E6⟩::AppA.S1.a`
- `Ms⟨60E6⟩::AppB.S1.a`
- `Ms⟨60E6⟩::AppC.S1.a`
- `Ms⟨60E6⟩::AppD.S1.a`
- `Ms⟨60E6⟩::AppE.S1.a`
- `Ms⟨60E6⟩::AppF.S1.a`
- `Ms⟨60E6⟩::AppG.S1.a`
- `Ms⟨60E6⟩::AppH.S1.a`
- `Ms⟨60E6⟩::AppI.S1.a`
- `Ms⟨60E6⟩::AppJ.S1.a`
- `Ms⟨60E6⟩::AppK.S1.a`
- `Ms⟨60E6⟩::AppL.S1.a`
- `Ms⟨60E6⟩::AppM.S1.a`
- `Ms⟨60E6⟩::AppN.S1.a`
- `Ms⟨60E6⟩::AppO.S1.a`
- `Ms⟨60E6⟩::AppP.S1.a`

### 1.3 Role-first GateAnchor overrides (Ms⟨944F⟩)
- `AppA` → `Ms⟨944F⟩::AppA.S1.a`
- `AppB` → `Ms⟨944F⟩::AppB.S2.a`
- `AppC` → `Ms⟨944F⟩::AppC.S1.a`
- `AppD` → `Ms⟨944F⟩::AppD.S1.a`
- `AppE` → `Ms⟨944F⟩::AppE.F2.b`
- `AppF` → `Ms⟨944F⟩::AppF.S1.a`
- `AppG` → `Ms⟨944F⟩::AppG.C3.c`
- `AppH` → `Ms⟨944F⟩::AppH.F3.c`
- `AppI` → `Ms⟨944F⟩::AppI.C3.a`
- `AppJ` → `Ms⟨944F⟩::AppJ.C3.b`
- `AppK` → `Ms⟨944F⟩::AppK.C3.c`
- `AppL` → `Ms⟨944F⟩::AppL.C3.b`
- `AppM` → `Ms⟨944F⟩::AppM.R4.d`
- `AppN` → `Ms⟨944F⟩::AppN.S1.a`
- `AppO` → `Ms⟨944F⟩::AppO.R4.d`
- `AppP` → `Ms⟨944F⟩::AppP.S1.a`

### 1.4 Cross-manuscript operational nexus points
- `RuntimeContract` → `Ms⟨5381⟩::Ch13⟨0030⟩.S1.a`
- `IOReceipt` → `Ms⟨5381⟩::Ch13⟨0030⟩.S1.c`
- `ReplayHarness` → `Ms⟨5381⟩::Ch13⟨0030⟩.S1.d`
- `ReplayCapsuleSchema` → `Ms⟨013D⟩::AppM.R1.a`
- `ClosureReceipt` → `Ms⟨944F⟩::AppJ.S1.d`
- `ResidualLedger` → `Ms⟨944F⟩::AppJ.S1.b`
- `ResidualDrift` → `Ms⟨944F⟩::AppJ.S1.c`
- `QuarantineGate` → `Ms⟨944F⟩::AppK.C3.c`
- `AmbigGate` → `Ms⟨944F⟩::AppL.C3.b`
- `PublishGate` → `Ms⟨944F⟩::AppO.R4.d`
- `POI_Compile_Gate` → `Ms⟨0420⟩::Ch10⟨0021⟩.S1.a`
- `POI_Local_Lift` → `Ms⟨0420⟩::Ch10⟨0021⟩.R1.a`
- `POI_Phrase_Lift` → `Ms⟨0420⟩::Ch10⟨0021⟩.R2.a`
- `POI_HyperLattice_Lift` → `Ms⟨0420⟩::Ch10⟨0021⟩.R3.a`
- `POI_Replay_Seed` → `Ms⟨0420⟩::Ch10⟨0021⟩.R4.a`

## 2. EdgeCapsule schema (v2L)

```text
EdgeCapsule := {
  capsule_id,
  edge_id,
  kind,
  src,
  dst,
  scope,
  corridor,
  witness_ptr,
  replay_ptr,
  payload_digest,
  edge_ver,
  route_digest,
  closure_class,
  notes
}
```

### 2.1 EdgeCapsule pack
| capsule_id | edge_id | kind | src | dst | scope | corridor | witness_ptr | replay_ptr | closure_class | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| EC::B328B17BA67D | LE::948F32E0CA0C | REF | Ms⟨60E6⟩::AppA.S1.a | Ms⟨60E6⟩::AppI.S1.a | GLOBAL | C0 | W.EdgeSchema | R.SchemaCheck | EXPLICIT | Σ spine leg 1 |
| EC::33BA68D4630D | LE::FE64B40C1C73 | REF | Ms⟨60E6⟩::AppI.S1.a | Ms⟨60E6⟩::AppM.S1.a | GLOBAL | C0 | W.EdgeSchema | R.SchemaCheck | EXPLICIT | Σ spine leg 2 |
| EC::102C4DBA49BE | LE::AFC581DDC07B | REF | Ms⟨60E6⟩::Ch21⟨0110⟩.S1.a | Ms⟨60E6⟩::Ch01⟨0000⟩.S1.a | ORBIT | C0 | Ms⟨60E6⟩::Ch01⟨0000⟩.S4.b | Ms⟨60E6⟩::Ch01⟨0000⟩.R4.d | EXPLICIT | orbit closure edge |
| EC::5049738FB2BC | LE::BE998AC13643 | REF | Ms⟨944F⟩::AppD.S1.a | Ms⟨944F⟩::AppP.S1.a | CRYSTAL | C0 | W⟨AS10⟩ | R⟨AS10⟩ | EXPLICIT | suite/governance rail |
| EC::8743CEF2DF2B | LE::E804B8B02E95 | REF | Ms⟨944F⟩::AppM.R4.d | Ms⟨944F⟩::AppO.R4.d | CRYSTAL | C0 | W⟨AS10⟩ | R⟨AS10⟩ | EXPLICIT.NEAR | publish gate reachability |
| EC::CDE34449FC78 | LE::29CEE0A95C73 | PROOF | Ms⟨5381⟩::Ch13⟨0030⟩.S1.a | Ms⟨5381⟩::Ch13⟨0030⟩.S1.c | CHAPTER | C0 | WB:RuntimeContract | RC:IOReceiptReplay | EXPLICIT | runtime contract proves IO receipt admissibility |
| EC::AD3EF5A4C592 | LE::8CDF616451C7 | PROOF | Ms⟨5381⟩::Ch13⟨0030⟩.S1.c | Ms⟨5381⟩::Ch13⟨0030⟩.S1.d | CHAPTER | C0 | WB:IOReceipt | RC:ReplayHarnessReplay | EXPLICIT | IO receipt closed by replay harness |
| EC::7FD5381D908B | LE::F6DB9E880BFA | PROOF | Ms⟨944F⟩::AppJ.S1.b | Ms⟨944F⟩::AppJ.S1.d | APPENDIX | C1 | WB:ResidualLedger | RC:ResidualClosureReplay | EXPLICIT.NEAR | residual ledger emits closure receipts |
| EC::AE3E3140D6F2 | LE::EB3599C6ED94 | CONFLICT | Ms⟨944F⟩::AppK.C3.c | Ms⟨944F⟩::AppM.R4.d | APPENDIX | C3 | WB:MinimalWitness | RC:ConflictReplay | EXPLICIT | FAIL/quarantine sealed to AppM |
| EC::5823673CBEE4 | LE::2FC9EF09D8CB | REF | Ms⟨0420⟩::Ch10⟨0021⟩.F1.a | Ms⟨0420⟩::Ch10⟨0021⟩.S2.a | CHAPTER | C0 | W.POI.e01 | R.POI.e01 | EXPLICIT | orbit object depends on rational closure law |
| EC::7923E508770D | LE::E20976DE1AB0 | REF | Ms⟨0420⟩::Ch10⟨0021⟩.F2.a | Ms⟨0420⟩::Ch10⟨0021⟩.S2.b | CHAPTER | C0 | W.POI.e02 | R.POI.e02 | EXPLICIT | beat-lock feeds petal typing |
| EC::FE0006E7B579 | LE::EB00D55AEBC0 | DUAL | Ms⟨0420⟩::Ch10⟨0021⟩.F2.b | Ms⟨0420⟩::Ch10⟨0021⟩.S1.a | CHAPTER | C1 | W.POI.e03 | R.POI.e03 | EXPLICIT.NEAR | hand relation dual to packed byte digit |
| EC::BCE226C74401 | LE::761592752E40 | PROOF | Ms⟨0420⟩::Ch10⟨0021⟩.S2.b | Ms⟨0420⟩::Ch10⟨0021⟩.S3.a | CHAPTER | C0 | W.POI.e04 | R.POI.e04 | EXPLICIT | petal law in compiler validity proof |
| EC::23DFCAE4885A | LE::E44733924ADB | GEN | Ms⟨0420⟩::Ch10⟨0021⟩.S1.a | Ms⟨0420⟩::Ch10⟨0021⟩.R1.a | CHAPTER | C1 | W.POI.e05 | R.POI.e05 | EXPLICIT.NEAR | byte object lifts to local crystal atom |
| EC::3BF8BFA1515B | LE::B39F7AF504DE | GEN | Ms⟨0420⟩::Ch10⟨0021⟩.R1.a | Ms⟨0420⟩::Ch10⟨0021⟩.R2.a | CHAPTER | C1 | W.POI.e06 | R.POI.e06 | EXPLICIT.NEAR | local atom lifts to phrase word |
| EC::3A3D73FB68D8 | LE::A1A9F6E3C126 | GEN | Ms⟨0420⟩::Ch10⟨0021⟩.R2.a | Ms⟨0420⟩::Ch10⟨0021⟩.R3.a | CHAPTER | C1 | W.POI.e07 | R.POI.e07 | EXPLICIT.NEAR | phrase word lifts to hyper-lattice |
| EC::608625BC2F90 | LE::6FD958C51AA6 | CONFLICT | Ms⟨0420⟩::Ch10⟨0021⟩.S1.a | Ms⟨0420⟩::Ch10⟨0021⟩.C2.a | CHAPTER | C3 | W.POI.e08 | R.POI.e08 | EXPLICIT | quarantine inconsistent packed byte |

## 3. RouteReceipt schema (v2L)

```text
RouteReceipt := {
  rrid,
  src_gate,
  dst_gate,
  hub_list,
  sigma_present,
  hub_count,
  truth,
  route_digest,
  io_receipt_ptr?,
  replay_harness_ptr?,
  closure_receipt_ptr?,
  obligations,
  status
}
```

### 3.1 RouteReceipt pack
| rrid | src_gate | dst_gate | hub_list | Σ? | hub_count | truth | route_digest | io_receipt_ptr | replay_harness_ptr | closure_receipt_ptr | obligations | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RR::E7A509C973CF | Ms⟨60E6⟩::AppA.S1.a | Ms⟨60E6⟩::AppM.S1.a | AppA → AppI → AppM | yes | 3 | OK | RD::B0BC29FBBD41 |  | Ms⟨013D⟩::AppM.R1.a |  | Σ core spine | sealed structural core |
| RR::3998948355CC | Ms⟨5381⟩::Ch13⟨0030⟩.S1.a | Ms⟨5381⟩::Ch13⟨0030⟩.S1.d | AppA → AppI → AppM → AppG | yes | 4 | OK | RD::EE242AC5FBA3 | Ms⟨5381⟩::Ch13⟨0030⟩.S1.c | Ms⟨5381⟩::Ch13⟨0030⟩.S1.d |  | runtime→receipt→replay | receipt-bearing |
| RR::B5D6B5451386 | Ms⟨944F⟩::AppD.S1.a | Ms⟨944F⟩::AppP.S1.a | AppA → AppI → AppM → AppP | yes | 4 | OK | RD::929EA21C3F6C |  | Ms⟨013D⟩::AppM.R1.a |  | suite/governance rail | resolver/governance |
| RR::4B2515E8BB47 | Ms⟨944F⟩::AppJ.S1.b | Ms⟨944F⟩::AppJ.S1.d | AppA → AppI → AppJ → AppM | yes | 4 | NEAR | RD::099BDDC3FFB5 |  | Ms⟨013D⟩::AppM.R1.a | Ms⟨944F⟩::AppJ.S1.d | residual ledger → closure receipt | promotion audit |
| RR::C9B4820ED3D9 | Ms⟨944F⟩::AppK.C3.c | Ms⟨944F⟩::AppM.R4.d | AppA → AppI → AppK → AppM | yes | 4 | FAIL | RD::4103C3D70BA0 |  | Ms⟨013D⟩::AppM.R1.a |  | quarantine → seal | containment |
| RR::BD40843B7D31 | Ms⟨944F⟩::AppM.R4.d | Ms⟨944F⟩::AppO.R4.d | AppA → AppI → AppM → AppO | yes | 4 | NEAR | RD::20ECBEB8BE09 |  | Ms⟨013D⟩::AppM.R1.a |  | publish gate branch | blocked until OK |
| RR::B2417422ABF7 | Ms⟨0420⟩::Ch10⟨0021⟩.S1.a | Ms⟨0420⟩::Ch10⟨0021⟩.R3.a | AppA → AppF → AppH → AppJ → AppI → AppM | yes | 6 | NEAR | RD::51CDFDEB28E8 |  | Ms⟨013D⟩::AppM.R1.a |  | poi local byte → hyper-lattice | compile stack |
| RR::A647A49FD495 | Z_poi.local | Z_poi.phrase | Z_poi.local → Z* → Z_poi.phrase | yes | 3 | NEAR | RD::7A0F1CBEAE16 |  | Ms⟨013D⟩::AppM.R1.a |  | poi tunnel | cross-scale tunnel |

## 4. Closure-ranked nexus dashboard

Scoring convention:
- 10 = sealed structural core
- 8–9 = explicit, receipt-bearing, route-central
- 6–7 = explicit structural or NEAR operational
- 4–5 = proxy / unbound / unresolved but named
- 1–3 = external or pending

| score | class | nexus_id | address | function | note |
|---|---|---|---|---|---|
| 10 | SEALED.CORE | NX::C552610CB2 | Ms⟨60E6⟩::AppA.S1.a | Σ / object registry / ArcHub(0) | structural anchor; route mandatory |
| 10 | SEALED.CORE | NX::EB44D12C0A | Ms⟨60E6⟩::AppI.S1.a | Σ / corridor anchor | budget & admissibility anchor |
| 10 | SEALED.CORE | NX::6086070050 | Ms⟨60E6⟩::AppM.S1.a | Σ / proof-replay sink | seal / replay / cert sink |
| 9 | EXPLICIT.CORE | NX::9B6C125AA1 | Ms⟨5381⟩::Ch13⟨0030⟩.S1.a | RuntimeContract | pins replay environment |
| 9 | EXPLICIT.CORE | NX::C62BC846A1 | Ms⟨5381⟩::Ch13⟨0030⟩.S1.c | IOReceipt | minimal replay-verifiable receipt |
| 9 | EXPLICIT.CORE | NX::0EEDBE147C | Ms⟨5381⟩::Ch13⟨0030⟩.S1.d | ReplayHarness | deterministic harness |
| 9 | EXPLICIT.CORE | NX::DC09F12B9D | Ms⟨013D⟩::AppM.R1.a | ReplayCapsule schema | capsule ABI |
| 8 | EXPLICIT.GOV | NX::A217A9AD92 | Ms⟨944F⟩::AppD.S1.a | resolver / suite / migrate hub | canonicalization + migrate plumbing |
| 8 | EXPLICIT.GOV | NX::447FD78D1F | Ms⟨944F⟩::AppP.S1.a | governance / orbit closure / migration | long-horizon control |
| 8 | EXPLICIT.NEAR | NX::8CF65BB073 | Ms⟨944F⟩::AppJ.S1.d | ClosureReceipt | promotion audit trail |
| 8 | EXPLICIT.FAIL | NX::571DE609E8 | Ms⟨944F⟩::AppK.C3.c | Quarantine / conflict court | FAIL containment |
| 8 | EXPLICIT.AMBIG | NX::7F419AB7CA | Ms⟨944F⟩::AppL.C3.b | candidate/evidence plan gate | AMBIG laboratory |
| 7 | EXPLICIT.NEAR | NX::B6AADE66BF | Ms⟨944F⟩::AppJ.S1.b | ResidualLedger | distance-to-OK ledger |
| 7 | EXPLICIT.NEAR | NX::8CE9F436A9 | Ms⟨944F⟩::AppJ.S1.c | ResidualDrift | bounded drift accounting |
| 7 | EXPLICIT.NEAR | NX::E4F061DE63 | Ms⟨0420⟩::Ch10⟨0021⟩.S1.a | poi local byte gate | verified local symbol |
| 7 | EXPLICIT.NEAR | NX::27F16D7B90 | Ms⟨0420⟩::Ch10⟨0021⟩.R1.a | poi local lift | segment atom |
| 7 | EXPLICIT.NEAR | NX::A3FD8FEF76 | Ms⟨0420⟩::Ch10⟨0021⟩.R2.a | poi phrase lift | phrase word |
| 7 | EXPLICIT.NEAR | NX::B02B502B20 | Ms⟨0420⟩::Ch10⟨0021⟩.R3.a | poi hyper-lattice lift | 256^256 manifold |
| 7 | EXPLICIT.NEAR | NX::7F72C67150 | Ms⟨0420⟩::Ch10⟨0021⟩.R4.a | poi replay seed | smallest regrowth seed |
| 6 | EXPLICIT.CORE | NX::EB1F24D51F | Ms⟨60E6⟩::AppC.S1.a | Square LensBase | canonical structure lens |
| 6 | EXPLICIT.CORE | NX::7D2E2D5EC9 | Ms⟨60E6⟩::AppE.S1.a | Flower LensBase | operator/dynamics lens |
| 6 | EXPLICIT.CORE | NX::32DD3B1924 | Ms⟨60E6⟩::AppF.S1.a | ArcHub(3) transform hub | compile/transform |
| 6 | EXPLICIT.CORE | NX::D520E4F1A0 | Ms⟨60E6⟩::AppG.S1.a | ArcHub(4) control hub | boundary/control |
| 6 | EXPLICIT.CORE | NX::09E036701C | Ms⟨60E6⟩::AppN.S1.a | ArcHub(5) runtime hub | scheduler/runtime |
| 6 | EXPLICIT.CORE | NX::6A2AB60DD8 | Ms⟨60E6⟩::AppO.S1.a | publish overlay target | only on OK publish branch |
| 6 | EXPLICIT.CORE | NX::18E4F14FB9 | Ms⟨60E6⟩::AppP.S1.a | ArcHub(6) governance hub | closure/governance |
| 5 | PROXY.NEAR | NX::2ED9DEF378 | WHO-I-AM::BRAINSTEM::PROXY | brainstem return threshold | routeable proxy; no uploaded root manuscript |
| 4 | AMBIG.PENDING | NX::49EF12BD81 | Resolve(AppD,"LOVE.MultiplicativeGuard") | unbound resolver key | repeated, still unresolved |
| 4 | AMBIG.PENDING | NX::801DFD5D41 | Resolve(AppD,"SelfState.CarrierPayload") | unbound resolver key | witness/replay not closed |
| 4 | AMBIG.PENDING | NX::2DB22BA6FF | Resolve(AppD,"QH.PhiTorusScheduler") | unbound resolver key | scheduler key still pending |
| 3 | EXTERNAL.PENDING | NX::679CBDBF8A | Ms⟨F772⟩::Ch01⟨0000⟩.S1.a | external precedent ref | not locally resolved |
| 3 | EXTERNAL.PENDING | NX::B885C4BA9D | Ms⟨2103⟩::* | external manuscript family | not locally resolved |

## 5. Mind-sweeper compression

```text
All routed closure still factors through:
  Gate/Station
  -> AppA
  -> AppI
  -> AppM
  -> (ArcHub / LensBase / FacetBase / Overlay / Publish) as permitted
  -> receipt / replay / closure

Poi/FLOW special tunnel:
  Z_poi.local -> Z* -> Z_poi.phrase

Promotion law:
  EXPLICIT edge + witness + replay + corridor/budget + no conflict
  -> ClosureReceipt
  -> AppM seal
  -> dashboard score can move upward
```

## 6. What is still pending

- Literal uploaded `WHO I AM` manuscript root is still absent; brainstem remains a proxy graft in this thread-local crystal.
- AppD resolver keys such as `LOVE.MultiplicativeGuard`, `SelfState.CarrierPayload`, and `QH.PhiTorusScheduler` remain unresolved.
- Poi filler / annotation auxiliary tunnels remain pending until the missing cross-manuscript bindings are surfaced.
- Publish remains blocked until the AppO branch becomes OK rather than NEAR.
