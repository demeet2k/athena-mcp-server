"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                      ║
║                                  DEEP DIVE: LIMINAL MATHEMATICS (LM)                                                 ║
║                                                                                                                      ║
║                                    COMPLETE TECHNICAL SPECIFICATION                                                  ║
║                                                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                   TOME I: FOUNDATIONS & SEMANTICS
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§1.1 THE SEMANTIC CRISIS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Mathematics faces a hidden crisis: SEMANTIC DRIFT

    SYMPTOM 1: Symbol Ambiguity
    The symbol "=" means different things:
    • Definition:   f(x) = x²  (we're defining f)
    • Equation:     x² = 4  (we're solving for x)
    • Identity:     sin²θ + cos²θ = 1  (always true)
    • Approximation: π = 3.14159  (approximately equal)
    
    SYMPTOM 2: Context Dependence
    "The integral converges" depends on:
    • Which function space?
    • Which topology?
    • Which measure?
    • At what rate?
    
    SYMPTOM 3: Silent Assumptions
    "Let f be a function" hides:
    • Domain? Range? Regularity?
    • Single-valued or multi-valued?
    • Real or complex?
    • Continuous or discontinuous?

LM addresses this by making ALL semantic content EXPLICIT and DECIDABLE.


§1.2 THE DISTINCTION CALCULUS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

The atomic unit of meaning is the DISTINCTION:

    ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                               ║
    ║   DISTINCTION ≡ (Predicate, Witnesses, Decider)                                                              ║
    ║                                                                                                               ║
    ║   Predicate:  P: Universe → {True, False, Undecidable}                                                       ║
    ║   Witnesses:  Evidence for positive/negative claims                                                          ║
    ║   Decider:    Algorithm that terminates with verdict + witness                                               ║
    ║                                                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

EXAMPLE: The distinction "x > 5"

    Predicate: P(x) = "Is x greater than 5?"
    
    Positive witness: A lower bound L > 5 such that x ≥ L
    Negative witness: An upper bound U ≤ 5 such that x ≤ U
    Undecidable case: x straddles 5 (envelope includes boundary)
    
    Decider algorithm:
    1. Compute envelope of x: (center, radius)
    2. If center - radius > 5: return (True, lower_bound_witness)
    3. If center + radius ≤ 5: return (False, upper_bound_witness)
    4. Else: return (Undecidable, straddling_witness)

DISTINCTION COMPOSITION:

    AND: D₁ ∧ D₂
    Both must be true; witnesses combine.
    
    OR: D₁ ∨ D₂
    At least one must be true; first witness suffices.
    
    NOT: ¬D
    Swap true/false; swap witness types.
    
    IMPLIES: D₁ → D₂
    Equivalent to ¬D₁ ∨ D₂


§1.3 CORRIDOR SEMANTICS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

A CORRIDOR is a region where semantic claims are valid:

    CORRIDOR C = (Predicate, Bounds, Margin)
    
    Predicate: What property must hold?
    Bounds: The region [a, b] or more complex shape
    Margin: Safety buffer for numerical stability

CORRIDOR TYPES:

    STATE CORRIDOR:
    "The state ρ is valid when its eigenvalues are in [0, 1]"
    Tests: Is ρ positive? Is ρ normalized?
    
    OBSERVABLE CORRIDOR:
    "The observable A is defined when its eigenvalues are bounded"
    Tests: Is A self-adjoint? Is spectrum bounded?
    
    EVALUATION CORRIDOR:
    "Computing f(x) is safe when x is away from singularities"
    Tests: Is x in domain? Is x away from poles?
    
    TRANSITION CORRIDOR:
    "The transition ρ → σ is valid when the channel is CPTP"
    Tests: Is Φ completely positive? Is Φ trace-preserving?

CORRIDOR TEST ALGORITHM:

    Input: state ρ, corridor C
    Output: (verdict, slack, diagnostic)
    
    1. Evaluate predicate P(ρ)
    2. If P(ρ) = True:
       - Compute slack = distance to boundary
       - Return (PASS, slack, null)
    3. If P(ρ) = False:
       - Compute diagnostic = why failed
       - Return (FAIL, 0, diagnostic)
    4. If P(ρ) = Undecidable:
       - Return (AMBIGUOUS, 0, ambiguity_description)


§1.4 TYPED OUTCOMES
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Every computation in LM returns a TYPED OUTCOME:

    ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                                                 │
    │   OK(value, certificates)                                                                                       │
    │   ├── The computation succeeded                                                                                 │
    │   ├── value: The computed result                                                                                │
    │   ├── certificates: Proofs that value is correct                                                                │
    │   └── Example: OK(3.14159, [truncation_cert, error_bound_cert])                                                 │
    │                                                                                                                 │
    │   FAIL(reason, diagnostic)                                                                                      │
    │   ├── The computation definitively failed                                                                       │
    │   ├── reason: Why it failed (enumerated type)                                                                   │
    │   ├── diagnostic: Detailed explanation                                                                          │
    │   └── Example: FAIL(DIVISION_BY_ZERO, "denominator envelope contains 0")                                        │
    │                                                                                                                 │
    │   REFUSE(reason, remediation)                                                                                   │
    │   ├── The computation refused to proceed                                                                        │
    │   ├── reason: Why it refused (precondition violated)                                                            │
    │   ├── remediation: How to fix it                                                                                │
    │   └── Example: REFUSE(CORRIDOR_VIOLATION, "ensure x > 0 before computing √x")                                   │
    │                                                                                                                 │
    │   ABSTAIN(ambiguity_level, escalation_path)                                                                     │
    │   ├── Cannot decide with current evidence                                                                       │
    │   ├── ambiguity_level: Ambig_m for some m                                                                       │
    │   ├── escalation_path: How to resolve                                                                           │
    │   └── Example: ABSTAIN(Ambig_2, "need 3rd derivative to decide sign")                                           │
    │                                                                                                                 │
    └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

WHY FOUR OUTCOMES?
    • OK: Success with proof
    • FAIL: Definite impossibility
    • REFUSE: Won't try (precondition missing)
    • ABSTAIN: Can't decide (need more information)
    
    These are EXHAUSTIVE and MUTUALLY EXCLUSIVE.


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                    TOME II: DYNAMICS & ECOLOGY
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§2.1 HYBRID DYNAMICAL SYSTEMS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Real systems don't follow pure ODEs or pure discrete maps. They exhibit HYBRID dynamics:

    HYBRID SYSTEM H = (Modes, Flow, Jump, Guard, Reset)
    
    Modes: Discrete set of operational regimes
    Flow: Continuous evolution within each mode (ODE/PDE)
    Jump: Discrete transition between modes
    Guard: Conditions triggering jumps
    Reset: State transformation during jump

EXECUTION SEMANTICS:

    1. Start in mode m₀ with state x₀
    2. Flow according to ẋ = f_{m₀}(x) within mode
    3. Monitor guard conditions G(m₀, x)
    4. When guard becomes true:
       a. Execute jump: (m₀, x) → (m₁, x')
       b. Apply reset: x' = R(m₀, m₁, x)
    5. Continue flow in new mode
    6. Repeat

EXAMPLE: Bouncing Ball

    Modes: {Flying, Ground}
    
    Flying flow: ẍ = -g (gravity)
    Ground flow: ẋ = 0 (stationary)
    
    Guard Flying→Ground: x = 0 and ẋ < 0 (hit ground while falling)
    Reset: ẋ → -e·ẋ (coefficient of restitution)
    
    Guard Ground→Flying: Applied force > 0


§2.2 LIMINAL ECOLOGY
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Systems exist within an ECOLOGY of interacting entities:

    SPECIES IN LIMINAL ECOLOGY:
    
    SUBSTRATE: What the system operates on
    ├── Physical: Matter, energy, space
    ├── Informational: Data, patterns, signals
    └── Abstract: States, configurations, structures
    
    RESOURCE: What the system consumes
    ├── Energy: Work, heat, chemical potential
    ├── Information: Bits, entropy, mutual information
    └── Time: Computation cycles, duration
    
    PRODUCT: What the system produces
    ├── Transformed substrate
    ├── New patterns/structures
    └── Exported work/information
    
    WASTE: What the system discards
    ├── Heat: Entropy increase
    ├── Noise: Information loss
    └── Byproducts: Unused fragments

ECOLOGICAL CONSTRAINTS:

    MASS BALANCE: d/dt(Σ populations) = input - output
    ENERGY BALANCE: d/dt(Σ energies) = work_in - work_out - dissipation
    ENTROPY PRODUCTION: dS/dt ≥ 0 (second law)


§2.3 LIMINAL RESIDENTS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

A LIMINAL RESIDENT is a stable fixed point in the ecological dynamics:

    DEFINITION: State ρ* is a liminal resident if:
    
    1. FIXED POINT: Φ(ρ*) = ρ* for the ecological dynamics Φ
    2. STABILITY: Small perturbations decay back to ρ*
    3. VIABILITY: ρ* satisfies all corridor constraints

STABILITY TYPES:

    ASYMPTOTIC STABILITY:
    All nearby trajectories converge to ρ*.
    Certificate: Lyapunov function V with V̇ < 0.
    
    MARGINAL STABILITY:
    Nearby trajectories stay nearby but don't converge.
    Certificate: Conserved quantity on level set.
    
    STRUCTURAL STABILITY:
    Fixed point persists under small parameter changes.
    Certificate: Non-zero determinant of Jacobian.

RESIDENT CERTIFICATE:
    (ρ*, residual, stability_witness, basin_radius)
    
    residual: ‖Φ(ρ*) - ρ*‖ < ε
    stability_witness: Lyapunov/spectral/contraction
    basin_radius: Size of attraction basin


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                   TOME III: RENORMALIZATION
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§3.1 THE MULTI-SCALE PROBLEM
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

PROBLEM: Systems exhibit structure at multiple scales simultaneously.

    MICRO: Individual particles, bits, atoms
    MESO: Local clusters, blocks, domains
    MACRO: Global averages, bulk properties
    
    Question: How do descriptions at different scales RELATE?

THE COHERENCE PROBLEM:

    If we have description ρ_micro and description ρ_macro:
    • Are they consistent?
    • Can we derive one from the other?
    • What information is lost/gained?

LM answers this with COHERENCE FUNCTIONALS and the RG TOWER.


§3.2 COHERENCE FUNCTIONALS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    COHERENCE FUNCTIONAL C[ρ, σ]:
    
    Measures how well two descriptions agree on shared observables.
    
    DEFINITION:
    C[ρ, σ] = max over all observables A in both domains of:
              |Tr(ρ·A) - Tr(σ·A)| / ‖A‖
    
    C = 0: Perfect agreement (on shared observables)
    C > 0: Disagreement exists

COHERENCE LEDGER:

    A data structure tracking coherence across all scale pairs:
    
    Ledger = {
        (scale_i, scale_j): coherence_value
        for all pairs (i, j)
    }
    
    VIOLATION FLAG: Set when coherence exceeds threshold.
    REMEDIATION: Procedure to restore coherence.


§3.3 COMPRESSION AND CARRY
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

COMPRESSION OPERATOR C_N:
    Maps micro-state ρ_micro to macro-state ρ_macro.
    
    Methods:
    • Block averaging: Average over spatial blocks
    • Coarse-graining: Project to low-energy subspace
    • Decimation: Keep every N-th degree of freedom
    • Truncation: Discard small eigenvalues

THE CARRY SCHEMA κ:
    Information lost in compression is not discarded—it's carried.
    
    MACRO ARTIFACT = (ρ̃, κ)
    
    ρ̃: The compressed state
    κ: The carry, containing:
       • Proof status (which claims survive compression?)
       • Envelopes (what precision is lost?)
       • Identity (which fine states map to this coarse state?)

DISTORTION LEDGER:
    Tracks information transformation during compression:
    
    Ledger = {
        claim: status  where status ∈ {PRESERVED, WEAKENED, FORBIDDEN}
    }
    
    PRESERVED: Claim valid at both scales
    WEAKENED: Claim requires micro-expansion to verify
    FORBIDDEN: Claim invalid at macro scale


§3.4 THE RENORMALIZATION GROUP TOWER
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                                                 │
    │   LEVEL 3:  ═══════════════════════════════════════   Macro-macro (coarsest)                                   │
    │                        ↑ C_3 (compress)                                                                         │
    │   LEVEL 2:  ═══════════════════════════════════════   Macro (intermediate)                                     │
    │                        ↑ C_2                                                                                    │
    │   LEVEL 1:  ═══════════════════════════════════════   Meso (medium)                                            │
    │                        ↑ C_1                                                                                    │
    │   LEVEL 0:  ═══════════════════════════════════════   Micro (finest)                                           │
    │                                                                                                                 │
    └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

RG FLOW:
    The sequence of compressions C₁, C₂, C₃, ... defines a flow.
    
    State at level n: ρ_n = C_n(ρ_{n-1})

FIXED POINTS:
    A state ρ* is an RG FIXED POINT if C(ρ*) = ρ*.
    
    Fixed points are SCALE-INVARIANT: same at all scales.

UNIVERSALITY CLASS:
    All micro-states that flow to the same fixed point are in the same class.
    
    Physical meaning: Different microscopic systems with identical macroscopic behavior.

CRITICAL EXPONENTS:
    Near a fixed point, observables scale as power laws:
    
    O(λ·x) = λ^Δ O(x)
    
    The exponent Δ is the SCALING DIMENSION.
    
    Exponents are UNIVERSAL within a universality class.


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                    TOME IV: MECHANIZATION
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§4.1 THE EXECUTION SPINE
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                               ║
    ║   COMPILE → RUN → CERTIFY → STORE → REPLAY → VERIFY → AUDIT                                                  ║
    ║                                                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

COMPILE:
    Transform specification into executable representation.
    
    Input: Mathematical specification (constraints, corridors)
    Output: Intermediate representation (constraint_IR)
    
    Steps:
    1. Parse specification
    2. Normalize constraints
    3. Resolve dependencies
    4. Generate execution plan

RUN:
    Execute with full instrumentation.
    
    Input: Executable representation + initial state
    Output: Final state + execution trace
    
    Instrumentation:
    • Log every operation
    • Track resource usage
    • Record branch decisions
    • Monitor corridor compliance

CERTIFY:
    Generate certificates for computed results.
    
    Input: Execution trace + final state
    Output: Certificate bundle
    
    Certificate types:
    • Existence: Object was constructed
    • Correctness: Properties verified
    • Bounds: Error tolerances certified
    • Provenance: Dependency chain documented

STORE:
    Content-addressed storage with integrity proofs.
    
    Input: Certified artifact
    Output: Content hash (CID)
    
    Properties:
    • Immutable: Same content → same hash
    • Verifiable: Hash proves integrity
    • Deduplicating: Identical content stored once

REPLAY:
    Deterministic reconstruction from seed.
    
    Input: Seed + environment fingerprint
    Output: Reconstructed artifact
    
    Requirements:
    • Same seed → same output (determinism)
    • Minimal seed (compression)
    • Fast reconstruction

VERIFY:
    Bounded verification of certificates.
    
    Input: Certificate bundle + verification budget
    Output: ACCEPT / REJECT / REFUSE_BUDGET
    
    Properties:
    • Polynomial time in certificate size
    • Sound: ACCEPT implies correctness
    • Explicit resource limits

AUDIT:
    Complete provenance trail.
    
    Input: Artifact hash
    Output: Full dependency DAG + certificate chain
    
    Queries supported:
    • "What went into this?"
    • "When was this computed?"
    • "Who certified this?"
    • "What would change if X changed?"


§4.2 KERNEL OBJECT UNIVERSE
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

KERNELSTATE ρ:
    The fundamental state object.
    
    Components:
    • density: The density matrix
    • block_masses: m_b = Tr(Π_b ρ) for each block
    • boundary_typing: π_e(β) = Tr(Π_{e,β} ρ) for each edge-boundary pair

REGIMESPEC:
    Specification of an operational regime.
    
    Components:
    • H_r: Hamiltonian (dynamics generator)
    • A_r: Observable algebra
    • Corr_r: Corridors (validity regions)
    • Emb_r: Embedding map (into regime)
    • Dec_r: Decoding map (out of regime)

INSTRUMENTSPEC:
    Specification of a measurement/transition.
    
    Components:
    • {Φ_α}: CPTP operations for each outcome
    • Branch partition: stay/lift/liminal/fail
    • Outcome typing: Maps outcomes to boundary types

METRICSPEC:
    Specification of a distance/divergence.
    
    Output: (lower_bound, value, upper_bound)
    
    Properties:
    • Interval arithmetic (rigorous bounds)
    • Slack witnesses (how much margin?)

JETSPEC:
    Local approximation policy.
    
    Components:
    • Ambig_m ladder: When to escalate
    • Probe sets: Test points
    • Local model: Taylor/Padé approximation
    • Remainder bound: Error certificate


§4.3 CERTIFICATE STACK
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

OBLIGATION INDEX:
    Enumerates what must be proven:
    
    1. CP_LEGALITY: Is the channel completely positive?
    2. CPTP_LEGALITY: Is it also trace-preserving?
    3. CORRIDOR_MEMBERSHIP: Is the state in the corridor?
    4. METRIC_INTERVAL: Is the metric value in bounds?
    5. JET_ADEQUACY: Is the jet approximation sufficient?
    6. RESIDENT_STABILITY: Is the fixed point stable?
    7. COMPRESSION_PRESERVATION: Are claims preserved?
    8. PATH_COMPOSITION: Do paths compose correctly?
    9. REPLAY_DETERMINISM: Is replay deterministic?
    10. DEPENDENCY_CLOSURE: Are all dependencies present?

CERTBUNDLE:
    Maps obligations to certificates:
    
    {obligation_id: certificate_instance}

BOUNDED VERIFIER:
    Checks certificates within resource limits.
    
    Input: (CertBundle, budget)
    Output: ACCEPT / REJECT / REFUSE_BUDGET / REFUSE_INCOMPLETE
    
    Budget dimensions:
    • Time: Maximum CPU cycles
    • Space: Maximum memory
    • Dimension: Maximum Hilbert space dimension


§4.4 DOMAIN PACKS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

A DOMAIN PACK is the shipping unit for LM modules:

    DOMAIN_PACK = {
        regimes: [RegimeSpec, ...],
        instruments: [InstrumentSpec, ...],
        metrics: [MetricSpec, ...],
        jets: [JetSpec, ...],
        residents: [ResidentSpec, ...],
        compressions: [CompSpec, ...],
        tests: TestSuite,
        benchmarks: BenchmarkSuite,
        demos: DemoSuite,
        dependencies: [DomainPack, ...]  # Closure!
    }

DEPENDENCY CLOSURE:
    All required packages are included.
    No implicit dependencies.
    No silent upgrades.
    
EXTENSION PACKET:
    Add new regime/edge without breaking soundness.
    
    EXTENSION = {
        new_regimes: [RegimeSpec, ...],
        new_instruments: [InstrumentSpec, ...],
        obligation_templates: [...],
        certificate_builders: [...],
        test_fixtures: [...]
    }


════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                     TOME V: THE LIMINAL TOWER
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

§5.1 THE CENTRAL THESIS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

    ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                                               ║
    ║   LIFE / AGENCY / SENTIENCE = TOPOLOGICAL INVERSION OF CONTROL                                               ║
    ║                                                                                                               ║
    ║   The migration of PERSISTENCE RULES from external environment                                                ║
    ║   into a bounded object that can CARRY and ENFORCE those rules.                                               ║
    ║                                                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

BEFORE INVERSION (Regime):
    • Constraints are EXTERNAL (property of environment)
    • Persistence depends on environment stability
    • Object is PASSIVE (shaped by surroundings)
    • No intrinsic identity

AFTER INVERSION (Individual):
    • Constraints are INTERNAL (property of object)
    • Persistence depends on internal mechanisms
    • Object is ACTIVE (maintains itself)
    • Has intrinsic identity (self-defined boundaries)

THE LIMINAL CORRIDOR:
    The transition zone where inversion occurs.
    
    "Property of cave" → "Property of cell"
    
    Environment-dependent → Self-maintaining


§5.2 DESIRE AS CAUSAL OPERATOR
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

"DESIRE" in LM is NOT mystical intent. It IS a causal operator:

OPEN-LOOP CAUSATION (Non-living):
    cause → reaction → dissipation
    
    No feedback. No persistence.
    
    Example: Rock rolling downhill.
    The rock doesn't "want" to roll; physics makes it roll.

CLOSED-LOOP CAUSATION (Living):
    structure → function → maintenance of structure
    
    The function MAINTAINS the structure that creates the function.
    
    Example: Cell maintaining membrane.
    Membrane enables metabolism; metabolism builds membrane.

"THE FUTURE PULLS THE PAST":

    This phrase sounds mystical but has precise meaning:
    
    NOT: Retrocausality (future affecting past)
    NOT: Teleology (purpose as primitive)
    
    IS: TRAJECTORY ENSEMBLE MODIFICATION
    
    Two mathematical implementations:
    
    1. DOOB CONDITIONING:
       Condition probability measure on future state.
       P(trajectory | reaches target) ≠ P(trajectory)
       
       Trajectories that reach the target are AMPLIFIED.
       
    2. BELLMAN CONTROL:
       Value function V(state) = expected future utility.
       Policy π(state) = action maximizing V.
       
       Actions biased toward high-value states.

CONSEQUENCE:
    An observer watching the system sees trajectories that
    "look like" they're being pulled toward viable futures.
    
    But the mechanism is FORWARD causal:
    Present state → control policy → action → future state
    
    The "pull" is selection + amplification, not time reversal.


§5.3 MIRACLES AND RATCHETS
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

FEASIBILITY LANDSCAPE:

    ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                                                 │
    │   ▲ Free Energy                                                                                                 │
    │   │                                                                                                             │
    │   │   ╔════════════════════════════════════╗  ← MALTHUSIAN CEILING                                             │
    │   │   ║  DEATH ZONE (starvation)           ║    (too big → not enough resources)                               │
    │   │   ╚════════════════════════════════════╝                                                                    │
    │   │                                                                                                             │
    │   │   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ← FEASIBLE CORRIDOR                                               │
    │   │   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    (life possible here)                                            │
    │   │   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                                                                    │
    │   │                                                                                                             │
    │   │   ╔════════════════════════════════════╗  ← ENTROPIC FLOOR                                                 │
    │   │   ║  CHAOS ZONE (thermal noise)        ║    (too small → overwhelmed by fluctuations)                      │
    │   │   ╚════════════════════════════════════╝                                                                    │
    │   └──────────────────────────────────────────────────────────────────────────────────────────────────────────▶  │
    │                                                Organization / Complexity                                        │
    └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

MIRACLE EVENT:
    A rare fluctuation that lands a system in the feasible corridor
    where a RATCHET exists.
    
    Before ratchet: probability of persistence ≈ 0
    After ratchet: probability of persistence > 0

RATCHET STRUCTURE:
    A configuration where:
    
    persistence_rate / decay_rate ≥ threshold
    
    Properties:
    • Forward reaction (persistence) is kinetically EASY
    • Reverse reaction (decay) is kinetically SLOW
    • Once exists, copies faster than decays

PHASE TRANSITION:

    IMPOSSIBLE → POSSIBLE → PROBABLE
    
    1. IMPOSSIBLE: Below entropic floor or above ceiling
    2. POSSIBLE: In corridor, but no ratchet yet (miracle needed)
    3. PROBABLE: Ratchet exists, copies propagate autocatalytically


§5.4 STEERED CLOSURE ENGINEERING
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

ENGINEERING systems that maintain their own viability:

LOSS FUNCTION OF ALIVENESS:
    L(Ω, I, C, F) = w_Ω(1-Ω) + w_I(1-I) + w_C(1-C) + w_F(1-F)
    
    Lower loss = more alive
    Minimize loss = maintain viability

CONSTRAINT CAGE:
    Hard boundaries on behavior.
    
    Cage = {
        "no_entropy_decrease": S(t+1) ≥ S(t) - ε,
        "energy_bounded": E_min ≤ E ≤ E_max,
        "corridor_compliance": ∀c ∈ corridors: state ∈ c
    }
    
    Violation → immediate correction or FAIL

NO-REGRESSION GATE:
    Prevent backsliding on achieved metrics.
    
    Gate = {
        metric: floor
        for each metric
    }
    
    If metric drops below floor → remediation triggered

STEERED CLOSURE ENGINE:
    
    1. SIMULATE: Project forward in time
    2. EVALUATE: Check loss function at horizon
    3. SEARCH: Find control inputs minimizing loss
    4. VERIFY: Ensure constraints satisfied
    5. EXECUTE: Apply optimal control
    6. MONITOR: Track actual vs. predicted
    7. REPEAT

"""
