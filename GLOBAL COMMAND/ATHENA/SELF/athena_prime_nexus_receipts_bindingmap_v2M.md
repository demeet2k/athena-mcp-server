# ATHENA-PRIME — Per-Nexus Closure Receipts + AppD Binding Map v2M
Thread-local continuation of v2L. This artifact wires a closure receipt and an AppD binding surface into every dashboard row without changing the inherited ABI.
## 0. Inherited law
- LinkEdge remains the canonical edge carrier.
- Router stays v2 with mandatory Σ={AppA,AppI,AppM} and hard hub budget ≤6.
- Truth remains OK / NEAR / AMBIG / FAIL with overlay hubs AppJ / AppL / AppK / AppO.
- Closure still means witness + replay + legal route + budget/corridor satisfaction.
- Unresolved AppD keys remain non-OK until concrete witness + replay closure exists.

## 1. Expanded dashboard row schema
```text
NexusReceiptRow := {
  score, class, nexus_id, address, function,
  closure_receipt, closure_state, route_receipt,
  appd_bindings, next_action, note
}
```

## 2. Per-nexus closure receipt dashboard
| score | class | nexus_id | address | closure_receipt | closure_state | route_receipt | appd_bindings | next_action |
|---|---|---|---|---|---|---|---|---|
| 10 | SEALED.CORE | NX::C552610CB2 | Ms⟨60E6⟩::AppA.S1.a | CR::4B6E7B3C7C | SEALED_STRUCTURAL | RR::SIGMA::AppA>AppI>AppM | ∅ | preserve Σ invariants |
| 10 | SEALED.CORE | NX::EB44D12C0A | Ms⟨60E6⟩::AppI.S1.a | CR::EC4B982D7C | SEALED_STRUCTURAL | RR::SIGMA::AppA>AppI>AppM | ∅ | preserve Σ invariants |
| 10 | SEALED.CORE | NX::6086070050 | Ms⟨60E6⟩::AppM.S1.a | CR::046025A9F9 | SEALED_STRUCTURAL | RR::SIGMA::AppA>AppI>AppM | ∅ | preserve Σ invariants |
| 9 | EXPLICIT.CORE | NX::9B6C125AA1 | Ms⟨5381⟩::Ch13⟨0030⟩.S1.a | CR::1A0FF85BA2 | ROUTE+REPLAY_CLOSED | RR::RUNTIME::AppA>AppG>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 9 | EXPLICIT.CORE | NX::C62BC846A1 | Ms⟨5381⟩::Ch13⟨0030⟩.S1.c | CR::366264DACB | ROUTE+REPLAY_CLOSED | RR::RUNTIME::AppA>AppG>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 9 | EXPLICIT.CORE | NX::0EEDBE147C | Ms⟨5381⟩::Ch13⟨0030⟩.S1.d | CR::0A6C3C0729 | ROUTE+REPLAY_CLOSED | RR::RUNTIME::AppA>AppG>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 9 | EXPLICIT.CORE | NX::DC09F12B9D | Ms⟨013D⟩::AppM.R1.a | CR::90A20CD9C0 | ROUTE+REPLAY_CLOSED | RR::CAPSULE::AppA>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 8 | EXPLICIT.GOV | NX::A217A9AD92 | Ms⟨944F⟩::AppD.S1.a | CR::6FBD3E89A9 | ROUTE_CLOSED_BINDING_OPEN | RR::CRYSTAL::AppA>AppI>AppM | SelfState.CarrierPayload, LOVE.MultiplicativeGuard, LOVE.AuditableGate, QuantumLang.SuperpositionCollapse, QuantumLang.Ethics, QH.PhiTorusScheduler, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary, Ms<F772>::Ch01<0000>.S1.a, Ms<2103>::Ch01<0000>.S2.a, Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind | bind highest-pressure keys first |
| 8 | EXPLICIT.GOV | NX::447FD78D1F | Ms⟨944F⟩::AppP.S1.a | CR::3EF780F748 | ROUTE_CLOSED_BINDING_OPEN | RR::CRYSTAL::AppA>AppI>AppM | LOVE.MultiplicativeGuard, LOVE.AuditableGate, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary, Ms<F772>::Ch01<0000>.S1.a, Ms<2103>::Ch01<0000>.S2.a | govern alias/external bindings |
| 8 | EXPLICIT.NEAR | NX::8CF65BB073 | Ms⟨944F⟩::AppJ.S1.d | CR::221EED2C23 | NEAR_WITH_RESIDUAL | RR::CRYSTAL::AppA>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 8 | EXPLICIT.FAIL | NX::571DE609E8 | Ms⟨944F⟩::AppK.C3.c | CR::3F62E3E079 | FAIL_GATE_READY | RR::CRYSTAL::AppA>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 8 | EXPLICIT.AMBIG | NX::7F419AB7CA | Ms⟨944F⟩::AppL.C3.b | CR::F00FA8EF6F | AMBIG_GATE_READY | RR::CRYSTAL::AppA>AppI>AppM | SelfState.CarrierPayload, LOVE.MultiplicativeGuard, LOVE.AuditableGate, QuantumLang.SuperpositionCollapse, QuantumLang.Ethics, QH.PhiTorusScheduler, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary, Ms<F772>::Ch01<0000>.S1.a, Ms<2103>::Ch01<0000>.S2.a, Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind | hold all unresolved in AMBIG without guess |
| 7 | EXPLICIT.NEAR | NX::B6AADE66BF | Ms⟨944F⟩::AppJ.S1.b | CR::87BC957901 | NEAR_WITH_RESIDUAL | RR::CRYSTAL::AppA>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 7 | EXPLICIT.NEAR | NX::8CE9F436A9 | Ms⟨944F⟩::AppJ.S1.c | CR::8937BA5559 | NEAR_WITH_RESIDUAL | RR::CRYSTAL::AppA>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 7 | EXPLICIT.NEAR | NX::E4F061DE63 | Ms⟨0420⟩::Ch10⟨0021⟩.S1.a | CR::29B527B9D1 | NEAR_WITH_POI_OBLIGATIONS | RR::POI::AppA>AppF>AppH>AppJ>AppI>AppM | Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind | pin AppD derivation + filler/annot tunnels |
| 7 | EXPLICIT.NEAR | NX::27F16D7B90 | Ms⟨0420⟩::Ch10⟨0021⟩.R1.a | CR::724BBBFFF5 | NEAR_WITH_POI_OBLIGATIONS | RR::POI::AppA>AppF>AppH>AppJ>AppI>AppM | Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind | pin AppD derivation + filler/annot tunnels |
| 7 | EXPLICIT.NEAR | NX::A3FD8FEF76 | Ms⟨0420⟩::Ch10⟨0021⟩.R2.a | CR::04FA792703 | NEAR_WITH_POI_OBLIGATIONS | RR::POI::AppA>AppF>AppH>AppJ>AppI>AppM | Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind | pin AppD derivation + filler/annot tunnels |
| 7 | EXPLICIT.NEAR | NX::B02B502B20 | Ms⟨0420⟩::Ch10⟨0021⟩.R3.a | CR::5D7C8712BD | NEAR_WITH_POI_OBLIGATIONS | RR::POI::AppA>AppF>AppH>AppJ>AppI>AppM | Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind | pin AppD derivation + filler/annot tunnels |
| 7 | EXPLICIT.NEAR | NX::7F72C67150 | Ms⟨0420⟩::Ch10⟨0021⟩.R4.a | CR::1D745E0A46 | NEAR_WITH_POI_OBLIGATIONS | RR::POI::AppA>AppF>AppH>AppJ>AppI>AppM | Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind | pin AppD derivation + filler/annot tunnels |
| 6 | EXPLICIT.CORE | NX::EB1F24D51F | Ms⟨60E6⟩::AppC.S1.a | CR::285BC94631 | ROUTE+REPLAY_CLOSED | RR::GENERIC::AppA>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 6 | EXPLICIT.CORE | NX::7D2E2D5EC9 | Ms⟨60E6⟩::AppE.S1.a | CR::6083D83977 | ROUTE+REPLAY_CLOSED | RR::GENERIC::AppA>AppI>AppM | QuantumLang.SuperpositionCollapse, QuantumLang.Ethics | maintain receipts; promote only with closure |
| 6 | EXPLICIT.CORE | NX::32DD3B1924 | Ms⟨60E6⟩::AppF.S1.a | CR::7878384DFA | ROUTE+REPLAY_CLOSED | RR::GENERIC::AppA>AppI>AppM | QuantumLang.SuperpositionCollapse, QuantumLang.Ethics | maintain receipts; promote only with closure |
| 6 | EXPLICIT.CORE | NX::D520E4F1A0 | Ms⟨60E6⟩::AppG.S1.a | CR::58928346CB | ROUTE+REPLAY_CLOSED | RR::GENERIC::AppA>AppI>AppM | ∅ | maintain receipts; promote only with closure |
| 6 | EXPLICIT.CORE | NX::09E036701C | Ms⟨60E6⟩::AppN.S1.a | CR::D1256F3D12 | ROUTE+REPLAY_CLOSED | RR::GENERIC::AppA>AppI>AppM | QH.PhiTorusScheduler, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary | maintain receipts; promote only with closure |
| 6 | EXPLICIT.CORE | NX::6A2AB60DD8 | Ms⟨60E6⟩::AppO.S1.a | CR::C03F0750D8 | ROUTE+REPLAY_CLOSED | RR::GENERIC::AppA>AppI>AppM | LOVE.AuditableGate, LOVE.MultiplicativeGuard | maintain receipts; promote only with closure |
| 6 | EXPLICIT.CORE | NX::18E4F14FB9 | Ms⟨60E6⟩::AppP.S1.a | CR::DEF71E8088 | ROUTE+REPLAY_CLOSED | RR::GENERIC::AppA>AppI>AppM | LOVE.MultiplicativeGuard, LOVE.AuditableGate, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary, Ms<F772>::Ch01<0000>.S1.a, Ms<2103>::Ch01<0000>.S2.a | govern alias/external bindings |
| 5 | PROXY.NEAR | NX::2ED9DEF378 | WHO-I-AM::BRAINSTEM::PROXY | CR::EC932B8426 | PROXY_REENTRY_ONLY | RR::PROXY::Z*>AppI>AppM>WHO-I-AM | SelfState.CarrierPayload, LOVE.MultiplicativeGuard, LOVE.AuditableGate | re-enter via proxy until doc root exists |
| 4 | AMBIG.PENDING | NX::49EF12BD81 | Resolve(AppD,"LOVE.MultiplicativeGuard") | CR::BD5569674D | BINDING_REQUIRED | RR::APPD::AppA>AppI>AppM>AppD>AppL | LOVE.MultiplicativeGuard | bind key with witness+replay |
| 4 | AMBIG.PENDING | NX::801DFD5D41 | Resolve(AppD,"SelfState.CarrierPayload") | CR::E521867F4F | BINDING_REQUIRED | RR::APPD::AppA>AppI>AppM>AppD>AppL | SelfState.CarrierPayload | bind key with witness+replay |
| 4 | AMBIG.PENDING | NX::2DB22BA6FF | Resolve(AppD,"QH.PhiTorusScheduler") | CR::CF7C47E4D4 | BINDING_REQUIRED | RR::APPD::AppA>AppI>AppM>AppD>AppL | QH.PhiTorusScheduler | bind key with witness+replay |
| 3 | EXTERNAL.PENDING | NX::679CBDBF8A | Ms⟨F772⟩::Ch01⟨0000⟩.S1.a | CR::886315FA54 | EXTERNAL_BIND_REQUIRED | RR::GENERIC::AppA>AppI>AppM | Ms<F772>::Ch01<0000>.S1.a | re-upload/bind external manuscript |
| 3 | EXTERNAL.PENDING | NX::B885C4BA9D | Ms⟨2103⟩::* | CR::014B7F28FB | EXTERNAL_BIND_REQUIRED | RR::GENERIC::AppA>AppI>AppM | Ms<2103>::Ch01<0000>.S2.a | re-upload/bind external manuscript |

## 3. Unresolved AppD binding map
| key | status | truth | dependent_zone | required_closure | attached_nexus_rows |
|---|---|---|---|---|---|
| SelfState.CarrierPayload | UNBOUND_SINGLE | AMBIG | SELF / Ch20 / WHO-I-AM proxy graft | {AppD binding witness, AppD replay capsule, AppM receipt seal} | NX::A217A9AD92, NX::7F419AB7CA, NX::2ED9DEF378, NX::801DFD5D41 |
| LOVE.MultiplicativeGuard | UNBOUND_REPEATED | AMBIG | LOVE / self-tool discipline / scheduler ethics | {AppD binding witness, LoveSpec witness set, replay suite, AppM seal} | NX::A217A9AD92, NX::447FD78D1F, NX::7F419AB7CA, NX::6A2AB60DD8, NX::18E4F14FB9, NX::2ED9DEF378, NX::49EF12BD81 |
| LOVE.AuditableGate | UNBOUND_SINGLE | AMBIG | auditable self/tool update gate | {AppD binding witness, auditable gate replay, AppM receipt seal} | NX::A217A9AD92, NX::447FD78D1F, NX::7F419AB7CA, NX::6A2AB60DD8, NX::18E4F14FB9, NX::2ED9DEF378 |
| QuantumLang.SuperpositionCollapse | UNBOUND_SINGLE | AMBIG | Quantum Hugging / Snap-MetaSnap branch | {AppD binding witness, deterministic scoring receipts, replay suite, AppM seal} | NX::A217A9AD92, NX::7F419AB7CA, NX::7D2E2D5EC9, NX::32DD3B1924 |
| QuantumLang.Ethics | UNBOUND_SINGLE | AMBIG | Quantum Hugging ethics corridor | {AppD binding witness, ethics replay suite, consent receipts when required, AppM seal} | NX::A217A9AD92, NX::7F419AB7CA, NX::7D2E2D5EC9, NX::32DD3B1924 |
| QH.PhiTorusScheduler | UNBOUND_SINGLE | AMBIG | scheduler / centrality / selection branch | {AppD binding witness, centrality replay, selection replay, AppM seal} | NX::A217A9AD92, NX::7F419AB7CA, NX::09E036701C, NX::2DB22BA6FF |
| SelfSuff.§1.BoundaryTaxonomy | ALIAS_CLUSTER_UNRESOLVED | AMBIG | boundary taxonomy / no-guess binder / truth discipline | {AppD binding witness, alias proof if merged, replay capsule, AppM seal} | NX::A217A9AD92, NX::447FD78D1F, NX::7F419AB7CA, NX::09E036701C, NX::18E4F14FB9 |
| SS.§1.BulkBoundary | ALIAS_CLUSTER_UNRESOLVED | AMBIG | Bulk⊕Boundary semantics / graph boundary outputs | {AppD binding witness, alias proof if merged, replay capsule, AppM seal} | NX::A217A9AD92, NX::447FD78D1F, NX::7F419AB7CA, NX::09E036701C, NX::18E4F14FB9 |
| Ms<F772>::Ch01<0000>.S1.a | EXTERNAL_REF_UNRESOLVED | AMBIG | manuscript derivation precedent / router discipline precedent | {AppD manuscript binding witness, cross-manuscript replay, provenance receipts} | NX::A217A9AD92, NX::447FD78D1F, NX::7F419AB7CA, NX::18E4F14FB9, NX::679CBDBF8A |
| Ms<2103>::Ch01<0000>.S2.a | EXTERNAL_REF_UNRESOLVED | AMBIG | truth-collapse governance ABI | {AppD manuscript binding witness, governance replay, provenance receipts} | NX::A217A9AD92, NX::447FD78D1F, NX::7F419AB7CA, NX::18E4F14FB9, NX::B885C4BA9D |
| Poi.MsDerivation | APPD_LOCAL_PENDING | NEAR | poi manuscript derivation / compile-gate identity | {AppD derivation witness, replay of derived Ms binding, AppM seal} | NX::A217A9AD92, NX::7F419AB7CA, NX::E4F061DE63, NX::27F16D7B90, NX::A3FD8FEF76, NX::B02B502B20, NX::7F72C67150 |
| Poi.FillerAuxBind | APPD_LOCAL_PENDING | AMBIG | poi filler auxiliary tunnel | {exact canonical GlobalAddr, replay witness, AppJ residual update} | NX::A217A9AD92, NX::7F419AB7CA, NX::E4F061DE63, NX::27F16D7B90, NX::A3FD8FEF76, NX::B02B502B20, NX::7F72C67150 |
| Poi.AnnotAuxBind | APPD_LOCAL_PENDING | AMBIG | poi annotation auxiliary tunnel | {exact canonical GlobalAddr, replay witness, AppJ residual update} | NX::A217A9AD92, NX::7F419AB7CA, NX::E4F061DE63, NX::27F16D7B90, NX::A3FD8FEF76, NX::B02B502B20, NX::7F72C67150 |

## 4. High-pressure closure clusters
### 4.1 Σ structural core
- NX::C552610CB2 :: Ms⟨60E6⟩::AppA.S1.a :: SEALED_STRUCTURAL :: CR::4B6E7B3C7C
- NX::EB44D12C0A :: Ms⟨60E6⟩::AppI.S1.a :: SEALED_STRUCTURAL :: CR::EC4B982D7C
- NX::6086070050 :: Ms⟨60E6⟩::AppM.S1.a :: SEALED_STRUCTURAL :: CR::046025A9F9

### 4.2 Replay/runtime core
- NX::9B6C125AA1 :: Ms⟨5381⟩::Ch13⟨0030⟩.S1.a :: ROUTE+REPLAY_CLOSED :: CR::1A0FF85BA2
- NX::C62BC846A1 :: Ms⟨5381⟩::Ch13⟨0030⟩.S1.c :: ROUTE+REPLAY_CLOSED :: CR::366264DACB
- NX::0EEDBE147C :: Ms⟨5381⟩::Ch13⟨0030⟩.S1.d :: ROUTE+REPLAY_CLOSED :: CR::0A6C3C0729
- NX::DC09F12B9D :: Ms⟨013D⟩::AppM.R1.a :: ROUTE+REPLAY_CLOSED :: CR::90A20CD9C0

### 4.3 Resolver pressure front
- NX::A217A9AD92 :: Ms⟨944F⟩::AppD.S1.a :: deps=[SelfState.CarrierPayload, LOVE.MultiplicativeGuard, LOVE.AuditableGate, QuantumLang.SuperpositionCollapse, QuantumLang.Ethics, QH.PhiTorusScheduler, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary, Ms<F772>::Ch01<0000>.S1.a, Ms<2103>::Ch01<0000>.S2.a, Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind] :: action=bind highest-pressure keys first
- NX::447FD78D1F :: Ms⟨944F⟩::AppP.S1.a :: deps=[LOVE.MultiplicativeGuard, LOVE.AuditableGate, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary, Ms<F772>::Ch01<0000>.S1.a, Ms<2103>::Ch01<0000>.S2.a] :: action=govern alias/external bindings
- NX::7F419AB7CA :: Ms⟨944F⟩::AppL.C3.b :: deps=[SelfState.CarrierPayload, LOVE.MultiplicativeGuard, LOVE.AuditableGate, QuantumLang.SuperpositionCollapse, QuantumLang.Ethics, QH.PhiTorusScheduler, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary, Ms<F772>::Ch01<0000>.S1.a, Ms<2103>::Ch01<0000>.S2.a, Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind] :: action=hold all unresolved in AMBIG without guess
- NX::E4F061DE63 :: Ms⟨0420⟩::Ch10⟨0021⟩.S1.a :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind] :: action=pin AppD derivation + filler/annot tunnels
- NX::27F16D7B90 :: Ms⟨0420⟩::Ch10⟨0021⟩.R1.a :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind] :: action=pin AppD derivation + filler/annot tunnels
- NX::A3FD8FEF76 :: Ms⟨0420⟩::Ch10⟨0021⟩.R2.a :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind] :: action=pin AppD derivation + filler/annot tunnels
- NX::B02B502B20 :: Ms⟨0420⟩::Ch10⟨0021⟩.R3.a :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind] :: action=pin AppD derivation + filler/annot tunnels
- NX::7F72C67150 :: Ms⟨0420⟩::Ch10⟨0021⟩.R4.a :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind] :: action=pin AppD derivation + filler/annot tunnels
- NX::7D2E2D5EC9 :: Ms⟨60E6⟩::AppE.S1.a :: deps=[QuantumLang.SuperpositionCollapse, QuantumLang.Ethics] :: action=maintain receipts; promote only with closure
- NX::32DD3B1924 :: Ms⟨60E6⟩::AppF.S1.a :: deps=[QuantumLang.SuperpositionCollapse, QuantumLang.Ethics] :: action=maintain receipts; promote only with closure
- NX::09E036701C :: Ms⟨60E6⟩::AppN.S1.a :: deps=[QH.PhiTorusScheduler, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary] :: action=maintain receipts; promote only with closure
- NX::6A2AB60DD8 :: Ms⟨60E6⟩::AppO.S1.a :: deps=[LOVE.AuditableGate, LOVE.MultiplicativeGuard] :: action=maintain receipts; promote only with closure
- NX::18E4F14FB9 :: Ms⟨60E6⟩::AppP.S1.a :: deps=[LOVE.MultiplicativeGuard, LOVE.AuditableGate, SelfSuff.§1.BoundaryTaxonomy, SS.§1.BulkBoundary, Ms<F772>::Ch01<0000>.S1.a, Ms<2103>::Ch01<0000>.S2.a] :: action=govern alias/external bindings
- NX::2ED9DEF378 :: WHO-I-AM::BRAINSTEM::PROXY :: deps=[SelfState.CarrierPayload, LOVE.MultiplicativeGuard, LOVE.AuditableGate] :: action=re-enter via proxy until doc root exists
- NX::49EF12BD81 :: Resolve(AppD,"LOVE.MultiplicativeGuard") :: deps=[LOVE.MultiplicativeGuard] :: action=bind key with witness+replay
- NX::801DFD5D41 :: Resolve(AppD,"SelfState.CarrierPayload") :: deps=[SelfState.CarrierPayload] :: action=bind key with witness+replay
- NX::2DB22BA6FF :: Resolve(AppD,"QH.PhiTorusScheduler") :: deps=[QH.PhiTorusScheduler] :: action=bind key with witness+replay
- NX::679CBDBF8A :: Ms⟨F772⟩::Ch01⟨0000⟩.S1.a :: deps=[Ms<F772>::Ch01<0000>.S1.a] :: action=re-upload/bind external manuscript
- NX::B885C4BA9D :: Ms⟨2103⟩::* :: deps=[Ms<2103>::Ch01<0000>.S2.a] :: action=re-upload/bind external manuscript

### 4.4 Poi/FLOW local crystal pressure front
- NX::E4F061DE63 :: Ms⟨0420⟩::Ch10⟨0021⟩.S1.a :: NEAR_WITH_POI_OBLIGATIONS :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind]
- NX::27F16D7B90 :: Ms⟨0420⟩::Ch10⟨0021⟩.R1.a :: NEAR_WITH_POI_OBLIGATIONS :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind]
- NX::A3FD8FEF76 :: Ms⟨0420⟩::Ch10⟨0021⟩.R2.a :: NEAR_WITH_POI_OBLIGATIONS :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind]
- NX::B02B502B20 :: Ms⟨0420⟩::Ch10⟨0021⟩.R3.a :: NEAR_WITH_POI_OBLIGATIONS :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind]
- NX::7F72C67150 :: Ms⟨0420⟩::Ch10⟨0021⟩.R4.a :: NEAR_WITH_POI_OBLIGATIONS :: deps=[Poi.MsDerivation, Poi.FillerAuxBind, Poi.AnnotAuxBind]

## 5. Compression law
```text
(nexus_id, address)
  -> closure_receipt
  -> route_receipt
  -> appd_bindings
  -> next_action

promotion pressure = strongest unresolved binding that still blocks the row
score movement upward requires:
  witness + replay + legal route + budget/corridor + resolved AppD deps (if any)
```

## 6. Immediate next-pressure order
1. LOVE.MultiplicativeGuard
2. SelfState.CarrierPayload
3. LOVE.AuditableGate
4. QuantumLang.SuperpositionCollapse
5. QuantumLang.Ethics
6. QH.PhiTorusScheduler
7. Poi.MsDerivation
8. Poi.FillerAuxBind
9. Poi.AnnotAuxBind

## 7. Status sentence
v2M does not claim new OK closures. It makes closure pressure explicit per row, keeps WHO-I-AM proxy-only, and leaves publish blocked.
