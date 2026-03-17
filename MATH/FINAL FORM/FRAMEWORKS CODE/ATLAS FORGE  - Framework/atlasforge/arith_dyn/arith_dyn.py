"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     ARITHMETIC DYNAMICS MODULE                               ║
║                                                                              ║
║  Dynamical Systems on Algebraic Varieties and Number Fields                  ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Study iteration of maps φ: X → X on algebraic varieties:                  ║
║    - Orbit structure O_φ(P) = {P, φ(P), φ²(P), ...}                         ║
║    - Preperiodic points, canonical heights                                   ║
║    - Dynamical degree and entropy                                           ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Ψ-pole ↔ Orbit hierarchy (preperiodic structure)                       ║
║    - C-pole ↔ Continuous dynamics (Julia/Fatou)                             ║
║    - D-pole ↔ Discrete orbits (periodic points)                             ║
║    - Σ-pole ↔ Entropy and chaos                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Set
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMICAL SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RationalMap:
    """
    Rational map φ: ℙⁿ → ℙⁿ.
    
    Given by homogeneous polynomials [F₀ : ... : Fₙ] of same degree d.
    """
    degree: int
    dimension: int  # n for ℙⁿ
    name: str = "φ"
    
    @property
    def algebraic_degree(self) -> int:
        """Degree of the map."""
        return self.degree
    
    def iterate(self, n: int) -> str:
        """φⁿ - n-th iterate."""
        return f"{self.name}^{n}"
    
    def degree_of_iterate(self, n: int) -> int:
        """deg(φⁿ) = d^n for most maps."""
        return self.degree ** n
    
    @classmethod
    def power_map(cls, d: int, n: int = 1) -> 'RationalMap':
        """Power map [x₀ : ... : xₙ] ↦ [x₀^d : ... : xₙ^d]."""
        return cls(d, n, f"[x^{d}]")
    
    @classmethod
    def chebyshev(cls, d: int) -> 'RationalMap':
        """Chebyshev polynomial T_d on ℙ¹."""
        return cls(d, 1, f"T_{d}")


@dataclass
class MorphismEndomorphism:
    """
    Endomorphism φ: X → X of algebraic variety X.
    """
    variety: str
    degree: int
    is_finite: bool = True
    
    def preimage(self, Y: str) -> str:
        """φ⁻¹(Y)."""
        return f"φ⁻¹({Y})"
    
    def pushforward(self) -> str:
        """φ_* on divisors/cycles."""
        return f"φ_*"
    
    def pullback(self) -> str:
        """φ* on divisors/cycles."""
        return "φ*"


# ═══════════════════════════════════════════════════════════════════════════════
# ORBITS AND PERIODIC POINTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Orbit:
    """
    Forward orbit O_φ(P) = {P, φ(P), φ²(P), ...}.
    """
    initial_point: str
    map_name: str = "φ"
    
    def forward_orbit(self) -> str:
        """O⁺_φ(P)."""
        return f"O⁺_{self.map_name}({self.initial_point}) = {{{self.initial_point}, {self.map_name}({self.initial_point}), ...}}"
    
    def backward_orbit(self) -> str:
        """O⁻_φ(P) = ∪ₙ φ⁻ⁿ(P)."""
        return f"O⁻_{self.map_name}({self.initial_point})"
    
    def full_orbit(self) -> str:
        """O_φ(P) = O⁺ ∪ O⁻."""
        return f"O_{self.map_name}({self.initial_point})"


@dataclass
class PeriodicPoint:
    """
    Periodic point: φⁿ(P) = P for some n ≥ 1.
    
    - Exact period = minimal such n
    - Multiplier λ = (φⁿ)'(P)
    """
    point: str
    period: int
    multiplier: Optional[complex] = None
    
    @property
    def is_fixed(self) -> bool:
        """Fixed point has period 1."""
        return self.period == 1
    
    def classify(self) -> str:
        """Classify by multiplier."""
        if self.multiplier is None:
            return "unknown"
        lam = abs(self.multiplier)
        if lam < 1:
            return "attracting"
        elif lam > 1:
            return "repelling"
        elif lam == 1 and self.multiplier != 1:
            return "indifferent"
        else:
            return "superattracting"


@dataclass
class PreperiodicPoint:
    """
    Preperiodic point: φᵐ⁺ⁿ(P) = φᵐ(P) for some m ≥ 0, n ≥ 1.
    
    Strictly preperiodic if m > 0.
    """
    point: str
    preperiod: int  # m
    period: int     # n
    
    @property
    def is_periodic(self) -> bool:
        """Periodic iff preperiod = 0."""
        return self.preperiod == 0
    
    @property
    def is_strictly_preperiodic(self) -> bool:
        """Strictly preperiodic iff preperiod > 0."""
        return self.preperiod > 0
    
    def portrait(self) -> str:
        """(m, n) portrait."""
        return f"({self.preperiod}, {self.period})"


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL HEIGHT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CanonicalHeight:
    """
    Canonical height ĥ_φ for dynamical system.
    
    ĥ_φ(P) = lim_{n→∞} h(φⁿ(P)) / dⁿ
    
    Properties:
    - ĥ_φ(φ(P)) = d · ĥ_φ(P)
    - ĥ_φ(P) ≥ 0, equality iff P preperiodic
    """
    map_degree: int
    base_height: str = "h"
    
    def definition(self) -> str:
        """Definition of canonical height."""
        d = self.map_degree
        return f"ĥ_φ(P) = lim_{{n→∞}} h(φⁿ(P)) / {d}ⁿ"
    
    def transform_property(self) -> str:
        """ĥ_φ(φ(P)) = d · ĥ_φ(P)."""
        return f"ĥ_φ(φ(P)) = {self.map_degree} · ĥ_φ(P)"
    
    def preperiodic_criterion(self) -> str:
        """P preperiodic iff ĥ_φ(P) = 0."""
        return "P preperiodic ⟺ ĥ_φ(P) = 0"


@dataclass 
class GreenFunction:
    """
    Green function G_φ for polynomial/rational map.
    
    G_φ(z) = lim_{n→∞} log|φⁿ(z)| / dⁿ
    """
    map_name: str = "φ"
    
    def definition(self) -> str:
        """Definition of Green function."""
        return f"G_{self.map_name}(z) = lim_{{n→∞}} log|{self.map_name}ⁿ(z)| / dⁿ"
    
    def height_relation(self) -> str:
        """Relation to canonical height."""
        return f"ĥ_φ(P) = Σ_v G_φ,v(P)"


# ═══════════════════════════════════════════════════════════════════════════════
# JULIA AND FATOU SETS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class JuliaSet:
    """
    Julia set J(φ) - chaotic locus.
    
    J(φ) = closure of repelling periodic points
         = ∂{z : φⁿ(z) → ∞}
    """
    map_name: str = "φ"
    
    def definition(self) -> str:
        """Definition of Julia set."""
        return f"J({self.map_name}) = closure of repelling periodic points"
    
    def alternative_definition(self) -> str:
        """Boundary of basin of infinity."""
        return f"J({self.map_name}) = ∂(basin of ∞)"
    
    def properties(self) -> List[str]:
        """Key properties."""
        return [
            "Completely invariant: φ⁻¹(J) = φ(J) = J",
            "Perfect set (no isolated points)",
            "Either connected or Cantor set (for quadratic)",
            "Sensitive dependence on initial conditions"
        ]


@dataclass
class FatouSet:
    """
    Fatou set F(φ) = ℙⁿ ∖ J(φ) - stable locus.
    
    Where iterates form normal family.
    """
    map_name: str = "φ"
    
    def definition(self) -> str:
        """Definition as complement of Julia."""
        return f"F({self.map_name}) = ℙⁿ ∖ J({self.map_name})"
    
    def components(self) -> str:
        """Fatou components."""
        return "Fatou components: attracting basins, Siegel disks, Herman rings, etc."


# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMICAL DEGREE AND ENTROPY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DynamicalDegree:
    """
    Dynamical degree δ(φ) = lim_{n→∞} (deg φⁿ)^{1/n}.
    
    For dominant rational map on projective variety.
    """
    algebraic_degree: int
    
    def definition(self) -> str:
        """Definition of dynamical degree."""
        return "δ(φ) = lim_{n→∞} (deg φⁿ)^{1/n}"
    
    def for_endomorphism(self) -> str:
        """For endomorphism, δ = d."""
        return f"δ(φ) = {self.algebraic_degree} (for endomorphism)"
    
    def entropy_relation(self) -> str:
        """h_{top}(φ) = log δ(φ)."""
        return "h_{top}(φ) = log δ(φ)"


@dataclass
class TopologicalEntropy:
    """
    Topological entropy h_{top}(φ).
    
    Measures complexity/chaos of dynamical system.
    """
    dynamical_degree: float
    
    @property
    def entropy(self) -> float:
        """h_{top} = log δ."""
        return np.log(self.dynamical_degree)
    
    def is_chaotic(self) -> bool:
        """Positive entropy indicates chaos."""
        return self.entropy > 0


# ═══════════════════════════════════════════════════════════════════════════════
# ARITHMETIC DYNAMICS THEOREMS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UniformBoundedness:
    """
    Uniform Boundedness Conjecture (Morton-Silverman).
    
    For φ: ℙⁿ → ℙⁿ of degree d ≥ 2 over number field K:
    |PrePer(φ, K)| ≤ B(n, d, [K:ℚ])
    """
    
    def conjecture(self) -> str:
        return "|PrePer(φ, K)| ≤ B(n, d, [K:ℚ]) (uniform bound)"
    
    def known_cases(self) -> List[str]:
        return [
            "n = 1, d = 2 (quadratic polynomials)",
            "Lattès maps",
            "Power maps"
        ]


@dataclass
class DynamicalMordellLang:
    """
    Dynamical Mordell-Lang Conjecture.
    
    For φ: X → X and subvariety V ⊂ X:
    {n : φⁿ(P) ∈ V} is finite union of arithmetic progressions.
    """
    
    def conjecture(self) -> str:
        return "{n : φⁿ(P) ∈ V(K̄)} = finite ∪ arithmetic progressions"
    
    def special_case(self) -> str:
        """When V is a point."""
        return "If φⁿ(P) = Q infinitely often, then P, Q preperiodic"


# ═══════════════════════════════════════════════════════════════════════════════
# MODULI OF DYNAMICAL SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DynamicalModuliSpace:
    """
    Moduli space M_d of degree d rational maps.
    
    M_d = Rat_d / PGL_2 (quotient by conjugation)
    """
    degree: int
    
    def space(self) -> str:
        """M_d."""
        return f"M_{self.degree} = Rat_{self.degree} / PGL_2"
    
    def dimension(self) -> int:
        """dim M_d = 2d - 2."""
        return 2 * self.degree - 2
    
    def marked_space(self, n: int) -> str:
        """M_d,n with n marked periodic points."""
        return f"M_{{{self.degree},{n}}}"


@dataclass
class PeriodicPointPortrait:
    """
    Portrait of periodic points.
    
    Graph structure of periodic cycles.
    """
    cycles: List[int]  # List of cycle lengths
    
    def total_periodic_points(self) -> int:
        """Total number of periodic points."""
        return sum(self.cycles)
    
    def portrait_polynomial(self) -> str:
        """Generating function."""
        return f"Σ |Per_n(φ)| t^n"


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ArithDynPoleBridge:
    """
    Bridge between arithmetic dynamics and pole structure.
    """
    
    @staticmethod
    def psi_pole_as_orbit() -> str:
        """
        Ψ-pole corresponds to orbit hierarchy.
        Preperiodic structure.
        """
        return "Ψ ↔ Orbit: Hierarchical preperiodic structure"
    
    @staticmethod
    def c_pole_as_continuous() -> str:
        """
        C-pole corresponds to continuous dynamics.
        Julia/Fatou sets, complex dynamics.
        """
        return "C ↔ Continuous: Julia set J(φ), Fatou set F(φ)"
    
    @staticmethod
    def d_pole_as_periodic() -> str:
        """
        D-pole corresponds to discrete orbits.
        Periodic points, exact periods.
        """
        return "D ↔ Periodic: Per_n(φ), discrete cycles"
    
    @staticmethod
    def sigma_pole_as_entropy() -> str:
        """
        Σ-pole corresponds to entropy.
        Chaos, ergodic behavior.
        """
        return "Σ ↔ Entropy: h_{top}(φ) = log δ(φ)"
    
    @staticmethod
    def gateway_as_height() -> str:
        """
        Gateway corresponds to canonical height.
        Bridge between dynamics and arithmetic.
        """
        return "Gateway ↔ Height: ĥ_φ bridges dynamics ↔ arithmetic"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def rational_map(degree: int, dim: int = 1) -> RationalMap:
    """Create rational map."""
    return RationalMap(degree, dim)


def periodic_point(point: str, period: int, 
                   multiplier: complex = None) -> PeriodicPoint:
    """Create periodic point."""
    return PeriodicPoint(point, period, multiplier)


def preperiodic_point(point: str, preperiod: int, period: int) -> PreperiodicPoint:
    """Create preperiodic point."""
    return PreperiodicPoint(point, preperiod, period)


def canonical_height(degree: int) -> CanonicalHeight:
    """Create canonical height."""
    return CanonicalHeight(degree)


def julia_set(phi: str = "φ") -> JuliaSet:
    """Create Julia set."""
    return JuliaSet(phi)


def dynamical_entropy(degree: float) -> TopologicalEntropy:
    """Create topological entropy."""
    return TopologicalEntropy(degree)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Maps
    'RationalMap',
    'MorphismEndomorphism',
    
    # Orbits
    'Orbit',
    'PeriodicPoint',
    'PreperiodicPoint',
    
    # Heights
    'CanonicalHeight',
    'GreenFunction',
    
    # Julia/Fatou
    'JuliaSet',
    'FatouSet',
    
    # Degree and Entropy
    'DynamicalDegree',
    'TopologicalEntropy',
    
    # Theorems
    'UniformBoundedness',
    'DynamicalMordellLang',
    
    # Moduli
    'DynamicalModuliSpace',
    'PeriodicPointPortrait',
    
    # Bridge
    'ArithDynPoleBridge',
    
    # Functions
    'rational_map',
    'periodic_point',
    'preperiodic_point',
    'canonical_height',
    'julia_set',
    'dynamical_entropy',
]
