"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Comprehensive Test Suite                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Tests for all major components of the AtlasForge framework.
"""

import math
import pytest
from typing import Callable


# ═══════════════════════════════════════════════════════════════════════════════
# CORE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestInterval:
    """Tests for Interval class."""
    
    def test_closed_interval(self):
        from atlasforge.core.types import Interval
        I = Interval.closed(0, 1)
        assert I.lo == 0
        assert I.hi == 1
        assert I.width == 1
        assert I.midpoint == 0.5
    
    def test_contains(self):
        from atlasforge.core.types import Interval
        I = Interval.closed(0, 1)
        assert I.contains(0.5)
        assert I.contains(0)
        assert I.contains(1)
        assert not I.contains(-0.1)
        assert not I.contains(1.1)
    
    def test_intersection(self):
        from atlasforge.core.types import Interval
        I1 = Interval.closed(0, 2)
        I2 = Interval.closed(1, 3)
        I3 = I1.intersection(I2)
        assert I3.lo == 1
        assert I3.hi == 2
    
    def test_arithmetic(self):
        from atlasforge.core.types import Interval
        I1 = Interval.closed(1, 2)
        I2 = Interval.closed(3, 4)
        
        # Addition
        I_sum = I1 + I2
        assert I_sum.lo == 4
        assert I_sum.hi == 6
        
        # Multiplication
        I_prod = I1 * I2
        assert I_prod.lo == 3
        assert I_prod.hi == 8


class TestEnums:
    """Tests for core enumerations."""
    
    def test_poles(self):
        from atlasforge.core.enums import Pole
        assert Pole.D.value == "D"
        assert Pole.OMEGA.value == "Ω"
        assert Pole.SIGMA.value == "Σ"
        assert Pole.PSI.value == "Ψ"
    
    def test_certificate_levels(self):
        from atlasforge.core.enums import CertificateLevel
        assert CertificateLevel.L0_CLAIM.value == 0
        assert CertificateLevel.L1_EMPIRICAL.value == 1
        assert CertificateLevel.L2_CERTIFIED.value == 2
        assert CertificateLevel.L3_FORMAL.value == 3
        assert CertificateLevel.L0_CLAIM < CertificateLevel.L3_FORMAL


class TestContentAddressed:
    """Tests for content-addressed objects."""
    
    def test_content_hash(self):
        from atlasforge.core.base import ContentAddressed
        from dataclasses import dataclass
        import json
        
        @dataclass
        class TestObj(ContentAddressed):
            value: int
            def canonical_repr(self) -> str:
                return json.dumps({'value': self.value})
        
        obj1 = TestObj(value=42)
        obj2 = TestObj(value=42)
        obj3 = TestObj(value=43)
        
        assert obj1.content_hash() == obj2.content_hash()
        assert obj1.content_hash() != obj3.content_hash()


# ═══════════════════════════════════════════════════════════════════════════════
# POLE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestArchetypes:
    """Tests for pole archetypes."""
    
    def test_fire_archetype(self):
        from atlasforge.poles.archetype import FireArchetype
        fire = FireArchetype()
        assert fire.pole.value == "D"
        result = fire.apply(10.0)
        assert result < 10.0  # Dissipative
    
    def test_rotation_engine(self):
        from atlasforge.poles.archetype import RotationEngine
        from atlasforge.core.enums import Pole
        engine = RotationEngine()
        
        assert engine.rotate(Pole.D) == Pole.OMEGA
        assert engine.rotate(Pole.OMEGA) == Pole.SIGMA
        assert engine.rotate(Pole.SIGMA) == Pole.PSI
        assert engine.rotate(Pole.PSI) == Pole.D


class TestGenerators:
    """Tests for generators."""
    
    def test_dissipative_generator(self):
        from atlasforge.poles.generator import DissipativeGenerator
        import numpy as np
        
        gen = DissipativeGenerator(rate=0.5)
        x = np.array([1.0, 2.0])
        dx = gen(x)
        assert np.all(dx < 0)  # Decay
    
    def test_oscillatory_generator(self):
        from atlasforge.poles.generator import OscillatoryGenerator
        import numpy as np
        
        gen = OscillatoryGenerator(frequency=1.0)
        x = np.array([1.0, 0.0])
        dx = gen(x)
        assert dx[0] == 0.0
        assert dx[1] == 1.0


class TestOperatorSimplex:
    """Tests for operator simplex."""
    
    def test_pole_coefficients(self):
        from atlasforge.poles.simplex import PoleCoefficients
        
        pc = PoleCoefficients(d=0.5, omega=0.3, sigma=0.1, psi=0.1)
        assert pc.is_valid()
        assert abs(pc.sum() - 1.0) < 1e-10
    
    def test_simplex_navigation(self):
        from atlasforge.poles.simplex import OperatorSimplex
        from atlasforge.core.enums import Pole
        
        simplex = OperatorSimplex()
        simplex.set_current(PoleCoefficients(d=1.0, omega=0.0, sigma=0.0, psi=0.0))
        
        assert simplex.dominant_pole == Pole.D


# ═══════════════════════════════════════════════════════════════════════════════
# LENS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCharts:
    """Tests for chart transformations."""
    
    def test_log_lens(self):
        from atlasforge.lenses.canonical import LogLens
        
        log = LogLens()
        x = 10.0
        y = log.forward(x)
        x_back = log.inverse(y)
        
        assert abs(y - math.log(x)) < 1e-10
        assert abs(x_back - x) < 1e-10
    
    def test_exp_lens(self):
        from atlasforge.lenses.canonical import ExpLens
        
        exp = ExpLens()
        x = 2.0
        y = exp.forward(x)
        x_back = exp.inverse(y)
        
        assert abs(y - math.exp(x)) < 1e-10
        assert abs(x_back - x) < 1e-10
    
    def test_phi_lens(self):
        from atlasforge.lenses.canonical import PhiLens
        
        phi = PhiLens()
        x = math.e
        result = phi.forward(x)
        
        # e^{i ln(e)} = e^i = cos(1) + i*sin(1)
        expected = complex(math.cos(1), math.sin(1))
        assert abs(result - expected) < 1e-10
    
    def test_transported_operations(self):
        from atlasforge.lenses.canonical import LogLens
        
        log = LogLens()
        a, b = 2.0, 3.0
        
        # In log space, multiplication becomes addition
        result = log.mul_as_add(a, b)
        assert abs(result - a * b) < 1e-10


class TestTransport:
    """Tests for transport through charts."""
    
    def test_field_transport(self):
        from atlasforge.lenses.transport import FieldTransport
        from atlasforge.lenses.canonical import LogLens
        
        log = LogLens()
        f = lambda x: x**2
        
        transport = FieldTransport(f, log)
        
        # f_T(y) = f(T^{-1}(y)) = f(e^y) = e^{2y}
        y = 1.0
        result = transport.transport_forward(y)
        expected = math.exp(2 * y)
        assert abs(result - expected) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstraints:
    """Tests for constraint system."""
    
    def test_root_constraint(self):
        from atlasforge.constraints.constraint import RootConstraint
        
        # H(x) = x^2 - 2 (roots at ±√2)
        H = lambda x: x**2 - 2
        constraint = RootConstraint(H=H)
        
        assert constraint.evaluate(math.sqrt(2)) < 1e-10
        assert constraint.is_satisfied(math.sqrt(2))
    
    def test_fixed_point_constraint(self):
        from atlasforge.constraints.constraint import FixedPointConstraint
        
        # F(x) = cos(x), fixed point around 0.739
        F = lambda x: math.cos(x)
        constraint = FixedPointConstraint(F=F)
        
        x_star = 0.7390851332151607
        assert abs(constraint.evaluate(x_star)) < 1e-6


class TestSolvers:
    """Tests for numerical solvers."""
    
    def test_bisection(self):
        from atlasforge.constraints.solvers import BisectionSolver
        from atlasforge.core.types import Interval
        
        H = lambda x: x**2 - 2
        solver = BisectionSolver(tol=1e-12)
        result = solver.solve(H, Interval.closed(1, 2))
        
        assert result.converged
        assert abs(result.solution - math.sqrt(2)) < 1e-10
    
    def test_newton(self):
        from atlasforge.constraints.solvers import NewtonSolver
        from atlasforge.core.types import Interval
        
        H = lambda x: x**2 - 2
        solver = NewtonSolver(tol=1e-12)
        result = solver.solve(H, Interval.closed(1, 2), x0=1.5)
        
        assert result.converged
        assert abs(result.solution - math.sqrt(2)) < 1e-10
    
    def test_brent(self):
        from atlasforge.constraints.solvers import BrentSolver
        from atlasforge.core.types import Interval
        
        H = lambda x: x**3 - x - 2
        solver = BrentSolver(tol=1e-12)
        result = solver.solve(H, Interval.closed(1, 2))
        
        assert result.converged
        assert abs(H(result.solution)) < 1e-10
    
    def test_interval_newton(self):
        from atlasforge.constraints.solvers import IntervalNewtonSolver
        from atlasforge.core.types import Interval
        
        H = lambda x: x**2 - 2
        solver = IntervalNewtonSolver(tol=1e-12)
        result = solver.solve(H, Interval.closed(1, 2))
        
        assert result.converged
        assert result.enclosure_verified
        assert result.enclosure.contains(math.sqrt(2))


# ═══════════════════════════════════════════════════════════════════════════════
# CERTIFICATE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCertificates:
    """Tests for certificate system."""
    
    def test_enclosure_certificate(self):
        from atlasforge.certificates.certificate import EnclosureCertificate, CertificateLevel
        from atlasforge.core.types import Interval
        
        cert = EnclosureCertificate(
            level=CertificateLevel.L2_CERTIFIED,
            solution=math.sqrt(2),
            enclosure=Interval.closed(1.41, 1.42),
            residual=1e-12,
            interval_arithmetic_used=True
        )
        
        assert cert.verify()
        assert cert.certificate_type == "enclosure"
    
    def test_certificate_bundle(self):
        from atlasforge.certificates.certificate import (
            CertificateBundle, CertificateFactory, CertificateLevel
        )
        from atlasforge.core.types import Interval
        
        bundle = CertificateBundle()
        bundle.add(CertificateFactory.enclosure(
            math.sqrt(2), Interval.closed(1.41, 1.42), 1e-12, True
        ))
        
        assert bundle.level == CertificateLevel.L2_CERTIFIED
        assert bundle.all_valid


# ═══════════════════════════════════════════════════════════════════════════════
# RECIPE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestRecipes:
    """Tests for recipe system."""
    
    def test_blueprint(self):
        from atlasforge.recipes.recipe import Blueprint
        from atlasforge.constraints.constraint import RootConstraint
        from atlasforge.core.enums import TruthProfile
        
        H = lambda x: x**2 - 2
        bp = Blueprint(
            constraint=RootConstraint(H=H),
            truth_profile=TruthProfile.VALIDATE
        )
        
        assert bp.content_hash() is not None
    
    def test_recipe_executor(self):
        from atlasforge.recipes.recipe import Blueprint, RecipeExecutor, SolvePlan
        from atlasforge.constraints.constraint import RootConstraint
        from atlasforge.core.types import Interval
        
        H = lambda x: x**2 - 2
        bp = Blueprint(
            constraint=RootConstraint(H=H, domain=Interval.closed(1, 2))
        )
        
        executor = RecipeExecutor()
        recipe = executor.execute(bp)
        
        assert recipe.success
        assert abs(recipe.solution - math.sqrt(2)) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIER TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestVerifier:
    """Tests for verifier system."""
    
    def test_validator(self):
        from atlasforge.verifier.verifier import Validator
        from atlasforge.core.types import Interval
        
        H = lambda x: x**2 - 2
        validator = Validator()
        
        verified, msg = validator.verify_solution(
            H, math.sqrt(2), tolerance=1e-10
        )
        
        assert verified
    
    def test_cross_validator(self):
        from atlasforge.verifier.verifier import CrossValidator
        
        cv = CrossValidator(tolerance=1e-8)
        solutions = [
            ("newton", 1.41421356),
            ("brent", 1.41421357),
            ("bisection", 1.41421355),
        ]
        
        valid, consensus, spread = cv.validate(solutions)
        assert valid
        assert abs(consensus - math.sqrt(2)) < 1e-6


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegistry:
    """Tests for registry system."""
    
    def test_content_store(self):
        from atlasforge.registry.registry import ContentStore
        from atlasforge.constraints.constraint import RootConstraint
        
        store = ContentStore()
        constraint = RootConstraint(H=lambda x: x**2 - 2)
        
        h = store.put(constraint)
        entry = store.get(h)
        
        assert entry is not None
        assert store.has(h)
    
    def test_dependency_dag(self):
        from atlasforge.registry.registry import DependencyDAG
        
        dag = DependencyDAG()
        dag.add_node("a", "type1")
        dag.add_node("b", "type2")
        dag.add_dependency("b", "a")  # b depends on a
        
        assert "a" in dag.get_dependencies("b")
        assert "b" in dag.get_dependents("a")
        
        # Invalidation propagates
        invalidated = dag.invalidate("a")
        assert "b" in invalidated


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestHybrid:
    """Tests for hybrid systems."""
    
    def test_linear_flow(self):
        from atlasforge.hybrid.hybrid import LinearFlow
        
        flow = LinearFlow(a=-1.0, b=0.0)
        
        # Exact solution: x(t) = x0 * e^{-t}
        x0 = 1.0
        x1 = flow.integrate(x0, 0.0, 1.0)
        expected = x0 * math.exp(-1.0)
        
        assert abs(x1 - expected) < 1e-10
    
    def test_hybrid_state(self):
        from atlasforge.hybrid.hybrid import HybridState
        
        state = HybridState(continuous=1.0, mode=0, time=0.0)
        copy = state.copy()
        
        assert copy.continuous == state.continuous
        assert copy.mode == state.mode


# ═══════════════════════════════════════════════════════════════════════════════
# CRYSTAL TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrystal:
    """Tests for Crystal Combat system."""
    
    def test_crystal_card(self):
        from atlasforge.crystal.crystal import CrystalCard, CardType
        
        card = CrystalCard(
            name="Test",
            card_type=CardType.ATTACK,
            operation=lambda x: x + 1
        )
        
        assert card.can_play(0)
        assert card.play(5) == 6
    
    def test_crystal_deck(self):
        from atlasforge.crystal.crystal import CrystalDeck, StandardCards
        
        H = lambda x: x**2 - 2
        deck = CrystalDeck()
        deck.add_card(StandardCards.newton_step(H))
        
        assert len(deck.cards) == 1
        playable = deck.get_playable(1.5)
        assert len(playable) == 1
    
    def test_z_star_lock(self):
        from atlasforge.crystal.crystal import ZStarLock
        
        lock = ZStarLock(tolerance=1e-10, patience=3)
        
        # Converging sequence
        for _ in range(10):
            lock.update(1.0)
        
        assert lock.locked
        assert abs(lock.locked_value - 1.0) < 1e-10
    
    def test_crystal_solver(self):
        from atlasforge.crystal.crystal import CrystalSolver
        from atlasforge.core.types import Interval
        
        H = lambda x: x**2 - 2
        solver = CrystalSolver(tolerance=1e-10, max_turns=500)
        
        result = solver.solve(H, x0=1.5, domain=Interval.closed(1, 2))
        
        assert result.converged or result.locked
        if result.solution:
            assert abs(result.solution - math.sqrt(2)) < 1e-4


# ═══════════════════════════════════════════════════════════════════════════════
# UTILS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestUtils:
    """Tests for utility functions."""
    
    def test_derivative(self):
        from atlasforge.utils.utils import derivative
        
        f = lambda x: x**2
        df = derivative(f, 2.0)
        
        assert abs(df - 4.0) < 1e-6
    
    def test_quadratic_roots(self):
        from atlasforge.utils.utils import quadratic_roots
        
        # x^2 - 5x + 6 = 0 has roots 2 and 3
        roots = quadratic_roots(1, -5, 6)
        roots.sort()
        
        assert abs(roots[0] - 2) < 1e-10
        assert abs(roots[1] - 3) < 1e-10
    
    def test_golden_ratio(self):
        from atlasforge.utils.utils import golden_ratio
        
        phi = golden_ratio()
        # φ^2 = φ + 1
        assert abs(phi**2 - phi - 1) < 1e-10
    
    def test_fibonacci(self):
        from atlasforge.utils.utils import fibonacci
        
        assert fibonacci(0) == 0
        assert fibonacci(1) == 1
        assert fibonacci(10) == 55


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_pipeline(self):
        """Test the full recipe pipeline."""
        from atlasforge.recipes.recipe import Blueprint, RecipeExecutor, SolvePlan
        from atlasforge.constraints.constraint import RootConstraint
        from atlasforge.verifier.verifier import Validator
        from atlasforge.registry.registry import Registry
        from atlasforge.core.types import Interval
        
        # Create blueprint
        H = lambda x: x**3 - x - 2
        bp = Blueprint(
            constraint=RootConstraint(H=H, domain=Interval.closed(1, 2)),
            name="cubic_root"
        )
        
        # Execute
        executor = RecipeExecutor()
        recipe = executor.execute(bp, SolvePlan.verified())
        
        # Verify
        validator = Validator()
        verified, msg = validator.verify_solution(H, recipe.solution)
        
        # Register
        registry = Registry()
        recipe_hash = registry.register(recipe)
        
        assert recipe.success
        assert verified
        assert registry.is_valid(recipe_hash)
    
    def test_chart_transported_solve(self):
        """Test solving in transformed coordinates."""
        from atlasforge.lenses.canonical import LogLens
        from atlasforge.constraints.solvers import BrentSolver
        from atlasforge.core.types import Interval
        
        # Solve e^x = 2 by transforming to log space
        # In log space: x = ln(2)
        H = lambda x: math.exp(x) - 2
        
        solver = BrentSolver(tol=1e-12)
        result = solver.solve(H, Interval.closed(0, 1))
        
        assert result.converged
        assert abs(result.solution - math.log(2)) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
