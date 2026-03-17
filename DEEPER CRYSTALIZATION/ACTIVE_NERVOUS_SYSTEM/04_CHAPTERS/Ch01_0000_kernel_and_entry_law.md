# Ch01<0000> - Kernel and Entry Law

StationHeader: [Arc 0 | Rot 0 | Lane Su | w=0]
Workflow role: Foundational anchor, legend, and parse-safe entry station for the whole tome.
Primary hubs: AppA -> AppC -> AppI -> AppM

## Routing context

- Orbit previous: `Ch21<0110>`
- Orbit next: `Ch02<0001>`
- Rail previous: `Ch19<0102>`
- Rail next: `Ch06<0011>`
- Arc previous: `Ch03<0002>`
- Arc next: `Ch02<0001>`
- Appendix couplings: `AppA, AppC, AppI, AppM`

## Source capsules

- `01_the_manuscript_seed_self_referential_crystalline_generation_protocol.md`
- `02_the_manuscript_seed_self_referential_crystalline_generation_protocol.md`
- `05_aqm_text_book.md`
- `19_section_iii_book_iii_the.md`
- `20_self_routing_meta_framework_for_manuscripts_metro_maps_and_infinite_recursive_search.md`
- `21_self_routing_meta_framework_for_manuscripts_metro_maps_and_infinite_recursive_search.md`

## Crystal tile

### Lens S - Square
`[⊙Z_0↔Z* | ○Arc 0 | ○Rot 0 | △Lane Su | ⧈View S | ω=0]`

#### Facet 1 - Objects

- `Ch01<0000>.S1.a` `ParseKernel` — The indivisible computational seed that accepts or rejects every incoming token stream, guaranteeing that only well-formed inputs cross the tome boundary.
- `Ch01<0000>.S1.b` `EntryLaw` — The axiomatic gate predicate that every agent, document, or signal must satisfy before being admitted into the crystal lattice.
- `Ch01<0000>.S1.c` `CharterSeal` — The immutable identity stamp binding a private charter to its originating author, preventing forgery or unauthorized scope mutation.
- `Ch01<0000>.S1.d` `PrivateScope` — The isolation boundary that confines a charter's operational reach to its declared namespace, blocking cross-scope leakage.

#### Facet 2 - Laws

- `Ch01<0000>.S2.a` `ParseSafetyLaw` — Every token stream entering the kernel must be deterministically classifiable as ACCEPT or REJECT within bounded computation steps.
- `Ch01<0000>.S2.b` `EntryValidationLaw` — No entity may bypass the entry gate; admission requires a witness-stamped proof of well-formedness that the kernel can verify in constant time.
- `Ch01<0000>.S2.c` `CharterBindingLaw` — A charter, once sealed, cannot be modified without producing a new version hash; the original seal remains an immutable historical record.
- `Ch01<0000>.S2.d` `ScopeIsolationLaw` — Operations within a private scope cannot read from, write to, or signal any namespace outside its declared boundary without an explicit tunnel permit.

#### Facet 3 - Constructions

- `Ch01<0000>.S3.a` `buildKernel()` — Assembles the parse kernel from the base axiom set, wiring the token classifier, rejection log, and acceptance registry into a single boot sequence.
- `Ch01<0000>.S3.b` `validateEntry()` — Executes the entry law predicate against an incoming entity, producing either an admission receipt or a typed rejection with diagnostic trace.
- `Ch01<0000>.S3.c` `sealCharter()` — Computes the cryptographic seal over a charter's content, author identity, and timestamp, binding all three into a tamper-evident capsule.
- `Ch01<0000>.S3.d` `isolateScope()` — Instantiates a private namespace container with hard walls, injecting only the explicitly declared dependency set and blocking all ambient references.

#### Facet 4 - Certificates

- `Ch01<0000>.S4.a` `Cert_Parse_Safe` — Attests that the kernel parsed a given input stream without encountering ambiguity, infinite loops, or unclassifiable tokens.
- `Ch01<0000>.S4.b` `Cert_Entry_Valid` — Attests that an entity passed the entry law predicate with a complete witness trace that any future auditor can replay.
- `Ch01<0000>.S4.c` `Cert_Charter_Sealed` — Attests that a charter's seal matches its content hash and that no post-seal mutation has occurred.
- `Ch01<0000>.S4.d` `Cert_Scope_Isolated` — Attests that a private scope operated without any cross-boundary reads, writes, or signals during its entire lifecycle.

### Lens F - Flower
`[⊙Z_0↔Z* | ○Arc 0 | ○Rot 0 | △Lane Su | ⧈View F | ω=0]`

#### Facet 1 - Objects

- `Ch01<0000>.F1.a` `KernelPhaseState` — The symmetry-resolved phase portrait of the parse kernel, revealing which acceptance and rejection modes are related by rotational equivalence.
- `Ch01<0000>.F1.b` `EntryOrbital` — The cyclic orbit traced by an entity as it passes through successive entry validation stages, forming a closed loop upon successful admission.
- `Ch01<0000>.F1.c` `CharterSymmetryGroup` — The set of transformations under which a charter's semantic content remains invariant, defining its equivalence class within the tome.
- `Ch01<0000>.F1.d` `ScopeResonance` — The harmonic coupling pattern between adjacent private scopes that share a common parent namespace without violating isolation.

#### Facet 2 - Laws

- `Ch01<0000>.F2.a` `KernelPhaseInvariance` — The parse kernel's accept/reject classification must be invariant under any symmetry transformation of the input encoding.
- `Ch01<0000>.F2.b` `EntryOrbitalClosure` — Every entity that enters the validation cycle must either complete a full orbital return to admission or be ejected; no orbit may remain open.
- `Ch01<0000>.F2.c` `CharterSymmetryPreservation` — Sealing a charter must preserve all symmetries present in its pre-seal content; the seal operation commutes with the symmetry group.
- `Ch01<0000>.F2.d` `ScopeResonanceDecay` — Resonance between adjacent scopes must decay monotonically with namespace distance, preventing long-range coupling violations.

#### Facet 3 - Constructions

- `Ch01<0000>.F3.a` `resolveKernelPhase()` — Decomposes the kernel's state space into irreducible phase sectors, assigning each token class to its symmetry-resolved acceptance mode.
- `Ch01<0000>.F3.b` `traceEntryOrbital()` — Traces the full validation orbital for an incoming entity, recording phase transitions at each gate stage until closure or ejection.
- `Ch01<0000>.F3.c` `computeCharterSymmetry()` — Computes the symmetry group of a charter by testing invariance under all base-4 coordinate permutations of its content.
- `Ch01<0000>.F3.d` `measureScopeResonance()` — Quantifies the resonance coupling strength between two scopes by evaluating their shared boundary's spectral overlap.

#### Facet 4 - Certificates

- `Ch01<0000>.F4.a` `Cert_Phase_Resolved` — Attests that the kernel's phase decomposition is complete and that every token class maps to exactly one irreducible sector.
- `Ch01<0000>.F4.b` `Cert_Orbital_Closed` — Attests that an entity's entry orbital terminated in either full admission or clean ejection with no dangling phase transitions.
- `Ch01<0000>.F4.c` `Cert_Symmetry_Preserved` — Attests that the charter seal operation preserved all pre-existing symmetries, verified by group-action replay.
- `Ch01<0000>.F4.d` `Cert_Resonance_Bounded` — Attests that inter-scope resonance falls below the isolation threshold at every measured boundary point.

### Lens C - Cloud
`[⊙Z_0↔Z* | ○Arc 0 | ○Rot 0 | △Lane Su | ⧈View C | ω=0]`

#### Facet 1 - Objects

- `Ch01<0000>.C1.a` `KernelTruthEnvelope` — The admissibility boundary within which the parse kernel's classifications carry certified truth status, beyond which results are marked uncertain.
- `Ch01<0000>.C1.b` `EntryAdmissibilityTest` — The multi-criterion evaluation that determines whether an entity's entry proof meets the minimum truth threshold for lattice admission.
- `Ch01<0000>.C1.c` `CharterUncertaintyMargin` — The measured gap between a charter's declared semantics and its verifiable operational behavior, quantifying residual ambiguity.
- `Ch01<0000>.C1.d` `ScopeConfidenceBound` — The upper limit on the confidence with which scope isolation can be asserted, accounting for covert channel analysis.

#### Facet 2 - Laws

- `Ch01<0000>.C2.a` `KernelTruthMonotonicity` — As additional witnesses are accumulated, the kernel's truth envelope can only expand or remain constant, never contract.
- `Ch01<0000>.C2.b` `EntryAdmissibilityThreshold` — An entity's admission proof must exceed the declared truth threshold; proofs at or below the threshold trigger quarantine rather than rejection.
- `Ch01<0000>.C2.c` `CharterUncertaintyMinimization` — Each charter revision must reduce the uncertainty margin or provide a certified explanation for why reduction was not achievable.
- `Ch01<0000>.C2.d` `ScopeConfidenceCalibration` — Scope confidence bounds must be recalibrated whenever the scope's dependency set changes, using fresh covert-channel analysis.

#### Facet 3 - Constructions

- `Ch01<0000>.C3.a` `evaluateKernelTruth()` — Evaluates the current truth envelope of the kernel by aggregating all accumulated witness attestations and computing their joint coverage.
- `Ch01<0000>.C3.b` `testEntryAdmissibility()` — Runs the multi-criterion admissibility test against an entity's proof, returning a scored verdict with per-criterion breakdown.
- `Ch01<0000>.C3.c` `measureCharterUncertainty()` — Measures the gap between declared and verified charter semantics by differential testing across boundary conditions.
- `Ch01<0000>.C3.d` `calibrateScopeConfidence()` — Recalculates scope confidence bounds by running covert-channel probes against all declared and discovered boundary surfaces.

#### Facet 4 - Certificates

- `Ch01<0000>.C4.a` `Cert_Truth_Envelope_Valid` — Attests that the kernel's truth envelope was computed from a complete witness set with no stale or revoked attestations.
- `Ch01<0000>.C4.b` `Cert_Admissibility_Passed` — Attests that an entity's proof exceeded the truth threshold on all criteria, with the scored breakdown attached as evidence.
- `Ch01<0000>.C4.c` `Cert_Uncertainty_Measured` — Attests that the charter's uncertainty margin was computed by a certified measurement process and falls within declared tolerances.
- `Ch01<0000>.C4.d` `Cert_Confidence_Calibrated` — Attests that scope confidence bounds reflect the most recent dependency set and covert-channel analysis results.

### Lens R - Fractal
`[⊙Z_0↔Z* | ○Arc 0 | ○Rot 0 | △Lane Su | ⧈View R | ω=0]`

#### Facet 1 - Objects

- `Ch01<0000>.R1.a` `KernelSelfSimilarity` — The property that the parse kernel's structure at every scale of decomposition mirrors the whole, enabling recursive verification without loss of fidelity.
- `Ch01<0000>.R1.b` `EntryRecursionDepth` — The measured depth of nested validation calls required to fully verify an entity's entry proof, bounded by the kernel's recursion limit.
- `Ch01<0000>.R1.c` `CharterCompressionRatio` — The ratio of a charter's semantic content to its minimal faithful encoding, measuring how efficiently the charter self-compresses.
- `Ch01<0000>.R1.d` `ScopeNestingInvariant` — The invariant property maintained when scopes are nested within scopes, ensuring that isolation guarantees compose recursively.

#### Facet 2 - Laws

- `Ch01<0000>.R2.a` `KernelSelfSimilarityLaw` — At every decomposition level, the kernel sub-component must satisfy the same parse-safety axioms as the whole kernel.
- `Ch01<0000>.R2.b` `EntryRecursionBound` — The recursion depth of entry validation must be bounded by O(log n) where n is the proof complexity, preventing stack exhaustion.
- `Ch01<0000>.R2.c` `CharterCompressionFidelity` — Compressing a charter must preserve all semantics recoverable by decompression; lossy compression is prohibited for charter content.
- `Ch01<0000>.R2.d` `ScopeNestingComposition` — The isolation guarantee of a nested scope is the intersection of its own guarantee with its parent's guarantee, computed compositionally.

#### Facet 3 - Constructions

- `Ch01<0000>.R3.a` `verifyKernelSelfSimilarity()` — Recursively decomposes the kernel and verifies that each sub-component satisfies the full axiom set, halting at the atomic token level.
- `Ch01<0000>.R3.b` `boundEntryRecursion()` — Instruments the entry validation process with a depth counter and hard limit, producing a bounded-recursion certificate upon completion.
- `Ch01<0000>.R3.c` `compressCharter()` — Applies lossless compression to a charter, producing a minimal encoding together with a decompression proof that guarantees semantic recovery.
- `Ch01<0000>.R3.d` `composeNestedScopes()` — Computes the composite isolation guarantee for a scope nesting chain by intersecting guarantees from outermost to innermost.

#### Facet 4 - Certificates

- `Ch01<0000>.R4.a` `Cert_Self_Similar` — Attests that the kernel passed self-similarity verification at all decomposition levels down to the atomic token boundary.
- `Ch01<0000>.R4.b` `Cert_Recursion_Bounded` — Attests that entry validation completed within the declared recursion depth bound with no stack overflow or truncation.
- `Ch01<0000>.R4.c` `Cert_Compression_Lossless` — Attests that charter compression preserved full semantic content, verified by round-trip decompression and differential comparison.
- `Ch01<0000>.R4.d` `Cert_Nesting_Composed` — Attests that nested scope isolation guarantees were correctly composed and that the composite guarantee holds at runtime.
