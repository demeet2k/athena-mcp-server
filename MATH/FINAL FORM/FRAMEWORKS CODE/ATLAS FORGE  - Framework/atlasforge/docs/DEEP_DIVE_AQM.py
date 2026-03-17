"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                      ║
║                              DEEP DIVE: AXIOMATIC QUANTUM MATHEMATICS (AQM)                                          ║
║                                                                                                                      ║
║                                    COMPLETE TECHNICAL SPECIFICATION                                                  ║
║                                                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                        TOME I: Q-NUMBERS IN DEPTH
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§1.1 THE PHILOSOPHICAL FOUNDATION
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Why Q-Numbers?

Classical mathematics treats numbers as perfect, infinitely precise points. The number π is a single,
exact value—even though we can never write it down completely. This works well in pure mathematics,
but creates problems:

    PROBLEM 1: PRECISION ILLUSION
    When we write "x = 3.14159", we pretend we know x exactly. But in reality:
    - Measurements have uncertainty
    - Computations have rounding errors
    - Physical quantities have quantum limits
    
    PROBLEM 2: SEMANTIC AMBIGUITY
    The symbol "x" might mean:
    - A single exact value (Platonic ideal)
    - A measured value (with error bars)
    - A random variable (with distribution)
    - A quantum observable (with superposition)
    
    PROBLEM 3: COMPOSITION OPACITY
    When we compute f(x, y), how does uncertainty propagate?
    - Linear propagation? Δf ≈ |∂f/∂x|Δx + |∂f/∂y|Δy
    - Quadrature? Δf ≈ √[(∂f/∂x)²(Δx)² + (∂f/∂y)²(Δy)²]
    - Something else entirely?

Q-Numbers solve these problems by making uncertainty FIRST-CLASS:

    ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                               ║
    ║   A Q-NUMBER is not a single value but a DENSITY OPERATOR ρ on a Hilbert space ℋ.                            ║
    ║                                                                                                               ║
    ║   The density operator encodes:                                                                               ║
    ║   • The expected value (mean)                                                                                 ║
    ║   • The uncertainty (variance)                                                                                ║
    ║   • The full probability distribution                                                                         ║
    ║   • Correlations with other Q-numbers                                                                         ║
    ║   • Quantum coherences (off-diagonal terms)                                                                   ║
    ║                                                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝


§1.2 MATHEMATICAL STRUCTURE OF DENSITY OPERATORS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

DEFINITION: A density operator ρ on Hilbert space ℋ satisfies:

    (1) HERMITICITY:           ρ† = ρ
        The operator equals its conjugate transpose.
        Ensures all eigenvalues are real.
        
    (2) POSITIVE SEMIDEFINITE: ρ ≥ 0
        All eigenvalues are non-negative.
        ⟨ψ|ρ|ψ⟩ ≥ 0 for all |ψ⟩ ∈ ℋ.
        
    (3) UNIT TRACE:            Tr(ρ) = 1
        Sum of eigenvalues equals 1.
        Total probability is normalized.

SPECTRAL DECOMPOSITION:
    ρ = Σᵢ λᵢ |φᵢ⟩⟨φᵢ|
    
    where {|φᵢ⟩} are orthonormal eigenvectors
    and {λᵢ} are eigenvalues with λᵢ ≥ 0, Σᵢ λᵢ = 1

INTERPRETATION:
    The eigenvalue λᵢ is the probability of finding the system in state |φᵢ⟩.
    The Q-number represents a probabilistic mixture of sharp values.

EXAMPLE: A Q-number for "approximately 3"

    ℋ = span{|2⟩, |3⟩, |4⟩}  (three-dimensional)
    
    ρ = 0.1 |2⟩⟨2| + 0.8 |3⟩⟨3| + 0.1 |4⟩⟨4|
    
    Expected value: Tr(ρ·X̂) = 0.1(2) + 0.8(3) + 0.1(4) = 3.0
    Variance: Tr(ρ·X̂²) - [Tr(ρ·X̂)]² = 0.2
    Standard deviation: √0.2 ≈ 0.447
    
    This Q-number says "3 ± 0.45"


§1.3 PURITY AND MIXEDNESS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

PURITY MEASURE:
    γ = Tr(ρ²)
    
    Range: 1/d ≤ γ ≤ 1, where d = dim(ℋ)

PURE STATES (γ = 1):
    ρ = |ψ⟩⟨ψ| for some unit vector |ψ⟩
    
    Properties:
    • Zero entropy: S(ρ) = -Tr(ρ log ρ) = 0
    • Minimum uncertainty for some observable
    • Can exhibit quantum coherence
    
    Example: |ψ⟩ = (|0⟩ + |1⟩)/√2  → ρ = ½[|0⟩⟨0| + |0⟩⟨1| + |1⟩⟨0| + |1⟩⟨1|]
    The off-diagonal terms |0⟩⟨1| and |1⟩⟨0| are coherences.

MIXED STATES (γ < 1):
    ρ = Σᵢ pᵢ |ψᵢ⟩⟨ψᵢ| with at least two distinct |ψᵢ⟩
    
    Properties:
    • Positive entropy: S(ρ) > 0
    • Represents classical uncertainty
    • No quantum coherence in eigenbasis
    
    Example: ρ = ½|0⟩⟨0| + ½|1⟩⟨1|
    This is a classical coin flip, not a superposition.

MAXIMALLY MIXED STATE (γ = 1/d):
    ρ = I/d (identity divided by dimension)
    
    Maximum entropy: S(ρ) = log(d)
    Complete ignorance about the value.


§1.4 THE Q-NUMBER HIERARCHY
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                                                 │
    │   CLASSICAL NUMBERS ⊂ Q-RATIONALS ⊂ Q-REALS ⊂ Q-COMPLEX ⊂ FULL Q-NUMBERS                                       │
    │        ℝ                  ℚ̃             ℝ̃          ℂ̃              𝒬                                            │
    │                                                                                                                 │
    └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

LEVEL 0: CLASSICAL NUMBERS (ℝ)
    Embedding: x ↦ ρₓ = |x⟩⟨x|
    
    Classical numbers are pure, delta-function Q-numbers.
    Zero uncertainty: Δx = 0.
    This is the "Platonic ideal" limit.

LEVEL 1: Q-RATIONALS (ℚ̃)
    Finite-dimensional density operators.
    Support on finitely many rational values.
    Exact arithmetic is possible.
    
    Example: "Either 1/3 or 2/3 with equal probability"
    ρ = ½|1/3⟩⟨1/3| + ½|2/3⟩⟨2/3|

LEVEL 2: Q-REALS (ℝ̃)
    Limits of Q-rationals.
    May have continuous spectrum.
    Bounded error certificates required.
    
    Example: Gaussian distribution centered at π
    ρ = ∫ (1/√(2πσ²)) e^{-(x-π)²/2σ²} |x⟩⟨x| dx

LEVEL 3: Q-COMPLEX (ℂ̃)
    Pairs of Q-reals with phase.
    Support complex amplitudes.
    Essential for quantum mechanics.

LEVEL 4: FULL Q-NUMBERS (𝒬)
    Arbitrary density operators.
    May include entanglement.
    Most general case.


§1.5 UNCERTAINTY ENVELOPES
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Every Q-number carries an UNCERTAINTY ENVELOPE specifying its spread:

    ENVELOPE ε = (center, radius, confidence)
    
    Meaning: With probability ≥ confidence, the value lies in [center - radius, center + radius].

ENVELOPE PROPAGATION:
    When computing f(ρ), the envelope transforms:
    
    ε_f ≈ |f'(center)| · ε  (linear approximation)
    
    For multivariate f(ρ₁, ρ₂, ...):
    
    ε_f² ≈ Σᵢ (∂f/∂xᵢ)² εᵢ²  (quadrature propagation)

CORRIDOR MEMBERSHIP:
    A Q-number ρ is "in corridor C = [a, b]" if its envelope fits:
    
    center - radius ≥ a  AND  center + radius ≤ b
    
    This is DECIDABLE: we can compute a witness or refutation.


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                   TOME II: QUANTUM ARITHMETIC IN DEPTH
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§2.1 CPTP CHANNELS: THE FOUNDATION
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

In AQM, arithmetic operations are CPTP (Completely Positive, Trace-Preserving) channels:

DEFINITION: A CPTP channel Φ: 𝒟(ℋ_in) → 𝒟(ℋ_out) satisfies:

    (1) COMPLETELY POSITIVE:
        For any extension Φ ⊗ I_n acting on ρ ⊗ σ,
        the result is positive if the input is positive.
        
        Physical meaning: No negative probabilities, ever.
        
    (2) TRACE PRESERVING:
        Tr(Φ(ρ)) = Tr(ρ) = 1
        
        Physical meaning: Total probability is conserved.

KRAUS REPRESENTATION:
    Every CPTP channel can be written as:
    
    Φ(ρ) = Σₖ Kₖ ρ Kₖ†
    
    where the Kraus operators {Kₖ} satisfy:
    
    Σₖ Kₖ† Kₖ = I  (completeness relation)

WHY CPTP?
    • Ensures mathematical consistency (positivity, normalization)
    • Captures all physically realizable operations
    • Includes both unitary evolution and measurement
    • Composes correctly: Φ₂ ∘ Φ₁ is CPTP if both are


§2.2 ADDITION CHANNEL
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

The addition channel computes "a + b" for Q-numbers:

    Φ₊: 𝒟(ℋ_a ⊗ ℋ_b) → 𝒟(ℋ_sum)

CONSTRUCTION:
    1. Start with tensor product ρ_a ⊗ ρ_b
    2. Apply addition unitary: U_add |x⟩|y⟩ = |x+y⟩|y⟩
    3. Partial trace over second register
    
    Result: ρ_{a+b}

ENVELOPE PROPAGATION:
    If ρ_a has envelope (μ_a, ε_a) and ρ_b has envelope (μ_b, ε_b):
    
    ρ_{a+b} has envelope (μ_a + μ_b, ε_a + ε_b)  [worst case]
    
    Or, if independent:
    
    ρ_{a+b} has envelope (μ_a + μ_b, √(ε_a² + ε_b²))  [quadrature]

SPECIAL CASES:
    • Classical + Classical = Classical
    • Pure + Pure = Pure (if independent)
    • Gaussian + Gaussian = Gaussian


§2.3 MULTIPLICATION CHANNEL
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

The multiplication channel is more complex:

    Φ_×: 𝒟(ℋ_a ⊗ ℋ_b) → 𝒟(ℋ_prod)

CONSTRUCTION:
    1. Start with tensor product ρ_a ⊗ ρ_b
    2. Apply multiplication unitary in logarithmic encoding
    3. Partial trace and decode
    
    Complication: Multiplication is nonlinear, creating correlations.

ENVELOPE PROPAGATION:
    If ρ_a has envelope (μ_a, ε_a) and ρ_b has envelope (μ_b, ε_b):
    
    ρ_{a×b} has envelope approximately:
    
    center: μ_a × μ_b
    radius: |μ_b| ε_a + |μ_a| ε_b + ε_a ε_b

ENTANGLEMENT CREATION:
    Unlike addition, multiplication can create entanglement!
    
    If ρ_a and ρ_b are pure but correlated (entangled),
    ρ_{a×b} exhibits non-classical statistics.


§2.4 INVERSE AND ROOT CHANNELS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

INVERSE CHANNEL Φ_inv:
    Computes "1/a" for Q-number a.
    
    PRECONDITION: a is bounded away from zero.
    
    Corridor predicate: |a| > δ for some δ > 0
    
    If precondition fails: REFUSE (not FAIL—we didn't try)
    
    ENVELOPE:
    If ρ_a has envelope (μ_a, ε_a) with |μ_a| > δ:
    
    ρ_{1/a} has envelope approximately:
    center: 1/μ_a
    radius: ε_a / |μ_a|²

ROOT CHANNEL Φ_√:
    Computes "√a" for Q-number a.
    
    PRECONDITION: a > 0 (strictly positive)
    
    Corridor predicate: a > δ > 0
    
    ENVELOPE:
    If ρ_a has envelope (μ_a, ε_a) with μ_a > δ:
    
    ρ_{√a} has envelope approximately:
    center: √μ_a
    radius: ε_a / (2√μ_a)


§2.5 COMPOSITION AND CERTIFICATES
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

CHANNEL COMPOSITION:
    CPTP channels compose associatively:
    
    (Φ₃ ∘ Φ₂) ∘ Φ₁ = Φ₃ ∘ (Φ₂ ∘ Φ₁)
    
    The composition is again CPTP.

CERTIFICATE COMPOSITION:
    When we compute Φ₂(Φ₁(ρ)):
    
    1. Φ₁ produces (ρ', cert₁) where cert₁ proves properties of ρ'
    2. Φ₂ produces (ρ'', cert₂) where cert₂ proves properties of ρ''
    3. Combined certificate: (cert₁, cert₂, composition_witness)
    
    The composition_witness proves that cert₂ is valid given cert₁.

ERROR ACCUMULATION:
    After n operations, envelope radius grows:
    
    Worst case: ε_n ≈ n · ε₀  (linear)
    Quadrature: ε_n ≈ √n · ε₀  (square root)
    
    The certificate tracks which regime applies.


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                    TOME III: REALIZATION IN DEPTH
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§3.1 THE REALIZATION PROBLEM
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

PROBLEM: Given constraints C and corridors K, does there exist a Q-number ρ satisfying all of them?

    CONSTRAINTS C = {fᵢ(ρ) = 0}
    Examples:
    • Tr(ρ) = 1 (normalization)
    • Tr(ρ·X̂) = μ (fixed mean)
    • Tr(ρ·X̂²) - Tr(ρ·X̂)² = σ² (fixed variance)
    
    CORRIDORS K = {gⱼ(ρ) ∈ [aⱼ, bⱼ]}
    Examples:
    • Tr(ρ·X̂) ∈ [2.9, 3.1] (mean in range)
    • Tr(ρ²) ∈ [0.5, 1.0] (purity in range)

REALIZATION THEOREM:
    There exists ρ ∈ 𝒟(ℋ) satisfying C ∪ K if and only if:
    
    1. CONSISTENCY: The constraints C have no contradictions.
    2. NON-EMPTINESS: The corridors K overlap with the constraint manifold.
    3. POSITIVITY: The feasible region contains positive operators.
    
    Moreover, the proof is CONSTRUCTIVE: we can build ρ and certify it.


§3.2 CONSTRUCTIVE REALIZATION
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

ALGORITHM: MaxEnt Realization

    INPUT: Constraints C, Corridors K
    OUTPUT: Q-number ρ satisfying C ∪ K, or REFUSE with witness
    
    1. FORMULATE as convex optimization:
       maximize  S(ρ) = -Tr(ρ log ρ)  [entropy]
       subject to fᵢ(ρ) = 0 for all i
                  gⱼ(ρ) ∈ [aⱼ, bⱼ] for all j
                  ρ ≥ 0, Tr(ρ) = 1
    
    2. SOLVE using semidefinite programming (SDP)
       If feasible: extract ρ* and Lagrange multipliers
       If infeasible: extract separating hyperplane (witness)
    
    3. CERTIFY:
       Verify all constraints hold
       Compute envelope from spectrum
       Bundle into certificate

WHY MAXIMUM ENTROPY?
    • Unique: Among all feasible ρ, maxent is canonical
    • Least biased: Encodes constraints, nothing more
    • Stable: Small perturbations → small changes
    • Physically motivated: Thermal equilibrium


§3.3 BRIDGE OPERATORS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Bridges translate Q-numbers between representations:

POSITION ↔ MOMENTUM BRIDGE (Fourier):
    F: L²(ℝ_x) → L²(ℝ_p)
    
    (Fψ)(p) = (1/√2πℏ) ∫ ψ(x) e^{-ipx/ℏ} dx
    
    For density operators:
    ρ_p = F ρ_x F†
    
    Uncertainty transforms:
    Δx · Δp ≥ ℏ/2  (Heisenberg)

DISCRETE ↔ CONTINUOUS BRIDGE:
    Embedding ι: ℓ²(ℤ) → L²(ℝ)
    (ιψ)(x) = Σₙ ψₙ · sinc(x - n)  [Shannon interpolation]
    
    Sampling π: L²(ℝ) → ℓ²(ℤ)
    (πψ)ₙ = ψ(n)  [point evaluation]
    
    Composition: π ∘ ι = I on bandlimited signals

PURE ↔ MIXED BRIDGE:
    Purification: ρ → |Ψ⟩⟨Ψ| on ℋ ⊗ ℋ_aux
    
    For any mixed ρ = Σᵢ pᵢ |φᵢ⟩⟨φᵢ|, there exists pure:
    |Ψ⟩ = Σᵢ √pᵢ |φᵢ⟩ ⊗ |eᵢ⟩
    
    such that Tr_aux(|Ψ⟩⟨Ψ|) = ρ
    
    Partial trace recovers the original mixed state.


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                    TOME IV: KERNEL CLOSURE IN DEPTH
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§4.1 THE INFINITE-FINITE TENSION
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

PROBLEM: Many mathematical objects are infinite-dimensional, but computation is finite.

    • Real numbers have infinitely many digits
    • Continuous functions have infinitely many values
    • Hilbert spaces may be infinite-dimensional
    
    How do we compute with these objects RIGOROUSLY?

SOLUTION: The Kernel Closure Principle

    ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                               ║
    ║   Every infinite object admits a FINITE KERNEL that:                                                          ║
    ║   1. Captures all decidable properties                                                                        ║
    ║   2. Supports deterministic replay                                                                            ║
    ║   3. Carries explicit error certificates                                                                      ║
    ║                                                                                                               ║
    ║   The infinite object is the LIMIT of kernel approximations.                                                  ║
    ║                                                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝


§4.2 TRUNCATION THEORY
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

TRUNCATION OPERATOR τ_d:
    Maps infinite-dimensional state to d-dimensional approximation.
    
    For ρ = Σᵢ λᵢ |φᵢ⟩⟨φᵢ| with eigenvalues in decreasing order:
    
    τ_d(ρ) = (Σᵢ₌₁ᵈ λᵢ |φᵢ⟩⟨φᵢ|) / (Σᵢ₌₁ᵈ λᵢ)
    
    Keep top d eigenvalues, renormalize.

ERROR BOUND:
    ‖ρ - τ_d(ρ)‖₁ ≤ 2 Σᵢ₌ₐ₊₁^∞ λᵢ
    
    The error is bounded by twice the discarded probability mass.

CONVERGENCE:
    As d → ∞, τ_d(ρ) → ρ in trace norm.
    
    Rate depends on eigenvalue decay:
    • Exponential decay: error ∼ e^{-αd}
    • Power law decay: error ∼ d^{-β}


§4.3 JET STRUCTURE
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Jets encode local behavior at boundaries:

DEFINITION: The m-jet of function f at point a is:

    J^m_a f = (f(a), f'(a), f''(a)/2!, ..., f^{(m)}(a)/m!)
    
    This is the Taylor polynomial truncated at order m.

JET SPACE J^m(X, Y):
    The space of all m-jets from X to Y.
    
    Dimension: If X = ℝⁿ, Y = ℝᵏ, then dim(J^m) = k × C(n+m, m)

JET ADEQUACY:
    A jet is ADEQUATE if it determines behavior within tolerance ε:
    
    |f(a + h) - P_m(h)| ≤ ε for |h| ≤ δ
    
    where P_m is the Taylor polynomial.

JET ESCALATION:
    If m-jet is inadequate (Ambig_m), escalate to (m+1)-jet.
    
    Ambig_m → Try m+1 → Either Resolved or Ambig_{m+1}
    
    This is the AQM analogue of "need more precision."


§4.4 FIXED POINT CERTIFICATION
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Many objects are defined as fixed points: f(x*) = x*

EXISTENCE CERTIFICATES:

    BANACH CERTIFICATE:
    If f is a contraction on complete metric space (ratio κ < 1):
    ‖f(x) - f(y)‖ ≤ κ ‖x - y‖
    Then f has unique fixed point.
    Certificate: (f, κ, initial_point, iteration_count)
    
    BROUWER CERTIFICATE:
    If f: K → K is continuous on compact convex K:
    Then f has a fixed point.
    Certificate: (K_description, f_continuity_witness)
    
    SCHAUDER CERTIFICATE:
    If f is compact on Banach space:
    Then f has a fixed point.
    Certificate: (compactness_witness, f_description)

RESIDUAL CERTIFICATE:
    For candidate x*:
    
    residual = ‖f(x*) - x*‖
    
    Certificate: (x*, residual, error_bound)
    
    If residual < ε and f is Lipschitz with constant L:
    True fixed point is within residual / (1 - L) of x*.

STABILITY WITNESS:
    LYAPUNOV: V(x) > 0 for x ≠ x*, V(x*) = 0, V̇(x) < 0
    SPECTRAL: All eigenvalues of Df(x*) have |λ| < 1
    CONTRACTION: ‖Df(x*)‖ < 1


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                     TOME V: LIMINAL SPACE IN DEPTH
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§5.1 THE LIMINAL CONCEPT
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

"Liminal" (from Latin limen, threshold) means "at the boundary."

LIMINAL STATES are those that exist between defined categories:
    • Not fully discrete, not fully continuous
    • Not fully deterministic, not fully stochastic
    • Not fully classical, not fully quantum
    • Transitioning from one regime to another

LIMINAL STATE SPACE AQM-Λ:
    A liminal state carries:
    
    1. MATTER/BEHAVIOR STATE: The current configuration
    2. VALIDITY CORRIDORS: Where the state is meaningful
    3. TRANSITION GATES: Requirements for regime change
    4. WITNESSES: Evidence supporting validity
    5. CERTIFICATES: Verification records


§5.2 THE LIFT OPERATOR Λ
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

The LIFT operator Λ transforms between regimes:

    Λ: REGIME_SOURCE → REGIME_TARGET

CANONICAL LIFTS:

    Λ_quantize: Classical → Quantum
    x ↦ |x⟩⟨x| (diagonal embedding)
    OR
    x ↦ |α=x⟩⟨α=x| (coherent state)
    
    Λ_discretize: Continuous → Discrete
    f(x) ↦ f|_lattice (restriction to lattice)
    OR
    f(x) ↦ (∫_{cell_n} f dx)_n (cell averages)
    
    Λ_embed: Finite-dim → Infinite-dim
    ρ_d ↦ ρ_d ⊕ 0 (zero-padded embedding)
    
    Λ_coarse: Fine → Coarse
    ρ_fine ↦ C ρ_fine C† (coarse-graining channel)

LIFT PROPERTIES:
    • Structure-preserving (as much as possible)
    • Certified (carries validity evidence)
    • Invertible (has project operator Π)
    • Composable: Λ₂ ∘ Λ₁ is a lift


§5.3 EMERGENCE COORDINATES
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

The OICF coordinates quantify emergence:

    Ω (OMEGA): VIABILITY
    ├── Definition: Margin to boundary of validity
    ├── Range: [0, 1] where 0 = at boundary, 1 = maximally stable
    ├── Interpretation: How far from failure?
    └── Computation: Distance to nearest corridor violation
    
    I (IOTA): INTEGRATION
    ├── Definition: Coupling strength between subsystems
    ├── Range: [0, 1] where 0 = decoupled, 1 = fully integrated
    ├── Interpretation: How connected?
    └── Computation: Mutual information / entanglement measure
    
    C (CHI): COHERENCE
    ├── Definition: Structured correlation across scales
    ├── Range: [0, 1] where 0 = incoherent, 1 = fully coherent
    ├── Interpretation: How aligned?
    └── Computation: Off-diagonal density matrix elements
    
    F (PHI): FUNCTION
    ├── Definition: Viability potential / utility measure
    ├── Range: [0, 1] where 0 = non-functional, 1 = optimal
    ├── Interpretation: How purposeful?
    └── Computation: Objective function value

EMERGENCE POTENTIAL:
    E = Ω · I · C · F
    
    When E crosses threshold, new properties emerge.
    
    Phase transition: subcritical → critical → supercritical


§5.4 THE CONVERGENCE THEOREM
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

REMARKABLE FACT: AQM and LM independently arrived at the SAME coordinates!

    AQM-Λ uses (Ω, I, C, F) from quantum information theory.
    LM uses (Ω, I, C, F) from dynamical systems theory.
    
    The coordinates have the SAME mathematical structure.

WHY CONVERGENCE?
    These coordinates are UNIVERSAL because any theory of emergence must track:
    
    1. Distance from failure (viability) — Ω
    2. Internal connectivity (integration) — I
    3. Cross-scale consistency (coherence) — C
    4. Goal-directedness (function) — F
    
    There is no other independent coordinate. These four span the space.

CONSEQUENCE:
    AQM and LM are not competing theories—they are DUAL FORMULATIONS
    of the same underlying structure, related by a bridge map.

"""
