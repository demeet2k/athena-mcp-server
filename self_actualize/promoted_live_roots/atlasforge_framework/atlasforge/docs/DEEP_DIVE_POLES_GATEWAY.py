"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                      ║
║                           DEEP DIVE: FOUR POLES & GATEWAY ARCHITECTURE                                               ║
║                                                                                                                      ║
║                                    COMPLETE TECHNICAL SPECIFICATION                                                  ║
║                                                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                PART I: THE FOUR POLES IN DEPTH
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§1.1 THE PHILOSOPHICAL BASIS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Mathematics is not a monolith. It is a TENSION between fundamental modes of being:

    ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                               ║
    ║   THE FOUR FUNDAMENTAL TENSIONS:                                                                              ║
    ║                                                                                                               ║
    ║   1. DISCRETE vs CONTINUOUS                                                                                   ║
    ║      Can the world be counted, or does it flow?                                                               ║
    ║      Are there atoms, or is reality infinitely divisible?                                                     ║
    ║                                                                                                               ║
    ║   2. DETERMINISTIC vs STOCHASTIC                                                                              ║
    ║      Is the future fixed by the past, or is there irreducible randomness?                                     ║
    ║      Can we know exactly, or only probabilistically?                                                          ║
    ║                                                                                                               ║
    ║   3. LOCAL vs GLOBAL                                                                                          ║
    ║      Does truth depend on context, or is it universal?                                                        ║
    ║      Can parts determine wholes, or do wholes constrain parts?                                                ║
    ║                                                                                                               ║
    ║   4. FLAT vs HIERARCHICAL                                                                                     ║
    ║      Are all objects on the same level, or do levels stack?                                                   ║
    ║      Is self-reference possible, or is there always a meta-level?                                             ║
    ║                                                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

These tensions are not resolved—they are BALANCED. The Four Poles represent the pure extremes.


§1.2 POLE D: DISCRETE (Earth/α)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                                                 │
    │   POLE D: THE DISCRETE REALM                                                                                    │
    │                                                                                                                 │
    │   ESSENCE:      Counting, distinction, exact separation                                                         │
    │   ELEMENT:      Earth (solid, stable, bounded)                                                                  │
    │   GREEK:        α (alpha) - the first letter, the beginning                                                     │
    │   CONSTANT:     e (Euler's number) - discrete growth                                                            │
    │                                                                                                                 │
    │   MATHEMATICAL DOMAINS:                                                                                         │
    │   ├── Number Theory: ℕ, ℤ, primes, divisibility                                                                 │
    │   ├── Combinatorics: Counting, permutations, partitions                                                         │
    │   ├── Graph Theory: Vertices, edges, connectivity                                                               │
    │   ├── Logic: Propositions, truth values, proofs                                                                 │
    │   ├── Automata Theory: States, transitions, languages                                                           │
    │   └── Algebra: Groups, rings, fields (discrete structures)                                                      │
    │                                                                                                                 │
    │   CORE OPERATIONS:                                                                                              │
    │   ├── Successor: n ↦ n + 1                                                                                      │
    │   ├── Addition: (m, n) ↦ m + n                                                                                  │
    │   ├── Multiplication: (m, n) ↦ m × n                                                                            │
    │   ├── Modular arithmetic: operations mod N                                                                      │
    │   └── Recursion: f(n) defined in terms of f(n-1)                                                                │
    │                                                                                                                 │
    │   KEY INVARIANTS:                                                                                               │
    │   ├── Cardinality: |A| is preserved under bijections                                                            │
    │   ├── Parity: Even/odd preserved under certain operations                                                       │
    │   └── Divisibility: a|b relationships                                                                           │
    │                                                                                                                 │
    │   CERTIFICATE TYPES:                                                                                            │
    │   ├── Existence: Constructive witness (exhibit the object)                                                      │
    │   ├── Primality: Compositeness witness or primality proof                                                       │
    │   └── Equality: Reduction to normal form                                                                        │
    │                                                                                                                 │
    │   THE DISCRETE QUESTION:                                                                                        │
    │   "How many?" "Which one?" "Is this the same as that?"                                                          │
    │                                                                                                                 │
    └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

WHY e FOR DISCRETE?
    The number e = 2.71828... is the base of natural logarithms.
    It governs DISCRETE GROWTH:
    
    • Compound interest: (1 + 1/n)^n → e as n → ∞
    • Derangements: D_n/n! → 1/e as n → ∞
    • Factorial growth: n! ≈ √(2πn)(n/e)^n (Stirling)
    
    e connects discrete counting to continuous growth.


§1.3 POLE Ω: CONTINUOUS (Water/𝔇)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                                                 │
    │   POLE Ω: THE CONTINUOUS REALM                                                                                  │
    │                                                                                                                 │
    │   ESSENCE:      Flow, limits, infinite divisibility                                                             │
    │   ELEMENT:      Water (fluid, adaptive, unbounded)                                                              │
    │   GREEK:        𝔇 (mathfrak D) - domain, continuous                                                             │
    │   CONSTANT:     π (pi) - circular closure                                                                       │
    │                                                                                                                 │
    │   MATHEMATICAL DOMAINS:                                                                                         │
    │   ├── Real Analysis: ℝ, limits, continuity, derivatives                                                         │
    │   ├── Complex Analysis: ℂ, holomorphic functions, residues                                                      │
    │   ├── Topology: Open sets, continuity, connectedness                                                            │
    │   ├── Differential Geometry: Manifolds, curvature, geodesics                                                    │
    │   ├── Measure Theory: Lebesgue measure, integrals                                                               │
    │   ├── Functional Analysis: Banach/Hilbert spaces, operators                                                     │
    │   └── Dynamical Systems: Flows, attractors, chaos                                                               │
    │                                                                                                                 │
    │   CORE OPERATIONS:                                                                                              │
    │   ├── Limit: lim_{n→∞} or lim_{x→a}                                                                             │
    │   ├── Derivative: df/dx = lim_{h→0} [f(x+h) - f(x)]/h                                                           │
    │   ├── Integral: ∫ f dx                                                                                          │
    │   ├── Composition: f ∘ g                                                                                        │
    │   └── Inversion: f^{-1} when bijective                                                                          │
    │                                                                                                                 │
    │   KEY INVARIANTS:                                                                                               │
    │   ├── Topological: Dimension, genus, fundamental group                                                          │
    │   ├── Metric: Distance, diameter, completeness                                                                  │
    │   └── Analytic: Smoothness class, growth rate                                                                   │
    │                                                                                                                 │
    │   CERTIFICATE TYPES:                                                                                            │
    │   ├── Existence: Cauchy sequence or fixed-point                                                                 │
    │   ├── Bounds: ε-δ arguments, error estimates                                                                    │
    │   └── Continuity: Modulus of continuity                                                                         │
    │                                                                                                                 │
    │   THE CONTINUOUS QUESTION:                                                                                      │
    │   "How close?" "What is the limit?" "Can we connect A to B?"                                                    │
    │                                                                                                                 │
    └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

WHY π FOR CONTINUOUS?
    The number π = 3.14159... is the ratio of circumference to diameter.
    It governs CLOSURE and CYCLES:
    
    • Circles: C = 2πr
    • Euler's identity: e^{iπ} + 1 = 0
    • Gaussian integral: ∫_{-∞}^{∞} e^{-x²} dx = √π
    
    π embodies the completion of continuous curves.


§1.4 POLE Σ: STOCHASTIC (Fire/Θ)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                                                 │
    │   POLE Σ: THE STOCHASTIC REALM                                                                                  │
    │                                                                                                                 │
    │   ESSENCE:      Probability, measurement, irreducible uncertainty                                               │
    │   ELEMENT:      Fire (transformative, unpredictable, energetic)                                                 │
    │   GREEK:        Θ (theta) - angle, phase, rotation                                                              │
    │   CONSTANT:     i (imaginary unit) - rotation by 90°                                                            │
    │                                                                                                                 │
    │   MATHEMATICAL DOMAINS:                                                                                         │
    │   ├── Probability Theory: Random variables, distributions                                                       │
    │   ├── Statistics: Estimation, hypothesis testing                                                                │
    │   ├── Quantum Mechanics: Wave functions, observables                                                            │
    │   ├── Information Theory: Entropy, channel capacity                                                             │
    │   ├── Stochastic Processes: Markov chains, Brownian motion                                                      │
    │   └── Statistical Mechanics: Partition functions, ensembles                                                     │
    │                                                                                                                 │
    │   CORE OPERATIONS:                                                                                              │
    │   ├── Expectation: 𝔼[X] = ∫ x dP(x)                                                                             │
    │   ├── Measurement: ρ → outcome k with probability p_k                                                           │
    │   ├── Conditioning: P(A|B) = P(A∩B)/P(B)                                                                        │
    │   ├── Sampling: Draw from distribution                                                                          │
    │   └── Marginalization: P(X) = Σ_y P(X,Y=y)                                                                      │
    │                                                                                                                 │
    │   KEY INVARIANTS:                                                                                               │
    │   ├── Normalization: Σ_k p_k = 1 or ∫ dP = 1                                                                    │
    │   ├── Positivity: p_k ≥ 0 for all k                                                                             │
    │   └── Information: Entropy, mutual information                                                                  │
    │                                                                                                                 │
    │   CERTIFICATE TYPES:                                                                                            │
    │   ├── Distribution: Explicit formula or sampling algorithm                                                      │
    │   ├── Bounds: Concentration inequalities, tail bounds                                                           │
    │   └── Independence: Factorization witnesses                                                                     │
    │                                                                                                                 │
    │   THE STOCHASTIC QUESTION:                                                                                      │
    │   "What is the probability?" "What do we expect?" "How uncertain?"                                              │
    │                                                                                                                 │
    └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

WHY i FOR STOCHASTIC?
    The imaginary unit i = √(-1) enables ROTATION and PHASE:
    
    • Euler's formula: e^{iθ} = cos(θ) + i·sin(θ)
    • Quantum amplitudes are complex: ψ ∈ ℂ
    • Fourier transform uses e^{-2πikx}
    
    i connects amplitude (what we compute) to probability (what we observe).


§1.5 POLE Ψ: HIERARCHICAL (Air/Λ)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                                                 │
    │   POLE Ψ: THE HIERARCHICAL REALM                                                                                │
    │                                                                                                                 │
    │   ESSENCE:      Recursion, self-reference, emergence                                                            │
    │   ELEMENT:      Air (layered, recursive, meta)                                                                  │
    │   GREEK:        Λ (lambda) - abstraction, function                                                              │
    │   CONSTANT:     φ (golden ratio) - self-similar scale                                                           │
    │                                                                                                                 │
    │   MATHEMATICAL DOMAINS:                                                                                         │
    │   ├── Recursion Theory: Computability, halting problem                                                          │
    │   ├── Type Theory: Types, kinds, universes                                                                      │
    │   ├── Category Theory: Objects, morphisms, functors                                                             │
    │   ├── Renormalization: Scale transformations, fixed points                                                      │
    │   ├── Fractal Geometry: Self-similarity, dimension                                                              │
    │   └── Emergence: Macro from micro, coarse-graining                                                              │
    │                                                                                                                 │
    │   CORE OPERATIONS:                                                                                              │
    │   ├── Recursion: f(n) = g(f(n-1), n)                                                                            │
    │   ├── Abstraction: λx.M (function creation)                                                                     │
    │   ├── Application: M N (function application)                                                                   │
    │   ├── Fixed point: Y f = f(Y f)                                                                                 │
    │   └── Coarse-graining: Project to lower resolution                                                              │
    │                                                                                                                 │
    │   KEY INVARIANTS:                                                                                               │
    │   ├── Type: Object has consistent type at all levels                                                            │
    │   ├── Scale invariance: Same structure at different scales                                                      │
    │   └── Fixed point: f(x*) = x*                                                                                   │
    │                                                                                                                 │
    │   CERTIFICATE TYPES:                                                                                            │
    │   ├── Well-foundedness: Termination proof                                                                       │
    │   ├── Type correctness: Derivation tree                                                                         │
    │   └── Fixed point: Contraction/Brouwer witness                                                                  │
    │                                                                                                                 │
    │   THE HIERARCHICAL QUESTION:                                                                                    │
    │   "What level?" "Does it terminate?" "What emerges?"                                                            │
    │                                                                                                                 │
    └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

WHY φ FOR HIERARCHICAL?
    The golden ratio φ = (1+√5)/2 ≈ 1.618 satisfies:
    
    φ² = φ + 1  ⟺  φ = 1 + 1/φ
    
    This is SELF-REFERENCE in equation form!
    
    • Fibonacci: F_n/F_{n-1} → φ
    • Golden spiral: Self-similar at all scales
    • Penrose tilings: Aperiodic self-similarity
    
    φ embodies the fixed point of recursive structure.


§1.6 POLE INTERACTIONS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

The poles are not isolated—they INTERACT through specific mechanisms:

    ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                               ║
    ║   D ←→ Ω:  DISCRETIZATION / CONTINUIZATION                                                                    ║
    ║   ├── Discrete approximates continuous (numerical analysis)                                                   ║
    ║   ├── Continuous limits of discrete (thermodynamic limit)                                                     ║
    ║   └── Bridge: Sampling / Interpolation                                                                        ║
    ║                                                                                                               ║
    ║   D ←→ Σ:  COUNTING / PROBABILITY                                                                             ║
    ║   ├── Combinatorics underlies probability                                                                     ║
    ║   ├── Random sampling from discrete sets                                                                      ║
    ║   └── Bridge: Generating functions                                                                            ║
    ║                                                                                                               ║
    ║   D ←→ Ψ:  INDUCTION / RECURSION                                                                              ║
    ║   ├── Mathematical induction over ℕ                                                                           ║
    ║   ├── Recursive definitions                                                                                   ║
    ║   └── Bridge: Structural induction                                                                            ║
    ║                                                                                                               ║
    ║   Ω ←→ Σ:  MEASURE / PROBABILITY                                                                              ║
    ║   ├── Probability as measure theory                                                                           ║
    ║   ├── Continuous distributions                                                                                ║
    ║   └── Bridge: Lebesgue integration                                                                            ║
    ║                                                                                                               ║
    ║   Ω ←→ Ψ:  ANALYSIS / RECURSION                                                                               ║
    ║   ├── Fixed-point theorems (Banach, Brouwer)                                                                  ║
    ║   ├── Renormalization group                                                                                   ║
    ║   └── Bridge: Contraction mapping                                                                             ║
    ║                                                                                                               ║
    ║   Σ ←→ Ψ:  QUANTUM / HIERARCHY                                                                                ║
    ║   ├── Quantum measurement creates hierarchies                                                                 ║
    ║   ├── Emergence of classicality                                                                               ║
    ║   └── Bridge: Decoherence, renormalization                                                                    ║
    ║                                                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                               PART II: THE GATEWAY ALGEBRA SL(2,R)
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§2.1 WHY SL(2,R)?
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

The group SL(2,ℝ) is the UNIVERSAL GATEWAY between poles.

DEFINITION:
    SL(2,ℝ) = {M = [[a,b],[c,d]] : a,b,c,d ∈ ℝ, det(M) = ad - bc = 1}
    
    2×2 real matrices with determinant 1.

WHY IS THIS THE GATEWAY?

    1. ACTS ON EVERYTHING:
       SL(2,ℝ) acts on:
       • The real line (via Möbius)
       • The complex upper half-plane
       • Projective spaces
       • Hyperbolic geometry
       • Quantum states (as SU(1,1) or SL(2,ℂ))
    
    2. MINIMAL NON-ABELIAN:
       The simplest group that is:
       • Non-abelian (order matters)
       • Connected (continuously parameterized)
       • Simple (no normal subgroups)
    
    3. CONFORMAL SYMMETRY:
       SL(2,ℝ) is the symmetry group of conformal field theory in 1+1 dimensions.
       It connects UV (high energy) and IR (low energy).


§2.2 MÖBIUS TRANSFORMATIONS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

SL(2,ℝ) acts on the extended complex plane via MÖBIUS TRANSFORMATIONS:

    ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                               ║
    ║   Given M = [[a,b],[c,d]] ∈ SL(2,ℝ), define:                                                                  ║
    ║                                                                                                               ║
    ║                         f_M(z) = (az + b) / (cz + d)                                                          ║
    ║                                                                                                               ║
    ║   PROPERTIES:                                                                                                 ║
    ║   • f_M ∘ f_N = f_{MN}  (composition = matrix multiplication)                                                 ║
    ║   • f_I = id  (identity matrix → identity function)                                                           ║
    ║   • f_{M⁻¹} = f_M⁻¹  (inverse matrix → inverse function)                                                      ║
    ║   • Preserves circles and lines (generalized circles)                                                         ║
    ║   • Preserves angles (conformal)                                                                              ║
    ║   • Preserves cross-ratio                                                                                     ║
    ║                                                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝


§2.3 THE FOUR CANONICAL GENERATORS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

SL(2,ℝ) is generated by four fundamental operations:

    ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                                                 │
    │   T(b): TRANSLATION                                                                                             │
    │   ├── Matrix: [[1, b], [0, 1]]                                                                                  │
    │   ├── Action: z ↦ z + b                                                                                         │
    │   ├── Meaning: Shift along the real axis                                                                        │
    │   └── Pole connection: D ↔ D (discrete shifts)                                                                  │
    │                                                                                                                 │
    │   S(a): SCALING (a > 0)                                                                                         │
    │   ├── Matrix: [[a, 0], [0, 1/a]]                                                                                │
    │   ├── Action: z ↦ a² z                                                                                          │
    │   ├── Meaning: Dilation/contraction                                                                             │
    │   └── Pole connection: Ω ↔ Ω (continuous scaling)                                                               │
    │                                                                                                                 │
    │   J: INVERSION                                                                                                  │
    │   ├── Matrix: [[0, -1], [1, 0]]                                                                                 │
    │   ├── Action: z ↦ -1/z                                                                                          │
    │   ├── Meaning: Swap 0 and ∞, inside and outside                                                                 │
    │   └── Pole connection: D ↔ Ω (discrete-continuous bridge)                                                       │
    │                                                                                                                 │
    │   R(θ): ROTATION (in upper half-plane)                                                                          │
    │   ├── Matrix: [[cos θ, -sin θ], [sin θ, cos θ]]                                                                 │
    │   ├── Action: Rotation by 2θ in hyperbolic metric                                                               │
    │   ├── Meaning: Phase rotation                                                                                   │
    │   └── Pole connection: Σ ↔ Σ (stochastic phase)                                                                 │
    │                                                                                                                 │
    └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


§2.4 THE CARTAN DECOMPOSITION
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Every element g ∈ SL(2,ℝ) can be uniquely decomposed as:

    g = k₁ · a · k₂
    
    where k₁, k₂ ∈ SO(2) (rotations) and a is diagonal (scaling).

EXPLICIT FORM:
    [[a,b],[c,d]] = [[cos θ₁, -sin θ₁], [sin θ₁, cos θ₁]] 
                  · [[e^t, 0], [0, e^{-t}]]
                  · [[cos θ₂, -sin θ₂], [sin θ₂, cos θ₂]]

MEANING:
    Any transformation = rotation + scaling + rotation.
    
    1. Rotate to align with principal axes
    2. Scale along principal axes  
    3. Rotate to final orientation


§2.5 THE IWASAWA DECOMPOSITION
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Alternative decomposition:

    g = n · a · k
    
    where:
    • n ∈ N (upper triangular, 1s on diagonal) — nilpotent
    • a ∈ A (diagonal, positive entries) — abelian
    • k ∈ K = SO(2) — compact

EXPLICIT FORM:
    [[a,b],[c,d]] = [[1, x], [0, 1]] · [[y, 0], [0, 1/y]] · [[cos θ, -sin θ], [sin θ, cos θ]]

MEANING:
    Any transformation = translation + scaling + rotation.
    
    This is the "NAK" decomposition used in representation theory.


§2.6 CONNECTING THE POLES
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

SL(2,ℝ) provides explicit BRIDGES between poles:

    ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                               ║
    ║   BRIDGE: D ↔ D (Discrete to Discrete)                                                                        ║
    ║   Generator: T(b) = [[1, b], [0, 1]]                                                                          ║
    ║   Action: Shifts, translations                                                                                ║
    ║   Example: n ↦ n + k (additive shift)                                                                         ║
    ║                                                                                                               ║
    ║   BRIDGE: D ↔ Ω (Discrete to Continuous)                                                                      ║
    ║   Generator: J = [[0, -1], [1, 0]]                                                                            ║
    ║   Action: z ↦ -1/z swaps counting ↔ measuring                                                                 ║
    ║   Example: n ↦ 1/n (integers to unit fractions)                                                               ║
    ║                                                                                                               ║
    ║   BRIDGE: Ω ↔ Ω (Continuous to Continuous)                                                                    ║
    ║   Generator: S(a) = [[a, 0], [0, 1/a]]                                                                        ║
    ║   Action: z ↦ a²z (dilation)                                                                                  ║
    ║   Example: Rescaling coordinates                                                                              ║
    ║                                                                                                               ║
    ║   BRIDGE: Σ ↔ Σ (Stochastic to Stochastic)                                                                    ║
    ║   Generator: R(θ) = [[cos θ, -sin θ], [sin θ, cos θ]]                                                         ║
    ║   Action: Phase rotation                                                                                      ║
    ║   Example: Fourier transform phases                                                                           ║
    ║                                                                                                               ║
    ║   BRIDGE: Ψ ↔ Ψ (Hierarchical to Hierarchical)                                                                ║
    ║   Generator: Y = fixed-point operator                                                                         ║
    ║   Action: f ↦ fix(f)                                                                                          ║
    ║   Example: Recursive structures                                                                               ║
    ║                                                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝


§2.7 THE GATEWAY IN ACTION: EXAMPLES
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

EXAMPLE 1: FOURIER TRANSFORM

    The Fourier transform is an SL(2,ℝ) action!
    
    F corresponds to J: [[0, -1], [1, 0]]
    
    Position space ↔ Momentum space
    
    F² = [[−1, 0], [0, −1]] = parity
    F⁴ = I

EXAMPLE 2: MODULAR FORMS

    Modular forms are functions f: ℍ → ℂ satisfying:
    
    f((az + b)/(cz + d)) = (cz + d)^k f(z)
    
    for all [[a,b],[c,d]] ∈ SL(2,ℤ).
    
    This connects number theory (D) to complex analysis (Ω).

EXAMPLE 3: QUANTUM MECHANICS

    The metaplectic group Mp(2,ℝ) double-covers SL(2,ℝ).
    
    It acts on:
    • Wave functions (position representation)
    • Momentum representation
    • Wigner function (phase space)
    
    Squeezing operators are SL(2,ℝ) transformations.

EXAMPLE 4: CONFORMAL FIELD THEORY

    The Virasoro algebra (infinite-dimensional extension of sl(2,ℝ))
    governs 2D conformal symmetry.
    
    Generators: L_n with [L_m, L_n] = (m-n)L_{m+n} + (c/12)(m³-m)δ_{m+n,0}
    
    The subalgebra {L_{-1}, L_0, L_1} is isomorphic to sl(2,ℝ).


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                              PART III: THE FOUR LENSES IN DEPTH
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§3.1 LENS □ (SQUARE): STRUCTURAL VIEW
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ESSENCE: See the object as a discrete structure.
    
    QUESTIONS:
    • What are the elements?
    • What are the relations?
    • What is the cardinality?
    • What is the symmetry group?
    
    OPERATIONS:
    • Count: |A|
    • Partition: A = ⊔_i A_i
    • Product: A × B
    • Quotient: A / ~
    
    INVARIANTS:
    • Cardinality
    • Equivalence classes
    • Group structure

§3.2 LENS ✿ (FLOWER): CYCLIC VIEW
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ESSENCE: See the object as cyclic symmetry.
    
    QUESTIONS:
    • What rotates into what?
    • What is the period?
    • What is the phase?
    • What are the harmonics?
    
    OPERATIONS:
    • Rotate: z ↦ e^{iθ} z
    • Decompose: Fourier series
    • Phase shift: f(t) ↦ f(t - τ)
    
    INVARIANTS:
    • Period
    • Phase spectrum
    • Rotational symmetry order

§3.3 LENS ☁ (CLOUD): PROBABILISTIC VIEW
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ESSENCE: See the object as probability distribution.
    
    QUESTIONS:
    • What is the mean?
    • What is the variance?
    • What are the tails?
    • What is the entropy?
    
    OPERATIONS:
    • Expectation: 𝔼[X]
    • Condition: P(·|A)
    • Marginalize: ∫ dY
    • Sample: X ~ P
    
    INVARIANTS:
    • Normalization
    • Moments
    • Entropy

§3.4 LENS ❋ (FRACTAL): RECURSIVE VIEW
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ESSENCE: See the object as self-similar structure.
    
    QUESTIONS:
    • What is the generator?
    • What is the fixed point?
    • What is the scaling dimension?
    • What RG flow does it follow?
    
    OPERATIONS:
    • Recurse: f(f(x))
    • Scale: x ↦ λx
    • Coarse-grain: Project to lower resolution
    • Find fixed point: solve f(x*) = x*
    
    INVARIANTS:
    • Scaling exponents
    • Fixed points
    • Universality class


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                        SYNTHESIS
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

The Four Poles and Gateway Architecture provide:

1. A COMPLETE TAXONOMY of mathematical domains
   Every mathematical structure belongs to a pole (or combination).

2. A TRANSFORMATION LANGUAGE via SL(2,ℝ)
   Any bridge between domains is an SL(2,ℝ) action.

3. MULTIPLE PERSPECTIVES via Four Lenses
   Every object can be viewed structurally, cyclically, probabilistically, recursively.

4. DUALITY STRUCTURE
   Poles are paired: (D ↔ Ω), (Σ ↔ Ψ)
   Gateway operators swap between poles.

This is the architectural foundation of the Universal Harmonic Framework.

"""
