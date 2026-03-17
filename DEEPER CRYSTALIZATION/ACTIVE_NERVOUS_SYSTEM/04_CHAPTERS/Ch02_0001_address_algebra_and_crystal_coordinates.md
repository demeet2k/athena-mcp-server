# Ch02<0001> - Address Algebra and Crystal Coordinates

StationHeader: [Arc 0 | Rot 0 | Lane Me | w=1]
Workflow role: Canonical addressing, base-4 station coding, and identity-preserving lattice placement.
Primary hubs: AppA -> AppC -> AppB -> AppI -> AppM

## Routing context

- Orbit previous: `Ch01<0000>`
- Orbit next: `Ch03<0002>`
- Rail previous: `Ch20<0103>`
- Rail next: `Ch04<0003>`
- Arc previous: `Ch01<0000>`
- Arc next: `Ch03<0002>`
- Appendix couplings: `AppA, AppC, AppB, AppI, AppM`

## Source capsules

- `12_information_from_the_void_mani.md`
- `15_megalithic_tome_latent_tunneling_the_multi_scale_math_stack.md`
- `23_the_athena_framework_synthesis.md`
- `24_the_athena_framework_synthesis.md`
- `28_the_invisible_teacher_textbook.md`
- `29_the_invisible_teacher_textbook.md`

## Crystal tile

### Lens S - Square
`[⊙Z_1↔Z* | ○Arc 0 | ○Rot 0 | △Lane Me | ⧈View S | ω=1]`

#### Facet 1 - Objects

- `Ch02<0001>.S1.a` `StationCode` — The unique base-4 address assigned to every cell in the crystal lattice, serving as the canonical locator for all routing, retrieval, and replay operations.
- `Ch02<0001>.S1.b` `CoordinateAlgebra` — The algebraic system governing how station codes compose, decompose, and transform under lattice operations while preserving address uniqueness.
- `Ch02<0001>.S1.c` `RootCell` — The designated origin cell at address <0000> from which all coordinate paths are measured and to which every address resolves under null transformation.
- `Ch02<0001>.S1.d` `ReplayablePath` — An ordered sequence of station codes encoding a deterministic traversal through the lattice that any agent can reproduce from the path record alone.

#### Facet 2 - Laws

- `Ch02<0001>.S2.a` `Base4UniquenessLaw` — Every cell in the lattice must have exactly one base-4 station code, and no two distinct cells may share the same code.
- `Ch02<0001>.S2.b` `CoordinateCompositionLaw` — The composition of two coordinate transformations must yield a valid station code; the algebra is closed under composition and associative.
- `Ch02<0001>.S2.c` `RootCellLaw` — The root cell is the identity element of the coordinate algebra; composing any address with the root cell address returns the original address unchanged.
- `Ch02<0001>.S2.d` `PathReplayabilityLaw` — A path is valid if and only if replaying its station code sequence from the declared origin deterministically arrives at the declared destination.

#### Facet 3 - Constructions

- `Ch02<0001>.S3.a` `assignCode()` — Assigns a unique base-4 station code to a newly created cell by computing its position from the parent cell's code and the insertion index.
- `Ch02<0001>.S3.b` `composeCoordinate()` — Computes the composed station code resulting from applying a coordinate transformation to an existing address, verifying closure and uniqueness.
- `Ch02<0001>.S3.c` `bindRootCell()` — Designates a cell as the root by verifying it satisfies identity-element axioms and anchoring the coordinate origin to its address.
- `Ch02<0001>.S3.d` `replayPath()` — Re-executes a recorded path step by step from origin to destination, verifying that each intermediate station code exists and is reachable.

#### Facet 4 - Certificates

- `Ch02<0001>.S4.a` `Cert_Code_Unique` — Attests that a station code was assigned without collision, verified by a full-lattice uniqueness scan at assignment time.
- `Ch02<0001>.S4.b` `Cert_Coordinate_Valid` — Attests that a composed coordinate is a well-formed station code within the algebra's domain, with the composition trace attached.
- `Ch02<0001>.S4.c` `Cert_Root_Bound` — Attests that the designated root cell satisfies identity-element axioms and that all lattice addresses resolve correctly relative to it.
- `Ch02<0001>.S4.d` `Cert_Path_Replayable` — Attests that a recorded path was successfully replayed from origin to destination with every intermediate station verified.

### Lens F - Flower
`[⊙Z_1↔Z* | ○Arc 0 | ○Rot 0 | △Lane Me | ⧈View F | ω=1]`

#### Facet 1 - Objects

- `Ch02<0001>.F1.a` `CodeOrbital` — The cyclic orbit a station code traces through the base-4 digit space under successive rotational transformations of the coordinate system.
- `Ch02<0001>.F1.b` `AlgebraSymmetryGroup` — The group of all coordinate transformations that leave the algebraic structure invariant, defining the lattice's internal symmetry.
- `Ch02<0001>.F1.c` `RootCellHarmonic` — The fundamental frequency of the root cell viewed as the zero-mode of the lattice's coordinate wave function, anchoring all phase relations.
- `Ch02<0001>.F1.d` `PathPeriodicity` — The property that certain replayable paths form closed loops in the lattice, returning to their origin after a characteristic number of steps.

#### Facet 2 - Laws

- `Ch02<0001>.F2.a` `CodeOrbitalClosure` — Every station code orbital must be a finite closed cycle; open orbits indicate a malformed coordinate transformation.
- `Ch02<0001>.F2.b` `AlgebraSymmetryInvariance` — The coordinate algebra's laws must hold identically under every transformation in the symmetry group.
- `Ch02<0001>.F2.c` `RootHarmonicStability` — The root cell's harmonic mode must remain stable under all lattice perturbations that preserve the coordinate algebra's axioms.
- `Ch02<0001>.F2.d` `PathPeriodicityQuantization` — Path periods must be integer multiples of the lattice's fundamental cycle length; fractional periods are forbidden.

#### Facet 3 - Constructions

- `Ch02<0001>.F3.a` `traceCodeOrbital()` — Iteratively applies rotational coordinate transforms to a station code, recording the orbit until closure or cycle-length bound is reached.
- `Ch02<0001>.F3.b` `computeAlgebraSymmetry()` — Enumerates all coordinate transformations that leave the algebra invariant, constructing the full symmetry group with its multiplication table.
- `Ch02<0001>.F3.c` `resolveRootHarmonic()` — Computes the root cell's harmonic mode by spectral decomposition of the lattice's adjacency operator restricted to the coordinate basis.
- `Ch02<0001>.F3.d` `detectPathPeriodicity()` — Analyzes a replayable path for periodic structure, reporting the cycle length and the set of cells visited per period.

#### Facet 4 - Certificates

- `Ch02<0001>.F4.a` `Cert_Orbital_Closed` — Attests that a station code's orbital is a finite closed cycle with the exact period and member set recorded.
- `Ch02<0001>.F4.b` `Cert_Symmetry_Complete` — Attests that the computed symmetry group is complete, verified by checking closure, associativity, identity, and inverse axioms.
- `Ch02<0001>.F4.c` `Cert_Harmonic_Stable` — Attests that the root cell's harmonic mode was verified stable under a prescribed perturbation battery.
- `Ch02<0001>.F4.d` `Cert_Periodicity_Quantized` — Attests that a path's detected period is an exact integer multiple of the fundamental cycle length.

### Lens C - Cloud
`[⊙Z_1↔Z* | ○Arc 0 | ○Rot 0 | △Lane Me | ⧈View C | ω=1]`

#### Facet 1 - Objects

- `Ch02<0001>.C1.a` `CodeTruthDomain` — The subset of station codes whose assignment has been fully verified, distinguishing certified addresses from provisional or unverified ones.
- `Ch02<0001>.C1.b` `CoordinateAdmissibility` — The truth-valued predicate determining whether a coordinate composition yields an admissible result within the current lattice state.
- `Ch02<0001>.C1.c` `RootCellConfidence` — The degree of certainty that the designated root cell correctly satisfies all identity-element axioms, accounting for incomplete verification.
- `Ch02<0001>.C1.d` `PathUncertaintyBudget` — The accumulated uncertainty along a replayable path, summing per-step verification confidence into a total path reliability score.

#### Facet 2 - Laws

- `Ch02<0001>.C2.a` `CodeTruthExpansion` — The code truth domain can only grow as new verifications complete; revocation requires explicit falsification evidence.
- `Ch02<0001>.C2.b` `CoordinateAdmissibilityMonotonicity` — Once a coordinate composition is certified admissible, it remains admissible unless the underlying algebra axioms are revised.
- `Ch02<0001>.C2.c` `RootConfidenceFloor` — Root cell confidence must exceed a declared minimum threshold; falling below triggers re-verification before any dependent operations proceed.
- `Ch02<0001>.C2.d` `PathUncertaintyAccumulation` — Path uncertainty accumulates additively per step and must remain below the declared budget for the path to be considered replayable.

#### Facet 3 - Constructions

- `Ch02<0001>.C3.a` `expandCodeTruth()` — Extends the code truth domain by verifying a batch of provisional station codes against the uniqueness and well-formedness predicates.
- `Ch02<0001>.C3.b` `testCoordinateAdmissibility()` — Evaluates whether a proposed coordinate composition falls within the current admissibility boundary, returning a scored verdict.
- `Ch02<0001>.C3.c` `auditRootConfidence()` — Re-verifies the root cell's identity-element properties and updates the confidence score based on fresh axiom checks.
- `Ch02<0001>.C3.d` `computePathUncertainty()` — Walks a replayable path step by step, accumulating per-step uncertainty and comparing the total against the declared budget.

#### Facet 4 - Certificates

- `Ch02<0001>.C4.a` `Cert_Truth_Domain_Expanded` — Attests that a batch of station codes was verified and promoted from provisional to certified status.
- `Ch02<0001>.C4.b` `Cert_Admissibility_Tested` — Attests that a coordinate composition was tested and found admissible with the scored breakdown attached.
- `Ch02<0001>.C4.c` `Cert_Root_Confidence_Audited` — Attests that the root cell's confidence score was freshly computed and exceeds the minimum threshold.
- `Ch02<0001>.C4.d` `Cert_Path_Uncertainty_Within_Budget` — Attests that a path's total accumulated uncertainty falls within the declared budget, with per-step scores attached.

### Lens R - Fractal
`[⊙Z_1↔Z* | ○Arc 0 | ○Rot 0 | △Lane Me | ⧈View R | ω=1]`

#### Facet 1 - Objects

- `Ch02<0001>.R1.a` `CodeSelfSimilarity` — The property that the base-4 address structure at any scale mirrors the whole lattice's addressing scheme, enabling recursive address decomposition.
- `Ch02<0001>.R1.b` `AlgebraRecursion` — The recursive definition of the coordinate algebra where higher-order compositions are built from lower-order ones using the same rules.
- `Ch02<0001>.R1.c` `RootCellFractalSeed` — The root cell viewed as the fractal seed from which the entire lattice addressing scheme grows by recursive application of the base-4 expansion.
- `Ch02<0001>.R1.d` `PathCompression` — The minimal encoding of a replayable path that exploits self-similar sub-path patterns to achieve lossless compression.

#### Facet 2 - Laws

- `Ch02<0001>.R2.a` `CodeSelfSimilarityLaw` — Every sub-lattice addressed by a prefix of a station code must obey the same base-4 uniqueness and composition laws as the full lattice.
- `Ch02<0001>.R2.b` `AlgebraRecursionTermination` — Recursive coordinate compositions must terminate at a well-defined base case, preventing infinite expansion.
- `Ch02<0001>.R2.c` `RootSeedReproduction` — Applying the base-4 expansion rule to the root cell seed must reproduce the lattice's addressing scheme at each generation level.
- `Ch02<0001>.R2.d` `PathCompressionFidelity` — Compressed paths must decompress to exactly the original step sequence with no information loss or step reordering.

#### Facet 3 - Constructions

- `Ch02<0001>.R3.a` `verifyCodeSelfSimilarity()` — Recursively checks that each sub-lattice addressed by a station code prefix obeys the full algebra axioms, descending through all prefix levels.
- `Ch02<0001>.R3.b` `recurseAlgebra()` — Constructs higher-order coordinate compositions by recursive application of the base rules, tracking depth and verifying termination.
- `Ch02<0001>.R3.c` `growFromRootSeed()` — Generates the lattice addressing scheme by iteratively applying the base-4 expansion rule to the root cell seed across generation levels.
- `Ch02<0001>.R3.d` `compressPath()` — Identifies self-similar sub-path patterns within a replayable path and encodes them as recursive references, producing the minimal representation.

#### Facet 4 - Certificates

- `Ch02<0001>.R4.a` `Cert_Code_Self_Similar` — Attests that self-similarity verification passed at all prefix levels of the station code hierarchy.
- `Ch02<0001>.R4.b` `Cert_Recursion_Terminated` — Attests that recursive algebra composition reached a well-defined base case without exceeding the depth bound.
- `Ch02<0001>.R4.c` `Cert_Seed_Reproduced` — Attests that the root seed expansion reproduced the expected lattice addressing scheme at each verified generation level.
- `Ch02<0001>.R4.d` `Cert_Path_Compressed` — Attests that path compression was lossless, verified by round-trip decompression and step-by-step comparison.
