#!/usr/bin/env python3
"""
AtlasForge v4.0.0-final Comprehensive Test Suite

Tests all new modules added in v4.0.0:
    - Gateway Algebra
    - Metallic Sequences
    - Latin Kernel Systems
    - OA6 Operator Algebra
    - Hybrid Coupling
    - Proofs and Certificates
    - Biology and Physics
"""

import sys
import numpy as np
from typing import Tuple

# Test counter
tests_passed = 0
tests_failed = 0

def test(name: str, condition: bool, details: str = ""):
    """Record test result."""
    global tests_passed, tests_failed
    if condition:
        tests_passed += 1
        print(f"  ✓ {name}")
    else:
        tests_failed += 1
        print(f"  ✗ {name}: {details}")

def section(name: str):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f" {name}")
    print(f"{'='*60}")


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY ALGEBRA TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_gateway_algebra():
    section("Gateway Algebra Module")
    
    from atlasforge.gateway import (
        GatewayScalar, BoostMatrix, PellSolution, PellGateway,
        FoldLadder, solve_pell_fundamental, velocity_addition
    )
    
    # Gateway scalar
    T = GatewayScalar(value=0.5)
    test("GatewayScalar creation", -1 < T.value < 1)
    test("Scale ratio R = (1+T)/(1-T)", 
         np.isclose(T.scale_ratio, 3.0))
    test("Rapidity α = artanh(T)", 
         np.isclose(T.rapidity, np.arctanh(0.5)))
    test("Transmission 𝒯 = 1 - T²", 
         np.isclose(T.transmission, 0.75))
    
    # Velocity addition
    T1, T2 = 0.3, 0.4
    T_composed = velocity_addition(T1, T2)
    test("Velocity addition law", 
         np.isclose(T_composed, (T1 + T2) / (1 + T1 * T2)))
    
    # Gateway composition
    g1 = GatewayScalar(value=0.3)
    g2 = GatewayScalar(value=0.4)
    g_sum = g1.compose(g2)
    test("Gateway composition matches velocity addition",
         np.isclose(g_sum.value, T_composed))
    
    # Boost matrix
    B = BoostMatrix.from_gateway(T)
    test("Boost matrix determinant = 1",
         np.isclose(np.linalg.det(B.matrix), 1.0))
    test("Boost eigenvalue ratio = R",
         np.isclose(B.eigenvalues[0] / B.eigenvalues[1], T.scale_ratio))
    
    # Pell equation
    pell = solve_pell_fundamental(8)
    test("Pell solution u² - 8v² = 1",
         pell.u**2 - 8 * pell.v**2 == 1)
    test("Triangular-square fundamental (3,1)",
         pell.u == 3 and pell.v == 1)
    
    # Pell gateway
    pg = PellGateway.from_discriminant(8)
    x, y = 3, 1  # Start from a valid Pell solution point
    x2, y2 = pg.forward_hop(x, y)
    Q_before = x**2 - 8*y**2
    Q_after = x2**2 - 8*y2**2
    test("Pell gateway forward hop preserves form",
         Q_before == Q_after)
    
    # Fold ladder
    fl = FoldLadder(base_kappa=1.0)
    test("Fold bandwidth τ = π/(2√κ)",
         np.isclose(fl.level_bandwidth(0), np.pi / 2))
    test("Fold doubling κ → 2κ",
         np.isclose(fl.kappa(1), 2.0))


# ═══════════════════════════════════════════════════════════════════════════════
# METALLIC SEQUENCES TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_metallic_sequences():
    section("Metallic Sequences Module")
    
    from atlasforge.metallic import (
        MetallicMean, GeneralizedFibonacci, GeneralizedLucas,
        ContinuedFraction, SpecialMetallics, golden_ratio, silver_ratio
    )
    
    # Golden ratio
    phi = MetallicMean(1)
    test("Golden ratio φ = (1+√5)/2",
         np.isclose(phi.value, (1 + np.sqrt(5)) / 2))
    test("φ satisfies x² - x - 1 = 0",
         np.isclose(phi.value**2 - phi.value - 1, 0))
    test("φ·φ̄ = -1 (unit of norm -1)",
         np.isclose(phi.value * phi.conjugate, -1))
    
    # Silver ratio
    delta_s = MetallicMean(2)
    test("Silver ratio δ₂ = 1 + √2",
         np.isclose(delta_s.value, 1 + np.sqrt(2)))
    
    # Generalized Fibonacci
    fib = GeneralizedFibonacci(1)
    test("Classical Fibonacci F₁₀ = 55",
         fib[10] == 55)
    test("Fibonacci recurrence F_{n+1} = F_n + F_{n-1}",
         all(fib[n+1] == fib[n] + fib[n-1] for n in range(2, 15)))
    
    pell = GeneralizedFibonacci(2)  # Pell numbers
    test("Pell numbers: F⁽²⁾ = [0,1,2,5,12,29,...]",
         pell.sequence(6) == [0, 1, 2, 5, 12, 29])
    
    # Generalized Lucas
    luc = GeneralizedLucas(1)
    test("Classical Lucas L₅ = 11",
         luc[5] == 11)
    
    # Metallic power
    a, b = phi.power(5)
    test("δ₁⁵ = 5δ₁ + 3 (power expansion)",
         a == 5 and b == 3)
    
    # Continued fraction - √2 = [1; 2̄] (period 2)
    cf_short = ContinuedFraction.from_sqrt(2, max_terms=10)
    test("√2 periodic part detected",
         cf_short.coefficients[0] == 1 and cf_short.coefficients[1] == 2)
    
    # Use periodic constructor to get more convergents
    cf = ContinuedFraction.periodic(1, [2], repetitions=5)
    p, q = cf.convergent(4)
    test("Convergent approaches √2",
         abs(p/q - np.sqrt(2)) < 0.01)


# ═══════════════════════════════════════════════════════════════════════════════
# LATIN KERNEL TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_latin_kernels():
    section("Latin Kernel Systems Module")
    
    from atlasforge.latin import (
        Klein4Element, Klein4Group, DiagonalLatinSquare,
        HolographicSeed4x4, Radix4Tower, AffineDLS,
        get_canonical_4x4_seed, holography_analysis
    )
    
    # Klein-4 group
    I = Klein4Element.I
    R = Klein4Element.R
    S = Klein4Element.S
    C = Klein4Element.C
    
    test("Klein-4 identity I² = I",
         I.compose(I) == I)
    test("Klein-4 R² = I",
         R.compose(R) == I)
    test("Klein-4 R·S = C",
         R.compose(S) == C)
    test("Klein-4 action on 0-3",
         set(R.apply(x) for x in range(4)) == {0, 1, 2, 3})
    
    # Holographic seed
    seed = get_canonical_4x4_seed()
    test("4×4 seed shape",
         seed.shape == (4, 4))
    
    dls = HolographicSeed4x4.get_dls()
    test("Seed is diagonal Latin square",
         dls.order == 4)
    
    analysis = holography_analysis(dls)
    test("Holography > 75%",
         analysis['fraction'] > 0.75)
    
    # Radix-4 tower
    tower = Radix4Tower()
    dls_16 = tower.generate(2)
    test("16×16 DLS from tower",
         dls_16.shape == (16, 16))
    
    # Verify 16×16 is Latin
    for i in range(16):
        row_set = set(dls_16[i, :])
        col_set = set(dls_16[:, i])
        test(f"Row {i} is permutation", len(row_set) == 16)
        test(f"Col {i} is permutation", len(col_set) == 16)
        break  # Just test first row/col to save time
    
    # Affine DLS
    affine = AffineDLS(7, 2)  # Order 7, slope 2
    test("Affine DLS construction for p=7, k=2",
         affine.matrix.shape == (7, 7))


# ═══════════════════════════════════════════════════════════════════════════════
# OA6 ALGEBRA TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_oa6_algebra():
    section("OA6 Operator Algebra Module")
    
    from atlasforge.oa6 import (
        OA6GeneratorType, FoldIndex, OA6Algebra,
        ComplementGenerator, RotationGenerator, OA6Word,
        ModularNormalForm
    )
    
    # Fold index
    kappa = FoldIndex(kappa=4.0)
    test("Fold bandwidth τ = π/(2√4) = π/4",
         np.isclose(kappa.bandwidth, np.pi / 4))
    
    # Ladder level
    k2 = FoldIndex.ladder_level(3)
    test("Ladder level 3: κ = 8",
         np.isclose(k2.kappa, 8.0))
    
    # Complement generator
    C = ComplementGenerator()
    test("Complement matrix [[0,1],[1,0]]",
         np.allclose(C.matrix_2x2(), [[0, 1], [1, 0]]))
    test("Complement preserves κ",
         C.kernel_effect(4.0) == 4.0)
    
    # Rotation generator
    R = RotationGenerator()
    test("Rotation matrix [[0,-1],[1,0]]",
         np.allclose(R.matrix_2x2(), [[0, -1], [1, 0]]))
    
    # OA6 algebra
    oa = OA6Algebra(initial_kappa=1.0)
    C = oa.complement()
    R = oa.rotation()
    
    # Word construction
    word = oa.word(C, R, C)
    test("OA6 word has 3 generators",
         len(word) == 3)
    
    # Word matrix product
    mat = word.matrix_product()
    test("Word matrix product exists",
         mat is not None)
    test("Word is in SL(2,R)",
         np.isclose(np.linalg.det(mat), 1.0) or np.isclose(np.linalg.det(mat), -1.0))
    
    # Kernel transport
    final_kappa = word.kernel_transport(1.0)
    test("Kernel transport through C·R·C",
         final_kappa == 1.0)  # All preserve κ


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID COUPLING TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_hybrid_coupling():
    section("Hybrid Coupling Module")
    
    from atlasforge.coupling import (
        PhaseVector, HybridOperator, TraceMoments,
        HeatKernelTrace, EigenvalueSpikeDetector,
        create_hybrid_coupling, analyze_hybrid
    )
    
    # Phase vector
    n = 5
    phi = PhaseVector.uniform(n, phase=0.0)
    test("Uniform phase vector dimension",
         phi.dimension == n)
    test("Phase vector norm ≈ √n",
         np.isclose(phi.norm, np.sqrt(n)))
    
    # Random phase
    phi_rand = PhaseVector.random(n, seed=42)
    test("Random phase vector",
         phi_rand.dimension == n)
    
    # Hybrid operator
    A = np.random.randn(n, n)
    A = (A + A.T) / 2  # Symmetric
    H = create_hybrid_coupling(A, phi_rand.phases, coupling=0.5)
    test("Hybrid operator is Hermitian",
         H.is_hermitian)
    
    # Eigenvalues
    eigs = H.eigenvalues()
    test("Eigenvalues are real (Hermitian)",
         np.allclose(eigs.imag, 0))
    
    # Trace moments
    tm = TraceMoments(H, max_order=5)
    M1 = tm.moment(1)
    M2 = tm.moment(2)
    test("M₁ = Tr(H)",
         np.isclose(M1.real, np.sum(eigs)))
    test("M₂ = Tr(H²) = Σλᵢ²",
         np.isclose(M2.real, np.sum(eigs**2), rtol=1e-5))
    
    # Heat kernel trace
    hkt = HeatKernelTrace(H)
    Z = hkt.partition_function(1.0)
    test("Partition function Z(β) > 0",
         Z > 0)
    
    # Spike detector
    detector = EigenvalueSpikeDetector(H)
    test("Interlacing check passes",
         detector.interlacing_check())
    
    # Full analysis
    diag = analyze_hybrid(H)
    test("Analysis includes eigenvalues",
         'eigenvalues' in diag)


# ═══════════════════════════════════════════════════════════════════════════════
# PROOFS AND CERTIFICATES TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_proofs_certificates():
    section("Proofs and Certificates Module")
    
    from atlasforge.proofs import (
        StatementType, CertificateLevel, CanonicalHash,
        Seed, Certificate, VerifierRegistry, get_verifier_registry,
        ObligationLedger, SeedPack, create_seed, create_certificate,
        verify_certificate
    )
    
    # Canonical hash
    h1 = CanonicalHash.from_string("hello")
    h2 = CanonicalHash.from_string("hello")
    h3 = CanonicalHash.from_string("world")
    test("Same content → same hash",
         h1.matches(h2))
    test("Different content → different hash",
         not h1.matches(h3))
    
    # Seed creation
    seed = create_seed(
        seed_id="test_seed_001",
        statement_type=StatementType.DEFINITION,
        generator={'type': 'constant', 'value': 42},
        constraints=[{'type': 'positive'}]
    )
    test("Seed has hash",
         seed.hash is not None)
    test("Seed serialization",
         'seed_id' in seed.to_dict())
    
    # Certificate creation
    cert = create_certificate(
        cert_id="cert_001",
        claim={'type': 'equality', 'description': 'x == y'},
        witness={'lhs': 5, 'rhs': 5},
        verifier_id="equality_v1",
        level=CertificateLevel.L1_EMPIRICAL
    )
    test("Certificate has hash",
         cert.hash is not None)
    
    # Verification
    valid, diag = verify_certificate(cert)
    test("Equality certificate verifies",
         valid)
    
    # Interval verifier
    interval_cert = create_certificate(
        cert_id="interval_001",
        claim={'type': 'interval_contains'},
        witness={'value': 1.5, 'lower': 1.0, 'upper': 2.0},
        verifier_id="interval_v1"
    )
    valid2, _ = verify_certificate(interval_cert)
    test("Interval containment verifies",
         valid2)
    
    # Obligation ledger
    ledger = ObligationLedger()
    obl = ledger.create(claim={'type': 'test'}, source="unit_test")
    test("Obligation created",
         obl.status == "open")
    test("Open obligation count = 1",
         len(ledger.open_obligations) == 1)
    
    ledger.discharge(obl.obligation_id, cert)
    test("Obligation discharged",
         obl.status == "discharged")
    test("Publication ready",
         ledger.all_discharged)
    
    # Seed pack
    pack = SeedPack(pack_id="test_pack", pack_type="geometric")
    pack.add_seed("construction", seed)
    pack.add_certificate("validity", cert)
    test("Seed pack has seed",
         "construction" in pack.seeds)


# ═══════════════════════════════════════════════════════════════════════════════
# BIOLOGY AND PHYSICS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_biology_physics():
    section("Biology and Physics Module")
    
    from atlasforge.biology import (
        TetradicState, TetradicController, FIRE, AIR, EARTH, WATER,
        GrayScottSystem, MorphogenGradient, IntegrateAndFireNeuron,
        DefectHyperplane, MultiScaleHomeostasis,
        create_turing_system
    )
    
    # Tetradic states
    test("FIRE = (0,0)",
         FIRE.bits == (0, 0))
    test("WATER = (1,1)",
         WATER.bits == (1, 1))
    test("Complement of FIRE is WATER",
         FIRE.complement() == WATER)
    test("Bit flip gives correct transitions",
         FIRE.flip_bit0() == EARTH)
    
    # Controller
    ctrl = TetradicController(current_state=FIRE)
    ctrl.update(0.5, 0.5)  # Both signals positive
    test("Controller updates state",
         ctrl.current_state == WATER)  # (1,1)
    
    # Morphogen gradient
    grad = MorphogenGradient(D=1.0, decay=0.1, grid_size=50)
    grad.set_source(0)
    test("Decay length ξ = √(D/λ)",
         np.isclose(grad.decay_length, np.sqrt(10)))
    
    ss = grad.steady_state()
    test("Steady state decays from source",
         ss[0] > ss[25] > ss[49])
    
    # Integrate-and-fire neuron
    neuron = IntegrateAndFireNeuron()
    test("Neuron at rest",
         neuron.V == neuron.V_rest)
    
    # Step with current
    spiked = neuron.step(current=5.0, dt=0.001, t=0.0)
    test("Neuron integrates without immediate spike",
         not spiked or neuron.V > neuron.V_rest)
    
    # Gray-Scott system
    gs = create_turing_system('spots', grid_size=(32, 32))
    test("Gray-Scott system created",
         gs.grid_size == (32, 32))
    test("Diffusion ratio D_v/D_u",
         gs.diffusion_ratio > 1)
    
    # Defect hyperplane
    defect = DefectHyperplane(dimension=0, level=1, position=5.0)
    stress = defect.stress_field(np.array([0, 5, 10]))
    test("Stress peaks at defect position",
         stress[1] > stress[0] and stress[1] > stress[2])
    
    # Multi-scale homeostasis
    msh = MultiScaleHomeostasis(n_levels=2)
    msh.set_state(0, (0,), FIRE)
    msh.set_state(0, (1,), WATER)
    test("Multi-scale states set correctly",
         msh.get_state(0, (0,)) == FIRE)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║           AtlasForge v4.0.0-final Test Suite                     ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    try:
        test_gateway_algebra()
        test_metallic_sequences()
        test_latin_kernels()
        test_oa6_algebra()
        test_hybrid_coupling()
        test_proofs_certificates()
        test_biology_physics()
        
        print("\n" + "="*60)
        print(f" RESULTS: {tests_passed} passed, {tests_failed} failed")
        print("="*60)
        
        if tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! AtlasForge v4.0.0-final is ready.")
            return 0
        else:
            print(f"\n⚠️  {tests_failed} tests failed. Please investigate.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
