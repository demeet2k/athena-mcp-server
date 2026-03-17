# Ch06<0011> - Documents-as-Theories

StationHeader: [Arc 1 | Rot 1 | Lane Su | w=5]
Workflow role: Theory-documents, manuscript objects, and theorem-bearing document shells.
Primary hubs: AppA -> AppC -> AppI -> AppM

## Routing context

- Orbit previous: `Ch05<0010>`
- Orbit next: `Ch07<0012>`
- Rail previous: `Ch01<0000>`
- Rail next: `Ch08<0013>`
- Arc previous: `Ch05<0010>`
- Arc next: `Ch04<0003>`
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
`[⊙Z_5↔Z* | ○Arc 1 | ○Rot 1 | △Lane Su | ⧈View S | ω=5]`

#### Facet 1 - Objects

- `Ch06<0011>.S1.a` `DocumentEntity` — A self-contained manuscript unit that functions as a theory, carrying axioms, derived claims, and evidence sufficient for independent verification.
- `Ch06<0011>.S1.b` `CorpusBinding` — The structural link connecting a document entity to the corpus lattice, ensuring the document's claims are reachable from the global address space.
- `Ch06<0011>.S1.c` `NervousLink` — The propagation channel through which state changes in one document entity are transmitted to dependent documents in the nervous system.
- `Ch06<0011>.S1.d` `MirrorBody` — The faithful replica of a document entity maintained in a separate storage layer, guaranteeing recoverability if the primary instance is corrupted.

#### Facet 2 - Laws

- `Ch06<0011>.S2.a` `DocumentAsTheoryLaw` — Every document entity must be interpretable as a theory with explicit axioms, derivation rules, and a finite set of derived claims.
- `Ch06<0011>.S2.b` `CorpusCoherenceLaw` — A corpus binding must preserve the logical consistency between the bound document and all other documents reachable from the same lattice node.
- `Ch06<0011>.S2.c` `NervousPropagationLaw` — State changes must propagate through nervous links within bounded latency; delayed propagation beyond the bound is a nervous-system fault.
- `Ch06<0011>.S2.d` `MirrorFidelityLaw` — A mirror body must be byte-identical to its primary at every synchronization point; divergence triggers immediate re-synchronization.

#### Facet 3 - Constructions

- `Ch06<0011>.S3.a` `theorizeDocument()` — Extracts axioms and derived claims from a document's content, assembling them into a formal theory structure with typed inference links.
- `Ch06<0011>.S3.b` `bindCorpus()` — Attaches a document entity to the corpus lattice at its assigned station code, verifying coherence with neighboring documents before finalizing.
- `Ch06<0011>.S3.c` `linkNervous()` — Establishes a nervous link between two document entities by registering the dependency, installing the propagation channel, and setting latency bounds.
- `Ch06<0011>.S3.d` `mirrorBody()` — Creates or re-synchronizes a mirror body by copying the primary document entity to the mirror layer and verifying byte-identical fidelity.

#### Facet 4 - Certificates

- `Ch06<0011>.S4.a` `Cert_Document_Theorized` — Attests that a document entity was successfully parsed into a formal theory with all axioms, rules, and claims explicitly typed.
- `Ch06<0011>.S4.b` `Cert_Corpus_Bound` — Attests that a document entity was bound to the corpus lattice with coherence verified against all reachable neighbors.
- `Ch06<0011>.S4.c` `Cert_Nervous_Linked` — Attests that a nervous link was established with the propagation channel active and latency within the declared bound.
- `Ch06<0011>.S4.d` `Cert_Mirror_Faithful` — Attests that a mirror body is byte-identical to its primary, verified by cryptographic hash comparison at the latest sync point.

### Lens F - Flower
`[⊙Z_5↔Z* | ○Arc 1 | ○Rot 1 | △Lane Su | ⧈View F | ω=5]`

#### Facet 1 - Objects

- `Ch06<0011>.F1.a` `TheoryPhaseState` — The symmetry-resolved decomposition of a document-theory into phase sectors, revealing which claim groups are related by rotational equivalence.
- `Ch06<0011>.F1.b` `CorpusResonanceField` — The field of mutual reinforcement that emerges when multiple bound documents share compatible axiom sets, amplifying collective confidence.
- `Ch06<0011>.F1.c` `NervousOscillation` — The periodic pulse pattern on a nervous link as state changes propagate and echo between coupled document entities.
- `Ch06<0011>.F1.d` `MirrorSymmetryAxis` — The axis of reflection between a primary document and its mirror body, defining the transformation that maps one to the other.

#### Facet 2 - Laws

- `Ch06<0011>.F2.a` `TheoryPhaseCompleteness` — The phase decomposition of a document-theory must span all its claims; any claim not assignable to a phase sector indicates an incomplete theory.
- `Ch06<0011>.F2.b` `CorpusResonanceStability` — The resonance field must remain stable under document additions; a new document that destabilizes the field carries a latent inconsistency.
- `Ch06<0011>.F2.c` `NervousOscillationDamping` — Nervous oscillations must damp to steady state within a declared number of propagation cycles; undamped oscillations indicate a feedback loop.
- `Ch06<0011>.F2.d` `MirrorSymmetryExactness` — The reflection transformation between primary and mirror must be exact; approximate reflections indicate a fidelity degradation.

#### Facet 3 - Constructions

- `Ch06<0011>.F3.a` `decomposeTheoryPhase()` — Decomposes a document-theory into phase sectors by grouping claims according to their symmetry equivalence under coordinate rotation.
- `Ch06<0011>.F3.b` `measureCorpusResonance()` — Computes the resonance field strength across the corpus by evaluating pairwise axiom compatibility between bound documents.
- `Ch06<0011>.F3.c` `dampNervousOscillation()` — Applies damping corrections to a nervous link that exhibits undamped oscillations, introducing controlled attenuation at each echo point.
- `Ch06<0011>.F3.d` `verifyMirrorSymmetry()` — Tests the reflection transformation between primary and mirror by applying it in both directions and verifying identity recovery.

#### Facet 4 - Certificates

- `Ch06<0011>.F4.a` `Cert_Phase_Complete` — Attests that the theory phase decomposition spans all claims in the document with no unassigned claims remaining.
- `Ch06<0011>.F4.b` `Cert_Resonance_Stable` — Attests that the corpus resonance field remained stable after the latest document addition, with field measurements before and after.
- `Ch06<0011>.F4.c` `Cert_Oscillation_Damped` — Attests that nervous oscillations damped to steady state within the declared cycle count, with the convergence trace attached.
- `Ch06<0011>.F4.d` `Cert_Mirror_Symmetric` — Attests that the mirror reflection transformation is exact, verified by round-trip application and identity recovery.

### Lens C - Cloud
`[⊙Z_5↔Z* | ○Arc 1 | ○Rot 1 | △Lane Su | ⧈View C | ω=5]`

#### Facet 1 - Objects

- `Ch06<0011>.C1.a` `TheoryAdmissibilityScore` — The truth-confidence score of a document-theory, aggregating the admissibility verdicts of its individual axioms and derived claims.
- `Ch06<0011>.C1.b` `CorpusCoherenceConfidence` — The measured certainty that a corpus binding preserves logical consistency, accounting for incomplete verification of distant neighbors.
- `Ch06<0011>.C1.c` `NervousLatencyUncertainty` — The uncertainty in a nervous link's propagation latency, bounding how precisely delivery timing can be guaranteed.
- `Ch06<0011>.C1.d` `MirrorDivergenceRisk` — The quantified probability that a mirror body has diverged from its primary between synchronization points, given the write rate and sync interval.

#### Facet 2 - Laws

- `Ch06<0011>.C2.a` `TheoryAdmissibilityThreshold` — A document-theory's admissibility score must exceed the declared threshold for it to be bindable to the corpus; below-threshold theories enter quarantine.
- `Ch06<0011>.C2.b` `CoherenceConfidenceFloor` — Corpus coherence confidence must not fall below a declared floor; violation triggers a full coherence re-audit of the affected lattice region.
- `Ch06<0011>.C2.c` `LatencyUncertaintyBound` — Nervous latency uncertainty must remain within the declared bound; exceeding it requires link re-calibration before further propagation.
- `Ch06<0011>.C2.d` `DivergenceRiskMitigation` — Mirror divergence risk must be mitigated by adjusting the synchronization interval to keep the probability below the declared maximum.

#### Facet 3 - Constructions

- `Ch06<0011>.C3.a` `scoreTheoryAdmissibility()` — Computes the admissibility score for a document-theory by aggregating per-claim truth-confidence values with evidence-quality weighting.
- `Ch06<0011>.C3.b` `auditCorpusCoherence()` — Audits corpus coherence by sampling pairwise consistency checks across bound documents and computing the aggregate confidence score.
- `Ch06<0011>.C3.c` `calibrateNervousLatency()` — Measures and calibrates a nervous link's latency by sending timed probe signals and computing the uncertainty interval.
- `Ch06<0011>.C3.d` `assessMirrorDivergence()` — Estimates mirror divergence risk from the write rate and sync interval, recommending interval adjustments if risk exceeds threshold.

#### Facet 4 - Certificates

- `Ch06<0011>.C4.a` `Cert_Theory_Admissible` — Attests that a document-theory's admissibility score exceeds the declared threshold, with the per-claim breakdown attached.
- `Ch06<0011>.C4.b` `Cert_Coherence_Audited` — Attests that corpus coherence was audited and the aggregate confidence score exceeds the declared floor.
- `Ch06<0011>.C4.c` `Cert_Latency_Calibrated` — Attests that nervous latency was calibrated and uncertainty falls within the declared bound, with probe measurements attached.
- `Ch06<0011>.C4.d` `Cert_Divergence_Assessed` — Attests that mirror divergence risk was assessed and the sync interval was adjusted to keep risk below the declared maximum.

### Lens R - Fractal
`[⊙Z_5↔Z* | ○Arc 1 | ○Rot 1 | △Lane Su | ⧈View R | ω=5]`

#### Facet 1 - Objects

- `Ch06<0011>.R1.a` `TheoryRecursionTree` — The recursive structure of a document-theory where derived claims serve as axioms for sub-theories, creating a self-similar theory hierarchy.
- `Ch06<0011>.R1.b` `CorpusCompressionRatio` — The ratio of the corpus's total semantic content to its minimal faithful encoding, measuring how efficiently the corpus self-compresses.
- `Ch06<0011>.R1.c` `NervousSelfSimilarity` — The property that nervous link topology at any sub-network scale mirrors the topology of the whole nervous system.
- `Ch06<0011>.R1.d` `MirrorRecursionDepth` — The number of mirror layers in a recursive mirroring scheme where mirrors themselves have mirrors for fault tolerance.

#### Facet 2 - Laws

- `Ch06<0011>.R2.a` `TheoryRecursionTermination` — The theory recursion tree must terminate at atomic claims that require no further derivation; infinite theory chains are prohibited.
- `Ch06<0011>.R2.b` `CorpusCompressionLosslessness` — Corpus compression must be lossless; every document entity must be perfectly recoverable from the compressed representation.
- `Ch06<0011>.R2.c` `NervousSelfSimilarityLaw` — Nervous sub-networks must obey the same propagation and latency laws as the full nervous system at every scale.
- `Ch06<0011>.R2.d` `MirrorRecursionBound` — Mirror recursion depth must be bounded; adding mirror layers beyond the bound yields diminishing fault-tolerance returns.

#### Facet 3 - Constructions

- `Ch06<0011>.R3.a` `recurseTheoryTree()` — Recursively expands a document-theory's derived claims into sub-theories, verifying termination at atomic claims at each depth.
- `Ch06<0011>.R3.b` `compressCorpus()` — Applies lossless compression to the corpus by identifying self-similar document patterns and encoding them as recursive references.
- `Ch06<0011>.R3.c` `verifyNervousSelfSimilarity()` — Tests nervous sub-networks at multiple scales against the full-system propagation laws, flagging any scale-dependent violations.
- `Ch06<0011>.R3.d` `boundMirrorRecursion()` — Sets and enforces the mirror recursion depth limit, computing the fault-tolerance gain at each additional layer.

#### Facet 4 - Certificates

- `Ch06<0011>.R4.a` `Cert_Theory_Terminated` — Attests that the theory recursion tree terminated at atomic claims at all branches with no infinite chains detected.
- `Ch06<0011>.R4.b` `Cert_Corpus_Compressed` — Attests that corpus compression was lossless, verified by full decompression and document-by-document comparison.
- `Ch06<0011>.R4.c` `Cert_Nervous_Self_Similar` — Attests that nervous self-similarity holds at all tested sub-network scales with no propagation law violations.
- `Ch06<0011>.R4.d` `Cert_Mirror_Recursion_Bounded` — Attests that mirror recursion depth is within the declared bound with the fault-tolerance analysis attached.
