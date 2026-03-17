"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ATLAS FORGE - Examples & Tutorials                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Comprehensive examples demonstrating the AtlasForge framework capabilities.
"""

import math
from typing import Callable, List, Tuple


def example_1_basic_root_finding():
    """
    Example 1: Basic Root Finding
    
    Find √2 by solving x² - 2 = 0
    """
    from atlasforge import (
        RootConstraint, Interval, Blueprint, RecipeExecutor, SolvePlan
    )
    
    print("=" * 60)
    print("Example 1: Basic Root Finding")
    print("=" * 60)
    
    # Define the constraint H(x) = x² - 2 = 0
    H = lambda x: x**2 - 2
    
    # Create constraint with search domain
    constraint = RootConstraint(H=H, domain=Interval.closed(1, 2))
    
    # Build blueprint
    blueprint = Blueprint(constraint=constraint, name="sqrt_2")
    
    # Execute with default plan
    executor = RecipeExecutor()
    recipe = executor.execute(blueprint)
    
    print(f"Constraint: x² - 2 = 0")
    print(f"Domain: [1, 2]")
    print(f"Solution: {recipe.solution}")
    print(f"Residual: {recipe.output.residual:.2e}")
    print(f"Success: {recipe.success}")
    print(f"Verified: {recipe.verified}")
    print(f"Certificate Level: {recipe.certificate_level}")
    print()
    
    return recipe


def example_2_multiple_solvers():
    """
    Example 2: Comparing Multiple Solvers
    
    Solve the same problem with different methods.
    """
    from atlasforge import (
        Interval, BisectionSolver, NewtonSolver, BrentSolver, 
        SecantSolver, IntervalNewtonSolver
    )
    
    print("=" * 60)
    print("Example 2: Comparing Multiple Solvers")
    print("=" * 60)
    
    H = lambda x: x**3 - x - 2  # Has root near 1.52
    domain = Interval.closed(1, 2)
    
    solvers = [
        ("Bisection", BisectionSolver(tol=1e-12)),
        ("Newton", NewtonSolver(tol=1e-12)),
        ("Secant", SecantSolver(tol=1e-12)),
        ("Brent", BrentSolver(tol=1e-12)),
        ("Interval Newton", IntervalNewtonSolver(tol=1e-12)),
    ]
    
    print(f"Solving: x³ - x - 2 = 0 on [1, 2]")
    print("-" * 60)
    
    for name, solver in solvers:
        result = solver.solve(H, domain)
        verified = "✓" if result.enclosure_verified else " "
        print(f"{name:15} | x* = {result.solution:.10f} | "
              f"iter = {result.iterations:3d} | verified: {verified}")
    
    print()
    return


def example_3_lens_transformations():
    """
    Example 3: Solving in Transformed Coordinates
    
    Use logarithmic lens to solve multiplicative problems.
    """
    from atlasforge import LogLens, ExpLens, PhiLens
    
    print("=" * 60)
    print("Example 3: Lens Transformations")
    print("=" * 60)
    
    # LogLens transforms multiplication to addition
    log = LogLens()
    
    a, b = 3.0, 4.0
    
    # In log space: log(a) + log(b) = log(a*b)
    log_a = log.forward(a)
    log_b = log.forward(b)
    log_sum = log_a + log_b
    product = log.inverse(log_sum)
    
    print("LogLens: Multiplication as Addition")
    print(f"  a = {a}, b = {b}")
    print(f"  log(a) = {log_a:.6f}, log(b) = {log_b:.6f}")
    print(f"  log(a) + log(b) = {log_sum:.6f}")
    print(f"  exp(log(a) + log(b)) = {product:.6f}")
    print(f"  a × b = {a * b}")
    print()
    
    # PhiLens maps to unit circle
    phi = PhiLens()
    x = math.e  # e maps to e^i = cos(1) + i*sin(1)
    z = phi.forward(x)
    
    print("PhiLens: Spectral Mapping")
    print(f"  Φ(e) = e^(i·ln(e)) = e^i")
    print(f"       = {z}")
    print(f"  |Φ(e)| = {abs(z):.6f}")
    print()
    
    return


def example_4_certificate_levels():
    """
    Example 4: Certificate Hierarchy
    
    Demonstrate the four certificate levels.
    """
    from atlasforge import (
        CertificateLevel, CertificateFactory, CertificateBundle,
        Interval, TruthProfile
    )
    
    print("=" * 60)
    print("Example 4: Certificate Hierarchy")
    print("=" * 60)
    
    print("Certificate Levels:")
    for level in CertificateLevel:
        print(f"  {level.name}: {level.value}")
    print()
    
    # Create certificates at different levels
    bundle = CertificateBundle()
    
    # L1: Empirical (numerical testing)
    cert_l1 = CertificateFactory.enclosure(
        solution=1.414,
        enclosure=Interval.closed(1.41, 1.42),
        residual=0.001,
        verified=False
    )
    bundle.add(cert_l1)
    print(f"L1 (Empirical) Certificate: residual = {cert_l1.residual}")
    
    # L2: Certified (interval arithmetic)
    cert_l2 = CertificateFactory.enclosure(
        solution=1.41421356,
        enclosure=Interval.closed(1.414213562, 1.414213564),
        residual=1e-12,
        verified=True
    )
    bundle.add(cert_l2)
    print(f"L2 (Certified) Certificate: enclosure width = {cert_l2.enclosure.width:.2e}")
    
    print()
    print(f"Bundle level: {bundle.level.name}")
    print(f"All valid: {bundle.all_valid}")
    print()
    
    return bundle


def example_5_crystal_combat():
    """
    Example 5: Crystal Combat Solver
    
    Card-based algorithmic fighting.
    """
    from atlasforge import (
        CrystalSolver, CrystalDeck, StandardCards, ZStarLock,
        AdaptivePivot, Interval
    )
    
    print("=" * 60)
    print("Example 5: Crystal Combat Solver")
    print("=" * 60)
    
    # Define problem
    H = lambda x: x**2 - 2
    domain = Interval.closed(1, 2)
    
    # Create custom deck
    deck = CrystalDeck(max_energy=50.0, energy_regen=5.0)
    deck.add_card(StandardCards.newton_step(H))
    bracket = [1.0, 2.0]
    deck.add_card(StandardCards.bisect_step(H, bracket))
    deck.add_card(StandardCards.project_to_interval(domain))
    
    # Create solver with adaptive pivot
    solver = CrystalSolver(
        deck=deck,
        pivot_rule=AdaptivePivot(high_threshold=0.1, low_threshold=0.001),
        tolerance=1e-10,
        max_turns=100
    )
    
    # Solve
    result = solver.solve(H, x0=1.5, domain=domain)
    
    print(f"Problem: x² - 2 = 0")
    print(f"Initial guess: x₀ = 1.5")
    print()
    print(f"Combat Result:")
    print(f"  Solution: {result.solution:.10f}")
    print(f"  Turns: {result.turns}")
    print(f"  Cards played: {result.cards_played}")
    print(f"  Total cost: {result.total_cost}")
    print(f"  Converged: {result.converged}")
    print(f"  Z* Locked: {result.locked}")
    print()
    
    # Show card history (last 5)
    if result.card_history:
        print("Last 5 cards played:")
        for card in result.card_history[-5:]:
            print(f"    - {card}")
    print()
    
    return result


def example_6_hybrid_system():
    """
    Example 6: Hybrid Dynamical System
    
    Continuous flow with discrete mode switches.
    """
    from atlasforge import (
        HybridState, HybridSystem, LinearFlow, Guard, Reset, Transition
    )
    
    print("=" * 60)
    print("Example 6: Hybrid Dynamical System")
    print("=" * 60)
    
    # Bouncing ball (simplified)
    # Mode 0: falling (dx/dt = -g)
    # Mode 1: contact (reset velocity)
    
    g = 9.8
    restitution = 0.8
    
    # Flows
    fall_flow = LinearFlow(a=0.0, b=-g)  # dx/dt = -g (velocity decreasing)
    
    # Guard: v < 0 (hit ground, simplified)
    guard_01 = Guard(
        predicate=lambda x, t, m: x < 0.1,
        source_mode=0,
        target_mode=0  # Stay in mode 0, just reset
    )
    
    # Reset: reverse and dampen velocity
    reset_01 = Reset(lambda x, t: abs(x) * restitution)
    
    transition = Transition(guard=guard_01, reset=reset_01, priority=1)
    
    system = HybridSystem(
        flows={0: fall_flow},
        transitions=[transition]
    )
    
    # Simulate
    initial = HybridState(continuous=10.0, mode=0, time=0.0)
    
    print("Bouncing Ball Simulation")
    print(f"Initial velocity: {initial.continuous}")
    print(f"Restitution: {restitution}")
    print()
    
    state = initial
    for i in range(5):
        state, jumped = system.step(state, dt=0.1)
        print(f"  t={state.time:.2f}: v={state.continuous:.4f}, jumps={state.jump_count}")
    
    print()
    return


def example_7_four_poles():
    """
    Example 7: Four-Pole Architecture
    
    Demonstrating the D-Ω-Σ-Ψ system.
    """
    from atlasforge import (
        Pole, FireArchetype, AirArchetype, WaterArchetype, EarthArchetype,
        RotationEngine, PoleCoefficients, OperatorSimplex
    )
    
    print("=" * 60)
    print("Example 7: Four-Pole Architecture")
    print("=" * 60)
    
    print("The Four Poles:")
    print(f"  D (Fire)  - Dissipation, Gradient descent, Decay")
    print(f"  Ω (Air)   - Oscillation, Rotation, Spectral")
    print(f"  Σ (Water) - Stochastic, Sampling, Probabilistic")
    print(f"  Ψ (Earth) - Recursive, Discrete, Combinatorial")
    print()
    
    # Archetypes and their characteristics
    archetypes = [
        ("Fire (D)", FireArchetype()),
        ("Air (Ω)", AirArchetype()),
        ("Water (Σ)", WaterArchetype()),
        ("Earth (Ψ)", EarthArchetype()),
    ]
    
    print("Archetype Characteristics:")
    for name, arch in archetypes:
        print(f"  {name}: pole={arch.pole.value}, element={arch.element.value}")
    print()
    
    # Rotation engine - demonstrates clockwise rotation
    engine = RotationEngine(current=FireArchetype())
    print("Pole Rotation (Fire → Air → Water → Earth → Fire):")
    print(f"  Start: {engine.current.element.value}")
    for i in range(4):
        engine.rotate_clockwise()
        print(f"    → {engine.current.element.value}")
    print()
    print()
    
    # Simplex coordinates
    coeffs = PoleCoefficients(alpha_d=0.6, alpha_omega=0.2, alpha_sigma=0.1, alpha_psi=0.1)
    print(f"Simplex position: D={coeffs.alpha_d}, Ω={coeffs.alpha_omega}, Σ={coeffs.alpha_sigma}, Ψ={coeffs.alpha_psi}")
    print(f"Dominant pole: {coeffs.dominant_pole.value}")
    print(f"On simplex: {coeffs.on_simplex}")
    print()
    
    return


def example_8_full_pipeline():
    """
    Example 8: Complete Pipeline with Verification
    
    Full PARSE → NORMALIZE → PLAN → SOLVE → CERTIFY → VERIFY flow.
    """
    from atlasforge import (
        RootConstraint, Interval, Blueprint, SolvePlan, RecipeExecutor,
        Validator, Registry, TruthProfile
    )
    
    print("=" * 60)
    print("Example 8: Complete Pipeline")
    print("=" * 60)
    
    # 1. Define problem
    print("1. DEFINE: H(x) = x³ - 2x - 5 = 0 on [2, 3]")
    H = lambda x: x**3 - 2*x - 5
    constraint = RootConstraint(H=H, domain=Interval.closed(2, 3))
    
    # 2. Create blueprint with PROVE profile
    print("2. BLUEPRINT: TruthProfile.PROVE (requires L2+ certificates)")
    blueprint = Blueprint(
        constraint=constraint,
        truth_profile=TruthProfile.PROVE,
        name="cubic_root_example"
    )
    
    # 3. Create verified solve plan
    print("3. PLAN: Using verified solver chain")
    plan = SolvePlan.verified()
    
    # 4. Execute
    print("4. EXECUTE: PARSE → NORMALIZE → PLAN → SOLVE → CERTIFY")
    executor = RecipeExecutor()
    recipe = executor.execute(blueprint, plan)
    
    # 5. Verify
    print("5. VERIFY: Independent verification")
    validator = Validator()
    verified, msg = validator.verify_solution(H, recipe.solution)
    
    # 6. Register
    print("6. REGISTER: Store in content-addressed registry")
    registry = Registry()
    recipe_hash = registry.register(recipe)
    
    print()
    print("Results:")
    print(f"  Solution: x* = {recipe.solution:.12f}")
    print(f"  H(x*) = {H(recipe.solution):.2e}")
    print(f"  Pipeline Success: {recipe.success}")
    print(f"  Verified: {recipe.verified}")
    print(f"  Independent Verification: {verified}")
    print(f"  Certificate Level: {recipe.certificate_level}")
    print(f"  Recipe Hash: {recipe_hash[:16]}...")
    print(f"  Registry Valid: {registry.is_valid(recipe_hash)}")
    print()
    
    return recipe


def run_all_examples():
    """Run all examples."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " ATLAS FORGE - Examples & Tutorials ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    example_1_basic_root_finding()
    example_2_multiple_solvers()
    example_3_lens_transformations()
    example_4_certificate_levels()
    example_5_crystal_combat()
    example_6_hybrid_system()
    example_7_four_poles()
    example_8_full_pipeline()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
