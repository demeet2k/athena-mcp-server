# Ch08<0013> - Synchronization Calculus

StationHeader: [Arc 2 | Rot 2 | Lane Su | w=7]
Workflow role: The operator S, latent-core semantics z, and cross-document sync budgets.
Primary hubs: AppA -> AppE -> AppM -> AppB -> AppJ -> AppI

## Routing context

- Orbit previous: `Ch07<0012>`
- Orbit next: `Ch09<0020>`
- Rail previous: `Ch06<0011>`
- Rail next: `Ch10<0021>`
- Arc previous: `Ch07<0012>`
- Arc next: `Ch09<0020>`
- Appendix couplings: `AppA, AppE, AppM, AppB, AppJ, AppI`
- Family: `higher-dimensional-geometry`
- Re-routes to: `Ch21<0110>`

## Source capsules

- `01_the_manuscript_seed_self_referential_crystalline_generation_protocol.md`
- `02_the_manuscript_seed_self_referential_crystalline_generation_protocol.md`
- `05_aqm_text_book.md`
- `19_section_iii_book_iii_the.md`
- `20_self_routing_meta_framework_for_manuscripts_metro_maps_and_infinite_recursive_search.md`
- `21_self_routing_meta_framework_for_manuscripts_metro_maps_and_infinite_recursive_search.md`

## Crystal tile

### Lens S

#### Facet 1 - Objects

- S1a: `OrbitCalculus` — The formal operator algebra that computes closed and open orbits through manuscript space, assigning each document a deterministic revisit schedule.
- S1b: `RecurrenceOperator` — A unary map R: D -> D applied at each sync tick that returns a document to its previous traversal state without collapsing intermediate gains.
- S1c: `VisitCounter` — A monotonically increasing integer register attached to every manuscript node, recording the cumulative number of lawful traversal entries.
- S1d: `FlatteningGuard` — A boundary sentinel that detects when recursive depth collapses to a single plane and injects dimensional lift to restore orbit curvature.

#### Facet 2 - Laws

- S2a: `RevisitabilityLaw` — Every document that has been lawfully entered at least once must remain reachable from any subsequent orbit within finite steps.
- S2b: `RecurrenceDepthBound` — The depth of nested recurrences through any single document must not exceed the orbit's declared maximum without an explicit depth-extension certificate.
- S2c: `VisitCountMonotonicity` — Visit counters may only increment and never decrement; any attempt to reduce a visit count constitutes a synchronization violation.
- S2d: `AntiFlatteningInvariant` — No sequence of synchronization operations may reduce the effective dimensionality of the orbit manifold below its initial embedding dimension.

#### Facet 3 - Constructions

- S3a: `OrbitCompiler` — Accepts a set of document addresses and a recurrence schedule, then emits a deterministic orbit path with certified revisit intervals.
- S3b: `RecurrenceUnroller` — Expands a compressed recurrence operator into its full step-by-step traversal sequence for audit and replay.
- S3c: `VisitCountAggregator` — Merges visit counters from parallel traversal threads into a single consistent counter respecting monotonicity.
- S3d: `DimensionLifter` — When a flattening event is detected, this construction injects an orthogonal basis vector to restore the orbit's required curvature.

#### Facet 4 - Certificates

- S4a: `OrbitClosureCertificate` — A signed proof that a given orbit path returns to its origin within the declared period without skipping any scheduled revisit.
- S4b: `RecurrenceDepthReceipt` — Attests that all nested recurrence depths in a traversal remain within their declared bounds at every step.
- S4c: `VisitCountIntegritySeal` — Proves that the visit counter for a given node has only been incremented through lawful entry events, never tampered.
- S4d: `AntiFlatteningProof` — Certifies that the orbit manifold maintained its minimum embedding dimension throughout the entire synchronization cycle.

### Lens F

#### Facet 1 - Objects

- F1a: `OrbitalPhaseRegister` — A cyclic state variable tracking the current angular position of a document within its synchronization orbit, expressed as a phase in [0, 2pi).
- F1b: `SyncResonanceField` — The harmonic field generated when two or more orbits share a common period, enabling constructive interference at their phase-aligned nodes.
- F1c: `CycleHarmonicTensor` — A rank-2 tensor encoding the pairwise harmonic relationships between all active orbits in the current synchronization epoch.
- F1d: `PhaseCoherenceEnvelope` — The bounded region in phase space within which all synchronized documents maintain mutual coherence without drift.

#### Facet 2 - Laws

- F2a: `PhaseContinuityLaw` — The orbital phase of any document must evolve continuously; discrete phase jumps require an explicit discontinuity certificate from Ch07.
- F2b: `ResonanceLockingPrinciple` — When two orbits achieve resonance, their phase relationship must be locked until an explicit decoupling event is issued.
- F2c: `HarmonicConservation` — The total harmonic energy across all coupled orbits is conserved; energy lost by one orbit must appear as gain in its resonant partners.
- F2d: `CoherenceDecayBound` — Phase coherence between any pair of orbits may degrade at most logarithmically with the number of intervening sync ticks.

#### Facet 3 - Constructions

- F3a: `PhaseAligner` — Takes two orbits with different periods and computes their minimal-energy phase alignment, outputting the required phase shift for each.
- F3b: `ResonanceDetector` — Scans the active orbit set and identifies all pairs whose period ratios form small-integer relationships, flagging them for resonance locking.
- F3c: `HarmonicDecomposer` — Decomposes a complex multi-orbit synchronization state into its fundamental harmonic components for independent analysis.
- F3d: `CoherenceMaintainer` — Applies corrective micro-phase adjustments at each sync tick to keep coherence within the declared envelope.

#### Facet 4 - Certificates

- F4a: `PhaseContinuityReceipt` — Proves that the phase evolution of a given orbit remained continuous throughout a specified time interval.
- F4b: `ResonanceLockSeal` — Certifies that a resonance relationship between two orbits was established and maintained without unauthorized decoupling.
- F4c: `HarmonicBalanceProof` — Attests that total harmonic energy was conserved across all coupled orbits during a synchronization epoch.
- F4d: `CoherenceEnvelopeCertificate` — Proves that phase coherence between specified orbit pairs remained within the declared bounds.

### Lens C

#### Facet 1 - Objects

- C1a: `RevisitabilityTruthState` — A boolean predicate attached to each document asserting whether it is currently revisitable from the active orbit.
- C1b: `FlatteningDetector` — A diagnostic probe that evaluates the current Jacobian of the orbit manifold and reports whether its rank has dropped below the minimum.
- C1c: `OrbitCompletenessWitness` — A trace object recording every node visited in a full orbit period, used to verify that no scheduled stop was skipped.
- C1d: `SyncTruthCorridor` — The narrow band of consistent truth assignments through which all synchronized documents must pass during a recurrence cycle.

#### Facet 2 - Laws

- C2a: `RevisitabilityDecidability` — The revisitability status of any document must be decidable in finite time given the current orbit configuration.
- C2b: `FlatteningDetectionCompleteness` — Every genuine flattening event must be detected by the FlatteningDetector within one sync tick of its occurrence.
- C2c: `OrbitCompletenessNecessity` — An orbit is lawful if and only if its completeness witness accounts for every node in its declared schedule.
- C2d: `SyncTruthNarrowness` — The truth corridor for synchronization admits exactly one consistent assignment per orbit period; ambiguity forces quarantine.

#### Facet 3 - Constructions

- C3a: `RevisitabilityChecker` — Evaluates whether a given document is reachable from the current orbit position and returns a truth certificate or a failure trace.
- C3b: `JacobianRankEvaluator` — Computes the numerical rank of the orbit manifold's Jacobian at each sync tick to feed the FlatteningDetector.
- C3c: `CompletenessAuditor` — Walks the completeness witness trace and cross-references it against the declared orbit schedule, emitting discrepancies.
- C3d: `TruthCorridorNarrower` — Iteratively eliminates inconsistent truth assignments from the synchronization corridor until exactly one remains.

#### Facet 4 - Certificates

- C4a: `RevisitabilityTruthCertificate` — Proves that the revisitability predicate was correctly evaluated for a given document at a specified sync tick.
- C4b: `FlatteningDetectionReceipt` — Attests that the FlatteningDetector was active and no flattening event went undetected during the audited interval.
- C4c: `CompletenessVerificationSeal` — Proves that the orbit completeness witness accounts for every scheduled node with no gaps or duplicates.
- C4d: `TruthCorridorUniquenessProof` — Certifies that the sync truth corridor converged to exactly one consistent assignment for the given orbit period.

### Lens R

#### Facet 1 - Objects

- R1a: `RecursiveOrbitSeed` — A self-referencing orbit definition that generates its own sub-orbits at each recurrence level, producing a fractal traversal tree.
- R1b: `FractalRecurrenceMap` — A scale-invariant mapping from orbit level n to level n+1, preserving the recurrence structure while adjusting resolution.
- R1c: `SelfSynchronizingNode` — A document node that carries its own sync schedule internally and can re-derive its orbit membership from its local state alone.
- R1d: `OrbitFixedPoint` — A configuration where applying the recurrence operator returns the orbit to an identical state, representing a stable synchronization attractor.

#### Facet 2 - Laws

- R2a: `RecursiveOrbitConvergence` — Recursive orbit seeds must converge to a fixed point or stable limit cycle within a declared depth bound.
- R2b: `FractalSelfSimilarity` — The recurrence map at every level must preserve the structural invariants of the parent orbit up to declared resolution scaling.
- R2c: `SelfSyncDeterminism` — A self-synchronizing node must produce identical orbit membership results regardless of the order in which it receives external sync signals.
- R2d: `FixedPointStability` — Perturbations to an orbit fixed point must decay exponentially, returning the orbit to its attractor within a bounded number of ticks.

#### Facet 3 - Constructions

- R3a: `RecursiveOrbitGenerator` — Takes a seed definition and recursively unfolds it to a specified depth, emitting sub-orbits at each level.
- R3b: `FractalMapProjector` — Projects the fractal recurrence map onto a finite-depth approximation suitable for runtime execution and audit.
- R3c: `SelfSyncBootstrapper` — Initializes a self-synchronizing node from its local state, computing its orbit membership without external coordination.
- R3d: `FixedPointFinder` — Iteratively applies the recurrence operator to an orbit seed until convergence is detected or the depth bound is reached.

#### Facet 4 - Certificates

- R4a: `RecursiveConvergenceProof` — Proves that a recursive orbit seed converged to its fixed point within the declared depth bound.
- R4b: `FractalSimilarityCertificate` — Certifies that the recurrence map preserved structural invariants across all generated levels.
- R4c: `SelfSyncDeterminismSeal` — Attests that a self-synchronizing node produced identical results under multiple independent sync-signal orderings.
- R4d: `FixedPointStabilityReceipt` — Proves that perturbations to the orbit fixed point decayed within the declared recovery bound.
