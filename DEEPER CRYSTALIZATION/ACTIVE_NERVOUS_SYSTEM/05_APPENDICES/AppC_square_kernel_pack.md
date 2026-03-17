# AppC - Square Kernel Pack

Routing role: Discrete kernels, indexing packs, chapter-tile schedules, and crystal algebra.
Source: Rosetta Seed Artifact (procedural generation from 4 cardinal seeds × Square lens)

## Compressed crystal tile

### Lens S

#### Facet 1 - Objects

- `AppC.S1.a`: `SuccessorKernel` — The primal discrete increment `n ↦ n+1`, generator of all counting, the additive seed's Square×Earth×L0 cell. Source: ROSETTA[+].Square.Earth.L0
- `AppC.S1.b`: `DifferenceKernel` — The discrete difference operator `Δ(F,G) = F − G`, constructor of zeros, fixed points, and equality detection. Source: ROSETTA[−].Square.Earth.L0 (decrement) and ROSETTA[−].Square.Air.L0 (difference operator F−G)
- `AppC.S1.c`: `ProductKernel` — The Cartesian product `A × B → |A||B|` and lattice gear-meshing `[a] ⊗_Λ [b] = [ab]`, the multiplicative seed's discrete binding primitive. Source: ROSETTA[×].Square.Earth.L0
- `AppC.S1.d`: `QuotientKernel` — The corridor-gated quotient `[a] ⊘_Λ [b] = [a] ⊗_Λ [b]⁻¹` only when `gcd(b,N) = 1`, the divisive seed's admissibility-conditioned inverse. Source: ROSETTA[÷].Square.Water.L0

#### Facet 2 - Laws

- `AppC.S2.a`: `SuccessorWellOrderLaw` — The successor function is well-defined on every ordered set; domain closed under increment; one-step difference preserved; replay deterministic. Certificate: `cert₊`
- `AppC.S2.b`: `ZeroConstructionLaw` — `Z₀(F,G) = Z(F−G)`: subtraction is the primitive of zero construction. Fixed points via `Fix(f) = Z(f−id)`, periods via `Per_k(f) = Z(f^k−id)`. The entire zero-ontology is built from difference.
- `AppC.S2.c`: `GearMeshingLaw` — In the Λ-lattice: `[a] ⊗_Λ [b] = [ab]`, units form `(Z_N)×`, divisibility and factorization are native multiplicative geometry. Multiplication is scale × rotation in Θ-space: magnitudes multiply, phases add.
- `AppC.S2.d`: `InverseCertificateLaw` — Division is only legal when an inverse certificate exists: `ax + Ny = 1 ⟹ a⁻¹ ≡ x (mod N)` via Bézout/EEA. Division by zero is not executed directly; it is rotated to the shadow/renormalized corridor.

#### Facet 3 - Constructions

- `AppC.S3.a`: `BoundedDiscreteAccumulation` — Additive accumulation `n ↦ n+k` with lattice-shell growth by one cell layer. Builds exact proof-step extensions in discrete derivation chains. Source: ROSETTA[+].Square.Earth.L1–L3
- `AppC.S3.b`: `ModularSubtractionEngine` — Modular subtraction `[a] ⊖_Λ [b] = [a−b]` with additive inverses `−[a] = [N−a]`. Removes shell/cell layers, contracts finite-state systems under exact counting rules. Source: ROSETTA[−].Square.Earth.L1–L3
- `AppC.S3.c`: `FactorizationDiscovery` — Multiplication as repeated addition → exponentiation as repeated multiplication → factorization as hidden structure discovery → divisor/factor lattice as discrete multiplicative geometry. Source: ROSETTA[×].Square.Earth.L1–L3
- `AppC.S3.d`: `EuclideanDescentEngine` — Euclidean division `a = qb + r` → gcd as obstruction detector → factor lattice and divisor graph as quotient geometry → repeated division as contraction step in discrete dynamics. Source: ROSETTA[÷].Square.Earth.L0–L3

#### Facet 4 - Certificates

- `AppC.S4.a`: `SuccessorReplayCert` — Proves: successor well-defined, domain closed under increment, one-step difference preserved, replay deterministic. Minimal cert for the additive seed.
- `AppC.S4.b`: `ZeroWitnessCert` — Proves: difference well-defined, zero set correctly computed, fixed-point or period witness valid, replay of root/equality detection correct.
- `AppC.S4.c`: `ProductBindingCert` — Proves: chart admissibility, product well-defined in chart, count/phase/probability/recursion invariant preserved, factorization/binding/route composition replayable.
- `AppC.S4.d`: `BézoutInverseCert` — Proves: `gcd(b,N) = 1`, `x = b⁻¹ mod N` via EEA, `ax ≡ a/b (mod N)`. The gate witness for lawful division. When gcd fails, the cert records "no inverse corridor exists."

### Lens F

#### Facet 1 - Objects

- `AppC.F1.a`: `PartialSumOscillation` — The harmonic state of partial sums `S_n ↦ S_{n+1}` oscillating toward convergence, with additive refinement of partitions creating wave-like approach to limit. Source: ROSETTA[+].Square.Water
- `AppC.F1.b`: `RecurrenceDifferenceWave` — The oscillatory pattern of recovering prior terms by recurrence difference, with rational corrections between partial sums creating backward-retrieval harmonics. Source: ROSETTA[−].Square.Water
- `AppC.F1.c`: `IterationOrbit` — The periodic/quasi-periodic orbit structure of multiplicative dynamics on finite rings/groups, with fast powering as harmonic acceleration. Source: ROSETTA[×].Square.Fire
- `AppC.F1.d`: `QuotientDescentCycle` — The periodic contraction pattern of repeated Euclidean division, descending through spectral-radius reduction by lawful inverse scaling. Source: ROSETTA[÷].Square.Fire

#### Facet 2 - Laws

- `AppC.F2.a`: `AdditiveConvergenceLaw` — Partial sums converge when additive refinement of partitions satisfies Riemann-sum mesh enrichment; discrete-to-continuous bridge is lawful only via additive limit process.
- `AppC.F2.b`: `BackwardRetrievalLaw` — Backward polygon/partition refinement recovers discrete continuity by subtractive limit control; rational correction between partial sums is lawful.
- `AppC.F2.c`: `MultiplicativeOrbitLaw` — Repeated multiplication generates orbits on finite groups; discrete branching or state blowup through product iteration is bounded by group order.
- `AppC.F2.d`: `QuotientContractionLaw` — Divide-and-reduce algorithms contract; quotient as contraction step in discrete dynamics has spectral-radius reduction bounded by inverse scaling factor.

#### Facet 3 - Constructions

- `AppC.F3.a`: `RiemannSumEnrichment` — Additive refinement of Riemann-sum partitions by one interval, building discrete-to-continuous bridges via additive limit process. Source: ROSETTA[+].Square.Water.L2–L3
- `AppC.F3.b`: `InverseLimitRecovery` — Backward recurrence reconstructor: given `F_{n+1}` and `F_n`, recovers `F_{n-1} = F_{n+1} − F_n`. Discrete continuity recovered by subtractive limit control.
- `AppC.F3.c`: `FastPoweringEngine` — Repeated squaring algorithm: `x^n` computed in `O(log n)` multiplications. Generates multiplicative dynamical orbits on finite rings/groups.
- `AppC.F3.d`: `DivideAndReduceEngine` — Repeated Euclidean descent, spectral-radius reduction by lawful inverse scaling, quotient as contraction step.

#### Facet 4 - Certificates

- `AppC.F4.a`: `ConvergenceCert` — Receipt proving partial sums converged within declared tolerance after bounded additive steps.
- `AppC.F4.b`: `BackwardRetrievalCert` — Receipt proving backward recurrence correctly recovered prior state from current and successor values.
- `AppC.F4.c`: `OrbitCert` — Receipt proving multiplicative orbit completed or period detected within bounded iterations on declared group.
- `AppC.F4.d`: `EuclideanDescentCert` — Receipt proving Euclidean descent terminated with correct gcd, quotient chain valid, no corridor violation.

### Lens C

#### Facet 1 - Objects

- `AppC.C1.a`: `AdditiveCountingProcess` — One additional event in a counting process; additive update of empirical frequencies; occupancy growth in stochastic lattice models. Source: ROSETTA[+].Cloud.Earth
- `AppC.C1.b`: `InclusionExclusionSeed` — Remove overcount by inclusion-exclusion; coprime density normalization; discrete mass correction on infinite lattices. Source: ROSETTA[−].Cloud.Earth
- `AppC.C1.c`: `IndependentEventProduct` — `P(A ∩ B) = P(A)P(B)` for independent events; product sample spaces; multinomial structure as repeated multiplicative branching. Source: ROSETTA[×].Cloud.Earth
- `AppC.C1.d`: `CoprimeProbability` — Coprime probability `6/π²`; normalize count worlds into admissible probabilities; quotient of event space by symmetry class. Source: ROSETTA[÷].Cloud.Earth

#### Facet 2 - Laws

- `AppC.C2.a`: `BayesianAccumulationLaw` — Additive evidence accumulates in discrete Bayesian updates; empirical frequency converges by additive law of large numbers.
- `AppC.C2.b`: `ExclusionConvergenceLaw` — Inclusion-exclusion converges; exact event exclusion under finite probability law is lawful; coprime density normalization is the discrete mass correction.
- `AppC.C2.c`: `IndependenceProductLaw` — Independent observations multiply likelihoods; product measures compose; characteristic functions multiply under independence.
- `AppC.C2.d`: `NormalizationQuotientLaw` — Normalize heavy-tailed laws by dividing total mass; hazard/rate as reciprocal time law; rescale continuous density to integrate to one.

#### Facet 3 - Constructions

- `AppC.C3.a`: `BayesianAccumulator` — Additive evidence update: accumulates discrete Bayesian evidence, updates empirical frequencies, grows occupancy in stochastic lattice models.
- `AppC.C3.b`: `InclusionExclusionEngine` — Removes overcount via alternating sum; normalizes coprime density; applies discrete mass correction on infinite lattices.
- `AppC.C3.c`: `ProductMeasureBuilder` — Constructs product measures from independent marginals; factorizes likelihoods; builds multinomial structures by repeated multiplicative branching.
- `AppC.C3.d`: `DensityNormalizer` — Divides total mass by partition function; normalizes heavy-tailed or singular mass; rescales continuous density to integrate to one.

#### Facet 4 - Certificates

- `AppC.C4.a`: `BayesianAccumulationCert` — Receipt proving evidence updates were additive, frequencies converged, occupancy growth stayed within declared lattice bounds.
- `AppC.C4.b`: `ExclusionCert` — Receipt proving inclusion-exclusion terminated, no overcount remained, coprime density normalization correct.
- `AppC.C4.c`: `IndependenceCert` — Receipt proving marginals independent, product measure well-defined, characteristic function factorization correct.
- `AppC.C4.d`: `NormalizationCert` — Receipt proving total mass finite, density normalized to one, no corridor violation in reciprocal scaling.

### Lens R

#### Facet 1 - Objects

- `AppC.R1.a`: `FibonacciRecurrenceSeed` — `F_{n+1} = F_n + F_{n-1}` as the additive recursion seed; Beatty/Zeckendorf integer decomposition by additive recurrence. Source: ROSETTA[+].Fractal.Earth
- `AppC.R1.b`: `InverseRecurrenceSeed` — `F_{n-1} = F_{n+1} − F_n` as the subtractive recursion seed; backward step history recovery; recursive tree pruning. Source: ROSETTA[−].Fractal.Earth
- `AppC.R1.c`: `MultiplicativeRecurrenceSeed` — Powers and repeated branching; divisor trees and multiplicative partitions; self-similar count growth under repeated product. Source: ROSETTA[×].Fractal.Earth
- `AppC.R1.d`: `ContractionRecurrenceSeed` — `1/φ` as contraction ratio; backward recurrence as quotient of scale; prune recursive tree by lawful inverse branch factor. Source: ROSETTA[÷].Fractal.Earth

#### Facet 2 - Laws

- `AppC.R2.a`: `RecursiveAccretionLaw` — Additive recursion generates combinatorial branch count; scale-layer population follows additive shell law; Fibonacci ratio converges to φ.
- `AppC.R2.b`: `RecursivePruningLaw` — Subtractive recursion contracts; shell-wise contraction in a self-similar ladder is bounded by 1/φ; backward coding retrieves history from recursion.
- `AppC.R2.c`: `MultiplicativeScaleLaw` — Powers compose scale; shell population follows multiplicative scaling law; self-similar count growth is bounded by repeated product.
- `AppC.R2.d`: `InverseScaleLaw` — Contraction ratio 1/φ governs inverse scaling; contract shell ladder without erasing seed law; lawful inward fold rather than destructive collapse.

#### Facet 3 - Constructions

- `AppC.R3.a`: `FibonacciExpander` — Expands additive recursion seed: generates Fibonacci sequence, Zeckendorf representations, combinatorial branch counts, scale-layer populations.
- `AppC.R3.b`: `RecursivePruner` — Contracts recursive tree: backward step recovery, shell-wise contraction, history retrieval from growth by subtractive inverse recurrence.
- `AppC.R3.c`: `EulerProductBuilder` — Euler product as multiplicative encoding of additive data: spectral products over modes or primes, continued products, recursive filter banks.
- `AppC.R3.d`: `ScaleContractor` — Divides by scale to descend one RG layer: moves from blow-up to effective theory, quotients microscopic excess into macroscopic parameter.

#### Facet 4 - Certificates

- `AppC.R4.a`: `RecursionConvergenceCert` — Receipt proving recursive ratio converged to φ within declared depth, Zeckendorf decomposition unique, shell population correct.
- `AppC.R4.b`: `PruningIntegrityCert` — Receipt proving backward recurrence recovered correct history, no seed law erased, contraction bounded by 1/φ.
- `AppC.R4.c`: `EulerProductCert` — Receipt proving multiplicative encoding correct over declared primes/modes, product convergent, no missing factor.
- `AppC.R4.d`: `RGDescentCert` — Receipt proving scale descent lawful, effective theory valid, no forbidden infinity division, renormalization corridor intact.
