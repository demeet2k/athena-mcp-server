"""
ATHENA OS - Mathematical Lens System
====================================
Lens-invariant framework for constructing and transforming mathematical objects.

Core Principle: Validity-by-construction
If T: D → ℝ is a bijection, then transporting algebra through T yields
internally consistent "alien" mathematics on D isomorphic to standard ℝ.

The universal transformation law: f_T = T⁻¹ ∘ f ∘ T (conjugacy)

This module implements:
1. Lens (Coordinate Isomorphisms) - T: D → ℝ with inverses
2. Transported Operators (Shadows) - f_T = T⁻¹ ∘ f ∘ T
3. Transported Arithmetic - ⊕_T, ⊗_T yielding isomorphic fields
4. Special Lenses - ln, exp, log_φ, trig-phase, warped periodic
5. Corridor Discipline - Invertibility bounds, contraction certificates

The four items that reconstruct the entire framework:
1. Lens Conjugacy: f_T = T⁻¹ ∘ f ∘ T
2. Transported Algebra: ⊕_T, ⊗_T 
3. Zero Hierarchy: H=0 → H'=0 → det J=0
4. Lattice Preimage Principle: T⁻¹(L) generates constant families
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from abc import ABC, abstractmethod
import numpy as np
import math


# =============================================================================
# LENS BASE CLASS - COORDINATE ISOMORPHISMS
# =============================================================================

class Lens(ABC):
    """
    A Lens is a bijection T: D → ℝ (or a subset thereof).
    
    The lens serves as a coordinate chart, enabling:
    - Transported operators: f_T = T⁻¹ ∘ f ∘ T
    - Transported arithmetic: x ⊕_T y = T⁻¹(T(x) + T(y))
    - Lattice pullbacks: T⁻¹(L) for lattice L
    
    Subclasses must implement forward (T) and inverse (T⁻¹) maps.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass
    
    @property
    @abstractmethod
    def domain(self) -> Tuple[float, float]:
        """Domain interval (a, b) where T is defined."""
        pass
    
    @property
    @abstractmethod
    def codomain(self) -> Tuple[float, float]:
        """Codomain interval where T maps to."""
        pass
    
    @abstractmethod
    def forward(self, x: float) -> float:
        """Apply T: x ↦ T(x)."""
        pass
    
    @abstractmethod
    def inverse(self, t: float) -> float:
        """Apply T⁻¹: t ↦ T⁻¹(t)."""
        pass
    
    def derivative(self, x: float, h: float = 1e-8) -> float:
        """Numerical derivative T'(x)."""
        return (self.forward(x + h) - self.forward(x - h)) / (2 * h)
    
    def is_monotone(self, samples: int = 100) -> bool:
        """Check if T is monotone on domain (necessary for bijection)."""
        a, b = self.domain
        if not np.isfinite(a):
            a = -1000
        if not np.isfinite(b):
            b = 1000
        
        xs = np.linspace(a + 1e-6, b - 1e-6, samples)
        derivs = [self.derivative(x) for x in xs]
        
        return all(d > 0 for d in derivs) or all(d < 0 for d in derivs)
    
    def in_domain(self, x: float) -> bool:
        """Check if x is in the domain."""
        a, b = self.domain
        return a < x < b
    
    # Conjugacy operations
    def conjugate(self, f: Callable[[float], float]) -> Callable[[float], float]:
        """
        Transport operator f through this lens: f_T = T⁻¹ ∘ f ∘ T
        
        This is the fundamental rotation/transformation law.
        """
        def f_T(x: float) -> float:
            t = self.forward(x)
            ft = f(t)
            return self.inverse(ft)
        return f_T
    
    def transport_add(self, x: float, y: float) -> float:
        """
        Transported addition: x ⊕_T y = T⁻¹(T(x) + T(y))
        
        This makes (D, ⊕_T, ⊗_T) a field isomorphic to (ℝ, +, ×).
        """
        return self.inverse(self.forward(x) + self.forward(y))
    
    def transport_mul(self, x: float, y: float) -> float:
        """
        Transported multiplication: x ⊗_T y = T⁻¹(T(x) · T(y))
        """
        return self.inverse(self.forward(x) * self.forward(y))
    
    def transport_power(self, x: float, p: float) -> float:
        """
        Transported power: Pow_T(x, p) = T⁻¹(p · T(x))
        
        Square/sqrt become exact scaling actions in lens space.
        """
        return self.inverse(p * self.forward(x))
    
    def lattice_preimage(self, lattice_value: float) -> float:
        """
        Pull back a single lattice point: T⁻¹(k)
        """
        return self.inverse(lattice_value)
    
    def lattice_preimage_family(self, base: float, period: float, 
                                 n_terms: int = 10) -> List[float]:
        """
        Pull back a periodic lattice: T⁻¹(base + k·period) for k ∈ ℤ
        """
        results = []
        for k in range(-n_terms, n_terms + 1):
            t = base + k * period
            try:
                x = self.inverse(t)
                if self.in_domain(x):
                    results.append(x)
            except (ValueError, OverflowError):
                pass
        return sorted(results)
    
    def compose(self, other: 'Lens') -> 'ComposedLens':
        """Compose lenses: (T₂ ∘ T₁)(x) = T₂(T₁(x))"""
        return ComposedLens(self, other)
    
    def __repr__(self) -> str:
        return f"Lens[{self.name}]"


class ComposedLens(Lens):
    """Composition of two lenses: T₂ ∘ T₁."""
    
    def __init__(self, inner: Lens, outer: Lens):
        self.inner = inner
        self.outer = outer
    
    @property
    def name(self) -> str:
        return f"({self.outer.name} ∘ {self.inner.name})"
    
    @property
    def domain(self) -> Tuple[float, float]:
        return self.inner.domain
    
    @property
    def codomain(self) -> Tuple[float, float]:
        return self.outer.codomain
    
    def forward(self, x: float) -> float:
        return self.outer.forward(self.inner.forward(x))
    
    def inverse(self, t: float) -> float:
        return self.inner.inverse(self.outer.inverse(t))


# =============================================================================
# STANDARD LENSES - THE CANONICAL COORDINATE SYSTEMS
# =============================================================================

class IdentityLens(Lens):
    """The identity lens T(x) = x."""
    
    @property
    def name(self) -> str:
        return "Id"
    
    @property
    def domain(self) -> Tuple[float, float]:
        return (-np.inf, np.inf)
    
    @property
    def codomain(self) -> Tuple[float, float]:
        return (-np.inf, np.inf)
    
    def forward(self, x: float) -> float:
        return x
    
    def inverse(self, t: float) -> float:
        return t


class LogLens(Lens):
    """
    Natural logarithm lens: T(x) = ln(x)
    
    Domain: (0, ∞), Codomain: ℝ
    
    Key property: multiplication ↔ addition
    ln(xy) = ln(x) + ln(y)
    """
    
    @property
    def name(self) -> str:
        return "ln"
    
    @property
    def domain(self) -> Tuple[float, float]:
        return (0, np.inf)
    
    @property
    def codomain(self) -> Tuple[float, float]:
        return (-np.inf, np.inf)
    
    def forward(self, x: float) -> float:
        if x <= 0:
            raise ValueError("ln requires x > 0")
        return np.log(x)
    
    def inverse(self, t: float) -> float:
        return np.exp(t)
    
    def derivative(self, x: float, h: float = 1e-8) -> float:
        if x <= 0:
            raise ValueError("ln requires x > 0")
        return 1.0 / x


class ExpLens(Lens):
    """
    Exponential lens: T(x) = exp(x)
    
    Domain: ℝ, Codomain: (0, ∞)
    Inverse of LogLens.
    """
    
    @property
    def name(self) -> str:
        return "exp"
    
    @property
    def domain(self) -> Tuple[float, float]:
        return (-np.inf, np.inf)
    
    @property
    def codomain(self) -> Tuple[float, float]:
        return (0, np.inf)
    
    def forward(self, x: float) -> float:
        return np.exp(x)
    
    def inverse(self, t: float) -> float:
        if t <= 0:
            raise ValueError("exp inverse requires t > 0")
        return np.log(t)
    
    def derivative(self, x: float, h: float = 1e-8) -> float:
        return np.exp(x)


class LogBaseLens(Lens):
    """
    Logarithm with arbitrary base: T(x) = log_b(x)
    
    Domain: (0, ∞), Codomain: ℝ
    """
    
    def __init__(self, base: float):
        if base <= 0 or base == 1:
            raise ValueError("Base must be positive and not 1")
        self.base = base
        self._ln_base = np.log(base)
    
    @property
    def name(self) -> str:
        if self.base == np.e:
            return "ln"
        elif self.base == 10:
            return "log₁₀"
        elif self.base == 2:
            return "log₂"
        else:
            return f"log_{self.base:.4f}"
    
    @property
    def domain(self) -> Tuple[float, float]:
        return (0, np.inf)
    
    @property
    def codomain(self) -> Tuple[float, float]:
        return (-np.inf, np.inf)
    
    def forward(self, x: float) -> float:
        if x <= 0:
            raise ValueError("log requires x > 0")
        return np.log(x) / self._ln_base
    
    def inverse(self, t: float) -> float:
        return np.power(self.base, t)


# Golden ratio constant
PHI = (1 + np.sqrt(5)) / 2  # ≈ 1.618033988749895


class PhiLogLens(LogBaseLens):
    """
    Golden ratio logarithm: T(x) = log_φ(x)
    
    Domain: (0, ∞), Codomain: ℝ
    
    Key property: x ↦ φx becomes s ↦ s+1 (discrete translation)
    This makes φ a native "step size" inside the symmetry crystal.
    """
    
    def __init__(self):
        super().__init__(PHI)
    
    @property
    def name(self) -> str:
        return "log_φ"


class TrigPhaseLens(Lens):
    """
    Trigonometric phase lens: T(x) = (π/2) · log_φ(x)
    
    Domain: (0, ∞), Codomain: ℝ
    
    Key property: φ-scaling becomes quarter-turn rotation
    T(φx) = T(x) + π/2
    
    This produces exact φ-indexed lattice families.
    """
    
    def __init__(self):
        self._ln_phi = np.log(PHI)
    
    @property
    def name(self) -> str:
        return "φ-phase"
    
    @property
    def domain(self) -> Tuple[float, float]:
        return (0, np.inf)
    
    @property
    def codomain(self) -> Tuple[float, float]:
        return (-np.inf, np.inf)
    
    def forward(self, x: float) -> float:
        if x <= 0:
            raise ValueError("φ-phase requires x > 0")
        return (np.pi / 2) * np.log(x) / self._ln_phi
    
    def inverse(self, t: float) -> float:
        return np.power(PHI, 2 * t / np.pi)
    
    def derivative(self, x: float, h: float = 1e-8) -> float:
        return (np.pi / 2) / (x * self._ln_phi)


class WarpedPeriodicLens(Lens):
    """
    Warped periodic lens: T(x) = (π/2)s + P(s), where s = log_φ(x)
    
    P(s) is a periodic function with P(s+1) = P(s)
    Corridor bound: |P'|_∞ < π/2 ensures bijection
    
    This lens:
    - Locks φ as lattice step
    - Embeds sin/cos as periodic texture in log-space
    - Supports exact constant generation
    """
    
    def __init__(self, warp_amplitude: float = 0.0, warp_phase: float = 0.0):
        """
        P(s) = warp_amplitude * sin(2π(s + warp_phase))
        
        Must have |warp_amplitude| * 2π < π/2 for bijection.
        """
        if abs(warp_amplitude) * 2 * np.pi >= np.pi / 2:
            raise ValueError("Warp amplitude too large for bijection")
        
        self.warp_amplitude = warp_amplitude
        self.warp_phase = warp_phase
        self._ln_phi = np.log(PHI)
    
    @property
    def name(self) -> str:
        if self.warp_amplitude == 0:
            return "φ-phase"
        return f"φ-warped(a={self.warp_amplitude:.3f})"
    
    @property
    def domain(self) -> Tuple[float, float]:
        return (0, np.inf)
    
    @property
    def codomain(self) -> Tuple[float, float]:
        return (-np.inf, np.inf)
    
    def _s(self, x: float) -> float:
        """s = log_φ(x)"""
        return np.log(x) / self._ln_phi
    
    def _P(self, s: float) -> float:
        """Periodic warp function."""
        return self.warp_amplitude * np.sin(2 * np.pi * (s + self.warp_phase))
    
    def _P_deriv(self, s: float) -> float:
        """Derivative of P."""
        return self.warp_amplitude * 2 * np.pi * np.cos(2 * np.pi * (s + self.warp_phase))
    
    def forward(self, x: float) -> float:
        if x <= 0:
            raise ValueError("Warped lens requires x > 0")
        s = self._s(x)
        return (np.pi / 2) * s + self._P(s)
    
    def inverse(self, t: float) -> float:
        """Newton iteration to invert T."""
        # Initial guess: ignore warp
        s = 2 * t / np.pi
        
        # Newton iteration
        for _ in range(20):
            f = (np.pi / 2) * s + self._P(s) - t
            fp = (np.pi / 2) + self._P_deriv(s)
            if abs(fp) < 1e-15:
                break
            s_new = s - f / fp
            if abs(s_new - s) < 1e-12:
                s = s_new
                break
            s = s_new
        
        return np.power(PHI, s)


# =============================================================================
# PHASE GEOMETRY - SIN/COS AS PERIODIC TEXTURE
# =============================================================================

class PhaseLens(Lens):
    """
    Direct phase angle lens using arctan2-based unwrapping.
    
    Maps positive reals to phase angles via log.
    T(x) = ln(x) (viewing phase as continuous angle)
    """
    
    @property
    def name(self) -> str:
        return "phase"
    
    @property
    def domain(self) -> Tuple[float, float]:
        return (0, np.inf)
    
    @property
    def codomain(self) -> Tuple[float, float]:
        return (-np.inf, np.inf)
    
    def forward(self, x: float) -> float:
        if x <= 0:
            raise ValueError("Phase lens requires x > 0")
        return np.log(x)
    
    def inverse(self, t: float) -> float:
        return np.exp(t)


# =============================================================================
# TRANSPORTED OPERATIONS - ALIEN ARITHMETIC
# =============================================================================

@dataclass
class TransportedField:
    """
    A field (D, ⊕_T, ⊗_T) isomorphic to (ℝ, +, ×) via lens T.
    
    Theorem: If T is a bijection D → ℝ, then (D, ⊕_T, ⊗_T) is a field
    isomorphic to (ℝ, +, ×). Any algebraic identity in ℝ has a
    transported twin in D.
    """
    lens: Lens
    
    @property
    def zero(self) -> float:
        """Additive identity: T⁻¹(0)"""
        return self.lens.inverse(0)
    
    @property
    def one(self) -> float:
        """Multiplicative identity: T⁻¹(1)"""
        return self.lens.inverse(1)
    
    def add(self, x: float, y: float) -> float:
        """x ⊕_T y = T⁻¹(T(x) + T(y))"""
        return self.lens.transport_add(x, y)
    
    def mul(self, x: float, y: float) -> float:
        """x ⊗_T y = T⁻¹(T(x) · T(y))"""
        return self.lens.transport_mul(x, y)
    
    def neg(self, x: float) -> float:
        """Additive inverse: T⁻¹(-T(x))"""
        return self.lens.inverse(-self.lens.forward(x))
    
    def inv(self, x: float) -> float:
        """Multiplicative inverse: T⁻¹(1/T(x))"""
        t = self.lens.forward(x)
        if abs(t) < 1e-15:
            raise ZeroDivisionError("Cannot invert transported zero")
        return self.lens.inverse(1.0 / t)
    
    def sub(self, x: float, y: float) -> float:
        """x ⊖_T y = x ⊕_T (-y)_T"""
        return self.add(x, self.neg(y))
    
    def div(self, x: float, y: float) -> float:
        """x ⊘_T y = x ⊗_T (1/y)_T"""
        return self.mul(x, self.inv(y))
    
    def power(self, x: float, p: float) -> float:
        """Pow_T(x, p) = T⁻¹(p · T(x))"""
        return self.lens.transport_power(x, p)
    
    def sqrt(self, x: float) -> float:
        """Square root = power by 1/2"""
        return self.power(x, 0.5)
    
    def square(self, x: float) -> float:
        """Square = power by 2"""
        return self.power(x, 2.0)


# =============================================================================
# EXTENDED HYBRID OPERATIONS
# =============================================================================

def kappa_sum(t: float, u: float, kappa: float) -> float:
    """
    Associative κ-sum in t-space: t ⊞_κ u = t + u + κtu
    
    This produces new idempotents and fixed lattices.
    """
    return t + u + kappa * t * u


class KappaField:
    """
    Extended hybrid regime with κ-sum.
    
    Operations are defined in t-space and pulled back through lens T.
    """
    
    def __init__(self, lens: Lens, kappa: float):
        self.lens = lens
        self.kappa = kappa
    
    def star_add(self, x: float, y: float) -> float:
        """x ⋆_κ y = T⁻¹(T(x) ⊞_κ T(y))"""
        tx = self.lens.forward(x)
        ty = self.lens.forward(y)
        result = kappa_sum(tx, ty, self.kappa)
        return self.lens.inverse(result)
    
    def idempotent(self) -> Optional[float]:
        """
        Find e such that e ⋆_κ e = e
        
        In t-space: t + t + κt² = t → t + κt² = 0 → t(1 + κt) = 0
        Solutions: t = 0 or t = -1/κ (if κ ≠ 0)
        """
        if abs(self.kappa) < 1e-15:
            return self.lens.inverse(0)
        
        # Non-trivial idempotent
        t_idem = -1.0 / self.kappa
        return self.lens.inverse(t_idem)


# =============================================================================
# LENS REGISTRY
# =============================================================================

class LensRegistry:
    """Registry of standard lenses."""
    
    def __init__(self):
        self.lenses: Dict[str, Lens] = {}
        self._register_standard()
    
    def _register_standard(self) -> None:
        """Register standard lenses."""
        self.register("id", IdentityLens())
        self.register("ln", LogLens())
        self.register("exp", ExpLens())
        self.register("log_phi", PhiLogLens())
        self.register("phi_phase", TrigPhaseLens())
        self.register("log_10", LogBaseLens(10))
        self.register("log_2", LogBaseLens(2))
    
    def register(self, name: str, lens: Lens) -> None:
        """Register a lens."""
        self.lenses[name] = lens
    
    def get(self, name: str) -> Optional[Lens]:
        """Get lens by name."""
        return self.lenses.get(name)
    
    def list_all(self) -> List[str]:
        """List all registered lens names."""
        return list(self.lenses.keys())
    
    def create_warped(self, amplitude: float, phase: float = 0.0) -> WarpedPeriodicLens:
        """Create a warped periodic lens."""
        return WarpedPeriodicLens(amplitude, phase)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_lens_system() -> bool:
    """Validate lens system."""
    # Identity lens
    id_lens = IdentityLens()
    assert abs(id_lens.forward(5.0) - 5.0) < 1e-10
    assert abs(id_lens.inverse(5.0) - 5.0) < 1e-10
    
    # Log lens
    ln_lens = LogLens()
    assert abs(ln_lens.forward(np.e) - 1.0) < 1e-10
    assert abs(ln_lens.inverse(1.0) - np.e) < 1e-10
    
    # Round-trip
    x = 7.5
    assert abs(ln_lens.inverse(ln_lens.forward(x)) - x) < 1e-10
    
    # φ-log lens
    phi_lens = PhiLogLens()
    assert abs(phi_lens.forward(PHI) - 1.0) < 1e-10
    assert abs(phi_lens.forward(PHI * PHI) - 2.0) < 1e-10
    
    # TrigPhase lens: T(φx) = T(x) + π/2
    trig_lens = TrigPhaseLens()
    x = 2.5
    t1 = trig_lens.forward(x)
    t2 = trig_lens.forward(PHI * x)
    assert abs(t2 - t1 - np.pi/2) < 1e-10
    
    # Transported field
    field = TransportedField(ln_lens)
    zero = field.zero  # e^0 = 1
    one = field.one    # e^1 = e
    assert abs(zero - 1.0) < 1e-10
    assert abs(one - np.e) < 1e-10
    
    # Transported multiplication (becomes addition in log-space)
    a, b = 2.0, 3.0
    product = field.mul(a, b)
    # T⁻¹(T(2) · T(3)) = exp(ln(2) · ln(3))
    expected = np.exp(np.log(2) * np.log(3))
    assert abs(product - expected) < 1e-10
    
    # Warped lens round-trip
    warped = WarpedPeriodicLens(0.1, 0.0)
    x = 3.7
    assert abs(warped.inverse(warped.forward(x)) - x) < 1e-8
    
    # Registry
    registry = LensRegistry()
    assert len(registry.list_all()) >= 5
    assert registry.get("ln") is not None
    
    return True


if __name__ == "__main__":
    print("Validating Lens System...")
    assert validate_lens_system()
    print("✓ Lens System validated")
    
    # Demo
    print("\n=== Lens Demo ===")
    ln = LogLens()
    print(f"ln(e) = {ln.forward(np.e):.6f}")
    print(f"ln⁻¹(1) = {ln.inverse(1):.6f}")
    
    print("\n=== Transported Field Demo ===")
    field = TransportedField(ln)
    print(f"Zero (T⁻¹(0)): {field.zero:.6f}")
    print(f"One (T⁻¹(1)): {field.one:.6f}")
    print(f"2 ⊗_ln 3: {field.mul(2, 3):.6f}")
    
    print("\n=== φ-Phase Lens Demo ===")
    phi_lens = TrigPhaseLens()
    print(f"T(1) = {phi_lens.forward(1):.6f}")
    print(f"T(φ) = {phi_lens.forward(PHI):.6f}")
    print(f"T(φ) - T(1) = {phi_lens.forward(PHI) - phi_lens.forward(1):.6f} (should be π/2 ≈ 1.571)")
