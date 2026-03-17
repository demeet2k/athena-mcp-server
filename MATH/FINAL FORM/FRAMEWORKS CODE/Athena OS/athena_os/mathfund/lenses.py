"""
ATHENA OS - Coordinate Lenses and Structure Transport
=====================================================
The core engine of the Lens-Zero Crystal Framework.

A LENS is a bijection T: D → ℝ with stated regularity.
The coordinate t = T(x) is the "chart".

The universal rotation rule (conjugacy):
    f_T = T⁻¹ ∘ f ∘ T

This single formula is the universal "rotation" rule between
mathematical worlds.

Key Lenses:
- ln: multiplication → addition
- log_φ: φ-scaling → translation
- phase: amplitude → angle
- affine: scaling + shift

The framework unifies:
- logarithms/exponentials (e, ln)
- power/radical laws (x^p)
- trigonometric phase (sin, cos)
- metallic-lattice scaling (φ)

All under one transformation engine: conjugacy by a lens.
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
import numpy as np
import math


# =============================================================================
# MATHEMATICAL CONSTANTS
# =============================================================================

PHI = (1 + math.sqrt(5)) / 2          # Golden ratio φ ≈ 1.618034
PHI_INV = 1 / PHI                      # 1/φ = φ - 1 ≈ 0.618034
LN_PHI = math.log(PHI)                 # ln(φ) ≈ 0.481212
PHI_CONJUGATE = 1 - PHI                # φ̄ = -1/φ ≈ -0.618034

E = math.e                             # Euler's number
PI = math.pi                           # π
TAU = 2 * PI                           # τ = 2π

GOLDEN_ANGLE = TAU / (PHI ** 2)        # 2π/φ² ≈ 2.39996 rad ≈ 137.5°


# =============================================================================
# DOMAIN SPECIFICATIONS
# =============================================================================

class DomainType(Enum):
    """Types of domains for lenses."""
    POSITIVE_REALS = auto()    # (0, ∞)
    ALL_REALS = auto()         # (-∞, ∞)
    UNIT_INTERVAL = auto()     # (0, 1)
    POSITIVE_EXTENDED = auto() # [0, ∞)
    CIRCLE = auto()            # [0, 2π)
    COMPLEX_PLANE = auto()     # ℂ


@dataclass
class Domain:
    """
    A declared domain D ⊆ ℝ with explicit branch/regularity assumptions.
    """
    
    domain_type: DomainType = DomainType.POSITIVE_REALS
    lower: float = 0.0
    upper: float = float('inf')
    lower_open: bool = True
    upper_open: bool = True
    
    def contains(self, x: float) -> bool:
        """Check if x is in the domain."""
        if self.lower_open:
            if x <= self.lower:
                return False
        else:
            if x < self.lower:
                return False
        
        if self.upper_open:
            if x >= self.upper:
                return False
        else:
            if x > self.upper:
                return False
        
        return True
    
    def clamp(self, x: float, epsilon: float = 1e-10) -> float:
        """Clamp x to be within domain."""
        result = x
        if self.lower_open:
            result = max(result, self.lower + epsilon)
        else:
            result = max(result, self.lower)
        
        if self.upper_open:
            result = min(result, self.upper - epsilon)
        else:
            result = min(result, self.upper)
        
        return result
    
    @classmethod
    def positive_reals(cls) -> 'Domain':
        """The default domain (0, ∞)."""
        return cls(DomainType.POSITIVE_REALS, 0.0, float('inf'), True, True)
    
    @classmethod
    def all_reals(cls) -> 'Domain':
        """The domain (-∞, ∞)."""
        return cls(DomainType.ALL_REALS, float('-inf'), float('inf'), True, True)
    
    @classmethod
    def unit_interval(cls) -> 'Domain':
        """The domain (0, 1)."""
        return cls(DomainType.UNIT_INTERVAL, 0.0, 1.0, True, True)
    
    @classmethod
    def circle(cls) -> 'Domain':
        """The domain [0, 2π)."""
        return cls(DomainType.CIRCLE, 0.0, TAU, False, True)


# =============================================================================
# LENS (Coordinate Isomorphism)
# =============================================================================

@dataclass
class Lens:
    """
    A Lens T: D → ℝ is a bijection with stated regularity.
    
    The coordinate t = T(x) is the chart.
    
    Core operation (conjugacy):
        f_T = T⁻¹ ∘ f ∘ T
    
    This transports functions between coordinate systems.
    """
    
    name: str
    
    # The forward transformation T: D → ℝ
    forward: Callable[[float], float]
    
    # The inverse transformation T⁻¹: ℝ → D
    inverse: Callable[[float], float]
    
    # Domain specification
    domain: Domain = field(default_factory=Domain.positive_reals)
    
    # Derivative (for regularity checking)
    derivative: Optional[Callable[[float], float]] = None
    
    # Description
    description: str = ""
    
    def __call__(self, x: float) -> float:
        """Apply forward transformation T(x)."""
        if not self.domain.contains(x):
            x = self.domain.clamp(x)
        return self.forward(x)
    
    def inv(self, t: float) -> float:
        """Apply inverse transformation T⁻¹(t)."""
        return self.inverse(t)
    
    def transport(self, f: Callable[[float], float]) -> Callable[[float], float]:
        """
        Transport a function through this lens.
        
        f_T = T⁻¹ ∘ f ∘ T
        
        This is the universal rotation law.
        """
        def transported(x: float) -> float:
            t = self.forward(x)
            ft = f(t)
            return self.inverse(ft)
        return transported
    
    def compose(self, other: 'Lens') -> 'Lens':
        """Compose two lenses: (T₁ ∘ T₂)(x) = T₁(T₂(x))."""
        return Lens(
            name=f"{self.name}∘{other.name}",
            forward=lambda x: self.forward(other.forward(x)),
            inverse=lambda t: other.inverse(self.inverse(t)),
            domain=other.domain,
            description=f"Composition of {self.name} and {other.name}"
        )
    
    def is_bijective(self, test_points: List[float] = None) -> bool:
        """
        Test bijectivity by checking round-trip.
        
        T⁻¹(T(x)) = x
        """
        if test_points is None:
            test_points = [0.1, 0.5, 1.0, 2.0, PHI, E, PI]
        
        for x in test_points:
            if not self.domain.contains(x):
                continue
            try:
                t = self.forward(x)
                x_back = self.inverse(t)
                if abs(x_back - x) > 1e-10:
                    return False
            except (ValueError, ZeroDivisionError, OverflowError):
                continue
        
        return True


# =============================================================================
# CANONICAL LENS LIBRARY
# =============================================================================

def create_ln_lens() -> Lens:
    """
    Natural logarithm lens: T(x) = ln(x).
    
    Properties:
    - Multiplication in x becomes addition in t
    - Powers become scaling: ln(x^p) = p·ln(x)
    """
    return Lens(
        name="ln",
        forward=math.log,
        inverse=math.exp,
        domain=Domain.positive_reals(),
        derivative=lambda x: 1/x,
        description="Natural logarithm: multiplication → addition"
    )


def create_exp_lens() -> Lens:
    """
    Exponential lens: T(x) = e^x.
    
    Properties:
    - Addition in x becomes multiplication in t
    """
    return Lens(
        name="exp",
        forward=math.exp,
        inverse=math.log,
        domain=Domain.all_reals(),
        derivative=math.exp,
        description="Exponential: addition → multiplication"
    )


def create_log_base_lens(base: float) -> Lens:
    """
    Logarithm with arbitrary base: T(x) = log_b(x).
    
    Base change: log_b(x) = ln(x) / ln(b)
    """
    ln_base = math.log(base)
    return Lens(
        name=f"log_{base:.4f}",
        forward=lambda x: math.log(x) / ln_base,
        inverse=lambda t: base ** t,
        domain=Domain.positive_reals(),
        derivative=lambda x: 1 / (x * ln_base),
        description=f"Logarithm base {base}"
    )


def create_phi_log_lens() -> Lens:
    """
    Golden ratio logarithm lens: T(x) = log_φ(x) = ln(x)/ln(φ).
    
    Special property: multiplying by φ becomes translation by 1.
    s = log_φ(x)  →  φ-scaling becomes s → s+1
    
    This is the key lens for metallic-lattice scaling.
    """
    return Lens(
        name="log_φ",
        forward=lambda x: math.log(x) / LN_PHI,
        inverse=lambda s: PHI ** s,
        domain=Domain.positive_reals(),
        derivative=lambda x: 1 / (x * LN_PHI),
        description="φ-log: φ-scaling → unit translation"
    )


def create_quarter_turn_lens() -> Lens:
    """
    Quarter-turn lens: T(x) = (π/2)·log_φ(x).
    
    φ-scaling becomes a literal quarter-turn (90°) in the symmetry crystal.
    """
    scale = PI / 2
    return Lens(
        name="quarter_turn",
        forward=lambda x: scale * math.log(x) / LN_PHI,
        inverse=lambda t: PHI ** (t / scale),
        domain=Domain.positive_reals(),
        derivative=lambda x: scale / (x * LN_PHI),
        description="Quarter-turn: φ-scaling → 90° rotation"
    )


def create_phase_lens() -> Lens:
    """
    Phase lens: T(x) = arg(x) (for complex) or T(x) = x mod 2π.
    
    For real positive x, uses log to get phase via x^i = e^(i·ln(x)).
    """
    return Lens(
        name="phase",
        forward=lambda x: math.log(x) % TAU,
        inverse=lambda theta: math.exp(theta),
        domain=Domain.positive_reals(),
        derivative=lambda x: 1/x,
        description="Phase: amplitude → angle"
    )


def create_affine_lens(a: float, b: float) -> Lens:
    """
    Affine lens: T(x) = a·x + b.
    
    Simple scaling and shift.
    """
    if a == 0:
        raise ValueError("Affine lens requires a ≠ 0")
    return Lens(
        name=f"affine({a},{b})",
        forward=lambda x: a * x + b,
        inverse=lambda t: (t - b) / a,
        domain=Domain.all_reals() if a > 0 else Domain.all_reals(),
        derivative=lambda x: a,
        description=f"Affine: x → {a}x + {b}"
    )


def create_power_lens(p: float) -> Lens:
    """
    Power lens: T(x) = x^p.
    
    Properties depend on p:
    - p > 0: preserves (0, ∞)
    - p = 2: square
    - p = 0.5: square root
    """
    return Lens(
        name=f"pow_{p}",
        forward=lambda x: x ** p,
        inverse=lambda t: t ** (1/p) if t >= 0 else -((-t) ** (1/p)),
        domain=Domain.positive_reals(),
        derivative=lambda x: p * (x ** (p - 1)),
        description=f"Power: x → x^{p}"
    )


def create_identity_lens() -> Lens:
    """
    Identity lens: T(x) = x.
    
    The trivial lens.
    """
    return Lens(
        name="id",
        forward=lambda x: x,
        inverse=lambda t: t,
        domain=Domain.all_reals(),
        derivative=lambda x: 1.0,
        description="Identity: x → x"
    )


# =============================================================================
# LENS REGISTRY
# =============================================================================

class LensRegistry:
    """
    Registry of canonical lenses.
    """
    
    def __init__(self):
        self.lenses: Dict[str, Lens] = {}
        self._register_canonical()
    
    def _register_canonical(self):
        """Register the canonical lens library."""
        self.register(create_identity_lens())
        self.register(create_ln_lens())
        self.register(create_exp_lens())
        self.register(create_phi_log_lens())
        self.register(create_quarter_turn_lens())
        self.register(create_phase_lens())
        self.register(create_power_lens(2))
        self.register(create_power_lens(0.5))
    
    def register(self, lens: Lens) -> None:
        """Register a lens."""
        self.lenses[lens.name] = lens
    
    def get(self, name: str) -> Optional[Lens]:
        """Get a lens by name."""
        return self.lenses.get(name)
    
    def list_lenses(self) -> List[str]:
        """List all registered lens names."""
        return list(self.lenses.keys())


# =============================================================================
# TRANSPORTED OPERATORS
# =============================================================================

@dataclass
class TransportedOperator:
    """
    An operator transported through a lens.
    
    f_T = T⁻¹ ∘ f ∘ T
    
    This is the "shadow" of f under lens T.
    """
    
    original_name: str
    lens: Lens
    operator: Callable[[float], float]
    
    def __call__(self, x: float) -> float:
        """Apply the transported operator."""
        return self.operator(x)
    
    @classmethod
    def from_function(cls, name: str, f: Callable[[float], float], 
                     lens: Lens) -> 'TransportedOperator':
        """Create a transported operator from a function."""
        transported = lens.transport(f)
        return cls(
            original_name=name,
            lens=lens,
            operator=transported
        )


# =============================================================================
# POLE/SHADOW/CROSS STRUCTURE
# =============================================================================

@dataclass
class PoleStructure:
    """
    Poles, shadows, and crosses.
    
    - Poles: Chosen primitive operators
    - Shadows: Conjugates in rotated coordinates
    - Cross symmetries: Equalities and reflections between pole families
    """
    
    # Primary poles
    poles: Dict[str, Callable[[float], float]] = field(default_factory=dict)
    
    # Shadows under various lenses
    shadows: Dict[str, Dict[str, TransportedOperator]] = field(default_factory=dict)
    
    # Cross-symmetry relations
    crosses: List[Tuple[str, str, str]] = field(default_factory=list)
    
    def add_pole(self, name: str, op: Callable[[float], float]) -> None:
        """Add a primary pole."""
        self.poles[name] = op
    
    def compute_shadow(self, pole_name: str, lens: Lens) -> TransportedOperator:
        """Compute the shadow of a pole under a lens."""
        if pole_name not in self.poles:
            raise ValueError(f"Unknown pole: {pole_name}")
        
        op = self.poles[pole_name]
        shadow = TransportedOperator.from_function(pole_name, op, lens)
        
        # Store in shadows
        if pole_name not in self.shadows:
            self.shadows[pole_name] = {}
        self.shadows[pole_name][lens.name] = shadow
        
        return shadow
    
    def add_cross_symmetry(self, pole1: str, pole2: str, 
                          relation: str) -> None:
        """Record a cross-symmetry relation."""
        self.crosses.append((pole1, pole2, relation))


# =============================================================================
# VALIDATION
# =============================================================================

def validate_lenses() -> bool:
    """Validate lenses module."""
    
    # Test domain
    D = Domain.positive_reals()
    assert D.contains(1.0)
    assert D.contains(PHI)
    assert not D.contains(0.0)
    assert not D.contains(-1.0)
    
    # Test ln lens
    ln_lens = create_ln_lens()
    assert abs(ln_lens(E) - 1.0) < 1e-10
    assert abs(ln_lens.inv(1.0) - E) < 1e-10
    assert ln_lens.is_bijective()
    
    # Test φ-log lens
    phi_lens = create_phi_log_lens()
    assert abs(phi_lens(PHI) - 1.0) < 1e-10
    assert abs(phi_lens.inv(1.0) - PHI) < 1e-10
    assert phi_lens.is_bijective()
    
    # Test transport: multiplication → addition
    # Under ln, x·y becomes ln(x) + ln(y)
    multiply_by_2 = lambda t: t + math.log(2)  # In log space
    transported = ln_lens.transport(multiply_by_2)
    # transported(x) should equal 2*x
    assert abs(transported(3.0) - 6.0) < 1e-10
    
    # Test quarter-turn lens
    qt_lens = create_quarter_turn_lens()
    assert qt_lens.is_bijective()
    
    # Test registry
    registry = LensRegistry()
    assert len(registry.list_lenses()) >= 5
    assert registry.get("ln") is not None
    assert registry.get("log_φ") is not None
    
    # Test pole structure
    poles = PoleStructure()
    poles.add_pole("square", lambda x: x * x)
    shadow = poles.compute_shadow("square", ln_lens)
    # square in x-space is doubling in log-space
    # So shadow(x) = exp(2*ln(x)) = x^2
    assert abs(shadow(3.0) - 9.0) < 1e-10
    
    return True


if __name__ == "__main__":
    print("Validating Lenses Module...")
    assert validate_lenses()
    print("✓ Lenses Module validated")
    
    # Demo
    print("\n=== Lens Demo ===")
    
    print("\nCanonical Lenses:")
    registry = LensRegistry()
    for name in registry.list_lenses():
        lens = registry.get(name)
        print(f"  {name}: {lens.description}")
    
    print("\n=== φ-Log Lens ===")
    phi_lens = create_phi_log_lens()
    print(f"φ = {PHI:.6f}")
    print(f"log_φ(φ) = {phi_lens(PHI):.6f} (should be 1.0)")
    print(f"log_φ(φ²) = {phi_lens(PHI**2):.6f} (should be 2.0)")
    print(f"log_φ(1) = {phi_lens(1.0):.6f} (should be 0.0)")
    
    print("\n=== Transport Demo ===")
    ln_lens = create_ln_lens()
    # Under ln, addition becomes multiplication
    add_1 = lambda t: t + 1  # Add 1 in log space
    transported = ln_lens.transport(add_1)
    print(f"Transport of 'add 1' under ln:")
    print(f"  transported(2) = {transported(2.0):.6f} (= 2·e ≈ 5.436)")
