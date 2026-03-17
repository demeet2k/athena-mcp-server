# Ch11<0022> - Helical Restart and Loop Closure

StationHeader: [Arc 3 | Rot 0 | Lane Me | w=10]
Workflow role: Aether versus Void transport, restart continuity, and lawful reset by capsule.
Primary hubs: AppA -> AppF -> AppM -> AppL -> AppI

## Routing context

- Orbit previous: `Ch10<0021>`
- Orbit next: `Ch12<0023>`
- Rail previous: `Ch09<0020>`
- Rail next: `Ch13<0030>`
- Arc previous: `Ch10<0021>`
- Arc next: `Ch12<0023>`
- Appendix couplings: `AppA, AppF, AppM, AppL, AppI`
- Family: `helical-recursion-engine`
- Identity-routed: `true`
- STRUCTURALLY CRITICAL: converts completion into restart

## Source capsules

- `03_2026_03_09_helical_recursion_and_ch12_boundary_checks.md`
- `04_2026_03_09_perfect_recursion_helical_manifestation_engine.md`
- `07_architects_core_initialization.md`
- `09_chapter_11_perpetual_motion_example.md`
- `10_chapter_11_perpetual_motion_example.md`
- `12_information_from_the_void_mani.md`

## Crystal tile

### Lens S

#### Facet 1 - Objects

- S1a: `RestartEngine` — The core operator that receives a completion signal from Ch21 and transforms it into a lawful re-entry token for Ch01 without destroying accumulated state.
- S1b: `LoopCloser` — A boundary-sealing operator that detects when a traversal has returned to its origin and binds the terminal state to the initial state as a closed morphism.
- S1c: `HelicalBridge` — A transport structure connecting completion at orbit level n to entry at orbit level n+1, encoding the vertical ascent that prevents degenerate flat loops.
- S1d: `ToroidalGate` — The re-entry aperture through which a closed loop passes to begin a new cycle on the toroidal manifold, preserving winding number and phase.

#### Facet 2 - Laws

- S2a: `RestartWithoutAmnesiaLaw` — Every restart must carry forward a signed state digest from the previous cycle; restarts that erase prior state are structurally forbidden.
- S2b: `LoopClosureCompleteness` — A loop may only be declared closed when every station in its declared schedule has been visited and its completeness witness is filed.
- S2c: `HelicalAscentMonotonicity` — The orbit level must strictly increase across each helical bridge crossing; lateral or downward crossings require explicit demotion certificates.
- S2d: `ToroidalWindingConservation` — The winding number of a traversal on the toroidal manifold is conserved across gate re-entry; changes require explicit winding-adjustment authorization.

#### Facet 3 - Constructions

- S3a: `RestartTokenMinter` — Receives a completion signal and the previous cycle's state digest, then mints a restart token encoding both the re-entry address and the carried-forward state.
- S3b: `ClosureBinder` — Takes the terminal state and the initial state of a loop, verifies structural compatibility, and emits a closure morphism binding them.
- S3c: `HelicalBridgeBuilder` — Constructs the transport structure between orbit levels, computing the vertical offset and adjusting phase to maintain helical geometry.
- S3d: `ToroidalGatekeeper` — Validates incoming re-entry requests against the toroidal manifold's winding constraints and either admits or rejects the traversal.

#### Facet 4 - Certificates

- S4a: `RestartStateContinuityCertificate` — Proves that the restart token carries a valid, unmodified state digest from the immediately preceding cycle.
- S4b: `LoopClosureCompleteSeal` — Certifies that all scheduled stations were visited and the closure morphism binds terminal to initial state correctly.
- S4c: `HelicalAscentProof` — Attests that the orbit level increased strictly across the helical bridge with no lateral or downward deviation.
- S4d: `ToroidalWindingReceipt` — Proves that the winding number was conserved or lawfully adjusted across the toroidal gate re-entry.

### Lens F

#### Facet 1 - Objects

- F1a: `AscentPhaseRegister` — A cyclic state variable tracking the current phase within the helical ascent cycle (ascent, turn, descent, re-entry).
- F1b: `TurnApex` — The highest point in the helical ascent where forward motion transitions to the descent arc that will carry the traversal back to re-entry.
- F1c: `DescentGradient` — The rate of phase change during the descent arc of the helical cycle, governing how quickly the traversal approaches re-entry.
- F1d: `RestartRhythmOscillator` — A periodic signal that synchronizes restart events across concurrent loops, ensuring phase-coherent re-entry at the toroidal gate.

#### Facet 2 - Laws

- F2a: `AscentPhaseContinuity` — The ascent phase must evolve continuously through the four-stage cycle; discrete jumps between stages require explicit phase-cut certificates.
- F2b: `TurnApexUniqueness` — Each helical cycle must contain exactly one turn apex; multiple apices indicate a degenerate cycle requiring correction.
- F2c: `DescentGradientBound` — The descent gradient must remain within declared bounds; too-rapid descent causes re-entry shock, too-slow descent causes cycle timeout.
- F2d: `RestartRhythmStability` — The restart rhythm oscillator's period must remain stable within declared tolerance across consecutive cycles.

#### Facet 3 - Constructions

- F3a: `AscentPhaseTracker` — Monitors the current ascent phase and emits phase-transition events at each stage boundary for downstream synchronization.
- F3b: `ApexDetector` — Identifies the turn apex in real time by detecting the sign change in the vertical velocity component of the helical traversal.
- F3c: `GradientController` — Adjusts the descent gradient dynamically to maintain it within declared bounds, applying corrective acceleration or deceleration.
- F3d: `RhythmSynchronizer` — Aligns the restart rhythm oscillator across concurrent loops by applying phase corrections at each re-entry event.

#### Facet 4 - Certificates

- F4a: `AscentPhaseContinuityReceipt` — Proves that the ascent phase evolved continuously through all four stages without unauthorized jumps.
- F4b: `ApexUniquenessCertificate` — Certifies that exactly one turn apex occurred in the audited helical cycle.
- F4c: `GradientBoundSeal` — Attests that the descent gradient remained within declared bounds throughout the descent arc.
- F4d: `RhythmStabilityProof` — Proves that the restart rhythm oscillator maintained stable period within tolerance across the audited cycles.

### Lens C

#### Facet 1 - Objects

- C1a: `AmnesiaDetector` — A diagnostic probe that compares the restart token's state digest against the previous cycle's terminal state, flagging any data loss.
- C1b: `RestartValidityPredicate` — A decidable boolean function returning true if and only if the restart token satisfies all structural and semantic preconditions for re-entry.
- C1c: `ClosureCompletenessWitness` — A trace object recording every station visited during a loop, used to verify that no scheduled stop was skipped before closure.
- C1d: `ToroidalConsistencyChecker` — A validator ensuring that the traversal's position on the toroidal manifold after re-entry is consistent with the declared winding number and phase.

#### Facet 2 - Laws

- C2a: `AmnesiaZeroTolerance` — Any detected amnesia (state digest mismatch between restart token and previous terminal state) immediately halts the restart and triggers quarantine.
- C2b: `RestartValidityDecidability` — The restart validity predicate must be decidable in finite time given the token and the re-entry manifold's current state.
- C2c: `ClosureCompletenessNecessity` — A loop closure is valid if and only if the completeness witness accounts for every scheduled station with no gaps or duplicates.
- C2d: `ToroidalConsistencyStrictness` — Post-re-entry position must match the predicted position within machine epsilon; deviations beyond this threshold invalidate the re-entry.

#### Facet 3 - Constructions

- C3a: `AmnesiaScanner` — Executes a byte-level comparison between the restart token's state digest and the archived terminal state, reporting any discrepancies.
- C3b: `RestartPreconditionEvaluator` — Checks all structural and semantic preconditions for a restart token and emits a pass/fail verdict with diagnostic details.
- C3c: `CompletenessTraceAuditor` — Walks the closure completeness witness against the declared schedule, emitting a discrepancy report or a clean-audit certificate.
- C3d: `ToroidalPositionVerifier` — Computes the expected post-re-entry position from winding number and phase, then compares it against the actual position.

#### Facet 4 - Certificates

- C4a: `AmnesiaFreeCertificate` — Proves that the restart token's state digest matches the previous cycle's terminal state with zero data loss.
- C4b: `RestartValidityProof` — Certifies that the restart token passed all precondition checks and is authorized for re-entry.
- C4c: `ClosureCompletenessVerificationSeal` — Proves that the completeness witness accounts for every scheduled station in the closed loop.
- C4d: `ToroidalConsistencyReceipt` — Attests that post-re-entry position matched the predicted value within declared tolerance.

### Lens R

#### Facet 1 - Objects

- R1a: `RecursiveRestartSeed` — A restart definition that generates sub-restarts at each recursion level, producing a hierarchy of nested restart cycles.
- R1b: `FractalHelixSpine` — A self-similar helical structure where each coil, when magnified, reveals a complete sub-helix with the same ascent geometry.
- R1c: `SelfClosingLoop` — A loop that carries its own closure logic internally, capable of detecting its own completion and binding terminal to initial state autonomously.
- R1d: `HelicalFixedPoint` — A configuration where the restart engine's output, when fed back as input, reproduces the same restart token, representing perpetual stable re-entry.

#### Facet 2 - Laws

- R2a: `RecursiveRestartBound` — Recursive restart seeds must terminate their expansion within a declared depth bound; unbounded recursive restart is forbidden.
- R2b: `FractalHelixSelfSimilarity` — Sub-helices revealed by magnification must preserve the ascent geometry and winding properties of the parent helix.
- R2c: `SelfClosureDeterminism` — A self-closing loop must produce identical closure morphisms regardless of the order in which its stations emit completion signals.
- R2d: `HelicalFixedPointAttraction` — Perturbations to the helical fixed point must decay exponentially, restoring perpetual re-entry within a bounded number of cycles.

#### Facet 3 - Constructions

- R3a: `RecursiveRestartUnfolder` — Expands a recursive restart seed to the declared depth, instantiating sub-restart cycles and wiring inter-level helical bridges.
- R3b: `FractalHelixGenerator` — Constructs the fractal helix spine from a template coil, replicating it at each scale level with appropriate phase and amplitude adjustments.
- R3c: `SelfClosureExecutor` — Runs the internal closure logic of a self-closing loop, producing the closure morphism and filing the completeness witness.
- R3d: `HelicalFixedPointSolver` — Iteratively applies the restart engine to its own output until convergence to the helical fixed point is detected.

#### Facet 4 - Certificates

- R4a: `RecursiveRestartTerminationProof` — Proves that a recursive restart seed completed its expansion within the declared depth bound.
- R4b: `FractalHelixSimilarityCertificate` — Certifies that sub-helices maintain geometric self-similarity with the parent at all generated levels.
- R4c: `SelfClosureDeterminismSeal` — Attests that a self-closing loop produced identical closure morphisms under multiple station-completion orderings.
- R4d: `HelicalFixedPointConvergenceReceipt` — Proves that the helical fixed-point solver converged to a stable perpetual re-entry configuration within bounds.
