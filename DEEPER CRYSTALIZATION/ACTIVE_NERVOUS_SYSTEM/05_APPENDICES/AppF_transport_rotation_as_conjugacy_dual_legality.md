# AppF - Transport, Rotation-as-Conjugacy, DUAL Legality

Routing role: Transport legality, dual routes, conjugacy bridges, and lawful movement across charts.
Source: Rosetta Seed Artifact (lens transport equations, sprouting laws, and chart conjugacy)

## Compressed crystal tile

### Lens S

#### Facet 1 - Objects

- `AppF.S1.a`: `LensChart` — An admissible coordinate chart `T(x)` that transforms one mathematical domain into another. The four canonical charts: `T_ln(x) = ln(x)` (e-chart), `T_φ(x) = log_φ(x)` (φ-chart), `T_θ(x) = θ` (i-chart/phase), `T_arc(x) = arc angle` (π-chart). Each chart makes a specific seed's behavior into simple translation.
- `AppF.S1.b`: `ConjugacyBridge` — The universal transport operator `f_T = T⁻¹ ∘ f ∘ T` that moves any lawful operation between charts. This is Rosetta Seed FE-IV, the fourth fundamental equation.
- `AppF.S1.c`: `TransportedArithmetic` — The chart-specific arithmetic operators: `x ⊕_T y = T⁻¹(T(x) + T(y))` (transported addition) and `x ⊗_T y = T⁻¹(T(x) · T(y))` (transported multiplication). These make "alien math" lawful.
- `AppF.S1.d`: `DualRoute` — The paired positive/anti-constant transport: every lens chart has a forward route (constant family) and a backward route (anti-constant family). `φ ↔ 1/φ`, `e ↔ 1/e`, `i ↔ −i`, `π ↔ 1/π`.

#### Facet 2 - Laws

- `AppF.S2.a`: `ConjugacyTransportLaw` — Any lawful operation must be stored as a seeded transported form in some chart where it is simplest, then pulled back: `f_T = T⁻¹ ∘ f ∘ T`. Proof in the native chart, transport back.
- `AppF.S2.b`: `TransportedArithmeticLaw` — `x ⊕_T y = T⁻¹(T(x) + T(y))` preserves the additive seed's structure in chart-space. A unit additive step in T-space becomes the seed's constant operation in native space.
- `AppF.S2.c`: `DualLegalityLaw` — Every forward transport has a lawful inverse transport. If `T(φx) = T(x) + π/2`, then `T(x/φ) = T(x) − π/2`. The dual route is always admissible when the forward route is.
- `AppF.S2.d`: `CorridorGateLaw` — Division transport is only legal when the inverse corridor exists. `[a] ⊘_Λ [b]` requires `gcd(b,N) = 1`. Division by zero is rotated to the shadow/renormalized corridor, never executed directly.

#### Facet 3 - Constructions

- `AppF.S3.a`: `ChartSprouter` — Given a cardinal seed and a target constant, constructs the lens chart `T` that transforms the cardinal into the constant's domain. Plus → e via `T = ln`, Plus → φ via `T = log_φ`, Plus → i via `T = phase`, Plus → π via `T = arc`.
- `AppF.S3.b`: `ConjugacyComposer` — Composes two chart transports `T₁, T₂` into a single bridge: `f_{T₁∘T₂} = T₂⁻¹ ∘ T₁⁻¹ ∘ f ∘ T₁ ∘ T₂`. Enables multi-hop chart transport.
- `AppF.S3.c`: `AntiConstantGenerator` — Given a constant family, generates the anti-constant family by applying the inverse chart: `φ → 1/φ`, `e → 1/e`, `i → −i`, `π → 1/π`. The subtractive and divisive seeds sprout naturally into these.
- `AppF.S3.d`: `CorridorValidator` — Tests whether a transport corridor is admissible: checks invertibility of the chart at the target point, verifies the denominator is nonzero, confirms the lens chart has a well-defined pullback.

#### Facet 4 - Certificates

- `AppF.S4.a`: `ChartAdmissibilityCert` — Proves: lens chart `T` is invertible, domain/range well-defined, transported arithmetic preserves the seed's algebraic identity.
- `AppF.S4.b`: `ConjugacyPreservationCert` — Proves: `f_T = T⁻¹ ∘ f ∘ T` correctly transports the seed operation, replay in native chart matches replay in transported chart.
- `AppF.S4.c`: `DualRouteCert` — Proves: forward and backward routes are both admissible, anti-constant family correctly generated, no corridor violation in either direction.
- `AppF.S4.d`: `CorridorIntegrityCert` — Proves: corridor test passed (or recorded failure), no division by zero attempted, shadow/renormalized resolution used when gate is closed.

### Lens F

#### Facet 1 - Objects

- `AppF.F1.a`: `PhiQuarterTurnResonance` — The master harmonic of the φ-lens: `T(φx) = T(x) + π/2` where `T(x) = (π/2)·log_φ(x)`. Scaling by φ in native space becomes a quarter-turn translation in chart space. This is the deepest Rosetta equation: scale becomes phase, multiplication becomes translation, recursion becomes rotation.
- `AppF.F1.b`: `ExponentialFlowHarmonic` — The e-lens harmonic: `ln(x) ↦ ln(x) + 1 ⟺ x ↦ ex`. Addition in ln-space becomes multiplication by e in native space. The continuous compounding wave.
- `AppF.F1.c`: `RotationPhaseHarmonic` — The i-lens harmonic: `θ ↦ θ + π/2 ⟺ z ↦ iz`. Additive phase increment becomes quarter-turn rotation. Generates the 4-cycle `1 → i → −1 → −i → 1`.
- `AppF.F1.d`: `GeometricClosureHarmonic` — The π-lens harmonic: `θ ↦ θ + δθ, Σδθ → π, 2π`. Additive arc accumulation becomes circular/polygonal closure. The polygon-to-circle limit.

#### Facet 2 - Laws

- `AppF.F2.a`: `QuarterTurnScalingLaw` — `T(φx) = T(x) + π/2` is exact; scaling by φ in native space is exactly a quarter-turn in chart space. Conversely, `T⁻¹(θ + kπ/2) = φ^(2θ/π) · φ^k` generates exact preimage ladders.
- `AppF.F2.b`: `ExponentialCompoundingLaw` — A unit additive step in ln-space is exactly multiplication by e: `ln(x) + 1 = ln(ex)`. Growth, decay, compounding, and semigroup flow all reduce to this single transport.
- `AppF.F2.c`: `PhaseCycleLaw` — Quarter-turn phase increment generates the cyclic group `{1, i, −1, −i}`. Four quarter-turns return to identity. Anti-aligned phase (`Δθ = π`) produces exact subtraction: `|ψ₁+ψ₂|² = (a−b)²`.
- `AppF.F2.d`: `PolygonClosureLaw` — Additive arc accumulation toward π and 2π is the limit of polygon approximation. `π = lim n·sin(π/n)` is the closure equation.

#### Facet 3 - Constructions

- `AppF.F3.a`: `PhiLadderGenerator` — Generates the complete preimage ladder from the φ-lens: `x_k = T⁻¹(θ + kπ/2) = φ^(2θ/π) · φ^k`. Produces entire constant families by transport from a simple chart-space lattice.
- `AppF.F3.b`: `ExponentialFlowGenerator` — Generates the exponential flow family: `x(t) = x₀ · e^t` via continuous transport in ln-chart. The semigroup of growth operators.
- `AppF.F3.c`: `FourierKernelGenerator` — Generates the Fourier basis `{e^{inθ}}` from repeated phase transport. Spectral decomposition as iterated quarter-turn composition.
- `AppF.F3.d`: `PolygonClosureGenerator` — Generates the polygon sequence `n·sin(π/n)` converging to π. Leibniz accumulation, orthogonality normalization, and curvature integral.

#### Facet 4 - Certificates

- `AppF.F4.a`: `PhiQuarterTurnCert` — Receipt proving `T(φx) = T(x) + π/2` holds exactly, preimage ladder correctly generated, no drift or rounding error in chart transport.
- `AppF.F4.b`: `ExponentialFlowCert` — Receipt proving ln-chart transport correct, compounding law preserved, semigroup property maintained.
- `AppF.F4.c`: `PhaseCycleCert` — Receipt proving four quarter-turns return to identity, anti-aligned phase produces exact subtraction, no phase drift.
- `AppF.F4.d`: `PolygonClosureCert` — Receipt proving polygon sequence converges to π within declared tolerance, closure law satisfied.

### Lens C

#### Facet 1 - Objects

- `AppF.C1.a`: `TransportConfidenceField` — The probabilistic admissibility surface over all available lens charts, representing the system's confidence that each chart transport will preserve the seed's truth.
- `AppF.C1.b`: `ChartSelectionDistribution` — The probability distribution over available charts for a given operation, reflecting which chart is most likely to produce the simplest or most reliable transport.
- `AppF.C1.c`: `CorridorRiskSurface` — The probability that a given transport corridor will fail (inverse doesn't exist, denominator zero, chart singular). The ÷-seed's admissibility test expressed probabilistically.
- `AppF.C1.d`: `DualRouteBalanceField` — The ratio of forward-to-backward transport reliability, measuring how symmetric the dual legality is for a given seed-constant pair.

#### Facet 2 - Laws

- `AppF.C2.a`: `TransportConfidenceLaw` — Transport confidence must increase monotonically as charts are verified; a failed transport attempt reduces confidence in the specific corridor without affecting other corridors.
- `AppF.C2.b`: `ChartSelectionLaw` — The optimal chart for a given operation is the one that minimizes transported complexity; chart selection must consider all four lens options before committing.
- `AppF.C2.c`: `CorridorRiskBoundLaw` — Corridor risk must be bounded below a declared threshold before transport is attempted; exceeding threshold triggers shadow/renormalized resolution.
- `AppF.C2.d`: `DualRouteSymmetryLaw` — If forward transport has confidence p, backward transport must have confidence ≥ p·(1/φ); asymmetric dual routes indicate structural defect.

#### Facet 3 - Constructions

- `AppF.C3.a`: `ConfidenceUpdater` — Updates transport confidence field after each successful or failed chart transport, using Bayesian accumulation.
- `AppF.C3.b`: `OptimalChartSelector` — Selects the lens chart that minimizes transported complexity for a given seed×element×level cell.
- `AppF.C3.c`: `RiskAssessor` — Evaluates corridor risk before transport attempt; triggers shadow resolution when risk exceeds threshold.
- `AppF.C3.d`: `DualRouteBalancer` — Monitors forward/backward route balance; flags asymmetric pairs for structural investigation.

#### Facet 4 - Certificates

- `AppF.C4.a`: `TransportConfidenceCert` — Receipt proving confidence field updated correctly after transport, no retroactive modification.
- `AppF.C4.b`: `ChartSelectionCert` — Receipt proving optimal chart was selected from all four options, complexity comparison documented.
- `AppF.C4.c`: `CorridorRiskCert` — Receipt proving risk assessment performed before transport, threshold check documented, shadow resolution used if needed.
- `AppF.C4.d`: `DualRouteBalanceCert` — Receipt proving dual route symmetry within declared tolerance, asymmetric pairs flagged.

### Lens R

#### Facet 1 - Objects

- `AppF.R1.a`: `RecursiveChartNesting` — The self-similar structure of chart transport: a chart can be applied to itself recursively, producing nested transport at every scale. `T ∘ T ∘ ... ∘ T` generates depth-indexed lens families.
- `AppF.R1.b`: `ScaleTransportLattice` — The lattice of scale-transport relationships: `x_k = φ^k · x_0` in native space corresponds to uniform translation in chart space. The fractal backbone of the φ-lens.
- `AppF.R1.c`: `LogPeriodicSpiral` — The self-similar spiral generated by combining φ-scaling with phase rotation: `log-periodic oscillation = 2πk/log(φ)`. The fractal time unit of the system.
- `AppF.R1.d`: `RGTransportChain` — The renormalization group flow as iterated chart transport: each RG step is a chart application that moves from one scale to the next, with the fixed point as the attractor.

#### Facet 2 - Laws

- `AppF.R2.a`: `RecursiveChartNestingLaw` — Nested chart transport must preserve the seed's algebraic identity at every depth; `T^n(x)` must remain well-defined and invertible for all declared n.
- `AppF.R2.b`: `ScaleTransportLatticeLaw` — The lattice `{φ^k · x_0}` is the unique self-similar transport lattice generated by the φ-lens; any other lattice with the same self-similarity must be isomorphic.
- `AppF.R2.c`: `LogPeriodicLaw` — Log-periodic oscillations with period `2π/log(φ)` are the fractal time signature of the φ-lens; any departure from this period indicates a different scaling constant.
- `AppF.R2.d`: `RGFixedPointLaw` — The RG transport chain converges to a fixed point iff the contraction ratio is bounded by `1/φ`; universality class emergence requires repeated scale composition.

#### Facet 3 - Constructions

- `AppF.R3.a`: `NestedChartExpander` — Recursively applies chart transport to generate depth-indexed lens families; computes `T^n(x)` for declared depth n.
- `AppF.R3.b`: `ScaleLatticeBuilder` — Builds the self-similar transport lattice `{φ^k · x_0}` from the φ-lens chart; generates entire constant families.
- `AppF.R3.c`: `LogPeriodicDetector` — Detects log-periodic oscillations in data and identifies the governing scaling constant by period analysis.
- `AppF.R3.d`: `RGFlowIterator` — Iterates the RG transport chain toward fixed point; detects convergence, universality class, and contraction ratio.

#### Facet 4 - Certificates

- `AppF.R4.a`: `NestedChartCert` — Receipt proving recursive chart nesting preserved seed identity at every depth, no degeneration.
- `AppF.R4.b`: `ScaleLatticeCert` — Receipt proving transport lattice correctly generated, self-similarity verified, isomorphism to canonical lattice established.
- `AppF.R4.c`: `LogPeriodicCert` — Receipt proving log-periodic period matches `2π/log(φ)` within declared tolerance, scaling constant identified.
- `AppF.R4.d`: `RGConvergenceCert` — Receipt proving RG flow converged to fixed point, contraction ratio bounded by `1/φ`, universality class declared.
