# ATHENA-PRIME — Poi AppD Candidate Binder + Replay Witness Pack v2Q

## Status
- branch: v2Q.a + v2Q.b
- truth: BOUND_NEAR
- publish: DENY
- target candidate: `Ms⟨0420⟩::Ch10⟨0021⟩.R3.a`
- working meaning: local poi flower byte-lattice lifts to a 256-slot crystal word

## v2Q.a — AppD Candidate Binder

### Binder object
```text
BinderID = APPD-BIND::POI::MS0420::CH10-R3A::v2Q
Resolver = AppD
Key = Poi.MsDerivation
CandidateGlobalAddr = Ms⟨0420⟩::Ch10⟨0021⟩.R3.a
Status = BOUND_NEAR
Reason = target candidate is explicit in the verified poi kernel, but exact AppD pin and auxiliary support-node rebinding remain open
```

### Route legality
```text
Chapter = Ch10⟨0021⟩
Arc = 3
Lane = Su
ArcHub(3) = AppF
FacetBase(3) = AppH
Truth overlay = AppJ
Σ = {AppA, AppI, AppM}
Hub budget = 6
Legal hub sequence = AppA -> AppF -> AppH -> AppJ -> AppI -> AppM
Target = Ms⟨0420⟩::Ch10⟨0021⟩.R3.a
```

### Preserved invariants
```text
{m:n, ρ, K, d, Δφ, δ, Π}
```

### Open AppD obligations
1. Pin exact Ms derivation in AppD.
2. Rebind auxiliary filler nodes.
3. Rebind auxiliary annotation nodes.
4. Preserve HCRL rotation completion: S -> F -> C -> R.

## v2Q.b — Replay Witness Pack

### Replay objective
Reconstruct the poi compile route from local byte through phrase word to global manifold without violating Σ, hub budget, or proof-carrying replay law.

### Witness pack

#### W1 — Local byte witness
```text
WitnessID = WB::POI::LOCAL-BYTE::v2Q
Local compiled object = Ξ = (B, I)
Byte = B = q0 + 4 q1 + 16 q2 + 64 q3
q0 = downbeat anchor
q1 = hand relation
q2 = spin field
q3 = plane state
Invariant bundle I = (m:n, ρ, K, h, p, τ, Λ)
Target atom = Ch10⟨0021⟩.S1.a -> Ch10⟨0021⟩.R1.a
```

#### W2 — Phrase word witness
```text
WitnessID = WB::POI::PHRASE-WORD::v2Q
Phrase = B⃗ = (B1, ..., BN)
Canonical phrase-scale witness = local atom lifts to phrase word
Target atom = Ch10⟨0021⟩.R2.a
```

#### W3 — Global manifold witness
```text
WitnessID = WB::POI::GLOBAL-MANIFOLD::v2Q
Global lift = B⃗ ∈ {0,...,255}^{256}
State space = 256^256
Canonical manifold witness = phrase word lifts to manifold
Target atom = Ch10⟨0021⟩.R3.a
```

### Replay seed / generator
```text
ReplaySeedID = RC::POI::FLOWER-SEED::v2Q
1. parse descriptor into candidate byte/witness domains
2. apply closure, petal, anchor, hand, and plane constraints
3. collapse local domains
4. emit byte sequence
5. verify phrase-level neighbor compatibility
6. regenerate manifold state
```

### Edge set carried into replay
```text
e01 REF  Ch10⟨0021⟩.F1.a -> Ch10⟨0021⟩.S2.a
e02 REF  Ch10⟨0021⟩.F2.a -> Ch10⟨0021⟩.S2.b
e03 DUAL Ch10⟨0021⟩.F2.b <-> Ch10⟨0021⟩.S1.a
e04 PROOF Ch10⟨0021⟩.S2.b -> Ch10⟨0021⟩.S3.a
e05 GEN  Ch10⟨0021⟩.S1.a -> Ch10⟨0021⟩.R1.a
e06 GEN  Ch10⟨0021⟩.R1.a -> Ch10⟨0021⟩.R2.a
e07 GEN  Ch10⟨0021⟩.R2.a -> Ch10⟨0021⟩.R3.a
e08 CONFLICT Ch10⟨0021⟩.S1.a -> Ch10⟨0021⟩.C2.a
```

### Replay capsule minimum contents
```text
- ExecGraph digest
- schedule digest
- IOReceipt chain digest and payloads
- schema registry pointer
- codec / ABI pointers
- policy hash
- numeric model IDs where applicable
```

### Auxiliary tunnels
```text
Z_filler -> Z* -> Z_flower   (AMBIG / unresolved address binding)
Z_annot  -> Z* -> Z_byte     (AMBIG / unresolved address binding)
```

### Stop conditions / fail branches
- If exact AppD Ms pin cannot be produced: remain BOUND_NEAR.
- If replay capsule omits required proof hooks: FAIL via AppK.
- If route exceeds hub budget or drops Σ: FAIL.
- If auxiliary tunnels are used as if closed without rebinding: AMBIG/NEAR, not OK.

## Closure summary
```text
Current state = BOUND_NEAR
Closed now:
- target candidate chosen
- legal route chosen
- three replay witnesses named
- replay seed specified
- edge pack carried
Not closed yet:
- exact AppD bind witness
- filler support node rebinding
- annotation support node rebinding
- full HCRL S -> F -> C -> R completion
```
