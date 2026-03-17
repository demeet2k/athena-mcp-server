# AppI - Corridors and Truth Lattice

Routing role: Truth-typed corridor contracts, admissibility budgets, and abstain-over-guess discipline.
Source: Rosetta Seed Artifact — ÷-seed (corridor gating, admissibility), −-seed (zero construction, equality detection), and the fundamental equation FE-IV (lens transport law)
Station: `NXT::R01::M40::AppI`

## Compressed crystal tile

### Lens S

#### Facet 1 - Objects

- `AppI.S1.a`: `AdmissibilityCorridor` — A certified pathway through which an operation is lawful. The ÷-seed's gate condition generalized: every operation has a corridor, and the corridor must be open before execution. `gcd(b,N)=1` is the lattice corridor; denominator ≠ 0 is the continuous corridor; inverse exists is the general corridor.
- `AppI.S1.b`: `TruthTag` — A typed truth label from the lattice `{CANON, NEAR, AMBIG, FRONTIER, VOID}`. Each tag declares the epistemic status of a claim. CANON = proven. NEAR = within declared tolerance. AMBIG = unresolved. FRONTIER = conjectured. VOID = unknown/collapsed.
- `AppI.S1.c`: `ZeroSetDetector` — The −-seed's zero-construction law applied to truth: `Z₀(F,G) = Z(F−G)`. Two claims are equal (in the same truth corridor) iff their difference is zero. Equality detection by subtraction.
- `AppI.S1.d`: `CorridorBudget` — The resource budget for corridor testing. Each corridor test consumes resources (computation, evidence, certification). The budget bounds how many corridor tests can be performed before decision must be made or abstained.

#### Facet 2 - Laws

- `AppI.S2.a`: `CorridorFirstLaw` — No operation executes before its corridor is tested. The ÷-seed's gate law: "test gate → construct inverse → form quotient." Corridor testing precedes action, always.
- `AppI.S2.b`: `TruthMonotonicityLaw` — Truth tags may only be promoted monotonically: `VOID → FRONTIER → AMBIG → NEAR → CANON`. Demotion requires explicit revocation with evidence. No silent downgrade.
- `AppI.S2.c`: `AbstainOverGuessLaw` — When corridor test is inconclusive and budget is exhausted, the system must abstain rather than guess. Abstention is tagged `AMBIG` and queued for future evidence. Guessing is a corridor violation.
- `AppI.S2.d`: `CorridorBudgetExhaustionLaw` — When budget is exhausted, all pending corridor tests are deferred. Deferred tests are recorded with their partial evidence. No corridor test is abandoned — it is suspended.

#### Facet 3 - Constructions

- `AppI.S3.a`: `CorridorTester` — Tests whether a corridor is open for a given operation. Returns: `OPEN` (proceed), `CLOSED` (abort), or `AMBIG` (insufficient evidence). Source: ÷-seed's gate condition.
- `AppI.S3.b`: `TruthPromoter` — Promotes a truth tag from one level to the next when sufficient evidence is provided. Enforces monotonicity. Records promotion receipt.
- `AppI.S3.c`: `AbstentionRecorder` — Records an abstention decision with partial evidence, reason for abstention, and re-entry conditions. The claim stays tagged `AMBIG` until new evidence arrives.
- `AppI.S3.d`: `CorridorBudgetManager` — Tracks corridor budget consumption. Triggers abstention when budget exhausted. Allocates budget to highest-priority corridor tests first.

#### Facet 4 - Certificates

- `AppI.S4.a`: `CorridorOpenCert` — Receipt proving corridor is open: inverse exists, denominator nonzero, chart invertible, transport admissible. The gate witness.
- `AppI.S4.b`: `TruthPromotionCert` — Receipt proving truth tag promoted with sufficient evidence. Records old tag, new tag, evidence set, and promotion timestamp.
- `AppI.S4.c`: `AbstentionCert` — Receipt proving abstention was lawful: corridor test inconclusive, budget exhausted, partial evidence preserved, re-entry conditions declared.
- `AppI.S4.d`: `CorridorBudgetCert` — Receipt proving budget correctly tracked, no over-expenditure, priority allocation documented.

### Lens F

#### Facet 1 - Objects

- `AppI.F1.a`: `CorridorFlow` — The continuous flow of operations through open corridors. When corridors are open, operations flow smoothly. When corridors close, flow redirects to alternative corridors or halts.
- `AppI.F1.b`: `TruthWave` — The propagation of truth-tag promotions through the system. A promotion at one node creates a wave of potential promotions at connected nodes. The harmonic of evidence propagation.
- `AppI.F1.c`: `AdmissibilityGradient` — The continuous field measuring how close each operation is to its corridor boundary. High gradient = close to corridor edge = sensitive to perturbation.
- `AppI.F1.d`: `CorridorPhaseTransition` — The abrupt transition when a corridor changes from OPEN to CLOSED (or vice versa). The ÷-seed's singularity: division by zero is the corridor's phase transition point.

#### Facet 2 - Laws

- `AppI.F2.a`: `CorridorFlowContinuityLaw` — Corridor flow must be continuous: no operation may jump from one corridor to another without passing through a declared transition point.
- `AppI.F2.b`: `TruthWaveDampingLaw` — Truth waves must be damped: a single promotion cannot trigger unlimited cascade promotions. Propagation depth is bounded by evidence budget.
- `AppI.F2.c`: `AdmissibilityGradientLaw` — Operations with high admissibility gradient (near corridor edge) must be flagged as sensitive. Sensitive operations require additional certification.
- `AppI.F2.d`: `CorridorTransitionLaw` — Corridor phase transitions must be handled by rotation to shadow/renormalized corridor, not by direct execution at the singularity. The ÷-seed's anti-singularity doctrine.

#### Facet 3 - Constructions

- `AppI.F3.a`: `CorridorFlowRouter` — Routes operations through open corridors. Detects closed corridors and redirects flow to alternatives.
- `AppI.F3.b`: `TruthWavePropagator` — Propagates truth promotions through the system with bounded depth. Tracks which promotions triggered which downstream promotions.
- `AppI.F3.c`: `AdmissibilityGradientComputer` — Computes how close each operation is to its corridor boundary. Flags sensitive operations.
- `AppI.F3.d`: `ShadowCorridorRotator` — When a corridor closes, rotates the operation to a shadow/renormalized corridor where it can be executed lawfully. The ÷-seed's singularity resolution.

#### Facet 4 - Certificates

- `AppI.F4.a`: `CorridorFlowContinuityCert` — Receipt proving operation flow was continuous, no illegal corridor jumps.
- `AppI.F4.b`: `TruthWavePropagationCert` — Receipt proving truth wave correctly propagated with bounded depth, cascade trail documented.
- `AppI.F4.c`: `AdmissibilityGradientCert` — Receipt proving gradient correctly computed, sensitive operations flagged, additional certification applied where needed.
- `AppI.F4.d`: `ShadowCorridorRotationCert` — Receipt proving singularity resolved by rotation to shadow corridor, not by direct execution. Shadow corridor documented.

### Lens C

#### Facet 1 - Objects

- `AppI.C1.a`: `CorridorOpenProbability` — The probability that a corridor will be found open when tested. Bayesian estimate from prior corridor tests and system state.
- `AppI.C1.b`: `TruthConfidenceField` — The probability distribution over truth tags for each claim. Not a single tag but a distribution: `P(CANON) = 0.7, P(NEAR) = 0.2, P(AMBIG) = 0.1`.
- `AppI.C1.c`: `EvidenceSufficiencyScore` — The probability that current evidence is sufficient for truth promotion. Below threshold = abstain. Above threshold = promote.
- `AppI.C1.d`: `CorridorRiskField` — The probability of corridor failure (closure, singularity, budget exhaustion) for each pending operation. High risk = preemptive routing to alternatives.

#### Facet 2 - Laws

- `AppI.C2.a`: `CorridorProbabilityUpdateLaw` — Corridor open probability must be updated after every test (Bayesian). Stale probabilities are not reusable beyond declared expiry.
- `AppI.C2.b`: `TruthConfidenceLaw` — Truth confidence must be computed from evidence, not from prior conviction. Prior-dominated confidence is flagged as insufficiently evidenced.
- `AppI.C2.c`: `EvidenceSufficiencyLaw` — Evidence sufficiency score must exceed declared threshold before truth promotion. Threshold is set per truth-tag level (higher level = higher threshold).
- `AppI.C2.d`: `CorridorRiskBoundLaw` — Operations with corridor risk exceeding threshold must be routed to alternative corridors or deferred. No high-risk corridor execution without explicit override.

#### Facet 3 - Constructions

- `AppI.C3.a`: `CorridorProbabilityUpdater` — Updates corridor open probability after each test using Bayesian accumulation.
- `AppI.C3.b`: `TruthConfidenceComputer` — Computes truth confidence distribution from evidence set. Reports distribution, not point estimate.
- `AppI.C3.c`: `EvidenceSufficiencyEvaluator` — Evaluates evidence sufficiency score against declared threshold for each truth-tag level.
- `AppI.C3.d`: `CorridorRiskRouter` — Routes operations based on corridor risk. High-risk operations deferred or rerouted. Threshold checked before execution.

#### Facet 4 - Certificates

- `AppI.C4.a`: `CorridorProbabilityUpdateCert` — Receipt proving Bayesian update correct, no stale probabilities used, expiry respected.
- `AppI.C4.b`: `TruthConfidenceComputationCert` — Receipt proving confidence computed from evidence, distribution documented, prior influence bounded.
- `AppI.C4.c`: `EvidenceSufficiencyCert` — Receipt proving sufficiency score above threshold for declared truth-tag level, evidence set documented.
- `AppI.C4.d`: `CorridorRiskRoutingCert` — Receipt proving all high-risk operations correctly routed, threshold checked, overrides documented.

### Lens R

#### Facet 1 - Objects

- `AppI.R1.a`: `RecursiveCorridorNesting` — Self-similar corridor structure: each corridor at one scale contains sub-corridors at the next scale down. The admissibility test at each depth has its own gate condition.
- `AppI.R1.b`: `FractalTruthLattice` — The truth lattice is self-similar: `{CANON, NEAR, AMBIG, FRONTIER, VOID}` exists at every recursion depth. Truth at depth n is independent of truth at depth n−1 but must be consistent with it.
- `AppI.R1.c`: `RecursiveEvidenceAccumulation` — Evidence accumulates recursively: evidence at depth n feeds into evidence evaluation at depth n+1. Each level builds on the previous level's certified evidence.
- `AppI.R1.d`: `CorridorScaleBridge` — The bridge between corridor admissibility at one scale and at the next. The ÷-seed's gate condition transported through the φ-lens: admissibility thresholds scale by φ.

#### Facet 2 - Laws

- `AppI.R2.a`: `RecursiveCorridorConsistencyLaw` — Corridor status at depth n must be consistent with corridor status at depth n−1. A corridor cannot be open at one depth and closed at the same depth's parent.
- `AppI.R2.b`: `FractalTruthConsistencyLaw` — Truth tags at depth n must not contradict truth tags at depth n−1. Promotion at one depth requires consistency check at adjacent depths.
- `AppI.R2.c`: `EvidenceAccumulationDepthLaw` — Evidence accumulated at depth n is valid as input at depth n+1 only if it carries a depth-n certification. Uncertified evidence cannot propagate upward.
- `AppI.R2.d`: `CorridorScalingLaw` — Admissibility thresholds scale by φ between levels: level n+1 threshold = φ × level n threshold. This ensures corridors tighten as governance deepens.

#### Facet 3 - Constructions

- `AppI.R3.a`: `RecursiveCorridorTester` — Tests corridor admissibility at each recursion depth. Reports per-depth status and consistency across depths.
- `AppI.R3.b`: `FractalTruthChecker` — Checks truth-tag consistency across recursion depths. Reports contradictions.
- `AppI.R3.c`: `RecursiveEvidenceAggregator` — Aggregates evidence from depth n into depth n+1 inputs. Requires depth-n certification before propagation.
- `AppI.R3.d`: `CorridorScaleBridgeBuilder` — Constructs the ScaleBridge between corridor admissibility at two scales using φ-scaling of thresholds.

#### Facet 4 - Certificates

- `AppI.R4.a`: `RecursiveCorridorConsistencyCert` — Receipt proving corridor consistent across all depths, no open/closed contradictions.
- `AppI.R4.b`: `FractalTruthConsistencyCert` — Receipt proving truth tags consistent across all recursion depths, no contradictions.
- `AppI.R4.c`: `RecursiveEvidenceAccumulationCert` — Receipt proving evidence properly accumulated across depths, all depth-n inputs certified.
- `AppI.R4.d`: `CorridorScaleBridgeCert` — Receipt proving admissibility thresholds scale by φ between levels, ScaleBridge correctly constructed.
