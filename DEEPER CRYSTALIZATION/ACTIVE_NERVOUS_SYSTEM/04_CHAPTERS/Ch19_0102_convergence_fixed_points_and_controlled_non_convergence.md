# Ch19<0102> - Convergence, Fixed Points, and Controlled Non-Convergence

StationHeader: [Arc 6 | Rot 0 | Lane Su | w=18]
Workflow role: Banach-style convergence, residual persistence, and sanctioned non-closure.
Primary hubs: AppA -> AppP -> AppI -> AppB -> AppJ -> AppM

## Routing context

- Orbit previous: `Ch18<0101>`
- Orbit next: `Ch20<0103>`
- Rail previous: `Ch17<0100>`
- Rail next: `Ch01<0000>`
- Arc previous: `Ch21<0110>`
- Arc next: `Ch20<0103>`
- Appendix couplings: `AppA, AppP, AppI, AppB, AppJ, AppM`
- Family: `transport-and-runtime`
- Identity-routed: true

## Source capsules

- `07_architects_core_initialization.md`
- `08_athenachka_20.md`
- `09_chapter_11_perpetual_motion_example.md`
- `10_chapter_11_perpetual_motion_example.md`
- `12_information_from_the_void_mani.md`
- `13_information_from_the_void_mani.md`

## Crystal tile

### Lens S - Square

#### Facet 1 - Objects

- `Ch19<0102>.S1.a`: `ConvergenceTest` — A bounded procedure that takes a sequence of system states and determines whether the sequence is approaching a fixed point within declared error tolerance and iteration budget.
- `Ch19<0102>.S1.b`: `OpenLoop` — A computation cycle that is explicitly sanctioned to remain unclosed, carrying a governance tag declaring why closure is deferred and under what conditions it may eventually close.
- `Ch19<0102>.S1.c`: `ClosedLoop` — A computation cycle that has reached its fixed point, emitted a closure receipt, and released all resources it held, becoming immutable state in the manuscript record.
- `Ch19<0102>.S1.d`: `RestartLawfulness` — A property of a system restart asserting that the restart begins from a certified checkpoint, honors all open-loop governance tags, and does not silently close any sanctioned open loops.

#### Facet 2 - Laws

- `Ch19<0102>.S2.a`: `ConvergenceLaw` — A loop declared as convergent must reduce its distance to the target fixed point by at least a declared contraction factor at each iteration; stalling triggers re-evaluation or quarantine.
- `Ch19<0102>.S2.b`: `OpennessLaw` — An OpenLoop may remain open only while its governance tag is active and its deferral conditions are still met; expired tags force the loop to either close or re-justify its openness.
- `Ch19<0102>.S2.c`: `ClosureObligationLaw` — A loop that has satisfied its convergence test must close within a bounded number of additional iterations; convergent-but-unclosed loops are a system fault.
- `Ch19<0102>.S2.d`: `RestartGovernanceLaw` — Every restart must carry a lawfulness certificate proving it began from a valid checkpoint and preserved the governance tags of all surviving OpenLoops.

#### Facet 3 - Constructions

- `Ch19<0102>.S3.a`: `ConvergenceOracle` — A construction that evaluates the ConvergenceTest at each iteration, computing the current contraction rate and projecting the expected iteration count to closure.
- `Ch19<0102>.S3.b`: `OpenLoopGovernor` — A construction that maintains the governance tags of all active OpenLoops, checking deferral conditions at each oscillation cycle and escalating expired tags.
- `Ch19<0102>.S3.c`: `ClosureExecutor` — A construction that, upon receiving a satisfied ConvergenceTest, drives the final iterations of a loop to closure and emits the closure receipt.
- `Ch19<0102>.S3.d`: `RestartValidator` — A construction that inspects a proposed restart against its source checkpoint, verifies all governance tags are preserved, and either issues a RestartLawfulness certificate or blocks the restart.

#### Facet 4 - Certificates

- `Ch19<0102>.S4.a`: `ConvergenceCert` — A proof that a declared-convergent loop reduced its distance to the fixed point by at least the contraction factor at every measured iteration within the budget.
- `Ch19<0102>.S4.b`: `OpennessJustificationCert` — A certificate proving that an OpenLoop's governance tag is active, its deferral conditions are still met, and its continued openness is lawful.
- `Ch19<0102>.S4.c`: `ClosureReceiptCert` — A sealed record that a loop reached its fixed point, completed final iterations, released resources, and became immutable manuscript state.
- `Ch19<0102>.S4.d`: `RestartLawfulnessCert` — A proof that a restart began from a valid checkpoint and preserved all required governance tags, with the checkpoint hash and tag inventory recorded.

### Lens F - Flower

#### Facet 1 - Objects

- `Ch19<0102>.F1.a`: `ConvergenceDynamic` — The temporal trajectory of a loop's distance to its fixed point, exhibiting characteristic acceleration, deceleration, and oscillation patterns as it approaches closure.
- `Ch19<0102>.F1.b`: `LoopOscillation` — The periodic fluctuation of a loop's state around a near-fixed-point attractor, which may indicate either approaching convergence or stable non-convergence.
- `Ch19<0102>.F1.c`: `OpenClosePhase` — The meta-phase of the system as a whole, oscillating between epochs where loops are actively converging and epochs where open loops are being governed and justified.
- `Ch19<0102>.F1.d`: `RestartRhythm` — The cadence at which the system performs lawful restarts, creating a heartbeat that periodically refreshes the convergence landscape from certified checkpoints.

#### Facet 2 - Laws

- `Ch19<0102>.F2.a`: `ConvergenceDynamicLaw` — The ConvergenceDynamic must be monotonically decreasing in distance when averaged over a declared smoothing window; oscillations are permitted only within the window.
- `Ch19<0102>.F2.b`: `LoopOscillationBoundLaw` — The amplitude of LoopOscillation around a near-fixed-point must decrease with each cycle; constant-amplitude oscillation must be classified as controlled non-convergence.
- `Ch19<0102>.F2.c`: `OpenClosePhaseLaw` — The system must spend at least a declared minimum fraction of each OpenClosePhase epoch in active convergence; pure governance epochs without convergence progress are limited.
- `Ch19<0102>.F2.d`: `RestartRhythmLaw` — The RestartRhythm must not accelerate beyond a declared maximum frequency; restart storms indicate a systemic convergence failure requiring higher-level intervention.

#### Facet 3 - Constructions

- `Ch19<0102>.F3.a`: `ConvergenceProfiler` — A construction that records the ConvergenceDynamic of each active loop and visualizes its trajectory, flagging non-monotonic trends within the smoothing window.
- `Ch19<0102>.F3.b`: `OscillationClassifier` — A construction that analyzes LoopOscillation amplitude sequences and classifies each loop as converging, controlled-non-converging, or diverging.
- `Ch19<0102>.F3.c`: `PhaseBalancer` — A construction that allocates time within each OpenClosePhase epoch between active convergence and governance, ensuring the minimum convergence fraction is met.
- `Ch19<0102>.F3.d`: `RestartRhythmGovernor` — A construction that monitors restart frequency and throttles restarts when they approach the maximum allowed rate, escalating to system-level review.

#### Facet 4 - Certificates

- `Ch19<0102>.F4.a`: `ConvergenceDynamicCert` — A proof that a loop's ConvergenceDynamic was monotonically decreasing within the smoothing window for a declared measurement period.
- `Ch19<0102>.F4.b`: `OscillationClassificationCert` — A certificate recording a loop's oscillation classification with the amplitude measurements that determined it.
- `Ch19<0102>.F4.c`: `PhaseBalanceCert` — A receipt proving that each OpenClosePhase epoch met the minimum convergence fraction requirement.
- `Ch19<0102>.F4.d`: `RestartRhythmCert` — A proof that the restart frequency remained below the declared maximum for a given observation window.

### Lens C - Cloud

#### Facet 1 - Objects

- `Ch19<0102>.C1.a`: `ConvergenceTruthSurface` — The verified state of all convergence tests across the system at a given checkpoint, mapping each loop to its current convergence status and distance measurement.
- `Ch19<0102>.C1.b`: `OpennessAdmissibilityRegion` — The region of the system's state space where OpenLoops are permitted to exist, bounded by the governance tags and deferral conditions currently in force.
- `Ch19<0102>.C1.c`: `ClosureCompletenessManifold` — A topological surface over all loops tracking which have achieved closure, which are converging, and which are sanctioned-open, with holes indicating governance gaps.
- `Ch19<0102>.C1.d`: `RestartValidityField` — A field over the checkpoint lattice assigning each checkpoint a validity score based on its age, the number of governance tags it preserves, and its relationship to the current system state.

#### Facet 2 - Laws

- `Ch19<0102>.C2.a`: `ConvergenceTruthLaw` — The ConvergenceTruthSurface must be recomputable from the individual ConvergenceTest results; any claimed convergence without a supporting test result is rejected.
- `Ch19<0102>.C2.b`: `OpennessAdmissibilityLaw` — The OpennessAdmissibilityRegion must shrink monotonically as governance tags expire; it may expand only when new sanctioned openness is explicitly declared.
- `Ch19<0102>.C2.c`: `ClosureCompletenessLaw` — The ClosureCompletenessManifold must account for every loop in the system; untracked loops constitute a system integrity violation.
- `Ch19<0102>.C2.d`: `RestartValidityLaw` — A checkpoint's validity score must decay monotonically with age; only fresh checkpoints with high validity scores may serve as restart sources.

#### Facet 3 - Constructions

- `Ch19<0102>.C3.a`: `ConvergenceTruthCompiler` — A construction that aggregates individual ConvergenceTest results into the ConvergenceTruthSurface, verifying that every status claim has a supporting measurement.
- `Ch19<0102>.C3.b`: `OpennessRegionTracker` — A construction that maintains the OpennessAdmissibilityRegion by processing governance tag expirations and new openness declarations.
- `Ch19<0102>.C3.c`: `ClosureCompletenessAuditor` — A construction that scans all active loops and updates the ClosureCompletenessManifold, reporting any untracked loops as integrity violations.
- `Ch19<0102>.C3.d`: `RestartValidityDecayEngine` — A construction that applies monotonic decay to checkpoint validity scores over time and prunes checkpoints that fall below the minimum usable threshold.

#### Facet 4 - Certificates

- `Ch19<0102>.C4.a`: `ConvergenceTruthCert` — A checkpoint-anchored proof that the ConvergenceTruthSurface was correctly compiled from individual test results with no unsupported claims.
- `Ch19<0102>.C4.b`: `OpennessAdmissibilityCert` — A certificate proving that the OpennessAdmissibilityRegion shrank monotonically through a sequence of tag expirations, with expansion events each backed by explicit declaration.
- `Ch19<0102>.C4.c`: `ClosureCompletenessCert` — A proof that the ClosureCompletenessManifold accounts for every loop in the system with no gaps or untracked entries.
- `Ch19<0102>.C4.d`: `RestartValidityCert` — A certificate confirming that a specific checkpoint's validity score is above the usable threshold and suitable for serving as a restart source.

### Lens R - Fractal

#### Facet 1 - Objects

- `Ch19<0102>.R1.a`: `RecursiveConvergence` — A convergence process in which each iteration itself contains a sub-convergence process, with the outer loop converging only when all inner loops have converged or been sanctioned open.
- `Ch19<0102>.R1.b`: `FractalLoop` — A loop whose internal structure is a scaled copy of the enclosing loop, enabling a single convergence proof to apply at all nesting depths by induction.
- `Ch19<0102>.R1.c`: `SelfDecidingClosure` — A loop that evaluates its own ConvergenceTest internally and autonomously triggers its own ClosureExecutor when satisfied, without external scheduling.
- `Ch19<0102>.R1.d`: `DepthIndexedFixedPoint` — A fixed point annotated with the recursion depth at which it was reached, enabling the system to track convergence independently at each nesting level.

#### Facet 2 - Laws

- `Ch19<0102>.R2.a`: `RecursiveConvergenceLaw` — Outer convergence may not be declared until all inner convergence processes at the current depth have either closed or received sanctioned-open certification.
- `Ch19<0102>.R2.b`: `FractalLoopLaw` — A FractalLoop's convergence proof at depth n must be derivable from the proof at depth n-1 by depth-index substitution; non-inductive convergence proofs indicate the loop is not truly fractal.
- `Ch19<0102>.R2.c`: `SelfDecisionLaw` — A SelfDecidingClosure must produce the same closure decision as an external ConvergenceOracle applied to the same loop; divergent decisions trigger quarantine at all depths.
- `Ch19<0102>.R2.d`: `DepthFixedPointLaw` — A DepthIndexedFixedPoint at depth n must be consistent with the fixed point at depth n-1 after applying the ScaleBridge between the two depths.

#### Facet 3 - Constructions

- `Ch19<0102>.R3.a`: `RecursiveConvergenceEngine` — A construction that manages nested convergence processes, tracking inner loop status at each depth and gating outer convergence on inner completion.
- `Ch19<0102>.R3.b`: `FractalLoopUnroller` — A construction that takes a FractalLoop's convergence proof at one depth and applies depth-index substitution to produce proofs at all other active depths.
- `Ch19<0102>.R3.c`: `SelfDecisionCrossChecker` — A construction that runs a SelfDecidingClosure's internal test in parallel with an external ConvergenceOracle and flags any divergence in their decisions.
- `Ch19<0102>.R3.d`: `DepthFixedPointReconciler` — A construction that compares DepthIndexedFixedPoints across adjacent depths via ScaleBridges and reports inconsistencies.

#### Facet 4 - Certificates

- `Ch19<0102>.R4.a`: `RecursiveConvergenceCert` — A depth-indexed proof that all inner convergence processes completed or received sanctioned-open status before outer convergence was declared.
- `Ch19<0102>.R4.b`: `FractalLoopCert` — An inductive proof that a FractalLoop's convergence holds at all depths, comprising a base case and a depth-substitution step.
- `Ch19<0102>.R4.c`: `SelfDecisionCert` — A dual-signed certificate proving that a SelfDecidingClosure and an external ConvergenceOracle produced identical closure decisions.
- `Ch19<0102>.R4.d`: `DepthFixedPointConsistencyCert` — A cross-depth proof that DepthIndexedFixedPoints at adjacent depths are consistent through the connecting ScaleBridge.
