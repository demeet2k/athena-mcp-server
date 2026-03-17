# Ch16<0033> - Verification Harnesses and Replay Kernels

StationHeader: [Arc 5 | Rot 2 | Lane Sa | w=15]
Workflow role: Deterministic re-checks, test capsules, and correctness enforcement.
Primary hubs: AppA -> AppN -> AppM -> AppK -> AppI

## Routing context

- Orbit previous: `Ch15<0032>`
- Orbit next: `Ch17<0100>`
- Rail previous: `Ch14<0031>`
- Rail next: `Ch21<0110>`
- Arc previous: `Ch18<0101>`
- Arc next: `Ch17<0100>`
- Appendix couplings: `AppA, AppN, AppM, AppK, AppI`
- Family: `transport-and-runtime`
- Identity-routed: true
- Primary attractor for: `Ch13<0030>`

## Source capsules

- `05_aqm_text_book.md`
- `06_aqm_lm_cut_through_the_hybrid_lens_framework.md`
- `09_chapter_11_perpetual_motion_example.md`
- `10_chapter_11_perpetual_motion_example.md`
- `14_legal_transport_calculus.md`
- `25_the_crystal_live.md`

## Crystal tile

### Lens S - Square

#### Facet 1 - Objects

- `Ch16<0033>.S1.a`: `ReplaySurface` — A deterministic re-execution environment that accepts a sequence of witness tokens and reproduces the exact computation path that originally generated them, enabling bit-exact verification.
- `Ch16<0033>.S1.b`: `VerificationLayer` — A dedicated stratum of the runtime stack whose sole purpose is to accept computation receipts and confirm their consistency with the manuscript's declared laws.
- `Ch16<0033>.S1.c`: `HonestyMeter` — A quantitative instrument that measures the divergence between a module's declared behavior and its observed output across a replay window, producing a scalar honesty score.
- `Ch16<0033>.S1.d`: `RecursionGuard` — A depth-counting sentinel that prevents verification loops from exceeding a declared recursion bound, halting and reporting when the bound is reached.

#### Facet 2 - Laws

- `Ch16<0033>.S2.a`: `ReplayDeterminismLaw` — A ReplaySurface must produce identical outputs for identical witness-token sequences regardless of when or where the replay is executed.
- `Ch16<0033>.S2.b`: `VerificationCompleteLaw` — Every computation receipt submitted to a VerificationLayer must receive either a confirmation or a typed rejection; silent drops are forbidden.
- `Ch16<0033>.S2.c`: `HonestyObligationLaw` — Any module whose HonestyMeter score falls below the system-declared threshold must halt execution and submit to re-verification before resuming.
- `Ch16<0033>.S2.d`: `RecursionBoundLaw` — The RecursionGuard's depth bound must be declared before verification begins and may not be increased during an active verification session.

#### Facet 3 - Constructions

- `Ch16<0033>.S3.a`: `ReplayKernel` — A minimal execution kernel that strips all non-deterministic inputs and replays a computation using only the stored witness-token sequence and initial state snapshot.
- `Ch16<0033>.S3.b`: `VerificationHarness` — A test-framework construction that wraps any CUTModule in a VerificationLayer, injecting known inputs and comparing outputs against expected receipts.
- `Ch16<0033>.S3.c`: `HonestyAuditor` — A construction that periodically samples module outputs, feeds them to the HonestyMeter, and escalates to quarantine if the honesty score trends below threshold.
- `Ch16<0033>.S3.d`: `RecursionDepthTracker` — A construction that instruments every verification call with a depth counter, enforcing the RecursionBoundLaw and emitting a depth-exceeded alert on violation.

#### Facet 4 - Certificates

- `Ch16<0033>.S4.a`: `ReplayFidelityCert` — A proof that a ReplaySurface reproduced the original computation's outputs with bit-exact fidelity for a given witness-token sequence.
- `Ch16<0033>.S4.b`: `VerificationCompleteCert` — A receipt confirming that every computation receipt in a batch received either confirmation or typed rejection from the VerificationLayer.
- `Ch16<0033>.S4.c`: `HonestyScoreCert` — A timestamped attestation of a module's HonestyMeter score, including the sample window and the inputs used for measurement.
- `Ch16<0033>.S4.d`: `RecursionBoundCert` — A proof that a verification session completed without exceeding the declared recursion depth bound at any point during execution.

### Lens F - Flower

#### Facet 1 - Objects

- `Ch16<0033>.F1.a`: `VerificationResonance` — The harmonic state achieved when a ReplaySurface and its originating runtime synchronize their execution phases, enabling live cross-checking.
- `Ch16<0033>.F1.b`: `ReplayHarmonic` — The frequency signature of a replay cycle, derived from the witness-token arrival rate and the ReplayKernel's processing speed.
- `Ch16<0033>.F1.c`: `HonestyPhase` — The temporal window within each RuntimeOscillation cycle dedicated exclusively to HonestyMeter sampling and score computation.
- `Ch16<0033>.F1.d`: `VerificationPulse` — A periodic signal emitted by the VerificationLayer that triggers all registered modules to submit their latest computation receipts for checking.

#### Facet 2 - Laws

- `Ch16<0033>.F2.a`: `ResonanceSyncLaw` — VerificationResonance must be established before any live cross-checking begins; unsynchronized verification attempts are rejected.
- `Ch16<0033>.F2.b`: `ReplayHarmonicLaw` — The ReplayHarmonic frequency must be an integer multiple of the original execution frequency to prevent aliasing artifacts in the replayed computation.
- `Ch16<0033>.F2.c`: `HonestyPhaseLaw` — The HonestyPhase must not overlap with any module's active execution phase, ensuring that honesty measurement does not perturb the computation being measured.
- `Ch16<0033>.F2.d`: `VerificationPulseLaw` — Every VerificationPulse must reach all registered modules within a single oscillation cycle; modules that miss a pulse are flagged for priority re-verification.

#### Facet 3 - Constructions

- `Ch16<0033>.F3.a`: `ResonanceLock` — A construction that phase-aligns the ReplaySurface with the live runtime, establishing VerificationResonance by adjusting the replay clock rate.
- `Ch16<0033>.F3.b`: `HarmonicSampler` — A construction that measures the ReplayHarmonic of each active replay session and verifies it against the integer-multiple constraint.
- `Ch16<0033>.F3.c`: `HonestyPhaseScheduler` — A construction that carves out HonestyPhase windows within the RuntimeOscillation cycle without colliding with any module's execution phase.
- `Ch16<0033>.F3.d`: `PulseBroadcaster` — A construction that emits VerificationPulses to all registered modules and collects acknowledgments, reporting any module that fails to respond.

#### Facet 4 - Certificates

- `Ch16<0033>.F4.a`: `ResonanceLockCert` — A proof that VerificationResonance was achieved, recording the phase offset and clock-rate adjustment applied during synchronization.
- `Ch16<0033>.F4.b`: `HarmonicFidelityCert` — A certificate attesting that a ReplayHarmonic maintained its integer-multiple relationship to the original execution frequency for a declared duration.
- `Ch16<0033>.F4.c`: `HonestyPhaseIsolationCert` — A proof that no HonestyPhase window overlapped with any module's active execution phase during a given oscillation epoch.
- `Ch16<0033>.F4.d`: `PulseDeliveryCert` — A receipt proving that a VerificationPulse reached all registered modules within the required oscillation cycle, listing response timestamps.

### Lens C - Cloud

#### Facet 1 - Objects

- `Ch16<0033>.C1.a`: `ReplayTruthSurface` — The verified state of all completed replays at a given checkpoint, forming the ground truth against which new computations are judged honest.
- `Ch16<0033>.C1.b`: `VerificationCompletenessManifold` — A topological surface over the module graph that maps which modules have been fully verified, partially verified, or unverified.
- `Ch16<0033>.C1.c`: `HonestyCorridor` — A bounded region within the system's state space where all active modules maintain HonestyMeter scores above the declared threshold.
- `Ch16<0033>.C1.d`: `RecursionAdmissibilityField` — A field over the verification stack assigning each recursion depth an admissibility weight, decaying with depth to penalize unbounded nesting.

#### Facet 2 - Laws

- `Ch16<0033>.C2.a`: `ReplayTruthLaw` — The ReplayTruthSurface must be monotonically growing; once a replay is verified, its truth status may never be retracted without a full re-replay.
- `Ch16<0033>.C2.b`: `VerificationCompletenessLaw` — The VerificationCompletenessManifold must cover the entire active module graph; any unverified hole blocks system-level certification.
- `Ch16<0033>.C2.c`: `HonestyCorridorLaw` — The system may continue execution only while the HonestyCorridor is non-empty; if all modules fail honesty, the system must enter quarantine.
- `Ch16<0033>.C2.d`: `RecursionAdmissibilityLaw` — The RecursionAdmissibilityField must assign zero admissibility to any depth beyond the system-declared maximum, making deeper recursion structurally impossible.

#### Facet 3 - Constructions

- `Ch16<0033>.C3.a`: `TruthSurfaceAccumulator` — A construction that incorporates each verified replay result into the ReplayTruthSurface, checking monotonicity before accepting the update.
- `Ch16<0033>.C3.b`: `CompletenessMapper` — A construction that continuously surveys the module graph and updates the VerificationCompletenessManifold, highlighting unverified regions.
- `Ch16<0033>.C3.c`: `CorridorMonitor` — A construction that tracks all active HonestyMeter scores and computes the current extent of the HonestyCorridor in real time.
- `Ch16<0033>.C3.d`: `AdmissibilityDecayFunction` — A construction that computes the admissibility weight for each recursion depth using an exponential decay function anchored at the maximum depth.

#### Facet 4 - Certificates

- `Ch16<0033>.C4.a`: `ReplayTruthCert` — A checkpoint-anchored proof that the ReplayTruthSurface grew monotonically through a sequence of replay verification events.
- `Ch16<0033>.C4.b`: `VerificationCompletenessCert` — A topological proof that the VerificationCompletenessManifold covers the entire active module graph with no unverified holes.
- `Ch16<0033>.C4.c`: `HonestyCorridorCert` — A proof that the HonestyCorridor remained non-empty for a declared number of oscillation epochs, with all module scores above threshold.
- `Ch16<0033>.C4.d`: `RecursionAdmissibilityCert` — A certificate confirming that the RecursionAdmissibilityField assigns zero weight beyond the declared maximum depth for a given session.

### Lens R - Fractal

#### Facet 1 - Objects

- `Ch16<0033>.R1.a`: `RecursiveVerifier` — A VerificationLayer that contains an embedded VerificationLayer, enabling verification of verification itself at arbitrary nesting depths.
- `Ch16<0033>.R1.b`: `FractalReplay` — A replay structure where each ReplaySurface contains sub-replays of its own verification steps, creating a self-documenting verification cascade.
- `Ch16<0033>.R1.c`: `SelfHonestSurface` — A HonestyMeter that applies its own measurement protocol to itself, producing a meta-honesty score that quantifies the reliability of the honesty measurement.
- `Ch16<0033>.R1.d`: `DepthBoundedVerificationTree` — A tree-structured verification graph where each node is a RecursiveVerifier and the tree depth is bounded by the RecursionGuard.

#### Facet 2 - Laws

- `Ch16<0033>.R2.a`: `RecursiveVerificationLaw` — A RecursiveVerifier at depth n must produce the same verification result as a non-recursive verifier applied to the same computation at depth n.
- `Ch16<0033>.R2.b`: `FractalReplayLaw` — Every sub-replay within a FractalReplay must independently satisfy the ReplayDeterminismLaw, and their collective result must equal the parent replay's result.
- `Ch16<0033>.R2.c`: `SelfHonestyLaw` — A SelfHonestSurface's meta-honesty score must be at least as high as any module-level honesty score it reports; a less-honest meter cannot certify more-honest modules.
- `Ch16<0033>.R2.d`: `DepthTerminationLaw` — Every DepthBoundedVerificationTree must terminate at the declared depth bound with a leaf certificate; infinite verification descent is structurally prohibited.

#### Facet 3 - Constructions

- `Ch16<0033>.R3.a`: `MetaVerifier` — A construction that instantiates a RecursiveVerifier at each nesting depth and cross-checks their results against the non-recursive baseline.
- `Ch16<0033>.R3.b`: `FractalReplayEngine` — A construction that executes a FractalReplay by decomposing it into independent sub-replays, running them in parallel, and reconciling their results.
- `Ch16<0033>.R3.c`: `SelfHonestyCalibrator` — A construction that periodically measures the SelfHonestSurface against known-honest reference modules to maintain calibration of the meta-honesty score.
- `Ch16<0033>.R3.d`: `VerificationTreePruner` — A construction that detects when a DepthBoundedVerificationTree has reached its depth limit and emits leaf certificates without further recursion.

#### Facet 4 - Certificates

- `Ch16<0033>.R4.a`: `RecursiveVerificationCert` — A depth-indexed proof that a RecursiveVerifier produced results consistent with non-recursive verification at every nesting level.
- `Ch16<0033>.R4.b`: `FractalReplayCert` — A composite certificate containing all sub-replay certificates and proving their reconciliation into the parent replay's verified result.
- `Ch16<0033>.R4.c`: `SelfHonestyCert` — A calibration-anchored certificate proving that a SelfHonestSurface's meta-honesty score exceeds all module-level scores it has certified.
- `Ch16<0033>.R4.d`: `VerificationTreeTerminationCert` — A proof that a DepthBoundedVerificationTree terminated at the declared depth with valid leaf certificates at every terminal node.
