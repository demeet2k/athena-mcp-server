# ATHENA-PRIME — Per-Mine Disarm Kit v2O

Status: NEAR / NONPUBLISH  
Scope: surfaced unresolved resolver keys and mine nodes grounded in the currently uploaded corpus only.  
Root: ATHENA-PRIME :: WHO-I-AM::PROXY :: Σ={AppA,AppI,AppM}

## Global disarm law

Promotion is blocked until `W_min` exists and replay closes.  
Ordering is normative: provenance/source integrity first, then `W_min` closure, then replay determinism, then optional enrichments.  
If ambiguity remains epistemic, route to `AppL` with `CandidateSet + EvidencePlan`.  
If replay mismatches, conflict remains open, or corridor/policy breaks, route to `AppK`.  
NEAR never routes to `AppO`.

## Universal lane template

- Resolve lane: `AppA -> AppI -> AppM -> AppD`
- NEAR lane: `AppA -> AppI -> AppM -> AppJ`
- AMBIG lane: `AppA -> AppI -> AppM -> AppL`
- FAIL lane: `AppA -> AppI -> AppM -> AppK`
- Closure lane: `... -> AppM`
- Publish is gated separately and is not part of this kit.

## Disarm rows

### 01. LOVE.MultiplicativeGuard
- **Truth now:** AMBIG
- **Surfaced anchors:** `Ms⟨5381⟩::Ch17⟨0100⟩.S2.b`, `Ms⟨5381⟩::Ch20⟨0103⟩.S1.c`
- **Surface W_min:** concrete AppD binding witness to a `GlobalAddr`; `WB:ConsentReceiptDigest`; `WB:LoveSpecDigest`; `WB:LoveSpecRegistryMerkleRoot`
- **Replay target:** `RC:LoveGateReplaySuite`, `RC:LoveSpecRegistrySuite`
- **Seal target:** `Cert:LOVEReplay`, `Cert:LoveSpecRegistryClosure`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch17/Ch20 -> AppM`
- **Stop-if:** evidence still points to multiple plausible bind targets
- **Escalate:** `AppL` if target ambiguity persists; `AppK` on overclaim, replay mismatch, or policy break
- **Immediate actions:** bind resolver key; merklize LoveSpec registry; replay love-gate receipts; seal AppM proof

### 02. SelfState.CarrierPayload
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch20⟨0103⟩.S1.b`
- **Surface W_min:** concrete AppD binding witness; `WB:KappaLedgerMerkleRoot`; rollback-capable MIGRATE capsule
- **Replay target:** `RC:KappaLedgerReplaySuite`, rollback replay for any migration
- **Seal target:** `Cert:KappaCurvatureReceipts`, `Cert:KappaCurvatureReplay`, MIGRATE conformance certs
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch20 -> AppM`
- **Stop-if:** carrier/payload split remains alias-ambiguous or would require silent schema drift
- **Escalate:** `AppL` for unresolved split semantics; `AppK` for silent rewrite / migration-without-receipts
- **Immediate actions:** bind key; pin κ-ledger root; attach rollback plan; replay curvature ledger

### 03. LOVE.AuditableGate
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch20⟨0103⟩.S2.a`
- **Surface W_min:** concrete AppD binding witness; `WB:LoveSpecRegistryMerkleRoot`; `WB:ConsentReceiptDigest`; `WB:KappaLedgerMerkleRoot`
- **Replay target:** `RC:LoveGateReplaySuite`, `RC:KappaLedgerReplaySuite`
- **Seal target:** `Cert:LoveGateReplay`, `Cert:KappaCurvatureReplay`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch20 -> AppM`
- **Stop-if:** audit path cannot be replayed under pinned registry/version state
- **Escalate:** `AppL` if the gate spec remains underspecified; `AppK` if publish/commit is attempted without replay closure
- **Immediate actions:** bind key; pin registry digests; pack gate replay capsule; verify κ receipts

### 04. QH.PhiTorusScheduler
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch17⟨0100⟩.S1.a`
- **Surface W_min:** concrete AppD binding witness; `WB:CentralityID`; `WB:GraphDigest`; `WB:EnvPin`; `WB:FrontierDigest`; `WB:PolicyDigest`
- **Replay target:** `RC:CentralityReplaySuite`, `RC:SelectionReplaySuite`
- **Seal target:** `Cert:CentralityReplay`, `Cert:SelectionReplay`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch17 -> AppM`
- **Stop-if:** scheduler binding points to multiple incompatible targets or determinism depends on unpinned policy/env
- **Escalate:** `AppL` for competing scheduler binds; `AppK` for nondeterministic selection or receipt tamper
- **Immediate actions:** bind key; pin centrality + frontier digests; replay selection/centrality; seal AppM certs

### 05. Poi.MsDerivation
- **Truth now:** NEAR
- **Surfaced anchor:** `Ms⟨0420⟩::Ch10⟨0021⟩` compile-kernel path in the Poi/FLOW manuscript
- **Surface W_min:** exact Ms derivation in AppD; one replay witness each for local byte, phrase word, and global manifold lift
- **Replay target:** local-byte replay, phrase replay, manifold replay
- **Seal target:** local compile witness bundle for `Z_poi.local -> Z* -> Z_poi.phrase`
- **Route after success:** `AppA -> AppF -> AppH -> AppJ -> AppI -> AppM -> Ch10⟨0021⟩`
- **Stop-if:** auxiliary filler / annotation nodes remain unbound or expired corpus dependencies are still missing
- **Escalate:** stay `AppJ` while NEAR; `AppL` if exact Ms target stays ambiguous
- **Immediate actions:** pin exact Ms target in AppD; attach 3 lift witnesses; keep HCRL rotation complete; only then tighten to OK candidate

### 06. Closure.SeedPack
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch21⟨0110⟩.S2.a`
- **Surface W_min:** concrete AppD binding witness; `WB:FullDependencyRoot`; `WB:FullReplayRoot`
- **Replay target:** `RC:CriticalReplaySuite`
- **Seal target:** `Cert:FullDependencyClosure`, `Cert:FullReplayClosure`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch21 -> AppM`
- **Stop-if:** any critical dependency pointer stays unresolved
- **Escalate:** `AppK` if close-orbit is requested with unresolved conflict; `AppL` if competing SeedPack targets remain
- **Immediate actions:** bind key; merklize dependencies and critical replays; re-run close-orbit under Ch21

### 07. MIGRATE.PublishOverlay
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch21⟨0110⟩.S3.b`
- **Surface W_min:** concrete AppD binding witness; `WB:TrustRootDigest`; `WB:PublishManifestDigest`
- **Replay target:** `RC:PublishGateSuite`, `RC:PublishSignatureSuite`, `RC:ReplayMigrateSuite`
- **Seal target:** `Cert:PublishGateAudit`, `Cert:PublishSignatureClosure`, `Cert:MIGRATEClosure`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch21 -> AppP/AppO`
- **Stop-if:** publish path still depends on unresolved conflicts or unsatisfied signatures
- **Escalate:** `AppK` if publish is attempted before OK; `AppL` if multiple overlay meanings remain
- **Immediate actions:** bind overlay key; sign manifest; replay migrate suite; keep publish denied until OK

### 08. Tunnel.Def
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch16⟨0033⟩.S1.b`
- **Surface W_min:** concrete AppD binding witness; `WB:TunnelTestCorpusMerkleRoot`; `WB:TunnelLogMerkleRoot`
- **Replay target:** `RC:TunnelReplaySuite`, `RC:TunnelLogClosureSuite`
- **Seal target:** `Cert:TunnelDeterminism`, `Cert:TunnelLogClosure`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch16 -> AppM`
- **Stop-if:** collapse/reparam/expand formalization still has multiple incompatible definitions
- **Escalate:** `AppL` for unresolved formal ambiguity; `AppK` when tunnel failure capsule or logs disagree
- **Immediate actions:** bind formal definition; replay tunnel corpus; merklize logs; seal determinism

### 09. Tunnel6
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch16⟨0033⟩.S1.c`
- **Surface W_min:** concrete AppD binding witness; tunnel corpus root; log root; corridor adapter compatibility receipts
- **Replay target:** `RC:TunnelReplaySuite`, `RC:AdapterConformanceSuite`
- **Seal target:** `Cert:TunnelDeterminism`, `Cert:AdapterConformance`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch16 -> AppM`
- **Stop-if:** adapter registry or rollback plans are missing
- **Escalate:** `AppJ` if only adapter receipts are missing; `AppK` on tunnel failure without quarantine protocol
- **Immediate actions:** bind recipe; define adapter registry; attach rollback plans; replay conformance

### 10. MirrorOrch
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch16⟨0033⟩.S1.d`
- **Surface W_min:** concrete AppD binding witness; tunnel corpus/log roots; failure capsule schema witness
- **Replay target:** `RC:TunnelReplaySuite`, `RC:QuarantineSuite`
- **Seal target:** `Cert:TunnelDeterminism`, `Cert:QuarantineOnFailure`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch16 -> AppM`
- **Stop-if:** failure semantics are undefined or not isolated
- **Escalate:** `AppK` immediately if tunnel failure handling is untyped
- **Immediate actions:** bind formalization; define failure capsule; replay failure branch

### 11. AQMII.QNumberDef
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch04⟨0003⟩.S1.a`
- **Surface W_min:** concrete AppD binding witness; `WB:KrausSetDigest`; `WB:RNGPin`; `WB:NoiseModelID`
- **Replay target:** `RC:CPTPReplaySuite`, `RC:MeasurementReplaySuite`
- **Seal target:** `Cert:CPTP`, `Cert:KrausWitnessSet`, `Cert:DeterministicMeasurementReplay`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch04/Ch05 -> AppM`
- **Stop-if:** channel witnesses or noise/RNG pins are absent
- **Escalate:** `AppL` if multiple QNumber definitions remain; `AppK` on nondeterministic measurement replay
- **Immediate actions:** bind external def; attach channel witnesses; replay measurement suite

### 12. AQMI.EmbedRho_z_sigma
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch04⟨0003⟩.S3.a`
- **Surface W_min:** concrete AppD binding witness; Kraus witness bundle; RNG/noise pins
- **Replay target:** `RC:CPTPReplaySuite`, `RC:MeasurementReplaySuite`
- **Seal target:** `Cert:CPTP`, `Cert:DeterministicMeasurementReplay`
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch04/Ch05 -> AppM`
- **Stop-if:** embedding family target remains externally unresolved
- **Escalate:** `AppL` for unresolved external reference; `AppK` on replay mismatch
- **Immediate actions:** bind reference; replay embedding examples; seal channel/measurement certs

### 13. SelfSuff.§1.BoundaryTaxonomy
- **Truth now:** AMBIG
- **Surfaced anchor:** `Ms⟨5381⟩::Ch01⟨0000⟩.C1.a` external AppD resolution edge
- **Surface W_min:** concrete AppD binding witness for `SelfSuff.§1`; if bound target mutates, MIGRATE receipt is mandatory
- **Replay target:** boundary taxonomy replay under pinned AppD encoding/digest rules
- **Seal target:** external resolution closure plus HoloSeed fixed-point bundle if dependency is pulled into kernel closure
- **Route after success:** `AppA -> AppI -> AppM -> AppD -> Ch01 -> AppM`
- **Stop-if:** external target is unresolved or aliasing is silent
- **Escalate:** `AppL` if multiple candidate targets remain; `AppK` for silent alias / schema drift
- **Immediate actions:** resolve target; publish binding witness; replay boundary taxonomy closure

## Queue order

### NOW
1. LOVE.MultiplicativeGuard  
2. SelfState.CarrierPayload  
3. LOVE.AuditableGate  
4. Poi.MsDerivation  

### NEXT
5. QH.PhiTorusScheduler  
6. Closure.SeedPack  
7. MIGRATE.PublishOverlay  
8. Tunnel.Def / Tunnel6 / MirrorOrch cluster  

### LATER
9. AQMII.QNumberDef  
10. AQMI.EmbedRho_z_sigma  
11. SelfSuff.§1.BoundaryTaxonomy  

## Universal stop-if / fail branch

- Stop if evidence contradicts the current candidate target.
- Stop if ambiguity persists past the bounded threshold and route to `AppL`.
- Stop if replay mismatches and route to `AppK`.
- Stop if any task violates Ω / policy / corridor.
- Never promote a mine to OK without `W_min` closure and replay closure.
